# Lineage and scope in HOME: the scientist and data scientist view (viewpoint 2 of 3)

Status: WRITTEN EARLY, appended as work goes. Research only; no code or recipe changed. Labels: verified (run or read at file:line), reasoned, not run.
Scratch scripts: tmpAI/panel/lineage_scope/scratch/ (run with `PYTHONPATH=. ./.venv/bin/python`).

(sections are appended below as they are verified)

## A. Worked case 1 (verified, run): remove ONE entity (sample_id 32557144) at three places, demo recipe
Scripts: scratch/ds_lib.py, cases.py, case1.py, case1b.py. Method: base build and each audit copy built from scratch into its own empty folder (`audit_copy.start_audit/add_step`, same engine functions as run_audit), every one of the 73 nodes (T1/T2/T3) compared by content digest. Step: `modif_filter sample_id not_in [E] na=keep`. Demo has 42 entities; E has 2 rows in ResFinder, 8 in Summary, 24 in VirulenceFinder, 1 in metadata.

| place | nodes that differ | what each plot then shows for E |
|---|---|---|
| T3:amr_heatmap | 1 (the plot) | gone from amr_heatmap only (74 -> 72 rows, 42 -> 41 entities). Every other figure still shows E. |
| T1:ResFinder | 15 of 73 (5 plots, 4 tables below + their T2) | gone from amr_heatmap, qa_amr_genes_per_sample, qa_fanout_rows_per_sample (42 -> 41 entities). STILL PRESENT in virulence_bar and virulence_variants: ST22_Anchor 617 -> 608 rows, E 18 -> 9 rows, entities 42 -> 42. |
| T1:metadata_schema | 32 of 73 nodes (10 plots below by `plots_below`, 9 of them change) | E is NOT removed from 7 of the 9 changed plots: the left joins keep E with source/year/country = NULL (ResFinder_with_metadata: E 2 -> 2 rows, country Norway -> null). E leaves only mlst_bar and year_distribution (2 plots) (MLST_with_metadata T2: 33 -> 32 rows). qa_population_zscore keeps E with country NULL and the same n50_zscore (0.4976). |

Reading: "reaches 10 plots" at the metadata means up to 10 figures CHANGE (9 do), not that the sample is gone. A user who wants "remove this sample" and picks the metadata because it is "the highest place" gets a figure in which the sample is still counted, now under NA. This is not a bug (D-0549/G8 say "below" is not "gone") but it is exactly what a reach count alone cannot say. Other entities' rows: 0 changed in every compared table (others_rows_changed = 0,0) for the removal; so for a plain removal the other samples are untouched in these three places (a calculation over all entities below would change that: see G15 in PATHS_AND_DERIVED_AGREED.md; not rerun here).
Build time of each audit copy from scratch (all 73 nodes, 42 entities): 1.3 to 1.4 s; base build 1.15 s.

Discrepancy to flag (not resolved): PATHS_AND_DERIVED_AGREED.md (2026-11-23) says a step at the metadata changes 13 of 17 plots; on today's recipe `plots_below(T1:metadata_schema)` returns 10 and the removal changes 9 (verified, this run). The recipe or the code moved since; the display must compute its numbers, never quote the study.

## B. Worked cases 2 to 6 (verified, run; scripts case2.py ... case6.py, timing.py, middle.py, plans.py, awkward.py in scratch/)

