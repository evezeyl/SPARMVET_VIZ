# config/deployment/ — Deployments (ADR-048)

Deployments describe **how SPARMVET is deployed into a specific environment**: where data lives, which data analysis recipe loads at startup, which app features is active by default, and what type of system it is.

One Docker image + one deployment = one running SPARMVET instance.

## Directory Layout

```
config/deployment/
├── local/
│   └── local.yaml               ← Dev fallback (resolution level 4)
├── demo/
│   └── 202612_demo_deployment.yaml  ← the owner's demo of December 2026 (no default recipe, no default data)
├── connect/
│   └── connect_template.yaml    ← Posit Connect template (DEPLOY-CONNECT-1)
├── pipeline_test/
│   └── pipeline_test.yaml       ← Headless CI deployment
└── templates/
    └── deployment_template.yaml          ← Full schema reference with inline comments
```

## Deployment Resolution Order

The Bootloader finds the active deployment at startup (first match wins):

| Level | Source | Who uses it |
|---|---|---|
| 1 | `SPARMVET_DEPLOYMENT` env var | Galaxy XML wrapper, IRIDA container, Docker Compose, systemd |
| 2 | `~/.sparmvet/deployment.yaml` | Local PC scientist / admin |
| 3 | `/etc/sparmvet/deployment.yaml` | Institutional server (sysadmin) |
| 4 | `config/deployment/local/local.yaml` | Developer running from the repo |

The active level is logged at startup: `[Bootloader] Deployment resolved at level N (label): path`

## Creating a New Deployment

Copy `templates/deployment_template.yaml`, fill in your paths and deployment type, and place it at the appropriate level. The five required location keys are:

```yaml
locations:
  raw_data:      "..."   # read-only input files
  data_analysis_recipes:     "..."   # YAML data analysis recipes and step lists
  cache:  "..."   # Parquet caches (app writes here)
  user_data: "..."   # exports, saves, T3 artifacts (user-writable)
  gallery:       "..."   # gallery assets (read-only)
```

All location paths are relative to `project_root` (if set), otherwise relative to CWD.

## The demo deployment of December 2026

`demo/202612_demo_deployment.yaml` is for the owner's demo: app features `developer`, no default recipe (the first recipe that passes the load gate opens; the selector is visible), the shipped recipes folder, `raw_data` as in `local.yaml`, and `user_data: USER_DIRECTORY/` (the simulated user directory at the repository root, git-ignored, created on demand). PROVISIONAL. Start it with:

```bash
PYTHONPATH=. SPARMVET_DEPLOYMENT=config/deployment/demo/202612_demo_deployment.yaml ./.venv/bin/shiny run app/src/main.py --port 8000
```

Not built yet: the key for the place that receives the browser upload and the upload off unless declared (D-0439, D-0440), the write test at start, `locations.logs`, the app-owned subfolder `SPARMVET-VIZ_APP`, the store of uploads by hash. Until the store is built an upload overwrites the data file at the recipe's own `source.path`: a recipe of the owner should declare its data path under `USER_DIRECTORY/`, not under `assets/test_data/`. A recipe whose data is missing is rejected at start. Its test: `app/tests/test_demo_deployment_file.py`.

## Branding and the name of a deployment

A deployment has no name key (`deployment_name` was removed, D-0479, and is refused at start); describe the file in a comment at its top. What the user sees is in the `branding` block:

```yaml
branding:
  theme_css: "assets/demo/web_demo.css"       # layered over the default stylesheet
  banner:                                      # optional: shown at the top of the app and in the Deployment panel
    logo_url: "assets/demo/logo-no.svg"
    ui_label: "AMR Surveillance"               # the name (was `title`)
    description: "Norwegian Veterinary Institute"   # one line of text (was `subtitle`)
  contact: "team@example.org"                  # shown when a recipe is refused
  show_recipe_name: true                       # false hides the banner of the open recipe in HOME; true when absent
```

The old banner keys `title` and `subtitle` are refused at start with the new names.

## Deployment Types

| `deployment_type` | Adapter class | Notes |
|---|---|---|
| `filesystem` (default) | `FilesystemConnector` | Local PC, server, Galaxy-mounted dirs |
| `galaxy` | `GalaxyConnector` | Falls back to `_GALAXY_JOB_HOME_DIR` env var if `project_root` absent |
| `irida` | `IridaConnector` | Token via `SPARMVET_IRIDA_TOKEN` env var; fetch implementation Phase 23-D |

## Posit Connect Deployment (DEPLOY-CONNECT-1)

Posit Connect cannot install editable source packages (`-e ./libs/...`). The
`connect/` directory contains the deployment template and a bundle prep script.

**Quick start:**

```bash
# 1. Build wheels for all local libs into pkgs/
bash assets/scripts/bundle_connect.sh

# 2. Review / fill in config/deployment/connect/connect_template.yaml

# 3. Deploy (requires CONNECT_SERVER + CONNECT_API_KEY env vars)
bash assets/scripts/bundle_connect.sh --deploy
```

**Entry point:** `app/src/main:app` (the ASGI Shiny application object).

**Required environment variables on the Connect server:**

| Variable | Value | Purpose |
|---|---|---|
| `SPARMVET_DEPLOYMENT` | path to your filled-in deployment | Deployment resolution level 1 |
| `SPARMVET_APP_FEATURES` | e.g. `pipeline-static` | Override default app features |

**What `bundle_connect.sh` does:**
1. Builds wheels for `libs/*` and `app/` into `pkgs/` using `pip wheel --no-deps`
2. Verifies all local libs are listed in `requirements-connect.txt`
3. Checks the app entry point imports cleanly
4. Optionally calls `rsconnect deploy shiny` with the correct entrypoint and env vars

**`requirements-connect.txt`** is the PyPI-only pin file used on Connect.
The `--find-links pkgs/` line at the top tells pip to use the pre-built wheels
for local packages before looking at PyPI.

## Full Schema Reference

See `templates/deployment_template.yaml` (inline comments) or `docs/workflows/connector.qmd` (narrative).
