# Facts: how the app finds and writes recipes, data, sessions, exports and uploads TODAY (scout, 2026-11-21, `dev` d4efb9b6; filed by the coordinator from the scout's hand-back, which was its own summary of a longer text; read, nothing run)

VERIFIED = read at the file:line given. NOT VERIFIED = inferred or only knowable by running. Short file names: `bootloader` = `app/src/bootloader.py`; `orchestrator` = `app/modules/orchestrator.py`; `blueprint_handlers`, `home_theater`, `session_handlers`, `export_handlers`, `ingestion_handlers`, `test_lab_handlers`, `data_import_handlers`, `audit_stack` are in `app/handlers/`; `session_manager`, `bundle_importer`, `data_import_check`, `anchor`, `opening_build`, `audit_run` in `app/modules/`; connectors in `libs/connector/src/connector/`.

## 0. Corrections to earlier collected files
- `tmpAI/panel/recipe_versions/FACTS.md` cites `session_handlers.py:556-564` for the recipe-hash warning; the warning is at `session_handlers.py:597-602`.
- Recipe places flags 5 and 6 are confirmed (`blueprint_handlers.py:975-984, 2685`; `bootloader.py:416-417, 656`).
- The deployment table of `tmpAI/coordinator/data_import_questions/ANSWERS_A_AND_B.md` agrees with the files.
- No ledger line mentions Data Import or the Data Import overwrite: OPEN.

## 1. The mechanism (VERIFIED unless stated)

**Recipes**
- One place: the deployment key `locations.data_analysis_recipes` (`bootloader.py:185`; required `:342-359`; the folder must exist, `filesystem.py:23, 53-66`).
- Found by a top-level `glob("*.yaml")`, once at start (`bootloader.py:404-417`). The load gate runs on all recipes at start (`:186-192, 425-495`). The selector shows the recipes that passed (`home_theater.py:1934`).
- Default recipe: the environment variable `SPARMVET_DATA_ANALYSIS_RECIPE` (`bootloader.py:599-600`), then `default_data_analysis_recipe` (`:601-602`), then the first key of an UNSORTED list (`:646-656`).
- No `name_date` logic and no "newest per name" in the code.
- Who writes recipes: BLUEPRINT saves a component in place (`blueprint_handlers.py:1153-1195`, write `:1188`), saves `info` in place (`:2590-2628`, write `:2621`), writes a branch (`:1484-1528`); BLUEPRINT "new recipe" writes to the FIXED folder `config/data_analysis_recipes/pipelines` and refuses an existing name (`:2685-2703`); an upload with Replace/Append stays in memory (`:1117-1150`); the ingestion copy overwrites silently (`ingestion_handlers.py:39-51`; no UI control found for it); a bundle import writes `<id>_imported_<time>.yaml` INTO the recipes folder (`bundle_importer.py:252-276`); the Test Lab scaffold returns a ZIP download (`test_lab_handlers.py:466-483, 349-352`) whose `source.path` may be the temporary upload path (`scaffolder.py:194-195`, `test_lab_studio.py:72`; NOT VERIFIED at run time).
- BLUEPRINT reads a fixed folder, not the deployment's recipes folder (`blueprint_handlers.py:975-984`).

**Data**
- `data_lookup` default `data_analysis_recipe_paths` (`bootloader.py:121`; `orchestrator.py:152`). Order of search (`orchestrator.py:172-188`): the folder of a bundle import first; then the recipe's `source.path` as written; then exactly `<table>.tsv` or `.parquet` in `raw_data` (`ingestor.py:18-31`).
- ONE `raw_data` place per deployment (`bootloader.py:431`).
- HOME Data Import writes to the place the orchestrator reads (`orchestrator.py:197-209`), copy then `os.replace`, overwrite with no copy of the old file (`data_import_check.py:238-272`); it can write outside `raw_data` when the recipe's path points elsewhere (`orchestrator.py:209`). The upload control exists only with `testing_mode` (`data_import_handlers.py:131-139`). It is a browser upload; the user cannot pick a path on the server.
- Excel: the command-line default output folder is `assets/test_data/extracted_sheets` (`libs/ingestion/src/ingestion/excel_handler.py:17`); the app converter returns a ZIP (`test_lab_handlers.py:975-991`).

