"""
Tests for the shared colorimetry primitives and delta-E strategies.

These tests verify the Oklab transform (Ottosson, 2020), the delta-E
strategy registry, and the distance_metric parameter on PEMD and CCI.
"""

import numpy as np
import pytest

from renoir.color import ColorAnalyzer
from renoir.color._colorimetry import (
    delta_e2000,
    get_delta_e_strategy,
    oklab_distance,
    srgb_to_lab_tuple,
    srgb_to_oklab,
    srgb_to_oklab_tuple,
)

# Oklab reference values from Ottosson (2020),
# https://bottosson.github.io/posts/oklab/
OKLAB_RED = (0.6279554, 0.2248631, 0.1258463)

PALETTE_A = [((255, 87, 51), 0.6), ((0, 49, 83), 0.4)]
PALETTE_B = [((240, 90, 55), 0.5), ((10, 55, 90), 0.5)]
COLORS = [(255, 87, 51), (0, 49, 83), (34, 139, 34), (255, 215, 0)]


@pytest.fixture
def analyzer():
    """Create a ColorAnalyzer instance for testing."""
    return ColorAnalyzer()


def test_oklab_black():
    """Black maps to the Oklab origin."""
    lab = srgb_to_oklab_tuple((0, 0, 0))
    assert lab == pytest.approx((0.0, 0.0, 0.0), abs=1e-6)


def test_oklab_white():
    """White maps to L=1 with zero chroma."""
    lab = srgb_to_oklab_tuple((255, 255, 255))
    assert lab == pytest.approx((1.0, 0.0, 0.0), abs=1e-3)


def test_oklab_neutral_gray_is_achromatic():
    """A neutral gray has zero a/b and a mid-range L."""
    L, a, b = srgb_to_oklab_tuple((128, 128, 128))
    assert a == pytest.approx(0.0, abs=1e-3)
    assert b == pytest.approx(0.0, abs=1e-3)
    assert 0.55 < L < 0.65


def test_oklab_red_reference():
    """Pure red matches the published Oklab reference values."""
    lab = srgb_to_oklab_tuple((255, 0, 0))
    assert lab == pytest.approx(OKLAB_RED, abs=1e-3)


def test_oklab_batch_shape_and_dtype():
    """Array input returns an (n, 3) float64 array."""
    arr = srgb_to_oklab(np.array([[255, 0, 0], [0, 255, 0]], dtype=np.uint8))
    assert arr.shape == (2, 3)
    assert arr.dtype == np.float64


def test_oklab_accepts_float_input():
    """Float 0-1 input matches uint8 input for the same colour."""
    as_int = srgb_to_oklab(np.array([[255, 87, 51]], dtype=np.uint8))
    as_float = srgb_to_oklab(np.array([[1.0, 87 / 255, 51 / 255]]))
    np.testing.assert_allclose(as_float, as_int, atol=1e-12)


def test_oklab_distance_identity():
    """Distance from a colour to itself is zero."""
    lab = srgb_to_oklab_tuple((123, 45, 67))
    assert oklab_distance(lab, lab) == pytest.approx(0.0, abs=1e-12)


def test_oklab_distance_symmetry():
    """Distance is symmetric in its arguments."""
    a = srgb_to_oklab_tuple((255, 87, 51))
    b = srgb_to_oklab_tuple((0, 49, 83))
    assert oklab_distance(a, b) == pytest.approx(oklab_distance(b, a))


def test_oklab_distance_black_white_is_one():
    """Black to white measures one, anchoring the normalization cap."""
    black = srgb_to_oklab_tuple((0, 0, 0))
    white = srgb_to_oklab_tuple((255, 255, 255))
    assert oklab_distance(black, white) == pytest.approx(1.0, abs=1e-3)


def test_strategy_registry_contains_defaults():
    """Both documented strategies are registered with their caps."""
    assert get_delta_e_strategy("cie2000").normalization_cap == 100.0
    assert get_delta_e_strategy("oklab").normalization_cap == 1.0


def test_strategy_unknown_name_raises():
    """An unknown strategy name raises ValueError."""
    with pytest.raises(ValueError, match="Unknown distance metric"):
        get_delta_e_strategy("lab76")


def test_cie2000_strategy_matches_legacy_functions():
    """The cie2000 strategy reproduces the pre-existing numerics."""
    strategy = get_delta_e_strategy("cie2000")
    rgb = (255, 87, 51)
    assert strategy.to_space(rgb) == pytest.approx(srgb_to_lab_tuple(rgb))
    lab1, lab2 = srgb_to_lab_tuple(rgb), srgb_to_lab_tuple((0, 49, 83))
    assert strategy.distance(lab1, lab2) == pytest.approx(delta_e2000(lab1, lab2))


def test_pemd_default_matches_cie2000(analyzer):
    """Omitting distance_metric is identical to explicit cie2000."""
    default = analyzer.palette_earth_movers_distance(PALETTE_A, PALETTE_B)
    explicit = analyzer.palette_earth_movers_distance(
        PALETTE_A, PALETTE_B, distance_metric="cie2000"
    )
    assert default == explicit


def test_pemd_oklab_self_distance_is_zero(analyzer):
    """PEMD of a palette against itself is zero under Oklab."""
    dist = analyzer.palette_earth_movers_distance(
        PALETTE_A, PALETTE_A, distance_metric="oklab"
    )
    assert dist == pytest.approx(0.0, abs=1e-9)


def test_pemd_oklab_positive_for_distinct_palettes(analyzer):
    """Distinct palettes have a positive Oklab PEMD."""
    dist = analyzer.palette_earth_movers_distance(
        PALETTE_A, PALETTE_B, distance_metric="oklab"
    )
    assert dist > 0.0


def test_pemd_invalid_metric_raises(analyzer):
    """An unknown distance_metric raises ValueError in PEMD."""
    with pytest.raises(ValueError, match="Unknown distance metric"):
        analyzer.palette_earth_movers_distance(
            PALETTE_A, PALETTE_B, distance_metric="lab76"
        )


def test_cci_default_matches_cie2000(analyzer):
    """Omitting distance_metric is identical to explicit cie2000."""
    default = analyzer.calculate_color_complexity(COLORS)
    explicit = analyzer.calculate_color_complexity(COLORS, distance_metric="cie2000")
    assert default == explicit


def test_cci_oklab_bounds(analyzer):
    """CCI and its spread component stay in [0, 1] under Oklab."""
    result = analyzer.calculate_color_complexity(COLORS, distance_metric="oklab")
    assert 0.0 <= result["cci"] <= 1.0
    assert 0.0 <= result["perceptual_spread"] <= 1.0


def test_cci_oklab_spread_uses_metric_cap(analyzer):
    """Oklab spread is normalised by its own cap, not the CIEDE2000 cap.

    With the wrong cap (100) a diverse palette would flatten to ~0.003;
    with the correct cap (1.0) it stays on the same 0-1 scale as cie2000.
    """
    result = analyzer.calculate_color_complexity(COLORS, distance_metric="oklab")
    assert result["perceptual_spread"] > 0.1


def test_cci_invalid_metric_raises(analyzer):
    """An unknown distance_metric raises ValueError in CCI."""
    with pytest.raises(ValueError, match="Unknown distance metric"):
        analyzer.calculate_color_complexity(COLORS, distance_metric="lab76")
