Copied on 2026-11-22 from the panel's scratch folder (D-0419). Answers of the agent in charge of the recipe proposal to the whole-picture agent (D-0526). Not confirmed by the owner.

# Answers of the recipe design proposal's agent to the whole-picture agent (2026-11-22)

Order of the owner (D-0526): "This agent is allowed to communicate with the agents that are in charge of the recipe design proposal". A study: nothing is built and no recipe, code, rule or ledger line is changed. Everything I ran is under this folder (scripts beside this file, outputs in `out/`, copies of the proposal's recipe files in `inputs/`). Questions: `SPARMVET_VIZ_wt_whole_picture/tmpAI/questions_for_the_proposal_authors.md`. The proposal: `.claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md` (form 3 is NOT confirmed, D-0496).

Labels: **run** (I ran it with the real engine or check; script and output named), **read** (at file:line or a ledger line with her words), **reasoned** (mine, not run).

Run from the repository root: `PYTHONPATH=. ./.venv/bin/python tmpAI/panel/tables_as_results/answers/<script>.py` (load average was 4 to 5 each time; nothing above 10).
Scripts: `q1_walkthrough.py`, `q1b_where_written.py`, `q_checks.py` (questions 2, 6, 7, 11), `q5_q8_scan.py`; the counts of question 8 are in `out/q8_counts.out`.

---

## Flags first (what could change a result silently or hide something)

1. **A record contradicts the code (rule H).** The ledger line D-0510 reports "the recipe check ... has no rule that refuses a join step in tier 2", and `BUILD_ORDER.md` slice 10 plans a new check "that a join with the metadata is a tier 1 step" with a test "a small recipe that joins the metadata in tier 2 is refused". The check ALREADY refuses every join action outside tier 1: code ST05 "polars_join is only allowed in tier1" (**read** `libs/utils/src/utils/recipe_check.py:693,714`, `libs/utils/src/utils/action_names.py:66` `TIER1_ONLY = {JOIN, JOIN_ASOF, JOIN_WHERE}`; **run**, `out/q_checks.out`: a join of the metadata in the tier 2 of a join, in the tier 3 of a plot and in the tier 2 of a source table are each refused with ST05). A test exists: `libs/utils/tests/test_recipe_check_join_tier1_only.py`. So the rule of D-0510 is built for the three join actions; what is not covered is only the plain words that name the metadata. I do not edit the ledger; the review session should see it.
2. **Reading A of "the earliest place" changes a derived table's result in a way nobody ticked** (**run**): the reads summary (a derived table made from a join with the metadata) shows a NEW group with an empty country and year that holds the removed entity (10 rows, total still 42). Reading B and B' do not. Details: `DIALOG_WALKTHROUGH_redone.md` part 3.
3. **A table that only a derived table reads is invisible to four places of the code today** (**run** and **read**): the check (S07, J14), the audit copy (`audit_copy.py:177`), the key rule (`key_drop.py:66`) and the export (`export_handlers.py:61-80`, `1383-1386`) all ask "which tables does a plot target?" (`recipe_tiers.plot_targets`, reads `target_dataset` only). If derived tables are built and one of these is forgotten, a tier 2 is refused, or a table is absent from the export, with no result changed and no message at the right place. Question 6.
4. **One plot id written in two groups** is accepted by today's check (**run**, `q_checks.py`: 0 errors); it is filed as a task already (question 11).

---

## The eleven answers

### 1. The default ticks (D-0508), reading A and reading B

- **Answer.** Done: `DIALOG_WALKTHROUGH_redone.md`. In one line: under reading A the lines `MLST` and `metadata_schema` start ticked and three results change (`mlst_bar`, the two results of the derived table, and a reads summary that gains an empty group); under reading B the lines `MLST_with_metadata` and `FastP_with_metadata` start ticked and the same three results change with no empty group; a derived table is never a ticked line for the entity key, in either reading; for a column the derived table makes itself (`year_label`) the derived table's tier 1 is the earliest place and neither reading says what is ticked (not decided).
- **Evidence.** **Run**: `q1_walkthrough.py` (`out/q1_walkthrough.out`) and `q1b_where_written.py` (`out/q1b_where_written.out`) on the proposal's slice plus the proposal's own reads summary (Part 2.6), with the real engine; the derived table is the route 1 of the proposal's Part 6, proved equal to plain Polars there. The lines of the dialog are **reasoned** from the columns of each place (run) and from D-0346 and D-0347; the real `lineage_walk.walk` was not run on it (it does not know derived tables).
- **The assumption of the whole-picture agent ("a derived table is never the earliest place for a removal by the entity key") HOLDS.** It does not hold for a column that only the derived table has: add that sentence to the study (edits 1 and 2).
- **Stays the owner's choice:** which reading (question 1 of the whole-picture design: A, B or B'); what is ticked for a column made inside a derived table; whether `FastP` or `FastP_with_metadata` is in the lineage of the open result (WHOLE_PICTURE 6.1). What she would see under each is in the walk-through table.

