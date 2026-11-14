"""The three filters give the same rows (issue #62, HOME-EXPLORE-1).

For every operator, on integer, float and text columns, with values written as `.0`, `.5` and integers:
the HOME engine (`_apply_filter_rows`), the plot filter of VizFactory and the action the reproducibility export
re-runs (what `t3_translator` emits: `modif_filter`) return the same rows. The expected rows are written by hand.

Not covered on purpose: missing values (#63, NA-RULE-63).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_int_equivalence.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.t3_audit_engine import _apply_filter_rows
from blueprint_arch.t3_translator import translate_t3_node
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from viz_factory.viz_factory import VizFactory

FRAME = pl.DataFrame({
    "i": [89, 90, 91],
    "f": [89.0, 90.0, 91.0],
    "t": ["89", "90", "91"],
    "s": ["a", "b", "c"],
})


def by_engine(rows):
    return _apply_filter_rows(FRAME.lazy(), rows).collect()["s"].to_list()


def by_plot(rows):
    recipe = {"plots": {"p": {"mapping": {"x": "s", "y": "i"}, "layers": [{"name": "geom_col", "params": {}}],
                              "filters": rows}}}
    return VizFactory().render(FRAME.lazy(), recipe, "p").data["s"].to_list()


def by_translated_action(rows):
    """The action list the reproducibility export re-runs; `between` has no translation, so it is run as modif_filter directly."""
    lf = FRAME.lazy()
    for row in rows:
        steps = ([{"action": "modif_filter", **row, "na": "remove"}] if row["op"] == "between"
                 else translate_t3_node({"node_type": "filter_row", "params": row}))
        for step in steps:
            lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
    return lf.collect()["s"].to_list()


def row(col, op, value, **extra):
    return {"column": col, "op": op, "value": value, **extra}


# (op, value, expected rows) on the integer column [89, 90, 91] and the float column [89.0, 90.0, 91.0]
NUMERIC_CASES = [
    ("ge", 90.5, ["c"]), ("gt", 90.5, ["c"]), ("lt", 90.5, ["a", "b"]), ("le", 90.5, ["a", "b"]),
    ("eq", 90.5, []), ("ne", 90.5, ["a", "b", "c"]),
    ("ge", 90.0, ["b", "c"]), ("gt", 90.0, ["c"]), ("lt", 90.0, ["a"]), ("le", 90.0, ["a", "b"]),
    ("eq", 90.0, ["b"]), ("ne", 90.0, ["a", "c"]),
    ("ge", 90, ["b", "c"]), ("eq", 90, ["b"]), ("lt", 90, ["a"]),
    ("between", [89.5, 90.5], ["b"]), ("between", [90, 91], ["b", "c"]),
]
SET_CASES = [("in", [90.5, 91], ["c"]), ("not_in", [90.5, 91], ["a", "b"]), ("in", [90.0], ["b"]), ("not_in", [90.0], ["a", "c"])]


@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("op, value, expected", NUMERIC_CASES)
def test_numeric_value_all_three_agree(column, op, value, expected):
    rows = [row(column, op, value)]
    assert by_engine(rows) == by_plot(rows) == by_translated_action(rows) == expected


# VizFactory builds in / not_in by comparing text ("91.0" is not "91"), the engine and the action compare numbers.
# Not the threshold defect of #62; reported to Eve (open choice), the mark goes when VizFactory is aligned.
VIZ_SET_DEFECT = {("f", "in", 0), ("f", "not_in", 1), ("i", "in", 2), ("i", "not_in", 3)}


@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("n", range(len(SET_CASES)))
def test_set_operators_engine_and_translated_action_agree(column, n):
    op, value, expected = SET_CASES[n]
    rows = [row(column, op, value)]
    assert by_engine(rows) == by_translated_action(rows) == expected


@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("n", range(len(SET_CASES)))
def test_set_operators_plot_filter_agrees(column, n, request):
    op, value, expected = SET_CASES[n]
    if (column, op, n) in VIZ_SET_DEFECT:
        request.applymarker(pytest.mark.xfail(strict=True, reason="plot in/not_in compares text: 91.0 is not 91 (reported to Eve)"))
    assert by_plot([row(column, op, value)]) == expected


@pytest.mark.parametrize("column", ["i", "f"])
@pytest.mark.parametrize("op, value, expected", [c for c in NUMERIC_CASES if c[0] != "between" and not isinstance(c[1], list)])
def test_text_value_as_the_panel_stores_it_engine_and_plot_agree(column, op, value, expected):
    """The panel stores the value as text. The translated action is not run here: see the report (it refuses a text value)."""
    rows = [row(column, op, str(value))]
    assert by_engine(rows) == by_plot(rows) == expected


@pytest.mark.parametrize("op, value, expected", [
    ("eq", "90", ["b"]), ("ne", "90", ["a", "c"]), ("in", ["89", "91"], ["a", "c"]), ("not_in", ["89"], ["b", "c"]),
    ("ge", "90", ["b", "c"]),  # text compares as text: "90" <= "91"
    ("eq", "90.5", []),
])
def test_text_column_all_three_agree(op, value, expected):
    rows = [row("t", op, value)]
    assert by_engine(rows) == by_plot(rows) == by_translated_action(rows) == expected


def test_between_text_value_on_an_integer_column_keeps_the_inside():
    rows = [row("i", "between", ["89.5", "90.5"])]
    assert by_engine(rows) == by_plot(rows) == ["b"]
    rows = [row("i", "between", ["89.5", "90.5"], closed="none")]
    assert by_engine(rows) == by_plot(rows) == ["b"]


def test_a_negative_non_integer_threshold_keeps_zero():
    frame = pl.LazyFrame({"x": [-1, 0, 1], "s": ["a", "b", "c"]})
    rows = [row("x", "gt", "-0.5")]
    assert _apply_filter_rows(frame, rows).collect()["s"].to_list() == ["b", "c"]
