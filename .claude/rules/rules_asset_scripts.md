# Asset Scripts & Execution Governance (rules_asset_scripts.md)

**Authority:** Manages the tools, bootstrappers, and utility scripts used directly by users or agents without the final Shiny Dashboard UI.

## 1. Asset Script Philosophy (`assets/scripts/`)

All files residing in `./assets/scripts/` act as headless workflow execution endpoints or developer aids.

- They orchestrate complex multi-step routines (e.g. `figshare_triple_integration.py`).
- They enable the automatic creation of project scaffolding.
- They bypass the main web UI and interact directly with the lower level libraries via explicit CLIs.

## 2. CLI Mandate for Asset Scripts

To ensure user accessibility directly from terminal windows:

- **`argparse` Standard**: All scripts must implement `argparse` for variable ingestion.
- **`--help` Document Strings**: The parser must be populated with a comprehensive script description, parameter explanations, and clear default assumptions.
- **Anti-Hardcoding Rule**: Source inputs and target outputs MUST NOT be hardcoded constants. They must always fall back to script arguments so that tests and variations can be run seamlessly.

## 3. Script Typology & Limitations

It is critical to logically segregate the tools created in this specific layer:

- **A. Functional Assistants (Bootstrappers)**
  - *Definition*: Scripts that generate permanent manifest files (`create_manifest.py`) or apply standards (`debug_apply_manifest_standards.py`).
  - *Impact*: Direct modification or generation of foundational tracking and schema data (YAML/JSON).
- **B. Suggestive Tools (Test Data / Synthesis)**
  - *Definition*: Scripts meant solely to create mock TSVs (`create_test_data.py`) or synthetic relational models for verifying schemas without real patient data.
  - *Impact*: MUST be strictly scoped to outputting to `tmp/` or explicitly requested test data directories (`tests/data/`). Never to default raw data roots.

## 4. Data Priority Hierarchy

When resolving sources for a pipeline script located in `assets/scripts/`, the script MUST obey the following fallback hierarchy to determine target files:

1. **CLI Override**: Always prioritized first (e.g., explicitly given via `--data /path/to/my_data.tsv`).
2. **Manifest Key**: Secondary priority (e.g., retrieving the location through `parse(manifest_yaml)['source']`).
3. **Default Skeleton/Fallback**: Lowest priority, mostly utilized when no variables are passed or during blind tests.
