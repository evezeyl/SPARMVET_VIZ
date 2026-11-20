"""The rule of a join's keys, written once (JOIN-KEY-ONE-1, Eve 2026-11-15, ADR-102).

A join keeps the types the tables have (JOIN-KEY-TYPES-1). It cannot be built when the two lists of key columns differ
in length, when a key column does not exist, or when the two columns of a pair have different types. The build
(DataAssembler._check_join_key_types), the Blueprint preview (blueprint_arch.join_designer.check_join_keys) and the
checker (utils.recipe_check, J11, J10, J09) all ask this module, so they cannot disagree; each one phrases the problem for
its own reader and keeps what is its own (the build raises, the preview returns rows, the checker adds its code).

A self-join (a join whose right table is, or is already held by, the table being joined) is never an error (D-0183): `self_join`
finds it and `self_join_text` writes what it does, for the checker (J12, before any data is read) and for the build (with the
row numbers). Pure: column names and types in, a plain dictionary out. A type is whatever the caller compares with `==` (a Polars dtype, a
dtype name); `None` means "not known here" and a pair with an unknown type is never a difference (the checker, which reads
declarations, does not always know a type). No import from another library of the repository.

Consumed by: libs/transformer/src/transformer/data_assembler.py, libs/blueprint_arch/src/blueprint_arch/join_designer.py,
libs/utils/src/utils/recipe_check.py.
If deleted: the three callers stop giving one verdict for the same join.
"""
from __future__ import annotations

from typing import Any, Dict, List, Mapping, Optional, Sequence

from utils import action_names, recipe_tiers

# @deps
# provides: function:recipe_join_keys, function:join_key_problem, function:key_length_problem, function:self_join, function:self_join_text, function:key_columns, function:suffix_of, constant:JOIN_KEEPS_COLUMNS, constant:JOIN_ACTIONS, constant:ROW_STEPS
# consumed_by: libs/transformer/src/transformer/data_assembler.py, libs/blueprint_arch/src/blueprint_arch/join_designer.py, libs/utils/src/utils/recipe_check.py, libs/utils/src/utils/step_effects.py (suffix_of, key_columns, ROW_STEPS)
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


def _listed(value: Any) -> list:
    """A key parameter as a list: a name becomes [name], nothing becomes [], a list is copied, anything else is kept as one item."""
    if value is None:
        return []
    return [value] if isinstance(value, str) else list(value) if isinstance(value, (list, tuple)) else [value]


def _keys_of(step: Mapping[str, Any]) -> tuple:
    """(left keys, right keys) of a join step as lists; an unquoted `on` (the key True) is read like the checker reads it."""
    on = step.get("on", step.get(True))
    left, right = (on, on) if on is not None else (step.get("left_on"), step.get("right_on"))
    return _listed(left), _listed(right)


def _writes_a_key(step: Mapping[str, Any], keys: Sequence[str]) -> bool:
    """True when `step` (with_columns or rename) writes or renames one of `keys`, or its parameter has a form that cannot be read."""
    if step.get("action") == action_names.WITH_COLUMNS:
        named = step.get("named_exprs")
        return not isinstance(named, Mapping) or bool(set(named) & set(keys))
    mapping = step.get("mapping")
    if not isinstance(mapping, Mapping):
        return True
    return bool((set(mapping) | {v for v in mapping.values() if isinstance(v, str)}) & set(keys))


def _left_is_base_itself(earlier_steps: Sequence[Any], left_keys: Sequence[str]) -> bool:
    """True when the table at a step is still the base table itself, as far as the key columns go.

    It is, when every step before only removes, reorders or picks rows (a filter, a sort, `polars_head`, `polars_remove` ...),
    writes OTHER columns (`polars_with_columns`, `polars_rename` of another column), or joins a table with a kind of join
    that keeps the left keys (left, inner, semi, anti; the default of `polars_join` is left). After a step that writes or
    renames a key column, a full or right join, or a step this rule cannot read, the left table may hold other keys.
    """
    for before in earlier_steps:
        if not isinstance(before, Mapping):
            return False
        action = before.get("action")
        if action == action_names.JOIN:
            if before.get("how", "left") not in _KEEPS_LEFT_KEYS:
                return False
        elif action in (action_names.WITH_COLUMNS, action_names.RENAME):
            if _writes_a_key(before, left_keys):
                return False
        elif action not in ROW_STEPS:
            return False
    return True


def _as_names(value: Any) -> Optional[List[str]]:
    """A key parameter as a list of column names; None when it holds something that is not a name."""
    names = _listed(value)
    return names if all(isinstance(n, str) for n in names) else None


def key_columns(step: Mapping[str, Any]) -> tuple:
    """(left columns, right columns) of every key group of a join step: `on` or `left_on` / `right_on`, and the `by` groups of an as-of join.

    A join on conditions has none. A column that is not a text (a step that cannot be read) gives ([], []).
    """
    left, right = _keys_of(step)
    by = step.get("by")
    by_left, by_right = (by, by) if by is not None else (step.get("by_left"), step.get("by_right"))
    parts = [_as_names(x) for x in (left, right, by_left, by_right)]
    if any(p is None for p in parts):
        return [], []
    return parts[0] + parts[2], parts[1] + parts[3]


