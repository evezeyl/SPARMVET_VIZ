# Utils Library (utils)

**Authority:** ADR-011

Shared utilities used across all application layers. Acts as the neutral resolution point for configuration, hashing, and shared output helpers — keeping these concerns out of the core analytic pipeline.

## Key Components

- **ConfigManager (config_loader.py)**: Recursively reads, validates, and dispatches YAML configuration files from `config/`. Supports `!include` tags for modular manifests. Single source of truth for all parsed configuration.
- **HashingUtility (hashing.py)**: Deterministic SHA-256 fingerprinting for manifests, source files, and Parquet metadata. Produces the `manifest_sha256` and `data_batch_hash` used in session keys and export provenance (ADR-069).
- **DebugOutput (debug_output.py)**: Shared CLI output helpers used by debug scripts across `libs/`.
- **Errors (errors.py)**: Shared exception hierarchy (`SparmvetError`, sub-classes).

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
