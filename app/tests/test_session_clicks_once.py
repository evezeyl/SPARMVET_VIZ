"""One click on a session card acts exactly once (RESTORE-LOOP-1; D-0050 "No silent error that is the rule.").

The effect `_handle_session_actions` read "the click count is above zero" and acted on it, and it called `_notify`, which reads and
then sets the notification log: the effect depended on what it wrote, so every notice made it run again, and again it restored.
A real browser showed the page busy for ever and "Session restored" piled up. These tests run the REAL reactive graph without a
browser (real `reactive.Value` inputs, real `Effect`, `await reactive.flush()`), so a dependency of the effect on what it writes
is seen: the earlier tests of this screen call the effect as a plain function and cannot see it. A kill switch destroys the effects
after 40 notices, so that a loop fails the test and does not hang it.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION R1  the restore runs outside `reactive.isolate()` again
  MUTATION R2  `_is_new_click` answers "the count is above zero" again
  MUTATION R3  the delete runs outside `reactive.isolate()` again
  MUTATION R4  `_handle_delete_all_confirmed` does not tell a failure

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_clicks_once.py -q
"""
import asyncio
from types import SimpleNamespace

import pytest
from shiny import reactive, render, ui
from shiny.types import SilentException

import app.handlers.session_handlers as session_handlers
from app.modules.session_manager import SessionDeleteError, SessionManager, make_audit_step

KEY_A, KEY_B = "aaaaaaaaaaaa:bbbbbbbbbbbb", "cccccccccccc:dddddddddddd"
SAFE = lambda key: key.replace(":", "_")   # noqa: E731
LOOP_LIMIT = 40


class LiveInput:
    """Shiny's input with real reactive values; a name that does not exist yet creates its value (the dependency is registered)
    and raises SilentException when read, as Shiny does."""

    MISSING = object()

    def __init__(self):
        self.values: dict[str, reactive.Value] = {}

    def _value(self, name):
        return self.values.setdefault(name, reactive.Value(self.MISSING))

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)

        def read():
            value = self._value(name).get()
            if value is self.MISSING:
                raise SilentException()
            return value
        return read

    def set(self, name, value):
        self._value(name).set(value)


def _step(reason):
    return make_audit_step("filter_row", {"column": "a", "op": "eq", "value": 1, "dtype": "Int64"}, "subtab_p", reason)


