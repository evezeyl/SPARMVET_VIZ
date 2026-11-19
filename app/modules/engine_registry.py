"""The app's choice of the engine: the one place that joins the libraries of the engines (D-0219, D-0238, D-0247).

A recipe writes `data_engine` and `plot_engine` at its top, and a tier or a plot entry may write its own (D-0219). The code
chooses with the value: where the tiers of a table or a join are run (`DataOrchestrator`) and where a plot is drawn
(`PlotEngines`, used by HOME, the export, Blueprint's preview, the gallery previews and the picture and golden scripts), the
engine named by the block, else by the recipe, selects the entry of its library. An engine this app has no library for is
refused with the words of D-0239 ("no library for this engine in this app", and the engines of this app); a block that has
no engine at all is refused too. No path falls back to the engine that exists because it is the only one (D-0050).

The libraries do not import each other: this module imports the entry file of each (`engine_python_polars.py`,
`engine_python_plotnine.py`) and nothing else of the engines, and builds what the checker needs to know about each name
(`engine_tables`). The names of the engines are in `utils.engines`, one table for everyone.

Consumed by: `app/modules/orchestrator.py`, `app/modules/data_analysis_recipe_validator.py` (the checker's catalogues),
`app/src/server.py`, `app/modules/gallery_examples.py`, `assets/scripts/golden_baseline.py`, `assets/scripts/recipe_pictures.py`.
If deleted: no tier is run and no plot is drawn by the app.

# @deps
# provides: constant:REGISTRY, function:data_entry, function:plot_entry, function:engine_tables, class:PlotEngines (render, record_of: what the export records of a drawn plot)
# consumes: libs/utils/src/utils/engines.py, libs/utils/src/utils/errors.py, libs/transformer/src/transformer/engine_python_polars.py, libs/viz_factory/src/viz_factory/engine_python_plotnine.py, libs/transformer/src/transformer/actions/base.py (ACTION_ENGINES), libs/viz_factory/src/viz_factory/registry.py (COMPONENT_ENGINES)
# consumed_by: app/modules/orchestrator.py, app/handlers/export_handlers.py (PlotEngines.record_of, passed in), app/modules/data_analysis_recipe_validator.py, app/modules/gallery_examples.py, app/src/server.py, assets/scripts/golden_baseline.py, assets/scripts/recipe_pictures.py, app/tests/test_engine_registry.py
# doc: .claude/knowledge/decision_ledger.md (D-0219, D-0238, D-0239, D-0247, D-0050)
# @end_deps
"""
from typing import Any, Dict, Optional

from transformer.engine_python_polars import ENTRY as _POLARS
from viz_factory.engine_python_plotnine import ENTRY as _PLOTNINE
from utils import engines
from utils.engines import DataEngineEntry, PlotEngineEntry
from utils.errors import VisualizationError

# engine value -> the entry of its library. The only table of entries in the app; the names are in `utils.engines.ENGINE_TABLE`
# and a test holds the two equal.
REGISTRY: Dict[str, Any] = {_POLARS.engine: _POLARS, _PLOTNINE.engine: _PLOTNINE}


def data_entry(recipe: Any, body: Any, tier: str, *, where: str) -> DataEngineEntry:
    """The entry of the data engine that runs `tier` of `body` (a table or a join; the plot entry for tier3).

    The engine is the tier's own `data_engine`, else the recipe's. Raises the recipe error, with the words of D-0239, when the
    block names none or names an engine this app has no library for (a plot engine in a data slot is refused the same way).
    `where` names the block in the message, for example "the tier1 of the table 'A'".
    """
    engine = engines.tier_engine(recipe, body, tier)
    entry = REGISTRY.get(engine) if isinstance(engine, str) else None
    if not isinstance(entry, DataEngineEntry):
        raise engines.engine_error("data_engine", engine, where=where)
    return entry


