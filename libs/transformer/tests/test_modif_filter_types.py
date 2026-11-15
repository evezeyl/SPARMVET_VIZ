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
    "dt": [datetime.datetime(2020, 1, 1, 9), datetime.datetime(2020, 1, 2, 10, 30), datetime.datetime(2020, 1, 3)],
    "k": pl.Series(["u", "v", "u"], dtype=pl.Categorical),
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


@pytest.mark.parametrize("column, op, value, holds", [
    ("d", "eq", 5, "dates"), ("d", "in", [5], "dates"), ("d", "eq", "2020-01-01", "dates"), ("d", "in", ["2020-01-01"], "dates"),
    ("d", "between", ["2020-01-01", "2020-01-03"], "dates"),
    ("dt", "eq", "2020-01-01 09:00:00", "dates and times"), ("dt", "in", ["2020-01-01 09:00:00"], "dates and times"),
    ("dt", "eq", datetime.date(2020, 1, 1), "dates and times"),
    ("k", "eq", 5, "categories"), ("k", "in", ["u", 5], "categories"),
    ("b", "gt", True, "true or false"), ("b", "between", [False, True], "true or false"),
])
def test_a_wrong_type_on_a_date_a_datetime_a_category_or_a_true_false_column_gives_a_plain_error(column, op, value, holds):
    """Before: 0 rows with no message (Date eq 5, Boolean gt True) or a raw Polars error ("unable to find column")."""
    with pytest.raises(TransformationError) as exc:
        run(column, op, value, **({"closed": "both"} if op == "between" else {}))
    text = str(exc.value)
    assert "modif_filter" in text and repr(column) in text and holds in text
    assert "unable to find column" not in text and "ComputeError" not in text and "TypeError" not in text
    assert exc.value.tip


def test_dates_and_datetimes_written_as_dates_work():
    assert run("d", "in", [datetime.date(2020, 1, 2)]) == ["b"]
    assert run("d", "ge", datetime.date(2020, 1, 2)) == ["b", "c"]
    assert run("d", "between", [datetime.date(2020, 1, 1), datetime.date(2020, 1, 2)], closed="left") == ["a"]
    assert run("dt", "in", [datetime.datetime(2020, 1, 2, 10, 30)]) == ["b"]
    assert run("dt", "gt", datetime.datetime(2020, 1, 1, 9)) == ["b", "c"]
    assert run("k", "in", ["u"]) == ["a", "c"]
    assert run("k", "eq", "v") == ["b"]


def test_a_list_of_whole_numbers_and_decimals_is_a_valid_list_of_numbers():
    assert run("x", "in", [1.5, 2, 3.5]) == ["a", "c"]
    assert run("x", "not_in", [1.5, 2]) == ["b", "c"]
    assert run("year", "in", [1998, 2000.0, 2003.5]) == ["a", "b"]