### 2. A join inside a derived table

- **Answer.** In the proposal there is none, and today's code makes a join in a derived table impossible without a new rule. A join action is allowed only in tier 1 of a JOIN (ST05, **run**), and a join step can only name a right table that the join lists in `ingredients` (J05, **read** `recipe_check.py:886-887`). A derived table has `from:` (one table) and no `ingredients`, so it has nothing to name. So: a derived table holds no join step, and a join with a look-up table is written BEFORE it, as a `joins` entry whose ingredients are source tables (`additional_datasets_schemas` count as source tables, J04 accepts every schema id, **read** `recipe_check.py:867`), and the derived table is made from that join.
- **How D-0510 and D-0511 apply.** D-0510 ("the join with any metadata must be done at T1") is unchanged: the metadata join is a tier 1 step of a join of raw data tables. D-0511 ("derived tables should already have the metadata joined"): a derived table is made from a table that already has it, and it cannot join it again (no join step is allowed in it). So the rule of D-0510 needs no second place to check. What the check cannot do, and nobody decided: tell that the `from:` table carries the metadata (D-0511 leaves the advice open: "NOT decided: whether the recipe check gives an advice").
- **What is NOT possible then:** a join of a summary with a look-up table AFTER the aggregation (for example a table of genes of interest joined to a per-group count): that needs a join that takes a derived table as an ingredient, and it reopens D-0344 ("a named join takes only source tables ... Yes, revisit if needed"). The proposal's Part 8 point 10 is this question. Nothing in her case needs it.
- **Assumption HOLDS** ("a derived table holds no join step; it is made from ONE table"), and it is stronger than assumed: it is not a choice of the proposal, it follows from `ingredients` being the only way to name a right table.
- **Stays the owner's:** whether a join may take a derived table as an ingredient (D-0344); whether the check advises when the `from:` table has no metadata columns.
- **Evidence.** **Run** `q_checks.py` (three ST05 refusals); **read** `recipe_check.py:693,714,867,886`, `action_names.py:66`, ledger D-0510, D-0511, D-0344.

### 3. The export of a table result

- **Answer.** Today's export writes (per table the plots read) `<table>/T1_data.tsv`, `T2_data.tsv` when the table has tier 2 steps, once per table (**read** `export_handlers.py:1378-1386, 1417-1439`), and `T3_data_<plot>.tsv` per plot, only for a plot with audited or tier 3 steps (`1440-1474`). So two plots reading one table already share one T1 and one T2 file and each has its own T3 file when audited. With a derived table, "the table on screen" is the derived table's last stage, which the export already writes as the table's `T2_data.tsv` (or T1). A file named from the result's id (D-0490 Part 1 A) for a TABLE result is therefore a second file with the same rows, by design (D-0487: the result is exported by name, "distinct from the intermediate T1, T2, T3 files"). My answer to your assumption: **one file per TABLE result id**; for a PLOT result no new data file unless it is audited (then `T3_data_<id>.tsv`, as today). When a plot and a table read the same derived table: the table's file once, the table result's id file once, the plot's picture once.
- **The assumption ("one file per result id, the same rows") HOLDS for a table result; it needs one precision for a plot result** (it has no data file of its own today unless audited).
- **Stays the owner's (her D-0490 does not say it; options and what the user sees):**
  - (a) the id file for each TABLE result, with the same rows as the table's own file (my reading; the README says "the same rows as `<table>/T2_data.tsv`" with the row count);
  - (b) no extra file: the README maps the result id to the table's file (one file fewer; a reader who looks for the id finds none, against "named from the entry's id");
  - (c) an id file for EVERY result, plot or table (N results of one table give N files with the same rows).
  - Not decided: the folder and the extension (`results/<id>.tsv` was suggested by the scientist viewpoint, D-0490).
- **Code that changes (reasoned from the reads above):** the loop is keyed by the plots' `target_dataset` (`1383`), the key check's scope is built from the same (`1025-1028`), and `tables_no_plot_reads` (`61-80`) reads only `target_dataset`: a derived table and a table result must be counted in all three.
- **Evidence.** **Read** `export_handlers.py` lines named; ledger D-0487, D-0490 with her words; nothing could be run (no table result exists).

