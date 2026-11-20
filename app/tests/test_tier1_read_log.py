"""HOME-WALK H: a read of a stored Tier 1 table writes one line ("is valid (key match)"); only a build writes "materialize_tier1 START" and "DONE".

The walk of 2026-11-20 counted about 450 START lines in the log of one session although no user action rebuilt a stored table (counted in the browser:
a plot tab, a data choice, a mode and a filter Apply rebuilt nothing; they only read). Edge cases: the first call builds (START and DONE); the second reads
(no START); after the data changed the table is rebuilt (START again).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_tier1_read_log.py -q
"""
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_tier3_reader import Tier3World


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _read(world):
    return world.orch.materialize_tier1("tiny", "C", world.anchors / "C.parquet", keys=world.keys()).collect()


def test_a_build_writes_start_and_done_and_a_read_of_the_stored_table_writes_only_the_validity_line(tmp_path, capsys):
    world = Tier3World(tmp_path)
    _read(world)
    built = capsys.readouterr().out
    assert "materialize_tier1 START" in built and "materialize_tier1 DONE" in built
    _read(world)
    again = capsys.readouterr().out
    assert "is valid (key match)" in again
    assert "materialize_tier1 START" not in again and "materialize_tier1 DONE" not in again


def test_a_changed_input_builds_again_and_says_so(tmp_path, capsys):
    world = Tier3World(tmp_path)
    _read(world)
    capsys.readouterr()
    world.write_data("sample_id\tgroup\tscore\ns1\tA\t9\ns2\tB\t8\n")   # other rows: the key of the data changes
    clear_data_analysis_recipe_cache()
    _read(world)
    out = capsys.readouterr().out
    assert "materialize_tier1 START" in out and "materialize_tier1 DONE" in out and "is valid (key match)" not in out
