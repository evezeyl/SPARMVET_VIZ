"""Add to audit pipeline, on the real reactive graph without a browser (FLOW-2; ui_implementation_contract.md sections 3 and 14, R1 to R4; ledger D-0656, D-0669, D-0670, D-0672).

What the design expects:
- the marks "User verified" and the reason are inputs whose ids carry the number of the Try: a mark or a reason of an OLDER trial is never read for a new one; the summary says "N of M places user verified";
- typing a reason or ticking a mark neither ends the trial nor draws the panel again (they are read by outputs of their own);
- "Add to audit pipeline" is refused without a reason (one plain line; nothing is applied); with one it applies through the engine's `apply_trial` (the trial's tables, not a second computation) and
  writes the step at ALL the places of the trial (D-0669), each node with `user_verified` (True only for a place marked), appended to the committed list; then the trial ends, the session is saved
  once, the count of saves moves and ONE notice says what was added; the staged condition of a condition trial is cleared by the Add itself (a drop trial leaves the staged rows: they are another step);
- a failure of the engine (`TrialRefused`, any error) leaves the committed list, the count and the session as they were, ends the trial cleanly and says so in one plain line;
- a second click adds nothing (no trial any more); a change of the world after the Try (the applied steps, the condition) ends the trial instead of adding.

Mutation index (each seen failing): MUTATION B1 `_add` writes only the places marked; MUTATION B2 `_add` ignores the reason; MUTATION B3 `_add` writes the state BEFORE `apply_trial` returns (a failed apply leaves a step);
MUTATION B4 the panel reads the marks (they become a dependency of its render).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_trial_add_dependencies.py -q

# @deps
# consumes: app/handlers/trial_handlers.py, app/modules/audit_add.py, app/modules/audit_try.py, app/tests/test_trial_panel_dependencies.py (the harness)
# doc: .claude/rules/ui_implementation_contract.md#14, .claude/knowledge/decision_ledger.md (D-0656, D-0669, D-0670, D-0672)
# @end_deps
"""
import pytest
from shiny import reactive

from app.modules.audit_places import PLACES_BUCKET, nodes_signature
from app.modules.audit_trial import PlaceEffect, TrialRefused, TrialResult
from app.modules.audit_try import TrialRecord, condition_lines, world_of
from app.modules.session_manager import make_audit_step
from app.tests.test_trial_panel_dependencies import ROW, _flush, _html, _peek, _set, _world

PLACES = ("T1:ResFinder", "T2:ResFinder", "T3:amr_heatmap")


def _tried():
    return tuple(make_audit_step("filter_row", {"column": "identity", "op": "lt", "value": 99.0, "na": "remove", "dtype": "Float64"}, plot_scope=PLACES_BUCKET, reason="", place=p, node_id="dec1") for p in PLACES)


class FakeTrial:
    """What `PlaceTrial` gives the handler: `apply_trial` returns applied + tried with the reason and `applied_at`, or raises."""

    def __init__(self, raises=None):
        self.discards, self.calls, self.raises = 0, [], raises

    def discard(self):
        self.discards += 1

    def apply_trial(self, recipe_id, applied, tried, reason, plans=None, when=None):
        self.calls.append((list(applied), list(tried), reason))
        if self.raises:
            raise self.raises
        return list(applied) + [{**n, "reason": reason, "applied_at": "2026-11-27T10:00:00"} for n in tried]


def _record(w, serial=1, error=None, committed=()):
    rows = _peek(w.pending)
    world = world_of("audit", "r", ("a", "b"), rows, [], nodes_signature(list(committed)))
    effects = tuple(PlaceEffect(p, p, 10, 4, "table changed") for p in PLACES)
    return TrialRecord(world, PLACES, _tried(), TrialResult(("sig",), effects), condition_lines(rows), serial)


