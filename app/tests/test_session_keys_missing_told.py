"""A session with no recipe or data keys says so, in the three places that used to say nothing (VERIF-FIX-2, E3 and place 7;
D-0050 "No silent error that is the rule.").

1. `_sync_session_provenance` (HOME) swallowed every error while it computed the recipe and data keys of the session or wrote the
   first record of the session: the keys stayed empty, and the next two places then went quiet too.
2. `save_audit_session` (the save after an added or removed audit step) returned with nothing saved when the keys were empty, and the user read
   "audit steps applied".
3. The Restore compared the saved keys with the keys of the open view only when both were there, and warned of nothing otherwise.
What the code does after is not changed (the effect still goes on, the Add still adds, the Restore still restores).

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION K1  the outer `except` of `_sync_session_provenance` goes back to `pass`
  MUTATION K2  the inner `except` (the first record of the session cannot be written) goes back to `pass`
  MUTATION K3  `save_audit_session` returns nothing again when the keys are empty
  MUTATION K4  the Restore does not say that the keys could not be compared
  MUTATION K5  the same sync failure is told again at every re-run of the effect

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_keys_missing_told.py -q
"""
from types import SimpleNamespace
from unittest import mock

import pytest
from shiny import reactive, render, ui

import app.handlers.home_theater as home_theater
from app.modules.audit_session_save import save_audit_session
from app.modules.session_manager import SessionManager
from app.tests.test_session_errors_visible import KEY, RESTORE, Screen
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.tests.test_cache_chain import World
from app.tests.test_session_unreadable_files_told import _save



@pytest.fixture(autouse=True)
def _fresh_cache():
    clear_data_analysis_recipe_cache()
    yield
    clear_data_analysis_recipe_cache()


class Home:
    """`home_theater.define_server` with every part a fake except the one under test: the effect `_sync_session_provenance`."""

    def __init__(self, tmp_path, monkeypatch, source_files=None, input_object=None, discovered=None):
        self.functions, self.notes = {}, []
        def effect(fn=None, *, priority=0):
            """Used bare (`@reactive.Effect`) or with arguments (`@reactive.Effect(priority=10)`)."""
            def keep(f):
                return self.functions.setdefault(f.__name__, f)
            return keep if fn is None else keep(fn)
        monkeypatch.setattr(reactive, "Effect", effect)
        monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(reactive, "Calc", lambda fn: fn)
        monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
        for name in ("plot", "text", "data_frame", "download"):
            monkeypatch.setattr(render, name, lambda *a, **k: (lambda fn: fn))
        monkeypatch.setattr(ui, "notification_show", lambda message, **kw: self.notes.append((kw.get("type"), str(message))))
        self.world = World(tmp_path)
        self.bootloader = mock.MagicMock()
        self.bootloader.get_location.side_effect = (
            lambda key: self.world.data_analysis_recipes_dir if key == "data_analysis_recipes" else self.world.root / "user")
        self.bootloader.get_default_data_analysis_recipe_or_none.return_value = "tiny"
        self.bootloader.is_enabled.side_effect = lambda flag: flag in ("t3_sandbox_enabled", "interactivity_enabled")   # Audit mode exists (Reshuffle belongs to it, D-0341)
        self.orchestrator = self.world.orch
        if discovered:
            self.bootloader.discovered_data_analysis_recipes = {"tiny": self.world.data_analysis_recipes_dir / "tiny.yaml"}
        self.manager = SessionManager(tmp_path / "user")
        self.home_state = reactive.Value({})
        self.log = reactive.Value([])
        home_theater.define_server(
            input_object or mock.MagicMock(), lambda *a, **k: (lambda fn: fn) if not (a and callable(a[0])) else a[0], mock.MagicMock(),
            bootloader=self.bootloader, wrangle_studio=mock.MagicMock(), dev_studio=mock.MagicMock(),
            orchestrator=self.orchestrator, viz_factory=mock.MagicMock(), gallery_viewer=mock.MagicMock(),
            current_app_features=mock.MagicMock(), anchor_path=mock.MagicMock(), tier1_anchor=mock.MagicMock(),
            active_cfg=lambda: SimpleNamespace(raw_config={}), active_collection_id=mock.MagicMock(),
            safe_input=lambda i, k, d: "tiny" if k == "data_analysis_recipe_id" else d,
            active_home_subtab=mock.MagicMock(), home_mode=reactive.Value("audit"), data_view=reactive.Value("T3"), source_table=reactive.Value(None),   # Audit mode: Reshuffle belongs to it (D-0341)
            home_state=self.home_state, session_manager=self.manager, notification_log=self.log)

    def sync(self):
        with reactive.isolate():
            self.functions["_sync_session_provenance"]()

    def texts(self, kind=None):
        return [m for t, m in self.notes if kind is None or t == kind]


def test_the_control_a_session_whose_keys_can_be_computed_gets_them_and_a_record_and_no_notice(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch)
    home.sync()
    with reactive.isolate():
        state = home.home_state.get()
    assert state["data_analysis_recipe_sha256"] and state["data_batch_hash"]
    assert len(home.manager.list_all_sessions()) == 1
    assert home.notes == []


