# @deps
# provides: class:SidebarValidator
# consumes: app/modules/sidebar_registry.py, app/modules/deployment_error.py, config/ui/templates/*.yaml, config/ui/sidebars/*.yaml
# consumed_by: app/src/server.py, scripts/validate_persona_config.py
# doc: .claude/rules/ui_implementation_contract.md §11, .claude/rules/rules_ui_dashboard.md §2
# @end_deps
"""
SidebarValidator — checks workspaces sidebar configs in persona templates (ADR-073).

Runs alongside PersonaValidator at app startup. Returns list[DeploymentError] (ADR-078
Phase C, DIAG-VALIDATE-SIDEBAR-1). Errors block startup; informational notes are printed.
"""

from pathlib import Path
import yaml

from app.modules.sidebar_registry import PANEL_REGISTRY
from app.modules.deployment_error import DeploymentError

_WORKSPACES = ("home", "blueprint", "gallery", "test_lab")
_SIDES = ("left", "right")

_WORKSPACE_GATE_FLAGS: dict[str, str | None] = {
    "home":      None,
    "blueprint": "blueprint_enabled",
    "gallery":   "gallery_enabled",
    "test_lab":  "test_lab_enabled",
}

_REF = "ADR-073 + .claude/rules/ui_implementation_contract.md §11"


