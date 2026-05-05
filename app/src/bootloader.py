# @deps
# provides: Bootloader (class), bootloader (global singleton instance)
# consumes: yaml, os, pathlib, typing, connector (get_connector)
# consumed_by: app.src.server, app.src.ui, app.handlers.home_theater, app.handlers.blueprint_handlers, app.handlers.gallery_handlers, app.handlers.ingestion_handlers
# doc: ADR-031, ADR-026, ADR-048, project_conventions.md §"Deployment Profile Resolution"
# @end_deps
# app/src/bootloader.py
#
# Deployment profile resolution chain (ADR-048 §4) — first match wins:
#   Level 1: SPARMVET_PROFILE env var       — Galaxy XML, IRIDA, Docker Compose, systemd
#   Level 2: ~/.sparmvet/profile.yaml        — local PC (scientist/admin places once)
#   Level 3: /etc/sparmvet/profile.yaml      — institutional server (sysadmin places at deploy)
#   Level 4: config/deployment/local/local_profile.yaml — developer repo fallback
#
# Connector lifecycle (ADR-048 §5, Option B):
#   After profile load, the appropriate connector is instantiated via get_connector().
#   connector.fetch_data() runs first (no-op for filesystem/Galaxy; downloads for IRIDA).
#   connector.resolve_paths() is then the authoritative source for all location paths.
#   get_location() reads from those resolved paths directly.
import yaml
import os
from pathlib import Path
from typing import Dict, Any

_RESOLUTION_LEVEL_LABELS = {
    1: "SPARMVET_PROFILE env var",
    2: "~/.sparmvet/profile.yaml (user-level)",
    3: "/etc/sparmvet/profile.yaml (system-level)",
    4: "config/deployment/local/local_profile.yaml (dev fallback)",
}


