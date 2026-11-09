"""app/tests/test_session_manager.py
Unit tests for SessionManager and AuditStep helpers.

Run:
    ./.venv/bin/python -m pytest app/tests/test_session_manager.py -v

# @deps
# provides: test:session_manager
# consumes: app/modules/session_manager.py
# consumed_by: CI
# doc: .claude/rules/ui_implementation_contract.md#12d
# @end_deps
"""

import json
import tempfile
from pathlib import Path

import pytest

from app.modules.session_manager import (
    SessionManager,
    make_audit_step,
    node_blocks_apply,
    gatekeeper_blocked,
    audit_steps_sha256,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_location(tmp_path):
    return tmp_path / "user_data"


@pytest.fixture()
def sm(tmp_location):
    return SessionManager(tmp_location)


def _data_analysis_recipe_text(version: int) -> str:
    """A minimal data analysis recipe that ConfigManager accepts (it requires analysis_groups, ADR-077)."""
    return (
        f"id: my_pipeline\nversion: {version}\n"
        "analysis_groups:\n  g:\n    label: G\n    plots:\n      p:\n        label: P\n"
        "        spec:\n          target_dataset: C\n          mapping: {x: a}\n"
        "          layers:\n            - name: geom_bar\n"
    )


@pytest.fixture()
def data_analysis_recipe_file(tmp_path):
    p = tmp_path / "my_pipeline.yaml"
    p.write_text(_data_analysis_recipe_text(1))
    return p


@pytest.fixture()
def source_files(tmp_path):
    a = tmp_path / "metadata.tsv"
    b = tmp_path / "amr.tsv"
    a.write_text("sample_id\tspecies\nS1\tcat\n")
    b.write_text("sample_id\tgene\nS1\tblaZ\n")
    return {"metadata": a, "amr": b}


# ---------------------------------------------------------------------------
# 22-A-2: compute_data_analysis_recipe_sha256
# ---------------------------------------------------------------------------

def test_data_analysis_recipe_sha256_stable(data_analysis_recipe_file):
    h1 = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    h2 = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    assert h1 == h2
    assert len(h1) == 64


def test_data_analysis_recipe_sha256_changes_on_edit(data_analysis_recipe_file):
    h1 = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    data_analysis_recipe_file.write_text(_data_analysis_recipe_text(2))   # same size, written in the same clock tick
    h2 = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    assert h1 != h2


def test_data_analysis_recipe_sha256_covers_included_files(tmp_path):
    """The file-set hash changes when an INCLUDED file changes (ADR-089)."""
    inc = tmp_path / "frag.yaml"
    inc.write_text("label: G\n")
    p = tmp_path / "with_include.yaml"
    p.write_text(
        "id: x\nanalysis_groups:\n  g:\n    label: !include 'frag.yaml'\n    plots:\n      p:\n"
        "        label: P\n        spec:\n          target_dataset: C\n          mapping: {x: a}\n"
        "          layers:\n            - name: geom_bar\n")
    h1 = SessionManager.compute_data_analysis_recipe_sha256(p)
    inc.write_text("label: H\n")
    assert SessionManager.compute_data_analysis_recipe_sha256(p) != h1


# ---------------------------------------------------------------------------
# 22-A-3: compute_data_batch_hash
# ---------------------------------------------------------------------------

def test_data_batch_hash_stable(source_files):
    h1 = SessionManager.compute_data_batch_hash(source_files)
    h2 = SessionManager.compute_data_batch_hash(source_files)
    assert h1 == h2


def test_data_batch_hash_changes_on_file_edit(source_files):
    h1 = SessionManager.compute_data_batch_hash(source_files)
    source_files["metadata"].write_text("sample_id\tspecies\nS2\tdog\n")
    h2 = SessionManager.compute_data_batch_hash(source_files)
    assert h1 != h2


def test_data_batch_hash_missing_file(tmp_path):
    files = {"missing": tmp_path / "nonexistent.tsv"}
    h = SessionManager.compute_data_batch_hash(files)
    assert isinstance(h, str) and len(h) == 64


# ---------------------------------------------------------------------------
# 22-A-4: compute_session_key
# ---------------------------------------------------------------------------

def test_session_key_format():
    key = SessionManager.compute_session_key("a" * 64, "b" * 64)
    assert key == "aaaaaaaaaaaa:bbbbbbbbbbbb"


# ---------------------------------------------------------------------------
# 22-A-5: session_dir
# ---------------------------------------------------------------------------

def test_session_dir_created(sm):
    d = sm.session_dir("abc123:def456")
    assert d.exists()
    assert d.is_dir()


# ---------------------------------------------------------------------------
# 22-A-6/7: write and read assembly ghost
# ---------------------------------------------------------------------------

def test_write_read_assembly_ghost(sm, data_analysis_recipe_file, source_files):
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    sm.write_assembly_ghost(
        session_key=key,
        data_analysis_recipe_id="my_pipeline",
        data_analysis_recipe_sha256=msig,
        data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": "tmp/a.parquet", "contracted": "tmp/c.parquet"},
    )
    ghost = sm.read_assembly_ghost(key)
    assert ghost is not None
    assert ghost["data_analysis_recipe_id"] == "my_pipeline"
    assert ghost["session_key"] == key
    assert "metadata" in ghost["source_files"]
    assert "sha256" in ghost["source_files"]["metadata"]


def test_read_assembly_ghost_missing(sm):
    assert sm.read_assembly_ghost("nonexistent:session0") is None


# ---------------------------------------------------------------------------
# 22-A-8: restore_t1t2
# ---------------------------------------------------------------------------

def test_restore_t1t2_missing_source(sm, data_analysis_recipe_file, tmp_path):
    result = sm.restore_t1t2(data_analysis_recipe_file, {"missing": tmp_path / "gone.tsv"})
    assert result["status"] == "missing_source"
    assert "missing" in result["missing"]


def test_restore_t1t2_new_session(sm, data_analysis_recipe_file, source_files):
    result = sm.restore_t1t2(data_analysis_recipe_file, source_files)
    assert result["status"] == "new_session"
    assert result["session_key"] != ""


def test_restore_t1t2_fast_path(sm, data_analysis_recipe_file, source_files, tmp_path):
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    # Create fake Parquet files so fast_path check passes
    p1 = tmp_path / "a.parquet"
    p2 = tmp_path / "c.parquet"
    p1.write_bytes(b"PAR1")
    p2.write_bytes(b"PAR1")

    sm.write_assembly_ghost(
        session_key=key, data_analysis_recipe_id="my_pipeline",
        data_analysis_recipe_sha256=msig, data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": str(p1), "contracted": str(p2)},
    )
    result = sm.restore_t1t2(data_analysis_recipe_file, source_files)
    assert result["status"] == "fast_path"
    assert result["parquet_paths"]["assembly"] == str(p1)


def test_restore_t1t2_reassemble(sm, data_analysis_recipe_file, source_files):
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    # Write ghost pointing to non-existent Parquets
    sm.write_assembly_ghost(
        session_key=key, data_analysis_recipe_id="my_pipeline",
        data_analysis_recipe_sha256=msig, data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": "/tmp/gone.parquet", "contracted": "/tmp/also_gone.parquet"},
    )
    result = sm.restore_t1t2(data_analysis_recipe_file, source_files)
    assert result["status"] == "reassemble"


# ---------------------------------------------------------------------------
# 22-A-9/10: write and list T3 ghosts
# ---------------------------------------------------------------------------

def test_write_list_t3_ghosts(sm):
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    audit_steps = [make_audit_step("filter_row", {"column": "species", "op": "in", "value": ["cat"]}, reason="test")]

    p1 = sm.write_t3_ghost(key, "my_pipeline", "a" * 64, "b" * 64, "T3", audit_steps, {}, label="first")
    p2 = sm.write_t3_ghost(key, "my_pipeline", "a" * 64, "b" * 64, "T3", audit_steps, {}, label="second")

    ghosts = sm.list_t3_ghosts(key)
    assert len(ghosts) == 2
    assert ghosts[0]["label"] in ("first", "second")  # sorted newest-first
    assert ghosts[0]["saved_at"] >= ghosts[1]["saved_at"]


# ---------------------------------------------------------------------------
# REPRO-RESTORE-HASH-1 (ADR-097 decision 3/§6d): t3_audit_steps_sha256 self-consistency
# ---------------------------------------------------------------------------

def test_t3_ghost_carries_a_self_consistency_hash(sm):
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    audit_steps = [make_audit_step("filter_row", {"column": "species", "op": "in", "value": ["cat"]}, reason="test")]
    sm.write_t3_ghost(key, "my_pipeline", "a" * 64, "b" * 64, "T3", audit_steps, {}, label="x")
    ghost = sm.list_t3_ghosts(key)[0]
    assert len(ghost["t3_audit_steps_sha256"]) == 64


def test_t3_ghost_hash_is_stable_for_identical_content(sm):
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    audit_steps = [make_audit_step("filter_row", {"column": "species"}, reason="test")]
    sm.write_t3_ghost(key, "p", "a" * 64, "b" * 64, "T3", audit_steps, {}, label="a")
    sm.write_t3_ghost(key, "p", "a" * 64, "b" * 64, "T3", list(audit_steps), {}, label="b")
    ghosts = sm.list_t3_ghosts(key)
    assert ghosts[0]["t3_audit_steps_sha256"] == ghosts[1]["t3_audit_steps_sha256"]


def test_t3_ghost_hash_differs_for_different_content(sm):
    """t3_audit_steps_by_plot is what the hash covers — t3_audit_steps_by_plot, not the
    legacy flat list, is the authoritative, current representation (Phase 22-J)."""
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    sm.write_t3_ghost(key, "p", "a" * 64, "b" * 64, "T3", label="a",
                       t3_audit_steps_by_plot={"subtab_p": [make_audit_step("filter_row", {"column": "species"}, reason="x")]})
    sm.write_t3_ghost(key, "p", "a" * 64, "b" * 64, "T3", label="b",
                       t3_audit_steps_by_plot={"subtab_p": [make_audit_step("exclusion_row", {"column": "species"}, reason="x")]})
    ghosts = sm.list_t3_ghosts(key)
    assert ghosts[0]["t3_audit_steps_sha256"] != ghosts[1]["t3_audit_steps_sha256"]


def test_legacy_ghost_with_no_stored_hash_reports_empty_not_a_mismatch(sm, tmp_path):
    """A ghost written before this field existed must not look corrupted on restore —
    an empty string, not a fabricated or recomputed value standing in for one."""
    import json
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    d = sm.session_dir(key)
    d.mkdir(parents=True, exist_ok=True)
    legacy = {
        "session_key": key, "data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64,
        "saved_at": "2026-01-01T00:00:00", "label": "", "tier_toggle": "T3",
        "t3_audit_steps": [], "t3_audit_steps_by_plot": {"subtab_p": []}, "t3_plot_overrides": {},
    }
    (d / "t3_20260101_000000.json").write_text(json.dumps(legacy))
    ghost = sm.list_t3_ghosts(key)[0]
    assert ghost["t3_audit_steps_sha256"] == ""


# ---------------------------------------------------------------------------
# 22-A-11: list_all_sessions
# ---------------------------------------------------------------------------

def test_list_all_sessions(sm, data_analysis_recipe_file, source_files):
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    sm.write_assembly_ghost(key, "my_pipeline", msig, dbh,
                            {k: str(v) for k, v in source_files.items()}, {})
    sessions = sm.list_all_sessions()
    assert any(s["session_key"] == key for s in sessions)


# ---------------------------------------------------------------------------
# 22-A-12/13: export and import zip
# ---------------------------------------------------------------------------

def test_export_import_roundtrip(sm, data_analysis_recipe_file, source_files, tmp_path):
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    sm.write_assembly_ghost(key, "my_pipeline", msig, dbh,
                            {k: str(v) for k, v in source_files.items()}, {})
    sm.write_t3_ghost(key, "my_pipeline", msig, dbh, "T3", [], {})

    zip_bytes = sm.export_session_zip(key)
    assert len(zip_bytes) > 0

    # Import into a fresh SessionManager
    sm2 = SessionManager(tmp_path / "import_target")
    restored_key = sm2.import_session_zip(zip_bytes)
    assert restored_key == key
    ghost = sm2.read_assembly_ghost(key)
    assert ghost is not None
    assert ghost["data_analysis_recipe_id"] == "my_pipeline"


def test_import_invalid_zip_raises(sm):
    with pytest.raises(Exception):
        sm.import_session_zip(b"not a zip")


# ---------------------------------------------------------------------------
# 22-A-14: delete_session
# ---------------------------------------------------------------------------

def test_delete_session(sm, data_analysis_recipe_file, source_files):
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)
    sm.write_assembly_ghost(key, "my_pipeline", msig, dbh,
                            {k: str(v) for k, v in source_files.items()}, {})
    assert sm.session_dir(key).exists()
    sm.delete_session(key)
    assert not (sm.root / key).exists()


