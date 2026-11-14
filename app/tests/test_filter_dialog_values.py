"""The pure side of the HOME filter dialog: types from the schema, values from the whole column, a map from the text shown to
the real value, the operators and the widget by type, the four ends of `between` (ADR-104 points 4, 7 and 8).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_dialog_values.py -q
"""
import datetime
import math

import polars as pl
import pytest

from app.modules.t3_audit_engine import (
    CLOSED_CHOICES, between_prose, closed_phrase, column_type_line, column_types, describe_filter, number_range,
    ops_for_column, pick_values, typed_number, value_choices, value_widget_for,
)
from utils.filter_values import FilterValueError

D = datetime.date


def late_frame(n=1200):
    """More than 500 rows; the values `late` and 2099 appear only after row 500."""
    texts = ["early"] * (n - 1) + ["late"]
    years = [2000 + i % 3 for i in range(n - 1)] + [2099]
    return pl.LazyFrame({"t": texts, "year": years})


# -- the whole column, not the first 500 rows

def test_the_sample_of_500_rows_would_miss_a_late_value():
    """The reason for the rule: the old dialog read `lf.head(500)`; the late values are not in it."""
    head = late_frame().head(500).collect()
    assert "late" not in head["t"].to_list() and 2099 not in head["year"].to_list()


def test_a_value_that_appears_after_row_500_is_offered():
    assert "late" in value_choices(late_frame(), "t")
    assert "2099" in value_choices(late_frame(), "year")
    assert value_choices(late_frame(), "year")["2099"] == 2099


def test_the_range_of_a_number_box_is_the_range_of_the_whole_column():
    assert number_range(late_frame(), "year") == (2000, 2099)


# -- the map from the text shown to the real value

def test_a_number_column_shown_as_a_list_keeps_real_numbers_in_numeric_order():
    lf = pl.LazyFrame({"y": [10, 2, 1998, 2, None]})
    choices = value_choices(lf, "y")
    assert list(choices) == ["2", "10", "1998"] and list(choices.values()) == [2, 10, 1998]
    assert all(type(v) is int for v in choices.values())


def test_a_float_column_keeps_real_floats_and_leaves_out_nan_and_missing():
    lf = pl.LazyFrame({"x": [1.5, 2.0, float("nan"), None]})
    choices = value_choices(lf, "x")
    assert list(choices.values()) == [1.5, 2.0] and all(type(v) is float for v in choices.values())
    assert not any(math.isnan(v) for v in choices.values())


def test_a_true_false_column_keeps_real_booleans():
    choices = value_choices(pl.LazyFrame({"b": [True, False, True, None]}), "b")
    assert choices == {"False": False, "True": True}
    assert all(type(v) is bool for v in choices.values())


def test_a_date_column_keeps_the_year_month_day_text_which_a_session_file_can_hold():
    choices = value_choices(pl.LazyFrame({"d": [D(2020, 1, 2), D(2020, 1, 1), None]}), "d")
    assert choices == {"2020-01-01": "2020-01-01", "2020-01-02": "2020-01-02"}


def test_text_and_category_columns_keep_text():
    lf = pl.LazyFrame({"t": ["b", "a", None], "k": pl.Series(["y", "x", "y"], dtype=pl.Categorical)})
    assert value_choices(lf, "t") == {"a": "a", "b": "b"}
    assert value_choices(lf, "k") == {"x": "x", "y": "y"}


def test_pick_values_returns_the_real_values_in_the_order_picked():
    choices = value_choices(pl.LazyFrame({"y": [1998, 2000, 2003]}), "y")
    assert pick_values(choices, ["2003", "1998"]) == [2003, 1998]
    assert pick_values(choices, []) == []


def test_pick_values_reports_a_text_that_is_not_in_the_column():
    with pytest.raises(FilterValueError) as exc:
        pick_values({"1": 1}, ["2"])
    assert "'2'" in str(exc.value)


# -- the type, from the schema of the table

def test_the_type_comes_from_the_schema_not_from_the_first_rows():
    lf = pl.LazyFrame({"a": [None] * 20 + [5], "b": ["x"] * 21}, schema={"a": pl.Int64, "b": pl.String})
    assert column_types(lf) == {"a": pl.Int64, "b": pl.String}


def test_the_screen_says_what_the_column_holds_in_plain_words():
    assert column_type_line("Year", pl.Int64) == "Year holds whole numbers (Int64)."
    assert column_type_line("flag", pl.Boolean) == "flag holds true or false (Boolean)."
    assert column_type_line("name", pl.String) == "name holds text (String)."


# -- operators and the value widget by type

def test_a_number_column_on_a_discrete_axis_offers_the_list_operators_and_the_comparisons():
    assert ops_for_column(pl.Int64, True) == ["in", "not_in", "eq", "ne", "gt", "ge", "lt", "le", "between"]


