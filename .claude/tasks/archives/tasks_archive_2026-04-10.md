# Tasks Archive: 2026-04-10

## 🟢 User Literacy, Error Handling & Simulation (COMPLETED)

- [x] **Export Audit:** Verified ZIP structure (Audit Log + Manifest + Tiers 1-3). [DONE]
- [x] **User Guides:** Created 'Scientific Cookbook' and 'Dev Studio' rationale guides. [DONE]
- [x] **Navigation Sync:** Updated main index with high-level guidance links. [DONE]
- [x] **Advanced Error Handling:** [ADR-031] Integrated `SPARMVET_Error` into ingestion/transformer. [DONE]
- [x] **UI Simulation:** Built `test_ui_scenarios.py` for automated persona-based flows. [DONE]
- [x] **Safety Integration:** [ADR-034] Heuristic typo correction and Viz aesthetic validation. [DONE]
- [x] **Gallery Taxonomy:** [ADR-035] Refactored to Axis-Based classification (Purpose/Pattern/Difficulty). [DONE]
- [x] **Automated Sweep & Hygiene:** Executed 3-persona simulation and negative error-gate audits. [DONE]

## 🟣 Phase 12-B Refinement: Tiered Logic Refactor (COMPLETED)

- [x] **Adoption of ADR-024 (Refined):** Formal split between Tier 1 (Relational) and Tier 2 (Plot-Prep) in YAML. [DONE]
- [x] **Library Core Update:** Added `_resolve_tier` and `run_tier1/2` to `DataWrangler`. [DONE]
- [x] **Manifest Migration:** structural refactor of all ST22 Dummy wrangling sub-files to use `tier1`/`tier2` keys. [DONE]
- [x] **CLI Support:** Updated `debug_wrangler.py` with `--tier` flag for atomic validation. [DONE]
- [x] **Identity Fallback:** Implemented graceful skip for missing `tier2` blocks. [DONE]
- [x] **Global Documentation:** Updated Architecture Decisions, Library READMEs, and created the 'Trunk and Branch' guide. [DONE]

## 🟣 Global Tiered Migration & Documentation Lock (COMPLETED)

- [x] **Global Manifest Refactor:** Refactored 160+ test manifests across `libs/transformer` and `libs/viz_factory`. [DONE]
- [x] **Runner Synchronization:** Updated `debug_runner.py` and `debug_assembler.py` to be tier-aware. [DONE]
- [x] **ST22 Gold Standard Verification:** Successfully executed ST22 Dummy assembly from `assets/template_manifests`. [DONE]
- [x] **Architecture Persistence:** Codified the 'Tiered Wrangling Mandate' in `rules_data_engine.md`. [DONE]
- [x] **Diagnostic Expansion:** Added `ManifestError` and structural heuristic checks to `DataWrangler`. [DONE]
- [x] **Manual Closeout:** Synchronized rules, documentation, and task archives for architectural lock. [DONE]
