"""The audit copy of a recipe, in memory: a copy that only ADDS audit steps, each in the second list `audit_steps` of its tier (piece C-1 of slice C of the
HOME audit redesign; slice A built the first form, with the steps at the end of `steps`).

Two recipes (D-0102, D-0143): the `original_recipe` (what HOME opens; never changed by anything here) and the `audit_recipe` (a deep copy that
carries the steps of the audit). The FORM of the copy (D-0332): in each tier of a table, a join or a plot the author's list `steps` is never touched and
a second list `audit_steps` holds the steps of the audit; the engine runs `steps`, then `audit_steps` (`utils.recipe_tiers.step_list`). An audit step is
the operation (`action` and its arguments) plus `id: audit_<8 hex>_<k>` and `audit_comment: "<reason>"` (D-0329, D-0321). The audit may take its own
steps out again, any of them (D-0314: one undo control, "Remove step"); an original step can never be removed. "The copy minus its audit steps equals
the original, otherwise it blocks" (ADR-105 point 6, D-0040; `integrity_errors`).

Input and output: the RESOLVED recipe, a dictionary (the loader has merged every `!include`). Pure Python: no file, no data frame, no Shiny, no
other library of this repository except `utils.recipe_tiers` (the one reading of where the tiers and the audit lists are) and `utils.action_names`.
No function changes its argument except `add_step` and `remove_step`, which change the audit copy they are given and never anything else; a call that is
refused changes nothing, not even the counter.

HOW THE NUMBER `k` IS GIVEN (D-0321: "the number at the end of an audit step id counts the order in which the steps were created in that audit"). The
copy is an `AuditCopy`: the recipe dictionary (`.recipe`, what is keyed, checked, run and some day written to a file) and, beside it and outside it, the
audit's two facts: `audit_id` (the 8 hex characters of every id of this audit) and `created` (how many steps this audit ever created). `add_step` adds 1 to
`created` and writes `audit_<audit_id>_<created>`; `remove_step` never lowers it. So the number of a removed step is never given again inside one audit,
and the dictionary stays exactly the recipe (add then remove gives back the dictionary as it was). WHY not "the highest number now present plus 1": that
gives the number of a removed last step again. PROVISIONAL: where `created` and `audit_id` are kept when the audit is written to a file and read again is
the audit record's job (D-0333; not built here): until then they live in the `AuditCopy` object only.

WHAT AN AUDIT STEP MAY NOT BE (D-0322, D-0297): its action is one of `AUDIT_ACTIONS` (a filter, a column drop; a removal by key is the filter on the key column), and a
`polars_drop` never names a column that a join step later reads as a key, BY PLACE (D-0358, D-0297: where no later join reads it, as in a plot's own steps, the drop is allowed):
ONE rule, `utils.key_drop`, asked by `add_step`, by `integrity_errors` and by the checker's audit profile (AU04). `integrity_errors` also names an `audit_steps` list written where no tier reads it (a tier 3 of a table or a
join, a tier 1 or tier 2 of a plot). The engine asks `integrity_errors` of every audit copy before it builds from it (`orchestrator.refuse_audit_steps_outside_an_audit`).

PLACE (PROVISIONAL, the builder's form): a place is the id of a node of `utils.recipe_graph`, written `T1:<table>`, `T2:<table>` or
`T3:<plot>`. `<table>` is a schema or a join id (`T1`, `T2`), `<plot>` a plot id (`T3`). The same text names a list in `all_audit_steps`.

Tiers that the copy creates: a table with no `tier2` (or a plot with no `tier3`) gets `tier2: {steps: [], audit_steps: [...]}` when the first audit step is
added; the engine of a tier is NOT written, so the effective one stays (the tier's own `data_engine`, else the recipe's). A tier that holds nothing but
an empty `steps` and an `audit_steps` list is, for the integrity check, the same as an ABSENT tier (the engine runs nothing for either): so the copy minus its
audit steps equals the original even when the audit created the tier. When the last audit step of such a tier is removed, the tier goes again only if the ORIGINAL
did not write it there (`AuditCopy.original` says), and the emptied `audit_steps` key always goes: add then remove gives back exactly the copy as it was.

PROVISIONAL, not decided and not built here: where the copy is written to a file, the date and initials of a step, the log of added and removed steps, the key
under `info` that names the original.

Consumed by: app/modules/cache_keys.py (the audit parts of the keys), app/modules/audit_run.py (the run of a copy), libs/utils/tests/test_audit_copy.py.
If deleted: no audit copy can be made, checked or keyed.

# @deps
# provides: function:start_audit, function:add_step, function:remove_step, function:all_audit_steps, function:with_audit_steps, function:integrity_errors, function:is_audit_id, function:audit_operation, function:parse_place, class:AuditCopy, class:AuditStep, class:AuditCopyError
# consumes: libs/utils/src/utils/key_drop.py (DropGate: a key column cannot be dropped where a join later reads it, D-0358, D-0297; `plans`: the engine's plan book of the original), libs/utils/src/utils/plan_book.py (PlanBook), libs/utils/src/utils/recipe_tiers.py (AUDIT_STEPS, AUDIT_COMMENT, AUDIT_ID, collection_bodies, collection_body, plot_entries, plot_entry, plot_targets, without_audit_steps, audit_step_places), libs/utils/src/utils/action_names.py (AUDIT_ACTIONS)
# consumed_by: app/modules/cache_keys.py, app/modules/audit_run.py, libs/utils/tests/test_audit_copy.py, app/tests/test_audit_keys.py, app/tests/test_audit_run.py
# doc: .claude/knowledge/architecture_decisions.md#adr-101, .claude/knowledge/architecture_decisions.md#adr-105, .claude/design/home_audit_steps.md, .claude/design/recipe_format_spec.md (DEC18)
# @end_deps
"""
import copy
import re
import secrets
from dataclasses import dataclass, field
from typing import Any, Dict, Iterable, List, Optional, Tuple

