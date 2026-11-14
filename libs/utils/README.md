# Utils Library (utils)

**Authority:** ADR-011

Shared utilities used across all application layers. Acts as the neutral resolution point for configuration, hashing, and shared output helpers — keeping these concerns out of the core analytic pipeline.

## Key Components

- **ConfigManager (config_loader.py)**: Recursively reads, validates, and dispatches YAML configuration files from `config/`. Supports `!include` tags for modular data analysis recipes. Single source of truth for all parsed configuration.
- **Hashing helpers (hashing.py)**: `generate_config_hash()` — deterministic SHA-256 fingerprint of a Python object (a step list or data analysis recipe fragment), used by the Transformer's Tier 1/Tier 2 cache-validity check (`decision_hash`, ADR-089). `get_parquet_metadata_hash()` reads that hash back from a Parquet file's metadata without loading the data. (Session-key hashes `data_analysis_recipe_sha256` and `data_batch_hash` are computed separately in `app/modules/cache_keys.py` and `app/modules/session_manager.py` via plain `hashlib`, not through this module.)
- **Recipe checker (recipe_check.py, recipe_spec.yaml)**: `check_recipe(raw, profile, catalogs=...)` judges one recipe in format version 1 (profiles `run`, `build`, `gallery`, `audit`) and returns problems with a permanent code, a path, what is wrong and the fix. The format itself (required and optional keys, renamed keys and types, gallery terms) is data in `recipe_spec.yaml`. Used by HOME's load gate, Blueprint's Validate, the importer, the scripts and the tests. Companions: `recipe_loader.py` (strict file reading, includes confined to the project), `formula_check.py` (a formula may build a Polars expression and nothing else), `polars_types.py` (the dtypes a text file can hold, read from the installed Polars), `recipe_paths.py` (shape and containment of development paths), `action_names.py` (the registered action names consumers spell).
- **Migration tools (recipe_migration.py, step_migration.py, contract_migration.py, strict_form_migration.py)**: bring a recipe from the unversioned format to format 1 (runs A to D: names and types, `keep_columns`/`drop_columns`, `final_contract`, strict form), run by `assets/scripts/migrate_recipe_format.py`.
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
