# @deps
# provides: class:BaseConnector
# doc: .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
BaseConnector — abstract interface for all deployment connector types (ADR-048 §5).

All connectors receive the already-loaded profile dict from the Bootloader.
They are responsible for two things only:
  1. resolve_paths()  — produce the five location Paths for this deployment.
  2. fetch_data()     — pull remote data to local storage (no-op for filesystem types).

The rest of the app always reads local filesystem paths after fetch_data() returns.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import Dict


class BaseConnector(ABC):
    """
    Abstract base for SPARMVET deployment connectors (ADR-048 §5).

    Subclasses must implement resolve_paths() and fetch_data().
    get_manifest_path() and get_default_persona() have default implementations
    that read directly from the profile dict.
    """

    def __init__(self, profile: Dict) -> None:
        """
        Parameters
        ----------
        profile : dict
            Fully loaded deployment profile YAML (as returned by yaml.safe_load).
        """
        self._profile = profile

    @abstractmethod
    def resolve_paths(self) -> Dict[str, Path]:
        """
        Return the five canonical location paths for this deployment.

        Keys (all required): raw_data, manifests, curated_data, user_sessions, gallery.
        Values are absolute or CWD-relative Path objects — never raw strings.
        """

    @abstractmethod
    def fetch_data(self) -> None:
        """
        Pull remote data into local scope.

        - Filesystem types (FilesystemConnector, GalaxyConnector): no-op.
        - IridaConnector: downloads samples/metadata from IRIDA REST API into local_cache.

        Called once at startup, before resolve_paths() is used by the rest of the app.
        """

    def get_manifest_path(self) -> Path | None:
        """
        Return the default manifest Path, or None if not set in the profile.

        default_manifest in the profile is relative to project_root (or CWD if
        project_root is absent). Returns an absolute or CWD-relative Path.
        """
        dm = self._profile.get("default_manifest")
        if not dm:
            return None
        p = Path(dm)
        if p.is_absolute():
            return p
        project_root_str = self._profile.get("project_root")
        if project_root_str:
            return Path(project_root_str) / p
        return p

    def get_default_persona(self) -> str | None:
        """Return the default persona ID from the profile, or None if not set."""
        return self._profile.get("default_persona")

    def get_deployment_name(self) -> str:
        """Return the human-readable deployment label."""
        return self._profile.get("deployment_name", "SPARMVET_VIZ")

    def get_deployment_type(self) -> str:
        """Return the deployment_type string (filesystem / irida / galaxy)."""
        return self._profile.get("deployment_type", "filesystem")
