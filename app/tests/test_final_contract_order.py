"""The key order of a join's final_contract is the column order of the collection, in Tier 1 and in the stored Tier 2.

Issue evezeyl/SPARMVET_VIZ#86; specification `.claude/design/recipe_format_spec.md` section 5 (category 3: named, and the
order is meaning). Before the fix the Tier 1 key was made from a sorted JSON form, so reversing the keys of
final_contract changed the columns of Tier 1 (the projection is applied at every read) but not the stored Tier 2.

Same tiny data analysis recipe as test_tier2_store.py.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_final_contract_order.py -q
"""
import pytest

from app.modules import cache_keys
from app.modules.cache_keys import canonical_hash, clear_data_analysis_recipe_cache, tier1_material
from app.tests.test_cache_chain import FILTER_A
from app.tests.test_tier2_store import Tier2World

AB = {"sample_id": {}, "group": {}}
BA = {"group": {}, "sample_id": {}}


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _columns(world):
    """One session reads T1 then T2 of collection C: returns (T1 columns, T2 columns)."""
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    t1 = world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys).collect().columns
    t2 = world.orch.materialize_tier2("tiny", "C", world.anchor, keys=keys).collect().columns
    return t1, t2


@pytest.fixture
def world(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A], final_contract=AB)
    assert _columns(w) == (["sample_id", "group"], ["sample_id", "group"])
    return w


def test_the_contract_order_is_the_column_order_of_tier1_and_tier2(world):
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], final_contract=BA)
    assert _columns(world) == (["group", "sample_id"], ["group", "sample_id"])


def test_reordering_and_going_back_restores_the_first_order(world):
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], final_contract=BA)
    _columns(world)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], final_contract=AB)
    assert _columns(world) == (["sample_id", "group"], ["sample_id", "group"])


def test_a_stale_tier2_file_does_not_survive_a_reorder(world):
    """The stored Tier 2 is rewritten (or removed) when the order changes, not served as it was."""
    first = world.t2.stat().st_mtime_ns
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], final_contract=BA)
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys)
    assert not world.t2.exists() or world.t2.stat().st_mtime_ns != first


def test_a_column_removed_from_the_contract_is_followed_by_tier2(world):
    """The thing removed, not only moved."""
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], final_contract={"group": {}})
    assert _columns(world) == (["group"], ["group"])


def test_without_tier2_steps_the_order_is_followed_and_no_tier2_file_exists(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[], final_contract=AB)
    assert _columns(w) == (["sample_id", "group"], ["sample_id", "group"])
    w.write_data_analysis_recipe(steps_tier2=[], final_contract=BA)
    assert _columns(w) == (["group", "sample_id"], ["group", "sample_id"])
    assert not w.t2.exists()


def test_no_contract_keeps_the_assembled_order(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    t1, t2 = _columns(w)
    assert t1 == t2 and set(t1) == {"sample_id", "group"}


# -- the key itself: the order of a contract is in it, the order of unordered things is not ------

def _raw(contract, input_fields):
    return {"id": "r", "data_schemas": {"T": {"input_fields": input_fields}},
            "joins": {"C": {"ingredients": [{"dataset_id": "T"}], "final_contract": contract}}}


def test_the_tier1_material_depends_on_the_order_of_the_contract():
    fields = {"a": {}, "b": {}}
    assert canonical_hash(tier1_material(_raw(AB, fields))) != canonical_hash(tier1_material(_raw(BA, fields)))


def test_the_tier1_material_does_not_depend_on_the_order_of_unordered_things():
    """Category 1 of the specification (named, order means nothing): input_fields."""
    one = _raw(AB, {"a": {"type": "numeric"}, "b": {"type": "utf8"}})
    other = _raw(AB, {"b": {"type": "utf8"}, "a": {"type": "numeric"}})
    assert canonical_hash(tier1_material(one)) == canonical_hash(tier1_material(other))


def test_the_engine_version_was_bumped_with_the_key_rule():
    assert int(cache_keys.ENGINE_CACHE_VERSION) >= 3
