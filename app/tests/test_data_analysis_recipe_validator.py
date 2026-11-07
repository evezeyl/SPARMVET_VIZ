"""Contract test for data analysis recipes: every data analysis recipe in the active deployment's data analysis recipes location
must have step lists in a shape the engine accepts (issue evezeyl/SPARMVET_VIZ#8).

The data analysis recipes folder is read from the deployment (Location 2) through the bootloader, so
a new data analysis recipe added there is tested without changing this file.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_analysis_recipe_validator.py -q
"""
import re
from pathlib import Path
from textwrap import dedent

import pytest

from app.modules.data_analysis_recipe_validator import find_data_analysis_recipes, validate_data_analysis_recipe
from app.src.bootloader import Bootloader

DATA_ANALYSIS_RECIPE_DIR = Bootloader().get_location("data_analysis_recipes")
DATA_ANALYSIS_RECIPES = find_data_analysis_recipes(DATA_ANALYSIS_RECIPE_DIR)


def test_data_analysis_recipes_are_found():
    assert DATA_ANALYSIS_RECIPES, f"no data analysis recipes found in {DATA_ANALYSIS_RECIPE_DIR}: the discovery would silently test nothing"


@pytest.mark.parametrize("path", DATA_ANALYSIS_RECIPES, ids=lambda p: p.name)
def test_data_analysis_recipe_has_no_step_problems(path):
    problems = validate_data_analysis_recipe(path)
    assert problems == [], "\n".join(str(p) for p in problems)


# --- the validator itself, on small data analysis recipes written for the test ------------------------


# ConfigManager refuses a data analysis recipe without analysis_groups (ADR-077), so every test
# data analysis recipe carries this minimal block.
_ANALYSIS = """
analysis_groups:
  g:
    label: G
    plots:
      p:
        label: P
        spec:
          target_dataset: A
          mapping: {x: a}
          layers:
            - name: geom_bar
"""


def _write(tmp_path: Path, body: str, name: str = "m.yaml", with_analysis: bool = True) -> Path:
    path = tmp_path / name
    text = re.sub(r"(?m)^id: .*$", f"id: {path.stem}", dedent(body))  # the id: key equals the file name
    path.write_text(text + (_ANALYSIS if with_analysis else ""))
    return path


def test_tiered_steps_is_valid(tmp_path):
    path = _write(tmp_path, """
        id: t
        joins:
          A:
            steps:
              tier1:
                - action: join
                  right_ingredient: B
                  'on': sample_id
        """)
    assert validate_data_analysis_recipe(path) == []


def test_flat_assembly_steps_is_reported_once_with_location(tmp_path):
    path = _write(tmp_path, """
        id: t
        joins:
          A:
            steps:
              - action: join
                right_ingredient: B
                'on': sample_id
        """)
    problems = validate_data_analysis_recipe(path)
    assert len(problems) == 1
    assert problems[0].location == "joins.A.steps"
    assert "Flat" in problems[0].problem
    assert problems[0].data_analysis_recipe == "m.yaml"


def test_flat_wrangling_in_a_data_schema_is_reported(tmp_path):
    path = _write(tmp_path, """
        id: t
        data_schemas:
          S:
            source: {type: tsv, path: ./x.tsv}
            wrangling:
              - action: sort
                columns: [Year]
        """)
    problems = validate_data_analysis_recipe(path)
    assert [p.location for p in problems] == ["data_schemas.S.wrangling"]


def test_all_problems_are_reported_not_only_the_first(tmp_path):
    path = _write(tmp_path, """
        id: t
        data_schemas:
          S:
            source: {type: tsv, path: ./x.tsv}
            wrangling:
              - action: sort
                columns: [Year]
        joins:
          A:
            steps:
              - action: join
                right_ingredient: S
        """)
    assert len(validate_data_analysis_recipe(path)) == 2


def test_join_in_tier2_is_reported(tmp_path):
    path = _write(tmp_path, """
        id: t
        joins:
          A:
            steps:
              tier1: []
              tier2:
                - action: join
                  right_ingredient: B
        """)
    problems = validate_data_analysis_recipe(path)
    assert len(problems) == 1 and "Tier 2" in problems[0].problem


def test_empty_wrangling_is_valid(tmp_path):
    path = _write(tmp_path, """
        id: t
        data_schemas:
          S:
            source: {type: tsv, path: ./x.tsv}
            wrangling: []
        """)
    assert validate_data_analysis_recipe(path) == []


def test_missing_include_is_a_problem_not_a_crash(tmp_path):
    path = _write(tmp_path, """
        id: t
        joins:
          A:
            steps: !include 'does_not_exist/steps.yaml'
        """)
    problems = validate_data_analysis_recipe(path)
    assert len(problems) == 1 and problems[0].location == "load"


def test_missing_file_is_a_problem_not_a_crash(tmp_path):
    problems = validate_data_analysis_recipe(tmp_path / "nope.yaml")
    assert len(problems) == 1 and "not found" in problems[0].problem


def test_data_analysis_recipe_without_analysis_groups_is_a_problem_not_a_crash(tmp_path):
    path = _write(tmp_path, "id: t\n", with_analysis=False)
    problems = validate_data_analysis_recipe(path)
    assert len(problems) == 1 and "analysis_groups" in problems[0].problem


def test_find_data_analysis_recipes_ignores_subfolders(tmp_path):
    _write(tmp_path, "id: a\n", "a.yaml", with_analysis=False)
    sub = tmp_path / "a"
    sub.mkdir()
    (sub / "fragment.yaml").write_text("x: 1\n")
    assert [p.name for p in find_data_analysis_recipes(tmp_path)] == ["a.yaml"]


# --- the id: key says the same as the file name ---

def test_id_that_differs_from_the_file_name_is_a_problem(tmp_path):
    p = tmp_path / "my_file.yaml"
    p.write_text("id: other_name\ndata_schemas: {}\njoins: {}\nanalysis_groups: {g: {plots: {}}}\n")
    problems = validate_data_analysis_recipe(p)
    assert [x.location for x in problems] == ["id"]
    assert "my_file" in problems[0].tip


def test_id_equal_to_the_file_name_is_fine(tmp_path):
    p = tmp_path / "my_file.yaml"
    p.write_text("id: my_file\ndata_schemas: {}\njoins: {}\nanalysis_groups: {g: {plots: {}}}\n")
    assert validate_data_analysis_recipe(p) == []


def test_every_shipped_data_analysis_recipe_has_its_file_name_as_id():
    root = Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes"
    files = [f for d in (root, *[p for p in root.iterdir() if p.is_dir()]) for f in d.glob("*.yaml")]
    assert files
    wrong = [str(p.relative_to(root)) for p in files
             if any(x.location == "id" for x in validate_data_analysis_recipe(p))]
    assert wrong == []
