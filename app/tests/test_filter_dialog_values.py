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
    LIST_ON_DEMAND_FROM, column_bounds, compose_date, compose_datetime, list_note, compose_duration, compose_time, ops_for_column, pick_values, typed_operand, value_choices,
    value_widget_for,
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


def test_a_datetime_column_lists_the_value_the_table_compares_and_keeps_its_text():
    """The label is the date and time as Polars writes it (every digit of the unit); the stored value is that text (a session file holds no
    datetime object); the table and the export read it back from the dtype (reviewer 2026-11-15: a picked value used to keep 0 rows)."""
    lf = pl.LazyFrame({"t": [datetime.datetime(2020, 1, 2, 10, 30), datetime.datetime(2020, 1, 1, 9), None]})
    choices = value_choices(lf, "t")
    assert choices == {"2020-01-01 09:00:00.000000": "2020-01-01 09:00:00.000000", "2020-01-02 10:30:00.000000": "2020-01-02 10:30:00.000000"}


def test_nanoseconds_below_the_microsecond_are_in_the_label():
    t = (pl.Series([datetime.datetime(2020, 1, 1, 10, 30)], dtype=pl.Datetime("us")).cast(pl.Datetime("ns")) + pl.Series([7]).cast(pl.Duration("ns")))
    assert list(value_choices(pl.DataFrame({"t": t}).lazy(), "t")) == ["2020-01-01 10:30:00.000000007"]


def test_a_millisecond_column_lists_milliseconds():
    t = pl.Series([datetime.datetime(2020, 1, 1, 10, 30, 0, 123000)]).cast(pl.Datetime("ms"))
    assert list(value_choices(pl.DataFrame({"t": t}).lazy(), "t")) == ["2020-01-01 10:30:00.123"]


@pytest.mark.parametrize("dtype", [pl.Binary, pl.List(pl.Int64)])
def test_a_column_of_another_type_offers_nothing_and_says_so(dtype):
    from app.modules.t3_audit_engine import not_offered_line
    assert ops_for_column(dtype, False) == []
    assert "No filter is offered" in not_offered_line("t", dtype) and str(dtype) in not_offered_line("t", dtype)


def test_a_datetime_with_microseconds_and_a_time_zone_keeps_them():
    tz = pl.DataFrame({"t": [datetime.datetime(2020, 1, 1, 9, 0, 0, 250000)]}).with_columns(pl.col("t").dt.replace_time_zone("UTC")).lazy()
    (label,) = value_choices(tz, "t")
    assert "250000" in label and "+00:00" in label


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


@pytest.mark.parametrize("dtype", [pl.String, pl.Categorical])
def test_text_and_category_columns_offer_the_list_operators_and_no_greater_or_less(dtype):
    """Greater and less on text is not offered (Eve, 2026-11-15, D9)."""
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


@pytest.mark.parametrize("dtype", [pl.String, pl.Categorical])
def test_text_columns_use_the_list(dtype):
    assert {value_widget_for(dtype, False, op) for op in ("in", "not_in", "eq", "ne")} == {"list"}


# -- the control that fits the type (FILTER-PICKERS-1, Eve 2026-11-15, D9)

ALL = ["in", "not_in", "eq", "ne", "gt", "ge", "lt", "le", "between"]
COMPARE = ["eq", "ne", "gt", "ge", "lt", "le", "between"]


@pytest.mark.parametrize("dtype", [pl.Date, pl.Datetime, pl.Datetime("ns", "UTC")])
def test_a_date_and_a_date_time_column_offer_the_list_and_every_comparison(dtype):
    assert ops_for_column(dtype, False) == ops_for_column(dtype, True) == ALL


@pytest.mark.parametrize("dtype", [pl.Time, pl.Duration, pl.Duration("ns")])
def test_a_time_and_a_duration_column_offer_the_comparisons_and_no_list(dtype):
    assert ops_for_column(dtype, False) == COMPARE


def test_a_true_false_column_offers_equal_and_not_equal_only():
    """In and none-of on one choice of two mean the same as equal and not equal; greater, less and between mean nothing."""
    assert ops_for_column(pl.Boolean, False) == ops_for_column(pl.Boolean, True) == ["eq", "ne"]


