# engine: python-polars (applies audit filters and drops with Polars casts and expressions)
"""app/modules/t3_audit_engine.py
Pure helpers extracted from home_theater.py (Phase 24-A, ADR-051).

Two-Category Law (ADR-045): this module is a non-Shiny module
(no @render.* / @reactive.* decorators) and may be imported from any
context — handlers, modules, scripts, tests.

Initial scope (24-A): _apply_filter_rows. Future steps will add
extract_t3_filter_rows / extract_t3_drop_columns.
"""

from __future__ import annotations

# @deps
# provides: function:refuse_decimal_for_whole_numbers, function:dialog_value, function:not_offered_line, function:column_types, function:value_choices, function:pick_values, function:number_range, function:typed_operand, function:compose_date, function:compose_time, function:compose_datetime, function:compose_duration, function:column_bounds, function:control_hint, function:readable_duration, function:list_note, constant:LIST_ON_DEMAND_FROM, function:ops_for_column, function:value_widget_for, function:column_type_line, function:closed_phrase, function:between_prose, constant:CLOSED_CHOICES, function:_apply_filter_rows, function:filter_rows_from_nodes, function:staged_filter_row, function:rows_built_on, function:audit_params_from_row, function:inapplicable_filter_rows, function:describe_filter, function:op_choice_label, function:audited_frame, function:audit_steps_in_order, function:dialog_frame, function:dialog_schema_signature, function:stored_key, function:stored_table_identity, function:source_table_identity, function:dialog_rows_signature, function:audit_failures, function:filters_cleared_notice, function:view_key, function:view_change_notice, function:column_is_in_frame, class:AuditStepError
# consumes: polars, app/modules/orchestrator.py (TIER1_KEY_META, TIER2_KEY_META, tier2_path_for), libs/utils/src/utils/errors.py, libs/utils/src/utils/pipeline_error.py, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py
# consumed_by: app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/export_handlers.py, app/tests/test_filter_dialog_values.py, app/tests/test_filter_four_way_pickers.py, app/tests/test_step_order.py, app/tests/test_removed_audit_step_type.py, app/tests/test_audit_error_names_the_plot.py, app/tests/test_filters_cleared_on_recipe_change.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

import datetime
import json
import math
import re
from decimal import Decimal

import polars as pl

from utils import action_names
from app.modules.orchestrator import TIER1_KEY_META, TIER2_KEY_META, tier2_path_for
from app.modules.renamed_keys import FIX_IN_APP, audit_step_defect
from utils.errors import TransformationError
from utils.pipeline_error import PipelineError
from utils.filter_values import (
    UNIT_NS, FilterValueError, duration_ns, filter_condition, kind_of, read_filter_value, type_words, unit_and_zone,
)
from utils.missing_values import keep_missing
from utils.na_choice import default_na, na_of


def column_is_in_frame(frame, column: str) -> bool:
    """True when `column` is a column of `frame`; a frame that is None counts as "cannot say" and gives True.

    WHY: the filter form's column box (`fb_col`) is rebuilt from the table only after the table changed (another recipe or
    plot), so for a moment the dialog texts are asked about the previous table's column. That column is absent from the new
    table by construction, the box is then rebuilt and asks again: the moment is not an error and must not be logged as one.
    A None frame (the table could not be built) stays an error the caller reports.
    """
    if frame is None:
        return True
    return column in frame.lazy().collect_schema().names()


def filters_cleared_notice(n_pending: int, n_applied: int) -> str | None:
    """The one plain notice shown when the open recipe changed and exploration filters were emptied; None when nothing was cleared.

    WHY: a filter is built against one recipe's columns, names and types (ADR-099 point 1, home_preview_filters.md section on
    clearing). Kept on the next recipe it would silently filter a column of the same name, or do nothing for another name.
    """
    if n_pending <= 0 and n_applied <= 0:
        return None
    return (
        "The filters of the previous recipe were removed because the recipe changed "
        "(a filter is built on one recipe's columns). Audited steps are kept."
    )


def view_key(recipe_id, mode: str, data_view: str, source_table, subtab) -> tuple:
    """What the table on screen is made of (D-0311, D-0178): the recipe, the mode (exploration or audit), the data choice (SRC, T1, T2, T3), the
    source table (only meaningful for SRC; None otherwise) and the open plot. An exploration filter is built on this table: when any of them
    changes, the filters are cleared."""
    return (recipe_id, mode, data_view, source_table if data_view == "SRC" else None, subtab)


_VIEW_CAUSES = (
    (1, "you switched to {mode_name} mode ({mode})"),
    (2, "you changed the data you view"),
    (3, "you changed the source table"),
    (4, "you opened another plot (its table can differ)"),
)


def view_change_notice(old: tuple | None, new: tuple, n_pending: int, n_applied: int) -> str | None:
    """The one plain notice shown when the view changed and exploration filters were emptied (D-0311); None when the view did not change,
    when it is the first view, or when nothing was cleared (no notice for nothing).

    A change of recipe keeps the recipe notice (`filters_cleared_notice`). When several things changed at once, the first cause in the order
    recipe, mode, data, source table, plot is named. PROVISIONAL words (the owner reads them).
    """
    if old is None or old == new or (n_pending <= 0 and n_applied <= 0):
        return None
    if old[0] != new[0]:
        return filters_cleared_notice(n_pending, n_applied)
    for index, cause in _VIEW_CAUSES:
        if old[index] != new[index]:
            why = cause.format(mode_name="Audit" if new[1] == "audit" else "Exploration",
                               mode=("Audit mode builds audit steps; exploration filters do not exist there" if new[1] == "audit"
                                     else "a filter belongs to the table it was built on"))
            return (f"The filters were removed because {why}. A filter is built on the table you view, so it is not kept when "
                    "that table changes. Audited steps are kept.")
    return None


