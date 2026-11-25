# Id consistency of the data files that shipped recipes read (DATA-ID-CHECK-1, 2026-11-17)

Evidence labels: RAN = a small Polars script I ran (`tmpAI/panel/data_ids/scan.py`, `demo.py`, `check.py`, outputs `*_out.txt`); READ = a file I read; REASONED = my inference.

## Finding first

1. One file has a real id defect: the MLST demo file `assets/test_data/demo_high_integrity/test_data_test_data_MLST_results_20260307_105756.tsv`. 30 rows, 17 distinct ids, 8 ids repeat (13 extra rows). All repeats are under the same scheme `ecoli_achtman_4`, so (sample, scheme) repeats too. One isolate has one sequence type per scheme: this is a defect of the synthetic data. RAN.
2. It was written by a generator that draws ids WITH replacement for every table except the metadata. READ.
3. The repeat explains every earlier number of the demo table: "28 rows for 15 samples" and "40 rows for 27 samples" (arithmetic in section 3). RAN.
4. Nothing tells the user today. The recipe check, the data check and the build all print nothing for this repeat. `is_entity_key` does not mean "unique" (section 5). RAN.
5. The demo metadata has a different, known issue: 3 lines without an id (empty, "-", two quote marks). That is the messy-value injection of the same generator, and the recipe already removes them on purpose (D-0167). Not a defect.

## 1. Every data file a shipped recipe reads

"Meant" = what the recipe description and the table type say (READ). Counts are from the raw text, every column as a string (RAN). "No id" counts empty, `-` and `""`.

