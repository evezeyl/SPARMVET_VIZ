"""The completion of the ids stays robust: a recipe the check would refuse fails with ONE plain message, the opening never raises, and the ids of a file are read once.

What this tests, and what the design expects (the three points the brief of this round names):

1. A recipe that declares an entity id and has a missing or wrong `completion` block (a half-edited recipe, seen in BLUEPRINT's live view) is refused by the
   recipe check and by HOME's load gate, and every read of it (the build, the data check, the plan of every place, the checks of the ids) gives ONE plain message that
   names the table and says what to write: no traceback and no crash of an output.
2. `run_id_checks`, which HOME's opening calls, can never raise: not for a broken recipe, not for keys that are not what they should be, not for a folder that is not
   a folder.
3. The ids of a file are read once for the same bytes and the same declarations, and read again when the bytes or a declaration change (the memo of
   `DataOrchestrator._ids_of`): the opening of a recipe does not get slower with the number of tables that take part.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_id_completion_robust.py -q

# @deps
# consumes: app/modules/orchestrator.py, app/modules/id_check_run.py, app/modules/plan_composer.py, app/modules/data_analysis_recipe_validator.py, libs/utils/src/utils/id_completion.py
# doc: .claude/knowledge/decision_ledger.md (D-0613, D-0581)
# @end_deps
"""
import contextlib
import io
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.data_analysis_recipe_validator import check_data_analysis_recipe_data
from app.modules.id_check_run import run_id_checks
from app.modules.plan_composer import compose_plan_book
from app.tests.test_id_completion_in_the_app import DEMO, PIPELINES, ROOT, quiet, world
from utils.errors import DataAnalysisRecipeError
from utils.recipe_check import check_recipe
from utils.recipe_factory import write_recipe
from utils.recipe_loader import check_recipe_file

import utils.id_completion as id_completion


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def broken(tmp_path, how):
    """A recipe with two tables and a metadata, then one `completion` block spoiled in the way `how` says."""
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]}, metadata=["s1", "s2"])
    block = recipe["data_schemas"]["A"]
    if how == "missing":
        del block["completion"]
    elif how == "blank":
        block["completion"]["meaning"] = "   "
    elif how == "no_marker":
        del block["completion"]["marker"]
    elif how == "not_a_mapping":
        block["completion"] = "yes"
    write_recipe(tmp_path / "w.yaml", recipe)
    return orchestrator, recipe


HOWS = ["missing", "blank", "no_marker", "not_a_mapping"]


@pytest.mark.parametrize("how", HOWS)
def test_the_check_refuses_it_and_every_read_gives_one_plain_message_that_names_the_table(tmp_path, how):
    orchestrator, recipe = broken(tmp_path, how)
    refused = check_recipe_file(tmp_path / "w.yaml").errors
    assert [p.code for p in refused if p.code.startswith("E0")], "the recipe check refuses it (E04 to E06): the load gate of HOME refuses what the check refuses"
    expected = pytest.raises(DataAnalysisRecipeError)
    with expected as error:   # the build of any table that reads a participant
        quiet(orchestrator.prepare_ingredient, "B", recipe["data_schemas"]["B"], "w", recipe)
    text = f"{error.value} {error.value.tip}"
    assert "'A'" in text and "completion" in text and "Traceback" not in text and "\n" not in str(error.value)
    with pytest.raises(DataAnalysisRecipeError) as again:   # the checks of the ids
        quiet(orchestrator.id_report, "w", recipe)
    assert "'A'" in str(again.value)


@pytest.mark.parametrize("how", HOWS)
def test_the_data_check_and_the_plan_of_every_place_report_it_and_do_not_raise(tmp_path, how):
    orchestrator, recipe = broken(tmp_path, how)
    check = check_data_analysis_recipe_data(tmp_path / "w.yaml", tmp_path, with_ids=True)
    assert check.problems and any("'A'" in p.text() for p in check.problems), "a plain line that names the table"
    assert check.ids is None and check.ids_error and "'A'" in check.ids_error   # warnings only: said, never raised
    loaded = load_data_analysis_recipe(tmp_path / "w.yaml")
    book = quiet(compose_plan_book, orchestrator, "w", loaded)   # BLUEPRINT's and HOME's plan of every place: a fault of the recipe is a value of the book
    assert book is not None


