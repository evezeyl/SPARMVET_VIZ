"""Add a tried audit step to the audit pipeline, in the browser (FLOW-2 of the new Audit flow; ledger D-0656, D-0662, D-0669, D-0670, D-0672, D-0302, D-0314).

Run, with ghost save ON for the session checks (the checks that need it are skipped under `qa`, where ghost save is off):
    PYTHONPATH=. SPARMVET_APP_FEATURES=developer ./.venv/bin/python -m pytest app/tests/test_audit_add_browser.py -q
and for the last test `SPARMVET_DATA_ANALYSIS_RECIPE=1_test_data_ST22_dummy SPARMVET_APP_FEATURES=pipeline-exploration-simple` (no audit: no Try, no Add).

# @deps
# consumes: app/handlers/trial_handlers.py (the panel, the marks, the reason, Add), app/handlers/audit_stack.py (the cards, the bin, the session save), app/modules/audit_add.py (the words), app/tests/test_audit_try_browser.py (the fixtures)
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0656, D-0662, D-0669, D-0670, D-0672)
# @end_deps

What a person does and sees, on the demo `1_test_data_ST22_dummy` (Audit mode):
- tries a condition at ResFinder (tier 1), sees the mark "User verified" under the place and "0 of 1 place user verified"; "Add to audit pipeline" is disabled and one line says why; ticking the mark
  and typing the reason keep the trial and the mark; with a reason the button is enabled; Add writes the step: one notice, the trial is gone (its folder empty), the right panel lists the step with
  "Written at ResFinder: Table, T1" and "User verified", the table shown says "Audited: your applied steps" and has the rows an independent count gives, the plot built from it equals a fresh audit
  copy with the step appended; the session file (ghost save on) holds the step with its mark and its reason; the bin removes it and the session file no longer holds it;
- two places chosen, one marked: the step is written at BOTH (D-0669), the cards say "User verified" and "not marked as verified";
- a double click adds the step once; changing the condition ends the trial and the marks start again at zero; a Restore of the session brings the added step back with its mark, and does NOT bring back
  a step that was removed.

Mutation index (each seen failing): MUTATION W1 `_add` writes only the places marked (headless test too); MUTATION W2 the Restore reads an older session file (the removal does not save).
"""
import json
import os
from pathlib import Path

import polars as pl
import pytest
from playwright.sync_api import Page, expect
from shiny.run import ShinyAppProc

from app.tests.browser_view import preview_rows, show_place, set_mode, wait_preview_rows, wait_shiny
from app.tests.conftest import shiny_app  # noqa: F401
from app.tests.test_audit_try_browser import (AREA, LAUNCH, NEEDS_AUDIT, PANEL, PLOT, RECIPE, back_to_a_clean_page, build_condition, build_list_condition, close_notices, enter_audit,  # noqa: F401
                                              listing, notices, press_try, ready, tables, trial_files, user_data, world)
from app.tests.test_lineage_view_browser import _line
from app.tests.test_shiny_smoke import _open_filters_panel, _wait_shiny

GHOST = LAUNCH != "qa"
NEEDS_GHOST = pytest.mark.skipif(not GHOST, reason="ghost save is off under qa: run with SPARMVET_APP_FEATURES=developer")
REASON = "poor quality hits below the median identity"
CARDS = "#audit_nodes_tier3"
ADD_NOTICE = "Step added to the audit pipeline at"


@pytest.fixture(scope="module", autouse=True)
def _the_test_process_bootloader_is_started_before_any_trial():
    """The first use of the Bootloader in THIS process removes every folder of `audit_trial` (its start-of-app clean-up, `audit_trial.clean_trials`), the live trial of the app under test included.
    Starting it here, before the first trial, keeps a test that reads the trial folder honest when it is run alone."""
    user_data()


