"""The Export button's wait for the server does not end while the server is still working (D-0270, D-0050), in the browser.

D-0270: the button is grey until the server confirms it holds the values; if the confirmation does not come it opens after a
wait with a plain notice. Case: after a recipe switch the server is still working on the switch when the 5 s of the fallback
are over (a long recipe). The confirmation is not lost, it is late. Opening the button then shows the old recipe's fields beside
the new recipe, and a press can mix them. The 5 s therefore count only time in which the server is NOT busy.

PROVISIONAL choice (no decision names it): "busy" is the page's own signal (the class `shiny-busy`, the events `shiny:busy` and
`shiny:idle`). The other option for Eve: a check at download time that the values the download reads are the remembered values of
the session it exports.

The app of this file is `slow_switch_app.py`: the real app, plus an effect that makes the switch to Q take 7 s on the server.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_export_ready_busy_wait.py -v
"""
import re
from pathlib import Path

import pytest
from playwright.sync_api import Page, expect
from shiny.pytest import create_app_fixture

from app.tests.slow_switch_app import SLOW_SECONDS
from app.tests.test_shiny_export_fields_per_session import (
    BTN, _download, _expect_fields, _open_export_panel, _set,
)
from app.tests.test_shiny_export_race import (
    P, P_SET, Q, Q_SET, _LOST, _assert_bundle_is_one_sessions, _ready, _shown,
)
from app.tests.test_shiny_smoke import _choose_recipe, _open_app, _wait_shiny

slow_app = create_app_fixture(str(Path(__file__).parent / "slow_switch_app.py"), scope="module")

# Samples the page every 50 ms from the switch until `ms` have passed: was the button grey, was the document marked busy.
_WATCH = """async ({recipe, ms}) => {
    const sel = document.querySelector('#data_analysis_recipe_id');
    const b = () => document.querySelector('#export_bundle_download');
    const t0 = performance.now();
    sel.value = recipe;
    sel.dispatchEvent(new Event('input', {bubbles: true}));
    sel.dispatchEvent(new Event('change', {bubbles: true}));
    const out = {greyAlways: true, firstOpenMs: null, busyGaps: [], notice: false, samples: 0, coverSamples: 0, shownUnderCover: 0, shownGrey: 0};
    const shown = (e) => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
    let lastBusy = null;
    while (performance.now() - t0 < ms) {
        const t = performance.now() - t0;
        const grey = b().classList.contains('export-not-ready');
        const busy = document.documentElement.classList.contains('shiny-busy');
        if (!grey) { out.greyAlways = false; if (out.firstOpenMs === null) out.firstOpenMs = Math.round(t); }
        if (t > 300 && !busy && grey && out.firstOpenMs === null) out.busyGaps.push(Math.round(t));
        out.samples += 1;
        const cover = !!document.querySelector('#home_opening_cover');
        if (cover) { out.coverSamples += 1; if (shown(b())) out.shownUnderCover += 1; }
        else if (shown(b()) && grey) out.shownGrey += 1;
        await new Promise(r => setTimeout(r, 50));
    }
    out.notice = !!document.querySelector('.shiny-notification') &&
        document.querySelector('#shiny-notification-panel').innerText.includes('may not have been received');
    return out;
}"""


@pytest.fixture(scope="module")
def slow_page(browser, slow_app):
    page = browser.new_page()
    _open_app(page, slow_app.url)
    yield page
    page.close()


@pytest.fixture()
def two_sessions(slow_page: Page):
    """P and Q each set to their own values; the page ends on P with the Export panel open and the button ready."""
    page = slow_page
    _choose_recipe(page, Q)
    _open_export_panel(page)
    _set(page, **Q_SET)
    _choose_recipe(page, P)
    _open_export_panel(page)
    _set(page, **P_SET)
    _expect_fields(page, _shown(P_SET), "P as set")
    downloads: list = []
    handler = lambda d: downloads.append(d)  # noqa: E731
    page.on("download", handler)
    yield page, downloads
    page.remove_listener("download", handler)
    _ready(page, 90_000)


def test_a_switch_the_server_needs_longer_than_the_fallback_keeps_the_button_grey_until_the_server_is_done(two_sessions):
    """The server needs about 7 s for the switch to Q: the button is grey the whole time, no 'may not have been received'
    notice, a press starts nothing; then it opens by the confirmation and the bundle is Q's, with Q's own values."""
    page, downloads = two_sessions
    # a first look 6.5 s after the switch (after the 5 s of the fallback, before the end of the work): sampled in the page
    seen = page.evaluate(_WATCH, {"recipe": Q, "ms": int(SLOW_SECONDS * 1000) - 800})
    assert seen["greyAlways"], f"the button opened while the server was still working: {seen}"
    assert not seen["notice"], f"the fallback notice appeared while the server was still working: {seen}"
    # D-0372: while the recipe is being opened the Export panel body is hidden by the cover, so the button is never visible then
    assert seen["shownUnderCover"] == 0, f"the Export button was visible while the opening cover was on the screen: {seen}"
    cover_on = page.locator("#home_opening_cover").count() > 0
    if cover_on:
        assert not page.locator(BTN).is_visible(), "the Export button is visible under the cover"
    else:
        assert page.locator(BTN).is_visible() and "export-not-ready" in (page.locator(BTN).get_attribute("class") or ""), \
            "after the cover and before the server is done the button must be visible and grey"
        assert page.locator(BTN).inner_text().strip() != "", "the button has no text"
    # a real mouse click on the place of the button (no actionability wait: it hits what is really there): under the cover the hidden panel takes
    # no click, on the grey button the click has no effect; either way no download starts (asserted below)
    box = page.locator(BTN).bounding_box()
    assert box is not None, "the button has no place on the page"
    page.mouse.click(box["x"] + box["width"] / 2, box["y"] + box["height"] / 2)
    press = page.evaluate("""() => { const b = document.querySelector('#export_bundle_download');
        const ev = new MouseEvent('click', {bubbles: true, cancelable: true}); b.dispatchEvent(ev);
        return {prevented: ev.defaultPrevented, grey: b.classList.contains('export-not-ready')}; }""")
    assert press["prevented"] and press["grey"], f"a press during the long switch was not refused: {press}"
    assert downloads == [], "the press during the long switch started a download"
    _ready(page, 90_000)
    expect(page.locator("#home_opening_cover")).to_have_count(0)
    assert page.locator(BTN).is_visible() and page.locator(BTN).inner_text().strip() != "", "after the server is done the button is visible with its text"
    assert page.locator(_LOST).count() == 0, "the button was opened by the fallback, not by the server's confirmation"
    _expect_fields(page, _shown(Q_SET), "Q's own fields after the long switch")
    z = _download(page)
    assert _assert_bundle_is_one_sessions(z, "after the long switch") == Q


def test_the_page_marks_the_document_busy_during_the_whole_work_of_the_switch(two_sessions):
    """The evidence the fix stands on: from the switch to the end of the server's work `shiny-busy` is set."""
    page, _ = two_sessions
    seen = page.evaluate(_WATCH, {"recipe": Q, "ms": int(SLOW_SECONDS * 1000) - 800})
    assert seen["busyGaps"] == [], f"the document was not marked busy at these ms during the server's work: {seen['busyGaps'][:20]}"
    _ready(page, 90_000)
