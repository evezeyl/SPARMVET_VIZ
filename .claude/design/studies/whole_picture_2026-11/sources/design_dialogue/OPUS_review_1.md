# Opus blind position: her two tests, the refusal of the metadata, the completion in the recipe, the separate log, the updated list of her questions, and the review of RECIPES and PATHS (channel blocks M629 to M634; ledger D-0573 to D-0578), 2026-11-23

**What this is.** My position, written BLIND (I have not opened the Sonnet agent's file), on the owner's answers and orders in the channel blocks "### M629 from sparmvet-viz-cb" to "### M634 from sparmvet-viz-cb" (ledger D-0573 to D-0578, now in the ledger). Reading and reasoning only, NO RUN. No study file is edited. The study files are read in the main tree (dev head 84775d8c). Her words are exact; "the review session's reading" is never treated as hers. "What the code does today" is kept apart from "what has to be built": she wrote "the code is not build yet" [HER WORDS D-0573]. Data agnostic: "the entity", "the result table" ("original data"), "the metadata"; "samples" only for the demo's numbers. Nothing is chosen for her; leans are marked as leans.

**Tags.** [HER WORDS D-n] / [RECIPE FILE] / [RULE FILE] / [CODE READ file:line] / [ESTABLISHED: file, point] / [POLARS SEMANTICS] / [REASONED, not run] / [TODAY] (what the code on dev does) / [TO BUILD] (decided or proposed, not in the code).

---

## FLAGS FIRST (a result changed without a message, a step hidden from the user, or a decision of hers reconsidered)

1. **"Not a zero" against today's count steps.** Her rule: "The marker of "not in original data" is not a zero" [HER WORDS D-0573]. A completed line has empty result cells, and the demo's `QA_AMR_per_sample` counts with `pl.col('gene').count()` [RECIPE FILE], which gives 0 for such a line [POLARS SEMANTICS]. So, once the completion exists, the 4 samples that ResFinder does not list would be counted 0 by the engine itself, unless the recipe says otherwise: the very thing her rule forbids, with no message. The demo's own plot text says "Expect 42 samples: 4 with 0 genes" [RECIPE FILE `plots/qa_amr_genes_per_sample.yaml`]. Section B5.
2. **The refusal of the metadata and the data check that only informs (D-0569).** She decided the data check only informs (option (b)) for "ids of a result file with no row in the metadata" [HER WORDS D-0569: "Choice for data check - b"]. Her new rule refuses "the metadata ... that contains errors or missing data (at the id level only ...)" [HER WORDS D-0573]. If "missing data at the id level" includes an id of the original data that the metadata lacks (her test 2), the new rule REVERSES D-0569 for that case: a point to put to her, not a correction (section B3, question N2).
3. **A refusal at the HOME load gate closes the recipe, and in some deployments the app.** [TODAY] A recipe that fails a check "never reaches `available_data_analysis_recipes`" [CODE READ `app/src/bootloader.py:453-459`]; the Data Import panel works on the open recipe only; with the recipe selector hidden (the pipeline profiles) a refused default recipe is "still fatal at startup" [RULE FILE `rules_data_analysis_recipe_structure.md` section 11a]. So her loop "re-upload and the verification start" [HER WORDS D-0573] has no way in the app for a refused recipe today. Section B3.
4. **`demo_abromics` would be refused as shipped.** Its metadata file holds 3 lines with no usable id (file lines 5, 6, 11) [ESTABLISHED: OVERLAP, D-0570 section]; the recipe removes them in its join's tier 1, after the metadata is read [RECIPE FILE `demo_abromics.yaml:30-31, 44-47`]. Under her rule the metadata itself is refused before that step can run. Her order of D-0569 ("remove the null and empty rows from the metadata") already points to changing the file: a dry-run point (D-0525).
5. **The committed D-0572 section lacks 11 of the replacements both agents signed.** The signature line of `CAUSE_AND_SOLUTIONS_ZEROS.md` reads "OPUS_checks_b6_v1.md, R1 to R26 applied", but R2, R4, R5, R6, R7, R8, R9, R10, R11, R13 and R14 are not in the text (for example line 164 still reads "before the recipe's steps", line 200 "no for the recipe side", line 228 "settled: the marker says "no result"") [RECORD READ, main tree]. A records error, not a result change; most of these lines are rewritten anyway by section A below.
6. **A dummy id cannot be "removed afterwards" from the metadata.** Her flow lets the user add an unknown or false id to the metadata "temporaly ... with dummy fill" and remove it afterwards [HER WORDS D-0573]. If the id is later removed from the METADATA, the original data still holds it, so test 2 fails again; it can only leave through a removal by key (an audit step) or a new data file. [REASONED]

---

## 0. Her words, and two readings to put to her

**Her words** [HER WORDS D-0573, channel block M629]: "We need to fix the metadata - it must not contain errors nor missing data. A rule. The marker of "not in original data" is not a zero ... right now our recipe does not say how to process those cases. Not sure the agent have understood the functionning the sets at correction 1. test inclusions : are all original data id included in metadata ? -> yes no problem / no -> warn and include those present in metadata to original data - with the specific marker "not in original data" 2. second test inclusion are all id in metadata included in original data ? -> yes no problem // no - inform - provide user with those id -> user add those manually to the metadata and re-upload and the verification start : if the user does not know this id or its false it can add it temporaly and fill with dummy fill and say I need to remove those ids afterwards eg. because eg they are wrong." And: "I think we need to refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id) - A user confirm is good because then we know it has read (or took responsability for the completion -> noted in the log)  - yes - can you send again for review ?"

**Reading 1: the direction of each test (a point for her, not a correction).** In each test the written question and the action point in opposite directions:

| | Her written question | What her "no" branch does | Direction of the action | The review session's reading (confirmed by her "yes") |
|---|---|---|---|---|
| Test 1 | "are all original data id included in metadata ?" (is every id of the original data in the metadata?) | "include those present in metadata to original data - with the specific marker "not in original data"" | ids of the METADATA that the original data lacks | "ids of the metadata that are not in the original data": follows the action |
| Test 2 | "are all id in metadata included in original data ?" (is every id of the metadata in the original data?) | "user add those manually to the metadata and re-upload" | ids of the ORIGINAL DATA that the metadata lacks | "ids of the original data that are not in the metadata": follows the action |

The review session read each test by its action, and she confirmed that reading with "yes". The ledger records her written questions next to that reading [D-0573]. Point for her, in one line: "Your test 1 asks whether every id of the original data is in the metadata, and its answer 'no' adds the metadata's ids to the original data; we read test 1 by what it does (ids of the metadata missing from the original data) and test 2 likewise (ids of the original data missing from the metadata). Is that right?" On the demo: test 1 by its action adds 4 lines to ResFinder; test 2 by its action finds nothing (0 ids outside the metadata in every file [ESTABLISHED: OVERLAP section 1]). Read by the written questions, test 1 would find nothing and test 2 would find ResFinder's 4, and each action would meet the other case.

**Reading 2: what "missing data at the id level" covers.** Her rule refuses the metadata with "errors or missing data (at the id level only ...)". Two readings: (r1) a line of the metadata with no id, an empty id, or a wrong id (her earlier "metadata should be clean - all with an id" [HER WORDS D-0572]); (r2) also an id of the original data that the metadata lacks (test 2). Under (r1) test 2 only informs, as D-0569 decided; under (r2) the metadata is refused until the id is added (really, or with a dummy fill), which reverses D-0569 (b) for that case (flag 2). Her test-2 wording "inform ... re-upload and the verification start" fits both. A point for her (question N2).

**Where the committed D-0572 text differs from her words** (her criticism: "Not sure the agent have understood the functionning the sets at correction"):
1. **Control (a)** (an id of the original data with no metadata) says "the data check informs" and keeps "a marker "not in metadata"" as an alternative [RECORD READ `CAUSE_AND_SOLUTIONS_ZEROS.md:218`; `OVERLAP_AND_POPULATION.md:209`]. Her flow: inform with the list; the user adds the ids to the metadata by hand and uploads it again; the verification starts again; an unknown or false id may be added with a dummy fill and a note to remove it afterwards; no marker "not in metadata" in her flow (the review session's reading, confirmed "yes"). The committed text has no correction loop, no re-upload, no dummy fill.
2. **Control (b)** (an id of the metadata with no line in the original data) says "the automatic completion at the first step, said in the documentation and in the alerts". Her words add: warn; the user's CONFIRMATION, noted in the log [D-0573]; once per data batch, kept in the session log [D-0574]; also in the export [D-0575]; in a separate log [D-0576]; the block required on every result table, its meaning required [D-0574]; the recipe never records how many lines were added [D-0574].
3. **Control (c)** (metadata lines with no id) keeps a third note, information only. Her rule: refused [D-0573].
4. **Control (d)** (an id repeated in the metadata) says "a note covers it". Under her rule a repeated id may be an error at the id level: open (question Q9').
5. **The marker's name** is `no_result_in_file`, "no result in file", "data file has no result" in the committed tables. Her name: "not in original data", and it is NOT a zero [D-0573].
6. **The B6 table** shows "42 samples, 4 in the bar at 0" for the completed demo: it assumes the recipe counts the marked lines as 0, which her rule does not allow by default (flag 1).
7. **B6 is called "HER PROPOSAL, not chosen"** and question 1 (where the completion lives) is open in the committed text. Since D-0574 the completion lives in the recipe (the block), required on every result table.
8. **Question 8** ("the marker "not in metadata", or the note only?") is answered by her flow (no marker; manual correction).

---

## A. B6 and the control of the ids, in line with her words (the content proposed for the merged text)

**A1. The rule on the metadata** [HER WORDS D-0573]. The metadata must not contain errors nor missing data at the id level; the metadata that does is REFUSED; true metadata may be missing in other columns, which does not refuse the file. It is the user's responsibility.
- [TODAY] Nothing checks the metadata's ids: the data check builds each table alone and compares no ids [ESTABLISHED: OVERLAP section 2, `data_analysis_recipe_validator.py:485`]; an empty id is read as missing only through the declared null words (`null_values: ["", "-"]` on the demo's id field [RECIPE FILE `input_fields/metadata_schema_input_fields.yaml:4`]); a cell of spaces stays an empty text [CODE READ `declared.py:115-120`].
- [TO BUILD] the check of the metadata's ids and the refusal, with a plain line that names the file, the lines and the ids.

**A2. Test 1: an id of the metadata that the original data lacks** (by its action, reading 1). Warn; the original data is completed with one line per such id, marked "not in original data"; the user CONFIRMS the completion, and the confirmation is noted in the log [D-0573]; once per data batch [D-0574]; the record also goes into the export [D-0575], in a log of its own [D-0576].
- [TO BUILD] the completion, the confirmation, the log.

**A3. Test 2: an id of the original data that the metadata lacks** (by its action). Inform and give the list of ids; the user adds them to the metadata by hand and uploads it again, and the verification starts again; an id the user does not know, or a false one, may be added temporarily with a dummy fill and a note "I need to remove those ids afterwards" [D-0573]. No marker "not in metadata" (the review session's reading, confirmed).
- [TODAY] Data Import replaces the metadata file after the ingestion's own read; it compares no ids [ESTABLISHED: OVERLAP section 2, `data_import_check.py:178-231`].
- [TO BUILD] the id comparison on upload, the list, the loop. Whether the recipe stays open meanwhile (inform) or the metadata is refused until fixed: question N2.

**A4. The completion lives in the recipe** [HER WORDS D-0574: "the recipe required on every result table"; "I would lean also to add this in the recipe"]: a block on each result table that has an entity id (option (i-b) of the committed table), done by the app when it reads the file; the block states what the marked lines mean, and the statement is REQUIRED ("I think we need to force"). The recipe never records how many lines were added ("it does not record directly in the recipe how many were added because it would modify the recipe"); the count and the ids go into the log.
- [TODAY] An unknown key of a schema is refused (S01) [CODE READ `recipe_check.py:390`]; no such block exists.
- [TO BUILD] the block (its key names are not decided), the check that requires it on every result table that declares an entity id, the completion in `ingredient_parts` after `_read_source` [CODE READ `orchestrator.py:282-295`].

**A5. The marker** is called "not in original data" and is not a zero [D-0573]; its form (a column, a value) is open (section B5).

**A6. The record** is in a SEPARATE log, in the session AND in the export [D-0575, D-0576]; the audit log of D-0478 is not touched (section C).

**A7. What she would see on the demo** (`qa_amr_genes_per_sample`: 42 entities; ResFinder 70 lines for 38; 4 without) once built:
- At the opening of a new data batch: a warning "4 ids of the metadata have no line in ResFinder: <ids>. They will be added to ResFinder, marked "not in original data". Confirm?" (words PROVISIONAL); after the confirmation, ResFinder's T1 has 74 lines, 4 marked; its Source view still shows the file's 70 [RULE FILE `ui_implementation_contract.md` section 2: Source is "a source table as read from the file"].
- The plot: depends on the meaning the recipe states (section B5): "nothing found": 4 in the bar at 0, as today, by the recipe's own statement; any other meaning: the 4 apart, never as a silent 0.
- Test 2: nothing on the demo (0 ids outside the metadata); the template `left_join_lesson` has 2 (`ACC0001`, `ACC0002`) [ESTABLISHED: OVERLAP section 1].

---

## B. The open points, each with evidence by reading

### B1. The session key and "once per data batch, as recalled by session ?"

- [TODAY] The session key is `recipe_sha256[:12] + ":" + data_batch_hash[:12]` [CODE READ `app/modules/session_manager.py:10, 305-308`]. The recipe hash covers the entry file and every included file [CODE READ `session_manager.py:280-287`]. The data batch hash is the hash of the per-file hashes of every dataset the recipe names: data schemas, the metadata, additional datasets [CODE READ `session_manager.py:294-299`; `app/modules/orchestrator.py:793-821`]. So **a change of the metadata file changes the batch hash**, and so does a change of any data file. A session lives under `{location_4}/_sessions/{session_key}/` [CODE READ `session_manager.py:266-273, 314-317`].
- Consequences for an acceptance kept in the session:
  - a new data batch (any file, the metadata included) asks again;
  - an edit of the recipe (any of its files) also asks again, since the recipe hash is in the key;
  - a deleted session (`delete_session` [CODE READ `session_manager.py:774`]) asks again;
  - on another machine the sessions folder is that deployment's location 4: it asks again, unless the session is carried by its zip (`export_session_zip`, `import_session_zip` [CODE READ `session_manager.py:647, 662`]).
- [TO BUILD] where the acceptance is stored in the session folder (section C).
- A deployment with no sessions (the pipeline profiles: `session_management_enabled` false [RULE FILE `rules_app_features_flags.md`, flag matrix]) has no place to keep the acceptance: question N5.

### B2. Does the data batch hash change when the metadata file changes?

Yes (B1). [CODE READ]

### B3. Where a refusal of the metadata would sit, and how it lives beside the data check that only informs

- [TODAY] Three places read a recipe's data:
  - The HOME load gate runs the structure check, then the data check; any problem rejects the recipe, which goes to the refused list with its contact; advices never reject and come from the recipe check only [CODE READ `bootloader.py:431-451`]. A rejected recipe is not selectable [CODE READ `bootloader.py:453-459`]. The gate runs again for a recipe whose files changed (`recheck_changed_data_analysis_recipes` [CODE READ `bootloader.py:503-509`]).
  - BLUEPRINT's Validate runs the same checks and only reports [ESTABLISHED: OVERLAP section 2].
  - Data Import checks a candidate file by the ingestion's own read, all files or none [ESTABLISHED: OVERLAP section 2].
- **Three seats for the refusal, with consequences:**
  - (s1) **At the gate** (a problem of the data check): the recipe cannot be opened; the Data Import panel works on the open recipe only, so her loop "re-upload and the verification start" cannot run inside the app; the file must be fixed outside the app; where the selector is hidden (the pipeline profiles), a refused default recipe is fatal at startup, with the cause and the contact [RULE FILE `rules_data_analysis_recipe_structure.md` section 11a].
  - (s2) **In Data Import**: an uploaded metadata with id errors is refused and the old file stays; this is where her loop lives. It does not cover a metadata that is already wrong when the recipe is opened.
  - (s3) **Both, plus a way in for a refused recipe**: the refused list offers the upload of a corrected metadata for that recipe (a new path; to build).
- **Beside D-0569 (only inform):** no contradiction under reading (r1) (empty or wrong ids of the metadata itself are refused; result ids missing from the metadata are informed, D-0569). Under reading (r2) the new rule reverses D-0569 for test 2's case. Question N2.
- **Deployments with no upload panel** (`metadata_ingestion_enabled` false in the static, simple, demo-vetinst and web-demo profiles [RULE FILE `rules_app_features_flags.md`, flag matrix]): the user cannot upload a corrected metadata; the fix is upstream (the pipeline); the refusal shows the contact. Question N4.

### B4. The cases around the two tests

- **A repeated id in the metadata.** [TODAY] Nothing checks uniqueness [ESTABLISHED: RECIPES G13]. A join with the metadata second multiplies the rows of a repeated id [ESTABLISHED: RECIPES G9, G13]. An error at the id level (refused) or a note? Question Q9'.
- **A temporary dummy id.** The app cannot tell a dummy from a real id unless it is marked. Options:
  - a column of the metadata that the app reads (for example "temporary");
  - a note given at upload and kept in the log;
  - nothing (the user's responsibility).

  The dummy entity appears in every result with its dummy metadata values until it is removed, and flag 6 applies to how it can be removed. Should the export warn while dummy ids remain? Question N7.
- **A recipe with no metadata block** (`figshare_integration`: its metadata is a data schema [ESTABLISHED: OVERLAP, D-0569 dry-run list]). Neither test can run, because there is no metadata to compare with. The check must say so, or the recipe must name its metadata (the `metadata_schema` block, or `entity.population` [CODE READ `recipe_check.py:332-348`]). Question N8.
- **A table with no entity id** (a look-up table such as the APEC list): never tested, never completed.
- **A result table that declares no entity id** (the 3 tables of `2_test_data_ST22_dummy`): the required block cannot apply. Her order "Have the recipes declaire entity id" [HER WORDS D-0569] covers the shipped recipes in the dry run.
- **A deployment with no upload panel** when the metadata is refused: B3.
- **The acceptance with no interactivity and no sessions** (`pipeline-static`): no session to keep it, and possibly no one at the screen. Options:
  - a standing acceptance written by the operator in the deployment and recorded in the export's log (then it is no longer once per batch);
  - a confirmation shown at each opening, recorded in the export only;
  - the recipe maker accepts in BLUEPRINT for the recipe (then it is not per batch).

  Question N5.

### B5. The marker

**Its form** (her name, "not in original data", and "a different kind of other "missing value"" [HER WORDS D-0572]): Polars has one null, plus NaN for floats [POLARS SEMANTICS], so the marker must sit beside empty result cells:
- (m1a) a yes/no column whose NAME is the marker, for example `not_in_original_data` (true on an added line, false on a line of the file), with the label "not in original data" through the join's `labels` mapping [CODE READ `libs/utils/src/utils/recipe_spec.yaml:44`];
- (m1b) a text column whose VALUE is the marker, for example a column `origin` holding "not in original data" on an added line and empty on a line of the file.

Her name as written has spaces: legal as a value; as a column name, legal in Polars and YAML but awkward in formulas. The check has no rule for column names, only for plot ids (snake_case, P03) [CODE READ `recipe_check.py:1132`]. After a left join from the metadata, an entity with no line has the marker column empty in both forms: a third state, "no line" [POLARS SEMANTICS].

**What "not a zero" asks of every aggregate** [POLARS SEMANTICS; RECIPE FILE for the demo's steps]:

| Aggregate | What an added line gives today, the cells empty | Compatible with "not a zero"? |
|---|---|---|
| a count of values (`pl.col('gene').count()`, the demo's `QA_AMR_per_sample`) | 0 | no, unless the recipe states "nothing found" |
| a count of rows (`pl.len()`, the demo's ResFinder tier 2) | 1 | no (neither 0 nor missing) |
| a sum | 0 | no, unless stated |
| a mean, minimum, maximum | missing | yes |
| a distinct count | 1 (a missing value counts as one value) | no |

So the engine would make zeros (and ones) by itself. Ways to keep her rule:
- (z1) the required meaning is chosen from a few words the check knows, for example "nothing found" (then counting the added lines as 0 is the recipe's own statement) and "unknown" or "not analysed" (then a step below the table must name the marker before any count, as an advice or a refusal of the check; a match on the text of the steps, which can miss a case);
- (z2) the meaning is free text and every count is the author's responsibility, with the data check telling how many marked lines each aggregate met;
- (z3) neither: she says what she meant.

Question N9.

### B6. The position ("at (first step)")

Her words: "an automatic completion at (first step)" [D-0572], "this might be before T1 a step the app does" [D-0572]. The review session reads this as before the recipe's own tier-1 steps, to confirm [M630 reading]. Before them, the marker means "the file has no line for this id" and the recipe's tier-1 steps see the added lines (ResFinder's stamp `status: pl.lit('Detected')` must then be adapted [RECIPE FILE]). An entity whose every line a tier-1 filter removes becomes absent, not marked: on the demo, 6 entities of `Detailed_summary` (42 ids in the file, 36 after its three filters [ESTABLISHED: RECIPES G12, engine run Opus RR2; RECIPE FILE `Detailed_summary_wrangling.yaml:20, 25, 30`]). Audit steps run after the author's steps of a tier [CODE READ `data_wrangler.py:92`], so a removal written at the end of tier 1 is never undone by the completion. Question Q5'.

### B7. Which metadata

(α) the metadata as read from its file, after the id check of A1: the result table's first place stays a first place after original data (her exception of D-0553), and a step at the metadata's place does not remove an added line. (β) the metadata after its tier 1: a step at the metadata removes the added line, but the result table's place lies below the metadata's place, so choosing both places is refused by her rule "the user chooses at most one place" [HER WORDS D-0553]. With the refusal of A1, (α) reads a metadata that has already passed the check. Question Q6'.

### B8. The join order

With the completion on every result table, a join with the result table first and the metadata second keeps every entity of the metadata: the added lines are in the result table [REASONED from the join semantics; ESTABLISHED: RECIPES G5]. Her direction "the join should not start with the medata or we need a solution we do not have yet" [HER WORDS D-0564] can then be followed without losing an entity. Rule, advice or documentation: question Q7' (it is the recipes file's question (iv)).

---

## C. The separate log (her "yes separate log", D-0576; format, name and entries open)

**What exists today** [TODAY]:
- **On dev**, a session folder holds `assembly.json` and `t3_<timestamp>.json`; the latter holds the audit steps and a `notification_log` list [CODE READ `session_manager.py:483-525`; RULE FILE `ui_implementation_contract.md` section 12d]. The audit log of D-0315 and D-0478 ("date, initials, reason"; always in the bundle beside the audit recipe) is DECIDED and NOT built [RULE FILE `ui_implementation_contract.md` section 7.1].
- **Only on the held branch** `task/audit-slice1-effects-log` (commit 42d5ae6d, "on hold (D-0551)"): `libs/utils/src/utils/audit_log.py`. It writes `audit_log.yaml`, which starts with `format: 1`; an entry is one event (`added` or `removed`) with `date`, `initials`, `reason`, the steps and the measured effects; the module text says "the session's audit folder is not built yet" and calls its keys PROVISIONAL [CODE READ `git show task/audit-slice1-effects-log:libs/utils/src/utils/audit_log.py`, lines 1-30]. Not on dev.

**Options:**

| Option | What it is | Pro | Con |
|---|---|---|---|
| L1 | One file of its own for the ids, beside the audit log, in the session folder and in the export | her "separate"; the audit log's form is untouched (D-0478); each file stays readable by itself | two files to name in the README and the report |
| L2 | One log with entries of several kinds (audit, ids) | one story in time | changes the audit log's file; against her "separate" |
| L3 | The ids record only in the export's README and report, no file | nothing new in the session | the acceptance of a batch is not kept; against D-0574 ("kept in the session log") |

**Recommendation (as a lean): L1**, in the same manner as the held audit log, so that both logs are read the same way:
- one YAML file per session folder (the session is one recipe and one data batch), starting with `format: 1`;
- a reader refuses an unknown format;
- the date and the initials are given by the caller;
- data only;
- the name PROVISIONAL, for example `id_log.yaml`.

**What an entry holds** (one entry per event; keys PROVISIONAL):
- `metadata_refused`: when; the file name and its hash; each problem (the line, the id, why: empty, missing, repeated, as she decides); the old file kept.
- `ids_not_in_metadata` (test 2): the result table, the ids listed, what the user did (re-upload; dummy ids declared, if she wants them marked).
- `completion`, per result table (test 1): the table; the metadata's file hash and the data file's hash; the ids added and their count; the marker; the meaning the recipe states.
- `accepted`: who (initials, as in the audit log), when, the sentence that was shown, the session key it holds for.

**Where it lives:**
- in the session folder, beside the T3 file and the future audit log;
- in the export, beside the audit log (D-0478) as its own file;
- the README says in one line what the file is;
- `report.qmd` carries a short section: per table, the ids added, the marker, the meaning.

The acceptance is once per data batch because the session key changes with the batch (B1). A refusal is recorded in the session of the batch that was refused; when no session exists yet (a refused recipe never opens), it is recorded in the export of the next session, or in a deployment-level log. Question N6.

**The audit log of D-0478 is unchanged:** the id log does not use its file, its keys or its events.

---

## D. The updated list of what she still has to answer (her order M633)

### D(a). The ten questions of the D-0572 section: which her words settle

| # | Question (committed text) | Status now | Her line |
|---|---|---|---|
| 1 | Where the completion lives | SETTLED: a block in the recipe on the result table, done by the app when it reads the file (i-b) | D-0574: "the recipe required on every result table"; "I would lean also to add this in the recipe" |
| 2 | One line in the recipe or none | SETTLED: the block, required on every result table | D-0574 |
| 3 | The meaning required, or the note enough | SETTLED: required | D-0574: "I think we need to force - it makes it transparent, it makes thinking about it" |
| 4 | The marker's form and name | NAME SETTLED ("not in original data", not a zero); FORM open | D-0573 |
| 5 | Before or after the recipe's tier-1 steps | OPEN (her words read as before; to confirm) | D-0572, M630 reading |
| 6 | Which metadata | OPEN | none |
| 7 | The join order | OPEN | none |
| 8 | The marker "not in metadata" or the note | SETTLED: no marker; the user corrects the metadata (or adds a dummy) and uploads again | D-0573 (her flow; the review session's reading, confirmed "yes") |
| 9 | A note for a repeated id | CHANGED: under her refusal rule, refused or a note | D-0573 |
| 10 | The count per target | OPEN, unchanged | none |

### D(b). The open ones, rewritten for the new state

- **Q4'** The marker "not in original data": a yes/no column named after it (`not_in_original_data`), or a text column whose value is "not in original data"?
- **Q5'** Your words "at (first step)": before the recipe's own tier-1 steps (they see and must handle the added lines; an entity whose every line a filter removes is absent, not marked), or after them?
- **Q6'** The completion reads the metadata as read from its file (after the id check), or after the metadata's tier 1?
- **Q7'** With the completion, the result table first keeps every entity: is "the join should not start with the metadata" a rule, an advice or documentation? (= recipes question (iv))
- **Q9'** A repeated id in the metadata: refused like a missing id, or a note?
- **Q10** The count per target: unchanged.

### D(c). New questions her answers created

- **N1** The direction of the two tests (section 0, reading 1): confirm.
- **N2** Test 2 and D-0569: when an id of the original data is not in the metadata, is the metadata refused until the id is added (really or with a dummy), or does the recipe open with the note (D-0569)?
- **N3** Which id errors refuse the metadata: an empty id (null after the null words), a cell of spaces, a repeated id (Q9'); a "false" id cannot be detected by the app.
- **N4** Where the refusal sits: at the opening (the recipe cannot open; in the pipeline profiles the app stops at start with the cause and the contact), in Data Import (an upload is refused, the old file stays), or both with a way in for a refused recipe (B3).
- **N5** Who accepts the completion where there is no session or no one at the screen (`pipeline-static`) (B4).
- **N6** The log: our recommendation L1 and its entries (C).
- **N7** A dummy id: marked or not; a warning in the export while it remains; removed by a removal by key (flag 6).
- **N8** A recipe with no metadata block: the check says the tests cannot run, or the recipe must name its metadata.
- **N9** "Not a zero" and the counts: the meaning chosen from a few words that the check knows (z1), or free text with the data check's counts (z2).

### D(d). The eight questions of the D-0570 section, and Part 1 and Part 2 of its list

| Item | Status | Line |
|---|---|---|
| 1 A never-analysed entity counted as "not detected" | SETTLED: the marker says "not in original data"; the meaning is the recipe maker's | D-0572, D-0573, D-0574 |
| 2 The name of the third class | SETTLED: "not in original data" | D-0573 |
| 3 The app reads the audit record | CHANGED, smaller: not needed for the completion (a removal leaves the entity absent or with no line); only for the line F | D-0574 |
| 4 Where the recipe says what a missing value means | SETTLED: in the required block, per result table | D-0574 |
| 5 The count per target | OPEN | none |
| 6 The threshold in "not detected" | OPEN, low; touched by Q5' (`Detailed_summary`) | none |
| 7 The number, the list or both | SETTLED in substance: both from the completed table; how a table result is shown is D-0487's open key | D-0572 ("That would remove need for 6 anti join"), D-0574 |
| 8 `demo_abromics`'s three id-less lines | SETTLED: the metadata must be clean; the dry run removes them, or the recipe is refused | D-0569, D-0573 |
| Part 1 A (the metadata first, fill in the recipe) | CHANGED: the fill is replaced by the completion and the stated meaning; the metadata-first spelling stays possible (Q7') | D-0573, D-0574 |
| B (count first) | CHANGED: still a pattern; the count table gets the block too | D-0574 |
| B2 (a table of the analysed entities first) | VOID as a form for the zeros; a manifest as the population remains a variant | D-0574 |
| B3 (the files list every analysed entity) | SUPERSEDED by the completion; compatible (a file that already lists every id gets no added line) | D-0574 |
| B4 | VOID | D-0574 |
| B5 | SUPERSEDED: the marker gives the three states | D-0573, D-0574 |
| B6 | DECIDED in form (i-b) | D-0574 |
| C | VOID for the completion; the audit-record reading survives only for F | D-0574 |
| D (no zeros) | CHANGED: becomes a stated meaning ("excluded") | D-0574 |
| E (right or full join) | VOID | D-0574 |
| E2 (anti-join) | VOID | D-0572: "That would remove need for 6 anti join" |
| Part 2 F (information line) | CHANGED: the log and the alerts carry the counts; F as a screen line remains possible | D-0575, D-0576 |
| G (declared meaning) | SETTLED: absorbed by the required meaning of the block | D-0574 |

### D(e). The recommended ORDER to bring them to her, one at a time

Each one names what she would see on the demo.
1. **N1** (the direction of the tests). Demo: test 1 adds 4 lines to ResFinder; test 2 finds nothing.
2. **N2** (test 2: refuse or inform). Demo: nothing; `left_join_lesson`: 2 ids, `ACC0001` and `ACC0002`: refused until added, or opened with the note.
3. **N3 with Q9'** (which id errors refuse). Demo: 42 ids, none empty or repeated: accepted; `demo_abromics`: 3 lines with no id: refused.
4. **N4** (where the refusal sits). Demo in the developer profile: a bad upload is refused in Data Import and the old file stays; a bad shipped metadata takes the recipe off HOME's list with its contact; in `pipeline-static` the app stops at start with the cause and the contact.
5. **N9 with Q4'** (the marker and "not a zero"). Demo: ResFinder's 4 added lines carry the marker. With the meaning "nothing found" the plot keeps 4 samples in the bar at 0, by the recipe's statement. With "unknown", the 4 are shown apart, never as a silent 0.
6. **Q5'** (the position). Demo: the 4 lines exist before ResFinder's tier-1 steps (its "Detected" stamp must change); the 6 entities that `Detailed_summary`'s filters remove are absent, not marked.
7. **Q6'** (which metadata). Demo: a step at the metadata for one of the 4 entities leaves its added line (as read from the file) or removes it (after tier 1; then ResFinder's place lies below the metadata's place).
8. **N5** (the acceptance without a session). Demo in `pipeline-static`: who confirms the 4 added lines.
9. **N6** (the log). Demo: one entry for ResFinder (4 ids, the marker, the meaning, the acceptance), in the session folder and in the export beside the audit log.
10. **N7** (dummy ids). Demo: none; a dummy would appear in plots with dummy metadata values until it is removed.
11. **Q7'** (the join order). Demo: with the result table first and one detected entity removed at ResFinder: 41 samples.
12. **N8** (no metadata block). Demo: none; `figshare_integration`: the tests cannot run.
13. **Q10** (per target).

---

## E. The review of `RECIPES_FROM_THE_MODEL_AGREED.md` and of the 7 questions of `PATHS_AND_DERIVED_AGREED.md` (her order M634)

**How to mark** (history is kept, never deleted [RULE FILE `rules_legacy_management.md`]): a blockquote "> **Update of 2026-11-23 (ledger D-0573 to D-0578):** ..." under each item whose status changed; nothing removed. The file's own questions are labelled (i) to (viii); "her questions (a) to (h)" of the order are read as these eight.

### E1. The half page

| Item | Status | Line |
|---|---|---|
| 1 Join with the metadata in tier 1 | STILL TRUE | D-0510 |
| 2 Two ways of writing a result; "the metadata first, the counts filled with 0 ... a false zero" | CHANGED MEANING: with the required completion a per-entity result can start from the result table and keep every entity; the marked line is not a zero; the false-zero facts stay true for today's recipes | D-0573, D-0574 |
| 3 "A zero cannot tell analysed from not analysed; a removed entity also shows 0" | PARTLY SUPERSEDED: the marker tells a completed entity from a counted one and from a removed one; analysed against not analysed stays unknown (the accepted risk) | D-0572, D-0573 |
| 4 Three kinds of join; rows multiply | STILL TRUE | |
| 5 Nothing checks today (uniqueness, side, block meaning, look-up key, inner join; two recipes declare no id) | STILL TRUE of the code; CHANGED as to what is to be built: the metadata's ids are refused when wrong (D-0573); the recipes declare their ids (D-0569) | D-0569, D-0573 |
| 6 The engine does not run the check | STILL TRUE (question (viii) open) | |
| 7 The five forms tried | STILL TRUE (history); the completion block is a new, decided element of the form, not tried | D-0574 |
| 8 The rename counts | STILL TRUE (counts of that date) | D-0562 |
| "Since the list was written, her words D-0563 to D-0566" | add D-0567 to D-0578 in one dated line | |

### E2. Her eight questions of the file

| Question | Status | Line |
|---|---|---|
| (viii) The engine does not run the check | STILL OPEN; weightier: a refusal of the metadata holds only where the check runs (the opening, BLUEPRINT, Data Import if built) | D-0573 |
| (iii) Must the entity id be declared; where "unique" is judged | CHANGED MEANING, partly SETTLED: the shipped recipes declare their ids (D-0569); the completion block is required on every result table that has an entity id (D-0574), so a result table must declare one to be completed; for the metadata, a repeated id may be an error (N3, Q9'); where uniqueness is judged for the result tables stays open | D-0569, D-0573, D-0574 |
| (iv) "The join should not start with the metadata": rule, advice, documentation | STILL OPEN, narrower: the completion is the "solution we do not have yet" of D-0564, so the data-first join keeps every entity (Q7') | D-0564, D-0574 |
| (ii) The default place for a per-entity result with zeros | CHANGED MEANING: with the result table first, a removal at the result table is complete; the default at the join (D-0549) stays; the "can remain" sentence (PATHS Q6) is needed only for metadata-first joins and for paths through other originals | D-0549, D-0574 |
| (i) A system for joins that are not metadata | STILL OPEN | |
| (vii) An inner look-up join removes rows | STILL OPEN | |
| (vi) A look-up join after tier 1 (question 27) | STILL OPEN | |
| (v) The recipe form | STILL OPEN; one decided element: the completion block on each result table | D-0574 |

### E3. The 19 agreed points

| Point | Status | Line |
|---|---|---|
| G1 The three blocks | STILL TRUE; the completion applies to result tables (data schemas with an entity id), never to look-up tables | D-0574 |
| G2 VirulenceFinder moves | STILL TRUE, not done; after the move it gets the completion block | D-0523, D-0574 |
| G3 Joins in tier 1, source tables only | STILL TRUE | |
| G4 The entity id | STILL TRUE; with D-0569 (declare), D-0573 (the metadata's ids checked and refused), D-0574 (the block needs a declared id) | |
| G5 A result per observation | STILL TRUE | |
| G6 A result per entity with zeros (the metadata first, fill 0, false zero) | SUPERSEDED as the recommended pattern: the fill with 0 is replaced by the completion with the marker and its stated meaning; its facts remain true for today's recipes | D-0573, D-0574 |
| G7 A zero cannot tell analysed from not analysed; "an entity with metadata and no observation exists in the result only when the metadata is the first table" | first half STILL TRUE (the accepted risk); second half SUPERSEDED: with the completion it exists with the result table first | D-0572, D-0574 |
| G8 A removal at a table with no entity id is refused by the engine | STILL TRUE | |
| G9 Three kinds of join | STILL TRUE | |
| G10 The tiers as shared steps; the audit block | STILL TRUE | |
| G11 A table result has no form yet | STILL TRUE of the code; the design is decided (D-0485, D-0487), its key open | D-0485, D-0487 |
| G12 Uniqueness differs between the file and tier 1 | STILL TRUE (a fact) | |
| G13 What nothing checks today | STILL TRUE of the code; the metadata's ids and the overlap are to be built (D-0570, D-0573) | |
| G14 An inner look-up join removes rows | STILL TRUE | |
| G15 The rename | STILL TRUE (decided, not done) | D-0562, D-0567 |
| G16 The engine does not run the check | STILL TRUE | |
| G17 Reading rules and parents | STILL TRUE; a completed result table also reads the metadata (a second parent of its first place: from the metadata's file under (α), from its tier 1 under (β)) | D-0574 |
| G18 The forms as tried | STILL TRUE (history); the completion block not tried | |
| G19 A rule "metadata on the right" would forbid the zeros pattern written with the metadata first | CHANGED MEANING: with the completion the zeros pattern can be written with the result table first, so such a rule forbids only a spelling | D-0574 |

### E4. The demo candidates and the rest of the file

- **Rows that stay as they are:**
  - the rename (YES, decided);
  - the VirulenceFinder move (YES);
  - the entity block (only under some answers);
  - the kind per join step (only under J2);
  - the inner look-ups (only under (vii) (b));
  - the reimport copies;
  - the APEC joins in tier 2;
  - the declared default key;
  - joins of joins.
- **Row that changes:** "the metadata moved off the first place in the 4 joins" no longer needs a solution to be chosen, because the completion is decided. It remains a choice under Q7'.
- **New rows to add (decided):**
  - the completion block, with its stated meaning, on every result table that declares an entity id: on the demo 9 data tables today, 10 after the VirulenceFinder move; only ResFinder receives lines, 4 [ESTABLISHED: OVERLAP section 1];
  - ResFinder's steps that stamp "Detected" and count rows, adapted;
  - the plot `qa_amr_genes_per_sample`, whose text "4 with 0 genes" follows the stated meaning;
  - `demo_abromics`'s metadata without its 3 id-less lines (D-0569, D-0573);
  - the two recipes that declare no id: they declare it (D-0569).
- **"The old recipe study", CHANGED:** the line "result: plot | table stays a direction (D-0487)" should read "a decided design, not built; its key open (D-0485, D-0487)".
- **Facts F1 to F6:** STILL TO RUN, only when she asks. For F6 the expected numbers hold for today's recipe.

### E5. The 7 questions of `PATHS_AND_DERIVED_AGREED.md`

| Question | Status | Line |
|---|---|---|
| Q1 A parent reused in another graph | STILL OPEN; touched: with the completion the metadata feeds every completed result table (a new edge: from its file under (α), from its tier 1 under (β), Q6') | D-0574 |
| Q2 Each T1 from the parent: which place | STILL OPEN | |
| Q3 The recipe form | STILL OPEN; the completion block is a decided part of the form | D-0574 |
| Q4 The default place where the rule says nothing | STILL OPEN | |
| Q5 What "Remove from all the data" writes | STILL OPEN; under (β) the completed result tables lie below the metadata, which adds nested pairs | D-0574 |
| Q6 "Can remain" before Apply | CHANGED MEANING, narrower: with the result table first and the completion, a removal at the result table is complete; the note concerns metadata-first joins and paths through other originals (the 23 virulence genes) | D-0574 |
| Q7 "Remove step"; the side of the metadata; the entity key | "Remove step" STILL OPEN; the side of the metadata: CHANGED, now Q7' (rule, advice or documentation); the entity key: CHANGED, the recipes declare their ids (D-0569) and the block needs a declared id (D-0574) | D-0569, D-0574 |

---

## Runs needed after her choices (each registered before it runs; three points)

1. **The completion with a stated meaning on the demo chain** (after Q4', N9, Q5'). Requirement: the ResFinder file with the 4 added lines and the marker written by hand into a scratch folder; the chain of `qa_amr_genes_per_sample` with the result table first and with the metadata first. Expected:
   - "nothing found": 4 in the bar at 0;
   - "unknown": the 4 apart;
   - `pl.len()` gives 1 and the stamp gives "Detected" unless adapted;
   - a removal at the end of ResFinder's tier 1 gives 41 samples (result table first).

   Independence: a scratch recipe from the demo's schemas, each table rebuilt in its own empty folder, no lineage code.
2. **The id check of the metadata** (after N2, N3). Requirement: scratch metadata files with an empty id, a cell of spaces, a repeated id, and an id missing for a data id. Expected: the reading of each case as she decides (refused or informed), checked on the files with the declared reading. Independence: plain reads of scratch files, no engine.
3. **The session key** (no choice needed; can run when asked). Requirement: "a new batch asks again". Expected: a changed metadata file gives another data batch hash and another session key. Independence: the hash functions on scratch files in an empty folder.

---

## Leans (as leans; nothing chosen)

- N2: (r1), refuse empty or wrong ids of the metadata itself and keep D-0569's information for test 2, unless she wants the loop to block; reason: it keeps both of her remedies of D-0568 and her decision of D-0569.
- N4: (s2) in Data Import plus (s1) at the opening with the contact, and a way in for a refused recipe (s3) where the deployment has Data Import.
- Q4': (m1a), a yes/no column `not_in_original_data` with the label "not in original data".
- N9: (z1), a few meaning words the check knows, so that a zero is always the recipe's statement.
- N6: L1, as section C.
- Q5': before the recipe's tier-1 steps (her words), with the information on filters.
- Q6': (α).
- Q7': an advice (the recipes file's lean (b)).
