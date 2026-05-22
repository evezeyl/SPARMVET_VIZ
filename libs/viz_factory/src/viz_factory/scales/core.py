from typing import Dict, Any
from matplotlib.ticker import MaxNLocator

# @deps
# provides: component:scale_color_gradient, component:scale_fill_gradient, component:scale_color_gradient2, component:scale_fill_gradient2, component:scale_color_gradientn, component:scale_fill_gradientn, component:scale_color_distiller, component:scale_fill_distiller, component:scale_color_cmap, component:scale_fill_cmap, component:scale_color_viridis_d, component:scale_fill_viridis_d, component:scale_color_viridis_c, component:scale_fill_viridis_c, component:scale_color_cmap_d, component:scale_fill_cmap_d, component:scale_color_discrete, component:scale_fill_discrete, component:scale_color_brewer, component:scale_fill_brewer, component:scale_color_manual, component:scale_fill_manual, component:scale_x_continuous, component:scale_y_continuous, component:scale_x_discrete, component:scale_y_discrete, component:scale_x_log10, component:scale_y_log10, component:scale_x_reverse, component:scale_y_reverse, component:scale_x_datetime, component:scale_y_datetime, component:scale_x_date, component:scale_y_date, component:scale_x_sqrt, component:scale_y_sqrt, component:scale_x_symlog, component:scale_y_symlog, component:scale_x_timedelta, component:scale_y_timedelta, component:scale_size_continuous, component:scale_size_discrete, component:scale_shape_discrete, component:scale_alpha_continuous, component:scale_alpha_discrete, component:scale_linetype_discrete, component:scale_stroke_continuous, component:scale_color_identity, component:scale_fill_identity, component:scale_size_identity, component:scale_shape_identity, component:scale_alpha_identity, component:scale_linetype_identity, component:scale_stroke_identity, component:scale_alpha, component:scale_alpha_manual, component:scale_size, component:scale_size_manual, component:scale_size_area, component:scale_shape, component:scale_shape_manual, component:scale_linetype, component:scale_linetype_manual, component:scale_color_hue, component:scale_fill_hue, component:scale_color_continuous, component:scale_fill_continuous
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import (
    scale_color_gradient, scale_fill_gradient,
    scale_color_gradient2, scale_fill_gradient2,
    scale_color_gradientn, scale_fill_gradientn,
    scale_color_distiller, scale_fill_distiller,
    scale_color_cmap, scale_fill_cmap,
    scale_color_cmap_d, scale_fill_cmap_d,
    scale_color_discrete, scale_fill_discrete,
    scale_color_brewer, scale_fill_brewer,
    scale_color_manual, scale_fill_manual,
    scale_x_continuous, scale_y_continuous,
    scale_x_discrete, scale_y_discrete,
    scale_x_log10, scale_y_log10,
    scale_x_reverse, scale_y_reverse,
    scale_x_datetime, scale_y_datetime,
    scale_x_date, scale_y_date,
    scale_x_sqrt, scale_y_sqrt,
    scale_x_symlog, scale_y_symlog,
    scale_x_timedelta, scale_y_timedelta,
    scale_size_continuous, scale_size_discrete,
    scale_shape_discrete,
    scale_alpha_continuous, scale_alpha_discrete,
    scale_linetype_discrete,
    scale_color_identity, scale_fill_identity,
    scale_size_identity, scale_shape_identity,
    scale_alpha_identity, scale_linetype_identity,
    scale_stroke_continuous,
    scale_stroke_identity,
    scale_alpha, scale_alpha_manual,
    scale_size, scale_size_manual, scale_size_area,
    scale_shape, scale_shape_manual,
    scale_linetype, scale_linetype_manual,
    scale_color_hue, scale_fill_hue,
    scale_color_continuous, scale_fill_continuous,
    ggplot
)
from viz_factory.registry import register_plot_component


# ── Shared parameter dictionaries ─────────────────────────────────────────────

_SCALE_GUIDE_PARAMS = {
    "name": {"widget": "string", "label": "Scale title (legend / axis label)", "required": False},
    "guide": {"widget": "enum", "label": "Guide type", "required": False,
              "options": ["legend", "colorbar", "none"]},
}

_SCALE_AXIS_PARAMS = {
    "name": {"widget": "string", "label": "Axis label", "required": False},
    "breaks": {"widget": "string", "label": "Break points (list or expression)", "required": False},
    "labels": {"widget": "string", "label": "Break labels", "required": False},
    "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
}

_VIRIDIS_PARAMS = {
    "option": {"widget": "enum", "label": "Viridis palette variant", "required": False,
               "default": "viridis",
               "options": ["viridis", "magma", "inferno", "plasma", "cividis"]},
    "direction": {"widget": "enum", "label": "Palette direction (1=normal, -1=reversed)",
                  "required": False, "default": "1", "options": ["1", "-1"]},
    "name": {"widget": "string", "label": "Scale title", "required": False},
    "guide": {"widget": "enum", "label": "Guide type", "required": False,
              "options": ["legend", "colorbar", "none"]},
}

_SCALE_IDENTITY_PARAMS = {
    "name": {"widget": "string", "label": "Legend title", "required": False},
    "guide": {"widget": "enum", "label": "Guide type", "required": False,
              "options": ["legend", "none"]},
}


# ── Color / Fill gradient scales ──────────────────────────────────────────────

