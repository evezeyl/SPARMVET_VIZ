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
    (pl.Datetime, "datetime"), (pl.Datetime("us", "UTC"), "datetime"), (pl.Categorical, "category"), (pl.Enum(["a"]), "category"),
    (pl.Time, "time"), (pl.Duration, "duration"), (pl.Duration("ns"), "duration"), (pl.Binary, "other"), (None, "other"),
])
def test_kind_of(dtype, kind):
    assert kind_of(dtype) == kind


def test_type_words_are_plain():
    assert type_words(pl.Int64) == "whole numbers"
    assert type_words(pl.Float64) == "decimal numbers"
    assert type_words(pl.Boolean) == "true or false"
    assert type_words(pl.Date) == "dates"
    assert type_words(pl.String) == "text"
    assert type_words(pl.Datetime) == "dates and times"
    assert type_words(pl.Categorical) == "categories"


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
    assert "number" in str(exc.value) and "Suggestion:" in str(exc.value)


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


def test_read_datetime_column_gives_the_exact_text():
    """The text keeps every digit (nanoseconds too) and its offset; the column's own unit and zone read it in `filter_condition`."""
    assert read_filter_value("2020-01-31 10:30:00", pl.Datetime) == "2020-01-31 10:30:00"
    assert read_filter_value(" 2020-01-31T10:30:00.000000007 ", pl.Datetime) == "2020-01-31T10:30:00.000000007"
    assert read_filter_value("2020-01-31 10:30:00+02:00", pl.Datetime("us", "Europe/Paris")) == "2020-01-31 10:30:00+02:00"
    assert read_filter_value(datetime.datetime(2020, 1, 31, 10, 30), pl.Datetime) == "2020-01-31T10:30:00"
    for bad in ("31/01/2020", "", None, 5, datetime.date(2020, 1, 31), "2020-13-45 10:00:00", "2020-01-01 25:00:00", "2020-01-01 10:61:00", "2020-01-01 10:30:61"):
        with pytest.raises(FilterValueError):
            read_filter_value(bad, pl.Datetime)


def test_text_and_other_columns_are_not_changed():
    assert read_filter_value("90.5", pl.Utf8) == "90.5"
    assert read_filter_value("90", None) == "90"
    assert read_filter_value("x", pl.Categorical) == "x"


def test_a_category_column_takes_text_only():
    with pytest.raises(FilterValueError) as exc:
        read_filter_value(90, pl.Categorical)
    assert "a number" in exc.value.problem and "categories" in exc.value.problem


# -- the strict mode of the recipe action: no conversion

@pytest.mark.parametrize("dtype, value", [
    (pl.Int64, 90), (pl.Int64, 90.5), (pl.Int64, 90.0), (pl.Float64, 90), (pl.Float64, 90.5), (pl.UInt8, 3),
    (pl.String, "a"), (pl.String, ""), (pl.Boolean, True), (pl.Boolean, False),
    (pl.Date, datetime.date(2020, 1, 1)), (pl.Datetime, datetime.datetime(2020, 1, 1, 10)), (pl.Categorical, "x"), (None, 5),
])
def test_strict_accepts_a_value_of_the_type_of_the_column(dtype, value):
    check_filter_value(value, dtype)


@pytest.mark.parametrize("dtype, value, given", [
    (pl.Int64, "90", "text"), (pl.Float64, "90.5", "text"), (pl.Int64, True, "true or false"),
    (pl.Int64, None, "empty"), (pl.String, 90, "a number"), (pl.String, True, "true or false"),
    (pl.Boolean, "true", "text"), (pl.Boolean, 1, "a number"),
    (pl.Date, 5, "a number"), (pl.Date, "2020-01-01", "text"), (pl.Date, datetime.datetime(2020, 1, 1, 10), "a date"),
    (pl.Datetime, "01/01/2020", "text"), (pl.Datetime, 5, "a number"), (pl.Datetime, datetime.date(2020, 1, 1), "a date"),
    (pl.Categorical, 5, "a number"), (pl.Categorical, True, "true or false"),
])
def test_strict_refuses_a_value_of_another_type_in_plain_words(dtype, value, given):
    with pytest.raises(FilterValueError) as exc:
        check_filter_value(value, dtype)
    text = str(exc.value)
    assert given in exc.value.problem and type_words(dtype) in exc.value.problem
    assert "Suggestion:" in text and exc.value.fix
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


