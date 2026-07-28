"""
Shared test utilities for the renoir test suite.
"""

from PIL import Image


def make_solid_image(rgb, size=(20, 20)):
    """Create a solid-color PIL Image for testing."""
    return Image.new("RGB", size, rgb)