| File (short) | Read by | Rows | Id column | Distinct | No id | Repeating ids | Exact duplicate rows | Meant | Verdict |
|---|---|---|---|---|---|---|---|---|---|
| demo MLST (`demo_high_integrity/..MLST_results..`) | `demo_abromics` | 30 | `sample_id` (`is_entity_key`) | 17 | 0 | 8 ids: 6,3,2,2,2,2,2,2 (13 extra rows); all under scheme `ecoli_achtman_4` | 0 | one row per (sample, scheme); recipe text says "a sample can appear on more than one row" | REAL INCONSISTENCY |
| demo metadata (`..test_metadata..`) | `demo_abromics` | 30 | `sample_id` (`is_entity_key`) | 27 | 3 (one empty, one `-`, one `""`) | none | 0 | one row per sample | ok after the 3 no-id lines (removed on purpose, D-0167) |
| demo ResFinder (`..ResFinder..`) | nothing (no recipe, no test reads it; only the generator writes it) | 30 | `sample_id` | 22 | 1 (`-`) | one id 4 times, one 3, one 2 | 0 | long (one row per gene) | not used; same generator, so same draw with replacement |
| ST22 metadata `test_metadata_..` | `1_test_data_ST22_dummy`, `2_..` | 42 | `sample_id` | 42 | 0 | none | 0 | one per sample | ok |
| ST22 MLST | `1_test_data_ST22_dummy` | 42 | `sample_id` | 42 | 0 | none | 0 | one per sample | ok |
| ST22 Summary, Quality_metrics, FastP, Quast, Bracken | `1_test_data_ST22_dummy` | 42 each | `sample_id` | 42 each | 0 | none | 0 | one per sample | ok |
| ST22 ResFinder | `1_` and `2_test_data_ST22_dummy` | 70 | `sample_id` | 38 | 0 | 18 ids (max 8) | 0 | long: "a sample can have several" | ok (4 metadata samples have no hit) |
| ST22 PlasmidFinder | `1_`, `2_` | 163 | `sample_id` | 41 | 0 | 41 ids (max 7) | 0 | long | ok (1 sample has no hit) |
| ST22 Detailed_Summary | `1_` | 280 | `sample_id` | 42 | 0 | 42 ids (max 13) | 0 | long | ok |
| ST22 VirulenceFinder (`2_VIGAS-P_ST22_dummy/..`) | `1_`, `1_Abromics_general_pipeline` | 1315 | `sample_id` | 42 | 0 | 42 ids (max 39) | 583 of 1315 | long (a list of genes per row is exploded by the recipe) | ids ok; 583 exact duplicate rows: I did not judge them (see "not checked") |
| `duplicated_1_test_data_ST22_dummy/*` (copy for the connector test) | deployment `pipeline_test`, a test | same counts as ST22 | | same | | same | same | the README says it is a copy | same as the ST22 files |
| `1_test_replacement_data/replacement_metadata.tsv` | no recipe (a replacement upload) | 42 | `sample_id` | 42 | 0 | none | 0 | one per sample | ok |
| figshare `fg_metadata` | `figshare_integration` | 980 | `sample_id` | 980 | 0 | none | 0 | one per sample | ok (a first look at 980 vs 989 distinct was my quote-reading error; read with quotes it is 980/980) |
| figshare `fg_phenotypes`, `fg_genotypes` | `figshare_integration` | 18437 / 10839 | `sample_id` | 980 each | 0 | all (long) | 0 | long | ok |
| `retest/samples.tsv`, `genes.tsv`, `genes_renamed_header.tsv` | retest recipes | 12 / 3 / 3 | `sample_id` | 12 / 3 / 3 | 0 | none | 0 | one per sample | ok |
| `retest/variants.tsv` | `retest_top_n_other` | 21 | `sample_id` | 18 | 0 | `s07` 4 times (4 identical rows) | 4 | on purpose: the file's own header says "Sample s07 has 4 rows of V2" | ok, deliberate |
| `STRESS/STRESS_data.tsv` | `stress_test_master` | 10000 | `id` | 10000 | 0 | none | 0 | one per row | ok |
| `assets/test_data/metadata.tsv` | `complex_template` | 29 | `ID` | 29 | 0 | none | 0 | one per sample | ok |
| `assets/test_data/genomics_data.tsv` | `complex_template` | 30 | none (`Accession`, `Gene_List`) | | | | | | no sample id |
| `assets/ref_data/Virulence_genes_APEC/..` | `1_` | 11 | none (gene list) | | | | | reference list | n/a |
| `simple_data.tsv`, `simple_metadata.tsv`, `ecoli_*.tsv`, `submission_logs.tsv` | templates `simple_template`, `e_coli`, `audit` | | | | | | | | the files do not exist in the repository (RAN: `ls`); those templates cannot be run as shipped |
| 37 gallery `example_data.tsv` | gallery bundles | 4 to 200 | most have none; 12 have a column `id` | `id` is 1 per row in 11 | 0 | `heatmap_correlation`: `id` = `CORR` on all 16 rows (a label, not a sample) | 0 | plot examples, no sample table | no inconsistency |

Files with a real inconsistency: only the demo MLST file. Open to her judgement (not an id defect): the 583 exact duplicate rows of the ST22 VirulenceFinder file; the unusable templates (missing data files).

MLST per (sample, scheme) (RAN): `SYN_74255382` 6 rows with the sequence types 1674, 538, 135, 57, 2040, 2040 and six different locus sets; `SYN_56337687` 3 rows (371, 88, "-"); `SYN_23672090` 2 (54, 57); `SYN_34324619` 2 (1674, unknown); `SYN_38371839` 2 (unknown, 57); `SYN_42120616` 2 (154, 131); `SYN_32804061` 2; `SYN_23559893` 2 (95, 57). Every one is the same scheme, so every one is impossible for one isolate. The demo ResFinder file has repeats too, but there repeats are allowed (one row per gene).

How the recipe reads empty ids (demo metadata): the recipe has `null_values: []` and says all three are read as missing. The built table has 0 missing and no `-` or `""` among its ids, so all three are gone (RAN). I did not trace which code turns `-` and `""` into missing.

## 2. Where the files come from

