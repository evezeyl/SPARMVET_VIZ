"""Every old step and its converted steps give the same table (migration run A, `utils.step_migration`).

The old actions are removed from the engine; what they produced is frozen in `data/step_conversion_snapshot.json`
(made on 2026-11-13 by running each old step through the REAL old path: `DataWrangler` with its column aliases and
defaults, a join through the assembler's action). For each case the converter must still write the frozen new steps,
and those steps, run through the new actions, must give a table with the same rows, columns, types and content hash
as the old action did. Nothing is hand-written on the right: it is what the migration tool writes.

The removed actions and the ones that need a decision are checked to refuse (NotConvertible) with a message.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_step_conversion.py -q
"""
import copy
import datetime
import hashlib
import json
from pathlib import Path

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as A
from utils.step_migration import NotConvertible, REMOVED_ACTIONS, convert_step

NAN = float("nan")
MAIN = pl.DataFrame({
    "id": ["a", "b", "c", "d", "e", "f"],
    "g": ["x", "x", "y", "y", "y", None],
    "v": [1, 2, 3, 4, 5, 6],
    "w": [1.5, None, 2.5, 3.5, 4.5, 5.5],
    "s": ['  "a b"  ', "c", None, ' "d" ', "e f", ""],
    "genes": ["a,b", "c", None, "d,e,f", "g", ""],
    "path": ["a_b_c", "d_e", "f", None, "g_h_i_j", "k"],
    "sp": ["Escherichia/coli", "Klebsiella/pneumoniae", "Salmonella", None, "A/B", "C/D"],
    "amr": ["Susceptible", "unknown1", "R", "S", None, "unknown2"],
    "d": [datetime.date(2022, 3, 15), datetime.date(2022, 4, 2), None, datetime.date(2023, 1, 9), datetime.date(2023, 12, 31), datetime.date(2024, 6, 1)],
    "code": ["A", "B", "A", "C", "B", "B"],
})
LISTS = pl.DataFrame({"id": ["a", "b", "c"], "l": [["p", "q", "r"], ["s"], []]})
STRUCTS = pl.DataFrame({"id": [1, 2], "st": [{"u": 1, "v": "a"}, {"u": 2, "v": "b"}]})
LONG = pl.DataFrame({"id": ["a", "a", "b"], "kind": ["x", "y", "x"], "val": [1, 2, 3]})
BOOLS = pl.DataFrame({"a": [True, False, True], "b": [True, True, False]})
RIGHT = pl.DataFrame({"id": ["a", "b", "z"], "extra": [10, 20, 30], "k": ["p", "q", "r"]})
TEXT_COLUMNS = [n for n, dt in MAIN.schema.items() if dt == pl.String]