def test_a_number_column_that_is_not_a_discrete_axis_offers_the_comparisons():
    assert ops_for_column(pl.Float64, False) == ["eq", "ne", "gt", "ge", "lt", "le", "between"]


@pytest.mark.parametrize("dtype", [pl.String, pl.Boolean, pl.Date, pl.Categorical])
def test_other_columns_offer_the_list_operators(dtype):
    assert ops_for_column(dtype, False) == ops_for_column(dtype, True) == ["in", "not_in", "eq", "ne"]


@pytest.mark.parametrize("op, widget", [
    ("in", "list"), ("not_in", "list"), ("eq", "list"), ("ne", "list"),
    ("gt", "number"), ("ge", "number"), ("lt", "number"), ("le", "number"), ("between", "range"),
])
def test_a_comparison_on_a_discrete_year_uses_the_number_box_a_list_operator_the_list(op, widget):
    """"> 1998 and < 2003" can be written on a Year that is a discrete axis (Eve, 2026-11-14)."""
    assert value_widget_for(pl.Int64, True, op) == widget


@pytest.mark.parametrize("op, widget", [("eq", "number"), ("ne", "number"), ("gt", "number"), ("between", "range")])
def test_a_number_column_that_is_not_discrete_uses_the_number_box(op, widget):
    assert value_widget_for(pl.Float64, False, op) == widget


@pytest.mark.parametrize("dtype", [pl.String, pl.Boolean, pl.Date])
def test_other_columns_use_the_list(dtype):
    assert {value_widget_for(dtype, False, op) for op in ("in", "not_in", "eq", "ne")} == {"list"}


# -- a number from the number box has the type of the column

@pytest.mark.parametrize("raw, dtype, expected", [(1998, pl.Int64, 1998), (1998.0, pl.Int64, 1998), (90.5, pl.Int64, 90.5), (90, pl.Float64, 90.0)])
def test_a_number_of_the_box_is_typed_from_the_schema(raw, dtype, expected):
    got = typed_number(raw, dtype)
    assert got == expected and type(got) is type(expected)


def test_an_empty_number_box_is_reported():
    with pytest.raises(FilterValueError):
        typed_number(None, pl.Int64)


# -- the four ends of between

def test_there_are_four_ends_each_in_plain_words():
    assert list(CLOSED_CHOICES) == ["both", "left", "right", "none"]
    assert CLOSED_CHOICES["both"].startswith("both ends included")
    assert all("recipe" not in v.lower() and "closed" not in v.lower() for v in CLOSED_CHOICES.values())


@pytest.mark.parametrize("closed, phrase", [
    ("both", "both ends included"), ("left", "the lower end included, the upper end not"),
    ("right", "the upper end included, the lower end not"), ("none", "neither end included"),
])
def test_the_closed_phrase(closed, phrase):
    assert closed_phrase(closed) == phrase


def test_the_report_sentence_says_the_ends():
    assert between_prose([89, 91], "left") == 'between "89" and "91", the lower end included, the upper end not'
    assert between_prose([89, 91], "both") == 'between "89" and "91", both ends included'


@pytest.mark.parametrize("closed, suffix", [
    ("both", ""), ("left", ", lower end included, upper end not"), ("right", ", upper end included, lower end not"),
    ("none", ", ends not included"),
])
def test_the_staged_line_says_the_ends_unless_both(closed, suffix):
    assert describe_filter("x", "between", [1, 3], None, closed) == f"x between 1 and 3{suffix}"


# -- the report and the audit panel say the ends

def _methods(params):
    from app.handlers.export_handlers import _build_methods_section
    node = {"node_type": "filter_row", "params": params, "reason": "poor quality"}
    return "\n".join(_build_methods_section([("p", {"title": "P"})], {"p": [node]}, {}, ["T1"]))


@pytest.mark.parametrize("closed, phrase", [
    ("both", "both ends included"), ("left", "the lower end included, the upper end not"),
    ("right", "the upper end included, the lower end not"), ("none", "neither end included"),
])
def test_the_export_report_says_the_ends_of_a_between(closed, phrase):
    text = _methods({"column": "identity", "op": "between", "value": [90, 99], "closed": closed, "na": "remove"})
    assert f'between "90" and "99", {phrase}' in text


def test_an_old_between_step_without_closed_is_reported_as_both_ends_included():
    text = _methods({"column": "identity", "op": "between", "value": [90, 99]})
    assert "both ends included" in text


@pytest.mark.parametrize("closed, shown", [("both", "[1, 3]"), ("left", "[1, 3)"), ("right", "(1, 3]"), ("none", "(1, 3)")])
def test_the_audit_panel_writes_the_ends_as_brackets(closed, shown):
    from app.handlers.audit_stack import _condition_summary
    node = {"node_type": "filter_row", "params": {"column": "x", "op": "between", "value": [1, 3], "closed": closed}}
    assert _condition_summary(node) == f"x ∈ {shown}"
