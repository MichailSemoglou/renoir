"""
Shared pytest fixtures for the renoir test suite.
"""

import os

import pytest
import numpy as np
from PIL import Image

from renoir import ArtistAnalyzer
from renoir.color import ColorAnalyzer, ColorExtractor, ColorNamer, ColorVisualizer


def pytest_collection_modifyitems(config, items):
    """Skip integration tests unless RUN_INTEGRATION=1 or -m integration is set."""
    if os.environ.get("RUN_INTEGRATION") == "1":
        return
    markexpr = getattr(config.option, "markexpr", "")
    if "integration" in markexpr:
        return
    skip_marker = pytest.mark.skip(
        reason="set RUN_INTEGRATION=1 to run integration tests"
    )
    for item in items:
        if "integration" in item.keywords:
            item.add_marker(skip_marker)


@pytest.fixture
def artist_analyzer():
    """Return a fresh ArtistAnalyzer instance."""
    return ArtistAnalyzer()


@pytest.fixture
def color_analyzer():
    """Return a fresh ColorAnalyzer instance."""
    return ColorAnalyzer()


@pytest.fixture
def color_extractor():
    """Return a fresh ColorExtractor instance."""
    return ColorExtractor()


@pytest.fixture
def color_namer():
    """Return a fresh ColorNamer with the default artist vocabulary."""
    return ColorNamer(vocabulary="artist")


@pytest.fixture
def color_visualizer():
    """Return a fresh ColorVisualizer instance."""
    return ColorVisualizer()


@pytest.fixture
def sample_colors():
    """A diverse five-color palette used across multiple test modules."""
    return [
        (255, 0, 0),
        (0, 255, 0),
        (0, 0, 255),
        (255, 255, 0),
        (255, 0, 255),
    ]


@pytest.fixture
def sample_image():
    """A 100x100 image with four solid-color quadrants."""
    img_array = np.zeros((100, 100, 3), dtype=np.uint8)
    img_array[0:50, 0:50] = [255, 0, 0]
    img_array[0:50, 50:100] = [0, 255, 0]
    img_array[50:100, 0:50] = [0, 0, 255]
    img_array[50:100, 50:100] = [255, 255, 0]
    return Image.fromarray(img_array)


@pytest.fixture
def mock_works():
    """A small collection of mock artwork dictionaries with dates."""
    return [
        {
            "artist": "claude-monet",
            "genre": "landscape",
            "style": "Impressionism",
            "date": 1872,
        },
        {
            "artist": "claude-monet",
            "genre": "landscape",
            "style": "Impressionism",
            "date": 1880,
        },
        {
            "artist": "claude-monet",
            "genre": "portrait",
            "style": "Impressionism",
            "date": 1875,
        },
        {
            "artist": "claude-monet",
            "genre": "landscape",
            "style": "Realism",
            "date": "1868",
        },
        {
            "artist": "claude-monet",
            "genre": "cityscape",
            "style": "Impressionism",
            "date": 1899,
        },
    ]
