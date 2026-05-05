from typing import Dict, Any

# @deps
# provides: component:coord_cartesian, component:coord_flip, component:coord_fixed, component:coord_equal, component:coord_trans, component:coord_lims
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import (
    coord_cartesian, coord_flip, coord_fixed,
    coord_trans, coord_equal, ggplot
)
from viz_factory.registry import register_plot_component


@register_plot_component("coord_cartesian")
def handle_coord_cartesian(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Cartesian coordinate system."""
    return p + coord_cartesian(**spec)


@register_plot_component("coord_flip")
def handle_coord_flip(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Flipped Cartesian coordinates (x becomes y)."""
    return p + coord_flip(**spec)


@register_plot_component("coord_fixed")
def handle_coord_fixed(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Cartesian coordinates with fixed aspect ratio."""
    return p + coord_fixed(**spec)


@register_plot_component("coord_equal")
def handle_coord_equal(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for fixed coordinates with 1:1 ratio."""
    return p + coord_equal(**spec)


@register_plot_component("coord_trans")
def handle_coord_trans(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Transformed Cartesian coordinates."""
    return p + coord_trans(**spec)


@register_plot_component("coord_lims")
def handle_coord_lims(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Strict coordinate-level limits.
    Prevents data clipping that occurs with scale_x_continuous(limits=...).
    """
    # Use coord_cartesian for strict limits without clipping
    return p + coord_cartesian(**spec)
