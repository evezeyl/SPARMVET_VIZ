# Which decisions and builds match the goals (2026-11-22)

The answer to your question of D-0530: "If it is possible : if it turns out that the global overview shows that some build decisions already agreed are still in agreement with the global overview that is currently re-evaluated, to our aims, then it means that those plans will likely not be changed, and thus the build can continue when agreement between my decisions and final global overview match."

Read-only. Nothing is released by this file: the coordinator has it checked and releases a build; you can stop any build.

**The verdicts.**
- **KEEP:** matches your goals and does not depend on any open question (every option of the open questions keeps it).
- **CHANGE:** matches after the change named in the row.
- **DROP:** does not match a goal or a decision of yours.
- **NOT SURE:** depends on a question that is yours; the question is named.
- Your rule of D-0531, "We cannot choose for him..the app cannot decide the scope": anything that has the app decide the scope does not match.
- The goals are those of `GOALS_REVIEW.md` section 2: G1 to G6 from your passage (D-0528), E1 to E7 from earlier decisions. "Question N" is part 8 of `WHOLE_PICTURE.md`. Every verdict is my reading; you may object to any row.

---

## 0. KEEP builds that can start or be merged now, in this order

Each item was tested by the independent review you ordered (D-0533; `GOALS_REVIEW_sonnet.md` part C, worktree `SPARMVET_VIZ_wt_goals_sonnet`). Its answer, and mine, are in `GOALS_REVIEW.md` section 11.

1. **Slice 0, the records agree.** No code: the records that contradict each other are corrected (`DIFFERENCES.md` B2, B3). Goal: well built. **KEEP, survived the independent review.**
2. **Merge the branch `task/home-filter-follows-table`** (commit `7981a569`) after its review: the exploration filters follow the table you view, not the plot (D-0505, D-0506). On the demo, filters set under `mlst_bar` stay when you open `year_distribution`, which reads the same table. Goal: clear choices. **KEEP, survived the independent review** (its 5 test files: 88 passed, run by that review, not by me).
3. **The refusal of a result id written twice in one recipe** (`DIFFERENCES.md` A23; task `RESULT-ID-TWICE-NOT-REFUSED`): today the second entry silently replaces the first. Goal: nothing silent ("No silent error that is the rule.", D-0050). **KEEP, survived the independent review** (its probe is weak, as it says).
4. **"Remove from all the data": write only at the places the user left ticked, and say nothing about the unticked tables.** From the held branch `task/remove-from-all-ticked`, take the write at the ticked places (`apply(..., ticked=...)`); leave out its sentences about unticked tables (`_flow`, `unticked_places`), and remove the "may stay" sentences of `dev` (`libs/utils/src/utils/remove_from_all.py`). Your decisions: the user may untick ("yes the user may unthink he is responsible of its choice", D-0499); no per-table warnings about downstream effects (D-0501). **KEEP, survived the independent review** (125 tests passed on the held branch, run by that review), **with its condition:** it stays a library step, with no screen, until the measured effect can show where the entity stays. Your case shows why: six places must be unticked to keep the entity in the quality results, not two (`GOALS_REVIEW.md` section 11 a, my run).
5. **The good-practice page, with what is decided:** the limits documented (D-0461); the three gotchas (D-0508); "do not use same column names for different meanings - declare what is ID key" (D-0498); the joins the app cannot follow YET and why not to use them (D-0486). The list of operations to avoid waits for the catalogue of uncertainties (D-0464). Goals: clear choices; the author and the user. **KEEP, survived the independent review, in part:** the paragraph on the audit folder (D-0423) is moved out; it waits until the folder is built and question 30 is answered.

Everything else waits for a question of yours, or is a change or a drop: see the tables.

---

## 1. Your decisions that lead to a build