- Script: `assets/scripts/generate_demo_data.py`, added in commit `67756131` (2026-03-28, "implement pipeline debugging workflow"; the same commit added the three TSV files). READ (`git show --stat 67756131`).
- At that commit it called `AquaSynthesizer.synthesize()` of `libs/generator_utils`. Its code (READ, `git show 67756131:libs/generator_utils/src/generator_utils/aqua_synthesizer.py` lines 48 to 100): the metadata table takes the anchor pool of 30 ids once each. Every other table (MLST, ResFinder) takes `pk_col = random.choices(self.anchor_pool, k=n_rows)`. `random.choices` draws WITH replacement, so ids repeat. Then every column, the id column included, gets "messy" values (`None`, `-`, `unknown`, `N/A`, empty) at 5 percent: that is where the 3 metadata lines without id come from.
- The numbers fit a draw of 30 from 30 with replacement (REASONED): about 19 distinct ids are expected, the MLST file has 17 and the ResFinder file has 22 (+ one `-`). The 2 MLST ids that are not in the metadata (`SYN_38282317`, `SYN_67199832`) are probably ids of the pool whose metadata line had its id blanked by the messy step (REASONED; the pool itself is not stored).
- Today the script cannot run: `synthesize` no longer exists in `libs/test_lab/src/test_lab/aqua_synthesizer.py` (RAN: grep finds the call at `assets/scripts/generate_demo_data.py:58` and no definition). There is no seed in the old code, so even the old run was not reproducible. Its final line "Found N matching IDs (1:1 join success)" only tests that the inner join has at least one row, not that it is 1:1.
- The ST22 data (`1_test_data_ST22_dummy`, `2_VIGAS-P_ST22_dummy`): not synthetic draws. Its README says it was parsed from real pipeline Excel files (`parse_pipeline_excel.py`, `create_test_data.py`), ids re-coded. Its one-row-per-sample tables are unique (table above). No generator repeat there.

## 3. Does the repeat explain the earlier numbers? Yes, fully (RAN, `demo.py`)

- MLST file: 30 rows, 17 distinct ids. Metadata: 27 ids. 2 MLST ids are not in the metadata (2 rows). 12 metadata ids have no MLST row.
- Before ("28 rows for 15 samples"): the join kept only samples that have an MLST row: 30 rows - 2 rows of the 2 orphan ids = 28 rows; 17 ids - 2 = 15 samples. 28 - 15 = 13 extra rows = the 13 repeats.
- Now ("40 rows for 27 samples"): the left join from the metadata keeps the 12 samples without MLST: 28 + 12 = 40 rows; 15 + 12 = 27 samples. 40 - 27 = 13 = the same 13 repeats.
- With one MLST row per (sample, scheme) (option b): 17 rows, 15 in the metadata, 15 + 12 = 27 rows for 27 samples.

So the number of rows exceeds the number of samples only because of these 13 rows; the join and the recipe do what they are told.

## 4. The fix for the data: a PROPOSAL, nothing changed

Which rows: the 13 extra rows (the 2nd to the last of each repeated id; the first row in file order stays). Which of the rows is "the original" is arbitrary: the data has no way to tell. Same as in (b).

| | (a1) new ids, no metadata line | (a2) new ids, and a metadata line for each | (b) keep one row per (sample, scheme), drop the rest | (c) regenerate the demo data |
|---|---|---|---|---|
| What | 13 rows get 13 new `SYN_` ids | as a1, and 13 new lines in the metadata (source, year, country invented) | delete the 13 rows | write a new generator run with unique ids |
| Demo table (rows / samples) | 27 / 27 | 40 / 40 (28 MLST rows matched + 12 samples without MLST = 40 rows; the 2 orphans stay) | 27 / 27 | unknown until it is run |
| Orphan MLST rows (not in metadata) | 15 rows of 15 ids (2 now) | 2 | 2 | unknown |
| Samples without MLST | 12 | 12 | 12 | unknown |
| Year missing in the table | 2 (was 7: the 5 extra rows of repeated no-year samples go) | depends on the invented lines | 2 | unknown |
| Plot `demo_st_by_source` | 27 rows (bars count samples) | 40 rows | 27 rows | changes |
| Cost / risk | small; data invented only in ids | invents 13 samples of metadata: more made-up science | small; loses 13 rows of (made-up) results | largest: all values and ids change; the old script cannot run (`synthesize` is gone); needs a seed to be reproducible |