### 4. "Table to view" for a result made from a derived table

- **Answer.** The proposal's suggestion stays **s3**: "Source" keeps one meaning, "what this table is made from, as read", and the list names both kinds of entry: the original files that feed it (`MLST`, `metadata_schema`) and the table it is made from (`MLST_with_metadata`, after its tier 2: 33 rows, named). T1, T2 and T3 of result B are the derived table's own T1 (33 rows, one per entity, `year_label` added), T2 (6 rows, "Result") and T3 (T2 plus the audit steps). A user sees the tier 2 of the join through the Source line `MLST_with_metadata (after tier 2)`. She does NOT see the join's tier 1 (42 rows, before the filter of the years) from result B; she sees it by opening a result that reads the join itself (here `mlst_bar`), or through a picker (question 13).
- **Facts I add (they matter for the choice):**
  - the entity column does not exist at the derived table's tier 2 or at its results (**run**: columns of `RESULTS_B:derived_B_tier2` in `out/q1_walkthrough.out`: `country, year_label, n_samples`). To remove an entity from the story of B the user must view T1 (derived) or a Source line: the result view itself offers no start for an entity key;
  - today the Source list is the graph's source tables of the plot: the `DS` nodes of `lineage_back` (**read** `recipe_graph.py:235-239, 449-457`). Once a derived table is a node of the graph, s1 ("the files as read") is given by the same function with no new code; s3 needs one more kind of line in the list;
  - with ONE level of derived tables the s3 list holds at most one table more than s1.
- **Assumption HOLDS** ("s3, and the full chain only through a picker if she chooses one").
- **Stays the owner's (what she would see):** s1 = Source lists `MLST`, `metadata_schema` only (the join is seen from `mlst_bar` only); s2 = Source lists `MLST_with_metadata` (33 rows) with the badge "made from MLST_with_metadata (after tier 2)" (Source then means two things); s3 = both, each named; or "Source = s1 plus the lineage picker shows the whole chain" (D-0496, D-0508: the outline at the base, "the story of the data"). Her sentence of D-0518 is the open point: "I am just wondering of how to make it navigate. It seems to me to be an interesting solution though".
- **Evidence.** **Read** `recipe_graph.py`, ledger D-0518, D-0496; **run** for the columns and rows (`q1_walkthrough.py`); the screen itself is **reasoned** (no screen exists).

### 5. Chains of derived tables

- **Answer.** None in the shipped recipes. A scan of the recipes of `config/data_analysis_recipes`, `assets/gallery_data` and `app/tests/equality/recipes`: 58 files looked at, 54 recipes loaded (4 fragments skipped, listed in `out/q5_q8_scan.out`), 86 plot entries, **0 plot entries with tier 3 steps**, 3 tables with an aggregating or reshaping step in their tier 2 (`QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_aggregated_no_key`, all in the demo recipe, each read directly by plots), and 0 plots with tier 3 steps on such a table. So there is no summary of a summary in any shipped recipe (**run**, `q5_q8_scan.py`).
- **Would "one level for now" lose anything she asked for?** Her case (D-0517: "one final result could be used on T2a but T2a could be used to produce one T3a for another final result") is one level. A two-stage computation (a per-entity summary, then a summary of it, for example quantiles of a per-entity count) fits in ONE derived table: its tier 1 makes the first aggregate, its tier 2 the second (a tier is a list of steps, any number); the first aggregate is then viewable as the derived table's T1 in "Table to view". What one level cannot do: give the middle table a name of its own, or let two different consumers read the middle table (that needs a second table made from the first). **Reasoned**; not run (no such case exists to run).
- **Assumption HOLDS** (no such case in the demo).
- **Stays the owner's:** one level or any number (the whole-picture design's "(a1) or (a2)"); revisit if a real recipe needs it (the same words as D-0344).

### 6. Tables read only by a derived table

