# Q5 - `Categorical` or `String` for each shipped field

Nothing was migrated. Every statement is marked RUN (I ran it), READ (I read a file) or INFERRED.

## How I counted (RUN: `find_cat.py`, reads every yaml under config/, assets/, app/, tests/, docs/)
- 92 field declarations whose type is Categorical in any letter case, in 36 files. 85 are written `Categorical`; 7 are lowercase `categorical` in two files no recipe includes (LEGACY).
- A file included by two datasets counts once here (the Summary file feeds `Summary` and `Summary_quality`).
- The gallery (`assets/gallery_data/*/data_analysis_recipe.yaml`, 34 recipes) declares NO Categorical field (RUN grep: the word appears only in the taxonomy label): all are `String` or numbers (RUN grep; the word only appears in the taxonomy label "1 Numeric, 1 Categorical"). Nothing to migrate there.
- Not runnable here: templates (`e_coli`, `simple_template`, `audit`) and `retest_broken_header`, `retest_bad_select_column`: their data files are absent or deliberately wrong (RUN, error shown), so their plot order is READ only.

## Result (counts of the 92)
- Stay Categorical: 0 forced by evidence. At the shipped sizes memory is not a reason (measure below). Eve may still choose to keep the figshare ones as a "large table" example.
- Become String: 80 (53 plain, 23 where a plot order changes, 4 where the declared type itself looks wrong).
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
# Q5 Categorical or String, every shipped declaration (RUN: scripts in tmpAI/panel/round5/)

Legend: String = becomes String; String* = becomes String AND a plot level order changes (listed); String! = becomes String but the declared type itself looks wrong; Enum candidate = a written order would be the honest type; LEGACY = orphan file.

Counts (declarations in files, 7 of them legacy lowercase): String: 53, LEGACY: 7, String*: 23, Enum candidate: 5, String!: 4; total 92

No declaration is classed as 'stays Categorical for memory': the biggest shipped table is 18,437 rows (RUN, see memory section).


## assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml

- Location: String - reference text; no plot
- Name_plasmid: String - reference text; no plot
- VirulenceFinder: String - reference text; no plot

## pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly_output_fields.yaml

- sample_id: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides
- ST: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides
- quality_metric: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides

## pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml

- Location: String - reference text; no plot
- Name_plasmid: String - reference text; no plot
- VirulenceFinder: String - reference text; no plot

## pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml

- taxon_1: String - plain text label; wrangling uses it

## pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml

- data: String - plain text label; wrangling uses it
- data_type: String - plain text label; wrangling uses it
- predicted_phenotype: String* - plain text; plain text label; plot order changes: amr_heatmap (legend); figshare plot_a (legend)
- cge_predicted_phenotype: String - plain text label; wrangling uses it
- contig: String - plain text label; wrangling uses it
- accession: String - plain text label; wrangling uses it

## pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml

- scheme: String - plain text label; wrangling uses it
- sequence_type: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_1: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_2: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_3: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_4: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_5: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_6: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- locus_7: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)

## pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml

- quality_module: Enum candidate - Passed / Warning (RUN): ordered levels; unused order in shipped plots
- quality_feedback: String - plain text label; wrangling uses it
- bracken_main_taxon: String - plain text label; wrangling uses it

## pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml

- gene: String* - plain text; plain text label; plot order changes: amr_heatmap (x)
- predicted_phenotype: String* - plain text; plain text label; plot order changes: amr_heatmap (legend); figshare plot_a (legend)

## pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml

- quality_module: Enum candidate - Passed / Warning (RUN): ordered levels; unused order in shipped plots
- taxon: String - plain text label; wrangling uses it
- genotype: String - plain text label; wrangling uses it
- phenotype: String - plain text label; wrangling uses it
- cge_phenotype: String - plain text label; wrangling uses it
- plasmid: String - plain text label; wrangling uses it
- ST: String* - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order); plot order changes: qa_sequence_type_missing (y), phenotype_genome_length_fragmentation (legend)

## pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml

- serotype: String - plain text label; wrangling uses it
- virulence_raw: String - plain text label; wrangling uses it

## pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml

- source: String* - plain text; plain text label; plot order changes: miaou (facet/legend), demo_st_by_source (x, legend)
- country: String* - plain text; plain text label; plot order changes: mlst_bar, qa_aggregated_no_key, qa_amr_genes_per_sample, qa_facet_by_mapping (panels), qa_population_zscore, qa_year_label, year_distribution (axis/legend/panels)

## pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml

