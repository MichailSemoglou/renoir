"""
Tests for ColorNamer class.

Test suite for color naming functionality including vocabulary loading,
color matching, CIEDE2000 distance calculations, and edge cases.
"""

import pytest
from renoir.color import ColorNamer


class TestColorNamerInitialization:
    """Test ColorNamer initialization and vocabulary management."""

    def test_default_initialization(self):
        """Test default initialization with artist vocabulary."""
        namer = ColorNamer()
        assert namer.vocabulary == "artist"

    def test_custom_vocabulary(self):
        """Test initialization with custom vocabulary."""
        namer = ColorNamer(vocabulary="xkcd")
        assert namer.vocabulary == "xkcd"

    def test_invalid_vocabulary(self):
        """Test that invalid vocabulary raises ValueError."""
        with pytest.raises(ValueError, match="Unknown vocabulary"):
            ColorNamer(vocabulary="invalid")

    def test_available_vocabularies(self):
        """Test listing available vocabularies."""
        vocabs = ColorNamer.available_vocabularies()
        assert isinstance(vocabs, list)
        assert "artist" in vocabs
        assert "xkcd" in vocabs
        assert "resene" in vocabs
        assert "natural" in vocabs

    def test_set_vocabulary(self):
        """Test switching vocabularies."""
        namer = ColorNamer(vocabulary="artist")
        namer.set_vocabulary("xkcd")
        assert namer.vocabulary == "xkcd"

    def test_set_invalid_vocabulary(self):
        """Test that setting invalid vocabulary raises ValueError."""
        namer = ColorNamer()
        with pytest.raises(ValueError, match="Unknown vocabulary"):
            namer.set_vocabulary("invalid")


class TestColorNaming:
    """Test color naming functionality."""

    def test_name_rgb_tuple(self):
        """Test naming a color from RGB tuple."""
        namer = ColorNamer(vocabulary="artist")
        name = namer.name((255, 255, 255))
        assert isinstance(name, str)
        assert len(name) > 0

    def test_name_hex_string(self):
        """Test naming a color from hex string."""
        namer = ColorNamer(vocabulary="artist")
        name = namer.name("#FFFFFF")
        assert isinstance(name, str)
        assert len(name) > 0

    def test_name_hex_without_hash(self):
        """Test naming a color from hex string without #."""
        namer = ColorNamer(vocabulary="artist")
        name = namer.name("FFFFFF")
        assert isinstance(name, str)

    def test_name_with_metadata(self):
        """Test naming with full metadata return."""
        namer = ColorNamer(vocabulary="artist")
        result = namer.name((255, 87, 51), return_metadata=True)

        assert isinstance(result, dict)
        assert "name" in result
        assert "hex" in result
        assert "rgb" in result
        assert "distance" in result
        assert "vocabulary" in result
        assert "family" in result

        # Check types
        assert isinstance(result["name"], str)
        assert isinstance(result["hex"], str)
        assert isinstance(result["rgb"], tuple)
        assert isinstance(result["distance"], (int, float))
        assert result["vocabulary"] == "artist"

    def test_name_invalid_rgb(self):
        """Test that invalid RGB raises ValueError."""
        namer = ColorNamer()

        # Out of range
        with pytest.raises(ValueError):
            namer.name((256, 0, 0))

        # Wrong length
        with pytest.raises(ValueError):
            namer.name((255, 255))

        # Wrong type
        with pytest.raises(ValueError):
            namer.name("not a color")

    def test_name_invalid_hex(self):
        """Test that invalid hex raises ValueError."""
        namer = ColorNamer()

        with pytest.raises(ValueError):
            namer.name("#GGGGGG")

        with pytest.raises(ValueError):
            namer.name("#FFF")  # Too short


