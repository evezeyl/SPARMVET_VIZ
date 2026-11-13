"""The step_ actions equal the old actions they replace, and refuse what the old ones swallowed (W6, R7).

For every valid input the new action gives the same table as the old one (differential test, until the old action is
removed by the migration series; the expectations are then frozen in `EXPECTED`). Where the old one was silent (an unknown
aggregation counted, a missing column returned the table unchanged, a missing parameter defaulted), the new one fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_step_actions.py -q
"""
import polars as pl
import pytest
from polars.testing import assert_frame_equal

import transformer.actions  # noqa: F401
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS as A
from utils.errors import TransformationError

DATA = pl.DataFrame({
    "g": ["x", "x", "y", "y", "y", None],
    "v": [1, 2, 3, 4, 5, 6],
    "w": [1.5, None, 2.5, 3.5, 4.5, 5.5],
    "path": ["a_b_c", "d_e", "f", None, "g_h_i_j", "k"],
    "sp": ["Escherichia/coli", "Klebsiella/pneumoniae/extra", "Salmonella", None, "A/B", "C/D"],
})


def run(name, spec, frame=DATA):
    return A[name](frame.lazy(), spec).collect()


# -- step_summarize ---------------------------------------------------------------------------

@pytest.mark.parametrize("agg", ["count", "sum", "mean"])
def test_summarize_equals_the_old_action(agg):
    new = run("step_summarize", {"group_by": ["g"], "columns": ["v", "w"], "agg": agg})
    old = run("summarize", {"group_by": ["g"], "columns": ["v", "w"], "agg": agg})
    assert_frame_equal(new, old)


def test_summarize_new_name_and_whole_table_equal_the_old_action():
    assert_frame_equal(run("step_summarize", {"group_by": ["g"], "columns": ["v"], "agg": "sum", "new_name": "total"}),
                       run("summarize", {"group_by": ["g"], "columns": ["v"], "agg": "sum", "new_name": "total"}))
    assert_frame_equal(run("step_summarize", {"group_by": [], "columns": ["v"], "agg": "sum"}),
                       run("summarize", {"group_by": [], "columns": ["v"], "agg": "sum"}))


@pytest.mark.parametrize("spec", [
    {"group_by": ["g"], "columns": ["v"]},                                      # agg is written, not defaulted
    {"group_by": ["g"], "columns": ["v"], "agg": "median"},                     # unknown aggregation: the old one counted
    {"group_by": ["g"], "columns": ["v", "w"], "agg": "sum", "new_name": "x"},  # a name for two columns
    {"columns": ["v"], "agg": "sum"},
])
def test_summarize_refuses_what_the_old_one_swallowed(spec):
    with pytest.raises(TransformationError):
        run("step_summarize", spec)


# -- step_top_n_other -------------------------------------------------------------------------

def test_top_n_other_equals_the_old_action_including_the_tie_rule():
    frame = pl.DataFrame({"variant": ["b", "a", "b", "a", "c", "d", None, "c"]})     # a, b, c have two each: ties by value
    new = run("step_top_n_other", {"column": "variant", "n": 2, "other_label": "Other", "new_column": "top"}, frame)
    old = run("top_n_other", {"column": "variant", "n": 2, "other_label": "Other", "new_column": "top"}, frame)
    assert_frame_equal(new, old)
    assert new["top"].to_list() == ["b", "a", "b", "a", "Other", "Other", None, "Other"]


def test_top_n_other_count_distinct_equals_the_old_action():
    frame = pl.DataFrame({"variant": ["a", "a", "b", "c"], "sample": ["s1", "s1", "s2", "s3"]})
    spec = {"column": "variant", "n": 1, "other_label": "Rest", "new_column": "t", "count_distinct": "sample"}
    assert_frame_equal(run("step_top_n_other", spec, frame), run("top_n_other", spec, frame))


@pytest.mark.parametrize("spec", [
    {"column": "g", "n": 2, "new_column": "t"},                       # other_label is written, not defaulted
    {"column": "g", "n": 2, "other_label": "O"},                      # new_column is written
    {"column": "g", "n": 0, "other_label": "O", "new_column": "t"},
    {"column": "g", "n": True, "other_label": "O", "new_column": "t"},
])
def test_top_n_other_refuses_a_step_that_hides_a_choice(spec):
    with pytest.raises(TransformationError):
        run("step_top_n_other", spec)


# -- step_split_column ------------------------------------------------------------------------

def test_split_column_equals_the_old_action_the_remainder_in_the_last_column():
    spec = {"columns": ["path"], "new_columns": ["a", "b"], "delimiter": "_"}
    new = run("step_split_column", spec)
    assert_frame_equal(new, run("split_column", spec))
    assert new["b"].to_list() == ["b_c", "e", None, None, "h_i_j", None]


def test_split_column_drop_source_equals_the_old_action():
    spec = {"columns": ["path"], "new_columns": ["a", "b"], "delimiter": "_", "drop_source": True}
    assert_frame_equal(run("step_split_column", spec), run("split_column", spec))


@pytest.mark.parametrize("spec", [
    {"columns": ["path"], "new_columns": ["a", "b"]},                                   # the delimiter is written
    {"columns": ["nope"], "new_columns": ["a", "b"], "delimiter": "_"},                 # the old one returned the table unchanged
    {"columns": ["path", "sp"], "new_columns": ["a", "b"], "delimiter": "_"},
])
def test_split_column_refuses_what_the_old_one_swallowed(spec):
    with pytest.raises(TransformationError):
        run("step_split_column", spec)


# -- step_split_column_to_parts ---------------------------------------------------------------

def test_split_column_to_parts_equals_the_old_action_when_no_part_is_left_over():
    frame = DATA.filter(pl.col("sp").is_null() | ~pl.col("sp").str.contains("extra"))
    new = run("step_split_column_to_parts", {"columns": ["sp"], "separator": "/", "new_columns": ["genus", "species"]}, frame)
    old = run("split_column_to_parts", {"column": "sp", "separator": "/", "new_columns": ["genus", "species"]}, frame)
    assert_frame_equal(new, old)


def test_split_column_to_parts_keeps_the_remainder_that_the_old_action_dropped_silently():
    spec = {"columns": ["sp"], "separator": "/", "new_columns": ["genus", "species"]}
    new = run("step_split_column_to_parts", spec)
    old = run("split_column_to_parts", {"column": "sp", "separator": "/", "new_columns": ["genus", "species"]})
    assert new["species"].to_list()[1] == "pneumoniae/extra"
    assert old["species"].to_list()[1] == "pneumoniae", "the finding: the old action lost 'extra' without a message"


def test_split_column_to_parts_refuses_a_missing_separator_and_two_sources():
    with pytest.raises(TransformationError):
        run("step_split_column_to_parts", {"columns": ["sp"], "new_columns": ["a", "b"]})
    with pytest.raises(TransformationError):
        run("step_split_column_to_parts", {"columns": ["sp", "path"], "separator": "/", "new_columns": ["a", "b"]})


def test_the_registry_says_composite():
    from transformer.actions.base import ACTION_SCHEMAS
    for name in ("step_summarize", "step_top_n_other", "step_split_column", "step_split_column_to_parts"):
        assert ACTION_SCHEMAS[name]["polars"] == "composite"
