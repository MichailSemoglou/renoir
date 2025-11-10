"""
Color analysis module for renoir.

This module provides comprehensive color analysis tools for art and design education,
including color extraction, multi-space analysis, and visualization capabilities.

Classes:
    ColorExtractor: Extract dominant colors from artwork images
    ColorAnalyzer: Analyze colors across different color spaces
    ColorVisualizer: Create publication-quality color visualizations
"""

from .extraction import ColorExtractor
from .analysis import ColorAnalyzer
from .visualization import ColorVisualizer

__all__ = [
    "ColorExtractor",
    "ColorAnalyzer",
    "ColorVisualizer"
]