**Stored tables**
- In `user_data/anchors` (`bootloader.py:204`). The `cache` location key is NOT used by the app code. Writes: `anchor.py:142-179`.
- If the place is read-only: opening a recipe stops with a message (`opening_build.py:160-167, 249-254`). The clean-up at start only prints on an error (`anchor.py:54-55, 86-87`).

**Sessions and the audit**
- In `user_data/_sessions` (`session_manager.py:270-274`), key = recipe hash and data hash (`:305-308`); no user identity anywhere.
- The assembly record is written at every opening, with no flag (`home_theater.py:1515-1578`; the user is told on failure `:1584-1588`). The audit ghost is written only with ghost save on (`audit_stack.py:135-136, 291`; `session_manager.py:483-540`).
- Session panel gated by `session_management_enabled` (`session_handlers.py:109-113`). Import refuses an existing key (`session_manager.py:736-737`) or keeps both under another name (`:750-753`). Export is a zip made in memory and downloaded (`:647-656`; `session_handlers.py:143`).
- The audit copy is not on disk; `audit_run.py` is used only by tests (`audit_run.py:29-34`). The audit folder is decided (D-0340), not built.

**Exports, imports, other writes**
- Exports: browser download only (`export_handlers.py:761, 1131`). No write on the server found.
- Bundle import folder: `user_data/_imports` (`bootloader.py:850-855`; `bundle_importer.py:261-266`).
- Gallery index: rewritten at start only when the Gallery is enabled (`bootloader.py:226-237`; `gallery_manager.py:187-214`; "not_writable" `:207-209`).
- Temporary files: the system temp folder (`export_handlers.py:1238, 2043`; `test_lab_handlers.py:814, 976`); in `anchors` (`anchor.py:150`); `.import_` in `_sessions` (`session_manager.py:739`); `<name>.import-tmp` beside a data file (`data_import_check.py:255`); in the Gallery folder (`gallery_manager.py:164`).
- Logs: standard output only; no log file.

**The location keys**
- Five: `raw_data`, `data_analysis_recipes`, `cache` (unused), `user_data`, `gallery`; plus `project_root` (`filesystem.py:41-50`) and `irida.local_cache` (`irida.py:62-65`).
- Paths that do NOT go through the locations: the search for the deployment file in `~/.sparmvet` and `/etc` (`bootloader.py:285, 290`); `config/deployment/local/local.yaml`, `config/app_features`, `config/palettes.yaml`, `config/ui/theme.css`, all relative to the working directory (`bootloader.py:295, 375-376, 946, 868`; `ui.py:22-23`); BLUEPRINT's fixed recipe folder (`blueprint_handlers.py:975-977, 2685`); `/.dockerenv` and `SPARMVET_IMAGE_REF` (`export_handlers.py:193-194`; the Dockerfile sets no such variable); Galaxy's `_GALAXY_JOB_HOME_DIR` and `GALAXY_SLOTS_DIR` (`galaxy.py:35, 54`).

**Connectors and API**
- Classes: Base, Filesystem (works), Galaxy (falls back to paths), IRIDA (token and block are validated; `fetch_data` raises `NotImplementedError`, `irida.py:40-52`). Factory `__init__.py:31-45`.
- No BioBlend client (the name appears only in an error message, `bootloader.py:143-144`). No HTTP client in the app code. **Nothing can receive data or a recipe through an API or a URL today.**

**Environment variables**
- Read by the code: `SPARMVET_DEPLOYMENT`, `SPARMVET_APP_FEATURES`, `SPARMVET_DATA_ANALYSIS_RECIPE`, `SPARMVET_IRIDA_TOKEN`. The removed `SPARMVET_PERSONA`, `SPARMVET_PROFILE`, `SPARMVET_CONNECTOR` stop the app (`renamed_keys.py:10-14, 76-93`). Not in the docs: `_GALAXY_JOB_HOME_DIR`, `GALAXY_SLOTS_DIR`, `SPARMVET_IMAGE_REF`.

