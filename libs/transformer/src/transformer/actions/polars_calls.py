"""The `polars_` actions: each one is a Polars call, exposed with Polars' parameter names and defaults (W6).

Why this module exists: the recipe reads like Polars code, and a name that starts with `polars_` means
"exactly the Polars call" (`recipe_format_spec.md` 7.5.1, DEC31 to DEC34). The parameters of every action are
read from `inspect.signature` of the Polars object it wraps, so a Polars release that adds or changes a
parameter shows up here and in the registry tests instead of being missed. What a recipe maker must state
and Polars would default (the order rule of `sort`, `unique`, `join`, `sample`; the `decimals` of `round`)
is marked required in `REQUIRED`: a choice that changes the result is written in the recipe (DEC33, DEC34).

Four kinds of call:
  frame     a LazyFrame method on the table of the step (`select`, `drop`, `sort`, `join`, ...);
  eager     a DataFrame method; the table is collected, the result goes on lazily (`pivot`, `sample`, `describe`);
  expr      an Expression method applied to the listed `columns` through `with_columns`; the optional
            `target_column` writes the result of ONE column to another column (`cast`, `fill_null`, `str_*`, ...);
  function  a function over several columns written to `target_column` (`coalesce`, `sum_horizontal`, ...).

A step is judged by `utils.ui_schema.step_problems` before it runs, so an unknown key, a missing required
parameter or a wrong form fails and names the step; nothing returns the table unchanged (DEC36).

Consumed by: the action registry (`AVAILABLE_WRANGLING_ACTIONS`), the checker, Blueprint's form catalogue.
If deleted: no recipe can use a `polars_` action.
"""
import importlib
import inspect
from typing import Any, Callable, Dict

import polars as pl

from transformer.actions.base import ACTION_SCHEMAS, register_action
from utils.errors import TransformationError
from utils.formula_check import FormulaError, evaluate_formula
from utils.ui_schema import step_problems

# @deps
# provides: action:polars_select, action:polars_drop, action:polars_with_columns, action:polars_rename, action:polars_unique, action:polars_sort, action:polars_drop_nulls, action:polars_drop_nans, action:polars_explode, action:polars_unnest, action:polars_unpivot, action:polars_pivot, action:polars_join, action:polars_sample, action:polars_describe, action:polars_cast, action:polars_fill_null, action:polars_fill_nan, action:polars_shift, action:polars_cum_sum, action:polars_cum_count, action:polars_interpolate, action:polars_round, action:polars_str_replace_all, action:polars_str_extract, action:polars_str_split, action:polars_str_strip_chars, action:polars_list_join, action:polars_list_slice, action:polars_dt_truncate, action:polars_coalesce, action:polars_sum_horizontal, action:polars_mean_horizontal, action:polars_min_horizontal, action:polars_max_horizontal, action:polars_all_horizontal, action:polars_any_horizontal
# consumes: libs/utils/src/utils/ui_schema.py (step_problems)
# consumed_by: libs/transformer/tests/test_polars_actions_equal_polars.py, libs/transformer/tests/test_registry_polars_rules.py
# doc: .claude/design/recipe_format_spec.md#7.5.1
# @end_deps

# The Polars name of a parameter that Polars takes as *args or **kwargs, and the name a recipe uses.
RECIPE_NAME = {"more_exprs": "exprs", "more_by": "by", "more_columns": "columns", "other": "right_ingredient"}
# the extra positional arguments of a call are merged into the one list the recipe writes
MERGED = {"more_exprs", "more_by", "more_columns"}
# the same Polars name can mean another thing in another call (`by` is a column list in sort, a separator in str.split)
OVERRIDE = {("polars_sort", "descending"): {"widget": "any", "label": "Descending: true or false for all columns, or a list with one value per column"},
            ("polars_sort", "nulls_last"): {"widget": "any", "label": "Nulls last: true or false for all columns, or a list with one value per column"},
            ("polars_str_split", "by"): {"widget": "string", "label": "Separator"},
            ("polars_str_splitn", "by"): {"widget": "string", "label": "Separator"}}