@pytest.mark.parametrize("dtype, op, widget", [
    (pl.Boolean, "eq", "bool"), (pl.Boolean, "ne", "bool"),
    (pl.Date, "in", "list"), (pl.Date, "not_in", "list"), (pl.Date, "eq", "date"), (pl.Date, "gt", "date"), (pl.Date, "between", "date_range"),
    (pl.Datetime, "in", "list"), (pl.Datetime, "ne", "datetime"), (pl.Datetime, "le", "datetime"), (pl.Datetime, "between", "datetime_range"),
    (pl.Time, "eq", "time"), (pl.Time, "ge", "time"), (pl.Time, "between", "time_range"),
    (pl.Duration, "eq", "duration"), (pl.Duration, "lt", "duration"), (pl.Duration, "between", "duration_range"),
])
def test_the_widget_follows_the_type_and_the_operator(dtype, op, widget):
    assert value_widget_for(dtype, False, op) == widget


# -- a number from the number box has the type of the column

@pytest.mark.parametrize("raw, dtype, expected", [(1998, pl.Int64, 1998), (1998.0, pl.Int64, 1998), (90.5, pl.Float64, 90.5), (90, pl.Float64, 90.0), ("12.0", pl.Int64, 12)])
def test_a_number_of_the_box_is_typed_from_the_schema(raw, dtype, expected):
    got = typed_operand(raw, dtype)
    assert got == expected and type(got) is type(expected)


def test_a_decimal_entered_for_an_integer_column_is_refused_at_entry_D0376():
    with pytest.raises(FilterValueError, match="whole number"):
        typed_operand(90.5, pl.Int64)


def test_a_STORED_decimal_value_for_an_integer_column_is_still_read_as_a_number():
    # the reader of stored values is unchanged by D-0376 (what a stored decimal should do is not decided)
    from utils.filter_values import read_filter_value
    got = read_filter_value(90.5, pl.Int64)
    assert got == 90.5 and type(got) is float


def test_an_empty_number_box_is_reported():
    with pytest.raises(FilterValueError):
        typed_operand(None, pl.Int64)


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


# -- the value the dialog stores (what "+ Add" writes into the row) -------------------------------------------------

from app.modules.t3_audit_engine import dialog_value  # noqa: E402


def _lf():
    return pl.LazyFrame({
        "year": [1998, 2000, 2003], "x": [1.5, 2.5, 3.5], "t": ["a", "b", "c"], "b": [True, False, True],
        "d": [D(2020, 1, 1), D(2020, 1, 2), None],
    })


def stored(column, op, discrete_axis=False, **widgets):
    lf = _lf()
    return dialog_value(lf, column, column_types(lf)[column], discrete_axis, op, **widgets)


def test_a_list_picked_on_a_year_stores_real_numbers_not_text():
    op, value, closed = stored("year", "in", True, picked=["1998", "2003"])
    assert (op, value) == ("in", [1998, 2003]) and all(type(v) is int for v in value)


def test_eq_and_ne_on_a_list_become_in_and_not_in():
    assert stored("year", "eq", True, picked=["2000"])[:2] == ("in", [2000])
    assert stored("t", "ne", False, picked=["a"])[:2] == ("not_in", ["a"])


def test_a_comparison_on_a_discrete_year_stores_the_number_of_the_box():
    op, value, _ = stored("year", "gt", True, operand=1999)
    assert (op, value) == ("gt", 1999) and type(value) is int


def test_a_number_box_value_has_the_type_of_the_column():
    assert type(stored("x", "ge", False, operand=2)[1]) is float
    assert type(stored("year", "ge", False, operand=2000.0)[1]) is int


def test_a_date_list_stores_the_year_month_day_text():
    assert stored("d", "in", False, picked=["2020-01-02"])[:2] == ("in", ["2020-01-02"])


def test_between_stores_typed_bounds_swapped_when_low_is_above_high_and_the_ends():
    assert stored("year", "between", False, low=2003, high=1998, closed="left") == ("between", [1998, 2003], "left")
    assert stored("x", "between", False, low=1, high=3)[1] == [1.0, 3.0]


def test_an_unknown_end_is_both():
    assert stored("year", "between", False, low=1, high=2, closed="weird")[2] == "both"


