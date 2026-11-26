# AUDIT-MODEL-SCENARIOS-1, round 2: the lineage of a COLUMN, its type, and the 2002.5 case (recipe 1, real engine, read-only)

Branch `feat/recipe-format-1`, HEAD `46fa84da`. No tracked file changed. Scripts: `tmpAI/panel/audit_model/trace.py` (step-by-step trace of every table), `r2_s12.py`, `r2_s13.py`, `r2_s13b.py`, `r2_s13c.py`, `r2_s14.py`, `r2_s15.py`, `r2_s16.py`, `r2_l50.py`; outputs in `out/r2_*.md`. Re-run: `source tmpAI/panel/audit_model/env.sh; ./.venv/bin/python tmpAI/panel/audit_model/r2_s15.py`.
Her words and the decisions of the day are quoted as "relayed, 2026-11-16" (messages M190, M191, M192 of `tmpAI/agent_channel.md`; not ledger lines yet; I ignored the clock times of their headers). Relayed as decided: at each ticked place the value is written in the type of THAT place's column, only lossless conversions (2022 to "2022" yes; 2022.5 to a whole number refused with a plain message), and the dialog warns when values do not correspond one to one between places.
Labels: RUN = I ran it with the real engine or the real functions; READ = read in code at file:line.

## 0. What does not fit her idea (read these first)

