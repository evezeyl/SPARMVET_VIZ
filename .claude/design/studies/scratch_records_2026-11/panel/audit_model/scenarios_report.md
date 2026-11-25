# AUDIT-MODEL-SCENARIOS-1: tests of Eve's mental model of the audit, on recipe 1 (`1_test_data_ST22_dummy`)

Branch `feat/recipe-format-1`, HEAD `46fa84da`. Read-only on the repository: nothing under `config/`, `libs/`, `app/` changed. The only files edited are the two lists under `tmpAI/panel/round7/` (part b), with copies of the originals in `tmpAI/panel/audit_model/orig/`.
Labels: RUN = I ran it, with the real engine (`DataOrchestrator` on a forked copy of the recipe, real actions `modif_filter`); the plot T3 step is applied with the same real action on the plot's T2 table, because the engine has no reader of a plot's tier-3 list (`libs/utils/src/utils/recipe_check.py:46`, `:900`).
Scripts and outputs: `tmpAI/panel/audit_model/` (`common.py`, `engine.py`, `s0` to `s11`, outputs in `out/`). Re-run: `source tmpAI/panel/audit_model/env.sh; ./.venv/bin/python tmpAI/panel/audit_model/s3.py`.
Her words from M188 are quoted as "relayed, 2026-11-16".

## 0. The results that do NOT fit her model (read these first)

1. **A removal written at the metadata does not remove the samples from the tables that read the metadata as a lookup.** Step `country != Norway` at T1 of `metadata_schema`: 14 samples left in the metadata file, but 16 of the 38 downstream places that hold sample ids keep all 42 samples, the 28 Norway samples now with `country` empty (left joins keep them). Example: `qc_reads_horizontal_barplot` still draws 42 samples, 28 of them with an empty country. Plots affected: `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou`. (S2 B, S5, S11-3; RUN)
2. **"All ticked" with a property step does not repair it.** Ticking the property step at every place that has the column, with `na: keep`, leaves the samples at the same 16 downstream places: the earlier tick blanks the value, the later tick finds it empty and keeps the row. Second example (year 2023, 8 samples): of the 27 places that have `year`, 12 still hold a 2023 sample (one is a plot). With `na: remove` it is 0 of 27, but then the rows that were empty from the start also go. The same intent as a list of sample ids ("remove these from all tables") removes them at every place. (S10, S11-3; RUN)
3. **The check after Apply by the property is blind.** After step 1, "country = Norway" finds 0 samples left although 28 samples are still in the plot above. With the 21 ids of the T2 view, the property check finds the 7 left-over samples at 34 places, the sample ids find them at 66 places: a table without the column cannot be checked by the property. (S2 B, S3; RUN)
4. **The old sentence "the plots are the same, only the tables before the year filter differ" is wrong for "remove from all tables".** With the 21 ids of T2 against the 28 ids of T1, 68 of 73 places differ and 15 of 17 plots differ; the 7 Norway samples of 2022 stay in 66 places and in 14 plots. The sentence was true only when ONE table is ticked. (S3; RUN)
5. **A sample removed from a lookup table stays in the table built from the other side, with a count of 0.** The 21 ids removed at `ResFinder` (T1): `QA_AMR_per_sample` T2 still has 42 samples; the 20 removed samples with hits are listed with `n_amr_genes` 0 (before: 1 to 4). The group "samples with no AMR gene" grows. (S8a; RUN)
6. **The earlier place covers the later one only if the recipe does not change the values in between.** Same rows are removed, but: the z-score of `QA_population_zscore` differs for 14 of 14 remaining samples (largest difference 0.57); `virulence_count` of `ST22_Anchor` differs on 1543 of 1543 rows. With a recode between the two places (scratch copy: "Norway" becomes "Norge" in T2 of `MLST_with_metadata`): the user selects Norge at T2, the rule writes that condition at T1, T1 loses 0 of 42 rows, silently; written at T2 it removes 21 of 33; the 21 ids work at both. (S4, S11-2; RUN)
7. **The same information has three names, so a search by name misses places.** `VF_gene` (VirulenceFinder, QA_fanout), `Selected_Virulence_Genes` (ST22_Anchor and its 2 plots) and `selected_virulence_genes` (AR1). A search for one name finds 4 places or 3, not all. `year_label` exists only from QA_year_types on; `era` only at T2. (S6, S4; RUN)
8. **Counts at a view depend on what the table holds, not only on the recipe's filters.** A third number: "Norway" at `ResFinder_with_metadata` is 27 (ResFinder lists 38 samples only), besides 28 and 21. And `metadata_schema` has no T2 of its own: it shows 28 at T1 and at T2; the 21 appears only at T2 of `MLST_with_metadata`. (S1; RUN)
9. **A step written at a place without the column does not just fail there, it breaks every build downstream.** Property step at the MLST file: `IngestionError ... column 'country' is not in the table` for MLST, `MLST_with_metadata`, AR1 and ST22_Anchor. This fits D-0196 (the app must never offer it); the build refuses it, it does not skip it. (S7; RUN)
10. **A step on a reference table with an inner join removes rows downstream although the table has no `sample_id`.** Removing the gene `iutA` at `APEC_STEC_virulence_genes`: ST22_Anchor 617 to 554 rows, AR1 342 to 307, 2 plots change; no sample lost in this run. (S5; RUN)
11. **The graph lists a place where nothing changes.** Ids step at `FastP`: 4 places downstream by the graph (ST22_Anchor T1, T2, 2 plots) do not change, because FastP is a lookup there. Not a miss (0 misses over 27 tables), but the dialog must say "no effect here". (S6b; RUN)

