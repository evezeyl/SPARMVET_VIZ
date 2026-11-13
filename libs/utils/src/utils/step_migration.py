"""Old action steps to the steps of recipe format 1 (migration run A, names and parameters).

One function per old action. Each reads the step as an old recipe wrote it (with the column aliases the old wrangler
guessed: `columns`, `column`, `source`, `source_column`, `target_column`), writes every default that the old action
applied silently into the new step, and returns the new steps in order, so that the table is identical. A choice that
Polars defaults the same way is not written. What cannot be converted without a decision raises `NotConvertible` and
the migration reports it; nothing is guessed.

The differential test (`libs/transformer/tests/test_step_conversion.py`) runs the old action and the converted steps on
the same table for every case below.

Pure: no Polars, no engine. Consumed by: the migration tool (`recipe_migration.py`) and the differential test.

# @deps
# provides: function:convert_step, class:NotConvertible, constant:REMOVED_ACTIONS
# consumed_by: libs/utils/src/utils/recipe_migration.py, libs/transformer/tests/test_step_conversion.py
# doc: .claude/design/home_evidence/actions_and_polars_2026-11-13.md sections 15, 25, 26
# @end_deps
"""
from typing import Any, Callable, Dict, List, Optional

STRIP_CHARACTERS = ' \t\n\r"'
COLUMN_KEYS = ("columns", "column", "source", "source_column", "target_column")

# old actions that leave the vocabulary, with what to do instead
REMOVED_ACTIONS = {
    "percentile": "removed (it was rank divided by the row count, not a percentile); use polars_with_columns with pl.col(c).rank() / pl.len()",
    "value_counts": "removed; use polars_group_by with pl.len() and a named aggregation",
    "select_by_pattern": "removed; name the columns in polars_select",
    "sanitize_column_names": "removed; the slug and original_name of input_fields name the columns, or write a polars_rename mapping",
    "derive_categories": "removed; a lookup is a polars_join with a reference table as an ingredient",
    "scan_parquet": "engine function, not a recipe action",
    "sink_parquet": "engine function, not a recipe action",
}


class NotConvertible(ValueError):
    """The step needs a decision of the recipe author; the message says what to write."""


def _columns(step: dict) -> List[str]:
    """The column list as the old wrangler resolved it: the first of the alias keys, a text becomes a one-item list."""
    for key in COLUMN_KEYS:
        value = step.get(key)
        if value:
            return [value] if isinstance(value, str) else list(value)
    return []


def _text(value) -> str:
    """A Python literal of a value for a formula (strings, numbers, booleans, None, lists)."""
    return repr(value)


def _only(step: dict, *keys) -> dict:
    return {k: step[k] for k in keys if k in step and step[k] is not None}


def _with(named: Dict[str, str], step: dict) -> dict:
    out = {"action": "polars_with_columns", "named_exprs": named}
    if "comment" in step:
        out["comment"] = step["comment"]
    return out


def _single(step: dict, name: str) -> str:
    columns = _columns(step) if name == "columns" else None
    value = step.get(name) if columns is None else (columns[0] if columns else None)
    if not value:
        raise NotConvertible(f"{step.get('action')}: no column given")
    return value


# -- one converter per old action ----------------------------------------------------------------------------

def _cast(s):
    return [{"action": "polars_cast", "columns": _columns(s), "dtype": s["dtype"]}]


def _coalesce(s):
    cols = _columns(s)
    return [{"action": "polars_coalesce", "exprs": cols, "target_column": cols[0]}]


def _count_by_group(s):
    group = s["group_by"] if isinstance(s["group_by"], list) else [s["group_by"]]
    return [_with({s.get("new_column", "group_count"): f"pl.len().over({_text(group)})"}, s)]


def _cum(name):
    def convert(s):
        col = s.get("column") or _single(s, "columns")
        return [{"action": f"polars_{name}", "columns": [col], "target_column": s.get("target_column") or f"{col}_{'cumsum' if name == 'cum_sum' else 'cumcount'}"}]
    return convert


