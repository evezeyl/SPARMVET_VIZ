# Transformer Library

## Purpose

The central engine for data wrangling and Phase 4 relational assembly. It enforces the ADR-013 data contracts by cleaning raw data and joining disparate sources into a single, tidy Polars DataFrame ready for visualization.

## Documentation
>
> [!IMPORTANT]
> This README is a high-level summary. For exhaustive deep-dives, architectural ADRs, and the full gallery of actions, you MUST refer to the official [Transformer Dev-to-User Guide](../../docs/workflows/wrangling.qmd).

## Key Components

- `DataWrangler (data_wrangler.py)`: Core engine that executes atomic cleaning actions against single datasets using declarative YAML pipelines.
- `DataAssembler (data_assembler.py)`: Relational join orchestrator. Implements **Strict Assembly Enforcement**: requires all ingredients explicitly defined in a recipe, otherwise triggers a controlled crash to protect data integrity.
- `PipelineExecutor (pipeline.py)`: Top-level runner that coordinates the full end-to-end flow (Ingest -> Wrangle -> Assemble).
- `ActionRegistry (registry.py)`: Central dictionary mapping YAML action keys to Python function logic.
- `MetadataValidator (metadata_validator.py)`: Ensures user-provided data aligns with manifest contracts. Performs **Malformed Data Gatekeeping** (ADR-034) by trapping missing columns with typo-correction suggestions and enforcing schema types.
- `IntegritySuite (transformer_integrity_suite.py)` - [Orchestrator]: Programmatically verifies the correctness of every registered action.
- `Phase3Debugger (debug_phase3_refinements.py)` - [Test Utility]: CLI runner for verifying decision hashing and gatekeeping logic.
- `debug_wrangler.py` - [Dev Tool]: CLI runner for isolated atomic wrangling verification. Entry: `run_wrangler_debug()`.
- `debug_assembler.py` - [Dev Tool]: CLI runner for multi-source assembly and `final_contract` output. Entry: `run_assembler_debug()`.
- `debug_pipeline.py` - [Test Utility]: CLI runner for full pipeline execution with materialized output for audit.
- `debug_expressions.py` - [Dev Tool]: CLI runner for atomic Polars expressions (Cast, Coalesce).
- `debug_decorator_suite.py` - [Helper]: CLI runner for Layer 1 action verification.
- **Action Sub-Packages (ADR-024)**:
  - `Reshapinger (reshaping/core.py)`: Structural transformations (Pivot, Unpivot, Explode, Split).
  - `Cleaner (cleaning/core.py)`: Atomic cleaning (Rename, Replace, Nulls, Selection, Sanitization).
  - `Expressionist (cleaning/expressions.py)`: Pattern-based extraction (Regex) and atomic logic (Cast, Coalesce, Label_If).
  - `Categorizer (cleaning/advanced.py)`: Complex lookup mapping.
  - `Analyst (cleaning/analytical.py)`: Sequential, window, temporal, and exhaustive Polars parity actions.
  - `Joiner (relational/joins.py)`: Relational assembly logic.
  - `Summarizer (performance/aggregation.py)`: Pre-visualization data collapsing for Tier 2.
- `Anchor (persistence/anchor.py)`: Tier 1 disk materialization tools (`sink_parquet`).
- **Reactive State (Tier 3)**: Transient views generated via Predicate Pushdown. Supports **Gated Reactivity** via the `btn_apply` trigger, allowing for side-by-side inspection in **Comparison Mode** (T2 reference vs T3 active).
- **Path Authority**: Persistence locations (Tiers 1-3) are determined by `config/connectors`, decoupling hardware from the UI.

## Manifest Syntax (Tiered Wrangling Mandate)

Following **ADR-024**, every `wrangling` entry in a manifest MUST use a nested key structure. This formalizes the separation between generic data cleaning and plot-specific preparation.

```yaml
wrangling:
  tier1: # THE TRUNK: Tidy, Clean, Wide Data (Shared foundation)
    - action: "clean_column_names"
    - action: "join"
      right_ingredient: "metadata"
      "on": ["sample_id"] # ADR-012b: Quotes around "on" prevent YAML boolean 'True' interpretation
    - action: "join_filter" # Prevents Cartesian product explosions when merging 'Long' datasets
      right_ingredient: "APEC_STEC_reference"
      left_on: "gene_slug"
      right_on: "Ref_Gene"

  tier2: # THE BRANCH: Plot-Ready, Aggregated, Long Data (Optional)
    - action: "unpivot"
      index: ["sample_id", "country"]
      on: ["n50", "total_length"]
      variable_name: "metric"
    - action: "recode_values"
      column: "metric"
      rules:
        - matches: "-"
          value: "Non Determined"
        - default: "keep"
```

### Manifest Safeguards (ADR-012b)

- **The Boolean Shield**: To prevent the YAML parser from misinterpreting `on:` as `True`, always use quotes (`"on":`) or ensure the logic engine (DataAssembler) is hardened to resolve both keys.
- **Relational Strategy**: When joining multiple 'Long' format datasets (e.g., AMR + Virulence), prioritize `join_filter` over `join` to maintain a manageable row count and prevent computational bloat.