@pytest.mark.parametrize("how", HOWS)
def test_the_opening_never_raises_whatever_the_recipe_the_keys_or_the_folder_are(tmp_path, how):
    orchestrator, recipe = broken(tmp_path, how)
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run = quiet(run_id_checks, orchestrator, "w", recipe, keys, tmp_path / "user")
    assert run.report is None and run.error and "could not be made" in run.error and "'A'" in run.error and not (tmp_path / "user").exists()


@pytest.mark.parametrize("what", ["no_keys", "keys_without_the_hashes", "no_folder"])
def test_the_opening_never_raises_when_the_keys_or_the_folder_are_wrong_either(tmp_path, what):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    keys = {"no_keys": None, "keys_without_the_hashes": object(), "no_folder": quiet(orchestrator.compute_data_analysis_recipe_keys, "w")}[what]
    folder = None if what == "no_folder" else tmp_path / "user"
    run = quiet(run_id_checks, orchestrator, "w", recipe, keys, folder)
    assert run.report is None and run.error and run.error.startswith("the checks of the ids could not be made"), "said in plain words, never raised"


def test_a_recipe_that_is_correct_still_runs_the_checks_and_writes_the_log(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"]}, metadata=["s1", "s2"])
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    run = quiet(run_id_checks, orchestrator, "w", recipe, keys, tmp_path / "user")
    assert run.error is None and run.report is not None and run.outcome.written


def test_a_blank_sentence_in_a_recipe_is_refused_by_the_gate_of_home_with_a_plain_line(tmp_path):
    broken(tmp_path, "blank")
    problems = [p for p in check_recipe(__import__("yaml").safe_load((tmp_path / "w.yaml").read_text()), "run", file_stem="w").errors]
    assert [p.code for p in problems if p.code == "E05"] and "sentence" in " ".join(p.message + p.fix for p in problems if p.code == "E05")


# -- the ids of a file are read once for the same bytes and the same declarations ----------------------------------

class Counting:
    """Count the reads of ids (`utils.id_completion.read_ids` as the orchestrator calls it)."""

    def __init__(self, monkeypatch):
        import app.modules.orchestrator as orchestrator_module
        self.count = {}
        real = orchestrator_module.read_ids

        def counted(lf, participant):
            self.count[participant.table] = self.count.get(participant.table, 0) + 1
            return real(lf, participant)
        monkeypatch.setattr(orchestrator_module, "read_ids", counted)


def build_all(orchestrator, tmp_path, recipe):
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, "w")
    for name in recipe["data_schemas"]:
        quiet(orchestrator.materialize_tier1, "w", name, tmp_path / f"{name}.parquet", keys=keys)


def test_the_ids_of_a_table_are_read_once_for_a_whole_opening_not_once_per_table_built(tmp_path, monkeypatch):
    names = {t: [f"s{i}" for i in range(3)] for t in "ABCDE"}
    orchestrator, recipe = world(tmp_path, names, metadata=["s0", "s1", "s2", "s9"])
    counting = Counting(monkeypatch)
    build_all(orchestrator, tmp_path, recipe)
    assert counting.count and set(counting.count.values()) == {1}, f"each of the six tables gives its ids once: {counting.count}"
    assert len(counting.count) == 6


def test_a_changed_file_is_read_again_even_when_it_has_the_same_size_and_the_new_ids_are_seen(tmp_path, monkeypatch):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]}, metadata=["s1", "s2"])
    before = {t.table: t for t in quiet(orchestrator.id_report, "w", recipe).tables}
    assert before["A"].added == ("s2",) and before["B"].added == ("s1",)
    (tmp_path / "data" / "B.tsv").write_text("sample_id\tv\ns7\t0\n")   # the same size, other ids
    assert (tmp_path / "data" / "B.tsv").stat().st_size == len("sample_id\tv\ns7\t0\n")
    after = quiet(orchestrator.id_report, "w", recipe)
    by = {t.table: t for t in after.tables}
    assert by["A"].added == ("s2", "s7"), "the new id is in the union and A lacks it"
    assert by["B"].added == ("s1", "s2")


@pytest.mark.parametrize("change", ["strip", "null_values", "id_column_type", "marker"])
def test_a_change_of_a_declaration_that_shapes_the_read_is_read_again(tmp_path, monkeypatch, change):
    orchestrator, recipe = world(tmp_path, {"A": ["s1", " s2"]}, metadata=["s1", "s2"])
    counting = Counting(monkeypatch)
    quiet(orchestrator.id_report, "w", recipe)
    first = counting.count["A"]
    schema = recipe["data_schemas"]["A"]
    if change == "strip":
        schema["strip"] = not schema["strip"]
    elif change == "null_values":
        schema["null_values"] = ["s1"]
    elif change == "id_column_type":
        schema["input_fields"]["sample_id"]["type"] = "Categorical"
    else:
        schema["completion"]["marker"] = "another_marker"
    quiet(orchestrator.id_report, "w", recipe)
    assert counting.count["A"] > first, f"A's ids are read again after a change of {change}"


