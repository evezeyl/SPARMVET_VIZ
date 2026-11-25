# The complete lineage in HOME, to choose the scope of an audit step: options for the owner (2026-11-24)

Three viewpoints worked one after the other, each reading the earlier files: `01_architect.md`, `02_data_scientist.md`, `03_user.md` (same folder). Nothing is built. The panel recommends; the owner decides.

## Flag first
1. A measured finding changes the wording of everything: the figures a place "reaches" are the figures that are RECOMPUTED, not the figures the entity leaves. On the demo, removing one entity at the metadata recomputes 9 figures and the entity stays in 7 of them with an empty country and year (19 of the 21 joins keep every line of the first table). At tier 1 of ResFinder, 3 of the 5 figures below lose the entity and 2 keep it.
2. One point reopens an earlier decision: the user viewpoint asks for a count at the chosen place BEFORE confirming (rows and entities before and after; a warning when the step removes nothing or everything). The earlier line (D-0545) says a measure at each trial can cost too much. Measured on the demo: the count at the chosen place alone takes 0.06 to 0.17 second; a full audited build 0.3 to 1.0 second. Real-size data is not measured.
3. Today an id typed with a leading space removes nothing and gives no message; a threshold that removes every row gives no message either.
4. The graph's own knowledge of the columns at a node is unknown at 50 of 87 nodes and wrong on the marker column at 12; the engine's plan was right at all 41 places checked. The lineage must take its columns from the engine's plan.

## The demo graph
87 nodes (14 original tables, 28 tier 1, 28 tier 2, 17 tier 3), 94 arrows, 5 levels, the widest level 28 nodes, 58 places, 6 tables no plot reads.

## The options
| Option | What the user sees | For | Against | Viewpoints |
|---|---|---|---|---|
| P1 Collapsible outline | An indented list that unfolds, from the original tables to the figures; one sentence per line; click a line to choose | Cheapest; plain text; can carry names, notes and warnings per line; keyboard-friendly; fully testable | Hides the shape: a table with several parents appears once; long on a large recipe (needs a search box) | Data scientist 1st; user 2nd; architect 2nd |
| P6 Outline + small map | The outline is the control; a small read-only map beside it shows the shape, built later | The list to trust plus the picture; the map library is already in the app (BLUEPRINT uses it): no new package | Largest build; the list and the map must never disagree (one data object for both) | Architect 1st; user 1st; data scientist 2nd, under conditions |
| P5 Column browser | Three columns: parents, the selection, children | Very clear for one table; scales | No whole picture; the user loses her place after a few clicks | All three: good as the view from a selection |
| P3 Graph map alone | Boxes and arrows, clickable, zoom | Best shape | Names, notes and warnings need a text twin; a box clicked by mistake | All three: not alone |
| P2 Diagram drawn on the server | A fixed picture with arrows | No script | Own layout code; tall picture; little gain | Low for all three |
| P4 Flow with widths | Bands whose width is the reach | None that holds | A width is read as an amount of data; wrong when tables are joined | Rejected by all three |

All three agree: one screen with a switch between "whole recipe" and "around my selection", not two screens; placed as its own collapsible panel in the centre of HOME in Audit mode, not inside the dialog (too small, it hides the data); a click on a node opens the dialog with that place ticked.

## The coordinator's recommendation
Build P1 first, as the control and the record, with the view "around my selection" made from the same data (parents, this, children: the idea of P5 inside the outline). Add the small map of P6 later, read-only, if the outline alone proves not enough. Reasons: it is the only form that can carry the sentences the measured cases show are needed; it needs no new package; it is the smallest build; all three viewpoints accept it.
What it must hold, from the three files: plain words for the tiers; "recomputed" kept apart from "the entity leaves"; the steps between the place and each figure in one folded line (the kind of join, a filter that drops empty values, a grouping, a fill); a collapsed line always shows how many tables and figures are below; the tables no plot reads as a first group, each with its description; "1 table changed" when no figure changes; a text mark on each node that holds a step.

## Questions for the owner
1. P1 first, the map later if needed: yes, or another option?
2. A count at the chosen place before confirming (rows and entities before and after; a warning for nothing removed or everything removed): yes? It reopens D-0545 for that one count only.
3. The split per figure "the entity leaves / the entity stays" before confirming: automatic, on request (a button "Check what each figure will show"), or only after Apply?
4. The plain words for the tiers: "right after the file is read" / "after the tables are joined and prepared" / "only inside one figure", with the tier number in small print: yes, or your words?
5. Should the lineage also be readable in Exploration (read-only, no choice of scope)?

## Her question: an audit step at a result table with no plot
Today: not possible from the screen. The library allows a step at tier 1 of any table; the dialog starts from the open plot and HOME cannot open a table no plot reads. With the lineage panel such a table is a line of the first group; a click opens the dialog at that table; after the step the screen says which table changed and that it is in the export.
