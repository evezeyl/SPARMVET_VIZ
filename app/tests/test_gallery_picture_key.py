"""The key that proves the stored picture of a Gallery example is current (D-0400, built on branch).

Headless, no drawing. Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_picture_key.py -q
"""
import json
import shutil
from pathlib import Path

import pytest

from app.modules.gallery_listing import FAILED_LINE, build_listing
from viz_gallery.picture_key import (KEY_FILE, key_of, picture_key_parts, picture_status, stale_pictures,
                                     write_picture_key)

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
NAMES = sorted(d.name for d in SHIPPED.iterdir() if d.is_dir())


@pytest.fixture
def example(tmp_path):
    folder = tmp_path / "bar_simple"
    shutil.copytree(SHIPPED / "bar_simple", folder)
    write_picture_key(folder, picture_key_parts(folder, plotnine="1.0"))
    return folder


def test_nothing_changed_the_picture_is_current(example):
    assert picture_status(example, plotnine="1.0") == (True, "")


def test_the_key_is_the_same_twice(example):
    assert key_of(picture_key_parts(example, "1.0")) == key_of(picture_key_parts(example, "1.0"))


def test_a_changed_recipe_makes_it_not_current(example):
    recipe = example / "data_analysis_recipe.yaml"
    recipe.write_text(recipe.read_text(encoding="utf-8") + "\n# edited\n", encoding="utf-8")
    current, reason = picture_status(example, plotnine="1.0")
    assert not current and "recipe" in reason and "data" not in reason


def test_changed_data_makes_it_not_current(example):
    data = example / "example_data.tsv"
    data.write_bytes(data.read_bytes() + b"\n")
    current, reason = picture_status(example, plotnine="1.0")
    assert not current and "data" in reason and "recipe" not in reason


def test_another_plotnine_version_makes_it_not_current(example):
    current, reason = picture_status(example, plotnine="1.1")
    assert not current and "plotnine" in reason


def test_the_meta_text_and_the_picture_are_not_in_the_key(example):
    (example / "example_meta.md").write_text("another text", encoding="utf-8")
    (example / "preview_plot.png").write_bytes(b"x")
    assert picture_status(example, plotnine="1.0")[0] is True


def test_a_missing_key_file_is_reported_not_raised(example):
    (example / KEY_FILE).unlink()
    current, reason = picture_status(example, plotnine="1.0")
    assert not current and "no key" in reason


@pytest.mark.parametrize("content", ["", "not json {", "[]", '{"key": 1}', '{"key": "a", "parts": {"recipe": "x"}}'])
def test_an_unreadable_key_file_is_reported_not_raised(example, content):
    (example / KEY_FILE).write_text(content, encoding="utf-8")
    current, reason = picture_status(example, plotnine="1.0")
    assert not current and "cannot be read" in reason


def test_a_key_that_was_edited_by_hand_is_not_trusted(example):
    stored = json.loads((example / KEY_FILE).read_text())
    stored["parts"]["plotnine"] = "9.9"
    (example / KEY_FILE).write_text(json.dumps(stored))
    assert picture_status(example, plotnine="9.9")[0] is False


def test_a_key_file_that_is_a_folder_or_a_missing_data_file_does_not_crash(example):
    (example / "example_data.tsv").unlink()
    assert picture_status(example, plotnine="1.0")[0] is False
    (example / KEY_FILE).unlink()
    (example / KEY_FILE).mkdir()
    assert picture_status(example, plotnine="1.0")[0] is False


def test_all_34_shipped_examples_are_current():
    assert len(NAMES) == 34
    assert stale_pictures(SHIPPED, NAMES) == {}


def test_no_shipped_recipe_includes_another_file():
    """The key reads the recipe file and the data file only; an include would be missed."""
    for name in NAMES:
        assert "!include" not in (SHIPPED / name / "data_analysis_recipe.yaml").read_text(encoding="utf-8"), name
        assert f"./assets/gallery_data/{name}/example_data.tsv" in (SHIPPED / name / "data_analysis_recipe.yaml").read_text(encoding="utf-8"), name


def test_the_notice_names_a_stale_example_and_keeps_it_listed():
    index = {"registry": {"a": {"name": "A"}, "b": {"name": "B"}}, "pivot": {}}
    stale = {"b": "the data changed since it was drawn"}
    listing = build_listing(index, {}, "unchanged", stale)
    assert set(listing.registry) == {"a", "b"}
    assert listing.notice == ["1 example(s) shown with a picture that is not current:",
                              "b: the picture is not current (the data changed since it was drawn)."]
    assert listing.blocks == [("1 example(s) shown with a picture that is not current:", [listing.notice[1]])]


def test_no_stale_picture_no_extra_line_and_a_rejected_example_is_not_repeated():
    index = {"registry": {"a": {"name": "A"}}, "pivot": {}}
    assert build_listing(index, {}, "unchanged", {}).notice == []
    notice = build_listing(index, {"b": ["bad"]}, "unchanged", {"b": "x"}).notice
    assert all("not current" not in line for line in notice)


def test_stale_pictures_finds_the_changed_one_in_a_real_folder(tmp_path):
    gallery = tmp_path / "g"
    for name in ("bar_simple", "dumbbell"):
        shutil.copytree(SHIPPED / name, gallery / name)
    (gallery / "dumbbell" / "example_data.tsv").write_bytes((gallery / "dumbbell" / "example_data.tsv").read_bytes() + b"\n")
    assert list(stale_pictures(gallery, ["bar_simple", "dumbbell"])) == ["dumbbell"]


def test_a_line_that_ends_with_a_colon_is_not_a_title():
    index = {"registry": {"a": {"name": "A"}}, "pivot": {}}
    listing = build_listing(index, {"bad": ["unexpected value:"]}, "unchanged")
    (title, lines), = listing.blocks
    assert title == "1 example(s) not shown, failed the check:"
    assert lines == ["bad, unexpected value:."] and lines[0].endswith(":.") is True
    lone = build_listing(index, {}, "failed").blocks
    assert lone == [(None, [FAILED_LINE])]