def test_the_same_bytes_and_declarations_are_not_read_again_by_a_second_report(tmp_path, monkeypatch):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]}, metadata=["s1", "s2"])
    counting = Counting(monkeypatch)
    quiet(orchestrator.id_report, "w", recipe)
    reads_as_read = dict(counting.count)
    quiet(orchestrator.id_report, "w", recipe)
    # the "as read" ids are kept; only the ids of the COMPLETED tables are read again (that is check 3: it must read what the build reads)
    assert all(counting.count[t] - reads_as_read[t] <= 1 for t in reads_as_read), (reads_as_read, counting.count)


def test_a_table_that_cannot_be_read_is_never_kept_and_raises_every_time(tmp_path):
    orchestrator, recipe = world(tmp_path, {"A": ["s1"], "B": ["s2"]}, metadata=["s1"])
    (tmp_path / "data" / "B.tsv").write_text("sample_id\tv\ns2\tnot_a_number\n")   # a value that does not fit its declared type
    for _ in range(2):
        with pytest.raises(Exception) as error:
            quiet(orchestrator.id_report, "w", recipe)
        assert "'B'" in str(error.value)
    (tmp_path / "data" / "B.tsv").write_text("sample_id\tv\ns2\t1\n")
    assert quiet(orchestrator.id_report, "w", recipe).check3_ok, "the repaired file is read and the result is right"


def test_the_memo_is_bounded(tmp_path, monkeypatch):
    import app.modules.orchestrator as orchestrator_module
    monkeypatch.setattr(orchestrator_module, "IDS_MEMO_LIMIT", 3)
    orchestrator, recipe = world(tmp_path, {t: ["s1"] for t in "ABCDEF"}, metadata=["s1"])
    quiet(orchestrator.id_report, "w", recipe)
    assert len(orchestrator._ids_memo) <= 3


def test_the_demo_gives_the_same_report_with_the_memo_as_without_it():
    orchestrator = __import__("app.modules.orchestrator", fromlist=["DataOrchestrator"]).DataOrchestrator(PIPELINES, ROOT)
    raw = load_data_analysis_recipe(PIPELINES / f"{DEMO}.yaml").raw
    first = quiet(orchestrator.id_report, DEMO, raw).as_dict()
    orchestrator._ids_memo.clear()
    again = quiet(orchestrator.id_report, DEMO, raw).as_dict()
    assert first == again and first["check_3"] == "passed"


# -- the sentences of the shipped recipes (the owner, 2026-11-24) -------------------------------------------------

def test_the_demo_says_for_resfinder_what_an_added_line_means_and_every_other_table_has_the_starting_sentence_and_its_own_marker():
    raw = load_data_analysis_recipe(PIPELINES / f"{DEMO}.yaml").raw
    start = id_completion.starting_meaning()
    blocks = {name: t["completion"] for name, t in raw["data_schemas"].items() if "completion" in t}
    blocks["metadata_schema"] = raw["metadata_schema"]["completion"]
    assert blocks["ResFinder"]["meaning"] == "The tool ran and found no resistance gene for this entity: Not Found, counted as 0."
    assert all(b["meaning"] == start for name, b in blocks.items() if name != "ResFinder"), "no scientific meaning is invented"
    assert all(b["marker"] == f"{name}_not_in_original_data" for name, b in blocks.items()), "one pattern for every table, the metadata too"
    assert len({b["marker"] for b in blocks.values()}) == len(blocks)


def test_the_warning_and_the_log_of_the_demo_hold_the_apps_words_and_the_sentence_of_resfinder(tmp_path):
    from app.modules.orchestrator import DataOrchestrator
    loaded = load_data_analysis_recipe(PIPELINES / f"{DEMO}.yaml")
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, DEMO, loaded)
    run = quiet(run_id_checks, orchestrator, DEMO, loaded.raw, keys, tmp_path)
    added = [line for line in run.lines if "were added" in line]
    assert len(added) == 1 and "ResFinder" in added[0] and '"missing in original table"' in added[0] and "Not Found, counted as 0" in added[0]
    assert '"missing in original table"' in run.log_text and "Not Found, counted as 0" in run.log_text
