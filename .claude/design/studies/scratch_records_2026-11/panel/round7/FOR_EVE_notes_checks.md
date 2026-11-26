# Notes beside FOR_EVE_one_list.md: the check of files 4, 6 and 7 against the records (2026-11-16)

Written for the person who audits the list. No repository file was edited. Marks: READ (I read it at the line), RUN (I ran a command).
Method (that of `tmpAI/panel/round7/questions_checked.md`, top): DECIDED = a record answers it and shows she took it; CONFIRM = a record answers it but who took it is not stated, or the built thing is an agent's reading of her words; OPEN = no record answers it, or two records of the same weight differ.
Records searched: `tmpAI/panel/adr/ledger.md` (N01 to N52, A01 to A17), `.claude/knowledge/architecture_decisions.md` (ADR-097 to ADR-106; ADR-103 :5274-5298, ADR-104 :5300-5325, ADR-105 :5327-5345), `.claude/design/recipe_format_spec.md` (DEC rows), `home_audit_steps.md`, `home_stage2_mechanism_spec.md`, `.claude/tasks/tasks.md` sections 5 to 7, the channel (M80 to M138 of 57; M85 to M134 of 40).

## File 4 (`recipe_fixes/fix_list.md` and channel M131 of 40, lines 959-981)

| Point | Tag | Source | Why |
|---|---|---|---|
| R1 is "unknown[...]" a class | OPEN | channel line 418 (N22: asked in M95, "No default from me"); ledger has no answer (grep "unknown[" in ledger and tasks.md: no hit) | no answer by her |
| R2 which phenotype column feeds the class | OPEN (only if R1 = c) | fix_list.md:284 | conditional |
| R3 which thresholds | OPEN | ledger N32 (ledger.md:91: "old thresholds verified"); fix_list.md:189-196 two pairs | her rule says verify the old thresholds; the check found two pairs; ambiguity rule M137 |
| R4 second recipe | OPEN | ledger N32; fix_list.md:259, :286 | her words say "AMR genes ... per sample and per gene" (channel M94, N9) without naming one recipe |
| PlasmidFinder list: delete, not wire | CONFIRM | ledger N31 (ledger.md:90) "wire it"; cleaning rule same line | two sentences of hers pull in two directions |
| FastP box plot by source | OPEN | fix_list.md:171 | the old plot cannot work (42 rows, 42 samples); no record |
| ResFinder tie rule | CONFIRM | ledger N32 / channel M95 "State the tie rule" | she asked for a stated rule; the stated rule is the data scientist's |
| identity first, then overlap | CONFIRM | channel M95 N9 "ordering by identity and coverage, highest first" | her order of words; 4 of 63 rows depend on it (fix_list.md:247) |
| drop NaN step | CONFIRM | ADR-103 point 5 (architecture_decisions.md:5287) "NaN ... explicit steps (polars_drop_nans)" | consistent with her rule; the step is the agent's |
| extra plot | CONFIRM | fix_list.md:256 | the agent's addition |
| 37 descriptions, `demo_join` text | DECIDED | ledger N25 (ledger.md:84) "fix ... the 37 missing descriptions and anything else" | |
| gallery: nothing to fix | DECIDED | ledger N22 (ledger.md:81) | result: already true |
| old output-fields list deleted | DECIDED | ledger N31 (a) | built on branch `task/recipe-fixes` (`dbdb0f20`), not merged (RUN `git log`) |
| empty `test_logic.yaml` deleted | DECIDED | ledger N31 cleaning rule | the loader crash on an empty file is a separate defect |
| wire (c) join, (e) stress plot, (f) ResFinder piece | DECIDED | ledger N31, N32 (N10: wire if a recipe uses that data) | (e) changes the stress picture (43.4 percent of pixels, fix_list.md:180) |
| first line of the formula (A1) | not a decision: PROVISIONAL | channel M95 line 417 (N21 "PROVISIONAL"); tasks.md:356 | nothing moves |

## File 6, `typing_at_reading.md` (section D, five points)

