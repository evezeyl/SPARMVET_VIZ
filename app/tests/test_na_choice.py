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
from app.modules.session_manager import SessionManager, make_audit_step, normalise_audit_steps
from app.modules.t3_audit_engine import _apply_filter_rows, filter_rows_from_nodes
from app.tests.test_filter_defects import LABELS, RULE, _num
from blueprint_arch.t3_translator import UntranslatableNode, translate_plot_steps, translate_t3_node
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.missing_values import count_missing, dialog_missing_lines
from viz_factory.viz_factory import VizFactory


def by_home(lf, row):
    return _apply_filter_rows(lf, [row]).collect()["s"].to_list()


def by_plot(lf, row):
    recipe = {"plots": {"p": {"mapping": {"x": "s"}, "layers": [{"name": "geom_bar", "params": {}}], "filters": [row]}}}
    return VizFactory().render(lf, recipe, "p").data["s"].to_list()


def by_export(lf, row):
    """What the reproducibility export re-runs: the audit node translated to steps, then run as the engine runs them."""
    node = {"node_type": "filter_row", "params": row}
    for step in translate_plot_steps([node]):
        lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    return lf.collect()["s"].to_list()


def expected(rows_kept, na):
    return sorted(rows_kept + ["d"]) if na == "keep" else rows_kept


# `between` has no translation in the export (t3_translator), so the export column is checked for the other operators.
@pytest.mark.parametrize("na", ["keep", "remove"])
@pytest.mark.parametrize("op, value, kept", RULE)
def test_home_plot_and_export_give_the_same_rows_for_keep_and_remove(op, value, kept, na):
    row = {"column": "x", "op": op, "value": value, "na": na}
    got = {"home": by_home(_num(), row), "plot": by_plot(_num(), row)}
    if op != "between":
        got["export"] = by_export(_num(), row)
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
    with pytest.raises(ValueError, match="keep"):
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

OLD_NODE = {"node_type": "filter_row", "id": "old1", "created_at": "2026-11-01T10:00:00", "plot_scope": "subtab_p",
            "params": {"column": "x", "op": "ne", "value": 2.0, "dtype": "Float64"}, "reason": "old", "active": True}


def _write_old_ghost(root, sm):
    from app.modules.cache_keys import canonical_hash
    by_plot_ = {"subtab_p": [OLD_NODE]}
    ghost = {"session_key": "k:k", "data_analysis_recipe_id": "r", "data_analysis_recipe_sha256": "a", "data_batch_hash": "b",
             "saved_at": "2026-11-01T10:00:00", "label": "", "tier_toggle": "T3", "schema_version": 2,
             "t3_audit_steps": [OLD_NODE], "t3_audit_steps_by_plot": by_plot_, "t3_plot_overrides": {},
             "notification_log": [], "t3_audit_steps_sha256": canonical_hash({"t3_audit_steps_by_plot": by_plot_, "t3_plot_overrides": {}})}
    (sm.session_dir("k:k") / "t3_20261101T100000000000.json").write_text(json.dumps(ghost))


def test_an_old_session_gives_the_same_rows_as_before_and_shows_remove(tmp_path):
    sm = SessionManager(tmp_path)
    _write_old_ghost(tmp_path, sm)
    (ghost,) = sm.list_t3_ghosts("k:k")
    by_plot_ = normalise_audit_steps(ghost["t3_audit_steps_by_plot"])
    node = by_plot_["subtab_p"][0]
    assert node["params"]["na"] == "remove"                     # carried and shown as remove
    # the rows of the table: what the old code gave (x != 2 removes the null row), i.e. remove
    (row,) = filter_rows_from_nodes(by_plot_["subtab_p"])
    assert by_home(_num(), row) == by_home(_num(), {k: v for k, v in OLD_NODE["params"].items()}) == ["a", "c", "e"]
    assert by_plot(_num(), row) == ["a", "c", "e"] and by_export(_num(), row) == ["a", "c", "e"]


def test_an_old_session_is_written_with_na_remove_when_it_is_next_saved(tmp_path):
    sm = SessionManager(tmp_path)
    _write_old_ghost(tmp_path, sm)
    (ghost,) = sm.list_t3_ghosts("k:k")
    path = sm.write_t3_ghost("k:k", "r", "a", "b", "T3", t3_audit_steps_by_plot=ghost["t3_audit_steps_by_plot"])
    saved = json.loads(path.read_text())
    assert saved["t3_audit_steps_by_plot"]["subtab_p"][0]["params"]["na"] == "remove"
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
    assert lines == ["1 row has no value in x: it is removed", "1 row has a failed calculation (NaN): not changed by this choice"]
    assert dialog_missing_lines("x", "eq", "keep", counts)[0] == "1 row has no value in x: it is kept"


def test_the_dialog_says_so_when_no_row_has_a_missing_value():
    counts = count_missing(pl.DataFrame({"x": [1.0, 2.0]}), "x")
    assert dialog_missing_lines("x", "eq", "remove", counts) == ["No row has a missing value in x."]


def test_the_dialog_warns_for_not_equal_and_none_of_on_a_column_with_missing_values():
    counts = count_missing(_num(), "x")
    for op in ("ne", "not_in"):
        lines = dialog_missing_lines("x", op, "remove", counts)
        assert any("Polars" in line for line in lines)
    assert not any("Polars" in line for line in dialog_missing_lines("x", "gt", "remove", counts))
