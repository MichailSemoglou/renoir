"""
renoir: A pedagogical tool for analyzing artist-specific works from WikiArt.

This package provides simple functions for extracting and analyzing works by
specific artists from the WikiArt dataset, designed for teaching computational
design and digital humanities courses.

Version 3.0.0 adds comprehensive color analysis capabilities for teaching
computational color theory to art and design students.
"""

__version__ = "3.0.2"
__author__ = "Michail Semoglou"

from .analyzer import ArtistAnalyzer, quick_analysis

# Color analysis module (new in v3.0.0)
from .color import ColorExtractor, ColorAnalyzer, ColorVisualizer

__all__ = [
    "ArtistAnalyzer",
    "quick_analysis",
    "ColorExtractor",
    "ColorAnalyzer",
    "ColorVisualizer",
]

# Make visualization capabilities easily discoverable
try:
    import matplotlib.pyplot as plt
    import seaborn as sns

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


def check_visualization_support():
    """
    Check if visualization libraries are available.

    Returns:
        bool: True if visualization libraries are installed
    """
    if VISUALIZATION_AVAILABLE:
        print("✅ Visualization support is available!")
        print(
            "You can use plotting methods and set show_plots=True in quick_analysis()"
        )
    else:
        print("❌ Visualization libraries not installed.")
        print("Install with: pip install 'renoir-wikiart[visualization]'")
    return VISUALIZATION_AVAILABLE
