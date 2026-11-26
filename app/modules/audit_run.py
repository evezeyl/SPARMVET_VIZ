# engine: python-polars (reads the stored tables of an audit copy with Parquet scans, counts their rows and compares two tables; hands out the lazy table a plot reads)
"""A run of an audit copy without a screen: which tables and plots of the copy are the original's and which are rebuilt (piece A5 of slice A, changed over to the second list `audit_steps` in piece C-1 of slice C of the HOME audit redesign).

Serves the audit that the next slices put on the screen. Nothing a user sees is wired to it yet.

Inputs: the orchestrator (`DataOrchestrator`), the id of the recipe, the audit copy (`utils.audit_copy`, the resolved dictionary `AuditCopy.recipe`: each tier holds the author's `steps` and the audit's `audit_steps`), the folder of the
stored tables of the ORIGINAL and a SEPARATE folder for the stored tables of the audit ("its own folder, never in the anchors folder",
`home_audit_steps.md` section 7.1). Output: an `AuditRun`, a plain record of what was reused, what was built and which plots are affected.

How: the copy and the original are built by the SAME engine functions (`DataOrchestrator.materialize_tier1`, `materialize_tier2`,
`materialize_tier3`); the copy is handed to them as a recipe (`cache_keys.loaded_from_resolved`, the `loaded` argument). "Nothing is ever copied: a stage
is either reused or recomputed":
- a table whose key in the copy EQUALS its key in the original is not rebuilt and not copied: it is read from the original's stored table (the original's
  table is stored first when it was not, as the app does);
- a table whose key differs is built into the audit's own folder (its Tier 1 and its Tier 2 separately: a step at tier 2 rebuilds the Tier 2 only and
  reads the original's Tier 1); the engine runs the author's `steps`, then the `audit_steps` of the tier (`utils.recipe_tiers.step_list`);
- a plot has no stored table (the tier-3 reader is lazy, A4): equal keys mean the same table; different keys mean the two tables are built and compared.

A plot is AFFECTED when the CONTENT of its table differs between the original and the audit run (ADR-101 point 6: "equal keys imply identical data;
different keys do not imply different data"). A filter that removes nothing moves a key and no row: that plot is not affected.

A step that the engine cannot apply is refused, naming the id of the step and its place; never skipped (D-0102). A table built while its inputs changed
(a data file) is returned and not stored, as for every caller of a build; the run says so in `AuditRun.inputs_changed`, never silently. The audit folder holds only what the
copy needs: a table that is the original's again (the step was removed) is taken out of it at once.

PROVISIONAL: the names and fields of the result; the words of `source` (`original`, `audit store`, `built`); that the run checks the copy with
`integrity_errors` (which also refuses an action that is not one of `AUDIT_ACTIONS`) and not with the checker's audit profile (it needs the registries; the
engine refuses what it cannot apply).

Consumed by: app/tests/test_audit_run.py. If deleted: nothing runs a copy yet; the slices that put the audit on the screen need it.

# @deps
# provides: function:run_audit, function:row_count, function:same_table, function:compare_tables, class:AuditRun, class:TableRun, class:PlotRun, class:AuditRunError
# consumes: app/modules/build_failure.py (short_engine_text: the sentence of an audit step that cannot be applied has no plan of the engine), app/modules/plan_composer.py (compose_plan_book: the engine's plan of the original, handed to the check of every copy), app/modules/orchestrator.py (materialize_tier1, materialize_tier2, materialize_tier3 with a handed recipe), app/modules/cache_keys.py (loaded_from_resolved, load_data_analysis_recipe), libs/utils/src/utils/audit_copy.py, libs/utils/src/utils/recipe_graph.py, libs/transformer/src/transformer/anchor.py (read_anchor_if_key)
# consumed_by: app/tests/test_audit_run.py, app/modules/audit_trial.py
# doc: .claude/knowledge/architecture_decisions.md#adr-101, .claude/knowledge/architecture_decisions.md#adr-105, .claude/design/home_audit_steps.md (section 7.1)
# @end_deps
"""
import copy
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Dict, List, Optional, Tuple

import polars as pl

