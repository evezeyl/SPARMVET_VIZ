"""What the actions of the group "rank, time and special joins" need, and what they do when it is missing (Eve, 2026-11-14).

Each action here depends on row order or on sorted keys. For each one this file proves, by running Polars 1.40.1 and the
action: the precondition fails with a plain message when it is not met (never a silent wrong result), the order of the
result is the same on every run (ADR-090), and what a null and a NaN do (one sentence of the action's description).

Sections: polars_rank, ...

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_time_joins_preconditions.py -q
"""
import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

NAN = float("nan")


def run(action, frame, spec):
    return AVAILABLE_WRANGLING_ACTIONS[action](frame.lazy(), spec).collect()


# =========================================================================================================
# polars_rank
# =========================================================================================================

RANK_X = pl.DataFrame({"x": [3.0, 1.0, 3.0, None, NAN, 2.0, NAN]})


def rank(method, frame=RANK_X, **more):
    return run("polars_rank", frame, {"columns": ["x"], "method": method, **more})["x"].to_list()


def test_rank_a_null_stays_null_and_is_not_counted():
    assert rank("dense")[3] is None and rank("average")[3] is None and rank("min", descending=True)[3] is None
    assert max(r for r in rank("dense") if r is not None) == 4  # 3, 1, 2 and the NaN: six rows hold four distinct values


def test_rank_a_nan_ranks_above_every_number_and_nans_tie():
    ranks = rank("average")
    assert ranks[4] == ranks[6] == 5.5
    assert ranks[4] > max(r for r in ranks[:4] + ranks[5:6] if r is not None)


def test_rank_the_tie_rules_differ_as_documented():
    assert rank("min") == [3, 1, 3, None, 5, 2, 5]
    assert rank("max") == [4, 1, 4, None, 6, 2, 6]
    assert rank("dense") == [3, 1, 3, None, 4, 2, 4]
    assert rank("ordinal") == [3, 1, 4, None, 5, 2, 6]


def test_rank_ordinal_depends_on_the_row_order_and_the_other_methods_do_not():
    """The reason the description says "sort first": the same rows in another order give other ordinal ranks for the ties."""
    reversed_frame = RANK_X.reverse()
    forward, backward = rank("ordinal"), rank("ordinal", reversed_frame)[::-1]
    assert forward != backward
    assert rank("min") == rank("min", reversed_frame)[::-1]
    assert rank("average") == rank("average", reversed_frame)[::-1]


def test_rank_random_with_a_seed_gives_the_same_ranks_on_every_run():
    first = rank("random", seed=7)
    assert all(rank("random", seed=7) == first for _ in range(5))
    assert rank("random", seed=1) != rank("random", seed=2)  # the seed is used (these two seeds differ on this frame)


def test_rank_random_without_a_seed_is_refused_because_polars_would_differ_on_every_run():
    with pytest.raises(TransformationError, match="seed is required when method is random"):
        rank("random")
    ties = pl.DataFrame({"x": [1.0] * 30})
    polars_runs = {tuple(ties.select(pl.col("x").rank("random")).to_series().to_list()) for _ in range(5)}
    assert len(polars_runs) > 1, "Polars itself is not reproducible without a seed: the reason for the refusal"


@pytest.mark.parametrize("method", ["average", "min", "max", "dense", "ordinal"])
def test_rank_a_seed_with_another_method_is_refused_because_polars_ignores_it_silently(method):
    with pytest.raises(TransformationError, match="seed cannot be given"):
        rank(method, seed=1)
    assert rank(method) == run_polars_rank(method)  # and Polars gives the same ranks with or without the seed


def run_polars_rank(method):
    return RANK_X.select(pl.col("x").rank(method, seed=1)).to_series().to_list()


def test_rank_the_method_is_required_there_is_no_hidden_tie_rule():
    with pytest.raises(TransformationError, match="method is required"):
        run("polars_rank", RANK_X, {"columns": ["x"]})


def test_rank_an_unknown_method_is_refused():
    with pytest.raises(TransformationError, match="average, min, max, dense, ordinal, random"):
        rank("median")


