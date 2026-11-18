"""The one reading of a collection's tier-2 list (RECIPE-DATASET-TIER2-1, issue #77, DEC16).

Every table has T1, T2 and T3. A collection is a join or a schema that a plot reads directly; its tier-2 list is its
T2. Before issue #77 the tier-2 list of a schema plotted directly was ignored by the engine (only joins were read).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_recipe_tiers.py -q
"""
from utils.recipe_tiers import plot_targets, step_list, tier2_steps, unapplied_join_tier2, unapplied_schema_tier2, without_tier2

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