@register_plot_component("scale_color_gradient", ui_schema={
    "label": "Color gradient (2-stop continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "gradient", "continuous", "sequential"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_gradient"]}],
    "allow_extra_params": True,
    "params": {
        "low": {"widget": "color", "label": "Low value colour", "required": False, "default": "#132B43"},
        "high": {"widget": "color", "label": "High value colour", "required": False, "default": "#56B1F7"},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous variable to a 2-colour gradient; the simplest continuous colour scale \u2014 use scale_color_viridis_c for perceptual uniformity.",
    "yaml_example": "layers:\n  - name: scale_color_gradient\n    params:\n      low: '#132B43'\n      high: '#56B1F7'",
})
def handle_color_gradient(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_gradient(**spec)


@register_plot_component("scale_fill_gradient", ui_schema={
    "label": "Fill gradient (2-stop continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "gradient", "continuous", "sequential"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_gradient"]}],
    "allow_extra_params": True,
    "params": {
        "low": {"widget": "color", "label": "Low value colour", "required": False, "default": "#132B43"},
        "high": {"widget": "color", "label": "High value colour", "required": False, "default": "#56B1F7"},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous fill variable to a 2-colour gradient; use for heatmaps or geom_tile where the fill encodes a numeric value.",
    "yaml_example": "layers:\n  - name: scale_fill_gradient\n    params:\n      low: white\n      high: '#345beb'",
})
def handle_fill_gradient(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_gradient(**spec)


@register_plot_component("scale_color_gradient2", ui_schema={
    "label": "Color gradient2 (diverging 3-stop)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "gradient", "diverging", "midpoint", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_gradient2"]}],
    "allow_extra_params": True,
    "params": {
        "low": {"widget": "color", "label": "Low end colour", "required": False, "default": "#2166AC"},
        "mid": {"widget": "color", "label": "Midpoint colour", "required": False, "default": "#F7F7F7"},
        "high": {"widget": "color", "label": "High end colour", "required": False, "default": "#D6604D"},
        "midpoint": {"widget": "number", "label": "Data value at midpoint", "required": False, "default": 0},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Diverging 2-stop gradient with a midpoint; use when the variable has a meaningful centre (e.g. z-scores, log fold-change).",
    "yaml_example": "layers:\n  - name: scale_color_gradient2\n    params:\n      low: blue\n      mid: white\n      high: red\n      midpoint: 0",
})
def handle_color_gradient2(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_gradient2(**spec)


@register_plot_component("scale_fill_gradient2", ui_schema={
    "label": "Fill gradient2 (diverging 3-stop)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "gradient", "diverging", "midpoint", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_gradient2"]}],
    "allow_extra_params": True,
    "params": {
        "low": {"widget": "color", "label": "Low end colour", "required": False, "default": "#2166AC"},
        "mid": {"widget": "color", "label": "Midpoint colour", "required": False, "default": "#F7F7F7"},
        "high": {"widget": "color", "label": "High end colour", "required": False, "default": "#D6604D"},
        "midpoint": {"widget": "number", "label": "Data value at midpoint", "required": False, "default": 0},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Diverging 2-stop fill gradient with a midpoint; use for heatmaps where the fill diverges around a central value.",
    "yaml_example": "layers:\n  - name: scale_fill_gradient2\n    params:\n      low: blue\n      mid: white\n      high: red\n      midpoint: 0",
})
def handle_fill_gradient2(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_gradient2(**spec)


@register_plot_component("scale_color_gradientn", ui_schema={
    "label": "Color gradientn (multi-stop continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "gradient", "multi-stop", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_gradientn"]}],
    "allow_extra_params": True,
    "params": {
        "colors": {"widget": "string", "label": "Colour list (e.g. ['#blue','#white','#red'])", "required": True},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous variable to an n-colour gradient; use for custom multi-stop palettes (e.g. temperature maps, clinical risk scores).",
    "yaml_example": "layers:\n  - name: scale_color_gradientn\n    params:\n      colours: [blue, white, red]",
})
def handle_color_gradientn(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_gradientn(**spec)


@register_plot_component("scale_fill_gradientn", ui_schema={
    "label": "Fill gradientn (multi-stop continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "gradient", "multi-stop", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_gradientn"]}],
    "allow_extra_params": True,
    "params": {
        "colors": {"widget": "string", "label": "Colour list (e.g. ['#blue','#white','#red'])", "required": True},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous fill variable to an n-colour gradient; use for heatmaps requiring more than two colour stops.",
    "yaml_example": "layers:\n  - name: scale_fill_gradientn\n    params:\n      colours: [blue, white, red]",
})
def handle_fill_gradientn(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_gradientn(**spec)


# ── Distiller (RColorBrewer continuous) ──────────────────────────────────────

@register_plot_component("scale_color_distiller", ui_schema={
    "label": "Color distiller (RColorBrewer continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "distiller", "brewer", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_distiller"]}],
    "allow_extra_params": True,
    "params": {
        "palette": {"widget": "string", "label": "RColorBrewer palette (e.g. Blues, RdYlBu)", "required": False, "default": "Blues"},
        "type": {"widget": "enum", "label": "Palette type", "required": False,
                 "default": "seq", "options": ["seq", "div", "qual"]},
        "direction": {"widget": "enum", "label": "Direction", "required": False,
                      "default": "1", "options": ["1", "-1"]},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous colour variable using an RColorBrewer palette; use for sequential or diverging continuous data when a named palette name is sufficient.",
    "yaml_example": "layers:\n  - name: scale_color_distiller\n    params:\n      palette: Blues",
})
def handle_color_distiller(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_distiller(**spec)


@register_plot_component("scale_fill_distiller", ui_schema={
    "label": "Fill distiller (RColorBrewer continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "distiller", "brewer", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_distiller"]}],
    "allow_extra_params": True,
    "params": {
        "palette": {"widget": "string", "label": "RColorBrewer palette (e.g. Blues, RdYlBu)", "required": False, "default": "Blues"},
        "type": {"widget": "enum", "label": "Palette type", "required": False,
                 "default": "seq", "options": ["seq", "div", "qual"]},
        "direction": {"widget": "enum", "label": "Direction", "required": False,
                      "default": "1", "options": ["1", "-1"]},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous fill variable using an RColorBrewer palette; use for heatmaps when an RColorBrewer name is preferred over manual hex colours.",
    "yaml_example": "layers:\n  - name: scale_fill_distiller\n    params:\n      palette: RdYlBu",
})
def handle_fill_distiller(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_distiller(**spec)


# ── Matplotlib cmap scales (continuous) ──────────────────────────────────────

@register_plot_component("scale_color_cmap", ui_schema={
    "label": "Color matplotlib colormap (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "cmap", "matplotlib", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_cmap"]}],
    "allow_extra_params": True,
    "params": {
        "cmap_name": {"widget": "string", "label": "Matplotlib colormap name (e.g. viridis, Blues, RdBu)", "required": False, "default": "viridis"},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous colour variable using a matplotlib colormap by name; use when the colourmap name is already known from Python/matplotlib conventions.",
    "yaml_example": "layers:\n  - name: scale_color_cmap\n    params:\n      cmap_name: viridis",
})
def handle_color_cmap(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_cmap(**spec)


@register_plot_component("scale_fill_cmap", ui_schema={
    "label": "Fill matplotlib colormap (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "cmap", "matplotlib", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_cmap"]}],
    "allow_extra_params": True,
    "params": {
        "cmap_name": {"widget": "string", "label": "Matplotlib colormap name (e.g. viridis, Blues, RdBu)", "required": False, "default": "viridis"},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a continuous fill variable using a matplotlib colormap; use for heatmaps when a matplotlib colormap name is preferred.",
    "yaml_example": "layers:\n  - name: scale_fill_cmap\n    params:\n      cmap_name: plasma",
})
def handle_fill_cmap(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_cmap(**spec)


# ── Viridis scales ────────────────────────────────────────────────────────────

@register_plot_component("scale_color_viridis_d", ui_schema={
    "label": "Color viridis (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "viridis", "discrete", "accessible"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_cmap_d"]}],
    "allow_extra_params": False,
    "params": _VIRIDIS_PARAMS,
    "description": "Map a discrete colour variable to the perceptually-uniform viridis palette; the recommended default for discrete colour scales \u2014 accessible to colour-blind viewers.",
    "yaml_example": "layers:\n  - name: scale_color_viridis_d\n    params:\n      option: D",
})
def handle_color_viridis_d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    if "cmap_name" not in spec:
        spec["cmap_name"] = spec.pop("option", "viridis")
    return p + scale_color_cmap_d(**spec)


