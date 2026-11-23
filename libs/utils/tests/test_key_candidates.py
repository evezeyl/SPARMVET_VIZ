"""The columns that may identify a row of a result table, read from the recipe (candidates only: `table_compare.compare` verifies them on the data).

Small recipe dictionaries show each rule and its edges; the demo recipe is read (never changed) to show the four kinds of table of the trials of
2026-11-22. The name and place of the key that a recipe author MAY declare are NOT decided (D-0489): the format, the spec and the checker do not know it,
so the library reads no recipe key for it: the caller gives the declared key as the argument `declared` (here, the tests give it directly).

# @deps
# consumes: libs/utils/src/utils/recipe_graph.py (key_candidates_for, key_candidate_sources), libs/utils/src/utils/recipe_loader.py
# doc: .claude/knowledge/decision_ledger.md (D-0485, D-0489)
# @end_deps
"""
from pathlib import Path

import pytest

from utils import action_names
from utils.recipe_graph import key_candidate_sources, key_candidates_for
from utils.recipe_loader import load_recipe

REPO = Path(__file__).resolve().parents[3]
DEMO = REPO / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"


def schema(*key_columns, other=("x",), **extra):
    fields = {name: {"type": "String", "is_entity_id": True} for name in key_columns}
    fields.update({name: {"type": "String"} for name in other})
    return {"source": {"type": "local_tsv", "path": "x.tsv"}, "input_fields": fields, **extra}


def recipe(entry_steps=None, tier2=None, ingredients=("Samples",), schema_key=("sample_id",)):
    raw = {"id": "r", "data_schemas": {"Samples": schema(*schema_key), "Other": schema()},
           "joins": {"J": {"ingredients": [{"dataset_id": i} for i in ingredients], "tier1": {"steps": entry_steps or []}, **({"tier2": {"steps": tier2}} if tier2 else {})}},
           "analysis_groups": {"g": {"ui_label": "g", "plots": {"p": {"ui_label": "p", "target_dataset": "J"}}}}}
    return raw


def step(action, **args):
    return {"action": action, **args}


GROUP = step(action_names.GROUP_BY, by=["country", "year"], named_aggs={"n": "pl.col('sample_id').count()"})


def test_the_entity_key_of_the_ingredient_is_a_candidate_when_nothing_changes_the_columns():
    assert key_candidates_for(recipe(), "J") == [("sample_id",)]


def test_a_table_with_no_declared_key_and_no_group_by_has_no_candidate():
    assert key_candidates_for(recipe(schema_key=()), "J") == []


def test_the_group_columns_of_the_last_aggregation_come_before_the_entity_key():
    raw = recipe(entry_steps=[step(action_names.GROUP_BY, by=["sample_id", "country"], named_aggs={"n": "pl.col('gene').count()"})])
    assert key_candidates_for(raw, "J") == [("sample_id", "country"), ("sample_id",)]


def test_after_an_aggregation_the_entity_key_is_gone_unless_it_is_a_group_column():
    assert key_candidates_for(recipe(entry_steps=[GROUP]), "J") == [("country", "year")]


def test_the_last_aggregation_wins_and_a_tier_2_aggregation_counts():
    raw = recipe(entry_steps=[GROUP], tier2=[step(action_names.GROUP_BY, by=["country"], named_aggs={"n": "pl.col('n').sum()"})])
    assert key_candidates_for(raw, "J") == [("country",)]


def test_a_renamed_group_column_is_followed_to_its_new_name():
    raw = recipe(entry_steps=[GROUP], tier2=[step(action_names.RENAME, mapping={"year": "year_label"})])
    assert key_candidates_for(raw, "J") == [("country", "year_label")]


def test_a_dropped_or_unselected_key_column_is_not_offered():
    dropped = recipe(entry_steps=[GROUP], tier2=[step(action_names.DROP, columns=["year"])])
    assert key_candidates_for(dropped, "J") == []
    unselected = recipe(entry_steps=[step(action_names.SELECT, exprs=["country", "x"])])
    assert key_candidates_for(unselected, "J") == []
    kept = recipe(entry_steps=[step(action_names.SELECT, exprs=["sample_id", "x"])])
    assert key_candidates_for(kept, "J") == [("sample_id",)]


