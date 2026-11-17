import functools
import logging
from typing import Callable, Dict, Any, Optional

from utils.plot_text_check import FacetTextError, facet_wrap_spec, layer_text_problems

from viz_factory.parameters import ComponentParameterError, exact_parameters

logger = logging.getLogger(__name__)

# @deps
# provides: decorator:register_plot_component, function:refuse_unsafe_texts, registry:PLOT_COMPONENTS, registry:COMPONENT_SCHEMAS, function:get_component
# consumes: libs/viz_factory/src/viz_factory/parameters.py (exact_parameters), libs/utils/src/utils/plot_text_check.py (layer_text_problems, facet_wrap_spec, FacetTextError), libs/viz_factory/src/viz_factory/errors.py (CannotAct)
# consumed_by: libs/viz_factory/tests/test_component_plotnine_field.py, libs/viz_factory/src/viz_factory/geoms/core.py, libs/viz_factory/src/viz_factory/themes/core.py, libs/viz_factory/src/viz_factory/scales/core.py, libs/viz_factory/src/viz_factory/positions/core.py, libs/viz_factory/src/viz_factory/guides/core.py, libs/viz_factory/src/viz_factory/facets/core.py, libs/viz_factory/src/viz_factory/coords/core.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/blueprint_arch/src/blueprint_arch/schema_registry.py
# doc: .claude/rules/rules_viz_factory.md, .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps

# The Central Repository for all Registered Plotting Components (geoms, scales, themes, etc.)
# Components MUST accept (plot, spec) and return a modified plot.
PLOT_COMPONENTS: Dict[str, Callable[[Any, Dict[str, Any]], Any]] = {}

# Parallel registry: component_name → ui_schema dict (ADR-075 BLUEPRINT IDE form catalog)
# Only populated when @register_plot_component(..., ui_schema={...}) is provided.
COMPONENT_SCHEMAS: Dict[str, Dict[str, Any]] = {}


def refuse_unsafe_texts(name: str, p: Any, spec: Any) -> None:
    """Refuse a layer whose text plotnine would evaluate as Python (PLOT-TEXT-RUNS-CODE-1, check PS06).

    Runs before the component is called, for every component handed out by `get_component` (the one way the factory
    reaches a component), so the same rule covers a plot drawn by the factory and a component fetched by name. The columns of the plot's data are given when the plot has them: a facet
    variable must then be a column.
    """
    from viz_factory.errors import CannotAct

    data = getattr(p, "data", None)
    columns = list(data.columns) if hasattr(data, "columns") else None
    problems = layer_text_problems(name, spec, columns)
    if problems:
        raise CannotAct("; ".join(what for _param, what, _suggestion in problems),
                        " ".join(s if s[-1:] in ".!?" else s + "." for s in dict.fromkeys(suggestion for _param, _what, suggestion in problems)))


def register_plot_component(name: str, ui_schema: Optional[Dict[str, Any]] = None):
    """
    Standard Plugin Decorator for Plotting Components.
    Any function decorated with `@register_plot_component("name")`
    will automatically become available to the VizFactory.

    Optional `ui_schema` kwarg populates COMPONENT_SCHEMAS for BLUEPRINT IDE form generation
    (ADR-075). Schema format: {label, category, context, tags, plotnine, params: {param: {widget, ...}}}.

    `plotnine` (ADR-106 V1) says what the component is to plotnine, like the field `polars` of an action:
    `exact` (only passes its parameters to the plotnine object of the same name), `modified` (adds logic or wraps another
    object; its description says what it changes), `own` (no plotnine object of that name). It is declared in every
    schema and re-derived from the code by `tests/test_component_plotnine_field.py`.

    The parameter list of an `exact` component is read from plotnine here, at registration (ADR-106 V3): its schema
    carries a small `overlay` (label, widget, options per parameter name) and optionally `not_exposed` (name: reason),
    and `params` is filled in from plotnine. A `modified` or `own` component writes its own `params`. A schema that
    mixes the two, or a list that cannot be read, is an error that names the component.
    """
    def decorator(func: Callable):
        if ui_schema is not None:
            _read_exact_parameters(name, ui_schema)  # a refused schema leaves both registries as they were
        if name in PLOT_COMPONENTS:
            logger.warning(f"Overwriting plotting component: {name}")
        PLOT_COMPONENTS[name] = func
        _CHECKED.pop(name, None)
        if ui_schema is not None:
            COMPONENT_SCHEMAS[name] = ui_schema
        return func
    return decorator


def _read_exact_parameters(name: str, schema: Dict[str, Any]) -> None:
    """Fill `params` and `not_exposed` of an `exact` schema from plotnine; refuse a schema that mixes the two kinds."""
    if schema.get("plotnine") != "exact":
        if "overlay" in schema or "not_exposed" in schema:
            raise ComponentParameterError(f"{name}: `overlay` and `not_exposed` belong to an `exact` component; a `{schema.get('plotnine')}` one writes its own `params`")
        return
    if "params" in schema:
        raise ComponentParameterError(f"{name}: an `exact` component does not write `params`; they are read from plotnine (write an `overlay`)")
    schema["params"], schema["not_exposed"] = exact_parameters(name, schema)


def _exact_facets(name: str, p: Any, spec: Any) -> Any:
    """`facet_wrap` gets its variables as a list of exact column names (`facet_grid`, `facet_rows`, `facet_cols` do the same in their own handlers)."""
    if name != "facet_wrap" or not isinstance(spec, dict):
        return spec
    from viz_factory.errors import CannotAct

    data = getattr(p, "data", None)
    try:
        return facet_wrap_spec(spec, list(data.columns) if hasattr(data, "columns") else None)
    except FacetTextError as exc:
        raise CannotAct(exc.what, exc.suggestion) from exc


# `get_component` hands out each component inside the text check; the registered function itself stays as written
# (a test reads its code to prove it is `exact`, and the check must not change what it is).
_CHECKED: Dict[str, Callable] = {}


def get_component(name: str) -> Callable:
    """Returns the function for a given plotting component, inside the text check (PS06), or raises error."""
    if name not in PLOT_COMPONENTS:
        available = ", ".join(PLOT_COMPONENTS.keys())
        raise ValueError(
            f"Plot component '{name}' not found. Available: {available}")
    if name not in _CHECKED:
        func = PLOT_COMPONENTS[name]

        @functools.wraps(func)
        def checked(p, spec):
            refuse_unsafe_texts(name, p, spec)
            return func(p, _exact_facets(name, p, spec))

        _CHECKED[name] = checked
    return _CHECKED[name]
