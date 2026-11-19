"""The load gate accepts a recipe whose plot has tier-3 steps, judges those steps, and still refuses a step list in a place the engine does not read.

Before: `engine_load_problems` counted the steps written in the loaded recipe, which also holds a flat copy of the plots under `plots`,
so a plot's tier-3 steps were counted as written and never as read ("the check read 0 of the 2 steps written here"): HOME refused
every recipe with tier-3 steps as a fault of the app. Now the tier-3 steps count once as written and are read by the same lookup as
`DataOrchestrator.materialize_tier3` (`utils.recipe_tiers.tier3_steps`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_gate_accepts_tier3.py -q

# @deps
# consumes: app/modules/data_analysis_recipe_validator.py (engine_load_problems, validate_data_analysis_recipe), app/src/bootloader.py (Bootloader._gate_one), libs/utils/src/utils/recipe_tiers.py (tier3_steps)
# doc: .claude/rules/rules_data_analysis_recipe_structure.md#11, .claude/knowledge/decision_ledger.md (D-0306, D-0029, D-0063)
# @end_deps
"""
import copy

from app.modules.data_analysis_recipe_validator import engine_load_problems, validate_data_analysis_recipe
from app.src.bootloader import Bootloader
from utils.recipe_factory import minimal_plot, minimal_recipe, write_recipe

KEEP = {"action": "modif_filter", "column": "value", "op": "ge", "value": 1, "na": "remove"}


def recipe(tier3):
    raw = minimal_recipe("r", plots={"p": minimal_plot("table", {"x": "sample_id"}, tier3=tier3)})
    return raw


def gate(tmp_path, raw):
    path = write_recipe(tmp_path / "r.yaml", raw)
    gate = Bootloader.__new__(Bootloader)
    gate.get_location = lambda key: str(tmp_path)
    gate.get_contact = lambda: None
    gate.get_imports_dir = lambda: None
    gate.data_lookup = None
    return path, gate._gate_one(str(path))[0]


def test_a_plot_with_tier3_steps_passes_the_validator_and_the_gate(tmp_path):
    path, gate_problems = gate(tmp_path, recipe([KEEP, {"action": "polars_drop", "columns": ["sample_id"]}]))
    assert validate_data_analysis_recipe(path) == []
    assert not [p for p in gate_problems if "steps written" in str(p)], gate_problems


def test_a_plot_with_no_tier3_steps_still_passes(tmp_path):
    path, _ = gate(tmp_path, recipe(None))
    assert validate_data_analysis_recipe(path) == []


def test_a_tier3_step_with_an_unknown_action_is_refused_by_the_gate_with_the_checkers_message(tmp_path):
    path, gate_problems = gate(tmp_path, recipe([{"action": "no_such_action_xyz"}]))
    text = " ".join(str(p) for p in gate_problems)
    assert gate_problems, "the gate accepted a recipe whose tier-3 step names an unknown action"
    assert "no_such_action_xyz" in text and "steps written" not in text
    assert "tier3" in text


def test_a_step_list_in_a_place_the_engine_does_not_read_is_still_refused_by_the_count(tmp_path):
    raw = recipe([KEEP])
    # a step list under a plot key the engine does not read: written, never read
    raw["analysis_groups"]["main"]["plots"]["p"]["extra"] = {"steps": [copy.deepcopy(KEEP)]}
    path = write_recipe(tmp_path / "r.yaml", raw)
    problems = engine_load_problems(path)
    assert any("steps written" in p.problem for p in problems), problems


def test_a_tier3_step_list_of_the_wrong_kind_is_not_counted_as_read(tmp_path):
    raw = recipe([KEEP])
    raw["analysis_groups"]["main"]["plots"]["p"]["tier3"] = [copy.deepcopy(KEEP)]  # a bare list: not the mapping form
    path = write_recipe(tmp_path / "r.yaml", raw)
    assert validate_data_analysis_recipe(path), "a tier3 written as a bare list was accepted"
