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


@register_plot_component("guides", ui_schema={
    "label": "Guides container",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "colorbar", "hide", "none"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guides"]}],
    "allow_extra_params": True,
    "params": {
        "color": {"widget": "enum", "label": "Color guide", "required": False,
                  "options": ["legend", "colorbar", "none"]},
        "fill": {"widget": "enum", "label": "Fill guide", "required": False,
                 "options": ["legend", "colorbar", "none"]},
        "shape": {"widget": "enum", "label": "Shape guide", "required": False,
                  "options": ["legend", "none"]},
        "size": {"widget": "enum", "label": "Size guide", "required": False,
                 "options": ["legend", "none"]},
        "linetype": {"widget": "enum", "label": "Linetype guide", "required": False,
                     "options": ["legend", "none"]},
        "alpha": {"widget": "enum", "label": "Alpha guide", "required": False,
                  "options": ["legend", "none"]},
    },
    "description": "Control the guide (legend) for multiple aesthetics at once; use instead of individual scale guide= params when you need to configure several guides together.",
    "yaml_example": "layers:\n  - name: guides\n    params:\n      color: legend\n      fill: colorbar",
})
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


@register_plot_component("guide_legend", ui_schema={
    "label": "Legend guide",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "key", "rows", "cols"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic to apply guide to (e.g. color, fill)", "required": True},
        "title": {"widget": "string", "label": "Legend title (default: scale name)", "required": False},
        "nrow": {"widget": "number", "label": "Number of rows in key", "required": False},
        "ncol": {"widget": "number", "label": "Number of columns in key", "required": False},
        "reverse": {"widget": "bool", "label": "Reverse key order", "required": False, "default": False},
        "label_position": {"widget": "enum", "label": "Key label position", "required": False,
                           "default": "right", "options": ["top", "bottom", "left", "right"]},
    },
    "description": "Render a discrete guide as a key-legend; the default for categorical fill/colour \u2014 configure nrow, ncol, or key size here.",
    "yaml_example": "layers:\n  - name: guides\n    params:\n      fill: legend",
})
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


@register_plot_component("guide_colorbar", ui_schema={
    "label": "Colorbar guide",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "colorbar", "continuous", "gradient"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_colorbar"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic to apply guide to (e.g. color, fill)", "required": True},
        "title": {"widget": "string", "label": "Colorbar title", "required": False},
        "barwidth": {"widget": "number", "label": "Bar width (grid units)", "required": False},
        "barheight": {"widget": "number", "label": "Bar height (grid units)", "required": False},
        "nbin": {"widget": "number", "label": "Number of color bins", "required": False, "default": 300},
        "reverse": {"widget": "bool", "label": "Reverse colorbar direction", "required": False, "default": False},
    },
    "description": "Render a continuous guide as a gradient colour bar; use with continuous fill/colour scales to show the value range.",
    "yaml_example": "layers:\n  - name: guides\n    params:\n      fill: colorbar",
})
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


