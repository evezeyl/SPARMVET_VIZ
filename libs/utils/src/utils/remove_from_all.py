# engine: python-polars (writes the Polars filter action that removes values from a table)
"""The option "remove from all the data" of the HOME audit, as pure logic (task AUDIT-REMOVE-FROM-ALL-DATA, step 1; D-0415 part B, D-0416, D-0313).

The owner's case (D-0415): an item is so bad that it will be redone; its results come later and not in this run; she wants it removed everywhere. The option is
separate from the places of the lineage (the normal dialog offers those, all ticked): it is explicit, independent of the lineage, and it writes the step at tier 1 of
every table that holds the key. Decided points (D-0416): it reaches every table that holds the key column, also a table no plot reads (1); it is OFF by default, an
explicit act (2); the list of the tables it reaches is known BEFORE anything is applied (3); its warning is data agnostic (4); it is offered ONLY for a removal by the
entity key, never for another column (D-0415, D-0313).

What this module answers, for a recipe and a column (`describe`):
1. Is the option offered? Only when the column is THE ENTITY KEY: a key that the recipe declares (`is_entity_id` on a field, D-0313, D-0082) or a column that a join of
   the recipe equates with one (the "key family" of `RecipeGraph.key_families`, the same basis as the lineage walk: declarations and join key pairs, never the name
   alone). A column that a join uses but that is not declared the key is information (`utils.join_keys`), not the entity key: it is not offered. A recipe that
   declares no entity key gets "not offered" and a reason.
2. Which tables does it reach? Every table of the recipe (a data schema, a metadata or additional table, a join) that HOLDS the key at the END of its tier 1, judged from
   the engine's plan (names and types) and the lineage links of `utils.lineage_walk` (a rename, a key under another name, the suffix of a clash are followed; the
   links are CERTAIN or the table is not reached). Its starting points are the data schemas that declare the key, so a table that declares the key and that no join
   links is reached too (D-0415: "reached only by (B)"), and a table no plot reads is reached (D-0416 point 1). A table that the app cannot follow, or whose plan the
   engine could not give, is NOT reached and is listed with the reason (`unsure`): never guessed. A table that holds a column of the same NAME and that nothing links
   to the key is not reached either, and is listed (`SAME_NAME_NOT_LINKED`): the name alone does not make two columns one (D-0355).
3. Where is the step written? At tier 1 of each reached table, `T1:<table>` (D-0415 B): for each place the table, the tier, the column's name THERE, its type THERE, and the
   plots that read the table (none for a table no plot reads), in graph order (the order of `RecipeGraph.collections`: sources, then joins, as in the recipe).
4. `apply` writes the removal in an audit copy (`utils.audit_copy`), ONLY at the places the user left ticked (`ticked`: a list of `KeyPlace.place` texts; D-0499, D-0531): at tier 1 of
   each ticked table one `modif_filter` step, `op: not_in` on the key with the values given, `na: keep` (a row with no key is not the entity removed: the rule of the filter dialog for
   "none of", `utils.na_choice.default_na`), in the second list `audit_steps`. Nothing is written at a place that is not ticked. Without a list (`ticked=None`) every reached place is written, as
   before this change (PROVISIONAL P8: the default is not decided by the owner; it is kept as it was and `Applied.ticked_given` says which case happened). An empty list writes nothing and is refused
   with a plain error; a ticked place that the option did not reach is refused with a plain error (never ignored). It is all or nothing: a value that does not fit the type of the key at one ticked
   table refuses the whole apply and names that table. `describe` never applies anything: the option is off until an explicit call of `apply`.
5. What the library reports is only what is true by construction (D-0501: no warning about the natural consequences downstream; the app does not decide the scope, D-0531): the places reached
   (`places`), the tables not reached with the code of the walk as data (`not_reached`), and after `apply` the places written and the places reached but not written (`Applied`). It says
   nothing about what the entity does in a table where no step is written: a table the user unticked is the user's choice (D-0499), not the library's to explain.

A table behind a join the app cannot YET follow (anti, right, full, a self-join; D-0452, D-0460) is NOT written and is in `not_reached` (code `uncertain_link`, the walk's reason `join_not_yet_followed`),
as data; a semi join is followed (D-0486): the table behind it is written like one behind an inner join. A table that shares only the NAME of the key (`same_name_not_linked`) is in `not_reached` too.

NOT decided, therefore not done here: whether the option also reaches a source FILE that no recipe table reads (D-0416: "asked only if the build meets it"; a file the
recipe does not declare is invisible to this logic; a declared table that nothing reads IS reached); whether the user can untick one table of the list in this option
(D-0416 says the list is shown before she confirms, not that she can change it: `apply` always writes at every reached table); where the unsure and the
same-name tables show on the screen and in what words.

PROVISIONAL (marked in the code; the builder's, not decided by the owner): P1 the words of `WARNING` ("or something alike", D-0416 point 4) and of the not-offered sentences;
P2 that the entity key is the key family (a declared key or a column a join equates with one) and that a column is judged by NAME when no place is given, and by the
lineage when a place is given (so that a renamed key can be asked at the place that has it); P3 `na: keep` and the operator `not_in` (with a list, also for one value);
P4 that a table the walk reaches only by an uncertain link is not reached but unsure; P5 that `apply` recomputes the option from the original of the audit copy and
refuses a stale one; P6 that without the engine's plan (`plans=None`) the plan is the one the recipe declares (names only, every type is the empty text: said, never invented)
and a table behind a step the walk does not read is unsure.

Pure: a recipe dictionary (the resolved recipe) in, plain frozen records out. No file, no data, no engine; the engine's plan book is an optional argument
(`utils.plan_book`), given by the caller that has the engine (`app/modules/plan_composer.py`).

Consumed by: libs/utils/tests/test_remove_from_all.py, app/tests/test_remove_from_all_demo.py (HOME's Create audit step dialog will call it; that screen is not built).
If deleted: HOME has no way to offer "remove from all the data".

# @deps
# provides: function:describe, function:apply, function:removal_step, function:not_offered_sentence, class:RemoveFromAll, class:KeyPlace, class:NotReached, class:Applied, constant:WARNING, constant:NOT_OFFERED_CODES, constant:NOT_REACHED_CODES
# consumes: libs/utils/src/utils/lineage_walk.py (LineageIndex: the links between the columns; certainty_from and uncertain_ends), libs/utils/src/utils/recipe_graph.py (key_families, declared_entity_keys, plots_reading), libs/utils/src/utils/declared_plans.py, libs/utils/src/utils/plan_book.py, libs/utils/src/utils/audit_copy.py (add_step, remove_step), libs/utils/src/utils/filter_values.py (check_filter), libs/utils/src/utils/na_choice.py (default_na), libs/utils/src/utils/recipe_tiers.py (without_audit_steps), libs/utils/src/utils/lineage_records.py (Reason)
# consumed_by: libs/utils/tests/test_remove_from_all.py, app/tests/test_remove_from_all_demo.py
# doc: .claude/knowledge/decision_ledger.md (D-0415, D-0416, D-0313, D-0082, D-0355, D-0351, D-0452, D-0454, D-0460), .claude/rules/ui_implementation_contract.md (section 8: the filter row and the value type rule), .claude/design/home_audit_steps.md
# @end_deps
"""
from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Dict, FrozenSet, List, Optional, Sequence, Set, Tuple

