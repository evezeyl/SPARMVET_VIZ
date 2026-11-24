"""The log of the ids of an opened recipe, and the export (D-0575, D-0576, D-0581, D-0582, D-0592, D-0613).

`run_id_checks` is what HOME's opening calls: the three checks, then the log written automatically ("automatic, no user"). It never raises, never refuses a recipe, and when
the folder cannot be written it prints the text and returns it. `export_log_text` is the text of `id_log.yaml` in every bundle.

The browser side (the opening calls it and nothing crashes) is `app/tests/test_shiny_smoke.py` and `test_opening_browser.py`.

# @deps
# consumes: app/modules/id_check_run.py, libs/utils/src/utils/id_log.py, app/modules/orchestrator.py
# doc: .claude/knowledge/decision_ledger.md (D-0575, D-0581, D-0582)
# @end_deps

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_id_checks_log.py -q
"""
import contextlib
import io
from pathlib import Path

import pytest
import yaml

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.id_check_run import ID_LOG_FOLDER, export_log_text, id_log_folder, run_id_checks
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_id_completion import DEMO, PIPELINES, ROOT, NOT_IN_ORIGINAL, quiet, world
from utils.id_log import AUTOMATIC, log_path, read_log, record_read

WHEN = "2026-11-24T10:00:00+01:00"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def demo_run(user_data, loud=False, **kw):
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    loaded = load_data_analysis_recipe(PIPELINES / f"{DEMO}.yaml")
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, DEMO, loaded)
    call = run_id_checks if loud else (lambda *a, **k: quiet(run_id_checks, *a, **k))   # `loud`: the console is what the test reads
    return call(orchestrator, DEMO, loaded.raw, keys, user_data, WHEN, **kw), keys, loaded


def test_the_log_is_written_in_a_folder_of_the_user_folder_with_the_numbers_and_the_unmatched_ids(tmp_path):
    run, keys, _ = demo_run(tmp_path)
    folder = tmp_path / ID_LOG_FOLDER
    assert id_log_folder(tmp_path) == folder and run.outcome.written and run.outcome.new and run.outcome.path == log_path(folder, DEMO)
    entry = read_log(run.outcome.path)["entries"][0]
    assert entry["who"] == AUTOMATIC and entry["when"] == WHEN and entry["kind"] == "checks"
    assert entry["recipe_sha256"] == keys.data_analysis_recipe_sha256 and entry["data_batch_hash"] == keys.data_batch_hash
    res = next(t for t in entry["ids"]["tables"] if t["table"] == "ResFinder")
    assert res["ids_added"] == {"count": 4, "ids": sorted(NOT_IN_ORIGINAL)}
    assert res["check_2_metadata_ids_not_in_this_table"]["count"] == 4 and res["check_1_ids_not_in_the_metadata"]["count"] == 0
    assert entry["ids"]["check_3"] == "passed" and entry["ids"]["ids_in_the_union"] == 42


def test_the_findings_are_in_plain_words_and_nothing_is_a_refusal(tmp_path):
    run, _, _ = demo_run(tmp_path)
    assert run.error is None and run.report.check3_ok
    assert len(run.lines) == 2 and all("ResFinder" in line for line in run.lines)
    assert run.log_warning is None and "ResFinder" in run.log_text


def test_opening_the_same_recipe_on_the_same_data_again_writes_nothing_new(tmp_path):
    demo_run(tmp_path)
    again, _, _ = demo_run(tmp_path)
    assert again.outcome.written and not again.outcome.new
    assert len(read_log(log_path(id_log_folder(tmp_path), DEMO))["entries"]) == 1


def test_a_folder_that_cannot_be_written_does_not_stop_the_opening_and_the_text_is_returned(tmp_path, capsys):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    run, _, _ = demo_run(blocker, loud=True)
    assert run.report is not None and not run.outcome.written
    assert "ResFinder" in run.log_text and run.log_warning and "could not be written" in run.log_warning
    assert "ResFinder" in capsys.readouterr().out, "the text is on the console"