@register_plot_component("guide_colourbar", ui_schema={
    "label": "Colourbar guide (alias)",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "colorbar", "colourbar", "continuous", "gradient"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_colorbar"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic to apply guide to", "required": True},
        "title": {"widget": "string", "label": "Colourbar title", "required": False},
        "barwidth": {"widget": "number", "label": "Bar width (grid units)", "required": False},
        "barheight": {"widget": "number", "label": "Bar height (grid units)", "required": False},
    },
    "description": "British spelling alias for guide_colorbar; identical behaviour \u2014 use whichever spelling is consistent with the rest of your manifest.",
    "yaml_example": "layers:\n  - name: guides\n    params:\n      fill: colourbar",
})
def handle_guide_colourbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Alias for guide_colorbar."""
    return handle_guide_colorbar(p, spec)


@register_plot_component("guide_none", ui_schema={
    "label": "Remove guide (hide legend)",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "none", "hide", "remove", "legend"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guides"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic to hide guide for (e.g. color, fill)", "required": True},
    },
    "description": "Suppress a guide entirely; use when the legend adds no information (e.g. fill is redundant with a text label or facet strip).",
    "yaml_example": "layers:\n  - name: guides\n    params:\n      fill: none",
})
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


@register_plot_component("guide_nrow", ui_schema={
    "label": "Legend rows count",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "rows", "layout"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic (e.g. color, fill)", "required": True},
        "nrow": {"widget": "number", "label": "Number of rows in legend", "required": True},
    },
    "description": "Set the number of rows in a legend; use to control legend layout when many categories would produce an overly tall legend.",
    "yaml_example": "layers:\n  - name: guide_nrow\n    params:\n      nrow: 2",
})
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


@register_plot_component("guide_ncol", ui_schema={
    "label": "Legend columns count",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "cols", "columns", "layout"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic (e.g. color, fill)", "required": True},
        "ncol": {"widget": "number", "label": "Number of columns in legend", "required": True},
    },
    "description": "Set the number of columns in a legend; use to arrange legend keys horizontally when legend width is constrained.",
    "yaml_example": "layers:\n  - name: guide_ncol\n    params:\n      ncol: 3",
})
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


@register_plot_component("guide_title", ui_schema={
    "label": "Legend title",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "title"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic (e.g. color, fill)", "required": True},
        "title": {"widget": "string", "label": "Legend title text", "required": True},
    },
    "description": "Override the title of a specific guide; use when the default column name would be unclear to report readers.",
    "yaml_example": "layers:\n  - name: guide_title\n    params:\n      title: Resistance class",
})
def handle_guide_title(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set title for a guide."""
    mapping = spec.pop("mapping", None)
    title = spec.pop("title", spec.pop("value", None))
    if not mapping:
        print("Warning: guide_title requires 'mapping'.")
        return p
    # Try to detect guide type or default to legend if unknown mapping
    return p + guides(**{mapping: guide_legend(title=title, **spec)})


@register_plot_component("guide_label", ui_schema={
    "label": "Legend labels toggle",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "labels", "show", "hide"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic (e.g. color, fill)", "required": True},
        "labels": {"widget": "bool", "label": "Show labels", "required": False, "default": True},
    },
    "description": "Override the labels shown in a guide; use to recode technical column values to human-readable names without modifying source data.",
    "yaml_example": "layers:\n  - name: guide_label\n    params:\n      labels: [Susceptible, Resistant]",
})
def handle_guide_label(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to toggle/format labels for a guide."""
    mapping = spec.pop("mapping", None)
    labels = spec.pop("labels", spec.pop("value", True))
    if not mapping:
        print("Warning: guide_label requires 'mapping'.")
        return p
    return p + guides(**{mapping: guide_legend(labels=labels, **spec)})


@register_plot_component("guide_direction", ui_schema={
    "label": "Legend direction",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "direction", "horizontal", "vertical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic (e.g. color, fill)", "required": True},
        "direction": {"widget": "enum", "label": "Legend direction", "required": True,
                      "default": "horizontal", "options": ["horizontal", "vertical"]},
    },
    "description": "Set the guide layout direction to horizontal or vertical; use horizontal for a legend placed below or above the plot.",
    "yaml_example": "layers:\n  - name: guide_direction\n    params:\n      direction: horizontal",
})
def handle_guide_direction(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set direction for a guide."""
    mapping = spec.pop("mapping", None)
    direction = spec.pop("direction", spec.pop("value", "horizontal"))
    if not mapping:
        print("Warning: guide_direction requires 'mapping'.")
        return p
    return p + guides(**{mapping: guide_legend(direction=direction, **spec)})


@register_plot_component("guide_reverse", ui_schema={
    "label": "Reverse legend",
    "category": "guide",
    "context": ["plot"],
    "tags": ["guide", "legend", "reverse", "order"],
    "wraps": [{"lib": "plotnine", "attr_path": ["guide_legend"]}],
    "allow_extra_params": False,
    "params": {
        "mapping": {"widget": "string", "label": "Aesthetic (e.g. color, fill)", "required": True},
        "reverse": {"widget": "bool", "label": "Reverse legend key order", "required": False, "default": True},
    },
    "description": "Reverse the order of legend keys; use when the natural ordering of a factor places the most important category at the bottom of the legend.",
    "yaml_example": "layers:\n  - name: guide_reverse\n    params:\n      reverse: true",
})
def handle_guide_reverse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to reverse a guide."""
    mapping = spec.pop("mapping", None)
    reverse = spec.pop("reverse", spec.pop("value", True))
    if not mapping:
        print("Warning: guide_reverse requires 'mapping'.")
        return p
    return p + guides(**{mapping: guide_legend(reverse=reverse, **spec)})
