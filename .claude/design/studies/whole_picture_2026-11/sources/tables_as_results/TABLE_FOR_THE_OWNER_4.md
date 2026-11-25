# The audit of a result table: did my step work, and what is affected (panel round 4, with trials, 2026-11-22)

Your order (channel block M552): opinions AND tests. The solutions were RUN on the demo recipe's real tables with the real engine; the viewpoints judged the outputs. Trials, scripts and outputs: `tmpAI/panel/tables_as_results/trials/REPORT.md`. Viewpoints: scientist, user, and the architect answering also for the developer. They recommend; you decide.

Your words: "What we want to know is that our changes worked and what is affected".

## 1. Flags first
1. **Your baseline is right, proven by a run.** Compare the ORIGINAL result with the AUDITED result, both at the last stage. On a copy of the demo where the entry has its own last step ("remove Germany") and one sample was removed upstream: original result against audited result shows 1 row removed and 31 values changed (true). T2 against the audited result shows 11 rows "removed", of which 10 are Germany rows the audit never touched.
2. **Sorting is not needed for your whole-row diff, and sorting would hide something.** The rows of the two tables are compared as a counted set (a row present twice counts twice), so their order does not matter. Sorting on every column fails on some column types, and it hides a change of the ROW ORDER, which is part of a result. The order is reported on its own line: "row order: same / different".
3. **Your whole-row diff misleads on one kind of table.** Where a value is computed over all samples (the z-score table), removing one sample moves every row a little: 42 lines "only in the original" and 41 "only in the audited table". It then looks as if the whole table was replaced, and the removed sample is one line among 42.
4. **No solution says WHY a number moved.** In a summary the removed sample is not a row. "19 -> 18" must not be read as "someone edited a number". What gives the why is a small table per audit step (section 3, S6).
5. **A dropped column makes the whole-row diff say "0 rows differ"** unless the dropped columns are listed on their own line. They must always be listed.
6. **A key must be verified, never assumed.** A candidate from the recipe is checked on BOTH tables (no two rows share it, no empty value); otherwise the app refuses to pair and says why. In the trial a table with 50 rows per sample was refused, correctly.
7. **The comparison is exact.** No difference appeared when the same table was built twice, stored and read back. But a change of the smallest possible step in a number makes a row "differ". The screen says "exact comparison". A tolerance would be a visible setting of yours, never a hidden one.
8. **"Its own recipe and its own data hashes" is half true today.** By a run: the recipe hash differs between the original and the audit; the data hash is the same (a removal is a step; the data files are the same bytes). The audit record you decided (D-0333) is not built yet.
9. **Found on the way, a defect:** with "All rows" off, the grid's own line says "Viewing rows 1 through 9 of 100" for a table of 1000 rows. You remembered a total; it is the wrong one. It is being corrected with the two preview sentences.

## 2. What each solution showed (real outputs, one sample removed from all tables)
| Solution | Summary per country and year (no sample id) | Value computed over all samples (z-score) | One row per sample | Long table, no key |
|---|---|---|---|---|
| **S1** your whole-row diff, no key, duplicates counted | clear: `Norway|2024|19` gone, `Norway|2024|18` new | **misleads**: 42 lines against 41 | clear: the sample's row is gone | clear: its 3 rows are gone |
| **S2** paired by a verified key | clearest: `Norway | 2024 | n_samples 19 -> 18` | clear: 1 row removed, 41 values changed, the column named | clear | **refused**: no key (correct) |
| **S3** the counts line | rows 6 -> 6 | rows 42 -> 41; mean of `n50` 308497 -> 307085 | rows before and after | rows before and after |
| **S4** per column: changed or not, how far | yes | `n50_zscore`: 41 of 41 changed, by -0.004 to +0.026; `n50`: 0 | yes | refused (needs the key) |
| **S5** S1 with rows paired where one column differs | paired right here | paired right here | paired right | paired right |
| **S6** per audit step alone: rows removed, values changed | yes | "remove the sample": 1 row, 41 values; "drop Germany": 10 rows, 0 values | yes | counts only |
- S5 paired wrongly on a constructed case (a removed `France|2022|7` with a new `France|2023|7`, read as "the year changed"). It is a guess. All viewpoints drop it.
- S6's numbers do not add up across steps (41 values and 0 alone; 31 together, because the Germany rows are then gone). The screen must say so.
- Cost on the demo: a few milliseconds each; S6 costs one audit run per step (2.3 seconds for a removal upstream). On 100,000 rows and 30 columns: under a second, 24 MB per table held in memory.

