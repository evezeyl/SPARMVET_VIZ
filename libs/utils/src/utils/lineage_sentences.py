"""The words of the warning for a join the app cannot YET follow (D-0452, D-0454, D-0460), from the facts of the walk's reason `join_not_yet_followed`.

The owner (D-0454): "she wants the full sentence, with YET in capital letters". The warning is ONE full sentence; the capital word YET is decided and a test asserts it
(`libs/utils/tests/test_lineage_unfollowed_join.py`). Everything else in the sentence is PROVISIONAL (the review session's proposal in the bracket of D-0454; the owner reads it):
the list of kinds named, the sentence that says what may change, the clause for an anti join, "Check them before you confirm".

One function turns the reason into the sentence; the library returns the sentence as text and never a colour or HTML (how a red line is shown is not decided, not built). The same
sentence is read by the drop gate (`utils.key_drop`) and by the list of tables "remove from all the data" leaves untouched (`utils.remove_from_all`), so that one fact has one wording.

Pure: a `Reason` in, a string out. No file, no engine.

Consumed by: libs/utils/src/utils/key_drop.py, libs/utils/src/utils/remove_from_all.py, libs/utils/tests/test_lineage_unfollowed_join.py.
If deleted: a red line has no sentence for the user.

# @deps
# provides: function:join_not_yet_followed_sentence, function:join_phrase
# consumes: libs/utils/src/utils/lineage_records.py (Reason), libs/utils/src/utils/step_effects.py (NOT_YET_FOLLOWED_JOINS)
# consumed_by: libs/utils/src/utils/key_drop.py, libs/utils/src/utils/remove_from_all.py, libs/utils/tests/test_lineage_unfollowed_join.py
# doc: .claude/knowledge/decision_ledger.md (D-0452, D-0454, D-0460, D-0486)
# @end_deps
"""
from __future__ import annotations

from utils import step_effects as fx
from utils.lineage_records import Reason


def join_phrase(reason: Reason) -> str:
    """The join, in words and with its place: "the anti join of step 1 of T1:J, which reads the table 'B'" (a self-join: "the self-join (how: left) of step ..."). PROVISIONAL wording."""
    kind, step, node, right = reason.get("kind", "?"), reason.get("step", "?"), reason.get("node", "?"), reason.get("right")
    what = f"the self-join (how: {kind})" if reason.get("self_join") else f"the {kind} join"
    reads = f", which reads the table {right!r}" if right else ""
    return f"{what} of step {step} of {node}{reads}"


def join_not_yet_followed_sentence(reason: Reason) -> str:
    """The warning for a line that crosses a join the app cannot YET follow: what the app cannot do, which join (kind, step, place, table), that the tables behind it may change in a
    way the app cannot describe, and what to do. The capital YET is decided (D-0454); the rest is PROVISIONAL."""
    named = ", ".join(fx.NOT_YET_FOLLOWED_JOINS) + " or self-join"
    clause = ": for an anti join, rows may be added instead of removed" if reason.get("kind") == "anti" else ""
    return (f"The app cannot YET follow this column through this kind of join ({named}). Here it is {join_phrase(reason)}. "
            f"The tables behind it may change in a way the app cannot describe{clause}. Check them before you confirm.")
