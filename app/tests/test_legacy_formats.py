"""Files written before the configuration rename stop with a message that names the fix (ADR-091)."""
import importlib.util
import io
import json
import textwrap
import zipfile
from pathlib import Path

import pytest

from app.modules.session_manager import LegacySessionError, SessionManager
from utils.config_loader import ConfigManager

REPO = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("migrate", REPO / "assets" / "scripts" / "migrate_config_vocabulary.py")
migrate = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(migrate)

OLD_SESSION = {"session_key": "a:b", "manifest_id": "p", "manifest_sha256": "x" * 64, "data_batch_hash": "y",
               "t3_recipe": [], "t3_recipe_by_plot": {"plot": [{"id": "n1", "recipe": "keep me"}]}}


# --- the recipe loader ---

def _recipe(tmp_path, body):
    p = tmp_path / "r.yaml"
    p.write_text(textwrap.dedent(body))
    return p


def test_old_join_manifests_key_stops_the_loader_and_names_joins(tmp_path, capsys):
    p = _recipe(tmp_path, """
        id: r
        data_schemas: {}
        join_manifests:
          A: {recipe: []}
        analysis_groups: {g: {plots: {}}}
        """)
    with pytest.raises(SystemExit):
        ConfigManager(str(p))
    err = capsys.readouterr().err
    assert "join_manifests" in err and "'joins'" in err and "migrate_config_vocabulary" in err


def test_old_recipe_key_in_a_join_names_steps(tmp_path, capsys):
    p = _recipe(tmp_path, """
        id: r
        data_schemas: {}
        joins:
          A: {recipe: []}
        analysis_groups: {g: {plots: {}}}
        """)
    with pytest.raises(SystemExit):
        ConfigManager(str(p))
    err = capsys.readouterr().err
    assert "'recipe'" in err and "'steps'" in err


def test_old_top_level_type_key_is_refused_and_the_fix_is_named(tmp_path, capsys):
    p = _recipe(tmp_path, """
        id: r
        type: species
        data_schemas: {}
        joins: {}
        analysis_groups: {g: {plots: {}}}
        """)
    with pytest.raises(SystemExit):
        ConfigManager(str(p))
    err = capsys.readouterr().err
    assert "'type'" in err and "removed" in err and "info:" in err


def test_conversion_drops_the_top_level_type_but_not_nested_type_keys():
    old = "id: r\ntype: species\ndata_schemas:\n  A:\n    input_fields:\n      x: {type: categorical}\n"
    new = migrate.convert_recipe_text(old)
    assert "type: species" not in new and "type: categorical" in new


# --- saved sessions ---

@pytest.fixture
def sm(tmp_path):
    return SessionManager(tmp_path / "sessions")


def test_old_assembly_ghost_is_refused_with_the_fix(sm):
    d = sm.session_dir("a:b")
    (d / "assembly.json").write_text(json.dumps(OLD_SESSION))
    with pytest.raises(LegacySessionError) as exc:
        sm.read_assembly_ghost("a:b")
    assert "data_analysis_recipe_sha256" in str(exc.value) and "migrate_config_vocabulary" in str(exc.value)


def test_old_session_is_listed_with_its_problem_not_skipped(sm):
    d = sm.session_dir("a:b")
    (d / "assembly.json").write_text(json.dumps(OLD_SESSION))
    listed = sm.list_all_sessions()
    assert len(listed) == 1 and "migrate_config_vocabulary" in listed[0]["legacy_problem"]


def test_old_session_zip_is_refused_before_anything_is_extracted(sm):
    buf = io.BytesIO()
    with zipfile.ZipFile(buf, "w") as zf:
        zf.writestr("a:b/assembly.json", json.dumps(OLD_SESSION))
    with pytest.raises(LegacySessionError):
        sm.import_session_zip(buf.getvalue())
    assert not list(sm.root.glob("*/assembly.json"))


# --- the migration script ---

def test_recipe_conversion_changes_keys_only():
    old = "joins_note: recipe stays in text\njoin_manifests:\n  A:\n    recipe: !include 'x.yaml'\n  B:\n    - recipe: []\n"
    new = migrate.convert_recipe_text(old)
    assert "joins:" in new and "    steps: !include 'x.yaml'" in new and "    - steps: []" in new
    assert "recipe stays in text" in new
    assert migrate.convert_recipe_text(new) == new  # idempotent


def test_session_conversion_renames_keys_not_values():
    new = migrate.convert_session_json(OLD_SESSION)
    assert new["data_analysis_recipe_sha256"] == "x" * 64 and "manifest_sha256" not in new
    assert new["t3_audit_steps_by_plot"]["plot"][0]["recipe"] == "keep me"


def test_dry_run_writes_nothing_and_apply_converts(tmp_path):
    f = tmp_path / "assembly.json"
    f.write_text(json.dumps(OLD_SESSION))
    ns = type("A", (), dict(recipes=None, sessions=str(tmp_path), gallery=None, apply=False))
    migrate.run(ns)
    assert "manifest_sha256" in f.read_text()
    ns.apply = True
    migrate.run(ns)
    assert "data_analysis_recipe_sha256" in f.read_text()
    migrate.run(ns)  # second run: nothing left
    assert json.loads(f.read_text())["data_analysis_recipe_sha256"] == "x" * 64


def test_old_gallery_bundle_is_converted_and_then_indexed(tmp_path):
    from viz_gallery.gallery_manager import GalleryManager
    b = tmp_path / "gal" / "bar"
    b.mkdir(parents=True)
    (b / "recipe_manifest.yaml").write_text("info: {name: Bar}\nplots: {}\n")
    (b / "recipe_meta.md").write_text("## Bar\n")
    (b / "example_data.tsv").write_text("a\n1\n")
    before = GalleryManager(str(tmp_path / "gal")).rebuild_index()
    assert before["registry"] == {} and before["metadata"]["legacy_bundles"] == ["bar"]
    ns = type("A", (), dict(recipes=None, sessions=None, gallery=str(tmp_path / "gal"), apply=True))
    migrate.run(ns)
    after = GalleryManager(str(tmp_path / "gal")).rebuild_index()
    assert list(after["registry"]) == ["bar"]