from app.modules.build_failure import short_engine_text
from app.modules.cache_keys import (
    DataAnalysisRecipeKeys, LoadedDataAnalysisRecipe, load_data_analysis_recipe, loaded_from_resolved, tier2_steps)
from app.modules.plan_composer import compose_plan_book
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, DataOrchestrator, InputsChanged, tier2_path_for
from transformer.anchor import read_anchor_if_key
from utils.audit_copy import AuditStep, all_audit_steps, integrity_errors, with_audit_steps
from utils.plan_book import PlanBook
from utils.recipe_graph import build_graph

# Where a table of the copy comes from.
FROM_ORIGINAL = "original"      # the key equals the original's: read from the original's stored table
FROM_AUDIT_STORE = "audit store"  # the key differs and the audit's own folder already held that table
BUILT = "built"                 # the key differs and the table was built now, into the audit's own folder
NONE = "none"                   # no tier-2 steps: Tier 2 is the Tier 1 table


class AuditRunError(Exception):
    """The run of a copy cannot go on. `step_id` and `place` name the audit step that cannot be applied, when the cause is one."""

    def __init__(self, message: str, step_id: Optional[str] = None, place: Optional[str] = None) -> None:
        super().__init__(message)
        self.step_id = step_id
        self.place = place


@dataclass(frozen=True)
class TableRun:
    """One table (a schema or a join) in the original and in the copy: its keys, where each stage came from and the file that holds it.
    `t1` and `t2` are `original`, `audit store`, `built` (and `none` for a Tier 2 with no steps); `t1_path` and `t2_path` are the stored files read."""
    table: str
    t1_key_original: str
    t1_key_audit: str
    t1: str
    t1_path: Path
    t2_key_original: str
    t2_key_audit: str
    t2: str
    t2_path: Optional[Path]


@dataclass(frozen=True)
class PlotRun:
    """One plot: the key of its table in the original and in the copy, `reused` (equal keys, so the same table, nothing was built) or not, and
    whether the content of its table differs (`affected`)."""
    plot: str
    key_original: str
    key_audit: str
    reused: bool
    affected: bool


