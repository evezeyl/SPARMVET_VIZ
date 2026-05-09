Status: PROCESSED
Triage:
  STALE — libs/viz_factory/README.md: component count claims 175, actual is 195 (off by 20; pre-dates DECO-2 additions April 30). Informational — count drifts naturally with new registrations. No task; update at next viz_factory sprint.
  STALE — libs/ingestion/README.md: ExcelHandler documented as class (ExcelHandler (excel_handler.py)) but implemented as CLI script only (main() function, no class). Real semantic drift — the class interface described in the README does not exist. Task filed: DOC-GAP-5.
  STALE — libs/transformer/README.md: references "Comparison Theater" feature that is not implemented. Appears to be aspirational doc language from design phase. Task filed: DOC-GAP-5 (bundle with ExcelHandler fix).
  CURRENT — transformer: DataWrangler, DataAssembler, PipelineExecutor, MetadataValidator, Action Registry, Short-Circuit logic all match implementation.
  CURRENT — viz_factory: render() filters, auto axis label adjustment — both accurate.
  CURRENT — connector: all 4 connector classes, deployment_type routing — accurate.
  CURRENT — blueprint_arch: ManifestNavigator, BlueprintMapper, schema_registry — all accurate.
# Audit Report: Semantic Documentation Sync
Generated: 2026-05-09
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Routine: 17 — Agent-based

## Summary
- Libs audited: 5 (transformer, viz_factory, ingestion, connector, blueprint_arch)
- CURRENT: 12 claims
- STALE: 3 claims
- MISSING: 0

## Findings

### libs/viz_factory/README.md

#### Claim: "175 Components Registered; Pass Rate: 98% (172/175 Passed)"
**Status:** STALE
**Evidence:** `@register_plot_component` count = 195 in source
**Note:** Count predates DECO-2 additions (2026-04-30). Informational — no task filed; update at next viz_factory sprint.

#### Claim: "IntegritySuite audits all 193+ registered components"
**Status:** STALE (same root cause)
**Note:** Bundled with above.

### libs/ingestion/README.md

#### Claim: "ExcelHandler (excel_handler.py): Authoritative normalisation engine... Extracts each sheet to a standardised TSV..."
**Status:** STALE
**Evidence:** `libs/ingestion/src/ingestion/excel_handler.py` contains only a `main()` CLI function — no `ExcelHandler` class
**Note:** README documents a class interface that doesn't exist. This is real semantic drift — any developer reading this will expect a class they can import. Filed in DOC-GAP-5.

### libs/transformer/README.md

#### Claim: "Reactive State (Tier 3): supports side-by-side inspection in the Comparison Theater"
**Status:** STALE
**Evidence:** "Comparison Theater" terminology not found in source code (search: app/handlers/, app/modules/)
**Note:** This is aspirational language from the design phase. T3 predicate pushdown exists but "Comparison Theater" as a named entity does not. Filed in DOC-GAP-5.

## Clean — All Claims Current

- transformer: DataWrangler, DataAssembler, PipelineExecutor, MetadataValidator, Action Registry, Short-Circuit Guard
- viz_factory: render() filter injection, auto axis label adjustment
- connector: all 4 connector classes, deployment_type routing, Phase 23-B status
- blueprint_arch: ManifestNavigator (all 7 public functions), BlueprintMapper, schema_registry, deferred imports

## References
- Routine 17 (Semantic doc sync) in `.claude/workflows/audit_routine_registry.md`
- `rules_documentation_aesthetics.md §1` — Code-Documentation Synchronization Mandate
