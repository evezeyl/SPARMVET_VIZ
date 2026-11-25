# Retest with the scope of her model (demo recipe, entity 10668076, column sample_id)

Labels: every number below was run (verified) unless it says "read" or "reasoned". Read-only: no tracked file changed.

## 0. Setup (proof)
- Code: worktree `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ_wt_good_practice`, `git log --oneline -1` = `873cae14` (docs commit on top of the merged build), `git status --short` = empty before and after every run. `app.__file__` and `utils.__file__` both resolve inside that worktree (printed at the top of `run_all_raw.txt`). Python: the main tree's `.venv/bin/python` (not touched otherwise). Load at start 5-6 (below 10).
- Method: the app's own functions. Places are written with `utils.remove_from_all.apply(..., ticked=[...])` (it calls `audit_copy.add_step` at the end of tier 1 of each ticked place, `not_in [10668076]`, `na: keep`), the audit copy is run with `app.modules.audit_run.run_audit`, each plot's own table is read with `DataOrchestrator.materialize_tier3` (same read as the library test `app/tests/test_remove_from_all_demo.py`). "Entity in a plot" = a row of the plot's table where any text column equals 10668076. "Changed" = the plot's table is not equal to the table of the unchanged audit copy.
- The option offers 27 places (every table except `APEC_STEC_virulence_genes`, which has no sample column); all places below are among them.
- Baseline (no step): the entity is in 16 of 17 plots (not in `qa_aggregated_no_key`, which groups it away: it holds no key column).
- Scripts and outputs: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ_wt_goals_sonnet/tmpAI/retest/` : `map.py` (the map), `retest.py` (the runs), `env.sh`, `run_all.txt` (summary), `run_all_raw.txt`, `run_E.txt`, `out/results.json`.

## 1. Numbers first
| Run | Places written | Plots changed (of 17) | Entity gone from | Entity stays in | Stays with columns emptied |
|---|---|---|---|---|---|
| A (her model, all analyses) | 17 | 15 | 14 | 2: `amr_heatmap`, `qa_l50_integer` | none |
| A3 (A + `T1:ResFinder` + `T1:QA_L50_integer`) | 19 | 17 | 16 | 0 | none |
| B (A minus the places of the quality analyses) | 15 | 12 | 11 | 5: the 3 quality plots + `amr_heatmap`, `qa_l50_integer` | none |
| B3 (B + `T1:ResFinder` + `T1:QA_L50_integer`) | 17 | 14 | 13 | 3: `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou` | none; their tables are byte-identical to the baseline |
| C (one history: `T1:MLST_with_metadata`) | 1 | 2 | 2: `mlst_bar`, `year_distribution` | 14 | none |
| D (the earlier scope: `T1:MLST` + `T1:metadata_schema`) | 2 | 13 | 9 | 7 | 3 plots (see run D) |
| E (first T1 of every original except the metadata) | 10 | 14 | 11 | 5 | `qa_population_zscore`: `n50`, `n50_zscore` |
| A2 (A + `T1:ResFinder` + `T1:Quast`) | 19 | 17 | 16 | 0 | none |
| B2 (B + `T1:ResFinder` + `T1:Quast`) | 17 | 17 | 15 | 1: `qc_reads_horizontal_barplot` | `n50`, `total_length`, `largest_contig`, `L50` |
| S6 (library test: 27 minus six unticked) | 21 | 14 | 13 | 3 (same three) | none |

Run D reproduces the earlier result on today's code (13 of 17 changed, entity stays in 7, in 3 of them with source/year/country emptied).
Plots that hold no key column: `qa_aggregated_no_key` (every run).
In every run, for each plot the entity is gone from, the table equals "baseline without the entity's rows" (nothing else changed), EXCEPT `qa_population_zscore` (see section 2, z-score) and `qa_aggregated_no_key` (the count of Norway 2024 goes 19 to 18 when the entity is removed before tier 2: verified in `out/A/QA_aggregated_no_key__T2.parquet`; the plot shows no key, so nothing in it names the entity).
Z-score: every place at `T1:QA_population_zscore` is written BEFORE tier 2, where the z-score over all samples is computed. Under runs A and B: baseline 42 rows, run 41 rows; the `n50_zscore` of the other 41 entities: 41 of 41 differ, largest absolute difference 0.064.

## 2. The map of the demo as her model sees it
Three blocks: `data_schemas` (9 tables), `additional_datasets_schemas` (2), `metadata_schema` (1) = 12 original tables; 17 joined or derived tables; 17 plots. (read from the recipe and `utils.recipe_graph`; run `map.py`.)

All join steps are `how: left` on `sample_id`, except the join with `APEC_STEC_virulence_genes` (`inner`, no `on` written: a gene join, no sample column). The first ingredient is the base (left) table. Metadata is the right table in 7 joined tables, the BASE (left) table in 4, and the only ingredient in 2.

| Original table | Joined tables that join it with the metadata (place `T1:<table>`) and the metadata's side | Plots under each | Reaches a plot WITHOUT meeting the metadata |
|---|---|---|---|
| `FastP` | `FastP_with_metadata` (FastP base, metadata right); `QC_Reads_Anchor` (FastP base, then Quast, Bracken, metadata, last, right); `ST22_Anchor` (metadata BASE, FastP right) | none; `qc_reads_horizontal_barplot`; `virulence_bar`, `virulence_variants` | no |
| `Quast` | `Quast_with_metadata` (Quast base, metadata right); `QC_Reads_Anchor`; `QA_population_zscore` (metadata BASE, Quast right) | `assembly_quality_dotplot`, `miaou`; `qc_reads_horizontal_barplot`; `qa_population_zscore` | yes: table `QA_L50_integer` (Quast alone) -> `qa_l50_integer` |
| `Bracken` | `Bracken_with_metadata` (Bracken base, metadata right); `QC_Reads_Anchor` | none; `qc_reads_horizontal_barplot` | no |
| `ResFinder` | `ResFinder_with_metadata` (ResFinder base); `ST22_Anchor` (metadata base); `QA_AMR_per_sample` (metadata base); `QA_fanout_exhibit` (metadata base) | none; `virulence_bar`, `virulence_variants`; `qa_amr_genes_per_sample`; `qa_fanout_rows_per_sample` | yes: the plot `amr_heatmap` reads `ResFinder` itself |
| `MLST` | `MLST_with_metadata` (MLST base, metadata right; tier 2 filters years 2023-2025); `ST22_Anchor` (metadata base); `AR1_MLST_Serotype_Virulence` (MLST base, metadata right) | `mlst_bar`, `year_distribution`; `virulence_bar`, `virulence_variants`; none | no |
| `VirulenceFinder` (additional) | `ST22_Anchor` (metadata base); `AR1` (after metadata, right); `QA_fanout_exhibit` (metadata base) | `virulence_bar`, `virulence_variants`; none; `qa_fanout_rows_per_sample` | no |
| `APEC_STEC_virulence_genes` (additional) | never joined with the metadata: it is inner-joined by gene into `ST22_Anchor` and `AR1`; it has no sample column, so no step can be written on it | (through `ST22_Anchor`) `virulence_bar`, `virulence_variants` | no (it is read by no plot alone) |
| `Summary` | no join with metadata; `Summary_phenotype_length_fragmentation` (Summary base, `Summary_quality` right) | `phenotype_genome_length_fragmentation` | no metadata at all |
| `Summary_quality` (same file as Summary) | no join with metadata; the same table above; and `QA_ST_with_NA` (alone) | `phenotype_genome_length_fragmentation`; `qa_sequence_type_missing` | no metadata at all |
| `Quality_metrics`, `Detailed_summary` | none | none (read by no table, no plot) | - |
| `metadata_schema` | in 13 tables (the 11 above that name it, plus `QA_year_types` and `QA_aggregated_no_key` as sole ingredient) | all plots except `phenotype_genome_length_fragmentation`, `amr_heatmap`, `qa_sequence_type_missing`, `qa_l50_integer` | - |

Where the demo does not fit her model (read from the map, confirmed by the runs):
1. One original in several joined tables: `FastP` 3, `Quast` 3, `Bracken` 2, `ResFinder` 4, `MLST` 3, `VirulenceFinder` 3. "The place where the original T1 and the metadata are joined" is then 2 to 4 places, not one (run C shows what one of them does: 2 plots).
2. A joined table built from several originals is in several trees: `ST22_Anchor` 6 originals (+metadata), `QC_Reads_Anchor` 4, `AR1` 4, `QA_fanout_exhibit` 3, `QA_population_zscore` 2, others 2.
3. Metadata is the BASE table in `ST22_Anchor`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore` (verified), so the entity's row comes from the metadata side there.
4. Plots on a table that never meets the metadata: `amr_heatmap` (on `ResFinder`), `qa_l50_integer` (on `QA_L50_integer`, Quast alone), `qa_sequence_type_missing` (`Summary_quality`), `phenotype_genome_length_fragmentation` (Summary + Summary_quality). The last two belong to histories with no metadata join at all; the first two are branches of a history that has a metadata join elsewhere.
5. Tables no plot reads: `Quality_metrics`, `Detailed_summary`, `FastP_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `AR1_MLST_Serotype_Virulence`.
6. Two tables read the metadata alone (`QA_year_types`, `QA_aggregated_no_key`): there is no join; the history is the metadata's own, and "the first T1" of it is `T1:metadata_schema` (the place she calls not advised). I wrote the step at their own T1 in runs A and B (my reading, not hers).

## 3. The runs
Run A = one step at the end of tier 1 of: 11 joined tables that join with metadata (`FastP_with_metadata`, `Quast_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `MLST_with_metadata`, `QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`) + the 2 metadata-only tables (`QA_year_types`, `QA_aggregated_no_key`) + the 4 originals with no metadata join (`Summary`, `Summary_quality`, `Quality_metrics`, `Detailed_summary`) = 17 places. Nothing at `T1:metadata_schema`.
- Plots changed 15 of 17. Entity gone from 14 plots. Stays in `amr_heatmap` and `qa_l50_integer`, WITH its full row (nothing emptied): those two plots read `ResFinder` and `QA_L50_integer` (Quast) directly; no written place is on their path. No column emptied anywhere. No key column: `qa_aggregated_no_key`.
- Every plot the entity left shows the baseline table minus its rows (`qa_population_zscore`: z-scores of the 41 others change, see section 1).
- Plot the owner did not intend to keep that still holds the entity: yes, two (`amr_heatmap`, `qa_l50_integer`); mechanism above (table never meets a written place). Run A3 writes `T1:ResFinder` and `T1:QA_L50_integer` as well: then 17 of 17 changed, entity in 0 plots.

