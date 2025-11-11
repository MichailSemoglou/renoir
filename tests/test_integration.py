"""
Integration tests for renoir package.

These tests verify complete workflows from data extraction through analysis
to visualization and export.
"""

import pytest
import tempfile
import os
import json
from unittest.mock import Mock, patch
import numpy as np
from PIL import Image

from renoir import ArtistAnalyzer, quick_analysis
from renoir.color import ColorExtractor, ColorAnalyzer, ColorVisualizer


@pytest.fixture
def mock_dataset():
    """Create a mock WikiArt dataset for testing."""
    # Create sample images
    img1 = Image.new('RGB', (50, 50), color='red')
    img2 = Image.new('RGB', (50, 50), color='blue')
    img3 = Image.new('RGB', (50, 50), color='green')

    return [
        {'artist': 'test-artist', 'title': 'Test Work 1', 'image': img1, 'genre': 'landscape', 'style': 'impressionism', 'date': '1890'},
        {'artist': 'test-artist', 'title': 'Test Work 2', 'image': img2, 'genre': 'portrait', 'style': 'impressionism', 'date': '1895'},
        {'artist': 'test-artist', 'title': 'Test Work 3', 'image': img3, 'genre': 'landscape', 'style': 'post-impressionism', 'date': '1900'},
        {'artist': 'other-artist', 'title': 'Other Work', 'image': img1, 'genre': 'abstract', 'style': 'modernism', 'date': '1920'},
    ]


def test_full_artist_analysis_workflow(mock_dataset):
    """Test complete workflow: extract -> analyze -> summarize."""
    with patch.object(ArtistAnalyzer, '_load_dataset', return_value=mock_dataset):
        # Extract works
        analyzer = ArtistAnalyzer()
        works = analyzer.extract_artist_works('test-artist')

        assert len(works) == 3

        # Analyze genres
        genres = analyzer.analyze_genres(works)
        assert len(genres) > 0
        assert genres[0][0] in ['landscape', 'portrait']

        # Analyze styles
        styles = analyzer.analyze_styles(works)
        assert len(styles) > 0

        # Get summary
        summary = analyzer.get_work_summary(works)
        assert summary['total_works'] == 3
        assert summary['artist'] == 'test-artist'


def test_full_color_extraction_workflow():
    """Test complete color extraction workflow."""
    # Create test image
    img = Image.new('RGB', (100, 100))
    pixels = img.load()
    for i in range(100):
        for j in range(100):
            if i < 50 and j < 50:
                pixels[i, j] = (255, 0, 0)  # Red
            elif i < 50:
                pixels[i, j] = (0, 255, 0)  # Green
            elif j < 50:
                pixels[i, j] = (0, 0, 255)  # Blue
            else:
                pixels[i, j] = (255, 255, 0)  # Yellow

    # Extract colors
    extractor = ColorExtractor()
    colors = extractor.extract_dominant_colors(img, n_colors=4)

    assert len(colors) == 4
    assert all(isinstance(c, tuple) and len(c) == 3 for c in colors)


def test_full_color_analysis_workflow():
    """Test complete color analysis workflow."""
    # Create test palette
    colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
    ]

    analyzer = ColorAnalyzer()

    # Convert colors
    hsv_colors = [analyzer.rgb_to_hsv(c) for c in colors]
    assert len(hsv_colors) == 5

    # Analyze statistics
    stats = analyzer.analyze_palette_statistics(colors)
    assert 'mean_saturation' in stats
    assert 'mean_value' in stats

    # Calculate diversity
    diversity = analyzer.calculate_color_diversity(colors)
    assert 0 <= diversity <= 1

    # Analyze temperature
    temp = analyzer.analyze_color_temperature_distribution(colors)
    assert 'warm_count' in temp
    assert 'cool_count' in temp