What fits: see the table at the end of each scenario.

## S1. Norway at the metadata T1 and at T2 (counts)

RUN (`out/s1.md`). No step. The metadata file (`metadata_schema`) has 42 samples; 28 are Norway. `MLST_with_metadata` (metadata joined to the MLST file): T1 = 42 rows, 28 Norway; T2 = 33 rows, 21 Norway; the plots `mlst_bar` and `year_distribution` read T2 (33, 21). The step that makes 28 into 21: join `MLST_with_metadata`, tier 2, `modif_filter column: year, op: between, value: [2023, 2025], na: remove` (`wrangling/MLST_Metadata_wrangling.yaml`). The 7 samples that go: 20545497, 29208527, 50677095, 66108847, 71729785, 79062032, 82707226, all year 2022, all Norway. 2022 has 9 samples (7 Norway, 1 France, 1 Germany); the 2022 step removes all 9; check from the raw metadata alone: Norway in 2023 to 2025 = 21. No sample has year missing.
Fits her model: **yes, 28 at T1 and 21 at T2.** Two precisions (misfit 8): the 21 shows only at T2 of `MLST_with_metadata`, not at a "metadata T2" (the metadata file has no tier-2 steps); and a third count, 27, exists at `ResFinder_with_metadata`.

## S2. A step written at T1 only: what the later places show

RUN (`out/s2.md`). Step `country != Norway` (na keep).
- A. At `MLST_with_metadata` T1: T1 42 to 14 rows/samples; T2 33 to 12; `mlst_bar` 33 to 12; `year_distribution` 33 to 12. Nothing else changes (69 places unchanged). The graph and the engine agree. **Fits.**
- B. At `metadata_schema` T1 (the root with the column): 41 places change. Samples really removed (to 14, or 12 at T2/plots): metadata, ST22_Anchor, the 5 QA tables built from the metadata as base, MLST_with_metadata T2 and the 10 plots on those tables. Samples kept with `country` empty: FastP_with_metadata, Quast_with_metadata (126 rows, 84 empty), Bracken_with_metadata, ResFinder_with_metadata (38 samples, 45 empty rows), MLST_with_metadata T1, QC_Reads_Anchor, AR1 (226 empty rows), and the 3 plots on them. In `MLST_with_metadata` T2 the year filter then removes them (33 to 12) only because their year is empty too. **Does not fit** (misfits 1, 2, 3).
Every table joined to MLST_with_metadata: none is downstream of it in recipe 1 (only the 2 plots), so A shows no joined table.

## S3. "Remove these from all tables"