### Identity Logic (ADR-014)

- **Automatic Fallback**: If the `tier2` block is omitted or left empty, the system automatically uses the Tier 1 output for visualization.
- **Recommendation**: Only utilize Tier 2 when the plot requires data transformations (e.g., pivoting to long format or aggregation) that differ from the tidy Tier 1 table.

## Short-Circuit & Freshness Guard (ADR-024 Refinement)

To maximize performance when iterating on complex pipelines, the `DataAssembler (data_assembler.py)` implements a **Short-Circuit Execution** pattern backed by **Decision Metadata Hashing**.

- **The Logic**: If a `sink_parquet` action is detected and the target file already exists, the assembler calculates a SHA-256 fingerprint of the current assembly recipe.
- **Automated Freshness Check**: The system compares the current manifest fingerprint against the `sparmvet_decision_hash` embedded in the Parquet file's metadata. If they match, it skips joins and skips re-wrangle. If they differ (logic change), it triggers a mandatory re-computation.
- **Manual Override**: To force a full re-computation regardless of hash status, set `force_recompute: true` in the YAML manifest.

## I/O Summary

- **Input**: Raw `pl.LazyFrame`s from the Ingestion layer, and YAML Manifest `spec` dictionaries.
- **Output**: Cleaned, joined, and contract-enforced `pl.LazyFrame`s matching the `output_fields` specification.

## Local CLI Runners

For Phase 1 & Phase 4 verification, use the local debugging runners to execute declarative YAML manifests and verify output TSVs.

**Full Suite Verification (The Automated Gate):**

```bash
./.venv/bin/python libs/transformer/tests/transformer_integrity_suite.py --output_dir tmp/transformer/
```

**Atomic Wrangling (Isolated Action):**

```bash
./.venv/bin/python libs/transformer/tests/debug_wrangler.py --data [INPUT] --manifest [YAML] --output [OUT_TSV]
```

**Relational Assembly (Multi-Source Job):**

```bash
./.venv/bin/python libs/transformer/tests/debug_assembler.py --manifest [YAML] --data [DATA_DIR] --output [OUT_TSV]
```

## Action UI Schema (ADR-075)

Every action that should be visible in the **Blueprint Architect IDE** must declare a `ui_schema` dict in its `@register_action(...)` decorator. The schema drives automatic form generation — no hand-coded forms required.

### Adding a schema to a new action

```python
from transformer.actions.base import register_action

@register_action("my_action", ui_schema={
    "label": "Human-readable label",          # shown in action picker
    "category": "cleaning",                    # groups actions in the picker
    "context": ["t1", "t2"],                   # which tiers allow this action
    "tags": ["null", "cleaning"],              # free-text search terms
    "params": {
        "columns": {
            "widget": "column_selector",       # widget type (see vocabulary below)
            "multi": True,
            "label": "Columns",
            "required": True,
        },
        "value": {
            "widget": "column_or_literal",
            "label": "Fill value",
            "required": True,
        },
    },
})
def action_my_action(lf, spec):
    ...
```

### Widget type vocabulary

| Widget | UI element | Use for |
|---|---|---|
| `column_selector` | Multi/single select from frame schema | Column names |
| `expression` | Code editor with Polars syntax highlighting | Polars expressions |
| `enum` | Dropdown from fixed list (`options: [...]`) | Categorical choices |
| `dtype_picker` | Dropdown of Polars dtype strings | `cast` dtype |
| `number` | Numeric input (int or float) | Counts, thresholds |
| `string` | Plain text input | New column names, patterns |
| `color` | Colour picker (hex or named) | Fill / colour overrides |
| `column_or_literal` | Column select OR literal value | Fill values, join keys |
| `bool` | Checkbox | Flags, on/off options |

### Context tags

| Tag | Tier | Usage |
|---|---|---|
| `t1` | Tier 1 wrangling | Cleaning, renaming, filtering |
| `t2` | Tier 2 wrangling | Reshaping, aggregation |
| `assembly` | Assembly recipe | Joins, cross-source derivation |

### Accessing the catalog programmatically

```python
from blueprint_arch.schema_registry import (
    get_action_catalog,
    get_actions_for_context,
    get_actions_by_category,
    search_actions,
)

# All annotated actions
catalog = get_action_catalog()

# Filter to t1-valid actions
t1_actions = get_actions_for_context("t1")

# Search by keyword
matches = search_actions("regex")
```

### Tests

Schema registration is covered by:
- `libs/transformer/tests/test_ui_schemas.py` — structure, param alignment, semantic rules (440 tests total across all three schema test files)

```bash
PYTHONPATH=. .venv/bin/python -m pytest libs/transformer/tests/test_ui_schemas.py -v
```

## Installation (Editable Mode)

According to the workspace standard, this library must be installed locally via:

```bash
pip install -e ./libs/transformer
```
