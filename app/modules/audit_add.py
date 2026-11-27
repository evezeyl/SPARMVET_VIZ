"""ADDING a tried audit step to the audit pipeline: the pure rules of FLOW-2 of the new Audit flow (no Shiny, no file, no engine; the screen is `app/handlers/trial_handlers.py`).

The model (ledger D-0656, D-0662, D-0669, D-0670, D-0672; `.claude/design/home_audit_what_is_true_now.md`): a step is tried first (`audit_try.py`). The user looks at the table at each place and may mark
the place "User verified" (the mark means "the table at this place was verified", D-0662: nothing about what the place reaches), writes the reason and presses "Add to audit pipeline". The step is
then written at ALL the places of the trial, also those not marked (D-0669); the mark is advice and blocks nothing; each node records whether its place was marked (`user_verified`, and `verified_at`
when it was). This module holds what the screen needs around that: the words, the rule that enables the button, the nodes with their marks, and the sentences of the export.

PROVISIONAL (the builder's words and choices; the owner reads them): every sentence below; the labels "User verified" (D-0670: her word) and "Add to audit pipeline" (D-0672); the field names
`user_verified` and `verified_at` of a node; that `verified_at` is the moment the mark was set; that nothing records WHO marked (the app has no user identity, D-0670: NOT decided); that a mark
is reset by a new Try even with the same condition and places.

Consumed by: app/handlers/trial_handlers.py, app/handlers/audit_stack.py (the card), app/modules/audit_places.py (the export's records), app/handlers/export_handlers.py. If deleted: HOME's Audit mode cannot add a tried step.

# @deps
# provides: constant:ADD_LABEL, constant:VERIFIED_LABEL, constant:REASON_LABEL, function:can_add, function:marks_summary, function:stamp_marks, function:added_notice, function:verified_card_line, function:verification_sentences
# consumes: nothing (pure)
# consumed_by: app/handlers/trial_handlers.py, app/handlers/audit_stack.py, app/modules/audit_places.py, app/handlers/export_handlers.py, app/tests/test_audit_add.py
# doc: .claude/rules/ui_implementation_contract.md#2, .claude/rules/ui_implementation_contract.md#3, .claude/knowledge/decision_ledger.md (D-0662, D-0669, D-0670, D-0672)
# @end_deps
"""
from __future__ import annotations

from typing import Any, Dict, Iterable, List, Mapping, Optional, Sequence, Tuple

ADD_LABEL = "Add to audit pipeline"                      # D-0672
VERIFIED_LABEL = "User verified"                         # D-0670
REASON_LABEL = "Reason (required)"                       # PROVISIONAL
REASON_PLACEHOLDER = "Why is this step needed?"          # PROVISIONAL
VERIFIED_LEGEND = "User verified: tick it when you have looked at the table at this place and accept the step there. Advice only: the step is written at every place of the trial."   # PROVISIONAL
REASON_NEEDED_LINE = "Write a reason to add this step. A step is never added without one."                                                                                 # PROVISIONAL
NOT_MARKED = "not marked as verified"                    # PROVISIONAL


def can_add(reason: Any) -> Tuple[bool, str]:
    """(True, "") when the reason is not empty or only spaces, else (False, one plain line that says why the button is disabled). The one rule of the gatekeeper at Add (a step without a reason is never
    written, `ui_implementation_contract.md` section 3)."""
    if str(reason or "").strip():
        return True, ""
    return False, REASON_NEEDED_LINE


def _places_word(total: int) -> str:
    return "place" if total == 1 else "places"


def marks_summary(verified: int, total: int) -> str:
    """"N of M places user verified" (D-0670). With one place: "N of 1 place user verified"."""
    return f"{verified} of {total} {_places_word(total)} user verified"


def stamp_marks(nodes: Iterable[dict], marks: Mapping[str, str]) -> List[dict]:
    """Copies of the added nodes, each with `user_verified` (True when its place is in `marks`, else False) and, when True, `verified_at` (the moment the mark was set).

    `marks` is `{place: time of the mark}`. A node with no place is not verified. The argument is not changed. Nothing else of a node is touched: the keys of the audit copy do not read these fields
    (`audit_places.nodes_signature`: id, place, kind, parameters)."""
    out: List[dict] = []
    for node in nodes:
        place = str(node.get("place") or "")
        stamped = {k: v for k, v in node.items() if k not in ("user_verified", "verified_at")}
        if place and place in marks:
            stamped["user_verified"] = True
            stamped["verified_at"] = str(marks[place])
        else:
            stamped["user_verified"] = False
        out.append(stamped)
    return out


def added_notice(places: int, verified: int) -> str:
    """The one notice after Add: "Step added to the audit pipeline at N places (K of N user verified)." PROVISIONAL words."""
    return f"Step added to the audit pipeline at {places} {_places_word(places)} ({marks_summary(verified, places)})."


def verified_card_line(node: Mapping[str, Any]) -> Optional[str]:
    """The line of a step card in the right panel: "User verified" or "not marked as verified" for a step that carries the field, None for a step of the old way (it says nothing about it)."""
    if "user_verified" not in node:
        return None
    return VERIFIED_LABEL if node.get("user_verified") else NOT_MARKED


def _decision_title(record: Mapping[str, Any]) -> str:
    params = record.get("params") or {}
    detail = "; ".join(f"{k}={v}" for k, v in params.items() if k in ("column", "op", "value"))
    return f"{record.get('action', 'step')} ({detail})" if detail else str(record.get("action", "step"))


def verification_sentences(records: Sequence[Mapping[str, Any]]) -> List[str]:
    """One plain sentence for each decision (the records that share an id) that carries the mark: "Step filter_row (column=identity; op=lt; value=90): 2 of 3 places user verified; not marked: Table
    ResFinder (tier 1)." A decision of the old way (no record of it carries `user_verified`) has no sentence. Used by README.txt and report.qmd, in the order the steps were added. PROVISIONAL words."""
    groups: Dict[str, List[Mapping[str, Any]]] = {}
    for record in records:
        groups.setdefault(str(record.get("id")), []).append(record)
    sentences: List[str] = []
    for group in groups.values():
        marked = [r for r in group if "user_verified" in r]
        if not marked:
            continue
        done = [r for r in marked if r.get("user_verified")]
        missing = [str(r.get("place_words") or r.get("place") or "?") for r in marked if not r.get("user_verified")]
        tail = f"; not marked: {', '.join(missing)}" if missing else ""
        sentences.append(f"Step {_decision_title(marked[0])}: {marks_summary(len(done), len(marked))}{tail}.")
    return sentences
