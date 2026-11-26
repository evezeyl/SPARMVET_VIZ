"""browser_view.py - the header strip of HOME as the browser tests drive it (slice B, D-0016, D-0310).

# @deps
# consumes: app/handlers/home_theater.py (the inputs home_mode, data_view, source_table, audit_compare), app/src/www/lineage_view.js (the chosen places and their Show buttons)
# consumed_by: app/tests/test_shiny_na_tick.py, app/tests/test_shiny_step_order.py, app/tests/test_tier_decides_filter_form.py, app/tests/test_filter_form_survives_rerender.py, app/tests/test_shiny_plot_tier3.py, app/tests/test_shiny_seed_places.py, app/tests/test_shiny_plot_errors.py, app/tests/test_filters_cleared_on_recipe_change.py, app/tests/test_shiny_session_restore.py, app/tests/test_shiny_apply_blocked.py, app/tests/test_export_download.py, app/tests/test_shiny_smoke.py
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
    wait_shiny(page)       # after a switch of user space the page is still drawing HOME again: a click made then can land on the old control
    page.locator(f"#home_mode input[value={mode}]").check(force=True)
    wait_shiny(page)
    expect(page.locator(f"#home_mode input[value={mode}]")).to_be_checked()


def in_audit_mode(page: Page) -> bool:
    """True when the page is in Audit mode (the mode control says so)."""
    return page.locator("#home_mode input[value=audit]").count() > 0 and page.locator("#home_mode input[value=audit]").is_checked()


def set_view(page: Page, view: str) -> None:
    """The data choice "Table to view" of Exploration. In Audit mode the choice is hidden (slice 3a, D-0652): the table shown is the one chosen in "Path of the data" and shown with the
    button Show (`show_place`); with nothing shown it is the Result data (T3) of the open plot, so `set_view(page, "T3")` is true already; any other view is asked of `show_place`."""
    if in_audit_mode(page):
        assert view == "T3", f"In Audit mode there is no 'Table to view': show the place with show_place(page, 'T1:<table>') instead of set_view({view!r})."
        expect(page.locator("#data_view")).to_have_count(0)
        wait_shiny(page)
        # "T3" in Audit mode is the Result data of the open plot: show it unless it is shown already
        active = page.locator("[id^='subtabs_'] .nav-link.active:visible")
        value = active.first.get_attribute("data-value") if active.count() else None
        if value and page.locator("#lineage_root .spv-lin-line").count():
            place = "T3:" + value.removeprefix("subtab_")
            line = page.locator(f"#lineage_root .spv-lin-line[data-id='{place}']")
            if line.count() and "shown" not in (line.get_attribute("class") or "").split():
                show_place(page, place, keep_chosen=False)
        return
    page.locator(f"#data_view input[value={view}]").check(force=True)
    wait_shiny(page)
    expect(page.locator(f"#data_view input[value={view}]")).to_be_checked()


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