class Live:
    def __init__(self, tmp_path, monkeypatch):
        self.notes, self.effects = [], []
        real_effect = reactive.Effect

        def effect(fn):
            made = real_effect(fn)
            self.effects.append(made)
            return made

        def shown(message, **kw):
            self.notes.append((kw.get("type"), str(message)))
            if len(self.notes) > LOOP_LIMIT:      # the kill switch: a loop fails the test, it does not hang it
                for made in self.effects:
                    made.destroy()
        monkeypatch.setattr(reactive, "Effect", effect)
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
        monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", shown)
        monkeypatch.setattr(ui, "modal_show", lambda *a, **k: None)
        monkeypatch.setattr(ui, "modal_remove", lambda *a, **k: None)
        monkeypatch.setattr(session_handlers, "bootloader", SimpleNamespace(is_enabled=lambda flag: True))
        self.manager = SessionManager(tmp_path / "user")
        for key, tag in ((KEY_A, "a"), (KEY_B, "c")):
            self.manager.write_assembly_ghost(key, "tiny", tag * 64, "b" * 64, {}, {})
        self.manager.write_t3_ghost(KEY_A, "tiny", "a" * 64, "b" * 64, t3_audit_steps_by_plot={"subtab_p": [_step("saved")]})
        self.input = LiveInput()
        for name in ("session_import_upload", "session_delete_all_btn", "session_delete_all_confirm"):
            self.input.set(name, None)
        self.home_state = reactive.Value({"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64})
        self.log = reactive.Value([])
        self.issues = reactive.Value([])
        self.session = SimpleNamespace(on_flushed=lambda fn, once=True: fn())
        session_handlers.define_session_server(
            self.input, lambda fn: fn, self.session, session_manager=self.manager, current_app_features=None,
            home_state=self.home_state, notification_log=self.log, session_processing_issues=self.issues,
            safe_input=lambda i, k, d: "tiny" if k == "data_analysis_recipe_id" else d)

    def texts(self, word):
        return [m for _, m in self.notes if word in m]

    def state(self):
        with reactive.isolate():
            return self.home_state.get()


async def _flush(times=3):
    for _ in range(times):
        await reactive.flush()


def _live(tmp_path, monkeypatch):
    return Live(tmp_path, monkeypatch)


def test_one_restore_click_restores_once_and_later_re_runs_do_not_repeat_it(tmp_path, monkeypatch):
    """MUTATION R1 and MUTATION R2 fail here (the notices pile up past the kill switch)."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        await _flush()
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 1)
        live.input.set(f"session_restore_{SAFE(KEY_B)}", 0)
        await _flush(6)
        assert len(live.texts("Session restored")) == 1, live.notes[:6]
        assert [n["reason"] for n in live.state()["t3_audit_steps_by_plot"]["subtab_p"]] == ["saved"]
        # things that re-run the effect: another box changes, a label is edited, the effect's own writes
        live.input.set(f"session_label_input_{SAFE(KEY_B)}", "a new label")
        await _flush(6)
        live.input.set(f"session_restore_{SAFE(KEY_B)}", 0)
        await _flush(3)
        assert len(live.texts("Session restored")) == 1, "a later re-run repeated the click"
        assert live.manager.get_session_label(KEY_B) == "a new label", "a label is saved once per change"
        # a second click is a second restore
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 2)
        await _flush(6)
        assert len(live.texts("Session restored")) == 2
    asyncio.run(scenario())


def test_a_step_added_after_a_restore_is_not_overwritten_by_a_later_re_run(tmp_path, monkeypatch):
    """The science risk: each repeat of the restore put the saved steps back over what the user did after it."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        await _flush()
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 1)
        await _flush(6)
        with reactive.isolate():
            state = live.home_state.get()
            new_step = _step("added after the restore")
            live.home_state.set({**state, "t3_audit_steps_by_plot": {"subtab_p": state["t3_audit_steps_by_plot"]["subtab_p"] + [new_step]}})
        live.input.set(f"session_label_input_{SAFE(KEY_B)}", "x")
        live.input.set(f"session_delete_{SAFE(KEY_B)}", 1)
        await _flush(8)
        reasons = [n["reason"] for n in live.state()["t3_audit_steps_by_plot"]["subtab_p"]]
        assert reasons == ["saved", "added after the restore"], reasons
    asyncio.run(scenario())


def test_one_delete_click_deletes_once(tmp_path, monkeypatch):
    """MUTATION R3 fails here."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        calls = []
        real = live.manager.delete_session
        live.manager.delete_session = lambda key: calls.append(key) or real(key)
        await _flush()
        live.input.set(f"session_label_input_{SAFE(KEY_B)}", "")     # the card is drawn: its label box exists
        live.input.set(f"session_delete_{SAFE(KEY_B)}", 1)
        await _flush(6)
        live.input.set(f"session_label_input_{SAFE(KEY_A)}", "other box changed")
        await _flush(6)
        assert calls == [KEY_B], calls
        assert len(live.texts("Session deleted")) == 1, live.notes[:6]
        assert [s["session_key"] for s in live.manager.list_all_sessions()] == [KEY_A]
        assert not (live.manager.root / KEY_B).exists(), "the label step re-created the folder of the session that was just deleted"
    asyncio.run(scenario())


def test_the_effect_does_not_depend_on_what_it_writes(tmp_path, monkeypatch):
    """MUTATION R1 and MUTATION R3 fail here (R2 stops the repeat, not the dependency). A dependency exists only in the run that
    reads the value, so it is counted where it shows: a click makes the effect run ONCE. If the restore or the delete ran in the
    effect's own context, what it writes (the notification log, `home_state`, the list version) would invalidate the effect and it
    would run a second time (R1 to R3 of ui_implementation_contract.md section 14: an effect never depends on a value it sets)."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        runs = []
        real = live.manager.list_all_sessions
        live.manager.list_all_sessions = lambda: runs.append(1) or real()
        await _flush()
        for name, value in ((f"session_restore_{SAFE(KEY_A)}", 1), (f"session_delete_{SAFE(KEY_B)}", 1)):
            before = len(runs)
            live.input.set(name, value)
            await _flush(6)
            assert len(runs) - before == 1, f"{name}: the effect ran {len(runs) - before} times for one click"
        assert len(live.texts("Session restored")) == 1 and len(live.texts("Session deleted")) == 1
    asyncio.run(scenario())


def test_a_restore_and_a_delete_on_different_cards_both_run_once(tmp_path, monkeypatch):
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        await _flush()
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 1)
        live.input.set(f"session_delete_{SAFE(KEY_B)}", 1)
        await _flush(8)
        assert len(live.texts("Session restored")) == 1 and len(live.texts("Session deleted")) == 1, live.notes
    asyncio.run(scenario())


