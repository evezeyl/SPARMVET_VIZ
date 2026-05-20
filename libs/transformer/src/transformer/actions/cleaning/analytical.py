import polars as pl
from typing import Dict, Any, List, Optional
from transformer.actions.base import register_action
from utils.errors import TransformationError

# @deps
# provides: action:window_agg, action:shift, action:fill_nulls_direction, action:sort, action:sample, action:cum_sum, action:cum_count, action:date_extract, action:date_truncate, action:list_slice, action:list_join, action:is_in, action:z_score, action:percentile, action:value_counts, action:describe_stats, action:select_by_pattern, action:horizontal_stats, action:any_horizontal, action:all_horizontal, action:interpolate
# consumes: libs/utils/src/utils/errors.py (TransformationError)
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8, libs/blueprint_arch/src/blueprint_arch/schema_registry.py (ui_schema via ACTION_SCHEMAS)
# doc: .claude/rules/rules_persona_bioscientist.md#8, .claude/knowledge/architecture_decisions.md (ADR-075, ADR-078)
# @end_deps


@register_action("window_agg", ui_schema={
    "label": "Window aggregation",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["window", "aggregation", "group", "analytical"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column to aggregate", "required": True, "dtype_filter": ["numeric"]},
        "partition_by": {"widget": "column_selector", "multi": True, "label": "Partition (group) by", "required": True},
        "function": {"widget": "enum", "label": "Aggregation function", "required": False, "default": "mean", "options": ["mean", "sum", "min", "max", "count", "median", "std"]},
        "target_column": {"widget": "string", "label": "Output column name", "required": False, "hint": "Defaults to {column}_{function}"},
    },
})
def action_window_agg(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Performs window-based aggregations (e.g. mean over a group).

    Args:
        column: The column to aggregate.
        partition_by: The column(s) to group by.
        function: The aggregation function (mean, sum, min, max, count).
        target_column: Optional name for the new column. Defaults to {column}_{function}.
    """
    col = spec.get("column")
    partition = spec.get("partition_by", [])
    func_name = spec.get("function", "mean")
    target = spec.get("target_column", f"{col}_{func_name}")

    if not col:
        raise TransformationError(
            "action 'window_agg' missing required parameter 'column'.",
            tip="Provide 'column' in the YAML spec."
        )

    # Map function names to Polars expressions
    mapping = {
        "mean": pl.col(col).mean(),
        "sum": pl.col(col).sum(),
        "min": pl.col(col).min(),
        "max": pl.col(col).max(),
        "count": pl.col(col).count(),
        "median": pl.col(col).median(),
        "std": pl.col(col).std(),
    }

    func_expr = mapping.get(func_name)
    if func_expr is None:
        raise TransformationError(
            f"action 'window_agg' unknown function '{func_name}'.",
            tip=f"Valid values for 'function': {list(mapping.keys())}."
        )

    return lf.with_columns(func_expr.over(partition).alias(target))


@register_action("shift", ui_schema={
    "label": "Shift (lag/lead)",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["lag", "lead", "shift", "time-series"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column", "required": True},
        "n": {"widget": "number", "label": "Steps (positive=lag, negative=lead)", "required": False, "default": 1},
        "target_column": {"widget": "string", "label": "Output column name", "required": False, "hint": "Defaults to {column}_shift_{n}"},
    },
})
def action_shift(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Shifts values by n steps (Lag/Lead).

    Args:
        column: Column to shift.
        n: Number of steps (positive for lag, negative for lead). Defaults to 1.
        target_column: Optional target name. Defaults to {column}_shift_{n}.
    """
    col = spec.get("column")
    n = spec.get("n", 1)
    target = spec.get("target_column", f"{col}_shift_{n}")

    if not col:
        raise TransformationError(
            "action 'shift' missing required parameter 'column'.",
            tip="Provide 'column' in the YAML spec."
        )

    return lf.with_columns(pl.col(col).shift(n).alias(target))


@register_action("fill_nulls_direction", ui_schema={
    "label": "Fill nulls by direction",
    "category": "cleaning",
    "context": ["t1", "t2"],
    "tags": ["null", "fill", "forward", "backward", "impute"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns", "required": True},
        "direction": {"widget": "enum", "label": "Fill direction", "required": False, "default": "forward", "options": ["forward", "backward"]},
    },
})
def action_fill_nulls_direction(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Fills nulls using forward or backward fill strategies.

    Args:
        columns: List of columns to fill.
        direction: 'forward' (FFILL) or 'backward' (BFILL). Defaults to 'forward'.
    """
    cols = spec.get("columns", [])
    direction = spec.get("direction", "forward")

    if not cols:
        raise TransformationError(
            "action 'fill_nulls_direction' missing required parameter 'columns'.",
            tip="Provide 'columns' (list) in the YAML spec."
        )

    return lf.with_columns([pl.col(c).fill_null(strategy=direction) for c in cols])


@register_action("sort", ui_schema={
    "label": "Sort rows",
    "category": "ordering",
    "context": ["t1", "t2", "assembly"],
    "tags": ["sort", "ordering"],
    "params": {
        "by": {"widget": "column_selector", "multi": True, "label": "Sort by columns (in order)", "required": False},
        "columns": {"widget": "column_selector", "multi": True, "label": "Sort by columns (fallback)", "required": False},
        "descending": {"widget": "bool", "label": "Descending", "required": False, "default": False},
    },
})
def action_sort(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Sorts the dataframe by one or more columns.

    Spec keys:
        by (or columns): column name or list of column names.
        descending: bool or list of bools. Defaults to False.

    'columns' accepted as alias for 'by' (backwards compatibility).
    """
    by = spec.get("by") or spec.get("columns", [])
    descending = spec.get("descending", False)

    if not by:
        raise TransformationError(
            "action 'sort' missing required parameter 'by' (or 'columns').",
            tip="Provide 'by' (list of column names) in the YAML spec."
        )

    return lf.sort(by, descending=descending)


@register_action("sample", ui_schema={
    "label": "Random sample",
    "category": "filtering",
    "context": ["t1", "t2"],
    "tags": ["sample", "random", "subset"],
    "params": {
        "fraction": {"widget": "number", "label": "Fraction of rows (0.0–1.0)", "required": False, "default": 0.1},
        "seed": {"widget": "number", "label": "Random seed (optional, for reproducibility)", "required": False},
    },
})
def action_sample(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Returns a random sample of rows.

    Args:
        fraction: Fraction of rows to return (0.0 to 1.0). Defaults to 0.1.
        seed: Optional random seed.
    """
    fraction = spec.get("fraction", 0.1)
    seed = spec.get("seed")

    return lf.collect().sample(fraction=fraction, seed=seed).lazy()


@register_action("cum_sum", ui_schema={
    "label": "Cumulative sum",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["cumulative", "sum", "running-total"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column", "required": True, "dtype_filter": ["numeric"]},
        "target_column": {"widget": "string", "label": "Output column name", "required": False, "hint": "Defaults to {column}_cumsum"},
    },
})
def action_cum_sum(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Calculates cumulative sum."""
    col = spec.get("column")
    target = spec.get("target_column", f"{col}_cumsum")
    return lf.with_columns(pl.col(col).cum_sum().alias(target))


@register_action("cum_count", ui_schema={
    "label": "Cumulative count",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["cumulative", "count", "running"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column", "required": True},
        "target_column": {"widget": "string", "label": "Output column name", "required": False, "hint": "Defaults to {column}_cumcount"},
    },
})
def action_cum_count(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Calculates cumulative count."""
    col = spec.get("column")
    target = spec.get("target_column", f"{col}_cumcount")
    return lf.with_columns(pl.col(col).cum_count().alias(target))


# --- Batch 2: Temporal ---

@register_action("date_extract", ui_schema={
    "label": "Extract date parts",
    "category": "temporal",
    "context": ["t1", "t2"],
    "tags": ["date", "temporal", "extract", "year", "month"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Date/Datetime column", "required": True},
        "parts": {"widget": "enum", "multi": True, "label": "Parts to extract", "required": False, "default": ["year"], "options": ["year", "month", "day", "week", "weekday", "hour"]},
    },
})
def action_date_extract(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Extracts parts of a date into new columns.

    Args:
        column: Date/Datetime column.
        parts: List of parts to extract (year, month, day, week, weekday, hour).
    """
    col = spec.get("column")
    parts = spec.get("parts", ["year"])

    if not col:
        raise TransformationError(
            "action 'date_extract' missing required parameter 'column'.",
            tip="Provide 'column' (a date/datetime column) in the YAML spec."
        )

    exprs = []
    for part in parts:
        if part == "year":
            exprs.append(pl.col(col).dt.year().alias(f"{col}_year"))
        elif part == "month":
            exprs.append(pl.col(col).dt.month().alias(f"{col}_month"))
        elif part == "day":
            exprs.append(pl.col(col).dt.day().alias(f"{col}_day"))
        elif part == "week":
            exprs.append(pl.col(col).dt.week().alias(f"{col}_week"))
        elif part == "weekday":
            exprs.append(pl.col(col).dt.weekday().alias(f"{col}_weekday"))
        elif part == "hour":
            exprs.append(pl.col(col).dt.hour().alias(f"{col}_hour"))

    return lf.with_columns(exprs)


@register_action("date_truncate", ui_schema={
    "label": "Truncate date",
    "category": "temporal",
    "context": ["t1", "t2"],
    "tags": ["date", "temporal", "truncate", "round"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Date column", "required": True},
        "every": {"widget": "string", "label": "Interval (e.g. 1mo, 1y, 1w, 1d)", "required": False, "default": "1mo"},
    },
})
def action_date_truncate(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Truncates dates to a given interval.

    Args:
        column: Date column.
        every: Interval string (e.g. '1mo', '1y', '1w').
    """
    col = spec.get("column")
    every = spec.get("every", "1mo")

    if not col:
        raise TransformationError(
            "action 'date_truncate' missing required parameter 'column'.",
            tip="Provide 'column' (a date column) in the YAML spec."
        )

    return lf.with_columns(pl.col(col).dt.truncate(every))


# --- Batch 3: List & Struct ---

@register_action("list_slice", ui_schema={
    "label": "List slice",
    "category": "list",
    "context": ["t1", "t2"],
    "tags": ["list", "slice", "subset"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "List column", "required": True},
        "offset": {"widget": "number", "label": "Start offset", "required": False, "default": 0},
        "length": {"widget": "number", "label": "Max length (leave blank for all)", "required": False},
        "target_column": {"widget": "string", "label": "Output column name (defaults to source)", "required": False},
    },
})
def action_list_slice(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Slices a list column."""
    col = spec.get("column")
    offset = spec.get("offset", 0)
    length = spec.get("length")
    target = spec.get("target_column", col)

    if not col:
        raise TransformationError(
            "action 'list_slice' missing required parameter 'column'.",
            tip="Provide 'column' (a list-type column) in the YAML spec."
        )

    return lf.with_columns(pl.col(col).list.slice(offset, length).alias(target))


@register_action("list_join", ui_schema={
    "label": "List join to string",
    "category": "list",
    "context": ["t1", "t2"],
    "tags": ["list", "join", "string", "concat"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "List column", "required": True},
        "separator": {"widget": "string", "label": "Separator", "required": False, "default": ";"},
        "target_column": {"widget": "string", "label": "Output column name (defaults to source)", "required": False},
    },
})
def action_list_join(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Joins a list column into a string."""
    col = spec.get("column")
    separator = spec.get("separator", ";")
    target = spec.get("target_column", col)

    if not col:
        raise TransformationError(
            "action 'list_join' missing required parameter 'column'.",
            tip="Provide 'column' (a list-type column) in the YAML spec."
        )

    return lf.with_columns(pl.col(col).list.join(separator).alias(target))


@register_action("is_in", ui_schema={
    "label": "Filter: value is in list",
    "category": "filtering",
    "context": ["t1", "t2"],
    "tags": ["filter", "set", "whitelist"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column", "required": True},
        "values": {"widget": "string", "label": "Allowed values (comma-separated)", "required": True},
    },
})
def action_is_in(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Filters rows where column value is in a list."""
    col = spec.get("column")
    values = spec.get("values", [])

    if not col or not values:
        raise TransformationError(
            "action 'is_in' missing required parameters.",
            tip="Provide 'column' and 'values' (list) in the YAML spec."
        )

    return lf.filter(pl.col(col).is_in(values))


# --- Batch 4: Advanced Analytical & Stats ---

@register_action("z_score", ui_schema={
    "label": "Z-score standardize",
    "category": "statistical",
    "context": ["t1", "t2"],
    "tags": ["zscore", "standardize", "normalize", "statistical"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Numeric columns", "required": True, "dtype_filter": ["numeric"]},
    },
})
def action_z_score(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Standardizes columns (z-score)."""
    cols = spec.get("columns", [])
    if not cols:
        raise TransformationError(
            "action 'z_score' missing required parameter 'columns'.",
            tip="Provide 'columns' (list) in the YAML spec."
        )
    return lf.with_columns([
        ((pl.col(c) - pl.col(c).mean()) / pl.col(c).std()).alias(f"{c}_zscore")
        for c in cols
    ])


@register_action("percentile", ui_schema={
    "label": "Percentile rank",
    "category": "statistical",
    "context": ["t1", "t2"],
    "tags": ["percentile", "rank", "statistical"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Numeric column", "required": True, "dtype_filter": ["numeric"]},
        "target_column": {"widget": "string", "label": "Output column name", "required": False, "hint": "Defaults to {column}_percentile"},
    },
})
def action_percentile(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Calculates percentile rank."""
    col = spec.get("column")
    target = spec.get("target_column", f"{col}_percentile")
    if not col:
        raise TransformationError(
            "action 'percentile' missing required parameter 'column'.",
            tip="Provide 'column' in the YAML spec."
        )
    return lf.with_columns(pl.col(col).rank(method="average", descending=False).alias(target) / pl.count())


@register_action("value_counts", ui_schema={
    "label": "Value counts",
    "category": "analytical",
    "context": ["t2"],
    "tags": ["frequency", "count", "distribution", "analytical"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Column", "required": True},
    },
})
def action_value_counts(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Returns frequency counts of a column."""
    col = spec.get("column")
    if not col:
        raise TransformationError(
            "action 'value_counts' missing required parameter 'column'.",
            tip="Provide 'column' in the YAML spec."
        )
    return lf.collect().select(pl.col(col).value_counts()).unnest(col).lazy()


@register_action("describe_stats", ui_schema={
    "label": "Describe (summary statistics)",
    "category": "analytical",
    "context": ["t2"],
    "tags": ["describe", "summary", "statistics", "eda"],
    "params": {},
})
def action_describe_stats(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Generates summary statistics."""
    # Note: describe() is an eager operation
    return lf.collect().describe().lazy()


@register_action("select_by_pattern", ui_schema={
    "label": "Select columns by pattern",
    "category": "selection",
    "context": ["t1", "t2"],
    "tags": ["columns", "selection", "pattern", "regex"],
    "params": {
        "pattern": {"widget": "string", "label": "Column name regex pattern", "required": True, "hint": "e.g. gene_.* selects all columns starting with 'gene_'"},
    },
})
def action_select_by_pattern(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Selects columns by regex pattern."""
    pattern = spec.get("pattern")
    if not pattern:
        raise TransformationError(
            "action 'select_by_pattern' missing required parameter 'pattern'.",
            tip="Provide 'pattern' (a regex string) in the YAML spec."
        )
    return lf.select(pl.col(f"^{pattern}$"))


# --- Batch 5: Niche / Horizontal ---

@register_action("horizontal_stats", ui_schema={
    "label": "Horizontal stats (row-wise)",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["horizontal", "row", "aggregate", "sum", "min", "max"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns to aggregate row-wise", "required": True, "dtype_filter": ["numeric"]},
        "operation": {"widget": "enum", "label": "Operation", "required": False, "default": "sum", "options": ["sum", "min", "max", "mean"]},
        "target_column": {"widget": "string", "label": "Output column name", "required": False, "hint": "Defaults to horizontal_{operation}"},
    },
})
def action_horizontal_stats(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Horizontal math across columns."""
    cols = spec.get("columns", [])
    operation = spec.get("operation", "sum")
    target = spec.get("target_column", f"horizontal_{operation}")

    if not cols:
        raise TransformationError(
            "action 'horizontal_stats' missing required parameter 'columns'.",
            tip="Provide 'columns' (list) in the YAML spec."
        )

    if operation == "sum":
        expr = pl.sum_horizontal(cols)
    elif operation == "min":
        expr = pl.min_horizontal(cols)
    elif operation == "max":
        expr = pl.max_horizontal(cols)
    elif operation == "mean":
        expr = pl.mean_horizontal(cols)
    else:
        raise TransformationError(
            f"action 'horizontal_stats' unknown operation '{operation}'.",
            tip="Valid values for 'operation': sum, min, max, mean."
        )

    return lf.with_columns(expr.alias(target))


@register_action("any_horizontal", ui_schema={
    "label": "Any horizontal (row OR)",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["horizontal", "boolean", "any", "row"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Boolean columns", "required": True},
        "target_column": {"widget": "string", "label": "Output column name", "required": True},
    },
})
def action_any_horizontal(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Checks if any column in row is True."""
    cols = spec.get("columns", [])
    target = spec.get("target_column")
    if not cols or not target:
        raise TransformationError(
            "action 'any_horizontal' missing required parameters.",
            tip="Provide 'columns' (list) and 'target_column' in the YAML spec."
        )
    return lf.with_columns(pl.any_horizontal(cols).alias(target))


@register_action("all_horizontal", ui_schema={
    "label": "All horizontal (row AND)",
    "category": "analytical",
    "context": ["t1", "t2"],
    "tags": ["horizontal", "boolean", "all", "row"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Boolean columns", "required": True},
        "target_column": {"widget": "string", "label": "Output column name", "required": True},
    },
})
def action_all_horizontal(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Checks if all columns in row are True."""
    cols = spec.get("columns", [])
    target = spec.get("target_column")
    if not cols or not target:
        raise TransformationError(
            "action 'all_horizontal' missing required parameters.",
            tip="Provide 'columns' (list) and 'target_column' in the YAML spec."
        )
    return lf.with_columns(pl.all_horizontal(cols).alias(target))


@register_action("interpolate", ui_schema={
    "label": "Interpolate missing values",
    "category": "cleaning",
    "context": ["t1", "t2"],
    "tags": ["interpolate", "impute", "missing", "numeric"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Numeric columns to interpolate", "required": True, "dtype_filter": ["numeric"]},
    },
})
def action_interpolate(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Linearly interpolates missing values."""
    cols = spec.get("columns", [])
    if not cols:
        raise TransformationError(
            "action 'interpolate' missing required parameter 'columns'.",
            tip="Provide 'columns' (list) in the YAML spec."
        )
    return lf.with_columns(pl.col(cols).interpolate())
