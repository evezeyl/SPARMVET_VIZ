"""The engine side of TRYING an audit step before it is applied (HOME audit, the review of a step; nothing on screen reads it yet).

The model (ledger D-0656, D-0662, D-0669 to D-0671; `.claude/design/home_audit_what_is_true_now.md`): the user stages a step at one or more places; before applying, its effect is
computed (a TRIAL); applying REUSES the tables the trial computed. This file is that mechanism, pure of Shiny. The screen (the list, the three labels, Compare) is a later slice;
it reads `PlaceTrial.trial_table` and `PlaceTrial.trial_plot`, which match `audit_place_view.Readers`.

WHAT A TRIAL IS. The audit copy of the recipe made from the APPLIED steps plus the TRIED step appended LAST in its place's list (a swapped order changes the key). It is run by
`audit_run.run_audit` into a folder of its own, `<user data>/audit_trial/<token>`, a sibling of the audit folder (`audit_anchors`) and never inside it or inside the original's
folder. WHY its own folder and its own `PlaceAudit`: `AuditRun.audited_frames` and `audited_table_lazy` read the stored file of a table with no key check, and the audit folder holds
one file per table; a trial that shared the folder could let the export or an audited view read a tried table. With its own folder and its own instance nothing that reads the audit
folder can reach a tried table (proved byte for byte in `app/tests/test_audit_trial.py`). One folder PER SESSION (a token): two browser tabs on one recipe and one set of data have
the same session key and the same audit folder (`session_manager.compute_session_key`, `home_theater._the_place_audit`), so a trial folder named by recipe or key alone could be emptied
or read by the other tab.

THE PLACEHOLDER REASON. `audit_copy.add_step` refuses an empty reason, so the tried steps carry `TRIAL_REASON` inside the trial copy only. It is in no key (the keys hold the operation
and its order, no reason, no id, no date: `nodes_signature`, `cache_keys`), in no stored file and in no session or export: the caller's own nodes are never changed (copies are made).

THE SIGNATURE (`PlaceTrial.signature`): recipe id, the hash of the recipe, the hash of the data, `nodes_signature(applied)` and `nodes_signature(tried)` (id, place, kind and parameters of each
node, no reason: the places are in it). The same signature is "the same trial": `try_step` returns the stored result; another signature (the condition, the places or the applied list changed: a
step removed with the bin) discards the old trial and empties its folder, then computes again.

WHAT THE TRIAL SAYS (`TrialResult`): for each chosen place the rows before and after at that table (rows removed = before - after, computed on the trial's tables: no second calculation); what the step
reaches (the tables and plots built from the places, from the lineage), each tagged `table changed` or `no row changed` by comparing with the audited state BEFORE the step (the applied steps, or the
original when there is none); the error when the step cannot be applied, as a plain sentence (today such an error shows only after Apply).

THE REUSE AT APPLY (`apply_trial`): (a) refuses with a plain reason when the live signature differs from the trial's (something changed since the trial; nothing is moved); (b) moves
(`os.replace`) from the trial folder into the audit folder the stored tables whose key in their footer EQUALS the key now wanted for the list that will be stored (the keys are computed again
from the live recipe and data, with the real reason: never a file by name alone, ADR-089), (c) empties the trial folder, (d) returns the list to store: the applied steps plus the tried ones with the
real reason and `applied_at` set NOW. After that `PlaceAudit.run_of(applied list)` builds nothing and gives the tables of a fresh computation. The reuse covers the tables (tier 1 and tier 2); the Result
data (T3) of a plot of an audit copy is stored nowhere (`orchestrator.materialize_tier3`, PROVISIONAL) and is recomputed when read.

NOTHING LEFT BEHIND: the folder is emptied at discard, at apply and at every change of signature (`PlaceTrial.discard`), and `clean_trials` does it for the callers of "leaving Audit mode",
"restore", "change of recipe" (own folder) and "app start" (every folder: a killed process leaves files until the next start).

WHO OWNS WHAT: the owner of a `PlaceTrial` calls `discard()`; `clean_trials(root, token)` is for a trial whose object is gone. A table taken from `trial_table` or `trial_plot` is never kept across a discard, a new
try or an apply (it is read from the trial folder, which these empty). If the folder was emptied by someone else the object notices (`_alive`): the readers answer None, `try_step` computes again and
`apply_trial` refuses with "Try the step again". Apply is all or nothing for a reader: any failure while moving removes what was moved in and discards the trial (`TrialRefused`, the caller's list is not changed).

`applied_at`: the moment a step was APPLIED, set by `apply_trial` and `with_applied_at` (the staging time is `created_at`). The export's "committed at" reads it and falls back to `created_at` for steps
stored before (`audit_places.place_step_records`); it is an optional key of a step, written in UTC to the second with NO zone suffix, like `created_at` (a known point: the audit-log design will set one form with the zone, until then the stored form is not changed); so the format number of the session file does not change (an older file has no such key and is read as before).

PROVISIONAL (the builder's choices): the words of the sentences; the names; that the content comparison collects both tables (as `audit_run` does for a plot); that a trial that failed is kept as a result
with its error (so a second click does not run again) and is refused at apply; that a stale trial is discarded when `apply_trial` refuses; that the trial folder is named by a token per `PlaceTrial`.

Consumed by: app/tests/test_audit_trial.py (the next slice wires it into app/handlers/home_theater.py). If deleted: nothing on screen, until the next slice.

# @deps
# provides: class:PlaceTrial, class:TrialResult, class:PlaceEffect, class:ReachItem, class:TrialRefused, function:clean_trials, function:new_token, function:with_applied_at, constant:TRIAL_FOLDER, constant:TRIAL_REASON, constant:TABLE_CHANGED, constant:NO_ROW_CHANGED
# consumes: app/modules/audit_view.py (PlaceAudit, AUDIT_ERRORS), app/modules/audit_run.py (AuditRun, row_count, same_table), app/modules/audit_places.py (audit_copy_for, nodes_signature, place_words), app/modules/orchestrator.py (TIER1_KEY_META, TIER2_KEY_META, tier2_path_for), app/modules/cache_keys.py (load_data_analysis_recipe, loaded_from_resolved), libs/transformer/src/transformer/anchor.py (read_anchor_if_key), libs/utils/src/utils/recipe_graph.py
# consumed_by: app/tests/test_audit_trial.py
# doc: .claude/knowledge/decision_ledger.md (D-0302, D-0630, D-0656, D-0662, D-0669, D-0671), .claude/design/home_audit_what_is_true_now.md, .claude/rules/rules_data_engine.md
# @end_deps
"""
from __future__ import annotations

