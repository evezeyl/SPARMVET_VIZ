# Recipe fixes decided by Eve on 2026-11-15: the exact list for the builder

Prepared by the data-scientist viewpoint. No repository file was changed. Every statement is marked RUN (I ran it) or READ (I read it in a file). Scratch work, scripts and the four ready patches are in `tmpAI/panel/round7/recipe_fixes/` (called "the scratch folder" below).

Plain words used once: "golden baseline" = `app/tests/golden/baseline.json`, the recorded content hash of every table and plot table of the 7 shipped pipelines. "The checker" = `check_recipe_file` with the registries (profile run). "Advice" = a checker message that is not an error.

## 0. What Eve decided (her words) and where the coordinator's summary differs (READ)

Sources: `tmpAI/agent_channel.md` blocks M94 and M95 from sparmvet-viz-57; ledger `tmpAI/panel/adr/ledger.md` lines N22, N25, N31, N32 (her words checked against her chat turns by the ledger author); `.claude/tasks/tasks.md` section 6.

| Subject | Her words | Same as the coordinator's summary? |
|---|---|---|
| Pipelines fixed | N25: "Pipelines recipes need to be fixed - ask data scientist agent to discover the expected intend and fix" | She did not name the 37 descriptions or the formula. Those come from the coordinator and the checker. |
| Multi-resistance formula (N21) | Not her decision. M95 point N21 is a coordinator default, tagged PROVISIONAL "no shipped result changes". `tasks.md` line 345 says "N21 (provisional)". | The summary says "the formula is corrected" as if decided. Only the missing-value part is the coordinator's provisional default. N22 (is "unknown" a class) was asked to her in M95 and I found no answer in the channel, the ledger (N01 to N52) or tasks.md. It is open. |
| Gallery | N22: "All recipes need to work"; "gallery ui rest the same, its only the adjustment of recipes and production of new plots" | Same. Already true at HEAD (item C). |
| Fragments | N31: "N8. This was already decided -a remove old output fields. b,c,d,e - ask agent data science to wire it" and the cleaning rule: deleted, or moved to an archive folder if history is needed | Same. For (d) I propose delete, not wire (reason in D). |
| ResFinder rule | N32: "This must be per sample then per duplicates - keep the one with best identity and best coverage"; "you filter out what is below ... then you keep the first higher"; N10 "ok": wire the piece in if a recipe uses that data, else archive | Same. The old thresholds are two different pairs (item E): she must say which. |

## A. The multi-resistance formula (2_test_data_ST22_dummy)

**What is wrong today.**
- File and line: `config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml` line 36 (READ): `pl.col('predicted_phenotype_clean').n_unique().over('sample_id') > 1`. The comment on line 33 says "sample carries >1 distinct resistance class".
- Two defects (RUN, `a_polars.py`, `a_engine.py`):
  1. A missing phenotype is counted as a value by `n_unique`. On the shipped data there is no missing phenotype, so no number moves today. It moves on dirty data (the check of 2026-11-15 found it).
  2. 13 of the 70 hits have the phenotype "unknown[qace_1_x68232]" (7) or "unknown[sitabcd_1_ay598030]" (6). Each counts as its own "class". 5 samples are multi-resistant only because of them.
  3. A third defect, found by me: the formula counts DRUGS, not classes. Sample 11843673 has gentamicin and spectinomycin (both aminoglycosides) and is flagged "Yes".
- Today (RUN, engine and plain Polars from the raw files agree): 70 rows, 38 samples, 16 samples multi-resistant, 46 of the 70 rows carry "Yes". The raw file has 70 rows and 38 samples; the metadata has 42 samples; the inner join keeps 38; 4 metadata samples have no hit.

**Is the definition written by Eve? (READ, git history)**
- Yes for the number of classes. Her own words of 2026-04-23, file `EVE_WORK/daily/2026-04-23/Instructions.md`, committed in `6eb809ca` (2026-04-23): "multi-resistant (meaning resistant to more than one class of antimicrobials)". So ">1 class" is hers. The first formula in that commit counted `phenotype_clean`, i.e. drugs, from the start.
- Not written by her: what a class is for the `unknown[...]` hits; and whether to count drugs or classes. The drug-to-class table `config/references/amr_phenotypes/test_amr_categories_phenotype.tsv` (README: "to their broader drug class (e.g., Beta-lactams)", commit `c2d0436f`, 2026-03-08) is the only written definition of "class". It has 17 drugs. It has no row for kanamycin (8 hits) or sulfisoxazole (8 hits), so 16 of the 70 hits have no class with that table as it is, besides the 13 unknown ones (RUN: 41 of 70 hits get a class).
- Question for Eve: Q1 below.

**Counts under each reading (RUN, plain Polars from the raw files; the engine gives the same for the two readings that are recipe steps)**

