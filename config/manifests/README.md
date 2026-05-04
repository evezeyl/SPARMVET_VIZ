# SPARMVET Manifest Standards & Configuration

This directory contains the declarative "Blueprints" for the SPARMVET_VIZ analytical pipeline.

## 🏗️ Architectural Standard (ADR-041)

To ensure high performance in the backend engine and a cohesive development experience in the Blueprint Architect UI, we strictly follow the **Unified Manifest Standard**:

### 1. Schema Blocks (Dictionary Format)

**Used for:** `input_fields`, `output_fields`, `metadata_schema`, `data_schemas`.

- **Structure**: `column_slug: { properties }`
- **Mandatory Properties**:
  - `original_name`: The raw column name in the source file.
  - `type`: `categorical`, `numeric`, or `date`.
  - `label`: Human-readable display name.
- **Why**: Dictionaries provide **O(1) lookup efficiency**. Looking up a column's metadata is instantaneous regardless of the number of columns. This aligns with Polars and Python's internal schema representations.

### 2. Logic Blocks (Sequential List Format)

**Used for:** `wrangling` (tier1, tier2), `join_manifests.recipe`.

- **Structure**: A tiered dictionary containing ordered lists of actions.
- **Mandatory Wrapper**: All wrangling logic must be nested under `tier1` (mandatory) or `tier2` (optional).
- **Format**:

    ```yaml
    wrangling:
      tier1:
        - action: "action_name"
          params: { ... }
    ```

- **Why**: Pipelining is inherently **sequential**. The order of execution must be preserved deterministically to ensure that dependent transformations (like filtering on a renamed column) function correctly.

### 3. Modular Fragments (`!include`)

- All components referenced via `!include` must be stored as **Flat fragments**.
- Included files should NOT repeat the top-level property name (e.g., a file included under `input_fields:` should start directly with the column keys).
- This ensures that the `ConfigManager` can merge inclusions recursively without creating deep nesting artifacts.

## 📁 Directory Structure

Manifests follow the **Basename Mirroring Mandate**:

- `main_manifest.yaml`
- `main_manifest/` (Mirror directory)
  - `input_fields/`: Raw database schemas.
  - `wrangling/`: Transformation logic stacks.
  - `output_fields/`: Published data contracts.
  - `plots/`: Visualization specifications.

## 🧩 Persona Masking

Visibility of specific datasets and plots is controlled via persona templates in `config/ui/templates/`. These templates do not change the data logic, only the exposure level in the UI.

---
**Last Updated**: 2026-04-20
**Authority**: @dasharch / ADR-041
