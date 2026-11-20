"""app/modules/session_manager.py
Session identity, ghost save/restore, and session lifecycle management.

Spec: ui_implementation_contract.md §12d, §13
Two-Category Law (ADR-045): Pure Python — no Shiny imports. Safe to use from
tests, CLI scripts, and server code.

Session identity
----------------
session_key = data_analysis_recipe_sha256[:12] + ":" + data_batch_hash[:12]

A session is uniquely identified by the combination of data analysis recipe content AND
source data content. Same data analysis recipe + different data batch → different session.
Same data + edited data analysis recipe → different session.

Ghost slots (per session_key, under {location_4}/_sessions/{session_key}/)
---------------------------------------------------------------------------
  assembly.json          — T1/T2 provenance (written once per assembly)
  t3_{timestamp}.json   — audit steps snapshots (one per btn_apply / panel leave)

Both carry `schema_version` = SESSION_FORMAT_VERSION; every reader refuses a file with another number (D-0312).
"""

from __future__ import annotations

# @deps
# provides: constant:SESSION_FORMAT_VERSION, function:session_format_problem (D-0312), function:session_recipe_refusal (D-0317), class:SessionManager, typedef:AuditStep, function:make_audit_step, function:normalise_audit_steps, function:extract_primary_keys, function:split_key_drops, function:key_drop_notice, class:SessionImportLimits, function:session_import_limits_from (D-0283), function:session_input_id_part, function:session_input_id_parts (two listed sessions never share a button), exception:SessionImportRefused, exception:SessionKeyExists (D-0281)
# consumes: app/modules/error_notice.py (notice — VERIF-FIX-2, lazy), libs/utils/src/utils/na_choice.py, stdlib (hashlib, json, re, shutil, zipfile, pathlib, datetime, uuid), app.modules.cache_keys (canonical_hash — REPRO-RESTORE-HASH-1; batch_hash_of, dataset_file_hashes: the one reading of the data files for the keys, ADR-101)
# consumes: libs/utils/src/utils/join_keys.py (recipe_join_keys: extract_primary_keys returns it; the join keys of joins.*.tier1 and tier2, read as the engine runs them, D-0250, D-0297)
# consumed_by: app/src/bootloader.py (limits), app/tests/test_session_import_safety.py, app/src/server.py, app/handlers/home_theater.py, app/handlers/audit_stack.py, app/handlers/session_handlers.py, app/handlers/filter_and_audit_handlers.py (make_audit_step), app/modules/bundle_importer.py (LegacySessionError)
# doc: .claude/rules/ui_implementation_contract.md#12d, .claude/knowledge/architecture_decisions.md#ADR-097
# @end_deps

import hashlib
import json
import re
import shutil
import uuid
import zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict

from app.modules.cache_keys import batch_hash_of, canonical_hash, dataset_file_hashes
from utils import join_keys
from utils.na_choice import with_na

# The node types that are a row filter: each one records `na` (keep or remove the rows with no value).
_FILTER_NODE_TYPES = ("filter_row", "exclusion_row")


# ---------------------------------------------------------------------------
# AuditStep schema (§12b)
# ---------------------------------------------------------------------------

class AuditStep(TypedDict, total=False):
    node_type: str              # filter_row | exclusion_row | drop_column | aesthetic_override
    id: str                     # hex UUID — propagated copies SHARE this id (linked deletion, ADR-049)
    created_at: str             # ISO timestamp
    plot_scope: str             # specific plot sub-tab id (per-plot stack key, ADR-049)
    params: dict                # node-type-specific payload
    reason: str                 # mandatory for filter/exclusion/drop nodes
    active: bool                # legacy soft-delete flag — Phase 22-I switched to hard delete
    primary_key_warning: bool   # True when authoring touched a join key (ADR-049, §12g.5)
    gallery_source: dict        # optional: {gallery_id, gallery_yaml_hash}


def make_audit_step(
    node_type: str,
    params: dict,
    plot_scope: str = "__all__",
    reason: str = "",
    gallery_source: dict | None = None,
    primary_key_warning: bool = False,
    node_id: str | None = None,
) -> AuditStep:
    """Create a new AuditStep.

    Parameters
    ----------
    node_id : str | None
        Optional explicit id — used when propagating one user decision into N
        plot stacks (all copies share the same id for linked deletion, §12g.1).
        Default: fresh hex UUID.
    primary_key_warning : bool
        Set True when the targeted column is a join key (§12g.5). Persists in
        the ghost; renders as a warning banner on the audit card and as a marker in
        the export Methods section.
    """
    if node_type in _FILTER_NODE_TYPES:
        params = with_na(params)    # NA-RULE-63: a filter step is never written without `na`
    node: AuditStep = {
        "node_type": node_type,
        "id": node_id or uuid.uuid4().hex,
        "created_at": _now_iso(),
        "plot_scope": plot_scope,
        "params": params,
        "reason": reason,
        "active": True,
    }
    if primary_key_warning:
        node["primary_key_warning"] = True
    if gallery_source:
        node["gallery_source"] = gallery_source
    return node


def normalise_audit_steps(by_plot: dict[str, list[dict]]) -> dict[str, list[dict]]:
    """A copy of the per-plot audit stacks in which every filter step records `na`.

    A step made before the choice existed has no `na` and always removed the rows with no value, so it is carried as
    "remove" (shown as such, written as such when next saved or exported). A step that has `na` is left as it is.
    The argument is not changed.
    """
    out: dict[str, list[dict]] = {}
    for plot, nodes in (by_plot or {}).items():
        out[plot] = [
            {**n, "params": with_na(n.get("params") or {})} if n.get("node_type") in _FILTER_NODE_TYPES else dict(n)
            for n in nodes
        ]
    return out


