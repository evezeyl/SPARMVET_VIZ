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


@register_plot_component("position_identity", ui_schema={
    "label": "Identity (no adjustment)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "identity", "default", "no-adjustment"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_identity"]}],
    "allow_extra_params": False,
    "params": {},
    "description": "Do not adjust point positions (default for most geoms); use explicitly only when overriding a stacked or dodged default.",
    "yaml_example": "layers:\n  - name: geom_bar\n  - name: position_identity",
})
def handle_position_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Default position (no adjustment)."""
    return _apply_position(p, position_identity(**spec))


@register_plot_component("position_stack", ui_schema={
    "label": "Stack",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "stack", "cumulative", "bar"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_stack"]}],
    "allow_extra_params": False,
    "params": {
        "vjust": {"widget": "number", "label": "Vertical justification (0–1)", "required": False, "default": 0.5},
        "reverse": {"widget": "bool", "label": "Reverse stacking order", "required": False, "default": False},
    },
    "description": "Stack bars or areas on top of each other; the default for multi-group geom_bar \u2014 use to show part-to-whole composition.",
    "yaml_example": "layers:\n  - name: geom_bar\n  - name: position_stack",
})
def handle_position_stack(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Stack objects on top of each other."""
    return _apply_position(p, position_stack(**spec))


@register_plot_component("position_fill", ui_schema={
    "label": "Fill (proportional stack)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "fill", "stack", "proportional", "100%", "bar"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_fill"]}],
    "allow_extra_params": False,
    "params": {
        "vjust": {"widget": "number", "label": "Vertical justification (0–1)", "required": False, "default": 0.5},
        "reverse": {"widget": "bool", "label": "Reverse stacking order", "required": False, "default": False},
    },
    "description": "Stack and normalise to 100%; use for 100% stacked bar charts comparing proportions across categories.",
    "yaml_example": "layers:\n  - name: geom_bar\n  - name: position_fill",
})
def handle_position_fill(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Stack objects and standardize to 100% height."""
    return _apply_position(p, position_fill(**spec))


@register_plot_component("position_dodge", ui_schema={
    "label": "Dodge (side-by-side)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "dodge", "side-by-side", "grouped", "bar"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_dodge"]}],
    "allow_extra_params": False,
    "params": {
        "width": {"widget": "number", "label": "Dodging width (default: None = uses geom width)", "required": False},
    },
    "description": "Place grouped bars side by side; the most common position for grouped bar charts.",
    "yaml_example": "layers:\n  - name: geom_bar\n  - name: position_dodge",
})
def handle_position_dodge(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Place objects side-by-side."""
    return _apply_position(p, position_dodge(**spec))


@register_plot_component("position_dodge2", ui_schema={
    "label": "Dodge2 (enhanced side-by-side)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "dodge2", "side-by-side", "boxplot", "violin"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_dodge2"]}],
    "allow_extra_params": False,
    "params": {
        "width": {"widget": "number", "label": "Dodging width", "required": False},
        "preserve": {"widget": "enum", "label": "Width preservation", "required": False,
                     "default": "total", "options": ["total", "single"]},
        "padding": {"widget": "number", "label": "Gap between dodged elements (0–1)", "required": False, "default": 0.1},
        "reverse": {"widget": "bool", "label": "Reverse dodge order", "required": False, "default": False},
    },
    "description": "Like position_dodge but with padding between groups; use when bars from different groups touch and you want visual separation.",
    "yaml_example": "layers:\n  - name: geom_bar\n  - name: position_dodge2\n    params:\n      padding: 0.1",
})
def handle_position_dodge2(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Enhanced dodging for varying widths."""
    return _apply_position(p, position_dodge2(**spec))


@register_plot_component("position_jitter", ui_schema={
    "label": "Jitter (random scatter)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "jitter", "scatter", "overplot", "noise"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_jitter"]}],
    "allow_extra_params": False,
    "params": {
        "width": {"widget": "number", "label": "Jitter width (horizontal amount)", "required": False, "default": 0.4},
        "height": {"widget": "number", "label": "Jitter height (vertical amount)", "required": False, "default": 0.4},
        "random_state": {"widget": "number", "label": "Random seed for reproducibility", "required": False},
    },
    "description": "Add random noise to point positions to reduce overplotting; use with geom_point for categorical scatter \u2014 prefer geom_sina for publication.",
    "yaml_example": "layers:\n  - name: geom_point\n  - name: position_jitter\n    params:\n      width: 0.2",
})
def handle_position_jitter(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Add random noise to prevent overplotting."""
    return _apply_position(p, position_jitter(**spec))


@register_plot_component("position_jitterdodge", ui_schema={
    "label": "JitterDodge (jitter within groups)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "jitter", "dodge", "grouped", "overplot"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_jitterdodge"]}],
    "allow_extra_params": False,
    "params": {
        "jitter_width": {"widget": "number", "label": "Jitter width within each group", "required": False, "default": 0.4},
        "jitter_height": {"widget": "number", "label": "Jitter height", "required": False, "default": 0.0},
        "dodge_width": {"widget": "number", "label": "Dodging width between groups", "required": False, "default": 0.75},
        "random_state": {"widget": "number", "label": "Random seed for reproducibility", "required": False},
    },
    "description": "Combine jitter and dodge for grouped scatter plots overlaid on grouped bars or boxes; use when showing individual points alongside group summaries.",
    "yaml_example": "layers:\n  - name: geom_point\n  - name: position_jitterdodge\n    params:\n      dodge_width: 0.75",
})
def handle_position_jitterdodge(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Combine jittering and dodging."""
    return _apply_position(p, position_jitterdodge(**spec))


@register_plot_component("position_nudge", ui_schema={
    "label": "Nudge (fixed offset)",
    "category": "position",
    "context": ["plot"],
    "tags": ["position", "nudge", "offset", "label", "text"],
    "wraps": [{"lib": "plotnine", "attr_path": ["position_nudge"]}],
    "allow_extra_params": False,
    "params": {
        "x": {"widget": "number", "label": "Horizontal offset", "required": False, "default": 0.0},
        "y": {"widget": "number", "label": "Vertical offset", "required": False, "default": 0.0},
    },
    "description": "Shift points by a fixed x/y offset; use with geom_text to prevent labels from overlapping the points they annotate.",
    "yaml_example": "layers:\n  - name: geom_text\n  - name: position_nudge\n    params:\n      y: 0.5",
})
def handle_position_nudge(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shift points by fixed offset."""
    return _apply_position(p, position_nudge(**spec))
