"""The engine of a tier is an argument of the key of that tier; the plot engine is in no table key (D-0240, D-0003, ADR-089).

The rule (one sentence): a key holds the engine of what it stores, and nothing else.
  - the tier-1 key holds the effective tier-1 engine of every table and join (the tier's own `data_engine`, else the recipe's);
  - the tier-2 key holds the effective tier-2 engine of its collection, and chains on the tier-1 key;
  - the plot engine (the recipe's or a plot entry's) is in no table key;
  - a later stage's engine never moves the key of an earlier stage.

The key functions only compare values, so a second engine is a stand-in string here ("engine-x"); the real engines of the app
are in `utils.engines`. Pure tests (a dictionary stands for the resolved recipe), then the same on recipe files.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_engine_keys.py -q
"""
import copy

import pytest

from app.modules import cache_keys
from app.modules.cache_keys import (
    canonical_hash, collection_tier2_key, tier1_engines, tier1_key, tier1_material, tier2_engine, tier2_key,
)

POLARS = "python-polars"
STAND_IN = "engine-x"
FILTER = {"action": "modif_filter", "column": "group", "op": "eq", "value": "A", "na": "remove"}
DATA = "batch-1"


def recipe() -> dict:
    """Two tables (A, B), a join J of them with a tier 2, a table C plotted directly with its own tier 2, a plot on each."""
    return {
        "id": "r",
        "data_engine": POLARS,
        "plot_engine": "python-plotnine",
        "data_schemas": {
            "A": {"input_fields": {"x": {"type": "utf8"}}, "tier1": {"steps": [FILTER]}},
            "B": {"input_fields": {"x": {"type": "utf8"}}, "tier1": {"steps": []}},
            "C": {"input_fields": {"x": {"type": "utf8"}}, "tier1": {"steps": []}, "tier2": {"steps": [FILTER]}},
        },
        "joins": {"J": {"ingredients": [{"dataset_id": "A"}, {"dataset_id": "B"}], "tier1": {"steps": []},
                        "tier2": {"steps": [FILTER]}}},
        "analysis_groups": {"g": {"ui_label": "G", "plots": {
            "pj": {"target_dataset": "J", "mapping": {"x": "x"}, "layers": [{"name": "geom_bar", "params": {}}]},
            "pc": {"target_dataset": "C", "mapping": {"x": "x"}, "layers": [{"name": "geom_bar", "params": {}}]}}}},
    }


def keys(raw: dict, data=DATA) -> dict:
    """What a session computes: the tier-1 key of the recipe and the tier-2 key of each collection that has tier-2 steps."""
    t1 = tier1_key(canonical_hash(tier1_material(raw)), data, tier1_engines(raw))
    return {"tier1": t1, "J": collection_tier2_key(raw, "J", t1), "C": collection_tier2_key(raw, "C", t1)}


def moved(before: dict, after: dict) -> set:
    return {name for name in before if before[name] != after[name]}


# --- the engine of a tier is in the key of that tier ----------------------------------------------------------------------


def test_a_changed_tier1_engine_of_a_table_moves_the_tier1_key_and_every_tier2_key_after_it():
    before = recipe()
    after = copy.deepcopy(before)
    after["data_schemas"]["A"]["tier1"]["data_engine"] = STAND_IN
    assert moved(keys(before), keys(after)) == {"tier1", "J", "C"}


def test_a_changed_tier1_engine_of_a_join_moves_the_tier1_key_and_the_tier2_keys():
    before = recipe()
    after = copy.deepcopy(before)
    after["joins"]["J"]["tier1"]["data_engine"] = STAND_IN
    assert moved(keys(before), keys(after)) == {"tier1", "J", "C"}


def test_the_tier1_key_is_one_per_recipe_so_a_tier1_engine_moves_the_key_of_every_table_PROVISIONAL():
    """PROVISIONAL, the brief asked "no key of another table that does not depend on it". ADR-089 as built has ONE tier-1 key for the
    whole recipe (`DataAnalysisRecipeKeys.tier1_key`, the fail-safe rule: a part that cannot be assigned to a table is part of
    Tier 1), so the engine of table A moves the key that table B and table C are stored under too. A key per table is ADR-101 (the
    series of labelled parts), not built. This test pins today's behaviour so that the day ADR-101 is built it is changed on purpose."""
    before = recipe()
    after = copy.deepcopy(before)
    after["data_schemas"]["B"]["tier1"]["data_engine"] = STAND_IN   # B is read by J only; C reads nothing of B
    assert keys(before)["tier1"] != keys(after)["tier1"]
    assert keys(before)["C"] != keys(after)["C"]     # chained on the one tier-1 key


