# Test Lab Library (test_lab)

**Authority:** ADR-011

Data utility toolkit. Provides synthetic data generation, manifest scaffolding, format extraction, and primary-key reconciliation. Used by the Test Lab user space and by asset scripts for headless data preparation.

## Purpose

Scientists often receive Excel workbooks, need anonymised shareable datasets, or want to test a manifest against controlled edge cases. `test_lab` handles all of these without touching the main ingestion pipeline.

## Key Components

- **AquaSynthesizer (aqua_synthesizer.py)**: Reads a real TSV and emits a structurally identical synthetic TSV — same column names, same value distributions and levels, different values. Safe to share. Also generates controlled-error datasets for pipeline testing.
- **ManifestBootstrapper (bootstrapper.py)**: Infers column types and cardinalities from a TSV and writes a boilerplate `input_fields` YAML fragment — eliminates manual schema typing when onboarding a new data source.
- **XlsxExtractor (extractor.py)**: Reads multi-sheet XLSX workbooks and writes one normalised TSV per sheet. Entry point for the Excel → TSV conversion flow in the Data Import panel.
- **KeyReconciler (reconciler.py)**: Boundary-aware primary-key matching with ambiguity detection. Suggests regex patterns for fuzzy PK alignment across datasets; shared with the Blueprint Architect pattern-matching helper.

## CLI Usage

All components expose `argparse` CLIs:

```bash
# Synthesize anonymous test data
.venv/bin/python -m test_lab.aqua_synthesizer --input real_data.tsv --output synthetic.tsv

# Bootstrap manifest fields from a TSV
.venv/bin/python -m test_lab.bootstrapper --input new_data.tsv --output input_fields.yaml

# Extract XLSX sheets to TSV
.venv/bin/python -m test_lab.extractor --xlsx data.xlsx --output_dir tmp/extracted/

# Reconcile primary keys across two TSVs
.venv/bin/python -m test_lab.reconciler --left metadata.tsv --right results.tsv --key sample_id
```

## Design Constraints

- **No Shiny imports** — fully headless-safe.
- **No cross-lib imports** — does not import from `transformer`, `ingestion`, or other `libs/`.
- Output always goes to an explicit `--output` path; never hardcoded.

## Installation

```bash
pip install -e libs/test_lab
```

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/test_lab/tests/ -v
```