def test_nothing_chosen_stores_nothing():
    assert stored("t", "in", False, picked=[]) is None
    assert stored("year", "gt", False, operand=None) is None
    assert stored("year", "between", False, low=None, high=2) is None


def test_a_pick_that_is_not_in_the_column_is_reported():
    with pytest.raises(FilterValueError):
        stored("year", "in", True, picked=["1234"])


def test_without_a_table_the_text_is_kept_as_written():
    assert dialog_value(None, "c", None, False, "eq", text="  abc ") == ("eq", "abc", "both")
    assert dialog_value(None, "c", None, False, "eq", text="  ") is None


def test_adding_a_row_on_a_column_of_another_type_is_refused_in_plain_words():
    lf = pl.LazyFrame({"t": [b"x"]})
    with pytest.raises(FilterValueError) as exc:
        dialog_value(lf, "t", column_types(lf)["t"], False, "in", picked=["x"])
    assert "No filter is offered" in str(exc.value) and "Suggestion:" in str(exc.value)



# -- the value a picker stores (FILTER-PICKERS-1)

T = datetime.time


def _typed_lf():
    return pl.LazyFrame({
        "b": [True, False, None], "d": [D(2020, 1, 1), D(2020, 1, 2), D(2020, 1, 3)],
        "dt": pl.Series([datetime.datetime(2020, 1, 1, 9), datetime.datetime(2020, 1, 2, 10, 30), None], dtype=pl.Datetime("us")),
        "t": pl.Series([T(9, 0), T(10, 30), None], dtype=pl.Time),
        "u": pl.Series([60, 5400, None], dtype=pl.Int64).cast(pl.Duration("us")) * 10**6,
    })


def stored2(column, op, **widgets):
    lf = _typed_lf()
    return dialog_value(lf, column, column_types(lf)[column], False, op, **widgets)


@pytest.mark.parametrize("raw, expected", [("true", True), ("false", False), (True, True), (False, False)])
@pytest.mark.parametrize("op", ["eq", "ne"])
def test_the_true_false_control_stores_a_real_boolean_even_false(op, raw, expected):
    got = stored2("b", op, operand=raw)
    assert got == (op, expected, "both") and type(got[1]) is bool


def test_a_date_picker_stores_the_year_month_day_text_for_each_comparison():
    for op in ("eq", "ne", "gt", "ge", "lt", "le"):
        assert stored2("d", op, operand=D(2020, 1, 2)) == (op, "2020-01-02", "both")


def test_two_date_pickers_store_the_dates_in_order_and_the_ends():
    assert stored2("d", "between", low=D(2020, 1, 3), high=D(2020, 1, 1), closed="none") == ("between", ["2020-01-01", "2020-01-03"], "none")


def test_a_date_list_still_stores_the_text_of_the_dates_picked():
    assert stored2("d", "not_in", picked=["2020-01-02"]) == ("not_in", ["2020-01-02"], "both")


@pytest.mark.parametrize("cleared", [None, ""])
def test_a_cleared_date_box_is_no_date_chosen_never_a_date_filled_in(cleared):
    """Eve 2026-11-15: a filter that lacks its value is refused, never filled in. The value the handler gets from an empty box is None
    (or an empty text): the row cannot be added, the message says what happened and what to do."""
    for call in (lambda: compose_date(cleared), lambda: stored2("d", "gt", operand=cleared),
                 lambda: stored2("d", "between", low=cleared, high=D(2020, 1, 3)), lambda: stored2("d", "between", low=D(2020, 1, 1), high=cleared),
                 lambda: compose_datetime(cleared, 10, 30, 0)):
        with pytest.raises(FilterValueError) as exc:
            call()
        assert "No date is chosen" in exc.value.problem and "no filter is added" in exc.value.problem
        assert str(exc.value).endswith("Suggestion: choose a date")


def test_a_chosen_date_passes_compose_date():
    assert compose_date(D(2020, 1, 2)) == D(2020, 1, 2)


def test_a_time_stores_the_text_of_the_three_boxes_exact():
    assert stored2("t", "gt", operand=compose_time(10, 30, 0)) == ("gt", "10:30:00", "both")
    assert stored2("t", "eq", operand=compose_time(0, 0, 0.5)) == ("eq", "00:00:00.5", "both")
    assert stored2("t", "eq", operand=compose_time(23, 59, 59.123456789)) == ("eq", "23:59:59.123456789", "both")


