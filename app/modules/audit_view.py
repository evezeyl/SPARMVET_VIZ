"""What HOME and the export read when audit steps are written at a place (tier 1, tier 2 or tier 3) (HOME audit, demo steps 2 and 7).

One object per open recipe: it makes the audit copy of the recipe from the committed place nodes (`audit_places.audit_copy_for`), runs it (`audit_run.run_audit`, which builds
into a folder of its own and never touches the stored tables of the original) and hands out the table a plot reads in the copy. Every reader of the audited plot (the plot, the
T3 table, the filter dialog, the results bundle) asks this one object, so they cannot differ ("a plot equals its table").

- No place node: nothing is built, the audit folder is removed when it exists (a stored table that cannot be served today is not left for a later bug,
  `rules_verification_testing.md` section 9) and every plot reads its original table (the answer is None).
- Place nodes (tier 1, tier 2 or tier 3): the run is made once per (recipe, data, nodes); a plot no step reaches reads its original table (None) even when a step beside it cannot be applied (that error is shown at the plots that step reaches); a plot a step reaches (written at its own tier 3 or at a table it is built from) reads the lazy table of the copy.
- A step that cannot be applied raises `AuditRunError`, naming the step and its place: never skipped (D-0102). The caller shows it in the place of the plot.

Pure of Shiny. Consumed by: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/tests/test_audit_view.py.

# @deps
# provides: class:PlaceAudit (run_of, plot_lazy, table_lazy, affected_plots, forget), constant:AUDIT_ERRORS
# consumes: app/modules/audit_places.py (audit_copy_for, nodes_signature), app/modules/audit_run.py (run_audit, AuditRun), app/modules/cache_keys.py (load_data_analysis_recipe), app/modules/orchestrator.py (DataOrchestrator)
# consumed_by: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/audit_trial.py, app/tests/test_audit_view.py
# doc: .claude/rules/ui_implementation_contract.md#12g, .claude/knowledge/architecture_decisions.md#adr-101
# @end_deps
"""
from __future__ import annotations

import shutil
from pathlib import Path
from typing import Any, Callable, Iterable, List, Optional

from app.modules.audit_places import audit_copy_for, nodes_reaching_node, nodes_reaching_plot, nodes_signature
from app.modules.audit_run import AuditRun, AuditRunError, run_audit
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator, InputsChanged
from blueprint_arch.t3_translator import UntranslatableNode
from utils.audit_copy import AuditCopyError
from utils.plan_book import PlanBook
from utils.recipe_graph import RecipeGraphError, build_graph

# What the audit copy raises when a committed step cannot be made into a step of the copy or cannot be run, each with a plain sentence that names the step and its place:
# every reader shows it in the place of the table or the plot, never skips the step (D-0102).
AUDIT_ERRORS = (AuditRunError, AuditCopyError, UntranslatableNode)


