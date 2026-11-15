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


# =========================================================================================================
# modif_join_where
# =========================================================================================================

import random  # noqa: E402

W_LEFT = pl.DataFrame({"id": ["a", "b", "c", "d"], "lo": [1, 5, None, 3], "hi": [4, 9, 3, 8]})
W_RIGHT = pl.DataFrame({"rid": ["x", "y", "z", "w"], "v": [2, 5, 10, 4]})
BETWEEN = ["pl.col('v') >= pl.col('lo')", "pl.col('v') <= pl.col('hi')"]


def where(left=W_LEFT, right=W_RIGHT, predicates=BETWEEN, **more):
    return run("modif_join_where", left, {"right_ingredient": "R", "predicates": predicates, "__right_df__": right.lazy(), **more})


def pairs_in_the_order_of_the_tables(left, right, keep):
    """The matching pairs in the order of the first table, then of the second: a cross join and a filter, no join_where."""
    crossed = left.lazy().with_row_index("_l").join(right.lazy().with_row_index("_r"), how="cross").filter(keep)
    return crossed.sort(["_l", "_r"]).drop(["_l", "_r"]).collect()


def test_where_the_pairs_come_in_the_order_of_the_first_table_then_of_the_second():
    out = where()
    expected = pairs_in_the_order_of_the_tables(W_LEFT, W_RIGHT, (pl.col("v") >= pl.col("lo")) & (pl.col("v") <= pl.col("hi")))
    assert_frame_equal(out, expected)
    assert out["id"].to_list() == ["a", "a", "b", "d", "d"] and out["rid"].to_list() == ["x", "w", "y", "y", "w"]
    # the order follows the rows as they are, not their values: the same rows reversed come in the reversed order of the first table
    reversed_out = where(W_LEFT.reverse())
    assert reversed_out["id"].to_list() == ["d", "d", "b", "a", "a"]


def test_where_the_order_is_the_same_on_every_run_on_tables_where_polars_is_not():
    rng = random.Random(0)
    size = 2500
    left = pl.DataFrame({"i": list(range(size)), "a": [rng.randint(0, 100) for _ in range(size)]})
    right = pl.DataFrame({"j": list(range(size)), "b": [rng.randint(0, 100) for _ in range(size)]})
    predicates = ["pl.col('a') < pl.col('b')", "pl.col('a') > pl.col('b') - 5"]
    expected = pairs_in_the_order_of_the_tables(left, right, (pl.col("a") < pl.col("b")) & (pl.col("a") > pl.col("b") - 5))
    for _ in range(5):
        assert where(left, right, predicates).equals(expected)
    polars_runs = [left.lazy().join_where(right.lazy(), pl.col("a") < pl.col("b"), pl.col("a") > pl.col("b") - 5).collect() for _ in range(12)]
    if all(run_.equals(polars_runs[0]) for run_ in polars_runs):
        pytest.skip("Polars gave the same order in 12 runs on this machine; the reason for the fixed order could not be shown here")
    assert any(not run_.equals(polars_runs[0]) for run_ in polars_runs), "Polars changes the order of the pairs from run to run"


def test_where_a_null_in_a_compared_column_does_not_match_and_a_nan_is_larger_than_every_number():
    assert where()["id"].to_list().count("c") == 0       # lo is null for c: its predicates are null, not true
    left = pl.DataFrame({"lo": [1.0], "hi": [9.0]})
    right = pl.DataFrame({"v": [2.0, NAN]})
    assert where(left, right, ["pl.col('v') >= pl.col('lo')"])["v"].to_list()[1] != 2.0  # NaN >= 1 is true
    assert where(left, right, ["pl.col('v') >= pl.col('lo')"]).height == 2
    assert where(left, right, ["pl.col('v') <= pl.col('hi')"]).height == 1   # NaN <= 9 is false


