"""The columns of the last `polars_select` step of a join's tier 1 are the column order of the collection, in Tier 1 and in
the stored Tier 2.

Issue evezeyl/SPARMVET_VIZ#86 (then a `final_contract`, removed in recipe format 1, DEC23): the order of the columns of the
published table is part of the Tier 1 key, so a reorder rebuilds Tier 1 and the stored Tier 2. A step list is a list, so
the order is in the key by construction; these tests keep it so.

Same tiny data analysis recipe as test_tier2_store.py.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_select_order.py -q
"""
import pytest

from app.modules import cache_keys
from app.modules.cache_keys import canonical_hash, clear_data_analysis_recipe_cache, tier1_material
from app.tests.test_cache_chain import FILTER_A
from app.tests.test_tier2_store import Tier2World

AB = ["sample_id", "group"]
BA = ["group", "sample_id"]


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
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A], select=AB)
    assert _columns(w) == (["sample_id", "group"], ["sample_id", "group"])
    return w


def test_the_select_order_is_the_column_order_of_tier1_and_tier2(world):
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], select=BA)
    assert _columns(world) == (["group", "sample_id"], ["group", "sample_id"])


def test_reordering_and_going_back_restores_the_first_order(world):
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], select=BA)
    _columns(world)
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], select=AB)
    assert _columns(world) == (["sample_id", "group"], ["sample_id", "group"])


def test_a_stale_tier2_file_does_not_survive_a_reorder(world):
    """The stored Tier 2 is rewritten (or removed) when the order changes, not served as it was."""
    first = world.t2.stat().st_mtime_ns
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], select=BA)
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    world.orch.materialize_tier1("tiny", "C", world.anchor, keys=keys)
    assert not world.t2.exists() or world.t2.stat().st_mtime_ns != first


def test_a_column_removed_from_the_select_is_followed_by_tier2(world):
    """The thing removed, not only moved."""
    world.write_data_analysis_recipe(steps_tier2=[FILTER_A], select=["group"])
    assert _columns(world) == (["group"], ["group"])


def test_without_tier2_steps_the_order_is_followed_and_no_tier2_file_exists(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[], select=AB)
    assert _columns(w) == (["sample_id", "group"], ["sample_id", "group"])
    w.write_data_analysis_recipe(steps_tier2=[], select=BA)
    assert _columns(w) == (["group", "sample_id"], ["group", "sample_id"])
    assert not w.t2.exists()


def test_no_select_keeps_the_assembled_order(tmp_path):
    w = Tier2World(tmp_path)
    w.write_data_analysis_recipe(steps_tier2=[FILTER_A])
    t1, t2 = _columns(w)
    assert t1 == t2 and set(t1) == {"sample_id", "group"}


# -- the key itself: the order of a select is in it, the order of unordered things is not ------

def _raw(order, input_fields):
    return {"id": "r", "data_schemas": {"T": {"input_fields": input_fields}},
            "joins": {"C": {"ingredients": [{"dataset_id": "T"}],
                            "steps": {"tier1": [{"action": "polars_select", "exprs": list(order)}]}}}}


def test_the_tier1_material_depends_on_the_order_of_the_select():
    fields = {"a": {}, "b": {}}
    assert canonical_hash(tier1_material(_raw(AB, fields))) != canonical_hash(tier1_material(_raw(BA, fields)))


def test_the_tier1_material_does_not_depend_on_the_order_of_unordered_things():
    """Category 1 of the specification (named, order means nothing): input_fields."""
    one = _raw(AB, {"a": {"type": "numeric"}, "b": {"type": "utf8"}})
    other = _raw(AB, {"b": {"type": "utf8"}, "a": {"type": "numeric"}})
    assert canonical_hash(tier1_material(one)) == canonical_hash(tier1_material(other))


def test_the_engine_version_was_bumped_for_recipe_format_1():
    assert int(cache_keys.ENGINE_CACHE_VERSION) >= 4
