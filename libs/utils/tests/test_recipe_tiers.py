"""The one reading of a collection's tier-2 list (RECIPE-DATASET-TIER2-1, issue #77, DEC16).

Every table has T1, T2 and T3. A collection is a join or a schema that a plot reads directly; its tier-2 list is its
T2. Before issue #77 the tier-2 list of a schema plotted directly was ignored by the engine (only joins were read).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_tiers.py -q
"""
from utils.recipe_tiers import (AUDIT_STEPS, audit_step_places, audit_steps_of, author_steps, collection_bodies, plot_targets, step_list, tier2_parts,
                               tier2_steps, tier3_parts, tier3_steps, unapplied_join_tier2, unapplied_schema_tier2, without_audit_steps,
                               without_data_engines, without_tier2)

STEP_A = {"action": "modif_filter", "column": "group", "op": "eq", "value": "A", "na": "remove"}
STEP_B = {"action": "polars_sort", "by": ["group"], "descending": [False], "maintain_order": True}


def _recipe(*, t_tier2=None, j_tier2=None, targets=("T",), extra=None):
    raw = {
        "data_schemas": {
            "T": {"tier1": {"steps": []}, **({"tier2": {"steps": t_tier2}} if t_tier2 is not None else {})},
            "U": {"tier1": {"steps": []}},
        },
        "joins": {"J": {"ingredients": [{"dataset_id": "T"}, {"dataset_id": "U"}],
                        "tier1": {"steps": []}, **({"tier2": {"steps": j_tier2}} if j_tier2 is not None else {})}},
        "analysis_groups": {"g": {"ui_label": "G", "plots": {
            f"p_{t}": {"target_dataset": t} for t in targets}}},
    }
    raw.update(extra or {})
    return raw


# -- tier2_steps: the T2 list of one collection ------------------------------------------------

def test_a_schema_plotted_directly_has_its_own_tier2():
    assert tier2_steps(_recipe(t_tier2=[STEP_A]), "T") == [STEP_A]


def test_a_join_has_its_steps_tier2():
    assert tier2_steps(_recipe(j_tier2=[STEP_B]), "J") == [STEP_B]


def test_the_join_does_not_inherit_the_tier2_of_its_ingredient():
    """A join reads the T1 of its ingredients; the ingredient's own tier 2 belongs to its own T2 only."""
    assert tier2_steps(_recipe(t_tier2=[STEP_A]), "J") == []


def test_empty_or_absent_tier2_means_t2_equals_t1():
    assert tier2_steps(_recipe(t_tier2=[]), "T") == []
    assert tier2_steps(_recipe(), "T") == []
    assert tier2_steps(_recipe(), "J") == []


def test_an_unknown_collection_has_no_tier2():
    assert tier2_steps(_recipe(t_tier2=[STEP_A]), "nope") == []
    assert tier2_steps({}, "T") == []


def test_metadata_and_additional_schemas_are_collections_too():
    raw = {"metadata_schema": {"tier1": {"steps": []}, "tier2": {"steps": [STEP_A]}},
           "additional_datasets_schemas": {"X": {"tier1": {"steps": []}, "tier2": {"steps": [STEP_B]}}}}
    assert tier2_steps(raw, "metadata_schema") == [STEP_A]
    assert tier2_steps(raw, "X") == [STEP_B]


def test_the_list_returned_is_a_new_list():
    raw = _recipe(t_tier2=[STEP_A])
    tier2_steps(raw, "T").append("x")
    assert tier2_steps(raw, "T") == [STEP_A]


def test_step_list_reads_the_steps_of_one_tier_of_a_table_or_a_join():
    assert step_list({"tier1": {"steps": [STEP_A]}, "tier2": {"steps": [STEP_B]}}, "tier2") == [STEP_B]
    assert step_list({"tier1": {"steps": [STEP_A]}}, "tier2") == []
    assert step_list({"tier2": {"data_engine": "python-polars"}}, "tier2") == []  # no steps key: nothing to run
    assert step_list(None, "tier1") == []
    assert step_list({"tier1": [STEP_A]}, "tier1") == []  # a tier written as a list is the old shape (refused by the checker, S06/J07)
    assert step_list([STEP_A], "tier1") == []


# -- which tier-2 lists are run nowhere ---------------------------------------------------------

def test_plot_targets_lists_what_the_plots_read():
    assert plot_targets(_recipe(targets=("T", "J"))) == {"T", "J"}
    assert plot_targets({}) == set()


def test_a_schema_tier2_that_no_plot_reads_is_unapplied():
    assert unapplied_schema_tier2(_recipe(t_tier2=[STEP_A], targets=("J",))) == ["T"]


