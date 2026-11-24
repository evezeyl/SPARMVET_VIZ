"""The choice `na` (keep or remove the rows with no value) reaches every place that filters (NA-RULE-63 part 2, Eve 2026-11-14).

The HOME table, the plot and the re-run of the exported recipe give the same rows for keep and for remove, on every
operator; no audit step is written without `na`; a session written before the choice existed gives the same rows as
before. The expected rows are written by hand (frame x = [1, 2, 3, null, NaN, 2] with labels a..f).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_na_choice.py -q
"""
import json

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.session_manager import SESSION_FORMAT_VERSION, SessionManager, make_audit_step, normalise_audit_steps
from app.modules.t3_audit_engine import _apply_filter_rows
from app.tests.audit_nodes import filter_rows_of as filter_rows_from_nodes
from app.tests.test_filter_defects import LABELS, RULE, _num
from blueprint_arch.t3_translator import UntranslatableNode, translate_t3_node
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.missing_values import count_missing, dialog_missing_lines


def by_home(lf, row):
    return _apply_filter_rows(lf, [row]).collect()["s"].to_list()


def by_plot(lf, row):
    return home_plot_data(lf, [row], {"mapping": {"x": "s"}, "layers": [{"name": "geom_bar", "params": {}}]})["s"].to_list()


def by_export(lf, row):
    """What the reproducibility export re-runs: the audit node translated to steps, then run as the engine runs them."""
    node = {"node_type": "filter_row", "params": row}
    for step in translate_t3_node(node):
        lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    return lf.collect()["s"].to_list()


def expected(rows_kept, na):
    return sorted(rows_kept + ["d"]) if na == "keep" else rows_kept


@pytest.mark.parametrize("na", ["keep", "remove"])
@pytest.mark.parametrize("op, value, kept", RULE)
def test_home_plot_and_export_give_the_same_rows_for_keep_and_remove(op, value, kept, na):
    row = {"column": "x", "op": op, "value": value, "na": na}
    got = {"home": by_home(_num(), row), "plot": by_plot(_num(), row), "export": by_export(_num(), row)}
    assert set(map(tuple, got.values())) == {tuple(expected(kept, na))}, got


def test_a_row_without_na_removes_as_it_always_did():
    row = {"column": "x", "op": "ne", "value": 2.0}
    assert by_home(_num(), row) == by_plot(_num(), row) == ["a", "c", "e"]


def test_na_keep_on_a_text_column_adds_the_null_and_not_the_text_NA():
    lf = pl.LazyFrame({"t": ["a", None, "NA", "b"], "s": ["a", "b", "c", "d"]})
    row = {"column": "t", "op": "ne", "value": "a", "na": "keep"}
    assert by_home(lf, row) == by_plot(lf, row) == by_export(lf, row) == ["b", "c", "d"]


def test_a_column_that_is_all_missing_keep_gives_everything_remove_gives_nothing():
    lf = pl.LazyFrame({"x": pl.Series([None, None], dtype=pl.Float64), "s": ["a", "b"]})
    for op, value in [("eq", 1.0), ("ne", 1.0), ("gt", 1.0), ("in", [1.0]), ("not_in", [1.0])]:
        assert by_home(lf, {"column": "x", "op": op, "value": value, "na": "keep"}) == ["a", "b"]
        assert by_home(lf, {"column": "x", "op": op, "value": value, "na": "remove"}) == []


def test_a_na_that_is_neither_keep_nor_remove_is_refused_not_guessed():
    with pytest.raises(ValueError, match="keep"):
        by_home(_num(), {"column": "x", "op": "eq", "value": 1.0, "na": "maybe"})
    with pytest.raises((ValueError, UntranslatableNode), match="keep"):    # the audited plot reads the step through the one translation, which refuses it
        by_plot(_num(), {"column": "x", "op": "eq", "value": 1.0, "na": "maybe"})


# ── the translator writes the chosen na ─────────────────────────────────────────────────────

def test_the_translator_writes_the_chosen_na_into_the_step():
    for na in ("keep", "remove"):
        (step,) = translate_t3_node({"node_type": "filter_row", "params": {"column": "x", "op": "ne", "value": 1, "na": na}})
        assert step["na"] == na


def test_the_translator_writes_remove_for_an_old_step_without_na():
    (step,) = translate_t3_node({"node_type": "filter_row", "params": {"column": "x", "op": "eq", "value": 1}})
    assert step["na"] == "remove"


def test_the_translator_refuses_a_na_that_is_neither_keep_nor_remove():
    with pytest.raises(UntranslatableNode, match="na"):
        translate_t3_node({"node_type": "filter_row", "params": {"column": "x", "op": "eq", "value": 1, "na": "maybe"}})


