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


def test_home_coerces_a_text_value_to_the_number_of_the_column_but_modif_filter_does_not():
    """Difference to decide: the filter panel sends text, so HOME casts it; a recipe writes the right type."""
    row = {"column": "n", "op": "eq", "value": "2"}
    assert home([row])["id"].to_list() == ["b"]
    with pytest.raises(Exception):
        run({**row, "na": "remove"})


def test_home_has_no_way_to_keep_the_missing_rows_of_a_filter():
    """HOME always drops them (what Polars does); modif_filter makes it a written choice."""
    row = {"column": "n", "op": "gt", "value": 1}
    assert "d" not in home([row])["id"].to_list()
    assert "d" in run({**row, "na": "keep"})["id"].to_list()
