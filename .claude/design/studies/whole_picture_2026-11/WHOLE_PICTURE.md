# The whole picture: how HOME is meant to work, where the code differs, what stays yours (2026-11-22)

**State of this document: complete (sections 0 to 7). Section 2's full tables are in `PARTS_TABLES.md`, same folder. A study, not a decision: nothing is built from it before you answer (D-0507). Written by an Opus agent for the coordinator, 2026-11-22.**

Your order of 2026-11-22 (ledger D-0507): "I think we should maybe use a good thinking model to have the abiity to see the whole picture on how it should work - and then build - because right now the old things that exist are taken again because they are not build and this mixes with the decisions of what should happen."

---

## 0. How to read this document, and flags first

**How to read it (five lines).**
1. Sections 0 and 1 can be read alone, in about ten minutes: the flags, then how the app is meant to work, told on the demo recipe.
2. Section 2 sums up each part; its full tables are in `PARTS_TABLES.md` (same folder). Section 3 lists every old or contradicting behaviour; section 4 where your decisions meet; section 5 your questions, one at a time; section 6 a build order; section 7 what I did not check.
3. Your words are between quotation marks, with their ledger number. A "reading" is the review session's or the coordinator's, not yours. "My recommendation" is mine. Cost and build time are not used as arguments.
4. The general words are "entity" and "entity key" (D-0512); on the demo the entity is a sample and the key is `sample_id`.
5. Evidence: [read by me] = I read the code; [collected] = from the files collected today; "run" = a run on the demo recipe, with the engine and the real data.

**Flags first.**
1. **The audit can write a step only at the plot's own table (T3)**, and the screen says so: "Audit steps apply to the plot's table (T3) for now." You decided: "We had said we can send at each tier - so we need to send the correct tier" (D-0507). Every decision about places (tick lines, the earliest place, "remove from all the data") has no screen yet; the code for them is in the library and only tests call it. (Section 3.1, 3.2.)
2. **"The earliest place" has two readings, and your words support both**: "the earliest place of each branch - which is the original data basically" (D-0501) and "the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged" (D-0509). They give different results. Run on the demo: if the original tables are ticked from `mlst_bar`, the sample stays in 3 quality plots with its `source`, `year` and `country` **emptied** (the picture of `miaou` changes); if the tables that join the metadata are ticked, nothing is emptied and your case of D-0499 works as you described it. (Section 4.1, question 1.)
3. **A sentence about a table where no step is written cannot be read reliably from the recipe.** Two reviews proved such sentences false on the demo; only a run can measure what happens there. The library's lists "may stay", "may differ" and "stays by your choice" were all false alarms on the demo and say the opposite of D-0501 ("no per table warnings about downstream effects"); they are code a builder would take again. (Section 3.3.)
4. **Three different forms of one audit step exist in the code**, and the decided one, the audit recipe of D-0102 and D-0332, is the one HOME does not use. The export writes an older fork of a join instead, and holds no original recipe ("1. yes must.", D-0389), no audit log ("not optional anymore", D-0478) and no audit record (D-0333). (Section 3.8, 3.13.)
5. **The exploration filters are tied to the plot, not to the table** (against D-0506: "the filter is associated to the table and not the plot"). On the demo, opening `year_distribution` after `mlst_bar`, which reads the same table, clears your filters. (Section 3.4.)
6. **HOME cannot show the story of the data.** For `mlst_bar` it shows the original files as read and the stages of the joined table; not the tier 1 of `MLST`, not the other tables of the lineage, not the 6 tables that no plot reads ("Must be and yes must be viewab[le]", D-0457). So a user cannot look at the table where a step would be written. (Rows V2, V3.)
7. **The HOME upload replaces a recipe of the same name without a word** (`app/handlers/ingestion_handlers.py:44-51`), against "upload under same name refused" (D-0390). The recipe is the scientific document. (Section 3.14.)
8. **A session saved before its original recipe was edited is opened with a warning**, not refused as you decided (D-0362): old audit steps are then applied to a recipe that has changed. (Section 3.12.)
9. **The records disagree in places.** D-0361 decided that a switch between Exploration and Audit clears the filters; D-0505 and D-0506 say "not decided". D-0389 says the original recipe is "always" in the export; D-0192 removed the recipe from the Publication part. Several rule texts describe old states. (Section 3.18, 4.10.)

---

## 1. The picture in one page

**Words.** The app is data agnostic: "remember we are data agnostic so sample id is the example" (D-0512). An entity is what one row of the metadata describes; the entity key is the column the recipe declares with `is_entity_key` (D-0313). On the demo recipe `1_test_data_ST22_dummy` the entity is a sample and the key is `sample_id`; the story below says "sample" as the demo's example.