import os
import shutil
import uuid
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable, List, Optional, Set, Tuple

from app.modules.audit_places import audit_copy_for, nodes_signature, place_words
from app.modules.audit_run import AuditRun, compare_shapes, same_table
from app.modules.audit_view import AUDIT_ERRORS, PlaceAudit
from app.modules.cache_keys import load_data_analysis_recipe, loaded_from_resolved
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, DataOrchestrator, tier2_path_for
from transformer.anchor import read_anchor_if_key
from utils.plan_book import PlanBook
from utils.recipe_graph import RecipeGraph, build_graph

# The folder (beside `audit_anchors`, under the user's data) that holds the trials, one sub-folder per `PlaceTrial` (a token).
TRIAL_FOLDER = "audit_trial"
# The reason a tried step carries inside the trial copy only (`add_step` refuses an empty one). Never written to a session or an export. PROVISIONAL words.
TRIAL_REASON = "Trial: this step is being tried. It is not applied, not saved and not exported."
# The two tags of what a step reaches. PROVISIONAL words.
TABLE_CHANGED = "table changed"
NO_ROW_CHANGED = "no row changed"


class TrialRefused(Exception):
    """A trial cannot be applied; the message is one plain sentence and nothing was moved or applied."""


@dataclass(frozen=True)
class PlaceEffect:
    """What the tried step does at one chosen place: `place` (a node id), `words` (plain), the rows of that table before the step (the audited state, or the original) and after it."""
    place: str
    words: str
    rows_before: int
    rows_after: int
    state: str
    columns_before: int = 0       # the columns of that table before and after the step: a drop changes these and no row (FLOW-3: a drop is tried like a condition)
    columns_after: int = 0

    @property
    def rows_removed(self) -> int:
        return self.rows_before - self.rows_after

    @property
    def columns_removed(self) -> int:
        return self.columns_before - self.columns_after