def test_a_card_drawn_again_starts_its_count_over(tmp_path, monkeypatch):
    """The card is rendered again after another card is deleted: its button sends 0, and the next click (1) is a new click."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        await _flush()
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 1)
        await _flush(4)
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 0)
        await _flush(2)
        live.input.set(f"session_restore_{SAFE(KEY_A)}", 1)
        await _flush(4)
        assert len(live.texts("Session restored")) == 2, live.notes
    asyncio.run(scenario())


# -- "Delete all sessions" told when it fails ------------------------------------------------------------------------------

def _delete_all(live, monkeypatch, fail_on=None, error=PermissionError("folder is locked")):
    real = live.manager.delete_session

    def delete(key):
        if key == fail_on:
            raise error
        real(key)
    live.manager.delete_session = delete


def test_delete_all_that_fails_says_what_was_and_was_not_deleted(tmp_path, monkeypatch):
    """MUTATION R4 fails here. Before: an uncaught OSError ended the user's session with a traceback."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        keys = [s["session_key"] for s in live.manager.list_all_sessions()]
        _delete_all(live, monkeypatch, fail_on=keys[1])
        await _flush()
        live.input.set("session_delete_all_confirm", 1)
        await _flush(4)
        errors = [m for t, m in live.notes if t == "error"]
        assert len(errors) == 1, live.notes
        text = errors[0]
        assert "1 session(s) were deleted" in text and keys[1][:24] in text and "folder is locked" in text, text
        assert "1 session(s) are still there" in text or "are still there" in text, text
        assert ". Suggestion:" in text, text
        assert [s["session_key"] for s in live.manager.list_all_sessions()] == [keys[1]], "what the text says is what is on disk"
    asyncio.run(scenario())


def test_delete_all_that_works_still_says_how_many(tmp_path, monkeypatch):
    """The control."""
    async def scenario():
        live = _live(tmp_path, monkeypatch)
        await _flush()
        live.input.set("session_delete_all_confirm", 1)
        await _flush(4)
        assert [m for t, m in live.notes] == ["🗑 Deleted 2 session(s)."], live.notes
        assert live.manager.list_all_sessions() == []
    asyncio.run(scenario())


def test_the_manager_reports_what_it_deleted_before_the_failure(tmp_path):
    manager = SessionManager(tmp_path / "user")
    for key, tag in ((KEY_A, "a"), (KEY_B, "c")):
        manager.write_assembly_ghost(key, "tiny", tag * 64, "b" * 64, {}, {})
    keys = [s["session_key"] for s in manager.list_all_sessions()]
    real = manager.delete_session
    manager.delete_session = lambda key: (_ for _ in ()).throw(OSError("locked")) if key == keys[1] else real(key)
    with pytest.raises(SessionDeleteError) as caught:
        manager.delete_all_sessions()
    assert caught.value.deleted == [keys[0]] and caught.value.failed_key == keys[1] and caught.value.not_attempted == []
