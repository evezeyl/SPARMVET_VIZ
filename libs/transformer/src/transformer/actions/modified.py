"""The `modif_` actions: a Polars idea with a documented change (W6, DEC31, DEC33).

`modif_filter` is the one vocabulary of the row filter: the same words (`column`, `op`, `value`, `na`) are written by the
HOME filter panel, by the audit and by a recipe author, so a step the audit records is a step the recipe can hold.
What differs from Polars `LazyFrame.filter` (which takes a formula) is written in the description and in the
parameters: nothing is hidden. The one choice that a filter always makes silently in Polars, what happens to a
missing value, is the required parameter `na`.

Consumed by: the recipe (tier 1, tier 2, tier 3 steps), the audit step compiler. If deleted: a filter step is refused.
"""
from typing import Any, Dict

import polars as pl

from transformer.actions.base import ACTION_SCHEMAS, register_action
from transformer.actions.polars_calls import _checked

# @deps
# provides: action:modif_filter
# consumes: libs/transformer/src/transformer/actions/polars_calls.py (_checked), libs/utils/src/utils/ui_schema.py
# consumed_by: app/tests/test_modif_filter_verify.py
# doc: .claude/design/recipe_format_spec.md#7.5.1 (DEC39), .claude/design/home_evidence/actions_and_polars_2026-11-13.md
# @end_deps

OPERATORS = ["eq", "ne", "gt", "ge", "lt", "le", "in", "not_in", "between"]

MODIF_FILTER_SCHEMA = {
    "label": "filter rows",
    "category": "filtering", "context": ["t1", "t2", "assembly"], "tags": ["filter", "rows", "modified"],
    "polars": "modified",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "filter"]}],
    "params": {
        "column": {"widget": "string", "label": "Column", "required": True},
        "op": {"widget": "enum", "label": "Operator", "options": OPERATORS, "required": True},
        "value": {"widget": "any", "label": "Value (a list for in and not_in, [low, high] for between)", "required": True},
        "na": {"widget": "enum", "label": "Missing values (null) in the column", "options": ["keep", "remove"], "required": True},
        "closed": {"widget": "enum", "label": "Which ends of between are included", "options": ["both", "left", "right", "none"]},
    },
    "rules": [
        {"when": {"op": ["in", "not_in"]}, "shape": {"value": "list"}, "forbid": ["closed"]},
        {"when": {"op": "between"}, "shape": {"value": "pair"}},
        {"when": {"op": ["eq", "ne", "gt", "ge", "lt", "le"]}, "shape": {"value": "scalar"}, "forbid": ["closed"]},
    ],
    "description": ("Keep the rows where `column` <op> `value` (eq, ne, gt, ge, lt, le, in, not_in, between). Unlike Polars filter, "
                    "which takes a formula, it takes the words of the filter panel. `na` says what happens to a missing value (null) "
                    "of the column: `remove` drops those rows (what a comparison does in Polars), `keep` keeps them. A NaN is a number, "
                    "not a missing value, and `na` does not touch it."),
    "yaml_example": "- action: modif_filter\n  column: identity\n  op: between\n  value: [90, 100]\n  na: remove",
}


def _condition(column: str, op: str, value: Any, closed: str) -> pl.Expr:
    col = pl.col(column)
    if op == "eq":
        return col == value
    if op == "ne":
        return col != value
    if op == "gt":
        return col > value
    if op == "ge":
        return col >= value
    if op == "lt":
        return col < value
    if op == "le":
        return col <= value
    if op == "in":
        return col.is_in(value)
    if op == "not_in":
        return ~col.is_in(value)
    return col.is_between(value[0], value[1], closed=closed)


@register_action("modif_filter", ui_schema=MODIF_FILTER_SCHEMA)
def action_modif_filter(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Keep the rows where `column` <op> `value`; `na` decides the rows whose column is null."""
    clean = _checked("modif_filter", spec)
    column = clean["column"]
    if column not in lf.collect_schema().names():
        from utils.errors import TransformationError
        raise TransformationError(f"step modif_filter: column {column!r} is not in the table",
                                  tip="Write a column that exists at this step; the filter never skips a missing column")
    condition = _condition(column, clean["op"], clean["value"], clean.get("closed", "both"))
    keep = condition.fill_null(False)
    if clean["na"] == "keep":
        keep = keep | pl.col(column).is_null()
    return lf.filter(keep)