def suffix_of(step: Mapping[str, Any]) -> str:
    """The suffix a join gives a right-table column whose name the table at this step already has: the step's `suffix`, else `_right`
    (the Polars default). The one place the default is written (the self-join text and the lineage walk both ask it)."""
    return step.get("suffix") or "_right"


# Join steps that name a right table (the as-of join and the join on conditions are joins too).
JOIN_ACTIONS = (action_names.JOIN, action_names.JOIN_ASOF, action_names.JOIN_WHERE)

_LABEL = {action_names.JOIN: "a join", action_names.JOIN_ASOF: "an as-of join", action_names.JOIN_WHERE: "a join on conditions"}


def self_join(base_id: str, earlier_steps: Sequence[Any], step: Mapping[str, Any]) -> Optional[Dict[str, Any]]:
    """The facts of a self-join, or None. One rule for the checker (J12) and the build (D-0183, Eve 2026-11-16).

    A self-join is a join step (`polars_join`, `polars_join_asof`, `modif_join_where`) whose right table is, or is already
    held by, the table being joined: the first table of the join (`base_id`) or a table joined by an earlier step. Polars
    reports nothing for it and it is never an error; the user is told what it does.

    Returns {"table", "is_base", "action", "how", "left_keys", "right_keys", "same_key", "nulls_equal", "suffix", "base_itself", "key_columns"}:
      same_key     the key columns are the same, in the same order, on both sides (and there is at least one)
      base_itself  the table is the first table, and the table at this step still has its keys (only rows removed, other
                   columns written, or joined with a join that keeps the left keys): then the key columns are the keys of
                   the table itself and `how: anti` on the same key has the one result `self_join_text` states
      key_columns  (left, right): every key column, `by` of an as-of join included (for the count of missing keys)
    """
    action = step.get("action")
    right_id = step.get("right_ingredient")
    if action not in JOIN_ACTIONS or not isinstance(right_id, str):
        return None
    left_keys, right_keys = _keys_of(step)
    if _as_names(left_keys) is None or _as_names(right_keys) is None:
        return None
    left_tables = [base_id]
    for before in earlier_steps:
        if isinstance(before, Mapping) and isinstance(before.get("right_ingredient"), str):
            left_tables.append(before["right_ingredient"])
    if right_id not in left_tables:
        return None
    same_key = bool(left_keys) and left_keys == right_keys
    return {
        "table": right_id, "action": action, "how": step.get("how", "left" if action == action_names.JOIN else None),
        "left_keys": left_keys, "right_keys": right_keys, "same_key": same_key, "nulls_equal": bool(step.get("nulls_equal")),
        "suffix": suffix_of(step), "key_columns": key_columns(step), "is_base": right_id == base_id,
        "base_itself": action == action_names.JOIN and right_id == base_id and same_key and _left_is_base_itself(earlier_steps, left_keys),
    }


def _times(table: str) -> str:
    return (f"A key value that appears a times in the table at this step and b times in {table!r} gives a x b rows")


def _left(table: str, nulls_equal: bool, suffix: str) -> str:
    gone = ("a missing key matches a missing key like any other value" if nulls_equal
            else "a row with a missing key is kept once, with empty copied columns")
    return f"{_times(table)}, and {gone}; the columns are copied with the suffix `{suffix}`"


def _inner(table: str, nulls_equal: bool, suffix: str) -> str:
    gone = ("a missing key matches a missing key like any other value" if nulls_equal else "a row with a missing key is dropped")
    return f"{_times(table)}, and {gone}; the columns are copied with the suffix `{suffix}`"


def _right(table: str, nulls_equal: bool, suffix: str) -> str:
    gone = ("a missing key matches a missing key like any other value" if nulls_equal
            else f"a row of {table!r} with a missing key is kept once, with empty columns for the table at this step")
    return f"{_times(table)}, and {gone}; the columns are copied with the suffix `{suffix}`"


def _full(table: str, nulls_equal: bool, suffix: str) -> str:
    gone = ("a missing key matches a missing key like any other value" if nulls_equal
            else "a row with a missing key is kept once from each side, with empty columns for the other side")
    return f"{_times(table)}, and {gone}; the columns are copied with the suffix `{suffix}`"


def _semi(table: str, nulls_equal: bool, suffix: str) -> str:
    gone = ("a missing key matches a missing key, so every row stays" if nulls_equal else "a row with a missing key is dropped")
    return f"No column is copied; each row whose key is found in {table!r} stays once, and {gone}"


def _anti(table: str, nulls_equal: bool, suffix: str) -> str:
    kept = ("a missing key matches a missing key, so such a row is removed" if nulls_equal else "a row with a missing key is kept")
    return f"No column is copied; it removes the rows whose key is found in {table!r}, and {kept}"


