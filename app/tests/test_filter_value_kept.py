"""The value the user typed in the Filters panel is not thrown away when the operator is chosen (D-0050: no silent error).

# @deps
# consumes: app/modules/t3_audit_engine.py (value_widget_for, ops_for_column, value_box_kind), app/handlers/filter_and_audit_handlers.py (filter_value_ui), app/tests/test_shiny_plot_errors.py (staged_app), app/tests/browser_view.py
# @end_deps

The defect (found with timelines over 20 repeats): the server drew the value box again at every choice of the operator, also when the
box did not change kind. A number typed before that redraw arrived was thrown away, and "+ Add row" then added the row with the smallest
value of the column ("value >= 1" for "value >= 100"): a filter with another value than the typed one, and no word.

Decided behaviour: the value box is drawn again only when the KIND of box changes (one number; two numbers for between; a list; ...,
`t3_audit_engine.value_widget_for`). Within one kind a change of operator leaves the box, and what is typed in it, as it is.

Headless: the kind of box by column type and operator (a change among the one-value comparisons never changes it).
Browser (qa app features, the staged recipe of `test_shiny_plot_errors.py`): the user's order of acts with no wait between the choice of
the operator and the typing; set `FILTER_VALUE_REPEAT=20` to repeat the browser tests (the defect shows in a part of the runs only).

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filter_value_kept.py -q
"""
import os

import polars as pl
import pytest
from playwright.sync_api import Page, expect

from app.modules.t3_audit_engine import ops_for_column, value_box_kind, value_widget_for
from app.tests.browser_view import set_mode, set_view
from app.tests.test_shiny_plot_errors import BAD, THRESHOLD, _open_home, _show_plot, staged_app  # noqa: F401  (staged_app is a fixture)
from app.tests.test_shiny_smoke import _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from app.tests.test_shiny_step_order import _press

REPEAT = int(os.environ.get("FILTER_VALUE_REPEAT", "1"))

ONE_VALUE = ["eq", "ne", "gt", "ge", "lt", "le"]


# ---- headless: the kind of box --------------------------------------------------------------------------------------------------

@pytest.mark.parametrize("dtype", [pl.Int64, pl.Float64])
def test_on_a_number_column_the_six_one_value_operators_need_the_same_box(dtype):
    """A change among them must never change the kind: the handler draws the box again only when the kind changes."""
    assert {value_widget_for(dtype, False, op) for op in ONE_VALUE} == {"number"}


def test_on_a_discrete_number_column_the_comparisons_share_one_box_and_the_list_operators_another():
    comparisons = {value_widget_for(pl.Int64, True, op) for op in ("gt", "ge", "lt", "le")}
    lists = {value_widget_for(pl.Int64, True, op) for op in ("in", "not_in", "eq", "ne")}
    assert comparisons == {"number"} and lists == {"list"}


@pytest.mark.parametrize("dtype, discrete, kinds", [
    (pl.Int64, False, {"number": ONE_VALUE, "range": ["between"]}),
    (pl.Float64, False, {"number": ONE_VALUE, "range": ["between"]}),
    (pl.Int64, True, {"list": ["in", "not_in", "eq", "ne"], "number": ["gt", "ge", "lt", "le"], "range": ["between"]}),
    (pl.String, False, {"list": ["in", "not_in", "eq", "ne"]}),
    (pl.Categorical, False, {"list": ["in", "not_in", "eq", "ne"]}),
    (pl.Boolean, False, {"bool": ["eq", "ne"]}),
    (pl.Date, False, {"list": ["in", "not_in"], "date": ONE_VALUE, "date_range": ["between"]}),
    (pl.Datetime, False, {"list": ["in", "not_in"], "datetime": ONE_VALUE, "datetime_range": ["between"]}),
    (pl.Time, False, {"time": ONE_VALUE, "time_range": ["between"]}),
    (pl.Duration, False, {"duration": ONE_VALUE, "duration_range": ["between"]}),
])
def test_the_kind_of_box_is_decided_by_the_operator_family_only(dtype, discrete, kinds):
    """The table of kinds: every operator offered is in exactly one family, and a family has one kind."""
    offered = ops_for_column(dtype, discrete)
    assert sorted(op for ops in kinds.values() for op in ops) == sorted(offered)
    for kind, ops in kinds.items():
        assert {value_box_kind(dtype, discrete, op) for op in ops} == {kind}, "the kind the form draws the box for is by the family only"


