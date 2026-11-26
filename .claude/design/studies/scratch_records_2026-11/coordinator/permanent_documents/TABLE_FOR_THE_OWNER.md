# Permanent documents that live only in the temporary folders: a table for the owner (2026-11-21)

Nothing in this table is decided. Nothing was moved, copied or deleted. Labels: RUN = I ran the command; READ = I read the file; REASONED = my conclusion.

## 0. How to read this

Your three sentences (all yours, relayed 2026-11-21):

- (a) "we need to have this specification in the design - no document that is permanent should be left in tmp" (D-0419).
- (b) "I think documents/study_ongoing for example could be a solution and what is for the design we already have a place in .claude I think".
- (c) ".claude/design/studies/ its good because the definitive ones can be moved to .claude/design".

So the places are (c replaces the folder name of b):

- a study (ongoing, or kept because a decision rests on it, or a table you have to read) goes to `.claude/design/studies/<one subfolder per study>/`;
- when the result of a study becomes the definitive design, it moves from there to `.claude/design/`;
- `tmpAI/` and `tmp/` stay scratch.

What I did: a read-only survey (find, grep, diff, one scan script kept in my scratch folder). I wrote this one file. I moved nothing.

Why it matters (READ `.gitignore:36-37`): `tmpAI/` and `tmp/` are not in git. A document that lives only there can disappear, and a task, a ledger line or an ADR that names it points at nothing durable.

What you get first: section 1 (the size), section 2 (one table, one row per study), section 4 (eight choices for you). Long lists are in the appendix.

## 1. The size of the problem (all RUN)

| What | Number |
|---|---|
| Size of `tmpAI/` | 2.8 GB, about 78 600 files (most are test outputs, screenshots, logs, copies of the repository) |
| Written documents (`.md`) in `tmpAI/`, copies of repository trees left out | 771 files, about 70 500 lines |
| Studies in `tmpAI/panel/` | 86 folders |
| Work folders in `tmpAI/coordinator/` | 58 folders |
| Tables written for you (`TABLE_FOR_THE_OWNER.md`) | 17, all in `tmpAI/panel/`; none of them in git except one copy (`recipe_places`, in `.claude/design/blueprint_revision/prior_work/`) |
| Pointers to `tmpAI/` or `tmp/` in the ledger, ADR file, tasks, handoff, design, rules, workflows, docs, CLAUDE.md, agent files | 886 mentions, 434 different paths: 342 exist, 92 do not |
| Of those, from the ledger | 40 mentions, 27 paths, all exist (no broken pointer) |
| From the ADR file | 13 mentions; 7 point at a missing file (`tmpAI/results.md`, 4 places) or at example paths |
| From tasks, handoff, ledger and ADR together: paths in `tmpAI/` that exist and that a record relies on | 239 (197 files, 42 folders) |
| From `.claude/design/`: paths in `tmpAI/` that exist | 125 |
| Pointers that are broken and name a real document | about 30 (section 6). The other missing paths (about 60) are examples, patterns or output places, not pointers to a document (for example `tmpAI/progress.md`, which is a per-worktree convention; `tmp/viz_test/geom_bar.png` in a how-to) |
| Documents already copied into git | about 17 files: 8 of `blueprint_gap`, 5 of `recipe_places`, 4 reports of `engine_keys`, 2 scripts of `test_lab_review`; equal to the originals except the first line (a header saying where it was copied from) (RUN, `diff` after removing line 1) |
| Files with an e-mail address | 5 documents (section 2, last column; the address is not copied here) |

Two awkward facts (RUN):

- This very table is named by `tasks.md:908` and `handoff_active.md:20` before it existed. Now it exists, only in `tmpAI/`.
- The ledger numbers I could attach to a study are only the numbered lines that quote its path (the grep). Other ledger text (the lists "Asked, not decided") also names some folders; those are marked "named in text".

## 2. The proposal in one table, by study

Columns: "Docs now" = folder, number of `.md` files, lines. "Decision rests on it" = ledger lines that name its path (RUN grep); "tasks/handoff" means a task or the handoff names it. "Proposed place": `S/<name>` = `.claude/design/studies/<name>/`. "Moves with it": T = the table only; T+ = table, briefs, facts, the viewpoint reports (architect, scientist, user), run facts; no screenshots or scratch. "Mail" = holds an e-mail address. "In git" = a copy already in git.

Status words are my reading (REASONED from `tasks.md` and the handoff), not decisions.

### 2a. Studies you still have to read or answer (first)

