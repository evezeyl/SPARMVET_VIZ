"""The step bar of HOME in Audit mode: the words and the rules of what the bar offers, with no Shiny import (ADR-045, Two-Category Law).

The step bar is the ONE entry that creates an audit step (ledger D-0663, D-0672): it sits with the data preview, names the item it acts on, holds the step being built (a condition or a column
drop, one at a time) and the button "Try"; the answer of Try (the places, the marks "User verified", the reason, "Add to audit pipeline", "Discard") is its fold-out. The screen is
`app/handlers/step_bar_handlers.py`; the effects of Try and Add are `app/handlers/trial_handlers.py`.

All words here are PROVISIONAL (the owner reads them).

# @deps
# provides: function:try_state, function:drop_words, function:kind_of_input, function:fold_summary, const:KIND_CHOICES, const:TRY_BUTTON, const:STEP_BAR_LABEL
# consumes: app/modules/audit_try.py (KIND_FILTER, KIND_DROP, drops_from_selection)
# consumed_by: app/handlers/step_bar_handlers.py, app/handlers/trial_handlers.py, app/tests/test_step_bar.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0663, D-0672)
# @end_deps
"""
from __future__ import annotations

from typing import Any, Optional, Sequence, Tuple

from app.modules.audit_try import KIND_DROP, KIND_FILTER, drops_from_selection

STEP_BAR_LABEL = "Create an audit step"                      # the accessible name of the region
KIND_CONDITION_LABEL = "Condition on rows"
KIND_DROP_LABEL = "Drop columns"
KIND_CHOICES = {KIND_FILTER: KIND_CONDITION_LABEL, KIND_DROP: KIND_DROP_LABEL}   # the plain switch: one kind at a time (D-0672)
KIND_LABEL = "Step to create"
TRY_BUTTON = "Try"
NEEDS_CONDITION = "Add a condition row first (in the Filters panel on the left: column, operator, value, then + Add), then press Try."
CONDITION_HINT = "No condition yet. Build it in the Filters panel on the left (column, operator, value, then + Add)."
CONDITION_EDIT_HINT = "To change it, remove a row or reset in the Filters panel on the left."
NEEDS_T3_FOR_DROP = "Columns are dropped at the Result data (T3) of a plot: show a plot's Result data in Path of the data first."
NEEDS_DESELECTED = "Deselect the columns to drop in the column chooser below the bar, then press Try."


def fold_summary(kind: str) -> str:
    """The first line of the fold-out: which kind of step the open trial is (the switch may have been moved since; the trial stays what it was tried as). PROVISIONAL words."""
    what = "a column drop" if kind == KIND_DROP else "a condition"
    return f"Result of Try: {what} (not applied): fold or open"


def kind_of_input(value: Any) -> str:
    """The kind of step the switch names (`KIND_FILTER` or `KIND_DROP`); anything else (no switch on the page, a stale value) is the condition, the default."""
    return KIND_DROP if value == KIND_DROP else KIND_FILTER


def drop_words(columns: Sequence[str]) -> str:
    """The step being built, in words, when it is a column drop (the columns named; no row is removed, said)."""
    if not columns:
        return "No column is deselected: nothing to drop yet."
    names = ", ".join(columns)
    return f"Drop {'the column' if len(columns) == 1 else f'the {len(columns)} columns'}: {names}. No row is removed."


def try_state(kind: str, n_rows: int, shown_place: Optional[str], column_names: Sequence[str], selection: Any) -> Tuple[bool, str, Tuple[str, ...]]:
    """(enabled, why not, the columns to drop) for the button Try of the bar. Never a silent grey: when the button is off the second item says why in one plain sentence.

    A condition needs at least one staged row. A drop needs the Result data (T3) of a plot to be the item shown (the place a drop was always offered at, PROVISIONAL) and at least one column
    deselected in the column chooser."""
    if kind == KIND_DROP:
        if not shown_place or not str(shown_place).startswith("T3:"):
            return False, NEEDS_T3_FOR_DROP, ()
        columns = tuple(drops_from_selection(list(column_names), selection))
        if not columns:
            return False, NEEDS_DESELECTED, ()
        return True, "", columns
    if n_rows <= 0:
        return False, NEEDS_CONDITION, ()
    return True, "", ()
