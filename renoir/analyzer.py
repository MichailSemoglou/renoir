"""
Artist analysis module for renoir.

This module provides functions for extracting and analyzing artist-specific works
from the WikiArt dataset, designed for educational use in computational design
and digital humanities courses.
"""

from typing import List, Dict, Optional, Any, Tuple, TYPE_CHECKING
from collections import Counter, defaultdict
from datasets import load_dataset

import numpy as np

if TYPE_CHECKING:
    from renoir.color import ColorAnalyzer, ColorNamer


class ArtistAnalyzer:
    """
    Analyze artist-specific works from the WikiArt dataset.

    This class provides methods to extract works by specific artists and analyze
    their metadata (genres, styles, periods). Designed for teaching data analysis
    to art and design students.

    Examples:
        >>> analyzer = ArtistAnalyzer()
        >>> works = analyzer.extract_artist_works('claude-monet')
        >>> print(f"Found {len(works)} works by Monet")
        >>> genres = analyzer.analyze_genres(works)
        >>> print(f"Main genre: {genres[0]}")
    """

    def __init__(self, cache_dir: Optional[str] = None):
        """
        Initialize the ArtistAnalyzer.

        Args:
            cache_dir: Optional directory to cache the WikiArt dataset
        """
        self.cache_dir = cache_dir
        self._dataset = None

    def _load_dataset(self):
        """
        Lazy load the WikiArt dataset.

        Raises:
            RuntimeError: If dataset loading fails
        """
        if self._dataset is None:
            try:
                print("Loading WikiArt dataset...")
                self._dataset = load_dataset(
                    "huggan/wikiart", split="train", cache_dir=self.cache_dir
                )
                print(f"✓ Loaded {len(self._dataset)} artworks")
            except Exception as e:
                raise RuntimeError(
                    f"Failed to load WikiArt dataset. "
                    f"Please check your internet connection and try again. "
                    f"Error: {str(e)}"
                )
        return self._dataset

    def load_dataset(self):
        """
        Load and return the WikiArt dataset.

        This is a public alias for :meth:`_load_dataset`.

        Returns:
            The loaded WikiArt dataset.

        Raises:
            RuntimeError: If dataset loading fails
        """
        return self._load_dataset()

    def list_artists(self, limit: Optional[int] = None) -> List[str]:
        """
        List artist names available in the WikiArt dataset.

        Args:
            limit: Optional maximum number of artist names to return

        Returns:
            List of artist names as they appear in the dataset
        """
        dataset = self._load_dataset()

        if not hasattr(dataset, "features"):
            return []

        artist_feature = dataset.features.get("artist")
        if artist_feature is None or not hasattr(artist_feature, "names"):
            return []

        names = list(artist_feature.names)
        if limit is not None:
            names = names[:limit]
        return names

    def extract_artist_works(
        self, artist_name: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract all works by a specific artist from WikiArt.

        Args:
            artist_name: Artist name as it appears in WikiArt (e.g., 'claude-monet')
            limit: Optional maximum number of works to return

        Returns:
            List of dictionaries containing artwork data. The current live
            `huggan/wikiart` dataset provides keys ``image``, ``artist``,
            ``genre`` and ``style``. Additional keys such as ``title`` or
            ``date`` may be present in augmented or user-provided datasets.

        Raises:
            ValueError: If artist_name is empty or invalid
            ValueError: If limit is negative

        Examples:
            >>> analyzer = ArtistAnalyzer()
            >>> monet_works = analyzer.extract_artist_works('claude-monet', limit=10)
            >>> print(sorted(monet_works[0].keys()))
            ['artist', 'genre', 'image', 'style']
        """
        # Input validation
        if not artist_name or not isinstance(artist_name, str):
            raise ValueError("artist_name must be a non-empty string")

        if artist_name.strip() == "":
            raise ValueError("artist_name cannot be empty or whitespace")

        if limit is not None:
            if not isinstance(limit, int):
                raise ValueError("limit must be an integer or None")
            if limit < 0:
                raise ValueError("limit must be non-negative")
            if limit == 0:
                return []

        try:
            dataset = self._load_dataset()
        except Exception as e:
            # Re-raise with more context
            raise RuntimeError(f"Failed to load dataset: {str(e)}")

        # Check if dataset has features (HuggingFace dataset) or is a simple list (tests)
        has_features = hasattr(dataset, "features")

        if has_features:
            # HuggingFace dataset with ClassLabel encoding
            artist_names = (
                dataset.features["artist"].names
                if hasattr(dataset.features["artist"], "names")
                else []
            )

            # Find the target artist's index
            target_artist_idx = None
            for idx, name in enumerate(artist_names):
                if name.lower() == artist_name.lower():
                    target_artist_idx = idx
                    break

            if target_artist_idx is None:
                print(f"⚠ Artist '{artist_name}' not found in dataset")
                print(
                    f"  Tip: Check spelling and use lowercase with hyphens (e.g., 'claude-monet')"
                )
                return []

            # Filter for specific artist by integer index
            artist_works = []
            try:
                for item in dataset:
                    artist_field = item.get("artist")
                    if artist_field == target_artist_idx:
                        artist_works.append(item)
                        if limit and len(artist_works) >= limit:
                            break
            except Exception as e:
                raise RuntimeError(f"Error while filtering artworks: {str(e)}")
        else:
            # Simple list (tests) - artist field is a string
            artist_works = []
            try:
                for item in dataset:
                    artist_field = item.get("artist", "")
                    if (
                        isinstance(artist_field, str)
                        and artist_field.lower() == artist_name.lower()
                    ):
                        artist_works.append(item)
                        if limit and len(artist_works) >= limit:
                            break
            except Exception as e:
                raise RuntimeError(f"Error while filtering artworks: {str(e)}")

        print(f"✓ Found {len(artist_works)} works by {artist_name}")

        return artist_works

    def analyze_genres(self, works: List[Dict[str, Any]]) -> List[tuple]:
        """
        Analyze genre distribution in a collection of works.

        Args:
            works: List of artwork dictionaries

        Returns:
            List of (genre, count) tuples, sorted by frequency

        Raises:
            ValueError: If works is not a list
            TypeError: If works contains non-dict elements

        Examples:
            >>> works = analyzer.extract_artist_works('claude-monet')
            >>> genres = analyzer.analyze_genres(works)
            >>> print(f"Most common genre: {genres[0][0]} ({genres[0][1]} works)")
        """
        if not isinstance(works, list):
            raise ValueError("works must be a list")

        if not works:
            return []

        # Validate that all items are dictionaries
        for i, work in enumerate(works):
            if not isinstance(work, dict):
                raise TypeError(f"Item at index {i} is not a dictionary")

        genres = [work.get("genre", "Unknown") for work in works]
        genre_counts = Counter(genres).most_common()
        return genre_counts

    def analyze_styles(self, works: List[Dict[str, Any]]) -> List[tuple]:
        """
        Analyze style distribution in a collection of works.

        Args:
            works: List of artwork dictionaries

        Returns:
            List of (style, count) tuples, sorted by frequency

        Raises:
            ValueError: If works is not a list
            TypeError: If works contains non-dict elements

        Examples:
            >>> works = analyzer.extract_artist_works('pablo-picasso')
            >>> styles = analyzer.analyze_styles(works)
            >>> for style, count in styles[:3]:
            ...     print(f"{style}: {count} works")
        """
        if not isinstance(works, list):
            raise ValueError("works must be a list")

        if not works:
            return []

        # Validate that all items are dictionaries
        for i, work in enumerate(works):
            if not isinstance(work, dict):
                raise TypeError(f"Item at index {i} is not a dictionary")

        styles = [work.get("style", "Unknown") for work in works]
        style_counts = Counter(styles).most_common()
        return style_counts

    def analyze_temporal_distribution(
        self, works: List[Dict[str, Any]]
    ) -> Dict[str, int]:
        """
        Analyze the temporal distribution of works by decade.

        Args:
            works: List of artwork dictionaries

        Returns:
            Dictionary mapping decades to work counts

        Examples:
            >>> works = analyzer.extract_artist_works('vincent-van-gogh')
            >>> decades = analyzer.analyze_temporal_distribution(works)
            >>> for decade, count in sorted(decades.items()):
            ...     print(f"{decade}s: {count} works")
        """
        decades = {}
        for work in works:
            date = work.get("date")
            if date and isinstance(date, (int, str)):
                try:
                    year = int(str(date)[:4]) if isinstance(date, str) else date
                    decade = (year // 10) * 10
                    decades[decade] = decades.get(decade, 0) + 1
                except (ValueError, IndexError):
                    pass
        return decades

    def get_work_summary(self, works: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate a comprehensive summary of a collection of works.

        Args:
            works: List of artwork dictionaries

        Returns:
            Dictionary with summary statistics

        Examples:
            >>> works = analyzer.extract_artist_works('edvard-munch')
            >>> summary = analyzer.get_work_summary(works)
            >>> print(f"Total works: {summary['total_works']}")
            >>> print(f"Main style: {summary['primary_style']}")
        """
        if not works:
            return {
                "total_works": 0,
                "artist": None,
                "primary_style": None,
                "primary_genre": None,
                "date_range": None,
            }

        genres = self.analyze_genres(works)
        styles = self.analyze_styles(works)

        # Extract date range
        dates = []
        for work in works:
            date = work.get("date")
            if date:
                try:
                    year = int(str(date)[:4]) if isinstance(date, str) else date
                    dates.append(year)
                except (ValueError, IndexError):
                    pass

        date_range = None
        if dates:
            date_range = (min(dates), max(dates))

        return {
            "total_works": len(works),
            "artist": works[0].get("artist", "Unknown"),
            "primary_style": styles[0][0] if styles else None,
            "primary_genre": genres[0][0] if genres else None,
            "date_range": date_range,
            "all_genres": genres,
            "all_styles": styles,
        }

    def _check_visualization_available(self) -> bool:
        """
        Check if visualization libraries are available.

        Returns:
            bool: True if matplotlib and seaborn are installed
        """
        try:
            import matplotlib.pyplot as plt
            import seaborn as sns

            return True
        except ImportError:
            return False

    def plot_genre_distribution(
        self,
        artist_name: str,
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (10, 6),
        show: bool = True,
    ) -> Any:
        """
        Plot genre distribution for a specific artist as a bar chart.

        Args:
            artist_name: Artist name as it appears in WikiArt
            limit: Optional limit on number of works to analyze
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)
            show: If True, display the figure with plt.show()

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> fig = analyzer.plot_genre_distribution('pierre-auguste-renoir')
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return None

        import matplotlib.pyplot as plt
        import seaborn as sns

        # Extract and analyze works
        works = self.extract_artist_works(artist_name, limit=limit)
        genres = self.analyze_genres(works)

        if not genres:
            print(f"No genre data available for {artist_name}")
            return

        # Prepare data for plotting
        genre_names = [g[0] for g in genres]
        genre_counts = [g[1] for g in genres]

        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(x=genre_counts, y=genre_names, ax=ax, palette="viridis")

        ax.set_xlabel("Number of Works", fontsize=12)
        ax.set_ylabel("Genre", fontsize=12)
        ax.set_title(
            f"Genre Distribution: {artist_name}", fontsize=14, fontweight="bold"
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {save_path}")
        if show:
            plt.show()
        return fig

    def plot_style_distribution(
        self,
        artist_name: str,
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (10, 6),
        show: bool = True,
    ) -> Any:
        """
        Plot style distribution for a specific artist as a bar chart.

        Args:
            artist_name: Artist name as it appears in WikiArt
            limit: Optional limit on number of works to analyze
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)
            show: If True, display the figure with plt.show()

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> fig = analyzer.plot_style_distribution('pablo-picasso')
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return None

        import matplotlib.pyplot as plt
        import seaborn as sns

        # Extract and analyze works
        works = self.extract_artist_works(artist_name, limit=limit)
        styles = self.analyze_styles(works)

        if not styles:
            print(f"No style data available for {artist_name}")
            return

        # Prepare data for plotting
        style_names = [s[0] for s in styles]
        style_counts = [s[1] for s in styles]

        # Create plot
        fig, ax = plt.subplots(figsize=figsize)
        sns.barplot(x=style_counts, y=style_names, ax=ax, palette="mako")

        ax.set_xlabel("Number of Works", fontsize=12)
        ax.set_ylabel("Style", fontsize=12)
        ax.set_title(
            f"Style Distribution: {artist_name}", fontsize=14, fontweight="bold"
        )

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {save_path}")
        if show:
            plt.show()
        return fig

    def compare_artists_genres(
        self,
        artist_names: List[str],
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (12, 8),
        show: bool = True,
    ) -> Any:
        """
        Compare genre distributions across multiple artists.

        Args:
            artist_names: List of artist names to compare
            limit: Optional limit on number of works per artist
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)
            show: If True, display the figure with plt.show()

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> fig = analyzer.compare_artists_genres(['claude-monet', 'pierre-auguste-renoir', 'edgar-degas'])
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return None

        import matplotlib.pyplot as plt
        import seaborn as sns
        import pandas as pd

        # Collect data for all artists
        all_data = []
        for artist_name in artist_names:
            works = self.extract_artist_works(artist_name, limit=limit)
            genres = self.analyze_genres(works)

            for genre, count in genres:
                all_data.append({"Artist": artist_name, "Genre": genre, "Count": count})

        if not all_data:
            print("No data available for comparison")
            return

        # Create DataFrame for easier plotting
        df = pd.DataFrame(all_data)

        # Create grouped bar chart
        fig, ax = plt.subplots(figsize=figsize)

        # Pivot data for grouped bars
        pivot_df = df.pivot(index="Genre", columns="Artist", values="Count").fillna(0)
        pivot_df.plot(kind="bar", ax=ax, width=0.8)

        ax.set_xlabel("Genre", fontsize=12)
        ax.set_ylabel("Number of Works", fontsize=12)
        ax.set_title("Genre Distribution Comparison", fontsize=14, fontweight="bold")
        ax.legend(title="Artist", bbox_to_anchor=(1.05, 1), loc="upper left")
        plt.xticks(rotation=45, ha="right")

        plt.tight_layout()

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {save_path}")
        elif show:
            plt.show()
        return fig

    def create_artist_overview(
        self,
        artist_name: str,
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (14, 10),
        show: bool = True,
    ) -> Any:
        """
        Create a comprehensive overview visualization for an artist.

        Includes genre distribution, style distribution, and temporal analysis
        in a multi-panel figure.

        Args:
            artist_name: Artist name as it appears in WikiArt
            limit: Optional limit on number of works to analyze
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)
            show: If True, display the figure with plt.show()

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> fig = analyzer.create_artist_overview('vincent-van-gogh')
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return None

        import matplotlib.pyplot as plt
        import seaborn as sns

        # Extract and analyze works
        works = self.extract_artist_works(artist_name, limit=limit)
        genres = self.analyze_genres(works)
        styles = self.analyze_styles(works)
        temporal = self.analyze_temporal_distribution(works)
        summary = self.get_work_summary(works)

        # Create figure with subplots
        fig = plt.figure(figsize=figsize)
        gs = fig.add_gridspec(3, 2, hspace=0.3, wspace=0.3)

        # Title
        fig.suptitle(
            f"Artist Overview: {artist_name}", fontsize=16, fontweight="bold", y=0.98
        )

        # Summary text
        ax_summary = fig.add_subplot(gs[0, :])
        ax_summary.axis("off")
        summary_text = f"""
        Total Works: {summary['total_works']}
        Primary Style: {summary['primary_style']}
        Primary Genre: {summary['primary_genre']}
        Date Range: {summary['date_range'][0]}-{summary['date_range'][1] if summary['date_range'] else 'N/A'}
        """
        ax_summary.text(
            0.5,
            0.5,
            summary_text,
            ha="center",
            va="center",
            fontsize=12,
            bbox=dict(boxstyle="round", facecolor="wheat", alpha=0.3),
        )

        # Genre distribution
        if genres:
            ax_genre = fig.add_subplot(gs[1, 0])
            genre_names = [g[0] for g in genres[:10]]  # Top 10
            genre_counts = [g[1] for g in genres[:10]]
            sns.barplot(x=genre_counts, y=genre_names, ax=ax_genre, palette="viridis")
            ax_genre.set_xlabel("Count")
            ax_genre.set_ylabel("Genre")
            ax_genre.set_title("Genre Distribution", fontweight="bold")

        # Style distribution
        if styles:
            ax_style = fig.add_subplot(gs[1, 1])
            style_names = [s[0] for s in styles[:10]]  # Top 10
            style_counts = [s[1] for s in styles[:10]]
            sns.barplot(x=style_counts, y=style_names, ax=ax_style, palette="mako")
            ax_style.set_xlabel("Count")
            ax_style.set_ylabel("Style")
            ax_style.set_title("Style Distribution", fontweight="bold")

        # Temporal distribution
        if temporal:
            ax_temporal = fig.add_subplot(gs[2, :])
            decades = sorted(temporal.keys())
            counts = [temporal[d] for d in decades]
            ax_temporal.plot(decades, counts, marker="o", linewidth=2, markersize=8)
            ax_temporal.fill_between(decades, counts, alpha=0.3)
            ax_temporal.set_xlabel("Decade")
            ax_temporal.set_ylabel("Number of Works")
            ax_temporal.set_title("Temporal Distribution", fontweight="bold")
            ax_temporal.grid(True, alpha=0.3)

        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches="tight")
            print(f"Figure saved to {save_path}")
        if show:
            plt.show()
        return fig

    # ------------------------------------------------------------------
    # Portfolio Color Signature API (Phase 5)
    # ------------------------------------------------------------------

    def _parse_year(self, work: Dict[str, Any]) -> Optional[int]:
        """
        Extract a four-digit year from an artwork dict.

        Mirrors the parsing logic in :meth:`analyze_temporal_distribution`
        so that synthetic and augmented datasets with date fields work
        consistently with the rest of the package.
        """
        date = work.get("date")
        if date and isinstance(date, (int, str)):
            try:
                return int(str(date)[:4]) if isinstance(date, str) else date
            except (ValueError, IndexError):
                pass
        return None

    def _sample_works(
        self,
        works: List[Dict[str, Any]],
        limit: int,
        strategy: str,
        random_state: int,
    ) -> Tuple[List[Dict[str, Any]], str]:
        """
        Select up to ``limit`` works using the requested strategy.

        Temporal sampling bins works by decade and distributes selections
        evenly across bins. If no parseable dates are found, it falls back
        to random sampling and reports the effective strategy.
        """
        if strategy not in {"temporal", "random", "first"}:
            raise ValueError("strategy must be 'temporal', 'random', or 'first'")

        if strategy == "first":
            return works[:limit], "first"

        if strategy == "random":
            rng = np.random.RandomState(random_state)
            n = min(limit, len(works))
            indices = rng.choice(len(works), n, replace=False)
            return [works[i] for i in sorted(indices)], "random"

        # strategy == "temporal"
        dated = []
        for work in works:
            year = self._parse_year(work)
            if year is not None:
                decade = (year // 10) * 10
                dated.append((work, year, decade))

        if not dated:
            sampled, _ = self._sample_works(works, limit, "random", random_state)
            return sampled, "random"

        decade_groups = defaultdict(list)
        for work, year, decade in dated:
            decade_groups[decade].append((work, year))

        decades = sorted(decade_groups.keys())
        n_decades = len(decades)

        # Distribute limit across decades as evenly as possible
        base = limit // n_decades
        extra = limit % n_decades

        rng = np.random.RandomState(random_state)
        selected = []
        leftovers = []
        for i, decade in enumerate(decades):
            n_from_decade = base + (1 if i < extra else 0)
            candidates = decade_groups[decade]
            candidates.sort(key=lambda x: x[1])
            if len(candidates) <= n_from_decade:
                chosen = candidates
            else:
                indices = set(rng.choice(len(candidates), n_from_decade, replace=False))
                chosen = [candidates[idx] for idx in sorted(indices)]
                leftovers.extend(
                    candidates[idx]
                    for idx in range(len(candidates))
                    if idx not in indices
                )
            selected.extend([work for work, _ in chosen])

        # A decade with fewer candidates than its quota causes an undershoot;
        # redistribute the shortfall from decades that still have leftovers.
        shortfall = limit - len(selected)
        if shortfall > 0 and leftovers:
            n_extra = min(shortfall, len(leftovers))
            indices = rng.choice(len(leftovers), n_extra, replace=False)
            selected.extend(leftovers[idx][0] for idx in sorted(indices))

        return selected, "temporal"

    def _aggregate_palette(
        self,
        colors: List[Tuple[int, int, int]],
        n_colors: int,
        random_state: int,
        namer: Optional["ColorNamer"] = None,
    ) -> List[Tuple[int, int, int]]:
        """
        Aggregate a collection of colors into ``n_colors`` representatives.

        Clustering is performed in CIE Lab space to keep the aggregation
        perceptually meaningful, then cluster centers are converted back
        to sRGB. If the input contains fewer unique colors than requested,
        the unique colors are returned instead of forcing duplicate clusters.
        """
        if not colors:
            return []

        # Normalize to plain-Python int tuples
        colors = [tuple(int(c) for c in color) for color in colors]

        n_colors = min(n_colors, len(colors))
        if n_colors <= 0:
            return []

        if namer is None:
            from renoir.color import ColorNamer

            namer = ColorNamer()

        unique_colors = list(dict.fromkeys(colors))  # preserve order, deduplicate
        if n_colors >= len(unique_colors):
            return unique_colors

        labs = np.array([namer._rgb_to_lab(c) for c in colors])

        from sklearn.cluster import KMeans

        kmeans = KMeans(n_clusters=n_colors, random_state=random_state, n_init=10)
        kmeans.fit(labs)
        centers = kmeans.cluster_centers_

        aggregated = [namer._lab_to_rgb(tuple(center)) for center in centers]
        return aggregated

    def _compute_palette_metrics(
        self,
        palette: List[Tuple[int, int, int]],
        analyzer: "ColorAnalyzer",
    ) -> Dict[str, Any]:
        """Compute the standard color metrics for a palette."""
        if not palette:
            return {}
        return {
            "diversity": analyzer.calculate_color_diversity(palette),
            "saturation": analyzer.calculate_saturation_score(palette),
            "brightness": analyzer.calculate_brightness_score(palette),
            "temperature": analyzer.analyze_color_temperature_distribution(palette),
            "harmony": analyzer.analyze_color_harmony(palette),
            "complexity": analyzer.calculate_color_complexity(palette),
        }

    def _empty_signature(self, artist_name: Optional[str] = None) -> Dict[str, Any]:
        """Return a neutral signature result when no works can be analyzed."""
        return {
            "artist": artist_name,
            "n_works_analyzed": 0,
            "n_works_available": 0,
            "n_works_selected": 0,
            "requested_strategy": None,
            "effective_strategy": None,
            "date_range": None,
            "palette": [],
            "metrics": {},
            "by_period": {},
            "work_palettes": [],
            "figure": None,
        }

    def _build_signature_figure(
        self,
        palette: List[Tuple[int, int, int]],
        artist_name: Optional[str],
        by_period: Dict[str, Any],
        save_path: Optional[str],
        show: bool = False,
    ) -> Any:
        """Build a multi-panel overview figure for a color signature."""
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return None

        from renoir.color import ColorVisualizer
        import matplotlib.pyplot as plt
        import matplotlib.patches as patches

        title = artist_name if artist_name else "Artist"

        if by_period:
            fig = plt.figure(figsize=(14, 8))
            gs = fig.add_gridspec(2, 1, hspace=0.3)

            ax_palette = fig.add_subplot(gs[0])
            for i, color in enumerate(palette):
                normalized = tuple(c / 255 for c in color)
                rect = patches.Rectangle(
                    (i, 0), 1, 1, facecolor=normalized, edgecolor="black", linewidth=2
                )
                ax_palette.add_patch(rect)
            ax_palette.set_xlim(0, len(palette))
            ax_palette.set_ylim(0, 1)
            ax_palette.set_aspect("equal")
            ax_palette.axis("off")
            ax_palette.set_title(
                f"Color Signature: {title} — Aggregated Palette",
                fontsize=14,
                fontweight="bold",
            )

            ax_trend = fig.add_subplot(gs[1])
            periods = sorted(by_period.keys(), key=lambda p: int(p))
            complexities = [
                by_period[p]["metrics"].get("complexity", {}).get("cci", 0)
                for p in periods
            ]
            saturations = [
                by_period[p]["metrics"].get("saturation", 0) for p in periods
            ]

            ax_trend.plot(periods, complexities, marker="o", label="CCI", linewidth=2)
            ax_trend.plot(
                periods, saturations, marker="s", label="Saturation", linewidth=2
            )
            ax_trend.set_xlabel("Period", fontsize=12)
            ax_trend.set_ylabel("Score", fontsize=12)
            ax_trend.set_title("Temporal Evolution", fontsize=14, fontweight="bold")
            ax_trend.legend()
            ax_trend.grid(True, alpha=0.3)

            plt.tight_layout()

            if save_path:
                plt.savefig(save_path, dpi=300, bbox_inches="tight")
                print(f"Figure saved to {save_path}")
            if show:
                plt.show()

            return fig

        visualizer = ColorVisualizer()
        return visualizer.create_artist_color_report(
            palette, title, save_path=save_path, show=show
        )

    def analyze_works_color_signature(
        self,
        works: List[Dict[str, Any]],
        n_colors: int = 5,
        group_by_period: bool = True,
        include_figure: bool = False,
        save_path: Optional[str] = None,
        random_state: int = 42,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Compute a color signature from a provided list of artwork dictionaries.

        This lower-level method lets callers supply their own dated works,
        enabling full temporal analysis when the dataset includes date metadata.

        Args:
            works: List of artwork dictionaries. Each should contain an ``image``
                key (PIL Image or ndarray) and optionally a ``date`` key.
            n_colors: Number of dominant colors to extract per artwork and
                to return in the aggregated signature palette.
            group_by_period: If True and dates are available, also compute
                per-decade signatures.
            include_figure: If True, generate and return a matplotlib figure.
            save_path: Optional path to save the figure instead of displaying it.
            random_state: Random seed for reproducible extraction and sampling.
            verbose: If True, print progress messages.

        Returns:
            Dictionary with aggregated palette, metrics, optional per-period
            breakdown, and optional figure.
        """
        if not isinstance(works, list):
            raise ValueError("works must be a list")

        for i, work in enumerate(works):
            if not isinstance(work, dict):
                raise TypeError(f"Item at index {i} is not a dictionary")

        if not works:
            return self._empty_signature()

        import warnings

        from sklearn.exceptions import ConvergenceWarning

        from renoir.color import ColorExtractor, ColorAnalyzer, ColorNamer

        extractor = ColorExtractor()
        analyzer = ColorAnalyzer()
        namer = ColorNamer()

        work_palettes = []
        for i, work in enumerate(works):
            image = work.get("image")
            year = self._parse_year(work)

            if image is None:
                if verbose:
                    print(f"Warning: work {i} has no image; skipping")
                continue

            try:
                with warnings.catch_warnings():
                    warnings.simplefilter("ignore", ConvergenceWarning)
                    palette = extractor.extract_dominant_colors(
                        image,
                        n_colors=n_colors,
                        random_state=random_state,
                    )
                work_palettes.append((work, palette, year))
                if verbose and (i + 1) % 5 == 0:
                    print(f"  Processed {i + 1}/{len(works)} works...")
            except Exception as e:
                if verbose:
                    print(f"Warning: failed to extract palette for work {i}: {e}")
                continue

        if not work_palettes:
            return self._empty_signature()

        all_colors = [color for _, palette, _ in work_palettes for color in palette]
        signature_palette = self._aggregate_palette(
            all_colors, n_colors, random_state, namer
        )
        metrics = self._compute_palette_metrics(signature_palette, analyzer)

        by_period: Dict[str, Any] = {}
        if group_by_period:
            period_groups = defaultdict(list)
            for work, palette, year in work_palettes:
                if year is not None:
                    decade = (year // 10) * 10
                    period_groups[decade].append((work, palette, year))

            for period in sorted(period_groups.keys()):
                group = period_groups[period]
                period_colors = [c for _, palette, _ in group for c in palette]
                period_palette = self._aggregate_palette(
                    period_colors, n_colors, random_state, namer
                )
                by_period[str(period)] = {
                    "n_works": len(group),
                    "years": sorted({y for _, _, y in group if y is not None}),
                    "palette": period_palette,
                    "metrics": self._compute_palette_metrics(period_palette, analyzer),
                }

        years = [y for _, _, y in work_palettes if y is not None]
        date_range = (min(years), max(years)) if years else None

        figure = None
        if include_figure:
            figure = self._build_signature_figure(
                signature_palette, None, by_period, save_path
            )

        return {
            "artist": None,
            "n_works_analyzed": len(work_palettes),
            "n_works_available": len(works),
            "n_works_selected": len(work_palettes),
            "requested_strategy": None,
            "effective_strategy": None,
            "date_range": date_range,
            "palette": signature_palette,
            "metrics": metrics,
            "by_period": by_period,
            "work_palettes": [
                {
                    "title": work.get("title", "Unknown"),
                    "artist": work.get("artist", "Unknown"),
                    "year": year,
                    "palette": palette,
                }
                for work, palette, year in work_palettes
            ],
            "figure": figure,
        }

    def artist_color_signature(
        self,
        artist_name: str,
        limit: int = 10,
        n_colors: int = 5,
        strategy: str = "temporal",
        include_figure: bool = False,
        save_path: Optional[str] = None,
        random_state: int = 42,
        verbose: bool = True,
    ) -> Dict[str, Any]:
        """
        Compute a color signature for an artist from WikiArt.

        By default, extracts up to 10 works sampled to maximize temporal
        coverage. If no parseable dates are available in the dataset, the
        method falls back to random sampling and reports the effective
        strategy in the result.

        Args:
            artist_name: Artist name as it appears in WikiArt.
            limit: Maximum number of works to analyze (default: 10).
            n_colors: Number of colors in the signature palette.
            strategy: Sampling strategy — ``'temporal'`` (default),
                ``'random'``, or ``'first'``.
            include_figure: If True, generate a visualization.
            save_path: Optional path to save the figure.
            random_state: Seed for reproducible sampling and extraction.
            verbose: If True, print progress messages.

        Returns:
            Dictionary with artist color signature, metrics, optional
            per-period breakdown, and optional figure.
        """
        if not artist_name or not isinstance(artist_name, str):
            raise ValueError("artist_name must be a non-empty string")

        if artist_name.strip() == "":
            raise ValueError("artist_name cannot be empty or whitespace")

        if not isinstance(limit, int):
            raise ValueError("limit must be an integer")

        if limit < 1:
            raise ValueError("limit must be at least 1")

        if verbose:
            print(f"Computing color signature for {artist_name}...")

        # For "first" strategy we can avoid loading the full corpus.
        extract_limit = limit if strategy == "first" else None
        works = self.extract_artist_works(artist_name, limit=extract_limit)

        if not works:
            return self._empty_signature(artist_name=artist_name)

        actual_limit = min(limit, len(works))
        selected, effective_strategy = self._sample_works(
            works, actual_limit, strategy, random_state
        )

        if effective_strategy != strategy and verbose:
            print(
                f"Note: '{strategy}' sampling not possible (no parseable dates). "
                f"Using '{effective_strategy}' instead."
            )

        if verbose:
            print(f"Analyzing {len(selected)} works...")

        result = self.analyze_works_color_signature(
            selected,
            n_colors=n_colors,
            group_by_period=True,
            include_figure=include_figure,
            save_path=save_path,
            random_state=random_state,
            verbose=verbose,
        )

        result["artist"] = artist_name
        result["n_works_available"] = len(works)
        result["n_works_selected"] = len(selected)
        result["requested_strategy"] = strategy
        result["effective_strategy"] = effective_strategy

        return result


def quick_analysis(
    artist_name: str,
    limit: Optional[int] = None,
    show_summary: bool = True,
    show_plots: bool = False,
) -> List[Dict[str, Any]]:
    """
    Quick function to analyze an artist's works with minimal setup.

    This is a convenience function for beginners, combining extraction
    and analysis in a single call.

    Args:
        artist_name: Artist name as it appears in WikiArt
        limit: Optional maximum number of works to retrieve
        show_summary: If True, print a summary of the results
        show_plots: If True, display visualization plots (requires matplotlib)

    Returns:
        List of artwork dictionaries

    Examples:
        >>> works = quick_analysis('claude-monet', limit=20)
        Loading WikiArt dataset...
        ✓ Loaded 103250 artworks
        ✓ Found 20 works by claude-monet

        Artist Summary:
        - Total works: 20
        - Primary style: Impressionism
        - Primary genre: landscape
        - Date range: 1865-1926

        >>> works = quick_analysis('claude-monet', limit=20, show_plots=True)
        # Displays visualization plots
    """
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works(artist_name, limit=limit)

    if show_summary and works:
        summary = analyzer.get_work_summary(works)
        print("\nArtist Summary:")
        print(f"- Total works: {summary['total_works']}")
        print(f"- Primary style: {summary['primary_style']}")
        print(f"- Primary genre: {summary['primary_genre']}")
        if summary["date_range"]:
            print(
                f"- Date range: {summary['date_range'][0]}-{summary['date_range'][1]}"
            )

    if show_plots:
        analyzer.create_artist_overview(artist_name, limit=limit)

    return works
