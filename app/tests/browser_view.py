"""browser_view.py - the header strip of HOME as the browser tests drive it (slice B, D-0016, D-0310).

# @deps
# consumes: app/handlers/home_theater.py (the inputs home_mode, data_view, source_table, audit_compare)
# consumed_by: app/tests/test_shiny_step_order.py, app/tests/test_tier_decides_filter_form.py, app/tests/test_filter_form_survives_rerender.py, app/tests/test_shiny_plot_tier3.py, app/tests/test_shiny_seed_places.py, app/tests/test_shiny_plot_errors.py, app/tests/test_filters_cleared_on_recipe_change.py, app/tests/test_shiny_session_restore.py, app/tests/test_shiny_apply_blocked.py, app/tests/test_export_download.py, app/tests/test_shiny_smoke.py
# @end_deps

The mode switch (`home_mode`: "exploration" or "audit", only with the audit on) and the data choice (`data_view`: "SRC", "T1", "T2",
"T3"), the second list of Source (`source_table`) and the Compare switch of Audit mode (`audit_compare`). Every call waits until Shiny is
idle and checks that the choice is the one on the page.
"""
from playwright.sync_api import Page, expect


def wait_shiny(page: Page, timeout: int = 10_000) -> None:
    page.wait_for_function("() => !document.documentElement.classList.contains('shiny-busy')", timeout=timeout)


def set_mode(page: Page, mode: str) -> None:
    page.locator(f"#home_mode input[value={mode}]").check(force=True)
    wait_shiny(page)
    expect(page.locator(f"#home_mode input[value={mode}]")).to_be_checked()


def set_view(page: Page, view: str) -> None:
    page.locator(f"#data_view input[value={view}]").check(force=True)
    wait_shiny(page)
    expect(page.locator(f"#data_view input[value={view}]")).to_be_checked()


def set_source(page: Page, table: str) -> None:
    page.locator("#source_table").select_option(table)
    wait_shiny(page)
    expect(page.locator("#source_table")).to_have_value(table)


def set_compare(page: Page, on: bool) -> None:
    page.locator("#audit_compare").set_checked(on, force=True)
    wait_shiny(page)
