# Categorical migration list (data scientist viewpoint, 2026-11-15)

Nothing was migrated and no repository file was edited. Marks: RUN = I ran it; READ = I read a file; INFERRED = reasoned, not run.
Scratch work is in `tmpAI/panel/round7/`: `compare.py` and `cmp_base.json` (old against new, every plot), `make_tree.py` (builds the recipe tree as it would be after the change, in `w/x/tree_new`), `table_b.py`, `enum_cases.py`, `joinkeys.py`.

## Summary first

- Recount today (RUN, `find_cat.py`): 120 declarations of Categorical in any letter case. Round 5 found 92. The difference is +28: four copies of the 2_test recipe under `app/tests/equality/recipes/` (7 fields each), added after round 5. The other 92 are unchanged: 82 `Categorical` in `config/data_analysis_recipes/`, 3 in `assets/ref_data/`, 7 lower-case `categorical` in two files that no recipe includes. The gallery (`assets/gallery_data/`, 34 recipes) declares none (RUN).
- Classes for the 85 live fields (82 + 3): nominal to `String` 68; text that is a list or free text, also `String`, 8; ordinal to `Enum` 1 (figshare `predicted_phenotype`); date to `Date` 3; number to `Float64` 1 (`value`); unsure 4 (I default them to `String`; they go to Eve as questions). Total `String` 80. The 7 lower-case legacy fields are not touched.
- Plots I could run: 32. The picture changes in 21 (20 shipped, 1 template). 11 are identical (RUN, PNG bytes at 60 dpi). The same code run twice on the old tree gives identical pictures for all 32, so the changes are real.
- Counts per category: equal in every plot, for every field (RUN, 32 plots). No value is lost and none becomes null.
- What changes in the 21 pictures: the order of the levels, so also the colour a level gets, the order of axis ticks and the order of panels. The set of labels is the same (RUN).
- Tables: the Tier 1, Tier 2 and plotted tables have the same content (same hash) in all 7 golden recipes, and in the retest and template recipes that can run. Only the column types change. One exception: the plotted table of the stress plot (flag 2).
- Join keys at risk: none (section C).

## Flags first (anything that changes a result or hides a step)

1. The colour of a level and the order change in 21 pictures. Expected from Eve's decision; the counts are the same. RUN.
2. Dates in the plotted table. With `collection_date` as `Date`, the plotted table (`plot.data`, a pandas table) writes `2023-04-11 00:00:00`. The Tier 1 and Tier 2 tables keep `2023-04-11`. The golden hash of the plot `stress_species_amr` moves for this reason only. RUN (`stressplot.py`). I did not check whether a bundle or export writes the plotted table.
3. `Enum` is strict. A value that is not in the list refuses the whole dataset, with a message that names the column and the value (RUN: `column 'predicted_phenotype' (Enum): 'NI'`). It never becomes null silently. A lower-case `r`, an empty cell or the text `NA` is also refused (unless `NA` is listed in `null_values`). Spaces around a value are removed first when `strip: true`. So a new level in a future data file stops the run until the recipe list is updated: loud, but it is work for the user.
4. The hand-written equality reference (`app/tests/equality/reference_2_test_data_ST22_dummy.py`, READ) declares `pl.Categorical` for 7 fields and compares with `assert_frame_equal`, which checks the type (RUN on a toy table: "dtypes do not match"). If the shipped recipe `2_test_data_ST22_dummy` becomes `String` and the reference does not, the equality test fails on type. The shipped recipe, the four equality copies and the reference must change together.
5. The golden baseline `app/tests/golden/baseline.json` records the type of every column. After the change `golden_baseline.py --check` reports "columns or types differ" for 71 table records (Tier 1, Tier 2 and plotted tables), all because of the type text. Only one of them, the plotted table of the stress plot, also differs in content hash (flag 2). It must be regenerated and the commit must say why.
6. "Alphabetical" means byte order. Upper case comes before lower case: `resistance_class` is drawn `DISINFECTANT, LEAF RUST, MULTI-DRUG, aminoglycoside ...` (RUN). Numbers written as text sort as text: ST is drawn `10, 101, 117, 131 ... 93, 95`. A reviewer may notice. Eve accepted alphabetical order for nominal fields.
7. Gain: today the order depends on the order of rows in the file. 30 shuffles of the same 42-row metadata file gave 5 different `Categorical` level orders (RUN). With `String` the order is always France, Germany, Norway.
8. Not runnable: the templates `e_coli`, `audit` and `simple_template` (5 plots) read data files that are not in the repository (RUN: file missing). Their order would change the same way (INFERRED). `retest_bad_select_column` and `retest_broken_header` fail on purpose, with the same error before and after (RUN).
9. A comment in `Summary_input_fields.yaml` line 20 says "if omitted its default to categorical". The format requires `type`; the comment is stale (READ). The spec note at `.claude/design/recipe_format_spec.md` line 129 says the recipes "stay Categorical where the order of the categories or memory matters"; it disagrees with Eve's decision of 2026-11-15 (READ).

## A. Every field, grouped by recipe file

How to read a line: the field; its values (read from the real data file after `strip` and the declared missing words); my class; the new type; the reason. "Q" points to section G. Shared files are listed once (the Summary file feeds `Summary` and `Summary_quality`; the MLST file feeds four recipes).

### `pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml`
Same three fields as the file in `assets/ref_data/` (a copy).

