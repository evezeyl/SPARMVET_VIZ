"""After "Keep both" the Session Management panel still works in a real browser (D-0281, D-0050 "No silent error: that is the rule").

Before the fix the copy was stored as `<key>~imported-<time>`, Shiny refused that text as an id and the whole panel showed one error
(no Restore, Delete or Import) and stayed broken after a reload. The test seeds a session, imports its own export (the key exists),
chooses Keep both, checks that the panel still shows Restore, Delete and Import for both sessions, then restores the copy and deletes it.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_session_keep_both.py -q

# @deps
# provides: test:shiny_session_keep_both
# consumes: app/handlers/session_handlers.py, app/modules/session_manager.py, app/tests/test_shiny_session_restore.py
# consumed_by: CI
# doc: .claude/rules/ui_implementation_contract.md#12d
# @end_deps
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_session_restore import (_RECORD_NOTICES, _free, _notices, _seed, _show_card)
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _wait_shiny

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_keep_both_leaves_a_working_panel_and_the_copy_can_be_restored_and_deleted(page: Page, shiny_app: ShinyAppProc, tmp_path):
    from app.modules.session_manager import SessionManager, session_input_id_part
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    key = _seed(sm, tmp_path, "keep_both_panel", with_step=True)
    zip_path = tmp_path / "own_export.zip"
    zip_path.write_bytes(sm.export_session_zip(key))
    copy_key = None
    try:
        _load_data_analysis_recipe(page, shiny_app.url)
        page.evaluate(_RECORD_NOTICES)
        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)

        page.set_input_files("#session_import_upload", str(zip_path))
        expect(page.locator("#session_import_keep")).to_be_visible(timeout=15_000)
        before = {s["session_key"] for s in sm.list_all_sessions()}
        page.locator("#session_import_keep").click()
        _wait_shiny(page)
        copies = [k for k in {s["session_key"] for s in sm.list_all_sessions()} - before]
        assert len(copies) == 1, f"Keep both stored {copies}"
        copy_key = copies[0]

        # the panel still works: both sessions have Restore and Delete, the Import control is there, and no id error is shown
        _show_card(page, "keep_both_panel", f"#session_restore_{session_input_id_part(key)}")
        _show_card(page, "keep_both_panel", f"#session_restore_{session_input_id_part(copy_key)}")
        expect(page.locator(f"#session_delete_{session_input_id_part(key)}")).to_be_visible()
        expect(page.locator(f"#session_delete_{session_input_id_part(copy_key)}")).to_be_visible()
        expect(page.locator("#session_import_upload")).to_have_count(1)
        assert "not a valid id" not in page.locator("#session_groups_accordion").inner_text()
        page.reload()   # it stayed broken after a reload before the fix
        _load_data_analysis_recipe(page, shiny_app.url)
        page.evaluate(_RECORD_NOTICES)
        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        _show_card(page, "keep_both_panel", f"#session_restore_{session_input_id_part(copy_key)}")

        page.locator(f"#session_restore_{session_input_id_part(copy_key)}").click()
        _notices(page, "restore of the copy", "Session restored", 1)
        _free(page, "restore of the copy")

        _show_card(page, "keep_both_panel", f"#session_delete_{session_input_id_part(copy_key)}")
        page.locator(f"#session_delete_{session_input_id_part(copy_key)}").click()
        _notices(page, "delete of the copy", "Session deleted", 1)
        expect(page.locator(f"#session_delete_{session_input_id_part(copy_key)}")).to_have_count(0, timeout=10_000)
        assert not (sm.root / copy_key).exists()
        assert (sm.root / key).exists(), "the first session was touched"
    finally:
        for k in (key, copy_key):
            if k:
                sm.delete_session(k)
