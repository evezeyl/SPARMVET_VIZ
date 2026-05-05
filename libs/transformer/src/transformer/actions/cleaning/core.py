import polars as pl
from typing import Dict, Any, List, Union
from transformer.actions.base import register_action
from ...utils.naming import clean_column_header

# @deps
# provides: action:fill_nulls, action:drop_nulls, action:replace_values, action:rename, action:drop_duplicates, action:unique_rows, action:recode_values, action:sanitize_column_names, action:keep_columns, action:drop_columns, action:strip_whitespace, action:round_numeric, action:filter_range, action:add_constant, action:filter_eq, action:rename_columns, action:unique
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8
# doc: .claude/rules/rules_persona_bioscientist.md#8
# @end_deps

# --- From null_handling.py ---


@register_action("fill_nulls")
def action_fill_nulls(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Replaces null values with a specified value across one or more columns.
    Requires 'value' in spec.
    """
    columns = spec.get("columns", [])
    fill_value = spec.get("value")
    if fill_value is None:
        raise ValueError(
            f"'fill_nulls' action requires a 'value' parameter. Spec: {spec}")
    return lf.with_columns(pl.col(columns).fill_null(fill_value))


@register_action("drop_nulls")
def action_drop_nulls(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Drops rows where any of the specified columns are null.
    """
    columns = spec.get("columns", [])
    return lf.drop_nulls(subset=columns)


@register_action("replace_values")
def action_replace_values(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Replaces a specific list of strings with a new value across multiple columns.
    Requires 'to_replace' (list) and 'new_value' in spec.
    """
    columns = spec.get("columns", [])
    to_replace = spec.get("to_replace")
    new_value = spec.get("new_value")

    if not isinstance(to_replace, list):
        raise ValueError(
            f"'replace_values' action requires 'to_replace' to be a list. Spec: {spec}")

    mapping = {old_val: new_value for old_val in to_replace}
    return lf.with_columns(pl.col(columns).replace(mapping, default=pl.col(columns)))


# --- From renaming.py ---

@register_action("rename")
def action_rename(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Renames columns according to spec.
    Supports:
        mapping: Dict[str, str]  - Multiple renames at once.
        new_name: str, columns: str or List[str] - 1:1 rename.
    """
    mapping = spec.get("mapping")
    if mapping:
        return lf.rename(mapping)

    new_name = spec.get("new_name")
    if not new_name:
        raise ValueError(
            f"'rename' action requires 'mapping' or 'new_name' parameter. Spec: {spec}")

    columns = spec.get("columns", [])
    if not columns:
        # Check for 'target_column' alias used in some scripts
        columns = spec.get("target_column")

    if not columns:
        raise ValueError(
            f"'rename' action missing source column(s). Spec: {spec}")

    # Convert to single string for the dictionary mapping if it's a single-item list
    target = columns if isinstance(columns, str) else columns[0]
    return lf.rename({target: new_name})


# --- From duplicates.py ---

@register_action("drop_duplicates")
def action_drop_duplicates(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Drops duplicate rows based on one or more columns as a subset.
    The new DataWrangler architecture allows passing multiple columns to a single
    unique() call, maximizing Polars' parallel execution performance.
    """
    columns = spec.get("columns", [])
    maintain_order = spec.get("maintain_order", False)
    # We use subset=columns to target the entire resolved set.
    if maintain_order:
        return lf.unique(subset=columns, maintain_order=True)
    return lf.unique(subset=columns)


@register_action("unique_rows")
def action_unique_rows(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Drops duplicate rows based on ALL columns (subset=None).
    Polar default for unique() is subset=None if not provided.
    """
    maintain_order = spec.get("maintain_order", True)
    return lf.unique(subset=None, maintain_order=maintain_order)


@register_action("recode_values")
def action_recode_values(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Recodes values in a column based on a series of predicates.
    Spec: {
        column: "source",
        new_column: "target",
        rules: [
           { matches: "Susceptible", value: 0 },
           { starts_with: "unknown", value: null },
           { default: 1 }
        ]
    }
    """
    col = spec.get("column")
    new_col = spec.get("new_column")
    rules = spec.get("rules", [])

    if not col or not rules:
        return lf

    target = new_col if new_col else col

    # 1. Resolve default
    default_val = None
    for rule in rules:
        if "default" in rule:
            default_val = rule["default"]
            break

    # 2. Build When/Then chain
    expr = None
    for rule in rules:
        predicate = None
        if "matches" in rule:
            predicate = pl.col(col) == rule["matches"]
        elif "matches_any" in rule:
            predicate = pl.col(col).is_in(rule["matches_any"])
        elif "starts_with" in rule:
            predicate = pl.col(col).cast(
                pl.String).str.starts_with(rule["starts_with"])
        elif "ends_with" in rule:
            predicate = pl.col(col).cast(
                pl.String).str.ends_with(rule["ends_with"])
        elif "contains" in rule:
            predicate = pl.col(col).cast(
                pl.String).str.contains(rule["contains"])

        if predicate is not None:
            if expr is None:
                expr = pl.when(predicate).then(pl.lit(rule["value"]))
            else:
                expr = expr.when(predicate).then(pl.lit(rule["value"]))

    if expr is not None:
        expr = expr.otherwise(pl.lit(default_val))
    else:
        expr = pl.lit(default_val)

    return lf.with_columns(expr.alias(target))

# --- From naming.py ---


@register_action("sanitize_column_names")
def action_sanitize_column_names(lf: pl.LazyFrame, spec: Dict[str, Any] = {}) -> pl.LazyFrame:
    """
    Sanitizes column names into safe snake_case using the project-standard utility.
    Useful for ingesting raw data from external sources that don't match the manifest keys.
    """
    columns = spec.get("columns", [])
    if not columns or columns == "all":
        cols_to_fix = lf.collect_schema().names()
    else:
        cols_to_fix = columns if isinstance(columns, list) else [columns]

    rename_map = {col: clean_column_header(col) for col in cols_to_fix}
    return lf.rename(rename_map)


# --- From selection.py ---

@register_action("keep_columns")
def action_keep_columns(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Selects only the specified columns, ensuring that primary keys defined in the schema
    are always preserved to prevent join breakage.
    """
    columns = spec.get("columns", [])
    # 1. Verification: Use Lazy execution pattern for schema checks
    schema = lf.collect_schema()
    existing_cols = schema.names()
    missing = [c for c in columns if c not in existing_cols]
    if missing:
        raise ValueError(
            f"Action 'keep_columns' failed: The following columns were not found in the dataset: {missing}. "
            f"Ensure you are using the sanitized column names (snake_case)."
        )

    # 2. Safety: Resolve primary keys from rule metadata
    pks = spec.get("__metadata__", {}).get("primary_keys", [])

    # Merge requested columns with primary keys, ensuring PKs come first
    final_selection = list(dict.fromkeys(pks + columns))

    return lf.select(final_selection)


@register_action("drop_columns")
def action_drop_columns(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Drops the specified columns, but prevents dropping primary keys.
    """
    requested_drops = spec.get("columns", [])
    if isinstance(requested_drops, str):
        requested_drops = [requested_drops]

    # Safety: Fetch PKs
    pks = spec.get("__metadata__", {}).get("primary_keys", [])

    # Filter out PKs from dropping
    safe_drops = [c for c in requested_drops if c not in pks]

    if len(safe_drops) < len(requested_drops):
        print(
            f"Warning: Primary keys {set(requested_drops) & set(pks)} were protected from dropping.")

    # Only drop if they exist
    existing_cols = lf.collect_schema().names()
    final_drops = [c for c in safe_drops if c in existing_cols]

    if not final_drops:
        return lf

    return lf.drop(final_drops)


# --- From cleaning.py ---

@register_action("strip_whitespace")
def action_strip_whitespace(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Strips leading and trailing whitespace from string columns.
    If 'columns' is not provided in spec, targets all pl.String columns.
    """
    columns = spec.get("columns", [])

    if not columns:
        # Smart Selection: auto-target String columns
        schema = lf.collect_schema()
        process_cols = [name for name,
                        dtype in schema.items() if dtype == pl.String]
    else:
        process_cols = columns if isinstance(columns, list) else [columns]

    if not process_cols:
        return lf

    # Aggressively strip multiple characters (whitespace, tabs, newlines, and flanking quotes)
    return lf.with_columns(pl.col(process_cols).str.strip_chars(' \t\n\r"'))


@register_action("round_numeric")
def action_round_numeric(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Rounds numeric columns to a specified number of decimal places.
    Spec: { columns: ["col1"], decimals: 2 }
    """
    columns = spec.get("columns", [])
    decimals = spec.get("decimals", 2)

    if not columns:
        return lf

    return lf.with_columns(pl.col(columns).round(decimals))


@register_action("filter_range")
def action_filter_range(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Filters rows based on a numeric range (inclusive).
    Spec: { columns: ["col1"], min: 0.0, max: 100.0 }
    Note: Always operates on the first column in the list if multiple provided.
    """
    columns = spec.get("columns", [])
    if not columns:
        return lf

    target = columns[0]
    min_val = spec.get("min")
    max_val = spec.get("max")

    if min_val is not None:
        lf = lf.filter(pl.col(target) >= min_val)
    if max_val is not None:
        lf = lf.filter(pl.col(target) <= max_val)

    return lf


@register_action("add_constant")
def action_add_constant(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Adds a new column with a constant (literal) value.
    Spec: { new_column: "status", value: "Present" }
    """
    new_col = spec.get("new_column")
    value = spec.get("value")
    if not new_col:
        raise ValueError(
            "'add_constant' action requires 'new_column' parameter.")
    return lf.with_columns(pl.lit(value).alias(new_col))


@register_action("filter_eq")
def action_filter_eq(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Equality filter."""
    col = spec.get("column", spec.get("columns", [None])[0])
    val = spec.get("value")
    if not col:
        return lf
    return lf.filter(pl.col(col) == val)


@register_action("rename_columns")
def action_rename_columns(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Alias for rename that supports columns + new_names lists."""
    mapping = spec.get("mapping")
    if mapping:
        return lf.rename(mapping)

    cols = spec.get("columns", [])
    new_names = spec.get("new_names", [])
    if cols and new_names:
        return lf.rename(dict(zip(cols, new_names)))
    return action_rename(lf, spec)


@register_action("unique")
def action_unique(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Alias for drop_duplicates."""
    return action_drop_duplicates(lf, spec)
