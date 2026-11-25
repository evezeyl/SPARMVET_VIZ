# SONNET position 1 (blind): her two tests, B6 and the control of the ids in line with her words, the open points, the log, the updated list of her questions, and the review of `RECIPES_FROM_THE_MODEL_AGREED.md` (blocks M629 to M634; ledger lines D-0573 to D-0578 are being written)

Written without the Opus agent's text. Reading and reasoning only; NO RUN (D-0566). No study file is edited; `WHOLE_PICTURE.md` untouched; no waiting loop; no process left. Data agnostic ("the entity"); cost and effort are no argument. Tags: [HER WORDS M629..M634] / [CODE READ file:line] (what the code DOES TODAY) / [TO BUILD] (what has to be built; the code is not built yet) / [RECIPE FILE] / [RULE FILE] / [ESTABLISHED: file, point] / [REASONED, not run].

---

## 0. Her two tests, exactly as she wrote them, and where the committed text differs

**Her words, exact** [HER WORDS M629]:
"1. test inclusions : are all original data id included in metadata ? -> yes no problem / no -> warn and include those present in metadata to original data - with the specific marker "not in original data"
2. second test inclusion are all id in metadata included in original data ? -> yes no problem // no - inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start : if the user does not know this id or its false it can add it temporaly and fill with dummy fill and say I need to remove those ids afterwards eg. because eg they are wrong."
And her rule: "We need to fix the metadata - it must not contain errors nor missing data. A rule." and, in answer: "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id) - A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)". And: "The marker of "not in original data" is not a zero ... right now our recipe does not say how to process those cases." [HER WORDS M629]

**What I notice in the words themselves (to put to her, because "Not sure the agent have understood the functionning the sets")**
- In test 1 the QUESTION is about the ids of the original data ("are all original data id included in metadata?"), but its ACTION completes the original data with ids "present in metadata". In test 2 the QUESTION is about the ids of the metadata ("are all id in metadata included in original data?"), but its ACTION adds ids to the metadata. So the question of each test and its action name two different sets. The review session paired the actions: test 1 = the ids of the metadata that are not in the original data (complete the data, marked); test 2 = the ids of the original data that are not in the metadata (inform; the user adds them to the metadata). That reading is consistent with the actions and with her earlier words; it is NOT the reading of the question sentences. Both the committed text and the review session use it. It must be confirmed by her in one sentence (new question Q-A below), with the demo: the 4 ids of the metadata that ResFinder lacks are test 1; no id of a result file is missing from the metadata, so test 2 finds nothing.
- Her order in the flow is: the metadata is checked and may be refused (id level only); test 2 sends the user back to the metadata ("re-upload and the verification start"); test 1 completes the data after a confirmation. Which test runs first is not said. [REASONED]

**Where the committed D-0572 text (the section in `CAUSE_AND_SOLUTIONS_ZEROS.md`, the control of the ids (a) to (d) in `OVERLAP_AND_POPULATION.md`) differs from her words**

| Committed text | Her words | Status |
|---|---|---|
| (a) An id in a result file and in no metadata: the data check informs, "tells the user to fix it"; she prefers the metadata corrected; "an alternative, a marker 'not in metadata'" (question 8; run 7 `not_in_metadata`) | Test 2: "inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start", a temporary id with a dummy fill and a note "I need to remove those ids afterwards". NO marker "not in metadata" in her flow (M629 point 3) | the marker, question 8 and run 7 are VOID; the dummy-id loop is missing in the committed text |
| (b) An id in the metadata and in no line of a result file: "an automatic completion", an alert | Test 1: "warn and include ... with the specific marker"; the completion needs the user's confirmation, once per data batch, noted in the log (M629, M630) | the confirmation and the log are missing |
| (c) Metadata lines with no id: "the metadata should be clean", the third note INFORMS | A RULE: the metadata is REFUSED when its ids are missing, empty or wrong (id level only; other columns may have true missing values) | the committed text informs; she refuses |
| The marker is the yes/no column `no_result_in_file` (provisional) | "not in original data"; it "is not a zero" | the name changes; "not a zero" is a new requirement on every aggregate |
| B6 "automatic" in three variants (i-a, i-b, i-c); questions 2 and 3 ask whether a line and a meaning are required | (i-b), the block REQUIRED on every result table that has an entity id, its meaning required (M630) | questions 1, 2, 3 are settled; (i-a), (i-c) are void |
| The B6 table shows "4 in the bar at 0" for the added entities | "The marker is not a zero ... our recipe does not say how to process those cases" | the 0 holds only if the recipe maker writes it; the default count of values gives a 0, which she says the marker is not (section 3.5) |
| (d) An id repeated in the metadata: a note | not in her words | open: is a repeated id an "error at the id level"? |
| Alert: "N lines added ... the app cannot tell" | warn, then confirmation | the alert becomes a confirmation dialog |