def test_two_time_boxes_are_put_in_order():
    assert stored2("t", "between", low=compose_time(11, 0, 0), high=compose_time(9, 0, 0)) == ("between", ["09:00:00", "11:00:00"], "both")


@pytest.mark.parametrize("parts", [(None, 0, 0), (1, None, 0), (1, 0, None), (1.5, 0, 0), (25, 0, 0), (1, 60, 0), (1, 0, 60), (1, 0, -1)])
def test_a_time_that_is_empty_or_not_a_time_is_a_plain_error_not_a_filter(parts):
    with pytest.raises(FilterValueError) as exc:
        stored2("t", "eq", operand=compose_time(*parts))
    assert "Suggestion:" in str(exc.value)


def test_a_date_time_is_the_date_and_the_three_boxes():
    assert compose_datetime(D(2020, 1, 2), 10, 30, 0) == "2020-01-02 10:30:00"
    assert stored2("dt", "ge", operand=compose_datetime(D(2020, 1, 2), 10, 30, 0)) == ("ge", "2020-01-02 10:30:00", "both")
    got = stored2("dt", "between", low=compose_datetime(D(2020, 1, 3), 0, 0, 0), high=compose_datetime(D(2020, 1, 1), 0, 0, 0))
    assert got == ("between", ["2020-01-01 00:00:00", "2020-01-03 00:00:00"], "both")


def test_a_date_time_with_no_date_is_a_plain_error():
    with pytest.raises(FilterValueError) as exc:
        compose_datetime(None, 10, 30, 0)
    assert "No date is chosen" in exc.value.problem and "Suggestion:" in str(exc.value)


def test_a_date_time_list_still_stores_the_exact_text():
    lf = _typed_lf()
    label = next(iter(value_choices(lf, "dt")))
    op, value, _ = dialog_value(lf, "dt", column_types(lf)["dt"], False, "in", picked=[label])
    assert (op, value) == ("in", [label])


def test_a_duration_is_a_number_and_a_unit():
    assert compose_duration(90, "min") == "90 min"
    assert compose_duration(90.0, "min") == "90 min"
    assert compose_duration(1.5, "h") == "1.5 h"
    assert stored2("u", "gt", operand=compose_duration(1.5, "h")) == ("gt", "1.5 h", "both")


def test_two_durations_are_put_in_order_whatever_their_units():
    got = stored2("u", "between", low=compose_duration(2, "h"), high=compose_duration(30, "min"))
    assert got == ("between", ["30 min", "2 h"], "both")


@pytest.mark.parametrize("number, unit", [(None, "min"), (5, None), (5, "years"), (5, "")])
def test_a_duration_with_no_number_or_no_known_unit_is_a_plain_error(number, unit):
    with pytest.raises(FilterValueError) as exc:
        stored2("u", "eq", operand=compose_duration(number, unit))
    assert "Suggestion:" in str(exc.value)


def test_the_dialog_values_of_the_new_types_have_the_type_of_the_column_in_the_stored_row():
    """The row the dialog stages passes the check the app makes on an audit step (a value of False or 0 is a value)."""
    from app.modules.renamed_keys import audit_step_defect
    for column, op, widgets in (("b", "eq", {"operand": "false"}), ("d", "gt", {"operand": D(2020, 1, 1)}),
                                ("t", "lt", {"operand": compose_time(0, 0, 0)}), ("u", "ge", {"operand": compose_duration(0, "s")})):
        o, v, _ = stored2(column, op, **widgets)
        step = {"node_type": "filter_row", "params": {"column": column, "op": o, "value": v, "na": "remove"}}
        assert audit_step_defect(step) is None, (column, v)


# -- the defaults of the boxes come from the whole column, exact

