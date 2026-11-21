"""The index holds no path that depends on where the gallery folder sits on the machine, and the rule for repeated names is pinned.

A start of the app gives the gallery folder as an absolute path; the committed index holds paths relative to the project root.
The start must find them equal and leave the tracked file untouched (finding B-1 of the review).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_index_paths.py -q
"""
import hashlib
import json
import os
import shutil
from pathlib import Path

import pytest

from app.modules.gallery_examples import check_gallery, check_gallery_at_start

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
RECIPE = "data_analysis_recipe.yaml"
NAMES = ("bar_simple", "point_simple")


@pytest.fixture
def work(tmp_path, monkeypatch):
    """A copy of the gallery at <tmp>/assets/gallery_data with the committed index copied as it is; cwd is <tmp> (the project root)."""
    folder = tmp_path / "assets" / "gallery_data"
    for name in NAMES:
        shutil.copytree(SHIPPED / name, folder / name)
    committed = json.loads((SHIPPED / "gallery_index.json").read_text())
    registry = {name: committed["registry"][name] for name in NAMES}
    pivot = {axis: {term: [n for n in ids if n in NAMES] for term, ids in terms.items()} for axis, terms in committed["pivot"].items()}
    pivot = {axis: {term: ids for term, ids in terms.items() if ids} for axis, terms in pivot.items()}
    index = {**committed, "registry": registry, "pivot": pivot, "metadata": {**committed["metadata"], "count": len(NAMES)}}
    (folder / "gallery_index.json").write_text(json.dumps(index, indent=2, ensure_ascii=False), encoding="utf-8")
    monkeypatch.chdir(tmp_path)
    return folder


def _state(folder: Path):
    path = folder / "gallery_index.json"
    return hashlib.sha256(path.read_bytes()).hexdigest(), path.stat().st_mtime_ns


@pytest.mark.parametrize("form", ["absolute", "relative"])
def test_a_start_from_a_committed_style_index_leaves_it_untouched(work, form):
    folder = work if form == "absolute" else Path("assets/gallery_data")
    before = _state(work)
    _, status = check_gallery_at_start(folder)
    assert status == "unchanged"
    assert _state(work) == before


def test_no_value_of_a_built_index_depends_on_the_machine(work):
    (work / "gallery_index.json").unlink()
    check_gallery_at_start(work)  # absolute folder: writes the index
    text = (work / "gallery_index.json").read_text()
    index = json.loads(text)
    for entry in index["registry"].values():
        assert entry["path"] == f"assets/gallery_data/{Path(entry['path']).parent.name}/{RECIPE}"
        assert not entry["path"].startswith("/")
    assert str(work.parent.parent) not in text


def test_the_index_is_equal_for_an_absolute_and_a_relative_folder(work):
    (work / "gallery_index.json").unlink()
    check_gallery_at_start(work)
    absolute = json.loads((work / "gallery_index.json").read_text())
    (work / "gallery_index.json").unlink()
    check_gallery_at_start("assets/gallery_data")
    relative = json.loads((work / "gallery_index.json").read_text())
    for index in (absolute, relative):
        index["metadata"].pop("generated_at")
    assert absolute == relative


def test_the_rule_for_a_repeated_name_or_plot_id_is_pinned(work):
    """PROVISIONAL rule (not decided by the owner): the first example in folder-name order is kept, the later one is left out."""
    shutil.copytree(work / "bar_simple", work / "aa_copy")  # same name and same plot id, sorts earlier
    text = (work / "aa_copy" / RECIPE).read_text().replace("id: bar_simple\n", "id: aa_copy\n").replace("gallery_data/bar_simple/", "gallery_data/aa_copy/")
    (work / "aa_copy" / RECIPE).write_text(text)
    examples = check_gallery(work)
    assert "aa_copy" in examples.accepted and "bar_simple" in examples.rejected
    shutil.rmtree(work / "aa_copy")
    shutil.copytree(work / "bar_simple", work / "zz_copy")
    # another plot id, the same name: only the name repeats
    (work / "zz_copy" / RECIPE).write_text(text.replace("id: aa_copy\n", "id: zz_copy\n").replace("gallery_data/aa_copy/", "gallery_data/zz_copy/").replace("bar_simple:", "zz_copy:"))
    examples = check_gallery(work)
    assert "bar_simple" in examples.accepted and "zz_copy" in examples.rejected
