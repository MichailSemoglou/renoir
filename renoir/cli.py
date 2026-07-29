"""
Command-line interface for renoir.

Exposes artist analysis, palette extraction, color naming, and GenAI
prompt generation as shell-friendly subcommands. Uses ``click`` as an
optional dependency; install with ``pip install renoir-wikiart[cli]``.

JSON output goes to *stdout*; progress and diagnostics go to *stderr*.
"""

from __future__ import annotations

import json
import logging
import sys
from typing import Optional

logger = logging.getLogger(__name__)

# ---------------------------------------------------------------------------
# Click availability check
# ---------------------------------------------------------------------------

_CLICK_AVAILABLE = False
try:
    import click

    _CLICK_AVAILABLE = True
except ImportError:
    click = None  # type: ignore[assignment]


def _check_click() -> None:
    if not _CLICK_AVAILABLE:
        sys.exit(
            "The renoir CLI requires the 'click' package.\n"
            "Install with: pip install renoir-wikiart[cli]"
        )


def _load_image(path: str):
    """Load an image from *path* as a PIL Image."""
    from PIL import Image

    try:
        return Image.open(path).convert("RGB")
    except FileNotFoundError:
        raise click.ClickException(f"File not found: {path}")
    except OSError as exc:
        raise click.ClickException(f"Cannot open image '{path}': {exc}")


# ---------------------------------------------------------------------------
# Top-level group
# ---------------------------------------------------------------------------

