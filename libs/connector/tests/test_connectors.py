"""
Unit tests for libs/connector — ADR-048 deployment connector library.

Run from project root:
    pytest libs/connector/tests/test_connectors.py -v

Profile constants are used for tests that do NOT call resolve_paths().
Tests that call resolve_paths() use tmp_path to satisfy the path-existence
check added in DIAG-CONNECTOR-1 (FilesystemConnector validates declared
locations exist on disk before returning).
"""
import os
import pytest
from pathlib import Path

from connector import (
    BaseConnector,
    FilesystemConnector,
    GalaxyConnector,
    IridaConnector,
    get_connector,
)

# ── Shared fixtures ────────────────────────────────────────────────────────────

MINIMAL_LOCATIONS = {
    "raw_data": "inputs/",
    "manifests": "manifests/",
    "curated_data": "parquet/",
    "user_sessions": "sessions/",
    "gallery": "gallery/",
}

FS_PROFILE = {
    "deployment_type": "filesystem",
    "locations": MINIMAL_LOCATIONS,
}

FS_PROFILE_WITH_ROOT = {
    "deployment_type": "filesystem",
    "project_root": "/data/pipeline/",
    "default_manifest": "manifests/amr/master.yaml",
    "default_persona": "pipeline-static",
    "deployment_name": "AMR Pipeline",
    "locations": MINIMAL_LOCATIONS,
}

IRIDA_PROFILE = {
    "deployment_type": "irida",
    "irida": {
        "base_url": "https://irida.example.ca",
        "project_id": 42,
        "auth": "oauth2",
        "local_cache": "/tmp/irida_cache/",
    },
    "locations": MINIMAL_LOCATIONS,
}

GALAXY_PROFILE = {
    "deployment_type": "galaxy",
    "locations": MINIMAL_LOCATIONS,
}

GALAXY_PROFILE_WITH_ROOT = {
    "deployment_type": "galaxy",
    "project_root": "/galaxy/job/123/",
    "locations": MINIMAL_LOCATIONS,
}


def _make_locations(base: Path) -> dict:
    """Create standard location subdirs under base and return an absolute locations dict."""
    locs = {
        "raw_data": str(base / "inputs"),
        "manifests": str(base / "manifests"),
        "curated_data": str(base / "parquet"),
        "user_sessions": str(base / "sessions"),
        "gallery": str(base / "gallery"),
    }
    for p in locs.values():
        Path(p).mkdir(parents=True, exist_ok=True)
    return locs


# ── BaseConnector ──────────────────────────────────────────────────────────────

def test_base_connector_is_abstract():
    with pytest.raises(TypeError):
        BaseConnector({})  # cannot instantiate abstract class


# ── FilesystemConnector ────────────────────────────────────────────────────────

