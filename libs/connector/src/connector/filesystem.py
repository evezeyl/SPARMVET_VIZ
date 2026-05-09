# @deps
# provides: class:FilesystemConnector
# consumes: class:BaseConnector, utils.deployment_error
# doc: .claude/knowledge/architecture_decisions.md#ADR-048, ADR-078
# @end_deps
"""
FilesystemConnector — connector for filesystem-based deployments (ADR-048 §5).

Covers: local developer PC, Galaxy-mounted job directories, institutional servers.
fetch_data() is always a no-op — data is already present on disk.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from utils.deployment_error import DeploymentError, exit_if_errors

from .base import BaseConnector

# Paths that must exist on disk before the app can start.
# curated_data and user_sessions are written by the app at runtime — created on demand.
_REQUIRED_TO_EXIST = ("raw_data", "manifests", "gallery")
_REF = "ADR-048 — deployment profile 'locations:' block"


class FilesystemConnector(BaseConnector):
    """
    Reads location paths directly from the deployment profile.

    If project_root is set in the profile, relative location paths are resolved
    under it. Absolute paths are used as-is.
    """

    def resolve_paths(self) -> Dict[str, Path]:
        """
        Resolve all five location keys to Path objects.

        project_root (if present) is prepended to any relative location path.
        """
        project_root_str = self._profile.get("project_root")
        project_root = Path(project_root_str) if project_root_str else None
        locations = self._profile.get("locations", {})

        resolved: Dict[str, Path] = {}
        for key, path_str in locations.items():
            p = Path(path_str)
            if project_root and not p.is_absolute():
                p = project_root / p
            resolved[key] = p

        errors: list[DeploymentError] = []
        for key in _REQUIRED_TO_EXIST:
            p = resolved.get(key)
            if p is not None and not p.exists():
                errors.append(DeploymentError(
                    component="FilesystemConnector",
                    problem=f"Required location '{key}' does not exist on disk: {p}",
                    location=f"locations.{key} in deployment profile",
                    fix=(
                        f"Create the directory at '{p}' or update the 'locations.{key}' "
                        f"path in the deployment profile to point at an existing directory."
                    ),
                    who="operator",
                    reference=_REF,
                ))
        exit_if_errors(errors)

        return resolved

    def fetch_data(self) -> None:
        """No-op — filesystem data is already present."""
