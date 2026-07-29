"""
Distinctness-First Palette Selection (DSP) for accessible design systems.

A constrained-greedy palette extraction algorithm that maximises perceptual
distinctness (minimum pairwise ΔE₂₀₀₀) while guaranteeing at least one
WCAG AA-compliant Surface/On-Surface contrast pair.

Imported from `dsp-palette <https://github.com/MichailSemoglou/dsp-palette>`_
(DOI 10.5281/zenodo.20092216), submitted to APSIPA ASC 2026, Track IVM.

Algorithm
---------
1. Quantise image via median cut → candidate pool (~256 colours).
2. Convert candidates to CIELAB (D65, 2° observer).
3. Initialise palette with the highest-frequency candidate.
4. Greedily expand by maximising *α·log(f) + β·minΔE*, subject to
   *minΔE ≥ τ* (default 10 ΔE₂₀₀₀).
5. Post-selection WCAG AA check: if no pair reaches 4.5:1, replace the
   least-distinct member with a candidate that creates a qualifying pair
   while preserving distinctness when possible.
6. Optionally assign semantic design-token roles (Surface, On-Surface,
   Primary, Secondary, Accent).

Public API
----------
``select_palette(image, n, ...) → SelectionResult``
    Run DSP on a PIL Image.

``assign_roles(palette_rgb, ...) → RoleAssignment``
    Assign semantic roles to an existing palette.

Reference
---------
Semoglou, M. (2026). Distinctness-First Palette Extraction for Accessible
Design Systems.  Submitted to *APSIPA ASC 2026*, Track IVM.
"""

import math
import warnings
from dataclasses import dataclass, field
from itertools import combinations
from typing import List, Literal, Optional, Sequence, Tuple, Union

import numpy as np
from numpy.typing import NDArray
from PIL import Image

from ._colorimetry import (
    delta_e2000,
    relative_luminance,
    srgb_to_lab,
    wcag_contrast,
    WCAG_AA_NORMAL,
    WCAG_AAA_NORMAL,
)

# ---------------------------------------------------------------------------
# Data classes
# ---------------------------------------------------------------------------


@dataclass
class SelectionResult:
    """Full output of the constrained greedy DSP selector.

    Attributes
    ----------
    palette_rgb : NDArray shape (n, 3)
        Final palette in sRGB 0–255 uint8.
    palette_lab : NDArray shape (n, 3)
        Final palette in CIELAB.
    frequencies : list[float]
        Normalised frequency (0–1) of each palette colour in the source image.
    wcag_guaranteed : bool
        True if at least one palette pair satisfies WCAG AA contrast (≥4.5:1).
    wcag_replacement_applied : bool
        True if the post-selection WCAG step replaced a palette member.
    wcag_distinctness_compromised : bool
        True if the WCAG replacement could only find a contrast-satisfying
        candidate that violates τ_dist.
    candidate_pool_size : int
        Actual number of distinct candidate colours considered.
    """

    palette_rgb: NDArray[np.uint8]
    palette_lab: NDArray[np.float64]
    frequencies: List[float]
    n: int
    alpha: float
    beta: float
    tau_dist: float
    wcag_guaranteed: bool
    wcag_replacement_applied: bool
    wcag_distinctness_compromised: bool
    candidate_pool_size: int

    def to_hex(self) -> List[str]:
        return [
            "#{:02x}{:02x}{:02x}".format(int(r), int(g), int(b))
            for r, g, b in self.palette_rgb
        ]

    def to_rgb_tuples(self) -> List[Tuple[int, int, int]]:
        return [(int(r), int(g), int(b)) for r, g, b in self.palette_rgb]