def extract_primary_keys(data_analysis_recipe_raw_config: dict) -> list[str]:
    """Return the union of join-key column names across all assembly steps.

    A column is a primary key if it is a key column (`on`, `left_on`, `right_on`, and the `by` groups of an as-of join: the rule of
    `utils.join_keys.key_columns`) of a join step of `joins.*.tier1` or `joins.*.tier2` (`utils.join_keys.recipe_join_keys`, written once). This includes both true PKs
    (sample_id) and secondary/accessory keys for long-format joins (gene_id).

    See ADR-049 / §12g.2.
    """
    # ONE rule, shared with the audit copy (D-0297): the same function says which columns the audit may not drop
    return join_keys.recipe_join_keys(data_analysis_recipe_raw_config)


def split_key_drops(by_plot: dict[str, list[dict]], primary_keys) -> tuple[dict[str, list[dict]], list[dict]]:
    """Separate the stored `drop_column` steps that name a join key from the rest of the per-plot audit stacks.

    WHY: the audit refuses to drop a join key (D-0297) but a session saved before that rule, or written by hand, can hold such a
    step, and Restore puts stored steps straight into the view. Returns `(kept, refused)`: `kept` is a copy of `by_plot` without those
    steps (every other step, in its order, plots that become empty stay as empty lists); `refused` lists them, one entry per step
    copy as `{"plot", "id", "column", "reason"}`. With no known join keys nothing is refused. The argument is not changed.
    """
    keys = set(primary_keys or [])
    kept: dict[str, list[dict]] = {}
    refused: list[dict] = []
    for plot, nodes in (by_plot or {}).items():
        kept[plot] = []
        for node in nodes or []:
            column = (node.get("params") or {}).get("column") if isinstance(node, dict) else None
            if isinstance(node, dict) and node.get("node_type") == "drop_column" and column in keys:
                refused.append({"plot": plot, "id": node.get("id", ""), "column": column, "reason": node.get("reason", "")})
            else:
                kept[plot].append(node)
    return kept, refused


def key_drop_notice(refused: list[dict], restored_ids: int) -> str:
    """The sentence that tells the user which stored steps were not restored because they drop a join key, and why.

    PROVISIONAL wording (D-0297 asks for plain words and the text of `ui_implementation_contract.md` 12g.3 goes to Eve with the other
    texts). One entry per decision (a decision propagated to several plots has one copy per plot and one id): its column, the plots, the
    reason the user wrote. `restored_ids` is how many other decisions were restored.
    """
    from app.modules.error_notice import notice
    by_decision: dict[tuple, dict] = {}
    for item in refused:
        entry = by_decision.setdefault((item["id"] or f"{item['plot']}/{item['column']}", item["column"]),
                                       {"column": item["column"], "plots": [], "reason": item["reason"]})
        entry["plots"].append(item["plot"])
        entry["reason"] = entry["reason"] or item["reason"]
    parts = []
    for entry in by_decision.values():
        why = f", your reason was: \"{entry['reason']}\"" if entry["reason"] else ""
        parts.append(f"dropping the column {entry['column']} (plot {', '.join(entry['plots'])}{why})")
    n = len(by_decision)
    what = (f"{n} step(s) of the saved session were not restored: {'; '.join(parts)}. A join key column cannot be dropped through the audit, "
            f"because the tables are joined on it. The other {restored_ids} step(s) were restored")
    return notice(what, "use a row filter or row exclusion instead; the saved file is not changed")


def node_blocks_apply(node: AuditStep) -> bool:
    """True if this node must have a non-empty reason before btn_apply."""
    return node.get("active", True) and node.get("node_type") in {
        "filter_row", "exclusion_row", "drop_column"
    } and not node.get("reason", "").strip()


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------

class SessionDeleteError(Exception):
    """`delete_all_sessions` stopped at a session it could not delete: what was done and what was not (D-0050).

    `deleted`: keys removed before the failure; `failed_key`: the one that could not be removed; `not_attempted`: the keys
    after it, still there; `cause`: the error of the operating system."""

    def __init__(self, deleted: list[str], failed_key: str, not_attempted: list[str], cause: BaseException):
        self.deleted, self.failed_key, self.not_attempted, self.cause = deleted, failed_key, not_attempted, cause
        super().__init__(f"{len(deleted)} session(s) deleted; {failed_key} could not be deleted ({type(cause).__name__}: {cause})")


class LegacySessionError(ValueError):
    """A stored session file is refused: written by another version of the app (D-0312) or with keys from before the rename (ADR-091)."""


# The format number of a session file (assembly.json and t3_*.json). Every writer writes it and every reader compares it
# (D-0312): a file with no number, a lower one or a higher one is refused as a whole, nothing is converted. Number 3 is the
# first of the redesigned sessions; the files written before it carried no number (assembly.json) or 2 (t3_*.json).
SESSION_FORMAT_VERSION = 3


def session_format_problem(data, where: str) -> str | None:
    """The plain line that refuses a session file of another format number, or None when the number is the current one.

    `where` names the file, e.g. "Session <key> (assembly.json)". PROVISIONAL wording (D-0312 gives the sense, a text the owner reads).
    """
    if not isinstance(data, dict):
        return None   # not a session file at all: the reader's own error says so (an unreadable file, not an old one)
    version = data.get("schema_version")
    if isinstance(version, int) and not isinstance(version, bool) and version == SESSION_FORMAT_VERSION:
        return None
    if isinstance(version, int) and not isinstance(version, bool) and version > SESSION_FORMAT_VERSION:
        return f"{where} was saved by a newer version of the app and cannot be opened. Delete it and start a new session."
    return f"{where} was saved by an older version of the app and cannot be opened. Delete it and start a new session."


