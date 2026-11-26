# Recipe name rule `name_date`: can the demo recipes be an exception? (2026-11-21)

Labels: RUN = I ran it. READ = I read the code (file:line). REASONED = my conclusion, not run.

## Answer in three lines
1. Yes, an exception is possible, and it needs no recipe name in the code. Today the app reads any file name (RUN: three recipes with a date name, a plain name and a name with no hyphen all load, build, plot and export the same).
2. The simplest way: enforce the rule only where the app WRITES a recipe, not where it reads one. All writers already pass through one function or are small (see table 2), so shipped and demo recipes need no rename.
3. If the rule were also enforced at READ, the 7 shipped recipes (and the 4 retest, 5 template, 17+ test recipes) would be refused, and a rename costs about 515 references for the 7 pipelines alone, plus all saved sessions and stored tables (their keys change). That is the "hell" case. I would not do it.

## 1. Today's names (READ + RUN)
Regex used: `^.+_YYYY-MM-DD$` on the file name without `.yaml`. Result: NONE of the 17 top-level recipe files follows `name_date`. Also none of the Gallery, template or test files.

| Group | Files | Name today | `id:` equals name? |
|---|---|---|---|
| `config/data_analysis_recipes/pipelines/` (what the local deployment lists) | 7 | `1_test_data_ST22_dummy`, `2_test_data_ST22_dummy`, `3_test_no_joins`, `1_Abromics_general_pipeline`, `demo_abromics`, `figshare_integration`, `stress_test_master` | yes (ADR-092) |
| `.../retest/` (retest deployment) | 4 | `retest_bad_select_column`, `retest_broken_header`, `retest_tier2`, `retest_top_n_other` | yes |
| `.../templates/` | 5 | `audit`, `complex_template`, `e_coli`, `left_join_lesson`, `simple_template` | yes |
| `.../experimental/` | 1 | `test_logic` | no `id:` found by my grep (not checked further) |
| Gallery `assets/gallery_data/*/data_analysis_recipe.yaml` | 34 | fixed file name; id = folder name (check GP04, `libs/utils/src/utils/recipe_check.py:1256`) | by folder |
| Test fixtures | 68 in `libs/transformer/tests/data/<action>_data_analysis_recipe.yaml`, 4 in `app/tests/equality/recipes/`, 194 YAML files in `libs/viz_factory/tests/test_data/` (not all are recipes) | 1:1:1 naming law of the tests | not checked |

What is a "demo" recipe?
- D-0373 (her words in the ledger): the demo recipe, "including the group tab labelled QA canaries", is not changed by agents; she reviews the demo recipes after her manual test. The only recipe named is the demo recipe `1_test_data_ST22_dummy` (READ: `config/deployment/demo/demo-vetinst.yaml:7`, `web-demo.yaml:7`, `pipeline_test.yaml:22` use it as default).
- D-0392 literally: "The rule covers real production recipes. The demo recipes stay as they are (D-0373 holds), unless leaving them breaks something; then it is reported to her and she is asked." Her words: "my demo can stay as such ... unless you want to change them - this might be needed to change them to avoid errors --- but ok its only name changes ... easy to automate."
- D-0392 does not say which recipes count as "demo". I read it as: the shipped recipes (`1_`, `2_`, `3_`, Abromics, figshare, stress) are demo or test recipes. REASONED. The owner should confirm the list. The 5 templates, the retest recipes and the Gallery examples are not named by any decision.

## 2. Where the app writes a recipe (READ, file:line)

