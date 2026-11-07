"""The same data and data analysis recipe must give the same anchors, in the same row order, every time.

Found on 2026-11-05: two builds of `ST22_Anchor` had the same rows in a different order, because
Polars returned the matches of a many-to-many join in a different order on each run. This test
builds every collection of the shipped test data analysis recipes several times, in empty folders, and
requires identical rows in identical order.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_anchor_determinism.py -q
"""
import shutil
from pathlib import Path

import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager

ROOT = Path(__file__).resolve().parents[2]
DATA_ANALYSIS_RECIPES_DIR = ROOT / "config" / "data_analysis_recipes" / "pipelines"
PROJECTS = ["1_test_data_ST22_dummy", "2_test_data_ST22_dummy"]
BUILDS = 4  # a random order differs between builds


def build_all(project: str, workdir: Path) -> dict[str, list[pl.DataFrame]]:
    """Build every collection of a project BUILDS times, each time in an empty folder."""
    collections = list(ConfigManager(str(DATA_ANALYSIS_RECIPES_DIR / f"{project}.yaml")).raw_config["joins"])
    builds: dict[str, list[pl.DataFrame]] = {c: [] for c in collections}
    for run in range(BUILDS):
        clear_data_analysis_recipe_cache()
        anchors = workdir / f"{project}_run{run}"
        shutil.rmtree(anchors, ignore_errors=True)
        anchors.mkdir(parents=True)
        # source.path of the data analysis recipes is relative to the project root
        orchestrator = DataOrchestrator(DATA_ANALYSIS_RECIPES_DIR, ROOT / "assets" / "test_data")
        keys = orchestrator.compute_project_keys(project)
        for collection in collections:
            lf = orchestrator.materialize_tier1(project, collection, anchors / f"{collection}.parquet", keys=keys)
            builds[collection].append(lf.collect())
    return builds


@pytest.fixture(scope="module")
def built(tmp_path_factory):
    workdir = tmp_path_factory.mktemp("anchors")
    return {project: build_all(project, workdir) for project in PROJECTS}


def _cases():
    for project in PROJECTS:
        for collection in ConfigManager(str(DATA_ANALYSIS_RECIPES_DIR / f"{project}.yaml")).raw_config["joins"]:
            yield pytest.param(project, collection, id=f"{project}-{collection}")


@pytest.mark.parametrize("project,collection", list(_cases()))
def test_every_build_gives_the_same_rows_in_the_same_order(built, project, collection):
    frames = built[project][collection]
    assert len(frames) == BUILDS and frames[0].height > 0
    for later in frames[1:]:
        assert later.equals(frames[0]), (
            f"{project}/{collection}: two builds of the same data and data analysis recipe differ "
            f"(same content when sorted: {later.sort(later.columns).equals(frames[0].sort(frames[0].columns))})")
