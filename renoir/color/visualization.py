"""
Visualization functions for color analysis.

This module provides tools for creating educational visualizations
of color data, palettes, and distributions.
"""

import logging
import os

import numpy as np
from typing import Any, Dict, List, Optional, Tuple, cast

try:
    import matplotlib.pyplot as plt
    import matplotlib.patches as patches
    from matplotlib.figure import Figure

    from ._plot_style import (
        ACCENT,
        BLACK,
        add_heading,
        add_panel,
        create_figure,
        grid_point,
        style_axis,
    )

    _MPL_AVAILABLE = True
except ImportError:
    plt = None  # type: ignore[assignment, misc]
    patches = None  # type: ignore[assignment, misc]
    Figure = None  # type: ignore[assignment, misc]
    _MPL_AVAILABLE = False

logger = logging.getLogger(__name__)

try:
    import seaborn as sns

    SEABORN_AVAILABLE = True
except ImportError:
    sns = None  # type: ignore[assignment, misc]
    SEABORN_AVAILABLE = False

_FIGURE_TITLE_COLOR = "#1A1A1A"
_SPINE_COLOR = "#CCCCCC"
_CELL_SPINE_COLOR = "#E0E0E0"
_CI_NAME_COLOR = "#555555"
_YEAR_LABEL_COLOR = "#888888"
_BAR_BACKGROUND_COLOR = "#E0E0E0"
_BRIGHTNESS_TEXT_THRESHOLD = 140
_MIN_SEGMENT_WIDTH_FOR_LABEL = 0.10
_CROSS_VOCAB_VOCABULARIES = ["artist", "resene", "natural", "xkcd"]
_CROSS_VOCAB_DEFAULT_LABELS = {
    "artist": "Artist pigments",
    "resene": "Resene",
    "natural": "Werner's Nomenclature",
    "xkcd": "xkcd",
}