@dataclass(frozen=True)
class ReachItem:
    """A table or a plot built from a chosen place: `node` (`T1:<table>`, `T2:<table>` or `T3:<plot>`), `words`, `kind` ("table" or "plot") and `state` (`table changed` or `no row changed`)."""
    node: str
    words: str
    kind: str
    state: str


@dataclass(frozen=True)
class TrialResult:
    """The answer of `try_step`. `error` is a plain sentence when the step cannot be applied (the other fields are then empty), else None."""
    signature: tuple
    effects: Tuple[PlaceEffect, ...] = ()
    reaches: Tuple[ReachItem, ...] = ()
    error: Optional[str] = None


@dataclass
class _Stored:
    signature: tuple
    run: Optional[AuditRun]
    result: TrialResult
    changed: Set[str]          # the node ids (`T1:<table>`, `T2:<table>`, `T3:<plot>`) whose table the tried step changes


def _plain(text: str) -> str:
    """The sentence of an error with the placeholder reason taken out: the trial copy carries `TRIAL_REASON`, and an error that quotes the step's reason must not show it to the user."""
    return text.replace(f', reason: "{TRIAL_REASON}"', "").replace(TRIAL_REASON, "").replace("  ", " ")


def new_token() -> str:
    """A short name for one session's trial folder."""
    return uuid.uuid4().hex[:12]


def now_iso() -> str:
    """The time stamp of a step, in the form `session_manager` writes (UTC, to the second)."""
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def with_applied_at(nodes: Iterable[dict], when: Optional[str] = None) -> List[dict]:
    """Copies of the nodes with `applied_at` set to `when` (now): the moment the steps were APPLIED, not staged (`created_at`). The argument is not changed."""
    stamp = when or now_iso()
    return [{**node, "applied_at": stamp} for node in nodes]


def clean_trials(trial_root: Path, token: Optional[str] = None) -> List[str]:
    """Empty trial folders: the one of `token` when given, every one when not (the start of the app: a killed process leaves its files until then).
    Returns the names that are really gone (a folder that could not be removed is not named). `trial_root` must be a folder named `audit_trial` (anything else is a bug of the caller: a
    recursive delete must never reach another folder). A folder that is not there is not an error. Never touches the audit folder or the original's folder.

    It never raises for the state of the disk (a folder that cannot be read or removed is left and not named: the start of the app must not stop for it). It never follows a link: when
    `audit_trial` is a symbolic link, or the folder of the token is one, nothing is done (a recursive delete of a link's target must not happen); a link inside `audit_trial` is left too.

    WHO CALLS IT. The owner of a `PlaceTrial` calls `PlaceTrial.discard()` (leaving Audit mode, restore, a change of recipe). `clean_trials(root, token)` is for a trial whose object is gone.
    WITHOUT a token it removes EVERY folder, as the start of the app needs; two app processes that share one user place would therefore remove each other's trials when one of them
    starts (a decision for the owner: separate user places, or a process mark in the folder name)."""
    root = Path(trial_root)
    if root.name != TRIAL_FOLDER:
        raise ValueError(f"The trial folder is called '{TRIAL_FOLDER}', not '{root.name}': nothing was removed.")
    if token is not None and (not token or Path(token).name != token or token in (".", "..")):
        raise ValueError(f"'{token}' is not the name of a trial folder: nothing was removed.")
    try:
        if root.is_symlink() or not root.is_dir():
            return []
        victims = ([root / token] if (root / token).exists() or (root / token).is_symlink() else []) if token is not None else sorted(root.iterdir())
    except OSError:
        return []
    removed: List[str] = []
    for path in victims:
        try:
            if path.is_symlink():
                continue
            if path.is_dir():
                shutil.rmtree(path, ignore_errors=True)
            else:
                path.unlink(missing_ok=True)
        except OSError:
            pass
        if not path.exists() and not path.is_symlink():
            removed.append(path.name)
    try:
        if not any(root.iterdir()):
            root.rmdir()
    except OSError:
        pass
    return removed