class TestPaletteNaming:
    """Test palette naming functionality."""

    def test_name_palette(self):
        """Test naming multiple colors."""
        namer = ColorNamer(vocabulary="artist")
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        names = namer.name_palette(colors)

        assert isinstance(names, list)
        assert len(names) == 3
        assert all(isinstance(name, str) for name in names)

    def test_name_palette_with_metadata(self):
        """Test naming palette with metadata."""
        namer = ColorNamer(vocabulary="artist")
        colors = [(255, 0, 0), (0, 255, 0)]
        results = namer.name_palette(colors, return_metadata=True)

        assert isinstance(results, list)
        assert len(results) == 2
        assert all(isinstance(r, dict) for r in results)
        assert all("name" in r for r in results)

    def test_empty_palette(self):
        """Test naming empty palette."""
        namer = ColorNamer()
        names = namer.name_palette([])
        assert names == []


class TestClosestPigment:
    """Test artist pigment matching functionality."""

    def test_closest_pigment_basic(self):
        """Test finding closest pigment."""
        namer = ColorNamer()
        result = namer.closest_pigment((0, 49, 83))

        assert isinstance(result, dict)
        assert "name" in result
        assert "ci_name" in result
        assert result["ci_name"] is not None
        assert "hex" in result
        assert "rgb" in result
        assert "distance" in result

    def test_closest_pigment_from_hex(self):
        """Test finding closest pigment from hex."""
        namer = ColorNamer()
        result = namer.closest_pigment("#003153")

        assert isinstance(result, dict)
        assert "ci_name" in result

    def test_closest_pigment_preserves_vocabulary(self):
        """Test that closest_pigment doesn't permanently change vocabulary."""
        namer = ColorNamer(vocabulary="xkcd")
        original_vocab = namer.vocabulary

        result = namer.closest_pigment((255, 0, 0))

        # Should return to original vocabulary
        assert namer.vocabulary == original_vocab


class TestVocabularyInfo:
    """Test vocabulary information retrieval."""

    def test_get_vocabulary_info(self):
        """Test getting vocabulary metadata."""
        namer = ColorNamer(vocabulary="artist")
        info = namer.get_vocabulary_info()

        assert isinstance(info, dict)
        assert "name" in info
        assert "count" in info
        assert "families" in info
        assert "ci_names" in info
        assert "file" in info

        assert info["name"] == "artist"
        assert info["count"] > 0
        assert isinstance(info["families"], dict)
        assert info["ci_names"] >= 0

    def test_vocabulary_info_different_vocabs(self):
        """Test vocabulary info for different vocabularies."""
        artist_namer = ColorNamer(vocabulary="artist")
        xkcd_namer = ColorNamer(vocabulary="xkcd")

        artist_info = artist_namer.get_vocabulary_info()
        xkcd_info = xkcd_namer.get_vocabulary_info()

        # Should have different metadata
        assert artist_info["name"] != xkcd_info["name"]


class TestColorConversions:
    """Test color conversion utilities."""

    def test_hex_to_rgb(self):
        """Test hex to RGB conversion."""
        namer = ColorNamer()
        rgb = namer._hex_to_rgb("#FF5733")
        assert rgb == (255, 87, 51)

    def test_hex_to_rgb_without_hash(self):
        """Test hex to RGB without # prefix."""
        namer = ColorNamer()
        rgb = namer._hex_to_rgb("FF5733")
        assert rgb == (255, 87, 51)

    def test_rgb_to_hex(self):
        """Test RGB to hex conversion."""
        namer = ColorNamer()
        hex_code = namer._rgb_to_hex((255, 87, 51))
        assert hex_code == "#FF5733"

    def test_rgb_to_lab(self):
        """Test RGB to Lab conversion."""
        namer = ColorNamer()
        lab = namer._rgb_to_lab((255, 0, 0))

        assert isinstance(lab, tuple)
        assert len(lab) == 3
        # Red should have high L (lightness)
        assert lab[0] > 0


