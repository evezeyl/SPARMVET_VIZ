# Utils Library (utils)

**Authority:** ADR-011

Shared utilities used across all application layers. Acts as the neutral resolution point for configuration, hashing, and shared output helpers — keeping these concerns out of the core analytic pipeline.

## Key Components

- **ConfigManager (config_loader.py)**: Recursively reads, validates, and dispatches YAML configuration files from `config/`. Supports `!include` tags for modular data analysis recipes. Single source of truth for all parsed configuration.
- **Hashing helpers (hashing.py)**: `generate_config_hash()` — deterministic SHA-256 fingerprint of a Python object (a step list or data analysis recipe fragment), used by the Transformer's Tier 1/Tier 2 cache-validity check (`decision_hash`, ADR-089). `get_parquet_metadata_hash()` reads that hash back from a Parquet file's metadata without loading the data. (Session-key hashes `data_analysis_recipe_sha256` and `data_batch_hash` are computed separately in `app/modules/cache_keys.py` and `app/modules/session_manager.py` via plain `hashlib`, not through this module.)
- **Engines (`engines.py`)**: the table of the engines (`ENGINE_TABLE`: engine, data analysis recipe key, library, name prefix), the engine of a block (`tier_engine`, `effective_engine`: the tier's own `data_engine` or `plot_engine`, else the data analysis recipe's), the refusal words of an engine the app has no library for ("no library for this engine in this app"), and the library versions of an engine for the export record. Used by the checker (T06, EN02), the orchestrator, the cache keys and the export.
- **Format checker (`recipe_check.py`)**: `check_recipe(raw, ...)` judges one data analysis recipe in format version 1, in one of four modes (`run`, `build`, `gallery`, `audit`), and returns problems with a permanent code, a path, what is wrong and the fix. The format itself (keys, renamed keys and types, gallery terms) is data in the `.yaml` file next to it. Used by HOME's load gate, Blueprint's Validate, the importer, the scripts and the tests. Companions: the strict file loader (includes confined to the project), `formula_check.py` (a formula may build a Polars expression and nothing else; also the grammar of a smoother formula) and `plot_text_check.py` (the texts of a plot layer that plotnine would run as Python: a smoother formula, a facet variable, a function string; check PS06), `polars_types.py` (the dtypes a text file can hold, read from the installed Polars), the path rules for development paths, `action_names.py` (the registered action names consumers spell).
- **Migration tools (`*_migration.py`)**: bring a data analysis recipe from the unversioned format to format 1 (runs A to D: names and types, `keep_columns`/`drop_columns`, `final_contract`, strict form), run by `assets/scripts/migrate_recipe_format.py`. `engine_keys_migration.py` (run by `assets/scripts/migrate_recipe_engine_keys.py`) rewrites a data analysis recipe of format 1 written before 2026-11-17 to the amended shape (a tier is its own key, a plot entry has no `spec`, `ui_label` and `ui_title`, the four dead `plot_defaults` keys removed, `theme_bw` written where a plot had none); it prints every change and is safe to run twice.
- **RemoveFromAll (remove_from_all.py)**: the pure logic of the HOME audit option "remove from all the data" (D-0415 part B, D-0416): `describe(recipe, column, plans=, place=)` says whether the column is the entity key (`is_entity_key`, D-0313), which tables hold it at the end of tier 1 (`T1:<table>`, the column's name and type there, the plots that read it, also tables no plot reads), which tables the app could not follow, and the one explicit list `may_stay` of tables where the selection may stay; `apply(audit_copy, option, values, reason)` writes one `not_in` filter per table in the audit copy, all or nothing, and returns what it could not do (`Applied`). It describes and applies nothing by itself; it reuses the lineage links of `lineage_walk.py`. The words are provisional.
- **DebugOutput (debug_output.py)**: Shared CLI output helpers used by debug scripts across `libs/`.
- **PipelineError (pipeline_error.py)**: Structured, user-facing error payload (problem/fix/who/category/evidence) threaded through the library exception hierarchy below (ADR-079/ADR-094).
- **Errors (errors.py)**: Shared exception hierarchy rooted at `SPARMVET_Error` (`IngestionError`, `TransformationError`, `VisualizationError`, `DataAnalysisRecipeError`). Each can optionally carry a `PipelineError` instance via `exc.pipeline_error`.

## Design Constraints

- **No Shiny imports** — fully headless-safe.
- **No cross-lib imports** — does not import from any other `libs/` package.
- All paths resolved via `ConfigManager` — no hardcoded paths.

## Installation

```bash
pip install -e libs/utils
```

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/utils/tests/ -v
```
