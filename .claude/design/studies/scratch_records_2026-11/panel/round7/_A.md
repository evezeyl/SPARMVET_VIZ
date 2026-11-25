# Categorical migration list (data scientist, 2026-11-15)

Nothing was migrated. No repository file was edited. Marks: RUN = I ran it; READ = I read a file; INFERRED = reasoned, not run.
Scratch scripts and raw results are in `tmpAI/panel/round7/` (`compare.py`, `cmp_base.json`, `make_tree.py`, `w/x/tree_new` = the recipe tree as it would be after the change).

## Summary first

- Recount today (RUN, `find_cat.py`): 120 type declarations of Categorical in any letter case. Round 5 found 92. The difference is +28: four copies of the 2_test recipe under `app/tests/equality/recipes/` (7 fields each) added after round 5. The 92 are unchanged: 82 `Categorical` in `config/data_analysis_recipes/`, 3 in `assets/ref_data/`, 7 lower-case `categorical` in two orphan files. The gallery (`assets/gallery_data/`) declares none (RUN).
- Classes for the 85 live fields (82 + 3): NOMINAL to `String` 68; text that is a list or free text, also `String`, 8; ORDINAL to `Enum` 1 (figshare `predicted_phenotype`); DATE 3; number 1 (`value`, `Float64`); UNSURE 4 (I default them to `String`, they go to Eve). Total `String`: 80. 7 lower-case legacy fields are not touched.
- Plots I could run: 32. Picture changes in 21 (20 in shipped recipes, 1 in a template). 11 are identical to the byte (RUN, PNG hash; the same code run twice gives identical pictures for all 32, so the changes are real).
- Counts per category: equal in every plot and every field (RUN, 32 plots). No value is lost, none becomes null.
- What changes in the 21 pictures: the order of the levels and therefore which colour a level gets and the order of axis ticks and panels. The set of labels is the same (RUN).
- Tables: the Tier 1 and Tier 2 tables and the plotted tables have the same content (same hash) in all 7 golden recipes and in the retest and template recipes I could run. Only the column types change. One exception: the plotted table of the stress plot shows the date as `2023-04-11 00:00:00` (see E and the flag below).
- Join keys at risk: none (C).

## Flags first (things that change a result or hide a step)

