# Scan: where the metadata is joined, and the steps that keep a fixed list of columns

Fact-checked by an independent agent on 2026-11-23 against the recipe files; nine statements corrected. Read only: nothing was run and nothing was changed.

Date 2026-11-23. Read only: recipes were read with the yaml loader (script `tmpAI/coordinator/scan_joins/scan.py`, its raw output `scan_out.txt`, `partB.json`). Nothing was run in the engine or the app. Evidence is "read at file:line" unless marked [REASONED]. Short names: "left join" = a join that keeps every row of the first table; "inner join" = a join that keeps only the rows found on both sides; "kept-list step" = a step that keeps only the listed columns (`polars_select`); "entity id" = the column that identifies the entity (here `sample_id`).

## First screen: the plain answers

1. Her question, "do all the recipes with those tables have the metadata as left join in tier 1?": **No, not all.** Of the 13 joined tables of the demo recipe that have the metadata among their ingredients: 7 bring it in by a join that keeps every row of the first table (left); 4 have the metadata as their FIRST table (nothing joins it in: the other tables are left-joined to it); 2 have no join step at all (they are made from the metadata alone). In the other recipes, each joined table that brings the metadata in does so by a left join; `demo_join` (recipe `demo_abromics`) has the metadata as its first table. The exception is the recipe `2_test_data_ST22_dummy`: both of its joined tables bring the metadata in by a join that keeps only the rows found on both sides (inner).
2. The metadata is the FIRST table of the join in 7 joined tables (all in the demo recipe except one in `demo_abromics`): `ST22_Anchor`, `QA_AMR_per_sample`, `QA_year_types`, `QA_fanout_exhibit`, `QA_aggregated_no_key`, `QA_population_zscore` (demo recipe) and `demo_join` (`demo_abromics.yaml:40`). Everywhere else it is second (or 4th in `QC_Reads_Anchor`). Two of the seven (`QA_year_types`, `QA_aggregated_no_key`) have NO join step at all.
3. The metadata join is always written in tier 1 of a JOINED table, never in an original data table, and no join step exists in any tier 2, tier 3 or original table (read: the script found none).
4. Joins that are not left joins: the two inner joins with the metadata in `2_test_*` (above), and the inner join with the reference list `APEC_STEC_virulence_genes` at `1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:30` and `.../AR1_MLST_Serotype_Virulence.yaml:20` (the AR1 file is shared by 2 recipes; the ST22 file is used by 1 recipe).
5. The 20 kept-list / group-by steps: **3 sit in original data tables** (`MLST` and `VirulenceFinder` tier 1, each shared by several recipes, and `Genes` of the retest recipe `retest_bad_select_column.yaml:28`); 11 are kept-list steps of joined tables that have the metadata among their ingredients (in 5 of them no step joins it in: it is the first table, or the only one); 2 are kept-list steps of joined tables without metadata (`QA_ST_with_NA`, `QA_L50_integer`); 4 are group-by steps (3 keep `sample_id` among the group columns, 1 does not: `QA_aggregated_no_key`).
6. The two QA tables: today each is a `joins:` entry with ONE ingredient (the metadata); the format already lets a second data schema read the same file; a data schema may have a tier 2 when a plot reads it directly. Nothing in the format forbids moving them (reasoned) (details in part C); one point is hers (C, her words: "they must move in the data_schema", ledger D-0608).

## Part A. Which joined tables join the metadata, and how

Listing: the recipes of `config/data_analysis_recipes/pipelines/*.yaml`, `templates/*.yaml`, `retest/*.yaml`, `experimental/*.yaml` (the shell `glob`); `experimental/test_logic.yaml` has no `data_schemas` and was skipped; the tarball `2026-04-10_pipelines.tar.gz` was not read. Role of the metadata: the recipe's `metadata_schema` block (a recipe without it has no metadata table; `figshare_integration` has `fg_metadata` by name only [REASONED: it plays the role]). The "first table" is the first line of `ingredients`.
Gallery bundles apart: `assets/gallery_data/*/data_analysis_recipe.yaml` hold no `metadata_schema` or `joins:` line (checked by grep on all bundles: 0 files; read three: `bar_simple`, `area_simple`, `bar_grouped`).

