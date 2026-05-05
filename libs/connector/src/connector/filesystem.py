# @deps
# provides: class:FilesystemConnector
# consumes: class:BaseConnector
# doc: .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
FilesystemConnector — connector for filesystem-based deployments (ADR-048 §5).

Covers: local developer PC, Galaxy-mounted job directories, institutional servers.
fetch_data() is always a no-op — data is already present on disk.
"""
from __future__ import annotations

from pathlib import Path
from typing import Dict

from .base import BaseConnector


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
        return resolved

    def fetch_data(self) -> None:
        """No-op — filesystem data is already present."""