| What it is, in plain words | Ledger | Verdict | Reason, and the goal | Depends on |
|---|---|---|---|---|
| The audit recipe: a copy of the recipe that holds the audit steps in a second list; the original never changes; the id, the reason (`audit_comment`), `audit_of` | D-0102, D-0143, D-0332, D-0329, D-0321, D-0339, D-0040 | KEEP | One form of a correction, re-runnable (G1, E6). | — |
| The fingerprint (record), the `audit/` folder in the user's place, a hand edit refused | D-0333, D-0331, D-0319, D-0340, D-0422, D-0423 | KEEP for the fingerprint and the refusal; NOT SURE for the folder where the user's place cannot be written | Trust and re-run (G1, G3). D-0422 assumes that a session can be saved in every deployment (the independent review). | 30 (the folder only) |
| The audit log, always exported, with what was shown | D-0478 | KEEP | Shows "that is is a user decision" (G1, G6). What it holds exactly is my reading of questions 10, 11, 12 and 25. | — |
| The export: two ticks; an original and an audited part; the data once; the original recipe | D-0298, D-0301, D-0490, D-0492, D-0389, D-0324 | KEEP | Re-run either part (G1, G3). Whether the Publication part also holds the original recipe is question 15. The tables of the audited part must follow the audit (section 2.1b). | — |
| The original and the corrected plot both visible in the export | D-0147 | KEEP | A reader sees the effect (G3). Where: question 16 (my reading: (a)). | — |
| "Remove step": one step taken out | D-0314 | KEEP | G1. | — |
| A session of another recipe or of an older form refused; a session of an edited recipe refused | D-0312, D-0317, D-0362 | KEEP | G1. What happens to today's sessions at the change of form is question 26. | — |
| The user chooses the places where a step is written; nothing is written that is not ticked; one automatic placement, "remove from all the data" | D-0093, D-0355, D-0053, D-0022, D-0531 | KEEP | The scope is the user's (G6, D-0531). | — |
| The dialog: one line per distinct table, with its reach; tables that no result reads are lines | D-0316, D-0346, D-0347, D-0451, D-0415 part A | KEEP | The user sees what each place reaches (G5). Kept under every option of question 28. | — |
| "Tick low": the earliest places ticked by default; the lineage shown as a propagation | D-0508, D-0501 (the default) | NOT SURE | The propagation: KEEP (G5). The default ticks: which places are "the earliest" is question 1; under option (b) of question 28 the default comes from the results you tick. | 1, 28 |
| No per-table warnings about downstream effects | D-0501 (first part) | NOT SURE | Question 28 (a) and (b) show an effect line per result, downstream of the step; whether that is a "per table warning" is yours (the independent review). | 28 |
| The count of rows removed at the plot removed; the check only where the step is applied | D-0501 (second part), D-0508 | NOT SURE | My reading: the effect at a place does not tell the effect at the results; a measured count per result is evidence (G1, G3, E1). Argued in `GOALS_REVIEW.md` section 6. | 28 |
| "Table changed" and "picture changed" for each plot | D-0318 | KEEP | Kept under every option of question 28; options (a) and (b) add counts. | — |
| "Remove from all the data": off by default, explicit, the list shown first, data-agnostic words; the user may untick | D-0415 part B, D-0416, D-0499, D-0500, D-0498 | KEEP | The one automatic placement, when asked (G6). | — |
| The entity key and the columns used to join, two lists | D-0313 | KEEP | G5. | — |
| A warning between ticked places when a value does not match one to one | D-0203 | NOT SURE | It pulls against D-0501; no later decision says which wins (the independent review). | 28 |
| The walk of the lineage: places from the engine's plan; a renamed column followed; red lines where the app cannot follow YET | D-0325, D-0337, D-0351 to D-0353, D-0356, D-0444, D-0445, D-0452, D-0454, D-0460, D-0473, D-0486 | KEEP | The lines of the dialog under every option (G5, E1). Which groups of tables are offered from a result is a builder's choice today; it meets your reading of D-0451 (`DIFFERENCES.md` A5), which question 1 needs. | — |
| Audit steps: filters, removals by key, and column drops | D-0322 | NOT SURE | My recommendation is now (b), as decided (`GOALS_REVIEW.md` section 11 e); the independent review recommends drops at the result's own table only. | 29 |
| A key column dropped is refused by place; a declared key follows the same rule; a drop the app cannot follow is refused | D-0358, D-0371, D-0448, D-0449, D-0460 (drops) | NOT SURE | Needed only if the audit keeps column drops. | 29 |
| The Reshuffle in Audit mode, to be written as a step | D-0341 | NOT SURE | My reading: a new arrangement removes no observation (G4) and is harder to trust (G3). Options include none in HOME (c) and the seed kept without a reason (d). | 17 |
| No plot-style change for now | D-0120, D-0145 | KEEP | G4. | — |
| A table can be a result; the result is the last stage; the comparison in layers; exported by its id | D-0485, D-0487, D-0489, D-0490 (part 1) | KEEP | G3. Its keys and the form are question 2. | 2 (the form only) |
| The recipe form with derived tables and `from:`; the one move of the demo recipes after the design is final | D-0516, D-0517, D-0525 | NOT SURE | Form 3 serves G2 and G3 (my reading); you have not confirmed it (D-0496). | 2 |
| Every join with the metadata in tier 1; the three kinds of table | D-0510, D-0523, D-0513 | KEEP | G1. | — |
| ST05 as built: every join refused outside tier 1, not only the metadata join | (a rule of the format specification, no line of yours) | NOT SURE | Wider than your decision on the metadata join (the independent review). | 27 |
| The build at opening; Exploration; "Table to view"; the filters cleared when the table changes or the mode changes | D-0326, D-0327, D-0310, D-0311, D-0361 | KEEP | G5. After the filter branch is merged, the filters are kept while the table viewed is the same. | — |
| A table that no result reads can be viewed and is exported | D-0457 | KEEP | E5, G3. How you reach it in the data preview is question 13. | 13 (the way in only) |
| The report by groups, results first | D-0491, D-0484 | NOT SURE | G3. The points that D-0491 leaves open (an intro line, an empty group, id or label, the audit trail grouped or flat) are proposed with it and need your yes. | the open points of D-0491 |
| The names pass: every display key with `ui_`; the recipe name `info.ui_label`; no plot `ui_title` | D-0407 to D-0412, D-0468 to D-0484 | KEEP (content) | G5. By your order it is applied in the one move, after question 2 (D-0525). | 2 (timing) |
| BLUEPRINT is an IDE: never replace a production-ready recipe by mistake; comments never lost; it encourages declaring the key | D-0495, D-0500 | KEEP | E4. Its build waits for its own questions (`BUILD_PLAN.md` section 4) and your order of D-0271. | BUILD_PLAN questions |
| The lineage picker | D-0496 | NOT SURE | Not decided; it serves the story (E5). | 13, 14 |
| The upload of a recipe: refused under an existing name; off unless a deployment declares a place | D-0390, D-0437, D-0440 | KEEP | No deployment declares an upload place today; what to do with the unreachable code is question 24. | 24 (the code only) |
| The first pass of this review: the app chooses the places from the results the user ticks | (a proposal, never decided) | DROP | Against "the app cannot decide the scope" (D-0531). | — |