@dataclass(frozen=True)
class AuditRun:
    recipe_id: str
    audit_dir: Path
    tables: Dict[str, TableRun] = field(default_factory=dict)
    plots: Dict[str, PlotRun] = field(default_factory=dict)
    inputs_changed: tuple = ()   # one sentence per build whose inputs changed while it ran ("the data files changed"): that table was not stored
    context: Optional["_Run"] = field(default=None, compare=False, repr=False)   # what `plot_table` needs to read a plot of the copy (set by `run_audit`)

    @property
    def affected_plots(self) -> List[str]:
        """The plots whose table differs in content between the original and the audit run, in the order of the recipe."""
        return [plot_id for plot_id, run in self.plots.items() if run.affected]

    def plot_table(self, plot_id: str, told: Optional[Callable[[InputsChanged], None]] = None) -> Optional[pl.LazyFrame]:
        """The table a plot reads in the copy, LAZY, read from the tables this run placed; None when the copy leaves the plot's table as it is (the plot's key is the
        original's: the plot lies below no audit step), so that the caller reads the original's table as it always does. KeyError for a plot the recipe does not have.
        `told` receives what a build says when its inputs changed while it read (the same callback as `materialize_tier3`)."""
        if plot_id not in self.plots:
            raise KeyError(f"The recipe has no plot '{plot_id}'.")
        if self.plots[plot_id].reused or self.context is None:
            return None
        return self.context.plot_lazy(plot_id, told)

    def audited_frames(self) -> Dict[str, Dict[str, pl.DataFrame]]:
        """The tables the copy changes, at each tier where it changes them: `{table: {"T1": frame, "T2": frame}}`, a tier left out when the copy's table at that tier is
        the original's (a table beside the place has no entry). The frames are read from the stored tables of this run (the audit's own folder), collected. The export
        writes them beside the originals (PROVISIONAL form, owner 2026-11-24)."""
        found: Dict[str, Dict[str, pl.DataFrame]] = {}
        for table, run in self.tables.items():
            frames: Dict[str, pl.DataFrame] = {}
            if run.t1 != FROM_ORIGINAL:
                frames["T1"] = pl.read_parquet(run.t1_path)
            if run.t2 not in (FROM_ORIGINAL, NONE) and run.t2_path is not None:
                frames["T2"] = pl.read_parquet(run.t2_path)
            if frames:
                found[table] = frames
        return found

    def audited_table_lazy(self, table: str, tier: str) -> Optional[pl.LazyFrame]:
        """The table `table` at `tier` ("T1" or "T2") as the copy builds it, LAZY, read from the stored table of this run; None when the copy leaves it as the original's (a table
        beside the audit steps). A table with no tier-2 steps has no tier 2 of its own: its audited T2 is its audited T1. This is the table HOME's T1 and T2 views show in Audit mode
        and the export writes as `T1_data_audited.tsv` / `T2_data_audited.tsv` (D-0622, D-0619); the export writes no T2 file for a table whose T2 equals its T1 (it is the T1 file)."""
        if tier not in ("T1", "T2"):
            raise ValueError("tier is T1 or T2")
        run = self.tables.get(table)
        if run is None:
            return None
        if tier == "T2" and run.t2 not in (FROM_ORIGINAL, NONE) and run.t2_path is not None:
            return pl.scan_parquet(run.t2_path)
        if (tier == "T1" or run.t2 == NONE) and run.t1 != FROM_ORIGINAL:
            return pl.scan_parquet(run.t1_path)
        return None

    def original_table_lazy(self, table: str, tier: str) -> pl.LazyFrame:
        """The ORIGINAL's stored table `table` at `tier` ("T1" or "T2"), LAZY (a table with no tier-2 steps of its own has the tier 1 table as its tier 2): what the copy's table is compared with
        when no applied audit step changes it (the trial of a step, `audit_trial.py`). Raises KeyError when this run has no context."""
        if tier not in ("T1", "T2"):
            raise ValueError("tier is T1 or T2")
        if self.context is None:
            raise KeyError("This run has no context to read the original's tables.")
        return self.context.original_table(table, tier)

    def original_plot_lazy(self, plot_id: str, told: Optional[Callable[[InputsChanged], None]] = None) -> pl.LazyFrame:
        """The table a plot reads in the ORIGINAL (its Result data, T3), LAZY, keyed as the app keys it; KeyError for a plot the recipe does not have or a run with no context."""
        if plot_id not in self.plots or self.context is None:
            raise KeyError(f"The recipe has no plot '{plot_id}'.")
        return self.context.original_plot(plot_id, told)

    @property
    def built_tables(self) -> List[str]:
        """The stages built now, as `<table> T1` or `<table> T2`, in the order of the recipe."""
        return [f"{t.table} {stage}" for t in self.tables.values() for stage, source in (("T1", t.t1), ("T2", t.t2)) if source == BUILT]


def row_count(table: pl.LazyFrame) -> int:
    """The number of rows of a lazy table, counted lazily (the table is not held in memory)."""
    return int(table.select(pl.len()).collect().item())


def compare_tables(first: pl.LazyFrame, second: pl.LazyFrame) -> Tuple[int, int, bool]:
    """(rows of the first, rows of the second, whether they are the same table): each table is read ONCE (collected); the row counts are compared first and the tables are
    compared only when the counts are equal (same columns, same rows, same order)."""
    left, right = first.collect(), second.collect()
    return left.height, right.height, left.height == right.height and left.equals(right)


def same_table(first: pl.LazyFrame, second: pl.LazyFrame) -> bool:
    """Whether two lazy tables hold the same columns, the same rows and the same order (each is read once, `compare_tables`)."""
    return compare_tables(first, second)[2]


def _stored(path: Path, meta_key: str, key: str) -> bool:
    return read_anchor_if_key(path, meta_key, key) is not None