def newest_session_steps() -> list:
    """The audit steps of the newest session file written in the user's folder (ghost save on), [] when there is none."""
    root = user_data() / "_sessions"
    files = sorted(root.glob("*/t3_*.json"), key=lambda p: p.stat().st_mtime_ns) if root.is_dir() else []
    return json.loads(files[-1].read_text())["audit_pipeline"] if files else []


def session_file_count() -> int:
    root = user_data() / "_sessions"
    return len(list(root.glob("*/t3_*.json"))) if root.is_dir() else 0


def mark(page: Page, index: int = 0):
    return page.locator(f"input[id^='trial_verified_'][id$='_{index}']")


def reason_box(page: Page):
    return page.locator("input[id^='trial_reason_']")


def remove_every_step(page: Page) -> None:
    for _ in range(5):
        buttons = page.locator("[id^='t3_delete_']")
        if not buttons.count():
            return
        buttons.first.click()
        wait_shiny(page)


def try_at_resfinder(page: Page, tables) -> None:
    enter_audit(page)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    wait_preview_rows(page, tables["resfinder"].height, timeout=60_000)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_be_visible(timeout=60_000)


@NEEDS_AUDIT
def test_add_after_the_mark_and_the_reason_writes_the_step_and_it_equals_a_fresh_computation(ready: Page, tables, world):
    page = ready
    try_at_resfinder(page, tables)
    panel = page.locator(PANEL)
    expect(panel).to_contain_text("User verified")
    expect(panel).to_contain_text("0 of 1 place user verified")
    expect(page.locator("#trial_add")).to_be_disabled()
    expect(page.locator(".spv-trial-add")).to_contain_text("Write a reason to add this step")
    mark(page).check()
    wait_shiny(page)
    expect(panel).to_contain_text("1 of 1 place user verified")
    reason_box(page).fill(REASON)
    reason_box(page).press("Tab")
    wait_shiny(page)
    expect(page.locator("#trial_add")).to_be_enabled(timeout=15_000)
    expect(panel).to_be_visible()
    expect(mark(page)).to_be_checked()                                                  # typing the reason kept the trial and the mark
    assert trial_files(), "the trial's tables are in the trial's own folder until the step is added"
    sessions_before = session_file_count()
    page.locator("#trial_add").click()
    wait_shiny(page, 60_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text(f"{ADD_NOTICE} 1 place (1 of 1 place user verified).", timeout=30_000)
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    assert trial_files() == [], "the trial's folder is empty after Add"
    expect(page.locator(CARDS)).to_contain_text("Written at ResFinder: Table, T1", timeout=20_000)
    expect(page.locator(CARDS)).to_contain_text("User verified")
    expect(page.locator(CARDS)).not_to_contain_text("PENDING")
    assert page.locator("#audit_pending_badge_ui").count() == 0 and page.locator(".audit-pending-badge").count() == 0, "FLOW-3: there is no Pending badge any more"
    wait_preview_rows(page, tables["kept_resfinder"], timeout=60_000)
    expect(page.locator("#shown_band_ui")).to_contain_text("Audited: your applied steps")
    expect(page.locator("#shown_band_ui")).not_to_contain_text("TRIAL")
    audited = world.audit().table_lazy(RECIPE, "ResFinder", "T1", [world.node(place="T1:ResFinder", params={"column": "identity", "op": "lt", "value": tables["threshold"], "na": "remove", "dtype": "Float64"})], world.plans)
    assert audited.collect().height == tables["kept_resfinder"], "the table shown equals a fresh computation of the audit copy with the step appended"
    show_place(page, f"T3:{PLOT}", keep_chosen=False)
    wait_preview_rows(page, tables["fresh_plot_after_resfinder_step"], timeout=60_000)   # the plot built from it equals a fresh audit copy with the step appended
    assert page.locator("#filter_remove_0").count() == 0, "the staged condition is cleared"
    if GHOST:
        steps = newest_session_steps()
        assert session_file_count() == sessions_before + 1, "one session file written by the Add"
        assert [(n["place"], n["reason"], n["user_verified"]) for n in steps if n["reason"] == REASON] == [("T1:ResFinder", REASON, True)]
        assert all(n.get("verified_at") for n in steps if n["reason"] == REASON) and all(n.get("applied_at") for n in steps if n["reason"] == REASON)
    show_place(page, "T1:ResFinder", keep_chosen=False)
    wait_preview_rows(page, tables["kept_resfinder"], timeout=60_000)
    page.locator("[id^='t3_delete_']").first.click()                                    # the bin of the step: as today
    wait_shiny(page)
    wait_preview_rows(page, tables["resfinder"].height, timeout=60_000)
    expect(page.locator(CARDS)).not_to_contain_text("Written at ResFinder: Table, T1")
    if GHOST:
        assert [n for n in newest_session_steps() if n["reason"] == REASON] == [], "the removal saved the session: a Restore does not bring the step back"


@NEEDS_AUDIT
def test_two_places_one_marked_the_step_is_written_at_both(ready: Page, tables):
    page = ready
    enter_audit(page)
    victim = tables["resfinder"]["sample_id"].drop_nulls().unique().sort()[0]
    show_place(page, "T1:ResFinder", keep_chosen=True)
    _line(page, "T1:Quality_metrics").click()
    wait_shiny(page)
    build_list_condition(page, "sample_id", "not_in", victim)
    press_try(page)
    panel = page.locator(PANEL)
    expect(panel).to_be_visible(timeout=60_000)
    expect(panel).to_contain_text("0 of 2 places user verified")
    mark(page, 0).check()
    wait_shiny(page)
    expect(panel).to_contain_text("1 of 2 places user verified")
    reason_box(page).fill(REASON)
    reason_box(page).press("Tab")
    expect(page.locator("#trial_add")).to_be_enabled(timeout=15_000)
    page.locator("#trial_add").click()
    wait_shiny(page, 60_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text(f"{ADD_NOTICE} 2 places (1 of 2 places user verified).", timeout=30_000)
    expected = {"ResFinder": tables["resfinder"].filter(pl.col("sample_id") != victim).height, "Quality metrics": tables["quality"].filter(pl.col("sample_id") != victim).height}
    show_place(page, "T1:ResFinder", keep_chosen=True)
    wait_preview_rows(page, expected["ResFinder"], timeout=60_000)
    expect(page.locator(CARDS)).to_contain_text("User verified")
    show_place(page, "T1:Quality_metrics", keep_chosen=True)
    wait_preview_rows(page, expected["Quality metrics"], timeout=60_000)
    expect(page.locator(CARDS)).to_contain_text("not marked as verified")             # written there too (D-0669), and honest about the mark
    if GHOST:
        mine = [n for n in newest_session_steps() if n["reason"] == REASON]
        assert sorted((n["place"], n["user_verified"]) for n in mine) == [("T1:Quality_metrics", False), ("T1:ResFinder", True)]
    remove_every_step(page)
    if GHOST:
        assert [n for n in newest_session_steps() if n["reason"] == REASON] == []


@NEEDS_AUDIT
def test_a_double_click_adds_the_step_once(ready: Page, tables):
    page = ready
    try_at_resfinder(page, tables)
    reason_box(page).fill(REASON)
    reason_box(page).press("Tab")
    expect(page.locator("#trial_add")).to_be_enabled(timeout=15_000)
    sessions_before = session_file_count()
    page.locator("#trial_add").dblclick()
    wait_shiny(page, 60_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text(ADD_NOTICE, timeout=30_000)
    assert notices(page).count(ADD_NOTICE) == 1
    expect(page.locator("[id^='t3_delete_']")).to_have_count(1, timeout=15_000)
    wait_preview_rows(page, tables["kept_resfinder"], timeout=60_000)
    if GHOST:
        assert session_file_count() == sessions_before + 1 and len([n for n in newest_session_steps() if n["reason"] == REASON]) == 1


@NEEDS_AUDIT
def test_a_changed_condition_ends_the_trial_and_the_marks_start_again_at_zero(ready: Page, tables):
    page = ready
    try_at_resfinder(page, tables)
    mark(page).check()
    wait_shiny(page)
    expect(page.locator(PANEL)).to_contain_text("1 of 1 place user verified")
    reason_box(page).fill(REASON)
    reason_box(page).press("Tab")
    wait_shiny(page)
    close_notices(page)
    page.locator("#filter_remove_0").click()
    wait_shiny(page)
    expect(page.locator(PANEL)).to_have_count(0, timeout=15_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The condition changed. The trial ended", timeout=15_000)
    build_condition(page, "identity", "lt", tables["threshold"])
    press_try(page)
    expect(page.locator(PANEL)).to_contain_text("0 of 1 place user verified", timeout=60_000)
    expect(mark(page)).not_to_be_checked()
    assert reason_box(page).input_value() == REASON, "the reason typed is a draft: it is not lost with the trial"
    page.locator("#trial_discard").click()
    wait_shiny(page)


@NEEDS_AUDIT
@NEEDS_GHOST
def test_a_restore_brings_back_an_added_step_with_its_mark_and_not_a_removed_one(ready: Page, tables):
    page = ready
    try_at_resfinder(page, tables)
    mark(page).check()
    reason_box(page).fill(REASON)
    reason_box(page).press("Tab")
    expect(page.locator("#trial_add")).to_be_enabled(timeout=15_000)
    page.locator("#trial_add").click()
    wait_shiny(page, 60_000)
    expect(page.locator(CARDS)).to_contain_text("Written at ResFinder: Table, T1", timeout=30_000)
    from app.modules.session_manager import SessionManager
    from app.modules.session_manager import session_input_id_parts
    from app.src.bootloader import bootloader
    manager = SessionManager(bootloader.get_location("user_data"))
    newest = sorted((user_data() / "_sessions").glob("*/t3_*.json"), key=lambda p: p.stat().st_mtime_ns)[-1]
    key = json.loads(newest.read_text())["session_key"]
    safe = session_input_id_parts([s["session_key"] for s in manager.list_all_sessions()])[key]
    if not page.locator(f"#session_restore_{safe}").is_visible():
        page.locator("#nav_accordion").get_by_text("Session Management").first.click()
        wait_shiny(page)
    page.locator(f"#session_restore_{safe}").click()
    wait_shiny(page, 60_000)
    expect(page.locator(CARDS)).to_contain_text("Written at ResFinder: Table, T1", timeout=30_000)
    expect(page.locator(CARDS)).to_contain_text("User verified")
    show_place(page, "T1:ResFinder", keep_chosen=False)
    page.locator("[id^='t3_delete_']").first.click()                                    # remove it: the session is saved without it
    wait_shiny(page)
    expect(page.locator("[id^='t3_delete_']")).to_have_count(0, timeout=15_000)
    page.locator(f"#session_restore_{safe}").click()
    wait_shiny(page, 60_000)
    expect(page.locator(CARDS)).not_to_contain_text("Written at ResFinder: Table, T1")
    assert page.locator("[id^='t3_delete_']").count() == 0, "the removed step did not come back with a Restore"


@pytest.mark.skipif(LAUNCH != "pipeline-exploration-simple", reason="run with SPARMVET_APP_FEATURES=pipeline-exploration-simple")
def test_without_the_audit_there_is_no_add(page: Page, shiny_app: ShinyAppProc):
    page.goto(shiny_app.url)
    page.wait_for_selector("#nav_accordion", timeout=30_000)
    page.wait_for_selector(".nav-link:has-text('Quality Control')", timeout=120_000)
    _wait_shiny(page)
    _open_filters_panel(page)
    page.locator("#filter_add_row").wait_for(state="attached", timeout=30_000)
    for element in ("#filter_try", "#trial_add", "#trial_discard"):
        assert page.locator(element).count() == 0, element
    expect(page.locator(".spv-trial-panel")).to_have_count(0)
