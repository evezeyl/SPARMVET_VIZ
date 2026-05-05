# @deps
# provides: class:GalaxyConnector
# consumes: class:FilesystemConnector
# doc: .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
GalaxyConnector — thin filesystem wrapper for Galaxy GxIT deployments (ADR-048 §5).

Galaxy mounts input datasets and the job working directory before the app starts.
No data fetching is needed. The connector's only role is path resolution,
with an optional fallback: if the profile omits project_root, the Galaxy job
home directory env var (_GALAXY_JOB_HOME_DIR) is used instead.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from .filesystem import FilesystemConnector


class GalaxyConnector(FilesystemConnector):
    """
    Filesystem connector for Galaxy GxIT deployments.

    Behaviour:
    - fetch_data() is always a no-op (Galaxy mounts data before the app starts).
    - resolve_paths() uses the profile's project_root if set. If project_root
      is absent, falls back to the _GALAXY_JOB_HOME_DIR env var. If neither
      is available, behaves identically to FilesystemConnector (CWD-relative paths).
    """

    # Galaxy env vars that may supply the job working directory.
    _GALAXY_HOME_VARS = ("_GALAXY_JOB_HOME_DIR", "GALAXY_SLOTS_DIR")

    def resolve_paths(self) -> Dict[str, Path]:
        if self._profile.get("project_root"):
            return super().resolve_paths()

        galaxy_home = self._galaxy_job_dir()
        if galaxy_home:
            patched = {**self._profile, "project_root": str(galaxy_home)}
            return FilesystemConnector(patched).resolve_paths()

        return super().resolve_paths()

    def fetch_data(self) -> None:
        """No-op — Galaxy mounts all datasets before the app container starts."""

    def _galaxy_job_dir(self) -> Path | None:
        """Return the Galaxy job directory from env vars, or None if not set."""
        for var in self._GALAXY_HOME_VARS:
            val = os.environ.get(var)
            if val:
                return Path(val)
        return None
