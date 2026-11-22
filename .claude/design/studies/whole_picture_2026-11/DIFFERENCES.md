# The differences, the records, and where your decisions meet (2026-11-22, version 2)

Companion of `WHOLE_PICTURE.md` (same folder). This file holds the full list that part 5 of the main document sums up in four points.

**How to read it.** Part A lists every difference between the app on `dev` and your decisions: 27 points. Part B lists what is wrong in the records themselves. Part C lists where two of your decisions meet. Part D lists the pairs examined and found to hold together. Each point of part A says what the app does, what you decided (your words, with the ledger number), what a user sees, the kind, and what closes it. "Question N" points to part 8 of `WHOLE_PICTURE.md`; the builds named are in `BUILD_ORDER.md`.

**Labels.** [read] = read in the code on 22 November, by me or by the author of version 1. [collected] = taken from the files collected for this study on 22 November (`BUILT_audit_lineage.md`, `BUILT_format_export_names.md`). [review] = confirmed by the review of the code claims (`tmpAI/coordinator/whole_picture/REVIEW_built.md` of the main tree). [run] = run on the demo recipe, with the source named.

**Kinds** (as in `PARTS_TABLES.md`): CONTRADICTS (the code does the opposite of a decision); BUILT BUT OLD (a behaviour from before a decision that replaced it); BUILT BUT PROVISIONAL (a builder's choice you never took); NOT BUILT; and two kinds found by the reviews: UNREACHABLE (code that no screen reaches) and DEFECT (wrong whatever is decided).

---

## A. The differences between the app and your decisions (27)

### A1. An audit step is written only at the plot's table (tier 3)
- **The app.** "Send to Audit" exists only in Audit mode while T3 is viewed (`app/handlers/filter_and_audit_handlers.py:152-155`, marked "P-B3, PROVISIONAL") [read, review]. Each step belongs to one plot and is applied to that plot's tier 3 table (`app/modules/t3_audit_engine.py:771-791`) [collected, review]. The screen says "Audit steps apply to the plot's table (T3) for now." (`app/handlers/home_theater.py:1479`) [read].
- **Decided.** "We had said we can send at each tier - so we need to send the correct tier" (D-0507); "the audit steps can be added at the end of each T1 - T2 - T3 (for now)" (D-0146); "That is the choice of the user - because the user decide the scope" (D-0355).
- **A user sees.** She cannot remove an entity before a join, nor at a table that no plot reads. A step for several plots is written once per plot.
- **Kind.** CONTRADICTS (marked PROVISIONAL in the code).
- **Closes.** Replaced by the Create audit step dialog. Needs questions 1 and 3 to 12.

### A2. The propagation modal instead of the dialog with tick lines
- **The app.** "Apply to:" with "This plot only" (selected), "All plots", "All plots except…" (`filter_and_audit_handlers.py:1056-1066`) [read, review]. Confirm writes one copy of the step per chosen plot. A plot whose table lacks the column is skipped, and the modal says "A skipped plot is NOT filtered — it shows the unfiltered data." (`:1044-1047`) [read].
- **Decided.** The dialog lists distinct tables as tick lines with their reach: your answer "A" (D-0316; the words of the option are the review session's), "The choices need to evaluate the reach" (D-0346), "back forth and back again" (D-0347); tables that no plot reads are lines: "Yes, its me that was too limited i think you under. We must modify" (D-0451); a consequence is shown, never ticked (D-0446).
- **A user sees.** A choice of plots, not of places. Two plots that read one table get two copies of one step.
- **Kind.** BUILT BUT OLD. The rule file (`ui_implementation_contract.md` section 12g.4) still calls it "what is built today".
- **Closes.** Replaced with A1, in the same build, with no time where both dialogs exist.

### A3. The default ticks of the built modal and of the library
- **The app.** The modal starts on "This plot only" (`filter_and_audit_handlers.py:1065`) [read]. The library `libs/utils/src/utils/remove_from_all.py` writes at every table it reaches (`apply`) [collected].
- **Decided.** First every place ticked: "I think that I would choose A as default : because then all the boxes follow the lineages - so it show clearly the extend of where it will be removed" (D-0194), "5. A (we might want to change this behavior after testing)" (D-0359). Then your new default: "but ok we tick low (early) near the original table - so by default it is propagated in the lineage" (D-0508; the ledger line says that it states your new default and that D-0316 is not edited).
- **A user sees.** Neither default.
- **Kind.** BUILT BUT OLD.
- **Closes.** With A1. Which places are "earliest" is question 1; the cases around it are questions 3 to 6. One function gives the default ticks to both dialogs (the architect's advice in the review of the default ticks, `tmpAI/panel/default_ticks/TABLE_FOR_THE_OWNER.md`).

### A4. The library's statements about tables where no step is written
- **The app.** On `dev`, `remove_from_all` lists the tables where the value "may stay" (`may_stay`) and `apply` returns `may_differ` and `not_written` [collected]. On the held branch `task/remove-from-all-ticked`, at its tip (`95b6285e`) [read: `git show`], the list `stays_by_choice` of the first commit was replaced by `unticked_places`, with three kinds: "stays", "removed upstream", "cannot say", read from the join kinds of the recipe. The branch is on hold by your order (D-0507).
- **What the runs showed.** On the demo, the six "may stay" of `dev` were false alarms: the entity was gone from all six (`tmpAI/panel/default_ticks/TRIAL.md`, Q6) [run]. Both versions of the branch made false statements (`tmpAI/coordinator/whole_picture/EVIDENCE_untick_branch_reviews.md`) [run]: the first told "stays" for a table built from a ticked table (untick `FastP_with_metadata` alone: told "stays", the entity is gone); the second told "stays" for `ST22_Anchor`, a large join that keeps only the genes of a look-up list, when the two entities were gone (2 rows before, 0 after), and "removed upstream" where the entity was still there. A statement about a table where no step is written cannot be read from the recipe; only a run measures it.
- **Decided.** "I would just shows the differents where applied and no per table warnings about downstream effects" (D-0501); "Id rather the check is more where you apply it - knowing it will affect the downward recipe than actually trying to capture the removal of something that by default should not exist" (D-0508).
- **A user sees.** Nothing yet: no screen shows these lists. They are code a builder would take again.
- **Kind.** CONTRADICTS (library on `dev`; held branch).
- **Closes.** Removed with A1. What replaces them is your choice: questions 7 and 9.

### A5. Which tables the walk offers, and which start ticked, are builders' choices
- **The app.** The walk of the lineage (`libs/utils/src/utils/lineage_walk.py`, its header, points P1 and P4, marked PROVISIONAL) [read] returns two groups of places: "lineage" (above and below the chosen place) and "join_linked" (linked by a join on the key). Which groups are offered is the builder's choice. A table that no plot reads is a line, and whether it starts ticked is not decided.
- **Decided.** "O1 - I mean we need the lineage of where it was selected (eg. T3) then all ticks by default" (D-0415); "So basic lineage is up to it can only go backwards when on its way up or forward when on its way backwards" (D-0451). NOT decided: which groups of tables are offered (the coordinator's note in D-0355; D-0415: "Not decided: the other filters (the tables joined on the key)").
- **Why it matters.** It decides whether, from `mlst_bar`, the original tables FastP, Quast and Bracken are places. If they are, reading A of question 1 empties no metadata (reasoned, not run). As I read D-0451, they are not in the lineage of `mlst_bar`.
- **Kind.** BUILT BUT PROVISIONAL (library).
- **Closes.** My reading of D-0451 confirmed or corrected by you before the dialog is built (it is stated in part 6.1 of the main document).

### A6. The exploration filters are tied to the plot, not to the table
- **The app.** The key of a filter is (recipe, mode, data choice, source table, open plot) (`app/modules/t3_audit_engine.py:69-73`) [read, review]. The plot is in it by a builder's choice ("P-B2, PROVISIONAL", `filter_and_audit_handlers.py:168-174`) [read]. The notice names the cause "you opened another plot (its table can differ)" (`t3_audit_engine.py`, `_VIEW_CAUSES`) [read].
- **Decided.** "ok, so I do not understand why there is more logic bucause the filter is associated to the table and not the plot" (D-0506); "point c - C" (D-0505: a typed value is kept across plot tabs while the viewed table is the same; the words of the option are the review session's).
- **A user sees.** On the demo she filters the table of `mlst_bar`, opens `year_distribution`, which reads the same table `MLST_with_metadata`, and her filters are gone.
- **Kind.** CONTRADICTS (marked PROVISIONAL).
- **Closes.** The table viewed (which table, at which stage) replaces the open plot in the key; the cause of the notice changes with it. No answer needed.

### A7. Screen texts that say "for now" or state an old limit
- "Audit steps apply to the plot's table (T3) for now." (`home_theater.py:1479`) [read] and "To create an audit step, view T3." (`filter_and_audit_handlers.py:694`) [read]: they go with A1.
- The button title "...applies only to T3, and cannot be silently discarded once committed." (`filter_and_audit_handlers.py:674-676`) [collected]: "applies only to T3" goes with A1; "cannot be silently discarded" is arguable, since a removal shows a notice (`app/handlers/audit_stack.py:675-682`) [review].
- "...still in the Publication content, just not engine-replayable yet." (export notice, `app/handlers/export_handlers.py:1615-1620`) [collected]: goes with A17.
- "Add N filter/exclusion(s) — choose scope" (`filter_and_audit_handlers.py:997`) [collected]: no "exclusion" is ever written; goes with A2.
- The panel title "My Adjustments (Tier 3)" (`app/handlers/audit_stack.py:460`) [collected]: "My" is the word of the retired "My view" (D-0179); goes with A11.
- **Closes.** Each text with the part it describes, never alone, so that no screen text and code disagree in between.

### A8. A screen text names "samples" as a fixed word
- **The app.** "One or more nodes target a join key. Removing rows here changes which samples appear in joined plots." (`filter_and_audit_handlers.py:1002-1007`) [read].
- **Decided.** "remember we are data agnostic so sample id is the example" (D-0512).
- **Kind.** CONTRADICTS.
- **Closes.** Removed with the modal (A2). The texts recorded so far are checked for the fixed word (D-0512).

### A9. The key-drop check of HOME cannot fire
- **The app.** HOME asks the drop gate at the place `T3:<plot>`, where nothing is built after the drop, so "refused by place" can refuse nothing from HOME (`filter_and_audit_handlers.py:895-904`) [collected, review]. The gate itself is built (`libs/utils/src/utils/key_drop.py`) [review].
- **Decided.** "4. B I think it should be refused by place because eg. we can have aggregations by count in a plot where the key does not matter" (D-0358); a declared entity key follows the same rule: your answer "B" (D-0448).
- **Kind.** The rule AGREES; it is unreachable from HOME because of A1.
- **Closes.** With A1: a drop can then be written at tier 1 or tier 2, where the gate decides.

### A10. Two ways of showing and naming a lineage
- **The app.** The structure is read once, by the shared recipe graph (`libs/utils/src/utils/recipe_graph.py`); BLUEPRINT's navigator takes its structure from it (`libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py:79`) [read]. What stays double is how a lineage is shown and named: BLUEPRINT's roles and colours (`trunk`, `add`, `meta`, `wrangle`, `branch`, `plot`; `blueprint_mapper.py:71`), its rail and its tube map, bound to BLUEPRINT (`app/src/ui.py:134`, `:288`) [collected]; and the walk's places (source, T1, T2, T3) for the audit (`libs/utils/src/utils/lineage_records.py`). The export's "Data Lineage" section is drawn from the navigator (`export_handlers.py:1703`) [collected].
- **Decided.** One source of truth (D-0065, D-0031); the story of the data (D-0508: "YES the story of is what I want to show - this is why I wanted the lineages"); BLUEPRINT is rebuilt later (D-0494).
- **A user sees.** No lineage in HOME; one graph in the export; another vocabulary in BLUEPRINT.
- **Kind.** Two vocabularies for one thing.
- **Closes.** One function of the shared graph gives the groups of linked tables, the path up, the path down and the stage of each node. HOME's picker (if you choose one, question 13) and the dialog's drawing (question 3) use it; BLUEPRINT moves onto it in its rebuild.

### A11. Three representations of one audit step
- **The app** [collected, review]. (a) HOME's node, kept in the session state and the session file (`app/modules/session_manager.py:56-106`). (b) The library's audit copy, the decided form (`libs/utils/src/utils/audit_copy.py`); its only callers, `remove_from_all.py` and `plan_composer.compose_candidate_plan_book`, are themselves called only by tests; `app/modules/audit_run.py` has no caller outside the tests. (c) The export's fork of each plot's join, named `<join>__t3_<plot>` (`libs/blueprint_arch/src/blueprint_arch/t3_translator.py:197-290`, `export_handlers.py:1561-1564`) [read].
- **Decided.** "the original recipe is never edited during auditing steps ... Audit only add steps ... Full recipe edit is only in blueprint" (D-0102); "Audit add steps to a copy of an original_recipe : the audit_recipe," (D-0143); the form: "Id go for F4 - seems easier also to see what has been modified or not" (D-0332); "when audit steps have been added the audit recipe is the truth - so the export must contain the recipe of the audit" (D-0324).
- **A user sees.** The reason under two key names (`reason` in HOME, `audit_comment` in the copy); in the reproducibility part, tables she never wrote (`<join>__t3_<plot>`).
- **Kind.** BUILT BUT OLD.
- **Closes.** One representation: HOME writes the audit copy, the session holds it, the export writes it. Two consequences (`BUILD_ORDER.md`): HOME's plot and table then come from an engine run of the audit copy; the session file changes form, and older session files are refused (D-0312: "A - best to clean all old sessions").

### A12. The session file keeps two older forms of the audit steps
- **The app.** A flat list "kept for bw compat" and a reader of a `__legacy__` bucket (`session_manager.py:509-523, 572-576`) [collected].
- **Decided.** "A - best to clean all old sessions" (D-0312); no compatibility shims (`.claude/rules/rules_legacy_management.md`).
- **Kind.** BUILT BUT OLD.
- **Closes.** Removed with A11.

### A13. The undo control
- **The app.** A trash button per step, titled "Delete this audit node (linked: removes from all plots)", removes every copy of that id from every plot (`app/handlers/audit_stack.py:530-534, 627-682`) [collected]. The library's `remove_step` (one step of an audit copy) has no caller [collected].
- **Decided.** ONE control, "Remove step": the user picks any step and removes it; your answer "B" (D-0314; the words are the review session's).
- **Kind.** BUILT BUT OLD.
- **Closes.** With A11.

### A14. The key of the audit: one list where two are decided
- **The app.** One list, the join keys, drives the warning of A8 (`session_manager.py:125-135`) [collected].
- **Decided.** Two lists, "the entity key" and "columns used to join": your answer "C" (D-0313; the words of the option are the review session's).
- **Kind.** BUILT BUT OLD.
- **Closes.** With A2: the dialog names the entity key and shows the join columns as information, in data-agnostic words.

### A15. The Reshuffle writes a new seed with no reason
- **The app.** In Audit mode a click writes a new seed into the plot's overrides, with no reason and no Apply; it is exported in the report and in `t3_steps.yaml` (`home_theater.py:877-899`; `export_handlers.py:1076-1089`) [collected, review].
- **Decided.** "A - but then we need to be able to add it as a step at the correct place in audit", and "when the user is happy with the reshuffle a seed step with the reshuffling needs to be written" (D-0341). NOT decided: how.
- **A user sees.** A new picture; the reason for the change is nowhere.
- **Kind.** BUILT BUT PROVISIONAL, and short of your words that a seed step is written.
- **Closes.** Question 17, after the study you asked for in D-0341.

### A16. A session saved before its recipe was edited is opened
- **The app.** It shows "Session was saved against a different data analysis recipe version. Audit step may not match current columns." and opens the session (`app/handlers/session_handlers.py:594-602`) [read].
- **Decided.** "so I would refuse - I would explain that the original recipe has been modified and that it needs to reanalyze and add the audit steps where they are done" (D-0362).
- **A user sees.** Her old steps applied to a recipe that is no longer the one they were made on.
- **Kind.** CONTRADICTS.
- **Closes.** A refusal with a plain line, once the session holds the audit recipe and its `audit_of` fingerprint (D-0339). No answer needed.

### A17. What an export of an audit holds
- **The app** [read at `export_handlers.py:1510-1570`]. `t3_steps.yaml` holds each audit step with its reason and its date. When the reproducibility box is ticked, the bundle holds a recipe made by `build_mode2_recipe`: each plot's join forked with the steps, plus the seeds. `effective_run.yaml` carries a hash of HOME's own step list [review]. With no audit step, that recipe IS the original recipe plus the seeds [review].
- **Absent when an audit exists.** The original recipe; the audit recipe; its record with the hash; the log of added and removed steps, with the initials and the warnings shown.
- **Decided.** "when audit steps have been added the audit recipe is the truth - so the export must contain the recipe of the audit" (D-0324); "1. yes must." (D-0389, the original recipe); two parts: "so we need to have the reproducibility bundle have 2 parts "original" "final_audited" something like that" (D-0490); the data once: "B." (D-0492); the log: "it is then actually not optional anymore to add the log for the audit to the export" (D-0478); the record: your answer "A" (D-0333).
- **A user sees.** An export of an audit that cannot be re-run from the original recipe; nothing that proves its recipe was not edited by hand; no record of the warnings she was shown.
- **Kind.** BUILT BUT OLD (the fork); NOT BUILT (the rest).
- **Closes.** The export of an audit (`BUILD_ORDER.md`). Questions 15 and 16 first.

### A18. The export's mode control
- **The app.** One check box, "Also include a reproducibility/reimport bundle", with a long help text (`export_handlers.py:675-692`) [read]; the raw-data warning is a notification shown after the export (`:1604-1612`) [collected].
- **Decided.** Two ticks, "Publication" and "Reproducibility", and one Export button: "For the export one button apply A" and "then we can select both at the same time" (D-0298); a short raw-data line beside the tick: "a" (D-0301).
- **Kind.** BUILT BUT OLD.
- **Closes.** With A17.

### A19. The report structure
- **The app.** All sections are `##`; one flat `## Plots` with `### <name>` per plot (`export_handlers.py:1813-2112`) [collected]; the name is `ui_title`, else `ui_label`, else the id in title case (`export_handlers.py:390`) [read].
- **Decided.** A report with "# Results", by group, before "# Technical" (D-0491); headings from the group's and the plot's `ui_label` (D-0484).
- **Kind.** BUILT BUT OLD.
- **Closes.** The report by groups (`BUILD_ORDER.md`), before or with the names pass, because it stops reading `ui_title`.

### A20. The bundle import
- **The app.** The import writes the recipe into the app's recipe folder under a new unique id, `<id>_imported_<time>`, and never overwrites a file (`app/modules/bundle_importer.py:252-273`) [read]. It never checks the hash of the audit steps ("not_checked") [collected].
- **Decided.** The recipe and its data go into the user's own place, under a name of the form name_date, and an existing name is refused (D-0435: the four points are the review session's restatement, which you answered "Yes"); your words: "the user will save under a new name,.so the old copy is likely in his system file - but the app does not do it".
- **Kind.** BUILT BUT OLD.
- **Closes.** With A17.

### A21. The recipe upload code that no screen offers
- **The app.** `app/handlers/ingestion_handlers.py:38-55` copies every uploaded `.yaml` into the recipe folder, over a file of the same name, and then says "Ingestion complete." [read]. But no user space mounts its button or its file input: `app/tests/test_ingestion_handler_reachability.py` records it as dead code, and records that the handler would stop the app if it ran (it passes a display name as a launch value) [read, review].
- **Decided.** "upload under same name refused" (D-0390); "Yes off unless deployment place required it." (D-0440); "a warning if trying to write on a file name name - the user delete in his file system or choose a new name" (D-0437); an overwrite control "only in its own directory" (D-0394); a typo fix may replace the previous file (D-0393, point 2); the write test at start "off by default" (D-0441); one deployment specification (D-0417, D-0418).
- **A user sees.** Nothing today.
- **Kind.** UNREACHABLE (and BUILT BUT OLD if it were ever mounted).
- **Closes.** Question 24: remove the code, or rebuild it under a declared upload place. Not without your answer.

### A22. The data preview's count of rows
- **The app.** With "All rows" off, the grid's own line reads "Viewing rows 1 through 9 of 100" for a table of 1000 rows (`home_theater.py:1692-1702`; the same call run in a scratch app, `tmpAI/panel/tables_as_results/trials/REPORT.md`) [run by that trial, not by me]. The sentences "N columns hidden" and "Showing 100 of N rows" are on the branch `task/home-preview-rows-columns`, not on `dev` [read: the branch exists].
- **Decided.** "flag 3 - hah ok but we can say that xx columns are hidden and the user can add those again", and "Those sentences were supposed to be added in every preview I think" (D-0488).
- **A user sees.** "of 100" for a table that has more rows.
- **Kind.** NOT BUILT on `dev`; a misleading line today.
- **Closes.** The branch, after its review. No answer needed.

### A23. A plot id written in two groups is not refused
- **The app.** The plots of all groups are put in one list by id, so a second entry with the same id silently replaces the first (`libs/utils/src/utils/recipe_tiers.py:152-161`) [read]. The recipe check compares plot ids across recipes (X5, `recipe_check.py:1288`) [read]; inside one recipe, by the recipe-redesign proposal's run, it reports nothing, and the load gate refuses such a recipe only through an internal fault (`tmpAI/panel/tables_as_results/refined/PROPOSAL_FOR_THE_OWNER.md`, flag 6) [run by the proposal, not by me].
- **Decided.** "No silent error that is the rule." (D-0050).
- **Kind.** DEFECT (wrong whatever form is chosen).
- **Closes.** A plain refusal by the recipe check, tests first. No answer needed.

### A24. The defaults when a recipe opens: a builder's choice
- **The app.** Exploration, and the data choice on T3, marked "PROVISIONAL P-B1" (`app/src/server.py:143-147`) [collected].
- **Decided.** Nothing for plots. For a table result: "maybe the result should be the default at opening but the user must still be able to navigate" (D-0487).
- **Kind.** BUILT BUT PROVISIONAL. **Closes.** Question 18.

### A25. Comparisons on dates: a builder's choice
- **The app.** A date column gets every comparison and "between" (`t3_audit_engine.py:321`, "PROVISIONAL FILTER-PICKERS-1 point 2") [collected]; the rule file says comparisons on dates are "not decided and not offered".
- **Decided.** For text only: "I think we will not need greater less than comparison for text ... I would go for not offered" (D-0061).
- **Kind.** BUILT BUT PROVISIONAL; code and rule text disagree. **Closes.** Question 20.

### A26. The words of the stages: a builder's choice
- **The app.** "Source", "T1", "T2", "T3" with tooltips, PROVISIONAL (`home_theater.py:1169`) [collected].
- **Decided.** Nothing.
- **Kind.** BUILT BUT PROVISIONAL. **Closes.** Question 19.

### A27. The demo recipe: `VirulenceFinder` among the look-up tables
- **The demo.** `VirulenceFinder` (gene detection results, with the entity key) sits in `additional_datasets_schemas` beside the look-up list `APEC_STEC_virulence_genes` (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:122-146`) [read].
- **Decided.** You confirmed the move: "ok. Yes "VirulenceFinder moves" ." (D-0523); you authorized an agent to make it: "angent need to move the demo recipe - authorized" (D-0524); then "we need to finalize the recipe design with the from and hyerarchy ... we had that going on - before we can do a big move on all demo recipes" (D-0525).
- **A user sees.** HOME's Data Import cannot replace the VirulenceFinder file: it offers the data tables and the metadata only (`app/handlers/data_import_handlers.py:200-208`) [read].
- **Kind.** Decided, not made; it waits for the one move.
- **Closes.** The one move of the shipped recipes (`BUILD_ORDER.md`).

---

## B. The records

### B1. T0 (its only place in this study)
Proposed by you on 22 November: "Well maybe then we need instead to be able to add some filters in the original data as T0 which would make sence instead of the beginning of T1" (D-0507). Withdrawn the same day: "revision request . no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged." (D-0509), and confirmed: "T has been removed - because we join all data sets with metadata in T1 when necesary (and not in other tiers) - and if No metadata join is needed. As we said the other data tables can be used in later joins." (D-0523). Nothing was built. Nothing to close.

### B2. Records that disagree with each other (rule H: reported, not resolved silently)
- **a. The filters on a switch of mode.** D-0361 decided it: "8 - No we had decided to clear them- Only the steps applied in the audit are kept -> but then they are writen in the recipe". D-0505 and D-0506 say, in the review session's words, "NOT decided: what a change of mode does to the filters"; the rule files say "PROVISIONAL". The code clears the filters, as D-0361 says. D-0361 governs; the records are corrected.
- **b. The semi join.** D-0486 says it is "built on branch `task/lineage-unfollowed-join-red`, in review, not merged". It is merged on `dev` (`libs/utils/src/utils/step_effects.py:68`, commit 82126831) [read].
- **c. The drop by place.** D-0358 says "Not built (the code refuses by name ...)". The drop gate by place is built (`libs/utils/src/utils/key_drop.py`) [review].
- **d. The held branch.** Any record that describes the branch's list as "stays by your choice" (`stays_by_choice`) describes its first commit; at its tip it is `unticked_places` (A4).
- **e. The right panel.** D-0383 and D-0385 say "not built"; the behaviour is built (`home_theater.py:1401-1425, 2348-2350`; `audit_stack.py:692-700`) [collected].

### B3. Rule texts out of date (none changes the code)
- `rules_data_engine.md` section 1, "The opening of a recipe (DECIDED, not built)": it is built (`app/modules/opening_build.py`, run through `app/handlers/opening_handlers.py`, imported at `home_theater.py:58, 60`) [read].
- `rules_data_engine.md`: the large-data threshold "not decided (D-0336)"; D-0363 decided it (1,000,000 rows per plot, used at `opening_build.py:41-43`) [collected].
- The aesthetic overrides described as "never applied": they are applied [collected].
- `ui_implementation_contract.md` section 12a: `developer_raw_yaml` in the list of the gatekeeper; it is removed [collected]. Same section: "the keys are not read from a file yet"; the engine reads `audit_steps` (`libs/transformer/src/transformer/data_wrangler.py:17`) [collected].
- `ui_implementation_contract.md` section 7.2: "The pure rule is `export_handlers.plot_content_rules(...)`": no such function [collected]; the three-way export scope, removed by "Maybe we should just simplify - all plots included in the export" (D-0292).
- `ui_implementation_contract.md` section 9 (Data Import): it still describes keeping the replaced file and recording it. You withdrew the kept dated copy ("so no need to have an archive under old date", D-0433) and decided no copy: "To use the correct data q8.is your b except that the rule of file name date means that we do not need to copy the old recipe and give a new name because same name unlikely to happen" (D-0434).
- `ui_implementation_contract.md` section 12g.4: "The three scope options above are what is built today" and "a join that no plot reads is not offered" (changed by D-0451).

---

## C. Where your decisions meet each other

### C1. "Tick low near the original table" and "modify at the join keeping the raw data unchanged": two readings
- D-0501: "yes the default will need to include the earliest place of each branch - which is the original data basically". D-0508: "but ok we tick low (early) near the original table - so by default it is propagated in the lineage".
- D-0509: "revision request . no T0 - as the T1 includes the join whith metadata that allows to modiffy at the join keeping the raw data unchanged." D-0510: "metada is a certain type of data - other joins could be used after but join with metadata must be done at T1 that would simplify removing of samples by key no". D-0523: "T has been removed - because we join all data sets with metadata in T1 when necesary (and not in other tiers) - and if No metadata join is needed. As we said the other data tables can be used in later joins."
- Two readings: (A) tier 1 of each original table; (B) the end of tier 1 of each table that joins the metadata, and, on a branch that never meets the metadata, the end of tier 1 of the first table its results read.
- A fact of the recipe, not a reading: the place of the metadata join plays no part in (A), because (A) writes before every join. The reason of D-0510 ("would simplify removing of samples by key") holds under (B): a step at the end of tier 1 of a joined table sits after the join with the metadata exactly when that join is a tier 1 step.
- **The runs** [run]: three runs on the demo recipe, one entity each (10668076 and 51573804, in every original file; 52676003, absent from the ResFinder file), with the real engine, through the library's run of the audit copy; first by version 1 (`tmpAI/run_scratch/earliest_place_run.py` of this worktree), then reproduced by the review of the code claims (`tmpAI/review_built/rerun.py`, `out_<entity>.txt`). All three give the same pattern:

| | (A) tier 1 of the original tables | (B) end of tier 1 of the tables that join the metadata |
|---|---|---|
| Removal started from `mlst_bar`, default ticks | 2 steps (`MLST`, `metadata_schema`). 13 plots change. The entity stays in 7 plots (6 for 52676003): in 4 whose tables never meet MLST or the metadata (`amr_heatmap`, `phenotype_genome_length_fragmentation`, `qa_l50_integer`, `qa_sequence_type_missing`), and in 3 with metadata emptied: `qc_reads_horizontal_barplot` (source, year, country), `assembly_quality_dotplot` and `miaou` (source, country; their table `Quast_with_metadata` has no year). `miaou` draws `source`: its picture changes. | Only `MLST_with_metadata` ticked: 1 step; 2 plots change (`mlst_bar`, `year_distribution`). All 13 tables that join the metadata ticked: 13 steps; 13 plots change; the entity stays only in the 4 plots whose tables never meet the metadata (3 for 52676003); nothing is emptied. |
| "Remove from all the data" | 11 steps; the entity is in no table and no plot. | 19 steps (the 13 joins, and the first table of the 6 branches without the metadata); the entity is in no plot; the 8 original tables still hold it at tier 1. |
| Your case of D-0499 | Untick `FastP`, `Quast`, `Bracken`: the entity stays in the 3 quality plots without its metadata, and in `qa_l50_integer`. Untick the metadata too: it stays in 9 plots. | Untick `QC_Reads_Anchor` and `Quast_with_metadata`: 17 steps; the entity stays in exactly the 3 quality plots, with its metadata; 14 plots change. |
| A computation over all entities written in tier 1 after the join | Never sees the removed entity. | Runs with it, then it is removed (the trial's small synthetic recipe: a z-score of -1.254 becomes -1.336; not rerun). On the demo such computations sit in tier 2 (`QA_population_zscore`, `QA_aggregated_no_key`). |

- **Why the metadata is emptied under (A)** [review]: a left join whose second table lost the row. In `FastP_with_metadata`, `Quast_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata` and `MLST_with_metadata` the data table is first and `metadata_schema` second (`how: left`); in `QC_Reads_Anchor` FastP is the base and the metadata is the last of three left joins; in `AR1_MLST_Serotype_Virulence` MLST is the base. Under (A) from `mlst_bar` the entity leaves `MLST` and `metadata_schema` only; `FastP`, `Quast` and `Bracken` still hold it, so the left joins keep the row with empty metadata columns. In `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit` and `QA_population_zscore` the metadata is the first table, so removing it there removes the row.
- **Limits of the runs** [review]: the place lists of (A) and (B) were written by hand in the scripts, not derived by a rule (see A5 for why it matters); "the plot holds the entity" is counted for the 16 of 17 plots that have the key column (`qa_aggregated_no_key` has none); the library's run, not HOME's screen; three entities.
- **The demo, read in its files** [read, review]: 13 tables join `metadata_schema`, all in tier 1. Four plots read a table that never meets the metadata. `Quality_metrics` and `Detailed_summary` are read by no plot and no join. A scan of 141 loadable recipe files (14 with joins) found none that joins the metadata in tier 2 [review].
- The question: question 1.

### C2. All places ticked (D-0194, D-0316, D-0359) and "tick low" (D-0508)
- D-0508 states your new default after the review you ordered in D-0501 ("And yes it reopen D-0316 - A would think A ... there is nothing wrong in changing my decision I think"); the ledger line says so and leaves D-0316 unedited. Resolved.
- The hole: your reason of D-0194 ("so it show clearly the extend of where it will be removed") moves to the drawing of the propagation: "so maybe lineage should be represented as a propagation eg. original -> T1 -> T2 so the user sees that it affect the next one" (D-0508). Whether a later place is still a line you can tick is not decided. Questions 3 and 4.

### C3. Tick lines with their reach (D-0346, D-0447) and the lineage "represented as a propagation" (D-0508)
- Both can hold: the reach is the propagation of a ticked line, counted. The hole is the same as in C2. Question 3.

### C4. Keep the poor-quality entity in the quality results (D-0499) and the proof that no statement can be read for a table where no step is written
- D-0499: "yes the user may unthink he is responsible of its choice. eg case : he wants to show the poor quality sample for the quality results but remove the bad sample from all other results."
- The two reviews of 22 November: a sentence about a table where no step is written was false on the demo and on small recipes (A4).
- What the runs add (C1): under (A) your case leaves the entity in the quality results without its metadata, and nothing in the recipe tells the dialog so; under (B) the result is what you described.
- The question it raises: how the user checks, after Apply, that her choice did what she wanted. Questions 1 and 9.

### C5. The data choice of the open plot (D-0310) and a picker that opens any table (D-0496, D-0457)
- D-0310: "the filters must show what is true in T3 when viewing T3, and what is true in T1 when viewing T1" (your words relayed with your answer "B").
- D-0457: "1. Must be and yes must be viewabøenin the data preview." D-0496: "No I think my idea is more an independent lineage picker ... so you can pick every original data and see all lineages that goes from there". D-0518: "imaging the case where there is something to remove (filter) that is not seen at the mlst_bar level ... I am just wondering of how to make it navigate."
- The hole: what "Source, T1, T2, T3" mean when the table viewed is not the open plot's, and from which table "Send to Audit" starts. D-0506 already makes the filters follow the table. Whether a picker is built is not decided (D-0496). Questions 13 and 14.

### C6. A result is a plot or a table (D-0485) and the recipe form, not confirmed (D-0496)
- D-0485: "so a plot entry actually should be a result_entry with either plot or table no? last tier of entry also can be T3=T2=T1 (so the fall back mechanism)"; "e : we need to follow the recipe --- so do not fix all tiers need to be functional."
- D-0514: "No Tier 3 is not a plot - T3 is the data that goes into a plot ... its still data". D-0516: "Id like the tier 3 to be defined in the same way tier 1 and 2 are defined - it does not makes sence in your example because tier 3 is dedined after the definition or results - it should occur before". D-0517: "yes we need the `from:` this clarifies but still the hiearchy is unclear of where to place it."
- D-0496: "wait for the panel I just said I might have more questions after". D-0525: the recipe design is finalized before one big move on all demo recipes.
- The hole: until the form is chosen, it is not known where a summary lives, and so where a "this result only" step is written for a table. Question 2; the review of the proposal: `RECIPE_REDESIGN_REVIEW.md`.

### C7. "Remove from all the data" (D-0415, D-0416) and the default ticks (D-0508)
- D-0415: "But I want an option that is independent of the lineage itself that allow selection all the data T1 where eg. the sample is selected." D-0508: tick low.
- Under (A) the earliest places are the 11 original tables, and the result equals ticking all 27 (the trial and C1). Under (B) there are 19 places. If one function gives the default ticks to both dialogs (A3), question 1 settles both.

### C8. The comparison in layers (D-0489) and the pair "rows with this value: before, after" (question 7)
- D-0489: "For layer 1 I think will be mostly what we need, agree the full row diff on request only".
- They are two moments: the pair is shown in the dialog, per place, BEFORE confirming; the layers compare the original and the audited RESULT after Apply. At a place where a step is written the pair is counted on the stored table of that place (D-0326 builds every table at opening). They hold together.

### C9. Metadata "more a practical tric than a real one" (D-0224) and the metadata as a declared kind (D-0510, D-0511, D-0513)
- D-0224: "well metadata is one row per sample id" and "its more a practical tric than a real one"; "its easy to find which one to join, most joins are done on metadata".
- D-0510 adds where its join goes; D-0513 makes the kinds the blocks. D-0224 was about the id rule (no separate one for the metadata). No conflict; recorded so that D-0224 is not read as an argument against D-0510.

### C10. "The export always contains the original recipe" (D-0389) and "remove the recipe from the mode 1" (D-0192)
- D-0389 (20 November, the later line): "1. yes must." and "the export of original recipes should also be exported with the reason that: if you need to redo the analysis then you will need to re-upload the recipe".
- D-0192 (16 November): "I think that would be best to add the recipe to the reproducibility mode 2 - And I suggest to remove the recipe from the mode 1", and "when in audit it will be added anyway (via the audit_recipe)". The line does not say that mode 1 is the Publication part; that is my reading of D-0298 (two ticks, "Publication" and "Reproducibility", replace the two modes).
- D-0490 then puts the original recipe in the reproducibility part ("original"). Question 15.

### C11. Seeing the original and the modified plot in the export (D-0147), and the baseline in the reproducibility part (D-0490)
- D-0147: "10. In the export we need to be able to see original and modified plot."
- D-0490: "ok, I think we need to add the baseline in the reproducibility bundle then we are covered."
- Today every exported plot is the audited one. With D-0490 the original can be re-run, but no original picture is in the bundle. Question 16.

### C12. A mode switch clears the filters (D-0361) and "not decided" (D-0505, D-0506)
- A records error, not two decisions (B2 a). No question.

### C13. The notes for silent cases (D-0477) and the proof of the two reviews
- D-0477: "eg. left join keeps the rows of the second table - ensure you removed in second table if this is what you want (or something similar) - Option B".
- The reviews: a sentence about a LATER table was false when a later step dropped rows.
- They hold together if each note speaks of the place it stands on (at the join itself: "a left join keeps the rows of its first table; this table is not ticked"), never of a table further down. A rule for the words of the notes, not a new question.

### C14. "Yes warn that is good" (D-0203) and "no per table warnings about downstream effects" (D-0501)
- D-0203: your "yes warn that is good" to the review session's sentence that the dialog "warns when a value does not correspond one-to-one between nodes, for example "two values at T1 become one at T2"".
- D-0501: "I would just shows the differents where applied and no per table warnings about downstream effects".
- They hold together if the one-to-one warning is shown only between places where the step is written (ticked places), which is "where you apply it" (D-0508). Recorded so that the builder does not drop D-0203 with the downstream warnings.

### C15. The drop of a declared entity key (D-0448) and a column renamed and renamed back (D-0445), with the places of the dialog
- D-0448: your answer "B": a declared entity key is dropped by place like any key, refused only where a later join reads it. D-0445: "A - but remember the user can still decide to scope his answer to remove eg..in T2": a column renamed in tier 1 and back in tier 2 is one column.
- No conflict. They govern the places and the drop gate of the dialog (`BUILD_ORDER.md`).

### C16. The lineage colours (D-0463) and the red line (D-0460)
- D-0463: "It can pick a color that is discrimination and already in the palette - my colors were example but i like green as good." D-0460: "B of needed we try to.fimd a.solutiom later." (a line the app cannot follow is red and cannot be ticked).
- Compatible. Which colour means what is open: question 23.

### C17. One engine per tier (D-0239, D-0455, D-0458)
- A tier may name its own data engine (D-0239); the engine study and its stage 0 are decided (D-0455, D-0458: "we can do stage 0 now that will avoid some headache after"). The story of part 4 of the main document does not mention engines: a reader should know that two tiers of one table may run on different engines. No conflict.

### C18. "A named join takes only source tables" (D-0344) and the derived tables of the recipe redesign
- D-0344: "we need to be able to join metadata for example to any other original data" and "Yes, revisit if needed".
- A derived table (`from:` one table) is not a join; it does not break D-0344. A join that takes a derived table as an ingredient would reopen it (the proposal leaves this open). Information for question 2.

---

## D. Examined and found to hold together

- D-0344 (a join takes only source tables) with D-0510 and D-0513: "source tables" are the tables of the three blocks; the join with the metadata is a tier 1 step of a join. No conflict.
- D-0346 ("A join that no plot reads is not offered") with D-0451 ("We must modify"): resolved by D-0451.
- D-0146 ("the audit steps can be added at the end of each T1 - T2 - T3 (for now)") with D-0507 ("and maybe we need at the beginning of T1 also"): resolved by D-0509 (no T0, no beginning of tier 1).
- D-0315 (the log in the bundle only when ticked) with D-0478 ("not optional anymore"): resolved by D-0478.
- D-0022 (a step is written at one of T1, T2 of a table or T3 of a plot) with D-0093 (applied at each ticked node): one write per ticked place. No conflict.
