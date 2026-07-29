"""
Shared color-science primitives for the renoir package.

All sRGB → CIELAB conversions use the D65 white point (2° observer)
per IEC 61966-2-1.  CIEDE2000 follows Sharma, Wu & Dalal (2005).

This module is the single source of truth.  Every other module that
needs sRGB-to-Lab, ΔE₂₀₀₀, relative luminance, WCAG contrast, or
hex↔RGB conversion imports from here.
"""

import math
from typing import List, Sequence, Tuple, Union

import numpy as np
from numpy.typing import NDArray

# ---------------------------------------------------------------------------
# Optional colour-science acceleration
# ---------------------------------------------------------------------------
try:
    import colour  # type: ignore[import-untyped]

    _COLOUR_AVAILABLE = True
except ImportError:  # pragma: no cover
    _COLOUR_AVAILABLE = False

# ---------------------------------------------------------------------------
# D65 reference white (XYZ, 2° observer)
# ---------------------------------------------------------------------------
_D65_XYZ = np.array([95.0489, 100.0, 108.8840])

# IEC 61966-2-1 sRGB linearisation constants
_SRGB_EPSILON = 0.04045
_SRGB_KAPPA = 903.3

# BT.709 luma coefficients
_LUMA_R = 0.2126
_LUMA_G = 0.7152
_LUMA_B = 0.0722

# WCAG 2.1 contrast thresholds
WCAG_AA_NORMAL = 4.5
WCAG_AAA_NORMAL = 7.0


# ===================================================================
# sRGB ⇄ CIELAB
# ===================================================================


def srgb_to_lab(rgb: NDArray) -> NDArray[np.float64]:
    """Convert an array of sRGB colours to CIELAB (D65, 2°).

    Accepts integer uint8 (0–255) or float (0–1) arrays.
    Returns an NDArray of shape (..., 3) with L*, a*, b* values.
    """
    orig = np.asarray(rgb)
    if np.issubdtype(orig.dtype, np.integer) or orig.max() > 1.0:
        rgb_norm = orig.astype(np.float64) / 255.0
    else:
        rgb_norm = orig.astype(np.float64)

    if _COLOUR_AVAILABLE:
        return np.asarray(
            colour.XYZ_to_Lab(
                colour.sRGB_to_XYZ(rgb_norm),
                illuminant=colour.CCS_ILLUMINANTS[
                    "CIE 1931 2 Degree Standard Observer"
                ]["D65"],
            ),
            dtype=np.float64,
        )

    # Pure-NumPy fallback (IEC 61966-2-1 linearise, XYZ matrix, XYZ→Lab)
    linear = np.where(
        rgb_norm <= _SRGB_EPSILON,
        rgb_norm / 12.92,
        ((rgb_norm + 0.055) / 1.055) ** 2.4,
    )
    M = np.array(
        [
            [0.4124564, 0.3575761, 0.1804375],
            [0.2126729, 0.7151522, 0.0721750],
            [0.0193339, 0.1191920, 0.9503041],
        ]
    )
    xyz = linear @ M.T * 100.0
    xyz_norm = xyz / _D65_XYZ
    eps = 0.008856
    f_vals = np.where(
        xyz_norm > eps,
        np.cbrt(xyz_norm),
        (_SRGB_KAPPA * xyz_norm + 16.0) / 116.0,
    )
    L = 116.0 * f_vals[..., 1] - 16.0
    a = 500.0 * (f_vals[..., 0] - f_vals[..., 1])
    b = 200.0 * (f_vals[..., 1] - f_vals[..., 2])
    return np.stack([L, a, b], axis=-1)


def srgb_to_lab_tuple(rgb: Tuple[int, int, int]) -> Tuple[float, float, float]:
    """Convert a single sRGB tuple to a CIELAB tuple.

    Convenience wrapper around :func:`srgb_to_lab` for code that expects
    ``(L*, a*, b*)`` return values rather than NDArrays.
    """
    arr = srgb_to_lab(np.array([rgb], dtype=np.uint8))
    return (float(arr[0, 0]), float(arr[0, 1]), float(arr[0, 2]))


# ===================================================================
# CIEDE2000  (Sharma, Wu & Dalal, 2005)
# ===================================================================


