"""A filter written with the control that fits the column type keeps the same rows in the HOME table, the plot, the results bundle
and the re-run of the exported recipe (FILTER-PICKERS-1, Eve 2026-11-15, D9).

The rows are built the way the dialog builds them (`dialog_value` then `staged_filter_row`), for a date, a true/false, a time of
day, a duration and a date and time column, every operator the dialog offers for it, keeping and removing the rows with no
value. An OLD audit step on a time column (what the app wrote before the typed values: the text of the time with the dtype) is
checked too, and a value of 0 or False must survive the check the app makes on an audit step.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_four_way_pickers.py -q
"""
import datetime

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.renamed_keys import audit_step_defect
from app.modules.t3_audit_engine import (
    _apply_filter_rows, audited_frame, compose_datetime, compose_duration, compose_time, dialog_value, ops_for_column, staged_filter_row,
)
from app.tests.audit_nodes import filter_nodes, home_plot_data
from blueprint_arch.t3_translator import translate_t3_node
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

D, T = datetime.date, datetime.time
SECONDS = [60, 5400, 7200, None]   # a: one minute, b: 90 minutes, c: two hours, d: no value
FRAME = pl.DataFrame({
    "s": ["a", "b", "c", "d"],
    "n": [1, 2, 3, 4],
    "d": [D(2020, 1, 1), D(2020, 1, 2), D(2020, 1, 3), None],
    "b": [True, False, True, None],
    "t": pl.Series([T(9, 0), T(10, 30), T(10, 30, 0, 250000), None], dtype=pl.Time),
    "u": pl.Series([None if x is None else x * 10**9 for x in SECONDS], dtype=pl.Int64).cast(pl.Duration("ns")).dt.cast_time_unit("us"),
    "dt": pl.Series([datetime.datetime(2020, 1, 1, 9), datetime.datetime(2020, 1, 2, 10, 30), datetime.datetime(2020, 1, 3, 0, 0, 0, 250000), None],
                    dtype=pl.Datetime("us")),
})
LF = FRAME.lazy()


def home_table(rows):
    return _apply_filter_rows(FRAME.lazy(), rows).collect()["s"].to_list()


def bundle(rows):
    return audited_frame(FRAME.lazy(), filter_nodes(rows)).collect()["s"].to_list()


def plot(rows):
    return home_plot_data(FRAME.lazy(), rows, {"mapping": {"x": "s", "y": "n"}, "layers": [{"name": "geom_col", "params": {}}]})["s"].to_list()


def rerun(rows):
    lf = FRAME.lazy()
    for r in rows:
        for step in translate_t3_node({"node_type": "filter_row", "params": r}):
            lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    return lf.collect()["s"].to_list()


def agree(rows, expected):
    got = {"table": home_table(rows), "bundle": bundle(rows), "plot": plot(rows), "re-run": rerun(rows)}
    assert got == {k: expected for k in got}, got


def dialog_row(column, op, na="remove", **widgets):
    """The row "+ Add" stages for what the controls hold."""
    chosen = dialog_value(LF, column, FRAME.schema[column], False, op, **widgets)
    assert chosen is not None
    op, value, closed = chosen
    return staged_filter_row(column, op, value, str(FRAME.schema[column]), na == "keep", closed=closed)


def with_missing(kept, na):
    return kept + (["d"] if na == "keep" else [])


NA = ["remove", "keep"]


@pytest.mark.parametrize("na", NA)
@pytest.mark.parametrize("op, picked, kept", [
    ("eq", D(2020, 1, 2), ["b"]), ("ne", D(2020, 1, 2), ["a", "c"]), ("gt", D(2020, 1, 2), ["c"]), ("ge", D(2020, 1, 2), ["b", "c"]),
    ("lt", D(2020, 1, 2), ["a"]), ("le", D(2020, 1, 2), ["a", "b"]),
])
def test_date_picker(op, picked, kept, na):
    agree([dialog_row("d", op, na, operand=picked)], with_missing(kept, na))


@pytest.mark.parametrize("closed, kept", [("both", ["a", "b", "c"]), ("left", ["a", "b"]), ("right", ["b", "c"]), ("none", ["b"])])
def test_two_date_pickers_with_the_four_ends(closed, kept):
    agree([dialog_row("d", "between", low=D(2020, 1, 3), high=D(2020, 1, 1), closed=closed)], kept)


def test_date_list_is_kept():
    agree([dialog_row("d", "in", picked=["2020-01-01", "2020-01-03"])], ["a", "c"])
    agree([dialog_row("d", "not_in", picked=["2020-01-02"])], ["a", "c"])


@pytest.mark.parametrize("na", NA)
@pytest.mark.parametrize("op, raw, kept", [("eq", "true", ["a", "c"]), ("ne", "true", ["b"]), ("eq", "false", ["b"]), ("ne", "false", ["a", "c"])])
def test_true_false_control(op, raw, kept, na):
    agree([dialog_row("b", op, na, operand=raw)], with_missing(kept, na))


@pytest.mark.parametrize("na", NA)
@pytest.mark.parametrize("op, hms, kept", [
    ("eq", (10, 30, 0), ["b"]), ("ne", (10, 30, 0), ["a", "c"]), ("gt", (10, 30, 0), ["c"]), ("ge", (10, 30, 0), ["b", "c"]),
    ("lt", (10, 30, 0), ["a"]), ("le", (10, 30, 0), ["a", "b"]), ("eq", (10, 30, 0.25), ["c"]),
])
def test_time_boxes(op, hms, kept, na):
    agree([dialog_row("t", op, na, operand=compose_time(*hms))], with_missing(kept, na))


