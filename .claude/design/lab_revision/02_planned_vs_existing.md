# TESTLAB-REVIEW-1, step 1b: what was planned against what exists

Written 2026-11-21 by a worker of TESTLAB-REVIEW-1 (D-0396). It builds nothing and decides nothing. Tree read: branch `task/lab-review` at `52c4bcfa` (no Test Lab file differs from `dev` at `555bb67f`, checked with `git diff --stat`).

**Summary.** The Test Lab has five tools on screen (ID reconciliation, recipe scaffolding, synthetic data, anonymisation, file reformatting) and one library tool with no screen (the Excel extractor). The libraries hold more than the screen offers: named synthetic scenarios, consistent anonymisation of several files, the de-anonymising join step, folder conversion and the bootstrapper's own recipe folder are all unreachable. Since the review of 2026-11-18, the recipe writers were rewritten for format 1 and their tests now run the checker; the scaffold passes the checker in profile `build` when the ids are text, but every scaffold is refused by the engine's own load (empty `analysis_groups`), the tables are still named after Shiny's upload numbers, and a numeric-looking id is still declared `Int64`. The ID cleaning steps still break ids that already matched, and a hyphen-to-underscore match gives a step that undoes nothing (both are known, recorded as strict xfail tests). The `test_lab` library imports `utils` without declaring it. The hand-off to BLUEPRINT is a ZIP that BLUEPRINT cannot open: its upload takes one `.yaml`.

**Labels.** "read" = I read the code now, file:line in this worktree. "document" = from a text, not re-checked. "run" = I ran it with one of the two probes below. "reasoned" = my reading of the code, not run.

**The runs** (scratch only, under `tmpAI/run/` of the worktree, git-ignored; the venv imports the main tree's libraries, whose Test Lab files equal this branch's):

```
cd .claude/worktrees/lab-review/tmpAI/run
PYTHONPATH=<worktree root> <main tree>/.venv/bin/python probe.py    # cases A to F
PYTHONPATH=<worktree root> <main tree>/.venv/bin/python probe2.py   # case G
```

Case A: two uploads as Shiny names them (`0.tsv`, `1.tsv`, user names `isolates.tsv`, `amr.tsv`), ids `007, 008, 009`, through `scaffold_from_uploads`, then `validate_data_analysis_recipe` in profiles `build` and `run`. Case B: one such upload. Case C and D: the ID reconciliation and its cleaning step. Case E: the synthesizer on a comma file. Case F: the anonymiser on a file with an empty id. Case G: one upload with text ids `S001`, `S002`, then the checker and the engine's own load. Nothing was started in a browser; every statement about the screen is read from the code.

**Short names.** `H` = `app/handlers/test_lab_handlers.py` (1007 lines), `S` = `app/modules/test_lab_studio.py`, `SC` = `libs/test_lab/src/test_lab/scaffolder.py`, `BS` = `bootstrapper.py`, `AQ` = `aqua_synthesizer.py`, `AN` = `anonymiser.py`, `RF` = `reformatter.py`, `EX` = `extractor.py`, `CORE` = `libs/id_reconciliation/src/id_reconciliation/core.py`, `RS` = `.../recipe_steps.py`, `IDP` = `libs/utils/src/utils/id_patterns.py`.

Sections: A mount, gate and the handler as a whole; B recipe scaffolding and the bootstrapper; C ID reconciliation; D synthetic data; E anonymisation; F file reformatting and the Excel extractor; G what the screen says; H library boundaries and the audit greps; I hand-offs by file; J the flags; K contradictions between sources; L the earlier review, point by point; M open choices, unranked.

---

## A. How the Test Lab is mounted and gated; the handler as a whole

| Fact | Evidence | Label |
|---|---|---|
| The nav item "Test Lab" exists only when `test_lab_enabled` is on; the theater shows `TestLabStudio.render_ui()`; the handlers are registered only with the flag | `home_theater.py:1835-1836`, `:1051-1054`; `server.py:122, 191-193` | read |
| The flag is on in `developer` and `qa` only; off in `pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`, `standalone`, `demo-vetinst`, `web-demo` | grep of `test_lab_enabled` in `config/app_features/*.yaml` | read |
| The theater is one accordion of five panels, all closed at start | `S:102-130` | read |
| Left sidebar: the alert log and an Info panel that says "Test Lab tools - instructions coming soon." | `config/ui/sidebars/testlab_standard_left.yaml`; `home_theater.py:1954-1966` | read |
| Right sidebar: five one-line tool descriptions | `testlab_standard_right.yaml`; `home_theater.py:2248-2301` | read |
| The handler holds 21 `except Exception` blocks; most turn an input that cannot be read into a quiet default (`sample_id`, threshold 0.7, `ref_id`, rate 0, `SUBJ_{:05d}`, `ANON`, first file) | `grep -c "except Exception" H` gives 21; e.g. `H:289-298, 421-424, 439-448, 632-637, 803-811` | read |
| One of them is now told to the user (the file that takes the cleaning steps); test `app/tests/test_click_reads_visible.py:100-110` | `H:451-460` | read |
| Each tool runs on a button and keeps its result until the button is pressed again; nothing resets a tool when its panel closes | `@reactive.event` on each `_*_result` (`H:132, 171, 404, 610, 787`) | read; the rule's "Closing a tool panel resets it" (`rules_test_lab.md:28`) is not what the code does (reasoned) |
| The handler takes a keyword `dev_studio` (the old name of ADR-068) and does not use it | `H:36`; `server.py:193` | read |
| An output `test_lab_workspace_ui` returns an empty div; no mount of it was found | `H:1004-1007`; grep finds it only there | read |