**Three kinds of table, the three blocks of a recipe** (D-0513; the mapping of each block to a kind is the review session's reading). `metadata_schema` carries the information about the entities: on the demo the source, year and country of each sample (D-0511). `data_schemas` hold the results of analysis for the entities and share the entity key with the metadata: on the demo `MLST`, `FastP`, `ResFinder` and the others, and `VirulenceFinder` once it is moved there, as you decided and as is not yet done (D-0513). `additional_datasets_schemas` hold the look-up tables: on the demo `APEC_STEC_virulence_genes`, the list of virulence genes of interest (D-0512, D-0513).

**The story of the data, on `mlst_bar`.**
1. The original files are read as they are: the MLST results and the metadata. In HOME this stage is "Source" (D-0310). The raw data are never changed (D-0509).
2. Tier 1 prepares each table: `MLST` keeps three columns and writes "Non Determined" for an unknown type; the metadata has no step (the demo recipe). Then the tier 1 of the joined table `MLST_with_metadata` joins the MLST results with the metadata on `sample_id`: a join with the metadata is always a tier 1 step (D-0510); a join takes only original tables (D-0344), and it reads each of them after its tier 1 (as built).
3. Tier 2 of `MLST_with_metadata` adds an era and keeps the years 2023 to 2025 (the demo recipe).
4. Tier 3 holds the plot's own steps; `mlst_bar` has none, so its T3 is its T2: "T1 feeds T2 feeds T3 feeds plot" (D-0179); "if no recipe steps for T3 then T3=T2" (D-0343).
5. The result is the plot `mlst_bar`. A result may also be a table, and it is always the last stage (D-0485) (not decided: the recipe form of a table result, see section 5, question 9).

A big join tells the same story with more branches: `ST22_Anchor` starts from the metadata, joins FastP, ResFinder, MLST and VirulenceFinder, then keeps only the genes of the look-up list (an inner join), all in its tier 1; its tier 2 counts the genes of each sample (the demo recipe). It feeds `virulence_bar` and `virulence_variants`. When a recipe opens, the app builds every table and draws every plot once, and with equal keys it rebuilds nothing (D-0326, D-0335).

**Looking (Exploration).** The user sees one plot, the result (D-0019, D-0180). Under it she views the stages of its table, Source, T1, T2 and T3 (D-0310), and, with the picker you asked for, any table of the recipe, in an outline that starts at the original files (D-0496, your wish; "I like the idea of outline at the base", D-0508) (not decided: which tables may be opened, section 5, question 6; where the picker opens, question 8). An exploration filter changes only the table viewed and never a plot, and it is never saved or exported (D-0327). It belongs to the table, not to the plot (D-0506), and it is cleared when the table viewed changes (D-0311) or the mode changes (D-0361).

**One audit, on the demo: a bad sample is seen in `mlst_bar`.**
1. She switches to Audit mode (D-0016); the right panel opens (D-0375, D-0385).
2. She finds the sample in the story of `mlst_bar` (D-0508) and creates an audit step from a table where she sees its key (D-0175): a removal by the entity key, one of the three kinds of audit step (D-0322), with a reason (D-0026).
3. The dialog lists the places of the lineage, one line per distinct table, each with its reach in tables and plots (D-0346, D-0347, D-0447, D-0451). The earliest places are ticked: "we tick low (early) near the original table" (D-0508) (not decided: which tier 1 is the earliest, section 5, question 1; my recommendation is the end of tier 1 of each table that joins the metadata, here `MLST_with_metadata` and the 12 other tables that join the metadata). The later tables appear as the propagation (D-0508) (not decided: as lines or as a drawing, question 2). For each ticked line the dialog shows the rows there (not decided: which number, question 3), "table changed" and "picture changed" for each plot (D-0318), the notes for the cases the app can follow (D-0477, D-0473) and, in red, what it cannot follow YET (D-0460, D-0454). It gives no warning about natural consequences further down (D-0501). Consequences are shown, never ticked (D-0446).
4. For a sample that must leave everything (it will be sequenced again), the separate option "remove from all the data" reaches every table that holds the key; it is off by default, shows its list before she confirms, and lets her untick a table, for example to keep the sample in the quality results (D-0415, D-0416, D-0498, D-0499, D-0500).
5. She confirms. The step is written at the end of each ticked tier (D-0146, D-0355), in the second list `audit_steps` of the audit recipe, a copy of the original recipe, with her reason as `audit_comment` (D-0102, D-0332, D-0329). The original recipe never changes (D-0102). The app runs only the changed tables again (D-0325).
6. She sees the audited plot; Compare shows the original and the audited plot (D-0016, D-0147); a result table gets the comparison in layers (D-0489) (not decided: a count of where the removed value is still found, question 4). She can take any step out again with "Remove step" (D-0314).
7. What is saved: when she applies with a reason (D-0302), her session keeps, in `audit/` inside her session folder, the audit recipe, its record with its hash, and the audit log with every warning she was shown (D-0319, D-0423, D-0333, D-0478) (not decided: what the log keeps of a warning, question 5). An audit recipe edited by hand is refused when it is opened again (D-0331).
8. What is exported: the audited results with the report, "# Results" by group before "# Technical" (D-0491); the Reproducibility part with an "original" and a "final_audited" part and the data stored once (D-0490, D-0492); the original recipe always (D-0389) (not decided: whether also in an export with only the Publication part, question 7); the audit log and its record always (D-0478, D-0333). Exploration is never exported (D-0327).

**What of this is built today.** Built: the stages and the opening, Exploration with its data choice, Compare of two plots, saving on Apply, and an export that contains only audited steps. Not built: a step written anywhere but at the plot's own table (section 3.1), the dialog with tick lines (3.2), the audit recipe as the one form of a step (3.8), the picker (row V4 of `PARTS_TABLES.md`), and the export of an audit as decided (3.13).

---

## 2. The parts (summary; the full tables are in `PARTS_TABLES.md`)

Each part has one table in `PARTS_TABLES.md` (same folder), with the columns DECIDED (your words and number), BUILT today (file:line), the difference, and the kind. Each row has an id (`S1`, `D2`, ...) that the sections below use. Here, one paragraph per part.

- **2.1 Stages of a table (rows S1 to S14).** The chain source, tier 1, tier 2, tier 3, result is built and agrees with your decisions (D-0179, D-0343). The three kinds of table are the three blocks of a recipe (D-0513); today nothing but HOME's Data Import and BLUEPRINT's drawing treats the blocks differently. Your rule that the join with the metadata is a tier 1 step (D-0510) is followed by the demo recipe but not checked. A table as a result (D-0485) is not built; the form with derived tables is not confirmed (D-0496). Two rule texts are out of date (the opening, the large-data threshold). The three sentences for the format specification that D-0513 asks for are proposed at the end of 2.1, as a proposal.
- **2.2 The audit: places and dialog (rows D1 to D14).** The most important difference of the document: a step can be written only at the open plot's table (T3), while you decided it can be written at each tier (D2, CONTRADICTS). The built dialog chooses plots, not places (D3, BUILT BUT OLD). "Remove from all the data" and the walk of the lineage exist only in the library, called by tests (D5, D6). The undo control and the key list are older designs (D7, D10). The Reshuffle writes a seed without a reason (D13, a builder's choice).
- **2.3 What the app tells and cannot know (rows I1 to I7).** The library's lists "may stay", "may differ" and (on a held branch) "stays by your choice" say the opposite of your words of D-0501 and D-0508 and were false alarms on the demo (I1, CONTRADICTS). The notes, the red lines and the good-practice page are not built. One screen text names "samples" as a fixed word (I7).
- **2.4 Viewing and the picker (rows V1 to V12).** The data choice Source, T1, T2, T3 is built; but it shows only the open plot's own table, so the story from the original files (D-0508) and the tables no plot reads (D-0457) cannot be seen (V2, V3). The exploration filters are tied to the plot, not to the table (V5, CONTRADICTS D-0506). Two finished pieces wait on branches (V8, V9).
- **2.5 The comparison (rows C1 to C4).** Compare of two plots is built. The layered comparison of a result table (D-0489) and the before-and-after comparison of D-0477 are not.
- **2.6 Audit recipe, record, log, sessions (rows R1 to R7).** Three representations of one audit step exist; the decided one (the audit recipe of D-0102, D-0332) is the one HOME does not use (R1). No audit folder, record or log (R3 to R5). A session of an edited original is opened with a warning, not refused (R7, CONTRADICTS D-0362).
- **2.7 Export and report (rows X1 to X14).** Correct on the scientific point that matters most: only audited steps are exported (X1). But the export of an audit is the older fork of a join (X3), the original recipe is in no part (X4), the mode control and the report structure are older designs (X5, X9).
- **2.8 Names (rows N1 to N4).** Every names decision is waiting for its one pass (N1). The HOME recipe upload replaces a recipe of the same name without a word (N2, CONTRADICTS D-0390).

Count of rows per kind (from `PARTS_TABLES.md`): AGREES 24; NOT BUILT 30; BUILT BUT OLD 10; BUILT BUT PROVISIONAL 4; CONTRADICTS 6.

---

## 3. The conflicts list

Every row of section 2 that is BUILT BUT OLD, BUILT BUT PROVISIONAL or CONTRADICTS, plus the records that disagree with each other. This is the list of "the old things that exist [that] are taken again" (D-0507). For each: what the app does; what was decided; what a user sees because of it; what closes it. "Slice N" points to section 6; "question N" to section 5.

**3.1 An audit step is written only at the plot's table (T3).** (row D2)
- The app: "Send to Audit" exists only in Audit mode while T3 is viewed (`app/handlers/filter_and_audit_handlers.py:152-155`); each step belongs to one plot and is applied to that plot's T3 table.
- Decided: "We had said we can send at each tier - so we need to send the correct tier" (D-0507); the end of each T1, T2 or T3 list (D-0146); the scope is the user's choice by the places ticked (D-0355).
- A user sees: "Audit steps apply to the plot's table (T3) for now." She cannot remove an entity before a join, cannot reach a table that no plot reads, and to change several plots she gets one copy of the step per plot (3.2).
- Closes: REPLACE, by the Create audit step dialog that writes at the ticked places (slice 4). Before it: questions 1, 2 and 3.

**3.2 The propagation modal against the dialog with tick lines.** (row D3)
- The app: "Apply to: This plot only / All plots / All plots except…", "This plot only" selected; one copy of the step per chosen plot; a plot whose table lacks the column is skipped, and the modal says "A skipped plot is NOT filtered — it shows the unfiltered data." (`filter_and_audit_handlers.py:1044-1066`).
- Decided: the dialog lists the distinct tables of the lineage as tick lines with their reach (D-0316, D-0346, D-0347, D-0415, D-0447, D-0451); consequences are shown and never ticked (D-0446).
- A user sees: a choice of plots, not of places. Two plots that read the same table get two separate copies of the same step.
- Closes: REPLACE in slice 4; the modal, its per-plot copies and the "linked" delete (3.9) go in the same slice, with no state where both dialogs exist.

**3.3 The lists "may stay", "may differ" and "stays by your choice".** (row I1)
- The app: nothing on screen. The library `libs/utils/src/utils/remove_from_all.py` lists `may_stay` and returns `may_differ` and `not_written`; the held branch `task/remove-from-all-ticked` adds `stays_by_choice`.
- Decided: "I would just shows the differents where applied and no per table warnings about downstream effects" (D-0501); "Id rather the check is more where you apply it" and "the user will have to learn that its not the sample that stays but where the change is applied" (D-0508).
- What the runs showed: on the demo every one of these statements was a false alarm (6 "may stay", 16 "stays by your choice"; the sample was gone everywhere; `TRIAL.md` Q6). Two reviews proved that a statement about a table where no step is written cannot be read from the recipe (untick `ST22_Anchor` and `metadata_schema`: told "stays", the two samples are gone).
- Closes: REMOVE the three lists in slice 4. What replaces them is your choice: the number shown where a step is written (question 3) and, perhaps, a measured recount after the build (question 4).

**3.4 The exploration filters are tied to the plot, not to the table.** (row V5)
- The app: the key of a filter is (recipe, mode, data choice, source table, open plot) (`app/modules/t3_audit_engine.py:69-73`); the plot is in it by a builder's choice marked "P-B2, PROVISIONAL" (`filter_and_audit_handlers.py:174-175`).
- Decided: "the filter is associated to the table and not the plot" (D-0506); a typed value is kept across plot tabs while the viewed table is the same (D-0505).
- A user sees: on the demo, she filters the table of `mlst_bar`, opens `year_distribution`, which reads the same table `MLST_with_metadata`, and her filters are gone, with the notice "you opened another plot".
- Closes: REPLACE the plot by the table viewed (which table, at which stage) in the key, in slice 1. No answer needed.