def test_a_keep_is_never_exported_as_remove_end_to_end():
    node = make_audit_step("filter_row", {"column": "x", "op": "not_in", "value": [2.0], "na": "keep"}, plot_scope="p")
    assert by_export(_num(), node["params"]) == ["a", "c", "d", "e"]


# ── no audit step is written without na ─────────────────────────────────────────────────────

@pytest.mark.parametrize("node_type", ["filter_row", "exclusion_row"])
def test_make_audit_step_always_records_na_for_a_filter(node_type):
    assert make_audit_step(node_type, {"column": "x", "op": "eq", "value": 1})["params"]["na"] == "remove"
    assert make_audit_step(node_type, {"column": "x", "op": "ne", "value": 1, "na": "keep"})["params"]["na"] == "keep"


def test_make_audit_step_leaves_the_other_node_types_alone():
    assert "na" not in make_audit_step("drop_column", {"column": "x"})["params"]
    assert "na" not in make_audit_step("aesthetic_override", {"alpha": 0.5})["params"]


def test_the_rows_of_a_node_carry_na_so_the_table_the_plot_and_the_bundle_read_it():
    nodes = [make_audit_step("filter_row", {"column": "x", "op": "ne", "value": 2.0, "na": "keep"})]
    (row,) = filter_rows_from_nodes(nodes)
    assert row["na"] == "keep" and by_home(_num(), row) == ["a", "c", "d", "e"]


def test_inactive_nodes_and_other_types_give_no_row():
    nodes = [{**make_audit_step("filter_row", {"column": "x", "op": "eq", "value": 1}), "active": False},
             make_audit_step("drop_column", {"column": "x"})]
    assert filter_rows_from_nodes(nodes) == []


# ── old data: a session written before this change ──────────────────────────────────────────

OLD_NODE = {"node_type": "filter_row", "id": "old1", "created_at": "2026-11-01T10:00:00", "plot_scope": "__places__", "place": "T3:p",
            "params": {"column": "x", "op": "ne", "value": 2.0, "dtype": "Float64"}, "reason": "old", "active": True}


def _write_old_ghost(root, sm):
    from app.modules.cache_keys import canonical_hash
    by_plot_ = {"__places__": [OLD_NODE]}
    ghost = {"session_key": "k:k", "data_analysis_recipe_id": "r", "data_analysis_recipe_sha256": "a", "data_batch_hash": "b",
             "saved_at": "2026-11-01T10:00:00", "label": "", "schema_version": SESSION_FORMAT_VERSION,
             "t3_audit_steps": [OLD_NODE], "t3_audit_steps_by_plot": by_plot_, "t3_plot_overrides": {},
             "notification_log": [], "t3_audit_steps_sha256": canonical_hash({"t3_audit_steps_by_plot": by_plot_, "t3_plot_overrides": {}})}
    (sm.session_dir("k:k") / "t3_20261101T100000000000.json").write_text(json.dumps(ghost))


def test_an_old_session_gives_the_same_rows_as_before_and_shows_remove(tmp_path):
    sm = SessionManager(tmp_path)
    _write_old_ghost(tmp_path, sm)
    (ghost,) = sm.list_t3_ghosts("k:k")
    by_plot_ = normalise_audit_steps(ghost["t3_audit_steps_by_plot"])
    node = by_plot_["__places__"][0]
    assert node["params"]["na"] == "remove"                     # carried and shown as remove
    # the rows of the table: what the old code gave (x != 2 removes the null row), i.e. remove
    (row,) = filter_rows_from_nodes(by_plot_["__places__"])
    assert by_home(_num(), row) == by_home(_num(), {k: v for k, v in OLD_NODE["params"].items()}) == ["a", "c", "e"]
    assert by_plot(_num(), row) == ["a", "c", "e"] and by_export(_num(), row) == ["a", "c", "e"]


def test_an_old_session_is_written_with_na_remove_when_it_is_next_saved(tmp_path):
    sm = SessionManager(tmp_path)
    _write_old_ghost(tmp_path, sm)
    (ghost,) = sm.list_t3_ghosts("k:k")
    path = sm.write_t3_ghost("k:k", "r", "a", "b", t3_audit_steps_by_plot=ghost["t3_audit_steps_by_plot"])
    saved = json.loads(path.read_text())
    assert saved["t3_audit_steps_by_plot"]["__places__"][0]["params"]["na"] == "remove"
    assert saved["t3_audit_steps"][0]["params"]["na"] == "remove"


def test_an_old_step_is_exported_with_na_remove():
    (step,) = translate_t3_node(OLD_NODE)
    assert step["na"] == "remove"