class SidebarValidator:
    """Validates workspaces sidebar configs in a persona template (ADR-073).

    Call validate() with the already-parsed template dict and its file path.
    Returns list[DeploymentError] (empty = valid). Informational notes are printed.
    """

    def validate(self, template: dict, template_path: str) -> list[DeploymentError]:
        """Return a list of DeploymentError records. Prints informational notes. Empty = valid."""
        errors: list[DeploymentError] = []
        workspaces = template.get("workspaces")

        if workspaces is None:
            print(
                f"[SidebarValidator] WARNING: '{template_path}' has no 'workspaces:' section "
                f"— sidebar slot registry not configured, bootloader defaults apply."
            )
            return errors

        features = template.get("features", {})
        persona_id = template.get("persona_id", template_path)

        if "manifest_selector_visible" not in features:
            ms = template.get("manifest_selector", {})
            features = dict(features)
            features["manifest_selector_visible"] = bool(ms.get("visible", True))

        for ws in _WORKSPACES:
            ws_cfg = workspaces.get(ws)
            if ws_cfg is None:
                continue

            for side in _SIDES:
                sb = ws_cfg.get(f"{side}_sidebar")
                if sb is None:
                    continue

                loc_key = f"workspaces.{ws}.{side}_sidebar"
                loc = f"{loc_key} in {template_path}"

                if not isinstance(sb, dict):
                    errors.append(DeploymentError(
                        component="SidebarValidator",
                        problem=(
                            f"[{persona_id}] {loc_key} must be a mapping dict "
                            f"(got {type(sb).__name__}) — likely a broken !include path."
                        ),
                        location=loc,
                        fix=(
                            f"Check the !include target for {loc_key} in {template_path}. "
                            f"Ensure the referenced YAML file exists under config/ui/sidebars/ "
                            f"and is a valid mapping with 'visible' and 'panels' keys."
                        ),
                        who="operator",
                        reference=_REF,
                    ))
                    continue

                visible = sb.get("visible", True)
                panels = sb.get("panels", [])

                if not isinstance(panels, list):
                    errors.append(DeploymentError(
                        component="SidebarValidator",
                        problem=f"[{persona_id}] {loc_key}.panels must be a list.",
                        location=f"{loc_key}.panels in {template_path}",
                        fix=(
                            f"Edit {template_path}: set {loc_key}.panels to a YAML sequence. "
                            f"Example:\n"
                            f"  {loc_key}:\n"
                            f"    visible: true\n"
                            f"    panels:\n"
                            f"      - type: project_info"
                        ),
                        who="operator",
                        reference=_REF,
                    ))
                    continue

                for slot in panels:
                    if not isinstance(slot, dict):
                        errors.append(DeploymentError(
                            component="SidebarValidator",
                            problem=(
                                f"[{persona_id}] {loc_key}: panel entry must be a dict "
                                f"with a 'type' key, got {slot!r}."
                            ),
                            location=f"{loc_key}.panels[] in {template_path}",
                            fix=(
                                f"Edit {template_path}: each entry under {loc_key}.panels "
                                f"must be a mapping. Replace bare values with '- type: <panel_type>'. "
                                f"Known panel types: {list(PANEL_REGISTRY.keys())}."
                            ),
                            who="operator",
                            reference=_REF,
                        ))
                        continue

                    ptype = slot.get("type", "")
                    if not ptype:
                        errors.append(DeploymentError(
                            component="SidebarValidator",
                            problem=f"[{persona_id}] {loc_key}: panel entry missing 'type' key.",
                            location=f"{loc_key}.panels[] in {template_path}",
                            fix=(
                                f"Edit {template_path}: add 'type: <panel_type>' to the "
                                f"panel entry under {loc_key}.panels. "
                                f"Known panel types: {list(PANEL_REGISTRY.keys())}."
                            ),
                            who="operator",
                            reference=_REF,
                        ))
                        continue

                    if ptype not in PANEL_REGISTRY:
                        print(
                            f"[SidebarValidator] WARNING: [{persona_id}] "
                            f"{loc_key} contains unknown panel type '{ptype}'. "
                            f"Known types: {list(PANEL_REGISTRY.keys())}"
                        )
                        continue

                    gate = PANEL_REGISTRY[ptype]["gate_flag"]
                    if gate is not None and not features.get(gate, False):
                        print(
                            f"[SidebarValidator] NOTE: [{persona_id}] "
                            f"{loc_key} includes '{ptype}' "
                            f"but its gate flag '{gate}' is disabled — panel will be silently skipped."
                        )

                    if not visible and panels:
                        print(
                            f"[SidebarValidator] NOTE: [{persona_id}] "
                            f"{loc_key} has visible:false but "
                            f"declares {len(panels)} panel(s) — they will not be rendered."
                        )
                        break

        return errors

    def validate_file(self, template_path: str) -> list[DeploymentError]:
        """Load a persona template YAML and validate its workspaces section.

        Supports !include via a local SafeLoader subclass that resolves paths
        relative to the template file.
        """
        path = Path(template_path)
        if not path.exists():
            return [DeploymentError(
                component="SidebarValidator",
                problem=f"Persona template file not found: {template_path}",
                location=template_path,
                fix=(
                    f"Ensure the template file exists at {template_path}. "
                    f"Check SPARMVET_PERSONA env var and the deployment profile "
                    f"'default_persona' key."
                ),
                who="operator",
                reference=_REF,
            )]

        try:
            class _Loader(yaml.SafeLoader):
                pass

            def _include(loader: yaml.SafeLoader, node: yaml.Node):
                rel = loader.construct_scalar(node)
                abs_path = path.parent / rel
                try:
                    with open(abs_path) as f:
                        return yaml.safe_load(f) or {}
                except FileNotFoundError:
                    return f"__missing__: {abs_path}"

            _Loader.add_constructor("!include", _include)
            with open(path) as f:
                template = yaml.load(f, Loader=_Loader) or {}
        except Exception as e:
            return [DeploymentError(
                component="SidebarValidator",
                problem=f"Failed to parse template '{template_path}': {e}",
                location=template_path,
                fix=(
                    f"Check {template_path} for YAML syntax errors. "
                    f"Run: python -c \"import yaml; yaml.safe_load(open('{template_path}'))\" "
                    f"to surface the parse error."
                ),
                who="operator",
                reference=_REF,
            )]

        # Surface missing !include targets as errors
        errors: list[DeploymentError] = []
        for ws in _WORKSPACES:
            ws_cfg = (template.get("workspaces") or {}).get(ws, {})
            for side in _SIDES:
                val = ws_cfg.get(f"{side}_sidebar")
                if isinstance(val, str) and val.startswith("__missing__:"):
                    missing_path = val.replace("__missing__: ", "")
                    errors.append(DeploymentError(
                        component="SidebarValidator",
                        problem=(
                            f"!include target not found for "
                            f"workspaces.{ws}.{side}_sidebar in {template_path}."
                        ),
                        location=f"workspaces.{ws}.{side}_sidebar in {template_path}",
                        fix=(
                            f"Create the missing sidebar config file at: {missing_path}\n"
                            f"Or update the !include path under "
                            f"workspaces.{ws}.{side}_sidebar in {template_path} "
                            f"to point at an existing file in config/ui/sidebars/."
                        ),
                        who="operator",
                        reference=_REF,
                    ))

        if errors:
            return errors

        return self.validate(template, template_path)
