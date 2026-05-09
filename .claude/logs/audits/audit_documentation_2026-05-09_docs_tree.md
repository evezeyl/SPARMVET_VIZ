Status: PROCESSED 2026-05-09 — DOC-DRIFT-1 + DOC-DRIFT-EMOJI fixed in-session; 4 content-gap tasks created (DOC-GAP-1 through 4)
# Audit Report: docs/ Tree Sync — 2026-05-09

## Summary
- Files audited: 58 `.qmd` files across all doc categories
- Stale references: 1 (file path drift in dashboard_app.qmd)
- Persona ID references with forbidden underscores: 1 (dashboard_app.qmd line 55)
- Orphaned/unreferenced .qmd files: 8
- Persona list drift: 2 personas missing from traceability matrix
- manifest_structure.yaml status: **DRIFTED** (assembly vs join directory naming)
- Forbidden YAML shorthand examples in docs: 0 (canonical `action:` syntax used consistently)

## Findings

### [STALE-PATH] Stale module path reference in dashboard_app.qmd
**File:** docs/workflows/dashboard_app.qmd
**Issue:** Line 69 references `app/modules/manifest_navigator.py` which no longer exists.
**Evidence:** Quoted line: `| ManifestNavigator (manifest_navigator.py) | Pure manifest introspection — importable anywhere, zero Shiny dependency. | app/modules/manifest_navigator.py |`. Actual location is `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` (ADR-067).
**Suggested fix:** Update line 69 path to `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py`.
**Cross-ref:** Same finding flagged in propagation audit — fix once.

### [FORBIDDEN-EXAMPLE] Persona IDs with underscores in dashboard_app.qmd
**File:** docs/workflows/dashboard_app.qmd
**Issue:** Line 55 uses `pipeline_static` and `pipeline_exploration_simple` — underscores silently fail all persona gates per `persona_traceability_matrix.md` §CRITICAL.
**Evidence:** `Pipeline Audit (Dark Grey #c0c0c0): Persona-gated — hidden entirely for pipeline_static and pipeline_exploration_simple`.
**Suggested fix:** `pipeline_static` → `pipeline-static`, `pipeline_exploration_simple` → `pipeline-exploration-simple`.

### [DRIFT] Directory naming mismatch in manifest_structure.yaml
**File:** docs/appendix/manifest_structure.yaml
**Issue:** Line 14 names directory `assembly:` but `rules_manifest_structure.md §2` defines the directory as `join/` with top-level key `join_manifests:`.
**Evidence:** Appendix line 14: `assembly: "Contains the assembly recipe file(s) for joining multiple ingredients..."`. Rules file: `'join/': Defines the join recipe ... Top-level manifest key: join_manifests:`.
**Suggested fix:** Update appendix line 14 to use `join:` (or, if the appendix is correct and rules drifted, audit the rules file instead).

### [DRIFT] Persona traceability matrix incomplete (6 of 8 personas)
**File:** `.claude/knowledge/persona_traceability_matrix.md`
**Issue:** Matrix lines 10–15 cover only `pipeline-static`, `pipeline-exploration-simple`, `pipeline-exploration-advanced`, `project-independent`, `developer`, `qa` — `demo-vetinst` and `web-demo` are missing. `docs/user_guide/deployment_personas.qmd` lists all 8 (lines 96–103).
**Suggested fix:** Add rows to the matrix for `demo-vetinst` and `web-demo`, or annotate them explicitly as deferred/proposed.

### [ORPHANED] 8 .qmd files exist but are not referenced from `_quarto.yml`
**Files:**
- docs/appendix/data_flow_analogy.qmd
- docs/appendix/data_lifecycle_theater.qmd
- docs/appendix/user_guide_gallery.qmd
- docs/deployment/deployment_guide.qmd
- docs/reference/troubleshooting.qmd  *(conflict — duplicate of `docs/troubleshooting/index.qmd` which IS in `_quarto.yml`)*
- docs/reference/wrangling_guide.qmd
- docs/user_guide/deployment_personas.qmd
- docs/workflows/ui_persona.qmd  *(linked from `core_architecture_code.qmd:12` but not in nav)*

**Issue:** Files exist with substantive content but are not in the book chapter navigation. Either (a) intentionally archived (annotate), (b) should be added (expand `_quarto.yml`), or (c) should be deleted.
**Suggested fix:** Triage the list — at minimum resolve the troubleshooting duplicate and decide whether `ui_persona.qmd` should be in nav given that other docs already link to it.

## Files spot-checked clean

- docs/foundations/core_architecture.qmd — references `libs/blueprint_arch/` correctly with ADR-067 cite; file paths verified
- docs/user_guide/audit_pipeline.qmd — T3 gating and persona masking accurate
- docs/reference/ui_style_guide.qmd — `config/ui/theme.css` reference correct (ADR-055)

## Notes & deferred findings

1. **Forbidden YAML shorthand check (passed):** No `- mutate:`, `- join:`, or `- sort:` shorthand examples found in docs/. Canonical `action:` syntax is consistently used.
2. **Pedagogical exception:** `docs/troubleshooting/index.qmd:242-245` shows `pipeline_static` as a *wrong example* — that occurrence is pedagogical and not a violation.
3. **`plot_defaults` and `analysis_groups`:** Both appendix and rules document these correctly. No drift in those sections.
4. **Orphaned-file judgement:** Some files (e.g., `data_flow_analogy.qmd`, `data_lifecycle_theater.qmd`) read like preserved reference material — recommend annotating intent rather than auto-deleting.