class TestFilesystemConnector:

    def test_resolve_paths_no_root(self, tmp_path):
        locs = _make_locations(tmp_path)
        c = FilesystemConnector({"deployment_type": "filesystem", "locations": locs})
        paths = c.resolve_paths()
        assert paths["raw_data"] == tmp_path / "inputs"
        assert paths["manifests"] == tmp_path / "manifests"

    def test_resolve_paths_with_root(self, tmp_path):
        # tmp_path acts as project_root; MINIMAL_LOCATIONS are relative and get joined
        _make_locations(tmp_path)
        profile = {
            "deployment_type": "filesystem",
            "project_root": str(tmp_path),
            "default_manifest": "manifests/amr/master.yaml",
            "default_persona": "pipeline-static",
            "deployment_name": "AMR Pipeline",
            "locations": MINIMAL_LOCATIONS,
        }
        c = FilesystemConnector(profile)
        paths = c.resolve_paths()
        assert paths["raw_data"] == tmp_path / "inputs"
        assert paths["manifests"] == tmp_path / "manifests"

    def test_resolve_paths_absolute_not_prepended(self, tmp_path):
        # Verify: absolute location path is NOT prepended with project_root;
        # relative location paths ARE prepended.
        root_dir = tmp_path / "root"
        abs_data = tmp_path / "absolute" / "data"
        root_dir.mkdir()
        abs_data.mkdir(parents=True)
        (root_dir / "manifests").mkdir()
        (root_dir / "parquet").mkdir()
        (root_dir / "sessions").mkdir()
        (root_dir / "gallery").mkdir()
        profile = {
            "project_root": str(root_dir),
            "locations": {**MINIMAL_LOCATIONS, "raw_data": str(abs_data)},
        }
        c = FilesystemConnector(profile)
        paths = c.resolve_paths()
        assert paths["raw_data"] == abs_data
        assert paths["manifests"] == root_dir / "manifests"

    def test_fetch_data_is_noop(self):
        c = FilesystemConnector(FS_PROFILE)
        c.fetch_data()  # must not raise

    def test_get_manifest_path_none_when_absent(self):
        c = FilesystemConnector(FS_PROFILE)
        assert c.get_manifest_path() is None

    def test_get_manifest_path_with_root(self):
        c = FilesystemConnector(FS_PROFILE_WITH_ROOT)
        mpath = c.get_manifest_path()
        assert mpath == Path("/data/pipeline/manifests/amr/master.yaml")

    def test_get_manifest_path_no_root(self):
        profile = {**FS_PROFILE, "default_manifest": "config/manifests/amr.yaml"}
        c = FilesystemConnector(profile)
        assert c.get_manifest_path() == Path("config/manifests/amr.yaml")

    def test_get_manifest_path_absolute(self):
        profile = {**FS_PROFILE, "default_manifest": "/absolute/manifest.yaml"}
        c = FilesystemConnector(profile)
        assert c.get_manifest_path() == Path("/absolute/manifest.yaml")

    def test_get_default_persona(self):
        c = FilesystemConnector(FS_PROFILE_WITH_ROOT)
        assert c.get_default_persona() == "pipeline-static"

    def test_get_default_persona_none(self):
        c = FilesystemConnector(FS_PROFILE)
        assert c.get_default_persona() is None

    def test_get_deployment_name(self):
        c = FilesystemConnector(FS_PROFILE_WITH_ROOT)
        assert c.get_deployment_name() == "AMR Pipeline"

    def test_get_deployment_name_default(self):
        c = FilesystemConnector(FS_PROFILE)
        assert c.get_deployment_name() == "SPARMVET_VIZ"

    def test_get_deployment_type(self):
        c = FilesystemConnector(FS_PROFILE)
        assert c.get_deployment_type() == "filesystem"


# ── GalaxyConnector ────────────────────────────────────────────────────────────

class TestGalaxyConnector:

    def test_resolve_paths_with_root_ignores_env(self, tmp_path, monkeypatch):
        _make_locations(tmp_path)
        monkeypatch.setenv("_GALAXY_JOB_HOME_DIR", str(tmp_path / "env_job"))
        profile = {
            "deployment_type": "galaxy",
            "project_root": str(tmp_path),
            "locations": MINIMAL_LOCATIONS,
        }
        c = GalaxyConnector(profile)
        paths = c.resolve_paths()
        # project_root takes priority over env var
        assert paths["raw_data"] == tmp_path / "inputs"

    def test_resolve_paths_env_var_fallback(self, tmp_path, monkeypatch):
        env_root = tmp_path / "env_job"
        _make_locations(env_root)
        monkeypatch.setenv("_GALAXY_JOB_HOME_DIR", str(env_root))
        profile = {
            "deployment_type": "galaxy",
            "locations": MINIMAL_LOCATIONS,
        }
        c = GalaxyConnector(profile)
        paths = c.resolve_paths()
        assert paths["raw_data"] == env_root / "inputs"

    def test_resolve_paths_no_root_no_env(self, tmp_path, monkeypatch):
        locs = _make_locations(tmp_path)
        monkeypatch.delenv("_GALAXY_JOB_HOME_DIR", raising=False)
        monkeypatch.delenv("GALAXY_SLOTS_DIR", raising=False)
        c = GalaxyConnector({"deployment_type": "galaxy", "locations": locs})
        paths = c.resolve_paths()
        assert paths["raw_data"] == tmp_path / "inputs"

    def test_fetch_data_is_noop(self):
        c = GalaxyConnector(GALAXY_PROFILE)
        c.fetch_data()  # must not raise

    def test_is_filesystem_subclass(self):
        assert issubclass(GalaxyConnector, FilesystemConnector)


