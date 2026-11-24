"""The one big move, on the shipped recipes (D-0586, D-0610, D-0613): a joined table starts from a data table and the metadata comes in by a left join.

What is checked, on every shipped recipe of `pipelines/` and `templates/` and on the tables the move rewrote:
- no joined table has the metadata (`metadata_schema`) as its first ingredient, and no join step with the metadata is an inner join (a look-up list may be);
- the two QA tables made from the metadata alone are data schemas on the metadata file (same file, own name, own marker), not joins of one ingredient;
- VirulenceFinder is a data schema with a `completion` block (not an additional dataset) in the two recipes that read it;
- the tables built from the rewritten joins hold the same entities as before and the same rows (the demo: ST22_Anchor 617 rows and 42 entities; the QA tables
  74, 1731, 42 rows; demo_abromics 27 rows for 27 samples);
- MLST and VirulenceFinder keep their own marker column through their first step (the select names it);
- every shipped recipe passes the recipe check and the data check, and the load gate keeps every one of them (nothing rejected).

The check "starts from the metadata" is a function of this file, not of the checker: the rule is advice only and is not enforced by the checker (how it would be
enforced is not decided). A test that cannot fail proves nothing, so the last tests turn a recipe back to the old form and see the function find it.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_recipes_data_first.py -q

# @deps
# consumes: config/data_analysis_recipes/pipelines/*.yaml, config/data_analysis_recipes/templates/*.yaml, app/modules/orchestrator.py, app/src/bootloader.py
# doc: .claude/rules/rules_data_analysis_recipe_structure.md
# @end_deps
"""
import copy
import os
from pathlib import Path

import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, load_data_analysis_recipe
from app.modules.data_analysis_recipe_validator import check_data_analysis_recipe_data, validate_data_analysis_recipe
from app.modules.orchestrator import DataOrchestrator
from app.tests.test_id_completion import DEMO, NOT_IN_ORIGINAL, PIPELINES, ROOT, quiet

TEMPLATES = ROOT / "config" / "data_analysis_recipes" / "templates"
METADATA = "metadata_schema"
SHIPPED = sorted(PIPELINES.glob("*.yaml")) + sorted(TEMPLATES.glob("*.yaml"))


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def raw_of(path: Path) -> dict:
    return load_data_analysis_recipe(path).raw


def starts_from_metadata(raw: dict) -> list:
    """The joined tables whose first ingredient is the metadata table."""
    return [j for j, spec in (raw.get("joins") or {}).items() if (spec.get("ingredients") or [{}])[0].get("dataset_id") == METADATA]


def inner_joins_with_the_metadata(raw: dict) -> list:
    """(joined table, tier) of every join step that brings the metadata in with `how: inner`."""
    found = []
    for j, spec in (raw.get("joins") or {}).items():
        for tier in ("tier1", "tier2"):
            for step in ((spec.get(tier) or {}).get("steps") or []):
                if step.get("action") == "polars_join" and step.get("right_ingredient") == METADATA and step.get("how") == "inner":
                    found.append((j, tier))
    return found


# -- the rule on every shipped recipe -------------------------------------------------------------------

def test_the_list_of_shipped_recipes_is_not_empty():
    assert len(SHIPPED) >= 10, "the discovery would test nothing"


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: p.stem)
def test_no_shipped_joined_table_starts_from_the_metadata(path):
    assert starts_from_metadata(raw_of(path)) == []


@pytest.mark.parametrize("path", SHIPPED, ids=lambda p: p.stem)
def test_no_shipped_join_brings_the_metadata_in_with_an_inner_join(path):
    assert inner_joins_with_the_metadata(raw_of(path)) == []


def test_the_look_up_list_may_still_be_an_inner_join():
    """Her words: the look-up filter is intended. The APEC/STEC list is joined with `how: inner` in ST22_Anchor and in AR1."""
    steps = raw_of(PIPELINES / f"{DEMO}.yaml")["joins"]["ST22_Anchor"]["tier1"]["steps"]
    assert [s["how"] for s in steps if s.get("right_ingredient") == "APEC_STEC_virulence_genes"] == ["inner"]


# -- the check can fail ---------------------------------------------------------------------------------

def test_the_check_finds_a_joined_table_that_starts_from_the_metadata_again():
    raw = copy.deepcopy(raw_of(PIPELINES / f"{DEMO}.yaml"))
    ingredients = raw["joins"]["ST22_Anchor"]["ingredients"]
    ingredients.sort(key=lambda i: i["dataset_id"] != METADATA)
    assert starts_from_metadata(raw) == ["ST22_Anchor"]


