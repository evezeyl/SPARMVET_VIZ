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

from app.tests.browser_view import set_view
from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_smoke import (_INTERACTIVE_APP_FEATURES, _wait_session_groups_open, _load_data_analysis_recipe, _navigate_to_mlst_plot,
                                        _open_filters_panel, _wait_for_fb_col_option, _choose_fb_op, _wait_shiny)

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
SAVED_REASON = "seeded step of the saved session"


OPEN_RECIPE = "1_test_data_ST22_dummy"   # the recipe the browser opens (`_load_data_analysis_recipe`)
OTHER_RECIPE = "restore_other_recipe"


def _seed(sm, label: str, with_step: bool, recipe_id: str = OPEN_RECIPE):
    """A session of the OPEN recipe (its real recipe key, a data batch of its own so that its key is its own) or, with another
    `recipe_id`, of another recipe (D-0317: its Restore is refused). With or without a saved audit step."""
    import hashlib
    from pathlib import Path
    from app.modules.session_manager import SessionManager, make_audit_step
    from app.src.bootloader import bootloader
    if recipe_id == OPEN_RECIPE:
        msig = SessionManager.compute_data_analysis_recipe_sha256(Path(bootloader.discovered_data_analysis_recipes[OPEN_RECIPE]))
    else:
        msig = hashlib.sha256(recipe_id.encode()).hexdigest()
    if recipe_id == OPEN_RECIPE:
        # G1 guard (2026-11-28): the Restore needs the data the session was made on, so the session carries the REAL data of the open recipe. Two seeded sessions
        # of one recipe and one data would share a key, and the app's own record of the open view is that key too, so the recipe hash is made up per label:
        # the key is its own (the Restore then also shows the recipe-version warning, which these tests do not count).
        from app.tests.real_data_identity import data_identity
        dbh, real_files = data_identity(OPEN_RECIPE)
        msig = hashlib.sha256(f"seed recipe {label}".encode()).hexdigest()
    else:
        dbh, real_files = hashlib.sha256(f"seed batch {label}".encode()).hexdigest(), {}
    key = SessionManager.compute_session_key(msig, dbh)
    sm.write_assembly_ghost(key, recipe_id, msig, dbh, real_files, {}, label=label)
    if with_step:
        step = make_audit_step("filter_row", {"column": "year", "op": "gt", "value": 1900, "dtype": "Int64"},
                               SAVED_REASON, place="T3:mlst_bar")
        sm.write_t3_ghost(key, recipe_id, msig, dbh, audit_steps=[step])
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
    """Open the group of the session panel that holds `button` if the button is not visible (the panel is drawn again after a
    restore and its accordion starts closed). Several groups can carry the same recipe id, so the group is found by its button."""
    item = page.locator("#session_groups_accordion .accordion-item").filter(has=page.locator(button))
    expect(item.first).to_be_visible(timeout=10_000)
    if not page.locator(button).is_visible():
        item.first.locator(".accordion-button").click()
        _wait_shiny(page)
    _wait_session_groups_open(page, label)
    expect(page.locator(button)).to_be_visible(timeout=10_000)


_REASONS_JS = "() => [...document.querySelectorAll('#audit_nodes_tier3 .spv-audit-reason')].map(e => e.textContent.replace(/^Reason: /, ''))"


def _reasons(page: Page) -> list[str]:
    """The reasons of the step cards of the right panel (FLOW-3: a card shows the reason it was added with, as text)."""
    return page.evaluate(_REASONS_JS)


