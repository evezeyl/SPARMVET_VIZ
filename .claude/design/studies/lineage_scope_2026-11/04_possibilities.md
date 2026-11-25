# Lineage map for the audit scope: possibilities

Research and mock-ups only. Mock-ups: `tmp/2026-11-24/lineage_mockups/index.html` (eight variants, same small data, double-click to open). The data are a simplified subset (19 nodes); the real demo graph (87 nodes, 94 edges) is exported to `tmpAI/panel/lineage_scope/scratch/real_graph.json` (script `scratch/export_graph.py`). Descriptions and step texts in the mock-ups are invented.

Web look-ups: the survey below is written from my own knowledge (cutoff mid 2026); NO site was fetched in this run. Every licence, size and "last release" entry is therefore "not verified online" and must be checked before a choice. Items I know from the repository are marked "repo".

## 1. Survey of graph packages

| Package | Licence (not verified online) | Maintained (not verified) | Size / vendoring | For our need (layered directed graph with joins, fold, click/hover, keyboard, offline) |
|---|---|---|---|---|
| Cytoscape.js 3.29.2 (repo, vendored) | MIT (repo manifest) | active project | one file, ~0.4 MB min; already in `app/src/www/vendor` | Click, hover, compound nodes (fold by hand), zoom; layout through extensions; keyboard access weak (canvas) |
| dagre 0.8.5 + cytoscape-dagre 2.5.0 (repo, vendored) | MIT | dagre is old, little change | two files, already vendored | Layered left-to-right layout; coarse edge routing (curves); fine for tens to a few hundred nodes |
| cytoscape-elk / cytoscape-klay / cytoscape-cola | MIT (plugins); ELK EPL-2.0 | plugins less active | each a file plus the engine | ELK gives better layered layouts with orthogonal arrows; klay older; cola is force-directed (wrong look for a lineage) |
| elkjs 0.9.x | EPL-2.0 | active (Kieler) | bundled ~1.5 MB one file, no build step | Best layered layout, orthogonal routing, hierarchy (folding groups possible), ports; async; draw yourself (SVG) or via Cytoscape plugin; used in mock-up C |
| D3 + d3-hierarchy | ISC / BSD | active | modular, one or two files | d3-hierarchy is for TREES only (not joins). You draw everything yourself |
| d3-dag (Sugiyama) | MIT | small, slower releases | ES modules, bundling usually needed | Layered layout of a DAG with joins; manual SVG; less handy without a build step |
| dagre-d3 / dagre-es | MIT | dagre-d3 old, unmaintained | few files | Old but simple layered SVG drawing; not advised for a new build |
| Mermaid | MIT | very active | ~2-3 MB | Text to diagram, clicks possible ("click" directive), little control over fold, selection state, layout; poor for live selection |
| vis-network | Apache-2.0 / MIT | active again after a pause | one file ~0.5 MB | Hierarchical layout, events; physics look; less control over exact layered layout |
| Sigma.js | MIT | active | needs graphology; WebGL | Made for very big graphs; no good layered layout; overkill |
| AntV G6 / X6 | MIT | active | 1 MB+, many modules | Rich (dagre/ELK-like layouts, fold nodes); heavy for our need |
| React Flow / Svelte Flow | MIT | active | need React/Svelte build | Not usable without a front-end build in a Shiny app (they are components of a framework); a build step would be a new tool for the repo |
| JointJS (core) | MPL-2.0 (the plus tier is commercial) | active | ~0.5 MB+ | Diagram editing features we do not need |
| GoJS | commercial licence | active | one file | Excellent, but paid: not suitable |
| Graphviz in the browser: viz.js / @hpcc-js/wasm | EPL (Graphviz) / Apache-2.0 | active | WASM ~1-2 MB | Same drawing as server-side dot, in the browser; click handling by SVG; no folding |
| Python: networkx | BSD | active | pure Python | Graph logic, but the repo already has `RecipeGraph`; layouts are rough (not layered) |
| Python: graphviz / pygraphviz | MIT / BSD | active | need the system program `dot` (installed here: `/usr/bin/dot`) | Server-side SVG with links (mock-up H); needs the binary in every deployment (container yes; Posit Connect and Galaxy: not verified) |
| Python: igraph | GPL-2.0 | active | compiled wheel | Layered (Sugiyama) layout, but GPL licence is a risk for the app |
| Python: grandalf | GPL-2.0 or EPL (not verified) | rarely updated | pure Python | Pure Python Sugiyama layout; positions only; low maintenance |
| Python: pyvis | BSD | little activity | wraps vis-network | Writes a page; hard to wire into Shiny events |
| Python: ipycytoscape + shinywidgets | MIT / MIT | ipywidgets route; works with Shiny for Python through `shinywidgets` | adds ipywidgets and its JS | Gives Cytoscape inside Shiny with events as reactive values; new dependencies; not verified in this repo |
| Python: plotly (network) | MIT | active | ~3 MB JS | Possible but a scatter-style graph; layout by hand; poor for arrows and folds |

