"""The step_top_n_other action (the old top_n_other): keep the N most frequent values, label the rest (issue #23).

Several cases follow the tests of the R function it mirrors (NorwegianVeterinaryInstitute/
2025_PAWH_APEC1, tests/testthat/test-top_n_other.R).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_top_n_other.py -q
"""
import random

import polars as pl
import pytest

from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from utils.errors import TransformationError

action_top_n_other = AVAILABLE_WRANGLING_ACTIONS["step_top_n_other"]


def full(spec):
    """The step as format 1 requires it: the label and the new column are written (they used to default)."""
    return {"other_label": "Other", "new_column": f"v_top{spec.get('n')}", **spec}


def run(values, spec, **extra):
    frame = pl.DataFrame({"v": values, **extra}).lazy()
    return action_top_n_other(frame, {"column": "v", **full(spec)}).collect()


def test_keeps_the_n_most_frequent_and_labels_the_rest():
    out = run(["a", "a", "a", "b", "b", "c", "d"], {"n": 2})
    assert out.columns == ["v", "v_top2"]
    assert out["v_top2"].to_list() == ["a", "a", "a", "b", "b", "Other", "Other"]


def test_ties_are_broken_alphabetically():
    # b, c and d each occur twice: the first two alphabetically (b, c) are kept
    out = run(["d", "d", "c", "c", "b", "b", "a"], {"n": 2})
    assert out["v_top2"].to_list() == ["Other", "Other", "c", "c", "b", "b", "Other"]


def test_the_same_data_gives_the_same_result_whatever_the_row_order():
    rng = random.Random(3)
    values = [rng.choice("abcdefgh") for _ in range(500)]
    shuffled = values[:]
    rng.shuffle(shuffled)
    kept = lambda vs: sorted(set(run(vs, {"n": 3})["v_top3"].to_list()) - {"Other"})
    assert kept(values) == kept(shuffled)


def test_rows_keep_their_order_and_nothing_is_lost():
    values = ["x", "y", "x", "z", "y", "x"]
    out = run(values, {"n": 1}, row_id=list(range(6)))
    assert out["row_id"].to_list() == list(range(6))
    assert out["v"].to_list() == values


def test_nulls_stay_null_and_take_no_place_in_the_top():
    out = run(["a", None, None, None, "b", "b"], {"n": 1})
    assert out["v_top1"].to_list() == ["Other", None, None, None, "b", "b"]


def test_a_custom_label_and_overwriting_the_same_column():
    out = run(["a", "a", "b", "c"], {"n": 1, "other_label": "Rest", "new_column": "v"})
    assert out.columns == ["v"]
    assert out["v"].to_list() == ["a", "a", "Rest", "Rest"]


def test_count_distinct_ranks_by_different_samples_not_rows():
    # "a" has 4 rows but 1 sample; "b" and "c" have 2 samples each
    out = run(["a", "a", "a", "a", "b", "b", "c", "c"], {"n": 2, "count_distinct": "s"},
              s=["s1", "s1", "s1", "s1", "s2", "s3", "s4", "s5"])
    assert out["v_top2"].to_list() == ["Other"] * 4 + ["b", "b", "c", "c"]


def test_works_on_a_categorical_column():
    frame = pl.DataFrame({"v": ["a", "a", "b", "c"]}).with_columns(pl.col("v").cast(pl.Categorical)).lazy()
    out = action_top_n_other(frame, {"column": "v", **full({"n": 1})}).collect()
    assert out["v_top1"].to_list() == ["a", "a", "Other", "Other"]


def test_every_value_is_kept_when_there_are_fewer_distinct_values_than_n():
    values = ["a", "b", "b", "c"]
    assert run(values, {"n": 10})["v_top10"].to_list() == values


def test_a_null_outside_the_top_n_is_still_null_not_the_label():
    out = run(["a", "a", "a", "b", "b", "c", None], {"n": 1})
    assert out["v_top1"].to_list() == ["a", "a", "a", "Other", "Other", "Other", None]


def test_a_two_way_tie_for_n_1_keeps_exactly_one_value():
    out = run(["a", "b"], {"n": 1})
    assert sorted(out["v_top1"].to_list()) == ["Other", "a"]   # the alphabetically first value is kept


def test_the_output_is_text_with_the_same_length_as_the_input():
    out = run(["a", "a", "b", "c", "c", "c"], {"n": 1})
    assert out["v_top1"].dtype == pl.String and out.height == 6


@pytest.mark.parametrize("spec", [{"n": 2}, {"column": "v"}, {"column": "v", "n": 0}, {"column": "v", "n": "3"}])
def test_bad_parameters_are_reported(spec):
    spec = {"other_label": "Other", "new_column": "t", **spec}
    with pytest.raises(TransformationError):
        action_top_n_other(pl.DataFrame({"v": ["a"]}).lazy(), spec)


@pytest.mark.parametrize("missing", ["other_label", "new_column"])
def test_the_label_and_the_new_column_are_written_not_defaulted(missing):
    spec = {"column": "v", "n": 1, "other_label": "Other", "new_column": "t"}
    del spec[missing]
    with pytest.raises(TransformationError, match=missing):
        action_top_n_other(pl.DataFrame({"v": ["a"]}).lazy(), spec)
