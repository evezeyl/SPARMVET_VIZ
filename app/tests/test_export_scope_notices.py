"""The two notices of `_sync_export_scope_choices`: the scope is named by the label the user sees, and an error is told in
the plain form (D-0050, D-0101). The effect is run headless: `reactive.Effect` records the function, `reactive.isolate` and the
notification are plain.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_export_scope_notices.py -q
"""
from types import SimpleNamespace

from shiny import reactive, render, ui

from app.handlers import export_handlers
from app.handlers.export_handlers import SCOPE_LABELS

GROUPS = {"qc": {"plots": {"p1": {}}}}


def _effect(monkeypatch, cfg, subtab, chosen, notes):
    found = {}
    monkeypatch.setattr(reactive, "Effect", lambda fn: found.setdefault(fn.__name__, fn) and fn)
    monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(ui, "notification_show", lambda m, **kw: notes.append((kw.get("type"), str(m))))
    updates = []
    monkeypatch.setattr(ui, "update_radio_buttons", lambda *a, **k: updates.append(k))
    boot = SimpleNamespace(is_enabled=lambda f: True)
    export_handlers.define_export_server(
        SimpleNamespace(import_bundle_upload=None), lambda fn: fn, None, bootloader=boot, orchestrator=None,
        viz_factory=None, current_app_features=None, active_cfg=cfg, tier1_anchor=None, tier_toggle=None,
        home_state=None, safe_input=lambda _i, key, default: chosen, active_home_subtab=SimpleNamespace(get=lambda: subtab),
        view_keys=lambda: None)
    return found["_sync_export_scope_choices"], updates


def test_the_scope_that_goes_away_is_named_by_its_label(monkeypatch):
    notes = []
    cfg = lambda: SimpleNamespace(raw_config={"analysis_groups": GROUPS})
    effect, updates = _effect(monkeypatch, cfg, "subtab_unknown", "group", notes)
    effect()
    assert updates[0]["selected"] == "global"
    assert len(notes) == 1 and f"'{SCOPE_LABELS['group']}'" in notes[0][1] and "'group'" not in notes[0][1], notes


def test_a_scope_that_stays_gives_no_notice(monkeypatch):
    notes = []
    cfg = lambda: SimpleNamespace(raw_config={"analysis_groups": GROUPS})
    effect, updates = _effect(monkeypatch, cfg, "subtab_p1", "group", notes)
    effect()
    assert updates[0]["selected"] == "group" and notes == []


def test_an_error_of_the_recipe_is_told_in_the_plain_form(monkeypatch):
    notes = []

    def broken():
        raise ValueError("no recipe")
    effect, updates = _effect(monkeypatch, broken, "subtab_p1", "global", notes)
    effect()
    assert updates == [] and len(notes) == 1
    text = notes[0][1]
    assert text.startswith("The Scope choices of the Export panel could not be brought up to date; they stay as they were")
    assert "(ValueError: no recipe)" in text and "check the recipe" not in text