## B. Recipe scaffolding and the bootstrapper

### B1. Planned, existing, reachable, tested

| Item | Planned (source) | Library | On screen | Tested | Verify / update |
|---|---|---|---|---|---|
| A boilerplate recipe ZIP from data files | `TEST_LAB.md:33-42`; ADR-084 point 6; `rules_test_lab.md` section 4 | `SC.scaffold` writes a master, per table `<id>_input_fields.yaml` and `<id>_wrangling.yaml` (the tier 1 file), and with two or more tables one join file `assembly/<recipe>_joint.yaml` (`SC:100-146`) | yes: recipe id box, files, optional metadata file, "Join key column" box pre-filled `sample_id`, optional "Bake in ID Reconciliation steps", a status line, a ZIP download (`H:316-531`) | `test_scaffolder.py` (24) runs the checker in profile `build` on fixtures named `samples.tsv`, `amr_results.tsv` with text ids `cnr001` (`test_scaffolder.py:9-27, 245-270`) | the fixtures do not use Shiny's upload names nor a numeric-looking id, so cases A and B below pass the tests and fail in the app |
| The user selects the key columns after reconciling; the system checks key uniqueness; tier 1 holds `drop_duplicates`, `null_if`, `drop_nulls` on join keys | `TEST_LAB.md:38, 331-347` | not built: one free-text box; tier 1 is empty unless reconciliation steps are given (`SC:167-175`) | no | - | the design example (`TEST_LAB.md:430-448`) shows `polars_unique` and `polars_drop_nulls` in tier 1: they come from the steps given, not from a key check |
| The join written | ADR-084 point 6 and `rules_test_lab.md` table 4a: only `joins: {}` | the scaffolder writes an inner join of every table to the first on the typed key (`SC:122-138, 177-189`); the bootstrapper writes `joins: {}` (`BS:191`) | yes (scaffolder) | `test_scaffolder.py:262-270` checks the join | contradiction K1 |
| The table name | the user's file name (`TEST_LAB.md` example: `metadata`, `amr_results`) | `dataset_id = sanitize(Path(datapath).stem)` (`SC:84-86`); `scaffold_from_uploads` passes the `datapath` (`S:71-76`) | yes | not with upload names | **run (case A)**: the tables are `'0'` and `'1'`, labels `'0'`, `'1'`, files `0_input_fields.yaml`, `1_wrangling.yaml`, join ingredient `'1'`. The user's names appear nowhere |
| The data path | "user updates path before loading in BLUEPRINT" (`TEST_LAB.md:505`) | `source.path` = the upload path, relative to the working folder when inside it, else absolute (`BS:95-103`) | yes | tests chdir into the data folder (`test_scaffolder.py:247-249`) | in the app the upload folder is Shiny's temporary folder (document: the 2026-11-18 review read Shiny's source); an absolute path is refused by the checker: **run** `shape_problems('/tmp/abc/0.tsv')` gives "is an absolute path. Fix: write a path relative to the project root" |
| The entity key | the key the user names (`TEST_LAB.md:331-335`); "nothing is guessed from a column name" (`recipe_check.py:448-449`, E03 text) | `is_entity_key: true` on a column named `id`, `sample_id` or `isolate_id` (`SC:158-159`, `BS:81-82`), not on the typed key | yes | yes (the name rule) | contradiction K5 |
| The type of the key | D-0225: "The sample id is a string or a categorical, never a number" | types from the first 100 rows, Polars' reader (`SC:108`, `BS:41-60`) | yes | not with numeric-looking ids | **run (case A, B)**: ids `007...` give `Int64` and E03 in profiles `build` and `run` ("declared Int64, a number ... loses leading zeros") |
| The join key name | the field slug | the typed text as written (`SC:183`); fields are slugged (`SC:152`) | yes | no | read; the earlier review ran it (`Sample ID` gives field `sample_id` and `on: [Sample ID]`); not re-run |
| The join key is a column of every file | - | checked only for the ID cleaning steps (`S:65-69`) | - | `test_id_cleaning_steps_reach_a_recipe.py:218` (cleaning only) | read |
| The recipe id | D-0007: "recipe `id` = file name"; ADR-092 | written as typed, after `strip()`; no check of spaces, slashes or case (`H:408-413`; `SC:101, 198`) | yes, box says "snake_case" | no | reasoned: a name with `/` becomes a folder in the ZIP. D-0390 to D-0392 (name and date) concern production recipes; whether a scaffold is one is not decided |
| The candidate-key hint | `rules_test_lab.md` table 4a: "PK candidate hints as YAML comments" | a first comment line `# Candidate PK: ...` in the tier 1 file (`SC:167-175`) | yes | `test_bootstrapper.py:208-212` | **run (case A)**: on three rows every column is "100% unique" (`sample_id, year, country`): the hint is true and says little on a small file |
| ID cleaning steps written into tier 1 | `TEST_LAB.md:38`; `rules_test_lab.md` 4c | `scaffold_from_uploads` turns the transformation into recipe steps (`RS.recipe_steps`) for the file the user picks; refuses a file without the column (`S:52-70`) | yes, when a reconciliation ran in the same session (`H:366-401`) | `app/tests/test_id_cleaning_steps_reach_a_recipe.py` (16) | the steps may break ids (section C) |
| The bootstrapper's own recipe folder | `rules_test_lab.md` section 4; `libs/test_lab/README.md:14` | `BS.bootstrap` writes a folder (`BS:118-198`) | no: no handler calls `bootstrap()` (grep); the scaffolder uses its type guess and table block only (`SC:21, 38`) | `test_bootstrapper.py` (18), runs the checker (`:160-215`) | two writers of one recipe shape (`SC` and `BS`) plus `utils.recipe_factory` (the earlier review, section 2.10); to decide which stays |

