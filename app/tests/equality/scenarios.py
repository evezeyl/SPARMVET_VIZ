"""The data sets the equality check runs on, and the engine result of each (EQUALITY-CHECK-1, PROVISIONAL)."""
from functools import lru_cache
from pathlib import Path

from app.tests.equality import reference_2_test_data_ST22_dummy as reference
from app.tests.equality.engine_black_box import EngineResult, run_engine

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[2]
SHIPPED_DATA = ROOT / "assets/test_data/1_test_data_ST22_dummy"
FILE_NAMES = {
    "metadata": "test_metadata_20260307_105756.tsv",
    "amr": "test_data_ResFinder_20260307_105756.tsv",
    "plasmid": "test_data_PlasmidFinder_20260307_105756.tsv",
}

# name -> (recipes folder, recipe id, data folder, the recipe's `null_values`)
SCENARIOS = {
    "clean": (ROOT / "config/data_analysis_recipes/pipelines", "2_test_data_ST22_dummy", SHIPPED_DATA, []),
    "dirty": (HERE / "recipes", "2_test_data_ST22_dummy_dirty", HERE / "data/dirty", [""]),
    "emptied": (HERE / "recipes", "2_test_data_ST22_dummy_emptied", HERE / "data/emptied", [""]),
    "dirty_no_null_text": (HERE / "recipes", "2_test_data_ST22_dummy_dirty_no_null_text", HERE / "data/dirty", []),
    "fractional_year": (HERE / "recipes", "2_test_data_ST22_dummy_fractional_year", HERE / "data/fractional_year", [""]),
}
SCHEMA_TABLES = ["metadata_schema", "amr_data", "plasmid_data"]
JOIN_TABLES = ["AMR_Profile_Joint", "Plasmid_Profile_Joint"]
ALL_TABLES = SCHEMA_TABLES + JOIN_TABLES
PLOTS = reference.PLOT_TARGETS


def files_of(scenario: str) -> dict[str, Path]:
    return {key: SCENARIOS[scenario][2] / name for key, name in FILE_NAMES.items()}


def hand_table(scenario: str, name: str):
    """One hand-written table of a scenario; raises when the recipe's meaning cannot be applied to the data."""
    return _hand_table(scenario, name)


@lru_cache(maxsize=None)
def _hand_table(scenario: str, name: str):
    return reference.reference_table(name, files_of(scenario), SCENARIOS[scenario][3])


@lru_cache(maxsize=None)
def engine_result(scenario: str) -> EngineResult:
    recipes_dir, recipe_id, _, _ = SCENARIOS[scenario]
    return run_engine(recipes_dir, recipe_id, ALL_TABLES, PLOTS)