def test_where_numbers_of_different_types_cannot_be_compared_and_the_step_fails_with_a_plain_message():
    mixed = W_RIGHT.with_columns(pl.col("v").cast(pl.Float64))
    with pytest.raises(pl.exceptions.SchemaError, match="cannot compare"):  # what Polars does
        W_LEFT.lazy().join_where(mixed.lazy(), pl.col("v") >= pl.col("lo")).collect()
    with pytest.raises(TransformationError, match="cannot compare Float64 with Int64") as caught:
        where(W_LEFT, mixed)
    assert "polars_cast" in caught.value.tip and "input_fields" in caught.value.tip


def test_where_a_column_in_both_tables_is_written_with_the_suffix_and_the_suffix_can_be_changed():
    right = W_RIGHT.with_columns(lo=pl.lit(0, dtype=pl.Int64))
    default = where(W_LEFT, right, ["pl.col('v') >= pl.col('lo_right')"])
    assert "lo_right" in default.columns
    named = where(W_LEFT, right, ["pl.col('v') >= pl.col('lo_x')"], suffix="_x")
    assert "lo_x" in named.columns and "lo_right" not in named.columns


def test_where_the_predicates_are_required_and_a_list_of_formula_texts():
    with pytest.raises(TransformationError, match="predicates is required"):
        run("modif_join_where", W_LEFT, {"right_ingredient": "R", "__right_df__": W_RIGHT.lazy()})
    with pytest.raises(TransformationError, match="predicates is empty"):
        where(predicates=[])
    with pytest.raises(TransformationError, match="one or more formulas"):
        where(predicates=[5])
    with pytest.raises(TransformationError, match="takes a list|wrong form"):
        where(predicates="pl.col('v') > 1")


def test_where_a_predicate_goes_through_the_formula_check():
    for formula in ("__import__('os').system('echo hacked')", "pl.read_csv('/etc/passwd')", "pl.col('v').map_elements(lambda x: x)"):
        with pytest.raises(TransformationError, match="refused"):
            where(predicates=[formula])


def test_where_a_join_on_conditions_has_no_key_columns():
    with pytest.raises(TransformationError, match="'on' is not a parameter|on is not a parameter"):
        where(**{"on": "id"})


def test_where_the_helper_columns_never_collide_with_a_column_of_the_tables():
    left = W_LEFT.with_columns(__row_of_first_table__=pl.lit("mine"))
    out = where(left)
    assert out.columns == left.columns + ["rid", "v"] and out["__row_of_first_table__"].to_list() == ["mine"] * out.height


def test_where_a_predicate_about_one_table_only_equals_polars():
    out = where(predicates=["pl.col('lo') > 1"])
    expected = W_LEFT.lazy().join_where(W_RIGHT.lazy(), pl.col("lo") > 1).collect()
    assert_frame_equal(out.sort(out.columns), expected.sort(expected.columns))


def test_where_an_empty_first_table_gives_an_empty_table_with_the_columns_of_polars():
    out = where(W_LEFT.head(0))
    polars_out = W_LEFT.head(0).lazy().join_where(W_RIGHT.lazy(), *[pl.col("v") >= pl.col("lo"), pl.col("v") <= pl.col("hi")]).collect()
    assert out.height == 0 and out.schema == polars_out.schema


def test_where_the_second_table_is_required():
    with pytest.raises(TransformationError, match="__right_df__"):
        run("modif_join_where", W_LEFT, {"right_ingredient": "R", "predicates": BETWEEN})


# =========================================================================================================
# windows over a sorted index: polars_group_by_dynamic (the helpers are shared with polars_rolling)
# =========================================================================================================

D = datetime.date
TIMED = pl.DataFrame({
    "i": [1, 2, 3, 4, 5, 6], "g": [None, "b", "a", None, "b", "a"], "x": [1.0, None, NAN, 4.0, 5.0, 6.0], "d": [D(2022, 1, d) for d in (1, 2, 8, 9, 15, 16)],
})