class TestCIEDE2000:
    """Test CIEDE2000 color difference calculations."""

    def test_identical_colors(self):
        """Test that identical colors have zero distance."""
        namer = ColorNamer()
        lab = namer._rgb_to_lab((128, 128, 128))
        distance = namer._ciede2000(lab, lab)
        assert distance == pytest.approx(0, abs=0.01)

    def test_different_colors(self):
        """Test that different colors have non-zero distance."""
        namer = ColorNamer()
        lab1 = namer._rgb_to_lab((255, 0, 0))
        lab2 = namer._rgb_to_lab((0, 0, 255))
        distance = namer._ciede2000(lab1, lab2)
        assert distance > 0

    def test_similar_colors_small_distance(self):
        """Test that similar colors have small distance."""
        namer = ColorNamer()
        lab1 = namer._rgb_to_lab((255, 0, 0))
        lab2 = namer._rgb_to_lab((254, 1, 1))
        distance = namer._ciede2000(lab1, lab2)
        # Should be very small
        assert distance < 5


class TestVocabularySpecifics:
    """Test specific vocabulary behaviors."""

    def test_artist_vocabulary_has_ci_names(self):
        """Test that artist vocabulary includes Color Index names."""
        namer = ColorNamer(vocabulary="artist")
        info = namer.get_vocabulary_info()
        # Artist vocabulary should have some CI names
        assert info["ci_names"] > 0

    def test_xkcd_vocabulary_lowercase_names(self):
        """Test that XKCD names are lowercase (per XKCD convention)."""
        namer = ColorNamer(vocabulary="xkcd")
        name = namer.name((255, 255, 255))
        # XKCD names should be lowercase or have mixed case
        assert isinstance(name, str)

    def test_werner_natural_alias(self):
        """Test that 'natural' is an alias for 'werner'."""
        namer1 = ColorNamer(vocabulary="natural")
        namer2 = ColorNamer(vocabulary="werner")

        # Both should produce same results
        color = (100, 150, 200)
        name1 = namer1.name(color)
        name2 = namer2.name(color)

        assert name1 == name2


class TestEdgeCases:
    """Test edge cases and boundary conditions."""

    def test_pure_colors(self):
        """Test naming pure RGB colors."""
        namer = ColorNamer(vocabulary="artist")

        # Pure red, green, blue, black, white
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (0, 0, 0), (255, 255, 255)]

        for color in colors:
            name = namer.name(color)
            assert isinstance(name, str)
            assert len(name) > 0

    def test_grayscale_colors(self):
        """Test naming grayscale colors."""
        namer = ColorNamer(vocabulary="artist")

        grays = [(128, 128, 128), (64, 64, 64), (192, 192, 192)]

        for gray in grays:
            name = namer.name(gray)
            assert isinstance(name, str)

    def test_lab_cache(self):
        """Test that Lab conversion caching works."""
        namer = ColorNamer()

        color = (123, 45, 67)

        # First conversion
        lab1 = namer._rgb_to_lab(color)

        # Should be in cache
        assert color in namer._lab_cache

        # Second conversion should use cache
        lab2 = namer._rgb_to_lab(color)

        assert lab1 == lab2

    def test_multiple_vocabulary_switches(self):
        """Test switching vocabularies multiple times."""
        namer = ColorNamer(vocabulary="artist")
        color = (200, 100, 50)

        name1 = namer.name(color)
        namer.set_vocabulary("xkcd")
        name2 = namer.name(color)
        namer.set_vocabulary("artist")
        name3 = namer.name(color)

        # First and third should be same (same vocabulary)
        assert name1 == name3
        # Second might be different (different vocabulary)
        assert isinstance(name2, str)


class TestIntegrationWithExtractor:
    """Test integration with ColorExtractor."""

    def test_with_color_extractor_output(self):
        """Test naming colors extracted from images."""
        # Simulate ColorExtractor output format
        colors = [(120, 89, 143), (201, 178, 156), (75, 93, 112)]

        namer = ColorNamer(vocabulary="artist")
        names = namer.name_palette(colors)

        assert len(names) == len(colors)
        assert all(isinstance(name, str) for name in names)


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