def test_the_kind_of_box_for_an_operator_the_column_does_not_offer_is_the_one_of_the_first_operator():
    """As the operator select shows it (the first offered): a stale operator of another column never gives a box of its own."""
    assert value_box_kind(pl.Int64, False, "in") == value_box_kind(pl.Int64, False, "eq") == "number"
    assert value_box_kind(pl.String, False, None) == value_box_kind(pl.String, False, "between") == "list"


def test_a_column_with_no_filter_has_no_box():
    assert value_box_kind(pl.Binary, False, "eq") is None


# ---- browser: what the user typed stays ----------------------------------------------------------------------------------------

def _open_the_filter_form(page: Page, staged_app: str) -> None:
    _open_home(page, staged_app)
    _show_plot(page, BAD)
    _open_filters_panel(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    _wait_for_fb_col_option(page, "value")
    page.locator("#fb_col").select_option("value")
    _wait_shiny(page)


def _rows(page: Page) -> str:
    return page.locator("#filter_rows_ui").inner_text()


@pytest.mark.parametrize("i", range(REPEAT))
def test_a_value_typed_right_after_choosing_the_operator_is_the_value_of_the_row(page: Page, staged_app, i):
    """Choose the number column, choose the operator, type 100 AT ONCE (no wait for the server), Tab, add: the row reads value >= 100."""
    _open_the_filter_form(page, staged_app)
    page.locator("#fb_op").select_option("ge")
    page.locator("#fb_value").fill(str(THRESHOLD))
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    expect(page.locator("#fb_value")).to_have_value(str(THRESHOLD))
    _press(page, "#filter_add_row")
    _wait_shiny(page)
    expect(page.locator("#filter_rows_ui")).to_contain_text(f"value ≥ {THRESHOLD}", timeout=10_000)


@pytest.mark.parametrize("i", range(REPEAT))
def test_a_change_of_operator_after_typing_keeps_the_typed_value(page: Page, staged_app, i):
    """Type 100, then change the operator among the one-value comparisons: the same box still holds 100 and the row has it."""
    _open_the_filter_form(page, staged_app)
    page.locator("#fb_op").select_option("ge")
    page.locator("#fb_value").fill(str(THRESHOLD))
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    box = page.locator("#fb_value").element_handle()
    for op in ("gt", "le", "ne", "ge"):
        page.locator("#fb_op").select_option(op)
        _wait_shiny(page)
        assert box.evaluate("e => e.isConnected"), f"the box was drawn again at the operator {op}"
        expect(page.locator("#fb_value")).to_have_value(str(THRESHOLD))
    page.locator("#fb_op").select_option("gt")
    _wait_shiny(page)
    _press(page, "#filter_add_row")
    _wait_shiny(page)
    expect(page.locator("#filter_rows_ui")).to_contain_text(f"value > {THRESHOLD}", timeout=10_000)


def test_a_change_of_kind_shows_the_new_boxes_and_adds_nothing(page: Page, staged_app):
    """From one value (>= 100 typed) to between: two EMPTY boxes (the typed value is not carried, D-0503; no default is a value, D-0504), no row until the user adds one."""
    _open_the_filter_form(page, staged_app)
    page.locator("#fb_op").select_option("ge")
    page.locator("#fb_value").fill(str(THRESHOLD))
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    page.locator("#fb_op").select_option("between")
    page.wait_for_selector("#fb_value_lo", timeout=15_000)
    _wait_shiny(page)
    expect(page.locator("#fb_value_lo")).to_have_value("")
    expect(page.locator("#fb_value_hi")).to_have_value("")
    assert page.locator("#fb_value").count() == 0, "the one-value box is gone: another kind of box is mounted"
    assert "value" not in _rows(page), "nothing is added until the user presses + Add row"
    # and back: the one-value box is a new box at the column's smallest value, visibly
    page.locator("#fb_op").select_option("ge")
    page.wait_for_selector("#fb_value", timeout=15_000)
    _wait_shiny(page)
    expect(page.locator("#fb_value")).to_have_value("1")
    assert "value" not in _rows(page)