@dataclass
class RoleAssignment:
    """Semantic design-token role assignment for a palette.

    Attributes
    ----------
    surface : int | None
    on_surface : int | None
    primary : int | None
    secondary : int | None
    accent : int | None
    extras : list[int]
        Indices of palette members not assigned to a named role (n > 5).
    """

    surface: Optional[int]
    on_surface: Optional[int]
    primary: Optional[int]
    secondary: Optional[int]
    accent: Optional[int]
    extras: List[int] = field(default_factory=list)

    @property
    def roles_map(self) -> dict:
        out: dict = {}
        for role, idx in [
            ("surface", self.surface),
            ("on-surface", self.on_surface),
            ("primary", self.primary),
            ("secondary", self.secondary),
            ("accent", self.accent),
        ]:
            if idx is not None:
                out[idx] = role
        for i, idx in enumerate(self.extras):
            out[idx] = f"extra-{i + 1}"
        return out


# ---------------------------------------------------------------------------
# Internal selection helpers
# ---------------------------------------------------------------------------


def _quantize_to_candidates(
    image: Image.Image,
    max_candidates: int,
) -> Tuple[NDArray[np.uint8], NDArray[np.float64]]:
    if image.mode != "RGB":
        image = image.convert("RGB")
    quantized = image.quantize(colors=max_candidates, method=Image.Quantize.MEDIANCUT)
    quantized_rgb = quantized.convert("RGB")
    pixels = np.array(quantized_rgb, dtype=np.uint8).reshape(-1, 3)
    unique, counts = np.unique(pixels, axis=0, return_counts=True)
    total = counts.sum()
    return unique, counts.astype(np.float64) / total


def _min_de_to_palette(
    lab_candidate: NDArray[np.float64],
    palette_lab: List[NDArray[np.float64]],
) -> float:
    return min(delta_e2000(lab_candidate, p) for p in palette_lab)


# ---------------------------------------------------------------------------
# Main selector
# ---------------------------------------------------------------------------


def select_palette(
    image: Image.Image,
    n: int = 5,
    alpha: float = 1.0,
    beta: float = 1.0,
    tau_dist: float = 15.0,
    max_candidates: int = 256,
    wcag_step: bool = True,
) -> SelectionResult:
    """Run the constrained greedy DSP selection on *image*.

    Parameters
    ----------
    image:
        A PIL Image. Converted to RGB internally.
    n:
        Target palette size (default 5).
    alpha:
        Weight for log-frequency in the selection score.
    beta:
        Weight for min-ΔE2000 in the selection score.
        The selection is largely invariant to β/α because the τ_dist hard
        constraint already clamps minimum distinctness.  Default α=β=1.0
        is representative of the family.
    tau_dist:
        Minimum ΔE2000 a candidate must have from all current palette
        members to be eligible (default 15 — "clearly distinct").
    max_candidates:
        Number of colours in the median-cut quantisation pool (default 256).
    wcag_step:
        If True (default), run the WCAG AA post-selection replacement check.
        Set to False to skip it (useful for benchmarks).

    Returns
    -------
    SelectionResult

    Example
    -------
    >>> from PIL import Image
    >>> from renoir.color.dsp import select_palette
    >>> img = Image.open("painting.jpg")
    >>> result = select_palette(img, n=5)
    >>> print(result.to_hex())
    """
    candidates_rgb, freqs = _quantize_to_candidates(image, max_candidates)
    return _select_from_candidates(
        candidates_rgb,
        freqs,
        n=n,
        alpha=alpha,
        beta=beta,
        tau_dist=tau_dist,
        wcag_step=wcag_step,
    )


