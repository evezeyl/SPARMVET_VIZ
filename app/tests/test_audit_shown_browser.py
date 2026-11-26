"""The shown item of HOME in Audit mode, in the browser (slice 3a of the new Audit flow; D-0653, D-0654, D-0655, D-0657, D-0311, D-0361).

Run (qa app features: every flag on, ghost save off; the file runs about four minutes on an idle machine):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_shown_browser.py -q
and, for the test that nothing of this exists without the audit:
    PYTHONPATH=. SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy SPARMVET_APP_FEATURES=pipeline-exploration-simple ./.venv/bin/python -m pytest app/tests/test_audit_shown_browser.py -q

# @deps
# consumes: app/handlers/home_theater.py (the band, the data preview, the strip), app/handlers/lineage_handlers.py (Show), app/src/www/lineage_view.js (the chosen places), app/handlers/filter_and_audit_handlers.py (the guard), app/tests/browser_view.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0653, D-0654, D-0655, D-0657)
# @end_deps

The design expects (header-strip design page of 2026-11-26): in Audit mode "Table to view" is hidden; choosing a place in "Path of the data" only stages it and changes nothing on screen; "Show"
(or "Show selection", the first place clicked) makes it the shown item, and then the data preview, its title, its badge, the column chooser and the filter form read that table; a band names
what is shown and whether it is the original or the audited table; with nothing shown the preview shows the table the open plot reads; a click on a plot tab shows that plot; a condition being
built is cleared, with a notice, only when ANOTHER table is shown; the place shown is marked with a word.

What a person does and sees, on the demo `1_test_data_ST22_dummy`:
- "Table to view" exists in Exploration with its own choice, is absent in Audit mode, and Exploration keeps its choice;
- Path of the data is open when Audit mode is entered; with nothing shown the band names the open plot's Result data (T3);
- a choice changes nothing (band, title, preview rows, columns); the chosen place is listed with Show; Show changes all of them, and the column chooser and the filter form hold that table's columns;
- two places in two graphs: "Show selection" shows the first clicked and the band says "1 other place chosen, not shown"; clicking in the other order shows the other;
- a table no plot reads says so; a plot node shows its Result data (there are no plot tabs in Audit mode, slice 3b: `test_audit_one_plot_browser.py`);
- a staged condition survives showing the same table again and is cleared, with a notice, when another table is shown;
- a selection that is not the table shown is refused at the Filters panel's "Send to Audit" with "Show your selection first", and nothing opens;
- leaving Audit mode forgets the shown item; entering it again shows the open plot's table;
- pipeline-exploration-simple (no audit): no band, no lineage, the data choice is there.

Mutation index (each seen failing): MUTATION B1 the server shows the first chosen place as soon as it is chosen (the first test); MUTATION B2 `_forget_shown_item` does not forget (the leave-and-enter test);
MUTATION B3 the key of the view does not hold the table shown (the cleared-with-notice test).
"""
import os
import re

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import in_audit_mode, preview_rows, set_mode, set_view, show_place, wait_preview_rows, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_lineage_view_browser import _clear_choice, _line, _open_panel
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _choose_fb_op, _load_data_analysis_recipe, _open_filters_panel, _wait_shiny
from pathlib import Path

LAUNCH = os.environ.get("SPARMVET_APP_FEATURES", "developer")
NEEDS_AUDIT = pytest.mark.skipif(LAUNCH not in _INTERACTIVE_APP_FEATURES or LAUNCH == "pipeline-exploration-simple", reason="needs the audit")
NO_AUDIT = pytest.mark.skipif(LAUNCH != "pipeline-exploration-simple", reason="the app without the audit")
RECIPE = "1_test_data_ST22_dummy"
ROOT = Path(__file__).resolve().parents[2]


@pytest.fixture(scope="module")
def tables(tmp_path_factory):
    """The rows and the columns of the tables the test looks at, from the engine's own tables (computed here, not typed in)."""
    from app.modules.orchestrator import DataOrchestrator
    orch = DataOrchestrator(ROOT / "config" / "data_analysis_recipes" / "pipelines", ROOT / "assets" / "test_data")
    where = tmp_path_factory.mktemp("shown")
    out = {}
    for name in ("ResFinder", "MLST", "Quality_metrics"):
        out[name] = orch.materialize_tier1(RECIPE, name, where / f"{name}.parquet").collect()
    out["amr_heatmap"] = orch.materialize_tier3(RECIPE, "amr_heatmap", where).collect()
    return out


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url, RECIPE)
    _open_filters_panel(page)
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)
    yield page


