"""
Tests for the pure-NumPy fallback paths in the colorimetry module.

The module accelerates sRGB->Lab and CIEDE2000 through the optional
colour-science dependency when it is installed. These tests force the
fallback branch with monkeypatching so both paths are exercised in every
environment, and pin the fallback to canonical reference values.
"""

import numpy as np
import pytest

from renoir.color import _colorimetry
from renoir.color._colorimetry import (
    delta_e2000,
    delta_e2000_batch,
    srgb_to_lab,
    srgb_to_lab_tuple,
)

# First pair from Table 1 of Sharma, Wu & Dalal (2005): the canonical
# CIEDE2000 reference datum.
SHARMA_LAB1 = (50.0000, 2.6772, -79.7751)
SHARMA_LAB2 = (50.0000, 0.0000, -82.7485)
SHARMA_EXPECTED_DE00 = 2.0425

# Canonical sRGB red in CIELAB (D65, 2 degree observer)
SRGB_RED_LAB = (53.2408, 80.0925, 67.2032)


@pytest.fixture
def force_fallback(monkeypatch):
    """Disable the colour-science acceleration for the duration of a test."""
    monkeypatch.setattr(_colorimetry, "_COLOUR_AVAILABLE", False)


def test_fallback_delta_e2000_matches_sharma_reference(force_fallback):
    """The pure-NumPy CIEDE2000 reproduces the canonical Sharma value."""
    assert delta_e2000(SHARMA_LAB1, SHARMA_LAB2) == pytest.approx(
        SHARMA_EXPECTED_DE00, abs=1e-3
    )


def test_fallback_srgb_to_lab_known_value(force_fallback):
    """Pure red converts to its canonical CIELAB coordinates."""
    lab = srgb_to_lab_tuple((255, 0, 0))
    assert lab == pytest.approx(SRGB_RED_LAB, abs=0.1)


def test_fallback_batch_matches_scalar(force_fallback):
    """The batch helper agrees with the scalar fallback under monkeypatching."""
    targets = np.array(
        [srgb_to_lab_tuple(c) for c in [(255, 0, 0), (0, 255, 0), (0, 0, 255)]]
    )
    ref = np.array(srgb_to_lab_tuple((200, 100, 50)))
    batched = delta_e2000_batch(ref, targets)
    scalar = [delta_e2000(ref, t) for t in targets]
    np.testing.assert_allclose(batched, scalar, atol=1e-9)


@pytest.mark.skipif(
    not _colorimetry._COLOUR_AVAILABLE, reason="colour-science not installed"
)
def test_fallback_matches_accelerated_lab(monkeypatch):
    """Fallback and accelerated sRGB->Lab agree within rounding."""
    colors = np.array([[255, 87, 51], [0, 49, 83], [34, 139, 34]], dtype=np.uint8)
    accelerated = srgb_to_lab(colors)
    monkeypatch.setattr(_colorimetry, "_COLOUR_AVAILABLE", False)
    fallback = srgb_to_lab(colors)
    np.testing.assert_allclose(fallback, accelerated, atol=0.05)


@pytest.mark.skipif(
    not _colorimetry._COLOUR_AVAILABLE, reason="colour-science not installed"
)
def test_fallback_matches_accelerated_delta_e(monkeypatch):
    """Fallback and accelerated CIEDE2000 agree within rounding."""
    pairs = [
        (srgb_to_lab_tuple((255, 87, 51)), srgb_to_lab_tuple((0, 49, 83))),
        (srgb_to_lab_tuple((255, 255, 255)), srgb_to_lab_tuple((0, 0, 0))),
        (SHARMA_LAB1, SHARMA_LAB2),
    ]
    accelerated = [delta_e2000(a, b) for a, b in pairs]
    monkeypatch.setattr(_colorimetry, "_COLOUR_AVAILABLE", False)
    fallback = [delta_e2000(a, b) for a, b in pairs]
    np.testing.assert_allclose(fallback, accelerated, atol=1e-3)