def _op_label(op: str) -> str:
    """Symbolic label for a filter operator (used in UI rendering and reports).

    Lives here (not in a UI module) so that both filter_and_audit_handlers and
    export_handlers can share one definition. ADR-045 compliant — pure, no Shiny.
    """
    return {"eq": "=", "ne": "≠", "gt": ">", "ge": "≥",
            "lt": "<", "le": "≤", "in": "∈", "not_in": "∉"}.get(op, op)


# One vocabulary for every place an operator is shown: the operator dropdown, the staged filter
# list, the audit panel (issue #57). symbol = short form, words = what it means.
OP_WORDS = {
    "eq": ("=", "equals"), "ne": ("≠", "not equal"),
    "gt": (">", "greater than"), "ge": ("≥", "greater or equal"),
    "lt": ("<", "less than"), "le": ("≤", "less or equal"),
    "in": ("∈", "any of"), "not_in": ("∉", "none of"),
    "between": ("↔", "between"),
}


def op_choice_label(op: str) -> str:
    """Dropdown text for an operator: symbol plus words, e.g. '≠ not equal'."""
    sym, words = OP_WORDS.get(op, (op, op))
    return f"{sym} {words}"


# What a staged line adds for `between` when the ends are not both included (never silent).
_CLOSED_SUFFIX = {"left": ", lower end included, upper end not", "right": ", upper end included, lower end not", "none": ", ends not included"}


def describe_filter(column: str, op: str, value, na: str | None = None, closed: str | None = None) -> str:
    """One-line text of a filter row. A one-value set reads as equality ('sequence_type = 101'),
    several values read 'any of' / 'none of' (issue #57). With `na` ("keep" or "remove") the line ends with what
    happens to the rows with no value in the column (NA-RULE-63). an end that is not included in a `between` is said, never silent."""
    text = _describe_condition(column, op, value)
    if op == "between" and closed in _CLOSED_SUFFIX:
        text += _CLOSED_SUFFIX[closed]
    if na is None:
        return text
    return f"{text} ({na_phrase(na)})"


def na_phrase(na: str) -> str:
    """'rows with no value kept' / 'rows with no value removed': the choice `na` in a few words."""
    return "rows with no value kept" if na == "keep" else "rows with no value removed"


def _describe_condition(column: str, op: str, value) -> str:
    vals = value if isinstance(value, (list, tuple)) else None
    if vals is not None and len(vals) == 1:
        op, vals = {"in": "eq", "not_in": "ne"}.get(op, op), None
        value = value[0]
    if op == "between" and isinstance(value, (list, tuple)) and len(value) == 2:
        return f"{column} between {value[0]} and {value[1]}"
    sym, words = OP_WORDS.get(op, (op, op))
    if vals is not None:
        return f"{column} {words} {', '.join(str(v) for v in vals)}"
    return f"{column} {sym} {value}"


# -- the pure side of the HOME filter dialog (ADR-104 points 4, 7 and 8) ---------------------------------------------

# The four ends of `between`, as the dialog shows them (the words of the choice, in the order of the radio).
CLOSED_CHOICES = {
    "both": "both ends included (min ≤ value ≤ max)",
    "left": "min included, max not (min ≤ value < max)",
    "right": "max included, min not (min < value ≤ max)",
    "none": "neither end included (min < value < max)",
}
_CLOSED_PHRASE = {
    "both": "both ends included", "left": "the lower end included, the upper end not",
    "right": "the upper end included, the lower end not", "none": "neither end included",
}


def closed_phrase(closed: str) -> str:
    """The ends of a `between` in words, for a report: 'both ends included', 'neither end included', ..."""
    return _CLOSED_PHRASE[closed]


def between_prose(value, closed: str) -> str:
    """The report sentence of a `between`: 'between "89" and "91", both ends included'."""
    return f'between "{value[0]}" and "{value[1]}", {closed_phrase(closed)}'


def column_types(lf) -> dict:
    """Column name -> dtype, from the schema of the table (not from a sample of rows)."""
    schema = lf.collect_schema()
    return {name: schema[name] for name in schema.names()}


def column_type_line(column: str, dtype) -> str:
    """What the filter dialog shows next to the column: 'Year holds whole numbers (Int64).'"""
    return f"{column} holds {type_words(dtype)} ({dtype})."


def value_choices(lf, column: str) -> dict:
    """The values of the whole column as the dialog lists them: {text shown: real value}, sorted, no missing value.

    The real value is a number for a number column, True or False for a true/false column, text for the rest. A date or a date and time is
    kept as its text (year-month-day, hour:minute:second) (a session file holds no date object; the export types it from the dtype). NaN is not
    listed: it is counted on its own and treated by its own steps (ADR-103).
    """
    kind = kind_of(column_types(lf).get(column))
    if kind == "datetime":
        # The text Polars writes for the value: every digit of the column's unit (nanoseconds too) and its offset; the table,
        # the plot and the export read the same text back in the column's own unit and zone (`filter_condition`).
        texts = lf.select(pl.col(column).drop_nulls().unique().sort().cast(pl.String)).collect()[column].to_list()
        return {t: t for t in texts}
    values = lf.select(pl.col(column).drop_nulls().unique()).collect()[column].to_list()
    if kind == "float":
        values = [float(v) for v in values if not (isinstance(v, float) and math.isnan(v))]
    if kind in ("int", "float", "bool", "date"):
        values = sorted(values)
    choices: dict = {}
    for v in values:
        label = v.isoformat() if kind == "date" else str(v)
        choices[label] = label if kind in ("date", "other", "category") else v
    if kind in ("text", "category", "other"):
        choices = dict(sorted(choices.items()))
    return choices


# PROVISIONAL (L10): above this many values the dialog serves the list on demand while typing (Shiny's server-side selectize shows
# at most 1000 matches of a search); up to it the whole list is in the page, nothing is hidden.
LIST_ON_DEMAND_FROM = 1000


