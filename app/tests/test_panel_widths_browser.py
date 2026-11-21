"""The side panels of the app frame in the browser: widths by window width, the right panel and the mode, the drag (D-0375, D-0381 to D-0386).

# @deps
# consumes: app/modules/frame_widths.py, app/src/www/panel_widths.js, app/src/ui.py, app/handlers/home_theater.py (_drive_right_panel, right_sidebar_content_ui)
# consumes: app/tests/browser_view.py, app/tests/test_shiny_smoke.py (helpers)
# @end_deps

Measured with bounding boxes (the panels are `#nav_sidebar` and `#audit_sidebar`, the centre is `.central-theater`). qa app features (every flag on,
ghost save off). NOT covered: other browsers than Chromium, touch screens, a window under 1000 px wide, bslib versions other than the installed one
(the drag uses its private variable and its DOM event: these tests are the guard of an upgrade).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_panel_widths_browser.py -q
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.modules import frame_widths as fw
from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.browser_view import set_mode, wait_shiny
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _choose_fb_op, _load_data_analysis_recipe, _navigate_to_mlst_plot, _open_filters_panel

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")
pytestmark = pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="needs the audit panel")

KEY = "spv.panel_widths.v1"
WINDOWS = (1100, 1366, 1600, 1920)
LEFT_HANDLE = ".bslib-sidebar-layout:has(> #nav_sidebar) > .bslib-sidebar-resize-handle"
RIGHT_HANDLE = ".bslib-sidebar-layout:has(> #audit_sidebar) > .bslib-sidebar-resize-handle"
RIGHT_TOGGLE = ".bslib-sidebar-layout:has(> #audit_sidebar) > .collapse-toggle"

WIDTHS = """() => { const w = id => { const e = document.getElementById(id); return e ? e.getBoundingClientRect().width : 0; };
  const c = document.querySelector('.central-theater'); return {W: window.innerWidth, left: w('nav_sidebar'), right: w('audit_sidebar'),
  main: c ? c.getBoundingClientRect().width : 0}; }"""

# elements of a panel that stick out of it (the hidden file inputs of Shiny are parked far outside on purpose)
OVERFLOW = """(sel) => { const root = document.querySelector(sel); const rb = root.getBoundingClientRect(); const out = [];
  root.querySelectorAll('*').forEach(e => { if (e.classList.contains('shiny-input-file') || !e.getClientRects().length) return;
    const b = e.getBoundingClientRect(); if (b.width === 0 || b.height === 0) return;
    if (b.right > rb.right + 1 || b.left < rb.left - 1) out.push(e.tagName + '#' + e.id + '.' + String(e.className).slice(0, 40) + ' w' + Math.round(b.width)); });
  return out; }"""


def widths(page: Page) -> dict:
    return page.evaluate(WIDTHS)


def _wait_right(page: Page, is_open: bool) -> None:
    page.wait_for_function("(o) => { const e = document.getElementById('audit_sidebar'); const w = e ? e.getBoundingClientRect().width : 0; return o ? w > 50 : w < 1; }",
                           arg=is_open, timeout=15_000)


def _open_app(page: Page, url: str, width: int = 1366, stored: str | None = None) -> None:
    """A fresh load at this window width, with the local storage emptied (or set to `stored` before the page runs), and the recipe open."""
    page.set_viewport_size({"width": width, "height": 1000})
    page.goto(url)
    page.evaluate("(v) => { localStorage.clear(); if (v !== null) localStorage.setItem('%s', v); }" % KEY, stored)
    page.reload()
    page.wait_for_selector("#nav_sidebar", timeout=60_000)


def _open_recipe(page: Page, url: str, width: int = 1366) -> None:
    _open_app(page, url, width)
    _load_data_analysis_recipe(page, url)


def _drag(page: Page, handle: str, dx: float) -> None:
    box = page.locator(handle).bounding_box()
    x, y = box["x"] + box["width"] / 2, box["y"] + box["height"] / 2
    page.mouse.move(x, y)
    page.mouse.down()
    page.mouse.move(x + dx, y, steps=8)
    page.mouse.up()
    page.wait_for_timeout(400)


def test_main_panel_share_at_the_four_window_widths(page: Page, shiny_app: ShinyAppProc):
    _open_recipe(page, shiny_app.url)
    for width in WINDOWS:
        page.set_viewport_size({"width": width, "height": 1000})
        set_mode(page, "exploration")
        _wait_right(page, False)
        explo = widths(page)
        assert explo["right"] < 1, explo
        assert explo["main"] / width >= 0.65, f"Exploration at {width}: {explo}"
        set_mode(page, "audit")
        _wait_right(page, True)
        page.wait_for_timeout(400)
        audit = widths(page)
        assert audit["main"] / width >= 0.65, f"Audit at {width}: {audit}"
        assert audit["main"] / width >= fw.MAIN_MIN_SHARE
        assert abs(audit["left"] - fw.default_px(fw.LEFT, width)) < 2 and abs(audit["right"] - fw.default_px(fw.RIGHT, width)) < 2, audit


def test_mode_switch_opens_and_closes_the_right_panel_and_the_other_spaces_keep_it_open(page: Page, shiny_app: ShinyAppProc):
    _open_recipe(page, shiny_app.url)
    _wait_right(page, False)
    set_mode(page, "audit")
    _wait_right(page, True)
    set_mode(page, "exploration")
    _wait_right(page, False)                       # D-0385: leaving Audit mode closes it again
    set_mode(page, "audit")
    _wait_right(page, True)
    page.locator("#sidebar_nav").get_by_text("Gallery", exact=True).first.click()
    wait_shiny(page)
    _wait_right(page, True)                        # D-0381: the other user spaces keep it open
    gallery = widths(page)
    assert gallery["main"] / gallery["W"] >= 0.6, gallery
    page.locator("#sidebar_nav").get_by_text("Home", exact=True).first.click()
    wait_shiny(page)
    set_mode(page, "exploration")
    _wait_right(page, False)                       # back in HOME the state the mode asks for


def test_the_right_panel_opened_by_hand_in_exploration_is_empty(page: Page, shiny_app: ShinyAppProc):
    _open_recipe(page, shiny_app.url)
    set_mode(page, "exploration")
    _wait_right(page, False)
    page.locator(RIGHT_TOGGLE).click()
    _wait_right(page, True)
    # the content of a closed panel is rendered when it is first opened: wait for that render (else the checks below would be vacuous)
    page.wait_for_selector("#right_sidebar_content_ui > *", state="attached", timeout=15_000)
    wait_shiny(page)
    assert page.locator("#audit_sidebar .card").count() == 0
    assert page.locator("#filter_inventory_ui, #btn_apply, .audit-pending-badge").count() == 0
    assert page.locator("#audit_sidebar").inner_text().strip() == ""
    set_mode(page, "audit")                        # the panel renders again in Audit mode
    expect(page.locator("#audit_sidebar .card")).not_to_have_count(0, timeout=10_000)


def test_nothing_sticks_out_of_the_real_panels_at_1100(page: Page, shiny_app: ShinyAppProc):
    _open_recipe(page, shiny_app.url, 1100)
    _navigate_to_mlst_plot(page)
    _open_filters_panel(page)
    for _ in range(12):                            # open every panel of the left sidebar (the list shrinks as they open)
        collapsed = page.locator("#nav_sidebar .accordion-button.collapsed")
        if collapsed.count() == 0:
            break
        collapsed.first.click()
        page.wait_for_timeout(150)
    wait_shiny(page)
    set_mode(page, "audit")
    _wait_right(page, True)
    _choose_column_firmly(page, "year")
    _choose_fb_op(page, "gt")
    wait_shiny(page)
    page.locator("#fb_value").fill("2000")
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    wait_shiny(page)
    assert page.evaluate(OVERFLOW, "#nav_sidebar") == []
    page.locator("#filter_send_to_audit").click()
    page.locator("#propagation_confirm").click()
    wait_shiny(page)
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=15_000)
    assert page.evaluate(OVERFLOW, "#audit_sidebar") == []
    assert page.evaluate(OVERFLOW, "#nav_sidebar") == []
    assert widths(page)["main"] / 1100 >= 0.65


def test_drag_is_kept_after_a_reload_limited_to_half_and_reset_by_a_double_click(page: Page, shiny_app: ShinyAppProc):
    _open_app(page, shiny_app.url, 1366)
    start = widths(page)["left"]
    page.locator(LEFT_HANDLE).hover()
    assert page.locator(LEFT_HANDLE).get_attribute("title") == "Drag to change the panel width. Double-click to reset."
    _drag(page, LEFT_HANDLE, 60)
    dragged = widths(page)["left"]
    assert abs(dragged - (start + 60)) < 3
    stored = page.evaluate("(k) => localStorage.getItem(k)", KEY)
    assert stored is not None and 0.2 < __import__("json").loads(stored)["left"] < 0.23        # a share of the window, not px
    page.reload()
    page.wait_for_selector("#nav_sidebar", timeout=60_000)
    assert abs(widths(page)["left"] - dragged) < 3                                              # restored
    # a drag that would take the main panel under half stops at the limit
    _drag(page, LEFT_HANDLE, 900)
    limit = 1366 * (1 - fw.MAIN_MIN_SHARE) - fw.default_px(fw.RIGHT, 1366)
    assert abs(widths(page)["left"] - limit) < 2, widths(page)
    _load_data_analysis_recipe(page, shiny_app.url)
    set_mode(page, "audit")
    _wait_right(page, True)
    page.wait_for_timeout(400)
    both = widths(page)
    assert both["main"] >= 1366 * fw.MAIN_MIN_SHARE - 2, both              # opening the right panel cannot break the half rule
    # a double click gives the default back and forgets the stored value
    page.locator(LEFT_HANDLE).dblclick()
    page.wait_for_timeout(500)
    assert abs(widths(page)["left"] - start) < 2
    assert page.evaluate("(k) => localStorage.getItem(k)", KEY) is None


def test_many_drags_in_one_page_load_all_work_and_a_real_resize_still_applies_the_share(page: Page, shiny_app: ShinyAppProc):
    """bslib fires window resize events during a drag; re-applying the stored share on each pinned every drag after the first (review of 2026-11-21)."""
    _open_recipe(page, shiny_app.url, 1366)
    set_mode(page, "audit")
    _wait_right(page, True)
    page.wait_for_timeout(500)
    left = widths(page)["left"]
    for dx in (40, 40, -30, 100, -200, 60):
        _drag(page, LEFT_HANDLE, dx)
        want = max(fw.LEFT.floor, left + dx)
        left = widths(page)["left"]
        assert abs(left - want) < 3, (dx, want, left)
    right = widths(page)["right"]
    for dx in (-40, 30, -20):                       # to the left makes the right panel wider
        _drag(page, RIGHT_HANDLE, dx)
        want = right - dx
        right = widths(page)["right"]
        assert abs(right - want) < 3, (dx, want, right)
    page.set_viewport_size({"width": 1600, "height": 1000})   # a real resize: the stored shares apply again
    page.wait_for_timeout(600)
    got = widths(page)
    assert abs(got["left"] - left / 1366 * 1600) < 3 and abs(got["right"] - right / 1366 * 1600) < 3, (got, left, right)


# what a click must reach: the controls of the panels and of the main panel. The grab area of a handle never lies over one of them.
CONTROLS = "input, button, a, select, textarea, label, .selectize-control, .accordion-button, .nav-link, .card, .plot-container, img, svg, canvas, table"
HANDLES_OVER = """([ctl, sel]) => { const out = [];
  for (const h of document.querySelectorAll('.bslib-sidebar-resize-handle')) {
    const b = h.getBoundingClientRect(); if (b.width === 0) continue;
    const prev = h.style.pointerEvents; h.style.pointerEvents = 'none';
    for (let y = b.top + 4; y < b.bottom - 4; y += 12) for (const x of [b.left + 1, (b.left + b.right) / 2, b.right - 1]) {
      const e = document.elementFromPoint(x, y); const c = e && e.closest(ctl); if (c) out.push(c.tagName + '#' + c.id + '.' + String(c.className).slice(0, 30) + ' at ' + Math.round(x) + ',' + Math.round(y)); }
    h.style.pointerEvents = prev; }
  return out; }"""


def test_the_grab_area_of_the_handles_lies_in_the_gap_and_covers_no_control(page: Page, shiny_app: ShinyAppProc):
    """A grab area over a control makes it unclickable (the date calendar near the left panel's edge); it lies between the panel and the main area."""
    _open_recipe(page, shiny_app.url, 1100)
    set_mode(page, "audit")
    _wait_right(page, True)
    page.wait_for_timeout(500)
    got = page.evaluate("""() => { const r = {}; for (const [k, id] of [['left', 'nav_sidebar'], ['right', 'audit_sidebar']]) {
      const a = document.getElementById(id).getBoundingClientRect(); const h = document.getElementById(id).closest('.bslib-sidebar-layout').querySelector(':scope > .bslib-sidebar-resize-handle').getBoundingClientRect();
      r[k] = {aside: [a.left, a.right], handle: [h.left, h.right]}; } return r; }""")
    assert got["left"]["handle"][0] >= got["left"]["aside"][1] - 1, got        # not over the left panel
    assert got["right"]["handle"][1] <= got["right"]["aside"][0] + 1, got      # not over the right panel
    assert got["left"]["handle"][1] - got["left"]["handle"][0] >= 8, got        # still wide enough to grab
    assert page.evaluate(HANDLES_OVER, [CONTROLS, None]) == []


def test_a_control_at_the_right_edge_of_the_left_panel_is_clickable_at_1100(page: Page, shiny_app: ShinyAppProc):
    _open_recipe(page, shiny_app.url, 1100)
    aside = page.locator("#nav_sidebar").bounding_box()
    edge = aside["x"] + aside["width"] - 3
    # the last pixels of the panel (its content and its scroll bar) belong to the panel, not to the handle
    tops = page.evaluate("([x, ys]) => ys.map(y => { const e = document.elementFromPoint(x, y); return e && e.closest('.bslib-sidebar-resize-handle') ? 'handle' : 'ok'; })",
                         [edge, [150, 300, 450, 600, 750]])
    assert set(tops) == {"ok"}, tops
    # a pop-up reaching the edge is above the handle: the stacking order of the handle is lower than the pop-ups (the date calendar has 10)
    z = page.evaluate("() => parseInt(getComputedStyle(document.querySelector('.bslib-sidebar-resize-handle')).zIndex)")
    assert z < 10                       # the date calendar (z-index 10) and Bootstrap's drop-downs (1000) are above it


@pytest.mark.parametrize("space", ["Blueprint Architect", "Test Lab", "Gallery", "Home"])
def test_the_toggle_of_the_right_panel_lies_over_no_content_and_no_accordion_button_is_clipped_at_1100(page: Page, shiny_app: ShinyAppProc, space):
    _open_app(page, shiny_app.url, 1100)
    if space == "Home":
        _load_data_analysis_recipe(page, shiny_app.url)
        set_mode(page, "audit")
        _wait_right(page, True)
    else:
        page.locator("#sidebar_nav").get_by_text(space, exact=True).first.click()
    page.wait_for_timeout(2500)
    got = page.evaluate("""() => { const a = document.getElementById('audit_sidebar'); const t = a.closest('.bslib-sidebar-layout').querySelector(':scope > .collapse-toggle').getBoundingClientRect();
      const first = [...a.querySelectorAll('.sidebar-content *')].find(e => e.getClientRects().length && e.getBoundingClientRect().height > 0 && !e.matches('div:empty'));
      const clipped = [...a.querySelectorAll('.accordion-button')].filter(b => b.scrollWidth > b.clientWidth + 1).map(b => b.textContent.trim().slice(0, 30));
      const inside = [...a.querySelectorAll('.accordion-button')].filter(b => b.getBoundingClientRect().right > a.getBoundingClientRect().right + 1).map(b => b.textContent.trim().slice(0, 30));
      const overlapping = [...a.querySelectorAll('.sidebar-content *')].filter(e => { const b = e.getBoundingClientRect(); return b.width > 0 && b.height > 0 && b.top < t.bottom && b.bottom > t.top && b.left < t.right && b.right > t.left && e.children.length === 0 && (e.textContent || '').trim() !== ''; }).map(e => e.textContent.trim().slice(0, 30));
      return {overlapping, clipped, inside}; }""")
    assert got["overlapping"] == [], got           # no text under the toggle
    assert got["clipped"] == [] and got["inside"] == [], got


@pytest.mark.parametrize("stored", ["not json {", '{"left": "abc"}', '{"left": -0.3}', '{"left": 5}', '{"left": 0.9, "right": null}', "[1, 2]"])
def test_a_broken_stored_value_gives_the_default(page: Page, shiny_app: ShinyAppProc, stored):
    _open_app(page, shiny_app.url, 1366, stored=stored)
    got = widths(page)
    assert abs(got["left"] - fw.default_px(fw.LEFT, 1366)) < 2, (stored, got)


def test_a_stored_share_is_applied_again_when_the_window_changes(page: Page, shiny_app: ShinyAppProc):
    _open_app(page, shiny_app.url, 1366, stored='{"left": 0.25}')
    assert abs(widths(page)["left"] - 0.25 * 1366) < 2
    page.set_viewport_size({"width": 1600, "height": 1000})
    page.wait_for_timeout(500)
    assert abs(widths(page)["left"] - 0.25 * 1600) < 2


def test_the_right_panel_can_be_dragged_too(page: Page, shiny_app: ShinyAppProc):
    _open_recipe(page, shiny_app.url, 1366)
    set_mode(page, "audit")
    _wait_right(page, True)
    page.wait_for_timeout(500)
    start = widths(page)["right"]
    _drag(page, RIGHT_HANDLE, -50)                 # to the left makes the right panel wider
    assert abs(widths(page)["right"] - (start + 50)) < 3
    page.reload()
    page.wait_for_selector("#nav_sidebar", timeout=60_000)
    stored = __import__("json").loads(page.evaluate("(k) => localStorage.getItem(k)", KEY))
    assert "right" in stored and "left" not in stored
