"""The records the lineage walk returns (LBFB step 0a): plain frozen data, no behaviour but derived counts.

One `Walk` holds, for one column the user looks at, a record per place where a step could be written (`Line`), a record per
place of the reach where the column no longer exists (`Gone`, a note under the lines that reach it), the places that no plot
reads (`Unread`, counted apart) and the tables that hold the same key and were not reached (`Outside`). Sentences are never
built here: a reason or a note is a code with its parameters (the words are another pure function, built later, so the owner
can approve them apart from the logic).

Counts are derived from sets and tuples (`Reach.n_plots` is `len` of a set; `Walk.found` is the number of ticked lines),
never stored beside them, so two numbers cannot disagree (D-0195, D-0316).

Consumed by: libs/utils/src/utils/lineage_walk.py, libs/utils/tests/test_lineage_walk.py.
If deleted: the walk has nothing to return.

# @deps
# provides: class:Walk, class:Line, class:Gone, class:Unread, class:Outside, class:Occurrence, class:Hop, class:StepRef, class:SourceColumn, class:Reach, class:Reason, class:Note, class:Start, class:SortedSet, constant:GROUPS, constant:LEVELS, constant:HOW_VALUES, constant:REASON_CODES, constant:NOTE_CODES, constant:VALUE_NOTES
# consumed_by: libs/utils/src/utils/lineage_walk.py, libs/utils/tests/test_lineage_walk.py, libs/utils/tests/test_lineage_walk_follow.py
# doc: .claude/knowledge/decision_ledger.md (D-0346, D-0347, D-0195, D-0351, D-0353, D-0337, D-0357)
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, FrozenSet, Optional, Tuple


# The LEVELS the user chooses (owner, 2026-11-20, D-0355: "we have all_raw data, all T1, All T2, All T3 ... so we need to have a way to choose"): the
# source tables, the tables after tier 1, after tier 2, and what a plot reads after tier 3. The walk offers the places of the chosen levels (any combination)
# that hold the column in the lineage of the chosen place. A place that covers several tiers (an empty tier is not a place) belongs to each of them.
SOURCE, T1, T2, T3 = "source", "T1", "T2", "T3"
LEVELS = (SOURCE, T1, T2, T3)

# The GROUPS of places (the user ticks; which groups are offered is PROVISIONAL). A line, a note or a place no plot reads carries the smallest group that holds it:
LINEAGE = "lineage"          # above and below the chosen place: back to its sources, then forward from them (D-0347 as written)
JOIN_LINKED = "join_linked"  # also the tables a join on the same column links to it (the key of a join that both sides equate)
# There is no group for "the same key, no join links it" (owner, D-0355): a column is never matched by its name alone.
GROUPS = (LINEAGE, JOIN_LINKED)


def group_rank(group: str) -> int:
    return GROUPS.index(group)


# How a column got to a place. `unchanged` and `unknown` say only that the name and the type did not change, or that the walk cannot say; `renamed` is a rename, a key under
# another name or the suffix of a clash (the hop says which, with the name before and after); `cast`, `recomputed`, `aggregated` and `grouped` are a step that writes the
# column's type, its values, its meaning (an aggregate) or the rows it sits on (a group key); `created` and `re_created` are a column made by a step. `dropped` and `gone`
# are not produced (a column that is gone is a `Gone` note, not a line).
UNCHANGED, RENAMED, CREATED, RE_CREATED, UNKNOWN = "unchanged", "renamed", "created", "re_created", "unknown"
CAST, RECOMPUTED, AGGREGATED, GROUPED, DROPPED, GONE = "cast", "recomputed", "aggregated", "grouped", "dropped", "gone"
HOW_VALUES = (UNCHANGED, RENAMED, CAST, RECOMPUTED, AGGREGATED, GROUPED, DROPPED, RE_CREATED, CREATED, GONE, UNKNOWN)

# The reasons a line is grey: a closed list.
PLAN_FAILED = "plan_failed"                    # the engine could not give the plan here or above (its sentence is a parameter)
STEP_NOT_READ = "step_not_read"                # a step on the path is outside the list of readings and the plan cannot show the column unchanged
READING_DISAGREES = "reading_disagrees"        # a reading of D-0351 gives other columns than the plan (D-0351: grey, never guessed); both facts are in the reason
SEVERAL_COLUMNS = "several_columns"            # the column exists more than once here (a table joined with itself): which one a step names is not decided
CANNOT_FOLLOW = "cannot_follow"                # no trace could be made (a plan that disagrees with the one above)
NO_STEP_LIST = "no_step_list"                  # a source table holds no list of steps (D-0332): the line is returned, a step cannot be written there (PROVISIONAL)
REASON_CODES = (PLAN_FAILED, STEP_NOT_READ, READING_DISAGREES, SEVERAL_COLUMNS, CANNOT_FOLLOW, NO_STEP_LIST)

# The notes under a line: a closed list. They are DATA (a code and parameters: node, step, action, the names and the types before and after, the direction); the
# words the user reads are written later in their own module. `direction` says whether the path from the place the user chose crosses the step with the
# data (`forward`: the line is after the step) or against it (`backward`: the line is before the step).
NOTE_UNREAD_STEP_PASSED = "unread_step_passed"   # the plan shows the name and type unchanged across a step the walk may not read: values may have changed
NOTE_ANOTHER_TYPE = "another_type_here"          # a cast: the type before and after (D-0337)
NOTE_RECOMPUTED = "recomputed_here"              # a compute step writes the column under its own name (D-0353); `knows_source_of_values` is False: names only are read
NOTE_AGGREGATED = "aggregated_here"              # a group-by aggregate that keeps the name (D-0353); `knows_source_of_values` is False
NOTE_ONE_ROW_PER_GROUP = "one_row_per_group_after_this_step"   # a group-by key keeps its name; the rows after the step are the groups (D-0353)
VALUE_NOTES = (NOTE_ANOTHER_TYPE, NOTE_RECOMPUTED, NOTE_AGGREGATED, NOTE_ONE_ROW_PER_GROUP)
NOTE_CODES = (NOTE_UNREAD_STEP_PASSED,) + VALUE_NOTES

# Why a walk holds no line, no note and no place no plot reads (never a silent empty result, D-0195).
NO_PLACE_AT_THE_LEVELS = "no_place_at_the_chosen_levels"   # parameters: the chosen levels, the levels where the column exists in the lineage, the group

# Why a table is listed as not reached.
WHY_DECLARED_KEY_NOT_REACHED = "declared_key_not_reached"   # it declares the same key as the lineage holds, and no join links it: information, never a line
OUTSIDE_CODES = (WHY_DECLARED_KEY_NOT_REACHED,)

TICK, GREY = "tick", "grey"


class SortedSet(frozenset):
    """A frozen set that iterates, prints and lists in sorted order, whatever the hash seed of the process. Membership stays a set's. A caller that prints
    or iterates a reach gets the same text in every run (the same input gives the same output)."""

    def __iter__(self):
        return iter(sorted(frozenset.__iter__(self)))

    def __repr__(self) -> str:
        return "{" + ", ".join(repr(x) for x in self) + "}" if self else "SortedSet()"


@dataclass(frozen=True)
class Start:
    """The column the user looks at: the node (`T1:J`, `T2:J`, `T3:p`, `DS:S`) and the column's name at the END of that node."""
    node: str
    column: str


