"""
Known defects of the filter engine, written down as tests (package P0, 2026-11-13).

Each defect test is marked `xfail(strict=True)` with its issue number: the suite stays green today, and
the day the defect is fixed the mark itself fails (XPASS strict), so it cannot be forgotten and has to
be removed in the commit that fixes it. The expected values are the decided rules, not today's output:

  #62  an integer column with a non-integer threshold: compare as numbers; `>= 90.5` keeps 91 only.
       The recipe filter (`modif_filter`, what filter_range, filter_lt, filter_gt and filter_eq became) is the reference
       and already do this; the engine truncates (`int(float(value))`), so the figure and the
       reproducibility bundle disagree.
  #63  a missing value is a value (`home_audit_steps.md` section 19): `!=` and none-of keep it;
       `==`, one-of and comparisons remove it; always counted and reported. Today `!=` and none-of
       drop it silently, and NaN is kept by `>=` but dropped by `<`.

DECISION TO TAKE (do not forget): each defect below was verified on 2026-11-13 and must be verified
again before it is fixed; if an issue is outdated or the rule changed, change or delete its test
here and say why in the commit. The fix belongs to package P1 (`HOME-EXPLORE-1`, `NA-RULE-63`,
`FILTER-DTYPES-1` in `.claude/tasks/tasks.md`); the shared implementation will live in `libs/utils`
and these tests then import it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_defects.py -q
"""
import polars as pl
import pytest

from app.modules.t3_audit_engine import _apply_filter_rows
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.step_migration import convert_step


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

@pytest.mark.xfail(strict=True, reason="#63 != drops the row with a missing value silently; the rule keeps it")
def test_not_equal_keeps_the_row_with_a_missing_value(with_missing):
    assert ids(with_missing, [{"column": "g", "op": "ne", "value": "A"}]) == ["b", "c"]


@pytest.mark.xfail(strict=True, reason="#63 none-of drops the row with a missing value silently; the rule keeps it")
def test_none_of_keeps_the_row_with_a_missing_value(with_missing):
    assert ids(with_missing, [{"column": "g", "op": "not_in", "value": ["A"]}]) == ["b", "c"]


def test_equal_and_one_of_remove_the_row_with_a_missing_value(with_missing):
    """Already as the rule says (this part of #63 needs no change)."""
    assert ids(with_missing, [{"column": "g", "op": "eq", "value": "A"}]) == ["a"]
    assert ids(with_missing, [{"column": "g", "op": "in", "value": ["A", "B"]}]) == ["a", "c"]


@pytest.mark.xfail(strict=True, reason="#63 NaN is kept by >= and dropped by <: it must behave as a missing value")
def test_nan_and_null_behave_the_same_in_comparisons():
    lf = pl.LazyFrame({"n": [1.0, None, float("nan")], "s": ["a", "b", "c"]})
    # the rule: a comparison removes a missing value, whichever way it is written
    assert ids(lf, [{"column": "n", "op": "ge", "value": "0"}]) == ["a"]
    assert ids(lf, [{"column": "n", "op": "lt", "value": "5"}]) == ["a"]


def test_a_missing_value_is_not_counted_or_reported_today(with_missing):
    """Pins the gap: the engine returns rows only. The count of rows removed for a missing value
    ('N rows have no value in this column') is part of P1 and will replace this test."""
    result = _apply_filter_rows(with_missing, [{"column": "g", "op": "ne", "value": "A"}])
    assert hasattr(result, "collect") and not hasattr(result, "removed_missing")
