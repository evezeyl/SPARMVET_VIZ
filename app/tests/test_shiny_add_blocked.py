"""Add to audit pipeline pressed before the button was drawn locked again: the page stays alive, the user is told, nothing is added
(APPLY-BLOCKED-1 of the old Apply, ported to the one way of FLOW-3; D-0050, D-0099, D-0672).

"Add to audit pipeline" is disabled while the reason is empty. A click that arrives before the button is redrawn reaches `trial_handlers._add` with no
reason: it must tell the user in one plain line, add nothing, keep the trial and the page alive. The click is forced here as a too-fast user would make
it: the page removes the `disabled` attribute and clicks. Then the reason is typed and Add adds the step.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_add_blocked.py -q
"""
import os

import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import add_to_pipeline, set_mode, set_view, stage_condition, try_staged
from app.tests.conftest import shiny_app  # noqa: F401 — re-exports fixture
from app.tests.test_shiny_session_restore import _RECORD_NOTICES, _free, _notices, _reasons, _seen
from app.tests.test_shiny_smoke import _INTERACTIVE_APP_FEATURES, _load_data_analysis_recipe, _navigate_to_mlst_plot, _open_filters_panel

_LAUNCH_APP_FEATURES = os.environ.get("SPARMVET_APP_FEATURES", "developer")


@pytest.mark.skipif(_LAUNCH_APP_FEATURES not in _INTERACTIVE_APP_FEATURES, reason="needs the audit")
def test_a_forced_add_without_a_reason_keeps_the_page_alive_and_adds_nothing(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url)
    page.evaluate(_RECORD_NOTICES)
    _open_filters_panel(page)
    _navigate_to_mlst_plot(page)
    set_mode(page, "audit")                  # an audit step is made in Audit mode, on the Result data (T3) of the plot shown
    set_view(page, "T3")
    stage_condition(page, "year", "gt", 2000)
    try_staged(page)

    # the contract: the step has no reason, so Add is locked and one line says why
    add = page.locator("#trial_add")
    expect(add).to_be_disabled(timeout=15_000)
    expect(page.locator(".spv-trial-add")).to_contain_text("Write a reason to add this step")

    # a click that comes before the button is drawn again: the page removes `disabled` and clicks
    page.eval_on_selector("#trial_add", "e => { e.disabled = false; e.click(); }")
    _notices(page, "forced Add", "Write a reason to add this step", 1)
    _free(page, "forced Add")
    assert page.locator("#shiny-disconnected-overlay").count() == 0, "the connection was closed: the page is dead"
    assert _seen(page, "Step added to the audit pipeline") == 0, "the step was added without a reason"
    assert _reasons(page) == [], "no step is in the audit panel"
    expect(page.locator(".spv-trial-panel")).to_be_visible()          # the trial is kept: the user writes the reason and goes on

    # the page is alive: a reason is typed and Add now adds
    add_to_pipeline(page, "the reason typed after the refusal", expected_places=1)
    _notices(page, "Add with a reason", "Step added to the audit pipeline", 1)
    assert _reasons(page) == ["the reason typed after the refusal"]
