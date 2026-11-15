"""A filter value has the type of its column: one reading and one condition for the HOME table, the plot and the recipe action.

ADR-104 point 7 (Eve, 2026-11-14). The HOME filter panel stores the real value (a number for a number column, true or
false for a true/false column). Two modes read a value against the dtype of the column:

- `read_filter_value` (lenient): a value an older row or audit step holds as text is read as the type of the column, from the
  dtype the step carries or the schema of the table. A value that cannot be read is reported in plain words, never guessed.
- `check_filter_value` (strict): the mode of the recipe action `modif_filter`. No conversion: a value of another type is
  refused with a plain error (what the value is, what the column holds, how to fix it).

`filter_condition` builds the Polars condition for one filter row in either mode, so that the HOME table, the plot and the
recipe action keep the same rows. The choice for missing values (`na`) is applied by the caller (`keep_missing`).

Consumed by: app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py,
libs/transformer/src/transformer/actions/modified.py, libs/blueprint_arch/src/blueprint_arch/t3_translator.py,
libs/utils/src/utils/recipe_check.py, app/handlers/filter_and_audit_handlers.py.
If deleted: the table, the plot and the action do not filter, and the export cannot type an old value.
"""
# @deps
# provides: function:kind_of, function:type_words, function:read_filter_value, function:check_filter_value, function:filter_condition, class:FilterValueError
# consumes: polars
# consumed_by: app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/transformer/src/transformer/actions/modified.py, libs/blueprint_arch/src/blueprint_arch/t3_translator.py, libs/utils/src/utils/recipe_check.py, app/handlers/filter_and_audit_handlers.py, libs/utils/tests/test_filter_values.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104
# @end_deps
import datetime
import re
from decimal import Decimal
from typing import Any

import polars as pl

# A date and time as text: year-month-day, hour:minute, optional seconds with up to nine digits, optional offset (Z or +hh:mm).
_DATETIME_TEXT = re.compile(r"^\d{4}-\d{2}-\d{2}[ T]\d{2}:\d{2}(:\d{2}(\.\d{1,9})?)?(Z|[+-]\d{2}:?\d{2})?$")
def _is_datetime_text(text: str) -> bool:
    """The text is a real date and time (a month 13 or an hour 25 is not)."""
    text = text.strip()
    if not _DATETIME_TEXT.match(text):
        return False
    try:
        datetime.date.fromisoformat(text[:10])
    except ValueError:
        return False
    hour, minute = int(text[11:13]), int(text[14:16])
    second = int(text[17:19]) if len(text) >= 19 and text[16] == ":" else 0
    return hour < 24 and minute < 60 and second < 60


_OFFSET = re.compile(r"(Z|[+-]\d{2}:?\d{2})$")
_DATETIME_FIX = "write the date and time as year-month-day hour:minute:second, for example 2020-01-31 10:30:00"
_WORDS = {"int": "whole numbers", "float": "decimal numbers", "bool": "true or false", "date": "dates", "datetime": "dates and times",
          "time": "times of day", "duration": "durations", "text": "text", "category": "categories"}

# A time of day as text: hour:minute, optional seconds with up to nine digits (a Polars Time keeps nanoseconds).
_TIME_TEXT = re.compile(r"^(\d{2}):(\d{2})(?::(\d{2})(?:\.(\d{1,9}))?)?$")
_TIME_FIX = "write the time as hour:minute:second, for example 10:30:00 (up to nine digits after the second)"
# A duration as text: a number and a unit, for example "90 min" or "1.5 h" (a Polars Duration keeps one unit: ns, us or ms).
_DURATION_TEXT = re.compile(r"^\s*(-?\d+(?:\.\d+)?)\s*(ns|us|ms|s|min|h|d|w)\s*$")
UNIT_NS = {"ns": 1, "us": 10**3, "ms": 10**6, "s": 10**9, "min": 60 * 10**9, "h": 3600 * 10**9, "d": 86400 * 10**9, "w": 7 * 86400 * 10**9}
_DURATION_FIX = "write the duration as a number and a unit (ns, us, ms, s, min, h, d or w), for example 90 min or 1.5 h"


