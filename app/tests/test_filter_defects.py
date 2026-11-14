"""
Known defects of the filter engine, written down as tests (package P0, 2026-11-13).

Each defect test is marked `xfail(strict=True)` with its issue number: the suite stays green today, and
the day the defect is fixed the mark itself fails (XPASS strict), so it cannot be forgotten and has to
be removed in the commit that fixes it. The expected values are the decided rules, not today's output:

  #62  an integer column with a non-integer threshold: compare as numbers; `>= 90.5` keeps 91 only.
       The recipe filter (`modif_filter`, what filter_range, filter_lt, filter_gt and filter_eq became) is the reference
       and already do this; the engine truncates (`int(float(value))`), so the figure and the
       reproducibility bundle disagree.
  #63  the NA rule decided by Eve on 2026-11-14 (M65): the engine follows Polars. Every operator removes
       a row with a missing value (null), `!=` and none-of included; NaN is a number larger than every number
       (kept by `!=`, none-of, `>`, `>=`, removed by `<`); `na: keep` of `modif_filter` adds the null rows
       and never changes what happens to NaN. The count sentences are not built yet (xfail "no count").

DECISION TO TAKE (do not forget): each defect below was verified on 2026-11-13 and must be verified
again before it is fixed; if an issue is outdated or the rule changed, change or delete its test
here and say why in the commit. The fix belongs to package P1 (`HOME-EXPLORE-1`, `NA-RULE-63`,
`FILTER-DTYPES-1` in `.claude/tasks/tasks.md`); the shared implementation will live in `libs/utils`
and these tests then import it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_defects.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.t3_audit_engine import _apply_filter_rows
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.step_migration import convert_step
from viz_factory.viz_factory import VizFactory


def _recipe_filter(old_action):
    """The recipe filter that the old action `old_action` became (`modif_filter`, written by the migration)."""
    def run(lf, spec):
        for step in convert_step({"action": old_action, **spec}):
            lf = AVAILABLE_WRANGLING_ACTIONS[step["action"]](lf, {k: v for k, v in step.items() if k != "action"})
        return lf
    return run


action_filter_eq, action_filter_gt, action_filter_lt, action_filter_range = (
    _recipe_filter("filter_eq"), _recipe_filter("filter_gt"), _recipe_filter("filter_lt"), _recipe_filter("filter_range"))


def ids(lf, rows):
    return _apply_filter_rows(lf, rows).collect()["s"].to_list()


@pytest.fixture
def ints():
    return pl.LazyFrame({"x": [89, 90, 91], "s": ["a", "b", "c"]})


@pytest.fixture
def with_missing():
    return pl.LazyFrame({"g": ["A", None, "B"], "s": ["a", "b", "c"]})


# ── #62: integer column, non-integer threshold (fixed, HOME-EXPLORE-1; shared code in utils.filter_values) ──

def test_ge_a_non_integer_threshold_keeps_only_the_larger_integers(ints):
    assert ids(ints, [{"column": "x", "op": "ge", "value": "90.5"}]) == ["c"]


def test_lt_a_non_integer_threshold_keeps_the_smaller_integers(ints):
    assert ids(ints, [{"column": "x", "op": "lt", "value": "90.5"}]) == ["a", "b"]


def test_eq_a_non_integer_threshold_matches_nothing(ints):
    assert ids(ints, [{"column": "x", "op": "eq", "value": "90.5"}]) == []


def test_the_registered_actions_already_compare_integers_to_a_non_integer_threshold(ints):
    """The reference of #62: the recipe actions the reproducibility export runs."""
    rows = lambda fn, spec: fn(ints, spec).collect()["s"].to_list()
    assert rows(action_filter_range, {"columns": ["x"], "min": 90.5}) == ["c"]
    assert rows(action_filter_gt, {"columns": ["x"], "value": 90.5}) == ["c"]
    assert rows(action_filter_lt, {"columns": ["x"], "value": 90.5}) == ["a", "b"]
    assert rows(action_filter_eq, {"columns": ["x"], "value": 90.5}) == []


@pytest.mark.parametrize("op, action, spec", [
    ("ge", action_filter_range, {"min": 90.5}),
    ("lt", action_filter_lt, {"value": 90.5}),
    ("eq", action_filter_eq, {"value": 90.5}),
])
def test_the_engine_and_the_registered_action_give_the_same_rows(ints, op, action, spec):
    by_engine = ids(ints, [{"column": "x", "op": op, "value": "90.5"}])
    by_action = action(ints, {"columns": ["x"], **spec}).collect()["s"].to_list()
    assert by_engine == by_action


def test_gt_agrees_by_coincidence_for_a_positive_threshold(ints):
    """Truncation toward zero makes `> 90.5` read `> 90`, which keeps the same integers: no defect here."""
    by_engine = ids(ints, [{"column": "x", "op": "gt", "value": "90.5"}])
    by_action = action_filter_gt(ints, {"columns": ["x"], "value": 90.5}).collect()["s"].to_list()
    assert by_engine == by_action == ["c"]


def test_gt_a_negative_non_integer_threshold_keeps_zero():
    lf = pl.LazyFrame({"x": [-1, 0, 1], "s": ["a", "b", "c"]})
    assert ids(lf, [{"column": "x", "op": "gt", "value": "-0.5"}]) == ["b", "c"]


# ── #63: missing values ───────────────────────────────────────────────────────

NAN = float("nan")
LABELS = ["a", "b", "c", "d", "e", "f"]