| Point | Tag | Source | Why |
|---|---|---|---|
| D1 keep the rule for a node that cannot take the value | OPEN | `home_stage2_mechanism_spec.md:78` and `:121` mark it [MINE]; tasks.md:396 (S2-2 OPEN, her words "I do not see how this is possible") | the only record is the writer's draft |
| D2 one error form at reading | DECIDED | tasks.md:396 "The most important thing: capture the errors of Polars and the type errors at reading" (channel M101 of 57) | her instruction |
| D3 silent conversions: principle | DECIDED | ADR-104 point 1 (:5308); DEC28 (spec :125), DEC33 (:139), DEC49 (:159) | her words "No silent error: that is the rule" (ledger L48) |
| D3 apply it to rounding, overflow, underflow, cut digits | CONFIRM | same | the application to reading is the data scientist's |
| D3 `Date` with no `format` | OPEN | spec :370 (`format` optional); `declared.py:5` | a change of the recipe format |
| D3 empty after trimming spaces | OPEN | channel line 419 (N23 asked, no answer found) | |
| D3 advice for the other silent cases | DECIDED | tasks.md:296 "Always add a checker advice when it helps" (her N12 words, ledger.md:71) | wording provisional |
| D4 checker judges declarations without data | DECIDED | DEC03 (spec :90); FD05 (spec :621); same N12 rule | the exact list of checks is the builder's |
| D5 HOME table and plot pass no `strict` | CONFIRM | ADR-104 point 7 (:5316); RUN grep: `viz_factory.py:258` and `app/modules/t3_audit_engine.py:555` call `filter_condition` without `strict` | the ADR says the engine is strict and old steps get their type; it does not name these two paths |

## File 6, `stat_summary.md` (section E, five points)

| Point | Tag | Source | Why |
|---|---|---|---|
| E1 N28 how to get a mean with a bar | OPEN | tasks.md:388; ledger A12; channel M106 ("N28 NOT decided") | merged with V9 |
| E2 `mean_se` divides by n | advice DECIDED; a `modif_` version OPEN | tasks.md:296; ADR-106 note V1-B | the `modif_` version is folded into point 16 |
| E3 advice when no `fun_data` | DECIDED (advice) | tasks.md:296 | |
| E4 formula text runs Python | DECIDED | ADR-099 point 14 (:5126); ledger N09; channel M133 of 40 (:1005-1008); fix on branch `task/smooth-formula` (2 commits, not merged, RUN) | same rule as the three earlier places |
| E5 names for label and rescale functions | OPEN | none | |

The coordinator counted 9 points for these two files (channel :1028); the files hold 5 and 5.

## File 7 (`filter_pickers_points_for_eve.md`, eight points and two smaller)

All eight are marked "PROVISIONAL ... an agent's choice" in `tasks.md:97-105` (RUN grep). Her decided part: ledger N06 (ledger.md:65).

| Point | Tag | Source | Why |
|---|---|---|---|
| 1 true/false operators | CONFIRM | ADR-104 point 4 (:5312) "every operator the engine has" and ledger L52 narrowed only for text greater/less (N06) | built offers fewer |
| 2 operators of time and duration | CONFIRM | same | no list for time and duration; dates as built agree |
| 3 time of day: three boxes | OPEN | none | |
| 4 duration: number and unit | OPEN | none | |
| 5 date and time | OPEN | none | |
| 6 starting values | OPEN | none; agent_principles.md:7 "do not choose for the user" is the nearest principle | |
| 7 value finer than the column | CONFIRM | DEC49 (spec :159), ADR-104 point 1, agent_principles.md:6 | the record points to "refuse" |
| 8 date box strict | principle DECIDED (no silent repair, ADR-104 point 1); form OPEN | tasks.md:105 | |
| list on demand above 1000 | OPEN | tasks.md:105 (L10) | one-path rule is nearest |
The title of the file says "seven choices"; it holds eight. The proposal file `filter_pickers.proposal.md` also says seven.

## What this check would not catch
- A decision of hers that exists only in a chat turn not in the records. I did not re-read her transcripts for these three files (the old-words file did).
- The "Eve" date column of the spec is taken as her record (taken_by_report.md section 6).
- I ran no code in the tree; the two `strict` calls and the Categorical state were checked by grep.
