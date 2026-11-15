"""The type of the table wins over the `dtype` a filter row carries (ADR-104 point 7, reviewer 2026-11-15).

A row's `dtype` can be missing (a hand-built row, an old step) or wrong (the column was cast after the step was written). The
HOME table and the plot read the value from the schema of the table at that node, never from the row.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_schema_dtype_wins.py -q
"""
import polars as pl
import pytest

from app.modules.t3_audit_engine import _apply_filter_rows
from viz_factory.viz_factory import VizFactory

FRAME = pl.DataFrame({"s": ["a", "b", "c"], "n": [1, 2, 3], "i": [89, 90, 91], "t": ["89", "90", "91"]})


def table(row):
    return _apply_filter_rows(FRAME.lazy(), [row]).collect()["s"].to_list()


def plot(row):
    recipe = {"plots": {"p": {"mapping": {"x": "s", "y": "n"}, "layers": [{"name": "geom_col", "params": {}}], "filters": [row]}}}
    return VizFactory().render(FRAME.lazy(), recipe, "p").data["s"].to_list()


# an old value held as text, on a whole-number column
BASE = {"column": "i", "op": "ge", "value": "90"}


@pytest.mark.parametrize("extra", [{}, {"dtype": None}, {"dtype": "String"}, {"dtype": "Utf8"}, {"dtype": "Float64"}, {"dtype": "Boolean"}])
@pytest.mark.parametrize("view", [table, plot])
def test_the_schema_reads_the_value_whatever_the_row_says(view, extra):
    """Missing, empty or wrong `dtype`: the column is Int64, so "90" is the number 90."""
    assert view({**BASE, **extra}) == ["b", "c"]


@pytest.mark.parametrize("extra", [{}, {"dtype": "Int64"}, {"dtype": "Float64"}])
@pytest.mark.parametrize("view", [table, plot])
def test_a_text_column_stays_text_whatever_the_row_says(view, extra):
    """The column is text: "90" is compared as text even when the row says Int64."""
    assert view({"column": "t", "op": "ge", "value": "90", **extra}) == ["b", "c"]
    assert view({"column": "t", "op": "in", "value": ["89"], **extra}) == ["a"]