@register_plot_component("scale_fill_viridis_d", ui_schema={
    "label": "Fill viridis (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "viridis", "discrete", "accessible"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_cmap_d"]}],
    "allow_extra_params": False,
    "params": _VIRIDIS_PARAMS,
    "description": "Map a discrete fill variable to the viridis palette; use for grouped bars or heatmap categories where colour-blind accessibility matters.",
    "yaml_example": "layers:\n  - name: scale_fill_viridis_d\n    params:\n      option: D",
})
def handle_fill_viridis_d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    if "cmap_name" not in spec:
        spec["cmap_name"] = spec.pop("option", "viridis")
    return p + scale_fill_cmap_d(**spec)


@register_plot_component("scale_color_viridis_c", ui_schema={
    "label": "Color viridis (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "viridis", "continuous", "accessible"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_cmap"]}],
    "allow_extra_params": False,
    "params": {
        **_VIRIDIS_PARAMS,
        "begin": {"widget": "number", "label": "Start of palette range (0–1)", "required": False, "default": 0},
        "end": {"widget": "number", "label": "End of palette range (0–1)", "required": False, "default": 1},
    },
    "description": "Map a continuous colour variable to the perceptually-uniform viridis palette; the recommended default for sequential continuous colour scales.",
    "yaml_example": "layers:\n  - name: scale_color_viridis_c\n    params:\n      option: D",
})
def handle_color_viridis_c(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    if "cmap_name" not in spec:
        spec["cmap_name"] = spec.pop("option", "viridis")
    return p + scale_color_cmap(**spec)


@register_plot_component("scale_fill_viridis_c", ui_schema={
    "label": "Fill viridis (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "viridis", "continuous", "accessible"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_cmap"]}],
    "allow_extra_params": False,
    "params": {
        **_VIRIDIS_PARAMS,
        "begin": {"widget": "number", "label": "Start of palette range (0–1)", "required": False, "default": 0},
        "end": {"widget": "number", "label": "End of palette range (0–1)", "required": False, "default": 1},
    },
    "description": "Map a continuous fill variable to the viridis palette; use for tile/raster heatmaps where perceptual uniformity is required.",
    "yaml_example": "layers:\n  - name: scale_fill_viridis_c\n    params:\n      option: D",
})
def handle_fill_viridis_c(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    if "cmap_name" not in spec:
        spec["cmap_name"] = spec.pop("option", "viridis")
    return p + scale_fill_cmap(**spec)


# ── Matplotlib cmap discrete scales ──────────────────────────────────────────

@register_plot_component("scale_color_cmap_d", ui_schema={
    "label": "Color matplotlib colormap (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "cmap", "matplotlib", "discrete"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_cmap_d"]}],
    "allow_extra_params": True,
    "params": {
        "cmap_name": {"widget": "string", "label": "Matplotlib colormap name", "required": False, "default": "tab10"},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a discrete colour variable to a matplotlib colormap; use when the colormap name is from matplotlib and the variable is categorical.",
    "yaml_example": "layers:\n  - name: scale_color_cmap_d\n    params:\n      cmap_name: tab10",
})
def handle_color_cmap_d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_cmap_d(**spec)


@register_plot_component("scale_fill_cmap_d", ui_schema={
    "label": "Fill matplotlib colormap (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "cmap", "matplotlib", "discrete"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_cmap_d"]}],
    "allow_extra_params": True,
    "params": {
        "cmap_name": {"widget": "string", "label": "Matplotlib colormap name", "required": False, "default": "tab10"},
        **_SCALE_GUIDE_PARAMS,
    },
    "description": "Map a discrete fill variable to a matplotlib colormap; use for categorical fill when a matplotlib colormap name is preferred over manual hex values.",
    "yaml_example": "layers:\n  - name: scale_fill_cmap_d\n    params:\n      cmap_name: Set2",
})
def handle_fill_cmap_d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_cmap_d(**spec)


