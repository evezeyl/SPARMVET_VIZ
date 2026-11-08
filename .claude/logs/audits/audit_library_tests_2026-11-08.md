Status: PROCESSED 2026-11-08 — 1 task created and fixed (id_reconciliation_integrity_suite.py rejected --output, GitHub #41, fixed 9dc2abc), 0 false positives, 0 acceptable debt. Rerun after the fix confirms overall PASS.
# Audit Report: Library Test Infrastructure
Generated: 2026-11-08T20:05:46
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: rules_verification_testing.md §1 — Standardized Test Naming and Architecture

- Libraries assessed: 9
- FULL (all three layers): 2
- PARTIAL (missing one or more layers): 7
- MISSING (no tests at all): 0
- pytest failures: 0
- Integrity suite failures: 1

## Result: FAIL

## Infrastructure Matrix

| Library | pytest files | Integrity Suite | Debug Scripts | Level | pytest | Suite |
|---------|-------------|-----------------|---------------|-------|--------|-------|
| `blueprint_arch` | 4 | 0 | 1 | PARTIAL | PASS | SKIP |
| `connector` | 1 | 0 | 0 | PARTIAL | PASS | SKIP |
| `id_reconciliation` | 4 | 1 | 0 | PARTIAL | PASS | FAIL |
| `ingestion` | 0 | 1 | 1 | PARTIAL | SKIP | PASS |
| `test_lab` | 6 | 0 | 0 | PARTIAL | PASS | SKIP |
| `transformer` | 7 | 1 | 8 | FULL | PASS | PASS |
| `utils` | 3 | 0 | 1 | PARTIAL | PASS | SKIP |
| `viz_factory` | 5 | 1 | 7 | FULL | PASS | PASS |
| `viz_gallery` | 1 | 0 | 2 | PARTIAL | PASS | SKIP |

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
267 passed in 2.69s
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
...........................                                              [100%]
27 passed in 0.07s
```

#### Integrity suite `none`: SKIP

### id_reconciliation

- Level: **PARTIAL**
- pytest files: test_core.py, test_matcher.py, test_pattern_detector.py, test_transformation.py
- Integrity suites: id_reconciliation_integrity_suite.py
- Debug scripts: none
- Missing layers:
  - debug scripts (debug_*.py)

#### pytest: PASS

```
............................                                             [100%]
28 passed in 0.27s
```

#### Integrity suite `id_reconciliation_integrity_suite.py`: FAIL

```
usage: id_reconciliation_integrity_suite.py [-h]
                                            [--module {matcher,pattern_detector,steps,core}]
                                            [--verbose]
id_reconciliation_integrity_suite.py: error: unrecognized arguments: --output /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/audit_lib_tests/id_reconciliation
```

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
 Date: 2026-11-08T20:00:31.611439
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
- pytest files: test_anonymiser.py, test_bootstrapper.py, test_extractor.py, test_reformatter.py, test_scaffolder.py, test_synthesizer.py
- Integrity suites: none
- Debug scripts: none
- Missing layers:
  - integrity suite (*_integrity_suite.py)
  - debug scripts (debug_*.py)

#### pytest: PASS

```
........................................................................ [ 76%]
......................                                                   [100%]
94 passed in 1.20s
```

#### Integrity suite `none`: SKIP

### transformer

- Level: **FULL**
- pytest files: test_data_wrangler.py, test_deterministic_order.py, test_metadata_validator.py, test_replace_values.py, test_top_n_other.py, test_ui_schemas.py, test_validate_types.py
- Integrity suites: transformer_integrity_suite.py
- Debug scripts: debug_assembler.py, debug_decorator_suite.py, debug_expressions.py, debug_phase3_refinements.py, debug_pipeline.py, debug_relational_audit.py, debug_wrangler.py, debug_wrangler_errors.py

#### pytest: PASS

```
........................................................................ [ 31%]
........................................................................ [ 62%]
........................................................................ [ 93%]
...............                                                          [100%]
231 passed in 1.00s
```

#### Integrity suite `transformer_integrity_suite.py`: PASS

```
mn                   | 🟢 PASSED   | Logic Verified (ADR-013)
split_column_to_parts          | 🟢 PASSED   | Logic Verified (ADR-013)
split_to_list                  | 🟢 PASSED   | Logic Verified (ADR-013)
strip_whitespace               | 🟢 PASSED   | Logic Verified (ADR-013)
summarize                      | 🟢 PASSED   | Logic Verified (ADR-013)
to_struct                      | 🟢 PASSED   | Logic Verified (ADR-013)
top_n_other                    | 🟢 PASSED   | Logic Verified (ADR-013)
unique                         | 🟢 PASSED   | Logic Verified (ADR-013)
unique_rows                    | 🟢 PASSED   | Logic Verified (ADR-013)
unnest                         | 🟢 PASSED   | Logic Verified (ADR-013)
unpivot                        | 🟢 PASSED   | Logic Verified (ADR-013)
value_counts                   | 🟢 PASSED   | Logic Verified (ADR-013)
window_agg                     | 🟢 PASSED   | Logic Verified (ADR-013)
z_score                        | 🟢 PASSED   | Logic Verified (ADR-013)

🔗 PHASE 2: RELATIONAL ACTION VERIFICATION
Relational Data analysis recipe | Status     | Details
---------------------------------------------------------------------------
relational_audit               | 🟢 PASSED   | Join/JoinFilter Verified

🏗️  PHASE 3: ASSEMBLY PIPELINE TESTS (Template Data analysis recipes)
Pipeline Data analysis recipe                      | Status
---------------------------------------------------------------------------
[WARNING] Pipeline directory not found. Skipping Layer 2 tests.

[============================================================]
 📊 FINAL INTEGRITY SUMMARY
 Total Registered Actions: 63
 Wrangler Passed:          61
 Wrangler Failed:          0
 Wrangler No Test:        0
 Assembly Pipelines Run:   0
 Assembly Pipelines Pass:  0
[============================================================]

✅ Integrity Report Saved: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/audit_lib_tests/transformer/2026-11-08_transformer_integrity_report.txt
```

### utils

- Level: **PARTIAL**
- pytest files: test_config_loader.py, test_path_expansion.py, test_pipeline_error.py
- Integrity suites: none
- Debug scripts: debug_config_loader.py
- Missing layers:
  - integrity suite (*_integrity_suite.py)

#### pytest: PASS

```
..................................................................       [100%]
66 passed in 0.12s
```

#### Integrity suite `none`: SKIP

### viz_factory

- Level: **FULL**
- pytest files: test_component_schemas.py, test_deco2_components.py, test_plot_config_resolver.py, test_plot_spec_roundtrip.py, test_reproducible_render.py
- Integrity suites: viz_factory_integrity_suite.py
- Debug scripts: debug_audit.py, debug_bulk_sync.py, debug_distiller.py, debug_gallery.py, debug_runner.py, debug_viz_factory_audit.py, debug_viz_factory_tier3.py

#### pytest: PASS

```
........................................................................ [ 30%]
........................................................................ [ 61%]
........................................................................ [ 92%]
.................                                                        [100%]
233 passed in 8.48s
```

#### Integrity suite `viz_factory_integrity_suite.py`: PASS

```
or discipline that produced this output.)
theme_dashboard                     | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_gray                          | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_legend_position               | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_light                         | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_linedraw                      | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_matplotlib                    | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_minimal                       | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_publication                   | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_seaborn                       | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_tufte                         | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_void                          | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
theme_xkcd                          | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
xlab                                | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)
ylab                                | 🔴 FAILED   |  diagnostic-error discipline that produced this output.)