def test_normalising_twice_changes_nothing_and_leaves_a_keep_alone():
    keep = make_audit_step("filter_row", {"column": "x", "op": "ne", "value": 1, "na": "keep"})
    once = normalise_audit_steps({"p": [OLD_NODE, keep]})
    assert normalise_audit_steps(once) == once and once["p"][1]["params"]["na"] == "keep"
    assert "na" not in OLD_NODE["params"]                      # the input is not changed in place


# ── what the dialog says ────────────────────────────────────────────────────────────────────

def test_the_dialog_gives_the_counts_of_missing_values_and_nan_separately():
    counts = count_missing(_num(), "x")
    lines = dialog_missing_lines("x", "eq", "remove", counts)
    assert lines == ["1 row has no value in x: it is removed", "1 row has a failed calculation: this choice does not change it."]
    assert dialog_missing_lines("x", "eq", "keep", counts)[0] == "1 row has no value in x: it is kept"


def test_the_dialog_says_so_when_no_row_has_a_missing_value():
    counts = count_missing(pl.DataFrame({"x": [1.0, 2.0]}), "x")
    assert dialog_missing_lines("x", "eq", "remove", counts) == ["No row has a missing value in x."]


def test_the_dialog_warns_for_not_equal_and_none_of_on_a_column_with_missing_values():
    counts = count_missing(_num(), "x")
    for op in ("ne", "not_in"):
        lines = dialog_missing_lines("x", op, "remove", counts)
        assert any("Tick the box above to keep them" in line for line in lines)
        keep = dialog_missing_lines("x", op, "keep", counts)
        assert any("kept because the box is ticked" in line for line in keep)
    assert not any("box" in line for line in dialog_missing_lines("x", "gt", "remove", counts))


# ── what the user reads: the staged row, the audit card and the report ──────────────────────

def test_the_staged_row_says_what_happens_to_the_rows_with_no_value():
    from app.modules.t3_audit_engine import describe_filter
    assert describe_filter("x", "ne", 2, "keep") == "x ≠ 2 (rows with no value kept)"
    assert describe_filter("x", "ne", 2, "remove") == "x ≠ 2 (rows with no value removed)"
    assert describe_filter("x", "ne", 2) == "x ≠ 2"          # callers that do not pass na keep their line


def test_the_audit_card_shows_the_choice_and_an_old_step_as_remove():
    from app.handlers.audit_stack import _params_summary
    keep = make_audit_step("filter_row", {"column": "x", "op": "ne", "value": 2, "na": "keep"})
    assert _params_summary(keep).endswith("no value: kept")
    assert _params_summary(OLD_NODE).endswith("no value: removed")
    assert "no value" not in _params_summary(make_audit_step("drop_column", {"column": "x"}))


def test_the_report_states_the_choice_for_every_filter_step():
    from app.handlers.export_handlers import _build_methods_section
    plots = [("p", {"title": "P"})]

    def report(node):
        return "\n".join(_build_methods_section(plots, {"p": [node]}, {"d": ["p"]}, ["T1"]))

    assert "keeping the rows with no value in **x**" in report(
        make_audit_step("filter_row", {"column": "x", "op": "ne", "value": "a", "na": "keep"}, reason="r"))
    assert "removing the rows with no value in **x**" in report(
        make_audit_step("filter_row", {"column": "x", "op": "ne", "value": "a", "na": "remove"}, reason="r"))
    assert "removing the rows with no value in **x**" in report(OLD_NODE | {"params": {"column": "x", "op": "ne", "value": "a"}})


# ── the real orchestrator: the table HOME shows and the recipe the export re-runs ───────────

@pytest.fixture
def world(tmp_path):
    from app.modules.cache_keys import clear_data_analysis_recipe_cache
    from app.tests.test_cache_chain import World
    clear_data_analysis_recipe_cache()
    w = World(tmp_path)
    # raw file: s3 has no value in the column "group" (an empty cell)
    w.write_data("sample_id\tgroup\ns1\tA\ns2\tB\ns3\t\ns4\tA\n")
    yield w
    clear_data_analysis_recipe_cache()


def _t1_ids(w):
    return [r["sample_id"] for r in w.build()]


