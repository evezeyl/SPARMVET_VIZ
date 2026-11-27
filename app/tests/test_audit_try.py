"""The pure rules of TRYING an audit step on screen (FLOW-1; `app/modules/audit_try.py`).

What the design expects (ledger D-0650, D-0656, D-0662, D-0669, D-0671; `.claude/design/home_audit_what_is_true_now.md`): a step is tried at the place shown plus the other places chosen (when the place
shown is among them), never at a place where the condition does not fit (named, not dropped), never at the metadata or two places on one path; the trial is the step "Add to audit pipeline" writes; the rows each place loses are the engine's own count; a trial ends, with one plain sentence, when the condition, the places, the mode, the recipe or data, the applied steps or the session change.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_try.py -q

FLOW-3: a column DROP is tried like a condition (`tried_drop_nodes`, `drop_fit_problem`, `drops_from_selection`, `panel_model(kind="drop")`): it changes columns and no row, and the panel says so.

Mutation index (each seen failing): MUTATION Y5 `drops_from_selection` returns every column; MUTATION Y6 the panel of a drop counts rows; MUTATION Y1 `trial_places` ignores the selection rule; MUTATION Y2 `fit_problem` drops a place that does not fit instead of refusing; MUTATION Y3 `end_cause`
never reports a change of the condition; MUTATION Y4 `tried_nodes` gives each place its own id.
"""
import polars as pl
import pytest

from app.modules.audit_place_view import STATE_WORDS, TRIAL
from app.modules.audit_places import nodes_signature
from app.modules.audit_trial import PlaceTrial, TRIAL_FOLDER
from app.modules.audit_try import (KIND_DROP, TrialRecord, trial_has_state, NOT_CHANGED, NOTHING_SHOWN, TRIAL_WORDS, band_trial_line, compare_left_label, compare_right_label, drop_condition_lines,
                                   drop_fit_problem, drops_from_selection, end_cause, fit_problem, panel_model, rows_signature, tried_drop_nodes, tried_nodes, trial_places, world_of)
from app.modules.audit_view import PlaceAudit
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.lineage_view import line_text
from app.tests.test_audit_view import RECIPE_ID, World
from utils.lineage_data import lineage_of


@pytest.fixture(scope="module")
def world(tmp_path_factory):
    made = World(tmp_path_factory.mktemp("audit_try"))
    made.lineage = lineage_of(made.loaded.raw, made.plans)
    yield made
    clear_data_analysis_recipe_cache()


def name_of(world):
    return lambda node: line_text(world.lineage.node(node))


def row(column="identity", op="lt", value=99.0, dtype="Float64", na="keep"):
    return {"column": column, "op": op, "value": value, "dtype": dtype, "na": na}


# -- where the tried step is written ------------------------------------------------------------------------------
def test_with_nothing_chosen_the_place_is_the_one_shown(world):
    assert trial_places("T3:amr_heatmap", [], world.graph, world.lineage) == (("T3:amr_heatmap",), "")
    assert trial_places("T1:ResFinder", [], world.graph, world.lineage) == (("T1:ResFinder",), ""), "a TABLE shown is a place a step can be tried at (new in this slice)"


def test_all_the_places_chosen_when_the_place_shown_is_among_them_in_the_order_chosen(world):
    assert trial_places("T1:MLST", ["T1:ResFinder", "T1:MLST"], world.graph, world.lineage) == (("T1:ResFinder", "T1:MLST"), "")


def test_a_selection_that_does_not_hold_the_place_shown_is_refused_in_the_words_of_show_your_selection_first(world):
    places, problem = trial_places("T1:ResFinder", ["T1:MLST"], world.graph, world.lineage)
    assert places == () and problem.startswith("Show your selection first") and problem.endswith("Nothing was tried."), problem


def test_two_places_on_one_path_the_metadata_and_nothing_shown_are_refused_in_plain_words(world):
    places, problem = trial_places("T1:ResFinder", ["T1:ResFinder", "T3:amr_heatmap"], world.graph, world.lineage)
    assert places == () and "lies below" in problem and problem.endswith("Nothing was tried."), "at most one place on a path (D-0553)"
    metadata = world.lineage.metadata_table
    assert metadata
    places, problem = trial_places(f"T1:{metadata}", [], world.graph, world.lineage)
    assert places == () and "metadata" in problem, "the metadata is not a place"
    assert trial_places(None, [], world.graph, world.lineage) == ((), NOTHING_SHOWN)


