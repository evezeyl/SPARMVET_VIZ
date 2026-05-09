"""app/modules/session_manager.py
Session identity, ghost save/restore, and session lifecycle management.

Spec: ui_implementation_contract.md §12d, §13
Two-Category Law (ADR-045): Pure Python — no Shiny imports. Safe to use from
tests, CLI scripts, and server code.

Session identity
----------------
session_key = manifest_sha256[:12] + ":" + data_batch_hash[:12]

A session is uniquely identified by the combination of manifest content AND
source data content. Same manifest + different data batch → different session.
Same data + edited manifest → different session.

Ghost slots (per session_key, under {location_4}/_sessions/{session_key}/)
---------------------------------------------------------------------------
  assembly.json          — T1/T2 provenance (written once per assembly)
  t3_{timestamp}.json   — T3 recipe snapshots (one per btn_apply / panel leave)
"""

from __future__ import annotations

# @deps
# provides: class:SessionManager, typedef:RecipeNode
# consumes: stdlib only (hashlib, json, shutil, zipfile, pathlib, datetime, uuid)
# consumed_by: app/src/server.py, app/handlers/home_theater.py, app/handlers/audit_stack.py, app/handlers/session_handlers.py
# doc: .claude/rules/ui_implementation_contract.md#12d
# @end_deps

import hashlib
import json
import shutil
import uuid
import zipfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, TypedDict


# ---------------------------------------------------------------------------
# RecipeNode schema (§12b)
# ---------------------------------------------------------------------------

class RecipeNode(TypedDict, total=False):
    node_type: str              # filter_row | exclusion_row | drop_column | aesthetic_override | developer_raw_yaml
    id: str                     # hex UUID — propagated copies SHARE this id (linked deletion, ADR-049)
    created_at: str             # ISO timestamp
    plot_scope: str             # specific plot sub-tab id (per-plot stack key, ADR-049)
    params: dict                # node-type-specific payload
    reason: str                 # mandatory for filter/exclusion/drop/developer nodes
    active: bool                # legacy soft-delete flag — Phase 22-I switched to hard delete
    primary_key_warning: bool   # True when authoring touched a join key (ADR-049, §12g.5)
    gallery_source: dict        # optional: {gallery_id, gallery_yaml_hash}


