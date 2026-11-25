# Dry run of the big move

Date: 2026-11-23. Commit of the worktree: d8bb534e. Root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ

Nothing was changed. This is a list for the owner to read.

## What needs you

1. The shipped data file `assets/test_data/demo_high_integrity/test_data_test_metadata_20260307_105756.tsv` has 3 line(s) with no id. Today the recipe `demo_abromics` removes them in its join. Your order was to remove such lines from the metadata (D-0569), and the app itself does not clean data (D-0594): so the maintainers would delete these 3 line(s) from the shipped file, and the removal step and the test that count them would change with it. Confirm, or keep them as a lesson about messy data? (section 6)
2. 2 joined table(s) are made from the metadata alone; the rule 'do not start from the metadata' does not touch them. What do you want for them? (section 3)
3. 5 joined table(s) start from the metadata and are to be rewritten by hand with the data table first; the rewriting is shown in a second dry run. Nothing to decide now. (section 3)
4. 20 steps keep only a fixed list of columns and would not carry a marker column. Your two ways: add the marker column to the list, or treat the marked lines at tier 1 and drop the marker by a visible step. One way for all, or per group (3 first in their stage, 10 last, 3 elsewhere or alone, 4 group-by)? (section 4)
5. 6 table(s) of 2 recipe(s) declare no entity id, but a column named like an id exists (a candidate, not a decision); 2 table(s) have no id column at all (reference tables). Which column is the id of each? (section 5)
6. The Gallery examples declare no entity id: 20 have no id column, 14 have a column named `id`. Do they need one? (section 5, annex)
7. Tables under `additional_datasets_schemas` that declare the entity id: 2; to be moved under the data schemas (your earlier point). (section 7)
8. 3 names that no rule covers (listed in section 1): Comments that name an old key (a person must reword them); Display-like keys that no decision names (for example `info.subtitle`).

Only a mechanical rename, no decision: the names pass (524 changes) and `is_entity_key` to `is_entity_id` (225 lines, not counting 11 line(s) in the dry-run tool's own files).

## Count per section

- 6. Metadata lines with no usable id (D-0569, D-0594): 3 metadata line(s) with no usable id
- 3. Joined tables that start from the metadata (D-0586): 7 joined table(s) (5 start from the metadata, 2 are made from it alone)
- 4. Steps that keep only a list of columns (D-0586, D-0587): 20 step(s)
- 5. Tables with no entity id declared (D-0569): 8 table(s) (and 34 Gallery examples in the annex)
- 7. Tables under `additional_datasets_schemas` that declare the entity id: 2 table(s)
- 2. `is_entity_key` becomes `is_entity_id` (mechanical, D-0562, D-0567): 225 line(s)
- 1. The names pass (mechanical): 524 change(s)

## 6. Metadata lines with no usable id (D-0569, D-0594)

Ledger D-0569 and D-0594. For each recipe with a metadata table: the lines of its data file where the id cell is empty, only spaces, or a missing-value mark that the recipe declares. The file is read as text, not by the engine; each cell is shown as written in the file. Then it says which steps of the recipe already remove such lines. The move would remove these lines from the metadata itself.

* recipe `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml`, file `assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv`, id column `sample_id` (the declared id), missing-value marks declared: ['', '-']: 0 line(s) with no usable id. Who removes them today: the metadata's own steps do not remove them; the join `AR1_MLST_Serotype_Virulence` does not.
* recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, file `assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv`, id column `sample_id` (the declared id), missing-value marks declared: ['', '-']: 0 line(s) with no usable id. Who removes them today: the metadata's own steps do not remove them; the joins `FastP_with_metadata`, `Quast_with_metadata`, `Bracken_with_metadata`, `ResFinder_with_metadata`, `MLST_with_metadata`, `QC_Reads_Anchor`, `ST22_Anchor`, `AR1_MLST_Serotype_Virulence`, `QA_AMR_per_sample`, `QA_year_types`, `QA_fanout_exhibit`, `QA_aggregated_no_key`, `QA_population_zscore` do not.
* recipe `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`, file `assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv`, id column `sample_id` (a candidate by name, no id is declared), missing-value marks declared: none: 0 line(s) with no usable id. Who removes them today: the metadata's own steps do not remove them; the joins `AMR_Profile_Joint`, `Plasmid_Profile_Joint` do not.
* recipe `config/data_analysis_recipes/pipelines/demo_abromics.yaml`, file `assets/test_data/demo_high_integrity/test_data_test_metadata_20260307_105756.tsv`, id column `sample_id` (the declared id), missing-value marks declared: ['', '-']: 3 line(s) with no usable id. Who removes them today: the metadata's own steps do not remove them; the join `demo_join` removes them (config/data_analysis_recipes/pipelines/demo_abromics.yaml:46 which drops the rows with a missing value in [sample_id]).
- assets/test_data/demo_high_integrity/test_data_test_metadata_20260307_105756.tsv:5: the id cell is (empty).
- assets/test_data/demo_high_integrity/test_data_test_metadata_20260307_105756.tsv:6: the id cell is `-` (a dash, a declared missing-value mark).
- assets/test_data/demo_high_integrity/test_data_test_metadata_20260307_105756.tsv:11: the id cell is `""` (two quote marks, read as empty).
* recipe `config/data_analysis_recipes/templates/complex_template.yaml`, file `assets/test_data/metadata.tsv`, id column `ID` (the declared id), missing-value marks declared: none: 0 line(s) with no usable id. Who removes them today: the metadata's own steps do not remove them; the join `master_assembly` does not.
* recipe `config/data_analysis_recipes/templates/e_coli.yaml`: the data file `./assets/pipeline_output/ecoli_metadata.tsv` was not found in this tree; not read.
* recipe `config/data_analysis_recipes/templates/left_join_lesson.yaml`, file `assets/test_data/left_join_lesson/left_join_lesson_metadata.tsv`, id column `ID` (the declared id), missing-value marks declared: none: 0 line(s) with no usable id. Who removes them today: the metadata's own steps do not remove them; the join `lesson_assembly` does not.
* recipe `config/data_analysis_recipes/templates/simple_template.yaml`: the data file `./assets/test_data/simple_metadata.tsv` was not found in this tree; not read.

## 3. Joined tables that start from the metadata (D-0586)

Ledger D-0586. In these joined tables the FIRST table is the metadata. The rule is that a recipe does not start from the metadata: the table is to be rewritten with the data table first; the metadata is then added to it, keeping every row of the data table. The rewriting is written by hand and shown in a second dry run (it depends on the completion of the ids, which is not built). Each line gives the joined table, its tables in order, and what its join steps do today.

- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:223: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, joined table `ST22_Anchor`. Tables in order: metadata_schema, FastP, ResFinder, MLST, VirulenceFinder, APEC_STEC_virulence_genes. Join steps today: a join with `FastP` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:5); a join with `ResFinder` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:11); a join with `MLST` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:17); a join with `VirulenceFinder` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:23); a join with `APEC_STEC_virulence_genes` that keeps only the rows found in both tables (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:30).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:249: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, joined table `QA_AMR_per_sample`. Tables in order: metadata_schema, ResFinder. Join steps today: a join with `ResFinder` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier1.yaml:5).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:279: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, joined table `QA_fanout_exhibit`. Tables in order: metadata_schema, ResFinder, VirulenceFinder. Join steps today: a join with `ResFinder` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier1.yaml:4); a join with `VirulenceFinder` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier1.yaml:9).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:297: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, joined table `QA_population_zscore`. Tables in order: metadata_schema, Quast. Join steps today: a join with `Quast` that keeps every row of the first table (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_population_zscore_tier1.yaml:6).
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:35: recipe `config/data_analysis_recipes/pipelines/demo_abromics.yaml`, joined table `demo_join`. Tables in order: metadata_schema, MLST. Join steps today: a join with `MLST` that keeps every row of the first table (config/data_analysis_recipes/pipelines/demo_abromics.yaml:49).

Joined tables made from the metadata alone:
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:265: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, joined table `QA_year_types` is made from the metadata alone: it joins nothing. The rule does not touch it; the owner's point.
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:289: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, joined table `QA_aggregated_no_key` is made from the metadata alone: it joins nothing. The rule does not touch it; the owner's point.

## 4. Steps that keep only a list of columns (D-0586, D-0587)

Ledger D-0586 and D-0587. A step that keeps only the listed columns (`polars_select`), or a step that groups the rows and keeps the group columns and the computed totals (`polars_group_by`), does not carry any other column that exists before it. A marker column added before such a step would be lost at that step, wherever the step stands in its stage (tier 1 is the first stage of a table, tier 2 the second): first, last or between. Each line says where, for example "the first step of 10 in that stage". A tier file that several recipes include is listed once, with every recipe that uses it. What this section does NOT cover: a step that only removes named columns (`polars_drop`) keeps all the others and is not listed; other steps that rebuild the columns (pivot, unpivot and similar) are NOT examined here, because no reliable list in the project says which actions do it (libs/utils/src/utils/step_effects.py reads only the select and the group-by).

- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml:2: used by 4 recipes: `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml` (table `MLST`, tier1), `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` (table `MLST`, tier1), `config/data_analysis_recipes/pipelines/3_test_no_joins.yaml` (table `MLST`, tier1), `config/data_analysis_recipes/pipelines/demo_abromics.yaml` (table `MLST`, tier1). The first step of 3 in that stage: `polars_select` keeps only [sample_id, scheme, sequence_type].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/VirulenceFinder_wrangling.yaml:2: used by 2 recipes: `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml` (table `VirulenceFinder`, tier1), `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` (table `VirulenceFinder`, tier1). The first step of 10 in that stage: `polars_select` keeps only [sample_id, serotype, virulence_raw].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml:32: used by 2 recipes: `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml` (table `AR1_MLST_Serotype_Virulence`, tier1), `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` (table `AR1_MLST_Serotype_Virulence`, tier1). Step 5 of 6 in that stage: `polars_select` keeps only [sample_id, source, year, country, sequence_type, serotype, selected_virulence_genes, vf_protein].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml:34: used by 2 recipes: `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml` (table `AR1_MLST_Serotype_Virulence`, tier1), `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` (table `AR1_MLST_Serotype_Virulence`, tier1). The last step of 6 in that stage: `polars_select` keeps only [sample_id, source, year, country, sequence_type, serotype, selected_virulence_genes, vf_protein].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:17: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `Summary_phenotype_length_fragmentation`, tier1. Step 3 of 5 in that stage: `polars_group_by` groups the rows by [sample_id, ST] and keeps the totals ['phenotype_count'].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml:46: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `ST22_Anchor`, tier1. The last step of 8 in that stage: `polars_select` keeps only [sample_id, source, year, country, sequence_type, serotype, Selected_Virulence_Genes, VF_protein, gene, status, phenotype].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier1.yaml:10: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_AMR_per_sample`, tier1. The last step of 2 in that stage: `polars_select` keeps only [sample_id, country, source, year, gene, predicted_phenotype].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier2.yaml:4: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_AMR_per_sample`, tier2. The only step in that stage: `polars_group_by` groups the rows by [sample_id, country] and keeps the totals ['n_amr_genes'].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_ST_with_NA.yaml:3: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_ST_with_NA`, tier1. The only step in that stage: `polars_select` keeps only [sample_id, ST].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_L50_integer.yaml:5: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_L50_integer`, tier1. The first step of 2 in that stage: `polars_select` keeps only [sample_id, L50].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier1.yaml:14: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_fanout_exhibit`, tier1. The last step of 3 in that stage: `polars_select` keeps only [sample_id, country, gene, VF_gene].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier2.yaml:3: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_fanout_exhibit`, tier2. The only step in that stage: `polars_group_by` groups the rows by [sample_id] and keeps the totals ['rows_per_sample'].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key_tier2.yaml:4: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_aggregated_no_key`, tier2. The only step in that stage: `polars_group_by` groups the rows by [country, year_label] and keeps the totals ['n_samples'].
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_population_zscore_tier1.yaml:11: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `QA_population_zscore`, tier1. The last step of 2 in that stage: `polars_select` keeps only [sample_id, country, n50].
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:49: recipe `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`, table `AMR_Profile_Joint`, tier1. The last step of 8 in that stage: `polars_select` keeps only [Year, Source, Country, gene, predicted_phenotype_clean, sample_id, accession, Multiresistant].
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/Plasmid_Profile_Joint.yaml:29: recipe `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`, table `Plasmid_Profile_Joint`, tier1. The last step of 5 in that stage: `polars_select` keeps only [Year, Source, Country, plasmid_name, sample_id, accession].
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:65: recipe `config/data_analysis_recipes/pipelines/demo_abromics.yaml`, table `demo_join`, tier1. The last step of 6 in that stage: `polars_select` keeps only [sample_id, sequence_type, source, year, country].
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:28: recipe `config/data_analysis_recipes/retest/retest_bad_select_column.yaml`, table `Genes`, tier1. The only step in that stage: `polars_select` keeps only [sample_id, gene, phenotype].
- config/data_analysis_recipes/templates/complex_template/master_steps.yaml:7: recipe `config/data_analysis_recipes/templates/complex_template.yaml`, table `master_assembly`, tier1. The last step of 2 in that stage: `polars_select` keeps only [sample_id, gene_presence, country].
- config/data_analysis_recipes/templates/left_join_lesson.yaml:73: recipe `config/data_analysis_recipes/templates/left_join_lesson.yaml`, table `lesson_assembly`, tier1. The last step of 2 in that stage: `polars_select` keeps only [sample_id, gene, country].

## 5. Tables with no entity id declared (D-0569)

Ledger D-0569. Tables that have no column marked as the entity id (`is_entity_key` today). Where a column is named like an id (for example `sample_id`) it is shown as a candidate: a name only, not a decision. A table with no such column is a table with no id column. The Gallery examples are counted here and listed in the annex at the end.

- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:54: recipe `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml`, table `APEC_STEC_virulence_genes`: no id declared and no column with an id-like name (no id column).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:135: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `APEC_STEC_virulence_genes`: no id declared and no column with an id-like name (no id column).
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:23: recipe `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`, table `metadata_schema`: no id declared; a column named `sample_id` exists: a candidate, not a decision.
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:35: recipe `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`, table `amr_data`: no id declared; a column named `sample_id`, `accession` exists: a candidate, not a decision.
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:45: recipe `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml`, table `plasmid_data`: no id declared; a column named `sample_id`, `accession` exists: a candidate, not a decision.
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:23: recipe `config/data_analysis_recipes/pipelines/figshare_integration.yaml`, table `fg_metadata`: no id declared; a column named `sample_id` exists: a candidate, not a decision.
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:34: recipe `config/data_analysis_recipes/pipelines/figshare_integration.yaml`, table `fg_phenotypes`: no id declared; a column named `sample_id` exists: a candidate, not a decision.
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:45: recipe `config/data_analysis_recipes/pipelines/figshare_integration.yaml`, table `fg_genotypes`: no id declared; a column named `sample_id` exists: a candidate, not a decision.

* Gallery examples with no id declared: 20 have no id column, 14 have a column named like an id (annex).

## 7. Tables under `additional_datasets_schemas` that declare the entity id

Ledger: none given (the owner's earlier point). Tables registered under `additional_datasets_schemas` that declare an entity id. The owner's earlier point: they are to be moved under the data schemas (listed only).

- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:44: recipe `config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml`, table `VirulenceFinder` declares the entity id (sample_id) under `additional_datasets_schemas`.
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:124: recipe `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, table `VirulenceFinder` declares the entity id (sample_id) under `additional_datasets_schemas`.

