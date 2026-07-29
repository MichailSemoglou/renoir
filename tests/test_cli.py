"""
Tests for the renoir CLI.

Uses click.testing.CliRunner for isolated invocation.
"""

import json
import sys
from io import BytesIO

import pytest
from PIL import Image


@pytest.fixture
def sample_image():
    """A 10 x 10 solid red PIL image."""
    return Image.new("RGB", (10, 10), color=(255, 0, 0))


@pytest.fixture
def sample_image_path(tmp_path, sample_image):
    """Write *sample_image* to a temporary PNG and return the path."""
    path = tmp_path / "test.png"
    sample_image.save(path)
    return str(path)


def _runner():
    from click.testing import CliRunner

    return CliRunner()


# ---------------------------------------------------------------------------
# artist
# ---------------------------------------------------------------------------


def test_artist_help():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["artist", "--help"])
    assert result.exit_code == 0
    assert "ARTIST_ID" in result.output


# ---------------------------------------------------------------------------
# extract
# ---------------------------------------------------------------------------


def test_extract_json_stdout(sample_image_path):
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["extract", sample_image_path, "--n-colors", "3"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert data["n_colors"] == 3
    assert len(data["colors"]) == 3
    for c in data["colors"]:
        assert "rgb" in c
        assert "hex" in c


def test_extract_css_stdout(sample_image_path):
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(
        cli, ["extract", sample_image_path, "--n-colors", "2", "--format", "css"]
    )
    assert result.exit_code == 0
    assert ":root {" in result.output
    assert "--palette-" in result.output


def test_extract_json_to_file(sample_image_path, tmp_path):
    from renoir.cli import cli

    runner = _runner()
    out = tmp_path / "out.json"
    result = runner.invoke(
        cli, ["extract", sample_image_path, "-o", str(out), "--n-colors", "2"]
    )
    assert result.exit_code == 0
    assert out.exists()
    with open(out) as f:
        assert json.load(f)


def test_extract_missing_file():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["extract", "/nonexistent/image.png"])
    assert result.exit_code != 0


# ---------------------------------------------------------------------------
# name
# ---------------------------------------------------------------------------


def test_name_hex():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["name", "#FF0000"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_name_rgb():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["name", "255,0,0"])
    assert result.exit_code == 0


def test_name_with_metadata():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["name", "#FF0000", "--metadata"])
    assert result.exit_code == 0
    data = json.loads(result.output)
    assert "name" in data


def test_name_bad_input():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["name", "not-a-color"])
    assert result.exit_code != 0


def test_name_vocabulary():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["name", "#FFFFFF", "--vocabulary", "xkcd"])
    assert result.exit_code == 0


# ---------------------------------------------------------------------------
# prompt
# ---------------------------------------------------------------------------


def test_prompt_basic(sample_image_path):
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["prompt", sample_image_path, "--n-colors", "3"])
    assert result.exit_code == 0
    assert len(result.output.strip()) > 0


def test_prompt_with_style(sample_image_path):
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(
        cli,
        [
            "prompt",
            sample_image_path,
            "--n-colors",
            "3",
            "--style",
            "impressionist",
            "--medium",
            "oil",
            "--mood",
            "serene",
        ],
    )
    assert result.exit_code == 0


def test_prompt_target_model(sample_image_path):
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(
        cli,
        ["prompt", sample_image_path, "--n-colors", "2", "--target-model", "dalle"],
    )
    assert result.exit_code == 0


def test_prompt_missing_image():
    from renoir.cli import cli

    runner = _runner()
    result = runner.invoke(cli, ["prompt", "/nonexistent/image.png"])
    assert result.exit_code != 0
