# Lineage and scope in HOME: the view of the user who is not a developer (viewpoint 3 of 3)

Saved by the coordinator from the agent's final report, 2026-11-24. The agent read `01_architect.md`, `02_data_scientist.md`, the dialog text at `app/handlers/filter_and_audit_handlers.py:1112-1141` and `app/modules/audit_places.py:195-217`. Not read: the user guide page, the demo plot names, any running screen (it judges from the texts only).

## 0. What I see today, and why I need more
- The dialog says: "The places read as the path of the lineage... every table and plot built from it is built again; the places below it follow from it. Choose one place, or the first place of several original tables."
- The lines read: "Table ResFinder (tier 1): 6 other tables and 9 plots are built from it".
- "Built again" sounds like "my entity is gone from all of them". The data scientist shows this is false: at the metadata table 9 figures change, the entity leaves only 2; in the other 7 it stays with empty values.
- I cannot tell: where in the pipeline I am; what "tier" means; which figure keeps my entity.

## 1. The three things that matter most
1. Say "recomputed" and "entity removed" as two separate things. Never let "reaches 10 figures" read as "gone from 10 figures".
2. Show the count at the place before I confirm ("ResFinder: 74 rows, 42 entities, to 72 rows, 41 entities"). If my step removes nothing (an id with a space) or everything, say so. That is a count at one table, not a full run.
3. Every table is reachable and has a plain description, also tables no figure reads.

## 2. Plain words for "tier"
| Today | Plain wording |
|---|---|
| tier 1 | "right after the file is read" |
| tier 2 | "after the tables are joined and prepared" |
| tier 3 | "only inside one figure" |
Alternative: "Table ResFinder, as read" / "Table ResFinder, ready for figures" / "Figure amr_heatmap only"; the number in small print.

## 3. The words and layout wanted for "remove one entity at the ResFinder table" (above Confirm, whichever proposal)
```
You are here:  Original file ResFinder  ->  [ResFinder, as read]  <- your step goes HERE
Your step: remove entity 32557144.
At this place: found in 2 rows; 74 -> 72 rows, 42 -> 41 entities.

Rebuilt from this place: 4 tables, 5 figures (names, click to open).
Of these 5 figures:
  - the entity LEAVES: amr_heatmap, qa_amr_genes_per_sample, qa_fanout_rows_per_sample
  - the entity STAYS (kept through a join, its ResFinder values empty):
      virulence_bar, virulence_variants
Not rebuilt: 12 other figures.
(Also fed by the same original file: ... names.)

[ ] Apply here    [ ] Apply to one figure only: amr_heatmap    [Cancel]
```
- The LEAVES / STAYS split is what a count of "5 figures" cannot give.
- If the app cannot say it before confirming, it must say plainly: "Rebuilt does not mean removed. Some figures keep the entity with empty values. After Apply you will see rows and entities before and after for each figure." That is the minimum, not the aim (the split needs a full run: 0.27 to 1 s on the demo).
- For the metadata table: "9 figures rebuilt; the entity stays in 7 of them with empty country and year."
- A short list of the steps between my place and a figure, in words, one line per figure, folded: "joined to the metadata (keeps all entities), then filtered to years 2023-2025 (drops entities with no year)".

## 4. Each proposal as a user
- P1 outline: I read lists easily; names, where I am, one sentence per row. Hidden: the shape (a table with six parents appears once; "see above" lines are easy to miss). Needs a text label for derived against refused (not colour only) and a search box. Verdict: the control I trust.
- P2 server-drawn SVG: arrows give direction; text hidden unless a twin is added; a tall drawing to scroll; position read as importance. Not worth the cost.
- P3 graph map: best shape; hides the name lists and the notes unless a text panel is added; hiding my neighbourhood makes me forget the other figures; a node clicked by mistake (the confirmation must repeat the place name). Fine as an addition, not alone.
- P4 flow with widths: I would read width as amount of data. Do not use.
- P5 columns (parents | selected | children): very clear for one table; hides the other branches; I lose where I am after three clicks. Good as the view from my selection.
- P6 outline + small map: the list for choosing, the picture for orientation; if the map folds figures into "5 plots" I must still reach the names. What I want, in two steps (list first).
- My mix: P1 as the control, P5's "parents / this / children" as the view from my selection, the P3 map later as a read-only picture; all three show the same text.