RUN (`out/s3.md`). The step `sample_id not_in [ids]` at T1 of each of the 27 tables that have `sample_id` (the 28th, `APEC_STEC_virulence_genes`, has none and is unchanged: it is a reference list). Ids of the T2 view = 21; ids of the T1 view = 28.
- With 21: 71 of 73 places change. Examples (rows/samples before to after): MLST 42/42 to 21/21; `Summary` 623/42 to 317/21; `QC_Reads_Anchor` 42/42 to 21/21; `ST22_Anchor` 617/42 to 350/21; `MLST_with_metadata` T1 42 to 21, T2 33/33 to 12/12; plots `qc_reads_horizontal_barplot` 42 to 21, `virulence_bar` 617 to 350 rows.
- With 28: MLST 14, `Summary` 208/14, `ST22_Anchor` 245/14, `MLST_with_metadata` T1 14, T2 12; every plot has lost the 28 Norway samples (at most 14 samples left: 14 or 12 on most, 11 on `amr_heatmap` where ResFinder holds 38 samples; the aggregate plot has 6 rows and no `sample_id`).
- Where the two differ: 68 of 73 places; 15 of 17 plots. Identical: the two plots `mlst_bar` and `year_distribution` only (12 samples each).
- Tables with no `country` column that receive the removal by sample id: 13 at T1 (MLST, FastP, Quast, Bracken, ResFinder, Summary, Summary_quality, Quality_metrics, Detailed_summary, VirulenceFinder, `Summary_phenotype_length_fragmentation`, `QA_ST_with_NA`, `QA_L50_integer`), e.g. `Detailed_summary` 91/36 to 44/17 (21 ids) or 30/11 (28 ids), `ResFinder` 70/38 to 37/18 or 25/11.
- After Apply, with 21: `country = Norway` still matches at 34 places (9 plots); the 28 root ids are still present at 66 places (14 plots). With 28: nowhere.
- Roots only (datasets) instead of every table: the same samples remain at the T2/T3 places (no difference in the sample counts).
**Fits her model as decided (D-0197).** The consequence she described ("if you apply in T2 there will be 21") is exactly the run; the size of it (14 plots keep the 7) is what the dialog must show.

## S4. The same condition at T1 and at T2; a column that the recipe changes

RUN (`out/s4.md`).
- Same condition at T1 and T2 of `MLST_with_metadata`, 3 conditions (country != Norway; year != 2024; the 21 ids): the second step is **redundant: T1, T2 and both plots are identical frames** to T1 alone (exact comparison). T1 alone against T2 alone: T2 and plots are identical, T1 differs (14 against 42 samples). Same at T3 of `mlst_bar`. **Fits.**
- A column the recipe changes between the places (real cases, recipe 1): derived values: `QA_population_zscore` (n50_zscore differs for 14 of 14 samples, max 0.57), `ST22_Anchor` (virulence_count differs on 1543 of 1543 rows; same rows); a rename: `VF_gene` in VirulenceFinder becomes `Selected_Virulence_Genes` in ST22_Anchor (condition `gene != hlyF`: identical ST22_Anchor T1 and T2, 543 rows, 42 samples; AR1 untouched by the anchor step, 342 to 300 rows with the dataset step); a derived column: `era` (T2 only: `era != Early` at T1 raises "column 'era' is not in the table"; the same T2 content comes from `year >= 2024` at T1); a cast: `year_label` (exists only from QA_year_types on). Scratch copy: recode "Norway" to "Norge" in T2: see misfit 6.
**Does not fit** in the cases above: the condition can mean something else, or the numbers in between differ.

## S5. A table that is not downstream; which joins carry the step