def _time_ns(text: str) -> int | None:
    """Nanoseconds since midnight of a time written as text, or None when it is not a real time (an hour 25 is not)."""
    m = _TIME_TEXT.match(text.strip())
    if not m:
        return None
    hour, minute, second = int(m.group(1)), int(m.group(2)), int(m.group(3) or 0)
    if hour > 23 or minute > 59 or second > 59:
        return None
    fraction = int((m.group(4) or "").ljust(9, "0")) if m.group(4) else 0
    return ((hour * 60 + minute) * 60 + second) * 10**9 + fraction


def duration_ns(text: str) -> Decimal | None:
    """The nanoseconds of a duration written as text (exact, a Decimal), or None when it is not a number and a unit."""
    m = _DURATION_TEXT.match(text)
    return Decimal(m.group(1)) * UNIT_NS[m.group(2)] if m else None


def _duration_text(value: Any) -> str:
    """A duration as the text the panel stores: "<number> <unit>"; a timedelta is written in microseconds."""
    if isinstance(value, datetime.timedelta):
        return f"{(value.days * 86400 + value.seconds) * 10**6 + value.microseconds} us"
    m = _DURATION_TEXT.match(str(value))
    return f"{m.group(1)} {m.group(2)}" if m else str(value)


class FilterValueError(ValueError):
    """A filter value that does not fit its column. `problem` says what is wrong, `fix` what to write; both are plain words."""

    def __init__(self, problem: str, fix: str = "") -> None:
        self.problem, self.fix = problem, fix
        super().__init__(f"{problem}. Suggestion: {fix}" if fix else problem)


def kind_of(dtype: Any) -> str:
    """The family of a dtype (a Polars dtype or its name): int, float, bool, date, datetime, text, category (Categorical, Enum),
    time, duration, or other (unknown, binary, lists, ...)."""
    s = str(dtype) if dtype is not None else ""
    # startswith, not "in": a List(Int64) or an Array(Float64, 3) column is not a number column
    if s.startswith(("Int", "UInt")):
        return "int"
    if s.startswith(("Float", "Decimal")):
        return "float"
    if s == "Boolean":
        return "bool"
    if s == "Date":
        return "date"
    if s.startswith("Datetime"):
        return "datetime"
    if s == "Time":
        return "time"
    if s.startswith("Duration"):
        return "duration"
    if s.startswith(("Categorical", "Enum")):
        return "category"
    if s in ("String", "Utf8"):
        return "text"
    return "other"


def type_words(dtype: Any) -> str:
    """What the column holds, in words a HOME user reads: whole numbers, decimal numbers, true or false, dates, text."""
    return _WORDS.get(kind_of(dtype)) or (str(dtype) if dtype is not None else "values of an unknown type")


def _given(value: Any) -> str:
    if value is None:
        return "empty"
    if isinstance(value, bool):
        return "true or false"
    if isinstance(value, (int, float)):
        return "a number"
    if isinstance(value, str):
        return "text"
    if isinstance(value, (datetime.date, datetime.datetime)):
        return "a date"
    if isinstance(value, datetime.time):
        return "a time"
    if isinstance(value, datetime.timedelta):
        return "a duration"
    return "a list"


def _wrong(value: Any, dtype: Any, fix: str) -> FilterValueError:
    shown = repr(value) if isinstance(value, str) else str(value)
    return FilterValueError(f"The value {shown} is {_given(value)}, but this column holds {type_words(dtype)} ({dtype})", fix)


def _number_fix(kind: str) -> str:
    return "write the value as a number without quotes, for example 90" if kind in ("int", "float") else "write a value of that type"


