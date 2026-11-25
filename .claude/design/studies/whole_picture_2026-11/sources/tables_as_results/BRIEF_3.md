# Panel round 3: the owner's own design for a table as a result (2026-11-22)

PRIORITY: the owner waits for this to answer a question that blocks a build. One round. You only recommend; she decides. Never read `tmp.md`.

Read first, in full, in this folder: `FACTS_2.md` (what a tier shows; what ties a tier 3 to a plot; what exists), `FACTS.md` (what is decided), `TABLE_FOR_THE_OWNER_2.md` (round 2: all four chose "one explicit key on a plot entry"). Verify at file:line what you rely on.

## Her rules for this panel
- Judge ON MERIT. That something reopens a decision, a check or a definition is information only: one line "Reopens:", never an argument.
- Build time is not an argument. "Avoid building something new" is a value she named: say honestly what is reused and what is not.
- The data stays data. The "All rows" switch stays.
- All tiers must work as written and follow the recipe: no tier is fixed or refused by the app.

## Her words (the essential ones)
"if its a table then mapping and layers cannot be an error because there is no plotting. My suggestion was we can have a "fake plot" that says the result is the table - so the the user needs to read the table and not the plot ... My point is that we do not need to have a special table plot panel we can use the preview/view table already existing - and at export we need to be sure the final table that is the result is provided by name as part of a result (not only an itermediary step)"
"I did not foresee the consequence of removing audit for the table as result ... because we can already drop key and filter on tables --- so it would only remove the comparison you mean ? I guess as long as the changes and what they do here are marked that would be ok - or we could hook a diff in the comparison ?"
"yes the result is the last stage. because the original table still work I think a diff could be an option - proposing alternative options are welcome. so a plot entry actually should be a result_entry with either plot or table no? last tier of entry also can be T3=T2=T1 (so the fall back mechanism) - For blueprint we will have to look at that later but good to see if solution can work - we will have to refactor blueprint any how. ... we need to follow the recipe --- so do not fix all tiers need to be functional."

## Her design, as she approved it
1. The thing a group holds is a RESULT ENTRY, which is either a plot or a table. A key says which (naming open: keep the list `plots` with a key such as `show`, or a general name such as `results`). A table entry needs no `mapping` or `layers`: nothing is drawn.
2. No new grid and no new panel. HOME reuses the data preview ("Table to view", "All rows"). When the entry's sub-tab is selected, the plot area shows a short sentence (the "fake plot": the result is the table, read it below), and the preview opens on that entry's table.
3. The result is always the LAST STAGE of the entry: tier 3 = tier 2 plus the entry's own steps, equal to tier 2 or tier 1 when there are none. No key to choose a tier.
4. At export the result is provided BY NAME as a result, always, distinct from the intermediate T1, T2, T3 files.
5. All tiers are functional and follow the recipe: tier 2 and tier 3 on any table work as written.

## What she asks the panel (answer what your viewpoint is asked in your own prompt; evidence at file:line)
(a) Can it work? What does each place do with such an entry: the opening build ("draws every plot once"), the export pictures, the Gallery previews, BLUEPRINT's live plot (only whether it CAN work; BLUEPRINT is refactored later), the report, the audit dialog and the lineage words ("plot"). How must the check PS03 change for the explicit key, and what happens when the key and a drawing part are both written?
(b) How does the data preview select the entry's table when its sub-tab is active (today it already follows the active sub-tab's entry: `app/handlers/home_theater.py:1671-1702`)? What does the plot area show? The sentence "Showing 100 of N rows".
(c) The export: the file name and place of the result (from `ui_label` or from the id?), how it is listed as a result in the README and the report, distinct from `T3_data_<id>.tsv`.
(d) Audit: filters and column drops work as on any tier 3 in Audit mode, and the original table still works ("Table to view" on T2 or T1 shows originals; Exploration shows the Result). What is missing is "Original against Audited" side by side for a table. Options: (d1) her idea, a DIFF in the comparison (which rows and columns were removed, which values changed); (d2) the applied audit steps marked on the table (a line above it: "audited: 2 steps applied, N rows and M columns removed"), no side by side; (d3) two grids side by side, as for plots; (d4) nothing beyond the badge; others you find. For each: what the user learns, what could change silently, what it needs.
(e) The names: the entry and its list. (e1) keep `plots` and add a key on the entry; (e2) rename the list to a general name such as `results` (and the code's "plot entry" to "result entry"); (e3) other. The cost of each in places (the recipe format and check; the places that read the list: the architect counted about 34, the developer 66 reads in 27 files; the documents; every shipped recipe and Gallery bundle would be migrated under e2: a names migration is being prepared anyway, the script `assets/scripts/migrate_display_names.py` exists), and what each reopens.
(f) Which of the earlier flags still apply (round 2, section 2 of `TABLE_FOR_THE_OWNER_2.md`).

## Your answer: AT MOST 300 words
Can it work (yes / yes with these conditions / no, because); your choice for (d) and for (e) with the reason and the strongest con of your choice; anything in her design you would change, with the reason (she welcomes alternatives); "Reopens:"; "Flags:" anything that changes a result silently, hides a step, or differs between screen and export. Evidence as file:line. No preamble.