| Study (plain name) | What it holds | Docs now | Decision rests on it? | Proposed place | Moves with it | Mail | In git |
|---|---|---|---|---|---|---|---|
| Deployment: how recipes and data are read and written (use cases) | the study table with designs A/B, the order you gave | `tmpAI/panel/deployment_io/`, 13 md, 1 553 lines | D-0413, D-0417, D-0418; tasks and handoff | `S/deployment_io` (its result feeds the deployment specification, which D-0418 says lives in the design: that specification becomes a file of `.claude/design/` when written) | T+ ; `ORDER.md` is your own words, keep it | no | no |
| Deployment standard: structure table | the structure of the one deployment specification, the container example, what the app checks at start | `tmpAI/panel/deployment_standard/`, 6 md, 1 179 lines | D-0418; tasks 905-909, handoff | `S/deployment_standard`; the specification itself goes to `.claude/design/` when written | T+ (FACTS.md only after the e-mail address is removed or left out) | yes (`FACTS.md`) | no |
| Names across the app (seven kinds of names) | table, facts, viewpoints; questions 1 to 7 answered | `tmpAI/panel/names_whole_app/`, 8 md, 1 396 lines | D-0406 to D-0410, D-0412; named in the handoff | `S/names_whole_app` (a decision rests on it) | T+ ; `ORDER.md` is your words | yes (`FACTS.md`) | no |
| Fields that carry names: purpose table | what `ui_label`, `info.label`, titles are for | `tmpAI/panel/name_fields/`, 1 md, 100 lines | D-0405 asked for it; task NAME-FIELDS-PURPOSE-TABLE | `S/name_fields` | T | no | no |
| Gallery: names, headings, chart type | the table and the drafts for Q1 and Q2 | `tmpAI/panel/gallery_study/`, 9 md, 1 264 lines | D-0397 (Q1 answered); tasks 292, 890 | `S/gallery_study` | T+ (include `Q1_...`, `Q2_...` drafts) | no | no |
| Gallery: verification of the 34 examples | table, facts, `SOURCES_CHECK.md` (EUCAST) | `tmpAI/panel/gallery_verify/`, 9 md, 1 399 lines | D-0401; tasks 895-896 | `S/gallery_verify` | T+ | no | no |
| Gallery: taxonomy review | table and viewpoints | `tmpAI/panel/gallery_taxonomy/`, 5 md, 516 lines | task GALLERY-TAXONOMY-REVIEW | `S/gallery_taxonomy` | T+ | no | no |
| Help beside the screen (popup help) | table and viewpoints | `tmpAI/panel/help_beside/`, 8 md, 482 lines | task HELP-BESIDE-THE-SCREEN-STUDY | `S/help_beside` | T+ | no | no |
| Data Import: message words and silent cases | table with S1 to S14 | `tmpAI/panel/data_import_words/`, 1 md, 124 lines | tasks 293, 502; handoff | `S/data_import_words` | T | no | no |
| Recipe versions | table, 3 viewpoints | `tmpAI/panel/recipe_versions/`, 7 md, 341 lines | named in the ledger text ("Asked, not decided" (a)); tasks 858, 874 | `S/recipe_versions` | T+ ; `M417_owner_decisions_and_open_points.md` is your words, keep it | no | no |
| Where recipes live | 11 questions P1 to P11 | `tmpAI/panel/recipe_places/`, 6 md, 301 lines | tasks 860 (RECIPE-NAME-DATE-RULE waits for it); handoff 90 | `S/recipe_places` (a copy already exists in `blueprint_revision/prior_work/recipe_places/`: choose one place, section 4 point 4) | T+ | no | yes, 5 files, equal except the header line |
| ADR history kept apart | table, facts, 100+ small files | `tmpAI/panel/adr_history/`, 110 md, 5 758 lines | named in the ledger text; tasks 855 waits for it | `S/adr_history` | T, FACTS.md and viewpoints; the 100 other small files are working material (see appendix) | no | no |
| Display labels of columns; seed step | two tables | `tmpAI/panel/column_labels/` 1 md 73 lines; `tmpAI/panel/seed_step/` 2 md 98 lines | named in the ledger text; handoff 134 | `S/column_labels`, `S/seed_step` | T | no | no |
| Column tracking and opening build | table, facts, `OPENING_BUILD_figures.md` | `tmpAI/panel/column_tracking/`, 5 md, 274 lines | named in the ledger text; tasks 771, 850 | `S/column_tracking` | T+ | no | no |
| Audit recipe file | table, 3 other files | `tmpAI/panel/audit_recipe_file/`, 4 md, 199 lines | named in the ledger text | `S/audit_recipe_file` | T+ | no | no |

### 2b. Decided or in use: kept because a decision or a build rests on it

