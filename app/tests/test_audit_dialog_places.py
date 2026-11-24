"""The dialog of Send to Audit writes a step at a place of any of the three tiers (demo step 7): `filter_and_audit_handlers._handle_propagation_confirm`, `_confirm_places`, `_stage_nodes`.

The closures of the real handler are run with stand-ins for the app (the way `test_audit_join_key_drops.py` runs them), on the small recipe of `test_audit_places.py`
(sources A and B, a join J with tier-2 steps read by a plot P, a table X read by a plot Q, and a second plot P2 on J):
- "This plot only" stages ONE pending node at `T3:<plot>`, in the one bucket, with no reason (Apply is locked until it has one) and the plot it was started from;
- "All plots" stages one node per plot, all with the id of the decision; "All plots except" leaves out the plots picked; a plot whose table lacks the column is skipped and told;
- "At a table this plot is built from": the ticked places are staged, one node each, with the id of the decision; a table together with a plot below it (or a table below
  another ticked table) is refused with ONE plain sentence, nothing is staged and the dialog stays open; the plot's own tier 3 alone is a valid choice;
- the refusal of a key drop at a place is the one rule `utils.key_drop`, asked by `_confirm_places` for every ticked place (its own tests: `test_audit_join_key_drops.py`).

Mutation index (seen failing): MUTATION D1 `_stage_nodes` writes `plot_scope` of the plot (a per-plot bucket again): the first test fails; MUTATION D2 `_confirm_places` leaves the plot's own
place out of the offered ones: the last-but-one test fails; MUTATION D3 `_confirm_places` skips `choice_problem`: the refusal test fails.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_audit_dialog_places.py -q
"""
from types import SimpleNamespace

import pytest

from app.modules.audit_places import PLACES_BUCKET, place_lines
from app.modules.session_manager import make_audit_step
from app.tests.test_audit_join_key_drops import Val, closure
from app.tests.test_audit_places import all_have_id, book, small
from utils.recipe_graph import build_graph


class Dialog:
    def __init__(self, active="subtab_P", recipe=None, has_column=lambda plot, column: True):
        self.raw = recipe or small()
        self.graph = build_graph(self.raw)
        self.plans = book(self.graph, all_have_id)
        self.state = Val({"active_plot_subtab": active, "_pending_t3_nodes": []})
        self.scratch = Val({"nodes": [], "kind": "filter"})
        self.notes, self.removed = [], []
        self.inputs = {}
        self.active = Val(active)
        self.has_column = has_column

    def scratch_filter(self, column="id"):
        node = make_audit_step("filter_row", {"column": column, "op": "ne", "value": "x", "na": "keep"}, plot_scope=PLACES_BUCKET, reason="")
        self.scratch.set({"nodes": [node], "kind": "filter"})
        return node

    def scratch_drop(self, column):
        node = make_audit_step("drop_column", {"column": column}, plot_scope=PLACES_BUCKET, reason="")
        self.scratch.set({"nodes": [node], "kind": "drop"})
        return node

    def _env(self):
        ui_stub = SimpleNamespace(modal_remove=lambda: self.removed.append(1))
        safe = lambda i, k, d=None: self.inputs.get(k, d)
        stage = closure("_stage_nodes", home_state=self.state, _propagation_scratch=self.scratch)
        found = lambda nodes, sub: (self.graph, self.plans, place_lines(self.graph, self.plans, sub.removeprefix("subtab_"), [n["params"]["column"] for n in nodes]))
        return ui_stub, safe, stage, found

    def confirm(self, choice, picks=None, except_picks=None):
        self.inputs = {"propagation_choice": choice, "propagation_places": picks or [], "propagation_except": except_picks or []}
        ui_stub, safe, stage, found = self._env()
        places = closure("_confirm_places", home_state=self.state, active_home_subtab=self.active, _places_offered=found, safe_input=safe, input={}, ui=ui_stub,
                         _stage_nodes=stage, _notify=lambda m, **k: self.notes.append(m), recipe_raw=lambda: self.raw, plots_below=__import__("app.modules.audit_places", fromlist=["x"]).plots_below)
        closure("_handle_propagation_confirm", home_state=self.state, _propagation_scratch=self.scratch, safe_input=safe, input={}, active_home_subtab=self.active,
                _all_plot_subtab_ids=lambda: ["subtab_P", "subtab_P2", "subtab_Q"], _plot_has_column=self.has_column, _plot_label=lambda s: s,
                _notify=lambda m, **k: self.notes.append(m), ui=ui_stub, _stage_nodes=stage, _confirm_places=places)()

    def pending(self):
        return self.state.get()["_pending_t3_nodes"]


