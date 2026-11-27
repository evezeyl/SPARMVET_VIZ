"""The session panel is drawn again only for what it shows (task HOME-SESSION-PANEL-REDRAWS-ON-ANY-STATE; ui_implementation_contract.md section 14, R1 to R4).

Real reactive graph, no browser: the render function of `session_management_ui` is run by an effect that counts how often it runs, and `home_state` is written the way HOME writes it.
What the panel shows of `home_state`: the session key of the open recipe and data (the two hashes) and, through the saves counted per session, the apply count. Any other key (the open plot, the
shown place, the collapse of an accordion) must not draw it again, or the session group a person opened closes (found 2026-11-27 in the browser: `test_session_panel_stays_open_browser.py`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_session_panel_dependencies.py -q

MUTATION (seen failing, then restored): the render reads `home_state.get()` itself again (the old code): the writes of unrelated keys draw the panel.
"""
import asyncio
from types import SimpleNamespace

from shiny import reactive, render, ui

import app.handlers.session_handlers as session_handlers
from app.tests.test_session_clicks_once import LiveInput

BASE = {"data_analysis_recipe_sha256": "a" * 64, "data_batch_hash": "b" * 64, "audit_saves_count": 0, "active_plot_subtab": "subtab_x", "audit_shown_place": None}


class _Manager:
    def scan_sessions(self):
        return [], []

    def list_all_sessions(self):
        return []


def _world(monkeypatch):
    renders = {"n": 0}
    found = {}
    monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
    monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(ui, "notification_show", lambda *a, **k: None)
    monkeypatch.setattr(session_handlers, "bootloader", SimpleNamespace(is_enabled=lambda flag: True))
    home_state = reactive.Value(dict(BASE))

    def output(fn):
        found[fn.__name__] = fn
        return fn
    session = SimpleNamespace(on_flushed=lambda fn, once=True: fn())
    live_input = LiveInput()
    for name in ("session_import_upload", "session_delete_all_btn", "session_delete_all_confirm", "session_delete_one_confirm"):
        live_input.set(name, None)
    session_handlers.define_session_server(
        live_input, output, session, session_manager=_Manager(), current_app_features=None, home_state=home_state,
        notification_log=reactive.Value([]), session_processing_issues=reactive.Value([]), safe_input=lambda i, k, d: d)

    @reactive.Effect
    def _draw():
        found["session_management_ui"]()
        renders["n"] += 1
    return home_state, renders


def _flush(times=4):
    async def go():
        for _ in range(times):
            await reactive.flush()
    asyncio.run(go())


def _write(home_state, **changes):
    with reactive.isolate():
        home_state.set({**home_state.get(), **changes})
    _flush()


def test_a_write_of_a_key_the_panel_does_not_show_does_not_draw_it(monkeypatch):
    home_state, renders = _world(monkeypatch)
    _flush()
    first = renders["n"]
    assert first >= 1
    for changes in ({"active_plot_subtab": "subtab_y"}, {"audit_shown_place": "T1:ResFinder"}, {"audit_shown_place": None}, {"plot_collapse_state": {"p": True}}):
        _write(home_state, **changes)
    assert renders["n"] == first, "the panel was drawn again for a key it does not show: the session group a person opened would close"


def test_a_change_of_the_session_key_or_of_the_saves_counted_draws_the_panel(monkeypatch):
    home_state, renders = _world(monkeypatch)
    _flush()
    before = renders["n"]
    _write(home_state, audit_saves_count=1)
    assert renders["n"] > before, "an Apply writes a save: the count of saves of the panel must follow"
    before = renders["n"]
    _write(home_state, data_batch_hash="c" * 64)
    assert renders["n"] > before, "another data batch is another session key"
