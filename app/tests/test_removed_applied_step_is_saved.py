"""Removing an applied audit step saves the session, so that a Restore no longer brings the step back (task REMOVED-APPLIED-STEP-NOT-SAVED; D-0302, D-0314, D-0680).

Before: the bin of a card only changed the state; the session file (written by Apply) still held the step, and a Restore of the latest session file put it back.
What the design expects: removing an APPLIED step writes the session as Apply writes it (`audit_stack._write_t3_ghost`: a new `t3_<time>.json` with the steps that remain); removing a step that is only
PENDING writes nothing (pending steps are not saved, D-0302); the removal needs no reason (D-0314); with ghost save off nothing is written; a failed write is told in one plain line and the removal
stands. A step added with "Add to audit pipeline" is removed the same way, and what stays of the file is exactly the steps that remain, marks included.

Mutation index (seen failing): MUTATION R1 `_handle_delete` does not save.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_removed_applied_step_is_saved.py -q

# @deps
# consumes: app/handlers/audit_stack.py (_handle_delete), app/modules/session_manager.py (SessionManager, latest T3 ghost), app/tests/test_session_clicks_once.py (LiveInput)
# doc: .claude/knowledge/decision_ledger.md (D-0302, D-0314, D-0680)
# @end_deps
"""
import asyncio
from types import SimpleNamespace

import pytest
from shiny import reactive, render, ui

import app.handlers.audit_stack as audit_stack
from app.modules.audit_add import stamp_marks
from app.modules.session_manager import SessionManager, make_audit_step
from app.tests.test_session_clicks_once import LiveInput

RECIPE_HASH, DATA_HASH = "a" * 64, "b" * 64
KEY = SessionManager.compute_session_key(RECIPE_HASH, DATA_HASH)


def _node(node_id, place="T1:ResFinder"):
    return make_audit_step("filter_row", {"column": "identity", "op": "lt", "value": 90, "na": "remove"}, plot_scope="__places__", reason=f"reason {node_id}", place=place, node_id=node_id)


async def _flush(times=4):
    for _ in range(times):
        await reactive.flush()


class Screen:
    def __init__(self, tmp_path, monkeypatch, ghost_save=True, writable=True):
        self.notes = []
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
        monkeypatch.setattr(ui, "notification_show", lambda message, **kw: self.notes.append((kw.get("type"), str(message))))
        self.manager = SessionManager(tmp_path / "user")
        self.manager.write_assembly_ghost(KEY, "tiny", RECIPE_HASH, DATA_HASH, {}, {})
        if not writable:
            self.manager.writable = False
        self.input = LiveInput()
        self.steps = [_node("a"), _node("b", "T2:ResFinder")]
        self.state = reactive.Value({"data_analysis_recipe_sha256": RECIPE_HASH, "data_batch_hash": DATA_HASH, "data_analysis_recipe_id": "tiny",
                                     "t3_audit_steps_by_plot": {"__places__": list(self.steps)}, "_pending_t3_nodes": []})
        self.input.set("btn_apply", None)
        for node in self.steps:
            self.input.set(f"t3_delete_{node['id']}", 0)
        bootloader = SimpleNamespace(get_automation_setting=lambda *a: ghost_save)
        audit_stack.define_server(self.input, lambda fn: fn, SimpleNamespace(), wrangle_studio=SimpleNamespace(logic_stack=reactive.Value([]), apply_logic=0),
                                  audit_pending=reactive.Value(False), snapshot_steps=reactive.Value([]), active_cfg=lambda: SimpleNamespace(raw_config={}),
                                  active_collection_id=lambda: "x", home_mode=reactive.Value("audit"), home_state=self.state, session_manager=self.manager,
                                  notification_log=reactive.Value([]), bootloader=bootloader)

    def files(self):
        return sorted((self.manager.session_dir(KEY)).glob("t3_*.json"))

    def latest_steps(self):
        import json
        files = self.files()
        return [n["id"] for n in json.loads(files[-1].read_text())["t3_audit_steps_by_plot"].get("__places__", [])] if files else None

    def committed(self):
        with reactive.isolate():
            return [n["id"] for n in self.state.get()["t3_audit_steps_by_plot"]["__places__"]]


def test_removing_an_applied_step_writes_the_session_without_it_and_a_restore_does_not_bring_it_back(tmp_path, monkeypatch):
    async def scenario():
        s = Screen(tmp_path, monkeypatch)
        await _flush()
        assert s.files() == [], "nothing was saved yet"
        s.input.set("t3_delete_a", 1)
        await _flush()
        assert s.committed() == ["b"], "the removal is in the state"
        assert s.latest_steps() == ["b"], "the session file holds the steps that remain: a Restore of it does not bring 'a' back"
        s.input.set("t3_delete_b", 1)
        await _flush()
        assert s.committed() == [] and s.latest_steps() == [], "removing the last step saves an empty list, not the old one"
    asyncio.run(scenario())


def test_removing_a_pending_step_writes_nothing_and_a_removal_needs_no_reason(tmp_path, monkeypatch):
    async def scenario():
        s = Screen(tmp_path, monkeypatch)
        pending = _node("p")
        with reactive.isolate():
            s.state.set({**s.state.get(), "_pending_t3_nodes": [pending]})
        s.input.set("t3_delete_p", 0)
        await _flush()
        s.input.set("t3_delete_p", 1)
        await _flush()
        assert s.files() == [], "pending steps are not saved (D-0302), so removing one changes nothing that was saved"
        assert s.committed() == ["a", "b"]
    asyncio.run(scenario())


def test_a_step_added_with_marks_is_removed_the_same_way_and_the_rest_keeps_its_marks(tmp_path, monkeypatch):
    async def scenario():
        s = Screen(tmp_path, monkeypatch)
        added = stamp_marks([_node("m1", "T1:ResFinder"), _node("m1", "T2:ResFinder")], {"T1:ResFinder": "2026-11-27T09:00:00"})
        for n in added:
            n["id"] = "m1"
        with reactive.isolate():
            s.state.set({**s.state.get(), "t3_audit_steps_by_plot": {"__places__": s.steps + added}})
        s.input.set("t3_delete_m1", 0)
        await _flush()
        s.input.set("t3_delete_a", 1)
        await _flush()
        import json
        saved = json.loads(s.files()[-1].read_text())["t3_audit_steps_by_plot"]["__places__"]
        assert [n["id"] for n in saved] == ["b", "m1", "m1"] and [n.get("user_verified") for n in saved] == [None, True, False]
        s.input.set("t3_delete_m1", 1)
        await _flush()
        assert s.latest_steps() == ["b"], "removing a decision removes every copy of it, from the file too"
    asyncio.run(scenario())


def test_with_ghost_save_off_nothing_is_written_and_the_removal_stands(tmp_path, monkeypatch):
    async def scenario():
        s = Screen(tmp_path, monkeypatch, ghost_save=False)
        s.input.set("t3_delete_a", 1)
        await _flush()
        assert s.committed() == ["b"] and s.files() == []
    asyncio.run(scenario())


def test_a_session_that_cannot_be_written_is_told_in_one_plain_line_and_the_removal_stands(tmp_path, monkeypatch):
    async def scenario():
        s = Screen(tmp_path, monkeypatch, writable=False)
        s.input.set("t3_delete_a", 1)
        await _flush()
        assert s.committed() == ["b"]
        warnings = [m for t, m in s.notes if t == "warning"]
        assert len(warnings) == 1 and "not saved" in warnings[0]
    asyncio.run(scenario())
