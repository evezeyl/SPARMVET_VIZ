"""Tier 2 is stored as a parquet with a chained key (ADR-089 point 6, fork issue evezeyl/SPARMVET_VIZ#10).

Same tiny data analysis recipe as test_cache_chain.py. Rewrite detection: after the first build both parquet
files get an old modification time; a rewrite shows as a different one.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_tier2_store.py -q
"""
import os

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, tier2_key
from app.modules.orchestrator import TIER2_KEY_META, tier2_path_for
from app.tests.test_cache_chain import FILTER_A, FILTER_B, OLD_MTIME_NS, World
from utils.hashing import get_parquet_metadata_hash


class Tier2World(World):
    def __init__(self, root):
        super().__init__(root)
        self.t2 = tier2_path_for(self.anchor)

    def read_t2(self):
        """One session reads T2: keys first, then the stored file. Returns the rows."""
        keys = self.orch.compute_data_analysis_recipe_keys("tiny")
        lf = self.orch.materialize_tier2("tiny", "C", self.anchor, keys=keys)
        return sorted(lf.collect().to_dicts(), key=lambda r: r["sample_id"])

    def pin_both(self):
        for p in (self.anchor, self.t2):
            if p.exists():
                os.utime(p, ns=(OLD_MTIME_NS, OLD_MTIME_NS))

    @staticmethod
    def rewritten(path):
        return os.stat(path).st_mtime_ns != OLD_MTIME_NS


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


@pytest.fixture
def world(tmp_path):
    """A data analysis recipe whose join has one tier2 step (keep group A), already built once."""
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    rows = w.read_t2()
    assert [r["sample_id"] for r in rows] == ["s1", "s2"]
    w.pin_both()
    return w


def test_tier2_is_written_next_to_tier1_with_its_chained_key(world):
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    assert world.t2.name == "C__T2.parquet" and world.t2.parent == world.anchor.parent
    assert get_parquet_metadata_hash(str(world.t2), TIER2_KEY_META) == tier2_key(keys.tier1_key, [FILTER_A])


def test_nothing_changed_reads_the_stored_file(world):
    rows = world.read_t2()
    assert [r["sample_id"] for r in rows] == ["s1", "s2"]
    assert not world.rewritten(world.t2) and not world.rewritten(world.anchor)


def test_tier2_step_change_recomputes_only_tier2(world):
    world.write_data_analysis_recipe(steps_tier2=[FILTER_B])
    rows = world.read_t2()
    assert [r["sample_id"] for r in rows] == ["s3"]
    assert world.rewritten(world.t2)
    assert not world.rewritten(world.anchor), "a Tier 2 step must not rewrite the Tier 1 file"


def test_tier1_change_recomputes_both(world):
    world.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
    rows = world.read_t2()
    assert [r["sample_id"] for r in rows] == ["s1", "s2", "s4"]
    assert world.rewritten(world.anchor) and world.rewritten(world.t2)


def test_missing_tier2_file_is_recomputed_from_tier1(world):
    world.t2.unlink()
    rows = world.read_t2()
    assert [r["sample_id"] for r in rows] == ["s1", "s2"]
    assert world.t2.exists() and not world.rewritten(world.anchor)


def test_empty_tier2_writes_no_file_and_equals_tier1(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[])
    assert len(w.read_t2()) == 3
    assert not w.t2.exists()


def test_a_stale_tier2_file_is_removed_when_the_steps_are_dropped(world):
    world.write_data_analysis_recipe(steps_tier2=[])
    assert len(world.read_t2()) == 3
    assert not world.t2.exists()


# -- cleanup: no false T2 stays on disk (edge cases) ------------------------------------------

def test_moving_the_tier2_steps_to_tier1_removes_the_tier2_file_without_reading_t2(world):
    """Only Tier 1 is read afterwards: the old T2 must still go, it would be a false T2."""
    world.write_data_analysis_recipe(steps_tier1=[FILTER_A], steps_tier2=[])
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    rows = world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys).collect().to_dicts()
    assert sorted(r["sample_id"] for r in rows) == ["s1", "s2"]
    assert not world.t2.exists()


def test_a_rebuilt_tier1_removes_the_old_tier2_even_when_tier2_is_not_read(world):
    world.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys)
    assert not world.t2.exists()


def test_a_valid_tier1_with_tier2_steps_keeps_the_tier2_file(world):
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys)
    assert world.t2.exists() and not world.rewritten(world.t2)


def test_a_corrupt_tier2_file_is_recomputed(world):
    world.t2.write_bytes(b"not a parquet file")
    rows = world.read_t2()
    assert [r["sample_id"] for r in rows] == ["s1", "s2"]


def test_a_tier2_step_that_removes_every_row_gives_an_empty_but_valid_tier2(world):
    world.write_data_analysis_recipe(steps_tier2=[{"action": "filter_eq", "column": "group", "value": "Z"}])
    assert world.read_t2() == []
    world.pin_both()
    assert world.read_t2() == []
    assert not world.rewritten(world.t2)


# -- the stored file must be readable again (found by the real export download test) ----------

def test_the_stored_tier2_with_categorical_columns_and_nulls_reads_back(tmp_path):
    """Categorical columns (the data analysis recipe default for ids and categories) with missing values.

    The first read computes and writes the file; the second reads it back. A writer whose output
    Polars cannot decode would fail here, and HOME would silently fall back to Tier 1.
    """
    w = Tier2World(tmp_path)
    w.write_data("sample_id\tgroup\ns1\tA\ns2\t\ns3\tA\ns4\tB\n")
    w.write_data_analysis_recipe(steps_tier2=[{"action": "drop_duplicates", "columns": ["sample_id"]}])
    first = w.read_t2()
    assert [r["sample_id"] for r in first] == ["s1", "s2", "s3", "s4"]
    assert first[1]["group"] is None
    w.pin_both()
    second = w.read_t2()                                   # read back from the stored file
    assert second == first and not w.rewritten(w.t2)
    import polars as pl
    assert pl.read_parquet(w.t2).height == 4               # and readable outside the orchestrator