# (label, old step, frame); every step is written as an old recipe wrote it
CASES = [
    ("cast", {"action": "cast", "columns": ["v"], "dtype": "Float64"}, MAIN),
    ("coalesce", {"action": "coalesce", "columns": ["g", "s"]}, MAIN),
    ("count_by_group", {"action": "count_by_group", "group_by": ["g"], "new_column": "n"}, MAIN),
    ("count_by_group default", {"action": "count_by_group", "group_by": ["g", "code"]}, MAIN),
    ("cum_sum", {"action": "cum_sum", "column": "v"}, MAIN),
    ("cum_sum named", {"action": "cum_sum", "column": "v", "target_column": "run"}, MAIN),
    ("cum_count", {"action": "cum_count", "column": "w"}, MAIN),
    ("date_extract", {"action": "date_extract", "column": "d", "parts": ["year", "month", "day", "week", "weekday"]}, MAIN),
    ("date_extract default", {"action": "date_extract", "column": "d"}, MAIN),
    ("date_truncate", {"action": "date_truncate", "column": "d", "every": "1y"}, MAIN),
    ("date_truncate default", {"action": "date_truncate", "column": "d"}, MAIN),
    ("describe_stats", {"action": "describe_stats"}, MAIN.select("v", "w")),
    ("divide_columns", {"action": "divide_columns", "numerator": "v", "denominator": "w", "new_column": "r"}, MAIN),
    ("drop_duplicates", {"action": "drop_duplicates", "columns": ["g"]}, MAIN),
    ("unique", {"action": "unique", "columns": ["code"]}, MAIN),
    ("unique_rows", {"action": "unique_rows"}, MAIN.select("g", "code")),
    ("drop_nulls", {"action": "drop_nulls", "columns": ["w"]}, MAIN),
    ("explode", {"action": "explode", "columns": ["l"]}, LISTS),
    ("unnest", {"action": "unnest", "columns": ["st"]}, STRUCTS),
    ("fill_nulls", {"action": "fill_nulls", "columns": ["w"], "value": 0}, MAIN),
    ("fill_nulls_direction forward", {"action": "fill_nulls_direction", "columns": ["w"], "direction": "forward"}, MAIN),
    ("fill_nulls_direction default", {"action": "fill_nulls_direction", "columns": ["w"]}, MAIN),
    ("filter_eq", {"action": "filter_eq", "column": "g", "value": "x"}, MAIN),
    ("filter_eq columns", {"action": "filter_eq", "columns": ["g"], "value": "y"}, MAIN),
    ("filter_ne", {"action": "filter_ne", "column": "g", "value": "x"}, MAIN),
    ("filter_gt", {"action": "filter_gt", "columns": ["v"], "value": 2}, MAIN),
    ("filter_lt", {"action": "filter_lt", "columns": ["w"], "value": 3}, MAIN),
    ("filter_range both", {"action": "filter_range", "columns": ["v"], "min": 2, "max": 5}, MAIN),
    ("filter_range min", {"action": "filter_range", "columns": ["v"], "min": 4}, MAIN),
    ("filter_range max", {"action": "filter_range", "columns": ["w"], "max": 3.5}, MAIN),
    ("is_in", {"action": "is_in", "column": "g", "values": ["x", "y"]}, MAIN),
    ("not_in", {"action": "not_in", "column": "g", "values": ["x"]}, MAIN),
    ("horizontal_stats sum", {"action": "horizontal_stats", "columns": ["v", "w"], "operation": "sum", "target_column": "t"}, MAIN),
    ("horizontal_stats default", {"action": "horizontal_stats", "columns": ["v", "w"]}, MAIN),
    ("horizontal_stats max", {"action": "horizontal_stats", "columns": ["v", "w"], "operation": "max"}, MAIN),
    ("interpolate", {"action": "interpolate", "columns": ["w"]}, MAIN),
    ("label_if", {"action": "label_if", "column": "v", "new_column": "lab", "predicate": ">=", "value": 3, "then": "High", "otherwise": "Low"}, MAIN),
    ("label_if no otherwise", {"action": "label_if", "column": "g", "new_column": "lab", "predicate": "==", "value": "x", "then": "X"}, MAIN),
    ("list_join", {"action": "list_join", "column": "l", "separator": "-"}, LISTS),
    ("list_join default", {"action": "list_join", "column": "l", "target_column": "j"}, LISTS),
    ("list_slice", {"action": "list_slice", "column": "l", "offset": 1, "length": 1}, LISTS),
    ("list_slice default", {"action": "list_slice", "column": "l", "target_column": "sl"}, LISTS),
    ("mutate", {"action": "mutate", "column": "v2", "expression": "pl.col('v') * 2"}, MAIN),
    ("mutate target_column", {"action": "mutate", "target_column": "v3", "expression": "pl.col('v') + 1"}, MAIN),
    ("pivot", {"action": "pivot", "index": "id", "on": "kind", "values": "val", "aggregate_function": "first"}, LONG),
    ("pivot default", {"action": "pivot", "index": ["id"], "on": ["kind"], "values": ["val"]}, LONG),
    ("recode_values", {"action": "recode_values", "column": "amr", "new_column": "n", "rules": [
        {"matches": "Susceptible", "value": 0}, {"starts_with": "unknown", "value": None}, {"matches_any": ["R", "S"], "value": 2}, {"default": 1}]}, MAIN),
    ("recode_values in place", {"action": "recode_values", "column": "code", "rules": [{"contains": "A", "value": "yes"}, {"default": "no"}]}, MAIN),
    ("regex_extract", {"action": "regex_extract", "source": "path", "pattern": "([a-z])_", "target_column": "first"}, MAIN),
    ("regex_extract group", {"action": "regex_extract", "source": "path", "pattern": "([a-z])_([a-z])", "group": 2, "target_column": "second"}, MAIN),
    ("regex_replace", {"action": "regex_replace", "columns": ["path"], "pattern": "_", "value": "-"}, MAIN),
    ("regex_replace default value", {"action": "regex_replace", "columns": ["path"], "pattern": "_"}, MAIN),
    ("rename mapping", {"action": "rename", "mapping": {"g": "group"}}, MAIN),
    ("rename new_name", {"action": "rename", "columns": ["g"], "new_name": "group"}, MAIN),
    ("rename_columns mapping", {"action": "rename_columns", "mapping": {"g": "group", "v": "value"}}, MAIN),
    ("rename_columns lists", {"action": "rename_columns", "columns": ["g", "v"], "new_names": ["group", "value"]}, MAIN),
    ("replace_values", {"action": "replace_values", "columns": ["code"], "to_replace": ["A", "B"], "new_value": "AB"}, MAIN),
    ("round_numeric", {"action": "round_numeric", "columns": ["w"], "decimals": 0}, MAIN),
    ("round_numeric default", {"action": "round_numeric", "columns": ["w"]}, MAIN),
    ("sample", {"action": "sample", "fraction": 0.5, "seed": 3}, MAIN),
    ("sample default", {"action": "sample"}, MAIN),
    ("shift", {"action": "shift", "column": "v", "n": 2}, MAIN),
    ("shift default", {"action": "shift", "column": "v"}, MAIN),
    ("sort by", {"action": "sort", "by": ["g", "v"], "descending": True}, MAIN),
    ("sort columns", {"action": "sort", "columns": ["code"]}, MAIN),
    ("split_and_explode", {"action": "split_and_explode", "columns": ["genes"], "separator": ","}, MAIN),
    ("split_and_explode default", {"action": "split_and_explode", "columns": ["genes"]}, MAIN),
    ("split_column", {"action": "split_column", "columns": ["path"], "new_columns": ["a", "b"], "delimiter": "_"}, MAIN),
    ("split_column default delimiter", {"action": "split_column", "source": "s", "new_columns": ["p", "q"]}, MAIN),
    ("split_to_list", {"action": "split_to_list", "columns": ["genes"], "separator": ","}, MAIN),
    ("split_to_list default", {"action": "split_to_list", "columns": ["genes"]}, MAIN),
    ("strip_whitespace columns", {"action": "strip_whitespace", "columns": ["s"]}, MAIN),
    ("summarize count", {"action": "summarize", "group_by": ["g"], "columns": ["v", "w"], "agg": "count"}, MAIN),
    ("summarize default agg", {"action": "summarize", "group_by": ["g"], "columns": ["v"], "new_name": "n"}, MAIN),
    ("summarize mean", {"action": "summarize", "group_by": ["g", "code"], "columns": ["w"], "agg": "mean"}, MAIN),
    ("summarize unknown agg counts", {"action": "summarize", "group_by": ["g"], "columns": ["v"], "agg": "median"}, MAIN),
    ("to_struct", {"action": "to_struct", "columns": ["v", "w"], "target_column": "vw"}, MAIN),
    ("top_n_other", {"action": "top_n_other", "column": "code", "n": 1}, MAIN),
    ("top_n_other named", {"action": "top_n_other", "column": "code", "n": 2, "other_label": "Rest", "new_column": "t"}, MAIN),
    ("unpivot", {"action": "unpivot", "index": ["id"], "on": ["v", "w"], "variable_name": "var", "value_name": "val"}, MAIN),
    ("unpivot default names", {"action": "unpivot", "index": ["id"], "on": ["v", "w"]}, MAIN),
    ("window_agg", {"action": "window_agg", "column": "v", "partition_by": ["g"], "function": "sum", "target_column": "t"}, MAIN),
    ("window_agg default", {"action": "window_agg", "column": "v", "partition_by": ["g"]}, MAIN),
    ("z_score", {"action": "z_score", "columns": ["v", "w"]}, MAIN),
    ("add_constant", {"action": "add_constant", "new_column": "src", "value": "NORM"}, MAIN),
    ("add_constant number", {"action": "add_constant", "new_column": "one", "value": 1}, MAIN),
    ("all_horizontal", {"action": "all_horizontal", "columns": ["a", "b"], "target_column": "t"}, BOOLS),
    ("any_horizontal", {"action": "any_horizontal", "columns": ["a", "b"], "target_column": "t"}, BOOLS),
]
JOINS = [
    ("join on", {"action": "join", "right_ingredient": "R", "on": "id", "how": "left"}, MAIN),
    ("join default how", {"action": "join", "right_ingredient": "R", "on": ["id"]}, MAIN),
    ("join inner", {"action": "join", "right_ingredient": "R", "on": "id", "how": "inner"}, MAIN),
    ("join left_on right_on", {"action": "join", "right_ingredient": "R", "left_on": "id", "right_on": "id", "how": "left"}, MAIN),
    ("join right", {"action": "join", "right_ingredient": "R", "on": "id", "how": "right"}, MAIN),
    ("join outer", {"action": "join", "right_ingredient": "R", "on": "id", "how": "outer"}, MAIN),
    ("join_filter", {"action": "join_filter", "right_ingredient": "R", "on": "id"}, MAIN),
]


