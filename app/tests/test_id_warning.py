"""The words and the read state of the warning of the ids (D-0582, D-0585, D-0613): headless, through the real checks of the ids on the demo recipe and on small
recipes in a temporary folder.

What is checked: each finding gives its plain line (ids added with the app's words "missing in original table" and the sentence of the recipe maker, ids not in
the metadata, lines with no usable id, a log that could not be written, checks that failed); nothing found gives no line; the click "I have read this" is written
in the log and read back for the same recipe and data and for no other; a log that cannot be read or written never raises and says "not read"; the sentences of the
export say "read in the app" or "automatic, no user". The opening effect hands the run to the warning once per opening.

PROVISIONAL (D-0613): the words, the read state per recipe and data batch, the word "read in the app" for the click.

# @deps
# consumes: app/modules/id_warning.py, app/modules/id_check_run.py, libs/utils/src/utils/id_log.py
# doc: .claude/knowledge/decision_ledger.md (D-0582, D-0585, D-0613)
# @end_deps

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_id_warning.py -q
"""
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.id_check_run import id_log_folder, run_id_checks
from app.modules.id_warning import (READ_IN_APP, ReadStatus, export_sentences, has_warning, log_place_text, mark_read, quiet_line, read_status,
                                    warning_lines)
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_id_completion_in_the_app import DEMO, PIPELINES, ROOT, quiet, world
from utils.id_completion import added_line_words, starting_meaning
from utils.id_log import AUTOMATIC, log_path, read_log

WHEN = "2026-11-24T10:00:00+01:00"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def run_of(tmp_path, tables, metadata=None, user=None):
    orchestrator, recipe = world(tmp_path, tables, metadata=metadata)
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    folder = user or tmp_path / "user"
    return quiet(run_id_checks, orchestrator, "w", recipe, keys, folder, WHEN), keys, folder


def demo_run(tmp_path):
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    loaded = load_data_analysis_recipe(PIPELINES / f"{DEMO}.yaml")
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, DEMO, loaded)
    return quiet(run_id_checks, orchestrator, DEMO, loaded.raw, keys, tmp_path, WHEN), keys


# -- the lines -----------------------------------------------------------------------------

def test_the_demo_gives_one_line_naming_resfinder_with_four_the_apps_words_and_the_sentence_of_the_recipe(tmp_path):
    run, _ = demo_run(tmp_path)
    (line,) = warning_lines(run)
    assert line.startswith("ResFinder: 4 entities missing in original table. The recipe says: ")
    assert "Not Found, counted as 0" in line and has_warning(run)
    assert added_line_words() == "missing in original table"


def test_one_added_entity_is_singular_and_carries_the_sentence_the_recipe_maker_wrote(tmp_path):
    run, _, _ = run_of(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    assert warning_lines(run) == [f"A: 1 entity {added_line_words()}. The recipe says: {starting_meaning()}"]


def test_ids_of_a_table_that_are_not_in_the_metadata_and_the_lines_with_no_usable_id_are_lines_of_their_own(tmp_path):
    run, _, _ = run_of(tmp_path, {"A": ["s1", "s9", None]}, metadata=["s1"])
    lines = warning_lines(run)
    assert "A: 1 id(s) are not in the metadata." in lines
    assert any(line.startswith("A: 1 line(s) have no usable id") for line in lines)
    assert any(line.startswith("metadata_schema: 1 entity missing in original table") for line in lines), "the metadata is completed too"


def test_equal_ids_everywhere_give_no_warning_at_all(tmp_path):
    run, _, _ = run_of(tmp_path, {"A": ["s1", "s2"], "B": ["s2", "s1"]}, metadata=["s1", "s2"])
    assert run.report is not None and warning_lines(run) == [] and not has_warning(run)


def test_no_run_and_a_recipe_with_no_table_that_takes_part_give_no_warning():
    assert warning_lines(None) == [] and not has_warning(None)


def test_a_table_that_cannot_be_read_gives_the_line_that_the_checks_failed(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]})
    (tmp_path / "data" / "B.tsv").unlink()
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run = quiet(run_id_checks, orchestrator, "w", recipe, keys, tmp_path / "user", WHEN)
    (line,) = warning_lines(run)
    assert line.startswith("The checks of the ids could not be made") and has_warning(run)


