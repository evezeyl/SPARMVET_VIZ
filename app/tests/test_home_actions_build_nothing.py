"""HOME-WALK H: after the opening of a recipe, the user's actions only READ the stored tables; none rebuilds one.

Counted in the walk of 2026-11-20 (and again here): a plot tab, a group tab, a change of the data choice (Source, T1, T2, T3), a change of the mode, adding a filter row
and applying it: no table file of the store is written and the server prints no build line ("materialize_tier1 DONE", "Tier 2 ... recomputed", "Tier 3 ...
computed"). Each of these looks at the stored tables again (a "valid (key match)" line each), which is a read, not a build.

Browser, qa app features (every flag on, ghost save off), one app on the staged recipe with an EMPTY store (the opening builds). NOT covered: a change of the
recipe or of the data (they rebuild by design, other tests), Compare, Export.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_home_actions_build_nothing.py -q
"""
from playwright.sync_api import Page

from app.tests import gate_stage as g
from app.tests.gate_stage import wait_shiny
from app.tests.test_opening_browser import built_lines, store_state


def test_user_actions_after_the_opening_build_nothing(page: Page, tmp_path, monkeypatch):
    monkeypatch.setenv("PYTHONUNBUFFERED", "1")   # the server's log is read as it is written
    with g.running_app(tmp_path) as (url, log):
        page.goto(url)
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
        wait_shiny(page, 120_000)
        stored, built = store_state(g.WORK), built_lines(log)
        assert stored and built, "the opening built and stored the tables"

        page.locator(".nav-link:has-text('AMR')").first.click()
        wait_shiny(page, 60_000)
        page.locator("#dynamic_tabs .nav-link:has-text('MLST Bar')").first.click()
        wait_shiny(page, 60_000)
        # the waits are long: under the load of a parallel run a redraw can take more than the 10 s of `browser_view`
        for radio in ("#data_view input[value=T1]", "#data_view input[value=T2]", "#data_view input[value=SRC]", "#data_view input[value=T3]",
                      "#home_mode input[value=audit]", "#home_mode input[value=exploration]"):
            page.locator(radio).check(force=True)
            wait_shiny(page, 60_000)
        page.locator("#nav_accordion").get_by_text("Filters").first.click()
        wait_shiny(page)
        page.locator("#fb_col").select_option(index=1)
        wait_shiny(page)
        page.evaluate("() => { const s = document.getElementById('fb_value'); if (s && s.selectize) { const v = Object.keys(s.selectize.options)[0]; if (v) s.selectize.addItem(v); } }")
        wait_shiny(page)
        page.locator("#filter_add_row").click()
        wait_shiny(page)
        page.locator("#filter_apply").click()
        wait_shiny(page)
        page.wait_for_timeout(1_500)

        assert store_state(g.WORK) == stored, "no table file of the store was written by a user action"
        assert built_lines(log) == built, f"no build line was printed by a user action: {built_lines(log)[len(built):]}"
        assert g.server_errors(log) == []
