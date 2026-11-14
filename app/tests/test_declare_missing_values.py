"""The missing-value texts are declared per field of the table where they occur (Eve 2026-11-14).

`assets/scripts/declare_missing_values.py` replaces the blanket list of the 14 texts of the old sanitiser by the texts
that really occur, in the field where they occur. The result of every recipe stays identical.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_declare_missing_values.py -q
"""
import importlib.util
from pathlib import Path

import polars as pl
import yaml

from ingestion.ingestor import DataIngestor

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location("dmv", ROOT / "assets/scripts/declare_missing_values.py")
dmv = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(dmv)

BLANKET = '["", "NA", "N/A", "None", "null", "NaN", "-", "na", "n/a", "none", "nan", "NULL", "n.a.", "N.A."]'
RECIPE = f"""id: t
spec_version: 1
source:
  type: local_tsv
  path: t.tsv
# a comment that must stay
null_values: {BLANKET}
strip: true
input_fields:
  sample:
    type: String
  st:
    original_name: ST
    type: String   # the sequence type: a dash means not typed
  note:
    type: String
"""
DATA = "sample\tST\tnote\ns1\t-\tNA\ns2\t22\t-\ns3\t 7 \tfine\n"


def _setup(tmp_path):
    (tmp_path / "t.tsv").write_text(DATA)
    recipe = tmp_path / "t.yaml"
    recipe.write_text(RECIPE)
    return recipe


def _ingest(tmp_path, recipe):
    schema = yaml.safe_load(recipe.read_text())
    schema["source"]["path"] = str(tmp_path / "t.tsv")
    return DataIngestor(str(tmp_path)).ingest("t", schema)[0].collect()


def test_a_dry_run_changes_nothing(tmp_path):
    recipe = _setup(tmp_path)
    dmv.declare([recipe], tmp_path, apply=False)
    assert recipe.read_text() == RECIPE


def test_the_texts_are_declared_in_the_field_where_they_occur_and_the_result_is_identical(tmp_path):
    recipe = _setup(tmp_path)
    before = _ingest(tmp_path, recipe)
    dmv.declare([recipe], tmp_path, apply=True)
    schema = yaml.safe_load(recipe.read_text())
    assert schema["null_values"] == []
    assert schema["input_fields"]["st"]["null_values"] == ["-"]
    assert schema["input_fields"]["note"]["null_values"] == ["NA", "-"]
    assert "null_values" not in schema["input_fields"]["sample"]
    assert "# a comment that must stay" in recipe.read_text() and "# the sequence type: a dash means not typed" in recipe.read_text()
    assert _ingest(tmp_path, recipe).equals(before)


def test_a_second_run_changes_nothing(tmp_path):
    recipe = _setup(tmp_path)
    dmv.declare([recipe], tmp_path, apply=True)
    once = recipe.read_text()
    dmv.declare([recipe], tmp_path, apply=True)
    assert recipe.read_text() == once


def test_a_text_that_is_a_value_in_another_field_is_not_missing_there(tmp_path):
    """The point of the declaration: `-` in the `st` field is missing, in a field that was not declared it stays text."""
    recipe = _setup(tmp_path)
    dmv.declare([recipe], tmp_path, apply=True)
    schema = yaml.safe_load(recipe.read_text())
    schema["input_fields"]["note"].pop("null_values")
    schema["source"]["path"] = str(tmp_path / "t.tsv")
    df = DataIngestor(str(tmp_path)).ingest("t", schema)[0].collect()
    assert df["note"].to_list() == ["NA", "-", "fine"] and df["st"].null_count() == 1


def test_the_shipped_recipes_have_nothing_left_to_declare():
    files = sorted((ROOT / "config/data_analysis_recipes/pipelines").glob("*.yaml"))
    assert dmv.declare(files, ROOT, apply=False) == []
