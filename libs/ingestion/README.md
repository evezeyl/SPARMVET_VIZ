# Ingestion Library (ingestion)

**Authority:** ADR-011, ADR-032

The architectural "Gatekeeper." Reads raw input formats (Excel, TSV) and validates them against the `input_fields` manifest contract before any wrangling occurs. Bad data is rejected here — nothing malformed reaches the Transformer layer.

## Key Components

- **DataIngestor (ingestor.py)**: Handles file I/O and enforces manifest schema contracts. Validates column presence, types, and cardinality against `input_fields`. Emits schema-validated `pl.LazyFrame`s.
- **ExcelHandler (excel_handler.py)**: Authoritative normalisation engine for multi-sheet Excel workbooks. Extracts each sheet to a standardised TSV, ready for ingestion.

## I/O Summary

- **Input**: Raw TSV/CSV files or Excel workbooks resolved via Path Authority (ADR-031).
- **Output**: Schema-validated `pl.LazyFrame`s ready for the Transformer layer. Non-conforming files raise immediately.

## Design Constraints

- **No Shiny imports** — fully headless-safe.
- **No cross-lib imports** — does not import from `transformer` or other `libs/`.
- Path authority delegated to `utils.config_loader.ConfigManager` — no hardcoded paths.

## Installation

```bash
pip install -e libs/ingestion
```

## Tests

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/ingestion/tests/ -v
```

## Debug CLI

```bash
PYTHONPATH=. .venv/bin/python libs/ingestion/tests/debug_ingestor.py \
  --manifest config/manifests/pipelines/<manifest>.yaml \
  --tmp tmpAI/ingestion/
```