def session_recipe_refusal(ghost: dict, open_recipe_id: str, session_key: str) -> str | None:
    """The plain line that refuses a Restore of a session that belongs to another recipe (D-0317), or None when it may go on.

    Compares the recipe id of the session record with the id of the open recipe. Same id: None (a different content hash or data
    batch is the business of the warnings, not of this refusal). PROVISIONAL wording. A record without a recipe id, or no open
    recipe, cannot be compared, and nothing is applied then either.
    """
    name = ghost.get("label") or session_key
    saved_id = ghost.get("data_analysis_recipe_id") or ""
    if not saved_id:
        return (f"Session {name} does not say which recipe it belongs to, so it cannot be restored. "
                "Delete it and start a new session.")
    if not open_recipe_id:
        return (f"Session {name} belongs to the recipe {saved_id}, and no recipe is open. "
                "Open that recipe first, then restore the session.")
    if saved_id != open_recipe_id:
        return (f"Session {name} belongs to another recipe ({saved_id}). "
                "Open that recipe first, then restore the session.")
    return None


def _not_a_mapping_line(where: str, data) -> str:
    """The plain line for a session file whose JSON is not a mapping (a list, a number, text), naming the file."""
    kind = {list: "a list", dict: "a mapping", str: "text", bool: "true or false", int: "a number", float: "a number",
            type(None): "nothing (null)"}.get(type(data), type(data).__name__)
    return f"{where} is not a session file: it holds {kind}, not the record of a session."