1. **Nothing in the code follows ONE column through a rename or through a built column.** The three things that exist read NAMES: the dialog (`app/modules/t3_audit_engine.py:125-128` `column_types`: name and type from `collect_schema()` of the one table in view); Blueprint's navigator (`resolve_fields_for_schema`, `data_analysis_recipe_navigator.py:520`: the DECLARED fields, backwards only); my scratch graph (S6). RUN: the navigator's field list equals the really built columns for only 10 of 28 tables (18 differ: `MLST` declares 10 columns and has 3; `ST22_Anchor` declares 26 and has 11; `Summary` declares 0 and has 4). No function gives the forward lineage or "this column here is that column there". (S12)
2. **Her example "T1 numbers, T2 text" appears in recipe 1 as two columns with two names, not as one column that changes type.** `year` is Float64 at every one of the 20 table stages that hold it (27 places with the plots) and no step casts it. The text version is a NEW column `year_label`, built from `year` by an expression (`pl.col('year').cast(pl.Int64).cast(pl.String)`), at QA_year_types and QA_aggregated_no_key. A schema search at each place does not link `year` to `year_label`. The only real type change of a kept column in recipe 1: `L50` Float64 at Quast, Int64 at QA_L50_integer (a cast; lossless, all values whole; `L50 >= 8.5` gives the same 23 samples at both places, RUN). (S13, S14)
3. **The same three virulence names are one lineage that a name search cuts into three.** `virulence_raw` (text, split) becomes `VF_gene` (VirulenceFinder T1:7, rename of `field_0`), which is `VF_gene` at the anchor T1:4, renamed `Selected_Virulence_Genes` (T1:6), and `selected_virulence_genes` at AR1 (T1:4, with a lower-case rename of the same column). A search for one spelling finds 3 or 4 places; the other places on the same lineage are silent misses (D-0195). (S13; RUN)
4. **The same NAME can be two different columns.** `phenotype` at Summary_quality (free text of the pipeline summary, e.g. "ampicillin, unknown[sitABCD_1_AY598030]") and `phenotype` at ST22_Anchor (the renamed `predicted_phenotype` of ResFinder): one value in common. `value` is text at Summary and decimal at Quast_with_metadata. A search over the whole recipe by name would list both as one field. (S16; RUN)
5. **Her 2002.5 case: the engine does not allow the lossy cast she describes.** `polars_cast` Float64 to Int64 on 2002.5 is REFUSED: "column 'Year' holds values with decimals ([2002.5, 2002.5]); casting to Int64 would drop them silently" (`libs/transformer/src/transformer/actions/polars_calls.py:365`). The many-to-one exists only when the recipe writes a visible step first (`floor` or `round`). With that step, the condition `Year = 2002` selects 2 rows at T1 (b, f) and 4 rows at T2 (b, c, d, f). (S15; RUN)
6. **With a lossy step in between, "the earliest place covers the later ones" fails, and the second step is NOT redundant.** `Year != 2002` written only at T1 leaves the rows c and d (2002.5); they read 2002 at T2, and the same condition evaluated again at T2 finds 2 rows. Written at T1 and at T2, the second step removes c and d. (S15; RUN; M187's caution 2, now with numbers on a lossy cast)
7. **Today's readers do not do what was decided for the typed value.** (a) A decimal for a whole-number column: the dialog reader returns 2002.5, the condition selects 0 rows and says nothing; the strict reader of the recipe action ACCEPTS 2002.5 for an Int64 column. The refusal "2022.5 to an integer is refused with a plain message" does not exist. (b) A number for a text column: the dialog reader keeps the number and Polars raises a comparison error; the strict reader refuses it. 2022 to "2022" is not done. (c) A text "2002" for a whole-number column is converted by the dialog reader (text to number works; number to text does not). `utils/filter_values.py:154-175`, RUN (S15)
8. **The value of a column changes at places other than casts.** MLST T1:3 `polars_fill_null` turns the missing sequence types into the text "Non Determined": a selection "missing" at the file and "Non Determined" at the end of T1 are the same rows under two values. VirulenceFinder T1:9 `polars_str_strip_chars` changes `VF_protein` (at least 4 values, e.g. 'Adherence protein', are new after the trim). `QA_population_zscore` T2 and `ST22_Anchor` T2 add values computed from other rows (S4 of round 1). (S13; RUN)
9. **Unpivot and aggregation break the meaning of a column without removing its name.** Quast (n50, total_length, largest_contig as columns) becomes `metric` + `value` at Quast_with_metadata. `value >= 324189` selects 104 rows / 42 samples; the n50 only (`metric = n50 and value >= 324189`) selects 21 rows / 21 samples, the same 21 as `n50 >= 324189` at the Quast file. The columns `n50`, `L50` are gone at that place; `year` also (the unpivot lists `index: [sample_id, source, country]`). (S16; RUN)

What fits her idea is in each scenario below.

## S12. How the places that have the field are found today

READ and RUN (`out/r2_s12.md`).
- By column NAME only. Every function reads names from a schema or a declaration:
  - `t3_audit_engine.column_types(lf)` (`:125`): `collect_schema()` of the one table in view: name and type. `audited_frame` (`:654-674`) reads `lf.collect_schema().names()` and raises `AuditStepError` when the step's column is not there (no silent skip). `_apply_filter_rows` (`:541-556`) SKIPS a filter whose column is not in the view (issue #56, exploration), and `except Exception: actual_dtypes = {}` swallows a failed schema read: a silent skip path, not the audit path.
  - Blueprint: `resolve_fields_for_schema` (declared `input_fields`/`output_fields`, unions of ingredients), `build_plot_lineage` (backward from a plot to its roots; RUN for `mlst_bar`: MLST, metadata_schema, `MLST_with_metadata`, the plot). No forward function. The declared lists are wrong for 18 of 28 tables (misfit 1).
  - `libs/utils`: no graph. `grep recipe_graph` finds only the design text; P3 is not built (`home_stage2_mechanism_spec.md:106,146`). `recipe_check.py` reads declared fields for J08 (`:722-731`).
- From the schema at each place (`collect_schema()` after each step): possible and cheap. RUN: the 56 stored table stages of recipe 1 were built once in 1.7 s; reading the schema (name and type of every column) of all 56 took 3 ms in total (no data read). Step by step (a prefix of the steps, `collect_schema` after each) works with `DataWrangler().run(lf, steps[:k])` and `DataAssembler(...).assemble(steps[:k])` (my `trace.py`): 79 recipe steps, all traced.
- What each can see: the schema at each place gives names and types exactly; it cannot say that `VF_gene` here is `Selected_Virulence_Genes` there, or that `year_label` is built from `year`. That is information that only the steps carry.
**Does her idea fit?** The idea (one column along the chain, shown differently per tier) needs more than the code has: the types per place, yes; the identity across a rename or a built column, no.

## S13. Each column of the main chains, step by step (real engine)

RUN (`out/r2_s13_raw.md`, `out/r2_s13_fields.md`, `out/r2_s13_values.md`: every step of the 28 tables that adds, removes or retypes a column).

| field | where it appears | NAME change | TYPE change | VALUES change | disappears |
|---|---|---|---|---|---|
| `country` | file `metadata_schema`: String. Added by join T1:1 in FastP_, Quast_, Bracken_, ResFinder_, MLST_with_metadata and AR1; T1:3 in QC_Reads_Anchor (`polars_join`) | none in 28 tables | none (String everywhere) | none (0 events) | QA_fanout_exhibit T2:1 (`polars_group_by` by sample_id) |
| `year` | file `metadata_schema`: Float64. Added by the same joins | none | none (Float64 at every place) | none by a step on `year` itself; `era` (MLST T2:1) and `year_label` (QA_year_types T1:1, QA_aggregated T1:1) are built from it; MLST T2:2 `modif_filter` keeps 2023 to 2025 | Quast_with_metadata T1:2 (`polars_unpivot`); QA_AMR T2:1 and QA_aggregated T2:1 (`group_by`); QA_fanout T1:3 and QA_population T1:2 (`polars_select`) |
| `virulence_raw` | file VirulenceFinder: String | none | T1:2 String to List(String) (`with_columns`), T1:3 back to String (`explode`) | split into two columns at T1:5-7 (`str_splitn`, `unnest`) | T1:8 `polars_drop` |
| `VF_gene` | VirulenceFinder T1:7 (rename of `field_0`); joined into ST22_Anchor T1:4, AR1 T1:2, QA_fanout T1:2 | renamed `Selected_Virulence_Genes` (ST22_Anchor T1:6) and `selected_virulence_genes` (AR1 T1:4) | none (String) | `VF_protein` is trimmed at VirulenceFinder T1:9 (`str_strip_chars`); the gene itself not | QA_fanout T2:1 (`group_by`); the old name is gone after each rename |
| `Selected_Virulence_Genes` | ST22_Anchor T1:6 | (this is the rename) | none | none | kept to the plots `virulence_bar`, `virulence_variants` |
| `selected_virulence_genes` | AR1 T1:4 | (this is the rename, lower case) | none | none | kept |
| `sequence_type` (value example) | file MLST | none | none | T1:2 (`replace_strict` 'unknown'), T1:3 `fill_null`: missing becomes "Non Determined" | none |

Which changes can be read from the recipe alone and which only by running (79 recipe steps at T1 and T2 of the 28 tables; RUN count of the actions in `out/r2_s13_values.md`):
- Readable from the action and its arguments (names and what happens): `polars_rename` 5 (the mapping), `polars_cast` 3 (columns and dtype; whether it is lossless needs the data, the engine refuses a lossy one), `polars_select` 10 and `polars_drop` 2 (the names kept or dropped), `polars_fill_null` 1 (the value), `modif_filter` 5, `polars_str_strip_chars` 3 (the columns; the effect on values only by running), `polars_unique` 2, `polars_sort` 2, `polars_explode` 2 (the column; its type only by running): 35 steps. `polars_unpivot` 3 and `polars_group_by` 4: the new names and the kept names are in the arguments (`index`, `on`, `variable_name`, `value_name`, `by`, the keys of `named_aggs`); the type of the new column (Float64, String, UInt32) only by running: 7 steps. Total names readable without running: 42 of 79.
- Only by running (or a dry run on empty files): `polars_join` 21 (the added columns are those of the right table, and a name that both sides have becomes `_right`: `ST_right` appeared inside `Summary_phenotype_length_fragmentation` T1:4 and was dropped at T1:5; this is not in the recipe), `polars_unnest` 2 and `polars_str_splitn` 2 (the new names `field_0`, `field_1` are the engine's own; the rename after them names them): 25 steps.
- Name readable but not the meaning: `polars_with_columns` 12 (the key of `named_exprs` is the new column; what it is built from is inside a text of Polars code: `length_ratio` from `hsp_len` and `total_len`, `era` from `year`, `year_label` from `year`, `n50_zscore` from `n50` over all rows, `virulence_count` from rows per sample).
**Fits?** For `country` and `year`: yes, one column runs unchanged from the file through the joins to the plots, and the type is the same everywhere; the lineage of the column is the lineage of the tables. For the virulence names: only with the renames (readable from the recipe); a search by name does not find them. For `year` to text: it is a different column.

## S14. What the engine can give per place for the dialog

RUN (`out/r2_s14.md`). Per place: the name and the type of each column (`column_types`, 3 ms for 56 stages), the dialog line (`column_type_line`: "year holds decimal numbers (Float64)."), and the values as the dialog lists them (`value_choices`).
- `year`: Float64 at all 20 table stages (the 7 plots read the same tables): values listed as 2022.0, 2023.0, 2024.0 (numbers; at `MLST_with_metadata` T2 only 2023.0 and 2024.0). `year_label`: String at QA_year_types T1/T2 and QA_aggregated_no_key T1/T2: "2022", "2023", "2024" (text).
- Column names that have more than one type across the places of recipe 1: only `value` (Float64 and String: two different columns) and `L50` (Float64 and Int64: one column cast). `country`: String everywhere; `sample_id`: String everywhere.
- The dialog function can show "at T2 this column is text, written as '2022'" only when the same name has another type at another place; recipe 1 has that for `L50` only (shown as 9.0 or 9: `L50 >= 9` gives the same 23 samples at both).
**Fits?** Yes for names and types per place (cheap and exact). The "number at T1, text at T2" display exists only if a recipe casts the same column; recipe 1 has no such case but `L50`.

## S15. Her 2002.5 case, exactly (small table; RUN, `out/r2_s15.md`)

T1: `Year` Float64 = 2001.0, 2002.0, 2002.5, 2002.5, 2003.0, 2002.0 (ids a to f).
- The recipe cast alone is refused (misfit 5). With a visible step first (`pl.col('Year').floor()`, then `polars_cast` to Int64): T2 `Year` = 2001, 2002, 2002, 2002, 2003, 2002 (Int64). Distinct values: T1 {2001.0, 2002.0, 2002.5, 2003.0} (4), T2 {2001, 2002, 2003} (3).
- Her question 1, will 2002.5 and 2002 be seen as the same: **no, not at T1; yes at T2.** The condition `Year = 2002` is true for b and f at T1 (2002.0; 2002.5 is another value) and for b, c, d, f at T2.
- A typed value 2002 written per place: at T1 it is read as 2002.0 (Float64), at T2 as 2002 (Int64). The condition is then evaluated on each place's own data, and it needs no tracing of rows (RUN: both selections made from the table at that place only).
- Writing `Year != 2002`: at T1 only: T1 keeps a, c, d, e; T2 keeps a, c, d, e with c and d reading 2002 (still there). At T2 only: T2 keeps a, e; T1 unchanged (6 rows). At T1 and T2: T2 keeps a, e. The T1-only step does not cover T2.
- Which conversions lose nothing (round trip, RUN): 2022 to text "2022" yes; 2022.0 to a whole number 2022 yes; 2022 to decimal 2022.0 yes; text "2022" to decimal yes; "2022.0" to a whole number yes; 2022.5 to a whole number NO.
- How to detect "two values at T1 become one at T2", three ways (RUN):
  1. From the distinct values at both places: 4 at T1, 3 at T2, same rows: one value merged. No row tracing. Exact only if no row was removed in between (a filter lowers the count too). Cost on 2,000,000 rows with 500,000 distinct values: 152 ms for one place, 244 ms for both.
  2. From the T1 distinct values and the step (the `cast` and its `floor`/`round` are readable from the recipe): apply the step to the distinct values and group: {2002: [2002.0, 2002.5]}. No row tracing; exact; needs the step to be readable (a `with_columns` expression is code in a text: readable only if it is a cast, a floor or a round that the app knows).
  3. From the data of both places and a unique key (`id`): join T1 and T2 on the key: {2002: [2002.0, 2002.5]}. Exact for any step, even a recode; needs a column that identifies a row at both places (not every table has one: QA_aggregated_no_key T2 has none). Cost 206 ms on 2,000,000 rows.
- Her question 2, does it need to find out from which row the value originated: **for a condition step, no** (each place evaluates the condition on its own data). **For the warning, no row-by-row lineage either**: counts at the two places (way 1), or the readable step (way 2), or a key join (way 3). Row-by-row tracing (which T1 row became which T2 row) is not needed and nothing in the code does it.
- The reverse, one value that becomes two (RUN): a recipe step recodes `country` 'UK' by `region`: T1 'UK' (a, b, c), T2 'Scotland' (a), 'England' (b, c). `country = UK` selects a, b, c at T1 and nothing at T2; `country = England` selects b, c at T2 and nothing at T1. From the distinct sets: only at T1 {UK}; only at T2 {England, Scotland}; which becomes which is not in the sets; the key join says UK to {England, Scotland} (and FR to FR).
**Fits?** Her model (each place evaluated on its own data, the dialog warns, no row tracing) holds. It does not fit "the earliest place covers": misfit 6.

## S16. Cases where the identity of a column is not clear (RUN, `out/r2_s16.md`)

- **Built from two columns:** `length_ratio` at Detailed_summary T1:5 is `hsp_len / total_len`, both then dropped (T1:9); `resistance_points` and `phenotype_count` at Summary_phenotype_length_fragmentation come from `value` through a `when/then` and a `sum`. The engine gives the new name and type; the origin is a code text.
- **Unpivot:** Quast_with_metadata T1:2: `metric` + `value` replace `n50`, `total_length`, `largest_contig` (misfit 9). `year` and `L50` are not in the new table.
- **Aggregation:** QA_AMR_per_sample T2:1 `group_by [sample_id, country]` keeps those two and adds `n_amr_genes`; `gene`, `predicted_phenotype`, `source`, `year` go. QA_aggregated_no_key T2 has `country`, `year_label`, `n_samples`: no `sample_id`.
- **Same name, different column:** `phenotype`, `value` (misfit 4). **A name added by the engine:** `ST_right`.
- **A derived value computed over all rows:** `n50_zscore` (QA_population_zscore T2), `virulence_count` (ST22_Anchor T2), `total_gene_count` (ResFinder T2).
What could be said to the user there, as information and without a guess (each sentence is something the run supports; not a design):
  - "This column is not in this table: it was removed at step 2 (unpivot)." (`year` at Quast_with_metadata.)
  - "In this table `value` holds the measures n50, total_length and largest_contig together (column `metric` tells which); the Quast file holds them as separate columns."
  - "`n50_zscore` is computed from all samples that reach this step; a removal made before this step changes it; after it, it does not."
  - "Another table has a column with the same name (`phenotype`) that is not the same data."
  - "This column was renamed here from `VF_gene`." (from the rename mapping).
The app cannot say, without running or without parsing a code text, where a column built by a `with_columns` expression comes from.

## Which scenarios fit her idea (one line each)

| S | Her idea predicts | The run gives | Fits? |
|---|---|---|---|
| S12 | one lineage of the column; the places found from the schema | names and types per place are exact and cheap (3 ms); no identity across rename or build; declared lists wrong for 18 of 28 tables | Partly: the schema is enough for places that keep their name; not for renamed or built columns |
| S13 | the same column runs along the chain, only the presentation differs | `country`, `year` run unchanged; the virulence column changes name twice; `year` to text is a new column | Yes for `country` and `year`; no for renamed or built columns |
| S14 | the dialog can show the name and type per place | exact per place; `year` is Float64 at all places; no text version of the same column | Yes |
| S15 | each place evaluates its own data; no row tracing; a warning on merged values | confirmed; T1-only does not cover T2; the cast refuses decimals; the readers do not yet refuse 2002.5 for a whole-number column | Yes for the model; not for the rule "the earliest covers" |
| S16 | (not stated) | unpivot, aggregation, built-from-two and same-name cases exist in recipe 1 | Open: needs information text, no guess |

## What I did not run or check

- The audit dialog and the per-place typed value do not exist: all numbers come from the engine and the readers as they are today. The decided B4 (a) and the one-to-one warning are relayed, not built.
- Other recipes (2_test, figshare, stress_test_master); a recipe with a `pivot` (columns that depend on values); a data cast of dates or categories.
- The lossless-conversion table is my own round-trip test, not an existing function (no such function exists in `libs/utils`).
- A real browser view of "number at T1, text at T2": recipe 1 has none; I made the small table.
- Timings are on this machine, one run each (2,000,000 rows, one column): 152 ms, 244 ms, 206 ms.

## Compliance with the decisions of the brief

| Decision | What the run shows |
|---|---|
| D-0195 "ensure that the whole lineage is really searched and found (no silent failure I think)" | A search by name or by schema finds the same-name places and misses the same column under another name (`VF_gene`, `Selected_Virulence_Genes`, `selected_virulence_genes`; `year` to `year_label`): silent misses (misfits 2 and 3). The same name for two columns (`phenotype`, `value`) is a false hit on a whole-recipe search (misfit 4). `_apply_filter_rows` skips a missing column silently in exploration (issue #56) and swallows a failed schema read. The audit path `audited_frame` raises instead of skipping. The schema per place itself is exact. |
| D-0197 "you need to do that as early as possible in the lineage" | With a lossy step between, the earliest place leaves rows that the later place shows as the selected value (T1-only `Year != 2002` leaves c and d; they read 2002 at T2): earliest is not enough there (S15). Without such a step it holds (round 1, S11-1). |
| D-0165 "Where no decision exists and one is needed, that must be reported to her." | Needed and without a decision: (1) what the dialog says for a column that is renamed or built from another (the information sentences of S16 are supported by the run, none is decided); (2) how "two values become one" is detected (distinct counts, the readable step, or a key join; the key join needs a key); (3) what the readers do with a decimal for a whole-number column (today: accepts or selects nothing; relayed decision: refuse); (4) what the dialog does for a number written for a text column (today: Polars error); (5) the same-name-different-column case on a whole-recipe search; (6) the cast guard today refuses lossy casts, so a many-to-one needs a visible step: whether the dialog's warning must also cover that step is not decided. |
