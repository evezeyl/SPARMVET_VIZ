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


@register_plot_component("coord_cartesian", ui_schema={
    "label": "Cartesian coordinates",
    "category": "coord",
    "context": ["plot"],
    "tags": ["coord", "cartesian", "zoom", "limits", "xlim", "ylim"],
    "wraps": [{"lib": "plotnine", "attr_path": ["coord_cartesian"]}],
    "allow_extra_params": False,
    "params": {
        "xlim": {"widget": "string", "label": "X limits as [min, max] (e.g. [0, 100])", "required": False},
        "ylim": {"widget": "string", "label": "Y limits as [min, max]", "required": False},
        "expand": {"widget": "bool", "label": "Add padding around data", "required": False, "default": True},
    },
    "description": "Set axis limits without dropping out-of-range data points; prefer over scale limits when zooming in without removing outliers.",
    "yaml_example": "layers:\n  - name: coord_cartesian\n    params:\n      xlim: [0, 100]",
})
def handle_coord_cartesian(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Cartesian coordinate system."""
    return p + coord_cartesian(**spec)


@register_plot_component("coord_flip", ui_schema={
    "label": "Flip coordinates (x ↔ y)",
    "category": "coord",
    "context": ["plot"],
    "tags": ["coord", "flip", "horizontal", "rotate", "bar"],
    "wraps": [{"lib": "plotnine", "attr_path": ["coord_flip"]}],
    "allow_extra_params": False,
    "params": {},
    "description": "Swap x and y axes; use for horizontal bar charts or when x-axis labels are long and overlap vertically.",
    "yaml_example": "layers:\n  - name: coord_flip",
})
def handle_coord_flip(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Flipped Cartesian coordinates (x becomes y)."""
    return p + coord_flip(**spec)


@register_plot_component("coord_fixed", ui_schema={
    "label": "Fixed aspect ratio",
    "category": "coord",
    "context": ["plot"],
    "tags": ["coord", "fixed", "aspect", "ratio", "square"],
    "wraps": [{"lib": "plotnine", "attr_path": ["coord_fixed"]}],
    "allow_extra_params": False,
    "params": {
        "ratio": {"widget": "number", "label": "Aspect ratio (y/x units)", "required": False, "default": 1.0},
        "xlim": {"widget": "string", "label": "X limits as [min, max]", "required": False},
        "ylim": {"widget": "string", "label": "Y limits as [min, max]", "required": False},
    },
    "description": "Force a fixed aspect ratio between x and y units; use for scatter plots where equal-unit scaling matters (e.g. geographic or spatial data).",
    "yaml_example": "layers:\n  - name: coord_fixed\n    params:\n      ratio: 1",
})
def handle_coord_fixed(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Cartesian coordinates with fixed aspect ratio."""
    return p + coord_fixed(**spec)


@register_plot_component("coord_equal", ui_schema={
    "label": "Equal aspect ratio (1:1)",
    "category": "coord",
    "context": ["plot"],
    "tags": ["coord", "equal", "1:1", "square", "aspect"],
    "wraps": [{"lib": "plotnine", "attr_path": ["coord_equal"]}],
    "allow_extra_params": False,
    "params": {
        "xlim": {"widget": "string", "label": "X limits as [min, max]", "required": False},
        "ylim": {"widget": "string", "label": "Y limits as [min, max]", "required": False},
    },
    "description": "Enforce 1:1 aspect ratio (equivalent to coord_fixed with ratio=1); use when x and y share the same unit scale.",
    "yaml_example": "layers:\n  - name: coord_equal",
})
def handle_coord_equal(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for fixed coordinates with 1:1 ratio."""
    return p + coord_equal(**spec)


@register_plot_component("coord_trans", ui_schema={
    "label": "Transformed coordinates",
    "category": "coord",
    "context": ["plot"],
    "tags": ["coord", "transform", "log", "sqrt", "axis"],
    "wraps": [{"lib": "plotnine", "attr_path": ["coord_trans"]}],
    "allow_extra_params": False,
    "params": {
        "x": {"widget": "string", "label": "X transformation (e.g. 'log10', 'sqrt')", "required": False},
        "y": {"widget": "string", "label": "Y transformation", "required": False},
        "xlim": {"widget": "string", "label": "X limits as [min, max]", "required": False},
        "ylim": {"widget": "string", "label": "Y limits as [min, max]", "required": False},
    },
    "description": "Apply a non-linear transformation to x or y after statistics are computed; unlike log scales, this preserves the geometry but changes axis spacing.",
    "yaml_example": "layers:\n  - name: coord_trans\n    params:\n      x: log10",
})
def handle_coord_trans(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Transformed Cartesian coordinates."""
    return p + coord_trans(**spec)


@register_plot_component("coord_lims", ui_schema={
    "label": "Coordinate limits (strict clip)",
    "category": "coord",
    "context": ["plot"],
    "tags": ["coord", "limits", "zoom", "clip", "xlim", "ylim"],
    "wraps": [{"lib": "plotnine", "attr_path": ["coord_cartesian"]}],
    "allow_extra_params": False,
    "params": {
        "xlim": {"widget": "string", "label": "X limits as [min, max] (strict — clips data)", "required": False},
        "ylim": {"widget": "string", "label": "Y limits as [min, max]", "required": False},
    },
    "description": "Set axis limits that also drop data outside the range (unlike coord_cartesian); use when out-of-range points should not influence statistics.",
    "yaml_example": "layers:\n  - name: coord_lims\n    params:\n      x: [0, 100]",
})
def handle_coord_lims(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Strict coordinate-level limits.
    Prevents data clipping that occurs with scale_x_continuous(limits=...).
    """
    # Use coord_cartesian for strict limits without clipping
    return p + coord_cartesian(**spec)
