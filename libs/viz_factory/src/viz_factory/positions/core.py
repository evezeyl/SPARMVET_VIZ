from typing import Dict, Any

# @deps
# provides: component:position_identity, component:position_stack, component:position_fill, component:position_dodge, component:position_dodge2, component:position_jitter, component:position_jitterdodge, component:position_nudge
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import (
    position_identity, position_stack, position_fill,
    position_dodge, position_dodge2, position_jitter,
    position_jitterdodge, position_nudge,
    ggplot
)
from viz_factory.registry import register_plot_component


def _apply_position(p: ggplot, pos_obj: Any) -> ggplot:
    """Helper to apply a position object to the last layer added to the plot."""
    if hasattr(p, 'layers') and len(p.layers) > 0:
        p.layers[-1].position = pos_obj
        print(
            f"Applied position to layer: {p.layers[-1].geom.__class__.__name__}")
    else:
        print("Warning: No layers found to apply position to.")
    return p


@register_plot_component("position_identity")
def handle_position_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Default position (no adjustment)."""
    return _apply_position(p, position_identity(**spec))


@register_plot_component("position_stack")
def handle_position_stack(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Stack objects on top of each other."""
    return _apply_position(p, position_stack(**spec))


@register_plot_component("position_fill")
def handle_position_fill(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Stack objects and standardize to 100% height."""
    return _apply_position(p, position_fill(**spec))


@register_plot_component("position_dodge")
def handle_position_dodge(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Place objects side-by-side."""
    return _apply_position(p, position_dodge(**spec))


@register_plot_component("position_dodge2")
def handle_position_dodge2(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Enhanced dodging for varying widths."""
    return _apply_position(p, position_dodge2(**spec))


@register_plot_component("position_jitter")
def handle_position_jitter(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Add random noise to prevent overplotting."""
    return _apply_position(p, position_jitter(**spec))


@register_plot_component("position_jitterdodge")
def handle_position_jitterdodge(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Combine jittering and dodging."""
    return _apply_position(p, position_jitterdodge(**spec))


@register_plot_component("position_nudge")
def handle_position_nudge(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shift points by fixed offset."""
    return _apply_position(p, position_nudge(**spec))