| Writer | What name it gives | Check today | Enforce `name_date` here |
|---|---|---|---|
| BLUEPRINT "new recipe" `app/handlers/blueprint_handlers.py:2635-2702` | the user's slug, `<slug>.yaml`, in a hard-coded `config/data_analysis_recipes/pipelines` (not the deployment folder) | regex `^[a-zA-Z_][a-zA-Z0-9_]*$` (line 2635): a HYPHEN and a leading DIGIT are refused today; refuses an existing name; writes through `write_recipe` | small: change the one regex and add a date check. Note: today `name_2026-11-17` cannot even be typed here |
| BLUEPRINT save of a component `blueprint_handlers.py:1188` | the file already open (same name) | none; overwrites in place | not a new name; not a place for the rule. This is the "typo edit" of D-0393 |
| BLUEPRINT info save `blueprint_handlers.py:2621` | the open recipe, in place | none | same: in place |
| BLUEPRINT branch `blueprint_handlers.py:1515-1517` | new fragment files + the master in place | refuses an existing fragment | no recipe name made |
| "Save as" | does not exist (no match for `save_as` in the app) | n/a | n/a |
| Upload `app/handlers/ingestion_handlers.py:44-51` | `shutil.copy(path, dir / name)`: the user's file name, any name | none. It REPLACES silently (READ, `shutil.copy` overwrites). D-0390's reading is right | small check at line 50 |
| | | **Finding (READ + grep):** no widget in the app has the id `btn_ingest` or `file_ingest` (grep over `app/`, `libs/`, `config/`: only the handler and a CSS line). The handler is registered (`app/src/server.py:276`) but nothing in the UI can trigger it. So today the upload of a recipe is not reachable by a user. I did not run it headless: reading is enough | |
| Bundle import `app/modules/bundle_importer.py:253-275` | `<original id>_imported_YYYYMMDDTHHMMSS` (+ `_2` counter), id rewritten to match | refuses nothing by name; builds a unique name | small: this is not `name_date`. It writes with `yaml.safe_dump`, NOT through `write_recipe`. D-0435 already says the user chooses the name, prefilled |
| Test Lab scaffolder `libs/test_lab/src/test_lab/scaffolder.py:145-165` | a zip returned as a download (`tl_scaffold_download`, `app/handlers/test_lab_handlers.py:516`) | no write into the recipes folder (READ) | the name is in the zip; a check could be advice only |
| Test Lab bootstrapper `libs/test_lab/src/test_lab/bootstrapper.py:195` | `<out_dir>/<id>.yaml`, caller gives both | none | no app caller found outside the scaffolder's zip; only tests |
| Generators `assets/scripts/create_data_analysis_recipe.py:223`, `SF_create_data_analysis_recipe.py:63` | name from `--out_file` | `write_recipe` (id must equal file name) | small: one call |
| `libs/blueprint_arch/src/blueprint_arch/new_recipe.py` | a draft dictionary, no file | n/a | n/a |
| Gallery submission (`app/modules/exporter.py`) | the file no longer exists; no `SubmissionExporter` in any `.py` | n/a | n/a (the rules file `rules_app_structure.md` still lists it: a doc mismatch) |

ONE function: YES, partly. `write_recipe` in `libs/utils/src/utils/recipe_factory.py:195-200` already refuses "id is not the file name". It is called by BLUEPRINT new recipe and both generator scripts. NOT called by the bundle import, the upload and the other in-place saves. Read side: the same id-equals-name check exists twice (`libs/utils/src/utils/recipe_check.py:244-245` code T05; `app/modules/data_analysis_recipe_validator.py:436-442`). There is no function that checks the SHAPE of a name (characters, date). REASONED: one new small function `recipe_name_problem(stem)` in `libs/utils` could be called by `write_recipe`, the upload and the bundle import.

## 3. Where the app only reads (READ)
- Discovery: `app/src/bootloader.py:404-422` = `glob("*.yaml")` in the deployment's recipes folder, id = file stem (no name check). Load gate `_gate_one` (line 431 on) runs the structure check and the data check; the structure check includes id equals file name.
- Gallery: separate path, fixed file name, id = folder (GP04).
- `default_data_analysis_recipe` of 3 deployments names `1_test_data_ST22_dummy` (`demo-vetinst.yaml:7`, `web-demo.yaml:7`, `pipeline_test.yaml:22`).

If the rule were enforced at READ, refused: all 7 pipelines, the 4 retest, the 5 templates, and the deployments that name `1_test_data_ST22_dummy` would find nothing.

### Cost of renaming all (RUN: `grep -rc`; counts are lines that contain the id)
| Recipe | app | libs | assets | config | docs | rules | knowledge | total |
|---|---|---|---|---|---|---|---|---|
| 1_test_data_ST22_dummy | 101 | 9 | 16 | 98 | 13 | 2 | 17 | 256 |
| 2_test_data_ST22_dummy | 97 | 1 | 4 | 22 | 4 | 5 | 12 | 145 |
| figshare_integration | 21 | 0 | 0 | 13 | 4 | 0 | 2 | 40 |
| 1_Abromics_general_pipeline | 13 | 0 | 0 | 1 | 9 | 0 | 1 | 24 |
| demo_abromics | 20 | 0 | 0 | 1 | 1 | 0 | 1 | 23 |
| 3_test_no_joins | 13 | 0 | 0 | 1 | 0 | 0 | 1 | 15 |
| stress_test_master | 8 | 0 | 0 | 4 | 0 | 0 | 0 | 12 |
| **7 pipelines** | | | | | | | | **515** |