# ---------------------------------------------------------------------------
# HOM-54: delete_all_sessions
# ---------------------------------------------------------------------------

def test_delete_all_sessions_removes_every_session(sm, data_analysis_recipe_file, source_files):
    msig1 = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh1 = SessionManager.compute_data_batch_hash(source_files)
    key1 = SessionManager.compute_session_key(msig1, dbh1)
    sm.write_assembly_ghost(key1, "my_pipeline", msig1, dbh1,
                            {k: str(v) for k, v in source_files.items()}, {})

    # A second, distinct session (different data analysis recipe version -> different sha256).
    recipe2 = data_analysis_recipe_file.parent / "my_pipeline_v2.yaml"
    recipe2.write_text(_data_analysis_recipe_text(2))
    msig2 = SessionManager.compute_data_analysis_recipe_sha256(recipe2)
    key2 = SessionManager.compute_session_key(msig2, dbh1)
    sm.write_assembly_ghost(key2, "my_pipeline", msig2, dbh1,
                            {k: str(v) for k, v in source_files.items()}, {})

    assert len(sm.list_all_sessions()) == 2

    deleted_count = sm.delete_all_sessions()

    assert deleted_count == 2
    assert sm.list_all_sessions() == []
    assert not (sm.root / key1).exists()
    assert not (sm.root / key2).exists()


