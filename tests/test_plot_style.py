"""Regression tests for the shared modular-grid plotting style."""

import pytest

matplotlib = pytest.importorskip("matplotlib")
matplotlib.use("Agg")

from renoir.color._plot_style import (
    ACCENT,
    DEFAULT_FIGSIZE,
    FONT,
    add_panel,
    create_figure,
    grid_cell,
    style_axis,
)


def test_panel_uses_modular_grid_and_close_heading():
    fig = create_figure("Report", figsize=DEFAULT_FIGSIZE)
    ax = add_panel(fig, 0, 1.45, 5, 2.25, "Data panel")

    assert list(ax.get_position().bounds) == pytest.approx(grid_cell(0, 1.75, 5, 2.25))
    assert {text.get_text() for text in fig.texts} == {"Report", "Data panel"}


def test_axis_style_uses_functional_black_and_white_rules():
    fig = create_figure("Report")
    ax = add_panel(fig, 0, 1.45, 5, 2.25)
    style_axis(ax, "Horizontal", "Vertical")

    assert ax.get_xlabel() == "Horizontal"
    assert ax.get_ylabel() == "Vertical"
    assert ax.xaxis.get_gridlines()[0].get_alpha() == 0.14
    assert not ax.spines["top"].get_visible()
    assert not ax.spines["right"].get_visible()
    assert ax.spines["left"].get_edgecolor()[:3] == (17 / 255, 17 / 255, 17 / 255)


def test_axis_style_honors_grid_direction():
    fig = create_figure("Report")
    ax = add_panel(fig, 0, 1.45, 5, 2.25)
    style_axis(ax, grid="y")

    assert not ax.xaxis.get_gridlines()[0].get_visible()
    assert ax.yaxis.get_gridlines()[0].get_visible()


def test_accent_is_single_functional_blue():
    assert ACCENT == "#0057B8"


def test_create_figure_preserves_rcparams(monkeypatch):
    import matplotlib.pyplot as plt

    monkeypatch.setitem(plt.rcParams, "font.family", ["serif"])
    fig = create_figure("Report")

    assert plt.rcParams["font.family"] == ["serif"]
    assert fig.texts[0].get_fontfamily() == [FONT]


def test_cross_vocabulary_labels_have_a_reserved_grid_column():
    from renoir.color import ColorVisualizer

    fig = ColorVisualizer().plot_cross_vocabulary_naming([(28, 62, 145)], show=False)

    assert fig.axes[0].get_position().x0 == pytest.approx((0.5 + 2.25) / 13)
    assert "Werner's Nomenclature" in {text.get_text() for text in fig.texts}


def test_pemd_value_has_a_reserved_grid_column():
    from renoir.color import ColorVisualizer

    pair = (
        [((28, 62, 145), 1.0)],
        [((214, 178, 94), 1.0)],
    )
    fig = ColorVisualizer().plot_pemd_comparison(
        [pair], pemd_values=[39.53], show=False
    )

    assert max(axis.get_position().x1 for axis in fig.axes) == pytest.approx(10.5 / 13)
    assert "PEMD\n39.53" in {text.get_text() for text in fig.texts}
