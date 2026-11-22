"""Every column type has the control that fits it in the HOME filter dialog, in the browser (FILTER-PICKERS-1, Eve 2026-11-15, D9).

A staged recipe in a temporary folder of `tmpAI/` (no tracked file is touched): one table of four samples with a column of every
type: `day` (Date), `flag` (Boolean), `clock` (Time), `start` (Datetime), and `span` (Duration, made by a tier1 step from
`stop - start`), one row with no value anywhere. In the qa app features:

- the type is said next to the column and the operators are the ones of the type (date and date and time: the list and every
  comparison; time and duration: the comparisons, no list; true/false: equal and not equal; text: the list, no greater or less);
- a date is picked in a date picker (one for each comparison, two for `between`, with its four ends), the boxes start at the
  smallest and largest value of the column;
- true/false is two choices; a time is three boxes (hour, minute, second); a duration is a number and a unit; a date and time
  is a date picker and three boxes; each stages a row whose text says the value, and Apply leaves the rows the value means;
- an empty control is a plain message, not a silent no-op.

Waits are on the app's state (the row summary, the option list), never on time.

Run: PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_filter_pickers.py -q
"""
import socket
import subprocess
import time
import urllib.request
from pathlib import Path

import pytest
import yaml
from playwright.sync_api import Page, expect

from app.tests.subprocess_env import app_command, app_env
from app.tests.test_shiny_smoke import _open_app, _open_filters_panel, _wait_for_fb_col_option, _wait_shiny
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema

REPO = Path(__file__).resolve().parents[2]
WORK = REPO / "tmpAI" / "browser_filter_pickers"
ROWS = 4   # s1, s2, s3 and s4 (no value in any typed column)
TSV = (
    "sample_id\tday\tflag\tclock\tstart\tstop\n"
    "s1\t2020-01-01\ttrue\t09:00:00\t2020-01-01 09:00:00\t2020-01-01 09:01:00\n"
    "s2\t2020-01-02\tfalse\t10:30:00\t2020-01-02 10:30:00\t2020-01-02 12:00:00\n"
    "s3\t2020-01-03\ttrue\t10:30:00.250000\t2020-01-03 00:00:00.250000\t2020-01-03 02:00:00.250000\n"
    "s4\t\t\t\t\t\n"
)
ALL = ["in", "not_in", "eq", "ne", "gt", "ge", "lt", "le", "between"]
COMPARE = ["eq", "ne", "gt", "ge", "lt", "le", "between"]


def _free_port() -> int:
    with socket.socket() as s:
        s.bind(("127.0.0.1", 0))
        return s.getsockname()[1]


@pytest.fixture(scope="module")
def typed_app():
    WORK.mkdir(parents=True, exist_ok=True)
    (WORK / "typed.tsv").write_text(TSV, encoding="utf-8")
    schema = minimal_schema(
        "./tmpAI/browser_filter_pickers/typed.tsv",
        {"sample_id": "String", "day": "Date", "flag": "Boolean", "clock": "Time", "start": "Datetime", "stop": "Datetime"},
        entity_key="sample_id", null_values=[""],
        tier1=[{"action": "polars_with_columns", "named_exprs": {"span": "pl.col('stop') - pl.col('start')"}}],
    )
    schema["description"] = "One row per sample, a column of every type."
    plot = minimal_plot("typed", {"x": "sample_id"}, [{"name": "geom_bar", "params": {}}], label="Samples")
    plot["description"] = "One bar per sample."
    recipe = minimal_recipe("typed", label="Typed", schemas={"typed": schema}, plots={"typed_plot": plot})
    recipe["info"]["description"] = "A table with a column of every type, for a browser test."
    group = recipe["analysis_groups"].pop("main")
    group.update({"ui_label": "Typed", "description": "The one group."})
    recipe["analysis_groups"] = {"typed_group": group}
    recipes = WORK / "recipes"
    recipes.mkdir(exist_ok=True)
    (recipes / "typed.yaml").write_text(yaml.safe_dump(recipe, sort_keys=False), encoding="utf-8")
    locations = {"raw_data": str(WORK), "data_analysis_recipes": str(recipes), "cache": str(WORK / "cache"),
                 "user_data": str(WORK / "user"), "gallery": str(REPO / "assets" / "gallery_data")}
    for key in ("cache", "user_data"):
        Path(locations[key]).mkdir(exist_ok=True)
    deployment = WORK / "deployment.yaml"
    deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "typed pickers", "locations": locations,
                                          "default_data_analysis_recipe": "typed", "default_app_features": "qa"}), encoding="utf-8")
    port = _free_port()
    env = app_env(SPARMVET_APP_FEATURES="qa", SPARMVET_DEPLOYMENT=str(deployment))
    with open(WORK / "server.log", "w") as out:
        proc = subprocess.Popen(app_command(port),
                                cwd=REPO, env=env, stdout=out, stderr=subprocess.STDOUT)
        try:
            url = f"http://127.0.0.1:{port}/"
            for _ in range(90):
                try:
                    urllib.request.urlopen(url, timeout=2)
                    break
                except Exception:
                    time.sleep(1)
            yield url
        finally:
            proc.terminate()
            proc.wait(timeout=20)


