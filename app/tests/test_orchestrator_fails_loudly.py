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


# -- a join keeps the types the recipe declares (JOIN-KEY-TYPES-1, Eve 2026-11-14) -----------------
# The orchestrator used to cast every join key to String before the join, behind the recipe author's back.
# It does not any more: the tables are joined with the types their input_fields declare, and two sides with
# different types fail with a message that names the recipe, the join, the step, the columns and the fix.

def _two_tables(tmp_path, left_type="Categorical", right_type="Categorical", right_key="sample_id", extra_step=""):
    """The tiny recipe with a second table R, joined to T on sample_id (or on T.sample_id = R.<right_key>)."""
    world = World(tmp_path)
    (world.data_dir / "R.tsv").write_text(f"{right_key}\tyear\ns1\t2020\ns2\t2021\ns3\t2022\n")
    on = "'on': [sample_id]" if right_key == "sample_id" else f"left_on: [sample_id]\n          right_on: [{right_key}]"
    entry = world.data_analysis_recipes_dir / "tiny.yaml"
    entry.write_text(f"""id: tiny
info: {{label: Tiny}}
data_schemas:
  T:
    source: {{type: local_tsv, path: {world.data_file}}}
    null_values: []
    strip: false
    input_fields:
      sample_id: {{original_name: sample_id, type: {left_type}, label: Sample, is_entity_key: true}}
      group: {{original_name: group, type: Categorical, label: Group}}
    wrangling: {{tier1: [], tier2: []}}
  R:
    source: {{type: local_tsv, path: {world.data_dir / "R.tsv"}}}
    null_values: []
    strip: false
    input_fields:
      {right_key}: {{original_name: {right_key}, type: {right_type}, label: Sample}}
      year: {{original_name: year, type: Int64, label: Year}}
    wrangling: {{tier1: [], tier2: []}}
joins:
  C:
    ingredients:
      - dataset_id: T
      - dataset_id: R
    steps:
      tier1:
        {extra_step}
        - action: polars_join
          right_ingredient: R
          {on}
          how: left
          maintain_order: left_right
      tier2: []
analysis_groups:
  g:
    label: G
    plots:
      p:
        label: P
        spec:
          target_dataset: C
          mapping: {{x: group}}
          layers:
            - name: geom_bar
              params: {{}}
""")
    bump(entry)
    return world


@pytest.mark.parametrize("declared", ["Categorical", "String"])
def test_a_join_keeps_the_declared_type_of_the_key(tmp_path, declared):
    result = _build(_two_tables(tmp_path, declared, declared))
    assert str(result.schema["sample_id"]) == declared
    assert result["year"].to_list() == [2020, 2021, 2022]


def test_a_join_of_a_string_key_and_a_categorical_key_fails_and_says_how_to_fix_it(tmp_path):
    with pytest.raises(Exception) as caught:
        _build(_two_tables(tmp_path, "String", "Categorical"))
    text = f"{caught.value} {getattr(caught.value, 'tip', '')}"
    for part in ("tiny", "'C'", "step 0", "sample_id", "String", "Categorical", "'R'", "input_fields", "polars_cast"):
        assert part in text, f"{part!r} is not in: {text}"


def test_a_join_with_left_on_right_on_of_different_types_fails(tmp_path):
    with pytest.raises(Exception) as caught:
        _build(_two_tables(tmp_path, "String", "Categorical", right_key="Gene_name"))
    assert "key types differ" in str(caught.value) and "sample_id" in str(caught.value) and "Gene_name" in str(caught.value)


def test_a_join_with_left_on_right_on_of_equal_types_builds(tmp_path):
    result = _build(_two_tables(tmp_path, "String", "String", right_key="Gene_name"))
    assert result["year"].to_list() == [2020, 2021, 2022]


def test_a_cast_step_in_the_recipe_is_how_a_type_is_changed(tmp_path):
    cast_step = "- {action: polars_cast, columns: [sample_id], dtype: String}"
    result = _build(_two_tables(tmp_path, "Categorical", "String", extra_step=cast_step))
    assert str(result.schema["sample_id"]) == "String"