# Parameters whose absence would hide a choice that changes the result: required although Polars defaults them (DEC34).
REQUIRED = {
    "polars_unique": {"keep", "maintain_order"},
    "polars_sort": {"maintain_order"},
    "polars_group_by": {"maintain_order"},
    "polars_str_splitn": {"n"},
    "polars_join": {"how", "maintain_order"},
    "polars_sample": {"seed"},
    "polars_round": {"decimals"},
    "polars_coalesce": {"target_column"},
    "polars_sum_horizontal": {"target_column"}, "polars_mean_horizontal": {"target_column"},
    "polars_min_horizontal": {"target_column"}, "polars_max_horizontal": {"target_column"},
    "polars_all_horizontal": {"target_column"}, "polars_any_horizontal": {"target_column"},
}

# Parameters of a Polars call that a recipe does not expose, with the reason (the registry test reads this).
NOT_EXPOSED = {
    "polars_select": {"named_exprs": "column names only (DEC37); a computed column is a polars_with_columns step first"},
    "polars_with_columns": {"exprs": "every new column is named in `named_exprs`, so the table shows what each formula makes"},
    "polars_group_by": {"named_by": "group by column names only; a computed key is a polars_with_columns step first"},
}

LIST_OF_COLUMNS = {"widget": "column_selector", "multi": True, "label": "Columns"}
HINTS: Dict[str, dict] = {
    "exprs": LIST_OF_COLUMNS, "columns": LIST_OF_COLUMNS, "subset": LIST_OF_COLUMNS, "by": LIST_OF_COLUMNS,
    "index": LIST_OF_COLUMNS, "on": LIST_OF_COLUMNS, "values": LIST_OF_COLUMNS, "left_on": LIST_OF_COLUMNS,
    "right_on": LIST_OF_COLUMNS,
    "mapping": {"widget": "mapping", "label": "Mapping"},
    "named_exprs": {"widget": "mapping", "label": "Column: formula (a Polars expression as text)"},
    "percentiles": {"widget": "list", "label": "Percentiles"},
    "keep": {"widget": "enum", "options": ["any", "first", "last", "none"]},
    "how": {"widget": "enum", "options": ["inner", "left", "right", "full", "semi", "anti", "cross"]},
    "maintain_order": {"widget": "bool"},
    "strategy": {"widget": "enum", "options": ["forward", "backward", "min", "max", "mean", "zero", "one"]},
    "interpolation": {"widget": "enum", "options": ["nearest", "higher", "lower", "midpoint", "linear"]},
    "method": {"widget": "enum", "options": ["linear", "nearest"]},
    "mode": {"widget": "enum", "options": ["half_to_even", "half_away_from_zero"]},
    "validate": {"widget": "enum", "options": ["m:m", "1:m", "m:1", "1:1"]},
    "aggregate_function": {"widget": "enum", "options": ["min", "max", "first", "last", "sum", "mean", "median", "len"]},
    "column_naming": {"widget": "enum", "options": ["auto", "combine"]},
    "dtype": {"widget": "dtype_picker", "label": "Polars dtype"},
}
# maintain_order of join is an enum of strings (Polars), of every other call a bool
JOIN_ORDER = {"widget": "enum", "options": ["none", "left", "right", "left_right", "right_left"]}

# (action, kind, Polars object path, class of the method, description, yaml_example, extra schema keys)
FRAME, EAGER, EXPR, FUNCTION = "frame", "eager", "expr", "function"


# Expression namespaces are properties of Expr; the class that holds the methods is what `wraps` names (ADR-075 help panel).
NAMESPACES = {"str": ("polars.expr.string", "ExprStringNameSpace"),
              "list": ("polars.expr.list", "ExprListNameSpace"),
              "dt": ("polars.expr.datetime", "ExprDateTimeNameSpace")}


