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


# A notice stays on the screen for a few seconds and then goes, so a read of "how many are on the screen now" depends on when it is
# made: too early it finds none (the notice has not arrived), too late it finds none (it has gone). The page therefore keeps a
# record of every notice that was ever added (a MutationObserver installed before the first click), and the test counts that record:
# it waits until the expected number is there, then waits a short time and checks that no further one came.
_RECORD_NOTICES = """() => {
  if (window.__seenNotices) return;
  window.__seenNotices = [];
  const note = (node) => {
    if (node.nodeType === 1 && node.classList && node.classList.contains('shiny-notification')) {
      setTimeout(() => window.__seenNotices.push(node.textContent), 0);   // the text is filled in after the node is added
    }
  };
  new MutationObserver((records) => records.forEach(r => r.addedNodes.forEach(note)))
    .observe(document.body, {childList: true, subtree: true});
}"""

_SETTLE_MS = 2_000   # a pause that cannot be a wait for a state: it is the time in which a repeated click would show itself (the old
                     # defect added a notice every second or less); the check that follows can fail on it


def _seen(page: Page, word: str) -> int:
    return page.evaluate("(w) => (window.__seenNotices || []).filter(t => t.includes(w)).length", word)


def _notices(page: Page, step: str, word: str, expected: int, already: int = 0, context: str = "") -> None:
    """Wait until `expected` notices with `word` came (counted from `already`), then check that no further one comes."""
    try:
        page.wait_for_function("([w, n]) => (window.__seenNotices || []).filter(t => t.includes(w)).length >= n",
                               arg=[word, already + expected], timeout=20_000)
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"[{step}] no '{word}' notice reached the screen within 20 s (seen: {_seen(page, word)}, "
                             f"expected {already + expected}){context}") from exc
    page.wait_for_timeout(_SETTLE_MS)
    got = _seen(page, word) - already
    assert got == expected, f"[{step}] {got} '{word}' notices came after the click, expected {expected}: the click is repeated"


def _free(page: Page, step: str, seconds: int = 20) -> None:
    """The busy flag is clear (a loop keeps the page busy for ever). Called after the notice came, so that a flag that is not yet
    set (the click has not reached the server) is not taken for a free page."""
    try:
        page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=seconds * 1000)
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"[{step}] the page stayed busy for {seconds} s: the click is repeated without end") from exc


def _show_card(page: Page, label: str, button: str) -> None:
    """Open the session group of `label` if its button is not visible: the panel is drawn again after a restore (it reads the
    state the restore sets), and its accordion starts closed."""
    group = page.locator("#session_groups_accordion").get_by_text(f"📁 {label}", exact=False).first
    expect(group).to_be_visible(timeout=10_000)
    if not page.locator(button).is_visible():
        group.click()
        _wait_shiny(page)
    expect(page.locator(button)).to_be_visible(timeout=10_000)


def _reasons(page: Page) -> list[str]:
    return page.evaluate("() => [...document.querySelectorAll('input[id^=t3_reason_]')].map(e => e.value)")


