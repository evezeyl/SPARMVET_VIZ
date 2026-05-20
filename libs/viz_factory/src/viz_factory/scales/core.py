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
})
def handle_fill_continuous(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + scale_fill_continuous(**spec)