## 2. How the app is shipped (VERIFIED unless stated)
- Deployment files: local, retest, connect_template, web-demo, demo-vetinst, pipeline_test, deployment_template, README (see `ANSWERS_A_AND_B.md` for the table).
- Dockerfile (`assets/containers/Dockerfile`): `FROM python:3.12-slim` (`:32`), `COPY . .` (`:66`), no `USER`, no `VOLUME`, no default `SPARMVET_DEPLOYMENT`, `CMD` (`:89-90`). `.dockerignore` leaves out `.claude`, `.git`, `tmp`, `assets/test_data` (`:6-12`), so the default development deployment would fail at start in the image (NOT VERIFIED by a run).
- `assets/scripts/bundle_connect.sh` (`:42-54, 99-107`). `create_test_deployment.py` writes the default recipe WITH `.yaml` (`:77`), which the bootloader treats as not found (`bootloader.py:602-614`; NOT VERIFIED by a run).
- `scripts/install_libs.sh:17` names a `requirements.txt` that does not exist. The root `pyproject.toml` has no package list (`:1-53`): `config/` and `assets/` live only in the repository tree. An install from PyPI and its package data: NOT VERIFIED. Install from the GitHub repository, editable: works per `install_libs.sh:42`.
- No Galaxy tool wrapper (XML) and no IRIDA plugin in the repository.

## 3. The places, one table

| Place | Decided by | Written by | If the place is read-only | Two users on one server | In a container |
|---|---|---|---|---|---|
| Recipes (one folder) | `locations.data_analysis_recipes` | BLUEPRINT saves; bundle import; ingestion copy | NOT VERIFIED | shared; no identity | in the image unless mounted |
| BLUEPRINT's recipes | fixed `config/data_analysis_recipes/pipelines` | BLUEPRINT new recipe | NOT VERIFIED | shared | in the image |
| Data | recipe `source.path`, or `locations.raw_data` | HOME Data Import (overwrite) | NOT VERIFIED | shared | needs a mount |
| Data of an import | `user_data/_imports` | bundle import | NOT VERIFIED (message) | shared | needs a mount |
| Stored tables | `user_data/anchors` | every opening | opening stops with a message | shared, keyed by content | needs a writable mount |
| Sessions | `user_data/_sessions` | every opening (record); Apply (audit ghost) | the user is told on failure | shared; a session of user A is listed for user B (NOT VERIFIED by a run) | needs a writable mount |
| Audit folder | decided D-0340, D-0319: inside the session's folder, in the user's own directory | not built | - | - | - |
| Exports | browser download | nothing on the server | works | per browser | works |
| Uploads | browser upload to a temp folder | Shiny | NOT VERIFIED | per browser session | system temp |
| Gallery index | `locations.gallery` | at start, when the Gallery is on | "not_writable", continues | shared | in the image |
| Logs | standard output | - | - | - | container log |

Key point: ONE shared `user_data` per deployment (`bootloader.py:1044`, `server.py:149`); nothing is keyed by a user. A read-only `user_data` stops the opening of recipes.

## 4. The owner's use cases against today

| Use case (her list) | Today |
|---|---|
| Common recipes of a consortium, read-only for the user | Works only if the folder is read-only at the level of the operating system. BLUEPRINT and the bundle import write INTO that same folder. |
| The user's own read/write directory (own data, export and import of recipes) | Does not exist: there is no second recipe place and no per-user place. |
| Static web page (one recipe, data updated now and then) | Works with app features pipeline-static. Still needs a writable `user_data` (the record at opening and the stored tables are always written). |
| Web page with exploration, nothing saved | The flags exist (pipeline-exploration-simple). The app still writes the record at opening. |
| Static pipeline on Galaxy or IRIDA | `deployment_type: galaxy` exists; no Galaxy deployment file is shipped and no tool wrapper exists. IRIDA fails at start (`fetch_data` not implemented). |
| Upload of metadata or data from paths the user has access to, shared and private | Only a browser upload. One `raw_data` per deployment; no choice of a server path; no private place. |
| Same with access set at deployment (IRIDA) | Not working. |
| Local: a user directory and a common directory | One recipes key; the selector shows one folder. |
| Recipe and data given by an API | Not implemented. |
| Shipped in a container | Needs mounts; paths relative to the working directory `/app`; test data left out of the image; no volume declared; runs as root (no `USER`). |
| Installed from GitHub, later PyPI | GitHub editable install works. PyPI NOT VERIFIED; `config/` and `assets/` are not in a package. |

Use cases she did not list, implied by the code or docs: several users on one server (shared folders, no login); a read-only container with one writable volume; offline use (assets are vendored, ADR-071; NOT VERIFIED by a run); a deployment that locks data ingestion (`bootloader.py:387-388`); Posit Connect (a template exists).

