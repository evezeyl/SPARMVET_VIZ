Status: PROCESSED
# Audit Report: Package Dependency Health
Generated: 2026-05-21T16:09:54
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-035 (Polars Parity), ADR-036 (Artist Parity), ADR-071 (No CDN — vendored assets)

- Outdated packages (real): 27
  - MAJOR updates: 2
  - MINOR updates: 15
  - PATCH updates: 10
- Local editable packages (excluded — false positives): 2
- Dependency conflicts: ✅ None
- Parity mandate packages with updates: 0

## ✅ No Dependency Conflicts

`pip check` reports no incompatibilities.

## 🔴 MAJOR Updates (review before upgrading)

- `importlib_metadata` **8.7.1 → 9.0.0** — declared by: SPARMVET_VIZ
- `zipp` **3.23.1 → 4.1.0** — declared by: (root or transitive)

MAJOR updates may contain breaking API changes. Review the release notes before upgrading.
Test locally: `pip install <package>==<latest>` then run the full test suite.

## 🟡 MINOR Updates (feature additions — consider upgrading)

- `certifi` 2026.4.22 → 2026.5.20 — declared by: (root or transitive)
- `click` 8.3.3 → 8.4.0 — declared by: (root or transitive)
- `fonttools` 4.62.1 → 4.63.0 — declared by: (root or transitive)
- `idna` 3.13 → 3.15 — declared by: (root or transitive)
- `markdown-it-py` 4.0.0 → 4.2.0 — declared by: (root or transitive)
- `mdit-py-plugins` 0.5.0 → 0.6.1 — declared by: (root or transitive)
- `narwhals` 2.20.0 → 2.21.2 — declared by: (root or transitive)
- `opentelemetry-api` 1.41.1 → 1.42.0 — declared by: (root or transitive)
- `playwright` 1.59.0 → 1.60.0 ⚠️ — declared by: (root or transitive)
- `pytest-playwright` 0.7.2 → 0.8.0 ⚠️ — declared by: (root or transitive)
- `requests` 2.33.1 → 2.34.2 — declared by: connector, SPARMVET_VIZ
- `urllib3` 2.6.3 → 2.7.0 — declared by: (root or transitive)
- `uvicorn` 0.46.0 → 0.47.0 — declared by: (root or transitive)
- `watchfiles` 1.1.1 → 1.2.0 — declared by: (root or transitive)
- `wcwidth` 0.6.0 → 0.7.0 — declared by: (root or transitive)

## 🟢 PATCH Updates (bug fixes — recommended)

- `fastexcel` 0.20.1 → 0.20.2 — declared by: ingestion, SPARMVET_VIZ
- `greenlet` 3.5.0 → 3.5.1 — declared by: (root or transitive)
- `htmltools` 0.6.0 → 0.6.1 — declared by: (root or transitive)
- `numpy` 2.4.4 → 2.4.6 — declared by: test_lab, SPARMVET_VIZ
- `orjson` 3.11.8 → 3.11.9 — declared by: (root or transitive)
- `pandas` 3.0.2 → 3.0.3 — declared by: app, viz_factory, SPARMVET_VIZ
- `pip` 26.1 → 26.1.1 — declared by: (root or transitive)
- `python-multipart` 0.0.27 → 0.0.29 — declared by: (root or transitive)
- `shiny` 1.6.0 → 1.6.1 ⚠️ — declared by: app, SPARMVET_VIZ
- `shinychat` 0.3.0 → 0.3.1 ⚠️ — declared by: (root or transitive)

Patch updates typically contain only bug fixes and are low-risk to apply.
Upgrade in a batch: `pip install <p1> <p2> ... --upgrade` then re-run tests.

## ℹ️ Local Packages (excluded — editable installs)

These appear in `pip list --outdated` because a PyPI package of the same name exists.
They are local editable installs and do not need updating via pip.

- `test_lab` (local editable — ignoring PyPI version 0.11)
- `utils` (local editable — ignoring PyPI version 1.0.2)

## Upgrade Protocol

**For PATCH updates (batch upgrade):**
```bash
# Upgrade low-risk packages together
.venv/bin/pip install --upgrade fastexcel greenlet htmltools numpy orjson
# Verify no regressions
.venv/bin/python -c 'from app.src.main import app; print("import OK")'
PYTHONPATH=. SPARMVET_PERSONA=qa .venv/bin/python -m pytest app/tests/test_filter_operators.py -q
```

**For MINOR / MAJOR updates (one at a time):**
```bash
# Update one package
.venv/bin/pip install '<package>==<latest>'
# Run full smoke tests
PYTHONPATH=. SPARMVET_PERSONA=qa .venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v
# If parity mandate package: run action/component inventory audit
.venv/bin/python scripts/audit_library_tests.py --lib transformer  # or viz_factory
```

## References
- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)
- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)
- `rules_verification_testing.md §8` — Playwright smoke testing after updates
- Routine 11 (Package dependency health) in `.claude/workflows/audit_routine_registry.md`