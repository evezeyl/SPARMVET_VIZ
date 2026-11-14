"""Contract test for data analysis recipes: every data analysis recipe in the active deployment's data analysis recipes location
must have step lists in a shape the engine accepts (issue evezeyl/SPARMVET_VIZ#8).

The data analysis recipes folder is read from the deployment (Location 2) through the bootloader, so
a new data analysis recipe added there is tested without changing this file.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_analysis_recipe_validator.py -q
"""
from pathlib import Path

import pytest

from app.modules.data_analysis_recipe_validator import find_data_analysis_recipes, validate_data_analysis_recipe
from app.src.bootloader import Bootloader
from app.tests.tiny_recipe import tiny_recipe, write_tiny

DATA_ANALYSIS_RECIPE_DIR = Bootloader().get_location("data_analysis_recipes")
DATA_ANALYSIS_RECIPES = find_data_analysis_recipes(DATA_ANALYSIS_RECIPE_DIR)


def test_data_analysis_recipes_are_found():
    assert DATA_ANALYSIS_RECIPES, f"no data analysis recipes found in {DATA_ANALYSIS_RECIPE_DIR}: the discovery would silently test nothing"


@pytest.mark.parametrize("path", DATA_ANALYSIS_RECIPES, ids=lambda p: p.name)
def test_data_analysis_recipe_has_no_step_problems(path):
    problems = validate_data_analysis_recipe(path)
    assert problems == [], "\n".join(str(p) for p in problems)


# --- the validator itself, on small data analysis recipes written for the test ------------------------
# Since 2026-11-14 the first half of the validation is the strict checker of recipe format 1 (`check_recipe`, with the
# action and plot component registries); a recipe it refuses is not handed to the engine. Each problem carries the
# permanent code of the check, the place in the recipe and the fix.

JOIN = {"label": "J", "ingredients": [{"dataset_id": "A"}], "steps": {"tier1": []}}
SORT = {"action": "polars_sort", "by": ["a"], "maintain_order": True}


def _problems(tmp_path, change, name=None):
    recipe = tiny_recipe()
    change(recipe)
    return validate_data_analysis_recipe(write_tiny(tmp_path, recipe, name))


def test_tiny_recipe_is_valid(tmp_path):
    assert validate_data_analysis_recipe(write_tiny(tmp_path)) == []


def test_tiered_steps_are_valid(tmp_path):
    assert _problems(tmp_path, lambda r: r.update(joins={"J": dict(JOIN, steps={"tier1": [SORT], "tier2": []})})) == []


def test_flat_join_steps_are_reported_once_with_the_place_the_code_and_the_fix(tmp_path):
    problems = _problems(tmp_path, lambda r: r.update(joins={"J": dict(JOIN, steps=[SORT])}))
    assert len(problems) == 1
    assert problems[0].location == "joins.J.steps" and "[J07]" in problems[0].problem and "tier1" in problems[0].tip
    assert problems[0].data_analysis_recipe == "m.yaml"


def test_flat_wrangling_in_a_data_schema_is_reported(tmp_path):
    problems = _problems(tmp_path, lambda r: r["data_schemas"]["A"].update(wrangling=[SORT]))
    assert [p.location for p in problems] == ["data_schemas.A.wrangling"] and "[S06]" in problems[0].problem


def test_all_problems_are_reported_not_only_the_first(tmp_path):
    def change(recipe):
        recipe["data_schemas"]["A"]["wrangling"] = [SORT]
        recipe["joins"] = {"J": dict(JOIN, steps=[SORT])}
        del recipe["analysis_groups"]["g"]["label"]
    assert len(_problems(tmp_path, change)) == 3


def test_a_join_step_in_tier2_is_reported(tmp_path):
    step = {"action": "polars_join", "right_ingredient": "A", "on": ["a"], "how": "left", "maintain_order": "left_right"}
    problems = _problems(tmp_path, lambda r: r.update(joins={"J": dict(JOIN, steps={"tier1": [], "tier2": [step]})}))
    assert len(problems) == 1 and "only allowed in tier1" in problems[0].problem


def test_a_removed_key_is_refused_and_the_fix_names_the_replacement(tmp_path):
    problems = _problems(tmp_path, lambda r: r.update(joins={"J": dict(JOIN, final_contract={"a": {}})}))
    assert [p.location for p in problems] == ["joins.J.final_contract"] and "polars_select" in problems[0].tip


def test_a_missing_label_is_refused(tmp_path):
    problems = _problems(tmp_path, lambda r: r["data_schemas"]["A"].pop("label"))
    assert [p.location for p in problems] == ["data_schemas.A"] and "label" in problems[0].problem


