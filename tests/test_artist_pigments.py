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
        """The published dataset describes exactly 56 pigments."""
        assert len(pigments) == 56

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


class TestVerifiedEntries:
    """Value-level regression checks for externally verified corrections."""

    EXPECTED = {
        "Lead White": ("PW1", -400),
        "Carmine": ("NR4", 1520),
        "Naples Yellow": ("PY41", -500),
        "Olive Green": (None, 1900),
        "Indigo": ("NB1", -2000),
        "Sap Green": ("NG2", 1600),
        "Sepia": ("NBr9", 1780),
        "Venetian Red": ("PR102", -40000),
        "Indian Red": ("PR102", -40000),
        "Vandyke Brown": ("NBr8", 1600),
        "Ultramarine Blue": ("PB29", 600),
        "Cadmium Orange": ("PO20", 1907),
        "Terre Verte": ("PG23", -100),
        "Hansa Yellow": ("PY1", 1910),
        "Titanium White": ("PW6", 1921),
        "Permanent Green Light": (None, 1938),
        "Hooker's Green": (None, 1820),
        "Payne's Grey": (None, 1780),
        "Azurite": ("PB30", -3000),
        "Smalt": ("PB32", 1500),
        "Verdigris": ("PG20", -300),
        "Malachite": ("PG39", -3000),
    }

    def test_verified_ci_names_and_dates(self, pigments):
        by_name = {p["name"]: p for p in pigments}
        for name, (ci, year) in self.EXPECTED.items():
            entry = by_name[name]
            assert entry["ci_name"] == ci, name
            assert entry["year_introduced"] == year, name

    def test_manganese_blue_discontinued(self, pigments):
        mb = next(p for p in pigments if p["name"] == "Manganese Blue")
        assert mb["year_discontinued"] == 1990

    def test_reference_colors(self, pigments):
        by_name = {p["name"]: p for p in pigments}
        assert by_name["Quinacridone Red"]["hex"] == "#EF3753"
        assert by_name["Titanium White"]["hex"] == "#E4E4E4"
