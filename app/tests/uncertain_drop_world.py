"""A small recipe on disk for the tests of a drop the walk cannot follow (D-0449): tables written as files, a recipe written as YAML, the real engine, no shipped file.

`World` writes the tables of a recipe that a test describes (columns, tier steps, joins, plots), composes the engine's plan of it, and answers the two questions of D-0449:
what does the gate say about a drop (the facts, the refusal, the warning), and what does the real engine build when the drop is written (`built`: every table of the original
and of the copy, read through `DataOrchestrator`, or the plain error). Nothing is stubbed: the copy is run by `run_audit` and the tables are built by the same
`materialize_tier1`, `materialize_tier2` and `materialize_tier3` as the app.
"""
from __future__ import annotations

import shutil
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, List, Optional, Sequence

import polars as pl
import yaml

from app.modules.audit_run import AuditRunError, run_audit
from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe, loaded_from_resolved
from app.modules.orchestrator import DataOrchestrator
from app.modules.plan_composer import compose_plan_book
from utils import key_drop
from utils.audit_copy import add_step, start_audit
from utils.plan_book import PlanBook

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
            fields = {c: {"original_name": c, "type": "Int64" if tables[name][c].dtype == pl.Int64 else "String", "label": c, **({"is_entity_key": True} if c == "sample_id" else {})}
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
        out.mkdir(parents=True, exist_ok=True)
        result = Built()
        try:
            keys = self.orch.compute_data_analysis_recipe_keys(RID, loaded=loaded)
            graph_tables = list(loaded.raw["data_schemas"]) + list(loaded.raw.get("joins") or {})
            for table in graph_tables:
                path = out / f"{table}.parquet"
                result.tables[f"T1:{table}"] = self.orch.materialize_tier1(RID, table, path, keys=keys, loaded=loaded).collect()
                result.tables[f"T2:{table}"] = self.orch.materialize_tier2(RID, table, path, keys=keys, loaded=loaded).collect()
            for group in loaded.raw["analysis_groups"].values():
                for plot_id in group["plots"]:
                    result.tables[f"T3:{plot_id}"] = self.orch.materialize_tier3(RID, plot_id, out, keys=keys, loaded=loaded).collect()
        except Exception as error:   # noqa: BLE001 - the sentence is the data
            tip = getattr(error, "tip", None)
            result.error = str(error).strip() + (f" ({tip})" if tip else "")
        return result

    def original_built(self) -> Built:
        return self.build(self.original, self.root / "built_original")

    def copy_with(self, place: str, step: dict, blind: bool = False):
        """The audit copy with one step added by `add_step`; `blind`: the gate gets no plan of the engine (names the recipe declares only), as a caller that has no engine."""
        audit = start_audit(self.original.raw, AUD)
        add_step(audit, place, step, "because", plans=None if blind else self.plans)
        return audit

    def audit_built(self, audit) -> Built:
        return self.build(loaded_from_resolved(self.original, audit.recipe, self.plans), self.root / "built_audit")

    def run(self, audit):
        """The run of the copy as HOME runs it (`run_audit`): the run, or the AuditRunError."""
        return run_audit(self.orch, RID, audit.recipe, self.root / "run_original", self.root / "run_audit")


def tsv_frame(**columns: Sequence) -> pl.DataFrame:
    return pl.DataFrame(columns)


def lost_and_rest(original: pl.DataFrame, after: pl.DataFrame):
    """(the columns the drop took out, the columns it added, whether every column both tables have holds the same values in the same rows): the drop took out what it was asked to and
    changed no other value."""
    common = [c for c in original.columns if c in after.columns]
    return set(original.columns) - set(after.columns), set(after.columns) - set(original.columns), original.select(common).equals(after.select(common))
