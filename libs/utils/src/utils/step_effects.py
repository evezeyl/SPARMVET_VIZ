# engine: python-polars (what each Polars action writes or keeps, by action name and join kind)
"""What the lineage walk may read from a step itself: the closed list of D-0351, in one place (LBFB step 0c, limited).

The owner decided (D-0351): besides the engine's plan, the walk may read "a short fixed list of what a step itself writes" and check each reading
against the plan: "each reading is checked against the engine's plan; when they disagree the column is shown grey with the reason, never guessed". On
2026-11-20 she added that the walk may read the column NAMES a compute step, a group-by and a cast write, never the formula. The list is EXACTLY:

1. the mapping of a rename (`polars_rename`: `mapping`);
2. the keys, the kind and the suffix of a join (`polars_join`: `right_ingredient`, `on`, `left_on`, `right_on`, `how`, `suffix`);
3. the columns of a drop (`polars_drop`: `columns`);
4. the columns of a select (`polars_select`: `exprs`, plain column names only);
5. the names a compute step writes (`polars_with_columns`: the keys of `named_exprs`, never the formulas);
6. the columns of a cast (`polars_cast`: `columns`; the type it gives is never read: the plan shows it);
7. the group columns and the names of the aggregates of a group-by (`polars_group_by`: `by` and the keys of `named_aggs`, never the aggregations).

`READINGS` is that list; a test fails when it holds anything else. A step outside it is `unread`: the walk knows only what the plan shows across it
(PROVISIONAL, see `lineage_walk`). A column that a read step does NOT name is untouched by it (reading and plan agree): it passes with no note and is
never grey for that step. A column that a step names and that already existed is the same column with its values or type changed (D-0353, D-0337):
the link is marked `recompute`, `cast` or `aggregate`, and a group column `group_key`; the walk follows it and puts the fact on the line as a note (data only).
What the walk can and cannot know there: it knows the step writes that NAME and the types before and after (from the plan); it cannot know whether the new
values come from the same column or from another one, because only names are read, never the formula (D-0356). That is the PROVISIONAL part: the link
says so (the note carries `knows_source_of_values` False).

`READINGS` is the ONE source of what is read: `effect_of` reads an action only when it is a key of `READINGS` (or a row step), and a test proves that
every registered action outside the two is `unread`.

The actions that only remove, reorder or pick rows (`join_keys.ROW_STEPS`) need no reading of their arguments: the name of
the action says that the columns stay. They are imported, never copied.

A join is read only for `how` = left or inner (the kinds shipped recipes use); any other kind (full, right, semi, anti,
cross, as-of, on conditions) is `unread` (PROVISIONAL: grey with the reason; the owner's question O8).

Pure: step dictionaries and plans in, small records out. No Polars, no file, no engine.

Consumed by: libs/utils/src/utils/lineage_walk.py, libs/utils/tests/test_step_effects.py.
If deleted: the walk cannot follow a column across a step.

# @deps
# provides: function:effect_of, function:predict, function:agreement_problem, function:unread_pairs, class:Effect, class:PredictedColumn, class:Source, constant:READINGS, constant:FOLLOWED_JOINS, constant:VALUE_CHANGES, constant:NOTE_CHANGES
# consumes: libs/utils/src/utils/join_keys.py, libs/utils/src/utils/action_names.py, libs/utils/src/utils/plan_book.py
# consumed_by: libs/utils/src/utils/lineage_walk.py, libs/utils/src/utils/declared_plans.py, libs/utils/tests/test_step_effects.py, libs/utils/tests/test_lineage_walk_follow.py
# doc: .claude/knowledge/decision_ledger.md (D-0351, D-0353, D-0356, D-0357), .claude/design/home_audit_steps.md
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, List, Mapping, Optional, Sequence, Tuple

from utils import action_names, join_keys
from utils.plan_book import Plan

# The closed list: action -> the arguments the walk may read from it (D-0351). One place.
READINGS: Dict[str, Tuple[str, ...]] = {
    action_names.RENAME: ("mapping",),
    action_names.JOIN: ("right_ingredient", "on", "left_on", "right_on", "how", "suffix"),
    action_names.DROP: ("columns",),
    action_names.SELECT: ("exprs",),
    action_names.WITH_COLUMNS: ("named_exprs",),
    action_names.CAST: ("columns",),
    action_names.GROUP_BY: ("by", "named_aggs"),
}

# The kinds of join the readings follow (PROVISIONAL, O8): the others are `unread`.
FOLLOWED_JOINS = ("left", "inner")

KEEPS, RENAME, DROP, SELECT, JOIN, WRITES, CAST, GROUP, UNREAD = "keeps", "rename", "drop", "select", "join", "writes", "cast", "group", "unread"

# What a changed name is, for a link that is not the same name (the walk follows these: the hop says which).
CHANGE_RENAME, CHANGE_KEY_OTHER_NAME, CHANGE_SUFFIX = "rename", "key_other_name", "suffix"
# What a step that writes a column of the same name changes: its values (a compute step), its type (a cast), its meaning (an aggregate); a group key keeps
# its values but the rows after the step are the groups.
CHANGE_RECOMPUTE, CHANGE_CAST, CHANGE_AGGREGATE, CHANGE_GROUP_KEY = "recompute", "cast", "aggregate", "group_key"
VALUE_CHANGES = (CHANGE_RECOMPUTE, CHANGE_CAST, CHANGE_AGGREGATE)       # the plan decides the type of the column (its values or type are written by the step)
NOTE_CHANGES = VALUE_CHANGES + (CHANGE_GROUP_KEY,)                      # the changes that are a note under the line


@dataclass(frozen=True)
class Effect:
    """One step as the walk reads it. `kind` is keeps, rename, drop, select, join or unread; `why` says why a step is unread."""
    kind: str
    action: str
    pairs: Tuple[Tuple[str, str], ...] = ()      # rename: (old name, new name)
    columns: Tuple[str, ...] = ()                # drop, select, cast; the group columns of a group-by
    written: Tuple[str, ...] = ()                # the names a compute step or a group-by writes
    left_keys: Tuple[str, ...] = ()              # join
    right_keys: Tuple[str, ...] = ()
    how: str = ""
    suffix: str = ""
    right: str = ""                              # the table id the join reads (`right_ingredient`)
    why: str = ""


@dataclass(frozen=True)
class Source:
    """Where a predicted column comes from: `left` is the table at this step, `right` the table a join reads."""
    side: str
    name: str


@dataclass(frozen=True)
class PredictedColumn:
    """A column after the step. `sources` is one source, or two for a join key that both sides equate; `change` is None when the name is
    the source's name, else why it differs (rename, key under another name, suffix of a clash)."""
    name: str
    sources: Tuple[Source, ...]                  # empty: the column is made by the step (it has no source column)
    change: Optional[str] = None


