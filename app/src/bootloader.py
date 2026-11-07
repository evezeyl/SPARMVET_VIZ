# @deps
# provides: Bootloader (class), bootloader (global singleton instance), SidebarConfig (dataclass), method:get_agent_config, method:get_agent_adapter, method:get_palettes
# consumes: yaml, os, pathlib, typing, dataclasses, connector (get_connector), app.modules.deployment_error, blueprint_arch.agent_adapter (deferred import)
# consumed_by: app.src.server, app.src.ui, app.handlers.home_theater, app.handlers.blueprint_handlers, app.handlers.gallery_handlers, app.handlers.ingestion_handlers, app.modules.sidebar_registry
# doc: ADR-031, ADR-026, ADR-048, ADR-073, ADR-076, ADR-078, project_conventions.md §"Deployment Resolution"
# @end_deps
# app/src/bootloader.py
#
# Deployment resolution chain (ADR-048 §4) — first match wins:
#   Level 1: SPARMVET_DEPLOYMENT env var       — Galaxy XML, IRIDA, Docker Compose, systemd
#   Level 2: ~/.sparmvet/deployment.yaml        — local PC (scientist/admin places once)
#   Level 3: /etc/sparmvet/deployment.yaml      — institutional server (sysadmin places at deploy)
#   Level 4: config/deployment/local/local.yaml — developer repo fallback
#
# Connector lifecycle (ADR-048 §5, Option B):
#   After deployment load, the appropriate connector is instantiated via get_connector().
#   connector.fetch_data() runs first (no-op for filesystem/Galaxy; downloads for IRIDA).
#   connector.resolve_paths() is then the authoritative source for all location paths.
#   get_location() reads from those resolved paths directly.
import yaml
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Dict, Any

from app.modules.deployment_error import DeploymentError, exit_if_errors
from utils.path_expansion import expand_deployment_paths
from app.modules.renamed_keys import (
    renamed_app_features_key_errors,
    renamed_deployment_key_errors,
    renamed_env_var_errors,
)

_BOOT_REF = "ADR-048 — .claude/rules/rules_runtime_environment.md §1"


@dataclass
class SidebarConfig:
    """Resolved sidebar configuration for one workspace × side combination (ADR-073)."""
    visible: bool = True
    panels: list = field(default_factory=list)

_RESOLUTION_LEVEL_LABELS = {
    1: "SPARMVET_DEPLOYMENT env var",
    2: "~/.sparmvet/deployment.yaml (user-level)",
    3: "/etc/sparmvet/deployment.yaml (system-level)",
    4: "config/deployment/local/local.yaml (dev fallback)",
}


