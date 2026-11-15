"""The four views of a filter give the same rows: HOME table, plot, results bundle, re-run of the exported recipe (ADR-104 point 7).

For every operator, on a whole-number, a decimal and a text column, keeping and removing the rows with no value. The rows are
written by hand. A step the panel stored before the real value was kept (text with a dtype) is checked too: the export reads
it from the dtype and the four views still agree. A true/false column and a date column are checked on the operators the
panel offers there (is one of, none of, equal, not equal).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_four_way.py -q
"""
import datetime

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.handlers.export_handlers import audited_frame
from app.modules.t3_audit_engine import _apply_filter_rows
from blueprint_arch.t3_translator import translate_t3_node
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from viz_factory.viz_factory import VizFactory

D = datetime.date
FRAME = pl.DataFrame({
    "s": ["a", "b", "c", "d"],
    "n": [1, 2, 3, 4],
    "i": [89, 90, 91, None],
    "f": [89.0, 90.0, 91.0, None],
    "t": ["89", "90", "91", None],
    "b": [True, False, True, None],
    "d": [D(2020, 1, 1), D(2020, 1, 2), D(2020, 1, 3), None],
    "dt": [datetime.datetime(2020, 1, 1, 9), datetime.datetime(2020, 1, 2, 10, 30), datetime.datetime(2020, 1, 3, 0, 0, 0, 250000), None],
})


def home_table(rows):
    return _apply_filter_rows(FRAME.lazy(), rows).collect()["s"].to_list()


def bundle(rows):
    return audited_frame(FRAME.lazy(), rows, []).collect()["s"].to_list()


def plot(rows):
    recipe = {"plots": {"p": {"mapping": {"x": "s", "y": "n"}, "layers": [{"name": "geom_col", "params": {}}], "filters": rows}}}
    return VizFactory().render(FRAME.lazy(), recipe, "p").data["s"].to_list()


def rerun(rows):
    lf = FRAME.lazy()
    for r in rows:
        for step in translate_t3_node({"node_type": "filter_row", "params": r}):
            lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    return lf.collect()["s"].to_list()


def agree(rows, expected):
    assert home_table(rows) == bundle(rows) == plot(rows) == rerun(rows) == expected


def stored(column, op, value, na, **extra):
    """A filter row as the panel stores it: dtype of the column and the choice for the rows with no value."""
    return {"column": column, "op": op, "value": value, "dtype": str(FRAME.schema[column]), "na": na, **extra}


# (op, value, rows kept; the row "d" has no value and is added when na is keep)
NUMBER = [
    ("eq", 90, ["b"]), ("ne", 90, ["a", "c"]), ("gt", 90, ["c"]), ("ge", 90, ["b", "c"]), ("lt", 90, ["a"]), ("le", 90, ["a", "b"]),
    ("in", [89, 91], ["a", "c"]), ("not_in", [89, 91], ["b"]), ("between", [89, 90], ["a", "b"]),
    ("eq", 90.5, []), ("ne", 90.5, ["a", "b", "c"]), ("ge", 90.5, ["c"]), ("lt", 90.5, ["a", "b"]),
    ("in", [90.5, 91], ["c"]), ("not_in", [90.5, 91], ["a", "b"]),
]
TEXT = [
    ("eq", "90", ["b"]), ("ne", "90", ["a", "c"]), ("gt", "90", ["c"]), ("ge", "90", ["b", "c"]), ("lt", "90", ["a"]),
    ("le", "90", ["a", "b"]), ("in", ["89", "91"], ["a", "c"]), ("not_in", ["89", "91"], ["b"]), ("eq", "90.5", []),
]


@pytest.mark.parametrize("na", ["remove", "keep"])
@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("op, value, kept", NUMBER)
def test_number_columns_four_views_agree(column, op, value, kept, na):
    agree([stored(column, op, value, na)], kept + (["d"] if na == "keep" else []))


@pytest.mark.parametrize("na", ["remove", "keep"])
@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("op, value, kept", [c for c in NUMBER if c[0] != "between"])
def test_old_step_with_the_value_as_text_four_views_agree(column, op, value, kept, na):
    """A step written before the real value was kept: the value is text, the step carries the dtype of the column."""
    text = [str(v) for v in value] if isinstance(value, list) else str(value)
    agree([stored(column, op, text, na)], kept + (["d"] if na == "keep" else []))


@pytest.mark.parametrize("na", ["remove", "keep"])
@pytest.mark.parametrize("op, value, kept", TEXT)
def test_text_column_four_views_agree(op, value, kept, na):
    agree([stored("t", op, value, na)], kept + (["d"] if na == "keep" else []))


@pytest.mark.parametrize("closed, kept", [("both", ["a", "b", "c"]), ("left", ["a", "b"]), ("right", ["b", "c"]), ("none", ["b"])])
@pytest.mark.parametrize("column", ["i", "f"])
def test_between_four_ends_four_views_agree(column, closed, kept):
    agree([stored(column, "between", [89, 91], "remove", closed=closed)], kept)


@pytest.mark.parametrize("na", ["remove", "keep"])
@pytest.mark.parametrize("op, value, kept", [
    ("in", [True], ["a", "c"]), ("not_in", [True], ["b"]), ("eq", True, ["a", "c"]), ("ne", True, ["b"]), ("in", [False], ["b"]),
])
def test_true_false_column_four_views_agree(op, value, kept, na):
    agree([stored("b", op, value, na)], kept + (["d"] if na == "keep" else []))


@pytest.mark.parametrize("op, value", [("in", ["True"]), ("not_in", ["True"]), ("eq", "True"), ("ne", "True")])
def test_old_step_with_true_as_text_keeps_the_rows_it_means(op, value):
    """The panel showed "True"; the old step holds that text. It meant the true rows, not no rows."""
    want = ["a", "c"] if op in ("in", "eq") else ["b"]
    agree([stored("b", op, value, "remove")], want)


@pytest.mark.parametrize("op, value, kept", [
    ("in", ["2020-01-02"], ["b"]), ("not_in", ["2020-01-02"], ["a", "c"]), ("in", ["2020-01-01", "2020-01-03"], ["a", "c"]),
])
def test_date_column_four_views_agree(op, value, kept):
    """The panel keeps a date as year-month-day text (a session file holds no date object); the export types it from the dtype."""
    agree([stored("d", op, value, "remove")], kept)


@pytest.mark.parametrize("na", ["remove", "keep"])
@pytest.mark.parametrize("op, value, kept", [
    ("in", ["2020-01-02 10:30:00"], ["b"]), ("not_in", ["2020-01-02 10:30:00"], ["a", "c"]),
    ("in", ["2020-01-01 09:00:00", "2020-01-03 00:00:00.250000"], ["a", "c"]), ("eq", ["2020-01-02 10:30:00"], ["b"]),
])
def test_datetime_column_four_views_agree(op, value, kept, na):
    """What the dialog lists for a date and time column, once picked, keeps the same rows in the table, the plot, the bundle and the
    re-run of the export (reviewer 2026-11-15: it used to keep none, silently, and the re-run raised a raw Polars error)."""
    agree([stored("dt", op, value, na)], kept + (["d"] if na == "keep" else []))


def test_the_dialog_list_of_a_datetime_column_picks_rows_in_every_view():
    from app.modules.t3_audit_engine import dialog_value, value_choices
    lf = FRAME.lazy()
    label = next(iter(value_choices(lf, "dt")))
    op, value, _ = dialog_value(lf, "dt", FRAME.schema["dt"], False, "in", picked=[label])
    agree([stored("dt", op, value, "remove")], ["a"])
