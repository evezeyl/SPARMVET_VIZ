"""The as-of join and the predicate join as the assembler runs them (ADR-102: a join keeps the types the tables have).

`polars_join_asof` has key columns: the assembler checks them before the action runs, as it does for `polars_join`
(equal key lists, key columns that exist, equal types), for the as-of key and for the `by` columns, and names the
recipe, the join and the step. An unsorted table fails in the action itself and the assembler lets that message through.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_polars_time_joins_assembler.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.data_assembler import DataAssembler
from utils.action_names import JOIN_ASOF
from utils.errors import TransformationError

RECIPE = "demo_recipe"
JOIN_ID = "Joined"


def _left():
    return pl.LazyFrame({"t": [1, 2, 4], "g": ["a", "b", "a"], "x": [1, 2, 3]})


def _right():
    return pl.LazyFrame({"t": [0, 3], "g": ["b", "a"], "v": [10, 20]})


def _step(**keys):
    return {"action": JOIN_ASOF, "right_ingredient": "R", "strategy": "backward", **keys}


def _assemble(left, right, steps):
    return DataAssembler({"L": left, "R": right}, recipe_id=RECIPE, join_id=JOIN_ID).assemble(steps)


def test_an_asof_join_runs_through_the_assembler_and_keeps_the_types():
    out = _assemble(_left(), _right(), [_step(on="t", by=["g"])]).collect()
    assert out.columns == ["t", "g", "x", "v"] and out["v"].to_list() == [None, 10, 20] and out.schema["t"] == pl.Int64


def test_the_asof_key_of_two_types_fails_and_names_everything():
    right = _right().with_columns(pl.col("t").cast(pl.Float64))
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(), right, [_step(on="t")]).collect()
    text = f"{caught.value} {caught.value.tip}"
    for part in (RECIPE, JOIN_ID, "step 0", "'t'", "Int64", "Float64", "'R'", "input_fields", JOIN_ASOF):
        assert part in text, f"{part!r} is not in: {text}"


def test_the_by_columns_of_two_types_fail_and_name_the_column():
    right = _right().with_columns(pl.col("g").cast(pl.Categorical))
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(), right, [_step(on="t", by=["g"])]).collect()
    assert "'g'" in str(caught.value) and "String" in str(caught.value) and "Categorical" in str(caught.value)


def test_the_by_columns_of_unequal_length_fail_with_the_names_of_the_parameters():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(), _right(), [_step(on="t", by_left=["g", "x"], by_right=["g"])]).collect()
    assert "by_left has 2 column(s)" in str(caught.value) and "by_right has 1 column(s)" in str(caught.value) and "'by'" in caught.value.tip


def test_a_by_column_that_does_not_exist_fails_in_the_check_with_a_plain_message():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(), _right(), [_step(on="t", by=["nope"])]).collect()
    assert "does not exist" in str(caught.value) and "['nope']" in str(caught.value) and RECIPE in str(caught.value)


def test_left_on_with_right_on_of_different_names_are_checked_and_work():
    right = _right().rename({"t": "t2"})
    out = _assemble(_left(), right, [_step(left_on="t", right_on="t2", by=["g"])]).collect()
    assert out["v"].to_list() == [None, 10, 20]
    with pytest.raises(TransformationError, match="'nope'"):
        _assemble(_left(), right, [_step(left_on="t", right_on="nope")]).collect()


def test_an_asof_step_without_any_key_fails_before_the_action_runs():
    with pytest.raises(TransformationError, match="Join key missing"):
        _assemble(_left(), _right(), [_step()]).collect()


def test_an_ingredient_that_does_not_exist_fails_with_the_available_ones():
    with pytest.raises(TransformationError, match="Ingredient 'R' required"):
        DataAssembler({"L": _left()}, recipe_id=RECIPE, join_id=JOIN_ID).assemble([_step(on="t")])


def test_an_unsorted_table_fails_through_the_assembler_with_the_message_of_the_action():
    unsorted = pl.LazyFrame({"t": [4, 1], "g": ["a", "a"], "x": [1, 2]})
    with pytest.raises(TransformationError, match="not sorted ascending"):
        _assemble(unsorted, _right(), [_step(on="t", by=["g"])]).collect()


def test_the_second_asof_step_is_checked_against_the_result_of_the_first():
    """The left table of a step is the table at that step: a column brought by the first join is a key of the second."""
    third = pl.LazyFrame({"v": [5, 15], "w": [1, 2]})
    steps = [_step(on="t", by=["g"]), {"action": JOIN_ASOF, "right_ingredient": "T", "strategy": "backward", "on": "v"}]
    # v is unsorted after the first join (null, 10, 20 is sorted with null first): the second join works
    out = DataAssembler({"L": _left(), "R": _right(), "T": third}, recipe_id=RECIPE, join_id=JOIN_ID).assemble(steps).collect()
    assert out["w"].to_list() == [None, 1, 2]


# -- modif_join_where --------------------------------------------------------------------------------

from utils.action_names import JOIN_WHERE  # noqa: E402


def _where_step(**more):
    return {"action": JOIN_WHERE, "right_ingredient": "R", "predicates": ["pl.col('v') >= pl.col('t')"], **more}


def test_a_join_on_conditions_runs_through_the_assembler_without_any_key():
    out = _assemble(_left(), _right(), [_where_step()]).collect()
    assert out.columns == ["t", "g", "x", "t_right", "g_right", "v"] and out.height == 6   # every t is below the 10 and 20 of v
    assert out["x"].to_list() == [1, 1, 2, 2, 3, 3]                                          # the order: first table, then second


def test_a_join_on_conditions_with_numbers_of_different_types_fails_through_the_assembler_with_a_plain_message():
    right = _right().with_columns(pl.col("v").cast(pl.Float64))
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(), right, [_where_step(predicates=["pl.col('v') >= pl.col('x')"])]).collect()
    assert "cannot compare" in str(caught.value) and "modif_join_where" in str(caught.value) and "input_fields" in caught.value.tip


def test_a_refused_step_keeps_its_own_plain_message_through_the_assembler():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(), _right(), [_where_step(predicates=[])]).collect()
    assert "predicates is empty" in str(caught.value) and "one or more formulas" in str(caught.value) and RECIPE in str(caught.value.pipeline_error.location)
