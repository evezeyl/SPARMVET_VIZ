"""A session file that cannot be read is never skipped without a word (VERIF-FIX-2; D-0050 "No silent error that is the rule.").

`SessionManager` used to skip an unreadable save in `list_t3_ghosts`, leave an unreadable session out of `list_all_sessions` and reset
a label when `assembly.json` could not be read, all with `except Exception`. The Restore then restored an OLDER save and said only
"Session restored", and the panel simply did not show the session. What the code does is not changed (the damaged file is still
skipped, the older save is still restored); the user is told which file was skipped, why, and what was restored instead.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION U1  `scan_t3_ghosts` forgets the skipped file
  MUTATION U2  `scan_sessions` forgets the unreadable session
  MUTATION U3  the Restore does not tell the skipped save
  MUTATION U4  the session list render does not report the unreadable session
  MUTATION U5  `write_assembly_ghost` does not say that the label was lost

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_unreadable_files_told.py -q
"""
import time

from shiny import reactive

from app.modules.session_manager import SessionManager, make_audit_step
from app.tests.test_session_errors_visible import KEY, RESTORE, Screen


def _step(reason):
    return make_audit_step("filter_row", {"column": "a", "op": "eq", "value": 1, "dtype": "Int64"}, "subtab_p", reason)


def _save(manager, reason):
    path = manager.write_t3_ghost(KEY, "tiny", "a" * 64, "b" * 64, "T2", t3_audit_steps_by_plot={"subtab_p": [_step(reason)]})
    time.sleep(0.002)   # the file name holds a time stamp: two saves never share one
    return path


def test_an_unreadable_save_is_skipped_and_named(tmp_path):
    """MUTATION U1 fails here."""
    manager = SessionManager(tmp_path / "user")
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    older = _save(manager, "older save")
    newest = _save(manager, "newest save")
    newest.write_text("{ this is not json")
    ghosts, skipped = manager.scan_t3_ghosts(KEY)
    assert [g["file"] for g in ghosts] == [str(older)], "the damaged newest save is skipped, as before"
    assert len(skipped) == 1 and skipped[0]["name"] == newest.name and skipped[0]["reason"], skipped
    assert [g["file"] for g in manager.list_t3_ghosts(KEY)] == [str(older)], "list_t3_ghosts gives what it always gave"


def test_a_readable_session_has_nothing_skipped(tmp_path):
    """The control."""
    manager = SessionManager(tmp_path / "user")
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    _save(manager, "one")
    ghosts, skipped = manager.scan_t3_ghosts(KEY)
    assert len(ghosts) == 1 and skipped == []
    sessions, unreadable = manager.scan_sessions()
    assert [s["session_key"] for s in sessions] == [KEY] and unreadable == []


def test_an_unreadable_session_is_left_out_of_the_list_and_named(tmp_path):
    """MUTATION U2 fails here."""
    manager = SessionManager(tmp_path / "user")
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    other = "cccccccccccc:dddddddddddd"
    manager.write_assembly_ghost(other, "tiny", "c" * 64, "d" * 64, {}, {})
    (manager.root / other / "assembly.json").write_text("not json at all")
    sessions, unreadable = manager.scan_sessions()
    assert [s["session_key"] for s in sessions] == [KEY], "the damaged session is still left out of the list"
    assert [u["session_key"] for u in unreadable] == [other] and unreadable[0]["reason"], unreadable
    assert [s["session_key"] for s in manager.list_all_sessions()] == [KEY], "list_all_sessions gives what it always gave"


def test_a_damaged_save_inside_a_listed_session_is_named_too(tmp_path):
    manager = SessionManager(tmp_path / "user")
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {})
    _save(manager, "fine")
    bad = _save(manager, "bad")
    bad.write_text("[]")   # valid JSON, not a session file
    sessions, unreadable = manager.scan_sessions()
    assert [s["session_key"] for s in sessions] == [KEY]
    assert [u["name"] for u in unreadable] == [bad.name], unreadable


def test_a_restore_that_skips_the_newest_save_says_which_was_skipped_and_which_was_restored(tmp_path, monkeypatch):
    """MUTATION U3 fails here. Before: 'Session restored (<older date>)' and nothing about the damaged file."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    manager = screen.manager
    older = _save(manager, "older save")
    newest = _save(manager, "newest save")
    newest.write_text("{ this is not json")
    older_date = manager.list_t3_ghosts(KEY)[0]["saved_at"][:16]
    screen.run("_handle_session_actions")
    with reactive.isolate():
        state = screen.home_state.get()
    assert [n["reason"] for n in state["t3_audit_steps_by_plot"]["subtab_p"]] == ["older save"], "the older save is still restored"
    warnings = screen.texts("warning")
    assert len(warnings) == 1, screen.notes
    text = warnings[0]
    assert newest.name in text and older_date in text and "skipped" in text.lower() and "OLDER" in text, text
    assert ". Suggestion:" in text, text
    assert older.name not in text


def test_a_restore_whose_every_save_is_damaged_says_so(tmp_path, monkeypatch):
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    only = _save(screen.manager, "only save")
    only.write_text("{ not json")
    screen.run("_handle_session_actions")
    warnings = screen.texts("warning")
    assert len(warnings) == 1 and only.name in warnings[0] and "Suggestion:" in warnings[0], screen.notes
    assert [m for t, m in screen.notes if "No T3 saves" in m], "the fresh start is still said"


def test_a_restore_with_nothing_damaged_says_nothing_extra(tmp_path, monkeypatch):
    """The control."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save(screen.manager, "fine")
    screen.run("_handle_session_actions")
    assert screen.texts("warning") == [] and screen.texts("error") == []


def test_the_session_list_reports_an_unreadable_session(tmp_path, monkeypatch):
    """MUTATION U4 fails here: the render may not write a reactive value, so it reports through the plot issue reporter."""
    screen = Screen(tmp_path, monkeypatch, {})
    other = "cccccccccccc:dddddddddddd"
    screen.manager.write_assembly_ghost(other, "tiny", "c" * 64, "d" * 64, {}, {})
    (screen.manager.root / other / "assembly.json").write_text("not json at all")
    screen.run("session_management_ui")
    with reactive.isolate():
        alerts = screen.log.get()
        issues = screen.issues.get()
    assert len(alerts) == 1 and other in alerts[0]["msg"] and ". Suggestion:" in alerts[0]["msg"], alerts
    assert len(issues) == 1 and issues[0]["severity"] == "error" and other in issues[0]["problem"], issues
    screen.run("session_management_ui")   # a second drawing of the list does not add it again
    with reactive.isolate():
        assert len(screen.log.get()) == 1 and len(screen.issues.get()) == 1


def test_a_label_lost_when_assembly_json_cannot_be_read_is_told(tmp_path):
    """MUTATION U5 fails here. The old record is rewritten (as before) and its label is lost: the caller is told."""
    manager = SessionManager(tmp_path / "user")
    path = manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, label="run one")
    path.write_text("{ broken")
    problems = []
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, on_problem=problems.append)
    assert len(problems) == 1 and "run one" not in problems[0] and "label" in problems[0].lower(), problems
    assert ". Suggestion:" in problems[0]
    assert manager.get_session_label(KEY) == "", "the rewrite still resets the label, as before"


def test_a_label_that_can_be_read_is_kept_and_nothing_is_told(tmp_path):
    """The control."""
    manager = SessionManager(tmp_path / "user")
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, label="run one")
    problems = []
    manager.write_assembly_ghost(KEY, "tiny", "a" * 64, "b" * 64, {}, {}, on_problem=problems.append)
    assert problems == [] and manager.get_session_label(KEY) == "run one"
