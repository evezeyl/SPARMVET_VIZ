# Path trial: the eight ways data reaches the app, run for real

Trial of 2026-11-18 on branch `trial/path-check` (worktree `.claude/worktrees/path-check`, two commits, never merged). It gives evidence. It decides and recommends nothing.
Decisions quoted by the brief: D-0268, D-0050, D-0101, D-0165. No decision exists yet for the path rules; the open questions are in section 9.

## 1. What I built and how I ran it

Labels: **ran** = I ran it and read the output. **read** = I read the code at file:line. **reasoned** = not run.

The trial switch is the environment variable `SPARMVET_PATH_TRIAL`, a list of flags:

- `t1i`, `t1ii`, `t1iii`: the folders passed to the existing check (`containment_problems`, code PA02). (i) = the deployment's raw data, recipes, gallery and user data folders. (ii) = the recipe's own folder. (iii) = both.
- `t2`: the same folder check when a data file is opened (`ingestor.py` `_open`; `orchestrator.py` `locate_dataset_file`) and where an upload writes (`data_import_handlers.py`, new helper `upload_target`).
- `t3`: only `.tsv` and `.parquet` are accepted (the list is `DATASET_FILE_SUFFIXES`, `ingestor.py:15`; `local_parquet` is read at `ingestor.py:76`). Checked by the checker (new code PA03) and at the open and at the upload. The file the link points to is judged too.
- Code: `libs/utils/src/utils/path_trial.py` (new), small hooks in `recipe_loader.py`, `recipe_check.py`, `ingestor.py`, `orchestrator.py`, `data_import_handlers.py`. With no flag set, behaviour is unchanged (`libs/utils/tests/test_recipe_paths.py`: 32 passed).
- How the folders reach the check: in the app, the callers do not pass them. In the trial the driver passes the deployment folders by an environment variable (the same folders the connector resolves). So "the app passes the folders" is imitated at one place, `check_recipe_file`. Every caller goes through it (validator and gallery manager).
- Where the code came from: I put the worktree's `libs/*/src` first on the path and printed `utils.__file__` and `ingestion.__file__`: both are inside the worktree. The interpreter is the main folder's `.venv`.

What I ran, and the two moments I measured for each case:

- **check** = the recipe check (`checker_problems`, the check HOME runs at startup and Blueprint runs on Validate). Result `ok` or the code that refused.
- **open** = the table is built (`DataOrchestrator.prepare_ingredient(...).collect()`, what HOME does when it opens). Result `reads` (rows read), `not found`, `wrong columns`, or `REFUSED` by the trial.
- The two are measured separately on purpose. In the app, HOME does not open a recipe that failed the check. Blueprint "reports and never blocks" (`rules_data_analysis_recipe_structure.md` 11a, read). So a column "check refuses / open reads" shows what the open does by itself.
- The upload was run by calling the real new helper `upload_target` and then the handler's own write line (`shutil.copy2(tmp, target)`). I did not start the Shiny app, so the handler's earlier steps (reading and validating the upload) were not run.
- Scratch files: all under `tmpAI/path_trial/` (data in `raw/`, recipes in `recipes/`, links in `raw/lk*.tsv`, `raw_link`, a scratch "other project" with its own `pyproject.toml` in `otherproj/`, a file outside the allowed folders in `outside/`). Raw results: `results_cases.json`, `results_case2.json`, `results_case3.json`, `results_shipped.json`, `table.md`.

## 2. The table: check / open, per case and state

Cell = `check / open`. `ok` = accepted. `PA01`, `PA02`, `PA03` = refused by the recipe check (PA01 shape: `..`, absolute, `~`; PA02 outside the allowed folders; PA03 file type). `REFUSED-open` and `REFUSED-type` = refused by the trial at the moment of opening. `T1(iii)+T2` and `T1(iii)+T2+T3` are the "+T2" and "+T3" columns asked for. The last two columns show T2 and T3 alone.
In the T2 columns the open check uses the deployment folders only (the recipe folder is not known at the open; in the app a recipe in use lies in the recipes folder, so it is inside (i) anyway, read: `find_data_analysis_recipes`, `data_analysis_recipe_validator.py:77-82`).

