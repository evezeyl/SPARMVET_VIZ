# @deps
# provides: action:regex_extract, action:cast, action:coalesce, action:label_if, action:mutate, action:regex_replace, action:null_if
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8
# doc: .claude/rules/rules_persona_bioscientist.md#8
# @end_deps
import polars as pl
from typing import Dict, Any
from transformer.actions.base import register_action


@register_action("regex_extract")
def action_regex_extract(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Extracts a substring based on a Regex pattern with capture groups.

    Usage in YAML:
      - action: "regex_extract"
        source: "some_col"
        pattern: r"v(\d+)\.(\d+)"
        target_column: "major_version"
        group: 1
    """
    source = spec.get("source", spec.get("target_column"))
    pattern = spec.get("pattern")
    target = spec.get("target_column")
    group = spec.get("group", 1)

    if not source or not pattern or not target:
        return lf

    # Implementation: Use str.extract to generate a new column
    return lf.with_columns(
        pl.col(source).str.extract(pattern, group_index=group).alias(target)
    )


@register_action("cast")
def action_cast(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Casts columns to a specific Polars data type.
    Spec: { columns: ["col1"], dtype: "Int64" }
    Supported dtypes: Int64, Float64, String, Boolean, Date, Categorical
    """
    columns = spec.get("columns", [])
    dtype_str = spec.get("dtype")

    dtype_map = {
        "Int64": pl.Int64,
        "Float64": pl.Float64,
        "String": pl.String,
        "Boolean": pl.Boolean,
        "Date": pl.Date,
        "Categorical": pl.Categorical
    }

    target_dtype = dtype_map.get(dtype_str)
    if not target_dtype:
        raise ValueError(
            f"Unsupported dtype for cast: {dtype_str}. Supported: {list(dtype_map.keys())}")

    return lf.with_columns(pl.col(columns).cast(target_dtype))


@register_action("coalesce")
def action_coalesce(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Fills nulls in the first column using values from subsequent columns in the list.
    Spec: { columns: ["target", "fallback1", "fallback2"] }
    """
    columns = spec.get("columns", [])
    if len(columns) < 2:
        return lf

    return lf.with_columns(pl.coalesce(columns).alias(columns[0]))


@register_action("label_if")
def action_label_if(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Conditional labeling based on a predicate.
    Spec: { 
        column: "source_col", 
        new_column: "label_col", 
        predicate: ">=", 
        value: 50, 
        then: "High", 
        otherwise: "Low" 
    }
    """
    col = spec.get("column")
    new_col = spec.get("new_column")
    pred = spec.get("predicate")
    val = spec.get("value")
    then_val = spec.get("then")
    else_val = spec.get("otherwise")

    if not all([col, new_col, pred, val]):
        return lf

    if pred == ">":
        expr = pl.when(pl.col(col) > val).then(
            pl.lit(then_val)).otherwise(pl.lit(else_val))
    elif pred == ">=":
        expr = pl.when(pl.col(col) >= val).then(
            pl.lit(then_val)).otherwise(pl.lit(else_val))
    elif pred == "<":
        expr = pl.when(pl.col(col) < val).then(
            pl.lit(then_val)).otherwise(pl.lit(else_val))
    elif pred == "<=":
        expr = pl.when(pl.col(col) <= val).then(
            pl.lit(then_val)).otherwise(pl.lit(else_val))
    elif pred == "==":
        expr = pl.when(pl.col(col) == val).then(
            pl.lit(then_val)).otherwise(pl.lit(else_val))
    elif pred == "!=":
        expr = pl.when(pl.col(col) != val).then(
            pl.lit(then_val)).otherwise(pl.lit(else_val))
    else:
        return lf

    return lf.with_columns(expr.alias(new_col))


@register_action("mutate")
def action_mutate(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Evaluates a Polars-compatible expression and assigns it to a new column.
    Spec: { column: "new_col", expression: "pl.col('old') * 2" }
    """
    target = spec.get("column", spec.get("target_column"))
    expr_str = spec.get("expression")

    if not target or not expr_str:
        return lf

    # Evaluate the expression string within Polars context
    # Note: We assume the expression is a valid Polars string expression using pl.
    try:
        expr = eval(expr_str, {"pl": pl})
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expr_str}': {e}")

    return lf.with_columns(expr.alias(target))


@register_action("regex_replace")
def action_regex_replace(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Regex-based string replacement."""
    cols = spec.get("columns", [])
    pattern = spec.get("pattern")
    value = spec.get("value", "")
    if not cols or not pattern:
        return lf
    return lf.with_columns(pl.col(cols).str.replace_all(pattern, value))


@register_action("null_if")
def action_null_if(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Converts a specific value to null."""
    cols = spec.get("columns", [])
    value = spec.get("value")
    if not cols:
        return lf
    return lf.with_columns(pl.when(pl.col(cols) == value).then(None).otherwise(pl.col(cols)))
