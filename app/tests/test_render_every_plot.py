"""Every plot of the shipped test data analysis recipes must render (issue #13).

Found on 2026-11-05: `amr_heatmap` mapped `fill` to a column that does not exist, and nothing
caught it until someone opened the tab. This test builds the dataset of every plot and renders it,
so a mapping to a missing column fails here.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_render_every_plot.py -q
"""
from pathlib import Path

import matplotlib
import pytest

matplotlib.use("Agg")

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from viz_factory.viz_factory import VizFactory

ROOT = Path(__file__).resolve().parents[2]
DATA_ANALYSIS_RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
# figshare_integration is the large one (about 200000 rows); it builds in under a second.
DATA_ANALYSIS_RECIPE_IDS = ["1_test_data_ST22_dummy", "2_test_data_ST22_dummy", "figshare_integration"]


def _plots():
    for data_analysis_recipe in DATA_ANALYSIS_RECIPE_IDS:
        raw = ConfigManager(str(DATA_ANALYSIS_RECIPES_DIR / f"{data_analysis_recipe}.yaml")).raw_config
        for group in raw.get("analysis_groups", {}).values():
            for plot_id, entry in group.get("plots", {}).items():
                yield pytest.param(data_analysis_recipe, plot_id, entry["spec"]["target_dataset"], id=f"{data_analysis_recipe}-{plot_id}")


@pytest.fixture(scope="module")
def anchors(tmp_path_factory):
    return tmp_path_factory.mktemp("anchors")


@pytest.mark.parametrize("data_analysis_recipe,plot_id,target", list(_plots()))
def test_plot_renders(anchors, data_analysis_recipe, plot_id, target):
    clear_data_analysis_recipe_cache()
    raw = ConfigManager(str(DATA_ANALYSIS_RECIPES_DIR / f"{data_analysis_recipe}.yaml")).raw_config
    orchestrator = DataOrchestrator(DATA_ANALYSIS_RECIPES_DIR, ROOT / "assets" / "test_data")
    # The data HOME and the export show: the stored Tier 2 (equal to Tier 1 without tier2 steps).
    # Read twice: the first call writes the file, the second reads it back, so a stored file that
    # cannot be read again fails here (found by the export download test, 2026-11-06).
    keys = orchestrator.compute_data_analysis_recipe_keys(data_analysis_recipe)
    tier1_path = anchors / f"{data_analysis_recipe}_{target}.parquet"
    orchestrator.materialize_tier2(data_analysis_recipe, target, tier1_path, keys=keys).collect()
    lf = orchestrator.materialize_tier2(data_analysis_recipe, target, tier1_path, keys=keys)
    assert lf.head(1).collect().height == 1, f"{target} has no rows"
    plot = VizFactory().render(lf, raw, plot_id)
    plot.draw()
    # A plot that asks for panels must have them (issue #65: facet_by in mapping used to be ignored without a message).
    spec = next(g["plots"][plot_id]["spec"] for g in raw["analysis_groups"].values() if plot_id in g["plots"])
    asks_for_panels = (
        spec.get("facet_by")
        or (spec.get("mapping") or {}).get("facet_by")
        or any(str(layer.get("name", "")).startswith(("facet_wrap", "facet_grid")) for layer in spec.get("layers", []))
    )
    if asks_for_panels:
        assert type(plot.facet).__name__ != "facet_null", f"{plot_id} asks for panels and has none"