def _date_extract(s):
    col = s.get("column") or _single(s, "columns")
    parts = s.get("parts") or ["year"]
    named = {}
    for part in parts:
        if part not in ("year", "month", "day", "week", "weekday", "hour"):
            continue                                    # the old action ignored an unknown part silently
        named[f"{col}_{part}"] = f"pl.col({_text(col)}).dt.{part}()"
    return [_with(named, s)]


def _date_truncate(s):
    col = s.get("column") or _single(s, "columns")
    return [{"action": "polars_dt_truncate", "columns": [col], "every": s.get("every", "1mo")}]


def _describe(s):
    return [{"action": "polars_describe"}]


def _divide(s):
    n, d = s["numerator"], s["denominator"]
    return [_with({s["new_column"]: f"pl.col({_text(n)}).cast(pl.Float64) / pl.col({_text(d)}).cast(pl.Float64)"}, s)]


def _drop_duplicates(s):
    cols = _columns(s)
    out = {"action": "polars_unique", "keep": "first", "maintain_order": bool(s.get("maintain_order", True))}
    if cols:
        out["subset"] = cols
    return [out]


def _unique_rows(s):
    return [{"action": "polars_unique", "keep": "any", "maintain_order": bool(s.get("maintain_order", True))}]


def _drop_nulls(s):
    cols = _columns(s)
    return [{"action": "polars_drop_nulls", **({"subset": cols} if cols else {})}]


def _same_columns(new):
    def convert(s):
        return [{"action": new, "columns": _columns(s)}]
    return convert


def _fill_nulls(s):
    return [{"action": "polars_fill_null", "columns": _columns(s), "value": s["value"]}]


def _fill_nulls_direction(s):
    return [{"action": "polars_fill_null", "columns": _columns(s), "strategy": s.get("direction", "forward")}]


def _filter_one(op):
    def convert(s):
        return [{"action": "modif_filter", "column": s.get("column") or _single(s, "columns"), "op": op, "value": s["value"], "na": "remove"}]
    return convert


def _filter_range(s):
    col = _single(s, "columns")
    lo, hi = s.get("min"), s.get("max")
    if lo is not None and hi is not None:
        return [{"action": "modif_filter", "column": col, "op": "between", "value": [lo, hi], "na": "remove"}]
    if lo is not None:
        return [{"action": "modif_filter", "column": col, "op": "ge", "value": lo, "na": "remove"}]
    if hi is not None:
        return [{"action": "modif_filter", "column": col, "op": "le", "value": hi, "na": "remove"}]
    raise NotConvertible("filter_range without min and max returned every row; delete the step")


def _set_filter(op):
    def convert(s):
        return [{"action": "modif_filter", "column": s["column"], "op": op, "value": list(s["values"]), "na": "remove"}]
    return convert


def _horizontal(op):
    def convert(s):
        operation = s.get("operation", "sum")
        if operation not in ("sum", "min", "max", "mean"):
            raise NotConvertible(f"horizontal_stats: unknown operation {operation!r}")
        return [{"action": f"polars_{operation}_horizontal", "exprs": _columns(s), "target_column": s.get("target_column") or f"horizontal_{operation}"}]
    return convert


def _interpolate(s):
    return [{"action": "polars_interpolate", "columns": _columns(s)}]


def _as_list(value):
    return None if value is None else ([value] if isinstance(value, str) else list(value))


def _join(forced_how: Optional[str] = None):
    def convert(s):
        how = forced_how or s.get("how", "left")
        how = "full" if how == "outer" else how
        out = {"action": "polars_join", "right_ingredient": s["right_ingredient"]}
        on = s.get("on", s.get(True))
        if on:
            out["on"] = _as_list(on)
        else:
            out["left_on"], out["right_on"] = _as_list(s["left_on"]), _as_list(s["right_on"])
        out["how"] = how
        out["maintain_order"] = "right_left" if how == "right" else "left_right"
        return [out]
    return convert