from utils import audit_copy, na_choice, recipe_tiers
from utils.action_names import FILTER
from utils.declared_plans import declared_plan_book
from utils.filter_values import FilterValueError, check_filter
from utils.lineage_records import Certainty, PLAN_FAILED as WALK_PLAN_FAILED, Note, Reason
from utils.lineage_walk import LineageIndex, Occ
from utils.plan_book import Plan, PlanBook, PlanFailure
from utils.recipe_graph import RecipeGraph, RecipeGraphError, build_graph

# PROVISIONAL P1 (D-0416 point 4: "This removes your selection from any data that holds it. or something alike"): data agnostic, it does not say what the entity is. One place.
WARNING = "This removes your selection from any data that holds it."

# Why the option is not offered: a closed list. The sentence is `not_offered_sentence` (PROVISIONAL words).
NO_ENTITY_KEY_DECLARED = "no_entity_key_declared"     # the recipe declares no `is_entity_id` anywhere
NOT_THE_ENTITY_KEY = "not_the_entity_key"             # the column is not the entity key (it may be a join column, a plain column, or absent)
RECIPE_CANNOT_BE_DRAWN = "recipe_cannot_be_drawn"     # the recipe cannot be drawn as a graph: nothing can be said about its tables
UNKNOWN_PLACE = "unknown_place"                       # the place asked is not a place of the recipe
COLUMN_NOT_AT_PLACE = "column_not_at_place"           # the place has no such column (or the engine could not give its columns)
NOT_OFFERED_CODES = (NO_ENTITY_KEY_DECLARED, NOT_THE_ENTITY_KEY, RECIPE_CANNOT_BE_DRAWN, UNKNOWN_PLACE, COLUMN_NOT_AT_PLACE)