Retest, 4 recipes: 52 lines in `app`, 18 in `assets`. Templates, 4 of 5 counted: 62 in `app`, 18 in `assets`. `1_test_data_ST22_dummy` is in 69 files (37 in `app/tests`, 3 golden, 2 equality, 4 in `libs/blueprint_arch/tests`, 2 in `libs/transformer/tests`, 1 in `libs/utils/tests`, 4 scripts, 3 deployment files).

Other things tied to the name (READ unless marked):
- Folder beside each recipe (basename mirroring): `pipelines/1_test_data_ST22_dummy/`, `2_...`, `figshare_integration/`, `stress_test_master/`: all `!include` paths inside the recipe change.
- Cross-use: `3_test_no_joins.yaml` includes fragments from the `1_test_data_ST22_dummy/` folder and reads its data (READ, lines 16-27). Renaming `1_` breaks `3_` too.
- Test data folders named after recipes: `assets/test_data/1_test_data_ST22_dummy`, `duplicated_1_test_data_ST22_dummy`, `config/references/amr_phenotypes` mentions it. The recipe's `source.path` holds the folder name.
- **Saved sessions and stored tables change (RUN).** The recipe hash is made from `relative_path:sha256` lines of the entry file and its included files (READ `app/modules/cache_keys.py:332-336`; `session_manager.py:281-287`). My three copies have identical content apart from the name; their hash differs (`8486002035db`, `c094ff85d1a1`, `256a3a3b5f06`), so the session key differs and the recipe part `rC-...` of the table key differs; the data part `dC-...` is the same. A rename therefore means: old sessions do not match, stored tables are rebuilt, old exports show another hash. Nothing is wrong silently (the old session is "another recipe"), but the owner's saved work would not reopen.
- Exports: the bundle records recipe id and path (RUN: README line "Data analysis recipe: no_joins_2026-11-17"). Old bundles keep their old id; import adds `_imported_...`.

## 4. Hyphen and date through the whole app (RUN)
Setup (scratch only, `tmpAI/coordinator/recipe_name_rule/`): copy of `3_test_no_joins` with its fragments and data, in three names, own deployment (`deploy.yaml`), `qa` app features: `no_joins_2026-11-17` (the `name_date` form), `no_joins_plain` (no date), `no_joins_20261117` (date without hyphen). Each has `id:` equal to the name. Load average was 2.8 to 3.5 before each run.

| Step | `no_joins_2026-11-17` | `no_joins_plain` | `no_joins_20261117` |
|---|---|---|---|
| Bootloader discovery and load gate (`available_data_analysis_recipes`, rejected list) | listed, not rejected | same | same |
| `validate_data_analysis_recipe` | no problem | same | same |
| data check | no problem | same | same |
| Build tables + one plot (`materialize_tier3`, `VizFactory.render`) | 42 rows, PNG written | same | same |
| PNG | md5 `c41aa0a8...` | identical | identical |
| Cache keys, session key | made (`8486002035db:61d2df800b9a`) | made | made |
| Session record written and read back | ok | ok | not run (same code) |
| App on port 8751 (Playwright): listed in selector, opens, tab "No Joins", sub-tab, 1 plot image, no browser console error | ok | ok | ok |
| Export bundle download from the app | ok: 7 files, README names the recipe | not run | not run |

