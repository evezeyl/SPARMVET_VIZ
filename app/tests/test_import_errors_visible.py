"""An import that cannot check a leg because of an ERROR says so, not "no original recipe found" (VERIF-FIX-2, place 10;
D-0050 "No silent error that is the rule.").

`import_bundle` hashed the original recipe of the same id with `except (Exception, SystemExit): ... = None`. A recipe that exists
on this machine but cannot be read gave the leg "not checked: no original recipe with this id was found locally", which is
false. The leg is still "not checked" (the import still goes on, it never blocks, ADR-097 point 7), its text now names the real
reason, and the import result carries a problem text that the handler shows next to the other import messages.

Mutation index (grep "MUTATION"; each seen failing):
  MUTATION I1  the hash error is swallowed again (no reason in the leg, no problem in the result)
  MUTATION I2  the handler does not show the problem texts of the result

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_import_errors_visible.py -q
"""
from pathlib import Path
from types import SimpleNamespace

import pytest
from shiny import reactive, render, ui

from app.handlers import export_handlers
from app.modules.bundle_importer import import_bundle
from app.tests.test_bundle_importer import _build_bundle, _fresh_bootloader, _fresh_cache  # noqa: F401  (autouse fixture)


def _local_original(tmp_path, text):
    path = tmp_path / "local" / "tiny.yaml"
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(text)
    return path


def test_a_local_recipe_that_cannot_be_read_is_not_reported_as_not_found(tmp_path):
    """MUTATION I1 fails here."""
    zb, _run, _orig = _build_bundle(tmp_path)
    bad = _local_original(tmp_path, "id: tiny\n  this: [is not: yaml")
    bl = _fresh_bootloader(tmp_path, available={"tiny": bad})
    result = import_bundle(zb, bootloader=bl)
    leg = result.legs["recipe"]
    assert leg.status == "not_checked", "the leg is still not checked: the import never blocks"
    assert "no original recipe with this id was found" not in leg.detail, leg.detail
    assert "could not be read" in leg.detail and str(bad) in leg.detail and ". Suggestion:" in leg.detail, leg.detail
    assert len(result.problems) == 1 and ". Suggestion:" in result.problems[0], result.problems
    assert result.session_key and result.imported_recipe_path.exists(), "the import itself still happened"


def test_a_recipe_that_ends_the_process_is_also_told(tmp_path, monkeypatch):
    """`ConfigManager` may call `sys.exit` on a contradictory recipe (ADR-077): the import survives and says so."""
    from app.modules import bundle_importer
    zb, _run, orig = _build_bundle(tmp_path)
    bl = _fresh_bootloader(tmp_path, available={"tiny": orig})
    real = bundle_importer.SessionManager.compute_data_analysis_recipe_sha256

    def exits_for_the_local_original(path):
        if Path(path) == orig:
            raise SystemExit(1)
        return real(path)

    monkeypatch.setattr(bundle_importer.SessionManager, "compute_data_analysis_recipe_sha256", staticmethod(exits_for_the_local_original))
    result = import_bundle(zb, bootloader=bl)
    assert result.legs["recipe"].status == "not_checked" and len(result.problems) == 1, result.problems
    assert "SystemExit" in result.problems[0] or "exit" in result.problems[0].lower()


def test_no_local_recipe_keeps_the_old_text_and_no_problem(tmp_path):
    """The control: a recipe that is simply not on this machine is not an error."""
    zb, _run, _orig = _build_bundle(tmp_path)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path))
    assert result.legs["recipe"].status == "not_checked"
    assert "no original recipe with this id was found" in result.legs["recipe"].detail
    assert result.problems == []


def test_a_readable_local_recipe_still_gives_a_checked_leg_and_no_problem(tmp_path):
    """The control."""
    zb, _run, orig = _build_bundle(tmp_path)
    result = import_bundle(zb, bootloader=_fresh_bootloader(tmp_path, available={"tiny": orig}))
    assert result.legs["recipe"].status == "match" and result.problems == []


def test_the_handler_shows_the_problem_texts_of_the_import(tmp_path, monkeypatch):
    """MUTATION I2 fails here. Before: the notice read 'All checked legs match.' whatever happened to the recipe leg."""
    zb, _run, _orig = _build_bundle(tmp_path)
    bad = _local_original(tmp_path, "id: tiny\n  this: [is not: yaml")
    bl = _fresh_bootloader(tmp_path, available={"tiny": bad})
    upload = tmp_path / "bundle.zip"
    upload.write_bytes(zb)
    notes, functions = [], {}
    monkeypatch.setattr(reactive, "Effect", lambda fn: functions.setdefault(fn.__name__, fn))
    monkeypatch.setattr(reactive, "event", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(render, "ui", lambda fn=None, **k: fn if fn else (lambda f: f))
    monkeypatch.setattr(render, "download", lambda *a, **k: (lambda fn: fn))
    monkeypatch.setattr(ui, "notification_show", lambda message, **kw: notes.append((kw.get("type"), str(message))))
    export_handlers.define_export_server(
        SimpleNamespace(import_bundle_upload=lambda: [{"datapath": str(upload)}]), lambda fn: fn, None,
        bootloader=bl, orchestrator=None, viz_factory=None, current_app_features=None, active_cfg=None,
        tier1_anchor=None, tier_toggle=None, home_state=None, safe_input=lambda i, k, d: d)
    with reactive.isolate():
        functions["_handle_import_bundle_upload"]()
    warnings = [m for t, m in notes if t == "warning"]
    assert any("could not be read" in m and ". Suggestion:" in m for m in warnings), notes
