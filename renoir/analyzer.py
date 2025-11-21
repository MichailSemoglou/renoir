"""
Artist analysis module for renoir.

This module provides functions for extracting and analyzing artist-specific works
from the WikiArt dataset, designed for educational use in computational design
and digital humanities courses.
"""

from typing import List, Dict, Optional, Any
from collections import Counter
from datasets import load_dataset


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

    def extract_artist_works(
        self, artist_name: str, limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract all works by a specific artist from WikiArt.

        Args:
            artist_name: Artist name as it appears in WikiArt (e.g., 'claude-monet')
            limit: Optional maximum number of works to return

        Returns:
            List of dictionaries containing artwork data (image, metadata)

        Raises:
            ValueError: If artist_name is empty or invalid
            ValueError: If limit is negative

        Examples:
            >>> analyzer = ArtistAnalyzer()
            >>> monet_works = analyzer.extract_artist_works('claude-monet', limit=10)
            >>> print(monet_works[0].keys())
            dict_keys(['image', 'artist', 'title', 'style', 'genre', 'date'])
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

        # Get artist names mapping from dataset features
        artist_names = dataset.features["artist"].names if hasattr(dataset.features["artist"], "names") else []

        # Find the target artist's index
        target_artist_idx = None
        for idx, name in enumerate(artist_names):
            if name.lower() == artist_name.lower():
                target_artist_idx = idx
                break

        if target_artist_idx is None:
            print(f"⚠ Artist '{artist_name}' not found in dataset")
            print(f"  Tip: Check spelling and use lowercase with hyphens (e.g., 'claude-monet')")
            return []

        # Filter for specific artist
        artist_works = []
        try:
            for item in dataset:
                # Artist field is an integer (ClassLabel index)
                artist_field = item.get("artist")
                if artist_field == target_artist_idx:
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
    ) -> None:
        """
        Plot genre distribution for a specific artist as a bar chart.

        Args:
            artist_name: Artist name as it appears in WikiArt
            limit: Optional limit on number of works to analyze
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> analyzer.plot_genre_distribution('pierre-auguste-renoir')
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return

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
        else:
            plt.show()

    def plot_style_distribution(
        self,
        artist_name: str,
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (10, 6),
    ) -> None:
        """
        Plot style distribution for a specific artist as a bar chart.

        Args:
            artist_name: Artist name as it appears in WikiArt
            limit: Optional limit on number of works to analyze
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> analyzer.plot_style_distribution('pablo-picasso')
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return

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
        else:
            plt.show()

    def compare_artists_genres(
        self,
        artist_names: List[str],
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (12, 8),
    ) -> None:
        """
        Compare genre distributions across multiple artists.

        Args:
            artist_names: List of artist names to compare
            limit: Optional limit on number of works per artist
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> analyzer.compare_artists_genres(['claude-monet', 'pierre-auguste-renoir', 'edgar-degas'])
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return

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
        else:
            plt.show()

    def create_artist_overview(
        self,
        artist_name: str,
        limit: Optional[int] = None,
        save_path: Optional[str] = None,
        figsize: tuple = (14, 10),
    ) -> None:
        """
        Create a comprehensive overview visualization for an artist.

        Includes genre distribution, style distribution, and temporal analysis
        in a multi-panel figure.

        Args:
            artist_name: Artist name as it appears in WikiArt
            limit: Optional limit on number of works to analyze
            save_path: Optional path to save the figure
            figsize: Figure size as (width, height)

        Example:
            >>> analyzer = ArtistAnalyzer()
            >>> analyzer.create_artist_overview('vincent-van-gogh')
        """
        if not self._check_visualization_available():
            print("Visualization libraries not available.")
            print("Install with: pip install 'renoir-wikiart[visualization]'")
            return

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
        else:
            plt.show()


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