from utils import action_names, key_drop, recipe_tiers
from utils.action_names import AUDIT_ACTIONS
from utils.plan_book import PlanBook
from utils.recipe_tiers import AUDIT_COMMENT, AUDIT_ID, AUDIT_STEPS

# The keys of an audit step that are not part of its operation: the id, the reason and the author's note (a note changes no data).
NON_OPERATION_KEYS = ("id", AUDIT_COMMENT, "comment")

_AUDIT_HEX = re.compile(r"^[0-9a-f]{8}$")
_TIER_OF_KIND = {"T1": "tier1", "T2": "tier2", "T3": "tier3"}
# A tier the copy may create and take away again; the tier 1 of a table is required by the format, so it is never removed.
_REMOVABLE_TIERS = ("tier2", "tier3")


class AuditCopyError(ValueError):
    """An audit-copy operation that cannot be done; the message says why in plain words and the copy is left as it was."""


@dataclass(frozen=True)
class AuditStep:
    """One audit step of a copy: the place of its list (`T1:<table>`, `T2:<table>`, `T3:<plot>`), its id and the step as written."""
    place: str
    step_id: str
    step: dict


@dataclass
class AuditCopy:
    """The audit copy of one original recipe, with the two facts of the audit that are not in the recipe (see the module text).

    recipe: the copy, a resolved dictionary: what is keyed, checked, run and written. original: a deep copy of the recipe the audit started from (it says
    which tiers the original wrote). audit_id: the 8 hex characters of every id. created: how many steps this audit ever created; it only goes up."""
    original: dict
    recipe: dict
    audit_id: str
    created: int = 0


def is_audit_id(value: Any) -> bool:
    """True for a text of the form `audit_<8 hex>_<k>`."""
    return isinstance(value, str) and bool(AUDIT_ID.match(value))


def audit_operation(step: dict) -> dict:
    """The operation an audit step stands for: the step without its id, its reason and any note (ADR-101 point 2: "without reasons, dates or initials")."""
    return {k: v for k, v in step.items() if k not in NON_OPERATION_KEYS}


def parse_place(place: Any) -> Tuple[str, str]:
    """(`tier1`, `tier2` or `tier3`, the table or plot id) of a place such as `T2:J`; raises `AuditCopyError` for any other text."""
    kind, _, name = place.partition(":") if isinstance(place, str) else ("", "", "")
    if kind not in _TIER_OF_KIND or not name:
        raise AuditCopyError(f"{place!r} is not a place of the recipe: write T1:<table>, T2:<table> or T3:<plot> (for example T2:my_join).")
    return _TIER_OF_KIND[kind], name


