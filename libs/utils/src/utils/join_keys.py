"""The rule of a join's keys, written once (JOIN-KEY-ONE-1, Eve 2026-11-15, ADR-102).

A join keeps the types the tables have (JOIN-KEY-TYPES-1). It cannot be built when the two lists of key columns differ
in length, when a key column does not exist, or when the two columns of a pair have different types. The build
(DataAssembler._check_join_key_types), the Blueprint preview (blueprint_arch.join_designer.check_join_keys) and the
checker (utils.recipe_check, J11, J10, J09) all ask this module, so they cannot disagree; each one phrases the problem for
its own reader and keeps what is its own (the build raises, the preview returns rows, the checker adds its code).

Pure: column names and types in, a plain dictionary out. A type is whatever the caller compares with `==` (a Polars dtype, a
dtype name); `None` means "not known here" and a pair with an unknown type is never a difference (the checker, which reads
declarations, does not always know a type). No import from another library of the repository.

Consumed by: libs/transformer/src/transformer/data_assembler.py, libs/blueprint_arch/src/blueprint_arch/join_designer.py,
libs/utils/src/utils/recipe_check.py.
If deleted: the three callers stop giving one verdict for the same join.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from utils import action_names

# @deps
# provides: function:join_key_problem, function:key_length_problem, function:anti_join_with_itself, function:anti_join_with_itself_text, constant:JOIN_KEEPS_COLUMNS
# consumed_by: libs/transformer/src/transformer/data_assembler.py, libs/blueprint_arch/src/blueprint_arch/join_designer.py, libs/utils/src/utils/recipe_check.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-102
# @end_deps


# Tier-1 actions that only remove or reorder rows: they cannot change the columns or their types (exact names).
JOIN_KEEPS_COLUMNS = frozenset({action_names.FILTER, action_names.SORT, action_names.UNIQUE, action_names.DROP_NULLS, action_names.SAMPLE})

# A join of these kinds keeps every row of its left table (or removes some): the keys of the result are keys of the left table.
_KEEPS_LEFT_KEYS = ("left", "inner", "semi", "anti")

# Steps that only remove, reorder or pick rows of the table: it stays the same table for the rule of a self-join.
ROW_STEPS = JOIN_KEEPS_COLUMNS | {action_names.HEAD, action_names.TAIL, action_names.SLICE, action_names.LIMIT,
                                  action_names.GATHER_EVERY, action_names.REMOVE, action_names.TOP_K, action_names.BOTTOM_K}


def key_length_problem(left_keys: Sequence[str], right_keys: Sequence[str], *, empty_is_problem: bool = False) -> Optional[Dict[str, Any]]:
    """{"kind": "length", ...} when the two key lists have different lengths, else None.

    empty_is_problem: two empty lists are a problem too. The preview says so (picking no column is no join); the build and
    the checker accept them (a join without key columns, such as a cross join, has none).
    """
    left_keys, right_keys = list(left_keys), list(right_keys)
    if len(left_keys) != len(right_keys) or (empty_is_problem and not left_keys):
        return {"kind": "length", "left_keys": left_keys, "right_keys": right_keys}
    return None


def join_key_problem(left_types: Mapping[str, Any], right_types: Mapping[str, Any], left_keys: Sequence[str], right_keys: Sequence[str],
                     *, empty_is_problem: bool = False) -> Optional[Dict[str, Any]]:
    """The first problem of a join on these keys, in the order length, missing, type; None when it can be built.

    left_types / right_types: {column name: type} of the left table (the table at this step) and of the right table.
    left_keys / right_keys: the key columns, paired by position.

    Returns None, or one of
      {"kind": "length", "left_keys", "right_keys"}
      {"kind": "missing", "missing_left": [...], "missing_right": [...]}
      {"kind": "type", "pairs": [{"left_column", "right_column", "left_type", "right_type", "same"}, ...], "differing": [the pairs with same False]}
    """
    length = key_length_problem(left_keys, right_keys, empty_is_problem=empty_is_problem)
    if length:
        return length
    left_keys, right_keys = list(left_keys), list(right_keys)
    missing_left = [c for c in left_keys if c not in left_types]
    missing_right = [c for c in right_keys if c not in right_types]
    if missing_left or missing_right:
        return {"kind": "missing", "missing_left": missing_left, "missing_right": missing_right}
    pairs: List[Dict[str, Any]] = []
    for left_col, right_col in zip(left_keys, right_keys):
        left_type, right_type = left_types[left_col], right_types[right_col]
        pairs.append({"left_column": left_col, "right_column": right_col, "left_type": left_type, "right_type": right_type,
                      "same": left_type is None or right_type is None or left_type == right_type})
    differing = [p for p in pairs if not p["same"]]
    if differing:
        return {"kind": "type", "pairs": pairs, "differing": differing}
    return None


def _keys_of(step: Mapping[str, Any]) -> tuple:
    """(left keys, right keys) of a join step as lists; an unquoted `on` (the key True) is read like the checker reads it."""
    on = step.get("on", step.get(True))
    left, right = (on, on) if on is not None else (step.get("left_on"), step.get("right_on"))
    return ([left] if isinstance(left, str) else list(left or [])), ([right] if isinstance(right, str) else list(right or []))


def _writes_a_key(step: Mapping[str, Any], keys: Sequence[str]) -> bool:
    """True when `step` (with_columns or rename) writes or renames one of `keys`, or its parameter has a form that cannot be read."""
    if step.get("action") == action_names.WITH_COLUMNS:
        named = step.get("named_exprs")
        return not isinstance(named, Mapping) or bool(set(named) & set(keys))
    mapping = step.get("mapping")
    if not isinstance(mapping, Mapping):
        return True
    return bool((set(mapping) | {v for v in mapping.values() if isinstance(v, str)}) & set(keys))


def anti_join_with_itself(base_id: str, earlier_steps: Sequence[Any], step: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """{"table", "keys"} when `step` is the anti-join of the base table with itself on the same key, else None (D-0078).

    `how: anti` keeps the rows of the left table whose key is not found in the right table. When the right table is the
    base table itself and the keys are the same on both sides, every row that has a key finds itself, so no such row
    remains (a row whose key is empty is not found anywhere and stays). The left table is still "the base table itself"
    when every step before only removes, reorders or picks rows (a filter, a sort, `polars_head`, `polars_remove` ...),
    writes OTHER columns (`polars_with_columns`, `polars_rename` of another column), or joins a table with a kind of join
    that keeps the left keys (left, inner, semi, anti; the default of `polars_join` is left). After a step that writes or
    renames a key column, a full or right join, or a step this rule cannot read, the left table may hold other keys:
    the rule says nothing and the case is "every other self-join" (the checker advises, J12). A non-step before returns None.
    """
    if step.get("action") != action_names.JOIN or step.get("how") != "anti" or step.get("right_ingredient") != base_id:
        return None
    left_keys, right_keys = _keys_of(step)
    if not left_keys or left_keys != right_keys:
        return None
    for before in earlier_steps:
        if not isinstance(before, Mapping):
            return None
        action = before.get("action")
        if action == action_names.JOIN:
            if before.get("how", "left") not in _KEEPS_LEFT_KEYS:
                return None
        elif action in (action_names.WITH_COLUMNS, action_names.RENAME):
            if _writes_a_key(before, left_keys):
                return None
        elif action not in ROW_STEPS:
            return None
    return {"table": base_id, "keys": left_keys}


def anti_join_with_itself_text(found: Mapping[str, Any]) -> tuple:
    """(what happens, the suggestion) for the case that `anti_join_with_itself` returned; one text for the checker and the build."""
    table, keys = found["table"], found["keys"]
    what = (f"The join of {table!r} with itself on the same key {keys} with how 'anti' keeps the rows whose key is not found in {table!r}, "
            f"and every row that has a key finds itself, so the result has no row that has a key")
    fix = (f"Suggestion: remove the step if you did not mean this. "
           f"Suggestion: to find the rows of {table!r} that have no partner in another table, write that other table as right_ingredient.")
    return what, fix
