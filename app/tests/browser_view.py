"""browser_view.py - the header strip of HOME as the browser tests drive it (slice B, D-0016, D-0310).

# @deps
# consumes: app/handlers/home_theater.py (the inputs home_mode, data_view, source_table, audit_compare), app/src/www/lineage_view.js (the chosen places and their Show buttons)
# consumed_by: app/tests/test_audit_add_browser.py, app/tests/test_audit_one_plot_browser.py, app/tests/test_shiny_na_tick.py, app/tests/test_shiny_step_order.py, app/tests/test_tier_decides_filter_form.py, app/tests/test_filter_form_survives_rerender.py, app/tests/test_shiny_plot_tier3.py, app/tests/test_shiny_seed_places.py, app/tests/test_shiny_plot_errors.py, app/tests/test_filters_cleared_on_recipe_change.py, app/tests/test_shiny_session_restore.py, app/tests/test_shiny_apply_blocked.py, app/tests/test_export_download.py, app/tests/test_shiny_smoke.py
# @end_deps

The mode switch (`home_mode`: "exploration" or "audit", only with the audit on) and the data choice (`data_view`: "SRC", "T1", "T2",
"T3"), the second list of Source (`source_table`) and the Compare switch of Audit mode (`audit_compare`). Every call waits until Shiny is
idle and checks that the choice is the one on the page.
"""
import re

from playwright.sync_api import Page, expect


def wait_shiny(page: Page, timeout: int = 10_000) -> None:
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=timeout)


def set_mode(page: Page, mode: str) -> None:
    """Switch the HOME mode and wait for the SERVER to have taken it (the caption under the control changes with the mode). The click can land before the control is ready, or be undone by a redraw
    of the mode row (found in the first test of several files, always under load): so wait for the control, click, and when the state did not change, click once more; then say plainly if it still did not."""
    wait_shiny(page)       # after a switch of user space the page is still drawing HOME again: a click made then can land on the old control
    radio = page.locator(f"#home_mode input[value={mode}]")
    expect(radio).to_be_attached(timeout=30_000)
    caption = page.locator("#mode_caption_ui")
    was = caption.inner_text() if caption.count() else ""
    last_error = None
    for _attempt in range(2):
        try:
            radio.check(force=True)
        except Exception as exc:        # Playwright: "Clicking the checkbox did not change its state" (a redraw undid the click)
            last_error = exc
        wait_shiny(page)
        if radio.is_checked():
            break
    else:
        raise AssertionError(f"The mode control did not change to {mode!r} after two clicks (last error: {last_error})")
    if was and caption.count():
        try:
            page.wait_for_function("(was) => { const c = document.querySelector('#mode_caption_ui'); return !c || c.innerText !== was; }", arg=was, timeout=20_000)
        except Exception:
            pass       # the caption may be the same in both modes in some setups; the checked control below is the assertion
    wait_shiny(page)
    expect(radio).to_be_checked()


def in_audit_mode(page: Page) -> bool:
    """True when the page is in Audit mode (the mode control says so)."""
    return page.locator("#home_mode input[value=audit]").count() > 0 and page.locator("#home_mode input[value=audit]").is_checked()


def set_view(page: Page, view: str) -> None:
    """The data choice "Table to view" of Exploration. In Audit mode the choice is hidden (slice 3a, D-0652): the table shown is the one chosen in "Path of the data" and shown with the
    button Show (`show_place`); with nothing shown it is the Result data (T3) of the plot of the tab Exploration had, so `set_view(page, "T3")` is true already; any other view is asked of
    `show_place`. There are no plot tabs in Audit mode (slice 3b): when a TABLE is shown, `set_view(page, "T3")` fails and says to name the plot with `show_plot` (the helper never picks
    a plot for the test)."""
    if in_audit_mode(page):
        assert view == "T3", f"In Audit mode there is no 'Table to view': show the place with show_place(page, 'T1:<table>') instead of set_view({view!r})."
        expect(page.locator("#data_view")).to_have_count(0)
        wait_shiny(page)
        band = page.locator("#shown_band_ui")
        assert not band.count() or "Result data, T3" in band.inner_text() or not band.inner_text().strip(), (
            "A table is shown and there are no plot tabs in Audit mode: name the plot whose Result data (T3) the test needs with show_plot(page, '<plot id>').")
        return
    page.locator(f"#data_view input[value={view}]").check(force=True)
    wait_shiny(page)
    expect(page.locator(f"#data_view input[value={view}]")).to_be_checked()


