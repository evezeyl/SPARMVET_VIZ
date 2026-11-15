"""The choice `na` of a filter: keep or remove the rows with no value in the column (NA-RULE-63, decided by Eve 2026-11-14).

Stdlib only (no Polars), so the audit translator, the session store and the HOME dialog can all read it. A row or an
audit step written before the choice existed has no `na`; it always removed those rows, so it is carried as "remove".
"""
# @deps
# provides: constant:NA_CHOICES, function:na_of, function:default_na, function:with_na, function:no_value_text
# consumes: -
# consumed_by: libs/utils/src/utils/missing_values.py, libs/blueprint_arch/src/blueprint_arch/t3_translator.py, app/modules/t3_audit_engine.py, libs/viz_factory/src/viz_factory/viz_factory.py, app/modules/session_manager.py, app/handlers/filter_and_audit_handlers.py
# doc: .claude/tasks/tasks.md#NA-RULE-63
# @end_deps
from typing import Optional

NA_CHOICES = ("keep", "remove")
_KEEP_BY_DEFAULT = ("ne", "not_in")


def na_of(row: Optional[dict]) -> str:
    """Return the `na` choice of a filter row or an audit step's params: "keep" or "remove".

    Data written before the choice existed has no `na`; it always removed the rows with no value, so it is "remove".
    A value that is neither is refused, never guessed.
    """
    na = (row or {}).get("na")
    if na is None:
        return "remove"
    if na not in NA_CHOICES:
        raise ValueError(f"na must be one of {NA_CHOICES}, not {na!r}")
    return na


def default_na(op: str) -> str:
    """The choice the HOME tick starts on: `!=` and not-in keep the rows with no value, every other operator removes them."""
    return "keep" if op in _KEEP_BY_DEFAULT else "remove"


def with_na(params: dict) -> dict:
    """A copy of `params` with `na` written (an old step without it becomes "remove")."""
    return {**params, "na": na_of(params)}


def no_value_text(na: str) -> str:
    """The choice in a few words for a list or a card: "no value: kept" or "no value: removed"."""
    return "no value: kept" if na_of({"na": na}) == "keep" else "no value: removed"