def read_filter_value(value: Any, dtype: Any) -> Any:
    """Return `value` in the type of a column of `dtype`; raise FilterValueError when it cannot be read as that type.

    Number columns: a float column gets a float; an integer column gets an int when the value is integer-valued ("90", 90.0),
    else a float ("90.5"), never truncated. True or false columns: True, False, "true", "false" in any case. Date columns:
    a date or "YYYY-MM-DD". Date and time columns: the exact text "YYYY-MM-DD HH:MM:SS[.fraction][offset]" (a datetime gives its text; a date alone is refused). Category columns: text.
    Text and other columns: the value as it is.
    """
    kind = kind_of(dtype)
    if kind in ("int", "float"):
        if isinstance(value, bool) or value is None or isinstance(value, (list, tuple, dict)):
            raise _wrong(value, dtype, _number_fix(kind))
        try:
            if kind == "int" and not isinstance(value, float):
                try:
                    return int(str(value).strip())  # exact for integers a float cannot hold
                except ValueError:
                    pass
            number = float(value)
        except (ValueError, TypeError):
            raise _wrong(value, dtype, _number_fix(kind)) from None
        return int(number) if kind == "int" and number.is_integer() else number
    if kind == "bool":
        if isinstance(value, bool):
            return value
        if isinstance(value, str) and value.strip().lower() in ("true", "false"):
            return value.strip().lower() == "true"
        raise _wrong(value, dtype, "write true or false")
    if kind == "date":
        if isinstance(value, datetime.datetime):
            return value.date()
        if isinstance(value, datetime.date):
            return value
        try:
            if isinstance(value, str):
                return datetime.date.fromisoformat(value.strip())
        except ValueError:
            pass
        raise _wrong(value, dtype, "write the date as year-month-day, for example 2020-01-31")
    if kind == "datetime":
        # The exact text: nanoseconds and the offset survive; the column's own unit and zone read it in `filter_condition`.
        if isinstance(value, datetime.datetime):
            return value.isoformat()
        if isinstance(value, str) and _is_datetime_text(value):
            return value.strip()
        raise _wrong(value, dtype, _DATETIME_FIX)
    if kind == "time":
        if isinstance(value, datetime.time):
            return value.isoformat()
        if isinstance(value, str) and _time_ns(value) is not None:
            return value.strip()
        raise _wrong(value, dtype, _TIME_FIX)
    if kind == "duration":
        if isinstance(value, datetime.timedelta) or (isinstance(value, str) and duration_ns(value) is not None):
            return _duration_text(value)
        raise _wrong(value, dtype, _DURATION_FIX)
    if kind == "category" and not isinstance(value, str):
        raise _wrong(value, dtype, "write the value as text")
    return value


def check_filter_value(value: Any, dtype: Any) -> None:
    """Strict mode: raise FilterValueError unless `value` already has the type of a column of `dtype`. Nothing is converted.

    Number columns take a number (not text, not true/false); text and category columns take text; true/false columns take True or
    False; date columns take a date, date and time columns a datetime (written without quotes in a recipe, which reads them as
    such). Time, duration and unknown columns are not judged here.
    """
    kind = kind_of(dtype)
    is_number = isinstance(value, (int, float)) and not isinstance(value, bool)
    if kind in ("int", "float") and not is_number:
        raise _wrong(value, dtype, _number_fix(kind))
    if kind in ("text", "category") and not isinstance(value, str):
        raise _wrong(value, dtype, "write the value as text, in quotes")
    if kind == "bool" and not isinstance(value, bool):
        raise _wrong(value, dtype, "write true or false without quotes")
    if kind == "date" and not (isinstance(value, datetime.date) and not isinstance(value, datetime.datetime)):
        raise _wrong(value, dtype, "write the date without quotes as year-month-day, for example 2020-01-31")
    if kind == "datetime" and not (isinstance(value, datetime.datetime) or (isinstance(value, str) and _is_datetime_text(value))):
        raise _wrong(value, dtype, _DATETIME_FIX + " (a text keeps every digit, a recipe cannot hold nanoseconds as a date)")
    if kind == "time" and not (isinstance(value, datetime.time) or (isinstance(value, str) and _time_ns(value) is not None)):
        raise _wrong(value, dtype, _TIME_FIX + " (in quotes, because a recipe reads 10:30:00 without quotes as a number)")
    if kind == "duration" and not (isinstance(value, datetime.timedelta) or (isinstance(value, str) and duration_ns(value) is not None)):
        raise _wrong(value, dtype, _DURATION_FIX + " (in quotes)")