---

## 1. What the code does TODAY and what has to be BUILT (kept apart)

| Topic | What the code does today | What has to be built |
|---|---|---|
| A refusal of a metadata with bad ids | The load gate refuses a recipe when its structure check or its data check reports a problem; a refused recipe goes to HOME's refused list with a contact [CODE READ `app/src/bootloader.py:431-451`; RULE FILE `rules_data_analysis_recipe_structure.md` 11a]. The data check builds each table alone after its tier 1 and compares no two tables [CODE READ `app/modules/data_analysis_recipe_validator.py:485-545`]. A number type on an entity id is refused (E03); `entity.population` must name a table with an id (E02) [CODE READ `recipe_check.py:332-348, 445-458`]. Data Import refuses a candidate file the ingestion cannot read, all files or none [CODE READ `app/modules/data_import_check.py`]. | A check of the metadata's ids as READ (before tier 1): missing, empty, wrong; its refusal at the gate, in Data Import, and as a problem line in BLUEPRINT's Validate. Nothing of this exists. |
| The two tests (data ids against metadata ids, both directions) | Nothing compares two tables' ids. | Both tests, their notes, the list of ids shown to the user. |
| The completion | No key, no action, no step appends rows; a schema's tier 1 runs on its own table and a join step there fails [CODE READ `orchestrator.py:282-295`; ESTABLISHED: RECIPES G18]. | The block on the data table, read by the app in `ingredient_parts` after `_read_source` [CODE READ `orchestrator.py:264-267, 282-295`], the marker, the new edge in the graph, the new part of the table's key. |
| The user's confirmation, once per data batch | A session is stored under the key `recipe hash[:12] : data batch hash[:12]` in `{location_4}/_sessions/` [CODE READ `session_manager.py:10, 294-308`]. | A stored acceptance, a dialog, the rule of "once". |
| The log | Under a session: `assembly.json` and `t3_<time>.json` (the second holds a `notification_log`, the alerts). There is no audit log file on `dev`; D-0478's audit log is decided, not built [CODE READ `session_manager.py:324-398, 483-540`; grep `audit_log` in `app/` and `libs/`: nothing]. | A log of its own for the id completion and its writer. |
| The data check informing without refusing | Does not exist: the data check returns problems only, advices come from the recipe check [CODE READ `bootloader.py:431-451`]. | The new channel (decided, D-0569). |

---

## 2. A. B6 and the control of the ids, in line with her words (the state to write into the study files)

