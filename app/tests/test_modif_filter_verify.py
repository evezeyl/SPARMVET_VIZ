"""modif_filter against the other two filter paths (MODIF-FILTER-VERIFY-1, Eve 2026-11-13: "behaviour must be verified").

One filter vocabulary now exists in three places: the filter rows of HOME and the audit (`_apply_filter_rows`), the
`filters` of a plot spec (VizFactory) and the recipe action `modif_filter`. With `na: remove` the action must give the
same rows as HOME's function for every operator on text, whole numbers and floats, with a null and a NaN in the data.
With `na: keep` the null rows are kept and nothing else changes. NaN is a number (larger than every number) and is
never touched by `na` (spec R6).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_modif_filter_verify.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.t3_audit_engine import _apply_filter_rows
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

NAN = float("nan")
FRAME = pl.DataFrame({
    "id": [1, 2, 3, 4, 5],
    "s": ["A", "B", "A", None, "C"],
    "n": [1, 2, 3, None, 5],
    "f": [1.5, NAN, 2.5, None, 0.5],
})

# (column, op, value) cases, the nine operators on the three kinds of column
CASES = [
    ("s", "eq", "A"), ("s", "ne", "A"), ("s", "in", ["A", "B"]), ("s", "not_in", ["A"]),
    ("n", "eq", 2), ("n", "ne", 2), ("n", "gt", 2), ("n", "ge", 2), ("n", "lt", 3), ("n", "le", 3),
    ("n", "in", [1, 5]), ("n", "not_in", [1, 5]), ("n", "between", [2, 3]),
    ("f", "gt", 1.0), ("f", "lt", 2.0), ("f", "ge", 1.5), ("f", "le", 1.5), ("f", "ne", 1.5),
    ("f", "between", [1.0, 3.0]), ("f", "not_in", [1.5]),
]


def _ids(frame):
    return sorted(frame.collect()["id"].to_list()) if isinstance(frame, pl.LazyFrame) else sorted(frame["id"].to_list())


def _action(column, op, value, na, **extra):
    spec = {"column": column, "op": op, "value": value, "na": na, **extra}
    return _ids(AVAILABLE_WRANGLING_ACTIONS["modif_filter"](FRAME.lazy(), spec))


@pytest.mark.parametrize("column,op,value", CASES, ids=[f"{c}-{o}" for c, o, _ in CASES])
def test_na_remove_equals_the_home_filter_rows(column, op, value):
    home = _ids(_apply_filter_rows(FRAME.lazy(), [{"column": column, "op": op, "value": value}]))
    assert _action(column, op, value, "remove") == home


@pytest.mark.parametrize("column,op,value", CASES, ids=[f"{c}-{o}" for c, o, _ in CASES])
def test_na_keep_adds_exactly_the_null_rows(column, op, value):
    removed = set(_action(column, op, value, "remove"))
    kept = set(_action(column, op, value, "keep"))
    nulls = set(FRAME.filter(pl.col(column).is_null())["id"].to_list())
    assert kept == removed | nulls


def test_a_nan_is_never_a_missing_value():
    """f has a NaN in row 2: `na` does not touch it, it is a number larger than the others."""
    assert 2 in _action("f", "gt", 100.0, "remove") and 2 in _action("f", "gt", 100.0, "keep")
    assert 2 not in _action("f", "lt", 100.0, "keep")


def test_between_is_inclusive_by_default_and_closed_changes_it():
    assert _action("n", "between", [2, 3], "remove") == [2, 3]
    assert _action("n", "between", [2, 3], "remove", closed="none") == []
    assert _action("n", "between", [2, 3], "remove", closed="left") == [2]


@pytest.mark.parametrize("spec,why", [
    ({"column": "n", "op": "gt", "value": 1}, "na is required"),
    ({"column": "n", "op": "gt", "value": [1], "na": "remove"}, "a list where a single value is needed"),
    ({"column": "n", "op": "in", "value": 1, "na": "remove"}, "a single value where a list is needed"),
    ({"column": "n", "op": "between", "value": [1], "na": "remove"}, "between needs two values"),
    ({"column": "n", "op": "gt", "value": 1, "na": "remove", "closed": "both"}, "closed belongs to between"),
    ({"column": "n", "op": "like", "value": "x", "na": "remove"}, "an unknown operator"),
    ({"column": "n", "op": "gt", "value": 1, "na": "maybe"}, "an unknown na"),
    ({"column": "nope", "op": "gt", "value": 1, "na": "remove"}, "a missing column"),
])
def test_a_step_that_cannot_filter_fails_instead_of_returning_everything(spec, why):
    with pytest.raises((TransformationError, pl.exceptions.PolarsError)):
        AVAILABLE_WRANGLING_ACTIONS["modif_filter"](FRAME.lazy(), spec).collect()


def test_the_registry_says_modified():
    from transformer.actions.base import ACTION_SCHEMAS
    assert ACTION_SCHEMAS["modif_filter"]["polars"] == "modified"