- **Answer.** The engine already builds the tier 2 of any join or source that has steps, whoever reads it: `DataOrchestrator.materialize_tier2` built a join's tier 2 (33 rows) when NO plot read the join (**run**, `q_checks.py`, section Q6), and the opening build lists the tier 2 of every collection that has tier 2 steps (**read** `app/modules/opening_build.py:83`). What does NOT follow today:
  - the **check** refuses it (J14 for a join, S07 for a source table, **run**: "tier2 of a join applies only when a plot reads the join"). It reads `recipe_tiers.plot_targets` (`recipe_tiers.py:182-194, 196-210`);
  - the **audit copy** refuses an audit step at its tier 2: "No plot reads 'MLST_with_metadata', so its tier 2 is applied nowhere" (**run**, `audit_copy.py:177`). The key rule also reads `plot_targets` (`key_drop.py:66`);
  - the **export** writes the tier 2 file only of a table that a plot targets (`1417-1439`); a table no plot reads gets its tier 1 file only (`1476-1506`). A join with a tier 2 read only by a derived table would be listed among the "tables no plot reads" and its tier 2 would NOT be exported, although the derived table is made from it. The export would then not hold the input of a table it exports (**read**; reasoned for the consequence);
  - HOME's data preview follows the open result's table (the data choice and its Source list, `home_theater.py:1173-1182`, `recipe_graph.source_tables_of_plot`; the contract section 7.2 rule 7 says "how the user reaches such a table in HOME ... is not decided"), so it is reached only through the Source list of s3 (question 4).
- **How it meets D-0451 and D-0457.** D-0451 ("at least t1 is also part of a lineage - T1+T2 and T1+T2+T3") and D-0457 ("must be viewable in the data preview"; the export writes every table): form 3 gives a reader to a table that today has none, so a table read only by a derived table is no longer "a table no plot reads" in the sense of S07/J14, but the four places above must count the derived table as a reader (`from:`). A table that nothing reads, derived table or result, keeps its question (question 21 of the whole-picture design; D-0514: "Why Tier 2 refuses ? its still data wrangling").
- **The assumption ("a tier 2 runs whenever a result or a derived table reads its table") HOLDS for the engine; it does NOT hold for the check, the audit copy, the key rule and the export.** Edit 5.
- **Stays the owner's:** question 21 (the tiers of a table nothing reads); how a table read only by a derived table is reached in HOME.

### 7. The audit copy and a result's tier 3

- **Answer.** Not checked by the proposal; I checked it (**run**, `q_checks.py`, section Q7):
  1. The place `T3:<id>` does not depend on the entry having a drawing: an entry with no `mapping` and no `layers` accepts an audit step (`T3:table_like`), the copy writes `tier3: {steps: [], audit_steps: [...]}` and `integrity_errors` is empty. So a table result needs no change in `audit_copy` for that.
  2. But everything is keyed on the list named `plots`: with the same entries under a list named `results`, `plot_entries` returns nothing and `add_step` refuses `T3:mlst_bar` ("The recipe has no plot 'mlst_bar'"), and `T2:MLST_with_metadata` ("No plot reads ...").
  3. A derived table is unknown: `T1:`/`T2:MLST_samples_per_country_year` are refused ("The recipe has no table or join ...").
  So "this result only" is writable for a table result as for a plot once ONE reading of all result entries replaces `plot_entries` (read at `recipe_tiers.py:152-161`), and the table kinds (`collection_bodies`, `recipe_tiers.py:235-242`) include derived tables. The graph (`recipe_graph.py`) has the nodes `T1`, `T2`, `T3` and the edge `T2:C -> T3:p`: a derived table is one more `T1`/`T2` pair read from the `T2` of its parent (the node `T2:C` is the same table when the list is empty, so "the last stage" needs no new rule).
