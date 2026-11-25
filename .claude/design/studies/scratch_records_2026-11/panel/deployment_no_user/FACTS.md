# Deployments with no user interaction: survey of facts (scout, 2026-11-21; saved from the scout's report, unchanged)
SURVEY STEP 1: deployments with no user interaction (repository dev, read-only, nothing run).

Method and labels. READ (file:line) = I read that line in this run. EARLIER = taken from a survey file already in the repo, cited there, not re-read by me. REASONED = follows from lines I read, not run. Ledger lines are in `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/decision_ledger.md` (abbreviated L###). I did not read `tmp.md` or `/home/evezeyl/work/SPARMVET_VIZ_retest`. I read the earlier study files named in the brief: `tmpAI/panel/deployment_io/FACTS.md`, `tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md`, `tmpAI/panel/deployment_standard/FACTS.md`, and section 0a (parts A, B, D, F) of `tmpAI/panel/deployment_standard/TABLE_FOR_THE_OWNER.md`. Their claims are not repeated here unless I checked them.

Ledger check: D-0427 (L461) and D-0428 (L462) exist. The brief's D-0422 to D-0426 match the ledger and the git log subjects.

## A. Decided, confirm, open

| point | status |
|---|---|
| 1. Where stored tables are kept | OPEN. No line decides it. D-0418 (L452) asks "where is the cache in A? in user? sessions?" and no answer is recorded. CONFIRM (READ): `<user_data>/anchors` (`app/src/bootloader.py:204`; `app/handlers/opening_handlers.py:125`). The `cache` key is never read (see G/H, section 1 row B10). |
| 2. Whether a deployment with no writable place may run | OPEN (choice 5, N1/N2/N3 in deployment_io TABLE). Partly DECIDED: D-0340 (L374): the audit files go through the user's existing location "with a plain error when the directory cannot be written". CONFIRM (READ): today a read-only `user_data` stops every recipe opening (`app/modules/opening_build.py:160-167, 249-254`). It also breaks the page at connection (section B3). |
| 3. Audit and sessions in a deployment with no user | DECIDED: D-0422 (L456): "as long as it can be saved in session in all deployments possibilities and exported in a directory the user can write I think we have our goal done" (her words, quoted in the line). D-0423 (L457): folder `audit/`, DECIDED. D-0302 (L336): "There wont be any audit on pipeline static, this is trivial." DECIDED. CONFIRM (READ): `config/app_features/pipeline-static.yaml:46-47` sets ghost save off. OPEN: what a deployment with no writable user place does with sessions and audit (D-0422 leaves it to choice 5). |
| 4. Declared data absent | DECIDED: D-0427 (L461): "If that data is absent, the opening should stop with a plain reason." (her words; the line says it is the review session's reading of Q5, not a rephrasing). D-0426 (L460): where the user can select data, the user selects; the recipe is not refused for that reason and never silently runs on other data. CONFIRM (READ, today): at start the gate runs the data check on every recipe (`app/src/bootloader.py:425-435`, check `libs/utils` rules via `app/modules/data_analysis_recipe_validator.py:484-535`). A missing file is reported as "dataset cannot be loaded" (`data_analysis_recipe_validator.py:521`). With the selector hidden and the default recipe failing, the start stops with a DeploymentError (`bootloader.py:617-626`). With the selector shown, the recipe is listed as unavailable (`app/handlers/recipe_gate_handlers.py:93-105`). If the file disappears after start, the opening refuses the recipe with the reason (`app/handlers/opening_handlers.py:146-152`). |
| 5. What "the data changed" does to stored tables and to a saved session | Session key: DECIDED in part. D-0025 (L54): "data hash = full content once per session". D-0317 (L351): the warning that lets the user continue stays only for the same recipe with a different data batch. D-0362 (L396): a session saved before a recipe edit is refused (not built). D-0327 (L361): exploration filters never change stored tables or the export. Stored-table rebuild timing and user notice: OPEN (no line). CONFIRM (READ): see E. |
| 6. Whether the app fetches data itself | OPEN. D-0428 (L462) is an order for a study ("a way for static deployment to put several data files and where to be fetch", her words). D-0417 (L451): one deployment specification. CONFIRM (READ): the app does not fetch (section D). |
| 7. Fonts and pictures | DECIDED for the picture key: D-0400 (L434): a key of recipe, data and plotnine version, PNG kept. OPEN: "whether fonts are a named dependency of the deployment or the image" (L434, goes to the deployment study). CONFIRM (READ): `libs/viz_factory/src/viz_factory/viz_factory.py:422` gives a warning when a named font is missing. |
| 8. Anything else on deployments with no user interaction | DECIDED: D-0428 (order), D-0417 (L451, one deployment specification), D-0418 (L452, named places with an access word are the base), D-0413 (L447, a written standard, structure first), D-0425 (L459: the deployment file decides what a recipe's data path may reach; the shipped recipes keep their paths; the local deployment declares `assets/test_data/`). DECIDED, not built: D-0184 (L213): a recipe is checked when selected, not at start. CONFIRM (READ): the start-time check still covers every recipe (`bootloader.py:425-435`). D-0263 (L294): container recipe update DEFERRED. D-0045 (L74): imported data stored by dataset id in its own folder, DECIDED. D-0303 (L337): configuration review waits, DECIDED. D-0373 (L407): demo recipe not changed by agents. |

## B. What the app writes with no click

Each row: what, where (location key), when, what happens if the folder cannot be written.

| # | What | Where (key) | When (file:line) | If the folder cannot be written |
|---|---|---|---|---|
| B1 | Stored tables: `<table>.parquet`, `<table>__T2.parquet`, `<table>__T3_<plot>.parquet` | `user_data` / `anchors` | Every opening: `app/handlers/opening_handlers.py:124-127` calls `run_opening` with `user_data/anchors`. Inside, `check_store` makes the folder and one `TemporaryFile` (`app/modules/opening_build.py:160-167`). Orphan tier-3 files are deleted (`opening_build.py:192-198`, called at `:251`). Each table: `libs/transformer/src/transformer/anchor.py:120-186`: `mkstemp` in the same folder (`:150`), `fsync` (`:173-174`), `os.replace` (`:175`). Also `app/handlers/home_theater.py:1116` (mkdir). Table names: `app/modules/orchestrator.py:30-39`; `opening_build.py:170-189`. | `check_store` raises OSError: the opening stops, nothing is refused, the text says the folder rights or space are the problem (`opening_build.py:201-209, 249-254`; shown at `opening_handlers.py:140-145`). A write error while building a table is classed as a machine error and stops the opening (`opening_build.py:280-283`, REASONED from the `kind` branch). |
| B2 | Start clean-up of stored tables | `user_data/anchors` | At start: `app/src/bootloader.py:204-216`. (a) Removes leftover `.tmp` files older than 600 s (`libs/transformer/src/transformer/anchor.py:27, 31-53`; only FileNotFoundError is caught, `:52-53`). (b) Deletes stored tables of another cache version (`bootloader.py:212`; `anchor.py:59-89`, unlink at `:82`). One sentence to the user, once (`bootloader.py:218-224`; `app/handlers/recipe_gate_handlers.py:133-142`). | Not in a try block at `bootloader.py:203-216`; an OSError from a delete would stop the start (REASONED from the shape of the code, not run). |
| B3 | Sessions folder `<user_data>/_sessions` | `user_data` | `app/modules/session_manager.py:270-274` (mkdir in `__init__`), built by `app/src/server.py:149`, which sits in `def server(input, output, session)` (`server.py:49`). Shiny runs that function per browser session (REASONED). Also `session_dir` mkdir (`session_manager.py:314-318`). | EARLIER (deployment_io FACTS, F11, VERIFIED BY A RUN by the architect): the visitor gets a raw Python error at the first click, not a message at start. REASONED: with a read-only `user_data`, the session function fails for every browser connection, so even a read-only page does not load. |
| B4 | Session record `assembly.json` (the "T1/T2 ghost") | `user_data` / `_sessions/<key>/` | An effect that runs at start of each browser session and again when its inputs change (`app/handlers/home_theater.py:1515-1521`, the comment says it runs unconditionally). It computes the data hash (`:1528-1529`) and writes the record (`:1567-1578`; `session_manager.py:324-393`, `path.write_text` at `:392`). No flag gates it; the only test is `session_manager is not None` (`home_theater.py:1567`). | Failure: a notice, not a stop (`home_theater.py:1584-1588`: "check that the user data folder can be written"). A legacy record: refused with a notice (`:1580-1583`). |
| B5 | T3 audit ghost `t3_<time>.json` | `user_data` / `_sessions/<key>/` | Only when ghost save is on: `app/handlers/audit_stack.py:135-138` and `:291-296`; writer `app/modules/session_manager.py:483-540` (write at `:539`). Not at start. | A warning toast (`audit_stack.py:295-296`). |
| B6 | Gallery index `gallery_index.json` | `gallery` | At start, only when `gallery_enabled` (`app/src/bootloader.py:226-231`). Check at `:233-241`, `libs/viz_gallery/src/viz_gallery/gallery_manager.py:187-214` rewrites the index only when its content differs (`:199-204`). Write is atomic: temp file and `os.replace` (`gallery_manager.py:161-171`). | `not_writable`: printed, the old index is kept, the app goes on (`gallery_manager.py:205-209`; `bootloader.py:237-240`). |
| B7 | Probes | system temp / anchors | `opening_build.py:166` (`TemporaryFile` in the anchors folder, every opening). Blueprint agent auth probe: `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:175-181` (temp dir, runs the Claude CLI; only when the agent is built, `app/src/bootloader.py:1022-1034`). | As B1 for the anchors probe. The agent probe: RuntimeError text (`agent_adapter.py:166-190`). |
| B8 | Temporary folders (system temp, not a deployment place) | system temp | `app/handlers/export_handlers.py:970, 1238` (per export), `:2043-2057` (report render, `quarto render` at `:2055-2056`); `app/handlers/test_lab_handlers.py:814, 976`; `app/modules/gallery_examples.py:110` (gallery sample). No app setting for the folder (the only `tempfile.tempdir` assignment is in a test, `app/tests/test_gallery_sample.py:30`). | Not read (the export's error path). REASONED: Python raises OSError. |
| B9 | Logs | standard output | `bootloader.py:206, 214-215, 240`; `gallery_manager.py:183-184, 208, 212-213`. No log file found in the earlier survey (EARLIER, FACTS). | Not applicable. |
| B10 | `locations.cache` | none | No write, no read. Grep of `app/`, `libs/`, `assets/`: only the presence check (`bootloader.py:348`) and tests (READ). The docs still say the cache is written (EARLIER: `connector.qmd:137`, `deployment_template.yaml:65-67`). | Not applicable. |
| B11 | Bundle imports | `user_data/_imports` | Only on a user action (`bootloader.py:850-855`; `app/modules/bundle_importer.py:261-266`). Not at start. | EARLIER: a message (not read). |
| B12 | Exports | browser download | User action only (EARLIER: `export_handlers.py:761, 1131`). | As B8 for the temp folder. |

Nothing at start writes the recipes folder (BLUEPRINT and the upload do, on user action: EARLIER `blueprint_handlers.py:1188`, `ingestion_handlers.py:50`).

## C. A static deployment today

Shipped files (READ):
- `config/app_features/pipeline-static.yaml`: export on (`:28`); session management off (`:22`); ghost save off (`:46-47`); gallery off (`:10`); selector hidden (`:39-40`); testing_mode false (`:43`); data ingestion off (`:33`); Home left sidebar only (`:49-54`).
- `config/app_features/web-demo.yaml`: interactivity on (`:8`); session management off (`:19`); export off (`:22`); ghost save off (`:33-34`).
- `config/app_features/demo-vetinst.yaml`: session management off (`:19`); export off (`:22`); ghost save off (`:35-36`).
- `config/deployment/pipeline_test/pipeline_test.yaml`: `user_data: tmp/pipeline_test/user/` (`:31`), `cache` (`:30`, unused), `raw_data` (`:26`), default recipe (`:22`).
- `config/deployment/demo/web-demo.yaml`: `user_data: tmp/DEMO/user/` (`:13`), `cache` (`:12`), default recipe (`:7`). demo-vetinst: same keys (EARLIER, deployment FACTS A1 row 10).

Writes from section B that still happen:

| B item | pipeline-static | web-demo / demo-vetinst (session and ghost off, export off on the web ones) |
|---|---|---|
| B1 stored tables at each opening | yes | yes |
| B2 start clean-up | yes | yes |
| B3 `_sessions` folder per browser session | yes (no flag) | yes |
| B4 `assembly.json` record | yes (no flag, `home_theater.py:1567`) | yes |
| B5 T3 ghost | no (ghost save off) | no |
| B6 Gallery index | no (gallery off) | no |
| B7 agent probe | no (blueprint off) | no |
| B8 temp for export | yes, when the user exports (export on) | no (export off, EARLIER app features) |
| B9 stdout | yes | yes |

Is a session created: yes, the `_sessions` folder and one `assembly.json` per recipe and data state (B3, B4). The session panel itself is hidden when session management is off (EARLIER: `app/handlers/session_handlers.py:109-113`, not re-read).

Does the page need a write to work: the data and the recipe are read-only. A writable `user_data` is needed by every opening (B1: `opening_build.py:249-254`) and by every browser session (B3: `session_manager.py:274`). A read-only `user_data` therefore stops the static page at the first opening, and the page may not load at all (REASONED, see B3). A failure of B4 is a notice only (`home_theater.py:1584-1588`).

## D. Several data files and where each is found

- A recipe declares each data file in a `source` block of a dataset. Only `source.type` `local_tsv` and `local_parquet` with `source.path` are used as the path (`app/modules/orchestrator.py:190-195`; `libs/ingestion/src/ingestion/ingestor.py:198-203`). Any other case searches the data folder by dataset name (`ingestor.py:204-221`, search context at `:213`).
- `data_lookup`: choices `data_analysis_recipe_paths` and `by_dataset_id` (`orchestrator.py:45`), checked in the orchestrator (`orchestrator.py:156-157`, ValueError). Default `data_analysis_recipe_paths` (EARLIER `bootloader.py:121`).
- Order (`app/modules/orchestrator.py:172-188`, READ): (1) a recipe imported from a bundle uses only its import folder (`import_data_dir`, `:165-170`); (2) with `data_analysis_recipe_paths` and a local `source.path`, that path is used if it exists, and otherwise the answer is None with no fallback to `raw_data` (`:185-187`); (3) otherwise the file is looked up by exact name in `raw_data` (`:188`). With `by_dataset_id` the recipe path is ignored (`:193`) and the name is looked up in `raw_data`.
- Exact name: `<id>.tsv` or `<id>.parquet` (`libs/ingestion/src/ingestion/ingestor.py:18-31`); both present is an error.
- Writes for Data Import: `file_place` (`orchestrator.py:197-209`); the file the app reads is the file it writes.
- Hashing: `get_source_files` leaves out a dataset with no file (`orchestrator.py:809-820`).
- `locations.raw_data` is one folder per deployment (EARLIER: `bootloader.py:431`; existence at `libs/connector/src/connector/filesystem.py:23, 53-67`).
- The one shipped pipeline example, `config/deployment/pipeline_test/pipeline_test.yaml`: `deployment_type: filesystem` (`:14`), `data_lookup: by_dataset_id` (`:19`), default recipe (`:22`), `raw_data: assets/test_data/duplicated_1_test_data_ST22_dummy/` (`:26`). Its header (`:2-7`) says it simulates Galaxy and IRIDA. It has no job folder and no fetch step.

Connector library (READ):
- Filesystem: `resolve_paths` (`libs/connector/src/connector/filesystem.py:35-69`, works); `fetch_data` no-op (`:71-72`).
- Galaxy: env names `_GALAXY_JOB_HOME_DIR`, `GALAXY_SLOTS_DIR` (`libs/connector/src/connector/galaxy.py:35`); `resolve_paths` uses them as project_root when the deployment has none (`:37-46`, lookup `:51-57`); `fetch_data` no-op (`:48-49`). Works as a path wrapper; no Galaxy file in the repo (EARLIER).
- IRIDA: `fetch_data` validates the token and the irida block then raises NotImplementedError (`libs/connector/src/connector/irida.py:40-52`); token read from `SPARMVET_IRIDA_TOKEN` (`:85-102`); block (`:104-124`); `resolve_paths` uses `irida.local_cache` as root (`:54-66`). Stub.
- Factory: an unknown `deployment_type` becomes Filesystem silently (`libs/connector/src/connector/__init__.py:40-45`).
- The app calls `fetch_data` once at start (`app/src/bootloader.py:126-134`); a failure becomes a DeploymentError (`:135-149`). That text (`:143-144`) names "BioBlendConnector" and `GALAXY_URL`, which do not exist in the code (EARLIER).

Fetch and download code: none in `app/` or `libs/` (READ). Searched for `requests`, `urllib`, `bioblend`, `httpx`, `http.client`, `urlopen`, `aiohttp`. Only hits: `urllib.parse.quote` in `app/handlers/export_handlers.py:351`; dev scripts in `assets/scripts/` (`check_gallery_links.py:17-48`, `check_launch_commands.py:22, 60`, `retest_walkthrough.py:27, 145`) and tests.

Environment variables a pipeline can set (READ unless marked):
- `SPARMVET_DATA_ANALYSIS_RECIPE`: `app/src/bootloader.py:599-600`.
- `SPARMVET_IRIDA_TOKEN`: `libs/connector/src/connector/irida.py:85`.
- `_GALAXY_JOB_HOME_DIR`, `GALAXY_SLOTS_DIR`: `galaxy.py:35`.
- `SPARMVET_DEPLOYMENT`, `SPARMVET_APP_FEATURES`: EARLIER (`bootloader.py:263-277`, `:161`).
- `SPARMVET_IMAGE_REF`: EARLIER (`export_handlers.py:186-194`).
- The Dockerfile sets only `PYTHONPATH=/app` (`assets/containers/Dockerfile:84`). Its comments show `-e SPARMVET_DEPLOYMENT=...` and `-e SPARMVET_APP_FEATURES=...` (`Dockerfile:21-22, 28-29`).

## E. Data that changes under a running app

When the app reads what:
- Recipe list: once at start (`app/src/bootloader.py:404-417`, glob at `:416`). The docstring says a new recipe needs a restart (`:407-415`).
- Load gate on every recipe at start: `bootloader.py:425-435` (structure and data, via `validate_data_analysis_recipe_data`, `data_analysis_recipe_validator.py:484-535`). Columns are checked there (`:530-535`, the run on one row).
- Poll: `app/handlers/recipe_gate_handlers.py:25` (2 s), `:153-156`. It calls `recheck_changed_data_analysis_recipes` (`bootloader.py:497-532`), which compares the recipe file content (`app/modules/cache_keys.py:346-360`, reads all bytes). For refused recipes only, it also compares data size and mtime (`bootloader.py:546-548`; the watch is set in `reject_after_opening` at `:571`). An available recipe's data files are not polled (REASONED from these lines).
- Each opening: `app/handlers/opening_handlers.py:91-127`.
- Each plot: `app/handlers/home_theater.py:373` and `:464-477` (frames kept per data hash).

Cache keys (READ):
- Data files: content. `app/modules/cache_keys.py:139-148` reads all bytes of each file with sha256; a missing one gets `MISSING:<id>` only if it vanished between the two calls (`:146`). No size or time is used for data.
- Batch hash: `cache_keys.py:150-158`. Table key: `cache_keys.py:284-291`, from the file hashes.
- Recipe: file set content (`cache_keys.py:332-343`).
- ADR-089 (`.claude/knowledge/architecture_decisions.md:4298-4304`): chained content keys, status note only. ADR-101 not located and not read.
- Stat (size, mtime) is used only for refused recipes (`bootloader.py:535-544`).

Stored table after the file is replaced (REASONED, from `run_opening` and `anchor.py`):
- The table is rebuilt only when its key differs: a table whose stored file carries its key is read, not built (`opening_build.py:224-229`, docstring). Rebuilt tables replace the same file name (`anchor.py:175`), so no history is kept.
- Timing: at the next opening (`opening_handlers.py:124-127`), and when HOME builds a table or plot (`home_theater.py:373, 464-477`). Never on a timer.
- If the inputs change during the build, the table is not stored and the user is told "reload the page (F5)" (`anchor.py:133-135, 169-170`; `app/modules/orchestrator.py:331-358`; `opening_handlers.py:138-139`; `app/modules/data_change_notice.py:41-50`).
- Data-change notice: `home_theater.py:1541-1550` warns (text from `data_change_notice.py:31-38`) only when that effect runs, that is on an input change or a gate change (REASONED). A replaced data file alone does not trigger it.

Saved session: the key is recipe hash plus data hash (`app/modules/session_manager.py:305-308`). A changed file gives a different key, so the old session keeps the old key. The session list shows 8 characters of the data hash (`app/handlers/session_handlers.py:204`) and only in the session panel.

Date or hash on screen: no date and no full hash in HOME code (REASONED from a search of `home_theater.py` for strftime, isoformat, date and hash in display code). The export carries `created_at` (`app/handlers/export_handlers.py:201`), `data_batch_hash` (`:215, 403, 439`) and a generated date (`:1753, 1779`).

Load gate and refreshed columns:
- At start: `bootloader.py:425-435`.
- When a recipe file changes: the poll (`bootloader.py:497-527`).
- For a refused recipe whose data changes: `bootloader.py:546-548, 520`.
- For an available recipe: a column error appears at the next opening as a build problem and the recipe is refused (`app/handlers/opening_handlers.py:146-152`; `bootloader.py:550-572`). The poll does not catch it (REASONED).

Half-written file: no lock on source files (search of `app/` and `libs/` for `fcntl`, `filelock`, `flock`: only the Blueprint agent, `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py:25, 114, 251, 330-356`). The hash reads whatever bytes exist (`cache_keys.py:146`). A partial file read at opening gives a build problem and a refusal (`opening_handlers.py:146-152`) that stays until size or mtime changes (`bootloader.py:546-548, 571`) (REASONED, not run). Stored tables are safe: they are written by temp file and rename (`anchor.py:145-175`).

## F. Two copies on one folder, identity, locks

- Atomic (READ): stored tables (`anchor.py:145-179`; the still-valid check at `:169-170`); gallery index (`gallery_manager.py:161-171`); Data Import copy then `os.replace` (`app/modules/data_import_check.py:254-265`).
- Not atomic (READ): `assembly.json` (`session_manager.py:392`), T3 ghost (`:539`), label rewrite (`:820`), metadata rewrite after import (`:1037`), recipe saves (`app/handlers/blueprint_handlers.py:1188-1189, 2621`). Session import stages into `.import_<uuid>` (`session_manager.py:739-749`) and moves it (not read further).
- Shared by every visitor (READ): the session key is built from the recipe hash and the data hash only (`session_manager.py:305-308`), and the folder is `_sessions/<key>` (`:270-273, 314-318`). The record has no user field (`session_manager.py:378-390`). Stored tables are under one `anchors` folder (`bootloader.py:204`) and keyed by content (`cache_keys.py:284-291`). Confirmed: no identity.
- Two copies: start clean-up in one copy deletes temporary files of the other that are older than 600 s (`bootloader.py:205`; `anchor.py:27, 49-50`) (REASONED; only a write slower than 600 s is at risk). Two copies writing the same `assembly.json` race (REASONED).
- Locks: no lock file for `user_data`. The only file lock is in the Blueprint agent's session folder (`agent_adapter.py:251, 330-333, 341-356`). In-process locks only: `bootloader.py:210, 506`.

## G. The temporary place of a pipeline

- Today the app uses the system temp folder in the places of B8, and `anchors` for its own write (`anchor.py:150`). Nothing in the deployment file or in an app setting chooses it. The Python default (environment variable `TMPDIR`) decides, which is a process setting, not a deployment key (REASONED from Python's standard behaviour).
- Quarto: the app calls `quarto` from PATH (`export_handlers.py:2055-2056`). The Dockerfile downloads Quarto to `/tmp` at build time (`assets/containers/Dockerfile:56-59`).
- Galaxy, documented (READ `docs/workflows/connector.qmd:194-196`): the job directory is mounted; `SPARMVET_DEPLOYMENT` is said to be set by a Galaxy XML tool wrapper. No wrapper is in the repo (EARLIER). The code uses the job directory only as project_root (`galaxy.py:37-46`). No documented or coded tmp place for the app in Galaxy.
- IRIDA, documented: `local_cache: "/tmp/sparmvet_cache/inputs/"` (`docs/workflows/connector.qmd:108`); `project_root: "/tmp/sparmvet_irida_cache/"` (`docs/deployment/deployment_guide.qmd:68`). The fetch is not implemented: `docs/deployment/deployment_guide.qmd:139-141` says so ("Not implemented yet (2026-11-07)"); `connector.qmd:146-154` and `:204` write it in the present tense. Coded: stub (`irida.py:40-52`). Planned: Phase 23-D (`irida.py:9-13, 44`).
- Container (READ `assets/containers/Dockerfile`): no `VOLUME` and no `USER` line. The run examples mount `/pipeline/output` read-only (`:25-27`). `WORKDIR /app` (`:62`), so the relative `tmp/...` paths of the deployment files point inside the image. A run as the docs describe has no writable `user_data` unless the operator adds a mount (REASONED from `opening_build.py:249-254`).
- Documented as writable: `user_data` (`docs/workflows/connector.qmd:132`; `deployment_guide.qmd:272-273`). Documented as "read-write by the engine" and "safe to delete": the `cache` location (`connector.qmd:137`), which no code reads.

## H. What a visitor sees

- Recipe banner (READ `app/handlers/home_theater.py:1137-1155`): text is the app features `ui_title.text` if set, else `info.label`; subtitle is `info.subtitle`. Hidden when the text is empty or `ui_title.visible` is false. `ui_title` is not in the shipped app features files (EARLIER).
- Info panel (READ `home_theater.py:1945-1952, 1766-1769`): shows the recipe's `info` block as written. No date is added by the code (REASONED).
- Deployment panel (READ `home_theater.py:1968-1980`): deployment banner title and subtitle; shown only when a banner exists (`:1969-1971`).
- Recipe cannot be opened, at the selector (READ `app/handlers/recipe_gate_handlers.py:81-105`): "N recipe(s) unavailable — failed data or structure check", the name, the first two problems, then "Contact: <contact>" or "Contact: not configured for this deployment" (`:101`). If the open recipe is dropped: "'X' was open and no longer passes its checks: HOME shows 'Y' instead." (`:81-83`).
- Refused at opening (READ `app/handlers/opening_handlers.py:146-152`): "The data analysis recipe 'X' could not be opened: <first problem> (and N more)", 30 s.
- Stopped opening (READ `opening_handlers.py:140-145`, text `opening_build.py:201-209`): nothing refused; the text names the folder whose rights or space need fixing.
- Progress line while opening (READ `opening_build.py:108`, `opening_handlers.py:62-69`; decided D-0334, L368).
- Start-time fatal messages (READ `bootloader.py:607-626, 631-638`) go to the operator through `exit_if_errors`, not to a visitor (REASONED).

## Corrections to earlier surveys

1. Deployment_io FACTS F9 says a vanished data file gives `MISSING:<table>` and a valid-looking key. Reading: `get_source_files` leaves such a dataset out (`orchestrator.py:815-819`), so the batch hash simply has one file less (the key changes, not silently in the record). `MISSING:` appears only if a file vanishes between two calls (`cache_keys.py:146`). The poll does not watch available data (section E).
2. Deployment_io FACTS F1 says the session record is written "at every opening". Reading: it is written by an effect on each change of recipe, data or gate version (`home_theater.py:1515-1578`) (REASONED).
3. D-0025 (L54) says "data hash = full content once per session". `cache_keys.py:350-351` (docstring) says the same. The code reads all data files each time that effect runs (`home_theater.py:1528-1529`; `orchestrator.py:809-820`). Her decision and the code differ. Not resolved here.
4. Deployment_standard 0a F says stored tables are "the same folder as the sessions". Reading: both sit under `user_data` as siblings (`anchors` and `_sessions`), not in one folder (`bootloader.py:204`; `session_manager.py:270-273`).

## Facts the study needs that I could not establish by reading (would have to be RUN)

- A read-only `user_data`: what the browser shows at connection (B3) and at the first opening (B1).
- Whether Shiny runs `server()` once per browser session (assumed, REASONED).
- Whether the start clean-up (B2) fails the start when a delete fails.
- What the visitor sees for a data file that is replaced, half written, or refreshed with other columns (E).
- Whether the data-change notice (`home_theater.py:1541-1550`) appears after a plain file replacement.
- Whether a visitor sees another visitor's session (same key) (F).
- Two copies on one folder: races on `assembly.json` and deletion of the other's temporary files.
- The export with the system temp folder not writable (B8).
- The gallery with a read-only gallery folder (B6).
- The container: build (already known not to build, EARLIER F16) and run with and without a writable mount.
- The Galaxy job folder variables in a real Galaxy job.
- Font output on a second machine (section A row 7).

## Not verified

- ADR-101 (not located); ADR-071 and ADR-089 beyond the status note.
- Everything marked EARLIER: the session panel gate (`session_handlers.py:109-113`), the demo-vetinst lines, the deployment and font facts of the earlier survey, `connector.qmd:200-205`, the Dockerfile ENV check (`deployment_io FACTS`), `bundle_importer.py` messages, and `export_handlers.py:761, 1131`.
- Whether "19 places" for `anchors` (deployment_standard 0a F) is right: I did not count.
- Blueprint writes (B and blueprint_handlers) beyond the lines listed.
- Whether the Info panel and the banner are in the home sidebar of each shipped file (EARLIER).
- Any runtime behaviour: nothing was run.
