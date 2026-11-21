# TESTLAB-REVIEW-1, step 2: what the Test Lab must be

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396: "TEST_LAB: a review to plan its rebuild (fallback task, the same kind as BLUEPRINT-REVIEW-1)"). It builds nothing and decides nothing. Every open choice is "to decide", with its options.

## Summary (10 lines)

1. Her description: "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format" (`ORDER.md`). Nothing else she said describes what the Test Lab is for.
2. Five journeys use it: put raw files into the format the app reads; make synthetic data, with planted errors, to test a recipe; match sample ids between two files; anonymise before sharing; start a recipe from data files.
3. Each journey ends with a file. Today only one of these files can be opened by the next user space as it is: a reformatted or synthetic TSV, through HOME's Data Import panel, and only when its column names match a recipe that is already loaded (section 2).
4. The recipe the scaffold writes cannot be opened anywhere: BLUEPRINT's upload takes one `.yaml`, HOME has no recipe upload on screen, and the engine refuses a recipe with no plot.
5. Her first example, "testing from synthetic data", is not reproducible today: no seed on the screen, no record of the settings in the download.
6. Her second example, "the correct format", has two readings: a tab-separated file (what the reformatter makes), or the columns and types a given recipe declares (no tool checks a file against a recipe).
7. Three decided rules are broken by what the Test Lab writes: the sample id may be written as a number (D-0225), the entity key is guessed from a column name instead of declared (D-0082, D-0216), and several results change silently (D-0050) (section 4).
8. The libraries hold more than the screen offers; the scripts in `assets/scripts/` do some of the same jobs, and one of them already writes a recipe with a first plot, which HOME can load (section 3.7).
9. The boundaries are mostly clear in the records (single key in the Test Lab, joins and full recipe edit in BLUEPRINT, no in-app hand-off); the scaffold's join crosses the first one (section 5).
10. Her words say "for the user"; the flags show the Test Lab only in the `developer` and `qa` setups. This is a point to decide, not a defect (section 6).

## How to read this file

Labels on every fact:

- **read**: I read it now (2026-11-21), in this worktree (branch `task/lab-review` at `9fbcc616`; no Test Lab code differs from `dev` `9e72c36d`), at file:line.
- **read-1**: from step 1 (`02_planned_vs_existing.md`, `03_parked_items_and_known_gaps.md`, tree `52c4bcfa`); not re-read. The section of `02` or `03` is given.
- **run-1**: run in step 1 by the probes now kept in `prior_work/probes_2026-11-21/` (cases A to G of `02`).
- **document**: taken from a text, not re-checked against the code.
- **reading**: my reading of the facts; not a fact and not decided.

Short names: `H` = `app/handlers/test_lab_handlers.py`, `S` = `app/modules/test_lab_studio.py`, `SC` = `libs/test_lab/src/test_lab/scaffolder.py`, `BS` = `.../bootstrapper.py`, `AQ` = `.../aqua_synthesizer.py`, `AN` = `.../anonymiser.py`, `RF` = `.../reformatter.py`, `EX` = `.../extractor.py`, `DI` = `app/handlers/data_import_handlers.py`.

What the owner wants is quoted only from `ORDER.md` or from a ledger line of `.claude/knowledge/decision_ledger.md` that is DECIDED and taken by EVE (number and words; I read each line now). Anything else is a document or my reading.

---

## 1. What the owner asked, and the decided rules that apply

### 1.1 Her words about the Test Lab

| Source | Her words |
|---|---|
| `ORDER.md` (block M422) | "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format --- same kind of work low priority if nothing else and lab_revision subdirectory - also a preparation without details" |
| `ORDER.md` (block M423) | "yes it will have to explore what we had planned, what is existing, many things will need to be anyway verified and updated" |
| D-0048 | "Order of work HOME, then Gallery, Blueprint and Test Lab last" (decision field) |
| D-0271 | her words in the evidence field: "we do changes to blueprint and lab after - we focus on home and gallery" |

The other descriptions of the Test Lab (`spaces/TEST_LAB.md:14-19`: "a collection of small, focused utilities that help users prepare data for the app and test the app itself", for data stewards, developers and testers, recipe authors) are design documents of May 2026 (read now), not her decided words. They agree with her description; they add the developers and testers.

### 1.2 Decided rules that the Test Lab's output must follow

All lines below are DECIDED and taken by EVE (read now). None of them names the Test Lab; they apply to it because the Test Lab writes recipes and data files. Applying them to the Test Lab is my reading, marked where it matters (section 4).