class PlaceAudit:
    """The audit of one recipe whose steps are written at places. `original_dir`: the stored tables of the original; `audit_dir`: the folder of the copy's own tables
    (not inside `original_dir`, `run_audit` refuses it)."""

    def __init__(self, orchestrator: DataOrchestrator, original_dir: Path, audit_dir: Path) -> None:
        self.orch = orchestrator
        self.original_dir = Path(original_dir)
        self.audit_dir = Path(audit_dir)
        self._memo: Optional[tuple] = None          # (signature, AuditRun)

    def forget(self) -> None:
        """Drop the memo of the last run. `PlaceTrial.apply_trial` calls it after it moved stored tables into the audit folder: a run object held from before points at files whose content is now
        the new state (an `AuditRun` reads a stored table by path, with no key check), so it must not be served again for its old list."""
        self._memo = None

    def run_of(self, recipe_id: str, nodes: Iterable[dict], plans: Optional[PlanBook] = None) -> Optional[AuditRun]:
        """The run of the copy made from `nodes` (the committed place nodes), or None when there is none. Raises `AuditRunError`, `AuditCopyError` or `UntranslatableNode`
        with a plain sentence when the copy cannot be made or run; nothing is kept then."""
        listed = list(nodes)
        if not listed:
            self._memo = None
            shutil.rmtree(self.audit_dir, ignore_errors=True)
            return None
        keys = self.orch.compute_data_analysis_recipe_keys(recipe_id)
        signature = (recipe_id, keys.data_analysis_recipe_sha256, keys.data_batch_hash, nodes_signature(listed))
        if self._memo is not None and self._memo[0] == signature:
            return self._memo[1]
        self._memo = None
        original = load_data_analysis_recipe(self.orch.data_analysis_recipes_dir / f"{recipe_id}.yaml")
        audit = audit_copy_for(original.raw, listed, plans)
        run = run_audit(self.orch, recipe_id, audit.recipe, self.original_dir, self.audit_dir)
        self._memo = (signature, run)
        return run

    def plot_lazy(self, recipe_id: str, plot_id: str, nodes: Iterable[dict], plans: Optional[PlanBook] = None,
                  told: Optional[Callable[[InputsChanged], None]] = None) -> Optional[Any]:
        """The table `plot_id` reads in the copy, a Polars lazy frame (typed `Any`: this file names no engine); None when there is no copy or no step reaches the plot (neither at its own tier 3 nor at a table it is built from): it then reads its original table."""
        listed = list(nodes)
        if listed and not self._some_step_reaches(recipe_id, listed, plot_id):
            return None                       # no step reaches this plot: it reads its original table, and a step that cannot run elsewhere is not its error
        run = self.run_of(recipe_id, listed, plans)
        if run is None:
            return None
        for text in run.inputs_changed:                 # a table of the run was built while its inputs changed and was not stored: the caller is told, as for every build
            if told is not None:
                told(InputsChanged(text))
        return run.plot_table(plot_id, told)

    def table_lazy(self, recipe_id: str, table: str, tier: str, nodes: Iterable[dict], plans: Optional[PlanBook] = None,
                   told: Optional[Callable[[InputsChanged], None]] = None) -> Optional[Any]:
        """The AUDITED table `table` at `tier` ("T1" or "T2") in the copy, a Polars lazy frame (the table HOME's T1 and T2 views show in Audit mode and the export writes beside the
        original, D-0622, D-0619); None when no committed step is written at a place the table is built from at that tier, or when the copy leaves the table as it is: the view then shows
        the original. As `plot_lazy`, a step that cannot run is not the error of a table it does not reach."""
        listed = list(nodes)
        if not listed:
            return None
        try:
            graph = build_graph(load_data_analysis_recipe(self.orch.data_analysis_recipes_dir / f"{recipe_id}.yaml").raw)
            if all(graph.has_node(n.get("place") or "") for n in listed) and not nodes_reaching_node(graph, listed, f"{tier}:{table}"):
                return None
        except (RecipeGraphError, KeyError):
            pass                              # the graph cannot be made: the run says why
        run = self.run_of(recipe_id, listed, plans)
        if run is None:
            return None
        for text in run.inputs_changed:
            if told is not None:
                told(InputsChanged(text))
        return run.audited_table_lazy(table, tier)

    def _some_step_reaches(self, recipe_id: str, nodes: List[dict], plot_id: str) -> bool:
        """Whether any committed step is written at a place the plot is built from (its own tier 3 or a table above it). A step at a place the recipe does not have counts as
        reaching every plot, so that the error of that step is shown and never silenced. When the recipe's graph cannot be made, the answer is yes (the run then says why)."""
        try:
            graph = build_graph(load_data_analysis_recipe(self.orch.data_analysis_recipes_dir / f"{recipe_id}.yaml").raw)
        except (RecipeGraphError, KeyError):
            return True
        if any(not graph.has_node(n.get("place") or "") for n in nodes):
            return True
        return bool(nodes_reaching_plot(graph, nodes, plot_id))

    def affected_plots(self, recipe_id: str, nodes: Iterable[dict], plans: Optional[PlanBook] = None) -> List[str]:
        """The plots whose table differs in CONTENT between the original and the copy, in the order of the recipe (ADR-101 point 6: a step that removes nothing affects none)."""
        run = self.run_of(recipe_id, nodes, plans)
        return [] if run is None else run.affected_plots