**3.5 Screen texts that say "for now" or state a limit that is old.**
- "Audit steps apply to the plot's table (T3) for now." (`app/handlers/home_theater.py:1479`): goes with 3.1.
- "To create an audit step, view T3." (`filter_and_audit_handlers.py:694`) and the button title "...applies only to T3, and cannot be silently discarded once committed." (`:674-676`): the second is also untrue today, because the trash button removes a committed step. Both go with 3.1.
- "...still in the Publication content, just not engine-replayable yet." (export notice, `app/handlers/export_handlers.py:1615-1620`): goes with 3.8.
- "Add N filter/exclusion(s) — choose scope" (`filter_and_audit_handlers.py:997`): "exclusion" is never written (row D8); goes with 3.2.
- The panel title "My Adjustments (Tier 3)" (`app/handlers/audit_stack.py:460`): "My" is the word of the retired "My view" (D-0179); goes with slice 3.
- Closes: each text goes with the part it describes; none is changed alone, so that no screen text and code disagree in between.

**3.6 Two ways of telling a lineage: the shared recipe graph and BLUEPRINT's navigator.**
- The app: the structure is read once, by the shared graph (`libs/utils/src/utils/recipe_graph.py`). BLUEPRINT's navigator now takes its structure from it (`libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py:79`, and its header: "This module keeps no second description of the structure"), as D-0031 asked. What remains double is how a lineage is SHOWN and NAMED: BLUEPRINT's roles and colours (`trunk`, `add`, `meta`, `wrangle`, `branch`, `plot`; `blueprint_mapper.py:71`), its Lineage Rail and its tube map, whose drawing is bound to BLUEPRINT (`app/src/ui.py:134`, `:288`); and the lineage walk's places (SOURCE, T1, T2, T3) for the audit (`libs/utils/src/utils/lineage_records.py`). The export's "Data Lineage" section is drawn from the navigator (`export_handlers.py:1703`).
- Decided: one source of truth (D-0065, D-0031); the picker shows the story and the branching (D-0496, D-0508); BLUEPRINT's design is revisited before it is built, "because we had the lineage/tube map also to leverage" (D-0309).
- A user sees: in HOME no lineage at all; in the export one graph; in BLUEPRINT another vocabulary.
- Closes: one pure function in the shared graph that gives the groups of linked tables, the path up and the path down, and the stage of each node; used by HOME's picker (slice 7) and by the dialog's propagation view (slice 4); BLUEPRINT moves onto it in its own rebuild (D-0494). Not a third system.

**3.7 T0.** Proposed by you on 2026-11-22 ("maybe then we need instead to be able to add some filters in the original data as T0", D-0507) and withdrawn the same day: "revision request . no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged." (D-0509). Nothing was built. Nothing to close.

**3.8 Three representations of one audit step.** (rows R1, X3)
- The app: (a) HOME's node, kept in the session state and the session file (`app/modules/session_manager.py:56-106`); (b) the library's audit copy, the decided form, with no caller in the running app (`libs/utils/src/utils/audit_copy.py`); (c) the export's fork of each plot's join, its tier 2 plus the translated steps (`libs/blueprint_arch/src/blueprint_arch/t3_translator.py:197-290`).
- Decided: the audit recipe is a copy that only adds steps, in a second list of each tier, with `audit_comment` (D-0102, D-0143, D-0332, D-0329); "when audit steps have been added the audit recipe is the truth - so the export must contain the recipe of the audit" (D-0324).
- A user sees: the same steps under two key names (`reason` in HOME, `audit_comment` in the copy); in the reproducibility part, a recipe with tables she never wrote (`<join>__t3_<plot>`); a plot whose step cannot be translated is "skipped" from the replay (the notice of 3.5).
- Closes: REPLACE (a) and (c) by (b) in slice 3: HOME writes the audit copy; the session holds it; the export writes it. Removed in the same slice: the translator's fork, the flat list kept "for bw compat" in the session file, the `__legacy__` reader, the stale `plot_scopes_intent` comments (`home_theater.py:287`, `orchestrator_helpers.py:53`).

**3.9 The undo control.** (row D7)
- The app: a trash button per step that removes every copy of its id from every plot (`audit_stack.py:627-682`).
- Decided: ONE control, "Remove step": the user picks any step and removes it (D-0314).
- A user sees: "Delete this audit node (linked: removes from all plots)".
- Closes: REPLACE in slice 3 (one step of the audit copy removed by its id: `audit_copy.remove_step` exists).

**3.10 The key of the audit.** (row D10)
- The app: one list, the join keys, drives the warning (`session_manager.py:125-135`).
- Decided: two lists, "the entity key" and "columns used to join" (D-0313, "C").
- A user sees: "One or more nodes target a join key. Removing rows here changes which samples appear in joined plots."
- Closes: REPLACE in slice 4 (the warning goes with the modal; the dialog names the entity key and shows the join columns as information, in data-agnostic words, D-0512).

**3.11 The Reshuffle writes a new seed without a reason.** (row D13)
- The app: in Audit mode a click writes a seed into the plot's overrides, with no reason and no Apply, and it is exported (`home_theater.py:877-899`).
- Decided: offered only in Audit mode (D-0341). NOT decided: how a reshuffle is written down as an audit step.
- A user sees: a new picture, a seed line with "remove the pin"; the reason for the change is nowhere.
- Closes: your choice (question 12).

**3.12 A session saved before the original recipe was edited is opened.** (row R7)
- The app: it warns and opens (`app/handlers/session_handlers.py:556`, as the ledger line says).
- Decided: "so I would refuse - I would explain that the original recipe has been modified and that it needs to reanalyze and add the audit steps where they are done" (D-0362).
- A user sees: her old audit steps applied to a recipe that is no longer the one they were made on.
- Closes: REPLACE (refuse, with the plain line) in slice 3, where the session holds the audit recipe and its `audit_of` fingerprint (D-0339). No answer needed.

**3.13 The export of an audit.** (rows X3 to X7, X9, X13)
- The app: one check box "Also include a reproducibility/reimport bundle"; when ticked, the fork of 3.8 and a copy of the data files; no original recipe in any part; no audit record, no audit log; a flat report (`## Plots`, then `### <name>` per plot) whose names come from `ui_title` first; the import writes into the app's recipe folder.
- Decided: two ticks "Publication" and "Reproducibility" and one button (D-0298); a raw-data line beside the tick (D-0301); the audit recipe (D-0324); the original recipe always, "1. yes must." (D-0389); two parts "original" and "final_audited", the data once (D-0490, D-0492); the log and the record always (D-0478, D-0333); "# Results before # Technical" (D-0491); headings from `ui_label` (D-0484); the import writes into the user's own place under a name_date and refuses an existing name (D-0435).
- A user sees: a bundle she cannot re-run from the original recipe; no proof that the audit recipe was not edited by hand; no record of the warnings she was shown.
- Closes: REPLACE in slices 5 and 6. Before slice 5: question 7 (the original recipe in the Publication part).

**3.14 The HOME upload replaces a recipe of the same name without a word.** (row N2)
- The app: every uploaded `.yaml` is copied into the recipe folder over any file of the same name (`app/handlers/ingestion_handlers.py:44-51`).
- Decided: "upload under same name refused" (D-0390).
- A user sees: "Ingestion complete." Her recipe, the scientific document (D-0186: "changing a recipe is" a failure), was replaced.
- Closes: REPLACE (refuse an existing name with a plain line) in slice 2. No answer needed for the refusal; where an upload is written belongs to the deployment specification (D-0417, D-0418; not decided in detail).

**3.15 Data-agnostic words.** (row I7) "Removing rows here changes which samples appear in joined plots." (`filter_and_audit_handlers.py:1004-1005`) names "samples" as a fixed word, against D-0416 and D-0512. Closes: removed with the modal in slice 4; the check of every recorded text that D-0512 asks for is part of slice 0.

**3.16 The HOME key-drop check that cannot fire.** (row D9) HOME asks the drop gate at `T3:<plot>`, where nothing comes after the drop, so the rule of D-0358 ("refused by place") cannot refuse anything from HOME. It is a consequence of 3.1. Closes: with slice 4, where a drop can be written at tier 1 or tier 2 and the gate then decides.