def _refuse_operator(op: str, value: Any, dtype: Any) -> None:
    """The operator does not fit the type of the column: said in plain words, never zero rows and never a raw error."""
    kind = kind_of(dtype)
    if dtype is not None and kind == "other":
        raise FilterValueError(f"A filter on a column that holds {dtype} is not offered", "filter another column, or change this column in the recipe")
    if kind == "bool" and op in ("gt", "ge", "lt", "le", "between"):
        shown = value[0] if isinstance(value, (list, tuple)) and value else value
        raise FilterValueError(f"The value {shown} cannot be compared with greater than, less than or between: this column holds "
                               f"{type_words(dtype)} ({dtype})", "use equal, not equal, one of or none of")
    if op == "between" and kind not in ("int", "float", "date", "datetime", "time", "duration"):
        raise FilterValueError(f"between needs a column of numbers, dates or times, and this column holds {type_words(dtype)} ({dtype})",
                               "use a column of numbers, dates or times, or one of the other operators")


def check_filter(op: str, value: Any, dtype: Any) -> None:
    """Strict mode for a whole filter: raise FilterValueError when the operator does not fit the column or a value has the wrong type.

    One rule for the recipe checker and the recipe action. A list given to eq or ne is a list for in or not_in; a list with a
    comparison is a shape error reported elsewhere and is not judged here.
    """
    _refuse_operator(op, value, dtype)
    if op in ("in", "not_in", "between"):
        values = list(value) if isinstance(value, (list, tuple)) else []
    else:
        values = list(value) if isinstance(value, (list, tuple)) and op in ("eq", "ne") else ([] if isinstance(value, (list, tuple)) else [value])
    for item in values:
        check_filter_value(item, dtype)


def _operand(value: Any, dtype: Any, strict: bool) -> Any:
    if strict:
        check_filter_value(value, dtype)
        return value
    return read_filter_value(value, dtype)


def unit_and_zone(dtype: Any) -> tuple:
    """The time unit (ms, us, ns) and time zone of a date and time dtype, read from its name; us and no zone when it says nothing."""
    text = str(dtype)
    unit = re.search(r"time_unit='(\w+)'", text)
    zone = re.search(r"time_zone='([^']+)'", text)
    return (unit.group(1) if unit else "us"), (zone.group(1) if zone else None)


def _datetime_values(values: list, dtype: Any) -> pl.Series:
    """The values as one Series of the column's own dtype (unit and zone), parsed from their exact text.

    A text without an offset is a wall-clock time in the zone of the column, an offset text is that instant shown in the zone of
    the column; an offset on a column with no zone, a value finer than the column's unit and a text that is no date and time are
    refused in plain words (nothing is cut, nothing is read as UTC by chance).
    """
    unit, zone = unit_and_zone(dtype)
    parts = []
    for value in values:
        text = value.isoformat() if isinstance(value, datetime.datetime) else str(value).strip()
        if not _is_datetime_text(text):
            raise _wrong(value, dtype, _DATETIME_FIX)
        if zone is None and _OFFSET.search(text):
            raise FilterValueError(f"The value {text!r} has a time zone offset, but this column has no time zone ({dtype})",
                                   "write the date and time without an offset")
        try:
            fine = pl.Series([text]).str.to_datetime(time_unit="ns", time_zone=zone)
        except Exception:
            raise _wrong(value, dtype, _DATETIME_FIX) from None
        coarse = fine.dt.cast_time_unit(unit)
        if (coarse.dt.cast_time_unit("ns") != fine).any():
            raise FilterValueError(f"The value {text!r} is finer than the unit of this column ({unit}); it would be cut",
                                   f"write at most the digits of the unit ({unit})")
        parts.append(coarse)
    return pl.concat(parts) if parts else pl.Series([], dtype=pl.Datetime(unit, zone))