def test_export_workflow():
    """Test complete export workflow."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    extractor = ColorExtractor()

    with tempfile.TemporaryDirectory() as tmpdir:
        # Export as CSS
        css_path = os.path.join(tmpdir, 'test.css')
        extractor.export_palette_css(colors, css_path, prefix='test')
        assert os.path.exists(css_path)

        with open(css_path, 'r') as f:
            content = f.read()
            assert '--test-1' in content
            assert '#ff0000' in content

        # Export as JSON
        json_path = os.path.join(tmpdir, 'test.json')
        extractor.export_palette_json(colors, json_path)
        assert os.path.exists(json_path)

        with open(json_path, 'r') as f:
            data = json.load(f)
            assert 'rgb_values' in data
            assert len(data['rgb_values']) == 3


def test_artist_to_palette_workflow(mock_dataset):
    """Test workflow from artist extraction to palette extraction."""
    with patch.object(ArtistAnalyzer, '_load_dataset', return_value=mock_dataset):
        # Extract artist works
        analyzer = ArtistAnalyzer()
        works = analyzer.extract_artist_works('test-artist', limit=2)

        assert len(works) == 2

        # Extract palette from first work
        extractor = ColorExtractor()
        palette = extractor.extract_palette_from_artwork(works[0], n_colors=3)

        assert 'colors' in palette
        assert 'artwork' in palette
        assert len(palette['colors']) == 3


def test_comparative_analysis_workflow(mock_dataset):
    """Test workflow comparing multiple artists."""
    with patch.object(ArtistAnalyzer, '_load_dataset', return_value=mock_dataset):
        analyzer = ArtistAnalyzer()

        # Extract works from both artists
        artist1_works = analyzer.extract_artist_works('test-artist')
        artist2_works = analyzer.extract_artist_works('other-artist')

        assert len(artist1_works) == 3
        assert len(artist2_works) == 1

        # Compare genres
        genres1 = analyzer.analyze_genres(artist1_works)
        genres2 = analyzer.analyze_genres(artist2_works)

        assert len(genres1) > 0
        assert len(genres2) > 0


def test_error_recovery_workflow():
    """Test that workflows handle errors gracefully."""
    analyzer = ArtistAnalyzer()
    extractor = ColorExtractor()
    color_analyzer = ColorAnalyzer()

    # Test empty inputs
    assert analyzer.analyze_genres([]) == []
    assert analyzer.analyze_styles([]) == []

    # Test invalid inputs with proper error messages
    with pytest.raises(ValueError):
        analyzer.extract_artist_works('')

    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(Image.new('RGB', (10, 10)), n_colors=0)

    with pytest.raises(ValueError):
        color_analyzer.rgb_to_hsv((300, 0, 0))  # Invalid RGB value


def test_quick_analysis_integration(mock_dataset):
    """Test the quick_analysis convenience function."""
    with patch.object(ArtistAnalyzer, '_load_dataset', return_value=mock_dataset):
        # Run quick analysis
        works = quick_analysis('test-artist', limit=2, show_summary=False)

        assert len(works) == 2
        assert all('image' in w for w in works)


def test_roundtrip_color_conversion_integration():
    """Test that color conversions maintain accuracy through full workflow."""
    test_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 128, 128),
        (255, 255, 0),
    ]

    analyzer = ColorAnalyzer()

    for rgb in test_colors:
        # RGB -> HSV -> RGB
        hsv = analyzer.rgb_to_hsv(rgb)
        back_to_rgb = analyzer.hsv_to_rgb(hsv)

        # Allow small rounding errors
        for i in range(3):
            assert abs(rgb[i] - back_to_rgb[i]) <= 2

        # RGB -> HSL -> RGB
        hsl = analyzer.rgb_to_hsl(rgb)
        back_to_rgb = analyzer.hsl_to_rgb(hsl)

        for i in range(3):
            assert abs(rgb[i] - back_to_rgb[i]) <= 2


@pytest.mark.parametrize('n_colors', [1, 3, 5, 10])
def test_color_extraction_scales(n_colors):
    """Test that color extraction works with different numbers of colors."""
    img = Image.new('RGB', (50, 50), color='red')
    extractor = ColorExtractor()

    colors = extractor.extract_dominant_colors(img, n_colors=n_colors)
    assert len(colors) == n_colors


def test_palette_comparison_workflow():
    """Test comparing two palettes end-to-end."""
    palette1 = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    palette2 = [(128, 0, 0), (0, 128, 0), (0, 0, 128)]

    analyzer = ColorAnalyzer()

    comparison = analyzer.compare_palettes(palette1, palette2)

    assert 'palette1_stats' in comparison
    assert 'palette2_stats' in comparison
    assert 'saturation_diff' in comparison
    assert 'brightness_diff' in comparison

    # Palette1 should have higher brightness
    assert comparison['brightness_diff'] > 0


def test_input_validation_throughout_workflow():
    """Test that input validation works at every stage."""
    analyzer = ArtistAnalyzer()
    extractor = ColorExtractor()
    color_analyzer = ColorAnalyzer()

    # Test various invalid inputs
    with pytest.raises((ValueError, TypeError)):
        analyzer.extract_artist_works(None)

    with pytest.raises((ValueError, TypeError)):
        analyzer.analyze_genres("not a list")

    with pytest.raises((ValueError, TypeError)):
        extractor.extract_dominant_colors("not an image", n_colors=5)

    with pytest.raises((ValueError, TypeError)):
        color_analyzer.rgb_to_hsv("not a tuple")

    with pytest.raises((ValueError, TypeError)):
        color_analyzer.analyze_palette_statistics("not a list")
