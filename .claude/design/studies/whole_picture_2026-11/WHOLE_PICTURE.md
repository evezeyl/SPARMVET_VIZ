# The whole picture: how HOME is meant to work (actualised in place, 2026-11-23)

## 0. Status, and where the truth lives

**What this is.** The one document that says what is decided and how the pieces work together. It is updated in place (her order, D-0605: "making new documents all the time make the decided truth impossible to follow"). It replaces version 5 (2026-11-22), kept in git at commit 0e149e31 with her `@eve` notes; the older text and the old numbered questions are there. Written 2026-11-23. Nothing here is built unless section 6 says so.

**Marks.** [HER WORDS D-nnnn] is copied exactly from the ledger or the channel, her spelling kept. "Reading" is the review session's or an agent's reading of her words, never her decision. "Her view" is something she said with "I think". [REASONED] is reasoning, not run. "Designed" means decided or proposed and not built.

**Four plain words are used instead of the developers' `key`:** a name in the recipe file (developers' word: `YAML key`); a column name; the entity id (the column that identifies the entity); the fingerprint of a stored table (developers' word: `cache key`). The demo's entity is a sample; everywhere else it is "the entity". The bare word still appears inside her quoted words. A number such as D-0508 is a line of the decision ledger, the list of your decisions (`.claude/knowledge/decision_ledger.md`).

### WHERE THE TRUTH LIVES (the index the agents read first; the cleaning of the studies is held, [HER WORDS D-0606]: "as long as the coordinator and agents knows what is what we can held the cleaning ...")

Status words: current / historical / superseded by <file> / "status to settle in the cleaning" (said when the top and the dates of the file do not tell). All 18 files of this folder are named.

| Topic | The ONE file with the current truth | Other files that touch it, and their status |
|---|---|---|
| The big line, the goals | this file, section 1 | `BIG_VIEW.md`: folded into this file; kept until the cleaning (her order, held). `GOALS_REVIEW.md`: current for her goals quoted from D-0528; historical for its dialog and its questions (written 2026-11-22, before D-0535 to D-0550). `GOALS_REVIEW_sonnet.md`: historical (independent review of 2026-11-22). `MATCH_LIST.md`: historical (verdicts on builds of 2026-11-22, before D-0535 and D-0580); status of single rows to settle in the cleaning |
| The recipe design | `RECIPES_FROM_THE_MODEL_AGREED.md` (its "Review of 2026-11-23" at the top says what is still true) | `RECIPE_PROPOSAL_refined.md`: current as the text of the proposal "form 3", NOT confirmed (D-0496). `RECIPE_PROPOSAL_answers.md` and `RECIPE_REDESIGN_REVIEW.md`: background for question B, dated 2026-11-22. `RECIPE_PROPOSAL_dialog_walkthrough.md`: its dialog lines predate D-0535 to D-0550; status to settle in the cleaning |
| The ids, the completion, the log | `CAUSE_AND_SOLUTIONS_ZEROS.md`, the sections dated 2026-11-23 from D-0581 onward and its closing text (D-0593 to D-0599) | `OVERLAP_AND_POPULATION.md`: current for the overlap numbers of the demo and the checks; its earlier parts are marked "changed by" in the text and are historical. The earlier sections of `CAUSE_AND_SOLUTIONS_ZEROS.md` (the catalogue of solutions) are historical where marked "changed by D-0581" or "no longer needed"; which sections can go: status to settle in the cleaning |
| The audit and the places | `PATHS_AND_DERIVED_AGREED.md` (its "Review of 2026-11-23" at the top) | `DESIGN_AGREED_AND_QUESTIONS.md`: superseded in part by the recheck table of `PATHS_AND_DERIVED_AGREED.md`; whether the note at its top is closed: status to settle. `BUILD_ORDER.md`: historical (slices of 2026-11-22, before D-0535); superseded by section 6 of this file (the agents' reading). `T0_OPTION_REVIEW.md`: current for the detail of the T0 option; folded into section 3 |
| The lineage and the graph | `PATHS_AND_DERIVED_AGREED.md` (points G1 to G22) and the code `libs/utils/src/utils/recipe_graph.py` | `DIFFERENCES.md` and `PARTS_TABLES.md`: historical snapshots of 2026-11-22 (the app against her decisions, part by part); later decisions are not in them; status of single rows to settle in the cleaning |
| The export | no study file holds it: the ledger lines D-0490 to D-0492, D-0324, D-0333, D-0478, D-0575 and `ui_implementation_contract.md` section 7.2; this file, section 2.6 | `DIFFERENCES.md`, `PARTS_TABLES.md`: the comparison of 2026-11-22 (historical) |
| The demo's oddities | `.claude/knowledge/demo_deliberate_oddities.md` (outside this folder) | `OVERLAP_AND_POPULATION.md` holds the id counts it cites |
| The dry run of the big move | `assets/scripts/dry_run_big_move.py` (built) and its report `tmp/2026-11-23/dry_run_big_move_report.md` (scratch: `tmp/` is not permanent, D-0419; run the script again to rewrite it) | none |
| What is built | this file, section 6 | `DIFFERENCES.md`, `PARTS_TABLES.md`: built state of 2026-11-22 (historical) |

## 1. The big line, in six sentences

1. **A recipe is a directed graph.** "its more a directional graph with Tx at nodes and branches gives the directions"; "Results (final tables and plots) are leaves no ?" [HER WORDS D-0553]. The user chooses at most one place on a path: "the user chooses at most one place =node (with the exception of the original parents where all can be choosed) then all paths are derived (~) and cannot be choosen. yes R2 rule" [HER WORDS D-0553]. The tiers hold steps shared by several next tables; only the last table cannot hold what several results use [D-0539].
2. **A recipe does not start from the metadata.** "recipes should not start from the metadata" and "original data -> joinleft on metadata - when there is the need for a metadata join" [HER WORDS D-0586; also D-0564, D-0510]. This is her decided rule. It is **not yet true of the shipped recipes**: the dry run finds 5 joined tables that start from the metadata and 2 made from it alone. How the rule is enforced (refused by the check, advised, or documented) is not decided.
3. **Before anything else the ids are made equal.** Every original table and the metadata get the ids they lack, with a marker ("not in original data", and "not in metadata", the review session's name that she accepted, D-0585); the recipe says what a marked line means; nothing blocks, the app warns and writes a log [D-0572 to D-0591; designed, not built].
4. **An audit step** is a filter, a column drop or a removal by the entity id, with a reason [D-0322], written at a place the user chooses (designed, not built), at the end of a tier of a table [D-0535, D-0541]. In one step, at most one chosen place on a path; everything below it is derived and cannot be chosen [D-0553, D-0547].
5. **Everything below a changed place is recalculated.** "we need to ensure that everystep after a change in a place is recalculated - that would otherwise produce errors indeed ..." [HER WORDS D-0560].
6. **The app never cleans data in HOME.** "our app is not supposed to do data cleaning - it is not done for that ..." [HER WORDS D-0594]; "at least not HOME" [HER WORDS D-0595]; "exacly cleaning tools live in LAB or other tools on the user side." [HER WORDS D-0596]. The app makes a problem visible, "if possible" [D-0593].

## 2. How it works: a short status, as the user meets it

```text
original files (read as they are; never changed)
   |  the read: spaces stripped, the missing-value marks of the recipe, the declared type
   v
ids made equal: three checks, completion with two markers      [designed, not built]
   result = the data file with its added ids = "T0". Her words (D-0602): the user cannot choose the place before the completion.
   Whether T0 itself may be a place is her option, not decided (D-0603; section 3)
   |  red warning + "I have read this" button, a log, nothing blocks (designed, not built)
   v
tier 1   clean; the join with the metadata is here: the data table first, left join on the metadata (her rule; not yet true of every shipped recipe)
   v
tier 2   compute
   v
the plot's own steps (tier 3: the table the plot reads)
   v
results: a plot or a table
 
beside it, the AUDIT: one chosen place on a path; every table below is recalculated; the effects are measured after Apply; the log (designed, not built)
beside that, the EXPORT: the results, the audit recipe with its record, the original recipe, the logs
```

### 2.1 The files and the recipe
- A recipe has three blocks of tables: `data_schemas` (results of analysis about the entities), `metadata_schema` (the information about the entities, one table), `additional_datasets_schemas` (look-up tables used in later joins) [D-0512, D-0513]. On the demo, `VirulenceFinder` moves to `data_schemas` ("VirulenceFinder moves", D-0523); an agent may make that change (D-0524); it waits for the one big move of the demo recipes (D-0525).
- The field `is_entity_key` becomes `is_entity_id`, one name for all cases (decided, D-0562; not built: it is done in the one big move, D-0525). The sentence she approved with "yes it seems good" (D-0567; the wording is the review session's): the column that identifies the entity, used to join with the metadata and to find the entity's rows; if its values are unique it also identifies each row of the table (one row per entity), if they repeat the table has several rows per entity (a long table).
- The tiers are not a plain division: tier 1 can hold steps common to several tier 2, and tier 2 steps common to several tier 3; "this is more a process to avoid doing recalculation that can be costly" [HER WORDS D-0539].
- A joined table reads the tier 1 of each ingredient; the join with the metadata is a tier 1 step [D-0510, D-0523; the recipe check already refuses a join step written in tier 2 or tier 3 (code ST05, `libs/utils/src/utils/recipe_check.py:714-715`; the steps allowed in tier 1 only are `polars_join`, the as-of join and the conditional join, `libs/utils/src/utils/action_names.py:66`; read in the code on 2026-11-23, not run in this pass; version 5 part 9 says its test was run then); `PATHS_AND_DERIVED_AGREED.md` G2 gives the edges]. The recipe form with derived tables ("form 3") is not confirmed [D-0496].
- A result is a plot or a table, shown at its last stage; a table result is exported by its name [D-0485, D-0487].
- Unchanged and not touched by this picture: the tiers, the fixed random seed, Exploration, the Gallery.

### 2.2 The ids made equal (designed, not built)
- **The read first.** What the read of the file does is built today: it strips the text, turns the marks the recipe declares into missing, then reads the declared type (`libs/ingestion/src/ingestion/declared.py:115-120`). The recipe handles the meaning of "-" and the trimming [D-0597].
- **The three checks, all shown together, none stops** [D-0581]: (1) ids of a result file that are in no metadata; (2) ids of the metadata that are in no result file; (3) after the completion, the unique ids of all the tables, and of the metadata when it exists, are the union of all the unique ids: "if there many that do not match it means there is a problem in eg. a pipeline" [HER WORDS D-0591]. With a metadata a difference at check 3 means "we have a bug" (her view, D-0590).
- **The completion.** Each original table gets a line for each id it lacks, marked "not in original data"; the metadata gets a line for an id found only in a result file, marked "not in metadata" [D-0572, D-0573, D-0585]. The name "not in original data" is hers (D-0573: the review session's reading that the marker name replaces the working name, which she confirmed with "yes"; her words, test 1 of her first passage of the message: "warn and include those present in metadata to original data - with the specific marker "not in original data"" [HER WORDS D-0609; channel block M629]). The FORM of the marker (a yes/no column, or a word) is open. "not in metadata" is the review session's suggestion that she accepted ("2. yes", D-0585). It is recipe-wide, with or without a join, "as long as a metadata file is attached" [HER WORDS D-0589: "as long as a metadata file is attached then all the original results should received the ids - whether or not the join"]. It "changes or removes nothing from the user's data" [HER WORDS D-0597]. Why: "we have done this mechansism so that the data can always use left joints to join with the metadata - limiting lineages problems" [HER WORDS D-0584].
- **The meaning.** The recipe must state what each marked line means ("A : required meaning", D-0586; "we need to force", D-0574). The marker is not a zero [D-0573]. The marker column is kept [D-0586]. The recipe never records how many lines were added [D-0574].
- **The warning and the log.** "we cannot have blocking actions - only warnings" [HER WORDS D-0581]. With a panel the warning is red and has a button that does not block (she chose "b) that is good", D-0582; the words "I have read this" and "automatic, no user" for the log with no panel are the review session's wording, D-0582 bracket) [D-0581]. The log is simple, separate from the audit log, written automatically in a directory, in the session and in the export, and "the user / person utilizing the results MUST read that log" [HER WORDS D-0582; also D-0575, D-0576, D-0592]. A static deployment needs a person who reads the log: "this must be clear in the documentation" [HER WORDS D-0585].
- **T0: what her words say, and her option.** The lineage starts at the data file with its added ids, and the user cannot choose the place before the completion (D-0602). Whether T0 itself may be a place is her option, not decided (D-0603). D-0602 [HER WORDS]: "I think we need to change the place from original_file to original_file_+all_ids - so the lineage would start here. That is in a way a T0. We cannot allow the user to choose the place - it needs to be done right after the original data import because if we add filters eg by value then it would lead to wrong results." Then D-0603 [HER WORDS]: "yes the T0 is basically the data file with the added ids --- which goes into T1 ---thus allowing to have filters in T1 or T0 in the audit no ? we need to sort out what is practical. to do - it is a suggestion of option not a decision." Two ways in: (a) T0 is a fixed first node and the first place is tier 1; (b) T0 is also a place the user may choose. In both the raw file before the completion is never a place, and the audit runs after the completion. The review's recommendation, a recommendation only, is (a). Detail: section 3, question 1.
- **On the demo** (`OVERLAP_AND_POPULATION.md` section 1): 42 entities in the metadata; `ResFinder` has a line for 38 of them and none for 4 (the 4 entities with 0 genes); every other result file has all 42. So the completion would add 4 lines to `ResFinder` and nothing else (as designed, not built).

### 2.3 A line with no usable id (her question, M669; answer: design, not built, reading of the agents, to confirm)
Her question: "who will this work if the null ids are not cleaned ?" [HER WORDS D-0607].
- **What "usable" means.** The read itself: the text is stripped (when the recipe declares `strip`) and a value is missing when it is one of the marks the recipe declares for that column (`declared.py:115-120`). **A trap:** a cell of only spaces becomes an empty text; it is read as missing only if the empty text is one of the declared marks. A column that declares no mark keeps it as text.
- **Design.** Such a line is not an id. It is not part of the set of unique ids. It adds no line to any other table. The app does not remove or fix it [D-0594]. It stays in its table. The warning and the log list it: the count per table and the lines.
- **In a join that starts from a data table**, such a line finds no metadata, so its metadata columns stay empty (reasoning: a missing id does not match in a join; not run). Another trap [REASONED, not run]: two lines whose id is the same empty text can match each other.
- **In a table that starts from the metadata**, all such lines together make one group with no id (how the table engine groups rows, established in `CAUSE_AND_SOLUTIONS_ZEROS.md`, not run).
- **Who removes it.** The user or the recipe maker, by a visible step in the recipe, as `demo_abromics` does.
- **Facts of the demo.** The metadata of the main demo recipe has no such line (42 distinct ids, none empty; dry run section 6). `demo_abromics` has three, lines 5, 6 and 11 of its metadata file: empty, a dash, two quote marks. They stay in the shipped file (her words are "ok b" and "we need to keep a record somewhere", D-0604; that "b" means "the three lines stay" is the review session's reading) and the recipe's own step `polars_drop_nulls` on the id removes them in its join (`demo_abromics.yaml:46`). Whether the third (two quote marks) is read as missing: the two sources disagree, see "to check" in section 7.
- **The one question this leaves her:** is this reading right: a line with no usable id is not an id, stays where it is, and is listed, never removed by the app? Her words D-0594 and D-0597 point that way; she has not said it for this case.

### 2.4 The audit (designed; the audit of today writes only at the open plot's table)
- **A step** is a filter, a column drop or a removal by the entity id, with a reason [D-0322; whether column drops stay is question 29 of version 5, section 5]. It is written in the audit recipe, a copy; the steps of the original recipe are always kept [HER WORDS D-0541: "audit steps can be written at each tier after the original tier block. The original recipe steps are always kept"]. The first build replaces the audit at the plot's table by steps at each tier [D-0535].
- **The places.** A place is a table at a tier. On the demo the graph has 85 nodes (12 files, 28 tier 1, 28 tier 2, 17 plots) and 58 places; the engine accepts a step at 55 of them (`PATHS_AND_DERIVED_AGREED.md` G1, half page 5). The user chooses at most one place on a path; what is below is derived, marked "~", not chosen [D-0547, D-0553]. Several independent histories (original parents) may each take the step at their first tier 1, "because of independent histories" [D-0547]. When several parents are chosen, the step is written in each tier 1 that comes from the parent; a parent reused in another graph is a gotcha, so both graphs are shown (how: not decided) [D-0555]. What is derived when a node has several parents is not decided (D-0553, under review in `PATHS_AND_DERIVED_AGREED.md`), nor which place "each tier 1 from the parent" means.
- **The default** is where the original tier 1 and the metadata are joined, "because filtering here would ensure me to remove for all other data without removing in the metadata itself" [HER WORDS D-0549]; with no metadata join, the first tier 1 of the lineage [D-0550]. The scope is the user's: "the app cannot decide the scope" [HER WORDS D-0531]; the app informs [D-0543].
- **Recalculation and effects.** Everything below the place is recalculated, no stored table of before is served [D-0560]. The effects are measured after Apply, registered, and kept in the log; what is shown to the user is decided later [D-0536, D-0537, D-0545, D-0546]. The measure at each tick is not made: it costs too much [D-0545].
- **"Remove from all the data"** is the one automatic placement, off until asked; her case is to keep the entity in the quality results only: "he wants to show the poor quality sample for the quality results but remove the bad sample from all other results" [HER WORDS D-0499]. The user may untick a table. The library step is built; the screen with the ticks is not. Its form is question 3 of section 3.
- **Remove step**, one undo control [D-0314]. The audit log (who, when, the reason, the scope, the warnings) is always in the export [D-0478].
- **On the demo** (a run of 2026-11-23 by one of the two design agents, `PATHS_AND_DERIVED_AGREED.md` half page, point 5): one entity removed at each of the 55 places where the engine accepts a step, each variant rebuilt from scratch; the tables whose fingerprint changes are exactly the tables below the place, and the tables whose content changes are among them; a wrong stored table that carries the old fingerprint is never served.

### 2.5 What the app never does
- No cleaning in HOME [D-0593 to D-0596]. Data Import accepts TSV and Parquet [HER WORDS D-0602: "Yes the data import accepts tsv - we keep parquet."]; also "HOME accepts tsv - conversion is done in Excel" [HER WORDS D-0597]. The Excel converter is a Lab tool, in developer only for now [D-0602]. The meaning of "-" and the trimming are the recipe's and the user's job [D-0597].

### 2.6 The export (decided, not built)
- The reproducibility bundle has two parts, "original" and "final_audited" (her "something like that": names not decided), the data stored once and read by both, and it must be "really clear which one is the orginal and which one is the audit_result" [HER WORDS D-0492; also D-0490]. The report has `# Results` before `# Technical` [D-0491]. A table result is exported by its name [D-0487]. The audit log, the audit record and the log of the ids are always in the export [D-0478, D-0575]. The exported tier 1 and tier 2 files are the originals today (version 5, 0.6 point 6): whether they become audited, or are marked as originals, is not decided.

## 3. What is still yours to answer, in one place, in the recommended order

### THREE HEAPS (her order, D-0612: "we need to fix what is already decided"; "small things are mixing with new things")

**(a) DECIDED, to be written and built: no question.**
1. The ids are made equal by a completion, with a marker on every added line. The marker name 'not in original data' is yours (D-0609). The marker 'not in metadata' is the review session's suggestion, which you accepted (D-0585). The form of the marker and how each table treats the marked lines are NOT decided (D-0573, D-0585). (D-0572 to D-0591; not built.)
2. Nothing blocks, only warnings (D-0581).
3. A simple separate log of the ids, written automatically, in the session and in the export (D-0575, D-0576, D-0582, D-0592).
4. A red warning with a button that does not block (D-0581, D-0582) (the review session's reading of your words; one line to confirm).
5. Recipes do not start from the metadata (D-0586); the marker column is kept and the meaning of a marked line is required (D-0586, D-0574).
6. No cleaning in HOME; Data Import accepts TSV and Parquet; the Excel converter stays in the Lab (D-0593 to D-0597, D-0602).
7. The two metadata-only tables (`QA_year_types`, `QA_aggregated_no_key`) and `VirulenceFinder` move to the data schemas (D-0608; D-0523; line 7 of the dry run, D-0610) (the review session's reading of your words; one line to confirm).
8. The entity id is `sample_id` for the six tables of `2_test_data_ST22_dummy` and `figshare_integration`; the APEC list stays a look-up with no entity id (D-0610 and D-0611) (the review session's reading of your words; one line to confirm).
9. The three id-less lines of `demo_abromics` stay in the shipped file (D-0604, the review session's reading of "ok b") (the review session's reading of your words; one line to confirm).
10. The rename to `is_entity_id` (D-0562, D-0567).
11. The audit writes steps at each tier at the places the user chooses; at most one place on a path; everything below is recalculated; effects are measured after Apply and kept in the log (D-0535, D-0536, D-0537, D-0545, D-0546, D-0553, D-0560).
12. The rule of places is built as a library (merge 1497c2bc; section 6) (built and merged on 2026-11-23; no ledger line: your go-ahead is D-0602).

**(b) NOT YET DONE: decided, or waiting only for work.** Pieces 2, 4, 6 and 7 (section 6); the one big move of the demo recipes, after a second dry run with the joins rewritten by hand (D-0525, D-0586); the documentation task, the rules on the ids early in the guidelines (D-0583); the manual test, after the mechanical build and the browser tests (D-0604); the cleaning of the studies (D-0605, held, D-0606).

**(c) NEW OR OPEN: the questions that block, at most five, in this order.** 1. T0, a place or not (question 1). 2. The form of "remove from all the data" (question 2, after T0). 3. The recipe form (question 3, after T0). 4. Line 4 of the dry run, table by table (question 4, after the scan). 5. Where the record goes when the log's folder cannot be written (question 5).

The small questions are kept apart, for after the big line (D-0599): see the list below.

**Answered since version 5, no longer asked:** question A (the completion reads the files as they are): "Question A - is as read." [HER WORDS D-0602]. Where the dialog starts and the effect on each result (old question 28): places as decided, effects measured and registered, shown later [D-0535, D-0536].

**Her view, not a final decision (D-0607):** question C (which tables are one population when there is no metadata), [HER WORDS D-0607]: "1. I think the population is the set of unique ids old in all the tables ( which leads to the problems when there is null id ...) - who will this work if the null ids are not cleaned ?"; the answer to the second half is in 2.3. What remains for the agents to state (their reading, not hers): which tables count are those that declare an entity id; a reference table with none, such as the APEC gene list, stays out (an earlier lean added: or the table named by `entity.population`).

**On hold until question 1 is settled:** questions 2 (E) and 3 (B). Her words [HER WORDS D-0607]: 2 and 3". depends of solutions if T0 is accepted or not - or  alternative solutions - I think."

### Question 1. T0: is "the data file with its added ids" a place you may choose?
- **Her words so far:** D-0602 and D-0603 (section 2.2), "it is a suggestion of option not a decision" and, on her E and B, "depends of solutions if T0 is accepted or not - or  alternative solutions - I think." [D-0607]. She asked for a review of the option (D-0604); it is `T0_OPTION_REVIEW.md` (read and reasoned, nothing run).
- **(a) T0 is a fixed first node, not a place.** The first place is tier 1. On the demo you see 12 first-place lines (7 tables with an empty tier 1, 5 with steps; `T0_OPTION_REVIEW.md` point 4). The rule of places needs no change. A removal by the entity id at tier 1 removes the added line too, as long as the entity id survives tier 1. The review argues that the order (the completion first, audit steps after, in both (a) and (b)) meets your worry about filters by value [REASONED]; you have not confirmed it.
- **(b) T0 is also a place.** 17 lines on the demo (`T0_OPTION_REVIEW.md` point 4: 5 more, one T0 line next to the tier 1 line of each of the 5 tables with tier 1 steps). It lets you act before the author's tier 1 steps: a filter on a column that tier 1 reshapes (on the demo, `phenotype` of `Summary`), or a removal before a tier 1 step that reads many rows (none on the demo). Cost: a step list that runs BEFORE the author's steps (a new list, a new part in the fingerprints, the check of the recipe, the check of the audit copy, the export, the dialog), and the rule "an audit step runs after the author's steps" no longer holds. T0 must then be viewable.
- **(c) No T0 node, or another solution.** The review did not study it. D-0602 starts the lineage at "original_file_+all_ids"; I cannot say more without her words.
- **Two traps in both (a) and (b):** a filter by value with "remove the rows with no value" also removes the added lines of other entities; and the recipe's own tier 1 steps act on the added lines: `ResFinder` stamps "Detected" on every line (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_wrangling_tier1.yaml:2-4`; `T0_OPTION_REVIEW.md` point 3), so the 4 added lines would read "Detected" [REASONED, not run] (a finding outside the review, reported to her). The dry run counts 20 steps that keep only a fixed list of columns and would drop a marker column (section 3, line 4 of the dry run).
- **Also open:** does the Source view show the file as read, or with the added ids? Her words cover neither. (b) forces T0 to be viewable; (a) leaves it open.
- **The review's recommendation (a recommendation, not a decision):** (a), with T0 shown somewhere. Neither: say what you meant.

### Question 2 (E). Which form of "remove from all the data" is offered?
- Three forms were measured on the demo (`PATHS_AND_DERIVED_AGREED.md` point 7, question 5). All three give the same 17 plot tables and leave the entity in none. They differ in the exported tier 1 files: (a) the 27 places in two steps and (b) the 11 first places (the first tier 1 of the 11 originals that declare the entity id; `PATHS_AND_DERIVED_AGREED.md` question 5) clear the entity from every original table; (c) the defaults, one step on 19 places, leave it in 7 original tables (6 with `T1:ResFinder`). Her decided form (tier 1 of every table that holds the entity id, D-0416) and the rule of one place per path cannot both hold in one step (35 pairs one below the other).
- **With T0 [REASONED, from `T0_OPTION_REVIEW.md` point 4 and `PATHS` question 5]:** T0 a place: the "first places" form would have two possible homes, T0 or tier 1; the review lists "write at T0 or at tier 1" as not decided; I cannot say which form it favours. T0 not a place: the three forms stay as measured, since the places begin at tier 1. No T0 node: the same as "not a place" for these forms; I cannot say more.
- Options: the three forms above. Neither: say what you meant.
- On hold until question 1. No lean yet; neither agent chose.

### Question 3 (B). The recipe form
- The proposal "form 3" (blocks in order: original tables, joined tables, derived tables, results) is not confirmed [D-0496]; form 4 is set aside (as the review session reports her words, "we can exclude form 4 and I guess 5": D-0496, the review session's bracket, not her words field). Options as put in version 5 (commit 0e149e31, part 8, question 2): (a) confirm form 3 (with one level of derived tables, or any number); (b) another form (forms 4 and 5 are shown in the proposal, or a form of your own); (c) not yet. They are not rewritten here until T0 is settled. Neither: say what you meant. The tier 3 question and the table results are in `RECIPE_PROPOSAL_refined.md`; the questions that remain after the review of 2026-11-23 are at the top of `RECIPES_FROM_THE_MODEL_AGREED.md`. One element is decided: the completion block on every result table, with its meaning required [D-0574].
- **With T0 [REASONED]:** T0 a place: the recipe format needs a new list or block of steps that runs before the author's steps (`T0_OPTION_REVIEW.md` point 4), which form 3 does not have. T0 not a place or no T0 node: nothing is added for the form. Whether the choice between form 3 and another form depends on T0, the three files do not say, and I cannot say.
- On hold until question 1.

### Question 4. Line 4 of the dry run of the big move: the 20 steps that keep a fixed list of columns
The dry run changes nothing; it lists what each change would do (`tmp/2026-11-23/dry_run_big_move_report.md`; numbers are the report's). Lines 1, 2, 3 and 5 to 8 are answered; only line 4 is still yours. The answered lines:
- **Line 1, answered.** Her words are "ok b" and "we need to keep a record somewhere for us of those particularities in the demo files" (D-0604); that "b" means that the three id-less lines of `demo_abromics` stay in the shipped file, as a lesson, is the review session's reading; the maintainers' record is `demo_deliberate_oddities.md`.
- **Line 2, answered.** Two joined tables are made from the metadata alone (`QA_year_types`, `QA_aggregated_no_key`). [HER WORDS D-0608]: "2. They break no rule but as there is no real metadata nor join they must move in the data_schema." Reading of the review session, not her words (D-0608 bracket): "they" are these two tables, and they move to the data schemas, in the one big move. Still to examine by reading: how a table made from the metadata file alone is written in `data_schemas` (a data schema that reads that data file, as `Summary` and `Summary_quality` share one), what happens to their tier 1 and tier 2 steps and to the three plots that read them, and what the entity id and the completion mean for them.
- **Line 3, answered:** "3. ok." [HER WORDS D-0608]. Five joined tables start from the metadata (four of the main demo recipe: `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; and `demo_join` of `demo_abromics`). The dry run's plan (not her words; the review session's reading of D-0608): they are rewritten by hand, data first, and shown in a second dry run; the rule behind it is hers (D-0586).
- **Line 5, answered** (D-0610 and D-0611). [HER WORDS D-0610]: "for the other yes is sample_id"; the review session reads "the other" as the six tables of `2_test_data_ST22_dummy` and `figshare_integration`. [HER WORDS D-0611]: "line 5 Virulence_genes_APEC.tsv is the lookup table so it stays in additional data - i just verified its confirmed." So `APEC_STEC_virulence_genes` stays under the additional datasets, with no entity id and outside the completion.
- **Line 6, answered: postponed.** The Gallery examples: "this can be postponed to later" [HER WORDS D-0610].
- **Line 7, answered** [HER WORDS D-0610]: "correct VirulenceFinder should move into data_schemas - because the additional_datasets_schemas are for done for example lookups, databases (not the ones conserning our results)". Her words name the table `VirulenceFinder`, not the recipe; the review session reads them for both recipes (`1_test_data_ST22_dummy` and `1_Abromics_general_pipeline`); D-0523 and D-0524 already covered the first. Her definition for the specification and the guidelines: `additional_datasets_schemas` holds look-ups and databases, not results about the entities.
- **Line 8, answered:** "Line 8 ok" [HER WORDS D-0610].
- Mechanical, no decision: the names pass (524 changes) and the rename to `is_entity_id` (225 lines).

**Line 4, still yours.** 20 steps keep only a fixed list of columns and would drop the marker column (3 first in their stage, 10 last, 3 elsewhere or alone, 4 group-by; the dry run's counts). [HER WORDS D-0608]: "4. We need to know data by data - the best is to fix as early as possible so we need to start by the original_data - do all the recipes with those tables have the metadata as left join in T1 ?" Reading of the review session, not her words: a table-by-table list of the facts, with the marker problem handled at the original data table, as early as possible. The two ways of D-0587 stay as the two options for each table: "the fixed column list will need to be increased by the column that keeps the markers - or the missing data processed before and T1 and the column that keeps the markers explicitely dropped".
- **The scan's answer to her question** (read only, fact-checked by another agent; the table-by-table page is `tmp/2026-11-23/scan_metadata_joins_and_fixed_lists.md`): not all are left joins: the recipe `2_test_data_ST22_dummy` brings the metadata in by a join that keeps only the rows found on both sides. Of the 20 steps, 3 sit in original data tables: `MLST`, `VirulenceFinder`, and `Genes` of a test recipe (`retest_bad_select_column.yaml`).

### Question 5. Where does the record go when the log's folder cannot be written?
- Today a folder that cannot be written warns and does not stop the start (section 6). A static deployment could lose its only record [D-0581, D-0585]. The agents' proposal, not decided (`CAUSE_AND_SOLUTIONS_ZEROS.md`, closing text (b) 3): the record goes into the export and the console, and the red warning says that the log could not be written. Neither: say what you meant.

### After the big line (titles only; the agents' lean is PROVISIONAL meanwhile)
- A parent reused in another graph: what the app shows (PATHS Q1); which place is "each tier 1 from the parent" (Q2); how the recipe states the default place (Q3); the default where her rule says nothing (Q4); whether the app says before Apply that the entity can remain below (Q6).
- A look-up join after tier 1 (version 5 question 27); a system for joins that are not metadata [D-0562]; an inner look-up join that removes rows; the engine does not run the recipe check (a gap or by design).
- A recipe whose only table is the metadata is registered as data: her view [D-0588], a documentation guideline; whether it becomes a rule of the format.
- The completion: the block's form and names, its position (before the recipe's tier 1 steps is the lean), the marker's form and the words of the meaning, the log's directory and name, how often the button is asked, where the red warning shows, a repeated id, a dummy id, how "data first" is enforced (check, advice, documentation), the count per target, the threshold, the converter text of the rules file.
- Column drops in the audit; the Reshuffle; sessions saved before the audit recipe; the lineage picker and where it opens; the export (the original picture, the original recipe in the Publication part); the words and defaults on screen; the audit log's details; tables no plot reads and their tiers; the recipe upload code.
- The eleven readings of version 5 ("accept all", never answered): they stay readings (section 5).

## 4. YOUR NOTES (@eve) AND WHAT BECAME OF EACH

Version 5 had **11** `@eve` markers (`git show 0e149e31:.claude/design/studies/whole_picture_2026-11/WHOLE_PICTURE.md | grep -c "@eve"` gives 11 lines). They are the notes N1 to N11 of the ledger, D-0538 to D-0548; her answers D-0549 and D-0550 follow. The review session read each note and she confirmed: "What I read in your comments - was correct" [HER WORDS D-0550]. Line numbers are those of version 5.

| N | Line | Her note (exact) | What became of it |
|---|---|---|---|
| 1 | 22 | "@eve : yes" (an observation is a row of a table) | Decided D-0538 |
| 2 | 23 | "the tiers division is not that simple because it depends but we have some rulbut that can be seen as such in a way. Eg t2 can be a place where we can have common steps for different t3 . and t1 can have common steps for differents t2, only t3 cannot hold things that are used by different results ... this is more a process to avoid doing recalculation that can be costly and allow branching to a next step that will be unique to resutls" | Decided D-0539; section 1 sentence 1 |
| 3 | 24 | "must correspond to the pass of data to different tiers used ----to the results back forth back -" | Decided D-0540; the lineage is the graph (section 1) |
| 4 | 25 | "yes audit steps can be written at each tier after the original tier block. The original recipe steps are always kept" | Decided D-0541; section 2.4 |
| 5 | 26 | "yes correct" (the audit recipe as defined) | Decided D-0542 |
| 6 | 46 | "we have to try to inform the user so it can make wrong decisions. But we cant prevent the user to make wrong decisions if he really wants. Our job is to try to give as clear information as possible - so the user has elements it needs to be able to make a good decision (if it does we have informed him)." | Decided D-0543: the app informs and cannot prevent (reading: "wrong" in the first sentence is a typo for "good", a note of the review session) |
| 7 | 53 | "I do not agree : we deliver a tool that allow he the goals of reliability - correct science, transparency, reproducibility, information providing - the user uses the tool - it is not our role to decide its a bad choice - we provide good tools - the user choice its own," | Decided D-0544: the sentence of version 5 that said her goals pull against each other is deleted (reading confirmed by her); it is not in this file |
| 8 | 77 | "I think to show the effect the steps after needs to be applied because all the steps after the place of change need to be recalculated - you cannot see effect if you do not recalculate. Recalculating each trial can be too costly - [...] I do not see how effect could be calculated without recomputation of all the steps after the change." | Decided D-0545: the effect is known after Apply, in the log; before confirming only the structure; section 2.4 |
| 9 | 78 | "again after apply." | Decided D-0546 |
| 10 | 81 (and the unmarked paragraphs of her note at lines 83 to 92) | "here I think is what what goes wrong: the user can only chose where to write the step in one corect scope - all the steps after are the following history. and are derived." [...] "All the derived steps must get a "~" [...]" (the whole text is in D-0547) | Decided D-0547, then D-0553 (one place per path; originals may all be chosen); the "~" mark and the history shown on the step are in section 2.4. Still open under it: how the graphs are shown (D-0555) |
| 11 | 122 | "I think its because the steps were added in T3 and not in the correct place - this needs to be revised." | Decided D-0548: to be revised; the first build writes at each tier (D-0535); the retest under her scope is in `PATHS_AND_DERIVED_AGREED.md` (half page 5 and 6); the effect numbers of version 5 are no longer used |

## 5. THE QUESTIONS OF THE EARLIER VERSION AND THEIR FATE

Version 5 had **30** numbered questions. One row each. Each question has ONE fate: answered (the ledger line), superseded (by what), still open (a pointer to section 3), or no longer needed (marked "the agents' reading" where no word of hers says so). What stays open under an answered or superseded question is named in its own clause "Open remainder".

| Q | Title (short) | Fate |
|---|---|---|
| 1 | Where is "the earliest place" | Answered: the default place is where the original tier 1 and the metadata are joined (D-0549), the first tier 1 when none (D-0550). Open remainder: the default where her rule says nothing (PATHS Q4, after the big line) |
| 2 | The recipe form (form 3) | Still open: section 3, question 3 (on hold for T0) |
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
| 17 | The Reshuffle | Still open, after the big line [D-0341: "not critical for now"] |
| 18 | What opens first | Still open, small (a reading, not accepted) |
| 19 | The words of the stages on screen | Still open, small (a reading, not accepted) |
| 20 | Comparisons on dates | Still open, small (a reading, not accepted) |
| 21 | Tier 2 on a table no plot reads | Still open (a reading, not accepted); her words "Why Tier 2 refuses ? its still data wrangling" [D-0514] lean the same way |
| 22 | A look-up table with an entity id: an advice | Answered for the demo: `VirulenceFinder` moves [D-0523]. Open remainder: the general advice of the recipe check (small) |
| 23 | Colours in a lineage | Still open, later |
| 24 | The recipe upload code | Still open, small (a reading, not accepted) |
| 25 | The form of the audit log in the export | Still open, small; the log of the ids is a separate log [D-0576] |
| 26 | Sessions saved before the audit recipe | Still open: needed before the audit steps move to the audit recipe |
| 27 | A look-up join in tier 2 | Still open, after the big line (RECIPES (vi); [D-0562] opens a system for joins that are not metadata) |
| 28 | Places or results; effect measured | Answered: places as decided, the effects measured and registered, what is shown decided later [D-0535, D-0536, D-0545] |
| 29 | Does the audit keep column drops | Still open, after the big line (step kinds stay as D-0322 until she says) |
| 30 | A deployment where your place cannot be written | Superseded by D-0581 (nothing blocks; the folder warning is built, section 6). Open remainder: whether Audit mode is offered where nothing can be written (small) |

The eleven readings of version 5 (10 to 12, 16, 18 to 22, 24, 25; "accept all, or the numbers you refuse") were never answered. They stay the review session's readings, not decisions.

## 6. WHAT IS BUILT, WHAT IS NOT

**Built and merged on 2026-11-23** (merge commits on `dev`):
- The rule of places on the recipe graph, `libs/utils/src/utils/recipe_graph.py` with `libs/utils/tests/test_rule_of_places.py` (merge 1497c2bc): nodes, parents, "below", "at most one chosen place on a path". It is a library; no screen calls it.
- A user folder that cannot be written warns and does not stop the start of a session (merge 536998d0, `app/modules/session_manager.py`).
- The dry run of the big move, `assets/scripts/dry_run_big_move.py`, a report only (merge d8bb534e).
- Built earlier and not reached by a screen: the listing of places, the audit copy, "remove from all the data" as a library step, the comparison of two tables.

**Held (her order D-0580, quota):**
- The audit slice 1 branch `task/audit-slice1-effects-log` (42d5ae6d): a fix for plot columns, an audit log module, the measure of effects, a callback of the audit run; not merged; its tests name today's places and must be redone on the new graph; it becomes piece 6.
- BLUEPRINT (no build); the Gallery recipes; the two builds of D-0534 (the BLUEPRINT silent error, the plot id unique across recipes) whose reviews are to be redone; every feasibility run until its code exists; the cleaning of old worktrees and scratch; the cleaning of the studies (her order, M668).

**The pieces to code next** (`BIG_VIEW.md` section 5):
- **Piece 2, the id checks in the data check:** the three checks, the numbers per table, the unmatched ids; a warning, never a refusal; the log written automatically; no completion yet. Needs from her: where the log directory is (open: you decide; the agents' lean only: a sub-folder of `user_data`).
- **Piece 4, the completion:** the block in the recipe, the two markers, the required meaning, the third check as a test. Needs: question A (answered, "as read") and C (her view, not a final decision, D-0607; the agents state which tables count); the block's names (open: you decide; the agents' lean only: a block the app reads); after pieces 1 and 2.
- **Piece 6, the audit at the chosen places:** the held branch continued on the new graph. Needs: question 2 (E), and question 1 (T0) for the places; BIG_VIEW also named her "done" on her notes: her notes are committed as she left them (D-0605, points 1 and 2 accepted).
- **Piece 7, the red warning with "I have read this" in HOME, and the export pointing to the log:** after piece 2. Needs: where the warning shows (open: you decide; the agents' lean only).

## 7. WHERE THE DETAIL IS, AND WHAT TO CHECK

The index at the top of this file holds the status of every study file; this section only points to it. `BIG_VIEW.md` and `T0_OPTION_REVIEW.md` are folded into this document and are kept only until the cleaning of the studies (her order, held). Outside the folder: `.claude/knowledge/demo_deliberate_oddities.md` (the demo's oddities, six rows of "why it is there"); the dry-run report (scratch, `tmp/`; rewrite it with the script); `tmpAI/coordinator/STATE_2026-11-23_evening.md` (scratch: the held list).

**To check (two sources disagree, or an item is not settled; nothing is picked):**
1. **Line 11 of the `demo_abromics` metadata file (two quote marks).** The dry-run report, section 6, says the cell is `""` "read as empty". `demo_deliberate_oddities.md` row 1 says it is not one of the listed marks and "whether it is read as missing was not run". Both are stated here; not run.
2. **Ledger numbers D-0606, D-0607 and D-0608.** Her words of the channel blocks M668, M669 and M670 are tagged D-0606, D-0607 and D-0608 in the order of the blocks; the lines now exist in the ledger (D-0606, D-0607, D-0608, DECIDED, taken by EVE) and the numbers match the order of the blocks.
   - **Her "they" in line 2** (D-0608) is read as the two tables `QA_year_types` and `QA_aggregated_no_key`; the review session marked this as its reading.
3. **"Five joins that start from the metadata".** `BIG_VIEW.md` piece 5 says "the four joins rewritten data first"; the dry-run report and the oddities record say five (the four of the main demo recipe plus `demo_join` of `demo_abromics`). This file uses five (dry run, section 3).
4. **Her "4."** in D-0602 ("4. key here is column name I think we have again the key problem") is not asked again here; what it refers to is not settled.
5. **The effect numbers of version 5 (13 plots, 7 plots, and so on):** they came from runs with places listed by hand; D-0548 says to revise them; they are not used here.

### WHAT THIS ACTUALISATION COULD NOT DO
1. **Not read in full:** `DIFFERENCES`, `PARTS_TABLES`, `BUILD_ORDER`, both `GOALS_REVIEW` files, `MATCH_LIST`, the three `RECIPE_PROPOSAL` files, `RECIPE_REDESIGN_REVIEW` and `DESIGN_AGREED_AND_QUESTIONS` (tops and dates only). `CAUSE_AND_SOLUTIONS_ZEROS`, `RECIPES_FROM_THE_MODEL_AGREED`, `PATHS_AND_DERIVED_AGREED` and `OVERLAP_AND_POPULATION` were read in the parts the brief named, not in full; a decision may sit in a part I did not read.
2. **Statuses in the table at the top that I could not settle:** `MATCH_LIST`, `DIFFERENCES`, `PARTS_TABLES`, `DESIGN_AGREED_AND_QUESTIONS`, `RECIPE_PROPOSAL_dialog_walkthrough`, and which earlier sections of `CAUSE_AND_SOLUTIONS_ZEROS` and `OVERLAP_AND_POPULATION` can go. They say "status to settle in the cleaning".
3. **Contradiction left open:** line 11 of the `demo_abromics` metadata (see "to check" 1). The count of joins that start from the metadata is four in `BIG_VIEW.md` and five elsewhere (explained, not a conflict).
4. **Missing in the sources:** the option "no T0 node" was not studied; how the effects are shown to the user is decided later (D-0536); whether the exported tier 1 and tier 2 files become audited; where the record goes when the log's folder cannot be written (a proposal only); what the meaning of a marked line may hold.
5. **Rests only on the review session's readings, and needs her word:** "b" of D-0604 means the three lines stay; "they" of D-0608 line 2 are the two metadata-only tables; her line 7 holds for both recipes; "the other" of line 5 are the six tables; the readings of her eleven notes (confirmed in one sentence, D-0550); the eleven readings of version 5 (never answered); "no cleaning" extends to the completion (the review session reads: not cleaning); the statuses "decided, not built" of the export come from the ledger's own "Not built".
6. **Ledger numbers D-0610 to D-0612** are given by the order of the channel blocks; those lines were not in the ledger when I wrote; the words of D-0610 and D-0611 are quoted from the channel blocks.
7. **Nothing was run:** every number comes from a named source; the scan's numbers come from its page, checked by another agent, not by me.
8. The file is shorter than the length asked, because its lines are long; the earlier text is in git (version 5, commit 0e149e31), not carried here.
