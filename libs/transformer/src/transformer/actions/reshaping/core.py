import polars as pl
from typing import Dict, Any, List, Union
from transformer.actions.base import register_action

# @deps
# provides: action:unpivot, action:explode, action:unnest, action:split_to_list, action:to_struct, action:pivot, action:split_column
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8, libs/blueprint_arch/src/blueprint_arch/schema_registry.py (ui_schema via ACTION_SCHEMAS)
# doc: .claude/rules/rules_persona_bioscientist.md#8, .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps


@register_action("unpivot", ui_schema={
    "label": "Unpivot (wide → long)",
    "category": "reshaping",
    "context": ["t2", "assembly"],
    "tags": ["melt", "pivot", "wide-to-long", "reshaping"],
    "params": {
        "index": {"widget": "column_selector", "multi": True, "label": "Index columns (kept as-is)", "required": True},
        "on": {"widget": "column_selector", "multi": True, "label": "Columns to unpivot (value columns)", "required": True},
        "variable_name": {"widget": "string", "label": "Variable column name", "required": False, "default": "variable"},
        "value_name": {"widget": "string", "label": "Value column name", "required": False, "default": "value"},
    },
})
def action_unpivot(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Unpivots (melts) a LazyFrame from wide to long format.
    Spec: { index: ["col1"], on: ["val1", "val2"], variable_name: "var", value_name: "val" }
    """
    index = spec.get("index", [])
    # ADR-012: Handle YAML 'on' boolean gotcha (key interpreted as True)
    on_cols = spec.get("on") or spec.get(True) or []

    variable_name = spec.get("variable_name", "variable")
    value_name = spec.get("value_name", "value")

    return lf.unpivot(on=on_cols, index=index, variable_name=variable_name, value_name=value_name)


@register_action("explode", ui_schema={
    "label": "Explode list column",
    "category": "reshaping",
    "context": ["t2", "assembly"],
    "tags": ["explode", "list", "reshaping", "rows"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "List columns to explode", "required": True},
    },
})
def action_explode(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Explodes list-like columns into multiple rows.
    Spec: { columns: ["col1"] }
    """
    columns = spec.get("columns", [])
    if not columns:
        return lf
    return lf.explode(columns)


@register_action("unnest")
def action_unnest(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Unnests struct columns into multiple columns.
    Spec: { columns: ["col1"] }
    """
    columns = spec.get("columns", [])
    if not columns:
        return lf
    return lf.unnest(columns)


@register_action("split_to_list")
def action_split_to_list(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Splits a string column into a List column.
    Spec: { columns: ["col1"], separator: "," }
    """
    columns = spec.get("columns", [])
    separator = spec.get("separator", ",")
    if not columns:
        return lf
    return lf.with_columns(pl.col(columns).str.split(separator))


@register_action("to_struct")
def action_to_struct(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Combines multiple columns into a struct.
    Spec: { columns: ["col1", "col2"], target_column: "my_struct" }
    """
    columns = spec.get("columns", [])
    target = spec.get("target_column")
    if not columns or not target:
        return lf
    return lf.with_columns(pl.struct(columns).alias(target)).drop(columns)


@register_action("pivot")
def action_pivot(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Pivots a LazyFrame from long to wide format (Materializes!).
    Spec: { index: ["col1"], on: "variable", values: "value", aggregate_function: "first" }
    NOTE: Pivot is NOT lazy in Polars. This will call .collect().
    """
    index = spec.get("index")
    on = spec.get("on")
    values = spec.get("values")
    aggregate_function = spec.get("aggregate_function", "first")

    # Pivot is not lazy, so we must collect.
    # To keep it semi-consistent with the pipeline, we return a new LazyFrame from the result.
    df = lf.collect().pivot(
        values=values,
        index=index,
        on=on,
        aggregate_function=aggregate_function
    )
    return df.lazy()


@register_action("split_column")
def action_split_column(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Split a string column into multiple new columns based on a delimiter.

    Usage in YAML:
      - action: "split_column"
        source: "some_col"
        new_columns: ["col_1", "col_2"]
        delimiter: ": "
        drop_source: true
    """
    # ADR-013 / ADR-001: Prioritize the resolved 'columns' list from DataWrangler
    columns = spec.get("columns", [])
    source = columns[0] if columns else spec.get(
        "source", spec.get("target_column"))

    new_columns = spec.get("new_columns", [])
    delimiter = spec.get("delimiter", spec.get("separator", " "))
    drop_source = spec.get("drop_source", False)

    if not source or not new_columns or source not in lf.collect_schema().names():
        return lf

    # Implementation: Use split to get a list, then extract columns.
    # The last column gets the 'remainder' (all remaining parts joined back)
    # to match typical 'split(sep, n)' behavior and satisfy the test case.

    n = len(new_columns)
    lf = lf.with_columns(
        pl.col(source).str.split(delimiter).alias("_split_list")
    )

    new_cols_exprs = []
    for i in range(n):
        col_name = new_columns[i]
        if i < n - 1:
            # Standard parts
            expr = pl.col("_split_list").list.get(i).alias(col_name)
        else:
            # Remainder part: slice from i to the end and join back
            # We only join if there's actually a remainder; otherwise null if list was too short
            expr = (
                pl.when(pl.col("_split_list").list.len() > i)
                .then(pl.col("_split_list").list.slice(i).list.join(delimiter))
                .otherwise(None)
                .alias(col_name)
            )
        new_cols_exprs.append(expr)

    lf = lf.with_columns(new_cols_exprs).drop("_split_list")

    if drop_source:
        lf = lf.drop(source)

    return lf
