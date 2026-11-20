"""The table of a plot with tier-3 steps of its own is stored by its key (D-0343, opening-build).

A plot with no tier-3 step reads its Tier 2 table and adds no file (T3 = T2); a join with no tier-2 step has T2 = T1 and adds none. A plot with
tier-3 steps has `<target>__T3_<plot>.parquet`, written once with its key (`sparmvet_tier3_key`, the key of `DataAnalysisRecipeKeys.plot_key_of`)
and read while the key matches.

What is proved, on the staged recipe of `test_tier3_reader.py` (table T, join C, plots `p_steps` with tier-3 steps and `p_plain` without):
- the file exists for `p_steps` only, carries the key of the plot and the cache version, and holds exactly the rows `materialize_tier3` returns;
- a second read builds nothing (a counter of stores) and returns the same rows;
- a change of the plot's own steps rebuilds only that table; a change of the Tier 2 steps rebuilds Tier 2 and Tier 3; a change of the data rebuilds all;
- a file that is missing, a file of another key and a file that cannot be read are rebuilt, never served;
- a plot that loses its tier-3 steps loses its stored table (removed when found); the other plot is untouched;
- a table built while its inputs changed is returned and not stored (the caller is told);
- the audit copy keeps its own folder protocol: a recipe handed in is computed and stored nowhere (PROVISIONAL, see `materialize_tier3`).

Mutation index (each seen failing): MUTATION S1 `materialize_tier3` never stores -> the file and the counter tests fail; MUTATION S2 the stored table is
read without its key -> the changed-step test serves a stale table.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_tier3_store.py -q
"""
from pathlib import Path
from unittest import mock

import polars as pl
import pytest

from app.modules.cache_keys import CACHE_VERSION_META, ENGINE_CACHE_VERSION, clear_data_analysis_recipe_cache
from app.modules.orchestrator import TIER3_KEY_META, tier3_path_for
from app.tests.test_tier3_reader import DROP_GROUP, KEEP_FROM_2, KEEP_FROM_3, KEEP_UP_TO_4, Tier3World


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def stored_files(world) -> list:
    return sorted(p.name for p in world.anchors.iterdir() if p.suffix == ".parquet")


def stores_during(action) -> list:
    """The names of the tables written while `action()` runs: a counter of builds."""
    from transformer import anchor
    written: list = []
    real = anchor.write_anchor

    def counting(lf, path, *args, **kwargs):
        written.append(Path(str(path)).name)
        return real(lf, path, *args, **kwargs)

    with mock.patch("app.modules.orchestrator.write_anchor", side_effect=counting):
        action()
    return sorted(written)


def test_the_stored_table_has_the_key_of_the_plot_and_the_rows_that_are_returned(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    returned = world.table("p_steps")
    path = tier3_path_for(world.anchors, "C", "p_steps")
    assert path.exists() and not tier3_path_for(world.anchors, "C", "p_plain").exists()
    meta = pl.read_parquet_metadata(str(path))
    assert meta[TIER3_KEY_META] == world.keys().plot_key_of("p_steps")
    assert meta[CACHE_VERSION_META] == ENGINE_CACHE_VERSION and meta["sparmvet_decision_hash"] == meta[TIER3_KEY_META]
    assert pl.read_parquet(path).equals(returned)


def test_a_plot_with_no_steps_and_a_join_with_no_tier2_add_no_file(tmp_path):
    world = Tier3World(tmp_path, tier2=[], tier3=None)
    world.table("p_steps")
    world.table("p_plain")
    assert stored_files(world) == ["C.parquet"], "T3 = T2 = T1: one file"


def test_a_second_read_builds_nothing_and_gives_the_same_rows(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    first = world.table("p_steps")
    again: list = []
    stored = stores_during(lambda: again.append(world.table("p_steps")))
    assert stored == [] and again[0].equals(first)


def test_a_change_of_the_plots_own_steps_rebuilds_only_its_table(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2], tier3=[KEEP_FROM_3])
    world.table("p_steps")
    world.write(tier2=[KEEP_FROM_2], tier3=[KEEP_UP_TO_4])
    rows: list = []
    stored = stores_during(lambda: rows.append(world.table("p_steps")))
    assert stored == ["C__T3_p_steps.parquet"], "Tier 1 and Tier 2 are served"
    assert sorted(rows[0]["sample_id"].to_list()) == ["s2", "s3", "s4"], "the new steps are the ones applied, not the stored table of the old ones"


def test_a_change_of_the_tier2_steps_rebuilds_tier2_and_tier3_and_not_tier1(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2], tier3=[DROP_GROUP])
    world.table("p_steps")
    world.write(tier2=[KEEP_FROM_3], tier3=[DROP_GROUP])
    stored = stores_during(lambda: world.table("p_steps"))
    assert stored == ["C__T2.parquet", "C__T3_p_steps.parquet"]


