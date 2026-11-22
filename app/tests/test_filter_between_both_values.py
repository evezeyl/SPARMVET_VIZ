"""HOME Filters: a row with the operator "between" is not added until BOTH ends hold a value the user gave (D-0504, D-0503, D-0050).

# @deps
# consumes: app/modules/t3_audit_engine.py (between_ends, dialog_value, BetweenIncomplete, EmptyBox, BETWEEN_INCOMPLETE_LINE), app/handlers/filter_and_audit_handlers.py (_filter_add_row, filter_add_reason_ui), app/tests/test_shiny_plot_errors.py (staged_app), app/tests/browser_view.py
# doc: .claude/rules/ui_implementation_contract.md#8
# @end_deps

Before: the two boxes of "between" started at the column's smallest and largest value, so "+ Add" with no typing added a row with
values the user never chose; a missing end of a number box was a silent no-op. Now the boxes start empty and an empty end is refused with a line.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_filter_between_both_values.py -q
"""
import datetime

import polars as pl
import pytest
from playwright.sync_api import Page, expect

from app.modules.t3_audit_engine import (
    BETWEEN_INCOMPLETE_LINE, BetweenIncomplete, EmptyBox, between_ends, compose_date, compose_duration, compose_time, dialog_value,
)
from app.tests.browser_view import set_mode, set_view
from app.tests.test_shiny_plot_errors import BAD, _open_home, _show_plot, staged_app  # noqa: F401  (staged_app is a fixture)
from app.tests.test_shiny_smoke import _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from app.tests.test_shiny_step_order import _press
from utils.filter_values import FilterValueError

LF = pl.LazyFrame({"value": [1, 2, 3, 4, 5]})


# ---- headless: the pure rule ------------------------------------------------------------------------------------------------------

def test_both_ends_given_are_kept_as_given():
    assert between_ends(lambda: 3, lambda: 9) == (3, 9)


def test_zero_is_a_value_the_user_gave():
    assert between_ends(lambda: 0, lambda: 0) == (0, 0)


@pytest.mark.parametrize("low, high", [(None, 9), (3, None), (None, None)])
def test_a_missing_end_is_refused_with_the_line(low, high):
    with pytest.raises(BetweenIncomplete) as err:
        between_ends(lambda: low, lambda: high)
    assert str(err.value) == BETWEEN_INCOMPLETE_LINE and "both" in BETWEEN_INCOMPLETE_LINE


def test_an_empty_box_of_a_date_a_time_or_a_duration_counts_as_a_missing_end():
    for empty in (lambda: compose_date(None), lambda: compose_time(None, 0, 0), lambda: compose_duration(None, "s")):
        with pytest.raises(EmptyBox):
            empty()
        with pytest.raises(BetweenIncomplete):
            between_ends(empty, lambda: 1)


def test_an_end_that_is_wrong_is_reported_before_the_missing_one():
    """The user fixes the value that is wrong; the line about the empty box would hide it."""
    def wrong():
        raise FilterValueError("The date 2023-02-30 does not exist", "write a real date")
    with pytest.raises(FilterValueError) as err:
        between_ends(wrong, lambda: None)
    assert not isinstance(err.value, BetweenIncomplete) and "does not exist" in str(err.value)


@pytest.mark.parametrize("low, high", [(None, 5), (2, None), (None, None)])
def test_dialog_value_refuses_a_number_between_with_a_missing_end(low, high):
    with pytest.raises(BetweenIncomplete):
        dialog_value(LF, "value", pl.Int64, False, "between", low=low, high=high)


def test_dialog_value_adds_exactly_the_typed_values_and_puts_them_in_order():
    assert dialog_value(LF, "value", pl.Int64, False, "between", low=2, high=4) == ("between", [2, 4], "both")
    assert dialog_value(LF, "value", pl.Int64, False, "between", low=4, high=2)[1] == [2, 4]   # reported to the owner: the order is put right, no line