### B2. Does what the writers write follow recipe format 1?

| Rule of format 1 | Scaffolder / bootstrapper | Evidence | Label |
|---|---|---|---|
| `id`, `spec_version: 1`, `data_engine`, `plot_engine`, `info` | written | `SC:197-208`; `BS:171-182`; run case A | read, run |
| Tiers as their own keys (D-0250): `tier1: !include` of a file that holds `steps`; no `wrangling:`, no `tier2` when empty | yes | `BS:106-116`, `SC:174, 189`; run case A (`steps: []`, the join file `steps:` with one `polars_join`) | read, run |
| No `output_fields`, no `final_contract` | none written | read; run | read, run |
| Prefixed action names (D-0036) | `polars_join` from `utils.action_names`; the cleaning steps `polars_str_replace_all`, `polars_with_columns`, `polars_cast`, `polars_str_strip_chars`, `polars_unique`, `polars_drop_nulls` | `SC:181`; `RS:41-82`; `action_names.py:23-31` | read |
| `'on'` quoted | yes (`'on':` in the written file) | run case A | run |
| `ui_label` (D-0253) | not applicable: no group and no plot is written. Tables, joins, fields and `info` keep `label`, as the spec says for now ("PENDING Eve", `recipe_spec.yaml:9-17`; spec DEC52) | read | read |
| `id` equals the file name (D-0007) | the master is `<id>/<id>.yaml` | `SC:146`; `BS:194` | read |
| Field types are Polars names; the key a String or Categorical | Polars names yes; the key may be `Int64` | run case A | run |
| `metadata_schema` at the top | legal (`recipe_spec.yaml:24, 80`) | read | read |
| Passes the checker | profile `build`: yes with text ids (run case G: no checker problem); no with numeric ids (E03, run cases A, B). Profile `run`: no (T09, no plot: expected for a scaffold) | run |
| Loads in the engine | **no, never**: "cannot load data analysis recipe: Data analysis recipe is missing the required 'analysis_groups:' block." (run case G, `engine_load_problems`; also returned by `validate_data_analysis_recipe(..., "build")` once the checker passes) | run |

So the writers follow format 1 as far as the checker reads it; the result is not a recipe the app can load, because the engine refuses an empty `analysis_groups`. The same fact is open for BLUEPRINT's new draft ("a fresh draft cannot be opened", `tasks.md:220`, a decision for the owner). `TEST_LAB.md:510` states it; `rules_test_lab.md:271` asks for the opposite (contradiction K8).

## C. ID reconciliation

