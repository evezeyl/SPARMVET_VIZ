"""The places of the code that may use an engine library, and the engine each one belongs to (stage 0 of the engine boundary, D-0455, D-0458).

A recipe names an engine (`python-polars` for the tables, `python-plotnine` for the plots, `utils.engines.ENGINE_TABLE`). Code that
imports Polars, plotnine, matplotlib, pandas or mizani, or that spells an engine's own names as data, is engine-specific. This
file is the one list of those places, so that the engine-specific parts are recorded as such and a new engine knows what must work
differently. Nothing here changes what the app does: it is a record, and a test (`libs/utils/tests/test_engine_boundary.py`) fails when
the code and the record disagree.

How a file says its engine (PROVISIONAL form, an agent's choice, not Eve's): one comment line at the top of the file,
`# engine: python-polars (what in this file belongs to the engine)`; two engines are joined with `+`. The test reads the line and
compares it with this list. The line stays outside the `@deps` block, so that the dependency tool reads the files as before.

Kinds (PROVISIONAL, an agent's classification of each file; the owner has not reviewed them):
- engine-library: part of the library of the engine itself (`libs/transformer/src` for python-polars, `libs/viz_factory/src` for
  python-plotnine) and imports the engine's library. Its own place; it stays.
- table-library: the app's own use of Polars as its table library (reading and writing files, holding a table, a script), or pandas for a
  table of the interface. Allowed for now; whether Polars keeps this role is an open choice of the owner.
- mixed: engine knowledge inside code that should be neutral or that belongs to the app (types, expressions, error classes, drawing).
  Allowed for now, to be moved.
- names-as-data: no import of the engine library; the file holds the engine's own names or grammar as data or as text it writes (action
  names, join kinds, formula text, plotnine layer names). These entries are found by hand and are NOT found by the test: a file of this
  kind that is missing here is not reported. The test only checks that an entry still exists, still mentions its engine and still has
  no import.

For every place that is not the engine's own, the stage that moves it is "not decided" (the owner decides it after the demo).

New code: do not import an engine library in a new file without adding the file here with its engine and kind, and do not spell the
names of an engine in a new place when a list of them exists (`utils.action_names`, `READINGS` and `FOLLOWED_JOINS` of `utils.step_effects`).

Names only: this module imports nothing.

# @deps
# provides: constant:PLACES, constant:LIBRARY_ENGINE, constant:KINDS, class:EnginePlace
# consumed_by: libs/utils/tests/test_engine_boundary.py
# doc: .claude/knowledge/decision_ledger.md (D-0455, D-0458)
# @end_deps
"""
from dataclasses import dataclass
from typing import Dict, Tuple

POLARS = "python-polars"
PLOTNINE = "python-plotnine"

# the import name of a library -> the engine it belongs to. pandas and matplotlib stand under the plot engine because that engine hands
# plotnine a pandas table and draws on matplotlib figures (`viz_factory.py`, `utils.engines.ENGINE_TABLE` packages); mizani is plotnine's own.
# PROVISIONAL: a use of pandas that has nothing to do with a plot (the help grid of the interface) is listed under it too, and said so.
LIBRARY_ENGINE: Dict[str, str] = {
    "polars": POLARS,
    "plotnine": PLOTNINE,
    "matplotlib": PLOTNINE,
    "pandas": PLOTNINE,
    "mizani": PLOTNINE,
}

ENGINE_LIBRARY = "engine-library"
TABLE_LIBRARY = "table-library"
MIXED = "mixed"
NAMES_AS_DATA = "names-as-data"
KINDS = (ENGINE_LIBRARY, TABLE_LIBRARY, MIXED, NAMES_AS_DATA)

ALLOWED_FOR_NOW = "allowed for now"
OWN_PLACE = "the engine's own place"
NOT_DECIDED = "not decided"


@dataclass(frozen=True)
class EnginePlace:
    """One file that may use an engine: its path from the repository root, its engine or engines, its kind and one phrase of why."""
    path: str
    engines: Tuple[str, ...]
    kind: str
    why: str          # the phrase the mark in the file repeats; no brackets
    standing: str     # OWN_PLACE for the engine's library, else ALLOWED_FOR_NOW
    stage: str        # the stage that moves it: NOT_DECIDED for everything that is not the engine's own place, "-" for the engine's own

    @property
    def mark(self) -> str:
        """The line the file carries at its top."""
        return f"# engine: {'+'.join(self.engines)} ({self.why})"


def _place(path: str, engines: str, kind: str, why: str) -> EnginePlace:
    own = kind == ENGINE_LIBRARY
    return EnginePlace(path, tuple(engines.split("+")), kind, why, OWN_PLACE if own else ALLOWED_FOR_NOW, "-" if own else NOT_DECIDED)


