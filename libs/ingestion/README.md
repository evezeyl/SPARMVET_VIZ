# Ingestion Library (ingestion)

**Authority:** ADR-011, ADR-032

The architectural "Gatekeeper." Reads raw input formats (Excel, TSV) and validates them against the `input_fields` data analysis recipe contract before any wrangling occurs. Bad data is rejected here — nothing malformed reaches the Transformer layer.

## Key Components

- **DataIngestor (ingestor.py)**: Handles file I/O and enforces data analysis recipe schema contracts. Validates column presence, types, and cardinality against `input_fields`. Emits schema-validated `pl.LazyFrame`s. Internally runs every ingested frame through `DataSanitizer` (`sanitizer.py`) — strips whitespace and normalises common null-sentinel strings (`"NA"`, `"N/A"`, `"-"`, etc.) on String columns before any wrangling.
- **Excel-to-TSV CLI (excel_handler.py)**: CLI utility (`main()`) for multi-sheet Excel workbook normalisation. Extracts each sheet to a standardised TSV for subsequent ingestion via DataIngestor.

## I/O Summary

- **Input**: Raw TSV/CSV files or Excel workbooks resolved via Path Authority (ADR-031).
- **Output**: Schema-validated `pl.LazyFrame`s ready for the Transformer layer. Non-conforming files raise immediately.

## Design Constraints

- **No Shiny imports** — fully headless-safe.
- **No peer-domain-lib imports** — does not import from `transformer`, `viz_factory`, `blueprint_arch`, or any other domain library in `libs/`. Only `utils` (Tier 1 base, `rules_runtime_environment.md §4`) is used.
- No hardcoded paths — `DataIngestor(data_dir)` takes its root directory as a constructor argument (resolved upstream by the caller, typically via the Bootloader/connector), then locates each dataset's file within it by exact match, falling back to a recursive glob (`find_file()`).

## Installation

```bash
pip install -e libs/ingestion
```

## Tests

This library has no pytest-discoverable tests today — `libs/ingestion/tests/` holds two
standalone CLI scripts, not `test_*.py` files. Run the integrity suite directly
(`rules_verification_testing.md §1`):

```bash
PYTHONPATH=. .venv/bin/python libs/ingestion/tests/ingestion_integrity_suite.py \
  --output_dir tmpAI/ingestion/
```

## Debug CLI

```bash
PYTHONPATH=. .venv/bin/python libs/ingestion/tests/debug_ingestor.py \
  --yaml config/data_analysis_recipes/pipelines/<data analysis recipe>.yaml \
  --data <path to the folder containing the raw TSV files>
```
