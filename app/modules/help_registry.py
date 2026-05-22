# Clean package imports via editable install (ADR-016). sys.path hacks are PROHIBITED.
# @deps
# provides: module:help_registry_ui, module:help_registry_server
# consumes: libs/transformer/src/transformer/actions/base.py (AVAILABLE_WRANGLING_ACTIONS)
# consumes: libs/blueprint_arch/src/blueprint_arch/schema_registry.py (get_action_catalog, get_component_catalog)
# consumes: libs/viz_factory/src/viz_factory/registry.py (PLOT_COMPONENT_REGISTRY)
# consumed_by: app/src/server.py
# doc: .claude/rules/rules_data_engine.md
# @end_deps
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from shiny import module, ui, render
import pandas as pd

# Source of truth: live registry populated via @register_action / @register_plot_component decorators


@module.ui
def help_registry_ui():
    return ui.nav_panel(
        "Help & Configuration Registry",
        ui.h2("YAML Action Registry Cookbook"),
        ui.markdown(
            "This table is **automatically generated** directly from the Python backend logic. "
            "It represents the exact list of `action` commands you can currently use in your Data Contract `data_wrangling` rules."
        ),
        ui.card(
            ui.output_data_frame("registry_table")
        ),
        ui.hr(),
        ui.h3("Missing a feature?"),
        ui.markdown(
            "Did you try to use an action that isn't listed above? Don't worry, the pipeline is designed to be easily extensible."
        ),
        ui.a(
            "Request Implementation",
            href="#",  # Replace with actual issue tracker URL when available
            target="_blank",
            class_="btn btn-primary"
        )
    )


@module.server
def help_registry_server(input, output, session):
    @render.data_frame
    def registry_table():
        rows = []

        # --- Transformer actions ---
        try:
            from blueprint_arch.schema_registry import get_action_catalog
            action_catalog = get_action_catalog()
        except Exception:
            action_catalog = {}

        for action_name, func in AVAILABLE_WRANGLING_ACTIONS.items():
            ui_schema = action_catalog.get(action_name, {})

            description = ui_schema.get("description", "")
            if not description:
                # Fall back to function __doc__
                doc = func.__doc__ or "No description provided."
                description = " ".join([line.strip() for line in doc.split("\n") if line.strip()])

            yaml_example = ui_schema.get("yaml_example", "")
            category = ui_schema.get("category", "")

            rows.append({
                "Type": "action",
                "Name": f"`{action_name}`",
                "Category": category,
                "Description": description,
                "YAML Example": yaml_example,
            })

        # --- VizFactory plot components ---
        try:
            from blueprint_arch.schema_registry import get_component_catalog
            component_catalog = get_component_catalog()
        except Exception:
            component_catalog = {}

        if not component_catalog:
            # Fall back to direct registry if schema_registry hasn't populated components yet
            try:
                from viz_factory.registry import PLOT_COMPONENT_REGISTRY
                for comp_name, func in PLOT_COMPONENT_REGISTRY.items():
                    doc = getattr(func, "__doc__", "") or "No description provided."
                    clean_doc = " ".join([line.strip() for line in doc.split("\n") if line.strip()])
                    rows.append({
                        "Type": "component",
                        "Name": f"`{comp_name}`",
                        "Category": "viz",
                        "Description": clean_doc,
                        "YAML Example": "",
                    })
            except Exception:
                pass
        else:
            for comp_name, ui_schema in component_catalog.items():
                description = ui_schema.get("description", "")
                if not description:
                    # Resolve from wraps __doc__ if available
                    wraps = ui_schema.get("wraps", [])
                    if wraps:
                        try:
                            import importlib
                            entry = wraps[0]
                            obj = importlib.import_module(entry["lib"])
                            for attr in entry.get("attr_path", []):
                                obj = getattr(obj, attr)
                            raw = getattr(obj, "__doc__", "") or ""
                            description = " ".join([line.strip() for line in raw.split("\n") if line.strip()])[:200]
                        except Exception:
                            description = "No description provided."
                    else:
                        description = "No description provided."

                yaml_example = ui_schema.get("yaml_example", "")
                category = ui_schema.get("category", "viz")

                rows.append({
                    "Type": "component",
                    "Name": f"`{comp_name}`",
                    "Category": category,
                    "Description": description,
                    "YAML Example": yaml_example,
                })

        df = pd.DataFrame(rows, columns=["Type", "Name", "Category", "Description", "YAML Example"])
        return render.DataGrid(df, filters=True, selection_mode="none")
