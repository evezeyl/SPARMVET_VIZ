### Demo recipe `1_test_data_ST22_dummy` (16 lines, 13 files)

| file:line | step | column | formula | today's check | D | D = today (plan, column) | result of the column in its recipe (today) | runs |
|---|---|---|---|---|---|---|---|---|
| 1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:14 | polars_with_columns | resistance_points | `pl.when(pl.col('value') == 'Susceptible').then(pl.lit(0)).when(pl.col('valu...` | accepted | built | yes | 123 rows, Int32, 41 missing, #86d6e3c9 | 1 |
| 1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:21 | polars_group_by | phenotype_count | `pl.col('resistance_points').sum()` | accepted | built | yes | 123 rows, Int32, 0 missing, #ba87dc31 | 1 |
| 1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml:19 | polars_with_columns | length_ratio | `pl.col('hsp_len').cast(pl.Float64) / pl.col('total_len').cast(pl.Float64)` | accepted | built | yes | 280 rows, Float64, 0 missing, #8d08eac5 | 17 |
| 1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling.yaml:12 | polars_with_columns | era | `pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Rece...` | accepted | built | yes | 42 rows, String, 0 missing, #fe420176 | 1 |
| 1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml:9 | polars_with_columns | sequence_type | `pl.col('sequence_type').replace_strict({'unknown': 'Non Determined'}, defau...` | accepted | built | yes | 42 rows, String, 2 missing, #121596de | 17 |
| 1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample.yaml:19 | polars_group_by | n_amr_genes | `pl.col('gene').count()` | accepted | built | yes | 74 rows, UInt32, 0 missing, #5b098933 | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key.yaml:8 | polars_with_columns | year_label | `pl.col('year').cast(pl.Int64).cast(pl.String)` | accepted | built | yes | 42 rows, String, 0 missing, #33adb551 | 2 |
| 1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key.yaml:16 | polars_group_by | n_samples | `pl.col('sample_id').count()` | accepted | built | yes | 42 rows, UInt32, 0 missing, #5e86fc86 | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit.yaml:22 | polars_group_by | rows_per_sample | `pl.col('VF_gene').count()` | accepted | built | yes | 1731 rows, UInt32, 0 missing, #1cd46aa5 | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_population_zscore.yaml:18 | polars_with_columns | n50_zscore | `(pl.col('n50') - pl.col('n50').mean()) / pl.col('n50').std()` | accepted | built | yes | 42 rows, Float64, 0 missing, #79760dac | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_year_types.yaml:6 | polars_with_columns | year_label | `pl.col('year').cast(pl.Int64).cast(pl.String)` | accepted | built | yes | 42 rows, String, 0 missing, #33adb551 | 2 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_wrangling.yaml:4 | polars_with_columns | status | `pl.lit('Detected')` | accepted | built | yes | 70 rows, String, 0 missing, #8d52e328 | 17 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_wrangling.yaml:10 | polars_with_columns | total_gene_count | `pl.len().over(['sample_id'])` | accepted | built | yes | 70 rows, UInt32, 0 missing, #72a82617 | 2 |
| 1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling.yaml:54 | polars_with_columns | virulence_count | `pl.len().over(['sample_id'])` | accepted | built | yes | 70 rows, UInt32, 0 missing, #72a82617 | 2 |
| 1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml:19 | polars_with_columns | value | `pl.col('value').cast(pl.String).str.split(', ')` | accepted | built | yes | 168 rows, List(String), 9 missing, #68183f30 | 17 |
| 1_test_data_ST22_dummy/wrangling/VirulenceFinder_wrangling.yaml:6 | polars_with_columns | virulence_raw | `pl.col('virulence_raw').cast(pl.String).str.split(',')` | accepted | built | yes | 1315 rows, List(String), 0 missing, #b878da13 | 17 |

### Other shipped recipes and templates

| file:line | step | column | formula | today's check | D | D = today (plan, column) | result of the column in its recipe (today) | runs |
|---|---|---|---|---|---|---|---|---|
| 1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:21 | polars_with_columns | drug_name | `pl.col('cge_predicted_phenotype').str.split(',')` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:35 | polars_with_columns | AMR_Categories_Summary | `pl.when(pl.col('amr_class').is_not_null().any().over('fragment_row')).then(...` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:50 | polars_group_by | gene_count | `pl.col('AMR_Categories_Summary').count()` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| 2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:13 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 70 rows, String, 0 missing, #2a4980f3 | 1 |
| 2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:38 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 70 rows, Boolean, 0 missing, #b6aae85c | 1 |
| 2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:43 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 70 rows, String, 0 missing, #8609e5d2 | 1 |
| templates/complex_template/genomics_wrangling.yaml:4 | polars_with_columns | gene_presence | `pl.col('gene_presence').cast(pl.String).str.split(';')` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |

### Equality recipes (`app/tests/equality/recipes`)

| file:line | step | column | formula | today's check | D | D = today (plan, column) | result of the column in its recipe (today) | runs |
|---|---|---|---|---|---|---|---|---|
| eq/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 67 rows, String, 1 missing, #27b3d109 | 1 |
| eq/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 64 rows, Boolean, 0 missing, #28224714 | 1 |
| eq/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 64 rows, String, 0 missing, #5e1a8096 | 1 |
| eq/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 67 rows, String, 1 missing, #27b3d109 | 1 |
| eq/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 64 rows, Boolean, 0 missing, #28224714 | 1 |
| eq/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 64 rows, String, 0 missing, #5e1a8096 | 1 |
| eq/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 70 rows, String, 0 missing, #2a4980f3 | 1 |
| eq/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 70 rows, Boolean, 0 missing, #b6aae85c | 1 |
| eq/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 70 rows, String, 0 missing, #8609e5d2 | 1 |
| eq/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 70 rows, String, 0 missing, #2a4980f3 | 1 |
| eq/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| eq/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
