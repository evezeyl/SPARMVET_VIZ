"""One reading of a filter value and one filter condition for the HOME table, the plot and the recipe action (ADR-104 point 7).

A value is read in the type of its column. Two modes: `read_filter_value` reads an old value written as text from the dtype
the step carries (and says so when it cannot); `check_filter_value` is the strict mode of the recipe action: no conversion,
a plain error. `filter_condition` builds the Polars condition for both.
"""
import datetime
import math

import polars as pl
import pytest

from utils.filter_values import (
    FilterValueError, check_filter_value, filter_condition, kind_of, read_filter_value, type_words,
)

FRAME = pl.DataFrame({
    "i": [89, 90, 91], "f": [89.0, 90.0, 91.0], "t": ["89", "90", "91"], "b": [True, False, True],
    "d": [datetime.date(2020, 1, 1), datetime.date(2020, 1, 2), datetime.date(2020, 1, 3)],
    "k": pl.Series(["x", "y", "x"], dtype=pl.Categorical), "s": ["a", "b", "c"],
})


def rows(column, op, value, dtype=None, **kw):
    dtype = FRAME.schema[column] if dtype is None else dtype
    return FRAME.filter(filter_condition(column, op, value, dtype, **kw))["s"].to_list()


# -- kinds and words

@pytest.mark.parametrize("dtype, kind", [
    (pl.Int64, "int"), (pl.UInt8, "int"), ("Int32", "int"), (pl.Float64, "float"), (pl.Float32, "float"), (pl.Decimal(10, 2), "float"),
    (pl.Boolean, "bool"), (pl.Date, "date"), (pl.String, "text"), (pl.Utf8, "text"), ("String", "text"),
    (pl.Datetime, "other"), (pl.Categorical, "other"), (None, "other"),
])
def test_kind_of(dtype, kind):
    assert kind_of(dtype) == kind


def test_type_words_are_plain():
    assert type_words(pl.Int64) == "whole numbers"
    assert type_words(pl.Float64) == "decimal numbers"
    assert type_words(pl.Boolean) == "true or false"
    assert type_words(pl.Date) == "dates"
    assert type_words(pl.String) == "text"
    assert type_words(pl.Categorical) == "Categorical"


# -- reading an old value from the dtype the step carries (the lenient mode)

@pytest.mark.parametrize("value, expected", [
    ("90", 90), ("90.0", 90), (90, 90), (90.0, 90), ("-3", -3), ("90.5", 90.5), (90.5, 90.5), ("-0.5", -0.5), (" 7 ", 7),
])
def test_read_integer_column(value, expected):
    out = read_filter_value(value, pl.Int64)
    assert out == expected and type(out) is type(expected)


def test_read_integer_column_keeps_a_large_integer_exact():
    assert read_filter_value("9007199254740993", pl.Int64) == 9007199254740993  # 2**53 + 1, not a float


@pytest.mark.parametrize("dtype", [pl.Float64, pl.Float32])
@pytest.mark.parametrize("value, expected", [("90", 90.0), ("90.5", 90.5), (3, 3.0)])
def test_read_float_column(dtype, value, expected):
    out = read_filter_value(value, dtype)
    assert out == expected and isinstance(out, float)


def test_read_nan_and_infinity_are_floats():
    assert math.isnan(read_filter_value("nan", pl.Int64))
    assert read_filter_value("inf", pl.Int64) == math.inf


def test_read_other_integer_widths():
    assert read_filter_value("5.5", pl.UInt8) == 5.5
    assert read_filter_value("5.0", pl.Int8) == 5


@pytest.mark.parametrize("bad", ["abc", "", None, True, [1], "1,5"])
@pytest.mark.parametrize("dtype", [pl.Int64, pl.Float64])
def test_a_value_that_cannot_be_read_as_a_number_is_reported_never_guessed(bad, dtype):
    with pytest.raises(FilterValueError) as exc:
        read_filter_value(bad, dtype)
    assert "number" in str(exc.value) and "Fix:" in str(exc.value)


@pytest.mark.parametrize("value, expected", [("True", True), ("true", True), ("FALSE", False), (True, True), (False, False)])
def test_read_boolean_column(value, expected):
    assert read_filter_value(value, pl.Boolean) is expected


@pytest.mark.parametrize("bad", ["yes", "1", 1, None, ""])
def test_a_boolean_that_cannot_be_read_is_reported(bad):
    with pytest.raises(FilterValueError):
        read_filter_value(bad, pl.Boolean)


def test_read_date_column():
    assert read_filter_value("2020-01-31", pl.Date) == datetime.date(2020, 1, 31)
    assert read_filter_value(datetime.date(2020, 1, 31), pl.Date) == datetime.date(2020, 1, 31)
    for bad in ("31/01/2020", "2020-13-01", "", None, 5):
        with pytest.raises(FilterValueError):
            read_filter_value(bad, pl.Date)


def test_text_and_other_columns_are_not_changed():
    assert read_filter_value("90.5", pl.Utf8) == "90.5"
    assert read_filter_value("90", None) == "90"
    assert read_filter_value(90, pl.Categorical) == 90


# -- the strict mode of the recipe action: no conversion