# ── Discrete color / fill scales ─────────────────────────────────────────────

@register_plot_component("scale_color_discrete", ui_schema={
    "label": "Color scale (discrete default)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "discrete", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_discrete"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Default discrete colour scale; use when you want plotnine to choose colours automatically for a categorical variable without specifying a palette.",
    "yaml_example": "layers:\n  - name: scale_color_discrete",
})
def handle_color_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_discrete(**spec)


@register_plot_component("scale_fill_discrete", ui_schema={
    "label": "Fill scale (discrete default)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "discrete", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_discrete"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Default discrete fill scale; use when you want plotnine to choose fills automatically \u2014 override with scale_fill_manual when specific colours are required.",
    "yaml_example": "layers:\n  - name: scale_fill_discrete",
})
def handle_fill_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_discrete(**spec)


# ── RColorBrewer discrete scales ─────────────────────────────────────────────

@register_plot_component("scale_color_brewer", ui_schema={
    "label": "Color brewer (discrete RColorBrewer)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "brewer", "discrete", "qualitative"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_brewer"]}],
    "allow_extra_params": True,
    "params": {
        "palette": {"widget": "string", "label": "Brewer palette (e.g. Set1, Paired, Dark2)", "required": False, "default": "Set1"},
        "type": {"widget": "enum", "label": "Palette type", "required": False,
                 "default": "qual", "options": ["qual", "seq", "div"]},
        "direction": {"widget": "enum", "label": "Direction", "required": False,
                      "default": "1", "options": ["1", "-1"]},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete colour variable to an RColorBrewer palette; a practical choice for categorical data when a named palette name is sufficient.",
    "yaml_example": "layers:\n  - name: scale_color_brewer\n    params:\n      palette: Set1",
})
def handle_color_brewer(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_brewer(**spec)


@register_plot_component("scale_fill_brewer", ui_schema={
    "label": "Fill brewer (discrete RColorBrewer)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "brewer", "discrete", "qualitative"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_brewer"]}],
    "allow_extra_params": True,
    "params": {
        "palette": {"widget": "string", "label": "Brewer palette (e.g. Set1, Paired, Dark2)", "required": False, "default": "Set1"},
        "type": {"widget": "enum", "label": "Palette type", "required": False,
                 "default": "qual", "options": ["qual", "seq", "div"]},
        "direction": {"widget": "enum", "label": "Direction", "required": False,
                      "default": "1", "options": ["1", "-1"]},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete fill variable to an RColorBrewer palette; use for grouped bar charts or box plots when a named palette is preferable to manual hex values.",
    "yaml_example": "layers:\n  - name: scale_fill_brewer\n    params:\n      palette: Set2",
})
def handle_fill_brewer(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_brewer(**spec)


# ── Manual color / fill scales ────────────────────────────────────────────────

@register_plot_component("scale_color_manual", ui_schema={
    "label": "Color manual (explicit palette)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "manual", "custom", "palette"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_manual"]}],
    "allow_extra_params": True,
    "params": {
        "values": {"widget": "string", "label": "Named colour dict or list (e.g. {A: '#red', B: '#blue'})", "required": True},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete colour variable to exact hex values; use when brand colours or institution-specific palettes must be applied precisely.",
    "yaml_example": "layers:\n  - name: scale_color_manual\n    params:\n      values: ['#345beb', '#10a395', '#ffc107']",
})
def handle_color_manual(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_manual(**spec)


@register_plot_component("scale_fill_manual", ui_schema={
    "label": "Fill manual (explicit palette)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "manual", "custom", "palette"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_manual"]}],
    "allow_extra_params": True,
    "params": {
        "values": {"widget": "string", "label": "Named colour dict or list (e.g. {A: '#red', B: '#blue'})", "required": True},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete fill variable to exact hex values; use when specific brand colours must be assigned to named categories.",
    "yaml_example": "layers:\n  - name: scale_fill_manual\n    params:\n      values: ['#345beb', '#10a395', '#ffc107']",
})
def handle_fill_manual(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_manual(**spec)


# ── Helpers ───────────────────────────────────────────────────────────────────

def _integer_breaks(lims):
    return MaxNLocator(integer=True).tick_values(lims[0], lims[1])


def _resolve_continuous_spec(spec: Dict[str, Any]) -> Dict[str, Any]:
    spec = dict(spec)
    if spec.pop("breaks_integer", False):
        spec.setdefault("breaks", _integer_breaks)
    return spec


# ── Continuous axis scales ────────────────────────────────────────────────────

@register_plot_component("scale_x_continuous", ui_schema={
    "label": "X axis (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "continuous", "axis", "numeric"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_continuous"]}],
    "allow_extra_params": True,
    "params": {
        **_SCALE_AXIS_PARAMS,
        "expand": {"widget": "string", "label": "Axis expand (e.g. [0, 0])", "required": False},
        "breaks_integer": {"widget": "bool", "label": "Force integer breaks", "required": False, "default": False},
    },
    "description": "Control x-axis breaks, labels, limits, and expand for continuous numeric variables; use to customise tick spacing or suppress auto-expansion.",
    "yaml_example": "layers:\n  - name: scale_x_continuous\n    params:\n      breaks: [0, 25, 50, 75, 100]",
})
def handle_x_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_continuous(**_resolve_continuous_spec(spec))


@register_plot_component("scale_y_continuous", ui_schema={
    "label": "Y axis (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "continuous", "axis", "numeric"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_continuous"]}],
    "allow_extra_params": True,
    "params": {
        **_SCALE_AXIS_PARAMS,
        "expand": {"widget": "string", "label": "Axis expand (e.g. [0, 0])", "required": False},
        "breaks_integer": {"widget": "bool", "label": "Force integer breaks", "required": False, "default": False},
    },
    "description": "Control y-axis breaks, labels, limits, and expand for continuous numeric variables; use to set a fixed y range or custom tick marks.",
    "yaml_example": "layers:\n  - name: scale_y_continuous\n    params:\n      limits: [0, 100]",
})
def handle_y_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_continuous(**_resolve_continuous_spec(spec))