| Study | What it holds | Docs now | Decision rests on it? | Proposed place | Moves with it | Mail | In git |
|---|---|---|---|---|---|---|---|
| Lineage (lbfb), logic review, tests | brief, build plan, logic review (it wins over the plan), questions, `lineage_tests/DESIGN.md` Q4 to Q11 | `tmpAI/panel/lbfb/` 6 md 910 lines; `tmpAI/panel/lineage_tests/` 13 md 1 843 lines | D-0414, D-0415 (and D-0416 by text); D-0351 to D-0354 name its questions; tasks, handoff 128, 132 | `S/lineage` (LOGIC_REVIEW and DESIGN become design files when the build is final) | T+ | no | no |
| Where a recipe fails (error place) | table | `tmpAI/panel/recipe_error_place/`, 1 md, 48 lines | D-0338, D-0342 (point (e) of D-0342 still open per the recipe rules) | `S/recipe_error_place` | T | no | no |
| Panel widths | brief, viewpoints | `tmpAI/panel/panel_widths/`, 4 md, 93 lines | D-0375 | `S/panel_widths` | T+ | no | no |
| Formula D; stat function and Polars; id versus key; axis text; path use cases | the studies behind D-0267, D-0275, D-0216 | `formula_d` 11 md 1 024; `stat_function_polars` 3 md 376; `id_vs_key` 1 md 51; `axis_text` 3 md 234; `path_use_cases` 4 md 368 | D-0267, D-0275, D-0216; the others named in the ledger text | `S/<each name>` | T+ | no | no |
| Gallery walk 2026-11-20 | final report of a walk | `tmpAI/coordinator/gallery_walk_2026-11-20/`, 1 md, 67 lines | D-0379 | `S/gallery_walk_2026-11-20` | the report | no | no |
| ADR tables | `ledger.md`, `taken_by_report.md` | `tmpAI/panel/adr/`, 4 md, 332 lines | named in the ledger text | `S/adr_tables` | T+ | no | no |
| The three files in your words | `ORDER.md` (deployment_io, names_whole_app), `M417_...`, the question pages `QUESTIONS_for_eve_2026-11-18.md`, `QUESTIONS_SORTED_2026-11-19.md`, `DEMO_BRANCH_PLAN_2026-11-18.md`, `READINESS_for_demo_*` | loose in `tmpAI/panel/` and inside the studies above | `QUESTIONS_for_eve_2026-11-18.md` is named by the ledger (D-0250 and following) | `S/owner_pages/` (one place for her own words), or with the study they belong to: your choice (section 4 point 1) | each file as it is | no | no |

### 2c. Old material (before 2026-11-14 or finished long ago); groups, not single studies (counts approximate, RUN)

| Group | What it holds | Docs now | A decision rests on it? | Proposed place | Mail | In git |
|---|---|---|---|---|---|---|
| Engine keys and arguments | `tmpAI/engine_keys/` (29 md) and the studies on engines and recipe arguments | about 56 md, 7 000 lines | tasks and handoff name `engine_keys`; no ledger line parses | `S/engine_keys` as archive, or scratch (section 4 point 6) | no | 4 reports equal except header (`step4_REVIEW`, `step4c_report`, `TIER3_facts`, `BLUEPRINT_T1_T2_PROOF`) |
| Blueprint gap | `tmpAI/panel/blueprint_gap/` | 8 md, 790 lines | named by tasks | already in git (`blueprint_revision/prior_work/`) | no | yes, 8 files |
| Rounds 4 to 7 of the panels | `round4` to `round7`, briefs, `FOR_EVE_*` | about 69 md, 7 200 lines | handoff and tasks name `round5`, `round7` | `S/rounds` as archive | no | no |
| Slice, review and control reports of the coordinator | `SLICE_*`, `*_REVIEW`, `*/FINAL_REPORT.md`, `CONTROL*` | about 150 md, 14 000 lines (most inside copies of the repository) | tasks name about 40 of them | the loose reports `S/coordinator_reports/`; the copies of the tree stay scratch | one (`home_walk_2026-11-20/FINAL_REPORT.md`) | no |
| Control runs, audits, switch check | `controls_*`, `audits`, `audit_full`, `switch_check`, `rename` ... | about 88 md, 7 500 lines | handoff and tasks name some control runs | scratch, except a final report a task names | no | no |
| Export, session, audit-rule studies | `export_*`, `session*`, `audit_*`, `key_types`, `data_ids`, `label_trace`, `author_manifest` ... | about 81 md, 6 700 lines | tasks and handoff name most | `S/<name>` for each one a task still names; others archive | yes (`author_manifest/REPORT_for_eve.md`, `check_on_select/impact_report.md`) | no |
| Formula, themes, viz, verification, UML sync, others | `formula_night`, `formula_safety`, `themes`, `viz_rename`, `verification` (715 md files, mostly generated), `seed_ops` ... | about 109 md, 10 000 lines | tasks name most | as above | yes (`formula_night/builder_report.md`) | no |

## 3. What stays in the temporary folders