SNAPSHOT = json.loads((Path(__file__).parent / "data" / "step_conversion_snapshot.json").read_text(encoding="utf-8"))


def _record(df: pl.DataFrame) -> dict:
    return {"rows": df.height, "columns": [f"{n}:{d}" for n, d in df.schema.items()],
            "sha256": hashlib.sha256(json.dumps(df.to_dicts(), default=str, sort_keys=True).encode()).hexdigest()}


def _new(steps, frame, right=None):
    lf = frame.lazy()
    for step in steps:
        spec = {k: v for k, v in step.items() if k != "action"}
        if right is not None and step["action"] == "polars_join":
            spec["__right_df__"] = right.lazy()
        lf = A[step["action"]](lf, spec)
    return lf.collect()


ALL_CASES = CASES + JOINS


def test_the_snapshot_covers_every_case():
    assert sorted(SNAPSHOT) == sorted(c[0] for c in ALL_CASES)


@pytest.mark.parametrize("label,step,frame", ALL_CASES, ids=[c[0] for c in ALL_CASES])
def test_the_converter_still_writes_the_frozen_steps(label, step, frame):
    assert json.loads(json.dumps(convert_step(copy.deepcopy(step), strings=TEXT_COLUMNS), default=str)) == SNAPSHOT[label]["new_steps"]


