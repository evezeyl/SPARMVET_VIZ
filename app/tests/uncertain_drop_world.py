"""A small recipe on disk for the tests of a drop the walk cannot follow (D-0449 built them, D-0460 turned the rule round): tables written as files, a recipe written as YAML, the real
engine, no shipped file.

`World` writes the tables of a recipe that a test describes (columns, tier steps, joins, plots), composes the engine's plan of it, and answers the two questions:
what does the gate say about a drop (the facts, the refusal), and what does the real engine build WITH the drop (`drop_built`: the drop written as a step of the recipe's own author,
the only way to ask the engine, because the gate refuses to write it as an audit step: D-0460). Nothing is stubbed: the tables are built by the same `materialize_tier1`,
`materialize_tier2` and `materialize_tier3` as the app, and an audit copy that the gate lets through is run by `run_audit`.
"""
from __future__ import annotations

import copy
import dataclasses
import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import polars as pl
import yaml

from app.modules.audit_run import AuditRunError, run_audit
from app.modules.cache_keys import ResolvedRecipe, clear_data_analysis_recipe_cache, load_data_analysis_recipe, loaded_from_resolved
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from utils import key_drop
from utils.audit_copy import AuditStep, add_step, start_audit, with_audit_steps
from utils.recipe_tiers import AUDIT_COMMENT, collection_bodies, plot_entries
from utils.plan_book import PlanBook
from utils.recipe_graph import build_graph

RID = "tiny"
AUD = "1a2b3c4d"


def step_drop(*columns: str) -> dict:
    return {"action": "polars_drop", "columns": list(columns)}


@dataclass
class Built:
    """What the engine built for a recipe: `tables` (name -> frame), or `error` (the sentence the user would read) when a table could not be built."""
    tables: Dict[str, pl.DataFrame] = field(default_factory=dict)
    error: Optional[str] = None


class World:
    def __init__(self, root: Path, tables: Dict[str, pl.DataFrame], schemas: Dict[str, dict], joins: Optional[Dict[str, dict]] = None, plots: Optional[Dict[str, dict]] = None) -> None:
        self.root = root
        self.data, self.recipes = root / "data", root / "recipes"
        for d in (self.data, self.recipes):
            d.mkdir(parents=True, exist_ok=True)
        for name, frame in tables.items():
            frame.write_csv(self.data / f"{name}.tsv", separator="\t")
        raw: Dict[str, Any] = {"id": RID, "spec_version": 1, "data_engine": "python-polars", "plot_engine": "python-plotnine", "info": {"label": "Tiny"},
                               "data_schemas": {}, "joins": dict(joins or {}),
                               "analysis_groups": {"g": {"ui_label": "G", "plots": {pid: {"ui_label": pid, **body} for pid, body in (plots or {}).items()}}}}
        for name, body in schemas.items():
            fields = {c: {"original_name": c, "type": "Int64" if tables[name][c].dtype == pl.Int64 else "String", "label": c, **({"is_entity_id": True} if c == "sample_id" else {})}
                      for c in tables[name].columns}
            raw["data_schemas"][name] = {"source": {"type": "local_tsv", "path": str(self.data / f"{name}.tsv")}, "null_values": [], "strip": False,
                                         "input_fields": fields, "tier1": {"steps": list(body.get("tier1", []))},
                                         **({"tier2": {"steps": list(body["tier2"])}} if body.get("tier2") else {})}
        (self.recipes / f"{RID}.yaml").write_text(yaml.safe_dump(raw, sort_keys=False))
        clear_data_analysis_recipe_cache()
        self.orch = DataOrchestrator(self.recipes, self.data)
        self.original = load_data_analysis_recipe(self.recipes / f"{RID}.yaml")
        self.plans: PlanBook = compose_plan_book(self.orch, RID, self.original)

    # -- what the gate says
    def facts(self, place: str, column: str, with_plan: bool = True):
        return key_drop.DropGate(self.original.raw, self.plans if with_plan else None).facts(place, column)

    # -- what the engine builds
    def build(self, loaded, out: Path) -> Built:
        """Every table of a recipe (the original or a copy) built by the engine's own functions, into the folder `out`; a plot's table is named `T3:<plot>`."""
        return build_all(self.orch, RID, loaded, out)

    def original_built(self) -> Built:
        return self.build(self.original, self.root / "built_original")

    def copy_with(self, place: str, step: dict, blind: bool = False):
        """The audit copy with one step added by `add_step`; `blind`: the gate gets no plan of the engine (names the recipe declares only), as a caller that has no engine."""
        audit = start_audit(self.original.raw, AUD)
        add_step(audit, place, step, "because", plans=None if blind else self.plans)
        return audit

    def hand_made_audit(self, place: str, step: dict):
        """An audit copy with the step written by hand, past the gate (what a file or an old session could hold): for the tests that ask what the engine and the run say to it."""
        audit = start_audit(self.original.raw, AUD)
        step_id = f"audit_{AUD}_1"
        audit.recipe = with_audit_steps(self.original.raw, [AuditStep(place, step_id, {**step, "id": step_id, AUDIT_COMMENT: "because"})])
        audit.created = 1
        return audit

    def audit_built(self, audit) -> Built:
        return self.build(loaded_from_resolved(self.original, audit.recipe, self.plans), self.root / "built_audit")

    def drop_built(self, place: str, *columns: str) -> Built:
        """What the engine builds if the drop were written: the drop is a step of the recipe's own author at the end of the list of `place` (an audit step cannot be written there:
        the gate refuses it, D-0460)."""
        return self.build(author_version(self.original, with_author_step(self.original.raw, place, step_drop(*columns))), self.root / "built_drop")

    def run(self, audit):
        """The run of the copy as HOME runs it (`run_audit`): the run, or the AuditRunError."""
        return run_audit(self.orch, RID, audit.recipe, self.root / "run_original", self.root / "run_audit")


