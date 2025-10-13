"""
Basic tests for the renoir package.

These tests can be expanded as the package develops.
"""

import pytest
from renoir import ArtistAnalyzer, check_visualization_support


def test_artist_analyzer_initialization():
    """Test that the analyzer initializes correctly."""
    analyzer = ArtistAnalyzer()
    assert analyzer.dataset is not None
    assert len(analyzer.artist_names) > 0
    assert len(analyzer.genre_names) > 0
    assert len(analyzer.style_names) > 0


def test_get_artist_index():
    """Test artist index retrieval."""
    analyzer = ArtistAnalyzer()
    renoir_index = analyzer.get_artist_index('pierre-auguste-renoir')
    assert renoir_index is not None
    assert isinstance(renoir_index, int)
    
    # Test non-existent artist
    invalid_index = analyzer.get_artist_index('non-existent-artist')
    assert invalid_index is None


def test_extract_artist_works():
    """Test extracting works for a specific artist."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir')
    assert isinstance(works, list)
    assert len(works) > 0
    
    # Check that all works are by Renoir
    renoir_index = analyzer.get_artist_index('pierre-auguste-renoir')
    for work in works:
        assert work['artist'] == renoir_index


def test_analyze_genres():
    """Test genre analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir')
    genres = analyzer.analyze_genres(works)
    
    assert isinstance(genres, dict)
    assert len(genres) > 0
    assert all(isinstance(k, str) for k in genres.keys())
    assert all(isinstance(v, int) for v in genres.values())


def test_analyze_styles():
    """Test style analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works('pierre-auguste-renoir')
    styles = analyzer.analyze_styles(works)
    
    assert isinstance(styles, dict)
    assert len(styles) > 0
    assert all(isinstance(k, str) for k in styles.keys())
    assert all(isinstance(v, int) for v in styles.values())


def test_list_artists():
    """Test listing artists."""
    analyzer = ArtistAnalyzer()
    
    # Test unlimited list
    all_artists = analyzer.list_artists()
    assert len(all_artists) > 0
    assert isinstance(all_artists, list)
    assert all(isinstance(artist, str) for artist in all_artists)
    
    # Test limited list
    limited_artists = analyzer.list_artists(limit=5)
    assert len(limited_artists) == 5
    assert limited_artists == all_artists[:5]


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