def _wraps(path):
    """The `wraps` entry of a Polars object: the module to import and the attribute path inside it."""
    path = list(path)
    if len(path) == 3 and path[0] == "Expr" and path[1] in NAMESPACES:
        module, cls = NAMESPACES[path[1]]
        return {"lib": module, "attr_path": [cls, path[2]]}
    return {"lib": "polars", "attr_path": path}


def _resolve(path):
    entry = _wraps(path)
    obj = importlib.import_module(entry["lib"])
    for part in entry["attr_path"]:
        obj = getattr(obj, part)
    return obj


def _widget_for(name: str, param: inspect.Parameter, action: str) -> dict:
    if (action, name) in OVERRIDE:
        return dict(OVERRIDE[(action, name)])
    if action == "polars_join" and name == "maintain_order":
        return dict(JOIN_ORDER)
    if name in HINTS:
        return dict(HINTS[name])
    default = param.default
    if isinstance(default, bool):
        return {"widget": "bool"}
    if isinstance(default, (int, float)):
        return {"widget": "number"}
    if name in ("value", "fill_value"):
        return {"widget": "column_or_literal"}
    return {"widget": "string"}


def _params_from_signature(action: str, target, kind: str) -> dict:
    """The parameter definitions of an action: every Polars parameter, Polars defaults, ours added."""
    params: Dict[str, dict] = {}
    skipped = NOT_EXPOSED.get(action, {})
    for name, p in inspect.signature(target).parameters.items():
        if name in ("self", "cls") or name in skipped:
            continue
        ours = RECIPE_NAME.get(name, name)
        if name in MERGED:
            continue
        definition = _widget_for(ours, p, action)
        definition.setdefault("label", ours)
        required = (p.default is inspect.Parameter.empty and p.kind not in (p.VAR_POSITIONAL, p.VAR_KEYWORD)) \
            or ours in REQUIRED.get(action, set()) or (p.kind is p.VAR_POSITIONAL and ours in ("exprs", "columns", "by"))
        if required:
            definition["required"] = True
        params[ours] = definition
    if kind == EXPR:
        params = {"columns": {**LIST_OF_COLUMNS, "label": "Columns the call is applied to", "required": True},
                  **params,
                  "target_column": {"widget": "string", "label": "Write the result of the single column to this column (default: in place)"}}
    if kind == FUNCTION:
        params["target_column"] = {"widget": "string", "label": "Column that receives the result", "required": True}
    return params


def _kwargs(spec: dict, target, action: str) -> dict:
    """The keyword arguments of the Polars call: every declared parameter the step gave, under its Polars name."""
    out = {}
    for name, p in inspect.signature(target).parameters.items():
        ours = RECIPE_NAME.get(name, name)
        if name in ("self", "cls") or name in MERGED or p.kind is p.VAR_KEYWORD or spec.get(ours) is None:
            continue
        out[name] = spec[ours]
    return out


def _dtype(name: str):
    dtype = getattr(pl, str(name), None)
    if not (isinstance(dtype, type) and issubclass(dtype, pl.DataType)) and not isinstance(dtype, pl.DataType):
        raise TransformationError(f"{name!r} is not a Polars dtype", tip="Write a Polars dtype name such as Int64, Float64, String, Date")
    return dtype


def _formula(text: str):
    """A Polars expression written as text, checked before it runs (`utils.formula_check`, spec section 15)."""
    try:
        return evaluate_formula(text)
    except FormulaError as exc:
        raise TransformationError(f"The formula {text!r} is refused: {exc}",
                                  tip="Write a Polars expression built from pl.col, pl.lit, pl.when and Expr methods, for example pl.col('x') * 2")
    except Exception as exc:  # noqa: BLE001 - a syntax error or a Polars error in a formula
        raise TransformationError(f"Failed to evaluate the formula {text!r}: {exc}", tip="Write a valid Polars expression, for example pl.col('x') * 2")


def _checked(action: str, spec: dict) -> dict:
    """The step without the engine's own keys, after the same rule set that the checker uses (never a silent no-op)."""
    clean = {k: v for k, v in spec.items() if not (isinstance(k, str) and k.startswith("__") and k.endswith("__"))}
    problems = step_problems(action, clean, ACTION_SCHEMAS[action])
    if problems:
        raise TransformationError(f"step {action}: " + "; ".join(p.text() for p in problems),
                                  tip="Correct the step in the recipe; the action does not guess")
    return clean