_T = "libs/transformer/src/transformer/"
_V = "libs/viz_factory/src/viz_factory/"
_U = "libs/utils/src/utils/"
_P = POLARS
_G = PLOTNINE
_PG = f"{POLARS}+{PLOTNINE}"
_GP = f"{PLOTNINE}+{POLARS}"

PLACES: Tuple[EnginePlace, ...] = tuple(_place(*row) for row in (
    # -- the engine libraries: imports of the engine's own library ------------------------------------------------------------------
    (_T + "actions/base.py", _P, ENGINE_LIBRARY, "the action registry and its engine field; every action is a function on a Polars LazyFrame"),
    (_T + "actions/composite.py", _P, ENGINE_LIBRARY, "the step_ actions: several Polars calls kept as one step"),
    (_T + "actions/modified.py", _P, ENGINE_LIBRARY, "the modif_ actions: Polars calls with a documented change"),
    (_T + "actions/polars_aggregations.py", _P, ENGINE_LIBRARY, "the polars_ table aggregations, each one a Polars call"),
    (_T + "actions/polars_calls.py", _P, ENGINE_LIBRARY, "the polars_ actions that wrap one Polars call each"),
    (_T + "actions/polars_rows.py", _P, ENGINE_LIBRARY, "the polars_ actions on rows, each one a Polars call"),
    (_T + "actions/polars_time_joins.py", _P, ENGINE_LIBRARY, "the polars_ rank, time and special join actions, each one a Polars call"),
    (_T + "anchor.py", _P, ENGINE_LIBRARY, "the stored tier tables, written and read as Parquet through Polars"),
    (_T + "data_assembler.py", _P, ENGINE_LIBRARY, "runs the join steps of a collection on Polars LazyFrames"),
    (_T + "data_wrangler.py", _P, ENGINE_LIBRARY, "runs the steps of a tier on a Polars LazyFrame"),
    (_T + "join_diagnosis.py", _P, ENGINE_LIBRARY, "plain words for a join that Polars refuses"),
    (_T + "registry.py", _P, ENGINE_LIBRARY, "the bridge to the action registry; it imports Polars but does not use it"),
    (_V + "checked_plot.py", _G, ENGINE_LIBRARY, "the checked call that draws a plotnine plot and explains its failure; uses matplotlib figures"),
    (_V + "coords/core.py", _G, ENGINE_LIBRARY, "the plot components of the coord family, wrapping plotnine"),
    (_V + "facets/core.py", _G, ENGINE_LIBRARY, "the plot components of the facet family, wrapping plotnine"),
    (_V + "font_check.py", _G, ENGINE_LIBRARY, "asks matplotlib which font families are installed"),
    (_V + "geoms/core.py", _G, ENGINE_LIBRARY, "the plot components of the geom family, wrapping plotnine"),
    (_V + "guides/core.py", _G, ENGINE_LIBRARY, "the plot components of the guide family, wrapping plotnine"),
    (_V + "parameters.py", _G, ENGINE_LIBRARY, "reads the parameter list of an exact plot component from plotnine"),
    (_V + "positions/core.py", _G, ENGINE_LIBRARY, "the plot components of the position family, wrapping plotnine"),
    (_V + "scales/core.py", _G, ENGINE_LIBRARY, "the plot components of the scale family, wrapping plotnine; uses a matplotlib tick locator"),
    (_V + "themes/core.py", _G, ENGINE_LIBRARY, "the theme components and the title and label setters, wrapping plotnine"),
    (_V + "viz_factory.py", _GP, ENGINE_LIBRARY, "draws with plotnine; takes a Polars table and hands plotnine a pandas copy"),
    # -- mixed: engine knowledge inside code that should be neutral or that belongs to the app --------------------------------------
    (_U + "filter_values.py", _P, MIXED, "builds Polars conditions for filters; the HOME table, the plot and the recipe action share it"),
    (_U + "formula_check.py", _P, MIXED, "checks recipe formulas against the Polars expression grammar"),
    (_U + "missing_values.py", _P, MIXED, "the Polars rules for missing and not-a-number values in filters"),
    (_U + "polars_types.py", _P, MIXED, "the Polars dtype names a text file can hold, read from the installed Polars"),
    (_U + "recipe_check.py", _P, MIXED, "the recipe checker; holds a Polars type check and a Polars row-order rule"),
    (_V + "plot_config_resolver.py", _G, MIXED, "the plot settings cascade on plain dicts; it imports no plotnine and imports pandas only inside a function, for column type checks"),
    ("app/modules/orchestrator.py", _P, MIXED, "runs the tiers through the engine entry, types tables as LazyFrame and catches Polars errors"),
    ("app/modules/t3_audit_engine.py", _P, MIXED, "applies audit filters and drops with Polars casts and expressions"),
    ("app/modules/wrangle_studio.py", _P, MIXED, "reads stored tables with Polars and names Polars dtypes"),
    ("app/modules/build_failure.py", _P, MIXED, "catches Polars errors of a computed table and cuts the query plan from their text"),
    ("app/modules/data_analysis_recipe_validator.py", _P, MIXED, "runs a plan on one row and catches Polars errors"),
    ("app/modules/opening_build.py", _GP, MIXED, "builds the tables as LazyFrames and closes the matplotlib figure of each drawing proof"),
    ("app/modules/gallery_examples.py", _GP, MIXED, "builds a gallery example as a LazyFrame and sets the matplotlib backend to draw it"),
    ("app/handlers/home_theater.py", _GP, MIXED, "the HOME handlers; draws placeholder figures with matplotlib itself and holds Polars tables"),
    ("app/handlers/blueprint_handlers.py", _P, MIXED, "the BLUEPRINT handlers; catches Polars errors and scans stored tables"),
    ("assets/scripts/figshare_plot_integration.py", _GP, MIXED, "a script that draws with plotnine and pandas directly, outside the engine registry"),
    # -- table-library: Polars as the app's own table library ------------------------------------------------------------------------
    ("libs/ingestion/src/ingestion/declared.py", _P, TABLE_LIBRARY, "reads the declared types and missing-value texts into Polars"),
    ("libs/ingestion/src/ingestion/excel_handler.py", _P, TABLE_LIBRARY, "reads Excel sheets into Polars tables"),
    ("libs/ingestion/src/ingestion/ingestor.py", _P, TABLE_LIBRARY, "reads data files into Polars tables with the declared types"),
    ("libs/test_lab/src/test_lab/anonymiser.py", _P, TABLE_LIBRARY, "anonymises the IDs of Polars tables"),
    ("libs/test_lab/src/test_lab/aqua_synthesizer.py", _P, TABLE_LIBRARY, "makes synthetic Polars tables"),
    ("libs/test_lab/src/test_lab/bootstrapper.py", _P, TABLE_LIBRARY, "reads data files with Polars to write a first recipe"),
    ("libs/test_lab/src/test_lab/extractor.py", _P, TABLE_LIBRARY, "extracts tables from workbooks into Polars"),
    ("libs/test_lab/src/test_lab/reformatter.py", _P, TABLE_LIBRARY, "converts file formats through Polars"),
    ("libs/test_lab/src/test_lab/scaffolder.py", _P, TABLE_LIBRARY, "infers the input fields of a recipe from Polars tables"),
    ("libs/id_reconciliation/src/id_reconciliation/core.py", _P, TABLE_LIBRARY, "matches the IDs of two Polars LazyFrames"),
    ("libs/id_reconciliation/src/id_reconciliation/matcher.py", _P, TABLE_LIBRARY, "matches ID lists with plain Python; it imports Polars but does not use it"),
    ("libs/viz_gallery/src/viz_gallery/example_recipe.py", _P, TABLE_LIBRARY, "builds a gallery example recipe and reads its data with Polars"),
    ("libs/viz_gallery/src/viz_gallery/gallery_manager.py", _P, TABLE_LIBRARY, "checks the gallery examples and reads their data with Polars"),
    (_U + "hashing.py", _P, TABLE_LIBRARY, "reads Parquet metadata; it imports Polars but does not use it"),
    (_U + "table_compare.py", _P, TABLE_LIBRARY, "compares two collected Polars tables: counted whole-row diff, key check and paired view"),
    ("app/src/server.py", _P, TABLE_LIBRARY, "reads the stored tier 1 table with a Polars Parquet scan"),
    ("app/handlers/gallery_handlers.py", _P, TABLE_LIBRARY, "shows a Polars table with the error when an example cannot load"),
    ("app/handlers/test_lab_handlers.py", _P, TABLE_LIBRARY, "reads uploaded files with Polars for the TEST_LAB tools"),
    ("app/modules/audit_run.py", _P, TABLE_LIBRARY, "hands out the table of a plot of the audit copy; Polars appears only in a type annotation"),
    ("app/modules/help_registry.py", _G, TABLE_LIBRARY, "builds a pandas table for the help grid of the interface; no plot is drawn and plotnine is not used here, so pandas has no plot engine to belong to in this file; not decided"),
    ("assets/scripts/SF_create_data_analysis_recipe.py", _P, TABLE_LIBRARY, "a script that reads one data file with Polars to write a recipe"),
    ("assets/scripts/create_data_analysis_recipe.py", _P, TABLE_LIBRARY, "a script that reads data files with Polars to write a recipe"),
    ("assets/scripts/create_import_test_files.py", _P, TABLE_LIBRARY, "a script that writes the Data Import test files with Polars"),
    ("assets/scripts/declare_missing_values.py", _P, TABLE_LIBRARY, "a script that reads the data with Polars to declare the missing-value texts"),
    ("assets/scripts/figshare_triple_integration.py", _P, TABLE_LIBRARY, "a script that reads and joins downloaded tables with Polars"),
    ("assets/scripts/golden_baseline.py", _GP, TABLE_LIBRARY, "builds the tables and pictures of every shipped recipe for the baseline; sets the matplotlib backend"),
    ("assets/scripts/migrate_recipe_format.py", _P, TABLE_LIBRARY, "runs Polars on purpose to show that the migrated recipe gives the same table"),
    ("assets/scripts/recipe_pictures.py", _GP, TABLE_LIBRARY, "draws the plots of the recipes through the app path and stores the pictures; sets the matplotlib backend; it imports Polars but does not use it"),
    # -- names-as-data: no import; the file holds the engine's names or grammar as data or as text it writes -----------------------
    (_T + "engine_python_polars.py", _P, NAMES_AS_DATA, "the entry file of the engine python-polars; it names the engine and imports no library"),
    (_T + "actions/min_items.py", _P, NAMES_AS_DATA, "the list of the polars_ actions that need a minimum number of items"),
    (_V + "engine_python_plotnine.py", _G, NAMES_AS_DATA, "the entry file of the engine python-plotnine; it names the engine and imports no library"),
    (_V + "registry.py", _G, NAMES_AS_DATA, "the registry of plot components and their plotnine field, with names of plotnine objects"),
    (_U + "action_names.py", _P, NAMES_AS_DATA, "the names of the Polars actions that code outside the registry spells"),
    (_U + "step_effects.py", _P, NAMES_AS_DATA, "what each Polars action writes or keeps, by action name and join kind"),
    (_U + "join_keys.py", _P, NAMES_AS_DATA, "the join kinds and the row actions of Polars that keep or lose a key"),
    (_U + "recipe_graph.py", _P, NAMES_AS_DATA, "reads the Polars select and drop actions to know the columns of a table"),
    (_U + "remove_from_all.py", _P, NAMES_AS_DATA, "writes the Polars filter action that removes values from a table"),
    (_U + "audit_copy.py", _P, NAMES_AS_DATA, "refuses a drop of a join key; it reads the name of the Polars drop action through utils.action_names and spells it only in text"),
    (_U + "step_migration.py", _P, NAMES_AS_DATA, "the table of old action names and the Polars action that replaces each, held as text; it imports no engine library"),
    (_U + "random_layers.py", _G, NAMES_AS_DATA, "the plotnine geoms, positions and stats that draw random numbers"),
    (_U + "plot_text_check.py", _G, NAMES_AS_DATA, "reads the texts that plotnine evaluates: facet formulas and stat functions"),
    ("libs/id_reconciliation/src/id_reconciliation/recipe_steps.py", _P, NAMES_AS_DATA, "writes Polars action names and Polars expression text into recipes"),
    ("libs/blueprint_arch/src/blueprint_arch/t3_translator.py", _P, NAMES_AS_DATA, "writes the Polars filter and drop actions of an audit step"),
    ("libs/viz_gallery/src/viz_gallery/picture_key.py", _G, NAMES_AS_DATA, "puts the installed plotnine version into the key of a gallery picture"),
    ("app/modules/plan_composer.py", _P, NAMES_AS_DATA, "reads the column plan from a Polars LazyFrame with its schema call"),
    ("assets/scripts/viz_rename_table.py", _G, NAMES_AS_DATA, "the table of old plot component names and the plotnine names that replace them"),
    ("assets/scripts/debug_bootstrap_viz_yamls.py", _G, NAMES_AS_DATA, "writes plotnine layer names, such as geoms, scales, coords, guides and theme elements, into the test recipes it makes"),
    ("assets/scripts/migrate_plot_specs.py", _G, NAMES_AS_DATA, "maps the old plot shorthand to plotnine geom layer names and writes them into recipes"),
    ("app/modules/plot_defaults_form.py", _G, NAMES_AS_DATA, "the plotnine theme names that the plot defaults form offers, and the plotnine default when none is chosen"),
    ("libs/utils/src/utils/recipe_factory.py", _G, NAMES_AS_DATA, "writes a plot entry whose default layer is the plotnine geom_bar"),
    ("scripts/audit_parity_coverage.py", _PG, NAMES_AS_DATA, "compares the Polars and plotnine public names with the registered ones"),
    ("scripts/audit_package_deps.py", _PG, NAMES_AS_DATA, "names Polars and plotnine as the packages that carry a parity rule"),
))
