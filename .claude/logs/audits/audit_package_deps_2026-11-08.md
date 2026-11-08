Status: PROCESSED 2026-11-08 — 0 tasks created (already tracked as GitHub #20/#35, dependency review, deliberately separate scope), 0 false positives, 1 acceptable debt noted (61 outdated packages, 11 major — tracked, not urgent).
# Audit Report: Package Dependency Health
Generated: 2026-11-08T20:00:19
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-035 (Polars Parity), ADR-036 (Artist Parity), ADR-071 (No CDN — vendored assets)

- Outdated packages (real): 61
  - MAJOR updates: 11
  - MINOR updates: 39
  - PATCH updates: 11
- Local editable packages (excluded — false positives): 2
- Dependency conflicts: ✅ None
- Parity mandate packages with updates: 2

## ✅ No Dependency Conflicts

`pip check` reports no incompatibilities.

## ⚠️ Parity Mandate Packages With Updates

### `plotnine` 0.15.4 → 0.15.9 (PATCH)
- **ADR:** ADR-036
- **Registry:** `libs/viz_factory/src/viz_factory/`
- **Rule:** `rules_viz_factory.md §1 — The Artist Parity Mandate`
- **Action required:** New Plotnine release may add new geoms, stats, scales, or themes. Run a VizFactory component inventory audit to identify gaps.
- Check the [plotnine changelog](https://github.com/has2k1/plotnine/releases) for new API additions since 0.15.4.

### `polars` 1.40.1 → 2.1.0 (MAJOR)
- **ADR:** ADR-035
- **Registry:** `libs/transformer/src/transformer/actions/`
- **Rule:** `rules_data_engine.md §5 — The Polars Parity Mandate`
- **Action required:** New Polars release may expose new expressions or functions. Run a transformer action inventory audit to identify gaps.
- Check the [polars changelog](https://github.com/pola-rs/polars/releases) for new API additions since 1.40.1.

## 🔴 MAJOR Updates (review before upgrading)

- `importlib_metadata` **8.7.1 → 10.1.0** — declared by: SPARMVET_VIZ
- `pillow` **12.2.0 → 13.0.0** — declared by: (root or transitive)
- `polars` **1.40.1 → 2.1.0** — declared by: app, connector, id_reconciliation, ingestion, test_lab, transformer, utils, viz_factory, viz_gallery, SPARMVET_VIZ
- `polars-runtime-32` **1.40.1 → 2.1.0** — declared by: (root or transitive)
- `pyarrow` **24.0.0 → 26.0.1** — declared by: transformer, SPARMVET_VIZ
- `pyee` **13.0.1 → 16.0.1** — declared by: (root or transitive)
- `python-dateutil` **2.9.0.post0 → 4.0.0** — declared by: (root or transitive)
- `python-slugify` **8.0.4 → 9.1.3** — declared by: (root or transitive)
- `setuptools` **82.0.1 → 84.2.1** — declared by: (root or transitive)
- `websockets` **16.0 → 17.4** — declared by: (root or transitive)
- `zipp` **3.23.1 → 4.1.2** — declared by: (root or transitive)

MAJOR updates may contain breaking API changes. Review the release notes before upgrading.
Test locally: `pip install <package>==<latest>` then run the full test suite.

## 🟡 MINOR Updates (feature additions — consider upgrading)

- `anyio` 4.13.0 → 4.16.0 — declared by: (root or transitive)
- `asgiref` 3.11.1 → 3.13.0 — declared by: (root or transitive)
- `certifi` 2026.4.22 → 2026.10.23 — declared by: (root or transitive)
- `charset-normalizer` 3.4.7 → 3.5.2 — declared by: (root or transitive)
- `click` 8.3.3 → 8.5.1 — declared by: (root or transitive)
- `contourpy` 1.3.3 → 1.4.0 — declared by: (root or transitive)
- `fastexcel` 0.20.1 → 0.21.0 — declared by: ingestion, SPARMVET_VIZ
- `fonttools` 4.62.1 → 4.68.0 — declared by: (root or transitive)
- `htmltools` 0.6.0 → 0.7.0 — declared by: (root or transitive)
- `idna` 3.13 → 3.20 — declared by: (root or transitive)
- `linkify-it-py` 2.1.0 → 2.2.0 — declared by: (root or transitive)
- `markdown-it-py` 4.0.0 → 4.2.0 — declared by: (root or transitive)
- `matplotlib` 3.10.9 → 3.11.2 — declared by: (root or transitive)
- `mdit-py-plugins` 0.5.0 → 0.6.1 — declared by: (root or transitive)
- `narwhals` 2.20.0 → 2.28.0 — declared by: (root or transitive)
- `numpy` 2.4.4 → 2.5.4 — declared by: test_lab, SPARMVET_VIZ
- `opentelemetry-api` 1.41.1 → 1.45.2 — declared by: (root or transitive)
- `orjson` 3.11.8 → 3.13.0 — declared by: (root or transitive)
- `packaging` 26.2 → 26.3 — declared by: (root or transitive)
- `pandas` 3.0.2 → 3.1.1 — declared by: app, viz_factory, SPARMVET_VIZ
- `pip` 26.1 → 26.3 — declared by: (root or transitive)
- `platformdirs` 4.9.6 → 4.14.5 — declared by: (root or transitive)
- `playwright` 1.59.0 → 1.64.1 ⚠️ — declared by: (root or transitive)
- `pluggy` 1.6.0 → 1.7.0 — declared by: (root or transitive)
- `Pygments` 2.20.0 → 2.21.0 — declared by: (root or transitive)
- `pytest` 9.0.3 → 9.2.0 — declared by: (root or transitive)
- `pytest-playwright` 0.7.2 → 0.10.0 ⚠️ — declared by: (root or transitive)
- `requests` 2.33.1 → 2.34.2 — declared by: connector, SPARMVET_VIZ
- `scipy` 1.17.1 → 1.18.1 — declared by: (root or transitive)
- `shiny` 1.6.0 → 1.9.0 ⚠️ — declared by: app, SPARMVET_VIZ
- `shinychat` 0.3.0 → 0.7.2 ⚠️ — declared by: (root or transitive)
- `starlette` 1.0.0 → 1.10.0 — declared by: (root or transitive)
- `statsmodels` 0.14.6 → 0.15.0 — declared by: (root or transitive)
- `typing_extensions` 4.15.0 → 4.16.0 — declared by: (root or transitive)
- `urllib3` 2.6.3 → 2.8.0 — declared by: (root or transitive)
- `uvicorn` 0.46.0 → 0.54.0 — declared by: (root or transitive)
- `watchfiles` 1.1.1 → 1.3.0 — declared by: (root or transitive)
- `wcwidth` 0.6.0 → 0.9.4 — declared by: (root or transitive)
- `wheel` 0.47.0 → 0.48.0 — declared by: (root or transitive)

## 🟢 PATCH Updates (bug fixes — recommended)

- `greenlet` 3.5.0 → 3.5.6 — declared by: (root or transitive)
- `iniconfig` 2.3.0 → 2.3.1 — declared by: (root or transitive)
- `kiwisolver` 1.5.0 → 1.5.1 — declared by: (root or transitive)
- `MarkupSafe` 3.0.3 → 3.0.4 — declared by: (root or transitive)
- `mizani` 0.14.4 → 0.14.6 — declared by: (root or transitive)
- `patsy` 1.0.2 → 1.0.3 — declared by: (root or transitive)
- `plotnine` 0.15.4 → 0.15.9 ⚠️ — declared by: viz_factory, SPARMVET_VIZ
- `prompt_toolkit` 3.0.52 → 3.0.53 — declared by: (root or transitive)
- `pyparsing` 3.3.2 → 3.3.3 — declared by: (root or transitive)
- `python-multipart` 0.0.27 → 0.0.33 — declared by: (root or transitive)
- `RapidFuzz` 3.14.5 → 3.14.6 — declared by: id_reconciliation

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
.venv/bin/pip install --upgrade greenlet iniconfig kiwisolver MarkupSafe mizani
# Verify no regressions
.venv/bin/python -c 'from app.src.main import app; print("import OK")'
PYTHONPATH=. SPARMVET_APP_FEATURES=qa .venv/bin/python -m pytest app/tests/test_filter_operators.py -q
```

**For MINOR / MAJOR updates (one at a time):**
```bash
# Update one package
.venv/bin/pip install '<package>==<latest>'
# Run full smoke tests
PYTHONPATH=. SPARMVET_APP_FEATURES=qa .venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v
# If parity mandate package: run action/component inventory audit
.venv/bin/python scripts/audit_library_tests.py --lib transformer  # or viz_factory
```

## References
- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)
- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)
- `rules_verification_testing.md §8` — Playwright smoke testing after updates
- Routine 11 (Package dependency health) in `.claude/workflows/audit_routine_registry.md`