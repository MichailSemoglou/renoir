"""
Basic tests for the renoir package.

These tests can be expanded as the package develops.
"""

import pytest
from unittest.mock import patch
from renoir import (
    ArtistAnalyzer,
    quick_analysis,
    check_visualization_support,
    ColorNamer,
)


def test_artist_analyzer_initialization():
    """Test that the analyzer initializes correctly."""
    analyzer = ArtistAnalyzer()
    assert analyzer._dataset is None  # Dataset loaded lazily


@pytest.mark.integration
@pytest.mark.skip(reason="Requires 66GB WikiArt dataset download")
def test_extract_artist_works():
    """Test extracting works for a specific artist."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works("pierre-auguste-renoir", limit=5)
    assert isinstance(works, list)
    assert len(works) > 0
    assert len(works) <= 5

    # Check that all works have required keys
    for work in works:
        assert "artist" in work
        assert "image" in work


@pytest.mark.integration
@pytest.mark.skip(reason="Requires 66GB WikiArt dataset download")
def test_analyze_genres():
    """Test genre analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works("pierre-auguste-renoir", limit=10)
    genres = analyzer.analyze_genres(works)

    assert isinstance(genres, list)
    assert len(genres) > 0
    # Each genre should be a tuple of (name, count)
    for genre_tuple in genres:
        assert isinstance(genre_tuple, tuple)
        assert len(genre_tuple) == 2
        assert isinstance(genre_tuple[0], str)
        assert isinstance(genre_tuple[1], int)


@pytest.mark.integration
@pytest.mark.skip(reason="Requires 66GB WikiArt dataset download")
def test_analyze_styles():
    """Test style analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works("pierre-auguste-renoir", limit=10)
    styles = analyzer.analyze_styles(works)

    assert isinstance(styles, list)
    assert len(styles) > 0
    # Each style should be a tuple of (name, count)
    for style_tuple in styles:
        assert isinstance(style_tuple, tuple)
        assert len(style_tuple) == 2
        assert isinstance(style_tuple[0], str)
        assert isinstance(style_tuple[1], int)


@pytest.mark.integration
@pytest.mark.skip(reason="Requires 66GB WikiArt dataset download")
def test_analyze_temporal_distribution():
    """Test temporal distribution analysis."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works("pierre-auguste-renoir", limit=10)
    temporal = analyzer.analyze_temporal_distribution(works)

    assert isinstance(temporal, dict)
    # Keys should be decades (integers)
    for decade, count in temporal.items():
        assert isinstance(decade, int)
        assert isinstance(count, int)
        assert decade % 10 == 0  # Should be a decade


@pytest.mark.integration
@pytest.mark.skip(reason="Requires 66GB WikiArt dataset download")
def test_get_work_summary():
    """Test work summary generation."""
    analyzer = ArtistAnalyzer()
    works = analyzer.extract_artist_works("pierre-auguste-renoir", limit=10)
    summary = analyzer.get_work_summary(works)

    assert isinstance(summary, dict)
    assert "total_works" in summary
    assert "artist" in summary
    assert "primary_style" in summary
    assert "primary_genre" in summary
    assert "date_range" in summary
    assert summary["total_works"] == len(works)


@pytest.mark.integration
@pytest.mark.skip(reason="Requires 66GB WikiArt dataset download")
def test_quick_analysis():
    """Test quick analysis function."""
    works = quick_analysis("claude-monet", limit=5, show_summary=False)
    assert isinstance(works, list)
    assert len(works) > 0
    assert len(works) <= 5


def test_visualization_support():
    """Test visualization support detection."""
    # This will return True or False depending on whether matplotlib is installed
    result = check_visualization_support()
    assert isinstance(result, bool)


def test_visualization_support_unavailable(capsys):
    """Test check_visualization_support when matplotlib is not available."""
    with patch("renoir.VISUALIZATION_AVAILABLE", False):
        result = check_visualization_support()
    assert result is False
    captured = capsys.readouterr()
    assert "not installed" in captured.out or "Visualization" in captured.out


def test_visualization_methods_exist():
    """Test that visualization methods exist on ArtistAnalyzer."""
    analyzer = ArtistAnalyzer()

    # Check that visualization methods exist
    assert hasattr(analyzer, "plot_genre_distribution")
    assert hasattr(analyzer, "plot_style_distribution")
    assert hasattr(analyzer, "compare_artists_genres")
    assert hasattr(analyzer, "create_artist_overview")
    assert hasattr(analyzer, "_check_visualization_available")


def test_color_namer_exported():
    """ColorNamer should be importable from the top-level renoir package."""
    assert ColorNamer is not None


def test_visualization_check():
    """Test the visualization availability check."""
    analyzer = ArtistAnalyzer()
    result = analyzer._check_visualization_available()
    assert isinstance(result, bool)


