"""
Tests for the CAM16-UCS delta-E backend (Li et al., 2017).

These tests require the optional colour-science dependency and are
skipped when it is not installed (``pip install 'renoir-wikiart[cam16]'``).
"""

import pytest

colour = pytest.importorskip("colour", reason="colour-science not installed")

from renoir.color import ColorAnalyzer  # noqa: E402
from renoir.color._colorimetry import (  # noqa: E402
    cam16ucs_distance,
    srgb_to_cam16ucs_tuple,
)

PALETTE_A = [((255, 87, 51), 0.6), ((0, 49, 83), 0.4)]
PALETTE_B = [((240, 90, 55), 0.5), ((10, 55, 90), 0.5)]
COLORS = [(255, 87, 51), (0, 49, 83), (34, 139, 34), (255, 215, 0)]


@pytest.fixture
def analyzer():
    """Create a ColorAnalyzer instance for testing."""
    return ColorAnalyzer()


def test_cam16_black_and_white():
    """Black maps to the CAM16-UCS origin, white to J' of about 100."""
    black = srgb_to_cam16ucs_tuple((0, 0, 0))
    white = srgb_to_cam16ucs_tuple((255, 255, 255))
    assert black == pytest.approx((0.0, 0.0, 0.0), abs=1e-3)
    assert white[0] == pytest.approx(100.0, abs=1.0)
    assert white[1] == pytest.approx(0.0, abs=1e-2)
    assert white[2] == pytest.approx(0.0, abs=1e-2)


def test_cam16_neutral_gray_is_achromatic():
    """A neutral gray has near-zero a'/b' and a mid-range J'."""
    Jp, ap, bp = srgb_to_cam16ucs_tuple((128, 128, 128))
    assert ap == pytest.approx(0.0, abs=1e-2)
    assert bp == pytest.approx(0.0, abs=1e-2)
    assert 30.0 < Jp < 70.0


def test_cam16_distance_properties():
    """CAM16-UCS distance is zero for identical colours and symmetric."""
    a = srgb_to_cam16ucs_tuple((255, 87, 51))
    b = srgb_to_cam16ucs_tuple((0, 49, 83))
    assert cam16ucs_distance(a, a) == pytest.approx(0.0, abs=1e-12)
    assert cam16ucs_distance(a, b) == pytest.approx(cam16ucs_distance(b, a))
    black = srgb_to_cam16ucs_tuple((0, 0, 0))
    white = srgb_to_cam16ucs_tuple((255, 255, 255))
    assert cam16ucs_distance(black, white) == pytest.approx(100.0, abs=1.0)


def test_cam16_viewing_condition_parameters():
    """The surround parameter changes the computed appearance."""
    default = srgb_to_cam16ucs_tuple((200, 120, 60))
    dark = srgb_to_cam16ucs_tuple((200, 120, 60), surround="Dark")
    assert default != pytest.approx(dark, abs=1e-6)


def test_pemd_cam16(analyzer):
    """PEMD accepts the cam16 backend and returns sensible values."""
    self_dist = analyzer.palette_earth_movers_distance(
        PALETTE_A, PALETTE_A, distance_metric="cam16"
    )
    assert self_dist == pytest.approx(0.0, abs=1e-9)
    dist = analyzer.palette_earth_movers_distance(
        PALETTE_A, PALETTE_B, distance_metric="cam16"
    )
    assert dist > 0.0


def test_cci_cam16_bounds(analyzer):
    """CCI and its spread component stay in [0, 1] under CAM16-UCS."""
    result = analyzer.calculate_color_complexity(COLORS, distance_metric="cam16")
    assert 0.0 <= result["cci"] <= 1.0
    assert 0.0 <= result["perceptual_spread"] <= 1.0
