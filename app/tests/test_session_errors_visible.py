"""The session screen tells the user when something fails (VERIF-FIX-2; D-0050 "No silent error that is the rule.").

Before this change the click handlers of the session screen wrapped Restore, Delete and the label in `except Exception: pass`:
a Restore that failed, a Delete that failed and a label that could not be saved gave the user nothing. The handlers are run
here without a browser, with a real `SessionManager` on a scratch folder, a fake input and a fake `ui.notification_show`.
Every text must be what happened, then "Suggestion:" (D-0099); what the code does after the error is not changed.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION S1  the Restore branch goes back to `except Exception: pass`
  MUTATION S2  the Delete branch goes back to `except Exception: pass`
  MUTATION S3  the label branch goes back to `except Exception: pass`
  MUTATION S4  a click that cannot be read for another reason than "the input does not exist yet" is swallowed again
  MUTATION S5  the same failure is told again at every re-run of the effect without a new click

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_errors_visible.py -q
"""
from types import SimpleNamespace

import pytest
from shiny import reactive, render, ui
from shiny.types import SilentException

import app.handlers.session_handlers as session_handlers
from app.modules.session_manager import SessionManager, make_audit_step

KEY = "aaaaaaaaaaaa:bbbbbbbbbbbb"
SAFE = KEY.replace(":", "_")
RESTORE, DELETE, LABEL = f"session_restore_{SAFE}", f"session_delete_{SAFE}", f"session_label_input_{SAFE}"


class FakeInput:
    """Reads like Shiny's input: a name that does not exist (yet) raises SilentException; a value may be an Exception to raise."""

    def __init__(self, **values):
        self.values = dict(values)

    def __getattr__(self, name):
        if name.startswith("__"):
            raise AttributeError(name)

        def read():
            if name not in self.values:
                raise SilentException()
            value = self.values[name]
            if isinstance(value, Exception):
                raise value
            return value
        return read


