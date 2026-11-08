Status: PROCESSED 2026-11-08 — all clean, no action needed (ADR-094 HOME load gate sweep)

# Audit Report: Hardcoded Configuration & Path Violations
Generated: 2026-11-08T10:44:55
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-048 (deployment), ADR-031 (bootloader), ADR-053 (no app features name checks)

## Result: ✅ PASS

- Blockers (must fix): 0
- Known-debt (tracked): 0

## Scan Scope
- Directories scanned: app, libs
- Skipped dirs: .venv, __pycache__, archives, tests, tmp, tmpAI
- Skipped files: base.py, bootloader.py, connector.py, filesystem.py, galaxy.py, galaxy_connector.py, irida.py, local.py, renamed_keys.py

## References
- `ADR-048` — Deployment & Connector Abstraction
- `ADR-031` — Bootloader owns path and app features resolution
- `ADR-053` — No app features name string comparisons in runtime code
- `.claude/rules/rules_runtime_environment.md §1` — venv enforcement
- `.claude/rules/rules_app_features_flags.md §Anti-Pattern` — is_enabled() pattern
- `config/deployment/local/local.yaml` — reference for allowed location keys