def list_note(count: int) -> str:
    """What the dialog says under a list of values served on demand (PROVISIONAL, L10), or "" when the whole list is shown.

    The list shows at most 1000 matches of what is typed; when more values exist the note says so, so that no value is hidden in silence.
    """
    if count <= LIST_ON_DEMAND_FROM:
        return ""
    return (f"This column has {count:,} different values. The list shows at most {LIST_ON_DEMAND_FROM:,} matches of what you type: "
            "when more values match, type more letters to see the others.")


def pick_values(choices: dict, labels) -> list:
    """The real values of the texts the user picked, in the order picked; a text that is not in the column is reported."""
    missing = [label for label in labels if label not in choices]
    if missing:
        raise FilterValueError(f"The value {missing[0]!r} is not in the column any more",
                               "open the list again and pick the values from it")
    return [choices[label] for label in labels]


def number_range(lf, column: str):
    """(smallest, largest) of the whole column for the number box, or None when it has no number."""
    kind = kind_of(column_types(lf).get(column))
    expr = pl.col(column).drop_nans() if kind == "float" else pl.col(column)
    row = lf.select(expr.min().alias("lo"), expr.max().alias("hi")).collect().row(0)
    return None if row[0] is None else (row[0], row[1])


def refuse_decimal_for_whole_numbers(value, dtype) -> None:
    """HOME filter rule (D-0376): a column of an integer type takes whole numbers only, for every operator and both ends of between.

    Raises the plain `FilterValueError` "This column holds whole numbers (Int64); type a whole number." (PROVISIONAL sentence) when a
    value (or one of a list) is a decimal. "12.0" is read as 12 (PROVISIONAL). Text that is not a number, an empty value and a
    value for another type are not judged here: `read_filter_value` says what is wrong with them. A float column is untouched.
    Called only where a value is ENTERED (`typed_operand`, used by `dialog_value`, and the live line of the form); rows already stored are read by
    `_apply_filter_rows` as before (what a stored decimal on an integer column should do is not decided). The recipe action `modif_filter` keeps its own rule.
    """
    if kind_of(dtype) != "int":
        return
    for item in (value if isinstance(value, (list, tuple)) else [value]):
        if isinstance(item, bool) or item is None:
            continue
        try:
            text = item.strip() if isinstance(item, str) else None
            if text is not None and re.fullmatch(r"[+-]?\d+,\d+", text):
                text = text.replace(",", ".")   # a decimal comma gets the same whole-number line as a decimal point
            number = float(text) if text is not None else float(item)
        except (ValueError, TypeError, OverflowError):
            continue
        if not number.is_integer():
            raise FilterValueError(f"This column holds whole numbers ({dtype}); type a whole number.")


def typed_operand(raw, dtype):
    """What a control gave, in the type of the column, as the panel stores it (ADR-104 point 7).

    A number keeps the type of the column (an integer column an integer, a decimal column a decimal), true or false a real
    boolean, a date its year-month-day text (a session file holds no date object; the export types it from the dtype), a
    date and time, a time of day and a duration their exact text. A value that cannot be read is a `FilterValueError`.
    """
    refuse_decimal_for_whole_numbers(raw, dtype)
    value = read_filter_value(raw, dtype)
    return value.isoformat() if kind_of(dtype) == "date" else value


def ops_for_column(dtype, discrete_axis: bool) -> list:
    """The operators the dialog offers for a column of `dtype` (ADR-104 point 4; Eve 2026-11-15, D9: every type has the control that fits it).

    - A number column offers the comparisons and `between`; when the plot uses it as a discrete axis it also offers the list
      operators first, so that a list can be picked and "> 1998 and < 2003" can still be written (Eve, 2026-11-14).
    - A date and a date and time column offer the list (`in`, `not_in`) and every comparison with a date picker.
    - A time of day and a duration column offer the comparisons (equal, not equal, greater, less, `between`): the values
      are typed in a box, a list of exact times would not help.
    - A true/false column offers equal and not equal: one of two choices; `in` and `not_in` would mean the same.
    - Text and category columns offer the list operators. Greater and less on text is not offered (decided).
    - A column of another type (binary, lists, ...) offers nothing.
    """
    numbers = ["eq", "ne", "gt", "ge", "lt", "le", "between"]
    kind = kind_of(dtype)
    if dtype is not None and kind == "other":
        return []
    if kind in ("int", "float"):
        return ["in", "not_in"] + numbers if discrete_axis else numbers
    if kind == "bool":
        # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 1: true/false offers equal and not equal only.
        return ["eq", "ne"]
    if kind in ("date", "datetime"):
        # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 2: the operators of a date: the list, every comparison and between.
        return ["in", "not_in"] + numbers
    if kind in ("time", "duration"):
        # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 2: a time of day and a duration offer the comparisons and between, no list.
        return numbers
    return ["in", "not_in", "eq", "ne"]


def not_offered_line(column: str, dtype) -> str:
    """What the dialog says for a column whose type has no filter (binary, lists, ...); the suggestion follows it."""
    return f"No filter is offered on {column}: the column holds {dtype}."


def value_widget_for(dtype, discrete_axis: bool, op: str) -> str:
    """The widget of the value, by type and operator.

    "list" (pick values), "number" and "range" (number boxes, `between`), "bool" (two choices), and per type "date",
    "datetime", "time", "duration" (one control) with the suffix "_range" for `between` (two controls).
    """
    kind = kind_of(dtype)
    if kind in ("int", "float"):
        if op == "between":
            return "range"
        if op in ("in", "not_in") or (op in ("eq", "ne") and discrete_axis):
            return "list"
        return "number"
    if kind == "bool":
        return "bool"
    if kind in ("date", "datetime", "time", "duration"):
        if kind in ("date", "datetime") and op in ("in", "not_in"):
            return "list"
        return f"{kind}_range" if op == "between" else kind
    return "list"


