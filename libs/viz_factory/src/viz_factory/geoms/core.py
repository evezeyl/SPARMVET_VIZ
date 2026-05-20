from typing import Dict, Any

# @deps
# provides: component:geom_boxplot, component:geom_violin, component:geom_point, component:geom_line, component:geom_bar, component:geom_col, component:geom_histogram, component:geom_smooth, component:geom_density, component:geom_errorbar, component:geom_pointrange, component:geom_tile, component:geom_raster, component:geom_text, component:geom_label, component:geom_jitter, component:geom_step, component:geom_segment, component:geom_abline, component:geom_area, component:geom_bin_2d, component:geom_blank, component:geom_count, component:geom_crossbar, component:geom_density_2d, component:geom_dotplot, component:geom_errorbarh, component:geom_freqpoly, component:geom_hline, component:geom_linerange, component:geom_path, component:geom_vline, component:stat_count, component:stat_bin, component:stat_summary, component:stat_boxplot, component:stat_smooth, component:stat_density, component:labs (geom)
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry), libs/blueprint_arch/src/blueprint_arch/schema_registry.py (ui_schema via COMPONENT_SCHEMAS)
# doc: .claude/rules/rules_viz_factory.md, .claude/knowledge/architecture_decisions.md (ADR-075)
# @end_deps

from plotnine import (
    geom_point, geom_line, geom_bar, geom_col, geom_boxplot, geom_violin,
    geom_histogram, geom_smooth, geom_density, geom_errorbar, geom_pointrange,
    geom_tile, geom_raster, geom_text, geom_label, geom_jitter, geom_step,
    geom_segment, geom_abline, geom_area, geom_bin_2d, geom_blank, geom_count,
    geom_crossbar, geom_density_2d, geom_dotplot, geom_errorbarh, geom_freqpoly,
    geom_hline, geom_linerange, geom_map, geom_path, geom_pointdensity,
    geom_polygon, geom_qq, geom_qq_line, geom_quantile, geom_rect, geom_ribbon,
    geom_rug, geom_sina, geom_spoke, geom_vline,
    stat_count, stat_bin, stat_summary, stat_boxplot, stat_ydensity,
    stat_smooth, stat_density, stat_qq, stat_ecdf, stat_unique, stat_function,
    stat_bin_2d, stat_bindot, stat_density_2d, stat_ellipse, stat_hull,
    stat_qq_line, stat_quantile, stat_sina, stat_sum, stat_summary_bin,
    ggplot, labs
)
from viz_factory.registry import register_plot_component

# Shared param dicts — reduce repetition across similar geom/stat components.