| Recipe | Joined table (line of its entry) | Tables in order | Metadata is | Step that brings the metadata (tier 1) | Kind |
|---|---|---|---|---|---|
| 1_Abromics_general_pipeline | AR1_MLST_Serotype_Virulence (:67) | MLST, metadata_schema, VirulenceFinder, APEC_STEC | 2nd | `1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml:4` | left |
| 1_test_data_ST22_dummy | FastP_with_metadata (:165) | FastP, metadata | 2nd | `.../FastP_Metadata_wrangling.yaml:2` | left |
| same | Quast_with_metadata (:173) | Quast, metadata | 2nd | `.../Quast_Metadata_wrangling.yaml:2` | left |
| same | Bracken_with_metadata (:181) | Bracken, metadata | 2nd | `.../Bracken_Metadata_wrangling.yaml:2` | left |
| same | ResFinder_with_metadata (:189) | ResFinder, metadata | 2nd | `.../ResFinder_Metadata_wrangling.yaml:2` | left |
| same | MLST_with_metadata (:197) | MLST, metadata | 2nd | `.../MLST_Metadata_wrangling_tier1.yaml:2` | left |
| same | QC_Reads_Anchor (:206) | FastP, Quast, Bracken, metadata | 4th (last) | `.../QC_Reads_Anchor_wrangling.yaml:14` | left |
| same | ST22_Anchor (:224) | metadata, FastP, ResFinder, MLST, VirulenceFinder, APEC_STEC | **1st** | no step "brings" it: it is the first table; others are left-joined to it (`ST22_Anchor_wrangling_tier1.yaml:5,11,17,23`) and the list by an inner join (`:30`) | left (and 1 inner) |
| same | AR1_MLST_Serotype_Virulence (:238) | MLST, metadata, VirulenceFinder, APEC_STEC | 2nd | `.../AR1_MLST_Serotype_Virulence.yaml:4` (inner with the list: `:20`) | left (and 1 inner) |
| same | QA_AMR_per_sample (:250) | metadata, ResFinder | **1st** | first table; `QA_AMR_per_sample_tier1.yaml:5` left-joins ResFinder | left |
| same | QA_year_types (:266) | metadata | **1st, alone** | no join step | none |
| same | QA_fanout_exhibit (:280) | metadata, ResFinder, VirulenceFinder | **1st** | `QA_fanout_exhibit_tier1.yaml:4,9` left-join the others | left |
| same | QA_aggregated_no_key (:290) | metadata | **1st, alone** | no join step | none |
| same | QA_population_zscore (:298) | metadata, Quast | **1st** | `QA_population_zscore_tier1.yaml:6` left-joins Quast | left |
| 2_test_data_ST22_dummy | AMR_Profile_Joint (:57) | amr_data, metadata | 2nd | `2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:17` | **inner** |
| same | Plasmid_Profile_Joint (:64) | plasmid_data, metadata | 2nd | `.../Plasmid_Profile_Joint.yaml:10` | **inner** |
| demo_abromics | demo_join (:40) | metadata, MLST | **1st** | `demo_abromics.yaml:49` left-joins MLST | left |
| templates/complex_template | master_assembly (:40) | genomics, metadata | 2nd | `complex_template/master_steps.yaml:2` | left |
| templates/e_coli | amr_with_metadata (:83) | amr_results, metadata | 2nd | `e_coli.yaml:90` | left |
| templates/left_join_lesson | lesson_assembly (:61) | sequenced, metadata | 2nd | `left_join_lesson.yaml:68` | left |
| templates/simple_template | main_collection (:58) | primary_data, metadata | 2nd | `simple_template.yaml:65` | left |

Recipes with no metadata block, so no metadata join: `3_test_no_joins` (no joins), `stress_test_master`, `templates/audit` (no joins), `retest/*` (4 recipes, joins of one ingredient). `figshare_integration`: `figshare_triple_join` has `fg_metadata` first and left-joins the other two (`figshare_integration/wrangling/figshare_triple_join_steps.yaml:2,7`) [REASONED: `fg_metadata` plays the metadata role, by its name only].

