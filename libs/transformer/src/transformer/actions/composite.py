"""The `step_` actions: more than one Polars call, kept because a single step is simpler to read (W6, DEC36, R7).

One old action stays a composite: `step_top_n_other` (about eight Polars calls, the tie rule of ADR-090, a port of the R
function of the APEC study). The others that were composite are Polars steps now (Eve 2026-11-13, "the Polars action and
nothing else, otherwise it is difficult to control"): `summarize` is `polars_group_by`, `split_column` and
`split_column_to_parts` are `polars_str_splitn` then `polars_unnest` (the old split_column_to_parts lost the remainder
silently). Every choice is a parameter and a step that cannot act fails.

Calls in order:
  step_top_n_other          group_by + agg + sort + head, join back, when/then

Consumed by: the recipe. If deleted: those steps are refused.
"""
from typing import Any, Dict

import polars as pl

from transformer.actions.base import register_action
from transformer.actions.polars_calls import _checked
from utils.errors import TransformationError

# @deps
# provides: action:step_top_n_other
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