def value_box_kind(dtype, discrete_axis: bool, op) -> str | None:
    """The kind of value box the Filters form mounts for a column and the operator chosen; None when the column has no filter.

    WHY (D-0050): the form draws the value box again only when this kind changes, never at a change of operator within one kind
    (a number typed in a box would be thrown away when the server's redraw arrives, and the row added with the box's default). The kind
    depends on the operator's family only (one value, a list, two values), through `value_widget_for`. An operator the column does not
    offer reads as the first one it offers, as the operator select shows it.
    """
    ops = ops_for_column(dtype, discrete_axis) if dtype is not None else ["in", "not_in", "eq", "ne"]
    if not ops:
        return None
    if op not in ops:
        op = ops[0]
    return value_widget_for(dtype, discrete_axis, op) if dtype is not None else "text"


# -- what the boxes of a time, a date and time and a duration write (one place, so that the stored text is the one the rule reads)

def _incomplete(what: str, missing: str):
    return FilterValueError(f"{what} is not complete: {missing}, so no filter is added", "fill every box of it (0 is a value)")


def _plain_number(value) -> str:
    """A number of a box as text without a trailing zero: 90.0 -> "90", 1.50 -> "1.5", 0.1234567 stays exact."""
    text = format(Decimal(repr(value)) if isinstance(value, float) else Decimal(value), "f")
    return text.rstrip("0").rstrip(".") if "." in text else text


def compose_time(hour, minute, second) -> str:
    """The text of the three boxes of a time of day: hour:minute:second, up to nine digits after the second (a Polars Time keeps nanoseconds)."""
    if hour is None or minute is None or second is None:
        raise _incomplete("The time", "the box of the hour, the minutes or the seconds is empty")
    if int(hour) != hour or int(minute) != minute:
        raise FilterValueError("The hour and the minutes must be whole numbers", "write a whole number, for example 10 and 30")
    if not 0 <= hour <= 23 or not 0 <= minute <= 59 or not 0 <= second < 60:
        raise FilterValueError(f"{hour}:{minute}:{second} is not a time of day (the hour is 0 to 23, the minutes 0 to 59, the seconds 0 up to 60)",
                               "write a time of day, for example 10 : 30 : 0")
    whole, _dot, fraction = _plain_number(second).partition(".")
    return f"{int(hour):02d}:{int(minute):02d}:{whole.zfill(2)}" + (f".{fraction}" if fraction else "")


_TYPED_DATE = re.compile(r"^(\d{4})-(\d{1,2})-(\d{1,2})$")
_DATE_SUGGESTION = "write the date as year-month-day, for example 2023-02-28, or pick it in the calendar"


def compose_date(date, typed=None):
    """The date of a date picker, or a plain refusal (Eve, 2026-11-15: a filter that lacks its value is refused, never filled in, and
    nothing is changed without a word).

    `date` is what the picker read. `typed` is the raw text of the box (None for a date picked in the calendar or the default of the box,
    where the widget wrote the text itself). The date that is staged is EXACTLY a date written in full as year-month-day (a month or day
    of one digit is fine) or picked in the calendar: the picker's own reading of free text is not trusted (it fills in today for a
    partial text, rolls 2023-02-30 over to 2023-03-02, reads 03/05/2022 as another date), so the text is read strictly here and must
    equal what the picker read. An empty box is "no date chosen".

    PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 8: the calendar stays for the mouse, the box is typed as year-month-day and read strictly (no keyboard navigation in
    the calendar); "2022-3-5" is accepted (unambiguous) and the staged line shows 2022-03-05.
    """
    if typed is not None:
        text = typed.strip()
        if text == "":
            raise FilterValueError("No date is chosen, so no filter is added", "choose a date")
        m = _TYPED_DATE.match(text)
        if m is None:
            raise FilterValueError(f"The text {text!r} in the date box is not a date written as year-month-day, so no filter is added",
                                   _DATE_SUGGESTION)
        try:
            read = datetime.date(int(m.group(1)), int(m.group(2)), int(m.group(3)))
        except ValueError:
            raise FilterValueError(f"The date {text} does not exist, so no filter is added", _DATE_SUGGESTION) from None
        if date != read:
            raise FilterValueError(f"The date box holds {text!r}, but the calendar read another date ({date}), so no filter is added",
                                   _DATE_SUGGESTION)
        return read
    if date is None or date == "":
        raise FilterValueError("No date is chosen, so no filter is added", "choose a date")
    return date


def compose_datetime(date, hour, minute, second, typed=None) -> str:
    """The text of a date picker and the three boxes of a time: year-month-day hour:minute:second (read in the time zone of the column)."""
    return f"{compose_date(date, typed).isoformat()} {compose_time(hour, minute, second)}"


def compose_duration(number, unit) -> str:
    """The text of the number box and the unit of a duration: "90 min"."""
    if number is None:
        raise _incomplete("The duration", "the number box is empty")
    if unit not in UNIT_NS:
        raise FilterValueError(f"The unit {unit!r} is not a unit of time", f"choose one of {', '.join(UNIT_NS)}")
    return f"{_plain_number(number)} {unit}"


def _order_key(kind: str, value):
    """What puts two bounds of `between` in order: texts of one layout compare as written, a duration by its length."""
    if kind == "duration":
        return duration_ns(value)
    return value


def readable_duration(count_ns: int) -> tuple:
    """A duration in nanoseconds as (number, unit): the largest unit that holds it exactly (5400 s is 90 min, 0 is 0 s)."""
    if count_ns == 0:
        return 0, "s"
    for unit in ("w", "d", "h", "min", "s", "ms", "us", "ns"):
        if count_ns % UNIT_NS[unit] == 0:
            return count_ns // UNIT_NS[unit], unit
    return count_ns, "ns"


_OFFSET = re.compile(r"(Z|[+-]\d{2}:?\d{2})$")