def test_delete_all_sessions_on_empty_store_is_a_noop(sm):
    assert sm.delete_all_sessions() == 0
    assert sm.list_all_sessions() == []


# ---------------------------------------------------------------------------
# AuditStep helpers
# ---------------------------------------------------------------------------

def test_make_audit_step_defaults():
    node = make_audit_step("filter_row", {"column": "x", "op": "eq", "value": "a"})
    assert node["active"] is True
    assert node["reason"] == ""
    assert "id" in node
    assert "created_at" in node


def test_node_blocks_apply_empty_reason():
    node = make_audit_step("filter_row", {}, reason="")
    assert node_blocks_apply(node) is True


def test_node_blocks_apply_filled_reason():
    node = make_audit_step("filter_row", {}, reason="Outlier removed.")
    assert node_blocks_apply(node) is False


def test_node_blocks_apply_aesthetic_never_blocks():
    node = make_audit_step("aesthetic_override", {}, reason="")
    assert node_blocks_apply(node) is False


def test_node_blocks_apply_inactive_never_blocks():
    node = make_audit_step("filter_row", {}, reason="")
    node["active"] = False
    assert node_blocks_apply(node) is False


def test_gatekeeper_blocked():
    audit_steps = [
        make_audit_step("filter_row", {}, reason="ok"),
        make_audit_step("exclusion_row", {}, reason=""),
        make_audit_step("drop_column", {"column": "x"}, reason=""),
        make_audit_step("aesthetic_override", {}, reason=""),
    ]
    blocked = gatekeeper_blocked(audit_steps)
    assert len(blocked) == 2
    assert audit_steps[1]["id"] in blocked
    assert audit_steps[2]["id"] in blocked