Cases 7a to 8e use scratch recipes that are NOT in the deployment's recipes folder, so (i) and (ii) differ.

| case | today | T1(i) | T1(ii) | T1(iii) | T1(iii)+T2 | T1(iii)+T2+T3 | T2 alone | T3 alone |
|---|---|---|---|---|---|---|---|---|
| 1a repo recipe, data under raw folder | ok / reads | ok / reads | PA02 / reads | ok / reads | ok / reads | ok / reads | ok / reads | ok / reads |
| 1b repo recipe, data in repo but not in a deployment folder | ok / reads | PA02 / reads | PA02 / reads | PA02 / reads | PA02 / REFUSED-open | PA02 / REFUSED-open | ok / REFUSED-open | ok / reads |
| 4 deposit by table id (by_dataset_id), recipe path points elsewhere | ok / reads | PA02 / reads | PA02 / reads | PA02 / reads | PA02 / reads | PA02 / reads | ok / reads | ok / reads |
| 7a lookup beside recipe, path 'lookup.tsv', started in project root | ok / not found | PA02 / not found | PA02 / not found | PA02 / not found | PA02 / REFUSED-open | PA02 / REFUSED-open | ok / REFUSED-open | ok / not found |
| 7b same, started from recipe folder | ok / reads | PA02 / reads | PA02 / reads | PA02 / reads | PA02 / REFUSED-open | PA02 / REFUSED-open | ok / REFUSED-open | ok / reads |
| 7c lookup beside recipe, path from project root, started in project root | ok / reads | PA02 / reads | ok / reads | ok / reads | ok / REFUSED-open | ok / REFUSED-open | ok / REFUSED-open | ok / reads |
| 7d same path, started from another folder (cwd_b) | ok / not found | PA02 / not found | ok / not found | ok / not found | ok / REFUSED-open | ok / REFUSED-open | ok / REFUSED-open | ok / not found |
| 8a recipe in project, run from another folder (cwd_b) | ok / not found | ok / not found | PA02 / not found | ok / not found | ok / REFUSED-open | ok / REFUSED-open | ok / REFUSED-open | ok / not found |
| 8b moved recipe in other project, data at its project root, run from WT | ok / not found | PA02 / not found | ok / not found | ok / not found | ok / REFUSED-open | ok / REFUSED-open | ok / REFUSED-open | ok / not found |
| 8c same, run from the other project root | ok / reads | PA02 / reads | ok / reads | ok / reads | ok / REFUSED-open | ok / REFUSED-open | ok / REFUSED-open | ok / reads |
| 8d path 'data/b.tsv' (exists only under cwd_b), run from cwd_b | ok / reads | PA02 / reads | PA02 / reads | PA02 / reads | PA02 / REFUSED-open | PA02 / REFUSED-open | ok / REFUSED-open | ok / reads |
| 8e same, run from project root | ok / not found | PA02 / not found | PA02 / not found | PA02 / not found | PA02 / REFUSED-open | PA02 / REFUSED-open | ok / REFUSED-open | ok / not found |
| A1 .tsv link in raw -> file outside | ok / reads | PA02 / reads | PA02 / reads | PA02 / reads | PA02 / REFUSED-open | PA02 / REFUSED-open | ok / REFUSED-open | ok / reads |
| A2 path with .. | PA01 / reads | PA01 / reads | PA01 / reads | PA01 / reads | PA01 / REFUSED-open | PA01 / REFUSED-open | PA01 / REFUSED-open | PA01 / reads |
| A3 absolute path | PA01 / reads | PA01 / reads | PA01 / reads | PA01 / reads | PA01 / REFUSED-open | PA01 / REFUSED-open | PA01 / REFUSED-open | PA01 / reads |
| A4a .yaml named as data | ok / wrong columns | ok / wrong columns | PA02 / wrong columns | ok / wrong columns | ok / wrong columns | PA03 / REFUSED-type | ok / wrong columns | PA03 / REFUSED-type |
| A4b .txt holding tab data named as data | ok / reads | ok / reads | PA02 / reads | ok / reads | ok / reads | PA03 / REFUSED-type | ok / reads | PA03 / REFUSED-type |
| A4c .txt key-like file named as data | ok / wrong columns | ok / wrong columns | PA02 / wrong columns | ok / wrong columns | ok / wrong columns | PA03 / REFUSED-type | ok / wrong columns | PA03 / REFUSED-type |
| A5a .tsv link to an .txt outside | ok / wrong columns | PA02 / wrong columns | PA02 / wrong columns | PA02 / wrong columns | PA02 / REFUSED-open | PA03 / REFUSED-open | ok / REFUSED-open | PA03 / REFUSED-type |
| A5b .tsv link to a .yaml inside raw | ok / wrong columns | ok / wrong columns | PA02 / wrong columns | ok / wrong columns | ok / wrong columns | PA03 / REFUSED-type | ok / wrong columns | PA03 / REFUSED-type |
| A6 .tsv of another user inside raw | ok / reads | ok / reads | PA02 / reads | ok / reads | ok / reads | ok / reads | ok / reads | ok / reads |

