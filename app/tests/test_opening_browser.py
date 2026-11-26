"""The opening of a recipe in the browser (opening-build, D-0326, D-0334, D-0335, D-0327).

Run under the qa app features (every flag on, ghost save off), which `gate_stage.running_app` sets:
    PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_opening_browser.py -q -n 3
Each test starts its own app on a staged copy of the 17-plot recipe `1_test_data_ST22_dummy` with an EMPTY store of tables (`app/tests/gate_stage.py`; nothing
tracked is written), so the first opening really builds.

What a person sees, and is proved here:
- the first opening shows a progress line in words ("Opening '<recipe>': tables 12 of 24, plots 5 of 17") that moves from 0 to the totals and goes when the
  opening is done; the theater waits and then shows the plots;
- after the opening every table is stored (files by key) and choosing another plot builds nothing: no file of the store is written and the server prints no build;
- a second visit (a new page, the same app) builds nothing and draws nothing again;
- a recipe with a plot that cannot be drawn is not used: the page falls back to the healthy recipe, says why, says that HOME switched (also when the refusal
  comes on the very first screen), and the server did not crash.

Flags: SPARMVET_APP_FEATURES=qa (`ghost_save` off), SPARMVET_DATA_ANALYSIS_RECIPE=the staged recipe, one app per test. NOT covered: the wording of the progress
line in a narrow window, the memory and the time of a large recipe (measured in `tmpAI`, see the report), two sessions that open the same recipe at the same time,
a deployment whose selector is hidden (headless tests of the theater cover the refused branch).

Browser tests: about 4 minutes.
"""
import re
from pathlib import Path

from playwright.sync_api import Page, expect

from app.tests import gate_stage as g
from app.tests.browser_view import set_mode
from app.tests.gate_stage import wait_shiny

# Collects every message the progress line shows (the page may show only the last one at any moment).
WATCH_PROGRESS = """
window.__progress = [];
document.addEventListener('DOMContentLoaded', () => {
  const note = () => document.querySelectorAll('.shiny-progress .progress-message, .progress-message').forEach(e => {
    const t = (e.textContent || '').trim();
    if (t && window.__progress[window.__progress.length - 1] !== t) window.__progress.push(t);
  });
  new MutationObserver(note).observe(document.documentElement, {subtree: true, childList: true, characterData: true});
});
"""
BUILT_LINES = ("materialize_tier1 DONE", "recomputed from Tier 1", "computed from its Tier 2")


def anchors_of(work: Path) -> Path:
    return work / "user" / "anchors"


def store_state(work: Path) -> dict:
    return {p.name: (p.stat().st_size, p.stat().st_mtime_ns) for p in sorted(anchors_of(work).glob("*.parquet"))}


def built_lines(log: Path) -> list:
    return [line for line in log.read_text().splitlines() if any(mark in line for mark in BUILT_LINES)]


