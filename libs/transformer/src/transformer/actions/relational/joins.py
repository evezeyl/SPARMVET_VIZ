from typing import Dict, Any, Optional
import polars as pl
from transformer.actions.base import register_action

# @deps
# provides: action:join, action:join_filter
# consumed_by: any YAML manifest using join steps, .claude/rules/rules_persona_bioscientist.md#8, libs/blueprint_arch/src/blueprint_arch/schema_registry.py (ui_schema via ACTION_SCHEMAS)
# doc: .claude/rules/rules_persona_bioscientist.md#8, .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps


@register_action("join", ui_schema={
    "label": "Join datasets",
    "category": "relational",
    "context": ["assembly"],
    "tags": ["join", "merge", "relational"],
    "params": {
        "right_ingredient": {"widget": "string", "label": "Right ingredient ID (data_schemas key)", "required": True},
        "on": {"widget": "column_selector", "multi": False, "label": "Join column (symmetric)", "required": False,
               "hint": "Use 'on' when both frames share the same column name"},
        "left_on": {"widget": "column_selector", "multi": False, "label": "Left join column", "required": False},
        "right_on": {"widget": "string", "label": "Right join column name", "required": False},
        "how": {"widget": "enum", "label": "Join strategy", "required": False, "default": "left",
                "options": ["left", "inner", "outer", "semi", "anti", "cross"]},
    },
})
def join_action(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Standard Join Action for the Assembly Layer.

    Parameters:
        right_ingredient: Key in the ingredients dictionary.
        on: Single column or list of columns to join on.
        how: Join strategy ('left', 'inner', 'outer', etc.)
    """
    right_df = spec.get("__right_df__")
    if right_df is None:
        raise ValueError(
            f"Assembly Action 'join' requires a resolved __right_df__. Check DataAssembler logic.")

    join_on = spec.get("on")
    left_on = spec.get("left_on")
    right_on = spec.get("right_on")
    how = spec.get("how", "left")

    if join_on:
        return lf.join(right_df, on=join_on, how=how)
    elif left_on and right_on:
        return lf.join(right_df, left_on=left_on, right_on=right_on, how=how)
    else:
        raise ValueError(
            "Join action requires either 'on' or both 'left_on' and 'right_on'.")


@register_action("join_filter")
def join_filter_action(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Inner Join Filter. Acts as a whitelist filter using a reference table.
    """
    spec["how"] = "inner"
    return join_action(lf, spec)
