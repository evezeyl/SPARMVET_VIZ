"""Exploration filters are emptied when the open recipe changes (ADR-099 point 1), and the user is told once.

Headless: the notice rule. Browser (qa app features): the real switch between two recipes that both have `sample_id`.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filters_cleared_on_recipe_change.py -q
"""
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

import re
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import polars as pl

from app.modules.t3_audit_engine import column_is_in_frame, filters_cleared_notice
from app.tests.subprocess_env import app_command, app_env
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_shiny_smoke import _choose_recipe, _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny

A = "1_test_data_ST22_dummy"
B = "2_test_data_ST22_dummy"
NOTICE = "The filters of the previous recipe were removed"


class TestNoticeRule:
    def test_nothing_to_clear_gives_no_notice(self):
        assert filters_cleared_notice(0, 0) is None

    @pytest.mark.parametrize("pending,applied", [(1, 0), (0, 1), (2, 3)])
    def test_something_cleared_gives_one_plain_notice(self, pending, applied):
        text = filters_cleared_notice(pending, applied)
        assert text and text.startswith(NOTICE)
        assert "Audited steps are kept" in text


def _stage_sample_filter(page: Page, recipe: str | None = None) -> str:
    """Stage a `sample_id` in-list filter and return the value chosen; the row is added to the staged list.

    With `recipe`, first wait until the data preview shows that recipe's table (the form's columns follow it)."""
    _open_filters_panel(page)
    if recipe is not None:
        _wait_for_table(page, recipe)
    _choose_column_firmly(page, "sample_id")
    _choose_operator(page, "in")
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }", timeout=10_000)
    value = page.evaluate("() => { const s = document.getElementById('fb_value').selectize; const v = Object.keys(s.options)[0]; s.addItem(v); return v; }")
    page.wait_for_function("(v) => document.getElementById('fb_value').selectize.items.includes(v)", arg=value, timeout=5_000)
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#filter_remove_0")).to_be_visible(timeout=5_000)
    return value


def _choose_column_firmly(page: Page, column: str) -> None:
    """Choose a filter column and check that the form has really taken it: the box holds it AND the dialog text under the
    tick names it (that text is computed from the table for the chosen column, so it is the form's own answer).

    One attempt, no recovery. If the form puts another column back, that is the defect "FORM RESET" (the form was mounted again
    while the server had not yet received the new column; `app/tests/test_filter_form_survives_rerender.py`) and this
    test FAILS with its name; it is not chosen again behind the user's back."""
    _wait_for_fb_col_option(page, column)
    page.locator("#fb_col").select_option(column)
    _wait_shiny(page)
    try:
        page.wait_for_function(
            """(c) => document.getElementById('fb_col').value === c
                && (document.getElementById('filter_na_text_ui') || {innerText: ''}).innerText.includes(' ' + c)""",
            arg=column, timeout=8_000)
    except Exception as exc:
        raise AssertionError(
            f"FORM RESET: the filter form put the column box back to {page.locator('#fb_col').input_value()!r} after {column!r} was chosen "
            f"(the column is in the table, so this is the defect, not a different table)") from exc
    _wait_shiny(page)
    expect(page.locator("#fb_col")).to_have_value(column)


def _choose_operator(page: Page, op: str) -> None:
    """Choose a filter operator once the box offers it (the operator list is rebuilt after a column change and follows the
    column's type) and check the box holds it once Shiny is idle."""
    page.wait_for_function(
        "(op) => Array.from(document.querySelectorAll('#fb_op option')).some(o => o.value === op)", arg=op, timeout=15_000)
    page.locator("#fb_op").select_option(op)
    _wait_shiny(page)
    expect(page.locator("#fb_op")).to_have_value(op)


def _notices(page: Page):
    return page.locator(f".shiny-notification:has-text('{NOTICE}')")


def _fresh(page: Page, base_url: str, recipe: str = A):
    _open_app(page, base_url)
    _choose_recipe(page, recipe)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=20_000)
    _wait_shiny(page)


# The group text must not also match the other recipe's group ("AMR Profiling Insight"): a stale tab would satisfy the wait.
_PLOT_TABS = {A: ("AMR and", "MLST Bar"), B: ("AMR Profiling Insight", "Multi-Resistance by Country")}
# A column that only this plot's table has (exact header text): the data preview shows the table of that plot.
_TABLE_MARKER = {A: "scheme", B: "predicted_phenotype_clean"}