def test_the_progress_line_moves_and_goes_the_tables_are_stored_and_a_plot_switch_builds_nothing(page: Page, tmp_path):
    with g.running_app(tmp_path) as (url, log):
        page.add_init_script(WATCH_PROGRESS)
        page.goto(url)
        page.wait_for_selector("#sidebar_nav", timeout=60_000)
        page.wait_for_function("() => window.__progress.length > 0", timeout=60_000)
        # the opening is over when the theater shows the groups of the recipe
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
        wait_shiny(page, 120_000)
        seen = page.evaluate("() => window.__progress")
        opening = [m for m in seen if m.startswith(f"Opening '{g.STAGE}'")]
        assert len(opening) >= 3, f"the line moved: {seen}"
        first, last = opening[0], opening[-1]
        pattern = re.compile(r"tables (\d+) of (\d+), plots (\d+) of (\d+)$")
        a, b = pattern.search(first), pattern.search(last)
        assert a and b, (first, last)
        assert a.group(1) == "0" and a.group(3) == "0" and b.group(1) == b.group(2) and b.group(3) == b.group(4) == "17", (first, last)
        counts = [tuple(map(int, pattern.search(m).groups())) for m in opening if pattern.search(m)]
        assert counts == sorted(counts), "the counts only go up"
        page.wait_for_function("() => document.querySelectorAll('.shiny-progress').length === 0", timeout=15_000)   # the line is gone
        # the plots show: the first plot tab holds a picture
        expect(page.locator("#dynamic_tabs img").first).to_be_visible(timeout=60_000)

        stored = store_state(g.WORK)
        assert stored and any(name.endswith("__T2.parquet") for name in stored), f"the tables are stored by key: {sorted(stored)}"
        built_before = len(built_lines(log))
        # switch through the plot tabs of the first group: every one reads its stored table
        tabs = page.locator("#dynamic_tabs .nav-underline .nav-link, #dynamic_tabs .nav-tabs .nav-link")
        for i in range(min(tabs.count(), 8)):
            if tabs.nth(i).is_visible():
                tabs.nth(i).click()
                wait_shiny(page, 60_000)
        assert store_state(g.WORK) == stored, "choosing a plot wrote no file of the store"
        assert len(built_lines(log)) == built_before, "the server printed no build while the plots were switched"
        assert g.server_errors(log) == []


def test_a_second_visit_builds_nothing_and_draws_nothing_again(page: Page, browser, tmp_path):
    with g.running_app(tmp_path) as (url, log):
        page.goto(url)
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
        wait_shiny(page, 120_000)
        stored, built = store_state(g.WORK), len(built_lines(log))
        assert built > 0, "the first visit built the tables"
        second = browser.new_page()
        try:
            second.add_init_script(WATCH_PROGRESS)
            second.goto(url)
            second.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=120_000)
            wait_shiny(second, 120_000)
        finally:
            second.close()
        assert store_state(g.WORK) == stored and len(built_lines(log)) == built, "the second visit built nothing"
        assert g.server_errors(log) == []


def test_a_recipe_with_a_plot_that_cannot_be_drawn_is_not_used_and_the_page_says_why(page: Page, tmp_path):
    with g.running_app(tmp_path) as (url, log):
        plot = g.WORK / "recipes" / g.STAGE / "plots" / "MLST_counts_bar.yaml"
        plot.write_text(plot.read_text().replace("x: sequence_type", "x: no_such_column"))   # passes the load gate: the data check does not draw plots
        page.goto(url)
        page.wait_for_selector("#sidebar_nav", timeout=60_000)
        wait_shiny(page, 240_000)
        page.wait_for_function(
            f"() => document.querySelector('#data_analysis_recipe_id') && document.querySelector('#data_analysis_recipe_id').value === '{g.OTHER}'", timeout=240_000)
        assert g.selector_value(page) == g.OTHER, "HOME fell back to the healthy recipe"
        notes = page.locator("#recipe_gate_notes_ui")
        expect(notes).to_contain_text(g.STAGE, timeout=30_000)          # the recipe is listed with the ones HOME does not use
        expect(notes).to_contain_text("Plot 'mlst_bar'", timeout=30_000)  # the reason names the plot
        expect(notes).to_contain_text("no_such_column", timeout=30_000)   # and the column
        # the user is told that HOME switched, never switched silently (ADR-104): the recipe that was open on the first screen is named
        expect(notes).to_contain_text(f"'{g.STAGE}' was open and no longer passes its checks: HOME shows '{g.OTHER}' instead.", timeout=30_000)
        assert g.server_errors(log) == []