def _schema(action: str, kind: str, target, path, description: str, example: str, rules=None, category="polars") -> dict:
    schema = {
        "label": action.removeprefix("polars_").replace("_", " "),
        "category": category, "context": ["t1", "t2", "assembly"], "tags": ["polars", action.removeprefix("polars_")],
        "polars": "exact" if kind in (FRAME, EAGER) else "wrapper",
        "wraps": [_wraps(path)],
        "params": _params_from_signature(action, target, kind),
        "description": description, "yaml_example": example,
    }
    if rules:
        schema["rules"] = rules
    if action in NOT_EXPOSED:
        schema["not_exposed"] = dict(NOT_EXPOSED[action])
    return schema


def _define(action: str, kind: str, path, run: Callable[[pl.LazyFrame, dict, Any], Any], description: str, example: str, rules=None):
    target = _resolve(path)

    def action_function(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
        clean = _checked(action, spec)
        out = run(lf, clean, target)
        return out.lazy() if isinstance(out, pl.DataFrame) else out

    action_function.__name__ = f"action_{action}"
    action_function.__doc__ = description
    register_action(action, ui_schema=_schema(action, kind, target, path, description, example, rules))(action_function)
    return action_function


# -- frame methods ----------------------------------------------------------------------------------

def _frame(action, method, description, example, rules=None, args=None):
    """A LazyFrame method; `args` names the parameters that Polars takes positionally, in order."""
    positional = args or []

    def run(lf, spec, target):
        kwargs = _kwargs(spec, target, action)
        pos = [kwargs.pop(name) for name in positional if name in kwargs]
        if method in ("select", "drop"):             # Polars takes the columns as *args; the recipe gives one list
            return getattr(lf, method)(*pos[0], **kwargs)
        return getattr(lf, method)(*pos, **kwargs)
    return _define(action, FRAME, ("LazyFrame", method), run, description, example, rules)


_frame("polars_select", "select", "Keep the listed columns, in the order written (Polars LazyFrame.select; names only).",
       "- action: polars_select\n  exprs: [sample_id, country]", args=["exprs"])
_frame("polars_drop", "drop", "Remove the listed columns; a missing column fails (Polars LazyFrame.drop).",
       "- action: polars_drop\n  columns: [temp_flag]\n  strict: true", args=["columns"])
_frame("polars_rename", "rename", "Rename columns by a mapping old name to new name (Polars LazyFrame.rename).",
       "- action: polars_rename\n  mapping: {Sample_ID: sample_id}", args=["mapping"])
_frame("polars_unique", "unique", "Keep one row of each group of equal rows in `subset` (Polars LazyFrame.unique); the order rule is written in the step.",
       "- action: polars_unique\n  subset: [sample_id]\n  keep: first\n  maintain_order: true")
_frame("polars_sort", "sort", "Sort the table by columns (Polars LazyFrame.sort); `maintain_order` is written in the step so that ties never change.",
       "- action: polars_sort\n  by: [year, country]\n  maintain_order: true", args=["by"])
_frame("polars_drop_nulls", "drop_nulls", "Drop the rows that have a null in `subset` (all columns when absent) (Polars LazyFrame.drop_nulls).",
       "- action: polars_drop_nulls\n  subset: [sample_id]")
_frame("polars_drop_nans", "drop_nans", "Drop the rows that have a NaN in `subset` (a NaN is a number, not a null) (Polars LazyFrame.drop_nans).",
       "- action: polars_drop_nans\n  subset: [identity]")
_frame("polars_explode", "explode", "One row per element of a list column (Polars LazyFrame.explode).",
       "- action: polars_explode\n  columns: [genes]", args=["columns"])
_frame("polars_unnest", "unnest", "Turn the fields of a struct column into columns (Polars LazyFrame.unnest).",
       "- action: polars_unnest\n  columns: [parts]", args=["columns"])
_frame("polars_unpivot", "unpivot", "Wide table to long table (Polars LazyFrame.unpivot).",
       "- action: polars_unpivot\n  'on': [AMR, QC]\n  index: [sample_id]\n  variable_name: kind\n  value_name: value")


def _with_columns(lf, spec, target):
    named = {name: _formula(text) for name, text in spec["named_exprs"].items()}
    return lf.with_columns(**named)


_define("polars_with_columns", FRAME, ("LazyFrame", "with_columns"), _with_columns,
        "Add or replace columns; every column is named in `named_exprs` with its formula (Polars LazyFrame.with_columns). All formulas see the table as it was before the step.",
        "- action: polars_with_columns\n  named_exprs:\n    n2: \"pl.col('n') * 2\"")


def _join_action(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    right = spec.get("__right_df__")
    if right is None:
        raise TransformationError("polars_join needs the resolved right table (__right_df__)", tip="The assembler resolves `right_ingredient`")
    clean = _checked("polars_join", spec)
    kwargs = _kwargs(clean, pl.LazyFrame.join, "polars_join")
    kwargs.pop("other", None)
    return lf.join(right, **kwargs)


_join_target = pl.LazyFrame.join
register_action("polars_join", ui_schema=_schema(
    "polars_join", FRAME, _join_target, ("LazyFrame", "join"),
    "Join the table of the step with a second table named by `right_ingredient` (Polars LazyFrame.join); `how` and `maintain_order` are written in the step.",
    "- action: polars_join\n  right_ingredient: metadata_schema\n  'on': [sample_id]\n  how: left\n  maintain_order: left_right",
    rules=[{"one_of": ["on", "left_on"]}]))(_join_action)


def _group_by_schema():
    schema = _schema("polars_group_by", FRAME, pl.LazyFrame.group_by, ("LazyFrame", "group_by"),
                     "Group the table and aggregate with named formulas (Polars LazyFrame.group_by(...).agg(...)); `maintain_order` is written in the step so that the groups come out in a fixed order.",
                     "- action: polars_group_by\n  by: [sample_id]\n  maintain_order: true\n  named_aggs:\n    gene_count: \"pl.col('gene').count()\"")
    schema["polars"] = "wrapper"
    schema["params"]["by"] = {**LIST_OF_COLUMNS, "label": "Group by columns (an empty list aggregates the whole table)", "required": True}
    schema["params"]["named_aggs"] = {"widget": "mapping", "label": "Result column: aggregation formula (a Polars expression as text)", "required": True, "value_widget": "expression"}
    return schema


def _group_by_action(lf: pl.LazyFrame, spec: Dict[str, Any]) -> pl.LazyFrame:
    clean = _checked("polars_group_by", spec)
    aggs = {name: _formula(text) for name, text in clean["named_aggs"].items()}
    if not clean["by"]:
        return lf.select(**aggs)
    return lf.group_by(clean["by"], maintain_order=clean["maintain_order"]).agg(**aggs)


register_action("polars_group_by", ui_schema=_group_by_schema())(_group_by_action)


# -- eager methods (the table is collected, the result goes on lazily) --------------------------------

def _eager(action, method, description, example, rules=None):
    def run(lf, spec, target):
        return getattr(lf.collect(), method)(**_kwargs(spec, target, action))
    return _define(action, EAGER, ("DataFrame", method), run, description, example, rules)


_eager("polars_pivot", "pivot", "Long table to wide table (Polars DataFrame.pivot; the table is collected first).",
       "- action: polars_pivot\n  'on': [kind]\n  index: [sample_id]\n  values: [value]\n  aggregate_function: first")
_eager("polars_sample", "sample", "A random sample of rows (Polars DataFrame.sample); `seed` is written in the step so that the same recipe gives the same table.",
       "- action: polars_sample\n  fraction: 0.1\n  seed: 1", rules=[{"one_of": ["n", "fraction"]}])
_eager("polars_describe", "describe", "Summary statistics of every column as a table (Polars DataFrame.describe; the table is collected first).",
       "- action: polars_describe")


# -- an expression method applied to the listed columns --------------------------------------------------

def _refuse_silent_truncation(lf: pl.LazyFrame, columns, dtype) -> None:
    """A float cast to an integer type drops the decimals without a word in Polars; here it fails and names the value.

    Eve 2026-11-13 (Q1): never silent, never a data-science problem. A maker who wants the decimals dropped writes a
    step for it (`polars_round` with `decimals: 0`, then the cast). The check collects only the offending values and
    only when a float column is cast to an integer type.
    """
    if not (isinstance(dtype, type) and issubclass(dtype, pl.DataType) and dtype.is_integer() or getattr(dtype, "is_integer", lambda: False)()):
        return
    schema = lf.collect_schema()
    for column in columns:
        if column in schema and schema[column].is_float():
            lost = (lf.select(pl.col(column).filter(pl.col(column).is_finite() & (pl.col(column) != pl.col(column).floor())))
                    .head(3).collect()[column].to_list())
            if lost:
                raise TransformationError(
                    f"step polars_cast: column {column!r} holds values with decimals ({lost}); casting to {dtype} would drop them silently",
                    tip="Round first in a step of its own (polars_round with decimals: 0, or the rule you want), then cast")


def _expr(action, path, description, example, rules=None):
    *owner, method = path

    def run(lf, spec, target):
        kwargs = _kwargs(spec, target, action)
        if "dtype" in kwargs:
            kwargs["dtype"] = _dtype(kwargs["dtype"])
        columns = spec["columns"]
        if action == "polars_cast":
            _refuse_silent_truncation(lf, columns, kwargs["dtype"])
        base = pl.col(columns)
        for part in owner[1:]:                       # the namespace: str, list, dt
            base = getattr(base, part)
        expression = getattr(base, method)(**kwargs)
        target_column = spec.get("target_column")
        if target_column:
            if len(columns) != 1:
                raise TransformationError(f"step {action}: target_column needs exactly one column in `columns`",
                                          tip="Write one column, or leave target_column out to work in place")
            expression = expression.alias(target_column)
        return lf.with_columns(expression)
    return _define(action, EXPR, tuple(path), run, description, example, rules)


_expr("polars_cast", ["Expr", "cast"], "Change the dtype of the listed columns (Polars Expr.cast). Unlike Polars, a float cast to an integer FAILS when a value has decimals: a truncation is never silent, write a rounding step first (Eve, Q1).",
      "- action: polars_cast\n  columns: [year]\n  dtype: Int64\n  strict: true")
_expr("polars_fill_null", ["Expr", "fill_null"], "Replace nulls by a value or by a strategy (Polars Expr.fill_null); give `value` or `strategy`, not both.",
      "- action: polars_fill_null\n  columns: [country]\n  value: Unknown", rules=[{"one_of": ["value", "strategy"]}])
_expr("polars_fill_nan", ["Expr", "fill_nan"], "Replace NaN values (not nulls) by a value (Polars Expr.fill_nan).",
      "- action: polars_fill_nan\n  columns: [identity]\n  value: 0.0")
_expr("polars_shift", ["Expr", "shift"], "Shift the values down by `n` rows (Polars Expr.shift).", "- action: polars_shift\n  columns: [count]\n  n: 1")
_expr("polars_cum_sum", ["Expr", "cum_sum"], "Running sum (Polars Expr.cum_sum).", "- action: polars_cum_sum\n  columns: [count]\n  reverse: false")
_expr("polars_cum_count", ["Expr", "cum_count"], "Running count of non-null values (Polars Expr.cum_count).", "- action: polars_cum_count\n  columns: [count]\n  reverse: false")
_expr("polars_interpolate", ["Expr", "interpolate"], "Fill nulls between values by interpolation (Polars Expr.interpolate).", "- action: polars_interpolate\n  columns: [reading]\n  method: linear")
_expr("polars_round", ["Expr", "round"], "Round numbers to `decimals` places (Polars Expr.round); `decimals` is written in the step.", "- action: polars_round\n  columns: [identity]\n  decimals: 1")
_expr("polars_str_replace_all", ["Expr", "str", "replace_all"], "Replace every match of a pattern in a text column (Polars str.replace_all).",
      "- action: polars_str_replace_all\n  columns: [name]\n  pattern: '_'\n  value: '-'\n  literal: true")
_expr("polars_str_extract", ["Expr", "str", "extract"], "Extract a group of a regular expression (Polars str.extract).",
      "- action: polars_str_extract\n  columns: [name]\n  pattern: '(\\d+)'\n  group_index: 1")
_expr("polars_str_split", ["Expr", "str", "split"], "Split a text column into a list at `by` (Polars str.split).", "- action: polars_str_split\n  columns: [genes]\n  by: ','")
_expr("polars_str_splitn", ["Expr", "str", "splitn"], "Split a text column at `by` into at most `n` parts; the last part keeps the remainder (Polars str.splitn). The result is a struct column: write `target_column` to keep the source, then polars_unnest it and polars_rename the fields (field_0, field_1, ...).",
      "- action: polars_str_splitn\n  columns: [species_type]\n  by: '/'\n  n: 2\n  target_column: parts")
_expr("polars_str_strip_chars", ["Expr", "str", "strip_chars"], "Strip characters from both ends of a text column; without `characters` Polars strips whitespace (Polars str.strip_chars).",
      "- action: polars_str_strip_chars\n  columns: [name]")
_expr("polars_list_join", ["Expr", "list", "join"], "Join the elements of a list column into text (Polars list.join).", "- action: polars_list_join\n  columns: [genes]\n  separator: ';'")
_expr("polars_list_slice", ["Expr", "list", "slice"], "A slice of each list (Polars list.slice).", "- action: polars_list_slice\n  columns: [genes]\n  offset: 0\n  length: 3")
_expr("polars_dt_truncate", ["Expr", "dt", "truncate"], "Truncate dates to a period (Polars dt.truncate).", "- action: polars_dt_truncate\n  columns: [collection_date]\n  every: 1mo")


# -- a function over several columns, written to a target column --------------------------------------------

def _function(action, name, description, example):
    def run(lf, spec, target):
        kwargs = _kwargs(spec, target, action)
        kwargs.pop("exprs", None)
        return lf.with_columns(target(*spec["exprs"], **kwargs).alias(spec["target_column"]))
    return _define(action, FUNCTION, (name,), run, description, example)


_function("polars_coalesce", "coalesce", "The first non-null value across the listed columns, written to `target_column` (Polars coalesce). Write the first column as the target to overwrite it.",
          "- action: polars_coalesce\n  exprs: [preferred_id, backup_id]\n  target_column: preferred_id")
_function("polars_sum_horizontal", "sum_horizontal", "Row-wise sum of the listed columns (Polars sum_horizontal).", "- action: polars_sum_horizontal\n  exprs: [a, b]\n  target_column: total")
_function("polars_mean_horizontal", "mean_horizontal", "Row-wise mean of the listed columns (Polars mean_horizontal).", "- action: polars_mean_horizontal\n  exprs: [a, b]\n  target_column: mean")
_function("polars_min_horizontal", "min_horizontal", "Row-wise minimum (Polars min_horizontal).", "- action: polars_min_horizontal\n  exprs: [a, b]\n  target_column: low")
_function("polars_max_horizontal", "max_horizontal", "Row-wise maximum (Polars max_horizontal).", "- action: polars_max_horizontal\n  exprs: [a, b]\n  target_column: high")
_function("polars_all_horizontal", "all_horizontal", "True where every listed boolean column is true (Polars all_horizontal).", "- action: polars_all_horizontal\n  exprs: [passed_qc, has_metadata]\n  target_column: complete")
_function("polars_any_horizontal", "any_horizontal", "True where any listed boolean column is true (Polars any_horizontal).", "- action: polars_any_horizontal\n  exprs: [resistant_a, resistant_b]\n  target_column: any_resistant")