Failures found: NONE for the hyphen or the date. Reason (READ): the recipe id is used in file names (`f"{recipe_id}.yaml"`, `opening_handlers.py:100`, `home_theater.py:372`), in a session tab label (`session_handlers.py:383`), and not in any HTML id: the ids I saw are built from the plot id only (`plot_cell_sequence_type_counts`, ...). `_safe_id` (`home_theater.py:95`) is used for group ids, not recipe ids. Not covered: Shiny ids built from recipe ids in BLUEPRINT and TEST_LAB, the audit copy, bundle import of a hyphen name, BLUEPRINT with a hyphen recipe (BLUEPRINT's new-recipe regex refuses a hyphen, line 2635, but opening one is not that code).
The three behave the same today (RUN): no rule exists.

## 5. The exact form of the rule: questions the code must answer (not decided)
1. "name": which characters? Lower case only? Digits allowed? A leading digit (the shipped `1_test...` has one; BLUEPRINT's regex refuses it today)? Underscores inside the name?
2. Is the date always the part after the LAST underscore? A hyphen in the date is then no problem for splitting. A name like `a_b_2026-11-17` works; a name with its own date inside is ambiguous.
3. Must the date be a real calendar date (`2026-02-30` refused)? Or only the shape `YYYY-MM-DD`?
4. Time: D-0391 leaves open whether a time is ever part of it. The bundle import today uses `YYYYMMDDTHHMMSS`.
5. Sorting: D-0391 wants "sort from most recent to oldest by name". With the date at the END, sorting by name groups by name first, so the newest is first only within one name, and the selector must sort descending to show it. Is that what she means? Also not verified: how the HOME selector orders recipes today (the dictionary comes from `glob`, no sort at `bootloader.py:422`).
6. `id:` equal to the name: already a rule (T05).
7. Gallery example: the file name is fixed (`data_analysis_recipe.yaml`) and the id is the folder name; a template is a model, not a recipe the user opens. Are they inside the rule? No decision says.
8. Same name already exists: upload refused (D-0390); BLUEPRINT new recipe already refuses; bundle import: D-0435 says refuse; typo edit in the user's own place may replace (D-0393 point 2).

## 6. What a recipe that does not follow the convention gets at load (options)
| Option | User sees | Owner's demo | Hard-coded name in code? | Cost |
|---|---|---|---|---|
| A. Nothing at load; rule enforced at write only | nothing | untouched | no | smallest. A hand-copied file with a bad name still works |
| B. Advice in BLUEPRINT's Validate only | an advice line when she validates | untouched | no | small: the validator already has "advices" (`bootloader.py:429-430`) |
| C. Advice in HOME's Info panel | a plain line under the recipe info | shows a note on every demo recipe unless exempt | no | small; noisy for demo unless the exemption exists |
| D. Refusal at the load gate + exception list | recipe listed as rejected with reason | needs the exemption | the list must live somewhere | largest; breaks every shipped recipe on day one |

Where could an exception be stated without a recipe name in code (same spirit as "no app-features name comparison")?
- By folder: the recipes folder of a deployment is either "shipped" or "user". Rule applies only to the user's own place (D-0393 point 4 and D-0394 already want a user place apart from the common one). The code compares no name, only "this folder is the user's writable place". REASONED.
- By a flag in the deployment file (for example a key that says the rule applies to this recipes folder). The demo deployments set it off. Matches D-0425 (the deployment file decides what may be read and written).
- By a key in the recipe `info` (for example "demo: true"): the recipe says it is exempt. Weakest: any recipe could claim it, and it changes the recipe file, which changes its hash (D-0373 says demo is not changed).

Suggestion: option A for the first build, enforced in ONE function in `libs/utils` called by every writer (BLUEPRINT new recipe, upload, bundle import, generator scripts), applied to the user's writable place only (the deployment says which folder that is). Add option B later (advice in Validate, no refusal) so a hand-copied bad name is visible. No exception list is then needed: the shipped recipes live in the common read-only place and are never written. This keeps D-0392 ("demo stay as they are") true without a name in the code, and avoids the 515-reference rename and the session and stored-table break.

## Not verified
- I did not run the recipe upload headless: no UI sends it (grep), so reading is the evidence.
- Not run: BLUEPRINT and TEST_LAB with a hyphen recipe open; bundle import of a hyphen recipe; the audit copy; the `retest` and Gallery paths; the full export content check; `experimental/test_logic.yaml` id.
- The counts are lines per file by `grep -rc`, including docs and comments; the real edit count may be lower or higher. `docs/` for the retest and templates, and `.claude/knowledge` for them, were not counted.
- Regex of "demo recipe": which recipes the owner calls demo is not stated by a decision beyond `1_test_data_ST22_dummy`.
- How HOME's selector sorts today.
- The 194 viz_factory test YAML files were counted, not each checked to be a recipe.
- No test suite was run; scratch files are only in `tmpAI/coordinator/recipe_name_rule/` (the app on 8751 is stopped).
