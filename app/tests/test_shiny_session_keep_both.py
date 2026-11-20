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
import time

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_session_restore import (_RECORD_NOTICES, _free, _notices, _seed, _show_card)
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _wait_shiny

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")


def _wait_for_copies(sm, before: set, timeout_s: float = 15.0) -> list:
    """The sessions stored since `before`, once there is at least one: the server writes the copy after the click arrives, and the
    page can be idle (`_wait_shiny`) before it did, so the store is polled until the copy is there (or the time is up)."""
    deadline = time.monotonic() + timeout_s
    while True:
        copies = sorted({s["session_key"] for s in sm.list_all_sessions()} - before)
        if copies or time.monotonic() >= deadline:
            return copies
        time.sleep(0.1)


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_keep_both_leaves_a_working_panel_and_the_copy_can_be_restored_and_deleted(page: Page, shiny_app: ShinyAppProc, tmp_path):
    from app.modules.session_manager import SessionManager, session_input_id_part
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    key = _seed(sm, "keep_both_panel", with_step=True)
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
        copies = _wait_for_copies(sm, before)
        assert len(copies) == 1, f"Keep both stored {copies} 15 s after the click (expected one new session)"
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


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_deleting_one_of_two_folders_that_look_alike_leaves_the_other(page: Page, shiny_app: ShinyAppProc):
    """Two folders whose names differ only in `:` and `_` used to share one Delete button: one click deleted both."""
    from app.modules.session_manager import SessionManager, session_input_id_parts
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    first, second = "cafe00000001:beef00000001", "cafe00000001_beef00000001"
    for key in (first, second):
        sm.write_assembly_ghost(key, "collide_pair", "c" * 64, "d" * 64, {}, {})
    parts = session_input_id_parts([first, second])
    try:
        if page.url.startswith("http"):
            page.reload()   # the page is shared by the module: a fresh session draws the list with the two folders just written
        _load_data_analysis_recipe(page, shiny_app.url)
        page.evaluate(_RECORD_NOTICES)
        if not page.locator("#session_groups_accordion").count():
            page.locator("#nav_accordion").get_by_text("Session Management").first.click()
            _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", state="attached", timeout=10_000)
        assert parts[first] != parts[second]
        _show_card(page, "collide_pair", f"#session_delete_{parts[first]}")
        expect(page.locator(f"#session_delete_{parts[second]}")).to_be_visible()
        assert "cannot tell apart" in page.locator("#session_management_ui").inner_text()
        page.locator(f"#session_delete_{parts[first]}").click()
        _notices(page, "delete of one of two look-alike folders", "Session deleted", 1)
        # the panel is drawn again with its groups closed: the deleted card is gone, the group is still listed
        expect(page.locator(f"#session_delete_{parts[first]}")).to_have_count(0, timeout=10_000)
        expect(page.locator("#session_groups_accordion").get_by_text("collide_pair")).to_have_count(1, timeout=10_000)
        assert not (sm.root / first).exists()
        assert (sm.root / second).exists(), "the other folder was deleted by the same click"
    finally:
        for key in (first, second):
            sm.delete_session(key)
