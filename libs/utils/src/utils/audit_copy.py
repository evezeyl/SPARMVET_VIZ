"""The audit copy of a recipe, in memory: a copy that only ADDS marked steps at the end of a list (piece A5 of slice A of the HOME audit redesign).

Two recipes (D-0102, D-0143): the `original_recipe` (what HOME opens; never changed by anything here) and the `audit_recipe` (a deep copy that
carries the steps of the audit). The audit adds steps at the END of the tier 1 or tier 2 list of a table (a source table or a join) or of the
tier 3 list of a plot (D-0146), and may take its own steps out again; an original step can never be removed.

A step of the copy is an ordinary recipe step (`action` and its parameters) plus the marker `id: audit_<8 hex>_<k>` and, as an option, the
reason in `comment` (recipe_format_spec.md DEC18; the checker's profile "audit"). The marker is how the copy and the original are told apart:
"the copy minus its marked audit steps must equal the original, otherwise it blocks" (ADR-105 point 6; `integrity_errors`).

Input and output: the RESOLVED recipe, a dictionary (the loader has merged every `!include`). Pure Python: no file, no data frame, no Shiny, no
other library of this repository except `utils.recipe_tiers` (the one reading of where the tiers are). No function changes its argument
except `add_step` and `remove_step`, which change the audit copy they are given and never anything else; a call that is refused changes nothing.

PLACE (PROVISIONAL, the builder's form): a place is the id of a node of `utils.recipe_graph`, written `T1:<table>`, `T2:<table>` or
`T3:<plot>`. `<table>` is a schema or a join id (`T1`, `T2`), `<plot>` a plot id (`T3`). The same text names a list in `marked_steps`.

PROVISIONAL: what `k` of the marker counts (the order of the step in its list, in the whole audit, in time?) is not decided; `add_step` takes the id
from the caller and checks only its form. Where the copy is written to a file (name, folder, header, the author's comments), the date and initials of
a step, the log of added and removed steps and the limits of the actions the audit may add are not decided and not built here.

Tiers that the copy creates: a table with no `tier2` (or a plot with no `tier3`) gets `tier2: {steps: [...]}` (the form of D-0250) when the first audit
step is added; the engine of a tier is NOT written, so the effective one stays (the tier's own `data_engine`, else the recipe's). When its last audit
step is removed, a tier2 or tier3 that holds nothing but an empty `steps` is removed again, so the copy equals the original again. An EMPTY tier2 or
tier3 (`{steps: []}`) and an ABSENT one mean the same to the engine, so `integrity_errors` treats them as equal.

Consumed by: app/modules/cache_keys.py (the audit parts of the keys), app/modules/audit_run.py (the run of a copy), libs/utils/tests/test_audit_copy.py.
If deleted: no audit copy can be made, checked or keyed.

# @deps
# provides: function:audit_recipe_of, function:add_step, function:remove_step, function:marked_steps, function:strip_marked, function:integrity_errors, function:is_marked, function:split_marked, function:audit_operation, function:parse_place, class:MarkedStep, class:AuditCopyError, constant:AUDIT_ID
# consumes: libs/utils/src/utils/recipe_tiers.py (collection_bodies, collection_body, plot_entries, plot_entry, plot_targets: where the tiers are)
# consumed_by: app/modules/cache_keys.py, app/modules/audit_run.py, libs/utils/tests/test_audit_copy.py, app/tests/test_audit_keys.py, app/tests/test_audit_run.py
# doc: .claude/knowledge/architecture_decisions.md#adr-101, .claude/knowledge/architecture_decisions.md#adr-105, .claude/design/home_audit_steps.md, .claude/design/recipe_format_spec.md (DEC18)
# @end_deps
"""
import copy
import re
from dataclasses import dataclass
from typing import Any, Dict, List, Optional, Tuple

from utils import recipe_tiers

# The marker of an audit step. The same form as the checker's `_AUDIT_ID` (`recipe_check.py`); a test holds the two equal.
AUDIT_ID = re.compile(r"^audit_[0-9a-f]{8}_\d+$")

# The keys of a step that are not part of its operation: the marker and the reason (`utils.ui_schema.STEP_KEYS` without `action`).
MARKER_KEYS = ("id", "comment")