@pytest.mark.parametrize("label,step,frame", ALL_CASES, ids=[c[0] for c in ALL_CASES])
def test_the_converted_steps_give_the_table_the_old_action_gave(label, step, frame):
    converted = convert_step(copy.deepcopy(step), strings=TEXT_COLUMNS)
    right = RIGHT if step["action"] in ("join", "join_filter") else None
    assert _record(_new(converted, frame, right)) == SNAPSHOT[label]["old"]


def test_strip_whitespace_without_columns_uses_the_declared_text_fields():
    step = {"action": "strip_whitespace"}
    converted = convert_step(step, strings=TEXT_COLUMNS)
    assert converted[0]["columns"] == TEXT_COLUMNS
    assert _new(converted, MAIN)["s"].to_list() == ["a b", "c", None, "d", "e f", ""]
    with pytest.raises(NotConvertible, match="declared String fields"):
        convert_step(step)


@pytest.mark.parametrize("action", sorted(REMOVED_ACTIONS))
def test_a_removed_action_is_refused_with_what_to_write_instead(action):
    with pytest.raises(NotConvertible, match=action):
        convert_step({"action": action})


def test_keep_and_drop_columns_wait_for_run_b_and_then_write_the_keys_out():
    for action in ("keep_columns", "drop_columns"):
        with pytest.raises(NotConvertible, match="run B"):
            convert_step({"action": action, "columns": ["g"]})
    assert convert_step({"action": "keep_columns", "columns": ["g", "v"]}, keys=["id"], run="B") == [{"action": "polars_select", "exprs": ["id", "g", "v"]}]
    assert convert_step({"action": "keep_columns", "columns": ["id", "g"]}, keys=["id"], run="B") == [{"action": "polars_select", "exprs": ["id", "g"]}]
    assert convert_step({"action": "drop_columns", "columns": ["id", "g"]}, keys=["id"], run="B") == [{"action": "polars_drop", "columns": ["g"]}]
    with pytest.raises(NotConvertible, match="dropped nothing"):
        convert_step({"action": "drop_columns", "columns": ["id"]}, keys=["id"], run="B")


