"""One click on a session card acts once, in a real browser (RESTORE-LOOP-1; D-0050 "No silent error that is the rule.").

Before the fix a click on Restore never ended: the page stayed busy, "Session restored" was shown again and again (a reviewer
counted 36 restores in 25 seconds for a session with a saved audit step, over a thousand for one with no save) and a Delete on
another card did not run. The effect `_handle_session_actions` acted whenever a click count was above zero and its notices wrote
the notification log it depended on. A restore that repeats also puts the saved steps back over the steps the user added after it.

The test seeds two sessions in the user data folder of the test app (one with a saved audit step on the plot `mlst_bar`, one
without any save), then drives the panel: Restore on each (the page becomes free, exactly one notice per click, the saved step is in
the audit panel), a new step is added and applied and is still there seconds later (a repeat would overwrite it), Delete on the
other card (gone, once).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_session_restore.py -q
"""
import os
import time

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_smoke import (_INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _navigate_to_mlst_plot,
                                        _open_filters_panel, _wait_for_fb_col_option, _wait_shiny)

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
SAVED_REASON = "seeded step of the saved session"


def _seed(sm, tmp_path, label: str, with_step: bool):
    """A session of its own recipe and data (its key differs from the open recipe's) with or without a saved audit step."""
    from app.modules.session_manager import SessionManager, make_audit_step
    recipe = tmp_path / f"{label}.yaml"
    recipe.write_text(
        f"id: {label}\n"
        "analysis_groups:\n  g:\n    label: G\n    plots:\n      p:\n        label: P\n"
        "        spec:\n          target_dataset: C\n          mapping: {x: a}\n"
        "          layers:\n            - name: geom_bar\n")
    data = tmp_path / f"{label}.tsv"
    data.write_text(f"a\tb\n1\t{label}\n")
    msig = SessionManager.compute_data_analysis_recipe_sha256(recipe)
    dbh = SessionManager.compute_data_batch_hash({"d": data})
    key = SessionManager.compute_session_key(msig, dbh)
    sm.write_assembly_ghost(key, label, msig, dbh, {"d": str(data)}, {})
    if with_step:
        step = make_audit_step("filter_row", {"column": "year", "op": "gt", "value": 1900, "dtype": "Int64"},
                               "subtab_mlst_bar", SAVED_REASON)
        sm.write_t3_ghost(key, label, msig, dbh, "T2", t3_audit_steps_by_plot={"subtab_mlst_bar": [step]})
    return key


def _toasts(page: Page, word: str) -> int:
    return page.evaluate("(w) => [...document.querySelectorAll('.shiny-notification')].filter(n => n.textContent.includes(w)).length", word)


def _free(page: Page, what: str, seconds: int = 15) -> None:
    """The busy flag clears within `seconds`: a loop keeps the page busy for ever."""
    try:
        page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=seconds * 1000)
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"the page stayed busy for {seconds} s after {what}: the click is repeated without end") from exc


def _show_card(page: Page, label: str, button: str) -> None:
    """Open the session group of `label` if its button is not visible: the panel is drawn again after a restore (it reads the
    state the restore sets), and its accordion starts closed."""
    if not page.locator(button).is_visible():
        page.locator("#session_groups_accordion").get_by_text(f"📁 {label}", exact=False).first.click()
        _wait_shiny(page)
    expect(page.locator(button)).to_be_visible(timeout=10_000)