_TIER_OF_KIND = {"T1": "tier1", "T2": "tier2", "T3": "tier3"}
# A tier the copy may create and take away again; the tier 1 of a table is required by the format, so it is never removed.
_REMOVABLE_TIERS = ("tier2", "tier3")


class AuditCopyError(ValueError):
    """An audit-copy operation that cannot be done; the message says why in plain words and the copy is left as it was."""


@dataclass(frozen=True)
class MarkedStep:
    """One marked audit step of a copy: the place of its list (`T1:<table>`, `T2:<table>`, `T3:<plot>`), its marker and the step as written."""
    place: str
    step_id: str
    step: dict


def is_marked(step: Any) -> bool:
    """True for a step that carries an audit marker (`id: audit_<8 hex>_<k>`)."""
    return isinstance(step, dict) and isinstance(step.get("id"), str) and bool(AUDIT_ID.match(step["id"]))


def split_marked(steps: Any) -> Tuple[list, list]:
    """(the steps that are not marked, the marked steps), each in list order. A list that is not a list gives two empty lists."""
    if not isinstance(steps, list):
        return [], []
    return [s for s in steps if not is_marked(s)], [s for s in steps if is_marked(s)]


def audit_operation(step: dict) -> dict:
    """The operation a marked step stands for: the step without its marker and its reason (ADR-101 point 2: "without reasons, dates or initials")."""
    return {k: v for k, v in step.items() if k not in MARKER_KEYS}


def parse_place(place: Any) -> Tuple[str, str]:
    """(`tier1`, `tier2` or `tier3`, the table or plot id) of a place such as `T2:J`; raises `AuditCopyError` for any other text."""
    kind, _, name = place.partition(":") if isinstance(place, str) else ("", "", "")
    if kind not in _TIER_OF_KIND or not name:
        raise AuditCopyError(f"{place!r} is not a place of the recipe: write T1:<table>, T2:<table> or T3:<plot> (for example T2:my_join).")
    return _TIER_OF_KIND[kind], name


def audit_recipe_of(original_recipe: dict) -> dict:
    """The audit copy of a recipe: a deep copy. The original is never changed."""
    return copy.deepcopy(original_recipe)


# ---------------------------------------------------------------------------------------------------------------------
# Where the lists are
# ---------------------------------------------------------------------------------------------------------------------