def test_the_check_finds_an_inner_join_with_the_metadata_again():
    raw = copy.deepcopy(raw_of(PIPELINES / "2_test_data_ST22_dummy.yaml"))
    for step in raw["joins"]["AMR_Profile_Joint"]["tier1"]["steps"]:
        if step.get("right_ingredient") == METADATA:
            step["how"] = "inner"
    assert inner_joins_with_the_metadata(raw) == [("AMR_Profile_Joint", "tier1")]


# -- the two QA tables, VirulenceFinder, the completion of 2_test and figshare --------------------------

def test_the_two_qa_tables_made_from_the_metadata_are_data_schemas_on_its_file():
    raw = raw_of(PIPELINES / f"{DEMO}.yaml")
    meta_path = raw[METADATA]["source"]["path"]
    for name in ("QA_year_types", "QA_aggregated_no_key"):
        assert name not in raw["joins"]
        schema = raw["data_schemas"][name]
        assert schema["source"]["path"] == meta_path
        assert schema["completion"]["marker"] == f"{name}_not_in_original_data"
    targets = {p["target_dataset"] for g in raw["analysis_groups"].values() for p in g["plots"].values()}
    assert {"QA_year_types", "QA_aggregated_no_key"} <= targets


def test_the_two_qa_tables_are_what_they_were_with_the_new_marker(tmp_path):
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, DEMO)
    work = tmp_path
    year = quiet(orchestrator.materialize_tier1, DEMO, "QA_year_types", work / "t_year.parquet", keys=keys).collect()
    assert year.height == 42 and year["sample_id"].n_unique() == 42 and year["QA_year_types_not_in_original_data"].sum() == 0
    assert year["year_label"].str.contains(r"\.0").sum() == 0
    agg1 = quiet(orchestrator.materialize_tier1, DEMO, "QA_aggregated_no_key", work / "t_agg.parquet", keys=keys).collect()
    agg2 = quiet(orchestrator.materialize_tier2, DEMO, "QA_aggregated_no_key", work / "t_agg.parquet", keys=keys).collect()
    assert agg1.height == 42 and "sample_id" in agg1.columns
    assert agg2.height == 9 and "sample_id" not in agg2.columns and agg2["n_samples"].sum() == 42


@pytest.mark.parametrize("recipe", ["1_test_data_ST22_dummy", "1_Abromics_general_pipeline"])
def test_virulencefinder_is_a_data_schema_with_a_completion_block(recipe):
    raw = raw_of(PIPELINES / f"{recipe}.yaml")
    assert "VirulenceFinder" in raw["data_schemas"] and "VirulenceFinder" not in (raw.get("additional_datasets_schemas") or {})
    assert raw["data_schemas"]["VirulenceFinder"]["completion"]["marker"] == "VirulenceFinder_not_in_original_data"
    assert "APEC_STEC_virulence_genes" in raw["additional_datasets_schemas"], "the look-up list stays a look-up"


@pytest.mark.parametrize("recipe,tables", [("2_test_data_ST22_dummy", ["metadata_schema", "amr_data", "plasmid_data"]),
                                           ("figshare_integration", ["fg_metadata", "fg_phenotypes", "fg_genotypes"])])
def test_the_entity_id_is_declared_and_each_table_has_its_marker(recipe, tables):
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    raw = raw_of(PIPELINES / f"{recipe}.yaml")
    report = quiet(orchestrator.id_report, recipe, raw)
    assert sorted(t.table for t in report.tables) == sorted(tables) and report.check3_ok
    for t in tables:
        schema = raw[t] if t == METADATA else raw["data_schemas"][t]
        assert schema["completion"]["marker"] == f"{t}_not_in_original_data"
        assert schema["input_fields"]["sample_id"]["is_entity_id"] is True


# -- the rewritten joined tables: the same entities and the same rows ----------------------------------

def built(work, recipe, collection, tier=1):
    orchestrator = DataOrchestrator(PIPELINES, ROOT)
    keys = quiet(orchestrator.compute_data_analysis_recipe_keys, recipe)
    path = work / f"t_{recipe}_{collection}.parquet"
    t1 = quiet(orchestrator.materialize_tier1, recipe, collection, path, keys=keys).collect()
    return t1 if tier == 1 else quiet(orchestrator.materialize_tier2, recipe, collection, path, keys=keys).collect()


@pytest.mark.parametrize("collection,t1_rows,t2_rows", [("ST22_Anchor", 617, 617), ("QA_AMR_per_sample", 74, 42), ("QA_fanout_exhibit", 1731, 42), ("QA_population_zscore", 42, 42)])
def test_the_rewritten_demo_tables_keep_their_rows_and_all_42_entities(collection, t1_rows, t2_rows, tmp_path):
    t1, t2 = built(tmp_path, DEMO, collection, 1), built(tmp_path, DEMO, collection, 2)
    assert (t1.height, t2.height) == (t1_rows, t2_rows)
    assert t1["sample_id"].n_unique() == 42 and t2["sample_id"].n_unique() == 42
    assert t1["sample_id"].null_count() == 0