# On the first progress message of an opening, what the theater and the Pipeline Audit panel hold at that moment (the opening blocks the server, so what is
# on the page then is what the server sent BEFORE the block).
SNAPSHOT_AT_PROGRESS = """
window.__snap = null;
new MutationObserver(() => {
  if (window.__snap) return;
  const m = Array.from(document.querySelectorAll('.progress-message')).find(e => (e.textContent || '').trim().startsWith("Opening '%s'"));
  if (m) {
    const t = document.querySelector('#dynamic_tabs');
    const a = document.querySelector('#audit_nodes_header_ui');
    const c = document.querySelector('#home_opening_cover');
    const shown = (e) => !!e && e.getClientRects().length > 0 && getComputedStyle(e).visibility !== 'hidden';
    window.__snap = {cover: c ? c.innerText : '', cover_shown: shown(c), theater_shown: shown(t),
                     audit: a && shown(a) ? a.innerText : '',
                     right_text: Array.from(document.querySelectorAll('#right_sidebar_content_ui *')).filter(shown).map(e => e.children.length ? '' : (e.innerText || '')).join(' ').trim(),
                     apply_shown: shown(document.querySelector('#btn_apply')),
                     left_old: ['#data_analysis_recipe_info_ui', '#sidebar_filters', '#data_import_ui', '#system_tools_ui', '#session_management_ui'].filter(i => shown(document.querySelector(i))),
                     selector_shown: shown(document.querySelector('#data_analysis_recipe_id')),
                     tabs: Array.from(document.querySelectorAll('#dynamic_tabs .nav-link')).filter(shown).length};
  }
}).observe(document.documentElement, {subtree: true, childList: true, characterData: true});
"""


def test_while_a_recipe_opens_the_previous_recipe_is_not_on_the_screen(page: Page, tmp_path):
    """HOME-WALK A (D-0334, the owner's yes of 2026-11-20): from the first progress message the theater says which recipe is being opened and holds no
    group tab of the previous recipe, and the right panel does not name the previous recipe. Flags: qa, ghost save off. One app, the staged recipe open first,
    then the second staged recipe is chosen in the selector. Not covered: the wording (PROVISIONAL), a narrow window."""
    with g.running_app(tmp_path) as (url, log):
        page.goto(url)
        page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=240_000)
        wait_shiny(page, 120_000)
        # the right panel is closed and empty in Exploration (D-0375, D-0383) and opens with Audit mode, where the Apply button is shown (D-0377)
        set_mode(page, "audit")
        expect(page.locator("#audit_nodes_header_ui")).to_contain_text(g.STAGE, timeout=60_000)   # the first recipe is shown, the right panel names it
        expect(page.locator("#btn_apply")).to_be_visible()   # before: the right panel is there with its Apply button
        page.evaluate(SNAPSHOT_AT_PROGRESS % g.OTHER)
        page.select_option("#data_analysis_recipe_id", g.OTHER)
        page.wait_for_function("() => window.__snap !== null", timeout=240_000)
        snap = page.evaluate("() => window.__snap")
        assert snap["cover_shown"] and g.OTHER in snap["cover"] and "Opening" in snap["cover"], snap
        assert not snap["theater_shown"] and snap["tabs"] == 0, f"nothing of the previous recipe is visible while the opening runs: {snap}"
        assert g.STAGE not in snap["audit"], f"the right panel does not name the previous recipe: {snap}"
        # D-0372: the previous recipe is not kept on the screen: nothing of the right panel and of the left panels' bodies is visible, no Apply to click
        assert snap["right_text"] == "" and not snap["apply_shown"], f"the right panel shows nothing of the previous recipe during the opening: {snap}"
        assert snap["left_old"] == [], f"the left panel bodies of the previous recipe are hidden: {snap}"
        assert snap["selector_shown"], snap   # the recipe selector stays (PROVISIONAL)
        page.wait_for_selector(".spv-audit-plot-area", timeout=240_000)   # Audit mode has no group tabs (slice 3b): the plot area is what the opening brings back
        wait_shiny(page, 120_000)
        expect(page.locator("#home_opening_cover")).to_have_count(0)
        expect(page.locator("#btn_apply")).to_be_visible()   # after: back
        expect(page.locator("#audit_nodes_header_ui")).to_contain_text(g.OTHER)   # when the opening ends the recipe shows