# ── Discrete axis scales ──────────────────────────────────────────────────────

@register_plot_component("scale_x_discrete", ui_schema={
    "label": "X axis (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "discrete", "axis", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_discrete"]}],
    "allow_extra_params": True,
    "params": {
        **_SCALE_AXIS_PARAMS,
        "expand": {"widget": "string", "label": "Axis expand", "required": False},
    },
    "description": "Control x-axis order and labels for discrete/categorical variables; use to reorder factor levels or rename axis tick labels.",
    "yaml_example": "layers:\n  - name: scale_x_discrete\n    params:\n      limits: [cat_a, cat_b, cat_c]",
})
def handle_x_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_discrete(**spec)


@register_plot_component("scale_y_discrete", ui_schema={
    "label": "Y axis (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "discrete", "axis", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_discrete"]}],
    "allow_extra_params": True,
    "params": {
        **_SCALE_AXIS_PARAMS,
        "expand": {"widget": "string", "label": "Axis expand", "required": False},
    },
    "description": "Control y-axis order and labels for discrete variables; use with coord_flip bar charts to specify the vertical category order.",
    "yaml_example": "layers:\n  - name: scale_y_discrete\n    params:\n      limits: [low, medium, high]",
})
def handle_y_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_discrete(**spec)


# ── Log10 axis scales ─────────────────────────────────────────────────────────

@register_plot_component("scale_x_log10", ui_schema={
    "label": "X axis log10 transform",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "log10", "logarithm", "transform"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_log10"]}],
    "allow_extra_params": True,
    "params": _SCALE_AXIS_PARAMS,
    "description": "Apply a log10 transformation to the x-axis; use for variables spanning orders of magnitude such as bacterial counts or p-values.",
    "yaml_example": "layers:\n  - name: scale_x_log10",
})
def handle_x_log10(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_log10(**spec)


@register_plot_component("scale_y_log10", ui_schema={
    "label": "Y axis log10 transform",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "log10", "logarithm", "transform"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_log10"]}],
    "allow_extra_params": True,
    "params": _SCALE_AXIS_PARAMS,
    "description": "Apply a log10 transformation to the y-axis; use for count data or MIC values where the distribution is heavily right-skewed.",
    "yaml_example": "layers:\n  - name: scale_y_log10",
})
def handle_y_log10(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_log10(**spec)


# ── Reverse axis scales ───────────────────────────────────────────────────────

@register_plot_component("scale_x_reverse", ui_schema={
    "label": "X axis reversed",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "reverse", "flip", "descending"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_reverse"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
    },
    "description": "Reverse the direction of the x-axis; use for dendrograms, forest plots, or year axes where decreasing order is conventional.",
    "yaml_example": "layers:\n  - name: scale_x_reverse",
})
def handle_x_reverse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_reverse(**spec)


@register_plot_component("scale_y_reverse", ui_schema={
    "label": "Y axis reversed",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "reverse", "flip", "descending"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_reverse"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
    },
    "description": "Reverse the direction of the y-axis; use when higher values should appear at the bottom (e.g. depth profiles, rank plots).",
    "yaml_example": "layers:\n  - name: scale_y_reverse",
})
def handle_y_reverse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_reverse(**spec)


# ── Datetime / Date axis scales ───────────────────────────────────────────────