class _Run:
    """The state of one run: the orchestrator, the original with its keys, the copy as a recipe, the two folders."""

    def __init__(self, orchestrator: DataOrchestrator, recipe_id: str, audit_recipe: dict, original_dir: Path, audit_dir: Path, original: LoadedDataAnalysisRecipe,
                 plans: PlanBook) -> None:
        self.orch = orchestrator
        self.recipe_id = recipe_id
        self.original_dir = original_dir
        self.audit_dir = audit_dir
        self.original: LoadedDataAnalysisRecipe = original
        self.plans = plans   # the engine's plan book of the ORIGINAL: the engine's check of every copy it builds from (the rule of a key drop) reads it
        self.audit_raw = copy.deepcopy(audit_recipe)
        self.audit_loaded = loaded_from_resolved(self.original, self.audit_raw, plans)
        self.keys_original = orchestrator.compute_data_analysis_recipe_keys(recipe_id, loaded=self.original)
        self.keys_audit = orchestrator.compute_data_analysis_recipe_keys(recipe_id, loaded=self.audit_loaded)
        self.graph = build_graph(self.audit_raw)
        self.changed: List[str] = []   # the builds whose inputs changed while they ran

    # -- where a stage of the copy is
    def t1_dir(self, table: str, keys: DataAnalysisRecipeKeys, out_dir: Path) -> Path:
        """The folder of the Tier 1 table the copy reads for `table`: the original's folder when the key is the original's, else `out_dir`."""
        return self.original_dir if keys.tier1_key_of(table) == self.keys_original.tier1_key_of(table) else out_dir

    def t2_path(self, table: str, keys: DataAnalysisRecipeKeys, out_dir: Path) -> Optional[Path]:
        """Where the Tier 2 table of the copy is stored when its key is not the original's (else None: it is the original's, beside its Tier 1)."""
        return None if keys.tier2_key_of(table) == self.keys_original.tier2_key_of(table) else out_dir / f"{table}__T2.parquet"

    # -- the original
    def told(self, changed: List[str], what: str) -> Callable[[InputsChanged], None]:
        """What a build says when its inputs changed while it ran: kept as a sentence in `changed`, shown in the result (never silent)."""
        return lambda change: changed.append(f"{what}: {change.text}; it was returned and not stored")

    def ensure_original(self, table: str) -> None:
        """The original's tables of `table` are stored under their keys (built now when they were not), as the app stores them."""
        path = self.original_dir / f"{table}.parquet"
        told = self.told(self.changed, f"the original's table '{table}'")
        self.orch.materialize_tier1(self.recipe_id, table, path, keys=self.keys_original, on_inputs_changed=told)
        if tier2_steps(self.original.raw, table):
            self.orch.materialize_tier2(self.recipe_id, table, path, keys=self.keys_original, on_inputs_changed=told)

    # -- the copy
    def copy_table(self, table: str, loaded: LoadedDataAnalysisRecipe, keys: DataAnalysisRecipeKeys, out_dir: Path, changed: List[str]) -> TableRun:
        """Tier 1 and Tier 2 of `table` in the copy `loaded` with `keys`: read from the original when the key is its own, else built into `out_dir`."""
        k1o, k1c = self.keys_original.tier1_key_of(table), keys.tier1_key_of(table)
        k2o, k2c = self.keys_original.tier2_key_of(table), keys.tier2_key_of(table)
        t1_path = self.t1_dir(table, keys, out_dir) / f"{table}.parquet"
        if k1c == k1o:
            t1 = FROM_ORIGINAL
        else:
            t1 = FROM_AUDIT_STORE if _stored(t1_path, TIER1_KEY_META, k1c) else BUILT
            self.orch.materialize_tier1(self.recipe_id, table, t1_path, keys=keys, loaded=loaded,
                                        on_inputs_changed=self.told(changed, f"the audit's table '{table}' (tier 1)"))
        t2_path: Optional[Path] = None
        if not tier2_steps(loaded.raw, table):
            t2 = NONE
        elif k2c == k2o:
            t2, t2_path = FROM_ORIGINAL, tier2_path_for(t1_path)
        else:
            t2_path = self.t2_path(table, keys, out_dir)
            t2 = FROM_AUDIT_STORE if _stored(t2_path, TIER2_KEY_META, k2c) else BUILT
            self.orch.materialize_tier2(self.recipe_id, table, t1_path, keys=keys, loaded=loaded, tier2_path=t2_path,
                                        on_inputs_changed=self.told(changed, f"the audit's table '{table}' (tier 2)"))
        return TableRun(table, k1o, k1c, t1, t1_path, k2o, k2c, t2, t2_path)

    def plot_lazy(self, plot_id: str, told: Optional[Callable[[InputsChanged], None]] = None) -> pl.LazyFrame:
        """The lazy table of a plot of the copy, over the tables the run placed (the Tier 3 of a copy is stored nowhere, see `materialize_tier3`)."""
        target = self.graph.plot_target(plot_id)
        return self.orch.materialize_tier3(self.recipe_id, plot_id, self.t1_dir(target, self.keys_audit, self.audit_dir), keys=self.keys_audit,
                                           loaded=self.audit_loaded, tier2_path=self.t2_path(target, self.keys_audit, self.audit_dir), on_inputs_changed=told)

    def original_table(self, table: str, tier: str) -> pl.LazyFrame:
        """The original's stored table `table` at `tier` (the original's tables are stored first by `ensure_original`)."""
        path = self.original_dir / f"{table}.parquet"
        if tier == "T2" and tier2_steps(self.original.raw, table):
            path = tier2_path_for(path)
        return pl.scan_parquet(path)

    def original_plot(self, plot_id: str, told: Optional[Callable[[InputsChanged], None]] = None) -> pl.LazyFrame:
        """The lazy table a plot reads in the original, over the original's stored tables."""
        return self.orch.materialize_tier3(self.recipe_id, plot_id, self.original_dir, keys=self.keys_original, on_inputs_changed=told)

    def plot_frame(self, plot_id: str, loaded: LoadedDataAnalysisRecipe, keys: DataAnalysisRecipeKeys, out_dir: Path, changed: List[str]) -> pl.DataFrame:
        """The table a plot reads in the copy, collected. The tables under it are those `copy_table` placed."""
        target = self.graph.plot_target(plot_id)
        return self.orch.materialize_tier3(self.recipe_id, plot_id, self.t1_dir(target, keys, out_dir), keys=keys, loaded=loaded,
                                           tier2_path=self.t2_path(target, keys, out_dir),
                                           on_inputs_changed=self.told(changed, f"the table of the plot '{plot_id}'")).collect()

    # -- an audit step that cannot be applied
    def refuse(self, error: BaseException, places: List[str], attempt: Callable[[LoadedDataAnalysisRecipe, DataAnalysisRecipeKeys, Path, List[str]], object]) -> None:
        """Raise the error of the engine as an `AuditRunError` that names the audit step that causes it. `places` are the lists whose audit steps can
        cause it. One candidate is named at once; several are tried in order, the first N added to the original on their own (ids and reasons kept), in a
        scratch folder, and the first that fails is named. An error that no audit step can cause (the original's own) is raised as it is."""
        candidates = [m for m in all_audit_steps(self.audit_raw) if m.place in places]
        if candidates and self.fails_without_audit(attempt):
            candidates = []                                                          # the author's own step breaks it: no audit step is blamed
        if not candidates:
            plain = short_engine_text(error, limit=900)
            if plain == str(error):
                raise error
            raise AuditRunError(plain) from error                                   # an error that no audit step causes still never shows the engine's plan
        culprit = candidates[0] if len(candidates) == 1 else self.first_failing(candidates, attempt)
        why = short_engine_text(error, limit=900) + (f" ({error.tip})" if getattr(error, "tip", None) else "")   # one line, without the engine's plan (D-0450: a step that cannot be applied ends as a plain error)
        if culprit is None:
            ids = ", ".join(f"{m.step_id} at {m.place}" for m in candidates)
            raise AuditRunError(f"An audit step cannot be applied; it is one of these, which together cannot be applied: {ids}. The engine says: {why}") from error
        raise AuditRunError(f"The audit step {culprit.step_id} at {culprit.place} cannot be applied: {why}", culprit.step_id, culprit.place) from error

    def fails_without_audit(self, attempt) -> bool:
        """True when the original recipe, with no audit step, fails the same attempt: the failure is the author's, not an audit step's."""
        scratch = Path(tempfile.mkdtemp(prefix=".audit_probe_", dir=self.audit_dir))
        try:
            loaded = loaded_from_resolved(self.original, with_audit_steps(self.original.raw, []), self.plans)
            attempt(loaded, self.orch.compute_data_analysis_recipe_keys(self.recipe_id, loaded=loaded), scratch, [])
            return False
        except Exception:
            return True
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def first_failing(self, candidates: List[AuditStep], attempt) -> Optional[AuditStep]:
        scratch = Path(tempfile.mkdtemp(prefix=".audit_probe_", dir=self.audit_dir))
        try:
            for count in range(1, len(candidates) + 1):
                probe = with_audit_steps(self.original.raw, candidates[:count])
                loaded = loaded_from_resolved(self.original, probe, self.plans)
                try:
                    attempt(loaded, self.orch.compute_data_analysis_recipe_keys(self.recipe_id, loaded=loaded), scratch, [])
                except Exception:
                    return candidates[count - 1]
            return None
        finally:
            shutil.rmtree(scratch, ignore_errors=True)

    def plot_places(self, plot_id: str) -> List[str]:
        """The places whose audit steps can break a plot: its own and the tier 1 and tier 2 of every table it is built from (an audit step there can take away a column that the plot's own steps need)."""
        node = f"T3:{plot_id}"
        return [n for n in self.graph.lineage_back(node) if self.graph.node(n).kind in ("T1", "T2")] + [node]

    # -- the whole run
    def run(self) -> AuditRun:
        tables: Dict[str, TableRun] = {}
        for table in self.graph.collections():
            self.ensure_original(table)
        for table in self.graph.collections():
            places = [f"T1:{self.graph.node(n).name}" for n in self.graph.lineage_back(f"T1:{table}") if self.graph.node(n).kind == "T1"]
            places += [f"T1:{table}", f"T2:{table}"]
            try:
                tables[table] = self.copy_table(table, self.audit_loaded, self.keys_audit, self.audit_dir, self.changed)
            except AuditRunError:
                raise
            except Exception as error:
                self.refuse(error, places, lambda loaded, keys, out, changed, table=table: self.copy_table(table, loaded, keys, out, changed))
        plots: Dict[str, PlotRun] = {}
        failures: List[AuditRunError] = []     # every plot whose table cannot be built from the audit steps is named, not only the first (the export tells them all)
        for plot_id in self.graph.plots():
            key_original, key_audit = self.keys_original.plot_key_of(plot_id), self.keys_audit.plot_key_of(plot_id)
            if key_original == key_audit:
                plots[plot_id] = PlotRun(plot_id, key_original, key_audit, True, False)
                continue
            try:
                table_audit = self.plot_frame(plot_id, self.audit_loaded, self.keys_audit, self.audit_dir, self.changed)
            except Exception as error:
                try:
                    self.refuse(error, self.plot_places(plot_id), lambda loaded, keys, out, changed, plot_id=plot_id: self.plot_frame(plot_id, loaded, keys, out, changed))
                except AuditRunError as refused:
                    failures.append(refused)
                    continue
            table_original = self.orch.materialize_tier3(self.recipe_id, plot_id, self.original_dir, keys=self.keys_original,
                                                         on_inputs_changed=self.told(self.changed, f"the original's table of the plot '{plot_id}'")).collect()
            plots[plot_id] = PlotRun(plot_id, key_original, key_audit, False, not table_original.equals(table_audit))
        if failures:
            first = failures[0]
            texts = list(dict.fromkeys(str(f) for f in failures))      # the same step that breaks several plots is told once
            raise first if len(texts) == 1 else AuditRunError(" ".join(texts), first.step_id, first.place)
        self.clean(tables)
        return AuditRun(self.recipe_id, self.audit_dir, tables, plots, tuple(self.changed), self)

    def clean(self, tables: Dict[str, TableRun]) -> None:
        """Take out of the audit's folder the stored tables that are the original's again: a leftover that cannot be served today can be served by a
        later bug (rules_verification_testing.md section 9)."""
        for run in tables.values():
            if run.t1 == FROM_ORIGINAL:
                (self.audit_dir / f"{run.table}.parquet").unlink(missing_ok=True)
            if run.t2 in (FROM_ORIGINAL, NONE):
                (self.audit_dir / f"{run.table}__T2.parquet").unlink(missing_ok=True)