def _wait_for_table(page: Page, recipe: str) -> None:
    """Wait until the plot sub-tab of the recipe is the active one AND the data preview shows that plot's table.
    Shiny's busy flag can be clear while the preview still shows the previous table, so it is not the condition."""
    _, plot = _PLOT_TABS[recipe]
    page.wait_for_function(
        """([plot, marker]) => {
            const active = Array.from(document.querySelectorAll('.nav-link.active')).some(t => t.innerText.includes(plot));
            const heads = Array.from(document.querySelectorAll('#home_data_preview th')).map(t => t.innerText.trim());
            return active && heads.includes(marker);
        }""",
        arg=[plot, _TABLE_MARKER[recipe]], timeout=30_000)


def _open_plot(page: Page, recipe: str) -> None:
    """Open the group tab and the plot sub-tab of the recipe; each click is followed by its real condition (that tab is the
    active one), and the data preview must show that plot's table. A click right after a recipe switch can hit a tab strip
    that is about to be rebuilt, so the group click is repeated until the group is active."""
    group, plot = _PLOT_TABS[recipe]
    group_link = page.locator(f".nav-link:has-text('{group}')").first
    for _ in range(3):
        group_link.click()
        try:
            page.wait_for_function(
                "(g) => Array.from(document.querySelectorAll('.nav-link.active')).some(t => t.innerText.includes(g))",
                arg=group, timeout=5_000)
            break
        except Exception:
            continue
    expect(page.locator(f".nav-link:has-text('{plot}')").first).to_be_visible(timeout=10_000)
    page.locator(f".nav-link:has-text('{plot}')").first.click()
    _wait_for_table(page, recipe)


def _show_table(page: Page, recipe: str) -> None:
    """Open a plot sub-tab of the recipe, in My view, and wait until the data preview shows that plot's table."""
    _open_plot(page, recipe)
    _open_filters_panel(page)
    page.locator("#tier_toggle input[value=T3]").check(force=True)   # My view: the table shows the applied filters
    _wait_shiny(page)
    _wait_for_table(page, recipe)


def _row_count(page: Page) -> int:
    """Rows of the data preview ("Viewing rows 1 through 15 of 15"), read after Shiny is idle."""
    _wait_shiny(page, 30_000)
    grid = page.locator("#home_data_preview")
    expect(grid.locator("tbody tr").first).to_be_visible(timeout=20_000)
    summary = grid.locator(".shiny-data-grid-summary")
    if summary.count() == 0:                       # a table that fits one page has no summary line
        return grid.locator("tbody tr").count()
    return int(re.search(r" of (\d+)", summary.inner_text()).group(1))


def _count_settled(page: Page, expected: int) -> int:
    """The preview reaches `expected` rows (retrying read of the app state); returns the last count seen."""
    deadline = time.time() + 20
    count = _row_count(page)
    while count != expected and time.time() < deadline:
        page.wait_for_timeout(250)   # poll interval of a retrying read
        count = _row_count(page)
    return count


def _count_settled_below(page: Page, unfiltered: int) -> int:
    """The preview drops below the unfiltered count after Apply (retrying read); returns the last count seen."""
    deadline = time.time() + 20
    count = _row_count(page)
    while count >= unfiltered and time.time() < deadline:
        page.wait_for_timeout(250)           # poll interval of a retrying read
        count = _row_count(page)
    return count


