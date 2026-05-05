from typing import Dict, Any

# @deps
# provides: component:facet_wrap, component:facet_grid, component:facet_rows, component:facet_cols, component:facet_null, component:facet_scales, component:facet_space, component:facet_labeller, component:facet_margins
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import facet_wrap, facet_grid, ggplot
from viz_factory.registry import register_plot_component


@register_plot_component("facet_wrap")
def handle_facet_wrap(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard individual panel wrapping."""
    # Ensure facets is a list or string
    facets = spec.pop("facets", None)
    return p + facet_wrap(facets=facets, **spec)


@register_plot_component("facet_grid")
def handle_facet_grid(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Standard 2D grid of panels.
    Supports both formula-style 'facets' (rows ~ cols) or explicit 'rows'/'cols'.
    """
    facets = spec.pop("facets", None)
    if facets and "~" in facets:
        items = [i.strip() for i in facets.split("~")]
        if len(items) == 2:
            spec["rows"] = items[0] if items[0] != "." else None
            spec["cols"] = items[1] if items[1] != "." else None

    # Remove 'facets' if still present for some reason (to avoid signature error)
    spec.pop("facets", None)
    return p + facet_grid(**spec)


@register_plot_component("facet_rows")
def handle_facet_rows(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for vertical-only stacking in a grid."""
    row_var = spec.pop("facets", None)
    return p + facet_grid(rows=row_var, **spec)


@register_plot_component("facet_cols")
def handle_facet_cols(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for horizontal-only stacking in a grid."""
    col_var = spec.pop("facets", None)
    return p + facet_grid(cols=col_var, **spec)


@register_plot_component("facet_null")
def handle_facet_null(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Default single-panel display. 
    This is useful for explicitly disabling multi-panel layouts.
    """
    from plotnine import facet_null
    return p + facet_null(**spec)


@register_plot_component("facet_scales")
def handle_facet_scales(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to modify facet scales (free, free_x, free_y)."""
    if hasattr(p, 'facet') and p.facet:
        p.facet.params['scales'] = spec.get(
            'scales', spec.get('value', 'fixed'))
    return p


@register_plot_component("facet_space")
def handle_facet_space(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to modify facet space (fixed, free)."""
    if hasattr(p, 'facet') and p.facet:
        p.facet.params['space'] = spec.get('space', spec.get('value', 'fixed'))
    return p


@register_plot_component("facet_labeller")
def handle_facet_labeller(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set facet labeller on the current facet object."""
    labeller = spec.get('labeller', spec.get('value'))
    if labeller and hasattr(p, 'facet') and p.facet is not None:
        # Use setattr for compatibility across plotnine versions
        try:
            p.facet.labeller = labeller
        except AttributeError:
            params = getattr(p.facet, 'params', None)
            if params is not None:
                params['labeller'] = labeller
    return p


@register_plot_component("facet_margins")
def handle_facet_margins(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set facet margins."""
    if hasattr(p, 'facet') and p.facet:
        p.facet.params['margins'] = spec.get(
            'margins', spec.get('value', True))
    return p
