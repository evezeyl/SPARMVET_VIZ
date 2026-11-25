# Facts for the panel "an independent lineage picker in HOME" (scout survey 2026-11-22, read-only, nothing run; filed by the coordinator)

The owner's order: ledger D-0496 (her words in its evidence field). "read" = read at file:line by the scout; "reasoned" = counted or inferred from what was read. Paths from the repository root.

## 1. Her idea, in her words
- "No I think my idea is more an independent lineage picker ... so you can pick every original data and see all lineages that goes from there. that means you can pick major lineages that are not linked to each other and on the lineage you can see how it branch and what to see in the table"
- "if we could link find what is the result viwe to what is the original data file that would allow both I think"
- "N2 ... I think the lineage view was already an idea and that could work well because we see the branching - and it can be in a popup window ...and yes a long recipe needs a layout but wat if we combine with N1 - up to the original data file so you can pick by linked lineages ?"
- The case she keeps in view: something to remove (a filter) "that is not seen at the mlst_bar level" (it shows in an earlier table: the join or a derived table). And a table no plot reads (D-0457: "Must be and yes must be viewabøenin the data preview"; how the user reaches it is open).
- Hypothesis NOT confirmed by her (D-0496: "wait for the panel"): the recipe form with derived tables (`derived_tables` with `from:`; a result has no author steps).