RUN (`out/s5.md`). Step at the metadata T1: 40 places downstream, 32 not (APEC, Bracken, Detailed_summary, FastP, MLST, Quality_metrics, Quast, ResFinder, Summary, Summary_quality, VirulenceFinder datasets; `QA_L50_integer`, `QA_ST_with_NA`, `Summary_phenotype_length_fragmentation`; their plots): all 32 unchanged. **Fits** (an unrelated chain is not reached).
Joins that read the metadata: as lookup with a LEFT join in 7 tables (FastP_, Quast_, Bracken_, ResFinder_, MLST_with_metadata, QC_Reads_Anchor, AR1): the samples stay, `country` empty. As base in 6 (ST22_Anchor and 5 QA tables): the samples go (42 to 14). Inner joins in the recipe: `ST22_Anchor` and AR1 with the reference list `APEC_STEC_virulence_genes` (on `VF_gene`): a step on the reference list removes rows downstream (misfit 10). Step by ids at FastP: reaches FastP_with_metadata, QC_Reads_Anchor and the plot; not ST22_Anchor (FastP is a lookup there).
Partly fits: the model says "the lineage forward", the join kind decides what a step does there (misfits 1, 5, 10).

## S6. D-0195: the places that have the property's column

RUN (`out/s6.md`, `out/s6b.txt`). `recipe_graph` (columns per node, forward lineage) does not exist: P3 is not built (`home_stage2_mechanism_spec.md:146`; the file `libs/utils/src/utils/recipe_graph.py` is absent). I built a scratch graph from the recipe (73 places = 12 datasets x T1,T2 + 16 joins x T1,T2 + 17 plots x T3) and compared three lists for 8 fields:
- B = every table built from the real data, columns read from it. A = the same engine on header-only copies of the data files (0 rows: the "dry run on the column names" of `home_stage2_mechanism_spec.md:120`; max rows in every table 0). A2 = declared `input_fields` only.
- **A and B agree on all 73 places for all 8 fields (0 differing column lists).** A2 is wrong at 52 of 73 places (misses `Selected_Virulence_Genes` 4, `year_label` 7, `VF_gene` 3; adds `year` 14, `n50` 7, `country` 2).
- `country`: 39 places = 14 tables at T1 + 13 at T2 (`QA_fanout_exhibit` loses it at T2) + 12 plots; 34 places do not have it. The "14" of the review session is the number of tables at T1 that have the column; with the second stage and the plots it is 39. `sample_id`: 69 places (27 at T1). `year` 27 (11 tables at T1), `n50` 10, `year_label` 7, `sequence_type` 12.
- The forward lineage of my graph against the real effect of a ids step at each of the 27 tables: 0 changes outside the graph (0 misses), 1 table with places listed but unchanged (FastP, 4 places).
Limits: A=B holds for recipe 1, which has no data-dependent action (a `polars_pivot` makes the columns depend on the values); a search by NAME misses renamed copies (misfit 7). **Fits D-0195 for the names that are the same; it does not for renamed or derived copies.**

## S7. Cases in which a step reaches a table that lacks the property column

RUN (`out/s7.md`, `out/s7b.txt`).
1. Only "all tables" (by sample id): 13 tables at T1 without `country` receive the ids step (S3).
2. Also a descendant that lost the column after a select/group: step written upstream (metadata T1, `country`): `QA_fanout_exhibit` T2 (group by sample) and its plot `qa_fanout_rows_per_sample` have no `country` and still change (42 to 14 rows). They are reached by the lineage, not written to.
3. The helper "use the values of this selection as a list on the key" (`home_audit_steps.md:121`): the user ticks the node; the step is the same ids step as case 1 (not run separately).
4. Written AT a node without the column (property): refused: `column 'country' is not in the table`; at the MLST file it breaks 4 downstream builds (misfit 9). At a node with neither the property nor `sample_id` (`QA_aggregated_no_key` T2, or the APEC list): refused; written at its T1 the ids step reaches the T2 (9 to 7 rows, which has no `sample_id`).
**Fits D-0196.** The steps that reach a table lacking the column are: "all tables" and the forward effect, and not a tick.

## S8. Anything else

RUN (`out/s8.md`). Misfits 5 (a count that grows: samples with 0 AMR genes), 3, 8. Also: a value typed int (2024) or float (2024.0) on a Float64 column gave the same 17 rows (no error). A T3 step that removes every row of `year_distribution` (years 2023, 2024 not_in) leaves 0 rows; `mlst_bar` (same table) unchanged. I did not render an empty plot (see "not run"). The engine cannot read a T3 step today, so a step "at T3" cannot be written in the app yet.

