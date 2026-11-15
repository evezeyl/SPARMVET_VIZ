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

# @deps
# provides: function:join_key_problem, function:key_length_problem
# consumed_by: libs/transformer/src/transformer/data_assembler.py, libs/blueprint_arch/src/blueprint_arch/join_designer.py, libs/utils/src/utils/recipe_check.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-102
# @end_deps


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