def dynamic(frame=TIMED, **more):
    spec = {"index_column": "i", "every": "3i", "closed": "left", "named_aggs": {"n": "pl.len()"}, **more}
    return run("polars_group_by_dynamic", frame, spec)


def polars_dynamic(frame=TIMED, every="3i", **more):
    return frame.lazy().group_by_dynamic("i", every=every, closed="left", **more).agg(n=pl.len()).collect()


def test_dynamic_the_index_not_sorted_fails_with_a_plain_message_and_polars_fails_too():
    unsorted = pl.DataFrame({"i": [3, 1, 2], "x": [1, 2, 3]})
    with pytest.raises(pl.exceptions.InvalidOperationError, match="not sorted"):
        unsorted.lazy().group_by_dynamic("i", every="3i").agg(n=pl.len()).collect()
    with pytest.raises(TransformationError) as caught:
        dynamic(unsorted)
    assert "'i' is not sorted ascending" in str(caught.value) and "polars_sort" in caught.value.tip and "maintain_order" in caught.value.tip


def test_dynamic_the_index_not_sorted_within_a_group_fails_even_in_a_later_group():
    unsorted_in_b = pl.DataFrame({"i": [1, 2, 5, 4], "g": ["a", "a", "b", "b"]})
    with pytest.raises(pl.exceptions.ComputeError, match="not sorted"):
        unsorted_in_b.lazy().group_by_dynamic("i", every="3i", group_by="g").agg(n=pl.len()).collect()
    with pytest.raises(TransformationError, match=r"not sorted ascending within each group of \['g'\]"):
        dynamic(unsorted_in_b, group_by=["g"])


def test_dynamic_sorted_within_each_group_but_not_over_the_whole_table_works_with_group_by_and_fails_without():
    frame = pl.DataFrame({"i": [9, 1, 10, 2], "g": ["z", "a", "z", "a"]})
    assert_frame_equal(dynamic(frame, group_by=["g"]), polars_dynamic(frame, group_by=["g"]))
    with pytest.raises(TransformationError, match="not sorted ascending"):
        dynamic(frame)


def test_dynamic_a_null_in_the_index_is_refused_and_polars_refuses_it_too():
    with_null = pl.DataFrame({"i": [None, 1, 2]})
    with pytest.raises(pl.exceptions.ComputeError, match="null values"):
        with_null.lazy().group_by_dynamic("i", every="3i").agg(n=pl.len()).collect()
    with pytest.raises(TransformationError, match="holds null values") as caught:
        dynamic(with_null)
    assert "polars_drop_nulls" in caught.value.tip


def test_dynamic_the_types_and_the_durations_must_fit_and_say_so_plainly():
    with pytest.raises(TransformationError, match="windows need a date, a time or a whole number"):
        dynamic(pl.DataFrame({"i": [1.0, 2.0]}))
    with pytest.raises(TransformationError, match="windows need a date, a time or a whole number"):
        dynamic(pl.DataFrame({"i": ["a", "b"]}))
    with pytest.raises(TransformationError, match="windows need"):
        dynamic(pl.DataFrame({"i": pl.Series([1, 2], dtype=pl.Int16)}))
    with pytest.raises(TransformationError, match="'1w' is a time duration but the index column 'i' is Int64"):
        dynamic(every="1w")
    with pytest.raises(TransformationError, match="'3i' counts whole numbers but the index column 'd' is Date"):
        dynamic(index_column="d", every="3i")
    with pytest.raises(TransformationError, match="offset '1w'"):
        dynamic(offset="1w")
    with pytest.raises(TransformationError, match="every 3 is not a duration text"):
        dynamic(every=3)


def test_dynamic_a_duration_that_is_not_a_duration_is_a_plain_message():
    with pytest.raises(TransformationError, match="duration"):
        dynamic(index_column="d", every="week")