def test_a_recipe_with_no_table_that_takes_part_has_no_report_and_no_log(tmp_path):
    from utils.recipe_factory import minimal_recipe, minimal_schema, write_recipe
    data = tmp_path / "d"
    data.mkdir()
    (data / "t.tsv").write_text("x\n1\n")
    recipe = minimal_recipe("w", schemas={"T": minimal_schema(str(data / "t.tsv"), {"x": "Int64"})})
    write_recipe(tmp_path / "w.yaml", recipe)
    orchestrator = DataOrchestrator(tmp_path, tmp_path)
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run = run_id_checks(orchestrator, "w", recipe, keys, tmp_path / "user", WHEN)
    assert run.report is None and run.outcome is None and run.error is None and run.lines == ()
    assert not (tmp_path / "user").exists() and export_log_text(tmp_path / "user", "w", run, "a", "b") is None


def test_a_table_that_cannot_be_read_makes_an_error_text_and_never_raises(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]})
    (tmp_path / "data" / "B.tsv").unlink()
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run = quiet(run_id_checks, orchestrator, "w", recipe, keys, tmp_path / "user", WHEN)
    assert run.report is None and run.error and "could not be made" in run.error and "'B'" in run.error
    assert not (tmp_path / "user").exists()


def test_the_log_of_two_data_batches_has_two_entries_and_the_click_is_kept_between_them(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    user = tmp_path / "user"
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run_id_checks(orchestrator, "w", recipe, keys, user, WHEN)
    record_read(id_log_folder(user), "w", keys.data_analysis_recipe_sha256, keys.data_batch_hash, who="EZ", when=WHEN)
    (tmp_path / "data" / "A.tsv").write_text("sample_id\tv\ns1\t0\ns5\t1\n")
    clear_data_analysis_recipe_cache()
    keys2 = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run_id_checks(orchestrator, "w", recipe, keys2, user, WHEN)
    kinds = [e["kind"] for e in read_log(log_path(id_log_folder(user), "w"))["entries"]]
    assert kinds == ["checks", "read", "checks"], "a new data batch is a new entry, to be read again"


# -- the export ----------------------------------------------------------------------------

def test_the_export_log_holds_the_entry_of_this_export_and_the_entries_of_the_user_folder(tmp_path):
    run, keys, _ = demo_run(tmp_path)
    record_read(id_log_folder(tmp_path), DEMO, keys.data_analysis_recipe_sha256, keys.data_batch_hash, who="EZ", when=WHEN)
    text = export_log_text(tmp_path, DEMO, run, keys.data_analysis_recipe_sha256, keys.data_batch_hash, when=WHEN)
    data = yaml.safe_load(text)
    assert data["format"] == 1 and "must read it" in data["about"]
    assert [e["kind"] for e in data["entries"]] == ["checks", "read"] and "note" not in data


def test_the_export_log_adds_the_entry_when_the_user_folder_could_not_be_written(tmp_path):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    run, keys, _ = demo_run(blocker)
    data = yaml.safe_load(export_log_text(blocker, DEMO, run, keys.data_analysis_recipe_sha256, keys.data_batch_hash, when=WHEN))
    assert [e["kind"] for e in data["entries"]] == ["checks"] and data["entries"][0]["ids"]["tables"]


def test_the_export_log_says_so_when_the_log_file_of_the_user_folder_cannot_be_read(tmp_path):
    run, keys, _ = demo_run(tmp_path)
    log_path(id_log_folder(tmp_path), DEMO).write_text("format: 9\nentries: []\n")
    data = yaml.safe_load(export_log_text(tmp_path, DEMO, run, keys.data_analysis_recipe_sha256, keys.data_batch_hash, when=WHEN))
    assert "could not be read" in data["note"] and [e["kind"] for e in data["entries"]] == ["checks"]


def test_the_export_does_not_write_into_the_user_folder(tmp_path):
    run, keys, _ = demo_run(tmp_path, write=False)
    assert run.outcome is None and run.report is not None
    export_log_text(tmp_path, DEMO, run, keys.data_analysis_recipe_sha256, keys.data_batch_hash)
    assert not (tmp_path / ID_LOG_FOLDER).exists()
