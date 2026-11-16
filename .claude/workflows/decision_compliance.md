# Decision compliance: what Eve decided is what we build (Eve, 2026-11-16)

Every agent reads this file, with `.claude/workflows/agent_principles.md`, before it starts. Not every agent loads `CLAUDE.md`, so what applies to you is here.

Authority: **decided by Eve on 2026-11-16** (agent channel block M150; ledger line `D-0125`). The same rules, for the coordinator, are in `.claude/agents/coordinator.md`; the pointer is in `CLAUDE.md` section 2.1. The list of rule-file changes holds the rows of these files (`.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md`, status "confirmed by Eve, 2026-11-16").

## 1. The goal (the text Eve approved: "1. ok")

> We deliver an app that is well developed, architecture-wise, and that makes correct and reproducible science possible. The science is transparent: the same data and recipe give the same result, and nothing changes a result silently. The software informs the user and does not choose for the user. The user is responsible for the choices and decides with the information in front of them. We do not do half fixes. These rules exist so that what we build is what Eve decided, built correctly once, with its consequences understood by everyone who builds it.

## 2. The rules

- **A.** Consistency with Eve's decisions is part of the coordinator's job; the coordinator ORGANISES it and does not do the checking (cost). In a real doubt it may read the cited decision lines (at most 100); it never checks code; code is checked by agents.
- **B.** One source of truth: every decision of Eve has a NUMBER, a date, her words quoted, who took it (only decisions she took or reviewed are DECIDED; an agent's choice is PROVISIONAL); a scribe writes it into the ledger the same day; a later decision names the one it replaces; a reversal is also a decision.
- **C.** Read, do not guess, and verify the code: a claim about what she decided comes from a source an agent READ (file and line); a claim about what code does comes from an agent that read or ran it; labels read / ran / reasoned / assumed; an assumed claim is never built.
- **D.** Briefs QUOTE decisions (numbers and her words) in a "Decisions" block; the coordinator never paraphrases a decision.
- **E.** Four checkpoints, all by agents: (1) before a brief: a scout lists the decisions and the governing rule files (through the `doc:` links in `@deps`) for the task and its files; (2) before a question to Eve: a cheap agent tags it DECIDED / DISSOLVED / OPEN, only OPEN goes on (through the review session, which also checks the tag); (3) before a merge: a reviewer checks each decided point as complied / contradicted / not covered with decision text and code line (a "complied" without both is invalid), plus a check from the other side (the decisions that govern the files of the diff); a contradiction stops the merge; (4) after a merge that CHANGES BEHAVIOUR (not pure test or records merges): a scribe checks that docs, tests, records, `@deps` and the UML and ADR sync (`workspace_standard.md`) match.
- **F.** Logic first: before a feature on the audit, the exports or the lineage an agent writes the succession of operations in numbered steps with one example, checked against the intent document.
- **G.** Ask plainly: say what was understood, the readings and an example; one numbered list; a default is never a decision.
- **H.** A contradiction between records stops the work and is reported at once; nobody resolves it silently.

## 3. The workers

Text of M150 point 3, in sentences:

- every agent file (builder, builder-opus, reviewer, scout, scribe, panel-*) gets one line: "read `agent_principles.md` and `decision_compliance.md` first; read the Decisions block of the brief".
- The brief names the governing rule files.
- A builder's report ends with a table: each decision of the block, how the code complies, file:line, test name; a reviewer verifies it independently and does not trust it.
- A builder that finds the brief contradicting a decision or a rule stops and reports.
- A builder also answers in its report "what happens to X after this change?" for one consequence the brief names; the reviewer checks the answer by running.

## 4. The four checkpoints (rule E, summarised)

| # | When | Who | What | Result |
|---|---|---|---|---|
| 1 | Before a brief | a `scout` | Lists the decisions (ledger numbers) and the governing rule files (through the `doc:` links in `@deps`) for the task and its files | The coordinator writes the "Decisions" block of the brief from it |
| 2 | Before a question to Eve | a cheap agent, then the review session | Tags the question DECIDED / DISSOLVED / OPEN | Only OPEN goes on |
| 3 | Before a merge | a `reviewer` | Each decided point: complied / contradicted / not covered, with the decision text and the code line (a "complied" without both is invalid); plus a check from the other side: the decisions that govern the files of the diff | A contradiction stops the merge; a "not covered" is asked to Eve |
| 4 | After a merge that CHANGES BEHAVIOUR (not a pure test or records merge) | a `scribe` | Docs, tests, records, `@deps`, and the UML and ADR sync (`workspace_standard.md`) match | A mismatch is fixed or reported |

## 5. The ledger of decisions

- **Where:** `.claude/knowledge/decision_ledger.md` (tracked in git). The path is a proposal that Eve confirms; until then it is the path every script and the hook read.
- **Form:** one decision per line, a number `D-0001`, a date, the area, the decision, the source, who took it (`EVE`, `AGENT`, `NOT STATED`), the status, the relation to other decisions, her words and the old key. Only a line taken by EVE is `DECIDED`; an AGENT line is `PROVISIONAL` and goes back to her.
- **Read it:** `./.venv/bin/python assets/scripts/decision_ledger.py list` (`--status PROVISIONAL` for the provisional ones); `./.venv/bin/python assets/scripts/decision_ledger.py check D-0001 D-0108` says which numbers do not exist. The file explains its own format at the top.
- **Add to it:** a scribe, the same day, with her words quoted. A later decision names the number it replaces. Nobody rewrites a line.

## 6. The "Decisions" block of a brief (what the hook checks)

A brief to a `builder`, a `builder-opus` or a `reviewer` has a "Decisions" block: a line that starts with the word `Decisions` (any capitals, optional `#` marks or `**`, optional colon or a bracket after it), then the decisions, one per line, each with its number and her words, up to the next blank line or heading. The block quotes; it does not paraphrase (rule D). Example (the two numbers and the words are real lines of the ledger):

```
Decisions
- D-0112: "Best hit = highest identity first; among equal identities, the one with the highest overlap (coverage)."
- D-0113: "add the `polars_drop_nans` step before the ResFinder filter, with a COMMENT in the recipe."
```

When the coordinator really has no decision for the task (checked by a scout), the brief says so with a line `NONE-CHECKED: <path>`, where the path is a file that exists: the saved report of the scout that checked.

The hook (`.claude/hooks/coordinator_guard.py`, for a session in coordinator mode only), as decided in M150 point 4: "for `builder`, `builder-opus` and `reviewer` calls the hook refuses a brief that has neither a "Decisions" block with numbers that exist in the ledger nor "NONE-CHECKED: <path of a scout report that exists>". Scouts and scribes are exempt. The reviewer still checks the content (the hook checks only the form)." Panel agents are not part of the hook until Eve says so.

## 7. Traceability

- Every worker keeps `tmpAI/progress.md` in its worktree (done, next, findings); after each dispatch, report and merge a scribe updates the handoff and `tasks.md` (`CLAUDE.md` section 2.1, standing rule 5).
- A change to this file, to `coordinator.md`, to the one line in the agent files or to the hook is a rule-file change: it gets a row in `RULE_FILE_CHANGES.md`.