def _select_from_candidates(
    candidates_rgb: NDArray[np.uint8],
    freqs: NDArray[np.float64],
    n: int = 5,
    alpha: float = 1.0,
    beta: float = 1.0,
    tau_dist: float = 15.0,
    wcag_step: bool = True,
) -> SelectionResult:
    if n < 1:
        raise ValueError(f"n must be ≥ 1, got {n}")

    candidates_lab = srgb_to_lab(candidates_rgb)
    K = len(candidates_rgb)

    palette_indices, in_palette = _greedy_expand_palette(
        candidates_rgb,
        candidates_lab,
        freqs,
        n=n,
        alpha=alpha,
        beta=beta,
        tau_dist=tau_dist,
    )

    (
        palette_indices,
        in_palette,
        wcag_guaranteed,
        wcag_replacement_applied,
        wcag_distinctness_compromised,
    ) = _apply_wcag_replacement(
        candidates_rgb,
        candidates_lab,
        palette_indices,
        in_palette,
        tau_dist=tau_dist,
        wcag_step=wcag_step,
    )

    final_rgb = candidates_rgb[palette_indices]
    final_lab = candidates_lab[palette_indices]
    final_freqs = [float(freqs[i]) for i in palette_indices]

    return SelectionResult(
        palette_rgb=final_rgb,
        palette_lab=final_lab,
        frequencies=final_freqs,
        n=len(palette_indices),
        alpha=alpha,
        beta=beta,
        tau_dist=tau_dist,
        wcag_guaranteed=wcag_guaranteed,
        wcag_replacement_applied=wcag_replacement_applied,
        wcag_distinctness_compromised=wcag_distinctness_compromised,
        candidate_pool_size=K,
    )


def _greedy_expand_palette(
    candidates_rgb: NDArray[np.uint8],
    candidates_lab: NDArray[np.float64],
    freqs: NDArray[np.float64],
    n: int,
    alpha: float,
    beta: float,
    tau_dist: float,
) -> Tuple[List[int], set]:
    K = len(candidates_rgb)
    palette_indices: List[int] = [int(np.argmax(freqs))]
    in_palette: set = set(palette_indices)

    while len(palette_indices) < n:
        best_score = -math.inf
        best_idx: Optional[int] = None
        palette_lab_list = [candidates_lab[i] for i in palette_indices]

        for idx in range(K):
            if idx in in_palette:
                continue
            min_de = _min_de_to_palette(candidates_lab[idx], palette_lab_list)
            if min_de < tau_dist:
                continue
            score = alpha * math.log(freqs[idx] + 1e-12) + beta * min_de
            if score > best_score:
                best_score = score
                best_idx = idx

        if best_idx is None:
            best_score, best_idx = _relax_and_retry(
                candidates_lab,
                freqs,
                palette_indices,
                in_palette,
                alpha,
                beta,
                tau_dist,
                best_score,
            )

            if best_idx is None:
                palette_lab_list = [candidates_lab[i] for i in palette_indices]
                remaining = [i for i in range(K) if i not in in_palette]
                if not remaining:
                    break
                best_idx = max(
                    remaining,
                    key=lambda i: _min_de_to_palette(
                        candidates_lab[i], palette_lab_list
                    ),
                )
                warnings.warn(
                    f"DSP: τ_dist={tau_dist} could not be satisfied at palette size "
                    f"{len(palette_indices) + 1}; added most-distant remaining candidate.",
                    stacklevel=2,
                )

        palette_indices.append(best_idx)
        in_palette.add(best_idx)

    return palette_indices, in_palette


def _relax_and_retry(
    candidates_lab: NDArray[np.float64],
    freqs: NDArray[np.float64],
    palette_indices: List[int],
    in_palette: set,
    alpha: float,
    beta: float,
    tau_dist: float,
    best_score: float,
) -> Tuple[float, Optional[int]]:
    K = len(candidates_lab)
    relaxed_tau = tau_dist
    max_iters = 50
    best_idx: Optional[int] = None

    for _ in range(max_iters):
        relaxed_tau *= 0.75
        if relaxed_tau <= 1e-6:
            break
        palette_lab_list = [candidates_lab[i] for i in palette_indices]
        for idx in range(K):
            if idx in in_palette:
                continue
            min_de = _min_de_to_palette(candidates_lab[idx], palette_lab_list)
            if min_de < relaxed_tau:
                continue
            score = alpha * math.log(freqs[idx] + 1e-12) + beta * min_de
            if score > best_score:
                best_score = score
                best_idx = idx
        if best_idx is not None:
            return best_score, best_idx

    return best_score, best_idx


