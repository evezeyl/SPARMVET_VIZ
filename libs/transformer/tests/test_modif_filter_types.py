"""`modif_filter` is strict about the type of its value (ADR-104 point 7, Eve 2026-11-14: "the engine stays strict").

A value that does not have the type of its column stops the step with a plain error: the step, the column, the value, what the
column holds and how to fix it. Never a raw Polars error, never a conversion.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_modif_filter_types.py -q
"""
import datetime

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

FRAME = pl.DataFrame({
    "id": ["a", "b", "c"], "year": [1998, 2000, 2003], "x": [1.5, 2.5, 3.5], "s": ["p", "q", "r"], "b": [True, False, True],
    "d": [datetime.date(2020, 1, 1), datetime.date(2020, 1, 2), datetime.date(2020, 1, 3)],
})


def run(column, op, value, **extra):
    spec = {"column": column, "op": op, "value": value, "na": "remove", **extra}
    return AVAILABLE_WRANGLING_ACTIONS["modif_filter"](FRAME.lazy(), spec).collect()["id"].to_list()


@pytest.mark.parametrize("column, op, value", [
    ("year", "gt", "1998"), ("year", "eq", "2000"), ("year", "in", ["1998", "2000"]), ("year", "not_in", [1998, "2000"]),
    ("year", "between", ["1998", 2003]), ("x", "ge", "1.5"), ("s", "eq", 1), ("s", "in", ["p", 2]), ("b", "eq", "true"),
    ("b", "in", ["True"]), ("year", "eq", True),
])
def test_a_value_of_another_type_gives_a_plain_error(column, op, value):
    with pytest.raises(TransformationError) as exc:
        run(column, op, value, **({"closed": "both"} if op == "between" else {}))
    text = str(exc.value)
    assert "modif_filter" in text and repr(column) in text
    assert "ComputeError" not in text and "InvalidOperation" not in text and "polars" not in text.lower()
    assert exc.value.tip
    assert "holds" in text  # what the column holds, in words


def test_the_plain_error_says_value_type_and_fix():
    with pytest.raises(TransformationError) as exc:
        run("year", "gt", "1998")
    text = str(exc.value)
    assert "'1998'" in text and "text" in text and "whole numbers" in text and "Int64" in text
    assert "number" in exc.value.tip and "quotes" in exc.value.tip


def test_nothing_is_converted_a_text_value_does_not_become_a_number():
    with pytest.raises(TransformationError):
        run("year", "ge", "2000")


@pytest.mark.parametrize("column, op, value, expected", [
    ("year", "gt", 1998, ["b", "c"]), ("year", "in", [1998, 2003], ["a", "c"]), ("year", "between", [1999, 2003], ["b", "c"]),
    ("year", "gt", 1998.5, ["b", "c"]), ("x", "ge", 2, ["b", "c"]), ("s", "in", ["p", "r"], ["a", "c"]),
    ("s", "gt", "p", ["b", "c"]), ("b", "eq", True, ["a", "c"]), ("b", "in", [False], ["b"]),
])
def test_a_value_of_the_type_of_the_column_works(column, op, value, expected):
    assert run(column, op, value) == expected


def test_between_on_a_text_column_is_refused_in_plain_words():
    with pytest.raises(TransformationError) as exc:
        run("s", "between", ["p", "q"])
    assert "between" in str(exc.value) and "numbers or dates" in str(exc.value)


def test_a_date_column_is_not_judged_here():
    """Date and Boolean comparisons are not decided (ADR-104 point 7): a date column keeps the behaviour of Polars."""
    assert run("d", "in", [datetime.date(2020, 1, 2)]) == ["b"]
    assert run("d", "ge", datetime.date(2020, 1, 2)) == ["b", "c"]
