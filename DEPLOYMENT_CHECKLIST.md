# Pre-Deployment Checklist

**Purpose:** Ensure all assets are built and the app is ready for deployment to Galaxy, IRIDA, Posit Connect, or standalone server.

**Execution:** Run these steps in order before packaging or pushing to a deployment target.

---

## Build Steps

### 1. Documentation (HELP-DOCS-1)

Render Quarto docs to generate `docs/_site/` for in-app bundling:

```bash
# From repo root:
quarto render docs/
```

**Why:** The app will serve docs at `/docs/` if `docs/_site/` exists. This provides an air-gapped help system with no internet dependency.

**Output:** `docs/_site/` directory with fully rendered HTML (check size ~50-200 MB depending on content).

**Optional:** If docs are not needed in this deployment, skip this step. The app will log `ℹ️ Documentation not bundled` at startup.

---

## Verification Steps

### 2. Dependency Check

Verify all local libraries are installed in editable mode:

```bash
# Install all libs at once:
scripts/install_libs.sh

# Or verify individual libs:
.venv/bin/python -c "from ingestion import *; from transformer import *; from viz_factory import *; print('✅ All libs import cleanly')"
```

**Why:** Editable installs are required for development and Galaxy/Connect deployments (they bundle source trees and reinstall).

---

### 3. Persona Validation

Validate all persona templates:

```bash
.venv/bin/python scripts/validate_persona_config.py --all
```

**Expected output:** `Total: 8 template(s) errors=0 RESULT: PASS`

---

### 4. App Import Check

Verify the full app starts without errors:

```bash
.venv/bin/python -c "from app.src.main import app; print('✅ App imports cleanly')"
```

**Expected output:**
```
[Bootloader] Profile resolved...
[Bootloader] Persona: ...
--- LOADING UI VERSION V5.1 ...
✅ App imports cleanly
✅ Documentation available at /docs/    [if docs were rendered]
```

---

### 5. Unit Tests (Optional)

Run the baseline unit test suite to catch regressions:

```bash
.venv/bin/python -m pytest \
  app/tests/test_filter_operators.py \
  libs/connector/tests/ \
  libs/viz_factory/tests/test_deco2_components.py \
  -q
```

**Expected output:** `... passed in ...s`

---

## Deployment Targets

### Galaxy / IRIDA

1. Run all steps above.
2. Ensure `SPARMVET_PROFILE` env var points to the correct profile YAML for your deployment (e.g., `config/deployment/galaxy/galaxy_profile.yaml`).
3. Bundle and push via appropriate platform tool.

### Posit Connect

1. Run all steps above.
2. Update `requirements.txt` to include editable lib installs (see `DEPLOY-CONNECT-1` in `.claude/tasks/tasks.md`).
3. Deploy using `rsconnect-python`:
   ```bash
   rsconnect deploy shiny . --entrypoint app/src/main.py
   ```

### Local Server

1. Run all steps above.
2. Set `SPARMVET_PROFILE` to your local profile path.
3. Start the server:
   ```bash
   .venv/bin/python -m shiny run app/src/main.py --host 0.0.0.0 --port 8000
   ```

---

## Troubleshooting

| Issue | Solution |
|---|---|
| `docs/_site` not found | Run `quarto render docs/` from repo root |
| Persona validation fails | Check `scripts/validate_persona_config.py --all` output for specific errors |
| App import fails | Run `.venv/bin/python scripts/install_libs.sh` to refresh editable installs |
| Tests fail | Run `pytest` with `--tb=short` to see full traceback |

---

## Post-Deployment

After deployment, verify in the deployed app:

1. **Home workspace loads** — click through analysis groups and plots
2. **Sidebar panels render** — manifest choice, filters, export, etc.
3. **Help system works** (if docs were bundled) — click `?` button in workspace headers
4. **Filter + Apply works** (if T3 enabled) — add a filter, click Apply, confirm plot updates

---

**Last updated:** 2026-05-09  
**Related tasks:** HELP-DOCS-1, DEPLOY-CONNECT-1, DEPLOY-LIBS-1