@pytest.mark.parametrize("na", ["keep", "remove"])
@pytest.mark.parametrize("op, value, kept", [
    ("eq", "A", ["s1", "s4"]), ("ne", "A", ["s2"]), ("in", ["A", "B"], ["s1", "s2", "s4"]), ("not_in", ["A"], ["s2"]),
])
def test_the_table_in_home_and_the_rerun_of_the_exported_recipe_give_the_rows_written_by_hand(world, op, value, kept, na):
    assert _t1_ids(world) == ["s1", "s2", "s3", "s4"]                    # the raw file, read once
    row = {"column": "group", "op": op, "value": value, "na": na}
    want = sorted(kept + (["s3"] if na == "keep" else []))
    # HOME: the filter on the table of the orchestrator
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    home = _apply_filter_rows(world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys), [row]).collect()
    assert sorted(home["sample_id"].to_list()) == want
    # the export: the audit step translated, written as tier2 of the recipe, run by the orchestrator
    (step,) = translate_t3_node({"node_type": "filter_row", "params": row})
    world.write_data_analysis_recipe(steps_tier2=[step])
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    rerun = world.orch.materialize_tier2("tiny", "C", world.anchor, keys=keys).collect()
    assert sorted(rerun["sample_id"].to_list()) == want


# ── review fixes (part 2b): audited_frame, the staged row, the audit params, the session, `between` ─────────

from app.tests.audit_nodes import audited_lf as audited_frame  # noqa: E402
from app.tests.audit_nodes import filter_nodes, home_plot_data  # noqa: E402
from app.modules.t3_audit_engine import audit_params_from_row, staged_filter_row  # noqa: E402


@pytest.mark.parametrize("na, kept", [("keep", ["a", "c", "d", "e"]), ("remove", ["a", "c", "e"])])
def test_the_results_bundle_frame_applies_na_keep_and_remove(na, kept):
    rows = [{"column": "x", "op": "ne", "value": 2.0, "na": na}]
    assert audited_frame(_num(), filter_nodes(rows)).collect()["s"].to_list() == kept


def test_the_results_bundle_frame_removes_the_dropped_column_after_a_keep_filter():
    rows = [{"column": "x", "op": "ne", "value": 2.0, "na": "keep"}]
    out = audited_frame(_num(), filter_nodes(rows, ["x"])).collect()
    assert out.columns == ["s"] and out["s"].to_list() == ["a", "c", "d", "e"]


# The staged row: what the dialog writes when "+ Add" is pressed
@pytest.mark.parametrize("op, tick, na", [
    ("eq", True, "keep"), ("eq", False, "remove"), ("ne", True, "keep"), ("ne", False, "remove"),
    ("not_in", False, "remove"), ("gt", True, "keep"),
])
def test_the_staged_row_records_the_tick_whatever_the_default_of_the_operator(op, tick, na):
    assert staged_filter_row("x", op, 2.0, "Float64", tick)["na"] == na


def test_the_staged_row_without_a_tick_uses_the_default_of_the_operator():
    assert staged_filter_row("x", "ne", 2.0, "Float64", None)["na"] == "keep"
    assert staged_filter_row("x", "eq", 2.0, "Float64", None)["na"] == "remove"


def test_the_staged_row_of_between_carries_closed_and_the_others_do_not():
    assert staged_filter_row("x", "between", [1.0, 3.0], "Float64", False, closed="none")["closed"] == "none"
    assert staged_filter_row("x", "between", [1.0, 3.0], "Float64", False)["closed"] == "both"
    assert "closed" not in staged_filter_row("x", "eq", 2.0, "Float64", False, closed="none")


# "Send to Audit": the params of the audit step built from a staged row
@pytest.mark.parametrize("na", ["keep", "remove"])
def test_the_audit_params_carry_the_tick_of_the_staged_row(na):
    row = staged_filter_row("x", "ne", 2.0, "Float64", na == "keep")
    assert audit_params_from_row(row)["na"] == na
    node = make_audit_step("filter_row", audit_params_from_row(row), plot_scope="p")
    assert node["params"]["na"] == na


def test_the_audit_params_carry_closed_exactly_as_chosen_for_between():
    for closed in ("both", "none"):
        row = staged_filter_row("x", "between", [1.0, 3.0], "Float64", False, closed=closed)
        assert audit_params_from_row(row)["closed"] == closed
    assert "closed" not in audit_params_from_row(staged_filter_row("x", "eq", 2.0, "Float64", False))


def test_a_staged_row_of_an_old_state_without_na_gives_remove_in_the_audit_params():
    assert audit_params_from_row({"column": "x", "op": "eq", "value": 1})["na"] == "remove"


