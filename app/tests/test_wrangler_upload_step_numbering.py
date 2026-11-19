"""STEP-NUMBERING-1: the same step has the same number (counted from 1) in the checker, the wrangler and the upload report.

One recipe whose SECOND tier-1 step names an action that does not exist.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_wrangler_upload_step_numbering.py -q
"""
import re

import polars as pl
import pytest

from app.modules.data_analysis_recipe_validator import checker_catalogs, uploaded_recipe_report
from transformer.data_wrangler import DataWrangler
from utils import action_names
from utils.recipe_check import check_recipe
from utils.recipe_factory import minimal_join, minimal_plot, minimal_recipe, minimal_schema
from utils.errors import TransformationError

STEPS = [
    {"action": action_names.FILTER, "column": "reads", "op": "ge", "value": 15, "na": "remove"},
    {"action": "no_such_action", "column": "reads"},
]


def recipe() -> dict:
    schemas = {"samples": minimal_schema("data/samples.tsv", {"sample_id": "String", "reads": "Int64"},
                                         entity_key="sample_id", tier1=STEPS)}
    joins = {"C": minimal_join(["samples"], [{"action": action_names.SELECT, "exprs": ["sample_id"]}], label="S")}
    return minimal_recipe("tiny", schemas=schemas, joins=joins,
                          plots={"p": minimal_plot("C", {"x": "sample_id"}, label="P")})


def test_the_second_step_is_number_two_in_the_checker_the_wrangler_and_the_upload_report():
    checked = [p for p in check_recipe(recipe(), "build", catalogs=checker_catalogs()).errors if "no_such_action" in p.message]
    # the checker names the place in the recipe (D-0250: the tier is its own key, the list is under `steps`)
    assert checked and all(p.path.endswith("tier1.steps[2].action") for p in checked)

    with pytest.raises(TransformationError) as raised:
        DataWrangler().run(pl.LazyFrame({"sample_id": ["a"], "reads": [1]}), STEPS)
    assert "wrangling step 2" in raised.value.pipeline_error.location
    assert not re.search(r"step [013]\b", raised.value.pipeline_error.location)

    fragment = {"tier1": {"steps": STEPS}}      # the tiers of a table, as they are written now (D-0250)
    report = [line for line in uploaded_recipe_report(fragment) if "no_such_action" in line]
    assert report and all("tier1[2]" in line for line in report)


def test_the_first_step_is_number_one_not_zero():
    with pytest.raises(TransformationError) as raised:
        DataWrangler().run(pl.LazyFrame({"a": [1]}), [{"column": "a"}])
    assert "step 1 " in raised.value.pipeline_error.problem
    assert [line for line in uploaded_recipe_report({"tier1": {"steps": [{"column": "a"}]}}) if "tier1[1]" in line]


def test_the_same_number_in_the_checker_the_wrangler_the_assembler_and_the_upload_report():
    """Wrangling steps: checker, wrangler, upload report. Join steps: checker and assembler (tests of the assembler: test_step_numbering.py).
    Both lists count from 1, so the second step of either is number 2 everywhere."""
    import polars as pl
    from app.tests.test_step_numbering import two_step_recipe
    from transformer.data_assembler import DataAssembler
    from utils.recipe_check import check_recipe as check

    raw, steps = two_step_recipe()
    found = [p for p in check(raw, "run", catalogs=checker_catalogs()).problems if p.code == "J05"]
    with pytest.raises(TransformationError) as assembling:
        DataAssembler({"A": pl.LazyFrame({"a": ["a"]}), "B": pl.LazyFrame({"a": ["a"]})}, recipe_id="r", join_id="AB").assemble(steps)
    with pytest.raises(TransformationError) as wrangling:
        DataWrangler().run(pl.LazyFrame({"sample_id": ["a"], "reads": [1]}), STEPS)
    upload = [line for line in uploaded_recipe_report({"tier1": {"steps": STEPS}}) if "no_such_action" in line]
    numbers = {
        "checker (join)": int(re.search(r"\[(\d+)\]", found[0].path).group(1)),
        "assembler": int(re.search(r"step (\d+)", assembling.value.pipeline_error.location).group(1)),
        "wrangler": int(re.search(r"step (\d+)", wrangling.value.pipeline_error.location).group(1)),
        "upload report": int(re.search(r"tier1\[(\d+)\]", upload[0]).group(1)),
    }
    assert set(numbers.values()) == {2}, numbers
