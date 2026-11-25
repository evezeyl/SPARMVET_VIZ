# Tables no plot reads, and a table as a result: what is decided (scout survey, 2026-11-22; filed and shortened by the coordinator)

Read-only. Tags: DECIDED (ledger line taken by the owner), CONFIRM (rule or design text, or a reading; no ledger line), OPEN, AS BUILT (file:line). Ledger = `.claude/knowledge/decision_ledger.md`.

## Her words (2026-11-22, channel block M532)
"No Tier 3 is not a plot - T3 is the data that goes into a plot ... its still data - Why Tier 2 refuses ? its still data wrangling - in a way for a user a table can be a way of visualize results eg. a summary, quantiles calculations osv ... At T2 can still use wrangling steps that we will want to appear in a table --- eg aggregation, mean, variance - Have the coordinator have agents review the problem - we have to consider that each table Tier can actually lead to information usefull for the user. One of my question is should we had an extra thing like when a table is considered as a visualizable result for a user that it can be shown in the "plot" area but as table ? I need opinions of several agents."

## The two questions
Q1. Should a table that no plot reads be allowed tier 2 steps (aggregation, mean, variance, quantiles, summaries) and a tier 3, as data a user wants to see?
Q2. Should a recipe be able to mark a table as a RESULT for the user, shown in the "plot" area as a table?

## A. Tier definitions
- DECIDED D-0024: T1/T2/T3 defined alike (ordered step list; an empty list keeps the previous node); optional T3 on the plot entry.
- DECIDED D-0179, her words: "T1 feeds T2 feeds T3 feeds plot."
- DECIDED D-0343: no T3 steps means T3 = T2; no T2 steps means T2 = T1; nothing extra is stored then.
- DECIDED D-0237, D-0250: a tier is a mapping (`data_engine`, `steps`); tiers 1 and 2 in a table and a join; tier 3 at the plot entry.
- DECIDED D-0063, her words: "The T3 is the data that goes to the plot BUT not the plot recipe". DECIDED D-0306: tier 3 is "data plot specific"; tier 1 and tier 2 must be buildable.
- DECIDED D-0109 (2026-11-16), her words: "A table on itself can produce results that are interesting for the user but need to have plots". The nearest record to Q2.
- DECIDED D-0310: the data choice offers Source, T1, T2, T3. DECIDED D-0327: exploration filters never change the table a plot uses.
- DECIDED D-0346 (modified in part by D-0451): the dialog line is the lowest level of the lineage that really has steps.
- DECIDED D-0451, her words: tables that no plot reads are also part of a lineage: "at least T1, and T1+T2 and T1+T2+T3 ... We must modify". Whether the line is ticked by default is the review session's reading (CONFIRM).
- DECIDED D-0457: the export holds all tables of a recipe, also those no plot reads; such a table "must be viewable in the data preview". OPEN: which tiers; how she reaches it in HOME.
- DECIDED D-0326, D-0335, D-0343 (not built): at opening every T1 and T2 table is built and stored, the T3 of each plot with its own steps is built, every plot is drawn once.
- DECIDED D-0416 point 1, D-0415: "remove from all the data" writes at T1 of every table holding the key, also a table no plot reads.
- DECIDED D-0447: the reach of a line counts tables the user can open and plots; tables no plot reads are counted apart.
- CONFIRM (rule text, no ledger line): `rules_data_engine.md:26` T2 = "logic or pre-aggregation shared by a Functional Group of plots"; `:56` tier2 holds "plot-specific transformations (aggregations, reshaping to long format, specific subsetting)"; `:27` T2 stored "per join" only (disagrees with `docs/foundations/data_tiering_adr.qmd:32`: "a join, or a table that a plot reads directly").
- CONFIRM (her text in a design file, `home_audit_steps.md:146`, 2026-11-12): "T1, T2 and T3 are defined the same way"; any registered action may be used in a recipe's T3; in audit only filters, drops and removals by key.
- OPEN: no ledger line decides a tier 2 or a tier 3 on a table no plot reads, nor a table marked as a result shown in the plot area.

## B. The refusals, as built
- S07, `libs/utils/src/utils/recipe_check.py:414-417`: "tier2 of a schema applies only when the schema is plotted directly: no plot reads this schema, so these steps would run nowhere (a join reads the tier 1 of its ingredients)". Ordered by the spec row DEC16 (`recipe_format_spec.md:120`, 2026-11-12: "a list that is never applied is a silent wrong result") and `home_audit_steps.md:161` (point 19, "decided 2026-11-12, Eve": a step list that is never applied is refused). No ledger line carries S07.
- J14, `recipe_check.py:825-828`: "tier2 of a join applies only when a plot reads the join: no plot reads this join, so these steps would run nowhere". A follow-up of 2026-11-15 (`recipe_format_spec.md:715`); NO line or text of the owner names J14.
- `libs/utils/src/utils/audit_copy.py:177-179`: an audit step at tier 2 of a table no plot reads is refused ("its tier 2 is applied nowhere and a step ... would be skipped").
- So the reason of all three is one fact AS BUILT: nothing runs the tier 2 of a table no plot reads. The refusals prevent a silent no-op; they are not a rule about what a table may be.
- Tests: `app/tests/test_schema_tier2.py:220-239`; `libs/utils/tests/test_recipe_check.py:154, 205, 272`; `libs/utils/tests/test_audit_copy.py:270, 755-757`.

