"""The steps of an IdTransformation, written as steps of a data analysis recipe (task ID-RECON-STEPS-1).

These tests stay inside the library: they look at the form of the result and at the errors. The proof that every
step passes the real action's own check and gives the same IDs as `apply_recode_step` needs the action registry, so it
lives in `app/tests/test_id_cleaning_steps_reach_a_recipe.py`.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/id_reconciliation/tests/test_recipe_steps.py -q
"""
import copy

import pytest

from id_reconciliation import IdTransformation, recipe_steps
from utils import action_names
from utils.formula_check import formula_problems

# One valid step of every action that `apply_recode_step` runs.
INTERNAL_STEPS = {
    "strip_whitespace": {"action": "strip_whitespace"},
    "cast_string": {"action": "cast_string"},
    "regex_replace": {"action": "regex_replace", "pattern": "^.{7}", "replacement": ""},
    "lowercase": {"action": "lowercase"},
    "mutate": {"action": "mutate", "expression": "pl.col('sample_id').str.slice(0, 3)"},
    "drop_duplicates": {"action": "drop_duplicates"},
    "null_if": {"action": "null_if", "value": "NA"},
    "drop_nulls": {"action": "drop_nulls"},
}


def _transformation(*steps):
    return IdTransformation(ref_column="sample_id", target_column="ID", steps=list(steps))


def _columns_named(step):
    """Every column a recipe step names, whatever the parameter that holds it."""
    return list(step.get("columns", [])) + list(step.get("subset", [])) + list(step.get("named_exprs", {}))


def test_no_step_gives_no_recipe_step():
    assert recipe_steps(_transformation(), "sample_id") == []


@pytest.mark.parametrize("name", sorted(INTERNAL_STEPS))
def test_each_step_becomes_one_recipe_step_on_the_given_column(name):
    out = recipe_steps(_transformation(INTERNAL_STEPS[name]), "isolate")
    assert len(out) == 1
    step = out[0]
    assert step["action"] in action_names.ALL.values(), "the action name comes from utils.action_names"
    assert _columns_named(step) == ["isolate"], "the step acts on the column the caller gave, and on no other"


def test_the_old_action_names_do_not_leave_the_library():
    out = recipe_steps(_transformation(*INTERNAL_STEPS.values()), "sample_id")
    assert len(out) == len(INTERNAL_STEPS)
    assert {s["action"] for s in out}.isdisjoint(INTERNAL_STEPS), [s["action"] for s in out]


def test_the_order_of_the_steps_is_kept():
    out = recipe_steps(_transformation(INTERNAL_STEPS["strip_whitespace"], INTERNAL_STEPS["regex_replace"],
                                       INTERNAL_STEPS["drop_nulls"]), "sample_id")
    assert [s["action"] for s in out] == [action_names.STR_STRIP_CHARS, action_names.STR_REPLACE_ALL,
                                          action_names.DROP_NULLS]


def test_the_pattern_and_its_replacement_are_written_as_given():
    step = recipe_steps(_transformation({"action": "regex_replace", "pattern": ".{3}$", "replacement": "-x"}), "id")[0]
    assert step["pattern"] == ".{3}$"
    assert step["value"] == "-x"
    assert step["literal"] is False, "the pattern is a regular expression, and the step says so"


def test_an_empty_replacement_is_kept_and_is_not_a_missing_one():
    step = recipe_steps(_transformation({"action": "regex_replace", "pattern": "^x", "replacement": ""}), "id")[0]
    assert step["value"] == ""


def test_removing_duplicates_keeps_the_first_row_and_the_row_order():
    step = recipe_steps(_transformation(INTERNAL_STEPS["drop_duplicates"]), "id")[0]
    assert step == {"action": action_names.UNIQUE, "subset": ["id"], "keep": "first", "maintain_order": True}


@pytest.mark.parametrize("name", ["lowercase", "null_if"])
@pytest.mark.parametrize("column", ["sample_id", "Sample ID", "it's", 'say "id"'])
def test_a_formula_names_the_column_whatever_its_spelling(name, column):
    step = recipe_steps(_transformation(INTERNAL_STEPS[name]), column)[0]
    formula = step["named_exprs"][column]
    assert formula_problems(formula) == []
    assert repr(column) in formula


def test_two_columns_stay_separate():
    one = recipe_steps(_transformation(INTERNAL_STEPS["lowercase"]), "first_id")
    two = recipe_steps(_transformation(INTERNAL_STEPS["lowercase"]), "second_id")
    assert "second_id" not in str(one) and "first_id" not in str(two)


def test_the_transformation_is_not_changed():
    transformation = _transformation(*INTERNAL_STEPS.values())
    before = copy.deepcopy(transformation.steps)
    out = recipe_steps(transformation, "sample_id")
    out[0]["columns"].append("another")
    assert transformation.steps == before


def test_an_unknown_action_is_refused_by_name():
    with pytest.raises(ValueError, match="uppercase"):
        recipe_steps(_transformation({"action": "uppercase"}), "sample_id")


def test_a_step_without_action_is_refused():
    with pytest.raises(ValueError, match="action"):
        recipe_steps(_transformation({"pattern": "_"}), "sample_id")


@pytest.mark.parametrize("step, missing", [
    ({"action": "regex_replace", "replacement": ""}, "pattern"),
    ({"action": "regex_replace", "pattern": "_"}, "replacement"),
    ({"action": "mutate"}, "expression"),
    ({"action": "null_if"}, "value"),
    ({"action": "null_if", "value": None}, "value"),
])
def test_a_missing_parameter_is_refused_and_named(step, missing):
    with pytest.raises(ValueError, match=missing):
        recipe_steps(_transformation(step), "sample_id")


@pytest.mark.parametrize("value", [["NA"], {"a": 1}, float("nan"), float("inf")])
def test_a_null_if_value_that_cannot_be_written_in_a_formula_is_refused(value):
    with pytest.raises(ValueError, match="null_if"):
        recipe_steps(_transformation({"action": "null_if", "value": value}), "sample_id")


@pytest.mark.parametrize("column", ["", None, 3])
def test_the_column_must_be_a_name(column):
    with pytest.raises(ValueError, match="column"):
        recipe_steps(_transformation(INTERNAL_STEPS["lowercase"]), column)