@pytest.mark.parametrize("seed", [1.5, -1, True, "7", 2 ** 64])
def test_rank_a_seed_that_is_not_a_whole_number_from_zero_is_refused_with_a_plain_message(seed):
    with pytest.raises(TransformationError):
        rank("random", seed=seed)


def test_rank_a_target_column_needs_exactly_one_column():
    with pytest.raises(TransformationError, match="target_column"):
        run("polars_rank", pl.DataFrame({"x": [1], "y": [2]}), {"columns": ["x", "y"], "method": "min", "target_column": "r"})


def test_rank_a_missing_column_fails_instead_of_being_ignored():
    with pytest.raises(Exception, match="nope"):
        run("polars_rank", RANK_X, {"columns": ["nope"], "method": "min"})


def test_rank_of_an_empty_table_is_an_empty_table_with_the_rank_type():
    empty = pl.DataFrame({"x": []}, schema={"x": pl.Float64})
    out = run("polars_rank", empty, {"columns": ["x"], "method": "min"})
    assert out.height == 0 and out.schema["x"] == pl.UInt32


def test_rank_text_columns_rank_alphabetically_and_equal_polars():
    frame = pl.DataFrame({"s": ["b", "a", "b", None]})
    got = run("polars_rank", frame, {"columns": ["s"], "method": "dense"})
    assert_frame_equal(got, frame.select(pl.col("s").rank("dense")))
    assert got["s"].to_list() == [2, 1, 2, None]


# =========================================================================================================
# polars_join_asof
# =========================================================================================================

import datetime  # noqa: E402
import warnings  # noqa: E402

from polars.testing import assert_frame_equal  # noqa: E402,F811

LEFT = pl.DataFrame({"t": [1, 2, 3, 5], "g": ["a", "b", "a", "b"], "x": [1, 2, 3, 4]})
RIGHT = pl.DataFrame({"t": [0, 1, 2, 3], "g": ["b", "a", "a", "b"], "v": [1, 2, 3, 4]})
SORT_FIX = "polars_sort"


def asof(left=LEFT, right=RIGHT, **more):
    spec = {"right_ingredient": "R", "on": "t", "strategy": "backward", "__right_df__": right.lazy(), **more}
    return run("polars_join_asof", left, spec)


def polars_asof(left=LEFT, right=RIGHT, **more):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        return left.lazy().join_asof(right.lazy(), on="t", **more).collect()


def test_asof_the_result_keeps_the_rows_and_the_order_of_the_first_table_even_with_interleaved_groups():
    out = asof(by=["g"])
    assert out["x"].to_list() == [1, 2, 3, 4] and out["t"].to_list() == [1, 2, 3, 5]
    assert all(asof(by=["g"]).equals(out) for _ in range(5))
    assert_frame_equal(out, polars_asof(strategy="backward", by=["g"]))


def test_asof_the_first_table_unsorted_without_by_fails_with_a_plain_message_and_the_fix():
    unsorted = pl.DataFrame({"t": [5, 1], "g": ["a", "a"], "x": [1, 2]})
    with pytest.raises(TransformationError) as caught:
        asof(unsorted)
    assert "'t'" in str(caught.value) and "not sorted ascending" in str(caught.value) and "table at this step" in str(caught.value)
    assert SORT_FIX in caught.value.tip and "maintain_order" in caught.value.tip


def test_asof_the_second_table_unsorted_without_by_fails_and_names_the_ingredient():
    with pytest.raises(TransformationError, match="'R' is not sorted ascending"):
        asof(right=RIGHT.sort("t", descending=True))


def test_asof_unsorted_within_a_group_is_refused_because_polars_returns_a_wrong_result_without_a_word():
    """The reason for the own check: Polars cannot check within groups and gives a wrong match for the row t=1."""
    unsorted = pl.DataFrame({"t": [5, 1], "g": ["a", "a"], "x": [1, 2]})
    right = pl.DataFrame({"t": [2, 6], "g": ["a", "a"], "v": [20, 60]})
    wrong = polars_asof(unsorted, right, strategy="backward", by=["g"])
    assert wrong["v"].to_list() == [20, 20], "Polars matched t=1 with the row at t=2, which lies after it: a wrong result"
    with pytest.raises(TransformationError, match=r"not sorted ascending within each group of \['g'\]"):
        asof(unsorted, right, by=["g"])