_GEOM_LINE_PARAMS = {
    "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
    "colour": {"widget": "color", "label": "Colour (fixed, not mapped)", "required": False},
    "size": {"widget": "number", "label": "Line width", "required": False},
    "linetype": {"widget": "enum", "label": "Line type", "required": False,
                 "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
}

_GEOM_FILL_PARAMS = {
    "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
    "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)", "required": False},
    "colour": {"widget": "color", "label": "Border colour", "required": False},
    "size": {"widget": "number", "label": "Border line width", "required": False},
    "linetype": {"widget": "enum", "label": "Border line type", "required": False,
                 "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
}

_GEOM_REFLINE_PARAMS = {
    "colour": {"widget": "color", "label": "Line colour", "required": False},
    "size": {"widget": "number", "label": "Line width", "required": False, "default": 0.5},
    "linetype": {"widget": "enum", "label": "Line type", "required": False, "default": "dashed",
                 "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
}

_STAT_SMOOTH_PARAMS = {
    "method": {"widget": "enum", "label": "Smoothing method", "required": False, "default": "auto",
               "options": ["auto", "lm", "loess", "rlm", "glm", "gam"]},
    "se": {"widget": "bool", "label": "Show confidence interval", "required": False, "default": True},
    "level": {"widget": "number", "label": "Confidence level (0–1)", "required": False, "default": 0.95},
    "n": {"widget": "number", "label": "Number of interpolation points", "required": False, "default": 80},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
}

_STAT_DENSITY_PARAMS = {
    "adjust": {"widget": "number", "label": "Bandwidth adjustment multiplier", "required": False, "default": 1.0},
    "kernel": {"widget": "enum", "label": "Kernel type", "required": False, "default": "gaussian",
               "options": ["gaussian", "epanechnikov", "rectangular", "triangular", "biweight",
                           "cosine", "optcosine"]},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
}


@register_plot_component("geom_boxplot", ui_schema={
    "label": "Box plot",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["distribution", "boxplot", "outliers", "quartiles", "summary"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_boxplot"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)", "required": False},
        "colour": {"widget": "color", "label": "Border/outlier colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "width": {"widget": "number", "label": "Box width (0–1)", "required": False},
        "notch": {"widget": "bool", "label": "Show notch (confidence interval)", "required": False, "default": False},
        "outlier_colour": {"widget": "color", "label": "Outlier point colour", "required": False},
        "outlier_shape": {"widget": "number", "label": "Outlier point shape code", "required": False},
        "outlier_size": {"widget": "number", "label": "Outlier point size", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "dodge2", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "stat": {"widget": "string", "label": "Statistical transformation", "required": False, "default": "boxplot"},
    },
})
def handle_boxplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Boxplot component wrapper."""
    return p + geom_boxplot(**spec)


@register_plot_component("geom_violin", ui_schema={
    "label": "Violin plot",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["distribution", "violin", "density", "quartiles", "comparison"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_violin"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
        "width": {"widget": "number", "label": "Max violin width (data units)", "required": False},
        "scale": {"widget": "enum", "label": "Scale violins to", "required": False, "default": "area",
                  "options": ["area", "count", "width"]},
        "trim": {"widget": "bool", "label": "Trim tails to data range", "required": False, "default": True},
        "draw_quantiles": {"widget": "string", "label": "Quantile lines to draw (e.g. [0.25,0.5,0.75])",
                           "required": False},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "dodge", "options": ["identity", "dodge", "dodge2"]},
    },
})
def handle_violin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Violin (Density) component wrapper."""
    return p + geom_violin(**spec)


@register_plot_component("geom_point", ui_schema={
    "label": "Scatter points",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["scatter", "points", "correlation", "relationship", "bivariate"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_point"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)", "required": False},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)", "required": False},
        "size": {"widget": "number", "label": "Point size", "required": False, "default": 1.5},
        "shape": {"widget": "number", "label": "Shape code (0–25)", "required": False, "default": 16},
        "stroke": {"widget": "number", "label": "Border stroke width", "required": False},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "jitter", "jitterdodge", "dodge"]},
        "stat": {"widget": "string", "label": "Statistical transformation", "required": False, "default": "identity"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_point(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Point (Scatter) component wrapper."""
    return p + geom_point(**spec)


@register_plot_component("geom_line", ui_schema={
    "label": "Line",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["line", "trend", "time-series", "connected", "evolution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_line"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False, "default": 0.5},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "default": "solid", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "lineend": {"widget": "enum", "label": "Line end style", "required": False,
                    "options": ["butt", "round", "square"]},
        "linejoin": {"widget": "enum", "label": "Line join style", "required": False,
                     "options": ["round", "mitre", "bevel"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "dodge", "jitter"]},
        "stat": {"widget": "string", "label": "Statistical transformation", "required": False, "default": "identity"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Line (Connected points) component wrapper."""
    return p + geom_line(**spec)


@register_plot_component("geom_bar", ui_schema={
    "label": "Bar",
    "category": "comparison",
    "context": ["plot"],
    "tags": ["bar", "count", "frequency", "categorical", "comparison", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_bar"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)", "required": False},
        "colour": {"widget": "color", "label": "Border colour", "required": False},
        "size": {"widget": "number", "label": "Border line width", "required": False},
        "linetype": {"widget": "enum", "label": "Border line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "blank"]},
        "width": {"widget": "number", "label": "Bar width (0–1)", "required": False},
        "stat": {"widget": "enum", "label": "Statistical transformation", "required": False, "default": "count",
                 "options": ["count", "identity", "bin", "density"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "stack", "options": ["stack", "dodge", "fill", "identity", "dodge2"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_bar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Bar (count) component wrapper."""
    return p + geom_bar(**spec)


@register_plot_component("geom_col", ui_schema={
    "label": "Column (identity bar)",
    "category": "comparison",
    "context": ["plot"],
    "tags": ["bar", "column", "identity", "value", "comparison"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_col"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
        "width": {"widget": "number", "label": "Bar width (0–1)", "required": False},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "stack", "options": ["stack", "dodge", "fill", "identity", "dodge2"]},
    },
})
def handle_col(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Column (identity) component wrapper."""
    return p + geom_col(**spec)


@register_plot_component("geom_histogram", ui_schema={
    "label": "Histogram",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["histogram", "distribution", "frequency", "numeric", "univariate"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_histogram"]}],
    "allow_extra_params": True,
    "params": {
        "bins": {"widget": "number", "label": "Number of bins", "required": False, "default": 30},
        "binwidth": {"widget": "number", "label": "Bin width (data units; overrides bins)", "required": False},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)", "required": False},
        "colour": {"widget": "color", "label": "Border colour", "required": False},
        "size": {"widget": "number", "label": "Border line width", "required": False},
        "linetype": {"widget": "enum", "label": "Border line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "blank"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "stack", "options": ["stack", "dodge", "fill", "identity"]},
        "stat": {"widget": "enum", "label": "Statistical transformation", "required": False, "default": "bin",
                 "options": ["bin", "count", "density", "identity"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_histogram(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Histogram component wrapper."""
    return p + geom_histogram(**spec)


@register_plot_component("geom_smooth", ui_schema={
    "label": "Smoothed line (trend)",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["smooth", "trend", "regression", "loess", "lm", "confidence"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_smooth"]}],
    "allow_extra_params": True,
    "params": {
        **_STAT_SMOOTH_PARAMS,
        "alpha": {"widget": "number", "label": "CI ribbon opacity", "required": False, "default": 0.2},
        "colour": {"widget": "color", "label": "Line colour", "required": False},
        "fill": {"widget": "color", "label": "CI ribbon fill colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False, "default": 1.0},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    },
})
def handle_smooth(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Smooth (Regression) component wrapper."""
    return p + geom_smooth(**spec)


@register_plot_component("geom_density", ui_schema={
    "label": "Density curve",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["density", "distribution", "kde", "smooth", "univariate"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_density"]}],
    "allow_extra_params": True,
    "params": {
        **_STAT_DENSITY_PARAMS,
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour under curve", "required": False},
        "colour": {"widget": "color", "label": "Line colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "stack", "fill"]},
    },
})
def handle_density(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Density component wrapper."""
    return p + geom_density(**spec)


@register_plot_component("geom_errorbar", ui_schema={
    "label": "Error bars",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["errorbar", "uncertainty", "confidence", "range", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_errorbar"]}],
    "allow_extra_params": True,
    "params": {
        "width": {"widget": "number", "label": "Whisker width (data units)", "required": False, "default": 0.5},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_errorbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Errorbar component wrapper."""
    return p + geom_errorbar(**spec)


@register_plot_component("geom_pointrange", ui_schema={
    "label": "Point + range",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["pointrange", "uncertainty", "confidence", "range", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_pointrange"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)", "required": False},
        "size": {"widget": "number", "label": "Line width / point size", "required": False},
        "shape": {"widget": "number", "label": "Point shape code (0–25)", "required": False, "default": 16},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "fatten": {"widget": "number", "label": "Point size relative to line (multiplier)", "required": False,
                   "default": 4},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_pointrange(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Pointrange component wrapper."""
    return p + geom_pointrange(**spec)


@register_plot_component("geom_tile", ui_schema={
    "label": "Heatmap tiles",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["heatmap", "tile", "matrix", "fill", "correlation", "bivariate"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_tile"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour (fixed override, not mapped)", "required": False},
        "colour": {"widget": "color", "label": "Tile border colour", "required": False},
        "size": {"widget": "number", "label": "Border line width", "required": False},
        "linetype": {"widget": "enum", "label": "Border line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "blank"]},
        "width": {"widget": "number", "label": "Tile width (data units; default = resolution)", "required": False},
        "height": {"widget": "number", "label": "Tile height (data units; default = resolution)", "required": False},
        "stat": {"widget": "string", "label": "Statistical transformation", "required": False, "default": "identity"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_tile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Tile (Heatmap) component wrapper."""
    return p + geom_tile(**spec)


@register_plot_component("geom_raster", ui_schema={
    "label": "Raster (fast heatmap)",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["raster", "heatmap", "fill", "fast", "grid", "matrix"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_raster"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour (fixed override, not mapped)", "required": False},
        "hjust": {"widget": "number", "label": "Horizontal justification (0=left, 0.5=center, 1=right)",
                  "required": False, "default": 0.5},
        "vjust": {"widget": "number", "label": "Vertical justification (0=bottom, 0.5=center, 1=top)",
                  "required": False, "default": 0.5},
        "interpolate": {"widget": "bool", "label": "Bilinear interpolation (smooth pixel edges)",
                        "required": False, "default": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_raster(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Raster (Heatmap) component wrapper."""
    return p + geom_raster(**spec)


@register_plot_component("geom_text", ui_schema={
    "label": "Text labels",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["text", "label", "annotation", "direct-label", "value"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_text"]}],
    "allow_extra_params": True,
    "params": {
        "colour": {"widget": "color", "label": "Text colour", "required": False},
        "size": {"widget": "number", "label": "Font size (pt)", "required": False, "default": 11},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "family": {"widget": "string", "label": "Font family", "required": False},
        "fontface": {"widget": "enum", "label": "Font face", "required": False,
                     "options": ["plain", "bold", "italic", "bold.italic"]},
        "hjust": {"widget": "number", "label": "Horizontal justification (0=left, 0.5=center, 1=right)",
                  "required": False, "default": 0.5},
        "vjust": {"widget": "number", "label": "Vertical justification (0=bottom, 0.5=center, 1=top)",
                  "required": False, "default": 0.5},
        "angle": {"widget": "number", "label": "Text angle (degrees)", "required": False, "default": 0},
        "lineheight": {"widget": "number", "label": "Line height multiplier", "required": False, "default": 1.2},
        "nudge_x": {"widget": "number", "label": "Horizontal nudge (data units)", "required": False, "default": 0},
        "nudge_y": {"widget": "number", "label": "Vertical nudge (data units)", "required": False, "default": 0},
        "check_overlap": {"widget": "bool", "label": "Skip overlapping labels", "required": False, "default": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_text(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Text (Annotation) component wrapper."""
    return p + geom_text(**spec)


@register_plot_component("geom_label", ui_schema={
    "label": "Labels (text with background box)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["label", "text", "annotation", "background", "box", "callout"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_label"]}],
    "allow_extra_params": True,
    "params": {
        "colour": {"widget": "color", "label": "Text colour", "required": False},
        "fill": {"widget": "color", "label": "Label background fill", "required": False, "default": "white"},
        "size": {"widget": "number", "label": "Font size (pt)", "required": False, "default": 11},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "family": {"widget": "string", "label": "Font family", "required": False},
        "fontface": {"widget": "enum", "label": "Font face", "required": False,
                     "options": ["plain", "bold", "italic", "bold.italic"]},
        "hjust": {"widget": "number", "label": "Horizontal justification", "required": False, "default": 0.5},
        "vjust": {"widget": "number", "label": "Vertical justification", "required": False, "default": 0.5},
        "angle": {"widget": "number", "label": "Text angle (degrees)", "required": False, "default": 0},
        "nudge_x": {"widget": "number", "label": "Horizontal nudge (data units)", "required": False, "default": 0},
        "nudge_y": {"widget": "number", "label": "Vertical nudge (data units)", "required": False, "default": 0},
        "label_padding": {"widget": "number", "label": "Padding around text (pt)", "required": False},
        "label_r": {"widget": "number", "label": "Corner radius (pt)", "required": False},
        "label_size": {"widget": "number", "label": "Border line width (pt)", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_label(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Label (Annotation) component wrapper."""
    return p + geom_label(**spec)


@register_plot_component("geom_jitter", ui_schema={
    "label": "Jittered points",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["jitter", "scatter", "overplot", "spread", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_jitter"]}],
    "allow_extra_params": True,
    "params": {
        "width": {"widget": "number", "label": "Horizontal jitter amount", "required": False, "default": 0.4},
        "height": {"widget": "number", "label": "Vertical jitter amount", "required": False, "default": 0.4},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)", "required": False},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)", "required": False},
        "size": {"widget": "number", "label": "Point size", "required": False, "default": 1.5},
        "shape": {"widget": "number", "label": "Shape code (0–25)", "required": False, "default": 16},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_jitter(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Jitter component wrapper."""
    return p + geom_jitter(**spec)


@register_plot_component("geom_step", ui_schema={
    "label": "Step line",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["step", "staircase", "ecdf", "cumulative", "evolution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_step"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_LINE_PARAMS,
        "direction": {"widget": "enum", "label": "Step direction", "required": False, "default": "hv",
                      "options": ["hv", "vh", "mid"]},
    },
})
def handle_step(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Step plot component wrapper (useful for ECDF and staircases)."""
    return p + geom_step(**spec)


@register_plot_component("geom_segment", ui_schema={
    "label": "Line segments",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["segment", "arrow", "lollipop", "annotation", "range"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_segment"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_LINE_PARAMS,
        "arrow": {"widget": "string", "label": "Arrow spec (e.g. arrow(length=unit(0.1,'cm')))",
                  "required": False},
        "lineend": {"widget": "enum", "label": "Line end style", "required": False,
                    "options": ["butt", "round", "square"]},
    },
})
def handle_segment(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Segment component wrapper (useful for Lollipop charts)."""
    return p + geom_segment(**spec)


@register_plot_component("geom_abline", ui_schema={
    "label": "Diagonal reference line",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["abline", "reference", "slope", "intercept", "diagonal", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_abline"]}],
    "allow_extra_params": True,
    "params": {
        "slope": {"widget": "number", "label": "Slope", "required": False, "default": 1},
        "intercept": {"widget": "number", "label": "Y-intercept", "required": False, "default": 0},
        **_GEOM_REFLINE_PARAMS,
    },
})
def handle_abline(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Reference line with given slope and intercept."""
    return p + geom_abline(**spec)


@register_plot_component("geom_area", ui_schema={
    "label": "Filled area",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["area", "fill", "stacked", "cumulative", "evolution", "proportion"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_area"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "stack", "options": ["stack", "fill", "identity"]},
        "stat": {"widget": "string", "label": "Statistical transformation", "required": False,
                 "default": "identity"},
    },
})
def handle_area(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Filled area plot."""
    return p + geom_area(**spec)


@register_plot_component("geom_bin_2d", ui_schema={
    "label": "2D bin heatmap",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["bin2d", "heatmap", "density", "2d", "count", "correlation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_bin_2d"]}],
    "allow_extra_params": True,
    "params": {
        "bins": {"widget": "number", "label": "Number of bins in each direction", "required": False, "default": 30},
        "binwidth": {"widget": "string", "label": "Bin widths [x, y] (e.g. [1,1])", "required": False},
        **_GEOM_FILL_PARAMS,
    },
})
def handle_bin_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Add a heatmap of 2d bin counts."""
    return p + geom_bin_2d(**spec)


@register_plot_component("geom_blank", ui_schema={
    "label": "Blank (expand limits only)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["blank", "utility", "limits", "expand"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_blank"]}],
    "allow_extra_params": False,
    "params": {},
})
def handle_blank(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Draw nothing (useful for expanding limits)."""
    return p + geom_blank(**spec)


@register_plot_component("geom_count", ui_schema={
    "label": "Count-sized scatter",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["count", "scatter", "overplot", "size", "frequency"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_count"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)", "required": False},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)", "required": False},
        "shape": {"widget": "number", "label": "Shape code (0–25)", "required": False, "default": 19},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_count(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Count number of point at location."""
    return p + geom_count(**spec)


@register_plot_component("geom_crossbar", ui_schema={
    "label": "Crossbar (hollow bar with median)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["crossbar", "summary", "uncertainty", "median", "range"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_crossbar"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
        "fatten": {"widget": "number", "label": "Median line thickness multiplier", "required": False, "default": 2.5},
        "width": {"widget": "number", "label": "Bar width (data units)", "required": False, "default": 0.5},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "dodge", "dodge2"]},
    },
})
def handle_crossbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Hollow bar with median line."""
    return p + geom_crossbar(**spec)


@register_plot_component("geom_density_2d", ui_schema={
    "label": "2D density contours",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["density2d", "contour", "bivariate", "kde", "heatmap"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_density_2d"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_LINE_PARAMS,
        "contour_var": {"widget": "enum", "label": "Variable to contour", "required": False, "default": "density",
                        "options": ["density", "ndensity", "count"]},
    },
})
def handle_density_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Contours of a 2d density estimate."""
    return p + geom_density_2d(**spec)


@register_plot_component("geom_dotplot", ui_schema={
    "label": "Dot plot",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["dotplot", "distribution", "count", "frequency", "univariate"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_dotplot"]}],
    "allow_extra_params": True,
    "params": {
        "binwidth": {"widget": "number", "label": "Bin width (data units)", "required": False},
        "bins": {"widget": "number", "label": "Number of bins", "required": False},
        "method": {"widget": "enum", "label": "Binning method", "required": False, "default": "dotdensity",
                   "options": ["dotdensity", "histodot"]},
        "stackdir": {"widget": "enum", "label": "Stack direction", "required": False, "default": "up",
                     "options": ["up", "down", "center", "centerwhole"]},
        "binaxis": {"widget": "enum", "label": "Bin axis", "required": False, "default": "x",
                    "options": ["x", "y"]},
        "dotsize": {"widget": "number", "label": "Dot size (relative to binwidth)", "required": False,
                    "default": 1},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "fill": {"widget": "color", "label": "Fill colour", "required": False},
        "colour": {"widget": "color", "label": "Border colour", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_dotplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Dot plot."""
    return p + geom_dotplot(**spec)


@register_plot_component("geom_errorbarh", ui_schema={
    "label": "Horizontal error bars",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["errorbarh", "horizontal", "uncertainty", "confidence", "range"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_errorbarh"]}],
    "allow_extra_params": True,
    "params": {
        "height": {"widget": "number", "label": "Whisker height (data units)", "required": False, "default": 0.5},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_errorbarh(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Horizontal error bars."""
    return p + geom_errorbarh(**spec)


@register_plot_component("geom_freqpoly", ui_schema={
    "label": "Frequency polygon",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["freqpoly", "frequency", "histogram", "line", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_freqpoly"]}],
    "allow_extra_params": True,
    "params": {
        "bins": {"widget": "number", "label": "Number of bins", "required": False, "default": 30},
        "binwidth": {"widget": "number", "label": "Bin width (data units; overrides bins)", "required": False},
        **_GEOM_LINE_PARAMS,
    },
})
def handle_freqpoly(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Frequency polygon."""
    return p + geom_freqpoly(**spec)


@register_plot_component("geom_hline", ui_schema={
    "label": "Horizontal reference line",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["hline", "reference", "horizontal", "threshold", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_hline"]}],
    "allow_extra_params": True,
    "params": {
        "yintercept": {"widget": "number", "label": "Y-intercept (Y value of the line)", "required": False,
                       "default": 0},
        **_GEOM_REFLINE_PARAMS,
    },
})
def handle_hline(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Horizontal line."""
    return p + geom_hline(**spec)


@register_plot_component("geom_linerange", ui_schema={
    "label": "Vertical line segment (range)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["linerange", "range", "uncertainty", "vertical", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_linerange"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_linerange(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Vertical line segment."""
    return p + geom_linerange(**spec)


# @register_plot_component("geom_map")
# def handle_map(p: ggplot, spec: Dict[str, Any]) -> ggplot:
#     """Map polygons."""
#     return p + geom_map(**spec)


@register_plot_component("geom_path", ui_schema={
    "label": "Path (points in order of appearance)",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["path", "connected", "trajectory", "time", "order"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_path"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_LINE_PARAMS,
        "lineend": {"widget": "enum", "label": "Line end style", "required": False,
                    "options": ["butt", "round", "square"]},
        "linejoin": {"widget": "enum", "label": "Line join style", "required": False,
                     "options": ["round", "mitre", "bevel"]},
        "arrow": {"widget": "string", "label": "Arrow spec (e.g. arrow(length=unit(0.1,'cm')))",
                  "required": False},
    },
})
def handle_path(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Connected points in order of appearance."""
    return p + geom_path(**spec)


@register_plot_component("geom_pointdensity", ui_schema={
    "label": "Point density scatter",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["pointdensity", "density", "scatter", "overplot", "2d"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_pointdensity"]}],
    "allow_extra_params": True,
    "params": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "size": {"widget": "number", "label": "Point size", "required": False, "default": 1.5},
        "shape": {"widget": "number", "label": "Shape code (0–25)", "required": False, "default": 16},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_pointdensity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Cross between a scatter plot and a 2D density plot."""
    return p + geom_pointdensity(**spec)


@register_plot_component("geom_polygon", ui_schema={
    "label": "Filled polygons",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["polygon", "shape", "fill", "region", "spatial"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_polygon"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
    },
})
def handle_polygon(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Filled polygons."""
    return p + geom_polygon(**spec)


@register_plot_component("geom_qq", ui_schema={
    "label": "Quantile-quantile (QQ) plot",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["qq", "quantile", "normality", "distribution", "comparison"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_qq"]}],
    "allow_extra_params": True,
    "params": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm, t, exp)",
                         "required": False, "default": "norm"},
        "dparams": {"widget": "string", "label": "Distribution parameters (dict expression)", "required": False},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "size": {"widget": "number", "label": "Point size", "required": False, "default": 1.5},
        "shape": {"widget": "number", "label": "Shape code (0–25)", "required": False, "default": 16},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_geom_qq(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Lower-level Quantile-Quantile plot."""
    return p + geom_qq(**spec)


@register_plot_component("geom_qq_line", ui_schema={
    "label": "QQ reference line",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["qq", "reference", "normality", "line", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_qq_line"]}],
    "allow_extra_params": True,
    "params": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm, t)",
                         "required": False, "default": "norm"},
        "line_p": {"widget": "string", "label": "Quantile probabilities for line [lo, hi]",
                   "required": False, "default": "[0.25, 0.75]"},
        "fullrange": {"widget": "bool", "label": "Extend line to full plot range",
                      "required": False, "default": False},
        **_GEOM_REFLINE_PARAMS,
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_qq_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Reference line for a QQ plot."""
    return p + geom_qq_line(**spec)


@register_plot_component("geom_quantile", ui_schema={
    "label": "Quantile regression lines",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["quantile", "regression", "trend", "robust", "median"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_quantile"]}],
    "allow_extra_params": True,
    "params": {
        "quantiles": {"widget": "string", "label": "Quantile(s) to fit (e.g. [0.25,0.5,0.75])",
                      "required": False, "default": "[0.25, 0.5, 0.75]"},
        "method": {"widget": "string", "label": "Fitting method (rq)", "required": False, "default": "rq"},
        **_GEOM_LINE_PARAMS,
    },
})
def handle_quantile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Quantile regression."""
    return p + geom_quantile(**spec)


@register_plot_component("geom_rect", ui_schema={
    "label": "Rectangles",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["rect", "rectangle", "highlight", "region", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_rect"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
    },
})
def handle_rect(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """2D rectangles."""
    return p + geom_rect(**spec)


@register_plot_component("geom_ribbon", ui_schema={
    "label": "Ribbon (filled band between two lines)",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["ribbon", "band", "confidence", "range", "fill", "evolution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_ribbon"]}],
    "allow_extra_params": True,
    "params": {
        **_GEOM_FILL_PARAMS,
        "position": {"widget": "enum", "label": "Position adjustment", "required": False,
                     "default": "identity", "options": ["identity", "stack", "fill"]},
    },
})
def handle_ribbon(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Filled area between two lines."""
    return p + geom_ribbon(**spec)


@register_plot_component("geom_rug", ui_schema={
    "label": "Rug plot (marginal ticks)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["rug", "marginal", "ticks", "distribution", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_rug"]}],
    "allow_extra_params": True,
    "params": {
        "sides": {"widget": "enum", "label": "Sides to draw rug on", "required": False, "default": "bl",
                  "options": ["b", "l", "t", "r", "bl", "bt", "br", "lt", "lr", "tr", "blt", "blr", "btr",
                               "ltr", "bltr"]},
        "outside": {"widget": "bool", "label": "Draw ticks outside plot area", "required": False, "default": False},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Tick colour", "required": False},
        "size": {"widget": "number", "label": "Tick line width", "required": False},
        "length": {"widget": "string", "label": "Tick length (unit string, e.g. '0.03npc')", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_rug(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Marginal rug plots."""
    return p + geom_rug(**spec)


@register_plot_component("geom_sina", ui_schema={
    "label": "Sina plot (normalized violin + points)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["sina", "violin", "jitter", "points", "distribution", "comparison"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_sina"]}],
    "allow_extra_params": True,
    "params": {
        "scale": {"widget": "enum", "label": "Scale points to", "required": False, "default": "area",
                  "options": ["area", "count", "width"]},
        "method": {"widget": "enum", "label": "Density method", "required": False, "default": "density",
                   "options": ["density", "counts"]},
        "maxwidth": {"widget": "number", "label": "Maximum width of sina (0–1)", "required": False},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)", "required": False},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)", "required": False},
        "size": {"widget": "number", "label": "Point size", "required": False, "default": 1.5},
        "shape": {"widget": "number", "label": "Shape code (0–25)", "required": False, "default": 16},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_sina(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Sina plot (normalized violin)."""
    return p + geom_sina(**spec)


@register_plot_component("geom_spoke", ui_schema={
    "label": "Spoke (angle + radius segments)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["spoke", "arrow", "angle", "direction", "vector"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_spoke"]}],
    "allow_extra_params": True,
    "params": {
        "radius": {"widget": "number", "label": "Spoke radius (overrides mapped radius)", "required": False},
        "arrow": {"widget": "bool", "label": "Draw arrowheads", "required": False, "default": False},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False, "default": 1.0},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_spoke(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Line segment with given angle and radius."""
    return p + geom_spoke(**spec)


@register_plot_component("geom_vline", ui_schema={
    "label": "Vertical reference line",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["vline", "reference", "vertical", "threshold", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_vline"]}],
    "allow_extra_params": True,
    "params": {
        "xintercept": {"widget": "number", "label": "X-intercept (X value of the line)", "required": False,
                       "default": 0},
        **_GEOM_REFLINE_PARAMS,
    },
})
def handle_vline(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Vertical line."""
    return p + geom_vline(**spec)


# --- Statistical Components ---


@register_plot_component("stat_count", ui_schema={
    "label": "Stat: count observations",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "count", "frequency", "bar", "categorical"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_count"]}],
    "allow_extra_params": True,
    "params": {
        "width": {"widget": "number", "label": "Bar width (0–1)", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_count(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_count(**spec)


@register_plot_component("stat_bin", ui_schema={
    "label": "Stat: bin observations",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "bin", "histogram", "frequency", "numeric"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_bin"]}],
    "allow_extra_params": True,
    "params": {
        "bins": {"widget": "number", "label": "Number of bins", "required": False, "default": 30},
        "binwidth": {"widget": "number", "label": "Bin width (data units; overrides bins)", "required": False},
        "boundary": {"widget": "number", "label": "Bin boundary alignment value", "required": False},
        "center": {"widget": "number", "label": "Bin center alignment value", "required": False},
        "closed": {"widget": "enum", "label": "Bin interval closure", "required": False, "default": "right",
                   "options": ["right", "left"]},
        "pad": {"widget": "bool", "label": "Add empty bins at each end", "required": False, "default": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_bin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bin(**spec)


@register_plot_component("stat_identity", ui_schema={
    "label": "Stat: identity (passthrough)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "identity", "passthrough", "utility"],
    "wraps": [],
    "allow_extra_params": False,
    "params": {},
})
def handle_stat_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    # Most geoms default to stat_identity already
    return p


@register_plot_component("stat_summary", ui_schema={
    "label": "Stat: summary (apply function per group)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "summary", "aggregate", "function", "group"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_summary"]}],
    "allow_extra_params": True,
    "params": {
        "fun_y": {"widget": "string", "label": "Function for y (e.g. 'mean', 'median')", "required": False},
        "fun_ymin": {"widget": "string", "label": "Function for ymin", "required": False},
        "fun_ymax": {"widget": "string", "label": "Function for ymax", "required": False},
        "fun_data": {"widget": "string", "label": "Function returning data frame", "required": False},
        "geom": {"widget": "string", "label": "Geom to render (e.g. point, errorbar, bar)",
                 "required": False, "default": "pointrange"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_summary(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_summary(**spec)


@register_plot_component("stat_boxplot", ui_schema={
    "label": "Stat: boxplot (compute box statistics)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "boxplot", "quartiles", "IQR", "outliers"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_boxplot"]}],
    "allow_extra_params": True,
    "params": {
        "coef": {"widget": "number", "label": "Whisker coefficient (IQR multiplier)", "required": False,
                 "default": 1.5},
        "geom": {"widget": "string", "label": "Geom to render", "required": False, "default": "boxplot"},
        "width": {"widget": "number", "label": "Box width (0–1)", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_boxplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_boxplot(**spec)


@register_plot_component("stat_ydensity", ui_schema={
    "label": "Stat: y-density (violin statistics)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "ydensity", "violin", "density", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_ydensity"]}],
    "allow_extra_params": True,
    "params": {
        "scale": {"widget": "enum", "label": "Scale violins to", "required": False, "default": "area",
                  "options": ["area", "count", "width"]},
        "trim": {"widget": "bool", "label": "Trim tails to data range", "required": False, "default": True},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_ydensity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ydensity(**spec)


@register_plot_component("stat_smooth", ui_schema={
    "label": "Stat: smooth (trend line)",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["stat", "smooth", "trend", "regression", "loess", "lm"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_smooth"]}],
    "allow_extra_params": True,
    "params": {**_STAT_SMOOTH_PARAMS},
})
def handle_stat_smooth(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_smooth(**spec)


@register_plot_component("stat_density", ui_schema={
    "label": "Stat: density (kernel density estimate)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "density", "kde", "distribution", "smooth"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_density"]}],
    "allow_extra_params": True,
    "params": {**_STAT_DENSITY_PARAMS},
})
def handle_stat_density(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_density(**spec)


@register_plot_component("stat_qq", ui_schema={
    "label": "Stat: quantile-quantile",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "qq", "quantile", "normality", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_qq"]}],
    "allow_extra_params": True,
    "params": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm)",
                         "required": False, "default": "norm"},
        "dparams": {"widget": "string", "label": "Distribution parameters (dict expression)", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_qq(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_qq(**spec)


@register_plot_component("stat_ecdf", ui_schema={
    "label": "Stat: empirical CDF",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "ecdf", "cdf", "cumulative", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_ecdf"]}],
    "allow_extra_params": True,
    "params": {
        "n": {"widget": "number", "label": "Number of interpolation points", "required": False, "default": None},
        "pad": {"widget": "bool", "label": "Pad to 0 and 1 at extremes", "required": False, "default": True},
        "geom": {"widget": "string", "label": "Geom to render", "required": False, "default": "step"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_ecdf(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ecdf(**spec)


@register_plot_component("stat_unique", ui_schema={
    "label": "Stat: unique (remove duplicates)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "unique", "deduplicate", "filter", "utility"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_unique"]}],
    "allow_extra_params": True,
    "params": {
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_unique(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_unique(**spec)


@register_plot_component("stat_function", ui_schema={
    "label": "Stat: function (plot a math function)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "function", "curve", "math", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_function"]}],
    "allow_extra_params": True,
    "params": {
        "fun": {"widget": "string", "label": "Function as Python expression (e.g. 'lambda x: x**2')",
                "required": True},
        "n": {"widget": "number", "label": "Number of evaluation points", "required": False, "default": 101},
        "xlim": {"widget": "string", "label": "X range for evaluation [min, max]", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_function(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Statistical function layer. 'fun' must be a callable; string lambdas are evaluated."""
    spec = dict(spec)
    fun = spec.get("fun")
    if isinstance(fun, str):
        try:
            # Safe for developer-controlled manifests only
            spec["fun"] = eval(fun)
        except Exception as e:
            print(
                f"Warning: stat_function could not evaluate 'fun' string: {e}")
            return p
    return p + stat_function(**spec)


@register_plot_component("stat_bin_2d", ui_schema={
    "label": "Stat: 2D binning",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "bin2d", "heatmap", "density", "2d", "count"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_bin_2d"]}],
    "allow_extra_params": True,
    "params": {
        "bins": {"widget": "string", "label": "Bins per axis [x, y] or single number", "required": False,
                 "default": "30"},
        "binwidth": {"widget": "string", "label": "Bin widths [x, y]", "required": False},
        "drop": {"widget": "bool", "label": "Drop bins with zero count", "required": False, "default": True},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_bin_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bin_2d(**spec)


@register_plot_component("stat_bindot", ui_schema={
    "label": "Stat: dot-plot binning",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "bindot", "dotplot", "frequency", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_bindot"]}],
    "allow_extra_params": True,
    "params": {
        "binwidth": {"widget": "number", "label": "Bin width (data units)", "required": False},
        "binaxis": {"widget": "enum", "label": "Bin axis", "required": False, "default": "x",
                    "options": ["x", "y"]},
        "method": {"widget": "enum", "label": "Binning method", "required": False, "default": "dotdensity",
                   "options": ["dotdensity", "histodot"]},
        "origin": {"widget": "number", "label": "Bin origin", "required": False},
        "right": {"widget": "bool", "label": "Right-closed intervals", "required": False, "default": True},
        "drop": {"widget": "bool", "label": "Drop empty bins", "required": False, "default": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_bindot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bindot(**spec)


@register_plot_component("stat_density_2d", ui_schema={
    "label": "Stat: 2D density estimate",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "density2d", "contour", "bivariate", "kde"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_density_2d"]}],
    "allow_extra_params": True,
    "params": {
        "contour": {"widget": "bool", "label": "Compute contours", "required": False, "default": True},
        "n": {"widget": "number", "label": "Grid points per axis for evaluation", "required": False, "default": 100},
        "h": {"widget": "string", "label": "Bandwidth [x, y]", "required": False},
        "adjust": {"widget": "number", "label": "Bandwidth adjustment multiplier", "required": False, "default": 1.0},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_density_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_density_2d(**spec)


@register_plot_component("stat_ellipse", ui_schema={
    "label": "Stat: confidence ellipse",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "ellipse", "confidence", "group", "cluster"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_ellipse"]}],
    "allow_extra_params": True,
    "params": {
        "type": {"widget": "enum", "label": "Ellipse type", "required": False, "default": "t",
                 "options": ["t", "norm", "euclid"]},
        "level": {"widget": "number", "label": "Confidence level (0–1)", "required": False, "default": 0.95},
        "segments": {"widget": "number", "label": "Number of ellipse segments", "required": False, "default": 51},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_ellipse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ellipse(**spec)


@register_plot_component("stat_hull", ui_schema={
    "label": "Stat: convex hull",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "hull", "convex", "polygon", "group", "cluster"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_hull"]}],
    "allow_extra_params": True,
    "params": {
        "geom": {"widget": "string", "label": "Geom to render hull with", "required": False, "default": "path"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_hull(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_hull(**spec)


@register_plot_component("stat_qq_line", ui_schema={
    "label": "Stat: QQ reference line",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "qq", "reference", "normality", "line"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_qq_line"]}],
    "allow_extra_params": True,
    "params": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm)",
                         "required": False, "default": "norm"},
        "dparams": {"widget": "string", "label": "Distribution parameters (dict expression)", "required": False},
        "line_p": {"widget": "string", "label": "Quantile probabilities for line [lo, hi]",
                   "required": False, "default": "[0.25, 0.75]"},
        "fullrange": {"widget": "bool", "label": "Extend line to full plot range",
                      "required": False, "default": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_qq_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_qq_line(**spec)


@register_plot_component("stat_quantile", ui_schema={
    "label": "Stat: quantile regression",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["stat", "quantile", "regression", "trend", "robust"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_quantile"]}],
    "allow_extra_params": True,
    "params": {
        "quantiles": {"widget": "string", "label": "Quantile(s) to fit (e.g. [0.25,0.5,0.75])",
                      "required": False, "default": "[0.25, 0.5, 0.75]"},
        "method": {"widget": "string", "label": "Fitting method", "required": False, "default": "rq"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_quantile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_quantile(**spec)


@register_plot_component("stat_sina", ui_schema={
    "label": "Stat: sina (density-normalized jitter)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "sina", "jitter", "violin", "density", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_sina"]}],
    "allow_extra_params": True,
    "params": {
        "scale": {"widget": "enum", "label": "Scale points to", "required": False, "default": "area",
                  "options": ["area", "count", "width"]},
        "method": {"widget": "enum", "label": "Density method", "required": False, "default": "density",
                   "options": ["density", "counts"]},
        "maxwidth": {"widget": "number", "label": "Maximum width (0–1)", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_sina(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_sina(**spec)


@register_plot_component("stat_sum", ui_schema={
    "label": "Stat: sum (count unique combinations)",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "sum", "count", "size", "overplot"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_sum"]}],
    "allow_extra_params": True,
    "params": {
        "geom": {"widget": "string", "label": "Geom to render", "required": False, "default": "point"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_sum(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_sum(**spec)


@register_plot_component("stat_summary_bin", ui_schema={
    "label": "Stat: binned summary",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "summary", "bin", "aggregate", "group"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_summary_bin"]}],
    "allow_extra_params": True,
    "params": {
        "fun_y": {"widget": "string", "label": "Function for y (e.g. 'mean', 'median')", "required": False},
        "fun_ymin": {"widget": "string", "label": "Function for ymin", "required": False},
        "fun_ymax": {"widget": "string", "label": "Function for ymax", "required": False},
        "bins": {"widget": "number", "label": "Number of bins", "required": False, "default": 30},
        "binwidth": {"widget": "number", "label": "Bin width (data units)", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
})
def handle_stat_summary_bin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_summary_bin(**spec)


@register_plot_component("labs", ui_schema={
    "label": "Labels (title, axes, legend)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["labels", "title", "axis", "legend", "annotation", "subtitle", "caption"],
    "wraps": [{"lib": "plotnine", "attr_path": ["labs"]}],
    "allow_extra_params": True,
    "params": {
        "title": {"widget": "string", "label": "Plot title", "required": False},
        "subtitle": {"widget": "string", "label": "Subtitle (below title)", "required": False},
        "caption": {"widget": "string", "label": "Caption (bottom right)", "required": False},
        "x": {"widget": "string", "label": "X-axis label", "required": False},
        "y": {"widget": "string", "label": "Y-axis label", "required": False},
        "fill": {"widget": "string", "label": "Fill legend title", "required": False},
        "colour": {"widget": "string", "label": "Colour legend title", "required": False},
        "color": {"widget": "string", "label": "Color legend title (alias)", "required": False},
        "size": {"widget": "string", "label": "Size legend title", "required": False},
        "shape": {"widget": "string", "label": "Shape legend title", "required": False},
        "alpha": {"widget": "string", "label": "Alpha legend title", "required": False},
        "linetype": {"widget": "string", "label": "Linetype legend title", "required": False},
    },
})
def handle_labs(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Label component (title, x, y, custom scales)."""
    return p + labs(**spec)