class TestRecipeSwitchClearsFilters:
    def test_table_of_the_other_recipe_is_not_filtered(self, page: Page, shiny_app: ShinyAppProc):
        """Real row counts: a filter applied on A must not shrink B's table, and A is unfiltered again on return."""
        _open_app(page, shiny_app.url)
        _choose_recipe(page, B)
        _show_table(page, B)
        unfiltered_b = _row_count(page)
        _choose_recipe(page, A)
        _show_table(page, A)
        unfiltered_a = _row_count(page)          # read from the marked table of A (_show_table waited for it)
        value = _stage_sample_filter(page, A)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        filtered_a = _count_settled_below(page, unfiltered_a)
        assert 1 <= filtered_a < unfiltered_a, "the filter did not change the table: the scenario proves nothing"
        # Every row shown carries the chosen value (no key uniqueness assumed: the count comes from the page).
        col = page.evaluate("() => Array.from(document.querySelectorAll('#home_data_preview th')).map(t => t.innerText.trim()).indexOf('sample_id')")
        shown = page.evaluate("(c) => Array.from(document.querySelectorAll('#home_data_preview tbody tr')).map(r => r.children[c].innerText.trim())", col)
        assert shown and set(shown) == {value}
        _choose_recipe(page, B)
        _show_table(page, B)
        assert _count_settled(page, unfiltered_b) == unfiltered_b
        _choose_recipe(page, A)
        _show_table(page, A)
        assert _count_settled(page, unfiltered_a) == unfiltered_a

    def test_applied_filter_is_removed_and_noticed_once(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _stage_sample_filter(page)
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        _choose_recipe(page, B)
        _wait_shiny(page)
        expect(_notices(page)).to_have_count(1, timeout=8_000)
        _open_filters_panel(page)
        expect(page.locator("#filter_remove_0")).to_have_count(0)
        expect(page.locator("#filter_apply")).not_to_contain_text("(1)")
        expect(page.locator("body")).not_to_contain_text("Active Filters")

    def test_staged_filter_is_removed_and_noticed(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _stage_sample_filter(page)
        _choose_recipe(page, B)
        expect(_notices(page)).to_have_count(1, timeout=8_000)
        _open_filters_panel(page)
        expect(page.locator("#filter_remove_0")).to_have_count(0)

    def test_no_filters_no_notice(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _choose_recipe(page, B)
        page.wait_for_timeout(1_000)   # stays: the absence of a notice needs a time window (a notice would come with the switch)
        expect(_notices(page)).to_have_count(0)
        _choose_recipe(page, A)
        page.wait_for_timeout(1_000)   # stays, same reason
        expect(_notices(page)).to_have_count(0)

    def test_filter_form_is_usable_after_the_switch(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _stage_sample_filter(page)
        _choose_recipe(page, B)
        _open_filters_panel(page)
        _wait_for_fb_col_option(page, "sample_id")
        expect(page.locator("#fb_col")).to_be_visible()
        # A new filter can be staged on the new recipe: the first row is index 0 again.
        _stage_sample_filter(page)

    def test_audited_step_of_recipe_a_is_back_after_returning(self, page: Page, shiny_app: ShinyAppProc):
        _fresh(page, shiny_app.url)
        _open_filters_panel(page)
        _open_plot(page, A)
        page.locator("#tier_toggle input[value=T3]").check(force=True)
        _wait_shiny(page)
        _choose_column_firmly(page, "year")
        _choose_operator(page, "lt")
        page.locator("#fb_value").fill("2050")
        expect(page.locator("#fb_value")).to_have_value("2050")
        page.locator("#filter_add_row").click()
        _wait_shiny(page)
        page.locator("#filter_send_to_audit").click()
        _wait_shiny(page)
        page.locator("#propagation_confirm").click()
        _wait_shiny(page)
        reason = page.locator("textarea[id^='t3_reason_'], input[id^='t3_reason_']").first
        expect(reason).to_be_visible(timeout=8_000)
        reason.fill("test reason")
        _wait_shiny(page)
        page.locator("#btn_apply").click()
        _wait_shiny(page)
        expect(page.locator("body")).to_contain_text("year", timeout=5_000)
        _choose_recipe(page, B)
        # The audited step is not a staged filter: no notice for it, nothing cleared.
        expect(_notices(page)).to_have_count(0)
        _choose_recipe(page, A)
        page.wait_for_selector(".nav-link:has-text('AMR')", timeout=20_000)
        _open_plot(page, A)
        expect(page.locator("body")).to_contain_text("year < 2050", timeout=20_000)


class TestColumnIsInFrame:
    def test_present_and_absent(self):
        lf = pl.DataFrame({"year": [1]}).lazy()
        assert column_is_in_frame(lf, "year")
        assert not column_is_in_frame(lf, "Year")        # case matters: recipe 2 has Year, recipe 1 has year
        assert not column_is_in_frame(pl.DataFrame({"a": [1]}), "year")

    def test_no_frame_stays_an_error_for_the_caller(self):
        assert column_is_in_frame(None, "year")


REPO = Path(__file__).resolve().parents[2]
LOG = REPO / "tmpAI" / "browser_switch_filters" / "server.log"


def test_recipe_switch_with_a_column_chosen_logs_no_counts_error(page: Page):
    """Finding 5 of the switch check: after A -> B with `year` chosen in the filter form, the server log has no
    "counts ... could not be computed" and the form's text names B's own column."""
    LOG.parent.mkdir(parents=True, exist_ok=True)
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
    with open(LOG, "w") as out:
        proc = subprocess.Popen(app_command(port), cwd=REPO, env=app_env(SPARMVET_APP_FEATURES="qa"), stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(90):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            _fresh(page, url)
            _open_filters_panel(page)
            _wait_for_fb_col_option(page, "year")
            page.locator("#fb_col").select_option("year")
            _wait_shiny(page)
            _choose_recipe(page, B)
            expect(page.locator("#filter_na_text_ui")).to_contain_text("Year", timeout=20_000)
            expect(page.locator("#filter_na_text_ui")).not_to_contain_text("could not be computed")
        finally:
            proc.terminate()
            proc.wait(timeout=20)
    assert "could not be computed" not in LOG.read_text()
