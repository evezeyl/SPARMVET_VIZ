"""Characterization of how the app is launched: which file each launch variable selects.

Written against the names in use on 2026-11-07 (SPARMVET_PROFILE, SPARMVET_APP_FEATURES,
default_app_features, fixed_manifest, default_manifest). The configuration rename of ADR-091
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
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE", "SPARMVET_CONNECTOR",
                "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)


def _deployment(tmp_path, name="dep.yaml", recipe=None, **extra):
    """Write a deployment file whose five locations are real folders under tmp_path."""
    root = tmp_path / name.replace(".yaml", "_data")
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    body = {"deployment_type": "filesystem", "deployment_name": name, "locations": locations}
    if recipe:  # a recipe that exists in the recipes folder and is the deployment default
        (root / "data_analysis_recipes" / f"{recipe}.yaml").write_text(f"id: {recipe}\n")
        body["default_data_analysis_recipe"] = recipe
    body.update(extra)
    path = tmp_path / name
    path.write_text(yaml.safe_dump(body))
    return path, root


def test_deployment_variable_selects_the_deployment_file(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert b.deployment_path == dep
    assert b.deployment_level == 1
    assert b.deployment_name == "dep.yaml"


def test_deployment_variable_pointing_nowhere_stops_the_app(tmp_path, monkeypatch):
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(tmp_path / "missing.yaml"))
    with pytest.raises(SystemExit):
        Bootloader()


def test_user_file_is_used_when_no_variable_is_set(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    user_dir = tmp_path / "home" / ".sparmvet"
    user_dir.mkdir()
    (user_dir / "deployment.yaml").write_text(dep.read_text())
    b = Bootloader()
    assert b.deployment_level == 2
    assert b.deployment_path == user_dir / "deployment.yaml"


def test_app_features_variable_accepts_a_short_name(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "qa")
    b = Bootloader()
    assert b.app_features_path.name == "qa.yaml"
    assert b.is_enabled("export_enabled") is True
    assert b.is_enabled("test_lab_enabled") is True


def test_app_features_variable_accepts_a_path(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, recipe="alpha")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "config/app_features/pipeline-static.yaml")
    b = Bootloader()
    assert b.app_features_path.name == "pipeline-static.yaml"
    assert b.is_enabled("interactivity_enabled") is False
    assert b.is_enabled("test_lab_enabled") is False


def test_features_differ_between_two_launches_of_the_same_deployment(tmp_path, monkeypatch):
    """The same deployment file with two feature sets: the point of keeping them separate."""
    dep, _ = _deployment(tmp_path, recipe="alpha")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "qa")
    full = Bootloader()
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "pipeline-static")
    static = Bootloader()
    assert full.deployment_path == static.deployment_path
    assert full.is_enabled("gallery_enabled") and not static.is_enabled("gallery_enabled")


def test_variable_beats_the_deployment_default(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "pipeline-static"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "qa")
    assert Bootloader().app_features_path.name == "qa.yaml"


def test_deployment_default_is_used_without_a_variable(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, recipe="alpha", **{"default_app_features": "pipeline-static"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    assert Bootloader().app_features_path.name == "pipeline-static.yaml"


def test_no_choice_anywhere_stops_the_app(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()


def test_keyword_beats_the_variable(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, recipe="alpha")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "qa")
    assert Bootloader(app_features="pipeline-static").app_features_path.name == "pipeline-static.yaml"


def test_missing_location_folder_stops_the_app(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_app_features": "qa"})
    (root / "gallery").rmdir()
    (root / "raw_data").rmdir()
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()


def test_recipes_are_listed_from_the_data_analysis_recipes_folder(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_app_features": "qa"})
    (root / "data_analysis_recipes" / "alpha.yaml").write_text("id: alpha\n")
    (root / "data_analysis_recipes" / "beta.yaml").write_text("id: beta\n")
    (root / "data_analysis_recipes" / "notes.txt").write_text("not a manifest\n")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    assert sorted(Bootloader().available_data_analysis_recipes) == ["alpha", "beta"]


def test_deployment_default_recipe_opens_first(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, recipe="beta", **{"default_app_features": "qa"})
    (root / "data_analysis_recipes" / "alpha.yaml").write_text("id: alpha\n")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    assert Bootloader().get_default_data_analysis_recipe() == "beta"


def test_launch_variable_beats_the_deployment_default_recipe(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, recipe="beta", **{"default_app_features": "qa"})
    (root / "data_analysis_recipes" / "alpha.yaml").write_text("id: alpha\n")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_DATA_ANALYSIS_RECIPE", "alpha")
    assert Bootloader().get_default_data_analysis_recipe() == "alpha"


def test_a_named_recipe_that_does_not_exist_stops_the_app(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, recipe="beta", **{"default_app_features": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_DATA_ANALYSIS_RECIPE", "nope")
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert "nope" in err and "SPARMVET_DATA_ANALYSIS_RECIPE" in err


def test_hidden_selector_without_a_named_recipe_stops_the_app(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "pipeline-static"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert "default_data_analysis_recipe" in err and "SPARMVET_DATA_ANALYSIS_RECIPE" in err


def test_visible_selector_without_a_named_recipe_opens_the_first_one(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_app_features": "qa"})
    (root / "data_analysis_recipes" / "alpha.yaml").write_text("id: alpha\n")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert b.get_default_data_analysis_recipe() == "alpha"


def test_a_preset_naming_a_recipe_stops_the_app(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path)
    body = yaml.safe_load((REPO / "config" / "app_features" / "qa.yaml").read_text().replace("!include ", ""))
    body = {k: v for k, v in body.items() if k != "workspaces"}
    body["data_analysis_recipe_selector"] = {"visible": False, "fixed_data_analysis_recipe": "x"}
    f = tmp_path / "fixed.yaml"
    f.write_text(yaml.safe_dump(body))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", str(f))
    with pytest.raises(SystemExit):
        Bootloader()
    assert "default_data_analysis_recipe" in capsys.readouterr().err


def test_home_and_variables_are_expanded_in_deployment_paths(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, **{"default_app_features": "qa"})
    body = yaml.safe_load(dep.read_text())
    monkeypatch.setenv("MY_DATA", str(root))
    body["locations"]["cache"] = "${MY_DATA}/cache"
    dep.write_text(yaml.safe_dump(body))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    assert str(Bootloader().get_location("cache")) == str(root / "cache")


def test_an_unset_variable_in_a_path_stops_the_app(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    body = yaml.safe_load(dep.read_text())
    body["locations"]["cache"] = "${NOT_SET_ANYWHERE}/cache"
    dep.write_text(yaml.safe_dump(body))
    monkeypatch.delenv("NOT_SET_ANYWHERE", raising=False)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    assert "NOT_SET_ANYWHERE" in capsys.readouterr().err


def test_branding_comes_from_the_deployment(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa",
                                      "branding": {"theme_css": "assets/demo/web_demo.css",
                                                   "banner": {"title": "Hello"}}})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert b.get_theme_css_path().name == "web_demo.css"
    assert b.get_ui_banner() == {"title": "Hello"}


def test_default_branding_is_the_base_stylesheet_and_no_banner(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert str(b.get_theme_css_path()) == "config/ui/theme.css" and b.get_ui_banner() is None


# --- old names stop the app with a message that names the new one (ADR-091) ---

@pytest.mark.parametrize("old, new", [("SPARMVET_PERSONA", "SPARMVET_APP_FEATURES"),
                                      ("SPARMVET_PROFILE", "SPARMVET_DEPLOYMENT")])
def test_old_launch_variable_stops_the_app_and_names_the_new_one(tmp_path, monkeypatch, capsys, old, new):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv(old, "qa")
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert old in err and new in err


def test_old_app_features_name_stops_the_app_and_names_the_new_one(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "project-independent"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert "project-independent" in err and "standalone" in err


def test_removed_connector_variable_stops_the_app_and_says_it_was_removed(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_CONNECTOR", "local")
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert "SPARMVET_CONNECTOR" in err and "removed" in err


def test_old_deployment_key_stops_the_app_and_names_the_new_one(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, **{"default_persona": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert "default_persona" in err and "default_app_features" in err


@pytest.mark.parametrize("old, new", [("persona_id", "name"), ("features", "flags"),
                                      ("manifest_selector", "data_analysis_recipe_selector")])
def test_old_app_features_key_stops_the_app_and_names_the_new_one(tmp_path, monkeypatch, capsys, old, new):
    dep, _ = _deployment(tmp_path)
    source = yaml.safe_load((REPO / "config" / "app_features" / "qa.yaml").read_text().replace("!include ", ""))
    body = {k: v for k, v in source.items() if k not in ("workspaces",)}
    body[old] = body.pop(new)
    old_file = tmp_path / "old_keys.yaml"
    old_file.write_text(yaml.safe_dump(body))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", str(old_file))
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert f"'{old}'" in err and f"'{new}'" in err


@pytest.mark.parametrize("old, new", [("curated_data", "cache"), ("user_sessions", "user_data"),
                                      ("manifests", "data_analysis_recipes")])
def test_old_location_key_stops_the_app_and_names_the_new_one(tmp_path, monkeypatch, capsys, old, new):
    dep, root = _deployment(tmp_path, **{"default_app_features": "qa"})
    body = yaml.safe_load(dep.read_text())
    body["locations"][old] = body["locations"].pop(new)
    dep.write_text(yaml.safe_dump(body))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    err = capsys.readouterr().err
    assert f"'{old}'" in err and f"'{new}'" in err


@pytest.mark.parametrize("old", ["prefer_discovery", "data_ingestion_enabled", "default_manifest"])
def test_old_deployment_switch_stops_the_app(tmp_path, monkeypatch, capsys, old):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa", old: True})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    assert old in capsys.readouterr().err


def test_unknown_data_lookup_stops_the_app(tmp_path, monkeypatch, capsys):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa", "data_lookup": "everywhere"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    with pytest.raises(SystemExit):
        Bootloader()
    assert "data_lookup" in capsys.readouterr().err


def test_operator_lock_overrides_an_app_features_flag(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa",
                                      "app_features_override": {"data_ingestion_enabled": False}})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert b.is_enabled("data_ingestion_enabled") is False
    assert b.is_enabled("export_enabled") is True  # other flags untouched


def test_data_lookup_defaults_to_data_analysis_recipe_paths(tmp_path, monkeypatch):
    dep, _ = _deployment(tmp_path, **{"default_app_features": "qa"})
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    assert Bootloader().data_lookup == "data_analysis_recipe_paths"
