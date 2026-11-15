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
from typing import Any

import polars as pl

_WORDS = {"int": "whole numbers", "float": "decimal numbers", "bool": "true or false", "date": "dates", "datetime": "dates and times",
          "text": "text", "category": "categories"}


class FilterValueError(ValueError):
    """A filter value that does not fit its column. `problem` says what is wrong, `fix` what to write; both are plain words."""

    def __init__(self, problem: str, fix: str = "") -> None:
        self.problem, self.fix = problem, fix
        super().__init__(f"{problem}. Fix: {fix}" if fix else problem)


def kind_of(dtype: Any) -> str:
    """The family of a dtype (a Polars dtype or its name): int, float, bool, date, datetime, text, category (Categorical, Enum),
    or other (Time, Duration, unknown)."""
    s = str(dtype) if dtype is not None else ""
    if "Int" in s:
        return "int"
    if "Float" in s or "Decimal" in s:
        return "float"
    if s == "Boolean":
        return "bool"
    if s == "Date":
        return "date"
    if s.startswith("Datetime"):
        return "datetime"
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
    a date or "YYYY-MM-DD". Date and time columns: a datetime or "YYYY-MM-DD HH:MM:SS" (a date alone is refused). Category columns: text.
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
        if isinstance(value, datetime.datetime):
            return value
        try:
            if isinstance(value, str):
                return datetime.datetime.fromisoformat(value.strip())
        except ValueError:
            pass
        raise _wrong(value, dtype, "write the date and time as year-month-day hour:minute:second, for example 2020-01-31 10:30:00")
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
    if kind == "datetime" and not isinstance(value, datetime.datetime):
        raise _wrong(value, dtype, "write the date and time without quotes, for example 2020-01-31 10:30:00")


def _operand(value: Any, dtype: Any, strict: bool) -> Any:
    if strict:
        check_filter_value(value, dtype)
        return value
    return read_filter_value(value, dtype)


def filter_condition(column: str, op: str, value: Any, dtype: Any, closed: str = "both", *,
                     strict: bool = False, other_as_text: bool = True) -> pl.Expr:
    """The Polars condition of one filter row: `column` `op` `value`, the value read (or checked, `strict`) against `dtype`.

    A list given to eq or ne means in or not_in. `in` and `not_in` compare typed values, never their text; only a column of
    another type (Categorical, Datetime, unknown) compares text when `other_as_text` (what the HOME table and the plot did).
    `between` takes [low, high] and `closed` (both, left, right, none) names the ends included; it needs a number or a date
    column. The rows with no value are not handled here (`na`, `keep_missing`).
    """
    kind = kind_of(dtype)
    col = pl.col(column)
    if isinstance(value, (list, tuple)) and op in ("eq", "ne"):
        op = "in" if op == "eq" else "not_in"
    if kind == "bool" and op in ("gt", "ge", "lt", "le", "between"):
        raise FilterValueError("Greater than, less than and between are not defined for a column of true or false",
                               "use equal, not equal, one of or none of")
    if op == "between":
        if kind not in ("int", "float", "date", "datetime"):
            raise FilterValueError(f"between needs a column of numbers or dates, and this column holds {type_words(dtype)}",
                                   "use a column of numbers or dates, or one of the other operators")
        lo, hi = _numbers([_operand(v, dtype, strict) for v in value], kind)
        return col.is_between(lo, hi, closed=closed)
    if op in ("in", "not_in"):
        raw = list(value) if isinstance(value, (list, tuple)) else [value]
        if kind in ("text", "category"):
            if strict:
                for v in raw:
                    check_filter_value(v, dtype)
            expr = (col.cast(pl.Utf8) if kind == "category" else col).is_in([str(v) for v in raw])
        else:
            values = _numbers([_operand(v, dtype, strict) for v in raw], kind)
            expr = col.cast(pl.Utf8).is_in([str(v) for v in values]) if kind == "other" and other_as_text else col.is_in(values)
        return expr if op == "in" else ~expr
    operand = _operand(value, dtype, strict)
    if kind == "category":
        col = col.cast(pl.Utf8)
    return {"eq": col == operand, "ne": col != operand, "gt": col > operand, "ge": col >= operand,
            "lt": col < operand, "le": col <= operand}[op]


def _numbers(values: list, kind: str) -> list:
    """A list of whole numbers and decimals is a list of numbers: when one is a decimal, all are, so Polars takes it as one list."""
    if kind in ("int", "float") and any(isinstance(v, float) for v in values):
        return [float(v) for v in values]
    return values
