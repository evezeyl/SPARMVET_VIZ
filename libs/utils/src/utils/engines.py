"""The engines a recipe may name, stated once (ADR-106 V8).

A recipe declares `data_engine` and `plot_engine`. The app builds one of each today: Polars for the data steps and
plotnine for the plots. The checker's allowed list (code T06), the recipe writers and the visualisation library all read
the names from here, so a second engine is added in one place and a library that does not implement the engine a recipe
asks for refuses it with a message instead of drawing with another engine.

Consumed by: `utils.recipe_check` (through `spec()["engines"]`), `utils.recipe_factory`, `utils.recipe_migration`,
`viz_factory.viz_factory` (the refusal), `test_lab` (the recipes it writes).
If deleted: no recipe can name an engine and the checker refuses every recipe.

# @deps
# provides: constant:DATA_ENGINE, constant:PLOT_ENGINE, constant:ENGINES, function:engine_problem
# consumed_by: libs/utils/src/utils/recipe_check.py, libs/utils/src/utils/recipe_migration.py, libs/viz_factory/src/viz_factory/viz_factory.py,
#              libs/test_lab/src/test_lab/bootstrapper.py, libs/test_lab/src/test_lab/scaffolder.py, libs/utils/tests/test_engines.py
# doc: .claude/knowledge/architecture_decisions.md (ADR-106 V8, ADR-100)
# @end_deps
"""
from typing import Any, Optional, Tuple

DATA_ENGINE = "python-polars"
PLOT_ENGINE = "python-plotnine"

# key of a recipe -> the engines built for it
ENGINES = {"data_engine": (DATA_ENGINE,), "plot_engine": (PLOT_ENGINE,)}


def engine_problem(key: str, value: Any) -> Optional[Tuple[str, str]]:
    """None when `value` is an engine built for `key`; else (what is wrong, how to fix it), in plain words."""
    allowed = ENGINES[key]
    if value in allowed:
        return None
    return (f"the recipe key {key} is {value!r}, which this app does not build",
            f"write {key}: {allowed[0]}" + (f" (one of {', '.join(allowed)})" if len(allowed) > 1 else ""))