def _plain_names(value: Any) -> Optional[Tuple[str, ...]]:
    """A list of plain column names, or None. A name that holds a space, a dot or a bracket is an expression, not a name; `*` and
    a `^...$` pattern select by pattern."""
    if not isinstance(value, list) or not value or not all(isinstance(v, str) and v for v in value):
        return None
    for v in value:
        if v == "*" or (v.startswith("^") and v.endswith("$")) or any(ch in v for ch in " .()\t") or v.startswith("pl."):
            return None
    return tuple(value)


def effect_of(step: Any) -> Effect:
    """Read one step. A step the list does not cover, or whose arguments cannot be read, is `unread` with the reason."""
    action = step.get("action") if isinstance(step, Mapping) else None
    if not isinstance(action, str):
        return Effect(UNREAD, "", why="the step has no action name")
    if action in join_keys.ROW_STEPS:
        return Effect(KEEPS, action)
    if action not in READINGS:                                                   # READINGS is the one source of what is read
        return Effect(UNREAD, action, why=f"the walk may not read the action {action} yet")
    if action == action_names.RENAME:
        mapping = step.get("mapping")
        if isinstance(mapping, Mapping) and mapping and all(isinstance(k, str) and isinstance(v, str) for k, v in mapping.items()):
            return Effect(RENAME, action, pairs=tuple((k, v) for k, v in mapping.items()))
        return Effect(UNREAD, action, why="the rename mapping is not a plain mapping of names")
    if action in (action_names.DROP, action_names.SELECT):
        names = _plain_names(step.get("columns" if action == action_names.DROP else "exprs"))
        if names is None:
            return Effect(UNREAD, action, why="the columns are not a list of plain column names")
        return Effect(DROP if action == action_names.DROP else SELECT, action, columns=names)
    if action == action_names.WITH_COLUMNS:
        named = step.get("named_exprs")
        if isinstance(named, Mapping) and named and all(isinstance(k, str) and k for k in named):
            return Effect(WRITES, action, written=tuple(named))
        return Effect(UNREAD, action, why="named_exprs is not a mapping of column names")
    if action == action_names.CAST:
        names = _plain_names(step.get("columns"))
        return Effect(CAST, action, columns=names) if names else Effect(UNREAD, action, why="the columns are not a list of plain column names")
    if action == action_names.GROUP_BY:
        by, aggs = _plain_names(step.get("by")), step.get("named_aggs", {})
        if by is None or "named_by" in step or not isinstance(aggs, Mapping) or not all(isinstance(k, str) and k for k in aggs):
            return Effect(UNREAD, action, why="the group columns or the named aggregates cannot be read as names")
        return Effect(GROUP, action, columns=by, written=tuple(aggs))
    if action == action_names.JOIN:
        how, right = step.get("how", "left"), step.get("right_ingredient")
        if how not in FOLLOWED_JOINS:
            return Effect(UNREAD, action, why=f"a join of kind {how!r} is not followed yet")
        left_keys, right_keys = join_keys.key_columns(step)
        if not isinstance(right, str) or not left_keys or len(left_keys) != len(right_keys):
            return Effect(UNREAD, action, why="the join has no readable key columns or no right table")
        return Effect(JOIN, action, left_keys=tuple(left_keys), right_keys=tuple(right_keys), how=how, suffix=join_keys.suffix_of(step), right=right)
    raise AssertionError(f"READINGS lists {action} but effect_of has no reading for it")      # a listed action without a reading is a bug of this module, never a silent unread


