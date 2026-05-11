# config/deployment/ — Deployment Profiles (ADR-048)

Deployment profiles describe **how SPARMVET is deployed into a specific environment**: where data lives, which manifest loads at startup, which persona is active by default, and what type of system it is.

One Docker image + one deployment profile = one running SPARMVET instance.

## Directory Layout

```
config/deployment/
├── local/
│   └── local_profile.yaml               ← Dev fallback (resolution level 4)
├── connect/
│   └── connect_profile_template.yaml    ← Posit Connect template (DEPLOY-CONNECT-1)
├── pipeline_test/
│   └── pipeline_test_profile.yaml       ← Headless CI profile
└── templates/
    └── connector_template.yaml          ← Full schema reference with inline comments
```

## Profile Resolution Order

The Bootloader finds the active profile at startup (first match wins):

| Level | Source | Who uses it |
|---|---|---|
| 1 | `SPARMVET_PROFILE` env var | Galaxy XML wrapper, IRIDA container, Docker Compose, systemd |
| 2 | `~/.sparmvet/profile.yaml` | Local PC scientist / admin |
| 3 | `/etc/sparmvet/profile.yaml` | Institutional server (sysadmin) |
| 4 | `config/deployment/local/local_profile.yaml` | Developer running from the repo |

The active level is logged at startup: `[Bootloader] Profile resolved at level N (label): path`

## Creating a New Profile

Copy `templates/connector_template.yaml`, fill in your paths and deployment type, and place it at the appropriate level. The five required location keys are:

```yaml
locations:
  raw_data:      "..."   # read-only input files
  manifests:     "..."   # YAML manifests and recipes
  curated_data:  "..."   # Parquet caches (app writes here)
  user_sessions: "..."   # exports, saves, T3 artifacts (user-writable)
  gallery:       "..."   # gallery assets (read-only)
```

All location paths are relative to `project_root` (if set), otherwise relative to CWD.

## Deployment Types

| `deployment_type` | Adapter class | Notes |
|---|---|---|
| `filesystem` (default) | `FilesystemConnector` | Local PC, server, Galaxy-mounted dirs |
| `galaxy` | `GalaxyConnector` | Falls back to `_GALAXY_JOB_HOME_DIR` env var if `project_root` absent |
| `irida` | `IridaConnector` | Token via `SPARMVET_IRIDA_TOKEN` env var; fetch implementation Phase 23-D |

## Posit Connect Deployment (DEPLOY-CONNECT-1)

Posit Connect cannot install editable source packages (`-e ./libs/...`). The
`connect/` directory contains the profile template and a bundle prep script.

**Quick start:**

```bash
# 1. Build wheels for all local libs into pkgs/
bash assets/scripts/bundle_connect.sh

# 2. Review / fill in config/deployment/connect/connect_profile_template.yaml

# 3. Deploy (requires CONNECT_SERVER + CONNECT_API_KEY env vars)
bash assets/scripts/bundle_connect.sh --deploy
```

**Entry point:** `app/src/main:app` (the ASGI Shiny application object).

**Required environment variables on the Connect server:**

| Variable | Value | Purpose |
|---|---|---|
| `SPARMVET_PROFILE` | path to your filled-in profile | Profile resolution level 1 |
| `SPARMVET_PERSONA` | e.g. `pipeline-static` | Override default persona |

**What `bundle_connect.sh` does:**
1. Builds wheels for `libs/*` and `app/` into `pkgs/` using `pip wheel --no-deps`
2. Verifies all local libs are listed in `requirements-connect.txt`
3. Checks the app entry point imports cleanly
4. Optionally calls `rsconnect deploy shiny` with the correct entrypoint and env vars

**`requirements-connect.txt`** is the PyPI-only pin file used on Connect.
The `--find-links pkgs/` line at the top tells pip to use the pre-built wheels
for local packages before looking at PyPI.

## Full Schema Reference

See `templates/connector_template.yaml` (inline comments) or `docs/workflows/connector.qmd` (narrative).
