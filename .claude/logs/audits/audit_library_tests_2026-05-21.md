Status: PROCESSED
# Audit Report: Library Test Infrastructure
Generated: 2026-05-21T16:15:43
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: rules_verification_testing.md §1 — Standardized Test Naming and Architecture

- Libraries assessed: 8
- FULL (all three layers): 2
- PARTIAL (missing one or more layers): 6
- MISSING (no tests at all): 0
- pytest failures: 0
- Integrity suite failures: 1

## Result: FAIL

## Infrastructure Matrix

| Library | pytest files | Integrity Suite | Debug Scripts | Level | pytest | Suite |
|---------|-------------|-----------------|---------------|-------|--------|-------|
| `blueprint_arch` | 4 | 0 | 1 | PARTIAL | PASS | SKIP |
| `connector` | 1 | 0 | 0 | PARTIAL | PASS | SKIP |
| `ingestion` | 0 | 1 | 1 | PARTIAL | SKIP | PASS |
| `test_lab` | 0 | 0 | 3 | PARTIAL | SKIP | SKIP |
| `transformer` | 1 | 1 | 8 | FULL | PASS | PASS |
| `utils` | 1 | 0 | 2 | PARTIAL | PASS | SKIP |
| `viz_factory` | 4 | 1 | 7 | FULL | PASS | FAIL |
| `viz_gallery` | 0 | 0 | 2 | PARTIAL | SKIP | SKIP |

## Per-Library Details

### blueprint_arch

- Level: **PARTIAL**
- pytest files: test_group_plot_manager.py, test_join_designer.py, test_lineage_nav.py, test_schema_registry.py
- Integrity suites: none
- Debug scripts: debug_blueprint_mapper.py
- Missing layers:
  - integrity suite (*_integrity_suite.py)

#### pytest: PASS

```
........................................................................ [ 26%]
........................................................................ [ 53%]
........................................................................ [ 80%]
...................................................                      [100%]
267 passed in 3.32s
```

#### Integrity suite `none`: SKIP

### connector

- Level: **PARTIAL**
- pytest files: test_connectors.py
- Integrity suites: none
- Debug scripts: none
- Missing layers:
  - integrity suite (*_integrity_suite.py)
  - debug scripts (debug_*.py)

#### pytest: PASS

```
...............................                                          [100%]
31 passed in 0.14s
```

#### Integrity suite `none`: SKIP

### ingestion

- Level: **PARTIAL**
- pytest files: none
- Integrity suites: ingestion_integrity_suite.py
- Debug scripts: debug_ingestor.py
- Missing layers:
  - pytest unit tests (test_*.py)

#### pytest: SKIP

```
No pytest files found — skipped
```

#### Integrity suite `ingestion_integrity_suite.py`: PASS

```
[============================================================]
 🛡️  INGESTION MASTER INTEGRITY SUITE
 Date: 2026-05-21T16:10:06.789361
[============================================================]

🧪 Test 1: Legacy Discovery (TSV)
🟢 PASSED: Loaded TSV via discovery
🧪 Test 2: Explicit Source (TSV)
🟢 PASSED: Renamed and Cast (numeric)
🧪 Test 3: Explicit Source (Parquet)
🟢 PASSED: Loaded Parquet and Cast (categorical)
🧪 Test 4: Case-Insensitive Rename
🟢 PASSED: Case-insensitive match success

[============================================================]
 ✅ Ingestion Integrity Check Complete.
[============================================================]
```

### test_lab

- Level: **PARTIAL**
- pytest files: none
- Integrity suites: none
- Debug scripts: debug_ambiguity.py, debug_reconciler.py, debug_sdk.py
- Missing layers:
  - pytest unit tests (test_*.py)
  - integrity suite (*_integrity_suite.py)

#### pytest: SKIP

```
No pytest files found — skipped
```

#### Integrity suite `none`: SKIP

### transformer

- Level: **FULL**
- pytest files: test_ui_schemas.py
- Integrity suites: transformer_integrity_suite.py
- Debug scripts: debug_assembler.py, debug_decorator_suite.py, debug_expressions.py, debug_phase3_refinements.py, debug_pipeline.py, debug_relational_audit.py, debug_wrangler.py, debug_wrangler_errors.py

#### pytest: PASS

```
........................................................................ [ 42%]
........................................................................ [ 85%]
........................                                                 [100%]
168 passed in 0.48s
```

#### Integrity suite `transformer_integrity_suite.py`: PASS