Shortlist (my judgement, not a decision):
1. **Cytoscape.js + dagre (vendored)**: nothing new to ship, the same pattern as BLUEPRINT's TubeMap, MIT, fold by compound or rebuild (mock-up B). Best cost/benefit. Weak: curved arrows, canvas (keyboard access and screen readers need a parallel list).
2. **Plain HTML (outline, matrix, columns, path view; no library)**: cheapest, keyboard friendly, offline, works in every deployment (A, D, E, F, G). Weak: no real picture of the graph.
3. **elkjs (+ own SVG)**: the best looking layered picture with right-angled arrows (C); EPL-2.0 file to vendor; worth it only if B's arrows are judged not readable enough at 3x size.
4. **Graphviz SVG on the server** (H): good picture, no browser library, but a system binary dependency; keep as a fallback for the export or documentation rather than for interaction.

## 2. The mechanics (independent of the look)

**From a click to the place of the step.** A click only changes the selected ids on the client; the confirm sends the ids (as the dialog does today) to the server, where `app/modules/audit_places.choice_problem(graph, offered, chosen, extra_offered)` (audit_places.py:218) checks them with `RecipeGraph.chosen_places_problem` (recipe_graph.py:459): every id a place, none below another chosen one. The handler at `filter_and_audit_handlers.py:1313` then writes the step at the chosen places. The map is therefore only a better way of producing `picks`; the rule stays on the server. The live marking (below = follows, above = unavailable) is client-side as `audit_places_path.js` does it today; the same code in the mock-ups (`core.js`) is about 20 lines.

