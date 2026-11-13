"""step_top_n_other equals the old action it replaces, and refuses what the old one swallowed (W6, R7).

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


def test_the_registry_says_composite():
    from transformer.actions.base import ACTION_SCHEMAS
    assert ACTION_SCHEMAS["step_top_n_other"]["polars"] == "composite"