def _setup(monkeypatch, raises=None, committed=(), steps=None):
    saved = []
    trial = FakeTrial(raises)
    w = _world(monkeypatch, trial=trial, save_session=lambda state: saved.append(state) or None, committed=lambda: list(committed),
               extra_inputs=("trial_reason_1", "trial_verified_1_0", "trial_verified_1_1", "trial_verified_1_2", "sidebar_nav"))
    w.saved, w.fake = saved, trial
    w.home_state_set = lambda **kw: w.home_state.set({**_peek(w.home_state), **kw})
    with reactive.isolate():
        w.home_state.set({"t3_audit_steps_by_plot": steps or {}, "t3_apply_count": 0, "t3_ghost_file": ""})
    _flush()
    _set(w, _record(w, committed=committed))
    _flush()
    return w


def _out(w, name):
    with reactive.isolate():
        return str(w.found[name]())


def _nodes(w):
    return _peek(w.home_state)["t3_audit_steps_by_plot"].get(PLACES_BUCKET, [])


def test_the_summary_counts_the_marks_and_a_new_trial_never_inherits_one(monkeypatch):
    w = _setup(monkeypatch)
    assert "0 of 3 places user verified" in _out(w, "trial_marks_summary_ui")
    w.live.set("trial_verified_1_0", True)
    w.live.set("trial_verified_1_2", True)
    _flush()
    assert "2 of 3 places user verified" in _out(w, "trial_marks_summary_ui")
    # a new Try (another number): the ticks of the older trial are not read, whatever the page still holds for those ids
    _set(w, _record(w, serial=2))
    _flush()
    assert "0 of 3 places user verified" in _out(w, "trial_marks_summary_ui"), "the ids carry the number of the Try: nothing of trial 1 is read for trial 2"


def test_typing_a_reason_and_ticking_a_mark_neither_end_the_trial_nor_draw_the_panel_again(monkeypatch):
    w = _setup(monkeypatch)
    runs = {"panel": 0, "summary": 0, "add": 0}

    @reactive.Effect
    def _watch_panel():
        runs["panel"] += 1
        w.found["trial_panel_ui"]()

    @reactive.Effect
    def _watch_summary():
        runs["summary"] += 1
        w.found["trial_marks_summary_ui"]()

    @reactive.Effect
    def _watch_add():
        runs["add"] += 1
        w.found["trial_add_ui"]()
    _flush()
    assert runs == {"panel": 1, "summary": 1, "add": 1}
    w.live.set("trial_verified_1_1", True)
    w.live.set("trial_reason_1", "poor quality")
    _flush()
    assert _peek(w.trial_state) is not None and w.notes == []
    assert runs["panel"] == 1, "the panel (it mounts the ticks and the reason) is not drawn again by a tick or a letter (R4)"
    assert runs["summary"] == 2, "the summary line follows the ticks"
    assert runs["add"] == 2, "the button's state follows 'the reason is not empty' (it changed once: no reason to a reason)"
    w.live.set("trial_reason_1", "poor quality, again")
    _flush()
    assert runs["add"] == 2 and runs["panel"] == 1, "typing more redraws nothing: the button's state did not change"


def test_the_add_button_is_disabled_until_a_reason_is_typed_and_a_line_says_why(monkeypatch):
    w = _setup(monkeypatch)
    off = _out(w, "trial_add_ui")
    assert "disabled" in off and "Write a reason to add this step" in off
    w.live.set("trial_reason_1", "   ")
    _flush()
    assert "disabled" in _out(w, "trial_add_ui"), "only spaces is no reason"
    w.live.set("trial_reason_1", "poor sequencing quality")
    _flush()
    on = _out(w, "trial_add_ui")
    assert "disabled" not in on and "Write a reason" not in on and 'id="trial_add"' in on and "Add to audit pipeline" in on


def test_add_without_a_reason_applies_nothing_and_keeps_the_trial(monkeypatch):
    w = _setup(monkeypatch)
    w.live.set("trial_add", 1)
    _flush()
    assert w.fake.calls == [] and _nodes(w) == [] and w.saved == [] and _peek(w.trial_state) is not None
    assert w.notes and "reason" in w.notes[-1]