def test_asof_unsorted_in_the_second_table_within_one_group_only_is_refused():
    right = pl.DataFrame({"t": [0, 1, 4, 3], "g": ["a", "a", "b", "b"], "v": [1, 2, 3, 4]})
    with pytest.raises(TransformationError, match="'R'"):
        asof(LEFT, right, by=["g"])


def test_asof_sorted_within_each_group_but_not_over_the_whole_table_works_with_by_and_fails_without():
    left = pl.DataFrame({"t": [9, 1, 10, 2], "g": ["z", "a", "z", "a"], "x": [1, 2, 3, 4]})
    right = pl.DataFrame({"t": [0, 8, 1, 9], "g": ["a", "z", "a", "z"], "v": [1, 2, 3, 4]})
    out = asof(left, right, by=["g"])
    assert out["v"].to_list() == [4, 3, 4, 3]
    assert_frame_equal(out, polars_asof(left, right, strategy="backward", by=["g"]))
    with pytest.raises(TransformationError, match="not sorted ascending"):
        asof(left, right)


def test_asof_a_step_cannot_switch_the_sortedness_check_off():
    with pytest.raises(TransformationError, match="check_sortedness"):
        asof(check_sortedness=False)


def test_asof_a_null_key_before_the_values_never_matches_and_a_null_elsewhere_is_refused():
    left = pl.DataFrame({"t": [None, 1, 5], "x": [1, 2, 3]})
    right = pl.DataFrame({"t": [None, 0, 2], "v": [1, 2, 3]})
    out = asof(left, right)
    assert out["v"].to_list() == [None, 2, 3]  # the null row has no match; the null of the second table is not a match for any row
    assert_frame_equal(out, polars_asof(left, right, strategy="backward"))
    for bad in (pl.DataFrame({"t": [1, None, 5], "x": [1, 2, 3]}), pl.DataFrame({"t": [1, 5, None], "x": [1, 2, 3]})):
        with pytest.raises(TransformationError, match="not sorted ascending"):
            asof(bad, right)


def test_asof_a_null_in_by_never_matches():
    left = pl.DataFrame({"t": [1, 2], "g": ["a", None], "x": [1, 2]})
    right = pl.DataFrame({"t": [0, 1], "g": ["a", None], "v": [10, 20]})
    assert asof(left, right, by=["g"])["v"].to_list() == [10, None]


def test_asof_a_nan_key_sorts_last_and_matches_a_nan():
    left = pl.DataFrame({"t": [1.0, 2.0, NAN], "x": [1, 2, 3]})
    right = pl.DataFrame({"t": [0.5, 1.5, NAN], "v": [1, 2, 3]})
    out = asof(left, right)
    assert out["v"].to_list() == [1, 2, 3]
    assert_frame_equal(out, polars_asof(left, right, strategy="backward"))
    with pytest.raises(TransformationError, match="not sorted ascending"):
        asof(pl.DataFrame({"t": [NAN, 1.0], "x": [1, 2]}), right)


def test_asof_a_second_table_with_no_rows_gives_nulls():
    out = asof(right=RIGHT.head(0))
    assert out["v"].to_list() == [None] * 4 and out.height == 4


def test_asof_strategy_is_required_and_must_be_one_of_the_three():
    with pytest.raises(TransformationError, match="strategy is required"):
        run("polars_join_asof", LEFT, {"right_ingredient": "R", "on": "t", "__right_df__": RIGHT.lazy()})
    with pytest.raises(TransformationError, match="backward, forward, nearest"):
        asof(strategy="closest")


def test_asof_a_half_pair_of_keys_is_refused():
    with pytest.raises(TransformationError, match="left_on and right_on go together"):
        asof(on=None, left_on="t")
    with pytest.raises(TransformationError, match="by_left and by_right go together"):
        asof(by_left=["g"])
    with pytest.raises(TransformationError, match="exactly one of on, left_on"):
        run("polars_join_asof", LEFT, {"right_ingredient": "R", "strategy": "backward", "__right_df__": RIGHT.lazy()})
    with pytest.raises(TransformationError, match="cannot be given together"):
        asof(left_on="t", right_on="t")