Plain answer per recipe, "every joined table that includes the metadata joins it with a left join in tier 1":
- 1_Abromics_general_pipeline: yes (1 table; metadata second).
- 1_test_data_ST22_dummy: yes where a join exists: 11 of 13 tables; the metadata is first in 6 (two of them with no join step) and second or later in 7 (5 second, `QC_Reads_Anchor` 4th, `AR1` 2nd).
- 2_test_data_ST22_dummy: **no**, both are inner joins (2 tables, metadata second).
- demo_abromics: yes (metadata first, 1 table).
- complex_template, e_coli, left_join_lesson, simple_template: yes (metadata second, 1 table each).
- figshare_integration: yes, by the name-role only [REASONED] (metadata-role table first).
- Where the metadata join lives: the tier 1 of the JOINED table (all the above); never the tier 1 of an original data table (confirmed: the script printed no join step in any original table or in any tier 2).

Non-left joins in the shipped recipes: (a) `AMR_Profile_Joint.yaml:17` and `Plasmid_Profile_Joint.yaml:10` (inner, with the metadata); (b) `ST22_Anchor_wrangling_tier1.yaml:30` and `AR1_MLST_Serotype_Virulence.yaml:20` (inner, with the reference list `APEC_STEC_virulence_genes`, matched on `VF_gene`).

## Part B. The 20 steps, table by table

Row = tier file:line; table (kind); recipes that use the file; position in its stage (k of n); what it keeps; entity id kept?; downstream (joins that read it, and the plots that read it or them).

### (1) Steps in ORIGINAL data tables (the earliest places)

| Step | Table | Recipes | Position | Keeps | Entity id | Downstream |
|---|---|---|---|---|---|---|
| `1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml:2` | MLST (original, tier 1) | 1_Abromics, 1_test_data, 3_test_no_joins, demo_abromics | first of 3 | sample_id, scheme, sequence_type | yes (sample_id) | joins reading it: AR1 (1_Abromics: plots abromics_st_by_country, abromics_st_by_source); in 1_test_data: MLST_with_metadata (plots mlst_bar, year_distribution), ST22_Anchor (virulence_bar, virulence_variants), AR1 (no plot); 3_test_no_joins: plotted directly (sequence_type_counts); demo_abromics: demo_join (demo_st_by_source) |
| `.../wrangling/VirulenceFinder_wrangling.yaml:2` | VirulenceFinder (original, tier 1) | 1_Abromics, 1_test_data | first of 10 | sample_id, serotype, virulence_raw | yes | 1_Abromics: AR1 (2 plots above); 1_test_data: ST22_Anchor (2 plots), AR1 (none), QA_fanout_exhibit (qa_fanout_rows_per_sample) |
| `retest/retest_bad_select_column.yaml:28` | Genes (original, tier 1) | retest_bad_select_column only | only step | sample_id, gene, phenotype | yes | join Genes_joined (plot genes_bar). Note: this recipe is a deliberate bad-select test (name) [REASONED] |

### (2) Kept-list steps in joined tables that have the metadata among their ingredients