## C. Where a tier 3 lives today (as built)
- Only in a plot entry, key `tier3` (`recipe_spec.yaml:54, 57, 75`); readers `recipe_tiers.tier3_steps(raw, plot_id)` (`recipe_tiers.py:169-179`).
- `DataOrchestrator.materialize_tier3(recipe_id, plot_id)` (`app/modules/orchestrator.py:690-699`); key `DataAnalysisRecipeKeys.plot_key_of(plot_id)` (`app/modules/cache_keys.py:452-469`); stored next to the T2 table of the target (`orchestrator.py:37, 703`).
- So a tier 3 cannot exist without a plot entry today: its key is a plot key. A tier 2 key exists for every table (`cache_keys.py:447-450, 465`) but its steps are refused when no plot reads the table.

## D. What assumes "a table shown is a plot's table" (as built)
- HOME data preview: `app/handlers/home_theater.py:1670-1679` (the active plot's table), drawn as a grid (`:1702`), placed under the plot (`:1256-1258`). Sub-tabs: one per plot (`:119-143`).
- Export: `app/handlers/export_handlers.py:1344-1382`: files only for tables a plot targets (a branch `task/export-every-table` is being built for T1 of the others).
- Opening build: not built; `app/tests/test_opening_build.py:434-439` asserts an unused source is NOT read at opening, against D-0326.
- Lineage walk: `libs/utils/src/utils/lineage_walk.py:31, 36, 515-517` (on `dev`: a place no plot reads is not a line; a branch `task/lineage-unread-tables-lines`, in review, makes it a line at tier 1).
- `remove_from_all.py`: writes at T1 of every reached table, also unread ones.

## E. What a plot entry is
- Keys (`recipe_spec.yaml:49-57`): `plot_engine`, `ui_label` (required), `description`, `comment`, `taxonomy`, `target_dataset`, `mapping`, `layers` (the last three required), `theme`, `facet_by`, `palette`, `labels`, `guides`, `tier3`.
- Drawn by `VizFactory.render` (`libs/viz_factory/src/viz_factory/viz_factory.py:177`), plotnine only.
- A table in the plot area today: NOT FOUND. No table geometry is registered (`libs/viz_factory/src`: not found; plotnine itself not searched).

## F. Shipped recipes (only the demo recipe was read)
- Tables no plot reads in the demo: joins FastP_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, AR1_MLST_Serotype_Virulence; sources linked to nothing: Quality_metrics, Detailed_summary.
- Aggregations exist in tier 2 of tables that plots read (QA_aggregated_no_key, QA_AMR_per_sample, QA_fanout_exhibit); a join with a group_by in tier 1 (Summary_phenotype_length_fragmentation).
- Plots used to show numbers: the eight QA canary plots ("the expected numbers are in its title").
- An unread aggregation planned and commented out: `Detailed_summary_wrangling.yaml:38-41` ("for barplot").
- A plot file present but not mounted: `plots/FastP_reads_boxplot.yaml`.

## G. Gallery and BLUEPRINT
- Gallery: an example is a plot entry with a taxonomy; its name is the plot entry's `ui_label` (`rules_gallery_standards.md:9, 18, 76-95`).
- BLUEPRINT TubeMap: node roles are source, join, plot (`libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py:20-37, 406`); the group and plot manager handles `analysis_groups` and plots only (`libs/blueprint_arch/README.md:144-163`).

## H. Earlier notes (paths, not opened)
`.claude/design/feature_extension/composite_dashboard_home2.md`; `.claude/design/feature_extension/dashboard_frontend_topology.md`.

## Contradictions in the records met on the way
1. D-0451 (her "T1+T2", "T1+T2+T3") against S07, J14 and the audit copy refusal: no ledger line says which governs.
2. D-0109 (a table alone needs plots) against her question of 2026-11-22: no line answers it.
3. `test_opening_build.py:434-439` against D-0326 (an unused source at opening).
4. `rules_data_engine.md:27` against `docs/foundations/data_tiering_adr.qmd:32` (where tier 2 is stored).
5. The draft `adr_100_recipe_format_1_draft.md:104` is out of date on schema tier 2.