class Bootloader:
    """
    System Bootloader (ADR-031, ADR-026, ADR-048).
    Handles path authority, UI app features feature toggling, and deployment resolution.

    Deployment resolution chain (ADR-048 §4):
        1. SPARMVET_DEPLOYMENT env var  — explicit path; used by Galaxy/IRIDA/Docker
        2. ~/.sparmvet/deployment.yaml  — user-level; local PC without env var
        3. /etc/sparmvet/deployment.yaml — system-level; admin-placed on server
        4. config/deployment/local/local.yaml — repo dev fallback

    See project_conventions.md §"Deployment Resolution" for full details.
    """
    # ADR-031: Static Cache Layer
    _app_features_cache: Dict[str, Dict[str, Any]] = {}
    _deployment_cache: Dict[str, Dict[str, Any]] = {}          # keyed by resolved deployment path string
    _resolved_locations_cache: Dict[str, Dict[str, Path]] = {}  # keyed by resolved deployment path string

    # Hierarchical Asset Cache: data_analysis_recipe_id -> dataset_id -> plot_id -> asset_type -> asset
    _asset_cache: Dict[str, Dict[str, Dict[str, Dict[str, Any]]]] = {}

    def get_cached_asset(self, data_analysis_recipe_id: str, dataset_id: str, plot_id: str, asset_type: str) -> Any:
        try:
            return self._asset_cache[data_analysis_recipe_id][dataset_id][plot_id][asset_type]
        except KeyError:
            return None

    def set_cached_asset(self, data_analysis_recipe_id: str, dataset_id: str, plot_id: str, asset_type: str, asset: Any):
        if data_analysis_recipe_id not in self._asset_cache:
            self._asset_cache[data_analysis_recipe_id] = {}
        if dataset_id not in self._asset_cache[data_analysis_recipe_id]:
            self._asset_cache[data_analysis_recipe_id][dataset_id] = {}
        if plot_id not in self._asset_cache[data_analysis_recipe_id][dataset_id]:
            self._asset_cache[data_analysis_recipe_id][dataset_id][plot_id] = {}
        self._asset_cache[data_analysis_recipe_id][dataset_id][plot_id][asset_type] = asset

    def __init__(self, app_features: str | None = None):
        exit_if_errors(renamed_env_var_errors(os.environ))
        # App features resolved after deployment load — see step 2 below
        self._app_features_kwarg = app_features

        # 1. Path Authority — 4-level deployment resolution (ADR-048 §4)
        self.deployment_path, self.deployment_level = self._resolve_deployment_path()
        print(
            f"[Bootloader] Deployment resolved at level {self.deployment_level} "
            f"({_RESOLUTION_LEVEL_LABELS[self.deployment_level]}): {self.deployment_path}"
        )

        # Load deployment (cached by resolved absolute path)
        _cache_key = str(self.deployment_path.resolve())
        if _cache_key not in self._deployment_cache:
            self._deployment_cache[_cache_key] = self._load_deployment_config()
        self.deployment_config = self._deployment_cache[_cache_key]
        exit_if_errors(renamed_deployment_key_errors(self.deployment_config, str(self.deployment_path)))

        # ADR-048 deployment fields (all optional in local dev deployment)
        project_root_str = self.deployment_config.get("project_root")
        self.project_root: Path | None = Path(project_root_str) if project_root_str else None
        self.default_data_analysis_recipe: str | None = self.deployment_config.get("default_data_analysis_recipe")
        self.default_app_features: str | None = self.deployment_config.get("default_app_features")
        self.data_lookup: str = self.deployment_config.get("data_lookup", "data_analysis_recipe_paths")
        self.deployment_name: str = self.deployment_config.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
        self.deployment_type: str = self.deployment_config.get("deployment_type", "filesystem")

        # Connector lifecycle (ADR-048 §5, Option B):
        # fetch_data() runs once at startup — no-op for filesystem/Galaxy, downloads for IRIDA.
        # resolve_paths() is then the single authoritative source for all location paths.
        if _cache_key not in self._resolved_locations_cache:
            try:
                from connector import get_connector
                _conn = get_connector(self.deployment_config)
                print(f"[Bootloader] Connector: {_conn.__class__.__name__} — fetch_data()")
                _conn.fetch_data()
                self._resolved_locations_cache[_cache_key] = _conn.resolve_paths()
            except Exception as _exc:
                exit_if_errors([DeploymentError(
                    component="Bootloader",
                    problem=f"Connector initialisation failed: {_exc}",
                    location=str(self.deployment_path),
                    fix=(
                        "Check that all credentials and endpoints declared in the deployment "
                        "deployment are reachable. For IridaConnector: verify SPARMVET_IRIDA_TOKEN "
                        "is set and the IRIDA server is accessible. For BioBlendConnector: verify "
                        "GALAXY_URL and GALAXY_API_KEY. For FilesystemConnector: verify path "
                        "entries under 'locations:' exist on disk."
                    ),
                    who="operator",
                    reference=_BOOT_REF,
                )])
        self._resolved_locations: Dict[str, Path] = self._resolved_locations_cache[_cache_key]

        # Keep raw locations dict for backward compat (key validation only)
        self.locations = self.deployment_config.get("locations", {})

        # Validate required location keys
        self._validate_deployment()

        # 2. App features logic — resolution order: kwarg > env var > deployment default_app_features > error
        self.app_features = (
            self._app_features_kwarg
            or os.environ.get("SPARMVET_APP_FEATURES")
            or self.default_app_features
        )
        if not self.app_features:
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem="No app features configured — cannot determine which feature flags to load.",
                location=(
                    "Resolution order checked: app_features= kwarg, SPARMVET_APP_FEATURES env var, "
                    f"default_app_features in {self.deployment_path} — all absent."
                ),
                fix=(
                    "Set the SPARMVET_APP_FEATURES environment variable (e.g. SPARMVET_APP_FEATURES=developer), "
                    f"or add 'default_app_features: developer' to {self.deployment_path}."
                ),
                who="operator",
                reference=_BOOT_REF,
            )])
        self.set_app_features(self.app_features)

        # 3. Data analysis recipes folder (agnostic discovery)
        self.data_analysis_recipes_dir = self.get_location("data_analysis_recipes")
        self.available_data_analysis_recipes = self._discover_data_analysis_recipes()
        self.default_data_analysis_recipe_name = self._resolve_default_data_analysis_recipe()

    def _resolve_deployment_path(self) -> tuple[Path, int]:
        """
        Resolve the deployment path via the 4-level priority chain (ADR-048 §4).

        Returns (resolved_path, level) where level ∈ {1, 2, 3, 4}.

        Raises FileNotFoundError if:
        - SPARMVET_DEPLOYMENT is set but points to a non-existent file (hard error — misconfiguration).
        - No deployment is found at any level (shows all checked paths in the message).

        Resolution order (first match wins):
            1. SPARMVET_DEPLOYMENT env var  — Galaxy XML, IRIDA container launch, Docker Compose, systemd
            2. ~/.sparmvet/deployment.yaml  — local PC (scientist or admin places this once at setup)
            3. /etc/sparmvet/deployment.yaml — institutional server (sysadmin places at deploy time)
            4. config/deployment/local/local.yaml — developer running from repo root
        """
        # Level 1: explicit env var — fail hard if set but missing (misconfiguration, not "not found")
        env_deployment = os.environ.get("SPARMVET_DEPLOYMENT")
        if env_deployment:
            p = Path(env_deployment)
            if not p.exists():
                exit_if_errors([DeploymentError(
                    component="Bootloader",
                    problem=(
                        f"SPARMVET_DEPLOYMENT env var is set to '{env_deployment}' "
                        f"but the file does not exist."
                    ),
                    location=f"SPARMVET_DEPLOYMENT={env_deployment}",
                    fix=(
                        f"Either create the deployment file at '{env_deployment}', "
                        f"correct the path in SPARMVET_DEPLOYMENT, or unset the variable "
                        f"to fall through to lower-priority deployment locations."
                    ),
                    who="operator",
                    reference=_BOOT_REF,
                )])
            return p, 1

        # Level 2: user-level config
        user_deployment = Path.home() / ".sparmvet" / "deployment.yaml"
        if user_deployment.exists():
            return user_deployment, 2

        # Level 3: system-level config
        system_deployment = Path("/etc/sparmvet/deployment.yaml")
        if system_deployment.exists():
            return system_deployment, 3

        # Level 4: dev repo fallback
        dev_fallback = Path("config/deployment/local/local.yaml")
        if dev_fallback.exists():
            return dev_fallback, 4

        exit_if_errors([DeploymentError(
            component="Bootloader",
            problem="No deployment found at any resolution level.",
            location=(
                f"Checked: (1) SPARMVET_DEPLOYMENT env var (not set), "
                f"(2) {Path.home() / '.sparmvet' / 'deployment.yaml'} (not found), "
                f"(3) /etc/sparmvet/deployment.yaml (not found), "
                f"(4) {dev_fallback} (not found)"
            ),
            fix=(
                "Create a deployment at config/deployment/local/local.yaml "
                "(copy from config/deployment/local/local.yaml.example if available), "
                "or set SPARMVET_DEPLOYMENT to an absolute path to your deployment file."
            ),
            who="operator",
            reference=_BOOT_REF,
        )])
        raise FileNotFoundError("unreachable")  # satisfies type checker

    def _validate_deployment(self) -> None:
        """Exit with DeploymentError if required location keys are missing from resolved paths."""
        errors = []
        if self.data_lookup not in ("data_analysis_recipe_paths", "by_dataset_id"):
            errors.append(DeploymentError(
                component="Bootloader",
                problem=f"data_lookup '{self.data_lookup}' is not a valid choice",
                location=f"data_lookup in {self.deployment_path}",
                fix="Use data_analysis_recipe_paths (data from the source.path of the data analysis recipe) or by_dataset_id (data delivered into raw_data as <dataset id>.tsv).",
                who="operator",
                reference=_BOOT_REF,
            ))
        exit_if_errors(errors)
        required = {"raw_data", "data_analysis_recipes", "cache", "user_data", "gallery"}
        missing = required - set(self._resolved_locations.keys())
        if missing:
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem=(
                    f"Deployment is missing required location keys: "
                    f"{sorted(missing)}"
                ),
                location=str(self.deployment_path),
                fix=(
                    f"Add the missing keys to the 'locations:' block in {self.deployment_path}. "
                    f"Required keys: raw_data, data analysis recipes, cache, user_data, gallery. "
                    f"See config/deployment/local/local.yaml for reference values."
                ),
                who="operator",
                reference=_BOOT_REF,
            )])

    def set_app_features(self, app_features: str):
        """Load an app features file from a path or a short name.

        Accepts:
          - Absolute path: /path/to/my_app_features.yaml
          - Relative path: config/app_features/developer.yaml
          - Short name: developer  →  config/app_features/developer.yaml
        """
        self.app_features = app_features
        p = Path(app_features)
        if "/" in app_features or "\\" in app_features or app_features.endswith(".yaml"):
            self.app_features_path = p.resolve()
        else:
            # Short name: a file in config/app_features/
            self.app_features_path = Path(
                f"config/app_features/{app_features}.yaml").resolve()

        cache_key = str(self.app_features_path)
        if cache_key not in self._app_features_cache:
            self._app_features_cache[cache_key] = self._load_app_features_config()

        self.config = self._app_features_cache[cache_key]
        print(f"[Bootloader] App features: {self.app_features} → {self.app_features_path}")
        # Operator lock: app_features_override in the deployment file is absolute, for example
        # data_ingestion_enabled: false when a pipeline always pushes the data. Applied per
        # instance, never into the cache shared by the class (it is keyed by file only).
        self.flags = {**self.config.get("flags", {}),
                      **(self.deployment_config.get("app_features_override") or {})}
        self.automation = self.config.get("automation", {})

    @property
    def app_features_display_name(self) -> str:
        """Human-readable app features name from the template's display_name field.

        Falls back to name, then to the raw app features value (path or shortname).
        Used for UI display only — never for behavioral gating.
        """
        return (
            self.config.get("display_name")
            or self.config.get("name")
            or self.app_features
        )

    def _discover_data_analysis_recipes(self) -> Dict[str, str]:
        """Scans the project directory for YAML data analysis recipes."""
        mf_files = list(self.data_analysis_recipes_dir.glob("*.yaml"))
        return {f.stem: str(f) for f in mf_files}

    def _resolve_default_data_analysis_recipe(self) -> str | None:
        """SPARMVET_DATA_ANALYSIS_RECIPE, then default_data_analysis_recipe of the deployment.

        A named data analysis recipe that is not in the data analysis recipes folder, or a hidden selector with nothing
        named, is an operator mistake and stops the app (ADR-077, ADR-091)."""
        source, name = None, None
        if os.environ.get("SPARMVET_DATA_ANALYSIS_RECIPE"):
            source, name = "SPARMVET_DATA_ANALYSIS_RECIPE", os.environ["SPARMVET_DATA_ANALYSIS_RECIPE"]
        elif self.default_data_analysis_recipe:
            source, name = "default_data_analysis_recipe", str(self.default_data_analysis_recipe)
        if name:
            if name not in self.available_data_analysis_recipes:
                exit_if_errors([DeploymentError(
                    component="Bootloader",
                    problem=f"The data analysis recipe '{name}' named by {source} was not found.",
                    location=f"{source} (data analysis recipes folder: {self.data_analysis_recipes_dir})",
                    fix=("Use the file name without .yaml of a data analysis recipe in the data analysis recipes folder. "
                         f"Found: {sorted(self.available_data_analysis_recipes) or 'none'}."),
                    who="operator", reference=_BOOT_REF,
                )])
            return name
        if not self.get_data_analysis_recipe_selector().get("visible", True):
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem="The app features hide the data analysis recipe selector but no data analysis recipe is named.",
                location="default_data_analysis_recipe in the deployment file and SPARMVET_DATA_ANALYSIS_RECIPE",
                fix="Name the data analysis recipe that opens: set default_data_analysis_recipe in the deployment file "
                    "(or SPARMVET_DATA_ANALYSIS_RECIPE for one run).",
                who="operator", reference=_BOOT_REF,
            )])
        return None

    def get_default_data_analysis_recipe(self) -> str:
        """The data analysis recipe that opens at startup (ADR-091): the launch variable, then the
        deployment default, otherwise the first available one (the user chooses when the
        selector is shown)."""
        if self.default_data_analysis_recipe_name:
            return self.default_data_analysis_recipe_name
        if not self.available_data_analysis_recipes:
            raise FileNotFoundError("No data analysis recipes found in Location 2.")
        return list(self.available_data_analysis_recipes.keys())[0]

    def _load_deployment_config(self) -> Dict[str, Any]:
        """Loads the deployment file."""
        if not self.deployment_path.exists():
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem=f"Deployment file not found: {self.deployment_path}",
                location=str(self.deployment_path),
                fix=(
                    "Ensure the deployment file exists at the resolved path. "
                    "For local dev: copy config/deployment/local/local.yaml.example "
                    "to config/deployment/local/local.yaml and fill in the location paths."
                ),
                who="operator",
                reference=_BOOT_REF,
            )])
            return {}  # unreachable

        try:
            with open(self.deployment_path, "r") as f:
                data = yaml.safe_load(f) or {}
            # ~ and ${VAR} in the folders of the deployment (ADR-091); an unset variable stops the app
            exit_if_errors(expand_deployment_paths(data, str(self.deployment_path)))
            return data
        except Exception as e:
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem=f"Failed to parse deployment '{self.deployment_path}': {e}",
                location=str(self.deployment_path),
                fix=(
                    f"Check {self.deployment_path} for YAML syntax errors. "
                    f"Run: python -c \"import yaml; yaml.safe_load(open('{self.deployment_path}'))\" "
                    f"to surface the parse error line."
                ),
                who="operator",
                reference=_BOOT_REF,
            )])
            return {}  # unreachable

    def _load_app_features_config(self) -> Dict[str, Any]:
        """Loads UI feature toggles from the app features file and applies dependency cascade.

        Cascade rules (rules_app_features_flags.md §107–127):
          - interactivity_enabled=False suppresses t3_sandbox/comparison/session/export_graph/audit_report
          - import_helper_enabled=False suppresses data_ingestion_enabled
          - Deployment data_ingestion_enabled:false is an absolute override

        Group D cascades (data_analysis_recipe_edit_enabled, blueprint_agent_enabled) are NOT
        silently suppressed here — they are fatal validator errors raised by
        AppFeaturesValidator at startup (Rule 7). If you wrote them on while
        blueprint_enabled=False, the app refuses to start. See
        rules_app_features_flags.md Cascade Enforcement §4–5.
        A WARNING is printed for each flag that was True in the template and forced False.

        Supports !include in app features files (paths relative to the template file).
        Uses a subclass of SafeLoader to avoid polluting the global constructor registry.
        """
        path = self.app_features_path
        if not path.exists():
            from app.modules.renamed_keys import RENAMED_APP_FEATURES_NAMES
            renamed = RENAMED_APP_FEATURES_NAMES.get(path.stem)
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem=(f"App features file not found: {path}"
                         + (f" ('{path.stem}' was renamed to '{renamed}')" if renamed else "")),
                location=str(path),
                fix=(
                    (f"Use '{renamed}' in SPARMVET_APP_FEATURES or default_app_features. " if renamed else "") +
                    f"Ensure the app features file exists at {path}. "
                    f"Valid names (files in config/app_features/): "
                    f"pipeline-static, pipeline-exploration-simple, pipeline-exploration-advanced, "
                    f"standalone, developer, qa. "
                    f"Check SPARMVET_APP_FEATURES env var or default_app_features in the deployment."
                ),
                who="operator",
                reference="ADR-026 + config/app_features/",
            )])
            return {}  # unreachable

        try:
            class _TemplateLoader(yaml.SafeLoader):
                pass

            def _include_constructor(loader: yaml.SafeLoader, node: yaml.Node) -> Any:
                rel = loader.construct_scalar(node)
                abs_inc = path.parent / rel
                try:
                    with open(abs_inc) as inc_f:
                        return yaml.safe_load(inc_f) or {}
                except FileNotFoundError:
                    print(f"[Bootloader] WARNING: !include target not found: {abs_inc}")
                    return {}

            _TemplateLoader.add_constructor("!include", _include_constructor)

            with open(path, "r") as f:
                config = yaml.load(f, Loader=_TemplateLoader) or {}
            exit_if_errors(renamed_app_features_key_errors(config, str(path)))
        except Exception as e:
            exit_if_errors([DeploymentError(
                component="Bootloader",
                problem=f"Failed to parse app features file '{path}': {e}",
                location=str(path),
                fix=(
                    f"Check {path} for YAML syntax errors. "
                    f"Run: python -c \"import yaml; yaml.safe_load(open('{path}'))\" "
                    f"to surface the parse error line. "
                    f"Also verify that all !include paths under 'workspaces:' exist in "
                    f"config/ui/sidebars/."
                ),
                who="operator",
                reference="ADR-026 + config/app_features/",
            )])
            return {}  # unreachable

        features = config.get("flags", {})

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

        # FLAG-2: mirror data_analysis_recipe_selector.visible into features for is_enabled() access.
        ms = config.get("data_analysis_recipe_selector", {})
        if "data_analysis_recipe_selector_visible" not in features:
            features["data_analysis_recipe_selector_visible"] = bool(ms.get("visible", True))

        # Group B: interactivity_enabled=False suppresses all interactive child flags.
        if not features.get("interactivity_enabled", False):
            for child in ("t3_sandbox_enabled", "comparison_mode_enabled",
                          "session_management_enabled"):
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

        # NOTE: Group D cascades (data_analysis_recipe_edit_enabled, blueprint_agent_enabled) are
        # intentionally NOT silently suppressed here. AppFeaturesValidator Rule 7 raises a
        # fatal error at startup if a template declares them on while blueprint_enabled=False.
        # The flag value passes through this loader unchanged so the validator sees the
        # user's actual intent (rather than a silently-rewritten "safe" version).

        config["flags"] = features
        return config

    def get_location(self, key: str) -> Path:
        """Returns the resolved path for a specific location key.

        Paths come from connector.resolve_paths() — project_root and deployment
        context are already applied. This is the authoritative source.
        """
        if key not in self._resolved_locations:
            raise KeyError(f"Location key '{key}' not defined in connector.")
        return self._resolved_locations[key]

    # Features that default TRUE when not declared in an app features file.
    # Everything else defaults False (opt-in).
    _FEATURES_DEFAULT_TRUE = {"show_app_features_badge"}

    def is_enabled(self, feature: str) -> bool:
        """Checks if a UI feature is enabled."""
        default = feature in self._FEATURES_DEFAULT_TRUE
        return self.flags.get(feature, default)

    def get_theme_css_path(self) -> Path:
        """Returns the CSS theme file for this app features (theme_css key, defaults to config/ui/theme.css)."""
        css_rel = (self.deployment_config.get("branding") or {}).get("theme_css", "config/ui/theme.css")
        return Path(css_rel)

    def get_ui_banner(self) -> dict | None:
        """Returns the banner dict {logo_url, title, subtitle} of the deployment's branding, or None."""
        return (self.deployment_config.get("branding") or {}).get("banner") or None

    def get_data_analysis_recipe_selector(self) -> dict:
        """Returns the data_analysis_recipe_selector block: {visible: bool}."""
        return self.config.get("data_analysis_recipe_selector", {"visible": True})

    def get_sidebar_config(self, workspace: str, side: str) -> "SidebarConfig":
        """Returns the resolved sidebar configuration for the given workspace and side.

        Reads workspaces.<workspace>.<side>_sidebar from the active app features file.
        !include references in the template are resolved at load time by _load_app_features_config().

        Default when not defined: left=visible with no panels, right=not visible.
        """
        workspaces = self.config.get("workspaces", {})
        ws_cfg = workspaces.get(workspace, {})
        sb_data = ws_cfg.get(f"{side}_sidebar")
        if not sb_data:
            return SidebarConfig(visible=(side == "left"), panels=[])
        return SidebarConfig(
            visible=bool(sb_data.get("visible", True)),
            panels=sb_data.get("panels", []),
        )

    def get_testing_mode(self) -> bool:
        """Returns testing_mode flag (true = pre-fill data selector from data analysis recipe defaults)."""
        return bool(self.config.get("testing_mode", True))

    def get_automation_setting(self, key: str, subkey: str) -> Any:
        """Returns automation settings (e.g., ghost_save frequency)."""
        return self.automation.get(key, {}).get(subkey)

    def get_python_path(self) -> str:
        """Retrieves the configured Python interpreter path (ADR-031)."""
        runtime = self.deployment_config.get("runtime", {})
        path = runtime.get("python_interpreter")
        if not path:
            raise KeyError(
                "Connector config missing 'runtime.python_interpreter' definition.")
        return str(path)

    # Built-in SPARMVET brand palette — always present so the system has a safe default.
    # Uses the authoritative brand colors from rules_css_style_spec.md §1c.
    _BUILTIN_PALETTES: dict = {
        "sparmvet_brand": [
            "#345beb",  # Blue — primary action
            "#10a395",  # Teal — export/upload
            "#ffc107",  # Amber — warning/pending
            "#d62828",  # Red — error/destructive
            "#6c757d",  # Grey — muted
            "#6a4c93",  # Violet — audit nodes
        ]
    }

    def get_palettes(self) -> dict:
        """Load deployment palette registry from config/palettes.yaml (BP-COLOR-2).

        Returns {name: [hex, ...]} merged dict: built-in SPARMVET palettes plus any
        deployment-defined palettes from config/palettes.yaml. Deployment palettes override
        built-ins when names collide (intentional — institutions can rebrand defaults).

        Never returns an empty dict — the built-in 'sparmvet_brand' palette is always
        present so callers always have at least one option.

        Diagnostics: if config/palettes.yaml exists but cannot be loaded, a WARNING is
        printed with the file path and the exact exception so the operator can fix it.
        """
        if hasattr(self, "_palettes_cache"):
            return self._palettes_cache

        # Always start from built-ins — deployment palettes are merged on top
        result = dict(self._BUILTIN_PALETTES)

        palette_path = Path("config/palettes.yaml")
        if not palette_path.exists():
            # File is optional — INFO only, not a warning
            print(
                f"[Bootloader] INFO: no deployment palette file at "
                f"'{palette_path}'. Using built-in palettes only "
                f"({list(result.keys())}). To add deployment palettes, create "
                f"config/palettes.yaml — see the file header for the required format."
            )
        else:
            try:
                with open(palette_path) as f:
                    raw = yaml.safe_load(f)
                if not isinstance(raw, dict):
                    raise ValueError(
                        f"Expected a YAML mapping at the top level, got {type(raw).__name__}. "
                        f"The file must start with 'palettes:' and contain named palette entries."
                    )
                deployment_palettes = raw.get("palettes")
                if not isinstance(deployment_palettes, dict):
                    raise ValueError(
                        f"'palettes:' key is missing or not a mapping. "
                        f"Each palette must be a named list of hex strings, e.g.:\n"
                        f"  palettes:\n"
                        f"    my_palette:\n"
                        f"      - \"#1D5B8B\"\n"
                        f"      - \"#E8A020\""
                    )
                # Validate individual entries and warn on bad ones (don't discard the whole file)
                loaded_count = 0
                for name, colors in deployment_palettes.items():
                    if not isinstance(colors, list) or not colors:
                        print(
                            f"[Bootloader] WARNING: palette '{name}' in "
                            f"'{palette_path}' is not a non-empty list — skipped. "
                            f"Each palette must be a list of hex strings."
                        )
                        continue
                    result[name] = [str(c) for c in colors]
                    loaded_count += 1
                print(
                    f"[Bootloader] Loaded {loaded_count} deployment palette(s) from "
                    f"'{palette_path}': {[k for k in deployment_palettes if k in result]}"
                )
            except Exception as exc:
                print(
                    f"[Bootloader] WARNING: could not load palette registry from "
                    f"'{palette_path.resolve()}': {exc}. "
                    f"Falling back to built-in palettes. Fix the file and restart to "
                    f"activate deployment palettes."
                )
                # result already contains built-ins — no data loss

        self._palettes_cache = result
        return self._palettes_cache

    def get_agent_config(self) -> dict:
        """Return the blueprint_agent: block from the active app features file.

        Returns an empty dict if the block is absent (e.g. non-developer app features files).
        Callers should gate on is_enabled('blueprint_agent_enabled') before using.
        """
        return self.config.get("blueprint_agent", {})

    def get_agent_adapter(self):
        """Instantiate and cache the BLUEPRINT AI agent adapter (ADR-076).

        Returns a ClaudeCliAdapter when blueprint_agent_enabled=True and the
        configured backend initialises successfully. Falls back to DisabledAdapter
        on any failure — startup is never blocked.

        The adapter is cached per-bootloader instance after the first call.
        """
        if hasattr(self, "_agent_adapter_cache"):
            return self._agent_adapter_cache

        if not self.is_enabled("blueprint_agent_enabled"):
            from blueprint_arch.agent_adapter import DisabledAdapter
            self._agent_adapter_cache = DisabledAdapter(
                "blueprint_agent_enabled is false for this app features."
            )
            return self._agent_adapter_cache

        cfg = self.get_agent_config()
        backend = cfg.get("backend", "disabled")
        instructions_file = cfg.get("instructions_file")

        from blueprint_arch.agent_adapter import make_adapter
        adapter = make_adapter(
            backend=backend,
            project_root=self.project_root or Path("."),
            instructions_file=instructions_file,
        )
        self._agent_adapter_cache = adapter
        return adapter


# Global Instance for UI/Server discovery
bootloader = Bootloader()