| What | Why it stays | Note |
|---|---|---|
| `tmpAI/agent_channel.md` | live state between sessions (`rules_agent_channel.md`: not in git on purpose) | holds an e-mail address; ADR and handoff name it as a source: REASONED, the record stays true only as long as the file is not deleted |
| `tmpAI/coordinator/progress_*.md`, markers, per-worktree `tmpAI/progress.md` | live state; the traceability rule of `CLAUDE.md` 2.1 asks for them | the awkward case: `progress_2026-11-14_session3.md` is named as a source by ADR, tasks and handoff (RUN). It is a record of a finished session, so it fits a study or archive folder more than live state. Suggestion: treat it as a study document and move it |
| Screenshots, probes, `.log`, `*.bak`, test outputs, `tmp/` test folders, `tmp/dep_graph.json` (generated) | scratch | nothing durable should name them (section 6, rule in section 4 point 7) |
| Copies of the whole tree (for example `tmpAI/coordinator/uml_2026-11-21/review/headtree/`, `slice_*_final*`) | scratch; 2.8 GB total | may be deleted by you or an agent later; not part of this table |

## 4. The choices for you, ranked

Each has options. "Finding it later" says what the option means when someone looks for a study.

**1. What moves with a table.** (a) The table alone: small, but the briefs, the facts and the viewpoints that justify it are lost with scratch. (b) The whole study folder: everything is found, but 2 800 lines of small working files in `adr_history` and many screenshots come too. (c) The whole folder without screenshots and scratch: Suggestion; briefs, facts, viewpoints, run facts and your own words come; images and logs do not. Finding it later: (c) and (b) give one folder per study; (a) gives only the table.

**2. The subfolder names.** (a) By subject: `deployment_io`, `names_whole_app`; short and the same as the names now, so old pointers are easy to map. (b) By subject and date: `2026-11-21_deployment_io`; shows age, but a rename later breaks pointers. (c) Numbered: `S-014_...`; unique, but names mean nothing. Suggestion: (a). Does a later change of the name reconsider a decision? No.

**3. After its decision.** (a) The study stays in `studies/`. (b) It moves to `.claude/design/outdated/` (exists, 13 files). (c) Its decided part is rewritten into a design file and the study stays beside it. Finding it later: (a) and (c) keep one place; (b) mixes finished studies with replaced designs. Reconsiders a decision: no; (c) gives the decision a design file, which your sentence (c) already allows.

**4. The pointers (the ledger is never rewritten).** (a) A table "moved from, moved to" in a README of the studies folder; the ledger stays as it is. (b) A note line in the ledger that names the new place (a new line, not an edit; D-0419 already records the rule). (c) Corrected pointers in tasks and handoff (these may be edited), the ledger and the ADR file read through the table. Suggestion: (a) and (c) together. Cost: 174 task mentions and 143 handoff mentions to correct, one script can do the replacing from the table and then check it.

**5. Files with an e-mail address.** (a) Clean before the move (remove the address, say so in the file). (b) Leave those files out. A file moved into git becomes shared. Five files: `names_whole_app/FACTS.md`, `deployment_standard/FACTS.md`, `author_manifest/REPORT_for_eve.md`, `check_on_select/impact_report.md`, `formula_night/builder_report.md`; the agent channel and `home_walk_2026-11-20/FINAL_REPORT.md` also have one (they do not move). Suggestion: (a) for the two FACTS files, because they belong to studies you still read.

**6. Old material from before 2026-11-14.** (a) Moved as archive (`S/archive_...`). (b) Left as scratch. Only what a task, the handoff or an ADR still names has to move (section 6 shows that some are already gone). Suggestion: (a) only for what is named; the rest scratch.

**7. From now on, where does an agent write a new study.** (a) Directly in `.claude/design/studies/<name>/` from the first day, scratch only in `tmpAI/`; nothing has to be moved later. (b) Write in `tmpAI/` and move at the end: this is the problem of today. Who checks: a line in the agent briefs ("a study document is written in `studies/`"), and an audit script that fails when `tasks.md`, the handoff, the ledger, the ADR file or `.claude/design/**` names a path under `tmpAI/` or `tmp/` that is not a convention (`tmpAI/progress.md`). Suggestion: (a) with both checks. Consequence for an agent that never commits: files appear as untracked in git; the commit by file name stays as it is.

**8. Does a large studies folder under `.claude/` cost anything.** READ: `CLAUDE.md` section 3 says files are read on demand; the automatic load is `CLAUDE.md` and `.claude/rules/*.md` (shown at the start of a session). `.aiignore` excludes `tmp/` and `tmpAI/` from the AI indexer but does not exclude `.claude/design/` (READ `.aiignore`; the file says it is for the indexer and the Read tool still works). So a studies folder would be seen by the indexer. `.claude/design/` is 3.3 MB, 181 files today (RUN). Option: add `.claude/design/studies/` to `.aiignore` so an agent reads a study only when it is named. Reconsiders a decision: no. Not verified: how the indexer weighs 70 000 lines (I could not test).

## 5. The order of work after your answers (not started)

