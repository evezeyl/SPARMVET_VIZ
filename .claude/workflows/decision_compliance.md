# Decision compliance: what Eve decided is what we build (Eve, 2026-11-16)

**How to read this file.** Her text is in sections 1, 2, 3 and in the quoted hook rule of section 6 (channel block M150). Everything marked **[ADDED]** was written by the builder on 2026-11-16, it is not her text, and she accepts or removes it; section 8 lists every added place.

**[ADDED]** Every agent reads this file, with `.claude/workflows/agent_principles.md`, before it starts. Not every agent loads `CLAUDE.md`, so what applies to you is here.

**[ADDED]** Authority: **decided by Eve on 2026-11-16** (agent channel block M150; ledger line `D-0125`). The same rules, for the coordinator, are in `.claude/agents/coordinator.md`; the pointer is in `CLAUDE.md` section 2.1. The list of rule-file changes holds the rows of these files (`.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md`, status "confirmed by Eve, 2026-11-16").

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

## 4. The four checkpoints (rule E, summarised) **[ADDED]**

**[ADDED]** This table is the builder's summary of rule E, not her text. If it and rule E differ, rule E holds.

| # | When | Who | What | Result |
|---|---|---|---|---|
| 1 | Before a brief | a `scout` | Lists the decisions (ledger numbers) and the governing rule files (through the `doc:` links in `@deps`) for the task and its files | The coordinator writes the "Decisions" block of the brief from it |
| 2 | Before a question to Eve | a cheap agent, then the review session | Tags the question DECIDED / DISSOLVED / OPEN | Only OPEN goes on |
| 3 | Before a merge | a `reviewer` | Each decided point: complied / contradicted / not covered, with the decision text and the code line (a "complied" without both is invalid); plus a check from the other side: the decisions that govern the files of the diff | A contradiction stops the merge; a "not covered" is asked to Eve |
| 4 | After a merge that CHANGES BEHAVIOUR (not a pure test or records merge) | a `scribe` | Docs, tests, records, `@deps`, and the UML and ADR sync (`workspace_standard.md`) match | A mismatch is fixed or reported |

## 5. The ledger of decisions **[ADDED]**

**[ADDED]** The whole section is the builder's description of the ledger (M150 point 5 asks for the numbering and proposes the path only).

- **Where:** `.claude/knowledge/decision_ledger.md` (tracked in git). The path is a proposal that Eve confirms; until then it is the path every script and the hook read.
- **Form:** one decision per line, a number `D-0001`, a date, the area, the decision, the source, who took it (`EVE`, `AGENT`, `NOT STATED`, `REVIEW SESSION`), the status, the relation to other decisions, her words and the old key. Only a line taken by EVE is `DECIDED`; an AGENT line is `PROVISIONAL` and goes back to her; a line of a plan that the review session relayed and that she did not say in her words is `RELAYED` (not decided).
- **Read it:** `./.venv/bin/python assets/scripts/decision_ledger.py list` (`--status PROVISIONAL` for the provisional ones); `./.venv/bin/python assets/scripts/decision_ledger.py check D-0001 D-0108` says which numbers do not exist. The file explains its own format at the top.
- **Add to it:** a scribe, the same day, with her words quoted. A later decision names the number it replaces. Nobody rewrites a line.

## 6. The "Decisions" block of a brief (what the hook checks)

**[ADDED]** The syntax of the block, its example and the NONE-CHECKED form below are the builder's; only the quoted hook rule is hers.

**[ADDED]** A brief to a `builder`, a `builder-opus` or a `reviewer` has a "Decisions" block: a line that starts with the word `Decisions` (any capitals, optional `#` marks or `**`, optional colon or a bracket after it), then the decisions, one per line, each with its number and her words, up to the next blank line or heading (an empty line right after the heading ends the block). The block quotes; it does not paraphrase (rule D). Example (the two numbers are real lines of the ledger, the words are hers):

```
Decisions
- D-0112: "yes - if same identity favor the one that has higest overlap/coverage."
- D-0113: "yes - with a comment in the recipe. yes add the step in the recipe."
```

**[ADDED]** When the coordinator really has no decision for the task (checked by a scout), the brief says so with a line `NONE-CHECKED: <path>`, where the path is the saved report of the scout that checked: a regular file inside the project folder (for example under `tmpAI/`), not a directory, not a file outside the project, not the ledger itself.

The hook (`.claude/hooks/coordinator_guard.py`, for a session in coordinator mode only), as decided in M150 point 4: "for `builder`, `builder-opus` and `reviewer` calls the hook refuses a brief that has neither a "Decisions" block with numbers that exist in the ledger nor "NONE-CHECKED: <path of a scout report that exists>". Scouts and scribes are exempt. The reviewer still checks the content (the hook checks only the form)." **[ADDED]** Panel agents are not part of the hook until Eve says so.

## 7. Traceability **[ADDED]**

**[ADDED]** The section is the builder's. The first bullet restates `CLAUDE.md` section 2.1 (standing rule 5); the second is a new rule that is not in M150 (M150 point 6 says only that the rule-file and ADR text of this change is on her list).

- Every worker keeps `tmpAI/progress.md` in its worktree (done, next, findings); after each dispatch, report and merge a scribe updates the handoff and `tasks.md` (`CLAUDE.md` section 2.1, standing rule 5).
- A change to this file, to `coordinator.md`, to the one line in the agent files or to the hook is a rule-file change: it gets a row in `RULE_FILE_CHANGES.md`.

## 8. Added by the builder, 2026-11-16, not Eve's text: she accepts or removes it

Her text: the goal (section 1), rules A to H (section 2), the workers (section 3), the hook rule quoted in section 6. Everything else in this file and in `.claude/agents/coordinator.md` was added by the builder:

1. The "How to read this file" paragraph, the paragraph "Every agent reads this file ... what applies to you is here" (including the remark that not every agent loads `CLAUDE.md`) and the "Authority" paragraph at the top.
2. Section 4, the summary table of rule E.
3. Section 5, the description of the ledger (path, form, how to read it, how to add).
4. In section 6: the syntax of the "Decisions" block, its example, the NONE-CHECKED form and its limits, and the sentence "Panel agents are not part of the hook until Eve says so".
5. Section 7: the restatement of the standing rule 5 and the new rule that a change to these files gets a row in the list of rule-file changes.
6. In `coordinator.md`: the sentence "Read `.claude/workflows/decision_compliance.md` at the start (...)" and the sentence "The goal, quoted from it: ...", which wrap her text; and the section title (marked there).