def _label_if(s):
    ops = {">", ">=", "<", "<=", "==", "!="}
    if s["predicate"] not in ops:
        raise NotConvertible(f"label_if: unknown predicate {s['predicate']!r}")
    expr = (f"pl.when(pl.col({_text(s['column'])}) {s['predicate']} {_text(s['value'])})"
            f".then(pl.lit({_text(s.get('then'))})).otherwise(pl.lit({_text(s.get('otherwise'))}))")
    return [_with({s["new_column"]: expr}, s)]


def _list_join(s):
    col = s.get("column") or _single(s, "columns")
    out = {"action": "polars_list_join", "columns": [col], "separator": s.get("separator", ";")}
    if s.get("target_column") and s["target_column"] != col:
        out["target_column"] = s["target_column"]
    return [out]


def _list_slice(s):
    col = s.get("column") or _single(s, "columns")
    out = {"action": "polars_list_slice", "columns": [col], "offset": s.get("offset", 0)}
    if s.get("length") is not None:
        out["length"] = s["length"]
    if s.get("target_column") and s["target_column"] != col:
        out["target_column"] = s["target_column"]
    return [out]


def _mutate(s):
    target = s.get("column") or s.get("target_column")
    if not target:
        raise NotConvertible("mutate: no column given")
    return [_with({target: s["expression"]}, s)]


def _null_if(s):
    named = {c: f"pl.when(pl.col({_text(c)}) == {_text(s.get('value'))}).then(None).otherwise(pl.col({_text(c)}))" for c in _columns(s)}
    return [_with(named, s)]


def _pivot(s):
    out = {"action": "polars_pivot", "on": _as_list(s["on"]), "index": _as_list(s["index"]), "values": _as_list(s["values"]),
           "aggregate_function": s.get("aggregate_function", "first")}
    return [out]


def _recode(s):
    col, rules = s["column"], s.get("rules") or []
    target = s.get("new_column") or col
    default = next((r["default"] for r in rules if "default" in r), None)
    expr = None
    for rule in rules:
        c = f"pl.col({_text(col)})"
        if "matches" in rule:
            predicate = f"{c} == {_text(rule['matches'])}"
        elif "matches_any" in rule:
            predicate = f"{c}.is_in({_text(list(rule['matches_any']))})"
        elif "starts_with" in rule:
            predicate = f"{c}.cast(pl.String).str.starts_with({_text(rule['starts_with'])})"
        elif "ends_with" in rule:
            predicate = f"{c}.cast(pl.String).str.ends_with({_text(rule['ends_with'])})"
        elif "contains" in rule:
            predicate = f"{c}.cast(pl.String).str.contains({_text(rule['contains'])})"
        else:
            continue
        piece = f".when({predicate}).then(pl.lit({_text(rule['value'])}))"
        expr = (f"pl{piece}" if expr is None else expr + piece)
    formula = f"{expr}.otherwise(pl.lit({_text(default)}))" if expr else f"pl.lit({_text(default)})"
    return [_with({target: formula}, s)]


def _regex_extract(s):
    source = s.get("source") or s.get("target_column")
    out = {"action": "polars_str_extract", "columns": [source], "pattern": s["pattern"], "group_index": s.get("group", 1)}
    if s.get("target_column") and s["target_column"] != source:
        out["target_column"] = s["target_column"]
    return [out]


def _regex_replace(s):
    return [{"action": "polars_str_replace_all", "columns": _columns(s), "pattern": s["pattern"], "value": s.get("value", "")}]


def _rename(s):
    if s.get("mapping"):
        return [{"action": "polars_rename", "mapping": dict(s["mapping"])}]
    cols = _columns(s)
    if not s.get("new_name") or not cols:
        raise NotConvertible("rename: needs mapping, or columns and new_name")
    return [{"action": "polars_rename", "mapping": {cols[0]: s["new_name"]}}]


def _rename_columns(s):
    if s.get("mapping"):
        return [{"action": "polars_rename", "mapping": dict(s["mapping"])}]
    cols, names = _columns(s), s.get("new_names") or []
    if cols and names:
        return [{"action": "polars_rename", "mapping": dict(zip(cols, names))}]
    return _rename(s)


