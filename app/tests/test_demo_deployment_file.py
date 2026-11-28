"""The deployment file of the December 2026 demo (202612_demo_deployment.yaml) is valid and starts the app.

It names no default recipe and no default data (the recipe is chosen and the data uploaded during the demo), its user place is
the simulated user directory USER_DIRECTORY (git-ignored, so not in a fresh clone), and its recipe folder is the shipped one (the owner moves her recipe there).
The file itself is never started from the repository: a copy whose user places point at a temporary folder is, so that the test
passes on a fresh clone and never reads or writes USER_DIRECTORY.
"""
from pathlib import Path

import pytest
import yaml

from app.modules.renamed_keys import (REMOVED_DEPLOYMENT_KEYS, RENAMED_BANNER_KEYS, RENAMED_DEPLOYMENT_KEYS,
                                      RENAMED_LOCATION_KEYS)
from app.src.bootloader import Bootloader

REPO = Path(__file__).resolve().parents[2]
DEMO = REPO / "config" / "deployment" / "demo" / "202612_demo_deployment.yaml"
LOCATIONS = {"raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"}


@pytest.fixture(autouse=True)
def start_from_repo(monkeypatch):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.chdir(REPO)


def _config(path=DEMO):
    return yaml.safe_load(path.read_text())


def _known_top_level_keys():
    keys = set()
    for path in (REPO / "config" / "deployment").glob("*/*.yaml"):
        if path != DEMO:
            keys |= set(yaml.safe_load(path.read_text()) or {})
    return keys


def _copy_with_temp_places(tmp_path, text=None):
    """A copy of the demo file whose user directory and cache are in tmp_path (nothing of the repository's USER_DIRECTORY is touched)."""
    user = tmp_path / "user"
    user.mkdir(exist_ok=True)
    text = DEMO.read_text() if text is None else text
    text = text.replace('"USER_DIRECTORY/"', f'"{user}/"').replace('"tmp/DEMO_202612/cache/"', f'"{tmp_path / "cache"}/"')
    copy = tmp_path / "demo.yaml"
    copy.write_text(text)
    return copy, user


def test_the_file_is_where_the_demo_deployments_are_and_has_the_required_keys():
    data = _config()
    assert set(data["locations"]) == LOCATIONS
    assert data["deployment_type"] == "filesystem"
    assert data["locations"]["user_data"] == "USER_DIRECTORY/"
    assert not Path(data["locations"]["user_data"]).is_absolute()


def test_it_has_no_retired_key_and_no_unknown_key():
    data = _config()
    retired = set(RENAMED_DEPLOYMENT_KEYS) | set(REMOVED_DEPLOYMENT_KEYS)
    assert not (retired & set(data))
    assert not (set(RENAMED_LOCATION_KEYS) & set(data["locations"]))
    assert not (set(RENAMED_BANNER_KEYS) & set((data.get("branding") or {}).get("banner") or {}))
    assert set(data) <= _known_top_level_keys(), sorted(set(data) - _known_top_level_keys())


def test_it_names_no_default_recipe_and_its_app_features_exist():
    data = _config()
    assert "default_data_analysis_recipe" not in data
    assert (REPO / "config" / "app_features" / f"{data['default_app_features']}.yaml").exists()


def test_its_recipe_folder_is_the_shipped_one():
    folder = REPO / _config()["locations"]["data_analysis_recipes"]
    assert folder.is_dir()
    assert folder == REPO / "config" / "data_analysis_recipes" / "pipelines"  # every recipe there is checked by test_every_recipe_follows_the_spec.py


def test_it_starts_with_no_default_recipe_and_opens_the_first_that_passes_the_gate(tmp_path, monkeypatch):
    copy, user = _copy_with_temp_places(tmp_path)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(copy))
    b = Bootloader()
    assert b.app_features == "developer"
    assert b.get_location("user_data") == user
    assert b.available_data_analysis_recipes
    assert b.get_default_data_analysis_recipe_or_none() == list(b.available_data_analysis_recipes)[0]


def test_a_recipe_without_its_data_is_rejected_at_start_with_this_file(tmp_path, monkeypatch):
    """KNOWN LIMIT, not a wish: until the checks are split, a recipe whose data is not there never reaches the selector."""
    recipes = tmp_path / "recipes"
    recipes.mkdir()
    source = REPO / "config" / "data_analysis_recipes" / "pipelines"
    for item in source.glob("1_test_data_ST22_dummy*"):
        if item.is_dir():
            import shutil
            shutil.copytree(item, recipes / item.name)
        else:
            (recipes / item.name).write_text(item.read_text().replace("assets/test_data", "NO_SUCH_PLACE/data"))
    for item in recipes.rglob("*.yaml"):
        item.write_text(item.read_text().replace("assets/test_data", "NO_SUCH_PLACE/data"))
    text = DEMO.read_text().replace('"config/data_analysis_recipes/pipelines/"', f'"{recipes}/"')
    copy, _ = _copy_with_temp_places(tmp_path, text)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(copy))
    b = Bootloader()
    assert b.available_data_analysis_recipes == {}
    problems = b.rejected_data_analysis_recipes["1_test_data_ST22_dummy"]["problems"]
    assert any("dataset cannot be loaded" in p for p in problems)


def test_a_retired_key_in_a_copy_is_refused(tmp_path, monkeypatch):
    """The test can fail: the same file with a retired key does not start."""
    copy, _ = _copy_with_temp_places(tmp_path, DEMO.read_text() + '\ndeployment_name: "old"\n')
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(copy))
    with pytest.raises(SystemExit):
        Bootloader()
    assert "deployment_name" in (set(REMOVED_DEPLOYMENT_KEYS) | set(RENAMED_DEPLOYMENT_KEYS))


def test_its_branding_is_the_default_one(tmp_path, monkeypatch):
    """It sets no branding: the default stylesheet and no banner, no contact (checked on the copy that starts)."""
    copy, _ = _copy_with_temp_places(tmp_path)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(copy))
    b = Bootloader()
    assert "branding" not in _config()
    assert b.get_ui_banner() is None and b.get_contact() is None
    assert b.show_recipe_name() is True
