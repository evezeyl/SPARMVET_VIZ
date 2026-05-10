import polars as pl
from typing import Dict, Any, List, Union
import os
from pathlib import Path
from transformer.actions.base import register_action
from utils.errors import TransformationError

# @deps
# provides: action:split_and_explode, action:derive_categories, action:split_column_to_parts, action:divide_columns
# consumes: libs/utils/src/utils/errors.py (TransformationError)
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8
# doc: .claude/rules/rules_persona_bioscientist.md#8, .claude/knowledge/architecture_decisions.md (ADR-078)
# @end_deps


@register_action("split_and_explode")
def action_split_and_explode(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Splits a string column by a separator and explodes it into multiple rows.
    """
    columns = spec.get("columns", [])
    separator = spec.get("separator", ",")

    # split_and_explode currently only supports one column at a time for safety
    # ADR-034: Flexible target resolution (handle scalar or list)
    target = columns[0] if (isinstance(columns, list)
                            and len(columns) > 0) else columns
    if not target:
        raise TransformationError(
            "action 'split_and_explode' missing required parameter 'columns'.",
            tip="Provide 'columns' (a single column name or list with one entry) in the YAML spec."
        )

    return lf.with_columns(
        pl.col(target).cast(pl.String).str.split(separator)
    ).explode(target)


@register_action("derive_categories")
def action_derive_categories(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    A lookup-based action that maps messy strings to clean categories
    using an external reference TSV.
    """
    columns = spec.get("columns", [])
    target_column = spec.get("target_column")
    separator = spec.get("separator", ", ")
    reference_file = spec.get("reference_file")
    lookup_left = spec.get("lookup_left")
    lookup_right = spec.get("lookup_right")
    extract_column = spec.get("extract_column")

    # Basic Validation
    if not all([reference_file, lookup_right, extract_column]):
        raise ValueError(
            f"'derive_categories' missing mandatory parameters (reference_file, lookup_right, extract_column). Spec: {spec}")

    if not Path(reference_file).exists():
        raise FileNotFoundError(f"Reference file not found: {reference_file}")

    # Identify source column
    if lookup_left:
        source_col = lookup_left
    else:
        source_col = columns if isinstance(columns, str) else columns[0]

    # 1. Load Reference Data
    ref_df = pl.read_csv(reference_file, separator="\t")
    ref_map = dict(zip(ref_df[lookup_right], ref_df[extract_column]))

    # 2. Vectorized Transformation
    def lookup_fn(s: str) -> Union[str, None]:
        if not s:
            return None
        parts = [p.strip() for p in s.split(separator.strip())]
        mapped = [ref_map.get(p) for p in parts if p in ref_map]
        return separator.join(sorted(list(set(mapped)))) if mapped else None

    return lf.with_columns([
        pl.col(source_col).map_elements(
            lookup_fn, return_dtype=pl.String).alias(target_column)
    ])


@register_action("split_column_to_parts")
def action_split_column_to_parts(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Splits a string column into multiple new columns using a separator.
    Spec: { column: "A/B", separator: "/", new_columns: ["A", "B"] }
    """
    source = spec.get("column")
    separator = spec.get("separator", "/")
    new_cols = spec.get("new_columns", [])

    if not source or not new_cols:
        raise TransformationError(
            "action 'split_column_to_parts' missing required parameters.",
            tip="Provide 'column' and 'new_columns' (list of target column names) in the YAML spec."
        )

    # Implementation: Use str.split_exact to get the parts
    # We cast to Float64 by default if possible to allow downstream math
    return lf.with_columns(
        pl.col(source).str.split_exact(separator, len(new_cols) - 1)
        .struct.rename_fields(new_cols)
        .alias("temp_struct")
    ).unnest("temp_struct")


@register_action("divide_columns")
def action_divide_columns(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Calculates the ratio between two columns.
    Spec: { numerator: "A", denominator: "B", new_column: "ratio" }
    """
    num = spec.get("numerator")
    den = spec.get("denominator")
    new_col = spec.get("new_column")

    if not num or not den or not new_col:
        raise TransformationError(
            "action 'divide_columns' missing required parameters.",
            tip="Provide 'numerator', 'denominator', and 'new_column' in the YAML spec."
        )

    # Safety: ensure numeric
    return lf.with_columns(
        (pl.col(num).cast(pl.Float64) / pl.col(den).cast(pl.Float64)).alias(new_col)
    )
