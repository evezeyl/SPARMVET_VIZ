# Test Lab Library (test_lab)

**Authority:** ADR-011

Data utility toolkit. Provides synthetic data generation, data analysis recipe scaffolding, and format extraction. Used by the Test Lab user space and by asset scripts for headless data preparation. Primary-key reconciliation is handled by `libs/id_reconciliation/`.

## Purpose

Scientists often receive Excel workbooks, need anonymised shareable datasets, or want to test a data analysis recipe against controlled edge cases. `test_lab` handles all of these without touching the main ingestion pipeline.

## Key Components

- **AquaSynthesizer (aqua_synthesizer.py)**: Reads a real TSV and emits a structurally identical synthetic TSV — same column names, same value distributions and levels, different values. Safe to share. Also generates controlled-error datasets for pipeline testing. Primary API is the class (`propose_config()` + `generate()`, wired into `app/handlers/test_lab_handlers.py`); the module also has a standalone legacy `main()` CLI with its own `--data_dir`/`--out_dir`-style flags (see CLI Usage below) — its own docstring points callers at the class API instead.
- **DataAnalysisRecipeBootstrapper (bootstrapper.py)**: Infers column types and cardinalities from a TSV and writes a boilerplate `input_fields` YAML fragment — eliminates manual schema typing when onboarding a new data source. Class API only, no CLI. Not wired into any handler yet — integration is pending known-bug fixes (`rules_test_lab.md §4b`, task TL-BOOTSTRAP-FIX-1).
- **XlsxExtractor (extractor.py)**: Reads multi-sheet XLSX workbooks (given a config mapping sheet → primary key) and writes one normalised TSV per sheet via `extract()`. Class API only, no CLI. Not wired into any handler — exercised only by its own tests. The Data Import panel's planned Excel→TSV conversion path uses `ExcelHandler` from `libs/ingestion/` instead (status: deferred, `ui_implementation_contract.md §10`).
- **DataReformatter (reformatter.py)**: Converts XLSX/CSV files to TSV with bulk folder processing. Class API only, no CLI — wired into `app/handlers/test_lab_handlers.py`.
- **Anonymiser (anonymiser.py)**: `anonymise()`/`anonymise_batch()` strip identifying columns and replace an ID column with a sequential, hash-based, or custom-prefix anonymous id, writing an original-id-to-anon-id mapping TSV alongside. Multi-file batches keep the same original id mapped to the same anon id across files. Class API only, no CLI.
- **DataAnalysisRecipeScaffolder (scaffolder.py)**: Turns prepared TSVs (plus optional recipe steps per dataset, e.g. the ID cleaning steps that `id_reconciliation.recipe_steps` writes) into a boilerplate data analysis recipe ZIP — structure, inferred types, PK hints, `tier1` wrangling stubs only. The steps are written as they are, keyed by `dataset_id(path)`; steps for a dataset that is not scaffolded are refused, never dropped. No analysis groups, plots, or join strategy (that is BLUEPRINT's job, see `rules_test_lab.md §4`). Class API only, no CLI.
- **ID Reconciliation**: Primary-key matching (exact, pattern-based, fuzzy), step list generation, and recode workflows are now in `libs/id_reconciliation/`. See that library's README for usage.

## CLI Usage

Only `aqua_synthesizer.py` exposes an `argparse` CLI (a legacy standalone entry point —
the class API `AquaSynthesizer().propose_config()` + `.generate()` is what the app actually
uses). The other five components (Bootstrapper, Extractor, Reformatter, Anonymiser,
Scaffolder) are class-only APIs with no CLI; four of them are wired directly into
`app/handlers/test_lab_handlers.py` (Bootstrapper is not yet wired in — see Key Components).

```bash
# Legacy quick-generate mode: fabricate n_rows of dummy data for the given headers
.venv/bin/python -m test_lab.aqua_synthesizer --generate_only sample_id value --n_rows 50 --out_dir tmp/

# Legacy real-data-shaped synthesis: fabricate IDs/values from real TSV(s) in a directory
.venv/bin/python -m test_lab.aqua_synthesizer --data_dir path/to/real_data/ \
  --primary_key_data sample_id --out_dir tmp/

# Bootstrap data analysis recipe fields from a TSV — class API only
# from test_lab.bootstrapper import DataAnalysisRecipeBootstrapper
# DataAnalysisRecipeBootstrapper().bootstrap(...)

# Extract XLSX sheets to TSV — class API only
# from test_lab.extractor import XlsxExtractor
# XlsxExtractor().extract(excel_path, config_path, out_dir)

# Reconcile primary keys across two files — use libs/id_reconciliation/ directly
# from id_reconciliation import IDReconciliationEngine
```

## Design Constraints

- **No Shiny imports** — fully headless-safe.
- **No cross-lib imports** — does not import from `transformer`, `ingestion`, or other `libs/`.
- Output always goes to an explicit output path argument (`out_dir` on the class APIs, `--out_dir` on the `aqua_synthesizer` CLI); never hardcoded.

## Installation

```bash
pip install -e libs/test_lab
```

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/test_lab/tests/ -v
```