[============================================================]
 📊 FINAL INTEGRITY SUMMARY
 Total Registered Components: 191
 Passed:                      0
 Failed:                      191
 No Test Data:                0
[============================================================]

✅ Integrity Report Saved: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/audit_lib_tests/viz_factory/viz_factory_integrity_report.txt
```

### viz_gallery

- Level: **PARTIAL**
- pytest files: test_gallery_bundle.py
- Integrity suites: none
- Debug scripts: debug_gallery_submission.py, debug_gallery_ui_logic.py
- Missing layers:
  - integrity suite (*_integrity_suite.py)

#### pytest: PASS

```
......                                                                   [100%]
6 passed in 0.30s
```

#### Integrity suite `none`: SKIP

## PARTIAL Libraries (informational — not a blocker)

- `blueprint_arch`: integrity suite (*_integrity_suite.py)
- `connector`: integrity suite (*_integrity_suite.py); debug scripts (debug_*.py)
- `id_reconciliation`: debug scripts (debug_*.py)
- `ingestion`: pytest unit tests (test_*.py)
- `test_lab`: integrity suite (*_integrity_suite.py); debug scripts (debug_*.py)
- `utils`: integrity suite (*_integrity_suite.py)
- `viz_gallery`: integrity suite (*_integrity_suite.py)

PARTIAL is informational only. File a `@dasharch` handoff in `tasks.md` to
add missing layers when time allows. See `rules_verification_testing.md §1`.

## Test Failures

- `id_reconciliation`: integrity suite exited 2

## References
- `.claude/rules/rules_verification_testing.md §1` — Standardized Test Naming and Architecture
- `.claude/rules/rules_verification_testing.md §3` — @verify Protocol and Phase-Gating
- `.claude/rules/rules_verification_testing.md §7` — Failure Test Mandate (ADR-034)
- `.claude/workflows/audit_routine_registry.md` — scheduled audit registry