What the text says when it is not simply "ok":

- Today, file missing: `Failed to read 'lookup.tsv': FileNotFoundError: No such file or directory (os error 2): lookup.tsv`. The check said ok before (ran, 7a).
- Today, a non-data file named as data: `Column(s) ['id', 'v'] declared in input_fields for 't' not found in the source file (expected file headers: ['id', 'v']).` (ran, A4a, A4c).
- T1 refusal (check): `data_schemas.t.source.path: [PA02] '<path>' resolves outside the folders this deployment allows. Fix: put the file under one of: <the absolute folders, full paths>` (ran). It does not say which of the five locations is meant, and the list is long absolute paths.
- T2 refusal (open): `'<path>' (really <absolute real path>) is outside the folders this deployment allows. Fix: put the file under one of: ...` (ran).
- T3 refusal (check and open): `'<path>' is a .txt file. The app reads only .tsv and .parquet data files. Fix: give the data as a .tsv or .parquet file` (ran).

## 3. What the user does and sees, case by case (in plain words)

1. **A recipe of the repository names development data.** Today it works from the folder the app was started in. With (i) it works while the data lies in the deployment's raw data folder and is refused (PA02) if the data lies elsewhere in the repository (1b). With (ii) it is refused unless the data lies beside the recipe: case 1a is refused, because the recipe is in `recipes/` and the data in `raw/` (ran).
2. **The five locations** (ran, `FilesystemConnector.resolve_paths`, `results_case2.json`):
   - relative: resolved against `project_root` when it is set. Without `project_root` the text stays relative and is read from the folder where the app was started.
   - Started from another folder and no `project_root`: the app stops with "Deployment failed", 3 fatal errors (the folders are not found). Even an absolute raw data folder fails, because the other four are relative (2 fatal errors).
   - with `..`: accepted as written, not cleaned (`tmpAI/path_trial/outside/../raw` stays as it is).
   - `..` up to the project root: accepted. Used as the allowed folder in (i), it makes the whole project allowed: the path `assets/test_data/anything.tsv` was then accepted, while with the normal raw folder it is refused (ran).
   - `~`: not expanded. It is read as a folder literally named `~`; the app stops with a fatal error "does not exist" (1 fatal error) (ran).
   - a link to a folder elsewhere: accepted. The allowed folder in (i) becomes the real folder behind the link (`realpath`): a recipe naming the data through the link is accepted when the link is the allowed folder, and refused when the real raw folder is allowed (ran). So with a link, what the user wrote (`raw_link/`) and what is allowed (`linked_raw/`) are different words for one folder; the message shows only real paths.
   - The trial changes none of this: the five locations are not checked, they only become the allowed folders.
