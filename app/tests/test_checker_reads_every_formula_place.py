"""The recipe checker reads every place where an action takes a formula (D-0030, D-0064, D-0050).

Decided: formulas only from the allowed list of Polars functions, and a recipe with a forbidden call is refused by the
checker (ST06) before it is built. The checker finds a formula by the widget of the parameter in the action schema, so
a formula parameter without that mark was accepted silently and failed only at run time.

Three guards:
1. the places where the transformer evaluates a formula (found in the source, not listed by hand) are exactly the
   places this file knows: a new action that takes a formula fails here until it is declared and covered;
2. every formula parameter of the real action schemas is one of those places, and every place is marked in its schema;
3. a forbidden call in each place (and in each form: text, mapping of texts, list of texts) is refused by the checker.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_checker_reads_every_formula_place.py -q
"""
import ast
import copy
from pathlib import Path

import pytest
import yaml

import transformer.actions  # noqa: F401  (loads the registry)
from app.modules.data_analysis_recipe_validator import checker_catalogs
from utils.recipe_check import check_recipe

ROOT = Path(__file__).resolve().parents[2]
ACTIONS_DIR = ROOT / "libs/transformer/src/transformer/actions"
TEMPLATE = ROOT / "config/data_analysis_recipes/templates/simple_template.yaml"
CATALOGS = checker_catalogs()
FORBIDDEN = "__import__('os').system('id')"

# module:function that calls `_formula` -> the (action, parameter, form) places it reads. A new function that calls
# `_formula` must be added here with the parameter it reads, or the first test fails.
PLACES = {
    "polars_calls:_with_columns": [("polars_with_columns", "named_exprs", "mapping")],
    "polars_calls:_group_by_action": [("polars_group_by", "named_aggs", "mapping")],
    "polars_rows:_remove_action": [("polars_remove", "predicates", "list")],
    "polars_time_joins:_require_same_types": [("modif_join_where", "predicates", "list")],
    "polars_time_joins:_join_where": [("modif_join_where", "predicates", "list")],
    "polars_time_joins:run": [("polars_group_by_dynamic", "named_aggs", "mapping"), ("polars_rolling", "named_aggs", "mapping")],
}
ALL_PLACES = sorted({place for places in PLACES.values() for place in places})


class _Callers(ast.NodeVisitor):
    """Collects the innermost function that contains each call of `_formula`."""

    def __init__(self, module: str):
        self.module, self.stack, self.found = module, [], set()

    def visit_FunctionDef(self, node):
        self.stack.append(node.name)
        self.generic_visit(node)
        self.stack.pop()

    visit_AsyncFunctionDef = visit_FunctionDef

    def visit_Call(self, node):
        func = node.func
        if (isinstance(func, ast.Name) and func.id == "_formula") or (isinstance(func, ast.Attribute) and func.attr == "_formula"):
            self.found.add(f"{self.module}:{self.stack[-1] if self.stack else '<module>'}")
        self.generic_visit(node)


def formula_callers() -> set:
    """Every function of the transformer actions that calls `_formula(...)` or `calls._formula(...)`."""
    found = set()
    for path in sorted(ACTIONS_DIR.glob("*.py")):
        visitor = _Callers(path.stem)
        visitor.visit(ast.parse(path.read_text()))
        found |= visitor.found
    return found


def test_the_places_that_evaluate_a_formula_are_the_places_this_test_covers():
    assert formula_callers() == set(PLACES), (
        "an action evaluates a formula in a function that this test does not know: mark its parameter with "
        "`value_widget: expression` (or `widget: expression`) in its schema and add it to PLACES")


def marked_as_formula(definition: dict) -> bool:
    return "expression" in (definition.get("widget"), definition.get("value_widget"))


@pytest.mark.parametrize("action,param,form", ALL_PLACES)
def test_the_schema_marks_the_parameter_as_a_formula(action, param, form):
    definition = CATALOGS["actions"][action]["params"][param]
    assert marked_as_formula(definition), f"{action}.{param} takes formulas but its schema does not say so: {definition}"


def test_every_formula_parameter_of_the_schemas_is_a_known_place():
    marked = {(name, param) for name, schema in CATALOGS["actions"].items() for param, definition in schema.get("params", {}).items()
              if marked_as_formula(definition)}
    assert marked == {(action, param) for action, param, _ in ALL_PLACES}


def recipe_with(step: dict) -> dict:
    raw = yaml.safe_load(TEMPLATE.read_text())
    raw = copy.deepcopy(raw)
    raw["joins"]["main_collection"]["tier1"]["steps"].append(step)
    return raw


def check(raw: dict):
    return check_recipe(raw, "run", file_stem="simple_template", catalogs=CATALOGS)


def test_the_base_recipe_is_clean():
    result = check(yaml.safe_load(TEMPLATE.read_text()))
    assert [p.text() for p in result.errors] == []
    assert "actions" in result.coverage


def formula_value(form: str, text: str):
    return {"z": text} if form == "mapping" else [text]


@pytest.mark.parametrize("action,param,form", ALL_PLACES)
def test_a_forbidden_call_is_refused_by_the_checker(action, param, form):
    step = {"action": action, param: formula_value(form, FORBIDDEN)}
    codes = [p.code for p in check(recipe_with(step)).errors]
    assert "ST06" in codes, f"{action}.{param}: a forbidden call passed the checker (codes seen: {codes})"


@pytest.mark.parametrize("action,param,form", ALL_PLACES)
def test_an_allowed_formula_is_not_refused(action, param, form):
    step = {"action": action, param: formula_value(form, "pl.col('value') * 2")}
    assert "ST06" not in [p.code for p in check(recipe_with(step)).errors]


def test_the_message_names_the_allowed_list():
    step = {"action": "polars_with_columns", "named_exprs": {"z": FORBIDDEN}}
    texts = [p.text() for p in check(recipe_with(step)).errors if p.code == "ST06"]
    assert texts and "__import__" in texts[0]