def build_all(orch: DataOrchestrator, rid: str, loaded, out: Path) -> Built:
    """Every table of `loaded` (T1 and T2 of each table and join, T3 of each plot) built by `materialize_tier1/2/3`, or the sentence of the first that cannot be built."""
    out.mkdir(parents=True, exist_ok=True)
    result = Built()
    try:
        keys = orch.compute_data_analysis_recipe_keys(rid, loaded=loaded)
        for table in build_graph(loaded.raw).collections():
            path = out / f"{table}.parquet"
            result.tables[f"T1:{table}"] = orch.materialize_tier1(rid, table, path, keys=keys, loaded=loaded).collect()
            result.tables[f"T2:{table}"] = orch.materialize_tier2(rid, table, path, keys=keys, loaded=loaded).collect()
        for group in loaded.raw["analysis_groups"].values():
            for plot_id in group["plots"]:
                result.tables[f"T3:{plot_id}"] = orch.materialize_tier3(rid, plot_id, out, keys=keys, loaded=loaded).collect()
    except Exception as error:   # noqa: BLE001 - the sentence is the data
        tip = getattr(error, "tip", None)
        result.error = str(error).strip() + (f" ({tip})" if tip else "")
    return result


def with_author_step(raw: dict, place: str, step: dict) -> dict:
    """A deep copy of the recipe with `step` added at the END of the author's list of steps of `place` (`T1:<table>`, `T2:<table>` or `T3:<plot>`)."""
    out = copy.deepcopy(raw)
    tier, _, name = place.partition(":")
    body = plot_entries(out)[name] if tier == "T3" else collection_bodies(out)[name]
    body.setdefault({"T1": "tier1", "T2": "tier2", "T3": "tier3"}[tier], {"steps": []}).setdefault("steps", []).append(copy.deepcopy(step))
    return out


def author_version(original, raw: dict):
    """The engine's form of the recipe `raw` taken as its own original (no audit steps): the author's version, test only. The engine would refuse an audit copy that differs from
    its original outside the audit steps; here nothing is audit."""
    return dataclasses.replace(loaded_from_resolved(original, raw), config=ResolvedRecipe(raw, original_raw=raw))


def changed_tables(before: Built, after: Built) -> set:
    """The names of the tables that differ between two builds (a table that is only in one of them counts)."""
    return {n for n in set(before.tables) | set(after.tables) if n not in before.tables or n not in after.tables or not before.tables[n].equals(after.tables[n])}



def tsv_frame(**columns: Sequence) -> pl.DataFrame:
    return pl.DataFrame(columns)


def lost_and_rest(original: pl.DataFrame, after: pl.DataFrame):
    """(the columns the drop took out, the columns it added, whether every column both tables have holds the same values in the same rows): the drop took out what it was asked to and
    changed no other value."""
    common = [c for c in original.columns if c in after.columns]
    return set(original.columns) - set(after.columns), set(after.columns) - set(original.columns), original.select(common).equals(after.select(common))
