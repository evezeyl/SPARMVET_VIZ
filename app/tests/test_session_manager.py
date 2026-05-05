"""app/tests/test_session_manager.py
Unit tests for SessionManager and RecipeNode helpers.

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
    make_recipe_node,
    node_blocks_apply,
    gatekeeper_blocked,
    recipe_sha256,
)


# ---------------------------------------------------------------------------
# Fixtures
# ---------------------------------------------------------------------------

@pytest.fixture()
def tmp_location(tmp_path):
    return tmp_path / "user_sessions"


@pytest.fixture()
def sm(tmp_location):
    return SessionManager(tmp_location)


@pytest.fixture()
def manifest_file(tmp_path):
    p = tmp_path / "my_pipeline.yaml"
    p.write_text("id: my_pipeline\nversion: 1\n")
    return p


@pytest.fixture()
def source_files(tmp_path):
    a = tmp_path / "metadata.tsv"
    b = tmp_path / "amr.tsv"
    a.write_text("sample_id\tspecies\nS1\tcat\n")
    b.write_text("sample_id\tgene\nS1\tblaZ\n")
    return {"metadata": a, "amr": b}


# ---------------------------------------------------------------------------
# 22-A-2: compute_manifest_sha256
# ---------------------------------------------------------------------------

def test_manifest_sha256_stable(manifest_file):
    h1 = SessionManager.compute_manifest_sha256(manifest_file)
    h2 = SessionManager.compute_manifest_sha256(manifest_file)
    assert h1 == h2
    assert len(h1) == 64


def test_manifest_sha256_changes_on_edit(manifest_file):
    h1 = SessionManager.compute_manifest_sha256(manifest_file)
    manifest_file.write_text("id: my_pipeline\nversion: 2\n")
    h2 = SessionManager.compute_manifest_sha256(manifest_file)
    assert h1 != h2


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

def test_write_read_assembly_ghost(sm, manifest_file, source_files):
    msig = SessionManager.compute_manifest_sha256(manifest_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    sm.write_assembly_ghost(
        session_key=key,
        manifest_id="my_pipeline",
        manifest_sha256=msig,
        data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": "tmp/a.parquet", "contracted": "tmp/c.parquet"},
    )
    ghost = sm.read_assembly_ghost(key)
    assert ghost is not None
    assert ghost["manifest_id"] == "my_pipeline"
    assert ghost["session_key"] == key
    assert "metadata" in ghost["source_files"]
    assert "sha256" in ghost["source_files"]["metadata"]


def test_read_assembly_ghost_missing(sm):
    assert sm.read_assembly_ghost("nonexistent:session0") is None


# ---------------------------------------------------------------------------
# 22-A-8: restore_t1t2
# ---------------------------------------------------------------------------

def test_restore_t1t2_missing_source(sm, manifest_file, tmp_path):
    result = sm.restore_t1t2(manifest_file, {"missing": tmp_path / "gone.tsv"})
    assert result["status"] == "missing_source"
    assert "missing" in result["missing"]


def test_restore_t1t2_new_session(sm, manifest_file, source_files):
    result = sm.restore_t1t2(manifest_file, source_files)
    assert result["status"] == "new_session"
    assert result["session_key"] != ""


def test_restore_t1t2_fast_path(sm, manifest_file, source_files, tmp_path):
    msig = SessionManager.compute_manifest_sha256(manifest_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    # Create fake Parquet files so fast_path check passes
    p1 = tmp_path / "a.parquet"
    p2 = tmp_path / "c.parquet"
    p1.write_bytes(b"PAR1")
    p2.write_bytes(b"PAR1")

    sm.write_assembly_ghost(
        session_key=key, manifest_id="my_pipeline",
        manifest_sha256=msig, data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": str(p1), "contracted": str(p2)},
    )
    result = sm.restore_t1t2(manifest_file, source_files)
    assert result["status"] == "fast_path"
    assert result["parquet_paths"]["assembly"] == str(p1)


def test_restore_t1t2_reassemble(sm, manifest_file, source_files):
    msig = SessionManager.compute_manifest_sha256(manifest_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    # Write ghost pointing to non-existent Parquets
    sm.write_assembly_ghost(
        session_key=key, manifest_id="my_pipeline",
        manifest_sha256=msig, data_batch_hash=dbh,
        source_files={k: str(v) for k, v in source_files.items()},
        parquet_paths={"assembly": "/tmp/gone.parquet", "contracted": "/tmp/also_gone.parquet"},
    )
    result = sm.restore_t1t2(manifest_file, source_files)
    assert result["status"] == "reassemble"


# ---------------------------------------------------------------------------
# 22-A-9/10: write and list T3 ghosts
# ---------------------------------------------------------------------------

def test_write_list_t3_ghosts(sm):
    key = "aaaaaaaaaaaa:bbbbbbbbbbbb"
    recipe = [make_recipe_node("filter_row", {"column": "species", "op": "in", "value": ["cat"]}, reason="test")]

    p1 = sm.write_t3_ghost(key, "my_pipeline", "a" * 64, "b" * 64, "T3", recipe, {}, label="first")
    p2 = sm.write_t3_ghost(key, "my_pipeline", "a" * 64, "b" * 64, "T3", recipe, {}, label="second")

    ghosts = sm.list_t3_ghosts(key)
    assert len(ghosts) == 2
    assert ghosts[0]["label"] in ("first", "second")  # sorted newest-first
    assert ghosts[0]["saved_at"] >= ghosts[1]["saved_at"]


# ---------------------------------------------------------------------------
# 22-A-11: list_all_sessions
# ---------------------------------------------------------------------------

def test_list_all_sessions(sm, manifest_file, source_files):
    msig = SessionManager.compute_manifest_sha256(manifest_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)

    sm.write_assembly_ghost(key, "my_pipeline", msig, dbh,
                            {k: str(v) for k, v in source_files.items()}, {})
    sessions = sm.list_all_sessions()
    assert any(s["session_key"] == key for s in sessions)


# ---------------------------------------------------------------------------
# 22-A-12/13: export and import zip
# ---------------------------------------------------------------------------

def test_export_import_roundtrip(sm, manifest_file, source_files, tmp_path):
    msig = SessionManager.compute_manifest_sha256(manifest_file)
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
    assert ghost["manifest_id"] == "my_pipeline"


def test_import_invalid_zip_raises(sm):
    with pytest.raises(Exception):
        sm.import_session_zip(b"not a zip")


# ---------------------------------------------------------------------------
# 22-A-14: delete_session
# ---------------------------------------------------------------------------

def test_delete_session(sm, manifest_file, source_files):
    msig = SessionManager.compute_manifest_sha256(manifest_file)
    dbh = SessionManager.compute_data_batch_hash(source_files)
    key = SessionManager.compute_session_key(msig, dbh)
    sm.write_assembly_ghost(key, "my_pipeline", msig, dbh,
                            {k: str(v) for k, v in source_files.items()}, {})
    assert sm.session_dir(key).exists()
    sm.delete_session(key)
    assert not (sm.root / key).exists()


# ---------------------------------------------------------------------------
# RecipeNode helpers
# ---------------------------------------------------------------------------

def test_make_recipe_node_defaults():
    node = make_recipe_node("filter_row", {"column": "x", "op": "eq", "value": "a"})
    assert node["active"] is True
    assert node["reason"] == ""
    assert "id" in node
    assert "created_at" in node


def test_node_blocks_apply_empty_reason():
    node = make_recipe_node("filter_row", {}, reason="")
    assert node_blocks_apply(node) is True


def test_node_blocks_apply_filled_reason():
    node = make_recipe_node("filter_row", {}, reason="Outlier removed.")
    assert node_blocks_apply(node) is False


def test_node_blocks_apply_aesthetic_never_blocks():
    node = make_recipe_node("aesthetic_override", {}, reason="")
    assert node_blocks_apply(node) is False


def test_node_blocks_apply_inactive_never_blocks():
    node = make_recipe_node("filter_row", {}, reason="")
    node["active"] = False
    assert node_blocks_apply(node) is False


def test_gatekeeper_blocked():
    recipe = [
        make_recipe_node("filter_row", {}, reason="ok"),
        make_recipe_node("exclusion_row", {}, reason=""),
        make_recipe_node("drop_column", {"column": "x"}, reason=""),
        make_recipe_node("aesthetic_override", {}, reason=""),
    ]
    blocked = gatekeeper_blocked(recipe)
    assert len(blocked) == 2
    assert recipe[1]["id"] in blocked
    assert recipe[2]["id"] in blocked


def test_recipe_sha256_active_only():
    recipe = [
        make_recipe_node("filter_row", {}, reason="kept"),
        {**make_recipe_node("exclusion_row", {}, reason="gone"), "active": False},
    ]
    h = recipe_sha256(recipe)
    assert isinstance(h, str) and len(h) == 64

    # Removing inactive node should not change the hash
    recipe2 = [recipe[0]]
    assert recipe_sha256(recipe) == recipe_sha256(recipe2)


# ---------------------------------------------------------------------------
# Label helpers
# ---------------------------------------------------------------------------

def test_set_get_label(sm):
    key = "aaaaaaaaaaaa:cccccccccccc"
    sm.write_t3_ghost(key, "pid", "a" * 64, "c" * 64, "T3", [], {}, label="original")
    sm.set_session_label(key, "updated")
    assert sm.get_session_label(key) == "updated"
