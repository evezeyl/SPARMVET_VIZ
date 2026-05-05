from typing import Dict, Any

# @deps
# provides: component:guides, component:guide_legend, component:guide_colorbar, component:guide_colourbar, component:guide_none, component:guide_nrow, component:guide_ncol, component:guide_title, component:guide_label, component:guide_direction, component:guide_reverse
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import (
    guides, guide_legend, guide_colorbar,
    ggplot
)
from viz_factory.registry import register_plot_component


@register_plot_component("guides")
def handle_guides_group(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Main guides container. Allows setting multiple guides at once.
    Example:
      params:
        color: "none"
        fill: "legend"
    """
    guide_specs = {}
    for mapping, guide_type in spec.items():
        if guide_type == "none" or guide_type is False:
            guide_specs[mapping] = False
        elif guide_type == "legend":
            guide_specs[mapping] = guide_legend()
        elif guide_type == "colorbar":
            guide_specs[mapping] = guide_colorbar()
        else:
            guide_specs[mapping] = guide_type

    return p + guides(**guide_specs)


@register_plot_component("guide_legend")
def handle_guide_legend(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Apply a legend guide to a specific mapping.
    MANDATORY key: 'mapping' (e.g., 'color', 'fill', 'shape')
    """
    mapping = spec.pop("mapping", None)
    if not mapping:
        print("Warning: guide_legend requires a 'mapping' parameter.")
        return p
    return p + guides(**{mapping: guide_legend(**spec)})


@register_plot_component("guide_colorbar")
def handle_guide_colorbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Apply a colorbar guide to a specific mapping (usually color or fill).
    MANDATORY key: 'mapping'
    """
    mapping = spec.pop("mapping", None)
    if not mapping:
        print("Warning: guide_colorbar requires a 'mapping' parameter.")
        return p
    return p + guides(**{mapping: guide_colorbar(**spec)})


@register_plot_component("guide_colourbar")
def handle_guide_colourbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Alias for guide_colorbar."""
    return handle_guide_colorbar(p, spec)


@register_plot_component("guide_none")
def handle_guide_none(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Remove the guide for a specific mapping.
    MANDATORY key: 'mapping'
    """
    mapping = spec.pop("mapping", None)
    if not mapping:
        print("Warning: guide_none requires a 'mapping' parameter.")
        return p
    return p + guides(**{mapping: False})


@register_plot_component("guide_nrow")
def handle_guide_nrow(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Helper to set nrow for a legend.
    MANDATORY key: 'mapping', 'nrow' (or 'value')
    """
    mapping = spec.pop("mapping", None)
    nrow = spec.pop("nrow", spec.pop("value", None))
    if not mapping or nrow is None:
        print("Warning: guide_nrow requires 'mapping' and 'nrow'.")
        return p
    return p + guides(**{mapping: guide_legend(nrow=nrow, **spec)})


@register_plot_component("guide_ncol")
def handle_guide_ncol(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Helper to set ncol for a legend.
    MANDATORY key: 'mapping', 'ncol' (or 'value')
    """
    mapping = spec.pop("mapping", None)
    ncol = spec.pop("ncol", spec.pop("value", None))
    if not mapping or ncol is None:
        print("Warning: guide_ncol requires 'mapping' and 'ncol'.")
        return p
    return p + guides(**{mapping: guide_legend(ncol=ncol, **spec)})


@register_plot_component("guide_title")
def handle_guide_title(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set title for a guide."""
    mapping = spec.pop("mapping", None)
    title = spec.pop("title", spec.pop("value", None))
    if not mapping:
        print("Warning: guide_title requires 'mapping'.")
        return p
    # Try to detect guide type or default to legend if unknown mapping
    return p + guides(**{mapping: guide_legend(title=title, **spec)})


@register_plot_component("guide_label")
def handle_guide_label(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to toggle/format labels for a guide."""
    mapping = spec.pop("mapping", None)
    labels = spec.pop("labels", spec.pop("value", True))
    if not mapping:
        print("Warning: guide_label requires 'mapping'.")
        return p
    return p + guides(**{mapping: guide_legend(labels=labels, **spec)})


@register_plot_component("guide_direction")
def handle_guide_direction(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set direction for a guide."""
    mapping = spec.pop("mapping", None)
    direction = spec.pop("direction", spec.pop("value", "horizontal"))
    if not mapping:
        print("Warning: guide_direction requires 'mapping'.")
        return p
    return p + guides(**{mapping: guide_legend(direction=direction, **spec)})


@register_plot_component("guide_reverse")
def handle_guide_reverse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to reverse a guide."""
    mapping = spec.pop("mapping", None)
    reverse = spec.pop("reverse", spec.pop("value", True))
    if not mapping:
        print("Warning: guide_reverse requires 'mapping'.")
        return p
    return p + guides(**{mapping: guide_legend(reverse=reverse, **spec)})