def _reasons(page: Page) -> list[str]:
    return page.evaluate("() => [...document.querySelectorAll('input[id^=t3_reason_]')].map(e => e.value)")


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_one_click_on_restore_and_on_delete_acts_once(page: Page, shiny_app: ShinyAppProc, tmp_path):
    from app.modules.session_manager import SessionManager
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    key_saved = _seed(sm, tmp_path, "restore_once_saved", with_step=True)
    key_empty = _seed(sm, tmp_path, "restore_once_empty", with_step=False)
    safe = lambda key: key.replace(":", "_")   # noqa: E731
    try:
        _load_data_analysis_recipe(page, shiny_app.url)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        page.locator("#tier_toggle input[value=T3]").check(force=True)
        _wait_shiny(page)

        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)
        for label in ("restore_once_saved", "restore_once_empty"):
            page.locator("#session_groups_accordion").get_by_text(f"📁 {label}", exact=False).first.click()
            _wait_shiny(page)

        # Restore the session that has a saved audit step
        expect(page.locator(f"#session_restore_{safe(key_saved)}")).to_be_visible(timeout=10_000)
        page.locator(f"#session_restore_{safe(key_saved)}").click()
        _free(page, "Restore of the session with a saved step")
        assert _toasts(page, "Session restored") == 1, f"{_toasts(page, 'Session restored')} notices after one click"
        page.wait_for_timeout(3_000)
        assert _toasts(page, "Session restored") <= 1, "the restore is repeated after the page was free"
        expect(page.locator('input[id^="t3_reason_"]').first).to_be_visible(timeout=10_000)
        assert SAVED_REASON in _reasons(page), f"the saved step is not in the audit panel: {_reasons(page)}"

        # Restore the session that has no save: nothing to restore, one notice, the page is free
        _show_card(page, "restore_once_empty", f"#session_restore_{safe(key_empty)}")
        page.locator(f"#session_restore_{safe(key_empty)}").click()
        _free(page, "Restore of the session with no save")
        assert _toasts(page, "no saved audit steps") == 1, "one notice for one click on the session with no save"
        page.wait_for_timeout(3_000)
        assert _toasts(page, "no saved audit steps") <= 1
        assert SAVED_REASON in _reasons(page), "the steps of the view are unchanged by a restore that has nothing to restore"

        # A step added after the restore must still be there seconds later: a repeated restore would put the saved steps back
        _wait_for_fb_col_option(page, "year")
        page.locator("#fb_col").select_option("year")
        _wait_shiny(page)
        page.locator("#fb_op").select_option("gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2000")
        page.wait_for_timeout(200)
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        page.locator("#filter_send_to_audit").click()
        _wait_shiny(page)
        page.locator("#propagation_confirm").click()
        _wait_shiny(page)
        new_reason = "a step added after the restore"
        deadline = time.time() + 20
        apply = page.locator("#btn_apply").first
        while True:
            boxes = page.locator('input[id^="t3_reason_"]')
            for i in range(boxes.count()):
                if not boxes.nth(i).input_value():
                    boxes.nth(i).fill(new_reason)
                    boxes.nth(i).press("Tab")
            _wait_shiny(page)
            if apply.is_enabled():
                break
            assert time.time() < deadline, "Apply was never enabled"
            page.wait_for_timeout(250)
        page.eval_on_selector("#btn_apply", "e => e.click()")
        page.wait_for_function("() => document.body.textContent.includes('audit steps applied')", timeout=20_000)
        _free(page, "Apply")
        page.wait_for_timeout(5_000)
        reasons = _reasons(page)
        assert SAVED_REASON in reasons and new_reason in reasons, f"the step added after the restore is gone: {reasons}"

        # Delete on the other card runs once and the card is gone
        before = _toasts(page, "Session deleted")
        _show_card(page, "restore_once_empty", f"#session_delete_{safe(key_empty)}")
        page.locator(f"#session_delete_{safe(key_empty)}").click()
        _free(page, "Delete")
        expect(page.locator(f"#session_delete_{safe(key_empty)}")).to_have_count(0, timeout=8_000)
        page.wait_for_timeout(3_000)
        assert _toasts(page, "Session deleted") - before == 1, "the delete notice was not shown exactly once"
        assert not (sm.root / key_empty).exists()
        assert (sm.root / key_saved).exists(), "the other session was not touched"

        # A second click on the same Restore is a second restore (the card was drawn again after the first: its count starts over)
        before = _toasts(page, "Session restored")
        _show_card(page, "restore_once_saved", f"#session_restore_{safe(key_saved)}")
        page.locator(f"#session_restore_{safe(key_saved)}").click()
        _free(page, "a second Restore of the same session")
        assert _toasts(page, "Session restored") - before == 1, "a second click gave no restore, or more than one"
        page.wait_for_timeout(3_000)
        assert _toasts(page, "Session restored") - before == 1
        assert _reasons(page) == [SAVED_REASON], "the second restore puts back the saved steps (and only them)"
    finally:
        for key in (key_saved, key_empty):
            sm.delete_session(key)
