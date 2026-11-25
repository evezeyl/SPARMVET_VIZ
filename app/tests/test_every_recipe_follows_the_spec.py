"""One test walks every recipe that ships (pipelines, retest, templates, the folders the deployments name, the
Gallery examples) against the checker. The rules are read from the one place the checker uses; this file holds no copy of them.

What it guarantees: a recipe, fragment or Gallery example added to any recipe folder is checked without anyone editing this
file. Every recipe file (a top-level YAML of a recipe folder, the rule of `find_data_analysis_recipes` and of the bootloader)
gets the recipe check, the full validate and the data check; every folder a deployment names, and the Gallery, gets the set
check (code X5: a plot id is unique over the recipes shipped together). An empty or unreadable YAML file inside a recipe folder
fails. Known exceptions are in ONE table (EXCUSES): an excused check that starts to pass, or an excuse that names a file that is
gone, fails the test, so the table cannot rot.

The Gallery examples' own data is read through the ingestion and compared with the file by
`app/tests/test_gallery_app_path.py` (all examples), so this file does not repeat it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_every_recipe_follows_the_spec.py -q
"""
import shutil
from pathlib import Path

import pytest
import yaml

import transformer.actions  # noqa: F401  (loads the registry the checker reads)
from app.modules.data_analysis_recipe_validator import (checker_catalogs, checker_problems, find_data_analysis_recipes,
                                                         validate_data_analysis_recipe, validate_data_analysis_recipe_data)
from app.modules.gallery_examples import check_gallery
from utils.recipe_check import check_recipe_set
from utils.recipe_loader import check_recipe_file, load_recipe

ROOT = Path(__file__).resolve().parents[2]
RECIPES_ROOT = ROOT / "config" / "data_analysis_recipes"
DEPLOYMENTS = ROOT / "config" / "deployment"
GALLERY = ROOT / "assets" / "gallery_data"
GALLERY_RECIPE = "data_analysis_recipe.yaml"
# The raw data folder of the development deployment: the folder the data check reads for recipes no deployment names.
DEFAULT_RAW = ROOT / yaml.safe_load((DEPLOYMENTS / "local" / "local.yaml").read_text())["locations"]["raw_data"]

CHECKS = ("not_empty", "recipe_check", "validate", "data_check")

# Known exceptions: (file relative to the project, the checks it is excused from, plain reason, what removes the entry).
# SETS holds the same for the set check of a folder. The test fails when an excused check passes and when a file is gone.
EXCUSES = [
    ("config/data_analysis_recipes/retest/retest_bad_select_column.yaml", ("data_check",),
     "exists to show the refusal of a select that names a missing column (the data check must fail)",
     "never: the refusal is tested in app/tests/test_retest_data_analysis_recipes.py"),
    ("config/data_analysis_recipes/retest/retest_broken_header.yaml", ("data_check",),
     "exists to show the refusal of a data file with a broken header (the data check must fail)",
     "never: the refusal is tested in app/tests/test_retest_data_analysis_recipes.py"),
    ("config/data_analysis_recipes/templates/audit.yaml", ("data_check",),
     "template: its data paths are placeholders, the files do not exist", "never: a template ships without data"),
    ("config/data_analysis_recipes/templates/e_coli.yaml", ("data_check",),
     "template: its data paths are placeholders, the files do not exist", "never: a template ships without data"),
    ("config/data_analysis_recipes/templates/simple_template.yaml", ("data_check",),
     "template: its data paths are placeholders, the files do not exist", "never: a template ships without data"),
]
SET_EXCUSES = [
    ("config/data_analysis_recipes/retest", "retest recipes reuse plot ids between them (genes_bar)",
     "task REVIEWS-D0534-TO-REDO (the plot id work of D-0534); the ids are not renamed here"),
]
EXCUSED = {(file, check) for file, checks, _, _ in EXCUSES for check in checks}
SET_EXCUSED = {folder for folder, _, _ in SET_EXCUSES}


def rel(path: Path) -> str:
    return str(Path(path).resolve().relative_to(ROOT))


# -- discovery: nothing here names a recipe, a folder or a rule of the checker ---------------------------------------------

def deployment_recipe_folders(deployments: Path = DEPLOYMENTS):
    """(folders that exist, deployment files whose folder is a documented placeholder).

    The folder is read the way the connector reads it: `locations.data_analysis_recipes`, under `project_root` when the path is
    relative, else under the project. A folder that does not exist is a placeholder when the deployment's `project_root` is one
    (it contains PLACEHOLDER or starts with PATH_TO, as the two template deployments write it); any other missing folder is
    returned in `missing` and fails the test."""
    found, placeholders, missing = [], [], []
    for deployment in sorted(deployments.rglob("*.yaml")):
        data = yaml.safe_load(deployment.read_text()) or {}
        name = (data.get("locations") or {}).get("data_analysis_recipes")
        if not name:
            continue
        project_root = data.get("project_root")
        folder = Path(name)
        if not folder.is_absolute():
            folder = (Path(project_root) if project_root else ROOT) / folder
        if folder.is_dir():
            found.append((deployment, folder.resolve()))
        elif project_root and ("PLACEHOLDER" in str(project_root) or str(project_root).startswith("PATH_TO")):
            placeholders.append(deployment)
        else:
            missing.append((deployment, folder))
    return found, placeholders, missing


