"""The retest data analysis recipes in config/data_analysis_recipes/retest/ must keep working, with the numbers the retest
procedure (.claude/workflows/retest_procedure.md) tells the tester to expect.

If this test fails, the procedure is wrong too: fix both.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_retest_data_analysis_recipes.py -q
"""
import importlib.util
import shutil
from pathlib import Path

import pytest
import yaml

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe, validate_data_analysis_recipe_data
from app.modules.orchestrator import DataOrchestrator
from app.src.bootloader import Bootloader
from utils.errors import IngestionError

ROOT = Path(__file__).resolve().parents[2]
DATA_ANALYSIS_RECIPES = ROOT / "config" / "data_analysis_recipes" / "retest"
RAW = ROOT / "assets" / "test_data"
RETEST_RECIPES = ["retest_tier2", "retest_top_n_other", "retest_broken_header", "retest_bad_select_column"]

# The file edits of the scripted walkthrough (RT-04, RT-05, RT-30, RT-31) are plain functions of the script. They are
# checked here without a browser, so that the script cannot edit a recipe into something the procedure does not describe.
_spec = importlib.util.spec_from_file_location("retest_walkthrough", ROOT / "assets/scripts/retest_walkthrough.py")
walkthrough = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(walkthrough)


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


def edited_copy(tmp_path, data_analysis_recipe, edit):
    """A copy of the retest recipes in which one recipe is edited; the shipped files are not touched."""
    copy = tmp_path / "retest"
    shutil.copytree(DATA_ANALYSIS_RECIPES, copy)
    entry = copy / f"{data_analysis_recipe}.yaml"
    entry.write_text(edit(entry.read_text(encoding="utf-8")), encoding="utf-8")
    return copy


def test_the_retest_recipes_are_the_ones_the_procedure_names():
    """A recipe added to or removed from the folder must be added to or removed from the procedure and this test."""
    assert sorted(p.stem for p in DATA_ANALYSIS_RECIPES.glob("*.yaml")) == sorted(RETEST_RECIPES)
    procedure = (ROOT / ".claude/workflows/retest_procedure.md").read_text(encoding="utf-8")
    for name in RETEST_RECIPES:
        assert f"`{name}`" in procedure, f"{name} is not named in the retest procedure"
    assert "retest_bad_output_field" not in procedure, "the retired scenario is still in the procedure"


@pytest.mark.parametrize("data_analysis_recipe", RETEST_RECIPES)
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


# -- the file edits of the walkthrough on retest_tier2 (RT-04, RT-05) ------------------------

def _result(copy, tmp_path):
    """Tier 1 and tier 2 of the join Result of an edited copy, and whether a tier 2 file was stored."""
    o = DataOrchestrator(copy, RAW)
    keys = o.compute_data_analysis_recipe_keys("retest_tier2")
    store = tmp_path / "store"
    store.mkdir()
    first = o.materialize_tier1("retest_tier2", "Result", store / "Result.parquet", keys=keys).collect()
    second = o.materialize_tier2("retest_tier2", "Result", store / "Result.parquet", keys=keys).collect()
    return first, second, (store / "Result__T2.parquet").exists()


def test_rt04_edit_changes_the_tier2_step_only(tmp_path):
    copy = edited_copy(tmp_path, "retest_tier2", lambda text: walkthrough.with_tier2_threshold(text, 20))
    first, second, stored = _result(copy, tmp_path)
    assert first.height == 12
    assert set(second["sample_id"].to_list()) == {"s05", "s06", "s09"}
    assert stored


def test_rt05_edit_moves_the_step_to_tier1(tmp_path):
    copy = edited_copy(tmp_path, "retest_tier2", walkthrough.with_step_moved_to_tier1)
    assert validate_data_analysis_recipe(copy / "retest_tier2.yaml") == []
    first, second, stored = _result(copy, tmp_path)
    assert first.height == 8, "the step runs in tier 1 now"
    assert second.height == 8
    assert not stored, "a join without tier 2 steps stores no tier 2 file"


@pytest.mark.parametrize("edit", ["with_step_moved_to_tier1", "with_header_fixed", "with_select_column_fixed"])
def test_an_edit_that_finds_nothing_to_change_fails(edit):
    """The script must not go on with an unedited file when a recipe was reworded."""
    with pytest.raises(ValueError, match="retest recipe"):
        getattr(walkthrough, edit)("id: other\n")
    with pytest.raises(ValueError, match="retest recipe"):
        walkthrough.with_tier2_threshold("id: other\n", 20)


