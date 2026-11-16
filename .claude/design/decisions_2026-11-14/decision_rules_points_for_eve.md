# Decision rules: points for Eve (DECISION-RULES-1, 2026-11-16)

The rules of your M150 are written (ledger, shared file, coordinator, agent files, hook). Eight points were not settled by your text. Each has two readings and a default. The default is not a decision: it is what the builder suggests, and nothing is changed for a default until you answer. Where the default differs from what is built today (points 4 and 7), the file says so. Answer by number.

## 1. Which decisions are numbered in the ledger?

- Your text says: the decisions "of the channel since 2026-11-14". The brief for the task said: from block M139 of 2026-11-16.
- Reading A: the old ledger (up to 2026-11-15, 107 lines) plus your decisions of M139 to M154. This is what was done.
- Reading B: A, plus every decision of the channel of 2026-11-14 that the old ledger does not hold.
- Default: A. I did not check the channel blocks of 2026-11-14 against the old ledger. The verification (M151 to M153) will find a missing decision.

## 2. A quoted Decisions block against the 20-line brief and the 15-line report

- `CLAUDE.md` 2.1 says a brief has at most 20 lines (more only for a complex problem) and a worker reports in 15 lines or fewer.
- Your rule D asks the brief to quote your words. Your rule for the workers asks a builder's report to end with a table, one row per decision.
- Reading A: the block and the table count inside the 20 and the 15 lines. The quotes must then be short.
- Reading B: the block and the table are outside the two limits.
- Default: A. Nothing in the files was changed to settle it.

## 3. A scout cannot save its report

- The hook accepts `NONE-CHECKED: <path>` only when the path is a saved scout report.
- A scout has no Write tool (it can only Read, Grep and Glob), so it cannot save the file.
- Reading A: the coordinator saves the scout's short report under `tmpAI/` (the hook allows this) or a scribe does.
- Reading B: the scout gets a Write tool for `tmpAI/` only. This changes an agent file.
- Default: A. No agent file was changed.

## 4. Panel agents and general agents are not covered by the hook

- The hook checks the Decisions block only for `builder`, `builder-opus` and `reviewer`. Your text names these three.
- A coordinator can start a general agent (for example `general-purpose` with `model: sonnet`) and give it a builder's work. The hook lets it through without a block. This is a way around the rule.
- Panel agents only recommend, so they matter less.
- Reading A: leave it as your text says (three agents).
- Reading B: gate every agent except `scout`, `scribe` and the `panel-*` agents. The general agents are then covered.
- Default: B, because A leaves a way around the rule. It is a small change in the hook and its tests.

## 5. `agent_dispatch_howto.md` is not edited

- Your M150 names no text for the howto. In M149 you asked for a proposal.
- The howto (sections 6 and 7) says what the hook refuses. It does not yet mention the Decisions block or NONE-CHECKED.
- Reading A: add a short section to the howto (the block, NONE-CHECKED, the three agents).
- Reading B: leave the howto; `decision_compliance.md` is the place.
- Default: A. Until then the howto is out of date on one point.

## 6. A number on the heading line is enough for the hook

- A brief with the single line `Decisions: D-0001` passes. So does a heading that only mentions a number, such as `DECISIONS (see D-0001)`, with no decision lines under it.
- The hook checks the form only. The reviewer checks the content.
- Reading A: leave it.
- Reading B: the hook asks for at least one number on a line below the heading.
- Default: A. The reviewer reads the block anyway (rule E, checkpoint 3).

## 7. An empty line right after the heading makes the block empty

- The block ends at the first empty line. If the writer leaves one empty line after `Decisions`, the numbers below are not counted and the brief is refused. The refusal says the block holds no number.
- Reading A: leave it and say it in the rules (section 6 of `decision_compliance.md` now says so).
- Reading B: the hook skips empty lines directly after the heading.
- Default: B, because the writer cannot see why it was refused.

## 8. Two more choices made in the build

- The ledger path `.claude/knowledge/decision_ledger.md` is only the example of M150. Reading A: keep it. Reading B: another folder. Default: A.
- A ledger that is missing or unreadable refuses a builder or reviewer call, because a check that cannot run must not pass. The other rules of the hook let the call through when they fail. Reading A: refuse (as built). Reading B: let the call through and warn. Default: A.