def recipe_folders(recipes_root: Path = RECIPES_ROOT, deployments: Path = DEPLOYMENTS):
    """Every folder that holds recipes: each folder directly in the recipes folder (the folder itself when it holds recipes), and each folder a deployment names."""
    folders = {d.resolve() for d in recipes_root.iterdir() if d.is_dir()}
    if find_data_analysis_recipes(recipes_root):
        folders.add(recipes_root.resolve())
    folders |= {folder for _, folder in deployment_recipe_folders(deployments)[0]}
    return sorted(folders)


def fragment_files(folder: Path):
    """The YAML files below a recipe folder's own level (the included fragments); the recipes are the ones directly in it."""
    top = set(find_data_analysis_recipes(folder))
    return sorted(p for p in Path(folder).rglob("*.yaml") if p not in top)


def discovery_problems(folder: Path):
    """Plain messages for a YAML file of a recipe folder that cannot be a recipe or a fragment: empty, not YAML, no mapping or list."""
    messages = []
    for path in list(find_data_analysis_recipes(folder)) + fragment_files(folder):
        raw, problems = load_recipe(path)
        if path.stat().st_size == 0 or not path.read_text().strip():
            messages.append(f"{rel(path) if ROOT in path.resolve().parents else path} is empty: it is neither a recipe nor an included fragment")
        elif raw is None or problems:
            messages.append(f"{path.name} cannot be read: " + "; ".join(p.text(path.name) for p in problems) if problems
                            else f"{path.name} holds nothing")
        elif not isinstance(raw, (dict, list)):
            messages.append(f"{path.name} is neither a recipe nor an included fragment")
    return messages


def set_check_problems(files):
    """The set check (X5) over the recipes at `files`; plain messages."""
    recipes = {}
    for path in files:
        raw, _ = load_recipe(path)
        if isinstance(raw, dict):
            recipes[Path(path).stem] = raw
    return [p.text("recipes") for p in check_recipe_set(recipes)]


def run_check(check: str, path: Path):
    """The errors of one check of one recipe file, as plain messages (an empty list: it passes)."""
    path = Path(path)
    if check == "not_empty":
        raw, problems = load_recipe(path) if path.stat().st_size else (None, [])
        return [] if raw else [f"{path.name} is empty or holds no recipe"]
    if check == "recipe_check":
        return [str(p) for p in checker_problems(path, "run")]
    if check == "validate":
        return [str(p) for p in validate_data_analysis_recipe(path)]
    if check == "data_check":
        return [str(p) for p in validate_data_analysis_recipe_data(path, DEFAULT_RAW)]
    raise ValueError(check)


def excuse_verdict(errors, excused: bool):
    """None when the result is as expected; else the plain message. An excused check that passes is itself a failure."""
    if excused and not errors:
        return "this check now passes: remove its entry from the table of known exceptions"
    if not excused and errors:
        return "\n".join(errors)
    return None


FOLDERS = recipe_folders()
RECIPE_FILES = [p for folder in FOLDERS for p in find_data_analysis_recipes(folder)]
CASES = [(p, check) for p in RECIPE_FILES for check in CHECKS]
GALLERY_RECIPES = sorted(GALLERY.glob(f"*/{GALLERY_RECIPE}"))


def _case_id(case):
    path, check = case
    return f"{path.parent.name}/{path.stem}::{check}"


# -- the walk ----------------------------------------------------------------------------------------------------------------

def test_discovery_finds_something_everywhere_it_must():
    found, placeholders, missing = deployment_recipe_folders()
    assert found, "no deployment names an existing recipe folder"
    assert missing == [], "a deployment names a recipe folder that does not exist (and it is no documented placeholder): " + str(missing)
    for deployment, folder in found:
        assert find_data_analysis_recipes(folder), f"{rel(deployment)} names {folder}, which holds no recipe"
    assert RECIPE_FILES and GALLERY_RECIPES
    assert placeholders, "the template deployments are expected to be listed as placeholders"


@pytest.mark.parametrize("folder", FOLDERS, ids=lambda f: rel(f))
def test_no_yaml_file_of_a_recipe_folder_is_empty_or_unreadable(folder):
    messages = discovery_problems(folder)
    excused = tuple(file for file, checks, _, _ in EXCUSES if "not_empty" in checks)
    assert [m for m in messages if not m.startswith(excused)] == []


