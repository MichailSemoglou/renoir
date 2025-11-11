"""
Tests for the color analysis module.

These tests verify color space conversions, statistics, and analysis functions.
"""

import pytest
import numpy as np

from renoir.color import ColorAnalyzer


@pytest.fixture
def analyzer():
    """Create a ColorAnalyzer instance for testing."""
    return ColorAnalyzer()


def test_analyzer_initialization(analyzer):
    """Test that ColorAnalyzer initializes correctly."""
    assert analyzer is not None


def test_rgb_to_hsv(analyzer):
    """Test RGB to HSV conversion."""
    # Red
    hsv = analyzer.rgb_to_hsv((255, 0, 0))
    assert hsv[0] == pytest.approx(0, abs=1)  # Hue
    assert hsv[1] == pytest.approx(100, abs=1)  # Saturation
    assert hsv[2] == pytest.approx(100, abs=1)  # Value

    # Green
    hsv = analyzer.rgb_to_hsv((0, 255, 0))
    assert hsv[0] == pytest.approx(120, abs=1)
    assert hsv[1] == pytest.approx(100, abs=1)
    assert hsv[2] == pytest.approx(100, abs=1)

    # Blue
    hsv = analyzer.rgb_to_hsv((0, 0, 255))
    assert hsv[0] == pytest.approx(240, abs=1)
    assert hsv[1] == pytest.approx(100, abs=1)
    assert hsv[2] == pytest.approx(100, abs=1)

    # White
    hsv = analyzer.rgb_to_hsv((255, 255, 255))
    assert hsv[1] == pytest.approx(0, abs=1)  # No saturation
    assert hsv[2] == pytest.approx(100, abs=1)  # Full value

    # Black
    hsv = analyzer.rgb_to_hsv((0, 0, 0))
    assert hsv[1] == pytest.approx(0, abs=1)
    assert hsv[2] == pytest.approx(0, abs=1)


def test_hsv_to_rgb(analyzer):
    """Test HSV to RGB conversion."""
    # Red
    rgb = analyzer.hsv_to_rgb((0, 100, 100))
    assert rgb == (255, 0, 0)

    # Green
    rgb = analyzer.hsv_to_rgb((120, 100, 100))
    assert rgb == (0, 255, 0)

    # Blue
    rgb = analyzer.hsv_to_rgb((240, 100, 100))
    assert rgb == (0, 0, 255)


def test_rgb_hsv_roundtrip(analyzer):
    """Test RGB->HSV->RGB conversion accuracy."""
    test_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
        (0, 255, 255),
    ]

    for rgb in test_colors:
        hsv = analyzer.rgb_to_hsv(rgb)
        back_to_rgb = analyzer.hsv_to_rgb(hsv)
        # Allow small rounding errors
        for i in range(3):
            assert abs(rgb[i] - back_to_rgb[i]) <= 1


def test_rgb_to_hsl(analyzer):
    """Test RGB to HSL conversion."""
    # Red
    hsl = analyzer.rgb_to_hsl((255, 0, 0))
    assert hsl[0] == pytest.approx(0, abs=1)
    assert hsl[1] == pytest.approx(100, abs=1)
    assert hsl[2] == pytest.approx(50, abs=1)

    # Gray
    hsl = analyzer.rgb_to_hsl((128, 128, 128))
    assert hsl[1] == pytest.approx(0, abs=1)  # No saturation
    assert hsl[2] == pytest.approx(50, abs=2)  # 50% lightness


def test_hsl_to_rgb(analyzer):
    """Test HSL to RGB conversion."""
    # Red
    rgb = analyzer.hsl_to_rgb((0, 100, 50))
    assert rgb[0] == 255
    assert rgb[1] <= 1  # Should be close to 0
    assert rgb[2] <= 1


def test_analyze_palette_statistics(analyzer):
    """Test palette statistics analysis."""
    colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
    ]

    stats = analyzer.analyze_palette_statistics(colors)

    assert isinstance(stats, dict)
    assert "mean_hue" in stats
    assert "mean_saturation" in stats
    assert "mean_value" in stats
    assert "std_hue" in stats
    assert "std_saturation" in stats
    assert "std_value" in stats

    # All test colors are fully saturated
    assert stats["mean_saturation"] == pytest.approx(100, abs=5)
    assert stats["mean_value"] == pytest.approx(100, abs=5)


def test_analyze_palette_statistics_empty(analyzer):
    """Test statistics with empty palette."""
    stats = analyzer.analyze_palette_statistics([])

    # Empty palette returns empty dict
    assert stats == {}


def test_calculate_color_diversity(analyzer):
    """Test color diversity calculation."""
    # Diverse palette
    diverse_colors = [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
        (0, 255, 255),  # Cyan
    ]
    diversity_high = analyzer.calculate_color_diversity(diverse_colors)
    assert 0 <= diversity_high <= 1
    assert diversity_high > 0.5  # Should be high

    # Low diversity (similar colors)
    similar_colors = [
        (255, 0, 0),
        (250, 5, 5),
        (245, 10, 10),
    ]
    diversity_low = analyzer.calculate_color_diversity(similar_colors)
    assert 0 <= diversity_low <= 1
    assert diversity_low < diversity_high


def test_calculate_color_diversity_edge_cases(analyzer):
    """Test diversity calculation edge cases."""
    # Single color
    assert analyzer.calculate_color_diversity([(255, 0, 0)]) >= 0

    # Empty list
    assert analyzer.calculate_color_diversity([]) == 0


