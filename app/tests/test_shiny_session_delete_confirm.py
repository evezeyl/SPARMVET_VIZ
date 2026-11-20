"""Delete Session asks before it deletes, in a real browser (D-0378).

# @deps
# consumes: app/handlers/session_handlers.py (_ask_delete_one, _handle_delete_one_confirmed), app/tests/test_shiny_session_restore.py
# @end_deps

The test seeds a session in the user data folder of the test app (`tmpAI/browser_state/<worker>/user`, never a real one). Delete then
Cancel: the question shows the session's label, the folder stays on disk and the card stays in the list. Delete then "Delete": the
folder and the card are gone.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_session_delete_confirm.py -q
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_session_restore import _load_data_analysis_recipe, _seed, _show_card
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _wait_shiny

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
LABEL = "delete_confirm_card"


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="Session Management panel only present for interactive app features files")
def test_delete_cancel_keeps_the_session_and_confirm_removes_it(page: Page, shiny_app: ShinyAppProc):
    from app.modules.session_manager import SessionManager, session_input_id_part
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    key = _seed(sm, LABEL, with_step=False)
    other = _seed(sm, LABEL + "_other", with_step=False)
    safe = session_input_id_part(key)
    try:
        _load_data_analysis_recipe(page, shiny_app.url)
        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)
        _show_card(page, LABEL, f"#session_delete_{safe}")

        # Delete, then Cancel: nothing is deleted, the question names the session
        page.locator(f"#session_delete_{safe}").click()
        modal = page.locator(".modal-dialog")
        expect(modal).to_contain_text("Delete this session? It cannot be undone.", timeout=10_000)
        expect(modal).to_contain_text(LABEL)
        modal.get_by_role("button", name="Cancel").click()
        expect(page.locator(".modal-dialog")).to_have_count(0, timeout=10_000)
        _wait_shiny(page)
        assert (sm.root / key).exists(), "Cancel deleted the session folder"
        _show_card(page, LABEL, f"#session_delete_{safe}")
        expect(page.locator(f"#session_delete_{safe}")).to_have_count(1)

        # Delete, then Delete: the folder and the card are gone; the other session is untouched
        page.locator(f"#session_delete_{safe}").click()
        expect(page.locator(".modal-dialog")).to_contain_text("Delete this session?", timeout=10_000)
        page.locator("#session_delete_one_confirm").click()
        expect(page.locator(f"#session_delete_{safe}")).to_have_count(0, timeout=10_000)
        assert not (sm.root / key).exists(), "the confirmed delete left the folder"
        assert (sm.root / other).exists(), "the other session was touched"
    finally:
        for k in (key, other):
            sm.delete_session(k)