@register_plot_component("scale_x_datetime", ui_schema={
    "label": "X axis datetime",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "datetime", "time", "date", "temporal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_datetime"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "date_labels": {"widget": "string", "label": "Date label format (e.g. %Y-%m-%d)", "required": False},
        "date_breaks": {"widget": "string", "label": "Date break interval (e.g. 1 month)", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min_date, max_date]", "required": False},
    },
    "description": "Format and control a datetime x-axis; use when the x column is a Python datetime type and you need custom date formatting.",
    "yaml_example": "layers:\n  - name: scale_x_datetime\n    params:\n      date_labels: '%Y-%m'",
})
def handle_x_datetime(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_datetime(**spec)


@register_plot_component("scale_y_datetime", ui_schema={
    "label": "Y axis datetime",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "datetime", "time", "date", "temporal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_datetime"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "date_labels": {"widget": "string", "label": "Date label format (e.g. %Y-%m-%d)", "required": False},
        "date_breaks": {"widget": "string", "label": "Date break interval (e.g. 1 month)", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min_date, max_date]", "required": False},
    },
    "description": "Format and control a datetime y-axis; use for Gantt-style charts or horizontal time plots where the y axis is datetime.",
    "yaml_example": "layers:\n  - name: scale_y_datetime\n    params:\n      date_labels: '%Y-%m'",
})
def handle_y_datetime(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_datetime(**spec)


@register_plot_component("scale_x_date", ui_schema={
    "label": "X axis date",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "date", "temporal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_date"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "date_labels": {"widget": "string", "label": "Date label format (e.g. %b %Y)", "required": False},
        "date_breaks": {"widget": "string", "label": "Date break interval (e.g. 3 months)", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min_date, max_date]", "required": False},
    },
    "description": "Format and control a date (not datetime) x-axis; use when the x column contains Python date objects.",
    "yaml_example": "layers:\n  - name: scale_x_date\n    params:\n      date_labels: '%Y'",
})
def handle_x_date(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_date(**spec)


@register_plot_component("scale_y_date", ui_schema={
    "label": "Y axis date",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "date", "temporal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_date"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "date_labels": {"widget": "string", "label": "Date label format (e.g. %b %Y)", "required": False},
        "date_breaks": {"widget": "string", "label": "Date break interval (e.g. 3 months)", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min_date, max_date]", "required": False},
    },
    "description": "Format and control a date y-axis; use when the y column contains Python date objects.",
    "yaml_example": "layers:\n  - name: scale_y_date\n    params:\n      date_labels: '%Y'",
})
def handle_y_date(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_date(**spec)


# ── Sqrt axis scales ──────────────────────────────────────────────────────────

@register_plot_component("scale_x_sqrt", ui_schema={
    "label": "X axis square root transform",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "sqrt", "transform"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_sqrt"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
    },
    "description": "Apply a square-root transformation to the x-axis; intermediate between linear and log \u2014 use for count data with moderate right-skew.",
    "yaml_example": "layers:\n  - name: scale_x_sqrt",
})
def handle_x_sqrt(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_sqrt(**spec)


@register_plot_component("scale_y_sqrt", ui_schema={
    "label": "Y axis square root transform",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "sqrt", "transform"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_sqrt"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
    },
    "description": "Apply a square-root transformation to the y-axis; use for count histograms where log would exaggerate small values.",
    "yaml_example": "layers:\n  - name: scale_y_sqrt",
})
def handle_y_sqrt(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_sqrt(**spec)


# ── Symlog axis scales ────────────────────────────────────────────────────────

@register_plot_component("scale_x_symlog", ui_schema={
    "label": "X axis symmetric log transform",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "symlog", "log", "symmetric", "transform"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_symlog"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "linear_width": {"widget": "number", "label": "Linear region half-width (linthresh)", "required": False, "default": 1},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
    },
    "description": "Symmetric log transformation for x; handles zero and negative values unlike log10 \u2014 use when the variable includes negative values.",
    "yaml_example": "layers:\n  - name: scale_x_symlog",
})
def handle_x_symlog(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_symlog(**spec)


@register_plot_component("scale_y_symlog", ui_schema={
    "label": "Y axis symmetric log transform",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "symlog", "log", "symmetric", "transform"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_symlog"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "linear_width": {"widget": "number", "label": "Linear region half-width (linthresh)", "required": False, "default": 1},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits as [min, max]", "required": False},
    },
    "description": "Symmetric log transformation for y; use when y spans both positive and negative values (e.g. log fold-change with true zero).",
    "yaml_example": "layers:\n  - name: scale_y_symlog",
})
def handle_y_symlog(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_symlog(**spec)


# ── Timedelta axis scales ─────────────────────────────────────────────────────

@register_plot_component("scale_x_timedelta", ui_schema={
    "label": "X axis timedelta",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "x", "timedelta", "duration", "temporal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_x_timedelta"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits", "required": False},
    },
    "description": "Format a timedelta x-axis; use when x represents a duration (Python timedelta) rather than an absolute date.",
    "yaml_example": "layers:\n  - name: scale_x_timedelta",
})
def handle_x_timedelta(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_x_timedelta(**spec)


@register_plot_component("scale_y_timedelta", ui_schema={
    "label": "Y axis timedelta",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "y", "timedelta", "duration", "temporal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_y_timedelta"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Axis label", "required": False},
        "breaks": {"widget": "string", "label": "Break points", "required": False},
        "limits": {"widget": "string", "label": "Axis limits", "required": False},
    },
    "description": "Format a timedelta y-axis; use when y represents elapsed time or a duration.",
    "yaml_example": "layers:\n  - name: scale_y_timedelta",
})
def handle_y_timedelta(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_y_timedelta(**spec)


# ── Size scales ───────────────────────────────────────────────────────────────

@register_plot_component("scale_size_continuous", ui_schema={
    "label": "Size scale (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "size", "continuous", "bubble"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_size_continuous"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Output size range as [min, max] (pt)", "required": False, "default": "[1, 6]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a continuous variable to point size; use to encode a third numeric dimension in a scatter plot (bubble chart).",
    "yaml_example": "layers:\n  - name: scale_size_continuous\n    params:\n      range: [1, 10]",
})
def handle_size_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_size_continuous(**spec)


@register_plot_component("scale_size_discrete", ui_schema={
    "label": "Size scale (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "size", "discrete", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_size_discrete"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Output size range as [min, max] (pt)", "required": False, "default": "[1, 6]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to point size; avoid if possible \u2014 size is harder to discriminate categorically than colour.",
    "yaml_example": "layers:\n  - name: scale_size_discrete",
})
def handle_size_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_size_discrete(**spec)


# ── Shape scale ───────────────────────────────────────────────────────────────

@register_plot_component("scale_shape_discrete", ui_schema={
    "label": "Shape scale (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "shape", "discrete", "categorical", "point"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_shape_discrete"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to point shape; use as a secondary encoding alongside colour for accessibility (works in greyscale).",
    "yaml_example": "layers:\n  - name: scale_shape_discrete",
})
def handle_shape_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_shape_discrete(**spec)


# ── Alpha (opacity) scales ────────────────────────────────────────────────────

@register_plot_component("scale_alpha_continuous", ui_schema={
    "label": "Alpha scale (continuous opacity)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "alpha", "opacity", "continuous"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_alpha_continuous"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Opacity range as [min, max] (0–1)", "required": False, "default": "[0.1, 1]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a continuous variable to point/fill transparency; use sparingly \u2014 alpha is hard to read accurately but can indicate density or confidence.",
    "yaml_example": "layers:\n  - name: scale_alpha_continuous\n    params:\n      range: [0.2, 1.0]",
})
def handle_alpha_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_alpha_continuous(**spec)


@register_plot_component("scale_alpha_discrete", ui_schema={
    "label": "Alpha scale (discrete opacity)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "alpha", "opacity", "discrete"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_alpha_discrete"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Opacity range as [min, max] (0–1)", "required": False, "default": "[0.1, 1]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to alpha; rarely useful \u2014 prefer colour or shape for categorical distinction.",
    "yaml_example": "layers:\n  - name: scale_alpha_discrete",
})
def handle_alpha_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_alpha_discrete(**spec)


# ── Linetype scale ────────────────────────────────────────────────────────────

@register_plot_component("scale_linetype_discrete", ui_schema={
    "label": "Linetype scale (discrete)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "linetype", "discrete", "line", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_linetype_discrete"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to line type; use as a secondary encoding on line plots when colour alone is insufficient.",
    "yaml_example": "layers:\n  - name: scale_linetype_discrete",
})
def handle_linetype_discrete(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_linetype_discrete(**spec)


# ── Stroke scale ──────────────────────────────────────────────────────────────

@register_plot_component("scale_stroke_continuous", ui_schema={
    "label": "Stroke scale (continuous)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "stroke", "continuous", "border", "outline"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_stroke_continuous"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Stroke width range as [min, max] (pt)", "required": False, "default": "[0.2, 2]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a continuous variable to point stroke width; use to encode an extra numeric dimension when combined with a filled shape.",
    "yaml_example": "layers:\n  - name: scale_stroke_continuous\n    params:\n      range: [0.5, 2.0]",
})
def handle_stroke_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_stroke_continuous(**spec)


# ── Identity scales ───────────────────────────────────────────────────────────

@register_plot_component("scale_color_identity", ui_schema={
    "label": "Color identity (use raw values as colours)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "identity", "raw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal colour values from a data column as colours; the data column must already contain valid colour strings (hex or named).",
    "yaml_example": "layers:\n  - name: scale_color_identity",
})
def handle_color_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_identity(**spec)


@register_plot_component("scale_fill_identity", ui_schema={
    "label": "Fill identity (use raw values as colours)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "identity", "raw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal colour strings from a data column as fill values; the column must contain valid hex or named colour strings.",
    "yaml_example": "layers:\n  - name: scale_fill_identity",
})
def handle_fill_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_identity(**spec)


@register_plot_component("scale_size_identity", ui_schema={
    "label": "Size identity (use raw values as point size)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "size", "identity", "raw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_size_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal numeric values from a data column directly as point sizes; bypasses the default size range mapping.",
    "yaml_example": "layers:\n  - name: scale_size_identity",
})
def handle_size_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_size_identity(**spec)


@register_plot_component("scale_shape_identity", ui_schema={
    "label": "Shape identity (use raw values as shapes)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "shape", "identity", "raw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_shape_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal shape codes from a data column as shapes; the column must contain integer shape codes valid in plotnine.",
    "yaml_example": "layers:\n  - name: scale_shape_identity",
})
def handle_shape_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_shape_identity(**spec)


@register_plot_component("scale_alpha_identity", ui_schema={
    "label": "Alpha identity (use raw values as opacity)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "alpha", "identity", "raw", "opacity"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_alpha_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal numeric values from a data column as alpha (transparency); values must be in [0, 1].",
    "yaml_example": "layers:\n  - name: scale_alpha_identity",
})
def handle_alpha_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_alpha_identity(**spec)


@register_plot_component("scale_linetype_identity", ui_schema={
    "label": "Linetype identity (use raw values as linetypes)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "linetype", "identity", "raw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_linetype_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal linetype strings from a data column; the column must contain valid plotnine linetype names ('solid', 'dashed', etc.).",
    "yaml_example": "layers:\n  - name: scale_linetype_identity",
})
def handle_linetype_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_linetype_identity(**spec)


@register_plot_component("scale_stroke_identity", ui_schema={
    "label": "Stroke identity (use raw values as stroke width)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "stroke", "identity", "raw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_stroke_identity"]}],
    "allow_extra_params": False,
    "params": _SCALE_IDENTITY_PARAMS,
    "description": "Use literal numeric stroke widths from a data column; bypasses range mapping.",
    "yaml_example": "layers:\n  - name: scale_stroke_identity",
})
def handle_stroke_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_stroke_identity(**spec)


# ── DECO-2: generic aesthetic scales ─────────────────────────────────────────

def _coerce_tuple_kwargs(spec: Dict[str, Any], keys=("h", "c", "l", "range")) -> Dict[str, Any]:
    """YAML naturally produces lists; plotnine/mizani's hue/lightness palettes
    do ``h[1] - h[0]`` which fails on Python lists (only works on tuples or
    numpy arrays). Convert known tuple-expecting kwargs from list → tuple so
    manifest authors can write the natural YAML form ``h: [0, 360]`` without
    crashing at draw time."""
    out = dict(spec)
    for k in keys:
        v = out.get(k)
        if isinstance(v, list) and len(v) == 2:
            out[k] = tuple(v)
    return out


@register_plot_component("scale_alpha", ui_schema={
    "label": "Alpha scale (generic)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "alpha", "opacity", "generic"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_alpha"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Opacity range as [min, max] (0–1)", "required": False, "default": "[0.1, 1]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Shorthand continuous alpha scale; equivalent to scale_alpha_continuous \u2014 maps a numeric variable to transparency.",
    "yaml_example": "layers:\n  - name: scale_alpha\n    params:\n      range: [0.3, 1.0]",
})
def handle_alpha(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_alpha(**_coerce_tuple_kwargs(spec))


@register_plot_component("scale_alpha_manual", ui_schema={
    "label": "Alpha manual (explicit opacity mapping)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "alpha", "opacity", "manual", "explicit"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_alpha_manual"]}],
    "allow_extra_params": True,
    "params": {
        "values": {"widget": "string", "label": "Per-category opacity dict or list", "required": True},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to manually specified alpha values; use when each category must have a specific opacity.",
    "yaml_example": "layers:\n  - name: scale_alpha_manual\n    params:\n      values: [0.3, 0.6, 1.0]",
})
def handle_alpha_manual(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_alpha_manual(**spec)


@register_plot_component("scale_size", ui_schema={
    "label": "Size scale (generic)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "size", "generic", "bubble"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_size"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "range": {"widget": "string", "label": "Output size range as [min, max] (pt)", "required": False, "default": "[1, 6]"},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Shorthand continuous size scale; equivalent to scale_size_continuous \u2014 maps a numeric variable to point size.",
    "yaml_example": "layers:\n  - name: scale_size\n    params:\n      range: [1, 8]",
})
def handle_size(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_size(**_coerce_tuple_kwargs(spec))


@register_plot_component("scale_size_manual", ui_schema={
    "label": "Size manual (explicit size mapping)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "size", "manual", "explicit"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_size_manual"]}],
    "allow_extra_params": True,
    "params": {
        "values": {"widget": "string", "label": "Per-category size dict or list (pt)", "required": True},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to manually specified point sizes; use when each category must have a specific size.",
    "yaml_example": "layers:\n  - name: scale_size_manual\n    params:\n      values: [2, 4, 8]",
})
def handle_size_manual(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_size_manual(**spec)


@register_plot_component("scale_size_area", ui_schema={
    "label": "Size area (area-proportional bubble sizes)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "size", "area", "bubble", "proportional"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_size_area"]}],
    "allow_extra_params": True,
    "params": {
        "max_size": {"widget": "number", "label": "Maximum bubble size (pt)", "required": False, "default": 6},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a continuous variable to point area (not radius); use for bubble charts where area proportional to value is the perceptually correct encoding.",
    "yaml_example": "layers:\n  - name: scale_size_area\n    params:\n      max_size: 10",
})
def handle_size_area(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_size_area(**_coerce_tuple_kwargs(spec))


@register_plot_component("scale_shape", ui_schema={
    "label": "Shape scale (generic categorical)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "shape", "generic", "categorical", "point"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_shape"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Shorthand discrete shape scale; equivalent to scale_shape_discrete.",
    "yaml_example": "layers:\n  - name: scale_shape",
})
def handle_shape(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_shape(**spec)


@register_plot_component("scale_shape_manual", ui_schema={
    "label": "Shape manual (explicit shape mapping)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "shape", "manual", "explicit", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_shape_manual"]}],
    "allow_extra_params": True,
    "params": {
        "values": {"widget": "string", "label": "Per-category shape dict or list (int or str)", "required": True},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to manually specified point shapes; use when specific shapes must be assigned to named categories.",
    "yaml_example": "layers:\n  - name: scale_shape_manual\n    params:\n      values: [16, 17, 15]",
})
def handle_shape_manual(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_shape_manual(**spec)


@register_plot_component("scale_linetype", ui_schema={
    "label": "Linetype scale (generic)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "linetype", "generic", "line"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_linetype"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Shorthand discrete linetype scale; equivalent to scale_linetype_discrete.",
    "yaml_example": "layers:\n  - name: scale_linetype",
})
def handle_linetype(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_linetype(**spec)


@register_plot_component("scale_linetype_manual", ui_schema={
    "label": "Linetype manual (explicit mapping)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "linetype", "manual", "explicit"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_linetype_manual"]}],
    "allow_extra_params": True,
    "params": {
        "values": {"widget": "string", "label": "Per-category linetype dict or list", "required": True},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Map a discrete variable to manually specified line types; use when specific dash patterns must be assigned to named line groups.",
    "yaml_example": "layers:\n  - name: scale_linetype_manual\n    params:\n      values: [solid, dashed, dotted]",
})
def handle_linetype_manual(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_linetype_manual(**spec)


@register_plot_component("scale_color_hue", ui_schema={
    "label": "Color hue (default discrete colour)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "hue", "discrete", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_hue"]}],
    "allow_extra_params": True,
    "params": {
        "h": {"widget": "string", "label": "Hue range [start, end] (0–360)", "required": False, "default": "[0, 360]"},
        "c": {"widget": "number", "label": "Chroma (saturation)", "required": False, "default": 100},
        "l": {"widget": "number", "label": "Lightness (0–100)", "required": False, "default": 65},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Evenly-spaced hues from the HCL colour wheel for discrete colour; the plotnine default discrete colour scale \u2014 use scale_color_viridis_d for accessibility.",
    "yaml_example": "layers:\n  - name: scale_color_hue\n    params:\n      h: [0, 360]",
})
def handle_color_hue(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_hue(**_coerce_tuple_kwargs(spec))


@register_plot_component("scale_fill_hue", ui_schema={
    "label": "Fill hue (default discrete fill)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "hue", "discrete", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_hue"]}],
    "allow_extra_params": True,
    "params": {
        "h": {"widget": "string", "label": "Hue range [start, end] (0–360)", "required": False, "default": "[0, 360]"},
        "c": {"widget": "number", "label": "Chroma (saturation)", "required": False, "default": 100},
        "l": {"widget": "number", "label": "Lightness (0–100)", "required": False, "default": 65},
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False, "options": ["legend", "none"]},
    },
    "description": "Evenly-spaced hues for discrete fill; the plotnine default \u2014 use scale_fill_viridis_d instead when accessibility matters.",
    "yaml_example": "layers:\n  - name: scale_fill_hue",
})
def handle_fill_hue(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_hue(**_coerce_tuple_kwargs(spec))


@register_plot_component("scale_color_continuous", ui_schema={
    "label": "Color continuous (default continuous colour)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "color", "continuous", "generic"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_color_continuous"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False,
                  "options": ["legend", "colorbar", "none"]},
    },
    "description": "Generic continuous colour scale dispatcher; delegates to the default continuous scale \u2014 rarely needed directly unless resetting a previously set scale.",
    "yaml_example": "layers:\n  - name: scale_color_continuous",
})
def handle_color_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_color_continuous(**spec)


@register_plot_component("scale_fill_continuous", ui_schema={
    "label": "Fill continuous (default continuous fill)",
    "category": "scale",
    "context": ["plot"],
    "tags": ["scale", "fill", "continuous", "generic"],
    "wraps": [{"lib": "plotnine", "attr_path": ["scale_fill_continuous"]}],
    "allow_extra_params": True,
    "params": {
        "name": {"widget": "string", "label": "Legend title", "required": False},
        "guide": {"widget": "enum", "label": "Guide type", "required": False,
                  "options": ["legend", "colorbar", "none"]},
    },
    "description": "Generic continuous fill scale dispatcher; use to reset fill to plotnine defaults after a manual or palette scale was applied upstream.",
    "yaml_example": "layers:\n  - name: scale_fill_continuous",
})
def handle_fill_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_continuous(**spec)
