# @deps
# provides: class:TestLabStudio (render_ui only), function:scaffold_from_uploads
# consumes: shiny.ui, libs/test_lab/src/test_lab/scaffolder.py,
#           libs/id_reconciliation/src/id_reconciliation/recipe_steps.py
# consumed_by: app/handlers/home_theater.py, app/src/server.py, app/handlers/test_lab_handlers.py,
#              app/tests/test_id_cleaning_steps_reach_a_recipe.py
# doc: .claude/rules/rules_test_lab.md §6, .claude/design/spaces/TEST_LAB.md
# @end_deps
"""
TestLabStudio (test_lab_studio.py)

Module-level orchestrator for the TEST_LAB workspace: the static UI shell (`TestLabStudio`) and the one place where
two Test Lab tools meet (`scaffold_from_uploads`: the ID reconciliation hands its cleaning steps to the scaffold).

Two-Category Law (ADR-045 + rules_test_lab.md §6):
  MUST NOT import shiny.reactive or register @render.* functions.
  Reactive wiring belongs in app/handlers/test_lab_handlers.py.
"""

from pathlib import Path
from typing import TYPE_CHECKING, List, Optional

from shiny import ui

if TYPE_CHECKING:
    from id_reconciliation import IdTransformation


def scaffold_from_uploads(
    file_infos: List[dict],
    data_analysis_recipe_id: str,
    join_key: str,
    meta_info: Optional[dict] = None,
    id_transformation: Optional["IdTransformation"] = None,
    id_file_name: Optional[str] = None,
) -> bytes:
    """The scaffold ZIP of uploaded data files, with the ID cleaning steps of a reconciliation when one is given.

    `file_infos` and `meta_info` are uploads as Shiny gives them: `name` is the file name the user chose, `datapath`
    the place of the uploaded copy. `id_transformation` and `id_file_name` come together: the steps of the
    transformation are written, as recipe steps, into `tier1` of the uploaded file of that name. They clean the
    column `id_transformation.ref_column`, under the name the scaffolded recipe gives it.

    Raises ValueError, with nothing written, when the file is not one of the uploads, when two uploads carry its name,
    or when it has no such column: steps for a column the file lacks would break the recipe.
    """
    # Imported here, as the handlers do: this module is loaded for every app features, the Test Lab libraries only
    # when a Test Lab tool runs.
    from id_reconciliation import recipe_steps
    from test_lab.scaffolder import DataAnalysisRecipeScaffolder

    if (id_transformation is None) != (id_file_name is None):
        raise ValueError("The ID transformation and the name of the file that takes its steps must be given together.")
    scaffolder = DataAnalysisRecipeScaffolder(join_key=join_key)
    steps = None
    if id_transformation is not None:
        chosen = [info for info in file_infos if info["name"] == id_file_name]
        names = ", ".join(info["name"] for info in file_infos)
        if not chosen:
            raise ValueError(f"The file {id_file_name} is not one of the uploaded data files ({names}).")
        if len(chosen) > 1:
            raise ValueError(f"Two uploaded data files have the name {id_file_name}: "
                             "the ID cleaning steps cannot tell them apart. Rename one file and upload again.")
        path = chosen[0]["datapath"]
        column = scaffolder.column_slug(id_transformation.ref_column)
        if column not in scaffolder.field_slugs(path):
            raise ValueError(
                f"The file {id_file_name} has no column {id_transformation.ref_column}: the ID cleaning steps were "
                "made for that column. Choose the file that was the reference file of the ID reconciliation.")
        steps = {scaffolder.dataset_id(path): recipe_steps(id_transformation, column)}
    return scaffolder.scaffold(
        [Path(info["datapath"]) for info in file_infos],
        data_analysis_recipe_id,
        steps=steps,
        metadata_path=Path(meta_info["datapath"]) if meta_info else None,
    )


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
                    "Data preparation utilities: ID reconciliation, data analysis recipe scaffolding, "
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
                    "Data analysis recipe Scaffolding",
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
