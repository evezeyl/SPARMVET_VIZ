"""The orchestrator fails with a message instead of doing something else silently (Eve: "fail instead of warn").

Three behaviours of `DataOrchestrator.materialize_tier1` used to hide a mistake of the recipe:
  - a collection id that is neither a join nor a schema was replaced by the FIRST join of the recipe;
  - a join step that named an ingredient the join does not hold was skipped with a console line;
  - a join whose `ingredients` named no known schema was assembled from ALL the schemas of the recipe.
Each gave a table that looked right and was something else. They fail now and name the id.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_orchestrator_fails_loudly.py -q
"""
import pytest

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import World, bump


@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


def _build(world, collection="C"):
    keys = world.orch.compute_data_analysis_recipe_keys("tiny")
    return world.orch.materialize_tier1("tiny", collection, world.anchor, keys=keys).collect()


def test_the_normal_join_still_builds(tmp_path):
    world = World(tmp_path)
    assert _build(world).height == 3


def test_a_plain_schema_still_builds_as_a_collection(tmp_path):
    world = World(tmp_path)
    assert _build(world, "T").columns == ["sample_id", "group"]


def test_an_unknown_collection_fails_and_is_not_replaced_by_the_first_join(tmp_path):
    world = World(tmp_path)
    with pytest.raises(Exception, match="No_Such_Collection"):
        _build(world, "No_Such_Collection")


def test_a_step_that_names_an_ingredient_the_join_does_not_hold_fails(tmp_path):
    world = World(tmp_path)
    step = {"action": "polars_join", "right_ingredient": "Elsewhere", "on": ["sample_id"], "how": "left", "maintain_order": "left_right"}
    world.write_data_analysis_recipe(steps_tier1=[step])
    with pytest.raises(Exception, match="Elsewhere"):
        _build(world)


def test_a_join_whose_ingredient_is_not_a_schema_fails_and_is_not_built_from_everything(tmp_path):
    world = World(tmp_path)
    entry = world.data_analysis_recipes_dir / "tiny.yaml"
    entry.write_text(entry.read_text().replace("- dataset_id: T", "- dataset_id: Not_A_Schema"))
    bump(entry)
    with pytest.raises(Exception, match="Not_A_Schema"):
        _build(world)
