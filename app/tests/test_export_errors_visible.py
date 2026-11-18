"""An export tells the user what it could not write (VERIF-FIX-2, places 11 to 14 and the `*_ERROR.txt` files;
D-0050 "No silent error that is the rule.").

Before: the data source paths that could not be read, the keys that could not be written into a picture, a reproducibility step that
failed and a Quarto render that failed were swallowed or written only INSIDE the zip (a file nobody opens before the user trusts the
export). What the export does is not changed (it still goes on and still writes the same files); the user is told on screen, with a
Suggestion:. The real download generator runs headless as in `test_export_download_path.py`.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION E1  `build_export_provenance` swallows the data source error again (no problem in the result)
  MUTATION E2  the generator does not show the problems of the provenance
  MUTATION E3  `_embed_png_provenance` swallows the error again
  MUTATION E4  `_embed_svg_provenance` swallows the error again
  MUTATION E5  the generator does not tell the pictures that got no keys
  MUTATION E6  the reproducibility failure is only written in the zip
  MUTATION E7  the Quarto failure is only written in the zip
  MUTATION E8  the `*_ERROR.txt` files are not summarised on screen

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_errors_visible.py -q
"""
import datetime
import io
import zipfile
from types import SimpleNamespace
from unittest import mock

import pytest

from app.handlers import export_handlers
from app.handlers.export_handlers import _embed_png_provenance, _embed_svg_provenance, build_export_provenance
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import World
from app.tests.test_export_download_path import _download_function, _run


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _prov(orchestrator):
    return build_export_provenance(
        now=datetime.datetime(2026, 11, 16, 12, 0, 0), data_analysis_recipe_id="tiny", safe_name="eve", app_features="qa",
        preset="web", dpi=300, active_tier="T2", all_plots=[],
        tiers_exported=["T1"], data_analysis_recipe_sha="m" * 64, data_sha="d" * 64,
        bootloader=SimpleNamespace(available_data_analysis_recipes={}), orchestrator=orchestrator)


def _bundle(world, notes, monkeypatch, extra_values=None):
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, notes, monkeypatch, extra_values=extra_values))
    assert len(yielded) == 1
    return zipfile.ZipFile(io.BytesIO(yielded[0]))


def _texts(notes, kind):
    return [m for t, m in notes if t == kind]


# -- place 11: the data source paths -----------------------------------------------------------------------------------------

def test_data_source_paths_that_cannot_be_read_are_a_problem_of_the_provenance():
    """MUTATION E1 fails here."""
    class Failing:
        def get_source_files(self, recipe_id):
            raise OSError("the data folder cannot be listed")
    prov = _prov(Failing())
    assert prov["data_source_paths"] == {}, "what is recorded is as before"
    assert len(prov["problems"]) == 1, prov["problems"]
    text = prov["problems"][0]
    assert "data folder cannot be listed" in text and "data file" in text and ". Suggestion:" in text, text


def test_data_source_paths_that_can_be_read_are_no_problem():
    """The control."""
    prov = _prov(SimpleNamespace(get_source_files=lambda recipe_id: {"T": "/data/T.tsv"}))
    assert prov["data_source_paths"] == {"T": "/data/T.tsv"} and prov["problems"] == []


def test_the_generator_shows_the_problems_of_the_provenance(tmp_path, monkeypatch):
    """MUTATION E2 fails here."""
    real = export_handlers.build_export_provenance
    monkeypatch.setattr(export_handlers, "build_export_provenance",
                        lambda **kw: real(**{**kw, "orchestrator": SimpleNamespace(
                            get_source_files=mock.Mock(side_effect=OSError("the data folder cannot be listed")))}))
    notes = []
    _bundle(World(tmp_path), notes, monkeypatch)
    warnings = _texts(notes, "warning")
    assert any("data folder cannot be listed" in m and ". Suggestion:" in m for m in warnings), notes


# -- place 12: the keys in a picture ---------------------------------------------------------------------------------

def test_a_picture_that_cannot_take_the_keys_is_still_returned_and_the_error_is_given_to_the_caller():
    """MUTATION E3 and MUTATION E4 fail here."""
    prov = {"data_analysis_recipe_id": "tiny"}
    problems = []
    assert _embed_png_provenance(b"this is not a png", prov, "p", "C", on_problem=problems.append) == b"this is not a png"
    assert _embed_svg_provenance(b"<svg", prov, "p", "C", on_problem=problems.append) == b"<svg"
    assert len(problems) == 2 and all(isinstance(p, Exception) for p in problems), problems


def test_a_picture_that_takes_the_keys_reports_nothing():
    """The control."""
    from PIL import Image
    out = io.BytesIO()
    Image.new("RGB", (4, 4)).save(out, format="PNG")
    problems = []
    result = _embed_png_provenance(out.getvalue(), {"data_analysis_recipe_id": "tiny"}, "p", "C", on_problem=problems.append)
    assert problems == [] and result != out.getvalue()
    assert _embed_png_provenance(b"not a png", {}, "p", "C") == b"not a png", "no callback: as before"