class Screen:
    """`define_session_server` with its decorators made plain, so the handlers are plain functions."""

    def __init__(self, tmp_path, monkeypatch, input_values=None, with_session=True, open_recipe="tiny"):
        self.functions = {}
        self.notes = []
        monkeypatch.setattr(reactive, "Effect", lambda fn: self.functions.setdefault(fn.__name__, fn))
        monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(render, "ui", lambda fn: self.functions.setdefault(fn.__name__, fn))
        monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", lambda message, **kw: self.notes.append((kw.get("type"), str(message))))
        self.modals = []
        monkeypatch.setattr(ui, "modal_show", lambda modal, **kw: self.modals.append(str(modal)))   # D-0378: Delete asks first
        monkeypatch.setattr(ui, "modal_remove", lambda *a, **k: None)
        monkeypatch.setattr(session_handlers, "bootloader", SimpleNamespace(is_enabled=lambda flag: True))
        self.manager = SessionManager(tmp_path / "user")
        self.manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
        self.input = FakeInput(session_import_upload=None, session_delete_all_btn=None, session_delete_all_confirm=None, session_delete_one_confirm=None,
                               **(input_values or {}))
        self.home_state = reactive.Value({"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64})
        self.log = reactive.Value([])
        self.issues = reactive.Value([])
        self.session = SimpleNamespace(on_flushed=lambda fn, once=True: fn())
        kwargs = {"session_processing_issues": self.issues} if with_session else {}
        session_handlers.define_session_server(
            self.input, lambda fn: fn, self.session, session_manager=self.manager, current_app_features=None,
            home_state=self.home_state, notification_log=self.log,
            safe_input=lambda i, k, d: open_recipe if k == "data_analysis_recipe_id" else d, **kwargs)

    def run(self, name):
        with reactive.isolate():
            return self.functions[name]()

    def delete_confirmed(self):
        """The click on a card's Delete (the scan), then the "Delete" button of the confirmation (D-0378)."""
        self.run("_handle_session_actions")
        assert self.modals, "Delete must ask before it deletes"
        return self.run("_handle_delete_one_confirmed")

    def texts(self, kind=None):
        return [m for t, m in self.notes if kind is None or t == kind]


def _suggestion_form(text):
    assert "Suggestion:" in text, text
    assert ". Suggestion:" in text, f"one period before Suggestion: {text}"
    assert "Fix:" not in text and "Suggestion: Suggestion" not in text, text


def test_a_restore_that_fails_is_told(tmp_path, monkeypatch):
    """MUTATION S1 fails here."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    monkeypatch.setattr(screen.manager, "read_assembly_ghost", lambda key: (_ for _ in ()).throw(PermissionError("disk is read only")))
    screen.run("_handle_session_actions")
    errors = screen.texts("error")
    assert len(errors) == 1 and "Restore" in errors[0] and "disk is read only" in errors[0] and KEY[:12] in errors[0], screen.notes
    _suggestion_form(errors[0])


def test_a_delete_that_fails_is_told_and_the_session_stays(tmp_path, monkeypatch):
    """MUTATION S2 fails here."""
    screen = Screen(tmp_path, monkeypatch, {DELETE: 1})
    monkeypatch.setattr(screen.manager, "delete_session", lambda key: (_ for _ in ()).throw(PermissionError("folder is locked")))
    screen.delete_confirmed()
    errors = screen.texts("error")
    assert len(errors) == 1 and "delete" in errors[0].lower() and "folder is locked" in errors[0], screen.notes
    _suggestion_form(errors[0])
    assert not [m for t, m in screen.notes if "Session deleted" in m], "no success text after a failed delete"


def test_a_label_that_cannot_be_saved_is_told(tmp_path, monkeypatch):
    """MUTATION S3 fails here."""
    screen = Screen(tmp_path, monkeypatch, {LABEL: "my label"})
    monkeypatch.setattr(screen.manager, "set_session_label", lambda key, label: (_ for _ in ()).throw(OSError("no space left")))
    screen.run("_handle_session_actions")
    errors = screen.texts("error")
    assert len(errors) == 1 and "label" in errors[0].lower() and "no space left" in errors[0], screen.notes
    _suggestion_form(errors[0])


def test_an_input_that_does_not_exist_yet_is_not_an_error(tmp_path, monkeypatch):
    """The control: a click box that is not rendered yet (SilentException) is the normal state, nothing is said."""
    screen = Screen(tmp_path, monkeypatch, {})
    screen.run("_handle_session_actions")
    assert screen.notes == []


def test_a_click_that_cannot_be_read_for_another_reason_is_told(tmp_path, monkeypatch):
    """MUTATION S4 fails here: a read that fails for a real reason is not the same as an input that does not exist yet."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: RuntimeError("input store is broken")})
    screen.run("_handle_session_actions")
    errors = screen.texts("error")
    assert len(errors) == 1 and "input store is broken" in errors[0], screen.notes
    _suggestion_form(errors[0])


def test_the_same_failure_is_told_once_per_click_not_at_every_re_run(tmp_path, monkeypatch):
    """MUTATION S5 fails here. The effect re-runs when any box of the screen changes while the click count stays above zero:
    the same failure of the same click is not told again; a new click is told again."""
    screen = Screen(tmp_path, monkeypatch, {DELETE: 1})
    monkeypatch.setattr(screen.manager, "delete_session", lambda key: (_ for _ in ()).throw(PermissionError("folder is locked")))
    screen.delete_confirmed()
    screen.run("_handle_session_actions")      # a re-run of the scan with the same click count asks nothing again
    assert len(screen.modals) == 1 and len(screen.texts("error")) == 1, screen.notes
    screen.input.values[DELETE] = 2
    screen.delete_confirmed()
    assert len(screen.texts("error")) == 2, screen.notes


def test_a_delete_that_works_still_works_and_says_so(tmp_path, monkeypatch):
    """The control: the success path is unchanged."""
    screen = Screen(tmp_path, monkeypatch, {DELETE: 1})
    screen.delete_confirmed()
    assert screen.texts("error") == []
    assert [m for t, m in screen.notes if "Session deleted" in m]
    assert not (screen.manager.root / KEY).exists()


def test_delete_asks_first_and_deletes_nothing_until_confirmed(tmp_path, monkeypatch):
    """D-0378: the click on Delete only opens the question; the folder is deleted by the Delete button of the question."""
    screen = Screen(tmp_path, monkeypatch, {DELETE: 1})
    screen.run("_handle_session_actions")
    assert len(screen.modals) == 1 and "Delete this session? It cannot be undone." in screen.modals[0] and KEY in screen.modals[0]
    assert (screen.manager.root / KEY).exists() and not [m for t, m in screen.notes if "deleted" in m]
    screen.run("_handle_session_actions")      # Cancel sends nothing: a re-run of the scan changes nothing
    assert (screen.manager.root / KEY).exists() and len(screen.modals) == 1
    screen.run("_handle_delete_one_confirmed")
    assert not (screen.manager.root / KEY).exists()


def test_the_modal_shows_the_label_of_the_session_when_it_has_one(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {DELETE: 1})
    screen.manager.set_session_label(KEY, "run of March")
    screen.run("_handle_session_actions")
    assert "run of March" in screen.modals[0]


def test_confirm_without_a_question_deletes_nothing(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {})
    screen.run("_handle_delete_one_confirmed")
    assert (screen.manager.root / KEY).exists()


def test_a_label_that_is_saved_is_not_told(tmp_path, monkeypatch):
    """The control: a label that saves gives no notice and is stored."""
    screen = Screen(tmp_path, monkeypatch, {LABEL: "run one"})
    screen.run("_handle_session_actions")
    assert screen.notes == []
    assert screen.manager.get_session_label(KEY) == "run one"
