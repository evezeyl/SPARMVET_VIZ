"""The retest data analysis recipes in config/data_analysis_recipes/retest/ must keep working, with the numbers the retest
procedure (.claude/tasks/retest_procedure_2026-11-06.md) tells the tester to expect.

If this test fails, the procedure is wrong too: fix both.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_retest_data_analysis_recipes.py -q
"""
from pathlib import Path

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from utils.errors import IngestionError

ROOT = Path(__file__).resolve().parents[2]
DATA_ANALYSIS_RECIPES = ROOT / "config" / "data_analysis_recipes" / "retest"
RAW = ROOT / "assets" / "test_data"


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def orch():
    return DataOrchestrator(DATA_ANALYSIS_RECIPES, RAW)


def t1(data_analysis_recipe, join, tmp_path):
    o = orch()
    return o.materialize_tier1(data_analysis_recipe, join, tmp_path / f"{join}.parquet", keys=o.compute_data_analysis_recipe_keys(data_analysis_recipe))


def t2(data_analysis_recipe, join, tmp_path):
    o = orch()
    return o.materialize_tier2(data_analysis_recipe, join, tmp_path / f"{join}.parquet", keys=o.compute_data_analysis_recipe_keys(data_analysis_recipe))


@pytest.mark.parametrize("data_analysis_recipe", ["retest_tier2", "retest_top_n_other", "retest_broken_header",
                                     "retest_bad_output_field"])
def test_every_retest_data_analysis_recipe_is_a_valid_data_analysis_recipe(data_analysis_recipe):
    assert validate_data_analysis_recipe(DATA_ANALYSIS_RECIPES / f"{data_analysis_recipe}.yaml") == []


# -- retest_tier2 ---------------------------------------------------------------------------

def test_tier2_join_has_12_rows_in_t1_and_8_in_t2_and_stores_the_t2_file(tmp_path):
    assert t1("retest_tier2", "Result", tmp_path).collect().height == 12
    assert t2("retest_tier2", "Result", tmp_path).collect().height == 8
    assert (tmp_path / "Result__T2.parquet").exists()


def test_join_without_tier2_steps_has_equal_t1_and_t2_and_no_t2_file(tmp_path):
    assert t2("retest_tier2", "All_samples", tmp_path).collect().height == 12
    assert not (tmp_path / "All_samples__T2.parquet").exists()


def test_the_values_the_procedure_names_are_kept_and_dropped(tmp_path):
    kept = set(t2("retest_tier2", "Result", tmp_path).collect()["sample_id"].to_list())
    assert kept == {"s02", "s03", "s05", "s06", "s08", "s09", "s11", "s12"}


# -- retest_top_n_other ----------------------------------------------------------------------

def counts(tmp_path):
    df = t1("retest_top_n_other", "Variants_joined", tmp_path).collect()
    out = df.group_by("variant_top3").len().to_dicts()
    return {r["variant_top3"]: r["len"] for r in out}


def test_top_n_other_with_count_distinct_keeps_v1_v3_v4(tmp_path):
    assert counts(tmp_path) == {"V1": 6, "V3": 3, "V4": 2, "Other": 9, None: 1}


def test_top_n_other_without_count_distinct_keeps_v1_v2_v3(tmp_path):
    entry = DATA_ANALYSIS_RECIPES / "retest_top_n_other.yaml"
    original = entry.read_text()
    try:
        entry.write_text(original.replace("          count_distinct: sample_id     # EDIT HERE (test 2): delete this line, then reload\n", ""))
        assert counts(tmp_path) == {"V1": 6, "V2": 4, "V3": 3, "Other": 7, None: 1}
    finally:
        entry.write_text(original)


# -- retest_broken_header / retest_bad_output_field ------------------------------------------

def test_a_renamed_header_fails_the_build_and_names_the_dataset_and_the_column(tmp_path):
    with pytest.raises(IngestionError) as e:
        t1("retest_broken_header", "Genes_joined", tmp_path)
    assert "Genes" in str(e.value) and "predicted_phenotype" in str(e.value)


def test_a_declared_output_field_with_no_column_is_reported_with_a_tip():
    problems = validate_data_analysis_recipe_data(DATA_ANALYSIS_RECIPES / "retest_bad_output_field.yaml", RAW)
    text = " ".join(str(p) for p in problems)
    assert "phenotype" in text and "predicted_phenotype" in text


def test_the_fixed_output_field_passes_the_check():
    entry = DATA_ANALYSIS_RECIPES / "retest_bad_output_field.yaml"
    original = entry.read_text()
    try:
        entry.write_text(original.replace("      phenotype: {type: categorical}      # EDIT HERE (test 3): change to predicted_phenotype",
                                          "      predicted_phenotype: {type: categorical}"))
        assert validate_data_analysis_recipe_data(entry, RAW) == []
    finally:
        entry.write_text(original)