---

## 2. The builds

### 2.1 Merged on `dev` this month

| What it is | Where | Verdict | Reason, and the goal | Depends on |
|---|---|---|---|---|
| The filters panel: pickers by type, a typed value kept, "between" needs both values | merges `51be0a46`, `781179e3` (D-0503, D-0504) | KEEP | G5. | — |
| The two sentences of the data preview (rows shown, columns hidden) | merge `d2e92547` (D-0488) | KEEP | G5. | — |
| The build at opening | `app/modules/opening_build.py` (D-0326, D-0335) | KEEP | Every table built and keyed; the base of a measured effect (G1). | — |
| The export writes every table that no plot reads | `app/handlers/export_handlers.py` (D-0457) | KEEP | E5, G3. | — |
| The lineage library: recipe graph, step readings, walk, records, the YET sentence | `libs/utils/src/utils/` | KEEP | The walk lists the places of the dialog under every option of question 28 (G5). Its `walk()` is called by tests only today. | — |
| The drop gate (a key column dropped is refused by place) | `libs/utils/src/utils/key_drop.py`; check AU04 | NOT SURE | It serves only audit drops (`recipe_check.py:571-578`; `audit_copy.py:199-208`). | 29 |
| The comparison of two tables, in layers | `libs/utils/src/utils/table_compare.py` (D-0489) | KEEP | Compare of a table result (G3); and the measured effect if question 28 is (a) or (b). Called by tests only today. | — |
| The audit copy library (the decided form) | `libs/utils/src/utils/audit_copy.py` | KEEP | The one form of a step (G1, E6). Its builder is called by tests only; its key-drop part depends on question 29. | — |
| The run of an audit copy by the engine | `app/modules/audit_run.py`, `compose_candidate_plan_book` | KEEP | Needed for HOME's audited plot and table (slice 3) and for a measured effect. Called by tests only today. | — |
| "Remove from all the data" library: the tables reached, written at tier 1 | `libs/utils/src/utils/remove_from_all.py` | CHANGE | Keep the reach (D-0500, D-0498); remove the "may stay" sentences (false on the demo; D-0501). See section 0, item 4. | — |