## 5. Pitfalls (all proposals)
- "Recomputed" read as "removed": the big one.
- Derived against refused: plain wording: "Covered by your step above. Nothing to choose here." / "Not available: you already chose a place below. Untick that one to use this."
- A table no figure reads: I would not find it, nor know that "0 figures changed" is not "nothing changed".
- A collapsed branch hiding a changed figure: a collapsed row always shows "N tables, M figures below", names one click away.
- An id with a space or another case: matches nothing, no message.
- A threshold that removes nothing or everything: needs "This step removes 0 rows here" / "removes all rows here".
- A step at a table made by an inner join with a look-up (no entity id there): greyed with the reason.
- The choice for empty values (remove or keep): on the demo 19 against 23 entities; the dialog must say how many empty values exist at that place.

## 6. Before confirming, and after
- Before: where I am; the place in plain words; rows and entities at the place before and after; the warning if 0 or all rows; the list of rebuilt tables and figures by name; "also fed by the same files"; one line per figure about what lies between; that recomputed is not removed.
- After (can wait): per figure, rows and entities before and after; figures that did not change; a step after which a figure no longer draws.
- Too much: column types; every join as its own line; timings; hashes or ids; all 87 nodes open; a map and a list that disagree; more than two warnings at once. One summary line ("19 of 21 joins keep all entities; 2 drop them") with details unfolding is fine.

## 7. The two views
- Whole recipe: when I start, to learn what exists ("where is the metadata used?", "which tables have no figure?").
- From my selection: when I choose: back to every original and forward to everything below.
- One screen with a switch ("Whole recipe / Around: ResFinder"). From a figure it opens on my selection; from elsewhere on the whole recipe.
- Where: not inside the modal dialog (too small; it hides the data). A "Lineage" panel in the centre of HOME, in Audit mode, collapsed by default; a click on a node opens the dialog with that place ticked; the dialog repeats the short block of section 3. The side panel is too narrow (good only for the list of my steps).
- In Exploration a read-only view would help me understand: for the owner to decide.

## 8. A result table with no figure
- Reached by the first group of the whole view: "Result tables (no figure reads them): 6". A click opens the dialog with "Table Quality_metrics, as read"; "after joins" cannot be picked there and the screen says why in one line.
- What it is: the recipe's description and `ui_label` (one sentence, not an id).
- After my step: "No figure changes. The table Quality_metrics changes: 42 -> 41 entities. It is part of the export." Never just "0 figures affected". The table gets a mark and appears in the step list.

## 9. After confirming, and explaining it
- Later I see: a text mark on the node ("step 3: remove 32557144"), the reason, a "remove this step" button, a list "My steps" in order, each pointing to its node; rows that follow marked "covered by step 3".
- For a colleague or reviewer, from the export, text not a drawing: the step, the place in plain words, the reason; the sentence shown at the time ("5 figures rebuilt; the entity left 3 and stayed in 2"); counts before and after at the place and per figure; what I typed and which ids were found. "The other places that were not chosen" is optional.

## 10. Words I do not understand, with plain replacements
| Word | Plain replacement |
|---|---|
| place | "where the step is applied" |
| reach | "what is built from it" |
| derived | "covered by your step above" |
| blocked | "not available: you chose a place below" |
| refused | "not allowed here, with the reason" |
| node | "box" or "table / figure" |
| leaf | "end of the line" |
| DAG | do not show |
| lineage | "path of the data" or "where the data comes from" |
| tier 1/2/3 | see section 2 |
| audit copy | "a separate copy used only for this check; your original data is not changed" |
| plan / plan book | do not show |
| original files with completed ids | "original files, with missing ids added" |
| result table | "table no figure reads (it goes to the export)" |
| completion marker | "line added to fill a missing entity" |
| left join / inner join | "keeps all entities" / "keeps only entities found in both" |
| na remove / keep | "drop rows with empty values" / "keep rows with empty values" |

## 11. Ranking as the user
1. P6 (list first, map second). 2. P1 (safe, readable, complete; the real control). 3. P5 (the best view from my selection). 4. P3 alone (I lose the names and the notes). 5. P2 (cost). 6. P4 (misleading).

## 12. Where I disagree
- With the architect: the shape matters less to me than the sentence about what happens to my entity; plots folded into a count are not acceptable (I must reach the names); "tier" is not understood without help; I want arrows but not as the only information; his "ResFinder_with_metadata feeds ST22_Anchor" is false.
- With the data scientist: a count at the place before confirming is required for me, not optional (otherwise I cannot catch my own typing mistake); I would like the per-figure LEAVES / STAYS split before Apply, even on request ("Check what each figure will show"): whether the earlier decisions allow it is for the owner; his list is complete but must be layered (a short block first, the rest on click).
- For the owner: whether the lineage appears in Exploration; whether the preview of each figure runs automatically or on request.
