# @deps
# provides: action:regex_extract, action:cast, action:coalesce, action:label_if, action:mutate, action:regex_replace, action:null_if
# consumes: libs/utils/src/utils/errors.py (TransformationError)
# consumed_by: any YAML manifest using these action names, .claude/rules/rules_persona_bioscientist.md#8, libs/blueprint_arch/src/blueprint_arch/schema_registry.py (ui_schema via ACTION_SCHEMAS)
# doc: .claude/rules/rules_persona_bioscientist.md#8, .claude/knowledge/architecture_decisions.md (ADR-075, ADR-078)
# @end_deps
import polars as pl
from typing import Dict, Any
from transformer.actions.base import register_action
from utils.errors import TransformationError


@register_action("regex_extract", ui_schema={
    "label": "Regex extract",
    "category": "string",
    "context": ["t1", "t2"],
    "tags": ["string", "regex", "extraction"],
    "params": {
        "source": {"widget": "column_selector", "multi": False, "label": "Source column", "required": True},
        "pattern": {"widget": "string", "label": "Regex pattern (with capture groups)", "required": True},
        "target_column": {"widget": "string", "label": "Output column name", "required": True},
        "group": {"widget": "number", "label": "Capture group index (1-based)", "required": False, "default": 1},
    },
    "description": "Extract a substring from a string column using a capture-group regex; creates a new column with the matched group.",
    "yaml_example": "- action: regex_extract\n  source: sample_name\n  pattern: '(ST\\d+)'\n  target_column: sequence_type\n  group: 1",
})
def action_regex_extract(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Extracts a substring based on a Regex pattern with capture groups.

    Usage in YAML:
      - action: "regex_extract"
        source: "some_col"
        pattern: r"v(\\d+)\\.(\\d+)"
        target_column: "major_version"
        group: 1
    """
    source = spec.get("source", spec.get("target_column"))
    pattern = spec.get("pattern")
    target = spec.get("target_column")
    group = spec.get("group", 1)

    if not source or not pattern or not target:
        raise TransformationError(
            "action 'regex_extract' missing required parameters.",
            tip="Provide 'source', 'pattern', and 'target_column' in the YAML spec."
        )

    # Implementation: Use str.extract to generate a new column
    return lf.with_columns(
        pl.col(source).str.extract(pattern, group_index=group).alias(target)
    )


@register_action("cast", ui_schema={
    "label": "Cast dtype",
    "category": "typing",
    "context": ["t1", "t2", "assembly"],
    "tags": ["dtype", "cast", "typing", "numeric", "string"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns", "required": True},
        "dtype": {"widget": "dtype_picker", "label": "Target dtype", "required": True,
                  "options": ["Int64", "Float64", "String", "Boolean", "Date", "Categorical"]},
    },
    "description": "Change the dtype of one or more columns; always cast Float64 to Int64 then to String in two steps to avoid '2022.0' string artifacts.",
    "yaml_example": "- action: cast\n  columns: [Year]\n  dtype: Int64\n- action: cast\n  columns: [Year]\n  dtype: String",
    "wraps": [{"lib": "polars", "attr_path": ["Expr", "cast"]}],
})
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


@register_action("coalesce", ui_schema={
    "label": "Coalesce (first non-null)",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["null", "fallback", "coalesce"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns (first = target, rest = fallbacks)", "required": True, "min_items": 2},
    },
    "description": "Return the first non-null value across a list of columns row-wise; the first column is overwritten with the result.",
    "yaml_example": "- action: coalesce\n  columns: [preferred_id, backup_id, fallback_id]",
    "wraps": [{"lib": "polars", "attr_path": ["coalesce"]}],
})
def action_coalesce(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Fills nulls in the first column using values from subsequent columns in the list.
    Spec: { columns: ["target", "fallback1", "fallback2"] }
    """
    columns = spec.get("columns", [])
    if len(columns) < 2:
        raise TransformationError(
            "action 'coalesce' requires at least 2 columns.",
            tip="Provide 'columns' as a list of at least 2 column names: [target, fallback1, ...]."
        )

    return lf.with_columns(pl.coalesce(columns).alias(columns[0]))


@register_action("label_if", ui_schema={
    "label": "Label if (conditional)",
    "category": "derivation",
    "context": ["t1", "t2", "assembly"],
    "tags": ["conditional", "when-then", "labeling", "derivation"],
    "params": {
        "column": {"widget": "column_selector", "multi": False, "label": "Source column", "required": True},
        "new_column": {"widget": "string", "label": "Output column name", "required": True},
        "predicate": {"widget": "enum", "label": "Predicate", "required": True,
                      "options": [">", ">=", "<", "<=", "==", "!="]},
        "value": {"widget": "column_or_literal", "label": "Comparison value", "required": True},
        "then": {"widget": "column_or_literal", "label": "Value when true", "required": True},
        "otherwise": {"widget": "column_or_literal", "label": "Value when false", "required": False},
    },
    "description": "Create a binary label column based on a numeric comparison predicate; use `recode_values` for string-based category remapping.",
    "yaml_example": "- action: label_if\n  column: identity_pct\n  new_column: high_identity\n  predicate: '>='\n  value: 90\n  then: High\n  otherwise: Low",
})
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
        raise TransformationError(
            "action 'label_if' missing required parameters.",
            tip="Provide 'column', 'new_column', 'predicate', and 'value' in the YAML spec."
        )

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
        raise TransformationError(
            f"action 'label_if' unknown predicate '{pred}'.",
            tip="Valid values for 'predicate': >, >=, <, <=, ==, !=."
        )

    return lf.with_columns(expr.alias(new_col))


@register_action("mutate", ui_schema={
    "label": "Mutate (expression)",
    "category": "derivation",
    "context": ["t1", "t2", "assembly"],
    "tags": ["expression", "derivation", "polars", "computed-column"],
    "params": {
        "column": {"widget": "string", "label": "Output column name", "required": False},
        "target_column": {"widget": "string", "label": "Output column name (fallback)", "required": False},
        "expression": {"widget": "expression", "label": "Polars expression (e.g. pl.col('x') * 2)", "required": True},
    },
    "description": "Evaluate an arbitrary Polars expression and assign it to a column; the most powerful action \u2014 use simpler actions (cast, fill_nulls, label_if) when they suffice.",
    "yaml_example": "- action: mutate\n  column: phenotype_clean\n  expression: \"pl.col('predicted_phenotype').str.strip_chars().str.to_lowercase()\"",
})
def action_mutate(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """
    Evaluates a Polars-compatible expression and assigns it to a new column.
    Spec: { column: "new_col", expression: "pl.col('old') * 2" }
    """
    target = spec.get("column", spec.get("target_column"))
    expr_str = spec.get("expression")

    if not target or not expr_str:
        raise TransformationError(
            "action 'mutate' missing required parameters.",
            tip="Provide 'column' and 'expression' in the YAML spec."
        )

    # Evaluate the expression string within Polars context
    # Note: We assume the expression is a valid Polars string expression using pl.
    try:
        expr = eval(expr_str, {"pl": pl})
    except Exception as e:
        raise ValueError(f"Failed to evaluate expression '{expr_str}': {e}")

    return lf.with_columns(expr.alias(target))


@register_action("regex_replace", ui_schema={
    "label": "Regex replace",
    "category": "string",
    "context": ["t1", "t2", "assembly"],
    "tags": ["string", "regex", "replace", "clean"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns", "required": True},
        "pattern": {"widget": "string", "label": "Regex pattern", "required": True},
        "value": {"widget": "string", "label": "Replacement string", "required": False, "default": ""},
    },
    "description": "Replace all regex pattern matches in string columns with a replacement string; use `strip_whitespace` for the common whitespace case.",
    "yaml_example": "- action: regex_replace\n  columns: [gene_name]\n  pattern: '_v\\d+$'\n  value: ''",
})
def action_regex_replace(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Regex-based string replacement."""
    cols = spec.get("columns", [])
    pattern = spec.get("pattern")
    value = spec.get("value", "")
    if not cols or not pattern:
        raise TransformationError(
            "action 'regex_replace' missing required parameters.",
            tip="Provide 'columns' and 'pattern' in the YAML spec."
        )
    return lf.with_columns(pl.col(cols).str.replace_all(pattern, value))


@register_action("null_if", ui_schema={
    "label": "Null if value",
    "category": "cleaning",
    "context": ["t1", "t2", "assembly"],
    "tags": ["null", "missing", "clean", "replace"],
    "params": {
        "columns": {"widget": "column_selector", "multi": True, "label": "Columns", "required": True},
        "value": {"widget": "column_or_literal", "label": "Value to convert to null", "required": True},
    },
    "description": "Replace a specific sentinel value (e.g. 'N/A', '-') with null across one or more columns; inverse of fill_nulls.",
    "yaml_example": "- action: null_if\n  columns: [resistance, virulence]\n  value: 'N/A'",
})
def action_null_if(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    """Converts a specific value to null."""
    cols = spec.get("columns", [])
    value = spec.get("value")
    if not cols:
        raise TransformationError(
            "action 'null_if' missing required parameter 'columns'.",
            tip="Provide 'columns' (list) in the YAML spec."
        )
    return lf.with_columns(pl.when(pl.col(cols) == value).then(None).otherwise(pl.col(cols)))
