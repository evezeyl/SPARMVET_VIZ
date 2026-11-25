# Lineage and scope in HOME: the architect's view

Viewpoint: software architect. Research only; no code changed. Statements marked "not verified" were not checked in code or on the web.
Scratch script (numbers): `tmpAI/panel/lineage_scope/scratch/stats.py` (run with `PYTHONPATH=. ./.venv/bin/python`).

## 1. Facts

### The demo graph (measured, `1_test_data_ST22_dummy.yaml`, `build_graph`)
- 87 nodes: 14 original files (DS), 28 tier 1, 28 tier 2, 17 tier 3 (one per plot). 94 edges. 14 roots (all DS).
- Depth: 5 levels (0 to 4). Level sizes 14, 14, 28, 18, 13. The widest level is 28 nodes (all tier 2 of 28 tables, mostly empty).
- 28 tables: 14 original + 14 joined. 58 places = 28 T1 + 13 T2 (only the T2 a plot reads) + 17 T3. 15 of the 28 tier 2 are not places.
- Biggest fan-out: `T1:metadata_schema` reaches 33 nodes below it (12 direct children). `T1:ResFinder` reaches 14 (4 tables, 5 plots).
- 6 tables no plot reads: Quality_metrics, Detailed_summary, FastP_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, AR1_MLST_Serotype_Virulence. Note: ResFinder_with_metadata is not a dead end: it feeds ST22_Anchor (a join) which plots read. The script's "no plot reads" test is "no T3 below", so it is a true leaf list except those 6 are real dead ends (their only child is their own T2).
- Every T1 has a child (its own T2), so "leaf" in the graph is only T3 and the unread T2.

### What the present dialog shows and cannot show
- It lists the places upstream of the open plot as an indented checkbox list (`audit_places.place_lines`, `path_rows`; depth = `--spv-depth`), with a reach sentence ("6 other tables and 9 plots are built from it", `reach_sentence`, audit_places.py:204) and the types of the columns. `audit_places_path.js` marks places derived (below a ticked one) or blocked (above) without redrawing the list (R4 of the contract, section 14).
- It starts from the open plot and walks back (`lineage_back`). It cannot show: branches that are not on that plot's path (siblings that share a parent); the original files with their completed ids as a start; a table no plot reads (not offered today, rule `D-0451` not yet built as ticked or not); what a place reaches except as a count; the direction of the arrows; a whole-recipe view.
- Choice rule in code: `RecipeGraph.chosen_places_problem` (recipe_graph.py:459): every id is a place, none below another chosen one. `DS:` is never a place (kind DS). The T1 of several original tables may be chosen together.

### BLUEPRINT's drawing and reuse
- BLUEPRINT's TubeMap is Cytoscape.js 3.29.2 + dagre 0.8.5 + cytoscape-dagre 2.5.0, MIT, already vendored (`app/src/www/vendor/VENDOR_MANIFEST.md`) and ALREADY loaded in the whole page (`app/src/ui.py:128-131`, also for HOME). Inline JS builds `cytoscape({... layout dagre ...})` at `ui.py:194`. Data are Cytoscape JSON produced on the server (`wrangle_studio.py:1273`, `active_tubemap_mermaid` holds Cytoscape JSON). The lineage chain functions are in `libs/blueprint_arch/.../data_analysis_recipe_navigator.py` (`build_lineage_chain`, `build_plot_lineage`; not read in detail: not verified).
- Reusable: the vendored libraries (no new dependency), the JSON-from-server pattern. Not reusable as is: it is made for editing in BLUEPRINT (its nodes are recipe files, `rel_path` based), and the cross-panel rule (CLAUDE.md section 8, point 4) says a module's UI outputs sit inside its own panel: HOME needs its own container and its own small script, not a call into BLUEPRINT's.