@pytest.fixture(autouse=True)
def back_to_exploration(request):
    """Every test leaves the page in Exploration, so that the next one starts from the same place."""
    yield
    if "ready" in request.fixturenames:
        page = request.getfixturevalue("ready")
        try:
            set_mode(page, "exploration")
        except Exception:
            pass


def _band(page: Page) -> str:
    return page.locator("#shown_band_ui").inner_text()


def _enter_audit(page: Page) -> None:
    set_mode(page, "audit")
    _open_panel(page)
    _clear_choice(page)
    wait_shiny(page)


def _title(page: Page) -> str:
    return page.locator("#home_data_preview_title").inner_text()


def _chooser_columns(page: Page) -> list:
    """The columns the column chooser offers (its options), read from the page."""
    return page.eval_on_selector("#preview_col_selector", "el => Array.from(el.options).map(o => o.value)")


def _filter_columns(page: Page) -> list:
    return page.eval_on_selector("#fb_col", "el => Array.from(el.options).map(o => o.value)")


def _wait_columns(page: Page, expected: list) -> None:
    page.wait_for_function("(c) => { const e = document.querySelector('#preview_col_selector'); return !!e && JSON.stringify(Array.from(e.options).map(o => o.value)) === JSON.stringify(c); }",
                           arg=expected, timeout=30_000)


def _stage_condition(page: Page, column: str, value: float) -> None:
    """Add one row to the staged filter (a number column, 'less than' a value), as a person does."""
    _choose_column_firmly(page, column)
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill(repr(value))
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)


def _staged_rows(page: Page) -> int:
    return page.locator("#filter_rows_ui .border.rounded").count()


@NEEDS_AUDIT
def test_table_to_view_is_in_exploration_only_and_exploration_keeps_its_choice(ready: Page):
    page = ready
    set_mode(page, "exploration")
    expect(page.locator("#data_view")).to_have_count(1, timeout=15_000)
    set_view(page, "T2")
    set_mode(page, "audit")
    expect(page.locator("#data_view")).to_have_count(0, timeout=15_000)
    expect(page.locator("body")).not_to_contain_text("Table to view")
    set_mode(page, "exploration")
    expect(page.locator("#data_view input[value=T2]")).to_be_checked(timeout=15_000)
    set_view(page, "T3")


@NEEDS_AUDIT
def test_path_of_the_data_is_open_on_entering_audit_and_nothing_shown_means_the_open_plots_result_data(ready: Page, tables):
    page = ready
    set_mode(page, "audit")
    page.locator("#acc_lineage").wait_for(timeout=30_000)
    assert page.locator("#acc_lineage .accordion-collapse.show").count() == 1, "open when Audit mode is entered"
    page.wait_for_selector("#lineage_root .spv-lin-line", timeout=30_000)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: AMR Heatmap: Result data, T3", timeout=30_000)
    wait_preview_rows(page, tables["amr_heatmap"].height, timeout=60_000)
    expect(_line(page, "T3:amr_heatmap")).to_have_class(re.compile(r"\bshown\b"), timeout=30_000)
    expect(_line(page, "T3:amr_heatmap").locator(".spv-lin-shown")).to_have_text("shown")
    assert "Original (as read)" in _band(page)