# -- what the strict mode and the condition refuse in plain words (reviewer 2026-11-15)

@pytest.mark.parametrize("column, op, value", [
    ("d", "eq", 5), ("d", "in", [5]), ("d", "eq", "2020-01-01"), ("d", "in", ["2020-01-01"]), ("d", "between", ["2020-01-01", "2020-01-03"]),
    ("k", "eq", 5), ("k", "in", ["x", 5]), ("dt", "eq", "01/01/2020"), ("dt", "in", ["01/01/2020"]),
    ("dt", "eq", datetime.date(2020, 1, 1)),
])
def test_strict_refuses_a_wrong_type_on_date_datetime_and_category_columns(column, op, value):
    frame = FRAME.with_columns(dt=pl.Series([datetime.datetime(2020, 1, 1, 10), datetime.datetime(2020, 1, 2, 10), None]))
    with pytest.raises(FilterValueError) as exc:
        filter_condition(column, op, value, frame.schema[column], strict=True)
    assert type_words(frame.schema[column]) in exc.value.problem and exc.value.fix
    assert "unable to find column" not in str(exc.value) and "Polars" not in str(exc.value)


@pytest.mark.parametrize("op, value", [("gt", True), ("ge", False), ("lt", True), ("le", False), ("between", [False, True])])
@pytest.mark.parametrize("strict", [False, True])
def test_greater_and_less_on_a_true_false_column_are_refused_not_zero_rows(op, value, strict):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("b", op, value, pl.Boolean, strict=strict)
    assert "true or false" in exc.value.problem and exc.value.fix


def test_a_list_of_whole_numbers_and_decimals_is_a_list_of_numbers_on_a_decimal_column():
    for strict in (False, True):
        assert rows("f", "in", [90, 90.5, 91], strict=strict) == ["b", "c"]
        assert rows("f", "not_in", [90, 90.5], strict=strict) == ["a", "c"]
        assert rows("f", "between", [89, 90.5], strict=strict) == ["a", "b"]
    assert rows("i", "in", [90, 90.5, 91]) == ["b", "c"]


def test_datetime_values_are_compared_as_datetimes():
    frame = pl.DataFrame({"s": ["a", "b", "c"], "dt": [datetime.datetime(2020, 1, 1, 10), datetime.datetime(2020, 1, 2, 10), None]})
    def got(op, value, **kw):
        return frame.filter(filter_condition("dt", op, value, frame.schema["dt"], **kw))["s"].to_list()
    assert got("in", ["2020-01-02 10:00:00"]) == ["b"]
    assert got("not_in", ["2020-01-02 10:00:00"]) == ["a"]
    assert got("eq", datetime.datetime(2020, 1, 1, 10), strict=True) == ["a"]
    assert got("in", [datetime.datetime(2020, 1, 1, 10)], strict=True) == ["a"]


def test_a_filter_on_a_category_with_numbers_is_refused_for_a_list_as_for_a_single_value():
    for strict in (False, True):
        for op, value in (("eq", 1), ("in", [1, 2]), ("not_in", [1]), ("in", ["x", 2])):
            with pytest.raises(FilterValueError) as exc:
                filter_condition("k", op, value, pl.Categorical, strict=strict)
            assert "categories" in exc.value.problem


@pytest.mark.parametrize("op, value", [("gt", True), ("ge", False), ("lt", True), ("le", False), ("between", [False, True])])
def test_the_true_false_message_names_the_value_the_type_and_the_fix(op, value):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("b", op, value, pl.Boolean)
    text = exc.value.problem
    shown = str(value[0] if isinstance(value, list) else value)
    assert shown in text and "true or false" in text and "Boolean" in text and "greater" in text.lower() and exc.value.fix