```
3)
split_and_explode              | 🟢 PASSED   | Logic Verified (ADR-013)
split_column                   | 🟢 PASSED   | Logic Verified (ADR-013)
split_column_to_parts          | 🟢 PASSED   | Logic Verified (ADR-013)
split_to_list                  | 🟢 PASSED   | Logic Verified (ADR-013)
strip_whitespace               | 🟢 PASSED   | Logic Verified (ADR-013)
summarize                      | 🟢 PASSED   | Logic Verified (ADR-013)
to_struct                      | 🟢 PASSED   | Logic Verified (ADR-013)
unique                         | 🟢 PASSED   | Logic Verified (ADR-013)
unique_rows                    | 🟢 PASSED   | Logic Verified (ADR-013)
unnest                         | 🟢 PASSED   | Logic Verified (ADR-013)
unpivot                        | 🟢 PASSED   | Logic Verified (ADR-013)
value_counts                   | 🟢 PASSED   | Logic Verified (ADR-013)
window_agg                     | 🟢 PASSED   | Logic Verified (ADR-013)
z_score                        | 🟢 PASSED   | Logic Verified (ADR-013)

🔗 PHASE 2: RELATIONAL ACTION VERIFICATION
Relational Manifest            | Status     | Details
---------------------------------------------------------------------------
relational_audit               | 🟢 PASSED   | Join/JoinFilter Verified

🏗️  PHASE 3: ASSEMBLY PIPELINE TESTS (Template Manifests)
Pipeline Manifest                                  | Status
---------------------------------------------------------------------------
[WARNING] Pipeline directory not found. Skipping Layer 2 tests.

[============================================================]
 📊 FINAL INTEGRITY SUMMARY
 Total Registered Actions: 62
 Wrangler Passed:          60
 Wrangler Failed:          0
 Wrangler No Test:        0
 Assembly Pipelines Run:   0
 Assembly Pipelines Pass:  0
[============================================================]

✅ Integrity Report Saved: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/audit_lib_tests/transformer/2026-05-21_transformer_integrity_report.txt
```

### utils

- Level: **PARTIAL**
- pytest files: test_pipeline_error.py
- Integrity suites: none
- Debug scripts: debug_config_loader.py, debug_gallery_submission.py
- Missing layers:
  - integrity suite (*_integrity_suite.py)

#### pytest: PASS

```
.......................................................                  [100%]
55 passed in 0.08s
```

#### Integrity suite `none`: SKIP

### viz_factory

- Level: **FULL**
- pytest files: test_component_schemas.py, test_deco2_components.py, test_plot_config_resolver.py, test_plot_spec_roundtrip.py
- Integrity suites: viz_factory_integrity_suite.py
- Debug scripts: debug_audit.py, debug_bulk_sync.py, debug_distiller.py, debug_gallery.py, debug_runner.py, debug_viz_factory_audit.py, debug_viz_factory_tier3.py

#### pytest: PASS

```
........................................................................ [ 32%]
........................................................................ [ 65%]
........................................................................ [ 98%]
...                                                                      [100%]
219 passed in 3.12s
```

#### Integrity suite `viz_factory_integrity_suite.py`: FAIL

```
TIMEOUT — integrity suite exceeded 300s
```

### viz_gallery

- Level: **PARTIAL**
- pytest files: none
- Integrity suites: none
- Debug scripts: debug_gallery_submission.py, debug_gallery_ui_logic.py
- Missing layers:
  - pytest unit tests (test_*.py)
  - integrity suite (*_integrity_suite.py)

#### pytest: SKIP

```
No pytest files found — skipped
```

#### Integrity suite `none`: SKIP

## PARTIAL Libraries (informational — not a blocker)

- `blueprint_arch`: integrity suite (*_integrity_suite.py)
- `connector`: integrity suite (*_integrity_suite.py); debug scripts (debug_*.py)
- `ingestion`: pytest unit tests (test_*.py)
- `test_lab`: pytest unit tests (test_*.py); integrity suite (*_integrity_suite.py)
- `utils`: integrity suite (*_integrity_suite.py)
- `viz_gallery`: pytest unit tests (test_*.py); integrity suite (*_integrity_suite.py)

PARTIAL is informational only. File a `@dasharch` handoff in `tasks.md` to
add missing layers when time allows. See `rules_verification_testing.md §1`.

## Test Failures

- `viz_factory`: integrity suite exited 1

## References
- `.claude/rules/rules_verification_testing.md §1` — Standardized Test Naming and Architecture
- `.claude/rules/rules_verification_testing.md §3` — @verify Protocol and Phase-Gating
- `.claude/rules/rules_verification_testing.md §7` — Failure Test Mandate (ADR-034)
- `.claude/workflows/audit_routine_registry.md` — scheduled audit registry