**3.17 Builders' choices that stay until you decide (BUILT BUT PROVISIONAL).**
- The defaults: T3 and Exploration (`app/src/server.py:143-147`; row V7). Question 10.
- Comparisons on dates (`app/modules/t3_audit_engine.py:321`; row V12): the rule file says "not decided and not offered". Question 13.
- The words "Source", "T1", "T2", "T3", "Mode" and their tooltips (row N4). Question 11.

**3.18 Records that disagree with each other (rule H: reported, not resolved silently).**
- a. A switch between Exploration and Audit: D-0361 DECIDED that it clears the exploration filters ("8 - No we had decided to clear them- Only the steps applied in the audit are kept"); D-0505 and D-0506 say "NOT decided: what a change of mode does to the filters"; the rule files say "PROVISIONAL". The code clears them, as D-0361 says.
- b. D-0486 says the semi join is "built on a branch, not merged"; it is merged on `dev` (commit 82126831; `libs/utils/src/utils/step_effects.py:68`).
- c. D-0358 says "NOT BUILT (the code refuses by name)"; the drop gate by place is built (`libs/utils/src/utils/key_drop.py`).
- d. Rule texts out of date: the opening "DECIDED, not built" (built); the large-data threshold "not decided" (D-0363 decided it); aesthetic overrides "never applied" (applied); `developer_raw_yaml` in the gatekeeper list (removed); `plot_content_rules` named as "the pure rule" (no such function); the three-way export scope (removed by D-0292); "the keys are not read from a file yet" (the engine reads `audit_steps`); D-0383 and D-0385 recorded as "not built" (built).
- Closes: a scribe corrects the records in slice 0. D-0361 governs: it is a decision of yours, and nothing later replaces it, so no question is needed.

**3.19 Where your earlier and later decisions pull apart.** D-0389 ("The export always contains the original recipe") against D-0192 ("I suggest to remove the recipe from the mode 1"). This is not an old behaviour of the code but two decisions: section 4 point 10 and question 7.

---

## 4. Where your decisions meet each other

Pairs of decisions that cannot both hold as written, or that leave a hole between them. Each point quotes both lines and ends with the question it raises. Candidates that I examined and found to hold together are listed at the end, with the reason.

### 4.1 "Tick low near the original table" against "modify at the join keeping the raw data unchanged" — CONFIRMED, the most important point

- D-0508: "but ok we tick low (early) near the original table - so by default it is propagated in the lineage". D-0501: "yes the default will need to include the earliest place of each branch - which is the original data basically".
- D-0509: "revision request . no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged." D-0510: "metada is a certain type of data - other joins could be used after but join with metadata must be done at T1 that would simplify removing of samples by key no".