### The constraints in five lines
1. No CDN; every asset vendored with a manifest entry; no build step (no npm bundle).
2. Pure logic in `libs/utils` (no Shiny, no engine); Shiny only in `app/handlers`; the layout/number logic is testable headless.
3. Never re-mount a widget on each click (contract section 14 R4): selection state lives in the browser or in a small `reactive.Value`; the server is told only the chosen place(s).
4. Palette, type scale (0.65 to 0.85rem) and panel widths from `rules_css_style_spec.md`; no colour-only signal; the right panel is 170 to 340 px wide, so a drawing in a side panel is small.
5. Server-side Shiny for Python on a container, Posit Connect, Galaxy interactive tool: no WASM, no system binary I cannot install on all three (graphviz binary is a cost).

## 2. The data contract every proposal shares

One pure function, no Shiny, no engine: `lineage_view(graph, plans, selection=None) -> LineageView`, in `libs/utils/src/utils/recipe_lineage.py` (new; size M). It reads `RecipeGraph` and the recipe raw; it returns plain data (dataclasses; serialisable to JSON). The display is then free.

```
LineageView
  mode: "whole" | "selection"
  focus: node id | None             # the selection (a T1, T2, T3 or a plot)
  nodes: [LineageNode]
  edges: [(parent_id, child_id)]    # direction parent -> child (reads from)
LineageNode
  id, kind: original | tier1 | tier2 | tier3 | result_table | plot
  table: table id (or plot id)
  label: ui_label | table id
  description: str                  # from the recipe (see below)
  tier_empty: bool                  # no steps in this tier (D-0346: an empty tier is not a separate line)
  place: bool                       # a step can be written here
  not_place_reason: str             # "the file as read, not a table after a tier" / "no plot reads this tier 2" / "same table as T1 (empty tier)"
  reach_tables: int, reach_plots: int, reach_plot_ids: [str]
  columns: [name]|None, columns_reason: str     # from column_info
  state: ""|chosen|derived|blocked  # only with a selection
  state_reason: str                 # plain sentence (reuse chosen_places_problem wording)
  collapsed_default: bool
```

Where each field comes from (verified unless said):
- ids, kind, edges, steps, `read_by_plot`: `Node` and `edges()` (recipe_graph.py:96, :181). `place`: `places()` (:448).
- reach: `below(place)` + `plots_below` (audit_places.py:154) + `reach_sentence` (:204). Counts exist; the plot IDs are available.
- columns: `column_info` / `columns_of` (:281, :296); types need the `PlanBook` (the engine), as `place_lines` already does.
- label and description: the recipe carries `ui_label` and `description` on data_schemas (demo lines 18-19) and on joins and plots (plot `ui_label`; plot `description` not verified); `info.ui_label`/`info.description` for the recipe. `Node` does NOT carry them today.
- result table (a table no plot reads): derivable (no T3 below T1/T2): not stored as a flag.

What is missing in `recipe_graph` today (verified by reading class `Node` and the methods list):
1. `label` and `description` on a node (needs the raw body: `self._bodies[table]` exists, so a method `describe(node_id)` is S).
2. `is_result_table(table)` (no plot below). S.
3. `tier_empty(node_id)` (len of steps = 0). S (`Node.steps` exists).
4. A "not a place, why" method (the sentences are inside `chosen_places_problem`; extract to one function). S.
5. A selection view: `neighbourhood(node_id)` = `lineage_back` + `lineage_forward` (both exist) plus their edges. S.
6. A per-path "collapse" notion: a chain of nodes with a single parent and single child and an empty tier can be folded into one line (D-0346 "only distinct tables are lines"). M. Not verified how `place_lines` folds empty tiers today.
7. DS completed ids: the demo recipes carry `completion:` on a schema (demo line 22-24): "the original data with completed ids" would need that read into `description`/a badge. Not verified beyond the demo lines.

Rule of selection (shared): the user chooses at most one place on a path, except original parents (D-0553). `choice_problem` stays the single arbiter; the display only previews it.

## 3. Proposals

A "result table" = a table no plot reads. In all proposals it appears as a leaf node of kind result_table with its own T1 (and T2 when it has steps, not possible when no plot reads: S07/J14 refuse tier 2 on it, so only T1). To write a step there the user picks its T1. This needs the dialog to accept an `extra_offered` place not on the open plot's path (the parameter `extra_offered` already exists in `choice_problem`, audit_places.py:218); the confirm step must then record `started_from` as none (not verified how `_confirm_places` handles a place outside the open plot's path).

