"""
The vocabulary of `ui_schema` widgets, and the value shape each widget stands for.

# @deps
# provides: constant:WIDGETS, function:expected_shape, function:shape_problem
# consumed_by: libs/transformer/tests/test_ui_schemas.py, libs/transformer/tests/test_action_schema_examples.py, libs/blueprint_arch/src/blueprint_arch/widget_text.py, libs/blueprint_arch/tests/test_schema_registry.py
# doc: .claude/design/recipe_format_spec.md (section 8), .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps

Two registries (`transformer` actions, `viz_factory` components) describe their parameters with these widgets; the
Blueprint form renders them and the recipe checker tests values against them. One list here, read by all, so the
registries, the form and the checker cannot disagree.

A parameter's shape is what the recipe holds: a scalar, a list, a mapping, or a list of mappings.
"""
from typing import Any, Optional

WIDGETS = (
    "column_selector",     # one column, or several when `multi`
    "expression",         # a Polars expression as text
    "enum",               # one of `options`, or several when `multi`
    "dtype_picker",       # a Polars dtype name
    "number",
    "string",             # plain text, a scalar
    "color",              # hex, name, or a mapping to a column or palette (Blueprint)
    "column_or_literal",  # a column name or a literal value
    "bool",
    "list",               # a YAML list; `items: mapping` when every item is a mapping
    "mapping",            # a YAML mapping, for example old name to new name
)


def expected_shape(param_def: dict) -> str:
    """'scalar', 'list', 'mapping' or 'list_of_mapping' for one parameter declaration."""
    widget = param_def.get("widget")
    if widget == "mapping":
        return "mapping"
    if widget == "list":
        return "list_of_mapping" if param_def.get("items") == "mapping" else "list"
    if widget in ("column_selector", "enum") and param_def.get("multi"):
        return "list"
    return "scalar"


def shape_problem(param_def: dict, value: Any) -> Optional[str]:
    """What is wrong with a value for a `list` or `mapping` parameter, or None. Scalar widgets are not judged here."""
    shape = expected_shape(param_def)
    if shape == "mapping" and not isinstance(value, dict):
        return "write a mapping, for example {old_name: new_name}"
    if shape in ("list", "list_of_mapping"):
        if not isinstance(value, list):
            return "write a list, for example [a, b]"
        if shape == "list_of_mapping" and not all(isinstance(item, dict) for item in value):
            return "every item of the list must be a mapping, for example {matches: S, value: 0}"
    return None
