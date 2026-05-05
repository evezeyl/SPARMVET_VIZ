import logging
from typing import Callable, Dict, Any

logger = logging.getLogger(__name__)

# @deps
# provides: decorator:register_plot_component, registry:PLOT_COMPONENTS, function:get_component
# consumed_by: libs/viz_factory/src/viz_factory/geoms/core.py, libs/viz_factory/src/viz_factory/themes/core.py, libs/viz_factory/src/viz_factory/scales/core.py, libs/viz_factory/src/viz_factory/positions/core.py, libs/viz_factory/src/viz_factory/guides/core.py, libs/viz_factory/src/viz_factory/facets/core.py, libs/viz_factory/src/viz_factory/coords/core.py, libs/viz_factory/src/viz_factory/viz_factory.py
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

# The Central Repository for all Registered Plotting Components (geoms, scales, themes, etc.)
# Components MUST accept (plot, spec) and return a modified plot.
PLOT_COMPONENTS: Dict[str, Callable[[Any, Dict[str, Any]], Any]] = {}


def register_plot_component(name: str):
    """
    Standard Plugin Decorator for Plotting Components.
    Any function decorated with `@register_plot_component("name")` 
    will automatically become available to the VizFactory.
    """
    def decorator(func: Callable):
        if name in PLOT_COMPONENTS:
            logger.warning(f"Overwriting plotting component: {name}")
        PLOT_COMPONENTS[name] = func
        return func
    return decorator


def get_component(name: str) -> Callable:
    """Returns the function for a given plotting component, or raises error."""
    if name not in PLOT_COMPONENTS:
        available = ", ".join(PLOT_COMPONENTS.keys())
        raise ValueError(
            f"Plot component '{name}' not found. Available: {available}")
    return PLOT_COMPONENTS[name]