# Why a table is not reached: a closed list. `UNSURE_CODES` are the doubts (the app could not tell); the others are information.
KEY_GONE_AT_TIER1 = "key_gone_at_tier1"               # the table is built from one that holds the key and the key is certainly not in it at the end of its tier 1
SAME_NAME_NOT_LINKED = "same_name_not_linked"         # the table holds a column of the same name that no declaration and no join links to the key (D-0355)
PLAN_FAILED = "plan_failed"                           # the engine could not give the columns of the table (its sentence is a parameter)
NOT_FOLLOWED = "not_followed"                         # a step the app cannot read lies between the key and this table (the reason is the walk's)
UNCERTAIN_LINK = "uncertain_link"                     # the key is linked to a column of this table only by a link the walk cannot prove
SEVERAL_COLUMNS = "several_columns"                   # the key is in this table more than once (a table joined with itself)
NOT_REACHED_CODES = (KEY_GONE_AT_TIER1, SAME_NAME_NOT_LINKED, PLAN_FAILED, NOT_FOLLOWED, UNCERTAIN_LINK, SEVERAL_COLUMNS)
# The doubts: a table where the logic cannot say the key is there to be removed from. `KEY_GONE_AT_TIER1` is one (review of 2026-11-21, F1): a table built from one that holds the key
# and that no longer has it at the end of its tier 1 (copied under another name, grouped away, dropped) is a fact of the walk, not a claim about the entity. `SAME_NAME_NOT_LINKED` is not one
# here: whether a same-named column with no declaration and no join is "the key" is the owner's question (P7), so it stays information.
UNSURE_CODES = (PLAN_FAILED, NOT_FOLLOWED, UNCERTAIN_LINK, SEVERAL_COLUMNS, KEY_GONE_AT_TIER1)


@dataclass(frozen=True)
class KeyPlace:
    """One place where the removal is written: tier 1 of a table. `place` is exactly the text `audit_copy.add_step` takes (`T1:<table>`); `column` and `type` are the
    key's name and engine type AT THE END of that tier 1 (the type is the empty text when the engine's plan was not given); `plots` are the plots that read the table,
    directly or through a join (none for a table no plot reads), in the order of the recipe. `notes` are the facts the walk found on the way from the declared key to this table,
    as data (`utils.lineage_records.NOTE_CODES`): a column that a step recomputes under its own name (`recomputed_here`), casts (`another_type_here`) or groups by
    (`one_row_per_group_after_this_step`). Data only: the library writes no sentence about them. Information, never a refusal."""
    place: str
    table: str
    tier: str
    column: str
    type: str
    plots: Tuple[str, ...]
    notes: Tuple[Note, ...] = ()


@dataclass(frozen=True)
class NotReached:
    """A table the option does not reach and the user should be told about: its place, why (a code of `NOT_REACHED_CODES`) and the reason as data (a walk `Reason` or None)."""
    table: str
    place: str
    code: str
    reason: Optional[Reason] = None


@dataclass(frozen=True)
class Applied:
    """What `apply` did: the ids of the steps written (in the order of `option.places`), `written` the places written (`KeyPlace.place`, same order), `not_written` the reached places where
    nothing was written (not ticked), and `ticked_given` False when no list was given and every reached place was written (PROVISIONAL P8). Only what is true by construction: nothing is said
    about the entity in a table where no step was written."""
    step_ids: Tuple[str, ...]
    written: Tuple[str, ...]
    not_written: Tuple[str, ...]
    ticked_given: bool = True