@pytest.mark.parametrize("case", CASES, ids=_case_id)
def test_the_recipe_follows_the_spec(case):
    path, check = case
    verdict = excuse_verdict(run_check(check, path), (rel(path), check) in EXCUSED)
    assert verdict is None, f"{rel(path)}: {check}: {verdict}"


@pytest.mark.parametrize("folder", [f for _, f in deployment_recipe_folders()[0]], ids=lambda f: rel(f))
def test_a_plot_id_is_unique_over_the_recipes_of_a_deployment_folder(folder):
    errors = set_check_problems(find_data_analysis_recipes(folder))
    verdict = excuse_verdict(errors, rel(folder) in SET_EXCUSED)
    assert verdict is None, f"{rel(folder)}: {verdict}"


def test_gallery_examples_pass_the_recipe_check_and_the_set_check():
    shipped = check_gallery(GALLERY)
    assert shipped.rejected == {}
    assert len(shipped.accepted) == len(GALLERY_RECIPES) >= 30
    assert set_check_problems(GALLERY_RECIPES) == []


@pytest.mark.parametrize("path", GALLERY_RECIPES, ids=lambda p: p.parent.name)
def test_each_gallery_example_has_no_error_in_the_gallery_profile(path):
    # the stem of a Gallery recipe is its folder's name, as `GalleryManager.check_examples` gives it
    result = check_recipe_file(path, "gallery", file_stem=path.parent.name, catalogs=checker_catalogs())
    assert {"structure", "actions", "components"} <= result.coverage
    assert [p.text(path.parent.name) for p in result.errors] == []


def test_the_table_of_known_exceptions_names_only_files_that_exist():
    for file, _, reason, removed_by in EXCUSES:
        assert (ROOT / file).is_file(), f"{file} is in the table of known exceptions and no longer exists: remove the entry"
        assert reason and removed_by
    for folder, reason, removed_by in SET_EXCUSES:
        assert (ROOT / folder).is_dir(), f"{folder} is in the table of known exceptions and no longer exists: remove the entry"
        assert reason and removed_by
    assert {rel(p) for p in RECIPE_FILES} >= {file for file, _, _, _ in EXCUSES}


def test_beeswarm_sina_is_accepted_and_listed():
    import json
    index = json.loads((GALLERY / "gallery_index.json").read_text())
    assert "beeswarm_sina" in check_gallery(GALLERY).accepted and "beeswarm_sina" in index["registry"]
    assert len(index["registry"]) == len(GALLERY_RECIPES)


# -- the test can fail: each guard is shown on copies, with the SAME functions the walk uses -------------------------------

def _copy_pipelines(tmp_path: Path) -> Path:
    work = tmp_path / "pipelines"
    shutil.copytree(ROOT / "config/data_analysis_recipes/pipelines", work)
    return work


def test_a_recipe_with_a_required_key_removed_is_reported(tmp_path):
    target = _copy_pipelines(tmp_path) / "3_test_no_joins.yaml"
    assert run_check("recipe_check", target) == []
    lines = target.read_text().split("\n")
    first = next(i for i, line in enumerate(lines) if line.startswith("    ui_label:"))
    target.write_text("\n".join(lines[:first] + lines[first + 1:]))
    assert excuse_verdict(run_check("recipe_check", target), False) is not None


def test_two_recipes_with_the_same_plot_id_are_reported_by_the_set_check(tmp_path):
    work = _copy_pipelines(tmp_path)
    assert set_check_problems([work / "3_test_no_joins.yaml"]) == []
    shutil.copy(work / "3_test_no_joins.yaml", work / "3_copy.yaml")
    problems = set_check_problems([work / "3_test_no_joins.yaml", work / "3_copy.yaml"])
    assert problems and all("plot id" in p for p in problems)


def test_an_empty_yaml_file_in_a_recipe_folder_is_reported(tmp_path):
    folder = tmp_path / "newfolder"
    (folder / "sub").mkdir(parents=True)
    assert discovery_problems(folder) == []
    (folder / "leftover.yaml").write_text("")
    (folder / "sub" / "fragment.yaml").write_text("   \n")
    messages = discovery_problems(folder)
    assert len(messages) == 2 and all("empty" in m for m in messages)
    assert run_check("not_empty", folder / "leftover.yaml") != []


def test_an_excused_check_that_passes_makes_the_guard_fail(tmp_path):
    target = _copy_pipelines(tmp_path) / "3_test_no_joins.yaml"
    assert run_check("recipe_check", target) == []
    assert "now passes" in excuse_verdict(run_check("recipe_check", target), True)
    assert excuse_verdict(["an error"], True) is None