def _snapshot(folder: Path) -> Dict[str, tuple]:
    """{path relative to `folder`: (size, modification time)} of every file now in the audit folder (empty when it does not exist)."""
    if not folder.is_dir():
        return {}
    return {str(p.relative_to(folder)): (p.stat().st_size, p.stat().st_mtime_ns) for p in folder.rglob("*") if p.is_file()}


def _rollback(folder: Path, before: Dict[str, tuple], created: bool) -> None:
    """After a run that did not finish (a refused step, any error, an interrupt): take out of the audit folder what THIS run built, so that nothing is left
    that should be gone (rules_verification_testing.md section 9).

    The rule: a file that is not in `before` (the run created it) or whose size or modification time differs from `before` (the run replaced it) is removed;
    a file that was there before and was not touched stays, so a table that a previous successful run of the same copy left, and that this run only read,
    is still served. The folder itself is removed when this run created it and it is empty. The original's folder is never touched here: `run_audit` refuses an audit folder that is, holds or lies inside the original's folder before anything is built, so it is not inside the folder this function cleans."""
    if not folder.is_dir():
        return
    for path in sorted(folder.rglob("*"), reverse=True):
        if path.is_file() and before.get(str(path.relative_to(folder))) != (path.stat().st_size, path.stat().st_mtime_ns):
            path.unlink(missing_ok=True)
        elif path.is_dir() and not any(path.iterdir()):
            path.rmdir()
    if created and not any(folder.iterdir()):
        folder.rmdir()