def test_empty_works_handling():
    """Test that methods handle empty works lists gracefully."""
    analyzer = ArtistAnalyzer()

    empty_works = []

    # These should not raise errors
    genres = analyzer.analyze_genres(empty_works)
    assert genres == []

    styles = analyzer.analyze_styles(empty_works)
    assert styles == []

    temporal = analyzer.analyze_temporal_distribution(empty_works)
    assert temporal == {}

    summary = analyzer.get_work_summary(empty_works)
    assert summary["total_works"] == 0


# --- Tests using mock data (no dataset download) ---

MOCK_WORKS = [
    {
        "artist": "claude-monet",
        "genre": "landscape",
        "style": "Impressionism",
        "date": 1872,
    },
    {
        "artist": "claude-monet",
        "genre": "landscape",
        "style": "Impressionism",
        "date": 1880,
    },
    {
        "artist": "claude-monet",
        "genre": "portrait",
        "style": "Impressionism",
        "date": 1875,
    },
    {
        "artist": "claude-monet",
        "genre": "landscape",
        "style": "Realism",
        "date": "1868",
    },
    {
        "artist": "claude-monet",
        "genre": "cityscape",
        "style": "Impressionism",
        "date": 1899,
    },
]


class TestAnalyzeGenresWithData:
    def test_genre_counts(self):
        analyzer = ArtistAnalyzer()
        genres = analyzer.analyze_genres(MOCK_WORKS)
        assert genres[0] == ("landscape", 3)
        assert ("portrait", 1) in genres
        assert ("cityscape", 1) in genres

    def test_invalid_type_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.analyze_genres("not a list")

    def test_non_dict_item_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(TypeError):
            analyzer.analyze_genres([{"genre": "landscape"}, "bad"])


class TestAnalyzeStylesWithData:
    def test_style_counts(self):
        analyzer = ArtistAnalyzer()
        styles = analyzer.analyze_styles(MOCK_WORKS)
        assert styles[0] == ("Impressionism", 4)
        assert ("Realism", 1) in styles

    def test_invalid_type_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.analyze_styles(42)

    def test_non_dict_item_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(TypeError):
            analyzer.analyze_styles([{"style": "x"}, 123])


class TestAnalyzeTemporalDistribution:
    def test_decades(self):
        analyzer = ArtistAnalyzer()
        temporal = analyzer.analyze_temporal_distribution(MOCK_WORKS)
        assert temporal[1870] == 2  # 1872, 1875
        assert temporal[1880] == 1
        assert temporal[1860] == 1  # "1868"
        assert temporal[1890] == 1

    def test_missing_dates(self):
        analyzer = ArtistAnalyzer()
        works = [{"artist": "x"}, {"artist": "y", "date": "invalid"}]
        temporal = analyzer.analyze_temporal_distribution(works)
        assert temporal == {}


class TestGetWorkSummary:
    def test_summary_with_data(self):
        analyzer = ArtistAnalyzer()
        summary = analyzer.get_work_summary(MOCK_WORKS)
        assert summary["total_works"] == 5
        assert summary["primary_style"] == "Impressionism"
        assert summary["primary_genre"] == "landscape"
        assert summary["date_range"] == (1868, 1899)
        assert "all_genres" in summary
        assert "all_styles" in summary

    def test_summary_no_dates(self):
        analyzer = ArtistAnalyzer()
        works = [{"artist": "x", "genre": "landscape", "style": "Realism"}]
        summary = analyzer.get_work_summary(works)
        assert summary["date_range"] is None


class TestExtractArtistWorksValidation:
    def test_empty_name_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.extract_artist_works("")

    def test_whitespace_name_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.extract_artist_works("   ")

    def test_non_string_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.extract_artist_works(123)

    def test_negative_limit_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.extract_artist_works("monet", limit=-1)

    def test_non_int_limit_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.extract_artist_works("monet", limit=1.5)

    def test_zero_limit_returns_empty(self):
        analyzer = ArtistAnalyzer()
        result = analyzer.extract_artist_works("monet", limit=0)
        assert result == []