| Step | Table | Recipes | Position | Keeps | Entity id | Downstream (plots) |
|---|---|---|---|---|---|---|
| `AR1_MLST_Serotype_Virulence.yaml:32` | AR1 | 1_Abromics, 1_test_data | 5 of 6 | sample_id, source, year, country, sequence_type, serotype, selected_virulence_genes, vf_protein | yes | 1_Abromics: abromics_st_by_country, abromics_st_by_source; 1_test_data: none |
| `AR1_MLST_Serotype_Virulence.yaml:34` | AR1 | same | last of 6 (the same list again) | same list | yes | same |
| `.../ST22_Anchor_wrangling_tier1.yaml:46` | ST22_Anchor | 1_test_data | last of 8 | sample_id, source, year, country, sequence_type, serotype, Selected_Virulence_Genes, VF_protein, gene, status, phenotype | yes | virulence_bar, virulence_variants |
| `.../QA_AMR_per_sample_tier1.yaml:10` | QA_AMR_per_sample | 1_test_data | last of 2 | sample_id, country, source, year, gene, predicted_phenotype | yes | qa_amr_genes_per_sample |
| `.../QA_fanout_exhibit_tier1.yaml:14` | QA_fanout_exhibit | 1_test_data | last of 3 | sample_id, country, gene, VF_gene | yes | qa_fanout_rows_per_sample |
| `.../QA_population_zscore_tier1.yaml:11` | QA_population_zscore | 1_test_data | last of 2 | sample_id, country, n50 | yes | qa_population_zscore |
| `2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:49` | AMR_Profile_Joint | 2_test | last of 8 | Year, Source, Country, gene, predicted_phenotype_clean, sample_id, accession, Multiresistant | `sample_id` kept, but this recipe declares NO entity id (candidate only) | multi_resistance_by_country, multi_resistance_by_source |
| `.../Plasmid_Profile_Joint.yaml:29` | Plasmid_Profile_Joint | 2_test | last of 5 | Year, Source, Country, plasmid_name, sample_id, accession | same note | plasmid_prevalence_by_country |
| `demo_abromics.yaml:65` | demo_join | demo_abromics | last of 6 | sample_id, sequence_type, source, year, country | yes | demo_st_by_source |
| `templates/complex_template/master_steps.yaml:7` | master_assembly | complex_template | last of 2 | sample_id, gene_presence, country | yes | gene_presence_by_country |
| `templates/left_join_lesson.yaml:73` | lesson_assembly | left_join_lesson | last of 2 | sample_id, gene, country | yes | samples_by_country |

### (3) Kept-list steps in joined tables with no metadata

| Step | Table | Position | Keeps | Entity id | Plots |
|---|---|---|---|---|---|
| `.../QA_ST_with_NA.yaml:3` | QA_ST_with_NA (ingredient: Summary_quality) | only step | sample_id, ST | yes | qa_sequence_type_missing |
| `.../QA_L50_integer.yaml:5` | QA_L50_integer (ingredient: Quast) | first of 2 | sample_id, L50 | yes | qa_l50_integer |

### (4) Group-by steps (they rebuild the columns)

| Step | Table (tier) | Position | Groups by; computes | Entity id among the group columns? | Plots |
|---|---|---|---|---|---|
| `.../Summary_phenotype_length_fragmentation_assembly.yaml:17` | Summary_phenotype_length_fragmentation (tier 1; ingredients Summary, Summary_quality, no metadata) | 3 of 5 | sample_id, ST; phenotype_count = sum of resistance_points | yes | phenotype_genome_length_fragmentation |
| `.../QA_AMR_per_sample_tier2.yaml:4` | QA_AMR_per_sample (tier 2) | only step | sample_id, country; n_amr_genes = count of gene | yes | qa_amr_genes_per_sample |
| `.../QA_fanout_exhibit_tier2.yaml:3` | QA_fanout_exhibit (tier 2) | only step | sample_id; rows_per_sample = count of VF_gene | yes | qa_fanout_rows_per_sample |
| `.../QA_aggregated_no_key_tier2.yaml:4` | QA_aggregated_no_key (tier 2) | only step | country, year_label; n_samples = count of sample_id | **no**: after this step the table has no entity id (it is the deliberate "aggregate with no id" fixture, its file comment says so); the marker question does not arise in the same way: a marker per sample cannot survive a table with one row per country and year | qa_aggregated_no_key |

Counts: 3 + 11 + 2 + 4 = 20 [the dry-run report and this scan list the same 20 steps].

## Part C. QA_year_types and QA_aggregated_no_key "must move in the data_schema": the facts

How they are written today (`1_test_data_ST22_dummy.yaml`):
- `QA_year_types` (:265-270): a `joins:` entry, one ingredient (`metadata_schema`), tier 1 = `wrangling/QA_year_types.yaml` (one step: `polars_with_columns` year_label from year via Int64 then String), no tier 2. Plots reading it: `qa_year_label` (`plots/qa_year_label.yaml:5`, listed at recipe :344) and `qa_facet_by_mapping` (`plots/qa_facet_by_mapping.yaml:5`, recipe :346).
- `QA_aggregated_no_key` (:289-295): one ingredient (`metadata_schema`), tier 1 = `QA_aggregated_no_key_tier1.yaml` (the same year_label step), tier 2 = `QA_aggregated_no_key_tier2.yaml` (group by country, year_label, count sample_id). Plot: `qa_aggregated_no_key` (`plots/qa_aggregated_no_key.yaml:5`, recipe :348).
- So three plots in all: `plots/qa_year_label.yaml:5` and `plots/qa_facet_by_mapping.yaml:5` read `QA_year_types`; `plots/qa_aggregated_no_key.yaml:5` reads `QA_aggregated_no_key`.

