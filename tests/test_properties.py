"""
Property-based tests for color invariants, using Hypothesis.

Rather than checking hand-picked examples, these tests assert invariants
that must hold for every input: round-trip stability, metric axioms, and
bounded composite scores. ``derandomize=True`` keeps CI runs
deterministic; Hypothesis still reports minimal counter-examples on
failure.
"""

import numpy as np
import pytest
from hypothesis import given, settings, strategies as st
from PIL import Image

from renoir.color import ColorAnalyzer
from renoir.color._colorimetry import (
    WCAG_AA_NORMAL,
    delta_e2000,
    hex_to_rgb,
    rgb_to_hex,
    srgb_to_lab_tuple,
    wcag_contrast,
)
from renoir.color.dsp import select_palette

rgb_tuples = st.tuples(st.integers(0, 255), st.integers(0, 255), st.integers(0, 255))

proportioned_palettes = st.lists(rgb_tuples, min_size=2, max_size=5).map(
    lambda cs: [(c, 1.0 / len(cs)) for c in cs]
)


@given(rgb_tuples)
@settings(max_examples=100, derandomize=True)
def test_hex_rgb_roundtrip(rgb):
    """RGB -> hex -> RGB is an identity on valid RGB tuples."""
    assert hex_to_rgb(rgb_to_hex(rgb)) == tuple(rgb)


@given(rgb_tuples)
@settings(max_examples=100, derandomize=True)
def test_lab_bounds(rgb):
    """CIELAB L* stays in [0, 100] and all channels stay finite.

    The 1e-3 tolerance absorbs floating-point rounding in the matrix
    constants: the pure-NumPy fallback yields 100.0000039 for white,
    while the colour-science path yields exactly 100.
    """
    L, a, b = srgb_to_lab_tuple(rgb)
    assert 0.0 - 1e-3 <= L <= 100.0 + 1e-3
    assert all(np.isfinite(v) for v in (L, a, b))


@given(rgb_tuples, rgb_tuples)
@settings(max_examples=100, derandomize=True)
def test_delta_e2000_metric_axioms(a, b):
    """Delta-E is nonnegative, symmetric, and zero for identical colors."""
    lab_a = srgb_to_lab_tuple(a)
    lab_b = srgb_to_lab_tuple(b)
    assert delta_e2000(lab_a, lab_b) >= 0.0
    assert delta_e2000(lab_a, lab_b) == pytest.approx(delta_e2000(lab_b, lab_a))
    assert delta_e2000(lab_a, lab_a) == pytest.approx(0.0, abs=1e-9)


@given(st.lists(rgb_tuples, min_size=2, max_size=6))
@settings(max_examples=25, derandomize=True)
def test_cci_in_unit_interval(colors):
    """CCI is bounded in [0, 1] for every palette."""
    analyzer = ColorAnalyzer()
    result = analyzer.calculate_color_complexity(colors)
    assert 0.0 <= result["cci"] <= 1.0


@given(proportioned_palettes)
@settings(max_examples=25, derandomize=True)
def test_pemd_self_distance_is_zero(palette):
    """PEMD of any palette against itself is zero."""
    analyzer = ColorAnalyzer()
    dist = analyzer.palette_earth_movers_distance(palette, palette)
    assert dist == pytest.approx(0.0, abs=1e-9)


# ---------------------------------------------------------------------------
# DSP WCAG AA guarantee
# ---------------------------------------------------------------------------


def _has_aa_pair(colors) -> bool:
    """True when at least one palette pair meets WCAG AA contrast."""
    for i in range(len(colors)):
        for j in range(i + 1, len(colors)):
            if wcag_contrast(colors[i], colors[j]) >= WCAG_AA_NORMAL:
                return True
    return False


@given(rgb_tuples)
@settings(max_examples=25, derandomize=True, deadline=None)
def test_dsp_wcag_guarantee_solid_images(rgb):
    """Single-colour images yield an honest single-colour palette.

    A solid image has one colour, so no contrast pair exists and none
    should be invented: DSP reports wcag_guaranteed=False and warns,
    rather than fabricating a colour that is not in the image.
    """
    img = Image.new("RGB", (16, 16), tuple(rgb))
    with pytest.warns(UserWarning, match="could not be satisfied"):
        result = select_palette(img, n=5)
    assert result.n == 1
    assert result.wcag_guaranteed is False


@given(st.integers(0, 10**6))
@settings(max_examples=20, derandomize=True, deadline=None)
def test_dsp_wcag_guarantee_noise_images(seed):
    """Random-noise images yield palettes with a WCAG AA pair."""
    rng = np.random.RandomState(seed)
    arr = rng.randint(0, 256, size=(16, 16, 3)).astype(np.uint8)
    img = Image.fromarray(arr)
    result = select_palette(img, n=5)
    colors = result.to_rgb_tuples()
    assert result.wcag_guaranteed is True
    assert _has_aa_pair(colors)
    assert len(colors) == 5