def show_plot(page: Page, plot_id: str) -> None:
    """Audit mode: show the plot `plot_id` (its Result data, T3) in the one plot area. There are no plot tabs in Audit mode (slice 3b, D-0657): a plot is chosen in "Path of the data" and shown.
    Nothing stays chosen."""
    show_place(page, f"T3:{plot_id}", keep_chosen=False)
    expect(page.locator(f"#plot_cell_{plot_id}")).to_be_attached(timeout=30_000)


def show_place(page: Page, place: str, keep_chosen: bool = True) -> None:
    """Audit mode: choose the place in "Path of the data" (a click on its line in the list, unless it is chosen already) and press Show on its line of the chosen places; wait until the
    lineage marks it as shown (slice 3a, D-0655). The panel must be on the page."""
    line = page.locator(f"#lineage_root .spv-lin-line[data-id='{place}']")
    line.wait_for(state="attached", timeout=30_000)
    if "chosen" not in (line.get_attribute("class") or ""):
        line.click()
        wait_shiny(page)
    page.locator(f"#lineage_root .spv-lin-staged .spv-lin-show[data-place='{place}']").click()
    wait_shiny(page)
    expect(page.locator(f"#lineage_root .spv-lin-line[data-id='{place}']")).to_have_class(re.compile(r"\bshown\b"), timeout=30_000)
    if not keep_chosen:
        # the place stays shown; nothing stays chosen (a chosen place is ticked in the dialog of Send to Audit, so a test that only wants to LOOK clears it)
        for b in page.locator("#lineage_root .spv-lin-clear").all():
            b.click()
    wait_shiny(page)


def set_source(page: Page, table: str) -> None:
    page.locator("#source_table").select_option(table)
    wait_shiny(page)
    expect(page.locator("#source_table")).to_have_value(table)


_STILL_JS = """() => new Promise(resolve => {
  const read = () => { const e = document.querySelector('#audit_compare'); if (!e) return null; const r = e.getBoundingClientRect(); return [r.left, r.top, r.width, r.height].map(Math.round).join(','); };
  let last = read(), same = 0, ticks = 0;
  const timer = setInterval(() => { const now = read(); same = (now === last) ? same + 1 : 0; last = now; ticks += 1;
    if (same >= 4 || ticks > 60) { clearInterval(timer); resolve(same >= 4); } }, 100);
})"""


def set_compare(page: Page, on: bool) -> None:
    """Click the Compare switch once the screen has stopped moving under it: entering Audit mode opens the right panel (a width transition) and the layout
    above the switch settles a moment later; a click made while it moves lands beside the switch and changes nothing (found 2026-11-26)."""
    page.locator("#audit_compare").wait_for(state="attached", timeout=15_000)
    page.evaluate(_STILL_JS)
    page.locator("#audit_compare").set_checked(on, force=True)
    wait_shiny(page)


# D-0488: the data preview says its size in the badge ("12 rows", "1 row", "Showing 100 of 2340 rows"); the grid has no summary line of its own
_ROWS_JS = (r"(n) => { const t = (document.querySelector('#home_data_preview_badge') || {}).innerText || '';"
            r" const m = t.match(/(?:of )?(\d+) rows?\b/); return !!m && (n === null || +m[1] === n); }")


def preview_rows(page: Page) -> int:
    """The number of rows the data preview says its table has, read from the badge once it says one."""
    page.wait_for_function(_ROWS_JS, arg=None, timeout=20_000)
    text = page.locator("#home_data_preview_badge").inner_text()
    return int(re.search(r"(?:of )?(\d+) rows?\b", text).group(1))


def wait_preview_rows(page: Page, n: int, timeout: int = 20_000) -> None:
    """Retrying assertion: the data preview says its table has n rows."""
    page.wait_for_function(_ROWS_JS, arg=n, timeout=timeout)