@dataclass(frozen=True)
class RemoveFromAll:
    """The option, described and not applied. `offered` False: `not_offered` says why and `places` is empty. `default_on` is always False (D-0416 point 2). `key_names` are the
    names of the entity key family (a declared key and the columns joins equate with it). `places` is the list of the tables it reaches, known before anything is applied
    (D-0416 point 3); `not_reached` the tables it does not reach and the reason; `place_asked` the place the column was asked at (None: judged by name)."""
    column: str
    place_asked: Optional[str]
    offered: bool
    not_offered: Optional[Reason]
    warning: str
    default_on: bool
    key_names: Tuple[str, ...]
    places: Tuple[KeyPlace, ...]
    not_reached: Tuple[NotReached, ...]

    @property
    def unsure(self) -> Tuple[NotReached, ...]:
        """The tables the app could not tell about (never guessed): the user must see them before confirming."""
        return tuple(n for n in self.not_reached if n.code in UNSURE_CODES)

    @property
    def types(self) -> Tuple[str, ...]:
        """The distinct engine types of the key over the reached tables, sorted (the empty text, when no plan of the engine was given, is left out)."""
        return tuple(sorted({p.type for p in self.places if p.type}))

    @property
    def types_differ(self) -> bool:
        return len(self.types) > 1


def not_offered_sentence(reason: Reason) -> str:
    """The plain sentence for a reason the option is not offered. PROVISIONAL words (the owner reads them)."""
    code = reason.code
    if code == NO_ENTITY_KEY_DECLARED:
        return "This recipe does not say which column is the entity key (the id of the thing each row describes), so removing from all the data is not offered. Declare the key in the recipe (is_entity_id)."
    if code == NOT_THE_ENTITY_KEY:
        declared = ", ".join(str(n) for n in reason.get("declared", ()) or ()) or "none"
        return (f"The column {reason.get('column')!r} is not the entity key of this recipe (the entity key is: {declared}), so removing from all the data is not offered for it. "
                "Use a filter on this column instead.")
    if code == RECIPE_CANNOT_BE_DRAWN:
        return f"The recipe cannot be read as a whole, so removing from all the data is not offered: {reason.get('sentence')}"
    if code == UNKNOWN_PLACE:
        return f"The recipe has no place {reason.get('place')!r}."
    if code == COLUMN_NOT_AT_PLACE:
        return f"The column {reason.get('column')!r} is not in {reason.get('place')} (or the engine could not give its columns), so removing from all the data is not offered for it there."
    return f"Not offered ({code})."


def _refused(column: str, place: Optional[str], code: str, params: Tuple[Tuple[str, Any], ...] = ()) -> RemoveFromAll:
    return RemoveFromAll(column, place, False, Reason(code, params), WARNING, False, (), (), ())


def _drawn(raw: Any) -> Tuple[Optional[RecipeGraph], Optional[str]]:
    try:
        return build_graph(recipe_tiers.without_audit_steps(raw) if isinstance(raw, dict) else raw), None
    except (RecipeGraphError, KeyError, TypeError, AttributeError) as error:
        return None, str(error)


