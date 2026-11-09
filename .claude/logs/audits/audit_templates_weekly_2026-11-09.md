Status: PROCESSED 2026-11-09 — 0 tasks created, 0 false positives skipped, 0 acceptable debt noted (PASS; also fixed a stale script filename this run was blocked on — run_audits.sh and the script's own docstring still said audit_template_flags.py after the ADR-091 rename to audit_app_features_flags.py)
# Audit Report: App features Template Flag Completeness
Generated: 2026-11-09T17:39:33
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: rules_app_features_flags.md — Authoritative flag matrix, cascade enforcement
Validator: AppFeaturesValidator + SidebarValidator (strict mode — warnings treated as errors)

- Templates validated: 8
- Passed: 8
- Failed: 0

## Result: ✅ PASS

All app features files pass strict validation.

## ✅ Templates Passing

- `demo-vetinst`
- `developer`
- `pipeline-exploration-advanced`
- `pipeline-exploration-simple`
- `pipeline-static`
- `qa`
- `standalone`
- `web-demo`

## References
- `.claude/rules/rules_app_features_flags.md` — authoritative flag matrix
- `scripts/validate_app_features_config.py` — validator CLI
- `config/app_features/` — all app features files
- Routine 8 (Template flag completeness) in `.claude/workflows/audit_routine_registry.md`