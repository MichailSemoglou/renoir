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
        """Lazy load the WikiArt dataset."""
        if self._dataset is None:
            print("Loading WikiArt dataset...")
            self._dataset = load_dataset(
                "huggan/wikiart",
                split="train",
                cache_dir=self.cache_dir
            )
            print(f"✓ Loaded {len(self._dataset)} artworks")
        return self._dataset

    def extract_artist_works(
        self,
        artist_name: str,
        limit: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Extract all works by a specific artist from WikiArt.

        Args:
            artist_name: Artist name as it appears in WikiArt (e.g., 'claude-monet')
            limit: Optional maximum number of works to return

        Returns:
            List of dictionaries containing artwork data (image, metadata)

        Examples:
            >>> analyzer = ArtistAnalyzer()
            >>> monet_works = analyzer.extract_artist_works('claude-monet', limit=10)
            >>> print(monet_works[0].keys())
            dict_keys(['image', 'artist', 'title', 'style', 'genre', 'date'])
        """
        dataset = self._load_dataset()

        # Filter for specific artist
        artist_works = []
        for item in dataset:
            if item.get('artist', '').lower() == artist_name.lower():
                artist_works.append(item)
                if limit and len(artist_works) >= limit:
                    break

        print(f"✓ Found {len(artist_works)} works by {artist_name}")
        return artist_works

    def analyze_genres(self, works: List[Dict[str, Any]]) -> List[tuple]:
        """
        Analyze genre distribution in a collection of works.

        Args:
            works: List of artwork dictionaries

        Returns:
            List of (genre, count) tuples, sorted by frequency

        Examples:
            >>> works = analyzer.extract_artist_works('claude-monet')
            >>> genres = analyzer.analyze_genres(works)
            >>> print(f"Most common genre: {genres[0][0]} ({genres[0][1]} works)")
        """
        genres = [work.get('genre', 'Unknown') for work in works]
        genre_counts = Counter(genres).most_common()
        return genre_counts

    def analyze_styles(self, works: List[Dict[str, Any]]) -> List[tuple]:
        """
        Analyze style distribution in a collection of works.

        Args:
            works: List of artwork dictionaries

        Returns:
            List of (style, count) tuples, sorted by frequency

        Examples:
            >>> works = analyzer.extract_artist_works('pablo-picasso')
            >>> styles = analyzer.analyze_styles(works)
            >>> for style, count in styles[:3]:
            ...     print(f"{style}: {count} works")
        """
        styles = [work.get('style', 'Unknown') for work in works]
        style_counts = Counter(styles).most_common()
        return style_counts

    def analyze_temporal_distribution(
        self,
        works: List[Dict[str, Any]]
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
            date = work.get('date')
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
                'total_works': 0,
                'artist': None,
                'primary_style': None,
                'primary_genre': None,
                'date_range': None
            }

        genres = self.analyze_genres(works)
        styles = self.analyze_styles(works)

        # Extract date range
        dates = []
        for work in works:
            date = work.get('date')
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
            'total_works': len(works),
            'artist': works[0].get('artist', 'Unknown'),
            'primary_style': styles[0][0] if styles else None,
            'primary_genre': genres[0][0] if genres else None,
            'date_range': date_range,
            'all_genres': genres,
            'all_styles': styles
        }


def quick_analysis(
    artist_name: str,
    limit: Optional[int] = None,
    show_summary: bool = True
) -> List[Dict[str, Any]]:
    """
    Quick function to analyze an artist's works with minimal setup.

    This is a convenience function for beginners, combining extraction
    and analysis in a single call.

    Args:
        artist_name: Artist name as it appears in WikiArt
        limit: Optional maximum number of works to retrieve
        show_summary: If True, print a summary of the results

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
    """
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works(artist_name, limit=limit)

    if show_summary and works:
        summary = analyzer.get_work_summary(works)
        print("\nArtist Summary:")
        print(f"- Total works: {summary['total_works']}")
        print(f"- Primary style: {summary['primary_style']}")
        print(f"- Primary genre: {summary['primary_genre']}")
        if summary['date_range']:
            print(f"- Date range: {summary['date_range'][0]}-{summary['date_range'][1]}")

    return works
