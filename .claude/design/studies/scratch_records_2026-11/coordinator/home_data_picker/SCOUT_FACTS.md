# HOME: is there a control to pick data from a declared place? (scout, 2026-11-21; saved from its report, unchanged)
Read-only search, nothing changed. Read first: agent_principles.md, decision_compliance.md. The brief has no "Decisions" block in the text I received, so I quote no ledger numbers except those the tasks file and ledger already show (D-0426, D-0434, D-0435, D-0439, cited as the ones it names).

**Short answer (point 5).** No HOME control today lets a user pick a folder or a data file from a declared place. The closest things: (a) HOME's recipe selector, which lists recipes from the one declared recipes place; (b) the Data Import panel, which only shows the data paths as text and has an upload plus a dataset assignment. Most likely meaning of the owner's words (REASONED): the planned "Data directory selector" of Data Import (ADR-052 table, `.claude/knowledge/architecture_decisions.md:1546`), or the recipe selector, which chooses from one declared place (`data_analysis_recipes`). Her "we had only one place" fits the recipe selector best (one declared recipes folder), or raw_data for the planned data selector. I could not confirm her memory.

**1. Data Import panel (`app/handlers/data_import_handlers.py`)**
Wiring: panel registered as `data_import` gated by `metadata_ingestion_enabled` (`app/modules/sidebar_registry.py:43-46`); placed in `config/ui/sidebars/home_standard_left.yaml:8`; rendered at `app/handlers/home_theater.py:2007-2015`; server defined at `home_theater.py:2562`.

| Control / text | Input id | What it lists / shows | When shown | On Apply |
|---|---|---|---|---|
| Path text, by_dataset_id | none (text) | `bootloader.get_location("raw_data")` (`data_import_handlers.py:88-99`) | always (panel shown) | n/a |
| Source-file list, other lookups | none (text) | `orchestrator.get_source_files(recipe)` (`:101-129`), i.e. `locate_dataset_file` per dataset (`app/modules/orchestrator.py:809-820`, `:172-188`); declared `source.path` or file by id in raw_data | always | n/a |
| Read-only notice | none | "Data paths are set by the deployment configuration (read-only)" | only when `testing_mode` is false (`:131-139`) | n/a |
| Upload | `data_import_multi_upload` (`ui.input_file`, `:162-165`) | a browser file, no server list. accept `.tsv .csv .xlsx .xls` if `data_ingestion_enabled`, else `.tsv .csv`; multiple only if ingestion (`:146-155`) | `metadata_ingestion_enabled` or `data_ingestion_enabled` and testing_mode (`:146-148`, `:131`) | stores pending entries (`:246-257`) |
| Dataset assignment per file | `data_import_assign_{i}` (`input_select`, `:219-222`) | choices: all `data_schemas` keys + `metadata_schema` if `data_ingestion_enabled` (`:200-205`); else only `metadata_schema` (`:207-208`) | only when pending uploads exist (`:194-196`) | read as `ds_id` (`:277`) |
| Apply | `data_import_apply` (`:236-239`) | n/a | button in assignment block | `apply_import` (`app/modules/data_import_check.py:275-289`): check all, then `store_all` copies over `file_place` (`orchestrator.py:197-209`) with replace in place (`data_import_check.py:241-272`); refreshes anchors (`:292-300`) |

No file or directory picker of a server place exists in the panel (grep for `directory`, `choose_dir`, `listdir` in app: none in Data Import). Note: the panel text "Current default data paths (override below for testing)" (`data_import_handlers.py:180`) says there is an override below, but no override control is in the code.

Flags (`config/app_features/*.yaml`): `testing_mode` true in developer.yaml:40, qa.yaml:46, standalone.yaml:42, pipeline-exploration-advanced.yaml:40; false in pipeline-static.yaml:43, pipeline-exploration-simple.yaml:42, web-demo.yaml:30, demo-vetinst.yaml:32. `metadata_ingestion_enabled` true in developer, qa, standalone, pipeline-exploration-advanced (lines 32, 38, 34-35 region, 30; not individually re-read), false in pipeline-static:31, pipeline-exploration-simple:30, web-demo:23, demo-vetinst:23. `data_ingestion_enabled` true only in developer.yaml:32, qa.yaml:38, standalone.yaml:34. `import_helper_enabled` gates `data_ingestion_enabled` (`app/src/bootloader.py:828-833`). `testing_mode` default True (`bootloader.py:903-905`).