3. **Upload** (ran, `results_case3.json`, `cases3b.py`): see section 5.
4. **A pipeline deposits files** (`data_lookup: by_dataset_id`, the table found by its id): the open reads `<id>.tsv` or `<id>.parquet` in the raw data folder and ignores the recipe's path (ran, case 4: reads 1 row). With T1 the recipe is refused (PA02) because the check still judges the path, which the run ignores: the check refuses a path that is never used. This also happens with the real `pipeline_test` deployment: all 16 config recipes are refused under (i) there (section 4).
5. **API** and 6. **pipe**: not built. `fetch_data` of the IRIDA connector raises "not yet implemented (Phase 23-D)" (read: `libs/connector/src/connector/irida.py:40-52`); the Galaxy one does nothing (`galaxy.py:48-49`). I found no import of `requests`, `urllib`, `httpx` or reading of stdin in `app/` or `libs/*/src` (ran: grep returned no file). `requests` is declared in two `pyproject.toml` files and not imported. A deposit is the only way for now.
7. **A default file beside the recipe** (ran, 7a to 7d). The recipe `repo_recipes/c7/c7.yaml` names `lookup.tsv`, which sits beside it:
   - 7a, app started in the project root: the check says ok (it does not test that the file exists). The open fails: `Failed to read 'lookup.tsv'`.
   - 7b, app started in the recipe's folder: the open reads it. So the same recipe works or fails with the folder where the app was started.
   - With T1 the check refuses `lookup.tsv` in 7a and 7b (the check resolves it against the project root, which is not allowed), although 7b reads fine. The checker's base and the run's base differ (section 6).
   - 7c, the path written from the project root: works from the project root, fails from another folder (7d).
   - Included files are different: `!include` is read relative to the recipe, always (read: `recipe_loader.py:59-72`, not re-run here).
8. **A recipe moved / started elsewhere** (ran, 8a to 8e): section 6.

## 4. The cost for the files that exist today (ran, `shipped.py`, `results_shipped.json`)

I ran the checker, with the trial flag, over every recipe that has `data_schemas`: 16 config recipes (7 pipelines, 5 templates, 4 retest), 34 gallery bundles (profile gallery, with the folder name as id), 4 equality recipes, 3 transformer test recipes. "Newly refused" = refused by PA02 (the trial folder check) and not today. Three of the transformer test recipes already fail today for other reasons (J02, S03, T04, T05, X1); they are counted but marked.

| Folder set and deployment | Config recipes (of 16) | Gallery (of 34) | Equality (of 4) | Transformer tests (of 3, already failing today) | Total newly refused |
|---|---|---|---|---|---|
| (i) deployment folders, `local` | 5 | 0 | 4 | 3 | 12 (9 files that work today) |
| (iii) both, `local` | 5 | 0 | 4 | 3 | 12 |
| (i) and (iii), `retest` deployment | 5 | 0 | 4 | 3 | 12 |
| (i) and (iii), `pipeline_test` deployment | 16 | 0 | 4 | 3 | 23 |
| (ii) recipe's own folder | 16 | 0 | 4 | 3 | 23 |
| T3 file type | 0 | 0 | 0 | 0 | 0 |

(iii) equals (i) with the shipped deployments because a recipe in use lies in the recipes folder, which is already one of the deployment folders.

The 12 refused under (i) with `local` and why (path, the folder it is not in):

- `pipelines/1_test_data_ST22_dummy.yaml` and `pipelines/1_Abromics_general_pipeline.yaml`: one table each, `./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv` (a reference table; `1_test_data_ST22_dummy` is the default recipe of `pipeline_test`).
- `pipelines/figshare_integration.yaml`: 3 tables under `./libs/transformer/tests/data/`.
- `templates/audit.yaml`: `./assets/audit_data/...`. `templates/e_coli.yaml`: 2 tables under `./assets/pipeline_output/...`.
- 4 equality recipes: `app/tests/equality/data/...`.
- 3 transformer test recipes: `libs/transformer/tests/data/...`.