def test_dynamic_a_missing_column_is_named_in_the_index_the_groups_and_the_formulas():
    with pytest.raises(TransformationError, match="'nope' is not in the table"):
        dynamic(index_column="nope")
    with pytest.raises(TransformationError, match="'nope' is not in the table"):
        dynamic(group_by=["nope"])
    with pytest.raises(TransformationError, match="nope"):
        dynamic(named_aggs={"s": "pl.col('nope').sum()"})


def test_dynamic_a_formula_goes_through_the_formula_check():
    with pytest.raises(TransformationError, match="refused"):
        dynamic(named_aggs={"s": "__import__('os').system('echo hacked')"})
    with pytest.raises(TransformationError, match="refused"):
        dynamic(named_aggs={"s": "pl.col('x').map_elements(lambda v: v)"})


def test_dynamic_closed_is_required_and_must_be_one_of_the_four():
    with pytest.raises(TransformationError, match="closed is required"):
        run("polars_group_by_dynamic", TIMED, {"index_column": "i", "every": "3i", "named_aggs": {"n": "pl.len()"}})
    with pytest.raises(TransformationError, match="left, right, both, none"):
        dynamic(closed="middle")


def test_dynamic_closed_changes_the_windows_so_it_cannot_be_left_to_a_default():
    frame = pl.DataFrame({"i": [1, 2, 3]})
    left = dynamic(frame, closed="left")["n"].to_list()
    right = dynamic(frame, closed="right")["n"].to_list()
    assert left == [2, 1] and right != left


def test_dynamic_the_groups_come_in_ascending_order_nulls_last_and_the_same_on_every_run():
    out = dynamic(group_by=["g"])
    assert out["g"].to_list() == ["a", "a", "b", "b", None, None]
    assert all(dynamic(group_by=["g"]).equals(out) for _ in range(8))
    two = dynamic(TIMED.with_columns(h=pl.Series([2, 1, 1, 2, 1, 1])), group_by=["h", "g"])
    assert two["h"].to_list() == sorted(two["h"].to_list())


def test_dynamic_the_order_holds_on_a_larger_table_with_many_groups():
    rng = random.Random(3)
    size = 20000
    rows = sorted((rng.randint(0, 100000), rng.choice("zyxwvutsrq")) for _ in range(size))
    frame = pl.DataFrame({"i": [r[0] for r in rows], "g": [r[1] for r in rows]})
    first = dynamic(frame, every="500i", group_by=["g"])
    assert first["g"].to_list() == sorted(first["g"].to_list())
    assert all(dynamic(frame, every="500i", group_by=["g"]).equals(first) for _ in range(5))


def test_dynamic_what_a_null_and_a_nan_do_in_a_window_follows_the_formula():
    out = dynamic(group_by=["g"], named_aggs={"s": "pl.col('x').sum()", "m": "pl.col('x').mean()", "c": "pl.col('x').count()", "n": "pl.len()"})
    by = {(r["g"], r["i"]): r for r in out.to_dicts()}
    assert by[("b", 0)]["s"] == 0.0 and by[("b", 0)]["m"] is None and by[("b", 0)]["c"] == 0 and by[("b", 0)]["n"] == 1   # only a null: the sum is 0
    assert by[("a", 3)]["s"] != by[("a", 3)]["s"] and by[("a", 3)]["c"] == 1                                              # a NaN: the sum is NaN, count counts it
    assert_frame_equal(out, TIMED.lazy().group_by_dynamic("i", every="3i", closed="left", group_by=["g"]).agg(
        s=pl.col("x").sum(), m=pl.col("x").mean(), c=pl.col("x").count(), n=pl.len()).collect())


def test_dynamic_an_empty_table_gives_an_empty_table():
    empty = pl.DataFrame({"i": [], "x": []}, schema={"i": pl.Int64, "x": pl.Float64})
    out = dynamic(empty, named_aggs={"s": "pl.col('x').sum()"})
    assert out.height == 0 and out.columns == ["i", "s"]