def test_a_changed_tier2_engine_moves_only_the_tier2_key_of_that_collection():
    before = recipe()
    after = copy.deepcopy(before)
    after["joins"]["J"]["tier2"]["data_engine"] = STAND_IN
    assert moved(keys(before), keys(after)) == {"J"}


def test_a_changed_tier2_engine_of_a_table_plotted_directly_moves_only_its_tier2_key():
    before = recipe()
    after = copy.deepcopy(before)
    after["data_schemas"]["C"]["tier2"]["data_engine"] = STAND_IN
    assert moved(keys(before), keys(after)) == {"C"}


def test_a_tier2_engine_is_not_in_the_tier1_material_so_tier1_is_not_rebuilt_for_it():
    before = recipe()
    after = copy.deepcopy(before)
    after["joins"]["J"]["tier2"]["data_engine"] = STAND_IN
    assert tier1_material(before) == tier1_material(after)
    assert tier1_engines(before) == tier1_engines(after)


def test_a_tier2_with_no_steps_has_no_key_whatever_its_engine():
    """T2 equals T1 and nothing is stored (ADR-089 point 6): an engine written on an empty tier 2 makes no key."""
    raw = recipe()
    raw["joins"]["J"]["tier2"] = {"data_engine": STAND_IN, "steps": []}
    assert collection_tier2_key(raw, "J", "T1") == ""
    raw["joins"]["J"].pop("tier2")
    assert collection_tier2_key(raw, "J", "T1") == ""


# --- the plot engine is in no table key ------------------------------------------------------------------------------------


def test_a_changed_plot_engine_of_the_recipe_moves_no_table_key():
    before = recipe()
    after = copy.deepcopy(before)
    after["plot_engine"] = STAND_IN
    assert keys(before) == keys(after)


def test_a_plot_engine_written_on_a_plot_entry_moves_no_table_key():
    before = recipe()
    after = copy.deepcopy(before)
    after["analysis_groups"]["g"]["plots"]["pj"]["plot_engine"] = STAND_IN
    assert keys(before) == keys(after)


def test_a_plot_engine_removed_from_the_recipe_moves_no_table_key():
    before = recipe()
    after = copy.deepcopy(before)
    del after["plot_engine"]
    assert keys(before) == keys(after)


# --- the recipe's engine is the default of a tier, and a later stage never moves an earlier key ----------------------------


def test_a_tier_with_no_engine_of_its_own_takes_the_recipes_and_the_key_is_the_same_as_when_it_is_written_on_the_tier():
    """The plan (3.2) says the key holds "the effective data engine" (the default and any override): the same value, written
    on the tier or inherited, is the same engine and so the same key. (Verified: `utils.engines.tier_engine`, also what the
    orchestrator runs.)"""
    inherited = recipe()
    written = copy.deepcopy(inherited)
    for table in written["data_schemas"].values():
        table["tier1"]["data_engine"] = POLARS
    written["joins"]["J"]["tier1"]["data_engine"] = POLARS
    written["joins"]["J"]["tier2"]["data_engine"] = POLARS
    written["data_schemas"]["C"]["tier2"]["data_engine"] = POLARS
    assert keys(inherited) == keys(written)


def test_the_recipe_engine_is_the_default_of_every_tier_so_changing_it_moves_every_key():
    before = recipe()
    after = copy.deepcopy(before)
    after["data_engine"] = STAND_IN
    assert moved(keys(before), keys(after)) == {"tier1", "J", "C"}


def test_changing_the_recipe_engine_does_not_move_the_tier1_key_of_a_recipe_whose_tier1s_all_name_their_own():
    """A later stage's engine does not move an earlier key: when every tier 1 names its engine, the recipe's value only
    decides the tier-2 engines that name none."""
    before = recipe()
    for table in before["data_schemas"].values():
        table["tier1"]["data_engine"] = POLARS
    before["joins"]["J"]["tier1"]["data_engine"] = POLARS
    after = copy.deepcopy(before)
    after["data_engine"] = STAND_IN
    assert moved(keys(before), keys(after)) == {"J", "C"}


def test_a_recipe_whose_every_tier_names_its_own_engine_is_not_moved_by_the_recipe_engine():
    """The recipe's engine is only a default: where every tier writes its own, changing the default moves no key."""
    before = recipe()
    for table in before["data_schemas"].values():
        table["tier1"]["data_engine"] = POLARS
    before["joins"]["J"]["tier1"]["data_engine"] = POLARS
    before["joins"]["J"]["tier2"]["data_engine"] = POLARS
    before["data_schemas"]["C"]["tier2"]["data_engine"] = POLARS
    after = copy.deepcopy(before)
    after["data_engine"] = STAND_IN
    assert keys(before) == keys(after)