def start_audit(original_recipe: dict, audit_id: Optional[str] = None) -> AuditCopy:
    """Begin an audit: a deep copy of the original, a deep copy of the original kept to compare with, an id of 8 hex characters (given, else drawn at random:
    it is a label that tells one audit from another and is in no key) and a counter at 0. The original is never changed."""
    if audit_id is None:
        audit_id = secrets.token_hex(4)
    if not isinstance(audit_id, str) or not _AUDIT_HEX.match(audit_id):
        raise AuditCopyError(f"{audit_id!r} is not an audit identifier: write 8 characters of 0-9 a-f.")
    return AuditCopy(copy.deepcopy(original_recipe), copy.deepcopy(original_recipe), audit_id, 0)


# ---------------------------------------------------------------------------------------------------------------------
# Where the lists are
# ---------------------------------------------------------------------------------------------------------------------


def _holders(recipe: dict) -> List[Tuple[str, str, str, dict]]:
    """(place, tier key, owner id, owner body) for every tier the audit may write to: the tier 1 and tier 2 of each table and join, then the
    tier 3 of each plot, each kind in the order of the recipe. The body is the table, join or plot entry itself (the live dictionary)."""
    found: List[Tuple[str, str, str, dict]] = []
    bodies = recipe_tiers.collection_bodies(recipe)
    for tier in ("tier1", "tier2"):
        for name, body in bodies.items():
            if isinstance(body, dict):
                found.append((f"T{tier[-1]}:{name}", tier, name, body))
    for name, entry in recipe_tiers.plot_entries(recipe).items():
        found.append((f"T3:{name}", "tier3", name, entry))
    return found


def _list_in(body: dict, tier: str, key: str) -> Optional[list]:
    held = body.get(tier)
    found = held.get(key) if isinstance(held, dict) else None
    return found if isinstance(found, list) else None


def all_audit_steps(audit_recipe: dict) -> List[AuditStep]:
    """Every audit step of the copy with its place, in a fixed order: the tier 1 lists, then the tier 2 lists (tables and joins in the order of the
    recipe), then the tier 3 lists (plots in the order of the recipe); inside a list, in list order. A step with no text id is listed with the id "" (and a
    step that is not a mapping is left out); `integrity_errors` names both."""
    found: List[AuditStep] = []
    for place, tier, _, body in _holders(audit_recipe):
        for step in _list_in(body, tier, AUDIT_STEPS) or []:
            if isinstance(step, dict):
                found.append(AuditStep(place, step["id"] if isinstance(step.get("id"), str) else "", step))
    return found


# ---------------------------------------------------------------------------------------------------------------------
# Add and remove
# ---------------------------------------------------------------------------------------------------------------------


def _target(audit_recipe: dict, place: str) -> Tuple[str, str, dict]:
    """(tier key, owner id, owner body) of a place, or an `AuditCopyError` that says what the recipe lacks."""
    tier, name = parse_place(place)
    if tier == "tier3":
        body = recipe_tiers.plot_entry(audit_recipe, name)
        if not isinstance(body, dict):
            raise AuditCopyError(f"The recipe has no plot '{name}', so there is no {place} to add a step to.")
        return tier, name, body
    body = recipe_tiers.collection_body(audit_recipe, name)
    if not isinstance(body, dict):
        raise AuditCopyError(f"The recipe has no table or join '{name}', so there is no {place} to add a step to.")
    if tier == "tier2" and name not in recipe_tiers.plot_targets(audit_recipe):
        raise AuditCopyError(f"No plot reads '{name}', so its tier 2 is applied nowhere and a step added to {place} would be skipped. "
                             f"Add the step to the tier 1 of '{name}', or to the tier 2 of a table that a plot reads.")
    held = body.get(tier)
    if held is not None and (not isinstance(held, dict) or _list_in(body, tier, "steps") is None):
        raise AuditCopyError(f"The {tier} of '{name}' is not written as a mapping with a list of steps, so no step can be added to {place}.")
    if isinstance(held, dict) and AUDIT_STEPS in held and not isinstance(held[AUDIT_STEPS], list):
        raise AuditCopyError(f"The {AUDIT_STEPS} of the {tier} of '{name}' is not a list, so no step can be added to {place}.")
    return tier, name, body


