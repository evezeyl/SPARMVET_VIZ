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

- **Where:** `.claude/knowledge/decision_ledger.md` (tracked in git). The path was a proposal; Eve kept it on 2026-11-16 (`D-0158`: "8. both defaults."); it is the path every script and the hook read.
- **Form:** one decision per line, a number `D-0001`, a date, the area, the decision, the source, who took it (`EVE`, `AGENT`, `NOT STATED`, `REVIEW SESSION`), the status, the relation to other decisions, her words and the old key. Only a line taken by EVE is `DECIDED`; an AGENT line is `PROVISIONAL` and goes back to her; a line of a plan that the review session relayed and that she did not say in her words is `RELAYED` (not decided).
- **Read it:** `./.venv/bin/python assets/scripts/decision_ledger.py list` (`--status PROVISIONAL` for the provisional ones); `./.venv/bin/python assets/scripts/decision_ledger.py check D-0001 D-0108` says which numbers do not exist. The file explains its own format at the top.
- **Add to it:** a scribe, the same day, with her words quoted. A later decision names the number it replaces. Nobody rewrites a line. (One exception, written in the ledger itself: a relayed line that she later confirmed changes its taken by, status and relation only, `D-0161`.)
- **A brief quotes only a line that is DECIDED and taken by EVE** (`D-0159`): `./.venv/bin/python assets/scripts/decision_ledger.py list --status DECIDED` lists them, `check --decided D-0001 ...` checks numbers. A proposal of hers that waits for her confirmation has no number: it is in the list "Asked, not decided" at the end of the ledger.

## 6. The "Decisions" block of a brief (what the hook checks)

**[ADDED]** The syntax of the block, its example and the NONE-CHECKED form below are the builder's; only the quoted hook rule is hers.

**[ADDED]** A brief to any agent that is gated (every agent except `scout`, `scribe` and the `panel-*` agents, a general agent included; `D-0156`) has a "Decisions" block: a line that starts with the word `Decisions` (any capitals, optional `#` marks or `**`, optional colon or a bracket after it), then the decisions, one list item per decision, each with its number and, in the same item, words of THAT ledger line between quotation marks (`D-0166`, see "What quoted words that appear in the line means" below), up to the next blank line or heading (empty lines right after the heading are skipped, `D-0157`). Only a number whose ledger line is DECIDED and taken by EVE is accepted (`D-0159`): a RELAYED, PROVISIONAL or NOT-STATED number is refused, and the refusal names the number and its status. The block quotes; it does not paraphrase (rule D). Example (the two numbers are real lines of the ledger, the words are hers):

```
Decisions
- D-0112: "yes - if same identity favor the one that has higest overlap/coverage."
- D-0113: "yes - with a comment in the recipe. yes add the step in the recipe."
```

**[ADDED]** When the coordinator really has no decision for the task (checked by a scout), the brief says so with a line `NONE-CHECKED: <path>`, where the path is the saved report of the scout that checked: a regular file inside the project folder (for example under `tmpAI/`), not a directory, not a file outside the project, not the ledger itself. A scout has no Write tool: the coordinator or a scribe saves the scout's short report under `tmpAI/` and the line names that file (`D-0155`). **What `NONE-CHECKED` means (`D-0165`).** Her addition to point 5: "no decisions that to be reported when one needed". **[ADDED by an agent, not Eve's words]** So `NONE-CHECKED` says that no decision applies and none is needed. Where no decision exists and one is needed, that is an open point: it goes to the numbered list for her and is never hidden behind `NONE-CHECKED` or guessed.

