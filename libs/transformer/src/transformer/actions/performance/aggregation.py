import polars as pl
from typing import Dict, Any, List, Union
from transformer.actions.base import register_action

# @deps
# provides: action:summarize, action:sort, action:count_by_group
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8
# doc: .claude/rules/rules_persona_bioscientist.md#8
# @end_deps


@register_action("summarize")
def action_summarize(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Groups by specific columns and aggregates the target column(s).
    Useful for collapsing data before visualization.
    """
    columns = spec.get("columns", [])
    group_by_cols = spec.get("group_by", [])
    agg_type = spec.get("agg", "count")
    new_name = spec.get("new_name")

    # Standardize inputs
    if isinstance(group_by_cols, str):
        group_by_cols = [group_by_cols]
    if isinstance(columns, str):
        columns = [columns]

    # Build the aggregation expressions
    if agg_type == "count":
        agg_exprs = [pl.col(c).count().alias(new_name if (
            new_name and len(columns) == 1) else f"{c}_count") for c in columns]
    elif agg_type == "sum":
        agg_exprs = [pl.col(c).sum().alias(new_name if (
            new_name and len(columns) == 1) else f"{c}_sum") for c in columns]
    elif agg_type == "mean":
        agg_exprs = [pl.col(c).mean().alias(new_name if (
            new_name and len(columns) == 1) else f"{c}_mean") for c in columns]
    else:
        agg_exprs = [pl.col(c).count().alias(new_name if (
            new_name and len(columns) == 1) else f"{c}_count") for c in columns]

    if not group_by_cols:
        return lf.select(agg_exprs)

    return lf.group_by(group_by_cols).agg(agg_exprs)


@register_action("count_by_group")
def action_count_by_group(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Calculates the count of rows per group and adds it as a new column 
    without collapsing the dataframe (Window Function).
    Spec: { group_by: ["col1"], new_column: "count_val" }
    """
    group_by = spec.get("group_by", [])
    new_col = spec.get("new_column", "group_count")

    if isinstance(group_by, str):
        group_by = [group_by]

    return lf.with_columns(
        pl.len().over(group_by).alias(new_col)
    )
