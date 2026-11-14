"""The behaviour of `modif_filter` (MODIF-FILTER-VERIFY-1, tests first; Eve 2026-11-13 and 2026-11-14).

`modif_filter` is the one vocabulary of the row filter (`column`, `op`, `value`, `na`). It is not a plain Polars
action, so the equality test of the `polars_` actions does not cover it; this file does:

  - every operator on numbers and on text, against the direct Polars expression;
  - `na`: `remove` drops the rows whose column is null, `keep` keeps them, for every operator (null is never a silent choice);
  - lists (`in`, `not_in`), `between` with every `closed`, an empty list, a NaN (a number, not a missing value);
  - what it refuses: a missing column, a wrong shape, an unknown operator, a missing `na`;
  - the rows and their order: a filter never reorders (ADR-090);
  (the comparison with the HOME filter panel is in app/tests/test_modif_filter_vs_home_filter.py: a library test does
  not import the app, Clear Lines.)

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_modif_filter.py -q
"""
import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

NAN = float("nan")
FRAME = pl.DataFrame({
    "id": ["a", "b", "c", "d", "e"],
    "n": [1, 2, 3, None, 5],
    "f": [1.5, NAN, 2.5, None, 4.5],
    "s": ["x", "y", "x", None, "z"],
})


def run(spec, frame=FRAME):
    return AVAILABLE_WRANGLING_ACTIONS["modif_filter"](frame.lazy(), dict(spec)).collect()


def ids(spec, frame=FRAME):
    return run(spec, frame)["id"].to_list()


# -- every operator against the direct Polars expression -------------------------------------------------

SCALAR = [("eq", pl.col("n") == 2), ("ne", pl.col("n") != 2), ("gt", pl.col("n") > 2),
          ("ge", pl.col("n") >= 2), ("lt", pl.col("n") < 3), ("le", pl.col("n") <= 3)]


@pytest.mark.parametrize("op,expr", SCALAR, ids=[o for o, _ in SCALAR])
def test_a_scalar_operator_on_numbers_equals_polars_when_na_is_remove(op, expr):
    value = {"eq": 2, "ne": 2, "gt": 2, "ge": 2, "lt": 3, "le": 3}[op]
    got = run({"column": "n", "op": op, "value": value, "na": "remove"})
    assert_frame_equal(got, FRAME.filter(expr))  # in Polars a comparison with null is null, so the row goes


def test_text_operators():
    assert ids({"column": "s", "op": "eq", "value": "x", "na": "remove"}) == ["a", "c"]
    assert ids({"column": "s", "op": "ne", "value": "x", "na": "remove"}) == ["b", "e"]
    assert ids({"column": "s", "op": "gt", "value": "x", "na": "remove"}) == ["b", "e"]


def test_in_and_not_in_with_a_list():
    assert ids({"column": "s", "op": "in", "value": ["x", "z"], "na": "remove"}) == ["a", "c", "e"]
    assert ids({"column": "s", "op": "not_in", "value": ["x", "z"], "na": "remove"}) == ["b"]


def test_an_empty_list_keeps_nothing_for_in_and_everything_not_null_for_not_in():
    assert ids({"column": "s", "op": "in", "value": [], "na": "remove"}) == []
    assert ids({"column": "s", "op": "not_in", "value": [], "na": "remove"}) == ["a", "b", "c", "e"]


@pytest.mark.parametrize("closed,expected", [("both", ["b", "c"]), ("left", ["b"]), ("right", ["c"]), ("none", [])])
def test_between_and_every_closed(closed, expected):
    assert ids({"column": "n", "op": "between", "value": [2, 3], "closed": closed, "na": "remove"}) == expected


def test_between_closes_both_ends_when_closed_is_not_written():
    assert ids({"column": "n", "op": "between", "value": [2, 3], "na": "remove"}) == ["b", "c"]


# -- na: the choice for a missing value is always written -------------------------------------------------

@pytest.mark.parametrize("spec", [
    {"column": "n", "op": "eq", "value": 2},
    {"column": "n", "op": "ne", "value": 2},
    {"column": "n", "op": "gt", "value": 2},
    {"column": "n", "op": "lt", "value": 3},
    {"column": "n", "op": "between", "value": [2, 3]},
    {"column": "s", "op": "in", "value": ["x"]},
    {"column": "s", "op": "not_in", "value": ["x"]},
])
def test_na_keep_adds_the_null_rows_and_nothing_else_for_every_operator(spec):
    removed = ids({**spec, "na": "remove"})
    kept = ids({**spec, "na": "keep"})
    assert "d" not in removed and "d" in kept
    assert [i for i in kept if i != "d"] == removed  # the null row is the only difference, order unchanged


def test_na_is_required():
    with pytest.raises(TransformationError, match="na"):
        run({"column": "n", "op": "eq", "value": 2})


def test_na_must_be_keep_or_remove():
    with pytest.raises(TransformationError):
        run({"column": "n", "op": "eq", "value": 2, "na": "drop"})


# -- NaN is a number, not a missing value ---------------------------------------------------------------

def test_a_nan_is_not_touched_by_na():
    # NaN > 2.0 is true in Polars (NaN sorts above every number), and `na` only decides the null row
    assert ids({"column": "f", "op": "gt", "value": 2.0, "na": "remove"}) == ["b", "c", "e"]
    assert ids({"column": "f", "op": "gt", "value": 2.0, "na": "keep"}) == ["b", "c", "d", "e"]


# -- rows and order --------------------------------------------------------------------------------------

def test_the_rows_keep_their_order_and_the_columns_stay():
    got = run({"column": "n", "op": "ge", "value": 2, "na": "remove"})
    assert got.columns == FRAME.columns and got["id"].to_list() == ["b", "c", "e"]


def test_nothing_matching_gives_an_empty_table_with_the_same_columns():
    got = run({"column": "n", "op": "gt", "value": 99, "na": "remove"})
    assert got.height == 0 and got.columns == FRAME.columns and got.schema == FRAME.schema


# -- what it refuses -------------------------------------------------------------------------------------

def test_a_column_that_is_not_in_the_table_fails_and_is_not_skipped():
    with pytest.raises(TransformationError, match="no_such"):
        run({"column": "no_such", "op": "eq", "value": 1, "na": "remove"})


@pytest.mark.parametrize("spec", [
    {"column": "n", "op": "in", "value": 2, "na": "remove"},              # a scalar where a list is needed
    {"column": "n", "op": "eq", "value": [1, 2], "na": "remove"},        # a list where a scalar is needed
    {"column": "n", "op": "between", "value": [1], "na": "remove"},     # not a pair
    {"column": "n", "op": "between", "value": 1, "na": "remove"},
    {"column": "n", "op": "eq", "value": 1, "closed": "both", "na": "remove"},  # closed belongs to between only
    {"column": "n", "op": "like", "value": 1, "na": "remove"},          # not an operator
    {"column": "n", "op": "eq", "na": "remove"},                          # no value
    {"op": "eq", "value": 1, "na": "remove"},                             # no column
    {"column": "n", "op": "eq", "value": 1, "na": "remove", "extra": 1},  # an unknown key
])
def test_a_wrong_step_is_refused(spec):
    with pytest.raises(TransformationError):
        run(spec)
