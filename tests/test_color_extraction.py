"""
Tests for the color extraction module.

These tests verify color palette extraction and export functionality.
"""

import pytest
import numpy as np
from PIL import Image
import tempfile
import os
import json

from renoir.color import ColorExtractor


@pytest.fixture
def extractor():
    """Create a ColorExtractor instance for testing."""
    return ColorExtractor()


@pytest.fixture
def sample_image():
    """Create a simple test image with known colors."""
    # Create 100x100 image with 4 quadrants of different colors
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)

    # Red quadrant
    img_array[0:50, 0:50] = [255, 0, 0]
    # Green quadrant
    img_array[0:50, 50:100] = [0, 255, 0]
    # Blue quadrant
    img_array[50:100, 0:50] = [0, 0, 255]
    # Yellow quadrant
    img_array[50:100, 50:100] = [255, 255, 0]

    return Image.fromarray(img_array)


@pytest.fixture
def sample_artwork_dict(sample_image):
    """Create a sample artwork dictionary."""
    return {
        "image": sample_image,
        "title": "Test Artwork",
        "artist": "Test Artist",
        "genre": "Test Genre",
        "style": "Test Style",
    }


def test_extractor_initialization(extractor):
    """Test that ColorExtractor initializes correctly."""
    assert extractor is not None
    assert isinstance(extractor.use_sklearn, bool)


def test_extract_dominant_colors_basic(extractor, sample_image):
    """Test basic color extraction."""
    colors = extractor.extract_dominant_colors(sample_image, n_colors=4)

    assert isinstance(colors, list)
    assert len(colors) == 4

    # Each color should be an RGB tuple
    for color in colors:
        assert isinstance(color, tuple)
        assert len(color) == 3
        for channel in color:
            assert 0 <= channel <= 255


def test_extract_dominant_colors_with_limit(extractor, sample_image):
    """Test color extraction with different n_colors values."""
    for n in [1, 3, 5, 10]:
        colors = extractor.extract_dominant_colors(sample_image, n_colors=n)
        assert len(colors) == n


def test_extract_dominant_colors_from_array(extractor):
    """Test that extraction works with numpy arrays."""
    img_array = np.random.randint(0, 256, (50, 50, 3), dtype=np.uint8)
    colors = extractor.extract_dominant_colors(img_array, n_colors=5)

    assert len(colors) == 5
    assert all(isinstance(c, tuple) for c in colors)


def test_extract_dominant_colors_rgba(extractor):
    """Test handling of RGBA images."""
    # Create RGBA image
    img_array = np.random.randint(0, 256, (50, 50, 4), dtype=np.uint8)
    colors = extractor.extract_dominant_colors(img_array, n_colors=5)

    assert len(colors) == 5
    # Should return RGB tuples, not RGBA
    for color in colors:
        assert len(color) == 3


def test_extract_dominant_colors_sample_size(extractor, sample_image):
    """Test that sample_size parameter works."""
    colors_sampled = extractor.extract_dominant_colors(
        sample_image, n_colors=3, sample_size=100
    )
    colors_full = extractor.extract_dominant_colors(
        sample_image, n_colors=3, sample_size=None
    )

    assert len(colors_sampled) == 3
    assert len(colors_full) == 3


def test_extract_palette_from_artwork(extractor, sample_artwork_dict):
    """Test extracting palette from artwork dictionary."""
    palette = extractor.extract_palette_from_artwork(sample_artwork_dict, n_colors=4)

    assert isinstance(palette, dict)
    assert "colors" in palette
    assert "artwork" in palette
    assert "artist" in palette
    assert "n_colors" in palette

    assert len(palette["colors"]) == 4
    assert palette["artwork"] == "Test Artwork"
    assert palette["artist"] == "Test Artist"


def test_extract_average_color(extractor, sample_image):
    """Test average color extraction."""
    avg_color = extractor.extract_average_color(sample_image)

    assert isinstance(avg_color, tuple)
    assert len(avg_color) == 3
    for channel in avg_color:
        assert 0 <= channel <= 255


def test_rgb_to_hex(extractor):
    """Test RGB to hex conversion."""
    assert extractor.rgb_to_hex((255, 0, 0)) == "#ff0000"
    assert extractor.rgb_to_hex((0, 255, 0)) == "#00ff00"
    assert extractor.rgb_to_hex((0, 0, 255)) == "#0000ff"
    assert extractor.rgb_to_hex((255, 255, 255)) == "#ffffff"
    assert extractor.rgb_to_hex((0, 0, 0)) == "#000000"
    assert extractor.rgb_to_hex((128, 128, 128)) == "#808080"