## S9. Hide a small year from ONE plot (relayed, 2026-11-16: "so the filter is at T3 and not at T1")

RUN (`out/s9_10.md`). Table `QA_year_types`: 2022 = 9 samples, 2023 = 8, 2024 = 25. Plot `qa_year_label` (x = year_label). Step `year_label != '2023'` at its T3.
- The plot's table loses 8 rows: 42 to 34 rows, 42 to 34 samples (Norway 28 to 26).
- Places changed: **1 of 73**. All other 72 places are identical, compared row by row: T1 and T2 of `QA_year_types` (42 rows each), the sister plot `qa_facet_by_mapping` that reads the same table (42/42), and every other table.
- The denominator of the figure: 42 before, 34 after; 8 samples left out of the plot. The table behind it still has 42 and the sister plot 42.
- What the figure draws (real VizFactory render): x categories before 2022, 2023, 2024; after 2022, 2024; the sister plot unchanged with 3.
**Fits her model.** Caution: the engine has no tier-3 reader today (simulated with the same action).

## S10. The two intents on the same value (year 2023, 8 samples)

RUN (`out/s9_10.md`, `out/s10b.md`). I1 = the property step ticked at every place that has `year` (27 places; "remove everywhere" by the node ticks, A default). I2 = "remove from all tables": the 8 ids at T1 of the 27 tables with `sample_id`. II = T3 of `qa_year_label` only.

| measure | I1 property everywhere (na keep) | I2 ids, all tables | II T3 only |
|---|---|---|---|
| places changed (of 73) | 41 | 71 | 1 |
| plots changed (of 17) | 13 | 17 | 1 |
| `qa_year_label` samples (42 before) | 34 | 34 | 34 |
| sister plot `qa_facet_by_mapping` | 34 | 34 | 42 |
| `QA_year_types` T1 | 34 | 34 | 42 |
| `FastP_with_metadata` T1 samples (42) | 42 (year empty on 8) | 34 | 42 |
| `ST22_Anchor` T1 (rows/samples, 617/42) | 426/34 | 426/34 | 617/42 |
| `MLST_with_metadata` T2 (33) | 25 | 25 | 33 |
| `Summary` (623/42) | 623/42 (no `year`) | 506/34 | 623/42 |
| `qc_reads_horizontal_barplot` | 42 (kept) | 34 | 42 |

The full 73-row table of places that differ is in `out/s9_10.md`. I1 keeps the 8 samples at 12 of the 27 places that have `year` (na keep); 0 of 27 with na remove (`out/s10b.md`). I2 removes them everywhere there is a `sample_id`.
**Fits her model for II, and for I2. Does not fit for I1** (misfit 2): the tick of every place by property does not express "remove the samples everywhere" unless the step is by ids or `na` is remove.

## S11. The three cautions as tests (relayed, 2026-11-16)

RUN (`out/s11.md`).
1. **In one chain, a step at the earlier place gives the same rows at the later places as ticking both: HOLDS on recipe 1.** For every table that has the column at T1 and for 3 conditions (ids of the T2 view: 27 of 27 tables; `country != Norway`: 14 of 14; `year != 2023`: 11 of 11), the T1 step alone and the ticks at T1 + T2 + every plot that reads it give identical frames at T2 and at the plots (exact comparison). 0 exceptions. This counts the same table only (T1, T2, plots).
2. **Only when the column is unchanged in between: the test FAILS the rule where the recipe changes values.** Holds for the same rows in the real cases `country`, `year`, `sample_id` of `MLST_with_metadata`. Fails: the values computed between (z-score 14 of 14; virulence_count 1543 of 1543); the scratch recode (T1 removes 0 of 42 rows with the T2 value, silent); the name (3 spellings, S6); the derived columns `era` and `year_label` (no earlier place). Ids survive the recode and the rename.
3. **Places of other chains are not covered: HOLDS for the unrelated chain, FAILS across a join.** Step at the metadata: 30 places that hold sample ids and are not downstream still hold the 28 Norway samples (all 30 unchanged); and of 38 downstream places that hold ids, the 28 are gone from 22 and still there at 16 (misfit 1). Ticking all places with the property leaves them at the same 16 (na keep); with na remove at 0.