def _time_parts(text: str) -> dict:
    """{"h", "min", "s"} of "hh:mm:ss[.fraction]"; the seconds are a float that is exact to the nine digits of a Time."""
    hour, minute, rest = text.split(":")
    return {"h": int(hour), "min": int(minute), "s": int(rest) if "." not in rest else float(rest)}


def column_bounds(lf, column: str, dtype):
    """The smallest and the largest value of the whole column as the values of the boxes ((low, high) of dicts), or None with no value.

    A date: {"date"}. A date and time: {"date", "h", "min", "s"} in the wall clock of the column's time zone. A time of day:
    {"h", "min", "s"}. A duration: {"number", "unit"}. Exact (nothing is cut), so that "between lowest and highest" keeps every row.
    """
    kind = kind_of(dtype)
    if kind not in ("date", "datetime", "time", "duration"):
        return None
    # PROVISIONAL (FILTER-PICKERS-1, an agent's choice, waits for Eve), point 6: the boxes of a time, a date or a duration start at the smallest and the largest value of the column.
    expr = pl.col(column)
    if kind == "date":
        lo, hi = lf.select(expr.min().alias("lo"), expr.max().alias("hi")).collect().row(0)
        return None if lo is None else ({"date": lo}, {"date": hi})
    if kind == "datetime":
        lo, hi = lf.select(expr.min().cast(pl.String).alias("lo"), expr.max().cast(pl.String).alias("hi")).collect().row(0)
        if lo is None:
            return None
        def parts(text):
            text = _OFFSET.sub("", text)
            return {"date": datetime.date.fromisoformat(text[:10]), **_time_parts(text[11:])}
        return parts(lo), parts(hi)
    lo, hi = lf.select(expr.min().cast(pl.Int64).alias("lo"), expr.max().cast(pl.Int64).alias("hi")).collect().row(0)
    if lo is None:
        return None
    if kind == "time":
        def parts(ns):
            seconds, fraction = divmod(ns, 10**9)
            minutes, second = divmod(seconds, 60)
            hour, minute = divmod(minutes, 60)
            return {"h": hour, "min": minute, "s": second if not fraction else float(Decimal(second) + Decimal(fraction) / 10**9)}
        return parts(lo), parts(hi)
    per = UNIT_NS[unit_and_zone(dtype)[0]]
    def parts(count):
        number, unit = readable_duration(count * per)
        return {"number": number, "unit": unit}
    return parts(lo), parts(hi)


def control_hint(dtype) -> str:
    """One line under the controls of a date and time or a duration, saying how what is typed is read (nothing is silent)."""
    kind = kind_of(dtype)
    if kind == "datetime":
        unit, zone = unit_and_zone(dtype)
        where = f"in the time zone of the column ({zone})" if zone else "as written: the column has no time zone"
        return f"The date and time are read {where}; the column keeps {unit}, a finer value is refused."
    if kind == "duration":
        unit, _zone = unit_and_zone(dtype)
        return f"The column keeps durations in {unit}; a finer value is refused, not cut."
    if kind == "time":
        return "The time is read as hour, minute and second (up to nine digits after the second)."
    return ""


def dialog_value(lf, column: str, dtype, discrete_axis: bool, op: str, *, picked=(), operand=None, low=None, high=None,
                 closed: str = "both", text: str = ""):
    """What "+ Add" writes into the filter row: (operator, real value, ends), or None when nothing is chosen yet.

    The value has the type of the column (ADR-104 point 7): values picked from a list are looked up in the map of the whole
    column; what a control gave (`operand`, or `low` and `high` for `between`, put in order) is typed from the dtype: a number,
    true or false, a date as year-month-day text, a date and time, a time or a duration as exact text (`compose_time`,
    `compose_datetime`, `compose_duration` build that text from the boxes). eq or ne on a list means in or not_in. Without a
    table (`dtype` None) the text is kept as written. Raises FilterValueError when a value cannot be read in the type of the
    column, or when a control of a date, true/false, time or duration is empty (never a silent no-op there).
    """
    if dtype is not None and not ops_for_column(dtype, discrete_axis):
        raise FilterValueError(not_offered_line(column, dtype), "filter another column")
    widget = value_widget_for(dtype, discrete_axis, op) if dtype is not None else "text"
    kind = kind_of(dtype)
    ends = closed if closed in CLOSED_CHOICES else "both"
    if widget == "range" or widget.endswith("_range"):
        if kind == "date":
            compose_date(low), compose_date(high)
        if kind not in ("int", "float") and (low is None or high is None):
            raise FilterValueError(f"No {type_words(dtype)[:-1]} is chosen in one of the two boxes of between, so no filter is added",
                                   "choose both ends")
        if low is None or high is None:
            return None
        low, high = typed_operand(low, dtype), typed_operand(high, dtype)
        swap = _order_key(kind, low) > _order_key(kind, high)
        value = [high, low] if swap else [low, high]
        filter_condition(column, op, value, dtype, ends)   # the rule judges the whole value now: a time that does not exist is refused here, not at Apply
        return op, value, ends
    if widget == "list":
        labels = list(picked or ())
        if not labels:
            return None
        return {"eq": "in", "ne": "not_in"}.get(op, op), pick_values(value_choices(lf, column), labels), "both"
    if widget in ("number", "bool", "date", "datetime", "time", "duration"):
        if kind == "date":
            compose_date(operand)
        if operand is None:
            if widget == "number":
                return None
            raise FilterValueError(f"No value is chosen for {type_words(dtype)}, so no filter is added", "choose it in the box")
        value = typed_operand(operand, dtype)
        filter_condition(column, op, value, dtype)         # the rule judges the whole value now (a time of a zone that has no such time is refused here)
        return op, value, "both"
    text = (text or "").strip()
    return (op, text, "both") if text else None


def inapplicable_filter_rows(lf, filter_rows: list) -> list:
    """Filter rows whose column is absent from lf; they are skipped, not applied (issue #56)."""
    try:
        names = set(lf.collect_schema().names())
    except Exception:
        return []
    return [f for f in filter_rows if f.get("column") is not None and f.get("column") not in names]


