# connector — Deployment Adapter Library (ADR-048)

> **Status:** Phase 23-B complete (2026-04-30). All four connector classes implemented and tested (31/31 tests pass).

## Purpose

The connector library is the **Bridge layer** (ADR-048 §5) between the Bootloader's deployment profile YAML and the rest of the app. It provides type-specific adapters that:

1. **Resolve** the five named locations to absolute filesystem paths.
2. **Fetch** remote data to a local cache when needed (IRIDA only; filesystem/Galaxy are no-ops).

After `fetch_data()` returns, every deployment type looks identical to the rest of the app — all data is in local filesystem paths.

## Architecture

One Docker image + one deployment profile YAML = one running SPARMVET instance. The connector is selected automatically from `deployment_type` in the profile.

```
BaseConnector (ABC)
├── FilesystemConnector     ← deployment_type: filesystem  (local PC, server)
│   ├── GalaxyConnector     ← deployment_type: galaxy      (Galaxy GxIT)
│   └── IridaConnector      ← deployment_type: irida       (IRIDA REST API)
```

## Key Components

| File | Class | Role |
|---|---|---|
| `base.py` | `BaseConnector` | Abstract interface — `resolve_paths()`, `fetch_data()`, `get_manifest_path()`, `get_default_app_features()` |
| `filesystem.py` | `FilesystemConnector` | Resolves locations under `project_root`; no-op `fetch_data()` |
| `galaxy.py` | `GalaxyConnector` | Extends Filesystem; falls back to `_GALAXY_JOB_HOME_DIR` env var when `project_root` absent |
| `irida.py` | `IridaConnector` | Resolves paths via `irida.local_cache`; validates `SPARMVET_IRIDA_TOKEN` + irida block; `fetch_data()` stub (Phase 23-D) |
| `__init__.py` | `get_connector(profile)` | Factory — routes `deployment_type` → class; defaults to `FilesystemConnector` |

## Usage

```python
from connector import get_connector

profile = {
    "deployment_type": "filesystem",
    "project_root": "/data/pipeline/amr/",
    "locations": {
        "raw_data": "inputs/",
        "manifests": "manifests/",
        "curated_data": "parquet/",
        "user_sessions": "sessions/",
        "gallery": "gallery/",
    },
}

connector = get_connector(profile)
paths = connector.resolve_paths()
# paths["raw_data"] == Path("/data/pipeline/amr/inputs")
```

The `Bootloader (app/src/bootloader.py)` calls `get_connector()` automatically — app code does not instantiate connectors directly.

## Deployment Profile Integration

The active dev profile is at `config/deployment/local/local_profile.yaml`. See `docs/workflows/connector.qmd` for the full ADR-048 schema reference.

Profile resolution order (first match wins):
1. `SPARMVET_PROFILE` env var
2. `~/.sparmvet/profile.yaml`
3. `/etc/sparmvet/profile.yaml`
4. `config/deployment/local/local_profile.yaml` ← dev fallback

## IRIDA Token

For `deployment_type: irida`, the OAuth2 bearer token must be injected via `SPARMVET_IRIDA_TOKEN` environment variable at container launch. It must never appear in the deployment profile YAML. Full IRIDA fetch implementation is Phase 23-D.

## Installation

```bash
pip install -e ./libs/connector
```

## Tests

```bash
pytest libs/connector/tests/ -v
# 31 tests, all passing. In-memory profiles only — no filesystem access required.
```