The hook (`.claude/hooks/coordinator_guard.py`, for a session in coordinator mode only), as decided in M150 point 4: "for `builder`, `builder-opus` and `reviewer` calls the hook refuses a brief that has neither a "Decisions" block with numbers that exist in the ledger nor "NONE-CHECKED: <path of a scout report that exists>". Scouts and scribes are exempt. The reviewer still checks the content (the hook checks only the form)." **[CHANGED by Eve, 2026-11-16, `D-0156` to `D-0159`, builder's wording]** The hook now gates every agent that would run except `scout`, `scribe` and the panel agents (`panel-scientist`, `panel-architect`, `panel-developer`, `panel-user`, named one by one); a missing or unreadable ledger refuses the call. **[ADDED by an agent, not Eve's words: task DECISION-RULES-2, fix round, the coordinator's instruction]** The ledger is read first, so a valid `NONE-CHECKED` line does not let a call through when the ledger is missing, unreadable or malformed (`D-0158`); a valid `NONE-CHECKED` line does not excuse a number in a Decisions block that is not DECIDED by EVE (`D-0159`); numbers are read without regard to case.

**What "quoted words that appear in that ledger line" means (`D-0166`; her decision is point 6, option C; this definition is the builder's proposal, not her words).**

1. A list item of the block starts at a line that begins, after an optional list marker (`-`, `*`, `+`, `1.`), with a number `D-nnnn` (case does not matter); the lines after it that are not themselves list items belong to it. The heading line is no item: a number there, or inside another item, has no quoted words and is refused.
2. A quote is text between straight (`"..."`) or curly double quotation marks in the item.
3. A quote **appears** in the line when each of its pieces is a contiguous piece of the text of that line and the pieces are found, in order and without overlap, in ONE field of THAT ledger line: its decision field or its evidence field (her words). A piece is the text between two cuts; a cut is `...` or the ellipsis character. Ignored when comparing: upper and lower case, every quotation mark (the quote's own and those inside the line), the difference of straight and curly apostrophes, and runs of spaces. Nothing else is ignored: a different word, a missing word or another order does not appear. (The brief asked to ignore the surrounding quotation marks; ignoring all of them also lets a quote cross the nested quotation marks of her words.)
4. A quote **counts** when its pieces together hold at least 12 characters and each piece at least 4. Why 12: the shortest words of hers that a brief quotes ("ok - decided") are 12 characters; shorter ones ("yes", "a)", "4. B.") occur in many lines and do not show that the writer read the line. Why 4 per piece: a cut must not reduce a quote to scraps that fit anywhere. A quote that does not count is ignored, not refused.
5. The item is accepted when it has at least one quote that counts and every quote that counts appears in that line. Otherwise the refusal says in plain words what to add (words from that line between quotation marks, at least 12 characters) or that the words quoted are not in that line, and shows the start of the ledger line. A number that is not DECIDED and taken by EVE is refused with its status even when its quote is true (`D-0159`). A valid `NONE-CHECKED` line excuses none of this.

Example: `- D-0050` is refused (no quoted words). `- D-0050: "no silent errors allowed"` is refused (the words are not in that line: it says "No silent error that is the rule."). `- D-0050: "No silent error that is the rule."` and `- D-0050: "no silent error"` are accepted.

## 7. Traceability **[ADDED]**

**[ADDED]** The section is the builder's. The first bullet restates `CLAUDE.md` section 2.1 (standing rule 5); the second is a new rule that is not in M150 (M150 point 6 says only that the rule-file and ADR text of this change is on her list).

- Every worker keeps `tmpAI/progress.md` in its worktree (done, next, findings); after each dispatch, report and merge a scribe updates the handoff and `tasks.md` (`CLAUDE.md` section 2.1, standing rule 5).
- A change to this file, to `coordinator.md`, to the one line in the agent files or to the hook is a rule-file change: it gets a row in `RULE_FILE_CHANGES.md`.

## 8. Added by the builder, 2026-11-16, not Eve's text: she accepts or removes it

Her text: the goal (section 1), rules A to H (section 2), the workers (section 3), the hook rule quoted in section 6. Everything else in this file and in `.claude/agents/coordinator.md` was added by the builder:

1. The "How to read this file" paragraph, the paragraph "Every agent reads this file ... what applies to you is here" (including the remark that not every agent loads `CLAUDE.md`) and the "Authority" paragraph at the top.
2. Section 4, the summary table of rule E.
3. Section 5, the description of the ledger (path, form, how to read it, how to add).
4. In section 6: the syntax of the "Decisions" block, its example, the NONE-CHECKED form and its limits, and the sentence "Panel agents are not part of the hook until Eve says so" (replaced on 2026-11-16 by `D-0156`, see section 9).
5. Section 7: the restatement of the standing rule 5 and the new rule that a change to these files gets a row in the list of rule-file changes.
6. In `coordinator.md`: the sentence "Read `.claude/workflows/decision_compliance.md` at the start (...)" and the sentence "The goal, quoted from it: ...", which wrap her text; and the section title (marked there).
7. Added in the first round after her answers (2026-11-16, ledger `D-0153` to `D-0163`), builder's wording of her decisions: section 9; in section 6 the paragraph marked "CHANGED by Eve", the sentence on how the hook gates agents, and the text of what a scout report is saved by; in section 5 the exception line and the line on quoting only DECIDED lines.
8. Added in the fix round (the coordinator's instruction, not hers): the hook reads the ledger first (a valid `NONE-CHECKED` line does not let a call through when the ledger cannot be read, `D-0158`); a valid `NONE-CHECKED` line does not excuse a number that is not DECIDED (`D-0159`); numbers are read without regard to case.
9. Added in round 2 (2026-11-16, ledger `D-0164` to `D-0166`): the meaning of `NONE-CHECKED` as worded in section 6 (her addition is `D-0165`; the wording is an agent's), the definition of quoted words that appear in a ledger line with its minimums 12 and 4 (the numbers and the "ignored when comparing" list are the builder's proposal), the example, and `agent_dispatch_howto.md` section 8.

## 9. Decided by Eve after the first version, 2026-11-16 (ledger `D-0153` to `D-0166`; channel M156 to M158)

**[ADDED]** The decisions below are hers (her turns are quoted in the ledger lines named). The sentences that write them into the files are the builder's.

- **No length limit** on briefs, worker reports, the handoff and the agent channel (`D-0154`, `D-0160`). Her words: "try to stay concise but do not sacrify to clarity" (`D-0154`) and "should not have strict limits - bypass limits when necessary - but keep precise and upated" (`D-0160`); her spelling is kept. The review session's sentence beside them: as long as needed to be clear and complete; no padding; the content stays precise and current (wording of the review session, not Eve's words); she has not corrected it. So the Decisions block and the table of a builder's report need not be shortened to a number [ADDED by an agent, not Eve's words]. For the handoff and the channel the review session also wrote (M157, not Eve's words): the open state stays at the top; done items are removed or archived the same day; a long file is cleaned by its owner and not cut mid-content [ADDED by an agent, not Eve's words: the handoff stays append-only, so there "archived" means moved, not deleted]. The `250 words` of a panel viewpoint is the panel's own limit and is not part of this decision.
- **Who is gated** (`D-0156`): every agent except `scout`, `scribe` and the four panel agents. A general agent started with `model: haiku` or `model: sonnet` needs a Decisions block like a builder.
- **Which numbers** (`D-0159`): only lines that are DECIDED and taken by EVE. `./.venv/bin/python assets/scripts/decision_ledger.py list --status DECIDED` lists them; `check --decided D-0001 ...` checks a list.
- **Empty lines after the heading** (`D-0157`) are skipped.
- **A scout's report** (`D-0155`): saved under `tmpAI/` by the coordinator or a scribe; a `NONE-CHECKED` line names that file. [ADDED by an agent, not Eve's words: reading A leaves the scout without a Write tool, so the scout and scribe files do not mention it.]
- **The ledger** (`D-0153`, `D-0158`): the old ledger plus her decisions of M139 to M154; the path `.claude/knowledge/decision_ledger.md` is kept; a missing or unreadable ledger refuses the call.
- **Added after round 2, 2026-11-16 (ledger `D-0164` to `D-0166`; channel M158):** point 5 = A (`D-0164`): the howto has a section on the Decisions block (`agent_dispatch_howto.md` section 8); her addition (`D-0165`): where no decision exists and one is needed, that is reported to her; `NONE-CHECKED` means no decision applies and none is needed (wording of the review session, M158, not Eve's words) (section 6); point 6 = C (`D-0166`): each number must be followed by quoted words that appear in that ledger line (section 6, the definition). Points 1 to 9 of `.claude/design/decisions_2026-11-14/decision_rules_points_for_eve.md` are now all answered.