### 2.1b Built, and missing from the first version of this list (added after the independent review)

| What it is | Where | Verdict | Reason, and the goal | Depends on |
|---|---|---|---|---|
| The export writes the T1 and T2 data files from the original tables; only a plot's T3 file is audited | `app/handlers/export_handlers.py:1405-1409, 1428-1431, 1463-1467` | CHANGE | In the audited part, the audited tables, or a plain line that they are the originals (results you can trust). Found by the independent review; read by me. | slice 5 |
| The import marks the audit steps "not_checked" | `app/modules/bundle_importer.py:186-194` | CHANGE | Check the audit recipe's fingerprint at import (clear, correct audits). | slice 5 |
| The propagation modal "This plot only / All plots / All plots except" | `app/handlers/filter_and_audit_handlers.py:1097` | DROP | Replaced by the dialog of places, under every option of question 28. | — |
| Screen texts that say "samples" or "for now" | `app/handlers/home_theater.py:1482`; `app/handlers/filter_and_audit_handlers.py:674-676, 997, 1002-1007` | CHANGE | Data-agnostic words (D-0512); each text goes with the part it describes. | — |
| The join fork of the reproducibility export | `libs/blueprint_arch/src/blueprint_arch/t3_translator.py:197`; `app/handlers/export_handlers.py:1559-1569` | DROP | It writes the steps at a place nobody chose (a fork of a join's tier 2), against "the app cannot decide the scope" (D-0531); replaced by the audit recipe. A home for the seed comes first. | 17 (the seed) |
| The audit where the user's place cannot be written | `app/handlers/audit_stack.py:1049-1058` (a technical warning after Apply) | NOT SURE | Not decided: D-0422 assumes saving works in every deployment. | 30 |

### 2.2 On branches, not merged

| What it is | Branch | Verdict | Reason, and the goal | Depends on |
|---|---|---|---|---|
| The exploration filters follow the table viewed | `task/home-filter-follows-table` (`7981a569`) | KEEP | Your decisions D-0505, D-0506 (G5). Merge after its review. | — |
| "Remove from all the data" with unticked tables | `task/remove-from-all-ticked` (`95b6285e`, on hold by D-0507) | CHANGE | Take the write at the ticked places; leave out the sentences about unticked tables, which were false on the demo (the two reviews). Section 0, item 4. | — |
| One Python for the deployment | `task/one-python` (`5bb9f719`, D-0263) | not judged | Outside the audit and the recipe form. | — |
| Trials (`trial/axis-text`, `trial/default-ticks`, `trial/formula-d`, `trial/path-check`, `trial/stat-function-polars`) | branches | not judged | Studies, not builds. | — |

### 2.3 The planned slices (`BUILD_ORDER.md`)

| Slice | Verdict | Reason | Depends on |
|---|---|---|---|
| 0, the records agree | KEEP | E6. Section 0, item 1. | — |
| 1, the filters follow the table | KEEP | Built on the branch above. "Open any table by its name" joins it once question 13 is answered. | — (13 for the addition) |
| 2, the recipe upload code that no screen offers | NOT SURE | My reading: remove (E6). | 24 |
| 3, one form of an audit step: the audit recipe; HOME's plot and table from its engine run | KEEP for the decision to replace today's audit at a plot's table; NOT SURE for its details | Needed under every option (G1, E6): on the demo, removing an entity before or after a z-score gives other values for all 41 other entities (the independent review's run, rerun by me), so two audits side by side would disagree. | 26, 29, 17 (the details) |
| 4, the dialog of places | NOT SURE | The dialog as decided, plus the measured effect if 28 is (a) or (b). | 28, 1, then 3 to 8 |
| 5, the export of an audit | NOT SURE | G1, G3. It must also write audited T1 and T2 tables, or mark them as the originals, and check the audit recipe's fingerprint at import (section 2.1b). | 15; 17 for the seed |
| 6, the report by groups | NOT SURE | G3. | the open points of D-0491 |
| 7, the one move of the shipped recipes, with the names | NOT SURE | Your order: after the recipe design is final (D-0525). | 2 |
| 8, the lineage picker | NOT SURE | E5; after the demo in the route. | 13, 14 |
| 9, a table as a result | NOT SURE | G3. | 2 |
| 10, the check and the good-practice page | KEEP (the page; the refusal of a duplicate result id) / NOT SURE (the advice codes of D-0498, D-0500: where and in what form is not decided) | Section 0, items 3 and 5; the paragraph on the audit folder waits (question 30). | — / D-0498 open point |
| 11, the preview sentences | done | merged `d2e92547`. | — |