def delta_e2000(
    lab1: Union[Sequence[float], NDArray[np.float64]],
    lab2: Union[Sequence[float], NDArray[np.float64]],
) -> float:
    """CIE ΔE 2000 between two CIELAB colours."""
    if _COLOUR_AVAILABLE:
        return float(
            colour.delta_E(
                np.asarray(lab1, dtype=np.float64),
                np.asarray(lab2, dtype=np.float64),
                method="CIE 2000",
            )
        )

    L1, a1, b1 = (float(x) for x in lab1)
    L2, a2, b2 = (float(x) for x in lab2)

    C1 = math.sqrt(a1**2 + b1**2)
    C2 = math.sqrt(a2**2 + b2**2)
    C_avg7 = ((C1 + C2) / 2) ** 7
    G = 0.5 * (1 - math.sqrt(C_avg7 / (C_avg7 + 25**7)))
    a1p = a1 * (1 + G)
    a2p = a2 * (1 + G)

    C1p = math.sqrt(a1p**2 + b1**2)
    C2p = math.sqrt(a2p**2 + b2**2)
    h1p = math.degrees(math.atan2(b1, a1p)) % 360
    h2p = math.degrees(math.atan2(b2, a2p)) % 360

    dLp = L2 - L1
    dCp = C2p - C1p

    if C1p * C2p == 0:
        dhp = 0.0
    elif abs(h2p - h1p) <= 180:
        dhp = h2p - h1p
    elif h2p - h1p > 180:
        dhp = h2p - h1p - 360
    else:
        dhp = h2p - h1p + 360

    dHp = 2 * math.sqrt(C1p * C2p) * math.sin(math.radians(dhp / 2))

    Lp_avg = (L1 + L2) / 2
    Cp_avg = (C1p + C2p) / 2
    Cp_avg7 = Cp_avg**7

    if C1p * C2p == 0:
        hp_avg = h1p + h2p
    elif abs(h1p - h2p) <= 180:
        hp_avg = (h1p + h2p) / 2
    elif h1p + h2p < 360:
        hp_avg = (h1p + h2p + 360) / 2
    else:
        hp_avg = (h1p + h2p - 360) / 2

    T = (
        1
        - 0.17 * math.cos(math.radians(hp_avg - 30))
        + 0.24 * math.cos(math.radians(2 * hp_avg))
        + 0.32 * math.cos(math.radians(3 * hp_avg + 6))
        - 0.20 * math.cos(math.radians(4 * hp_avg - 63))
    )
    SL = 1 + 0.015 * (Lp_avg - 50) ** 2 / math.sqrt(20 + (Lp_avg - 50) ** 2)
    SC = 1 + 0.045 * Cp_avg
    SH = 1 + 0.015 * Cp_avg * T

    d_theta = 30 * math.exp(-(((hp_avg - 275) / 25) ** 2))
    RC = 2 * math.sqrt(Cp_avg7 / (Cp_avg7 + 25**7))
    RT = -math.sin(math.radians(2 * d_theta)) * RC

    return math.sqrt(
        (dLp / SL) ** 2
        + (dCp / SC) ** 2
        + (dHp / SH) ** 2
        + RT * (dCp / SC) * (dHp / SH)
    )


# ===================================================================
# WCAG 2.1 contrast
# ===================================================================


def relative_luminance(rgb: "Union[Sequence[float], NDArray]") -> float:
    """WCAG 2.1 relative luminance for sRGB.

    Accepts integer uint8 (0–255) or float (0–1) values.
    Reference: https://www.w3.org/TR/WCAG21/#dfn-relative-luminance
    """
    orig = np.asarray(rgb)
    if np.issubdtype(orig.dtype, np.integer) or orig.max() > 1.0:
        arr = orig.astype(np.float64) / 255.0
    else:
        arr = orig.astype(np.float64)
    lin = np.where(
        arr <= _SRGB_EPSILON,
        arr / 12.92,
        ((arr + 0.055) / 1.055) ** 2.4,
    )
    return float(_LUMA_R * lin[0] + _LUMA_G * lin[1] + _LUMA_B * lin[2])


def wcag_contrast(
    rgb1: "Union[Sequence[float], NDArray]",
    rgb2: "Union[Sequence[float], NDArray]",
) -> float:
    """WCAG 2.1 contrast ratio between two sRGB colours.

    Returns a float in [1, 21].
    """
    L1 = relative_luminance(rgb1)
    L2 = relative_luminance(rgb2)
    lighter = max(L1, L2)
    darker = min(L1, L2)
    return (lighter + 0.05) / (darker + 0.05)


def wcag_level(contrast_ratio: float) -> str:
    """Map a contrast ratio to 'AAA' / 'AA' / 'A' / 'fail'."""
    if contrast_ratio >= WCAG_AAA_NORMAL:
        return "AAA"
    if contrast_ratio >= WCAG_AA_NORMAL:
        return "AA"
    if contrast_ratio >= 3.0:
        return "A"
    return "fail"


# ===================================================================
# hex ⇄ RGB
# ===================================================================


def hex_to_rgb(hex_color: str) -> Tuple[int, int, int]:
    """Convert a hex colour string to an RGB tuple.

    Accepts ``#RRGGBB``, ``RRGGBB``, ``#RGB``, and ``RGB`` forms.
    """
    hex_color = hex_color.lstrip("#")
    if len(hex_color) == 3:
        hex_color = "".join(c * 2 for c in hex_color)
    if len(hex_color) != 6:
        raise ValueError(f"Invalid hex color: {hex_color!r}")
    try:
        return (
            int(hex_color[0:2], 16),
            int(hex_color[2:4], 16),
            int(hex_color[4:6], 16),
        )
    except (ValueError, IndexError):
        raise ValueError(f"Invalid hex color: {hex_color!r}")


def rgb_to_hex(rgb: Union[Tuple[int, int, int], NDArray]) -> str:
    """Convert an RGB tuple to a ``#RRGGBB`` hex string."""
    return "#{:02x}{:02x}{:02x}".format(int(rgb[0]), int(rgb[1]), int(rgb[2]))


# ===================================================================
# Convenience batch helpers
# ===================================================================


def delta_e2000_batch(
    lab_ref: NDArray[np.float64],
    lab_targets: NDArray[np.float64],
) -> NDArray[np.float64]:
    """ΔE2000 from one reference Lab to many target Labs."""
    targets = np.asarray(lab_targets, dtype=np.float64)
    if _COLOUR_AVAILABLE:
        ref = np.broadcast_to(
            np.asarray(lab_ref, dtype=np.float64), targets.shape
        ).copy()
        return np.asarray(
            colour.delta_E(ref, targets, method="CIE 2000"),
            dtype=np.float64,
        )
    return np.array([delta_e2000(lab_ref, t) for t in targets])