def _expect_rows(page: Page, n: int) -> None:
    """The data table holds n rows: a retrying assertion on the app's state (its summary says "of n" when it pages, else the rows are counted)."""
    page.wait_for_function(
        """(n) => {
            const grid = document.querySelector('#home_data_preview');
            if (!grid) return false;
            const summary = grid.querySelector('.shiny-data-grid-summary');
            if (summary) return summary.innerText.includes('of ' + n);
            return grid.querySelectorAll('tbody tr').length === n;
        }""", arg=n, timeout=20_000)


def _open_dialog(page: Page, url: str, column: str) -> None:
    _open_app(page, url)
    page.locator(".nav-link:has-text('Typed')").first.click()
    _wait_shiny(page)
    _open_filters_panel(page)
    _wait_for_fb_col_option(page, column)
    page.locator("#fb_col").select_option(column)
    _wait_shiny(page)
    _expect_rows(page, ROWS)


def _ops(page: Page) -> list:
    return page.locator("#fb_op option").evaluate_all("els => els.map(e => e.value)")


def _choose_op(page: Page, op: str) -> None:
    page.locator("#fb_op").select_option(op)
    _wait_shiny(page)


def _set(page: Page, selector: str, value) -> None:
    box = page.locator(selector)
    box.fill(str(value))
    box.press("Tab")
    _wait_shiny(page)


def _set_date(page: Page, selector: str, value: str) -> None:
    """Type a date into a date picker the way a user does: type it, Enter (the picker reads it), then leave the box."""
    box = page.locator(selector)
    box.click()
    box.press("Control+a")
    box.press_sequentially(value)
    box.press("Enter")
    box.press("Tab")
    _wait_shiny(page)
    expect(box).to_have_value(value)


def _add_and_apply(page: Page, staged_text: str, rows: int) -> None:
    """Stage the row, check what it says, apply it, check the rows, remove it (the table is whole again)."""
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text(staged_text, timeout=10_000)
    page.locator("#filter_apply").click()
    _wait_shiny(page)
    _expect_rows(page, rows)
    page.locator("#filter_remove_0").click()
    _wait_shiny(page)
    _expect_rows(page, ROWS)


def _closed(page: Page, value: str) -> None:
    page.locator(f"input[name=fb_closed][value={value}]").check()
    _wait_shiny(page)