There are two tables on every path of the demo where a "tier 1" sits: the tier 1 of the original table (for example `MLST`: keep three columns, write "Non Determined") and the tier 1 of the table that joins it with the metadata (`MLST_with_metadata`: the left join on `sample_id`). HOME shows only the second as "T1" of `mlst_bar` (`app/handlers/home_theater.py:327-348`, read by me). So "the earliest place" has two readings:
- **(a)** the end of tier 1 of each ORIGINAL table (the trial's "A");
- **(b)** the end of tier 1 of the table that JOINS the results table with the metadata (and, on a branch that never meets the metadata, the first table of that branch).

One observation that is a fact of the recipe, not a reading: the place of the metadata join (tier 1 or tier 2) changes nothing for (a), because (a) writes before every join. D-0510's reason ("that would simplify removing of samples by key") is only true under (b): a step at the end of tier 1 of a joined table sits after the join with the metadata exactly when that join is a tier 1 step.

What each reading does on the demo. **Run** on 2026-11-22 for this document (the engine, the real data, one sample, `10668076`, present in all 27 tables that hold the key; the script is `tmpAI/run_scratch/earliest_place_run.py` of the worktree, scratch, not in git, written on the trial's harness):

| | (a) tier 1 of the original tables | (b) end of tier 1 of the tables that join the metadata |
|---|---|---|
| A removal started from `mlst_bar`, with the default ticks | 2 steps (`MLST`, `metadata_schema`). 13 plots change. The sample stays in 7 plots: in 4 of them because their tables never meet `MLST` or the metadata (`amr_heatmap`, `phenotype_genome_length_fragmentation`, `qa_l50_integer`, `qa_sequence_type_missing`), and in 3 of them **with its `source`, `year` and `country` emptied** (`qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`), because there the metadata is the second table of a left join. `miaou` draws `source` (verified in its file): its picture changes. | Only the table of `mlst_bar` ticked (1 step at `MLST_with_metadata`): 2 plots change (`mlst_bar`, `year_distribution`); nothing else is touched. Every table that joins the metadata ticked (13 steps): 13 plots change; the sample stays only in the 4 plots whose tables never meet the metadata; nothing is emptied. |
| "Remove from all the data" | 11 steps; the sample is in no table and no plot (the same as the trial's run). | 19 steps (13 joined tables, and the first table of the 6 branches without the metadata); the sample is in no plot; the 8 original tables still hold it at their tier 1 (the raw data unchanged). |
| Your case of D-0499: keep the bad sample in the quality results, remove it from all others | Untick `FastP`, `Quast`, `Bracken`: the sample stays in the 3 quality plots **without its metadata**, and in `qa_l50_integer`. Untick the metadata too: it stays in 9 plots, so it is not "removed from all other results". | Untick `QC_Reads_Anchor` and `Quast_with_metadata`: the sample stays in exactly the 3 quality plots, **with its metadata**, and is removed from the 14 others. |
| What changes in the recipe | the tier 1 of the original tables (the files are never changed) | only the joined tables |
| A step in tier 1, after the join, that computes over all entities | the entity leaves before it: no effect on the others | the computation runs with the entity, then the entity is removed: the others' values were computed with it (trial, synthetic recipe: a z-score of -1.254 becomes -1.336). On the demo such computations are in tier 2 (`QA_population_zscore`, `QA_aggregated_no_key`, verified), so there is no difference there. |

**Which tables join the metadata, on the demo (read by me in its files).** 13 tables have `metadata_schema` among their tables, and every one of their joins with it is a tier 1 step (D-0510 holds on the demo): `FastP_with_metadata`, `Quast_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `MLST_with_metadata`, `QC_Reads_Anchor` and `AR1_MLST_Serotype_Virulence` (there the metadata is the SECOND table of a left join), `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit` and `QA_population_zscore` (there the metadata is the FIRST table), `QA_year_types` and `QA_aggregated_no_key` (the metadata alone, no join step). 4 plots read a table that never meets the metadata: `amr_heatmap` reads the original table `ResFinder` directly (after its tier 2); `phenotype_genome_length_fragmentation` reads the join of `Summary` and `Summary_quality`; `qa_sequence_type_missing` reads a join of `Summary_quality` alone; `qa_l50_integer` a join of `Quast` alone. Two original tables are read by no plot and no join: `Quality_metrics`, `Detailed_summary`. In the run of reading (b), the earliest place on such a branch was the first table that the branch's results read (`ResFinder` for `amr_heatmap`; the three joins for the three other plots; the two lone tables themselves). The look-up table `APEC_STEC_virulence_genes` has no entity key and is never a place.

The question: question 1 of section 5.

### 4.2 All places ticked (D-0194, D-0316, D-0359) against "tick low" (D-0508) — CONFIRMED, partly resolved

- D-0194: "I think that I would choose A as default : because then all the boxes follow the lineages - so it show clearly the extend of where it will be removed". D-0359: "5. A (we might want to change this behavior after testing)".
- D-0501: "And yes it reopen D-0316 - A would think A ... there is nothing wrong in changing my decision"; D-0508: "we tick low (early) near the original table".
- What holds: D-0508 is your answer after the review you asked for in D-0501 (`tmpAI/panel/default_ticks/TABLE_FOR_THE_OWNER.md`: all four viewpoints for "A"). The ledger records it as your new default but no line says "replaces D-0316"; a scribe should add the relation (slice 0).
- The hole: your reason of D-0194 ("it show clearly the extend") moves to the drawing of the propagation (D-0508: "lineage should be represented as a propagation eg. original -> T1 -> T2"). It is not decided whether a later place is still a line the user can tick (your year example of D-0199: a filter "in T3 and not T1"), or untick (D-0499). The question: question 2.

### 4.3 Tick lines with their reach (D-0346, D-0447) and "the lineage represented as a propagation" (D-0508) — CONFIRMED as a hole

- D-0346: "The choices need to evaluate the reach"; D-0447 ("A"): the reach is said in two parts, the tables one can open and the plots, then the tables no plot reads.
- D-0508: "so maybe lineage should be represented as a propagation eg. original -> T1 -> T2 so the user sees that it affect the next one".
- They can both hold: the reach is the propagation of a ticked line, counted. The hole is the same as in 4.2: whether the tables of the reach are lines or only a drawing. Folded into question 2.

### 4.4 Keep the bad sample in the quality results (D-0499) and the proof that no statement can be read for a table where no step is written — CONFIRMED

- D-0499: "yes the user may unthink he is responsible of its choice. eg case : he wants to show the poor quality sample for the quality results but remove the bad sample from all other results."
- The two reviews of 2026-11-22: a sentence about a table where no step is written ("stays", "removed upstream") was false on the demo and on small recipes; only a run can measure it.
- What the run of 4.1 adds: under reading (a), your case leaves the sample in the quality results without its metadata; nothing in the recipe tells the dialog so before the run. Under reading (b), the result is what you asked for.
- The question it raises: how the user checks, after applying, that her choice did what she wanted. Questions 1 and 4.

### 4.5 The data choice of the open plot (D-0310) and a picker that opens any table (D-0496, D-0457) — CONFIRMED as a hole

- D-0310: "the filters must show what is true in T3 when viewing T3, and what is true in T1 when viewing T1": the four choices are the stages of the open plot's table.
- D-0457: "Must be and yes must be viewab[le] in the data preview" (tables that no plot reads belong to no plot). D-0496 (your wish): "you can pick every original data and see all lineages that goes from there".
- The hole: what "Source / T1 / T2 / T3" mean when the table viewed is not the open plot's, and from which table "Send to Audit" starts. D-0506 already makes the filters follow the table, which removes one conflict. The question: question 6.

### 4.6 A result is a plot or a table (D-0485) and the form with derived tables, not confirmed (D-0496) — CONFIRMED as a hole

- D-0485: "the result is the last stage ... last tier of entry also can be T3=T2=T1 (so the fall back mechanism)"; "we need to follow the recipe --- so do not fix all tiers need to be functional".
- D-0496: "wait for the panel I just said I might have more questions after". D-0511: "derived tables should already have the metadata joined".
- The hole: until the form is chosen, it is not known where a summary table lives, whether a result may carry steps of its own, and therefore where a "this result only" audit step is written (D-0346 says: the audit gives the result its own audit steps at tier 3). The panel's proposal recommends form 3 (`tmpAI/panel/tables_as_results/refined/PROPOSAL_FOR_THE_OWNER.md`). The question: question 9.

### 4.7 "Remove from all the data" (D-0415, D-0416) and the default ticks (D-0508) — CONFIRMED, folded into question 1

- D-0415: "I want an option that is independent of the lineage itself that allow selection all the data T1 where eg. the sample is selected". D-0508: tick low.
- Under reading (a) the earliest places are the 11 original tables and the result is the same as ticking all 27 (trial and run). Under reading (b) there are 19 places. If one rule gives the default ticks to both dialogs (the architect's advice in the review), question 1 settles both.

### 4.8 The comparison in layers (D-0489) and "rows with this sample: before, after" (the review's advice; D-0508 left the number open) — EXAMINED, they hold together

- D-0489: "For layer 1 I think will be mostly what we need, agree the full row diff on request only".
- They are two moments: the pair is said in the dialog, per place, BEFORE confirming; the layers compare the original and the audited RESULT after applying. At a place where a step is written, the pair can be counted on the stored table of that place (D-0326 builds every table at opening). After the step, in later tables, a count needs a run of the candidate recipe (D-0325: "a real run of only the changed tables happens when the audit step is applied"). The question of the number is question 3; the question of a count in later tables is question 4.

### 4.9 Metadata "more a practical trick" (D-0224) and the metadata as a declared kind with its own rule (D-0510, D-0511, D-0513) — EXAMINED, no conflict

- D-0224 (2026-11-17): "well metadata is one row per sample id" and "its more a practical tric than a real one"; "most joins are done on metadata".
- D-0510 adds a rule for where its join goes; D-0513 makes the kinds the blocks. D-0224 was about the id rule (no separate one for the metadata); nothing replaces it. Recorded here so that a reader does not take D-0224 as an argument against D-0510.

### 4.10 "The export always contains the original recipe" (D-0389) and "remove the recipe from the mode 1" (D-0192) — CONFIRMED

- D-0389: "1. yes must." (to the question whether the export always contains the original recipe) and "the export of original recipes should also be exported with the reason that: if you need to redo the analysis then you will need to re-upload the recipe".
- D-0192: "I think that would be best to add the recipe to the reproducibility mode 2 - And I suggest to remove the recipe from the mode 1".
- D-0490 then puts the original recipe in the reproducibility bundle ("original"); the review session read that the publication bundle gets nothing more (not confirmed by you).
- The question: does "always" include an export with only the Publication tick? Question 7.

### 4.11 "See original and modified plot in the export" (D-0147) and the baseline in the reproducibility part (D-0490) — CONFIRMED as a hole

- D-0147: "10. In the export we need to be able to see original and modified plot."
- D-0490: "ok, I think we need to add the baseline in the reproducibility bundle then we are covered."
- Today every exported plot is the audited one. With D-0490 the original can be re-run, but no original picture is in the bundle. Folded into question 7.

### 4.12 A mode switch clears the filters (D-0361) and "not decided" (D-0505, D-0506) — EXAMINED, a records error

- D-0361: "8 - No we had decided to clear them- Only the steps applied in the audit are kept -> but then they are writen in the recipe".
- D-0505 and D-0506 list "NOT decided: what a change of mode does to the filters". This is a mistake in the records (section 3.18 a), not two decisions. No question.

### 4.13 The notes for the silent cases (D-0477) and the proof of the two reviews — EXAMINED, they hold together under one condition

- D-0477: "eg. left join keeps the rows of the second table - ensure you removed in second table if this is what you want (or something similar) - Option B".
- The reviews: a sentence about a LATER table ("the sample stays there") was false when a later step dropped rows (the inner join on the gene list in `ST22_Anchor`).
- They hold together if each note speaks of the place it stands on (for example, at the join itself: "a left join keeps the rows of its first table; this table is not ticked"), never of a table further down. A rule for the words of the notes, for slice 4; not a new question.

### Examined and dropped (they hold together)

- D-0344 (a join takes only source tables) with D-0510 and D-0513: "source tables" are the tables of the three blocks; the join with the metadata is a tier 1 step of a join; no conflict. It would meet the derived tables only if you confirm that form and want a join that takes a derived table (the panel's question 10).
- D-0346 ("A join that no plot reads is not offered") with D-0451 ("We must modify"): resolved by D-0451.
- D-0146 ("the end of each T1 - T2 - T3 (for now)") with D-0507 ("maybe we need at the beginning of T1 also"): resolved by D-0509 (no T0, no beginning of T1).
- D-0315 (log in the bundle only when ticked) with D-0478 ("not optional anymore"): resolved by D-0478.
- D-0022 ("a step is written at ONE of T1/T2 of a table or T3 of a plot") with D-0093 (applied at each ticked node): one write per ticked place; no conflict.

---

## 5. What stays yours to choose

One question at a time, the ones that block the most first. Each: the question; what it blocks; the options with what you would see on the demo recipe, their merit for and against, and what they reopen (as information, never as an argument); what today's runs say; a recommendation, marked as mine. Cost and build time are not used anywhere.

Not asked, because you closed them while this document was written: the metadata joined from a table that is not a raw data table, and the information about the entities held outside `metadata_schema` (D-0511: "well it seems trivial the metadata is what carries the sample information - derived tables should already have the metadata joined ..."); whether a table's kind must be declared (D-0513: it is declared by its block).

### Question 1. When the dialog ticks "the earliest place", is it the tier 1 of each original table, or the end of tier 1 of the table that joins it with the metadata?

- **Blocks:** where every removal is written by default, in the normal dialog and in "remove from all the data"; what the audit recipe holds. Slice 4 cannot start without it.
- **Option (a): the tier 1 of each original table.**
  - On the demo: from `mlst_bar`, 2 ticked lines (`MLST`, `metadata_schema`); the sample leaves 13 plots; it stays, with `source`, `year` and `country` emptied, in `qc_reads_horizontal_barplot`, `assembly_quality_dotplot` and `miaou` (whose picture changes, it draws `source`). "Remove from all the data": 11 lines; the sample is in no plot.
  - For: the fewest steps; each written step is the first on its path, so its number means what you expect (trial Q4); a computation over all entities never sees the removed entity; already run twice on the demo.
  - Against: the original tables' tier 1 changes, and HOME cannot show it today; where the metadata is the second table of a left join and the results table is not ticked, the row stays with emptied metadata (run), a change of results that a note must announce; your case of D-0499 cannot be done cleanly (run); the place of the metadata join (D-0510) plays no role.
  - Reopens: nothing.
- **Option (b): the end of tier 1 of each table that joins the metadata; on a branch that never meets the metadata, the end of tier 1 of the first table its results read (on the demo: `ResFinder` for `amr_heatmap`, the joins of the three other such plots, and the two tables no plot reads; section 4.1).**
  - On the demo: from `mlst_bar`, the 13 tables that join the metadata are ticked; 13 plots change; nothing is emptied. "Remove from all the data": 19 lines; the sample is in no plot; the 8 original tables keep it at their tier 1.
  - For: your words "modify at the join keeping the raw data unchanged" (D-0509) and the reason of D-0510; a removal after the join removes the row whatever the kind of join, so no metadata is emptied (run); your D-0499 case works as you described it (run); the original tables stay as read.
  - Against: more steps (13 or 19 on the demo, against 2 or 11): the same removal is written once per joined table, so the audit recipe is longer; a computation over all entities written in tier 1 after the join runs before the removal (trial, synthetic case; not the case on the demo); two rules, because a branch without the metadata falls back to its first table (D-0510 allows such recipes).
  - Reopens: nothing; it applies D-0509 and D-0510.
- **Evidence:** the run of section 4.1 (this document) and the trial (`tmpAI/panel/default_ticks/TRIAL.md`, Q1 and Q3).
- **My recommendation: (b).** It is the only reading in which your rule of D-0510 does what you said it is for; it keeps the original tables unchanged, as D-0509 says; on the demo it gives your D-0499 case exactly and empties no metadata, which (a) does in 3 plots. The tests of slice 4 should be the lines of the table in 4.1.

### Question 2. With the earliest places ticked, how does the dialog show the later places?

- **Blocks:** whether a later place can still be chosen on purpose (your year example, D-0199) or unticked (D-0499), and how the reach is shown (D-0346, D-0447). Slice 4.
- **Option (a):** every place of the lineage is a line; only the earliest start ticked; the later ones are unticked lines, in the order of the propagation. On the demo, from `mlst_bar` under question 1 (b): the original tables `MLST` and `metadata_schema` and the tier 2 places are unticked lines next to the 13 ticked ones. For: every choice is visible. Against: the user viewpoint of the review found that unticked lines read as "the sample stays there", which is the opposite of the truth.
- **Option (b):** only the ticked places are lines; under each line its propagation is drawn (original, T1, T2, the plots), not tickable; the line "this plot only" stays (D-0346); to write at another place on purpose, the user opens that table and starts the dialog from there (a step starts where the user sees the column, D-0175). For: your words "lineage should be represented as a propagation" (D-0508); short. Against: a later place is one step further away.
- **Option (c):** as (b), with one control "choose other places" that opens the full list of (a).
- Reopens: nothing in (a) and (c); (b) reaches D-0355 ("the user decide the scope") only through another start point.
- **Evidence:** the review of the default ticks (`TABLE_FOR_THE_OWNER.md`, flag 6 and section 3).
- **My recommendation: (c).** The propagation as you described it, and every choice of D-0355 and D-0499 one click away.

### Question 3. Which number does the dialog show at a ticked place before you confirm?

- **Blocks:** the content of the dialog: "the dialog shows the rows and plots affected before she confirms" (D-0316). Slice 4.
- **Option (a):** the pair: "rows with this value here: 26 before, 0 after" (`Summary` and one sample on the demo).
- **Option (b):** "rows removed here: 26", with your meaning of 0: the value is not found in this table (D-0508).
- Reopens: nothing.
- **Evidence:** trial Q4: the pair was true in every run; "removed" alone is true at the first place of a path, which under the earliest-place default every written step is.
- **My recommendation: (a).** One line holds both facts; "0 before" says exactly your "it does not find the value"; and it stays true when a user ticks a later place by hand, where "removed: 0" would mislead.

### Question 4. After a step is applied, does the app count where the removed value is still found?

- **Blocks:** the end of slice 4, and how a user checks your D-0499 case.
- **Option (a):** no count. The user checks with the audited results, the preview's row counts (D-0488) and Compare. Your words: "Id rather the check is more where you apply it" (D-0508).
- **Option (b):** one measured count after the build, as one line that names only the tables where the removed value is still found, with the rows ("Still found after the audit: table of `miaou`, 3 rows"); nothing when none.
- **Option (c):** as (b), with a second count that ignores upper and lower case and spaces around the value (it finds a key rewritten by a step, one of your three gotchas, D-0508).
- On the demo: under question 1 (a), from `mlst_bar`, (b) names the 3 quality tables whose metadata was emptied; under question 1 (b), "remove from all the data" gives no line (run).
- Reopens: nothing, if it is read as a fact; it would go against D-0501 if it became a warning per table, which it is not.
- **Evidence:** the two reviews (a statement about a table where no step is written cannot be read from the recipe; only a run can measure it); the run of 4.1.
- **My recommendation: (b).** It is the only true check of what the dialog cannot read from the recipe, and it lets a user verify a choice like D-0499. It names only a table where the value you removed is still there.

### Question 5. What does the audit log keep of a warning that the dialog showed?

- **Blocks:** the audit log, which is always exported (D-0478) and is built with the dialog in slice 4, because it records what the dialog shows. D-0478 lists it as not decided: "what 'the warnings shown' holds in the log (the words as displayed, the facts as data, or both)".
- **Option (a):** the words exactly as displayed.
- **Option (b):** the facts as data (the kind of note, the table, the numbers), from which the words can be made again.
- **Option (c):** both.
- On the demo, for the removal of one sample under question 1 (a), a log line would read, for example, "left join: the rows of `QC_Reads_Anchor` stay when only the metadata is ticked" (the words) and `{note: left_join_keeps_first_table, table: QC_Reads_Anchor, ticked: metadata_schema}` (the facts). Both illustrations are mine.
- Reopens: nothing.
- **My recommendation: (c).** Your two reasons of D-0478 need both: "so we can show that the user has been warned" (the words she read) and "reviewing if there are complains what is not working and where" (the facts).
- Not asked here: how the initials are entered (D-0478 lists it as not decided); it comes with the screen of slice 4.

### Question 6. May HOME show a table that is not the open plot's table, and from which table does "Send to Audit" start?

- **Blocks:** the picker (slice 8), the 6 tables of the demo that no plot reads (D-0457), the start of the dialog from an earlier table.
- **Option (a):** any table of the recipe can be opened, at any of its stages; the badge names the table; "Send to Audit" starts the dialog from the table viewed.
- **Option (b):** only the tables of the open plot's lineage can be opened; "Send to Audit" as in (a). On the demo, `Quality_metrics` and `Detailed_summary` are in no plot's lineage, so they stay unreachable, against D-0457.
- **Option (c):** any table can be opened for viewing; "Send to Audit" only from the open plot's own table. The bad row seen in the tier 1 of `MLST` must be removed from `mlst_bar`'s table.
- Reopens: (a) and (c) widen D-0310 (the data choice of the open plot); (b) widens it less.
- **Evidence:** the picker review (all four viewpoints: any table, opened in the normal data preview; the scientist: a user who sees a row in a join and cannot act there "will filter at the wrong place (D-0450)").
- **My recommendation: (a).** It is your picker ("pick every original data and see all lineages"), D-0457 needs it, and D-0175 says a step starts where the user sees the column.

### Question 7. When an audit exists, what does the Publication part of an export hold besides the audited results?

- **Blocks:** slice 5. D-0389 says the original recipe is "always" in the export; D-0192 removed the recipe from mode 1; D-0147 asks to see the original and the modified plot.
- **Option (a):** nothing more. The original recipe and its data are in the reproducibility part ("original"), the audit recipe in "final_audited" (D-0490, D-0492). An export with only the Publication tick then holds no original recipe.
- **Option (b):** the original recipe in every export, Publication included, with its one line of reason (D-0389 read literally).
- **Option (c):** the original plots beside the audited ones (D-0147); the recipes as in (a).
- On the demo: with a step on `mlst_bar`, (c) puts the original and the audited `mlst_bar` picture in the Publication part.
- Reopens: (a) and (c) narrow D-0389's "always" to the exports that hold the reproducibility part; (b) reopens D-0192.
- **My recommendation: (c),** with the README sentence of D-0333 saying which file is which. It meets D-0147 and D-0192 and keeps the Publication part readable; to meet D-0389 fully, the Reproducibility tick would have to be on whenever an audit exists, which is your call.

### Question 8. Where does the picker open?

- **Blocks:** slice 8.
- **Option (a):** a popup window, as you said ("it can be in a popup window", D-0496).
- **Option (b):** a side panel, so the figure stays in sight while the user compares it with the table (the user viewpoint of the review). In Exploration the right panel is empty today (D-0383: "yes (but it will be empty at least for now)").
- **Option (c):** both, with one switch, as you asked for the recipe overview: "it can be coded so its easier to change place" (D-0084).
- Reopens: nothing.
- **My recommendation: (b),** the right panel in Exploration, with the switch of (c) kept in mind; it is the one viewpoint that differs from your words, so it is yours to weigh.

### Question 9. A table as a result: which recipe form?

- **Blocks:** table results (row S7), their export by name (X7), the comparison of a result table on screen (C2), and where a "this result only" step goes for a table.
- **Options** (the refined panel proposal, `tmpAI/panel/tables_as_results/refined/PROPOSAL_FOR_THE_OWNER.md`): **form 3**, derived tables in a block of their own, a result has no steps of its own and the audit writes "this result only" in the result's tier 3; **form 4**, the same, and a result may add steps of its own; **form 5**, named tier 3 stages inside a table.
- On the demo (the panel's run): `mlst_bar` reads `MLST_with_metadata` (33 rows after its tier 2); a derived table of samples per country and year (6 rows) is shown as a table and as a plot; removing one sample at the joined table's tier 2 changes both.
- Reopens: form 3: D-0063 and D-0306 (the author writes a plot's tier 3); form 4: none of these; form 5: D-0250, D-0063, D-0306.
- **My recommendation: form 3,** as the panel recommends; it also agrees with D-0511 ("derived tables should already have the metadata joined").

### Question 10. The defaults when a recipe opens.

- **Blocks:** nothing large; the defaults are builders' choices today (row V7).
- **Option (a):** as built: Exploration, and the data choice on T3 (the table the plot is drawn from).
- **Option (b):** Exploration, and the data choice on Source (the story starts at the original files, D-0508).
- **Option (c):** the mode and the table last used in this session are kept.
- Reopens: nothing. For a table result D-0487 already says "maybe the result should be the default at opening".
- **My recommendation: (a),** because the table under the figure is the one the figure is drawn from, and your words of D-0508 ("we could choose earlier T for preview") keep the earlier stages one click away.

### Question 11. The words on screen for the stages.

- **Blocks:** the texts of slices 4 and 8; the words today are PROVISIONAL (row N4).
- **Option (a):** "Source, T1, T2, T3" with their tooltips, as built.
- **Option (b):** plain words: "Original data files", "Joined tables", "Figure", "Where this table comes from", "What uses this table" (the user viewpoint of the picker review).
- **Option (c):** plain words with the stage in brackets, for example "Joined table (T1)".
- **My recommendation: (c):** a user who is not a developer reads the words, and the stage names stay to link the screen with the recipe and the documentation.

### Question 12. How is a Reshuffle recorded?

- **Blocks:** nothing now; D-0341: "this reshuffling is not critical for now". Today a reshuffle changes the picture with no reason (row D13).
- **Option (a):** a reshuffle is an audit step with a reason, written in the audit recipe.
- **Option (b):** it stays a setting of the plot without a reason, and the audit log records it with the seed (D-0478 asks for "information for all the steps that are applied").
- **Option (c):** the button is removed until the study of D-0341 is done.
- **My recommendation: (b),** so that no change of a picture is without a trace, while the form of D-0341 is studied.

### Question 13. Comparisons on dates in the Filters panel.

- **Blocks:** nothing large (row V12).
- **Option (a):** as built: every comparison and "between" on a date.
- **Option (b):** a list of values only, as the rule file says.
- Reopens: nothing; D-0061 refused comparisons on TEXT and said "every type must be usable".
- **My recommendation: (a):** dates have an order, and a period ("between two dates") is a common filter.

### Question 14. Which tiers may a table that no plot reads have?

- **Blocks:** the viewing of such tables (D-0457 lists it as not decided) and, under form 3, a table read only by a derived table (the panel found that the check refuses its tier 2, code J14).
- **Option (a):** tier 1 only, as built (the check refuses tier 2 steps there, codes S07 and J14).
- **Option (b):** tier 2 is allowed, shown in the preview and exported.
- Your words of D-0451: "at least t1 is also part of a lineage - T1+T2 and T1+T2+T3".
- **My recommendation: (b),** after your words and the panel's finding; the check's codes S07 and J14 then change.

### Question 15. Does the recipe check give an advice when the kinds of table look mixed up?

- **Blocks:** nothing large. D-0511 lists it as not decided. Two facts that the check can read exactly, by block, from the recipe:
  - (i) a table in `additional_datasets_schemas` (the look-up tables) that declares an entity key: on the demo it would name `VirulenceFinder`, the table you want moved (D-0513);
  - (ii) a recipe whose tables declare an entity key but that has no `metadata_schema`.
- **Option (a):** an advice (never a refusal) for (i) and (ii), with "Suggestion:" (D-0099).
- **Option (b):** no advice; the good-practice page only.
- **My recommendation: (a).** Both are exact facts of the recipe, and (i) would have found the demo's case by itself.

### To read, not to choose

- The three sentences for the format specification (D-0513), proposed at the end of section 2.1 of `PARTS_TABLES.md`.

---

## 6. A build order in slices

Each slice replaces one part completely: after it, no part exists twice and nothing old is kept "for compatibility". For each: what you can do after it that you cannot do today; the conflicts of section 3 it closes; the questions of section 5 it needs; the tests that prove it, as behaviour a user sees on the demo recipe. **NO ANSWER NEEDED** marks a slice that could start at once.

**Slice 0 — the records agree with each other. NO ANSWER NEEDED.**
- What: a scribe corrects what section 3.18 lists (the mode switch of D-0361 against D-0505 and D-0506; the states of D-0486 and D-0358; the rule texts out of date), adds to the ledger that D-0508 states the new default of D-0316 (your words of D-0501: "there is nothing wrong in changing my decision"), and checks every recorded text for "sample" as a fixed word (D-0512).
- After it: an agent who reads the records finds what you decided, not what was true last week.
- Closes: 3.18. Tests: none (records); a reviewer compares each correction with the ledger line it cites.

**Slice 1 — the exploration filters follow the table. NO ANSWER NEEDED.**
- What: the key of an exploration filter holds the table viewed and its stage instead of the open plot (D-0506, D-0505); everything else of the Filters panel stays.
- After it: on the demo, filters set on the table of `mlst_bar` stay when you open `year_distribution` (same table, `MLST_with_metadata`); they are cleared, with the notice, when you open `virulence_bar` (table `ST22_Anchor`); a switch to Audit mode still clears them (D-0361).
- Closes: 3.4. Tests: these three, in the browser; a small test recipe where a plot has its own tier 3 steps (its T3 is another table, so the filters are cleared).
- Order: after the branch of D-0504 is merged (the same file; D-0505 says "it follows the build of D-0504").

**Slice 2 — an upload never replaces a recipe. NO ANSWER NEEDED.**
- What: HOME's recipe upload refuses a file name that exists, with a plain line (D-0390).
- After it: uploading `1_test_data_ST22_dummy.yaml` again is refused and the file is unchanged; a new name is added.
- Closes: 3.14. Tests: those two (the file's hash is equal before and after the refused upload). Not in this slice: where an upload is written (the deployment specification) and the name_date rule at load (D-0441, open).

**Slice 3 — one representation of an audit step: the audit recipe. NO ANSWER NEEDED.**
- What: HOME writes each step into the audit copy of the library, in the decided form (D-0332: `audit_steps`, `audit_comment`, the id), at the place where it writes today (the plot's own tier 3, the line "this plot only" of D-0346), through today's dialog until slice 4 replaces it. The session holds the audit recipe in `audit/` with its plain text file and its record (D-0423, D-0333); a hand-edited audit recipe is refused at reopening (D-0331); "Remove step" removes one step (D-0314); a session of an edited original is refused (D-0362, through `audit_of`, D-0339). Removed in the same slice: HOME's node store, the flat list and the `__legacy__` reader of the session file, the stale comments, the title "My Adjustments".
- After it: you do what you do today, but your session holds an audit recipe you can open and read, a proof against hand edits, and a real "Remove step".
- Closes: 3.8 (HOME part), 3.9, 3.12, part of 3.5. Tests on the demo: a filter on `mlst_bar` with a reason gives `audit/` with one step in `mlst_bar`'s tier 3 `audit_steps` and its `audit_comment`; the copy minus its audit steps equals the original (D-0040); an edited byte gives a refusal at reopening; of two steps, one removed, the other stays and the plot follows; an edited original recipe gives a refused session with the plain line.
- Information: slices 3 and 4 could be one; they are apart so that each replaces one part, and today's dialog is only pointed at the new representation, not extended.

**Slice 4 — the Create audit step dialog. Needs questions 1, 2, 3, 4 and 5.**
- What: the dialog replaces the propagation modal. Places at tier 1, tier 2 and tier 3, found by the lineage walk of the library, which becomes live; the default ticks (question 1); the later places (question 2); the number at each place (question 3); the reach (D-0346, D-0447), "table changed" and "picture changed" (D-0318), the notes (D-0477, D-0473) and the red lines with "YET" (D-0460, D-0454); "remove from all the data" with untick (D-0415, D-0416, D-0498, D-0499, D-0500); the entity key and the join columns as two lists (D-0313); data-agnostic words (D-0512); after Apply, the before-and-after comparison (D-0477) and the count of question 4; the audit log with the warnings (D-0478, question 5). The one pure function of the shared graph that gives the path up and down of a table is built here, for the drawing of the propagation. Removed in the same slice: the modal, its per-plot copies, the library's three lists of 3.3, the T3-only texts.
- After it: on the demo, from `mlst_bar` you remove a sample at the place you choose; before confirming you see the places, their reach, the numbers and the notes; after applying you see what changed; you can remove a sample from all the data and keep it in the quality results (D-0499).
- Closes: 3.1, 3.2, 3.3, 3.5 (the T3 texts), 3.10, 3.15, 3.16. Tests on the demo: each line of the table of section 4.1, as numbers the test checks; the D-0499 case; the left-join note on a small recipe; a red line for an anti join (small recipe); a drop of a join key written at a tier 1 and refused by place (D-0358); the log holds every warning shown; no screen text names "sample" as a fixed word.

**Slice 5 — the export of an audit. Needs question 7.**
- What: two ticks and one button (D-0298) and the raw-data line beside the tick (D-0301); the reproducibility part with `original/`, `final_audited/` and the data once, and a README that says which part is which (D-0490, D-0492; folder names not decided: "something like that"); the original recipe and the original plots as question 7 says; the audit recipe, its record and its log (D-0324, D-0333, D-0478); `decision_hash` retired (D-0345); the bundle import writes into the user's own place under a name_date and refuses an existing name (D-0435). Removed: the translator's fork of a join (`t3_translator.build_mode2_recipe`) and the "not engine-replayable yet" notice.
- After it: an export of an audit can be re-run from either part; its record shows the audit recipe was not changed by hand; its log shows what you were warned of.
- Closes: 3.13, 3.8 (export part), 3.5 (the export notice). Tests on the demo: an export with one audited step holds both parts and the record and the log; the re-import verifies both parts, including the hash of the audit recipe (today "not_checked"); an export with no audit step has no `final_audited` part, and the README says so.

**Slice 6 — the report by groups. NO ANSWER NEEDED for the structure.**
- What: "# Results" with one "## <group>" and one "### <result>" per result, then "# Technical" (D-0491); headings from `ui_label` (D-0484); the report stops reading `ui_title`. The points that D-0491 leaves open (an intro line, an empty group, id or label in five places, the audit trail grouped or flat) are proposed with it (`tmpAI/coordinator/report_by_group/PROPOSAL.md`).
- After it: the report of the demo reads by the 5 groups you see in HOME.
- Closes: the report part of 3.13. Tests: on the demo the report has 5 groups and 17 plots under them; every heading is a `ui_label`.

**Slice 7 — the names pass.** Needs the open cases of its dry run (a group `ui_title` whose text would be kept nowhere; a plot `ui_title` that differs from its figure title outside the demo, D-0484). One pass per file kind, by the migration script (D-0407, D-0436). Closes row N1. Tests: the proof tests of D-0411 (the two customized deployments start, banner and contact shown) and a search that no removed key is read anywhere (D-0409).

**Slice 8 — the story of the data in HOME: the picker. Needs questions 6, 8 and 11.**
- What: "open a table by its name" in the data preview; the picker as an outline (D-0508: "I like the idea of outline at the base") built on the function of slice 4; the tables no plot reads reachable (D-0457); the branches with the row counts and hidden columns of D-0488 merged first.
- After it: on the demo you open `MLST` after its tier 1, `ST22_Anchor`, `Quality_metrics`; you see where a table comes from and what uses it.
- Closes: rows V2, V3, V4, V8. Tests: on the demo, each of the 6 tables no plot reads opens; the badge names the table; from `MLST` the outline shows 3 joined tables and 4 figures (the picker review's count).

**Slice 9 — a table as a result. Needs question 9** (and the names of D-0485 and D-0487). Closes rows S7, X7, and C2 on screen. Tests: the panel's slice of the demo (a summary of samples per country and year shown as a table and as a plot, with equal numbers).

**Slice 10 — the rules of the recipe format.** The check that a join with the metadata is a tier 1 step (D-0510: "A I think for now"): **NO ANSWER NEEDED** for the rule, the words of the refusal stay PROVISIONAL until you read them. The good-practice page with what is decided (D-0461, D-0462, D-0486, D-0498, the three gotchas of D-0508): **NO ANSWER NEEDED**; the list of operations to avoid waits for the catalogue of uncertainties (D-0464). The three sentences of the format specification: your reading of the proposal. The advice of question 15. The move of `VirulenceFinder` in the demo: your word on who makes it and when (D-0513, D-0373). Tests: a small recipe that joins the metadata in tier 2 is refused with a plain line; the demo passes.

**A possible order:** slice 0; slices 1 and 2 beside it (small, independent); slice 3; slice 10's decided parts at any time; slice 4 once questions 1 to 5 are answered; slice 5 after question 7; slices 6 and 7; slice 8 after questions 6, 8 and 11; slice 9 after question 9.

---

## 7. What this document did not check

- **Code I did not read myself.** Every BUILT cell marked [collected] in `PARTS_TABLES.md` comes from the two files of 2026-11-22 (`BUILT_audit_lineage.md`, `BUILT_format_export_names.md`); I did not reopen those lines. I read myself: `app/handlers/home_theater.py:327-348, 485-518, 1476-1480`; `app/handlers/filter_and_audit_handlers.py:150-155, 172-180, 1002-1008, 1044-1068`; `app/modules/t3_audit_engine.py:69-73`; `libs/utils/src/utils/step_effects.py:64-75`; `app/handlers/ingestion_handlers.py:36-55`; `app/handlers/export_handlers.py:60-74, 386-392, 675-692`; `libs/utils/src/utils/recipe_graph.py:606-632`; `libs/utils/src/utils/recipe_tiers.py:28-44`; `app/modules/orchestrator.py:798-812`; `app/handlers/data_import_handlers.py:196-212`; the header and imports of `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py`; the demo recipe's main file, its tier files of the joins and four plot files.
- **Ledger lines.** I read myself the lines that carry weight in sections 1, 3, 4 and 5 (D-0016, D-0021, D-0022, D-0102, D-0146, D-0179, D-0192, D-0194, D-0197, D-0198, D-0224, D-0310, D-0311, D-0313 to D-0316, D-0322, D-0324, D-0327, D-0332, D-0333, D-0344, D-0346, D-0347, D-0355, D-0359, D-0361, D-0363, D-0389, D-0415, D-0416, D-0446, D-0447, D-0451, D-0457, D-0460, D-0477, D-0478, D-0485, D-0487, D-0489 to D-0492, D-0496, D-0498 to D-0501, D-0505 to D-0513). Every other number is quoted from the collected decision files, which cut the lines but do not change them; D-0371 in particular was not re-read.
- **D-0510 to D-0513** are in the ledger of the main working tree, not yet committed on `dev`; they could still change before they are committed.
- **The run of section 4.1** used one sample (`10668076`, present in all 27 tables that hold the key), the library's audit copy and audit run (as the trial did), not HOME's screen; plot tables were compared as whole tables. Another sample, present in fewer tables, was not run. The 19 places of "(b) remove from all the data" are my list, made from the recipe. The case "a computation over all entities in tier 1 after the join" was run only on the trial's small synthetic recipe.
- **Nobody ran a browser** for this document; no dialog exists; no wording was seen on a screen.
- **Other shipped recipes** were not checked for D-0510 (a join with the metadata in tier 2) or for D-0513 (a results table among the look-up tables); D-0513 asks for that check before anything is moved.
- **Decision entries outside the scope:** I read every entry of the three decision files except D-0256 to D-0280 (themes, formulas, recipe arguments; plot components are out of scope). Of the ledger's list "Asked, not decided" I searched only for a few words.
- **Not read, as instructed:** `tmp.md` and `tmpAI/agent_channel.md`.
- **One slip of method:** I used the system `python3` once, for a text replacement in this document (three question numbers), against the project rule that only `./.venv/bin/python` runs; no code or data was touched.