def _num():
    # a=1, b=2, c=3, d=null, e=NaN, f=2
    return pl.LazyFrame({"x": [1.0, 2.0, 3.0, None, NAN, 2.0], "s": LABELS})


def _plot(lf, rows):
    recipe = {"plots": {"p": {"mapping": {"x": "s"}, "layers": [{"name": "geom_bar", "params": {}}],
                              "filters": rows}}}
    return VizFactory().render(lf, recipe, "p").data["s"].to_list()


def _step(lf, rows, na="remove"):
    out = lf
    for r in rows:
        out = AVAILABLE_WRANGLING_ACTIONS["modif_filter"](out, {**r, "na": na})
    return out.collect()["s"].to_list()


def _all_places(lf, row, na="remove"):
    """The three places that filter: the HOME table, the plot, the engine step (with `na`)."""
    return {"home": ids(lf, [row]), "plot": _plot(lf, [row]), "step": _step(lf, [row], na)}


# operator, value, rows kept; null (d) is always removed, NaN (e) follows "a number larger than every number"
RULE = [
    ("eq", 2.0, ["b", "f"]), ("ne", 2.0, ["a", "c", "e"]),
    ("gt", 2.0, ["c", "e"]), ("ge", 2.0, ["b", "c", "e", "f"]),
    ("lt", 2.0, ["a"]), ("le", 2.0, ["a", "b", "f"]),
    ("in", [2.0], ["b", "f"]), ("not_in", [2.0], ["a", "c", "e"]),
    ("between", [1.0, 3.0], ["a", "b", "c", "f"]),
]


@pytest.mark.parametrize("op, value, expected", RULE)
def test_every_operator_removes_the_null_row_and_nan_is_a_large_number(op, value, expected):
    row = {"column": "x", "op": op, "value": value}
    got = _all_places(_num(), row)
    assert got == {"home": expected, "plot": expected, "step": expected}


@pytest.mark.parametrize("op, value, expected", RULE)
def test_na_keep_adds_the_null_row_and_leaves_nan_as_it_was(op, value, expected):
    got = _step(_num(), [{"column": "x", "op": op, "value": value}], na="keep")
    assert got == sorted(expected + ["d"])


def test_not_equal_removes_the_row_with_a_missing_value(with_missing):
    assert ids(with_missing, [{"column": "g", "op": "ne", "value": "A"}]) == ["c"]
    assert _plot(with_missing, [{"column": "g", "op": "ne", "value": "A"}]) == ["c"]


def test_none_of_removes_the_row_with_a_missing_value(with_missing):
    assert ids(with_missing, [{"column": "g", "op": "not_in", "value": ["A"]}]) == ["c"]
    assert _plot(with_missing, [{"column": "g", "op": "not_in", "value": ["A"]}]) == ["c"]


def test_equal_and_one_of_remove_the_row_with_a_missing_value(with_missing):
    assert ids(with_missing, [{"column": "g", "op": "eq", "value": "A"}]) == ["a"]
    assert ids(with_missing, [{"column": "g", "op": "in", "value": ["A", "B"]}]) == ["a", "c"]


def test_na_keep_with_none_of_keeps_the_missing_row(with_missing):
    got = _step(with_missing, [{"column": "g", "op": "not_in", "value": ["A"]}], na="keep")
    assert got == ["b", "c"]


def test_the_text_NA_is_a_value_not_a_missing_value():
    lf = pl.LazyFrame({"t": ["a", None, "NA", "b"], "s": ["a", "b", "c", "d"]})
    ne = {"column": "t", "op": "ne", "value": "a"}
    assert _all_places(lf, ne) == {"home": ["c", "d"], "plot": ["c", "d"], "step": ["c", "d"]}
    assert _step(lf, [{"column": "t", "op": "eq", "value": "NA"}]) == ["c"]
    # keep adds only the real null (row b), not the text "NA"
    assert _step(lf, [ne], na="keep") == ["b", "c", "d"]


def test_a_column_that_is_all_missing():
    lf = pl.LazyFrame({"x": pl.Series([None, None], dtype=pl.Float64), "s": ["a", "b"]})
    for op, value in [("ne", 1.0), ("eq", 1.0), ("gt", 1.0), ("not_in", [1.0])]:
        row = {"column": "x", "op": op, "value": value}
        assert _all_places(lf, row) == {"home": [], "plot": [], "step": []}
        assert _step(lf, [row], na="keep") == ["a", "b"]


def test_a_column_with_nan_only_is_untouched_by_na():
    lf = pl.LazyFrame({"x": [NAN, NAN], "s": ["a", "b"]})
    for na in ("keep", "remove"):
        assert _step(lf, [{"column": "x", "op": "ne", "value": 1.0}], na=na) == ["a", "b"]
        assert _step(lf, [{"column": "x", "op": "lt", "value": 1.0}], na=na) == []
        assert _step(lf, [{"column": "x", "op": "gt", "value": 1.0}], na=na) == ["a", "b"]
    assert ids(lf, [{"column": "x", "op": "lt", "value": "1"}]) == []
    assert ids(lf, [{"column": "x", "op": "gt", "value": "1"}]) == ["a", "b"]


def test_a_missing_value_is_not_counted_or_reported_today(with_missing):
    """Pins the gap: the engine returns rows only. The count of rows removed for a missing value
    ('N rows have no value in this column') is part of P1 and will replace this test."""
    result = _apply_filter_rows(with_missing, [{"column": "g", "op": "ne", "value": "A"}])
    assert hasattr(result, "collect") and not hasattr(result, "removed_missing")
