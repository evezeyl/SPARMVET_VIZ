# Q5 - `Categorical` or `String` for each shipped field

Nothing was migrated. Every statement is marked RUN (I ran it), READ (I read a file) or INFERRED.

## How I counted (RUN: `find_cat.py`, reads every yaml under config/, assets/, app/, tests/, docs/)
- 92 field declarations whose type is Categorical in any letter case, in 36 files. 85 are written `Categorical`; 7 are lowercase `categorical` in two files no recipe includes (LEGACY).
- A file included by two datasets counts once here (the Summary file feeds `Summary` and `Summary_quality`).
- The gallery (`assets/gallery_data/*/data_analysis_recipe.yaml`, 30 recipes) declares NO Categorical field: all are `String` or numbers (RUN grep; the word only appears in the taxonomy label "1 Numeric, 1 Categorical"). Nothing to migrate there.
- Not runnable here: templates (`e_coli`, `simple_template`, `audit`) and `retest_broken_header`, `retest_bad_select_column`: their data files are absent or deliberately wrong (RUN, error shown), so their plot order is READ only.

## Result (counts of the 92)
- Stay Categorical: 0 forced by evidence. At the shipped sizes memory is not a reason (measure below). Eve may still choose to keep the figshare ones as a "large table" example.
- Become String: 80 (54 plain, 22 where a plot order changes, 4 where the declared type itself looks wrong).
- Enum candidates (a written order is the honest type): 5.
- Legacy / not live: 7.

## Plots whose level order changes if the Categorical field becomes String (RUN: same recipe, same data, only the type changed; compared the labels drawn on axis, legend and panels)
First-appearance order (Categorical) becomes alphabetical (String). Table values and counts are the same (the 12-plot hash comparison of round 4 still holds, RUN `check_string`).
- 1_test_data_ST22_dummy: amr_heatmap (gene axis, legend), miaou (source), mlst_bar (country legend), qa_aggregated_no_key, qa_amr_genes_per_sample, qa_facet_by_mapping (panel order Norway,France,Germany -> France,Germany,Norway), qa_population_zscore, qa_sequence_type_missing (ST axis), qa_year_label, year_distribution, phenotype_genome_length_fragmentation (legend ST).
- 2_test_data_ST22_dummy: multi_resistance_by_country (panels), plasmid_prevalence_by_country (legend).
- figshare_integration: plot_a, plot_b, plot_c (axis and legend).
- stress_test_master: stress_species_amr (axis and legend). The round-4 String copy (`pipes_string`) did NOT convert this recipe (its types are written with quotes); I redid it in `pipes_stress` (RUN) and the order does change. Round 4's "same" for stress should be read as untested.
- demo_abromics: demo_st_by_source.
- Unchanged: assembly_quality_dotplot, qa_fanout_rows_per_sample, qa_l50_integer, qc_reads_horizontal_barplot, virulence_bar, virulence_variants, 3_test_no_joins/sequence_type_counts, 2_test multi_resistance_by_source, retest_tier2 (both plots: data already ascending), retest_top_n_other.
- 1_Abromics_general_pipeline was not run (no data render in my run); its MLST fields are the same as in demo_abromics (READ).
- Limit: I read axis labels, legend text and panel order of the first-appearance vs alphabetical, not the pictures pixel by pixel.

## Where first-appearance order carries meaning
- In the shipped recipes nowhere (INFERRED from RUN + READ): the orders seen are by chance of the file (ST 227,93,95,10...; countries Norway,France,Germany; resistance classes beta-lactam,tetracycline,MULTI-DRUG). The only deliberate sorts (`ResFinder_wrangling`, `ST22_Anchor_wrangling`: by gene count then sample_id, READ) order the rows of the table, and `sample_id` is already String, so samples are drawn alphabetically both ways (RUN: y axis "same" for amr_heatmap).
- Where a written order would be honest (Enum): figshare phenotype S / I / R / NI (today legend S,R,NI,I; String gives I,NI,R,S); quality_module Passed / Warning; audit `status`; `year` (time order; 4-digit text sorts right but not 5 vs 10).
- Dates: `collection_date` (stress, e_coli) and `submission_date` (audit) are dates written as text: the honest type is Date. ISO text (2023-04-11) sorts in time order as String too (RUN values seen in STRESS_data.tsv).
- `value` in the stress pipeline holds numbers (46.49) but is declared Categorical: the type is wrong whatever is decided.
- ST / sequence_type and locus_1..7: identifiers. Neither type gives a numeric order (String: 10,101,117,...,1485,154).

## Join keys (RUN keys.py + READ)
- Every join `on` key in the shipped recipes is `sample_id`, declared `String` in all 15 recipes. The two other joins are `VF_gene` = `Gene_name`: `VF_gene` is built by a text split in the wrangling (READ, cast String), `Gene_name` is declared String. No shipped join key is Categorical, so none changes type on one side only.
- The risk is for users: a join of Categorical with String is refused (ADR-102, RUN in round 4, `q2.py`), so a user who converts one side only gets a refusal, not a silent change.
- Stress `id` and audit `lab_id` are Categorical identifiers but those recipes have no join.

## Memory (RUN `memory.py`, `memory_rss.py`)
- Largest shipped table: fg_phenotypes 18,437 rows x 4 columns; fg_genotypes 10,839 x 6. Polars' own size estimate (approximate): fg_genotypes 6 text columns String 0.48 MB, Categorical 0.26 MB; fg_phenotypes String 0.30, Categorical 0.22 MB; STRESS 4 columns String 0.42, Categorical 0.16 MB. In parquet on disk the sizes are equal (37.6 vs 38.1 kB, 4.4 vs 4.7 kB) and for STRESS Categorical is larger (30.8 vs 48.2 kB, because of the 10,000 unique ids).
- Same table repeated 100 times (1.08 million rows): estimate String 47.8 MB, Categorical 26.1 MB (about 45 % less); group_by 0.09 s vs 0.02 s, sort 0.40 vs 0.20 s. Process memory (RSS) was not conclusive (the original table stays in memory), so quote only the estimate.
- Meaning: Categorical saves memory and time only for few distinct values over very many rows; shipped tables are under 1 MB.

## The list (one line per declaration)