- `Location`: 1 value: 'plasmid' (5 of 11 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. reference text, half blank; no plot.
- `Name_plasmid`: 1 value: 'ColV' (6 of 11 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. reference text, half blank; no plot.
- `VirulenceFinder`: 1 value: 'several variants' (6 of 11 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. reference text, half blank; no plot.

### `pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml`

- `taxon_1`: 1 value: 'Escherichia_coli'. Class NOMINAL, new type `String`. a species name; one value; no meaningful order.

### `pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml`

- `data`: 56 values, for example 'Col(MG828)', 'Col156', 'Col440I', 'ColRNAI', 'ColpVC' (3 of 280 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. name of a detected item (gene, plasmid, allele); labels.
- `data_type`: 3 values: 'MLST', 'Plasmid', 'Resistance'. Class NOMINAL, new type `String`. kind of record (MLST, Plasmid, Resistance); labels.
- `predicted_phenotype`: 11 values: 'Susceptible', 'ampicillin', 'gentamicin', 'kanamycin', 'spectinomycin', 'streptomycin', 'sulfisoxazole', 'tetracycline', 'trimethoprim', 'unknown[qacE_1_X68232]', 'unknown[sitABCD_1_AY598030]'. Class NOMINAL, new type `String`. antibiotic names (not the S/I/R scale here); labels.
- `cge_predicted_phenotype`: 9 values: 'Amoxicillin, Ampicillin, Cephalothin,...', 'Benzylkonium Chloride, Ethidium Bromi...', 'Doxycycline, Tetracycline', 'Gentamicin', 'Hydrogen peroxide', 'Spectinomycin, Streptomycin', 'Streptomycin', 'Sulfamethoxazole', 'Trimethoprim'. Class OTHER (list as text), new type `String`. a comma list of antibiotic names in one cell; text, no order.
- `contig`: 63 values, for example 'contig00002', 'contig00005', 'contig00006', 'contig00007', 'contig00009'. Class NOMINAL, new type `String`. contig identifier; label.
- `accession`: 29 values, for example '008486', '009781', 'AF024602', 'AF137361', 'AF534183'. Class NOMINAL, new type `String`. database accession; identifier.

### `pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml`
Used by 1_test_data_ST22_dummy, 1_Abromics_general_pipeline, 3_test_no_joins and demo_abromics. The values below are from the ST22 file (42 rows); demo_abromics has its own 30-row file with `-`, `N/A` and a blank, declared missing.

- `scheme`: 1 value: 'ecoli_achtman_4'. Class NOMINAL, new type `String`. typing scheme name; one value.
- `sequence_type`: 18 values, for example '10', '101', '131', '135', '1485' (2 of 42 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. sequence type (ST) number: a label, not a quantity; '-' is declared missing.
- `locus_1`: 11 values: 'adk(10)', 'adk(101)', 'adk(13)', 'adk(20)', 'adk(21)', 'adk(36)', 'adk(37)', 'adk(43)', 'adk(6)', 'adk(96)', 'adk(97)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.
- `locus_2`: 16 values, for example 'fumC(11)', 'fumC(231)', 'fumC(24)', 'fumC(29)', 'fumC(30)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.
- `locus_3`: 16 values, for example 'gyrB(10)', 'gyrB(12)', 'gyrB(13)', 'gyrB(15)', 'gyrB(19)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.
- `locus_4`: 13 values, for example 'icd(1)', 'icd(10)', 'icd(100)', 'icd(108)', 'icd(13)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.
- `locus_5`: 13 values, for example 'mdh(1)', 'mdh(16)', 'mdh(17)', 'mdh(20)', 'mdh(23)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.
- `locus_6`: 15 values, for example 'purA(1)', 'purA(10)', 'purA(11)', 'purA(12)', 'purA(13)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.
- `locus_7`: 12 values: 'recA(17)', 'recA(2)', 'recA(21)', 'recA(25)', 'recA(26)', 'recA(29)', 'recA(30)', 'recA(41)', 'recA(6)', 'recA(66)', 'recA(67)', 'recA(7)'. Class NOMINAL, new type `String`. allele call such as adk(10): a label.

### `pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml`

- `quality_module`: 2 values: 'Passed', 'Warning'. Class UNSURE (ordinal?), new type `String (default) or Enum [Passed, Warning]`. a quality verdict: Passed/Warning has a severity order, but the full list of verdicts is not in the data and no plot or step uses it: QUESTION Q2.
- `quality_feedback`: 2 values: 'All tests passed', 'Low Bracken main taxon proportion (<90)'. Class NOMINAL, new type `String`. message text, 2 values.
- `bracken_main_taxon`: 1 value: 'Escherichia_coli'. Class NOMINAL, new type `String`. a species name; one value.

### `pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml`

- `gene`: 13 values, for example 'aac(3)-VIa', 'aadA5', "ant(3'')-Ia", "aph(3'')-Ib", 'aph(6)-Id'. Class NOMINAL, new type `String`. resistance gene name; label.
- `predicted_phenotype`: 11 values: 'Susceptible', 'ampicillin', 'gentamicin', 'kanamycin', 'spectinomycin', 'streptomycin', 'sulfisoxazole', 'tetracycline', 'trimethoprim', 'unknown[qacE_1_X68232]', 'unknown[sitABCD_1_AY598030]'. Class NOMINAL, new type `String`. antibiotic names (not S/I/R in this table); label.

### `pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml`

- `quality_module`: 1 value: 'Passed'. Class UNSURE (ordinal?), new type `String (default) or Enum [Passed, Warning]`. a quality verdict: Passed/Warning has a severity order, but the full list of verdicts is not in the data and no plot or step uses it: QUESTION Q2.
- `taxon`: 1 value: 'unknown'. Class NOMINAL, new type `String`. a species label; one value.
- `genotype`: 12 values: "aac(3)-VIa, ant(3'')-Ia, blaTEM-1B, q...", "aadA5, ant(3'')-Ia, dfrA17, sitABCD, ...", "ant(3'')-Ia, sitABCD", "aph(3'')-Ib, aph(6)-Id, sitABCD, tet(A)", 'blaTEM-1B, sitABCD', 'blaTEM-1B, sitABCD, sitABCD', 'blaTEM-1C, sitABCD', 'blaTEM-1C, sitABCD, sitABCD', 'sitABCD', 'sitABCD, sitABCD', 'sitABCD, sitABCD, sitABCD', 'sitABCD, sul2' (4 of 42 cells missing after strip and the declared missing words). Class OTHER (list as text), new type `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `phenotype`: 8 values: 'Susceptible', 'ampicillin, unknown[sitABCD_1_AY598030]', 'gentamicin, spectinomycin, ampicillin...', 'spectinomycin, unknown[sitABCD_1_AY59...', 'streptomycin, kanamycin, unknown[sitA...', 'streptomycin, spectinomycin, trimetho...', 'unknown[sitABCD_1_AY598030]', 'unknown[sitABCD_1_AY598030], sulfisox...'. Class OTHER (list as text), new type `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `cge_phenotype`: 7 values: 'Amoxicillin, Ampicillin, Cephalothin,...', 'Gentamicin, Streptomycin, Amoxicillin...', 'Hydrogen peroxide', 'Hydrogen peroxide, Sulfamethoxazole', 'Spectinomycin, Streptomycin, Trimetho...', 'Streptomycin, Hydrogen peroxide', 'Streptomycin, Hydrogen peroxide, Doxy...' (4 of 42 cells missing after strip and the declared missing words). Class OTHER (list as text), new type `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `plasmid`: 23 values, for example 'Col(MG828), Col(MG828), Col(MG828), C...', 'Col(MG828), Col(MG828), ColRNAI, IncF...', 'Col(MG828), Col(MG828), IncFIA, IncFI...', 'Col(MG828), Col(MG828), IncFIB(AP0019...', 'Col(MG828), Col(MG828), IncFIB(AP0019...' (1 of 42 cells missing after strip and the declared missing words). Class OTHER (list as text), new type `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `ST`: 19 values, for example '10', '101', '117', '131', '135' (2 of 42 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. sequence type number: a label; '-' declared missing; text order 10,101,117 (not numeric) is acceptable for labels.

### `pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml`

- `serotype`: 13 values, for example 'O11:H25', 'O120:H4', 'O13/O129/O13/O135:H4', 'O161:H4', 'O2/O50:H1'. Class NOMINAL, new type `String`. O:H serotype label.
- `virulence_raw`: 48 values, for example 'air: Enteroaggregative immunoglobulin...', 'astA: EAST-1 heat-stable toxin', 'capU: Hexosyltransferase homolog', 'cba:  Colicin B', 'cea:  Colicin E1'. Class OTHER (compound text), new type `String`. 'gene: description' text that a wrangling step splits: a text step needs String.

### `pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml`

- `source`: 3 values: 'Broiler', 'Layer', 'Parent'. Class NOMINAL, new type `String`. production type; Broiler, Layer, Parent are groups, not a scale.
- `country`: 3 values: 'France', 'Germany', 'Norway'. Class NOMINAL, new type `String`. country; label.

### `pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml`

- `gene`: 13 values, for example 'aac(3)-VIa', 'aadA5', "ant(3'')-Ia", "aph(3'')-Ib", 'aph(6)-Id'. Class NOMINAL, new type `String`. resistance gene name.
- `predicted_phenotype`: 10 values: 'ampicillin', 'gentamicin', 'kanamycin', 'spectinomycin', 'streptomycin', 'sulfisoxazole', 'tetracycline', 'trimethoprim', 'unknown[qacE_1_X68232]', 'unknown[sitABCD_1_AY598030]'. Class NOMINAL, new type `String`. antibiotic names (not S/I/R here).
- `accession`: 13 values, for example 'AF024602', 'AF137361', 'AF534183', 'AY034138', 'AY458016'. Class NOMINAL, new type `String`. database accession; identifier.

### `pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml`

- `Source`: 3 values: 'Broiler', 'Layer', 'Parent'. Class NOMINAL, new type `String`. production type; groups, not a scale.
- `Country`: 3 values: 'France', 'Germany', 'Norway'. Class NOMINAL, new type `String`. country; label.

### `pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml`

- `plasmid_name`: 18 values, for example 'Col(MG828)', 'Col156', 'Col440I', 'ColRNAI', 'ColpVC'. Class NOMINAL, new type `String`. plasmid replicon name; label.
- `accession`: 13 values, for example 'AF024602', 'AF137361', 'AF534183', 'AY034138', 'AY458016'. Class NOMINAL, new type `String`. database accession; identifier.

### `pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml`

- `host_animal_common`: 7 values: 'cat', 'cattle', 'chicken', 'dog', 'horse', 'swine', 'turkey'. Class NOMINAL, new type `String`. animal group; label.
- `gene`: 288 values, for example 'A7J112581', 'ARR-3', 'Col(BS512)', 'Col(KPHS6)', 'Col(MG828)'. Class NOMINAL, new type `String`. gene or replicon name; label.
- `gene_type`: 2 values: 'chromosome', 'plasmid'. Class NOMINAL, new type `String`. chromosome or plasmid; label.
- `gene_identifier`: 265 values, for example 'AAC(3)-II', 'AAC(3)-IIb', 'AAC(3)-IId', 'AAC(3)-IIe', 'AAC(3)-IIg' (14 of 10839 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. gene variant name; label.
- `gene_name_family`: 52 values, for example 'AAC(3)', "AAC(6')", "AAC(6')-Ib-cr", "ANT(2'')", "ANT(3'')" (3385 of 10839 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. gene family; label ('NA' declared missing; one raw value carries a leading tab that strip removes; 55 raw texts become 53).
- `resistance_class`: 19 values, for example 'DISINFECTANT', 'LEAF RUST', 'MULTI-DRUG', 'aminoglycoside', 'arsenic' (14 of 10839 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. drug class; label (mixed upper and lower case: String order puts upper case first).

### `pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml`

- `host_animal_species`: 7 values: 'Bos taurus', 'Canis familiaris', 'Equus caballus', 'Felis catus', 'Gallus gallus', 'Meleagris gallopavo', 'Sus domesticus'. Class NOMINAL, new type `String`. species name; label.
- `host_animal_common`: 7 values: 'cat', 'cattle', 'chicken', 'dog', 'horse', 'swine', 'turkey'. Class NOMINAL, new type `String`. animal group; label.
- `specimen_source_tissue`: 196 values, for example 'abdomen', 'abdominal abscess', 'abdominal exudate', 'abdominal fluid', 'abdominal fluid swab'. Class NOMINAL, new type `String`. tissue or source label, many values.
- `final_diagnosis`: 375 values, for example '1 week old cross bred calf died of sc...', '19 day old foal w/ acute diarrhea', '3 month old foal with persistant diar...', '80% of herd had fever of 104, ruminat...', 'aborted fetus' (6 of 980 cells missing after strip and the declared missing words). Class OTHER (free text), new type `String`. a free-text diagnosis written by a person; 379 values; text.
- `animal_infection_site_uti`: 2 values: 'Not UTI/urine/urinary tract', 'UTI/urine/urinary tract'. Class NOMINAL, new type `String`. two labels (UTI or not).

### `pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml`
18437 rows. Raw counts (RUN): S 11204, R 6726, NI 405, I 102. `I` and `NI` occur only with breakpoint `clsi`.

- `mic_id`: 50 values, for example 'amikacin', 'amoxicillin', 'amoxicillin_clavulanic_acid', 'ampicillin', 'azithromycin'. Class NOMINAL, new type `String`. antibiotic name (50); no scale.
- `breakpoint`: 2 values: 'clsi', 'iq'. Class NOMINAL, new type `String (or keep Categorical as the documented example, see Q8)`. standard used (clsi, iq); label; not plotted, not used by any step.
- `predicted_phenotype`: 4 values: 'I', 'NI', 'R', 'S'. Class ORDINAL, new type `Enum [S, I, R, NI]`. susceptible, intermediate, resistant (clinical scale); NI placement is question Q1.

### `pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml`
The data file is CRLF text with 10000 rows (RUN).

- `id`: 10000 values, for example 'REC_0', 'REC_1', 'REC_10', 'REC_100', 'REC_1000'. Class NOMINAL (identifier), new type `String`. one distinct value per row (10000 of 10000); an identifier.
- `species`: 4 values: 'E. coli', 'K. pneumoniae', 'P. aeruginosa', 'S. enterica'. Class NOMINAL, new type `String`. species name; label.
- `amr_class`: 5 values: 'Aminoglycosides', 'Beta-lactams', 'Carbapenems', 'Fluoroquinolones', 'Tetracyclines'. Class NOMINAL, new type `String`. drug class; label.
- `collection_date`: 1197 values, for example '2020-01-10', '2020-01-11', '2020-01-12', '2020-01-13', '2020-01-14'. Class DATE, new type `Date (format %Y-%m-%d)`. ISO date text; all 10000 parse (RUN).
- `value`: 6315 values, for example '0.01', '0.02', '0.03', '0.05', '0.06'. Class OTHER (number), new type `Float64`. decimal numbers 0.01 to 99.98 (1 or 2 decimals); all 10000 parse; text round trip identical (RUN).

### `retest/retest_bad_select_column.yaml`

- `gene`: 3 values: 'blaTEM-1B', 'sul1', 'tet(A)'. Class NOMINAL, new type `String`. gene name.
- `predicted_phenotype`: 3 values: 'Ampicillin', 'Sulfonamide', 'Tetracycline'. Class NOMINAL, new type `String`. antibiotic name.

### `retest/retest_broken_header.yaml`

- `gene`: 3 values: 'blaTEM-1B', 'sul1', 'tet(A)'. Class NOMINAL, new type `String`. gene name.
- `predicted_phenotype`: column absent in the data file (deliberate: broken header test). Class NOMINAL, new type `String`. antibiotic name.

### `retest/retest_tier2.yaml`

- `group`: 3 values: 'A', 'B', 'C'. Class NOMINAL, new type `String`. group label A, B, C.
- `year`: 3 values: '2022', '2023', '2024'. Class UNSURE (ordinal by time), new type `String (default) or Enum ['2022','2023','2024']`. a year used as a label; 4-digit text sorts in time order; QUESTION Q3.

### `retest/retest_top_n_other.yaml`

- `variant`: 8 values: 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8' (1 of 21 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. variant label.

### `templates/audit.yaml`

- `lab_id`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL (identifier), new type `String`. laboratory identifier; is_entity_key.
- `submission_date`: no data file in the repository (the template reads a file that is not shipped). Class DATE, new type `Date (format not verifiable: no data)`. a date; no data file, format assumed ISO.
- `status`: no data file in the repository (the template reads a file that is not shipped). Class UNSURE (ordinal?), new type `String (default)`. a workflow status (such as pending, done): order unknown, values not in the repo; QUESTION Q4.

### `templates/complex_template/genomics_input.yaml`
This template has data (30 rows).

- `gene_presence`: 26 values, for example "aph(3')-Ia;dfrA17;strB;strA", "aph(3')-Ia;sul2", 'blaTEM-1', "blaTEM-1; aph(3')-Ia; dfrA17; sul2", 'blaTEM-1;strA;catA1;sul2' (1 of 30 cells missing after strip and the declared missing words). Class OTHER (list as text), new type `String`. semicolon list of genes in one cell.

### `templates/complex_template/metadata_input.yaml`

- `country`: 4 values: 'Denmark', 'Finland', 'Norway', 'Sweden' (1 of 29 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. country; label.

### `templates/e_coli.yaml`

- `serotype`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. serotype label.
- `sequence_type`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. ST number: a label.
- `ctx_m_gene`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. CTX-M gene name; label (no data: meaning not verifiable).
- `collection_date`: no data file in the repository (the template reads a file that is not shipped). Class DATE, new type `Date (format not verifiable: no data)`. a date; no data file, format assumed ISO.
- `country_of_origin`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. country.
- `hospital_site`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. site label.
- `patient_outcome`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. outcome label (values unknown; if it is a scale such as recovered/died it would be a question).

### `templates/simple_template.yaml`

- `group`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. group label.
- `category`: no data file in the repository (the template reads a file that is not shipped). Class NOMINAL, new type `String`. category label.

### `assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml`
Outside `config/`: included by 1_Abromics_general_pipeline. A builder must not forget this file.

- `Location`: 1 value: 'plasmid' (5 of 11 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. reference text, half blank; no plot.
- `Name_plasmid`: 1 value: 'ColV' (6 of 11 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. reference text, half blank; no plot.
- `VirulenceFinder`: 1 value: 'several variants' (6 of 11 cells missing after strip and the declared missing words). Class NOMINAL, new type `String`. reference text, half blank; no plot.

### `pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly_output_fields.yaml`
Legacy: written `categorical` in lower case, which is not a type. No recipe includes it (READ); a test lists it as 'found 2026-11-15, not decided' (`app/tests/test_resfinder_abromics_fragment.py` lines 185 and 188).

- `sample_id`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `ST`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `quality_metric`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7

### `pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml`
Legacy: same case as above.

- `plasmid`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `hsp_lengthtotal_length`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `contig`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `accession`: class OTHER (legacy), not changed. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7

### `app/tests/equality/recipes/2_test_data_ST22_dummy_{dirty, dirty_no_null_text, emptied, fractional_year}/input_fields/{amr_data, metadata_schema, plasmid_data}.yaml`

Four test copies of the 2_test recipe, 7 fields each, 28 declarations (new since round 5). They are copies of `2_test_data_ST22_dummy/input_fields/`: `gene`, `predicted_phenotype`, `accession`, `Source`, `Country`, `plasmid_name`, `accession`. Class and new type: the same as the shipped 2_test fields (NOMINAL, `String`). The data are deliberately dirty (RUN: `Country` holds `Norway`, `norway`, `  Norway `, `NA`; `predicted_phenotype` holds ` kanamycin `, `Kanamycin`, `SULFISOXAZOLE`). `String` keeps these values as distinct texts, as `Categorical` did. They must change together with the hand-written reference (flag 4). Question Q7.

## B. Plots: the count per category before and after (RUN)

Method (`compare.py`): the same recipe and data, once as shipped (before) and once with my types (after, tree `w/x/tree_new`). For every plot I took the plotted table and counted the rows of every text, category, enum and date column, compared as text. I also saved each picture as PNG and compared the bytes, and read the order of all texts drawn (axis, legend, panel titles).

Result: 32 plots ran. In all of them every count per category is equal before and after, and no value is lost or null (RUN). The list below is every plot where a retyped field is drawn on an axis, as fill, colour or panel. "Order" is the order in which the levels are drawn, first four.

| recipe | plot | field (role) | levels | rows | counts equal | picture | order before | order after |
|---|---|---|---|---|---|---|---|---|
| 1_Abromics_general_pipeline | abromics_st_by_country | country (fill) | 3 | 342 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_Abromics_general_pipeline | abromics_st_by_source | source (fill) | 3 | 342 | yes | changed | Broiler, Parent, Layer | Broiler, Layer, Parent |
| 1_test_data_ST22_dummy | phenotype_genome_length_fragmentation | ST (color) | 20 | 126 | yes | changed | 227, 93, 95, 10 | 10, 101, 117, 131 |
| 1_test_data_ST22_dummy | amr_heatmap | gene (x) | 13 | 70 | yes | changed | tet(A), dfrA17, blaTEM-1B, aac(3)-VIa | aac(3)-VIa, aadA5, ant(3'')-Ia, aph(3'')-Ib |
| 1_test_data_ST22_dummy | amr_heatmap | predicted_phenotype (fill) | 10 | 70 | yes | changed | kanamycin, unknown[qacE_1_X68232], streptomycin, tetracycline | ampicillin, gentamicin, kanamycin, spectinomycin |
| 1_test_data_ST22_dummy | mlst_bar | country (fill) | 3 | 33 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_test_data_ST22_dummy | year_distribution | country (fill) | 3 | 33 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_test_data_ST22_dummy | miaou | source (fill/x) | 3 | 126 | yes | changed | Broiler, Parent, Layer | Broiler, Layer, Parent |
| 1_test_data_ST22_dummy | qa_amr_genes_per_sample | country (fill) | 3 | 42 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_test_data_ST22_dummy | qa_sequence_type_missing | ST (x) | 20 | 42 | yes | changed | 227, 93, 95, 10 | 10, 101, 117, 131 |
| 1_test_data_ST22_dummy | qa_year_label | country (fill) | 3 | 42 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_test_data_ST22_dummy | qa_facet_by_mapping | country (facet) | 3 | 42 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_test_data_ST22_dummy | qa_aggregated_no_key | country (x) | 3 | 9 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 1_test_data_ST22_dummy | qa_population_zscore | country (x) | 3 | 42 | yes | changed | Norway, France, Germany | France, Germany, Norway |
| 2_test_data_ST22_dummy | multi_resistance_by_country | Country (facet) | 3 | 70 | yes | changed | France, Norway, Germany | France, Germany, Norway |
| 2_test_data_ST22_dummy | multi_resistance_by_source | Source (facet) | 3 | 70 | yes | same | Broiler, Layer, Parent | Broiler, Layer, Parent |
| 2_test_data_ST22_dummy | plasmid_prevalence_by_country | plasmid_name (fill) | 18 | 163 | yes | changed | IncI1-I(Alpha), Col156, IncFII(pHN7A8), IncFII(29) | Col(MG828), Col156, Col440I, ColRNAI |
| 2_test_data_ST22_dummy | plasmid_prevalence_by_country | Country (facet) | 3 | 163 | yes | changed | France, Norway, Germany | France, Germany, Norway |
| demo_abromics | demo_st_by_source | source (fill) | 3 | 28 | yes | changed | Layer, Parent, Broiler | Broiler, Layer, Parent |
| figshare_integration | plot_a_phenotype_bar | mic_id (x) | 50 | 203146 | yes | changed | amikacin, amoxicillin_clavulanic_acid, ampicillin, cefazolin | amikacin, amoxicillin, amoxicillin_clavulanic_acid, ampicillin |
| figshare_integration | plot_a_phenotype_bar | predicted_phenotype (fill) | 4 | 203146 | yes | changed | S, R, NI, I | S, I, R, NI |
| figshare_integration | plot_b_genotype_bar | host_animal_common (x) | 7 | 203146 | yes | changed | cat, chicken, cattle, dog | cat, cattle, chicken, dog |
| figshare_integration | plot_b_genotype_bar | gene_name_family (fill) | 53 | 203146 | yes | changed | ampC, tet, TEM, MFS | AAC(3), AAC(6'), AAC(6')-Ib-cr, ANT(2'') |
| figshare_integration | plot_c_resistance_class | resistance_class (x) | 20 | 203146 | yes | changed | beta-lactam, tetracycline, MULTI-DRUG, sulfonamide | DISINFECTANT, LEAF RUST, MULTI-DRUG, aminoglycoside |
| figshare_integration | plot_c_resistance_class | host_animal_common (fill) | 7 | 203146 | yes | changed | cat, chicken, cattle, dog | cat, cattle, chicken, dog |
| stress_test_master | stress_species_amr | species (x) | 4 | 10000 | yes | changed | K. pneumoniae, E. coli, P. aeruginosa, S. enterica | E. coli, K. pneumoniae, P. aeruginosa, S. enterica |
| stress_test_master | stress_species_amr | amr_class (fill) | 5 | 10000 | yes | changed | Fluoroquinolones, Carbapenems, Beta-lactams, Aminoglycosides | Aminoglycosides, Beta-lactams, Carbapenems, Fluoroquinolones |
| retest_tier2 | value_by_group | group (x) | 3 | 8 | yes | same | A, B, C | A, B, C |
| retest_tier2 | samples_per_year | year (x) | 3 | 12 | yes | same | 2022, 2023, 2024 | 2022, 2023, 2024 |
| complex_template | gene_presence_by_country | country (x) | 5 | 74 | yes | changed | Denmark, Sweden, Norway, Finland | Denmark, Finland, Norway, Sweden |

Pictures that change (21): 1_Abromics_general_pipeline abromics_st_by_country, abromics_st_by_source; 1_test_data_ST22_dummy amr_heatmap, miaou, mlst_bar, phenotype_genome_length_fragmentation, qa_aggregated_no_key, qa_amr_genes_per_sample, qa_facet_by_mapping, qa_population_zscore, qa_sequence_type_missing, qa_year_label, year_distribution; 2_test_data_ST22_dummy multi_resistance_by_country, plasmid_prevalence_by_country; demo_abromics demo_st_by_source; figshare_integration plot_a, plot_b, plot_c; stress_test_master stress_species_amr; complex_template (template) gene_presence_by_country.

Pictures that stay identical (11): 1_test_data_ST22_dummy assembly_quality_dotplot, qa_fanout_rows_per_sample, qa_l50_integer, qc_reads_horizontal_barplot, virulence_bar, virulence_variants; 2_test_data_ST22_dummy multi_resistance_by_source (data already in alphabetical order); 3_test_no_joins sequence_type_counts; retest_tier2 samples_per_year and value_by_group (already ascending); retest_top_n_other variants_bar.

Notes:
- The facet panels of `qa_facet_by_mapping` change from Norway, France, Germany to France, Germany, Norway. The subtitle of that plot says "Expect 3 panels: France, Germany, Norway" (READ), so the new order matches the text.
- `figshare plot_a`: the legend of `predicted_phenotype` goes from S, R, NI, I to S, I, R, NI (the `Enum` order). Counts: I 1056, NI 3839, R 100434, S 97817 on the joined table (203146 rows), before and after.
- Value tests of the `Enum` (RUN, `enum_cases.py`, `noNI.py`): with the list [S, I, R] and the real figshare file the build stops with `values that do not fit the declared type: column 'predicted_phenotype' (Enum): 'NI'`. Not a null, not a silent drop. A lower-case value, an empty cell and `NA` are refused the same way. A duplicate level in the list fails at once (`Enum categories must be unique`). An empty list refuses every value.
- Sort and compare on an `Enum` follow the written order (RUN): `sort` gives S, I, R, NI; `p >= 'I'` keeps I, R, NI. A filter on a value that is not a level returns 0 rows for `==` and fails for `is_in`. A text step (`str.*`) on an `Enum` column fails (`expected String, got enum`): no shipped step does that on `predicted_phenotype` (the recipe built and the hashes are equal).
- Alternatives I also ran (`tree_enumq`): `quality_module` as `Enum [Passed, Warning]` and `year` as `Enum ['2022','2023','2024']`. Every picture and count is identical to the `String` version (these fields are not plotted, or are already in order).

The other retyped fields are carried in tables but never drawn; for them only the type of the table column changes and the content hash is equal (RUN, golden check). Not runnable: the 5 template plots (flag 8).

## C. Join keys

RUN (`joinkeys.py`, 32 join key pairs in 8 recipes, plus the whole set built after the change). Every join key is `sample_id`, declared `String` on both sides in the shipped recipes, before and after. The two other joins are `VF_gene` (built by a text split in the wrangling, `String`) with `Gene_name` (declared `String` in the APEC reference file); and `VirulenceFinder.sample_id` is `String` (READ). No join key is `Categorical`, so none changes type on one side only. All recipes built after the change with no join error (RUN, golden build of 7 recipes plus retest and template recipes).

Fields that are entity keys and are `Categorical` today: stress `id` and audit `lab_id`. Both become `String`; neither recipe has a join.

Risk for users, not for shipped recipes: a join of `Categorical` with `String`, of `Enum` with `String`, or of two `Enum` with different lists is refused by the engine (RUN: "datatypes of join keys don't match"). It stops loudly. If the figshare example keeps one `Categorical` field (Q8), it must not be a key. Also the checker advice J13 stays: a key written as a float type merges `001`, `1` and `1.0`; not relevant here.

## D. `collection_date` and `submission_date`

Where they are declared (RUN grep): `collection_date` in `stress_test_master` (`Stress_Source_input_fields.yaml`) and in the template `e_coli.yaml` (table `metadata_schema`); `submission_date` in the template `audit.yaml`. Nowhere else. (The word `submission_date` also appears in the `info` block of gallery recipes; that is recipe metadata, not a column.)

Used by a step, plot, filter or output? No. No wrangling step, plot mapping, filter or join mentions them (RUN grep over `config/` and the plot specs). They are only carried along as columns: in the stress recipe `collection_date` is a column of the Tier 1 and Tier 2 table `Master_Collection` and so of any export of that table.

Do the values parse as dates? Stress: all 10000 are `YYYY-MM-DD`, range 2020-01-10 to 2026-09-28, no missing, all parse, and the text written back equals the original (RUN). The two templates: no data file in the repository, so the format and the parse cannot be verified.

My recommendation (Eve decides, Q5):
- `stress_test_master`: `Date`, format `%Y-%m-%d`. The column is in the data file and in the tables; dropping it changes the tables (the golden hashes of Tier 1 and Tier 2 move; with `Date` they do not). Effect to know: flag 2.
- `e_coli` and `audit` templates: `Date` with `format: "%Y-%m-%d"` as the documented way to declare a date. If the real file uses another format the load stops and names the value (RUN: `11/04/2023`, `2023-02-30` and a date with a time are all refused). No recipe uses these columns, so dropping them is also correct; I would keep them as a visible example of a date.

## E. The stress recipe: `value`

File: `assets/test_data/STRESS/STRESS_data.tsv`, column `value` (declared `Categorical`, label "Value"). The data hold numbers (RUN): 10000 rows, 6315 distinct, from 0.01 to 99.98, written with one or two decimals, no blank, no NaN. Right type: `Float64`. All 10000 parse, and writing them back as text gives the original text for all 10000, so nothing is rounded or changed.

What changes downstream (RUN): the Tier 1 and Tier 2 tables have the same text (same hash). No plot or step uses `value` (it is carried only). What the user gains: with `Categorical` a mean fails (`mean operation not supported for dtype cat`) and `value > 50` fails (`cannot compare categorical with i32`); with `Float64` the mean is 50.366 and 5051 rows are above 50. The plotted table of `stress_species_amr` now holds `value` as numbers.

`Decimal` with scale 2 would keep two decimals exactly; `Float64` is the usual type for a measurement and round-trips these values. Default `Float64` (Q6).

## F. What a builder must do

Ordered changes (file, field, old type, new type):

1. `config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml`: `predicted_phenotype` `Categorical` to `Enum`, add `categories: [S, I, R, NI]` (order written in the recipe; the checker rule FD05 asks for it, RUN).
2. `.../pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml`: `collection_date` `Categorical` to `Date`, add `format: "%Y-%m-%d"`; `value` `Categorical` to `Float64`.
3. `.../templates/e_coli.yaml`: `collection_date` to `Date` (format as above). `.../templates/audit.yaml`: `submission_date` to `Date` (format as above).
4. Every other `Categorical` in `config/data_analysis_recipes/` to `String`: 77 fields in these files: 1_test_data_ST22_dummy input_fields (Bracken 1, Detailed_summary 6, MLST 9, Quality_metrics 3, ResFinder 2, Summary 7, VirulenceFinder 2, metadata_schema 2, APEC_STEC 3), 2_test_data_ST22_dummy input_fields (amr_data 3, metadata_schema 2, plasmid_data 2), figshare (fg_genotypes 6, fg_metadata 5, fg_phenotypes 2: `mic_id`, `breakpoint`), stress (3: `id`, `species`, `amr_class`), retest (retest_bad_select_column 2, retest_broken_header 2, retest_tier2 2, retest_top_n_other 1), templates (audit 2: `lab_id`, `status`; complex_template 2; e_coli 6; simple_template 2). The four fields of Q2, Q3, Q4 follow Eve's answer; the default is `String`. If Eve keeps one figshare field as the documented example (Q8), leave it `Categorical` and say so in a comment on the line.
5. `assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml`: 3 fields to `String` (outside `config/`; round 5 and the first count of "config only" would miss it).
6. In the same commit, the four equality recipe copies (28 fields to `String`) and the hand-written reference `app/tests/equality/reference_2_test_data_ST22_dummy.py` (7 `pl.Categorical` to `pl.String`). If Eve prefers to leave the copies, the reference must hold a type per scenario instead (Q7).
7. Do not touch the 7 lower-case legacy fields (Q7).
8. Regenerate `app/tests/golden/baseline.json` (`assets/scripts/golden_baseline.py --out ...`); in the commit message: only column types change, content hashes unchanged except the plotted table of `stress_species_amr` (the date text), and give the Polars version.
9. Fix the stale texts: the comment at `Summary_input_fields.yaml:20`, the spec note at `recipe_format_spec.md:129`, and any user doc that says the shipped recipes keep `Categorical` (READ: none found in `docs/`).

Tests that must exist:
- Enum order pinned: read the shipped `fg_phenotypes_input_fields.yaml` and assert `type == 'Enum'` and `categories == ['S','I','R','NI']` exactly. Mutation check: swap two levels, the test must fail. Add: the drawn legend order of `plot_a_phenotype_bar` equals the list.
- Enum complete: for every shipped `Enum` field, the set of values in the real data file (after strip and missing words) equals the set of the list (a missing level makes the build fail; an extra unused level is reported). Mutation: remove `NI`, the build must fail with the message above.
- Counts per category equal: store the before counts (`tmpAI/panel/round7/cmp_base.json`, key `counts`, old side) as a golden file and compare, per plot and per plotted field, with the counts after. Mutation: change a value in a copy of the data, the test must fail.
- Golden table check: after regeneration, a test that compares the content hashes of Tier 1, Tier 2 and plotted tables with the old hashes (kept) and allows only the type text to differ (and the one stress plot date exception, or fix it first).
- Dates: every shipped `Date` field parses all values of its data file; Tier 1 text equals the old text. Mutation: write one `11/04/2023` in a copy; the build must refuse it.
- No `Categorical` left except the allowed example: a test that lists every `Categorical` declaration under `config/` and `assets/` and allows only the names Eve confirmed; and none in lower case.
- Equality test: reference and recipes agree on the type (the existing `test_recipe_equals_hand_written.py` runs on all five scenarios).
- Level order not tied to row order: for a nominal field, shuffle the rows of the file; the drawn order and the counts stay the same (RUN by hand today: 5 orders before, 1 after).

Pictures that change: the 21 listed in B.

## G. Questions for Eve

1. Place of `NI` in the figshare scale. The data hold `NI` 405 times, only with breakpoint `clsi`; no file in the repository says what `NI` means (READ: the figshare README does not define it). I believe it is "no interpretation" (INFERRED), which is not a point on the S, I, R scale. Options: (a) `[S, I, R, NI]`, as you wrote it; (b) `[S, I, R]` and `NI` declared missing (it would then be hidden from counts: counts change, so I advise against); (c) keep `NI` last but name it as "not on the scale" in the label. Default: (a).
2. `quality_module` (`Passed`, `Warning`; in the Summary and the Quality_metrics tables; used by no plot or step). A verdict has a severity order, but the full list of verdicts the pipeline can write is not in the data (is there a `Failed`?). Options: `String` (default); `Enum [Passed, Warning]` (a `Failed` in a later file would stop the load); `Enum [Failed, Warning, Passed]` once you give me the full list. Default: `String`.
3. `year` in `retest_tier2` (2022, 2023, 2024; one retest table). Options: `String` (default: 4-digit text sorts in time order, RUN picture identical); `Enum ['2022','2023','2024']` (RUN picture identical, but a new year needs a recipe edit); `Int64` (numbers, but a bar chart then treats the year as a continuous axis). Default: `String`.
4. `status` in the `audit` template (no data in the repository). If it is a workflow (for example received, in progress, done) the order has meaning. I cannot list the values. Options: `String` (default); `Enum` with the list you give. Default: `String`.
5. Dates. (a) `stress_test_master`: `Date` (default) or drop the column (tables change). (b) `e_coli` and `audit` templates: `Date` with an assumed ISO format (default), or drop the column. (c) May the plotted table show `2023-04-11 00:00:00` (flag 2)? Default: yes, and note it in the commit.
6. Stress `value`: `Float64` (default) or `Decimal` with two decimals.
7. Test copies and legacy. (a) Migrate the four equality recipe copies and the reference with the shipped 2_test recipe (default), or leave the copies as `Categorical` and give the reference one type per scenario. (b) The 7 lower-case `categorical` fields in two orphan files: leave (default; a test lists them as "not decided") or delete the files.
8. The documented `Categorical` example in figshare. My proposal: `breakpoint` in `fg_phenotypes` (2 values over 18437 rows, the largest table; not plotted, not used by any step, not a key, not in another table; RUN: with it kept `Categorical` the content hashes are unchanged, only its type text differs). Options: `breakpoint` (default); another field; none. Round 5 (READ, Polars size estimate, not process memory): `fg_phenotypes`, 4 columns, 0.30 MB as String against 0.22 MB as Categorical; the gain for one 2-value column is smaller.
9. Alphabetical order is byte order (flag 6: upper case first, numbers as text). Accept (default), or ask for a case-insensitive order on a field (that needs an `Enum` or a sort key; not built today).
