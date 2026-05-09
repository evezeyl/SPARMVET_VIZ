Status: PROCESSED 2026-05-09 — DOC-DRIFT-1 + DOC-DRIFT-EMOJI fixed in-session; 4 content-gap tasks created (DOC-GAP-1 through 4)
# Audit Report: README Sync — 2026-05-09

## Summary
- Files audited: 11 (root README, 8 lib READMEs, DEPLOYMENT_CHECKLIST.md, app/README.md)
- READMEs missing: 0
- Stale references found: 3
- Major drift items: 2

## Findings

### [DRIFT] Incomplete persona list in root README
**File:** README.md
**Issue:** Line 78 lists only 6 personas in `Available profiles:` (`pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`, `project-independent`, `developer`, `qa`) — the introductory text on line 55 claims 8 personas (adds `demo-vetinst`, `web-demo`).
**Evidence:** `config/ui/templates/` contains 8 YAML files including `demo-vetinst_template.yaml` and `web-demo_template.yaml`.
**Suggested fix:** Add `demo-vetinst` and `web-demo` to the line-78 list so it matches §3 of `rules_persona_feature_flags.md`.

### [DRIFT] GalleryManager listed in utils README — actually lives in viz_gallery
**File:** libs/utils/README.md
**Issue:** Line 11 documents `GalleryManager (gallery_manager.py)` as a key component of `libs/utils/`, but the class lives in `libs/viz_gallery/src/viz_gallery/gallery_manager.py`. The viz_gallery README documents it correctly at line 11.
**Evidence:** No `gallery_manager.py` exists in `libs/utils/src/utils/`. Likely a copy-paste artifact.
**Suggested fix:** Remove the GalleryManager entry from `libs/utils/README.md`.

### [STALE-LINK] Transformer README documents debugger "classes" that don't exist
**File:** libs/transformer/README.md
**Issue:** Lines 19–25 list `WranglerDebugger (debug_wrangler.py)`, `AssemblerDebugger (debug_assembler.py)`, `PipelineDebugger (debug_pipeline.py)`, `ExpressionsDebugger (debug_expressions.py)`, `DecoratorDebugger (debug_decorator_suite.py)` in Violet format — none of these classes exist in the corresponding files. The files are CLI scripts with module-level functions (e.g., `run_wrangler_debug()`).
**Evidence:** Direct read of `libs/transformer/tests/debug_*.py` shows no class definitions matching these names.
**Suggested fix:** Rewrite lines 19–25 as CLI script descriptions (not Violet-format class refs). Example: `debug_wrangler.py — CLI runner for atomic wrangling verification`.

### [VIOLET-VIOLATION] Utils README applies Violet format to a non-utils component
**File:** libs/utils/README.md, line 11
**Issue:** Linked to the GalleryManager finding above. Per Violet Law (`rules_documentation_aesthetics.md §3`), the `ComponentName (file.py)` format implies the file lives inside the current lib. Cross-referencing a different lib's component must not use the Violet format.
**Suggested fix:** Either remove (preferred — see GalleryManager finding) or rewrite as a plain cross-reference: `See libs/viz_gallery/ for GalleryManager — gallery bundle persistence layer.`

## Files in clean state

- libs/blueprint_arch/README.md — Violet format correct, ADR references current, component list accurate
- libs/connector/README.md — Schema definition matches ADR-048, Phase 23-B status accurate
- libs/ingestion/README.md — DataIngestor and ExcelHandler correctly documented, no stale references
- libs/test_lab/README.md — Four components (AquaSynthesizer, ManifestBootstrapper, XlsxExtractor, KeyReconciler) all present in src/, Violet-compliant
- libs/viz_factory/README.md — Extensive component list accurate, DECO-2 additions current, integrity suite referenced correctly, Violet format consistent
- libs/viz_gallery/README.md — GalleryManager correctly documented as residing here, ADR-037 / ADR-061 / ADR-063 references valid
- DEPLOYMENT_CHECKLIST.md — Persona validation command and three deployment target sections match current ADR-048 connector abstraction and persona system
- app/README.md — Decomposition into handlers and modules aligns with ADR-045 Two-Category Law
