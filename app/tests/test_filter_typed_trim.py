"""HOME filter and audit dialogs: leading and trailing spaces of what the user TYPES are removed before it is stored or compared (D-0626).

# @deps
# consumes: app/modules/t3_audit_engine.py (trim_typed, dialog_value, typed_operand, staged_filter_row, audit_params_from_row, _apply_filter_rows, value_choices, BetweenIncomplete)
# doc: .claude/rules/ui_implementation_contract.md#8
# @end_deps

What is trimmed: a typed text, a typed number or date text, each end of a `between`, each item of a typed list. Inner spaces are never touched.
What is NOT trimmed: a value PICKED from the list of the column's own values (a value of the data may itself hold a leading space; the filter must find it).
PROVISIONAL (an agent's choice, listed in the report): the user is not told that something was trimmed; a typed value that is only spaces is treated as no value
and refused like an empty box.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_typed_trim.py -q
"""
import datetime

import polars as pl
import pytest

from app.modules.t3_audit_engine import (
    BetweenIncomplete, _apply_filter_rows, audit_params_from_row, dialog_value, staged_filter_row, trim_typed, typed_operand, value_choices,
)
from utils.filter_values import FilterValueError

LF = pl.LazyFrame({"n": [1, 2, 3, 4, 5], "name": ["abc", " lead", "a  b", "abc", "z"], "d": [datetime.date(2020, 1, i) for i in range(1, 6)]})


def test_trim_typed_text_list_and_untouched_values():
    assert trim_typed("  x  ") == "x" and trim_typed("a  b") == "a  b" and trim_typed("   ") == ""
    assert trim_typed([" a", "b ", " c d "]) == ["a", "b", "c d"]
    assert trim_typed(5) == 5 and trim_typed(None) is None and trim_typed(True) is True and trim_typed(2.5) == 2.5


def test_a_typed_number_with_spaces_gives_the_same_value_and_the_same_rows():
    assert dialog_value(LF, "n", pl.Int64, False, "ge", operand=" 3 ") == dialog_value(LF, "n", pl.Int64, False, "ge", operand="3") == ("ge", 3, "both")
    op, value, closed = dialog_value(LF, "n", pl.Int64, False, "ge", operand=" 3 ")
    rows = _apply_filter_rows(LF, [staged_filter_row("n", op, value, "Int64", False)]).collect()
    assert rows["n"].to_list() == [3, 4, 5]


def test_typed_text_is_stored_trimmed_and_filters_the_same_rows_as_without_the_spaces():
    plain = dialog_value(None, "name", None, False, "eq", text="abc")
    spaced = dialog_value(None, "name", None, False, "eq", text="  abc ")
    assert spaced == plain == ("eq", "abc", "both")
    row = staged_filter_row("name", spaced[0], spaced[1], "Utf8", False)
    assert audit_params_from_row(row)["value"] == "abc", "the stored audit step holds the trimmed value"
    assert _apply_filter_rows(LF, [row]).collect()["name"].to_list() == ["abc", "abc"]
    assert dialog_value(None, "name", None, False, "eq", text=" a  b ")[1] == "a  b", "inner spaces are not touched"


def test_a_value_picked_from_the_list_that_holds_a_space_is_not_changed():
    choices = value_choices(LF, "name")
    assert " lead" in choices.values()
    label = next(k for k, v in choices.items() if v == " lead")
    chosen = dialog_value(LF, "name", pl.String, False, "in", picked=[label])
    assert chosen[1] == [" lead"], "a picked value stays exactly as in the data"
    row = staged_filter_row("name", chosen[0], chosen[1], "String", False)
    assert _apply_filter_rows(LF, [row]).collect()["name"].to_list() == [" lead"]


def test_the_ends_of_between_are_trimmed_and_a_blank_end_is_refused_like_an_empty_box():
    assert dialog_value(LF, "n", pl.Int64, False, "between", low=" 2 ", high=" 4") == ("between", [2, 4], "both")
    with pytest.raises(BetweenIncomplete):
        dialog_value(LF, "n", pl.Int64, False, "between", low="   ", high=4)


def test_a_typed_date_with_spaces_and_a_blank_typed_value_for_a_date():
    assert dialog_value(LF, "d", pl.Date, False, "ge", operand="  2020-01-03 ")[1] == "2020-01-03"
    with pytest.raises(FilterValueError):
        dialog_value(LF, "d", pl.Date, False, "ge", operand="   ")


def test_typed_operand_trims_a_text_and_a_list_of_typed_texts():
    assert typed_operand("  true ", pl.Boolean) is True
    assert typed_operand("  7 ", pl.Int64) == 7