def test_dynamic_a_step_cannot_write_the_aggregations_as_a_list_or_a_key_that_is_not_a_parameter():
    with pytest.raises(TransformationError):
        dynamic(named_aggs=["pl.len()"])
    with pytest.raises(TransformationError, match="maintain_order"):
        dynamic(maintain_order=True)


# =========================================================================================================
# polars_rolling
# =========================================================================================================

def rolling(frame=TIMED, **more):
    spec = {"index_column": "i", "period": "3i", "closed": "right", "named_aggs": {"n": "pl.len()"}, **more}
    return run("polars_rolling", frame, spec)


def polars_rolling(frame=TIMED, period="3i", **more):
    return frame.lazy().rolling("i", period=period, closed="right", **more).agg(n=pl.len()).collect()


def test_rolling_gives_one_row_per_row_and_keeps_the_order_without_group_by():
    out = rolling()
    assert out.height == TIMED.height and out["i"].to_list() == TIMED["i"].to_list()
    assert out.columns == ["i", "n"]
    assert_frame_equal(out, polars_rolling())


def test_rolling_the_window_reaches_back_by_the_period_and_closed_decides_the_edges():
    frame = pl.DataFrame({"i": [1, 2, 3, 4, 5]})
    assert rolling(frame, closed="right")["n"].to_list() == [1, 2, 3, 3, 3]    # (i - 3, i]
    assert rolling(frame, closed="left")["n"].to_list() == [0, 1, 2, 3, 3]     # [i - 3, i): the row itself is not in it
    assert rolling(frame, closed="both")["n"].to_list() == [1, 2, 3, 4, 4]
    assert rolling(frame, closed="none")["n"].to_list() == [0, 1, 2, 2, 2]


def test_rolling_with_group_by_the_rows_come_grouped_in_ascending_order_nulls_last_and_the_same_on_every_run():
    out = rolling(group_by=["g"])
    assert out["g"].to_list() == ["a", "a", "b", "b", None, None] and out.height == TIMED.height
    assert out.filter(pl.col("g") == "a")["i"].to_list() == [3, 6]
    assert all(rolling(group_by=["g"]).equals(out) for _ in range(8))
    assert_frame_equal(out, polars_rolling(group_by=["g"]))


def test_rolling_the_order_holds_on_a_larger_table_with_many_groups():
    rng = random.Random(5)
    size = 20000
    rows = sorted((rng.randint(0, 100000), rng.choice("zyxwvutsrq")) for _ in range(size))
    frame = pl.DataFrame({"i": [r[0] for r in rows], "g": [r[1] for r in rows]})
    first = rolling(frame, period="500i", group_by=["g"])
    assert first.height == size and first["g"].to_list() == sorted(first["g"].to_list())
    assert all(rolling(frame, period="500i", group_by=["g"]).equals(first) for _ in range(5))


def test_rolling_the_index_not_sorted_fails_with_a_plain_message_and_polars_fails_too():
    unsorted = pl.DataFrame({"i": [3, 1, 2], "x": [1, 2, 3]})
    with pytest.raises(pl.exceptions.InvalidOperationError, match="not sorted"):
        unsorted.lazy().rolling("i", period="3i").agg(n=pl.len()).collect()
    with pytest.raises(TransformationError) as caught:
        rolling(unsorted)
    assert "'i' is not sorted ascending" in str(caught.value) and "polars_sort" in caught.value.tip
    in_b = pl.DataFrame({"i": [1, 2, 5, 4], "g": ["a", "a", "b", "b"]})
    with pytest.raises(TransformationError, match=r"within each group of \['g'\]"):
        rolling(in_b, group_by=["g"])


