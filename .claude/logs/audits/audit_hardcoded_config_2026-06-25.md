# Audit Report: Hardcoded Configuration & Path Violations
Generated: 2026-06-25T21:00:13
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-048 (deployment profile), ADR-031 (bootloader), ADR-053 (no persona name checks)

## Result: ❌ FAIL

- Blockers (must fix): 1
- Known-debt (tracked): 0

## ❌ Absolute Path Strings

**Fix:** Replace with bootloader.get_location(key) or a relative path resolved at runtime.

### `libs/test_lab/src/test_lab/reformatter.py:35`
- **Reason:** Absolute /data/ path
- **Code:** `summary = r.convert_folder("/data/raw", out_dir="/tmp/out")`

## Scan Scope
- Directories scanned: app, libs
- Skipped dirs: .venv, __pycache__, archives, tests, tmp, tmpAI
- Skipped files: base.py, bootloader.py, connector.py, filesystem.py, galaxy.py, galaxy_connector.py, irida.py, local_connector.py

## References
- `ADR-048` — Deployment Profile & Connector Abstraction
- `ADR-031` — Bootloader owns path and persona resolution
- `ADR-053` — No persona name string comparisons in runtime code
- `.claude/rules/rules_runtime_environment.md §1` — venv enforcement
- `.claude/rules/rules_persona_feature_flags.md §Anti-Pattern` — is_enabled() pattern
- `config/deployment/local/local_profile.yaml` — reference for allowed location keys