| Item | Planned (source) | Library | On screen | Tested | Verify / update |
|---|---|---|---|---|---|
| Two files, one id column each; exact, then pattern, then fuzzy | `TEST_LAB.md:68-80`; ADR-084 point 5 | `CORE.reconcile`: exact, then the ONE best pattern applied to all unmatched ids, then rapidfuzz token-set with cutoff 70 (`CORE:70-114`; `matcher.py`) | yes: two files, two column lists, PRE-CHECK, Reconcile, status, many-to-many warning, the patterns applied, a threshold slider, the match table, a YAML download (`H:55-310`) | `libs/id_reconciliation/tests/` (56), `test_id_cleaning_steps_reach_a_recipe.py` (16) | - |
| 2 to 6 files; multi-file sequencing; a complexity warning | `TEST_LAB.md:72, 299-320` | not built (two ids lists only) | no | - | the design describes more than exists |
| Certainty per pair; less than 100% must be confirmed by the user, pair by pair; "No false positives allowed" | `TEST_LAB.md:151-162` | certainty 1.0, 0.95, the fuzzy score (`CORE:98-104`; `matcher.py:174-180`) | the table shows them; there is no confirm, reject, unverify or manual pick per row; a slider keeps every match above a threshold (`H:254-269, 299`) | - | the confirmation step, central in her description ("there is a manual step where people have to confirm or not", `TEST_LAB.md:85-91`, quoted there as hers, 2026-11-08), is not built |
| Chunked review, bulk accept, re-run of patterns after each round | `TEST_LAB.md:211-245` | `chunk_size` stored, not used by the screen (`CORE:65-68`) | no | - | not built |
| Recode workflow (trim, extract, regex, re-run) | `TEST_LAB.md:271-297` | `apply_recode_step` knows eight actions (`CORE:264-299`) | no recode form | yes | not on screen |
| The transformation file | a YAML with `metadata` (files, columns, date, who), `transformation_steps`, `match_summary`, `audit_log` (`TEST_LAB.md:164-209`) | `IdTransformation.to_yaml`: `ref_column`, `target_column`, `steps`, `metadata` (fuzzy map, many-to-many reason) (`data_structures.py`) | download "id_transformation.yaml" | round trip (`test_transformation.py`) | no file names, no date, no match counts, no audit log; `save_transformation`/`load_transformation` (`id_transformation.py`) are used only by a test (grep) |
| Reuse of a saved transformation | ADR-084: "User loads a saved recipe manually"; `TEST_LAB.md:870` | `from_yaml` exists | no upload of a transformation | - | not on screen |
| Many-to-many needs a written reason | `TEST_LAB.md:247-269` | `detect_many_to_many` (`CORE:243-250`) | warning: "A written reason is required before downloading" (`H:221-224`); the download adds the reason when there is one and downloads anyway (`H:302-310`) | - | the screen text is not true (read) |
| The cleaning steps act only where they matched | implied: "Generates reusable id transformation" that reproduces the matches (`TEST_LAB.md:101`) | the step applies to the whole column (`CORE:208-213`; `RS:50-53`) | via the scaffold | strict xfail `test_suggested_steps.py:105-112` | **run (case C)**: refs `ISOLATE_1, ISOLATE_2, sample_004, sample_005` against `ISOLATE_1, ISOLATE_2, 004, 005`: four matched; the step `^.{7}` gives `_1, _2, 004, 005`: two of four match; the two exact ids are broken, with no message |
| A hyphen-to-underscore match | - | the pattern swaps both ways (`IDP:47-57, 107-110`); the step is always `_` to `-` (`CORE:206-207`) | via the scaffold | strict xfail `test_suggested_steps.py:87-93` | **run (case D)**: refs `S-001..` matched `S_001..` by pattern; the step written gives `S-001..` again: 0 of 3 match |
| Fuzzy matches | listed for user confirmation | kept only as a text map in `metadata.fuzzy_recode_map` (`CORE:219-222`); `recipe_steps` writes no step for them (`RS:99-117`) | the scaffold status does not say they were left out (`H:501-506`) | - | read |
| Delimiter by file ending | - | `.tsv` is tab, everything else comma (`H:43-54`) | yes | no | read; a `.txt` with tabs gives one column |
| The pattern helper shared with BLUEPRINT | ADR-084 point 3; `rules_test_lab.md` 2c | `IDP` exists; its `@deps` says `consumed_by: ... join_designer.py` (`IDP:7-12`) | - | `test_pattern_detector.py` | `join_designer.py` imports nothing from `id_patterns` (grep): the `@deps` line is wrong and the sharing is not built |
| The shim `pattern_detector.py` | rule 2c calls it "a thin re-export shim" (`rules_test_lab.md:64`) | 11 lines that re-export `IDP` (`pattern_detector.py`) | - | - | task PATTERN-DETECTOR-SHIM-1 (open); the owner's development rule forbids shims (ADR-099 point 16(a)) |

## D. Synthetic data (AquaSynthesizer)

| Item | Planned (source) | Library | On screen | Tested | Verify / update |
|---|---|---|---|---|---|
| From a schema or from example data; the system proposes a config, the user adjusts per column | `TEST_LAB.md:62-64, 675-688` | `propose_config` from a TSV or a list of names (`AQ:49-75`) | a file or a comma list of names, rows 10 to 5000, mode; no per-column review (`H:537-639`) | `test_synthesizer.py` (21) | the config review step is not on screen |
| Types: id, date, numeric with a distribution, categorical with extendable values | `TEST_LAB.md:729-756` | id (by name), integer, float (uniform), boolean, categorical (up to 15 values), else string with placeholders `value_A/B/C` (`AQ:135-217`) | yes | yes | no date type, no normal distribution, no "extend with"; a text column with more than 15 values becomes `value_A/B/C` (read; the earlier review ran it) |
| The key column | a pattern per id column | a column is a key only if unique and named like one (`_is_pk_name`: `id`, `sample`, ends `_id`, `_key`, ...) (`AQ:20-28, 143-148`) | yes | yes | `isolate` is not a key (document, earlier review run) |
| Stress test: missing values, wrong type, duplicate ids, key mismatches, schema errors, malformed fields | `TEST_LAB.md:65, 689-698, 758-773` | all six in the library (`AQ:223-302`) | two sliders only: missing values and duplicate ids (`H:592-607`) | yes | the duplicate slider does nothing without a recognised key and says nothing (`AQ:259`; document, earlier review run) |
| Reproducible: a seed; the config saved with the data; named scenarios | `TEST_LAB.md:66, 700-704, 776-810`; `rules_test_lab.md` 3d, 9 (scenario round trip) | `generate(seed=...)`, `save_config`, `load_config`, `list_scenarios` (`AQ:77-129`) | no seed (`H:639`), no config in the download (TSV only, `H:667-675`), no scenario save or load | round trip tested in the library | a stress file cannot be produced again; her example use "testing from synthetic data" (`ORDER.md`) needs it reproducible (reasoned) |
| Delimiter | - | always tab (`AQ:136`) | file box accepts `.csv`, `.txt` (`H:541-546`) | no | **run (case E)**: a comma file gives one column `sample_id,year` |
| Only the first 100 rows read | - | `n_rows=100` (`AQ:136`) | not said | - | read |
| A second generator | - | `assets/scripts/generate_demo_data.py` writes the demo data set without `AquaSynthesizer` (read: no import of `test_lab`; ADR-068 says the script was moved to `test_lab.aqua_synthesizer`) | - | - | two mechanisms for synthetic data (reasoned) |
| A legacy CLI | `rules_asset_scripts.md` (argparse) | `main()` with other flags than the class (`AQ:364-458`), uses the module helpers kept "for backward compatibility" (`AQ:305`) | - | - | to verify whether anything still calls it |

