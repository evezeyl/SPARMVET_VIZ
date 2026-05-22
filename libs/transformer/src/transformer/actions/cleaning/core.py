import polars as pl
from typing import Dict, Any, List, Union
from transformer.actions.base import register_action
from ...utils.naming import clean_column_header

# @deps
# provides: action:fill_nulls, action:drop_nulls, action:replace_values, action:rename, action:drop_duplicates, action:unique_rows, action:recode_values, action:sanitize_column_names, action:keep_columns, action:drop_columns, action:strip_whitespace, action:round_numeric, action:filter_range, action:add_constant, action:filter_eq, action:rename_columns, action:unique
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8, libs/blueprint_arch/src/blueprint_arch/schema_registry.py (ui_schema via ACTION_SCHEMAS)
# doc: .claude/rules/rules_persona_bioscientist.md#8, .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps

# --- From null_handling.py ---


@register_action("fill_nulls", ui_schema={
    "label": "Fill nulls",
    "category": "cleaning",
    "context": ["t1", "t2"],
    "tags": ["null", "cleaning", "imputation"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns", "required": True},
        "value": {"widget": "column_or_literal", "label": "Fill value", "required": True},
    },
    "description": "Replace null values in one or more columns with a fixed literal; prefer `coalesce` when the fill source is another column.",
    "yaml_example": "- action: fill_nulls\n  columns: [sample_id, country]\n  value: Unknown",
    "wraps": [{"lib": "polars", "attr_path": ["Expr", "fill_null"]}],
})
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


