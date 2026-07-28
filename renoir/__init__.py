"""
renoir: A pedagogical tool for analyzing artist-specific works from WikiArt.

This package provides simple functions for extracting and analyzing works by
specific artists from the WikiArt dataset, designed for teaching computational
design and digital humanities courses.

Version 3.7.0 hardens input validation, fixes crashes on dateless datasets,
eliminated duplicated logic across the codebase, and raises test coverage to 90%.
"""

import logging

__version__ = "3.7.0"
__author__ = "Michail Semoglou"

logger = logging.getLogger(__name__)

from .analyzer import ArtistAnalyzer, quick_analysis

# Color analysis module (new in v3.0.0)
from .color import (
    ColorExtractor,
    ColorAnalyzer,
    ColorVisualizer,
    ColorNamer,
    PromptGenerator,
)

__all__ = [
    "ArtistAnalyzer",
    "quick_analysis",
    "ColorExtractor",
    "ColorAnalyzer",
    "ColorVisualizer",
    "ColorNamer",
    "PromptGenerator",
]

# Make visualization capabilities easily discoverable
try:
    import matplotlib  # noqa: F401
    import seaborn  # noqa: F401

    VISUALIZATION_AVAILABLE = True
except ImportError:
    VISUALIZATION_AVAILABLE = False


def check_visualization_support():
    """
    Check if visualization libraries are available.

    Convenience wrapper that checks the module-level ``VISUALIZATION_AVAILABLE``
    flag. For a more detailed check including seaborn availability, use
    :func:`renoir.color.visualization.check_visualization_support`.

    Returns:
        bool: True if visualization libraries are installed
    """
    if VISUALIZATION_AVAILABLE:
        try:
            from .color.visualization import (
                check_visualization_support as _detailed_check,
            )

            return _detailed_check()
        except ImportError:
            logger.info("Visualization support is available")
            logger.info(
                "You can use plotting methods and set show_plots=True in quick_analysis()"
            )
    else:
        logger.warning("Visualization libraries not installed.")
        logger.warning("Install with: pip install 'renoir-wikiart[visualization]'")
    return VISUALIZATION_AVAILABLE
