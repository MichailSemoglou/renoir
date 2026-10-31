"""
Schema validation tests for the artist pigments dataset.

Every entry in renoir/data/colors/artist_pigments.json is checked against
the field semantics documented in the deposit README and JSON Schema, so
malformed entries fail the build.
"""

import json
import re
from pathlib import Path

import pytest

DATA_PATH = (
    Path(__file__).parent.parent / "renoir" / "data" / "colors" / "artist_pigments.json"
)

FAMILIES = {
    "Black",
    "Blue",
    "Brown",
    "Green",
    "Grey",
    "Orange",
    "Red",
    "Violet",
    "White",
    "Yellow",
}

CI_NAME_PATTERN = re.compile(r"^[PN][A-Za-z]{1,2}\d+$")

REQUIRED_FIELDS = {
    "name",
    "hex",
    "rgb",
    "ci_name",
    "family",
    "description",
    "year_introduced",
}

ALLOWED_FIELDS = REQUIRED_FIELDS | {"year_discontinued"}


@pytest.fixture(scope="module")
def pigments():
    with open(DATA_PATH, encoding="utf-8") as f:
        return json.load(f)


class TestDatasetShape:
    """Test top-level structure of the dataset."""

    def test_entry_count(self, pigments):
        """The published dataset describes exactly 63 pigments."""
        assert len(pigments) == 63

    def test_names_are_unique(self, pigments):
        names = [p["name"] for p in pigments]
        assert len(names) == len(set(names))


class TestEntryFields:
    """Test that every entry conforms to the documented schema."""

    def test_required_fields_present(self, pigments):
        for p in pigments:
            assert REQUIRED_FIELDS <= set(p), p["name"]
            assert set(p) <= ALLOWED_FIELDS, p["name"]

    def test_hex_format(self, pigments):
        for p in pigments:
            assert re.fullmatch(r"#[0-9A-F]{6}", p["hex"]), p["name"]

    def test_rgb_matches_hex(self, pigments):
        for p in pigments:
            h = p["hex"].lstrip("#")
            expected = [int(h[i : i + 2], 16) for i in (0, 2, 4)]
            assert p["rgb"] == expected, p["name"]

    def test_family_vocabulary(self, pigments):
        for p in pigments:
            assert p["family"] in FAMILIES, p["name"]

    def test_ci_name_nullable(self, pigments):
        for p in pigments:
            ci = p["ci_name"]
            assert ci is None or CI_NAME_PATTERN.match(ci), p["name"]

    def test_years_are_integers(self, pigments):
        for p in pigments:
            assert type(p["year_introduced"]) is int, p["name"]
            if "year_discontinued" in p:
                assert type(p["year_discontinued"]) is int, p["name"]
                assert p["year_discontinued"] >= p["year_introduced"], p["name"]

    def test_descriptions_non_empty(self, pigments):
        for p in pigments:
            assert isinstance(p["description"], str) and p["description"].strip()


class TestPipelineIntegration:
    """Test that every entry round-trips through the naming pipeline."""

    def test_every_entry_matches_itself(self, pigments):
        from renoir.color import ColorNamer

        namer = ColorNamer(vocabulary="artist")
        for p in pigments:
            result = namer.name(tuple(p["rgb"]), return_metadata=True)
            assert result["name"] == p["name"], p["name"]


