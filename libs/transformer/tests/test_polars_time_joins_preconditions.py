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
