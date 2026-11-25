# How a HOME user finds and opens the tables of a recipe: your lineage picker (panel of 2026-11-22)

Your order: ledger D-0496. A read-only study: nothing is built from it. Four viewpoints, one round: scientist, architect, developer, a user who is not a developer. Facts: `FACTS.md` (this folder). The viewpoints in full: `VIEWPOINTS.md`. The panel recommends; you decide.

## 1. Flags first
1. **Today HOME cannot show the table you need in your own case.** On `mlst_bar` you can see the two data files as read, and T1, T2, T3 of `MLST_with_metadata`. That is all. No other join, and none of the 6 tables that no plot reads, can be opened. So "nothing new" does not meet your decision that every table is viewable (D-0457).
2. **Three places of the code assume "the table shown is the open plot's table".** If a table can be picked freely, each must change, or the screen would mislead:
   - The exploration filters are tied to (recipe, mode, stage, plot), not to the table. A pick from one table to another under the same plot would KEEP the filters of the first table on the second. The table must be part of that key.
   - "Send to Audit" is offered when the stage is T3. After a free pick, "T3" must mean "T3 of the open plot's own table", or a step would be written at the plot while another table is on screen (your rule: no wrong scope, D-0450).
   - The export's README line says "data view T3" without the table's name.
3. **A lineage is not a tree.** A joined table has several parents: `ST22_Anchor` is built from 6 data files. In a tree per data file it appears 6 times, and a reader of one tree sees only one of its parents. All four viewpoints say: one table is ONE thing on the screen, shown with ALL its parents, wherever it is listed.
4. **Picking one data file can show almost everything.** `metadata_schema` leads to 13 joined tables and 13 plots: 41 of the 85 nodes. The demo recipe has 4 separate groups of linked tables: one of 8 data files with 14 joins and 15 plots, one of 2 data files, and two data files that stand alone. (Counted by a run of the shared graph.)
5. **It meets earlier lines of yours** (information, not an argument): D-0310 ties the choice Source, T1, T2, T3 to the open plot; your picker does not depend on it. HOME's design note of 13 November already says "the lineage popup is the navigator", with a click that shows a node's first rows, read-only, in its own window (D-0027). Your idea goes further: the table itself opens.
6. **The picker does not need the recipe form with derived tables.** Only the list of nodes changes if you confirm that form. The drawn graph depends on it most.

