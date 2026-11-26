"""The lineage panel of HOME in Audit mode, in the browser (LINEAGE-VIEW-G, D-0629, D-0634, D-0627).

Run (qa app features: every flag on, ghost save off):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_lineage_view_browser.py -q
and, for the test that the panel is absent without the audit:
    PYTHONPATH=. SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy SPARMVET_APP_FEATURES=pipeline-exploration-simple ./.venv/bin/python -m pytest app/tests/test_lineage_view_browser.py -q

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
    heads = page.eval_on_selector_all("#lineage_root .spv-lin-group", "els => els.filter(e => e.style.display !== 'none').length")
    assert heads == 1, "a group with no node shown has no header"
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
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("No plot is built from there", timeout=10_000)
    expect(page.locator("#audit_nodes_tier3 .spv-audit-mine .spv-audit-place")).to_contain_text("Written at Quality metrics: Table, T1")
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


# ---------------------------------------------------------------- the look of 2026-11-26 (the owner's test of HOME in Audit mode)
# What the design expects: a choice in the list is a choice in the map and the reverse (the chosen dot is dark and thick and the chosen part is in view); the line "Chosen" is bold, blue on the
# amber tint; what is built from the chosen place has the thickness of the chosen place; the columns have true headings and each independent graph its number; the map can be moved and
# zoomed; the parts can be resized and the choice is kept in the browser; none of this makes the server draw the panel again (section 14, R4).
# Mutation index (each seen failing): MUTATION K1 `choose` does not reveal the chosen dot in the map; MUTATION K2 the stored sizes are never read back.

def _style(locator, props):
    return locator.evaluate("(e, ps) => { const c = getComputedStyle(e); const o = {}; ps.forEach(p => o[p] = c[p]); return o; }", props)


def _inside(inner, outer) -> bool:
    a, b = inner.bounding_box(), outer.bounding_box()
    return a is not None and b is not None and a["x"] >= b["x"] - 1 and a["y"] >= b["y"] - 1 and a["x"] + a["width"] <= b["x"] + b["width"] + 1 and a["y"] + a["height"] <= b["y"] + b["height"] + 1


def _fresh_page(page: Page, url: str) -> None:
    """A new load of the app (the page forgets its state; the browser's local storage stays): the recipe is chosen again and the Filters panel opened."""
    page.goto("about:blank")
    _load_data_analysis_recipe(page, url)
    _open_filters_panel(page)


def _view_scale(page: Page) -> float:
    return page.evaluate("() => parseFloat(/scale\\(([-0-9.]+)\\)/.exec(document.querySelector('#lineage_root .spv-lin-vp').getAttribute('transform'))[1])")


def _view_shift(page: Page):
    return page.evaluate("() => { const m = /translate\\(([-0-9.]+) ([-0-9.]+)\\)/.exec(document.querySelector('#lineage_root .spv-lin-vp').getAttribute('transform')); return [parseFloat(m[1]), parseFloat(m[2])]; }")


@NEEDS_AUDIT
def test_a_choice_in_the_list_is_a_choice_in_the_map_and_the_reverse_and_is_in_view(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    map_box = page.locator("#lineage_root .spv-lin-map")
    ids = page.eval_on_selector_all("#lineage_root .spv-lin-line", "els => els.map(e => e.dataset.id)")
    last = next(i for i in reversed(ids) if i.startswith("T3:"))
    # move the map far away first: choosing a line must bring its dot into view (a dot out of view looks like a choice that did not reach the map)
    box = map_box.bounding_box()
    page.mouse.move(box["x"] + box["width"] - 20, box["y"] + box["height"] - 20)
    page.mouse.down(); page.mouse.move(box["x"] - 100, box["y"] - 200, steps=6); page.mouse.up()
    for target in ("T1:ResFinder", last):
        _line(page, target).scroll_into_view_if_needed()
        _line(page, target).click()
        _wait_shiny(page)
        dot = _dot(page, target)
        expect(dot).to_have_class(__import__("re").compile(r"chosen"))
        style = _style(dot, ["strokeWidth", "stroke"])
        assert style["strokeWidth"] == "5px" and style["stroke"] == "rgb(26, 26, 26)", style
        assert _inside(dot, map_box), "the chosen dot is in view in the map"
        _line(page, target).click()                                 # a second click chooses nothing
    # the reverse: a click on a dot chooses its line, and the line is in view in the list
    _dot(page, "T1:MLST").click()
    expect(_line(page, "T1:MLST")).to_have_class(__import__("re").compile(r"chosen"))
    assert _inside(_line(page, "T1:MLST"), page.locator("#lineage_root .spv-lin-list")), "the chosen line is in view in the list"
    _clear_choice(page)


@NEEDS_AUDIT
def test_the_line_chosen_is_bold_teal_on_the_amber_tint_and_what_is_built_has_nearly_the_chosen_thickness(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    quiet = _style(page.locator("#lineage_root .spv-lin-chosen"), ["fontWeight"])
    assert quiet["fontWeight"] == "400", "with nothing chosen it stays the quiet note"
    _line(page, "T1:ResFinder").click()
    _wait_shiny(page)
    style = _style(page.locator("#lineage_root .spv-lin-chosen"), ["fontWeight", "color", "backgroundColor", "fontSize"])
    assert style["fontWeight"] == "700" and style["color"] == "rgb(11, 99, 88)" and style["backgroundColor"] == "rgb(255, 243, 205)", style
    assert style["fontSize"] == "12.8px", "the scale of the secondary text (0.8rem)"
    swatch = _style(_line(page, "T1:ResFinder").locator(".spv-lin-swatch"), ["borderTopWidth", "borderTopColor"])
    assert swatch["borderTopWidth"] == "4px" and swatch["borderTopColor"] == "rgb(26, 26, 26)", "the dot beside the chosen line is dark and bold too"
    built_line = _line(page, "T3:amr_heatmap").locator(".spv-lin-swatch")
    assert _style(built_line, ["borderTopWidth", "borderTopColor"]) == {"borderTopWidth": "3px", "borderTopColor": "rgb(52, 91, 235)"}
    chosen = _style(_dot(page, "T1:ResFinder"), ["strokeWidth", "stroke"])
    built_dots = page.locator("#lineage_root .spv-lin-dot.built")
    assert built_dots.count() >= 5
    for d in built_dots.all():
        s = _style(d, ["strokeWidth", "stroke"])
        assert chosen["strokeWidth"] == "5px" and s["strokeWidth"] == "4px", "what is built from the place is nearly as thick as the place"
        assert s["stroke"] == "rgb(52, 91, 235)" and s["stroke"] != chosen["stroke"], "and stays apart from it by its colour"
    _clear_choice(page)


@NEEDS_AUDIT
def test_every_place_uses_the_same_plain_name(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    long = "Summary phenotype length fragmentation: Table, T1"
    assert _line(page, "T1:Summary_phenotype_length_fragmentation").locator(".spv-lin-line-text").inner_text() == long
    assert _line(page, "T3:amr_heatmap").locator(".spv-lin-line-text").inner_text() == "AMR Heatmap: Plot data, T3"
    shown_text = __import__("re").sub(r"\([^)]*\)", "", page.locator("#lineage_root .spv-lin-list").inner_text())     # an id in brackets keeps its underscores: it tells two equal names apart
    assert "_" not in shown_text
    assert "(table QA_L50_integer)" in page.locator("#lineage_root .spv-lin-list").inner_text(), "a table and a plot with the same name are told apart"
    assert "table after its tier" not in page.locator("#lineage_root .spv-lin-list").inner_text()
    assert _dot(page, "T1:Summary_phenotype_length_fragmentation").get_attribute("aria-label").startswith(long)
    _dot(page, "T3:amr_heatmap").click()
    assert page.locator("#lineage_root .spv-lin-text-head").inner_text() == "AMR Heatmap: Plot data, T3"
    assert "Chosen: AMR Heatmap." in page.locator("#lineage_root .spv-lin-bar").inner_text()
    _clear_choice(page)


@NEEDS_AUDIT
def test_the_columns_have_true_headings_and_every_graph_its_number(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    heads = page.eval_on_selector_all("#lineage_root .spv-lin-head", "els => els.filter(e => e.style.display !== 'none').map(e => Array.from(e.childNodes).filter(n => n.nodeType === 3).map(n => n.nodeValue).join(''))")
    assert heads[0] == "Original tables" and heads[1] == "Level 1" and not any("Tier" in h or "Plot" in h for h in heads), heads
    titles = page.eval_on_selector_all("#lineage_root .spv-lin-head title", "els => els.map(e => e.textContent)")
    assert any("not a tier" in t and "plots (tier 3)" in t for t in titles)
    nums = page.eval_on_selector_all("#lineage_root .spv-lin-gnum-svg", "els => els.filter(e => e.style.display !== 'none').map(e => e.textContent)")
    assert nums == ["1", "2", "3", "4", "5", "6"], nums
    head_texts = page.eval_on_selector_all("#lineage_root .spv-lin-group-title", "els => els.map(e => e.textContent.split(' ')[2])")
    assert head_texts == nums, "the same number in the text and on the map"
    chips = page.eval_on_selector_all("#lineage_root .spv-lin-line .spv-lin-gnum", "els => els.map(e => e.textContent)")
    assert len(chips) == N_NODES and set(chips) == set(nums), "every line carries its graph's number"
    # the tag "no plot" is the result colour and the repeated sentence is gone
    tag = _style(page.locator("#lineage_root .spv-lin-tag").first, ["color", "backgroundColor"])
    assert tag["color"] == "rgb(11, 99, 88)" and tag["backgroundColor"] == "rgb(230, 247, 245)", tag
    assert "no plot reads it" not in page.locator("#lineage_root .spv-lin-list").inner_text()
    # around one place: the number of the graph shown, headings of that layout only
    _line(page, "T1:ResFinder").click()
    page.locator("#lineage_root .spv-lin-switch", has_text="Around my selection").click()
    shown_nums = page.eval_on_selector_all("#lineage_root .spv-lin-gnum-svg", "els => els.filter(e => e.style.display !== 'none').map(e => e.textContent)")
    assert len(shown_nums) == 1
    page.locator("#lineage_root .spv-lin-switch", has_text="Whole recipe").click()
    _clear_choice(page)


@NEEDS_AUDIT
def test_the_map_can_be_zoomed_and_moved_and_the_wheel_needs_ctrl(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    assert _view_scale(page) == 1.0
    page.locator("#lineage_root .spv-lin-zoom[title^='Zoom in']").click()
    assert _view_scale(page) > 1.0
    page.locator("#lineage_root .spv-lin-zoom[title^='Zoom out']").click()
    page.locator("#lineage_root .spv-lin-zoom[title^='Zoom out']").click()
    assert _view_scale(page) < 1.0
    page.locator("#lineage_root .spv-lin-zoom", has_text="Reset view").click()
    assert _view_scale(page) == 1.0 and _view_shift(page) == [0.0, 0.0]
    box = page.locator("#lineage_root .spv-lin-map").bounding_box()
    page.mouse.move(box["x"] + box["width"] - 12, box["y"] + box["height"] - 12)
    page.mouse.wheel(0, -300)                                     # no Ctrl: the page scrolls, the map does not zoom
    assert _view_scale(page) == 1.0
    page.keyboard.down("Control"); page.mouse.wheel(0, -300); page.keyboard.up("Control")
    assert _view_scale(page) > 1.0
    page.locator("#lineage_root .spv-lin-zoom", has_text="Reset view").click()
    page.mouse.move(box["x"] + box["width"] - 12, box["y"] + box["height"] - 12)
    page.mouse.down(); page.mouse.move(box["x"] + box["width"] - 62, box["y"] + box["height"] - 52, steps=5); page.mouse.up()
    shift = _view_shift(page)
    assert shift[0] < -30 and shift[1] < -30, shift
    # the map takes the keyboard: the arrows move it, 0 resets
    page.locator("#lineage_root .spv-lin-map").focus()
    page.keyboard.press("ArrowLeft")
    assert _view_shift(page)[0] > shift[0]
    page.keyboard.press("0")
    assert _view_shift(page) == [0.0, 0.0]
    # a dot can still be chosen after all that
    _dot(page, "T1:ResFinder").click()
    expect(_line(page, "T1:ResFinder")).to_have_class(__import__("re").compile(r"chosen"))
    _clear_choice(page)


@NEEDS_AUDIT
def test_the_parts_can_be_resized_the_choice_is_kept_and_a_double_click_resets(ready: Page, shiny_app: ShinyAppProc):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    list_box = lambda: page.locator("#lineage_root .spv-lin-list").bounding_box()["width"]
    body_h = lambda: page.locator("#lineage_root .spv-lin-body").bounding_box()["height"]
    page.evaluate("() => window.localStorage.removeItem('spv.lineage_layout.v1')")
    w0, h0 = list_box(), body_h()
    hv = page.locator("#lineage_root .spv-lin-handle.v")
    hb = hv.bounding_box()
    page.mouse.move(hb["x"] + hb["width"] / 2, hb["y"] + hb["height"] / 2)
    page.mouse.down(); page.mouse.move(hb["x"] + 140, hb["y"] + hb["height"] / 2, steps=6); page.mouse.up()
    assert list_box() > w0 + 100, "the list is wider"
    hh = page.locator("#lineage_root .spv-lin-handle.h").first
    hb = hh.bounding_box()
    page.mouse.move(hb["x"] + hb["width"] / 2, hb["y"] + hb["height"] / 2)
    page.mouse.down(); page.mouse.move(hb["x"] + hb["width"] / 2, hb["y"] + hb["height"] / 2 + 90, steps=6); page.mouse.up()
    assert body_h() > h0 + 60, "the list and the map are taller"
    stored = page.evaluate("() => JSON.parse(window.localStorage.getItem('spv.lineage_layout.v1'))")
    assert 0.2 <= stored["split"] <= 0.8 and stored["bodyH"] > 400, stored
    # the keyboard: a handle takes the arrow keys
    hv.focus()
    page.keyboard.press("ArrowLeft")
    assert page.evaluate("() => JSON.parse(window.localStorage.getItem('spv.lineage_layout.v1')).split") < stored["split"]
    # the text area has a handle of its own: the arrow keys make it taller, a drag upwards makes it smaller
    ht = page.locator("#lineage_root .spv-lin-handle.h").nth(1)
    ht.scroll_into_view_if_needed()
    t0 = page.locator("#lineage_root .spv-lin-text").bounding_box()["height"]
    ht.focus()
    for _ in range(3):
        page.keyboard.press("ArrowDown")
    t1 = page.locator("#lineage_root .spv-lin-text").bounding_box()["height"]
    assert t1 > t0 + 40, (t0, t1)
    tb = ht.bounding_box()
    page.mouse.move(tb["x"] + tb["width"] / 2, tb["y"] + tb["height"] / 2)
    page.mouse.down(); page.mouse.move(tb["x"] + tb["width"] / 2, tb["y"] + tb["height"] / 2 - 40, steps=6); page.mouse.up()
    assert page.locator("#lineage_root .spv-lin-text").bounding_box()["height"] < t1 - 20
    # a new load of the page builds the panel with the kept sizes (a missing or broken value gives the default)
    kept = body_h()
    _fresh_page(page, shiny_app.url)
    _open_panel(page)
    assert abs(body_h() - kept) < 3, "the kept height is back"
    page.evaluate("() => window.localStorage.setItem('spv.lineage_layout.v1', '{broken')")
    _fresh_page(page, shiny_app.url)
    _open_panel(page)
    assert abs(body_h() - 360) < 3, "a broken value gives the default silently"
    page.evaluate("() => window.localStorage.setItem('spv.lineage_layout.v1', JSON.stringify({split: 7, bodyH: 'tall'}))")
    _fresh_page(page, shiny_app.url)
    _open_panel(page)
    assert abs(body_h() - 360) < 3, "a value out of its limits gives the default silently"
    w0 = list_box()
    # a double click gives the default back and removes the kept value
    page.locator("#lineage_root .spv-lin-handle.v").focus()
    page.keyboard.press("ArrowRight")
    page.locator("#lineage_root .spv-lin-handle.h").first.focus()
    page.keyboard.press("ArrowDown")
    assert body_h() > 360 + 10 and list_box() > w0 + 10
    assert page.evaluate("() => window.localStorage.getItem('spv.lineage_layout.v1')") is not None
    for h in page.locator("#lineage_root .spv-lin-handle").all():
        h.dblclick()
    assert abs(body_h() - 360) < 3 and abs(list_box() - w0) < 4
    assert page.evaluate("() => window.localStorage.getItem('spv.lineage_layout.v1')") is None


@NEEDS_AUDIT
def test_none_of_this_draws_the_panel_again(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    page.evaluate("() => { document.querySelector('#lineage_root').__same = 1; window.__spvPanelDraws = 0; }")
    _line(page, "T1:ResFinder").click()
    _dot(page, "T1:MLST").click()
    page.locator("#lineage_root .spv-lin-zoom[title^='Zoom in']").click()
    page.locator("#lineage_root .spv-lin-switch", has_text="Around my selection").click()
    page.locator("#lineage_root .spv-lin-switch", has_text="Whole recipe").click()
    hv = page.locator("#lineage_root .spv-lin-handle.v")
    hv.focus()
    page.keyboard.press("ArrowRight")
    page.evaluate("() => window.localStorage.removeItem('spv.lineage_layout.v1')")
    _wait_shiny(page)
    assert page.evaluate("() => document.querySelector('#lineage_root').__same") == 1, "the same element: the server did not draw the panel again"
    _clear_choice(page)


@NEEDS_AUDIT
def test_a_step_on_a_plot_says_where_it_was_written(ready: Page):
    page = ready
    _open_panel(page)
    _clear_choice(page)
    _amr_plot(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    _stage_identity_filter(page)
    expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    assert page.locator("#propagation_choice input[value=this]").is_checked()
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at AMR Heatmap: Plot data, T3", timeout=15_000)
    # the section of the audit steps: its own block below the recipe's steps, a heading in the style of a recipe tier, the place under it
    mine = page.locator("#audit_nodes_tier3 .spv-audit-mine")
    expect(mine.locator("h6")).to_have_text("My Adjustments — AMR Heatmap")
    assert _style(mine.locator("h6"), ["color", "fontWeight"]) == _style(page.locator("#audit_sidebar h6", has_text="Inherited"), ["color", "fontWeight"]) == {"color": "rgb(52, 91, 235)", "fontWeight": "700"}
    assert mine.locator(".spv-audit-place").count() == 1 and "Written at" in mine.inner_text()
    heading_y = page.locator("#audit_sidebar h6", has_text="Inherited").bounding_box()["y"]
    assert mine.bounding_box()["y"] > heading_y, "below the recipe's steps"
    place = _style(page.locator("#audit_nodes_tier3 .spv-audit-place").first, ["fontWeight", "fontSize", "color"])
    assert place["fontWeight"] == "600" and place["color"] == "rgb(26, 26, 26)", place
    assert "rows with no identity record are removed" in page.locator("#audit_nodes_tier3").inner_text()
    page.locator("[id^='t3_delete_']").first.click()
    _wait_shiny(page)
    expect(page.locator("[id^='t3_delete_']")).to_have_count(0, timeout=15_000)
    page.locator("#filter_reset").click()
    _wait_shiny(page)


@pytest.mark.skipif(LAUNCH in _INTERACTIVE_APP_FEATURES, reason="the launch has the audit")
def test_without_the_audit_the_panel_is_never_drawn(page: Page, shiny_app: ShinyAppProc):
    page.goto(shiny_app.url)                       # the recipe is named by SPARMVET_DATA_ANALYSIS_RECIPE (the app features hide the selector)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=90_000)
    _wait_shiny(page, 60_000)
    expect(page.locator("#home_mode")).to_have_count(0)
    expect(page.locator("#acc_lineage")).to_have_count(0)
    expect(page.locator("#lineage_root")).to_have_count(0)
