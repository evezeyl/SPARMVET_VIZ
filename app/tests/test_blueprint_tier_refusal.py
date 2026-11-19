"""The refusal of Blueprint's Save for a step made for the other tier (PROVISIONAL wording, D-0308).

A file holds one tier. A step added with the picker on tier 2 and saved into a tier-1 file is refused (the refusal stays until the
owner chooses). The message must be true: it names the step, the tier the step was made for, the open file, says that nothing was
saved, and says what the user can do TODAY. The first version told the user to "open the tier2 file of the table" (a table can have
none) or to "remove the step" (no control removes one step).

The helper is tested alone; the save closure is then run on a copy of the demo recipe: a table with a tier-2 file (ResFinder), a
table with none (FastP), nothing written in either case, and a click on the table node loads the steps of the file again.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_tier_refusal.py -q
"""
from pathlib import Path

import pytest

from app.modules.blueprint_tier_refusal import other_tier_refusal, tier_word
from app.tests.test_blueprint_plot_open import Blueprint, Input, blueprint, scratch_demo  # noqa: F401  (fixtures)

WRONG_WORDS = ("Open the tier2 file", "remove the step", "Remove the step")


# -- the text

def test_a_table_with_a_file_for_the_tier_names_that_file():
    text = other_tier_refusal("polars_with_columns", "tier2", "tier1", "FastP_wrangling.yaml",
                              {"tier1": "d/wrangling/FastP_wrangling.yaml", "tier2": "d/wrangling/FastP_t2.yaml"})
    assert "'polars_with_columns'" in text and "made for tier 2" in text and "(FastP_wrangling.yaml) is tier 1" in text
    assert "nothing was saved" in text
    assert "FastP_t2.yaml" in text and "lineage rail" in text
    assert "no tier 2 file" not in text


def test_a_table_without_a_file_for_the_tier_says_so_and_what_to_do_by_hand():
    text = other_tier_refusal("polars_with_columns", "tier2", "tier1", "FastP_wrangling.yaml", {"tier1": "d/f.yaml", "tier2": None})
    assert "no tier 2 file yet" in text and "cannot create one" in text and "`tier2:`" in text and "by hand" in text
    assert "lineage rail" not in text


def test_a_tier_written_inside_the_recipe_is_not_called_a_file():
    text = other_tier_refusal("polars_with_columns", "tier2", "tier1", "f.yaml", {"tier2": {"inline": {"steps": []}}})
    assert "inside the recipe, not in a file" in text and "no tier 2 file yet" not in text


def test_the_other_direction_names_tier_1_and_tier_2_the_right_way_round():
    text = other_tier_refusal("polars_select", "tier1", "tier2", "t2.yaml", {"tier1": "d/t1.yaml"})
    assert "made for tier 1" in text and "(t2.yaml) is tier 2" in text and "t1.yaml" in text


def test_no_sibling_information_is_the_case_of_no_file():
    assert "no tier 2 file yet" in other_tier_refusal("a", "tier2", "tier1", "f.yaml", None)


@pytest.mark.parametrize("siblings", [None, {}, {"tier2": None}, {"tier2": "d/t2.yaml"}, {"tier2": {"inline": {}}}])
def test_the_message_names_no_control_that_does_not_exist(siblings):
    text = other_tier_refusal("a", "tier2", "tier1", "f.yaml", siblings)
    for words in WRONG_WORDS:
        assert words not in text
    assert "nothing was saved" in text and "click the table node again" in text


def test_tier_word_leaves_an_unknown_name_alone():
    assert tier_word("tier2") == "tier 2" and tier_word("other") == "other"


# -- the save closure, on the demo recipe

def refused(blueprint, scratch_demo, plot_or_table, tier_for_step):
    """Open a table, add a step marked for `tier_for_step` to the stack, press Save; returns (file, text before, notifications)."""
    blueprint.open_recipe(scratch_demo)
    blueprint.tap(plot_or_table)
    file = Path(blueprint.ws.active_component_path.get())
    before = file.read_text()
    step = {"action": "polars_with_columns", "params": {"exprs": ["pl.lit(1).alias('proof_one')"]}, "comment": "x", "_tier": tier_for_step}
    blueprint.ws.logic_stack.set(blueprint.ws.logic_stack.get() + [step])
    blueprint.ui.notifications.clear()
    blueprint.ns["_handle_data_analysis_recipe_save_internal"]()
    return file, before, [m for t, m in blueprint.ui.notifications]


def test_save_of_a_tier_2_step_into_a_tier_1_file_of_a_table_with_no_tier_2_file(blueprint, scratch_demo):
    file, before, said = refused(blueprint, scratch_demo, "FastP", "tier2")

    assert file.read_text() == before                                    # nothing was written
    assert len(said) == 1 and "FastP_wrangling.yaml" in said[0] and "made for tier 2" in said[0]
    assert "no tier 2 file yet" in said[0] and "`tier2:`" in said[0]


def test_save_of_a_tier_2_step_into_a_tier_1_file_of_a_table_that_has_a_tier_2_file(blueprint, scratch_demo):
    file, before, said = refused(blueprint, scratch_demo, "ResFinder", "tier2")

    assert file.read_text() == before
    assert len(said) == 1 and f"({file.name}) is tier 1" in said[0] and file.name == "ResFinder_wrangling_tier1.yaml"
    assert "ResFinder_wrangling_tier2.yaml" in said[0]                   # the file the step belongs in
    assert "lineage rail" in said[0] and "no tier 2 file" not in said[0]


def test_the_message_does_not_name_a_file_that_the_recipe_does_not_have(blueprint, scratch_demo):
    _, _, said = refused(blueprint, scratch_demo, "FastP", "tier2")
    assert not [n for n in said if "lineage rail" in n]


def test_a_click_on_the_table_node_again_loads_the_steps_of_the_file_and_the_unsaved_step_is_gone(blueprint, scratch_demo):
    file, before, _ = refused(blueprint, scratch_demo, "FastP", "tier2")
    assert any(n.get("action") == "polars_with_columns" for n in blueprint.ws.logic_stack.get())

    blueprint.tap("FastP")

    assert not any(n.get("action") == "polars_with_columns" for n in blueprint.ws.logic_stack.get())
    assert file.read_text() == before


def test_a_step_of_the_right_tier_is_still_saved(blueprint, scratch_demo):
    blueprint.open_recipe(scratch_demo)
    blueprint.tap("FastP")
    file = Path(blueprint.ws.active_component_path.get())
    step = {"action": "polars_with_columns", "params": {"exprs": ["pl.lit(1).alias('proof_one')"]}, "comment": "x", "_tier": "tier1"}
    blueprint.ws.logic_stack.set(blueprint.ws.logic_stack.get() + [step])

    blueprint.ns["_handle_data_analysis_recipe_save_internal"]()

    assert "polars_with_columns" in file.read_text()
