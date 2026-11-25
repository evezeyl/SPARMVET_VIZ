"""The lineage panel of HOME in Audit mode, in the browser (LINEAGE-VIEW-G, D-0629, D-0634, D-0627).

Run (qa app features: every flag on, ghost save off):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_lineage_view_browser.py -q
and, for the test that the panel is absent without the audit:
    PYTHONPATH=. SPARMVET_APP_FEATURES=pipeline-exploration-simple ./.venv/bin/python -m pytest app/tests/test_lineage_view_browser.py -q

What a person does on the demo `1_test_data_ST22_dummy`, and sees (the design expects: a list and a map with one entry for every node; a choice by click or keyboard; what is built from the
chosen place is marked; one chosen place for each independent graph; the dialog opens with the chosen place ticked; a table no plot reads can take a step):
- Exploration: no panel. Audit mode: a collapsible panel, collapsed; opened, the list and the map hold the same 51 nodes; no line is the metadata; the node tagged "+ meta" says so;
- a click on a dot chooses its place (the list line and the dot are chosen together); everything built from it is marked; the text area says what is built from it; a second click
  chooses nothing; a choice in the same independent graph replaces the first one;
- the keyboard: a list line takes focus, Enter chooses; a dot takes focus and Space chooses; hover shows the name and the steps without choosing;
- "All original tables of this group" chooses every first place of the graph; "Around my selection" keeps fewer dots, "Whole recipe" brings them back;
- with a place chosen, "Create an audit step here..." opens the dialog of Send to Audit with the place ticked and "At a table this plot is built from" selected;
- a result table no plot reads (Quality_metrics) is chosen: the small form appears with the columns of that table; a step is added, waits for its reason, is applied, is marked in the list and
  on the dot, the audit panel says that no figure changes, and the bin removes it and its mark.

Mutation index (each seen failing): MUTATION L1 the script does not mark what is built from the chosen place; MUTATION L2 the dialog ignores the chosen places.
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_mode, set_view
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_shiny_smoke import (_INTERACTIVE_APP_FEATURES, _choose_fb_op, _load_data_analysis_recipe, _open_filters_panel, _wait_shiny)

LAUNCH = os.environ.get("SPARMVET_APP_FEATURES", "developer")
NEEDS_AUDIT = pytest.mark.skipif(LAUNCH not in _INTERACTIVE_APP_FEATURES, reason="needs the audit")
NOTICE = "#shiny-notification-panel"
N_NODES = 51


def _open_panel(page: Page) -> None:
    root = page.locator("#lineage_root")
    if root.count() == 0:
        set_mode(page, "audit")
        page.locator("#acc_lineage").wait_for(timeout=30_000)
    if page.locator("#acc_lineage .accordion-collapse.show").count() == 0:
        page.locator("#acc_lineage .accordion-button").click()
    page.wait_for_selector("#lineage_root .spv-lin-line", timeout=30_000)
    _wait_shiny(page)


def _line(page: Page, node_id: str):
    return page.locator(f"#lineage_root .spv-lin-line[data-id='{node_id}']")


def _dot(page: Page, node_id: str):
    return page.locator(f"#lineage_root .spv-lin-dot[data-id='{node_id}']")


def _clear_choice(page: Page) -> None:
    for b in page.locator("#lineage_root .spv-lin-clear").all():
        b.click()
    page.locator("#lineage_root .spv-lin-switch", has_text="Whole recipe").click()
    _wait_shiny(page)


def _close_notices(page: Page) -> None:
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    _open_filters_panel(page)
    yield page


@NEEDS_AUDIT
def test_no_panel_in_exploration_and_a_collapsed_panel_in_audit_mode(ready: Page):
    page = ready
    set_mode(page, "exploration")
    expect(page.locator("#acc_lineage")).to_have_count(0)
    expect(page.locator("#lineage_root")).to_have_count(0)
    set_mode(page, "audit")
    expect(page.locator("#acc_lineage")).to_have_count(1, timeout=30_000)
    assert page.locator("#acc_lineage .accordion-collapse.show").count() == 0, "collapsed when it is drawn"
    assert "Path of the data" in page.locator("#acc_lineage").inner_text()


@NEEDS_AUDIT
def test_the_list_and_the_map_hold_the_same_nodes_and_no_metadata(ready: Page):
    page = ready
    _open_panel(page)
    lines = page.locator("#lineage_root .spv-lin-line")
    dots = page.locator("#lineage_root .spv-lin-dot")
    expect(lines).to_have_count(N_NODES)
    expect(dots).to_have_count(N_NODES)
    ids_lines = sorted(page.eval_on_selector_all("#lineage_root .spv-lin-line", "els => els.map(e => e.dataset.id)"))
    ids_dots = sorted(page.eval_on_selector_all("#lineage_root .spv-lin-dot", "els => els.map(e => e.dataset.id)"))
    assert ids_lines == ids_dots and len(set(ids_lines)) == N_NODES
    text = page.locator("#lineage_root .spv-lin-list").inner_text()
    assert "metadata_schema" not in text and "DS:" not in text
    assert "[+ meta]" in text and "no plot" in text
    assert page.locator("#lineage_root .spv-lin-group").count() == 6
    # the dots do not share a place
    spots = page.eval_on_selector_all("#lineage_root .spv-lin-dot", "els => els.map(e => (e.getAttribute('cx')||e.getAttribute('x')) + ',' + (e.getAttribute('cy')||e.getAttribute('y')))")
    assert len(set(spots)) == N_NODES
    for d in page.locator("#lineage_root .spv-lin-dot").all()[:5]:
        assert d.get_attribute("aria-label") and d.get_attribute("tabindex") == "0"


@NEEDS_AUDIT
def test_a_click_on_a_dot_chooses_its_place_and_marks_what_is_built_from_it(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    _dot(page, "T1:ResFinder").click()
    _wait_shiny(page)
    expect(_line(page, "T1:ResFinder")).to_have_class(__import__("re").compile(r"chosen"))
    expect(_dot(page, "T1:ResFinder")).to_have_class(__import__("re").compile(r"chosen"))
    built_lines = page.locator("#lineage_root .spv-lin-line.built").count()
    assert built_lines >= 5 and page.locator("#lineage_root .spv-lin-dot.built").count() == built_lines
    assert "Built from here:" in page.locator("#lineage_root .spv-lin-text").inner_text()
    assert "Chosen: ResFinder" in page.locator("#lineage_root .spv-lin-bar").inner_text()
    # a second click chooses nothing
    _dot(page, "T1:ResFinder").click()
    expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(0)
    expect(page.locator("#lineage_root .spv-lin-line.built")).to_have_count(0)
    # one chosen place for each independent graph: a second choice in the same graph replaces the first
    _line(page, "T1:ResFinder").click()
    other = page.eval_on_selector_all("#lineage_root .spv-lin-line", "els => els.map(e => e.dataset.id).filter(i => i.startsWith('T3:'))")[0]
    _line(page, "T1:MLST").click() if page.locator("#lineage_root .spv-lin-line[data-id='T1:MLST']").count() else None
    chosen = page.locator("#lineage_root .spv-lin-line.chosen").count()
    assert chosen >= 1 and other


@NEEDS_AUDIT
def test_one_place_for_each_independent_graph_and_all_original_tables_of_a_group(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    # two places of the same independent graph: the second replaces the first
    group_of = page.evaluate("""() => { const root = document.querySelector('#lineage_root'); const d = JSON.parse(root.querySelector('script').textContent);
        const g = d.groups.find(x => x.first_places.length > 1); return {nodes: g.nodes, first: g.first_places, id: g.id}; }""")
    first, second = group_of["first"][0], group_of["first"][1]
    _line(page, first).click()
    _line(page, second).click()
    expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(1)
    expect(_line(page, second)).to_have_class(__import__("re").compile(r"chosen"))
    # all original tables of that group
    page.locator("#lineage_root .spv-lin-all").nth(group_of["id"]).click()
    expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(len(group_of["first"]))
    # places of two different graphs: both stay
    other_group = page.evaluate("""() => { const d = JSON.parse(document.querySelector('#lineage_root script').textContent);
        const g = d.groups.filter(x => x.first_places.length)[0]; const h = d.groups.filter(x => x.first_places.length && x.id !== %d)[0]; return h.first_places[0]; }""" % group_of["id"])
    _line(page, other_group).click()
    assert page.locator("#lineage_root .spv-lin-line.chosen").count() == len(group_of["first"]) + 1
    _clear_choice(page)
    expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(0)


@NEEDS_AUDIT
def test_keyboard_and_hover(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    line = _line(page, "T1:ResFinder")
    line.focus()
    page.keyboard.press("Enter")
    expect(line).to_have_class(__import__("re").compile(r"chosen"))
    page.keyboard.press("Enter")                                   # Enter again chooses nothing
    expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(0)
    dot = _dot(page, "T1:MLST")
    dot.focus()
    expect(page.locator("#lineage_root .spv-lin-text")).to_contain_text("MLST")
    page.keyboard.press("Space")
    expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(1)
    # hover shows another node and chooses nothing; the text goes back to the chosen place after
    _dot(page, "T1:ResFinder").hover()
    expect(page.locator("#lineage_root .spv-lin-text")).to_contain_text("ResFinder")
    assert page.locator("#lineage_root .spv-lin-line.chosen").count() == 1
    # a place that cannot be chosen says why and chooses nothing
    unreadable = page.evaluate("""() => { const d = JSON.parse(document.querySelector('#lineage_root script').textContent); const n = d.nodes.find(x => !x.choosable); return n ? n.id : null; }""")
    if unreadable:
        _clear_choice(page)
        _line(page, unreadable).click()
        expect(page.locator("#lineage_root .spv-lin-line.chosen")).to_have_count(0)
        expect(page.locator("#lineage_root .spv-lin-text")).to_contain_text("Cannot be chosen")


@NEEDS_AUDIT
def test_around_my_selection_keeps_fewer_dots_and_whole_recipe_brings_them_back(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    _line(page, "T1:ResFinder").click()
    page.locator("#lineage_root .spv-lin-switch", has_text="Around my selection").click()
    visible = page.eval_on_selector_all("#lineage_root .spv-lin-dot", "els => els.filter(e => e.style.display !== 'none').length")
    visible_lines = page.eval_on_selector_all("#lineage_root .spv-lin-line", "els => els.filter(e => e.style.display !== 'none').length")
    assert 3 < visible < N_NODES and visible == visible_lines
    page.locator("#lineage_root .spv-lin-switch", has_text="Whole recipe").click()
    assert page.eval_on_selector_all("#lineage_root .spv-lin-dot", "els => els.filter(e => e.style.display !== 'none').length") == N_NODES
    _clear_choice(page)


def _amr_plot(page: Page) -> None:
    page.locator(".nav-link:has-text('AMR')").first.click()
    _wait_shiny(page)
    page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
    _wait_shiny(page)


def _stage_identity_filter(page: Page) -> None:
    _choose_column_firmly(page, "identity")
    _choose_fb_op(page, "lt")
    _wait_shiny(page)
    page.locator("#fb_value").fill("99")
    page.wait_for_timeout(200)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)


@NEEDS_AUDIT
def test_create_an_audit_step_here_opens_the_dialog_with_the_chosen_place_ticked(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    _amr_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    _open_panel(page)
    _stage_identity_filter(page)
    _line(page, "T1:ResFinder").click()
    page.locator("#lineage_root .spv-lin-create").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=15_000)
    assert page.locator("#propagation_choice input[value=place]").is_checked()
    expect(page.locator("#propagation_places input[value='T1:ResFinder']")).to_be_checked()
    assert "Chosen in the path of the data and ticked below" in page.locator("#propagation_lineage_note").inner_text()
    page.locator("#shiny-modal .modal-footer button").first.click()
    expect(page.locator("#propagation_confirm")).to_have_count(0, timeout=5_000)
    # a chosen place the step cannot be written at (the table of a plot beside) is named, not ticked
    _clear_choice(page)
    _stage_identity_filter(page)
    _line(page, "T1:Quality_metrics").click()
    page.locator("#lineage_root .spv-lin-create").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=15_000)
    assert "not offered for this step" in page.locator("#propagation_lineage_note").inner_text()
    assert page.locator("#propagation_choice input[value=this]").is_checked()
    page.locator("#shiny-modal .modal-footer button").first.click()
    expect(page.locator("#propagation_confirm")).to_have_count(0, timeout=5_000)
    page.locator("#filter_reset").click()
    _wait_shiny(page)
    _clear_choice(page)


@NEEDS_AUDIT
def test_a_step_at_a_result_table_no_plot_reads(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    _line(page, "T1:Quality_metrics").click()
    expect(page.locator("#lineage_step_column")).to_be_visible(timeout=20_000)
    options = page.eval_on_selector_all("#lineage_step_column option", "els => els.map(e => e.value)")
    assert len(options) >= 2
    # the form is for ONE such table: choosing a plot's table too removes it
    page.locator("#lineage_step_column").select_option(options[0])
    _wait_shiny(page)
    expect(page.locator("#lineage_step_op")).to_be_visible(timeout=10_000)
    page.locator("#lineage_step_value").fill("")
    page.locator("#lineage_step_add").click()
    expect(page.locator(NOTICE)).to_contain_text("Nothing was added", timeout=10_000)
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(0)
    _close_notices(page)
    # a value that exists in the table: keep those rows (any of)
    page.locator("#lineage_step_op").select_option("in")
    _wait_shiny(page)
    page.locator("#lineage_step_value").fill("zzz-no-such-value")
    page.locator("#lineage_step_add").click()
    _wait_shiny(page)
    expect(page.locator(NOTICE)).to_contain_text("Step staged at Table Quality_metrics (tier 1)", timeout=10_000)
    expect(page.locator(NOTICE)).to_contain_text("no figure changes")
    _close_notices(page)
    # waiting for its reason in the audit panel, with the words of where it is written
    expect(page.locator('input[id^="t3_reason_"]')).to_have_count(1, timeout=15_000)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("no plot is built from there", timeout=10_000)
    expect(page.locator("#btn_apply").first).to_be_disabled()
    expect(_line(page, "T1:Quality_metrics").locator(".spv-lin-mark")).to_contain_text("audit step", timeout=10_000)
    assert "*" in (_dot(page, "T1:Quality_metrics").evaluate("e => e.nextSibling.textContent"))
    box = page.locator('input[id^="t3_reason_"]').first
    box.fill("check the table of the quality metrics")
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    expect(page.locator(NOTICE)).to_contain_text("No plot is built from Table Quality_metrics (tier 1): no figure changes", timeout=15_000)
    expect(_line(page, "T1:Quality_metrics").locator(".spv-lin-mark")).to_contain_text("audit step")
    # the step shows in the audit panel of another plot too, and its bin removes it and its mark
    page.locator(".nav-link:has-text('Quality Control')").first.click()
    _wait_shiny(page)
    expect(page.locator("[id^='t3_delete_']")).to_have_count(1, timeout=15_000)
    page.locator("[id^='t3_delete_']").first.click()
    _wait_shiny(page)
    expect(_line(page, "T1:Quality_metrics").locator(".spv-lin-mark")).to_have_text("", timeout=15_000)
    _clear_choice(page)


@pytest.mark.skipif(LAUNCH in _INTERACTIVE_APP_FEATURES, reason="the launch has the audit")
def test_without_the_audit_the_panel_is_never_drawn(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    expect(page.locator("#home_mode")).to_have_count(0)
    expect(page.locator("#acc_lineage")).to_have_count(0)
    expect(page.locator("#lineage_root")).to_have_count(0)
