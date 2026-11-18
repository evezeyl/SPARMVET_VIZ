# SPARMVET Data Analysis Recipe Standards & Configuration

This directory contains the declarative "Blueprints" for the SPARMVET_VIZ analytical pipeline.

## 🏗️ Architectural Standard (ADR-041)

To ensure high performance in the backend engine and a cohesive development experience in the Blueprint Architect UI, we strictly follow the **Unified Data analysis recipe Standard**:

### 1. Schema Blocks (Dictionary Format)

**Used for:** `input_fields`, `metadata_schema`, `data_schemas`.

- **Structure**: `column_slug: { properties }`
- **Mandatory Properties**:
  - `original_name`: The raw column name in the source file.
  - `type`: a Polars type name that a text file can hold (`String`, `Int64`, `Float64`, `Date`, `Boolean`, ...).
  - `label`: Human-readable display name.
- **Why**: Dictionaries provide **O(1) lookup efficiency**. Looking up a column's metadata is instantaneous regardless of the number of columns. This aligns with Polars and Python's internal schema representations.

### 2. Logic Blocks (Sequential List Format)

**Used for:** the `steps` of a tier (`tier1`, `tier2` of a table or of `joins.*`; `tier3` of a plot entry).

- **Structure**: A tier is a key of its table, join or plot entry: a mapping with an optional `data_engine` (first key) and `steps`, the ordered list of actions.
- **Mandatory key**: `tier1` is required in a table and in a join; `tier2` is optional. There is no `wrangling:` key and no `steps:` container.
- **Format**:

    ```yaml
    tier1:
      steps:
        - action: "action_name"
          params: { ... }
    ```

- **Why**: Pipelining is inherently **sequential**. The order of execution must be preserved deterministically to ensure that dependent transformations (like filtering on a renamed column) function correctly.

### 3. Modular Fragments (`!include`)

- All components referenced via `!include` must be stored as **Flat fragments**.
- Included files should NOT repeat the top-level property name (e.g., a file included under `input_fields:` should start directly with the column keys).
- This ensures that the `ConfigManager` can merge inclusions recursively without creating deep nesting artifacts.

## 📁 Directory Structure

Data analysis recipes follow the **Basename Mirroring Mandate**:

- `main_data_analysis_recipe.yaml`
- `main_data_analysis_recipe/` (Mirror directory)
  - `input_fields/`: Raw database schemas.
  - `wrangling/`: Transformation logic, one file per tier (included as `tier1: !include ...`).
  - `assembly/`: The tiers of the joins.
  - `plots/`: Plot entries (each file holds the whole entry).

## 🧩 App features Masking

Visibility of specific datasets and plots is controlled via app features files in `config/app_features/`. These templates do not change the data logic, only the exposure level in the UI.

---
**Last Updated**: 2026-04-20
**Authority**: @dasharch / ADR-041