| Number | Words of the line |
|---|---|
| D-0050 | "No silent error that is the rule." (her words, evidence field) |
| D-0015 | "the software informs, warns, lets the user decide; a risky choice needs a recorded reason; only technical problems block" (decision field) |
| D-0225 | "The sample id is a string or a categorical, never a number" (decision field) |
| D-0067 | "in our recipes samples id must be either string or categorical" (her words, evidence field) |
| D-0082 | "Keys are declared in the recipe" (decision field) |
| D-0216 | "Important for the person to make the recipe would add which is id" (her words, evidence field) |
| D-0004 | "it should be reproducible" (her words, quoted in the decision field) |
| D-0056 | "every seed that is used is written in the recipe or the audit recipe" (decision field; about recipes) |
| D-0007 | "recipe `id` = file name" (decision field) |
| D-0390, D-0392 | "A recipe file name is name_date, exactly." (D-0390); "The rule covers real production recipes." (D-0392) |
| D-0102 | "full recipe edit exists only in Blueprint" (decision field) |
| D-0306 | "Blueprint is the UI IDE for building the recipes and must be able to build the WHOLE recipe" (decision field) |
| D-0374 | "Informing about undeclared file columns belongs to the user space BLUEPRINT." (decision field) |
| D-0381 | "BLUEPRINT, GALLERY and TEST_LAB use the same width and drag mechanism for their side panels as HOME" (decision field; the line says the wording is the coordinator's) |

The goal text that every agent works under (`.claude/workflows/decision_compliance.md` section 1, approved by her: "1. ok"): "the same data and recipe give the same result, and nothing changes a result silently. The software informs the user and does not choose for the user."

---

## 2. Who uses the Test Lab and for what: five journeys

Each journey says who, what they start with, what the Test Lab does today, the file they leave with, where it goes next, and whether that next place can open it today.

### J1. A user with raw files who needs them in the format the app reads

- **Who.** A data steward or scientist whose pipeline gives Excel workbooks or comma, semicolon or pipe files (document: `TEST_LAB.md:16-17`).
- **Today.** "File reformatting": one file at a time; an Excel file gives one TSV per ticked sheet in a ZIP; a delimited file gives one TSV with the delimiter the user picks, default comma (read: `H:966-993`). A delimited file is read with every column as text (read-1: `02` F, `RF` `infer_schema_length=0`); an Excel file keeps Excel's cell types (read-1: `RF:68`). Unticking every sheet gives all sheets (read-1: `H:979`). No count of rows or columns is shown (read-1: `H:950-965`). No record of what was done goes with the file (read: the download writes only the TSVs, `H:977-993`).
- **Leaves with.** `<name>.tsv`, or `<name>_converted.zip` of TSVs (read: `H:995-1000`).
- **Goes next.** (a) HOME's Data Import panel, which accepts `.tsv` and `.csv` (and Excel when `data_ingestion_enabled` is on), checks each file against the declared fields of the table it is assigned to, and writes it into the deployment's raw data folder as `<table><ext>` (read: `DI:131-175`, `DI:257-338`). The panel's upload exists only in "testing mode" (read: `DI:131-140`; `testing_mode: true` in `pipeline-exploration-advanced`, `standalone`, `developer`, `qa`, read: `config/app_features/*.yaml`). (b) The scaffold of J5.
- **Can the next place open it today?** A TSV: yes, through Data Import, when its column names match the declared fields of a recipe already loaded (read: `DI:273-315`, `MetadataValidator.validate`). The ZIP: no, it must be unzipped first (Data Import accepts no `.zip`, read: `DI:151`). Whether a type mismatch (for example an Excel number in a text field) is refused there: not verified.
- **Open point.** What "the correct format" means (her words): the file type only (TSV), or what a given recipe declares (column names, types, missing-value words). No Test Lab tool reads a recipe (read-1: `03` 1.11; "Test Lab tools don't operate on an open data analysis recipe", `home_theater.py:1955-1957`, a choice of 2026-11-08 as reported in the code comment).

### J2. A recipe maker who needs synthetic data, with planted errors, to test a recipe

- **Who.** A recipe author or tester (document: `TEST_LAB.md:18`; her example "testing from synthetic data", `ORDER.md`).
- **Today.** "Synthetic data": from an uploaded file (first 100 rows, read as tab-separated) or from a typed list of column names; rows 10 to 5000; mode demo or stress; in stress mode two error kinds of six (missing values, duplicate ids) (read-1: `02` D). The generator is called without a seed (read: `H:639`, `synth.generate(config)`; `AQ:77-86` seeds only when a seed is given). A text column with more than 15 distinct values becomes `value_A/B/C`; no date type (read-1: `02` D). The id column is a key only when it is unique and its name looks like a key (read-1: `AQ:20-28, 143-148`).
- **Leaves with.** One TSV (read: `H:667-675`, `df.write_csv(..., separator="\t")`); no seed, no settings, no list of the planted errors.
- **Goes next.** HOME's Data Import panel (as J1) to replace a table's file of the recipe under test; or the deployment's raw data folder by hand.
- **Can the next place open it today?** Yes when the column names match the recipe's declared fields (as J1). Reading, not verified: a stress file with planted type errors may be refused by Data Import's check before the recipe ever runs, so the recipe's own handling of bad values is not what gets tested.
- **Not reproducible.** The same settings give another file the next time (reasoned from `H:639` and `AQ:84-86`). The library can do better: `generate(seed=...)`, `save_config`, `load_config`, named scenarios (read-1: `AQ:77-129`); none is on the screen.
- **Several tables with one set of ids.** The generator makes one table at a time. The demo data script does not use it for that reason: "it generates ONE table at a time from a column config and keeps no shared set of ids, so it cannot promise a common set or one row per sample and scheme" (read: `assets/scripts/generate_demo_data.py:16-18`). Her rule for test data is one common set of ids (D-0205: "the same set of ids are used across all the datasets of the recipes", her words).

### J3. A user whose sample ids do not match between two files

- **Who.** Anyone joining two result files from different tools.
- **Today.** "ID reconciliation": two files, one id column each; exact, then one pattern, then fuzzy matching; a table with a certainty per pair; a threshold slider; a YAML download (read-1: `02` C). There is no confirm or reject per pair (the design asks for it, `TEST_LAB.md:151-162`, document). The cleaning step written for the matches acts on the whole column and breaks ids that already matched (run-1: case C), and a hyphen-to-underscore match gives a step that undoes nothing (run-1: case D); both are recorded as strict expected failures (read-1: `test_suggested_steps.py:87-112`). Fuzzy matches are not written as steps and the screen does not say so (read-1: `02` C).
- **Leaves with.** `id_transformation.yaml` in the library's own step language (`ref_column`, `target_column`, `steps`, `metadata`); no file names, no date, no match counts (read-1: `02` C, K17).
- **Goes next.** Only the scaffold of J5, in the same session ("Bake in ID Reconciliation steps", read-1: `H:366-401`), which turns the steps into recipe steps (`recipe_steps`). No user space reads the transformation file: the Test Lab has no upload for it; BLUEPRINT's upload takes a recipe `.yaml` (read: `wrangle_studio.py:225-226`); whether BLUEPRINT would read this file is not verified (it is not a recipe).
- **Can the next place open it today?** No, outside the same Test Lab session.

### J4. A user who must anonymise before sharing

- **Who.** A data steward (document: `TEST_LAB.md:16-17`).
- **Today.** "Anonymisation": one file; an id column; personal columns ticked to be stripped into the mapping; sequential, hash or custom pattern (read-1: `02` E). The id column is renamed `anon_<column>` and moved first, which the screen does not say (read-1: `AN:119, 307-309`). An empty id crashes the tool (run-1: case F). Two files anonymised one after the other get different new ids for the same sample with the sequential pattern; the several-file function exists in the library only (read-1: `02` E).
- **Leaves with.** One ZIP: `anonymised_<stem>.tsv`, `mapping_<id column>.tsv`, and `anonymisation_config.yaml`, an audit record with a header that says it is not a recipe, holding the date, the id column, the personal columns, the pattern, the prefix, the file names and the mapping file name (read: `H:813-835`; `AN:118-139, 336-359`). The handler passes the temporary upload path (read: `H:816-817`, `info["datapath"]`), so the stem and the file name in the record are likely Shiny's upload number, not the user's file name: the same defect as the scaffold's table names (reasoned; not run).
- **Goes next.** Outside the app (sharing); or HOME's Data Import. The way back (a join that restores the ids) is "printed in the Anonymiser's own output" in the user doc (document: `docs/workflows/developer_workflow.qmd:89`); the function exists, writes the old action name `join`, and is not called (read-1: `AN:228-246`; `prior_work/step4c_report.md` lists it as not fixed).
- **Can the next place open it today?** Reading, not verified: a recipe that declares `sample_id` will not find `anon_sample_id`, so Data Import's check refuses the file unless the recipe is changed. The mapping travels in the same ZIP as the anonymised table, with no warning (read-1: `H:716-718`); ADR-097 point 8 recommends anonymising "before data ever reaches the app, with any de-anonymisation key kept outside it entirely" (read-1: `01` section 2; contradiction K10 of `02`).

### J5. A user who starts a recipe from data files

- **Who.** A recipe author (document: `TEST_LAB.md:19`).
- **Today.** "Data analysis recipe scaffolding": a recipe id, the data files, an optional metadata file, a join key box pre-filled `sample_id`, optional ID cleaning steps; a ZIP (read-1: `02` B1). The tables are named after Shiny's upload numbers `0`, `1` (run-1: case A); the data path is the temporary upload path, which the checker refuses as absolute (run-1, read-1: `02` B1); a numeric-looking id is typed `Int64` (run-1: cases A, B); the entity key is marked by column name (read-1: `SC:158-159`); every table is inner-joined to the first on the typed key (read-1: `SC:122-138, 177-189`); no plot is written, so the engine refuses to load it (run-1: case G).
- **Leaves with.** `<id>.zip`: `<id>/<id>.yaml` plus per table a fields file and a tier-1 file, and a join file when there are two tables; no data files.
- **Goes next.** The status line says "Download the ZIP and open in BLUEPRINT to continue" (read-1: `H:509-510`).
- **Can the next place open it today?** No. BLUEPRINT's upload takes one `.yaml` (read: `wrangle_studio.py:225-226`) and lists recipes from a fixed folder (read-1: `02` I). HOME has no recipe upload on screen: the handler `handle_ingest` reads an input `file_ingest` that no UI creates (read: `app/handlers/ingestion_handlers.py:39-58`; grep finds `file_ingest` only there). Even unzipped by hand into the recipe folder, the recipe is refused until a plot is written (run-1: case G).

### Summary of the hand-offs

| Journey | File the user leaves with | Next place | Opens today? | Label |
|---|---|---|---|---|
| J1 format | TSV, or ZIP of TSVs | HOME Data Import (testing mode) | TSV yes if the column names match a loaded recipe; ZIP no | read |
| J2 synthetic | TSV, no seed, no settings | HOME Data Import | yes if the names match; not reproducible | read; reproducibility reasoned |
| J3 ids | `id_transformation.yaml` | the scaffold, same session only | no elsewhere | read-1, read |
| J4 anonymise | ZIP: table, mapping, record | outside the app; HOME Data Import | renamed key column: reasoned no | read; reasoned |
| J5 recipe | ZIP of a recipe with no plot, no data | BLUEPRINT, HOME | no | read, run-1 |

Hand-offs between user spaces are files, by decision (ADR-093; the "Send to scaffolding" and "Open in BLUEPRINT" buttons were dropped on 2026-05-22 for space independence, read-1: `01` section 5). So the question for the rebuild is not "add a button" but "make the file one that the next space can open".

---

## 3. The tools one by one

Columns: planned (source) / in the library / reachable on the screen / tested (test functions, counted, not run) / what must be verified and updated. Detail: `02` sections B to F.

### 3.1 File reformatting

| Planned | Library | On screen | Tested | Verify and update |
|---|---|---|---|---|
| XLSX to one TSV per sheet; CSV to TSV; a folder at once (`TEST_LAB.md:25-31`, document) | `convert_xlsx`, `convert_csv`, `convert_folder` (read-1) | one file; sheets; a delimiter list, default comma (read: `H:966-993`) | `test_reformatter.py` (20, read-1) | the delimiter is not guessed and not shown; no sheet ticked means all; two sheet names may give one file name (reasoned); no record; Excel number cells and leading zeros (not run) |

### 3.2 The Excel extractor

| Planned | Library | On screen | Tested | Verify and update |
|---|---|---|---|---|
| "Stage A" of an automation path (`docs/workflows/test_lab_sdk.qmd`, document) | `XlsxExtractor.extract`: a sheet to TSV with the key renamed `id`; prints and skips a sheet without the key (read-1: `EX:12-73`) | no (read-1: grep) | `test_extractor.py` (6) | a third sheet converter beside `RF` and `ExcelHandler` (`libs/ingestion`); renaming the key to `id` hides its meaning (reasoning); wire or remove |

### 3.3 ID reconciliation

| Planned | Library | On screen | Tested | Verify and update |
|---|---|---|---|---|
| 2 to 6 files; confirm each match below 100%; chunked review; recode form; a transformation file with files, date, who, counts, audit log; reuse by upload (`TEST_LAB.md:68-320`, document) | two lists; exact, pattern, fuzzy; eight recode actions; YAML round trip (read-1) | two files, the table, a slider, a download (read-1: `H:55-310`) | `libs/id_reconciliation/tests` (56), `app/tests/test_id_cleaning_steps_reach_a_recipe.py` (16) | the cleaning step breaks matched ids (run-1); fuzzy matches dropped silently; "A written reason is required" not enforced (read-1: `H:221-224, 302-310`); the shim `pattern_detector.py` (open task PATTERN-DETECTOR-SHIM-1: remove it); the pattern helper not shared with BLUEPRINT although its `@deps` says so |

### 3.4 Recipe scaffolding (and the bootstrapper)

| Planned | Library | On screen | Tested | Verify and update |
|---|---|---|---|---|
| A boilerplate from data files: structure, types, key hints, ID cleaning steps, `joins: {}` (ADR-084 point 6, document); the user picks the key after reconciling, the system checks uniqueness (`TEST_LAB.md:331-347`, document) | `SC.scaffold` (ZIP, writes a join); `BS.bootstrap` (folder, `joins: {}`) not called by any screen (read-1) | yes (read-1: `H:316-531`) | `test_scaffolder.py` (24), `test_bootstrapper.py` (18), both run the checker in profile `build` with file names and text ids that hide defects 1 and 3 of `03` (read-1) | upload names as table names; temporary absolute path; `Int64` key; key by name; silent `sample_id` default; inner join; no plot, so it never loads; recipe id not checked |

### 3.5 Synthetic data

| Planned | Library | On screen | Tested | Verify and update |
|---|---|---|---|---|
| From a schema or example data, per-column review; dates, distributions; six error kinds; seed; config saved; named scenarios (`TEST_LAB.md:657-810`, document) | `propose_config`, `generate(seed=...)`, six error kinds, `save_config`, `load_config` (read-1) | file or names, rows, mode, two error sliders (read-1) | `test_synthesizer.py` (21) | no seed and no config on screen (read: `H:639, 667-675`); `np.random.seed` sets the random state of the whole process when a seed is given (read: `AQ:84-86`; reasoning: another part of the app that uses numpy's global state would be affected); comma file read as tab (run-1: case E); one table at a time (read: `generate_demo_data.py:16-18`) |

### 3.6 Anonymisation

| Planned | Library | On screen | Tested | Verify and update |
|---|---|---|---|---|
| Several files consistent; personal columns into the mapping; patterns; reversible by a join printed in the output; the mapping private (`TEST_LAB.md:514-653`, document) | `anonymise`, `anonymise_batch`, `build_deanon_steps` (old name `join`) (read-1) | one file; ZIP with the mapping (read: `H:805-835`) | `test_anonymiser.py` (read-1: in the 111 functions of `libs/test_lab/tests`) | crash on an empty id (run-1); renamed key column; unsalted 8-character hash (reasoned risk); the mapping next to the data (ADR-097 point 8) |

### 3.7 The same jobs done outside the Test Lab

The rebuild must know these, because two mechanisms for one job is what the owner's rules forbid ("One authoritative way to do each thing", `rules_legacy_management.md`, a rule file; reading that it applies here).

| Job | Outside the Test Lab | Fact | Label |
|---|---|---|---|
| Start a recipe from TSV files | `assets/scripts/create_data_analysis_recipe.py` | writes a recipe of format 1 WITH a first plot ("Rows per <first column>", group "First look"), through `utils.recipe_factory` | read: lines 1-5, 150-165 |
| Start a recipe from one file | `assets/scripts/SF_create_data_analysis_recipe.py` | writes a recipe with no plot (`plots={}`) | read: lines 1-6, 63-64 |
| Minimal recipe writer | `libs/utils/src/utils/recipe_factory.py` | `minimal_recipe` writes a default bar chart unless `plots={}`; "`plots={}` writes `analysis_groups: {}`: a draft, valid in profile `build` only" | read: lines 130-187 |
| Synthetic data with one set of ids | `assets/scripts/generate_demo_data.py` | three tables from one set of ids, a seed, messy values on purpose | read: lines 8-30 |
| Small synthetic tables for one recipe | `make_complex_template_data.py`, `make_left_join_lesson_data.py` | a seed each (`random.Random(seed)`) | read: grep of `seed` |
| Excel to TSV | HOME Data Import (Excel accepted when `data_ingestion_enabled`); `ExcelHandler` in `libs/ingestion` | the Excel path of HOME is "Deferred" in the UI contract section 10 (document) | read: `DI:151`; document |

So the writer that makes a loadable first recipe already exists (`recipe_factory` with a first plot), and the Test Lab's scaffolder does not use it (reading: `SC` builds its own dictionaries, read-1 `02` B1).

---

## 4. What the decided format and rules require of what the Test Lab writes

| # | Requirement | Source | What the Test Lab writes today | Respected / violated | Evidence |
|---|---|---|---|---|---|
| F1 | Recipe format 1: `spec_version: 1`, the tiers as own keys, prefixed action names, `'on'` quoted, no `output_fields` | `recipe_format_spec.md` (document); D-0250 "Tier container is B: a tier is written as its key" | scaffold and bootstrapper: yes | respected (scaffold, bootstrapper); violated by the anonymiser's de-anonymising step (old name `join`, not on screen) | read-1: `02` B2; read-1: `AN:228-246` |
| F2 | The recipe id equals the file name | D-0007 | `<id>/<id>.yaml`; the id is not checked for spaces or slashes | respected in the layout; not checked | read-1: `SC:146`, `H:408-413` |
| F3 | A loadable recipe has a plot | the engine and HOME's gate (document: `rules_data_analysis_recipe_structure.md` section 11) | no plot | violated for "open it next": the engine refuses it | run-1: case G |
| F4 | The sample id is a string or a categorical, never a number | D-0225, D-0067 | a numeric-looking id is `Int64`; Excel sheets keep Excel number types (reasoned); CSV reformatting reads all as text | violated (scaffold); unknown (Excel reformatting, not run); respected (CSV reformatting) | run-1: cases A, B; read-1 |
| F5 | The entity key is declared by the person who makes the recipe, not guessed | D-0082 "Keys are declared in the recipe"; D-0216 "Important for the person to make the recipe would add which is id" | `is_entity_key` set on a column named `id`, `sample_id` or `isolate_id`; the user's typed key is not marked; an empty key box gives `sample_id` silently; the synthesizer finds the key by name | violated | read-1: `SC:158-159`, `BS:81-82`, `H:421-424`, `AQ:20-28` |
| F6 | Reproducibility: the same input and settings give the same file; the seed and the settings travel with every generated file | D-0004 "it should be reproducible"; D-0056 (seeds written in the recipe; it is about recipes: applying it to Test Lab files is my reading); the goal text | synthetic: no seed, no settings; anonymisation: a record (`anonymisation_config.yaml`); ID transformation: steps, no files, no date; reformatting: no record; scaffold: the recipe itself, with no note of the source file names | violated (synthetic, reformatting); partly (ID transformation, scaffold, anonymisation: the record holds the settings, but likely the upload number instead of the file name, and no app version) | read: `H:639, 667-675, 816-817, 975-993`; `AN:118-139, 336-359`; the file name reasoned |
| F7 | Nothing changes a result silently | D-0050 "No silent error that is the rule."; the goal text | inner join drops rows with no partner; the cleaning step breaks matched ids; 21 `except Exception` blocks with quiet defaults; no sheet ticked means all; key renamed `anon_<column>`; the duplicate slider does nothing without a recognised key; only the first 100 rows read; fuzzy matches left out | violated | read-1: `03` section 2, items 5, 7, 11, 14, 22, 24, 28, 31, 35; run-1: case C |
| F8 | The tool informs; the user chooses | D-0015 "the software informs, warns, lets the user decide" | the tools choose without showing: the delimiter by file ending, types from 100 rows, the key by name, the join type, the first file for the cleaning steps (now told, `H:451-460`) | violated, except the one message | read-1: `02` A, B1, C |
| F9 | Recipe file names `name_date` | D-0390; scope D-0392 "real production recipes" | the scaffold writes `<id>.yaml` with no date | not applicable today if a scaffold is not a production recipe: to decide | read-1: `01` section 4 |
| F10 | Undeclared file columns are BLUEPRINT's to tell | D-0374 | the scaffold declares every column of the file | not concerned | read-1 |
| F11 | Formulas checked before they run | FORMULA-SAFETY-1 (task; the owner's confirmation open) | the recode `mutate` goes through `utils.formula_check` | respected as built | read-1: `03` 1.7 |

---

## 5. The boundaries

### 5.1 With BLUEPRINT

| Point | Record | Today | Label |
|---|---|---|---|
| Full recipe edit | D-0102 "full recipe edit exists only in Blueprint"; D-0306 BLUEPRINT "must be able to build the WHOLE recipe" | the Test Lab writes new recipe files; it edits none | read (ledger); read-1 |
| Joins | ADR-084 point 5: single key in the Test Lab, joins designed in BLUEPRINT; ADR-084 point 6 and `rules_test_lab.md` table 4a: the scaffold writes `joins: {}` | the scaffold writes an inner join of every table to the first (contradiction K1 of `02`) | read-1 |
| How a table enters a recipe | the BLUEPRINT review lists it as its first open choice: "(a) Test Lab boilerplate, then BLUEPRINT; (b) a table and field editor in BLUEPRINT; (c) a branch copy of a table" (`../blueprint_revision/04_what_blueprint_must_be.md`, To decide #1, read now) | (a) is the only way that exists, and its file cannot be opened (J5) | read |
| The empty draft | `tasks.md:220` (WRITERS-W8-1, "DECISIONS FOR EVE"): the loader refuses a recipe without a plot; BLUEPRINT's new draft has the same problem | one decision covers both spaces | read-1: `03` 1.5 |
| The pattern helper | ADR-084 point 3 (shared through `libs/utils`) against ADR-082 ("each space keeps its own implementation until a clear duplication emerges") | not shared | read-1: K6 |
| Columns a file has and the recipe does not declare | D-0374: BLUEPRINT tells the user | n/a for the Test Lab | read |
| Hand-off | by file only (ADR-093); buttons dropped on 2026-05-22 | ZIP that BLUEPRINT cannot open | read-1 |

### 5.2 With HOME

| Point | Record | Today | Label |
|---|---|---|---|
| HOME runs recipes; the Test Lab does not open one | "Test Lab tools don't operate on an open data analysis recipe" (code comment, 2026-11-08) | as stated | read-1 |
| Getting data into HOME | HOME's Data Import panel (testing mode) checks files against the recipe and writes them into the raw data folder | the Test Lab's TSVs can go there by download and upload | read: `DI:131-175, 257-338` |
| Excel in two places | HOME Data Import accepts Excel when `data_ingestion_enabled` is on; the Test Lab reformatter converts Excel | two paths for one job (reasoning) | read: `DI:151`; read-1 |
| Making a recipe when none is usable | HOME names "Blueprint/Test Lab" as the place to make one (ADR-094) | both lead to files HOME cannot open (J5; BLUEPRINT's draft) | read-1: `01` section 2 |
| Recipe upload in HOME | none on screen (`file_ingest` is not created by any UI) | - | read |

### 5.3 With the Gallery

| Point | Record | Today | Label |
|---|---|---|---|
| The Gallery takes no input | D-0046: "dead submission code goes"; `gallery_viewer.py:18`: "the submission modal was removed" | no hand-off in either direction | read |
| Example data of a Gallery bundle | each bundle has `example_data.tsv` (document: `rules_gallery_standards.md` section 1); small synthetic data for a template is made by a script (D-0062 "small synthetic data is made for `complex_template`"; `make_complex_template_data.py`) | the Test Lab's synthetic data is not used for it | read |

---

## 6. "Utilities for the user" and the flags: a point to decide, not a defect

- Her words: "a set of utilities for the user to help user" (`ORDER.md`). They do not name an app features setup.
- The flags: `test_lab_enabled` is true in `developer` and `qa` only, false in `pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`, `standalone`, `demo-vetinst`, `web-demo` (read-1: `02` A and J). The in-app help says the Test Lab is "not visible to scientist-facing app features files" (read-1: `app/src/help/test_lab.md:21`). The task CONFIG-REVIEW-1 keeps the Test Lab developer-only in its target setups (read-1: `03` 1.12).
- The design document names three audiences, two of which are not developers: data stewards and recipe authors (document: `TEST_LAB.md:16-19`).
- So the records do not say whether a scientist using `standalone` should reach some or all of the tools. Options (mine, for the guide): (a) keep the Test Lab in `developer` and `qa` only; (b) show it in `standalone` too; (c) one flag per tool, so a setup shows only the safe tools (reformatting, anonymisation) to scientists; (d) some tools become command-line scripts only (the scripts of section 3.7 already do some jobs). Each changes the flag matrix of `rules_app_features_flags.md` and the target of CONFIG-REVIEW-1.

---

## 7. What to verify before a rebuild

| # | What | Why | How |
|---|---|---|---|
| V1 | Each tool in a browser, with the `developer` setup | nothing was seen on a screen in this review | start the app, run each tool once with the files of `prior_work/` probes |
| V2 | A reformatted TSV and a synthetic TSV through HOME's Data Import | the only hand-off that may work today (J1, J2) | upload into a table of a loaded recipe; read the message |
| V3 | What Data Import does with planted errors (wrong types, missing values) | a stress file may be refused before the recipe runs (J2) | upload a stress file from the synthesizer |
| V4 | An anonymised file into Data Import | the renamed key column (J4) | as V2 |
| V5 | An Excel id column with leading zeros through the reformatter | D-0225 | convert a sheet with `007` typed as a number and as text |
| V6 | The file name in `anonymisation_config.yaml` and in the anonymised file's name, through a real upload | likely the upload number (J4, F6) | browser: anonymise `isolates.tsv`, open the ZIP |
| V7 | Whether anything calls `BS.bootstrap()`, the extractor, `AQ.main()` outside the repository | before removing anything | ask the owner's other repositories (outside this review) |
| V8 | The UML diagrams of the Test Lab against the code | never compared (read-1: `01` section 7) | `audit_uml_model.py`, then the four diagrams |
| V9 | The tests that use real file names and text ids | they hide the upload-name and `Int64` defects | read `test_scaffolder.py:9-27`, add the Shiny names in a scratch copy |
| V10 | The same-session carry-over of ID steps into the scaffold | the only in-space hand-off (J3) | browser: reconcile, tick "Bake in", scaffold, read the tier file |
| V11 | Global random state | `np.random.seed` in the synthesizer sets the process-wide state | read who else in the app uses `np.random` without its own generator |

## Not verified

- Nothing was seen in a browser; every statement about the screen is read from the code.
- Data Import's handling of type errors, of a renamed key column and of planted errors (V2 to V4).
- The file name the anonymiser writes through a real upload (V6), and `ExcelHandler`.
- Whether BLUEPRINT's upload would read an `id_transformation.yaml`.
- The test functions were counted, not run.
- Rows marked read-1 rely on step 1; the Test Lab code did not change since (run now: `git diff --stat 52c4bcfa HEAD` on `libs/test_lab`, `libs/id_reconciliation`, `H`, `S`, `id_patterns.py`, `DI` shows no change), but I did not re-read every line.

## To decide (for the guide)

Each is open. Options are those the records name, plus mine where marked "mine".

| # | Choice | Options | Pros | Cons |
|---|---|---|---|---|
| 1 | Who the Test Lab is for (section 6) | (a) developer and qa only; (b) also standalone; (c) one flag per tool; (d) some tools as scripts only (mine) | (a) as built; (b) matches "for the user"; (c) safe tools for scientists only; (d) less screen to keep | (a) her words say "user"; (b) every tool must then be safe for a non-developer; (c) more flags; (d) a scientist cannot run a script |
| 2 | What "the correct format" means (J1) | (a) a TSV; (b) what a chosen recipe declares (names, types, missing-value words), checked; (c) both, the second optional (mine) | (a) as built, simple; (b) the user learns before HOME refuses the file | (b) the Test Lab then reads a recipe, against the choice of 2026-11-08 recorded in the code |
| 3 | What every generated file carries (F6) | (a) nothing extra; (b) a record of the settings and the seed in the download; (c) the record plus a "make it again" upload | (b), (c) reproducible, as D-0004 asks for recipes | more files in each download |
| 4 | How a scaffold becomes a recipe that opens (F3, J5) | (a) the loader accepts a draft with no plot; (b) the scaffold writes a first plot, as `create_data_analysis_recipe.py` does; (c) a draft profile in the checker (the same decision as BLUEPRINT's new draft, `tasks.md:220`) | (b) exists in a script; one decision for two spaces | (a) a recipe with nothing to show in HOME; (b) a plot the user did not ask for |
| 5 | How a scaffold reaches BLUEPRINT and HOME | (a) a ZIP unzipped by hand; (b) BLUEPRINT accepts a recipe ZIP; (c) the scaffold writes into the user's own recipe place (the recipe places study, D-0393, D-0394); and whether the data files go into the ZIP | (c) no copy by hand | (b), (c) depend on the places study |
| 6 | Does the scaffold write a join (F7, K1) | (a) `joins: {}` (ADR-084); (b) a join marked "to check" with the rows with no partner shown; (c) as today | (a) follows the ADR and the BLUEPRINT boundary; (b) helps and informs | (c) changes rows silently |
| 7 | The key of a scaffold (F5) | the user picks from the columns found; one column, a pair, or a date (the earlier review's question 2); marked as entity key from that choice | follows D-0082, D-0216 | one more step for the user |
| 8 | ID cleaning steps (J3) | refuse a step that breaks a match; write it to act only on the ids that need it; warn (earlier review question 5); confirm each pair (the design) | - | - |
| 9 | Synthetic data for "testing from synthetic data" (J2) | seed and settings; dates and free text; the other four error kinds; several tables from one set of ids (as the demo script); from a recipe's declared fields (mine) | her first example | more to build |
| 10 | Anonymisation | several files on screen; the hash pattern salted or removed; where the mapping goes (ADR-097 point 8); the way back written in format 1 | - | - |
| 11 | One way per job (section 3.7) | which recipe writer stays (`SC`, `BS`, `recipe_factory`, the two scripts); which Excel path stays (`RF`, `EX`, `ExcelHandler`, HOME Data Import); which synthetic generator stays (`AQ`, the scripts) | one authoritative way (rule file) | removals touch tests and docs |
| 12 | Is a scaffold a production recipe for the name rule (F9) | yes (name_date); no (draft) | - | - |
| 13 | The words on the screen and in the help | the earlier review's question 9; the Info panel text placeholder | - | - |
