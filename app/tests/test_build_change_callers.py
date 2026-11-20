"""Every caller of a table build is told when the inputs changed during the build (STALE-KEY-STORE-1, round 3).

D-0050 "No silent error that is the rule", D-0005 "export refuses when files changed since the view", D-0003 "no anchor reuse by
file name". A table built while its recipe or data change is returned, not stored; the build tells its caller through
`on_inputs_changed`. This file checks the callers: HOME (data_change_notice tests), the export (refuses), Blueprint and the gallery
(tell), and that no caller in `app/` can forget the callback.

Choice for the last point (a new caller must not forget): a SCAN of the call sites, not a required argument. A required argument would
change the signature that about 60 tests and every helper call without one; the scan fails for any call in `app/` (not in tests) that
names no `on_inputs_changed`, so a new caller is caught the day it is written.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_build_change_callers.py -q
"""
import ast
import io
import zipfile
from pathlib import Path
from unittest import mock

import pytest

from app.handlers.blueprint_handlers import tell_inputs_changed as blueprint_tell
from app.handlers.export_handlers import blocked_export_notice, refusal_for_build_changes
from app.modules import gallery_examples
from app.modules.cache_keys import DataAnalysisRecipeKeys, clear_data_analysis_recipe_cache
from app.modules.orchestrator import InputsChanged
from app.tests.test_cache_chain import FILTER_A, World

ROOT = Path(__file__).resolve().parents[2]
BUILDS = ("materialize_tier1", "materialize_tier2")
NEW_DATA = "sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _calls_without_the_callback(root=ROOT):
    """Calls of a build under `root/app` (not in tests) with no `on_inputs_changed`, or with a literal None (which tells nobody)."""
    missing = []
    for path in sorted((root / "app").rglob("*.py")):
        if "tests" in path.relative_to(root).parts:
            continue
        for node in ast.walk(ast.parse(path.read_text(), str(path))):
            if isinstance(node, ast.Call) and isinstance(node.func, ast.Attribute) and node.func.attr in BUILDS:
                given = {k.arg: k.value for k in node.keywords}
                none = isinstance(given.get("on_inputs_changed"), ast.Constant) and given["on_inputs_changed"].value is None
                if "on_inputs_changed" not in given or none:
                    missing.append(f"{path.relative_to(root)}:{node.lineno} {node.func.attr}" + (" (None)" if none else ""))
    return missing


def test_no_caller_of_a_table_build_in_app_forgets_to_say_what_it_does_when_inputs_change():
    assert _calls_without_the_callback() == [], "pass on_inputs_changed (tell the user, or refuse): a build that changed is never silent"


def test_the_scan_sees_a_call_that_forgets_the_callback_or_passes_none(tmp_path):
    """The scan itself can fail: planted callers (in a temporary copy of the tree, never in `app/`) are found."""
    planted = tmp_path / "app" / "modules"
    planted.mkdir(parents=True)
    (planted / "forgets.py").write_text("def f(o):\n    return o.materialize_tier1('r', 'c', 'p', keys=None)\n")
    (planted / "none.py").write_text("def f(o):\n    return o.materialize_tier2('r', 'c', 'p', keys=None, on_inputs_changed=None)\n")
    (planted / "good.py").write_text("def f(o, tell):\n    return o.materialize_tier2('r', 'c', 'p', on_inputs_changed=tell)\n")
    found = _calls_without_the_callback(tmp_path)
    assert found == ["app/modules/forgets.py:2 materialize_tier1", "app/modules/none.py:2 materialize_tier2 (None)"]


# ------------------------------------------------------------------ the export refuses

def test_an_export_whose_table_was_built_while_the_data_changed_is_refused_with_nothing_else_written(tmp_path):
    """The export collects what the build tells (as export_handlers does) and refuses at the end: the zip holds only EXPORT_NOT_CREATED.txt."""
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    export_keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    real = w.orch.prepare_ingredient

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        w.write_data(NEW_DATA)
        return lf

    changes = []
    notes = []
    with mock.patch.object(w.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes):
        table = w.orch.materialize_tier2("tiny", "C", w.anchor, keys=export_keys,
                                         on_inputs_changed=lambda c: changes.append(c.text))
    assert table.collect().height >= 0 and changes == ["the data files changed"]
    refusal = refusal_for_build_changes(changes, export_keys, export_keys, lambda msg, **kw: notes.append((kw.get("type"), msg)))
    archive = zipfile.ZipFile(io.BytesIO(refusal))
    assert archive.namelist() == ["EXPORT_NOT_CREATED.txt"]
    text = archive.read("EXPORT_NOT_CREATED.txt").decode()
    assert "while a table of this export was being built: the data files changed" in text and "Reload the page" in text
    assert "nothing was exported" in text
    assert notes and notes[0][0] == "error" and "Export blocked" in notes[0][1] and notes[0][1].count("while a table") == 1


def test_an_export_whose_builds_saw_no_change_is_not_refused():
    assert refusal_for_build_changes([], None, None, lambda *a, **k: pytest.fail("no notification expected")) is None


def test_the_refusal_has_the_same_file_and_form_as_the_refusal_for_a_change_since_the_view():
    keys = DataAnalysisRecipeKeys("r", "d", {"T": "t"})
    since_view = blocked_export_notice(["the data files"], keys, keys)
    during_build = blocked_export_notice(["the data files changed"], keys, keys, during_build=True)
    assert since_view.splitlines()[0] == during_build.splitlines()[0] == "EXPORT NOT CREATED"
    assert "What to do:" in since_view and "What to do:" in during_build and "Keys (for the record)" in during_build
    assert "after this view was opened" in since_view and "while a table of this export was being built" in during_build


