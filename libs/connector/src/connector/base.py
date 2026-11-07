# @deps
# provides: class:BaseConnector
# doc: .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
BaseConnector — abstract interface for all deployment connector types (ADR-048 §5).

All connectors receive the already-loaded deployment dict from the Bootloader.
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
    get_default_app_features() has a default implementation
    that read directly from the deployment dict.
    """

    def __init__(self, deployment: Dict) -> None:
        """
        Parameters
        ----------
        deployment : dict
            Fully loaded deployment file (as returned by yaml.safe_load).
        """
        self._deployment = deployment

    @abstractmethod
    def resolve_paths(self) -> Dict[str, Path]:
        """
        Return the five canonical location paths for this deployment.

        Keys (all required): raw_data, data analysis recipes, cache, user_data, gallery.
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

    def get_default_app_features(self) -> str | None:
        """Return the default app features ID from the deployment, or None if not set."""
        return self._deployment.get("default_app_features")

    def get_deployment_name(self) -> str:
        """Return the human-readable deployment label."""
        return self._deployment.get("deployment_name", "SPARMVET_VIZ")

    def get_deployment_type(self) -> str:
        """Return the deployment_type string (filesystem / irida / galaxy)."""
        return self._deployment.get("deployment_type", "filesystem")