Under (ii) the 11 other config recipes are refused too, because their data lies in `assets/test_data/`, not beside the recipe. Under the `pipeline_test` deployment all 16 are refused because its raw folder is `assets/test_data/duplicated_1_test_data_ST22_dummy/`, while the recipes name `assets/test_data/...`; yet that deployment ignores the recipe paths (`by_dataset_id`).
The gallery bundles are accepted under every set: their data sits beside the recipe, in the gallery folder, which is an allowed folder in (i), and in (ii) the recipe's own folder.

## 5. The upload (case 3), ran

Setup: a recipe table `t` that names `tmpAI/path_trial/raw/up_demo.tsv`; an upload `u1.tsv`; the handler's write line `shutil.copy2`.

- **Table with a path (3a).** Before: the file holds `ORIGINAL`. After the upload: it holds the uploaded rows (`UP1`, `UP2`); the recipe file's bytes are unchanged (ran). The user gets the notice "N file(s) imported - plots are refreshing now" (read: `data_import_handlers.py:377-381`); it does not say that a file at the recipe's path was replaced. Nothing is asked. Silent.
- **Table with a path in the repository outside raw (3b)** and **a link to a file outside (3c)**: today both are written. In 3c the file outside the allowed folders was changed through the link (ran, `secret.tsv` changed).
- **Table without a path (3d)**: written to `raw/newtab.tsv`; found by id afterwards (ran).
- **`.xlsx` (3e)**: written as `raw/newtab.xlsx`. The reader looks for `newtab.tsv` or `newtab.parquet` only, so the table is not found afterwards (`find_dataset_file` returned nothing, ran). The handler said "imported". The docs say the Excel handler turns xlsx into TSV on upload; this code path copies the `.xlsx` as it is (read and ran).
- **`.xlsx` on a table with a `.tsv` path (3f)**: the `.xlsx` bytes (`PK...`) are copied into the `.tsv` file; the next build says `Column(s) ['id', 'v'] ... not found in the source file` (ran). The console prints the first bytes of the file as "available_columns".
- **`.csv` or `.txt` (3g, 3h)**: written as `newtab.csv` or `newtab.txt`; not found by id (ran).
- With T2: 3b and 3c are refused with the "outside the folders" text; 3a, 3d stay allowed (the path is inside the raw folder, so the overwrite still happens).
- With T3: 3e to 3h and 3f are refused with the file type text (T3 judges the uploaded name too). 3a, 3d, 3b, 3c still write.

## 6. Three bases for a relative path, ran (cases 7 and 8)

The checker resolves against the project root (`project_root_of`, nearest `pyproject.toml`; `recipe_loader.py:116`). The run resolves against the folder where the app was started (`ingestor.py:77`). `!include` resolves against the recipe folder.