def _replace_values(s):
    mapping = {old: s.get("new_value") for old in s["to_replace"]}
    named = {c: f"pl.col({_text(c)}).replace_strict({_text(mapping)}, default=pl.col({_text(c)}))" for c in _columns(s)}
    return [_with(named, s)]


def _round(s):
    return [{"action": "polars_round", "columns": _columns(s), "decimals": s.get("decimals", 2)}]


def _sample(s):
    return [{"action": "polars_sample", "fraction": s.get("fraction", 0.1), "seed": s.get("seed", 0)}]


def _shift(s):
    col = s.get("column") or _single(s, "columns")
    n = s.get("n", 1)
    return [{"action": "polars_shift", "columns": [col], "n": n, "target_column": s.get("target_column") or f"{col}_shift_{n}"}]


def _sort(s):
    by = s.get("by") or _columns(s)
    by = [by] if isinstance(by, str) else list(by)
    out = {"action": "polars_sort", "by": by, "maintain_order": True}
    if s.get("descending") is not None:
        out["descending"] = s["descending"]
    return [out]


def _split_and_explode(s):
    col = _single(s, "columns")
    return [{"action": "polars_str_split", "columns": [col], "by": s.get("separator", ",")},
            {"action": "polars_explode", "columns": [col]}]


def _split_steps(source, sep, names, drop_source):
    steps = [{"action": "polars_str_splitn", "columns": [source], "by": sep, "n": len(names), "target_column": "_split_parts"},
             {"action": "polars_unnest", "columns": ["_split_parts"]},
             {"action": "polars_rename", "mapping": {f"field_{i}": n for i, n in enumerate(names)}}]
    return steps + ([{"action": "polars_drop", "columns": [source]}] if drop_source else [])


def _split_column(s):
    cols = _columns(s)
    source = cols[0] if cols else s.get("source") or s.get("target_column")
    return _split_steps(source, s.get("delimiter", s.get("separator", " ")), list(s["new_columns"]), bool(s.get("drop_source", False)))


def _split_column_to_parts(s):
    return _split_steps(s.get("column") or _single(s, "columns"), s.get("separator", "/"), list(s["new_columns"]), False)


def _split_to_list(s):
    return [{"action": "polars_str_split", "columns": _columns(s), "by": s.get("separator", ",")}]


def _strip_whitespace(s, strings=None):
    cols = _columns(s) or list(strings or [])
    if not cols:
        raise NotConvertible("strip_whitespace without columns means every text column: the migration needs the declared String fields of the schema")
    return [{"action": "polars_str_strip_chars", "columns": cols, "characters": STRIP_CHARACTERS}]


def _summarize(s):
    columns = _columns(s)
    agg = s.get("agg", "count")
    agg = agg if agg in ("count", "sum", "mean") else "count"        # the old action counted any unknown aggregation
    new_name = s.get("new_name")
    named = {(new_name if (new_name and len(columns) == 1) else f"{c}_{agg}"): f"pl.col({_text(c)}).{agg}()" for c in columns}
    group_by = s.get("group_by") or []
    return [{"action": "polars_group_by", "by": [group_by] if isinstance(group_by, str) else list(group_by),
             "maintain_order": True, "named_aggs": named}]


def _to_struct(s):
    cols, target = _columns(s), s["target_column"]
    return [_with({target: f"pl.struct({_text(cols)})"}, s), {"action": "polars_drop", "columns": cols}]


def _top_n_other(s):
    col, n = s["column"], s["n"]
    out = {"action": "step_top_n_other", "column": col, "n": n, "other_label": s.get("other_label", "Other"),
           "new_column": s.get("new_column") or f"{col}_top{n}"}
    if s.get("count_distinct"):
        out["count_distinct"] = s["count_distinct"]
    return [out]


def _unpivot(s):
    out = {"action": "polars_unpivot", "on": _as_list(s.get("on", s.get(True))), "variable_name": s.get("variable_name", "variable"),
           "value_name": s.get("value_name", "value")}
    if s.get("index"):
        out["index"] = _as_list(s["index"])
    return [out]


