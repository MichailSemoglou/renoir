"""Shared modular-grid typography and layout for color visualizations."""

from typing import Optional, Tuple

import matplotlib.pyplot as plt
from matplotlib.lines import Line2D

ACCENT = "#0057B8"
BLACK = "#111111"
SECONDARY = "#666666"
FONT = "DejaVu Sans"
DEFAULT_FIGSIZE = (16, 10.6666666667)
SERIES_COLORS = [ACCENT, "#333333", "#777777", "#BBBBBB", "#000000"]


def grid_cell(column: float, row: float, width: float, height: float):
    """Return an axes rectangle on the 12-column, 8-row content grid."""
    return [
        (0.5 + column) / 13,
        1 - (0.5 + row + height) / 9,
        width / 13,
        height / 9,
    ]


def grid_point(column: float, row: float):
    """Return a text anchor on the 12-column, 8-row content grid."""
    return (0.5 + column) / 13, 1 - (0.5 + row) / 9


def add_heading(fig, column: float, row: float, text: str, size: int = 12) -> None:
    """Place a heading at a modular grid anchor."""
    x, y = grid_point(column, row)
    fig.text(
        x,
        y,
        text,
        fontsize=size,
        fontfamily=FONT,
        fontweight="bold",
        color=BLACK,
        ha="left",
        va="baseline",
    )


def create_figure(title: str, figsize: Tuple[float, float] = DEFAULT_FIGSIZE):
    """Create a figure with a grid-aligned title and baseline rule."""
    fig = plt.figure(figsize=figsize)
    fig.patch.set_facecolor("white")
    add_heading(fig, 0, 0.25, title, size=20)
    start = grid_point(0, 0.75)
    end = grid_point(12, 0.75)
    fig.add_artist(
        Line2D(
            [start[0], end[0]],
            [start[1], end[1]],
            transform=fig.transFigure,
            color=BLACK,
            linewidth=0.8,
        )
    )
    return fig


def add_panel(
    fig,
    column: float,
    row: float,
    width: float,
    height: float,
    title: Optional[str] = None,
    projection: Optional[str] = None,
    heading_offset: float = 0.3,
):
    """Add an axes panel with its heading above the data."""
    if title:
        add_heading(fig, column, row, title)
    if projection is None:
        return fig.add_axes(grid_cell(column, row + heading_offset, width, height))
    return fig.add_axes(
        grid_cell(column, row + heading_offset, width, height), projection=projection
    )


def style_axis(
    axis, xlabel: Optional[str] = None, ylabel: Optional[str] = None, grid: str = "both"
) -> None:
    """Apply the shared black-and-white axis, label, and grid treatment."""
    if xlabel is not None:
        axis.set_xlabel(xlabel, fontsize=9, fontfamily=FONT, color=BLACK, labelpad=5)
    if ylabel is not None:
        axis.set_ylabel(ylabel, fontsize=9, fontfamily=FONT, color=BLACK, labelpad=5)
    axis.grid(grid, color=BLACK, alpha=0.14, linewidth=0.6)
    axis.set_axisbelow(True)
    axis.spines["top"].set_visible(False)
    axis.spines["right"].set_visible(False)
    axis.spines["left"].set_color(BLACK)
    axis.spines["bottom"].set_color(BLACK)
    axis.spines["left"].set_linewidth(0.7)
    axis.spines["bottom"].set_linewidth(0.7)
    axis.tick_params(colors=BLACK, labelsize=9, length=3, pad=3)
    for label in [*axis.get_xticklabels(), *axis.get_yticklabels()]:
        label.set_fontfamily(FONT)