def test_transformation_sha256_active_only():
    audit_steps = [
        make_audit_step("filter_row", {}, reason="kept"),
        {**make_audit_step("exclusion_row", {}, reason="gone"), "active": False},
    ]
    h = audit_steps_sha256(audit_steps)
    assert isinstance(h, str) and len(h) == 64

    # Removing inactive node should not change the hash
    audit_steps2 = [audit_steps[0]]
    assert audit_steps_sha256(audit_steps) == audit_steps_sha256(audit_steps2)


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------

def test_set_get_label(sm):
    key = "aaaaaaaaaaaa:cccccccccccc"
    sm.write_t3_ghost(key, "pid", "a" * 64, "c" * 64, "T3", [], {}, label="original")
    sm.set_session_label(key, "updated")
    assert sm.get_session_label(key) == "updated"


# ---------------------------------------------------------------------------
# Stored formats on disk (characterization for the configuration rename, ADR-091)
# The key names below are written into saved sessions. The rename changes them and
# ships a migration; these tests pin today's names so the change is deliberate.
# ---------------------------------------------------------------------------

def test_stored_assembly_ghost_key_names(sm, data_analysis_recipe_file, source_files):
    import json
    msig = SessionManager.compute_data_analysis_recipe_sha256(data_analysis_recipe_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)
    sm.write_assembly_ghost(
        session_key=key, data_analysis_recipe_id="my_pipeline", data_analysis_recipe_sha256=msig, data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": "tmp/a.parquet", "contracted": "tmp/c.parquet"},
    )
    raw = json.loads(next((sm.session_dir(key)).glob("assembly.json")).read_text())
    assert {"session_key", "data_analysis_recipe_id", "data_analysis_recipe_sha256", "data_batch_hash", "source_files"} <= set(raw)


def test_stored_t3_ghost_key_names(sm):
    import json
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    node = make_audit_step("filter_row", {"column": "species", "op": "in", "value": ["cat"]}, reason="test")
    path = sm.write_t3_ghost(key, "my_pipeline", "a" * 64, "b" * 64, "T3", [node], {}, label="x")
    raw = json.loads(Path(path).read_text())
    assert {"session_key", "data_analysis_recipe_id", "data_analysis_recipe_sha256", "data_batch_hash", "saved_at",
            "tier_toggle", "t3_audit_steps", "t3_plot_overrides"} <= set(raw)