## E. Anonymisation

| Item | Planned (source) | Library | On screen | Tested | Verify / update |
|---|---|---|---|---|---|
| Several files, the same original id gives the same new id everywhere | `TEST_LAB.md:50-54, 533-536`; right sidebar text "consistent synthetic equivalents" | `anonymise_batch` (`AN:144-226`) | one file only (`H:688-721`); `anonymise_batch` is not called (grep) | yes (library) | anonymising two files one after the other gives different new ids for the same sample with the sequential pattern (reasoned from `AN:267-283`; the earlier review states it) |
| Personal columns stripped into the mapping | `TEST_LAB.md:46, 587-589` | yes (`AN:295-334`) | yes, a tick list | yes | - |
| Patterns: sequential, hash, custom | `TEST_LAB.md:528-531` | sequential, unsalted SHA-256 first 8 characters, a format string (`AN:42-55`) | yes | yes | the hash is recomputable by anyone who can guess the ids, and two ids can share 8 characters with no message (reasoned) |
| A missing id | - | `mapping[None]` (`AN:302-303`) | the result has no `try` (`H:786-835`) | - | **run (case F)**: `KeyError None` |
| The key column name | `TEST_LAB.md:559`: "`sample_id` -> `ANON_0001`" in the same column | renamed `anon_<column>` and moved first (`AN:119, 307-309`) | not said (`H:847-850`) | yes | a recipe that reads `sample_id` will not find it (reasoned) |
| De-anonymise by a BLUEPRINT join, the steps printed in the output | `TEST_LAB.md:52, 569-573`; `developer_workflow.md:182` | `build_deanon_steps` writes the old action name `join` and a `_comment` key (`AN:228-246`) | not called (grep); the ZIP holds the anonymised table, the mapping and a config record (`H:813-835`) | - | not on screen; not format 1 (`join` is refused with the new name, D-0036) |
| The mapping is private | `TEST_LAB.md:519-526`; ADR-097 point 8 (key "kept outside" the app) | in the same ZIP as the anonymised table | "Download ZIP (anonymised + mapping + config)" (`H:716-718`); no warning | - | contradiction K10 |
| Delimiter by file ending | - | `AN:252-255` | - | - | as in C |

## F. File reformatting and the Excel extractor

| Item | Planned (source) | Library | On screen | Tested | Verify / update |
|---|---|---|---|---|---|
| XLSX to one TSV per sheet; CSV to TSV; folder | `TEST_LAB.md:25-31` | `convert_xlsx`, `convert_csv` (any delimiter, all as text: `infer_schema_length=0`), `convert_folder` (`RF:42-165`) | one file; a sheet tick list; a delimiter list defaulting to comma; a download (`H:879-1000`); no folder | `test_reformatter.py` (20) | the delimiter is not guessed; a tab file with "Comma" gives one column (document, earlier review run) |
| No sheet ticked | - | `None` means all sheets (`RF:70-76`) | `list(...) or None` (`H:979`) | - | read: unticking every sheet gives all sheets |
| Two sheet names that differ only by symbols | - | `_safe_stem` may give one file name (`RF:172-175`) | - | - | reasoned: the second overwrites the first |
| What was made | - | - | status shows the file name or the sheet names, no rows or columns (`H:950-965`) | - | read |
| Excel cell types | - | `pl.read_excel` keeps Excel's types (`RF:68`) | - | - | not run: a numeric id typed as a number in Excel may lose leading zeros (reasoned) |
| The Excel extractor (sheet, key renamed `id`) | `docs/workflows/test_lab_sdk.qmd` "Stage A"; `libs/test_lab/README.md:15` | `XlsxExtractor.extract` (`EX:12-73`); prints a warning and skips a sheet without its key (`EX:48-65`) | no screen (grep: only its test imports it) | `test_extractor.py` (6) | `TEST_LAB.md:3-6` counts it as wired: not true; renaming the key to `id` contradicts naming a column by its meaning (reasoned) |
| Two sheet converters | - | `RF.convert_xlsx`, `EX.extract`, and `ExcelHandler` in `libs/ingestion` (named in `TEST_LAB.md:952` and `README.md:15`) | - | - | three code paths for one job (reasoned; `ExcelHandler` not read) |

## G. What the screen and the help say