def test_add_writes_the_step_at_all_the_places_with_the_marks_and_ends_the_trial(monkeypatch):
    w = _setup(monkeypatch)
    w.live.set("trial_verified_1_0", True)
    w.live.set("trial_verified_1_2", True)
    w.live.set("trial_reason_1", "poor sequencing quality")
    _flush()
    w.live.set("trial_add", 1)
    _flush()
    nodes = _nodes(w)
    assert [n["place"] for n in nodes] == list(PLACES), "D-0669: written at ALL the places, also the one not marked"
    assert [n["user_verified"] for n in nodes] == [True, False, True]
    assert {n["id"] for n in nodes} == {"dec1"} and {n["reason"] for n in nodes} == {"poor sequencing quality"} and {n["applied_at"] for n in nodes} == {"2026-11-27T10:00:00"}
    assert "verified_at" in nodes[0] and "verified_at" not in nodes[1]
    assert _peek(w.trial_state) is None and w.fake.discards >= 1, "the trial ended and its folder was emptied"
    state = _peek(w.home_state)
    assert state["t3_apply_count"] == 1, "the count of saves moves (the session panel counts the saves of the session)"
    assert _peek(w.pending) == [], "the condition was added: the staged rows go (the form is not drawn again by this, only emptied)"
    assert len(w.saved) == 1 and w.saved[0]["t3_audit_steps_by_plot"][PLACES_BUCKET] == nodes, "the session is saved once, with the step"
    assert w.notes == ["Step added to the audit pipeline at 3 places (2 of 3 places user verified)."]
    applied_arg, tried_arg, reason_arg = w.fake.calls[0]
    assert applied_arg == [] and len(tried_arg) == 3 and reason_arg == "poor sequencing quality", "the engine's apply_trial got the trial's own nodes"


def test_a_second_click_adds_nothing(monkeypatch):
    w = _setup(monkeypatch)
    w.live.set("trial_reason_1", "r")
    _flush()
    w.live.set("trial_add", 1)
    _flush()
    w.live.set("trial_add", 2)
    _flush()
    assert len(_nodes(w)) == 3 and len(w.fake.calls) == 1 and len(w.saved) == 1, "a step is added once"


def test_the_added_step_is_appended_to_the_steps_already_applied_and_none_is_lost(monkeypatch):
    earlier = make_audit_step("filter_row", {"column": "x", "op": "eq", "value": 1, "na": "keep"}, plot_scope=PLACES_BUCKET, reason="first", place="T1:ResFinder", node_id="old")
    inactive = {**make_audit_step("filter_row", {"column": "x", "op": "eq", "value": 2, "na": "keep"}, plot_scope=PLACES_BUCKET, reason="gone", place="T1:ResFinder", node_id="off"), "active": False}
    w = _setup(monkeypatch, committed=[earlier], steps={PLACES_BUCKET: [earlier, inactive]})
    w.live.set("trial_reason_1", "second")
    _flush()
    w.live.set("trial_add", 1)
    _flush()
    ids = [n["id"] for n in _nodes(w)]
    assert ids == ["old", "off", "dec1", "dec1", "dec1"], "the earlier steps stay in their order, an inactive one is not dropped, the new ones come last"
    assert [c[0] for c in w.fake.calls] == [[earlier]], "apply_trial was given the applied steps the audit copy uses (the active ones)"


@pytest.mark.parametrize("failure", [TrialRefused("Something changed since you tried this step. Nothing was applied. Try the step again."), RuntimeError("disk full")])
def test_a_failed_apply_leaves_nothing_applied_ends_the_trial_and_says_so(monkeypatch, failure):
    w = _setup(monkeypatch, raises=failure)
    before = _peek(w.home_state)
    w.live.set("trial_verified_1_0", True)
    w.live.set("trial_reason_1", "r")
    _flush()
    w.live.set("trial_add", 1)
    _flush()
    assert _peek(w.home_state) == before, "the committed list and the count are as they were"
    assert w.saved == [], "the session file is not written"
    assert _peek(w.trial_state) is None and w.fake.discards >= 1
    assert len(w.notes) == 1 and "Nothing was applied" in w.notes[0]


def test_a_change_of_the_world_after_the_try_ends_the_trial_instead_of_adding(monkeypatch):
    w = _setup(monkeypatch)
    w.live.set("trial_reason_1", "r")
    _flush()
    with reactive.isolate():
        w.pending.set([{**ROW, "value": 50.0}])
    w.live.set("trial_add", 1)
    _flush()
    assert _nodes(w) == [] and w.fake.calls == [] and _peek(w.trial_state) is None and w.saved == []