def describe(recipe: Any, column: str, *, plans: Optional[PlanBook] = None, place: Optional[str] = None) -> RemoveFromAll:
    """The option "remove from all the data" for `column`, described and not applied.

    `recipe`: the resolved recipe (a dictionary); its audit steps, if it is an audit copy, are not read (the plan is the original's: an audit step never changes which table
    holds the key). `plans`: the engine's plan book of that recipe (`app/modules/plan_composer.py`); without it the plan the recipe declares is used (names only, the types are
    the empty text, a table behind a step the walk does not read is `unsure`; PROVISIONAL P6). `place`: where the user stands (`T1:<table>`, `T2:<table>` or `T3:<plot>`) when the
    column's name is the one THERE; without it the column is judged by its name (PROVISIONAL P2). A plan book that lacks a place raises `PlanBookIncomplete`: a bug of the caller."""
    graph, error = _drawn(recipe)
    if graph is None:
        return _refused(column, place, RECIPE_CANNOT_BE_DRAWN, (("sentence", error or ""),))
    tables = graph.collections()
    schemas = [t for t in tables if graph.node(f"T1:{t}").collection_kind == "schema"]
    declared = {t: tuple(graph.declared_entity_keys(t)) for t in schemas}
    if not any(declared.values()):
        return _refused(column, place, NO_ENTITY_KEY_DECLARED)
    every_declared = tuple(sorted({name for names in declared.values() for name in names}))
    index = LineageIndex(graph, plans if plans is not None else declared_plan_book(graph))
    not_key = _refused(column, place, NOT_THE_ENTITY_KEY, (("column", column), ("declared", every_declared)))

    if place is None:
        family = graph.key_family_of(column)
        if family is None:
            return not_key
        names: FrozenSet[str] = frozenset(family)
    else:
        if not graph.has_node(place):
            return _refused(column, place, UNKNOWN_PLACE, (("place", place),))
        here = index.plan_end(place)
        if not isinstance(here, Plan) or not here.has(column):
            return _refused(column, place, COLUMN_NOT_AT_PLACE, (("column", column), ("place", place)))
        begin: Occ = (place, index.end(place)[1], column)
        linked = index.component([begin])
        found = {occ[2] for occ in linked if occ[0].startswith("DS:") and occ[2] in declared.get(occ[0][3:], ())}
        if not found:
            return not_key
        names = frozenset(n for name in found for n in (graph.key_family_of(name) or (name,)))

    seeds: List[Occ] = []
    downstream: Set[str] = set()                       # the tables built from a schema that declares the key, and those schemas themselves
    for table in schemas:
        plan = index.plan_end(f"DS:{table}")
        for name in declared[table]:
            if name in names:
                downstream.update([f"T1:{table}", *graph.lineage_forward(f"DS:{table}")])
                if isinstance(plan, Plan) and plan.has(name):
                    seeds.append((f"DS:{table}", 0, name))
    component = index.component(seeds)
    certainty = index.certainty_from(seeds, component)
    ends = index.uncertain_ends(component)

    places: List[KeyPlace] = []
    left: List[NotReached] = []
    for table in tables:
        t1 = f"T1:{table}"
        node, k = index.end(t1)
        plan = index.plan_end(t1)
        if isinstance(plan, PlanFailure):
            if t1 in downstream:
                left.append(NotReached(table, t1, PLAN_FAILED, Reason(WALK_PLAN_FAILED, (("sentence", plan.sentence), ("node", plan.node or node), ("step", plan.step if plan.step is not None else -1)))))
            continue
        held = [(node, k, name) for name in plan.names if (node, k, name) in component]
        if len(held) == 1:
            how = certainty.get(held[0]) or Certainty(1)
            if how.certain:
                places.append(KeyPlace(t1, table, "T1", held[0][2], plan.type_of(held[0][2]) or "", tuple(graph.plots_reading(t1)), how.notes))
            else:
                left.append(NotReached(table, t1, UNCERTAIN_LINK, how.reason))
            continue
        if held:
            left.append(NotReached(table, t1, SEVERAL_COLUMNS, Reason(SEVERAL_COLUMNS, (("names", tuple(h[2] for h in held)),))))
            continue
        lineage = set(graph.lineage_back(t1)) | {t1}
        doubt = next((d for d in ends if d.in_node in lineage), None)
        if doubt is not None:
            left.append(NotReached(table, t1, NOT_FOLLOWED, doubt.reason))
        elif any(plan.has(name) for name in names):
            left.append(NotReached(table, t1, SAME_NAME_NOT_LINKED, Reason(SAME_NAME_NOT_LINKED, (("names", tuple(n for n in plan.names if n in names)),))))
        elif t1 in downstream:
            left.append(NotReached(table, t1, KEY_GONE_AT_TIER1))
    return RemoveFromAll(column, place, True, None, WARNING, False, tuple(sorted(names)), tuple(places), tuple(left))


def removal_step(column: str, values: Sequence[Any]) -> dict:
    """The audit step that removes these values of the key at one place: `modif_filter`, `not_in` on the key with a list (also for one value), `na: keep` (PROVISIONAL P3: a
    row with no key is not the removed entity; the default of the filter dialog for "none of", `utils.na_choice.default_na`). The step has no id and no reason: `add_step` writes them."""
    return {"action": FILTER, "column": column, "op": "not_in", "value": list(values), "na": na_choice.default_na("not_in")}


