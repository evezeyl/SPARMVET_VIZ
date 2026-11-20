"""The independent oracle of the lineage walk tests (LBFB step 0a): a replay of a recipe in plain Polars that knows nothing of the walk.

It reads the recipe as a dictionary and the source tables as data frames, applies every step with the Polars call the step names, and gives
(a) the engine's plan of every place as a `PlanBook` (the names and types after every step; a failure is a `PlanFailure` with Polars' own
sentence, and so is everything below it), (b) the frames, (c) the marker check (`marker_holders`): mark the values of a source column,
replay, and see which tables still hold marked values; that finds where a column really is, through renames and joins, without any rule
of the walk, (d) `after_filter`: replay with one filter step added at a place, to see which tables change and what a table holds.

It uses only the Polars calls a test recipe needs: filter (`modif_filter` with the simple operators written here), rename, drop, select, join,
with_columns (a formula text evaluated with `pl`), cast, group_by, fill_null, unpivot and sort. It is test code: it never imports the walk, `step_effects`, `recipe_graph` or
anything of `app`.

Run with the tests of libs/utils.
"""
from __future__ import annotations

import copy
from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Set, Tuple

import polars as pl

from utils.plan_book import Plan, PlanBook, PlanFailure

MARK = "~m"


@dataclass
class Replay:
    plans: PlanBook
    frames: Dict[Tuple[str, int], pl.DataFrame]
    failures: Dict[Tuple[str, int], str]

    def end(self, node: str) -> Optional[pl.DataFrame]:
        ks = [k for (n, k) in self.frames if n == node]
        return self.frames[(node, max(ks))] if ks else None


def _steps(body: Any, tier: str) -> List[dict]:
    held = body.get(tier) if isinstance(body, dict) else None
    steps = held.get("steps") if isinstance(held, dict) else None
    return list(steps) if isinstance(steps, list) else []


def _filter_expr(step: Mapping[str, Any]) -> pl.Expr:
    col, op, value = pl.col(step["column"]), step["op"], step.get("value")
    keep_missing = step.get("na", "remove") == "keep"
    expr = {"eq": col == value, "ne": col != value, "gt": col > value, "ge": col >= value, "lt": col < value, "le": col <= value,
            "in": col.is_in(value if isinstance(value, list) else [value]), "not_in": ~col.is_in(value if isinstance(value, list) else [value])}[op]
    return (expr | col.is_null()) if keep_missing else expr.fill_null(False)


def apply_step(df: pl.DataFrame, step: Mapping[str, Any], ends: Mapping[str, pl.DataFrame]) -> pl.DataFrame:
    action = step["action"]
    if action == "modif_filter":
        return df.filter(_filter_expr(step))
    if action == "polars_rename":
        return df.rename(dict(step["mapping"]), strict=step.get("strict", True))
    if action == "polars_drop":
        return df.drop(*step["columns"])
    if action == "polars_select":
        return df.select(step["exprs"])
    if action == "polars_sort":
        return df.sort(step["by"], maintain_order=True)
    if action == "polars_with_columns":
        return df.with_columns(**{name: eval(text, {"pl": pl}) for name, text in step["named_exprs"].items()})   # noqa: S307 - test formulas
    if action == "polars_group_by":
        return df.group_by(step["by"], maintain_order=True).agg(**{name: eval(text, {"pl": pl}) for name, text in step["named_aggs"].items()})   # noqa: S307 - test formulas
    if action == "polars_fill_null":
        return df.with_columns(pl.col(step["columns"]).fill_null(step["value"]))
    if action == "polars_unpivot":
        return df.unpivot(on=step["on"], index=step["index"], variable_name=step["variable_name"], value_name=step["value_name"])
    if action == "polars_cast":
        return df.cast({c: getattr(pl, step["dtype"]) for c in step["columns"]})
    if action == "polars_join":
        right = ends[f"T1:{step['right_ingredient']}"]
        how = step.get("how", "left")
        kwargs: Dict[str, Any] = {"how": how, "suffix": step.get("suffix") or "_right"}
        if how in ("left", "inner"):
            kwargs["maintain_order"] = "left"
        if "on" in step:
            return df.join(right, on=step["on"], **kwargs)
        return df.join(right, left_on=step["left_on"], right_on=step["right_on"], **kwargs)
    raise ValueError(f"the oracle does not know the action {action}")


def _plan_of(df: pl.DataFrame) -> Plan:
    return Plan.of((name, str(dtype)) for name, dtype in df.schema.items())