class PlaceTrial:
    """The trial of one session's step. `audited`: the `PlaceAudit` of the APPLIED steps (the one HOME reads); its folders are the original's and the audit's. `trial_root`: the folder
    `audit_trial` under the user's data; this object's folder is `trial_root/<token>`."""

    def __init__(self, orchestrator: DataOrchestrator, audited: PlaceAudit, trial_root: Path, token: Optional[str] = None) -> None:
        self.orch = orchestrator
        self.audited = audited
        self.original_dir = audited.original_dir
        self.audit_dir = audited.audit_dir
        self.trial_root = Path(trial_root)
        if self.trial_root.name != TRIAL_FOLDER:
            raise ValueError(f"The trial folder is called '{TRIAL_FOLDER}', not '{self.trial_root.name}'.")
        self.token = token or new_token()
        self.trial_dir = self.trial_root / self.token
        self._reader = PlaceAudit(orchestrator, self.original_dir, self.trial_dir)
        self._stored: Optional[_Stored] = None

    # -- the signature
    def signature(self, recipe_id: str, applied: Iterable[dict], tried: Iterable[dict]) -> tuple:
        """What makes two trials the same: the recipe, its hash, the hash of the data, the applied steps and the tried steps (id, place, kind, parameters; no reason)."""
        keys = self.orch.compute_data_analysis_recipe_keys(recipe_id)
        return ("trial", recipe_id, keys.data_analysis_recipe_sha256, keys.data_batch_hash, nodes_signature(list(applied)), nodes_signature(list(tried)))

    # -- is the stored trial still there
    def _alive(self) -> bool:
        """Whether there is a stored trial AND its files are still there. Someone else may have emptied the folder (`clean_trials(token)`, a start of the app, a person): a stored result
        whose tables are gone is "no trial", never a table that fails when it is read."""
        stored = self._stored
        if stored is None:
            return False
        if stored.run is None:
            return True                                           # the result of a step that could not run holds no table
        if not self.trial_dir.is_dir():
            return False
        for table_run in stored.run.tables.values():
            for stage, path in ((table_run.t1, table_run.t1_path), (table_run.t2, table_run.t2_path)):
                if stage in ("built", "audit store") and (path is None or not Path(path).is_file()):
                    return False
        return True

    # -- discard
    def discard(self) -> None:
        """Forget the trial and empty its folder (idempotent)."""
        self._stored = None
        self._reader = PlaceAudit(self.orch, self.original_dir, self.trial_dir)
        clean_trials(self.trial_root, self.token)

    # -- try
    def try_step(self, recipe_id: str, applied: Iterable[dict], tried: Iterable[dict], plans: Optional[PlanBook] = None) -> TrialResult:
        """Compute the effect of the tried steps (one node per chosen place, all with the id of the decision) on top of the applied steps, without applying them.

        The tried nodes are appended LAST, in the order given. They need no reason (the trial copy carries `TRIAL_REASON`; the caller's dictionaries are not changed). The same signature
        as the stored trial returns the stored result; another one discards the old trial first. A step the engine cannot apply is returned as `TrialResult.error` (a plain sentence naming the
        step and its place), never raised."""
        applied_list, tried_list = list(applied), list(tried)
        if not tried_list:
            raise ValueError("A trial needs at least one tried step.")
        signature = self.signature(recipe_id, applied_list, tried_list)
        if self._stored is not None and self._stored.signature == signature and self._alive():
            return self._stored.result
        self.discard()
        shared = sorted({str(n.get("id")) for n in tried_list} & {str(n.get("id")) for n in applied_list})
        if shared:
            return TrialResult(signature, error=f"This step cannot be tried: its id ({', '.join(shared)}) is already the id of an applied step, and two steps with one id would be removed together. "
                                                f"Nothing was tried. Make the step again.")
        trial_nodes = [{**node, "reason": TRIAL_REASON} for node in tried_list]
        try:
            run = self._reader.run_of(recipe_id, applied_list + trial_nodes, plans)
            audited_run = self.audited.run_of(recipe_id, applied_list, plans) if applied_list else None
            assert run is not None
            original = load_data_analysis_recipe(self.orch.data_analysis_recipes_dir / f"{recipe_id}.yaml")
            effects, reaches, changed = self._compare(build_graph(original.raw), run, audited_run, [n["place"] for n in tried_list])
        except AUDIT_ERRORS as error:
            self.discard()
            result = TrialResult(signature, error=_plain(str(error)))
            self._stored = _Stored(signature, None, result, set())
            return result
        result = TrialResult(signature, tuple(effects), tuple(reaches))
        self._stored = _Stored(signature, run, result, changed)
        return result

    def _compare(self, graph: RecipeGraph, run: AuditRun, audited_run: Optional[AuditRun], places: List[str]) -> Tuple[List[PlaceEffect], List[ReachItem], Set[str]]:
        changed: Set[str] = set()
        effects: List[PlaceEffect] = []
        chosen = list(dict.fromkeys(places))
        for place in chosen:
            before, after = self._pair(graph, run, audited_run, place)
            rows_before, rows_after, columns_before, columns_after, same = compare_shapes(before, after)
            if not same:
                changed.add(place)
            effects.append(PlaceEffect(place, place_words(place), rows_before, rows_after, NO_ROW_CHANGED if same else TABLE_CHANGED, columns_before, columns_after))
        reached: Set[str] = set()
        for place in chosen:
            reached.update(graph.below(place))
        reached.difference_update(chosen)
        reaches: List[ReachItem] = []
        for node_id in graph.nodes():
            if node_id not in reached:
                continue
            node = graph.node(node_id)
            if node.kind not in ("T1", "T2", "T3") or (node.kind == "T2" and not node.steps):
                continue                                   # a tier 2 with no steps is its tier 1 again (one table, one line)
            before, after = self._pair(graph, run, audited_run, node_id)
            differs = not same_table(before, after)
            if differs:
                changed.add(node_id)
            reaches.append(ReachItem(node_id, place_words(node_id), "plot" if node.kind == "T3" else "table", TABLE_CHANGED if differs else NO_ROW_CHANGED))
        return effects, reaches, changed

    @staticmethod
    def _pair(graph: RecipeGraph, run: AuditRun, audited_run: Optional[AuditRun], node_id: str) -> Tuple[Any, Any]:
        """(the table before the step, the table with the step tried) of one node: the audited state before, else the original; the trial's table, else the same as before."""
        node = graph.node(node_id)
        if node.kind == "T3":
            after = run.plot_table(node.name)
            before = audited_run.plot_table(node.name) if audited_run is not None else None
            if before is None:
                before = run.original_plot_lazy(node.name)
        else:
            after = run.audited_table_lazy(node.name, node.kind)
            before = audited_run.audited_table_lazy(node.name, node.kind) if audited_run is not None else None
            if before is None:
                before = run.original_table_lazy(node.name, node.kind)
        return before, (before if after is None else after)

    # -- the readers of `audit_place_view.Readers`
    def trial_table(self, table: str, tier: str) -> Optional[Any]:
        """The lazy table `table` at `tier` ("T1" or "T2") with the tried step, or None when there is no trial or the tried step does not change that table (the audited or the original answer then
        stands). A table with no tier-2 steps has no tier 2 of its own: its tier 2 is its tier 1."""
        if not self._alive() or self._stored.run is None:
            return None
        run = self._stored.run
        table_run = run.tables.get(table)
        if table_run is None:
            return None
        node = f"T1:{table}" if tier == "T2" and table_run.t2 == "none" else f"{tier}:{table}"
        return run.audited_table_lazy(table, tier) if node in self._stored.changed else None

    def trial_plot(self, plot_id: str) -> Optional[Any]:
        """The lazy table a plot reads (its Result data, T3) with the tried step, or None when there is no trial or the tried step does not change it."""
        if not self._alive() or self._stored.run is None or f"T3:{plot_id}" not in self._stored.changed:
            return None
        return self._stored.run.plot_table(plot_id)

    # -- apply
    def apply_trial(self, recipe_id: str, applied: Iterable[dict], tried: Iterable[dict], reason: str, plans: Optional[PlanBook] = None, when: Optional[str] = None) -> List[dict]:
        """Apply the trial: the list to store (the applied steps and the tried ones with `reason` and `applied_at`), after moving the trial's stored tables into the audit folder.

        Raises `TrialRefused` (plain sentence, nothing moved) when there is no trial, when the live signature is not the trial's (something changed since: the stale trial is discarded and the
        caller must try again), when the trial found an error, or when the reason is empty. A table is moved only when the key in its footer equals the key now wanted for the list that is
        stored, computed again from the live recipe and data; any other file of the trial folder is not moved. The trial folder is emptied at the end."""
        applied_list, tried_list = list(applied), list(tried)
        if self._stored is None:
            raise TrialRefused("There is no trial of this step. Try the step first.")
        if not self._alive():
            self.discard()
            raise TrialRefused("The tables of the trial are gone (the trial folder was emptied). Nothing was applied. Try the step again.")
        if self.signature(recipe_id, applied_list, tried_list) != self._stored.signature:
            self.discard()
            raise TrialRefused("Something changed since you tried this step (the step, its places, the steps already applied, the recipe or the data). Nothing was applied. Try the step again.")
        if self._stored.result.error:
            raise TrialRefused(f"This step cannot be applied: {self._stored.result.error}")
        if not str(reason or "").strip():
            raise TrialRefused("A step needs a reason before it is applied. Nothing was applied.")
        final = with_applied_at([{**node, "reason": reason} for node in tried_list], when)
        stored_list = applied_list + final
        run = self._stored.run
        assert run is not None
        moved: List[Path] = []
        try:
            original = load_data_analysis_recipe(self.orch.data_analysis_recipes_dir / f"{recipe_id}.yaml")
            wanted = self.orch.compute_data_analysis_recipe_keys(recipe_id, loaded=loaded_from_resolved(original, audit_copy_for(original.raw, stored_list, plans).recipe, plans))
            self.audited.forget()                       # before the first move: a run held for the old list must not be served while the files change
            self.audit_dir.mkdir(parents=True, exist_ok=True)
            for table in run.tables:
                t1 = self.trial_dir / f"{table}.parquet"
                self._move_if_key(t1, TIER1_KEY_META, wanted.tier1_key_of(table), moved)
                self._move_if_key(tier2_path_for(t1), TIER2_KEY_META, wanted.tier2_key_of(table), moved)
            self.discard()
        except BaseException as error:
            left = self._undo(moved)
            if not isinstance(error, Exception):
                raise
            tail = f" These files could not be removed from the audit folder: {', '.join(left)}." if left else ""
            raise TrialRefused(f"The step could not be added: {_plain(str(error)) or type(error).__name__}. Nothing was applied.{tail} Try the step again.") from error
        finally:
            self.audited.forget()                       # whatever happened: the next read computes from keys, it never serves the memo of the old run
        return stored_list

    def _undo(self, moved: List[Path]) -> List[str]:
        """All or nothing for a reader: take out of the audit folder every file this apply moved in (they were tried tables; a table that was there before and was overwritten is rebuilt
        from its key at the next read, which is correct and costs only time), then discard the trial. Returns the names that could not be removed (empty when all went)."""
        left: List[str] = []
        for path in moved:
            try:
                path.unlink(missing_ok=True)
            except OSError:
                left.append(path.name)
        self._stored = None
        self._reader = PlaceAudit(self.orch, self.original_dir, self.trial_dir)
        try:
            clean_trials(self.trial_root, self.token)
        except Exception:
            pass
        shutil.rmtree(self.trial_dir, ignore_errors=True)
        return left

    def _move_if_key(self, source: Path, meta_key: str, key: str, moved: List[Path]) -> bool:
        """Move one stored table of the trial folder into the audit folder when the key in its footer is `key`; never by file name alone (ADR-089). The target is added to `moved` as soon as
        the move is made (a move that fails halfway is undone by `_undo`)."""
        if not source.is_file() or read_anchor_if_key(source, meta_key, key) is None:
            return False
        target = self.audit_dir / source.name
        os.replace(source, target)
        moved.append(target)
        return True
