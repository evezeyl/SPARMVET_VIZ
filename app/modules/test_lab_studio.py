# @deps
# provides: class:TestLabStudio (render_ui only)
# consumes: shiny.ui
# consumed_by: app/handlers/home_theater.py, app/src/server.py, app/handlers/test_lab_handlers.py
# doc: .claude/rules/rules_test_lab.md §6, .claude/design/spaces/TEST_LAB.md
# @end_deps
"""
TestLabStudio (test_lab_studio.py)

Module-level orchestrator for the TEST_LAB workspace UI shell.
Analogous to WrangleStudio — provides static UI construction only.

Two-Category Law (ADR-045 + rules_test_lab.md §6):
  MUST NOT import shiny.reactive or register @render.* functions.
  Reactive wiring belongs in app/handlers/test_lab_handlers.py.
"""

from shiny import ui


class TestLabStudio:
    """TEST_LAB workspace shell.

    render_ui() returns the central theater area.
    The five output_ui slots (tl_*_ui) are filled by test_lab_handlers.py.
    Left sidebar accordion content is in home_theater.py sidebar_tools_ui.
    """

    def __init__(self):
        pass

    def render_ui(self):
        """Central theater: view title banner + five tool panel slots."""
        return ui.div(
            ui.div(
                ui.span("Test Lab", class_="banner-title"),
                ui.span(
                    "Data preparation utilities: ID reconciliation, manifest scaffolding, "
                    "synthetic data generation, anonymisation, and file reformatting.",
                    class_="banner-subtitle",
                ),
                class_="view-title-banner",
            ),
            ui.accordion(
                ui.accordion_panel(
                    "ID Reconciliation",
                    ui.output_ui("tl_reconcile_ui"),
                    icon=ui.tags.i(class_="bi bi-link-45deg"),
                ),
                ui.accordion_panel(
                    "Manifest Scaffolding",
                    ui.output_ui("tl_scaffold_ui"),
                    icon=ui.tags.i(class_="bi bi-file-earmark-code"),
                ),
                ui.accordion_panel(
                    "Synthetic Data",
                    ui.output_ui("tl_synth_ui"),
                    icon=ui.tags.i(class_="bi bi-table"),
                ),
                ui.accordion_panel(
                    "Anonymisation",
                    ui.output_ui("tl_anon_ui"),
                    icon=ui.tags.i(class_="bi bi-person-lock"),
                ),
                ui.accordion_panel(
                    "File Reformatting",
                    ui.output_ui("tl_reformat_ui"),
                    icon=ui.tags.i(class_="bi bi-arrow-left-right"),
                ),
                id="test_lab_accordion",
                open=False,
            ),
        )