Facts for a mover:
1. Two data schemas can read the same data file: `Summary` (`1_test_data_ST22_dummy.yaml:22`) and `Summary_quality` (`:33`) have the identical `source.path` `./assets/test_data/1_test_data_ST22_dummy/test_data_Summary_20260307_105756.tsv`, and both include the same `input_fields` file (:25 and :36, file `Summary_input_fields.yaml`). So a new schema on the metadata file is a pattern that exists.
2. A data schema must declare: `source` (type, path), `null_values`, `strip`, `input_fields`, `tier1` (required); `description`, `comment`, `tier2` are optional (`libs/utils/src/utils/recipe_spec.yaml:32-34`). A field needs only `type` (`:39-41`); `is_entity_key` is optional. `label` is used by the shipped schemas but is not in the spec lists above [REASONED: tolerated or handled by the names pass; not checked].
3. A data schema may have a tier 2 when a plot reads it directly; the check refuses a tier 2 on a schema no plot reads with code S07 (`recipe_check.py:415`, rule at `recipe_tiers.py:196-200`), and on a join no plot reads with J14 (`recipe_check.py:826`, `recipe_tiers.py:203-210`). Both QA tables are read by plots, so neither code would fire.
4. `schema_bodies` counts the data schemas, the additional datasets and the metadata schema as schemas (`recipe_tiers.py:112-120`), so a plot may target a schema by name (S07 text says "plotted directly").
5. What would have to be written for each (list of facts, not a proposal): `QA_year_types`: a data schema with the metadata's `source.path` (`:154`), `null_values: []`, `strip: true`, the metadata's input fields file, tier 1 = the year_label step; the 2 plots' `target_dataset` change to the new schema name; the `joins:` entry removed. `QA_aggregated_no_key`: the same schema with tier 1 = year_label step AND tier 2 = the group-by step; one plot retargeted; the `joins:` entry removed. The tests that name the two tables (`app/tests/test_qa_canaries.py`, `test_remove_from_all_demo.py`, `libs/utils/tests/test_key_candidates.py`, `test_table_compare.py`) and the notes (`.claude/knowledge/demo_deliberate_oddities.md`) name them: names of the schemas decide whether they change.
6. NOT allowed or not settled today, for her: (a) the metadata itself is a separate top-level block `metadata_schema`, not an entry of `data_schemas` (`1_test_data_ST22_dummy.yaml:149`); a new entry of `data_schemas` would be a second reading of the metadata file, not the metadata block itself. (b) Because such a schema reads the metadata file with no join, the recipe would then have a second table that is "the metadata" without being the metadata; and if the metadata file is replaced by Data Import, `ui_implementation_contract.md` section 9 step 4 requires every table reading the file to read it too: both are fine here by construction. (c) The entity id of the moved tables: the metadata declares `sample_id`; the new schema would have to declare it again (the same input fields file does that). (d) The reasons the two tables exist as joins today (their file comments: "T2 is an aggregate without sample_id", "year as a number and as a label") do not depend on the join, [REASONED].

## What surprised me

- The dry-run report and this scan list the same 20 steps.
- `2_test_data_ST22_dummy` joins the metadata by INNER join: the answer to her question is not "yes, all left".
- `AR1_MLST_Serotype_Virulence.yaml` has the same kept list twice in a row (steps 5 and 6 of 6, `:32` and `:34`).
- The three plots on the two QA tables: `plots/qa_year_label.yaml:5` and `plots/qa_facet_by_mapping.yaml:5` read `QA_year_types` (two plots); `plots/qa_aggregated_no_key.yaml:5` reads `QA_aggregated_no_key` (one plot).
