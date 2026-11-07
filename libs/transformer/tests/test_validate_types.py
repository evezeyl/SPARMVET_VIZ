"""MetadataValidator.validate_types: values must fit the type the data analysis recipe declares (issue #11).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_validate_types.py -q
"""
import polars as pl
import pytest

from transformer.metadata_validator import MetadataValidator
from utils.errors import DataAnalysisRecipeError

CONTRACT = {
    "sample_id": {"type": "categorical"},
    "reads": {"type": "numeric"},
    "label": {"type": "utf8"},
}


def lf(**cols):
    return pl.DataFrame(cols).lazy()


def check(frame, contract=CONTRACT):
    MetadataValidator().validate_types(frame, contract, context="[T]")


def test_a_valid_file_passes():
    check(lf(sample_id=["a", "b"], reads=[1.5, 2.0], label=["x", "y"]))


def test_text_in_a_numeric_column_is_rejected_with_the_column_and_values():
    with pytest.raises(DataAnalysisRecipeError) as err:
        check(lf(sample_id=["a", "b", "c"], reads=["1", "abc", "n/a"], label=["x", "y", "z"]))
    message = str(err.value)
    assert "'reads'" in message and "'abc'" in message and "'n/a'" in message
    assert "categorical or utf8" in err.value.tip


def test_only_a_few_examples_are_shown():
    values = [f"bad{i}" for i in range(10)]
    with pytest.raises(DataAnalysisRecipeError) as err:
        check(lf(sample_id=values, reads=values, label=values))
    assert str(err.value).count("bad") == 3


def test_digits_are_accepted_as_text_for_categorical_and_utf8_columns():
    check(lf(sample_id=[32557144, 97991777], reads=[1.0, 2.0], label=[1, 2]))      # numbers stored as numbers
    check(lf(sample_id=["32557144", "007"], reads=["1", "2"], label=["12", "x"]))  # numbers written as text


def test_numbers_written_as_text_are_fine_in_a_numeric_column():
    check(lf(sample_id=["a"], reads=["12.5"], label=["x"]))


def test_missing_values_are_not_errors():
    check(lf(sample_id=["a", "b"], reads=[1.0, None], label=["x", None]))


def test_a_whole_number_column_declared_int_rejects_decimals():
    with pytest.raises(DataAnalysisRecipeError):
        check(lf(n=["1", "2.5"]), {"n": {"type": "int"}})


def test_an_empty_contract_or_an_undeclared_column_is_ignored():
    check(lf(reads=["abc"]), {})
    check(lf(reads=["abc"]), {"other": {"type": "numeric"}})
