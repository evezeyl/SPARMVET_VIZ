"""Characterization of the gallery bundle layout and its index (ADR-037, ADR-091).

Written against the file names of 2026-11-07 (data_analysis_recipe.yaml, recipe_meta.md). The
configuration rename (issue evezeyl/SPARMVET_VIZ#27) renames the bundle files and
regenerates gallery_index.json, which stores the path of each bundle file.
"""
import json
import shutil
from pathlib import Path

import polars as pl
import pytest
import yaml

from viz_gallery.gallery_manager import GalleryManager

SHIPPED = Path(__file__).resolve().parents[3] / "assets" / "gallery_data"
BUNDLE_FILES = ("data_analysis_recipe.yaml", "example_data.tsv", "recipe_meta.md")
TAXONOMY = {"family", "pattern", "difficulty", "geom", "show", "sample_size"}


def _bundles(root):
    return sorted(d for d in root.iterdir() if d.is_dir() and (d / BUNDLE_FILES[0]).exists())


def test_submit_writes_the_bundle_files(tmp_path):
    gm = GalleryManager(str(tmp_path))
    folder = Path(gm.submit_recipe(
        "My Plot", recipe=[], data=pl.DataFrame({"a": [1, 2], "b": ["x", "y"]}),
        meta_markdown="## My Plot\n", geom="geom_point"))
    for name in BUNDLE_FILES:
        assert (folder / name).exists(), name
    info = yaml.safe_load((folder / BUNDLE_FILES[0]).read_text())["info"]
    assert info["name"] == "My Plot" and info["geom"] == "geom_point"


def test_every_shipped_bundle_has_the_required_files():
    bundles = _bundles(SHIPPED)
    assert len(bundles) >= 30
    for d in bundles:
        for name in BUNDLE_FILES:
            assert (d / name).exists(), f"{d.name} lacks {name}"


def test_rebuild_index_lists_every_shipped_bundle(tmp_path):
    work = tmp_path / "gallery"
    shutil.copytree(SHIPPED, work)
    (work / "gallery_index.json").unlink(missing_ok=True)
    index = GalleryManager(str(work)).rebuild_index()
    on_disk = {d.name for d in _bundles(work)}
    assert set(index["registry"]) == on_disk
    assert index["metadata"]["count"] == len(on_disk)
    for entry in index["registry"].values():
        assert set(entry["taxonomy"]) == TAXONOMY
        assert entry["path"].endswith(BUNDLE_FILES[0])
    saved = json.loads((work / "gallery_index.json").read_text())
    assert set(saved["registry"]) == on_disk


def test_bundle_without_meta_is_left_out_of_the_index(tmp_path):
    work = tmp_path / "gallery"
    work.mkdir()
    keep = next(iter(_bundles(SHIPPED)))
    shutil.copytree(keep, work / "complete")
    shutil.copytree(keep, work / "no_meta")
    (work / "no_meta" / "recipe_meta.md").unlink()
    index = GalleryManager(str(work)).rebuild_index()
    assert list(index["registry"]) == ["complete"]


def test_empty_gallery_gives_an_empty_index(tmp_path):
    index = GalleryManager(str(tmp_path / "empty")).rebuild_index()
    assert index["registry"] == {} and index["metadata"]["count"] == 0


def test_shipped_index_matches_the_bundles_on_disk():
    saved = json.loads((SHIPPED / "gallery_index.json").read_text())
    assert set(saved["registry"]) == {d.name for d in _bundles(SHIPPED)}
