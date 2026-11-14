"""The gallery examples through the app's own path: the table, the picture, the comparison (spec section 9: G2, G5).

- the data contract: the table the app builds for an example equals the plain reading of its data file, so a
  generated type cannot change a picture silently;
- the picture: every example is drawn by ConfigManager, DataOrchestrator and VizFactory, at the one standard size;
- the comparison of a new picture with the committed one (identical, size only, differs, new), and what --apply writes.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_app_path.py -q
"""
import importlib.util
import shutil
import sys
from pathlib import Path

import polars as pl
import pytest
from PIL import Image

from app.modules.gallery_examples import PREVIEW_SIZE, example_table, render_example
from utils.errors import IngestionError

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
# The examples that cannot be standard recipes yet (the same list as libs/viz_gallery/tests/test_gallery_examples_are_recipes.py).
WAITING = {"beeswarm_sina"}

_spec = importlib.util.spec_from_file_location("gallery_previews", ROOT / "assets/scripts/gallery_previews.py")
previews = importlib.util.module_from_spec(_spec)
sys.modules["gallery_previews"] = previews
_spec.loader.exec_module(previews)


def _accepted_names():
    return sorted(d.name for d in SHIPPED.iterdir() if d.is_dir() and d.name not in WAITING)


# ---- the data contract and the picture ------------------------------------------------------------------------------------

@pytest.mark.parametrize("name", _accepted_names())
def test_the_table_of_an_example_equals_its_data_file_and_its_plot_is_drawn(name, tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    folder = SHIPPED / name
    plain = pl.read_csv(folder / "example_data.tsv", separator="\t", infer_schema_length=None)
    table = example_table(folder, tmp_path / "work")
    assert table.schema == plain.schema
    assert table.equals(plain)
    picture = render_example(folder, tmp_path / "work", tmp_path / f"{name}.png")
    with Image.open(picture) as image:
        assert image.size == (PREVIEW_SIZE["width"] * PREVIEW_SIZE["dpi"], PREVIEW_SIZE["height"] * PREVIEW_SIZE["dpi"])


def _project_with_example(tmp_path: Path, name: str = "bar_simple") -> Path:
    """A small project folder holding one shipped example; returns the example folder."""
    target = tmp_path / "assets" / "gallery_data" / name
    shutil.copytree(SHIPPED / name, target)
    return target


def test_an_example_whose_data_does_not_fit_its_contract_gets_no_picture(tmp_path, monkeypatch):
    folder = _project_with_example(tmp_path)
    monkeypatch.chdir(tmp_path)
    data = folder / "example_data.tsv"
    data.write_text(data.read_text().rstrip("\n") + "\nX\tE. coli\tBeta-lactam\tnot a number\n")
    with pytest.raises(IngestionError, match="not a number"):
        render_example(Path("assets/gallery_data/bar_simple"), tmp_path / "work", tmp_path / "out.png")
    assert not (tmp_path / "out.png").exists()


def test_an_example_without_its_data_file_gets_no_picture(tmp_path, monkeypatch):
    folder = _project_with_example(tmp_path)
    monkeypatch.chdir(tmp_path)
    (folder / "example_data.tsv").unlink()
    with pytest.raises(Exception):
        render_example(Path("assets/gallery_data/bar_simple"), tmp_path / "work", tmp_path / "out.png")
    assert not (tmp_path / "out.png").exists()


def test_two_examples_drawn_in_one_work_folder_stay_separate(tmp_path, monkeypatch):
    monkeypatch.chdir(ROOT)
    first = example_table(SHIPPED / "bar_simple", tmp_path / "work")
    second = example_table(SHIPPED / "line_simple", tmp_path / "work")
    again = example_table(SHIPPED / "bar_simple", tmp_path / "work")
    assert first.columns != second.columns and first.equals(again)


# ---- comparing a new picture with the committed one ---------------------------------------------------------------------

def _picture(path: Path, size=(40, 20), colour=(255, 255, 255), dot=None) -> Path:
    image = Image.new("RGB", size, colour)
    if dot:
        image.putpixel(dot, (0, 0, 0))
    image.save(path, dpi=(10, 10))
    return path


def _no_redraw(size, path):
    raise AssertionError("a picture of the same size is never drawn again")


def test_compare_identical_differs_and_new(tmp_path):
    new = _picture(tmp_path / "new.png")
    assert previews.compare("a", new, _picture(tmp_path / "same.png"), _no_redraw).verdict == "identical"
    changed = previews.compare("a", new, _picture(tmp_path / "dot.png", dot=(3, 3)), _no_redraw)
    assert changed.verdict == "differs" and changed.detail == "0.12% of the pixels" and not changed.content_unchanged
    assert previews.compare("a", new, tmp_path / "missing.png", _no_redraw).verdict == "new"


def test_compare_another_size_draws_again_at_the_old_size(tmp_path):
    new = _picture(tmp_path / "new.png", size=(48, 30))
    old = _picture(tmp_path / "old.png", size=(40, 30))
    asked = []

    def redraw_same(size, path):
        asked.append(size)
        return _picture(path, size=(40, 30))

    row = previews.compare("a", new, old, redraw_same)
    assert row.verdict == "size only" and row.content_unchanged and "40x30 before, 48x30 now" in row.detail
    assert asked == [{"width": 4.0, "height": 3.0, "dpi": 10}]
    row = previews.compare("a", new, old, lambda size, path: _picture(path, size=(40, 30), dot=(1, 1)))
    assert row.verdict == "differs" and "at the old size" in row.detail
    row = previews.compare("a", new, old, lambda size, path: _picture(path, size=(41, 30)))
    assert row.verdict == "differs" and "was not compared" in row.detail


def test_apply_writes_only_the_pictures_whose_content_did_not_change(tmp_path, monkeypatch):
    folder = _project_with_example(tmp_path)
    monkeypatch.chdir(tmp_path)
    gallery, out = Path("assets/gallery_data"), tmp_path / "out"
    committed = (folder / "preview_plot.png").read_bytes()
    first, = previews.run(gallery, out)
    assert first.name == "bar_simple" and (folder / "preview_plot.png").read_bytes() == committed   # a dry run writes nothing
    _picture(folder / "preview_plot.png", size=(960, 600))        # a committed picture with another content
    blank = (folder / "preview_plot.png").read_bytes()
    row, = previews.run(gallery, out, apply=True)
    assert row.verdict == "differs" and (folder / "preview_plot.png").read_bytes() == blank
    row, = previews.run(gallery, out, apply=True, changed=True)
    assert row.verdict == "differs" and (folder / "preview_plot.png").read_bytes() != blank
    (folder / "preview_thumb.png").unlink()
    row, = previews.run(gallery, out, apply=True)
    assert row.verdict == "identical" and (folder / "preview_thumb.png").is_file()
    (folder / "preview_plot.png").unlink()
    row, = previews.run(gallery, out)
    assert row.verdict == "error" and "GP05" in row.detail          # no picture: the example fails the check, nothing is drawn
    with pytest.raises(ValueError, match="no such example folder"):
        previews.run(gallery, out, only=["missing"])