## Which scenarios fit her model (one line each)

| S | Fits? |
|---|---|
| S1 | Yes: 28 at T1, 21 at T2. Two precisions (a third count 27; the metadata file has no T2). |
| S2 A | Yes. S2 B: no (samples stay in 7 lookup tables and 3 plots). |
| S3 | Yes as decided (D-0197); the old "plots are the same" is wrong (15 of 17 plots differ). |
| S4 | Yes for redundancy (identical frames). No when the recipe changes values, names or derives columns. |
| S5 | Yes for unrelated chains (32 unchanged). Left join keeps the samples; inner join with a reference list removes rows. |
| S6 | Yes for the same names (A = B on 73 places). No for renamed copies. |
| S7 | Yes (D-0196): only "all tables" by ids, and the forward effect. |
| S8 | A count that grows (misfit 5); the engine has no T3 reader. |
| S9 | Yes (1 place of 73 changes). |
| S10 | Yes for II and I2; no for I1. |
| S11 | (1) holds, (2) fails when values change, (3) holds for unrelated chains and fails across a left join. |

## (a) Draft text for the dialog and the help: "selected at T2 = 21, at T1 = 28"

Version of two sentences:
> You are looking at T2: Norway has 21 samples here, because the recipe has already removed the 7 Norway samples of 2022 before this table. "Remove these samples from all tables" removes these 21 only; Suggestion: to remove Norway from the whole lineage, select it at T1, where you see 28.

Version of five sentences:
> The samples you see depend on where you look. In `MLST_with_metadata`, Norway has 28 samples at T1 and 21 at T2, because a step of the recipe (the years 2023 to 2025) has already removed the 7 samples of 2022 before T2. "Remove these samples from all tables" removes the samples you selected in the view you are in: 21 at T2, 28 at T1. If you select at T2, the 7 samples of 2022 stay in the other tables and plots (here in 14 of 17 plots). Suggestion: to remove samples from the whole lineage, select them at T1, as early as possible; the lines below show how many samples each table and plot keeps.