def make_recipe_node(
    node_type: str,
    params: dict,
    plot_scope: str = "__all__",
    reason: str = "",
    gallery_source: dict | None = None,
    primary_key_warning: bool = False,
    node_id: str | None = None,
) -> RecipeNode:
    """Create a new RecipeNode.

    Parameters
    ----------
    node_id : str | None
        Optional explicit id — used when propagating one user decision into N
        plot stacks (all copies share the same id for linked deletion, §12g.1).
        Default: fresh hex UUID.
    primary_key_warning : bool
        Set True when the targeted column is a join key (§12g.5). Persists in
        the ghost; renders as ⚠️ banner on the audit card and as a marker in
        the export Methods section.
    """
    node: RecipeNode = {
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


def extract_primary_keys(manifest_raw_config: dict) -> list[str]:
    """Return the union of join-key column names across all assembly recipes.

    A column is a primary key if it appears as `on`/`left_on`/`right_on` in any
    `join_manifests.*.recipe[*]` step. This includes both true PKs
    (sample_id) and secondary/accessory keys for long-format joins (gene_id).

    See ADR-049 / §12g.2.
    """
    keys: set[str] = set()
    join_defs = manifest_raw_config.get("join_manifests", {})
    if not isinstance(join_defs, dict):
        return []
    for join_def in join_defs.values():
        if not isinstance(join_def, dict):
            continue
        recipe = join_def.get("recipe", [])
        if not isinstance(recipe, list):
            continue
        for step in recipe:
            if not isinstance(step, dict):
                continue
            for field in ("on", "left_on", "right_on"):
                v = step.get(field)
                if isinstance(v, str):
                    keys.add(v)
                elif isinstance(v, list):
                    for c in v:
                        if isinstance(c, str):
                            keys.add(c)
    return sorted(keys)


def node_blocks_apply(node: RecipeNode) -> bool:
    """True if this node must have a non-empty reason before btn_apply."""
    return node.get("active", True) and node.get("node_type") in {
        "filter_row", "exclusion_row", "drop_column", "developer_raw_yaml"
    } and not node.get("reason", "").strip()


# ---------------------------------------------------------------------------
# SessionManager
# ---------------------------------------------------------------------------

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
    # 22-A-2: Manifest SHA256
    # ------------------------------------------------------------------

    @staticmethod
    def compute_manifest_sha256(manifest_path: Path) -> str:
        """SHA256 of the manifest YAML file content."""
        data = Path(manifest_path).read_bytes()
        return hashlib.sha256(data).hexdigest()

    # ------------------------------------------------------------------
    # 22-A-3: Data batch hash
    # ------------------------------------------------------------------

    @staticmethod
    def compute_data_batch_hash(source_files: dict[str, Path]) -> str:
        """SHA256 of all per-file SHA256s concatenated in sorted key order.

        source_files: {dataset_id: path}
        """
        parts = []
        for key in sorted(source_files.keys()):
            p = Path(source_files[key])
            if p.exists():
                file_hash = hashlib.sha256(p.read_bytes()).hexdigest()
            else:
                file_hash = f"MISSING:{key}"
            parts.append(f"{key}:{file_hash}")
        combined = "\n".join(parts).encode()
        return hashlib.sha256(combined).hexdigest()

    # ------------------------------------------------------------------
    # 22-A-4: Session key
    # ------------------------------------------------------------------

    @staticmethod
    def compute_session_key(manifest_sha256: str, data_batch_hash: str) -> str:
        """f'{manifest_sha256[:12]}:{data_batch_hash[:12]}'"""
        return f"{manifest_sha256[:12]}:{data_batch_hash[:12]}"

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
        manifest_id: str,
        manifest_sha256: str,
        data_batch_hash: str,
        source_files: dict[str, str],   # {dataset_id: path_str}
        parquet_paths: dict[str, str],   # {"assembly": ..., "contracted": ...}
    ) -> Path:
        """Write assembly.json to the session directory."""
        ghost = {
            "session_key": session_key,
            "manifest_id": manifest_id,
            "manifest_sha256": manifest_sha256,
            "data_batch_hash": data_batch_hash,
            "assembled_at": _now_iso(),
            "source_files": {
                k: {"path": str(v), "sha256": _file_sha256(v)}
                for k, v in source_files.items()
            },
            "parquet_paths": parquet_paths,
        }
        path = self.session_dir(session_key) / "assembly.json"
        path.write_text(json.dumps(ghost, indent=2))
        return path

    # ------------------------------------------------------------------
    # 22-A-7: Read T1/T2 assembly ghost
    # ------------------------------------------------------------------

    def read_assembly_ghost(self, session_key: str) -> dict | None:
        path = self.session_dir(session_key) / "assembly.json"
        if not path.exists():
            return None
        return json.loads(path.read_text())

    # ------------------------------------------------------------------
    # 22-A-8: T1/T2 restore — 6-step Prepped Chef check
    # ------------------------------------------------------------------

    def restore_t1t2(
        self,
        manifest_path: Path,
        source_files: dict[str, Path],
    ) -> dict:
        """6-step Prepped Chef restore logic.

        Returns:
            {
                "status": "fast_path" | "reassemble" | "new_session" | "missing_source",
                "session_key": str,
                "manifest_sha256": str,
                "data_batch_hash": str,
                "parquet_paths": dict,   # present on fast_path
                "missing": list[str],    # present on missing_source
            }
        """
        # Step 1: check for missing source files
        missing = [k for k, p in source_files.items() if not Path(p).exists()]
        if missing:
            return {"status": "missing_source", "missing": missing,
                    "session_key": "", "manifest_sha256": "", "data_batch_hash": "",
                    "parquet_paths": {}}

        # Step 2: compute hashes
        manifest_sha256 = self.compute_manifest_sha256(manifest_path)
        data_batch_hash = self.compute_data_batch_hash(source_files)
        session_key = self.compute_session_key(manifest_sha256, data_batch_hash)

        base = {"session_key": session_key, "manifest_sha256": manifest_sha256,
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
        manifest_id: str,
        manifest_sha256: str,
        data_batch_hash: str,
        tier_toggle: str,
        t3_recipe: list[dict] | None = None,
        t3_plot_overrides: dict | None = None,
        label: str = "",
        t3_recipe_by_plot: dict[str, list[dict]] | None = None,
        notification_log: list | None = None,
    ) -> Path:
        """Write a timestamped t3_{timestamp}.json to the session directory.

        Phase 22-J: prefers `t3_recipe_by_plot` (per-plot stacks). The flat
        `t3_recipe` argument is kept for backward compatibility with callers
        not yet updated and is stored alongside as a flattened convenience.
        """
        if t3_recipe_by_plot is None:
            t3_recipe_by_plot = {}
        if t3_recipe is None:
            # Flatten per-plot for the legacy field — readers that don't know
            # about per-plot still get a usable list.
            t3_recipe = [n for nodes in t3_recipe_by_plot.values() for n in nodes]
        ts = _timestamp()
        ghost = {
            "session_key": session_key,
            "manifest_id": manifest_id,
            "manifest_sha256": manifest_sha256,
            "data_batch_hash": data_batch_hash,
            "saved_at": _now_iso(),
            "label": label,
            "tier_toggle": tier_toggle,
            "schema_version": 2,           # 22-J: bumped from implicit v1 (flat list only)
            "t3_recipe": t3_recipe,        # legacy flat view, kept for bw compat
            "t3_recipe_by_plot": t3_recipe_by_plot,
            "t3_plot_overrides": t3_plot_overrides or {},
            "notification_log": notification_log or [],
        }
        path = self.session_dir(session_key) / f"t3_{ts}.json"
        path.write_text(json.dumps(ghost, indent=2))
        return path

    # ------------------------------------------------------------------
    # 22-A-10: List T3 ghosts for a session
    # ------------------------------------------------------------------

    def list_t3_ghosts(self, session_key: str) -> list[dict]:
        """All t3_*.json for a session, sorted newest-first.

        Phase 22-J: surfaces both `t3_recipe` (legacy flat) and
        `t3_recipe_by_plot` (per-plot stacks). For pre-22-J ghosts that have
        only the flat list, the flat nodes are bucketed under "__legacy__" so
        the UI can offer re-targeting (§12g.8).
        """
        d = self.session_dir(session_key)
        ghosts = []
        for f in sorted(d.glob("t3_*.json"), reverse=True):
            try:
                data = json.loads(f.read_text())
            except Exception:
                continue
            by_plot = data.get("t3_recipe_by_plot")
            flat = data.get("t3_recipe", [])
            if not isinstance(by_plot, dict) or not by_plot:
                # Legacy ghost — lift the flat list into the orphaned bucket.
                by_plot = {"__legacy__": list(flat)} if flat else {}
            ghosts.append({
                "file": str(f),
                "saved_at": data.get("saved_at", ""),
                "label": data.get("label", ""),
                "manifest_sha256": data.get("manifest_sha256", ""),
                "data_batch_hash": data.get("data_batch_hash", ""),
                "tier_toggle": data.get("tier_toggle", "T2"),
                "schema_version": data.get("schema_version", 1),
                "t3_recipe": flat,
                "t3_recipe_by_plot": by_plot,
                "t3_plot_overrides": data.get("t3_plot_overrides", {}),
            })
        return ghosts

    # ------------------------------------------------------------------
    # 22-A-11: List all sessions
    # ------------------------------------------------------------------

    def list_all_sessions(self) -> list[dict]:
        """All sessions, sorted by most-recent T3 ghost saved_at (newest first)."""
        sessions = []
        for assembly_file in self.root.glob("*/assembly.json"):
            try:
                ghost = json.loads(assembly_file.read_text())
                session_key = ghost.get("session_key", assembly_file.parent.name)
                t3_ghosts = self.list_t3_ghosts(session_key)
                latest_t3 = t3_ghosts[0].get("saved_at", "") if t3_ghosts else ""
                sessions.append({
                    "session_key": session_key,
                    "manifest_id": ghost.get("manifest_id", ""),
                    "manifest_sha256": ghost.get("manifest_sha256", ""),
                    "data_batch_hash": ghost.get("data_batch_hash", ""),
                    "assembled_at": ghost.get("assembled_at", ""),
                    "latest_t3_saved_at": latest_t3,
                    "t3_count": len(t3_ghosts),
                })
            except Exception:
                continue
        sessions.sort(key=lambda s: s["latest_t3_saved_at"] or s["assembled_at"], reverse=True)
        return sessions

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

    def import_session_zip(self, zip_bytes: bytes) -> str:
        """Unpack a session zip into _sessions/. Returns the restored session_key."""
        import io
        buf = io.BytesIO(zip_bytes)
        with zipfile.ZipFile(buf, "r") as zf:
            names = zf.namelist()
            assembly_files = [n for n in names if n.endswith("assembly.json")]
            t3_files = [n for n in names if "/t3_" in n and n.endswith(".json")]
            if not assembly_files and not t3_files:
                raise ValueError("ZIP does not contain a valid session (no assembly.json or t3_*.json found).")
            zf.extractall(self.root)
            # Derive session_key from assembly.json if present, otherwise from T3 ghost.
            anchor = assembly_files[0] if assembly_files else t3_files[0]
            session_key = Path(anchor).parts[0]
        return session_key

    # ------------------------------------------------------------------
    # 22-A-14: Delete session
    # ------------------------------------------------------------------

    def delete_session(self, session_key: str) -> None:
        """Remove the entire session directory."""
        d = self.root / session_key
        if d.exists():
            shutil.rmtree(d)

    # ------------------------------------------------------------------
    # Utilities
    # ------------------------------------------------------------------

    def get_session_label(self, session_key: str) -> str:
        """Return the label from the most-recent T3 ghost, or ''."""
        ghosts = self.list_t3_ghosts(session_key)
        return ghosts[0].get("label", "") if ghosts else ""

    def set_session_label(self, session_key: str, label: str) -> None:
        """Update the label field in the most-recent T3 ghost."""
        ghosts = self.list_t3_ghosts(session_key)
        if not ghosts:
            return
        path = Path(ghosts[0]["file"])
        data = json.loads(path.read_text())
        data["label"] = label
        path.write_text(json.dumps(data, indent=2))


# ---------------------------------------------------------------------------
# T3 recipe helpers
# ---------------------------------------------------------------------------

def recipe_sha256(t3_recipe: list[dict]) -> str:
    """SHA256 of the active-only T3 recipe serialized to JSON (sorted keys)."""
    active = [n for n in t3_recipe if n.get("active", True)]
    serialized = json.dumps(active, sort_keys=True, ensure_ascii=False).encode()
    return hashlib.sha256(serialized).hexdigest()


def gatekeeper_blocked(t3_recipe: list[dict]) -> list[str]:
    """Return list of node IDs that block btn_apply (active nodes with empty reason)."""
    return [n["id"] for n in t3_recipe if node_blocks_apply(n)]


# ---------------------------------------------------------------------------
# Private helpers
# ---------------------------------------------------------------------------

def _now_iso() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%S")


def _timestamp() -> str:
    return datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%S%f")


def _file_sha256(path: str | Path) -> str:
    p = Path(path)
    if not p.exists():
        return f"MISSING"
    return hashlib.sha256(p.read_bytes()).hexdigest()