## 2. The alternatives
| | What it is | Merit: for | Merit: against | Your three cases (a row seen only earlier; "which figures use this file"; a table no plot reads) |
|---|---|---|---|---|
| P0 | Nothing new: the table shown follows the open plot | Table and plot always agree; nothing can mislead | The earlier tables and the 6 unread tables cannot be opened | fails 1 and 3 |
| P1 | A flat list of every table, with a search box | Reaches every table; a name is found fast in a long recipe | Shows no link between tables: the user does not know where a row comes from or where a step belongs | 1 partly; fails 2 |
| P2 | Your picker as a DRAWN graph (boxes and arrows) | The branching and both parents of a join are seen at a glance; the path up from the open result can be lit | 41 boxes with crossing arrows for `metadata_schema`; zoom and pan; small labels. The existing drawing (BLUEPRINT's tube map) has one flat layout, redraws with a flicker, and allows only one map on the page | 1 yes; 2 hard to read; 3 only if lone tables are drawn |
| P3 | Your picker as a collapsible OUTLINE (indented text, one group per data file) | Reads like a file list; no layout problem; a lone table shows as a lone root; searchable; easy to test | The branching is read, not seen; a joined table repeats under each parent and must be marked as one table | 1 yes; 2 yes (two lists of 13); 3 yes if marked |
| P4 | P2 or P3 TOGETHER with the search of P1 (your "combine with N1") | Find by name, then see where it sits; both directions | Two ways in to one choice: they must stay in step | all three, if linked |

Cost and build time are not in this table, by your rule. What a builder needs to know is in section 5.

## 3. What the four viewpoints recommend
- **All four: P4**, the picker together with search.
- **Three of four (scientist, architect, user): the OUTLINE as the base.** The drawn graph is added later, when the drawing function is made general (today it belongs to BLUEPRINT). The scientist accepts either base, on one condition: a table is shown once, with all its parents.
- **All four: a click opens the table in HOME's normal data preview**, not inside the popup. Reasons: the preview already has the row total, the hidden columns, the badge and the filters; rows shown in a popup could not be explored or audited; a second way of showing a table would have to be kept equal to the first.
- **The user viewpoint: a side panel, not a popup**, because a popup hides the plot while the user compares it with the table. You said "it can be in a popup window". This is the one point where a viewpoint differs from your words.
- **Words** (user viewpoint): a scientist who did not write the recipe does not know "lineage", "tier", "T1", "source". Plain words proposed: "Original data files", "Joined tables", "Figure", "Where this table comes from", "What uses this table".

## 4. My recommendation
**P4 with the outline as the base; each table shown once with all its parents; a click opens the table in the data preview; the drawn graph later.**
- It answers your three cases on the demo recipe, and it stays readable for `metadata_schema`.
- It keeps one place where a table is looked at, so what you explore is what you can audit.
- It needs no decision on the recipe form.

What the outline would look like for your example (a sketch, words provisional):
```
Find a table: [ mlst            ]

Original data file: MLST
   Joined table: MLST_with_metadata        built from MLST + metadata_schema
        Figure: mlst_bar                   <- the figure you are looking at
        Figure: year_distribution
   Joined table: ST22_Anchor               built from 6 data files (shown under each)
        Figure: virulence_bar
        Figure: virulence_variants
   Joined table: AR1_MLST_Serotype_Virulence   built from 4 data files; used by no figure

Used by no figure: Quality_metrics, Detailed_summary, FastP_with_metadata, ...
```
From `mlst_bar`, "Where this table comes from" opens the same outline with its path marked. A click on `MLST_with_metadata` opens it in the data preview, with a line such as: "You are viewing the table MLST_with_metadata. It is the table of the figure above." or, for another table, "It is NOT the table of the figure above (mlst_bar). The figure does not change. Your exploration filters were cleared. [Back to the figure's table]".

## 5. Facts for the build (their own row; not arguments)
- The shared recipe graph already answers "everything that comes from this data file" and "every data file of this result". Missing: the groups of linked tables; a node for the last stage of a table no plot reads.
- The engine can already build any table by its name. HOME's preview cannot ask for one: it always starts from the open plot.
- The existing drawing uses a library that is already in the app (no new one needed). It draws on a canvas, so a browser test cannot read its boxes as text; an outline is plain text.
- The same for every alternative except P0: (1) one pure function "groups, path up, path down" in the shared graph; (2) "open a table by its name" for the preview. Both can be built whatever you choose here.
- Not checked by anyone: how the drawing behaves with 85 nodes; a Shiny popup against a real second browser window; the session file.

## 6. For you to decide (nothing is chosen)
1. P0, P1, P2, P3 or P4; and for P4 the base: the outline, the drawn graph, or both from the start.
2. A click on a node: the table opens in the data preview (the preview stops following the plot until you go back), or first rows inside the popup.
3. Popup, side panel, or both possible.
4. May a HOME user view a table that is not on the path of the open plot? (Your picker says yes; your earlier line D-0310 is silent on it.)
5. "Send to Audit" when the table shown is not the open plot's table: not offered there (as today, only at the plot's own table), or offered through the dialog with the tick lines once that dialog is built.
6. The words: "Original data files", "Joined tables", "Figure", "Where this table comes from", "What uses this table", or others.
7. Which app features switch shows the picker: the one that already shows the choice Source, T1, T2, T3 (interactivity), or a new one.
8. May the two common parts (section 5, last point but one) be built now, before your answers? They are needed by every alternative except "nothing new".

You said you may have more questions after this panel: the review session brings them to me.