Demo sketch conventions: `[x]` chosen, `~` derived, `-` blocked, `(n)` plots below.

### P1. Indented collapsible outline (native `<details>`), per path
Server-rendered HTML tree. Roots = originals. A node with several parents appears under each parent but is shown once fully and then as a reference line ("see above") to keep it a tree.

Whole recipe (collapsed to the first level):
```
v Original files with completed ids (14)
  > ResFinder          (original)  5 plots below
  > metadata_schema    (original)  17 plots below
  ...
v Result tables, no plot reads them (6)
  > Quality_metrics    short description
```
Selection around ResFinder (opened path):
```
ResFinder (original, T1)  [x]            reaches 4 tables, 5 plots
 ~ ResFinder_with_metadata (T1)  result table, no plot   follows from the place above
 ~ ST22_Anchor (T1) -> QA_AMR_per_sample -> plots: amr_heatmap, virulence_bar ...
```
- Select: a radio/checkbox per place row; reuses `audit_places_path.js` unchanged in spirit (row, depth, derived/blocked notes). The server gets the ticked ids; `choice_problem` confirms.
- Derived/refused: indentation + text note + "follows from ..." (not colour only). Reach: one sentence per row, plots on expand.
- Scale: 87 nodes fine; 3x (260) fine with default-collapsed levels; a node with 33 below is the long list (collapse).
- Collapsible/extensible: native; "expand all" button. Result table: own group.
- A11y: best (native disclosure, keyboard, screen reader). Direction: implied by indent; no arrows.
- Code: new `recipe_lineage.py` (M) + a render function in `app/modules` (S) + small CSS (S). Dependencies: none. Tests: structure and text headless (pure); JS unchanged. Risk: low; weak on "see the shape" (branching reads poorly when a table has several parents: duplicate lines).
- Fit: all three deployments (no JS library).

### P2. Layered left-to-right inline SVG, laid out on the server
Own Python layering (rank = depth, order = barycentre pass), emit `<svg>` with `<a>`/`<g tabindex>` nodes and arrow markers. No dependency (own code ~150 lines), or `networkx` (BSD, pure Python, not installed; not verified by web) for a topological layering only.

Whole recipe: a wide drawing 5 columns x up to 28 rows (about 5 x 28 nodes), needs scroll/zoom. Selection: only the back/forward subgraph (ResFinder: 15 nodes, 5 columns) fits in a centre panel.
- Select: click on a node; a click needs JS to tell Shiny (`Shiny.setInputValue`), or the node is a `<label>` of a hidden checkbox (no JS, keyboard works). Derived/blocked: a CSS class + a text badge in the node + a legend.
- Scale: layout in Python is simple but crossing minimisation is poor above ~100 nodes; collapse is by server-side "fold this subtree" which re-renders the SVG (a redraw on click: allowed if only the SVG widget is replaced, not an input).
- Result table: leaf at the right edge, own style. A11y: needs `role`, `aria-label`, tab order (M); colour-only risk unless badges.
- Code: L (layout + SVG + tests). Dependencies none. Tests: SVG string and positions headless; looks need the browser. Risk: medium (own layout bugs, fine tuning). Deployment: all.

