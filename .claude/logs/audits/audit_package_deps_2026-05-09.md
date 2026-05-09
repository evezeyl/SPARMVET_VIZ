Status: PROCESSED
Triage:
  REAL — importlib_metadata MAJOR (8.7.1 → 9.0.0): transitive dependency. Review release notes before upgrading; test that ingestion/connector imports are unaffected. Low urgency — no direct API usage found in project code.
  ACTION — plotnine PATCH (0.15.3 → 0.15.4): parity mandate package (ADR-036). Per audit_package_deps.py rules: check plotnine 0.15.4 changelog for new API additions that may widen the parity gap. Run parity audit after upgrade. Batch with other PATCH upgrades.
  INFO — shiny PATCH (1.6.0 → 1.6.1), shinychat PATCH (0.3.0 → 0.3.1): UI framework updates. Upgrade in next maintenance window with smoke test (SPARMVET_PERSONA=qa pytest app/tests/test_shiny_smoke.py).
  PASS — No dependency conflicts detected (pip check clean).
# Audit Report: Package Dependency Health
Generated: 2026-05-09T23:18:09
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-035 (Polars Parity), ADR-036 (Artist Parity), ADR-071 (No CDN — vendored assets)

- Outdated packages (real): 13
  - MAJOR updates: 1
  - MINOR updates: 5
  - PATCH updates: 7
- Local editable packages (excluded — false positives): 2
- Dependency conflicts: None
- Parity mandate packages with updates: 1

## Result: ⚠️ REVIEW NEEDED

Exit 1 due to MAJOR update on importlib_metadata. No conflicts.

## Parity Mandate

### plotnine 0.15.3 → 0.15.4 (PATCH)
- ADR-036 Artist Parity Mandate
- Check 0.15.4 changelog for new geoms/stats/scales before upgrading.
- Upgrade command: `.venv/bin/pip install plotnine==0.15.4`
- After upgrade: re-run `audit_parity_coverage.py` to catch new gaps.

## MAJOR Updates (review first)

- `importlib_metadata` 8.7.1 → 9.0.0 — transitive; not directly imported by project code.

## MINOR Updates

- markdown-it-py 4.0.0 → 4.2.0
- mdit-py-plugins 0.5.0 → 0.6.0
- narwhals 2.20.0 → 2.21.0
- urllib3 2.6.3 → 2.7.0
- wcwidth 0.6.0 → 0.7.0

## PATCH Updates (low-risk batch)

- fastexcel 0.20.1 → 0.20.2
- htmltools 0.6.0 → 0.6.1
- orjson 3.11.8 → 3.11.9
- pip 26.1 → 26.1.1
- plotnine 0.15.3 → 0.15.4 (parity mandate — see above)
- shiny 1.6.0 → 1.6.1
- shinychat 0.3.0 → 0.3.1

## References
- Routine 11 (Package dependency health) in `.claude/workflows/audit_routine_registry.md`
- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)
- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)