def test_a_log_that_could_not_be_written_is_a_line_of_the_warning_and_the_place_text_says_so(tmp_path):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    run, _, _ = run_of(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"], user=blocker)
    assert any("could not be written" in line for line in warning_lines(run))
    assert "could not be written" in log_place_text(run) and "id_log.yaml" in log_place_text(run)


def test_the_place_text_names_the_log_file_and_says_every_export_holds_it(tmp_path):
    run, _, folder = run_of(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    text = log_place_text(run)
    assert str(log_path(id_log_folder(folder), "w")) in text and "Every export holds it (id_log.yaml)" in text


# -- the read state ------------------------------------------------------------------------

def test_a_click_is_written_in_the_log_with_the_date_and_no_person_and_is_read_back_for_the_same_recipe_and_data(tmp_path):
    run, keys, folder = run_of(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    log_folder = id_log_folder(folder)
    sha, batch = keys.data_analysis_recipe_sha256, keys.data_batch_hash
    assert read_status(log_folder, "w", sha, batch) == ReadStatus(False)
    outcome = mark_read(log_folder, "w", sha, batch, when=WHEN)
    assert outcome.written
    status = read_status(log_folder, "w", sha, batch)
    assert status.read and status.when == WHEN and status.who == READ_IN_APP
    entry = read_log(log_path(log_folder, "w"))["entries"][-1]
    assert entry["kind"] == "read" and entry["who"] == READ_IN_APP and entry["who"] != AUTOMATIC
    assert quiet_line(status) == "Id warnings read on 2026-11-24."


def test_a_click_for_one_data_batch_or_one_recipe_does_not_count_for_another(tmp_path):
    _, keys, folder = run_of(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    log_folder = id_log_folder(folder)
    mark_read(log_folder, "w", keys.data_analysis_recipe_sha256, keys.data_batch_hash, when=WHEN)
    assert not read_status(log_folder, "w", keys.data_analysis_recipe_sha256, "another-batch").read, "new data: red again"
    assert not read_status(log_folder, "w", "another-recipe", keys.data_batch_hash).read, "changed recipe: red again"
    assert not read_status(log_folder, "other", keys.data_analysis_recipe_sha256, keys.data_batch_hash).read


def test_the_last_click_is_the_one_shown_and_an_earlier_one_stays_in_the_log(tmp_path):
    _, keys, folder = run_of(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    log_folder, sha, batch = id_log_folder(folder), keys.data_analysis_recipe_sha256, keys.data_batch_hash
    mark_read(log_folder, "w", sha, batch, when="2026-11-24T09:00:00+01:00")
    mark_read(log_folder, "w", sha, batch, when="2026-11-25T09:00:00+01:00")
    assert read_status(log_folder, "w", sha, batch).when.startswith("2026-11-25")
    assert [e["kind"] for e in read_log(log_path(log_folder, "w"))["entries"]] == ["checks", "read", "read"]


def test_a_click_that_cannot_be_written_says_why_and_never_raises(tmp_path):
    blocker = tmp_path / "not_a_folder"
    blocker.write_text("x")
    outcome = quiet(mark_read, id_log_folder(blocker), "w", "a", "b")
    assert not outcome.written and outcome.problem and "could not be written" in outcome.problem


def test_a_log_file_that_cannot_be_read_means_not_read(tmp_path):
    folder = id_log_folder(tmp_path)
    folder.mkdir(parents=True)
    log_path(folder, "w").write_text("format: 9\nentries: []\n")
    assert read_status(folder, "w", "a", "b") == ReadStatus(False)
    log_path(folder, "w").write_text("entries: [unclosed\n")
    assert read_status(folder, "w", "a", "b") == ReadStatus(False)


# -- the export ----------------------------------------------------------------------------

def test_the_export_says_the_log_is_automatic_with_no_user_when_nobody_clicked(tmp_path):
    run, _ = demo_run(tmp_path)
    text = "\n".join(export_sentences(run, ReadStatus(False)))
    assert "missing in original table" in text and "Not Found, counted as 0" in text
    assert f"({AUTOMATIC})" in text and "must read it" in text and "read in the app" not in text


def test_the_export_says_the_warning_was_read_in_the_app_after_a_click(tmp_path):
    run, keys = demo_run(tmp_path)
    mark_read(id_log_folder(tmp_path), DEMO, keys.data_analysis_recipe_sha256, keys.data_batch_hash, when=WHEN)
    status = read_status(id_log_folder(tmp_path), DEMO, keys.data_analysis_recipe_sha256, keys.data_batch_hash)
    text = "\n".join(export_sentences(run, status))
    assert "read in the app on 2026-11-24" in text and AUTOMATIC not in text


def test_the_export_says_the_ids_are_equal_when_they_are_and_asks_nothing_of_the_reader(tmp_path):
    run, _, _ = run_of(tmp_path, {"A": ["s1"], "B": ["s1"]})
    assert export_sentences(run, ReadStatus(False)) == ["The ids are equal in every table of the recipe; the log of the ids (id_log.yaml) says so."]


def test_the_export_has_no_sentence_when_no_table_takes_part_and_names_a_failed_check(tmp_path):
    assert export_sentences(None, ReadStatus(False)) == []
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]})
    (tmp_path / "data" / "B.tsv").unlink()
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run = quiet(run_id_checks, orchestrator, "w", recipe, keys, tmp_path / "user", WHEN)
    assert any("could not be made" in s for s in export_sentences(run, ReadStatus(False)))


# -- the opening hands the run to the warning ------------------------------------------------

def test_the_opening_writes_what_the_id_checks_found_once_per_opening_and_again_for_new_data(tmp_path, monkeypatch):
    """MUTATION: an opening that does not write the state leaves the warning empty; one that writes at every run is a reactive loop (section 14, R3)."""
    from shiny import reactive
    import app.handlers.opening_handlers as handlers
    from app.tests.test_opening_handler import Opening
    from app.tests.test_tier3_reader import Tier3World
    calls = []
    canned = object()
    monkeypatch.setattr(handlers, "run_id_checks", lambda *a, **k: calls.append(a) or canned)
    world_ = Tier3World(tmp_path)
    state = reactive.Value(None)
    opening = Opening(world_, monkeypatch, id_run_state=state)
    opening.run()
    with reactive.isolate():
        first = state.get()
    keys = world_.orch.compute_data_analysis_recipe_keys("tiny")
    assert first["run"] is canned and first["recipe_id"] == "tiny" and first["recipe_sha256"] == keys.data_analysis_recipe_sha256
    assert first["data_batch_hash"] == keys.data_batch_hash and first["folder"] == id_log_folder(world_.root / "user") and len(calls) == 1
    opening.run()
    with reactive.isolate():
        assert state.get() is first and len(calls) == 1, "the same opening again: nothing is made and nothing is written"
    world_.write_data("sample_id\tgroup\tscore\ns1\tA\t1\ns2\tA\t2\ns3\tB\t3\ns4\tB\t4\ns5\tB\t5\ns6\tB\t6\n")
    clear_data_analysis_recipe_cache()
    opening.run()
    with reactive.isolate():
        assert state.get() is not first and state.get()["data_batch_hash"] != first["data_batch_hash"] and len(calls) == 2, "new data: new checks, new state"


def test_the_opening_without_a_warning_slot_still_runs_the_checks_and_does_not_fail(tmp_path, monkeypatch):
    import app.handlers.opening_handlers as handlers
    from app.tests.test_opening_handler import Opening
    from app.tests.test_tier3_reader import Tier3World
    calls = []
    monkeypatch.setattr(handlers, "run_id_checks", lambda *a, **k: calls.append(a) or None)
    opening = Opening(Tier3World(tmp_path), monkeypatch)
    opening.run()
    assert len(calls) == 1 and opening.current()["status"] == "ready"


# -- the export sentence and the title say only what is true (found by the review of the id warning) ----------------------------

def test_the_export_says_the_ids_were_not_equal_only_when_they_really_differ(tmp_path):
    from dataclasses import replace
    from app.modules.id_check_run import IdCheckRun
    from app.modules.id_warning import ids_differ
    from utils.id_log import LogOutcome
    # 1. ids that really differ: the sentence says so
    differ, _, _ = run_of(tmp_path / "d", {"A": ["s1"]}, metadata=["s1", "s2"])
    assert ids_differ(differ) and "were not equal" in export_sentences(differ, ReadStatus(False))[0]
    # 2. the checks could not be made: the sentence says that, never "not equal"
    failed = IdCheckRun(report=None, lines=(), outcome=None, error="the table A cannot be read")
    assert not ids_differ(failed) and has_warning(failed)
    text = "\n".join(export_sentences(failed, ReadStatus(False)))
    assert "could not be made" in text and "not known whether the ids" in text and "were not equal" not in text and "The ids are equal" not in text
    # 3. the ids are equal and only the log could not be written: the sentence says that, never "not equal"
    equal, _, _ = run_of(tmp_path / "e", {"A": ["s1"]}, metadata=["s1"])
    broken = replace(equal, outcome=LogOutcome(written=False, new=True, path=None, text="the entry", problem="the folder cannot be written"))
    assert not ids_differ(broken) and has_warning(broken)
    text = "\n".join(export_sentences(broken, ReadStatus(False)))
    assert "equal in every table" in text and "could not be written" in text and "were not equal" not in text and "written automatically" not in text
    assert ids_differ(replace(differ, error="x")), "a difference stays a difference when a check also failed"


def test_the_title_of_the_warning_is_true_when_the_only_finding_is_the_log():
    from app.handlers.id_warning_handlers import LOG_TITLE, TITLE
    assert LOG_TITLE == "The log of the ids could not be written." and TITLE != LOG_TITLE