@pytest.mark.parametrize("dtype", [pl.Binary, pl.List(pl.Int64)])
@pytest.mark.parametrize("op, value", [("in", ["10:30:00"]), ("eq", "10:30:00")])
def test_other_types_are_refused_in_plain_words(dtype, op, value):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("t", op, value, dtype)
    assert "not offered" in exc.value.problem and str(dtype) in exc.value.problem and exc.value.fix


def test_an_unknown_type_keeps_the_text_comparison():
    frame = pl.DataFrame({"s": ["a", "b"], "t": ["x", "y"]})
    assert frame.filter(filter_condition("t", "in", ["x"], None))["s"].to_list() == ["a"]


def test_check_filter_judges_the_operator_and_the_values_with_one_rule():
    from utils.filter_values import check_filter
    check_filter("gt", 5, pl.Int64)
    check_filter("in", [1, 2.5], pl.Float64)
    check_filter("between", [datetime.date(2020, 1, 1), datetime.date(2020, 1, 2)], pl.Date)
    for op, value, dtype in (("gt", True, pl.Boolean), ("between", ["a", "b"], pl.String), ("in", [1], pl.Categorical),
                             ("eq", "x", pl.Time), ("eq", 5, pl.Date), ("in", ["90"], pl.Int64)):
        with pytest.raises(FilterValueError):
            check_filter(op, value, dtype)


# -- a time of day and a duration: typed from their text (FILTER-PICKERS-1)

T = datetime.time
TIMES = pl.DataFrame({
    "s": ["a", "b", "c", "d"], "t": pl.Series([T(9, 0), T(10, 30), T(10, 30, 0, 250000), None], dtype=pl.Time),
})
SECONDS = [60, 5400, 7200, None]   # one minute, 90 minutes, two hours, no value


def durations(unit):
    ns = pl.Series([None if x is None else x * 10**9 for x in SECONDS], dtype=pl.Int64).cast(pl.Duration("ns"))
    return pl.DataFrame({"s": ["a", "b", "c", "d"], "u": ns.dt.cast_time_unit(unit)})


DURATIONS = {unit: durations(unit) for unit in ("us", "ms", "ns")}


def rows_of(frame, column, op, value, **kw):
    return frame.filter(filter_condition(column, op, value, frame.schema[column], **kw))["s"].to_list()


@pytest.mark.parametrize("op, value, kept", [
    ("eq", "10:30:00", ["b"]), ("ne", "10:30:00", ["a", "c"]), ("gt", "10:30:00", ["c"]), ("ge", "10:30:00", ["b", "c"]),
    ("lt", "10:30", ["a"]), ("le", "10:30:00", ["a", "b"]), ("in", ["09:00:00", "10:30:00.25"], ["a", "c"]),
    ("not_in", ["09:00:00"], ["b", "c"]), ("between", ["09:00:00", "10:30:00"], ["a", "b"]),
])
def test_a_time_column_compares_times_typed_from_their_text(op, value, kept):
    assert rows_of(TIMES, "t", op, value) == kept


@pytest.mark.parametrize("closed, kept", [("both", ["a", "b"]), ("left", ["a"]), ("right", ["b"]), ("none", [])])
def test_a_time_between_has_its_four_ends(closed, kept):
    assert rows_of(TIMES, "t", "between", ["09:00:00", "10:30:00"], closed=closed) == kept


def test_a_time_keeps_its_nanoseconds_nothing_is_cut():
    f = pl.DataFrame({"s": ["a", "b"], "t": pl.Series([36000 * 10**9 + 7, 36000 * 10**9], dtype=pl.Int64).cast(pl.Time)})
    assert rows_of(f, "t", "eq", "10:00:00.000000007") == ["a"]
    assert rows_of(f, "t", "between", ["10:00:00.000000007", "10:00:00.000000007"]) == ["a"]


