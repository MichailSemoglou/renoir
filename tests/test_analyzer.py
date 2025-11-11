"""
Basic tests for the renoir package.

These tests can be expanded as the package develops.
"""

import pytest
from renoir import ArtistAnalyzer, quick_analysis, check_visualization_support


def test_artist_analyzer_initialization():
    """Test that the analyzer initializes correctly."""
    analyzer = ArtistAnalyzer()
    assert analyzer._dataset is None  # Dataset loaded lazily


def test_extract_artist_works():
    """Test extracting works for a specific artist."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir', limit=5)
    assert isinstance(works, list)
    assert len(works) > 0
    assert len(works) <= 5

    # Check that all works have required keys
    for work in works:
        assert 'artist' in work
        assert 'image' in work


def test_analyze_genres():
    """Test genre analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir', limit=10)
    genres = analyzer.analyze_genres(works)

    assert isinstance(genres, list)
    assert len(genres) > 0
    # Each genre should be a tuple of (name, count)
    for genre_tuple in genres:
        assert isinstance(genre_tuple, tuple)
        assert len(genre_tuple) == 2
        assert isinstance(genre_tuple[0], str)
        assert isinstance(genre_tuple[1], int)


def test_analyze_styles():
    """Test style analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir', limit=10)
    styles = analyzer.analyze_styles(works)

    assert isinstance(styles, list)
    assert len(styles) > 0
    # Each style should be a tuple of (name, count)
    for style_tuple in styles:
        assert isinstance(style_tuple, tuple)
        assert len(style_tuple) == 2
        assert isinstance(style_tuple[0], str)
        assert isinstance(style_tuple[1], int)


def test_analyze_temporal_distribution():
    """Test temporal distribution analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir', limit=10)
    temporal = analyzer.analyze_temporal_distribution(works)

    assert isinstance(temporal, dict)
    # Keys should be decades (integers)
    for decade, count in temporal.items():
        assert isinstance(decade, int)
        assert isinstance(count, int)
        assert decade % 10 == 0  # Should be a decade


def test_get_work_summary():
    """Test work summary generation."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir', limit=10)
    summary = analyzer.get_work_summary(works)

    assert isinstance(summary, dict)
    assert 'total_works' in summary
    assert 'artist' in summary
    assert 'primary_style' in summary
    assert 'primary_genre' in summary
    assert 'date_range' in summary
    assert summary['total_works'] == len(works)


def test_quick_analysis():
    """Test quick analysis function."""
    works = quick_analysis('claude-monet', limit=5, show_summary=False)
    assert isinstance(works, list)
    assert len(works) > 0
    assert len(works) <= 5


def test_visualization_support():
    """Test visualization support detection."""
    # This will return True or False depending on whether matplotlib is installed
    result = check_visualization_support()
    assert isinstance(result, bool)


def test_visualization_methods_exist():
    """Test that visualization methods exist on ArtistAnalyzer."""
    analyzer = ArtistAnalyzer()

    # Check that visualization methods exist
    assert hasattr(analyzer, 'plot_genre_distribution')
    assert hasattr(analyzer, 'plot_style_distribution')
    assert hasattr(analyzer, 'compare_artists_genres')
    assert hasattr(analyzer, 'create_artist_overview')
    assert hasattr(analyzer, '_check_visualization_available')


def test_visualization_check():
    """Test the visualization availability check."""
    analyzer = ArtistAnalyzer()
    result = analyzer._check_visualization_available()
    assert isinstance(result, bool)


def test_empty_works_handling():
    """Test that methods handle empty works lists gracefully."""
    analyzer = ArtistAnalyzer()

    empty_works = []

    # These should not raise errors
    genres = analyzer.analyze_genres(empty_works)
    assert genres == []

    styles = analyzer.analyze_styles(empty_works)
    assert styles == []

    temporal = analyzer.analyze_temporal_distribution(empty_works)
    assert temporal == {}

    summary = analyzer.get_work_summary(empty_works)
    assert summary['total_works'] == 0
