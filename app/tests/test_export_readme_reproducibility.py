"""The README of the bundle and the first sentence of the notification tell what happened to the reproducibility part
(D-0050 "No silent error that is the rule."). The real download generator runs headless as in `test_export_download_path.py`.

Cases: box ticked and built; box ticked and the build raised (the folder holds only ERROR.txt); box ticked and built but a data
file could not be copied (`<id>_ERROR.txt`); box not ticked.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_readme_reproducibility.py -q
"""
import io
import zipfile
from unittest import mock

import pytest

from app.handlers import export_handlers
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import World
from app.tests.test_export_download_path import _download_function, _run


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _export(tmp_path, monkeypatch, box):
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    function = _download_function(world, view, notes, monkeypatch, extra_values={"export_include_reproducibility": box})
    zf = zipfile.ZipFile(io.BytesIO(_run(function)[0]))
    readme = zf.read(next(n for n in zf.namelist() if n.endswith("/README.txt"))).decode()
    line = next(ln for ln in readme.splitlines() if ln.startswith("Reproducibility  :"))
    repro_notes = [m for _t, m in notes if "Reproducibility part" in m or "reproducibility part" in m]
    return zf, line, repro_notes


def test_built_completely_says_included(tmp_path, monkeypatch):
    zf, line, notes = _export(tmp_path, monkeypatch, True)
    assert line.startswith("Reproducibility  : included (") and "INCOMPLETE" not in line and "NOT built" not in line
    assert len(notes) == 1 and notes[0].startswith("Reproducibility part: included (the full recipe and the data files)")


def test_a_build_that_raised_says_requested_and_not_built(tmp_path, monkeypatch):
    """Fails without the fix: the README said "included" while the folder held only ERROR.txt."""
    monkeypatch.setattr("app.handlers.export_handlers.bake_place_steps", mock.Mock(side_effect=ValueError("cannot translate")))
    zf, line, _notes = _export(tmp_path, monkeypatch, True)
    assert any(n.endswith("data_analysis_recipes_reproducibility/ERROR.txt") for n in zf.namelist())
    assert line.startswith("Reproducibility  : requested") and "NOT built" in line
    assert "data_analysis_recipes_reproducibility/ERROR.txt" in line and "included" not in line


def test_a_data_file_that_could_not_be_copied_says_incomplete(tmp_path, monkeypatch):
    """Fails without the fix: the README and the notification said "included (the full recipe and the data files)"."""
    real = export_handlers.build_export_provenance

    def with_a_missing_file(*a, **k):
        prov = real(*a, **k)
        prov["data_source_paths"] = {**prov["data_source_paths"], "gone": str(tmp_path / "does_not_exist.tsv")}
        return prov
    monkeypatch.setattr(export_handlers, "build_export_provenance", with_a_missing_file)
    zf, line, notes = _export(tmp_path, monkeypatch, True)
    assert any(n.endswith("data_reproducibility/gone_ERROR.txt") for n in zf.namelist())
    assert line.startswith("Reproducibility  : included but INCOMPLETE") and "gone" in line and "_ERROR.txt" in line
    assert len(notes) == 1 and "INCOMPLETE" in notes[0] and "gone" in notes[0]
    assert "the full recipe and the data files" not in notes[0]


def test_box_not_ticked_says_not_included(tmp_path, monkeypatch):
    zf, line, notes = _export(tmp_path, monkeypatch, False)
    assert line.startswith("Reproducibility  : not included (") and notes == []