def _wait_reasons(page: Page, step: str, expected: list[str], timeout: int = 15_000) -> None:
    """Wait until the audit panel holds exactly the reasons `expected` (as a set, in any order)."""
    try:
        page.wait_for_function(
            "(want) => { const got = (" + _REASONS_JS[len("() => "):] + ").sort();"
            " return JSON.stringify(got) === JSON.stringify(want.slice().sort()); }", arg=expected, timeout=timeout)
    except Exception as exc:  # noqa: BLE001
        raise AssertionError(f"[{step}] the audit panel holds {_reasons(page)}, expected {expected}") from exc


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_one_click_on_restore_and_on_delete_acts_once(page: Page, shiny_app: ShinyAppProc):
    from app.modules.session_manager import SessionManager
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    key_saved = _seed(sm, "restore_once_saved", with_step=True)
    key_empty = _seed(sm, "restore_once_empty", with_step=False)
    safe = lambda key: key.replace(":", "_")   # noqa: E731
    try:
        _load_data_analysis_recipe(page, shiny_app.url)
        page.evaluate(_RECORD_NOTICES)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        set_view(page, "T3")

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
        # P-B5 (PROVISIONAL): a restored session that holds audit steps opens Audit mode, where the audited plot those steps were made for is shown
        expect(page.locator("#home_mode input[value=audit]")).to_be_checked(timeout=10_000)
        # slice 3a (PROVISIONAL): the band says that the restored steps are applied
        expect(page.locator("#shown_band_ui")).to_contain_text("Restored session: 1 audit step is applied.", timeout=15_000)
        # slice 3b (PROVISIONAL): Audit mode has no plot tabs; the plot area holds the plot of the tab Exploration had (nothing shown yet), where the saved step was made
        expect(page.locator(".spv-audit-plot-area")).to_contain_text("Plot shown: MLST Bar", timeout=15_000)
        expect(page.locator("#home_groups_nav")).to_have_count(0)

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
        _choose_fb_op(page, "gt")
        _wait_shiny(page)
        page.locator("#fb_value").fill("2000")
        page.wait_for_timeout(200)   # the number box is mounted again after the operator changes: a value typed in that moment is lost
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        from app.tests.browser_view import add_to_pipeline, try_staged
        new_reason = "a step added after the restore"
        try_staged(page)
        add_to_pipeline(page, new_reason, expected_places=1)
        _notices(page, "3 Add", "Step added to the audit pipeline", 1)
        _free(page, "3 Add")
        _wait_reasons(page, "3 the new step is in the audit panel after Add", [SAVED_REASON, new_reason])
        page.wait_for_timeout(5_000)   # the time in which a repeated restore would overwrite the step (a repeat came every second or less)
        _wait_reasons(page, "3 the new step is still there 5 s after Add", [SAVED_REASON, new_reason], timeout=3_000)

        # 4. Delete on the other card runs once and the card is gone
        _show_card(page, "restore_once_empty", f"#session_delete_{safe(key_empty)}")
        page.locator(f"#session_delete_{safe(key_empty)}").click()
        page.locator("#session_delete_one_confirm").click()   # D-0378: Delete asks first
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


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_restore_of_a_session_of_another_recipe_is_refused_once_and_applies_nothing(page: Page, shiny_app: ShinyAppProc):
    """D-0317: one click on Restore of a session saved against another recipe shows the refusal line once, no 'Session restored',
    and the audit steps of the view are what they were."""
    from app.modules.session_manager import SessionManager
    from app.src.bootloader import bootloader
    sm = SessionManager(bootloader.get_location("user_data"))
    key_other = _seed(sm, "restore_refused", with_step=True, recipe_id=OTHER_RECIPE)
    button = f"#session_restore_{key_other.replace(':', '_')}"
    try:
        if page.url.startswith("http"):
            page.reload()   # the page is shared by the module: a fresh session draws the list with the session just written
        _load_data_analysis_recipe(page, shiny_app.url)
        page.evaluate(_RECORD_NOTICES)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        set_view(page, "T3")
        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)
        before = _reasons(page)
        restored_before = _seen(page, "Session restored")
        _show_card(page, "restore_refused", button)
        page.locator(button).click()
        _notices(page, "refused restore", f"belongs to another recipe ({OTHER_RECIPE})", 1)
        _free(page, "refused restore")
        assert _seen(page, "Session restored") == restored_before, "a refused session was reported as restored"
        assert _reasons(page) == before, "the audit steps of the view changed although the restore was refused"
        assert SAVED_REASON not in _reasons(page)
        assert "Open that recipe first, then restore the session." in " ".join(
            page.evaluate("() => window.__seenNotices"))
    finally:
        sm.delete_session(key_other)


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES,
                    reason="Session Management panel only present for interactive app features files")
def test_restore_of_a_session_made_on_other_data_is_refused_and_applies_nothing(page: Page, shiny_app: ShinyAppProc, tmp_path):
    """G1 guard (Eve 2026-11-28): a session of the open recipe whose data differ from the data on disk: Restore is refused once, the message names both sets of data,
    no step reaches the view, and the table shown is the table that was shown."""
    import hashlib
    from app.modules.session_manager import SessionManager, make_audit_step
    from app.src.bootloader import bootloader
    from app.tests.real_data_identity import data_identity
    sm = SessionManager(bootloader.get_location("user_data"))
    now_hash, now_files = data_identity(OPEN_RECIPE)
    other = tmp_path / "other_summary.tsv"
    other.write_text("a\tb\n1\t2\n")
    table = next(iter(now_files))
    msig = hashlib.sha256(b"seed recipe restore_other_data").hexdigest()
    old_hash = hashlib.sha256(b"seed batch restore_other_data").hexdigest()
    key = SessionManager.compute_session_key(msig, old_hash)
    sm.write_assembly_ghost(key, OPEN_RECIPE, msig, old_hash, {table: other}, {}, label="restore_other_data")
    sm.write_t3_ghost(key, OPEN_RECIPE, msig, old_hash, audit_steps=[make_audit_step(
        "filter_row", {"column": "year", "op": "gt", "value": 1900, "dtype": "Int64"}, SAVED_REASON, place="T3:mlst_bar")])
    button = f"#session_restore_{key.replace(':', '_')}"
    try:
        if page.url.startswith("http"):
            page.reload()
        _load_data_analysis_recipe(page, shiny_app.url)
        page.evaluate(_RECORD_NOTICES)
        _open_filters_panel(page)
        _navigate_to_mlst_plot(page)
        set_view(page, "T3")
        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        _wait_shiny(page)
        page.wait_for_selector("#session_groups_accordion", timeout=10_000)
        badge_before = page.locator("#home_data_preview_badge").inner_text()
        _show_card(page, "restore_other_data", button)
        page.locator(button).click()
        _notices(page, "refused restore on other data", "was made on other data", 1)
        _free(page, "refused restore on other data")
        text = " ".join(t for t in page.evaluate("() => window.__seenNotices") if "other data" in t)
        assert old_hash[:8] in text and now_hash[:8] in text and "other_summary.tsv" in text, text
        assert _seen(page, "Session restored") == 0, "a refused session was reported as restored"
        assert _reasons(page) == [] and SAVED_REASON not in _reasons(page), "a step of the other data reached the view"
        assert page.locator("#home_data_preview_badge").inner_text() == badge_before, "the table shown changed"
    finally:
        sm.delete_session(key)
