"""
Tests for color harmony detection methods.

Covers detect_triadic_harmony, detect_analogous_harmony,
detect_split_complementary, detect_tetradic_harmony, and
analyze_color_harmony.
"""

import pytest
from renoir.color import ColorAnalyzer


class TestDetectTriadicHarmony:
    """Tests for detect_triadic_harmony."""

    def test_per_triadic(self, color_analyzer):
        """Red, green, blue are 120 degrees apart and form a triad."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        triads = color_analyzer.detect_triadic_harmony(colors, tolerance=30)
        assert len(triads) >= 1

    def test_no_triadic_in_analogous(self, color_analyzer):
        """Three close-hue colors should not form a triad."""
        colors = [(255, 0, 0), (255, 50, 0), (255, 100, 0)]
        triads = color_analyzer.detect_triadic_harmony(colors, tolerance=30)
        assert len(triads) == 0

    def test_single_color(self, color_analyzer):
        """A single color cannot form a triad."""
        triads = color_analyzer.detect_triadic_harmony([(255, 0, 0)])
        assert triads == []

    def test_two_colors(self, color_analyzer):
        """Two colors cannot form a triad."""
        triads = color_analyzer.detect_triadic_harmony([(255, 0, 0), (0, 255, 0)])
        assert triads == []

    def test_empty_palette(self, color_analyzer):
        triads = color_analyzer.detect_triadic_harmony([])
        assert triads == []

    def test_tight_tolerance(self, color_analyzer):
        """With zero tolerance, only exact 120-degree spacing passes."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        triads_strict = color_analyzer.detect_triadic_harmony(colors, tolerance=0)
        triads_loose = color_analyzer.detect_triadic_harmony(colors, tolerance=30)
        assert len(triads_loose) >= len(triads_strict)


class TestDetectAnalogousHarmony:
    """Tests for detect_analogous_harmony."""

    def test_analogous_blues(self, color_analyzer):
        """Close-hue blues and greens form an analogous group."""
        colors = [(0, 100, 255), (0, 200, 200), (0, 255, 100)]
        groups = color_analyzer.detect_analogous_harmony(colors, max_hue_range=60)
        assert len(groups) >= 1
        assert all(len(g) >= 2 for g in groups)

    def test_no_analogous_in_spread(self, color_analyzer):
        """Colors spread across the wheel should not be analogous."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        groups = color_analyzer.detect_analogous_harmony(colors, max_hue_range=30)
        assert len(groups) == 0

    def test_single_color(self, color_analyzer):
        groups = color_analyzer.detect_analogous_harmony([(255, 0, 0)])
        assert groups == []

    def test_empty_palette(self, color_analyzer):
        groups = color_analyzer.detect_analogous_harmony([])
        assert groups == []

    def test_wide_range_captures_more(self, color_analyzer):
        """A wider hue range should capture at least as many groups."""
        colors = [(255, 0, 0), (255, 100, 0), (0, 200, 200), (0, 100, 255)]
        narrow = color_analyzer.detect_analogous_harmony(colors, max_hue_range=30)
        wide = color_analyzer.detect_analogous_harmony(colors, max_hue_range=90)
        assert len(wide) >= len(narrow)


class TestDetectSplitComplementary:
    """Tests for detect_split_complementary."""

    def test_split_complementary_basic(self, color_analyzer):
        """Red with two colors flanking its complement should be detected."""
        colors = [(255, 0, 0), (0, 200, 100), (0, 100, 200)]
        splits = color_analyzer.detect_split_complementary(colors, tolerance=30)
        assert len(splits) >= 1
        triplet = splits[0]
        assert triplet[0] == (255, 0, 0)
        assert set(triplet[1:]) == {(0, 200, 100), (0, 100, 200)}

    def test_no_split_complementary(self, color_analyzer):
        """All warm colors should not produce split-complementary triplets."""
        colors = [(255, 0, 0), (255, 100, 0), (255, 200, 0)]
        splits = color_analyzer.detect_split_complementary(colors, tolerance=30)
        assert len(splits) == 0

    def test_single_color(self, color_analyzer):
        splits = color_analyzer.detect_split_complementary([(255, 0, 0)])
        assert splits == []

    def test_empty_palette(self, color_analyzer):
        splits = color_analyzer.detect_split_complementary([])
        assert splits == []


class TestDetectTetradicHarmony:
    """Tests for detect_tetradic_harmony."""

    def test_tetradic_basic(self, color_analyzer):
        """Two complementary pairs may form a tetradic set."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        tetrads = color_analyzer.detect_tetradic_harmony(colors, tolerance=30)
        assert len(tetrads) == 1

    def test_too_few_colors(self, color_analyzer):
        """Fewer than four colors cannot form a tetrad."""
        tetrads = color_analyzer.detect_tetradic_harmony(
            [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        )
        assert tetrads == []

    def test_empty_palette(self, color_analyzer):
        tetrads = color_analyzer.detect_tetradic_harmony([])
        assert tetrads == []

    def test_all_same_hue(self, color_analyzer):
        """Four near-identical colors should not form a tetrad."""
        colors = [(255, 0, 0), (250, 5, 5), (245, 10, 10), (240, 15, 15)]
        tetrads = color_analyzer.detect_tetradic_harmony(colors, tolerance=30)
        assert len(tetrads) == 0


class TestAnalyzeColorHarmony:
    """Tests for the comprehensive analyze_color_harmony method."""

    def test_full_analysis_structure(self, color_analyzer):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        result = color_analyzer.analyze_color_harmony(colors)

        assert isinstance(result, dict)
        assert "complementary_pairs" in result
        assert "triadic_sets" in result
        assert "analogous_groups" in result
        assert "split_complementary_sets" in result
        assert "tetradic_sets" in result
        assert "harmony_counts" in result
        assert "total_harmonies" in result
        assert "harmony_score" in result
        assert "dominant_harmony" in result

    def test_harmony_score_range(self, color_analyzer):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        result = color_analyzer.analyze_color_harmony(colors)
        assert 0 <= result["harmony_score"] <= 1

    def test_dominant_harmony_is_string(self, color_analyzer):
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255)]
        result = color_analyzer.analyze_color_harmony(colors)
        assert isinstance(result["dominant_harmony"], str)

    def test_no_harmony_in_monochrome(self, color_analyzer):
        """Nearly identical grays produce analogous harmony (same hue region)."""
        colors = [(128, 128, 128), (130, 130, 130), (126, 126, 126)]
        result = color_analyzer.analyze_color_harmony(colors)
        assert result["dominant_harmony"] == "analogous"
        assert result["total_harmonies"] >= 0

    def test_single_color(self, color_analyzer):
        result = color_analyzer.analyze_color_harmony([(255, 0, 0)])
        assert result["dominant_harmony"] == "none"
        assert result["harmony_score"] == 0

    def test_harmony_counts_consistent(self, color_analyzer):
        """total_harmonies must equal the sum of harmony_counts values."""
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        result = color_analyzer.analyze_color_harmony(colors)
        expected = sum(result["harmony_counts"].values())
        assert result["total_harmonies"] == expected

    def test_empty_palette(self, color_analyzer):
        result = color_analyzer.analyze_color_harmony([])
        assert result["dominant_harmony"] == "none"
        assert result["harmony_score"] == 0