@pytest.mark.parametrize("closed, kept", [("both", ["a", "b"]), ("left", ["a"]), ("right", ["b"]), ("none", [])])
def test_two_time_boxes_with_the_four_ends(closed, kept):
    agree([dialog_row("t", "between", low=compose_time(10, 30, 0), high=compose_time(9, 0, 0), closed=closed)], kept)


@pytest.mark.parametrize("na", NA)
@pytest.mark.parametrize("op, number, unit, kept", [
    ("eq", 90, "min", ["b"]), ("ne", 90, "min", ["a", "c"]), ("gt", 1.5, "h", ["c"]), ("ge", 5400, "s", ["b", "c"]),
    ("lt", 2, "h", ["a", "b"]), ("le", 1, "min", ["a"]), ("eq", 0, "s", []),
])
def test_duration_number_and_unit(op, number, unit, kept, na):
    agree([dialog_row("u", op, na, operand=compose_duration(number, unit))], with_missing(kept, na))


@pytest.mark.parametrize("closed, kept", [("both", ["a", "b"]), ("left", ["a"]), ("right", ["b"]), ("none", [])])
def test_two_durations_with_the_four_ends(closed, kept):
    agree([dialog_row("u", "between", low=compose_duration(1.5, "h"), high=compose_duration(1, "min"), closed=closed)], kept)


@pytest.mark.parametrize("na", NA)
@pytest.mark.parametrize("op, parts, kept", [
    ("eq", (D(2020, 1, 2), 10, 30, 0), ["b"]), ("ne", (D(2020, 1, 2), 10, 30, 0), ["a", "c"]), ("gt", (D(2020, 1, 2), 10, 30, 0), ["c"]),
    ("ge", (D(2020, 1, 2), 10, 30, 0), ["b", "c"]), ("lt", (D(2020, 1, 2), 10, 30, 0), ["a"]), ("le", (D(2020, 1, 1), 9, 0, 0), ["a"]),
    ("eq", (D(2020, 1, 3), 0, 0, 0.25), ["c"]),
])
def test_date_and_time_picker(op, parts, kept, na):
    agree([dialog_row("dt", op, na, operand=compose_datetime(*parts))], with_missing(kept, na))


@pytest.mark.parametrize("closed, kept", [("both", ["a", "b"]), ("left", ["a"]), ("right", ["b"]), ("none", [])])
def test_two_date_and_time_pickers_with_the_four_ends(closed, kept):
    low, high = compose_datetime(D(2020, 1, 2), 10, 30, 0), compose_datetime(D(2020, 1, 1), 9, 0, 0)
    agree([dialog_row("dt", "between", low=low, high=high, closed=closed)], kept)


def test_date_and_time_exact_list_is_kept():
    agree([dialog_row("dt", "in", picked=["2020-01-02 10:30:00.000000"])], ["b"])


@pytest.mark.parametrize("op, value, kept", [
    ("in", ["10:30:00"], ["b"]), ("not_in", ["10:30:00"], ["a", "c"]), ("eq", ["10:30:00"], ["b"]), ("in", ["09:00:00", "10:30:00.25"], ["a", "c"]),
])
@pytest.mark.parametrize("na", NA)
def test_an_old_audit_step_on_a_time_column_works_again(op, value, kept, na):
    """The app could write this before the typed values (the text of the time and the dtype); the table, the plot, the bundle and the
    re-run refused it for a while ("not offered"); it works again."""
    row = {"column": "t", "op": op, "value": value, "dtype": "Time", "na": na}
    agree([row], with_missing(kept, na))


def test_an_old_audit_step_with_a_scalar_text_on_a_time_column_works():
    agree([{"column": "t", "op": "gt", "value": "10:00:00", "dtype": "Time", "na": "remove"}], ["b", "c"])


@pytest.mark.parametrize("column, op, widgets", [
    ("b", "eq", {"operand": "false"}),                      # False
    ("t", "ge", {"operand": compose_time(0, 0, 0)}),         # midnight, the "0" time
    ("u", "ge", {"operand": compose_duration(0, "s")}),      # a duration of 0
])
def test_a_value_of_false_or_zero_passes_the_check_of_an_audit_step(column, op, widgets):
    row = dialog_row(column, op, **widgets)
    node = {"node_type": "filter_row", "params": {k: row[k] for k in ("column", "op", "value", "na")}}
    assert audit_step_defect(node) is None, row
    assert len(audited_frame(FRAME.lazy(), [{**node, "reason": "r"}]).collect()) >= 0


@pytest.mark.parametrize("dtype", [pl.Date, pl.Boolean, pl.Time, pl.Duration, pl.Datetime("us")])
def test_the_operators_offered_are_the_ones_the_four_views_run(dtype):
    """Every operator the dialog offers for the type is run by the table, the plot, the bundle and the re-run, with a value of that type."""
    column = {pl.Date: "d", pl.Boolean: "b", pl.Time: "t", pl.Duration: "u"}.get(dtype, "dt")
    sample = {"d": "2020-01-02", "b": True, "t": "10:30:00", "u": "90 min", "dt": "2020-01-02 10:30:00"}[column]
    for op in ops_for_column(FRAME.schema[column], False):
        value = [sample, sample] if op == "between" else ([sample] if op in ("in", "not_in") else sample)
        if column == "b" and op in ("in", "not_in"):
            continue
        row = {"column": column, "op": op, "value": sorted(value) if op == "between" else value, "dtype": str(FRAME.schema[column]), "na": "remove"}
        got = [home_table([row]), bundle([row]), plot([row]), rerun([row])]
        assert got[0] == got[1] == got[2] == got[3], (column, op, got)
