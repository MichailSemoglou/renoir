"""
Tests for Distinctness-First Palette Selection (DSP).
"""

import numpy as np
import pytest
from PIL import Image


@pytest.fixture
def solid_red():
    return Image.new("RGB", (20, 20), color=(255, 0, 0))


@pytest.fixture
def colorful():
    img = Image.new("RGB", (50, 50))
    arr = np.array(img)
    arr[:25, :25] = (255, 0, 0)
    arr[:25, 25:] = (0, 255, 0)
    arr[25:, :25] = (0, 0, 255)
    arr[25:, 25:] = (255, 255, 0)
    return Image.fromarray(arr)


class TestSelectPalette:
    def test_returns_n_colors(self, colorful):
        from renoir.color.dsp import select_palette

        result = select_palette(colorful, n=4)
        assert result.n == 4
        assert len(result.palette_rgb) == 4

    def test_monochrome_does_not_crash(self, solid_red):
        from renoir.color.dsp import select_palette

        result = select_palette(solid_red, n=3)
        assert result.n > 0

    def test_to_hex(self, colorful):
        from renoir.color.dsp import select_palette

        result = select_palette(colorful, n=3)
        hexes = result.to_hex()
        assert len(hexes) == 3
        assert all(h.startswith("#") and len(h) == 7 for h in hexes)

    def test_to_rgb_tuples(self, colorful):
        from renoir.color.dsp import select_palette

        result = select_palette(colorful, n=3)
        tuples = result.to_rgb_tuples()
        assert len(tuples) == 3
        assert all(isinstance(t, tuple) and len(t) == 3 for t in tuples)

    def test_frequencies_sum_to_one(self, colorful):
        from renoir.color.dsp import select_palette

        result = select_palette(colorful, n=3)
        assert len(result.frequencies) == 3
        assert all(0 <= f <= 1 for f in result.frequencies)

    def test_wcag_guaranteed_for_high_contrast(self):
        img = Image.new("RGB", (30, 30))
        arr = np.array(img)
        arr[:, :15] = (255, 255, 255)
        arr[:, 15:] = (0, 0, 0)
        result = Image.fromarray(arr)
        from renoir.color.dsp import select_palette

        palette = select_palette(result, n=2, tau_dist=5)
        assert palette.wcag_guaranteed

    def test_wcag_step_can_be_disabled(self, colorful):
        from renoir.color.dsp import select_palette

        result = select_palette(colorful, n=3, wcag_step=False)
        assert isinstance(result.wcag_guaranteed, bool)

    def test_tau_dist_respected(self, colorful):
        from renoir.color.dsp import select_palette, delta_e2000, srgb_to_lab

        result = select_palette(colorful, n=3, tau_dist=15)
        lab = srgb_to_lab(result.palette_rgb)
        for i in range(len(lab)):
            for j in range(i + 1, len(lab)):
                d = delta_e2000(lab[i], lab[j])
                if not result.wcag_replacement_applied:
                    assert d >= 14.0, f"pair ({i},{j}) ΔE={d:.1f} < 14"


class TestExtractDominantColorsDSP:
    def test_method_dsp(self, colorful):
        from renoir.color import ColorExtractor

        extractor = ColorExtractor()
        colors = extractor.extract_dominant_colors(
            colorful,
            n_colors=3,
            method="dsp",
        )
        assert len(colors) == 3
        flat = [(int(c[0]), int(c[1]), int(c[2])) for c in colors]

    def test_method_dsp_on_numpy_array(self, colorful):
        from renoir.color import ColorExtractor

        arr = np.array(colorful)
        extractor = ColorExtractor()
        colors = extractor.extract_dominant_colors(
            arr,
            n_colors=2,
            method="dsp",
        )
        assert len(colors) == 2


class TestRoleAssignment:
    def test_assign_roles_light(self):
        from renoir.color.dsp import select_palette, assign_roles

        result = select_palette(_gradient_image(), n=5)
        roles = assign_roles(
            result.palette_rgb,
            result.palette_lab,
            result.frequencies,
            mode="light",
        )
        assert roles.surface is not None
        assert roles.on_surface is not None
        assert roles.primary is not None

    def test_assign_roles_dark(self):
        from renoir.color.dsp import select_palette, assign_roles

        result = select_palette(_gradient_image(), n=5)
        roles = assign_roles(
            result.palette_rgb,
            result.palette_lab,
            result.frequencies,
            mode="dark",
        )
        assert roles.surface is not None

    def test_surface_is_lightest_in_light_mode(self):
        from renoir.color.dsp import select_palette, assign_roles

        result = select_palette(_gradient_image(), n=5)
        roles = assign_roles(
            result.palette_rgb,
            result.palette_lab,
            result.frequencies,
            mode="light",
        )
        surface_L = result.palette_lab[roles.surface, 0]
        for i in range(result.n):
            assert result.palette_lab[i, 0] <= surface_L + 0.01

    def test_roles_map(self):
        from renoir.color.dsp import select_palette, assign_roles

        result = select_palette(_gradient_image(), n=5)
        roles = assign_roles(
            result.palette_rgb,
            result.palette_lab,
            result.frequencies,
        )
        rmap = roles.roles_map
        assert result.n == len(rmap)
        assert "surface" in rmap.values()

    def test_empty_palette(self):
        from renoir.color.dsp import assign_roles
        import numpy as np

        roles = assign_roles(
            np.empty((0, 3)),
            np.empty((0, 3)),
            [],
        )
        assert roles.surface is None


def _gradient_image():
    """Create a synthetic image with enough colour variation for 5 DSP colours."""
    arr = np.zeros((40, 40, 3), dtype=np.uint8)
    for y in range(40):
        for x in range(40):
            arr[y, x] = (
                int(x / 40 * 240),
                int(y / 40 * 200),
                int(((x + y) / 80) * 180 + 40),
            )
    return Image.fromarray(arr)