# ── IridaConnector ─────────────────────────────────────────────────────────────

class TestIridaConnector:

    def test_resolve_paths_uses_local_cache(self, tmp_path):
        cache_root = tmp_path / "irida_cache"
        _make_locations(cache_root)
        profile = {
            "deployment_type": "irida",
            "irida": {
                "base_url": "https://irida.example.ca",
                "project_id": 42,
                "auth": "oauth2",
                "local_cache": str(cache_root),
            },
            "locations": MINIMAL_LOCATIONS,
        }
        c = IridaConnector(profile)
        paths = c.resolve_paths()
        assert paths["raw_data"] == cache_root / "inputs"
        assert paths["manifests"] == cache_root / "manifests"

    def test_resolve_paths_no_local_cache_falls_back(self, tmp_path):
        locs = _make_locations(tmp_path)
        profile = {
            "deployment_type": "irida",
            "irida": {"base_url": "x", "project_id": 1},
            "locations": locs,
        }
        c = IridaConnector(profile)
        paths = c.resolve_paths()
        assert paths["raw_data"] == tmp_path / "inputs"

    def test_fetch_data_exits_without_token(self, tmp_path, monkeypatch):
        # _validate_irida_config() uses exit_if_errors() → sys.exit(1) (ADR-077/ADR-078)
        cache_root = tmp_path / "irida_cache"
        _make_locations(cache_root)
        monkeypatch.delenv("SPARMVET_IRIDA_TOKEN", raising=False)
        profile = {
            "deployment_type": "irida",
            "irida": {
                "base_url": "https://irida.example.ca",
                "project_id": 42,
                "auth": "oauth2",
                "local_cache": str(cache_root),
            },
            "locations": MINIMAL_LOCATIONS,
        }
        c = IridaConnector(profile)
        with pytest.raises(SystemExit):
            c.fetch_data()

    def test_fetch_data_exits_without_irida_block(self, tmp_path, monkeypatch):
        # _validate_irida_config() uses exit_if_errors() → sys.exit(1) (ADR-077/ADR-078)
        locs = _make_locations(tmp_path)
        monkeypatch.setenv("SPARMVET_IRIDA_TOKEN", "tok")
        c = IridaConnector({"deployment_type": "irida", "locations": locs})
        with pytest.raises(SystemExit):
            c.fetch_data()

    def test_fetch_data_raises_not_implemented_when_configured(self, tmp_path, monkeypatch):
        cache_root = tmp_path / "irida_cache"
        _make_locations(cache_root)
        monkeypatch.setenv("SPARMVET_IRIDA_TOKEN", "tok")
        profile = {
            "deployment_type": "irida",
            "irida": {
                "base_url": "https://irida.example.ca",
                "project_id": 42,
                "auth": "oauth2",
                "local_cache": str(cache_root),
            },
            "locations": MINIMAL_LOCATIONS,
        }
        c = IridaConnector(profile)
        with pytest.raises(NotImplementedError, match="Phase 23-D"):
            c.fetch_data()

    def test_get_irida_base_url(self):
        c = IridaConnector(IRIDA_PROFILE)
        assert c.get_irida_base_url() == "https://irida.example.ca"

    def test_get_irida_project_id(self):
        c = IridaConnector(IRIDA_PROFILE)
        assert c.get_irida_project_id() == 42

    def test_is_filesystem_subclass(self):
        assert issubclass(IridaConnector, FilesystemConnector)


# ── get_connector factory ──────────────────────────────────────────────────────

class TestGetConnector:

    def test_filesystem_type(self):
        c = get_connector(FS_PROFILE)
        assert isinstance(c, FilesystemConnector)
        assert not isinstance(c, GalaxyConnector)
        assert not isinstance(c, IridaConnector)

    def test_galaxy_type(self):
        c = get_connector(GALAXY_PROFILE)
        assert isinstance(c, GalaxyConnector)

    def test_irida_type(self):
        c = get_connector(IRIDA_PROFILE)
        assert isinstance(c, IridaConnector)

    def test_absent_type_defaults_to_filesystem(self):
        c = get_connector({"locations": MINIMAL_LOCATIONS})
        assert isinstance(c, FilesystemConnector)
        assert not isinstance(c, GalaxyConnector)
