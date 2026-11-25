# Check 5: the golden baseline, stored pictures, equality findings (entries 37, 38, 39, 40, 41, 30)

Written 2026-11-16. HEAD `77b663f1`. Read-only check; scratch in `tmpAI/panel/verification/` (`b5_*.py`, `dump/`, `pics/`).
Labels: verified = I ran it or read it; reasoned; could not check.

Method: `b5_diff.py` compares the JSON of every baseline commit with the one before it. For B and C the tables were
materialised in detached worktrees with the project's own `golden_baseline.build_recipe` (`b5_dump.py`) and compared with
plain Polars (`b5_cmp.py`, `b5_types.py`). Only ledger lines with status DECIDED are named as hers.
Check on HEAD (the script, not a test suite): `golden_baseline.py --check app/tests/golden/baseline.json` -> "result-identical" (verified).

## A. Table: every commit that moved `app/tests/golden/baseline.json` since 2026-11-09

The baseline has 7 recipes and 76 entries (T1, T2, plot data). Six commits (the first creates it).

| Commit, date | Added | Removed | Changed in content | Changed in type only | Reason in the message | Decision that allows it | Verdict |
|---|---|---|---|---|---|---|---|
| `18e5cda6` 11-13 | 76 (file made) | 0 | - | - | first golden baseline | D-0039 "DEC43 one migration tool, golden baseline" (DECIDED) | ALLOWED AND EXACT (a first record, nothing to change) |
| `99a14148` 11-14 | 0 | 0 | 7 | 0 | "two deliberate changes": demo recipe; ST22 phenotype rename | demo: D-0047 "demo recipe corrected (Eve)" (DECIDED, tasks.md DEMO-RECIPE-1 "(Eve)"). ST22 `phenotype`: none found for the column (DEMO-RECIPE-1 itself says "Eve to confirm" and D-0050 "No silent error" only covers that the old silent skip is visible) | ST22_Anchor 4 entries: ALLOWED BUT NOT CONFIRMED (no decision for the column; one question). demo_abromics 3 entries: ALLOWED BUT MORE CHANGED THAN THE DECISION SAYS (see B) |
| `ce373923` 11-14 | 3 | 3 | 0 | 0 | "three plot ids of figshare_integration are lower case now" | D-0034 line is about the recipe format; I found no decision that names the lower-case ids | NO DECISION FOUND for the rename (content proven identical: the 3 hashes, rows, columns equal before and after, verified) |
| `1547aab9` 11-14 | 0 | 0 | 0 | 14 | sample_id Categorical to String where not joined | D-0057 (Categorical and String both usable; shipped recipes to String where plain text) (DECIDED, dated 11-15, i.e. after this commit) | ALLOWED AND EXACT for the values (C). The decision is dated one day later than the commit |
| `9490490d` 11-15 | 0 | 0 | 2 | 0 | issue #77: a schema plotted directly runs its own tier 2 | D-0034 "schema's own tier2 applied" (DEC16) (DECIDED) | ALLOWED AND EXACT (B) |
| `2ac83ddb` 11-15 | 0 | 0 | 0 | 71 | "column type text only" (CATEGORICAL-MIGRATION-1) | D-0057 and D-0098 (DECIDED) | ALLOWED AND EXACT for the values (C); the level order of Enum and String cannot be seen by the golden check |

Totals over the 6 commits: added 79 (76 first file + 3), removed 3, changed in content 9 (7 + 2), changed in type only 85 (14 + 71).
Note: the 7 of `99a14148` are 4 + 3 entries as listed below. The 3 added and 3 removed of `ce373923` are one rename (3 ids).

## B. What the changed content is

### `99a14148`, `1_test_data_ST22_dummy` (verified, tables built before and after)
`ST22_Anchor` T1, T2 and the plots `virulence_bar`, `virulence_variants`: 617 rows both sides, one new column `phenotype` (Categorical).
Samples lost or gained: none. Compared on the 10 or 11 common columns: 0 cells differ, same row order. So the only change is the new column.
What the new column holds: the ResFinder `predicted_phenotype` renamed. 31 of 617 values are missing (null). Example row: sample 32557144, gene sul1, phenotype tetracycline.
Is it what the decision says? D-0047 names only the demo recipe. For `phenotype` no decision line; the task text says the old contract published a column that the old engine silently skipped, and that Eve is to confirm it is `Predicted Phenotype` and not the undeclared `CGE Predicted Phenotype` of the same file (not confirmed in the records I read).