@pytest.mark.parametrize("dtype, value", [
    (pl.Int64, 90), (pl.Int64, 90.5), (pl.Int64, 90.0), (pl.Float64, 90), (pl.Float64, 90.5), (pl.UInt8, 3),
    (pl.String, "a"), (pl.String, ""), (pl.Boolean, True), (pl.Boolean, False),
    (pl.Date, datetime.date(2020, 1, 1)), (pl.Categorical, "x"), (None, 5),
])
def test_strict_accepts_a_value_of_the_type_of_the_column(dtype, value):
    check_filter_value(value, dtype)


@pytest.mark.parametrize("dtype, value, given", [
    (pl.Int64, "90", "text"), (pl.Float64, "90.5", "text"), (pl.Int64, True, "true or false"),
    (pl.Int64, None, "empty"), (pl.String, 90, "a number"), (pl.String, True, "true or false"),
    (pl.Boolean, "true", "text"), (pl.Boolean, 1, "a number"),
])
def test_strict_refuses_a_value_of_another_type_in_plain_words(dtype, value, given):
    with pytest.raises(FilterValueError) as exc:
        check_filter_value(value, dtype)
    text = str(exc.value)
    assert given in exc.value.problem and type_words(dtype) in exc.value.problem
    assert "Fix:" in text and exc.value.fix
    assert "Polars" not in text and "ComputeError" not in text


# -- the condition: the same rows for the table, the plot and the action

@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("op, value, expected", [
    ("ge", 90, ["b", "c"]), ("gt", 90.5, ["c"]), ("lt", 90.5, ["a", "b"]), ("eq", 90, ["b"]), ("ne", 90, ["a", "c"]),
    ("in", [90.5, 91], ["c"]), ("not_in", [90.5, 91], ["a", "b"]), ("in", [90.0], ["b"]),
    ("between", [89.5, 90.5], ["b"]), ("eq", [89, 91], ["a", "c"]), ("ne", [89], ["b", "c"]),
])
def test_condition_on_number_columns(column, op, value, expected):
    assert rows(column, op, value) == expected


@pytest.mark.parametrize("op, value, expected", [
    ("ge", "90", ["b", "c"]), ("in", ["89", "91"], ["a", "c"]), ("not_in", ["90.5"], ["a", "b", "c"]), ("eq", "90.5", []),
])
def test_condition_reads_an_old_text_value_from_the_dtype(op, value, expected):
    assert rows("i", op, value) == rows("f", op, value) == expected


@pytest.mark.parametrize("closed, expected", [
    ("both", ["a", "b", "c"]), ("left", ["a", "b"]), ("right", ["b", "c"]), ("none", ["b"]),
])
def test_between_has_four_ends(closed, expected):
    assert rows("i", "between", [89, 91], closed=closed) == expected


def test_between_on_text_is_refused_in_plain_words():
    with pytest.raises(FilterValueError) as exc:
        filter_condition("s", "between", ["a", "b"], pl.String)
    assert "between" in exc.value.problem and "text" in exc.value.problem


def test_boolean_values_are_compared_as_booleans_not_as_text():
    assert rows("b", "in", [True]) == ["a", "c"]
    assert rows("b", "in", ["True"]) == ["a", "c"]  # an old row holds the text the panel showed
    assert rows("b", "not_in", [True]) == ["b"]
    assert rows("b", "eq", False) == ["b"]
    assert rows("b", "ne", True) == ["b"]


def test_date_values_are_compared_as_dates():
    assert rows("d", "in", [datetime.date(2020, 1, 2)]) == ["b"]
    assert rows("d", "in", ["2020-01-02"]) == ["b"]
    assert rows("d", "not_in", ["2020-01-02"]) == ["a", "c"]
    assert rows("d", "eq", ["2020-01-01", "2020-01-03"]) == ["a", "c"]
    assert rows("d", "between", [datetime.date(2020, 1, 1), datetime.date(2020, 1, 2)], closed="left") == ["a"]


def test_text_columns_compare_text():
    assert rows("t", "in", ["89", "91"]) == ["a", "c"]
    assert rows("t", "ge", "90") == ["b", "c"]
    assert rows("t", "ne", "90") == ["a", "c"]


def test_other_columns_compare_text_for_lists():
    assert rows("k", "in", ["x"]) == ["a", "c"]
    assert rows("k", "not_in", ["x"]) == ["b"]


def test_a_value_that_cannot_be_read_stops_the_condition():
    with pytest.raises(FilterValueError):
        filter_condition("i", "ge", "abc", pl.Int64)
    with pytest.raises(FilterValueError):
        filter_condition("i", "in", ["1", "x"], pl.Int64)


def test_strict_condition_refuses_text_on_a_number_column_and_does_not_convert():
    with pytest.raises(FilterValueError):
        filter_condition("i", "ge", "90", pl.Int64, strict=True)
    with pytest.raises(FilterValueError):
        filter_condition("i", "in", ["90"], pl.Int64, strict=True)
    with pytest.raises(FilterValueError):
        filter_condition("i", "between", ["89", 91], pl.Int64, strict=True)
    assert FRAME.filter(filter_condition("i", "ge", 90, pl.Int64, strict=True))["s"].to_list() == ["b", "c"]