def test_the_export_refuses_at_the_end_before_it_hands_over_the_bundle():
    """The download checks the list the five builds fill, after the bundle is made and before it is yielded."""
    source = (ROOT / "app" / "handlers" / "export_handlers.py").read_text()
    assert source.count("on_inputs_changed=_on_build_change") == 5
    check = source.index("refusal_for_build_changes(_build_changes")
    assert source.rindex("zf.writestr", 0, check) > 0 and source.index("yield buf.read()", check) > check


# ------------------------------------------------------------------ Blueprint and the gallery tell

def test_blueprint_tells_the_user_in_the_form_of_the_home_notice():
    told = []
    blueprint_tell(InputsChanged("the data analysis recipe changed"), notify=lambda msg, **kw: told.append((kw.get("type"), msg)))
    assert len(told) == 1 and told[0][0] == "warning"
    happened, _, suggestion = told[0][1].partition(" Suggestion: ")
    assert "While a table was being built, the data analysis recipe changed" in happened and "reload the page (F5)" in suggestion


def test_the_gallery_build_fails_with_the_plain_notice(capsys):
    with pytest.raises(gallery_examples.InputsChangedDuringBuild) as raised:
        gallery_examples.tell_inputs_changed(InputsChanged("the data files changed"))
    text = str(raised.value)
    assert text.startswith("While a table was being built, the data files changed") and "Suggestion: run the command again" in text


@pytest.fixture
def scratch():
    """A folder under tmpAI/ (agent scratch): the recipe of an example may only name a data path relative to the project root."""
    import shutil
    import tempfile
    base = ROOT / "tmpAI"
    base.mkdir(exist_ok=True)
    folder = Path(tempfile.mkdtemp(prefix="gallery_build_change_", dir=base))
    yield folder
    shutil.rmtree(folder, ignore_errors=True)


def _gallery_copy(folder):
    """One example copied to `folder`, its data path pointing at the copy."""
    import shutil
    from app.modules.gallery_examples import rebuild_gallery_index
    gallery = folder / "gallery"
    shutil.copytree(ROOT / "assets" / "gallery_data" / "bar_simple", gallery / "bar_simple")
    recipe = gallery / "bar_simple" / "data_analysis_recipe.yaml"
    relative = (gallery / "bar_simple" / "example_data.tsv").relative_to(ROOT)
    recipe.write_text(recipe.read_text().replace("./assets/gallery_data/bar_simple/example_data.tsv", f"./{relative}"))
    rebuild_gallery_index(gallery)
    return gallery


def test_the_preview_command_fails_with_exit_1_and_the_notice_when_the_data_changes_during_a_build(scratch, capsys, monkeypatch):
    """The command (assets/scripts/gallery_previews.py main) exits 1, prints the notice, and writes no picture, also with --apply."""
    import importlib.util
    from app.modules.orchestrator import DataOrchestrator
    spec = importlib.util.spec_from_file_location("gallery_previews", ROOT / "assets" / "scripts" / "gallery_previews.py")
    command = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(command)
    gallery = _gallery_copy(scratch)
    data = gallery / "bar_simple" / "example_data.tsv"
    picture = gallery / "bar_simple" / "preview_plot.png"
    picture_before = picture.read_bytes()
    real = DataOrchestrator.prepare_ingredient

    def ingest_then_the_file_changes(self, *args, **kwargs):
        lf = real(self, *args, **kwargs)
        data.write_text(data.read_text() + data.read_text().splitlines()[1] + "\n")
        return lf

    monkeypatch.chdir(ROOT)
    monkeypatch.setattr(DataOrchestrator, "prepare_ingredient", ingest_then_the_file_changes)
    code = command.main(["--gallery", str(gallery), "--out", str(scratch / "out"), "--apply"])
    shown = capsys.readouterr().out
    assert code == 1
    assert "bar_simple" in shown and "error" in shown and "While a table was being built, the data files changed" in shown
    assert "Suggestion: run the command again when the files are stable" in shown
    assert picture.read_bytes() == picture_before, "a picture that may mix two states must not be written"
    assert not (scratch / "out" / "bar_simple.png").exists()


def test_the_preview_command_still_succeeds_when_nothing_changes_during_the_build(scratch, capsys, monkeypatch):
    import importlib.util
    spec = importlib.util.spec_from_file_location("gallery_previews", ROOT / "assets" / "scripts" / "gallery_previews.py")
    command = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(command)
    gallery = _gallery_copy(scratch)
    monkeypatch.chdir(ROOT)
    assert command.main(["--gallery", str(gallery), "--out", str(scratch / "out")]) == 0
    assert "error: 0" in capsys.readouterr().out


def test_the_gallery_build_hands_the_callback_to_both_tiers(tmp_path):
    """Tier 1 gets the callback (checked on the call). The plot's table is read by `materialize_tier3`, which builds the Tier 2 through the private
    `_materialize_tier2` and tells the callback it was given: a change that the build reports must reach the gallery's own callback, which fails the build.
    Only the two builds are stand-ins (a build that reports a change); the reader `materialize_tier3` is the real one."""
    import polars as pl
    example = ROOT / "assets" / "gallery_data" / "bar_simple"
    change = InputsChanged("the data files changed")
    with mock.patch("app.modules.orchestrator.DataOrchestrator.materialize_tier1") as tier1, \
            mock.patch("app.modules.orchestrator.DataOrchestrator._materialize_tier2", return_value=(pl.LazyFrame({"x": [1]}), "key", change)):
        with pytest.raises(gallery_examples.InputsChangedDuringBuild) as raised:
            gallery_examples._build(example, tmp_path / "work", Path("."))
    assert tier1.call_args.kwargs["on_inputs_changed"] is gallery_examples.tell_inputs_changed
    assert "the data files changed" in str(raised.value), "the plot's table was read without the gallery's callback"