def _append(body: dict, tier: str, written: dict) -> None:
    if tier not in body:
        body[tier] = {"steps": []}
    body[tier].setdefault(AUDIT_STEPS, []).append(written)


def _refuse_if_not_allowed(step: Any, recipe: dict, place: str, plans: Optional[PlanBook] = None) -> None:
    if not isinstance(step, dict) or not isinstance(step.get("action"), str):
        raise AuditCopyError("A step is a mapping with an action (for example {action: modif_filter, column: ..., op: ..., value: ..., na: ...}).")
    if step["action"] not in AUDIT_ACTIONS:
        raise AuditCopyError(f"An audit step is a filter, a column drop or a removal by key: {', '.join(AUDIT_ACTIONS)}. '{step['action']}' is not one of them.")
    problem = _key_drop(step, recipe, place, plans=plans)
    if problem:
        raise AuditCopyError(problem)


def _key_drop(step: Any, recipe: dict, place: str, gate: Optional[key_drop.DropGate] = None, plans: Optional[PlanBook] = None) -> Optional[str]:
    """The plain sentence when the step drops a key column AT THIS PLACE (D-0358, D-0297), else None (a column the app cannot follow to the joins after it is allowed with a
    warning, `utils.key_drop.DropGate.warning`, D-0449): ONE rule, `utils.key_drop`. A caller that asks several times on one recipe passes the same `gate`; `plans` is the engine's
    plan book of the ORIGINAL recipe (the caller that has the engine gives it; without it the rule reads the names the recipe declares)."""
    if isinstance(step, dict) and step.get("action") == action_names.DROP:
        return (gate or key_drop.DropGate(recipe, plans)).problem(place, step.get("columns"))
    return None


def add_step(audit: AuditCopy, place: str, step: dict, comment: str, plans: Optional[PlanBook] = None) -> str:
    """Write ONE audit step in the list `audit_steps` of `place`, after the ones already there, and return its id (changes the copy; a refused call changes nothing).

    `step` is the operation: `action` (one of `AUDIT_ACTIONS`) and its arguments, without `id` or `audit_comment` (the copy writes the id and takes the reason
    from `comment`). `comment` is the reason, a text that is not empty. The id is `audit_<audit_id>_<created + 1>`: see the module text for what the number counts.

    `plans`: the engine's plan book of the ORIGINAL recipe (`app/modules/plan_composer.py`), for the rule of a key drop (`utils.key_drop`); without it the rule reads only the
    names the recipe declares: a key column behind a step it cannot read is then not seen (the run of the copy asks again with the engine's plan and refuses it)."""
    tier, _, body = _target(audit.recipe, place)
    _refuse_if_not_allowed(step, audit.recipe, place, plans)
    given = [k for k in ("id", AUDIT_COMMENT) if k in step]
    if given:
        raise AuditCopyError(f"The step already holds {', '.join(given)}; the copy writes the id, and the reason is the argument comment.")
    if not isinstance(comment, str) or not comment.strip():
        raise AuditCopyError("An audit step needs its reason: a text that is not empty.")
    written = copy.deepcopy(step)
    written["id"] = f"audit_{audit.audit_id}_{audit.created + 1}"
    written[AUDIT_COMMENT] = comment
    _append(body, tier, written)
    audit.created += 1
    return written["id"]


def with_audit_steps(original_recipe: dict, steps: Iterable[AuditStep]) -> dict:
    """The original plus these audit steps AS THEY ARE WRITTEN (their ids and reasons kept), each after the ones before it in its list: a deep copy.
    For a caller that needs to rebuild part of a copy (the run names the step that cannot be applied by trying them one after the other)."""
    rebuilt = copy.deepcopy(original_recipe)
    for found in steps:
        tier, _, body = _target(rebuilt, found.place)
        _append(body, tier, copy.deepcopy(found.step))
    return rebuilt