def test_a_date_has_a_date_picker_for_each_comparison_and_two_for_between(page: Page, typed_app):
    _open_dialog(page, typed_app, "day")
    expect(page.locator("#fb_col_type")).to_have_text("day holds dates (Date).", timeout=10_000)
    assert _ops(page) == ALL
    # the list keeps the dates present (a list, not a picker)
    _choose_op(page, "in")
    expect(page.locator("#fb_value-selectized")).to_be_visible(timeout=5_000)
    # a comparison: a date picker that starts at the smallest date of the column
    _choose_op(page, "gt")
    expect(page.locator("#fb_value input")).to_have_value("2020-01-01", timeout=5_000)
    assert page.locator("#fb_value-selectized").count() == 0
    _set_date(page, "#fb_value input", "2020-01-02")
    _add_and_apply(page, "day > 2020-01-02", 1)                  # s3 (the tick of "greater" removes the row with no value)
    _choose_op(page, "eq")
    _set_date(page, "#fb_value input", "2020-01-02")
    _add_and_apply(page, "day = 2020-01-02", 1)                  # s2
    # between: two pickers that start EMPTY (D-0504: no end is a value the user did not choose), the four ends
    _choose_op(page, "between")
    expect(page.locator("#fb_value_lo input")).to_have_value("", timeout=5_000)
    expect(page.locator("#fb_value_hi input")).to_have_value("", timeout=5_000)
    _set_date(page, "#fb_value_lo input", "2020-01-01")
    _set_date(page, "#fb_value_hi input", "2020-01-03")
    labels = page.locator("input[name=fb_closed]").evaluate_all("els => els.map(e => e.value)")
    assert labels == ["both", "left", "right", "none"]
    for closed, rows in (("both", 3), ("left", 2), ("right", 2), ("none", 1)):
        _closed(page, closed)
        page.locator("#filter_add_row").click()
        page.locator("#filter_apply").click()
        _wait_shiny(page)
        _expect_rows(page, rows)
        page.locator("#filter_remove_0").click()
        _wait_shiny(page)
        _expect_rows(page, ROWS)


def test_true_false_is_two_choices_equal_and_not_equal(page: Page, typed_app):
    _open_dialog(page, typed_app, "flag")
    expect(page.locator("#fb_col_type")).to_have_text("flag holds true or false (Boolean).", timeout=10_000)
    assert _ops(page) == ["eq", "ne"]
    choices = page.locator("input[name=fb_value]").evaluate_all("els => els.map(e => e.value)")
    assert choices == ["true", "false"]
    page.locator("input[name=fb_value][value=false]").check()
    _wait_shiny(page)
    _add_and_apply(page, "flag = False", 1)                      # s2
    _choose_op(page, "ne")
    page.locator("input[name=fb_value][value=false]").check()
    _wait_shiny(page)
    _add_and_apply(page, "flag ≠ False", 3)                      # s1, s3, and the row with no value (the tick of "not equal" keeps it)


def test_a_time_is_three_boxes_that_start_at_the_exact_smallest_and_largest_time(page: Page, typed_app):
    _open_dialog(page, typed_app, "clock")
    expect(page.locator("#fb_col_type")).to_have_text("clock holds times of day (Time).", timeout=10_000)
    assert _ops(page) == COMPARE
    _choose_op(page, "gt")
    for box, value in (("#fb_h", "9"), ("#fb_min", "0"), ("#fb_s", "0")):
        expect(page.locator(box)).to_have_value(value, timeout=5_000)
    _set(page, "#fb_h", 10)
    _set(page, "#fb_min", 30)
    _add_and_apply(page, "clock > 10:30:00", 1)                  # s3 (10:30:00.25)
    _choose_op(page, "eq")
    _set(page, "#fb_h", 10)
    _set(page, "#fb_min", 30)
    _set(page, "#fb_s", 0.25)
    _add_and_apply(page, "clock = 10:30:00.25", 1)               # s3 only: the digits are kept
    _choose_op(page, "between")
    for box in ("#fb_h_lo", "#fb_min_lo", "#fb_s_lo", "#fb_h_hi", "#fb_min_hi", "#fb_s_hi"):
        expect(page.locator(box)).to_have_value("", timeout=5_000)   # D-0504: the ends start empty
    for box, value in (("#fb_h_lo", 9), ("#fb_min_lo", 0), ("#fb_s_lo", 0), ("#fb_h_hi", 10), ("#fb_min_hi", 30), ("#fb_s_hi", 0.25)):
        _set(page, box, value)   # the smallest and the largest time of the column, typed by the user
    _add_and_apply(page, "clock between 09:00:00 and 10:30:00.25", 3)   # s1, s2, s3: every row with a value


