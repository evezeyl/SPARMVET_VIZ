# SPARMVET-VIZ Changelog
Append a new `## [date]` section for each release / breaking-change session.
Breaking changes are marked ⚠️. Renames that affect the data analysis recipe data contract are marked 🔑.

---

## [2026-11-24] - HOME audit: the third tier through the audit copy, and the audited table files of an export made in Audit mode (branch `task/audit-places-demo`; D-0535, D-0553, D-0329, D-0613; owner's word of 2026-11-24 on the table files)

The tiers work ONE way now: every audit step is a node written at a place (`T1:<table>`, `T2:<table>`, `T3:<plot>`), all in the one bucket `__places__`, and HOME, the filter dialog, the audit panel, the export and the session read the audit copy.

- ⚠️ **Removed (one way to do one thing):** the plot-level lists of nodes (`t3_audit_steps_by_plot["subtab_<plot>"]`), `t3_audit_engine.audited_frame`, `audit_steps_in_order`, `dialog_frame`, `audit_failures`, `filter_rows_from_nodes`, `AuditStepError`; `t3_translator.build_mode2_recipe` (the fork of a join per plot) and `translate_plot_steps`; HOME's `_t3_filter_rows`, `_t3_drop_columns`, `_active_plot_t3_nodes`; the export's `t3_filter_rows`/`t3_drop_columns` arguments; the key `t3_translation_skipped` of `effective_run.yaml` (no plot can be skipped any more: a step that cannot be written stops the reproducibility part). The importer still reads that key from a bundle made before.
- 🔑 ⚠️ **Session files are format number 5**: an older file (4, 3, ...) is refused, never converted, and a file whose step has no `place` is refused with a plain line. The stored key is still named `t3_audit_steps_by_plot` (it now holds the single bucket `__places__`; renaming it is a later format number, PROVISIONAL).
- **The dialog** writes "This plot only", "All plots" and "All plots except" as nodes at `T3:<plot>` (one node per plot, one id; a plot whose table lacks the column is skipped and told). The place list also holds the plot's own line, so the rule of places covers a table and the plot below it in one decision (one plain refusal; two separate decisions at different places stay allowed). The steps run tier 1, tier 2, tier 3, and inside a tier in the order written.
- **One error for the audit:** an audit step that cannot run is refused with its id and its place for every plot it breaks (`AuditRunError`), in the plot's place, in the table's place, in the export (nothing is exported) and in the dialog (no table is offered). The hint of the old message "removed by audit step N" is not in it any more (PROVISIONAL: the engine's own words name the column).
- `bake_place_steps` bakes a step at a plot into the plot's own `tier3.steps` and leaves out the loader's root `plots` mirror (a root `plots:` does not load again; found when the fork was removed).
- **Audited table files (owner, 2026-11-24; the form is PROVISIONAL):** an export made in Audit mode writes `<table>/T1_data_audited.tsv` and `T2_data_audited.tsv` beside the originals for every table an audit step changes (`AuditRun.audited_frames`); README.txt and report.qmd say which file is which and which steps made the difference; an export made in Exploration mode keeps the originals only and says so. `t3_steps.yaml` lists the steps under `steps_by_place` (was `audit_steps_at_tables`).
- Tests: `test_audit_view.py` (tier 3, isolation between plots on one table, order across tiers), `test_audit_dialog_places.py`, `test_export_audited_tables.py`, `test_step_order.py` (table, plot, bundle file and re-run agree through the audit copy), the rewritten `audit_nodes.py` helpers (`audited_lf` runs the engine's own actions).

---

## [2026-11-24] - HOME audit: an audit step written at a table upstream of the plot, in five functional steps (branch `task/audit-places-demo`; D-0535, D-0553, D-0346, D-0329, D-0613)

Each step left the app working; the commits are marked `[DEMO STEP n/5 functional]`.

- **Step 1** `app/modules/audit_places.py`: for an open plot and the column(s) of a step, the tables upstream where the engine's plan holds the column (tier 1; tier 2 when the table has tier-2 steps of its own), with the other tables and plots built from each (D-0346) and the check of a choice (at most one place on a path; the first places of several original tables together; D-0553).
- **Step 2** `app/modules/audit_view.py` (`PlaceAudit`), `AuditRun.plot_table`: the committed nodes written at a place (node field `place`, bucket `__places__` of `t3_audit_steps_by_plot`) make an audit copy of the recipe (`utils.audit_copy`), run by `audit_run.run_audit` into a folder of its own (`user_data/audit_anchors`); HOME reads the audited table in Audit mode (plot, T3 view, filter dialog, Compare's audited pane; `_resolve_active_lf(..., original=True)` for the original pane). The original's stored tables are not touched; removing the last step removes the folder.
- **Step 3** the dialog of Send to Audit has the choice "At a table this plot is built from" (default stays "This plot only"); a choice that breaks the rule of places, no table ticked, and a key drop that a later join reads are refused in one line with the dialog open; the audit card says "Written at Table X (tier n)"; the plot badge says how many steps were written upstream and whether its table changed.
- **Step 4** export: the data file and the figure of each plot below the place are the audited ones; `t3_steps.yaml` `audit_steps_at_tables`; README, report (section "Audit steps written at a table") and Methods text; the checksum of the audit steps covers them; the reproducibility recipe holds each step as a plain step at the end of its tier (`bake_place_steps`). ⚠️ **Session format 4** (`SESSION_FORMAT_VERSION`): a session file of format 3 is refused, not converted; the tests that wrote the number 3 read the constant.
- **Step 5** tests of the marker case (a filter on `ResFinder_not_in_original_data` at the tier 1 of ResFinder) and of the key drop at a place; user guide and contract.
- PROVISIONAL (builder's choices): the words of the dialog, card, badge, README and report lines; that the T1 and T2 files of an audited table stay the original tables; that `Remove step` removes a decision with all its places.

---

## [2026-11-24] - The warning of the ids in HOME and its button "I have read this" (branch `task/id-warning-home`; D-0582, D-0585, D-0613)

- **A red warning above the tabs of HOME** (`app/handlers/id_warning_handlers.py`, output `id_warning_ui`, slot in `app/src/ui.py`), in every app features file (no flag gates it), when the checks of the ids found something: lines added ("missing in original table" with the sentence of the recipe maker), ids of a table not in the metadata, lines with no usable id, a log that could not be written, or checks that failed. Nothing found: no warning. It shows the place of the log, the log itself in a collapsible block, and the button **I have read this**.
- **The button blocks nothing.** The click is written in the log of the ids as an entry of kind `read` (`utils.id_log.record_read`, `who: read in the app`, the date, the fingerprints of the recipe and the data) and the warning shrinks to one quiet line ("Id warnings read on <date>. Show again"). PROVISIONAL: asked once per recipe and data batch (kept in the log file, so a new session on the same data shows the quiet line); a changed recipe or new data shows the red warning again; a click that cannot be written is said in the warning.
- **The Export panel** shows one line ("This export includes the log of the ids: N warning(s)", red until read); **README.txt and report.qmd** (new section "The ids of the tables") say what was found, in the app's words with the recipe maker's sentence per table, and whether the warning was read in the app or the log is "automatic, no user". The export is never refused because of it. The block that writes `id_log.yaml` moved before the report so the report can say it.
- `opening_handlers.define_server` takes `id_run_state` and writes what the checks found once per opening (equality guard); the warning reads it. CSS: `theme.css` section 27 (error red on `#ffe0e0`, primary button; no new colour or size).
- Docs: `understanding_your_export.qmd` (new section), `good_practice_recipes.qmd`, `ui_implementation_contract.md` section 15.

---

## [2026-11-24] - The one big move on the shipped recipes: data first, the entity id declared, an added ResFinder line reads Not Found (branch `task/ids-checks-completion`; D-0586, D-0610, D-0613)

- 🔑 ⚠️ **A joined table of a shipped recipe starts from a data table and brings the metadata in by a left join** (D-0586, D-0613). Rewritten in `1_test_data_ST22_dummy`: `ST22_Anchor` (now FastP first), `QA_AMR_per_sample` and `QA_fanout_exhibit` (ResFinder first), `QA_population_zscore` (Quast first); in `demo_abromics`: `demo_join` (MLST first). Same rows, same entities as before (617, 74, 1731, 42, 27 rows); only the order of the rows of some tables differs. The rule is advice in `good_practice_recipes.qmd`; the checker does not enforce it (how it would be enforced is not decided).
- ⚠️ **`demo_join` has no `polars_drop_nulls` step any more**: the table starts from the MLST table, so the 3 metadata lines with no sample id match nothing and are not in it; the metadata file is not touched (D-0594) and the app's warning lists the three lines.
- 🔑 **`QA_year_types` and `QA_aggregated_no_key` are data schemas** on the metadata file (D-0610), no longer joins of one ingredient; same names, so the plots keep their `target_dataset`. Their markers are `QA_year_types_not_in_original_data` and `QA_aggregated_no_key_not_in_original_data`. The metadata file is read a second time under each name.
- 🔑 **`VirulenceFinder` moved from `additional_datasets_schemas` to `data_schemas`** (`1_test_data_ST22_dummy`, `1_Abromics_general_pipeline`) with a `completion` block (D-0610). The first select of `MLST_wrangling.yaml` and `VirulenceFinder_wrangling.yaml` now names the table's own marker, so the table keeps it.
- ⚠️ **An entity with no ResFinder line reads `Not Found`, not `Detected`, and has 0 genes** (D-0613, the owner's reading of ResFinder): `ResFinder_wrangling_tier1.yaml` stamps the status from the marker; `ResFinder_wrangling_tier2.yaml` counts only the lines of the file. Changed pictures against the state before the completion: `amr_heatmap` (74 rows instead of 70: the 4 entities appear with no gene), `virulence_bar` and `virulence_variants` (same 617 rows; the 31 rows of the 4 entities read Not Found, they were empty). `qa_amr_genes_per_sample` shows 42 entities, 4 at 0 (the count already counted only genes).
- 🔑 **`2_test_data_ST22_dummy` and `figshare_integration` declare `is_entity_id` on `sample_id`** in their six tables (the three of each) with a `completion` block; the two joins of `2_test_data_ST22_dummy` with the metadata are left joins (they were inner joins). Same rows (70 and 163); the shipped data lacks no id there.
- ⚠️ **Consequence of the two QA tables being data schemas:** no join links them to the metadata, so the lineage walk does not reach them (they are listed as `outside`, with the sources no join links); a removal of a sample by its id does not act on them, and `qa_year_label` and `qa_facet_by_mapping` are no longer lines of that walk. The deployment `pipeline_test` (files found by the name of the table) needs a file per table name: `QA_year_types.tsv` and `QA_aggregated_no_key.tsv` were added to `assets/test_data/duplicated_1_test_data_ST22_dummy/` as copies of `metadata_schema.tsv`, as `Summary_quality.tsv` is a copy of `Summary.tsv` (no data file was edited).
- Not done on purpose: `figshare_triple_join` still starts from `fg_metadata` (a data schema that plays the metadata role by its name, not the `metadata_schema` block); the template `left_join_lesson` no longer teaches its lesson after the completion (3 strict xfails kept, the owner decides what the lesson becomes).

---

## [2026-11-24] - The ids are made equal: the completion at the read, the three checks and their log (branch `task/ids-checks-completion`; D-0572 to D-0599, D-0613)

- 🔑 ⚠️ **A new block `completion: {marker, meaning}` is required** on every table of `data_schemas`, and on `metadata_schema`, that declares an `is_entity_id` (check E04; E05 to E07 for a wrong block). PROVISIONAL form (D-0613). `marker` is the name of a yes/no column the app adds, by convention `<table>_not_in_original_data` for every table, the metadata included (the owner, 2026-11-24; `not_in_metadata` no longer exists); `meaning` is a free sentence of the recipe maker about the table (the list of words was removed; E05 refuses a missing or blank sentence and does not judge it); the app's own fixed words for an added line are `missing in original table`. Two tables never share a marker (E06). Shipped recipes: the ResFinder table of the demo has the sentence "The tool ran and found no resistance gene for this entity: Not Found, counted as 0."; every other table has the starting sentence "Not yet stated by the recipe maker: ..." until the owner gives its own. A table of `additional_datasets_schemas` never takes part. The format number stays 1 (D-0469). Every shipped recipe, template and generator (`recipe_factory`, the Test Lab bootstrapper and scaffolder, `create_data_analysis_recipe.py`) writes the block; the engine does not run a table that declares an entity id and has none.
- ⚠️ **The read of the files now completes the ids** (`libs/utils/src/utils/id_completion.py`, `DataOrchestrator._read_source`): before the steps of tier 1 every table that takes part gets a line for each entity id of the union that it lacks (the id, every other value missing, the marker true), the metadata too; nothing is removed or changed; a line with no usable id stays, is not completed and is listed. On the demo `ResFinder` gains 4 lines (38 of 42 ids); `demo_abromics` MLST gains 12 (the metadata has 3 lines with no id). The Source view of HOME shows the file as read (PROVISIONAL). There is no T0 place (D-0613).
- **Three checks of the ids, warnings only** (`DataOrchestrator.id_report`, `check_data_analysis_recipe_data`): ids of a result table not in the metadata, ids of the metadata not in a result table, and, after the completion, equal sets in every table (a difference is a bug of the app, D-0590). A recipe is never refused or hidden for them.
- **The log of the ids** (`libs/utils/src/utils/id_log.py`, `app/modules/id_check_run.py`): written automatically when HOME opens a recipe, `<user_data>/_id_logs/<recipe id>.id_log.yaml` ("automatic, no user", one entry per recipe and data state, the fingerprints, the numbers and the unmatched ids); `record_read` is the function of the later button "I have read this". When the folder cannot be written the text is printed to the console and returned. Every export holds `id_log.yaml` and README.txt names it. No HOME screen yet.
- The cache key of a table that reads a table that takes part holds the id declarations and the data files of all of them (`cache_keys.table_key_parts`); the cache version is unchanged (a key that does not match is never served).
- Docs: `good_practice_recipes.qmd`, `Standards_yaml.qmd`, `recipe_format_spec.md` (7.3, E04 to E07), `rules_data_analysis_recipe_structure.md` section 13, `rules_data_engine.md`.

---

## [2026-11-23] - The names pass: one name key, `ui_label`, everywhere (branch `task/names-pass`; D-0409, D-0410, D-0411, D-0468, D-0474, D-0479 to D-0484, D-0497)

- 🔑 ⚠️ **`ui_label` is the one name key of the recipe** (D-0409, D-0410, D-0468). `info.label`, `info.name`, `info.display_name` and `info.ui_title` become `info.ui_label`; the `label` of a table, a join and an input field becomes `ui_label`. The old keys are refused by the recipe check with the new name (I03, S01, J01, FD01). `info.ui_label` is optional: without it the file name is shown and the check gives an ADVICE (I01, severity A; the words are PROVISIONAL). The format number stays 1 (D-0469). Applied to the 188 files of the repository by `assets/scripts/migrate_display_names.py --apply --in-worktree` (524 changes).
- 🔑 ⚠️ **`ui_title` is removed** from groups and plot entries (D-0409, D-0484; the 25 removed texts equal the figure title of their plot). The old key is refused with the new name (G01, P01). Nothing invents a name any more: a group is its `ui_label`, a plot is its `ui_label` (no `description` as a tab, no plot id in title case, no `name`).
- ⚠️ **The export report uses the same `ui_label` as HOME and is built by group** (D-0484): the group `ui_label` is a `##` heading, the plot `ui_label` a `###` (PROVISIONAL heading levels; the two parts `# Results` and `# Technical` of D-0491 are NOT built here).
- ⚠️ **The deployment banner** `branding.banner`: `title` becomes `ui_label`, `subtitle` becomes `description` (D-0411); the old keys are refused at start. **`deployment_name` is removed** from the deployment files (D-0479) and refused at start; `Bootloader.deployment_name` and `BaseConnector.get_deployment_name()` are removed. A comment block with the former text was written at the top of each deployment file (PROVISIONAL form).
- ⚠️ **The recipe banner in HOME** shows `info.ui_label` (the file name when there is none) and no longer `info.subtitle`, which stays a free key of `info` (D-0482). A new switch `branding.show_recipe_name: true|false` in the deployment file hides it (true when absent; D-0474). The app features key `ui_title {text, subtitle, visible}` is removed and refused.
- ⚠️ **App features files**: `display_name` becomes `ui_label` (D-0480); the key `name` is removed (D-0481): the id is the file name, hyphens and underscores are both free (D-0483); the rule "no underscore in the id" of `AppFeaturesValidator` and its troubleshooting entry are removed. The export writes the app features file as `Web Demo (web-demo)` (the `ui_label` and the file name, D-0497) in the README, the report and the picture metadata.
- The user-visible words "entity key" now read "entity id" (messages of the recipe check E02 and of "remove from all the data", the user guide).
- Not changed on purpose: the allowed-key lists of deployment and app features files (they wait for the deployment standard, D-0412); the `label` strings of the Python registries (D-0468); the plot-node labels of the TubeMap; `docs/UML/app.mdj`.

---

## [2026-11-23] - The mark `is_entity_key` is now `is_entity_id` (branch `task/rename-is-entity-id`; D-0562, D-0567)

- 🔑 ⚠️ **`is_entity_key` is renamed `is_entity_id`**, one name for all cases (D-0562): the field is not a row key, it refers to the entity (on the demo, the sample); when its values are unique in the table it is also the key of the table, when they repeat the table has several rows per entity. The approved sentence is the description in the specification (`recipe_format_spec.md`) and in `docs/appendix/Standards_yaml.qmd` (D-0567). The same columns are marked; nothing else of the recipes changed.
- ⚠️ **A recipe that still writes `is_entity_key` (or `is_primary_key`) in a field is refused** by the recipe check, code FD03, with the new name (`is_entity_id`); there is no alias and no fallback read (the old mark is not read: a population table that carries only the old mark gets E02). `libs/utils/src/utils/recipe_migration.py` rewrites both old names. Every shipped recipe, `input_fields` file, template, Gallery bundle and test recipe was rewritten.
- `assets/scripts/dry_run_big_move.py`: section 2 (this rename) is done and lists no line; the tool reads the new name when it looks for the declared entity id.
- Not changed on purpose: the Python identifiers and prose that say "entity key" as a concept (`declared_entity_keys`, the `entity_key=` argument of `minimal_schema`, the notes `NOTE_DECLARED_ENTITY_KEY`); the ledger, the studies and the logs keep the old name as history.

---

## [2026-11-18] — Engine keys: the data analysis recipe shape, the engines, the cache version 5 (branch `task/engine-keys`; D-0219 to D-0258)

Recipe format 1 was amended before its first release (D-0236): no format 2. One migration run rewrote every data analysis recipe, template, retest scenario, test data analysis recipe and the 34 gallery bundles (`assets/scripts/migrate_recipe_engine_keys.py`, safe to run twice, prints every change); a data analysis recipe in the earlier shape is refused with the new form and the tool named.

- 🔑 ⚠️ **A tier is its own key** (D-0250). `wrangling: {tier1, tier2}` of a table, `steps: {tier1, tier2}` of a join and `steps: {tier3}` of a plot entry are gone: write `tier1:`, `tier2:` (and `tier3:` at the plot entry), each a mapping with an optional `data_engine` (first key) and `steps` (the list). `tier1: !include f.yaml` per tier; a fragment that held two tiers is split into one file per tier.
- 🔑 ⚠️ **A plot entry has no `spec:`** (D-0237, D-0252). The content (`target_dataset`, `mapping`, `layers`, `theme`, ...) is written in the entry, or the whole entry is in its own file included at the entry level.
- 🔑 ⚠️ **`label` of a group and of a plot entry is `ui_label`; new `ui_title`** (D-0253): the report uses `ui_title`, else `ui_label`. The figure text is written only in the `labs` layer: `title:` of the plot content is removed (the migration moved each old title into `labs` and `ui_title`). The `label` of `info`, tables, joins and fields is unchanged for now (pending, one table in `recipe_spec.yaml`).
- 🔑 ⚠️ **The engines are used** (D-0219, D-0238, D-0239, D-0247). `data_engine` and `plot_engine` at the top are the defaults; a tier or a plot entry may name its own; the code chooses the library by the value (`app/modules/engine_registry.py`); every registered action and plot component carries the field `engine`; each library has an entry file (`engine_python_polars.py`, `engine_python_plotnine.py`). A step in a block of another engine is refused (EN02); an engine the app has no library for is refused with "no library for this engine in this app" (T06). A data analysis recipe that names no engine is refused at the load gate and at run time (no default).
- 🔑 ⚠️ **Four dead `plot_defaults` keys are removed** (D-0220, D-0242): `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`. The checker refuses each with a tombstone (PD02); the migration prints each with its old value. Font, legend and spacing are set through a theme layer; the axis-text adjustment is overridden per axis with an `element_text` layer.
- ⚠️ **No built-in `theme_bw`** (D-0258). A plot with no theme is drawn with plotnine's own default (`theme_gray`). The migration wrote `theme_bw` once in the `plot_defaults` of 35 data analysis recipes and bundles (every plot that had none), so every picture is identical (checked: 50 data analysis recipe pictures, 34 gallery previews, the golden tables).
- ⚠️ **Cache version 4 to 5** (D-0240). The engine of a tier is an argument of the key of that tier; the plot engine is in no table key. Every stored table of an older version is removed at the start of the app and rebuilt once; the user is told once: "The tables of your data analysis recipes are rebuilt once because the app changed how it names what it stored. Your results do not change." (PROVISIONAL wording).
- **`effective_run.yaml` has a new key `engines`** (D-0248): the engine per table tier and per plot, the library versions of the engines used, and the theme as applied per plot.
- ⚠️ **Join keys are alive in HOME** (found while reading the join steps in the new place): the key columns of the data analysis recipe's joins were read from a place that never matched (always an empty list on `dev`); now a column drop of a join key is refused in the audit ("Cannot drop join key column(s) ..."), a filter on a key carries the key warning, and a restored session that holds a drop of a key restores every other step and tells which step it left out (the saved file is not changed).
- ⚠️ **Blueprint**: one tier per file (Save refuses a step tagged for the other tier); an upload in the old shape is refused with a message (UP01, UP02); a branch writes a tier 1 file and, for a plot, a copy of the whole entry under `ui_label`. Removed as dead: the "Add plot wrangling" button and the key `pre_plot_wrangling` (read by nothing, refused by the plot checker), the "forward clear" hint (it checked `output_fields` slots that no data analysis recipe has), the roles `plot_wrangling` and `output_fields`. The lineage rail shows the tier 2 file of a table, labelled "(tier 2)".
- The Test Lab bootstrapper and scaffolder, `create_data_analysis_recipe.py` and the Blueprint agent's instruction text (`config/ui/agents/blueprint_default.md`) write the new shape; a test runs the checker on what each writer writes.
- Tombstone: the four `plot_defaults` keys of PD02 expire two phases after this change is merged (the removal task is made with the merge).

---

## [2026-11-15] — The audit steps of a plot run in their recorded order everywhere (PLOT-TABLE-ORDER-1, S2-1)

- ⚠️ **Results change, by decision (Eve 2026-11-14 and 2026-11-15).** One function, `audited_frame` (`app/modules/t3_audit_engine.py`), builds the My view frame of a plot from its audit steps in the order they were recorded: HOME table, HOME plot (and Compare), the results bundle and its plot, and the check before an export. Before: the table and the bundle data ran all filters then all drops, the plot ran all drops then skipped a filter on a dropped column silently, the exported recipe kept the recorded order.
- A step whose column does not exist, or was removed by an earlier step, is an error that names the plot, the step, the column and the fix; the export refuses (`EXPORT_NOT_CREATED.txt` names every failing plot). A spec `filters` entry of the plot factory on a missing column raises too (it was skipped).
- The filter dialog acts on the table after the plot's audited steps: a dropped column is not offered (My view only).
- The audit step type `developer_raw_yaml` is removed (AUDIT-RAWYAML-REMOVE-1): a session file, an imported bundle or an audit list that holds one is refused with a message that names the step.

## [2026-11-15] — A schema plotted directly runs its own tier 2 (issue #77, RECIPE-DATASET-TIER2-1)

- ⚠️ **Results change, by decision (DEC16, Eve 2026-11-12).** Every table has T1, T2 and T3 with or without a join; a schema that a plot reads directly is a collection and its own `wrangling.tier2` is its T2. Before, the engine read the tier-2 steps of joins only, so these steps were silently ignored: the recipe said one thing and the figure showed another.
- What changed in the shipped recipes (all pipelines, templates, retest recipes and 39 gallery examples checked before and after; only one schema has a tier-2 list): `1_test_data_ST22_dummy`, schema `ResFinder`, plot `amr_heatmap`. Its T2 and the plot's table now have the column `total_gene_count` and are sorted by it (descending), then by `sample_id`; 70 rows before and after; the picture differs. Its T1 and every join that uses `ResFinder` as an ingredient are unchanged.
- The T2 of such a schema is stored like a join's (`<name>__T2.parquet`, chained `tier2_key`, ADR-089); an empty list stores nothing (T2 equals T1). A schema's tier 2 is no longer part of the Tier 1 key, so every Tier 1 anchor is rebuilt once.
- A join reads the T1 of its ingredients (spec line 357). A tier-2 list on a schema that is only an ingredient runs nowhere and is refused at load (S07).
- One reading for everyone: `utils.recipe_tiers.tier2_steps` (engine, cache keys, HOME badge and tables, export, audit panel, checker, Blueprint lineage, which now notes on a schema's wrangling node that its tier 2 runs only where it is plotted directly).

---

## [2026-11-06] — Tier 2 stored, export reads what the view shows, ADR-045 fixes

### Tier 2 as a parquet with a chained key (issue #10, ADR-089)
- `DataOrchestrator.materialize_tier2()` stores `<name>__T2.parquet` next to the Tier 1 file, with `sparmvet_tier2_key` (Tier 1 key + the join's tier2 steps). A join without tier2 steps stores nothing; a stale T2 file is deleted when Tier 1 is checked or rebuilt.
- ⚠️ HOME no longer falls back to Tier 1 when Tier 2 fails: the error is shown.
- ⚠️ Anchor parquet files are written with Polars (`write_parquet(metadata=...)`), not through pyarrow: categorical columns written by pyarrow could not be read back.

### Export (EXPORT-KEYCHECK-1, EXPORT-T3-1)
- The export reads T1/T2 through the key-checked orchestrator (the "reuse the anchor if the file exists" shortcut is gone) and renders plots from T2, as HOME does.
- The export is refused when the data analysis recipe or the data changed since the view was opened (`EXPORT_NOT_CREATED.txt` explains it).
- Export = Result (T2) plus the AUDITED T3 steps (rows, drops, aesthetic overrides, trail), always applied to the exported plot and its data (issue #25). Exploration filters (not sent to audit) are never exported: no "Include T3" checkbox, no `FILTERS.txt`; reminders in the Export panel and under the filter buttons. T3 data is `T3_data_<plot>.tsv` per plot with audited steps, built on T2.
- README, `report.qmd` and PNG/SVG metadata record the data analysis recipe file-set hash, the data hash and the Tier 1 / Tier 2 keys.

### ADR-045 (behavioural audit 2026-11-06)
- `architect_active_plot` no longer writes a reactive value in a render (`_plot_outcome` Calc); `app/tests/test_render_purity.py` guards all renders.
- Removed `tier_reference`, `tier3_leaf`, `apply_tier2_transforms` and the unmounted outputs `plot_reference`, `table_reference`, `plot_leaf`, `table_leaf`, `handle_plot_brush`. `server.py` is 237 lines.

---

## [2026-05-09] — Export enhancements + notification ghost persistence

### Export panel (EXPORT-2, EXPORT-3, EXPORT-4)
- **EXPORT-4:** Added `export_plot_width` / `export_plot_height` numeric inputs (inches, default 8×5) to Export panel; both values passed to `fig.save()` and recorded in provenance + README.txt.
- **EXPORT-2:** T3 data inclusion is now controlled by an explicit `export_include_t3` checkbox (gated on `t3_sandbox_enabled`), pre-checked when `tier_toggle == "T3"`. Previously auto-detected; non-advanced app features files still fall back silently.
- **EXPORT-3:** `report.qmd` gains TOC (depth 3), `number-sections`, cosmo theme, 11pt font. Plots now use Quarto cross-reference `#fig-<id>` syntax. `_build_methods_section()` helper auto-generates a `## Methods` section from `applied_filters` + active T3 nodes; section omitted when nothing to report.

### Session persistence (UX-NOTIF-2)
- `notification_log` reactive is now serialized to the T3 ghost on every `btn_apply` and restored on session load. Old ghosts without the key return `[]` silently (no migration needed).

### Design decisions
- Gallery clone decoupled from WrangleStudio (design only, GALLERY-CLONE-DECOUPLE-1 — not yet implemented): clone will write a `developer_raw_yaml` node into Home T3 `_pending_t3_nodes`; WrangleStudio instantiation gated on `developer_mode_enabled`.
- EXPORT-TUBEMAP assessed as blocked (headless SVG render for Cytoscape.js required; depends on Blueprint stability).

---

## [2026-05-04] — Export redesign + data analysis recipe modularisation

### Export pipeline (EXPORT-REDESIGN-1, EXPORT-REDESIGN-2)
- **Removed** separate "Export Audit Report" button and its handler (`export_audit_report_ui`, `export_audit_report_download`, `_audit_report_filename`). The `audit_report_enabled` app features flag is now unused by the UI (kept in validator for backwards compat).
- **Removed** "Single Graph Export" accordion panel from the sidebar. Functionality superseded by the scope toggle.
- **Added** 3-way scope toggle `[Global project | Active group | Active plot]` to the Export panel, gated on app features having both `export_enabled`.
- **Added** `data_analysis_recipes/t3_steps.yaml` to the export bundle when T3 has committed active nodes.
- **Added** "T3 Audit Trail" section to `report.qmd` — per-plot table of committed T3 steps + user justifications; deactivated nodes excluded.
- Accordion label renamed from "Global Project Export" → "Export".
- Spec: `.claude/design/export_specification.md`

### Data analysis recipe modularisation
- `1_test_data_ST22_dummy.yaml` rewritten from 1334 → ~290 lines using `!include` fragments under `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/`.
- `figshare_integration.yaml` rewritten using `!include` (224 → 69 lines).
- Templates updated to current schema conventions: `simple_project_template.yaml` (canonical inline showcase), `e_coli.yaml`, `audit.yaml`.
- Fragment conventions + threshold (inline ≤80 lines / ≤2 schemas / ≤3 plots) documented in `.claude/knowledge/data_analysis_recipe_data_contract_rules.md` §6.

---

## [2026-05-04] — joins → joins rename

⚠️ 🔑 **Breaking change to data analysis recipe data contract** — all data analysis recipe YAML files must be migrated simultaneously.

### What changes
| Old | New | Where |
|-----|-----|-------|
| YAML key `joins:` | `joins:` | All data analysis recipe `.yaml` files (~10 config files) |
| Python dict key `"joins"` | `"joins"` | ~21 Python files in app/ + libs/ |
| Role string `"assembly"` | `"join"` | blueprint_handlers, data_analysis_recipe_navigator, wrangle_studio |
| TubeMap node label `"…\nAssembly"` | `"…\nJoin"` | `libs/utils/src/utils/blueprint_mapper.py` lines ~167, ~189 |
| UI labels `"◆ Assembly"`, `"Assembly Output (Input)"` | `"◆ Join"`, `"Join Output (Input)"` | `app/modules/wrangle_studio.py` |

### Motivation
"Assembly" has a specific meaning in bioinformatics (genome/contig assembly). The concept here is purely a dataset join operation. Rename avoids confusion, especially in the Cytoscape TubeMap which the team reads.

### Exception — do NOT rename
- `session_manager.py` ~line 213: `{"assembly": ..., "contracted": ...}` — this is a Parquet file path label, unrelated to the data analysis recipe role.

### Variable name rule
Never use bare `join` as a Python variable (shadows `str.join()`, confusing next to Polars). Use `join_defs`, `join_block`, `join_step`, `is_join_step` etc.

### Execution plan
See task `ASSEMBLY-RENAME` in `.claude/tasks/tasks.md` for the 5-pass VSCode checklist.

---

## [2026-05-05] — Library extraction & module decomposition

### Phase 29: Library extraction

- **New library:** `libs/blueprint_arch/` — extracted `data_analysis_recipe_navigator.py` (core lineage introspection) + `blueprint_mapper.py` (TubeMap DAG generation) from `app/modules/` into a standalone, headless-safe lib.
- **New library:** `libs/test_lab/` — extracted `dev_studio.py` → `test_lab_studio.py` for data utilities and developer diagnostics.
- All imports updated across `app/handlers/` and `app/src/` to reference new lib paths.
- ADR-067: Library extraction standards for headless-safe modules.

---

## [2026-05-09] — Sidebar slot registry & feature flag enforcement

### Phase 31: Sidebar slot registry (ADR-073)

- **Data analysis recipe-driven sidebars:** Sidebar panel layout now declarative via app features files, not hardcoded in Python.
- **Registry:** `app/modules/sidebar_registry.py` — maps panel types (`project_info`, `filters`, `audit_stack`, `blueprint_agent_chat`, etc.) to gate flags.
- **Slot lists:** `config/ui/sidebars/` directory with per-workspace panel sequences (home_standard_left.yaml, blueprint_standard_right.yaml, etc.).
- **Validation:** `app/modules/sidebar_validator.py` — checks panel types against registry, includes existence, gate-flag consistency. Runs at startup alongside AppFeaturesValidator.
- **Right sidebar exclusion fix (task 25-O):** Replaces `bootloader.is_enabled("t3_sandbox_enabled")` hardcoded checks with `bootloader.get_sidebar_config("home", "right").visible` — eliminates ADR-053 (app features name string comparison) violation.
- Verified: 8/8 app features files pass validation.

### Phase 31 (continued): ADR-077, ADR-078 fatal cascades & DeploymentError

- **ADR-077:** Group D cascades (data_analysis_recipe_edit_enabled, blueprint_agent_enabled) now fatal validator errors, not silent bootloader suppression. Establishes no-silent-suppression principle for config decisions.
- **ADR-078:** DeploymentError dataclass + helpers (`format_errors_block`, `exit_if_errors`, `raise_if_errors`) in `app/modules/deployment_error.py`. AppFeaturesValidator retrofitted to return `list[DeploymentError]`. Server startup uses `exit_if_errors` gate.
- **Verified:** 8/8 templates pass; synthetic 3-violation config produces clean formatted error block.
- Phase B (startup gate): IMPLEMENTED. Phase C (full retrofit to bootloader, connectors, data analysis recipe preflight): deferred.

### Phase 31 (continued): Feature implementation

- **BP-AGENT-PANEL-1:** `blueprint_agent_chat` panel registered in sidebar registry; added to BLUEPRINT workspace right sidebar for developer/qa app features files.
- **BP-AGENT-CSS-1:** `.bp-agent-container`, `.bp-agent-message`, `.bp-agent-input-area` CSS rules in `config/ui/theme.css` (§19).
- **21-F-7:** Added `scale_x_discrete` layer to Year-based test plots in 2_test_data_ST22_dummy (ensures Year columns render as discrete categories).
- **TubeMap aesthetics:** Renamed `ref` node type → `add` in blueprint_mapper.py for semantic clarity (additional_datasets now render as "Add Data" nodes).
- **HELP-DOCS-1:** Conditional docs bundling — app checks for `docs/_site/` at startup and logs availability. DEPLOYMENT_CHECKLIST.md documents `quarto render docs/` as pre-deployment routine.

---

## [2026-05-09] — ADR 066–076 rollup

| ADR | Title | Status |
|-----|-------|--------|
| ADR-066 | Rename `joins` → `joins` — avoids bioinformatics term collision; affects all data analysis recipe YAMLs and ~21 Python files | DECIDED |
| ADR-067 | Extract `libs/blueprint_arch/` — pure-Python data analysis recipe navigation + TubeMap; headless-safe, zero Shiny imports | DECIDED |
| ADR-068 | Extract `libs/test_lab/` — absorbs `generator_utils`, renames `dev_studio.py` → `test_lab_studio.py` | DECIDED |
| ADR-069 | Complete Export Audit Trail Standard — audit steps IS the audit trace; auto-included in `report.qmd`; no separate FILTERS.txt for T3 | DECIDED |
| ADR-070 | Functionality-First Deployment Model — app features files are named flag bundles, not the primary concept; behavior is always flag-driven | DECIDED |
| ADR-071 | Deployment Hardening Standard — no CDN links; all assets vendored locally; no secrets in source; cross-panel output prohibition | DECIDED |
| ADR-072 | [RESERVED] — numbering gap; no decision recorded | N/A |
| ADR-073 | Configurable Sidebar Slot Registry — sidebar layout declared per-workspace in app features files; two-layer flag resolution | DECIDED / IMPLEMENTED |
| ADR-074 | Lineage Infrastructure as Shared Provision — `build_plot_lineage` + `get_plot_ids_in_group` in `libs/blueprint_arch/`; export bundle includes lineage DAG | DECIDED / PARTIAL |
| ADR-075 | BLUEPRINT IDE Build Mode — `ui_schema` form builder; action picker; YAML escape hatch; 20-step undo; contextual help | DECIDED / PENDING |
| ADR-076 | BLUEPRINT AI Agent Helper — multi-backend adapter (CLI/API/local); 7 agent tools; HTML-comment tool-call protocol | DECIDED / PENDING |

---

## [2026-05-09] — Audit session (P0/P1 hygiene)

### Phase 32: Audit & documentation (IN PROGRESS)

- **P0 completed:** AUDIT-DEPGRAPH-NOW (deps graph regenerated), AUDIT-HANDOFF-UPDATE (handoff rewritten), AUDIT-RULES-FLAGS-UPDATE (removed stale known-violation annotations; no runtime app features name checks found), AUDIT-ADR072-STUB (ADR-072 reserved stub confirmed; ADR-069 moved to correct chronological position), AUDIT-QUALITY-WRANGLING (empty unreferenced `Quality_metrics_assembly_wrangling.yaml` deleted), AUDIT-PHANTOM-TEST (phantom `test_config_loader.py` reference not present in file — no-op), AUDIT-CHANGELOG-UPDATE (this entry).
- **P0 remaining:** AUDIT-WRANGLE-FLAG (`wrangle_studio_enabled` flag addition to AppFeaturesValidator).
- **P1 queued:** AUDIT-DEMO-APP_FEATURES (flag matrix demo columns), AUDIT-ABROMICS-CHECK (pipeline data analysis recipe structure assessment), AUDIT-PLAN-ORDER (implementation_plan_master.md phase reordering — escalated to sonnet/medium).

---

## Prior phases (Archives)

For phases 3–27, see git log or ADRs 1–76 in `.claude/knowledge/architecture_decisions.md`.

---

## [2026-05-05] — Library extraction (Phase 29)

### New libraries promoted from app/
- `libs/blueprint_arch/` — data analysis recipe navigation, TubeMap rendering, lineage tracing. Moved from `app/modules/`.
- `libs/test_lab/` — formerly `libs/dev_studio/`; unified with test infrastructure.

### Renames
- `app/modules/dev_studio.py` → `libs/test_lab_studio.py` (class retained `TestLabStudio`)
- Imports updated across `blueprint_handlers.py`, `home_theater.py`, `server.py`

### Consequence
All 8 `libs/` packages now follow the two-tier dependency model:
- Tier 1 base: `libs/utils/` (no cross-lib imports; importable by any domain lib)
- Tier 2 domain: all other libs (zero peer-to-peer imports; each independently reusable)
- Tier 3 orchestration: `app/` only (wires multiple libs together)

---

## [2026-05-09] — Sidebar slot registry + lineage + BLUEPRINT IDE design (Phases 31–32)

### Phase 31 — Sidebar configurability (ADR-073 implementation)
- **Added** `config/ui/sidebars/` — reusable panel-list YAML files per workspace/app features combination.
- **Added** `app/modules/sidebar_registry.py` — `PANEL_REGISTRY` dict maps panel types to gate flags and renderers.
- **Added** `app/modules/sidebar_validator.py` — validates sidebar configs and `!include` targets; runs at startup.
- **Added** `scripts/validate_app_features_config.py` — CLI gate for app features files + sidebars (used in CI).
- **Updated** all 8 app features files with `workspaces:` section declaring left/right sidebar slot lists per workspace.
- **Fixes** ADR-053 violation: right sidebar visibility now gated via `bootloader.get_sidebar_config("home", "right").visible` instead of app features name comparisons.

### Phase 31 — Export provenance (partial, ADR-069)
- **Implemented** `LINEAGE-NAV-1`: `build_plot_lineage(plot_id, data_analysis_recipe_path)` and `get_plot_ids_in_group(group_id, data_analysis_recipe_path)` — backward and forward lineage tracing.
- **Implemented** `LINEAGE-EXPORT-1`: `lineage/lineage_graph.json` generation (shared-node DAG) + Mermaid flowchart in `report.qmd`.
- **Implemented** `BP-SCHEMA-1`: `ui_schema` kwarg in `@register_action` and `@register_plot_component`; 19 transformer actions + 7 viz_factory components annotated; `schema_registry.py` reads schemas at startup.
- **Pending** export tasks: EXPORT-HASH-2, EXPORT-VERSION-1, EXPORT-IMG-META-1, EXPORT-AUDIT-COMPLETE-1.

### Phase 32 — BLUEPRINT IDE Build Mode design (ADR-075 + ADR-076)
- **ADR-075** — BLUEPRINT form builder, action picker, Apply gate, YAML escape hatch (read-only / editable), session undo deque (20 steps), contextual help via `__doc__`.
- **ADR-076** — BLUEPRINT AI Agent Helper: adapter protocol (CLI, API, local model backends), tool-call protocol (HTML-comment fenced JSON), 7 agent tools, chat panel, session bundle artifacts.
- **Pending** all form/escape/undo/help/color/agent implementation tasks.

### ADRs authored 2026-05-09
- **ADR-073** — Sidebar Slot Registry (implemented today)
- **ADR-074** — Lineage Infrastructure as Shared Provision (2 tasks implemented)
- **ADR-075** — BLUEPRINT IDE Build Mode (7 tasks pending)
- **ADR-076** — BLUEPRINT AI Agent Helper (10 tasks pending)

---
## [2026-05-09 — afternoon] — Configuration discipline + diagnostic errors (Phase 32)

### ADRs authored
- **ADR-076 (revised)** — BLUEPRINT AI Agent Helper: §10 tool-call protocol (HTML-comment fenced JSON for `claude_cli`) + §11 subprocess isolation (per-session `cwd`, flock single-flight, auth probe). Streaming dropped from Phase 1.
- **ADR-077** — No-Silent-Suppression principle. Group D cascades are fatal validator errors, not silent bootloader rewrites. General principle: *"Silent suppression hides bugs. Silent rewriting hides intent."*
- **ADR-078** — Diagnostic Error Discipline. `DeploymentError` dataclass with five mandatory fields (component, problem, location, fix, who). Phase B delivered (AppFeaturesValidator + server.py + CLI). Phase C committed: SidebarValidator, Bootloader, Connectors, data analysis recipe preflight, troubleshooting catalog, CLI scripts.
- **ADR-079** — Runtime Error Discipline (placeholder). Distinct treatment from ADR-078 because audience (analyst, not operator), fix surface (data/data_analysis_recipe, not config), and render path (Shiny, not stderr) differ. Targets ingestion / assembler / wrangler / viz_factory / T3 apply / Blueprint data analysis recipe validation.

### Tasks closed
- **BP-AGENT-FLAG-1** ✅ — `blueprint_agent_enabled` flag + config block landed in 8 templates; cascade is fatal (Rule 7).
- **DIAG-CORE-1** ✅ — `app/modules/deployment_error.py` + AppFeaturesValidator retrofit + server.py + CLI script updated.

### Files added
- `app/modules/deployment_error.py` — `DeploymentError` dataclass + `format_errors_block` / `exit_if_errors` / `raise_if_errors` / `DeploymentFailure`.

### Files modified
- All 8 `config/app_features/*.yaml` — `blueprint_agent_enabled` flag + (developer/qa) `blueprint_agent:` config block.
- `app/modules/app_features_validator.py` — `_FATAL_CASCADE_GATES` + Rule 7; returns `list[DeploymentError]`.
- `app/src/server.py` — `exit_if_errors()` startup gate replaces `raise ValueError(...)`.
- `app/src/bootloader.py` — Group D cascade explicitly NOT applied (per ADR-077). Docstring points at AppFeaturesValidator.
- `scripts/validate_app_features_config.py` — `format_errors_block()` for output.
- `.claude/rules/rules_app_features_flags.md` — Group D, Full Flag Matrix, Cascade Enforcement §4–5 (now FATAL), Misconfiguration table, Files Governed.
- `.claude/knowledge/project_conventions.md` — new sections 17 (Fail-Fast Configuration Discipline) and 18 (DeploymentError pattern).

### Convention shifts
- New cascades default to **fatal** (validator-enforced). Soft cascades require ADR justification.
- Startup-time errors MUST emit `DeploymentError` records, not bare strings or `raise ValueError`.
- Streaming SSE explicitly out of scope for the BLUEPRINT agent in Phase 1; all backends buffered.