# -- retest_broken_header (RT-30) -------------------------------------------------------------

def test_a_renamed_header_fails_the_build_and_names_the_dataset_and_the_column(tmp_path):
    with pytest.raises(IngestionError) as e:
        t1("retest_broken_header", "Genes_joined", tmp_path)
    assert "Genes" in str(e.value) and "predicted_phenotype" in str(e.value)


def test_rt30_edit_makes_the_recipe_pass_the_data_check(tmp_path):
    assert validate_data_analysis_recipe_data(DATA_ANALYSIS_RECIPES / "retest_broken_header.yaml", RAW) != []
    copy = edited_copy(tmp_path, "retest_broken_header", walkthrough.with_header_fixed)
    assert validate_data_analysis_recipe_data(copy / "retest_broken_header.yaml", RAW) == []


# -- retest_bad_select_column (RT-31; it replaces retest_bad_output_field, retired with the schema output_fields) ----

def test_a_select_step_with_a_misspelled_column_is_reported_with_the_message_of_the_engine():
    problems = validate_data_analysis_recipe_data(DATA_ANALYSIS_RECIPES / "retest_bad_select_column.yaml", RAW)
    assert len(problems) == 1
    assert problems[0].location == "data_schemas.Genes"
    text = str(problems[0])
    assert 'unable to find column "phenotype"' in text, text
    assert "predicted_phenotype" in text, "the message lists the columns that exist"


def test_the_misspelled_select_step_fails_the_build_too(tmp_path):
    """The check and the engine agree: the recipe cannot be built either."""
    with pytest.raises(Exception, match='unable to find column "phenotype"'):
        t1("retest_bad_select_column", "Genes_joined", tmp_path).collect()


def test_rt31_edit_makes_the_recipe_pass_the_data_check_and_keeps_the_three_columns(tmp_path):
    copy = edited_copy(tmp_path, "retest_bad_select_column", walkthrough.with_select_column_fixed)
    assert validate_data_analysis_recipe_data(copy / "retest_bad_select_column.yaml", RAW) == []
    o = DataOrchestrator(copy, RAW)
    frame = o.materialize_tier1("retest_bad_select_column", "Genes_joined", tmp_path / "Genes_joined.parquet",
                                keys=o.compute_data_analysis_recipe_keys("retest_bad_select_column")).collect()
    assert frame.columns == ["sample_id", "gene", "predicted_phenotype"]
    assert frame.height == 3


# -- the load gate on the retest deployment (RT-30, RT-31) -----------------------------------------

def test_the_load_gate_refuses_the_two_broken_recipes_and_gives_the_reasons_of_the_procedure(tmp_path, monkeypatch):
    """What the tester reads beneath the recipe selector: the two refused recipes, each with its reason."""
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE",
                "SPARMVET_CONNECTOR", "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(ROOT)
    # The retest deployment as shipped, with its cache and user folders moved out of the repository
    deployment = yaml.safe_load((ROOT / "config/deployment/local/retest.yaml").read_text(encoding="utf-8"))
    deployment["locations"]["cache"] = str(tmp_path / "cache")
    deployment["locations"]["user_data"] = str(tmp_path / "user")
    path = tmp_path / "retest.yaml"
    path.write_text(yaml.safe_dump(deployment), encoding="utf-8")
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(path))
    monkeypatch.setenv("SPARMVET_APP_FEATURES", "qa")

    gate = Bootloader()

    assert sorted(gate.available_data_analysis_recipes) == ["retest_tier2", "retest_top_n_other"]
    assert sorted(gate.rejected_data_analysis_recipes) == ["retest_bad_select_column", "retest_broken_header"]
    header = " ".join(gate.rejected_data_analysis_recipes["retest_broken_header"]["problems"])
    assert "data_schemas.Genes: dataset cannot be loaded" in header and "predicted_phenotype" in header
    select = " ".join(gate.rejected_data_analysis_recipes["retest_bad_select_column"]["problems"])
    assert 'data_schemas.Genes: dataset cannot be loaded: unable to find column "phenotype"' in select