def remove_step(audit: AuditCopy, step_id: str) -> None:
    """Take one audit step out of the copy, whichever it is (the one undo control, D-0314; changes the copy). An id that is not an audit id, or that no audit step has,
    is refused: an original step can never be removed. The counter does not go down.

    An emptied `audit_steps` key goes. A tier that then holds nothing but an empty `steps` goes too when the ORIGINAL did not write it at that place (the add created it):
    so an add followed by a remove gives back exactly the dictionary the copy was before the add. The tier 1 of a table is never removed."""
    if not is_audit_id(step_id):
        raise AuditCopyError(f"{step_id!r} is not an audit id: only the audit steps of the copy can be removed, never a step of the original recipe.")
    written_by_original = {place for place, tier, _, body in _holders(audit.original) if tier in body}
    for place, tier, _, body in _holders(audit.recipe):
        listed = _list_in(body, tier, AUDIT_STEPS)
        for index, step in enumerate(listed or []):
            if isinstance(step, dict) and step.get("id") == step_id:
                del listed[index]
                if not listed:
                    del body[tier][AUDIT_STEPS]
                if tier in _REMOVABLE_TIERS and body[tier] == {"steps": []} and place not in written_by_original:
                    del body[tier]
                return
    raise AuditCopyError(f"No audit step of the copy has the id {step_id}, so nothing was removed.")


# ---------------------------------------------------------------------------------------------------------------------
# Integrity: the copy minus its audit steps equals the original
# ---------------------------------------------------------------------------------------------------------------------


def _without_empty_optional_tiers(recipe: dict) -> dict:
    """A copy of the recipe without an empty tier2 or tier3 (`{steps: []}` and nothing else): for the engine it is the same as none."""
    normal = copy.deepcopy(recipe)
    for _, tier, _, body in _holders(normal):
        if tier in _REMOVABLE_TIERS and body.get(tier) == {"steps": []}:
            del body[tier]
    return normal


def _short(value: Any, width: int = 60) -> str:
    text = repr(value)
    return text if len(text) <= width else text[:width - 3] + "..."


def _differences(original: Any, other: Any, path: str) -> List[str]:
    """Plain sentences about what differs between the original and the copy without its audit steps, `path` being where in the recipe."""
    here = path or "the recipe"
    if isinstance(original, dict) and isinstance(other, dict):
        found: List[str] = []
        for key in original:
            if key not in other:
                found.append(f"{path + '.' if path else ''}{key} was removed from the copy (the audit only adds steps).")
        for key in other:
            if key not in original:
                found.append(f"{path + '.' if path else ''}{key} was added to the copy outside the audit steps.")
        for key in original:
            if key in other:
                found.extend(_differences(original[key], other[key], f"{path + '.' if path else ''}{key}"))
        return found
    if isinstance(original, list) and isinstance(other, list) and path.endswith(".steps"):
        if original == other:
            return []
        if len(other) < len(original):
            return [f"An original step was removed from {here} ({len(original)} steps in the original, {len(other)} in the copy)."]
        if len(other) > len(original):
            return [f"A step that is not an audit step was added to {here} ({len(original)} steps in the original, {len(other)} in the copy)."]
        if sorted(map(repr, original)) == sorted(map(repr, other)):
            return [f"The original steps of {here} were reordered."]
        return [f"Original step {i} of {here} was changed (original {_short(a)}, copy {_short(b)})."
                for i, (a, b) in enumerate(zip(original, other), start=1) if a != b]
    if isinstance(original, list) and isinstance(other, list):
        if original == other:
            return []
        if len(original) != len(other):
            return [f"{here} was changed in the copy ({len(original)} entries in the original, {len(other)} in the copy)."]
        found = []
        for i, (a, b) in enumerate(zip(original, other)):
            found.extend(_differences(a, b, f"{path}[{i}]"))
        return found
    if original != other:
        return [f"{here} was changed in the copy (original {_short(original)}, copy {_short(other)})."]
    return []


def _audit_ids_in_steps(recipe: dict) -> List[Tuple[str, str]]:
    """(place, what) for every item of an author's `steps` list that carries an audit id or an `audit_comment`: where only the audit writes them."""
    found: List[Tuple[str, str]] = []
    for place, tier, _, body in _holders(recipe):
        for step in _list_in(body, tier, "steps") or []:
            if isinstance(step, dict):
                if is_audit_id(step.get("id")):
                    found.append((place, f"the id {step['id']}"))
                if AUDIT_COMMENT in step:
                    found.append((place, AUDIT_COMMENT))
    return found