def filter_rows_from_nodes(nodes: list) -> list[dict]:
    """The filter rows of the active `filter_row` and `exclusion_row` audit steps, with their `na` choice.

    A step written before the choice existed has no `na` and is carried as "remove", what it always did.
    """
    rows: list[dict] = []
    for n in nodes:
        if not n.get("active", True) or n.get("node_type") not in ("filter_row", "exclusion_row"):
            continue
        p = n.get("params", {})
        if "column" not in p:
            continue
        row = {
            "column": p.get("column"),
            "op": p.get("op", "eq"),
            "value": p.get("value"),
            "dtype": p.get("dtype", "Utf8"),
            "na": na_of(p),
        }
        if row["op"] == "between":
            row["closed"] = p.get("closed", "both")
        rows.append(row)
    return rows


def staged_filter_row(column: str, op: str, value, dtype: str, na_tick: bool | None, closed: str = "both", view: tuple | None = None) -> dict:
    """The filter row the "+ Add" button stages: the tick of the dialog is recorded, never dropped.

    `na_tick` True keeps the rows with no value, False removes them; None (the tick is not mounted) is the default of
    the operator. `closed` is written for `between` only. `view` is the view key the row was built on (`view_key`): the data preview applies
    the row only while the view is that one (`rows_built_on`); a row without it is never applied.
    """
    keep = default_na(op) == "keep" if na_tick is None else bool(na_tick)
    row = {"column": column, "op": op, "value": value, "dtype": dtype, "na": "keep" if keep else "remove"}
    if op == "between":
        row["closed"] = closed
    if view is not None:
        row["view"] = view
    return row


def rows_built_on(rows: list, key: tuple | None) -> list:
    """The exploration filter rows built on the view `key` (D-0311, review F3): the only ones the data preview may apply. A filter built on another
    table (before the clearing effect has run, or kept by a bug) is not applied; a row with no view key is not applied either; no key, no row."""
    return [row for row in rows if key is not None and row.get("view") == key]


def audit_params_from_row(frow: dict) -> dict:
    """The params of the audit step built from a staged row on "Send to Audit": everything the user chose.

    `na` (keep or remove the rows with no value) and, for `between`, `closed` are carried exactly as chosen. A row of an
    older state without `na` is "remove".
    """
    params = {"column": frow.get("column", ""), "op": frow.get("op", "eq"), "value": frow.get("value", ""), "na": na_of(frow)}
    if frow.get("dtype"):
        params["dtype"] = frow["dtype"]
    if params["op"] == "between":
        params["closed"] = frow.get("closed", "both")
    return params


def _apply_filter_rows(lf, filter_rows: list) -> "pl.LazyFrame":
    """
    Apply a list of {column, op, value, dtype, na, closed} dicts to a LazyFrame.

    Type strategy (ADR-104 point 7): a value has the type of its column. The dtype of the column is read from the
    schema of the table each call (the stored 'dtype' of a row can be stale or absent). A value an older row holds as
    text is read as that type; a value that cannot be read stops with a plain `FilterValueError`, it is never guessed.
    The condition itself is `utils.filter_values.filter_condition`, shared with the plot and the recipe action
    (eq or ne with a list mean in or not_in; in and not_in compare typed values).
    """
    try:
        schema = lf.collect_schema()
        actual_dtypes = {name: schema[name] for name in schema.names()}
    except Exception:
        actual_dtypes = {}

    for f in filter_rows:
        col = f.get("column")
        if col is None:
            continue
        # Issue #56: T1 is wide and T2 may be long, so a filter built on one view can name a
        # column the active view does not have. Skip it (see inapplicable_filter_rows) rather than crash.
        if actual_dtypes and col not in actual_dtypes:
            continue
        dtype = actual_dtypes.get(col) or f.get("dtype")
        condition = filter_condition(col, f.get("op", "eq"), f.get("value"), dtype, f.get("closed", "both"))
        # NA-RULE-63: "keep" adds the rows with no value; a row without `na` removes them
        lf = lf.filter(keep_missing(condition, col, na_of(f)))
    return lf


# -- the audited steps of a plot, in one place (PLOT-TABLE-ORDER-1) -------------------------------------------------

class AuditStepError(TransformationError):
    """An audited step that cannot run on the table it meets: its column is not there.

    The message says which step (its number in the plot's list and its reason), the column, the step that removed it
    (when one did) and the fix. It carries a `PipelineError`, so the Alerts panel and the Processing issues table hold the same
    text. The HOME table, the HOME plot and the export show or write it; none of them skips the step.
    """


def _of_plot(plot_id: str | None) -> str:
    return f" of the plot '{plot_id}'" if plot_id else ""


def _step_words(step: dict, plot_id: str | None = None) -> str:
    what = (f"drop column {step['column']}" if step["kind"] == "drop"
            else describe_filter(step["column"], step["row"]["op"], step["row"]["value"], step["row"]["na"],
                                 step["row"].get("closed")))
    reason = f', reason: "{step["reason"]}"' if step["reason"] else ""
    return f"audit step {step['number']}{_of_plot(plot_id)} ({what}{reason})"