| Text | Where | Fact |
|---|---|---|
| "Test Lab tools - instructions coming soon." | Info panel, `home_theater.py:1963` | a placeholder; the comment says it waits for "Test-Lab-specific instructions once that's decided" (owner's choice of 2026-11-08 as reported in the comment) |
| "Match and align ID columns across related files before assembling a pipeline." | right sidebar, `home_theater.py:2261-2262` | two files only |
| "Generate boilerplate pipeline data analysis recipe from uploaded files." | `:2270` | it also writes a join |
| "Generate demo or stress-test datasets from a schema or example file." | `:2278-2279` | two of six error kinds on screen |
| "Replace real IDs with consistent synthetic equivalents. Reversible via BLUEPRINT join." | `:2287-2288` | consistent inside one file; the join step is not given |
| "A written reason is required before downloading the id transformation." | `H:223` | not enforced |
| "Scaffolded ... Download the ZIP and open in BLUEPRINT to continue." | `H:509-510` | BLUEPRINT cannot open the ZIP (section I) |
| `app/src/help/test_lab.md` | lines 6, 9, 12 | "save the result as a named ID transformation"; "empty wrangling/plot stubs"; "including named error scenarios": none is on the screen as written |
| `AN:31`, `RF:20` `@deps` | - | "TL-UI-ANON-1 - not yet built", "TL-UI-REFORMAT-1 - not yet built": both are built |

## H. Library boundaries (`rules_test_lab.md`) and the audit greps of section 10

The six greps of section 10, run now from the worktree root (run):

| # | Command (as in the rule) | Result |
|---|---|---|
| 1 | `grep -rn "from shiny\|import shiny" libs/test_lab/ libs/id_reconciliation/ --include="*.py"` | no output: pass |
| 2 | `grep -rn "from transformer\|from blueprint_arch\|from viz_factory\|from ingestion\|from connector" libs/id_reconciliation/src/ --include="*.py"` | no output: pass |
| 3 | `grep -rn "ConfigManager" libs/test_lab/src/ --include="*.py"` | one hit, a docstring: `reformatter.py:7: Shiny-free. No ConfigManager.` The rule says "All commands must return zero output", so the check fails on a comment that states compliance |
| 4 | `grep -rL "NOT a pipeline data analysis recipe" libs/test_lab/scenarios/` | one hit: `libs/test_lab/scenarios/.gitkeep` (the folder holds no scenario). Fails on the placeholder file |
| 5 | `grep -rn "app features.*developer\|app features.*qa" app/handlers/test_lab_handlers.py` | no output: pass |
| 6 | `grep -rn "sys\.path" libs/test_lab/tests/ libs/id_reconciliation/tests/` | no output: pass |

So the code respects the boundaries the greps test; two greps are written so that they fail on harmless files (to update in the rule).

Further boundary checks (read):

| Rule | Fact | Evidence |
|---|---|---|
| A library that imports `libs/utils` MUST declare `"utils"` in its `pyproject.toml` (`rules_runtime_environment.md` section 4) | `test_lab` imports `utils` (`BS:13`, `SC:18-19`) and declares only polars, numpy, openpyxl, pyyaml (`libs/test_lab/pyproject.toml`). `id_reconciliation` declares `utils` (correct) | read |
| `test_lab` must not import transformer, viz_factory, blueprint_arch, connector | none | grep |
| `id_reconciliation` imports only stdlib, polars, utils, rapidfuzz | yes (`utils.formula_check`, `utils.id_patterns`, `utils.action_names`) | grep |
| The Two-Category Law: no `shiny.reactive` and no `@render` in `test_lab_studio.py` | `S` imports `shiny.ui` only and has no decorator | read |
| Every library is installed by `scripts/install_libs.sh` | `id_reconciliation` is missing from its list (`install_libs.sh:23-32`); the root `pyproject.toml` lists its `src` for pytest (line 38) | read |
| The container installs the libraries | `assets/containers/Dockerfile` names neither `test_lab` nor `id_reconciliation` (task DOCKER-RELEASE-1, issue #90) | read (grep) |
| The pattern helper is shared with BLUEPRINT (ADR-084 point 3) | not used by `join_designer.py` | grep |

## I. Hand-offs by file to BLUEPRINT and HOME

| Hand-off | Planned | What exists | Label |
|---|---|---|---|
| Scaffold ZIP to BLUEPRINT | "Export the boilerplate ZIP; open it in BLUEPRINT like any data analysis recipe" (`docs/workflows/developer_workflow.qmd:87`; `developer_workflow.md:180`) | BLUEPRINT's upload accepts one `.yaml` and puts its steps on the step stack (`wrangle_studio.py:225-226`; `blueprint_handlers.py:1117-1150`); BLUEPRINT lists recipes from the fixed folder `config/data_analysis_recipes/pipelines` (`blueprint_handlers.py:975`, from the BLUEPRINT review). A ZIP with `!include` files can reach BLUEPRINT only by unzipping it into that folder on the server by hand; then the engine refuses it until a plot exists (section B2) | read, run |
| Scaffold ZIP to HOME | HOME runs recipes of the deployment's recipe location | no upload of a recipe ZIP in HOME (the two `.zip` inputs are a session and a reproducibility bundle: `session_handlers.py:158`, `export_handlers.py:698`); the recipe would be refused by the load gate (no plot) | read (accept lists); reasoned for the gate |
| The data files the recipe names | the user edits the path (`TEST_LAB.md:505`) | the recipe names the temporary upload path; the data are not in the ZIP | read |
| Anonymised files and the mapping to BLUEPRINT | a join step printed by the tool | not printed; the old step name `join` (section E) | read |
| Synthetic TSV to HOME or BLUEPRINT | "Test a data analysis recipe you are building: Synthesise data" (`developer_workflow.md:115`) | a TSV download; no link to a recipe's `input_fields`; no seed; no config | read |
| ID transformation to the scaffold | in-space carry-over (`developer_workflow.md:136-141`) | built (the "Bake in" tick) | read |
| Reformatted TSVs to the Data Import panel of HOME | - | HOME's Data Import panel has its own Excel path (`ui_implementation_contract.md` section 10, "Deferred") | document |
| Dropped by the owner (2026-05-22) | "Send to scaffolding" button; "Open in BLUEPRINT" button | not built, on purpose (archive lines 147-160) | read |

## J. The flags

| Flag | Effect | Where |
|---|---|---|
| `test_lab_enabled` | the nav item, the theater, the handlers, the right sidebar panel | `home_theater.py:1835`; `server.py:122, 191`; `sidebar_registry.py:91-101` |
| none | the left sidebar Info panel (`test_lab_info`, gate `None`) | `sidebar_registry.py:27-29` |
| `blueprint_enabled` | not read by the Test Lab: the scaffold status tells the user to "open in BLUEPRINT" whatever the flag | `H:509-510` (read) |
| the deployment's recipe and data locations | not read by the Test Lab | grep of `get_location` in `H`, `S`: none |

Today the Test Lab is on only in `developer` and `qa`. The owner's description "a set of utilities for the user to help user" (`ORDER.md`) does not say for which app features: to decide (section M).

## K. Contradictions between sources (listed, not resolved)

- **K1 The join in the scaffold.** ADR-084 point 6, `rules_test_lab.md` table 4a (`:138`) and `TEST_LAB.md:874` ("Boilerplate scope: Structure + inferred types + PK hints + ID cleaning id transformations only"): an empty `joins: {}`. `TEST_LAB.md:342-346` and its example (`:490-501`) and the code (`SC:122-138`): a join pre-filled with the key.
- **K2 What the Test Lab writes into tier 1.** `docs/appendix/test_lab_rationale.qmd` ("Test Lab never authors `tier1`/`tier2` wrangling logic") against the scaffold (cleaning steps and the join in `tier1`).
- **K3 Six tools wired.** `TEST_LAB.md:3-6` against the code (the extractor has no screen).
- **K4 Known bugs.** `rules_test_lab.md:145-151` and `libs/test_lab/README.md:14` (three bugs, "do not add features") against `BS:179-192` (fixed). Proposal R085 of 2026-11-14 is not applied.
- **K5 The entity key.** `TEST_LAB.md:331-335` (the user names the key) and the checker's E03 text ("nothing is guessed from a column name") against `SC:158-159` (marked by name). The rule proposal R081 would write the name rule into the rule.
- **K6 Pattern sharing.** ADR-084 point 3 (`id_patterns` used by `join_designer.py`) against ADR-082 line 3913 ("each space keeps its own implementation until a clear duplication emerges") and the code (no import).
- **K7 The shim.** `rules_test_lab.md:64, 226` (a "thin re-export shim", described as the design) against ADR-099 point 16(a) and task PATTERN-DETECTOR-SHIM-1 (no shims).
- **K8 The boilerplate gate.** `rules_test_lab.md:271` ("MUST pass `ConfigManager.load()`") against `TEST_LAB.md:510` and the run (the load refuses an empty `analysis_groups`).
- **K9 Injected actions.** `rules_test_lab.md:155` (four actions) against `RS:85-96` (eight step kinds, six recipe actions).
- **K10 Where anonymisation and the key live.** ADR-097 point 8 ("anonymisation before data ever reaches the app, with any de-anonymisation key kept outside it entirely") against the Test Lab anonymiser in the app and the mapping in the same download; and `TEST_LAB.md:46-52` ("reversible") against `test_lab_rationale.qmd` ("not reversed by a reader who only has the anonymised file", which is about a reader, not the tool).
- **K11 Scenario loader name.** `rules_test_lab.md:106, 118` (`load_scenario()`) and the mandatory header text against `AQ:46, 116` (`load_config()`).
- **K12 Panel reset.** `rules_test_lab.md:28` ("Closing a tool panel resets it to empty state") against the code (results kept until the button is pressed again).
- **K13 One task, two states.** `tasks.md:347` (TESTLAB-REVIEW-1 open, "Not started") against `tasks.md:677` (TESTLAB-REVIEW-1 "`[done: report]`"). Under rule H of `decision_compliance.md` this is reported, not resolved.
- **K14 Which ADR made `libs/test_lab`.** `docs/workflows/test_lab_sdk.qmd:3` (ADR-084) against ADR-068.
- **K15 Install.** `rules_toolchain.md` ("Install every `libs/*` package") against `scripts/install_libs.sh` (no `id_reconciliation`).
- **K16 Library imports.** `libs/test_lab/README.md:52` ("No cross-lib imports") and `rules_runtime_environment.md` section 4 (declare `utils`) against the code (imports `utils`, not declared).
- **K17 The transformation file.** `TEST_LAB.md:164-209` (files, date, who, counts, audit log) against `IdTransformation.to_yaml` (columns, steps, metadata).
- **K18 Who the Test Lab is for.** `TEST_LAB.md:16-19` (data stewards, developers, recipe authors) and her words in `ORDER.md` ("utilities for the user") against the flag matrix and `app/src/help/test_lab.md:21` ("not visible to scientist-facing app features files"). A difference to put before her, not a defect.

## L. The review of 2026-11-18, point by point (what still holds)

| Its point | Today | Evidence |
|---|---|---|
| 2.1 the scaffold fails the checker with F01, J07, S03, J02 | fixed: run case G passes the checker in profile `build`; the tests run the checker (`test_scaffolder.py:245-270`, `test_bootstrapper.py:160-215`) | run, read |
| 2.1 tables named "0", "1"; temporary path; `Int64` key | still true | run cases A, B |
| 2.1 the data check cannot load it (empty `analysis_groups`) | still true | run case G |
| 2.2 silent `sample_id` default; typed key not slugged; no check of the key in every file; entity key by name | still true | read `H:421-424`, `SC:158-159, 183` |
| 2.3 delimiter by file ending or fixed tab | still true | read; run case E |
| 2.4 synthetic placeholders, no seed, no scenario on screen, duplicate slider silent | still true | read |
| 2.5 anonymiser crash on a missing id; one file only; unsalted hash; mapping in the ZIP | still true | run case F; read |
| 2.6 the cleaning step breaks exact matches; fuzzy matches dropped; the reason not enforced | still true, now recorded as strict xfail tests (ID-RECON-STEPS-1) | run case C; read |
| (new) the hyphen-to-underscore step | recorded as strict xfail; confirmed | run case D |
| 2.7 reformatting: no sheet means all; name clash; no counts; stale "not yet built" | still true | read |
| 2.8 the panels and help | still true | read (section G) |
| 2.10 the writers must be rewritten for the new shape | done in step 4c of the big recipe change (read: the code writes D-0250 tiers; the handoff line 165 names step 4c) | read, document |
| 2.11 the recipe id not checked; 21 `except Exception` | still true | read |

## M. Open choices, unranked ("to decide"; ranking belongs to the guide)

Each is open; options are those the sources name. Nothing is recommended here.

1. **What the Test Lab is for and for whom** (her words: "a set of utilities for the user to help user eg. testing from synthetic data, preparing data files in the correct format"): which tools stay, which app features show it (today developer and qa only).
2. **Does the scaffold write a join?** An empty stub (ADR-084), a join marked "to check" with the rows that have a partner, or as today (the earlier review's question 3).
3. **How a scaffold becomes a recipe the app can open**: the loader accepts an empty `analysis_groups` for a draft, or the scaffold writes a first plot, or a draft profile (the same question as BLUEPRINT's new draft, `tasks.md:220`).
4. **How the scaffold reaches BLUEPRINT and HOME**: a ZIP the user unzips into the recipe folder, BLUEPRINT accepts a recipe ZIP, or the scaffold writes into the user's own place (the BLUEPRINT review's recipe places study, D-0393, D-0394 are related); and whether the data files go into the ZIP (the earlier review's question 1).
5. **The key of the scaffold**: a choice from the columns found, one column or a pair or a date (earlier review question 2); the entity key marked from the user's choice, not by name.
6. **How an ID cleaning step is written**: refuse a step that breaks an exact match, write it to act only on ids that need it, or warn (earlier review question 5); and what happens to fuzzy matches.
7. **The confirm-each-match step** of the ID reconciliation (in the design, not built) and the reuse of a saved transformation.
8. **Synthetic data**: dates and free text, a seed, the config in the download, named scenarios on screen, the other four error kinds (earlier review question 4); its link to a recipe (her example "testing from synthetic data").
9. **Anonymisation**: several files on screen, the hash pattern (salt or remove; earlier review question 6), where the mapping goes (ADR-097 point 8), the de-anonymising step in format 1.
10. **Delimiters and Excel**: guess and show, or ask; one sheet converter or several (`RF`, `EX`, `ExcelHandler`); the extractor wired or removed (earlier review question 7).
11. **Two or three recipe writers** (`SC`, `BS`, `utils.recipe_factory`): which one writes recipes.
12. **The three ideas of the task** (extract a pilot recipe, a tool-specific recipe, combine recipes): wanted or not, and their size.
13. **The words**: the Info panel text, the right sidebar, the help, the docs (earlier review question 9).
14. **The rule file and the ADR**: apply the proposals R077 to R086 of 2026-11-14, correct ADR-084 to format 1 words, the audit greps that fail on harmless files.

## Not verified

- Nothing was seen in a browser: the reachability statements are read from the handlers and the UI code.
- The test suites were not run; counts are `def test` counts. The three xfail tests were read, not run.
- An XLSX was not converted; a CSV was not scaffolded (the synthesizer case shows the same pattern).
- The scaffold through a real Shiny upload (the upload names were reproduced by hand, as the earlier review did).
- How BLUEPRINT shows a scaffold placed into its recipe folder.
- `ExcelHandler` in `libs/ingestion`, the legacy CLI of `AQ`, the UML pictures.
- Whether anything outside the repository calls `bootstrap()` or the extractor.
