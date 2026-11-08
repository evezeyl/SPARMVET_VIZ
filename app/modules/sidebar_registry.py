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
    "data_analysis_recipe_info": {
        "gate_flag": None,
        "label": "Info",
    },
    "test_lab_info": {
        "gate_flag": None,
        "label": "Info",
    },
    "deployment_info": {
        "gate_flag": None,
        "label": "Deployment Info",
    },
    "data_analysis_recipe_choice": {
        "gate_flag": "data_analysis_recipe_selector_visible",
        "label": "Data analysis recipe Choice",
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
    "blueprint_agent_chat": {
        "gate_flag": "blueprint_agent_enabled",
        "label": "Blueprint Agent",
    },
    "gallery_main": {
        "gate_flag": "gallery_enabled",
        "label": "Gallery Explorer",
    },
    "blueprint_main": {
        "gate_flag": "blueprint_enabled",
        "label": "Blueprint Recipe Editor",
    },
    "blueprint_surgeon": {
        "gate_flag": "blueprint_enabled",
        "label": "Blueprint Surgeon",
    },
    "blueprint_action_help": {
        "gate_flag": "blueprint_enabled",
        "label": "Action Help",
    },
    "blueprint_plot_defaults": {
        "gate_flag": "blueprint_enabled",
        "label": "Plot Defaults",
    },
    "blueprint_branch_node": {
        "gate_flag": "data_analysis_recipe_edit_enabled",
        "label": "Branch Node",
    },
    "gallery_right_info": {
        "gate_flag": "gallery_enabled",
        "label": "Gallery Explorer",
    },
    "test_lab_right_info": {
        "gate_flag": "test_lab_enabled",
        "label": "Test Lab Tools (right)",
    },
    # "test_lab" below is not referenced by any shipped config/ui/sidebars/*.yaml (checked
    # 2026-11-08, issue #42 cleanup pass) -- pre-existing, unrelated to #42's panel set,
    # left as-is rather than pulled into this issue's scope.
    "test_lab": {
        "gate_flag": "test_lab_enabled",
        "label": "Test Lab Tools",
    },
    "notification_log": {
        "gate_flag": None,
        "label": "Notification Log",
    },
    "processing_issues": {
        "gate_flag": None,
        "label": "Processing Issues",
    },
}


def is_panel_active(panel_type: str, bootloader) -> bool:
    """Return True if the panel should be rendered for the current app features.

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