**Where the map gets its data.** One pure function (no Shiny) giving: nodes (id, kind, table, tier label, plain "what it is", short description of a plot or result table), edges, for each node the names built from it (`RecipeGraph.lineage_forward`), and per (place, result) the list of step texts between them (the mock-up computes it as the shortest path; a real function should list every path, since a join has two). Sent once as JSON (a data attribute or `Shiny.setInputValue`/custom message). Not verified: where a plain-words description of a plot comes from today (probably `ui_label` and the plot's mapping).

**Forth-back-forth.** From the selection: back = `RecipeGraph.lineage_back` to every original; then forward = `lineage_forward` of those originals and of the selection (mock-ups: `LG.visible`). A "whole recipe / around my selection" switch only changes which ids are shown; the data stay the same.

**A result table with no plot.** It is a node with no children (here `T1:Quast_with_metadata`; in the demo 6 such tables). Today's dialog starts from the open plot and cannot reach it; the map offers it as a leaf, selectable like any place. The rule of `chosen_places_problem` already accepts it (not verified for a place with no plot below; a test is needed).

**Where it can sit.**
- Central collapsible panel: the most room (full width, 400+ px high); it fits B, C, E. It would sit in HOME's own panel (rule CLAUDE.md section 8, point 4).
- Pop-up (modal): can be almost full screen, hides the plot (she cannot compare the plot while choosing); fine for a one-time choice. The existing dialog is a modal.
- Side panel (right panel, 170-340 px): too narrow for B, C; fits A, D, F and a small G map.

**What Shiny for Python allows for a custom element.**
- A script with data attributes and `Shiny.setInputValue` (what the repo already does: `audit_places_path.js`, `export_ready.js`): the simplest, no new package, full control; the render stays server-side HTML plus a script. Trade-off: you write and test the JS yourself; a canvas widget needs its own keyboard layer.
- A custom output binding (`Shiny.OutputBinding`): the proper way when the map is an output that the server redraws; a little more code; allows `render` functions that send JSON; works the same in the container, Posit Connect and Galaxy.
- An htmlwidget via `shinywidgets` (ipycytoscape, plotly): quickest to prototype, but adds ipywidgets and its JavaScript to a vendored, offline app (CDN ban, ADR-071): needs checking that all assets can be vendored (not verified).

## 3. Variants A to H: what the user can do for the audit

Marks: yes / partly / no. 87 nodes is the demo; "3x" is about 260 nodes. Size S/M/L; risk is for the build. Judgement is mine.

| | View whole | Fold / unfold | Select scope | Several originals | See what follows | Info on element | Reach a result table | Steps already placed | 87 nodes | 3x nodes | Clean | Size | Risk |
|---|---|---|---|---|---|---|---|---|---|---|---|---|---|
| A outline | list, not shape | yes (native) | tick | yes | yes (marks) | yes | yes | easy to add on a line | fine | long, folds help | very | S | low; repeated lines for joins |
| B Cytoscape+dagre | yes, picture | yes (table box to tiers) | click | yes | yes (colour + text) | yes | yes | badge on a box | fine | crowded; fold and "around" needed | good | M | low-medium (known library) |
| C ELK | yes, right-angled | not built (possible) | click | yes | yes | yes | yes | badge | fine | readable | good | M | medium (new file, async) |
| D column browser | no (neighbours) | n/a (walk) | button | yes | yes | yes | yes | easy | fine | fine | very | S | low; hard to compare branches |
| E matrix | by rows, columns | partly (group rows) | row click | yes | yes (column marks) | yes | yes (column) | cell mark | fine (87x17) | scroll, frozen header | clean but abstract | S | low; unusual for her |
| F path view | one result at a time | n/a | click | partly (originals in view) | yes | yes | yes (starts from it) | on boxes | fine | fine | good | S-M | low; no global view |
| G hybrid | list plus tiny map | list grouped | click | yes | yes | yes | yes | in the list | fine | map crowded | good | S-M | low-medium |
| H Graphviz SVG | yes, picture | no | click on SVG | yes | yes (client recolour) | yes | yes | badge | fine | big picture | clean, fixed | M | medium (binary dependency, refresh) |

No ranking required. If I rank (mine): B for the picture of the whole recipe, E or A as the keyboard/list companion, F for a user who starts from a result. A combination (a picture to see, a list to choose) is probably the safest for a user who "cannot judge from text": look at B first.

## 4. Not done or not verified

- No web look-up was done; licences, sizes and release dates in section 1 are from memory.
- The mock-ups were opened headless in Chromium (no page errors; each had one click tried), not tried by hand on a phone or with a keyboard. C needs the network (elkjs from jsdelivr); the others work offline (B reads the libraries from `app/src/www/vendor`).
- Fold in B is by rebuilding the graph (tables to tiers); with 87 real nodes the layout time was not measured. The real graph was exported but the mock-ups use the 19-node subset.
- The choice rule in the mock-ups is a simplification (several originals only together, any other place alone); the real rule is `RecipeGraph.chosen_places_problem` and was not re-tested against the mock-up.
- shinywidgets/ipycytoscape and the availability of `dot` on Posit Connect and Galaxy: not verified.