class TestEntryValues:
    """Value-level regression checks locking every entry in the dataset."""

    EXPECTED = {
        "Titanium White": ("PW6", 1921),
        "Zinc White": ("PW4", 1780),
        "Lead White": ("PW1", -400),
        "Cadmium Yellow Light": ("PY35", 1840),
        "Cadmium Yellow Deep": ("PY37", 1840),
        "Chrome Yellow": ("PY34", 1809),
        "Lemon Yellow": ("PY31", 1820),
        "Orpiment": ("PY39", -1500),
        "Yellow Ochre": ("PY43", -40000),
        "Raw Sienna": ("PBr7", -40000),
        "Burnt Sienna": ("PBr7", -40000),
        "Raw Umber": ("PBr7", -40000),
        "Burnt Umber": ("PBr7", -40000),
        "Cadmium Orange": ("PO20", 1907),
        "Realgar": ("PY39", -1500),
        "Cadmium Red Light": ("PR108", 1910),
        "Cadmium Red Deep": ("PR108", 1910),
        "Alizarin Crimson": ("PR83", 1868),
        "Vermilion": ("PR106", -3000),
        "Rose Madder": ("NR9", -1500),
        "Venetian Red": ("PR102", -40000),
        "Indian Red": ("PR102", -40000),
        "Quinacridone Magenta": ("PR122", 1958),
        "Dioxazine Purple": ("PV23", 1952),
        "Cobalt Violet": ("PV14", 1859),
        "Ultramarine Blue": ("PB29", 600),
        "Azurite": ("PB30", -3000),
        "Smalt": ("PB32", 1500),
        "Egyptian Blue": ("PB31", -3200),
        "Cobalt Blue": ("PB28", 1802),
        "Cerulean Blue": ("PB35", 1860),
        "Prussian Blue": ("PB27", 1704),
        "Phthalo Blue": ("PB15", 1935),
        "Manganese Blue": ("PB33", 1907),
        "Phthalo Green": ("PG7", 1938),
        "Viridian": ("PG18", 1838),
        "Emerald Green": ("PG21", 1814),
        "Chromium Oxide Green": ("PG17", 1840),
        "Verdigris": ("PG20", -300),
        "Malachite": ("PG39", -3000),
        "Sap Green": ("NG2", 1600),
        "Hooker's Green": (None, 1820),
        "Terre Verte": ("PG23", -100),
        "Naples Yellow": ("PY41", -500),
        "Aureolin": ("PY40", 1852),
        "Weld lake": ("NY2", -1000),
        "Payne's Grey": (None, 1780),
        "Ivory Black": ("PBk9", -40000),
        "Lamp Black": ("PBk6", -40000),
        "Mars Black": ("PBk11", 1920),
        "Charcoal Black": ("PBk8", -40000),
        "Sepia": ("NBr9", 1780),
        "Vandyke Brown": ("NBr8", 1600),
        "Mummy Brown": (None, 1550),
        "Bistre": ("NBr11", 1300),
        "Permanent Green Light": (None, 1938),
        "Olive Green": (None, 1900),
        "Cobalt Teal": ("PG50", 1930),
        "Indigo": ("NB1", -2000),
        "Carmine": ("NR4", 1523),
        "Quinacridone Red": ("PR209", 1958),
        "Transparent Red Oxide": ("PR101", 1980),
        "Hansa Yellow": ("PY1", 1910),
    }

    EXPECTED_HEX = {
        "Titanium White": "#E4E4E4",
        "Zinc White": "#FDFFF5",
        "Lead White": "#F6F4ED",
        "Cadmium Yellow Light": "#FFE303",
        "Cadmium Yellow Deep": "#FFA300",
        "Chrome Yellow": "#FFA700",
        "Lemon Yellow": "#FFF44F",
        "Orpiment": "#FFD764",
        "Yellow Ochre": "#CC7722",
        "Raw Sienna": "#D68A59",
        "Burnt Sienna": "#E97451",
        "Raw Umber": "#826644",
        "Burnt Umber": "#8A3324",
        "Cadmium Orange": "#FF6103",
        "Realgar": "#D9481C",
        "Cadmium Red Light": "#FF033E",
        "Cadmium Red Deep": "#B7282E",
        "Alizarin Crimson": "#E32636",
        "Vermilion": "#E34234",
        "Rose Madder": "#E0115F",
        "Venetian Red": "#C80815",
        "Indian Red": "#CD5C5C",
        "Quinacridone Magenta": "#8E3A59",
        "Dioxazine Purple": "#6A0DAD",
        "Cobalt Violet": "#8B00FF",
        "Ultramarine Blue": "#4166F5",
        "Azurite": "#0066CC",
        "Smalt": "#003399",
        "Egyptian Blue": "#1034A6",
        "Cobalt Blue": "#0047AB",
        "Cerulean Blue": "#2A52BE",
        "Prussian Blue": "#003153",
        "Phthalo Blue": "#000F89",
        "Manganese Blue": "#03A89E",
        "Phthalo Green": "#123524",
        "Viridian": "#40826D",
        "Emerald Green": "#50C878",
        "Chromium Oxide Green": "#5D7745",
        "Verdigris": "#43B3AE",
        "Malachite": "#3FCE68",
        "Sap Green": "#507D2A",
        "Hooker's Green": "#49796B",
        "Terre Verte": "#56614E",
        "Naples Yellow": "#FADA5E",
        "Aureolin": "#FDEE00",
        "Weld lake": "#EFE3A0",
        "Payne's Grey": "#536878",
        "Ivory Black": "#292421",
        "Lamp Black": "#1A1110",
        "Mars Black": "#0C0B0A",
        "Charcoal Black": "#36454F",
        "Sepia": "#704214",
        "Vandyke Brown": "#5E2E0C",
        "Mummy Brown": "#824B27",
        "Bistre": "#3D2B1F",
        "Permanent Green Light": "#7FCD91",
        "Olive Green": "#BAB86C",
        "Cobalt Teal": "#007BA7",
        "Indigo": "#4B0082",
        "Carmine": "#960018",
        "Quinacridone Red": "#EF3753",
        "Transparent Red Oxide": "#8D4E23",
        "Hansa Yellow": "#E9D66B",
    }

    EXPECTED_DISCONTINUED = {
        "Manganese Blue": 1990,
        "Mummy Brown": 1964,
    }

    def test_ci_names_and_dates(self, pigments):
        by_name = {p["name"]: p for p in pigments}
        assert set(by_name) == set(self.EXPECTED)
        for name, (ci, year) in self.EXPECTED.items():
            entry = by_name[name]
            assert entry["ci_name"] == ci, name
            assert entry["year_introduced"] == year, name

    def test_reference_colors(self, pigments):
        by_name = {p["name"]: p for p in pigments}
        assert set(by_name) == set(self.EXPECTED_HEX)
        for name, hex_value in self.EXPECTED_HEX.items():
            assert by_name[name]["hex"] == hex_value, name

    def test_discontinued_years(self, pigments):
        for p in pigments:
            expected = self.EXPECTED_DISCONTINUED.get(p["name"])
            if expected is None:
                assert "year_discontinued" not in p, p["name"]
            else:
                assert p["year_discontinued"] == expected, p["name"]