def plot_entry(entry: Any, recipe: Any, plot_id: str) -> PlotEngineEntry:
    """The entry of the plot engine that draws a plot: the plot entry's own `plot_engine`, else the recipe's.

    Raises the plot error (`VisualizationError`), with the words of D-0239, when none is written or the app has no library for it.
    """
    engine = engines.effective_engine("plot_engine", entry, recipe)
    found = REGISTRY.get(engine) if isinstance(engine, str) else None
    if not isinstance(found, PlotEngineEntry):
        raise engines.engine_error("plot_engine", engine, where=f"Plot '{plot_id}'", error=VisualizationError)
    return found


def engine_tables() -> dict:
    """The engine of every registered action and plot component, for the checker (`action_engines`, `component_engines`).

    Read from the registries of the libraries: each registering decorator stores the field `engine` (D-0238), so the checker
    refuses a step under another engine's block by what the registry says, not by the prefix of a name.
    """
    import transformer.actions  # noqa: F401  (importing it registers the actions)
    import viz_factory  # noqa: F401  (importing it registers the plot components)
    from transformer.actions.base import ACTION_ENGINES
    from viz_factory.registry import COMPONENT_ENGINES

    return {"action_engines": dict(ACTION_ENGINES), "component_engines": dict(COMPONENT_ENGINES)}


class PlotEngines:
    """Draws a plot with the plot engine its entry or its recipe names. It stands where a `VizFactory` stood in the app.

    `factory_arguments` are what the app gives each engine's factory when it is built (today the deployment's palettes). A
    factory is built once, on its first plot. `render` has the call of `VizFactory.render`: the engine is read from the plot's
    own entry in `recipe["plots"]`, else from the recipe, and handed to the factory in the recipe it receives.
    """

    def __init__(self, **factory_arguments: Any):
        self._factory_arguments = factory_arguments
        self._factories: Dict[str, Any] = {}

    def factory_of(self, entry: PlotEngineEntry) -> Any:
        if entry.engine not in self._factories:
            self._factories[entry.engine] = entry.factory(**self._factory_arguments)
        return self._factories[entry.engine]

    def render(self, df: Any, recipe: Dict[str, Any], plot_id: str, **render_arguments: Any):
        plots = recipe.get("plots") if isinstance(recipe, dict) else None
        own = plots.get(plot_id) if isinstance(plots, dict) else None
        found = plot_entry(own, recipe, plot_id)
        return self.factory_of(found).render(df, {**recipe, "plot_engine": found.engine}, plot_id, **render_arguments)

    def record_of(self, plot: Any, recipe: Dict[str, Any], plot_id: str) -> Dict[str, Any]:
        """What the export records of a plot this dispatcher drew (D-0248): the engine that drew it (`plot_entry`, the function
        `render` chose with, so the record and the drawing cannot differ), that it was drawn, and the theme as the engine says it
        applied it, read from the plot itself. An engine that does not say which theme it applied is recorded as such."""
        plots = recipe.get("plots") if isinstance(recipe, dict) else None
        found = plot_entry(plots.get(plot_id) if isinstance(plots, dict) else None, recipe, plot_id)
        if found.applied_theme is None:
            theme = {"recorded": False, "reason": f"the engine {found.engine} does not say which theme it applied"}
        else:
            try:
                theme = found.applied_theme(plot) or {"recorded": False, "reason": "the plot does not carry what it was drawn with"}
            except Exception as exc:   # a theme that cannot be read must not turn a drawn plot into a failed one (D-0050: it is told)
                theme = {"recorded": False, "reason": f"the theme could not be read from the plot ({type(exc).__name__}: {str(exc)[:120]})"}
        return {"plot_engine": found.engine, "drawn": True, "theme": theme}

    @property
    def default_random_state(self) -> Any:
        """The seed an engine's random layers use when the recipe writes none.

        PROVISIONAL: HOME and the export read one default seed for every plot. It is the one of the app's plot engine
        (today there is one). When a second plot engine exists the seed belongs to the plot's engine and the readers
        (`seed_in_use`, `export_seed_plan`) need the plot's engine: that is a decision for then.
        """
        return self.factory_of(REGISTRY[engines.PLOT_ENGINE]).default_random_state