def test_a_tier2_that_names_its_own_engine_follows_its_tier1_key_but_not_the_recipe_engine():
    """The tier-2 key chains on the tier-1 key, so a tier 1 that takes the recipe's engine moves it; the tier-2 engine itself is
    its own value, not the recipe's."""
    before = recipe()
    before["joins"]["J"]["tier2"]["data_engine"] = POLARS
    after = copy.deepcopy(before)
    after["data_engine"] = STAND_IN
    assert tier2_engine(before, "J") == tier2_engine(after, "J") == POLARS
    assert tier2_engine(after, "C") == STAND_IN


# --- the effective engines, read by the function the orchestrator runs ------------------------------------------------------


def test_the_effective_tier1_engines_are_listed_for_every_table_and_join():
    raw = recipe()
    raw["data_schemas"]["B"]["tier1"]["data_engine"] = STAND_IN
    assert tier1_engines(raw) == {"A": POLARS, "B": STAND_IN, "C": POLARS, "J": POLARS}


def test_the_effective_tier2_engine_of_a_collection_is_its_own_else_the_recipes():
    raw = recipe()
    raw["joins"]["J"]["tier2"]["data_engine"] = STAND_IN
    assert tier2_engine(raw, "J") == STAND_IN
    assert tier2_engine(raw, "C") == POLARS


def test_a_recipe_that_names_no_engine_gives_a_key_that_says_so_and_never_a_default():
    """The checker refuses a recipe with no engine (T04); the key does not invent one: it holds None, so the same recipe with the
    engine written has another key."""
    bare = recipe()
    del bare["data_engine"]
    assert set(tier1_engines(bare).values()) == {None}
    assert keys(bare) != keys(recipe())


def test_a_tier_written_as_a_list_or_not_at_all_does_not_break_the_keys():
    raw = recipe()
    raw["data_schemas"]["A"]["tier1"] = [FILTER]      # the old shape, refused by the checker, never keyed by a default
    del raw["data_schemas"]["B"]["tier1"]
    assert tier1_engines(raw)["A"] == POLARS and tier1_engines(raw)["B"] == POLARS
    assert isinstance(keys(raw)["tier1"], str)


# --- the key functions take the engine as an argument ----------------------------------------------------------------------


@pytest.mark.parametrize("name", ["tier1", "tier2"])
def test_every_key_function_changes_with_the_engine_it_is_given(name):
    if name == "tier1":
        one = tier1_key("material", DATA, {"A": POLARS})
        other = tier1_key("material", DATA, {"A": STAND_IN})
    else:
        one = tier2_key("T1", [FILTER], POLARS)
        other = tier2_key("T1", [FILTER], STAND_IN)
    assert one != other


def test_no_two_engines_give_the_same_key_for_the_same_steps():
    engines = ["python-polars", "engine-x", "engine-y", "", None]
    produced = {tier2_key("T1", [FILTER], e) for e in engines}
    assert len(produced) == len(engines)


def test_the_tier1_key_does_not_depend_on_the_order_the_engines_are_listed_in():
    assert tier1_key("m", DATA, {"A": POLARS, "B": STAND_IN}) == tier1_key("m", DATA, {"B": STAND_IN, "A": POLARS})


# --- the same recipe and data give the same keys, always -------------------------------------------------------------------


def test_the_same_recipe_and_data_give_the_same_keys_twice():
    assert keys(recipe()) == keys(recipe())
    assert keys(recipe()) == keys(copy.deepcopy(recipe()))


def test_the_same_recipe_with_another_key_order_gives_the_same_keys():
    shuffled = dict(reversed(list(recipe().items())))
    assert keys(recipe()) == keys(shuffled)


def test_other_data_gives_other_keys():
    assert moved(keys(recipe(), "d1"), keys(recipe(), "d2")) == {"tier1", "J", "C"}


# --- the cache version ------------------------------------------------------------------------------------------------------


def test_the_cache_version_is_5_and_a_version_4_key_is_another_key(monkeypatch):
    assert cache_keys.ENGINE_CACHE_VERSION == "5"
    raw = recipe()
    now = keys(raw)
    monkeypatch.setattr(cache_keys, "ENGINE_CACHE_VERSION", "4")
    assert moved(now, keys(raw)) == {"tier1", "J", "C"}