## 5. What is already decided on places (ledger line numbers in brackets)
D-0333 (367; DECIDED by the owner, not built), D-0340 (374; DECIDED, not built), D-0390 (424), D-0391 (425), D-0392 (426), D-0393 (427), D-0394 (428), D-0319 (353), D-0102 (131; partly built), D-0263 (294; DECIDED, not done: the key is still in seven files), D-0184 (213; DECIDED, contradicted by the code), D-0362 (396; DECIDED, not built), D-0281 (315; built), D-0283 (317; built), D-0013 (42), D-0064 (93), D-0331 (365), D-0315 (349), D-0373 (407), D-0395 (429). Read each line in `.claude/knowledge/decision_ledger.md` before relying on it.
ADRs: ADR-048 (`architecture_decisions.md:1038`), ADR-071 (`:2250`), ADR-091 (`:4396`; gaps `:4484-4487`; a per-user folder needs an identity `:4438`), ADR-093 (`:4531`), ADR-097 (`:4814`), ADR-099 (`:5055`; points 6 and 7 at `:4975-4983`).

Her earlier questions:
| Point | Status |
|---|---|
| Recipe file name `name_date` | DECIDED, not built |
| Upload refused when the name exists | DECIDED, not built |
| Selector shows the newest per name | OPEN |
| The user's own write place | the need is DECIDED; the place is OPEN |
| Overwrite only in the user's own place | DECIDED, not built |
| Data Import overwrite | OPEN |
| Names of bundle-imported recipes | OPEN (import by file: CONFIRM) |
| Where sessions live | CONFIRM (`_sessions`) |
| Where the audit copy lives | DECIDED (D-0340, D-0319), not built |

## 6. Flagged first (changes a result silently, or hides a step)
1. A session record is written at every opening, with no flag, also in "static" setups (`home_theater.py:1515-1578`).
2. Shared folders with no identity: sessions and stored tables of all users are in one place (`session_manager.py:305-308, 611`).
3. BLUEPRINT overwrites a recipe in place with no backup (`blueprint_handlers.py:1188, 2621, 1517`); the interim backup of ADR-091 is not built.
4. HOME Data Import overwrites with no copy (`data_import_check.py:242-243, 265`) and can write outside `raw_data` (`orchestrator.py:209`).
5. The ingestion copy overwrites silently (`ingestion_handlers.py:49-50`).
6. The default recipe can come from an unsorted list (`bootloader.py:416-417, 656`).
7. BLUEPRINT and HOME read different recipe folders.
8. A scaffolded recipe may name a temporary path (NOT VERIFIED).
9. A bundle import writes into the shared recipes folder (`bundle_importer.py:263`).
10. A read-only `user_data` stops openings (`opening_build.py:249-254`).
11. Audit steps are lost when ghost save is off (`audit_stack.py:135-136, 291`; D-0302).

## 7. Not verified
Run-time behaviour of containers, Galaxy, IRIDA, Connect, PyPI, read-only mounts, two users; texts in the browser; Shiny's temp paths; whether the ingestion copy can be reached; the message of a bundle import on a read-only place; whether sessions of another user are listed; the order of the glob; package discovery of the root project; the recipe export in reproducibility mode (`export_handlers.py:1496-1502`).

## 8. Contradictions between sources
D-0184 against `bootloader.py:186-192`; D-0263 against seven deployment files; `docs/reference/environment_variables.qmd:22` (FileNotFoundError; the code raises DeploymentError, `bootloader.py:263-281`) and `:26` (AuthenticationError against `irida.py:85-102`); `environment_variables.qmd:180` and `docs/workflows/connector.qmd:178` (a `*id*.tsv` glob; the code wants the exact name, `ingestor.py:18-31`); `deployment_template.yaml:37` and `connector.qmd:92` (fallback to pipeline-static; the code stops, `bootloader.py:159-178`); `connector.qmd:200-205` (IRIDA in the present tense; it is a stub); the `cache` location in `deployment_guide.qmd:219`, `connector.qmd:131`, `deployment_template.yaml:65-67` (unused by the code); Gallery "read-only" in `deployment_guide.qmd:223` against the index rewrite; `connector.qmd:196` (Galaxy variables) against `galaxy.py:35, 54`; "BioBlendConnector" in `bootloader.py:143-144` and `docs/troubleshooting/index.qmd:172` (no such class); `install_libs.sh:17` (`requirements.txt` missing); `create_test_deployment.py:77` (`.yaml` suffix); ADR-091 gaps `:4485-4486` still open; `libs/connector/README.md:3` (four classes; IRIDA is a stub).
