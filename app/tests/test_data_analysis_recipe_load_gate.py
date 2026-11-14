"""HOME's automatic load gate (ADR-094): a recipe that fails structure or data-vs-contract
validation is excluded from bootloader.available_data_analysis_recipes, recorded in
bootloader.rejected_data_analysis_recipes with its problems and a resolved contact, and the
app never crashes because of it.
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader
from app.tests.tiny_recipe import tiny_recipe, write_tiny

REPO = Path(__file__).resolve().parents[2]

_BROKEN_RECIPE = "id: {name}\n"  # no analysis_groups: at all — fails structure


@pytest.fixture(autouse=True)
def clean_launch_env(monkeypatch, tmp_path):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE",
                "SPARMVET_CONNECTOR", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)


def _deployment(tmp_path, name="dep.yaml", contact=None, **extra):
    root = tmp_path / name.replace(".yaml", "_data")
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    body = {"deployment_type": "filesystem", "deployment_name": name,
            "default_app_features": "qa", "locations": locations}
    if contact:
        body["branding"] = {"contact": contact}
    body.update(extra)
    path = tmp_path / name
    path.write_text(yaml.safe_dump(body))
    return path, root


def test_a_recipe_that_fails_structure_is_excluded_and_recorded(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path)
    write_tiny(root / "data_analysis_recipes", tiny_recipe("good"))
    (root / "data_analysis_recipes" / "broken.yaml").write_text(_BROKEN_RECIPE.format(name="broken"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert sorted(b.available_data_analysis_recipes) == ["good"]
    assert "broken" in b.rejected_data_analysis_recipes
    assert any("analysis_groups" in p for p in b.rejected_data_analysis_recipes["broken"]["problems"])


def test_a_recipe_that_fails_data_contract_is_excluded_and_recorded(tmp_path, monkeypatch):
    """The recipe is a valid format 1 recipe (the checker accepts it); only its data is wrong: the file is not there."""
    dep, root = _deployment(tmp_path)
    recipe = tiny_recipe("mismatched", data_path="./assets/test_data/tiny/does_not_exist.tsv")
    write_tiny(root / "data_analysis_recipes", recipe)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert "mismatched" not in b.available_data_analysis_recipes
    assert "mismatched" in b.rejected_data_analysis_recipes
    problems = b.rejected_data_analysis_recipes["mismatched"]["problems"]
    assert any("cannot be loaded" in p or "dataset" in p for p in problems)
    assert not any("[" in p[:6] for p in problems)  # no checker code: the form was accepted, the data check refused


def test_a_recipe_in_an_old_form_is_excluded_with_the_code_and_the_fix_of_the_checker(tmp_path, monkeypatch):
    """Recipe format 1 is enforced at the gate: a removed key is refused, and the reason names the replacement."""
    dep, root = _deployment(tmp_path)
    recipe = tiny_recipe("old_form")
    recipe["data_schemas"]["A"]["output_fields"] = {"a": {"type": "categorical"}}
    write_tiny(root / "data_analysis_recipes", recipe)
    write_tiny(root / "data_analysis_recipes", tiny_recipe("good"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert sorted(b.available_data_analysis_recipes) == ["good"]
    problems = b.rejected_data_analysis_recipes["old_form"]["problems"]
    assert any("[S01]" in p and "output_fields" in p and "polars_select" in p for p in problems)


def test_contact_resolution_prefers_the_recipe_own_contact(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, contact="deployment-contact@example.org")
    recipe = (
        "id: broken\n"
        "info:\n  contact: recipe-author@example.org\n"
    )
    (root / "data_analysis_recipes" / "broken.yaml").write_text(recipe)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert b.rejected_data_analysis_recipes["broken"]["contact"] == "recipe-author@example.org"


def test_contact_resolution_falls_back_to_the_deployment_contact(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path, contact="deployment-contact@example.org")
    (root / "data_analysis_recipes" / "broken.yaml").write_text(_BROKEN_RECIPE.format(name="broken"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert b.rejected_data_analysis_recipes["broken"]["contact"] == "deployment-contact@example.org"


def test_contact_resolution_is_none_when_nothing_is_configured(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path)  # no contact
    (root / "data_analysis_recipes" / "broken.yaml").write_text(_BROKEN_RECIPE.format(name="broken"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert b.rejected_data_analysis_recipes["broken"]["contact"] is None


def test_rejected_default_falls_through_to_a_valid_recipe_when_selector_visible(tmp_path, monkeypatch):
    """The operator named a default that exists but fails the gate; selector is visible
    (the default here), so HOME must not crash and must not silently open the broken one."""
    dep, root = _deployment(tmp_path, default_data_analysis_recipe="broken")
    (root / "data_analysis_recipes" / "broken.yaml").write_text(_BROKEN_RECIPE.format(name="broken"))
    write_tiny(root / "data_analysis_recipes", tiny_recipe("good"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()  # must not raise

    assert b.default_data_analysis_recipe_name is None
    assert b.get_default_data_analysis_recipe() == "good"


def test_rejected_default_is_fatal_when_selector_hidden(tmp_path, monkeypatch):
    """No escape hatch for the user in this deployment — a broken named default must still
    stop the app, but the message must name the real cause, not suggest a spelling mistake.

    data_analysis_recipe_selector.visible is an app features field, not a deployment field
    (rules_app_features_flags.md) — pipeline-static is the shipped app features with it off,
    so it is used here instead of qa to get a hidden selector.
    """
    dep, root = _deployment(
        tmp_path, default_data_analysis_recipe="broken",
        default_app_features="pipeline-static",
        contact="team@example.org",
    )
    (root / "data_analysis_recipes" / "broken.yaml").write_text(_BROKEN_RECIPE.format(name="broken"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    with pytest.raises(SystemExit):
        Bootloader()


def test_a_default_naming_a_recipe_that_does_not_exist_is_still_the_old_fatal_path(tmp_path, monkeypatch):
    """Unchanged behaviour: a genuine typo (file absent from disk) is still a 'not found'
    error, distinct from 'found but failed validation'."""
    dep, root = _deployment(tmp_path, default_data_analysis_recipe="nope")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    with pytest.raises(SystemExit):
        Bootloader()


# ---------------------------------------------------------------------------
# issue #38 — zero usable recipes must not crash the Bootloader itself, and
# must expose a non-raising way to ask "is there anything to show".
# ---------------------------------------------------------------------------

def test_zero_recipes_on_disk_bootloader_construction_does_not_raise(tmp_path, monkeypatch):
    """An empty data_analysis_recipes folder — the app's own repro steps for issue #38.
    Bootloader() must not raise; the crash this issue is about only ever happened later,
    at the first unguarded get_default_data_analysis_recipe() call during session setup."""
    dep, _root = _deployment(tmp_path)  # no recipe written, no default named
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()  # must not raise

    assert b.available_data_analysis_recipes == {}
    assert b.rejected_data_analysis_recipes == {}
    assert b.has_usable_data_analysis_recipe is False
    assert b.get_default_data_analysis_recipe_or_none() is None
    with pytest.raises(FileNotFoundError):
        b.get_default_data_analysis_recipe()


def test_all_recipes_rejected_is_also_a_non_raising_empty_state(tmp_path, monkeypatch):
    """Every recipe exists but fails the gate — same non-raising empty state as zero on disk,
    with the rejections still recorded for the sidebar to explain."""
    dep, root = _deployment(tmp_path)
    (root / "data_analysis_recipes" / "broken.yaml").write_text(_BROKEN_RECIPE.format(name="broken"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()  # must not raise

    assert b.available_data_analysis_recipes == {}
    assert "broken" in b.rejected_data_analysis_recipes
    assert b.has_usable_data_analysis_recipe is False
    assert b.get_default_data_analysis_recipe_or_none() is None
    with pytest.raises(FileNotFoundError):
        b.get_default_data_analysis_recipe()


def test_has_usable_data_analysis_recipe_is_true_once_one_passes(tmp_path, monkeypatch):
    dep, root = _deployment(tmp_path)
    write_tiny(root / "data_analysis_recipes", tiny_recipe("good"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))

    b = Bootloader()

    assert b.has_usable_data_analysis_recipe is True
    assert b.get_default_data_analysis_recipe_or_none() == "good"
