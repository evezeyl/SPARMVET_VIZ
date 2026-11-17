"""Apply with a step that has no reason tells the user and applies nothing (APPLY-BLOCKED-1; D-0050, D-0099).

`handle_apply` built `blocked_types` as if `gatekeeper_blocked` returned nodes, but it returns ids (strings): the branch that must tell
the user "N step(s) need a reason" raised AttributeError (`'str' object has no attribute 'get'`) and the effect ended with an
unhandled error; nothing was told. The contract (ui_implementation_contract.md sections 3 and 12a): Apply is locked while a step that
needs a reason has none. The button is disabled then, so this branch is reached only when a click arrives before the button is drawn
again. The real handler runs here without a browser.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION B1  the kinds are read from the ids again (`n.get` on a string)
  MUTATION B2  the blocked branch applies the pending steps (does not return)
  MUTATION B3  the notice is not shown

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_apply_blocked.py -q
"""
from types import SimpleNamespace
from unittest import mock

import pytest
from shiny import reactive, render, ui
from shiny.types import SilentException

import app.handlers.audit_stack as audit_stack
from app.modules.session_manager import SessionManager, make_audit_step

PLOT = "subtab_p"


def _step(kind, reason, **params):
    base = {"filter_row": {"column": "a", "op": "eq", "value": 1, "dtype": "Int64"},
            "exclusion_row": {"column": "a", "op": "ne", "value": 2, "dtype": "Int64"},
            "drop_column": {"column": "b"}}[kind]
    return make_audit_step(kind, {**base, **params}, PLOT, reason)


class Screen:
    def __init__(self, tmp_path, monkeypatch, committed=(), pending=(), reasons=None):
        self.functions, self.notes = {}, []
        monkeypatch.setattr(reactive, "Effect", lambda fn: self.functions.setdefault(fn.__name__, fn))
        monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(reactive, "Calc", lambda fn: fn)
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
        for name in ("plot", "text", "data_frame", "download"):
            monkeypatch.setattr(render, name, lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", lambda message, **kw: self.notes.append((kw.get("type"), str(message))))
        self.manager = SessionManager(tmp_path / "user")
        self.state = reactive.Value({
            "data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64, "data_analysis_recipe_id": "tiny",
            "t3_audit_steps_by_plot": {PLOT: list(committed)} if committed else {}, "_pending_t3_nodes": list(pending)})
        self.audit_pending = reactive.Value(True)
        self.snapshot = reactive.Value(None)
        self.log = reactive.Value([])
        typed = dict(reasons or {})

        class Input:
            def __getattr__(inner, name):
                def read():
                    for nid, text in typed.items():
                        if name == f"t3_reason_{audit_stack._safe_input_suffix(nid)}":
                            return text
                    raise SilentException()
                return read
        studio = SimpleNamespace(logic_stack=SimpleNamespace(get=lambda: ["step"]), apply_logic=None)
        audit_stack.define_server(
            Input(), lambda fn=None, **k: fn if fn else (lambda f: f), mock.MagicMock(), wrangle_studio=studio,
            audit_pending=self.audit_pending, snapshot_steps=self.snapshot, active_cfg=lambda: SimpleNamespace(raw_config={}),
            active_collection_id=lambda: "C", home_state=self.state, session_manager=self.manager,
            notification_log=self.log, bootloader=SimpleNamespace(get_automation_setting=lambda *a: True))

    def apply(self):
        with reactive.isolate():
            self.functions["handle_apply"]()

    def current(self):
        with reactive.isolate():
            return self.state.get()

    def texts(self, kind=None):
        return [m for t, m in self.notes if kind is None or t == kind]

    def saves(self):
        return list(self.manager.root.glob("*/t3_*.json")) if self.manager.root.exists() else []


def test_apply_with_one_step_without_a_reason_tells_the_user_and_applies_nothing(tmp_path, monkeypatch):
    """MUTATION B1, B2 and B3 fail here. Before: AttributeError: 'str' object has no attribute 'get'."""
    step = _step("filter_row", "")
    screen = Screen(tmp_path, monkeypatch, pending=[step])
    screen.apply()
    errors = screen.texts("error")
    assert len(errors) == 1, screen.notes
    assert "1 step" in errors[0] and "no reason" in errors[0] and "row filter" in errors[0].lower(), errors[0]
    assert ". Suggestion: write a reason for each step, then press Apply" in errors[0], errors[0]
    assert "Fill in" not in errors[0], errors[0]
    state = screen.current()
    assert state["t3_audit_steps_by_plot"] == {}, "nothing was applied"
    assert [n["id"] for n in state["_pending_t3_nodes"]] == [step["id"]], "the step is still pending"
    assert not state.get("t3_apply_count"), "no apply was counted"
    assert screen.saves() == [], "nothing was saved"
    assert not any("audit steps applied" in m for _, m in screen.notes)


def test_apply_with_steps_of_two_kinds_names_how_many_of_each(tmp_path, monkeypatch):
    committed = [_step("drop_column", "kept because the column is empty")]
    pending = [_step("filter_row", ""), _step("exclusion_row", ""), _step("exclusion_row", "")]
    screen = Screen(tmp_path, monkeypatch, committed=committed, pending=pending)
    screen.apply()
    text = screen.texts("error")[0]
    assert "3 step(s) have no reason" in text, text
    assert "1 row filter" in text and "2 exclusion" in text and "drop" not in text.lower(), text
    assert len(screen.current()["t3_audit_steps_by_plot"][PLOT]) == 1 and screen.saves() == []


def test_copies_that_share_an_id_are_one_step(tmp_path, monkeypatch):
    """A decision propagated to three plots is one step with three copies: the user typed (or did not type) one reason."""
    one = _step("filter_row", "")
    copies = [{**one, "plot_scope": f"subtab_{i}"} for i in range(3)]
    screen = Screen(tmp_path, monkeypatch, pending=copies)
    screen.apply()
    assert "1 step(s) have no reason" in screen.texts("error")[0], screen.notes


def test_a_reason_typed_before_the_click_is_kept_when_another_step_still_has_none(tmp_path, monkeypatch):
    """The branch keeps what the user typed (as written): the typed reason is stored, the step without one blocks the Apply."""
    typed, empty = _step("filter_row", ""), _step("drop_column", "")
    screen = Screen(tmp_path, monkeypatch, pending=[typed, empty], reasons={typed["id"]: "a reason typed in the box"})
    screen.apply()
    assert "1 step(s) have no reason" in screen.texts("error")[0] and "drop column" in screen.texts("error")[0].lower()
    reasons = {n["id"]: n["reason"] for n in screen.current()["_pending_t3_nodes"]}
    assert reasons[typed["id"]] == "a reason typed in the box" and reasons[empty["id"]] == ""


def test_apply_with_every_reason_applies_as_before(tmp_path, monkeypatch):
    """The control."""
    step = _step("filter_row", "")
    screen = Screen(tmp_path, monkeypatch, pending=[step], reasons={step["id"]: "keep the good rows"})
    screen.apply()
    assert screen.texts("error") == []
    state = screen.current()
    assert [n["reason"] for n in state["t3_audit_steps_by_plot"][PLOT]] == ["keep the good rows"]
    assert state["_pending_t3_nodes"] == [] and state["t3_apply_count"] == 1
    assert len(screen.saves()) == 1
    assert [m for t, m in screen.notes if "audit steps applied" in m]