@NEEDS_AUDIT
def test_choosing_changes_nothing_and_show_changes_the_preview_the_title_the_chooser_and_the_filter_form(ready: Page, tables):
    page = ready
    _enter_audit(page)
    before = (_band(page).split("\n")[0], _title(page), preview_rows(page))
    _wait_columns(page, tables["amr_heatmap"].columns)
    _line(page, "T1:ResFinder").click()
    _wait_shiny(page)
    page.wait_for_timeout(1500)
    assert (_band(page).split("\n")[0], _title(page), preview_rows(page)) == before, "choosing only stages: what is shown does not change"
    assert _band(page).endswith("1 other place chosen, not shown."), "the band only says that a place is chosen and not shown"
    assert _chooser_columns(page) == tables["amr_heatmap"].columns
    staged = page.locator("#lineage_root .spv-lin-staged-line")
    expect(staged).to_have_count(1)
    expect(staged.first).to_contain_text("ResFinder: Table, T1")
    expect(staged.first.locator(".spv-lin-show")).to_have_text("Show")
    # Show
    page.locator("#lineage_root .spv-lin-show[data-place='T1:ResFinder']").click()
    _wait_shiny(page)
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: ResFinder: Table, T1", timeout=30_000)
    assert "Original (as read)" in _band(page) and "No audit step has been added yet" in _band(page)
    expect(page.locator("#home_data_preview_title")).to_contain_text("ResFinder: Table, T1", timeout=15_000)
    wait_preview_rows(page, tables["ResFinder"].height, timeout=60_000)
    _wait_columns(page, tables["ResFinder"].columns)
    page.wait_for_function("(c) => { const e = document.querySelector('#fb_col'); return !!e && JSON.stringify(Array.from(e.options).map(o => o.value)) === JSON.stringify(c); }",
                           arg=[c for c in tables["ResFinder"].columns], timeout=30_000)
    assert "Viewing: T1" in page.locator("#home_data_preview_badge").inner_text()
    expect(_line(page, "T1:ResFinder")).to_have_class(re.compile(r"\bshown\b"))
    expect(_line(page, "T3:amr_heatmap")).not_to_have_class(re.compile(r"\bshown\b"))
    assert page.locator(f"#lineage_root .spv-lin-dot[data-id='T1:ResFinder']").evaluate("e => e.parentNode.querySelectorAll('.spv-lin-shownmark').length") >= 1
    # slice 3b: a table is not a figure: the plot area says so (the tests of the plot area are in `test_audit_one_plot_browser.py`)
    expect(page.locator(".spv-audit-plot-area")).to_contain_text("No figure: ResFinder: Table, T1 is a table", timeout=30_000)


@NEEDS_AUDIT
def test_a_table_no_plot_reads_and_a_plot_node_are_shown_with_their_own_words(ready: Page, tables):
    page = ready
    _enter_audit(page)
    show_place(page, "T1:Quality_metrics")
    expect(page.locator("#shown_band_ui")).to_contain_text("No plot reads this table.", timeout=30_000)
    wait_preview_rows(page, tables["Quality_metrics"].height, timeout=60_000)
    show_place(page, "T3:mlst_bar")
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: MLST", timeout=30_000)
    assert "Result data, T3" in _band(page)
    expect(page.locator("#home_data_preview_title")).to_contain_text("Result data, T3", timeout=15_000)
    # slice 3b: the plot shown is the open plot (there are no tabs in Audit mode), so a step may be written at it
    expect(page.locator(".spv-audit-plot-area")).to_contain_text("Plot shown: MLST Bar", timeout=30_000)
    expect(page.locator("#filter_controls_ui")).not_to_contain_text("show the Result data (T3)", timeout=15_000)


@NEEDS_AUDIT
def test_show_selection_shows_the_first_place_clicked_and_counts_the_others(ready: Page, tables):
    page = ready
    _enter_audit(page)
    groups = page.evaluate("""() => { const d = JSON.parse(document.querySelector('#lineage_root script').textContent);
        const first = {}; d.nodes.forEach(n => { if (n.choosable && n.kind === 'T1' && !(n.group in first)) first[n.group] = n.id; });
        return Object.values(first); }""")
    assert len(groups) >= 2, groups
    a, b = groups[0], groups[1]
    for order in ((a, b), (b, a)):
        _clear_choice(page)
        for place in order:
            _line(page, place).click()
            _wait_shiny(page)
        expect(page.locator("#lineage_root .spv-lin-staged-line")).to_have_count(2)
        names = page.eval_on_selector_all("#lineage_root .spv-lin-staged-line .spv-lin-staged-name", "els => els.map(e => e.textContent)")
        assert names[0] == page.evaluate("(id) => JSON.parse(document.querySelector('#lineage_root script').textContent).nodes.find(n => n.id === id).line", order[0]), "the list keeps the order of the clicks"
        expect(page.locator("#shown_band_ui")).to_contain_text("chosen, not shown", timeout=15_000)      # the server has the choice (it says how many places are staged)
        page.locator("#lineage_root .spv-lin-showsel").click()
        _wait_shiny(page)
        first_name = page.evaluate("(id) => JSON.parse(document.querySelector('#lineage_root script').textContent).nodes.find(n => n.id === id).line", order[0])
        try:
            expect(page.locator("#shown_band_ui")).to_contain_text(f"Shown: {first_name}", timeout=30_000)
        except AssertionError:
            notes = page.locator("#shiny-notification-panel").inner_text() if page.locator("#shiny-notification-panel").count() else ""
            raise AssertionError(f"order {order}, the band says {_band(page)!r}, the notices say {notes!r}")
        expect(page.locator("#shown_band_ui")).to_contain_text("1 other place chosen, not shown.")
        expect(_line(page, order[0])).to_have_class(re.compile(r"\bshown\b"))
        expect(_line(page, order[1])).not_to_have_class(re.compile(r"\bshown\b"))