1. Fix the choices of section 4.
2. A scout makes the list "moved from, moved to" for each study (a script can build it from this table).
3. Count before: documents per study and total lines (a script).
4. Clean the five e-mail files (an agent, by hand).
5. Copy, then check each copy equals the original (`diff`); only then does the original leave `tmpAI/`. Here the order matters: I propose copy first, delete never in this task; the owner decides about the originals.
6. Correct the pointers in `tasks.md` and the handoff (script from the table); add the README table in `studies/`.
7. Proof: every pointer in tasks, handoff, ledger, ADR, design, rules, workflows, CLAUDE.md resolves (the same scan I ran for section 1, now in `scripts/`); count after = count before; the audit script of choice 7 runs in `run_audits.sh`.
8. A reviewer checks the diff; commit by file name.

## 6. Broken pointers that name a real document (RUN; file:line then the missing target)

| Where | Missing |
|---|---|
| `.claude/knowledge/architecture_decisions.md:4926, 5328, 5330, 5337` | `tmpAI/results.md` |
| `.claude/design/decisions_2026-11-14/adr_sync_changes.md:61` | `tmpAI/results.md` |
| `.claude/design/decisions_2026-11-14/adr_sync_changes.md:113` | `tmpAI/ledger.md` (note: `tmpAI/panel/adr/ledger.md` exists) |
| `.claude/tasks/tasks.md:97` and `.claude/design/decisions_2026-11-14/rule_file_proposals/filter_pickers.proposal.md:7` | `tmpAI/filter_pickers_points_for_eve.md` |
| `.claude/tasks/tasks.md:854` | `tmpAI/review_texts_and_endings/FINAL_REPORT.md` |
| `.claude/logs/handoffs/handoff_active.md:16, 17` | `tmpAI/coordinator/gallery_picture_key_review/REPORT.md` (the folder exists; the report is not there yet) |
| `.claude/tasks/tasks.md:908`, `handoff_active.md:20` | `tmpAI/coordinator/permanent_documents/TABLE_FOR_THE_OWNER.md` (exists once this file is written) |
| `.claude/logs/handoffs/handoff_active.md:1696`, `docs/appendix/running_helper_scripts.qmd:98,101` | `tmp/demo_data_generated` |
| `.claude/design/blueprint_revision/06_proposal_architect.md:186`, `06_proposal_developer.md:22` | `tmpAI/lbfb_0b/out_ST22.json` |
| `.claude/design/lab_revision/06_proposal_architect.md:4` | `tmpAI/panel/lab_step4/arch_check` |
| `.claude/design/blueprint_revision/prior_work/BLUEPRINT_T1_T2_PROOF.md:9, 71` | `tmpAI/bp_proof` |
| `.claude/design/blueprint_revision/prior_work/step4_REVIEW.md:3, 15, 47` | `tmpAI/review4`, `tmpAI/runs/app_run_4c.txt` |
| `.claude/design/lab_revision/prior_work/step4c_report.md:5, 42` | `tmpAI/runs/app_run_4c.txt`, `tmpAI/breakonce4c.py`, `tmpAI/breakonce4c_out.txt` |
| `.claude/design/decisions_2026-11-14/evidence/plot_text_code_execution_2026-11-16.md:11, 12, 105` | `tmpAI/baseline`, `tmpAI/probe/probe_all.py`, `probe_sites.py`, `render_all.py` |
| `.claude/design/home_redesign_intent_and_consequences.md:21, 316` | `tmpAI/intent_turns` |
| `.claude/design/lab_revision/02_planned_vs_existing.md:9, 12`, `SUBTASKS.md:14`, `prior_work/README.md:10, 11, 26` | `tmpAI/run`, `tmpAI/run/probe.py`, `probe2.py`, `out_A` |

Note: the ledger has no broken pointer (27 paths, all exist) (RUN).

## 7. Not verified

- The counts of files and lines are for written documents (`.md`) outside copies of the repository; a few documents inside copies may be counted, a few real ones may be skipped (REASONED). Group rows in 2c are approximate.
- Which ledger line decided what for each study: I used only the numbered lines that quote the study's path. A study that a decision rests on without quoting the path is not shown.
- "Status" (still to read, decided) is my reading of `tasks.md` and the handoff; I did not ask anyone.
- The e-mail test was a pattern search ("@" and a domain) on `.md` files only; other file kinds in the studies (json, py, tsv) were not scanned.
- Whether `diff`-equal copies in git are the newest version of the original: checked for the 17 listed files only.
- I did not check what the indexer loads (section 4 point 8), nor the size of git history.
- Sub-studies listed under 2c (old material) were not read one by one.

---

## Appendix: file by file, with line counts

The appendix is generated from the scan (RUN) and follows below.

### tmpAI/panel/deployment_io/ (13 md files, 1553 lines; 15 files in all)

