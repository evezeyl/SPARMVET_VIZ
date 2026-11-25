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