class SessionManager:
    """Manages session identity, T1/T2 ghost, and T3 ghost files.

    All file I/O is under {location_4}/_sessions/{session_key}/.
    Pure Python — no Shiny state.
    """

    SESSIONS_DIR = "_sessions"

    def __init__(self, location_4: Path):
        self.root = Path(location_4) / self.SESSIONS_DIR
        self.root.mkdir(parents=True, exist_ok=True)

    # ------------------------------------------------------------------
    # 22-A-2: Data analysis recipe SHA256
    # ------------------------------------------------------------------

    @staticmethod
    def compute_data_analysis_recipe_sha256(data_analysis_recipe_path: Path) -> str:
        """Hash of the data analysis recipe file set: the entry file and every included file (ADR-089).

        Sorted `relative_path:sha256` lines, hashed again. Independently verifiable with sha256sum.
        """
        from app.modules.cache_keys import load_data_analysis_recipe
        return load_data_analysis_recipe(data_analysis_recipe_path).data_analysis_recipe_sha256

    # ------------------------------------------------------------------
    # 22-A-3: Data batch hash
    # ------------------------------------------------------------------

    @staticmethod
    def compute_data_batch_hash(source_files: dict[str, Path]) -> str:
        """SHA256 of all per-file SHA256s concatenated in sorted key order.

        source_files: {dataset_id: path}
        """
        return batch_hash_of(dataset_file_hashes(source_files))

    # ------------------------------------------------------------------
    # 22-A-4: Session key
    # ------------------------------------------------------------------

    @staticmethod
    def compute_session_key(data_analysis_recipe_sha256: str, data_batch_hash: str) -> str:
        """f'{data_analysis_recipe_sha256[:12]}:{data_batch_hash[:12]}'"""
        return f"{data_analysis_recipe_sha256[:12]}:{data_batch_hash[:12]}"

    # ------------------------------------------------------------------
    # 22-A-5: Session directory
    # ------------------------------------------------------------------

    def session_dir(self, session_key: str) -> Path:
        """Returns (and creates) the session directory."""
        d = self.root / session_key
        d.mkdir(parents=True, exist_ok=True)
        return d

    # ------------------------------------------------------------------
    # 22-A-6: Write T1/T2 assembly ghost
    # ------------------------------------------------------------------

    def write_assembly_ghost(
        self,
        session_key: str,
        data_analysis_recipe_id: str,
        data_analysis_recipe_sha256: str,
        data_batch_hash: str,
        source_files: dict[str, str],   # {dataset_id: path_str}
        parquet_paths: dict[str, str],   # {"assembly": ..., "contracted": ...}
        label: str | None = None,
        on_problem=None,
    ) -> Path:
        """Write assembly.json to the session directory.

        REPRO-SESSION-LABELS-1 (#50): `label` is the canonical home for the
        user-facing session label — assembly.json is written once per session and
        exists before any T3 ghost does, unlike the old label-in-T3-ghost storage
        (which left a brand-new session unlabellable until its first Apply). A
        rewrite of an already-assembled session (recipe/data changed, ADR-089) must
        not silently erase a label the user already set: pass `label=None` (the
        default) to preserve whatever is already on disk; pass an explicit string
        (including "") to set or clear it.

        `on_problem(text)` is called when the earlier record cannot be read: it is rewritten (as always) and its label is
        lost; the text tells the user so (D-0050).
        """
        path = self.session_dir(session_key) / "assembly.json"
        if label is None:
            label = ""
            if path.exists():
                try:
                    earlier = json.loads(path.read_text())
                except Exception as exc:
                    earlier = None
                    label = ""
                    if on_problem is not None:
                        from app.modules.error_notice import notice
                        on_problem(notice(
                            f"The earlier record of the session {session_key} could not be read, so it was written again and "
                            "its label, if it had one, is lost", "type the label again in the Session Management panel", exc))
                if earlier is not None and not isinstance(earlier, dict):
                    label = ""
                    if on_problem is not None:
                        from app.modules.error_notice import notice
                        on_problem(notice(
                            f"The earlier record of the session {session_key} could not be read, so it was written again and "
                            "its label, if it had one, is lost", "type the label again in the Session Management panel",
                            ValueError(_not_a_mapping_line(f"Session {session_key} ({path.name})", earlier))))
                    earlier = None
                if earlier is not None:
                    # Never written over without saying so (D-0312): the stored record of another format number stays as it is.
                    problem = session_format_problem(earlier, f"Session {session_key} ({path.name})")
                    if problem:
                        raise LegacySessionError(problem)
                    label = earlier.get("label", "")
        ghost = {
            "session_key": session_key,
            "data_analysis_recipe_id": data_analysis_recipe_id,
            "data_analysis_recipe_sha256": data_analysis_recipe_sha256,
            "data_batch_hash": data_batch_hash,
            "assembled_at": _now_iso(),
            "label": label,
            "schema_version": SESSION_FORMAT_VERSION,
            "source_files": {
                k: {"path": str(v), "sha256": _file_sha256(v)}
                for k, v in source_files.items()
            },
            "parquet_paths": parquet_paths,
        }
        path.write_text(json.dumps(ghost, indent=2))
        return path

    # ------------------------------------------------------------------
    # 22-A-7: Read T1/T2 assembly ghost
    # ------------------------------------------------------------------

    @staticmethod
    def _read_current_json(path: Path, label: str) -> dict:
        """Read a stored session file; refuse one written before the rename, naming the fix."""
        from app.modules.renamed_keys import legacy_session_problem, refused_audit_step_in_ghost
        data = json.loads(path.read_text())
        if not isinstance(data, dict):
            raise ValueError(_not_a_mapping_line(f"{label} ({path.name})", data))
        problem = (session_format_problem(data, f"{label} ({path.name})")
                   or legacy_session_problem(data, f"{label} ({path.name})")
                   or refused_audit_step_in_ghost(data, f"{label} ({path.name})"))
        if problem:
            raise LegacySessionError(problem)
        return data

    def read_assembly_ghost(self, session_key: str) -> dict | None:
        path = self.session_dir(session_key) / "assembly.json"
        if not path.exists():
            return None
        return self._read_current_json(path, f"Session {session_key}")

    # ------------------------------------------------------------------
    # 22-A-8: T1/T2 restore — 6-step Prepped Chef check
    # ------------------------------------------------------------------

    def restore_t1t2(
        self,
        data_analysis_recipe_path: Path,
        source_files: dict[str, Path],
    ) -> dict:
        """6-step Prepped Chef restore logic.

        Returns:
            {
                "status": "fast_path" | "reassemble" | "new_session" | "missing_source",
                "session_key": str,
                "data_analysis_recipe_sha256": str,
                "data_batch_hash": str,
                "parquet_paths": dict,   # present on fast_path
                "missing": list[str],    # present on missing_source
            }
        """
        # Step 1: check for missing source files
        missing = [k for k, p in source_files.items() if not Path(p).exists()]
        if missing:
            return {"status": "missing_source", "missing": missing,
                    "session_key": "", "data_analysis_recipe_sha256": "", "data_batch_hash": "",
                    "parquet_paths": {}}

        # Step 2: compute hashes
        data_analysis_recipe_sha256 = self.compute_data_analysis_recipe_sha256(data_analysis_recipe_path)
        data_batch_hash = self.compute_data_batch_hash(source_files)
        session_key = self.compute_session_key(data_analysis_recipe_sha256, data_batch_hash)

        base = {"session_key": session_key, "data_analysis_recipe_sha256": data_analysis_recipe_sha256,
                "data_batch_hash": data_batch_hash}

        # Step 3: look for existing assembly ghost
        ghost = self.read_assembly_ghost(session_key)

        if ghost is None:
            # Step 5: no match → fresh session
            print(f"[SessionManager] restore_t1t2 → NEW_SESSION (no ghost for key={base['session_key'][:24]}…)")
            return {**base, "status": "new_session", "parquet_paths": {}}

        parquet_paths = ghost.get("parquet_paths", {})

        # Step 3: check Parquet files exist
        parquets_present = all(Path(p).exists() for p in parquet_paths.values())

        if parquets_present:
            # Step 3: fast path
            print(f"[SessionManager] restore_t1t2 → FAST_PATH (cache hit, key={base['session_key'][:24]}…)")
            return {**base, "status": "fast_path", "parquet_paths": parquet_paths}
        else:
            # Step 4: ghost exists but Parquet missing → caller must re-assemble
            print(f"[SessionManager] restore_t1t2 → REASSEMBLE (ghost found but parquet missing, key={base['session_key'][:24]}…)")
            return {**base, "status": "reassemble",
                    "parquet_paths": parquet_paths,
                    "source_files": ghost.get("source_files", {})}

    # ------------------------------------------------------------------
    # 22-A-9: Write T3 ghost
    # ------------------------------------------------------------------

    def write_t3_ghost(
        self,
        session_key: str,
        data_analysis_recipe_id: str,
        data_analysis_recipe_sha256: str,
        data_batch_hash: str,
        t3_audit_steps: list[dict] | None = None,
        t3_plot_overrides: dict | None = None,
        label: str = "",
        t3_audit_steps_by_plot: dict[str, list[dict]] | None = None,
        notification_log: list | None = None,
    ) -> Path:
        """Write a timestamped t3_{timestamp}.json to the session directory.

        Phase 22-J: prefers `t3_audit_steps_by_plot` (per-plot stacks). The flat
        `t3_audit_steps` argument is kept for backward compatibility with callers
        not yet updated and is stored alongside as a flattened convenience.
        """
        if t3_audit_steps_by_plot is None:
            t3_audit_steps_by_plot = {}
        t3_audit_steps_by_plot = normalise_audit_steps(t3_audit_steps_by_plot)
        if t3_audit_steps is not None:
            t3_audit_steps = list(normalise_audit_steps({"_": t3_audit_steps})["_"])
        if t3_audit_steps is None:
            # Flatten per-plot for the legacy field — readers that don't know
            # about per-plot still get a usable list.
            t3_audit_steps = [n for nodes in t3_audit_steps_by_plot.values() for n in nodes]
        ts = _timestamp()
        _overrides = t3_plot_overrides or {}
        ghost = {
            "session_key": session_key,
            "data_analysis_recipe_id": data_analysis_recipe_id,
            "data_analysis_recipe_sha256": data_analysis_recipe_sha256,
            "data_batch_hash": data_batch_hash,
            "saved_at": _now_iso(),
            "label": label,
            # D-0312: one format number for every session file (a lower or higher one is refused by every reader).
            # PROVISIONAL (coordinator): no `tier_toggle` is stored any more; the saved value was never the user's choice on the screen.
            "schema_version": SESSION_FORMAT_VERSION,
            "t3_audit_steps": t3_audit_steps,        # legacy flat view, kept for bw compat
            "t3_audit_steps_by_plot": t3_audit_steps_by_plot,
            "t3_plot_overrides": _overrides,
            "notification_log": notification_log or [],
            # REPRO-RESTORE-HASH-1 (ADR-097 decision 3/§6d): a self-consistency fingerprint
            # of this ghost's own T3 content — not a comparison against "current" T3 (there
            # is no independent current copy to compare against; restore is about to replace
            # it with exactly this). Same canonical_hash() shape export uses
            # (build_export_provenance's t3_audit_steps_sha256), so a ghost and an export
            # taken at the same moment agree. Meaningful only if the ghost file is corrupted
            # or hand-edited outside the app afterward.
            "t3_audit_steps_sha256": canonical_hash({
                "t3_audit_steps_by_plot": t3_audit_steps_by_plot,
                "t3_plot_overrides": _overrides,
            }),
        }
        path = self.session_dir(session_key) / f"t3_{ts}.json"
        path.write_text(json.dumps(ghost, indent=2))
        return path

    # ------------------------------------------------------------------
    # 22-A-10: List T3 ghosts for a session
    # ------------------------------------------------------------------

    def list_t3_ghosts(self, session_key: str) -> list[dict]:
        """All readable t3_*.json for a session, sorted newest-first (`scan_t3_ghosts` also says which files it skipped)."""
        return self.scan_t3_ghosts(session_key)[0]

    def scan_t3_ghosts(self, session_key: str) -> tuple[list[dict], list[dict]]:
        """`(saves, skipped)`: the readable t3_*.json of a session, newest first, and the files that could not be read.

        A skipped file is still skipped (nothing is restored from it); it is no longer skipped silently: each one is
        `{"file", "name", "reason"}` so that the caller can tell the user which save was left out and why (D-0050).

        Phase 22-J: surfaces both `t3_audit_steps` (legacy flat) and
        `t3_audit_steps_by_plot` (per-plot stacks). For pre-22-J ghosts that have
        only the flat list, the flat nodes are bucketed under "__legacy__" so
        the UI can offer re-targeting (§12g.8).
        """
        d = self.session_dir(session_key)
        ghosts = []
        skipped = []
        for f in sorted(d.glob("t3_*.json"), reverse=True):
            try:
                data = self._read_current_json(f, f"Session {session_key}")
            except LegacySessionError:
                raise
            except Exception as exc:
                skipped.append({"file": str(f), "name": f.name, "reason": _reason(exc)})
                continue
            by_plot = data.get("t3_audit_steps_by_plot")
            flat = data.get("t3_audit_steps", [])
            if not isinstance(by_plot, dict) or not by_plot:
                # Legacy ghost — lift the flat list into the orphaned bucket.
                by_plot = {"__legacy__": list(flat)} if flat else {}
            ghosts.append({
                "file": str(f),
                "saved_at": data.get("saved_at", ""),
                "label": data.get("label", ""),
                "data_analysis_recipe_sha256": data.get("data_analysis_recipe_sha256", ""),
                "data_batch_hash": data.get("data_batch_hash", ""),
                "schema_version": data.get("schema_version"),
                "t3_audit_steps": flat,
                "t3_audit_steps_by_plot": by_plot,
                "t3_plot_overrides": data.get("t3_plot_overrides", {}),
                # Absent on ghosts written before REPRO-RESTORE-HASH-1 — "" means "nothing
                # to check", not a mismatch (see the self-consistency check in
                # session_handlers.py::_restore_session).
                "t3_audit_steps_sha256": data.get("t3_audit_steps_sha256", ""),
            })
        return ghosts, skipped

    # ------------------------------------------------------------------
    # 22-A-11: List all sessions
    # ------------------------------------------------------------------

    def list_all_sessions(self) -> list[dict]:
        """All sessions, sorted by most-recent T3 ghost saved_at (newest first). `scan_sessions` also names what it left out."""
        return self.scan_sessions()[0]

    def scan_sessions(self) -> tuple[list[dict], list[dict]]:
        """`(sessions, unreadable)`: the list `list_all_sessions` gives, and the files that were left out of it.

        An unreadable `assembly.json` leaves its session out of the list, and an unreadable save is not counted in its
        session; both are still the case, and each is named as `{"session_key", "name", "reason", "kind"}` (kind "session": the session is not listed; "save": it is listed) so that the screen can
        tell the user (D-0050).
        """
        sessions = []
        unreadable = []
        for assembly_file in self.root.glob("*/assembly.json"):
            try:
                ghost = self._read_current_json(assembly_file, f"Session {assembly_file.parent.name}")
                session_key = ghost.get("session_key", assembly_file.parent.name)
                t3_ghosts, skipped = self.scan_t3_ghosts(session_key)
                unreadable += [{"session_key": session_key, "name": item["name"], "reason": item["reason"], "kind": "save"}
                               for item in skipped]
                latest_t3 = t3_ghosts[0].get("saved_at", "") if t3_ghosts else ""
                label = ghost.get("label", "") or (t3_ghosts[0].get("label", "") if t3_ghosts else "")
                sessions.append({
                    "session_key": session_key,
                    "data_analysis_recipe_id": ghost.get("data_analysis_recipe_id", ""),
                    "data_analysis_recipe_sha256": ghost.get("data_analysis_recipe_sha256", ""),
                    "data_batch_hash": ghost.get("data_batch_hash", ""),
                    "assembled_at": ghost.get("assembled_at", ""),
                    "latest_t3_saved_at": latest_t3,
                    "t3_count": len(t3_ghosts),
                    "label": label,
                })
            except LegacySessionError as exc:
                # shown in the session panel with the fix, never skipped silently
                sessions.append({"session_key": assembly_file.parent.name, "legacy_problem": str(exc),
                                 "data_analysis_recipe_id": "", "data_analysis_recipe_sha256": "",
                                 "data_batch_hash": "", "assembled_at": "", "latest_t3_saved_at": "",
                                 "t3_count": 0})
            except Exception as exc:
                unreadable.append({"session_key": assembly_file.parent.name, "name": assembly_file.name, "reason": _reason(exc),
                                   "kind": "session"})
                continue
        sessions.sort(key=lambda s: s["latest_t3_saved_at"] or s["assembled_at"], reverse=True)
        return sessions, unreadable

    # ------------------------------------------------------------------
    # 22-A-12: Export session as zip
    # ------------------------------------------------------------------

    def export_session_zip(self, session_key: str) -> bytes:
        """Zip {session_key}/ into in-memory bytes for download."""
        import io
        d = self.session_dir(session_key)
        buf = io.BytesIO()
        with zipfile.ZipFile(buf, "w", zipfile.ZIP_DEFLATED) as zf:
            for f in d.rglob("*"):
                if f.is_file():
                    zf.write(f, arcname=f.relative_to(self.root))
        return buf.getvalue()

    # ------------------------------------------------------------------
    # 22-A-13: Import session zip
    # ------------------------------------------------------------------

    def import_session_zip(self, zip_bytes: bytes, *, limits: "SessionImportLimits | None" = None,
                           on_exists: str | None = None) -> str:
        """Unpack a session zip into _sessions/. Returns the session_key it is stored under.

        Order (D-0281, D-0283): the file size, then every member name, then the declared unpacked size, then the
        content, are checked BEFORE anything is written. A key that already exists is never written over silently:
        with `on_exists=None` this raises `SessionKeyExists` and writes nothing; the caller asks the user and calls again
        with "replace" (the stored session is replaced) or "keep_both" (the zip is stored under
        `<key>_imported_<time>`, PROVISIONAL naming, its own session_key and a label that says it was imported).
        A zip that is refused, or an import that fails, leaves no file behind.
        """
        import io
        limits = limits or SessionImportLimits.default()
        if on_exists not in (None, "replace", "keep_both"):
            raise ValueError(f"on_exists must be None, 'replace' or 'keep_both', not {on_exists!r}")
        if len(zip_bytes) > limits.max_zip_bytes:
            raise SessionImportRefused(
                f"The file is {_human_bytes(len(zip_bytes))} and the limit for an imported session zip is "
                f"{_human_bytes(limits.max_zip_bytes)}. The limit is set by {limits.where}.")
        try:
            zf = zipfile.ZipFile(io.BytesIO(zip_bytes), "r")
        except zipfile.BadZipFile as exc:
            raise SessionImportRefused(f"The file is not a readable zip ({exc}).") from exc
        with zf:
            infos = zf.infolist()
            session_key = _checked_member_names(infos)
            declared = sum(i.file_size for i in infos)
            if declared > limits.max_unpacked_bytes:
                raise SessionImportRefused(
                    f"The zip is {_human_bytes(len(zip_bytes))} but would unpack to {_human_bytes(declared)} and the "
                    f"limit for the unpacked size is {_human_bytes(limits.max_unpacked_bytes)}. The limit is set by "
                    f"{limits.where}.")
            names = [i.filename for i in infos if not i.is_dir()]
            assembly_files = [n for n in names if n.endswith("assembly.json")]
            t3_files = [n for n in names if "/t3_" in n and n.endswith(".json")]
            if not assembly_files and not t3_files:
                raise ValueError("ZIP does not contain a valid session (no assembly.json or t3_*.json found).")
            from app.modules.renamed_keys import legacy_session_problem, refused_audit_step_in_ghost
            for name in assembly_files + t3_files:
                try:
                    data = json.loads(zf.read(name))
                except ValueError as exc:
                    raise SessionImportRefused(
                        f"The zip was refused and nothing was written: the file {_shown(name)} is not readable JSON ({exc}).") from exc
                if not isinstance(data, dict):
                    raise SessionImportRefused(
                        "The zip was refused and nothing was written: "
                        + _not_a_mapping_line(f"the file {_shown(name)}", data))
                problem = (session_format_problem(data, f"Imported session file {name}")
                           or legacy_session_problem(data, f"Imported session file {name}")
                           or refused_audit_step_in_ghost(data, f"Imported session file {name}"))
                if problem:
                    raise LegacySessionError(problem)
            for name in assembly_files:
                inner = json.loads(zf.read(name)).get("session_key")
                if inner is not None and inner != session_key:
                    raise SessionImportRefused(
                        f"The zip was refused and nothing was written: the session folder is named '{_shown(session_key)}' "
                        f"but the session_key inside {_shown(name)} is '{_shown(str(inner))}'. The two must be the same.")
            for name in t3_files:
                inner = json.loads(zf.read(name)).get("session_key")
                if inner is not None and inner != session_key:
                    raise SessionImportRefused(
                        f"The zip was refused and nothing was written: the session folder is named '{_shown(session_key)}' "
                        f"but the session_key inside {_shown(name)} is '{_shown(str(inner))}'. The two must be the same.")
            if self.root.exists():
                for other in self.root.iterdir():
                    if other.name != session_key and not other.name.startswith(".") \
                            and session_input_id_part(other.name) == session_input_id_part(session_key):
                        raise SessionImportRefused(
                            f"The zip was refused and nothing was written: the session folder '{_shown(session_key)}' "
                            f"would look the same on the screen as the stored session '{_shown(other.name)}'. "
                            "Rename the folder inside the zip.")
            target = self.root / session_key
            if target.exists() and on_exists is None:
                raise SessionKeyExists(session_key)
            stamp = _timestamp()
            work = self.root / f".import_{uuid.uuid4().hex}"
            try:
                staged = work / session_key
                for info in infos:
                    dest = work / info.filename
                    if info.is_dir():
                        dest.mkdir(parents=True, exist_ok=True)
                        continue
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    with zf.open(info) as src, open(dest, "wb") as out:
                        shutil.copyfileobj(src, out)
                if on_exists == "keep_both" and target.exists():
                    stored_key = f"{session_key}_imported_{stamp}"
                    _mark_as_imported_copy(staged, stored_key, session_key)
                    staged.rename(self.root / stored_key)
                    return stored_key
                if target.exists():
                    backup = self.root / f".replaced_{uuid.uuid4().hex}"
                    target.rename(backup)
                    try:
                        staged.rename(target)
                    except Exception:
                        backup.rename(target)
                        raise
                    shutil.rmtree(backup, ignore_errors=True)
                else:
                    staged.rename(target)
                return session_key
            finally:
                shutil.rmtree(work, ignore_errors=True)

    # ------------------------------------------------------------------
    # 22-A-14: Delete session
    # ------------------------------------------------------------------

    def delete_session(self, session_key: str) -> None:
        """Remove the entire session directory."""
        d = self.root / session_key
        if d.exists():
            shutil.rmtree(d)

    def delete_all_sessions(self) -> int:
        """Delete every session — HOM-54 (Eve, 2026-11-08): faster test cleanup than
        deleting one by one. Reuses delete_session() per key rather than rmtree-ing the
        root directly, so a legacy/malformed session entry can't abort the whole sweep.
        Returns the number of sessions deleted."""
        keys = [s["session_key"] for s in self.list_all_sessions()]
        deleted: list[str] = []
        for i, sk in enumerate(keys):
            try:
                self.delete_session(sk)
            except Exception as exc:
                raise SessionDeleteError(deleted, sk, keys[i + 1:], exc) from exc
            deleted.append(sk)
        return len(keys)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def get_session_label(self, session_key: str) -> str:
        """Return the session's label, or ''.

        REPRO-SESSION-LABELS-1 (#50): assembly.json is canonical (exists for every
        session, even one with no T3 ghost yet). Falls back to the most-recent T3
        ghost for sessions labelled before this change — old ghosts stored it there.
        """
        ghost = self.read_assembly_ghost(session_key)
        label = (ghost or {}).get("label", "")
        if label:
            return label
        ghosts = self.list_t3_ghosts(session_key)
        return ghosts[0].get("label", "") if ghosts else ""

    def set_session_label(self, session_key: str, label: str) -> None:
        """Set the session's label in assembly.json — works even before any Apply."""
        path = self.session_dir(session_key) / "assembly.json"
        if not path.exists():
            return
        data = self._read_current_json(path, f"Session {session_key}")   # a refused file is not written to
        data["label"] = label
        path.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# audit steps helpers