if _CLICK_AVAILABLE:

    @click.group()
    def cli() -> None:
        """renoir — WikiArt color analysis from the command line."""
        pass

    # -----------------------------------------------------------------------
    # artist
    # -----------------------------------------------------------------------

    @cli.command()
    @click.argument("artist_id")
    @click.option(
        "--limit",
        default=20,
        type=int,
        help="Maximum works to return.",
    )
    @click.option(
        "--json",
        "as_json",
        is_flag=True,
        help="Emit JSON to stdout.",
    )
    def artist(artist_id: str, limit: int, as_json: bool) -> None:
        """Show metadata and color signature for ARTIST_ID.

        ARTIST_ID is the WikiArt slug, e.g. ``claude-monet``.
        """
        from renoir import ArtistAnalyzer

        analyzer = ArtistAnalyzer()
        works = analyzer.extract_artist_works(artist_id, limit=limit)
        genres = analyzer.analyze_genres(works)
        styles = analyzer.analyze_styles(works)

        result: dict = {
            "artist": artist_id,
            "total_works": len(works),
            "genres": [{"name": g, "count": c} for g, c in genres],
            "styles": [{"name": s, "count": c} for s, c in styles],
        }

        if as_json:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(f"Artist: {artist_id}")
            click.echo(f"Total works extracted: {len(works)}")
            click.echo("\nGenres:")
            for genre, count in genres:
                click.echo(f"  {genre}: {count}")
            click.echo("\nStyles:")
            for style, count in styles:
                click.echo(f"  {style}: {count}")

    # -----------------------------------------------------------------------
    # extract
    # -----------------------------------------------------------------------

    @cli.command()
    @click.argument("image", type=click.Path(exists=True, dir_okay=False))
    @click.option(
        "--n-colors",
        default=5,
        type=int,
        help="Number of dominant colors.",
    )
    @click.option(
        "--format",
        "output_format",
        default="json",
        type=click.Choice(["json", "css"]),
        help="Output format.",
    )
    @click.option(
        "--output",
        "-o",
        default=None,
        type=click.Path(dir_okay=False, writable=True, resolve_path=True),
        help="Write to file.",
    )
    @click.option(
        "--method",
        default="kmeans",
        type=click.Choice(["kmeans", "frequency", "dsp"]),
        help="Extraction method (dsp = distinctness-first with WCAG AA guarantee).",
    )
    def extract(
        image: str,
        n_colors: int,
        output_format: str,
        output: Optional[str],
        method: str,
    ) -> None:
        """Extract the dominant color palette from IMAGE."""
        from renoir.color import ColorExtractor

        pil_image = _load_image(image)
        extractor = ColorExtractor()
        colors = extractor.extract_dominant_colors(
            pil_image,
            n_colors=n_colors,
            method=method,
        )
        colors = [(int(c[0]), int(c[1]), int(c[2])) for c in colors]

        if output_format == "json":
            if output:
                extractor.export_palette_json(colors, output)
                click.echo(f"Palette written to {output}", err=True)
            else:
                payload = {
                    "n_colors": n_colors,
                    "colors": [
                        {"rgb": list(c), "hex": extractor.rgb_to_hex(c)} for c in colors
                    ],
                }
                click.echo(json.dumps(payload, indent=2))
        elif output_format == "css":
            prefix = "palette"
            if output:
                extractor.export_palette_css(colors, output, prefix=prefix)
                click.echo(f"CSS written to {output}", err=True)
            else:
                hex_colors = [extractor.rgb_to_hex(c) for c in colors]
                lines = [
                    f"  --{prefix}-{i + 1}: {h};" for i, h in enumerate(hex_colors)
                ]
                click.echo(":root {")
                click.echo("\n".join(lines))
                click.echo("}")

    # -----------------------------------------------------------------------
    # name
    # -----------------------------------------------------------------------

    @cli.command()
    @click.argument("color")
    @click.option(
        "--vocabulary",
        default="artist",
        type=click.Choice(["artist", "resene", "werner", "xkcd"]),
        help="Color-naming vocabulary.",
    )
    @click.option(
        "--metadata",
        is_flag=True,
        help="Include CI name and distance.",
    )
    def name(color: str, vocabulary: str, metadata: bool) -> None:
        """Name a COLOR using perceptually accurate matching.

        COLOR can be a hex string (``#FF5733``) or comma-separated RGB
        (``255,87,51``).
        """
        from renoir.color import ColorNamer

        if color.startswith("#"):
            rgb_value: "str | tuple[int, int, int]" = color
        else:
            parts = color.split(",")
            if len(parts) != 3:
                raise click.ClickException(
                    "COLOR must be a hex string (#FF5733) or "
                    "comma-separated RGB (255,87,51)."
                )
            rgb_value = (int(parts[0].strip()), int(parts[1].strip()), int(parts[2].strip()))

        namer = ColorNamer(vocabulary=vocabulary)
        result = namer.name(rgb_value, return_metadata=metadata)

        if metadata:
            click.echo(json.dumps(result, indent=2))
        else:
            click.echo(result)

    # -----------------------------------------------------------------------
    # prompt
    # -----------------------------------------------------------------------

    @cli.command()
    @click.argument("image", type=click.Path(exists=True, dir_okay=False))
    @click.option(
        "--style",
        default=None,
        type=str,
        help="Art style, e.g. 'impressionist'.",
    )
    @click.option(
        "--medium",
        default=None,
        type=str,
        help="Medium, e.g. 'oil', 'watercolor'.",
    )
    @click.option(
        "--mood",
        default=None,
        type=str,
        help="Mood descriptor.",
    )
    @click.option(
        "--target-model",
        default="midjourney",
        type=click.Choice(["dalle", "midjourney", "stable_diffusion"]),
        help="Target generative model.",
    )
    @click.option(
        "--n-colors",
        default=5,
        type=int,
        help="Number of colors to extract.",
    )
    @click.option(
        "--method",
        default="kmeans",
        type=click.Choice(["kmeans", "frequency", "dsp"]),
        help="Extraction method (dsp = distinctness-first with WCAG AA guarantee).",
    )
    def prompt(
        image: str,
        style: Optional[str],
        medium: Optional[str],
        mood: Optional[str],
        target_model: str,
        n_colors: int,
        method: str,
    ) -> None:
        """Generate a GenAI prompt from the color palette of IMAGE."""
        from renoir.color import ColorExtractor, PromptGenerator

        pil_image = _load_image(image)
        extractor = ColorExtractor()
        colors = extractor.extract_dominant_colors(
            pil_image,
            n_colors=n_colors,
            method=method,
        )
        colors = [(int(c[0]), int(c[1]), int(c[2])) for c in colors]

        generator = PromptGenerator(vocabulary="artist")
        result = generator.generate(
            colors,
            style=style,
            medium=medium,
            mood=mood,
            target_model=target_model,
        )
        click.echo(result)

else:

    def cli() -> None:  # type: ignore[misc]
        _check_click()