def run_audit(orchestrator: DataOrchestrator, recipe_id: str, audit_recipe: dict, original_dir: Path, audit_dir: Path) -> AuditRun:
    """Build every table and every plot table of an audit copy, reusing the original's stored tables where the keys are equal; say which plots are affected.

    `original_dir` holds the original's stored tables (`<table>.parquet`, `<table>__T2.parquet`); `audit_dir` is the audit's own folder and must be another
    folder. Raises `AuditRunError` when the copy is not a copy of the original plus audit steps in the `audit_steps` lists (`integrity_errors`), when the
    folders are the same or one lies inside the other (symlinks followed), or when an audit step cannot be applied (naming its id and its place). Changes neither the original's recipe nor the audit copy. A run that does not finish (a refused step, any error, an interrupt)
    leaves in the audit folder nothing that it built (`_rollback`)."""
    original_dir, audit_dir = Path(original_dir), Path(audit_dir)
    original_real, audit_real = original_dir.resolve(), audit_dir.resolve()
    if original_real == audit_real:
        raise AuditRunError("The audit's stored tables go in a folder of their own, never in the folder of the original's tables.")
    # Symlinks are followed. A run that does not finish removes what it built in the audit folder (`_rollback`): that folder must never hold the original's tables.
    if audit_real.is_relative_to(original_real) or original_real.is_relative_to(audit_real):
        raise AuditRunError("The audit's stored tables go in a folder of their own: the folder of the audit and the folder of the original's tables must not be one inside the other.")
    original = load_data_analysis_recipe(orchestrator.data_analysis_recipes_dir / f"{recipe_id}.yaml")
    plans = compose_plan_book(orchestrator, recipe_id, original)   # the engine's plan of the original (LBFB step 0b): nothing is built or stored by it
    problems = integrity_errors(audit_recipe, original.raw, plans)
    if problems:
        raise AuditRunError("The audit copy is not the original plus audit steps, so it is not run: " + " ".join(problems))
    created = not audit_dir.exists()
    before = _snapshot(audit_dir)
    audit_dir.mkdir(parents=True, exist_ok=True)
    try:
        return _Run(orchestrator, recipe_id, audit_recipe, original_dir, audit_dir, original, plans).run()
    except BaseException:
        _rollback(audit_dir, before, created)
        raise