def _wait_reasons(page: Page, step: str, expected: list[str], timeout: int = 15_000) -> None:
    """Wait until the audit panel holds exactly the reasons `expected` (as a set, in any order)."""
    try:
        page.wait_for_function(
            "(want) => { const got = [...document.querySelectorAll('input[id^=t3_reason_]')].map(e => e.value).sort();"
            " return JSON.stringify(got) === JSON.stringify(want.slice().sort()); }", arg=expected, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"[{step}] the audit panel holds {_reasons(page)}, expected {expected}") from exc


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
        page.evaluate(_RECORD_NOTICES)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        page.locator("#tier_toggle input[value=T3]").check(force=True)
        _wait_shiny(page)

        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)
        for label in ("restore_once_saved", "restore_once_empty"):
            _show_card(page, label, f"#session_restore_{safe(key_saved if label.endswith('saved') else key_empty)}")

        # 1. Restore the session that has a saved audit step: one notice, the page becomes free, the saved step is in the view
        saved_button = f"#session_restore_{safe(key_saved)}"
        _show_card(page, "restore_once_saved", saved_button)
        page.locator(saved_button).click()
        _notices(page, "1 restore of the session with a saved step", "Session restored", 1)
        _free(page, "1 restore of the session with a saved step")
        _wait_reasons(page, "1 the saved step is in the audit panel", [SAVED_REASON])

        # 2. Restore the session that has no save: one notice, nothing restored, the steps of the view are unchanged
        _show_card(page, "restore_once_empty", f"#session_restore_{safe(key_empty)}")
        page.locator(f"#session_restore_{safe(key_empty)}").click()
        _notices(page, "2 restore of the session with no save", "no saved audit steps", 1)
        _free(page, "2 restore of the session with no save")
        _wait_reasons(page, "2 the steps of the view are unchanged by a restore with nothing to restore", [SAVED_REASON])

        # 3. A step added after the restore must still be there seconds later: a repeated restore would put the saved steps back
        _wait_for_fb_col_option(page, "year")
        page.locator("#fb_col").select_option("year")
        _wait_shiny(page)
        page.locator("#fb_op").select_option("gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2000")
        page.wait_for_timeout(200)   # the number box is mounted again after the operator changes: a value typed in that moment is lost
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
        page.locator("#filter_send_to_audit").click()
        expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
        page.locator("#propagation_confirm").click()
        _wait_shiny(page)
        new_reason = "a step added after the restore"
        apply = page.locator("#btn_apply").first
        # Wait for each state in turn, never for the first sign of it: the audit panel and the Apply button are drawn one after the
        # other, so "Apply is enabled" can still be the state from before the new step arrived (a click then found the step
        # without its reason, or no step at all: seen in repeated runs). (a) the new step is in the panel (two reason boxes),
        # (b) the server has closed the gate for it (the button says "Apply" with the stop sign and is disabled), (c) the reason is
        # typed and read (the button says "Apply" and is enabled).
        try:
            expect(page.locator('input[id^="t3_reason_"]')).to_have_count(2, timeout=15_000)
        except AssertionError as exc:
            raise AssertionError(f"[3 add a step] the new step never reached the audit panel: {_reasons(page)}") from exc
        expect(apply).to_have_text("Apply \u26d4", timeout=15_000)
        expect(apply).to_be_disabled()
        empty = page.locator('input[id^="t3_reason_"]').evaluate_all("(boxes) => boxes.findIndex(b => !b.value)")
        assert empty >= 0, f"[3 add a step] no reason box is empty although the gate is closed: {_reasons(page)}"
        box = page.locator('input[id^="t3_reason_"]').nth(empty)
        box.fill(new_reason)
        box.press("Tab")   # leaving the box sends the text; a click sent before it would be refused by the Apply gate
        expect(apply).to_have_text("Apply", timeout=15_000)
        expect(apply).to_be_enabled()
        # the state at the click, kept for the message of a failure: what the button said and what every reason box held
        at_click = f"; at the click the button said {apply.inner_text()!r} and the reason boxes held {_reasons(page)}"
        page.eval_on_selector("#btn_apply", "e => e.click()")
        _notices(page, "3 Apply", "audit steps applied", 1, context=at_click)
        _free(page, "3 Apply")
        _wait_reasons(page, "3 the new step is in the audit panel after Apply", [SAVED_REASON, new_reason])
        page.wait_for_timeout(5_000)   # the time in which a repeated restore would overwrite the step (a repeat came every second or less)
        _wait_reasons(page, "3 the new step is still there 5 s after Apply", [SAVED_REASON, new_reason], timeout=3_000)

        # 4. Delete on the other card runs once and the card is gone
        _show_card(page, "restore_once_empty", f"#session_delete_{safe(key_empty)}")
        page.locator(f"#session_delete_{safe(key_empty)}").click()
        _notices(page, "4 delete of the other card", "Session deleted", 1)
        _free(page, "4 delete of the other card")
        expect(page.locator(f"#session_delete_{safe(key_empty)}")).to_have_count(0, timeout=10_000)
        assert not (sm.root / key_empty).exists(), "[4 delete of the other card] the folder of the deleted session is still there"
        assert (sm.root / key_saved).exists(), "[4 delete of the other card] the other session was touched"

        # 5. A second click on the same Restore is a second restore (the card was drawn again after the first: its count starts over)
        before = _seen(page, "Session restored")
        _show_card(page, "restore_once_saved", saved_button)
        page.locator(saved_button).click()
        _notices(page, "5 second restore of the same session", "Session restored", 1, already=before)
        _free(page, "5 second restore of the same session")
        _wait_reasons(page, "5 the second restore puts back the saved steps (and only them)", [SAVED_REASON])
    finally:
        for key in (key_saved, key_empty):
            sm.delete_session(key)