def _apply_wcag_replacement(
    candidates_rgb: NDArray[np.uint8],
    candidates_lab: NDArray[np.float64],
    palette_indices: List[int],
    in_palette: set,
    tau_dist: float,
    wcag_step: bool,
) -> Tuple[List[int], set, bool, bool, bool]:
    wcag_replacement_applied = False
    wcag_distinctness_compromised = False
    wcag_guaranteed = _palette_has_aa_pair(candidates_rgb, palette_indices)

    if not wcag_step or wcag_guaranteed:
        return (
            palette_indices,
            in_palette,
            wcag_guaranteed,
            wcag_replacement_applied,
            wcag_distinctness_compromised,
        )

    palette_lab_list = [candidates_lab[i] for i in palette_indices]
    K = len(candidates_rgb)

    least_distinct_pos = min(
        range(len(palette_indices)),
        key=lambda pos: _intra_min_de(palette_indices, palette_lab_list, pos),
    )
    victim_idx = palette_indices[least_distinct_pos]

    remaining_indices = [
        idx for k, idx in enumerate(palette_indices) if k != least_distinct_pos
    ]
    remaining_lab = [candidates_lab[idx] for idx in remaining_indices]

    candidate_pool = [i for i in range(K) if i not in in_palette]
    best_replacement: Optional[int] = None
    best_contrast = 0.0
    best_replacement_fallback: Optional[int] = None
    best_contrast_fallback = 0.0

    for cand in candidate_pool:
        cand_lab = candidates_lab[cand]
        max_cr_with_remaining = max(
            (
                wcag_contrast(candidates_rgb[cand], candidates_rgb[pal_idx])
                for pal_idx in remaining_indices
            ),
            default=0.0,
        )
        if max_cr_with_remaining < WCAG_AA_NORMAL:
            continue

        if remaining_lab:
            min_de_remaining = min(
                delta_e2000(cand_lab, rlab) for rlab in remaining_lab
            )
        else:
            min_de_remaining = float("inf")

        if min_de_remaining >= tau_dist:
            if max_cr_with_remaining > best_contrast:
                best_contrast = max_cr_with_remaining
                best_replacement = cand
        else:
            if max_cr_with_remaining > best_contrast_fallback:
                best_contrast_fallback = max_cr_with_remaining
                best_replacement_fallback = cand

    if best_replacement is not None:
        palette_indices[least_distinct_pos] = best_replacement
        in_palette.discard(victim_idx)
        in_palette.add(best_replacement)
        wcag_replacement_applied = True
        wcag_guaranteed = True
    elif best_replacement_fallback is not None:
        palette_indices[least_distinct_pos] = best_replacement_fallback
        in_palette.discard(victim_idx)
        in_palette.add(best_replacement_fallback)
        wcag_replacement_applied = True
        wcag_guaranteed = True
        wcag_distinctness_compromised = True
    else:
        warnings.warn(
            "DSP: WCAG AA contrast guarantee could not be satisfied "
            "from the candidate pool.",
            stacklevel=2,
        )

    return (
        palette_indices,
        in_palette,
        wcag_guaranteed,
        wcag_replacement_applied,
        wcag_distinctness_compromised,
    )


def _palette_has_aa_pair(
    candidates_rgb: NDArray[np.uint8],
    palette_indices: List[int],
) -> bool:
    for a, b in combinations(palette_indices, 2):
        if wcag_contrast(candidates_rgb[a], candidates_rgb[b]) >= WCAG_AA_NORMAL:
            return True
    return False


def _intra_min_de(
    palette_indices: List[int],
    palette_lab_list: list,
    pos: int,
) -> float:
    others = [palette_lab_list[k] for k in range(len(palette_indices)) if k != pos]
    if not others:
        return 0.0
    return min(delta_e2000(palette_lab_list[pos], o) for o in others)


# ---------------------------------------------------------------------------
# Role assignment
# ---------------------------------------------------------------------------