def test_a_step_the_walk_cannot_read_stops_the_offer_of_a_column_that_may_not_survive_it():
    unreadable = recipe(entry_steps=[step("polars_unpivot", on=["a"], index=["sample_id"])])
    assert key_candidates_for(unreadable, "J") == []                  # whether `sample_id` exists after it is not known: never guessed


def test_a_declared_key_comes_first_and_is_offered_whatever_the_steps_do():
    raw = recipe(entry_steps=[GROUP])
    assert key_candidates_for(raw, "J", declared=["country", "year", "extra"]) == [("country", "year", "extra"), ("country", "year")]
    raw = recipe(entry_steps=[step("polars_unpivot", on=["a"], index=["sample_id"])])
    assert key_candidates_for(raw, "J", declared=["sample_id", "measure"]) == [("sample_id", "measure")]


def test_a_declared_key_of_one_name_may_be_written_as_text():
    assert key_candidates_for(recipe(), "J", declared="sample_id") == [("sample_id",)]


def test_a_candidate_is_listed_once():
    assert key_candidates_for(recipe(), "J", declared=["sample_id"]) == [("sample_id",)]


def test_the_sources_say_where_each_candidate_comes_from():
    raw = recipe(entry_steps=[GROUP])
    assert key_candidate_sources(raw, "J", declared=["country"]) == [(("country",), "declared in the recipe"), (("country", "year"), "group-by columns of the last aggregation")]
    assert key_candidate_sources(recipe(), "J") == [(("sample_id",), "entity id declared on an ingredient")]


@pytest.mark.parametrize("bad", [[], [""], [1], {"a": 1}, 3, [["a"]]])
def test_a_wrongly_written_declared_key_is_refused_plainly_not_ignored(bad):
    with pytest.raises(ValueError, match="declared key"):
        key_candidates_for(recipe(), "J", declared=bad)


def test_a_schema_read_directly_gives_its_own_entity_key():
    raw = recipe()
    assert key_candidates_for(raw, "Samples") == [("sample_id",)]


def test_an_unknown_table_is_a_plain_key_error():
    with pytest.raises(KeyError, match="no table or join"):
        key_candidates_for(recipe(), "Nope")


def test_the_recipe_is_not_changed():
    raw = recipe(entry_steps=[GROUP])
    import copy
    before = copy.deepcopy(raw)
    key_candidates_for(raw, "J", declared=["country"])
    assert raw == before


# ----------------------------------------------------------------------------------------------------- the demo recipe, read only

@pytest.fixture(scope="module")
def demo():
    raw, problems = load_recipe(str(DEMO))
    assert raw is not None
    return raw


def test_demo_the_aggregate_has_its_group_columns(demo):
    assert key_candidates_for(demo, "QA_aggregated_no_key") == [("country", "year_label")]


def test_demo_the_value_over_all_samples_has_the_entity_key(demo):
    assert key_candidates_for(demo, "QA_population_zscore") == [("sample_id",)]


def test_demo_the_per_sample_table_offers_the_group_columns_then_the_entity_key(demo):
    assert key_candidates_for(demo, "QA_AMR_per_sample") == [("sample_id", "country"), ("sample_id",)]


def test_demo_a_long_table_with_an_unreadable_step_offers_nothing(demo):
    assert key_candidates_for(demo, "Quast_with_metadata") == []


def test_nothing_in_a_recipe_is_read_as_a_declared_key(demo):
    """The library reads no recipe key for the declared key (its name and place are not decided, D-0489): a body that holds a `result_key` is not read."""
    raw = recipe()
    raw["joins"]["J"]["result_key"] = ["x"]
    assert key_candidates_for(raw, "J") == [("sample_id",)]
    assert all(source != "declared in the recipe" for table in demo["joins"] for _, source in key_candidate_sources(demo, table))


def test_a_declared_key_given_as_none_means_none_declared():
    assert key_candidates_for(recipe(), "J", declared=None) == [("sample_id",)]


def test_the_entry_may_be_a_join_or_a_schema_and_a_plots_own_tier_3_steps_are_not_read():
    """The id is a table or join id. A plot of the recipe has tier 3 steps of its own that this function does not read: it gives the candidates of the table."""
    raw = recipe()
    raw["analysis_groups"]["g"]["plots"]["p"]["tier3"] = {"steps": [step(action_names.DROP, columns=["sample_id"])]}
    assert key_candidates_for(raw, "J") == [("sample_id",)]
    with pytest.raises(KeyError):
        key_candidates_for(raw, "p")