def _time_values(values: list, dtype: Any) -> pl.Series:
    """The values as one Series of Time (nanoseconds since midnight, exact), parsed from their text."""
    counts = []
    for value in values:
        text = value.isoformat() if isinstance(value, datetime.time) else str(value)
        ns = _time_ns(text)
        if ns is None:
            raise _wrong(value, dtype, _TIME_FIX)
        counts.append(ns)
    return pl.Series(counts, dtype=pl.Int64).cast(pl.Time)


def _duration_values(values: list, dtype: Any) -> pl.Series:
    """The values as one Series of Duration in the unit of the column; a value finer than that unit is refused (nothing is cut)."""
    unit, _zone = unit_and_zone(dtype)
    counts = []
    for value in values:
        text = _duration_text(value)
        ns = duration_ns(text)
        if ns is None:
            raise _wrong(value, dtype, _DURATION_FIX)
        count = ns / UNIT_NS[unit]
        if count != count.to_integral_value():
            raise FilterValueError(f"The value {text!r} is finer than the unit of this column ({unit}); it would be cut",
                                   f"write at most the digits of the unit ({unit}), for example a whole number of {unit}")
        counts.append(int(count))
    return pl.Series(counts, dtype=pl.Int64).cast(pl.Duration(unit))


_AS_SERIES = {"datetime": _datetime_values, "time": _time_values, "duration": _duration_values}


def _typed_series(values: list, dtype: Any) -> pl.Series:
    """The values as one Series of the dtype of the column: date and time, time of day and duration are parsed from their exact text."""
    return _AS_SERIES[kind_of(dtype)](values, dtype)


def filter_condition(column: str, op: str, value: Any, dtype: Any, closed: str = "both", *, strict: bool = False) -> pl.Expr:
    """The Polars condition of one filter row: `column` `op` `value`, the value read (or checked, `strict`) against `dtype`.

    A list given to eq or ne means in or not_in. `in` and `not_in` compare typed values, never their text; a date and time is
    parsed from its exact text into the unit and zone of the column. `between` takes [low, high] and `closed` (both, left, right,
    none) names the ends included; it needs a number or a date column. A column that holds a time, a duration or another type
    that is not offered, and true or false with a comparison, are refused in plain words. An unknown type (`dtype` None) compares
    text. The rows with no value are not handled here (`na`, `keep_missing`).
    """
    kind = kind_of(dtype)
    col = pl.col(column)
    if isinstance(value, (list, tuple)) and op in ("eq", "ne"):
        op = "in" if op == "eq" else "not_in"
    _refuse_operator(op, value, dtype)
    if op == "between":
        operands = [_operand(v, dtype, strict) for v in value]
        if kind in _AS_SERIES:
            pair = _typed_series(operands, dtype)
            lo, hi = pl.lit(pair.slice(0, 1)), pl.lit(pair.slice(1, 1))   # a Series, not Python objects: no digit is cut
        else:
            lo, hi = _numbers(operands, kind)
        return col.is_between(lo, hi, closed=closed)
    if op in ("in", "not_in"):
        raw = list(value) if isinstance(value, (list, tuple)) else [value]
        operands = [_operand(v, dtype, strict) for v in raw]
        if kind == "text":
            expr = col.is_in([str(v) for v in operands])
        elif kind == "category" or dtype is None:
            expr = col.cast(pl.Utf8).is_in([str(v) for v in operands])
        elif kind in _AS_SERIES:
            expr = col.is_in(_typed_series(operands, dtype).implode())
        else:
            expr = col.is_in(_numbers(operands, kind))
        return expr if op == "in" else ~expr
    operand = _operand(value, dtype, strict)
    if kind in _AS_SERIES:
        operand = pl.lit(_typed_series([operand], dtype))
    return {"eq": col == operand, "ne": col != operand, "gt": col > operand, "ge": col >= operand,
            "lt": col < operand, "le": col <= operand}[op]


def _numbers(values: list, kind: str) -> list:
    """A list of whole numbers and decimals is a list of numbers: when one is a decimal, all are, so Polars takes it as one list."""
    if kind in ("int", "float") and any(isinstance(v, float) for v in values):
        return [float(v) for v in values]
    return values