def test_keys_that_cannot_be_computed_are_told(tmp_path, monkeypatch):
    """MUTATION K1 fails here. Before: nothing; the state keys stay empty."""
    home = Home(tmp_path, monkeypatch)
    monkeypatch.setattr(home.orchestrator, "get_source_files", mock.Mock(side_effect=OSError("the data folder is not readable")))
    home.sync()
    errors = home.texts("error")
    assert len(errors) == 1 and "data folder is not readable" in errors[0], home.notes
    assert "keys" in errors[0] and ". Suggestion:" in errors[0], errors[0]
    with reactive.isolate():
        assert not home.home_state.get().get("data_batch_hash"), "the state is not changed by the notice"


def test_a_session_record_that_cannot_be_written_is_told(tmp_path, monkeypatch):
    """MUTATION K2 fails here."""
    home = Home(tmp_path, monkeypatch)
    monkeypatch.setattr(home.manager, "write_assembly_ghost", mock.Mock(side_effect=PermissionError("read-only folder")))
    home.sync()
    errors = home.texts("error")
    assert len(errors) == 1 and "read-only folder" in errors[0] and "record" in errors[0], home.notes
    assert ". Suggestion:" in errors[0]
    with reactive.isolate():
        assert home.home_state.get()["data_batch_hash"], "the keys were set before the record: still the case"


def test_a_failure_is_told_once_not_at_every_re_run_and_again_after_it_recovered(tmp_path, monkeypatch):
    """MUTATION K5 fails here."""
    home = Home(tmp_path, monkeypatch)
    real = home.orchestrator.get_source_files
    failing = mock.Mock(side_effect=OSError("the data folder is not readable"))
    monkeypatch.setattr(home.orchestrator, "get_source_files", failing)
    home.sync()
    home.sync()
    assert len(home.texts("error")) == 1, home.notes
    monkeypatch.setattr(home.orchestrator, "get_source_files", real)
    home.sync()                       # recovers
    assert len(home.texts("error")) == 1
    monkeypatch.setattr(home.orchestrator, "get_source_files", failing)
    home.sync()
    assert len(home.texts("error")) == 2, home.notes


def test_a_label_lost_while_the_record_is_rewritten_is_told(tmp_path, monkeypatch):
    home = Home(tmp_path, monkeypatch)
    home.sync()
    (home.manager.root / home.manager.list_all_sessions()[0]["session_key"] / "assembly.json").write_text("{ broken")
    with reactive.isolate():
        home.home_state.set({})        # the keys are computed again
    home.sync()
    warnings = home.texts("warning")
    assert len(warnings) == 1 and "label" in warnings[0] and ". Suggestion:" in warnings[0], home.notes


def test_apply_with_no_keys_says_the_steps_were_not_saved():
    """MUTATION K3 fails here. Before: `save_audit_session` returned None and the screen said 'audit steps applied'."""
    manager = mock.Mock()
    for state in ({}, {"data_analysis_recipe_sha256": "a" * 64}, {"data_batch_hash": "b" * 64}):
        text = save_audit_session(state, manager)
        assert text and "not saved" in text and ". Suggestion:" in text, text
    manager.write_t3_ghost.assert_not_called()


def test_apply_with_keys_still_saves_and_says_nothing(tmp_path):
    """The control."""
    manager = SessionManager(tmp_path / "user")
    text = save_audit_session({"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64}, manager)
    assert text is None
    assert manager.root.glob("*/t3_*.json")


@pytest.mark.parametrize("current", [{}, {"data_analysis_recipe_sha256": "a" * 64}])
def test_a_restore_with_no_data_key_to_compare_is_refused_and_says_so(tmp_path, monkeypatch, current):
    """MUTATION K4 fails here. G1 (Eve 2026-11-28): with no data key in the open view the data cannot be compared, so nothing is restored."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save(screen.manager, "the steps")
    with reactive.isolate():
        screen.home_state.set(dict(current))
    screen.run("_handle_session_actions")
    errors = screen.texts("error")
    assert len(errors) == 1 and "could not be compared" in errors[0] and ". Suggestion:" in errors[0], screen.notes
    with reactive.isolate():
        assert not screen.home_state.get().get("audit_pipeline"), "nothing is restored"


def test_a_restore_with_no_recipe_key_still_says_so_and_restores(tmp_path, monkeypatch):
    """MUTATION K4 fails here: the data key is there and equal, the recipe key is missing: the old warning stays (the recipe part is not G1)."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save(screen.manager, "the steps")
    with reactive.isolate():
        screen.home_state.set({"data_batch_hash": "b" * 64})
    screen.run("_handle_session_actions")
    warnings = screen.texts("warning")
    assert len(warnings) == 1 and "compare" in warnings[0] and ". Suggestion:" in warnings[0], screen.notes
    with reactive.isolate():
        assert screen.home_state.get()["audit_pipeline"], "the restore still happens"


def test_a_restore_with_both_keys_present_and_equal_says_nothing_extra(tmp_path, monkeypatch):
    """The control."""
    screen = Screen(tmp_path, monkeypatch, {RESTORE: 1})
    _save(screen.manager, "the steps")
    screen.run("_handle_session_actions")
    assert screen.texts("warning") == []
