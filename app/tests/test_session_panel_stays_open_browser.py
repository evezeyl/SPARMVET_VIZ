"""The session panel does not close the group a person opened when something else of HOME changes (task HOME-SESSION-PANEL-REDRAWS-ON-ANY-STATE; ui_implementation_contract.md section 14, R1 to R4).

Run (qa app features): PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_session_panel_stays_open_browser.py -q

# @deps
# consumes: app/handlers/session_handlers.py (session_management_ui: reads only the session key of the open recipe and data), app/handlers/home_theater.py (_set_open_subtab writes home_state on every Show and every tab click)
# doc: .claude/rules/ui_implementation_contract.md#14
# @end_deps

The panel used to read the whole `home_state` in its render, so every write of that state (a plot tab, a Show in Audit mode, a folded accordion) drew the panel again and closed the
session group the person had opened. A person who opens a group to look at a session and then shows another item lost the group each time.

What is checked: a seeded session group is opened; a click on a plot tab in Exploration, and a Show of another plot and of a table in Audit mode, leave it open.

MUTATION (seen failing, then restored): the render reads `home_state` again (the old code) and the group is closed after the first write.
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import set_mode, show_place, show_plot, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_lineage_view_browser import _open_panel
from app.tests.test_shiny_smoke import (
    _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _wait_session_groups_open, _wait_shiny)

LAUNCH = os.environ.get("SPARMVET_APP_FEATURES", "developer")
NEEDS_AUDIT = pytest.mark.skipif(LAUNCH not in _INTERACTIVE_APP_FEATURES or LAUNCH == "pipeline-exploration-simple", reason="needs the audit")
RECIPE = "1_test_data_ST22_dummy"
LABEL = "panel_stays_open"


def _seed(tmp_path):
    from app.modules.session_manager import SessionManager
    from app.src.bootloader import bootloader
    manager = SessionManager(bootloader.get_location("user_data"))
    recipe = tmp_path / f"{LABEL}.yaml"
    recipe.write_text(f"id: {LABEL}\nanalysis_groups:\n  g:\n    label: G\n    plots:\n      p:\n        label: P\n        spec:\n          target_dataset: C\n"
                      "          mapping: {x: a}\n          layers:\n            - name: geom_bar\n")
    data = tmp_path / f"{LABEL}.tsv"
    data.write_text("a\tb\n1\t2\n")
    msig = SessionManager.compute_data_analysis_recipe_sha256(recipe)
    dbh = SessionManager.compute_data_batch_hash({"d": data})
    key = SessionManager.compute_session_key(msig, dbh)
    manager.write_assembly_ghost(key, LABEL, msig, dbh, {"d": str(data)}, {})
    return manager, key


def _group_is_open(page: Page) -> bool:
    return page.locator("#session_groups_accordion .accordion-collapse.show").count() > 0


def _open_group(page: Page) -> None:
    page.locator("#nav_accordion").get_by_text("Session Management").first.click()
    _wait_shiny(page)
    page.wait_for_selector("#session_groups_accordion", timeout=10_000)
    page.locator("#session_groups_accordion").get_by_text(f"📁 {LABEL}", exact=False).first.click()
    _wait_shiny(page)
    _wait_session_groups_open(page, LABEL)
    assert _group_is_open(page)


def _plot_area_drawn(page: Page) -> None:
    page.wait_for_selector(".spv-plot-accordion, .spv-audit-plot-area", timeout=90_000)
    _wait_shiny(page, 60_000)


@NEEDS_AUDIT
def test_the_group_stays_open_when_a_plot_tab_is_clicked_and_when_items_are_shown(page: Page, shiny_app: ShinyAppProc, tmp_path):
    manager, key = _seed(tmp_path)
    try:
        _load_data_analysis_recipe(page, shiny_app.url, RECIPE)
        _plot_area_drawn(page)
        _open_group(page)
        # Exploration: a click on another plot tab writes home_state (the open plot)
        page.locator(".nav-link:has-text('AMR')").first.click()
        wait_shiny(page)
        page.locator("[id^='subtabs_'] .nav-link:has-text('AMR Heatmap')").first.click()
        wait_shiny(page)
        assert _group_is_open(page), "a click on a plot tab closed the session group"
        # Audit mode: the Show of another plot and of a table writes home_state too
        set_mode(page, "audit")
        _open_panel(page)
        wait_shiny(page)
        assert _group_is_open(page), "entering Audit mode closed the session group"
        show_plot(page, "mlst_bar")
        assert _group_is_open(page), "a Show of another plot closed the session group"
        show_place(page, "T1:ResFinder", keep_chosen=False)
        assert _group_is_open(page), "a Show of a table closed the session group"
        expect(page.locator(f"#session_delete_{key.replace(':', '_')}")).to_be_visible()
        set_mode(page, "exploration")
    finally:
        manager.delete_session(key)