def test_asof_a_missing_key_column_is_a_plain_message_naming_the_columns():
    with pytest.raises(TransformationError, match="'nope' is not in the table at this step"):
        asof(on="nope")
    with pytest.raises(TransformationError, match="'g' is not in 'R'") as caught:
        asof(right=RIGHT.drop("g"), by=["g"])
    assert "columns" in str(caught.value)


def test_asof_the_second_table_is_required():
    with pytest.raises(TransformationError, match="__right_df__"):
        run("polars_join_asof", LEFT, {"right_ingredient": "R", "on": "t", "strategy": "backward"})


# -- the tolerance: Polars panics or reads it in units nobody wrote -------------------------------------------

DAYS = pl.DataFrame({"d": [datetime.date(2022, 1, 1), datetime.date(2022, 1, 5)], "x": [1, 2]})
DAYS_RIGHT = pl.DataFrame({"d": [datetime.date(2022, 1, 2), datetime.date(2022, 1, 4)], "v": [1, 2]})
MOMENTS = pl.DataFrame({"d": [datetime.datetime(2022, 1, 1), datetime.datetime(2022, 1, 2)], "x": [1, 2]})
MOMENTS_RIGHT = pl.DataFrame({"d": [datetime.datetime(2022, 1, 1, 12), datetime.datetime(2022, 1, 2, 1)], "v": [1, 2]})


def asof_d(left, right, **more):
    return run("polars_join_asof", left, {"right_ingredient": "R", "on": "d", "strategy": "forward", "__right_df__": right.lazy(), **more})


def test_asof_a_duration_text_for_a_number_key_is_refused_because_polars_panics():
    with pytest.raises(pl.exceptions.PanicException, match="timedelta string"):
        LEFT.lazy().join_asof(RIGHT.lazy(), on="t", tolerance="1d").collect()
    with pytest.raises(TransformationError, match="is a duration but the key 't' is Int64"):
        asof(tolerance="1d")


def test_asof_a_number_for_a_datetime_key_is_refused_because_polars_reads_microseconds():
    seconds = MOMENTS.lazy().join_asof(MOMENTS_RIGHT.lazy(), on="d", strategy="forward", tolerance=7200).collect()
    assert seconds["v"].to_list() == [None, None], "two hours written as 7200 are 7200 microseconds in Polars: nothing matches, silently"
    with pytest.raises(TransformationError, match="microseconds"):
        asof_d(MOMENTS, MOMENTS_RIGHT, tolerance=7200)
    assert asof_d(MOMENTS, MOMENTS_RIGHT, tolerance="2h")["v"].to_list() == [None, 2]


def test_asof_a_tolerance_finer_than_a_day_for_a_date_key_is_refused_and_days_and_weeks_work():
    with pytest.raises(TransformationError, match="cannot be finer than a day"):
        asof_d(DAYS, DAYS_RIGHT, tolerance="1h")
    out = asof_d(DAYS, DAYS_RIGHT, tolerance="2d")
    assert out["v"].to_list() == [1, None]
    assert_frame_equal(out, DAYS.lazy().join_asof(DAYS_RIGHT.lazy(), on="d", strategy="forward", tolerance="2d").collect())
    wide = pl.DataFrame({"d": [datetime.date(2022, 1, 1), datetime.date(2022, 1, 20)], "x": [1, 2]})
    far = pl.DataFrame({"d": [datetime.date(2022, 1, 2), datetime.date(2022, 1, 25)], "v": [1, 2]})
    assert asof_d(wide, far, tolerance="1w")["v"].to_list() == [1, 2]
    assert asof_d(wide, far, tolerance="2d")["v"].to_list() == [1, None]


@pytest.mark.parametrize("bad", [True, [1], -2])
def test_asof_a_tolerance_that_is_not_a_duration_text_or_a_positive_number_is_refused(bad):
    with pytest.raises(TransformationError):
        asof(tolerance=bad)


def test_asof_a_number_tolerance_for_a_number_key_equals_polars():
    assert_frame_equal(asof(tolerance=1), polars_asof(strategy="backward", tolerance=1))