def test_hex_to_rgb(extractor):
    """Test hex to RGB conversion."""
    assert extractor.hex_to_rgb("#ff0000") == (255, 0, 0)
    assert extractor.hex_to_rgb("#00ff00") == (0, 255, 0)
    assert extractor.hex_to_rgb("#0000ff") == (0, 0, 255)
    assert extractor.hex_to_rgb("#ffffff") == (255, 255, 255)
    assert extractor.hex_to_rgb("#000000") == (0, 0, 0)

    # Test without '#'
    assert extractor.hex_to_rgb("ff0000") == (255, 0, 0)


def test_rgb_hex_roundtrip(extractor):
    """Test that RGB->hex->RGB conversion is accurate."""
    test_colors = [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (128, 64, 32),
        (200, 150, 100),
        (50, 100, 150),
    ]

    for color in test_colors:
        hex_color = extractor.rgb_to_hex(color)
        back_to_rgb = extractor.hex_to_rgb(hex_color)
        assert color == back_to_rgb


def test_palette_to_dict(extractor):
    """Test palette dictionary conversion."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
    palette_dict = extractor.palette_to_dict(colors, include_hex=True)

    assert "rgb_values" in palette_dict
    assert "hex_values" in palette_dict
    assert "n_colors" in palette_dict

    assert len(palette_dict["rgb_values"]) == 3
    assert len(palette_dict["hex_values"]) == 3
    assert palette_dict["n_colors"] == 3

    # Check hex values
    assert palette_dict["hex_values"][0] == "#ff0000"
    assert palette_dict["hex_values"][1] == "#00ff00"
    assert palette_dict["hex_values"][2] == "#0000ff"


def test_palette_to_dict_without_hex(extractor):
    """Test palette dictionary conversion without hex codes."""
    colors = [(255, 0, 0), (0, 255, 0)]
    palette_dict = extractor.palette_to_dict(colors, include_hex=False)

    assert "rgb_values" in palette_dict
    assert "hex_values" not in palette_dict
    assert "n_colors" in palette_dict


def test_export_palette_css(extractor):
    """Test CSS palette export."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".css", delete=False) as f:
        css_path = f.name

    try:
        extractor.export_palette_css(colors, css_path, prefix="test")

        # Read and verify the CSS file
        with open(css_path, "r") as f:
            content = f.read()

        assert ":root {" in content
        assert "--test-1: #ff0000;" in content
        assert "--test-2: #00ff00;" in content
        assert "--test-3: #0000ff;" in content

    finally:
        if os.path.exists(css_path):
            os.remove(css_path)


def test_export_palette_json(extractor):
    """Test JSON palette export."""
    colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]

    with tempfile.NamedTemporaryFile(mode="w", suffix=".json", delete=False) as f:
        json_path = f.name

    try:
        extractor.export_palette_json(colors, json_path)

        # Read and verify the JSON file
        with open(json_path, "r") as f:
            data = json.load(f)

        assert "rgb_values" in data
        assert "hex_values" in data
        assert "n_colors" in data

        assert data["n_colors"] == 3
        assert data["rgb_values"][0] == [255, 0, 0]
        assert data["hex_values"][0] == "#ff0000"

    finally:
        if os.path.exists(json_path):
            os.remove(json_path)


def test_numpy_type_handling(extractor):
    """Test that numpy types are correctly converted to Python types."""
    # Create colors with numpy types
    np_colors = [
        (np.uint8(255), np.uint8(0), np.uint8(0)),
        (np.uint8(0), np.uint8(255), np.uint8(0)),
    ]

    palette_dict = extractor.palette_to_dict(np_colors)

    # Check that values are Python ints, not numpy types
    for rgb in palette_dict["rgb_values"]:
        for val in rgb:
            assert isinstance(val, int)
            assert not isinstance(val, np.integer)


def test_extraction_methods_available():
    """Test that extraction method selection works."""
    extractor = ColorExtractor()

    # These should not raise errors regardless of sklearn availability
    test_img = np.random.randint(0, 256, (20, 20, 3), dtype=np.uint8)

    colors_kmeans = extractor.extract_dominant_colors(
        test_img, n_colors=3, method="kmeans"
    )
    colors_freq = extractor.extract_dominant_colors(
        test_img, n_colors=3, method="frequency"
    )

    assert len(colors_kmeans) == 3
    assert len(colors_freq) == 3