def predict(effect: Effect, before: Plan, right: Optional[Plan]) -> Tuple[PredictedColumn, ...]:
    """The columns after a read step, from the columns before (and the right table's, for a join). Polars semantics, stated once:
    a rename is simultaneous; a select keeps the order written; a left or inner join keeps the table's columns, merges each right key into
    its left key, and copies the other right columns, with the suffix when the table at this step already has the name."""
    left = [Source("left", n) for n in before.names]
    if effect.kind == KEEPS:
        return tuple(PredictedColumn(n, (Source("left", n),)) for n in before.names)
    if effect.kind == RENAME:
        mapping = dict(effect.pairs)
        return tuple(PredictedColumn(mapping.get(n, n), (Source("left", n),), CHANGE_RENAME if mapping.get(n, n) != n else None) for n in before.names)
    if effect.kind == DROP:
        gone = set(effect.columns)
        return tuple(PredictedColumn(n, (Source("left", n),)) for n in before.names if n not in gone)
    if effect.kind == SELECT:
        return tuple(PredictedColumn(n, (Source("left", n),)) for n in effect.columns if before.has(n))
    if effect.kind == WRITES:
        written = set(effect.written)
        kept = [PredictedColumn(n, (Source("left", n),), CHANGE_RECOMPUTE if n in written else None) for n in before.names]
        return tuple(kept) + tuple(PredictedColumn(n, ()) for n in effect.written if not before.has(n))
    if effect.kind == CAST:
        cast_names = set(effect.columns)
        return tuple(PredictedColumn(n, (Source("left", n),), CHANGE_CAST if n in cast_names else None) for n in before.names)
    if effect.kind == GROUP:
        grouped = [PredictedColumn(n, (Source("left", n),), CHANGE_GROUP_KEY) for n in effect.columns if before.has(n)]
        aggregated = [PredictedColumn(n, (Source("left", n),), CHANGE_AGGREGATE) if before.has(n) and n not in effect.columns else PredictedColumn(n, ())
                      for n in effect.written if n not in effect.columns]
        return tuple(grouped) + tuple(aggregated)
    assert effect.kind == JOIN and right is not None
    keys = dict(zip(effect.right_keys, effect.left_keys))              # right key -> left key
    merged: Dict[str, str] = {lk: rk for rk, lk in keys.items()}      # left key -> right key
    out: List[PredictedColumn] = []
    for source in left:
        rk = merged.get(source.name)
        if rk is not None and right.has(rk):
            out.append(PredictedColumn(source.name, (source, Source("right", rk)), CHANGE_KEY_OTHER_NAME if rk != source.name else None))
        else:
            out.append(PredictedColumn(source.name, (source,)))
    taken = set(before.names)
    for name in right.names:
        if name in keys:
            continue
        renamed = name + effect.suffix if name in taken else name
        out.append(PredictedColumn(renamed, (Source("right", name),), CHANGE_SUFFIX if renamed != name else None))
    return tuple(out)