def test_the_reason_typed_is_a_draft_kept_for_the_next_trial_and_cleared_by_an_add(monkeypatch):
    w = _setup(monkeypatch)
    w.live.set("trial_reason_1", "draft text")
    _flush()
    _set(w, None)
    _flush()
    _set(w, _record(w, serial=2))
    html = _html(w)
    assert "draft text" in html, "a trial that ends or is tried again does not lose what was typed"
    w.live.set("trial_add", 1)
    _flush()


def test_a_tick_and_the_click_on_add_in_one_flush_are_both_seen(monkeypatch):
    """The tick and the click can reach the server together: the Add must count the tick (it reads the ticks itself, not the copy the tracker keeps, which may not have run yet)."""
    w = _setup(monkeypatch)
    w.live.set("trial_reason_1", "r")
    _flush()
    w.live.set("trial_verified_1_1", True)
    w.live.set("trial_add", 1)
    _flush()
    assert [n["user_verified"] for n in _nodes(w)] == [False, True, False]


def test_adding_a_drop_leaves_the_staged_rows_of_the_filters_panel_alone(monkeypatch):
    """FLOW-3: a drop and a condition are two steps; the Add of the drop must not clear the condition the user is building."""
    from app.modules.audit_try import KIND_DROP, drop_condition_lines
    w = _setup(monkeypatch)
    drop_nodes = tuple(make_audit_step("drop_column", {"column": "identity"}, plot_scope=PLACES_BUCKET, reason="", place=p, node_id="drop1") for p in PLACES)
    rows = _peek(w.pending)
    record = TrialRecord(world_of("audit", "r", ("a", "b"), [], [], ()), PLACES, drop_nodes, TrialResult(("sig",), tuple(PlaceEffect(p, p, 10, 10, "table changed", 8, 7) for p in PLACES)),
                         drop_condition_lines(["identity"]), 1, KIND_DROP)
    _set(w, record)
    _flush()
    w.live.set("trial_reason_1", "not needed for the heatmap")
    _flush()
    w.live.set("trial_add", 1)
    _flush()
    assert [n["node_type"] for n in _nodes(w)] == ["drop_column"] * 3 and {n["id"] for n in _nodes(w)} == {"drop1"}
    assert _peek(w.pending) == rows, "MUTATION: the Add of a drop clears the staged rows too"
    assert len(w.saved) == 1 and _peek(w.trial_state) is None


def test_a_reason_typed_survives_a_trip_to_another_user_space(monkeypatch):
    """D-0050: leaving HOME removes the box of the reason from the page and Shiny then reports it as empty text, which stays there when the user comes back. The text typed is a draft that must
    not be dropped by that report (the old reason boxes had the same rule). MUTATION: `_track_reason` takes every report as the user's."""
    w = _setup(monkeypatch)
    w.live.set("sidebar_nav", "Home")
    w.live.set("trial_reason_1", "poor sequencing quality")
    _flush()
    assert "disabled" not in _out(w, "trial_add_ui")
    w.live.set("sidebar_nav", "Gallery")
    w.live.set("trial_reason_1", "")                                  # the box left the page: Shiny reports it empty
    _flush()
    w.live.set("sidebar_nav", "Home")                                  # back: the stale empty value is still what the server holds
    _flush()
    assert "disabled" not in _out(w, "trial_add_ui"), "the draft was dropped by the report of the box that left the page"
    assert "poor sequencing quality" in _html(w), "the box is drawn again with the draft"
    w.live.set("trial_reason_1", "poor sequencing quality")           # the new box reports the draft it was drawn with
    _flush()
    w.live.set("trial_add", 1)
    _flush()
    assert {n["reason"] for n in _nodes(w)} == {"poor sequencing quality"}
    w2 = _setup(monkeypatch)
    w2.live.set("trial_reason_1", "typed on the page, then emptied by the user")
    _flush()
    w2.live.set("trial_reason_1", "")                                   # the user empties the box on the page: that IS the user's
    _flush()
    assert "disabled" in _out(w2, "trial_add_ui"), "an empty box on the page is an empty reason"