# -- the condition must fit every place ----------------------------------------------------------------------------
def test_a_condition_that_does_not_fit_a_place_chosen_is_named_and_nothing_is_tried(world):
    # `identity` is in ResFinder and in the Result data (T3) of the plot; it is not in MLST
    problem = fit_problem([row()], ["T1:ResFinder", "T1:MLST"], world.lineage, lambda place: None, name_of(world))
    assert problem.startswith("The condition does not fit every place chosen.") and "MLST" in problem and "ResFinder: Table, T1" not in problem.split("MLST")[0].split("chosen.")[1]
    assert problem.endswith("Choose places where the column is, or build the condition on another table.")
    assert fit_problem([row()], ["T1:ResFinder"], world.lineage, lambda place: None, name_of(world)) == ""


def test_a_column_of_another_type_at_a_place_is_named_with_both_types(world):
    problem = fit_problem([row(dtype="String")], ["T1:ResFinder"], world.lineage, lambda place: None, name_of(world))
    assert "Float64" in problem and "String" in problem


def test_the_columns_of_the_audited_table_decide_when_they_are_given(world):
    without = [(n, t) for n, t in world.lineage.node("T1:ResFinder").columns if n != "identity"]
    problem = fit_problem([row()], ["T1:ResFinder"], world.lineage, lambda place: without, name_of(world))
    assert "identity" in problem and "as it is with the steps now applied or tried" in problem, "a column an applied step dropped is not there"


# -- the nodes handed to the engine --------------------------------------------------------------------------------
def test_one_decision_for_each_row_written_at_each_place_with_the_id_of_the_decision():
    nodes = tried_nodes([row(), row("sample_id", "ne", "x", "String")], ["T1:ResFinder", "T1:MLST"], primary_keys=["sample_id"])
    assert [(n["place"], n["params"]["column"]) for n in nodes] == [("T1:ResFinder", "identity"), ("T1:MLST", "identity"), ("T1:ResFinder", "sample_id"), ("T1:MLST", "sample_id")]
    assert nodes[0]["id"] == nodes[1]["id"] and nodes[2]["id"] == nodes[3]["id"] and nodes[0]["id"] != nodes[2]["id"], "one id for a decision at all its places (linked removal)"
    assert not nodes[0].get("primary_key_warning") and nodes[2]["primary_key_warning"] is True
    assert all(n["reason"] == "" and n["node_type"] == "filter_row" and n["params"]["na"] == "keep" for n in nodes), "no reason: the engine gives its placeholder inside the trial only"


def test_the_rows_signature_changes_with_the_value_and_not_with_the_dtype_text_order():
    assert rows_signature([row(value=1.0)]) != rows_signature([row(value=2.0)])
    assert rows_signature([row()]) == rows_signature([dict(reversed(list(row().items())))])


# -- when a trial ends ---------------------------------------------------------------------------------------------
def make_world(**changes):
    base = dict(mode="audit", recipe="r", keys=("a", "b"), rows=[row()], chosen=["T1:ResFinder"], applied=(), session="")
    base.update(changes)
    return world_of(**base)


@pytest.mark.parametrize("change,word", [
    ({"mode": "exploration"}, "left Audit mode"),
    ({"recipe": "other"}, "another recipe"),
    ({"keys": ("a", "c")}, "recipe or its data changed"),
    ({"session": "t3_2026.json"}, "session was restored"),
    ({"applied": (("x",),)}, "applied or removed"),
    ({"chosen": ["T1:MLST"]}, "places chosen changed"),
    ({"rows": [row(value=1.0)]}, "condition changed"),
    ({"rows": []}, "condition changed"),
    ({"rows": [row(), row("sample_id", "ne", "x", "String")]}, "condition changed"),
])
def test_a_trial_ends_with_one_plain_sentence_for_each_cause(change, word):
    cause = end_cause(make_world(), make_world(**change))
    assert cause and word in cause and cause.endswith("not applied, not saved and not exported."), cause


def test_nothing_changed_nothing_ends_and_the_first_cause_is_the_one_told():
    assert end_cause(make_world(), make_world()) is None
    both = end_cause(make_world(), make_world(mode="exploration", rows=[]))
    assert "left Audit mode" in both and "condition" not in both


# -- the panel from the engine's own numbers ------------------------------------------------------------------------
def test_the_rows_each_place_loses_are_the_engines_count_and_equal_an_independent_count(world, tmp_path):
    audit = PlaceAudit(world.orch, world.anchors, tmp_path / "audit_anchors")
    trial = PlaceTrial(world.orch, audit, tmp_path / TRIAL_FOLDER)
    threshold = 99.0
    nodes = tried_nodes([row(value=threshold)], ["T1:ResFinder"])
    result = trial.try_step(RECIPE_ID, [], nodes, world.plans)
    assert result.error is None
    original = world.orch.materialize_tier1(RECIPE_ID, "ResFinder", world.anchors / "ResFinder.parquet").collect()
    expected = original.filter(pl.col("identity").is_null() | (pl.col("identity") < threshold)).height          # `na: keep`: a row with no value is kept
    model = panel_model(result, ["identity < 99.0"], name_of(world))
    assert result.effects[0].rows_before == original.height and result.effects[0].rows_after == expected
    assert model.effects[0].startswith("ResFinder: Table, T1: the step removes ")
    assert str(original.height - expected) in model.effects[0] and f"of {original.height}" in model.effects[0]
    assert model.heading == TRIAL_WORDS and not model.error
    assert "plots are built from them" in model.reach_summary or "plot are built from them" in model.reach_summary
    assert any(item.startswith("AMR Heatmap") for item in model.reach_items), model.reach_items
    trial.discard()