def agreement_problem(effect: Effect, predicted: Sequence[PredictedColumn], before: Plan, right: Optional[Plan], actual: Plan) -> Optional[str]:
    """None when the prediction equals the engine's plan after the step (the same names, and for every column the type its source has);
    else one plain sentence saying where they differ. A join whose key columns are missing is a problem too."""
    if effect.kind == JOIN:
        assert right is not None
        absent = [k for k in effect.left_keys if not before.has(k)] + [k for k in effect.right_keys if not right.has(k)]
        if absent:
            return f"the join names key columns {absent} that the tables do not have"
    names = [p.name for p in predicted]
    if len(set(names)) != len(names):
        return "the reading gives one name to two columns"
    if set(names) != set(actual.names):
        missing, extra = sorted(set(names) - set(actual.names)), sorted(set(actual.names) - set(names))
        return f"the reading expects the columns {missing} that the plan does not have and the plan has {extra} that the reading does not expect"
    if effect.kind in (CAST, GROUP) and any(not before.has(n) for n in effect.columns):
        return f"the step names columns {[n for n in effect.columns if not before.has(n)]} that the table does not have"
    for p in predicted:
        if not p.sources or p.change in VALUE_CHANGES:               # made by the step, or a column whose values or type the step writes: the plan decides
            continue
        first = p.sources[0]
        expected = (before if first.side == "left" else right).type_of(first.name)  # type: ignore[union-attr]
        if actual.type_of(p.name) != expected:
            return f"the column {p.name!r} has the type {actual.type_of(p.name)} in the plan and the reading expects {expected}"
    return None


def unread_pairs(before: Plan, after: Plan) -> Tuple[Tuple[str, ...], Tuple[str, ...], Tuple[str, ...], Tuple[str, ...]]:
    """What the plan alone shows across a step the walk may not read: (names kept with the same type, names kept with another type,
    names that vanished, names that appeared). Only the plan: nothing is said of what the step did to the values."""
    kept = tuple(n for n in before.names if after.has(n) and after.type_of(n) == before.type_of(n))
    retyped = tuple(n for n in before.names if after.has(n) and after.type_of(n) != before.type_of(n))
    vanished = tuple(n for n in before.names if not after.has(n))
    created = tuple(n for n in after.names if not before.has(n))
    return kept, retyped, vanished, created
