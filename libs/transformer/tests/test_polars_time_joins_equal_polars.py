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
import datetime
import warnings

import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS

from test_action_recipe_pairs import ROOT, _run
from test_polars_actions_equal_polars import Case, eager

NAN = float("nan")
GROUP = {"polars_rank", "polars_join_asof", "modif_join_where", "polars_group_by_dynamic", "polars_rolling"}
# Polars gives the pairs of a join on conditions in another order on every run: the action orders them (first table, then second)
# and the rows are compared with the direct call after sorting both; the order itself is tested in test_polars_time_joins_preconditions.py (modif_join_where section)
UNORDERED = {"modif_join_where"}

# one column with ties, a null and two NaN; a second one with ties and a null
RANKED = pl.DataFrame({
    "id": ["a", "b", "c", "d", "e", "f", "g"],
    "x": [3.0, 1.0, 3.0, None, NAN, 2.0, NAN],
    "n": [5, 5, 7, None, 1, 7, 5],
})

# as-of join: both tables sorted ascending on t (within each site too)
ASOF_LEFT = pl.DataFrame({
    "id": ["a", "b", "c", "d", "e", "f"], "site": ["s1", "s2", "s1", "s2", "s1", "s3"],
    "t": [1, 2, 4, 6, 9, 10], "x": [10, 20, 30, 40, 50, 60],
})
ASOF_RIGHT = pl.DataFrame({
    "site": ["s1", "s2", "s1", "s2", "s1"], "t": [0, 3, 5, 5, 8], "v": [100, 200, 300, 400, 500],
})
# the same idea with other names for the key and the group column, and a Date key
ASOF_LEFT_RENAMED = ASOF_LEFT.rename({"t": "t_l", "site": "site_l", "x": "v_l"})
ASOF_RIGHT_RENAMED = ASOF_RIGHT.rename({"t": "t_r", "site": "site_r", "v": "v_l"})
DATE_LEFT = pl.DataFrame({"d": [datetime.date(2022, 1, 1), datetime.date(2022, 1, 5), datetime.date(2022, 1, 20)], "x": [1, 2, 3]})
DATE_RIGHT = pl.DataFrame({"d": [datetime.date(2022, 1, 2), datetime.date(2022, 1, 4)], "v": [10, 20]})

# join on conditions: whole numbers only (Polars does not compare Int64 with Float64)
WHERE_LEFT = pl.DataFrame({"id": ["a", "b", "c", "d"], "lo": [1, 5, None, 3], "hi": [4, 9, 3, 8]})
WHERE_RIGHT = pl.DataFrame({"rid": ["x", "y", "z", "w"], "v": [2, 5, 10, 4]})
WHERE_RIGHT_CLASH = WHERE_RIGHT.with_columns(lo=pl.lit(0, dtype=pl.Int64))
WHERE_FLOAT_LEFT = pl.DataFrame({"id": ["a", "b"], "lo": [1.0, 5.0], "hi": [4.0, 9.0]})
WHERE_FLOAT_RIGHT = pl.DataFrame({"rid": ["x", "y", "n"], "v": [2.0, 5.0, NAN]})

