# Run register of the Opus agent, topic "how to build the recipes" (step 2 of D-0554). Owner's rule D-0561.

Every run is written here BEFORE it is made, with (1) the requirement or hypothesis, (2) the result expected by design, stated so that the run can contradict it, (3) why it is independent of the old lineage structure. After the run: the observed result, and AGREES or CONTRADICTS.

Common points.
- Machine rule: the script exits at once when the 1-minute load is above 10.
- Read-only on the repository. Scripts, scratch recipes, data and outputs live in `tmpAI/coordinator/design_dialogue/opus3_*`.
- Worktree `SPARMVET_VIZ_wt_goals` (`0744cafb`), environment `opus2_env.sh`.
- Independence: the recipe is read by `ConfigManager` and my own parse (`opus2_graph.py`).
- Scratch recipes are run by `DataOrchestrator.materialize_tier1/2/3`, each variant in a new empty folder, with steps written BY HAND into the scratch recipe (no audit code).
- The checker is reached only through the loader `cache_keys.load_data_analysis_recipe`.
- Nothing calls `lineage_walk`, `lineage_records`, `remove_from_all`, `recipe_graph`, `run_audit`, `key_drop` or HOME's audit code.

Scratch data, the same for all scratch recipes:
- metadata M (`sample_id`, `country`): s1 to s5. s5 has no analysis, the case of "metadata for more samples" in D-0549.
- R, the genes found, several rows per sample (`sample_id`, `gene`): s1 g1, s1 g2, s2 g1, s3 g3. s4 has no gene.
- Q, a quality value, one row per sample (`sample_id`, `n50`): s1 to s4.
- G, a look-up table (`gene`, `gene_class`): g1, g2, g3. G2 is the same with g1 written twice.
- V, a second per-observation table (`sample_id`, `vf`): s1 v1, s1 v2, s2 v1.

## RR1 `join_catalogue` (`opus3_catalogue.py`, output `opus3_catalogue.out`)
1. Requirement: "We will need a system for joins that are not metadata though" [D-0562]; the kinds of table: "results of analysis for the sample information so there is a common key with the metadata (sample id) - or tables used at look up" [D-0512].
2. Expected: every join step of every shipped recipe either joins on a column that both sides declare `is_entity_key` (an entity join), or joins on a column that neither side declares (a look-up or other join). On the demo every join is on `sample_id` except the two with `APEC_STEC_virulence_genes` (`VF_gene` = `Gene_name`, inner). A join on a column declared on one side only contradicts this and is a finding.
3. My parse only.
Status: DONE (load 2.2; `opus3_catalogue.out`). Observed: 50 recipes, 33 join steps: 26 on a column both sides declare (entity joins), 7 on a column neither declares, 0 on one side only. The 7: the 3 joins with the APEC look-up table (`VF_gene` = `Gene_name`, inner: 2 in the demo, 1 in `1_Abromics_general_pipeline`), and 4 joins on `sample_id` in two recipes that declare no entity key at all (`2_test_data_ST22_dummy`, `figshare_integration`). **AGREES.** Finding: a declaration alone cannot tell an entity join from a look-up join where a recipe declares nothing.

## RR2 `demo_join_cardinality` (`opus3_catalogue.py`)
1. Requirement: "sample id is not a key in resfinder because its not unique" and "if its unique then it is a key if not it refers to the column used for the join" [D-0562].
2. Expected:
   - In the demo's tier-1 tables, `sample_id` is unique in the metadata and in every one-row-per-sample table, and not unique in ResFinder and VirulenceFinder.
   - A join whose right side is unique on the join column keeps the row count of its base.
   - Joins whose right side is not unique multiply rows: `ST22_Anchor` and `QA_fanout_exhibit` grow from the 42 rows of the metadata.
   - Every joined table still holds `sample_id` (R7: every tier-1 table except APEC holds it).
   Any other uniqueness, or a joined table without `sample_id`, contradicts this.
3. Reads the parquet files that the engine wrote into an empty folder in R7 (`opus2_runB/ORIG`), with polars and my parse.
Status: DONE (`opus3_catalogue.out`). Observed: `sample_id` unique in the metadata and in the one-row-per-sample tables; NOT unique in ResFinder (70 rows, 38 samples), VirulenceFinder (984, 42), and also Summary (623, 42) and Detailed_summary (91, 36); every joined table holds `sample_id`. The joins whose right side is not unique multiply rows (`ST22_Anchor` 42 -> 617, `QA_fanout_exhibit` 42 -> 1731, `AR1_MLST_Serotype_Virulence` 42 -> 342, `QA_AMR_per_sample` 42 -> 74). **CONTRADICTS** my statement in two points. (1) Summary and Detailed_summary are also several rows per sample. (2) A joined tier-1 table can change its row count by its other steps: `Quast_with_metadata` 42 -> 126 by its `polars_unpivot`, and `Summary_phenotype_length_fragmentation` 623 -> 126. The join step alone was not measured.

