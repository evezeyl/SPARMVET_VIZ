"""The MLST sequence types must survive the wrangling (issue #21).

Found on 2026-11-05: a `recode_values` rule with `default: "keep"` overwrote every sequence type
with the text "keep" (in `recode_values` the default is a literal value, not "keep the original").

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_mlst_sequence_type.py -q
"""
from pathlib import Path

import polars as pl
import pytest

from app.modules.data_analysis_recipe_validator import find_data_analysis_recipes
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager

ROOT = Path(__file__).resolve().parents[2]
DATA_ANALYSIS_RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
RAW = ROOT / "assets" / "test_data" / "1_test_data_ST22_dummy" / "test_data_MLST_results_20260307_105756.tsv"
# The ingestion step turns these into nulls (libs/ingestion DataSanitizer); the data analysis recipe labels them.
UNDETERMINED = "Non Determined"


@pytest.fixture(scope="module")
def mlst():
    raw = ConfigManager(str(DATA_ANALYSIS_RECIPES_DIR / "1_test_data_ST22_dummy.yaml")).raw_config
    orchestrator = DataOrchestrator(DATA_ANALYSIS_RECIPES_DIR, ROOT / "assets" / "test_data")
    return orchestrator.prepare_ingredient("MLST", raw["data_schemas"]["MLST"]).collect()


def test_each_sample_keeps_its_raw_sequence_type(mlst):
    raw = pl.read_csv(RAW, separator="\t", infer_schema_length=0).select("sample_id", "Sequence Type")
    expected = {
        row[0]: row[1] if row[1].isdigit() else UNDETERMINED
        for row in raw.rows()
    }
    got = dict(zip(mlst["sample_id"].cast(pl.Utf8).to_list(), mlst["sequence_type"].cast(pl.Utf8).to_list()))
    assert got == expected


def test_there_are_several_sequence_types_and_no_nulls(mlst):
    assert mlst["sequence_type"].n_unique() > 1
    assert mlst["sequence_type"].null_count() == 0
    assert "keep" not in mlst["sequence_type"].cast(pl.Utf8).to_list()


def _recode_rules(node):
    """Yield the rules list of every recode_values step found anywhere in a data analysis recipe."""
    if isinstance(node, dict):
        if node.get("action") == "recode_values":
            yield node.get("rules") or []
        for value in node.values():
            yield from _recode_rules(value)
    elif isinstance(node, list):
        for item in node:
            yield from _recode_rules(item)


@pytest.mark.parametrize("path", find_data_analysis_recipes(DATA_ANALYSIS_RECIPES_DIR), ids=lambda p: p.name)
def test_no_data_analysis_recipe_uses_default_keep_in_recode_values(path):
    raw = ConfigManager(str(path)).raw_config
    bad = [
        rule for rules in _recode_rules(raw) for rule in rules
        if isinstance(rule, dict) and str(rule.get("default", "")).lower() == "keep"
    ]
    assert bad == [], "default: keep is a literal value in recode_values; use replace_values to leave others alone"
