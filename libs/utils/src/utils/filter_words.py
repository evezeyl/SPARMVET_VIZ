"""The plain words of a filter, in one place: its value and what happens to the rows with no value in the column.

Stdlib only, so the HOME panels, the audit cards, the dialog and the export read the same sentences (one function for each thing, never a second spelling).
Display only: nothing here changes what a step stores or compares.

PROVISIONAL (the owner's own example of 2026-11-26, one line to change): "rows with no <column> record are removed" / "rows with no <column> record are kept"; a whole number is shown without ".0".

# @deps
# provides: function:value_text, function:no_value_words
# consumes: libs/utils/src/utils/na_choice.py
# consumed_by: app/handlers/audit_stack.py, app/handlers/home_theater.py, app/handlers/export_handlers.py, app/handlers/lineage_handlers.py, app/modules/t3_audit_engine.py
# doc: .claude/rules/ui_implementation_contract.md#8
# @end_deps
"""
from __future__ import annotations

from typing import Any

from utils.na_choice import na_of

_EXACT_INTEGER_LIMIT = 1e15      # beyond this a float no longer holds every whole number exactly: shown as Python writes it


def value_text(value: Any) -> str:
    """A filter value as text. A decimal number that is a whole number is shown without ".0" ("2024", not "2024.0"): the column may hold decimals (a year read as Float64),
    and the number the user typed was 2024. Any other value is shown as written (2.5, text, True). NaN and infinity are shown as Python writes them."""
    if isinstance(value, float) and value.is_integer() and abs(value) < _EXACT_INTEGER_LIMIT:
        return str(int(value))
    return str(value)


def no_value_words(na: str, column: str) -> str:
    """What the choice `na` does to the rows with no value in `column`, in plain words: "rows with no year record are removed" or "rows with no year record are kept".
    `na` is "keep" or "remove" (anything else is refused, never guessed: `na_of`)."""
    fate = "kept" if na_of({"na": na}) == "keep" else "removed"
    return f"rows with no {column} record are {fate}"