# windows: sorted by d (and by d within each country), a null and a NaN in f
D = datetime.date
WINDOWED = pl.DataFrame({
    "d": [D(2022, 1, 3), D(2022, 1, 10), D(2022, 1, 20), D(2022, 2, 2), D(2022, 2, 15), D(2022, 3, 1), D(2022, 3, 5)],
    "country": ["NO", "SE", "NO", "SE", "NO", "SE", "NO"],
    "f": [1.0, 2.0, None, NAN, 5.0, 6.0, 7.0],
})
WINDOWED_INT = pl.DataFrame({"i": [1, 2, 3, 4, 7, 8, 12], "g": ["a", "b", "a", "b", "a", "b", "a"], "f": [1.0, 2.0, None, NAN, 5.0, 6.0, 7.0]})
WINDOWED_MOMENTS = pl.DataFrame({"t": [datetime.datetime(2022, 1, 1, h) for h in (0, 1, 5, 6, 7, 13)], "f": [1.0, 2.0, 3.0, None, 5.0, 6.0]})

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
    # -- polars_join_asof: the three strategies, with and without `by`, other key names, a Date key -----
    Case("polars_join_asof", ASOF_LEFT, {"right_ingredient": "R", "on": "t", "by": ["site"], "strategy": "backward", "tolerance": 5, "__right_df__": ASOF_RIGHT.lazy()},
         lambda lf: lf.join_asof(ASOF_RIGHT.lazy(), on="t", by=["site"], strategy="backward", tolerance=5)),
    Case("polars_join_asof", ASOF_LEFT, {"right_ingredient": "R", "on": "t", "strategy": "forward", "__right_df__": ASOF_RIGHT.lazy()},
         lambda lf: lf.join_asof(ASOF_RIGHT.lazy(), on="t", strategy="forward")),
    Case("polars_join_asof", ASOF_LEFT, {"right_ingredient": "R", "on": "t", "by": ["site"], "strategy": "nearest", "__right_df__": ASOF_RIGHT.lazy()},
         lambda lf: lf.join_asof(ASOF_RIGHT.lazy(), on="t", by=["site"], strategy="nearest")),
    Case("polars_join_asof", ASOF_LEFT_RENAMED,
         {"right_ingredient": "R", "left_on": "t_l", "right_on": "t_r", "by_left": ["site_l"], "by_right": ["site_r"], "strategy": "backward",
          "suffix": "_other", "coalesce": False, "allow_exact_matches": False, "__right_df__": ASOF_RIGHT_RENAMED.lazy()},
         lambda lf: lf.join_asof(ASOF_RIGHT_RENAMED.lazy(), left_on="t_l", right_on="t_r", by_left=["site_l"], by_right=["site_r"],
                                 strategy="backward", suffix="_other", coalesce=False, allow_exact_matches=False)),
    Case("polars_join_asof", DATE_LEFT, {"right_ingredient": "R", "on": "d", "strategy": "forward", "tolerance": "2d", "__right_df__": DATE_RIGHT.lazy()},
         lambda lf: lf.join_asof(DATE_RIGHT.lazy(), on="d", strategy="forward", tolerance="2d")),
    # -- modif_join_where: two predicates (the pair holds this case), one, a clashing column with a suffix, NaN, no match -----
    Case("modif_join_where", WHERE_LEFT, {"right_ingredient": "R", "predicates": ["pl.col('v') >= pl.col('lo')", "pl.col('v') <= pl.col('hi')"],
                                           "__right_df__": WHERE_RIGHT.lazy()},
         lambda lf: lf.join_where(WHERE_RIGHT.lazy(), pl.col("v") >= pl.col("lo"), pl.col("v") <= pl.col("hi"))),
    Case("modif_join_where", WHERE_LEFT, {"right_ingredient": "R", "predicates": ["pl.col('lo') < pl.col('v')"], "__right_df__": WHERE_RIGHT.lazy()},
         lambda lf: lf.join_where(WHERE_RIGHT.lazy(), pl.col("lo") < pl.col("v"))),
    Case("modif_join_where", WHERE_LEFT, {"right_ingredient": "R", "predicates": ["pl.col('v') >= pl.col('lo_r')"], "suffix": "_r",
                                           "__right_df__": WHERE_RIGHT_CLASH.lazy()},
         lambda lf: lf.join_where(WHERE_RIGHT_CLASH.lazy(), pl.col("v") >= pl.col("lo_r"), suffix="_r")),
    Case("modif_join_where", WHERE_FLOAT_LEFT, {"right_ingredient": "R", "predicates": ["pl.col('v') >= pl.col('lo')", "pl.col('v') <= pl.col('hi')"],
                                                 "__right_df__": WHERE_FLOAT_RIGHT.lazy()},
         lambda lf: lf.join_where(WHERE_FLOAT_RIGHT.lazy(), pl.col("v") >= pl.col("lo"), pl.col("v") <= pl.col("hi"))),
    Case("modif_join_where", WHERE_LEFT, {"right_ingredient": "R", "predicates": ["pl.col('v') > 100"], "__right_df__": WHERE_RIGHT.lazy()},
         lambda lf: lf.join_where(WHERE_RIGHT.lazy(), pl.col("v") > 100)),
    # -- polars_group_by_dynamic: months per country (the pair holds this one), every option, a whole-number index, moments -----
    Case("polars_group_by_dynamic", WINDOWED,
         {"index_column": "d", "every": "1mo", "closed": "left", "group_by": ["country"], "named_aggs": {"isolates": "pl.len()", "total": "pl.col('f').sum()"}},
         lambda lf: lf.group_by_dynamic("d", every="1mo", closed="left", group_by=["country"]).agg(isolates=pl.len(), total=pl.col("f").sum())),
    Case("polars_group_by_dynamic", WINDOWED,
         {"index_column": "d", "every": "2w", "period": "10d", "offset": "1d", "include_boundaries": True, "closed": "right", "label": "right",
          "start_by": "monday", "named_aggs": {"isolates": "pl.len()", "mean_f": "pl.col('f').mean()", "seen": "pl.col('f').count()"}},
         lambda lf: lf.group_by_dynamic("d", every="2w", period="10d", offset="1d", include_boundaries=True, closed="right", label="right",
                                        start_by="monday").agg(isolates=pl.len(), mean_f=pl.col("f").mean(), seen=pl.col("f").count())),
    Case("polars_group_by_dynamic", WINDOWED_INT, {"index_column": "i", "every": "4i", "closed": "both", "named_aggs": {"n": "pl.len()"}},
         lambda lf: lf.group_by_dynamic("i", every="4i", closed="both").agg(n=pl.len())),
    Case("polars_group_by_dynamic", WINDOWED_INT, {"index_column": "i", "every": "4i", "closed": "none", "group_by": ["g"], "label": "datapoint",
                                                   "named_aggs": {"first_f": "pl.col('f').first()", "last_f": "pl.col('f').last()"}},
         lambda lf: lf.group_by_dynamic("i", every="4i", closed="none", group_by=["g"], label="datapoint").agg(
             first_f=pl.col("f").first(), last_f=pl.col("f").last())),
    Case("polars_group_by_dynamic", WINDOWED_MOMENTS, {"index_column": "t", "every": "6h", "closed": "left", "named_aggs": {"total": "pl.col('f').sum()"}},
         lambda lf: lf.group_by_dynamic("t", every="6h", closed="left").agg(total=pl.col("f").sum())),
    # -- polars_rolling: 30 days per country (the pair holds this one), every option, a whole-number index, moments ----------------
    Case("polars_rolling", WINDOWED,
         {"index_column": "d", "period": "30d", "closed": "right", "group_by": ["country"], "named_aggs": {"isolates": "pl.len()", "total": "pl.col('f').sum()"}},
         lambda lf: lf.rolling("d", period="30d", closed="right", group_by=["country"]).agg(isolates=pl.len(), total=pl.col("f").sum())),
    Case("polars_rolling", WINDOWED, {"index_column": "d", "period": "2w", "offset": "-1w", "closed": "both",
                                      "named_aggs": {"isolates": "pl.len()", "mean_f": "pl.col('f').mean()", "seen": "pl.col('f').count()"}},
         lambda lf: lf.rolling("d", period="2w", offset="-1w", closed="both").agg(isolates=pl.len(), mean_f=pl.col("f").mean(), seen=pl.col("f").count())),
    Case("polars_rolling", WINDOWED_INT, {"index_column": "i", "period": "3i", "closed": "left", "named_aggs": {"n": "pl.len()"}},
         lambda lf: lf.rolling("i", period="3i", closed="left").agg(n=pl.len())),
    Case("polars_rolling", WINDOWED_INT, {"index_column": "i", "period": "3i", "closed": "none", "group_by": ["g"],
                                          "named_aggs": {"first_f": "pl.col('f').first()", "last_f": "pl.col('f').last()"}},
         lambda lf: lf.rolling("i", period="3i", closed="none", group_by=["g"]).agg(first_f=pl.col("f").first(), last_f=pl.col("f").last())),
    Case("polars_rolling", WINDOWED_MOMENTS, {"index_column": "t", "period": "3h", "closed": "right", "named_aggs": {"total": "pl.col('f').sum()"}},
         lambda lf: lf.rolling("t", period="3h", closed="right").agg(total=pl.col("f").sum())),
]