def test_the_generator_tells_which_pictures_got_no_keys(tmp_path, monkeypatch):
    """MUTATION E5 fails here: one text for all of them, not one per picture."""
    def failing(raw, prov, plot_id, ds="", on_problem=None):
        on_problem(RuntimeError("PIL is not installed"))
        return raw
    monkeypatch.setattr(export_handlers, "_embed_png_provenance", failing)
    notes = []
    _bundle(World(tmp_path), notes, monkeypatch)
    warnings = [m for m in _texts(notes, "warning") if "keys" in m and "picture" in m]
    assert len(warnings) == 1 and "PIL is not installed" in warnings[0] and "'p'" in warnings[0], notes
    assert ". Suggestion:" in warnings[0]


# -- place 13: the reproducibility step ------------------------------------------------------------------------------

def test_a_reproducibility_step_that_fails_is_told(tmp_path, monkeypatch):
    """MUTATION E6 fails here. Before: ERROR.txt inside the zip and nothing on the screen."""
    monkeypatch.setattr("blueprint_arch.t3_translator.build_mode2_recipe", mock.Mock(side_effect=ValueError("cannot translate")))
    notes = []
    archive = _bundle(World(tmp_path), notes, monkeypatch, {"export_include_reproducibility": True})
    assert any(n.endswith("data_analysis_recipes_reproducibility/ERROR.txt") for n in archive.namelist()), "as before"
    warnings = [m for m in _texts(notes, "warning") + _texts(notes, "error") if "reproducibility" in m and "cannot translate" in m]
    assert len(warnings) == 1 and ". Suggestion:" in warnings[0], notes


def test_a_reproducibility_step_that_works_is_not_told(tmp_path, monkeypatch):
    """The control."""
    notes = []
    archive = _bundle(World(tmp_path), notes, monkeypatch, {"export_include_reproducibility": True})
    assert any("data_analysis_recipes_reproducibility/tiny.yaml" in n for n in archive.namelist())
    assert not [m for m in notes if "could not be built" in m[1]]


# -- place 14: Quarto ----------------------------------------------------------------------------------------------------

def test_a_quarto_render_that_fails_is_told_and_the_source_stays_in_the_bundle(tmp_path, monkeypatch):
    """MUTATION E7 fails here. The harness lets `quarto render` fail with 'no render in this test'."""
    notes = []
    archive = _bundle(World(tmp_path), notes, monkeypatch)
    names = archive.namelist()
    assert any(n.endswith("report.qmd") for n in names) and any(n.endswith("report_RENDER_FAILED.txt") for n in names), "as before"
    warnings = [m for m in _texts(notes, "warning") if "Quarto" in m]
    assert len(warnings) == 1 and "no render in this test" in warnings[0] and "report.qmd" in warnings[0], notes
    assert ". Suggestion:" in warnings[0]


def test_a_quarto_that_is_not_installed_is_told_with_its_own_words(tmp_path, monkeypatch):
    import subprocess

    def missing(args, *a, **k):
        raise FileNotFoundError(2, "No such file or directory: 'quarto'")
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    function = _download_function(world, view, notes, monkeypatch)
    monkeypatch.setattr(subprocess, "run", missing)
    _run(function)
    warnings = [m for m in _texts(notes, "warning") if "Quarto" in m]
    assert len(warnings) == 1 and "quarto" in warnings[0].lower() and "install" in warnings[0].lower(), notes


# -- the `*_ERROR.txt` files -----------------------------------------------------------------------------------------

def test_the_error_files_of_the_zip_are_summarised_on_screen(tmp_path, monkeypatch):
    """MUTATION E8 fails here. A plot or a table that fails is written as *_ERROR.txt inside the zip (still the case); before,
    the user was told nothing when the export finished."""
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    function = _download_function(world, view, notes, monkeypatch)
    real = world.orch.materialize_tier1
    monkeypatch.setattr(world.orch, "materialize_tier1", mock.Mock(side_effect=RuntimeError("the tier 1 table broke")))
    yielded = _run(function)
    names = zipfile.ZipFile(io.BytesIO(yielded[0])).namelist()
    assert any(n.endswith("T1_data_ERROR.txt") for n in names), "the file is still written"
    summaries = [m for t, m in notes if "ERROR.txt" in m]
    assert len(summaries) == 1 and "the tier 1 table broke" in summaries[0] and ". Suggestion:" in summaries[0], notes
    monkeypatch.setattr(world.orch, "materialize_tier1", real)


def test_an_export_without_error_files_gets_no_summary(tmp_path, monkeypatch):
    """The control."""
    notes = []
    _bundle(World(tmp_path), notes, monkeypatch)
    assert not [m for t, m in notes if "ERROR.txt" in m], notes


