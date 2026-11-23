"""One numbering of steps for the recipe writer: from 1, in the checker and in every assembler message (Eve, 2026-11-15).

The checker writes paths such as `joins.AB.tier1.steps[2]` (the second step); the assembler said "step 1" for the same step
(it counted from 0). Both count from 1 now. This test takes one recipe with an error in its SECOND join step and shows the same number
in the checker's path and in the assembler's error.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/transformer/tests/test_step_numbering.py -q
"""
import re

import polars as pl
import pytest

import transformer.actions  # noqa: F401
from app.modules.data_analysis_recipe_validator import checker_catalogs
from app.tests.tiny_recipe import tiny_recipe
from transformer.data_assembler import DataAssembler
from utils.errors import TransformationError
from utils.recipe_check import check_recipe
from utils.recipe_factory import minimal_join, minimal_schema


def two_step_recipe():
    raw = tiny_recipe()
    raw["data_schemas"]["B"] = minimal_schema("./assets/test_data/tiny/A.tsv", {"a": {"type": "String", "ui_label": "A"}}, label="B")
    raw["data_schemas"]["B"]["description"] = "One row per a."
    ok = {"action": "polars_join", "right_ingredient": "B", "on": ["a"], "how": "left", "maintain_order": "left_right"}
    bad = {"action": "polars_join", "right_ingredient": "Ghost", "on": ["a"], "how": "left", "maintain_order": "left_right"}  # not an ingredient of the join
    raw["joins"] = {"AB": minimal_join(["A", "B"], [ok, bad])}
    raw["joins"]["AB"]["description"] = "A with B."
    return raw, [ok, bad]


def test_the_checker_and_the_assembler_name_the_same_step_number_for_the_same_step():
    raw, steps = two_step_recipe()
    found = [p for p in check_recipe(raw, "run", catalogs=checker_catalogs()).problems if p.code == "J05"]
    assert found, "the checker must refuse the second step"
    checker_number = int(re.search(r"tier1\.steps\[(\d+)\]", found[0].path).group(1))
    ingredients = {"A": pl.LazyFrame({"a": ["a"]}), "B": pl.LazyFrame({"a": ["a"]})}
    with pytest.raises(TransformationError) as caught:
        DataAssembler(ingredients, recipe_id="r", join_id="AB").assemble(steps)
    pipeline_error = caught.value.pipeline_error
    assembler_number = int(re.search(r"step (\d+)", pipeline_error.location).group(1))
    assert checker_number == assembler_number == 2


def test_a_step_without_an_action_is_numbered_from_one():
    with pytest.raises(TransformationError) as caught:
        DataAssembler({"A": pl.LazyFrame({"id": ["a"]})}, recipe_id="r", join_id="AB").assemble([{"action": "polars_head", "n": 1}, {"on": "id"}])
    assert "Assembly step 2 has no 'action' key" in str(caught.value)
