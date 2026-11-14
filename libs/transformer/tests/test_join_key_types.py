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
  - the left side is the table at that step: a cast step before the join (the fix for the left table) makes it
    work, the message says that the right table is changed in its own input_fields or wrangling, and the
    second join of a recipe is checked against the result of the first;
  - a key column that is missing on one side or on both, and `left_on` / `right_on` lists of unequal length, fail
    in the check itself with the same kind of message (recipe, join, step, columns, which side lacks what, fix);
  - `how: semi` and `how: anti` are checked like the other kinds of join;

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


def test_the_fix_says_that_a_step_before_the_join_changes_only_the_left_table():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(pl.String), _right(pl.Categorical), [_join(on=["sample_id"])]).collect()
    tip = caught.value.tip
    assert "only the left table" in tip
    assert "'R'" in tip and "its own input_fields" in tip and "its own wrangling" in tip


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

def _fails_with(left, right, step, *parts):
    with pytest.raises(TransformationError) as caught:
        _assemble(left, right, [step]).collect()
    text = f"{caught.value} {caught.value.tip}"
    for part in (RECIPE, JOIN_ID, "step 0", "'R'", *parts):
        assert part in text, f"{part!r} is not in: {text}"
    return caught.value


def test_a_key_column_missing_on_the_left_only_fails_and_says_which_side():
    error = _fails_with(_left(pl.String), _right(pl.String, key="other"), _join(left_on=["no_such"], right_on=["other"]),
                        "'no_such'", "missing in the left table", "sample_id")
    assert "missing in 'R'" not in str(error)
    assert error.pipeline_error.category == "assembly" and error.pipeline_error.who == "data_analysis_recipe_author"


def test_a_key_column_missing_on_the_right_only_fails_and_says_which_side():
    error = _fails_with(_left(pl.String), _right(pl.String), _join(left_on=["sample_id"], right_on=["no_such"]),
                        "'no_such'", "missing in 'R'", "year")
    assert "missing in the left table" not in str(error)


def test_a_key_column_missing_on_both_sides_names_both_sides():
    _fails_with(_left(pl.String), _right(pl.String), _join(on=["no_such_column"]),
                "'no_such_column'", "missing in the left table", "missing in 'R'")


def test_with_two_keys_every_missing_column_is_named():
    _fails_with(_left(pl.String), _right(pl.String), _join(on=["sample_id", "gene", "lab"]),
                "'gene'", "'lab'", "missing in the left table", "missing in 'R'")


def test_left_on_and_right_on_of_unequal_length_fail_and_name_the_lists():
    _fails_with(_left(pl.String), _right(pl.String), _join(left_on=["sample_id", "country"], right_on=["sample_id"]),
                "left_on", "right_on", "2", "1", "same number")


def test_left_on_without_right_on_fails_in_the_check_and_says_so():
    # What the engine does today without the check: Polars raises ValueError ("'left_on' requires corresponding
    # 'right_on'"), which the assembler wraps as "raised an unexpected error: ValueError" (verified by running).
    _fails_with(_left(pl.String), _right(pl.String), _join(left_on=["sample_id"]), "left_on", "right_on", "same number")


def test_the_missing_column_error_carries_the_structured_record():
    error = _fails_with(_left(pl.String), _right(pl.String), _join(on=["no_such_column"]), "no_such_column")
    evidence = error.pipeline_error.evidence
    assert "no_such_column" in evidence["missing_in_left"] and "no_such_column" in evidence["missing_in_right"]


# -- semi and anti joins are joins on keys too --------------------------------------------------

@pytest.mark.parametrize("how", ["semi", "anti"])
def test_a_semi_or_anti_join_with_different_key_types_fails(how):
    _fails_with(_left(pl.String), _right(pl.Categorical), _join(on=["sample_id"], how=how),
                "String in the left table and Categorical in 'R'")