def test_an_action_that_is_not_registered_is_refused(tmp_path):
    problems = _problems(tmp_path, lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": [{"action": "sort", "columns": ["a"]}]}))
    assert len(problems) == 1 and "'sort' is not a registered action" in problems[0].problem


def test_a_step_without_a_required_parameter_is_refused(tmp_path):
    problems = _problems(tmp_path, lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": [{"action": "polars_sort", "by": ["a"]}]}))
    assert len(problems) == 1 and "maintain_order is required" in problems[0].problem


def test_a_plot_layer_that_is_not_registered_is_refused(tmp_path):
    def change(recipe):
        recipe["analysis_groups"]["g"]["plots"]["p"]["spec"]["layers"] = [{"name": "geom_nope", "params": {}}]
    problems = _problems(tmp_path, change)
    assert len(problems) == 1 and "geom_nope" in problems[0].problem


def test_an_empty_tier1_is_valid(tmp_path):
    assert _problems(tmp_path, lambda r: r["data_schemas"]["A"].update(wrangling={"tier1": []})) == []


def test_missing_include_is_a_problem_not_a_crash(tmp_path):
    path = write_tiny(tmp_path)
    path.write_text(path.read_text().replace("wrangling:\n      tier1: []", "wrangling: !include 'does_not_exist/w.yaml'"))
    problems = validate_data_analysis_recipe(path)
    assert problems and any("does_not_exist/w.yaml" in p.problem and "not found" in p.problem for p in problems)


def test_a_file_that_is_not_yaml_is_a_problem_not_a_crash(tmp_path):
    path = tmp_path / "m.yaml"
    path.write_text("id: m\n  bad: [\n")
    problems = validate_data_analysis_recipe(path)
    assert len(problems) == 1 and "not valid YAML" in problems[0].problem


def test_missing_file_is_a_problem_not_a_crash(tmp_path):
    problems = validate_data_analysis_recipe(tmp_path / "nope.yaml")
    assert len(problems) == 1 and "not found" in problems[0].problem


def test_data_analysis_recipe_without_analysis_groups_is_a_problem_not_a_crash(tmp_path):
    problems = _problems(tmp_path, lambda r: r.pop("analysis_groups"))
    assert len(problems) == 1 and "analysis_groups" in problems[0].problem


def test_the_checker_must_have_looked_at_the_actions_and_the_plot_components(tmp_path, monkeypatch):
    """A recipe is never accepted on a partial check: without the registries the validation fails and says so."""
    from app.modules import data_analysis_recipe_validator as module
    monkeypatch.setattr(module, "checker_catalogs", lambda: {})
    problems = validate_data_analysis_recipe(write_tiny(tmp_path))
    assert len(problems) == 1 and "did not cover" in problems[0].problem and "actions" in problems[0].problem


def test_find_data_analysis_recipes_ignores_subfolders(tmp_path):
    write_tiny(tmp_path, tiny_recipe("a"))
    sub = tmp_path / "a"
    sub.mkdir()
    (sub / "fragment.yaml").write_text("x: 1\n")
    assert [p.name for p in find_data_analysis_recipes(tmp_path)] == ["a.yaml"]


# --- the id: key says the same as the file name ---

def test_id_that_differs_from_the_file_name_is_a_problem(tmp_path):
    problems = validate_data_analysis_recipe(write_tiny(tmp_path, tiny_recipe("other_name"), "my_file.yaml"))
    assert [x.location for x in problems] == ["id"]
    assert "my_file" in problems[0].tip


def test_id_equal_to_the_file_name_is_fine(tmp_path):
    assert validate_data_analysis_recipe(write_tiny(tmp_path, tiny_recipe("my_file"))) == []


def test_every_shipped_data_analysis_recipe_has_its_file_name_as_id():
    root = Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes"
    files = [f for d in (root, *[p for p in root.iterdir() if p.is_dir()]) for f in d.glob("*.yaml")]
    assert files
    wrong = [str(p.relative_to(root)) for p in files
             if any(x.location == "id" for x in validate_data_analysis_recipe(p))]
    assert wrong == []


def test_every_template_is_a_valid_data_analysis_recipe():
    """The templates are what people copy: each must load and pass the same checks as a real data analysis recipe."""
    root = Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes" / "templates"
    templates = sorted(root.glob("*.yaml"))
    assert len(templates) >= 4  # the universal template was removed 2026-11-14 (Eve)
    bad = {t.name: [str(p) for p in validate_data_analysis_recipe(t)] for t in templates}
    assert {k: v for k, v in bad.items() if v} == {}
