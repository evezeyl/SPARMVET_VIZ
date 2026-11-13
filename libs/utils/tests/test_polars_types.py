"""The dtypes a text file can hold are read from the installed Polars; this pins the result so an upgrade shows (R9).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_polars_types.py -q
"""
import io

import polars as pl
import pytest

from utils.polars_types import PARAMETER_KEYS, dtype_with_parameters, text_dtype_names

# If Polars changes this list, read the change before updating it: a dtype that appears needs a decision (DEC27).
PINNED = (
    "Boolean", "Categorical", "Date", "Datetime", "Decimal", "Enum", "Float16", "Float32", "Float64",
    "Int128", "Int16", "Int32", "Int64", "Int8", "String", "Time", "UInt128", "UInt16", "UInt32", "UInt64", "UInt8",
)


def test_the_readable_dtypes_are_the_pinned_list_for_this_polars():
    assert text_dtype_names() == PINNED


def test_a_dtype_that_text_cannot_hold_is_not_listed():
    assert not {"Binary", "Duration", "List", "Struct", "Object", "Null", "Array", "Unknown"} & set(text_dtype_names())


def test_the_alias_utf8_is_not_a_name():
    assert "Utf8" not in text_dtype_names()


@pytest.mark.parametrize("name, field, text, expected", [
    ("Int64", {}, "2022", 2022),
    ("Boolean", {}, "true", True),
    ("Enum", {"categories": ["low", "high"]}, "low", "low"),
])
def test_a_declared_dtype_goes_to_the_reader(name, field, text, expected):
    dtype = dtype_with_parameters(name, field)
    frame = pl.read_csv(io.BytesIO(f"a\n{text}\n".encode()), schema_overrides={"a": dtype})
    assert frame["a"].to_list() == [expected]


def test_2022_dot_0_does_not_read_as_int64():
    with pytest.raises(Exception, match="2022.0"):
        pl.read_csv(io.BytesIO(b"a\n2022.0\n"), schema_overrides={"a": dtype_with_parameters("Int64", {})})


def test_each_parameter_key_belongs_to_a_listed_dtype():
    assert all(set(users) <= set(text_dtype_names()) for users in PARAMETER_KEYS.values())