@pytest.mark.parametrize("how", ["semi", "anti"])
def test_a_semi_or_anti_join_with_equal_key_types_runs(how):
    right = _right(pl.String).filter(pl.col("sample_id") == "s1")
    result = _assemble(_left(pl.String), right, [_join(on=["sample_id"], how=how)]).collect()
    assert result["sample_id"].to_list() == (["s1"] if how == "semi" else ["s2", "s3"])


# -- the first step: the base table as right table ----------------------------------------------

def test_a_first_step_that_joins_the_base_table_with_itself_is_skipped_by_the_assembler_today():
    # CHARACTERISATION, not an endorsement: the base is the first ingredient; a first step whose right_ingredient
    # is that same ingredient is skipped ("redundant init", data_assembler.py), so it is neither executed nor
    # checked, and a left_on/right_on of different types on that table passes. Reported to the owner as an open
    # design question (silent skip). If the owner decides that this must fail, this test changes with it.
    table = pl.LazyFrame({"a": ["x", "y"], "n": [1, 2]})
    step = {"action": JOIN, "right_ingredient": "R", "how": "left", "maintain_order": "left_right", "left_on": ["a"], "right_on": ["n"]}
    result = DataAssembler({"R": table}, recipe_id=RECIPE, join_id=JOIN_ID).assemble([step]).collect()
    assert result.equals(table.collect())


def test_a_first_step_that_joins_the_base_table_with_itself_on_other_keys_adds_nothing_today():
    # CHARACTERISATION, decision pending (D9, J-c): the self-join of the base table on different left_on / right_on
    # columns is a real join in Polars (it would add the right-hand copy of every column) but the assembler skips it
    # without a message. Options for Eve: keep, fail with a plain message, or warn; and whether a real self-join
    # (different keys) is allowed. If she decides, this test changes with it.
    table = pl.LazyFrame({"a": ["x", "y"], "b": ["y", "z"], "n": [1, 2]})
    step = {"action": JOIN, "right_ingredient": "R", "how": "left", "maintain_order": "left_right", "left_on": ["a"], "right_on": ["b"]}
    result = DataAssembler({"R": table}, recipe_id=RECIPE, join_id=JOIN_ID).assemble([step]).collect()
    assert result.columns == ["a", "b", "n"], "no right-hand copy of the columns: the step was skipped"
    assert result.equals(table.collect())
    done = table.collect().join(table.collect(), left_on="a", right_on="b", how="left", maintain_order="left_right")
    assert done.width > result.width, "the join, run, would have added columns"


def test_a_float_join_key_merges_identifiers_that_differ_in_the_files_decision_pending():
    # CHARACTERISATION, decision pending (D10, J-d): a key declared Float64 turns the identifiers "001", "1" and
    # "1.0" of the files into the same number, so three samples become one key and the join returns more rows than
    # samples (3 x 3 = 9 for 3 samples). No message is given. Options for Eve: change the template to a text type,
    # and/or an advice in the checker against a float join key. If she decides, this test changes with it.
    import io

    def table(value):
        text = f"sample_id\t{value}\n001\t1\n1\t2\n1.0\t3\n"
        return pl.read_csv(io.StringIO(text), separator="\t", schema_overrides={"sample_id": pl.Float64}).lazy()

    left, right = table("n"), table("year")
    assert left.collect()["sample_id"].n_unique() == 1, "the three identifiers are one key"
    result = _assemble(left, right, [_join(on=["sample_id"])]).collect()
    assert result.height == 9 and result.height > left.collect().height, "more rows than samples"


def test_the_error_carries_the_structured_record_for_the_ui():
    with pytest.raises(TransformationError) as caught:
        _assemble(_left(pl.String), _right(pl.Categorical), [_join(on=["sample_id"])]).collect()
    record = caught.value.pipeline_error
    assert record.category == "assembly" and record.who == "data_analysis_recipe_author"
    assert record.evidence["left_type"] == "String" and record.evidence["right_type"] == "Categorical"
