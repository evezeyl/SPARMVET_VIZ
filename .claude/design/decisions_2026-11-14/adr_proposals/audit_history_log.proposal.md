# Proposal: audit history log and who/when on audit steps (N7-2)

**Status:** PROPOSAL. Not in the ADR log. It enters `.claude/knowledge/architecture_decisions.md` only when Eve says yes on the ADR file.
**Decision it records:** Eve, 2026-11-15 (channel M118): "DECIDED N7-2: yes to the wording" (the wording of channel M101, N7(2)).
**Tracked in:** `.claude/tasks/tasks.md` section 7 (line N7-2) and section 6 (AUDIT-HISTORY-LOG-1).

## Proposed text

**Eve, 2026-11-15: the final audit steps carry who (initials) and when. They are the record that matters, and their export does not depend on any log.** A history log `audit_history_log` (creations, removals, reverts, each with time and initials) may be appended as a separate optional part. It is written by default. It is never mixed into the final audit steps, and the list of final audit steps is not derived from it.

**Why:** a removed step must stay visible (tamper evidence). Only the log can show a removal, so the log is written by default. If a deployment turns it off, a removed step leaves no trace; that is the one loss, and it is a choice.

**Alternatives recorded in the review (not chosen):** deriving the list of final steps from the log (an earlier design note of 2026-11-13; reversed by this decision).

**Consequences:**
- The export of the final steps works with or without the log.
- A log that is turned off costs the record of removals, not the result.

## Open for Eve

- Yes or no to this wording on the ADR file.
