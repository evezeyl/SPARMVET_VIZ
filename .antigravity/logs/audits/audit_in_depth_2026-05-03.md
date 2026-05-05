# Comprehensive In-Depth Audit Report (SPARMVET_VIZ)
**Date:** 2026-05-03
**Scope:** Exhaustive evaluation of `app/`, `libs/`, `config/`, `assets/`, `docs/`, and `.agents/` looking for technical debt, inconsistencies, missing implementations, and architectural drift.

## 1. Architectural Adherence & Inconsistencies

### 1.1 Directory Governance & Script Placement (ADR-032 Violation)
According to **ADR-032 (Library Autonomy & Script Internalization)**, library-internal test/debug runners belong inside their respective `libs/` packages, while `assets/scripts/` is reserved for cross-library, user-facing workspace helper scripts.
- **Inconsistency:** The `assets/scripts/` directory currently contains scripts that belong in test suites. For example, `debug_viz_factory_audit.py` should be moved to `libs/viz_factory/tests/` or `libs/utils/tests/` to adhere strictly to the modular library boundary.

### 1.2 Pipeline & Manifest Standard Inconsistencies
- **Terminology Drift:** As noted in previous daily logs, generic terminology like `phenotype` still exists in some manifests instead of the mandated `predicted_phenotype`. A systematic renaming pass is needed to bring all test data and manifests to full precision renaming standards.
- **Taxonomy Tags:** `tasks.md` flags a need for a Taxonomy Data Audit (`assets/gallery_data/*/recipe_manifest.yaml`) to verify that the newly implemented 6-axis tags are correctly assigned across all gallery assets.

## 2. Incomplete Tasks & Scientific Blockers

### 2.1 The ST22 Plasmid Lineage (Lineage 2)
This is the primary scientific blocker currently active.
- **Missing Elements:** 
  - `2_test_data_ST22_dummy/input_fields/plasmid_data.yaml` is not yet created.
  - Tier 1 filtering (e.g., min identity/overlap for PlasmidFinder) and the subsequent assembly recipe merging metadata and AMR results remain unimplemented.
  
### 2.2 VizFactory Gaps (Spatial & Network Data)
- **Spatial Data (`GALLERY-MAP` / `geom_map`):** The capability to render map chart types (choropleth, hexbin) is currently blocked. The system lacks a spatial manifest format and `GeoDataFrame` support within `VizFactory`.
- **Network Data (`GALLERY-FLOW`):** Flow and network chart types (Chord diagram, Sankey) are blocked because Plotnine has no native support for them. This requires an architectural decision on whether `VizFactory` should support non-Plotnine renderers.

## 3. Technical Debt & Codebase "TODOs"

### 3.1 Ingestion Placeholder Debt
The `libs/ingestion/src/ingestion/placeholder/um_sanitization.py` file contains several unaddressed `TODO`s that represent significant technical debt:
- Missing data type transformations and validation for a minimal set of required columns.
- Missing error handling/reporting for join or read failures to inform the Orchestrator.
- Missing sanitization logic for formatting errors (e.g., stray spaces, Windows newline characters).

### 3.2 Materialization & Debugging Infrastructure
- **Unified Materialization Output:** The debug runners (`debug_wrangler.py` and `debug_assembler.py`) do not automatically route output to standard dated subfolders (`tmp/YYYY-MM-DD/{lineage_id}/`) as prescribed by the scientific audit protocol. This creates inconsistent debugging trails.

### 3.3 T3 LazyFrame Threading
- When new Tier 3 node types (e.g., rename, derive, pivot) are added, the threading mechanism in `_apply_t3_to_lf` needs explicit expansion. This design is pending review in `design_sge_lineage_t3.md`.

## 4. UI/UX & Quality of Life Deficits

### 4.1 Theater and Export Functionality
- **`THEATER-1` (Plot Collapse):** Users cannot currently collapse/minimize individual plot panels within the accordion. Adding a caret toggle for a 1-line collapsed state (persisted in `home_state`) is necessary for a denser data-focus view.
- **`EXPORT-TUBEMAP`:** The global export bundle currently lacks a static map of the T1→T2 lineage. A headless render path for `BlueprintMapper.generate_cy_elements()` is required to embed this SVG into Quarto reports.
- **Selective Export (`EXPORT-2`):** The global export currently lacks UI checkboxes allowing users to selectively include/exclude T1/T2/T3 data, recipes, or filter traces.

### 4.2 Notification Resilience
- **`UX-NOTIF-2`:** Toast notifications currently do not survive a page refresh because they are not persisted to the T3 ghost state.
- **`UX-NOTIF-3`:** There is no project-load notification when the Blueprint Architect reloads a manifest without changing the `project_id`.

## 5. Strategic Recommendations for Success

1. **Prioritize the ST22 Plasmid Lineage:** Fulfill the missing `plasmid_data.yaml` to ensure the core multi-source assembly demonstration is complete.
2. **Resolve the Ingestion Sanitization Debt:** Address the `TODO`s in `um_sanitization.py`. Robust ingestion is critical for data integrity before it reaches the pipeline.
3. **Move Stray Debug Scripts:** Relocate `debug_viz_factory_audit.py` and similar scripts from `assets/scripts/` to their respective `libs/*/tests/` directories to fully comply with ADR-032.
4. **Finalize the Spatial/Network Strategy:** If spatial/network visualisations are core to the product vision, escalate the feasibility study for non-Plotnine integration in `VizFactory`. Otherwise, formally deprecate these tasks to clear the backlog.
