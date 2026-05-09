Status: PROCESSED
Triage:
  REAL — blueprint_arch: 188 pytest failures in test_schema_registry.py. Tests check for `allow_extra_params` and `wraps` fields in ui_schema (ADR-075 Blueprint IDE). Component registrations in viz_factory are missing these fields. Task filed: LIB-TESTS-BLUEPRINT-1.
  REAL — viz_factory integrity suite: TIMEOUT at 120s. Suite renders all registered components and exceeds the script timeout. Task filed: LIB-TESTS-VIZ-TIMEOUT-1 (increase timeout in audit_library_tests.py or add --timeout flag).
  INVESTIGATE — transformer integrity suite: Reports PASS (exit 0) but internally shows 60/62 wrangler actions as FAILED via ADR-078 diagnostic-error discipline. Actions are being tested without their expected test TSV data, triggering the new fatal diagnostic errors. Suite exits 0 because the diagnostic-error is the designed behavior (ADR-078 §3: "Fail loud, fail early"). Filed as informational note; the suite output format pre-dates ADR-078 and should be updated — task filed: LIB-TESTS-TRANSFORMER-SUITE-1.
  INFO — 6/8 libraries are PARTIAL coverage (no integrity suite or no pytest). Not blockers. Informational tasks filed under existing PARTIAL enhancement list.
# Audit Report: Library Test Infrastructure
Generated: 2026-05-09T23:20:35
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: rules_verification_testing.md §1 — Standardized Test Naming and Architecture

- Libraries assessed: 8
- FULL (all three layers): 2
- PARTIAL (missing one or more layers): 6
- MISSING (no tests at all): 0
- pytest failures: 1
- Integrity suite failures: 1

## Result: FAIL

## Infrastructure Matrix

| Library | pytest files | Integrity Suite | Debug Scripts | Level | pytest | Suite |
|---------|-------------|-----------------|---------------|-------|--------|-------|
| `blueprint_arch` | 2 | 0 | 1 | PARTIAL | FAIL | SKIP |
| `connector` | 1 | 0 | 0 | PARTIAL | PASS | SKIP |
| `ingestion` | 0 | 1 | 1 | PARTIAL | SKIP | PASS |
| `test_lab` | 0 | 0 | 3 | PARTIAL | SKIP | SKIP |
| `transformer` | 1 | 1 | 8 | FULL | PASS | PASS* |
| `utils` | 0 | 0 | 2 | PARTIAL | SKIP | SKIP |
| `viz_factory` | 2 | 1 | 7 | FULL | PASS | FAIL |
| `viz_gallery` | 0 | 0 | 2 | PARTIAL | SKIP | SKIP |

*transformer integrity suite exits 0 but reports 60/62 actions FAILED internally — see triage note above.

## Failure Details

### blueprint_arch — pytest FAIL (188 failures)

`test_schema_registry.py::TestComponentCatalog` tests check:
- `test_component_has_allow_extra_params[<geom>]` — missing `allow_extra_params` field
- `test_component_has_wraps[<geom>]` — missing `wraps` field
- `test_geom_categories_are_semantic` — geom category validation
- `test_plot_context_filter` — context filter validation

Root cause: ADR-075 Blueprint IDE requires `ui_schema` with `allow_extra_params` and `wraps` fields in `@register_plot_component` decorators. These fields are not yet present in viz_factory component registrations.

### viz_factory — integrity suite TIMEOUT

Suite exceeds 120s hard limit in audit_library_tests.py. Suite renders all 193 registered components — rendering time scales with component count. Short-term fix: increase timeout in the audit script to 300s.

## PARTIAL Libraries (informational — not a blocker)

- `blueprint_arch`: integrity suite
- `connector`: integrity suite; debug scripts
- `ingestion`: pytest unit tests
- `test_lab`: pytest unit tests; integrity suite
- `utils`: pytest unit tests; integrity suite
- `viz_gallery`: pytest unit tests; integrity suite

## References
- `.claude/rules/rules_verification_testing.md §1`
- Routine 10 (Library test coverage) in `.claude/workflows/audit_routine_registry.md`
