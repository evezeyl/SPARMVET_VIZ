"""A join keeps the types the tables have (JOIN-KEY-TYPES-1, Eve 2026-11-14).

Eve: "The cast of join key should keep the type that exists in the dataset; any change of type should be a
decision. So the types of the columns should be defined in the recipe, and if those need to be changed it
should be done within the recipe."

The assembler no longer receives keys cast to String behind the recipe author's back. It compares the type of
each key column on the two sides before it runs a join, and a difference fails with a message that names the
recipe, the join, the step, the columns, the two types and the fix.

What each test proves:
  - equal types of any kind (Categorical, String, Int64) join and the key keeps its type in the result;
  - String against Categorical fails (the case the old hidden cast used to hide), in both directions;
  - `left_on` / `right_on` of different types fail, and the message names the right-hand column;
  - with a list of keys only the columns that differ are named;
  - the left side is the table at that step: a cast step before the join (the fix) makes it work, and the
    second join of a recipe is checked against the result of the first;
  - a key column that does not exist is not reported as a type problem (Polars names the missing column);

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_join_key_types.py -q
"""
import polars as pl
import pytest

import transformer.actions  # noqa: F401  (loads the registry)
from transformer.data_assembler import DataAssembler
from utils.action_names import CAST, JOIN
from utils.errors import TransformationError

RECIPE = "demo_recipe"
JOIN_ID = "Joined"


def _left(dtype):
    return pl.LazyFrame({"sample_id": ["s1", "s2", "s3"], "country": ["NO", "SE", "NO"]}).with_columns(pl.col("sample_id").cast(dtype))


def _right(dtype, key="sample_id"):
    return pl.LazyFrame({key: ["s1", "s2", "s3"], "year": [2020, 2021, 2022]}).with_columns(pl.col(key).cast(dtype))


def _join(**keys):
    return {"action": JOIN, "right_ingredient": "R", "how": "left", "maintain_order": "left_right", **keys}


def _assemble(left, right, steps):
    return DataAssembler({"L": left, "R": right}, recipe_id=RECIPE, join_id=JOIN_ID).assemble(steps)


# -- equal types: the key keeps its type --------------------------------------------------------

@pytest.mark.parametrize("dtype", [pl.Categorical, pl.String])
def test_equal_key_types_join_and_the_key_keeps_its_type(dtype):
    result = _assemble(_left(dtype), _right(dtype), [_join(on=["sample_id"])]).collect()
    assert result.schema["sample_id"] == dtype
    assert result.height == 3 and result["year"].to_list() == [2020, 2021, 2022]


def test_equal_integer_keys_join():
    left = pl.LazyFrame({"sample_id": [1, 2, 3], "country": ["NO", "SE", "NO"]})
    right = pl.LazyFrame({"sample_id": [1, 2, 3], "year": [2020, 2021, 2022]})
    result = _assemble(left, right, [_join(on=["sample_id"])]).collect()
    assert result.schema["sample_id"] == pl.Int64 and result["year"].to_list() == [2020, 2021, 2022]


# -- a difference fails, with a message the recipe author can act on ----------------------------

def test_string_against_categorical_fails_and_names_everything():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(pl.String), _right(pl.Categorical), [_join(on=["sample_id"])]).collect()
    text = f"{caught.value} {caught.value.tip}"
    for part in (RECIPE, JOIN_ID, "step 0", "sample_id", "String", "Categorical", "'R'", "input_fields", JOIN, CAST):
        assert part in text, f"{part!r} is not in: {text}"


def test_categorical_against_string_fails_the_other_way_round_too():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(pl.Categorical), _right(pl.String), [_join(on=["sample_id"])]).collect()
    assert "Categorical in the left table and String in 'R'" in str(caught.value)


def test_int_against_string_fails():
    left = pl.LazyFrame({"sample_id": [1, 2, 3]})
    with pytest.raises(TransformationError, match="Int64 in the left table and String"):
        _assemble(left, _right(pl.String), [_join(on=["sample_id"])]).collect()


def test_a_key_given_as_a_plain_string_is_checked_like_a_list():
    with pytest.raises(TransformationError, match="sample_id"):
        _assemble(_left(pl.String), _right(pl.Categorical), [_join(on="sample_id")]).collect()


def test_left_on_right_on_of_different_types_fail_and_name_both_columns():
    left = pl.LazyFrame({"VF_gene": ["a", "b"]})
    right = pl.LazyFrame({"Gene_name": ["a", "b"], "n": [1, 2]}).with_columns(pl.col("Gene_name").cast(pl.Categorical))
    with pytest.raises(TransformationError) as caught:
        _assemble(left, right, [_join(left_on=["VF_gene"], right_on=["Gene_name"])]).collect()
    text = str(caught.value)
    assert "VF_gene" in text and "Gene_name" in text and "String" in text and "Categorical" in text


def test_left_on_right_on_of_equal_types_join():
    left = pl.LazyFrame({"VF_gene": ["a", "b"]})
    right = pl.LazyFrame({"Gene_name": ["a", "b"], "n": [1, 2]})
    result = _assemble(left, right, [_join(left_on=["VF_gene"], right_on=["Gene_name"])]).collect()
    assert result["n"].to_list() == [1, 2]


def test_with_two_keys_only_the_column_that_differs_is_named():
    left = pl.LazyFrame({"sample_id": ["s1"], "gene": ["g1"]}).with_columns(pl.col("gene").cast(pl.Categorical))
    right = pl.LazyFrame({"sample_id": ["s1"], "gene": ["g1"], "n": [1]})
    with pytest.raises(TransformationError) as caught:
        _assemble(left, right, [_join(on=["sample_id", "gene"])]).collect()
    text = str(caught.value)
    assert "'gene'" in text and "'sample_id'" not in text


# -- the left side is the table at that step ----------------------------------------------------

def test_a_cast_step_before_the_join_is_the_fix():
    steps = [{"action": CAST, "columns": ["sample_id"], "dtype": "Categorical"}, _join(on=["sample_id"])]
    result = _assemble(_left(pl.String), _right(pl.Categorical), steps).collect()
    assert result.schema["sample_id"] == pl.Categorical


def test_the_second_join_is_checked_against_the_result_of_the_first():
    third = pl.LazyFrame({"sample_id": ["s1", "s2", "s3"], "lab": ["x", "y", "z"]}).with_columns(pl.col("sample_id").cast(pl.Categorical))
    steps = [_join(on=["sample_id"]), {**_join(on=["sample_id"]), "right_ingredient": "T"}]
    assembler = DataAssembler({"L": _left(pl.String), "R": _right(pl.String), "T": third}, recipe_id=RECIPE, join_id=JOIN_ID)
    with pytest.raises(TransformationError) as caught:
        assembler.assemble(steps).collect()
    assert "step 1" in str(caught.value) and "'T'" in str(caught.value)


# -- what is not a type problem -----------------------------------------------------------------

def test_a_missing_key_column_is_left_to_polars_and_is_not_reported_as_a_type_problem():
    with pytest.raises(pl.exceptions.ColumnNotFoundError, match="no_such_column"):
        _assemble(_left(pl.String), _right(pl.String), [_join(on=["no_such_column"])]).collect()


def test_the_error_carries_the_structured_record_for_the_ui():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(pl.String), _right(pl.Categorical), [_join(on=["sample_id"])]).collect()
    record = caught.value.pipeline_error
    assert record.category == "assembly" and record.who == "data_analysis_recipe_author"
    assert record.evidence["left_type"] == "String" and record.evidence["right_type"] == "Categorical"