### Case 2: a filter on values, `identity >= 98` on ResFinder (74 rows, 42 entities, 4 of them completed lines with identity NULL)
| place | na | ResFinder rows / entities | amr_heatmap | virulence_bar (ST22_Anchor) | qa_amr_genes / qa_fanout (entities) | nodes differ |
|---|---|---|---|---|---|---|
| T1:ResFinder | remove | 74->28 / 42->19 | 28 rows, 19 ent | 617->410 rows, 42 ent (left join keeps all 42, ResFinder columns NULL) | 19 / 19 | 15 |
| T1:ResFinder | keep | 74->32 / 42->23 | 32 rows, 23 ent | 617->410, 42 ent | 23 / 23 | 15 |
| T2:ResFinder | remove | T1 unchanged | 28 rows, 19 ent | unchanged | unchanged (42) | 2 |
| T3:amr_heatmap | remove | unchanged | 28 rows, 19 ent | unchanged | unchanged | 1 |
Reading: (1) the same sentence "keep identity >= 98" gives N = 19 in two figures and N = 42 in the virulence figures in the same job; the user must know the N differs per figure, a reviewer will ask. (2) `na=remove` against `na=keep` is 19 against 23 entities: the 4 are the completed "Not Found" samples (no ResFinder line, `status = Not Found`): they are biologically "tested, no resistance gene", and `remove` makes them disappear from the heatmap and the counts as if untested. (3) T2:ResFinder and T3:amr_heatmap give the same heatmap here (28 rows) but T2 is exported as a table; T3 is only the figure.
Engine semantics checked on a small table (awkward.py, verified): NaN is a number larger than every number (`gt 5` keeps NaN, `lt 5` drops it; `na` does not touch it); `na=remove` drops null for EVERY operator including `ne` and `not_in`; `between` and `in` drop null with remove; an integer 5 against a Float64 column is accepted (`x gt 5` ok); a number against a String column is refused with a plain sentence ("The value 1 is a number, but this column holds text"); an ID typed with a leading space or in another case MATCHES NOTHING and is not refused: removal of " 32557144" from T1:ResFinder ran in 0.58 s with 0 plots affected and no message (timing.py, verified).