- BRIEF.md: 35
- FACTS.md: 133
- ORDER.md: 30
- ROUND2_BRIEF.md: 24
- TABLE_FOR_THE_OWNER.md: 427
- architect.md: 298
- architect_round2.md: 93
- developer.md: 148
- developer_round2.md: 61
- scientist.md: 147
- scientist_round2.md: 53
- user.md: 82
- user_round2.md: 22

### tmpAI/panel/deployment_standard/ (6 md files, 1179 lines; 6 files in all)

- BRIEF.md: 45
- FACTS.md: 235
- TABLE_FOR_THE_OWNER.md: 434
- architect.md: 228
- deployer.md: 90
- developer.md: 147

### tmpAI/panel/names_whole_app/ (8 md files, 1396 lines; 11 files in all)

- BRIEF.md: 41
- FACTS.md: 499
- ORDER.md: 22
- TABLE_FOR_THE_OWNER.md: 268
- architect.md: 183
- data_scientist.md: 143
- developer.md: 133
- user_new_to_data_science.md: 107

### tmpAI/panel/name_fields/ (1 md files, 100 lines; 1 files in all)

- TABLE_FOR_THE_OWNER.md: 100

### tmpAI/panel/gallery_study/ (9 md files, 1264 lines; 84 files in all)

- BRIEF.md: 26
- MAP_part1.md: 265
- MAP_part2.md: 274
- Q1_NAMES_AND_HEADINGS_DRAFT.md: 171
- Q2_CHART_TYPE_DRAFT.md: 213
- TABLE_FOR_THE_OWNER.md: 58
- architect.md: 146
- scientist.md: 76
- user.md: 35

### tmpAI/panel/gallery_verify/ (9 md files, 1399 lines; 124 files in all)

- BRIEF.md: 23
- SOURCES_CHECK.md: 58
- TABLE_FOR_THE_OWNER.md: 466
- data_scientist_1.md: 260
- data_scientist_2.md: 247
- data_scientist_2_scratch/ex/lollipop_advanced/example_meta.md: 24
- data_scientist_2_scratch/ex/point_simple/example_meta.md: 20
- statistician.md: 240
- user_new_to_data_science.md: 61

### tmpAI/panel/gallery_taxonomy/ (5 md files, 516 lines; 8 files in all)

- BRIEF.md: 38
- TABLE_FOR_THE_OWNER.md: 187
- data_scientist.md: 107
- statistician.md: 91
- user_new_to_data_science.md: 93

### tmpAI/panel/help_beside/ (8 md files, 482 lines; 116 files in all)

- BRIEF.md: 40
- FACTS.md: 51
- RUN_FACTS.md: 55
- RUN_FACTS_2.md: 42
- TABLE_FOR_THE_OWNER.md: 101
- architect.md: 66
- developer.md: 80
- user.md: 47

### tmpAI/panel/data_import_words/ (1 md files, 124 lines; 1 files in all)

- TABLE_FOR_THE_OWNER.md: 124

### tmpAI/panel/recipe_versions/ (7 md files, 341 lines; 9 files in all)

- FACTS.md: 43
- FACTS_NAME_DATE.md: 25
- M417_owner_decisions_and_open_points.md: 13
- TABLE_FOR_THE_OWNER.md: 44
- architect.md: 120
- scientist.md: 48
- user.md: 48

### tmpAI/panel/recipe_places/ (6 md files, 301 lines; 149 files in all)

- BRIEF.md: 40
- M418_owner_answers_and_study_order.md: 11
- TABLE_FOR_THE_OWNER.md: 51
- architect.md: 88
- scientist.md: 79
- user.md: 32

### tmpAI/panel/adr_history/ (110 md files, 5758 lines; 113 files in all)

