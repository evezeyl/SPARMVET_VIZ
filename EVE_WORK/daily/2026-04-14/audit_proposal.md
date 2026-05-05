# Phase 12 Architectural Audit: Findings & Proposals (Updated)

## 1. Consistency & Hygiene Check

### Inconsistencies Identified
1. **Tier 3 Audit Stack Architecture and Splits**: 
   - *Old (`ui_traceability_matrix`)*: Separate elements for `audit_nodes_tier2` and `audit_nodes_tier3`. 
   - *New (`ui_implementation_contract` & [Comparison_SideDataPolts_Tiers_Claude_implementation_plan.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/EVE_WORK/daily/2026-04-09/Comparison_SideDataPolts_Tiers_Claude_implementation_plan.md))*: A single interactive Tier 3 sandbox. However, the exact functioning revolves around two states for Tier 3 data:
     - **`t3_recipe_prefill`**: The Tier 3 wide format, facilitating wide-data visualization and user manipulation before blueprint steps.
     - **`t3_recipe_complete`**: Includes the T2 blueprint (aggregation, long format, post-filters) necessary for plot production. (Note: if no T2 prefill transforms exist, `t3_recipe_complete = t3_recipe_prefill`).
2. **Theater Layout Modes**:
   - *Old*: `triple_tier_mode` (T1/T2/T3). 
   - *New*: Replaced by a 2x2 grid `Comparison` mode or 1x2 grid depending on persona. Static personas that do not allow Tier 3 will only show the single/split 1x2 configuration (Reference only).
   - *Active-Only Layout*: This refers specifically to the Tier 3 isolated view (split between Tier 3 Wide / pre-fill and complete Tier 3).
3. **Audit Controls**:
   - The **Revert Protocol** (`btn_revert`) is critical to revert changes back to the pre-filled imported steps from Tier 2. Node disabling (strikethrough) and Violet node trash validation modality apply.
4. **Column Pickers / Data Alteration**:
   - *Tier 1/2 UI*: Pickers only alter visualization for the user. They do NOT modify the data schema.
   - *Tier 3 UI*: Pickers must append proper "drop column" steps to the audit trace and actually modify the data pipeline upon pressing `btn_apply`.

---

## A. Reorganization Plan (Move/Merge Strategy)

To prevent duplication and solidify the new "Source of Truth":

1. **Merge & Deprecate [ui_traceability_matrix.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/ui_traceability_matrix.md)**:
   - Replace with `persona_traceability_matrix.md` based strictly on the 5 persona profiles. Delete [.claude/knowledge/ui_traceability_matrix.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/ui_traceability_matrix.md).
2. **Consolidate 'Source of Truth' via Referencing**:
   - Remove outdated UI Phase sections from [implementation_plan_master.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/plans/implementation_plan_master.md) and [project_conventions.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/knowledge/project_conventions.md).
   - Replace them exclusively with references to the [ui_implementation_contract.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/ui_implementation_contract.md) to ensure only one authoritative, complete source of truth remains.
3. **Update Workflows ([ui_manifest_integration_testing.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/workflows/ui_manifest_integration_testing.md))**:
   - Standardize a testing strategy to optimize GUI testing without manual web browser interactions (e.g., headless Shiny API or a Shiny addon).
   - Tests must evaluate **ONE persona at a time**.
4. **Refresh [workspace_standard.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/workspace_standard.md)**:
   - Add [ui_implementation_contract.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/rules/ui_implementation_contract.md) to the Master Index. Ensure the UI Reactivity/Persona logic definitions are correctly scoped.

---

## B. Updated Implementation Plan (Phase 12 Extension)

*To be referenced via UI Contract.*

### Phase 12-A: Comparison Theater & Persona Scaffolding (ACTIVE)
- [x] **Comparison Theater Base**: Dual-column layout setup.
- [ ] **Dynamic Layout Grid**: Implement logic to shift between 1x2 and 2x2 grid modes based on the loaded persona (remaining 1x2 Reference if Tier 3 is disabled for a static persona).
- [ ] **Tab Minimization Logic**: Configuration to shrink inactive panes into tabs at theater edges when one pane maximizes.
- [ ] **Persona Reactivity Matrix Enforcement**: Link [app/src/ui.py](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/app/src/ui.py) strictly to the 5 personas from [ui_reactivity_persona.md](file:///home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmp/extra/ui_reactivity_persona.md).
- [ ] **Visual vs Functional Pickers**: Connect Tier 1/2 schema pickers as visual-only decorators, and Tier 3 pickers as node-generating audit actions mapped to `btn_apply`.

### Phase 12-B: Position-Aware Sandbox & Controls
- [ ] **Bifurcated Tier 3 (`t3_recipe`)**: Implement the distinction between `t3_recipe_prefill` (wide format exploration prior to blueprint steps) and `t3_recipe_complete` (final plot data including T2 blueprint).
- [ ] **Single Audit Stack**: Pre-fill with *Violet* nodes and attach new *Yellow* nodes. Node positions matter (pre-transform vs post-transform based on Violet node position).
- [ ] **Validation & Revert Protocol**: Add `btn_revert` to wipe the user sandbox and reset to the unmodified T2 blueprint. Implement disable toggles and deletion warnings.
- [ ] **Comment Gatekeeper**: Tie `btn_apply` to validation of `comment_fields` across all active yellow/modified nodes.

### Phase 12-C: Headless UI Manifest Verification
- [ ] **Persona Gating Tests**: Implement headless test strategies (e.g., Shiny testing addons) to verify each persona's UI masking element by element, locking to one persona at a time per test suite.
