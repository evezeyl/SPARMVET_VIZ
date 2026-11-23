"""At start the Bootloader removes the leftover temporary files of killed writers from the store of tables (STALE-KEY-STORE-1).

A writer killed in the middle of a stored table leaves `.<table>.parquet.<random>.tmp` the size of a table. The Bootloader removes
those older than a short age and leaves a recent one (a write in progress by another process) alone. The test starts a REAL Bootloader.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_bootloader_store_cleanup.py -q
"""
import os
import time
from pathlib import Path

import pytest
import yaml

from app.src.bootloader import Bootloader
from transformer.anchor import ORPHAN_AGE_SECONDS

REPO = Path(__file__).resolve().parents[2]


@pytest.fixture(autouse=True)
def clean_launch_env(monkeypatch, tmp_path):
    for var in ("SPARMVET_DEPLOYMENT", "SPARMVET_APP_FEATURES", "SPARMVET_PERSONA", "SPARMVET_PROFILE", "SPARMVET_CONNECTOR",
                "SPARMVET_DATA_ANALYSIS_RECIPE"):
        monkeypatch.delenv(var, raising=False)
    monkeypatch.setenv("HOME", str(tmp_path / "home"))
    (tmp_path / "home").mkdir()
    monkeypatch.chdir(REPO)


def _deployment(tmp_path):
    root = tmp_path / "dep_data"
    locations = {}
    for key in ("raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"):
        (root / key).mkdir(parents=True, exist_ok=True)
        locations[key] = str(root / key)
    path = tmp_path / "dep.yaml"
    path.write_text(yaml.safe_dump({"deployment_type": "filesystem", "default_app_features": "qa",
                                    "locations": locations}))
    return path, root / "user_data" / "anchors"


def _plant(folder: Path, name: str, age_seconds: float) -> Path:
    folder.mkdir(parents=True, exist_ok=True)
    path = folder / name
    path.write_bytes(b"x" * 100)
    when = time.time() - age_seconds
    os.utime(path, (when, when))
    return path


def test_the_start_removes_an_old_leftover_and_keeps_a_fresh_one_and_a_stored_table(tmp_path, monkeypatch):
    dep, anchors = _deployment(tmp_path)
    old = _plant(anchors, ".C.parquet.abc123.tmp", ORPHAN_AGE_SECONDS + 3600)       # a writer killed long ago
    fresh = _plant(anchors, ".C__T2.parquet.def456.tmp", 5)                       # a write in progress by another process
    table = _plant(anchors, "C.parquet", ORPHAN_AGE_SECONDS + 3600)               # a stored table: never touched, however old
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    Bootloader()
    assert not old.exists(), "MUTATION 'cleanup at start removed': the old leftover must be gone after the start"
    assert fresh.exists(), "a recent temporary file may be a write in progress and must be kept"
    assert table.exists()


def test_a_start_with_no_store_folder_yet_does_not_fail(tmp_path, monkeypatch):
    dep, anchors = _deployment(tmp_path)
    assert not anchors.exists()
    monkeypatch.setenv("SPARMVET_DEPLOYMENT", str(dep))
    Bootloader()