## RR3 `pattern_per_observation` (`opus3_recipes.py`, output `opus3_recipes.out`)
1. The pattern put to her: a result per observation, data left, metadata right. "T1 original -> left_join -> metadata" [D-0547]. "The metadata should be the right table -- best practice and would solve problems (some users will have metadata for more samples so that will allow to join what really is in T1 without the extra in metadata)" [D-0549].
2. Expected: the join JO = [R, M] (left) has R's 4 rows, each with its country; s4 and s5 are absent. Removal of s1:
   - at `T1:R`: JO has 2 rows, s1 gone;
   - at `T1:M`: JO keeps 4 rows, s1's 2 rows with `country` empty;
   - at `T1:JO`: 2 rows.
3. Scratch recipe, steps written by hand, engine, new empty folders.
Status: DONE (load 2.2; `opus3_recipes.out`, run on the combined scratch recipe `both`). Observed: JO 4 rows (s1 x2, s2, s3), s4 and s5 absent. Removal of s1 at `T1:R`: 2 rows. At `T1:M`: 4 rows, s1's `country` empty (also in JQ). At `T1:JO`: 2 rows. **AGREES.**

## RR4 `pattern_per_entity_with_zeros` (`opus3_recipes.py`)
1. The second pattern put to her: a result per entity that needs zeros. Aggregate to the entity grain first, then join with the metadata as the first (left) table. Written today with a second table RC on R's file (her reimport idea, D-0556) whose tier 1 counts genes per sample.
2. Expected: JE = [M, RC] (left), then the nulls are filled with 0. JE has one row per metadata sample, s1 to s5, with `n_genes` 2, 1, 1, 0, 0: s4 (analysed, no gene) and s5 (not analysed) cannot be told apart. Removal of s1:
   - at `T1:M`: s1 gone;
   - at `T1:RC`: s1 STAYS, with `n_genes` 0. A false zero;
   - at `T1:JE`: s1 gone.
   Anything else contradicts this.
3. As RR3.
Status: DONE (`both`). Observed: JE s1 2, s2 1, s3 1, s4 0, s5 0. Removal of s1 at `T1:M`: s1 gone. At `T1:RC`: s1 stays with `n_genes` 0, a false zero. At `T1:JE`: s1 gone. A step at `T1:R` does not reach JE (RC is its own table on the same file). **AGREES.**

## RR5 `joins_not_metadata` (`opus3_recipes.py`)
1. Requirement: "We will need a system for joins that are not metadata though" [D-0562]; look-up tables "can be used as later join (eg, our example of filtering AMR genes of interest)" [D-0512].
2. Expected:
   - Look-up join JL = [R, G] on `gene` (left, G unique on `gene`): 4 rows, `sample_id` kept. Removal of s1 at `T1:R`: 2 rows. A removal by `sample_id` at `T1:G` is refused by the engine (no `sample_id`).
   - With G2 (g1 twice), the rows of g1 multiply: 6 rows.
   - Join between analyses JQ = [R, Q] on `sample_id` (Q one row per sample): 4 rows.
   - Join between two per-observation tables JV = [R, V] on `sample_id` (left): s1 has 2 x 2 = 4 rows, s2 1, s3 1 (V empty), so 6 rows. Removal of s1 at `T1:V`: s1 stays (2 rows, `vf` empty). At `T1:JV`: 2 rows.
   Anything else contradicts this.
3. As RR3.
Status: DONE (`joins`). Observed: JL 4 rows; with G2, 6 rows. JQ 4. JV 6 (s1 4, s2 1, s3 1 with `vf` empty). Removal of s1 at `T1:R`: all three joins lose s1. At `T1:V`: JV keeps s1's 2 rows with `vf` empty. At `T1:JV`: 2 rows. At `T1:G`: the engine refuses ("column 'sample_id' is not in the table"), and JL cannot be built. **AGREES.**

## RR6 `forms_refused_or_run` (`opus3_recipes.py`)
1. The recipe forms of her question on the recipe form (Q3 of `PATHS_AND_DERIVED_AGREED.md`):
   - "one trunk", a join that reads a join ("Yes, revisit if needed", D-0344);
   - a default place declared by the author (a new key);
   - derived tables with `from:` ("yes we need the `from:`", D-0517);
   - her question 27: a look-up join after tier 1 (D-0562, not decided).
