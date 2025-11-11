"""
Tests for the color visualization module.

These tests verify that visualization methods run without errors.
Visual output cannot be automatically tested.
"""

import pytest
import numpy as np
import tempfile
import os

# Try importing visualization dependencies
try:
    import matplotlib

    matplotlib.use("Agg")  # Use non-interactive backend for testing
    import matplotlib.pyplot as plt
    from renoir.color import ColorVisualizer

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


pytestmark = pytest.mark.skipif(
    not VISUALIZATION_AVAILABLE, reason="Visualization libraries not installed"
)


@pytest.fixture
def visualizer():
    """Create a ColorVisualizer instance for testing."""
    return ColorVisualizer()


@pytest.fixture
def sample_colors():
    """Create a sample color palette for testing."""
    return [
        (255, 0, 0),  # Red
        (0, 255, 0),  # Green
        (0, 0, 255),  # Blue
        (255, 255, 0),  # Yellow
        (255, 0, 255),  # Magenta
    ]


@pytest.fixture
def cleanup_plots():
    """Cleanup fixture to close all plots after each test."""
    yield
    plt.close("all")


def test_visualizer_initialization(visualizer):
    """Test that ColorVisualizer initializes correctly."""
    assert visualizer is not None


def test_plot_palette(visualizer, sample_colors, cleanup_plots):
    """Test palette plotting."""
    # Should not raise an error
    visualizer.plot_palette(
        sample_colors, title="Test Palette", save_path=None, show_hex=True
    )
    plt.close()


def test_plot_palette_save(visualizer, sample_colors, cleanup_plots):
    """Test palette plotting with save."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        save_path = f.name

    try:
        visualizer.plot_palette(
            sample_colors, title="Test Palette", save_path=save_path
        )

        # Check that file was created
        assert os.path.exists(save_path)
        assert os.path.getsize(save_path) > 0

    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
        plt.close()


def test_plot_palette_no_hex(visualizer, sample_colors, cleanup_plots):
    """Test palette plotting without hex codes."""
    visualizer.plot_palette(sample_colors, show_hex=False)
    plt.close()


def test_plot_color_wheel(visualizer, sample_colors, cleanup_plots):
    """Test color wheel plotting."""
    # Should not raise an error
    visualizer.plot_color_wheel(sample_colors)
    plt.close()


def test_plot_rgb_distribution(visualizer, sample_colors, cleanup_plots):
    """Test RGB distribution plotting."""
    visualizer.plot_rgb_distribution(sample_colors)
    plt.close()


def test_plot_hsv_distribution(visualizer, sample_colors, cleanup_plots):
    """Test HSV distribution plotting."""
    visualizer.plot_hsv_distribution(sample_colors)
    plt.close()


def test_plot_3d_rgb_space(visualizer, sample_colors, cleanup_plots):
    """Test 3D RGB space plotting."""
    visualizer.plot_3d_rgb_space(sample_colors)
    plt.close()


def test_compare_palettes(visualizer, sample_colors, cleanup_plots):
    """Test palette comparison visualization."""
    colors1 = sample_colors[:3]
    colors2 = sample_colors[2:5]

    visualizer.compare_palettes(colors1, colors2, labels=("Palette 1", "Palette 2"))
    plt.close()


def test_create_artist_color_report(visualizer, sample_colors, cleanup_plots):
    """Test comprehensive color report."""
    visualizer.create_artist_color_report(sample_colors, artist_name="Test Artist")
    plt.close()


def test_plot_palette_empty_list(visualizer, cleanup_plots):
    """Test palette plotting with empty list."""
    # Should handle gracefully
    try:
        visualizer.plot_palette([])
        plt.close()
    except Exception as e:
        # Should either work or raise a clear error
        assert "color" in str(e).lower() or "empty" in str(e).lower()
        plt.close()


def test_plot_palette_single_color(visualizer, cleanup_plots):
    """Test palette plotting with single color."""
    visualizer.plot_palette([(255, 0, 0)])
    plt.close()


def test_plot_color_wheel_save(visualizer, sample_colors, cleanup_plots):
    """Test color wheel with save."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        save_path = f.name

    try:
        visualizer.plot_color_wheel(sample_colors, save_path=save_path)
        assert os.path.exists(save_path)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
        plt.close()


def test_rgb_distribution_save(visualizer, sample_colors, cleanup_plots):
    """Test RGB distribution with save."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        save_path = f.name

    try:
        visualizer.plot_rgb_distribution(sample_colors, save_path=save_path)
        assert os.path.exists(save_path)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
        plt.close()


def test_compare_palettes_save(visualizer, sample_colors, cleanup_plots):
    """Test palette comparison with save."""
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as f:
        save_path = f.name

    try:
        visualizer.compare_palettes(
            sample_colors[:3], sample_colors[2:5], save_path=save_path
        )
        assert os.path.exists(save_path)
    finally:
        if os.path.exists(save_path):
            os.remove(save_path)
        plt.close()


def test_visualization_methods_exist(visualizer):
    """Test that all expected methods exist."""
    methods = [
        "plot_palette",
        "plot_color_wheel",
        "plot_rgb_distribution",
        "plot_hsv_distribution",
        "plot_3d_rgb_space",
        "compare_palettes",
        "create_artist_color_report",
    ]

    for method in methods:
        assert hasattr(visualizer, method)
        assert callable(getattr(visualizer, method))


def test_custom_figsize(visualizer, sample_colors, cleanup_plots):
    """Test custom figure sizes."""
    visualizer.plot_palette(sample_colors, figsize=(16, 3))
    plt.close()

    visualizer.plot_rgb_distribution(sample_colors, figsize=(10, 8))
    plt.close()


def test_many_colors(visualizer, cleanup_plots):
    """Test visualization with many colors."""
    # Create palette with 20 colors
    many_colors = [(int(i * 255 / 20), 100, 100) for i in range(20)]

    visualizer.plot_palette(many_colors)
    plt.close()

    visualizer.plot_color_wheel(many_colors)
    plt.close()