### `99a14148`, `demo_abromics` `demo_join` T1, T2 and the plot `demo_st_by_source` (verified)
Before: 30 rows, 4 columns (sample_id, source, year, country): the join returned only the metadata, because the ingredient named a schema that did not exist.
After: 28 rows, 5 columns (adds `sequence_type`); `year` is now text ("2024", before the number 2024.0).
Rows are not "the same minus 2": the before table has 27 distinct sample ids plus 3 rows with no sample id; the after table has 15 distinct sample ids and no row without id.
- 12 of the 27 samples are gone (no MLST result, inner join): SYN_10481154, SYN_17716524, SYN_19405834, SYN_19953992, SYN_23244607, SYN_42019898, SYN_57921853, SYN_68041514, SYN_69408797, SYN_86102363, SYN_87929678, SYN_99643781.
- The 3 rows with a missing sample id are gone.
- 13 rows are repeats of a sample (MLST has several rows per sample; SYN_74255382 has 6 rows with 5 different sequence types). The task text says "one row per sample"; the table is not one row per sample.
- The plot before: a VisualizationError (display name `Sequence Type` as an aesthetic); now it draws 28 rows (the plot counts rows).
What the decision says: D-0047 "demo recipe corrected (Eve)" and the task: "demo_join 30 rows (metadata only) -> 28 rows (the samples that have an MLST result)". The task line does not say that 12 samples and 3 id-less rows drop out, nor that the result is not one row per sample (the recipe's own description for MLST says "a sample can appear on more than one row"). Verdict: the correction itself is decided; the silent size of the loss (12 of 27 samples, 3 id-less rows) is not stated in the decision.

### `9490490d`, `ResFinder` T2 and `amr_heatmap` (verified; the fix that made the change is `fe2a812e`, 13:09:41, the baseline regenerated 73 seconds later)
I built the table before the engine fix (`fe2a812e^`) and after: 70 rows both; same rows in any order (all cells equal); one new column `total_gene_count` (UInt32, e.g. 8 for sample 16632098); the row ORDER changed (sorted by `total_gene_count` descending, then sample_id). Every other one of the 51 tables of the recipe is equal (cell by cell). This is exactly what the two steps of the ResFinder tier 2 say (D-0034, DEC16). Nothing more changed.

### `ce373923` rename (verified)
`plot_A_phenotype_bar`, `plot_B_genotype_bar`, `plot_C_resistance_class` become lower case: rows, columns and hash of each equal before and after (script compare, True x3). No other place that I found uses the capital plot ids as a plot id: `assets/scripts/figshare_plot_integration.py` only has picture file names starting `plot_A_...`; the rest are archive notes and `docs/vision/platform_evolution.qmd` (not read).

## C. What the content hash covers (entry 39)

Read in `assets/scripts/golden_baseline.py` `table_record`: sha256 of `frame.write_csv()`, so of the TEXT the CSV writer gives for each cell, header and row order included. Types are not in the hash (they are a separate field, `columns`).
Three small cases (run):
1. Text "2022" against the number 2022: same hash (b3fd612550 both). A float 2022.0 gives another hash (2a5c83eb8d): "2022.0" is written.
2. A rounded decimal gives another hash (0.123456789012 / Float32 / round(2): three different hashes). Int64 5 against Float64 5.0: another hash.
3. A date turned to text: same hash. Categorical against String: same hash. An Enum with another level order: same hash. A date against a datetime at midnight: another hash.
Proof for the two type commits (verified): all 7 recipes materialised at `ce373923` (before any type change) and at `2ac83ddb` (after both). 74 tables compared, 72 have a changed type: 234 columns (231 Categorical to String, 3 Categorical to Float64). Values compared as text (and numerically for the Float64): 0 differences, same rows, same order. The only two tables that differ are the 2 ResFinder tables of `9490490d` (B). The Enum columns of the figshare recipe are written by my scratch store as Categorical (parquet), so for the Enum the values were compared but the declared levels were not (could not check here).
What the golden check cannot see, in three lines:
- A change of type that writes the same text (text vs number, Categorical vs String vs Enum, date vs text): the hash does not move; only the type field would, and that is edited by regenerating the baseline.
- The order of the levels of a category or an Enum (the order a plot axis uses), and Enum levels left out.
- Anything outside the 7 recipes and their raw data in `assets/test_data` (other data, dirty data, the export, HOME views).

## D. Stored pictures (entry 30; verified for what is named)

Since 11-09 the PNG commits outside `docs/UML/diagrams` (about 41 files of diagrams, documents) are only the gallery previews:
| Commit | What | Reason in the message | Decision | Verdict |
|---|---|---|---|---|
| `abc6a186` 11-14 13:32 | 8 examples (boxplot_faceted, boxplot_simple, jitter_strip, point_faceted, point_simple, tile_simple, violin_faceted, violin_simple), plot and thumb | "whose picture differs from the committed one (review each, drop what is not wanted)" | D-0077 "gallery screen works as before; all gallery recipes rewritten, every one works" (DECIDED) | Not shown that she looked at them. 7 changed size 800x600 to 960x600; `jitter_strip` same size, 2.60 percent of pixels differ. I looked at 1 of the 8: `boxplot_simple`: same data and boxes; new picture is larger, axis labels turned 45 degrees, median line thicker. Presentation only for this one. The other 7 not viewed |
| `d81ce81f` 11-14 | density_simple, histogram_simple, ridgeline_advanced: size only | "pixel-identical at the old size, now 960 x 600" | D-0077 | ALLOWED (size) |
| `5363c930` 11-15 | beeswarm_sina new preview | "0.82 percent of the pixels differ, because the points were never seeded before" (I measured 0.82 percent) | D-0056 seed fixed at 0 and written in the recipe; D-0062 beeswarm_sina converted (both DECIDED) | ALLOWED AND EXACT |
No picture changed in a commit that says nothing about pictures (the only PNG commits are the four above plus UML diagram images in documents commits). The ST22 `amr_heatmap` plot picture is not stored in git (the baseline stores plot data; the PNG hash mentioned in `9490490d` is not in the repository).

## E. Equality tests' stored findings (entry 41)
History of `FINDINGS.md` and `open_findings.py`: `8c172bd2` (11-15, added: F1 6 differences, F2 5 differences) and `2e0be951` (11-16, F1 marked corrected, recipe copies regenerated).
- F1 (a missing phenotype counted as a class): removed from the open list because commit `7f4ea21a` (11-16) changed the SHIPPED recipe formula `AMR_Profile_Joint.yaml` to `drop_nulls().n_unique()`. It is a fix of a recipe, not a removal. The claim "no shipped number moves" is true for the golden baseline: the check on HEAD says result-identical (verified). Whether the dirty-data cases now pass I could NOT run (pytest was refused in this session; I did not try to work around it).
- Decision for that formula change: none found (no ledger line for it; `RECIPE-FIXES-1` appears only in the spec table of the checker). The change alters the result of the shipped recipe for data that has a missing phenotype. Question 4.
- F2 (`null_values: []`): still open, not fixed, 5 differences kept outside the default run.

## F. Entries as actual checks
- **30 (pictures)**: DID NOT DEVIATE in the sense that every changed picture has a commit message with a reason and the three commits are about gallery recipes (D-0077, D-0056, D-0062). Left open: 7 of the 8 pictures not viewed by me; no record that she reviewed them. Evidence section D.
- **37 (`99a14148`)**: DEVIATED partly (demo_join: the loss of 12 samples and 3 id-less rows is larger than the decision text; the column `phenotype` has no decision). ST22_Anchor itself: only a column added, nothing else moved. Evidence section B. Size of a fix: none to make; the choice is hers (questions 1 and 2).
- **38 (`ce373923`)**: DID NOT DEVIATE in the data (3 hashes equal). No decision found for the rename; no other plot-id use found; saved sessions not checked. Question 3.
- **39**: DID NOT DEVIATE (0 value differences in 234 columns; section C). The check cannot see the level order.
- **40 (`9490490d`)**: DID NOT DEVIATE from DEC16: exactly the new column and the sort; 70 rows unchanged; every other table equal. The old picture of `amr_heatmap` is not stored, so a side-by-side is not possible. Her possible surprise: row order and a new column in a table she may know.
- **41**: COULD NOT BE CHECKED by run (pytest refused). Read: F1 fixed by a recipe change (7f4ea21a), F2 open; the `unknown[...]` question is still open.

## Questions for Eve
1. `demo_abromics` now keeps 28 rows for 15 samples (12 samples without an MLST result and 3 rows without a sample id are gone, one sample can have up to 6 rows). Keep it as it is, or change the join so every metadata sample stays (a left join) or one row per sample?
2. In `ST22_Anchor` the new column `phenotype` is the ResFinder `predicted_phenotype` (31 of 617 empty). Is that the column you meant, or `CGE Predicted Phenotype`?
3. The three figshare plot ids were written in lower case (`plot_a_...`). Do you accept it? No other place uses the capital ids as plot ids (a saved session or export that named them is not checked).
4. The formula of the multi-resistance flag changed so that a missing phenotype is not counted (no shipped number moves). Do you accept it for data that has a missing phenotype (2 of 64 rows in the dirty test data)? And does `unknown[...]` count as a class (16 or 11 samples)?
5. Eight gallery pictures changed in `abc6a186` (larger, labels turned; jitter_strip 2.6 percent of pixels). Did you look at them? Keep, or put the old ones back?
6. `ResFinder` T2 rows are now sorted by gene count, with one more column. Keep (DEC16) or ask for the old order?
