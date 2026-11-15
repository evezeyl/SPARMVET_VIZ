"""GATE-GAP-1: HOME's load gate (ADR-094) runs again for a recipe whose files changed during the session.

Before: the gate ran once in Bootloader.__init__. A recipe saved from Blueprint (a step, a branch, the info block) and
now failing its checks stayed in `available_data_analysis_recipes` until a restart, so HOME kept offering and running it.
Decided (Eve, 2026-11-15): a recipe must pass all checks at validation before HOME can use it; Blueprint is where a
failing recipe is opened and fixed (its save is never blocked).
"""
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader
from app.tests.tiny_recipe import tiny_recipe, write_tiny

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def clean_launch_env(monkeypatch, tmp_path):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE",
                "SPARMVET_CONNECTOR", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)


def _deployment(tmp_path, contact=None):
    root = tmp_path / "dep_data"
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    body = {"deployment_type": "filesystem", "deployment_name": "dep",
            "default_app_features": "qa", "locations": locations}
    if contact:
        body["branding"] = {"contact": contact}
    path = tmp_path / "dep.yaml"
    path.write_text(yaml.safe_dump(body))
    return path, root / "data_analysis_recipes"


def _write_with_fragment(folder: Path, name: str, shared_dir: Path | None = None) -> Path:
    """A recipe whose plot spec is an included fragment (`<name>/spec_p.yaml`, or a shared file outside the mirrored folder)."""
    recipe = tiny_recipe(name)
    spec = recipe["analysis_groups"]["g"]["plots"]["p"]["spec"]
    recipe["analysis_groups"]["g"]["plots"]["p"]["spec"] = "__INC__"
    if shared_dir is None:
        fragment = folder / name / "spec_p.yaml"
        include = f"{name}/spec_p.yaml"
    else:
        fragment = shared_dir / "spec_shared.yaml"
        include = "../shared/spec_shared.yaml"
    fragment.parent.mkdir(parents=True, exist_ok=True)
    fragment.write_text(yaml.safe_dump(spec, sort_keys=False))
    text = yaml.safe_dump(recipe, sort_keys=False).replace("__INC__", f"!include '{include}'")
    (folder / f"{name}.yaml").write_text(text)
    return fragment


def _break(fragment: Path):
    spec = yaml.safe_load(fragment.read_text())
    spec["layers"] = [{"name": "geom_does_not_exist", "params": {}}]
    fragment.write_text(yaml.safe_dump(spec, sort_keys=False))


def _repair(fragment: Path):
    spec = yaml.safe_load(fragment.read_text())
    spec["layers"] = [{"name": "geom_bar", "params": {}}]
    fragment.write_text(yaml.safe_dump(spec, sort_keys=False))


def _boot(tmp_path, monkeypatch, contact=None):
    dep, folder = _deployment(tmp_path, contact)
    return dep, folder


def test_a_step_saved_after_start_that_now_fails_removes_the_recipe_from_HOME(tmp_path, monkeypatch):
    dep, folder = _boot(tmp_path, monkeypatch, contact="lab@example.org")
    fragment = _write_with_fragment(folder, "good")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert "good" in b.available_data_analysis_recipes and not b.rejected_data_analysis_recipes

    _break(fragment)  # what Blueprint's component save writes, with no check

    changed = b.recheck_changed_data_analysis_recipes()

    assert changed == ["good"]
    assert "good" not in b.available_data_analysis_recipes
    record = b.rejected_data_analysis_recipes["good"]
    assert any("geom_does_not_exist" in p or "layer" in p.lower() for p in record["problems"]), record["problems"]
    assert record["contact"] == "lab@example.org"


def test_a_repaired_recipe_comes_back(tmp_path, monkeypatch):
    dep, folder = _boot(tmp_path, monkeypatch)
    fragment = _write_with_fragment(folder, "good")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    _break(fragment)
    b.recheck_changed_data_analysis_recipes()
    assert "good" in b.rejected_data_analysis_recipes

    _repair(fragment)
    changed = b.recheck_changed_data_analysis_recipes()

    assert changed == ["good"]
    assert "good" in b.available_data_analysis_recipes
    assert "good" not in b.rejected_data_analysis_recipes


