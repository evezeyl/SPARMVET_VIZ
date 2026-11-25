
### country
- metadata_schema: in the file/base as String
- FastP_with_metadata: T1:1 polars_join: appears (String)
- Quast_with_metadata: T1:1 polars_join: appears (String)
- Bracken_with_metadata: T1:1 polars_join: appears (String)
- ResFinder_with_metadata: T1:1 polars_join: appears (String)
- MLST_with_metadata: T1:1 polars_join: appears (String)
- QC_Reads_Anchor: T1:3 polars_join: appears (String)
- ST22_Anchor: in the file/base as String
- AR1_MLST_Serotype_Virulence: T1:1 polars_join: appears (String)
- QA_AMR_per_sample: in the file/base as String
- QA_year_types: in the file/base as String
- QA_fanout_exhibit: in the file/base as String; T2:1 polars_group_by: gone
- QA_aggregated_no_key: in the file/base as String
- QA_population_zscore: in the file/base as String

### year
- metadata_schema: in the file/base as Float64
- FastP_with_metadata: T1:1 polars_join: appears (Float64)
- Quast_with_metadata: T1:1 polars_join: appears (Float64); T1:2 polars_unpivot: gone
- Bracken_with_metadata: T1:1 polars_join: appears (Float64)
- ResFinder_with_metadata: T1:1 polars_join: appears (Float64)
- MLST_with_metadata: T1:1 polars_join: appears (Float64)
- QC_Reads_Anchor: T1:3 polars_join: appears (Float64)
- ST22_Anchor: in the file/base as Float64
- AR1_MLST_Serotype_Virulence: T1:1 polars_join: appears (Float64)
- QA_AMR_per_sample: in the file/base as Float64; T2:1 polars_group_by: gone
- QA_year_types: in the file/base as Float64
- QA_fanout_exhibit: in the file/base as Float64; T1:3 polars_select: gone
- QA_aggregated_no_key: in the file/base as Float64; T2:1 polars_group_by: gone
- QA_population_zscore: in the file/base as Float64; T1:2 polars_select: gone

### year_label
- QA_year_types: T1:1 polars_with_columns: appears (String)
- QA_aggregated_no_key: T1:1 polars_with_columns: appears (String)

### era
- MLST_with_metadata: T2:1 polars_with_columns: appears (String)

### virulence_raw
- VirulenceFinder: in the file/base as String; T1:2 polars_with_columns: type String -> List(String); T1:3 polars_explode: type List(String) -> String; T1:8 polars_drop: gone

### VF_gene
- VirulenceFinder: T1:7 polars_rename: appears (String)
- ST22_Anchor: T1:4 polars_join: appears (String); T1:6 polars_rename: gone
- AR1_MLST_Serotype_Virulence: T1:2 polars_join: appears (String); T1:4 polars_rename: gone
- QA_fanout_exhibit: T1:2 polars_join: appears (String); T2:1 polars_group_by: gone

### Selected_Virulence_Genes
- ST22_Anchor: T1:6 polars_rename: appears (String)

### selected_virulence_genes
- AR1_MLST_Serotype_Virulence: T1:4 polars_rename: appears (String)

### sequence_type
- MLST: in the file/base as String
- MLST_with_metadata: in the file/base as String
- ST22_Anchor: T1:3 polars_join: appears (String)
- AR1_MLST_Serotype_Virulence: in the file/base as String