Run B = A minus `T1:QC_Reads_Anchor` and `T1:Quast_with_metadata` (the tables under the three quality plots; their ancestors FastP/Quast/Bracken/metadata_schema were not written in A anyway) = 15 places.
- Plots changed 12. Gone from 11. Stays in 5: `qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `miaou` (as intended) and `amr_heatmap`, `qa_l50_integer` (same cause as in A). Nothing emptied: entity rows 1, 3, 3 with source/year/country complete.
- With the two extra places (B3, 17 places): exactly the three quality plots keep the entity; their tables equal the baseline byte for byte (not changed); 14 plots changed.

Run C = one step at `T1:MLST_with_metadata`: 2 plots change (`mlst_bar`, `year_distribution`), the entity is gone from those two and stays in the other 14, nothing emptied, nothing else changed (the two tables equal baseline-minus-entity). The `MLST` history has 3 joined places (`MLST_with_metadata`, `ST22_Anchor`, `AR1`); in C only one is written, so `virulence_bar` and `virulence_variants` (ST22_Anchor) keep the entity.

Run D = `T1:MLST` + `T1:metadata_schema` (earlier scope, rerun): 13 changed; gone from 9; stays in 7 (`qc_reads_horizontal_barplot`, `assembly_quality_dotplot`, `phenotype_genome_length_fragmentation`, `amr_heatmap`, `miaou`, `qa_sequence_type_missing`, `qa_l50_integer`); emptied: `qc_reads_horizontal_barplot` (source, year, country), `assembly_quality_dotplot` (source, country), `miaou` (source, country).

Run E (extra: the first T1 right after each original data table, her "exception", for all originals except metadata): 14 changed; gone from 11; stays in 5: `qa_amr_genes_per_sample`, `qa_fanout_rows_per_sample`, `qa_population_zscore` (metadata is the BASE table there), `qa_year_label`, `qa_facet_by_mapping` (metadata only). `qa_population_zscore` stays with `n50` and `n50_zscore` emptied. The two ST22_Anchor plots lose the entity in E only because the inner join with the APEC list drops a row with no virulence gene (data coincidence, reasoned from the join kind; the entity row comes from the metadata base).

Run B2 (extra): B + `T1:Quast` (the first T1 of the Quast history, instead of `T1:QA_L50_integer`): `assembly_quality_dotplot` and `miaou` LOSE the entity (their table `Quast_with_metadata` has Quast as base), and `qc_reads_horizontal_barplot` keeps it with `n50`, `total_length`, `largest_contig`, `L50` empty.

## 4. Comparison of A and B with the six-places result of the library test
- The library test result (six places unticked of 27, 21 written; S6 here, same code): entity stays in exactly the three quality plots with their metadata, 14 plots changed.
- Run B3 (17 places, chosen by her rule plus the two places for the two branches) gives the SAME tables for all 17 plots: the sha256 of each plot's table is equal between B3 and S6 (verified, 17 of 17). B3 writes 4 places fewer than S6 (`T1:MLST`, `T1:VirulenceFinder`, `T1:Summary_phenotype_length_fragmentation`, `T1:QA_ST_with_NA`: all covered by other written places) and does NOT write at the originals `FastP`, `Quast`, `Bracken`, `metadata_schema`.
- Run B alone (her rule, without the two branch places) is NOT the same result: it differs in `amr_heatmap` and `qa_l50_integer` (entity stays: 5 plots instead of 3).
- So: her model gives the same result as the six-place choice only when the two branches that have no metadata join are also written; the choice is by a rule (where original and metadata meet) instead of by naming six tables.

## 5. What the retest shows about "the effect calculated are wrong because the wrong scope has been chosen"
Disappears with her scope (run B3 against run D; each verified):
- The emptied metadata in the three quality plots (`qc_reads_horizontal_barplot`: source, year, country; `assembly_quality_dotplot`, `miaou`: source, country). Mechanism: D removed the entity from `metadata_schema` only (and `MLST`); `QC_Reads_Anchor` and `Quast_with_metadata` have FastP / Quast as the BASE (left) table and metadata on the right, so the base row stays and the metadata comes in empty. In B3 nothing is removed upstream of those joins, so the rows are complete (tables identical to the baseline).
- The entity staying in `phenotype_genome_length_fragmentation` and `qa_sequence_type_missing` (D stayed because the written places were not on their path; they read `Summary` / `Summary_quality`, histories with no metadata). With a place at the first T1 of these histories they are cleaned (both in A and B).
- The count of plots changed: D changed 13 with 7 holding the entity by accident; B3 changes 14 and the 3 that keep it are exactly the three intended.

Does NOT disappear, or is not given by her default place (each with its mechanism):
1. `amr_heatmap` and `qa_l50_integer` (run A, run B): the plot reads the original (`ResFinder`) or a table built from one original alone (`QA_L50_integer` from Quast) that never meets the metadata. The default "where original and metadata are joined" is not on their path; the entity stays, complete. They need a place at the first T1 of that branch (`T1:ResFinder`; `T1:QA_L50_integer`).
2. For `Quast` the two defaults of her model give DIFFERENT places inside ONE history and conflict (run B2): the first T1 (`T1:Quast`), which would cover `qa_l50_integer`, also removes the entity from `assembly_quality_dotplot` and `miaou` (their joined table has Quast as base) and empties the Quast columns in `qc_reads_horizontal_barplot` (it stays with `n50`, `total_length`, `largest_contig`, `L50` empty). Only a place at the first table of that branch (`T1:QA_L50_integer`, built from Quast alone) gives her result. For `ResFinder` the first T1 is not in conflict because no quality plot reads it. So "ONE place per tree" does not hold for `Quast`: the tree of an original table is a tree with several branches, and the branches that meet the metadata and those that do not need different places.
3. Her "exception" (first T1 of every original, run E) leaves the entity in the 4 tables where the metadata is the BASE (`QA_AMR_per_sample`, `QA_fanout_exhibit`, `QA_population_zscore`; `ST22_Anchor` only escapes by the inner join) and in the 2 metadata-only tables: removing from the original does not remove the entity's row coming from the metadata side. And `qa_population_zscore` stays with its Quast values empty. Her default (the joined table) handles these; the first-T1 default does not.
4. The z-score table (every run that writes `T1:QA_population_zscore`, which is before tier 2): the z-scores of ALL 41 other entities change (max 0.064). This is the nature of the table (a z-score over the population), not the scope; any place before tier 2 does it, and a place after tier 2 would keep the entity's contribution in the other rows' z-scores.
5. `qa_aggregated_no_key`: the plot has no key column; with any place that removes the entity before tier 2 its count (Norway 2024: 19 to 18) changes, and nothing in the plot names the entity.
6. Run C shows that a "history" can be several plots in several branches: one joined table is one place; the 14 other plots keep the entity.

What she may be missing (D-0532, with the argument):
- A history can have two defaults, or none that covers it: `Quast` (joined with the metadata in 3 tables AND read alone by `QA_L50_integer`; run B2), `ResFinder` (4 joined tables AND read by `amr_heatmap`), `Summary`/`Summary_quality` (none: no metadata, the default is the first T1). Why it matters: one place per tree, written as her rule says, leaves the entity in `amr_heatmap` and `qa_l50_integer` (run A) and the user does not see it unless the effects are measured per plot. How: the entity row survives in a table that no written place is upstream of.
- "The place where original T1 + metadata are joined" is several places for one original (2 to 4 here) and one joined table sits in several trees (`ST22_Anchor` 6 originals): with a place per joined table she must pick them one by one; run C is one of 4 for MLST. Written as "one place per tree", the user would write 3 steps for the MLST tree (`MLST_with_metadata`, `ST22_Anchor`, `AR1`) to get what the owner sees as "MLST removed".
- When the metadata is the base table (4 joined tables) the first-T1 of the originals does not remove the entity (run E); only the joined table's place does. This supports her default for joins, but not for her "first T1" exception.
- All of this was measured on the entity 10668076 and the demo; the effects per plot are what the user needs to see before confirming: the run shows that the place list alone does not tell her which plots keep the entity.

## 6. What I ran and what I could not do
- Ran: `map.py` (the map), `retest.py` (runs A, A2, A3, B, B2, B3, C, D, E, S6; 0 failures). All under `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ_wt_goals_sonnet/tmpAI/retest/`. The worktree `SPARMVET_VIZ_wt_good_practice` stayed clean (`git status --short` empty).
- Not done: only one entity (10668076) and the demo recipe; no run on the tier 2 place choices (no step at T2 or T3); no check of what a user sees in the dialog; "history" of the metadata-only tables is my reading; I did not run a place at `T1:metadata_schema` alone. Which tables count as "the place of a tree" for a join with six originals is not decided here.