def test_a_schema_tier2_read_by_a_plot_is_applied_even_when_it_is_also_an_ingredient():
    assert unapplied_schema_tier2(_recipe(t_tier2=[STEP_A], targets=("T", "J"))) == []


def test_an_empty_tier2_is_never_unapplied():
    assert unapplied_schema_tier2(_recipe(t_tier2=[], targets=("J",))) == []


def test_a_join_tier2_that_no_plot_reads_is_unapplied():
    assert unapplied_join_tier2(_recipe(j_tier2=[STEP_B], targets=("T",))) == ["J"]


def test_a_join_tier2_read_by_a_plot_is_applied():
    assert unapplied_join_tier2(_recipe(j_tier2=[STEP_B], targets=("J",))) == []


def test_an_empty_or_absent_join_tier2_is_never_unapplied():
    assert unapplied_join_tier2(_recipe(j_tier2=[], targets=("T",))) == []
    assert unapplied_join_tier2(_recipe(targets=("T",))) == []
    assert unapplied_join_tier2({}) == []


# -- without_tier2: what Tier 1 depends on ---------------------------------------------------

def test_without_tier2_removes_every_collection_tier2_and_nothing_else():
    raw = _recipe(t_tier2=[STEP_A], j_tier2=[STEP_B])
    stripped = without_tier2(raw)
    assert "tier2" not in stripped["data_schemas"]["T"]
    assert "tier2" not in stripped["joins"]["J"]
    assert stripped["data_schemas"]["T"]["tier1"] == {"steps": []}
    assert stripped["analysis_groups"] == raw["analysis_groups"]
    # the recipe itself is not changed
    assert raw["data_schemas"]["T"]["tier2"] == {"steps": [STEP_A]}
    assert raw["joins"]["J"]["tier2"] == {"steps": [STEP_B]}


def test_without_tier2_gives_the_same_material_whatever_the_tier2_lists_hold():
    assert without_tier2(_recipe(t_tier2=[STEP_A])) == without_tier2(_recipe(t_tier2=[STEP_B])) == without_tier2(_recipe())


# --- the written data engines leave the Tier 1 material; the effective engine is a key argument (D-0240) ---------------------

def _engines_recipe():
    return {
        "data_engine": "python-polars",
        "plot_engine": "python-plotnine",
        "data_schemas": {"A": {"tier1": {"data_engine": "python-polars", "steps": [1]}, "tier2": {"data_engine": "x", "steps": [2]}}},
        "metadata_schema": {"tier1": {"data_engine": "python-polars", "steps": []}},
        "joins": {"J": {"tier1": {"data_engine": "python-polars", "steps": [3]}, "tier2": {"steps": [4]}}},
    }


def test_without_data_engines_drops_the_recipes_engine_and_the_engine_of_every_tier1_and_nothing_else():
    material = without_data_engines(_engines_recipe())
    assert "data_engine" not in material
    assert material["plot_engine"] == "python-plotnine"           # the plot engine is not this function's business
    assert material["data_schemas"]["A"]["tier1"] == {"steps": [1]}
    assert material["metadata_schema"]["tier1"] == {"steps": []}
    assert material["joins"]["J"]["tier1"] == {"steps": [3]}
    assert material["data_schemas"]["A"]["tier2"] == {"data_engine": "x", "steps": [2]}   # a tier 2 leaves with `without_tier2`


def test_without_data_engines_does_not_change_the_recipe_it_is_given():
    raw = _engines_recipe()
    without_data_engines(raw)
    assert raw == _engines_recipe()


def test_without_data_engines_leaves_a_tier_that_is_not_a_mapping_or_names_no_engine_as_it_is():
    raw = {"data_schemas": {"A": {"tier1": [1, 2]}, "B": {}, "C": {"tier1": {"steps": []}}}, "joins": {"J": "not a mapping"}}
    assert without_data_engines(raw) == raw


def test_collection_bodies_lists_every_table_and_join_and_a_join_wins_a_shared_id():
    raw = {"data_schemas": {"A": {"k": 1}, "S": {"k": "schema"}}, "additional_datasets_schemas": {"B": {"k": 2}},
           "metadata_schema": {"k": 3}, "joins": {"J": {"k": 4}, "S": {"k": "join"}}}
    found = collection_bodies(raw)
    assert set(found) == {"A", "S", "B", "metadata_schema", "J"}
    assert found["S"] == {"k": "join"}        # the order `collection_body` resolves an id in
    assert collection_bodies({}) == {}


# -- the two lists of a tier of an audit recipe (D-0332): the author's `steps` and the audit's `audit_steps` ----------------------------------------