**2. "data selector" in the code and history**
- Code today: no file or data selector. The only `data_selector`-like text is the docstring `bootloader.py:904` and `rules_ui_dashboard.md:61`, `config/app_features/pipeline-*.yaml:41-42`. "Data selector" in current docs (`home_preview_filters.md:37`, `home_exploration_build_brief.md:69`) means the HOME "Table to view: Source | T1 | T2 | T3" control (`home_theater.py:1227`; `app/src/help/home.md:13`; `rules_ui_dashboard.md:72`). That is a table choice, not a file picker.
- Planned earlier: ADR-052 table `architecture_decisions.md:1546` "Data Import | Data directory selector ..."; ADR-052 `:1537` "the data selector pre-fills from manifest default test data paths"; archive `tasks_archive_phase25.md:229-243`, step 25-F: "Active file/directory selector pre-filled from manifest default data paths", commit F2 "active data selector for exploration personas + testing_mode awareness". ADR-058 (`architecture_decisions.md:1794-1819`) built the explicit assignment table instead.
- Removed? Not found: no code, test, or text says it was built and removed. Whether F2 was ever merged cannot be verified (no git history; `tasks_archive_phase25.md:17` shows a "25-F | 29bf346" row, meaning not read).
- Owner's later decision on the default data: D-0426 (tasks.md:920) and D-0439 (tasks.md:929), and an open point that the data place of a deployment is not decided.

**3. Other pickers of server files (models)**
- Recipe selector: `home_theater.py:1982-1995` (`data_analysis_recipe_id`, gate `data_analysis_recipe_selector_visible`, `sidebar_registry.py:35-38`); choices `bootloader.available_data_analysis_recipes` (`home_theater.py:1934`). Built from a glob `*.yaml` in the recipes dir (`app/src/bootloader.py:410-423`); gate filters (`bootloader.py:503-538`). Labels = file stem.
- BLUEPRINT recipe import: `app/handlers/blueprint_handlers.py:975-984`: fixed `config/data_analysis_recipes/pipelines` (fallback `config/`), NOT the declared location. Choices label = stem, value = path.
- Session panel: `app/handlers/session_handlers.py:116-120` `session_manager.scan_sessions()`; no `_sessions` name found.
- Test Lab: no picker of server files found (only `tmp_path.iterdir`, `test_lab_handlers.py:828`, `:985`); not fully read.
- Bundle import: browser upload `app/handlers/export_handlers.py:696-702`, `import_bundle` `:878`; writes to `<user_data>/_imports/<id>/data` (`app/modules/bundle_importer.py:261-266`); bundle_importer `:300` uses `raw_data` location.

**4. Data places today**
- Declared location keys required: raw_data, data_analysis_recipes, cache, user_data, gallery (`bootloader.py:348`); documented in `config/deployment/README.md:39-45`. Only `raw_data` holds data files: `DataOrchestrator.__init__` `orchestrator.py:152-163`; `locate_dataset_file` `:172-188`; `file_place` `:197-209`; `get_source_files` `:809-820`; `get_location` `bootloader.py:846-854`.
- Second data place (not declared as a location): `<user_data>/_imports/<recipe>/data` (`orchestrator.py:165-170`, `bootloader.py:856-861`).
- Third: the recipe's own `source.path` (development lookup; `orchestrator.py:190-195`), which can be any path.
- So "one data place only (raw_data)" is confirmed for the deployment declaration; the code has two more data sources (import folder, recipe paths).

**5. Answer to the question**
The owner most likely meant the recipe selector (`home_theater.py:1982-1995`), which picks from the one declared place (`data_analysis_recipes`, `bootloader.py:410-423`), or a planned data directory selector (ADR-052:1546; archive :229-243) that is not in the code today. Today's HOME lists: recipes from one folder; data as text (raw_data or source paths); no data file list.

**Not verified:** git history (whether F2 or any data selector was built and removed, and when); the runtime rendering of the panel; the `metadata_ingestion_enabled` values in pipeline-exploration-advanced and standalone at the exact lines; `_discover_data_analysis_recipes`'s source of `data_analysis_recipes_dir` (not read); Test Lab's full set of file inputs; the owner's exact memory of "pick a place".