class TestExtractArtistWorksWithMock:
    def test_filter_by_artist(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = MOCK_WORKS
        works = analyzer.extract_artist_works("claude-monet")
        assert len(works) == 5

    def test_filter_with_limit(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = MOCK_WORKS
        works = analyzer.extract_artist_works("claude-monet", limit=2)
        assert len(works) == 2

    def test_artist_not_found(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = MOCK_WORKS
        works = analyzer.extract_artist_works("unknown-artist")
        assert works == []


class TestLoadDatasetFailure:
    def test_load_dataset_runtime_error(self):
        analyzer = ArtistAnalyzer()
        with patch(
            "renoir.analyzer.load_dataset", side_effect=Exception("network error")
        ):
            with pytest.raises(RuntimeError, match="Failed to load"):
                analyzer.extract_artist_works("monet")

    def test_load_dataset_caches(self):
        analyzer = ArtistAnalyzer()
        fake_ds = MOCK_WORKS
        with patch("renoir.analyzer.load_dataset", return_value=fake_ds) as mock_ld:
            analyzer.extract_artist_works("claude-monet")
            analyzer.extract_artist_works("claude-monet")
            assert mock_ld.call_count == 1  # cached after first call


class TestQuickAnalysis:
    def test_quick_analysis_with_mock(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = MOCK_WORKS
        with patch("renoir.analyzer.ArtistAnalyzer", return_value=analyzer):
            works = quick_analysis(
                "claude-monet", limit=3, show_summary=True, show_plots=False
            )
            assert isinstance(works, list)
            assert len(works) == 3


# --- Portfolio Color Signature API tests (Phase 5) ---


def _make_image(rgb, size=(20, 20)):
    """Create a solid-color PIL Image for testing."""
    from PIL import Image

    return Image.new("RGB", size, rgb)


class TestSampleWorks:
    """Test the internal _sample_works helper."""

    def test_temporal_sampling_spreads_across_decades(self):
        analyzer = ArtistAnalyzer()
        works = [
            {"date": 1870},
            {"date": 1872},
            {"date": 1880},
            {"date": 1885},
            {"date": 1890},
            {"date": 1899},
        ]
        selected, strategy = analyzer._sample_works(works, 4, "temporal", 42)
        assert strategy == "temporal"
        assert len(selected) == 4
        decades = {(w["date"] // 10) * 10 for w in selected}
        assert len(decades) >= 2  # should cover multiple decades

    def test_temporal_fallback_when_no_dates(self):
        analyzer = ArtistAnalyzer()
        works = [{"artist": "x"}, {"artist": "y"}, {"artist": "z"}]
        selected, strategy = analyzer._sample_works(works, 2, "temporal", 42)
        assert strategy == "random"
        assert len(selected) == 2

    def test_first_strategy(self):
        analyzer = ArtistAnalyzer()
        works = [{"date": i} for i in range(10)]
        selected, strategy = analyzer._sample_works(works, 3, "first", 42)
        assert strategy == "first"
        assert [w["date"] for w in selected] == [0, 1, 2]

    def test_random_strategy(self):
        analyzer = ArtistAnalyzer()
        works = [{"date": i} for i in range(10)]
        selected, strategy = analyzer._sample_works(works, 3, "random", 42)
        assert strategy == "random"
        assert len(selected) == 3
        assert len({id(w) for w in selected}) == 3  # no duplicates

    def test_invalid_strategy_raises(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError, match="strategy must be"):
            analyzer._sample_works([{}], 1, "invalid", 42)


class TestAggregatePalette:
    """Test the internal _aggregate_palette helper."""

    def test_aggregate_reduces_to_n_colors(self):
        analyzer = ArtistAnalyzer()
        colors = [(255, 0, 0), (0, 255, 0), (0, 0, 255), (255, 255, 0)]
        result = analyzer._aggregate_palette(colors, 2, 42)
        assert len(result) == 2
        for color in result:
            assert len(color) == 3
            assert all(0 <= c <= 255 for c in color)
            assert all(isinstance(c, int) for c in color)

    def test_aggregate_returns_unique_when_few_distinct(self):
        analyzer = ArtistAnalyzer()
        colors = [(255, 0, 0)] * 10 + [(0, 255, 0)] * 10
        result = analyzer._aggregate_palette(colors, 5, 42)
        # Should not force duplicate clusters
        assert len(result) == 2
        assert set(result).issubset({(255, 0, 0), (0, 255, 0)})

    def test_aggregate_empty(self):
        analyzer = ArtistAnalyzer()
        assert analyzer._aggregate_palette([], 3, 42) == []


class TestAnalyzeWorksColorSignature:
    """Test the lower-level signature method."""

    def test_full_temporal_signature(self):
        analyzer = ArtistAnalyzer()
        works = [
            {
                "image": _make_image((255, 0, 0)),
                "date": 1870,
                "title": "Red 1",
            },
            {
                "image": _make_image((0, 0, 255)),
                "date": 1885,
                "title": "Blue 1",
            },
            {
                "image": _make_image((0, 255, 0)),
                "date": 1895,
                "title": "Green 1",
            },
        ]
        result = analyzer.analyze_works_color_signature(
            works, n_colors=2, verbose=False
        )
        assert result["n_works_analyzed"] == 3
        assert len(result["palette"]) > 0
        assert "metrics" in result
        assert "diversity" in result["metrics"]
        assert set(result["by_period"].keys()) == {"1870", "1880", "1890"}
        assert result["date_range"] == (1870, 1895)

    def test_signature_without_dates(self):
        analyzer = ArtistAnalyzer()
        works = [
            {"image": _make_image((255, 0, 0))},
            {"image": _make_image((0, 0, 255))},
        ]
        result = analyzer.analyze_works_color_signature(
            works, n_colors=2, verbose=False
        )
        assert result["n_works_analyzed"] == 2
        assert len(result["palette"]) > 0
        assert result["by_period"] == {}
        assert result["date_range"] is None

    def test_signature_skips_missing_images(self):
        analyzer = ArtistAnalyzer()
        works = [
            {"image": _make_image((255, 0, 0))},
            {"date": 1880},  # no image
        ]
        result = analyzer.analyze_works_color_signature(
            works, n_colors=2, verbose=False
        )
        assert result["n_works_analyzed"] == 1

    def test_signature_empty_works(self):
        analyzer = ArtistAnalyzer()
        result = analyzer.analyze_works_color_signature([], verbose=False)
        assert result["n_works_analyzed"] == 0
        assert result["palette"] == []

    def test_signature_invalid_input(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.analyze_works_color_signature("not a list", verbose=False)
        with pytest.raises(TypeError):
            analyzer.analyze_works_color_signature(["not a dict"], verbose=False)


class TestArtistColorSignature:
    """Test the high-level artist color signature method."""

    def test_with_dated_mock_images(self):
        analyzer = ArtistAnalyzer()
        works = [
            {"artist": "test-artist", "image": _make_image((255, 0, 0)), "date": 1870},
            {"artist": "test-artist", "image": _make_image((0, 0, 255)), "date": 1880},
            {"artist": "test-artist", "image": _make_image((0, 255, 0)), "date": 1890},
        ]
        analyzer._dataset = works
        result = analyzer.artist_color_signature("test-artist", limit=3, verbose=False)
        assert result["artist"] == "test-artist"
        assert result["n_works_available"] == 3
        assert result["n_works_selected"] == 3
        assert result["effective_strategy"] == "temporal"
        assert len(result["palette"]) > 0

    def test_fallback_when_no_dates(self):
        analyzer = ArtistAnalyzer()
        works = [
            {"artist": "test-artist", "image": _make_image((255, 0, 0))},
            {"artist": "test-artist", "image": _make_image((0, 0, 255))},
        ]
        analyzer._dataset = works
        result = analyzer.artist_color_signature("test-artist", limit=2, verbose=False)
        assert result["effective_strategy"] == "random"
        assert result["n_works_selected"] == 2

    def test_empty_artist(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = []
        result = analyzer.artist_color_signature(
            "unknown-artist", limit=2, verbose=False
        )
        assert result["n_works_analyzed"] == 0
        assert result["palette"] == []

    def test_validation(self):
        analyzer = ArtistAnalyzer()
        with pytest.raises(ValueError):
            analyzer.artist_color_signature("", verbose=False)
        with pytest.raises(ValueError):
            analyzer.artist_color_signature("monet", limit=0, verbose=False)
        with pytest.raises(ValueError):
            analyzer.artist_color_signature("monet", limit=-1, verbose=False)

    def test_filters_out_other_artists(self):
        analyzer = ArtistAnalyzer()
        works = [
            {"artist": "test-artist", "image": _make_image((255, 0, 0)), "date": 1870},
            {"artist": "test-artist", "image": _make_image((0, 0, 255)), "date": 1880},
            {"artist": "other-artist", "image": _make_image((0, 255, 0)), "date": 1890},
        ]
        analyzer._dataset = works
        result = analyzer.artist_color_signature("test-artist", limit=10, verbose=False)
        assert result["n_works_available"] == 2
        assert result["n_works_selected"] == 2


class TestDatasetHelpers:
    """Tests for public dataset helper methods."""

    def test_load_dataset_returns_dataset(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = MOCK_WORKS
        result = analyzer.load_dataset()
        assert result is MOCK_WORKS

    def test_list_artists_with_mock_features(self):
        from unittest.mock import MagicMock

        analyzer = ArtistAnalyzer()
        mock_names = ["claude-monet", "pablo-picasso", "vincent-van-gogh"]
        mock_feature = MagicMock()
        mock_feature.names = mock_names
        mock_dataset = MagicMock()
        mock_dataset.features = {"artist": mock_feature}
        analyzer._dataset = mock_dataset

        artists = analyzer.list_artists()
        assert artists == mock_names

        limited = analyzer.list_artists(limit=2)
        assert limited == mock_names[:2]

    def test_list_artists_fallback_without_features(self):
        analyzer = ArtistAnalyzer()
        analyzer._dataset = MOCK_WORKS
        assert analyzer.list_artists() == []
