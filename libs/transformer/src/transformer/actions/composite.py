"""The `step_` actions: more than one Polars call, kept because a single step is simpler to read (W6, DEC36, R7).

Five old actions were examined one by one (evidence section 25); these four stay, each with its calls written in the
description and every choice a parameter: nothing is defaulted silently and a step that cannot act fails (it never
returns the table unchanged). `step_top_n_other` keeps its logic of the old action (ADR-090 tie rule).

Calls in order:
  step_summarize            group_by, agg
  step_top_n_other          group_by + agg + sort + head, join back, when/then
  step_split_column         str.split, list.get, list.slice + list.join (the last part keeps the remainder), optional drop
  step_split_column_to_parts  str.splitn, struct.rename_fields, unnest

Consumed by: the recipe. If deleted: those steps are refused.
"""
from typing import Any, Dict

import polars as pl

from transformer.actions.base import register_action
from transformer.actions.polars_calls import _checked
from utils.errors import TransformationError

# @deps
# provides: action:step_summarize, action:step_top_n_other, action:step_split_column, action:step_split_column_to_parts
# consumes: libs/transformer/src/transformer/actions/polars_calls.py (_checked)
# consumed_by: libs/transformer/tests/test_step_actions.py
# doc: .claude/design/recipe_format_spec.md#7.5.1 (DEC36, R7), .claude/design/home_evidence/actions_and_polars_2026-11-13.md section 25
# @end_deps

LIST = {"widget": "column_selector", "multi": True}


def _schema(label, category, description, example, params, rules=None, calls=None):
    schema = {"label": label, "category": category, "context": ["t1", "t2", "assembly"], "tags": ["step", "composite"],
              "polars": "composite", "params": params, "description": description, "yaml_example": example}
    if rules:
        schema["rules"] = rules
    if calls:
        schema["wraps"] = calls
    return schema


@register_action("step_summarize", ui_schema=_schema(
    "summarize", "aggregation",
    "Group the table and aggregate columns (Polars group_by then agg); one aggregation for all listed columns. Groups come out in the order they first appear.",
    "- action: step_summarize\n  group_by: [sample_id]\n  columns: [gene]\n  agg: count\n  new_name: gene_count",
    {"group_by": {**LIST, "label": "Group by columns (an empty list aggregates the whole table)", "required": True},
     "columns": {**LIST, "label": "Columns to aggregate", "required": True},
     "agg": {"widget": "enum", "label": "Aggregation", "options": ["count", "sum", "mean"], "required": True},
     "new_name": {"widget": "string", "label": "Name of the result when one column is aggregated (else column_agg)"}},
    calls=[{"lib": "polars", "attr_path": ["LazyFrame", "group_by"]}]))