def test_an_unknown_action_and_a_filter_without_bounds_are_refused():
    with pytest.raises(NotConvertible):
        convert_step({"action": "no_such_action"})
    with pytest.raises(NotConvertible, match="delete the step"):
        convert_step({"action": "filter_range", "columns": ["v"]})


def test_a_comment_survives_on_the_first_converted_step():
    out = convert_step({"action": "split_column", "columns": ["path"], "new_columns": ["a", "b"], "delimiter": "_", "comment": "why"})
    assert out[0]["comment"] == "why" and all("comment" not in s for s in out[1:])


def test_every_converted_step_is_valid_for_its_new_action():
    """The converter may write only parameters that the new action declares and only forms it accepts."""
    from transformer.actions.base import ACTION_SCHEMAS
    from utils.ui_schema import step_problems
    bad = {}
    for label, step, _frame in ALL_CASES:
        for new in convert_step(copy.deepcopy(step), strings=TEXT_COLUMNS):
            spec = {k: v for k, v in new.items() if k != "action"}
            problems = step_problems(new["action"], spec, ACTION_SCHEMAS[new["action"]])
            if problems:
                bad[f"{label} -> {new['action']}"] = [p.text() for p in problems]
    assert bad == {}


# -- what the old actions did that was wrong (frozen findings); the converted steps do the documented thing ----------

def test_drop_duplicates_without_columns_failed_before_and_the_converted_step_deduplicates_all_columns():
    got = _new(convert_step({"action": "drop_duplicates"}), MAIN.select("g", "code"))
    assert got.height == MAIN.select("g", "code").unique(maintain_order=True).height      # the old action raised "at least one key is required"


def test_drop_nulls_without_columns_dropped_nothing_before_and_the_converted_step_drops_rows_with_any_null():
    frame = MAIN.select("g", "w")
    assert _new(convert_step({"action": "drop_nulls"}), frame).height == frame.drop_nulls().height == 4     # the old action kept all 6 rows


def test_null_if_never_nulled_the_column_before_and_the_converted_formula_does():
    new = _new(convert_step({"action": "null_if", "columns": ["code"], "value": "A"}), MAIN)
    assert new["code"].to_list() == [None, "B", None, "C", "B", "B"] and new.columns == MAIN.columns   # the old action left the column and added a stray one


def test_split_column_failed_on_short_values_before_and_the_converted_steps_give_null():
    step = {"action": "split_column", "columns": ["path"], "new_columns": ["a", "b", "c"], "delimiter": "_", "drop_source": True}
    new = _new(convert_step(step), MAIN)                                                                  # the old action raised "index out of bounds"
    assert new["c"].to_list() == ["c", None, None, None, "i_j", None] and "path" not in new.columns


def test_sample_default_fraction_and_seed_are_written_into_the_step():
    converted = convert_step({"action": "sample"})
    assert converted[0]["fraction"] == 0.1 and converted[0]["seed"] == 0
    assert _new(converted, pl.DataFrame({"i": list(range(200))})).height == 20


def test_a_right_join_keeps_the_right_table_order_as_the_old_action_did():
    left = pl.DataFrame({"id": ["a", "b", "c"], "x": [1, 2, 3]})
    right = pl.DataFrame({"id": ["c", "a", "z"], "y": [10, 20, 30]})
    converted = convert_step({"action": "join", "right_ingredient": "R", "on": "id", "how": "right"})
    assert converted[0]["maintain_order"] == "right_left"
    assert _new(converted, left, right)["id"].to_list() == ["c", "a", "z"]


def test_strip_whitespace_in_a_schema_without_string_fields_did_nothing_and_is_removed():
    """The old step acted on the String columns only; `categorical` fields were Categorical by then, so it did nothing."""
    assert convert_step({"action": "strip_whitespace"}, strings=[]) == []