def assign_roles(
    palette_rgb: NDArray,
    palette_lab: NDArray[np.float64],
    frequencies: List[float],
    tau_role: float = 10.0,
    mode: Literal["light", "dark", "auto"] = "light",
    image_mean_L: Optional[float] = None,
) -> RoleAssignment:
    """Assign semantic design-token roles to a DSP palette.

    Roles (fill order): surface, on-surface, primary, secondary, accent.

    Parameters
    ----------
    palette_rgb:
        Shape (n, 3) sRGB colours (0–255).
    palette_lab:
        Shape (n, 3) CIELAB colours.
    frequencies:
        Length-n list of normalised pixel frequencies (0–1).
    tau_role:
        Minimum ΔE2000 between primary candidate and surface (default 10).
    mode:
        ``'light'`` — surface = highest L* (default).
        ``'dark'`` — surface = lowest L*.
        ``'auto'`` — dark if mean L* < 40, else light.
    image_mean_L:
        Pre-computed mean L* of the full image (used by ``mode='auto'``).

    Returns
    -------
    RoleAssignment
    """
    n = len(palette_rgb)
    if n == 0:
        return RoleAssignment(
            surface=None,
            on_surface=None,
            primary=None,
            secondary=None,
            accent=None,
            extras=[],
        )

    available = list(range(n))

    if mode == "auto":
        if image_mean_L is not None:
            mean_L = image_mean_L
        else:
            mean_L = float(
                sum(frequencies[i] * float(palette_lab[i, 0]) for i in range(n))
            )
        effective_mode: Literal["light", "dark"] = "dark" if mean_L < 40.0 else "light"
    else:
        effective_mode = mode

    if effective_mode == "dark":
        surface_idx = min(available, key=lambda i: float(palette_lab[i, 0]))
    else:
        surface_idx = max(available, key=lambda i: float(palette_lab[i, 0]))
    available.remove(surface_idx)

    if not available:
        return RoleAssignment(
            surface=surface_idx,
            on_surface=None,
            primary=None,
            secondary=None,
            accent=None,
            extras=[],
        )

    on_surface_idx = max(
        available,
        key=lambda i: wcag_contrast(palette_rgb[i], palette_rgb[surface_idx]),
    )
    available.remove(on_surface_idx)

    if not available:
        return RoleAssignment(
            surface=surface_idx,
            on_surface=on_surface_idx,
            primary=None,
            secondary=None,
            accent=None,
            extras=[],
        )

    eligible_primary = [
        i
        for i in available
        if delta_e2000(palette_lab[i], palette_lab[surface_idx]) >= tau_role
    ]
    if not eligible_primary:
        eligible_primary = available[:]

    primary_idx = max(eligible_primary, key=lambda i: frequencies[i])
    available.remove(primary_idx)

    if not available:
        return RoleAssignment(
            surface=surface_idx,
            on_surface=on_surface_idx,
            primary=primary_idx,
            secondary=None,
            accent=None,
            extras=[],
        )

    primary_hue = (
        math.degrees(
            math.atan2(
                float(palette_lab[primary_idx, 2]),
                float(palette_lab[primary_idx, 1]),
            )
        )
        % 360.0
    )

    def _hue_distance(idx: int) -> float:
        h = (
            math.degrees(
                math.atan2(float(palette_lab[idx, 2]), float(palette_lab[idx, 1]))
            )
            % 360.0
        )
        diff = abs(h - primary_hue)
        return min(diff, 360.0 - diff)

    secondary_idx = max(available, key=_hue_distance)
    available.remove(secondary_idx)

    if not available:
        return RoleAssignment(
            surface=surface_idx,
            on_surface=on_surface_idx,
            primary=primary_idx,
            secondary=secondary_idx,
            accent=None,
            extras=[],
        )

    def _chroma(idx: int) -> float:
        a, b = float(palette_lab[idx, 1]), float(palette_lab[idx, 2])
        return math.sqrt(a**2 + b**2)

    accent_idx = max(available, key=_chroma)
    available.remove(accent_idx)

    extras = sorted(available, key=lambda i: frequencies[i], reverse=True)

    return RoleAssignment(
        surface=surface_idx,
        on_surface=on_surface_idx,
        primary=primary_idx,
        secondary=secondary_idx,
        accent=accent_idx,
        extras=extras,
    )
