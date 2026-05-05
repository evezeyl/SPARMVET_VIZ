# Codebase ADR Compliance Audit
**Date:** 2026-05-03
**Scope:** Exhaustive evaluation of the SPARMVET_VIZ codebase against established Architecture Decision Records (ADRs) and Project Rules.

*Note: This audit relies on direct inspection of the codebase rather than tracking notes in `tasks.md`.*

## 1. ADR-045 (App Structure & The Two-Category Law)

**Rule:** `app/modules/` must contain "Pure manifest introspection... Zero Shiny imports." Shiny reactive wiring is exclusively reserved for `app/handlers/`.
**Violation:** 
- `app/modules/gallery_viewer.py`
- `app/modules/dev_studio.py`
- `app/modules/wrangle_studio.py`
- `app/modules/help_registry.py`
All of these files contain `from shiny import ui, reactive, render`. This breaks the hard boundary established in ADR-045, mixing UI orchestration into pure module components.

**Rule:** `app/src/server.py` MUST be a thin orchestrator and MUST NOT grow beyond ~250 lines.
**Violation:** `server.py` is currently 285 lines, exhibiting minor architectural drift.

## 2. Manifest Construction Mandates (rules_manifest_structure.yaml & rules_persona_bioscientist.md)

**Rule:** "NEVER use `dataset_id:` as a join key. The correct key is `right_ingredient:`."
**Violation:** `dataset_id:` is currently used extensively across the following manifests:
- `config/manifests/pipelines/stress_test_master.yaml`
- `config/manifests/pipelines/1_test_data_ST22_dummy.yaml`
- `config/manifests/pipelines/2_test_data_ST22_dummy.yaml`
- `config/manifests/pipelines/figshare_integration.yaml`
- `config/manifests/pipelines/1_Abromics_general_pipeline.yaml`
- `config/manifests/pipelines/demo_abromics.yaml`
- Multiple template manifests (`simple_project_template.yaml`, `complex_project_template.yaml`, `example_species_config.yaml`).

**Rule:** "NEVER use bare `on:` as a YAML key. `on` is a YAML boolean (`True`). Always write it as `'on':` (quoted single-tick, or double-quoted)."
**Violation:** Unquoted `on:` keys are present in:
- `config/manifests/templates/simple_project_template.yaml`
- `config/manifests/templates/complex_demo/master_recipe.yaml`
- `config/manifests/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml`
- `config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_Summary_assembly_wrangling.yaml`
- `config/manifests/pipelines/1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml` (which also incorrectly uses a list format `on: ["genotype", "phenotype"]`).

## 3. ADR-016 (Runtime Environment & No Path Hacking)

**Rule:** The use of `sys.path.append` or `sys.path.insert` is completely PROHIBITED. All libraries must rely on standard module resolution after `pip install -e`.
**Violation:** There are 18 occurrences of path hacking across the testing and asset scripts, indicating that the test environment hooks are bypassing the editable install mandate.
- Examples include: `libs/viz_gallery/assets/generate_previews.py`, `libs/transformer/tests/debug_wrangler.py`, `libs/ingestion/tests/debug_ingestor.py`, and many others.

## 4. ADR-011 (Clear Lines Library Policy)

**Rule:** Libraries within `libs/` must be entirely data-agnostic and MUST NEVER import code from another library (e.g., `transformer` cannot import from `ingestion`).
**Violation:** 
- `libs/transformer/tests/debug_wrangler.py` imports `DataIngestor` from `libs.ingestion` and `ConfigManager` from `libs.utils`.
- `libs/viz_gallery/tests/debug_gallery_ui_logic.py` imports `bootloader` from `app.src.bootloader`, reaching *up* into the application orchestration layer from a library.

## 5. ADR-032 (Directory Governance & Script Placement)

**Rule:** Library-internal test and debug runners belong strictly inside their respective `libs/{lib}/tests/` directories. `assets/scripts/` is reserved only for cross-library, user-facing helper scripts.
**Violation:** `assets/scripts/` continues to host internal debugging utilities:
- `debug_viz_factory_audit.py` (Belongs in `libs/viz_factory/tests/`)
- `debug_apply_manifest_standards.py`
- `debug_bootstrap_viz_yamls.py`

## 6. Resolved Violations (For Verification)
- **ADR-052 (Persona Feature Flags):** The codebase was successfully audited for prohibited string comparisons (`if persona in (...)` or `persona == "..."`). The UI components now correctly use `bootloader.is_enabled()`, confirming the tech debt tracked in `rules_persona_feature_flags.md` has been resolved.
- **Flat Keys in Plot Specs:** Checked for prohibited flat keys `position:` and `labels:` across `config/manifests/` and `assets/gallery_data/`. None were found; all conform to the `layers:` nesting requirement.

## Conclusion & Next Steps
This audit highlights significant discrepancies between what is documented as "Law" in the `.agents/rules/` and what currently exists in the codebase. The highest priority for remediation should be:
1. Fixing the `dataset_id:` and unquoted `on:` YAML parsing hazards in the manifests.
2. Refactoring the `app/modules/` to extract Shiny UI imports, restoring the Two-Category Law.
3. Standardizing imports in the `libs/` debug scripts to eliminate `sys.path` hacking and cross-library bleeding.