- **Check ok, run does not find** (today): 8e, path `data/b.tsv`, app started in the project root: the check is ok, the open fails with `Failed to read 'b.tsv'`. Also 7a, 7d, 8a, 8b.
- **Check refuses (with T1), run would find**: 8d, the same path, app started in `cwd_b` where `data/b.tsv` exists: the open reads 2 rows; the check with any T1 set refuses it (PA02, resolved against the project root). Also 7b.
- A recipe moved to another project (8b, 8c): the same path text is ok for the check in both places; the open finds the data only when the app is started in the folder that holds `data/d.tsv`. Under T1(i) 8b/8c are refused, under (ii) and (iii) accepted (the recipe's folder is the project root there).
- A moved recipe never re-bases its paths. Under (i) it is accepted only if the path still falls in a deployment folder.
- An imported bundle (`app/modules/bundle_importer.py`, read; case 9 ran): the recipe is written to the recipes folder, the data to `<user_data>/_imports/<recipe id>/data/<dataset id>.<ext>`, found by id; the recipe's own paths are not touched. In the run, the data was read from the import folder even though the recipe names another path (reads 1 row, today and with T2). Under T1(i) the check refuses the recipe because of the original machine's path text, which the run ignores (same as case 4). Needs: `user_data` allowed (in (i), included), and the file extension must be `.tsv` or `.parquet` (what `find_dataset_file` finds).
- **Gallery bundles**: the check in the gallery profile (GP06, read: `recipe_check.py:1047-1052`) wants the data file named `example_data.tsv` and the folder name in its path; the real data path is read from the project root as `./assets/gallery_data/<id>/example_data.tsv` (ran, all 34 pass today). They are accepted under all folder sets (ran). With another gallery location (a Posit Connect deployment says `gallery/` under its `project_root`) the path text `./assets/gallery_data/...` would not be that folder: not tested (no such deployment run).

## 7. Attack-shaped cases, harmless, ran

Folder allowed = `raw/`. The scratch "secret" is a file I created in `outside/`.

- **A1, a `.tsv` link inside raw to a file outside.** Today: check ok, open reads the outside file (1 row). T1 (any set): refused at the check, PA02 (`realpath`). T2: refused at the open ("really <real path>"). T3 alone: reads (the suffix is `.tsv`).
- **A2, `..`.** Today the check refuses it (PA01). The open, without the check, reads the file (1 row). T2 refuses at the open.
- **A3, absolute path.** Same as A2.
- **A4a, a `.yaml` named as data; A4c, a key-like `.txt`.** Today: check ok; open: `not found in the source file (expected file headers...)`. The text does not show the file. The console block printed by the ingestor does: `available_columns: ['ssh-ed25519 AAAAFAKEKEYFORTRIAL']`, the first line of the file (ran; I did not check whether the browser shows this block). T3 refuses them (PA03 and at the open).
- **A4b, a `.txt` that holds tab data.** Today: read without a word (1 row). T3: refused.
- **A5a, a `.tsv` link to an `.txt` outside.** Today: check ok; open: wrong columns. T1: refused (outside). T3: refused (the real file's suffix).
- **A5b, a `.tsv` link to a `.yaml` inside raw.** Today: wrong columns. T1(i): accepted (inside). T3: refused (the real suffix).
- **A6, the `.tsv` of another user inside raw.** Accepted and read in every state (3 rows).

## 8. What each layer stops and does not stop

- **T1 (folder check at the recipe check).** Stops: a link or a path that leads outside the allowed folders (A1, A5a); data kept in the repository outside the folders (1b); a widened folder if the deployment is wrong is NOT stopped (the `..` location, section 3). Does not stop: a file of another user inside an allowed folder (A6); the open itself (a recipe that was not checked, for instance in Blueprint, still reads); a link created after the check; a recipe path that the run ignores is still refused (case 4, bundles).
- **T2 (same check at the open and at the upload write).** Stops: the recipe that was never checked (A2, A3); a link changed after the check; the upload written outside the folders (3b, 3c). Does not stop: the overwrite of a file inside the allowed folder (3a); a file of another user inside the folder (A6); the case where the allowed folder itself is too wide.
- **T3 (only `.tsv` and `.parquet`).** Stops: a path to a key file, `.yaml`, `.txt` (A4a to A4c, A5b); an upload of `.xlsx`, `.csv`, `.txt` that the reader would never find (3e to 3h). Does not stop: a `.tsv` of another user inside an allowed folder (A6); a `.tsv` outside the allowed folders when used alone (A1 reads with T3 alone); a binary file named `.tsv` (it passes the type check, the reader then reports wrong columns).
- **None of them** change what the user sees about the overwrite on upload (3a): nothing is asked and nothing is said. A refusal at upload exists only for a target outside the folders (T2) or a wrong type (T3).

## 9. Silent behaviours today, each shown by a run

1. The upload copies over the file the recipe names, without a question or a notice (3a).
2. The upload writes through a link and changes the file outside the folders (3c).
3. An `.xlsx` copied into the `.tsv` path of a table corrupts it, with "imported" shown (3f).
4. An `.xlsx`, `.csv` or `.txt` upload without a path is "imported" but never found by id (3e, 3g, 3h).
5. The reader opens any suffix: a `.txt` with tab data is read (A4b).
6. A link inside the data folder to a file outside is read (A1).
7. The open does no check: a path with `..` or an absolute path is read when the check was not the gate (A2, A3). Blueprint does not block by rule.
8. The recipe check accepts a path to a file that does not exist (7a).
9. The same relative path can pass the check and fail the run, or the reverse (8d, 8e).
10. The console shows the first line of a non-data file named as data (A4c).
11. The deployment's folders accept `..` unchanged, and an unset `project_root` ties them to the start folder (section 3).

Records and docs that disagree: found by the scout, not re-checked here (D-0035 against DEC30; `deployment_guide.qmd:57`; `connector.qmd:125,250,129`). My runs agree with: the folders resolve against the start folder when `project_root` is not set, and uploads go to the recipe's path when it is set.

## 10. Files a real build would touch and the tests it would need (effort tags are information, not an argument; D-0268)

Questions with no decision yet (D-0165), needed before a build: which folders are allowed (i, ii, iii); the base for a relative path (project root, recipe folder, start folder); whether a path that the run ignores (by id, bundle) is checked; the upload target and notice; link rule; the messages.

Files:

- `libs/utils/src/utils/recipe_paths.py` (a type function, a base option), `recipe_check.py` (PA03 and the base), `recipe_loader.py`: `[sonnet/medium]`.
- The callers: `app/modules/data_analysis_recipe_validator.py` (3 places), `libs/viz_gallery/src/viz_gallery/gallery_manager.py` (2 places), `app/src/bootloader.py` (to supply the folders): `[sonnet/medium]`.
- `libs/ingestion/src/ingestion/ingestor.py` `_open`, `app/modules/orchestrator.py` `locate_dataset_file` and `get_source_files` (the open check, with the recipe folder passed in if (ii) or (iii)): `[sonnet/medium]`.
- `app/handlers/data_import_handlers.py` (target, notice about an overwrite, xlsx to TSV or refusal): `[sonnet/high]`.
- Docs and records: `connector.qmd`, `deployment_guide.qmd`, `recipe_format_spec.md` DEC30, the ledger (D-0035), `@deps`, the UML: `[haiku/low]`.
- Shipped files: the 12 refused (or 23) recipes need a data location (move the data, or an allowed folder) `[sonnet/low]`.

Tests: containment with a link, with `..`, with a folder that is a link; the three bases (a path ok for the check and not found by the run, and the reverse); the file type (a `.yaml`, a `.txt` with tab data, a link to another type, a `.tsv` link to `.yaml`); the open check on a recipe that was not checked; the upload (path set, not set, `.xlsx`, link, outside) with the overwrite notice; `by_dataset_id` with a recipe path elsewhere; an imported bundle; every shipped recipe, gallery bundle and equality recipe passes with the real deployment's folders (a test that would have failed with the 12). Each test must fail when the new behaviour is turned off (I saw the trial states differ from today in every case above, which is the same effect).

## 11. What I could not run

- The Shiny app itself (the upload handler's validation steps, HOME's "rejected recipe" note, the notifications). I ran the helper and the write line only. What text a user sees in the browser for the console block of A4c is not checked.
- The `pipeline_test` deployment as a live app; its data folder was only used for the shipped-file count.
- A Posit Connect deployment and IRIDA or Galaxy for real; Windows paths and Windows links.
- T2 with the recipe folder as allowed folder at the open: the trial passes only the deployment folders there (the recipe folder is not known at the open). In the app they coincide.
- Permission differences (another user's file in the folder).
- The effect of the trial on the whole test suite (not asked; I ran only `libs/utils/tests/test_recipe_paths.py`: 32 passed with no flag).
