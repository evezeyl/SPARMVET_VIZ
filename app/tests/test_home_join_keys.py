"""HOME and the join keys of the recipe (step 4b made this alive; D-0250).

`extract_primary_keys` reads the keys of every join step of `joins.*.tier1.steps` and `tier2.steps`. On dev it read a place that no
recipe had, so it always gave `[]` and nothing was ever refused. Now, for the demo recipe, it gives `Gene_name`, `VF_gene` and
`sample_id`, and HOME uses them (`home_state["primary_keys"]`):

- a column drop is written in the plot's own steps (the place `T3:<plot>`), after every join, so a join key dropped there is NOT refused any more: the refusal is by PLACE
  (D-0358, which modulates D-0297; the rule is `utils.key_drop`, its tests `libs/utils/tests/test_key_drop.py`), the trial of the drop asks it with the place it has (ADAPTED: before, a key
  was refused by its name with "Cannot drop join key column(s): ...");
- a filter on a join key is ALLOWED; the audit step it makes carries `primary_key_warning=True` (the yellow banner on the step card, a marker in the report); a filter on another column
  does not carry it.

FLOW-3 (2026-11-27): the closures `_col_drop_to_audit` and `_send_staged_to_audit` and the propagation dialog are gone; the drop is tried by `trial_handlers._try_drop` and the nodes of a condition are
`audit_try.tried_nodes`, so these tests run those (the real effect on the harness of `test_trial_panel_dependencies.py`; the rule is the real `key_drop.DropGate`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_home_join_keys.py -q
"""
from pathlib import Path

import pytest

from app.modules.audit_try import tried_nodes
from app.modules.cache_keys import load_data_analysis_recipe
from app.modules.session_manager import extract_primary_keys
from app.tests.test_audit_join_key_drops import _nodes_of, _trial_of_drop
from utils import key_drop

DEMO = Path(__file__).resolve().parents[2] / "config" / "data_analysis_recipes" / "pipelines" / "1_test_data_ST22_dummy.yaml"


def demo_raw() -> dict:
    return load_data_analysis_recipe(DEMO).config.raw_config


def demo_keys() -> list:
    return extract_primary_keys(demo_raw())


DEMO_PLOT = "mlst_bar"      # a plot of the demo recipe


def test_the_demo_recipe_gives_its_join_keys():
    assert demo_keys() == ["Gene_name", "VF_gene", "sample_id"]


COLUMNS = ["sample_id", "Gene_name", "VF_gene", "year", "source"]
PLACE = f"T3:{DEMO_PLOT}"


def drop(monkeypatch, kept, raw=None, plans=None):
    return _trial_of_drop(monkeypatch, raw if raw is not None else demo_raw(), kept, columns=COLUMNS, shown=PLACE, plans=plans)


def test_dropping_a_join_key_column_in_a_plots_own_steps_is_tried(monkeypatch):
    """ADAPTED (D-0358): the demo recipe joins on `sample_id`; the drop is at `T3:mlst_bar`, after every join, so nothing is refused (before: refused by name)."""
    world = drop(monkeypatch, ["Gene_name", "VF_gene", "year", "source"])      # `sample_id` is deselected
    assert _nodes_of(world) == [("sample_id", PLACE)] and "The drop is tried" in world.notes[-1]


def test_the_trial_asks_the_rule_with_the_place_of_the_open_plot_and_follows_its_refusal(monkeypatch):
    """MUTATION K4 fails here: the real rule refuses nothing at a plot, so a stand-in answer proves the trial asks `T3:<open plot>` for the deselected columns and obeys."""
    asked = []

    def answer(self, place, columns):
        asked.append((place, list(columns)))
        return "STAND-IN refusal"
    monkeypatch.setattr(key_drop.DropGate, "problem", answer)
    world = drop(monkeypatch, ["year", "source"])
    assert asked == [(PLACE, ["sample_id", "Gene_name", "VF_gene"])]
    assert _nodes_of(world) == [] and world.notes[-1] == "STAND-IN refusal Nothing was tried."


def test_the_trial_gives_the_rule_the_engine_plan_of_the_open_recipe(monkeypatch):
    """LBFB step 0b: the trial asks the rule with `recipe_plans()` (MUTATION PC8: the plan is not passed)."""
    given = []
    real = key_drop.DropGate.__init__

    def init(self, raw, plans=None):
        given.append(plans)
        real(self, raw, plans)
    monkeypatch.setattr(key_drop.DropGate, "__init__", init)
    from utils.declared_plans import declared_plan_book
    from utils.recipe_graph import build_graph
    sentinel = declared_plan_book(build_graph(demo_raw()))      # any real plan book: the test is about which one the rule gets
    drop(monkeypatch, ["year", "source"], plans=sentinel)
    assert given == [sentinel]


def test_dropping_a_column_that_is_not_a_key_is_tried(monkeypatch):
    world = drop(monkeypatch, ["sample_id", "Gene_name", "VF_gene", "source"])   # `year` is deselected
    assert _nodes_of(world) == [("year", PLACE)]


def test_a_filter_on_a_join_key_is_allowed_and_its_audit_step_carries_the_warning():
    nodes = tried_nodes([{"column": "sample_id", "op": "eq", "value": "a", "dtype": "String", "na": "remove"}], [PLACE], primary_keys=demo_keys())
    assert len(nodes) == 1
    assert nodes[0]["node_type"] == "filter_row"                 # kept as a filter, not turned into an exclusion (AUDIT-1)
    assert nodes[0].get("primary_key_warning") is True
    assert nodes[0]["params"]["column"] == "sample_id" and nodes[0]["params"]["op"] == "eq"


def test_a_filter_on_another_column_carries_no_warning_and_a_mixed_try_marks_only_the_key():
    nodes = tried_nodes([{"column": "year", "op": "gt", "value": 2020, "dtype": "Int64", "na": "remove"},
                         {"column": "VF_gene", "op": "ne", "value": "z", "dtype": "String", "na": "remove"}], [PLACE], primary_keys=demo_keys())
    assert [(n["params"]["column"], n.get("primary_key_warning", False)) for n in nodes] == [("year", False), ("VF_gene", True)]


def test_nothing_is_tried_when_the_composer_has_a_bug(monkeypatch):
    """A bug of the plan composer is not "cannot tell": the trial writes no step and tries nothing (the notice is shown by `recipe_plans`)."""
    from app.modules.plan_composer import PlanComposerBug

    def broken():
        raise PlanComposerBug("bug")
    from app.tests.test_trial_panel_dependencies import _TrialThatCounts, _flush, _world
    import app.handlers.trial_handlers as trial_handlers
    trial = _TrialThatCounts()
    monkeypatch.setattr(trial_handlers, "trial_places", lambda shown_place, chosen, graph, lineage: ((PLACE,), ""))
    world2 = _world(monkeypatch, trial=trial, shown_place=lambda: PLACE, columns_at=lambda p: [(c, "String") for c in COLUMNS], open_graph=lambda: object(), lineage_calc=lambda: (object(), ""),
                    recipe_raw=lambda: demo_raw(), recipe_plans=broken)
    _flush()
    world2.live.set("preview_col_selector", ["year", "source"])
    world2.live.set("col_drop_try", 1)
    _flush()
    assert _nodes_of(world2) == [] and trial.tried == [] and world2.notes == []