def _window_agg(s):
    col = s.get("column") or _single(s, "columns")
    function = s.get("function", "mean")
    if function not in ("mean", "sum", "min", "max", "count", "median", "std"):
        raise NotConvertible(f"window_agg: unknown function {function!r}")
    partition = _as_list(s.get("partition_by")) or []
    return [_with({s.get("target_column") or f"{col}_{function}": f"pl.col({_text(col)}).{function}().over({_text(partition)})"}, s)]


def _z_score(s):
    named = {f"{c}_zscore": f"(pl.col({_text(c)}) - pl.col({_text(c)}).mean()) / pl.col({_text(c)}).std()" for c in _columns(s)}
    return [_with(named, s)]


def _add_constant(s):
    return [_with({s["new_column"]: f"pl.lit({_text(s.get('value'))})"}, s)]


def _horizontal_bool(name):
    def convert(s):
        return [{"action": f"polars_{name}", "exprs": _columns(s), "target_column": s["target_column"]}]
    return convert


CONVERTERS: Dict[str, Callable] = {
    "cast": _cast, "coalesce": _coalesce, "count_by_group": _count_by_group,
    "cum_sum": _cum("cum_sum"), "cum_count": _cum("cum_count"),
    "date_extract": _date_extract, "date_truncate": _date_truncate, "describe_stats": _describe,
    "divide_columns": _divide, "drop_duplicates": _drop_duplicates, "unique": _drop_duplicates, "unique_rows": _unique_rows,
    "drop_nulls": _drop_nulls, "explode": _same_columns("polars_explode"), "unnest": _same_columns("polars_unnest"),
    "fill_nulls": _fill_nulls, "fill_nulls_direction": _fill_nulls_direction,
    "filter_eq": _filter_one("eq"), "filter_ne": _filter_one("ne"), "filter_gt": _filter_one("gt"), "filter_lt": _filter_one("lt"),
    "filter_range": _filter_range, "is_in": _set_filter("in"), "not_in": _set_filter("not_in"),
    "horizontal_stats": _horizontal(None), "interpolate": _interpolate,
    "join": _join(), "join_filter": _join("inner"),
    "label_if": _label_if, "list_join": _list_join, "list_slice": _list_slice, "mutate": _mutate, "null_if": _null_if,
    "pivot": _pivot, "recode_values": _recode, "regex_extract": _regex_extract, "regex_replace": _regex_replace,
    "rename": _rename, "rename_columns": _rename_columns, "replace_values": _replace_values, "round_numeric": _round,
    "sample": _sample, "shift": _shift, "sort": _sort, "split_and_explode": _split_and_explode, "split_column": _split_column,
    "split_column_to_parts": _split_column_to_parts, "split_to_list": _split_to_list, "summarize": _summarize,
    "to_struct": _to_struct, "top_n_other": _top_n_other, "unpivot": _unpivot, "window_agg": _window_agg, "z_score": _z_score,
    "add_constant": _add_constant, "all_horizontal": _horizontal_bool("all_horizontal"), "any_horizontal": _horizontal_bool("any_horizontal"),
}


def convert_step(step: dict, *, strings: Optional[List[str]] = None) -> List[dict]:
    """The new steps for one old step, in order. `strings` is the list of declared String fields of the schema, needed
    only by `strip_whitespace` without `columns`. Raises NotConvertible when a decision of the author is needed."""
    name = step.get("action")
    if name in REMOVED_ACTIONS:
        raise NotConvertible(f"{name}: {REMOVED_ACTIONS[name]}")
    if name in ("keep_columns", "drop_columns"):
        raise NotConvertible(f"{name}: converted in run B (polars_select, polars_drop)")
    if name == "strip_whitespace":
        converted = _strip_whitespace(step, strings)
    elif name in CONVERTERS:
        converted = CONVERTERS[name](step)
    else:
        raise NotConvertible(f"unknown action {name!r}")
    comment = step.get("comment")
    if comment and converted and "comment" not in converted[0]:
        converted[0] = {**converted[0], "comment": comment}
    return converted
