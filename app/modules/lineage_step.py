"""The audit step written from the lineage panel at a result table no plot reads (LINEAGE-VIEW-G step 3, D-0627, D-0630), and the staging of pending steps at a place.

Pure: no Shiny, no file, no engine call. The Filters panel of HOME is built on the table of the open plot, so it cannot write a step at a table no plot reads. The lineage panel
has a small form for that case: a column of THE PLACE (the engine's plan, `utils.lineage_data` / `utils.plan_book`, never the recipe's own idea of its columns), an operator and a
value. This module turns what the user typed into the filter row of the Filters panel (`t3_audit_engine.staged_filter_row`, the same rules: the value has the type of the column,
leading and trailing spaces of a typed value are removed (D-0626), `na` is the default of the operator and is told) and refuses, in a plain sentence, what it cannot read.

THE FORM'S COLUMNS (PROVISIONAL, the builder's reading): a column whose type is a whole number, a decimal number, text, a category, true or false, or a date. A column of a date and
time, a time of day, a duration or another type is not offered in this small form (the dialog of the Filters panel has the pickers for them; building them again here is not
decided): `form_columns` returns them in `left_out` so that the panel says so, never silently.

THE VALUE TEXT: one value for a comparison; several values separated by a comma for "any of" and "none of" (an item is trimmed, an empty item is refused); two values separated by a
comma for "between", the lower first; true or false for a true/false column; year-month-day for a date.

`stage_nodes` is the one function that puts pending steps at places into the state (the dialog of the Filters panel and this form both use it).

Consumed by: app/handlers/lineage_handlers.py, app/handlers/filter_and_audit_handlers.py (stage_nodes), app/tests/test_lineage_step.py. If deleted: no step can be written at a table no plot reads.

# @deps
# provides: function:form_columns, function:form_ops, function:parse_value, function:step_params, function:stage_nodes, function:stage_sentence, constant:FORM_KINDS, constant:PENDING_NOTE
# consumes: app/modules/t3_audit_engine.py (ops_for_column, value_widget_for, typed_operand, trim_typed, staged_filter_row, audit_params_from_row, describe_filter), libs/utils/src/utils/filter_values.py (kind_of, filter_condition, FilterValueError), app/modules/session_manager.py (make_audit_step)
# consumed_by: app/handlers/lineage_handlers.py, app/handlers/filter_and_audit_handlers.py, app/tests/test_lineage_step.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/knowledge/decision_ledger.md (D-0627, D-0630)
# @end_deps
"""
from __future__ import annotations

from typing import Any, Dict, List, Optional, Sequence, Tuple

from app.modules.audit_places import PLACES_BUCKET
from app.modules.t3_audit_engine import audit_params_from_row, describe_filter, ops_for_column, staged_filter_row, trim_typed, typed_operand, value_widget_for
from utils.filter_values import FilterValueError, filter_condition, kind_of

FORM_KINDS = ("int", "float", "text", "category", "bool", "date")
PENDING_NOTE = "Write a reason in the Pipeline Audit panel on the right, then press Apply."   # PROVISIONAL words


def form_columns(columns: Optional[Sequence[Tuple[str, str]]]) -> Tuple[List[Tuple[str, str]], List[str]]:
    """`(offered, left_out)` for the columns of a place (the engine's (name, type) pairs): the columns the form takes, in the plan's order, and the names of the others."""
    offered: List[Tuple[str, str]] = []
    left_out: List[str] = []
    for name, dtype in columns or ():
        if kind_of(dtype) in FORM_KINDS and ops_for_column(dtype, False):
            offered.append((name, dtype))
        else:
            left_out.append(name)
    return offered, left_out


def form_ops(dtype: str) -> List[str]:
    """The operators the form offers for a column of this type (the same list as the dialog of the Filters panel, with no discrete axis)."""
    return ops_for_column(dtype, False)


def _items(text: str) -> List[str]:
    items = [trim_typed(i) for i in str(text or "").split(",")]
    if not any(items):
        return []
    if "" in items:
        raise FilterValueError("The list holds an empty item", "write the values separated by a comma, with no empty item")
    return items


def parse_value(column: str, op: str, dtype: str, text: str) -> Tuple[str, Any]:
    """`(operator, value)` for what the user typed, the value in the type of the column. Raises `FilterValueError` (plain words) for a value that cannot be read, or for none.

    "in" and "not_in" (and "eq"/"ne" on text, which mean the same) take a list; "between" takes two values, the lower first (put in order when reversed); every other comparison one."""
    widget = value_widget_for(dtype, False, op)
    items = _items(text)
    if not items:
        raise FilterValueError(f"No value is given for {column}, so no step is written", "type the value (several values: separated by a comma)")
    if widget == "list":
        value: Any = [typed_operand(i, dtype) for i in items]
        op = {"eq": "in", "ne": "not_in"}.get(op, op)
    elif widget == "range":
        if len(items) != 2:
            raise FilterValueError("'between' needs two values", "type the lower and the upper value, separated by a comma")
        low, high = typed_operand(items[0], dtype), typed_operand(items[1], dtype)
        value = [high, low] if low > high else [low, high]
    else:
        if len(items) != 1:
            raise FilterValueError(f"A comparison takes one value, {len(items)} were typed", "type one value, or choose 'any of' for several")
        value = typed_operand(items[0], dtype)
    filter_condition(column, op, value, dtype)           # the rule judges the whole value now: a refused value is refused here, not at Apply
    return op, value


def step_params(column: str, op: str, dtype: str, text: str) -> Dict[str, Any]:
    """The params of the audit step for what the form holds (the same as `audit_params_from_row` of a staged Filters row): the column, the operator, the typed value, the type of
    the column and `na` (the default of the operator). Raises `FilterValueError`."""
    real_op, value = parse_value(column, op, dtype, text)
    return audit_params_from_row(staged_filter_row(column, real_op, value, dtype, None))


def stage_sentence(params: Dict[str, Any]) -> str:
    """The one line of what was staged, with what happens to the rows with no value (never silent)."""
    return describe_filter(params["column"], params["op"], params["value"], params.get("na"))


def stage_nodes(state: dict, placed: Sequence[Tuple[dict, str]], started_from: str) -> dict:
    """The state with one pending node added for each (scratch node, place): written at that place, with the id of the decision, no reason yet (Apply is locked until it has one).
    Returns a new state; the caller sets it. A scratch node without an id gets one from `make_audit_step`; the nodes of one decision share it."""
    from app.modules.session_manager import make_audit_step
    pending = list(state.get("_pending_t3_nodes", []))
    for scratch_node, place in placed:
        pending.append(make_audit_step(
            scratch_node["node_type"], dict(scratch_node.get("params", {})),
            plot_scope=PLACES_BUCKET, reason="",
            primary_key_warning=bool(scratch_node.get("primary_key_warning")),
            node_id=scratch_node.get("id"), place=place, started_from=started_from,
        ))
    return {**state, "_pending_t3_nodes": pending}