@register_action("drop_nulls", ui_schema={
    "label": "Drop null rows",
    "category": "cleaning",
    "context": ["t1", "t2"],
    "tags": ["null", "cleaning", "row-filter"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns (any null → drop row)", "required": False, "hint": "Leave empty to drop rows with any null"},
    },
    "description": "Drop rows where any of the listed columns are null; leave columns empty to drop rows with any null across all columns.",
    "yaml_example": "- action: drop_nulls\n  columns: [sample_id, collection_date]",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "drop_nulls"]}],
})
def action_drop_nulls(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Drops rows where any of the specified columns are null.
    """
    columns = spec.get("columns", [])
    return lf.drop_nulls(subset=columns)


@register_action("replace_values", ui_schema={
    "label": "Replace values",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["replace", "values", "recode", "string"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns", "required": True},
        "to_replace": {"widget": "string", "label": "Values to replace (YAML list)", "required": True, "hint": "[old_val1, old_val2]"},
        "new_value": {"widget": "column_or_literal", "label": "Replacement value", "required": True},
    },
    "description": "Replace a specific set of values across one or more columns with a single replacement; use `recode_values` for rule-based conditional remapping.",
    "yaml_example": "- action: replace_values\n  columns: [species]\n  to_replace: [Calf, calf]\n  new_value: Bovine_calf",
    "wraps": [{"lib": "polars", "attr_path": ["Expr", "replace"]}],
})
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

@register_action("rename", ui_schema={
    "label": "Rename column",
    "category": "renaming",
    "context": ["t1", "t2", "assembly"],
    "tags": ["rename", "column", "naming"],
    "params": {
        "columns": {"widget": "column_selector", "multi": False, "label": "Source column", "required": False},
        "new_name": {"widget": "string", "label": "New name", "required": False},
        "mapping": {"widget": "string", "label": "Rename mapping (YAML dict old: new)", "required": False, "hint": "{old_name: new_name, ...}"},
    },
    "description": "Rename one or more columns; use `mapping` for bulk renames, or `columns` + `new_name` for a single column.",
    "yaml_example": "- action: rename\n  mapping: {old_col: new_col, other_col: clean_col}",
})
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

@register_action("drop_duplicates", ui_schema={
    "label": "Drop duplicates",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["dedup", "unique", "cleaning"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Subset columns (leave empty for all)", "required": False},
        "maintain_order": {"widget": "enum", "label": "Maintain order", "required": False, "default": False, "options": [True, False]},
    },
    "description": "Remove duplicate rows based on a column subset; leave columns empty to deduplicate on all columns.",
    "yaml_example": "- action: drop_duplicates\n  columns: [sample_id]\n  maintain_order: true",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "unique"]}],
})
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


@register_action("unique_rows", ui_schema={
    "label": "Unique rows (all columns)",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["dedup", "unique", "cleaning"],
    "params": {
        "maintain_order": {"widget": "enum", "label": "Maintain order", "required": False, "default": True, "options": [True, False]},
    },
    "description": "Remove rows that are completely identical across all columns; equivalent to drop_duplicates with no column subset.",
    "yaml_example": "- action: unique_rows\n  maintain_order: true",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "unique"]}],
})
def action_unique_rows(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Drops duplicate rows based on ALL columns (subset=None).
    Polar default for unique() is subset=None if not provided.
    """
    maintain_order = spec.get("maintain_order", True)
    return lf.unique(subset=None, maintain_order=maintain_order)


@register_action("recode_values", ui_schema={
    "label": "Recode values",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["recode", "categorize", "conditional", "clean"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Source column", "required": True},
        "new_column": {"widget": "string", "label": "Output column name (leave blank to overwrite)", "required": False},
        "rules": {"widget": "string", "label": "Rules (YAML list of {matches/starts_with/…: val, value: out})", "required": True, "hint": "[{matches: 'S', value: 0}, {default: 1}]"},
    },
    "description": "Remap values in a column via a rule chain (exact match, prefix, suffix, substring, default); more expressive than `replace_values` for categorical cleaning.",
    "yaml_example": "- action: recode_values\n  column: resistance\n  new_column: resistance_binary\n  rules:\n    - matches: Susceptible\n      value: 0\n    - matches_any: [Resistant, Intermediate]\n      value: 1\n    - default: null",
})
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


@register_action("sanitize_column_names", ui_schema={
    "label": "Sanitize column names",
    "category": "renaming",
    "context": ["t1"],
    "tags": ["rename", "snake_case", "clean", "naming"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns to sanitize (leave empty for all)", "required": False},
    },
    "description": "Convert column names to snake_case using the project naming utility; run at the start of Tier 1 when ingesting external TSVs with inconsistent headers.",
    "yaml_example": "- action: sanitize_column_names\n  columns: []",
})
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

@register_action("keep_columns", ui_schema={
    "label": "Keep columns",
    "category": "selection",
    "context": ["t1", "t2", "assembly"],
    "tags": ["columns", "selection", "projection"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns to keep", "required": True},
    },
    "description": "Project the frame down to a named set of columns; primary keys are always retained; prefer `drop_columns` to remove individual unwanted columns.",
    "yaml_example": "- action: keep_columns\n  columns: [sample_id, year, country, resistance_class]",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "select"]}],
})
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


@register_action("drop_columns", ui_schema={
    "label": "Drop columns",
    "category": "selection",
    "context": ["t1", "t2", "assembly"],
    "tags": ["columns", "selection", "removal"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns to drop", "required": True},
    },
    "description": "Remove specific columns from the frame; primary keys are protected from accidental removal.",
    "yaml_example": "- action: drop_columns\n  columns: [intermediate_col, temp_flag]",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "drop"]}],
})
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

@register_action("strip_whitespace", ui_schema={
    "label": "Strip whitespace",
    "category": "cleaning",
    "context": ["t1", "t2"],
    "tags": ["string", "cleaning", "whitespace"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "String columns", "required": False, "hint": "Leave empty to auto-target all String columns"},
    },
    "description": "Remove leading/trailing whitespace and quotes from string columns; leave columns empty to auto-target all String columns in the frame.",
    "yaml_example": "- action: strip_whitespace\n  columns: [species, country]",
})
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


@register_action("round_numeric", ui_schema={
    "label": "Round numeric",
    "category": "numeric",
    "context": ["t1", "t2", "assembly"],
    "tags": ["numeric", "round", "precision"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Numeric columns", "required": True, "dtype_filter": ["numeric"]},
        "decimals": {"widget": "number", "label": "Decimal places", "required": False, "default": 2},
    },
    "description": "Round float columns to a fixed number of decimal places; useful before plotting when floating-point noise pollutes axis labels.",
    "yaml_example": "- action: round_numeric\n  columns: [identity_pct, coverage_pct]\n  decimals: 1",
    "wraps": [{"lib": "polars", "attr_path": ["Expr", "round"]}],
})
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


