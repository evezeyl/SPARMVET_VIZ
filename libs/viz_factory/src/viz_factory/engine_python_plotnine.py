"""The entry of the plot engine `python-plotnine`: the one small file that names the engine and exposes `ENTRY` (D-0247).

The app (`app/modules/engine_registry.py`) imports this file and nothing else of the library to choose the engine of a plot:
`ENTRY.factory` is the class that draws a plot from a recipe (`render`). The code of the engine stays where it is
(`viz_factory.py` and the component folders); a second engine is its own library with a file of the same kind. The libraries do
not import each other, so this file imports only this library and the names of `utils.engines`.

Consumed by: `app/modules/engine_registry.py`. If deleted: the app has no plot engine and refuses every plot.

# @deps
# provides: constant:ENTRY, constant:ENGINE
# consumes: libs/utils/src/utils/engines.py (PLOT_ENGINE, PlotEngineEntry), libs/viz_factory/src/viz_factory/viz_factory.py
# consumed_by: app/modules/engine_registry.py, libs/viz_factory/tests/test_component_engine_field.py
# doc: .claude/knowledge/decision_ledger.md (D-0247)
# @end_deps
"""
from utils.engines import PLOT_ENGINE, PlotEngineEntry
from viz_factory.viz_factory import VizFactory

ENGINE = PLOT_ENGINE
ENTRY = PlotEngineEntry(engine=ENGINE, factory=VizFactory)
