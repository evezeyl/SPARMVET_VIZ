# @deps
# provides: class:IridaConnector
# consumes: class:FilesystemConnector
# doc: .claude/knowledge/architecture_decisions.md#ADR-048
# @end_deps
"""
IridaConnector — connector for IRIDA REST API deployments (ADR-048 §5, §8).

Full OAuth2 fetch implementation is Phase 23-D. This module provides:
- The correct interface (resolve_paths, fetch_data, get_manifest_path).
- Token validation (reads SPARMVET_IRIDA_TOKEN from env, fails early if absent).
- Path resolution using irida.local_cache as effective project_root post-fetch.
- A NotImplementedError from fetch_data() until Phase 23-D lands.

After fetch_data() completes, all paths resolve inside local_cache — identical
to a filesystem deployment from the rest of the app's perspective.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict

from .filesystem import FilesystemConnector


class IridaConnector(FilesystemConnector):
    """
    Connector for IRIDA REST API deployments.

    Token security rule (ADR-048 §8): the OAuth2 bearer token is NEVER stored
    in the deployment profile YAML. It is always read from the SPARMVET_IRIDA_TOKEN
    environment variable, injected by IRIDA at container launch.
    """

    def fetch_data(self) -> None:
        """
        Download samples, metadata, and analysis results from IRIDA to local_cache.

        Phase 23-D implementation pending. Until then, raises NotImplementedError.
        Token (SPARMVET_IRIDA_TOKEN) and irida block are validated first so
        misconfiguration is caught at startup, not at data access time.
        """
        self._validate_irida_config()
        raise NotImplementedError(
            "IridaConnector.fetch_data() is not yet implemented (Phase 23-D). "
            "Set deployment_type: filesystem to use local data instead."
        )

    def resolve_paths(self) -> Dict[str, Path]:
        """
        Resolve paths using irida.local_cache as the effective project_root.

        local_cache is where fetch_data() will download IRIDA data. After
        fetch_data() returns, the rest of the app reads from local_cache
        exactly as if it were a filesystem deployment.
        """
        local_cache = self._local_cache()
        if local_cache:
            patched = {**self._profile, "project_root": str(local_cache)}
            return FilesystemConnector(patched).resolve_paths()
        return super().resolve_paths()

    def get_irida_base_url(self) -> str | None:
        """Return the IRIDA base URL from the profile irida block."""
        return self._profile.get("irida", {}).get("base_url")

    def get_irida_project_id(self) -> int | None:
        """Return the IRIDA project ID from the profile irida block."""
        return self._profile.get("irida", {}).get("project_id")

    def _local_cache(self) -> Path | None:
        """Return the local_cache path from the irida block, or None."""
        cache_str = self._profile.get("irida", {}).get("local_cache")
        return Path(cache_str) if cache_str else None

    def _validate_irida_config(self) -> None:
        """Raise early if token or irida block is missing."""
        token = os.environ.get("SPARMVET_IRIDA_TOKEN")
        if not token:
            raise EnvironmentError(
                "SPARMVET_IRIDA_TOKEN environment variable is required for IRIDA "
                "deployment but is not set. Inject it at container launch."
            )
        if not self._profile.get("irida"):
            raise ValueError(
                "Deployment profile is missing the required 'irida' block "
                "(base_url, project_id, local_cache) for IRIDA deployment."
            )
