"""Every plot component says what it is to plotnine, and the code proves it (VIZ-STANDARD-1, ADR-106 V1/V2).

The registry field `plotnine` of a component's `ui_schema` has the same style as the field `polars` of an action:

  exact     the component only passes its parameters to the plotnine object of the same name;
  modified  it wraps a plotnine object of that name but adds logic of its own, or wraps another object;
  own       no plotnine object of that name exists.

The value is re-derived here from the code of each component, so a component marked `exact` that gains logic, or a
`modified` one that loses it, fails. A `modified` or `own` component states in its description what it changes
(ADR-106 V2); the test checks that the sentence exists, not that it is true (a person reads it).

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py (PLOT_COMPONENTS, COMPONENT_SCHEMAS)
# doc: .claude/knowledge/architecture_decisions.md (ADR-106)
# @end_deps
"""
import ast
import inspect
import textwrap
from typing import Any, Dict

import plotnine
import pytest
from plotnine import ggplot, geom_point, theme_bw

import viz_factory  # noqa: F401  (importing it registers the components)
from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS

FIELD = "plotnine"
VALUES = {"exact", "modified", "own"}
SENTENCE = {"modified": "Differs from plotnine:", "own": "Not in plotnine:"}


def derive_kind(func, name: str) -> str:
    """exact / modified / own, read from the code of the component function `func` registered under `name`."""
    plotnine_object = getattr(plotnine, name, None)
    if plotnine_object is None:
        return "own"
    function = ast.parse(textwrap.dedent(inspect.getsource(func))).body[0]
    body = list(function.body)
    if body and isinstance(body[0], ast.Expr) and isinstance(getattr(body[0], "value", None), ast.Constant):
        body = body[1:]  # the docstring
    imported = {}
    while body and isinstance(body[0], ast.ImportFrom) and body[0].module == "plotnine":
        imported.update({(a.asname or a.name): a.name for a in body[0].names})
        body = body[1:]
    plot_arg, spec_arg = (a.arg for a in function.args.args[:2])
    if len(body) == 1 and isinstance(body[0], ast.Return) and isinstance(body[0].value, ast.BinOp):
        add = body[0].value
        call = add.right
        passes_spec_unchanged = (
            isinstance(add.op, ast.Add) and isinstance(add.left, ast.Name) and add.left.id == plot_arg
            and isinstance(call, ast.Call) and isinstance(call.func, ast.Name) and not call.args
            and len(call.keywords) == 1 and call.keywords[0].arg is None
            and isinstance(call.keywords[0].value, ast.Name) and call.keywords[0].value.id == spec_arg)
        if passes_spec_unchanged:
            callee = call.func.id
            target = getattr(plotnine, imported[callee]) if callee in imported else func.__globals__.get(callee)
            if target is plotnine_object:
                return "exact"
    return "modified"


# -- the deriving rule itself, on small functions ---------------------------------------------------

def _pass_through(p, spec: Dict[str, Any]):
    return p + geom_point(**spec)


def _pass_through_with_docstring_and_import(p, spec: Dict[str, Any]):
    """Pass through."""
    from plotnine import geom_point as gp
    return p + gp(**spec)


def _adds_a_default(p, spec: Dict[str, Any]):
    spec.setdefault("size", 3)
    return p + geom_point(**spec)


def _changes_a_value(p, spec: Dict[str, Any]):
    return p + geom_point(**{**spec, "size": 3})


def _wraps_another_object(p, spec: Dict[str, Any]):
    return p + theme_bw(**spec)


def _returns_the_plot(p, spec: Dict[str, Any]):
    return p


def _renames_the_plot_argument(plot, spec: Dict[str, Any]):
    return plot + geom_point(**spec)


def _passes_something_else(p, spec: Dict[str, Any]):
    return p + geom_point(**spec["inner"])