(The numbers 28, 21, 7 and "14 of 17" are the real ones of recipe 1; the app would compute them for any recipe. Eve's words used: "you need to do that as early as possible in the lineage", D-0197. The draft is not decided text.)

## (b) The wrong example, corrected

Done in `tmpAI/panel/round7/FOR_EVE_one_list.md` point 2 and `FOR_EVE_still_open_2026-11-16.md` block B2 and the table row Pt2 (originals in `tmpAI/panel/audit_model/orig/`). Replacement text of the one list:
> **2. [CORRECTED 2026-11-16; Eve decided it: D-0197] Which sample ids "remove these samples from all tables" uses.** ... You cannot tick `country = Norway` at the MLST data file: that file has no `country` column, and a filter is built only in a view whose table has the column (D-0196). The case that can happen: you look at `MLST_with_metadata`: 28 Norway samples at T1, 21 at T2 (the recipe's own year filter removed the 7 of 2022). You select Norway there and choose "remove these samples from all tables". The tables without a `country` column (13 at T1) get the step as a list of sample ids. Decided: the list is the one of the view where you selected (D-0197). Run: with the 21 of T2 the 7 samples stay in 66 of 73 places and in 14 of 17 plots; with the 28 of T1 nowhere.

Other places that still carry the old wording: `FOR_EVE_one_list.md` line 18 (the word list: "*ids*: a list of sample numbers used when a table has no column for the property", true); `home_audit_steps.md:123` (the example with the 28 root ids; true, but it does not say that 21 is the T2 view's list; not edited, outside tmpAI). The lists still show B3 / point 3 with "Default (B)" and "no default supported": it is decided (D-0194: A); I did not edit them (not asked).

## (c) "Only the earliest ticked place of a chain writes the step": when it is exactly equivalent, when not (no recommendation)

Exactly equivalent (same rows and same values at every later place of the same table, T1 to T2 to the plots; exact frames): in 52 of 52 table-condition pairs of recipe 1 (ids 27, `country` 14, `year` 11): the later ticks add nothing. Also exactly equivalent: the rename (the same rows by either spelling) once the column name is translated at each place.
Not equivalent:
- The value of the column changes between the places: the recode "Norge" at T2: a condition written at T1 with the T2 value removes 0 of 42 rows (T2-only removes 21 of 33); the ids do not have the problem.
- A value computed from other rows is in between: z-score (14 of 14 differ, max 0.57), `virulence_count` (1543 of 1543 differ): the same rows go, the remaining numbers differ, so a step "after" the computation is a different result from "before".
- The column exists only later (`era`, `year_label`): the earliest place with the column is the later place; the earlier ones cannot be written to.
- Another table, through a left join: the root step leaves the samples at 16 places (28 Norway samples with empty country in 7 tables and 3 plots); ticking the later places with `na keep` does not remove them (12 of 27 places for `year`).
- Another chain: not reached (30 places keep the 28 samples).
- Other effect on the places: with a T1-only step the earlier view itself changes (T1 of `MLST_with_metadata` 42 to 14), with a T2-only step T1 stays 42; the later places are the same.

## What I did not check or run

- The audit dialog, the check after Apply and the tick lines do not exist: everything is the engine plus the actions placed by hand. The T3 step is simulated (no tier-3 reader in the engine).
- Other recipes (2_test, figshare, stress_test_master): only recipe 1. A recipe with a data-dependent action (pivot) is not tested for the dry-run column list.
- Time and preview of "check other plots while the dialog is open" (M185): not part of this task.
- An empty plot rendered by the real VizFactory: not run (S8c gives 0 rows only); the rendering in S9 was run for one plot.
- Her own turns for D-0194 to D-0197: not read; the quotes are those of the brief, and I only checked that the four numbers exist in the ledger.
- A scratch recode (S11-2) is the only change of a recipe, in memory in the script; `git status` shows no tracked file changed.

## Compliance with the decisions of the brief

| Decision | What the run shows against it |
|---|---|
| D-0197 "you need to do that as early as possible in the lineage" | S3: select at T1 (28 ids) removes the Norway samples from all 73 places; at T2 (21) the 7 stay at 66 places. It holds, and the cost of not doing it is 14 plots. S11-3: even at the earliest place (the metadata root) a property step does not reach 16 places across a left join; by ids it does. |
| D-0197 "if you apply the T1 then you will have 28, eg if you apply in T2 there will be 21 due to the other events in between" | S1: 28 at T1, 21 at T2 of `MLST_with_metadata`; the cause is the recipe step `modif_filter year between [2023, 2025]` (7 samples of 2022). A third count 27 at `ResFinder_with_metadata`; the metadata file has no T2. |
| D-0194 "I think that I would choose A as default" | S10, S11-3: "all ticked" by ids removes everywhere; "all ticked" by property with `na: keep` leaves the samples at 12 of 27 places with the column (and 16 downstream places for Norway). Not contradicted for ids, not met for property steps. No decision exists on `na` for these ticks: to report (D-0165). |
| D-0195 "ensure that the whole lineage is really searched and found (no silent failure I think)" | S6: dry run = built list at 73 of 73 places for 8 fields; my graph has 0 misses over 27 tables; but a search by name misses renamed copies (3 spellings) and `recipe_graph` is not built; a check by property is blind (misfit 3). A rule for renamed columns does not exist: to report (D-0165). |
| D-0196 "I do not see how it is possible for me to tick country = Norway at the MLST data file" | S7: confirmed. A property step at a node without the column is refused by the engine; at the MLST file it breaks 4 downstream builds. The only routes to a table without the column: "all tables" by ids and the forward effect. |
| D-0165 "Where no decision exists and one is needed, that must be reported to her." | Needed, no decision found: (1) `na` for a property step ticked at several places; (2) what the dialog does about renamed or derived copies of a column; (3) what the check after Apply reports for a table without the column (blind by property); (4) the intent question (relayed, 2026-11-16: three viewpoints); (5) a T3 reader in the engine (not built). |
