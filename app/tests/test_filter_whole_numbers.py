"""A column of whole numbers takes whole numbers only in the HOME filter (D-0376).

# @deps
# consumes: app/modules/t3_audit_engine.py (refuse_decimal_for_whole_numbers, dialog_value, _apply_filter_rows)
# @end_deps

For every integer type and every operator (both ends of between included) a decimal is refused with the plain line and
nothing is added; a decimal column is untouched; "12.0" is read as 12 (PROVISIONAL); an old row that holds a decimal for an
integer column gives the same plain error, never a silent result.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_whole_numbers.py -q
"""
import polars as pl
import pytest

from app.modules.t3_audit_engine import _apply_filter_rows, dialog_value, refuse_decimal_for_whole_numbers
from utils.filter_values import FilterValueError

INT_DTYPES = [pl.Int8, pl.Int16, pl.Int32, pl.Int64, pl.UInt8, pl.UInt16, pl.UInt32, pl.UInt64]
OPS = ["eq", "ne", "gt", "ge", "lt", "le"]


def lf_of(dtype):
    return pl.LazyFrame({"x": pl.Series([10, 12, 13, 15], dtype=dtype), "s": ["a", "b", "c", "d"]})


def line(dtype):
    return f"This column holds whole numbers ({dtype}); type a whole number."


@pytest.mark.parametrize("dtype", INT_DTYPES)
@pytest.mark.parametrize("op", OPS)
@pytest.mark.parametrize("value", [12.5, 0.1, float("nan"), float("inf")])
def test_the_form_refuses_a_decimal_for_every_integer_type_and_operator(dtype, op, value):
    with pytest.raises(FilterValueError) as exc:
        dialog_value(lf_of(dtype), "x", dtype, False, op, operand=value)
    assert str(exc.value) == line(dtype)


@pytest.mark.parametrize("dtype", INT_DTYPES)
@pytest.mark.parametrize("low, high", [(12.5, 14), (11, 14.5), (1.5, 2.5)])
def test_between_refuses_a_decimal_at_either_end(dtype, low, high):
    with pytest.raises(FilterValueError) as exc:
        dialog_value(lf_of(dtype), "x", dtype, False, "between", low=low, high=high)
    assert str(exc.value) == line(dtype)


@pytest.mark.parametrize("dtype", INT_DTYPES)
@pytest.mark.parametrize("op", OPS)
def test_a_whole_number_is_added_and_a_decimal_that_is_whole_is_read_as_the_integer(dtype, op):
    for typed in (12, 12.0):
        got = dialog_value(lf_of(dtype), "x", dtype, False, op, operand=typed)
        assert got == (op, 12, "both") and type(got[1]) is int


def test_between_with_whole_ends_and_a_negative_whole_number():
    assert dialog_value(lf_of(pl.Int64), "x", pl.Int64, False, "between", low=12, high=15) == ("between", [12, 15], "both")
    assert dialog_value(lf_of(pl.Int64), "x", pl.Int64, False, "gt", operand=-3) == ("gt", -3, "both")


def test_a_negative_decimal_is_refused():
    with pytest.raises(FilterValueError, match="whole number"):
        dialog_value(lf_of(pl.Int64), "x", pl.Int64, False, "gt", operand=-0.5)


def test_an_empty_box_adds_nothing_and_says_nothing_about_decimals():
    assert dialog_value(lf_of(pl.Int64), "x", pl.Int64, False, "gt", operand=None) is None


@pytest.mark.parametrize("dtype", [pl.Float64, pl.Float32])
@pytest.mark.parametrize("op", OPS)
def test_a_decimal_column_accepts_decimals_as_before(dtype, op):
    assert dialog_value(lf_of(dtype), "x", dtype, False, op, operand=12.5) == (op, 12.5, "both")
    assert dialog_value(lf_of(dtype), "x", dtype, False, "between", low=11.5, high=13.5) == ("between", [11.5, 13.5], "both")


def test_text_that_is_not_a_number_is_not_the_business_of_this_rule():
    refuse_decimal_for_whole_numbers("abc", pl.Int64)   # read_filter_value says what is wrong with it
    refuse_decimal_for_whole_numbers(None, pl.Int64)
    refuse_decimal_for_whole_numbers(True, pl.Int64)
    refuse_decimal_for_whole_numbers(12.5, pl.String)   # another type: not judged here
    refuse_decimal_for_whole_numbers("12.0", pl.Int64)
    refuse_decimal_for_whole_numbers([12, "13.0"], pl.Int64)
    with pytest.raises(FilterValueError):
        refuse_decimal_for_whole_numbers(["12", "12.5"], pl.Int64)


@pytest.mark.parametrize("row", [
    {"column": "x", "op": "gt", "value": "12.5"}, {"column": "x", "op": "eq", "value": 12.5},
    {"column": "x", "op": "between", "value": ["11.5", 14]}, {"column": "x", "op": "in", "value": [12, 12.5]},
])
def test_an_old_or_restored_row_with_a_decimal_gives_the_plain_error_not_rows(row):
    with pytest.raises(FilterValueError, match="This column holds whole numbers"):
        _apply_filter_rows(lf_of(pl.Int64), [row]).collect()


def test_an_old_row_with_whole_values_still_filters():
    out = _apply_filter_rows(lf_of(pl.Int64), [{"column": "x", "op": "ge", "value": "12.0"}]).collect()["s"].to_list()
    assert out == ["b", "c", "d"]
