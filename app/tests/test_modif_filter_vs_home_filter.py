"""`modif_filter` and the HOME filter panel give the same rows where a filter is meant to agree (MODIF-FILTER-VERIFY-1).

The app has three filter implementations: `modif_filter` (a recipe step; the audit compiles to it), the HOME filter
panel (`t3_audit_engine._apply_filter_rows`) and the plot filter of VizFactory (`filters` of the plot spec). This file
compares the first two (the third is a copy of the second, see the finding below). The places where they differ are
tests of their own, because a difference between them is a finding, not an accident.

Finding (2026-11-14, FILTER-UNIFY-1): `_apply_filter_rows` and the filter loop of `VizFactory.render` are two copies of
the same code with the same silent behaviours (a missing column is skipped, a text value is coerced to the number of
the column, a missing value is dropped with no choice). Whether they become `modif_filter` is a design decision.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_modif_filter_vs_home_filter.py -q
"""
import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from app.modules.t3_audit_engine import _apply_filter_rows
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

NAN = float("nan")
FRAME = pl.DataFrame({
    "id": ["a", "b", "c", "d", "e"],
    "n": [1, 2, 3, None, 5],
    "s": ["x", "y", "x", None, "z"],
})


def run(spec):
    return AVAILABLE_WRANGLING_ACTIONS["modif_filter"](FRAME.lazy(), dict(spec)).collect()


def home(rows):
    return _apply_filter_rows(FRAME.lazy(), rows).collect()


@pytest.mark.parametrize("row", [
    {"column": "n", "op": "eq", "value": 2},
    {"column": "n", "op": "ne", "value": 2},
    {"column": "n", "op": "gt", "value": 2},
    {"column": "n", "op": "ge", "value": 2},
    {"column": "n", "op": "lt", "value": 3},
    {"column": "n", "op": "le", "value": 3},
    {"column": "n", "op": "between", "value": [2, 3]},
    {"column": "n", "op": "between", "value": [2, 3], "closed": "left"},
    {"column": "s", "op": "eq", "value": "x"},
    {"column": "s", "op": "ne", "value": "x"},
    {"column": "s", "op": "in", "value": ["x", "z"]},
    {"column": "s", "op": "not_in", "value": ["x"]},
])
def test_the_home_filter_gives_the_same_rows_as_modif_filter_with_na_remove(row):
    assert_frame_equal(home([row]), run({**row, "na": "remove"}))


def test_home_skips_a_missing_column_but_modif_filter_fails():
    """Difference by design: a filter built on one view may name a column another view lacks (issue #56)."""
    row = {"column": "no_such", "op": "eq", "value": 1}
    assert home([row]).height == FRAME.height
    with pytest.raises(TransformationError):
        run({**row, "na": "remove"})


def test_home_reads_an_old_text_value_as_the_number_of_the_column_but_modif_filter_refuses_it():
    """Decided (ADR-104 point 7): the panel keeps the real value; an old row holding text is read from its dtype, the action stays strict."""
    row = {"column": "n", "op": "eq", "value": "2"}
    assert home([row])["id"].to_list() == ["b"]
    with pytest.raises(TransformationError) as exc:
        run({**row, "na": "remove"})
    assert "whole numbers" in str(exc.value)


def test_home_keeps_the_missing_rows_of_a_filter_when_na_is_keep_like_modif_filter():
    """NA-RULE-63 part 2: HOME reads the same choice as modif_filter; without it the rows are removed."""
    row = {"column": "n", "op": "gt", "value": 1}
    assert "d" not in home([row])["id"].to_list()
    assert "d" not in home([{**row, "na": "remove"}])["id"].to_list()
    assert_frame_equal(home([{**row, "na": "keep"}]), run({**row, "na": "keep"}))
    assert "d" in home([{**row, "na": "keep"}])["id"].to_list()


@pytest.mark.parametrize("row", [
    {"column": "n", "op": "ne", "value": 2},
    {"column": "n", "op": "between", "value": [2, 3]},
    {"column": "s", "op": "not_in", "value": ["x"]},
    {"column": "s", "op": "in", "value": ["x", "z"]},
])
def test_the_home_filter_gives_the_same_rows_as_modif_filter_with_na_keep(row):
    assert_frame_equal(home([{**row, "na": "keep"}]), run({**row, "na": "keep"}))