## 3. The viewpoints
| | Scientist | User | Architect and developer |
|---|---|---|---|
| Baseline | the original result, not T2 | (not asked) | the two tables are already built in one place (`app/modules/audit_run.py:266-271`); it compares them only as equal or not, and nothing on screen uses it yet |
| S1 whole-row diff | keep, capped; the only view that works with no key | on request, for small tables; not for the z-score kind | build first, as counted sets, never a guess |
| S2 paired by key | keep where the key is verified; keep the refusal | on request; "the clearest one" | build second; the rule "a candidate from the recipe, verified on the data, else refuse" is sound |
| S3 counts line | keep, always shown, with the lists of columns on both sides | always shown | build first |
| S4 per column | keep, with S2 | on request | later, from S2 |
| S5 guessed pairs | drop | do not show | drop |
| S6 per step | keep: the only piece that names the decision | always, in the right panel beside each step | last; computed once at Apply, kept with the audit log; if the data or the recipe changed since, shown as "not current", never as current |
| Strongest con of their own choice | more to read; a verified key proves that rows are unique, not that a row means the same thing | no solution says why; a user may read "19 -> 18" as an edit | the shared library gains a table comparison in Polars while the place of Polars in the app is not decided |

Your doubt about a key for aggregations: answered by the trial. The group-by columns are the key of a summary; verified on both tables they give `n_samples 19 -> 18`. The key identifies the GROUP, not the sample: the words on screen must say "this group lost a sample".

## 4. My recommendation (the coordinator's; yours to accept, change or refuse)
Layers, each true by itself, the first always shown, the others on request:
1. **Always, one line above the table:** which two tables are compared (the original result and the audited result), rows and columns before and after, how many rows are only in one of them, the columns dropped, "row order same / different", "exact comparison".
2. **On request, your whole-row diff:** "only in the original" and "only in the audited table", counted, with a limit and "and N more" (never cut silently).
3. **On request, where a key is verified:** the paired view: rows removed, rows added, values changed "before -> after", and per column how many changed. Where no key can be verified: one sentence saying why, and layer 2 stays.
4. **Beside each audit step (the right panel):** for that step alone, rows removed and values changed in this result. This is the "did my step work", and the nearest thing to the "why".
Not built: the guessed pairing (S5). Compared as one thing, computed once, in one place: HOME, the export and the audit log read the same record.
What can be built before the result table exists: layers 1 to 3 take two tables, so they work today for the table of any PLOT in Audit mode (the data preview of T3 has the same question). Layer 4 needs the audit run wired to the screen.

## 5. For you to decide (nothing chosen)
1. The layers of section 4: all four; or which.
2. Where "on request" lives: the Compare switch (for a table it opens the diff instead of doing nothing), or a control beside the table. Your design: no new grid, no new panel.
3. Exact comparison only; or a tolerance you set and see.
4. The export of an audit: the original result and the audited result both by name; the diff itself as a file; or only the audit log with the counts (your D-0478: the log with what was shown is always exported).
5. May a recipe author DECLARE the key of a result table? Needed only for long tables where the app cannot find one; not needed now.
6. Above a size (rows times columns), the lists are refused with a plain line and the counts are still shown: the limit is yours.
7. The words. Suggestions of the user viewpoint, not final: "Your step removed 1 sample. This table: 42 -> 41 rows, 4 -> 4 columns. 41 rows kept, 1 row removed, 0 added; 41 values changed in column n50_zscore."; headings "Removed rows", "Added rows", "Changed values (before -> after)"; "No key identifies a row in this table, so rows cannot be paired. Listed: only in the original, only in the audited table."; beside the steps "Step | rows removed | values changed".

## 6. A build order if you choose it (each slice complete, tests first)
1. Tests first: empty tables, duplicated rows, empty values and NaN, a column whose type changed, a dropped column, a changed row order.
2. Layers 1 and 2 (the counts line and the whole-row diff), for the tables of plots now.
3. Layer 3, where a key is verified.
4. Layer 4, with the audit run wired to the screen and the numbers kept with the audit log.
5. The result-table entry (ledger D-0485) reuses all of it.

## 7. Not verified
No browser run. No real result table exists yet: the trials used the tables that plots read. Audit steps written at an entry's own last stage were not tried (that form is not merged). The "why" of a moved aggregate beyond layer 4 was not solved by any solution.
