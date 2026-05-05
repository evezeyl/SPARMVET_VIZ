---
description: The Master Gate for UI and Manifest Integration Testing
---
# 🖥️ UI Manifest Integration Testing (The Master Gate)

## Authority

This workflow acts as the final overarching **Phase-Gate** ensuring visual integration does not crash due to backend failures.

## Requirement (Headless-First)

Execution of any UI integration tests (e.g. via `app/src/main.py` or Shiny live previews) is **STRICTLY PROHIBITED** until the required headless workflows have successfully cleared their Proof of Life audits:

- ✅ *Ingestion Audit Passed*
- ✅ *Transformer/Assembler Audit Passed*
- ✅ *Viz Factory Audit Passed*

## Validation Steps

1. Verify that all dependencies have generated their verified Headless test artifacts inside `tmp/Manifest_test/{manifest_basename}/`.
2. Confirm the `@verify` of the Headless testing loops has been signed off by the User.
3. Test UI logic programmatically with headless Playwright smoke tests. Infrastructure lives in
   `app/tests/conftest.py` (fixture) + `app/tests/test_shiny_smoke.py` (12 tests, T1–T4).
   Use `qa` persona for deterministic runs (all flags ON, ghost_save OFF):

   ```bash
   # Fast unit regression (always run first)
   PYTHONPATH=. ./.venv/bin/python -m pytest \
     app/tests/test_filter_operators.py libs/connector/tests/ \
     libs/viz_factory/tests/test_deco2_components.py -q

   # Playwright smoke — headless Chromium, one persona at a time
   PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest \
     app/tests/test_shiny_smoke.py -v

   # App import sanity
   python -c "from app.src.main import app; print('OK')"
   ```

   Full gate rules and selector pitfalls: `rules_ui_dashboard.md §6`.
   Persona masking matrix: `persona_traceability_matrix.md`.