def test_a_changed_data_file_rebuilds_the_three_tables(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    world.table("p_steps")
    world.write_data("sample_id\tgroup\tscore\ns1\tA\t1\ns2\tA\t2\ns3\tB\t3\ns4\tB\t4\ns5\tB\t6\ns6\tB\t7\n")
    clear_data_analysis_recipe_cache()
    rows: list = []
    stored = stores_during(lambda: rows.append(world.table("p_steps")))
    assert stored == ["C.parquet", "C__T2.parquet", "C__T3_p_steps.parquet"]
    assert "s6" in rows[0]["sample_id"].to_list()


@pytest.mark.parametrize("damage", ["missing", "another key", "corrupt"])
def test_a_missing_or_wrong_or_unreadable_file_is_rebuilt_never_served(tmp_path, damage):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    good = world.table("p_steps")
    path = tier3_path_for(world.anchors, "C", "p_steps")
    if damage == "missing":
        path.unlink()
    elif damage == "another key":
        pl.DataFrame({"sample_id": ["zzz"], "score": [9]}).write_parquet(path, metadata={TIER3_KEY_META: "not-this-key", "sparmvet_decision_hash": "not-this-key"})
    else:
        path.write_bytes(b"this is not a parquet file")
    rows: list = []
    stored = stores_during(lambda: rows.append(world.table("p_steps")))
    assert stored == ["C__T3_p_steps.parquet"] and rows[0].equals(good)
    assert pl.read_parquet_metadata(str(path))[TIER3_KEY_META] == world.keys().plot_key_of("p_steps")


def test_a_plot_that_loses_its_tier3_steps_loses_its_stored_table(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    world.table("p_steps")
    assert "C__T3_p_steps.parquet" in stored_files(world)
    world.write(tier2=[KEEP_FROM_2], tier3=None)
    clear_data_analysis_recipe_cache()
    assert world.table("p_steps").height == 4, "it reads its Tier 2 now"
    assert "C__T3_p_steps.parquet" not in stored_files(world), "the file of a table that is not its table any more is removed when found"


def test_a_table_built_while_its_inputs_changed_is_returned_and_not_stored(tmp_path):
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    told: list = []
    real = world.orch.compute_data_analysis_recipe_keys
    calls = {"n": 0}

    def keys_that_move(recipe_id, loaded=None):
        calls["n"] += 1
        found = real(recipe_id, loaded=loaded)
        if calls["n"] > 1:   # the keys asked for to check the table before it is stored: the data changed meanwhile
            world.write_data("sample_id\tgroup\tscore\ns1\tA\t1\n")
        return found

    keys = world.keys()
    with mock.patch.object(world.orch, "compute_data_analysis_recipe_keys", side_effect=keys_that_move):
        table = world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=keys, on_inputs_changed=told.append)
    assert table.collect().height > 0
    assert not tier3_path_for(world.anchors, "C", "p_steps").exists(), "a table that mixes two states of its inputs is not stored"
    assert told, "the caller is told"


def test_a_recipe_handed_in_stores_no_tier3_table(tmp_path):
    from app.modules.cache_keys import load_data_analysis_recipe, loaded_from_resolved
    world = Tier3World(tmp_path, tier2=[KEEP_FROM_2])
    original = load_data_analysis_recipe(world.data_analysis_recipes_dir / "tiny.yaml")
    handed = loaded_from_resolved(original, original.raw)
    keys = world.orch.compute_data_analysis_recipe_keys("tiny", loaded=handed)
    rows = world.orch.materialize_tier3("tiny", "p_steps", world.anchors, keys=keys, loaded=handed).collect()
    assert rows.height > 0
    assert not any("T3" in name for name in stored_files(world)), "the audit copy keeps its own folder protocol"