### P3. Cytoscape.js + dagre (already vendored), small and its own to HOME
Server builds the JSON from `LineageView` (nodes, edges, classes `chosen/derived/blocked/place/result`). A HOME script (like `audit_places_path.js`, first-party, e.g. `lineage_view.js`) creates one cytoscape instance per container and does not re-create it on a click: it changes classes and `Shiny.setInputValue('lineage_pick', id)`.
- Whole recipe: dagre rankDir LR, 87 nodes, tiers T1 and T2 of one table grouped as a compound node ("table") so a table is one box with its tiers inside (compound nodes are in core Cytoscape; the clean option for D-0346). Selection: the same, filtered by `lineage_back`+`lineage_forward`, with `cy.nodes().hide()`.
- Select: tap a place node. Derived (dashed outline + label "follows") and blocked (greyed, label "a place below is chosen") are classes set from the same rows as `audit_places_path.js`. Reach: tooltip is not enough (touch, a11y): a side text panel under the drawing that shows the sentence of the hovered or selected node.
- Scale: handles 260 nodes; collapse by an expand-collapse extension (not vendored) or by own hide of subtrees (S/M). Zoom and pan built in.
- A11y: weak by default (canvas): needs a parallel text outline (P1) for keyboard and screen readers. This is the key cost.
- Code: M/L (JS ~200 lines + builder S + CSS). Dependencies: none new (cytoscape 3.29.2, dagre 0.8.5, cytoscape-dagre 2.5.0 already vendored and loaded in the page, ui.py:128-131). Tests: JSON headless; interaction needs Playwright. Risk: the second graph in one page (id clash with the TubeMap's container; use another container id and a separate `cy` variable); an extra weight for HOME users is nil (already loaded). Deployment: all (static files).
- Alternatives in the same class (look-up from memory, licence not verified by web): ELK (`elkjs`, EPL-2.0, ~1 MB, better layering, async) via `cytoscape-elk`; `d3-dag` (MIT); `vis-network` (Apache-2.0/MIT, physics-based, large, worse for a strict layered layout); `Mermaid` (MIT, 2+ MB, text to SVG: no real selection; not recommended as it is the same "shortcut" Eve rejected for StarUML, different case though).

### P4. Sankey or flow style (reach as width)
`d3-sankey` (BSD-3, not vendored; needs d3 core ~ not verified size) or hand-made SVG. Node height = number of plots below; links = edges.
- Shows reach as thickness: one look says "metadata_schema reaches 17 plots, ResFinder 5". It does NOT show per-step, one place at a time, and a node with a single parent and many children gets ribbons that cross; a Sankey wants links that carry a quantity, here the quantity is a count of plots, which is not conserved along the path (a plot below two tables is counted twice): misleading (a table's reach is not a sum of its children's). Select: click as P3. A11y: weak.
- Verdict: reach as width is attractive for "what it reaches" but the maths is wrong for a DAG with joins. Use the idea only as a bar next to a node in P1 or P3, not as the layout. Code M/L; new dependency. Risk: high (misread).

### P5. Column browser (Miller columns): parents | selection | children
Three columns (or a list + a detail pane): left = the parents of the selected node (originals if root), middle = the node with its description, tiers, reach and columns, right = its children (with a count of plots each). Click a child to move right. For a whole-recipe view the first column lists the 14 originals plus the 6 result tables.
- Select: "Write the step here" button on the middle node (disabled with the reason if it is not a place). Derived/blocked: the right column shows children as "follow from this place"; moving to a child that is below an already chosen place shows the block reason. One place per path is natural: the user is at one node at a time. The exception "all original parents together" needs a "also tick another original" line in the first column.
- Scale: best (always 3 short lists); no layout, no library. Needs 3 narrow columns: fits the centre only (not the right panel). Direction: left to right is the arrows. Branch overview: weak (see one path at a time); a "whole picture" is absent.
- A11y: good (lists, keyboard). Code: M (builder + UI + a `reactive.Value` for the focus: the focus change re-renders the columns, not an input widget, so R4 holds if the columns are an `output_ui` separate from the confirm button). Dependencies none. Risk: low; the weakness is the lack of the overall picture the owner asks for.

### P6. Hybrid: compact outline for choosing + small diagram for orientation
P1 (outline, the real control, accessible) + P3 (a small read-only Cytoscape map of the same selection, which highlights the node focused or hovered in the outline, and the other way round: a click on the map scrolls/highlights the outline row). The map never carries the choice: so the accessible control is always the outline; the map is orientation only. This also cuts the P3 risk: the A11y gap (the map is decorative `aria-hidden`; the outline is the truth).
- Whole recipe: outline collapsed on top, map below at zoom-to-fit with only tables as nodes (28 table nodes, tiers hidden: one box per table, D-0346) and plots folded into a count badge. Selection: the neighbourhood only.
- Code: L (P1 + P3). Deps none new. Tests: outline headless; map class sync in Playwright. Risk: medium (keeping two views in step; do it with one JSON and one `data-` attribute as `audit_places_path.js` does). Deployment: all.

## 4. Where the lineage lives in HOME

Options, with my view:
- Inside the audit dialog: the choice is made right there, no new state; but a modal is small and blocks the data: bad for a drawing. Keep the dialog for P1 (outline) only; fits the present flow (confirm button, `choice_problem`).
- A collapsible band above the plot (like the plot and data accordions, `ui_implementation_contract` section 2: "separate collapsible accordion panels"): a third accordion "Lineage", visible in Audit mode only (gate `t3_sandbox_enabled`), default collapsed. This is the best fit for a drawing (full centre width) and for "collapsible". The click on a node there opens the audit dialog with that place ticked (or pre-selects it when the dialog is open).
- Right sidebar (the audit panel): too narrow for a drawing (170 to 340 px); fine for the outline P1 as "where this step goes" summary.

One component with a filter, not two: `lineage_view(graph, plans, selection)` with `selection=None` means whole recipe. The "selection" is the open plot (default), or the node the user clicked, or the node of the dialog. Exploration mode shows the lineage read-only (information, no step); Audit mode adds the "write a step here" action. (Whether the lineage should be shown in Exploration is a question for Eve: not decided.)

## 5. Comparison (architect's scoring: 1 low to 5 high; build size S/M/L; risk low/med/high)

| | Clarity of shape | Simple for user | Ease of choosing | Fit code and recipe | Build | Risk | Scales to 260 | Testable headless | A11y |
|---|---|---|---|---|---|---|---|---|---|
| P1 outline | 2 | 5 | 4 | 5 | M | low | 4 | 5 | 5 |
| P2 server SVG | 4 | 3 | 3 | 3 | L | med | 2 | 3 | 3 |
| P3 Cytoscape | 5 | 3 | 4 | 4 | M/L | med | 4 | 3 | 2 |
| P4 Sankey | 3 | 2 | 3 | 2 | M/L | high | 3 | 3 | 2 |
| P5 columns | 2 | 4 | 4 | 5 | M | low | 5 | 5 | 4 |
| P6 hybrid | 5 | 4 | 5 | 4 | L | med | 4 | 4 | 5 |

### The architect's ranking (my view; the data scientist and the user may weigh differently)
1. P6 hybrid, built in two steps: first P1 (usable alone, closes the need to choose a scope and to reach a result table), then P3's map as an addition. Reason: the accessible, testable control is the outline; the map answers "the shape" the owner asks for, with libraries already vendored and loaded.
2. P1 alone, if the map is judged not needed: cheapest, safest, fully inside the rules.
3. P3 alone: best shape, but the keyboard/screen-reader gap needs a text twin anyway (which is P6).
4. P5 columns: very simple, but no whole picture; good as the "from a selection" version.
5. P2 and P4 last: own layout cost (P2) or a misleading width on a DAG (P4).

Shared first step for any: the data contract (section 2, items 1 to 6), size M, headless tests, no UI. The dialog needs the "extra place not on the open plot's path" case for result tables (`extra_offered`).

## 6. Questions left

For the data scientist viewpoint:
- Is "reach" (tables and plots below) enough to choose a scope, or must the lineage also show per place what the step changes (rows, columns, a type that differs) before confirming? Which words are correct for a place where the column is recomputed under its own name (D-0353)?
- Is a table that appears under several parents (a join) shown once or under each parent? Which reading is right for a joined table (a step at its T1 vs at an ingredient: different rows)?
- Is a step at a result table (no plot) scientifically meaningful and exported (it changes a stored table nobody plots)?

For the user viewpoint:
- Do you need the shape (arrows, branches) or is a list that unfolds enough? Would you read the drawing at all with 28 table boxes?
- What must a node say in one line (name, description, "result table", number of plots)? Is the word "tier" understood, or "step in the table"?
- Should the lineage also be visible in Exploration (read-only), or only in Audit mode?
- Whole recipe first or the selection first on opening?

Not verified: licences and sizes of ELK, d3-dag, vis-network, d3-sankey, Mermaid, networkx (from memory, not searched); whether `_confirm_places` accepts a place outside the open plot's path; the `description` key on joins and plots; how `place_lines` folds empty tiers; BLUEPRINT's navigator functions in detail.