1. **The metadata is REFUSED when its ids are missing, empty or wrong** (id level only; another column may hold a true missing value). It is the user's responsibility. A refusal, not an information. [HER WORDS M629]
2. **Test 1** (the ids of the metadata that are not in a result file, in the pairing of the review session, to be confirmed): the user is warned; the data is completed with those ids, each added line marked "not in original data"; the completion needs the user's confirmation, once per data batch, noted in the log. [HER WORDS M629, M630]
3. **Test 2** (the ids of a result file that are not in the metadata): the app informs the user and gives the list; the user adds them to the metadata and uploads it again; the verification starts again; an id the user does not know, or that is false, may be added temporarily with a dummy fill and a note that it must be removed afterwards. There is no marker "not in metadata". [HER WORDS M629]
4. **The marker is called "not in original data" and is not a zero.** The recipe must say how to process those cases; today it does not. [HER WORDS M629]
5. **The completion is a block in the recipe on the data table, option (i-b), REQUIRED on every result table that has an entity id, its meaning required.** The recipe never records how many lines were added (that would modify the recipe). [HER WORDS M630]
6. **The record** (the ids added, the count, the marker, the user's acceptance, and the refusal of the metadata) is in a SEPARATE log, in the session and in the export. [HER WORDS M631, M632]

---

## 3. B. The open points, with evidence

### 3.1 The session key, a deleted session, another machine ("once per data batch, as recalled by session?")
- **The key.** `session_key = data_analysis_recipe_sha256[:12] + ":" + data_batch_hash[:12]` [CODE READ `session_manager.py:306-308`]. So the key holds the recipe too: an edit to the recipe set (any included file) gives a new key even with the same data. "Once per data batch" is once per (recipe, batch) if the acceptance is stored under the session key; once per data batch only if it is stored under the batch hash alone. This is a choice for her (Q-D).
- **Does the batch hash change when the metadata file changes?** Yes. The batch hash is the hash of the per-file hashes of every dataset of the recipe: data schemas, the metadata, the additional datasets [CODE READ `orchestrator.py:793-821` `get_source_files`/`dataset_schemas`; `cache_keys.py:139-152` `dataset_file_hashes`, `batch_hash_of`; `session_manager.py:294-304`]. So a replaced metadata file, or a replaced result file, gives a new key and a new session, and the acceptance is asked again. [CODE READ]
- **A session deleted.** `delete_session` removes the whole folder [CODE READ `session_manager.py:774-778`]: the log and the acceptance go with it; the next opening is a new session and asks again. A session exported before keeps its log (the export zips the whole folder, `export_session_zip`, `:647-650`).
- **Another machine or another user.** Each machine has its own `_sessions` store. The key is made of content hashes, not paths, so the same files give the same key [RULE FILE `ui_implementation_contract.md` 12d]; a different user finds no session and is asked: which fits "the user took responsibility". An imported session zip brings the folder, with the log, under its key (`import_session_zip`, `:662-737`; a key that exists is never written over silently). Whether an imported acceptance of another user counts is open (Q-D).
- **A refusal has no session yet:** a refused metadata never reaches an assembly, so no `assembly.json` exists; `session_dir` creates the folder (`:314-320`) but the scan lists sessions by their `assembly.json` (`:602-640`), so a folder with a log only would not be listed. Where the refusal is logged is open (section 5).

### 3.2 Where a refusal of the metadata sits, and how it differs from the data check that informs
- **The gate** (HOME, at startup and when files change): a problem refuses the recipe: it leaves the selector and shows in the refused list with its reason and contact [RULE FILE 11a]. The id check of the metadata would be a problem here. A refused recipe cannot be opened, so the audit cannot be used to delete an id: the second remedy of D-0568 is not available for a refused metadata; the remedy is to correct the metadata and re-upload (her rule).
- **Data Import:** the same check run on the candidate metadata before anything is written (all files or none): the refusal of a bad file.
- **BLUEPRINT's Validate** reports the same lines and never blocks [RULE FILE 11a].
- **The data check that informs (D-0569)** is the other direction of the control: it never refuses. Under her rules the line is: the metadata's ids are refused; a mismatch between the metadata and a result file informs (test 2) or asks a confirmation (test 1).
- **A deployment with no upload panel** (`metadata_ingestion_enabled` false: `pipeline-static`, `pipeline-exploration-simple`): a refused recipe shows in the refused list with the recipe's or the deployment's contact; the user cannot re-upload there. [RULE FILE `rules_app_features_flags.md` Group C; 11a]
- **The check must read the metadata AS READ.** The existing data check builds each table after its tier 1 (`prepare_ingredient`) [CODE READ `data_analysis_recipe_validator.py:~520`]; a tier-1 step (as the drop of missing ids in `demo_abromics`, `demo_abromics.yaml:44-47`) would hide the error. The check for a refusal reads the table as read by `_read_source`, with the declared `strip` and `null_values`. [REASONED; TO BUILD]
- **What "wrong" can mean** (not defined in her words): missing, empty (after strip and the null words), repeated (an entity table should have one line per entity: an id repeated multiplies a join), a type that is a number (already E03). A pattern ("an id that does not look like the others") would need a declared pattern. Hers (Q-B).

### 3.3 The cases around the two tests
- **An id repeated in the result file:** normal (a long table). **In the metadata:** the committed text proposed a note; under her rule it may be an error at the id level: open.
- **A temporary dummy id:** the user adds an id to the metadata with a dummy fill and a note. The app cannot tell a dummy; the note must be written somewhere the export carries: the log of the id completion (proposal). What "remove afterwards" does is up to the user; the log and the later alerts can list the dummy ids as "added temporarily". Open (Q-F).
- **A recipe with no metadata block** (`figshare_integration`: its metadata is a data schema): the two tests need "the metadata": the `metadata_schema` block, or `entity.population`. Without either the tests cannot run. Open: the recipe is given a metadata block, or the tests name another table.
- **A table with no entity id** (the APEC list): not completed and not tested; the block is required only where an entity id is declared. [HER WORDS M630]
- **A metadata refused where the app has no upload panel:** see 3.2.

### 3.4 The marker
- **Name.** Her words: "not in original data". As a column the identifier must be written without spaces; the project writes slugs in lower case with underscores [CODE READ `recipe_check.py:63` `_SNAKE`, used for ids; the input_fields slugs of the demo are `sample_id`, `predicted_phenotype`]: `not_in_original_data` for the column, "not in original data" for the label in the alerts and the plots. The name is hers.
- **Form.** A yes/no column (true on the added lines, false on the file's lines) beside empty result cells (m1 of the study file), because Polars has one kind of missing value and a second kind must be a column [POLARS SEMANTICS]; a sentinel text is counted as a value.
- **"Not a zero": what it asks of every aggregate.** After the completion a marked line has empty result cells. Then:

| Aggregate (Polars) | What it gives for an entity whose lines are all marked | What "not a zero" asks |
|---|---|---|
| count of values (`gene.count()`) | 0 | a zero, which she says the marker is not: the recipe maps those entities to missing (or to a state) |
| sum | 0 | the same |
| row count (`pl.len()`) | 1 | a line of "no data" counted as one |
| mean, minimum, maximum, standard deviation | missing | already not a zero |
| distinct count | missing counted as a value (1), unless the nulls are dropped first | the recipe decides |
| a stamp (`pl.lit('Detected')`) | the added line is stamped | the demo's ResFinder stamps "Detected", then `ST22_Anchor` and `integration_plot` show it |

[POLARS SEMANTICS; RECIPE FILE `ResFinder_wrangling_tier1.yaml`, `_tier2.yaml`, `QA_AMR_per_sample_tier2.yaml`, `ST22_Anchor_wrangling_tier1.yaml:47`, `integration_plot.yaml:9`] On the demo the plot `qa_amr_genes_per_sample` counts values per entity: the 4 entities would be a 0 unless the recipe maker maps them to "not in original data". The default gives 0; that is the demo recipe's own decision to take (Q-C).
- **What the checks can verify:** the recipe check, that a table with an entity id carries the required block and its meaning; the data check, the number of added lines and their ids (for the log and the alert). That every aggregate handles the marker cannot be verified: a text match at best.

### 3.5 The position (her words: "at (first step)")
Read as before the recipe's own tier-1 steps (P1). With P1 the recipe's own steps see the added lines (so the stamp and the row counts must be adapted), and the audit step at the end of tier 1 runs after the completion [CODE READ `data_wrangler.py:92`, `orchestrator.py:282-295`]. With P2 (after the author's steps) the added lines are hidden from tier 1, which contradicts "processed as a normal recipe". `Detailed_summary` shows the difference (42 ids in the file, 36 after its filters). Her confirmation is still asked.

### 3.6 Which metadata
With her rule, the metadata the completion reads is the metadata that has been checked: the file as read (α). Reading it after its tier 1 (β) would let a tier-1 step clean the ids, which her rule ("it must not contain errors nor missing data") leaves to the user, and puts the result tables below the metadata's place (D-0553). α is reasoned as the fit; hers.

### 3.7 The join order
With the completion required and the metadata clean, a result table holds every id of the metadata. Data first with the metadata second (`left`): a removal at the result table is complete. Metadata first: the entity stays by the metadata after a removal at the result table (a false result, unless the recipe reads the marker). The question remains (a rule, an advice or documentation), now narrower. [ESTABLISHED: CAUSE, B6 table]

---

## 4. C. The separate log

Her words: "maybe better to keep the id adding in a separate log ?" and "yes separate log" [HER WORDS M631, M632]. Only "separate" is settled.

**What exists on `dev`:** the session folder holds `assembly.json` and `t3_<time>.json`; `t3_*.json` carries `notification_log` (the alerts shown), not an audit log; there is no `audit_log` module or file on `dev` (grep in `app/` and `libs/`); the audit log of D-0478 is decided and not built. [CODE READ]

| Option | Pro | Con |
|---|---|---|
| **L1. One file per kind** in the session folder: `id_completion_log.jsonl` now, an audit log later beside it | follows "separate"; each kind has its own entry shape and can change alone; D-0478's audit log is untouched; an export copies the file; the session export already zips the whole folder | more than one file to read and to carry in the export |
| **L2. One log with typed entries** (`session_log.jsonl`: `kind: id_completion`, `kind: audit`, ...) | one place, one time order | joins the id completion to the audit log's format and to its later decisions; a change for one kind touches the rest; against her "separate" |
| **L3. Inside an existing file** (`assembly.json`, the T3 ghost) | no new file | `assembly.json` is rewritten when the data changes (history lost); the T3 ghost is written on apply only; mixes kinds |

**Recommendation (a recommendation):** L1, one append-only file of JSON lines per kind: `id_completion_log.jsonl`. **Each entry holds:** the time; the event (`proposed`, `accepted`, `refused_metadata`, `dummy_ids_noted`); the session key, the recipe hash and the data batch hash; the table; the metadata file's hash; the ids added (or the refused ids and lines); the count; the marker's name; who accepted (the field the deployment gives for the user) and the sentence shown; the user's note; the app version. **Where:** `{location_4}/_sessions/{session_key}/id_completion_log.jsonl`, and in the export bundle in a `logs/` folder beside the audit log, with one line in the README and in `report.qmd` that says the completion exists and where its record is (her rule: what the user sees is what the export contains) [RULE FILE `rules_verification_testing.md` section 9]. **Acceptance:** an `accepted` entry per (table or batch) with the text she accepted. **Refusal:** a `refused_metadata` entry with the ids or lines refused; since a refused recipe has no assembly, the entry is written under the session key computed from the hashes (the folder is created by `session_dir`) — open: or only shown and not logged (Q-E). The audit log of D-0478 is unchanged.

---

## 5. D. The updated list of what she still has to answer

### (a) The ten questions: settled by her words
| # | Question | State | By |
|---|---|---|---|
| 1 | Where the completion lives | SETTLED: (i-b), in the recipe on the data table | M630: "I would lean also to add this in the recipe" |
| 2 | One line in the recipe or none | SETTLED: required on every result table that has an entity id | M630: "the recipe required on every result table" |
| 3 | A required meaning | SETTLED: required ("I think we need to force") | M630 |
| 4 | Marker: form and name | PARTLY: the name "not in original data" settled; the form (a column) and the identifier open | M629 |
| 8 | The marker "not in metadata" | VOID: not in her flow | M629 point 3 (review session's reading, she confirmed with "yes") |
| 10 (demo_abromics note) | the three id-less lines | SETTLED by her rule: a metadata with missing ids is refused | M629 |

### (b) Still open, rewritten for the new state
- **5. When in the table** (P1 or P2): "at (first step)" read as P1; confirm.
- **6. Which metadata** (α or β): reasoned as α under her rule; confirm.
- **7. The join order:** data first only, or metadata first allowed with an advice; narrower now.
- **9. A repeated id in the metadata:** becomes part of "what counts as a wrong id" (Q-B).
- **10 (count per target):** still open.

### (c) New questions her answers created (Q-A to Q-J)
- **Q-A** Which set does each test check? (her question sentences and actions name different sets, section 0).
- **Q-B** What counts as a wrong id in the metadata: missing, empty, repeated, a type, a pattern?
- **Q-C** On the demo: should the 4 entities with no ResFinder line count as 0 genes (not detected) or stay "not in original data" (missing)? She says the marker is not a zero.
- **Q-D** "Once per data batch": stored under the data batch alone, or under the session key (recipe plus batch)? A deleted or moved session: ask again? An acceptance imported from another user: counts or not?
- **Q-E** The log: the form (L1), the name, what the entries hold, whether a refusal is logged and where, whether the user's note and the dummy ids are in it.
- **Q-F** A temporary dummy id: where is the note written, and does the app remind the user to remove it?
- **Q-G** The wording of the refusal and of the confirmation, and where each shows (gate, Data Import, Validate).
- **Q-H** The block's form and key names, whether the marker's name is fixed, and what the required meaning accepts (free text or a short list).
- **Q-I** The order of the checks: the metadata check, then test 2, then test 1 with the confirmation?
- **Q-J** A recipe with no metadata block (`figshare_integration`): add one, or name another table for the tests?
- **Q-K** `demo_abromics`'s file: corrected to 27 lines, or kept as a fixture that shows the refusal (not as a shipped recipe)? [dry run]

### (d) The eight questions of the D-0570 section, and Part 1 / Part 2
- **The eight:** Q1 SETTLED (the meaning is the recipe maker's); Q2 PARTLY SETTLED (name settled; the identifier open); Q3 (audit record) VOID if the completion is in the recipe, open only if C is kept; Q4 SETTLED (the recipe says it, required); Q5 STILL OPEN; Q6 (threshold) STILL OPEN, low; Q7 (number, list, both) PARTLY: the list is the marked lines; how it is shown open; Q8 SETTLED (demo_abromics: the metadata must be clean).
- **Part 1 (A to E2):** A and B are the join-order question now (Q7); **B2 and B4** (a table of the analysed entities) are no longer needed for the zeros; they remain a way to separate "analysed" from "not"; **B3** (the pipeline writes the lines): not forbidden, superseded in function by the completion; **B5** (a column "has a line"): superseded by the marker; **C** (the app completes after the join and labels removals from the audit record): VOID for the zeros, since the completion is in the recipe; **D** (no zeros): not chosen; **E** (a right or full join): void; **E2** (the anti-join): "to avoid" and no longer needed (her words: "That would remove need for 6 anti join").
- **Part 2:** **F** (the information line) still possible as the alert and the export record; **G** (the recipe declares the meaning): SETTLED, it is the required block.
(History marked, not deleted. To confirm with her.)

### (e) The order to bring them to her, one at a time, each with what she would see on the demo
1. **Q-A** the sets of the two tests. Demo: ResFinder lacks 4 of the 42 metadata ids: test 1; no result file id is missing from the metadata: test 2 finds nothing.
2. **Q-B** what counts as a wrong id. Demo: the metadata has 42 distinct non-empty ids and passes; `demo_abromics` shows "3 lines have no id (lines 5, 6, 11)" and is refused.
3. **Q-G and the place of the refusal** (the gate, Data Import, Validate; a deployment with no upload panel). Demo: `demo_abromics` would be missing from the selector with the reason and the contact.
4. **Q-I** the order of the checks.
5. **Q-D** once per data batch: what is stored where. Demo: the dialog "4 lines will be added to ResFinder: <ids>. Confirm?" once; a changed metadata file asks again.
6. **Q-H** the block's form and names, and **question 4** the marker's form and identifier. Demo: one block on ResFinder with the meaning; a column `not_in_original_data`.
7. **Q-C** the meaning of the 4 on the demo (0 or missing). Demo: the plot's bar at 0 holds 4, or the 4 are not drawn.
8. **Question 5** position and **question 6** which metadata.
9. **Question 7** the join order.
10. **Q-E and Q-F** the log, the dummy ids.
11. **Q-J, Q-K**, then the old open ones (the count per target, the threshold, the inner look-up join, question 27, the system for joins).

---

## 6. E. The review of `RECIPES_FROM_THE_MODEL_AGREED.md` against her decisions since (history is marked, never deleted)

Decisions since it was written: D-0562 (rename) to D-0572; the blocks M627, M629 to M634 (ledger D-0573 to D-0578 being written).

### The 19 agreed points
| Point | State | By |
|---|---|---|
| G1 the three blocks | STILL TRUE; CHANGED in weight: the metadata block is the population of the tests and the completion | M629, M630 |
| G2 VirulenceFinder moves | STILL TRUE (decided); a dry-run item | D-0523 |
| G3 joins in tier 1, source tables only | STILL TRUE | D-0344, D-0510 |
| G4 the entity id | CHANGED MEANING: the spec sentence is the one she approved; the id is REQUIRED on every result table for the block; "unique where" still open | D-0567, M630 |
| G5 pattern 1 (result per observation) | STILL TRUE | |
| G6 pattern 2 (zeros, false zero) | CHANGED: the false zero is accepted (D-0569); with the required completion, data first keeps the zeros | D-0569, M630 |
| G7 a zero cannot tell "nothing found" from "not analysed" | CHANGED: the marker "not in original data" distinguishes the ADDED lines; it is not a zero | M629 |
| G8 a removal at a table with no entity id is refused | STILL TRUE | |
| G9 three kinds of join | STILL TRUE | |
| G10 tiers as shared steps; audit block | STILL TRUE | D-0539, D-0541 |
| G11 a table result has no form yet | STILL TRUE | D-0485, D-0487 (decided, not built) |
| G12 uniqueness differs between file and tier 1 | STILL OPEN (question (iii)); the tests are about presence, not uniqueness | |
| G13 what nothing checks | SUPERSEDED IN PART: the metadata's id check, the two tests and the data check in both directions are decided, not built; still nothing checks the uniqueness of a result id, a look-up key, an inner join's row loss | D-0568, M629 |
| G14 an inner look-up join removes rows | STILL TRUE | |
| G15 the rename and its sentence | STILL TRUE; the demo_abromics item changes (Q-K) | D-0567 |
| G16 the check is not run by the engine | STILL TRUE, and more important: the refusal of the metadata must be at the gate | M629 |
| G17 reading rules, parents | CHANGED: the metadata's FILE becomes a parent of every completed table (an edge from the file, not a place) | M630 |
| G18 the forms as tried | STILL TRUE; a new form: the completion block on the data table | M630 |
| G19 a rule "metadata on the right" forbids pattern 2 | CHANGED MEANING: with the completion the data first keeps the zeros; the rule is a question of order only | M630 |

### Her questions (i) to (viii) of that file
| Question | State | By |
|---|---|---|
| (viii) where a rule is enforced (the engine does not run the check) | STILL OPEN, more weighty: the refusal of the metadata is a gate rule | M629 |
| (iii) the entity id declared; where "unique" is judged | PARTLY SETTLED: declared and required (block); where unique is judged STILL OPEN | D-0569, M630 |
| (iv) the side of the metadata | CHANGED MEANING: the join order (Q7) with the completion | D-0564, M630 |
| (ii) the result with zeros, the default place | CHANGED: zeros by the completion; the default place at the join (D-0549) stands; "can remain" (PATHS Q6) narrower | M630 |
| (i) a system for joins that are not metadata | CHANGED: the anti-join is to be avoided and the completion removes the need; the look-up kinds STILL OPEN | D-0570, M627 |
| (vii) an inner look-up join removes rows | STILL OPEN | |
| (vi) look-up join after tier 1 (question 27) | STILL OPEN | |
| (v) the recipe form | CHANGED: a new required block on the schema; the other forms STILL OPEN | M630 |

### The demo candidates
Rename: STILL TRUE. VirulenceFinder move: STILL TRUE. The `entity` block: CHANGED (the population is the metadata block; the block on each result table is required). The metadata off the first place: depends on Q7. A kind on each join step: STILL OPEN. The two inner look-up joins: STILL OPEN. A second table per extra use (the reimport rule): PATHS Q1, STILL OPEN. APEC in tier 2: STILL OPEN. A declared default key: STILL OPEN. NEW: the completion block on 10 demo result tables (all with an entity id except the metadata and APEC), the adapted steps of ResFinder (stamp, row count), `ST22_Anchor` and `integration_plot`, the decision of Q-C, `demo_abromics` (Q-K), the two recipes that declare no entity id. The dry run description STILL TRUE; it gains the log and the block.

### `PATHS_AND_DERIVED_AGREED.md`: its 7 questions
| Question | State |
|---|---|
| Q1 a parent reused | STILL OPEN; CHANGED: the metadata file is a parent of every completed table (an edge from the file) |
| Q2 "each T1 coming from the parent" | STILL OPEN |
| Q3 the recipe form | STILL OPEN; CHANGED: a new required block |
| Q4 the default where her rule is silent | STILL OPEN; the join place default (D-0549) stands |
| Q5 "remove from all the data" | STILL OPEN; each completed table's first place removes the entity (with the data first) |
| Q6 "can remain" before Apply | CHANGED: narrower; remains only for the metadata-first join |
| Q7 earlier points (Remove step, side of the metadata, entity key) | side of the metadata CHANGED (Q7 above); entity key SETTLED (D-0567, D-0569, M630); the Remove step STILL OPEN |

---

## 7. My lean, as a lean
For the questions that remain: P1 (before the recipe's own tier-1 steps), α (the metadata as read), the column `not_in_original_data` with empty cells, the data first in the join with an advice when the metadata is first, one append-only file of JSON lines for the id completion log, the acceptance stored under the session key, and the refusal of the metadata read before tier 1. Nothing is chosen for her.