def _step_error(step: dict, remover: dict | None, columns: list, plot_id: str | None = None) -> AuditStepError:
    column = step["column"]
    engine = f"step {action_names.DROP if step['kind'] == 'drop' else action_names.FILTER}: column {column!r} is not in the table"
    if remover is not None:
        why = f"The {_step_words(remover, plot_id)} removed it before."
        fix = (f"remove audit step {remover['number']} or audit step {step['number']} from the plot's audit list "
               "(the steps run in the order they were recorded)")
    else:
        why = f"The table has the columns {', '.join(columns)}."
        fix = f"remove audit step {step['number']} from the plot's audit list, or use a column of the table"
    problem = f"The {_step_words(step, plot_id)} cannot run: {engine}. {why}"
    pipeline_error = PipelineError(
        component="T3Audit", problem=problem, location=f"audit step {step['number']}{_of_plot(plot_id)}",
        fix=fix[:1].upper() + fix[1:] + ".", who="analyst", category="t3_apply", surface="audit_panel",
        evidence={"plot": plot_id, "audit_step": step["number"], "column": column,
                  "removed_by_audit_step": remover["number"] if remover else None},
        reference="ui_implementation_contract.md section 12 and 14; PLOT-TABLE-ORDER-1")
    return AuditStepError(f"{problem} Fix: {fix}.", tip=fix[:1].upper() + fix[1:] + ".", pipeline_error=pipeline_error)


def _refused_step_error(node: dict, number: int, defect: str, plot_id: str | None) -> AuditStepError:
    """A step the app cannot apply (unknown or removed type, or missing what it needs): refused, never skipped in silence."""
    reason = f', reason: "{node["reason"]}"' if node.get("reason") else ""
    off = ", switched off" if not node.get("active", True) else ""
    problem = f"The audit step {number}{_of_plot(plot_id)} (id {node.get('id', '?')}{reason}{off}) is refused: {defect}."
    fix = (f"remove audit step {number} with the trash icon of the audit panel, or {FIX_IN_APP}")
    pipeline_error = PipelineError(
        component="T3Audit", problem=problem, location=f"audit step {number}{_of_plot(plot_id)}",
        fix=fix[:1].upper() + fix[1:] + ".", who="analyst", category="t3_apply", surface="audit_panel",
        evidence={"plot": plot_id, "audit_step": number, "step_type": node.get("node_type")}, reference="PLOT-TABLE-ORDER-1")
    return AuditStepError(f"{problem} Fix: {fix}.", tip=fix[:1].upper() + fix[1:] + ".", pipeline_error=pipeline_error)


def audit_steps_in_order(nodes: list, plot_id: str | None = None) -> list[dict]:
    """The data steps of a plot's audit list, in the order they are applied: THE ORDER RULE (one place).

    DECIDED 2026-11-15 (Eve, S2-1): the recorded order, the order of the list ("steps in the order written in the recipe and
    performed in the audit in the same order"). It is also the order the exported recipe is written in
    (`blueprint_arch.t3_translator.translate_plot_steps`). If the rule is ever changed, change this function only; every
    consumer (HOME table, HOME plot, Compare, the results bundle, the check before an export, the filter dialog) reads the
    steps from here.

    A step is `{"number", "kind": "filter" | "drop", "column", "reason", "row"}`; `row` is the filter row (`filter_rows_from_nodes`).
    `number` is the position, counted from 1, among the active steps of the list (a plot style step is not counted: it is
    not a step of the data). A step the app cannot apply (an unknown or removed type, or a step without its column, operator or
    value) raises `AuditStepError`, switched off or not: it is never skipped in silence.
    """
    steps: list[dict] = []
    number = 0      # position among the active data steps: what the messages say
    position = 0    # position among all data steps, switched off or not: what a refusal says
    for node in nodes:
        if node.get("node_type") in ("aesthetic_override", "random_seed"):
            continue
        position += 1
        defect = audit_step_defect(node)
        if defect:
            raise _refused_step_error(node, position, defect, plot_id)
        if not node.get("active", True):
            continue
        number += 1
        kind = node["node_type"]
        params = node.get("params") or {}
        if kind in ("filter_row", "exclusion_row"):
            row = filter_rows_from_nodes([node])[0]
            steps.append({"number": number, "kind": "filter", "column": row["column"], "reason": node.get("reason", ""), "row": row})
        else:
            steps.append({"number": number, "kind": "drop", "column": params["column"], "reason": node.get("reason", ""), "row": None})
    return steps


def audited_frame(lf, nodes: list, plot_id: str | None = None):
    """The audited data of one plot: its audited steps applied to its base frame, in the order of `audit_steps_in_order`.

    The base is the table the plot reads (the stored Tier 2, Tier 1 when the table has no tier2 steps, plus the plot's own tier-3 steps):
    build rule T3 > T2 > T1. The ONE function for HOME's T3 table in Audit mode, HOME's audited plot (also in Compare), the results bundle (`T3_data_<plot>.tsv` and the plot), the check before an
    export and the column list of the filter dialog: they cannot differ. A step whose column is not in the table at that point
    (never there, or removed by an earlier step) raises `AuditStepError`, which names the plot (`plot_id`); it is never skipped.
    Exploration filters are not an argument: they are not audited and are never exported (HOME applies them with
    `_apply_filter_rows` before calling this).
    """
    removed_by: dict[str, dict] = {}
    for step in audit_steps_in_order(nodes, plot_id):
        columns = lf.collect_schema().names()
        if step["column"] not in columns:
            raise _step_error(step, removed_by.get(step["column"]), columns, plot_id)
        if step["kind"] == "drop":
            lf = lf.drop(step["column"])
            removed_by[step["column"]] = step
        else:
            lf = _apply_filter_rows(lf, [step["row"]])
    return lf


def dialog_frame(lf, nodes: list, with_audited_steps: bool, plot_id: str | None = None):
    """The table the filter dialog acts on. In Audit mode on T3 (`with_audited_steps`): the plot's table after its audited steps (a column
    that an earlier step dropped is not offered, a value list holds the rows that are still there). On any other view: the table shown, as
    it is (Source, T1, T2, and T3 in Exploration, where no audited step is on the table). DECIDED 2026-11-15 (Eve, S2-1 (a)); D-0178."""
    return audited_frame(lf, nodes, plot_id) if with_audited_steps else lf