### 2.4 Open tasks of `.claude/tasks/tasks.md` that this study touches

Only the tasks of the audit, the lineage, the export of an audit, the recipe form and BLUEPRINT's safety were judged. The other open tasks (engines, formulas, security, the Gallery, the configuration, the plot library) were not judged here.

| Task | Verdict | Reason | Depends on |
|---|---|---|---|
| `AUDIT-VIEW-1`: in Audit mode, data and plots come from the copy of the recipe | KEEP (in content) | It is slice 3's consequence 1 (G1). Its build goes with slice 3. | 26 (timing, with slice 3) |
| `AUDIT-REPLACE-1`: replace, do not leave behind, the old parts when Audit mode is built | KEEP | E6. | — |
| `AUDIT-RECIPE-RULE`: one list of steps; the audit recipe is the exported recipe | KEEP | D-0332 refines it (G1). | — |
| `AUDIT-HISTORY-LOG-1`: an optional history log | CHANGE | Your later rule makes the log always exported, not optional (D-0478). | — |
| `AUDIT-DIALOG-PREVIEWS`, `AUDIT-WARN`, `AUDIT-ERROR-Q`, `AUDIT-ADVICE` | NOT SURE | They describe the dialog's lines and warnings; the measured effect of question 28 changes what is shown. | 28 |
| `AUDIT-USABILITY-1`: two or three scientists use the dialog, thinking aloud | KEEP | G5; it is the acceptance check of `GOALS_REVIEW.md` 4.11. After slice 4. | — |
| `AUDIT-PANEL-UNTESTED`: no test clicks the delete icon | CHANGE | The icon is replaced by "Remove step" (D-0314); the test is written for that. | — |
| `AUDIT-MESSAGES-PLAIN-1`: messages show internal names | KEEP | G5. | — |
| `EXPORT-MODES`: the export in two cases and two modes | KEEP (in content) | D-0298, D-0490, D-0492 (G1). It is slice 5. | 15 |
| `EXPORT-RECIPE-REFUSE-1` | NOT SURE | It waits for you (point Y8). | its own question |
| `SESSIONS-MANY-DATASETS` | NOT SURE | Four questions wait for you. | its own questions |
| `DATA-IMPORT-OVERWRITE` | NOT SURE | It waits for your yes. | its own question |
| `BP-COMMENTS-1`: a BLUEPRINT save keeps comments | KEEP (in content) | D-0495 (E4). Its library question comes first; BLUEPRINT after HOME and the Gallery (D-0271). | its library question |
| `ENGINE-T3-READER`: the engine does not read the steps of a plot | NOT SURE | Under form 3 a result holds no data steps; the audit writes at a result's own place. | 2 |
| `RESULT-ID-TWICE-NOT-REFUSED` | KEEP | E1. Section 0, item 3. | — |
| `DEMO-USERS-1`, `DEMO-BRANCH-PLAN-1` | KEEP | E7; the December demo of `GOALS_REVIEW.md` 4.11. | — |

---

## 3. What I could not do

- I did not review the code of the branch `task/home-filter-follows-table`; KEEP means its decisions match the goals, not that the code is right. Its review decides the merge.
- The open tasks were judged only where they touch the study (2.4); the others were not read.
- Second pass: no run; each verdict rests on the ledger lines read and on the files of this study. Third pass: the rows marked "survived the independent review" were tested by that review (`GOALS_REVIEW_sonnet.md` part C); I re-ran two of its checks (the case of D-0499 and the z-score), not its test runs of the two branches.