def test_this_plot_only_stages_one_node_at_the_tier3_of_the_plot_in_the_one_bucket_with_no_reason():
    d = Dialog()
    scratch = d.scratch_filter()
    d.confirm("this")
    (node,) = d.pending()
    assert node["place"] == "T3:P" and node["plot_scope"] == PLACES_BUCKET and node["reason"] == "" and node["started_from"] == "subtab_P" and node["id"] == scratch["id"]
    assert d.removed, "the dialog is closed"


def test_all_plots_is_one_node_per_plot_with_the_id_of_the_decision_and_all_except_leaves_the_picked_out():
    d = Dialog()
    scratch = d.scratch_filter()
    d.confirm("all")
    assert sorted(n["place"] for n in d.pending()) == ["T3:P", "T3:P2", "T3:Q"] and {n["id"] for n in d.pending()} == {scratch["id"]}
    d = Dialog()
    scratch = d.scratch_filter()
    d.confirm("except", except_picks=["subtab_P2"])
    assert sorted(n["place"] for n in d.pending()) == ["T3:P", "T3:Q"]


def test_a_plot_whose_table_lacks_the_column_is_skipped_and_told():
    d = Dialog(has_column=lambda plot, column: plot != "subtab_Q")
    d.scratch_filter()
    d.confirm("all")
    assert sorted(n["place"] for n in d.pending()) == ["T3:P", "T3:P2"]
    assert any("Skipped" in note and "subtab_Q" in note for note in d.notes), d.notes


def test_ticked_tables_are_staged_one_node_each_with_the_id_of_the_decision():
    d = Dialog()
    scratch = d.scratch_filter()
    d.confirm("place", picks=["T1:A", "T1:B"])
    assert sorted(n["place"] for n in d.pending()) == ["T1:A", "T1:B"] and {n["id"] for n in d.pending()} == {scratch["id"]} and d.removed


def test_a_table_together_with_the_plot_below_it_is_refused_in_one_plain_sentence_and_nothing_is_staged():
    for picks in (["T1:A", "T3:P"], ["T3:P", "T2:J"], ["T1:J", "T3:P"]):
        d = Dialog()
        d.scratch_filter()
        d.confirm("place", picks=picks)
        assert d.pending() == [] and d.removed == [], picks
        (note,) = d.notes
        assert note.startswith("⛔") and all(f"'{p}'" in note for p in picks) and "choose one of them" in note, note


def test_the_plots_own_tier3_alone_is_a_valid_choice_of_the_place_dialog_and_another_plots_is_not_offered():
    d = Dialog()
    d.scratch_filter()
    d.confirm("place", picks=["T3:P"])
    assert [n["place"] for n in d.pending()] == ["T3:P"]
    d = Dialog()
    d.scratch_filter()
    d.confirm("place", picks=["T3:Q"])
    assert d.pending() == [] and "not one of the places offered" in d.notes[0]


def test_nothing_ticked_is_refused():
    d = Dialog()
    d.scratch_filter()
    d.confirm("place", picks=[])
    assert d.pending() == [] and "Choose at least one place" in d.notes[0]