## Needs the owner (every place where no rule decides)

- section 1: 3 place(s) listed by the names pass under 'CANNOT BE DECIDED BY THE SCRIPT' (read them in section 1)
- section 3: 2 joined table(s) are made from the metadata alone: the rule does not touch them (the owner's point)
- section 4: which of her two ways (D-0587) each of these steps takes is not decided by any rule
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:54: table `APEC_STEC_virulence_genes`: has no id column: a reference table, or a declaration for the owner
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:135: table `APEC_STEC_virulence_genes`: has no id column: a reference table, or a declaration for the owner
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:23: table `metadata_schema`: no id declared; candidate by name: sample_id
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:35: table `amr_data`: no id declared; candidate by name: sample_id, accession
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:45: table `plasmid_data`: no id declared; candidate by name: sample_id, accession
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:23: table `fg_metadata`: no id declared; candidate by name: sample_id
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:34: table `fg_phenotypes`: no id declared; candidate by name: sample_id
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:45: table `fg_genotypes`: no id declared; candidate by name: sample_id
- config/data_analysis_recipes/templates/e_coli.yaml: the metadata data file `./assets/pipeline_output/ecoli_metadata.tsv` does not exist in this tree
- config/data_analysis_recipes/templates/simple_template.yaml: the metadata data file `./assets/test_data/simple_metadata.tsv` does not exist in this tree
- The Gallery examples: 20 have no id column and 14 have a column named `id`, none declared as the entity id (the full list is in the annex).

## 2. `is_entity_key` becomes `is_entity_id` (mechanical, D-0562, D-0567)

A mechanical rename: no decision for her; listed so that she can see every place.

Ledger D-0562 and D-0567. The column mark `is_entity_key` would be renamed `is_entity_id` everywhere it is written. This is a text rename: the lines are listed, none is changed. Without the files of this dry-run tool there are 225 lines. Lines per kind of file:
* code: 29 line(s) in 12 file(s)
* docs and design notes: 95 line(s) in 39 file(s)
* input_fields file: 11 line(s) in 11 file(s)
* other: 2 line(s) in 2 file(s)
* recipe or template file: 14 line(s) in 10 file(s)
* rules: 2 line(s) in 2 file(s)
* tests: 70 line(s) in 37 file(s)
* the specification (recipe_spec.yaml): 2 line(s) in 1 file(s)
* the dry-run tool itself (it names the old key on purpose; it is updated when the rename is applied): 11 line(s) in 3 file(s), listed apart and not counted above

- .claude/design/adr_100_recipe_format_1_draft.md:66 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| 10 | `is_primary_key` becomes `is_entity_key` | DEC13 | BUILT: `recipe_spec.yaml`:82, `recipe_check.py`:353. One fragment that no recipe i`
- .claude/design/blueprint_revision/04_what_blueprint_must_be.md:145 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| `entity`, `is_entity_key` on the sample id; the id is text | D-0029, D-0225 | No control | read-1 |`
- .claude/design/blueprint_revision/prior_work/GAP_REPORT_full_part1.md:49 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `37. Entity key: each recipe declares its entity key (is_entity_key, D-0082, DECIDED; line 111) and the entity block (D-0029, DECIDED; line 5`
- .claude/design/blueprint_revision/prior_work/GAP_REPORT_full_part2.md:26 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- input_fields: no writer in Blueprint (grep). Fields are read (load_fields_file navigator.py:451; blueprint_handlers.py:668). Field spec: t`
- .claude/design/blueprint_revision/prior_work/GAP_REPORT_full_part4.md:13 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `R5 Entity block and entity key (is_entity_key) | D-0082 (line 111), D-0029 (line 58), DECIDED | NOT BUILT (grep: no writer) | declare the en`
- .claude/design/blueprint_revision/prior_work/GAP_REPORT_full_part4.md:64 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- entity block and is_entity_key: in the ledger (D-0029, D-0082), not in the Blueprint design files read. Marked: ledger only.`
- .claude/design/decisions_2026-11-14/evidence/records_corrections.md:44 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `C3. ADR-099 (`architecture_decisions.md`): point 15 (line 5023) ends "Which samples a selector finds, the check on the plotted variable, the`
- .claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md:150 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| R081 | rules_test_lab.md | 133 | "input_fields with inferred types" | "... inferred Polars types, label, original_name; is_entity_key on i`
- .claude/design/decisions_2026-11-14/rule_file_proposals/rules_test_lab.md.proposal.md:11 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `Proposed: `| \`input_fields:\` with inferred Polars types, \`label\`, \`original_name\` | Yes | From TSV headers + sampling; \`is_entity_key`
- .claude/design/exploration/2026-11-17_data_scientist_checks_keys_and_formula_members.md:51 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- `:43`, `:56`: `{type: String, is_entity_key: true}`. This is the current vocabulary.`
- .claude/design/exploration/2026-11-17_data_scientist_checks_keys_and_formula_members.md:84 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- The `ui_implementation_contract.md` audit key set comes from join keys (`session_manager.py:124-150`), not from `is_entity_key`. So the ke`
- .claude/design/exploration/2026-11-18_date_keys_and_joins.md:73 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **E03.** Refuses a field marked `is_entity_key: true` whose declared type is numeric (`recipe_check.py:364-379`). Date, Datetime, Boolean,`
- .claude/design/exploration/2026-11-18_date_keys_and_joins.md:75 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **Where `is_entity_key` is read.** Written by `recipe_factory.py:79`, `test_lab/bootstrapper.py:123`, `test_lab/scaffolder.py:157`; read b`
- .claude/design/exploration/2026-11-18_date_keys_and_joins.md:135 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `Today two sources: the audit protects names found in join steps (`session_manager.py:119-146`), the checker uses `is_entity_key`. Options:`
- .claude/design/exploration/2026-11-18_date_keys_and_joins.md:136 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **K1: keep two sources, make them agree by a checker rule.** Every column that is `is_entity_key` must appear as a key in at least one joi`
- .claude/design/exploration/2026-11-18_date_keys_and_joins.md:137 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **K2 (my pick): the recipe declares the entity key (`is_entity_key`); the audit protects the entity keys plus every column used in a join `
- .claude/design/exploration/2026-11-18_date_keys_and_joins.md:138 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **K3: derive the join keys from `is_entity_key` only (joins stop naming keys).** Con: breaks joins on non-entity keys (gene id in long tab`
- .claude/design/exploration/2026-11-18_step_split_wide_design.md:322 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `The prototype names a cell by its row number and its text. Naming the sample id would need the step to know the table's key (`is_entity_key``
- .claude/design/exploration/2026-11-18_test_lab_review.md:68 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **The id column becomes `Int64` and loses leading zeros.** The types are guessed from the first 100 rows with Polars' default reader (`sca`
- .claude/design/exploration/2026-11-18_test_lab_review.md:77 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **The name-based entity key.** `scaffolder.py:156` and `bootstrapper.py:122` mark a column as `is_entity_key` when its slug is `id`, `samp`
- .claude/design/exploration/2026-11-18_test_lab_review.md:164 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `5. **The entity key is the one the user names, not a column with a certain name.** After: the key column is marked `is_entity_key`; nothing `
- .claude/design/home_audit_reading_guide.md:111 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| O9 | Rename the recipe field `is_primary_key` to `is_entity_key` (a primary key is unique, an entity key repeats in long tables); warn fir`
- .claude/design/home_audit_steps.md:39 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| **Key** (entity ID) | The column that identifies the entity (for example `sample_id`), **declared with `is_primary_key: true`** in the dat`
- .claude/design/home_audit_steps.md:160 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `A key is not a database primary key: in a long table it repeats, it only identifies the entity. Renaming the recipe field `is_primary_key` t`
- .claude/design/home_evidence/home_test_inventory_2026-11-13.md:30 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| **Adapt** (names only, mechanical) | the 12 files that mention `is_primary_key` (`test_bundle_importer`, `test_cache_chain`, `test_cache_k`
- .claude/design/lab_revision/02_planned_vs_existing.md:51 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| The entity key | the key the user names (`TEST_LAB.md:331-335`); "nothing is guessed from a column name" (`recipe_check.py:448-449`, E03 t`
- .claude/design/lab_revision/04_what_test_lab_must_be.md:198 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| F5 | The entity key is declared by the person who makes the recipe, not guessed | D-0082 "Keys are declared in the recipe"; D-0216 "Import`
- .claude/design/outdated/recipe_format_review_2026-11-13.md:26 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| D9 | `is_primary_key` becomes `is_entity_key` (warn first, refuse later) | **CONFIRM/OPEN**: the guide lists it as my recommendation; the `
- .claude/design/outdated/recipe_format_review_2026-11-13.md:104 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **Q4. `is_primary_key` to `is_entity_key` now?** *I recommend now*: 29 schemas and about 50 files are touched anyway, a second sweep costs`
- .claude/design/outdated/recipe_format_spec_v0.8_2026-11-13.md:91 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `5. `is_primary_key` becomes `is_entity_key`.`
- .claude/design/outdated/recipe_format_spec_v0.8_2026-11-13.md:341 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| `is_entity_key` | o | `true` when the column identifies the entity (it repeats in long tables). Replaces `is_primary_key`. `[DECIDED]` |`
- .claude/design/outdated/recipe_format_spec_v0.8_2026-11-13.md:478 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| FD03 | E | `is_primary_key` | `is_entity_key` |`
- .claude/design/outdated/recipe_format_spec_v0.8_2026-11-13.md:480 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| FD05 | E | `is_entity_key` not true/false; `categories` not a list of text | |`
- .claude/design/outdated/recipe_format_spec_v0.8_2026-11-13.md:534 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| field | `is_primary_key` | `is_entity_key` |`
- .claude/design/outdated/recipe_format_st22_draft.yaml:8 (other): `is_entity_key` becomes `is_entity_id`. Now: `# `is_primary_key` -> `is_entity_key`, spec keys removed). Include paths below are those of the current recipe.`
- .claude/design/recipe_format_spec.md:45 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {type: String, is_entity_key: true}`
- .claude/design/recipe_format_spec.md:59 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `input_fields: {sample_id: {type: String, is_entity_key: true}}`
- .claude/design/recipe_format_spec.md:117 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| DEC13 | `is_primary_key` becomes `is_entity_key` | a generic word: the format knows no field-specific term | 2026-11-13 | 4 |`
- .claude/design/recipe_format_spec.md:409 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| `is_entity_key` | o | `true` when the column identifies the entity (it repeats in long tables) |`
- .claude/design/recipe_format_spec.md:669 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| E03 | E | a field marked `is_entity_key` (the sample id) has a number type (an integer, a float or a decimal); D-0225, D-0067 | declare it`
- .claude/design/recipe_format_spec.md:681 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| FD03 | E | `is_primary_key` | `is_entity_key` |`
- .claude/design/recipe_format_spec.md:683 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| FD05 | E | `is_entity_key` not true/false; `categories` missing for `Enum` or not a list of text; `precision`, `scale`, `format`, `time_un`
- .claude/design/recipe_format_spec.md:761 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| field | `is_primary_key` | `is_entity_key` |`
- .claude/design/spaces/TEST_LAB.md:410 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/spaces/TEST_LAB.md:457 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md:829 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **On the demo (case 2):** after the completion ResFinder holds 38 + 4 = 42 ids, and so does every other table that declares the entity id `
- .claude/design/studies/whole_picture_2026-11/DESIGN_AGREED_AND_QUESTIONS.md:147 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `**G12 No new recipe key.** The recipe already declares the blocks, the ingredients and their order, the tiers, the plot targets, `entity.pop`
- .claude/design/studies/whole_picture_2026-11/OVERLAP_AND_POPULATION.md:40 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `Registered first: `RUN_REGISTER_sonnet_overlap.md`, O1, with its three points. The script reads the source files with a plain reader (polars`
- .claude/design/studies/whole_picture_2026-11/PARTS_TABLES.md:13 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- Words: the **entity key** is the column the recipe declares with `is_entity_key` (D-0313; "remember we are data agnostic so sample id is t`
- .claude/design/studies/whole_picture_2026-11/RECIPES_FROM_THE_MODEL_AGREED.md:3 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `**What this is.** Step 2 of her sequence (ledger D-0554): "how to build the recipes from the directed-graph model". It carries her decision `
- .claude/design/studies/whole_picture_2026-11/RECIPES_FROM_THE_MODEL_AGREED.md:65 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| G15 The rename `is_entity_key` to `is_entity_id` | STILL TRUE (decided, not done) | D-0562, D-0567 |`
- .claude/design/studies/whole_picture_2026-11/RECIPES_FROM_THE_MODEL_AGREED.md:106 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `8. The rename `is_entity_key` to `is_entity_id` touches 10 files of the demo (11 tables), 21 recipe files, and 111 tracked files in all (218`
- .claude/design/studies/whole_picture_2026-11/RECIPES_FROM_THE_MODEL_AGREED.md:261 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `**G15. The rename `is_entity_key` to `is_entity_id`** [HER WORDS D-0562: "I think is_entity_id for all cases"], in one move by a script (D-0`
- .claude/design/studies/whole_picture_2026-11/RECIPES_FROM_THE_MODEL_AGREED.md:292 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| `is_entity_key` becomes `is_entity_id` | G15, one move | YES (decided) | 10 files of `1_test_data_ST22_dummy/input_field`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_answers.md:133 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| `is_entity_key: true` | field | unchanged | D-0313, D-0082 |`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:119 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:155 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:274 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:312 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:458 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:496 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:646 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:684 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:832 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/RECIPE_PROPOSAL_refined.md:862 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- .claude/design/studies/whole_picture_2026-11/WHOLE_PICTURE.md:643 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {original_name: sample_id, type: String, is_entity_key: true}`
- .claude/design/studies/whole_picture_2026-11/WHOLE_PICTURE.md:654 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {original_name: sample_id, type: String, is_entity_key: true}`
- .claude/knowledge/architecture_decisions.md:90 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `> **Partly stale (2026-11-14, ADR-SYNC-1):** never accepted; `join_on` is now `on` or `left_on`/`right_on`, `is_primary_key` is now `is_enti`
- .claude/knowledge/architecture_decisions.md:5075 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `> - **Keys of entities:** declared, never guessed (point 6), but the key is information, not mechanism (point 16(i), ADR-105); the field is `
- .claude/knowledge/architecture_decisions.md:5119 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `6. **[HISTORICAL in part: the field is now `is_entity_key` (ADR-100, DEC13); the key is information, not a mechanism of removal, and a key-l`
- .claude/knowledge/architecture_decisions.md:5214 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `2. **Strict file shape.** Unknown keys fail; old names are refused at once and the message names the new one; no compatibility default (DEC0`
- .claude/knowledge/decision_ledger.md:63 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `D-0034 | 2026-11-13 | recipe format | DEC13-26: `is_entity_key`; aliases removed; one name per role (`columns`); schema's own tier2 applied;`
- .claude/knowledge/decision_ledger.md:482 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `D-0448 | 2026-11-21 | HOME audit: the drop of a declared entity key (lineage question O6, the part left open) | Her answer: B, to the review`
- .claude/knowledge/decision_ledger.md:534 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `D-0500 | 2026-11-22 | HOME audit, "remove from all the data": what counts as the sample key: option B (the declared entity key and a column `
- .claude/knowledge/decision_ledger.md:546 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `D-0512 | 2026-11-22 | The app is data agnostic: "sample" and "sample id" are examples, the word is the entity and the entity key; the kinds `
- .claude/knowledge/decision_ledger.md:596 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `D-0562 | 2026-11-23 | Her decision: the recipe field is_entity_key is renamed is_entity_id, one name for all cases; a new open topic, joins `
- .claude/knowledge/decision_ledger.md:664 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- M224 (2026-11-17, entity declaration, item 3 of the list of M170, NOT her words): the review session reads her answer as "yes"; she did no`
- .claude/logs/handoffs/handoff_active.md:9 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `A. Her orders of 2026-11-23, each a ledger line: D-0534 (BLUEPRINT: a duplicate plot id must be fixed; plot ids unique across recipes enforc`
- .claude/logs/handoffs/handoff_active.md:895 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `**Eve's answers (2026-11-13):** the format applies to EVERY recipe (app and tests, transformer test recipes, gallery, writers); unknown keys`
- .claude/rules/rules_data_analysis_recipe_structure.md:211 (rules): `is_entity_key` becomes `is_entity_id`. Now: `**Primary key rule:** the sample id is a string or a categorical, never a number: a number gives join and type problems (it loses leading ze`
- .claude/rules/ui_implementation_contract.md:697 (rules): `is_entity_key` becomes `is_entity_id`. Now: `**DECIDED, not built as described here (D-0313, D-0082):** both lists exist and are named differently: "the entity key" (declared in the rec`
- .claude/tasks/outdated/tasks_before_sort_2026-11-13.md:85 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **RECIPE-FORMAT-1** `[opus/high]` — the recipe-format step, after UNKNOWN-KEYS-1 (otherwise new keys are ignored silently): required ``
- .claude/tasks/tasks.md:170 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **RECIPE-FORMAT-1** `[opus/high]` — the recipe-format step, after UNKNOWN-KEYS-1 (otherwise new keys are ignored silently): required ``
- .claude/tasks/tasks.md:529 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **ENTITY-DECL-SHIPPED-1** `[sonnet/medium]` — open; the "yes" of channel M224 is the review session's reading, not her words, and exem`
- .claude/tasks/tasks.md:573 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **SAMPLE-ID-FOLLOWUPS-ASK-EVE** `[sonnet/low]` [records] — questions for Eve, no build: (a) should a Date or Boolean entity key also b`
- .claude/tasks/tasks.md:938 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- 2026-11-23: D-0562: the recipe field `is_entity_key` becomes `is_entity_id` (unique = a key; not unique = the reference to the entity used`
- .claude/tasks/tasks.md:944 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **AUDIT-REMOVE-FROM-ALL-DATA** `[sonnet/high]` (owner, 2026-11-21, ledger `D-0414` as corrected by `D-0415`; Step 1 DONE 2026-11-21: m`
- .claude/tasks/tasks.md:952 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **RECIPE-RULE-ONE-NAME-ONE-MEANING** `[sonnet/medium]`: her rule for recipe making (D-0498): do not use the same column name for diffe`
- .claude/tasks/tasks.md:961 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **NAMES-UI-LABEL-EVERYWHERE** `[sonnet/high]` (owner's decision D-0409, 2026-11-21; built with the one pass of D-0407, NOT started: th`
- .claude/tasks/tasks.md:1001 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [ ] **DOCS-JOINS-AND-KEY-PAGES-DISAGREE** `[sonnet/medium]` (found 2026-11-23 by the review of the good-practice page; ledger D-0486: "the`
- app/modules/wrangle_studio.py:1334 (code): `is_entity_key` becomes `is_entity_id`. Now: `is_pk       = meta.get("is_entity_key", False)`
- app/tests/home_harness.py:52 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: String, label: Sample, is_entity_key: true}}`
- app/tests/home_harness.py:61 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: String, label: Sample, is_entity_key: true}}`
- app/tests/test_build_failure_names.py:60 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: String, label: Sample, is_entity_key: true}}`
- app/tests/test_bundle_importer.py:44 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: Categorical, label: Sample, is_entity_key: true}}`
- app/tests/test_cache_chain.py:69 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: Categorical, label: Sample, is_entity_key: true}}`
- app/tests/test_checker_advice_visible.py:35 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"""The key is the sample id (is_entity_key): a number there is refused by E03 (D-0225). J13 itself stays an advice and refuses nothing."""`
- app/tests/test_column_names_through_the_steps.py:56 (tests): `is_entity_key` becomes `is_entity_id`. Now: `'      sample_id: {original_name: "Sample ID", type: String, is_entity_key: true}',`
- app/tests/test_column_names_through_the_steps.py:62 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"      sample_id: {type: String, is_entity_key: true}",`
- app/tests/test_data_import_check.py:37 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: Sample ID, type: String, label: Sample, is_entity_key: true}}`
- app/tests/test_data_import_check.py:46 (tests): `is_entity_key` becomes `is_entity_id`. Now: `id: {{type: String, label: Id, is_entity_key: true}}`
- app/tests/test_data_import_check.py:54 (tests): `is_entity_key` becomes `is_entity_id`. Now: `id: {{type: String, label: Id, is_entity_key: true}}`
- app/tests/test_dataset_lookup_one.py:46 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: Categorical, label: Sample, is_entity_key: true}}`
- app/tests/test_export_unread_tables.py:53 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: Categorical, label: Sample, is_entity_key: true}}`
- app/tests/test_left_join_lesson.py:5 (tests): `is_entity_key` becomes `is_entity_id`. Now: `table (`is_entity_key`, the two tables name it with different columns), it runs through the real path, the left join keeps`
- app/tests/test_left_join_lesson.py:82 (tests): `is_entity_key` becomes `is_entity_id`. Now: `keys = [(slug, f["original_name"]) for slug, f in table["input_fields"].items() if f.get("is_entity_key")]`
- app/tests/test_left_join_lesson.py:83 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert len(keys) == 1, f"{name} must declare exactly one is_entity_key field"`
- app/tests/test_migrate_recipe_engine_keys.py:29 (tests): `is_entity_key` becomes `is_entity_id`. Now: `id: {type: String, is_entity_key: true}`
- app/tests/test_orchestrator_fails_loudly.py:83 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: {left_type}, label: Sample, is_entity_key: true}}`
- app/tests/test_recipe_data_one_set_of_ids.py:48 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"the id column is the one the recipe declares with is_entity_key (Accession and ID), not a name guess",`
- app/tests/test_recipe_data_one_set_of_ids.py:78 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"""The file column that holds the sample id: the field declared `is_entity_key`, else the field `sample_id`."""`
- app/tests/test_recipe_data_one_set_of_ids.py:81 (tests): `is_entity_key` becomes `is_entity_id`. Now: `if isinstance(spec, dict) and spec.get("is_entity_key"):`
- app/tests/test_recipe_data_one_set_of_ids.py:262 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert tables["sequenced"][1] == "Accession" and tables["metadata_schema"][1] == "ID", "the declared is_entity_key columns"`
- app/tests/test_recipe_pictures.py:76 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: Categorical, label: Sample, is_entity_key: true}}`
- app/tests/test_resfinder_abromics_fragment.py:54 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: String, is_entity_key: true}}`
- app/tests/test_schema_tier2.py:75 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: String, label: Sample, is_entity_key: true}}`
- app/tests/test_table_keys.py:74 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"sample_id": {"original_name": "sample_id", "type": "Categorical", "label": "Sample", "is_entity_key": True},`
- app/tests/test_table_keys.py:499 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"sample_id": {"original_name": "sample_id", "type": "Categorical", "label": "Sample", "is_entity_key": True},`
- app/tests/test_tier3_reader.py:91 (tests): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {{original_name: sample_id, type: String, label: Sample, is_entity_key: true}}`
- app/tests/test_writers_emit_format_one.py:245 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert samples["input_fields"]["sample_id"]["is_entity_key"] is True`
- app/tests/test_writers_emit_format_one.py:246 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert "is_entity_key" not in samples["input_fields"]["country"]`
- app/tests/test_writers_emit_format_one.py:248 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert raw["metadata_schema"]["input_fields"]["sample_id"]["is_entity_key"] is True`
- app/tests/test_writers_emit_format_one.py:292 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert fields["sample_id"] == {"type": "String", "original_name": "Sample ID", "label": "Sample Id", "is_entity_key": True}`
- app/tests/test_writers_emit_format_one.py:349 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert not [name for name, field in fields.items() if "is_entity_key" in field]`
- app/tests/uncertain_drop_world.py:58 (tests): `is_entity_key` becomes `is_entity_id`. Now: `fields = {c: {"original_name": c, "type": "Int64" if tables[name][c].dtype == pl.Int64 else "String", "label": c, **({"is_entity_key": True}`
- assets/scripts/create_data_analysis_recipe.py:18 (code): `is_entity_key` becomes `is_entity_id`. Now: `- a column named by --primary_key_data is marked `is_entity_key: true`; a table without such a column is written`
- assets/scripts/create_data_analysis_recipe.py:123 (code): `is_entity_key` becomes `is_entity_id`. Now: `field["is_entity_key"] = True`
- assets/scripts/create_data_analysis_recipe.py:238 (code): `is_entity_key` becomes `is_entity_id`. Now: `"file the first name found is marked is_entity_key.")`
- assets/scripts/make_left_join_lesson_data.py:15 (code): `is_entity_key` becomes `is_entity_id`. Now: `recipe declares which column is the sample id (`is_entity_key`), it is not guessed from a name.`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:8 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:5 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:6 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:4 (input_fields file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:23 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {original_name: sample_id, type: String, label: Sample, is_entity_key: true}`
- config/data_analysis_recipes/retest/retest_broken_header.yaml:23 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {original_name: sample_id, type: String, label: Sample, is_entity_key: true}`
- config/data_analysis_recipes/retest/retest_tier2.yaml:23 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {original_name: sample_id, type: String, label: Sample, is_entity_key: true}`
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:23 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `sample_id: {original_name: sample_id, type: String, label: Sample, is_entity_key: true}`
- config/data_analysis_recipes/templates/audit.yaml:25 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/complex_template/genomics_input.yaml:4 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/complex_template/metadata_input.yaml:4 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/e_coli.yaml:24 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/e_coli.yaml:58 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/left_join_lesson.yaml:11 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `description: "What a left join does when the sample ids of the two tables do not match. The sequenced table (the left table) has 10 samples,`
- config/data_analysis_recipes/templates/left_join_lesson.yaml:33 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/left_join_lesson.yaml:52 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/simple_template.yaml:24 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- config/data_analysis_recipes/templates/simple_template.yaml:49 (recipe or template file): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- docs/appendix/Standards_yaml.qmd:48 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `| `is_entity_key` | Marks the column that identifies the entity of the table (was `is_primary_key`). Informational: join keys are written in`
- docs/appendix/data_analysis_recipe_structure.yaml:11 (other): `is_entity_key` becomes `is_entity_id`. Now: `input_fields: "Defines the columns that are read (keys: type, original_name, label, is_entity_key, null_values, strip). type is a Polars typ`
- docs/foundations/data_contracts_adr.qmd:63 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- docs/foundations/data_contracts_adr.qmd:134 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `is_entity_key: true`
- docs/foundations/data_contracts_adr.qmd:139 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: ``is_entity_key: true` is informational: it documents which column identifies the entity of the table (when the optional `entity` block names`
- docs/reference/development_rules.qmd:227 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- Multi-dataset Assembly declares its join keys in the join step (`on`, or `left_on` and `right_on`, always as lists). `is_entity_key: true``
- docs/user_guide/good_practice_recipes.qmd:37 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `Mark the column that identifies the entity with `is_entity_key: true` in the `input_fields` of its table. The app uses this declaration to d`
- docs/user_guide/good_practice_recipes.qmd:123 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- [Standards YAML](../appendix/Standards_yaml.qmd): the keys of `input_fields`, including `is_entity_key`.`
- libs/test_lab/src/test_lab/bootstrapper.py:83 (tests): `is_entity_key` becomes `is_entity_id`. Now: `fields[safe_col]["is_entity_key"] = True`
- libs/test_lab/src/test_lab/scaffolder.py:160 (tests): `is_entity_key` becomes `is_entity_id`. Now: `fields[safe_col]["is_entity_key"] = True`
- libs/test_lab/tests/test_bootstrapper.py:134 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert data["sample_id"]["is_entity_key"] is True`
- libs/utils/README.md:14 (docs and design notes): `is_entity_key` becomes `is_entity_id`. Now: `- **RemoveFromAll (remove_from_all.py)**: the pure logic of the HOME audit option "remove from all the data" (D-0415 part B, D-0416): `descr`
- libs/utils/src/utils/key_drop.py:27 (code): `is_entity_key` becomes `is_entity_id`. Now: `A declared entity key (`is_entity_key`) is not refused for being declared: it is dropped by place like any key, refused only where a later j`
- libs/utils/src/utils/lineage_records.py:77 (code): `is_entity_key` becomes `is_entity_id`. Now: `NOTE_DECLARED_ENTITY_KEY = "declared_entity_key"   # a drop here removes a column that a table declares `is_entity_key`: information for the`
- libs/utils/src/utils/lineage_records.py:201 (code): `is_entity_key` becomes `is_entity_id`. Now: `that stop the walk from following it (`unfollowed`, as reasons), and whether it comes from a column a table declares `is_entity_key` (`decla`
- libs/utils/src/utils/lineage_records.py:336 (code): `is_entity_key` becomes `is_entity_id`. Now: `key_basis: str = "declared entity keys (is_entity_key) and the key pairs of the joins of the recipe; never the column name alone"`
- libs/utils/src/utils/lineage_walk.py:868 (code): `is_entity_key` becomes `is_entity_id`. Now: `the name alone: only `is_entity_key` declarations and the key pairs of joins are used)."""`
- libs/utils/src/utils/recipe_check.py:347 (code): `is_entity_key` becomes `is_entity_id`. Now: `if isinstance(fields_, dict) and not any(isinstance(f, dict) and f.get("is_entity_key") for f in fields_.values()):`
- libs/utils/src/utils/recipe_check.py:348 (code): `is_entity_key` becomes `is_entity_id`. Now: `self.add("E02", "entity.population", f"{population!r} has no field with is_entity_key: true", "mark the key column")`
- libs/utils/src/utils/recipe_check.py:449 (code): `is_entity_key` becomes `is_entity_id`. Now: `Only a column marked is_entity_key is judged: nothing is guessed from a column name. A type that cannot be read is`
- libs/utils/src/utils/recipe_check.py:452 (code): `is_entity_key` becomes `is_entity_id`. Now: `if not isinstance(definition, dict) or definition.get("is_entity_key") is not True:`
- libs/utils/src/utils/recipe_check.py:507 (code): `is_entity_key` becomes `is_entity_id`. Now: `if "is_entity_key" in definition and not isinstance(definition["is_entity_key"], bool):`
- libs/utils/src/utils/recipe_check.py:508 (code): `is_entity_key` becomes `is_entity_id`. Now: `self.add("FD05", f"{path}.is_entity_key", "is_entity_key is true or false", "write true or false")`
- libs/utils/src/utils/recipe_factory.py:80 (code): `is_entity_key` becomes `is_entity_id`. Now: `fields[entity_key]["is_entity_key"] = True`
- libs/utils/src/utils/recipe_graph.py:397 (code): `is_entity_key` becomes `is_entity_id`. Now: `"""The key families: the columns declared `is_entity_key` in any schema, joined into one family when a join equates them`
- libs/utils/src/utils/recipe_graph.py:401 (code): `is_entity_key` becomes `is_entity_id`. Now: `for name, field in body["input_fields"].items() if isinstance(field, dict) and field.get("is_entity_key") is True}`
- libs/utils/src/utils/recipe_graph.py:428 (code): `is_entity_key` becomes `is_entity_id`. Now: `"""The columns a schema declares `is_entity_key` in its `input_fields`, in the order written; empty for a join or for a schema`
- libs/utils/src/utils/recipe_graph.py:435 (code): `is_entity_key` becomes `is_entity_id`. Now: `return tuple(name for name, field in fields.items() if isinstance(field, dict) and field.get("is_entity_key") is True) if isinstance(fields,`
- libs/utils/src/utils/recipe_graph.py:575 (code): `is_entity_key` becomes `is_entity_id`. Now: `3. the entity key declared (`is_entity_key`) on each ingredient, followed through all the steps.`
- libs/utils/src/utils/recipe_migration.py:5 (code): `is_entity_key` becomes `is_entity_id`. Now: `- renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name`;`
- libs/utils/src/utils/recipe_migration.py:40 (code): `is_entity_key` becomes `is_entity_id`. Now: `_FIELD_KEY_RENAMES = {"is_primary_key": "is_entity_key", "source_name": "original_name"}`
- libs/utils/src/utils/recipe_migration.py:344 (code): `is_entity_key` becomes `is_entity_id`. Now: `for key_name in ("is_entity_key", "is_primary_key"):`
- libs/utils/src/utils/recipe_spec.yaml:41 (the specification (recipe_spec.yaml)): `is_entity_key` becomes `is_entity_id`. Now: `optional: [categories, precision, scale, format, time_unit, time_zone, original_name, is_entity_key, null_values, strip]`
- libs/utils/src/utils/recipe_spec.yaml:107 (the specification (recipe_spec.yaml)): `is_entity_key` becomes `is_entity_id`. Now: `is_primary_key: "is_entity_key"`
- libs/utils/src/utils/remove_from_all.py:11 (code): `is_entity_key` becomes `is_entity_id`. Now: `1. Is the option offered? Only when the column is THE ENTITY KEY: a key that the recipe declares (`is_entity_key` on a field, D-0313, D-0082`
- libs/utils/src/utils/remove_from_all.py:79 (code): `is_entity_key` becomes `is_entity_id`. Now: `NO_ENTITY_KEY_DECLARED = "no_entity_key_declared"     # the recipe declares no `is_entity_key` anywhere`
- libs/utils/src/utils/remove_from_all.py:170 (code): `is_entity_key` becomes `is_entity_id`. Now: `return "This recipe does not say which column is the entity key (the id of the thing each row describes), so removing from all the data is n`
- libs/utils/src/utils/strict_form_migration.py:187 (code): `is_entity_key` becomes `is_entity_id`. Now: `self.report.append(f"{where}.input_fields.{slug.value}: role removed (nothing reads it; the key of a table is is_entity_key)")`
- libs/utils/tests/lineage_fixtures.py:71 (tests): `is_entity_key` becomes `is_entity_id`. Now: `fields = {c: ({"type": "String", "is_entity_key": True} if c in keys else {"type": "String"}) for c in columns}`
- libs/utils/tests/test_audit_copy.py:81 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"id": {"type": "String", "is_entity_key": True}, "v": {"type": "Float64"}},`
- libs/utils/tests/test_audit_copy.py:85 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},`
- libs/utils/tests/test_engine_keys_migration.py:37 (tests): `is_entity_key` becomes `is_entity_id`. Now: `id: {type: String, is_entity_key: true}`
- libs/utils/tests/test_engine_keys_migration.py:432 (tests): `is_entity_key` becomes `is_entity_id`. Now: `write(tmp_path / "r" / "fields.yaml", "id: {type: String, is_entity_key: true}\nv: {type: Float64, label: A value}\n")`
- libs/utils/tests/test_engine_keys_migration.py:434 (tests): `is_entity_key` becomes `is_entity_id`. Now: `id: {type: String, is_entity_key: true}`
- libs/utils/tests/test_engine_keys_migration.py:441 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert read(tmp_path / "r" / "fields.yaml") == "id: {type: String, is_entity_key: true}\nv: {type: Float64, ui_label: A value}\n"`
- libs/utils/tests/test_key_candidates.py:25 (tests): `is_entity_key` becomes `is_entity_id`. Now: `fields = {name: {"type": "String", "is_entity_key": True} for name in key_columns}`
- libs/utils/tests/test_lineage_drop.py:195 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"""Decided (D-0448, "Her answer: B"): D-0297 names JOIN keys, D-0358 says by place: a key a table declares (`is_entity_key`) is no reason to`
- libs/utils/tests/test_recipe_check.py:52 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"id": {"type": "String", "is_entity_key": True}, "v": {"type": "Float64"}},`
- libs/utils/tests/test_recipe_check.py:59 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},`
- libs/utils/tests/test_recipe_check.py:136 (tests): `is_entity_key` becomes `is_entity_id`. Now: `r["data_schemas"]["A"]["input_fields"]["id"].pop("is_entity_key")), "run"),`
- libs/utils/tests/test_recipe_check.py:169 (tests): `is_entity_key` becomes `is_entity_id`. Now: `("FD05", "E", lambda r: r["data_schemas"]["A"]["input_fields"]["id"].update(is_entity_key="yes"), "run"),`
- libs/utils/tests/test_recipe_check_entity_key_type.py:59 (tests): `is_entity_key` becomes `is_entity_id`. Now: `raw["data_schemas"]["A"]["input_fields"]["id"].pop("is_entity_key")`
- libs/utils/tests/test_recipe_check_join_keys.py:294 (tests): `is_entity_key` becomes `is_entity_id`. Now: `raw["data_schemas"][table]["input_fields"]["id"].pop("is_entity_key")`
- libs/utils/tests/test_recipe_check_join_keys.py:315 (tests): `is_entity_key` becomes `is_entity_id`. Now: `raw["data_schemas"]["B"]["input_fields"]["id"].pop("is_entity_key")`
- libs/utils/tests/test_recipe_engine_keys.py:44 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"id": {"type": "String", "is_entity_key": True, "label": "Id"}, "v": {"type": "Float64"}},`
- libs/utils/tests/test_recipe_engine_keys.py:48 (tests): `is_entity_key` becomes `is_entity_id`. Now: `"input_fields": {"id": {"type": "String", "is_entity_key": True}, "w": {"type": "Int64"}},`
- libs/utils/tests/test_recipe_engine_keys.py:441 (tests): `is_entity_key` becomes `is_entity_id`. Now: `input_fields: {id: {type: String, is_entity_key: true}, v: {type: Float64}}`
- libs/utils/tests/test_recipe_factory.py:77 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert recipe["data_schemas"]["reads"]["input_fields"]["sample_id"] == {"type": "String", "is_entity_key": True}`
- libs/utils/tests/test_recipe_graph.py:381 (tests): `is_entity_key` becomes `is_entity_id`. Now: `a["input_fields"]["sample_id"]["is_entity_key"] = True`
- libs/utils/tests/test_recipe_graph.py:383 (tests): `is_entity_key` becomes `is_entity_id`. Now: `b["input_fields"]["isolate"]["is_entity_key"] = True`
- libs/utils/tests/test_recipe_graph.py:393 (tests): `is_entity_key` becomes `is_entity_id`. Now: `a["input_fields"]["ka"]["is_entity_key"] = True`
- libs/utils/tests/test_recipe_graph.py:394 (tests): `is_entity_key` becomes `is_entity_id`. Now: `b["input_fields"]["kb"]["is_entity_key"] = True`
- libs/utils/tests/test_recipe_graph.py:553 (tests): `is_entity_key` becomes `is_entity_id`. Now: `raw = {"data_schemas": {"A": {**schema(["sample_id", "x"]), "input_fields": {"sample_id": {"type": "String", "is_entity_key": True}, "x": {"`
- libs/utils/tests/test_recipe_loader.py:36 (tests): `is_entity_key` becomes `is_entity_id`. Now: `FIELDS_INLINE = "{id: {type: String, is_entity_key: true}}"`
- libs/utils/tests/test_recipe_loader.py:56 (tests): `is_entity_key` becomes `is_entity_id`. Now: `write(tmp_path / "r" / "fields.yaml", "id: {type: String, is_entity_key: true}\n")`
- libs/utils/tests/test_recipe_loader.py:105 (tests): `is_entity_key` becomes `is_entity_id`. Now: `write(tmp_path / "r" / "fields.yaml", "input_fields:\n  id: {type: String, is_entity_key: true}\n")`
- libs/utils/tests/test_recipe_loader.py:128 (tests): `is_entity_key` becomes `is_entity_id`. Now: `write(tmp_path / "r" / "inner.yaml", "{type: String, is_entity_key: true}\n")`
- libs/utils/tests/test_recipe_migration.py:64 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert fields["is_entity_key"] is True and fields["original_name"] == "Sample ID"`
- libs/utils/tests/test_recipe_migration.py:100 (tests): `is_entity_key` becomes `is_entity_id`. Now: `assert load(new) == {"sample_id": {"type": "Categorical", "is_entity_key": True}, "reads": {"type": "Float64"}}`
- libs/utils/tests/test_remove_from_all.py:5 (tests): `is_entity_key` becomes `is_entity_id`. Now: `- the option is offered only for the ENTITY KEY, the key a recipe declares (`is_entity_key`, D-0313, D-0082): never for another column, also`
- libs/utils/tests/test_remove_from_all.py:316 (tests): `is_entity_key` becomes `is_entity_id`. Now: `(rfa.Reason(rfa.NO_ENTITY_KEY_DECLARED), "This recipe does not say which column is the entity key (the id of the thing each row describes), `

## 1. The names pass (mechanical)

The names pass is a mechanical migration of the display-name keys (the list of assets/scripts/migrate_display_names.py, reused as it is).


##### Summary
524 change(s) in 188 file(s); 3 listed place(s) in 2 open case(s); 0 conflict(s); 0 change(s) the script cannot place; 0 recipe(s) would get the advice (no name).
25 plot title(s) removed: 25 same as the figure title, 0 same except spaces, 0 differ, 0 plot(s) have no figure title in a labs layer (D-0484)

| kind of file | files read | changes |
|---|---:|---:|
| recipes | 101 | 211 |
| recipe templates | 9 | 40 |
| Gallery bundles | 34 | 68 |
| test fixtures | 113 | 171 |
| deployment files | 5 | 14 |
| deployment templates | 2 | 4 |
| app features files | 8 | 16 |

by rule: R01 label->ui_label (D-0410) x122, R02 name->ui_label (D-0410) x0, R03 ui_title->ui_label (D-0410) x0, R04 ui_title->REMOVED (D-0409) x0, R05 ui_title->REMOVED (D-0409) x25, R06 title->ui_label (D-0411) x2, R07 subtitle->description (D-0411) x2, R08 deployment_name->REMOVED (D-0479) x7, R09 ui_title->REMOVED (D-0411) x0, R10 label->ui_label (D-0468) x85, R11 label->ui_label (D-0468) x39, R12 label->ui_label (D-0468) x219, R13 display_name->ui_label (D-0480) x8, R14 ui_title.visible: false->branding.show_recipe_name: false (D-0474) x0, R15 deployment_name->a comment block at the top of the file (D-0479) x7, R16 name->REMOVED (D-0481) x8

##### Changes the dry run would make

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**assets/gallery_data/area_simple/data_analysis_recipe.yaml**
- assets/gallery_data/area_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/area_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_grouped/data_analysis_recipe.yaml**
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml**
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_simple/data_analysis_recipe.yaml**
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml**
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml**
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bubble/data_analysis_recipe.yaml**
- assets/gallery_data/bubble/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bubble/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/connected_scatter/data_analysis_recipe.yaml**
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml**
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/density_simple/data_analysis_recipe.yaml**
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/dumbbell/data_analysis_recipe.yaml**
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/ecdf/data_analysis_recipe.yaml**
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/error_bar/data_analysis_recipe.yaml**
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/freqpoly/data_analysis_recipe.yaml**
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml**
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/histogram_simple/data_analysis_recipe.yaml**
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/jitter_strip/data_analysis_recipe.yaml**
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/line_grouped/data_analysis_recipe.yaml**
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/line_simple/data_analysis_recipe.yaml**
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml**
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/point_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/point_simple/data_analysis_recipe.yaml**
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/proportion_bar/data_analysis_recipe.yaml**
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/qq_plot/data_analysis_recipe.yaml**
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml**
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml**
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/stacked_area/data_analysis_recipe.yaml**
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/stacked_bar/data_analysis_recipe.yaml**
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/step_chart/data_analysis_recipe.yaml**
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/tile_simple/data_analysis_recipe.yaml**
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml**
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_simple/data_analysis_recipe.yaml**
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml**
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:4: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:8: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:12: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:16: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.ui_label  [D-0468]

**config/app_features/demo-vetinst.yaml**
- config/app_features/demo-vetinst.yaml:4: R16 name REMOVED (value: demo-vetinst; file name: demo-vetinst)  [D-0481]
- config/app_features/demo-vetinst.yaml:5: R13 display_name -> ui_label  [D-0480]

**config/app_features/developer.yaml**
- config/app_features/developer.yaml:2: R16 name REMOVED (value: developer; file name: developer)  [D-0481]
- config/app_features/developer.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/pipeline-exploration-advanced.yaml**
- config/app_features/pipeline-exploration-advanced.yaml:2: R16 name REMOVED (value: pipeline-exploration-advanced; file name: pipeline-exploration-advanced)  [D-0481]
- config/app_features/pipeline-exploration-advanced.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/pipeline-exploration-simple.yaml**
- config/app_features/pipeline-exploration-simple.yaml:2: R16 name REMOVED (value: pipeline-exploration-simple; file name: pipeline-exploration-simple)  [D-0481]
- config/app_features/pipeline-exploration-simple.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/pipeline-static.yaml**
- config/app_features/pipeline-static.yaml:2: R16 name REMOVED (value: pipeline-static; file name: pipeline-static)  [D-0481]
- config/app_features/pipeline-static.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/qa.yaml**
- config/app_features/qa.yaml:17: R16 name REMOVED (value: qa; file name: qa)  [D-0481]
- config/app_features/qa.yaml:18: R13 display_name -> ui_label  [D-0480]

**config/app_features/standalone.yaml**
- config/app_features/standalone.yaml:4: R16 name REMOVED (value: standalone; file name: standalone)  [D-0481]
- config/app_features/standalone.yaml:5: R13 display_name -> ui_label  [D-0480]

**config/app_features/web-demo.yaml**
- config/app_features/web-demo.yaml:4: R16 name REMOVED (value: web-demo; file name: web-demo)  [D-0481]
- config/app_features/web-demo.yaml:5: R13 display_name -> ui_label  [D-0480]

**config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml**
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:20: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:30: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:44: R10 additional_datasets_schemas.VirulenceFinder.label -> additional_datasets_schemas.VirulenceFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:54: R10 additional_datasets_schemas.APEC_STEC_virulence_genes.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:67: R11 joins.AR1_MLST_Serotype_Virulence.label -> joins.AR1_MLST_Serotype_Virulence.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:18: R10 data_schemas.Summary.label -> data_schemas.Summary.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:29: R10 data_schemas.Summary_quality.label -> data_schemas.Summary_quality.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:43: R10 data_schemas.Quality_metrics.label -> data_schemas.Quality_metrics.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:54: R10 data_schemas.Detailed_summary.label -> data_schemas.Detailed_summary.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:66: R10 data_schemas.FastP.label -> data_schemas.FastP.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:77: R10 data_schemas.Quast.label -> data_schemas.Quast.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:88: R10 data_schemas.Bracken.label -> data_schemas.Bracken.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:99: R10 data_schemas.ResFinder.label -> data_schemas.ResFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:111: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:124: R10 additional_datasets_schemas.VirulenceFinder.label -> additional_datasets_schemas.VirulenceFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:135: R10 additional_datasets_schemas.APEC_STEC_virulence_genes.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:150: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:165: R11 joins.FastP_with_metadata.label -> joins.FastP_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:173: R11 joins.Quast_with_metadata.label -> joins.Quast_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:181: R11 joins.Bracken_with_metadata.label -> joins.Bracken_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:189: R11 joins.ResFinder_with_metadata.label -> joins.ResFinder_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:197: R11 joins.MLST_with_metadata.label -> joins.MLST_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:206: R11 joins.QC_Reads_Anchor.label -> joins.QC_Reads_Anchor.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:216: R11 joins.Summary_phenotype_length_fragmentation.label -> joins.Summary_phenotype_length_fragmentation.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:224: R11 joins.ST22_Anchor.label -> joins.ST22_Anchor.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:238: R11 joins.AR1_MLST_Serotype_Virulence.label -> joins.AR1_MLST_Serotype_Virulence.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:250: R11 joins.QA_AMR_per_sample.label -> joins.QA_AMR_per_sample.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:259: R11 joins.QA_ST_with_NA.label -> joins.QA_ST_with_NA.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:266: R11 joins.QA_year_types.label -> joins.QA_year_types.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:273: R11 joins.QA_L50_integer.label -> joins.QA_L50_integer.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:280: R11 joins.QA_fanout_exhibit.label -> joins.QA_fanout_exhibit.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:290: R11 joins.QA_aggregated_no_key.label -> joins.QA_aggregated_no_key.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:298: R11 joins.QA_population_zscore.label -> joins.QA_population_zscore.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:4: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:8: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:12: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:16: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:4: R12 data_schemas.Bracken.input_fields.sample_id.label -> data_schemas.Bracken.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:9: R12 data_schemas.Bracken.input_fields.taxon_1.label -> data_schemas.Bracken.input_fields.taxon_1.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:13: R12 data_schemas.Bracken.input_fields.proportion_1.label -> data_schemas.Bracken.input_fields.proportion_1.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:4: R12 data_schemas.Detailed_summary.input_fields.sample_id.label -> data_schemas.Detailed_summary.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:10: R12 data_schemas.Detailed_summary.input_fields.data.label -> data_schemas.Detailed_summary.input_fields.data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:14: R12 data_schemas.Detailed_summary.input_fields.data_type.label -> data_schemas.Detailed_summary.input_fields.data_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:18: R12 data_schemas.Detailed_summary.input_fields.predicted_phenotype.label -> data_schemas.Detailed_summary.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:22: R12 data_schemas.Detailed_summary.input_fields.cge_predicted_phenotype.label -> data_schemas.Detailed_summary.input_fields.cge_predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:26: R12 data_schemas.Detailed_summary.input_fields.identity.label -> data_schemas.Detailed_summary.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:30: R12 data_schemas.Detailed_summary.input_fields.overlap.label -> data_schemas.Detailed_summary.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:34: R12 data_schemas.Detailed_summary.input_fields.hsp_lengthtotal_length.label -> data_schemas.Detailed_summary.input_fields.hsp_lengthtotal_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:38: R12 data_schemas.Detailed_summary.input_fields.contig.label -> data_schemas.Detailed_summary.input_fields.contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:42: R12 data_schemas.Detailed_summary.input_fields.start.label -> data_schemas.Detailed_summary.input_fields.start.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:46: R12 data_schemas.Detailed_summary.input_fields.end.label -> data_schemas.Detailed_summary.input_fields.end.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:50: R12 data_schemas.Detailed_summary.input_fields.accession.label -> data_schemas.Detailed_summary.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:4: R12 data_schemas.FastP.input_fields.sample_id.label -> data_schemas.FastP.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:9: R12 data_schemas.FastP.input_fields.total_reads.label -> data_schemas.FastP.input_fields.total_reads.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:13: R12 data_schemas.FastP.input_fields.q30_rate.label -> data_schemas.FastP.input_fields.q30_rate.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:17: R12 data_schemas.FastP.input_fields.gc_content.label -> data_schemas.FastP.input_fields.gc_content.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:4: R12 data_schemas.MLST.input_fields.sample_id.label -> data_schemas.MLST.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:10: R12 data_schemas.MLST.input_fields.scheme.label -> data_schemas.MLST.input_fields.scheme.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:15: R12 data_schemas.MLST.input_fields.sequence_type.label -> data_schemas.MLST.input_fields.sequence_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:20: R12 data_schemas.MLST.input_fields.locus_1.label -> data_schemas.MLST.input_fields.locus_1.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:25: R12 data_schemas.MLST.input_fields.locus_2.label -> data_schemas.MLST.input_fields.locus_2.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:29: R12 data_schemas.MLST.input_fields.locus_3.label -> data_schemas.MLST.input_fields.locus_3.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:34: R12 data_schemas.MLST.input_fields.locus_4.label -> data_schemas.MLST.input_fields.locus_4.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:38: R12 data_schemas.MLST.input_fields.locus_5.label -> data_schemas.MLST.input_fields.locus_5.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:43: R12 data_schemas.MLST.input_fields.locus_6.label -> data_schemas.MLST.input_fields.locus_6.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:48: R12 data_schemas.MLST.input_fields.locus_7.label -> data_schemas.MLST.input_fields.locus_7.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:4: R12 data_schemas.Quality_metrics.input_fields.sample_id.label -> data_schemas.Quality_metrics.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:9: R12 data_schemas.Quality_metrics.input_fields.quality_module.label -> data_schemas.Quality_metrics.input_fields.quality_module.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:13: R12 data_schemas.Quality_metrics.input_fields.quality_feedback.label -> data_schemas.Quality_metrics.input_fields.quality_feedback.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:17: R12 data_schemas.Quality_metrics.input_fields.total_reads_after.label -> data_schemas.Quality_metrics.input_fields.total_reads_after.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:21: R12 data_schemas.Quality_metrics.input_fields.ratio_reads_after.label -> data_schemas.Quality_metrics.input_fields.ratio_reads_after.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:25: R12 data_schemas.Quality_metrics.input_fields.bracken_main_taxon.label -> data_schemas.Quality_metrics.input_fields.bracken_main_taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:29: R12 data_schemas.Quality_metrics.input_fields.proportion_of_main_taxon.label -> data_schemas.Quality_metrics.input_fields.proportion_of_main_taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:33: R12 data_schemas.Quality_metrics.input_fields.reads_gc_content.label -> data_schemas.Quality_metrics.input_fields.reads_gc_content.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:37: R12 data_schemas.Quality_metrics.input_fields.n50.label -> data_schemas.Quality_metrics.input_fields.n50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:41: R12 data_schemas.Quality_metrics.input_fields.total_length.label -> data_schemas.Quality_metrics.input_fields.total_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:45: R12 data_schemas.Quality_metrics.input_fields.largest_contig.label -> data_schemas.Quality_metrics.input_fields.largest_contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:49: R12 data_schemas.Quality_metrics.input_fields.num_contigs_500bp.label -> data_schemas.Quality_metrics.input_fields.num_contigs_500bp.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:53: R12 data_schemas.Quality_metrics.input_fields.num_contigs_0bp.label -> data_schemas.Quality_metrics.input_fields.num_contigs_0bp.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:4: R12 data_schemas.Quast.input_fields.sample_id.label -> data_schemas.Quast.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:9: R12 data_schemas.Quast.input_fields.n50.label -> data_schemas.Quast.input_fields.n50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:13: R12 data_schemas.Quast.input_fields.total_length.label -> data_schemas.Quast.input_fields.total_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:17: R12 data_schemas.Quast.input_fields.largest_contig.label -> data_schemas.Quast.input_fields.largest_contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:21: R12 data_schemas.Quast.input_fields.L50.label -> data_schemas.Quast.input_fields.L50.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:4: R12 data_schemas.ResFinder.input_fields.sample_id.label -> data_schemas.ResFinder.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:9: R12 data_schemas.ResFinder.input_fields.gene.label -> data_schemas.ResFinder.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:13: R12 data_schemas.ResFinder.input_fields.predicted_phenotype.label -> data_schemas.ResFinder.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:17: R12 data_schemas.ResFinder.input_fields.identity.label -> data_schemas.ResFinder.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:21: R12 data_schemas.ResFinder.input_fields.overlap.label -> data_schemas.ResFinder.input_fields.overlap.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:7: R12 data_schemas.Summary.input_fields.sample_id.label -> data_schemas.Summary.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:12: R12 data_schemas.Summary.input_fields.quality_module.label -> data_schemas.Summary.input_fields.quality_module.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:21: R12 data_schemas.Summary.input_fields.taxon.label -> data_schemas.Summary.input_fields.taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:59: R12 data_schemas.Summary.input_fields.ST.label -> data_schemas.Summary.input_fields.ST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:64: R12 data_schemas.Summary.input_fields.genome_length.label -> data_schemas.Summary.input_fields.genome_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:70: R12 data_schemas.Summary.input_fields.N50.label -> data_schemas.Summary.input_fields.N50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:75: R12 data_schemas.Summary.input_fields.contigs_sup300bp.label -> data_schemas.Summary.input_fields.contigs_sup300bp.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:4: R12 additional_datasets_schemas.VirulenceFinder.input_fields.sample_id.label -> additional_datasets_schemas.VirulenceFinder.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:9: R12 additional_datasets_schemas.VirulenceFinder.input_fields.serotype.label -> additional_datasets_schemas.VirulenceFinder.input_fields.serotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:13: R12 additional_datasets_schemas.VirulenceFinder.input_fields.virulence_raw.label -> additional_datasets_schemas.VirulenceFinder.input_fields.virulence_raw.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:5: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:10: R12 metadata_schema.input_fields.source.label -> metadata_schema.input_fields.source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:14: R12 metadata_schema.input_fields.year.label -> metadata_schema.input_fields.year.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:18: R12 metadata_schema.input_fields.country.label -> metadata_schema.input_fields.country.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml:2: R05 analysis_groups.Quality Control.plots.qc_reads_horizontal_barplot.ui_title REMOVED (value: Reads Quality & Taxonomy Proportion)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml:2: R05 analysis_groups.Results.plots.mlst_bar.ui_title REMOVED (value: MLST Sequence Type Distribution by Country)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml:2: R05 analysis_groups.Quality Control.plots.assembly_quality_dotplot.ui_title REMOVED (value: Assembly Quality Metrics (Quast))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:2: R05 analysis_groups.Results.plots.amr_heatmap.ui_title REMOVED (value: AMR Genes Presence by Category)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:2: R05 analysis_groups.Results.plots.virulence_bar.ui_title REMOVED (value: Selected Virulence Genes Count)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml:2: R05 analysis_groups.Results.plots.virulence_variants.ui_title REMOVED (value: Integrated Virulence & MLST Typing)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml:2: R05 analysis_groups.Cat 🐱.plots.miaou.ui_title REMOVED (value: 🐱 Miaou — Assembly Metric Distributions by Source)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml:2: R05 analysis_groups.Curiosity.plots.phenotype_genome_length_fragmentation.ui_title REMOVED (value: Phenotype Score correlation with Assembly Metrics)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_aggregated_no_key.ui_title REMOVED (value: QA: samples per country and year (aggregated, no sample_id))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_amr_genes_per_sample.ui_title REMOVED (value: QA: AMR genes per sample)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_facet_by_mapping.ui_title REMOVED (value: QA: facet_by written in mapping)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_fanout_rows_per_sample.ui_title REMOVED (value: QA EXHIBIT: rows per sample after joining two long tables)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_l50_integer.ui_title REMOVED (value: QA: samples per L50 (integer column))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_population_zscore.ui_title REMOVED (value: QA: N50 z-score per sample (depends on all samples))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_sequence_type_missing.ui_title REMOVED (value: QA: samples per sequence type)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_year_label.ui_title REMOVED (value: QA: samples per year (text label))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml:2: R05 analysis_groups.Results.plots.year_distribution.ui_title REMOVED (value: Sample Count by Year (T1 = all years, T2 = 2023–2025 only))  [D-0409]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:18: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:23: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:35: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:45: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:57: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:64: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/3_test_no_joins.yaml**
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:20: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/demo_abromics.yaml**
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:12: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:22: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:36: R11 joins.demo_join.label -> joins.demo_join.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:23: R10 data_schemas.fg_metadata.label -> data_schemas.fg_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:34: R10 data_schemas.fg_phenotypes.label -> data_schemas.fg_phenotypes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:45: R10 data_schemas.fg_genotypes.label -> data_schemas.fg_genotypes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:58: R11 joins.figshare_triple_join.label -> joins.figshare_triple_join.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:4: R12 data_schemas.fg_genotypes.input_fields.host_animal_common.label -> data_schemas.fg_genotypes.input_fields.host_animal_common.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:8: R12 data_schemas.fg_genotypes.input_fields.sample_id.label -> data_schemas.fg_genotypes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:12: R12 data_schemas.fg_genotypes.input_fields.gene.label -> data_schemas.fg_genotypes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:16: R12 data_schemas.fg_genotypes.input_fields.gene_type.label -> data_schemas.fg_genotypes.input_fields.gene_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:21: R12 data_schemas.fg_genotypes.input_fields.gene_identifier.label -> data_schemas.fg_genotypes.input_fields.gene_identifier.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:26: R12 data_schemas.fg_genotypes.input_fields.gene_name_family.label -> data_schemas.fg_genotypes.input_fields.gene_name_family.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:31: R12 data_schemas.fg_genotypes.input_fields.resistance_class.label -> data_schemas.fg_genotypes.input_fields.resistance_class.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:4: R12 data_schemas.fg_metadata.input_fields.sample_id.label -> data_schemas.fg_metadata.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:8: R12 data_schemas.fg_metadata.input_fields.host_animal_species.label -> data_schemas.fg_metadata.input_fields.host_animal_species.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:12: R12 data_schemas.fg_metadata.input_fields.host_animal_common.label -> data_schemas.fg_metadata.input_fields.host_animal_common.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:16: R12 data_schemas.fg_metadata.input_fields.specimen_source_tissue.label -> data_schemas.fg_metadata.input_fields.specimen_source_tissue.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:21: R12 data_schemas.fg_metadata.input_fields.final_diagnosis.label -> data_schemas.fg_metadata.input_fields.final_diagnosis.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:25: R12 data_schemas.fg_metadata.input_fields.animal_infection_site_uti.label -> data_schemas.fg_metadata.input_fields.animal_infection_site_uti.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:4: R12 data_schemas.fg_phenotypes.input_fields.sample_id.label -> data_schemas.fg_phenotypes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:8: R12 data_schemas.fg_phenotypes.input_fields.mic_id.label -> data_schemas.fg_phenotypes.input_fields.mic_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:14: R12 data_schemas.fg_phenotypes.input_fields.breakpoint.label -> data_schemas.fg_phenotypes.input_fields.breakpoint.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:20: R12 data_schemas.fg_phenotypes.input_fields.predicted_phenotype.label -> data_schemas.fg_phenotypes.input_fields.predicted_phenotype.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_a_phenotype_bar.ui_title REMOVED (value: Phenotypic Resistance per Antibiotic)  [D-0409]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_b_genotype_bar.ui_title REMOVED (value: Resistance Gene Families by Host)  [D-0409]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_c_resistance_class.ui_title REMOVED (value: Resistance Class by Host Animal)  [D-0409]

**config/data_analysis_recipes/pipelines/stress_test_master.yaml**
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:12: R10 data_schemas.Stress_Source.label -> data_schemas.Stress_Source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:23: R11 joins.Master_Collection.label -> joins.Master_Collection.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml**
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:5: R12 data_schemas.Stress_Source.input_fields.id.label -> data_schemas.Stress_Source.input_fields.id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:9: R12 data_schemas.Stress_Source.input_fields.species.label -> data_schemas.Stress_Source.input_fields.species.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:13: R12 data_schemas.Stress_Source.input_fields.amr_class.label -> data_schemas.Stress_Source.input_fields.amr_class.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:17: R12 data_schemas.Stress_Source.input_fields.collection_date.label -> data_schemas.Stress_Source.input_fields.collection_date.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:21: R12 data_schemas.Stress_Source.input_fields.value.label -> data_schemas.Stress_Source.input_fields.value.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_bad_select_column.yaml**
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:16: R10 data_schemas.Genes.label -> data_schemas.Genes.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:23: R12 data_schemas.Genes.input_fields.sample_id.label -> data_schemas.Genes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:24: R12 data_schemas.Genes.input_fields.gene.label -> data_schemas.Genes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:25: R12 data_schemas.Genes.input_fields.predicted_phenotype.label -> data_schemas.Genes.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:35: R11 joins.Genes_joined.label -> joins.Genes_joined.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_broken_header.yaml**
- config/data_analysis_recipes/retest/retest_broken_header.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:16: R10 data_schemas.Genes.label -> data_schemas.Genes.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:23: R12 data_schemas.Genes.input_fields.sample_id.label -> data_schemas.Genes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:24: R12 data_schemas.Genes.input_fields.gene.label -> data_schemas.Genes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:25: R12 data_schemas.Genes.input_fields.predicted_phenotype.label -> data_schemas.Genes.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:33: R11 joins.Genes_joined.label -> joins.Genes_joined.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_tier2.yaml**
- config/data_analysis_recipes/retest/retest_tier2.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_tier2.yaml:16: R10 data_schemas.Samples.label -> data_schemas.Samples.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:23: R12 data_schemas.Samples.input_fields.sample_id.label -> data_schemas.Samples.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:24: R12 data_schemas.Samples.input_fields.group.label -> data_schemas.Samples.input_fields.group.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:25: R12 data_schemas.Samples.input_fields.value.label -> data_schemas.Samples.input_fields.value.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:26: R12 data_schemas.Samples.input_fields.year.label -> data_schemas.Samples.input_fields.year.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:34: R11 joins.Result.label -> joins.Result.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:47: R11 joins.All_samples.label -> joins.All_samples.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_top_n_other.yaml**
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:16: R10 data_schemas.Variants.label -> data_schemas.Variants.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:23: R12 data_schemas.Variants.input_fields.sample_id.label -> data_schemas.Variants.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:24: R12 data_schemas.Variants.input_fields.variant.label -> data_schemas.Variants.input_fields.variant.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:38: R11 joins.Variants_joined.label -> joins.Variants_joined.ui_label  [D-0468]

**config/data_analysis_recipes/templates/audit.yaml**
- config/data_analysis_recipes/templates/audit.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/audit.yaml:13: R10 data_schemas.submission_logs.label -> data_schemas.submission_logs.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:26: R12 data_schemas.submission_logs.input_fields.lab_id.label -> data_schemas.submission_logs.input_fields.lab_id.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:30: R12 data_schemas.submission_logs.input_fields.submission_date.label -> data_schemas.submission_logs.input_fields.submission_date.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:34: R12 data_schemas.submission_logs.input_fields.status.label -> data_schemas.submission_logs.input_fields.status.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:38: R12 data_schemas.submission_logs.input_fields.turnaround_time.label -> data_schemas.submission_logs.input_fields.turnaround_time.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:51: R05 analysis_groups.Performance.plots.tat_distribution.ui_title REMOVED (value: Turnaround Time by Laboratory)  [D-0409]
- config/data_analysis_recipes/templates/audit.yaml:71: R05 analysis_groups.Volumes.plots.submission_status.ui_title REMOVED (value: Submissions by Current Status)  [D-0409]

**config/data_analysis_recipes/templates/complex_template.yaml**
- config/data_analysis_recipes/templates/complex_template.yaml:9: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/complex_template.yaml:15: R10 data_schemas.genomics.label -> data_schemas.genomics.ui_label  [D-0468]
- config/data_analysis_recipes/templates/complex_template.yaml:27: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/complex_template.yaml:40: R11 joins.master_assembly.label -> joins.master_assembly.ui_label  [D-0468]

**config/data_analysis_recipes/templates/e_coli.yaml**
- config/data_analysis_recipes/templates/e_coli.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/e_coli.yaml:12: R10 data_schemas.amr_results.label -> data_schemas.amr_results.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:25: R12 data_schemas.amr_results.input_fields.sample_id.label -> data_schemas.amr_results.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:29: R12 data_schemas.amr_results.input_fields.serotype.label -> data_schemas.amr_results.input_fields.serotype.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:33: R12 data_schemas.amr_results.input_fields.sequence_type.label -> data_schemas.amr_results.input_fields.sequence_type.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:37: R12 data_schemas.amr_results.input_fields.ctx_m_gene.label -> data_schemas.amr_results.input_fields.ctx_m_gene.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:41: R12 data_schemas.amr_results.input_fields.growth_rate.label -> data_schemas.amr_results.input_fields.growth_rate.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:46: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:62: R12 metadata_schema.input_fields.collection_date.label -> metadata_schema.input_fields.collection_date.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:66: R12 metadata_schema.input_fields.country_of_origin.label -> metadata_schema.input_fields.country_of_origin.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:70: R12 metadata_schema.input_fields.hospital_site.label -> metadata_schema.input_fields.hospital_site.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:74: R12 metadata_schema.input_fields.patient_age.label -> metadata_schema.input_fields.patient_age.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:78: R12 metadata_schema.input_fields.patient_outcome.label -> metadata_schema.input_fields.patient_outcome.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:83: R11 joins.amr_with_metadata.label -> joins.amr_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:104: R05 analysis_groups.AMR.plots.serotype_dist.ui_title REMOVED (value: Serotype Distribution by Country)  [D-0409]
- config/data_analysis_recipes/templates/e_coli.yaml:119: R05 analysis_groups.AMR.plots.growth_rate_by_st.ui_title REMOVED (value: Growth Rate by Sequence Type)  [D-0409]

**config/data_analysis_recipes/templates/left_join_lesson.yaml**
- config/data_analysis_recipes/templates/left_join_lesson.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:22: R10 data_schemas.sequenced.label -> data_schemas.sequenced.ui_label  [D-0468]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:41: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:61: R11 joins.lesson_assembly.label -> joins.lesson_assembly.ui_label  [D-0468]

**config/data_analysis_recipes/templates/simple_template.yaml**
- config/data_analysis_recipes/templates/simple_template.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/simple_template.yaml:12: R10 data_schemas.primary_data.label -> data_schemas.primary_data.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:28: R12 data_schemas.primary_data.input_fields.value.label -> data_schemas.primary_data.input_fields.value.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:32: R12 data_schemas.primary_data.input_fields.group.label -> data_schemas.primary_data.input_fields.group.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:37: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:53: R12 metadata_schema.input_fields.category.label -> metadata_schema.input_fields.category.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:58: R11 joins.main_collection.label -> joins.main_collection.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:80: R05 analysis_groups.Overview.plots.value_by_group.ui_title REMOVED (value: Measurement Values by Group)  [D-0409]

**config/deployment/connect/connect_template.yaml**
- config/deployment/connect/connect_template.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/connect/connect_template.yaml:21: R08 deployment_name REMOVED (value: SPARMVET — Production (Posit Connect))  [D-0479]

**config/deployment/demo/demo-vetinst.yaml**
- config/deployment/demo/demo-vetinst.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/demo/demo-vetinst.yaml:5: R08 deployment_name REMOVED (value: SPARMVET demo (demo-vetinst))  [D-0479]
- config/deployment/demo/demo-vetinst.yaml:21: R06 branding.banner.title -> branding.banner.ui_label  [D-0411]
- config/deployment/demo/demo-vetinst.yaml:22: R07 branding.banner.subtitle -> branding.banner.description  [D-0411]

**config/deployment/demo/web-demo.yaml**
- config/deployment/demo/web-demo.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/demo/web-demo.yaml:5: R08 deployment_name REMOVED (value: SPARMVET demo (web-demo))  [D-0479]
- config/deployment/demo/web-demo.yaml:21: R06 branding.banner.title -> branding.banner.ui_label  [D-0411]
- config/deployment/demo/web-demo.yaml:22: R07 branding.banner.subtitle -> branding.banner.description  [D-0411]

**config/deployment/local/local.yaml**
- config/deployment/local/local.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/local/local.yaml:5: R08 deployment_name REMOVED (value: SPARMVET_VIZ (Local Dev))  [D-0479]

**config/deployment/local/retest.yaml**
- config/deployment/local/retest.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/local/retest.yaml:5: R08 deployment_name REMOVED (value: SPARMVET RETEST)  [D-0479]

**config/deployment/pipeline_test/pipeline_test.yaml**
- config/deployment/pipeline_test/pipeline_test.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/pipeline_test/pipeline_test.yaml:15: R08 deployment_name REMOVED (value: SPARMVET_VIZ (Pipeline Test))  [D-0479]

**config/deployment/templates/deployment_template.yaml**
- config/deployment/templates/deployment_template.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/templates/deployment_template.yaml:23: R08 deployment_name REMOVED (value: My Pipeline — Institution Name)  [D-0479]

**libs/transformer/tests/data/modif_filter_data_analysis_recipe.yaml**
- libs/transformer/tests/data/modif_filter_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml**
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:21: R12 data_schemas.modif_join_where.input_fields.id.label -> data_schemas.modif_join_where.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:24: R12 data_schemas.modif_join_where.input_fields.lo.label -> data_schemas.modif_join_where.input_fields.lo.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:27: R12 data_schemas.modif_join_where.input_fields.hi.label -> data_schemas.modif_join_where.input_fields.hi.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:41: R12 data_schemas.modif_join_where_right.input_fields.rid.label -> data_schemas.modif_join_where_right.input_fields.rid.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:44: R12 data_schemas.modif_join_where_right.input_fields.v.label -> data_schemas.modif_join_where_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_all_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_all_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_any_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_any_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_bottom_k_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_bottom_k_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_coalesce_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_coalesce_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cum_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cum_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cum_sum_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cum_sum_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_describe_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_describe_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_nans_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_nans_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_nulls_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_nulls_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_dt_truncate_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_dt_truncate_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_explode_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_explode_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_fill_nan_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_fill_nan_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_fill_null_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_fill_null_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_first_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_first_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_gather_every_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_gather_every_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_group_by_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_group_by_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_group_by_dynamic_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_group_by_dynamic_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_head_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_head_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_interpolate_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_interpolate_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:21: R12 data_schemas.polars_join_asof.input_fields.id.label -> data_schemas.polars_join_asof.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:24: R12 data_schemas.polars_join_asof.input_fields.site.label -> data_schemas.polars_join_asof.input_fields.site.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:27: R12 data_schemas.polars_join_asof.input_fields.t.label -> data_schemas.polars_join_asof.input_fields.t.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:30: R12 data_schemas.polars_join_asof.input_fields.x.label -> data_schemas.polars_join_asof.input_fields.x.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:44: R12 data_schemas.polars_join_asof_right.input_fields.site.label -> data_schemas.polars_join_asof_right.input_fields.site.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:47: R12 data_schemas.polars_join_asof_right.input_fields.t.label -> data_schemas.polars_join_asof_right.input_fields.t.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:50: R12 data_schemas.polars_join_asof_right.input_fields.v.label -> data_schemas.polars_join_asof_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:21: R12 data_schemas.polars_join.input_fields.id.label -> data_schemas.polars_join.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:24: R12 data_schemas.polars_join.input_fields.g.label -> data_schemas.polars_join.input_fields.g.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:27: R12 data_schemas.polars_join.input_fields.n.label -> data_schemas.polars_join.input_fields.n.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:30: R12 data_schemas.polars_join.input_fields.f.label -> data_schemas.polars_join.input_fields.f.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:33: R12 data_schemas.polars_join.input_fields.s.label -> data_schemas.polars_join.input_fields.s.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:47: R12 data_schemas.polars_join_right.input_fields.id.label -> data_schemas.polars_join_right.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:50: R12 data_schemas.polars_join_right.input_fields.v.label -> data_schemas.polars_join_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_last_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_last_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_limit_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_limit_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_list_join_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_list_join_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_list_slice_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_list_slice_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_max_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_max_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_max_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_max_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_mean_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_mean_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_mean_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_mean_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_median_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_median_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_min_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_min_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_min_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_min_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_null_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_null_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_pivot_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_pivot_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_quantile_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_quantile_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rank_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rank_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_remove_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_remove_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rename_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rename_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_reverse_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_reverse_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rolling_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rolling_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_round_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_round_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sample_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sample_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_select_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_select_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_shift_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_shift_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_slice_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_slice_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sort_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sort_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_std_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_std_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_extract_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_extract_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_replace_all_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_replace_all_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_split_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_split_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_splitn_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_splitn_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_strip_chars_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_strip_chars_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sum_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sum_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sum_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sum_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_tail_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_tail_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_top_k_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_top_k_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unique_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unique_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unnest_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unnest_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unpivot_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unpivot_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_var_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_var_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_with_columns_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_with_columns_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_with_row_index_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_with_row_index_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml**
- libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

##### CANNOT BE DECIDED BY THE SCRIPT
(listed, never changed; each line is a place a person or the owner decides)

###### OC09: Display-like keys that no decision names (for example `info.subtitle`) -- 2 place(s)
> D-0408: `info` is the free information block: every key written is shown. No line renames or removes these keys.
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:8: info.subtitle: E. coli ST22 — AMR & Virulence Research (demo)
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:8: info.subtitle: A single data schema with no joins at all — issue

###### OC05: What the Gallery writes in `info`, and where a Gallery description lives -- 0 place(s)
> D-0408: NOT decided: what the Gallery generator writes in `info` (Gallery question Q8). The KEY of a Gallery bundle is renamed like any recipe's (D-0407: `ui_` in every file kind; D-0468: the `label` of recipe files); what `info` is for in an example is open.
- 34 Gallery bundle(s); keys written in their `info`: description x34, label x34, submission_date x34; 34 bundle(s) with an example_meta.md (the guidance text)

###### OC10: Comments that name an old key (a person must reword them) -- 1 place(s)
> D-0411: the one pass also covers the documentation and the recipe specification. The script never edits a comment.
- config/deployment/templates/deployment_template.yaml:46: branding.banner: optional {logo_url, title, subtitle} shown in the Deployment info panel.

##### COMMENT BLOCKS the script would write at the top of each deployment file (D-0479; form and wording PROVISIONAL: not decided)
(the first line is the former `deployment_name`; the second is the fixed marker line that tells a second run that the block exists; then only what the file itself states. Read the wording: it can be changed in one place, the BLOCK_* constants at the top of the script, before anything is applied.)

**config/deployment/connect/connect_template.yaml**: at the top of the file, before the existing leading comment (18 line(s)), which is kept below it
```
#### SPARMVET — Production (Posit Connect)
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default app features: pipeline-static
#### Default recipe: my_pipeline
```

**config/deployment/demo/demo-vetinst.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
#### SPARMVET demo (demo-vetinst)
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default app features: demo-vetinst
#### Default recipe: 1_test_data_ST22_dummy
#### Contact: amr-surveillance@vetinst.no
```

**config/deployment/demo/web-demo.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
#### SPARMVET demo (web-demo)
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default app features: web-demo
#### Default recipe: 1_test_data_ST22_dummy
```

**config/deployment/local/local.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
#### SPARMVET_VIZ (Local Dev)
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default app features: developer
#### Contact: https://github.com/evezeyl/SPARMVET_VIZ/issues
```

**config/deployment/local/retest.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
#### SPARMVET RETEST
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default app features: developer
```

**config/deployment/pipeline_test/pipeline_test.yaml**: at the top of the file, before the existing leading comment (12 line(s)), which is kept below it
```
#### SPARMVET_VIZ (Pipeline Test)
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default recipe: 1_test_data_ST22_dummy
```

**config/deployment/templates/deployment_template.yaml**: at the top of the file, before the existing leading comment (13 line(s)), which is kept below it
```
#### My Pipeline — Institution Name
#### Description of this deployment, written by the names pass; the app does not read it.
#### Default app features: pipeline-static
#### Default recipe: pipeline_name
#### Contact: team@example.org
```

##### CODE places that read or write a removed key (the pass must change them; not changed here; text match, a person reads each line)
name (app features file) (D-0481: the key goes; the validator rule on it and its underscore refusal, the display fallback, the old-key refusal that names it, the tests and the documents that say hyphens only):
  code: 7 place(s) in 4 file(s)
  - app/modules/app_features_validator.py:79: app_features_id = template.get("name", "")
  - app/modules/app_features_validator.py:83: # Rule 2: name must use hyphens, never underscores
  - app/modules/app_features_validator.py:84: if "_" in app_features_id and app_features_id not in (""):
  - app/modules/app_features_validator.py:87: problem=f"name '{app_features_id}' contains underscores",
  - app/src/bootloader.py:406: or self.config.get("name")
  - app/modules/renamed_keys.py:33: "persona_id": "name",
  - app/modules/sidebar_validator.py:54: app_features_id = template.get("name", template_path)
  tests: 6 place(s) in 2 file(s)
  - app/tests/test_app_features_validator.py:24: "name": app_features_id or path,
  - app/tests/test_app_features_validator.py:47: # --- Rule 2: name must use hyphens ---
  - app/tests/test_app_features_validator.py:49: def test_app_features_id_underscore_raises_error():
  - app/tests/test_app_features_validator.py:53: assert any("underscores" in e.problem for e in errors)
  - app/tests/test_app_features_validator.py:66: "name": "developer",
  - app/tests/test_bootloader_launch.py:291: @pytest.mark.parametrize("old, new", [("persona_id", "name"), ("features", "flags"),
  docs: 6 place(s) in 4 file(s)
  - .claude/rules/ui_implementation_contract.md:935: Defined in app features files: `config/app_features/<app_features_id>.yaml`. App features IDs use hyphens, nev
  - docs/troubleshooting/index.qmd:35: | [app-features-id-underscore](#app-features-id-underscore) | AppFeaturesValidator | operator | `app_features_
  - docs/troubleshooting/index.qmd:237: ### `app-features-id-underscore` {#app-features-id-underscore}
  - docs/troubleshooting/index.qmd:241: SPARMVET app features IDs use **hyphens only** — never underscores. An underscore-based
  - docs/reference/environment_variables.qmd:79: The app features config file can be placed **anywhere** — there is no filename convention requirement. The fil
  - docs/workflows/ui_app_features.qmd:251: name: "developer"
deployment_name (D-0479: the key goes; the bootloader and the connector hold no deployment name):
  code: 4 place(s) in 3 file(s)
  - app/src/bootloader.py:122: self.deployment_name: str = self.deployment_config.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
  - libs/connector/src/connector/base.py:64: def get_deployment_name(self) -> str:
  - libs/connector/src/connector/base.py:66: return self._deployment.get("deployment_name", "SPARMVET_VIZ")
  - assets/scripts/create_test_deployment.py:68: "deployment_name": args.description,
  tests: 29 place(s) in 20 file(s)
  - app/tests/gate_stage.py:71: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "gate stage", "locat
  - app/tests/test_bootloader_launch.py:37: body = {"deployment_type": "filesystem", "deployment_name": name, "locations": locations}
  - app/tests/test_bootloader_launch.py:58: assert b.deployment_name == "dep.yaml"
  - app/tests/test_bootloader_store_cleanup.py:38: path.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "dep", "default_app_featur
  - app/tests/test_cache_version_6.py:212: path.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "dep", "default_app_featur
  - app/tests/test_data_analysis_recipe_load_gate.py:35: body = {"deployment_type": "filesystem", "deployment_name": name,
  - app/tests/test_deployment_branding.py:58: assert b.deployment_name == file_data.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
  - app/tests/test_deployment_branding.py:81: assert b.deployment_name == "SPARMVET demo (demo-vetinst)"
  - app/tests/test_deployment_branding.py:91: assert b.deployment_name == "SPARMVET demo (web-demo)"
  - app/tests/test_empty_data_analysis_recipe_startup.py:39: "deployment_name": "empty-recipes-test",
  - app/tests/test_gate_gap.py:35: body = {"deployment_type": "filesystem", "deployment_name": "dep",
  - app/tests/test_opening_handler.py:236: (tmp_path / "dep.yaml").write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "dep", 
  - app/tests/test_shiny_filter_pickers.py:80: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "typed pickers", "lo
  - app/tests/test_shiny_filter_types.py:69: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "typed values", "loc
  - app/tests/test_shiny_filter_value_list.py:63: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "long list", "locati
  - app/tests/test_shiny_filter_whole_numbers.py:59: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "whole numbers", "lo
  - app/tests/test_shiny_plot_errors.py:95: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot errors", "loca
  - app/tests/test_shiny_plot_tier3.py:97: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot tier3", "locat
  - app/tests/test_shiny_plot_warnings.py:72: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot warnings", "lo
  - app/tests/test_shiny_step_order.py:85: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "step order", "locat
  - app/tests/test_tier_decides_filter_form.py:197: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "tier filter", "loca
  - libs/connector/tests/test_connectors.py:44: "deployment_name": "AMR Pipeline",
  - libs/connector/tests/test_connectors.py:111: "deployment_name": "AMR Pipeline",
  - libs/connector/tests/test_connectors.py:151: def test_get_deployment_name(self):
  - libs/connector/tests/test_connectors.py:153: assert c.get_deployment_name() == "AMR Pipeline"
  - libs/connector/tests/test_connectors.py:155: def test_get_deployment_name_default(self):
  - libs/connector/tests/test_connectors.py:157: assert c.get_deployment_name() == "SPARMVET_VIZ"
  - libs/utils/tests/test_path_expansion.py:25: "deployment_name": "~keep~"}
  - libs/utils/tests/test_path_expansion.py:28: assert cfg["deployment_name"] == "~keep~"  # not a path key
  docs: 5 place(s) in 2 file(s)
  - docs/deployment/deployment_guide.qmd:39: deployment_name: "AMR Surveillance — Institute Server"
  - docs/deployment/deployment_guide.qmd:63: deployment_name: "AMR Pipeline — IRIDA"
  - docs/deployment/deployment_guide.qmd:92: | `deployment_name` | — | Not shown; purely informational |
  - docs/workflows/connector.qmd:84: deployment_name: "AMR Pipeline — Galaxy EU"
  - docs/workflows/connector.qmd:255: deployment_name: "SPARMVET_VIZ (Local Dev)"
display_name (D-0480: the key becomes ui_label in app features files (the reader `app_features_display_name`, the allowed keys of the validator, the old-key refusal)):
  code: 28 place(s) in 10 file(s)
  - app/handlers/blueprint_handlers.py:2651: ui.input_text("bp_new_display_name", "Display name",
  - app/handlers/blueprint_handlers.py:2700: display_name = (safe_input(input, "bp_new_display_name", "") or slug).strip()
  - app/handlers/blueprint_handlers.py:2708: slug, display_name, description=desc, author=author, created=today))
  - app/modules/wrangle_studio.py:1879: display_name = "mapping (aes)"
  - app/modules/wrangle_studio.py:1885: display_name = component_name
  - app/modules/wrangle_studio.py:1892: display_name = node.get("action", "unknown")
  - app/modules/wrangle_studio.py:1917: ui.span(f"{i + 1}. {display_name}", class_="fw-bold small"),
  - app/src/bootloader.py:398: def app_features_display_name(self) -> str:
  - app/src/bootloader.py:399: """Human-readable app features name from the template's display_name field.
  - app/src/bootloader.py:405: self.config.get("display_name")
  - app/src/server.py:173: print(f"DEBUG: Initializing Server with App features: {bootloader.app_features_display_name}")
  - app/src/server.py:174: current_app_features = reactive.Value(bootloader.app_features_display_name)
  - libs/utils/build/lib/utils/recipe_check.py:315: if "display_name" in info:
  - libs/utils/build/lib/utils/recipe_check.py:316: self.add("I03", "info.display_name", "display_name was renamed", self.spec["renamed"]["info"]["display_name"])
  - libs/utils/build/lib/utils/recipe_migration.py:5: - renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name
  - libs/utils/build/lib/utils/recipe_migration.py:151: name = _find(info[1], "display_name")
  - libs/utils/build/lib/utils/recipe_migration.py:155: report.append("info: display_name -> label")
  - libs/utils/src/utils/recipe_check.py:315: if "display_name" in info:
  - libs/utils/src/utils/recipe_check.py:316: self.add("I03", "info.display_name", "display_name was renamed", self.spec["renamed"]["info"]["display_name"])
  - libs/utils/src/utils/recipe_migration.py:5: - renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name
  - libs/utils/src/utils/recipe_migration.py:151: name = _find(info[1], "display_name")
  - libs/utils/src/utils/recipe_migration.py:155: report.append("info: display_name -> label")
  - assets/scripts/dry_run_big_move.py:8: 1. the names pass (the list of assets/scripts/migrate_display_names.py, reused, not duplicated)           D-04
  - assets/scripts/dry_run_big_move.py:25: # consumes: assets/scripts/migrate_display_names.py (build_plan, lines_of, report_refusal)
  - assets/scripts/dry_run_big_move.py:62: spec = importlib.util.spec_from_file_location("migrate_display_names", SCRIPT_DIR / "migrate_display_names.py"
  - assets/scripts/dry_run_big_move.py:252: header = "Names pass (assets/scripts/migrate_display_names.py)"
  - assets/scripts/dry_run_big_move.py:680: 1: "The names pass is a mechanical migration of the display-name keys (the list of assets/scripts/migrate_disp
  - assets/scripts/migrate_recipe_format.py:4: What run A does: adds spec_version and the engine lines; renames display_name, is_primary_key and source_name;
  tests: 13 place(s) in 12 file(s)
  - app/tests/debug_pipeline_connector.py:181: record("App features loaded", PASS, bl2.app_features_display_name)
  - app/tests/test_bundle_importer.py:35: info: {{display_name: Tiny}}
  - app/tests/test_cache_keys.py:65: info: {{display_name: Tiny}}
  - app/tests/test_data_analysis_recipe_info.py:8: assert info_lines({"display_name": "AMR", "version": "1.0"}) == [(0, "display_name", "AMR"), (0, "version", "1
  - app/tests/test_data_import_check.py:28: info: {{display_name: Tiny}}
  - app/tests/test_ingestion_handler_reachability.py:41: def test_a_display_name_is_not_a_launch_value(display, monkeypatch):
  - app/tests/test_writers_emit_format_one.py:35: OLD_WORDS = ("output_fields", "final_contract", "display_name", "is_primary_key", "source_name", "_t3_origin",
  - libs/blueprint_arch/tests/test_new_recipe.py:43: assert "name" not in info and "display_name" not in info
  - libs/test_lab/tests/test_bootstrapper.py:152: assert "output_fields" not in schema and "display_name" not in recipe["info"]
  - libs/utils/tests/test_recipe_check.py:130: ("I03", "E", lambda r: r["info"].update(display_name="x"), "run"),
  - libs/utils/tests/test_recipe_factory.py:51: for old in ("output_fields", "final_contract", "display_name", "is_primary_key", "source_name"):
  - libs/utils/tests/test_recipe_migration.py:15: display_name: Old recipe   # the name
  - libs/utils/tests/test_recipe_migration.py:68: def test_display_name_becomes_label():
  docs: 4 place(s) in 3 file(s)
  - docs/reference/environment_variables.qmd:79: The app features config file can be placed **anywhere** — there is no filename convention requirement. The fil
  - docs/reference/environment_variables.qmd:87: # 2. Edit display_name, name, and feature flags in the new file
  - docs/workflows/ui_app_features.qmd:252: display_name: "Workflow Developer"
  - .claude/rules/rules_toolchain.md:24: | `assets/scripts/migrate_display_names.py` | DRY RUN of the names pass (ledger D-0407 to D-0412, D-0468 to D-

##### Facts to name the recipe banner switch (D-0472)
(per deployment file: its default app features file and the keys of its `branding` block; per app features file: what its `ui_title` sets today. The list of allowed deployment keys does not exist yet: D-0412 asks for it, it comes with the deployment standard; today the only refusal tables are app/modules/renamed_keys.py and the readers app/src/bootloader.py:591, 874, 877-879)
- config/deployment/connect/connect_template.yaml: default_app_features = pipeline-static; branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/demo/demo-vetinst.yaml: default_app_features = demo-vetinst; branding keys: theme_css, banner, contact; banner keys: logo_url, title, subtitle; the banner shows: title 'AMR Surveillance — Overview'; line 'Norwegian Veterinary Institute'; logo 'assets/demo/logo-no.svg'
- config/deployment/demo/web-demo.yaml: default_app_features = web-demo; branding keys: theme_css, banner; banner keys: logo_url, title, subtitle; the banner shows: logo 'assets/demo/logo-no.svg'
- config/deployment/local/local.yaml: default_app_features = developer; branding keys: contact; banner keys: (no banner); the banner shows: no banner
- config/deployment/local/retest.yaml: default_app_features = developer; branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/pipeline_test/pipeline_test.yaml: default_app_features = (none); branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/templates/deployment_template.yaml: default_app_features = pipeline-static; branding keys: contact; banner keys: (no banner); the banner shows: no banner
- config/app_features/demo-vetinst.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/developer.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-exploration-advanced.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-exploration-simple.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-static.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/qa.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/standalone.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/web-demo.yaml: does not set ui_title (the recipe banner is shown)

##### WOULD GET THE ADVICE (no recipe name)
(not an error, D-0470: the file name is shown where a name is needed)

##### DECIDED, nothing for the script to change (counts only)
(D-0468, D-0469, D-0471, D-0475)

###### OC02: DECIDED, not renamed: the `"label"` strings of the Python code (action forms, registries) -- 0 place(s)
> D-0468: the review session's reading (not her words): the `"label"` strings of the Python code are not recipe keys and are not renamed by this pass. Counted by text match, not a parse.
- 890 place(s) in 22 file(s) write a `"label"` key in libs/*/src (text match; blueprint_arch: 11, test_lab: 6, transformer: 53, utils: 3, viz_factory: 814, viz_gallery: 3)

###### OC03: DECIDED: the recipe format number stays 1 -- 0 place(s)
> D-0469 (her words: we are still in development so the same format can stay): the recipe format number stays 1. The count shows the spec_version of every master recipe.
- spec_version found in 1 x122 master recipe(s)

###### OC04: DECIDED: old session files are refused, not converted -- 4 place(s)
> D-0475 (her words: 3, 4, 6, 7. accepted.; point 4 as the review session reports it: a saved session with an old name key is refused with a plain line, no conversion, resting on D-0312, D-0471): old session files are refused, not converted. The script lists where a session holds a name key and never touches a session.
- 97 session file(s) found under a `_sessions` folder, 0 with an old name key. The session writer's own `label` is the user's label of the session, not a recipe name (app/modules/session_manager.py).
- tmpAI/panel/verification/scratch4b/sess_4af4s9a0/_sessions/aaaaaaaaaaaa:bbbbbbbbbbbb/assembly.json: cannot be read as JSON
- tmpAI/panel/verification/scratch4b/sess_lw4xfw_r/_sessions/aaaaaaaaaaaa:bbbbbbbbbbbb/t3_99999999T999999999999.json: cannot be read as JSON
- tmpAI/panel/verification/scratch4b/sess_tg_vpi6z/_sessions/aaaaaaaaaaaa:bbbbbbbbbbbb/assembly.json: cannot be read as JSON
- tmpAI/panel/verification/scratch4b/sess_v53th6sw/_sessions/aaaaaaaaaaaa:bbbbbbbbbbbb/t3_99999999T999999999999.json: cannot be read as JSON

###### OC20: DECIDED: a removed plot `ui_title` that is the same as the figure title -- 25 place(s)
> D-0484: the text is removed and copied nowhere, because the `labs` layer of the plot already holds it (exact text equal).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml:2: analysis_groups.Quality Control.plots.qc_reads_horizontal_barplot.ui_title is the same as the figure title: "Reads Quality & Taxonomy Proportion"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml:2: analysis_groups.Results.plots.mlst_bar.ui_title is the same as the figure title: "MLST Sequence Type Distribution by Country"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml:2: analysis_groups.Quality Control.plots.assembly_quality_dotplot.ui_title is the same as the figure title: "Assembly Quality Metrics (Quast)"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:2: analysis_groups.Results.plots.amr_heatmap.ui_title is the same as the figure title: "AMR Genes Presence by Category"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:2: analysis_groups.Results.plots.virulence_bar.ui_title is the same as the figure title: "Selected Virulence Genes Count"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml:2: analysis_groups.Results.plots.virulence_variants.ui_title is the same as the figure title: "Integrated Virulence & MLST Typing"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml:2: analysis_groups.Cat 🐱.plots.miaou.ui_title is the same as the figure title: "🐱 Miaou — Assembly Metric Distributions by Source"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml:2: analysis_groups.Curiosity.plots.phenotype_genome_length_fragmentation.ui_title is the same as the figure title: "Phenotype Score correlation with Assembly Metrics"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml:2: analysis_groups.QA Canaries.plots.qa_aggregated_no_key.ui_title is the same as the figure title: "QA: samples per country and year (aggregated, no sample_id)"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml:2: analysis_groups.QA Canaries.plots.qa_amr_genes_per_sample.ui_title is the same as the figure title: "QA: AMR genes per sample"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml:2: analysis_groups.QA Canaries.plots.qa_facet_by_mapping.ui_title is the same as the figure title: "QA: facet_by written in mapping"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml:2: analysis_groups.QA Canaries.plots.qa_fanout_rows_per_sample.ui_title is the same as the figure title: "QA EXHIBIT: rows per sample after joining two long tables"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml:2: analysis_groups.QA Canaries.plots.qa_l50_integer.ui_title is the same as the figure title: "QA: samples per L50 (integer column)"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml:2: analysis_groups.QA Canaries.plots.qa_population_zscore.ui_title is the same as the figure title: "QA: N50 z-score per sample (depends on all samples)"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml:2: analysis_groups.QA Canaries.plots.qa_sequence_type_missing.ui_title is the same as the figure title: "QA: samples per sequence type"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml:2: analysis_groups.QA Canaries.plots.qa_year_label.ui_title is the same as the figure title: "QA: samples per year (text label)"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml:2: analysis_groups.Results.plots.year_distribution.ui_title is the same as the figure title: "Sample Count by Year (T1 = all years, T2 = 2023–2025 only)"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml:2: analysis_groups.AMR Integration.plots.plot_a_phenotype_bar.ui_title is the same as the figure title: "Phenotypic Resistance per Antibiotic"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml:2: analysis_groups.AMR Integration.plots.plot_b_genotype_bar.ui_title is the same as the figure title: "Resistance Gene Families by Host"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml:2: analysis_groups.AMR Integration.plots.plot_c_resistance_class.ui_title is the same as the figure title: "Resistance Class by Host Animal"
- config/data_analysis_recipes/templates/audit.yaml:51: analysis_groups.Performance.plots.tat_distribution.ui_title is the same as the figure title: "Turnaround Time by Laboratory"
- config/data_analysis_recipes/templates/audit.yaml:71: analysis_groups.Volumes.plots.submission_status.ui_title is the same as the figure title: "Submissions by Current Status"
- config/data_analysis_recipes/templates/e_coli.yaml:104: analysis_groups.AMR.plots.serotype_dist.ui_title is the same as the figure title: "Serotype Distribution by Country"
- config/data_analysis_recipes/templates/e_coli.yaml:119: analysis_groups.AMR.plots.growth_rate_by_st.ui_title is the same as the figure title: "Growth Rate by Sequence Type"
- config/data_analysis_recipes/templates/simple_template.yaml:80: analysis_groups.Overview.plots.value_by_group.ui_title is the same as the figure title: "Measurement Values by Group"

##### 64 file(s) read but not examined (no spec_version, included by no recipe)
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Bracken_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Bracken_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/FastP_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/FastP_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_L50_integer.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_ST_with_NA.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_population_zscore_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_population_zscore_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_year_types.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QC_Reads_Anchor_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Quast_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Quast_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_wrangling_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_wrangling_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/VirulenceFinder_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/metadata_schema_wrangling.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/Plasmid_Profile_Joint.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/wrangling/amr_data.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/wrangling/plasmid_data.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/fg_genotypes_wrangling.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/fg_metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/fg_phenotypes_wrangling.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/figshare_triple_join_steps.yaml
- config/data_analysis_recipes/pipelines/stress_test_master/plots/final_plot.yaml
- config/data_analysis_recipes/pipelines/stress_test_master/wrangling/Master_Collection_steps.yaml
- config/data_analysis_recipes/pipelines/stress_test_master/wrangling/Stress_Source_wrangling.yaml
- config/data_analysis_recipes/templates/complex_template/genomics_wrangling.yaml
- config/data_analysis_recipes/templates/complex_template/master_steps.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/wrangling/plasmid_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/wrangling/plasmid_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/wrangling/plasmid_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/wrangling/plasmid_data.yaml

4 of them hold display-like keys (label, name, title, subtitle, display_name, ui_title, ui_label) that the script did not look at:
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml: title (line 2), name (line 10)
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml: label (line 4)
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml: name (line 18)
- config/data_analysis_recipes/pipelines/stress_test_master/plots/final_plot.yaml: title (line 1), name (line 6)

## Annex: the Gallery examples with no entity id declared

- assets/gallery_data/area_simple/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/area_simple/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/bar_grouped/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/bar_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/bubble/data_analysis_recipe.yaml:14: recipe `assets/gallery_data/bubble/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/connected_scatter/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:14: recipe `assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/density_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/dumbbell/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/ecdf/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/error_bar/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/freqpoly/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/histogram_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:14: recipe `assets/gallery_data/jitter_strip/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/line_grouped/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/line_simple/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/point_faceted/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/point_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:14: recipe `assets/gallery_data/proportion_bar/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/qq_plot/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/stacked_area/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/stacked_bar/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:14: recipe `assets/gallery_data/step_chart/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/tile_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:13: recipe `assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml`, table `example`: no id declared and no column with an id-like name (no id column).
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/violin_faceted/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:12: recipe `assets/gallery_data/violin_simple/data_analysis_recipe.yaml`, table `example`: no id declared; a column named `id` exists: a candidate, not a decision.
