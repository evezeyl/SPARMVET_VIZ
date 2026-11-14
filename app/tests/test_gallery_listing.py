"""What the gallery lists and the lines it shows about what it left out (flags G-a, G-b; no silent error).

Pure function, no Shiny. Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_listing.py -q
"""
import json
import os
import shutil
import stat
from pathlib import Path

import pytest

from app.modules.gallery_examples import check_gallery_at_start, rebuild_gallery_index
from app.modules.gallery_listing import READ_ONLY_LINE, build_listing, read_listing

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
RECIPE = "data_analysis_recipe.yaml"

INDEX = {
    "registry": {"good": {"name": "Good", "path": "g/r.yaml"}, "bad": {"name": "Bad", "path": "b/r.yaml"}},
    "pivot": {"by_family": {"Comparison": ["good", "bad"], "Ranking": ["bad"]}},
}
REJECTED = {"bad": ["[PS04] unknown argument colr", "second reason"]}


def test_a_rejected_example_is_not_listed_even_if_the_old_index_lists_it():
    listing = build_listing(INDEX, REJECTED, "not_writable")
    assert list(listing.registry) == ["good"]
    assert listing.pivot["by_family"] == {"Comparison": ["good"]}
    assert "bad" not in json.dumps(listing.pivot)


def test_read_only_folder_returns_both_lines():
    listing = build_listing(INDEX, REJECTED, "not_writable")
    assert listing.notice[0] == "1 example(s) not shown, failed the check:"
    assert listing.notice[1] == "bad, [PS04] unknown argument colr."
    assert listing.notice[-1] == READ_ONLY_LINE == "The gallery folder is read-only, so the list was not rewritten."


def test_writable_folder_returns_the_reason_line_only():
    listing = build_listing(INDEX, REJECTED, "rewritten")
    assert listing.notice == ["1 example(s) not shown, failed the check:", "bad, [PS04] unknown argument colr."]


def test_nothing_rejected_means_no_block_even_when_read_only():
    listing = build_listing(INDEX, {}, "not_writable")
    assert listing.notice == [] and set(listing.registry) == {"good", "bad"}


def test_the_given_index_is_not_changed():
    before = json.dumps(INDEX, sort_keys=True)
    build_listing(INDEX, REJECTED, "rewritten")
    assert json.dumps(INDEX, sort_keys=True) == before


def test_a_missing_or_corrupt_index_gives_an_empty_listing(tmp_path):
    assert read_listing(tmp_path, {}, "unchanged").registry == {}
    (tmp_path / "gallery_index.json").write_text("{not json")
    assert read_listing(tmp_path, {}, "unchanged").registry == {}


@pytest.mark.skipif(os.geteuid() == 0, reason="root ignores folder permissions")
def test_real_read_only_gallery_with_a_failing_example_in_the_old_index(tmp_path):
    work = tmp_path / "gallery_data"
    shutil.copytree(SHIPPED / "bar_simple", work / "bar_simple")
    rebuild_gallery_index(work)
    shutil.copytree(work / "bar_simple", work / "bar_wrong")
    text = (work / "bar_wrong" / RECIPE).read_text().replace("bar_simple", "bar_wrong").replace("name: geom_bar", "name: geom_barr")
    (work / "bar_wrong" / RECIPE).write_text(text)
    # the old index lists bar_wrong, as an index written before the example broke would
    index = json.loads((work / "gallery_index.json").read_text())
    index["registry"]["bar_wrong"] = dict(index["registry"]["bar_simple"], name="Wrong")
    (work / "gallery_index.json").write_text(json.dumps(index))
    work.chmod(stat.S_IRUSR | stat.S_IXUSR)
    try:
        examples, status = check_gallery_at_start(work)
        assert status == "not_writable"
        listing = read_listing(work, examples.rejected, status)
    finally:
        work.chmod(stat.S_IRWXU)
    assert list(listing.registry) == ["bar_simple"]
    assert listing.notice[0].startswith("1 example(s) not shown") and listing.notice[1].startswith("bar_wrong, ")
    assert listing.notice[-1] == READ_ONLY_LINE
