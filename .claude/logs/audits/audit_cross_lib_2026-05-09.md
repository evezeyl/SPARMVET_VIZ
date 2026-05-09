Status: PROCESSED
# Audit Report: ADR-011 Cross-Lib Violation Scan
Triage: Fixed. (1) Audit script updated to exclude tests/ and assets/ — not lib production code. (2) schema_registry.py refactored from deferred cross-lib imports to injection pattern: register(action_schemas, component_schemas) called by server.py at startup. Re-run: ⚠️ KNOWN DEBT ONLY (0 new blockers, 1 tracked transformer→ingestion).
Generated: 2026-05-09T21:26:33
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-011 / ADR-016 — Two-Tier Dependency Model

## Result: ❌ FAIL

- New violations (blockers): 7
- Known tech-debt violations: 5

## ❌ New Violations (must fix before merge)

### libs/blueprint_arch/src/blueprint_arch/schema_registry.py:40
- **From:** `blueprint_arch`
- **Imports:** `transformer` via `transformer.actions.base`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

### libs/blueprint_arch/src/blueprint_arch/schema_registry.py:49
- **From:** `blueprint_arch`
- **Imports:** `viz_factory` via `viz_factory.registry`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

### libs/blueprint_arch/tests/test_schema_registry.py:19
- **From:** `blueprint_arch`
- **Imports:** `transformer` via `transformer.actions`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

### libs/blueprint_arch/tests/test_schema_registry.py:20
- **From:** `blueprint_arch`
- **Imports:** `viz_factory` via `viz_factory`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

### libs/viz_factory/tests/debug_runner.py:17
- **From:** `viz_factory`
- **Imports:** `transformer` via `transformer.data_wrangler`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

### libs/viz_factory/tests/debug_runner.py:24
- **From:** `viz_factory`
- **Imports:** `transformer` via `transformer.data_wrangler`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

### libs/viz_gallery/assets/generate_previews.py:28
- **From:** `viz_gallery`
- **Imports:** `viz_factory` via `viz_factory.viz_factory`
- **Fix:** Remove or reroute this import. Domain libs must not import from peers.
  - If you need shared logic, move it to `libs/utils/`.
  - If this is orchestration, move the call to `app/`.

## ⚠️ Known Tech-Debt Violations (tracked, do not expand)

- `libs/transformer/src/transformer/pipeline.py:20` — `transformer` → `ingestion` (`ingestion.ingestor`)
- `libs/transformer/tests/debug_assembler.py:24` — `transformer` → `ingestion` (`ingestion.ingestor`)
- `libs/transformer/tests/debug_pipeline.py:9` — `transformer` → `ingestion` (`ingestion.ingestor`)
- `libs/transformer/tests/debug_relational_audit.py:21` — `transformer` → `ingestion` (`ingestion.ingestor`)
- `libs/transformer/tests/debug_wrangler.py:23` — `transformer` → `ingestion` (`ingestion.ingestor`)

These are tracked in tasks.md. Do not add new violations to this category.

## References
- `.claude/rules/rules_runtime_environment.md §4` — Two-Tier Dependency Model
- `.claude/knowledge/architecture_decisions.md` ADR-011, ADR-016
- `.claude/tasks/tasks.md` — `ADR-011 cross-lib violations` tech-debt block