1. The colour of a level and the order on 21 pictures change (expected from Eve's decision). Counts are the same. RUN.
2. Dates in the plotted table: with `collection_date` as `Date`, the plotted table (`plot.data`, pandas) writes `2023-04-11 00:00:00`. The Tier 1 and Tier 2 tables stay `2023-04-11`. The golden hash of the plot `stress_species_amr` moves for this reason only. RUN (`stressplot.py`). If a bundle or export writes the plotted table, the date text differs. I did not find out whether it does (not checked).
3. `Enum` is strict (RUN): a value that is not in the list refuses the whole dataset with a message naming the column and the value (for example `column 'predicted_phenotype' (Enum): 'NI'`). It never becomes null silently. A lower-case `r`, an empty cell or the text `NA` is also refused (unless `NA` is in `null_values`). Spaces around a value are removed first when `strip: true`.
4. The hand-written equality reference (`app/tests/equality/reference_2_test_data_ST22_dummy.py`) declares `pl.Categorical` for 7 fields and compares with `assert_frame_equal`, which checks the type. If the recipe `2_test_data_ST22_dummy` becomes `String` and the reference does not, the equality test fails on type (RUN of the same comparison with a toy table: "dtypes do not match"). The four equality recipe copies and the reference must change together, or none.
5. The golden baseline `app/tests/golden/baseline.json` records the type of every column. After the change it reports "columns or types differ" for 70 tables (RUN, `golden_baseline.py --check`). It must be regenerated, and the commit must say why. The check also says the content hash is unchanged for all of them (except flag 2).
6. "Alphabetical" means byte order: upper case before lower case (RUN: `resistance_class` is drawn `DISINFECTANT, LEAF RUST, MULTI-DRUG, aminoglycoside, ...`), and numbers written as text sort as text (ST: `10, 101, 117, 131 ... 93, 95`). A reviewer may notice; Eve has accepted the alphabetical order for nominal fields.
7. Today's order depends on the order of rows in the file: with `Categorical`, 30 shuffles of the same 42-row metadata file gave 5 different level orders (RUN). With `String` the order is always France, Germany, Norway. This is a gain in reproducibility.
8. The 7 plots of the templates `e_coli`, `audit` and `simple_template` (5 plots) cannot run: their data files are not in the repository (RUN: file missing). Their order would also change (INFERRED, same mechanism). Two retest recipes fail on purpose before and after (RUN, same error).

## A. Every field, by recipe file

For each file: the fields, what the values are (read from the real data file, after `strip` and the declared missing words; a blank cell is counted as a missing value), my class, the new type, and the reason. "Q" points to section G.

### `pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml`

- `Location`: values: 2 values: 'plasmid' [5 of 11 cells blank]. Class: NOMINAL -> `String`. reference text, half blank; no plot.
- `Name_plasmid`: values: 2 values: 'ColV' [6 of 11 cells blank]. Class: NOMINAL -> `String`. reference text, half blank; no plot.
- `VirulenceFinder`: values: 2 values: 'several variants' [6 of 11 cells blank]. Class: NOMINAL -> `String`. reference text, half blank; no plot.

### `pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml`

- `taxon_1`: values: 1 values: 'Escherichia_coli'. Class: NOMINAL -> `String`. a species name; one value; no meaningful order.

### `pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml`

- `data`: values: 57 values, e.g. 'Col(MG828)', 'Col156', 'Col440I', 'ColRNAI', 'ColpVC'. Class: NOMINAL -> `String`. name of a detected item (gene, plasmid, allele); labels.
- `data_type`: values: 3 values: 'MLST', 'Plasmid', 'Resistance'. Class: NOMINAL -> `String`. kind of record (MLST, Plasmid, Resistance); labels.
- `predicted_phenotype`: values: 11 values: 'Susceptible', 'ampicillin', 'gentamicin', 'kanamycin', 'spectinomycin', 'streptomycin', 'sulfisoxazole', 'tetracycline', 'trimethoprim', 'unknown[qacE_1_X68232]', 'unknown[sitABCD_1_AY598030]'. Class: NOMINAL -> `String`. antibiotic names (not the S/I/R scale here); labels.
- `cge_predicted_phenotype`: values: 9 values: 'Amoxicillin, Ampicillin, Cephalothin,...', 'Benzylkonium Chloride, Ethidium Bromi...', 'Doxycycline, Tetracycline', 'Gentamicin', 'Hydrogen peroxide', 'Spectinomycin, Streptomycin', 'Streptomycin', 'Sulfamethoxazole', 'Trimethoprim'. Class: OTHER (list as text) -> `String`. a comma list of antibiotic names in one cell; text, no order.
- `contig`: values: 63 values, e.g. 'contig00002', 'contig00005', 'contig00006', 'contig00007', 'contig00009'. Class: NOMINAL -> `String`. contig identifier; label.
- `accession`: values: 29 values, e.g. '008486', '009781', 'AF024602', 'AF137361', 'AF534183'. Class: NOMINAL -> `String`. database accession; identifier.

### `pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml`
used by 1_test_data_ST22_dummy, 1_Abromics_general_pipeline, 3_test_no_joins, demo_abromics (data files differ for demo_abromics: 30 rows, with '-', 'N/A' and a blank declared missing)

- `scheme`: values: 1 values: 'ecoli_achtman_4'. Class: NOMINAL -> `String`. typing scheme name; one value.
- `sequence_type`: values: 19 values, e.g. '-', '10', '101', '131', '135'. Class: NOMINAL -> `String`. sequence type (ST) number: a label, not a quantity; '-' is declared missing.
- `locus_1`: values: 11 values: 'adk(10)', 'adk(101)', 'adk(13)', 'adk(20)', 'adk(21)', 'adk(36)', 'adk(37)', 'adk(43)', 'adk(6)', 'adk(96)', 'adk(97)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.
- `locus_2`: values: 16 values, e.g. 'fumC(11)', 'fumC(231)', 'fumC(24)', 'fumC(29)', 'fumC(30)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.
- `locus_3`: values: 16 values, e.g. 'gyrB(10)', 'gyrB(12)', 'gyrB(13)', 'gyrB(15)', 'gyrB(19)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.
- `locus_4`: values: 13 values, e.g. 'icd(1)', 'icd(10)', 'icd(100)', 'icd(108)', 'icd(13)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.
- `locus_5`: values: 13 values, e.g. 'mdh(1)', 'mdh(16)', 'mdh(17)', 'mdh(20)', 'mdh(23)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.
- `locus_6`: values: 15 values, e.g. 'purA(1)', 'purA(10)', 'purA(11)', 'purA(12)', 'purA(13)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.
- `locus_7`: values: 12 values: 'recA(17)', 'recA(2)', 'recA(21)', 'recA(25)', 'recA(26)', 'recA(29)', 'recA(30)', 'recA(41)', 'recA(6)', 'recA(66)', 'recA(67)', 'recA(7)'. Class: NOMINAL -> `String`. allele call such as adk(10): a label.

### `pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml`

- `quality_module`: values: 2 values: 'Passed', 'Warning'. Class: UNSURE (ordinal?) -> `String (default) or Enum [Passed, Warning]`. a quality verdict: Passed/Warning has a severity order, but the full list of verdicts is not in the data and no plot or step uses it: QUESTION Q2.
- `quality_feedback`: values: 2 values: 'All tests passed', 'Low Bracken main taxon proportion (<90)'. Class: NOMINAL -> `String`. message text, 2 values.
- `bracken_main_taxon`: values: 1 values: 'Escherichia_coli'. Class: NOMINAL -> `String`. a species name; one value.

### `pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml`

- `gene`: values: 13 values, e.g. 'aac(3)-VIa', 'aadA5', "ant(3'')-Ia", "aph(3'')-Ib", 'aph(6)-Id'. Class: NOMINAL -> `String`. resistance gene name; label.
- `predicted_phenotype`: values: 11 values: 'Susceptible', 'ampicillin', 'gentamicin', 'kanamycin', 'spectinomycin', 'streptomycin', 'sulfisoxazole', 'tetracycline', 'trimethoprim', 'unknown[qacE_1_X68232]', 'unknown[sitABCD_1_AY598030]'. Class: NOMINAL -> `String`. antibiotic names (not S/I/R in this table); label.

### `pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml`

- `quality_module`: values: 1 values: 'Passed'. Class: UNSURE (ordinal?) -> `String (default) or Enum [Passed, Warning]`. a quality verdict: Passed/Warning has a severity order, but the full list of verdicts is not in the data and no plot or step uses it: QUESTION Q2.
- `taxon`: values: 1 values: 'unknown'. Class: NOMINAL -> `String`. a species label; one value.
- `genotype`: values: 13 values, e.g. 'None', "aac(3)-VIa, ant(3'')-Ia, blaTEM-1B, q...", "aadA5, ant(3'')-Ia, dfrA17, sitABCD, ...", "ant(3'')-Ia, sitABCD", "aph(3'')-Ib, aph(6)-Id, sitABCD, tet(A)". Class: OTHER (list as text) -> `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `phenotype`: values: 8 values: 'Susceptible', 'ampicillin, unknown[sitABCD_1_AY598030]', 'gentamicin, spectinomycin, ampicillin...', 'spectinomycin, unknown[sitABCD_1_AY59...', 'streptomycin, kanamycin, unknown[sitA...', 'streptomycin, spectinomycin, trimetho...', 'unknown[sitABCD_1_AY598030]', 'unknown[sitABCD_1_AY598030], sulfisox...'. Class: OTHER (list as text) -> `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `cge_phenotype`: values: 8 values: '-', 'Amoxicillin, Ampicillin, Cephalothin,...', 'Gentamicin, Streptomycin, Amoxicillin...', 'Hydrogen peroxide', 'Hydrogen peroxide, Sulfamethoxazole', 'Spectinomycin, Streptomycin, Trimetho...', 'Streptomycin, Hydrogen peroxide', 'Streptomycin, Hydrogen peroxide, Doxy...'. Class: OTHER (list as text) -> `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `plasmid`: values: 24 values, e.g. 'Col(MG828), Col(MG828), Col(MG828), C...', 'Col(MG828), Col(MG828), ColRNAI, IncF...', 'Col(MG828), Col(MG828), IncFIA, IncFI...', 'Col(MG828), Col(MG828), IncFIB(AP0019...', 'Col(MG828), Col(MG828), IncFIB(AP0019...'. Class: OTHER (list as text) -> `String`. a comma list in one cell (several genes, drugs or plasmids); text, no order.
- `ST`: values: 20 values, e.g. '-', '10', '101', '117', '131'. Class: NOMINAL -> `String`. sequence type number: a label; '-' declared missing; text order 10,101,117 (not numeric) is acceptable for labels.

### `pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml`

- `serotype`: values: 13 values, e.g. 'O11:H25', 'O120:H4', 'O13/O129/O13/O135:H4', 'O161:H4', 'O2/O50:H1'. Class: NOMINAL -> `String`. O:H serotype label.
- `virulence_raw`: values: 48 values, e.g. 'air: Enteroaggregative immunoglobulin...', 'astA: EAST-1 heat-stable toxin', 'capU: Hexosyltransferase homolog', 'cba:  Colicin B', 'cea:  Colicin E1'. Class: OTHER (compound text) -> `String`. 'gene: description' text that a wrangling step splits: a text step needs String.

### `pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml`

- `source`: values: 3 values: 'Broiler', 'Layer', 'Parent'. Class: NOMINAL -> `String`. production type; Broiler, Layer, Parent are groups, not a scale.
- `country`: values: 3 values: 'France', 'Germany', 'Norway'. Class: NOMINAL -> `String`. country; label.

### `pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml`

- `gene`: values: 13 values, e.g. 'aac(3)-VIa', 'aadA5', "ant(3'')-Ia", "aph(3'')-Ib", 'aph(6)-Id'. Class: NOMINAL -> `String`. resistance gene name.
- `predicted_phenotype`: values: 11 values: 'Susceptible', 'ampicillin', 'gentamicin', 'kanamycin', 'spectinomycin', 'streptomycin', 'sulfisoxazole', 'tetracycline', 'trimethoprim', 'unknown[qacE_1_X68232]', 'unknown[sitABCD_1_AY598030]'. Class: NOMINAL -> `String`. antibiotic names (not S/I/R here).
- `accession`: values: 29 values, e.g. '008486', '009781', 'AF024602', 'AF137361', 'AF534183'. Class: NOMINAL -> `String`. database accession; identifier.

### `pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml`

- `Source`: values: 3 values: 'Broiler', 'Layer', 'Parent'. Class: NOMINAL -> `String`. production type; groups, not a scale.
- `Country`: values: 3 values: 'France', 'Germany', 'Norway'. Class: NOMINAL -> `String`. country; label.

### `pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml`

- `plasmid_name`: values: 18 values, e.g. 'Col(MG828)', 'Col156', 'Col440I', 'ColRNAI', 'ColpVC'. Class: NOMINAL -> `String`. plasmid replicon name; label.
- `accession`: values: 29 values, e.g. '008486', '009781', 'AF024602', 'AF137361', 'AF534183'. Class: NOMINAL -> `String`. database accession; identifier.

### `pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml`

- `host_animal_common`: values: 7 values: 'cat', 'cattle', 'chicken', 'dog', 'horse', 'swine', 'turkey'. Class: NOMINAL -> `String`. animal group; label.
- `gene`: values: 288 values, e.g. 'A7J112581', 'ARR-3', 'Col(BS512)', 'Col(KPHS6)', 'Col(MG828)'. Class: NOMINAL -> `String`. gene or replicon name; label.
- `gene_type`: values: 2 values: 'chromosome', 'plasmid'. Class: NOMINAL -> `String`. chromosome or plasmid; label.
- `gene_identifier`: values: 266 values, e.g. 'AAC(3)-II', 'AAC(3)-IIb', 'AAC(3)-IId', 'AAC(3)-IIe', 'AAC(3)-IIg'. Class: NOMINAL -> `String`. gene variant name; label.
- `gene_name_family`: values: 54 values, e.g. "\tANT(3'')", 'AAC(3)', "AAC(6')", "AAC(6')-Ib-cr", "ANT(2'')" [3371 of 10839 cells blank]. Class: NOMINAL -> `String`. gene family; label ('NA' declared missing; one value carries a leading tab that strip removes).
- `resistance_class`: values: 20 values, e.g. 'DISINFECTANT', 'LEAF RUST', 'MULTI-DRUG', 'NA', 'aminoglycoside'. Class: NOMINAL -> `String`. drug class; label (mixed upper and lower case: String order puts upper case first).

### `pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml`

- `host_animal_species`: values: 7 values: 'Bos taurus', 'Canis familiaris', 'Equus caballus', 'Felis catus', 'Gallus gallus', 'Meleagris gallopavo', 'Sus domesticus'. Class: NOMINAL -> `String`. species name; label.
- `host_animal_common`: values: 7 values: 'cat', 'cattle', 'chicken', 'dog', 'horse', 'swine', 'turkey'. Class: NOMINAL -> `String`. animal group; label.
- `specimen_source_tissue`: values: 196 values, e.g. 'abdomen', 'abdominal abscess', 'abdominal exudate', 'abdominal fluid', 'abdominal fluid swab'. Class: NOMINAL -> `String`. tissue or source label, many values.
- `final_diagnosis`: values: 379 values, e.g. '1 week old cross bred calf died of sc...', '19 day old foal w/ acute diarrhea', '3 month old foal with persistant diar...', '80% of herd had fever of 104, ruminat...', 'NA'. Class: OTHER (free text) -> `String`. a free-text diagnosis written by a person; 379 values; text.
- `animal_infection_site_uti`: values: 2 values: 'Not UTI/urine/urinary tract', 'UTI/urine/urinary tract'. Class: NOMINAL -> `String`. two labels (UTI or not).

### `pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml`

- `mic_id`: values: 50 values, e.g. 'amikacin', 'amoxicillin', 'amoxicillin_clavulanic_acid', 'ampicillin', 'azithromycin'. Class: NOMINAL -> `String`. antibiotic name (50); no scale.
- `breakpoint`: values: 2 values: 'clsi', 'iq'. Class: NOMINAL -> `String (or keep Categorical as the documented example, see Q8)`. standard used (clsi, iq); label; not plotted, not used by any step.
- `predicted_phenotype`: values: 4 values: 'I', 'NI', 'R', 'S'. Class: ORDINAL -> `Enum [S, I, R, NI]`. susceptible, intermediate, resistant (clinical scale); NI placement is question Q1.

### `pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml`

- `id`: values: 2000 values, e.g. 'REC_0', 'REC_1', 'REC_10', 'REC_100', 'REC_1000'. Class: NOMINAL (identifier) -> `String`. one distinct value per row (10000 of 10000); an identifier.
- `species`: values: 4 values: 'E. coli', 'K. pneumoniae', 'P. aeruginosa', 'S. enterica'. Class: NOMINAL -> `String`. species name; label.
- `amr_class`: values: 5 values: 'Aminoglycosides', 'Beta-lactams', 'Carbapenems', 'Fluoroquinolones', 'Tetracyclines'. Class: NOMINAL -> `String`. drug class; label.
- `collection_date`: values: 1197 values, e.g. '2020-01-10', '2020-01-11', '2020-01-12', '2020-01-13', '2020-01-14'. Class: DATE -> `Date (format %Y-%m-%d)`. ISO date text; all 10000 parse (RUN).
- `value`: values: 2000 values, e.g. '0.01', '0.02', '0.03', '0.05', '0.06'. Class: OTHER (number) -> `Float64`. decimal numbers 0.01 to 99.98 (1 or 2 decimals); all 10000 parse; text round trip identical (RUN).

### `retest/retest_bad_select_column.yaml`

- `gene`: values: 288 values, e.g. 'A7J112581', 'ARR-3', 'Col(BS512)', 'Col(KPHS6)', 'Col(MG828)'. Class: NOMINAL -> `String`. gene name.
- `predicted_phenotype`: values: 3 values: 'Ampicillin', 'Sulfonamide', 'Tetracycline'. Class: NOMINAL -> `String`. antibiotic name.

### `retest/retest_broken_header.yaml`

- `gene`: values: 288 values, e.g. 'A7J112581', 'ARR-3', 'Col(BS512)', 'Col(KPHS6)', 'Col(MG828)'. Class: NOMINAL -> `String`. gene name.
- `predicted_phenotype`: values: column absent in the file on purpose (broken header test). Class: NOMINAL -> `String`. antibiotic name.

### `retest/retest_tier2.yaml`

- `group`: values: 3 values: 'A', 'B', 'C'. Class: NOMINAL -> `String`. group label A, B, C.
- `year`: values: 3 values: '2022', '2023', '2024'. Class: UNSURE (ordinal by time) -> `String (default) or Enum ['2022','2023','2024']`. a year used as a label; 4-digit text sorts in time order; QUESTION Q3.

### `retest/retest_top_n_other.yaml`

- `variant`: values: 9 values: 'V1', 'V2', 'V3', 'V4', 'V5', 'V6', 'V7', 'V8' [1 of 21 cells blank]. Class: NOMINAL -> `String`. variant label.

### `templates/audit.yaml`

- `lab_id`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL (identifier) -> `String`. laboratory identifier; is_entity_key.
- `submission_date`: values: no data file in the repo (templates read files that are not shipped). Class: DATE -> `Date (format not verifiable: no data)`. a date; no data file, format assumed ISO.
- `status`: values: no data file in the repo (templates read files that are not shipped). Class: UNSURE (ordinal?) -> `String (default)`. a workflow status (such as pending, done): order unknown, values not in the repo; QUESTION Q4.

### `templates/complex_template/genomics_input.yaml`

- `gene_presence`: values: 27 values, e.g. ' blaTEM-1', ' catA1; dfrA17', ' sul2;  catA1;  strB', ' sul2; sul1', "aph(3')-Ia;dfrA17;strB;strA" [1 of 30 cells blank]. Class: OTHER (list as text) -> `String`. semicolon list of genes in one cell.

### `templates/complex_template/metadata_input.yaml`

- `country`: values: 5 values: 'Denmark', 'Finland', 'Norway', 'Sweden' [1 of 29 cells blank]. Class: NOMINAL -> `String`. country; label.

### `templates/e_coli.yaml`

- `serotype`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. serotype label.
- `sequence_type`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. ST number: a label.
- `ctx_m_gene`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. CTX-M gene name; label (no data: meaning not verifiable).
- `collection_date`: values: no data file in the repo (templates read files that are not shipped). Class: DATE -> `Date (format not verifiable: no data)`. a date; no data file, format assumed ISO.
- `country_of_origin`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. country.
- `hospital_site`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. site label.
- `patient_outcome`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. outcome label (values unknown; if it is a scale such as recovered/died it would be a question).

### `templates/simple_template.yaml`

- `group`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. group label.
- `category`: values: no data file in the repo (templates read files that are not shipped). Class: NOMINAL -> `String`. category label.

### `assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml`

- `Location`: values: 2 values: 'plasmid' [5 of 11 cells blank]. Class: NOMINAL -> `String`. reference text, half blank; no plot.
- `Name_plasmid`: values: 2 values: 'ColV' [6 of 11 cells blank]. Class: NOMINAL -> `String`. reference text, half blank; no plot.
- `VirulenceFinder`: values: 2 values: 'several variants' [6 of 11 cells blank]. Class: NOMINAL -> `String`. reference text, half blank; no plot.

### `pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly_output_fields.yaml`

- `sample_id`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `ST`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `quality_metric`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7

### `pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml`

- `plasmid`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `hsp_lengthtotal_length`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `contig`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
- `accession`: class OTHER (legacy) -> unchanged. lower-case 'categorical' is not a type; no recipe includes this file (READ); leave or delete: Q7