- FACTS.md: 35
- TABLE_FOR_THE_OWNER.md: 52
- architect.md: 152
- architect/split_dryrun/ADR-001.md: 15
- architect/split_dryrun/ADR-002.md: 11
- architect/split_dryrun/ADR-003.md: 10
- architect/split_dryrun/ADR-004.md: 13
- architect/split_dryrun/ADR-005.md: 7
- architect/split_dryrun/ADR-006.md: 8
- architect/split_dryrun/ADR-007.md: 11
- architect/split_dryrun/ADR-008.md: 10
- architect/split_dryrun/ADR-009.md: 14
- architect/split_dryrun/ADR-010.md: 10
- architect/split_dryrun/ADR-011.md: 20
- architect/split_dryrun/ADR-012.md: 18
- architect/split_dryrun/ADR-013.md: 14
- architect/split_dryrun/ADR-014.md: 16
- architect/split_dryrun/ADR-015.md: 11
- architect/split_dryrun/ADR-016.md: 11
- architect/split_dryrun/ADR-018.md: 13
- architect/split_dryrun/ADR-019.md: 11
- architect/split_dryrun/ADR-020.md: 11
- architect/split_dryrun/ADR-021.md: 13
- architect/split_dryrun/ADR-022.md: 11
- architect/split_dryrun/ADR-023.md: 10
- architect/split_dryrun/ADR-024.md: 30
- architect/split_dryrun/ADR-025.md: 22
- architect/split_dryrun/ADR-026.md: 14
- architect/split_dryrun/ADR-027.md: 17
- architect/split_dryrun/ADR-028.md: 49
- architect/split_dryrun/ADR-029b.md: 10
- architect/split_dryrun/ADR-029c.md: 10
- architect/split_dryrun/ADR-030.md: 9
- architect/split_dryrun/ADR-031.md: 16
- architect/split_dryrun/ADR-032.md: 12
- architect/split_dryrun/ADR-033.md: 18
- architect/split_dryrun/ADR-034.md: 12
- architect/split_dryrun/ADR-035.md: 15
- architect/split_dryrun/ADR-036.md: 12
- architect/split_dryrun/ADR-037.md: 23
- architect/split_dryrun/ADR-038.md: 11
- architect/split_dryrun/ADR-039.md: 15
- architect/split_dryrun/ADR-040.md: 173
- architect/split_dryrun/ADR-041.md: 26
- architect/split_dryrun/ADR-042.md: 15
- architect/split_dryrun/ADR-043.md: 63
- architect/split_dryrun/ADR-044.md: 42
- architect/split_dryrun/ADR-045.md: 80
- architect/split_dryrun/ADR-046.md: 28
- architect/split_dryrun/ADR-047.md: 84
- architect/split_dryrun/ADR-048.md: 217
- architect/split_dryrun/ADR-049.md: 78
- architect/split_dryrun/ADR-050.md: 48
- architect/split_dryrun/ADR-051.md: 97
- architect/split_dryrun/ADR-052.md: 115
- architect/split_dryrun/ADR-053.md: 25
- architect/split_dryrun/ADR-054.md: 106
- architect/split_dryrun/ADR-055.md: 26
- architect/split_dryrun/ADR-056.md: 28
- architect/split_dryrun/ADR-057.md: 26
- architect/split_dryrun/ADR-058.md: 30
- architect/split_dryrun/ADR-059.md: 42
- architect/split_dryrun/ADR-060.md: 26
- architect/split_dryrun/ADR-061.md: 36
- architect/split_dryrun/ADR-062.md: 24
- architect/split_dryrun/ADR-063.md: 38
- architect/split_dryrun/ADR-064.md: 43
- architect/split_dryrun/ADR-065.md: 42
- architect/split_dryrun/ADR-066.md: 34
- architect/split_dryrun/ADR-067.md: 24
- architect/split_dryrun/ADR-068.md: 27
- architect/split_dryrun/ADR-069.md: 70
- architect/split_dryrun/ADR-070.md: 33
- architect/split_dryrun/ADR-071.md: 123
- architect/split_dryrun/ADR-072.md: 9
- architect/split_dryrun/ADR-073.md: 223
- architect/split_dryrun/ADR-074.md: 113
- architect/split_dryrun/ADR-075.md: 198
- architect/split_dryrun/ADR-076.md: 323
- architect/split_dryrun/ADR-077.md: 66
- architect/split_dryrun/ADR-078.md: 157
- architect/split_dryrun/ADR-079.md: 235
- architect/split_dryrun/ADR-080.md: 38
- architect/split_dryrun/ADR-081.md: 79
- architect/split_dryrun/ADR-082.md: 142
- architect/split_dryrun/ADR-083.md: 61
- architect/split_dryrun/ADR-084.md: 85
- architect/split_dryrun/ADR-085.md: 87
- architect/split_dryrun/ADR-086.md: 57
- architect/split_dryrun/ADR-087.md: 27
- architect/split_dryrun/ADR-088.md: 43
- architect/split_dryrun/ADR-089.md: 58
- architect/split_dryrun/ADR-090.md: 42
- architect/split_dryrun/ADR-091.md: 117
- architect/split_dryrun/ADR-092.md: 20
- architect/split_dryrun/ADR-093.md: 50
- architect/split_dryrun/ADR-094.md: 62
- architect/split_dryrun/ADR-095.md: 108
- architect/split_dryrun/ADR-096.md: 67
- architect/split_dryrun/ADR-097.md: 216
- architect/split_dryrun/ADR-098.md: 27
- architect/split_dryrun/ADR-099.md: 147
- architect/split_dryrun/ADR-100.md: 45
- architect/split_dryrun/ADR-101.md: 23
- architect/split_dryrun/ADR-102.md: 26
- architect/split_dryrun/ADR-103.md: 27
- architect/split_dryrun/ADR-104.md: 28
- architect/split_dryrun/ADR-105.md: 22
- architect/split_dryrun/ADR-106.md: 26
- user.md: 33