def action_step_summarize(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = _checked("step_summarize", spec)
    columns, group_by, agg, new_name = clean["columns"], clean["group_by"], clean["agg"], clean.get("new_name")
    if new_name and len(columns) != 1:
        raise TransformationError("step step_summarize: new_name needs exactly one column in `columns`", tip="Write one column, or leave new_name out")
    method = {"count": "count", "sum": "sum", "mean": "mean"}[agg]
    exprs = [getattr(pl.col(c), method)().alias(new_name or f"{c}_{agg}") for c in columns]
    if not group_by:
        return lf.select(exprs)
    return lf.group_by(group_by, maintain_order=True).agg(exprs)


@register_action("step_top_n_other", ui_schema=_schema(
    "top n and other", "aggregation",
    "Keep the n most frequent values of a column and label every other value `other_label` (a null stays null). Ties are ranked by the value itself, alphabetically (ADR-090), rows keep their order. Mirrors top_n_other() of the R code of the APEC study.",
    "- action: step_top_n_other\n  column: variant\n  n: 10\n  other_label: Other\n  new_column: variant_top10",
    {"column": {"widget": "column_selector", "multi": False, "label": "Column", "required": True},
     "n": {"widget": "number", "label": "How many values to keep (a whole number of at least 1)", "required": True},
     "other_label": {"widget": "string", "label": "Label of the other values", "required": True},
     "new_column": {"widget": "string", "label": "Column that receives the result", "required": True},
     "count_distinct": {"widget": "column_selector", "multi": False, "label": "Count distinct values of this column instead of rows (off when absent)", "off_when_absent": True}}))
def action_step_top_n_other(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = _checked("step_top_n_other", spec)
    col, n, other_label, new_col = clean["column"], clean["n"], clean["other_label"], clean["new_column"]
    if isinstance(n, bool) or not isinstance(n, int) or n < 1:
        raise TransformationError(f"step step_top_n_other: 'n' must be a whole number of at least 1, got {n!r}", tip="Use a positive integer, for example n: 10")
    count_by = clean.get("count_distinct")
    key = pl.col(col).cast(pl.String)          # rank on text so the join never depends on categorical dictionaries
    count = pl.col(count_by).drop_nulls().n_unique() if count_by else pl.len()
    top = (lf.select(key.alias("__key"), *([pl.col(count_by)] if count_by else []))
           .filter(pl.col("__key").is_not_null()).group_by("__key").agg(count.alias("__n"))
           .sort(["__n", "__key"], descending=[True, False]).head(n)
           .select("__key", pl.lit(True).alias("__is_top")))
    return (lf.with_columns(key.alias("__key"))
            .join(top, on="__key", how="left", maintain_order="left_right")
            .with_columns(pl.when(pl.col("__key").is_null()).then(pl.lit(None, dtype=pl.String))
                          .when(pl.col("__is_top").is_not_null()).then(pl.col("__key"))
                          .otherwise(pl.lit(other_label)).alias(new_col))
            .drop("__key", "__is_top"))


@register_action("step_split_column", ui_schema=_schema(
    "split column", "reshaping",
    "Split a text column at a delimiter into the named columns; the last named column keeps the remainder after the previous delimiters. A value with fewer parts gives null in the missing columns. The source column is kept unless `drop_source` is true.",
    "- action: step_split_column\n  columns: [species_biotype]\n  new_columns: [species, biotype]\n  delimiter: '_'",
    {"columns": {**LIST, "label": "The source column (one)", "required": True},
     "new_columns": {"widget": "list", "label": "Output column names", "required": True},
     "delimiter": {"widget": "string", "label": "Delimiter", "required": True},
     "drop_source": {"widget": "bool", "label": "Drop the source column (off when absent)", "off_when_absent": True}}))
def action_step_split_column(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = _checked("step_split_column", spec)
    if len(clean["columns"]) != 1:
        raise TransformationError("step step_split_column: write exactly one source column in `columns`", tip="One column per step")
    source, names, delimiter = clean["columns"][0], clean["new_columns"], clean["delimiter"]
    if source not in lf.collect_schema().names():
        raise TransformationError(f"step step_split_column: column {source!r} is not in the table", tip="The step never skips a missing column")
    n = len(names)
    lf = lf.with_columns(pl.col(source).str.split(delimiter).alias("_split_list"))
    parts = []
    for i, name in enumerate(names):
        if i < n - 1:
            parts.append(pl.col("_split_list").list.get(i, null_on_oob=True).alias(name))
        else:
            parts.append(pl.when(pl.col("_split_list").list.len() > i)
                         .then(pl.col("_split_list").list.slice(i).list.join(delimiter)).otherwise(None).alias(name))
    lf = lf.with_columns(parts).drop("_split_list")
    return lf.drop(source) if clean.get("drop_source") else lf


@register_action("step_split_column_to_parts", ui_schema=_schema(
    "split column to parts", "reshaping",
    "Split a text column at a separator into the named columns (Polars str.splitn, struct.rename_fields, unnest). A value with more parts than names keeps the remainder in the last column (the old split_column_to_parts dropped it silently); one with fewer gives null. The source column is kept.",
    "- action: step_split_column_to_parts\n  columns: [species_type]\n  separator: '/'\n  new_columns: [species, biotype]",
    {"columns": {**LIST, "label": "The source column (one)", "required": True},
     "separator": {"widget": "string", "label": "Separator", "required": True},
     "new_columns": {"widget": "list", "label": "Output column names", "required": True}}))
def action_step_split_column_to_parts(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = _checked("step_split_column_to_parts", spec)
    if len(clean["columns"]) != 1:
        raise TransformationError("step step_split_column_to_parts: write exactly one source column in `columns`", tip="One column per step")
    source, names = clean["columns"][0], clean["new_columns"]
    # splitn keeps the remainder in the last part; the old action used split_exact, which dropped it without a word
    return lf.with_columns(pl.col(source).str.splitn(clean["separator"], len(names))
                           .struct.rename_fields(names).alias("__parts")).unnest("__parts")