AUDIT_1 = {"action": "modif_filter", "column": "v", "op": "gt", "value": 1, "na": "keep", "id": "audit_1a2b3c4d_1", "audit_comment": "r"}
AUDIT_2 = {"action": "polars_drop", "columns": ["w"], "id": "audit_1a2b3c4d_2", "audit_comment": "r"}


def _audit_recipe():
    raw = _recipe(t_tier2=[STEP_A], j_tier2=[STEP_B])
    raw["data_schemas"]["T"]["tier1"] = {"steps": [STEP_B], AUDIT_STEPS: [AUDIT_1]}
    raw["data_schemas"]["T"]["tier2"][AUDIT_STEPS] = [AUDIT_2]
    raw["analysis_groups"]["g"]["plots"]["p_T"]["tier3"] = {"steps": [STEP_A], AUDIT_STEPS: [AUDIT_1, AUDIT_2]}
    return raw


def test_the_step_list_of_a_tier_is_the_authors_steps_then_the_audit_steps_and_each_list_can_be_read_apart():
    body = _audit_recipe()["data_schemas"]["T"]
    assert step_list(body, "tier1") == [STEP_B, AUDIT_1]
    assert author_steps(body, "tier1") == [STEP_B] and audit_steps_of(body, "tier1") == [AUDIT_1]
    assert step_list(body, "tier2") == [STEP_A, AUDIT_2]
    assert step_list({"tier1": {"steps": [STEP_B]}}, "tier1") == [STEP_B] and audit_steps_of({"tier1": {"steps": [STEP_B]}}, "tier1") == []
    assert step_list(None, "tier1") == [] and step_list({}, "tier2") == [] and audit_steps_of("x", "tier1") == []


def test_the_readers_of_a_collection_and_of_a_plot_run_the_authors_steps_then_the_audit_steps():
    raw = _audit_recipe()
    assert tier2_steps(raw, "T") == [STEP_A, AUDIT_2] and tier2_parts(raw, "T") == ([STEP_A], [AUDIT_2])
    assert tier3_steps(raw, "p_T") == [STEP_A, AUDIT_1, AUDIT_2] and tier3_parts(raw, "p_T") == ([STEP_A], [AUDIT_1, AUDIT_2])
    assert tier2_parts(raw, "J") == ([STEP_B], []) and tier3_parts(raw, "nothing") == ([], [])


def test_a_tier_that_holds_only_audit_steps_is_a_tier_with_steps_to_run():
    raw = _recipe()
    raw["data_schemas"]["T"]["tier2"] = {"steps": [], AUDIT_STEPS: [AUDIT_1]}
    assert tier2_steps(raw, "T") == [AUDIT_1] and tier2_parts(raw, "T") == ([], [AUDIT_1])


def test_a_tier_two_that_holds_audit_steps_on_a_table_no_plot_reads_is_an_unapplied_tier_two():
    raw = _recipe(targets=("J",))
    raw["data_schemas"]["T"]["tier2"] = {"steps": [], AUDIT_STEPS: [AUDIT_1]}
    assert unapplied_schema_tier2(raw) == ["T"]


def test_the_places_of_the_audit_lists_and_the_recipe_without_them():
    raw = _audit_recipe()
    assert audit_step_places(raw) == ["data_schemas.T.tier1", "data_schemas.T.tier2", "plot p_T.tier3"]
    assert audit_step_places(_recipe()) == [] and audit_step_places("x") == []
    stripped = without_audit_steps(raw)
    assert audit_step_places(stripped) == [] and step_list(stripped["data_schemas"]["T"], "tier1") == [STEP_B]
    assert raw["data_schemas"]["T"]["tier1"][AUDIT_STEPS] == [AUDIT_1], "the recipe given is not changed"


def test_the_recipe_without_tier_2_loses_the_audit_steps_of_tier_2_with_it_and_keeps_those_of_tier_1():
    material = without_tier2(_audit_recipe())
    assert step_list(material["data_schemas"]["T"], "tier1") == [STEP_B, AUDIT_1] and "tier2" not in material["data_schemas"]["T"]


def test_the_places_of_audit_lists_include_a_tier_where_no_tier_reads_them():
    raw = _recipe()
    raw["data_schemas"]["T"]["tier3"] = {"steps": [], AUDIT_STEPS: []}
    raw["analysis_groups"]["g"]["plots"]["p_T"]["tier1"] = {"steps": [], AUDIT_STEPS: []}
    assert audit_step_places(raw) == ["data_schemas.T.tier3", "plot p_T.tier1"]