@register_action("filter_range", ui_schema={
    "label": "Filter by range",
    "category": "filtering",
    "context": ["t1", "t2"],
    "tags": ["numeric", "filter", "range", "cleaning"],
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "filter"]}],
    "params": {
        "columns": {"widget": "column_selector", "multi": False, "label": "Column", "required": True, "dtype_filter": ["numeric"]},
        "min": {"widget": "number", "label": "Min value (inclusive)", "required": False},
        "max": {"widget": "number", "label": "Max value (inclusive)", "required": False},
    },
    "description": "Keep rows where a numeric column falls within an inclusive range; use `filter_eq` for exact-value filtering or `is_in` for a discrete set.",
    "yaml_example": "- action: filter_range\n  columns: identity\n  min: 90\n  max: 100",
})
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


@register_action("add_constant", ui_schema={
    "label": "Add constant column",
    "category": "derivation",
    "context": ["t1", "t2", "assembly"],
    "tags": ["column", "literal", "derivation"],
    "params": {
        "new_column": {"widget": "string", "label": "New column name", "required": True},
        "value": {"widget": "column_or_literal", "label": "Constant value", "required": True},
    },
    "description": "Add a new column with a constant literal value across all rows; useful for tagging rows with a source label or pipeline version.",
    "yaml_example": "- action: add_constant\n  new_column: data_source\n  value: NORM_2025",
    "wraps": [{"lib": "polars", "attr_path": ["lit"]}],
})
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


@register_action("filter_eq", ui_schema={
    "label": "Filter equal",
    "category": "filtering",
    "context": ["t1", "t2"],
    "tags": ["filter", "equality"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column", "required": False},
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns (fallback, uses first)", "required": False, "hint": "Alternative to 'column'; uses first element"},
        "value": {"widget": "column_or_literal", "label": "Value", "required": True},
    },
    "description": "Keep rows where a column equals an exact value; use `is_in` for filtering to a set of allowed values.",
    "yaml_example": "- action: filter_eq\n  column: country\n  value: Norway",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "filter"]}],
})
def action_filter_eq(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Equality filter."""
    col = spec.get("column", spec.get("columns", [None])[0])
    val = spec.get("value")
    if not col:
        return lf
    return lf.filter(pl.col(col) == val)


@register_action("rename_columns", ui_schema={
    "label": "Rename columns",
    "category": "renaming",
    "context": ["t1", "t2", "assembly"],
    "tags": ["rename", "columns"],
    "params": {
        "mapping": {"widget": "string", "label": "Rename mapping (YAML dict old: new)", "required": False, "hint": "e.g. {old_name: new_name}"},
        "columns": {"widget": "column_selector", "multi": True, "label": "Source columns (list form)", "required": False},
        "new_names": {"widget": "string", "label": "New names (comma-separated, same order as columns)", "required": False},
    },
    "description": "Rename columns via a mapping dict or parallel lists; alias for `rename` with explicit list/zip support.",
    "yaml_example": "- action: rename_columns\n  mapping: {Sample_ID: sample_id, CollectionYear: year}",
})
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


@register_action("unique", ui_schema={
    "label": "Unique (alias for drop_duplicates)",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["dedup", "unique", "cleaning"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Subset columns (leave empty for all)", "required": False},
        "maintain_order": {"widget": "enum", "label": "Maintain order", "required": False, "default": False, "options": [True, False]},
    },
    "description": "Alias for drop_duplicates; remove duplicate rows based on a column subset or all columns.",
    "yaml_example": "- action: unique\n  columns: [sample_id, gene]",
    "wraps": [{"lib": "polars", "attr_path": ["LazyFrame", "unique"]}],
})
def action_unique(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Alias for drop_duplicates."""
    return action_drop_duplicates(lf, spec)