def _id(case: Case) -> str:
    extra = case.spec.get("method") or case.spec.get("strategy") or case.spec.get("how") or ""
    return f"{case.action}-{extra}"


def _canonical(case: Case, frame: pl.DataFrame) -> pl.DataFrame:
    """The frame as compared: rows sorted by every column when Polars gives no order for this action."""
    return frame.sort(frame.columns, nulls_last=True) if case.action in UNORDERED else frame


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
    assert_frame_equal(_canonical(case, got), _canonical(case, expected))


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
    assert_frame_equal(_canonical(case, got), _canonical(case, expected))


# -- modif_join_where: the same rows as Polars (as a set), in the stated order, on a table big enough for Polars to vary ------------

def test_modif_join_where_returns_the_rows_of_polars_as_a_set_and_in_the_stated_order_on_every_run():
    """Rows equal Polars' rows (nothing added or dropped); order = first table, then second, on repeated runs (DEC31, DEC32)."""
    import random
    rng = random.Random(1)
    size = 2000
    left = pl.DataFrame({"i": list(range(size)), "a": [rng.randint(0, 100) for _ in range(size)]})
    right = pl.DataFrame({"j": list(range(size)), "b": [rng.randint(0, 100) for _ in range(size)]})
    action = AVAILABLE_WRANGLING_ACTIONS["modif_join_where"]
    spec = {"right_ingredient": "R", "predicates": ["pl.col('a') < pl.col('b')", "pl.col('a') > pl.col('b') - 5"], "__right_df__": right.lazy()}
    polars_rows = left.lazy().join_where(right.lazy(), pl.col("a") < pl.col("b"), pl.col("a") > pl.col("b") - 5).collect()
    first = eager(action(left.lazy(), dict(spec)))
    assert_frame_equal(first.sort(first.columns), polars_rows.sort(polars_rows.columns))
    assert first.sort(["i", "j"]).equals(first), "the rows are not in the order: first table, then second table"
    for _ in range(4):
        assert eager(action(left.lazy(), dict(spec))).equals(first)