def test_calculate_saturation_score(analyzer):
    """Test saturation score calculation."""
    # High saturation colors
    vivid = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    score_vivid = analyzer.calculate_saturation_score(vivid)
    assert score_vivid > 90

    # Low saturation colors (grays)
    muted = [(128, 128, 128), (100, 100, 100), (150, 150, 150)]
    score_muted = analyzer.calculate_saturation_score(muted)
    assert score_muted < 10


def test_calculate_brightness_score(analyzer):
    """Test brightness score calculation."""
    # Bright colors
    bright = [(255, 255, 255), (255, 255, 0), (255, 0, 255)]
    score_bright = analyzer.calculate_brightness_score(bright)
    assert score_bright > 90

    # Dark colors
    dark = [(0, 0, 0), (10, 10, 10), (20, 20, 20)]
    score_dark = analyzer.calculate_brightness_score(dark)
    assert score_dark < 10


def test_compare_palettes(analyzer):
    """Test palette comparison."""
    palette1 = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    palette2 = [(128, 0, 0), (0, 128, 0), (0, 0, 128)]

    comparison = analyzer.compare_palettes(palette1, palette2)

    assert isinstance(comparison, dict)
    assert "palette1_stats" in comparison
    assert "palette2_stats" in comparison
    assert "hue_diff" in comparison
    assert "saturation_diff" in comparison
    assert "brightness_diff" in comparison
    assert "diversity_diff" in comparison

    # Palette1 should have higher brightness
    assert comparison["brightness_diff"] > 0


def test_classify_color_temperature(analyzer):
    """Test color temperature classification."""
    # Warm colors (hue 0-60 or 300-360)
    assert analyzer.classify_color_temperature((255, 0, 0)) == "warm"  # Red
    assert analyzer.classify_color_temperature((255, 165, 0)) == "warm"  # Orange
    assert analyzer.classify_color_temperature((255, 255, 0)) == "warm"  # Yellow (hue ~60)

    # Cool colors (hue 120-300)
    assert analyzer.classify_color_temperature((0, 255, 0)) == "cool"  # Green
    assert analyzer.classify_color_temperature((0, 0, 255)) == "cool"  # Blue
    assert analyzer.classify_color_temperature((128, 0, 128)) == "cool"  # Purple

    # Neutral (low saturation < 10%)
    assert analyzer.classify_color_temperature((128, 128, 128)) == "neutral"  # Gray
    assert (
        analyzer.classify_color_temperature((200, 200, 200)) == "neutral"
    )  # Light gray


def test_analyze_color_temperature_distribution(analyzer):
    """Test temperature distribution analysis."""
    colors = [
        (255, 0, 0),  # Warm
        (255, 165, 0),  # Warm
        (0, 255, 0),  # Cool
        (0, 0, 255),  # Cool
        (128, 128, 128),  # Neutral
    ]

    dist = analyzer.analyze_color_temperature_distribution(colors)

    assert isinstance(dist, dict)
    assert "warm_count" in dist
    assert "cool_count" in dist
    assert "neutral_count" in dist
    assert "warm_percentage" in dist
    assert "cool_percentage" in dist
    assert "neutral_percentage" in dist
    assert "dominant_temperature" in dist

    assert dist["warm_count"] == 2
    assert dist["cool_count"] == 2
    assert dist["neutral_count"] == 1
    assert dist["warm_percentage"] == pytest.approx(40, abs=1)
    assert dist["cool_percentage"] == pytest.approx(40, abs=1)


def test_detect_complementary_colors(analyzer):
    """Test complementary color detection."""
    # Red and cyan are complementary
    colors = [
        (255, 0, 0),  # Red (hue 0)
        (0, 255, 255),  # Cyan (hue 180)
        (0, 255, 0),  # Green (not complementary to others)
    ]

    pairs = analyzer.detect_complementary_colors(colors, tolerance=30)

    assert isinstance(pairs, list)
    # Should find the red-cyan pair
    assert len(pairs) >= 1


def test_detect_complementary_colors_no_matches(analyzer):
    """Test complementary detection with no matches."""
    colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
    pairs = analyzer.detect_complementary_colors(colors)
    assert len(pairs) == 0


def test_calculate_contrast_ratio(analyzer):
    """Test WCAG contrast ratio calculation."""
    # Black on white (maximum contrast)
    ratio = analyzer.calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
    assert ratio == pytest.approx(21, abs=0.1)

    # White on white (minimum contrast)
    ratio = analyzer.calculate_contrast_ratio((255, 255, 255), (255, 255, 255))
    assert ratio == pytest.approx(1, abs=0.1)

    # Check that ratio is always >= 1
    ratio = analyzer.calculate_contrast_ratio((100, 100, 100), (200, 200, 200))
    assert ratio >= 1


def test_contrast_ratio_symmetry(analyzer):
    """Test that contrast ratio is symmetric."""
    color1 = (100, 150, 200)
    color2 = (50, 75, 100)

    ratio1 = analyzer.calculate_contrast_ratio(color1, color2)
    ratio2 = analyzer.calculate_contrast_ratio(color2, color1)

    assert ratio1 == pytest.approx(ratio2, abs=0.01)


def test_wcag_compliance_check(analyzer):
    """Test WCAG contrast ratio compliance."""
    # High contrast should pass
    ratio = analyzer.calculate_contrast_ratio((0, 0, 0), (255, 255, 255))
    assert ratio > 4.5  # WCAG AA minimum

    # Low contrast should fail
    ratio = analyzer.calculate_contrast_ratio((200, 200, 200), (210, 210, 210))
    assert ratio < 4.5