def _holders(recipe: dict) -> List[Tuple[str, str, str, dict]]:
    """(place, tier key, owner id, owner body) for every tier list the audit may write to: the tier 1 and tier 2 of each table and join, then the
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


def _steps_of(body: dict, tier: str) -> Optional[list]:
    held = body.get(tier)
    steps = held.get("steps") if isinstance(held, dict) else None
    return steps if isinstance(steps, list) else None


def marked_steps(audit_recipe: dict) -> List[MarkedStep]:
    """Every marked step of the copy with its place, in a fixed order: the tier 1 lists, then the tier 2 lists (tables and joins in the order of the
    recipe), then the tier 3 lists (plots in the order of the recipe); inside a list, in list order."""
    found: List[MarkedStep] = []
    for place, tier, _, body in _holders(audit_recipe):
        for step in split_marked(_steps_of(body, tier))[1]:
            found.append(MarkedStep(place, step["id"], step))
    return found


def strip_marked(audit_recipe: dict) -> dict:
    """The copy without its marked audit steps (a new dictionary). A tier that the copy created stays, empty: `integrity_errors` compares with
    that in mind."""
    stripped = copy.deepcopy(audit_recipe)
    for _, tier, _, body in _holders(stripped):
        held = body.get(tier)
        if isinstance(held, dict) and isinstance(held.get("steps"), list):
            held["steps"] = split_marked(held["steps"])[0]
    return stripped


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
    if held is not None and _steps_of(body, tier) is None:
        raise AuditCopyError(f"The {tier} of '{name}' is not written as a mapping with a list of steps, so no step can be added to {place}.")
    return tier, name, body


def add_step(audit_recipe: dict, place: str, step: dict, step_id: str, comment: Optional[str] = None) -> None:
    """Write ONE step at the end of the list of `place`, marked `step_id` and with the reason `comment` (changes the copy; a refused call changes nothing).

    `step` is the operation: `action` and its parameters, without `id` or `comment` (those are the two arguments). `step_id` has the form
    `audit_<8 hex>_<k>` and is not used by another marked step of the copy; what `k` counts is PROVISIONAL, it is not decided and only the form is checked."""
    tier, name, body = _target(audit_recipe, place)
    if not isinstance(step, dict) or not isinstance(step.get("action"), str):
        raise AuditCopyError("A step is a mapping with an action (for example {action: modif_filter, column: ..., op: ..., value: ..., na: ...}).")
    given = [k for k in MARKER_KEYS if k in step]
    if given:
        raise AuditCopyError(f"The step already holds {', '.join(given)}; give the marker as step_id and the reason as comment.")
    if not isinstance(step_id, str) or not AUDIT_ID.match(step_id):
        raise AuditCopyError(f"{step_id!r} is not an audit id: write audit_ and 8 characters of 0-9 a-f, an underscore and a number, for example audit_1a2b3c4d_1.")
    if step_id in {m.step_id for m in marked_steps(audit_recipe)}:
        raise AuditCopyError(f"The id {step_id} is already used by another audit step of the copy.")
    if comment is not None and not isinstance(comment, str):
        raise AuditCopyError("The reason (comment) is text.")
    written = copy.deepcopy(step)
    written["id"] = step_id
    if comment is not None:
        written["comment"] = comment
    if tier not in body:
        body[tier] = {"steps": []}
    body[tier]["steps"].append(written)


def remove_step(audit_recipe: dict, step_id: str) -> None:
    """Take one marked audit step out of the copy (changes the copy). An id that is not an audit id, or that no marked step has, is refused: an
    original step can never be removed. A tier2 or tier3 that the copy created and that is empty again is removed, so the copy can equal the original."""
    if not isinstance(step_id, str) or not AUDIT_ID.match(step_id):
        raise AuditCopyError(f"{step_id!r} is not an audit id: only the audit steps of the copy can be removed, never a step of the original recipe.")
    for _, tier, _, body in _holders(audit_recipe):
        steps = _steps_of(body, tier)
        if steps is None:
            continue
        for index, step in enumerate(steps):
            if is_marked(step) and step["id"] == step_id:
                del steps[index]
                if tier in _REMOVABLE_TIERS and body[tier] == {"steps": []}:
                    del body[tier]
                return
    raise AuditCopyError(f"No audit step of the copy has the id {step_id}, so nothing was removed.")


# ---------------------------------------------------------------------------------------------------------------------
# Integrity: the copy minus its marked steps equals the original
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
    """Plain sentences about what differs between the original and the copy without its marked steps, `path` being where in the recipe."""
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
            return [f"A step that is not a marked audit step was added to {here} ({len(original)} steps in the original, {len(other)} in the copy)."]
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


def integrity_errors(audit_recipe: dict, original_recipe: dict) -> List[str]:
    """Plain sentences about what makes the copy different from the original other than by marked steps added at the end; empty when the copy is sound.

    "The copy minus its marked audit steps must equal the original, otherwise it blocks" (ADR-105 point 6). Checks: the original holds no marked step;
    the marked ids are not used twice; every marked step stands after all the unmarked steps of its list; and the copy without its marked steps equals the
    original (an original step changed, removed or reordered; a key changed, added or removed anywhere else)."""
    errors: List[str] = []
    for found in marked_steps(original_recipe):
        errors.append(f"The original recipe already holds the audit step {found.step_id} at {found.place}: it is not an original recipe.")
    seen: Dict[str, str] = {}
    for found in marked_steps(audit_recipe):
        if found.step_id in seen:
            errors.append(f"The id {found.step_id} is used twice ({seen[found.step_id]} and {found.place}).")
        seen[found.step_id] = found.place
    for place, tier, _, body in _holders(audit_recipe):
        steps = _steps_of(body, tier) or []
        flags = [is_marked(s) for s in steps]
        for index, flag in enumerate(flags):
            if flag and not all(flags[index:]):
                errors.append(f"The audit step {steps[index]['id']} is not at the end of {place}: an audit step is added after every original step and not before one.")
    errors.extend(_differences(_without_empty_optional_tiers(original_recipe), _without_empty_optional_tiers(strip_marked(audit_recipe)), ""))
    return errors
