# SPARMVET_VIZ Workspace Review Report (v1.0)
**Date**: 2026-04-24
**Evaluator**: @dasharch
**Objective**: Comprehensive inspection of development and documentation alignment, inconsistencies, incomplete tasks, and legacy code across the workspace.

---

## 1. Architectural & Rules Alignment (Documentation vs. Reality)

### 🔴 Critical Inconsistencies & Cross-Reference Errors
1. **Workspace Standard Sections Missing**: 
   - [architecture_decisions.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/architecture_decisions.md) (ADR 014) references "Section 12 of the Workspace Standard", but the file [.claude/rules/workspace_standard.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/workspace_standard.md) contains no such section (it has `#REVIEW` comments acknowledging this gap).
   - ADR 016 similarly references "Section 13, Workspace Standard", which is missing. These referential pointers are broken, likely due to recent modularization of the rulebooks (`rules_data_engine.md`, etc.).
2. **Assets/Scripts Deprecation Contradiction (ADR-032 vs. Workspace Standard)**: 
   - ADR-032 states that `assets/scripts/` is **deprecated** and its deletion is mandatory, migrating logic to library-internal modules.
   - However, `assets/scripts/` still contains 12 active files (including critical operations like `build_dep_graph.py`), and `workspace_standard.md` §5-A instructs agents to explicitly use `assets/scripts/build_dep_graph.py`. This is a strict architectural contradiction.
3. **Connectors Directory Renaming**:
   - Phase 23-A indicates `config/connectors/` must be renamed to `config/deployment/` for the new deployment abstraction. The directory remains as `config/connectors/`, but some docs already refer to `config/deployment/`.

### 🟢 Solid Alignments
- **App Structure & Server Decomposition (ADR-045)**: Perfectly aligned. `app/src/server.py` is a highly constrained thin orchestrator (~234 lines). The `Five Handler` logic is correctly compartmentalized in `app/handlers/`, adhering strongly to the Two-Category law.
- **Manifest Structure Standard (ADR-041)**: Code and manifestations in `config/manifests/` heavily abide by the rich dictionary definitions and sequential `wrangling` list structures.

---

## 2. Live Task Status & Development State 

### 🟡 In-Progress (Active Phases)
- **Phase 21: Unified Home Theater**:
  - *Completed*: Navigation simplification, Manifest-driven tab structures, Tier Toggle integration, Collapsible Data Previews, Export Results Bundle (21-I).
  - *Pending/Stuck*: Context-Reactive Filters & Column Selection (21-F) is mid-flight. Right Sidebar Suppression (21-G) and Headless Verification (21-H) are still pending. Comparison Mode (21-E) is deferred.
- **Phase 18: Blueprint Architect**:
  - *Completed*: Bidirectional Lineage mapping, TubeMap functionality (interactive DAG), and Live Preview updates.
  - *Pending*: Field Gap Analysis tool (18-E) to reverse-walk schemas.

### 🟣 Deferred / Backlogged 
- **Action Registry Parity**: The Blueprint Architect interface still needs to expose the `175+` registered actions.
- **Visualization Fixes**: `scale_x_timedelta` and `geom_map` are still suffering from datatype/spatial data requirement mismatches in `viz_factory`.

---

## 3. Technical Debt, Risks & Unknowns

### 1. TubeMap Library Replacement (UI Stability Risk)
- The current stack (`Mermaid.js` + `svg-pan-zoom`) triggers visual flicker during Shiny reactive updates and does not support true hierarchical/lane-based layout schemas. 
- *Next Steps*: Codebase logs reflect a planned migration to `vis-network` (or ELK layout), which is a looming overhaul that will impact `ui.py` and `wrangle_studio.py` deeply.

### 2. Parquet Materialization Footprint (Disk & Standard)
- While `tmpAI/` and `tmp/` separation protocols are observed, the formalization of dated output routes (`tmp/YYYY-MM-DD/{lineage_id}/`) to standardize debug trails is incompletely enforced. 

### 3. Renaming Precision Check (Scientific Audit)
- Identified technical debt regarding generic terminology in manifests (e.g., `phenotype` instead of the mandated `predicted_phenotype`). An automated pass for precision renaming is pending.

### 4. UI Shell Stability Law Discrepancies
- The recent `home_theater.py` logic successfully isolates nested `@render.ui` sub-outputs to prevent DOM node destruction. However, the size of `home_theater.py` (`67.9 KB`) is extremely large and risks creating a new monolith similar to the one resolved in `server.py` by ADR-045.

---

## 4. Conclusion & Recommendations

The **SPARMVET_VIZ** workspace is mathematically robust in the Backend/Transformer architecture and adheres strongly to the Decorator-First Polars processing rules.

**Immediate actions for developers are required in Documentation Alignment:**
1. Rectify the rulebook cross-references (`Section 12`, `Section 13`) in `architecture_decisions.md` to point to the correct modular `.claude/rules/` files.
2. Resolve the `assets/scripts/` contradiction. Either formally reinstate the folder for workspace-global scripts (like dependency graphing), or fully migrate them to `libs/utils/` and strictly adhere to ADR-032.
3. Align the `connectors/` vs. `deployment/` terminology across `bootloader.py` and directory structures.

*Report produced computationally by @dasharch. No operational changes applied.*
