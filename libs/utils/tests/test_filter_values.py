"""Shared coercion of a filter value to the dtype of its column (issue #62, HOME-EXPLORE-1)."""
import math

import polars as pl
import pytest

from utils.filter_values import coerce_filter_value


@pytest.mark.parametrize("value, expected", [
    ("90", 90), ("90.0", 90), (90, 90), (90.0, 90), ("-3", -3),
    ("90.5", 90.5), (90.5, 90.5), ("-0.5", -0.5), (" 7 ", 7),
])
def test_integer_column(value, expected):
    out = coerce_filter_value(value, pl.Int64)
    assert out == expected
    assert type(out) is type(expected)


def test_integer_column_keeps_a_large_integer_exact():
    big = "9007199254740993"  # 2**53 + 1, not representable as a float
    assert coerce_filter_value(big, pl.Int64) == 9007199254740993


@pytest.mark.parametrize("dtype", [pl.Float64, pl.Float32])
@pytest.mark.parametrize("value, expected", [("90", 90.0), ("90.5", 90.5), (3, 3.0)])
def test_float_column(dtype, value, expected):
    out = coerce_filter_value(value, dtype)
    assert out == expected and isinstance(out, float)


def test_unparseable_text_is_returned_unchanged():
    assert coerce_filter_value("abc", pl.Int64) == "abc"
    assert coerce_filter_value("", pl.Float64) == ""
    assert coerce_filter_value(None, pl.Int64) is None


def test_non_numeric_column_is_returned_unchanged():
    assert coerce_filter_value("90.5", pl.Utf8) == "90.5"
    assert coerce_filter_value("90", None) == "90"


def test_nan_and_infinity_are_floats():
    assert math.isnan(coerce_filter_value("nan", pl.Int64))
    assert coerce_filter_value("inf", pl.Int64) == math.inf


def test_unsigned_and_other_integer_widths():
    assert coerce_filter_value("5.5", pl.UInt8) == 5.5
    assert coerce_filter_value("5.0", pl.Int8) == 5