def wait_preview_rows_below(page: Page, n: int, timeout: int = 20_000) -> None:
    """Retrying assertion: the data preview says its table has fewer than n rows."""
    page.wait_for_function(
        r"""(n) => { const t = (document.querySelector('#home_data_preview_badge') || {}).innerText || '';
                    const m = t.match(/(?:of )?(\d+) rows?\b/); return !!m && +m[1] < n; }""", arg=n, timeout=timeout)


# -- the one way to create an audit step (FLOW-3): stage a condition or a drop, Try, (mark), reason, Add to audit pipeline ----------------------------------
ADD_NOTICE = "Step added to the audit pipeline at"


def stage_condition(page: Page, column: str, op: str, value) -> None:
    """Audit mode or Exploration: build one condition row in the Filters panel on the table shown (a number is typed, a text is picked from the list of the column's values) and press "+ Add"."""
    from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
    from app.tests.test_shiny_smoke import _choose_fb_op
    _choose_column_firmly(page, column)
    _choose_fb_op(page, op)
    wait_shiny(page)
    page.wait_for_function("() => document.getElementById('fb_value') !== null", timeout=15_000)
    if page.evaluate("() => !!document.getElementById('fb_value').selectize"):     # a list of the column's values: the value is picked from it (its text)
        text = str(value)
        page.wait_for_function("(v) => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).includes(v); }", arg=text, timeout=15_000)
        page.evaluate("(v) => document.getElementById('fb_value').selectize.addItem(v)", text)
        page.wait_for_function("(v) => document.getElementById('fb_value').selectize.items.includes(v)", arg=text, timeout=5_000)
    else:
        page.locator("#fb_value").fill(repr(value))
        page.wait_for_timeout(200)
    wait_shiny(page)
    page.locator("#filter_add_row").click()
    wait_shiny(page)


def add_to_pipeline(page: Page, reason: str, mark: bool = False, expected_places: int | None = None) -> None:
    """The staged step (a condition built with `stage_condition`, or columns deselected for `drop_columns`) is TRIED already (its panel is on the page): mark "User verified" on every place when
    `mark`, write the reason, press "Add to audit pipeline" and wait for the notice that says it was added. `expected_places`: the number of places the notice must name."""
    panel = page.locator(".spv-trial-panel")
    expect(panel).to_be_visible(timeout=60_000)
    if mark:
        for tick in page.locator("input[id^='trial_verified_']").all():
            tick.check()
        wait_shiny(page)
    box = page.locator("input[id^='trial_reason_']")
    box.fill(reason)
    box.press("Tab")
    wait_shiny(page)
    expect(page.locator("#trial_add")).to_be_enabled(timeout=15_000)
    page.locator("#trial_add").click()
    wait_shiny(page, 60_000)
    text = f"{ADD_NOTICE} {expected_places} place" if expected_places is not None else ADD_NOTICE
    expect(page.locator("#shiny-notification-panel")).to_contain_text(text, timeout=30_000)
    expect(panel).to_have_count(0, timeout=15_000)


def try_staged(page: Page) -> None:
    """Press Try on the staged condition and wait for the panel of the trial."""
    expect(page.locator("#filter_try")).to_be_visible(timeout=15_000)
    page.locator("#filter_try").click()
    wait_shiny(page, 90_000)
    expect(page.locator(".spv-trial-panel")).to_be_visible(timeout=60_000)


def add_condition_step(page: Page, column: str, op: str, value, reason: str, mark: bool = False, expected_places: int | None = None) -> None:
    """The whole way, for a condition: stage it on the table shown, Try, (mark), reason, Add to audit pipeline."""
    stage_condition(page, column, op, value)
    try_staged(page)
    add_to_pipeline(page, reason, mark, expected_places)


def drop_columns(page: Page, columns: list, reason: str, mark: bool = False) -> None:
    """The whole way, for a column drop: deselect the columns in the column chooser of the Result data (T3) shown, Try the drop, (mark), reason, Add to audit pipeline."""
    for column in columns:
        page.evaluate("(c) => { const s = document.getElementById('preview_col_selector').selectize; s.removeItem(c); }", column)
    wait_shiny(page)
    expect(page.locator("#col_drop_try")).to_be_enabled(timeout=15_000)
    page.locator("#col_drop_try").click()
    wait_shiny(page, 90_000)
    add_to_pipeline(page, reason, mark)