@pytest.mark.parametrize("func, name, expected", [
    (_pass_through, "geom_point", "exact"),
    (_pass_through_with_docstring_and_import, "geom_point", "exact"),
    (_renames_the_plot_argument, "geom_point", "exact"),
    (_adds_a_default, "geom_point", "modified"),
    (_changes_a_value, "geom_point", "modified"),
    (_wraps_another_object, "geom_point", "modified"),
    (_returns_the_plot, "geom_point", "modified"),
    (_passes_something_else, "geom_point", "modified"),
    (_pass_through, "geom_nothing_like_it", "own"),
])
def test_the_rule_reads_the_code(func, name, expected):
    assert derive_kind(func, name) == expected


def test_a_pass_through_under_a_name_of_another_plotnine_object_is_modified():
    # theme_bw called under the name of theme_light: the name exists in plotnine, the object is another one
    assert derive_kind(_wraps_another_object, "theme_light") == "modified"
    assert derive_kind(_wraps_another_object, "theme_bw") == "exact"


# -- the registry ------------------------------------------------------------------------------------

def test_every_registered_component_has_a_schema():
    assert len(PLOT_COMPONENTS) >= 191
    assert sorted(set(PLOT_COMPONENTS) - set(COMPONENT_SCHEMAS)) == []


def test_every_component_declares_the_field():
    missing = [n for n in PLOT_COMPONENTS if COMPONENT_SCHEMAS[n].get(FIELD) not in VALUES]
    assert missing == [], f"components without a valid `{FIELD}` field: {missing}"


def test_the_declared_value_is_the_one_the_code_proves():
    wrong = {n: (COMPONENT_SCHEMAS[n].get(FIELD), derive_kind(PLOT_COMPONENTS[n], n))
             for n in PLOT_COMPONENTS if COMPONENT_SCHEMAS[n].get(FIELD) != derive_kind(PLOT_COMPONENTS[n], n)}
    assert wrong == {}, "declared against derived"


def test_a_modified_or_own_component_states_what_it_changes_in_its_description():
    lacking = []
    for name in PLOT_COMPONENTS:
        kind = COMPONENT_SCHEMAS[name][FIELD]
        if kind not in SENTENCE:
            continue
        _, found, sentence = COMPONENT_SCHEMAS[name].get("description", "").partition(SENTENCE[kind])
        if not found or len(sentence.strip()) < 20:
            lacking.append(name)
    assert lacking == []


def test_an_exact_component_has_no_change_sentence():
    claimed = [n for n in PLOT_COMPONENTS if COMPONENT_SCHEMAS[n][FIELD] == "exact"
               and any(s in COMPONENT_SCHEMAS[n].get("description", "") for s in SENTENCE.values())]
    assert claimed == []


def test_the_three_values_are_all_in_use():
    assert {COMPONENT_SCHEMAS[n][FIELD] for n in PLOT_COMPONENTS} == VALUES


def test_an_exact_component_wraps_the_plotnine_object_of_its_own_name():
    wrong = []
    for name, schema in COMPONENT_SCHEMAS.items():
        if schema[FIELD] != "exact":
            continue
        wraps = schema.get("wraps") or []
        if not wraps or wraps[0]["lib"] != "plotnine" or getattr(plotnine, wraps[0]["attr_path"][0], None) is not getattr(plotnine, name):
            wrong.append(name)
    assert wrong == []


def test_an_own_component_is_not_a_plotnine_name():
    assert [n for n in PLOT_COMPONENTS if COMPONENT_SCHEMAS[n][FIELD] == "own" and hasattr(plotnine, n)] == []


def test_the_registry_check_can_fail():
    saved = COMPONENT_SCHEMAS["geom_point"].pop(FIELD)
    try:
        assert [n for n in PLOT_COMPONENTS if COMPONENT_SCHEMAS[n].get(FIELD) not in VALUES] == ["geom_point"]
    finally:
        COMPONENT_SCHEMAS["geom_point"][FIELD] = saved


def test_facet_wrap_is_exact_and_leaves_the_recipe_parameters_alone():
    assert COMPONENT_SCHEMAS["facet_wrap"][FIELD] == "exact"
    spec = {"facets": "g"}
    PLOT_COMPONENTS["facet_wrap"](ggplot(), spec)
    assert spec == {"facets": "g"}
