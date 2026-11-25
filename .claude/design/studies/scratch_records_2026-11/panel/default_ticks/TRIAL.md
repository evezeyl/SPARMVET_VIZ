# Trial: default ticks (A: earliest places only) against (B: all places ticked), "rows removed here: N"

Worktree `SPARMVET_VIZ_wt_ticks_trial`, branch `trial/default-ticks`. Nothing tracked was changed, nothing committed. Scripts and raw outputs: `trial/` (see `trial/README.md`), synthetic recipes: `synth/`.
Labels: **run** = verified by a run of the library (`utils.remove_from_all.describe/apply`, `app.modules.audit_run.run_audit`, the engine builds the tables); **reasoned** = not run.
Environment proof: `utils.remove_from_all`, `utils.lineage_walk`, `app.modules.audit_run` were imported from the worktree (printed paths, first command of the session).
Demo = `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, real data, 28 tables, 17 plots; `sample_id` is the declared key.

## Definitions used
- **A** = the places that start ticked AND are the tier 1 of a SOURCE table (data schema, additional dataset, metadata schema; graph `collection_kind == "schema"`). A join's own tier 1 is a later place. Demo: 11 of the 27 lines. (`common.earliest_places`)
- **B** = every line that starts ticked (`option.default_ticked`): 27 on the demo.
- "Every table" = tier 1 and tier 2 of each of the 28 tables plus the table of each of the 17 plots (73 frames), built by the engine after the audit; compared with `DataFrame.equals` (same rows, same order, same values).
- N, three definitions (all by run): **N_total(X)** = rows of the table X (tier 1) before the audit minus after it, with the whole ticked set; **N_local(X)** = rows removed by the step written AT X, given the other ticked steps (rows with the set minus X, minus rows with the set); **N_alone(X)** = rows removed if the step were written at X alone.

## Q1. A against B on the demo: identical?

**Yes, every frame identical (run).** Samples removed: one that is in all 27 tier 1 tables (`10668076`), two (`10668076`, `12244317`), the sample present in the fewest (`52676003`, 24 of 27), one with 25 tables, a mid one, and a set of 5 mixed ids.

| case (sample ids) | present in tables | steps A / B | frames A != B | frames still holding the sample (A or B) |
|---|---|---|---|---|
| 1 id (in 27) | 27 | 11 / 27 | 0 of 73 | 0 |
| 2 ids (in 27) | 27 | 11 / 27 | 0 of 73 | 0 |
| fewest | 24 | 11 / 27 | 0 of 73 | 0 |
| low | 25 | 11 / 27 | 0 of 73 | 0 |
| mid | 27 | 11 / 27 | 0 of 73 | 0 |
| 5 mixed ids | 24,25,27,27,27 | 11 / 27 | 0 of 73 | 0 |

Rows removed in total (sum over the 73 frames) are equal under A and B in every case (for example 849 for the 5 ids). The two tables that compute across samples (`QA_aggregated_no_key`, `QA_population_zscore`) are equal under A and B too: the sample leaves before the computation in both. Differences A against B: none, so there is nothing to explain on the demo. Scripts: `q1_equal.py`, `q1b_more_samples.py`.

## Q2. What "the earliest place of each branch" is, in the library's terms

**Rule used (run):** a line of `option.lines` that starts ticked and whose table is a source schema (`graph.node("T1:<table>").collection_kind == "schema"`), written at the END of that table's tier 1 (the library writes only there). Joins cannot read joins (the engine refuses it: "names 'Jx', which is not a data schema", run v13), so every join's inputs are source tables; each source is its own branch start.

Demo (run, `q0_places.py`): 11 places of 27. Sources (A): Summary, Summary_quality, Quality_metrics, Detailed_summary, FastP, Quast, Bracken, ResFinder, MLST, VirulenceFinder, metadata_schema. Joins (later, 16): FastP_with_metadata, Quast_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, MLST_with_metadata, QC_Reads_Anchor, Summary_phenotype_length_fragmentation, ST22_Anchor, AR1_MLST_Serotype_Virulence, QA_AMR_per_sample, QA_ST_with_NA, QA_year_types, QA_L50_integer, QA_fanout_exhibit, QA_aggregated_no_key, QA_population_zscore. `APEC_STEC_virulence_genes` has no sample column and is not a line. A = 11, B = 27.

Where the rule is ambiguous or does not give the right place (synthetic recipes, run):

| case | what the library does | what the rule A gives |
|---|---|---|
| a join's own tier 1 steps rewrite the key (`sample_id + "_x"`, v7g) | the join is a line, with note `values_unproved` under B | not ticked under A; sample gone anyway (sources ticked) |
| the key is created by a step from another column and the table is joined on it (v8h) | linked by the join pair: a line, ticked, source | ticked, works |
| the same, no join (v8h2) | `same_name_not_linked`, listed, UNTICKED (D-0498) | not ticked: the sample stays in that table (both A and B) |
| a source holds the sample under another column name, declared key there, joined with left_on/right_on (v9i2) | linked, a line, column `isolate_id` | ticked, works |
| the same, declared key under another name, no join (v9i) | NOT a line, NOT in `not_reached`, nothing said: **silent** | the sample stays in that table (both A and B) |
| the key renamed in tier 1 (`sid` to `sample_id`, v10j) | followed, the place column is `sample_id` | ticked, works |
| the key copied then the original dropped in the source (v1a2) | the copy is followed (`sid_copy` is the place column) | ticked, works |
| the key copied by an expression with upper-case and the original dropped in the source (v1a3) | the copy is followed, NO note, `may_stay` empty | the typed `s3` does not match `S3`: **sample stays in S1 and J1 silently** (A and B); N_alone = 0 at S1 |
| the key dropped in the join after the join (v1a1) | `key_gone_at_tier1`, in `may_stay`, nothing written | sample is gone (sources ticked): the alarm is false |
| the sample enters a later table from a table that is not a place (v14: join recomputes `sample_id` from `isolate` of an undeclared source) | join is a line (note `recomputed_here`, in `may_stay`) | **A does not remove it in the join; B does** (see Q7) |
| the key only in the RIGHT table of a left join, the left source holds it under another name (v11k) | MAP is a line, S1 is not mentioned at all | the sample's row stays in S1 and in the join with empty key (see Q3) |
| two schemas read the same file (demo Summary and Summary_quality) | two lines, both ticked | both ticked, works |
| a second schema reads the same data but does not declare the key (v6f) | `same_name_not_linked`, listed, unticked | the sample stays there (both A and B) |

## Q3. The left-join case

**Demo, run (`q3_leftjoin_demo.py`):** the sample removed only at the right table of a left join: **the left row stays in the join with empty columns.**

| ticked | table | rows with the sample after | columns empty for those rows |
|---|---|---|---|
| only metadata_schema | FastP_with_metadata (FastP left join metadata) | 1 | source, year, country |
| only metadata_schema | QC_Reads_Anchor | 1 | source, year, country |
| only ResFinder | QA_AMR_per_sample (metadata left join ResFinder) | 1 | gene, predicted_phenotype |
| only Quast | QC_Reads_Anchor | 1 | n50, total_length, largest_contig, L50 |

With only the left table ticked (FastP) the row leaves the join. With A (all 11 sources) or B the sample is in 0 of 27 tables: **under A the case disappears on the demo** (also when each of two ticked sources is the right side of a left join). The tables that still hold the sample under "only metadata_schema" are 20 of 27, under "only ResFinder" 25 of 27.

When it remains under A (run, synthetic):
- **The left source is not a place.** v11k: S1 holds `isolate`, MAP maps `isolate` to `sample_id` (declared key), J1 = S1 left join MAP. Under A (MAP) and B (MAP, J1): the sample's row stays in S1 and in J1 with `sample_id` empty; `may_stay` is empty, `not_reached` is empty: **silent**. N_total at J1 = 0 (rows before 6, after 6) while J1 held the sample's row before. Ticking only J1 removes the row in J1 but leaves it in MAP and S1. With an inner join (or MAP as the left table) the row leaves the join; S1 (not a place) still holds it.
- **The right source has no key at all** (v12: reference table REF without key as the left table, the long sample table on the right): the sample's rows leave, no sample value remains, the REF rows stay with empty columns. That is the nature of a left join, no step can change it (run: `still hold values: none`).
- A source that is a reached place but unticked by the user: as the demo rows above.

## Q4. "Rows removed here: N"

Demo, run (`q4_n.py`, samples one and two; the table of 27 lines is in `trial/out/q4_n.txt`).

| place | N_total A | N_local A | N_alone | N_total B | N_local B |
|---|---|---|---|---|---|
| the 11 sources (e.g. Summary 26, VirulenceFinder 23, metadata_schema 1) | = N_alone | = N_alone | rows with the sample (1 to 26) | same | same |
| the 16 joins (e.g. ST22_Anchor 7, QA_fanout_exhibit 23, Quast_with_metadata 3) | shown as a fact, the same numbers as B (not written) | not written | = rows with the sample (1 to 23) | = N_total A | **0 at all 16 (two samples: also 0 at all 16)** |

- **Under B, N_local is 0 at every later place (16 of 16)**: the earlier ticked sources already removed the rows. "N = 0 means the wrong place" would fire on 16 of 27 lines, all false alarms, in both cases.
- Under A there is no step at a join, so no N there; N_total at a join is a plain fact and equals what B shows.
- N_alone is the same for A and B (a function of the table). It is the number of rows that hold the sample in that table.
- **How N can be true:** N_local at a later place is 0 whether the place is clean (demo, 16 of 16) or not (v11k: N_local at J1 under B = 0 and the sample's row stays). N_total (rows before minus after in that table) is 0 at J1 in v11k and positive in the clean demo, so it tells the two apart; but N_total = 0 also when the sample is legitimately absent. The pair "rows that hold the sample before / rows removed" is true in all cases run; "removed" alone is not (run, `q4c_n_total_right_key.py`).
- **The signal only makes sense at a place that is the earliest on its branch** and only if the sample is expected in that table. It is also 0 when the typed value does not match what the place holds (lowercase, rewritten copy: S1 N_alone = 0, run v2b, v1a3).

## Q5. The silent cases (synthetic recipes in `synth/`, run)

A = sources ticked, B = all ticked, "stays" = still holds after the audit in some table.

| case | earliest only enough? | sample stays | what the library said | N at the place |
|---|---|---|---|---|
| (a1) key copied, original dropped in the join | yes | none | J1 `key_gone_at_tier1` in `may_stay` (false alarm) | sources N=1 |
| (a2) copy then drop in the source | yes (the copy is followed) | none | nothing | N=1 |
| (a3) copy by upper-case expression, original dropped | **no** | S1 and J1 (A and B) | nothing | S1 N=0 and J1 N=0 |
| (b) lowercased in S1, typed as in the file `S3` | **no** | S1, J1 (A and B) | `values_unproved` S1, S2 (A), + J1 (B) | S1 N=0 (catches it), S2 N=1 |
| (b) typed `s3` | **no** | S2 (A and B) | the same alarms | S2 N=0 (catches it) |
| (c) key Int64 in one table, String in the other | the apply is refused for the whole choice | nothing written | refusal text names the table and type | n/a |
| (d) z-score in the join tier 1 | yes for A and B | none; others' z equal under A and B | nothing | N=1 |
| (d) user ticks only the join | n/a | s3 stays in S1 and S2; **others' z differ from A** (e.g. s1: -1.254 under A, -1.336 join only) | nothing | N=1 at J1, the same as A |
| (e) anti / full / semi join | yes | none (A, B); with only S1 or only S2 ticked the sample stays in the join and the other source | anti and full: `uncertain_link`, in `may_stay`, nothing written (false alarms under A) | sources N=1 |
| (f) same data read twice, second without the declared key | no | the second table (A and B) | listed `same_name_not_linked` (not in `may_stay`) | n/a |
| (f) demo Summary and Summary_quality | yes | none | `may_stay` 3 of the 6 | N=26 and 1 |
| (k) key only in the right table of a left join | **no** | S1 and J1, row with empty key | nothing | MAP N=1, J1 N_local=0 |
| (v14) join recomputes the key from a non-place column | **no** | J1 (1 row) under A; none under B | `recomputed_here`, J1 in `may_stay` (option level); under A no alarm because J1 is not written | J1 N_alone=2, N_local under B =1 |
| (i) key declared under another name, no join | **no** | that table (A and B) | nothing, not even listed | n/a |

Does N = 0 catch the lowercased key? Yes at the place that holds the lowercase (S1, typed `S3`) and at the place that holds the other case (S2, typed `s3`). Does it MISS? Run: (1) N = 0 at a right place because the sample is not in that table: sample `52676003` is absent from Detailed_summary and ResFinder (and ResFinder_with_metadata under B): N = 0 at 2 sources under A, 3 lines under B. (2) N > 0 although the sample's row stays elsewhere: v11k, MAP N = 1, rows stay in S1 and J1. (3) a table the library does not list at all (v9i, v1a3's S1 under B has N = 0): no N exists to read.

## Q6. Facts for the user, demo

| | A | B |
|---|---|---|
| lines in the dialog | 27 | 27 |
| ticked | 11 | 27 |
| steps written | 11 | 27 |
| `option.may_stay` (before apply) | 6 | 6 |
| notes on lines (`unread_step_passed` 16, `one_row_per_group_after_this_step` 3) | 19 notes on 6 lines (the same 6) | the same |
| `apply`: `may_differ` (written, values may differ) | 3 (Summary, Summary_quality, Detailed_summary: the ticked ones of the 6) | 6 |
| `apply`: `not_written` | 0 | 0 |
| `apply`: `stays_by_choice` | 16 (all the joins, unticked) | 0 |
| `not_reached` / `unsure` | 0 / 0 | 0 / 0 |
| tables that still hold the sample after (T1, T2, plots) | 0 | 0 |
| true alarms among the `may_differ` | **0 of 3** | **0 of 6** |
| true among the 16 `stays_by_choice` | **0 of 16** | n/a |

Confirmed on the demo: the 6 "may stay" are all false alarms in the run for the samples tried (one id, two ids, fewest, 5 mixed): the sample is gone in all six, tier 1, tier 2 and the plots. In the synthetic variants the alarms were true in some cases ((b): S1 and J1 held the sample, 2 of the 3 alarms under B, 1 of the 2 under A) and false in others (a1: J1; (e): Janti, Jfull; g: J1).

## Q7. Does a result differ between A and B in a way "rows removed here" cannot show?

- **Demo: no.** 0 of 73 frames differ in all 6 cases.
- **Synthetic, one case where A is not enough and B is (v14):** a join recomputes the key from a column of an undeclared table (not a place). A leaves 1 row holding the sample in J1 (and its plot); B removes it (N_local at J1 under B = 1, N_alone = 2). Under A the join is unticked, so no number and, because the join is not written, no alarm is produced for it (`stays_by_choice` = 1, shown as the user's choice). The result differs and "rows removed here" under A cannot show it.
- **A tick set the user changes by hand changes results beyond N** (d, v4f): ticking only the join removes the sample from the join with the same N as A (1) but the z-scores of the other samples differ from A (s1: -1.336 against -1.254, 5 rows each); S1 and S2 still hold the sample. Not a difference between A and B but between A or B and a hand-made choice; N is equal.
- In all other synthetic cases A and B are identical (v0, a1, a2, b, c, d, e, f, g, h, i, j, k, 12).

## What the trial cannot see
- Only the demo and 16 small synthetic recipes. No second real recipe. The demo's key is clean (same spelling in all tables, type String everywhere, no table with the sample under another name), so it cannot show the silent cases; they exist only in the synthetic recipes I wrote.
- The library follows a copy of the key without a note (v1a3), so "the library said nothing" depends on the walk as built on this branch.
- N is computed at tier 1 only (the step is written there). Tier 2 and the plots were compared for equality, not counted.
- Tables that a user reads that are not in the recipe (a source FILE no table declares) are invisible to this logic and to the trial.
- No browser, no dialog: what a user sees was not tested; only the numbers the library and the engine give. The words of any note were not looked at.
- Timing: the audit run is the cost (the 130 runs of `q4_n.py` took about 7 minutes); not measured otherwise.
- Samples tried on the demo are 33 ids present in all 27 tables and 9 present in 24 to 26; the others were not tried one by one.
