"""A change of recipe must not carry the audit steps of the first recipe to the second (task AUDIT-STEPS-SURVIVE-RECIPE-CHANGE, 2026-11-26).

Run (qa app features):
    PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_audit_steps_survive_recipe_change.py -q

# @deps
# consumes: app/handlers/home_theater.py (the audit steps in the state of HOME, the recipe selector), app/handlers/filter_and_audit_handlers.py (the dialog), app/handlers/audit_stack.py (Apply), app/tests/browser_view.py
# doc: .claude/rules/ui_implementation_contract.md#12g, .claude/knowledge/decision_ledger.md (D-0317, D-0302)
# @end_deps

WHAT IT TESTS. An audit step is written at a place BY NAME (`T1:MLST`, `audit_places.py`), not with the recipe it was written for. The state of HOME that holds the applied steps was reasoned (never run)
to be kept when another recipe is selected (`home_theater._sync_session_provenance` keeps `**cur` and rewrites only the keys). Two shipped recipes hold a table of the same name, `MLST`, with the same
columns and data: `1_test_data_ST22_dummy` and `3_test_no_joins`. A step of the first (remove one sequence type at the tier 1 of MLST) would apply to the second if it survived, and change its table without a
word.

WHAT THE DESIGN EXPECTS (D-0317: a session belongs to its own recipe; nothing of one recipe's audit is applied to another's; D-0050, no silent change of a result): after the other recipe is selected, its
table MLST has all its rows as the engine builds them, the Pipeline Audit panel lists no step, and one plain notice says that the steps of the first recipe are not applied to it. The steps are set
aside for their own recipe: selecting the first recipe again brings them back (what `test_filters_cleared_on_recipe_change.py` has always expected).

The expected rows are computed in the test with polars from the same recipes and data, never typed in.
"""
import re
from pathlib import Path

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import preview_rows, set_mode, show_place, wait_preview_rows, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_filters_cleared_on_recipe_change import _choose_column_firmly
from app.tests.test_shiny_smoke import _choose_fb_op, _choose_recipe, _load_data_analysis_recipe, _navigate_to_mlst_plot, _open_filters_panel, _wait_shiny

A, B = "1_test_data_ST22_dummy", "3_test_no_joins"
ROOT = Path(__file__).resolve().parents[2]
REASON = "survive-test: remove one sequence type"


@pytest.fixture(scope="module")
def expected(tmp_path_factory):
    from app.modules.orchestrator import DataOrchestrator
    orch = DataOrchestrator(ROOT / "config" / "data_analysis_recipes" / "pipelines", ROOT / "assets" / "test_data")
    where = tmp_path_factory.mktemp("survive")
    a = orch.materialize_tier1(A, "MLST", where / "a_MLST.parquet").collect()
    b = orch.materialize_tier1(B, "MLST", where / "b_MLST.parquet").collect()
    counts = b.group_by("sequence_type").len().sort("len", descending=True)
    victim = counts["sequence_type"][0]                       # a sequence type both recipes hold
    assert victim in a["sequence_type"].to_list()
    return {"a": a.height, "b": b.height, "victim": victim, "a_after": a.filter(pl.col("sequence_type") != victim).height,
            "b_if_leaked": b.filter(pl.col("sequence_type") != victim).height}


@pytest.fixture(scope="module")
def ready(page: Page, shiny_app: ShinyAppProc):
    _load_data_analysis_recipe(page, shiny_app.url, A)
    _open_filters_panel(page)
    yield page
    set_mode(page, "exploration")


def _close_notices(page: Page) -> None:
    page.evaluate("() => document.querySelectorAll('#shiny-notification-panel .shiny-notification-close').forEach(b => b.click())")


def test_the_steps_of_one_recipe_are_not_applied_to_another_recipe_with_a_table_of_the_same_name(ready: Page, expected):
    page = ready
    assert expected["a_after"] < expected["a"] and expected["b_if_leaked"] < expected["b"], "the test needs a value that removes rows in both recipes"
    # recipe A: a step at the tier 1 of MLST, applied
    _navigate_to_mlst_plot(page)
    set_mode(page, "audit")
    _choose_column_firmly(page, "sequence_type")
    _choose_fb_op(page, "ne")
    _wait_shiny(page)
    page.wait_for_function("() => { const e = document.getElementById('fb_value'); return e && e.selectize && Object.keys(e.selectize.options).length > 0; }", timeout=20_000)
    page.evaluate("(v) => document.getElementById('fb_value').selectize.addItem(v)", expected["victim"])
    _wait_shiny(page)
    page.locator("#filter_add_row").click()
    _wait_shiny(page)
    expect(page.locator("#filter_send_to_audit")).to_be_visible(timeout=10_000)
    page.locator("#filter_send_to_audit").click()
    expect(page.locator("#propagation_confirm")).to_be_visible(timeout=10_000)
    page.locator("#propagation_choice input[value=place]").check(force=True)
    expect(page.locator("#propagation_places_wrapper")).to_be_visible(timeout=5_000)
    page.locator("#propagation_places input[value='T1:MLST']").set_checked(True, force=True)
    page.locator("#propagation_confirm").click()
    _wait_shiny(page)
    box = page.locator('input[id^="t3_reason_"]').first
    expect(box).to_be_visible(timeout=15_000)
    box.fill(REASON)
    box.press("Tab")
    expect(page.locator("#btn_apply").first).to_be_enabled(timeout=15_000)
    page.locator("#btn_apply").first.click()
    _wait_shiny(page)
    expect(page.locator("#audit_nodes_tier3")).to_contain_text("Written at MLST: Table, T1", timeout=20_000)
    show_place(page, "T1:MLST")
    wait_preview_rows(page, expected["a_after"], timeout=60_000)
    _close_notices(page)
    # recipe B has a table of the same name, MLST, with the same data
    _choose_recipe(page, B)
    expect(page.locator("#data_analysis_recipe_id")).to_have_value(B)
    page.wait_for_selector("#lineage_root .spv-lin-line[data-id='T1:MLST']", timeout=60_000)
    wait_shiny(page)
    show_place(page, "T1:MLST")
    page.wait_for_timeout(3000)
    got = preview_rows(page)
    assert got == expected["b"], f"recipe B shows {got} rows of MLST, the engine builds {expected['b']}: the step of recipe A was applied ({expected['b_if_leaked']} rows if it leaked)"
    assert expected["b"] != expected["b_if_leaked"]
    expect(page.locator("#audit_nodes_tier3")).not_to_contain_text("Written at", timeout=15_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The audit steps of the recipe", timeout=15_000)
    assert "are not applied to" in page.locator("#shiny-notification-panel").inner_text()
    _close_notices(page)
    # back to recipe A: its steps are back (set aside for it, not lost)
    _choose_recipe(page, A)
    page.wait_for_selector("#lineage_root .spv-lin-line[data-id='T1:MLST']", timeout=60_000)
    wait_shiny(page)
    show_place(page, "T1:MLST")
    wait_preview_rows(page, expected["a_after"], timeout=60_000)
