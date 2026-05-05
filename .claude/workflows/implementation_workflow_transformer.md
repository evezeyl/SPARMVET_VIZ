---
description: Unified Workflow for Transformer Layer Implementation (Tier 1 & 2 Logic)
---

# ⚙️ Transformer Implementation Workflow

This workflow defines the mandatory process for implementing new transformation actions, persistence layers, and pre-aggregation logic in the **Transformer** library, ensuring adherence to **ADR-013 (Data Contract)**, **ADR-024 (Tiered Lifecycle)**, and **Violet Law**.

## 1. Specification & Registry

wwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwwww

- **Source Selection**: Map the requirement to a Polars function (e.g., `unpivot`, `sink_parquet`).
- **Registry Heart**: Register the action using `@register_action("name")` in the appropriate subdirectory:
  - `reshaping/`: Structural changes (unpivot, explode, unnest).
  - `cleaning/`: Atomic expressions (coalesce, cast, regex_extract).
  - `persistence/`: Disk materialization (sink_parquet, scan_parquet).
  - `performance/`: Aggregations (group_by, agg).

## 2. Implementation Phase

- **Logic**: Implement the action to accept `(lf: pl.LazyFrame, spec: Dict[str, Any])`.
- **Parameter Extraction**: Extract all parameters from the `spec` dictionary.
- **Component Referencing**: Use the **Violet Component** standard (`DataWrangler (data_wrangler.py)`, `DataAssembler (data_assembler.py)`) in documentation.

## 3. The 1:1:1 Naming Law (Evidence Loop)

Every transformation component MUST consist of a triplet in `libs/transformer/tests/data/`:

1. **Data (`{action}_test.tsv`)**: The raw data (Tab-Separated).
2. **Manifest (`{action}_test.yaml`)**: The manifest defining the `wrangling` block and `output_fields` contract.
3. **Artifact Generation**: Run the **Universal Wrangler Runner** (for Layer 1) or **Assembly Debugger** (for Layer 2):

    ```bash
    ./.venv/bin/python libs/transformer/tests/debug_wrangler.py --data libs/transformer/tests/data/{action}_test.tsv --manifest libs/transformer/tests/data/{action}_test.yaml --output tmp/transformer/{action}_debug_view.tsv
    ```

## 4. Documentation & Persistence

- **README Update**: Add the action to the "Key Components" list in `libs/transformer/README.md`.
- **User Documentation**: Append the component to `docs/workflows/transformer_implementation.qmd`.
- **Checkpoint Logic**: If implementing a Persistence action (Tier 1 Anchor), ensure it triggers the **Short-Circuit Rule** to bypass redundant Layer 1/2 processing.

## 5. Summary Presentation

- Print the first 10 rows and schema to the terminal using `df.glimpse()`.
- HALT: Only continue after user `@verify` of the materialized `tmp/` artifact.