(REASONED from the counts of `demo.py`; a1/b year-missing count RAN: 7 now, 2 after b.)

Effect on what holds the demo numbers (READ the tests; none run):
- `app/tests/test_demo_join_keeps_every_sample.py`: `test_the_expected_numbers_are_the_ones_of_the_decision` asserts `(27, 12, 40)` hard-coded; `test_a_sample_with_several_mlst_results_keeps_all_its_rows` asserts a sample with 6 rows (it locks the defect in: it must be replaced by "no (sample, scheme) repeats" for a, b and c); `test_the_two_mlst_only_samples..` asserts 2 orphan rows of 2 samples (breaks for a1); the two description tests assert "40 rows for 27 samples" and the orphan counts and ids in the text.
- `app/tests/test_shiny_na_tick.py` (browser): 40 rows, 33 after `= 2024`, "7 rows have no value in year": all change (27, 25, 2 for a1 and b).
- `app/tests/golden/baseline.json`: `demo_abromics` plots, t1 and t2 hold `rows: 40` and a sha256: re-baseline needed for every option.
- `app/tests/golden/categorical_counts_before.json` and `categorical_content_before.json`: hold the demo table of before the categorical migration (`test_categorical_migration.py` compares to them). Any data change breaks that test; re-recording them would change what they document (the state before commit `806dc852`). This needs a decision of how to keep that proof.
- The demo ResFinder file is read by no recipe and no test (RAN: grep): a fix of the demo ResFinder file touches nothing but the file.
- No other test or recipe names the demo ids (grep `SYN_74255382`: only the data files).

What the MLST description should say afterwards (my wording, for her to change):
- Schema `MLST`: "One row per sample and MLST scheme: a sample has one sequence type per scheme. In this demo file every id appears once (the repeated ids of an earlier version were synthetic-data errors and were corrected)." The old text "in this demo file a sample can appear on more than one row" is removed.
- Join `demo_join` and `info.description`: the sentence "a sample with several MLST results has several rows (40 rows for 27 samples)" goes; the numbers become the new ones; for a1 the sentence "the 2 MLST rows of 2 samples that are not in the metadata" becomes the new orphan count. The plot description "(a sample repeated in the MLST data counts more than once)" goes.
- If the file stays as it is (no fix), the recipe text should say it plainly: "this file holds 13 repeated rows that are known errors of the synthetic data".

## 5. Does the app let such a defect pass silently? Yes (RAN + READ)

What I ran on `demo_abromics.yaml` (`check.py`, output `check_out.txt`):
```
STRUCTURE CHECK: []
DATA CHECK: []
BUILD stdout: '[Orchestrator] ▶ materialize_tier1 START ...  ✅ materialize_tier1 DONE — assembly 'demo_join' in 0.03s'
BUILD stderr: ''     warnings: only an unclosed-file note
rows 40 samples 27      (SYN_74255382 has 6 rows)
```
`check_recipe_file(...,'run')` also gives `[]`. Nothing says that a key repeats.