# What a join on the same key does, by kind of join (checked against real runs: libs/transformer/tests/test_self_join_build.py)
_SAME_KEY_RESULT = {"left": _left, "inner": _inner, "right": _right, "full": _full, "semi": _semi, "anti": _anti}


def self_join_text(found: Mapping[str, Any], counts: Optional[Mapping[str, Any]] = None) -> tuple:
    """(what happens, the suggestions) for a self-join that `self_join` found. One text for the checker and the build.

    The message holds no remedy; every suggestion starts with "Suggestion:". How the two are joined into one sentence, with one
    period, is `utils.fix_text.with_fix`, the same for every reader.
    `counts` (the build only, where the data is known): {"before", "after", "missing_left", "missing_right"} - the number of
    rows before and after the join and of rows with a missing key in the key columns, in the left table and in the right
    table (None when the join has no key columns). They are added as a last sentence.
    """
    table, how, label = found["table"], found["how"], _LABEL[found["action"]]
    keys, same, nulls_equal = found["left_keys"], found["same_key"], found["nulls_equal"]
    remove = "Suggestion: remove the step if you did not mean this."
    if found["base_itself"] and how == "anti":
        if nulls_equal:
            what = (f"The join of {table!r} with itself on the same key {keys} with how 'anti' keeps no row, "
                    f"because every row finds itself, a missing key included (nulls_equal)")
        else:
            what = (f"The join of {table!r} with itself on the same key {keys} with how 'anti' keeps only the rows whose key is missing, "
                    f"because a missing key never matches. If no row has a missing key, the result is empty")
        fix = (f"{remove} Suggestion: to find the rows of {table!r} that have no partner in another table, write that other table as right_ingredient.")
    elif same and found["action"] == action_names.JOIN and how in _SAME_KEY_RESULT:
        head = (f"Join of {table!r} with itself on the same column ({', '.join(map(repr, keys))}) with how '{how}'" if found["is_base"]
                else f"This step joins {table!r} to a table that already holds it, on the same key {keys}, with how '{how}'")
        what = head + ". " + _SAME_KEY_RESULT[how](table, nulls_equal, found["suffix"])
        fix = remove
    else:
        has_keys = bool(found["key_columns"][0])
        if not has_keys:
            on = ""
        elif same:
            on = f", on the same key {keys}"
        else:
            on = f", with the left key {found['left_keys']} and the right key {found['right_keys']}"
        kind = f", with how {how!r}" if how else ""
        missing = ("" if not has_keys else "; a row whose key is missing matches rows whose key is missing (nulls_equal)" if nulls_equal
                   else "; a row whose key is missing never matches")
        what = (f"This step is {label} of {table!r} with a table that already holds it{on}{kind}. "
                f"Each row is matched with rows of the same table, which answers a real question (a parent and a child column, for example) "
                f"and is a mistake if you meant another table{missing}")
        fix = f"{remove} Suggestion: if you meant another table, write that table as right_ingredient."
    if counts is not None:
        what += ". " + _counts_sentence(found, counts, table)
    return what, fix


def _counts_sentence(found: Mapping[str, Any], counts: Mapping[str, Any], table: str) -> str:
    """The numbers of the build: rows before and after, and the rows whose key is missing (never matched)."""
    sentence = f"Rows before the join: {counts['before']}; rows after: {counts['after']}"
    if counts.get("missing_left") is not None:
        columns = found["key_columns"][0]
        sentence += (f"; rows with a missing key in {columns}: {counts['missing_left']} in the table at this step and "
                     f"{counts['missing_right']} in {table!r}")
        sentence += " (they find themselves a partner only with nulls_equal)" if found["nulls_equal"] else " (a missing key never matches)"
    return sentence


# ---------------------------------------------------------------------------------------------------------------------
# The join keys and the declared keys of a recipe (the warning of a filter on a key; the drop of a key is judged by place in `utils.key_drop`, D-0358)
# ---------------------------------------------------------------------------------------------------------------------


def recipe_join_keys(raw: Any) -> List[str]:
    """The union of every join-key column of every join step of `joins.*.tier1` and `joins.*.tier2` (the steps they run), sorted (the rule of ADR-049,
    12g.2: true keys such as `sample_id` and accessory keys of long tables such as `gene_id`). Only a join step names join keys: the `on` of an unpivot
    or a group step names columns that are not keys. The HOME audit asks the same question through `app.modules.session_manager.extract_primary_keys`; a test
    holds the two equal on every shipped recipe (that file is not edited here, so the walk is written once more, on the same `key_columns` and
    `JOIN_ACTIONS`)."""
    keys: set = set()
    joins = raw.get("joins") if isinstance(raw, dict) else None
    for join in joins.values() if isinstance(joins, dict) else []:
        if not isinstance(join, dict):
            continue
        for step in recipe_tiers.step_list(join, "tier1") + recipe_tiers.step_list(join, "tier2"):
            if isinstance(step, dict) and step.get("action") in JOIN_ACTIONS:
                left, right = key_columns(step)
                keys.update(left)
                keys.update(right)
    return sorted(keys)
