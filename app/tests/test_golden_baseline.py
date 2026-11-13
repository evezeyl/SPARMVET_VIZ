"""The golden baseline: the tables of the shipped recipes must not move (GOLDEN-BASELINE-1, P0).

`assets/scripts/golden_baseline.py` records the T1 table, the T2 table and the table of every plot of the
shipped recipes (rows, ordered columns and types, a content hash). The recipe migration (run A) must be
result-identical: this test fails the day a table changes. It also proves that the check can fail:
a changed data value, a changed tier-2 step and a changed column order each give a difference.

When a table is meant to change (a decision of Eve, for example `na` for the filters), regenerate the file
and say why in the commit message:
  PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --out app/tests/golden/baseline.json

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_golden_baseline.py -q
"""
import importlib.util
import json
from pathlib import Path

import polars as pl
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import FILTER_A, FILTER_B, World

ROOT = Path(__file__).resolve().parents[2]
BASELINE = ROOT / "app" / "tests" / "golden" / "baseline.json"


def _load_script():
    spec = importlib.util.spec_from_file_location("golden_baseline", ROOT / "assets" / "scripts" / "golden_baseline.py")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


gb = _load_script()


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _record(world):
    return {"polars": pl.__version__, "recipes": {"tiny": gb.build_recipe("tiny", world.data_analysis_recipes_dir, world.data_dir, True)}}


# -- the table record ------------------------------------------------------------------------

def test_the_record_keeps_row_order_and_column_order():
    a = pl.DataFrame({"x": [1, 2], "y": ["a", "b"]})
    assert gb.table_record(a) == gb.table_record(a.clone())
    assert gb.table_record(a)["sha256"] != gb.table_record(a.reverse())["sha256"]
    assert gb.table_record(a)["sha256"] != gb.table_record(a.select("y", "x"))["sha256"]


def test_the_record_sees_the_type():
    ints = pl.DataFrame({"x": [1, 2]})
    floats = pl.DataFrame({"x": [1.0, 2.0]})
    assert gb.table_record(ints)["columns"] != gb.table_record(floats)["columns"]


# -- the check can fail (a test that cannot fail proves nothing) ------------------------------

def test_a_world_that_did_not_change_is_identical(tmp_path):
    world = World(tmp_path)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    before = _record(world)
    clear_data_analysis_recipe_cache()
    assert gb.differences(before, _record(world)) == []


def test_a_changed_data_value_is_a_difference(tmp_path):
    world = World(tmp_path)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    before = _record(world)
    world.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tC\n")
    clear_data_analysis_recipe_cache()
    found = gb.differences(before, _record(world))
    assert any("t1 C" in line for line in found), found


def test_a_changed_tier2_step_changes_only_what_it_changes(tmp_path):
    world = World(tmp_path)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    before = _record(world)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_B])
    clear_data_analysis_recipe_cache()
    found = gb.differences(before, _record(world))
    assert any("t2 C" in line for line in found), found
    assert not any("t1 C" in line for line in found), "the Tier 1 table did not change"


def test_a_changed_column_order_is_a_difference(tmp_path):
    """Ingestion keeps the order of the file, so the same data with swapped columns is another table."""
    world = World(tmp_path)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    before = _record(world)
    world.write_data("group\tsample_id\nA\ts1\nA\ts2\nB\ts3\n")
    clear_data_analysis_recipe_cache()
    found = gb.differences(before, _record(world))
    assert any("t1 C" in line for line in found), found


def test_a_recipe_that_fails_must_keep_failing_the_same_way():
    expected = {"polars": "x", "recipes": {"r": {"load": {"error": "A: one"}}}}
    assert gb.differences(expected, {"polars": "x", "recipes": {"r": {"load": {"error": "A: one"}}}}) == []
    assert gb.differences(expected, {"polars": "x", "recipes": {"r": {"load": {"error": "A: two"}}}})
    assert gb.differences(expected, {"polars": "x", "recipes": {"r": {"t1": {}, "t2": {}, "plots": {}}}})


# -- the shipped recipes ----------------------------------------------------------------------

def test_the_shipped_recipes_still_build_the_same_tables():
    expected = json.loads(BASELINE.read_text(encoding="utf-8"))
    assert len(expected["recipes"]) >= 7, "the baseline lost recipes"
    found = gb.build(ROOT / expected["recipes_dir"], ROOT / expected["raw_data"], sorted(expected["recipes"]), with_plots=True)
    problems = gb.differences(expected, found)
    assert problems == [], "\n".join(problems)