def test_a_duration_is_a_number_and_a_unit(page: Page, typed_app):
    _open_dialog(page, typed_app, "span")
    expect(page.locator("#fb_col_type")).to_contain_text("span holds durations", timeout=10_000)
    assert _ops(page) == COMPARE
    _choose_op(page, "gt")
    expect(page.locator("#fb_value")).to_have_value("1", timeout=5_000)     # the shortest, 1 min
    expect(page.locator("#fb_unit")).to_have_value("min")
    _set(page, "#fb_value", 1.5)
    page.locator("#fb_unit").select_option("h")
    _wait_shiny(page)
    _add_and_apply(page, "span > 1.5 h", 1)                      # s3 (2 h)
    _choose_op(page, "between")
    expect(page.locator("#fb_value_lo")).to_have_value("", timeout=5_000)   # D-0504: the ends start empty
    expect(page.locator("#fb_value_hi")).to_have_value("")
    _set(page, "#fb_value_lo", 1)
    page.locator("#fb_unit_lo").select_option("min")
    _set(page, "#fb_value_hi", 2)
    page.locator("#fb_unit_hi").select_option("h")
    _wait_shiny(page)
    _add_and_apply(page, "span between 1 min and 2 h", 3)


def test_a_date_and_time_is_a_date_picker_and_three_boxes_and_keeps_the_exact_list(page: Page, typed_app):
    _open_dialog(page, typed_app, "start")
    expect(page.locator("#fb_col_type")).to_contain_text("start holds dates and times", timeout=10_000)
    assert _ops(page) == ALL
    _choose_op(page, "in")
    expect(page.locator("#fb_value-selectized")).to_be_visible(timeout=5_000)
    _choose_op(page, "ge")
    expect(page.locator("#fb_value input")).to_have_value("2020-01-01", timeout=5_000)
    expect(page.locator("#filter_value_ui")).to_contain_text("time zone")  # how the value is read is said
    _set_date(page, "#fb_value input", "2020-01-02")
    _set(page, "#fb_h", 10)
    _set(page, "#fb_min", 30)
    _add_and_apply(page, "start ≥ 2020-01-02 10:30:00", 2)       # s2 and s3


def test_text_keeps_the_list_and_has_no_greater_or_less(page: Page, typed_app):
    _open_dialog(page, typed_app, "sample_id")
    assert _ops(page) == ["in", "not_in", "eq", "ne"]


def test_an_empty_box_says_so_and_adds_no_filter(page: Page, typed_app):
    """A box of a time that is empty is a plain message, never a silent no-op (a date picker cannot stay empty: it falls back to a date,
    and the staged line says which)."""
    _open_dialog(page, typed_app, "clock")
    _choose_op(page, "gt")
    _set(page, "#fb_min", "")
    page.locator("#filter_add_row").click()
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The time is not complete", timeout=10_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text("Suggestion:")
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet")


def _clear_date(page: Page, selector: str, key: str) -> None:
    """Empty a date box the way a user does, then leave it with `key`: Enter (the picker used to fill in today) or Tab (blur)."""
    box = page.locator(selector)
    box.click()
    box.press("Control+a")
    box.press("Delete")
    box.press(key)
    if key == "Enter":
        box.press("Tab")
    _wait_shiny(page)


@pytest.mark.parametrize("key", ["Enter", "Tab"])
@pytest.mark.parametrize("op, selector", [("gt", "#fb_value input"), ("between", "#fb_value_lo input"), ("between", "#fb_value_hi input")])
def test_a_cleared_date_box_stays_empty_stages_nothing_and_says_what_to_do(page: Page, typed_app, op, selector, key):
    """Eve 2026-11-15: a filter that lacks its value is refused, never filled in. The datepicker took Enter in an empty box as "today"."""
    _open_dialog(page, typed_app, "day")
    _choose_op(page, op)
    _clear_date(page, selector, key)
    expect(page.locator(selector)).to_have_value("")                     # no date was put in its place
    page.locator("#filter_add_row").click()
    if op == "between":   # D-0504: an empty end of between is the one line about both ends, near the boxes
        expect(page.locator("#fb_add_reason")).to_contain_text("Give both values for 'between'", timeout=10_000)
    else:
        expect(page.locator("#shiny-notification-panel")).to_contain_text("No date is chosen, so no filter is added", timeout=10_000)
        expect(page.locator("#shiny-notification-panel")).to_contain_text("Suggestion: choose a date")
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet")


def test_the_date_of_a_date_and_time_cleared_is_refused_too(page: Page, typed_app):
    _open_dialog(page, typed_app, "start")
    _choose_op(page, "ge")
    _clear_date(page, "#fb_value input", "Enter")
    expect(page.locator("#fb_value input")).to_have_value("")
    page.locator("#filter_add_row").click()
    expect(page.locator("#shiny-notification-panel")).to_contain_text("No date is chosen", timeout=10_000)
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet")


