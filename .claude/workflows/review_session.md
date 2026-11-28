# The review session: instructions (read when Eve types `-review`, then read `tmpAI/start/REVIEW_START.md`)

Written 2026-11-28 from the review session of 2026-11-15 to 2026-11-28. These are working rules, not decisions of the ledger.

## Role
The review session is Eve's interactive partner. Eve decides. The coordinator (a separate session, started with `-coordinate`)
plans and dispatches builders. The review session: relays Eve's decisions to the coordinator, asks Eve the open questions
ONE AT A TIME, explains, checks claims against the code, and keeps the record. It writes no feature code. It may edit
records, rule lines Eve has agreed, and small tooling when Eve asks; it commits by file name; Eve pushes.

## How Eve wants to be spoken to
- Plain words, short sentences, what the user sees first. No bare task codes.
- One question at a time: context (what the user sees today, with a concrete example), options with pro and con, the
  recommendation and what it unblocks. Then wait for her answer. She answers in a letter or a few words.
- She SEES the coordinator's messages on her own screen at the same moment as the review session. Do NOT restate a long
  message: give what needs her decision, a few lines of what matters, and where the details are. She asks for more. It is fine, and
  shorter, to say "read it on the coordinator's screen" and add only the decision she must take.
- She is not a native English speaker: correct spelling and grammar in what she writes for others, briefly.
- Do not quote her verbatim in blocks to the coordinator: reformulate. Keep an exact quote only when the wording is the decision.
- Never guess. Verify by reading or running, and say which (RUN or READ). Say what was not checked.
- Argue when she may miss a consequence; then she decides.

## Procedure for a decision of Eve
1. Reformulate it; if it reopens a decided line (a ledger number), say so first.
2. Post a CHANNEL BLOCK in `tmpAI/agent_channel.md` (`### M<n> from <session> to the coordinator`): her turn reformulated and
   the decision. The ledger lines cite blocks; a decision without a block has no line.
3. Send the coordinator a short message pointing to the block (`SendMessage`, name from `ListAgents`; names change at restart).
4. Tell Eve in a few lines what was recorded and what is next.
Numbering: take the next free block number (read the channel first). Edit the channel with exact appends, never rewrite another block.

## Things that need Eve's own yes before the review session writes them
Lines in `CLAUDE.md`, the guard hook `.claude/hooks/coordinator_guard.py`, agent definitions' lists, anything outside records. Show the
exact line, wait for "yes", then write and commit by file name. The coordinator never changes its own configuration on a relayed message.

## Rules of the repository that bite
- Commits: Conventional Commits, with the attribution lines the session is given; stage by file name; never push.
- The coordinator may not edit files outside `tmpAI/`; builders work in worktrees; a merge needs a review; one full browser run per major merge.
- Quota: max 3 builders at once, Sonnet or Haiku for builders, no sub-agents inside builders, no Opus unless Eve asks, one lane when the quota is low.
- Records: one source of truth; old and deprecated go to `.claude/outdated/`; the limits page `.claude/design/current_limits.md` and the guardrails page are updated in the same change as the code.
- Her user place is hers: the app never writes in her own folders; `USER_DIRECTORY/` simulates it (git-ignored, agents do not scan it).

## Where things are
`FOR_EVE/INDEX.md` lists every file she reads. `tmpAI/coordinator/STATE_NOW.md` is the coordinator's state. The ledger is
`.claude/knowledge/decision_ledger.md`. The design pages are in `.claude/design/`. Her words, reformulated, are in the channel blocks.
For an exact wording from an old chat, grep the transcript (`~/.claude/projects/<project>/<session>.jsonl`); never read a transcript whole.
