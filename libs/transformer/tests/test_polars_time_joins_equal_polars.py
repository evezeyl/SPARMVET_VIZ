"""The actions of the group "rank, time and special joins" equal the direct Polars call (Eve, 2026-11-14).

Same method as `test_polars_actions_equal_polars.py` (N9 b): each case is the definition of one action: its name, the
step as a recipe writes it, a probe frame and the direct Polars call whose result it must equal (same rows, same order,
same schema). Determinism is written in the step (DEC34). The cases live here and not in the older file because that file
fixes the list of its cases to the 37 planned actions.

What each test proves:
  - the direct Polars call of every case runs (a typo would hide a real failure);
  - the action equals the direct Polars call, for every option that changes the result;
  - the file layer loses nothing: the pair (recipe + TSV) of an action, read by ingestion and run by the real path,
    equals the direct Polars call on the frame of its first case;
  - the cases cover the five actions of the group, and only those.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_time_joins_equal_polars.py -q
"""
import warnings

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

from test_action_recipe_pairs import ROOT, _run
from test_polars_actions_equal_polars import Case, eager

NAN = float("nan")
GROUP = {"polars_rank"}

# one column with ties, a null and two NaN; a second one with ties and a null
RANKED = pl.DataFrame({
    "id": ["a", "b", "c", "d", "e", "f", "g"],
    "x": [3.0, 1.0, 3.0, None, NAN, 2.0, NAN],
    "n": [5, 5, 7, None, 1, 7, 5],
})

CASES = [
    # -- polars_rank: every method; the first case is the one the pair holds -------------------------
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "min", "descending": False, "target_column": "x_rank"},
         lambda lf: lf.with_columns(pl.col("x").rank("min", descending=False).alias("x_rank"))),
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "average"}, lambda lf: lf.with_columns(pl.col("x").rank("average"))),
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "max"}, lambda lf: lf.with_columns(pl.col("x").rank("max"))),
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "dense"}, lambda lf: lf.with_columns(pl.col("x").rank("dense"))),
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "ordinal"}, lambda lf: lf.with_columns(pl.col("x").rank("ordinal"))),
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "random", "seed": 7},
         lambda lf: lf.with_columns(pl.col("x").rank("random", seed=7))),
    Case("polars_rank", RANKED, {"columns": ["x"], "method": "min", "descending": True},
         lambda lf: lf.with_columns(pl.col("x").rank("min", descending=True))),
    Case("polars_rank", RANKED, {"columns": ["x", "n"], "method": "dense"},
         lambda lf: lf.with_columns(pl.col(["x", "n"]).rank("dense"))),
]


def _id(case: Case) -> str:
    extra = case.spec.get("method") or case.spec.get("strategy") or case.spec.get("how") or ""
    return f"{case.action}-{extra}"


@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_direct_polars_call_of_the_case_runs(case):
    """A typo in a case would make its equality test fail for the wrong reason forever."""
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        assert isinstance(eager(case.polars(case.frame.lazy())), pl.DataFrame)


def test_the_cases_cover_the_actions_of_the_group_built_so_far():
    assert {c.action for c in CASES} <= GROUP and "polars_rank" in {c.action for c in CASES}


@pytest.mark.parametrize("case", CASES, ids=[_id(c) for c in CASES])
def test_the_action_equals_the_direct_polars_call(case):
    action = AVAILABLE_WRANGLING_ACTIONS[case.action]
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        got = eager(action(case.frame.lazy(), dict(case.spec)))
        expected = eager(case.polars(case.frame.lazy()))
    assert_frame_equal(got, expected)


def test_a_case_that_differs_from_polars_is_found():
    """The comparison can fail: the same step against another method is not equal."""
    case = CASES[1]
    got = eager(AVAILABLE_WRANGLING_ACTIONS[case.action](case.frame.lazy(), dict(case.spec)))
    with pytest.raises(AssertionError):
        assert_frame_equal(got, eager(case.frame.lazy().with_columns(pl.col("x").rank("max"))))


# -- the file layer loses nothing -------------------------------------------------------------------

FIRST = {}  # the first case of an action is the one its pair holds
for _case in CASES:
    FIRST.setdefault(_case.action, _case)


@pytest.mark.parametrize("action", sorted(FIRST))
def test_the_ingested_file_is_the_frame_of_the_case_and_the_result_equals_polars(action, monkeypatch):
    monkeypatch.chdir(ROOT)
    case = FIRST[action]
    ingested, got, _ = _run(action)
    assert_frame_equal(ingested, case.frame)  # the TSV, the declared types and null_values lose nothing
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        expected = eager(case.polars(case.frame.lazy()))
    assert_frame_equal(got, expected)