def _type_date(page: Page, selector: str, text: str, key: str) -> None:
    """Type text into a date box as a user does (no repair by the test), then leave it with `key`: Enter or Tab."""
    box = page.locator(selector)
    box.click()
    box.press("Control+a")
    box.press("Delete")
    box.press_sequentially(text)
    box.press(key)
    if key == "Enter":
        box.press("Tab")
    _wait_shiny(page)


SUGGESTION = "Suggestion: write the date as year-month-day, for example 2023-02-28, or pick it in the calendar"
BAD_TEXTS = ["2023-0", "abc", "20220305", "2023-02-30", "03/05/2022"]


@pytest.mark.parametrize("key", ["Tab", "Enter"])
@pytest.mark.parametrize("column, op", [("day", "gt"), ("start", "ge")])
@pytest.mark.parametrize("text", BAD_TEXTS)
def test_a_date_that_is_not_typed_in_full_is_refused_and_the_box_keeps_the_text(page: Page, typed_app, text, column, op, key):
    """The date WIDGET used to replace the text (today, 2023-03-02, "8-11-11") and a filter was staged: nothing is staged now, the message
    says what happened, and the box still holds what the user typed so that it can be corrected."""
    _open_dialog(page, typed_app, column)
    _choose_op(page, op)
    _type_date(page, "#fb_value input", text, key)
    expect(page.locator("#fb_value input")).to_have_value(text)
    page.locator("#filter_add_row").click()
    expect(page.locator("#shiny-notification-panel")).to_contain_text("no filter is added", timeout=10_000)
    expect(page.locator("#shiny-notification-panel")).to_contain_text(SUGGESTION)
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet")


@pytest.mark.parametrize("key", ["Tab", "Enter"])
@pytest.mark.parametrize("box", ["#fb_value_lo input", "#fb_value_hi input"])
def test_each_box_of_between_is_checked_the_same_way(page: Page, typed_app, box, key):
    _open_dialog(page, typed_app, "day")
    _choose_op(page, "between")
    _type_date(page, box, "2023-02-30", key)
    page.locator("#filter_add_row").click()
    expect(page.locator("#shiny-notification-panel")).to_contain_text("The date 2023-02-30 does not exist", timeout=10_000)
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet")


@pytest.mark.parametrize("key", ["Tab", "Enter"])
@pytest.mark.parametrize("column, op, staged", [("day", "gt", "day > 2020-01-02"), ("start", "ge", "start ≥ 2020-01-02 09:00:00")])
def test_a_date_typed_with_one_digit_month_and_day_is_accepted_and_the_staged_line_shows_it_in_full(page: Page, typed_app, column, op, staged, key):
    """"2020-1-2" is unambiguous: it is accepted, and the staged line says 2020-01-02 (nothing is hidden)."""
    _open_dialog(page, typed_app, column)
    _choose_op(page, op)
    _type_date(page, "#fb_value input", "2020-1-2", key)
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text(staged, timeout=10_000)


def test_a_date_picked_in_the_calendar_is_staged_as_picked(page: Page, typed_app):
    _open_dialog(page, typed_app, "day")
    _choose_op(page, "gt")
    page.locator("#fb_value input").click()
    page.locator(".datepicker-days td.day:not(.old):not(.new)", has_text="15").first.click()   # the 15th of the month shown (January 2020)
    _wait_shiny(page)
    expect(page.locator("#fb_value input")).to_have_value("2020-01-15")
    page.locator("#filter_add_row").click()
    expect(page.locator("#filter_rows_ui")).to_contain_text("day > 2020-01-15", timeout=10_000)


@pytest.mark.parametrize("column", ["day", "start", "clock", "span"])
def test_between_on_every_kind_adds_nothing_until_both_ends_are_given(page: Page, typed_app, column):
    """D-0504: the rule is on the operator; a date, a date and time, a time of day and a duration give the one line and no row, with the ends empty."""
    _open_dialog(page, typed_app, column)
    _choose_op(page, "between")
    page.locator("#filter_add_row").click()
    expect(page.locator("#fb_add_reason")).to_contain_text("Give both values for 'between'", timeout=10_000)
    expect(page.locator("#filter_rows_ui")).to_contain_text("No filters yet")