# ---------------------------------------------------------------------------

def audit_steps_sha256(t3_audit_steps: list[dict]) -> str:
    """SHA256 of the active-only audit steps serialized to JSON (sorted keys)."""
    active = [n for n in t3_audit_steps if n.get("active", True)]
    serialized = json.dumps(active, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(serialized).hexdigest()


def gatekeeper_blocked(t3_audit_steps: list[dict]) -> list[str]:
    """Return list of node IDs that block btn_apply (active nodes with empty reason)."""
    return [n["id"] for n in t3_audit_steps if node_blocks_apply(n)]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

# ---------------------------------------------------------------------------
# Session import: limits, refusals, member-name check (D-0281, D-0283)
# ---------------------------------------------------------------------------

# PROVISIONAL (Eve fixes the numbers, D-0283): measured on 2026-11-18, a full session of 1_test_data_ST22_dummy with two
# audited filters is a zip of about 2 KB (about 1 KB more per audit save); 3 times that is about 6 KB, which is below what
# one real session of ten saves needs, so the defaults are round numbers well above it.
DEFAULT_SESSION_IMPORT_MAX_ZIP_MB = 1
DEFAULT_SESSION_IMPORT_MAX_UNPACKED_MB = 10
_MB = 1024 * 1024
_SESSION_IMPORT_KEYS = ("max_zip_mb", "max_unpacked_mb")


class SessionImportRefused(ValueError):
    """The zip was refused before anything was written; the text is for the user (D-0050)."""


class SessionKeyExists(Exception):
    """A session with this key is already stored; nothing was written. The caller asks the user (D-0281)."""

    def __init__(self, session_key: str):
        super().__init__(f"A session with the key {session_key} already exists.")
        self.session_key = session_key


@dataclass(frozen=True)
class SessionImportLimits:
    max_zip_bytes: int
    max_unpacked_bytes: int
    where: str      # in words: which keys of which file set the limits

    @classmethod
    def default(cls) -> "SessionImportLimits":
        return session_import_limits_from({}, "")


def session_import_limits_from(deployment_config: dict, deployment_path: str) -> SessionImportLimits:
    """Read `session_import.max_zip_mb` and `session_import.max_unpacked_mb` of the deployment file (D-0283).

    A key that is absent takes the default; a wrong value or an unknown key under `session_import` raises ValueError
    naming the key and the file (the operator mistake is told, not guessed).
    """
    block = (deployment_config or {}).get("session_import")
    where_file = f"the deployment file {deployment_path}" if deployment_path else "the deployment file"
    if block is None:
        block = {}
    if not isinstance(block, dict):
        raise ValueError(f"session_import in {where_file} must be a block with {' and '.join(_SESSION_IMPORT_KEYS)}.")
    unknown = sorted(set(block) - set(_SESSION_IMPORT_KEYS))
    if unknown:
        raise ValueError(f"session_import.{unknown[0]} in {where_file} is not a known key; the keys are "
                         f"{' and '.join('session_import.' + k for k in _SESSION_IMPORT_KEYS)}.")
    values = {}
    for key, default in (("max_zip_mb", DEFAULT_SESSION_IMPORT_MAX_ZIP_MB),
                         ("max_unpacked_mb", DEFAULT_SESSION_IMPORT_MAX_UNPACKED_MB)):
        value = block.get(key, default) if key in block else default
        if isinstance(value, bool) or not isinstance(value, (int, float)) or value <= 0:
            raise ValueError(f"session_import.{key} in {where_file} must be a number of megabytes above 0, not {value!r}.")
        values[key] = int(value * _MB)
    if block:
        where = f"session_import.max_zip_mb and session_import.max_unpacked_mb in {where_file} (a key that is absent uses its default)"
    else:
        where = (f"the default, because session_import.max_zip_mb and session_import.max_unpacked_mb are not in "
                 f"{where_file}; set them there to change the limit")
    return SessionImportLimits(values["max_zip_mb"], values["max_unpacked_mb"], where)


def _human_bytes(n: int) -> str:
    if n >= _MB:
        return f"{n / _MB:.1f} MB ({n} bytes)"
    if n >= 1024:
        return f"{n / 1024:.1f} KB ({n} bytes)"
    return f"{n} bytes"


_S_IFMT, _S_IFLNK, _S_IFREG, _S_IFDIR = 0o170000, 0o120000, 0o100000, 0o040000


_KEY_CHARS = re.compile(r"[A-Za-z0-9_:]+")


def session_input_id_part(session_key: str) -> str:
    """The part of a Shiny input id that stands for a session key (letters, digits, underscore only).

    WHY: Shiny refuses any other character in an id, and one refused id breaks the whole Session Management panel.
    The panel looks the key up from the list of sessions, never from the id text, so two keys that give one id are
    refused when a zip is imported (`import_session_zip`).
    """
    return re.sub(r"[^A-Za-z0-9_]", "_", session_key)


def session_input_id_parts(listed_keys) -> dict[str, str]:
    """Key -> input id part for the sessions that are LISTED, unique by construction.

    WHY: two folders put in the store by hand, by a copy or by older code can give one safe form (`a:b` and `a_b`). They
    would share one button, so one Delete click would delete both. A key whose safe form is shared in the list gets the
    safe form plus `_` plus the first 8 hex characters of the sha256 of its exact key; the other keys keep the plain
    safe form. The panel and its effects look the key up in this mapping from the same listing, never from id text.
    """
    import hashlib
    keys = list(dict.fromkeys(listed_keys))
    count: dict[str, int] = {}
    for key in keys:
        part = session_input_id_part(key)
        count[part] = count.get(part, 0) + 1
    return {key: (session_input_id_part(key) if count[session_input_id_part(key)] == 1
                  else f"{session_input_id_part(key)}_{hashlib.sha256(key.encode('utf-8')).hexdigest()[:8]}")
            for key in keys}


def session_id_collisions(listed_keys) -> list[list[str]]:
    """Groups of listed keys whose plain safe forms are the same (two or more), in listing order."""
    groups: dict[str, list[str]] = {}
    for key in dict.fromkeys(listed_keys):
        groups.setdefault(session_input_id_part(key), []).append(key)
    return [g for g in groups.values() if len(g) > 1]


def _shown(text: str, limit: int = 60) -> str:
    """A name shortened for a message (a hostile zip may hold a very long one)."""
    return text if len(text) <= limit else text[:limit] + "... (shortened)"


def _checked_member_names(infos: list) -> str:
    """Refuse the whole zip at the first member that is not a plain file or folder inside ONE session folder.

    Returns the session key (the one top folder). Nothing has been written when this runs.
    """
    top = None
    seen: set[str] = set()
    for info in infos:
        name = info.filename
        parts = name.replace("\\", "/").split("/")
        problem = None
        if not name:
            problem = "an empty name"
        elif name.startswith(("/", "\\")) or (len(name) > 1 and name[1] == ":" and name[0].isalpha() and (len(name) == 2 or name[2] in "/\\")):
            problem = "an absolute path or a drive"
        elif ".." in parts:
            problem = "a path with a '..' part that goes up"
        elif "\\" in name:
            problem = "a name with a backslash"
        elif len(name) > 500 or any(len(p.encode("utf-8", "replace")) > 200 for p in parts):
            problem = "a name that is too long"
        elif name in seen:
            problem = "a name that appears twice in the zip"
        elif "\x00" in name:
            problem = "a name with a null character"
        else:
            kind = (info.external_attr >> 16) & _S_IFMT
            if kind not in (0, _S_IFREG, _S_IFDIR):
                problem = "a link or a special file"
            elif len(parts) < 2 and not info.is_dir():
                problem = "a file outside a session folder"
            else:
                first = parts[0]
                if not first or first.startswith("."):
                    problem = "a session folder name that is empty or starts with a dot"
                elif not _KEY_CHARS.fullmatch(first):
                    problem = (f"in a session folder named '{_shown(first)}'; a session folder name may hold only letters, "
                               "digits, '_' and ':'")
                elif top is None:
                    top = first
                elif first != top:
                    problem = f"a path outside the session folder {top}"
        seen.add(name)
        if problem:
            raise SessionImportRefused(
                f"The zip was refused and nothing was written: the member '{_shown(name)}' is {problem}. A session zip holds "
                "only plain files inside one session folder.")
    if top is None:
        raise ValueError("ZIP does not contain a valid session (no assembly.json or t3_*.json found).")
    return top


def _mark_as_imported_copy(folder: Path, new_key: str, original_key: str) -> None:
    """Make the unpacked copy a session of its own: its files carry the new key and the label says it was imported.

    PROVISIONAL (D-0281 "keep both"): the list, Restore and Delete find a session by the key inside assembly.json.
    """
    when = _now_iso()
    for path in folder.glob("*.json"):
        try:
            data = json.loads(path.read_text())
        except Exception:
            continue
        if not isinstance(data, dict) or "session_key" not in data:
            continue
        data["session_key"] = new_key
        if path.name == "assembly.json":
            old = data.get("label", "")
            data["label"] = f"Imported {when} UTC (copy of {original_key})" + (f": {old}" if old else "")
            data["imported_at"] = when
            data["imported_from_key"] = original_key
        path.write_text(json.dumps(data, indent=2))


def _reason(exc: BaseException) -> str:
    """The error as one line of plain text: `ErrorType: its own words`."""
    return f"{type(exc).__name__}: {' '.join(str(exc).split()) or 'no message'}"


def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")


def _file_sha256(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        return f"MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()