def test_a_recipe_rejected_at_start_and_repaired_later_comes_back(tmp_path, monkeypatch):
    dep, folder = _boot(tmp_path, monkeypatch)
    fragment = _write_with_fragment(folder, "late")
    _break(fragment)
    write_tiny(folder, tiny_recipe("other"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert "late" in b.rejected_data_analysis_recipes and "late" not in b.available_data_analysis_recipes

    _repair(fragment)
    b.recheck_changed_data_analysis_recipes()

    assert sorted(b.available_data_analysis_recipes) == ["late", "other"]
    assert b.rejected_data_analysis_recipes == {}


def test_nothing_changed_runs_no_check_and_keeps_the_version(tmp_path, monkeypatch):
    dep, folder = _boot(tmp_path, monkeypatch)
    _write_with_fragment(folder, "good")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    calls = []
    import app.src.bootloader as module
    real = module.validate_data_analysis_recipe
    monkeypatch.setattr(module, "validate_data_analysis_recipe", lambda *a, **k: calls.append(a) or real(*a, **k))
    version = b.data_analysis_recipe_gate_version

    assert b.recheck_changed_data_analysis_recipes() == []

    assert calls == [] and b.data_analysis_recipe_gate_version == version


def test_one_changed_recipe_is_checked_alone_and_the_other_stays_available(tmp_path, monkeypatch):
    dep, folder = _boot(tmp_path, monkeypatch)
    broken = _write_with_fragment(folder, "one")
    _write_with_fragment(folder, "two")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    version = b.data_analysis_recipe_gate_version

    _break(broken)
    assert b.recheck_changed_data_analysis_recipes() == ["one"]

    assert sorted(b.available_data_analysis_recipes) == ["two"]
    assert list(b.rejected_data_analysis_recipes) == ["one"]
    assert b.data_analysis_recipe_gate_version > version


def test_a_fragment_shared_outside_the_mirrored_folder_is_watched(tmp_path, monkeypatch):
    """Two recipes include one file that is not under `<name>/`: breaking it rejects both."""
    dep, folder = _boot(tmp_path, monkeypatch)
    (tmp_path / "pyproject.toml").write_text("")  # an include may reach anything inside the project, nothing outside it (T11)
    shared = folder.parent / "shared"
    fragment = _write_with_fragment(folder, "a", shared_dir=shared)
    _write_with_fragment(folder, "b", shared_dir=shared)
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    assert sorted(b.available_data_analysis_recipes) == ["a", "b"], b.rejected_data_analysis_recipes

    _break(fragment)

    assert sorted(b.recheck_changed_data_analysis_recipes()) == ["a", "b"]
    assert b.available_data_analysis_recipes == {}


def test_a_recipe_file_deleted_after_start_leaves_the_list(tmp_path, monkeypatch):
    dep, folder = _boot(tmp_path, monkeypatch)
    _write_with_fragment(folder, "gone")
    write_tiny(folder, tiny_recipe("stays"))
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()

    (folder / "gone.yaml").unlink()
    b.recheck_changed_data_analysis_recipes()

    assert "gone" not in b.available_data_analysis_recipes
    assert "stays" in b.available_data_analysis_recipes


def test_the_dictionaries_are_replaced_not_changed_in_place(tmp_path, monkeypatch):
    """Another session may be iterating over the list while a save re-checks it: never change a dictionary in place."""
    dep, folder = _boot(tmp_path, monkeypatch)
    fragment = _write_with_fragment(folder, "good")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    b = Bootloader()
    before = b.available_data_analysis_recipes

    _break(fragment)
    b.recheck_changed_data_analysis_recipes()

    assert "good" in before  # the object another session holds is untouched
    assert b.available_data_analysis_recipes is not before


def test_the_text_HOME_shows_for_a_rejected_recipe_names_it_the_reason_and_the_contact():
    from app.modules.data_analysis_recipe_validator import rejected_recipe_text
    text = rejected_recipe_text("sample_run", {"problems": ["[PS02] target_dataset X is not a schema", "b", "c", "d"],
                                               "contact": "lab@example.org"})
    assert "sample_run" in text and "[PS02]" in text and "lab@example.org" in text
    assert "and 1 more" in text  # at most three problems are listed
    assert "does not use" in text.lower()
    none_contact = rejected_recipe_text("r", {"problems": ["p"], "contact": None})
    assert "not configured" in none_contact