@dataclass(frozen=True)
class Reason:
    """Why a line is grey: a code of `REASON_CODES` and its parameters as (key, value) pairs in a fixed order."""
    code: str
    params: Tuple[Tuple[str, Any], ...] = ()

    def get(self, key: str, default: Any = None) -> Any:
        return next((v for k, v in self.params if k == key), default)


@dataclass(frozen=True)
class Note:
    """A fact under a line, as data (a code of `NOTE_CODES` and its parameters)."""
    code: str
    params: Tuple[Tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class StepRef:
    """One step of the recipe, identifiable: the node whose list holds it, its number in that list (1 is the first; the author's steps
    come first, then the audit steps), the action, the place in the recipe (`steps_path` and the number) and the step's own `id` when it has one."""
    node: str
    step: int
    action: str
    step_path: str
    step_id: Optional[str] = None


@dataclass(frozen=True)
class Hop:
    """A step the column passed on its way to a place, from its source to there. `how`: unchanged (by the plan, across a step the walk
    may not read), renamed, created, re_created or unknown. For a join step, `join_how` is the kind (left, inner) and `join_side` says
    whether the column came from the table at that step (`base`) or from the table the join reads (`right`)."""
    step: StepRef
    how: str
    name_before: Optional[str]
    name_after: str
    type_before: Optional[str]
    type_after: str
    join_how: Optional[str] = None
    join_side: Optional[str] = None


@dataclass(frozen=True)
class SourceColumn:
    """A column of a source file as the recipe declares it: the table id and the column's name there."""
    table: str
    name: str


@dataclass(frozen=True)
class Occurrence:
    """The column at a place, once: its name and engine type there, how it got there, the source column(s) it comes from (two for a join
    key that both sides equate) and the steps it passed that matter (renames, joins, unread steps, creations; a step that only keeps rows is
    not listed). A place can hold several occurrences of one column (a table joined with itself)."""
    name: str
    type: str
    how: str
    sources: Tuple[SourceColumn, ...]
    steps: Tuple[Hop, ...]


@dataclass(frozen=True)
class Reach:
    """What a step written at a place reaches, as SETS of place ids (`T1:J`, `T2:J`): the tables that a plot reads (directly or through a join),
    the stored tables that no plot reads, and the plots (their ids). A count is the length of a set and is never stored."""
    tables_with_plot: FrozenSet[str]
    tables_no_plot: FrozenSet[str]
    plots: FrozenSet[str]

    def __post_init__(self) -> None:
        for name in ("tables_with_plot", "tables_no_plot", "plots"):               # a plain set given is held as a sorted one: iteration and repr never depend on the hash seed
            object.__setattr__(self, name, SortedSet(getattr(self, name)))

    @property
    def n_tables(self) -> int:
        return len(self.tables_with_plot)

    @property
    def n_tables_no_plot(self) -> int:
        return len(self.tables_no_plot)

    @property
    def n_plots(self) -> int:
        return len(self.plots)


@dataclass(frozen=True)
class Line:
    """One place where a step can be written, exactly the text `add_step` takes in `place` (`T1:<table>`, `T2:<table>`, `T3:<plot>`).

    `covers`: the nodes collapsed into the place (an empty tier is not a place). `occurrences`: the column there (a list). `state`: `tick`
    (the column is the same one, proved by the plan and the readings) or `grey` (cannot be decided; `reason` says why). `scope_group`: the
    smallest scope that holds the line (`GROUPS`). `reach`: what a step here reaches, whether or not the column survives."""
    place: str
    covers: Tuple[str, ...]
    tier: str
    kind: str                                   # table or plot
    occurrences: Tuple[Occurrence, ...]
    state: str
    reason: Optional[Reason]
    notes: Tuple[Note, ...]
    scope_group: str
    is_start: bool
    reach: Reach
    refusal: Optional[Reason] = None            # "refused here, with the reason" (the drop of a key column, by place): carried per line, nothing sets it yet (step 4)
    duplicates: Optional[str] = None            # a source line whose tier 1 has no steps is the same table as that tier 1 (PROVISIONAL, D-0346): the place it duplicates, so that a caller shows one line


@dataclass(frozen=True)
class Gone:
    """A place of the reach where the column no longer exists, as a note under the lines that reach it (`reached_by`: their places). `removed_by` is
    the step that removed it (None when the plan shows no step: the column never arrived). `step_kind` is the kind of step the walk was asked for:
    for a filter the rows of this place still change (it is in the reach); for a drop the table here does not change (`table_changes`)."""
    place: str
    covers: Tuple[str, ...]
    removed_by: Optional[StepRef]
    reached_by: Tuple[str, ...]
    step_kind: str
    table_changes: bool
    reach: Reach
    scope_group: str = LINEAGE


@dataclass(frozen=True)
class Unread:
    """A place no plot reads: not offered as a line (D-0346), counted apart. `holds` says whether the column is there by the plan."""
    place: str
    covers: Tuple[str, ...]
    holds: bool
    reach: Reach
    scope_group: str = LINEAGE


@dataclass(frozen=True)
class Outside:
    """A source table that declares a key of the same family as the lineage's and that no join links to it: plain information, never a line (the name alone
    does not make two columns one). `reach` is what depends on the table."""
    table: str
    column: str
    why: str
    reach: Reach


@dataclass(frozen=True)
class Walk:
    """The result of one walk. `lines` holds every place of the chosen levels that holds the column in the lineage of the chosen place, ticked or grey, each
    tagged with its group, in graph order; nothing the walk cannot decide is left out (D-0195). `key_basis` says what the
    walk used to call two key columns the same: declared keys and the key pairs of joins, never the name alone."""
    start: Start
    step_kind: str                               # filter or drop
    levels: Tuple[str, ...]                      # the levels the caller chose (`LEVELS`); the places of the others are not offered
    lines: Tuple[Line, ...]
    gone: Tuple[Gone, ...]
    unread: Tuple[Unread, ...]
    outside: Tuple[Outside, ...]
    key_basis: str = "declared entity keys (is_entity_key) and the key pairs of the joins of the recipe; never the column name alone"
    start_type: str = ""                         # the engine type of the column at the place the user chose: each line holds its own, the difference is the note
    held_at_levels: Tuple[str, ...] = ()         # the levels (`LEVELS`) at which the column exists in the lineage, whatever levels were chosen

    @property
    def nothing(self) -> Optional[Reason]:
        """Why the walk holds nothing, or None. Derived, never stored: no line, no note under a line and no place no plot reads means the chosen levels select no
        place of the lineage; the reason says which levels were chosen and at which levels the column exists (D-0195: no silent empty result)."""
        if self.lines or self.gone or self.unread:
            return None
        return Reason(NO_PLACE_AT_THE_LEVELS, (("levels", self.levels), ("held_at_levels", self.held_at_levels)))

    @property
    def found(self) -> int:
        return sum(1 for line in self.lines if line.state == TICK)

    @property
    def grey(self) -> int:
        return sum(1 for line in self.lines if line.state == GREY)

    @property
    def accounted(self) -> Tuple[str, ...]:
        """Every place the walk accounts for: lines, notes and places no plot reads. Each candidate place is in exactly one."""
        return tuple(x.place for x in self.lines) + tuple(x.place for x in self.gone) + tuple(x.place for x in self.unread)

    def within(self, group: str) -> "Walk":
        """The walk restricted to the places of this group and the narrower ones (what a caller that offers only some groups shows)."""
        keep = group_rank(group)
        return Walk(self.start, self.step_kind, self.levels, tuple(x for x in self.lines if group_rank(x.scope_group) <= keep), tuple(x for x in self.gone if group_rank(x.scope_group) <= keep),
                    tuple(x for x in self.unread if group_rank(x.scope_group) <= keep), self.outside, self.key_basis,
                    self.start_type, self.held_at_levels)