def test_a_place_where_the_step_removes_nothing_says_so_plainly(world, tmp_path):
    trial = PlaceTrial(world.orch, PlaceAudit(world.orch, world.anchors, tmp_path / "audit_anchors"), tmp_path / TRIAL_FOLDER)
    result = trial.try_step(RECIPE_ID, [], tried_nodes([row(value=-1.0, op="gt")], ["T1:ResFinder"]), world.plans)
    model = panel_model(result, [], name_of(world))
    assert "removes no row" in model.effects[0] and "no row changed" in model.effects[0]
    trial.discard()


def test_a_step_that_cannot_run_shows_its_plain_error_and_nothing_else(world, tmp_path):
    trial = PlaceTrial(world.orch, PlaceAudit(world.orch, world.anchors, tmp_path / "audit_anchors"), tmp_path / TRIAL_FOLDER)
    result = trial.try_step(RECIPE_ID, [], tried_nodes([row("no_such_column", "eq", 1, "Int64")], ["T1:ResFinder"]), world.plans)
    model = panel_model(result, [], name_of(world))
    assert model.error.startswith("This step cannot be tried:") and "no_such_column" in model.error and not model.effects and not model.reach_items
    # the band and the plot label say nothing about a trial: with an error there is no trial state on any item (review of FLOW-1)
    record = TrialRecord(None, ("T1:ResFinder",), (), result, ())
    assert not trial_has_state(record), "a trial whose step cannot run has no state"
    assert band_trial_line("original", trial_has_state(record)) == "" and band_trial_line("audited", trial_has_state(record)) == ""
    assert trial_has_state(TrialRecord(None, (), (), type("R", (), {"error": None})(), ())) and not trial_has_state(None)
    trial.discard()


# -- the words of the three states and of Compare ----------------------------------------------------------------------
def test_the_three_states_are_told_in_words_and_compare_beside_a_trial_says_which_pane_is_which():
    assert TRIAL_WORDS == STATE_WORDS[TRIAL] and "Not applied, not saved, not exported" in TRIAL_WORDS
    assert compare_right_label() == TRIAL_WORDS
    assert compare_left_label(True, False) == "Before this step: your applied steps"
    assert "no earlier step" in compare_left_label(False, False) and "same as the original" in compare_left_label(False, False)
    assert compare_left_label(True, True) == compare_left_label(False, True) == "Original (as read)"
    assert band_trial_line("original", True) == NOT_CHANGED == band_trial_line("audited", True)
    assert band_trial_line(TRIAL, True) == "" and band_trial_line("original", False) == ""


def test_a_condition_is_never_used_on_a_table_other_than_the_one_it_was_built_on():
    from app.modules.t3_audit_engine import BUILT_ELSEWHERE_LINE, rows_built_elsewhere, staged_filter_row
    key_a, key_b = ("recipe", "audit", "T1", None, "A"), ("recipe", "audit", "T1", None, "B")
    row_a = staged_filter_row("x", "eq", 1, "Int64", None, view=key_a)
    assert not rows_built_elsewhere([row_a], key_a)
    assert rows_built_elsewhere([row_a], key_b), "a row built on A is not for B"
    assert rows_built_elsewhere([row_a], None), "no table shown: nothing it was built on"
    assert rows_built_elsewhere([row_a, staged_filter_row("y", "eq", 1, "Int64", None, view=key_b)], key_a), "one row built elsewhere is enough"
    assert rows_built_elsewhere([staged_filter_row("x", "eq", 1, "Int64", None)], key_a), "a row with no view key was built nowhere known"
    assert not rows_built_elsewhere([], key_a), "nothing staged: nothing built elsewhere (the other guard says so)"
    assert "built on another table" in BUILT_ELSEWHERE_LINE and "Nothing was" in BUILT_ELSEWHERE_LINE