# -- fix round 1: texts that are true, one form, notices held until the bundle is handed over ---------------------------------

def test_the_quarto_suggestion_is_true_for_the_bundle_the_user_receives(tmp_path, monkeypatch):
    """MUTATION Q1 fails here. Before: 'render report.qmd yourself with quarto render ...', which gives a report with no figures:
    report.qmd links `_render/<plot>.png` and no `_render/` folder is in the zip. The text is read against the produced zip."""
    notes = []
    archive = _bundle(World(tmp_path), notes, monkeypatch)
    names = archive.namelist()
    qmd = next(n for n in names if n.endswith("/report.qmd"))
    folder = qmd.rsplit("/", 1)[0]
    assert not any("/_render/" in n or n.startswith("_render/") for n in names), "the premise: no _render/ folder in the zip"
    assert "_render/p.png" in archive.read(qmd).decode(), "the premise: the report links its figures there"
    assert f"{folder}/C/plots/p.png" in names, "the pictures are in <table>/plots/"
    warnings = [m for m in _texts(notes, "warning") if "Quarto" in m]
    assert len(warnings) == 1
    text = warnings[0]
    assert "quarto render report.qmd" not in text, text
    assert "<table>/plots/" in text and "_render/" in text and "not in the bundle" in text and "shows no figures" in text, text
    assert text.count("Suggestion:") == 2 and "Fix:" not in text, text
    stub = archive.read(next(n for n in names if n.endswith("report_RENDER_FAILED.txt"))).decode()
    assert "<table>/plots/" in stub and "not in the bundle" in stub and "run:" not in stub, stub


def test_the_summary_has_the_reason_without_the_remedy_and_each_remedy_after_a_suggestion_label(tmp_path, monkeypatch):
    """MUTATION Q2 fails here. Before: '(VisualizationError: Plot ..., layer 1 (geom_barr): ... Fix: write geom_bar.). Suggestion: ...'."""
    world = World(tmp_path)
    recipe = world.data_analysis_recipes_dir / "tiny.yaml"
    recipe.write_text(recipe.read_text().replace("geom_bar", "geom_barr"))
    clear_data_analysis_recipe_cache()
    notes = []
    _bundle(world, notes, monkeypatch)
    summaries = [m for t, m in notes if "ERROR.txt" in m and t == "error"]
    assert len(summaries) == 1, notes
    text = summaries[0]
    assert "geom_barr" in text and "is not a registered plot component" in text, text
    assert "Fix:" not in text, text
    assert text.count("Suggestion:") == 2, text
    assert "Suggestion: write geom_bar" in text and "Suggestion: open the *_ERROR.txt files" in text, text
    reason, _, remedies = text.partition(". Suggestion:")
    assert "write geom_bar" not in reason, "the reason holds the problem only"


def _refused_export(tmp_path, monkeypatch, extra_values=None, patch=None):
    from app.tests.test_export_download_path import _change_the_data_during_the_first_build
    world = World(tmp_path)
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    notes = []
    function = _download_function(world, view, notes, monkeypatch, extra_values=extra_values)
    _change_the_data_during_the_first_build(world, monkeypatch)
    if patch:
        patch()
    yielded = _run(function)
    return notes, zipfile.ZipFile(io.BytesIO(yielded[0])).namelist()


def test_a_refused_export_shows_only_the_refusal_not_the_notices_of_a_zip_nobody_receives(tmp_path, monkeypatch):
    """MUTATION Q3 fails here: Quarto fails in this harness, a picture gets no keys, the provenance has a problem; the export is
    then refused because the data changed while a table was built. Only the refusal is shown."""
    real = export_handlers.build_export_provenance
    monkeypatch.setattr(export_handlers, "build_export_provenance",
                        lambda **kw: real(**{**kw, "orchestrator": SimpleNamespace(get_source_files=mock.Mock(side_effect=OSError("no listing")))}))

    def failing(raw, prov, plot_id, ds="", on_problem=None):
        on_problem(RuntimeError("PIL is not installed"))
        return raw
    monkeypatch.setattr(export_handlers, "_embed_png_provenance", failing)
    notes, names = _refused_export(tmp_path, monkeypatch)
    assert names == ["EXPORT_NOT_CREATED.txt"]
    assert [m for t, m in notes if t == "error" and "Export blocked" in m], notes
    others = [m for t, m in notes if "Quarto" in m or "keys could not be written" in m or "no listing" in m or "ERROR.txt" in m]
    assert others == [], others


def test_the_same_export_that_is_handed_over_shows_those_notices(tmp_path, monkeypatch):
    """The control of the test above: without the change of the data the same notices are shown."""
    notes = []
    _bundle(World(tmp_path), notes, monkeypatch)
    assert [m for t, m in notes if "Quarto" in m], notes
