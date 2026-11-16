"""The build refuses the anti-join of a table with itself on the same key (D-0078, D-0050).

Before, the step ran and the join gave an empty table (4 rows in, 0 out) without a message; the user saw an empty plot.
The rule is `utils.join_keys.anti_join_with_itself`, the same one the checker asks (J15). Every other join of a table
with itself still runs as written (D-0066).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_anti_join_with_itself_build.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.data_assembler import DataAssembler
from utils.action_names import JOIN
from utils.errors import TransformationError

TABLE = {"k": [1, 2, 2, 3], "x": ["a", "b", "c", "d"]}


def assemble(steps, other=None):
    tables = {"A": pl.LazyFrame(TABLE), "B": pl.LazyFrame({"k": [1, 3], "y": [10, 30]})}
    return DataAssembler(tables, recipe_id="demo", join_id="J").assemble(steps)


def step(right="A", how="anti", **keys):
    return {"action": JOIN, "right_ingredient": right, "how": how, "maintain_order": "left_right", **({"on": ["k"]} if not keys else keys)}


def test_the_anti_join_of_the_base_table_with_itself_is_refused_with_what_happens_and_a_suggestion():
    with pytest.raises(TransformationError) as refused:
        assemble([step()])
    error = refused.value
    assert "'A'" in str(error) and "['k']" in str(error) and "no row" in str(error)
    assert error.tip.startswith("Suggestion:") and error.tip.count("Suggestion:") == 2


def test_it_is_refused_after_a_join_of_another_table_too():
    with pytest.raises(TransformationError, match="with itself"):
        assemble([step(right="B", how="left"), step()])


def test_the_same_key_written_as_left_on_and_right_on_is_refused_too():
    with pytest.raises(TransformationError, match="with itself"):
        assemble([step(left_on=["k"], right_on=["k"])])


@pytest.mark.parametrize("how", ["left", "inner", "semi"])
def test_every_other_self_join_still_runs_as_written(how):
    result = assemble([step(how=how)]).collect()
    assert result.height >= 4  # left, inner, semi: no row is lost and none is refused


def test_a_self_join_on_other_keys_runs():
    tables = {"A": pl.LazyFrame({"id": [1, 2], "parent": [None, 1]})}
    result = DataAssembler(tables, recipe_id="demo", join_id="J").assemble(
        [{"action": JOIN, "right_ingredient": "A", "how": "anti", "left_on": ["parent"], "right_on": ["id"], "maintain_order": "left_right"}]).collect()
    assert result.height == 1  # the row with no parent: a real question, not an error


def test_the_anti_join_with_another_table_runs_and_keeps_the_rows_without_a_partner():
    result = assemble([step(right="B")]).collect()
    assert result["k"].to_list() == [2, 2]


def test_the_anti_join_of_a_table_joined_before_runs():
    """A left-joined with B, then anti with B: the rows of A that have no partner in B."""
    result = assemble([step(right="B", how="left"), step(right="B")]).collect()
    assert result["k"].to_list() == [2, 2]
