# @deps
# provides: class:SidebarValidator
# consumes: app/modules/sidebar_registry.py, config/ui/templates/*.yaml, config/ui/sidebars/*.yaml
# consumed_by: app/src/server.py, scripts/validate_persona_config.py
# doc: .claude/rules/ui_implementation_contract.md §11, .claude/rules/rules_ui_dashboard.md §2
# @end_deps
"""
SidebarValidator — checks workspaces sidebar configs in persona templates (ADR-073).

Runs alongside PersonaValidator at app startup. Warnings are non-fatal; errors block startup.
"""

from pathlib import Path
from typing import Optional
import yaml

from app.modules.sidebar_registry import PANEL_REGISTRY

_WORKSPACES = ("home", "blueprint", "gallery", "test_lab")
_SIDES = ("left", "right")

# Panels in the slot list whose gate flag is disabled produce an informational note only
# (silently skipped at runtime). Flag as a warning only if the slot is unreachable for
# every persona that would normally use that workspace (currently just informational).
_WORKSPACE_GATE_FLAGS: dict[str, str | None] = {
    "home":      None,
    "blueprint": "blueprint_enabled",
    "gallery":   "gallery_enabled",
    "test_lab":  "test_lab_enabled",
}


class SidebarValidator:
    """Validates workspaces sidebar configs in a persona template (ADR-073).

    Call validate() with the already-parsed template dict and its file path.
    Returns a list of error strings (empty = valid). Warnings are printed to stdout.
    """

    def validate(self, template: dict, template_path: str) -> list[str]:
        """Return a list of error strings. Prints warnings. Empty = valid."""
        errors: list[str] = []
        workspaces = template.get("workspaces")

        if workspaces is None:
            print(
                f"[SidebarValidator] WARNING: '{template_path}' has no 'workspaces:' section "
                f"— sidebar slot registry not configured, bootloader defaults apply."
            )
            return errors

        features = template.get("features", {})
        persona_id = template.get("persona_id", template_path)

        for ws in _WORKSPACES:
            ws_cfg = workspaces.get(ws)
            if ws_cfg is None:
                continue  # workspace not declared — defaults apply, not an error

            for side in _SIDES:
                sb = ws_cfg.get(f"{side}_sidebar")
                if sb is None:
                    continue

                if not isinstance(sb, dict):
                    errors.append(
                        f"[{persona_id}] workspaces.{ws}.{side}_sidebar must be a dict "
                        f"(got {type(sb).__name__}) — check !include path."
                    )
                    continue

                visible = sb.get("visible", True)
                panels = sb.get("panels", [])

                if not isinstance(panels, list):
                    errors.append(
                        f"[{persona_id}] workspaces.{ws}.{side}_sidebar.panels must be a list."
                    )
                    continue

                for slot in panels:
                    if not isinstance(slot, dict):
                        errors.append(
                            f"[{persona_id}] workspaces.{ws}.{side}_sidebar: "
                            f"panel entry must be a dict with a 'type' key, got {slot!r}."
                        )
                        continue

                    ptype = slot.get("type", "")
                    if not ptype:
                        errors.append(
                            f"[{persona_id}] workspaces.{ws}.{side}_sidebar: "
                            f"panel entry missing 'type' key."
                        )
                        continue

                    if ptype not in PANEL_REGISTRY:
                        print(
                            f"[SidebarValidator] WARNING: [{persona_id}] "
                            f"workspaces.{ws}.{side}_sidebar contains unknown "
                            f"panel type '{ptype}'. Known types: "
                            f"{list(PANEL_REGISTRY.keys())}"
                        )
                        continue

                    gate = PANEL_REGISTRY[ptype]["gate_flag"]
                    if gate is not None and not features.get(gate, False):
                        print(
                            f"[SidebarValidator] NOTE: [{persona_id}] "
                            f"workspaces.{ws}.{side}_sidebar includes '{ptype}' "
                            f"but its gate flag '{gate}' is disabled — panel will be silently skipped."
                        )

                    if not visible and panels:
                        print(
                            f"[SidebarValidator] NOTE: [{persona_id}] "
                            f"workspaces.{ws}.{side}_sidebar has visible:false but "
                            f"declares {len(panels)} panel(s) — they will not be rendered."
                        )
                        break  # only print once per sidebar

        return errors

    def validate_file(self, template_path: str) -> list[str]:
        """Load a persona template YAML and validate its workspaces section.

        Supports !include via a local SafeLoader subclass that resolves paths
        relative to the template file.
        """
        path = Path(template_path)
        if not path.exists():
            return [f"Template file not found: {template_path}"]

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
                    # Return a sentinel so the dict-type check in validate() catches it
                    return f"__missing__: {abs_path}"

            _Loader.add_constructor("!include", _include)
            with open(path) as f:
                template = yaml.load(f, Loader=_Loader) or {}
        except Exception as e:
            return [f"Failed to parse template '{template_path}': {e}"]

        # Surface missing !include targets as errors
        errors = []
        for ws in _WORKSPACES:
            ws_cfg = (template.get("workspaces") or {}).get(ws, {})
            for side in _SIDES:
                val = ws_cfg.get(f"{side}_sidebar")
                if isinstance(val, str) and val.startswith("__missing__:"):
                    errors.append(
                        f"!include target not found: {val.replace('__missing__: ', '')} "
                        f"(referenced in {template_path} workspaces.{ws}.{side}_sidebar)"
                    )

        if errors:
            return errors

        return self.validate(template, template_path)