def dialog_schema_signature(types: dict, discrete: set) -> tuple:
    """What the add-row form's column select, type line and operator list are made of: the columns with their types, and the
    columns the plot uses as a discrete axis (it changes the operator list of a number column).

    Two tables with the same signature give the same form, whatever their rows. The form is mounted again only when this
    changes, so a choice the user has just made is not put back by a recompute that changed nothing in it."""
    return (tuple((name, str(dtype)) for name, dtype in types.items()), tuple(sorted(discrete)))


def stored_key(path, meta_key: str) -> str | None:
    """The content key written in the footer of a stored table (ADR-089), read from the file now; None when the file is
    missing, cannot be read or carries no such key. Only the footer is read, never the rows."""
    try:
        footer = pl.read_parquet_metadata(path)
    except (OSError, pl.exceptions.PolarsError):
        return None
    return footer.get(meta_key) or None


def stored_table_identity(tier: str, collection: str | None, recipe_id: str, view_key: str, tier1_path,
                          unstored_builds: int, plot_key: str | None = None, table_key: str | None = None) -> tuple | None:
    """Which stored table the dialog reads, as a value that is equal for two reads of the same table and different when the
    table can have other rows; None when nothing says which rows the table holds (the signature is then never equal).

    The dialog reads the stored Tier 1 table of the plot's collection ("T1") or its stored Tier 2 table ("T2" and "T3"; the Tier 1 table
    when the collection has no tier-2 steps, so T1 and T2 without tier-2 steps are the same table). The Source view reads no stored table
    (`source_table_identity`).
    The identity holds: the collection and the recipe, the Tier 1 key the open view holds (`DataAnalysisRecipeKeys`), the key written
    in the footer of the stored files the rows come from (read now, from the files, not computed: a file rewritten at the same path
    under another key, for example after an edit of a tier-2 step, which the Tier 1 key does not see because tier-2 steps are not
    part of it), and `unstored_builds`, how many tables were built and returned without being stored since the app started (their
    rows are in memory and no file carries a key for them). A collection that is not named, or a Tier 1 file with no key, gives None.
    The Tier 2 file is read when the view is T2 or T3 and the file exists: without tier-2 steps it does not exist (the orchestrator
    removes it), and the rows are those of the Tier 1 file.

    In "T3" the base is the table the plot reads: the stored Tier 2 plus the plot's own tier-3 steps of the recipe. That table
    is not stored (nothing carries its key in a file), so the caller gives its key (`plot_key`, `DataAnalysisRecipeKeys.plot_key_of`) and
    the key of the stored Tier 2 table it starts from (`table_key`, `DataAnalysisRecipeKeys.tier2_key_of`). The plot's key is part of the
    identity in "T3" only when it differs from `table_key`, that is when the plot has tier-3 steps: a plot without them reads the stored
    table as it is, so its identity in "T3" is exactly its identity in "T2" (a change of view between them does not change the table).
    In "T1" and "T2" the plot's key is never part of it (they read stored files).
    """
    if not collection:
        return None
    t1 = stored_key(tier1_path, TIER1_KEY_META)
    if t1 is None:
        return None
    t2 = stored_key(tier2_path_for(tier1_path), TIER2_KEY_META) if tier in ("T2", "T3") else None
    own_key = plot_key if tier == "T3" and plot_key != table_key else None
    return (collection, recipe_id, view_key, t1, t2, unstored_builds, own_key)


def source_table_identity(recipe_id: str, table_id: str, recipe_sha256: str, data_batch_hash: str) -> tuple:
    """Which source table the Source view reads, as a value: equal for two reads of the same table, different when it can have other rows.
    A source table is read from its file with its declared types (`DataOrchestrator.read_source`) and stored nowhere, so what says which
    rows it holds is the recipe (the declared types) and the hash of the data files the open view holds."""
    return ("SRC", recipe_id, table_id, recipe_sha256, data_batch_hash)


def dialog_rows_signature(table_identity, audit_nodes) -> tuple:
    """Which rows the dialog's table holds, as a value: equal for the same rows, different when they can differ.

    The rows are decided by (a) the stored table the dialog reads (`stored_table_identity`) and (b) the plot's audited steps that
    Audit mode applies to it on T3 (`audited_frame`; empty on every other view): every step in full (its type, column, operator, the whole list
    of values, `na`, `closed`, its reason) and their order. Exploration filters are not an input: the dialog does not apply them
    (`filter_and_audit_handlers._active_frame`). Nothing is read from the printed plan of the table: a plan is only the text of the
    steps and drops what makes two tables differ (a long list of values is printed truncated, a rewritten file prints the same).

    The value widget (list of values, range, bounds) is built from the rows, so it is mounted again when this changes, and not when a
    recompute rebuilt the same table. A doubt is never equal: when `table_identity` is None, or the steps cannot be written as text,
    every call returns a value that differs from every other (one more render).

    What this does NOT cover (so a list can still be old): a stored file that another process replaces between the build of the table
    and the read of its footer, and a file changed outside the app that still carries its old key (the key says what the file was
    built from, not what is in it now; ADR-089 and the export check work on the same keys).
    """
    if table_identity is None:
        return ("uncovered", object())
    try:
        steps = json.dumps(list(audit_nodes or []), sort_keys=True, default=str, separators=(",", ":"))
    except (TypeError, ValueError):
        return ("uncovered", object())
    return ("rows", table_identity, steps)


def audit_failures(plots: list) -> list[tuple[str, AuditStepError]]:
    """The plots whose audited steps cannot run: `plots` is a list of `(plot_id, make_base_frame, nodes)`; every failing plot
    is returned with its error (not only the first), a plot without steps is not looked at. The check the export makes before it
    writes anything: it runs `audited_frame`, so it says what the table and the plot say."""
    failing: list[tuple[str, AuditStepError]] = []
    for plot_id, make_base, nodes in plots:
        if not nodes:
            continue
        try:
            audited_frame(make_base(), nodes, plot_id)
        except AuditStepError as error:
            failing.append((plot_id, error))
    return failing