# -- FLOW-3: a column drop is tried like a condition ---------------------------------------------------------------------
def test_the_columns_to_drop_are_the_ones_the_chooser_does_not_select_in_the_order_of_the_table():
    names = ["a", "b", "c", "d"]
    assert drops_from_selection(names, ["b", "d"]) == ["a", "c"]
    assert drops_from_selection(names, ("a", "b", "c", "d")) == [], "everything selected: nothing to drop"
    assert drops_from_selection(names, []) == names, "an empty selection drops every column (the engine and the panel then say what that does)"
    assert drops_from_selection(names, None) == [] and drops_from_selection(names, "a") == [], "no chooser on the page: nothing is deselected, never a guess"


def test_one_decision_for_each_column_written_at_each_place_with_no_reason():
    nodes = tried_drop_nodes(["identity", "sample_id", "identity"], ["T3:amr_heatmap", "T1:ResFinder"])
    assert [(n["place"], n["params"]["column"]) for n in nodes] == [("T3:amr_heatmap", "identity"), ("T1:ResFinder", "identity"), ("T3:amr_heatmap", "sample_id"), ("T1:ResFinder", "sample_id")], "a column named twice is one decision"
    assert nodes[0]["id"] == nodes[1]["id"] and nodes[2]["id"] == nodes[3]["id"] and nodes[0]["id"] != nodes[2]["id"]
    assert all(n["node_type"] == "drop_column" and n["reason"] == "" and n["plot_scope"] == "__places__" for n in nodes)


def test_a_drop_that_does_not_fit_a_place_names_the_place_and_the_columns_and_a_type_difference_is_no_problem(world):
    present = lambda place: [("identity", "Float64"), ("sample_id", "String")]
    assert drop_fit_problem(["identity"], ["T3:amr_heatmap"], world.lineage, present, name_of(world)) == ""
    assert drop_fit_problem(["identity"], ["T1:ResFinder"], world.lineage, lambda place: [("identity", "String")], name_of(world)) == "", "a column is dropped whatever it holds"
    text = drop_fit_problem(["identity", "gone"], ["T1:ResFinder", "T3:amr_heatmap"], world.lineage, present, name_of(world))
    assert "does not fit every place" in text and "gone is not in the table there" in text and "Nothing was tried" in text and "identity is not" not in text
    unknown = drop_fit_problem(["identity"], ["T3:amr_heatmap"], world.lineage, lambda place: None, name_of(world))
    assert unknown == "" or "not known" in unknown, "without the audited columns the lineage's plan decides"


def test_the_drop_is_told_in_words_and_says_that_no_row_is_removed():
    one, many = drop_condition_lines(["identity"])[0], drop_condition_lines(["identity", "sample_id"])[0]
    assert one == "Drop the column: identity. No row is removed." and many == "Drop the columns: identity, sample_id. No row is removed."


def test_the_columns_a_drop_removes_are_the_engines_count_rows_are_unchanged_and_the_panel_says_columns_not_rows(world, tmp_path):
    trial = PlaceTrial(world.orch, PlaceAudit(world.orch, world.anchors, tmp_path / "audit_anchors"), tmp_path / TRIAL_FOLDER)
    result = trial.try_step(RECIPE_ID, [], tried_drop_nodes(["identity"], ["T1:ResFinder"]), world.plans)
    assert result.error is None
    original = world.orch.materialize_tier1(RECIPE_ID, "ResFinder", world.anchors / "ResFinder.parquet").collect()
    effect = result.effects[0]
    assert effect.rows_before == effect.rows_after == original.height, "a drop removes no row"
    assert effect.columns_before == original.width and effect.columns_after == original.width - 1 and effect.columns_removed == 1
    assert effect.state == "table changed", "the columns differ, so the table is not the same one although the rows are"
    model = panel_model(result, drop_condition_lines(["identity"]), name_of(world), KIND_DROP)
    assert model.effects[0] == f"ResFinder: Table, T1: the step drops 1 column of {original.width} here (table changed)."
    assert "removes" not in model.effects[0] and "row" not in model.effects[0], "MUTATION Y6: the words of a drop never speak of rows"
    assert trial.trial_table("ResFinder", "T1").collect_schema().names() == [c for c in original.columns if c != "identity"], "the table shown with the trial lacks the column"
    trial.discard()


def test_a_drop_of_a_column_that_is_not_there_is_the_engines_plain_error(world, tmp_path):
    trial = PlaceTrial(world.orch, PlaceAudit(world.orch, world.anchors, tmp_path / "audit_anchors"), tmp_path / TRIAL_FOLDER)
    result = trial.try_step(RECIPE_ID, [], tried_drop_nodes(["no_such_column"], ["T1:ResFinder"]), world.plans)
    model = panel_model(result, [], name_of(world), KIND_DROP)
    assert model.error.startswith("This step cannot be tried:") and "no_such_column" in model.error and not model.effects
    trial.discard()