2. Expected: the loader refuses each one with the checker's code:
   - a join of a join: J04 ("is not a schema of this recipe");
   - `default_place` on a schema: S01 (unknown key);
   - `from:` on a join: J01 (unknown key);
   - a join step in tier 2: ST05.
   A recipe that loads contradicts this.
3. The loader only. The scratch recipes are not run further.
Status: DONE (`opus3_recipes.out`). Observed: the loader (`load_data_analysis_recipe`) LOADED all four forms. **CONTRADICTS**: the loader of the engine does not run the recipe check. The check runs at the app's load gate and in BLUEPRINT (`app/modules/data_analysis_recipe_validator.py:303`). RR8 asks the check itself.

## RR7 `today_form_quality_case` (`opus3_recipes.py`)
1. Her case "remove the samples from all analyses BUT the ones that show the bad quality" [D-0549], on a small recipe in today's form: JO = [R, M], JQ = [Q, M]; a plot of the analysis on JO and a quality plot on JQ.
2. Expected: one place, `T1:JO` (the join place of the analysis), gives the analysis plot without s1 and the quality plot unchanged, still with s1. My graph shows `T1:JO` and `T1:JQ` as independent places.
3. As RR3; the graph from my parse.
Status: DONE (`both`). Observed: one place `T1:JO`: the analysis table loses s1 (2 rows); the quality table JQ is unchanged (4 rows, s1 present). My graph: `T1:JO` and `T1:JQ` are independent; the metadata lies above all three plots. **AGREES.**

## RR8 `forms_against_the_check_and_the_engine` (`opus3_rr8.py`, output `opus3_rr8.out`), added after RR6 contradicted its expectation
1. Same forms as RR6. Is each refused by the recipe check itself, and can the engine build it?
2. Expected:
   - `check_recipe(raw, "run")` gives these errors: J04 for the join of a join; S01 for `default_place`; J01 for `from`; ST05 for the join in tier 2.
   - The engine cannot build the join of a join (JO is not a source table) nor the join in tier 2.
   - The engine builds the recipe with `default_place` or `from` (unknown keys are not read by the engine).
   Any other result contradicts this.
3. The checker and the engine are the objects under test; the four scratch recipes are the YAML files RR6 wrote (`opus3_out/recipes/rr6_*`). No lineage code.
Status: DONE (`opus3_rr8.out`, `opus3_rr8_codes.out`). Observed, check: J04 for the join of a join (`'JO' is not a schema of this recipe`), S01 for `default_place`, J01 for `from`, ST05 for the join in tier 2 (`polars_join is only allowed in tier1`), beside the errors that every minimal scratch recipe has (no labels; absolute paths). Engine: the join of a join is refused ("names 'JO', which is not a data schema"); a join with its join step moved to tier 2 cannot be built ("No step list and no ingredients"); with `default_place` or `from` the engine builds every table. **AGREES.**

## RR9 `rename_count` (shell: `git ls-files` and `grep`; output `opus3_rr9.out`)
1. Requirement: "is_entity_id for all cases" [D-0562], in one move [D-0525]. The merged list (G15, section 5) gives the counts that the move touches.
2. Expected (the Sonnet numbers): 10 files with `is_entity_key` in the demo's folder (11 tables: `Summary_input_fields.yaml` is included by two tables); 21 files under `config/data_analysis_recipes`; 111 tracked files in all; 218 lines. Other counts contradict this.
3. A count of text in the repository's tracked files (main tree, `dev`); no code is run.
Status: DONE (main tree `d7b9ea44`; `opus3_rr9.out`). Observed: 10 files in the demo's folder (`Summary_input_fields.yaml` included twice, recipe lines 25 and 36: 11 tables); 21 files under `config/data_analysis_recipes`; 111 tracked files; 218 lines. **AGREES.**