- **The assumption (the T3 place of a result keeps the result's id) HOLDS** if result ids are unique over the whole recipe: the `T3:` prefix separates it from table ids, but `from:` names ids of tables and results in one space (Part 4 of the proposal) and today's duplicate id is not refused (question 11).
- **Facts for the form:** no shipped plot entry has tier 3 steps (**run**, `q5_q8_scan.py`: 86 plots, 0), and the one template that shows `tier3` has it as a comment (`config/data_analysis_recipes/templates/left_join_lesson.yaml:98-105`). So "the author never writes steps in a result's tier 3" (Part 8 point 8) changes no shipped recipe. The check would need one new rule (a result's `tier3` holds `audit_steps` only, in an audit recipe); the check and `audit_copy` already refuse `audit_steps` outside an audit recipe (`recipe_tiers.audit_step_places`, `orchestrator.refuse_audit_steps_outside_an_audit`, read).
- **Stays the owner's:** confirmation of point 8 (form 3 only).

### 8. The files the one move touches

Counts are **read** from `git ls-files` and grep (`out/q8_counts.out`), not a list of edits.

| Kind | Count | What changes under form 3 |
|---|---|---|
| Shipped recipes (master files) | 54 load (7 pipelines, 5 templates, 4 retest, 4 equality, 34 Gallery) | the keys that the names decide: the list of results, the key that says plot or table, `from:` in place of `target_dataset`. Which names: NOT decided (D-0485 "naming open", D-0487) |
| Included plot files (`plots/*.yaml`) | 37 (demo 18, `2_test_data_ST22_dummy` 3, `figshare_integration` 3, `stress_test_master` 1, equality 12) | the same keys (a folder `results/` was suggested, proposal 2.7) |
| Data steps inside plot entries | **0** of 86 plot entries | nothing to move (run) |
| Joins whose tier 2 aggregates (what a derived table would be) | 3, all in the demo recipe | whether they become derived tables is NOT decided and not needed: they are joins read by plots today |
| Python sources that read `target_dataset` | 30 (list: `handlers`: `audit_stack`, `blueprint_handlers`, `export_handlers`, `filter_and_audit_handlers`, `home_theater`; `modules`: `blueprint_plot_view`, `cache_keys`, `engine_record`, `gallery_examples`, `opening_build`, `orchestrator`, `view_badge`; `app/src/server.py`; libs: `blueprint_arch` (4), `utils` (5: `engine_keys_migration`, `recipe_check`, `recipe_factory`, `recipe_graph`, `recipe_tiers`), `viz_factory` (3), `viz_gallery` (1); scripts: 4) | rename of the key; the new kinds (derived table, result kinds) in `recipe_tiers`, `recipe_graph`, `recipe_check`, `audit_copy`, `key_drop`, `lineage_walk`, `export_handlers`, `opening_build`, `orchestrator` (read: they read `plot_targets` or `plot_entries`) |
| Python tests that name `target_dataset` | 96 files (`app/tests` 58, `libs/utils/tests` 18, `viz_factory/tests` 13, `blueprint_arch/tests` 6, `viz_gallery/tests` 1); 144 Python files read a "plots" key in all | fixtures follow the keys |
| Documentation, rules, knowledge naming `target_dataset` | 17 tracked files: `docs/appendix/data_analysis_recipe_structure.yaml`, `docs/appendix/viz_factory_*.qmd` (2), `docs/reference/wrangling_guide.qmd`, `docs/troubleshooting/index.qmd`, `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd`, `docs/workflows/blueprint_architect.qmd`, `docs/UML/app.mdj`, `.claude/rules/rules_data_analysis_recipe_structure.md` (section 8), `.claude/rules/rules_agent_role_bioscientist.md`, and 6 files of `.claude/knowledge/` | the spec (`libs/utils/src/utils/recipe_spec.yaml:49-57,75`) and the rule files the owner owns |
| Migration | `libs/utils/src/utils/engine_keys_migration.py`, `assets/scripts/migrate_plot_specs.py`, `scripts/migrate_data_analysis_recipes.py` exist (read); the names pass has its dry run (`assets/scripts/migrate_display_names.py`, `rules_toolchain.md`) | the one move needs the same kind of script (reasoned); a recipe saved by a user in the old shape is refused with the new names, as `renamed_keys.py` does for other keys (read) |

- **The Gallery's format.** A Gallery bundle is a recipe of format 1 with a plot entry that carries a `taxonomy` mapping (`rules_gallery_standards.md` section 2; example `assets/gallery_data/bar_simple/data_analysis_recipe.yaml`). Under form 3 the entry's keys follow the names pass, and `taxonomy` stays an entry key (it is in the allowed list of the plot entry, `recipe_spec.yaml:57`). The Gallery's generator writes the keys: `libs/viz_gallery/src/viz_gallery/example_recipe.py:127,142` writes `target_dataset` and `"plots"`; `app/modules/gallery_examples.py:93` reads `entry["target_dataset"]`; the index is rebuilt by `refresh_gallery.py`. A Gallery example is a picture (`preview_plot.png`, section 6): a TABLE result in the Gallery is not covered by any rule and not decided.
- **The assumption ("the Gallery examples follow the format and move in the same pass") HOLDS**, with the generator and the standards text in the same pass.
- **Stays the owner's:** the names (so the number of renames is only information); whether the three aggregating joins of the demo become derived tables in the same move (D-0525 lists what the move gathers; they are not on the list).

### 9. BLUEPRINT

- **Answer.** Not checked for form 3, and BLUEPRINT is not safe on a real recipe today for other reasons. **Read** `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py:20-42, 395-410`: the map has the kinds `trunk, add, meta, wrangle, branch, plot, info`; the plots are read from `group_spec.get("plots", {})` and `target_dataset`; there is no kind for a derived table or a table result. **Read** `tmpAI/coordinator/blueprint_verify/REPORT.md` section 0 (runs, 2026-11-22): Save loses every comment of the file (17 in the demo), an untouched Apply changes steps, a plot loses its mapping, Save writes with no check; section 1: Save does not write join tiers, tier 3, new tables or `plot_defaults`. `BUILD_PLAN.md` line 17 (same folder): the build plan "will NOT build" anything about results, derived tables and tier 3 before her decision.
- **The assumption ("not checked; BLUEPRINT is rebuilt after the format", D-0485) HOLDS.**
- **Stays the owner's:** nothing new here; the question is the order (format first, then BLUEPRINT), which she decided.
- **Evidence.** **Read** as above; nothing run by me.

### 10. The names in the examples

- **Answer.** The proposal's examples use old names where later decisions changed them (the proposal was written before the names pass was built, and D-0484 and D-0468 are of the same day). The table is below; I did not rewrite the proposal. The final examples (the ones she is shown before the move) should use the decided names; nothing in the proposal's logic depends on them.
- **The assumption ("yes") HOLDS as an intention; the text of the proposal does NOT yet.**

| In the proposal's examples | Where | Decided replacement | Line |
|---|---|---|---|
| `info.label` | recipe `info` | `info.ui_label` (optional; the file name is the fallback; an advice when missing) | D-0410, D-0470, D-0468 |
| `label:` on a source table, `metadata_schema`, a join (and on a derived table, which is new) | table kinds | `ui_label` | D-0407, D-0468 |
| `label:` on a field of `input_fields` | field | `ui_label` (the review session's reading of D-0468 lists "field `label`"; the field's display alias is D-0360) | D-0468 (reading, not her words), D-0360 |
| `ui_title:` in every plot or result entry | entry | REMOVED; the figure title is the `labs` layer only; the report uses the group and entry `ui_label` | D-0484, D-0409, D-0253 |
| `ui_label`, `description`, `comment` on groups and entries | | unchanged | D-0407 |
| `labs: title ...` in layers | | unchanged: the figure text is written only in `labs` | D-0253 |
| `spec_version: 1` | | stays 1 (no format 2) | D-0469 |
| `is_entity_key: true` | field | unchanged | D-0313, D-0082 |
| the words "sample" and "one row per sample" in descriptions of the demo | text | demo example text; a rule, a message or a screen text says "the entity" | D-0512 |
| `plots`/`results`, `result:`, `from:`, `derived_tables`, `target_dataset` | structure keys | NOT decided (D-0485 "naming open", D-0487; D-0517 decides only "yes we need the `from:`") | |
| `ingredients: [{dataset_id: ...}]` | join | no ledger line renames it (searched the ledger for `dataset_id`: no line) | |

### 11. The duplicate result id

- **Answer.** Yes: it is filed as a task of today, independent of the form: `RESULT-ID-TWICE-NOT-REFUSED` (`[sonnet/medium]`, "a defect: ledger D-0050, no silent error; no decision needed", open, "Not started"), **read** `.claude/tasks/tasks.md:958`, with the evidence `tmpAI/panel/tables_as_results/refined/try/out/check_duplicate_ids.out`. I re-ran the check: a plot id written in two groups gives 0 errors from the recipe check and `plot_entries` keeps one entry (the second replaces the first) (**run**, `q_checks.py` section Q11). The study's `DIFFERENCES.md` A23 says "Closes: A plain refusal by the recipe check, tests first. No answer needed." and does not name the task.
- **The assumption ("not filed") does NOT hold.** Edit 7.
- **Stays the owner's:** nothing.

---

## What changes in the study (exact edits)

Files are in `.claude/design/studies/whole_picture_2026-11/` of the worktree `SPARMVET_VIZ_wt_whole_picture`. "Old" is the sentence now; "New" is the sentence to put.

1. **`RECIPE_REDESIGN_REVIEW.md`, section 8, point 1.**
   Old: "1. A derived table is never the earliest place for a removal by the entity key (it is always below the tables that hold the entity first)."
   New: "1. A derived table is never the earliest place for a removal by the entity key (it is always below the tables that hold the entity first). Holds: run on the demo slice (`answers/DIALOG_WALKTHROUGH_redone.md`). It is the earliest place of a column that the derived table makes itself (for example `year_label`); what is ticked then is not decided."
2. **`WHOLE_PICTURE.md`, part 7.4, first bullet ("The places of an audit step").**
   Old: "For a removal by the entity key the earliest place is always further up (question 1), so the default ticks do not change (my assumption; asked to the authors of the proposal)."
   New: "For a removal by the entity key the earliest place is always further up (question 1), so the default ticks do not change (run on the demo slice by the authors of the proposal). On a derived table, reading A has a visible effect: the removed entity stays in a reads summary as a group with an empty country and year (10 rows instead of 9, total still 42), because the left join keeps the row of the first table; readings B and B' do not do that. For a column the derived table makes itself the earliest-place rule is not defined."
3. **`RECIPE_REDESIGN_REVIEW.md`, section 8, point 2.**
   Old: "2. A derived table holds no join step: it is made from ONE table."
   New: "2. A derived table holds no join step: it is made from ONE table. Holds, and is stronger than assumed: a join action is allowed only in tier 1 of a join (ST05, `recipe_check.py:714`) and a join step can only name a right table listed in `ingredients` (J05), which a derived table does not have. A join with a look-up table is written before the derived table; a look-up join after an aggregation needs a join that takes a derived table (reopens D-0344)."
4. **`RECIPE_REDESIGN_REVIEW.md`, section 4.2, last bullet and `WHOLE_PICTURE.md` part 7.4, second bullet.**
   Old (4.2): "Whether a derived table may join anything at all (a look-up table) is not said in the proposal (question 2 to the authors)."
   New: "A derived table cannot join anything: a join action is refused outside tier 1 of a join today (ST05) and a derived table has no `ingredients` to name a right table. A look-up join before the derived table is possible; one after an aggregation reopens D-0344."
   Old (WHOLE_PICTURE 7.4): "(as I read D-0511; whether a derived table may join anything is asked to the authors)."
   New: "(as I read D-0511; a derived table cannot join anything: ST05 refuses a join action outside tier 1 of a join)."
5. **`RECIPE_REDESIGN_REVIEW.md`, section 4.10, first bullet.**
   Old: "Under form 3, "read" means read by a result or by a derived table. The check's refusals of a tier 2 (S07 for a source table, J14 for a join) must count a derived table as a reader (Part 0 flag 5, run)."
   New: "Under form 3, "read" means read by a result or by a derived table. Four places read only the targets of the plots and must count a derived table as a reader: the check (S07, J14: `recipe_tiers.plot_targets`), the audit copy (`audit_copy.py:177`: it refuses an audit step at the tier 2 of a table no plot reads), the key rule (`key_drop.py:66`) and the export (`export_handlers.py:61-80, 1383-1386`: a tier 2 is exported only for a table a plot targets). The engine already builds that tier 2 (run)."
6. **`RECIPE_REDESIGN_REVIEW.md`, section 5, points 1, 9; `WHOLE_PICTURE.md` part 7.5, point 1 and the recommendation line.**
   Old (review 5.1): "The walk-through should be redone with D-0508, under both readings."
   New: "Redone with D-0508 under both readings, on the demo slice and the proposal's reads summary: `answers/DIALOG_WALKTHROUGH_redone.md`."
   Old (review 5.9): "Whether the library's audit copy (`libs/utils/src/utils/audit_copy.py`, which names the place `T3:<plot>`) writes it unchanged for a table result was not checked by the proposal (question 7 to the authors)."
   New: "Checked by run (`answers/q_checks.py`): `T3:<id>` accepts an entry with no drawing; but the audit copy reads only the list `plots` and knows no derived table, so `T3:<result>` and `T1:`/`T2:<derived table>` are refused under form 3 until `plot_entries` and `collection_bodies` read the new kinds."
   Old (WHOLE_PICTURE 7.5 point 1): "The walk-through should be redone."
   New: "The walk-through was redone (`answers/DIALOG_WALKTHROUGH_redone.md`)."
   Old (WHOLE_PICTURE 7.6 last line): "and the walk-through of the dialog redone with your default of D-0508."
   New: "(the walk-through of the dialog has been redone with your default of D-0508, readings A and B)."
7. **`DIFFERENCES.md`, A23, line "Closes".**
   Old: "- **Closes.** A plain refusal by the recipe check, tests first. No answer needed."
   New: "- **Closes.** A plain refusal by the recipe check, tests first. No answer needed. Filed as the open task `RESULT-ID-TWICE-NOT-REFUSED` (`.claude/tasks/tasks.md:958`)." And in `RECIPE_REDESIGN_REVIEW.md` section 8, none of the six assumptions concerns it; remove "not filed" wherever the questions file says "Assumed meanwhile: not filed" (it is in `questions_for_the_proposal_authors.md`, question 11).
8. **`BUILD_ORDER.md`, slice 10, first bullet and the "Tests" bullet.**
   Old: "- The check that a join with the metadata is a tier 1 step (D-0510, confirmed in her words by D-0523). **NO ANSWER NEEDED** for the rule: a scan of 141 loadable recipe files found none that joins the metadata in tier 2 (review of the code claims); the words of the refusal stay PROVISIONAL until she reads them."
   New: "- The check that a join with the metadata is a tier 1 step (D-0510, confirmed in her words by D-0523) EXISTS for every join action: ST05 "polars_join is only allowed in tier1" (`recipe_check.py:714`, `action_names.py:66`, test `libs/utils/tests/test_recipe_check_join_tier1_only.py`; run on 2026-11-22). What remains is only whether the refusal should name the metadata in plain words; **NO ANSWER NEEDED** for the rule."
   Old (Tests): "a small recipe that joins the metadata in tier 2 is refused with a plain line;"
   New: "(the refusal of a join in tier 2 is already tested; keep that test and add the one with the metadata named, if the words are added)".
   Also report to the review session: the ledger line D-0510 holds the sentence "the recipe check ... has no rule that refuses a join step in tier 2", which ST05 contradicts (rule H); the line is not edited by me.
9. **`WHOLE_PICTURE.md`, part 7.4, fourth bullet ("A table as a result, and its export").**
   Old: "The proposal does not say how the export names it (your "Part 1 -A" of D-0490 names it from the result's id), nor what happens when a plot and a table read the same derived table."
   New: "The proposal does not say it; the authors answer: a file named from the result's id for each TABLE result, with the same rows as the derived table's own `T2_data.tsv` (a plot result keeps the table's file, and gets `T3_data_<id>.tsv` only when audited). Options for you: that, or only a line in the README that maps the id to the table's file, or an id file for every result (`answers/ANSWERS.md` question 3). The export loop, the key check's scope and `tables_no_plot_reads` read only the plots' targets and must count derived tables and table results."
10. **`WHOLE_PICTURE.md` part 7.4 third bullet ("The story of the data") and `RECIPE_REDESIGN_REVIEW.md` 4.3.**
    Add after "This is your question of D-0518": "The entity column does not exist at the derived table's tier 2 or at a table result of an aggregate (run): to remove an entity the user starts from the derived table's T1, or from a Source line, not from the result."
11. **`RECIPE_REDESIGN_REVIEW.md`, section 8, points 3 to 6.** Append: 3 "Holds for a table result; a plot result has no data file of its own unless audited (question 3 of the answers)." 4 "Holds: it is the proposal's own suggestion." 5 "Holds (run): 54 recipes, 86 plot entries, none with tier 3 steps, no chain." 6 "Holds as an intention; the proposal's examples still use `label` and `ui_title` (table in `answers/ANSWERS.md`, question 10)."
12. **`WHOLE_PICTURE.md`, part 9 ("What nobody checked"), third bullet.** Add: "The authors of the proposal ran the dialog walk-through again for me on the demo slice and the reads summary (`answers/`); the real lineage walk was not run on it (it does not know derived tables), and the lines of the dialog are reasoned from the columns of each place."

## Not checked

- No screen, no browser: every "what the user would see" is described. The dialog lines of the walk-through are reasoned from the columns of each place (run) and from D-0346 and D-0347; the library's `lineage_walk.walk` was not run on a recipe with derived tables (it cannot read them).
- Derived tables and table results do not exist in the engine, the check, the audit copy, the graph, the export or BLUEPRINT. I used the proposal's own proof (a derived table's steps as the tier 3 of a probe plot equal plain Polars, Part 6) and ran the reads summary through the same route; I did not rebuild the plain-Polars comparison for `FastP_reads_summary` (the proposal did: Part 2.6, 9 rows equal).
- The two readings were run on a slice with two joins that join the metadata (`MLST_with_metadata`, `FastP_with_metadata`), not on the 13 of the demo (the whole-picture study's own runs, part 6.1, I did not repeat).
- The scan of question 5 covers the repository's recipes only (4 fragments skipped); recipes in a user's folder and in imported bundles were not looked at.
- The counts of question 8 are greps of tracked files; they say which files name the keys, not what each edit is.
- The ledger lines D-0468 and D-0407 to D-0412 were read in the ledger, with the brackets that say what is the review session's reading; I did not read the transcripts.
- The class of a gallery example with a table result (question 8), the export of a table result (question 3), and BLUEPRINT writing a derived table (question 9) were not run: nothing exists to run.
