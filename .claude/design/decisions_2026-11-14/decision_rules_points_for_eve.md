# Decision rules: points for Eve (DECISION-RULES-1, 2026-11-16)

The rules of your M150 are written (ledger, shared file, coordinator, agent files, hook). Eight points were not settled by your text. Each has two readings and a default. The default is not a decision: it is what the builder suggests, and nothing is changed for a default until you answer. Where the default differs from what is built today (points 4 and 7), the file says so. Answer by number.

**Status, 2026-11-16 (DECISION-RULES-2):** Eve answered all nine points in her review session (her turns cd1b0ac7 #2048, #2087, and for points 5 and 6 #2120 and #2137; relayed in M156, M157 and M158); each answer is a ledger line (points 5 and 6: `D-0164` to `D-0166`).

## 1. Which decisions are numbered in the ledger?

- Your text says: the decisions "of the channel since 2026-11-14". The brief for the task said: from block M139 of 2026-11-16.
- Reading A: the old ledger (up to 2026-11-15, 107 lines) plus your decisions of M139 to M154. This is what was done.
- Reading B: A, plus every decision of the channel of 2026-11-14 that the old ledger does not hold.
- Default: A. I did not check the channel blocks of 2026-11-14 against the old ledger. The verification (M151 to M153) will find a missing decision.

**ANSWERED, Eve, 2026-11-16: "1.A" (ledger D-0153).** Reading A.

## 2. A quoted Decisions block against the 20-line brief and the 15-line report

- `CLAUDE.md` 2.1 says a brief has at most 20 lines (more only for a complex problem) and a worker reports in 15 lines or fewer.
- Your rule D asks the brief to quote your words. Your rule for the workers asks a builder's report to end with a table, one row per decision.
- Reading A: the block and the table count inside the 20 and the 15 lines. The quotes must then be short.
- Reading B: the block and the table are outside the two limits.
- Default: A. Nothing in the files was changed to settle it.

**ANSWERED, Eve, 2026-11-16: "2. Remove the brief limit - try to stay concise but do not sacrify to clarity."; and on the handoff and the channel: "should not have strict limits - bypass limits when necessary - but keep precise and upated" (ledger D-0154, D-0160).** Neither A nor B: the limits are removed, so the question of the block and the table inside a limit no longer arises. Written into `CLAUDE.md` 2.1, the agent files, the howto, `rules_agent_channel.md` and `decision_compliance.md` section 9 (rows R145 to R159 of the rule-file list).

## 3. A scout cannot save its report

- The hook accepts `NONE-CHECKED: <path>` only when the path is a saved scout report.
- A scout has no Write tool (it can only Read, Grep and Glob), so it cannot save the file.
- Reading A: the coordinator saves the scout's short report under `tmpAI/` (the hook allows this) or a scribe does.
- Reading B: the scout gets a Write tool for `tmpAI/` only. This changes an agent file.
- Default: A. No agent file was changed.

**ANSWERED, Eve, 2026-11-16: "3. A. tmpAI is what AI tools need so its a good place to use." (ledger D-0155).** Reading A: the coordinator or a scribe saves the scout's report under `tmpAI/`.

## 4. Panel agents and general agents are not covered by the hook

- The hook checks the Decisions block only for `builder`, `builder-opus` and `reviewer`. Your text names these three.
- A coordinator can start a general agent (for example `general-purpose` with `model: sonnet`) and give it a builder's work. The hook lets it through without a block. This is a way around the rule.
- Panel agents only recommend, so they matter less.
- Reading A: leave it as your text says (three agents).
- Reading B: gate every agent except `scout`, `scribe` and the `panel-*` agents. The general agents are then covered.
- Default: B, because A leaves a way around the rule. It is a small change in the hook and its tests.

**ANSWERED, Eve, 2026-11-16: "4. B." (ledger D-0156).** Built in `.claude/hooks/coordinator_guard.py`: every agent that would run is gated except `scout`, `scribe` and the four panel agents (listed one by one, so that a name only starting with `panel-` is gated).

## 5. `agent_dispatch_howto.md` is not edited

- Your M150 names no text for the howto. In M149 you asked for a proposal.
- The howto (sections 6 and 7) says what the hook refuses. It does not yet mention the Decisions block or NONE-CHECKED.
- Reading A: add a short section to the howto (the block, NONE-CHECKED, the three agents).
- Reading B: leave the howto; `decision_compliance.md` is the place.
- Default: A. Until then the howto is out of date on one point.

**ANSWERED, Eve, 2026-11-16: "5 - ok - no decisions that to be reported when one needed ." (ledger D-0164, and her addition D-0165).** Reading A: the section is added (`agent_dispatch_howto.md` section 8). Her addition: where no decision exists and one is needed, that must be reported to her; `NONE-CHECKED` means no decision applies and none is needed (also in `decision_compliance.md` section 6).

## 6. A number on the heading line is enough for the hook

- A brief with the single line `Decisions: D-0001` passes. So does a heading that only mentions a number, such as `DECISIONS (see D-0001)`, with no decision lines under it.
- The hook checks the form only. The reviewer checks the content.
- Reading A: leave it.
- Reading B: the hook asks for at least one number on a line below the heading.
- Default: A. The reviewer reads the block anyway (rule E, checkpoint 3).

**ANSWERED, Eve, 2026-11-16: "6. 3" and "C was 3" (#2120, #2137; ledger D-0166).** Option C: each number must be followed, in the same list item, by quoted words that appear in that ledger line; a bare number is refused. Built in the hook; the exact definition of "appear" is in `decision_compliance.md` section 6 (the builder's proposal, not her words: at least 12 characters, `...` for a cut, case and quotation marks ignored). First: her earlier words were "unclear - should it be human redible - I have no idea what the number represent." (#2048).

## 7. An empty line right after the heading makes the block empty

- The block ends at the first empty line. If the writer leaves one empty line after `Decisions`, the numbers below are not counted and the brief is refused. The refusal says the block holds no number.
- Reading A: leave it and say it in the rules (section 6 of `decision_compliance.md` now says so).
- Reading B: the hook skips empty lines directly after the heading.
- Default: B, because the writer cannot see why it was refused.

**ANSWERED, Eve, 2026-11-16: "7. B." (ledger D-0157).** The hook skips the empty lines right after the heading.

## 8. Two more choices made in the build

- The ledger path `.claude/knowledge/decision_ledger.md` is only the example of M150. Reading A: keep it. Reading B: another folder. Default: A.
- A ledger that is missing or unreadable refuses a builder or reviewer call, because a check that cannot run must not pass. The other rules of the hook let the call through when they fail. Reading A: refuse (as built). Reading B: let the call through and warn. Default: A.

**ANSWERED, Eve, 2026-11-16: "8. both defaults." (ledger D-0158).** The path stays; a missing or unreadable ledger refuses the call.

## 9. A relayed or provisional number is accepted by the hook

**Point 9** (the ninth point of the review session's list of 2026-11-16, not in the eight above): the hook accepted any number that exists in the ledger, also a RELAYED or PROVISIONAL one. Reading A: keep. Reading B: accept only numbers whose line is DECIDED and taken by EVE. **ANSWERED, Eve, 2026-11-16: "9. B" (ledger D-0159).** A refusal names the number and its status.
