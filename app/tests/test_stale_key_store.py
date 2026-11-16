"""A stored table carries the key of the files it was REALLY built from (STALE-KEY-STORE-1, ADR-089).

HOME computes its keys once and keeps them while the recipe or the data change on disk. A table that is not stored yet is
then built from the files of NOW. It must be stored under the key of those files, never under the key HOME holds: the next
read with the held key (or after the author changed the recipe back) would serve the wrong table as valid.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_stale_key_store.py -q
"""
from unittest import mock

import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache, tier2_key
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, tier2_path_for
from app.tests.test_cache_chain import FILTER_A, FILTER_B, World
from utils.hashing import get_parquet_metadata_hash


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def ids(lf):
    return sorted(lf.collect()["sample_id"].to_list())


def stored(path, meta):
    return get_parquet_metadata_hash(str(path), meta)


def test_a_table_built_after_a_recipe_change_is_stored_under_the_key_of_the_new_recipe(tmp_path):
    w = World(tmp_path)
    held = w.orch.compute_data_analysis_recipe_keys("tiny")           # the view is opened
    w.write_data_analysis_recipe(steps_tier1=[FILTER_B])               # the recipe changes under it
    other = w.anchor.parent / "D.parquet"
    rows = ids(w.orch.materialize_tier1("tiny", "C", other, keys=held))
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert rows == ["s3"]
    assert stored(other, TIER1_KEY_META) == now.tier1_key != held.tier1_key


def test_the_author_changes_the_recipe_back_and_the_table_of_the_other_recipe_is_not_served(tmp_path):
    w = World(tmp_path)
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.write_data_analysis_recipe(steps_tier1=[FILTER_B])
    other = w.anchor.parent / "D.parquet"
    w.orch.materialize_tier1("tiny", "C", other, keys=held)           # built from the new recipe
    w.write_data_analysis_recipe()                                     # back to the first text
    back = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert back.tier1_key == held.tier1_key
    assert ids(w.orch.materialize_tier1("tiny", "C", other, keys=back)) == ["s1", "s2", "s3"]


def test_a_table_built_after_a_data_change_is_stored_under_the_key_of_the_new_data(tmp_path):
    w = World(tmp_path)
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
    rows = ids(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=held))
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert rows == ["s1", "s2", "s3", "s4"]
    assert stored(w.anchor, TIER1_KEY_META) == now.tier1_key != held.tier1_key


def test_tier2_built_on_a_new_tier1_is_stored_under_the_chain_of_the_new_tier1(tmp_path):
    w = World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    held = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.write_data_analysis_recipe(steps_tier1=[FILTER_B], steps_tier2=[FILTER_A])    # tier 1 AND tier 2 changed
    rows = ids(w.orch.materialize_tier2("tiny", "C", w.anchor, keys=held))
    now = w.orch.compute_data_analysis_recipe_keys("tiny")
    assert rows == []                                                   # B rows then kept A only: nothing
    t2 = tier2_path_for(w.anchor)
    assert stored(w.anchor, TIER1_KEY_META) == now.tier1_key
    assert stored(t2, TIER2_KEY_META) == tier2_key(now.tier1_key, [FILTER_A])


def test_matching_keys_still_reuse_the_stored_table(tmp_path):
    """The normal path is untouched: keys that match the stored key serve the file, nothing is rebuilt."""
    w = World(tmp_path)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    with mock.patch("app.modules.orchestrator.write_anchor") as writer:
        assert ids(w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)) == ["s1", "s2", "s3"]
    writer.assert_not_called()


def test_a_build_whose_inputs_changed_during_the_build_is_not_stored(tmp_path):
    w = World(tmp_path)
    keys = w.orch.compute_data_analysis_recipe_keys("tiny")
    real = w.orch.prepare_ingredient

    def ingest_then_the_file_changes(*args, **kwargs):
        lf = real(*args, **kwargs)
        w.write_data("sample_id\tgroup\ns1\tA\ns2\tA\ns3\tB\ns4\tA\n")
        return lf

    with mock.patch.object(w.orch, "prepare_ingredient", side_effect=ingest_then_the_file_changes):
        rows = w.orch.materialize_tier1("tiny", "C", w.anchor, keys=keys)
    assert ids(rows)                          # the caller still gets a table
    assert not w.anchor.exists(), "a table built while its inputs changed must not be stored under any key"