What exists:
- `is_entity_key` (READ `.claude/design/recipe_format_spec.md:374`): "true when the column identifies the entity (it repeats in long tables)". It does NOT declare "unique". The checker only asks that a table has one (E02, `libs/utils/src/utils/recipe_check.py:261`). No code in `libs/ingestion` or `app/modules` reads the flag to compare it with the data (RAN: grep; `app/modules/wrangle_studio.py:1327` only draws a key icon). So a repeat of the entity key is by definition not a violation: long tables (ResFinder, PlasmidFinder) must repeat it.
- The data check `validate_data_analysis_recipe_data` (`app/modules/data_analysis_recipe_validator.py:352`) only tests that datasets load and steps run.
- Join: `polars_join` offers `validate` with `m:m, 1:m, m:1, 1:1` (`libs/transformer/src/transformer/actions/polars_calls.py:90`). No shipped recipe uses it (RAN: grep `validate:` in `config/data_analysis_recipes`: no hit). `1:m` or `m:1` would raise an ERROR in Polars; D-0183 says "no error in polars then no error for us. Warning/caution is good", and here Polars raises only if the recipe asks. A recipe that declares nothing gets nothing.
- A precedent for a caution with counts exists: `_self_join_caution` (`libs/transformer/src/transformer/data_assembler.py:121`) computes row counts before and after a join and keeps a `PipelineError` of severity warning in `self.cautions`; it prints it; the checker says the same without numbers (J12, `recipe_check.py:702`). The code says that no carrier takes it to the screen yet (report SELF-JOIN-WARN-1). There is no such caution for a repeated key.

What is missing, where it could show a count as information or warning, never an error (not built):
1. A repeat count at reading: in `libs/ingestion/src/ingestion/declared.py` (the reader of the declared fields), per table with an `is_entity_key`: "8 ids repeat on 21 rows". Information only, because long tables repeat on purpose.
2. A caution at the join (like `_self_join_caution`): rows before and after the join step, and how many rows come from a repeated key on the right side ("the right table repeats the key: the table grows from 27 samples to 40 rows"). That is the number she asked for, and it is true for every join.
3. A declared intention: a table field the recipe maker can write ("one row per sample", or "one row per sample and scheme", as `unique_by: [sample_id, scheme]`) so that a repeat against the declaration is a warning with the count, and a long table says nothing. This needs a decision (it adds a recipe key; D-0165). Without it, 1 and 2 are information only.
4. The recipe text: the description is the only place that says "a sample can appear on more than one row". It hides the defect and nothing compares it with the data.

## 6. ONE question for her

Evidence: the MLST demo file has 13 rows whose sample id repeats under the same scheme (8 ids; the worst is `SYN_74255382` with 6 sequence types under one scheme). It is a defect of the synthetic data generator (draw with replacement), not of the recipe, the join or the app. Your own words (M196): "change the id of one of the duplicates".

Question: shall we change the ids of the 13 extra rows to 13 new synthetic ids (option a), and should these 13 new samples also get a line in the metadata?
- Yes, change the ids: the records support this default (your words above; no decision says otherwise).
- On the metadata: no record decides it. a1 (no line): the demo table is 27 rows for 27 samples and 15 MLST rows have no metadata. a2 (a line each, with invented source, year, country): 40 rows for 40 samples, more made-up data. Alternative (b): drop the 13 rows. I give no default for this part.

D-0165 note: no decision exists for a "one row per sample" declaration (section 5, point 3); if you want the app to warn on a repeated key, that decision is needed.

## What I did not check
- I did not run any test, the app or a browser (the machine is busy); effects on tests are read from the test files, not measured.
- I did not trace how `-` and `""` become missing (the result is checked, the code is not).
- I did not judge the 583 exact duplicate rows of the ST22 VirulenceFinder file (real pipeline output or not; whether the recipe's counts double them).
- I did not read every shipped recipe's join steps for other repeats of the right-hand key; only the demo, ST22 and the table counts.
- The old generator's behaviour is read from git, not run (the script cannot run now). The pool of 30 ids is not stored, so "the 2 MLST ids not in the metadata come from blanked metadata ids" is an inference.
- The templates `simple_template`, `e_coli`, `audit` point to missing files: noted, not investigated.
- The a2 table cell "40 / 40" I computed by hand (28 matched MLST rows + 12 without), not by a script.