def test_rolling_sorted_within_each_group_but_not_over_the_whole_table_works_with_group_by_and_fails_without():
    frame = pl.DataFrame({"i": [9, 1, 10, 2], "g": ["z", "a", "z", "a"]})
    assert_frame_equal(rolling(frame, group_by=["g"]), polars_rolling(frame, group_by=["g"]))
    with pytest.raises(TransformationError, match="not sorted ascending"):
        rolling(frame)


def test_rolling_a_null_in_the_index_is_refused_and_polars_refuses_it_too():
    with_null = pl.DataFrame({"i": [None, 1, 2]})
    with pytest.raises(pl.exceptions.ComputeError, match="null values"):
        with_null.lazy().rolling("i", period="3i").agg(n=pl.len()).collect()
    with pytest.raises(TransformationError, match="holds null values"):
        rolling(with_null)


def test_rolling_the_types_and_the_durations_must_fit_and_say_so_plainly():
    with pytest.raises(TransformationError, match="windows need a date, a time or a whole number"):
        rolling(pl.DataFrame({"i": [1.0, 2.0]}))
    with pytest.raises(TransformationError, match="'3d' is a time duration but the index column 'i' is Int64"):
        rolling(period="3d")
    with pytest.raises(TransformationError, match="'3i' counts whole numbers but the index column 'd' is Date"):
        rolling(index_column="d")
    with pytest.raises(TransformationError, match="period 3 is not a duration text"):
        rolling(period=3)


def test_rolling_closed_and_period_are_required_and_closed_is_one_of_the_four():
    with pytest.raises(TransformationError, match="closed is required"):
        run("polars_rolling", TIMED, {"index_column": "i", "period": "3i", "named_aggs": {"n": "pl.len()"}})
    with pytest.raises(TransformationError, match="period is required"):
        run("polars_rolling", TIMED, {"index_column": "i", "closed": "right", "named_aggs": {"n": "pl.len()"}})
    with pytest.raises(TransformationError, match="left, right, both, none"):
        rolling(closed="middle")


def test_rolling_a_missing_column_and_an_unsafe_formula_are_refused_with_a_plain_message():
    with pytest.raises(TransformationError, match="'nope' is not in the table"):
        rolling(index_column="nope")
    with pytest.raises(TransformationError, match="nope"):
        rolling(named_aggs={"s": "pl.col('nope').sum()"})
    with pytest.raises(TransformationError, match="refused"):
        rolling(named_aggs={"s": "pl.read_csv('/etc/passwd')"})


def test_rolling_what_a_null_and_a_nan_do_in_a_window_follows_the_formula():
    out = rolling(named_aggs={"s": "pl.col('x').sum()", "m": "pl.col('x').mean()", "c": "pl.col('x').count()", "n": "pl.len()"}, period="2i")
    by = {row["i"]: row for row in out.to_dicts()}
    assert by[1]["s"] == 1.0 and by[2]["s"] == 1.0 and by[2]["c"] == 1 and by[2]["n"] == 2          # the null is skipped by sum and count, not by len
    assert by[3]["s"] != by[3]["s"] and by[3]["c"] == 1                                              # the NaN makes the sum NaN
    only_null = rolling(pl.DataFrame({"i": [1, 2], "x": [None, None]}, schema={"i": pl.Int64, "x": pl.Float64}), period="2i",
                        named_aggs={"s": "pl.col('x').sum()"})
    assert only_null["s"].to_list() == [0.0, 0.0]                                                    # a window with only nulls sums to 0
    assert_frame_equal(out, TIMED.lazy().rolling("i", period="2i", closed="right").agg(
        s=pl.col("x").sum(), m=pl.col("x").mean(), c=pl.col("x").count(), n=pl.len()).collect())


def test_rolling_an_empty_table_gives_an_empty_table():
    empty = pl.DataFrame({"i": [], "x": []}, schema={"i": pl.Int64, "x": pl.Float64})
    out = rolling(empty, named_aggs={"s": "pl.col('x').sum()"})
    assert out.height == 0 and out.columns == ["i", "s"]