# ---------------------------------------------------------------------------
# Validator tests
# ---------------------------------------------------------------------------

def test_validate_export_filename_path_traversal():
    """Path-traversal filenames must be rejected."""
    from renoir.color.extraction import _validate_export_filename

    with pytest.raises(ValueError, match="path traversal"):
        _validate_export_filename("../evil.css")

    with pytest.raises(ValueError, match="path traversal"):
        _validate_export_filename("foo/../../etc/passwd")


def test_validate_export_filename_null_byte():
    """Null bytes in filenames must be rejected."""
    from renoir.color.extraction import _validate_export_filename

    with pytest.raises(ValueError, match="null bytes"):
        _validate_export_filename("palette\x00.css")


def test_validate_export_filename_valid_paths():
    """Normal filenames and absolute paths must be accepted."""
    from renoir.color.extraction import _validate_export_filename

    # Should not raise
    _validate_export_filename("palette.css")
    _validate_export_filename("output/palette.json")
    _validate_export_filename(os.path.join(tempfile.gettempdir(), "palette.css"))


# ---------------------------------------------------------------------------
# Input validation edge cases
# ---------------------------------------------------------------------------

def test_extract_dominant_colors_invalid_n_colors_type(extractor, sample_image):
    """Non-integer n_colors must raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(sample_image, n_colors=2.5)


def test_extract_dominant_colors_n_colors_zero(extractor, sample_image):
    """n_colors < 1 must raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(sample_image, n_colors=0)


def test_extract_dominant_colors_n_colors_too_large(extractor, sample_image):
    """n_colors > 256 must raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(sample_image, n_colors=257)


def test_extract_dominant_colors_invalid_sample_size_type(extractor, sample_image):
    """Non-integer sample_size must raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(sample_image, sample_size=1.5)


def test_extract_dominant_colors_sample_size_zero(extractor, sample_image):
    """sample_size < 1 must raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(sample_image, sample_size=0)


def test_extract_dominant_colors_invalid_method(extractor, sample_image):
    """Unknown method must raise ValueError."""
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(sample_image, method="unknown")


def test_extract_dominant_colors_invalid_image_type(extractor):
    """Non-image input must raise TypeError."""
    with pytest.raises(TypeError):
        extractor.extract_dominant_colors("not_an_image")


def test_extract_dominant_colors_wrong_channels(extractor):
    """Image with 2 channels must raise ValueError."""
    bad_img = np.zeros((10, 10, 2), dtype=np.uint8)
    with pytest.raises(ValueError):
        extractor.extract_dominant_colors(bad_img)


def test_extract_dominant_colors_grayscale(extractor):
    """2D (grayscale) numpy array must be handled gracefully."""
    gray = np.full((20, 20), 128, dtype=np.uint8)
    colors = extractor.extract_dominant_colors(gray, n_colors=1)
    assert len(colors) == 1


def test_extract_dominant_colors_all_black(extractor):
    """All-black image triggers the 'no valid pixels' warning path."""
    black = np.zeros((10, 10, 3), dtype=np.uint8)
    colors = extractor.extract_dominant_colors(black, n_colors=3)
    # Should return fallback colors, not raise
    assert len(colors) == 3


def test_extract_dominant_colors_fewer_pixels_than_n_colors(extractor):
    """Image with fewer unique pixels than n_colors triggers warning and clamps."""
    tiny = np.array([[[100, 150, 200]]], dtype=np.uint8)  # 1 pixel
    colors = extractor.extract_dominant_colors(tiny, n_colors=5, filter_extremes=False)
    assert len(colors) >= 1


def test_extract_dominant_colors_filter_extremes_false(extractor):
    """filter_extremes=False keeps pure black/white pixels."""
    img = np.zeros((10, 10, 3), dtype=np.uint8)
    img[0:5, :] = 255  # half white
    colors = extractor.extract_dominant_colors(img, n_colors=2, filter_extremes=False)
    assert len(colors) == 2


# ---------------------------------------------------------------------------
# check_color_extraction_support helper
# ---------------------------------------------------------------------------

def test_check_color_extraction_support():
    """check_color_extraction_support must return a bool."""
    from renoir.color.extraction import check_color_extraction_support
    result = check_color_extraction_support()
    assert isinstance(result, bool)