def replay(recipe: Mapping[str, Any], tables: Mapping[str, pl.DataFrame]) -> Replay:
    """Replay every table of the recipe in order: sources, joins, second tiers, plots."""
    entries: Dict[Tuple[str, int], Any] = {}
    frames: Dict[Tuple[str, int], pl.DataFrame] = {}
    failures: Dict[Tuple[str, int], str] = {}
    ends: Dict[str, pl.DataFrame] = {}
    failed_ends: Dict[str, str] = {}
    schemas: Dict[str, Any] = {}
    for section in ("data_schemas", "additional_datasets_schemas"):
        schemas.update(recipe.get(section) or {})
    if "metadata_schema" in recipe:
        schemas["metadata_schema"] = recipe["metadata_schema"]
    joins: Dict[str, Any] = dict(recipe.get("joins") or {})
    plots: Dict[str, Any] = {}
    for group in (recipe.get("analysis_groups") or {}).values():
        plots.update(group.get("plots") or {})

    def run(node: str, start: Optional[pl.DataFrame], start_failure: Optional[str], steps: List[dict]) -> None:
        if start is None:
            for k in range(len(steps) + 1):
                entries[(node, k)] = PlanFailure(start_failure or "", node, 0)
                failures[(node, k)] = start_failure or ""
            failed_ends[node] = start_failure or ""
            return
        current = start
        frames[(node, 0)] = current
        entries[(node, 0)] = _plan_of(current)
        for k, step in enumerate(steps, start=1):
            try:
                current = apply_step(current, step, ends)
            except Exception as error:   # noqa: BLE001 - Polars raises several kinds; the sentence is the data
                for j in range(k, len(steps) + 1):
                    entries[(node, j)] = PlanFailure(str(error), node, k)
                    failures[(node, j)] = str(error)
                failed_ends[node] = str(error)
                return
            frames[(node, k)] = current
            entries[(node, k)] = _plan_of(current)
        ends[node] = current

    for sid, body in schemas.items():
        entries[(f"DS:{sid}", 0)] = _plan_of(tables[sid])
        frames[(f"DS:{sid}", 0)] = tables[sid]
    for sid, body in schemas.items():
        run(f"T1:{sid}", tables[sid], None, _steps(body, "tier1"))
    for jid, body in joins.items():
        ingredients = [i["dataset_id"] for i in body.get("ingredients", [])]
        base = f"T1:{ingredients[0]}" if ingredients else None
        steps = _steps(body, "tier1")
        right_failed = next((failed_ends[f"T1:{s['right_ingredient']}"] for s in steps if f"T1:{s.get('right_ingredient')}" in failed_ends), None)
        if base in ends and right_failed is None:
            run(f"T1:{jid}", ends[base], None, steps)
        else:
            run(f"T1:{jid}", None, failed_ends.get(base, right_failed or ""), steps)
    for cid, body in {**schemas, **joins}.items():
        t1 = f"T1:{cid}"
        run(f"T2:{cid}", ends.get(t1), failed_ends.get(t1), _steps(body, "tier2"))
    for pid, entry in plots.items():
        t2 = f"T2:{entry['target_dataset']}"
        run(f"T3:{pid}", ends.get(t2), failed_ends.get(t2), _steps(entry, "tier3"))
    return Replay(PlanBook(entries), frames, failures)


def marked(tables: Mapping[str, pl.DataFrame], marks: Mapping[str, List[str]]) -> Dict[str, pl.DataFrame]:
    """Copies of the tables in which every value of the marked columns ends with MARK (text columns only)."""
    out = dict(tables)
    for table, columns in marks.items():
        out[table] = tables[table].with_columns(*[(pl.col(c).cast(pl.String) + MARK).alias(c) for c in columns])
    return out


def holds_mark(df: pl.DataFrame) -> bool:
    return any(df[c].dtype == pl.String and df[c].drop_nulls().str.contains(MARK, literal=True).any() for c in df.columns)


def marker_holders(recipe: Mapping[str, Any], tables: Mapping[str, pl.DataFrame], marks: Mapping[str, List[str]]) -> Set[str]:
    """The node ids whose table (after all their steps) holds a marked value: where the marked source columns really are.
    A step that rewrites the values of a marked column (a recode) makes the mark disappear there: such a node is not reported."""
    result = replay(recipe, marked(tables, marks))
    nodes = {n for (n, _) in result.frames}
    return {n for n in nodes if not n.startswith("DS:") and result.end(n) is not None and holds_mark(result.end(n))}  # type: ignore[arg-type]


def with_audit_filter(recipe: Mapping[str, Any], place: str, column: str, value: Any) -> Dict[str, Any]:
    """A copy of the recipe with one filter (remove the rows whose `column` equals `value`) added at the END of the list of a place (`T1:C`, `T2:C`, `T3:p`)."""
    copy_ = copy.deepcopy(dict(recipe))
    tier, name = place.split(":", 1)
    step = {"action": "modif_filter", "column": column, "op": "ne", "value": value, "na": "keep"}
    if tier == "T3":
        for group in copy_["analysis_groups"].values():
            if name in group["plots"]:
                group["plots"][name].setdefault("tier3", {}).setdefault("steps", []).append(step)
        return copy_
    key = "tier1" if tier == "T1" else "tier2"
    for section in ("data_schemas", "additional_datasets_schemas", "joins"):
        if name in (copy_.get(section) or {}):
            copy_[section][name].setdefault(key, {}).setdefault("steps", []).append(step)
            return copy_
    if name == "metadata_schema":
        copy_["metadata_schema"].setdefault(key, {}).setdefault("steps", []).append(step)
    return copy_


def changed_nodes(recipe: Mapping[str, Any], tables: Mapping[str, pl.DataFrame], after: Mapping[str, Any]) -> Set[str]:
    """The nodes (T1, T2, T3) whose final table differs between two replays (the audit step moved them)."""
    base, other = replay(recipe, tables), replay(after, tables)
    nodes = {n for (n, _) in base.frames if not n.startswith("DS:")}
    return {n for n in nodes if base.end(n) is None or other.end(n) is None or not base.end(n).equals(other.end(n))}  # type: ignore[union-attr]