| Reading | Multi-resistant samples of 38 | Comment |
|---|---|---|
| Today | 16 | |
| A1: missing values not counted (the coordinator's provisional N21) | 16 | no shipped number moves (engine run: same table, same hashes) |
| A2: A1 and `unknown[...]` left out | 11 | 5 samples change; recipe steps below (engine run: 11) |
| A2b: all `unknown[...]` as one class "unknown" | 16 | no change |
| A3: classes by the table as it is | 6 | too low: 29 of 70 hits have no class |
| A4: classes, kanamycin to Aminoglycosides and sulfisoxazole to Sulfonamides added to the table, unknown left out | 10 | 6 samples differ from today |
| A5: classes from the column "CGE Predicted Phenotype" through the table | 17 | see Q2: the two phenotype columns agree on 6 of 70 rows in this dummy data |

**Per sample, only the samples that differ (RUN, `a_table.py`)**

| sample | phenotypes of its hits | today | A2 | A4 | A5 |
|---|---|---|---|---|---|
| 11843673 | gentamicin, spectinomycin | Yes | Yes | No | Yes |
| 20545497 | tetracycline, unknown[sitabcd] | Yes | No | No | Yes |
| 25542390 | ampicillin, unknown[qace] | Yes | No | No | Yes |
| 29208527 | trimethoprim, unknown[sitabcd] | Yes | No | No | Yes |
| 32557144 | tetracycline, unknown[sitabcd] | Yes | No | No | Yes |
| 51573804 | tetracycline, unknown[qace] | Yes | No | No | No |
| 66678807 | trimethoprim | No | No | No | Yes |
| 71729785 | kanamycin | No | No | No | Yes |

**The change (exact).** Patch files, applied on `config/data_analysis_recipes/pipelines` with `patch -p1` (RUN: they apply cleanly):
- `patch_A1_nulls_only.patch` (one line, the coordinator's provisional default). Old line 36: `      is_multi_resistant_bool: pl.col('predicted_phenotype_clean').n_unique().over('sample_id') > 1`. New: `      is_multi_resistant_bool: pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id') > 1`.
- `patch_A2_unknown_out.patch` (on top of A1; only after Eve answers Q1). New step after step 1 (inserted after old line 13):
```
  # Step 1b: the phenotypes that count as a resistance (an "unknown[...]" or a missing phenotype is not a class)
  - action: polars_with_columns
    named_exprs:
      counted_phenotype: "pl.when(pl.col('predicted_phenotype_clean').str.starts_with('unknown')).then(pl.lit(None, dtype=pl.String)).otherwise(pl.col('predicted_phenotype_clean'))"
```
  and line 36 becomes `is_multi_resistant_bool: pl.col('counted_phenotype').drop_nulls().n_unique().over('sample_id') > 1`. The published columns do not change (`counted_phenotype` is not in the final select). The checker passes with no new advice (RUN).
- Also change the comment of step 4 so it says the rule: "Yes when the hits of the sample name more than one phenotype; missing phenotypes and unknown[...] do not count; a phenotype is a drug, not a class".

**Results that change with A2 (RUN, engine and plain Polars equal)**
- Table `AMR_Profile_Joint`: same 70 rows, same order, same columns; only `Multiresistant` changes: 46 "Yes" rows become 36 (16 samples become 11).
- Plot `multi_resistance_by_country` (bars count ROWS, not samples): the 11 bar groups become 10.

| Country, Year | No before to after | Yes before to after |
|---|---|---|
| Germany 2024 | 3 to 5 | 2 to 0 (bar gone) |
| Norway 2022 | 5 to 9 | 7 to 3 |
| Norway 2024 | 10 to 14 | 21 to 17 |
| other groups | unchanged | unchanged |

  Samples with "Yes": Germany 4 to 3, Norway 12 to 8. Pictures: 6.9 percent of the pixels differ (country), 16.7 percent (source). Plot `multi_resistance_by_source`: Broiler No 6 to 8, Yes 17 to 15; Layer No 11 to 15, Yes 13 to 9; Parent No 7 to 11, Yes 16 to 12 (rows).
- A1 moves nothing (RUN: the golden check on A1 alone reports "result-identical").

**Tests that must exist**
1. `app/tests/test_amr_multiresistance_formula.py` (new). Run the real shipped fragment on a tiny made-up table: one drug plus one missing phenotype gives No; two drugs gives Yes; all missing gives No; one drug plus `unknown[x]` gives No (A2); `unknown[x]` alone gives No; `Tetracycline` and ` tetracycline ` count once. Break test: put back `n_unique()` and see the first case fail.
2. Shipped data: with A1 the number of "Yes" samples is 16 and the same hash as the baseline; with A2 it is 11 and the five samples named above change. Assert the sample list, not only the count.
3. `app/tests/equality/reference_2_test_data_ST22_dummy.py` line 105 uses `drop_nulls()` only (READ). With A2 the engine says 11 and the reference 16, so the clean cases fail: add the same "unknown" exclusion to the reference. The four dirty copies `app/tests/equality/recipes/*/assembly/AMR_Profile_Joint.yaml` line 29 hold the old formula (READ): give them the same fix, otherwise finding F1 stays open there. I did not run the repo equality tests against the patch.
4. `libs/utils/tests/test_formula_check.py` line 31 lists the old formula as an accepted example (READ). It stays valid; add the new `counted_phenotype` formula to the list (the checker accepts it: RUN).

## B. The 37 missing descriptions

**What is wrong (RUN, `check_show.py`).** The checker gives 37 advices on the 7 shipped pipelines: 14 schemas (S04), 9 joins (J03), 6 groups (G02), 8 plots (P02): 1_Abromics 7, 1_test_data_ST22_dummy 7, 2_test_data_ST22_dummy 10, 3_test_no_joins 2, demo_abromics 4, figshare_integration 3, stress_test_master 4. (The same kinds of advice, plus 8 about a missing `info.contact`, also appear on 4 retest recipes and 4 templates: 35 more; not asked, not touched.)

**The change.** The descriptions are in `patch_B_descriptions.patch` (apply with `patch -p1`; RUN: applies) and listed below. Each is one `description:` line placed after the `label:` line of its node, with the same indent as `label:`. After the patch: 37 advices become 0 (RUN, all 7 recipes), and the golden check says "result-identical" (RUN): descriptions change no table. (They change the recipe file hash, so the stored tables of ADR-089 rebuild once.)

Each description says what one row is, or what the bars count, in the plain facts of the data (RUN counts in the facts script `b_facts.py`). Plots that count rows say so, because a sample with more hits then weighs more.

| # | file (config/data_analysis_recipes/pipelines/) | kind and path | insert after old line | description to paste |
|---|---|---|---|---|
| 1 | 1_Abromics_general_pipeline.yaml | schema `data_schemas.MLST` | 20 (indent 4) | One row per sample: the MLST sequence type (strain type from seven gene alleles) of each isolate. |
| 2 | 1_Abromics_general_pipeline.yaml | schema `metadata_schema` | 29 (indent 2) | One row per sample with its source, year and country of isolation. |
| 3 | 1_Abromics_general_pipeline.yaml | schema `additional_datasets_schemas.VirulenceFinder` | 41 (indent 4) | One row per sample and virulence gene found by VirulenceFinder, with the serotype of the sample. |
| 4 | 1_Abromics_general_pipeline.yaml | schema `additional_datasets_schemas.APEC_STEC_virulence_genes` | 50 (indent 4) | Reference list with one row per virulence gene of interest (APEC and STEC); used to keep only these genes from the VirulenceFinder hits. |
| 5 | 1_Abromics_general_pipeline.yaml | group `analysis_groups.MLST_Overview` | 73 (indent 4) | Which sequence types occur, and in which countries and sources. |
| 6 | 1_Abromics_general_pipeline.yaml | plot `analysis_groups.MLST_Overview.plots.abromics_st_by_country` | 76 (indent 8) | Bars count the rows of the table (one per sample and selected virulence gene, so a sample with more genes weighs more) for each sequence type, coloured by country. |
| 7 | 1_Abromics_general_pipeline.yaml | plot `analysis_groups.MLST_Overview.plots.abromics_st_by_source` | 93 (indent 8) | Bars count the rows of the table (one per sample and selected virulence gene, so a sample with more genes weighs more) for each sequence type, coloured by source. |
| 8 | 1_test_data_ST22_dummy.yaml | schema `data_schemas.Summary_quality` | 29 (indent 4) | The same file as Summary, read as one row per sample with its quality columns (main taxon, genotype, phenotype, plasmid, ST, genome length, N50, contigs), so the phenotype counts can be joined to the quality values. |
| 9 | 1_test_data_ST22_dummy.yaml | join `joins.FastP_with_metadata` | 162 (indent 4) | One row per sample: the FastP read-quality values with the sample's source, year and country; a left join on the sample id, so every FastP sample stays. |
| 10 | 1_test_data_ST22_dummy.yaml | join `joins.Quast_with_metadata` | 169 (indent 4) | One row per sample and assembly measure (N50, total length, largest contig): a left join with the metadata, then the three measure columns turned into rows so the plots can facet by measure. |
| 11 | 1_test_data_ST22_dummy.yaml | join `joins.Bracken_with_metadata` | 176 (indent 4) | One row per sample: the main taxon found by Bracken and its proportion, with the sample's source, year and country (left join). |
| 12 | 1_test_data_ST22_dummy.yaml | join `joins.ResFinder_with_metadata` | 183 (indent 4) | One row per resistance gene hit in a sample, with the sample's source, year and country; a left join from the hits, so a sample with no hit has no row. |
| 13 | 1_test_data_ST22_dummy.yaml | join `joins.MLST_with_metadata` | 190 (indent 4) | One row per sample: sequence type with source, year and country (left join); the second stage keeps only the years 2023 to 2025 and adds an era (Early before 2024, Recent from 2024). |
| 14 | 1_test_data_ST22_dummy.yaml | join `joins.QC_Reads_Anchor` | 197 (indent 4) | One row per sample with read quality (FastP), assembly quality (Quast), main taxon (Bracken) and source, year, country; three left joins on the sample id, so every FastP sample stays. |
| 15 | 2_test_data_ST22_dummy.yaml | schema `metadata_schema` | 23 (indent 2) | One row per sample with its source, year and country of isolation. |
| 16 | 2_test_data_ST22_dummy.yaml | schema `data_schemas.amr_data` | 34 (indent 4) | One row per resistance gene hit reported by ResFinder (a sample can have several); only hits with identity of at least 90 and overlap of at least 60 percent are kept. |
| 17 | 2_test_data_ST22_dummy.yaml | schema `data_schemas.plasmid_data` | 43 (indent 4) | One row per plasmid hit reported by PlasmidFinder (a sample can have several); only hits with identity of at least 90 and overlap of at least 60 percent are kept. |
| 18 | 2_test_data_ST22_dummy.yaml | join `joins.AMR_Profile_Joint` | 54 (indent 4) | One row per resistance gene hit with the sample's source, year and country (inner join: a sample with no hit, or not in the metadata, has no row), and the flag Multiresistant that is Yes when the sample has hits for more than one predicted phenotype (unknown and missing phenotypes are not counted). |
| 19 | 2_test_data_ST22_dummy.yaml | join `joins.Plasmid_Profile_Joint` | 60 (indent 4) | One row per plasmid hit with the sample's source, year and country (inner join: a sample with no plasmid hit, or not in the metadata, has no row), sorted by year, source and country. |
| 20 | 2_test_data_ST22_dummy.yaml | group `analysis_groups.AMR_Insight` | 71 (indent 4) | How many resistance gene hits come from multi-resistant samples, by year, country and source. |
| 21 | 2_test_data_ST22_dummy.yaml | plot `analysis_groups.AMR_Insight.plots.multi_resistance_by_country` | 74 (indent 8) | Bars count resistance gene hits (rows, not samples: a sample with more genes weighs more) per year, coloured by whether the sample is multi-resistant, one panel per country. |
| 22 | 2_test_data_ST22_dummy.yaml | plot `analysis_groups.AMR_Insight.plots.multi_resistance_by_source` | 77 (indent 8) | Bars count resistance gene hits (rows, not samples: a sample with more genes weighs more) per year, coloured by whether the sample is multi-resistant, one panel per source. |
| 23 | 2_test_data_ST22_dummy.yaml | group `analysis_groups.Plasmid_Insight` | 80 (indent 4) | Which plasmid types are found, by year and country. |
| 24 | 2_test_data_ST22_dummy.yaml | plot `analysis_groups.Plasmid_Insight.plots.plasmid_prevalence_by_country` | 83 (indent 8) | Bars count plasmid hits (rows, not samples) per year, coloured by plasmid name, one panel per country. |
| 25 | 3_test_no_joins.yaml | group `analysis_groups.no_join_group` | 32 (indent 4) | One plot drawn straight from a data table with no join, to show that a recipe can do without joins. |
| 26 | 3_test_no_joins.yaml | plot `analysis_groups.no_join_group.plots.sequence_type_counts` | 35 (indent 8) | Bars count samples (one row per sample) for each MLST sequence type. |
| 27 | demo_abromics.yaml | schema `data_schemas.MLST` | 12 (indent 4) | One row per MLST result of a sample; in this demo file a sample can appear on more than one row. |
| 28 | demo_abromics.yaml | schema `metadata_schema` | 21 (indent 2) | One row per metadata line (source, year, country); in this demo file some sample ids are repeated, empty or written as a dash. |
| 29 | demo_abromics.yaml | group `analysis_groups.MLST_Overview` | 58 (indent 4) | Which sequence types occur in each source. |
| 30 | demo_abromics.yaml | plot `analysis_groups.MLST_Overview.plots.demo_st_by_source` | 61 (indent 8) | Bars count the rows of the joined table (a sample repeated in the data counts more than once) for each sequence type, coloured by source. |
| 31 | figshare_integration.yaml | schema `data_schemas.fg_metadata` | 23 (indent 4) | One row per animal sample with host species, specimen source, final diagnosis and infection site. |
| 32 | figshare_integration.yaml | schema `data_schemas.fg_phenotypes` | 33 (indent 4) | One row per sample and antibiotic test (MIC id) with the breakpoint and the predicted phenotype. |
| 33 | figshare_integration.yaml | schema `data_schemas.fg_genotypes` | 43 (indent 4) | One row per sample and resistance gene with its type, identifier, gene family and resistance class. |
| 34 | stress_test_master.yaml | schema `data_schemas.Stress_Source` | 12 (indent 4) | One row per synthetic record (species, collection date, antibiotic class, value); generated to test speed, not real isolates. |
| 35 | stress_test_master.yaml | join `joins.Master_Collection` | 22 (indent 4) | The stress table as it is (no join step), kept as the one collection the plot reads. |
| 36 | stress_test_master.yaml | group `analysis_groups.Stress_Distribution` | 30 (indent 4) | How the synthetic records spread over species and antibiotic classes, to test that a large plot stays responsive. |
| 37 | stress_test_master.yaml | plot `analysis_groups.Stress_Distribution.plots.stress_species_amr` | 33 (indent 8) | Bars count records for each species, coloured by antibiotic class. |

Also wrong, found while writing them (RUN): the existing description of the join `demo_join` in `demo_abromics.yaml` says "One row per sample". The data gives 28 rows for 15 samples: MLST has 30 rows for 17 samples (one id 6 times), and the metadata has repeated, empty and "-" ids. Replace with: "One row per MLST result joined to a metadata line (inner join); a sample that is repeated in the data appears more than once." Not in the patch; I did not want to change an existing text without telling you.

The wording of row 12 (`AMR_Profile_Joint`) follows reading A2. If Eve picks another reading in Q1, change its last clause.

**Tests that must exist.** `app/tests/test_shipped_recipes_pass_the_checker.py` only asserts "no error" (READ). Add: every file under `config/data_analysis_recipes/pipelines` gives zero advice of the codes S04, J03, G02, P02 (and its own break test: remove one description and see the test fail). Keep it to pipelines: retest recipes and templates still carry 35 advices.

## C. Every gallery example (`assets/gallery_data/`)

**Result (RUN, `gallery_run.py`, `gallery_adv.py`, `gallery_seed.py`): nothing to fix.**
- 34 example folders. All 34 have `spec_version: 1`, all 34 pass the checker in the profile gallery with the registries (coverage: structure, actions, components), all 34 are in `gallery_index.json` (34 listed, `metadata.rejected` empty). No example is left out.
- All 34 are built and drawn by the app's own path (`example_table`, `render_example`: ConfigManager, DataOrchestrator, VizFactory) and the table equals the plain reading of the data file. Each picture is pixel-identical to the committed `preview_plot.png` (0.0 percent differ, 34 of 34). The two examples with a random layer (`jitter_strip`, `beeswarm_sina`) write `random_state: 0`.
- The only message is advice I02 "info.contact is missing" on all 34 (no change of any result). The 7 shipped pipelines all carry the contact line. Adding it to the gallery is a choice for the builder; not needed for "every recipe works".
- Existing tests already pin this: `app/tests/test_gallery_app_path.py` (WAITING is empty, every example drawn), `app/tests/test_gallery_full_check.py` line 65 (rejected is empty).
- So the coordinator's wording "the work is to leave nothing out" is already done at HEAD `3d69e14f`. The earlier left-out examples were converted before (READ: for example `beeswarm_sina` in commit `5363c930`). Failures to list: none. Examples the index leaves out: none.
- I could not use `assets/scripts/refresh_gallery.py` and `gallery_previews.py` (the permission system refused the first call); I called the same functions they call (`check_gallery`, `render_example`).

**Test that must exist:** none new. Keep the two above. One suggestion: add the contact line check only if Eve wants I02 to be zero.

## D. Fragments that no recipe includes

**Found (RUN, `unwired.py`: `ConfigManager.loaded_files` for every recipe of `pipelines`, `templates`, `retest`, `experimental`).** 6 fragments, the same 6 as the existing list `KNOWN_FRAGMENTS_INCLUDED_BY_NOTHING` in `app/tests/test_resfinder_abromics_fragment.py` (READ). Also found: `config/data_analysis_recipes/experimental/test_logic.yaml` is an EMPTY file (0 bytes, RUN). `ConfigManager` crashes on it (`TypeError: argument of type 'NoneType'`); nothing reads it (READ, grep). It is not current: delete (Eve's cleaning rule). I archive nothing: `config/data_analysis_recipes/2026-04-10_pipelines.tar.gz` is an April archive of old pipelines that already exists.

| # | File (under `pipelines/`) | What it holds | Decision | Result that changes |
|---|---|---|---|---|
| a | `1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly_output_fields.yaml` | The old output-fields list of the phenotype view (5 columns; the format has no such list) | DELETE (Eve: "remove old output fields") | none |
| b | `1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml` | A box plot of `total_reads` with `x: sample_id` on table FastP, target not wired; old title "Total Reads by Sample (QC)" | WIRE, but changed (see below) | one new plot, no existing picture |
| c | `1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml` | One left join of the Detailed summary with the metadata, in the removed action form (`action: "join"`, no `tier1:`) | WIRE as a new join `Detailed_summary_with_metadata` | one new table: 91 rows, 36 samples, 16 columns, 0 rows without metadata |
| d | `1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml` | An old-format list of PlasmidFinder input fields (`type: numeric`, `is_primary_key`) filed in `wrangling/` | DELETE | none |
| e | `stress_test_master/plots/final_plot.yaml` | The richer stress plot: bars side by side, palette Set1, no `target_dataset` | WIRE: the recipe includes it instead of its inline plain plot | the stress picture changes; the plot table does not |
| f | `1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml` | The converted ResFinder piece (item E) | WIRE (item E) | new table and new plot |

Intent, from the history (READ):
- (b) The plot spec was first committed on 2026-04-10 (`b9a09e72`); the design note `.claude/design/plot_authoring_model.md` shows it in an older form with `factory_id: boxplot_logic`. `.claude/design/recipe_review_st22_2026-11-11.md` row 14 lists it as "mounted by no group", "keep or remove on purpose". The wired plot `qc_reads_horizontal_barplot` already shows total reads per sample. **Scientific problem (RUN):** FastP has exactly one row per sample (42 rows, 42 samples). A box plot per sample has one value per box: 42 empty boxes. As written it cannot be a box plot. I wire it by SOURCE: target `FastP_with_metadata` (the join exists), `x: source`, `y: total_reads`. RUN, from the raw files and the engine: Broiler 13 samples, median 1,653,504 reads; Layer 19, 2,534,734; Parent 10, 2,468,538. This changes the old intent (per sample to per source). It is my choice and I tell Eve in point 3 of the list "What Eve must be told" in F; the file is easy to revert.
- (c) The old comments in the recipe (commit `7e3839b5`, 2026-04-13) say the Detailed summary is meant for "a barplot for each isolate ... predicted phenotype ... number of data types that supported the prediction ... facets". So the summary is meant to carry the metadata for those facets. I wire the join only; I do not add that plot (it is a new design). The new collection is read by no plot, like five other `*_with_metadata` collections today.
- (d) The recipe `2_test_data_ST22_dummy` already has the current version of this list (`2_test_data_ST22_dummy/input_fields/plasmid_data.yaml`, same columns that are used, names `plasmid_name`). `1_test_data_ST22_dummy` has no PlasmidFinder table and no plot of plasmids. Wiring it would add a table nothing reads. By Eve's rule (not current: deleted) I delete it. This differs from the literal "b, c, d, e wire".
- (e) The inline plot in the recipe has the same table, same x and fill. The richer file adds `position: dodge`, `scale_fill_brewer` Set1 and an axis label. Set1 has 9 colours; the data has 5 classes (RUN). I add `target_dataset: Master_Collection` and `fill: AMR Class` in the labels (the file lacked both; without the fill label the legend title would turn into `amr_class`).
- Old output-fields mentions left in active files (READ), for the old-words work, not changed here: `1_test_data_ST22_dummy.yaml` lines 15 and 159, `figshare_integration.yaml` line 20, `1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml` lines 15 to 54, `1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml` line 18, `config/data_analysis_recipes/README.md` lines 11 and 51.

**The change (exact).** `patch_D_fragments.patch` (apply after B). It contains: delete a and d; the new content of c (`tier1:` then one `polars_join` left on `sample_id`, `maintain_order: left_right`); the new content of b (`target_dataset: FastP_with_metadata`, `x: source`, `y: total_reads`, `geom_boxplot`, title "Total Reads by Source (QC)"; the old keys `family`, `pattern`, `difficulty` are dropped because the group entry carries taxonomy); in `1_test_data_ST22_dummy.yaml` the join `Detailed_summary_with_metadata` and, in the group "Quality Control", the plot `fastp_reads_boxplot`; the new `final_plot.yaml` and in `stress_test_master.yaml` the inline spec replaced by `spec: !include 'stress_test_master/plots/final_plot.yaml'`. Also delete `config/data_analysis_recipes/experimental/test_logic.yaml` (not in the patch).
Checks (RUN): checker 0 problems; the golden check shows exactly the new tables and plots and no change of an existing hash (items b, c); `test_shipped_recipes_hygiene` logic on the patched recipes: 21 passed.

**Pictures (RUN, pixel comparison of the 27 plots of 6 pipelines before and after A2 + B + D + E):** 22 identical; changed: `stress_species_amr` 43.4 percent of pixels (stacked bars become side by side, Set1 colours); `multi_resistance_by_country` 6.9 percent and `multi_resistance_by_source` 16.7 percent (item A2); new: `fastp_reads_boxplot` and `amr_classes_per_sample`. `figshare_integration` was not redrawn (203,146-row table; the golden hash check shows no change).

**Tests that must exist.**
- `KNOWN_FRAGMENTS_INCLUDED_BY_NOTHING` in `app/tests/test_resfinder_abromics_fragment.py` becomes the empty set; the test `test_the_fragments_that_nothing_includes_are_exactly_the_known_ones` fails today against the patch (RUN) and must be changed; the finder `test_the_orphan_finder_can_fail` stays. Move the finder into its own test file (it no longer belongs to the ResFinder test).
- A test that a recipe file that loads to nothing (empty file) is a named error, not a crash: `ConfigManager` on `experimental/test_logic.yaml` gives `TypeError` (RUN). Fix the loader or delete the file; if the file is deleted, no test is needed, but the crash stays for any empty recipe the user uploads (it is a loader defect: say so to the builder).
- A test that the box plot of item b has more than one row per box: every box has at least 2 values (the defect I found would otherwise return).

## E. The ResFinder rule

**The old thresholds (RUN git history, READ files).** There is no filter in the old ResFinder_Abromics fragment itself (its three old steps: `derive_categories`, `drop_duplicates` on the gene, `summarize`; READ in `a6335403^`). The "minimum identity and minimum coverage" she recalls exist in two places, with different values. "Coverage" is the column `%Overlap`.

| Where | Commit and date | Values | Applies to |
|---|---|---|---|
| Detailed summary of `1_test_data_ST22_dummy` | `0eaa070a`, 2026-04-10 15:49 (comment); `3945d110`, 2026-04-10 22:15 (code `filter_range`) | identity at least 90, overlap at least 85, length ratio at least 0.8 (the comment says ">", the code is inclusive: `filter_range` min is `>=`, READ in `0eaa070a:libs/transformer/src/transformer/actions/cleaning/core.py`). The recipe today (`Detailed_summary_wrangling.yaml` lines 20 to 34) has `ge` 90, 85, 0.8; line 54 of `1_test_data_ST22_dummy.yaml` still says ">" | the Detailed summary table (280 rows, 91 left) |
| AMR lineage of `2_test_data_ST22_dummy` | `6eb809ca`, 2026-04-23 ("Defined detection thresholds: 90% identity, 60% overlap", from the agent log; Eve had asked "What are the traditional thresholds ... we need to find out in the scientific literature") | identity at least 90, overlap at least 60; still in `2_test_data_ST22_dummy/wrangling/amr_data.yaml` lines 2 to 11 | the ResFinder file itself (70 rows) |

I could not find them in the tarball `2026-04-10_pipelines.tar.gz` (RUN: only field lists). I did not search the sibling folder EVE_WORK (the permission system refused). 90 percent identity and 60 percent length are, from my memory of the ResFinder documentation, the tool's own defaults (external, not verified here). Question Q3.

**Numbers on the shipped ResFinder file (RUN, engine and plain Polars equal):**

| Step | Rows | Samples |
|---|---|---|
| Raw file (`test_data_ResFinder_20260307_105756.tsv`) | 70 | 38 |
| Filter identity at least 90 and overlap at least 60 | 70 (0 removed; lowest identity 94.98, lowest overlap 65.00) | 38 |
| Same with overlap at least 85 | 36 (34 removed) | 22 (16 samples lose every hit) |
| Best hit per sample and gene (90/60) | 63 | 38 |
| Best hit per sample and gene (90/85) | 34 | 22 |
| Final table sample by class (90/60) | 60 rows, 38 samples, 7 classes, sum of `gene_count` 63 | |
| Final table (90/85) | 32 rows, 22 samples | |
| OLD rule (one row per gene over ALL samples, no filter) | 70 to 13 rows, then 12 rows, 10 samples | |

Per sample and gene there are 63 pairs; 5 pairs have more than one row (12 rows), so 7 rows are dropped. In 4 of the 63 rows the best hit is not the first row in the file. In none of the 5 pairs is the best hit tied on identity and overlap (float values with 15 digits). The old rule kept 13 of 70 hits and represented 10 of 38 samples; the class totals were 2, 1, 3, 2, 1, 2, 2 against 18, 7, 8, 8, 9, 7, 6 now. The old golden file `old_final.tsv` (12 rows) is therefore a wrong reference for the new rule.

**The rule as recipe steps (RUN, in the scratch recipe; in `patch_E_resfinder_rule.patch`).** In `ResFinder_Abromics_wrangling.yaml`, keep steps 1 to 8 (classes from the drug names; unchanged, so the old test of those 8 steps still passes), then replace the old steps 9 and 10 (`polars_unique` on `gene`, `polars_group_by`) by:
```
  - action: polars_drop_nans
    subset: [identity, overlap]
  - action: modif_filter
    column: identity
    op: ge
    value: 90          # Q3: 90 / 60 is my default
    na: remove
  - action: modif_filter
    column: overlap
    op: ge
    value: 60
    na: remove
  - action: polars_sort
    by: [identity, overlap, accession]
    descending: [true, true, false]
    nulls_last: true
    maintain_order: true
  - action: polars_unique
    subset: [sample_id, gene]
    keep: first
    maintain_order: true
  - action: polars_sort
    by: [sample_id, AMR_Categories_Summary]
    maintain_order: true
  - action: polars_group_by
    by: [sample_id, AMR_Categories_Summary]
    maintain_order: true
    named_aggs:
      gene_count: "pl.col('AMR_Categories_Summary').count()"
```
Why each step:
- `polars_drop_nans` is not in Eve's words. Polars sorts a NaN above every number, so a NaN identity would sort FIRST in a descending sort and be kept as the "best" hit, and `na: remove` does not remove NaN (READ: the earlier equality check, finding N24, ran this). The step changes nothing on the shipped data (0 NaN). I propose it; Eve can strike it.
- Order: highest identity first, then highest overlap (her words "identity and coverage"). In 4 of 63 kept rows the choice between "identity first" and "overlap first" changes the row (RUN).
- **Tie rule (mine, for Eve to see):** two rows with the same identity and the same overlap: the one with the lowest accession (text order) is kept; if the accession is the same too, the first row of the file is kept. It is deterministic because the sort is stable (`maintain_order: true`) and the three keys are written; the accession rule does not depend on the order of the file. Cost: the table needs the column `accession` declared as `String` (not `Categorical`: Polars sorts a Categorical by the order of first appearance, not by the text, unless told otherwise; this was a trap I checked in the equality notes). Missing accession goes last (`nulls_last`). Real ResFinder files can have ties (reasoned, not run: two identical copies of a gene in one genome, 100 and 100): there the class and the count do not depend on which copy is kept when accession and drug list are the same.
- Last sort: states the order of the result; without it the rows come in the order of the identity sort.
- `gene_count` counts rows with a class; a gene with no class would give a row with an empty class and count 0. On the shipped data every drug is in the table (RUN: 0 unmapped), so no such row exists.

**Where it is wired (N10: a recipe uses that data).** `1_test_data_ST22_dummy` uses that same ResFinder file (and `2_test_data_ST22_dummy` as `amr_data`). The piece needs a base table with `cge_predicted_phenotype`, `identity`, `overlap`, `accession`, and the reference table as a second ingredient. The existing `ResFinder` schema of the recipe does not declare `cge_predicted_phenotype` or `accession`; adding them would add columns to `ResFinder_with_metadata`, `ST22_Anchor`, three QA tables and the heat map table (their hashes would change). So I add two NEW schemas instead, the way `Summary_quality` already reads the file of `Summary` a second time:
- `ResFinder_drugs` (data_schemas; same file; fields sample_id, gene, cge_predicted_phenotype, identity, overlap, accession; types String and Float64),
- `AMR_phenotype_reference` (additional_datasets_schemas; `./config/references/amr_phenotypes/test_amr_categories_phenotype.tsv`; fields phenotype_name, amr_class, both String),
- the join `ResFinder_AMR_classes` (ingredients ResFinder_drugs, AMR_phenotype_reference; steps `!include` the piece),
- one plot `amr_classes_per_sample` in the group Results: `geom_col`, `x: sample_id`, `y: gene_count`, `fill: AMR_Categories_Summary`, `coord_flip`, axis labels. The plot is mine (without it the user never sees the result); it is a new picture, no old one changes.
Files: two new `input_fields` files, one new `plots` file, the edited `1_test_data_ST22_dummy.yaml`. Checker: 0 problems (RUN). The header comment of the piece must be rewritten (it still says "included by no shipped recipe" and describes the old per-gene rule).

**Result:** one new table `ResFinder_AMR_classes` (60 rows) and one new plot; no existing table or plot of any recipe changes (golden check, RUN: E alone adds 3 new entries: t1 and t2 of `ResFinder_AMR_classes` and the plot; D alone adds 3: t1 and t2 of `Detailed_summary_with_metadata` and the plot `fastp_reads_boxplot`; no existing hash changes). Applying the same rule to `2_test_data_ST22_dummy` is NOT done here (Q4): it would change 70 rows to 63, and the multi-resistant samples from 16 to 15 (today's formula) or from 11 to 10 (A2); the sample that flips is 12244317 (RUN, `e_on2.py`).

**Tests that must exist (in `app/tests/test_resfinder_abromics_fragment.py`).**
- The first 8 steps keep their tests (RUN: 6 of 8 tests pass against the patch).
- `test_the_whole_fragment_gives_the_old_final_table` (12 rows) fails against the new rule (RUN). Replace with: the final table equals a plain-Polars reading of the raw file written in the test (60 rows; the numbers above), AND a made-up table with these cases: a row below the identity threshold is removed; a sample whose only hit is below the threshold has no row; two rows of one sample and gene with different identity keep the higher; same identity, higher overlap kept; same identity and overlap, different accession: the lower accession kept, whatever the order of the rows in the file (run with the file order reversed and get the same result); tied on all three: the first in the file; NaN identity is removed; empty identity is removed; the same gene in two samples is kept twice (the old rule would keep one).
- Break test: put back `subset: [gene]` and see the "same gene in two samples" case fail.
- Because `accession` must be a String, add a case where the accession values are numbers-as-text.

## F. Order of the work, what changes, questions for Eve

**Order (independent commits; each leaves the tests green).**
1. A1 (one line, nothing moves). Also the four dirty equality copies (same line). Tests: item A 1 and 4.
2. B (37 descriptions) + the new "no advice" test. Result-identical (golden check, RUN). Can break: nothing but the file hash (caches rebuild).
3. D (fragments) with the `KNOWN_FRAGMENTS` list set to the empty set and the golden baseline regenerated (new entries only: 6). Can break: `test_resfinder_abromics_fragment.py` (the known-list test), the golden test.
4. E (the rule and its wiring). Same files as D for `1_test_data_ST22_dummy.yaml`, so it comes after D (the patches are made in this order and apply in it, RUN). Can break: `test_the_whole_fragment_gives_the_old_final_table`; the golden test (6 new entries; with D the 12 together).
5. A2 only after Eve answers Q1. Can break: the equality reference, the golden baseline (4 changed hashes), and the description of row 12.
The golden baseline is regenerated once per commit that changes it (`assets/scripts/golden_baseline.py --out`, message says why). I checked every state with `assets/scripts/golden_baseline.py --recipes-dir <scratch> --check app/tests/golden/baseline.json` (RUN).

**What changes in the golden baseline (RUN, all five commits together: 10 differences).**
- New entries (6, all in `1_test_data_ST22_dummy`): t1 and t2 of `Detailed_summary_with_metadata`, t1 and t2 of `ResFinder_AMR_classes`, plots `fastp_reads_boxplot` and `amr_classes_per_sample`.
- Changed hashes (4, only with A2): `2_test_data_ST22_dummy` t1 and t2 of `AMR_Profile_Joint`, plots `multi_resistance_by_country` and `multi_resistance_by_source`. With only A1, B, D, E: no changed hash.
- No committed picture of a shipped pipeline exists (READ: `git ls-files` shows PNG only in the gallery and the docs); the gallery pictures do not change. The changed pictures are the three listed in D.

**Questions only Eve can answer (checked against the ledger N01 to N52, tasks.md sections 6 and 7 and the channel; no record answers them).**
- **Q1.** Is `unknown[...]` a resistance class when deciding "multi-resistant"? (a) keep as it is and say so in the plot title: 16 samples; (b) leave it out: 11 (A2); (c) count classes through the drug-to-class table once it covers kanamycin and sulfisoxazole: 10 (A4); the table is hers to extend. **Default: (b) now, (c) later.** Record: asked by the coordinator in M95 (N22), never answered; tasks.md only has N21.
- **Q2.** Only if Q1 is (c): which column gives the drug for the class, "Predicted Phenotype" (used today) or "CGE Predicted Phenotype" (the drug lists the table was made for)? In the dummy data they agree on 6 of 70 rows (RUN); with the CGE column the count is 17. **Default: "Predicted Phenotype".**
- **Q3.** Which thresholds does the ResFinder rule use? (a) identity at least 90 and overlap at least 60 (the AMR lineage of 2026-04-23; no hit removed on the shipped file); (b) identity at least 90, overlap at least 85 and length ratio at least 0.8 (the Detailed summary of 2026-04-10; on the ResFinder file 35 of 70 hits and 17 of 38 samples would go (RUN); with identity and overlap only, 34 and 16; the ratio needs the HSP column, which the ResFinder file also has but the recipe does not declare). **Default: (a).**
- **Q4.** Does the per sample and gene rule apply to the AMR lineage of `2_test_data_ST22_dummy` too (70 to 63 rows; 16 to 15 or 11 to 10 multi-resistant samples)? Her words name only the converted piece. **Default: no.**

**What Eve must be told to choose well (not questions).**
1. "Multi-resistant" here means more than one class (her words of 2026-04-23). The common definition in surveillance (multidrug-resistant) is resistance in at least three classes (external, from memory of the standard definition; not checked here). A reviewer can ask. The plot title and the description of `AMR_Profile_Joint` should say which rule is used.
2. The bars of both multi-resistance plots and the plasmid plot count hit rows, not samples (70 hits for 38 samples). That is stated now in the descriptions (item B); changing the counting is her call.
3. My choices not decided by her: the FastP box plot by source (the old one cannot be a box plot, one value per box); `polars_drop_nans` before the filter; the tie rule (lowest accession, then file order); the extra plot `amr_classes_per_sample`; delete, not wire, the PlasmidFinder list (d); delete the empty `test_logic.yaml`. Each is one hunk of a patch and can be struck.
4. "Best hit" is read as highest identity first, then highest overlap. If overlap were first, 4 of the 63 kept rows would be other rows.
5. The reference table lacks kanamycin and sulfisoxazole; 16 of 70 hits have no class for that reason.
6. Eve's own earlier question (2026-04-23) about the usual thresholds was never answered by a literature source in the repository; both pairs are an agent's choice.

## G. What I did not check
- The full repo test suite against the patches (I ran the hygiene logic, the fragment tests, the checker, the golden check, the renders and the pixel comparison on copies).
- The sibling folder EVE_WORK (access refused), so her earlier chats about the old thresholds are not read.
- `figshare_integration` pictures were not redrawn.
- Whether the Blueprint and HOME screens show the new join and plot correctly.

## H. Scratch files (all in `tmpAI/panel/round7/recipe_fixes/`)
`patch_A1_nulls_only.patch`, `patch_A2_unknown_out.patch`, `patch_B_descriptions.patch`, `patch_D_fragments.patch`, `patch_E_resfinder_rule.patch` (apply in the order A1, B, D, E, A2 with `patch -p1` inside `config/data_analysis_recipes/pipelines`; RUN: B, D, E apply on top of each other and the result equals `s4/`); scripts `unwired.py`, `check_show.py`, `chk.py`, `a_polars.py`, `a_engine.py`, `a_table.py`, `a_v6.py`, `b_desc.py`, `b_facts.py`, `e_polars.py`, `e_polars2.py`, `e_steps.py`, `e_on2.py`, `d_numbers.py`, `gallery_run.py`, `gallery_adv.py`, `gallery_seed.py`, `render_recipe.py`; state folders `s0` (HEAD) to `s4` (all five commits), pictures `png_s0`, `png_s4`, `gallery_png`.