### Case 3: remove the lines the completion added (marker `ResFinder_not_in_original_data`, 4 entities: 40503315, 52676003, 75442817, 87836481)
| place | ResFinder | amr_heatmap | qa_amr_genes_per_sample | virulence_bar |
|---|---|---|---|---|
| T1:ResFinder | 74->70 rows, 42->38 ent | 70 rows, 38 ent | 42->38 rows: the 4 had n_amr_genes = 0 (a real zero) and leave the plot | unchanged, 42 ent, 617 rows |
| T2:ResFinder / T3:amr_heatmap | T1 unchanged | 38 ent | unchanged, 42, the four still show 0 | unchanged |
| T1:ResFinder_with_metadata | - | unchanged (74) | unchanged | unchanged |
| T1:ST22_Anchor | REFUSED: "column 'ResFinder_not_in_original_data' is not in the table" (the marker is dropped by the join's select) | | | |
Reading: removing "the completed lines" is not removing the samples. The same step moves the denominator from 42 to 38 in the AMR counts and leaves it at 42 in the virulence plots. For the 4 samples the zero count ("no resistance gene found") turns into "not in the figure": a prevalence computed from the figure changes. The marker column is held by 39 of the 73 real nodes; only some places hold it; the user is told only by an error after trying (T1:ST22_Anchor), unless the display asks the engine's plan.

### Case 4: a column drop
- drop `gene` at T1:ResFinder, `identity` at T1:ResFinder, `country` at T1:metadata_schema: REFUSED before any build (AuditCopyError "The app cannot YET follow the column ... to the end ... the join reads 'MLST', whose columns the recipe does not give here ... the recipe does not say what polars_unpivot does to the columns"). So on the demo a T1 column drop is not possible at these places; it says why. `sample_id` at T1:ResFinder is refused as a join key of 4 steps (names them).
- drop `gene` at T2:ResFinder: accepted, builds, 2 nodes differ, amr_heatmap table loses `gene` (columns after: sample_id, predicted_phenotype, identity, overlap, marker, status, total_gene_count) while the plot reads `gene`: the audit run reports no failure and counts the plot as "affected" (the build is lazy; drawing not run). An affected plot is not the same as a plot that still draws.
- The recipe graph's own column walk (`RecipeGraph.column_info`) is unknown at 50 of 87 nodes, and at the 12 nodes where it claims a column list it is WRONG on the completion marker column (it omits `<table>_not_in_original_data`; 12 of 23 known nodes mismatch the real table, all on the marker). The engine's plan book (`compose_plan_book`, 0.27 s on the demo) matched the real tables at all 41 places checked (0 mismatch) and gives the type. Conclusion: "where does this column exist, with which type" must come from the plan book, never from the graph walk (verified).

### Case 5: a statistic computed before or after the removal (QA_population_zscore, n50_zscore)
Remove E at T1:Quast: 41 other entities' n50_zscore change (max change 0.026); same at T1:QA_population_zscore; at T3:qa_population_zscore: 0 other changes (E hidden, the other z-scores still computed WITH E). Both are defensible; they are different statements ("population without E" against "population with E, E not shown"). The graph knows the steps below the place (`Node.steps`: 12 `polars_with_columns`, 4 `polars_group_by`, 3 `polars_unpivot`, 21 `polars_join` on the demo) but not whether a `with_columns` is a window over all rows.

### Case 6: a removal that works by a side effect (the metadata case again)
E (year 2024, in the author's range) leaves `mlst_bar` and `year_distribution` after a removal at T1:metadata_schema only because the metadata columns of E become NULL and the author's own step `T2:MLST_with_metadata modif_filter year between [2023, 2025] na=remove` drops NULL years. The removal is not what removed it. At the 7 other changed plots E stays with country/year NULL. 19 of 21 demo joins are `left` (they keep the entity), 2 are `inner` (ST22_Anchor and AR1_MLST_Serotype_Virulence with the look-up APEC_STEC_virulence_genes, which has no sample_id: a filter there changes ST22_Anchor 617->350 rows, entities 42->42; the removal-by-id is not possible there).

### Measured cost (verified on the demo: 42 entities, 28 tables, 73 nodes; real data not measured)
- Full build of all nodes from scratch: 1.15 s. One audit copy by `run_audit` (reuses unchanged tables): 0.27 s (T3:amr_heatmap), 0.59 s (T1:ResFinder, 5 tables built), 1.04 s (T1:metadata_schema, 12 tables built). Plan book: 0.27 s.
- The count at the chosen place alone (one table with the step, not the tables below): 0.06 s (metadata) to 0.17 s (ResFinder): e.g. ResFinder 74->72.

### Case 7: result tables (a table no plot reads) (verified, result_table.py)
Six on the demo: Quality_metrics, Detailed_summary, FastP_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, AR1_MLST_Serotype_Virulence. For all six the only child of the T1 is its own T2 and no other table reads them (forward of T1 holds no T1). CORRECTION to the architect's file (section 1, line 13): "ResFinder_with_metadata is not a dead end: it feeds ST22_Anchor" is false on the graph; ST22_Anchor reads ResFinder itself (parents FastP, metadata_schema, ResFinder, MLST, VirulenceFinder, APEC_STEC_virulence_genes).
A removal of E at T1:Quality_metrics / T1:ResFinder_with_metadata / T1:AR1_MLST_Serotype_Virulence: exactly that one table is rebuilt, key changed, rows 42->41 / 74->72 / 342->333, `affected_plots` = [] in all three. A screen that says "no plot is affected" would be true and would hide that a table in the export changed.

## 1. What makes the choice of scope correct (answer to question 1)

What decides a correct choice is not the place but what lies between the place and each figure, and what the step does at the place. Verified on the demo; "Source" gives where the information can be read.

| What the user must see before confirming | Why (case) | Source (verified unless said) |
|---|---|---|
| The names of the tables and plots below each candidate place, with their analysis group; the plots below the same originals that the open plot is not below ("also feeds 10 other figures") | metadata reaches 10 plots, 9 change; from 11 of the 17 plots the originals feed 10 other plots (graph run) | `graph.below`, `plots_below` |
| For each plot/table below: the recipe steps between the place and it: join kind (19 left, 2 inner), filters that remove nulls (`na: remove`), group_by, unpivot, with_columns, fill_null, sort | cases 1, 5, 6: the same removal acts through these | `Node.steps` (action names are in the graph; params in the recipe) |
| Whether the column the step needs exists at the place, its type, and whether another table below renames or recomputes it | case 3 and 4 | the engine's plan book (0.27 s, 0 mismatch at 41 places), NOT the graph walk (unknown at 50 of 87 nodes; wrong on the marker) |
| That the audit step runs AFTER the recipe's own steps of that tier (so `status`, `total_gene_count` exist only after) | `ResFinder` T1 has `with_columns` steps | `test_audit_run.py` docstring (read; not rerun) |
| How many rows and entities the step touches AT THE PLACE; how many null values the column holds there; which of the typed ids exist at the place | case 2 (4 null identity = the completed "Not Found"), whitespace id removes 0 silently | one table with the step: 0.06 to 0.17 s (middle.py) |
| That "below" is not "gone": the paths where the place is not the first table of a left join keep the entity with NULL columns | cases 1, 6 | graph + join steps; coverage per incoming path (G27 of the study) |

Per kind of step:
1. Filter on values: rows and entities removed at the place; the `na` choice and the number of null rows it decides (case 2: 19 against 23 entities); NaN is not null (it is larger than every number, `gt` keeps it); type of the column; below, the entities that survive in left-joined tables with NULL columns (virulence_bar keeps 42), and the figures whose N differs (19 against 42).
2. Removal of entities by id: which ids exist at the place (a whitespace or case difference removes nothing and raises nothing: 0.58 s, 0 plots affected); rows per id at the place (E: 2 rows ResFinder, 1 metadata, 8 Summary, 24 VirulenceFinder); at a place that is not the first table of the entity's path (a left join with the metadata first) the id stays: case 1 (E stays in 18 -> 9 rows of ST22_Anchor, and in 7 of 9 changed plots at the metadata); the tables with no `sample_id` (APEC_STEC look-up) cannot be removed by id and are refused.
3. Column drop: exists at the place or not (plan book), type, which plot mappings read it (`graph.plot_columns`: amr_heatmap reads `gene`; after a drop at T2:ResFinder the audit run builds and counts the plot "affected" although its mapping column is gone: drawing not run); a join key is refused with the joins named; renames.
4. Removal of the completed lines (marker `<table>_not_in_original_data`): where the marker exists (39 of 73 nodes; refused at T1:ST22_Anchor), how many lines (4 in ResFinder), that these entities are real zeros in the AMR counts (n_amr_genes = 0 for the four) and leave the figure, and that the other figures keep them (N 38 against 42).

Two or three places where the same step gives a different figure (verified):
- E removed at T1:ResFinder: 3 of the 5 plots below lose E; virulence_bar and virulence_variants keep E (18 -> 9 rows). At T3:amr_heatmap: 1 figure only. At T1:metadata_schema: E stays in 7 of 9 changed plots (NULL metadata), leaves 2 (one by the author's own `year between ... na=remove`).
- `identity >= 98` at T1 against T2 against T3: the same heatmap (28 rows, 19 entities) but T1 also changes the exported T1, the 4 joined tables and 5 plots; at T1, 617 -> 410 rows in ST22_Anchor with 42 entities; T2 and T3 leave them.
- E removed before or after the z-score: 41 other values change (max 0.026) or 0.

## 2. The six proposals, each against "does it carry this at the moment of the choice, without hiding a step" (answer to question 2)

Scientist's rule: the information of section 1 is the contract; a proposal is only a way to show it. None of the six, as described by the architect, shows the steps between the place and the figures, the plan-book column presence or the "also feeds other figures" list. The architect's `LineageNode` has reach counts and `columns` from the graph walk; both are insufficient (the walk is unknown at 50 of 87 nodes and wrong on the marker).

| | Can it carry the information? | Where a user is misled | To make it honest |
|---|---|---|---|
| P1 outline | Best: a sentence and a list per row, expandable; the same text for the screen reader and for the export. | A DAG drawn as a tree: a joined table under 6 parents appears once ("see above") and a reader may think the figure below is reached by one path only; collapsed rows hide affected plots; the indent suggests "order of processing"; a row that says "T1 ResFinder" hides whether T1 has recipe steps (21 of 28 do, 7 do not) | A badge that stays when collapsed: "N tables, M plots below"; the names on expand; a "also read through: <other parents>" line on every joined row; "recipe steps: n" on each tier row |
| P2 server SVG | Only if text is added; the picture carries topology, not text. | Distance and column of a node are read as order or size; crossing edges hide which of two lines reaches a plot | Arrows exactly "reads from"; no size or distance meaning; text twin |
| P3 Cytoscape | Topology and class colours; text only in a side panel. | Hide/show of the neighbourhood removes the 10 other plots below the same originals, so the user sees only her own path; derived/blocked by colour or dash; a compound "table" box hides which tier has steps; canvas is silent to a screen reader | Always show "also feeds N other figures" with names; badge text on the node; text twin |
| P4 Sankey | No. | A width is read as an amount of data; the quantity (plots below) is not additive (a plot under two tables counts twice); a rows or entities width would be a measure not computed at the choice | Do not use. If a width ever appears, label it "number of figures below", never rows or samples |
| P5 columns | Good per node (a detail pane has room for the section 1 list). | One node at a time: parallel branches and the other figures of the same originals are out of sight; the blocked/derived state of a place not visited is not visible | A fixed strip "chosen so far" and "figures not reached" |
| P6 hybrid | As P1 plus orientation. | Map and outline disagree; the map folds plots into a count and hides names | One JSON for both; the outline holds every name; map is read-only |

In all: "reach" must be named as what it is: the figures that are recomputed, not the figures from which the sample disappears. A place whose reach has a left join or an `na: remove` below must say so on the row.

## 3. Is a measured count needed before confirming? (answer to question 3)

Scientist's view, not a decision (D-0545/D-0546 say the effect is known after Apply; I do not contradict that; I give evidence):
- Structural reach is necessary and, alone, misleading: ResFinder reaches 5 plots, the sample leaves 3; metadata reaches 10, 9 change, the sample leaves 2 and 1 of those by an accident of an author filter.
- A measure per plot before confirming is not needed for a defensible choice IF the structural display tells what reach means, lists the steps below, and the result after the step shows per node rows and entities before -> after (and "no row removed" when nothing moved: `affected_plots` already means a content difference, ADR-101 point 6) with the step removable. A reviewer asks N per figure; that comes from the measure after.
- A cheap, correct middle exists: the count at the chosen place only (one table with the step: 0.06 s metadata, 0.17 s ResFinder on the demo, verified): rows, entities, null rows, ids found, before -> after. It catches the two silent cases (an id typed with a space; a threshold that removes nothing or everything: `gt 1000` gives 0 rows in amr_heatmap with no error, verified) and the `na` case.
- Cost of a whole audit copy on the demo (verified): 0.27 s (plot), 0.59 s (ResFinder), 1.04 s (metadata); full build 1.15 s; real data not measured, so "per place preview" could be offered on request, not run for every candidate. The `PlaceAudit` memo holds one signature (`PlaceAudit._memo`, audit_view.py): previewing several candidates alternately would recompute (reasoned, not run).

## 4. The two views (answer to question 4)
- Whole recipe: where a table is used (metadata is read by 11 tables), the shared parents (ST22_Anchor has 6 parents, metadata feeds 10 plots), the 6 result tables, the plots that read an original directly (amr_heatmap reads ResFinder tier 2), the tables with no sample_id, which tier of which table has recipe steps. Must never omit: result tables; the plots that read a table directly; an original read by several tables; the unknown states; the empty tiers (saying empty).
- From a selection (one figure, or one table): the path back to EVERY original (4 for qc_reads, 6 for virulence_bar) and forward to everything below; it must also show "the same originals also feed N other figures" with names (10 for virulence_bar, 4 for amr_heatmap), else the user chooses a place on her own figure's path without seeing she changes others. Verified numbers: graph run.

## 5. A result table with no plot (answer to question 5)
- Meaning: a step at T1 of a table nobody plots changes only that table and everything exported from it; on the demo exactly one table is rebuilt, no plot changes (case 7, verified). Only tier 1 can exist there (recipe check S07/J14 refuse tier-2 steps on a table no plot reads, `export_handlers.py` comment lines 68-75, read). Its tier 2 node in the graph is the same table.
- Must be shown: that it is a result table (no figure reads it), its description (all 14 joins and 12 schemas of the demo carry `description` and `ui_label`, verified), its rows and entities before -> after at the place (this IS the whole effect), that "0 figures change" is not "nothing changed", and that its T1 file is in the export (D-0457: the export writes the tier 1 file of each table no plot reads; read, export not run).
- Effect verified: by the one-table count (0.06 to 0.17 s) and, after Apply, by the changed T1 key and rows. `affected_plots` is empty and must not be the message.
- Export: the baked recipe appends the step at the end of that tier (`bake_place_steps`, read) and `place_step_records` lists `plots` = [] for it; whether `started_from` is empty for a place outside the open plot's path: not verified (the architect also did not verify).

## 6. What each proposal must record so the choice can be reconstructed (answer to question 6)
Recorded today (read at `audit_places.place_step_records`): id, place (node id and words), `started_from`, action, params, reason, `committed_at`, the plots below (structural). NOT recorded today: the other places that were offered, the tier/step position, the warnings or sentences shown, the measured effect, whether the plot count was a reach or a change, the unknown states.
For every proposal the same record is needed (the display is irrelevant to it): (1) the chosen place(s) and the derived places that followed (ids); (2) the places offered at that moment and why each other was refused or not chosen (the graph is a function of the recipe, so a hash of the recipe plus the list suffices; a sentence list is more readable in the report); (3) the notes shown (left join, `na: remove` below, aggregation below, unknown), as the sentences as the user saw them, because wording changes between app versions; (4) the measure after (per node rows and entities before -> after, the plots that did not change); (5) the parameters including `na` and the ids as typed and the ids found at the place; (6) the reason (required today). A picture (P2 to P4) records nothing by itself: the export must hold the text, never the drawing. With the whole/selection views: record only the choice, not the view. Same data and recipe -> same record is required: the notes must be computed from recipe and data, not typed.

## 7. Ranking, the scientist's view (answer to question 7)
1. P1 outline (as the real control and the record), 2. P6 (P1 plus a read-only map; accept the architect's first choice under the conditions below), 3. P5 (as the view from a selection), 4. P3 alone, 5. P2, 6. P4 (do not use).
Where I disagree with the architect:
- His contract (reach counts, `columns` from the graph walk) is not enough for a defensible choice: the walk is unknown at 50/87 nodes and wrong on the completion marker (12 of 23 known nodes); use the plan book. Add: steps between place and figure, names of the other figures fed by the same originals, notes (left join, `na: remove`, aggregation).
- "ResFinder_with_metadata feeds ST22_Anchor" is false (verified).
- He scores "clarity of shape" high for P3/P6; for defending a figure the text per node matters more than the shape.
- His "plots folded into a count badge" on the map hides the affected plots; names must stay reachable.
I accept P6 first if: (a) the outline holds every name, note and count and the map only highlights; (b) both come from one data object; (c) unknown is shown as "unknown", not as absent; (d) the notes of section 1 exist; (e) the record of section 6 is written; (f) a result table is a first-class row with "no figure reads it" and its own before -> after.
Questions for the user viewpoint: Is "figures recomputed" understood, or does she read it as "figures where the sample disappears"? Does she want the count at the place before Apply (0.06 s) and a per-figure measure after, or an on-request preview of each candidate? Would she read a note per left join or only one summary line? Does she want "also feeds N other figures" at the choice or after? Is the word "tier" understood on a node?
Not run: the drawing itself, the export bundle, real-size data, the plan book in a deployment where it fails (`PlanFailure`), the audit dialog, the "previewing several candidates alternately" cost, drawing of the plot after a column drop.
