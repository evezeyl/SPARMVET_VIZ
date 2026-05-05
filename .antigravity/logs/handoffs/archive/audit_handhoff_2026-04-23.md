# Architectural Handoff: Scientific Audit & Visualization (2026-04-23)

## Status: BLOCKED / INFRASTRUCTURE REQUEST
**Requesting Agent:** Antigravity (Lineage Developer)
**Target Agent:** App Orchestrator / Library Architect

### 1. DataAssembler: Shorthand & Normalization
**Requirement**: Support ADR-041 shorthand syntax (`- join: { on: key }`) and unrolled list processing for `mutate`.
**Consequence**: Current lineage development is forced into verbose canonical YAML, increasing manifest maintenance overhead and risk of "Yaml Boolean" pitfalls (e.g. `on` interpreted as `True`).
**Task**: Implement a pre-normalization pass in `DataAssembler.assemble` to map shorthand to canonical actions.

### 2. VizFactory: High-Fidelity Grammar Support
**Requirement**: Support for `position`, `labels` (labs), and `guides` blocks in the plot manifest.
**Consequence**: We are currently unable to produce side-by-side (`dodge`) bar charts or scientifically accurate legends (e.g. renaming "is_multi_resistant" to "Multiresistant") through declarative YAML.
**Task**: Upgrade `VizFactory.render` and `_standardize_config` to pass these parameters to the underlying Plotnine geoms.

### 3. Materialization: Contract-Aware Typing
**Requirement**: `materialize_manifest_plots.py` MUST respect the `final_contract` dtypes.
**Consequence**: `pl.scan_csv` re-infers types from TSV artifacts, causing categorical integers (Year) to revert to continuous scales (floats).
**Task**: Modify the materialization scan to use `schema_overrides` based on the assembly's `final_contract`.

### 4. Ingestor: Non-Breaking Warnings
**Requirement**: Non-breaking warnings when columns requested in manifest are missing in source.
**Consequence**: System failures on missing metadata columns hinder discovery-phase development.
**Task**: Implement non-breaking diagnostic logging in `DataIngestor`.