class ColorVisualizer:
    """
    Create visualizations for color analysis and education.

    This class provides methods for visualizing color palettes,
    distributions, and relationships. Designed for teaching color
    theory and computational analysis to art and design students.
    """

    def __init__(self, namer=None, analyzer=None):
        """Initialize the ColorVisualizer.

        Args:
            namer: Optional pre-configured ``ColorNamer`` instance.
                When ``None``, one is created lazily on first use.
            analyzer: Optional pre-configured ``ColorAnalyzer`` instance.
                When ``None``, one is created lazily on first use.
        """
        if SEABORN_AVAILABLE:
            sns.set_style("whitegrid")
        self._namer = namer
        self._analyzer = analyzer

    def _get_namer(self):
        if self._namer is None:
            from .namer import ColorNamer

            self._namer = ColorNamer()
        return self._namer

    def _get_analyzer(self):
        if self._analyzer is None:
            from .analysis import ColorAnalyzer

            self._analyzer = ColorAnalyzer()
        return self._analyzer

    @staticmethod
    def _draw_palette_strip(
        ax,
        colors: List[Tuple[int, int, int]],
        title: Optional[str] = None,
    ) -> None:
        for i, color in enumerate(colors):
            normalized = tuple(c / 255 for c in color)
            rect = patches.Rectangle(
                (i, 0), 1, 1, facecolor=normalized, edgecolor="white", linewidth=1
            )
            ax.add_patch(rect)
        ax.set_xlim(0, len(colors))
        ax.set_ylim(0, 1)
        ax.set_aspect("equal")
        ax.axis("off")
        if title:
            ax.set_title(title, fontsize=12, fontweight="bold")

    @staticmethod
    def _finalize_figure(
        fig,
        save_path: Optional[str],
        show: bool,
        label: str = "Figure",
    ):
        if save_path:
            from ..color.extraction import _validate_export_filename

            _validate_export_filename(os.path.basename(save_path))
            fig.savefig(save_path, dpi=150, facecolor="white")
            logger.info("%s saved to: %s", label, save_path)
        if show:
            plt.show()
        return fig

    def plot_palette(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Palette",
        figsize: Tuple[int, int] = (12, 2),
        save_path: Optional[str] = None,
        show_hex: bool = True,
        show_names: bool = False,
        vocabulary: str = "artist",
        show: bool = True,
    ) -> Figure:
        """
        Visualize a color palette as horizontal color swatches.

        Educational method for displaying extracted colors clearly.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size (width, height)
            save_path: Optional path to save the figure
            show_hex: Whether to show hex codes below colors
            show_names: Whether to show evocative color names (default: False)
            vocabulary: Color naming vocabulary to use when show_names=True
                       Options: 'artist', 'resene', 'natural', 'xkcd'
            show: If True, display the figure with plt.show()

        Example:
            >>> from renoir.color import ColorExtractor, ColorVisualizer
            >>> extractor = ColorExtractor()
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 87, 51), (100, 200, 150), (50, 100, 200)]
            >>> visualizer.plot_palette(colors, title="My Palette")
            >>> # With color names
            >>> visualizer.plot_palette(colors, show_names=True, vocabulary="artist")
        """
        n_colors = len(colors)

        # Adjust figure height if showing names
        if show_names:
            figsize = (figsize[0], figsize[1] + 1)

        fig = create_figure(title, figsize=figsize)
        ax = add_panel(fig, 0, 1.25, 12, 6.75)

        # Load color names if requested
        color_names = None
        if show_names:
            try:
                from .namer import ColorNamer

                namer = ColorNamer(vocabulary=vocabulary)
                color_names = cast(List[str], namer.name_palette(colors))
            except ImportError:
                logger.warning("ColorNamer not available. Showing hex codes only.")
                color_names = None

        self._draw_palette_strip(ax, colors)

        # Add text overlays
        for i, color in enumerate(colors):
            brightness = self._calculate_brightness(color)
            text_color = "white" if brightness < 128 else "black"

            if show_hex and not show_names:
                hex_code = "#{:02x}{:02x}{:02x}".format(*color)
                ax.text(
                    i + 0.5,
                    0.5,
                    hex_code,
                    ha="center",
                    va="center",
                    fontsize=10,
                    fontweight="bold",
                    color=text_color,
                )

            if show_names and color_names:
                name = color_names[i]
                if len(name) > 15:
                    words = name.split()
                    mid = len(words) // 2
                    name = "\n".join([" ".join(words[:mid]), " ".join(words[mid:])])

                ax.text(
                    i + 0.5,
                    0.5,
                    name,
                    ha="center",
                    va="center",
                    fontsize=9,
                    fontweight="bold",
                    color=text_color,
                )

        return self._finalize_figure(fig, save_path, show, "Palette")

    def plot_named_palette(
        self,
        colors: List[Tuple[int, int, int]],
        vocabulary: str = "artist",
        title: Optional[str] = None,
        figsize: Tuple[int, int] = (12, 4),
        save_path: Optional[str] = None,
        show_metadata: bool = False,
        show: bool = True,
    ) -> Optional[Figure]:
        """
        Visualize a color palette with evocative color names.

        Creates a rich visualization showing color swatches with their
        evocative names and optional metadata like Color Index names.

        Args:
            colors: List of RGB tuples
            vocabulary: Color naming vocabulary ('artist', 'resene', 'natural', 'xkcd')
            title: Plot title (auto-generated if None)
            figsize: Figure size (width, height)
            save_path: Optional path to save the figure
            show_metadata: Whether to show additional metadata like CI names
            show: If True, display the figure with plt.show()

        Example:
            >>> from renoir.color import ColorExtractor, ColorVisualizer
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 87, 51), (100, 200, 150), (50, 100, 200)]
            >>> visualizer.plot_named_palette(colors, vocabulary="artist")
        """
        try:
            from .namer import ColorNamer
        except ImportError:
            logger.error("ColorNamer not available")
            return None

        namer = ColorNamer(vocabulary=vocabulary)
        named_colors = cast(
            List[Dict[str, Any]], namer.name_palette(colors, return_metadata=True)
        )

        n_colors = len(colors)

        # Auto-generate title if not provided
        if title is None:
            title = f"Color Palette ({vocabulary.title()} Names)"

        # Adjust figure height for metadata
        if show_metadata:
            figsize = (figsize[0], figsize[1] + 0.5)  # type: ignore[assignment]

        fig = create_figure(title, figsize=figsize)
        ax = add_panel(fig, 0, 1.25, 12, 6.75)

        self._draw_palette_strip(ax, colors)

        # Add text overlays
        for i, (color, metadata) in enumerate(zip(colors, named_colors)):
            brightness = self._calculate_brightness(color)
            text_color = "white" if brightness < 128 else "black"

            name = metadata["name"]
            if len(name) > 15:
                words = name.split()
                if len(words) > 1:
                    mid = len(words) // 2
                    name = "\n".join([" ".join(words[:mid]), " ".join(words[mid:])])

            y_pos = 0.6 if show_metadata else 0.5
            ax.text(
                i + 0.5,
                y_pos,
                name,
                ha="center",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=text_color,
            )

            if show_metadata:
                meta_lines = []
                if metadata.get("ci_name"):
                    meta_lines.append(f"CI: {metadata['ci_name']}")
                if metadata.get("family"):
                    meta_lines.append(metadata["family"])

                if meta_lines:
                    meta_text = "\n".join(meta_lines)
                    ax.text(
                        i + 0.5,
                        0.3,
                        meta_text,
                        ha="center",
                        va="center",
                        fontsize=8,
                        color=text_color,
                    )

        return self._finalize_figure(fig, save_path, show, "Named palette")

    def plot_color_wheel(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Wheel Distribution",
        figsize: Tuple[int, int] = (8, 8),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot colors on a color wheel to show hue distribution.

        Educational visualization showing where colors fall on the spectrum.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()

        Example:
            >>> visualizer = ColorVisualizer()
            >>> colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
            >>> fig = visualizer.plot_color_wheel(colors)
        """
        analyzer = self._get_analyzer()

        fig = create_figure(title, figsize=figsize)
        ax = add_panel(fig, 0, 1.25, 12, 6.75, projection="polar")

        # Convert colors to HSV and extract hues
        hsv_values = [analyzer.rgb_to_hsv(color) for color in colors]

        for color, hsv in zip(colors, hsv_values):
            hue_rad = np.radians(hsv[0])  # Convert hue to radians
            saturation = hsv[1] / 100  # Normalize saturation

            # Plot point
            normalized_color = tuple(c / 255 for c in color)
            ax.plot(
                hue_rad,
                saturation,
                "o",
                color=normalized_color,
                markersize=15,
                markeredgecolor="black",
                markeredgewidth=2,
            )

        ax.set_ylim(0, 1)
        ax.set_theta_zero_location("N")  # type: ignore[attr-defined]
        ax.set_theta_direction(-1)  # type: ignore[attr-defined]
        ax.set_ylabel("Saturation", fontsize=9, color=BLACK)

        # Add color wheel background
        theta = np.linspace(0, 2 * np.pi, 360)
        for t in theta:
            hue_deg = np.degrees(t) % 360
            rgb = analyzer.hsv_to_rgb((hue_deg, 100, 100))
            normalized = tuple(c / 255 for c in rgb)
            ax.plot([t, t], [0, 1], color=normalized, linewidth=2, alpha=0.3)

        return self._finalize_figure(fig, save_path, show, "Color wheel")

    def plot_rgb_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "RGB Distribution",
        figsize: Tuple[int, int] = (12, 4),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot RGB channel distributions as histograms.

        Educational visualization for understanding color composition.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
        """
        rgb_array = np.array(colors)

        fig = create_figure(title, figsize=figsize)
        channel_names = ["Red", "Green", "Blue"]
        channel_colors = [ACCENT, "#333333", "#777777"]
        axes = [
            add_panel(fig, index * 4.25, 1.25, 3.5, 6.75, f"{name} Channel")
            for index, name in enumerate(channel_names)
        ]

        for i, (ax, name, color) in enumerate(zip(axes, channel_names, channel_colors)):
            ax.hist(rgb_array[:, i], bins=20, color=color, alpha=0.8, edgecolor="black")
            ax.set_xlim(0, 255)
            style_axis(ax, "Value (0-255)", "Frequency")

        return self._finalize_figure(fig, save_path, show, "RGB distribution")

    def plot_hsv_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "HSV Distribution",
        figsize: Tuple[int, int] = (14, 4),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot HSV (Hue, Saturation, Value) distributions.

        Educational visualization for understanding color in HSV space.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
        """
        analyzer = self._get_analyzer()
        hsv_values = [analyzer.rgb_to_hsv(color) for color in colors]
        hsv_array = np.array(hsv_values)

        fig = create_figure(title, figsize=figsize)
        axes = [
            add_panel(fig, index * 4.25, 1.25, 3.5, 6.75, panel_title)
            for index, panel_title in enumerate(
                [
                    "Hue Distribution",
                    "Saturation Distribution",
                    "Value/Brightness Distribution",
                ]
            )
        ]
        channel_colors = [ACCENT, "#333333", "#777777"]

        axes[0].hist(
            hsv_array[:, 0],
            bins=24,
            color=channel_colors[0],
            alpha=0.8,
            edgecolor="black",
        )
        axes[0].set_xlim(0, 360)
        style_axis(axes[0], "Hue (degrees)", "Frequency")

        axes[1].hist(
            hsv_array[:, 1],
            bins=20,
            color=channel_colors[1],
            alpha=0.8,
            edgecolor="black",
        )
        axes[1].set_xlim(0, 100)
        style_axis(axes[1], "Saturation (%)", "Frequency")

        axes[2].hist(
            hsv_array[:, 2],
            bins=20,
            color=channel_colors[2],
            alpha=0.8,
            edgecolor="black",
        )
        axes[2].set_xlim(0, 100)
        style_axis(axes[2], "Value (%)", "Frequency")

        return self._finalize_figure(fig, save_path, show, "HSV distribution")

    def plot_3d_rgb_space(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "RGB Color Space (3D)",
        figsize: Tuple[int, int] = (10, 8),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Plot colors in 3D RGB space.

        Advanced educational visualization showing spatial relationships.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
        """
        fig = create_figure(title, figsize=figsize)
        ax = add_panel(fig, 0, 1.25, 12, 6.75, projection="3d")

        rgb_array = np.array(colors)

        # Normalize colors for display
        normalized_colors = rgb_array / 255

        # Plot points
        ax.scatter(
            rgb_array[:, 0],
            rgb_array[:, 1],
            rgb_array[:, 2],
            c=normalized_colors,
            s=200,  # type: ignore[misc]
            alpha=0.8,
            edgecolors="black",
            linewidths=2,
        )

        ax.set_xlabel("Red", fontsize=9, color=BLACK)
        ax.set_ylabel("Green", fontsize=9, color=BLACK)
        ax.set_zlabel("Blue", fontsize=9, color=BLACK)  # type: ignore[attr-defined]

        # Set limits
        ax.set_xlim(0, 255)
        ax.set_ylim(0, 255)
        ax.set_zlim(0, 255)  # type: ignore[attr-defined]

        return self._finalize_figure(fig, save_path, show, "3D RGB space")

    def compare_palettes(
        self,
        palette1: List[Tuple[int, int, int]],
        palette2: List[Tuple[int, int, int]],
        labels: Tuple[str, str] = ("Palette 1", "Palette 2"),
        figsize: Tuple[int, int] = (12, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Compare two color palettes side by side.

        Educational visualization for comparing artistic color choices.

        Args:
            palette1: First list of RGB tuples
            palette2: Second list of RGB tuples
            labels: Tuple of labels for the two palettes
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
        """
        fig = create_figure("Palette comparison", figsize=figsize)
        ax1 = add_panel(fig, 0, 1.25, 12, 2.75, labels[0])
        ax2 = add_panel(fig, 0, 4.75, 12, 2.75, labels[1])

        self._draw_palette_strip(ax1, palette1)
        self._draw_palette_strip(ax2, palette2)

        return self._finalize_figure(fig, save_path, show, "Palette comparison")

    def plot_temperature_distribution(
        self,
        colors: List[Tuple[int, int, int]],
        title: str = "Color Temperature Distribution",
        figsize: Tuple[int, int] = (10, 6),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize warm vs. cool color distribution.

        Educational visualization for color temperature analysis.

        Args:
            colors: List of RGB tuples
            title: Plot title
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
        """
        analyzer = self._get_analyzer()
        temp_dist = analyzer.analyze_color_temperature_distribution(colors)

        # Create bar chart
        fig = create_figure(title, figsize=figsize)
        ax = add_panel(fig, 0, 1.25, 12, 6.75)

        categories = ["Warm", "Cool", "Neutral"]
        counts = [
            temp_dist["warm_count"],
            temp_dist["cool_count"],
            temp_dist["neutral_count"],
        ]
        bar_colors = [ACCENT, "#333333", "#999999"]

        bars = ax.bar(
            categories,
            counts,
            color=bar_colors,
            alpha=0.85,
            edgecolor="black",
            linewidth=0.7,
        )

        # Add percentages on bars
        for bar, count in zip(bars, counts):
            percentage = (count / sum(counts)) * 100
            ax.text(
                bar.get_x() + bar.get_width() / 2,
                bar.get_height() + 0.5,
                f"{percentage:.1f}%",
                ha="center",
                va="bottom",
                fontsize=10,
                color=BLACK,
            )

        style_axis(ax, ylabel="Number of Colors", grid="y")

        return self._finalize_figure(fig, save_path, show, "Temperature distribution")

    def create_artist_color_report(
        self,
        colors: List[Tuple[int, int, int]],
        artist_name: str,
        figsize: Tuple[int, int] = (16, 12),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Create a comprehensive color analysis report for an artist.

        Combines multiple visualizations into a single figure.
        Educational method for comprehensive color analysis.

        Args:
            colors: List of RGB tuples from the artist's works
            artist_name: Name of the artist
            figsize: Figure size
            save_path: Optional path to save the figure
            show: If True, display the figure with plt.show()
        """
        analyzer = self._get_analyzer()

        fig = create_figure(f"Color Analysis: {artist_name}", figsize=figsize)

        # 1. Palette (top, spanning all columns)
        ax_palette = add_panel(fig, 0, 1.25, 12, 2.0, "Dominant Color Palette")
        self._draw_palette_strip(ax_palette, colors[:10])

        # 2. RGB distributions
        rgb_array = np.array(colors)
        channel_names = ["Red", "Green", "Blue"]
        channel_colors = [ACCENT, "#333333", "#777777"]

        for i, (name, color) in enumerate(zip(channel_names, channel_colors)):
            ax = add_panel(fig, i * 4.25, 3.75, 3.5, 1.5, name)
            ax.hist(rgb_array[:, i], bins=15, color=color, alpha=0.8, edgecolor="black")
            ax.set_xlim(0, 255)
            style_axis(ax, ylabel="Frequency")

        # 3. HSV analysis
        hsv_values = [analyzer.rgb_to_hsv(color) for color in colors]
        hsv_array = np.array(hsv_values)

        # Hue circular plot
        ax_hue = add_panel(fig, 0, 6.0, 3.5, 1.7, "Hue", projection="polar")
        theta = np.radians(hsv_array[:, 0])
        ax_hue.hist(theta, bins=24, color=ACCENT, alpha=0.8)

        # Saturation
        ax_sat = add_panel(fig, 4.25, 6.0, 3.5, 1.7, "Saturation")
        ax_sat.hist(
            hsv_array[:, 1], bins=15, color="#333333", alpha=0.8, edgecolor="black"
        )
        ax_sat.set_xlim(0, 100)
        style_axis(ax_sat, "Saturation (%)", "Frequency")

        # Value
        ax_val = add_panel(fig, 8.5, 6.0, 3.5, 1.7, "Brightness")
        ax_val.hist(
            hsv_array[:, 2], bins=15, color="#777777", alpha=0.8, edgecolor="black"
        )
        ax_val.set_xlim(0, 100)
        style_axis(ax_val, "Value (%)", "Frequency")

        return self._finalize_figure(fig, save_path, show, "Color report")

    # ------------------------------------------------------------------
    # Paper-figure methods (added v3.4.0)
    # ------------------------------------------------------------------

    def _calculate_brightness(self, rgb: Tuple[int, int, int]) -> float:
        """Return perceptual brightness (ITU-R BT.601 luma) for an RGB triplet."""
        return 0.299 * rgb[0] + 0.587 * rgb[1] + 0.114 * rgb[2]

    def plot_historical_pigment_probability(
        self,
        color: Tuple[int, int, int],
        year: int,
        results: Optional[List[Dict]] = None,
        top_k: int = 5,
        figsize: Tuple[float, float] = (10.0, 4.5),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize Historical Pigment Probability (HPP) output for one color.

        Shows the input color alongside the ranked candidate pigments returned
        by :meth:`~renoir.color.namer.ColorNamer.historical_pigment_probability`,
        with swatch, Color Index name, year of introduction, probability bar,
        and availability flag for each candidate.

        Args:
            color: Input RGB color tuple, e.g. ``(28, 62, 145)``.
            year: Historical year against which availability is assessed.
            results: Pre-computed HPP output (list of dicts).  If ``None`` the
                method calls :class:`~renoir.color.namer.ColorNamer` internally.
            top_k: Number of candidate pigments to display (default 5).
            figsize: Figure dimensions ``(width, height)`` in inches.
            save_path: File path for saving (PNG at 300 dpi or PDF).
            show: If True, display the figure with plt.show().
        """
        if results is None:
            namer = self._get_namer()
            results = namer.historical_pigment_probability(color, year, top_k=top_k)

        k = len(results)
        r, g, b = color
        hex_str = f"#{r:02X}{g:02X}{b:02X}"
        brightness = self._calculate_brightness(color)
        input_fg = "white" if brightness < _BRIGHTNESS_TEXT_THRESHOLD else "#111111"

        fig = create_figure("Historical Pigment Probability", figsize=figsize)

        # ── Input panel ──────────────────────────────────────────────────
        ax_in = add_panel(fig, 0, 1.25, 2, 6.75)
        ax_in.set_xlim(0, 1)
        ax_in.set_ylim(0, 1)
        ax_in.set_xticks([])
        ax_in.set_yticks([])
        for sp in ax_in.spines.values():
            sp.set_edgecolor(_SPINE_COLOR)
            sp.set_linewidth(0.8)
        ax_in.set_facecolor(f"#{r:02X}{g:02X}{b:02X}")
        ax_in.text(
            0.5,
            0.60,
            hex_str,
            transform=ax_in.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            fontweight="bold",
            color=input_fg,
        )
        ax_in.text(
            0.5,
            0.40,
            str(year),
            transform=ax_in.transAxes,
            ha="center",
            va="center",
            fontsize=9,
            color=input_fg,
            alpha=0.85,
        )
        ax_in.text(
            0.5,
            0.20,
            "Input color",
            transform=ax_in.transAxes,
            ha="center",
            va="center",
            fontsize=8,
            color=input_fg,
            alpha=0.75,
        )

        # ── Candidate panels ─────────────────────────────────────────────
        max_prob = max(c["probability"] for c in results) if results else 1.0
        candidate_width = 10 / k if k else 10

        for idx, cand in enumerate(results):
            ax = add_panel(fig, 2 + idx * candidate_width, 1.25, candidate_width, 6.75)
            self._draw_candidate_panel(ax, cand, max_prob)

        return self._finalize_figure(fig, save_path, show, "HPP figure")

    def _draw_candidate_panel(self, ax, cand: Dict, max_prob: float) -> None:
        """Draw a single candidate pigment panel for HPP visualization."""
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(_CELL_SPINE_COLOR)
            sp.set_linewidth(0.7)
        ax.set_facecolor("white")

        cr, cg, cb = cand["rgb"]
        cand_hex = f"#{cr:02X}{cg:02X}{cb:02X}"
        cand_bright = self._calculate_brightness(cand["rgb"])
        cand_fg = "white" if cand_bright < _BRIGHTNESS_TEXT_THRESHOLD else "#111111"
        available = cand.get("available", True)
        yr_intro = cand.get("year_introduced")

        ax.add_patch(
            patches.Rectangle(
                (0, 0.50),
                1,
                0.50,
                facecolor=cand_hex,
                linewidth=0,
            )
        )

        ax.text(
            0.5,
            0.66,
            cand["name"],
            ha="center",
            va="center",
            fontsize=7.0,
            fontweight="bold",
            color=cand_fg,
            multialignment="center",
        )

        ci = cand.get("ci_name") or ""
        ax.text(
            0.5, 0.44, ci, ha="center", va="top", fontsize=6.5, color=_CI_NAME_COLOR
        )

        if yr_intro is not None:
            yr_label = "antiquity" if yr_intro <= 0 else f"est. {yr_intro}"
        else:
            yr_label = "date unknown"
        ax.text(
            0.5,
            0.34,
            yr_label,
            ha="center",
            va="top",
            fontsize=6.0,
            color=_YEAR_LABEL_COLOR,
        )

        bar_y, bar_h = 0.17, 0.07
        ax.add_patch(
            patches.Rectangle(
                (0.05, bar_y),
                0.90,
                bar_h,
                facecolor=_BAR_BACKGROUND_COLOR,
                linewidth=0,
            )
        )
        fill_w = 0.90 * (cand["probability"] / max_prob)
        bar_col = ACCENT if available else "#AAAAAA"
        ax.add_patch(
            patches.Rectangle(
                (0.05, bar_y),
                fill_w,
                bar_h,
                facecolor=bar_col,
                linewidth=0,
            )
        )

        ax.text(
            0.5,
            bar_y - 0.03,
            f"p = {cand['probability']:.3f}",
            ha="center",
            va="top",
            fontsize=6.0,
            color=_CI_NAME_COLOR,
        )

        badge_col = ACCENT if available else BLACK
        badge_txt = "Available" if available else "Not yet available"
        ax.text(
            0.5,
            0.04,
            badge_txt,
            ha="center",
            va="bottom",
            fontsize=6.0,
            fontweight="bold",
            color=badge_col,
        )

    def plot_pemd_comparison(
        self,
        pairs: List[Tuple[List, List]],
        labels: Optional[List[Tuple[str, str]]] = None,
        pemd_values: Optional[List[float]] = None,
        figsize: Tuple[float, float] = (9.0, 4.0),
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize Palette Earth Mover's Distance (PEMD) for one or more palette pairs.

        Each pair is shown as two proportional color strips with the PEMD value
        annotated between them.  Accepts pre-computed PEMD values or computes
        them internally.

        Args:
            pairs: List of ``(palette1, palette2)`` tuples.  Each palette is a
                list of ``((R, G, B), proportion)`` tuples.
            labels: List of ``(label1, label2)`` strings for each pair.
            pemd_values: Pre-computed PEMD floats, one per pair.  If ``None``
                values are computed internally (requires scipy).
            figsize: Figure dimensions ``(width, height)`` in inches.
            save_path: File path for saving (PNG at 300 dpi or PDF).
            show: If True, display the figure with plt.show().
        """
        n_pairs = len(pairs)
        if n_pairs == 0:
            raise ValueError("pairs must contain at least one palette pair")
        analyzer = self._get_analyzer()
        if labels is None:
            labels = [
                (f"Palette A ({i + 1})", f"Palette B ({i + 1})") for i in range(n_pairs)
            ]

        # Validate and compute missing PEMD values
        if pemd_values is not None and len(pemd_values) != n_pairs:
            raise ValueError(
                f"pemd_values has {len(pemd_values)} entries but pairs has {n_pairs}."
            )
        computed: List[Optional[float]] = (
            list(pemd_values) if pemd_values is not None else [None] * n_pairs
        )
        for i, (p1, p2) in enumerate(pairs):
            if computed[i] is None:
                computed[i] = analyzer.palette_earth_movers_distance(p1, p2)

        fig = create_figure("Palette Earth Mover's Distance (PEMD)", figsize=figsize)
        pair_height = 6.75 / n_pairs
        heading_offset = min(0.3, pair_height * 0.1)
        height_allowance = min(0.75, pair_height * 0.4)
        strip_height = pair_height / 2 - height_allowance

        def _draw_strip(ax: "plt.Axes", palette: List, label: str) -> None:
            ax.set_xlim(0, 1)
            ax.set_ylim(0, 1)
            ax.set_xticks([])
            ax.set_yticks([])
            for sp in ax.spines.values():
                sp.set_edgecolor(_SPINE_COLOR)
                sp.set_linewidth(0.6)
            ax.set_facecolor("white")
            total_w = sum(prop for _, prop in palette) or 1.0
            x = 0.0
            for rgb, prop in palette:
                seg_w = prop / total_w
                rr, gg, bb = rgb
                bright = self._calculate_brightness(rgb)
                seg_fg = "white" if bright < _BRIGHTNESS_TEXT_THRESHOLD else "#111111"
                ax.add_patch(
                    patches.Rectangle(
                        (x, 0),
                        seg_w,
                        1,
                        facecolor=f"#{rr:02X}{gg:02X}{bb:02X}",
                        linewidth=0,
                    )
                )
                if seg_w > _MIN_SEGMENT_WIDTH_FOR_LABEL:
                    ax.text(
                        x + seg_w / 2,
                        0.5,
                        f"#{rr:02X}{gg:02X}{bb:02X}",
                        ha="center",
                        va="center",
                        fontsize=8,
                        color=seg_fg,
                    )
                x += seg_w

        for pair_idx, (p1, p2) in enumerate(pairs):
            lbl1, lbl2 = labels[pair_idx]
            pemd_val = computed[pair_idx]
            row = 1.25 + pair_idx * pair_height
            ax1 = add_panel(
                fig, 0, row, 10, strip_height, lbl1, heading_offset=heading_offset
            )
            ax2 = add_panel(
                fig,
                0,
                row + pair_height / 2,
                10,
                strip_height,
                lbl2,
                heading_offset=heading_offset,
            )
            _draw_strip(ax1, p1, lbl1)
            _draw_strip(ax2, p2, lbl2)

            x, y = grid_point(10.5, row + pair_height / 2)
            fig.text(
                x,
                y,
                f"PEMD\n{pemd_val:.2f}",
                ha="left",
                va="center",
                fontsize=9,
                fontweight="bold",
                color=BLACK,
            )

        return self._finalize_figure(fig, save_path, show, "PEMD figure")

    def plot_cross_vocabulary_naming(
        self,
        colors: List[Tuple[int, int, int]],
        vocabulary_labels: Optional[Dict[str, str]] = None,
        figsize: Optional[Tuple[float, float]] = None,
        save_path: Optional[str] = None,
        show: bool = True,
    ) -> Figure:
        """
        Visualize how a palette is named across all four color vocabularies.

        Creates a grid with vocabularies in rows and colors in columns.
        Each cell shows the matched color swatch and the name from that
        vocabulary (CIEDE2000 nearest-neighbor match).

        Args:
            colors: List of RGB tuples to name.
            vocabulary_labels: Optional mapping of vocabulary key to display
                label.  Defaults to standard vocabulary names.
            figsize: Figure dimensions ``(width, height)`` in inches.
                Auto-sized when ``None``.
            save_path: File path for saving (PNG at 300 dpi or PDF).
            show: If True, display the figure with plt.show().
        """
        if not colors:
            raise ValueError("colors must contain at least one RGB color")

        from .namer import ColorNamer

        _VOCABS = _CROSS_VOCAB_VOCABULARIES
        _labels = dict(_CROSS_VOCAB_DEFAULT_LABELS)
        if vocabulary_labels:
            _labels.update(vocabulary_labels)
        vocabulary_labels = _labels

        # Gather names + matched RGB for each vocabulary
        vocab_data: Dict[str, List[Dict]] = {}
        for v in _VOCABS:
            namer = ColorNamer(vocabulary=v)
            vocab_data[v] = cast(
                List[Dict[str, Any]], namer.name_palette(colors, return_metadata=True)
            )

        n_colors = len(colors)
        n_vocabs = len(_VOCABS)

        if figsize is None:
            figsize = (9.5, max(3.0, 0.85 * n_vocabs + 1.0))

        fig = create_figure("Cross-vocabulary color naming", figsize=figsize)
        label_width = 2.25
        column_width = (12 - label_width) / n_colors
        row_height = 6.75 / n_vocabs
        axes = {
            (row_idx, col_idx): add_panel(
                fig,
                label_width + col_idx * column_width,
                1.25 + row_idx * row_height,
                column_width,
                row_height - 0.3,
            )
            for row_idx in range(n_vocabs)
            for col_idx in range(n_colors)
        }

        # Column headers: input color hex
        for col_idx, rgb in enumerate(colors):
            rr, gg, bb = rgb
            add_heading(
                fig,
                label_width + col_idx * column_width,
                1.0,
                f"#{rr:02X}{gg:02X}{bb:02X}",
                size=8,
            )

        # Row labels: vocabulary names
        for row_idx, v in enumerate(_VOCABS):
            label_row = 1.25 + (row_idx + 0.5) * row_height + 0.15
            x, y = grid_point(0, label_row)
            fig.text(
                x,
                y,
                vocabulary_labels[v],
                fontsize=8,
                fontweight="bold",
                color=BLACK,
                ha="left",
                va="center",
            )

        # Cells
        for row_idx, v in enumerate(_VOCABS):
            for col_idx, rgb in enumerate(colors):
                self._draw_cross_vocab_cell(
                    axes[row_idx, col_idx], rgb, vocab_data[v][col_idx]
                )

        return self._finalize_figure(fig, save_path, show, "Cross-vocabulary figure")

    def _draw_cross_vocab_cell(
        self,
        ax,
        rgb: Tuple[int, int, int],
        meta,
    ) -> None:
        """Draw a single cell in the cross-vocabulary naming grid."""
        ax.set_xlim(0, 1)
        ax.set_ylim(0, 1)
        ax.set_xticks([])
        ax.set_yticks([])
        for sp in ax.spines.values():
            sp.set_edgecolor(_CELL_SPINE_COLOR)
            sp.set_linewidth(0.6)

        if isinstance(meta, dict):
            name_str = meta.get("name", "—")
            mr, mg, mb = meta.get("rgb", rgb)
        else:
            name_str = str(meta)
            mr, mg, mb = rgb

        if len(name_str) > 12:
            words = name_str.split()
            midpoint = len(words) // 2
            name_str = "\n".join(
                [" ".join(words[:midpoint]), " ".join(words[midpoint:])]
            )

        ax.add_patch(
            patches.Rectangle(
                (0, 0),
                0.5,
                1,
                facecolor=f"#{rgb[0]:02X}{rgb[1]:02X}{rgb[2]:02X}",
                linewidth=0,
            )
        )
        ax.add_patch(
            patches.Rectangle(
                (0.5, 0),
                0.5,
                1,
                facecolor=f"#{mr:02X}{mg:02X}{mb:02X}",
                linewidth=0,
            )
        )
        ax.axvline(0.5, color="white", linewidth=0.8)

        bright_match = self._calculate_brightness((mr, mg, mb))
        txt_col = (
            "white"
            if bright_match < _BRIGHTNESS_TEXT_THRESHOLD
            else _FIGURE_TITLE_COLOR
        )
        ax.text(
            0.75,
            0.5,
            name_str,
            ha="center",
            va="center",
            fontsize=5.5,
            color=txt_col,
            multialignment="center",
        )


def check_visualization_support() -> bool:
    """
    Check if visualization dependencies are available.

    Returns:
        True if matplotlib is available, False otherwise
    """
    if _MPL_AVAILABLE:
        logger.info("Color visualization fully supported (matplotlib available)")
        if SEABORN_AVAILABLE:
            logger.info("Enhanced styling available (seaborn available)")
        else:
            logger.info("Basic styling (seaborn not installed, but not required)")
        return True
    logger.warning("Visualization not available. Install with: pip install matplotlib")
    return False