@pytest.mark.parametrize("value", ["25:00:00", "10:60", "10", "ten", "10:30:61", "10:30:00.1234567891", True, 5])
@pytest.mark.parametrize("strict", [False, True])
def test_a_time_that_is_not_a_time_is_a_plain_error(value, strict):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("t", "eq", value, pl.Time, strict=strict)
    assert "times of day" in exc.value.problem and "Time" in exc.value.problem and "Suggestion:" in str(exc.value)
    assert "Polars" not in str(exc.value) and "ComputeError" not in str(exc.value)


def test_a_time_object_is_read_and_written_as_text():
    assert read_filter_value(T(10, 30), pl.Time) == "10:30:00"
    assert read_filter_value(T(10, 30, 0, 250000), pl.Time) == "10:30:00.250000"
    assert read_filter_value(" 10:30 ", pl.Time) == "10:30"
    check_filter_value(T(10, 30), pl.Time)
    check_filter_value("10:30:00", pl.Time)


@pytest.mark.parametrize("unit", ["us", "ms", "ns"])
@pytest.mark.parametrize("op, value, kept", [
    ("eq", "90 min", ["b"]), ("ne", "90 min", ["a", "c"]), ("gt", "1.5 h", ["c"]), ("ge", "5400 s", ["b", "c"]), ("lt", "2 h", ["a", "b"]),
    ("le", "1 min", ["a"]), ("between", ["1 min", "90 min"], ["a", "b"]), ("between", ["0 s", "2 h"], ["a", "b", "c"]),
    ("in", ["1 min", "2 h"], ["a", "c"]), ("not_in", ["1 min"], ["b", "c"]),
])
def test_a_duration_column_compares_durations_typed_from_number_and_unit(unit, op, value, kept):
    assert rows_of(DURATIONS[unit], "u", op, value) == kept


def test_a_duration_written_as_a_timedelta_is_read_as_text():
    assert read_filter_value(datetime.timedelta(minutes=90), pl.Duration) == "5400000000 us"
    check_filter_value(datetime.timedelta(minutes=90), pl.Duration)


@pytest.mark.parametrize("value", ["", "90", "min", "ninety minutes", "1,5 h", "90 minutes", "1e3 s", None, True])
@pytest.mark.parametrize("strict", [False, True])
def test_a_duration_that_is_not_a_number_and_a_unit_is_a_plain_error(value, strict):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("u", "eq", value, pl.Duration("us"), strict=strict)
    assert "Suggestion:" in str(exc.value) and "Polars" not in str(exc.value)


def test_a_duration_finer_than_the_unit_of_the_column_is_refused_not_cut():
    with pytest.raises(FilterValueError) as exc:
        filter_condition("u", "eq", "1.0000005 s", pl.Duration("us"))
    assert "finer than the unit" in exc.value.problem and "us" in exc.value.problem


def test_a_negative_duration_is_a_duration():
    f = pl.DataFrame({"s": ["a", "b"], "u": pl.Series([-5 * 10**6, 5 * 10**6], dtype=pl.Int64).cast(pl.Duration("us"))})
    assert rows_of(f, "u", "lt", "0 s") == ["a"]
    assert rows_of(f, "u", "eq", "-5 s") == ["a"]


def test_greater_than_on_a_time_or_duration_is_not_refused_but_true_false_still_is():
    assert rows_of(TIMES, "t", "gt", "09:00:00") == ["b", "c"]
    with pytest.raises(FilterValueError):
        filter_condition("b", "gt", True, pl.Boolean)


def test_check_filter_judges_a_time_and_a_duration():
    from utils.filter_values import check_filter
    check_filter("between", ["09:00:00", "10:00:00"], pl.Time)
    check_filter("gt", "90 min", pl.Duration)
    for op, value, dtype in (("eq", 5, pl.Time), ("eq", "90", pl.Duration), ("in", ["25:00"], pl.Time)):
        with pytest.raises(FilterValueError):
            check_filter(op, value, dtype)


