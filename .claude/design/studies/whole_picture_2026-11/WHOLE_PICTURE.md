# The whole picture: how HOME is meant to work (actualised in place, 2026-11-24)

Updated 2026-11-24 after the build for the demo (merges `3b59d97b` to `b3889404`); checked by a second agent against the ledger.

## 0. Status, and where the truth lives

**What this is.** The one document that says what is decided and how the pieces work together. It is updated in place (her order, D-0605: new documents all the time make the decided truth impossible to follow). It replaces version 5 (2026-11-22), kept in git at commit 0e149e31 with her `@eve` notes; the older text and the old numbered questions are there. Actualised 2026-11-24. Section 6 says what is built.

**Marks.** A decision is written once, in plain words, with its ledger number; her exact words are in the decision ledger and are not repeated here (cleaning of 2026-11-24, D-0613). "Reading" is the review session's or an agent's reading of her words, never her decision. "Her view" is something she said with "I think". [REASONED] is reasoning, not run. "Designed" means decided or proposed and not built.

**Four plain words are used instead of the developers' term for a lookup name:** a name in the recipe file (developers' word: `YAML key`); a column name; the entity id (the column that identifies the entity); the fingerprint of a stored table (developers' word: `cache key`). The demo's entity is a sample; everywhere else it is "the entity". A number such as D-0508 is a line of the decision ledger, the list of your decisions (`.claude/knowledge/decision_ledger.md`).

### WHERE THE TRUTH LIVES (the index the agents read first)

Eight files remain in this folder: this one, `PATHS_AND_DERIVED_AGREED.md`, `CAUSE_AND_SOLUTIONS_ZEROS.md`, `OVERLAP_AND_POPULATION.md`, `RECIPES_FROM_THE_MODEL_AGREED.md`, `DESIGN_AGREED_AND_QUESTIONS.md`, `RECIPE_PROPOSAL_refined.md`, `GOALS_REVIEW.md`. Ten files were removed on 2026-11-24 (their text stays in git history): `BIG_VIEW`, `BUILD_ORDER`, `DIFFERENCES`, `PARTS_TABLES`, `MATCH_LIST`, `GOALS_REVIEW_sonnet`, `T0_OPTION_REVIEW`, `RECIPE_PROPOSAL_answers`, `RECIPE_PROPOSAL_dialog_walkthrough`, `RECIPE_REDESIGN_REVIEW`. The seven other kept files still hold quotations of her words from the study rounds; their decisions are in the ledger.

Status words: current / historical / superseded by <file> / "status to settle".

| Topic | The ONE file with the current truth | Other files that touch it, and their status |
|---|---|---|
| The big line, the goals | this file, section 1 | `GOALS_REVIEW.md`: current for her goals (D-0528); historical for its dialog and its questions (written 2026-11-22, before D-0535 to D-0550). Removed 2026-11-24, see git history: `BIG_VIEW.md` (folded into this file), `GOALS_REVIEW_sonnet.md`, `MATCH_LIST.md` |
| The recipe design | `RECIPES_FROM_THE_MODEL_AGREED.md` (its "Review of 2026-11-23" at the top says what is still true) | `RECIPE_PROPOSAL_refined.md`: current as the text of the proposal "form 3", NOT confirmed (D-0496). Removed 2026-11-24, see git history: `RECIPE_PROPOSAL_answers.md`, `RECIPE_REDESIGN_REVIEW.md`, `RECIPE_PROPOSAL_dialog_walkthrough.md` |
| The ids, the completion, the log | `CAUSE_AND_SOLUTIONS_ZEROS.md`, the sections dated 2026-11-23 from D-0581 onward and its closing text (D-0593 to D-0599) | `OVERLAP_AND_POPULATION.md`: current for the overlap numbers of the demo and the checks; its earlier parts are marked "changed by" and are historical. The earlier sections of `CAUSE_AND_SOLUTIONS_ZEROS.md` (the catalogue of solutions) are historical where marked "changed by D-0581" or "no longer needed" |
| The audit and the places | `PATHS_AND_DERIVED_AGREED.md` (its "Review of 2026-11-23" at the top) | `DESIGN_AGREED_AND_QUESTIONS.md`: superseded in part by the recheck table of `PATHS_AND_DERIVED_AGREED.md`. Removed 2026-11-24, see git history: `BUILD_ORDER.md`, `T0_OPTION_REVIEW.md` (T0 is dropped, D-0613) |
| The lineage and the graph | `PATHS_AND_DERIVED_AGREED.md` (points G1 to G22) and the code `libs/utils/src/utils/recipe_graph.py` | `DIFFERENCES.md` and `PARTS_TABLES.md` (the comparison of 2026-11-22): removed 2026-11-24, see git history |
| The export | no study file holds it: the ledger lines D-0490 to D-0492, D-0324, D-0333, D-0478, D-0575 and `ui_implementation_contract.md` section 7.2; this file, section 2.6 | none |
| The demo's oddities | `.claude/knowledge/demo_deliberate_oddities.md` (outside this folder) | `OVERLAP_AND_POPULATION.md` holds the id counts it cites |
| The dry run of the big move | `assets/scripts/dry_run_big_move.py` (built) and its report `.claude/design/studies/whole_picture_2026-11/sources/tmp_2026-11-23/dry_run_big_move_report.md` (scratch: `tmp/` is not permanent, D-0419; run the script again to rewrite it) | none |
| What is built | this file, section 6 | none |

## 1. The big line, in six sentences

1. **A recipe is a directed graph.** Tiers sit at the nodes and the branches give the directions; results (final tables and plots) are the leaves [D-0553]. The user chooses at most one place on a path, except that all the original parents may be chosen; every path below the choice is derived and cannot be chosen (the rule of places, "R2") [D-0553]. The tiers hold steps shared by several next tables; only the last table cannot hold what several results use [D-0539].
2. **A recipe does not start from the metadata.** The original data comes first, left joined to the metadata when a metadata join is needed [D-0586; also D-0564, D-0510]. This is her decided rule. It is built in the shipped recipes (the one big move, merge 1f6cb913, section 6), with the exceptions the handoff lists for the owner. How the rule is enforced for new recipes (refused by the check, advised, or documented) is not decided.
3. **Before anything else the ids are made equal.** Every original table and the metadata get the ids they lack, with a marker; the recipe says what a marked line means; nothing blocks, the app warns and writes a log [D-0572 to D-0591; built, merge 1f6cb913 (the checks, the completion, the log); the warning in HOME is built, merge c6d56f47].
4. **An audit step** is a filter, a column drop or a removal by the entity id, with a reason [D-0322], written at a place the user chooses (built, merge 2349ddac: tier 1, 2 or 3 through the audit copy), at the end of a tier of a table [D-0535, D-0541]. In one step, at most one chosen place on a path; everything below it is derived and cannot be chosen [D-0553, D-0547].
5. **Everything below a changed place is recalculated.** A step after a change is never served from a stored table of before [D-0560].
6. **The app never cleans data in HOME.** Cleaning tools live in the Lab or in other tools on the user's side [D-0594, D-0595, D-0596]. The app makes the problem visible where it can (D-0593).

## 2. How it works: a short status, as the user meets it

```text
original files (read as they are; never changed)
   |  the read: spaces stripped, the missing-value marks of the recipe, the declared type
   v
ids made equal: three checks, completion with markers          [built, merge 1f6cb913; see section 6]
   result = the data file with its added ids. The user cannot choose the place before the completion (D-0602).
   T0 is dropped (D-0613): no T0 node, no T0 place; the first place is tier 1; the completion of ids runs when the files are read, before tier 1 (section 3)
   |  red warning + "I have read this" button, a log, nothing blocks (built, merge c6d56f47)
   v
tier 1   clean; the join with the metadata is here: the data table first, left join on the metadata (her rule; built in the shipped recipes, section 6)
   v
tier 2   compute
   v
the plot's own steps (tier 3: the table the plot reads)
   v
results: a plot or a table

beside it, the AUDIT: one chosen place on a path; every table below is recalculated (built, merge 2349ddac); the measure and the log of the effects: designed, not built (section 6, held)
beside that, the EXPORT: the results, the audit recipe with its record, the original recipe, the logs (section 2.6 says what is built)
```

### 2.1 The files and the recipe
- A recipe has three blocks of tables: `data_schemas` (results of analysis about the entities), `metadata_schema` (the information about the entities, one table), `additional_datasets_schemas` (look-up tables and databases, not results about the entities, used in later joins) [D-0512, D-0513, D-0610]. On the demo, `VirulenceFinder` moves to `data_schemas` [D-0523, D-0524]; this was done in the one big move (merge 1f6cb913).
- The field `is_entity_key` became `is_entity_id`, one name for all cases (D-0562; built, merge `3b59d97b`). The sentence she approved (D-0567; the wording is the review session's): the column that identifies the entity, used to join with the metadata and to find the entity's rows; if its values are unique it also identifies each row of the table (one row per entity), if they repeat the table has several rows per entity (a long table).
- The tiers are not a plain division: tier 1 can hold steps common to several tier 2, and tier 2 steps common to several tier 3; the point is to avoid costly recalculation [D-0539].
- A joined table reads the tier 1 of each ingredient; the join with the metadata is a tier 1 step [D-0510, D-0523; the recipe check already refuses a join step written in tier 2 or tier 3 (code ST05, `libs/utils/src/utils/recipe_check.py:717-718`; the steps allowed in tier 1 only are `polars_join`, the as-of join and the conditional join, `libs/utils/src/utils/action_names.py:66`; read in the code on 2026-11-23, not run in this pass); `PATHS_AND_DERIVED_AGREED.md` G2 gives the edges]. The recipe form with derived tables ("form 3") is not confirmed [D-0496].
- A result is a plot or a table, shown at its last stage; a table result is exported by its name [D-0485, D-0487].
- Unchanged and not touched by this picture: the tiers, the fixed random seed, Exploration, the Gallery.

### 2.2 The ids made equal (built, merge 1f6cb913)
- **The read first.** What the read of the file does: it strips the text, turns the marks the recipe declares into missing, then reads the declared type (`libs/ingestion/src/ingestion/declared.py:115-120`). The recipe handles the meaning of "-" and the trimming [D-0597].
- **The three checks, all shown together, none stops** [D-0581]: (1) ids of a result file that are in no metadata; (2) ids of the metadata that are in no result file; (3) after the completion, the unique ids of all the tables, and of the metadata when it exists, are the union of all the unique ids. If many ids do not match, there is a problem upstream, for example in a pipeline [D-0591]. With a metadata a difference at check 3 means a bug in the app (her view, D-0590).
- **The completion.** Each original table gets a line for each id it lacks, marked as not in the original data; the metadata gets a line for an id found only in a result file [D-0572, D-0573, D-0585]. As built the marker is a yes/no column `<table>_not_in_original_data` for every table, the metadata included (D-0615 for the marker; D-0613 for the form). The marker name `not_in_metadata` no longer exists; one result field of the first id check keeps that name inside the code (`libs/utils/src/utils/id_completion.py:315`). It is recipe-wide, with or without a join, as long as a metadata file is attached [D-0589]. It changes or removes nothing from the user's data [D-0597]. Why: the data can always use left joins with the metadata, which limits lineage problems [D-0584].
- **The meaning.** The recipe must state what each marked line means; the marker is not a zero [D-0573, D-0574, D-0586]. The marker column is kept [D-0586]. The recipe never records how many lines were added [D-0574]. As built the meaning is a free sentence of the recipe maker (D-0616).
- **The warning and the log.** Nothing blocks, only warnings [D-0581]. As built, the red warning is shown in every setup of the app, also where the audit panel is absent (merge `c6d56f47`; provisional). With a panel the warning is red and has a button that does not block (she chose that form, D-0582; the words "I have read this" and "automatic, no user" for the log with no panel are the review session's wording, D-0582) [D-0581]. The log is simple, separate from the audit log, written automatically in a directory, in the session and in the export, and the person using the results must read it [D-0582; also D-0575, D-0576, D-0592]. A static deployment needs a person who reads the log; this must be clear in the documentation [D-0585].
- **T0: dropped (D-0613).** She suggested, as an option and not a decision, a first node T0 = the data file with the added ids [D-0602, D-0603]. The owner then dropped it (D-0613): no T0 node, no T0 place. The lineage uses the tiers as its nodes; the first place is tier 1; there is no T0 node (D-0613). The user cannot choose a place before the completion (D-0602).
- **On the demo** (`OVERLAP_AND_POPULATION.md` section 1): 42 entities in the metadata; `ResFinder` has a line for 38 of them and none for 4 (the 4 entities with 0 genes); every other result file has all 42. So the completion adds 4 lines to `ResFinder` and nothing else.

### 2.3 A line with no usable id (her question, D-0607; answer: design, reading of the agents, to confirm)
Her question (D-0607): how will this work if the null ids are not cleaned?
- **What "usable" means.** The read itself: the text is stripped (when the recipe declares `strip`) and a value is missing when it is one of the marks the recipe declares for that column (`declared.py:115-120`). **A trap:** a cell of only spaces becomes an empty text; it is read as missing only if the empty text is one of the declared marks. A column that declares no mark keeps it as text.
- **Design.** Such a line is not an id. It is not part of the set of unique ids. It adds no line to any other table. The app does not remove or fix it [D-0594]. It stays in its table. The warning and the log list it: the count per table and the lines.
- **In a join that starts from a data table**, such a line finds no metadata, so its metadata columns stay empty (reasoning: a missing id does not match in a join; not run). Another trap [REASONED, not run]: two lines whose id is the same empty text can match each other.
- **In a table that starts from the metadata**, all such lines together make one group with no id (how the table engine groups rows, established in `CAUSE_AND_SOLUTIONS_ZEROS.md`, not run).
- **Who removes it.** The user or the recipe maker, by a visible step in the recipe, as `demo_abromics` did; the handoff says that step was removed from `demo_join` in the big move and lists the option of keeping it as a visible step.
- **Facts of the demo.** The metadata of the main demo recipe has no such line (42 distinct ids, none empty; dry run section 6). `demo_abromics` has three, lines 5, 6 and 11 of its metadata file: empty, a dash, two quote marks. They stay in the shipped file, and a record of such particularities is kept for the maintainers (D-0604; that this means "the three lines stay" is the review session's reading). Whether the third (two quote marks) is read as missing: the two sources disagree, see "to check" in section 7.
- **The one question this leaves her:** is this reading right: a line with no usable id is not an id, stays where it is, and is listed, never removed by the app? D-0594 and D-0597 point that way; she has not said it for this case.

### 2.4 The audit (built at the chosen places, merge 2349ddac; the effects measure and log are designed, not built)
- **A step** is a filter, a column drop or a removal by the entity id, with a reason [D-0322; whether column drops stay is question 29 of version 5, section 5]. It is written in the audit recipe, a copy; the steps of the original recipe are always kept; audit steps can be written at each tier after the original tier block [D-0541]. The first build replaces the audit at the plot's table by steps at each tier [D-0535].
- **The places.** A place is a table at a tier. On the demo the graph has 85 nodes (12 files, 28 tier 1, 28 tier 2, 17 plots) and 58 places; the engine accepts a step at 55 of them (`PATHS_AND_DERIVED_AGREED.md` G1, half page 5). The user chooses at most one place on a path; what is below is derived, marked "~", not chosen [D-0547, D-0553]. Several independent histories (original parents) may each take the step at their first tier 1, because of independent histories [D-0547]. When several parents are chosen, the step is written in each tier 1 that comes from the parent; a parent reused in another graph is a gotcha, so both graphs are shown (how: not decided) [D-0555]. What is derived when a node has several parents is not decided (D-0553, under review in `PATHS_AND_DERIVED_AGREED.md`), nor which place "each tier 1 from the parent" means.
- **The default** is where the original tier 1 and the metadata are joined, because filtering there removes the entity from all other data without removing it in the metadata itself [D-0549]; with no metadata join, the first tier 1 of the lineage [D-0550]. The scope is the user's: the app cannot decide the scope [D-0531]; the app informs [D-0543].
- **Recalculation and effects.** Everything below the place is recalculated, no stored table of before is served [D-0560]. The effects are measured after Apply, registered, and kept in the log; what is shown to the user is decided later [D-0536, D-0537, D-0545, D-0546]. Measuring at each trial is not decided; it can cost too much (D-0545).
- **"Remove from all the data"** is the one automatic placement, off until asked [D-0416]; her case is to keep the entity in the quality results only while removing a bad entity from all other results [D-0499]. The user may untick a table. The library step is built; the screen with the ticks is not. Its form is question 2 of section 3.
- **Remove step**, one undo control [D-0314]. The audit log (who, when, the reason, the scope, the warnings) is always in the export [D-0478].
- **On the demo** (a run of 2026-11-23 by one of the two design agents, `PATHS_AND_DERIVED_AGREED.md` half page, point 5): one entity removed at each of the 55 places where the engine accepts a step, each variant rebuilt from scratch; the tables whose fingerprint changes are exactly the tables below the place, and the tables whose content changes are among them; a wrong stored table that carries the old fingerprint is never served.

### 2.5 What the app never does
- No cleaning in HOME [D-0593 to D-0596]. Data Import accepts TSV and Parquet [D-0602]; HOME accepts TSV; the conversion is done in Excel (D-0597); that the user does it is a reading. The Excel converter is a Lab tool, in developer only for now [D-0602]. The meaning of "-" and the trimming are the recipe's and the user's job [D-0597].

### 2.6 The export
Read on 2026-11-24 in `.claude/rules/ui_implementation_contract.md` section 7.2 (rules 4, 8 and 9) and `.claude/knowledge/changelog.md` (entries of 2026-11-24).
- **Built:**
  - Audit steps written at a table are applied to the data file and the figure of every plot built from the place; `t3_steps.yaml` lists them under `steps_by_place`; README.txt and report.qmd say where each step is written and why; the reproducibility recipe holds each step as a plain step of its tier (contract rule 8; merge `2349ddac`).
  - An export made in Audit mode writes `<table>/T1_data_audited.tsv` and `T2_data_audited.tsv` beside the originals for every table an audit step changes (contract rule 9; the form is PROVISIONAL).
  - Every export holds `id_log.yaml` and README.txt names it; the Export panel shows one line about the log; report.qmd has a section "The ids of the tables" (changelog, entries "The ids are made equal" and "The warning of the ids in HOME"; merges `1f6cb913`, `c6d56f47`).
- **Decided, not built** (contract section 7.2 rule 4 still reads "DECIDED, not built"): the reproducibility bundle with two parts, the original and the audited result, with the data stored once and read by both, and a clear statement which is which [D-0490, D-0492]; the report with `# Results` before `# Technical` [D-0491]; the audit log, the audit record and its hash in every bundle of an audit [D-0478, D-0333]; a table result exported by its name [D-0487]. Part names are not decided. Not decided: whether the exported tier 1 and tier 2 files become audited in Exploration mode (as built they stay the originals there).

## 3. What is still yours to answer, in one place, in the recommended order

### THREE HEAPS (her order, D-0612: fix what is already decided; small things were mixing with new things)

**(a) DECIDED, to be written and built: no question.**
1. The ids are made equal by a completion, with a marker on every added line (D-0572 to D-0591; built, merge 1f6cb913). The form of the marker and how each table treats the marked lines were open in D-0573 and D-0585; the form was fixed provisionally in the build (D-0613, D-0615, D-0616).
2. Nothing blocks, only warnings (D-0581).
3. A simple separate log of the ids, written automatically, in the session and in the export (D-0575, D-0576, D-0582, D-0592).
4. A red warning with a button that does not block (D-0581, D-0582) (the review session's reading of your decision; built, merge c6d56f47).
5. Recipes do not start from the metadata (D-0586); the marker column is kept and the meaning of a marked line is required (D-0586, D-0574).
6. No cleaning in HOME; Data Import accepts TSV and Parquet; the Excel converter stays in the Lab (D-0593 to D-0597, D-0602).
7. The two metadata-only tables (`QA_year_types`, `QA_aggregated_no_key`) and `VirulenceFinder` move to the data schemas (D-0608; D-0523; line 7 of the dry run, D-0610) (the review session's reading; done in the big move).
8. The entity id is `sample_id` for the six tables of `2_test_data_ST22_dummy` and `figshare_integration`; the APEC list stays a look-up with no entity id (D-0610 and D-0611) (the review session's reading; done in the big move).
9. The rename to `is_entity_id` (D-0562, D-0567; built).
10. The audit writes steps at each tier at the places the user chooses; at most one place on a path; everything below is recalculated; effects are measured after Apply and kept in the log (D-0535, D-0536, D-0537, D-0545, D-0546, D-0553, D-0560; the places are built, the measure and log are not).
11. The rule of places is built as a library (merge 1497c2bc; section 6) (no ledger line: the go-ahead is D-0613).

**(b) NOT YET DONE: decided, or waiting only for work.** A drawn lineage in HOME is not built. Built: the dialog lists the places along the path and marks the derived places (merge `b3889404`). Not built: places on other branches than the open plot's; a result table with no plot as a leaf. Also not done: the sentences of what a missing line means for every table except ResFinder (section 6); the documentation task, the rules on the ids early in the guidelines (D-0583) (the user guide pages `understanding_your_export.qmd` and `good_practice_recipes.qmd` and section 15 of `ui_implementation_contract.md` were written: merges `1f6cb913`, `c6d56f47`); the manual test, after the mechanical build and the browser tests (D-0604); the measure and log of the effects of an audit step (D-0536, D-0537; held); the export parts of section 2.6 marked "decided, not built". The one big move of the demo recipes is done (merge 1f6cb913, section 6), except what the handoff's line "For the owner at the end" lists. The cleaning of the studies (D-0605, D-0606) is done in this pass.

**(c) NEW OR OPEN: the questions that block, at most four, in this order.** 1. The form of "remove from all the data" (question 2). 2. The recipe form (question 3). 3. Line 4 of the dry run, table by table (question 4, after the scan). 4. Where the record goes when the log's folder cannot be written (question 5). (The list numbers differ from the question numbers; the question numbers are kept, because the text refers to them.)

The small questions are kept apart, for after the big line (D-0599): see the list below.

**Answered since version 5, no longer asked:** question A (the completion reads the files as they are): the files are read as read (D-0602). Where the dialog starts and the effect on each result (old question 28): places as decided, effects measured and registered, shown later [D-0535, D-0536].

**Her view, not a final decision (D-0607):** question C (which tables are one population when there is no metadata): the population is the set of unique ids in all the tables, which leads to problems when there is a null id; the answer to that second half is in 2.3. What remains for the agents to state (their reading, not hers): which tables count are those that declare an entity id; a reference table with none, such as the APEC gene list, stays out (an earlier lean added: or the table named by `entity.population`).

**Question 1 is settled (D-0613), so the hold on questions 2 (E) and 3 (B) lapses:** they are open for her choice. Built for the completion, as PROVISIONAL forms (D-0613; she can change them): the completion block is read by the app before the recipe's tier-1 steps; the marker is a yes/no column `<table>_not_in_original_data` (D-0615); the meaning is a required free sentence (D-0616). She had said (D-0607) that her answers to E and B depended on whether T0 is accepted.

### Question 1. T0: is "the data file with its added ids" a place you may choose?
- **ANSWERED: T0 is dropped (D-0613).** No T0 node and no T0 place; the first place is tier 1; the completion of ids runs when the files are read, before tier 1. The review of the option (D-0604) is removed from this folder (git history); the "with T0" readings under questions 2 and 3 are void.
- **Two traps remain for the first place (the recipe's own tier 1 steps act on added lines)** [REASONED, not run]: a filter by value with "remove the rows with no value" also removes the added lines of other entities; and `ResFinder` stamps "Detected" on every line (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_wrangling_tier1.yaml:2-4`), so the 4 added lines would read "Detected" (the build handles ResFinder: the added line reads Not Found, counted as 0, D-0617). The dry run counts 20 steps that keep only a fixed list of columns and would drop a marker column (question 4).
- **Also open:** does the Source view show the file as read, or with the added ids? Her decisions cover neither.

### Question 2 (E). Which form of "remove from all the data" is offered?
- Three forms were measured on the demo (`PATHS_AND_DERIVED_AGREED.md` point 7, question 5). All three give the same 17 plot tables and leave the entity in none. They differ in the exported tier 1 files: (a) the 27 places in two steps and (b) the 11 first places (the first tier 1 of the 11 originals that declare the entity id; `PATHS_AND_DERIVED_AGREED.md` question 5) clear the entity from every original table; (c) the defaults, one step on 19 places, leave it in 7 original tables (6 with `T1:ResFinder`). Her decided form (tier 1 of every table that holds the entity id, D-0416) and the rule of one place per path cannot both hold in one step (35 pairs one below the other).
- T0 is dropped, so the places begin at tier 1 and the three forms stay as measured.
- Options: the three forms above. Neither: say what you meant. Question 1 is settled (D-0613); no hold. No lean is recorded in this file; neither agent chose.

### Question 3 (B). The recipe form
- The proposal "form 3" (blocks in order: original tables, joined tables, derived tables, results) is not confirmed [D-0496]; forms 4 and 5 are set aside (D-0496, as the review session reports her decision). Options as put in version 5 (commit 0e149e31, part 8, question 2): (a) confirm form 3 (with one level of derived tables, or any number); (b) another form (a form of your own); (c) not yet. Neither: say what you meant. The tier 3 question and the table results are in `RECIPE_PROPOSAL_refined.md`; the questions that remain after the review of 2026-11-23 are at the top of `RECIPES_FROM_THE_MODEL_AGREED.md`. One element is decided and built: the completion block on every result table, with its meaning required [D-0574].
- With T0 dropped nothing is added to the form for a step list before the author's steps. Question 1 is settled (D-0613); no hold.

### Question 4. Line 4 of the dry run of the big move: the 20 steps that keep a fixed list of columns
The dry run changes nothing; it lists what each change would do (`.claude/design/studies/whole_picture_2026-11/sources/tmp_2026-11-23/dry_run_big_move_report.md`; numbers are the report's). Lines 1, 2, 3 and 5 to 8 are answered; only line 4 is still open. The answered lines:
- **Line 1, answered.** The three id-less lines of `demo_abromics` stay in the shipped file, as a lesson (D-0604; the review session's reading); the maintainers' record is `demo_deliberate_oddities.md`.
- **Line 2, answered.** Two joined tables are made from the metadata alone (`QA_year_types`, `QA_aggregated_no_key`); they break no rule, but as there is no real metadata nor join they move to the data schemas [D-0608] (reading of the review session: "they" are these two tables). Done in the big move; what remains is listed in the handoff.
- **Line 3, answered** [D-0608]. Five joined tables started from the metadata (four of the main demo recipe: `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; and `demo_join` of `demo_abromics`). They were rewritten by hand, data first (D-0586; done in the big move).
- **Line 5, answered** (D-0610 and D-0611). The entity id of the other tables is `sample_id` (the review session reads "the other" as the six tables of `2_test_data_ST22_dummy` and `figshare_integration`). `APEC_STEC_virulence_genes` is a look-up and stays under the additional datasets, with no entity id and outside the completion (she verified it).
- **Line 6, answered: postponed.** The Gallery examples, to later [D-0610].
- **Line 7, answered** [D-0610]. `VirulenceFinder` moves into `data_schemas`, because the additional datasets are for look-ups and databases, not results about the entities. The decision names the table, not the recipe; the review session reads it for both recipes (`1_test_data_ST22_dummy` and `1_Abromics_general_pipeline`); D-0523 and D-0524 already covered the first. Her definition goes into the specification and the guidelines.
- **Line 8, answered** [D-0610].
- Mechanical, no decision: the names pass (524 changes) and the rename to `is_entity_id` (225 lines); both done.

**Line 4, still open.** 20 steps keep only a fixed list of columns and would drop the marker column (3 first in their stage, 10 last, 3 elsewhere or alone, 4 group-by; the dry run's counts). Her decision (D-0608): the data must be examined table by table, and the fix is made as early as possible, starting at the original data; she asked whether all the recipes with those tables have the metadata as a left join in tier 1. The two ways of D-0587 stay as the two options for each table: the fixed column list is increased by the column that keeps the markers, or the missing data is processed before tier 1 and the marker column is explicitly dropped.
- **The scan's answer to her question** (read only, fact-checked by another agent; the table-by-table page is `.claude/design/studies/whole_picture_2026-11/sources/tmp_2026-11-23/scan_metadata_joins_and_fixed_lists.md`): not all are left joins: the recipe `2_test_data_ST22_dummy` brings the metadata in by a join that keeps only the rows found on both sides. Of the 20 steps, 3 sit in original data tables: `MLST`, `VirulenceFinder`, and `Genes` of a test recipe (`retest_bad_select_column.yaml`).

### Question 5. Where does the record go when the log's folder cannot be written?
- Today a folder that cannot be written warns and does not stop the start (section 6). A static deployment could lose its only record [D-0581, D-0585]. The agents' proposal, not decided (`CAUSE_AND_SOLUTIONS_ZEROS.md`, closing text (b) 3): the record goes into the export and the console, and the red warning says that the log could not be written (as built, the text is printed to the console and returned, and every export holds `id_log.yaml`). Neither: say what you meant.

### After the big line (titles only; the agents' lean is PROVISIONAL meanwhile)
- A parent reused in another graph: what the app shows (PATHS Q1); which place is "each tier 1 from the parent" (Q2); how the recipe states the default place (Q3); the default where her rule says nothing (Q4); whether the app says before Apply that the entity can remain below (Q6).
- A look-up join after tier 1 (version 5 question 27); a system for joins that are not metadata [D-0562]; an inner look-up join that removes rows; the engine does not run the recipe check (a gap or by design).
- A recipe whose only table is the metadata is registered as data: her view [D-0588], a documentation guideline; whether it becomes a rule of the format.
- The completion: the block's names, its position (before the recipe's tier 1 steps is the lean), the log's directory and name, how often the button is asked, where the red warning shows, a repeated id, a dummy id, how "data first" is enforced (check, advice, documentation), the count per target, the threshold, the converter text of the rules file.
- Column drops in the audit; the Reshuffle; sessions saved before the audit recipe; the lineage picker and where it opens; the export (the original picture, the original recipe in the Publication part); the words and defaults on screen; the audit log's details; tables no plot reads and their tiers; the recipe upload code.
- The eleven readings of version 5 ("accept all", never answered): they stay readings (section 5).

## 4. YOUR NOTES (@eve) AND WHAT BECAME OF EACH

Version 5 had **11** `@eve` markers (`git show 0e149e31:.claude/design/studies/whole_picture_2026-11/WHOLE_PICTURE.md | grep -c "@eve"` gives 11 lines). They are the notes N1 to N11 of the ledger, D-0538 to D-0548; her answers D-0549 and D-0550 follow. The review session read each note and she confirmed that its reading was correct [D-0550]. Line numbers are those of version 5.

| N | Line | What her note said (plain words; her exact text is in the ledger) | What became of it |
|---|---|---|---|
| 1 | 22 | Yes: an observation is a row of a table | Decided D-0538 |
| 2 | 23 | The division into tiers is not that simple: tier 2 can hold steps common to several tier 3, tier 1 steps common to several tier 2; only tier 3 cannot hold what different results use; this avoids costly recalculation and allows branching to a step unique to a result | Decided D-0539; section 1 sentence 1 |
| 3 | 24 | The lineage must correspond to the passage of data through the tiers to the results, back and forth | Decided D-0540; the lineage is the graph (section 1) |
| 4 | 25 | Yes: audit steps can be written at each tier after the original tier block; the original recipe steps are always kept | Decided D-0541; section 2.4 |
| 5 | 26 | Yes: the audit recipe is correct as defined | Decided D-0542 |
| 6 | 46 | We must inform the user so the user can make good decisions; we cannot prevent a wrong decision if the user really wants it; our job is to give information as clear as possible | Decided D-0543: the app informs and cannot prevent (reading: "wrong" in her first sentence is a typo for "good", a note of the review session) |
| 7 | 53 | She does not agree with the sentence that her goals pull against each other: the tool delivers reliability, correct science, transparency, reproducibility and information; the user uses the tool; it is not our role to decide that a choice is bad | Decided D-0544: the sentence of version 5 is deleted (reading confirmed by her); it is not in this file |
| 8 | 77 | To show the effect, the steps after the place of change must be applied: all of them are recalculated and you cannot see an effect without recomputation; recalculating at each trial can be too costly | Decided D-0545: the effect is known after Apply, in the log; before confirming only the structure; section 2.4 |
| 9 | 78 | Again: after Apply | Decided D-0546 |
| 10 | 81 (and the unmarked paragraphs of her note at lines 83 to 92) | What goes wrong here: the user can only choose where to write the step in one correct scope; all the steps after are the following history and are derived; every derived step gets a "~" (the whole text is in D-0547) | Decided D-0547, then D-0553 (one place per path; originals may all be chosen); the "~" mark and the history shown on the step are in section 2.4. Still open under it: how the graphs are shown (D-0555) |
| 11 | 122 | The effect came out so because the steps were added in tier 3 and not in the correct place; this needs to be revised | Decided D-0548: to be revised; the first build writes at each tier (D-0535); the retest under her scope is in `PATHS_AND_DERIVED_AGREED.md` (half page 5 and 6); the effect numbers of version 5 are no longer used |

## 5. THE QUESTIONS OF THE EARLIER VERSION AND THEIR FATE

Version 5 had **30** numbered questions. One row each. Each question has ONE fate: answered (the ledger line), superseded (by what), still open (a pointer to section 3), or no longer needed (marked "the agents' reading" where no word of hers says so). What stays open under an answered or superseded question is named in its own clause "Open remainder".

| Q | Title (short) | Fate |
|---|---|---|
| 1 | Where is "the earliest place" | Answered: the default place is where the original tier 1 and the metadata are joined (D-0549), the first tier 1 when none (D-0550). Open remainder: the default where her rule says nothing (PATHS Q4, after the big line) |
| 2 | The recipe form (form 3) | Still open: section 3, question 3 |
| 3 | Later places as lines or a drawing | Superseded by D-0547 and D-0553: derived places are marked "~" and cannot be chosen (the agents' reading that no tick line is needed for them) |
| 4 | Default ticks for a filter on another column | Still open, after the big line (PATHS Q4) |
| 5 | A place where the entity id is made again | Still open, after the big line (a detail of the dialog; D-0508 asks to detect and document it) |
| 6 | A table no plot reads: ticked like the others | Still open, after the big line; D-0451 answered "Yes" before D-0508 |
| 7 | Which number each ticked line shows | Superseded by D-0545 and D-0546 (the effect is known after Apply). Open remainder: the rows-at-the-place number (after the big line) |
| 8 | A step after a computation over all entities | No longer needed (the agents' reading): the effect is seen after Apply [D-0546]; D-0501 asks for no downstream warnings |
| 9 | After Apply: count where the removed value is still found | Answered: effects measured after Apply and kept in the log [D-0536, D-0537, D-0546] |
| 10 | What the log keeps of a warning | Still open, small; D-0478 says the warnings are in the log; the form of the words is open |
| 11 | Does the log mark how each place was chosen | Still open, small (a reading of version 5, not accepted) |
| 12 | A step cancelled before confirming | Still open, small (a reading, not accepted) |
| 13 | A lineage picker | Still open, after the big line [D-0496: not decided] |
| 14 | Where the picker opens | Still open, later (follows 13) |
| 15 | Original recipe in the Publication part | Answered: the original recipe is in the reproducibility part "original" [D-0490, D-0492]. Open remainder: whether the Publication part also holds it (small) |
| 16 | Where the export shows the original plot | Still open, small (D-0147 decides that it is shown) |
| 17 | The Reshuffle | Still open, after the big line [D-0341: not critical for now] |
| 18 | What opens first | Still open, small (a reading, not accepted) |
| 19 | The words of the stages on screen | Still open, small (a reading, not accepted) |
| 20 | Comparisons on dates | Still open, small (a reading, not accepted) |
| 21 | Tier 2 on a table no plot reads | Still open (a reading, not accepted); her question "why does tier 2 refuse? it is still data wrangling" [D-0514] leans the same way |
| 22 | A look-up table with an entity id: an advice | Answered for the demo: `VirulenceFinder` moves [D-0523]. Open remainder: the general advice of the recipe check (small) |
| 23 | Colours in a lineage | Still open, later |
| 24 | The recipe upload code | Still open, small (a reading, not accepted) |
| 25 | The form of the audit log in the export | Still open, small; the log of the ids is a separate log [D-0576] |
| 26 | Sessions saved before the audit recipe | Session format 5 refuses older files (built, merge `2349ddac`); no further open point known |
| 27 | A look-up join in tier 2 | Still open, after the big line (RECIPES (vi); [D-0562] opens a system for joins that are not metadata) |
| 28 | Places or results; effect measured | Answered: places as decided, the effects measured and registered, what is shown decided later [D-0535, D-0536, D-0545] |
| 29 | Does the audit keep column drops | Still open, after the big line (step kinds stay as D-0322 until she says) |
| 30 | A deployment where your place cannot be written | Superseded by D-0581 (nothing blocks; the folder warning is built, section 6). Open remainder: whether Audit mode is offered where nothing can be written (small) |

The eleven readings of version 5 (10 to 12, 16, 18 to 22, 24, 25; "accept all, or the numbers you refuse") were never answered. They stay the review session's readings, not decisions.

## 6. WHAT IS BUILT, WHAT IS NOT

**Built and merged since 2026-11-23** (merge commits on `dev`, not pushed): the rename of `is_entity_key` to `is_entity_id` (`3b59d97b`, D-0562); the names pass, `ui_label` everywhere (`b0c64e1b`); the three id checks, the completion of ids with the marker `<table>_not_in_original_data`, the required free sentence `meaning`, the log of the ids, the export holding `id_log.yaml` with a README line, and the shipped recipes rewritten data first, with ResFinder reading Not Found, counted as 0 (`1f6cb913`; D-0615, D-0616, D-0617); the red warning in HOME with the button "I have read this" (`c6d56f47`); the audit at the chosen places at tier 1, 2 and 3 through the audit copy, with audited table files in an export made in Audit mode, session format 5 (`2349ddac`); the dialog shows the places along the path and the derived places (merge `b3889404`); a plot that no audit step reaches reads its original table when a step elsewhere cannot run (same merge); the exception: `figshare_triple_join` of `figshare_integration` still starts from its metadata-like table `fg_metadata` (not rewritten).

**Built and merged on 2026-11-23** (merge commits on `dev`):
- The rule of places on the recipe graph, `libs/utils/src/utils/recipe_graph.py` with `libs/utils/tests/test_rule_of_places.py` (merge 1497c2bc): nodes, parents, "below", "at most one chosen place on a path". It is a library; the audit dialog reads places through `app/modules/audit_places.py`.
- A user folder that cannot be written warns and does not stop the start of a session (merge 536998d0, `app/modules/session_manager.py`).
- The dry run of the big move, `assets/scripts/dry_run_big_move.py`, a report only (merge d8bb534e).
- Built earlier: the listing of places, the audit copy, "remove from all the data" as a library step (no screen with ticks), the comparison of two tables.

**Held (her order D-0580, quota):**
- The branch `task/audit-slice1-effects-log` (42d5ae6d): a fix for plot columns, an audit log module, the measure of effects, a callback of the audit run. It is NOT merged and was not used: the audit at the chosen places was built anew (merge `2349ddac`). The measure and the log of the effects (not shown to the user) are therefore not built; its tests name today's places and must be redone on the new graph.
- BLUEPRINT (no build); the Gallery recipes; the two builds of D-0534 (the BLUEPRINT silent error, the plot id unique across recipes) whose reviews are to be redone; every feasibility run until its code exists.

**The pieces to code (status at 2026-11-24):**
- **Piece 2, the id checks in the data check:** built (merge `1f6cb913`). The log directory is a sub-folder of `user_data` (`<user_data>/_id_logs/`; code `app/modules/id_check_run.py`).
- **Piece 4, the completion:** built (merge `1f6cb913`), with the block `completion: {marker, meaning}` (PROVISIONAL form, D-0613).
- **Piece 6, the audit at the chosen places:** built (merge `2349ddac`). Still needed: question 2 (E) for the form of "remove from all the data"; the measure and log of effects (held).
- **Piece 7, the red warning with "I have read this" in HOME, and the export pointing to the log:** built for the log of the ids (merges `c6d56f47`, `1f6cb913`; `id_log.yaml` in the bundle and a README line).
- **The one big move of the shipped recipes** (data first, the entity id declared, the tables moved to the data schemas): built (merge `1f6cb913`), except what the handoff's line "For the owner at the end" lists; the exception: `figshare_triple_join` of `figshare_integration` still starts from `fg_metadata` (not rewritten).
- **Audit views and audit recipe (D-0622, D-0618 to D-0626):** built, merge `80443853` (2026-11-25, not pushed). In Audit mode the T1 and T2 views show the audited tables; an export made in Audit mode writes the audit recipe, which runs on its own; typed values are trimmed (D-0626).
- **The metadata is not an audit place (D-0632):** built, merge `578d69d2`. An audit operation never targets the metadata; the recipe maker may still tidy it in its tier 1.
- **The metadata join rules (D-0633, D-0636, D-0637):** built, merge `578d69d2`, as recipe checks J16, J17 and S10 on every shipped recipe and template. A joined table that brings in the metadata starts from its data table and uses a left join in tier 1. `figshare_integration` declares `metadata_schema`. Open: a metadata that no joined table lists (not decided, D-0637).
- **The lineage view in HOME (D-0629 to D-0631):** built, merge `578d69d2`: the data function `libs/utils/src/utils/lineage_data.py` and the panel "Path of the data" (Audit mode, collapsed; list plus dots, mock-up G, `app/modules/lineage_view.py`). Its words and three tier colours are PROVISIONAL. The Graphviz picture (mock-up H) is not built. Open: LINEAGE-UML-SYNC and the other lineage tasks in the handoff.

## 7. WHERE THE DETAIL IS, AND WHAT TO CHECK

The index at the top of this file holds the status of every study file; this section only points to it. Outside the folder: `.claude/knowledge/demo_deliberate_oddities.md` (the demo's oddities, six rows of "why it is there"); the dry-run report (scratch, `tmp/`; rewrite it with the script); `tmpAI/coordinator/STATE_2026-11-23_evening.md` (scratch: the held list).

**To check (two sources disagree, or an item is not settled; nothing is picked):**
1. **Line 11 of the `demo_abromics` metadata file (two quote marks).** The dry-run report, section 6, says the cell is `""` "read as empty". `demo_deliberate_oddities.md` row 1 says it is not one of the listed marks and "whether it is read as missing was not run". Both are stated here; not run.
2. **Ledger numbers D-0606, D-0607 and D-0608** are tagged in the order of the channel blocks M668, M669 and M670; the lines exist in the ledger (DECIDED, taken by EVE) and the numbers match.
   - **Her "they" in line 2** (D-0608) is read as the two tables `QA_year_types` and `QA_aggregated_no_key`; the review session marked this as its reading.
3. **"Five joins that start from the metadata".** The removed overview said "the four joins rewritten data first"; the dry-run report and the oddities record say five (the four of the main demo recipe plus `demo_join` of `demo_abromics`). This file uses five (dry run, section 3).
4. **Her item "4." in D-0602** (about the key problem of a column name) is not asked again here; what it refers to is not settled.
5. **The effect numbers of version 5 (13 plots, 7 plots, and so on):** they came from runs with places listed by hand; D-0548 says to revise them; they are not used here.
6. **The three id-less lines of `demo_abromics`** (moved here from the decided heap, D-0604): her answer to that line of the dry run was option b (D-0604); that this means the three lines stay in the shipped file is the review session's reading, to confirm.

### WHAT THIS ACTUALISATION COULD NOT DO
1. **Not read in full when written (2026-11-23):** the study files then named; `CAUSE_AND_SOLUTIONS_ZEROS`, `RECIPES_FROM_THE_MODEL_AGREED`, `PATHS_AND_DERIVED_AGREED` and `OVERLAP_AND_POPULATION` were read in the parts the brief named, not in full; a decision may sit in a part not read.
2. **Statuses that were not settled:** `DESIGN_AGREED_AND_QUESTIONS`, and which earlier sections of `CAUSE_AND_SOLUTIONS_ZEROS` and `OVERLAP_AND_POPULATION` can go. The removed files are in git history.
3. **Contradiction left open:** line 11 of the `demo_abromics` metadata (see "to check" 1).
4. **Missing in the sources:** how the effects are shown to the user is decided later (D-0536); whether the exported tier 1 and tier 2 files become audited in Exploration mode; what the meaning of a marked line may hold beyond a free sentence.
5. **Rests only on the review session's readings, and needs her word:** the three lines of `demo_abromics` stay (D-0604); "they" of D-0608 line 2 are the two metadata-only tables; her line 7 holds for both recipes; "the other" of line 5 are the six tables; the readings of her eleven notes (confirmed in one sentence, D-0550); the eleven readings of version 5 (never answered); "no cleaning" extends to the completion (the review session reads: not cleaning); the "decided, not built" status of the export parts comes from the ledger's own "Not built" and the contract's rule 4.
6. **Nothing was run:** every number comes from a named source; the scan's numbers come from its page, checked by another agent.
7. The earlier text is in git (version 5, commit 0e149e31), not carried here.