# Session: a KEEP step survives the save, the list and the restore
def test_a_keep_step_survives_save_list_and_restore(tmp_path):
    sm = SessionManager(tmp_path)
    keep = make_audit_step("filter_row", {"column": "x", "op": "ne", "value": 2.0, "na": "keep"}, plot_scope="__places__", place="T3:p")
    path = sm.write_t3_ghost("k:k", "r", "a", "b", t3_audit_steps_by_plot={"__places__": [keep]})
    saved = json.loads(path.read_text())
    assert saved["t3_audit_steps_by_plot"]["__places__"][0]["params"]["na"] == "keep"
    assert saved["t3_audit_steps"][0]["params"]["na"] == "keep"
    (ghost,) = sm.list_t3_ghosts("k:k")
    restored = normalise_audit_steps(ghost["t3_audit_steps_by_plot"])
    assert restored["__places__"][0]["params"]["na"] == "keep"
    (row,) = filter_rows_from_nodes(restored["__places__"])
    assert by_home(_num(), row) == ["a", "c", "d", "e"]


def test_a_between_step_keeps_closed_through_save_and_restore(tmp_path):
    sm = SessionManager(tmp_path)
    node = make_audit_step("filter_row", {"column": "x", "op": "between", "value": [1.0, 3.0], "closed": "none", "na": "keep"},
                           plot_scope="__places__", place="T3:p")
    sm.write_t3_ghost("k:k", "r", "a", "b", t3_audit_steps_by_plot={"__places__": [node]})
    (ghost,) = sm.list_t3_ghosts("k:k")
    (row,) = filter_rows_from_nodes(normalise_audit_steps(ghost["t3_audit_steps_by_plot"])["__places__"])
    assert row["closed"] == "none" and row["na"] == "keep"


# `between`: translated to a modif_filter step with its bounds, closed and na (Eve, 2026-11-14)
def test_between_is_translated_with_its_bounds_closed_and_na():
    node = {"node_type": "filter_row", "params": {"column": "x", "op": "between", "value": [1.0, 3.0], "closed": "none", "na": "keep"}}
    assert translate_t3_node(node) == [
        {"action": "modif_filter", "column": "x", "op": "between", "value": [1.0, 3.0], "closed": "none", "na": "keep"}]


def test_between_without_closed_is_closed_on_both_ends_and_an_old_step_removes():
    (step,) = translate_t3_node({"node_type": "filter_row", "params": {"column": "x", "op": "between", "value": [1.0, 3.0]}})
    assert step["closed"] == "both" and step["na"] == "remove"


@pytest.mark.parametrize("value", [[1.0], [1.0, 2.0, 3.0], 5.0, None])
def test_between_without_a_pair_is_refused_not_guessed(value):
    with pytest.raises(UntranslatableNode, match="between"):
        translate_t3_node({"node_type": "filter_row", "params": {"column": "x", "op": "between", "value": value}})


def test_a_step_that_is_not_between_carries_no_closed():
    (step,) = translate_t3_node({"node_type": "filter_row", "params": {"column": "x", "op": "eq", "value": 1, "closed": "none"}})
    assert "closed" not in step


# Four-way on `between`: the table, the plot, the results bundle and the re-run of the export, from the audit step
BETWEEN = {"both": ["a", "b", "c", "f"], "none": ["b", "f"]}   # x = [1, 2, 3, null, NaN, 2], bounds [1, 3]


@pytest.mark.parametrize("na", ["keep", "remove"])
@pytest.mark.parametrize("closed", ["both", "none"])
def test_between_gives_the_same_rows_in_the_table_the_plot_the_bundle_and_the_export(closed, na):
    staged = staged_filter_row("x", "between", [1.0, 3.0], "Float64", na == "keep", closed=closed)
    node = make_audit_step("filter_row", audit_params_from_row(staged), plot_scope="__places__", place="T3:p")
    (row,) = filter_rows_from_nodes([node])
    want = expected(BETWEEN[closed], na)
    got = {"home": by_home(_num(), row), "plot": by_plot(_num(), row),
           "bundle": audited_frame(_num(), filter_nodes([row])).collect()["s"].to_list(), "export": by_export(_num(), node["params"])}
    assert {k: sorted(v) for k, v in got.items()} == {k: sorted(want) for k in got}, got


def test_the_staged_line_of_between_says_when_the_ends_are_not_included():
    from app.modules.t3_audit_engine import describe_filter
    assert describe_filter("x", "between", [1, 3], "remove", "none") == "x between 1 and 3, ends not included (rows with no value removed)"
    assert describe_filter("x", "between", [1, 3], "remove", "both") == "x between 1 and 3 (rows with no value removed)"


def test_a_filter_listed_in_the_inventory_says_what_happens_to_the_rows_with_no_value():
    from utils.na_choice import no_value_text
    assert no_value_text("keep") == "no value: kept" and no_value_text("remove") == "no value: removed"
    with pytest.raises(ValueError):
        no_value_text("maybe")
