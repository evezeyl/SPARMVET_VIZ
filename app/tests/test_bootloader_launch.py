"""Characterization of how the app is launched: which file each launch variable selects.

Written against the names in use on 2026-11-07 (SPARMVET_PROFILE, SPARMVET_PERSONA,
default_persona, fixed_manifest, default_manifest). The configuration rename of ADR-091
(issue evezeyl/SPARMVET_VIZ#27) renames these in the same commits as the code, and the
behaviour tests marked CURRENT GAP are rewritten when the manifest default starts to work.
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def clean_launch_env(monkeypatch, tmp_path):
    """Start every test with no launch variable and an empty home (no ~/.sparmvet file)."""
    for var in ("SPARMVET_PROFILE", "SPARMVET_PERSONA", "SPARMVET_CONNECTOR"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)


def _deployment(tmp_path, name="dep.yaml", **extra):
    """Write a deployment file whose five locations are real folders under tmp_path."""
    root = tmp_path / name.replace(".yaml", "_data")
    locations = {}
    for key in ("raw_data", "manifests", "curated_data", "user_sessions", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    body = {"deployment_type": "filesystem", "deployment_name": name, "locations": locations}
    body.update(extra)
    path = tmp_path / name
    path.write_text(yaml.safe_dump(body))
    return path, root


def test_profile_variable_selects_the_deployment_file(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_persona": "qa"})
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    b = Bootloader()
    assert b.connector_path == dep
    assert b.deployment_level == 1
    assert b.deployment_name == "dep.yaml"


def test_profile_variable_pointing_nowhere_stops_the_app(tmp_path, monkeypatch):
    monkeypatch.setenv("SPARMVET_PROFILE", str(tmp_path / "missing.yaml"))
    with pytest.raises(SystemExit):
        Bootloader()


def test_user_file_is_used_when_no_variable_is_set(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_persona": "qa"})
    user_dir = tmp_path / "home" / ".sparmvet"
    user_dir.mkdir()
    (user_dir / "profile.yaml").write_text(dep.read_text())
    b = Bootloader()
    assert b.deployment_level == 2
    assert b.connector_path == user_dir / "profile.yaml"


def test_app_features_variable_accepts_a_short_name(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    monkeypatch.setenv("SPARMVET_PERSONA", "qa")
    b = Bootloader()
    assert b.app_features_path.name == "qa_template.yaml"
    assert b.is_enabled("export_enabled") is True
    assert b.is_enabled("test_lab_enabled") is True


def test_app_features_variable_accepts_a_path(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    monkeypatch.setenv("SPARMVET_PERSONA", "config/ui/templates/pipeline-static_template.yaml")
    b = Bootloader()
    assert b.app_features_path.name == "pipeline-static_template.yaml"
    assert b.is_enabled("interactivity_enabled") is False
    assert b.is_enabled("test_lab_enabled") is False


def test_features_differ_between_two_launches_of_the_same_deployment(tmp_path, monkeypatch):
    """The same deployment file with two feature sets: the point of keeping them separate."""
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    monkeypatch.setenv("SPARMVET_PERSONA", "qa")
    full = Bootloader()
    monkeypatch.setenv("SPARMVET_PERSONA", "pipeline-static")
    static = Bootloader()
    assert full.connector_path == static.connector_path
    assert full.is_enabled("gallery_enabled") and not static.is_enabled("gallery_enabled")


def test_variable_beats_the_deployment_default(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_persona": "pipeline-static"})
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    monkeypatch.setenv("SPARMVET_PERSONA", "qa")
    assert Bootloader().app_features_path.name == "qa_template.yaml"


def test_deployment_default_is_used_without_a_variable(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_persona": "pipeline-static"})
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    assert Bootloader().app_features_path.name == "pipeline-static_template.yaml"


def test_no_choice_anywhere_stops_the_app(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()


def test_keyword_beats_the_variable(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    monkeypatch.setenv("SPARMVET_PERSONA", "qa")
    assert Bootloader(app_features="pipeline-static").app_features_path.name == "pipeline-static_template.yaml"


def test_missing_location_folder_stops_the_app(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_persona": "qa"})
    (root / "gallery").rmdir()
    (root / "raw_data").rmdir()
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()


def test_recipes_are_listed_from_the_manifests_folder(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_persona": "qa"})
    (root / "manifests" / "alpha.yaml").write_text("id: alpha\n")
    (root / "manifests" / "beta.yaml").write_text("id: beta\n")
    (root / "manifests" / "notes.txt").write_text("not a manifest\n")
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    assert sorted(Bootloader().available_projects) == ["alpha", "beta"]


def test_CURRENT_GAP_template_fixed_manifest_wins_and_deployment_default_is_ignored(tmp_path, monkeypatch):
    """ADR-091 changes this: the deployment default takes effect and the template key is removed."""
    dep, root = _deployment(tmp_path, **{"default_manifest": "beta", "default_persona": "pipeline-static"})
    (root / "manifests" / "beta.yaml").write_text("id: beta\n")
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    b = Bootloader()
    assert b.default_manifest == "beta"  # read from the deployment file ...
    assert b.get_default_project() == "1_test_data_ST22_dummy"  # ... but the template pin is used


def test_CURRENT_GAP_without_any_pin_the_first_listed_recipe_opens(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_manifest": "beta", "default_persona": "qa"})
    (root / "manifests" / "alpha.yaml").write_text("id: alpha\n")
    (root / "manifests" / "beta.yaml").write_text("id: beta\n")
    monkeypatch.setenv("SPARMVET_PROFILE", str(dep))
    b = Bootloader()
    assert b.get_default_project() == next(iter(b.available_projects))