def test_a_date_between_and_comparisons_on_real_dates_and_on_their_year_month_day_text():
    D = datetime.date
    f = pl.DataFrame({"s": ["a", "b", "c"], "d": [D(2020, 1, 1), D(2020, 1, 2), D(2020, 1, 3)]})
    for value in ("2020-01-02", D(2020, 1, 2)):
        assert rows_of(f, "d", "gt", value) == ["c"]
        assert rows_of(f, "d", "le", value) == ["a", "b"]
    assert rows_of(f, "d", "between", ["2020-01-02", "2020-01-03"], closed="left") == ["b"]
    assert rows_of(f, "d", "between", [D(2020, 1, 1), D(2020, 1, 3)], closed="none") == ["b"]


def test_a_datetime_between_keeps_nanoseconds():
    t = pl.Series([datetime.datetime(2020, 1, 1, 10, 30)], dtype=pl.Datetime("us")).cast(pl.Datetime("ns"))
    t = pl.concat([t, t + pl.Series([7], dtype=pl.Int64).cast(pl.Duration("ns"))])
    f = pl.DataFrame({"s": ["a", "b"], "t": t})
    assert rows_of(f, "t", "between", ["2020-01-01 10:30:00.000000007", "2020-01-01 10:30:00.000000007"]) == ["b"]


# -- a wall-clock time that does not exist, or exists twice, in the time zone of the column (daylight-saving change)

PARIS = pl.Datetime("us", "Europe/Paris")
GAP = "2020-03-29 02:30:00"      # the clock jumps from 02:00 to 03:00: this time does not exist
TWICE = "2020-10-25 02:30:00"    # the clock goes back from 03:00 to 02:00: this time exists twice


def _paris_frame():
    naive = pl.Series([datetime.datetime(2020, 3, 29, 1, 0), datetime.datetime(2020, 3, 29, 4, 0), datetime.datetime(2020, 10, 24, 12, 0)], dtype=pl.Datetime("us"))
    return pl.DataFrame({"s": ["a", "b", "c"], "t": naive.dt.replace_time_zone("Europe/Paris")})


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("op, value", [("eq", GAP), ("gt", GAP), ("in", [GAP]), ("between", ["2020-03-29 01:00:00", GAP])])
def test_a_time_that_does_not_exist_in_the_zone_of_the_column_says_so(op, value, strict):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("t", op, value, PARIS, strict=strict)
    text = str(exc.value)
    assert "does not exist" in exc.value.problem and "Europe/Paris" in exc.value.problem and GAP in exc.value.problem
    assert "is text" not in text and "Suggestion: choose a time before or after the change" in text


@pytest.mark.parametrize("strict", [False, True])
@pytest.mark.parametrize("op, value", [("eq", TWICE), ("le", TWICE), ("not_in", [TWICE])])
def test_a_time_that_exists_twice_in_the_zone_of_the_column_says_so_and_what_the_dialog_can_do(op, value, strict):
    with pytest.raises(FilterValueError) as exc:
        filter_condition("t", op, value, PARIS, strict=strict)
    text = str(exc.value)
    assert "exists twice" in exc.value.problem and "Europe/Paris" in exc.value.problem and TWICE in exc.value.problem
    assert "is text" not in text and "Suggestion:" in text
    assert "boxes" in exc.value.problem and "list" in exc.value.fix and "before or after the change" in exc.value.fix


def test_the_times_around_the_change_and_a_time_with_its_offset_still_work():
    f = _paris_frame()
    assert f.filter(filter_condition("t", "ge", "2020-03-29 03:00:00", PARIS))["s"].to_list() == ["b", "c"]
    assert f.filter(filter_condition("t", "lt", "2020-03-29 01:59:59", PARIS))["s"].to_list() == ["a"]
    # an exact text with its offset says which of the two: it is read, not refused
    assert f.filter(filter_condition("t", "eq", "2020-03-29 03:00:00+02:00", PARIS))["s"].to_list() == []
    filter_condition("t", "eq", "2020-10-25 02:30:00+01:00", PARIS)
    filter_condition("t", "eq", "2020-10-25 02:30:00+02:00", PARIS)