def test_the_bounds_of_the_column_fill_the_boxes_exact():
    lf = pl.LazyFrame({
        "d": [D(2020, 1, 3), D(2020, 1, 1)],
        "dt": pl.Series([datetime.datetime(2020, 1, 2, 10, 30, 0, 250000), datetime.datetime(2020, 1, 1, 9)], dtype=pl.Datetime("us")).dt.replace_time_zone("Europe/Paris"),
        "t": pl.Series([36000 * 10**9 + 123456789, 3600 * 10**9], dtype=pl.Int64).cast(pl.Time),
        "u": pl.Series([5400, 7200], dtype=pl.Int64).cast(pl.Duration("us")) * 10**6,
    })
    types = column_types(lf)
    lo, hi = column_bounds(lf, "d", types["d"])
    assert (lo, hi) == ({"date": D(2020, 1, 1)}, {"date": D(2020, 1, 3)})
    lo, hi = column_bounds(lf, "dt", types["dt"])
    assert lo == {"date": D(2020, 1, 1), "h": 9, "min": 0, "s": 0} and hi == {"date": D(2020, 1, 2), "h": 10, "min": 30, "s": 0.25}
    lo, hi = column_bounds(lf, "t", types["t"])
    assert lo == {"h": 1, "min": 0, "s": 0} and hi == {"h": 10, "min": 0, "s": 0.123456789}
    lo, hi = column_bounds(lf, "u", types["u"])
    assert lo == {"number": 90, "unit": "min"} and hi == {"number": 2, "unit": "h"}


def test_the_bounds_of_a_column_with_no_value_are_none():
    assert column_bounds(pl.LazyFrame({"d": [None, None]}, schema={"d": pl.Date}), "d", pl.Date) is None


def test_the_default_boxes_reproduce_the_extremes_so_a_between_on_them_keeps_every_row():
    """A default that cut a digit would drop the largest row from `between lowest and highest` (silent)."""
    from app.modules.t3_audit_engine import _apply_filter_rows
    t = pl.Series([36000 * 10**9 + 123456789, 3600 * 10**9 + 7], dtype=pl.Int64).cast(pl.Time)
    lf = pl.LazyFrame({"s": ["a", "b"], "t": t})
    lo, hi = column_bounds(lf, "t", column_types(lf)["t"])
    got = dialog_value(lf, "t", pl.Time, False, "between", low=compose_time(lo["h"], lo["min"], lo["s"]), high=compose_time(hi["h"], hi["min"], hi["s"]))
    row = {"column": "t", "op": got[0], "value": got[1], "dtype": "Time", "na": "remove", "closed": got[2]}
    assert _apply_filter_rows(lf, [row]).collect()["s"].to_list() == ["a", "b"]


# -- the value list served on demand (PROVISIONAL, L10)

def test_a_short_list_is_shown_whole_with_no_note():
    assert list_note(0) == list_note(1) == list_note(LIST_ON_DEMAND_FROM) == ""


@pytest.mark.parametrize("count", [LIST_ON_DEMAND_FROM + 1, 30_000, 100_000])
def test_a_long_list_says_how_many_values_exist_and_that_a_search_shows_at_most_a_thousand(count):
    text = list_note(count)
    assert f"{count:,}" in text and "1,000" in text and "type more letters" in text


def test_the_pick_of_the_last_of_100000_values_is_the_real_value():
    lf = pl.LazyFrame({"name": [f"name_{i:06d}" for i in range(100_000)]})
    assert dialog_value(lf, "name", pl.String, False, "in", picked=["name_099999"])[:2] == ("in", ["name_099999"])


# -- a time that does not exist (or exists twice) in the zone of the column is refused when the row is added

@pytest.mark.parametrize("parts, what", [((D(2020, 3, 29), 2, 30, 0), "does not exist"), ((D(2020, 10, 25), 2, 30, 0), "exists twice")])
@pytest.mark.parametrize("op", ["eq", "gt", "le"])
def test_a_daylight_saving_time_is_refused_at_add_with_a_message_that_says_what_happened(op, parts, what):
    t = pl.Series([datetime.datetime(2020, 1, 1, 9)], dtype=pl.Datetime("us")).dt.replace_time_zone("Europe/Paris")
    lf = pl.LazyFrame({"t": t})
    with pytest.raises(FilterValueError) as exc:
        dialog_value(lf, "t", column_types(lf)["t"], False, op, operand=compose_datetime(*parts))
    assert what in exc.value.problem and "Europe/Paris" in exc.value.problem and "is text" not in str(exc.value)
    assert "Suggestion: choose a time before or after the change" in str(exc.value)


