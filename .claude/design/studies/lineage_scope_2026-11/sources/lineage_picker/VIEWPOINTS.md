# The four viewpoints on the lineage picker (2026-11-22, one round; shortened by the coordinator, nothing changed in meaning)

Alternatives: P0 nothing new; P1 flat list with search; P2 drawn graph; P3 outline; P4 P2 or P3 with P1. Sub-question: a click opens the table (a) in HOME's data preview or (b) inside the popup.

## Scientist and data scientist (read the code, ran nothing)
- First: if the table viewed can be outside the open plot, `_resolve_active_lf` (`app/handlers/home_theater.py:485-518`) and the badge must name the TABLE, or rows of table X are read under the title of plot Y. "Send to Audit" is offered only on T3 (`filter_and_audit_handlers.py:649`): a user who sees the bad row in a join and cannot act from there will filter at the wrong place (D-0450). A silent clear of the exploration filters looks like "the rows came back". A tree per data file lists a join under each parent: a reader of one tree may take it as the whole.
- P0: her case fails; 6 tables cannot be opened. P1: reaches everything, shows no parents. P2: shows both parents and the path up; poor layout for a large tree. P3: no layout problem, searchable; a join repeats under each parent. P4: both directions.
- Recommends P4, on P3 or P2, with a join as ONE node with all its parents. Sub-question: (a). The user must be told: which table and stage; which results read it; that the filters were cleared; where "Send to Audit" applies, with its reach; the row count. The view state never enters the export (D-0327).

## Architect (ran the shared graph on the demo recipe)
- First: `view_key` (`app/modules/t3_audit_engine.py:69-73`) holds no table id for T1, T2, T3: a pick of another table under the same plot would keep the filters. `_can_write_audit_step` (`filter_and_audit_handlers.py:155`) and `home_theater.py:1730, 1800` test only `data_view == "T3"`. `_screen_view_text` (`home_theater.py:455-460`) writes "data view T3" without a table.
- Checks: 85 nodes; 4 groups of 67, 12, 3 and 3 nodes; `lineage_forward` of `metadata_schema` = 41 nodes; a DAG, not a tree; 15 T2 nodes have no child (no last-stage node for a table no plot reads).
- P2: the drawing has a global single instance and a click bound to BLUEPRINT's input (`app/src/ui.py:134-288`); its colours are duplicated in JS. P3: tested as HTML.
- Recommends P4 with P3 as the base; the drawing only once the shared drawing function is general. Sub-question: (a). A Shiny modal shares the session; a real second browser window does not and could not set the state.
- Boundary: data = a pure function in `libs/utils/recipe_graph.py` (groups, paths up and down, table and stage per node, unread tables included); drawing = a general `initCyGraph(elements, container, inputId)` plus an element builder in `app/modules`; HOME = ONE value "viewed = (table, stage)", set by opening a plot and by the picker. Flag: `interactivity_enabled` (to confirm).

## Developer (facts for a builder; no recommendation by cost)
- `read_source(recipe, dataset)` takes a source name only and raises for another name (`app/modules/orchestrator.py:298`). `materialize_tier1` / `materialize_tier2` take any collection name, write under the anchors folder and need the keys (`:431`, `:589`). T3 needs a plot id.
- The drawing allows one map per page (`window._cyInstance`), layout left to right, no compound nodes, no collapse.
- Testable: P1 and P3 as DOM text; P2 only through the elements data and JavaScript (canvas).
- Slices: (1) pure function "groups, path up, path down" with tests; (2) "a table by its name" for the preview; (3) the picker view; (4) the popup or panel wiring with a browser test. 1 and 2 are the same for every alternative except P0 and can run side by side.
- Sub-question: (b) adds outputs inside the popup; (a) keeps the popup light.

## A user who is not a developer (walked the three tasks on the demo recipe; ran nothing)
- Task 1 (`mlst_bar`, where does a sample come from): P0 shows the tables with no link between them; P1 names only; P2 and P3 answer if the path of the open figure is marked.
- Task 2 (`metadata_schema`, which figures depend on it): drawn = about 30 boxes with crossing arrows; outline = two lists of 13, readable.
- Task 3 (a table no figure uses): P0 cannot; P1 only if marked; the outline shows lone roots.
- Recommends P4 with the outline, in a SIDE PANEL, with a group "Used by no figure" and a switch "Show the path of the open figure". Sub-question: (a).
- Words: not "lineage", "tier", "T1", "source"; rather "Original data files", "Joined tables", "Figure", "Where this table comes from", "What uses this table".
- Banner when the table is not the figure's: "You are viewing table X. It is NOT the table of the plot above (mlst_bar). The plot does not change. Filters were cleared. [Back to the plot's table]".
- Pitfalls to tell: P0 hides tables; P1 names say nothing of what a table depends on; P2 a drawing can look complete when cut off or zoomed; P3 a joined table appears under several data files and is one table.