def _refuse_values(values: Any) -> List[Any]:
    if not isinstance(values, (list, tuple)) or not values:
        raise audit_copy.AuditCopyError("Removing from all the data needs the values to remove: a list with at least one value.")
    for value in values:
        if value is None or isinstance(value, (list, tuple, dict, set)):
            raise audit_copy.AuditCopyError(f"The value {value!r} cannot be removed: write each value as a text or a number (a missing value is not a value of the key).")
    return list(values)


def _chosen_places(option: RemoveFromAll, ticked: Optional[Sequence[str]]) -> Tuple[List[KeyPlace], bool]:
    """The places to write, in the order of `option.places` (never the order of `ticked`), and whether a list was given. The same place twice counts once."""
    if ticked is None:
        return list(option.places), False
    if isinstance(ticked, str) or not isinstance(ticked, (list, tuple, set, frozenset)):
        raise audit_copy.AuditCopyError("The places to write at must be a list of the places the user left ticked, so nothing was written.")
    offered = {p.place for p in option.places}
    for item in ticked:
        if not isinstance(item, str) or item not in offered:
            raise audit_copy.AuditCopyError(f"The place {item!r} is not one that this option reaches, so nothing was written.")
    if not ticked:
        raise audit_copy.AuditCopyError("No place is ticked, so nothing was written. Tick at least one place.")
    wanted = set(ticked)
    return [p for p in option.places if p.place in wanted], True


def apply(audit: audit_copy.AuditCopy, option: RemoveFromAll, values: Sequence[Any], comment: str, plans: Optional[PlanBook] = None, ticked: Optional[Sequence[str]] = None) -> Applied:
    """Write the removal in the audit copy at tier 1 of the places the user left ticked, and return `Applied` (the step ids, the places written, the reached places not written).

    `ticked`: a list of `KeyPlace.place` texts taken from `option.places`; ONLY those are written (D-0499, D-0531). `None` keeps the earlier behaviour: every reached place is written
    (PROVISIONAL P8, not decided by the owner; `Applied.ticked_given` is then False). An empty list, a place the option did not reach or a value that is not a text is a plain error and nothing is
    written. The order of the steps is the order of `option.places`, not of `ticked`; a place named twice is written once.

    ALL OR NOTHING: the values are checked against the type of the key at every ticked place, and the option against the original of the copy, before the first write; a step that
    cannot be written takes back the ones already written (and the counter), so that a refused call changes nothing. `option` must be an offered option described for the
    ORIGINAL of this copy with the same `plans` (PROVISIONAL P5: it is described again and a difference is refused: a stale list of tables is never written). The same reason
    (`comment`) goes on every step: it is the reason of one decision. The user's explicit act: nothing here is called by `describe`."""
    if not option.offered:
        raise audit_copy.AuditCopyError("Removing from all the data is not offered for this column, so nothing was written. " + not_offered_sentence(option.not_offered))  # type: ignore[arg-type]
    if not option.places:
        raise audit_copy.AuditCopyError("The app can reach no table with certainty (none holds the key, or it cannot follow it), so nothing was written.")
    targets, ticked_given = _chosen_places(option, ticked)
    values = _refuse_values(values)
    if not isinstance(comment, str) or not comment.strip():
        raise audit_copy.AuditCopyError("An audit step needs its reason: a text that is not empty.")
    if describe(audit.original, option.column, plans=plans, place=option.place_asked) != option:
        raise audit_copy.AuditCopyError("The list of tables no longer matches the recipe of this audit (it was described for another recipe or another plan), so nothing was written. Ask again.")
    for place in targets:
        try:
            check_filter("not_in", values, place.type or None)
        except FilterValueError as error:
            raise audit_copy.AuditCopyError(f"The value cannot be removed at {place.place}: the key is {place.type} there. {error} Nothing was written.") from None
    created, written = audit.created, []
    try:
        for place in targets:
            written.append(audit_copy.add_step(audit, place.place, removal_step(place.column, values), comment, plans))
    except BaseException:
        for step_id in reversed(written):
            audit_copy.remove_step(audit, step_id)
        audit.created = created
        raise
    done = tuple(p.place for p in targets)
    return Applied(tuple(written), done, tuple(p.place for p in option.places if p.place not in done), ticked_given)