@NEEDS_AUDIT
def test_a_staged_condition_is_kept_when_the_same_table_is_shown_again_and_cleared_with_a_notice_when_another_is(ready: Page, tables):
    page = ready
    _enter_audit(page)
    show_place(page, "T1:ResFinder")
    _wait_columns(page, tables["ResFinder"].columns)
    threshold = float(tables["ResFinder"]["identity"].drop_nulls().median())
    _stage_condition(page, "identity", threshold)
    assert _staged_rows(page) == 1
    # the same table shown again: nothing is cleared
    page.locator("#lineage_root .spv-lin-show[data-place='T1:ResFinder']").click()
    _wait_shiny(page)
    page.wait_for_timeout(1500)
    assert _staged_rows(page) == 1, "showing the same table again clears nothing"
    panel = page.locator("#shiny-notification-panel")
    assert panel.count() == 0 or "removed" not in panel.inner_text(), "no notice for nothing"
    # another table: the condition is removed, with a notice
    show_place(page, "T1:MLST")
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The condition you were building was removed because you showed another table", timeout=15_000)
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet", timeout=15_000)
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


@NEEDS_AUDIT
def test_a_selection_that_is_not_the_table_shown_is_refused_at_the_filters_panel(ready: Page, tables):
    page = ready
    _enter_audit(page)
    threshold = float(tables["amr_heatmap"]["identity"].drop_nulls().median())
    _stage_condition(page, "identity", threshold)
    assert _staged_rows(page) == 1
    _line(page, "T1:MLST").click()                         # chosen, not shown
    _wait_shiny(page)
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")
    page.locator("#filter_send_to_audit").click()
    _wait_shiny(page)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("Show your selection first", timeout=15_000)
    assert page.locator("#propagation_confirm").count() == 0, "no dialog opens"
    assert _staged_rows(page) == 1, "the condition is kept: nothing was sent"
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


@NEEDS_AUDIT
def test_leaving_audit_mode_forgets_the_shown_item_and_entering_it_again_shows_the_open_plot(ready: Page, tables):
    page = ready
    _enter_audit(page)
    show_place(page, "T1:ResFinder")
    wait_preview_rows(page, tables["ResFinder"].height, timeout=60_000)
    set_mode(page, "exploration")
    expect(page.locator("#shown_band_ui")).to_have_text("", timeout=15_000)
    expect(page.locator("#acc_lineage")).to_have_count(0)
    set_mode(page, "audit")
    expect(page.locator("#shown_band_ui")).to_contain_text("Shown: AMR Heatmap: Result data, T3", timeout=30_000)
    wait_preview_rows(page, tables["amr_heatmap"].height, timeout=60_000)


@NO_AUDIT
def test_without_the_audit_there_is_no_band_no_lineage_and_the_data_choice_is_there(page: Page, shiny_app: ShinyAppProc):
    page.goto(shiny_app.url)                       # the recipe is named by SPARMVET_DATA_ANALYSIS_RECIPE (these app features hide the selector)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=90_000)
    _wait_shiny(page, 60_000)
    expect(page.locator("#data_view")).to_have_count(1, timeout=30_000)
    assert page.locator("#shown_band_ui").inner_text().strip() == ""
    assert page.locator("#lineage_root").count() == 0 and page.locator("#home_mode").count() == 0 and not in_audit_mode(page)
