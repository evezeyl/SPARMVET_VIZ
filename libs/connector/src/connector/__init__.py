# @deps
# provides: BaseConnector, FilesystemConnector, GalaxyConnector, IridaConnector, get_connector()
# consumes: connector.base, connector.filesystem, connector.galaxy, connector.irida
# consumed_by: app/src/bootloader.py, app/src/server.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
connector — SPARMVET deployment connector library (ADR-048).

Public API:
    BaseConnector      — abstract base; all connectors implement this interface.
    FilesystemConnector — filesystem + Galaxy-mounted deployments.
    GalaxyConnector    — Galaxy GxIT (thin filesystem wrapper + job dir env var fallback).
    IridaConnector     — IRIDA REST API (fetch_data() pending Phase 23-D).
    get_connector(profile) — factory: returns the right connector for a profile dict.
"""
from .base import BaseConnector
from .filesystem import FilesystemConnector
from .galaxy import GalaxyConnector
from .irida import IridaConnector

__all__ = [
    "BaseConnector",
    "FilesystemConnector",
    "GalaxyConnector",
    "IridaConnector",
    "get_connector",
]


def get_connector(profile: dict) -> BaseConnector:
    """
    Factory: return the appropriate connector for a deployment profile dict.

    deployment_type → connector class:
        "filesystem" (or absent) → FilesystemConnector
        "galaxy"                 → GalaxyConnector
        "irida"                  → IridaConnector
    """
    dtype = profile.get("deployment_type", "filesystem")
    if dtype == "irida":
        return IridaConnector(profile)
    if dtype == "galaxy":
        return GalaxyConnector(profile)
    return FilesystemConnector(profile)
