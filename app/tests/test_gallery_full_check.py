"""The full check of the gallery examples and the index built from it (spec section 9: G3, D4; DEC47, DEC48).

Every shipped example passes `check_recipe` (profile `gallery`) WITH the registries of the actions and of the plot
components; the library test (`libs/viz_gallery/tests`) runs the structure only. The committed `gallery_index.json`
is the index rebuilt from the examples by this full check; an example that fails is left out with its reason.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gallery_full_check.py -q
"""
import importlib.util
import json
import shutil
import sys
from pathlib import Path

from app.modules.gallery_examples import check_gallery, rebuild_gallery_index, recipe_catalogs

ROOT = Path(__file__).resolve().parents[2]
SHIPPED = ROOT / "assets" / "gallery_data"
RECIPE = "data_analysis_recipe.yaml"
# The examples that cannot be standard recipes yet (the same list as libs/viz_gallery/tests/test_gallery_examples_are_recipes.py).
WAITING = {"beeswarm_sina"}

_spec = importlib.util.spec_from_file_location("refresh_gallery", ROOT / "assets/scripts/refresh_gallery.py")
refresh = importlib.util.module_from_spec(_spec)
sys.modules["refresh_gallery"] = refresh
_spec.loader.exec_module(refresh)


def _copy_of(tmp_path: Path, *names: str) -> Path:
    work = tmp_path / "assets" / "gallery_data"
    for name in names:
        shutil.copytree(SHIPPED / name, work / name)
    return work


def _with_a_wrong_layer(work: Path) -> None:
    """A second example `bar_wrong` whose first layer is not a registered component."""
    shutil.copytree(work / "bar_simple", work / "bar_wrong")
    text = (work / "bar_wrong" / RECIPE).read_text().replace("bar_simple", "bar_wrong").replace("name: geom_bar", "name: geom_barr")
    (work / "bar_wrong" / RECIPE).write_text(text)


def test_the_catalogs_hold_the_registries():
    catalogs = recipe_catalogs()
    assert {"polars_join", "modif_filter"} <= set(catalogs["actions"])
    assert {"geom_bar", "stat_ecdf", "labs", "theme_minimal"} <= catalogs["components"]
    assert "theme_minimal" in catalogs["themes"] and "geom_bar" not in catalogs["themes"]
    assert "fill" in catalogs["component_arguments"]["geom_bar"]


def test_every_shipped_example_passes_the_full_check():
    shipped = check_gallery(SHIPPED)
    assert shipped.coverage == {"structure", "actions", "components"}
    assert set(shipped.rejected) == WAITING, shipped.rejected
    assert set(shipped.accepted) == {d.name for d in SHIPPED.iterdir() if d.is_dir()} - WAITING and len(shipped.accepted) >= 30


def test_the_full_check_finds_what_the_structure_check_cannot(tmp_path):
    work = _copy_of(tmp_path, "bar_simple")
    _with_a_wrong_layer(work)
    examples = check_gallery(work)
    assert list(examples.accepted) == ["bar_simple"]
    assert any("[PS04]" in reason and "geom_bar" in reason for reason in examples.rejected["bar_wrong"])
    index = rebuild_gallery_index(work)
    assert list(index["registry"]) == ["bar_simple"] and list(index["metadata"]["rejected"]) == ["bar_wrong"]


def test_the_committed_index_is_the_index_rebuilt_from_the_examples(tmp_path):
    work = tmp_path / "assets" / "gallery_data"
    shutil.copytree(SHIPPED, work)
    committed = json.loads((SHIPPED / "gallery_index.json").read_text())
    rebuilt = rebuild_gallery_index(work)
    relative = {name: {**entry, "path": f"assets/gallery_data/{name}/{RECIPE}"} for name, entry in rebuilt["registry"].items()}
    assert committed["registry"] == relative
    assert committed["pivot"] == rebuilt["pivot"]
    assert committed["metadata"]["count"] == rebuilt["metadata"]["count"] == len(rebuilt["registry"])
    assert committed["metadata"]["rejected"] == rebuilt["metadata"]["rejected"] and set(committed["metadata"]["rejected"]) == WAITING
    assert committed["metadata"]["coverage"] == rebuilt["metadata"]["coverage"] == ["actions", "components", "structure"]


def test_the_geom_of_the_index_is_read_from_the_layers():
    index = json.loads((SHIPPED / "gallery_index.json").read_text())
    # dumbbell declared geom_segment and draws geom_line first (finding G4): the index says what is drawn
    assert index["registry"]["dumbbell"]["taxonomy"]["geom"] == "geom_line"
    assert "dumbbell" in index["pivot"]["by_geom"]["geom_line"] and "dumbbell" not in index["pivot"]["by_geom"].get("geom_segment", [])


def test_the_refresh_script_reports_without_apply_and_writes_with_apply(tmp_path, capsys):
    work = _copy_of(tmp_path, "bar_simple")
    _with_a_wrong_layer(work)
    assert refresh.main(["--gallery", str(work)]) == 1
    out = capsys.readouterr().out
    assert "Accepted: 1 example(s)." in out and "Left out: bar_wrong" in out and "[PS04]" in out and "Nothing written" in out
    assert not (work / "gallery_index.json").exists()
    assert refresh.main(["--gallery", str(work), "--apply"]) == 1
    assert list(json.loads((work / "gallery_index.json").read_text())["registry"]) == ["bar_simple"]
    shutil.rmtree(work / "bar_wrong")
    assert refresh.main(["--gallery", str(work), "--apply"]) == 0
    assert refresh.main(["--gallery", str(tmp_path / "missing")]) == 2
