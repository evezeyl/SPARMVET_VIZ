# Clean package imports via editable install (ADR-016). sys.path hacks are PROHIBITED.
# @deps
# provides: module:help_registry_ui, module:help_registry_server
# consumes: libs/transformer/src/transformer/actions/base.py (AVAILABLE_WRANGLING_ACTIONS)
# consumed_by: app/src/server.py
# doc: .claude/rules/rules_data_engine.md
# @end_deps
from transformer.actions.base import AVAILABLE_WRANGLING_ACTIONS
from shiny import module, ui, render
import pandas as pd

# Source of truth: live registry populated via @register_action decorators


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
        # Build a dataframe by introspecting the Python Registry
        rows = []
        for action_name, func in AVAILABLE_WRANGLING_ACTIONS.items():
            doc = func.__doc__ or "No description provided."
            # Clean up docstring line breaks
            clean_doc = " ".join([line.strip()
                                 for line in doc.split("\n") if line.strip()])

            rows.append({
                "Action Command": f"`{action_name}`",
                "Function Description & Arguments": clean_doc
            })

        df = pd.DataFrame(rows)
        return render.DataGrid(df, filters=True, selection_mode="none")
