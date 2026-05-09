# @deps
# provides: PANEL_REGISTRY (dict), is_panel_active (function)
# consumes: app/src/bootloader.py (via callers)
# consumed_by: app/handlers/home_theater.py
# doc: .claude/rules/ui_implementation_contract.md §11, .claude/rules/rules_ui_dashboard.md §2
# @end_deps
"""
Sidebar Panel Registry (ADR-073).

Maps panel type identifiers to gate flags and human-readable labels.
Headless-safe — no Shiny imports at module level.

Each entry in PANEL_REGISTRY:
  gate_flag : str | None
      Feature flag name to check via bootloader.is_enabled().
      None means the panel is always visible.
  label : str
      Human-readable panel title (used by SidebarValidator diagnostics).
"""

# None gate_flag = always visible; string = bootloader.is_enabled(flag) must be True
PANEL_REGISTRY: dict[str, dict] = {
    "project_info": {
        "gate_flag": None,
        "label": "Project Info",
    },
    "deployment_info": {
        "gate_flag": None,
        "label": "Deployment Info",
    },
    "manifest_choice": {
        "gate_flag": "manifest_selector_visible",
        "label": "Manifest Choice",
    },
    "filters": {
        "gate_flag": "interactivity_enabled",
        "label": "Filters",
    },
    "data_import": {
        "gate_flag": "metadata_ingestion_enabled",
        "label": "Data Import",
    },
    "export": {
        "gate_flag": "export_enabled",
        "label": "Export",
    },
    "session_management": {
        "gate_flag": "session_management_enabled",
        "label": "Session Management",
    },
    "audit_stack": {
        "gate_flag": "t3_sandbox_enabled",
        "label": "Pipeline Audit",
    },
    "blueprint_nav": {
        "gate_flag": "blueprint_enabled",
        "label": "Blueprint Navigator",
    },
    "blueprint_logic": {
        "gate_flag": "blueprint_enabled",
        "label": "Blueprint Logic",
    },
    "gallery_search": {
        "gate_flag": "gallery_enabled",
        "label": "Gallery Search",
    },
    "notification_log": {
        "gate_flag": None,
        "label": "Notification Log",
    },
}


def is_panel_active(panel_type: str, bootloader) -> bool:
    """Return True if the panel should be rendered for the current persona.

    Checks the gate_flag from PANEL_REGISTRY against bootloader.is_enabled().
    Unknown panel types log a warning and return False.
    """
    entry = PANEL_REGISTRY.get(panel_type)
    if entry is None:
        print(f"[SidebarRegistry] WARNING: Unknown panel type '{panel_type}' — skipping.")
        return False
    gate = entry["gate_flag"]
    if gate is None:
        return True
    return bootloader.is_enabled(gate)
