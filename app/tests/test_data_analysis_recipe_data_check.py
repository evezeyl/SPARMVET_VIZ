"""The data analysis recipe data check, and the loud failure of a dataset that cannot be loaded (issue #18).

Before: a declared field that matches no column stayed silent, and a dataset that failed to load
was dropped from the assembly with one console line (its join steps were skipped).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_data_analysis_recipe_data_check.py -q
"""
from pathlib import Path
from textwrap import dedent

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import find_data_analysis_recipes, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from utils.errors import IngestionError

ROOT = Path(__file__).resolve().parents[2]
DATA_ANALYSIS_RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"


@pytest.mark.parametrize("path", find_data_analysis_recipes(DATA_ANALYSIS_RECIPES_DIR), ids=lambda p: p.name)
def test_shipped_data_analysis_recipes_declare_only_columns_their_datasets_have(path):
    problems = validate_data_analysis_recipe_data(path, ROOT / "assets" / "test_data")
    assert problems == [], "\n".join(str(p) for p in problems)


# --- small data analysis recipes written for the test ---------------------------------------------------

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


def _make_data_analysis_recipe(tmp_path: Path, *, reads_header="sample_id\treads", reads_rows=("s1\t10", "s2\t20"),
             output_slug="reads", reads_type="numeric") -> Path:
    """A data analysis recipe with two datasets (A, B) and a collection J joining B onto A."""
    (tmp_path / "a.tsv").write_text("sample_id\tcountry\ns1\tNO\ns2\tSE\n")
    (tmp_path / "b.tsv").write_text(reads_header + "\n" + "\n".join(reads_rows) + "\n")
    data_analysis_recipe = tmp_path / "proj.yaml"
    data_analysis_recipe.write_text(dedent(f"""
        id: proj
        data_schemas:
          A:
            source: {{type: local_tsv, path: {tmp_path / 'a.tsv'}}}
            input_fields:
              sample_id: {{type: categorical}}
              country: {{type: categorical}}
          B:
            source: {{type: local_tsv, path: {tmp_path / 'b.tsv'}}}
            input_fields:
              sample_id: {{type: categorical}}
              reads: {{type: {reads_type}}}
            output_fields:
              sample_id: {{type: categorical}}
              {output_slug}: {{type: numeric}}
        joins:
          J:
            ingredients:
              - dataset_id: A
              - dataset_id: B
            steps:
              tier1:
                - action: join
                  right_ingredient: B
                  'on': sample_id
                  how: left
          OnlyA:
            ingredients:
              - dataset_id: A
            steps:
              tier1: []
        """) + _ANALYSIS)
    return data_analysis_recipe


def test_a_consistent_data_analysis_recipe_has_no_problems(tmp_path):
    data_analysis_recipe = _make_data_analysis_recipe(tmp_path)
    assert validate_data_analysis_recipe_data(data_analysis_recipe, tmp_path) == []


def test_a_declared_output_field_with_no_column_is_reported_with_a_hint(tmp_path):
    data_analysis_recipe = _make_data_analysis_recipe(tmp_path, output_slug="read")
    [problem] = validate_data_analysis_recipe_data(data_analysis_recipe, tmp_path)
    assert problem.location == "data_schemas.B.output_fields.read"
    assert "matches no column" in problem.problem
    assert "Did you mean 'reads'?" in problem.tip


def test_a_missing_input_column_is_reported_as_a_dataset_that_cannot_be_loaded(tmp_path):
    data_analysis_recipe = _make_data_analysis_recipe(tmp_path, reads_header="sample_id\tread_count")
    [problem] = validate_data_analysis_recipe_data(data_analysis_recipe, tmp_path)
    assert problem.location == "data_schemas.B"
    assert "cannot be loaded" in problem.problem and "Missing columns" in problem.problem
    assert "reads" in problem.problem


def test_the_data_check_looks_at_column_names_not_at_values(tmp_path):
    """Values are checked when a file is imported (issue #11); this check is about the data analysis recipe."""
    data_analysis_recipe = _make_data_analysis_recipe(tmp_path, reads_rows=("s1\tabc", "s2\t20"))
    assert validate_data_analysis_recipe_data(data_analysis_recipe, tmp_path) == []


def test_a_missing_data_file_is_reported(tmp_path):
    data_analysis_recipe = _make_data_analysis_recipe(tmp_path)
    (tmp_path / "b.tsv").unlink()
    [problem] = validate_data_analysis_recipe_data(data_analysis_recipe, tmp_path)
    assert problem.location == "data_schemas.B" and "cannot be loaded" in problem.problem


# --- the build ---------------------------------------------------------------------------------

def _build(tmp_path: Path, collection: str):
    clear_data_analysis_recipe_cache()
    orchestrator = DataOrchestrator(tmp_path, tmp_path)
    return orchestrator.materialize_tier1("proj", collection, tmp_path / f"{collection}.parquet",
                                          keys=orchestrator.compute_data_analysis_recipe_keys("proj"))


def test_the_build_works_when_every_dataset_loads(tmp_path):
    _make_data_analysis_recipe(tmp_path)
    assert _build(tmp_path, "J").collect().columns == ["sample_id", "country", "reads"]


def test_the_build_fails_loudly_when_a_dataset_it_needs_cannot_be_loaded(tmp_path):
    _make_data_analysis_recipe(tmp_path, reads_header="sample_id\tread_count")
    with pytest.raises(IngestionError) as err:
        _build(tmp_path, "J")
    assert "'B'" in str(err.value) and "'J'" in str(err.value) and "Missing columns" in str(err.value)


def test_a_broken_dataset_that_the_collection_does_not_use_does_not_stop_the_build(tmp_path):
    _make_data_analysis_recipe(tmp_path, reads_header="sample_id\tread_count")
    assert _build(tmp_path, "OnlyA").collect().columns == ["sample_id", "country"]
