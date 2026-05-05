# Phase 12 Architectural Audit: Findings & Proposals (Updated V3)

## 1. Consistency & Hygiene Check
### Inconsistencies Identified
1. **Tier 3 Audit Stack Architecture and Splits**: 
   - *Old (`ui_traceability_matrix`)*: Deprecated.
   - *New*: A single interactive Tier 3 sandbox. Revolves around two logic states:
     - **`t3_recipe_prefill`**: Tier 3 wide format, facilitating wide-data visualization before blueprint steps.
     - **`t3_recipe_complete`**: Includes the T2 blueprint (aggregation, long format, post-filters) necessary for plot production.
2. **Theater Layout Modes**:
   - Replaced by a 2x2 grid `Comparison` mode or 1x2 grid depending on persona. Static personas that do not allow Tier 3 will only show the single/split 1x2 configuration.
3. **Audit Controls & Data Immutability**:
   - Tier 1 and Tier 2 are **strictly immutable** and persistent (cached via Parquet). They are never recalculated via UI interactions, saving huge compute overhead. Tier 3 is a transient branch of Tier 1/2.
   - The **Revert Protocol** (`btn_revert`) only exists if Tier 3 is enabled, and it reverts the transient Tier 3 state back to the Tier 2 blueprint.
4. **Column Pickers**:
   - *Tier 1/2 UI*: Visualization-only (does not alter data).
   - *Tier 3 UI*: Generates "drop column" steps in the audit trace, but data is only modified/recalculated when `btn_apply` is triggered.

---

## A. Reorganization Plan (Move/Merge Strategy)
1. **Merge & Deprecate**: Replace the old traceability matrix with a `persona_traceability_matrix.md` based strictly on the 5 persona profiles.
2. **Consolidate 'Source of Truth'**: Remove outdated UI Phase sections from [implementation_plan_master.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/plans/implementation_plan_master.md) and [project_conventions.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/project_conventions.md). Rely fully on [ui_implementation_contract.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/ui_implementation_contract.md).
3. **Headless/UI Testing Workflows**: Implement `shiny test` or `pytest-playwright` addons to minimize browser interaction. This allows automated verification of the persona masking logic and UI states without massive manual labor.

---

## B. Updated Implementation Plan (Phase 12 Extension)

### Phase 12-A: Comparison Theater & Persona Scaffolding
- [x] **Comparison Theater Base**: Dual-column layout setup.
- [ ] **Persona Reactivity Enforcement**: Implement a strict activation matrix dictating the availability of the Left Nav Panel, Right Audit Panel, and Theater Grids based on the active persona profile.
- [ ] **Visual vs Functional Pickers**: Tier 1/2 schema pickers (visual-only), Tier 3 pickers (node-generating actions mapped to `btn_apply`).

### Phase 12-B: Position-Aware Sandbox & Controls
- [ ] **Bifurcated Tier 3 (`t3_recipe`)**: Isolate `t3_recipe_prefill` vs `t3_recipe_complete`.
- [ ] **Single Audit Stack**: Pre-fill with *Violet* properties, append *Yellow* properties. Position dictates execution order relative to the blueprint.
- [ ] **Validation & Revert Protocol**: Add `btn_revert` (only visible when Tier 3 is active).
- [ ] **Comment Gatekeeper**: `btn_apply` execution blocked until `comment_fields` populated.

### Phase 12-C: Headless UI Manifest Verification
- [ ] **Persona Gating Tests**: Implement automated tests (via Shiny addons) locking one persona at a time to assert proper component masking.