class Bootloader:
    """
    System Bootloader (ADR-031, ADR-026, ADR-048).
    Handles path authority, UI persona feature toggling, and deployment profile resolution.

    Profile resolution chain (ADR-048 §4):
        1. SPARMVET_PROFILE env var  — explicit path; used by Galaxy/IRIDA/Docker
        2. ~/.sparmvet/profile.yaml  — user-level; local PC without env var
        3. /etc/sparmvet/profile.yaml — system-level; admin-placed on server
        4. config/deployment/local/local_profile.yaml — repo dev fallback

    See project_conventions.md §"Deployment Profile Resolution" for full details.
    """
    # ADR-031: Static Cache Layer
    _persona_cache: Dict[str, Dict[str, Any]] = {}
    _connector_cache: Dict[str, Dict[str, Any]] = {}          # keyed by resolved profile path string
    _resolved_locations_cache: Dict[str, Dict[str, Path]] = {}  # keyed by resolved profile path string

    # Hierarchical Asset Cache: project_id -> dataset_id -> plot_id -> asset_type -> asset
    _asset_cache: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}

    def get_cached_asset(self, project_id: str, dataset_id: str, plot_id: str, asset_type: str) -> Any:
        try:
            return self._asset_cache[project_id][dataset_id][plot_id][asset_type]
        except KeyError:
            return None

    def set_cached_asset(self, project_id: str, dataset_id: str, plot_id: str, asset_type: str, asset: Any):
        if project_id not in self._asset_cache:
            self._asset_cache[project_id] = {}
        if dataset_id not in self._asset_cache[project_id]:
            self._asset_cache[project_id][dataset_id] = {}
        if plot_id not in self._asset_cache[project_id][dataset_id]:
            self._asset_cache[project_id][dataset_id][plot_id] = {}
        self._asset_cache[project_id][dataset_id][plot_id][asset_type] = asset

    def __init__(self, persona: str | None = None, connector: str | None = None):
        # Persona resolved after profile load — see step 2 below
        self._persona_kwarg = persona
        # connector kwarg kept for backward compatibility; used only in level-4 fallback path
        self.connector = connector or os.environ.get("SPARMVET_CONNECTOR", "local")

        # 1. Path Authority — 4-level profile resolution (ADR-048 §4)
        self.connector_path, self.deployment_level = self._resolve_profile_path()
        print(
            f"[Bootloader] Profile resolved at level {self.deployment_level} "
            f"({_RESOLUTION_LEVEL_LABELS[self.deployment_level]}): {self.connector_path}"
        )

        # Load profile (cached by resolved absolute path)
        _cache_key = str(self.connector_path.resolve())
        if _cache_key not in self._connector_cache:
            self._connector_cache[_cache_key] = self._load_connector_config()
        self.connector_config = self._connector_cache[_cache_key]

        # ADR-048 deployment fields (all optional in local dev profile)
        project_root_str = self.connector_config.get("project_root")
        self.project_root: Path | None = Path(project_root_str) if project_root_str else None
        self.default_manifest: str | None = self.connector_config.get("default_manifest")
        self.default_persona: str | None = self.connector_config.get("default_persona")
        self.deployment_name: str = self.connector_config.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
        self.deployment_type: str = self.connector_config.get("deployment_type", "filesystem")

        # Connector lifecycle (ADR-048 §5, Option B):
        # fetch_data() runs once at startup — no-op for filesystem/Galaxy, downloads for IRIDA.
        # resolve_paths() is then the single authoritative source for all location paths.
        if _cache_key not in self._resolved_locations_cache:
            from connector import get_connector
            _conn = get_connector(self.connector_config)
            print(f"[Bootloader] Connector: {_conn.__class__.__name__} — fetch_data()")
            _conn.fetch_data()
            self._resolved_locations_cache[_cache_key] = _conn.resolve_paths()
        self._resolved_locations: Dict[str, Path] = self._resolved_locations_cache[_cache_key]

        # Keep raw locations dict for backward compat (key validation only)
        self.locations = self.connector_config.get("locations", {})

        # Validate required location keys
        self._validate_profile()

        # 2. Persona Logic — resolution order: kwarg > env var > profile default_persona > error
        self.persona = (
            self._persona_kwarg
            or os.environ.get("SPARMVET_PERSONA")
            or self.default_persona
        )
        if not self.persona:
            raise ValueError(
                "No persona configured. Set SPARMVET_PERSONA env var, "
                "add default_persona to deployment profile, or pass persona= kwarg."
            )
        self.set_persona(self.persona)

        # 3. Project Authority (Agnostic Discovery)
        self.project_dir = self.get_location("manifests")
        self.available_projects = self._discover_projects()

    def _resolve_profile_path(self) -> tuple[Path, int]:
        """
        Resolve the deployment profile path via the 4-level priority chain (ADR-048 §4).

        Returns (resolved_path, level) where level ∈ {1, 2, 3, 4}.

        Raises FileNotFoundError if:
        - SPARMVET_PROFILE is set but points to a non-existent file (hard error — misconfiguration).
        - No profile is found at any level (shows all checked paths in the message).

        Resolution order (first match wins):
            1. SPARMVET_PROFILE env var  — Galaxy XML, IRIDA container launch, Docker Compose, systemd
            2. ~/.sparmvet/profile.yaml  — local PC (scientist or admin places this once at setup)
            3. /etc/sparmvet/profile.yaml — institutional server (sysadmin places at deploy time)
            4. config/deployment/local/local_profile.yaml — developer running from repo root
        """
        # Level 1: explicit env var — fail hard if set but missing (misconfiguration, not "not found")
        env_profile = os.environ.get("SPARMVET_PROFILE")
        if env_profile:
            p = Path(env_profile)
            if not p.exists():
                raise FileNotFoundError(
                    f"SPARMVET_PROFILE env var is set to '{env_profile}' but the file does not exist. "
                    "Check the path or unset the variable to fall through to lower-priority levels."
                )
            return p, 1

        # Level 2: user-level config
        user_profile = Path.home() / ".sparmvet" / "profile.yaml"
        if user_profile.exists():
            return user_profile, 2

        # Level 3: system-level config
        system_profile = Path("/etc/sparmvet/profile.yaml")
        if system_profile.exists():
            return system_profile, 3

        # Level 4: dev repo fallback
        dev_fallback = Path(f"config/deployment/{self.connector}/local_profile.yaml")
        if dev_fallback.exists():
            return dev_fallback, 4

        raise FileNotFoundError(
            "No deployment profile found. Checked:\n"
            "  1. SPARMVET_PROFILE env var (not set)\n"
            f"  2. {Path.home() / '.sparmvet' / 'profile.yaml'} (not found)\n"
            "  3. /etc/sparmvet/profile.yaml (not found)\n"
            f"  4. {dev_fallback} (not found)\n\n"
            "To fix: create config/deployment/local/local_profile.yaml "
            "or set SPARMVET_PROFILE to a valid profile path."
        )

    def _validate_profile(self) -> None:
        """Raise ValueError if required location keys are missing from resolved paths."""
        required = {"raw_data", "manifests", "curated_data", "user_sessions", "gallery"}
        missing = required - set(self._resolved_locations.keys())
        if missing:
            raise ValueError(
                f"Deployment profile '{self.connector_path}' is missing required "
                f"location keys: {sorted(missing)}"
            )

    def set_persona(self, persona: str):
        """Load persona config from a file path or legacy shortname.

        Accepts:
          - Absolute path: /path/to/my_persona.yaml
          - Relative path: config/ui/templates/developer_template.yaml
          - Legacy shortname: developer  →  config/ui/templates/developer_template.yaml
        """
        self.persona = persona
        p = Path(persona)
        if "/" in persona or "\\" in persona or persona.endswith(".yaml"):
            self.persona_path = p.resolve()
        else:
            # Legacy shortname — backward compatible
            self.persona_path = Path(
                f"config/ui/templates/{persona}_template.yaml").resolve()

        cache_key = str(self.persona_path)
        if cache_key not in self._persona_cache:
            self._persona_cache[cache_key] = self._load_persona_config()

        self.config = self._persona_cache[cache_key]
        print(f"[Bootloader] Persona: {self.persona} → {self.persona_path}")
        self.features = self.config.get("features", {})
        self.automation = self.config.get("automation", {})

    @property
    def persona_display_name(self) -> str:
        """Human-readable persona name from the template's display_name field.

        Falls back to persona_id, then to the raw persona value (path or shortname).
        Used for UI display only — never for behavioral gating.
        """
        return (
            self.config.get("display_name")
            or self.config.get("persona_id")
            or self.persona
        )

    def _discover_projects(self) -> Dict[str, str]:
        """Scans the project directory for YAML manifests."""
        mf_files = list(self.project_dir.glob("*.yaml"))
        return {f.stem: str(f) for f in mf_files}

    def get_default_project(self) -> str:
        """Returns the fixed_manifest project ID if set, else the first available project."""
        fixed = self.get_manifest_selector().get("fixed_manifest")
        if fixed:
            return fixed
        if not self.available_projects:
            raise FileNotFoundError("No projects found in Location 2.")
        return list(self.available_projects.keys())[0]

    def _load_connector_config(self) -> Dict[str, Any]:
        """Loads the deployment profile YAML."""
        if not self.connector_path.exists():
            raise FileNotFoundError(
                f"Connector config not found: {self.connector_path}")

        try:
            with open(self.connector_path, "r") as f:
                return yaml.safe_load(f) or {}
        except Exception:
            return {}

    def _load_persona_config(self) -> Dict[str, Any]:
        """Loads UI feature toggles from the persona template and applies dependency cascade.

        Cascade rules (rules_persona_feature_flags.md §107–127):
          - interactivity_enabled=False suppresses t3_sandbox/comparison/session/export_graph/audit_report
          - import_helper_enabled=False suppresses data_ingestion_enabled
          - Deployment-profile data_ingestion_enabled:false is an absolute override
        A WARNING is printed for each flag that was True in the template and forced False.
        """
        path = self.persona_path
        if not path.exists():
            print(f"[Bootloader] WARNING: Persona config not found: {path}")
            return {}

        try:
            with open(path, "r") as f:
                config = yaml.safe_load(f) or {}
        except Exception:
            return {}

        features = config.get("features", {})

        # Backward compat: old templates may still have export_bundle_enabled /
        # export_graph_enabled. Map them to export_enabled (either old flag true → true).
        if "export_enabled" not in features:
            features["export_enabled"] = (
                features.pop("export_bundle_enabled", False)
                or features.pop("export_graph_enabled", False)
            )
        else:
            features.pop("export_bundle_enabled", None)
            features.pop("export_graph_enabled", None)

        # FLAG-2: mirror manifest_selector.visible into features for is_enabled() access.
        ms = config.get("manifest_selector", {})
        if "manifest_selector_visible" not in features:
            features["manifest_selector_visible"] = bool(ms.get("visible", True))

        # Group B: interactivity_enabled=False suppresses all interactive child flags.
        if not features.get("interactivity_enabled", False):
            for child in ("t3_sandbox_enabled", "comparison_mode_enabled",
                          "session_management_enabled", "audit_report_enabled"):
                if features.get(child, False):
                    print(
                        f"[Bootloader] WARNING: {child}=True ignored — "
                        f"interactivity_enabled=False in {path.name}"
                    )
                    features[child] = False

        # Group C: import_helper_enabled=False suppresses data_ingestion_enabled.
        if not features.get("import_helper_enabled", False):
            if features.get("data_ingestion_enabled", False):
                print(
                    f"[Bootloader] WARNING: data_ingestion_enabled=True ignored — "
                    f"import_helper_enabled=False in {path.name}"
                )
                features["data_ingestion_enabled"] = False

        # Deployment-profile override: data_ingestion_enabled:false in profile is absolute
        # (automated-pipeline deployments push data; user cannot upload).
        if self.connector_config.get("data_ingestion_enabled") is False:
            features["data_ingestion_enabled"] = False

        config["features"] = features
        return config

    def get_location(self, key: str) -> Path:
        """Returns the resolved path for a specific location key.

        Paths come from connector.resolve_paths() — project_root and deployment
        context are already applied. This is the authoritative source.
        """
        if key not in self._resolved_locations:
            raise KeyError(f"Location key '{key}' not defined in connector.")
        return self._resolved_locations[key]

    # Features that default TRUE when not declared in a persona template.
    # Everything else defaults False (opt-in).
    _FEATURES_DEFAULT_TRUE = {"show_persona_badge", "data_import_panel_visible"}

    def is_enabled(self, feature: str) -> bool:
        """Checks if a UI feature is enabled."""
        default = feature in self._FEATURES_DEFAULT_TRUE
        return self.features.get(feature, default)

    def get_theme_css_path(self) -> Path:
        """Returns the CSS theme file for this persona (theme_css key, defaults to config/ui/theme.css)."""
        css_rel = self.config.get("theme_css", "config/ui/theme.css")
        return Path(css_rel)

    def get_ui_banner(self) -> dict | None:
        """Returns ui_banner config dict {logo_url, title, subtitle} or None if not set."""
        return self.config.get("ui_banner") or None

    def get_manifest_selector(self) -> dict:
        """Returns the manifest_selector block: {visible: bool, fixed_manifest: str|None}."""
        return self.config.get("manifest_selector", {"visible": True, "fixed_manifest": None})

    def get_testing_mode(self) -> bool:
        """Returns testing_mode flag (true = pre-fill data selector from manifest defaults)."""
        return bool(self.config.get("testing_mode", True))

    def get_automation_setting(self, key: str, subkey: str) -> Any:
        """Returns automation settings (e.g., ghost_save frequency)."""
        return self.automation.get(key, {}).get(subkey)

    def get_script_path(self, key: str) -> Path:
        """Resolves system script paths from connector config (ADR-032)."""
        mapping = self.connector_config.get("scripts", {})
        path_str = mapping.get(key)
        if not path_str:
            raise KeyError(
                f"Script key '{key}' not found in connector 'scripts' block.")
        return Path(path_str)

    def get_python_path(self) -> str:
        """Retrieves the configured Python interpreter path (ADR-031)."""
        runtime = self.connector_config.get("runtime", {})
        path = runtime.get("python_interpreter")
        if not path:
            raise KeyError(
                "Connector config missing 'runtime.python_interpreter' definition.")
        return str(path)


# Global Instance for UI/Server discovery
bootloader = Bootloader()
