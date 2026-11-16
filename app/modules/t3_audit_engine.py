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
# provides: function:dialog_value, function:not_offered_line, function:column_types, function:value_choices, function:pick_values, function:number_range, function:typed_operand, function:compose_date, function:compose_time, function:compose_datetime, function:compose_duration, function:column_bounds, function:control_hint, function:readable_duration, function:list_note, constant:LIST_ON_DEMAND_FROM, function:ops_for_column, function:value_widget_for, function:column_type_line, function:closed_phrase, function:between_prose, constant:CLOSED_CHOICES, function:_apply_filter_rows, function:filter_rows_from_nodes, function:staged_filter_row, function:audit_params_from_row, function:inapplicable_filter_rows, function:describe_filter, function:op_choice_label, function:audited_frame, function:audit_steps_in_order, function:dialog_frame, function:audit_failures, class:AuditStepError
# consumes: app/modules/error_notice.py (notice, lazy — VERIF-FIX-2), polars, libs/utils/src/utils/errors.py, libs/utils/src/utils/pipeline_error.py, libs/utils/src/utils/filter_values.py, libs/utils/src/utils/missing_values.py, libs/utils/src/utils/na_choice.py
# consumed_by: app/handlers/home_theater.py, app/handlers/filter_and_audit_handlers.py, app/handlers/export_handlers.py, app/tests/test_filter_dialog_values.py, app/tests/test_filter_four_way_pickers.py, app/tests/test_step_order.py, app/tests/test_removed_audit_step_type.py, app/tests/test_audit_error_names_the_plot.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-051
# @end_deps

import datetime
import math
import re
from decimal import Decimal

import polars as pl

from utils import action_names
from app.modules.renamed_keys import FIX_IN_APP, audit_step_defect
from utils.errors import TransformationError
from utils.pipeline_error import PipelineError
from utils.filter_values import (
    UNIT_NS, FilterValueError, duration_ns, filter_condition, kind_of, read_filter_value, type_words, unit_and_zone,
)
from utils.missing_values import keep_missing
from utils.na_choice import default_na, na_of


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


def typed_operand(raw, dtype):
    """What a control gave, in the type of the column, as the panel stores it (ADR-104 point 7).

    A number keeps the type of the column (an integer column an integer, a decimal column a decimal), true or false a real
    boolean, a date its year-month-day text (a session file holds no date object; the export types it from the dtype), a
    date and time, a time of day and a duration their exact text. A value that cannot be read is a `FilterValueError`.
    """
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


def inapplicable_filter_rows(lf, filter_rows: list, on_problem=None) -> list:
    """Filter rows whose column is absent from lf; they are skipped, not applied (issue #56).

    When the columns of `lf` cannot be read, no row can be judged and `[]` is still returned (what the function always did);
    `on_problem(text)` is then called, so that the caller can say that nothing was checked (D-0050). What the function should
    return in that case is a choice for Eve, not made here."""
    try:
        names = set(lf.collect_schema().names())
    except Exception as exc:
        if on_problem is not None:
            from app.modules.error_notice import notice
            on_problem(notice(
                "The columns of the table could not be read, so nobody checked which filters name a column the table does not have",
                "reload the page (F5); a filter on a column that is not in the table is skipped without a word until then", exc))
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


def staged_filter_row(column: str, op: str, value, dtype: str, na_tick: bool | None, closed: str = "both") -> dict:
    """The filter row the "+ Add" button stages: the tick of the dialog is recorded, never dropped.

    `na_tick` True keeps the rows with no value, False removes them; None (the tick is not mounted) is the default of
    the operator. `closed` is written for `between` only.
    """
    keep = default_na(op) == "keep" if na_tick is None else bool(na_tick)
    row = {"column": column, "op": op, "value": value, "dtype": dtype, "na": "keep" if keep else "remove"}
    if op == "between":
        row["closed"] = closed
    return row


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
    """The "My view" data of one plot: its audited steps applied to its base frame, in the order of `audit_steps_in_order`.

    The base is the stored Tier 2 (Tier 1 when the table has no tier2 steps): build rule T3 > T2 > T1. The ONE function
    for HOME's table, HOME's plot (also in Compare), the results bundle (`T3_data_<plot>.tsv` and the plot), the check before an
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


def dialog_frame(lf, nodes: list, in_my_view: bool, plot_id: str | None = None):
    """The table the filter dialog acts on: in My view the plot's table after its audited steps (a column that an earlier
    step dropped is not offered, a value list holds the rows that are still there); in T1 and T2 the table as it is. DECIDED
    2026-11-15 (Eve, S2-1 (a))."""
    return audited_frame(lf, nodes, plot_id) if in_my_view else lf


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
