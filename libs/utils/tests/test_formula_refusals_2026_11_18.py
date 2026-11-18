"""Formula refusals of 2026-11-18: `set_sorted`, `search_sorted` (D-0257), `pl.Unknown`, `pl.Binary` (D-0259).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_formula_refusals_2026_11_18.py -q
"""
import polars as pl
import pytest

from utils.fix_text import split_fix
from utils.formula_check import FormulaError, evaluate_formula, formula_problems

DATA = pl.DataFrame({"a": ['{"x": 1}'], "n": [3, 1, 2][:1]})


@pytest.mark.parametrize("text,word", [
    ("pl.col('n').set_sorted()", "set_sorted"),
    ("pl.col('n').set_sorted(descending=True)", "set_sorted"),
    ("pl.col('n').search_sorted(2)", "search_sorted"),
    ("pl.col('n').sort().search_sorted(pl.lit(2))", "search_sorted"),
])
def test_sorted_members_are_refused_with_a_plain_message(text, word):
    [message] = formula_problems(text)
    what, fix = split_fix(message)
    assert what.startswith(word + " ")
    assert "wrong" in what and "no message" in what
    assert fix.startswith("Suggestion:")
    with pytest.raises(FormulaError):
        evaluate_formula(text)


def test_set_sorted_suggests_a_sort_step():
    assert "sort step" in formula_problems("pl.col('n').set_sorted()")[0]


@pytest.mark.parametrize("text", ["pl.col('n').sort()", "pl.col('n').sort_by('n')", "pl.col('n').arg_sort()",
                                  "pl.col('n').top_k(2)"])
def test_sorting_that_checks_itself_is_still_allowed(text):
    assert formula_problems(text) == []


def _decode(t):
    return f"pl.col('a').str.json_decode({t})"


UNKNOWN = ["pl.Unknown", "pl.Unknown()", "pl.Array(pl.Unknown, 2)", "pl.List(pl.Unknown)", "pl.Struct({'x': pl.Unknown})"]
BINARY = ["pl.Binary", "pl.Binary()", "pl.List(pl.Binary)", "pl.Array(pl.Binary, 2)"]


def _check(text, word):
    problems = formula_problems(text)
    assert problems, f"allowed but must be refused: {text!r}"
    assert any(f"pl.{word}" in p for p in problems), problems
    assert any("Suggestion: use a type a table can hold" in p for p in problems)
    with pytest.raises(FormulaError):
        evaluate_formula(text)


@pytest.mark.parametrize("t", UNKNOWN)
def test_unknown_is_refused_in_every_spelling(t):
    _check(_decode(t), "Unknown")


@pytest.mark.parametrize("text", ["pl.col('n').cast(pl.Unknown)", "pl.lit(None, dtype=pl.Unknown)",
                                  "pl.col('n').cast(dtype=pl.Array(pl.Unknown, 2))"])
def test_unknown_is_refused_in_cast_and_lit(text):
    _check(text, "Unknown")


@pytest.mark.parametrize("t", BINARY)
def test_binary_is_refused_in_every_spelling(t):
    _check(_decode(t), "Binary")


@pytest.mark.parametrize("text", ["pl.col('n').cast(pl.Binary)", "pl.lit(None, dtype=pl.Binary)"])
def test_binary_is_refused_in_cast_and_lit(text):
    _check(text, "Binary")


@pytest.mark.parametrize("text", [
    "pl.col('a').str.json_decode(pl.Struct({'x': pl.Int64}))",
    "pl.col('n').cast(pl.String)",
    "pl.col('n').cast(pl.List(pl.Int64))",
    "pl.col('n').cast(pl.Array(pl.Float64, 3))",
])
def test_neighbouring_types_are_still_allowed(text):
    assert formula_problems(text) == []


def test_the_parked_list_holds_exactly_these_today():
    from utils.formula_check import REFUSED_DTYPES
    assert set(REFUSED_DTYPES) == {"Object", "Unknown", "Binary"}
