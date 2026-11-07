"""Contract test for manifests: every manifest in the active deployment's manifests location
must have recipes in a shape the engine accepts (issue evezeyl/SPARMVET_VIZ#8).

The manifests folder is read from the deployment (Location 2) through the bootloader, so
a new manifest added there is tested without changing this file.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_manifest_validator.py -q
"""
from pathlib import Path
from textwrap import dedent

import pytest

from app.modules.manifest_validator import find_manifests, validate_manifest
from app.src.bootloader import Bootloader

MANIFEST_DIR = Bootloader().get_location("manifests")
MANIFESTS = find_manifests(MANIFEST_DIR)


def test_manifests_are_found():
    assert MANIFESTS, f"no manifests found in {MANIFEST_DIR}: the discovery would silently test nothing"


@pytest.mark.parametrize("path", MANIFESTS, ids=lambda p: p.name)
def test_manifest_has_no_recipe_problems(path):
    problems = validate_manifest(path)
    assert problems == [], "\n".join(str(p) for p in problems)


# --- the validator itself, on small manifests written for the test ------------------------


# ConfigManager refuses a manifest without analysis_groups (ADR-077), so every test
# manifest carries this minimal block.
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
    path.write_text(dedent(body) + (_ANALYSIS if with_analysis else ""))
    return path


def test_tiered_recipe_is_valid(tmp_path):
    path = _write(tmp_path, """
        id: t
        join_manifests:
          A:
            recipe:
              tier1:
                - action: join
                  right_ingredient: B
                  'on': sample_id
        """)
    assert validate_manifest(path) == []


def test_flat_assembly_recipe_is_reported_once_with_location(tmp_path):
    path = _write(tmp_path, """
        id: t
        join_manifests:
          A:
            recipe:
              - action: join
                right_ingredient: B
                'on': sample_id
        """)
    problems = validate_manifest(path)
    assert len(problems) == 1
    assert problems[0].location == "join_manifests.A.recipe"
    assert "Flat" in problems[0].problem
    assert problems[0].manifest == "m.yaml"


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
    problems = validate_manifest(path)
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
        join_manifests:
          A:
            recipe:
              - action: join
                right_ingredient: S
        """)
    assert len(validate_manifest(path)) == 2


def test_join_in_tier2_is_reported(tmp_path):
    path = _write(tmp_path, """
        id: t
        join_manifests:
          A:
            recipe:
              tier1: []
              tier2:
                - action: join
                  right_ingredient: B
        """)
    problems = validate_manifest(path)
    assert len(problems) == 1 and "Tier 2" in problems[0].problem


def test_empty_wrangling_is_valid(tmp_path):
    path = _write(tmp_path, """
        id: t
        data_schemas:
          S:
            source: {type: tsv, path: ./x.tsv}
            wrangling: []
        """)
    assert validate_manifest(path) == []


def test_missing_include_is_a_problem_not_a_crash(tmp_path):
    path = _write(tmp_path, """
        id: t
        join_manifests:
          A:
            recipe: !include 'does_not_exist/recipe.yaml'
        """)
    problems = validate_manifest(path)
    assert len(problems) == 1 and problems[0].location == "load"


def test_missing_file_is_a_problem_not_a_crash(tmp_path):
    problems = validate_manifest(tmp_path / "nope.yaml")
    assert len(problems) == 1 and "not found" in problems[0].problem


def test_manifest_without_analysis_groups_is_a_problem_not_a_crash(tmp_path):
    path = _write(tmp_path, "id: t\n", with_analysis=False)
    problems = validate_manifest(path)
    assert len(problems) == 1 and "analysis_groups" in problems[0].problem


def test_find_manifests_ignores_subfolders(tmp_path):
    _write(tmp_path, "id: a\n", "a.yaml", with_analysis=False)
    sub = tmp_path / "a"
    sub.mkdir()
    (sub / "fragment.yaml").write_text("x: 1\n")
    assert [p.name for p in find_manifests(tmp_path)] == ["a.yaml"]
