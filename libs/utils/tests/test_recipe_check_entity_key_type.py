"""E03 (D-0225, D-0067): the declared entity key (the sample id) is a String or a Categorical, never a number.

A number as an id gives join and type problems: leading zeros are lost, 001 and 1 become one sample.
The checker refuses a recipe whose entity key column has a numeric type, and says recipe, table, column, type and the fix.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_check_entity_key_type.py -q
"""
import pytest

import utils.recipe_check as recipe_check
from utils.recipe_check import check_recipe

from test_recipe_check import CATALOGS, mutated, valid


def run(raw):
    return check_recipe(raw, "run", file_stem="r", catalogs=CATALOGS)


def set_key_type(table, type_, **extra):
    def change(raw):
        raw["data_schemas"][table]["input_fields"]["id"].update(type=type_, **extra)
    return change


@pytest.mark.parametrize("type_", ["Int64", "Int32", "UInt8", "Float64", "Float32"])
def test_a_number_as_the_sample_id_is_refused_with_table_column_type_and_fix(type_):
    result = run(mutated(set_key_type("A", type_)))
    found = [p for p in result.problems if p.code == "E03"]
    assert len(found) == 1 and found[0].severity == "E" and not result.ok
    text = found[0].text("my_recipe")
    assert text.startswith("my_recipe : data_schemas.A.input_fields.id.type :")
    assert "'A'" in text and "'id'" in text and type_ in text
    assert "Suggestion: declare it as String" in text and "Categorical" in text and "Fix:" not in text.split("Suggestion")[0]


def test_a_decimal_is_a_number_too():
    result = run(mutated(set_key_type("A", "Decimal", precision=10, scale=2)))
    assert "E03" in result.codes()


@pytest.mark.parametrize("type_", ["String", "Categorical"])
def test_a_string_or_a_categorical_id_passes(type_):
    def change(raw):
        set_key_type("A", type_)(raw)
        set_key_type("B", type_)(raw)
    assert run(mutated(change)).problems == []


def test_a_number_in_a_column_that_is_not_the_entity_key_is_not_refused():
    # v is Float64 in the valid recipe and is not a key; w is Int64
    assert "E03" not in run(valid()).codes()


def test_no_id_declared_gives_no_e03_and_the_checker_does_not_guess():
    # the id column is not marked: nothing is guessed from the name, a number named id stays unflagged here
    def change(raw):
        raw["data_schemas"]["A"]["input_fields"]["id"].update(type="Int64")
        raw["data_schemas"]["A"]["input_fields"]["id"].pop("is_entity_id")
    assert "E03" not in run(mutated(change)).codes()


def test_a_table_without_the_id_column_is_not_refused():
    def change(raw):
        raw["data_schemas"]["B"]["input_fields"].pop("id")
        raw["joins"] = {}
        raw["analysis_groups"]["g"]["plots"]["p"]["target_dataset"] = "A"
    assert "E03" not in run(mutated(change)).codes()


def test_text_in_one_table_and_a_number_in_the_joined_table_only_the_number_is_named():
    result = run(mutated(set_key_type("B", "Int64")))
    named = [p.path for p in result.problems if p.code == "E03"]
    assert named == ["data_schemas.B.input_fields.id.type"]
    assert "J09" in result.codes()  # the join key types differ: the existing check still speaks


def test_the_metadata_schema_is_checked_like_any_table():
    def change(raw):
        raw["metadata_schema"] = raw["data_schemas"].pop("B")
        raw["joins"]["AB"]["ingredients"][1]["dataset_id"] = "metadata_schema"
        raw["joins"]["AB"]["tier1"]["steps"][0]["right_ingredient"] = "metadata_schema"
        raw["metadata_schema"]["input_fields"]["id"]["type"] = "Int64"
    result = run(mutated(change))
    assert [p.path for p in result.problems if p.code == "E03"] == ["metadata_schema.input_fields.id.type"]


def test_the_check_can_fail(monkeypatch):
    """Disable the check and the refusal is gone: the tests above do not pass by accident."""
    monkeypatch.setattr(recipe_check._Check, "entity_key_type", lambda self, definition, path, table, slug: None)
    assert "E03" not in run(mutated(set_key_type("A", "Int64"))).codes()