## RR10 `additional_tables_with_entity_id` (`opus3_rr10.py`, output `opus3_rr10.out`)
1. The disagreed point 1 of `RECIPES_AGREED_AND_OPEN_v1.md`: my advice "an additional (look-up) table with an entity id" against the Sonnet position "information only". Her words on the blocks: D-0512, D-0513; her decision "VirulenceFinder moves" [D-0523].
2. Expected: in the shipped recipes, at least one table in `additional_datasets_schemas` declares an entity id: the demo's `VirulenceFinder`, the table her D-0523 moves. The Sonnet expectation was 0; a result of 0 contradicts mine.
3. My parse only.
Status: DONE (`opus3_rr10.out`). Observed: 50 recipes, 4 tables in `additional_datasets_schemas`, 2 of which declare an entity id: `VirulenceFinder` in the demo and `VirulenceFinder` in `1_Abromics_general_pipeline`. **AGREES** (Sonnet's expected 0 is contradicted). In both cases it is the per-sample analysis table that her D-0523 moves for the demo.

## RR11 `read_the_23` (`opus3_rr11.py`, output `opus3_rr11.out`): READS FILES ONLY. No engine and no build (her order D-0566: no run on the cause).
1. Requirement: "find the cause" of the two tables that stayed identical [D-0563]; whether my R5 sentence ("the tier 2 counts rows per sample") is right.
2. Expected: the recipe's tier 2 counts non-empty `VF_gene` values (`pl.col('VF_gene').count()`). My stored tables of R5, written by the engine into empty folders, show:
   - in T1 of `QA_fanout_exhibit`, 23 rows for the entity before and after the step, `VF_gene` non-empty in all 23, and `gene` non-empty in 23 before and in 0 after;
   - in T2, `rows_per_sample` = 23 before and after.
   In the raw files: the metadata has 42 entities; ResFinder has 70 rows and 38 distinct entities; the entity's lines in the VirulenceFinder file are counted as they are. A different stored table contradicts this.
3. Reads parquet files the engine wrote earlier (`opus2_runA/ORIG`, `opus2_runA/AT_T1_ResFinder`) and the raw TSV files, with polars only.
Status: DONE (load 2.8; `opus3_rr11.out`; reads only). Observed: before the step, the entity has 23 rows in T1 of `QA_fanout_exhibit`, `VF_gene` non-empty in 23 (23 distinct), `gene` = `blaTEM-1C` in 23, and T2 `rows_per_sample` 23. After a step at `T1:ResFinder`: 23 rows, `VF_gene` non-empty in 23, `gene` empty in all 23, T2 23. Raw files: metadata 42 rows, 42 entities; ResFinder 70 rows, 38 entities; the VirulenceFinder file has 29 lines with the entity. **AGREES**. My R5 sentence "the tier 2 counts rows per sample" was wrong in what it counts: the tier 2 counts non-empty `VF_gene` values (`pl.col('VF_gene').count()`). The count equals the rows here only because each of the 23 rows has a virulence gene.

## RR12 `scan_joined_tables` (`opus3_rr12.py`, output `opus3_rr12.out`): READS FILES ONLY (my parse; no engine)
1. Requirement: the scan of D-0563 and D-0564 (the joined tables that start from the metadata; counts after a join), as written in `CAUSE_identical_tables.md` section (d).
2. Expected (its numbers):
   - 14 recipes with joins and 31 joined tables;
   - 7 joined tables start from the metadata (6 in the demo, plus `demo_abromics :: demo_join`), 4 of them in the demo with a data join;
   - `ST22_Anchor` is the only joined table that counts rows (`pl.len()`);
   - 5 inner join steps.
   Other numbers contradict it.
3. My parse of the recipe files; a text search of the steps; nothing is run.
Status: DONE (`opus3_rr12.out`). Observed: 14 recipes with joins, 31 joined tables; 7 start from the metadata (6 demo: `ST22_Anchor`, `QA_AMR_per_sample`, `QA_year_types`, `QA_fanout_exhibit`, `QA_aggregated_no_key`, `QA_population_zscore`; plus `demo_abromics::demo_join`); only `ST22_Anchor` counts rows (`pl.len()`) among joined tables; 5 inner join steps. **AGREES.**

## RR13 `overlap_count` (`opus3_rr13.py`, output `opus3_rr13.out`): READS FILES ONLY; no engine and no build (D-0565, D-0566)
1. Requirement: her contract, "the metadata is supposed to cover all the ids of the result files ..." [D-0568]; a cross-check of the table in `OVERLAP_AND_POPULATION.md`.
2. Expected by her contract: 0 ids of each result file absent from the metadata (raw, stripped, stripped and lower-cased). The Sonnet table also gives 4 metadata ids absent from ResFinder (70 rows, 38 distinct) and 0 elsewhere. A different count contradicts it.
3. Independence: a plain reader on the data files of the demo, using the recipe's own declarations (my parse: the declared entity field, its `original_name`, the `source.path`, `strip` and `null_values`); no repository code beyond the YAML loader.
Status: DONE (load 4.6; `opus3_rr13.out`; reads only). Observed: the metadata has 42 rows, 42 ids, 0 nulls. For each of the ten tables that declare the entity id, 0 ids are not in the metadata (raw, stripped, lower-cased). Metadata ids absent from the file: 4 of 42 for ResFinder (70 rows, 38 ids), 0 elsewhere. Rows: Detailed_summary 280, VirulenceFinder 1315, the others 42. APEC declares no id. **AGREES** with her contract and with the Sonnet table, number for number.