def _unread_audit_lists(recipe: dict) -> List[Tuple[str, str]]:
    """(path, what it is) for every `audit_steps` written where the engine reads no such tier: a tier 3 of a table or a join, a tier 1 or tier 2 of a plot."""
    found: List[Tuple[str, str]] = []
    for name, body in recipe_tiers.collection_bodies(recipe).items():
        if isinstance(body, dict) and isinstance(body.get("tier3"), dict) and AUDIT_STEPS in body["tier3"]:
            found.append((f"{name}.tier3", "a table or a join has no tier 3"))
    for name, entry in recipe_tiers.plot_entries(recipe).items():
        for tier in ("tier1", "tier2"):
            if isinstance(entry.get(tier), dict) and AUDIT_STEPS in entry[tier]:
                found.append((f"plot {name}.{tier}", "a plot has a tier 3 only"))
    return found


def integrity_errors(audit_recipe: dict, original_recipe: dict, plans: Optional[PlanBook] = None) -> List[str]:
    """Plain sentences about what makes the copy different from the original other than by audit steps in `audit_steps`; empty when the copy is sound.

    "The copy minus its audit steps must equal the original, otherwise it blocks" (ADR-105 point 6). Checks: the original holds no `audit_steps` and no audit
    id or reason anywhere; the audit ids are not used twice; every `audit_steps` is a list whose items have the form of an audit step (an audit id, a reason that
    is a text that is not empty, an action that an audit may use); no item of an author's `steps` list carries an audit id or a reason (a hand-made audit step
    in the wrong list); and the copy without its `audit_steps` equals the original (an original step changed, removed or reordered; a key changed, added or
    removed anywhere else). `plans`: the engine's plan book of the ORIGINAL recipe, for the rule of a key drop (see `add_step`)."""
    errors: List[str] = []
    gate: Optional[key_drop.DropGate] = None                 # built when the first audit step that drops a column needs it
    for where in recipe_tiers.audit_step_places(original_recipe):
        errors.append(f"The original recipe already holds {AUDIT_STEPS} at {where}: it is not an original recipe.")
    for place, what in _audit_ids_in_steps(original_recipe):
        errors.append(f"The original recipe already holds {what} on a step at {place}: it is not an original recipe.")
    seen: Dict[str, str] = {}
    for place, tier, _, body in _holders(audit_recipe):
        held = body.get(tier)
        if isinstance(held, dict) and AUDIT_STEPS in held and not isinstance(held[AUDIT_STEPS], list):
            errors.append(f"The {AUDIT_STEPS} of {place} is not a list.")
            continue
        for index, step in enumerate(_list_in(body, tier, AUDIT_STEPS) or [], start=1):
            where = f"{AUDIT_STEPS} {index} of {place}"
            if not isinstance(step, dict):
                errors.append(f"The audit step {index} of {place} is not a mapping with an action.")
                continue
            step_id = step.get("id")
            if not is_audit_id(step_id):
                errors.append(f"The {where} has no audit id (audit_ and 8 characters of 0-9 a-f, an underscore and a number): {step_id!r}.")
            elif step_id in seen:
                errors.append(f"The id {step_id} is used twice ({seen[step_id]} and {place}).")
            else:
                seen[step_id] = place
            reason = step.get(AUDIT_COMMENT)
            if not isinstance(reason, str) or not reason.strip():
                errors.append(f"The {where} has no reason: {AUDIT_COMMENT} is a text that is not empty.")
            if step.get("action") not in AUDIT_ACTIONS:
                errors.append(f"The {where} is '{step.get('action')}'; an audit step is one of {', '.join(AUDIT_ACTIONS)}.")
            if step.get("action") == action_names.DROP:
                gate = gate or key_drop.DropGate(audit_recipe, plans)
            problem = _key_drop(step, audit_recipe, place, gate)
            if problem:
                errors.append(f"The {where} ({step_id}): {problem}")
    for place, kind in _unread_audit_lists(audit_recipe):
        errors.append(f"An {AUDIT_STEPS} list is written at {place}, where no tier reads it ({kind}): nothing would run its steps.")
    for place, what in _audit_ids_in_steps(audit_recipe):
        errors.append(f"A step of the author's list of {place} carries {what}: an audit step belongs in {AUDIT_STEPS}, never among the author's steps.")
    errors.extend(_differences(_without_empty_optional_tiers(original_recipe),
                               _without_empty_optional_tiers(recipe_tiers.without_audit_steps(audit_recipe)), ""))
    return errors