- plasmid: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides
- hsp_lengthtotal_length: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides
- contig: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides
- accession: LEGACY - lowercase 'categorical' in a file no recipe includes (READ: grep found no include); not a Polars type; leave or delete, Eve decides

## pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml

- gene: String* - plain text; plain text label; plot order changes: amr_heatmap (x)
- predicted_phenotype: String* - plain text; plain text label; plot order changes: amr_heatmap (legend); figshare plot_a (legend)
- accession: String - plain text label; wrangling uses it

## pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml

- Source: String - plain text label; wrangling uses it
- Country: String* - plain text; plain text label; plot order changes: multi_resistance_by_country (panels)

## pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml

- plasmid_name: String* - plain text; plain text label; plot order changes: plasmid_prevalence_by_country (legend)
- accession: String - plain text label; wrangling uses it

## pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml

- host_animal_common: String* - plain text; plain text label; plot order changes: figshare plot_b (x), plot_c (legend)
- gene: String* - plain text; plain text label; plot order changes: amr_heatmap (x)
- gene_type: String - plain text label; wrangling uses it
- gene_identifier: String - plain text label; wrangling uses it
- gene_name_family: String* - plain text; plain text label; plot order changes: figshare plot_b (legend)
- resistance_class: String* - plain text; plain text label; plot order changes: figshare plot_c (x)

## pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml

- host_animal_species: String - plain text label; wrangling uses it
- host_animal_common: String* - plain text; plain text label; plot order changes: figshare plot_b (x), plot_c (legend)
- specimen_source_tissue: String - plain text label; wrangling uses it
- final_diagnosis: String - plain text label; wrangling uses it
- animal_infection_site_uti: String - plain text label; wrangling uses it

## pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml

- mic_id: String* - plain text; plain text label; plot order changes: figshare plot_a (x)
- breakpoint: String - plain text label; wrangling uses it
- predicted_phenotype: Enum candidate - S / I / R / NI (RUN values): a written order (S, I, R, NI) is meaningful; first appearance gave S,R,NI,I

## pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml

- id: String - identifier, as many distinct values as rows (10000 of 10000): Categorical gives no memory gain
- species: String* - plain text; plain text label; plot order changes: stress_species_amr (x)
- amr_class: String* - plain text; plain text label; plot order changes: stress_species_amr (legend)
- collection_date: String! - dates as text: order is time; the honest type is Date; as String ISO dates still sort in time order
- value: String! - numbers (46.49...) declared Categorical: the type is wrong, should be Float64; ask Eve (stress test may do this on purpose)

## retest/retest_bad_select_column.yaml

- gene: String* - plain text; plain text label; plot order changes: amr_heatmap (x)
- predicted_phenotype: String* - plain text; plain text label; plot order changes: amr_heatmap (legend); figshare plot_a (legend)

## retest/retest_broken_header.yaml

- gene: String* - plain text; plain text label; plot order changes: amr_heatmap (x)
- predicted_phenotype: String* - plain text; plain text label; plot order changes: amr_heatmap (legend); figshare plot_a (legend)

## retest/retest_tier2.yaml

- group: String - plain text label; wrangling uses it
- year: Enum candidate - year as category: time order; as String 4-digit years sort correctly; Int or Enum if gaps matter

## retest/retest_top_n_other.yaml

- variant: String - plain text label; wrangling uses it

## templates/audit.yaml

- lab_id: String - identifier, as many distinct values as rows (10000 of 10000): Categorical gives no memory gain
- submission_date: String! - dates as text: order is time; the honest type is Date; as String ISO dates still sort in time order
- status: Enum candidate - workflow status: probably ordered; data file absent, READ only

## templates/complex_template/genomics_input.yaml

- gene_presence: String - plain text label; wrangling uses it

## templates/complex_template/metadata_input.yaml

- country: String* - plain text; plain text label; plot order changes: mlst_bar, qa_aggregated_no_key, qa_amr_genes_per_sample, qa_facet_by_mapping (panels), qa_population_zscore, qa_year_label, year_distribution (axis/legend/panels)

## templates/e_coli.yaml

- serotype: String - plain text label; wrangling uses it
- sequence_type: String - identifier (ST number / allele): neither order is numeric (Categorical = order of appearance, String = 10,101,117..1485,154 text order)
- ctx_m_gene: String - plain text label; wrangling uses it
- collection_date: String! - dates as text: order is time; the honest type is Date; as String ISO dates still sort in time order
- country_of_origin: String - plain text label; wrangling uses it
- hospital_site: String - plain text label; wrangling uses it
- patient_outcome: String - plain text label; wrangling uses it

## templates/simple_template.yaml

- group: String - plain text label; wrangling uses it
- category: String - plain text label; wrangling uses it