def test_a_date_between_with_an_empty_end_is_refused():
    lf = pl.LazyFrame({"d": [datetime.date(2020, 1, 1)]})
    with pytest.raises(BetweenIncomplete):
        dialog_value(lf, "d", pl.Date, False, "between", low=datetime.date(2020, 1, 1), high=None)


def test_another_operator_is_not_changed():
    assert dialog_value(LF, "value", pl.Int64, False, "ge", operand=3) == ("ge", 3, "both")
    assert dialog_value(LF, "value", pl.Int64, False, "ge", operand=None) is None   # as before: the one-value number box is not a "between"


# ---- browser: the user's acts ------------------------------------------------------------------------------------------------------

def _open_the_filter_form(page: Page, staged_app: str) -> None:
    _open_home(page, staged_app)
    _show_plot(page, BAD)
    _open_filters_panel(page)
    set_mode(page, "audit")
    set_view(page, "T3")
    _wait_for_fb_col_option(page, "value")
    page.locator("#fb_col").select_option("value")
    _wait_shiny(page)


def _between(page: Page) -> None:
    page.locator("#fb_op").select_option("between")
    page.wait_for_selector("#fb_value_lo", timeout=15_000)
    _wait_shiny(page)


def _rows(page: Page) -> str:
    return page.locator("#filter_rows_ui").inner_text()


def _add(page: Page) -> None:
    _press(page, "#filter_add_row")
    _wait_shiny(page)


def _no_row_and_line(page: Page) -> None:
    assert "between" not in _rows(page) and "≤" not in _rows(page), "no row was added"
    expect(page.locator("#fb_add_reason")).to_contain_text("Give both values for 'between'", timeout=10_000)


def test_between_boxes_start_empty(page: Page, staged_app):
    _open_the_filter_form(page, staged_app)
    _between(page)
    expect(page.locator("#fb_value_lo")).to_have_value("")
    expect(page.locator("#fb_value_hi")).to_have_value("")


def test_add_at_once_adds_nothing_and_says_why(page: Page, staged_app):
    _open_the_filter_form(page, staged_app)
    _between(page)
    _add(page)
    _no_row_and_line(page)


def test_only_the_lower_value_adds_nothing(page: Page, staged_app):
    _open_the_filter_form(page, staged_app)
    _between(page)
    page.locator("#fb_value_lo").fill("2")
    page.locator("#fb_value_lo").press("Tab")
    _wait_shiny(page)
    _add(page)
    _no_row_and_line(page)
    expect(page.locator("#fb_value_lo")).to_have_value("2")   # showing the line did not lose what was typed (section 14, R4)


def test_both_values_add_the_row_with_the_typed_values(page: Page, staged_app):
    _open_the_filter_form(page, staged_app)
    _between(page)
    _add(page)   # first refused: the line shows, then it goes when the row is added
    page.locator("#fb_value_lo").fill("2")
    page.locator("#fb_value_hi").fill("4")
    page.locator("#fb_value_hi").press("Tab")
    _wait_shiny(page)
    _add(page)
    expect(page.locator("#filter_rows_ui")).to_contain_text("between 2 and 4", timeout=10_000)
    expect(page.locator("#fb_add_reason")).not_to_contain_text("Give both values")


def test_her_case_one_value_then_between_then_add_adds_nothing(page: Page, staged_app):
    """Choose >=, type a number, switch to between, add at once: before the fix a row with the default ends was added."""
    _open_the_filter_form(page, staged_app)
    page.locator("#fb_op").select_option("ge")
    page.locator("#fb_value").fill("3")
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    _between(page)
    _add(page)
    _no_row_and_line(page)


def test_another_operator_still_adds_its_row(page: Page, staged_app):
    _open_the_filter_form(page, staged_app)
    page.locator("#fb_op").select_option("ge")
    page.locator("#fb_value").fill("3")
    page.locator("#fb_value").press("Tab")
    _wait_shiny(page)
    _add(page)
    expect(page.locator("#filter_rows_ui")).to_contain_text("value ≥ 3", timeout=10_000)