def test_the_demo_join_of_demo_abromics_is_27_rows_for_27_samples(tmp_path):
    table = built(tmp_path, "demo_abromics", "demo_join")
    assert table.height == 27 and table["sample_id"].n_unique() == 27 and table["sample_id"].null_count() == 0
    assert table["sequence_type"].null_count() == 0 and (table["sequence_type"] == "Non Determined").sum() >= 12


def test_no_entity_of_the_demo_reads_detected_without_a_resfinder_line(tmp_path):
    anchor = built(tmp_path, DEMO, "ST22_Anchor")
    assert set(anchor.filter(pl.col("sample_id").is_in(NOT_IN_ORIGINAL))["status"].to_list()) == {"Not Found"}
    assert set(anchor.filter(~pl.col("sample_id").is_in(NOT_IN_ORIGINAL))["status"].to_list()) == {"Detected"}


# -- the marker kept by the first step of MLST and VirulenceFinder ---------------------------------------

def test_mlst_keeps_its_own_marker_and_the_twelve_added_lines_of_demo_abromics_read_non_determined(tmp_path):
    table = built(tmp_path, "demo_abromics", "MLST")
    assert "MLST_not_in_original_data" in table.columns
    added = table.filter(pl.col("MLST_not_in_original_data"))
    assert added.height == 12 and added["sequence_type"].to_list() == ["Non Determined"] * 12
    assert table.filter(~pl.col("MLST_not_in_original_data")).height == table.height - 12


def test_virulencefinder_keeps_its_own_marker_and_nothing_is_added_in_the_shipped_data(tmp_path):
    table = built(tmp_path, DEMO, "VirulenceFinder")
    assert "VirulenceFinder_not_in_original_data" in table.columns and table["VirulenceFinder_not_in_original_data"].sum() == 0


# -- every shipped recipe passes the checks and the load gate ----------------------------------------------

@pytest.mark.parametrize("path", sorted(PIPELINES.glob("*.yaml")) + sorted(TEMPLATES.glob("*.yaml")), ids=lambda p: p.stem)
def test_every_shipped_recipe_passes_the_recipe_check(path):
    problems = validate_data_analysis_recipe(path)
    assert problems == [], "\n".join(str(p) for p in problems)


@pytest.mark.parametrize("path", sorted(PIPELINES.glob("*.yaml")), ids=lambda p: p.stem)
def test_every_shipped_pipeline_recipe_passes_the_data_check(path):
    check = quiet(check_data_analysis_recipe_data, path, ROOT, "data_analysis_recipe_paths", None)
    assert check.problems == [] and check.ids_error is None


def test_the_load_gate_keeps_every_shipped_pipeline_recipe():
    from app.src.bootloader import Bootloader
    saved = {k: os.environ.pop(k, None) for k in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_DATA_ANALYSIS_RECIPE")}
    try:
        gate = quiet(Bootloader)
    finally:
        for k, v in saved.items():
            if v is not None:
                os.environ[k] = v
    assert gate.rejected_data_analysis_recipes == {}
    assert {p.stem for p in PIPELINES.glob("*.yaml")} <= set(gate.available_data_analysis_recipes)


# -- the dry run of the big move lists nothing of the move on the shipped files ----------------------------

def test_the_dry_run_finds_no_joined_table_that_starts_from_the_metadata_and_no_additional_table_with_an_id():
    """`assets/scripts/dry_run_big_move.py` is the owner's list of what the move had to change: on the shipped recipes its sections 3 and 7 are now empty."""
    import importlib.util
    spec = importlib.util.spec_from_file_location("dry_run_big_move", ROOT / "assets/scripts/dry_run_big_move.py")
    tool = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(tool)
    lines = quiet(tool.build, ROOT)

    def section(n):
        start = next(i for i, l in enumerate(lines) if l.startswith(f"## {n}. "))
        end = next((i for i in range(start + 1, len(lines)) if lines[i].startswith("## ")), len(lines))
        return [l for l in lines[start + 1:end] if l.startswith(("- ", "* "))]

    joins = [l for l in section(3) if "joined table" in l and "none" not in l]
    assert joins == [], joins
    assert [l for l in section(7) if "declares the entity id" in l] == []
    assert any("0 joined table(s) (0 start from the metadata, 0 are made from it alone)" in l for l in lines)