def test_a_between_with_a_time_that_does_not_exist_is_refused_at_add():
    t = pl.Series([datetime.datetime(2020, 1, 1, 9)], dtype=pl.Datetime("us")).dt.replace_time_zone("Europe/Paris")
    lf = pl.LazyFrame({"t": t})
    with pytest.raises(FilterValueError) as exc:
        dialog_value(lf, "t", column_types(lf)["t"], False, "between", low=compose_datetime(D(2020, 3, 28), 0, 0, 0), high=compose_datetime(D(2020, 3, 29), 2, 30, 0))
    assert "does not exist" in exc.value.problem


def test_the_hours_around_the_change_are_accepted_at_add():
    t = pl.Series([datetime.datetime(2020, 1, 1, 9)], dtype=pl.Datetime("us")).dt.replace_time_zone("Europe/Paris")
    lf = pl.LazyFrame({"t": t})
    for parts in ((D(2020, 3, 29), 1, 59, 59), (D(2020, 3, 29), 3, 0, 0), (D(2020, 10, 25), 1, 59, 59), (D(2020, 10, 25), 3, 0, 0)):
        assert dialog_value(lf, "t", column_types(lf)["t"], False, "gt", operand=compose_datetime(*parts)) is not None


# -- the date staged is exactly a date the user typed in full or picked (Eve 2026-11-15: never filled in, never changed without a word)

SUGGEST = "Suggestion: write the date as year-month-day, for example 2023-02-28, or pick it in the calendar"


@pytest.mark.parametrize("typed, parsed", [
    ("2023-0", D(2026, 11, 16)), ("abc", D(2026, 11, 16)), ("20220305", D(2026, 11, 16)),            # the widget fills in today
    ("2023-02-30", D(2023, 3, 2)),                                                                      # the widget rolls over
    ("03/05/2022", D(2008, 11, 11)), ("2023-0", None), ("99999-01-01", D(2026, 11, 16)),              # another order, partial, too long
])
def test_a_text_that_is_not_a_whole_date_is_refused_whatever_the_widget_read(typed, parsed):
    with pytest.raises(FilterValueError) as exc:
        compose_date(parsed, typed)
    assert "no filter is added" in exc.value.problem and str(exc.value).endswith(SUGGEST)
    assert typed in exc.value.problem


def test_an_impossible_date_says_that_it_does_not_exist():
    with pytest.raises(FilterValueError) as exc:
        compose_date(D(2023, 3, 2), "2023-02-30")
    assert "does not exist" in exc.value.problem


@pytest.mark.parametrize("typed, parsed, expected", [
    ("2022-03-05", D(2022, 3, 5), D(2022, 3, 5)), (" 2022-03-05 ", D(2022, 3, 5), D(2022, 3, 5)),
    ("2022-3-5", D(2022, 3, 5), D(2022, 3, 5)),                    # unambiguous: accepted, the staged line shows 2022-03-05
])
def test_a_date_typed_in_full_is_the_date_staged(typed, parsed, expected):
    assert compose_date(parsed, typed) == expected


def test_a_typed_date_that_the_widget_read_as_another_date_is_refused():
    with pytest.raises(FilterValueError) as exc:
        compose_date(D(2022, 3, 6), "2022-03-05")
    assert "no filter is added" in exc.value.problem and str(exc.value).endswith(SUGGEST)


def test_an_empty_typed_text_is_no_date_chosen():
    with pytest.raises(FilterValueError) as exc:
        compose_date(D(2026, 11, 16), "  ")
    assert str(exc.value).endswith("Suggestion: choose a date")


def test_without_the_typed_text_the_picked_date_is_used():
    """A date picked in the calendar or the default of the box: the widget wrote the text itself, there is nothing to compare."""
    assert compose_date(D(2022, 3, 5)) == D(2022, 3, 5)


def test_the_date_of_a_date_and_time_is_checked_the_same_way():
    with pytest.raises(FilterValueError) as exc:
        compose_datetime(D(2026, 11, 16), 10, 30, 0, typed="abc")
    assert str(exc.value).endswith(SUGGEST)
    assert compose_datetime(D(2022, 3, 5), 10, 30, 0, typed="2022-03-05") == "2022-03-05 10:30:00"