### tmpAI/panel/column_labels/ (1 md files, 73 lines; 1 files in all)

- TABLE_FOR_THE_OWNER.md: 73

### tmpAI/panel/seed_step/ (2 md files, 98 lines; 3 files in all)

- QUESTION_and_FACTS.md: 42
- TABLE_FOR_THE_OWNER.md: 56

### tmpAI/panel/column_tracking/ (5 md files, 274 lines; 417 files in all)

- FACTS.md: 68
- OPENING_BUILD_figures.md: 64
- OPENING_CHECK_options.md: 63
- TABLE_FOR_THE_OWNER.md: 76
- measure/progress.md: 3

### tmpAI/panel/audit_recipe_file/ (4 md files, 199 lines; 10 files in all)

- FACTS.md: 56
- TABLE_FOR_THE_OWNER.md: 63
- ZONE_TABLE_FOR_THE_OWNER.md: 47
- ZONE_question.md: 33

### tmpAI/panel/lbfb/ (6 md files, 910 lines; 28 files in all)

- BRIEF.md: 29
- BUILD_PLAN.md: 329
- LOGIC_REVIEW.md: 265
- QUESTIONS_FROM_STEP1.md: 15
- scientist.md: 226
- user.md: 46

### tmpAI/panel/lineage_tests/ (13 md files, 1843 lines; 24 files in all)

- DESIGN.md: 687
- architect/p1.md: 48
- architect/p2a.md: 90
- architect/p2b.md: 116
- architect/p2c.md: 143
- architect/p2d.md: 120
- architect/p2e.md: 9
- architect/p3.md: 70
- architect/p4.md: 28
- architect/p5.md: 53
- architect/p6.md: 19
- scientist_cases.md: 404
- user_cases.md: 56

### tmpAI/panel/recipe_error_place/ (1 md files, 48 lines; 1 files in all)

- TABLE_FOR_THE_OWNER.md: 48

### tmpAI/panel/panel_widths/ (4 md files, 93 lines; 15 files in all)

- BRIEF.md: 33
- BRIEF_ROUND2.md: 29
- OWNER_WORDS_NOT_YET_IN_LEDGER.md: 2
- architect_round2.md: 29

### tmpAI/panel/formula_d/ (11 md files, 1024 lines; 58 files in all)

- EVIDENCE.md: 424
- PANEL_for_eve_2026-11-18.md: 70
- extra_table.md: 23
- head.md: 55
- hostile_table.md: 63
- mid1.md: 15
- mid2.md: 152
- mid3.md: 110
- tables.md: 50
- tail.md: 47
- weak_table.md: 15

### tmpAI/panel/stat_function_polars/ (3 md files, 376 lines; 25 files in all)

- REPORT.md: 296
- block_builder_report.md: 23
- evidence/names_table.md: 57

### tmpAI/panel/id_vs_key/ (1 md files, 51 lines; 1 files in all)

- scout_what_exists.md: 51

### tmpAI/panel/axis_text/ (3 md files, 234 lines; 2406 files in all)

- FACTS.md: 139
- INDEX.md: 26
- PANEL_for_eve_2026-11-18.md: 69

### tmpAI/panel/path_use_cases/ (4 md files, 368 lines; 4 files in all)

- EXPORT_RECORD_facts.md: 14
- FACTS.md: 73
- PANEL_for_eve_2026-11-18.md: 84
- TRIAL.md: 197

### tmpAI/panel/adr/ (4 md files, 332 lines; 6 files in all)

- ledger.md: 170
- ledger_before_2026-11-15_2330.md: 94
- review_corrections.md: 24
- taken_by_report.md: 44

### tmpAI/coordinator/gallery_walk_2026-11-20/ (1 md)

- tmpAI/coordinator/gallery_walk_2026-11-20/FINAL_REPORT.md: 67

### Loose documents in tmpAI/panel/ (your words and question pages)

- tmpAI/panel/DEMO_BRANCH_PLAN_2026-11-18.md: 82
- tmpAI/panel/QUESTIONS_SORTED_2026-11-19.md: 111
- tmpAI/panel/QUESTIONS_for_eve_2026-11-18.md: 363
- tmpAI/panel/READINESS_for_demo_2026-11-18.md: 50
- tmpAI/panel/READINESS_for_demo_2026-11-18_v2.md: 67
- tmpAI/panel/brief_joins_gallery.md: 21
- tmpAI/panel/brief_na_default_formulas.md: 18
- tmpAI/panel/brief_round4.md: 28
- tmpAI/panel/brief_round5.md: 40
- tmpAI/panel/brief_view_vs_export.md: 18
- tmpAI/panel/proposals_for_eve.md: 455
- tmpAI/panel/viz_plan_for_eve.md: 85

The old-material groups of section 2c are not listed file by file (about 560 files); the scan data is in tmpAI/coordinator/permanent_documents/scratch/ if you want it.