## 2. DECIDED / CONFIRM / OPEN (ledger `.claude/knowledge/decision_ledger.md`)
DECIDED
- D-0310: the data choice in Exploration offers Source, T1, T2, T3; "the filters must show what is true in T3 when viewing T3, and what is true in T1 when viewing T1". (CONFIRM: it does not say whether a table OUTSIDE the open plot's lineage may be chosen; its words tie the choice to the plot.)
- D-0178, D-0311: exploration filters are built on the table viewed and are cleared when the viewed table changes. D-0327: exploration never changes a plot, a stored table or the export.
- D-0457: every table of the recipe is exported and must be viewable in the data preview, also those no plot reads. OPEN there: how the user reaches such a table.
- D-0451: tables no plot reads are part of a lineage and are lines of the audit dialog.
- D-0485, D-0487: a result entry is a plot or a table; the result is the last stage; "maybe the result should be the default at opening but the user must still be able to navigate because it needs that to explore data (incl for audit to be able to verify where)"; the badge "result or earlier stage" accepted.
- D-0488: every preview says the rows total and the hidden columns.
- Audit dialog: D-0022, D-0093 ("the user need to choose at which point (node) to apply"), D-0316 (every place the step reaches is ticked at opening), D-0346 (tick lines are distinct tables, each with its reach), D-0347 (the walk goes back, forward, back), D-0325 (the places are found by asking the engine for the plan), D-0450 ("Sorry do not get wrong results because we did not select the correct scope"), D-0415 (a separate option "remove from all the data", independent of the lineage).
- D-0027: "raw YAML removed; node popup in its own window as a pure function". D-0020: one candidate step at a time, previewed in a modal. D-0015: the software informs, warns, lets the user decide.
- D-0344: a named join takes only source tables ("revisit if needed").
- D-0309: "We will need to go back to the blueprint design before its build - because we had the lineage/tube map also to leverage". D-0348: BLUEPRINT comes after HOME, "then we know what we can reuse from the home design".
- D-0463: a discriminating colour already in the palette may be picked; green liked (which colour means what: not decided).
Design files (decided 2026-11-12/13, older than the ledger lines above)
- `.claude/design/spaces/HOME.md:125`: "the lineage popup is the navigator: the nodes drawn as a tree from the datasets to the plots, a click shows the node's first rows (read-only)"; `:48` a read-only popup per node, own window.
- `.claude/design/home_audit_reading_guide.md:113` O11 "DECIDED (2026-11-13)": "the lineage popup as the navigator of every node".
- `.claude/design/home_audit_steps.md:124-138`: the selector Source | T1 | T2 | T3; the lineage popup for other nodes; "The lineage chain is also available on request as a read-only layered list (per node: name, description, steps in plain words, key present, rows and samples, plots that read it)".
ADRs
- ADR-039 (PROPOSED), ADR-040 (partly built), ADR-082: the TubeMap and the Lineage Rail belong to BLUEPRINT. ADR-074: lineage infrastructure is a SHARED provision; "No lineage SVG in HOME export" (section 5). ADR-105: audit acts along the lineage (not built). ADR-045 Two-Category Law (pure logic in libs and modules, Shiny wiring in handlers).
OPEN (nobody decided)
- Whether a HOME user may view a table outside the lineage of the open plot (as built: no).
- Whether the picker popup is the same window as the node popup of D-0027 or another.
- Where the drawing of a lineage belongs (BLUEPRINT's own, or shared).

## 3. What exists in code
Shared recipe graph (`libs/utils/src/utils/recipe_graph.py`; recipe only, no data needed)
- Nodes: DS:<source>, T1:<table>, T2:<table>, T3:<plot>. Edges: source to T1; T1 of an ingredient to T1 of a join; T1 to T2; T2 to T3 of each plot that targets the table.
- `lineage_forward(node)` = everything that descends from a node; `lineage_back(node)` = everything it depends on; `plots_reading`, `source_tables`, `source_tables_of_plot`, `source_tables_of_table`, `parents`, `children`. So "all that descends from source X" and "all sources of result Y" exist as functions today.
- NOT there: a function for the separate trees (connected components); a T3 node for a table no plot reads.
- The lineage walk (`lineage_walk.py`, `lineage_records.py`: lines, reach, `no_plot_reads`) follows a COLUMN and needs the engine's plan (the data files must exist). No app runtime code calls the walk yet (only libs and tests).
BLUEPRINT's TubeMap and Lineage Rail
- Drawn with Cytoscape.js 3.29.2 + dagre 0.8.5 + cytoscape-dagre 2.5.0, vendored locally (`app/src/www/vendor/`, VENDOR_MANIFEST.md). No Mermaid or other graph library is vendored.
- The element builder `libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py` is headless (no Shiny) and stands on the recipe graph through the navigator. Its roles and colours are BLUEPRINT's (trunk, add, meta, wrangle, branch, plot).
- The drawing function `initCyTubeMap` lives in `app/src/ui.py:134` (app-wide), but its click sends the input `blueprint_node_clicked` (`ui.py:288`). The map is shown only with `blueprint_enabled`.
- Known defects of the map (ADR-040 lines 707-731): a flat left-to-right graph, no lanes, redraw flicker on every reactive change, limited node shapes; legend colours off the palette (ADR-082 line 3929).
- HOME's export already imports the navigator (`export_handlers.py:1703`) for `lineage_graph.json` and the "Data Lineage" section of the report (a Mermaid block drawn by Quarto, one graph for all plots).
HOME today (`app/handlers/home_theater.py`)
- "Table to view: Source | T1 | T2 | T3" (default T3, provisional). The "Source table" list holds ONLY the source tables that feed the open plot (`:1441-1459`, `_source_tables_of` `:402-414`).
- Every view is resolved from the open plot (`_resolve_active_lf` `:485-518`): as built NO table outside the open plot's lineage can be shown. In particular a JOIN or an intermediate table that the plot's table is built from is not reachable either: T1 and T2 are those of the plot's own target table only.
- The orchestrator can already build any table by its name: `read_source(recipe, dataset)`, `materialize_tier1(recipe, collection, ...)`, `materialize_tier2(...)`; tier 3 takes a plot id (`app/modules/orchestrator.py:298, 431, 589, 690`). (Not checked: what it does for a name that is not a table.)
- Modals HOME has: the propagation modal of the audit (`filter_and_audit_handlers.py:970-1116`, a radio "This plot only / All plots / All plots except"), an aesthetic modal. No popup window, no node popup (D-0027 is not built), no "Create audit step" dialog with tick lines (decided, not built).
- Badges (`app/modules/view_badge.py`): "Viewing: T2", "T2=T1", "T3=T2=T1", "table '<id>'".

## 4. The demo recipe as the example (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`; reasoned from the file)
- 12 original data files, 16 joins, 17 plots. It is also the LARGEST shipped recipe (the next has 8 entries). About 85 graph nodes when every stage is a node.
- No plot has tier 3 steps of its own (T3 = T2 for all 17). No join takes another join. Longest path: data file, its T1, the join's T1, the join's T2, the plot.
- Separate trees (no shared table): 
  - Tree A: 8 data files (`metadata_schema`, `FastP`, `Quast`, `Bracken`, `ResFinder`, `MLST`, `VirulenceFinder`, `APEC_STEC_virulence_genes`), 14 joins, 15 plots. Held together by `metadata_schema` and the big joins.
  - Tree B: `Summary`, `Summary_quality`; 2 joins; 2 plots.
  - Tree C: `Quality_metrics` alone. Tree D: `Detailed_summary` alone. (No join, no plot: tables no plot reads.)
- What you see when you pick ONE data file (its descendants):
  | data file | joins | plots |
  |---|---|---|
  | `metadata_schema` | 13 | 13 |
  | `Quast` | 4 | 5 |
  | `ResFinder` | 4 | 5 (one plot, `amr_heatmap`, reads the data file directly) |
  | `MLST` | 3 (`MLST_with_metadata`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`) | 4 (`mlst_bar`, `year_distribution`, `virulence_bar`, `virulence_variants`) |
  | `FastP` | 3 | 3 |
  | `VirulenceFinder` | 3 | 3 |
  | `Bracken` | 2 | 1 |
  | `APEC_STEC_virulence_genes` | 2 | 2 |
  | `Summary_quality` | 2 | 2 |
  | `Summary` | 1 | 1 |
  | `Quality_metrics`, `Detailed_summary` | 0 | 0 |
- A table made from several data files appears in several trees: 12 of the 16 joins (`ST22_Anchor` has 6 data files, `QC_Reads_Anchor` 4, `AR1_...` 4).
- The path UP from one result, example `mlst_bar`: `mlst_bar` reads `MLST_with_metadata` (tier 2 with steps), built from `MLST` and `metadata_schema`. Today a user on `mlst_bar` can view: the two data files as read (Source), and T1, T2, T3 of `MLST_with_metadata`. Example `virulence_bar`: reads `ST22_Anchor`, built from 6 data files.
- Tables no plot reads at all: joins `FastP_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `AR1_MLST_Serotype_Virulence`; data files `Quality_metrics`, `Detailed_summary`. Today none of them can be opened in HOME.
- One plot file in the folder is referenced by nothing (`plots/FastP_reads_boxplot.yaml`).

## 5. Records the idea meets (named, not judged)
1. D-0310 ties the data choice to the open plot; the picker "does not depend on the selected result".
2. ADR-039/040/082 place the tube map in BLUEPRINT; ADR-074 says the lineage infrastructure is shared; D-0309 and D-0348 expect reuse between HOME and BLUEPRINT.
3. HOME.md:125 and O11 (2026-11-13) already DECIDED "the lineage popup is the navigator" (a tree from the datasets to the plots; a click shows the node's first rows, read-only). Her new idea adds: start from a picked data file; separate trees; the link both ways; opening the table itself.
4. D-0027: the node popup is its own window. Whether the picker is that window: open.
5. `home_audit_steps.md:134` (2026-11-12, "other places are listed unticked") is older than D-0316 (all ticked): a stale design line.
6. `assets/dep_graph.html:101-103` loads three scripts from a CDN (against the no-CDN rule; a developer aid, not the app).
7. Exploration filters are cleared when the viewed table changes (D-0311): a pick in the picker changes the viewed table.

## 6. Not checked
Nothing was run. The counts are from reading the YAML. The orchestrator's behaviour for an unknown table name. How long the engine's plan takes for every table of the demo (the walk needs it; the tree itself does not).
