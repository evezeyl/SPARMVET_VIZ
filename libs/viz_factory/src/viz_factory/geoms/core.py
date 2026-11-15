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

_GEOM_LINE_OVERLAY = {
    "alpha": {"widget": "number", "label": "Opacity (0–1)"},
    "colour": {"widget": "color", "label": "Colour (fixed, not mapped)"},
    "size": {"widget": "number", "label": "Line width"},
    "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
}

_GEOM_FILL_OVERLAY = {
    "alpha": {"widget": "number", "label": "Opacity (0–1)"},
    "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)"},
    "colour": {"widget": "color", "label": "Border colour"},
    "size": {"widget": "number", "label": "Border line width"},
    "linetype": {"widget": "enum", "label": "Border line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
}

_GEOM_REFLINE_OVERLAY = {
    "colour": {"widget": "color", "label": "Line colour"},
    "size": {"widget": "number", "label": "Line width"},
    "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    "alpha": {"widget": "number", "label": "Opacity (0–1)"},
}

_STAT_SMOOTH_OVERLAY = {
    "method": {"widget": "enum", "label": "Smoothing method", "options": ["auto", "lm", "loess", "rlm", "glm", "gam"]},
    "se": {"widget": "bool", "label": "Show confidence interval"},
    "level": {"widget": "number", "label": "Confidence level (0–1)"},
    "n": {"widget": "number", "label": "Number of interpolation points"},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
}

_STAT_DENSITY_OVERLAY = {
    "adjust": {"widget": "number", "label": "Bandwidth adjustment multiplier"},
    "kernel": {"widget": "enum", "label": "Kernel type", "options": ["gaussian", "epanechnikov", "rectangular", "triangular", "biweight",
                           "cosine", "optcosine"]},
    "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
}


@register_plot_component("geom_boxplot", ui_schema={
    "label": "Box plot",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["distribution", "boxplot", "outliers", "quartiles", "summary"],
    "wraps": [{"lib": "plotnine", "attr_path": ["geom_boxplot"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)"},
        "colour": {"widget": "color", "label": "Border/outlier colour"},
        "size": {"widget": "number", "label": "Line width"},
        "width": {"widget": "number", "label": "Box width (0–1)"},
        "notch": {"widget": "bool", "label": "Show notch (confidence interval)"},
        "outlier_colour": {"widget": "color", "label": "Outlier point colour"},
        "outlier_shape": {"widget": "any", "label": "Outlier point shape (a code 0–25 or a marker name such as o)"},
        "outlier_size": {"widget": "number", "label": "Outlier point size"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "stat": {"widget": "string", "label": "Statistical transformation"},
    },
    "description": "Box-and-whisker plot showing median, IQR, and outliers; prefer over bar+error for skewed or small-n distributions.",
    "yaml_example": "layers:\n  - name: geom_boxplot",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
        "width": {"widget": "number", "label": "Max violin width (data units)"},
        "scale": {"widget": "enum", "label": "Scale violins to", "options": ["area", "count", "width"]},
        "trim": {"widget": "bool", "label": "Trim tails to data range"},
        "draw_quantiles": {"widget": "string", "label": "Quantile lines to draw (e.g. [0.25,0.5,0.75])"},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2"]},
    },
    "description": "Kernel-density shape mirrored around a line; shows full distribution shape unlike boxplot \u2014 use when n is large enough to estimate density.",
    "yaml_example": "layers:\n  - name: geom_violin",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)"},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)"},
        "size": {"widget": "number", "label": "Point size"},
        "shape": {"widget": "any", "label": "Shape (a code 0–25 or a marker name such as o)"},
        "stroke": {"widget": "number", "label": "Border stroke width"},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "jitter", "jitterdodge", "dodge"]},
        "stat": {"widget": "string", "label": "Statistical transformation"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Scatter plot of individual data points; the default choice for two continuous variables or for overlaying raw data onto summaries.",
    "yaml_example": "layers:\n  - name: geom_point",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "lineend": {"widget": "enum", "label": "Line end style", "options": ["butt", "round", "square"]},
        "linejoin": {"widget": "enum", "label": "Line join style", "options": ["round", "mitre", "bevel"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "jitter"]},
        "stat": {"widget": "string", "label": "Statistical transformation"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Connect points with a line in x-axis order; use for time series or trends where the order of observations is meaningful.",
    "yaml_example": "layers:\n  - name: geom_line",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)"},
        "colour": {"widget": "color", "label": "Border colour"},
        "size": {"widget": "number", "label": "Border line width"},
        "linetype": {"widget": "enum", "label": "Border line type", "options": ["solid", "dashed", "dotted", "blank"]},
        "width": {"widget": "number", "label": "Bar width (0–1)"},
        "stat": {"widget": "enum", "label": "Statistical transformation", "options": ["count", "identity", "bin", "density"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["stack", "dodge", "fill", "identity", "dodge2"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Counted bar chart \u2014 computes counts from raw data using stat_count; use when you want to display frequency of a categorical variable without pre-aggregating.",
    "yaml_example": "layers:\n  - name: geom_bar",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
        "width": {"widget": "number", "label": "Bar width (0–1)"},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["stack", "dodge", "fill", "identity", "dodge2"]},
    },
    "description": "Bar chart from pre-computed values using stat_identity; use instead of geom_bar when your data already contains the bar heights (e.g. summarize output).",
    "yaml_example": "layers:\n  - name: geom_col",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "bins": {"widget": "number", "label": "Number of bins"},
        "binwidth": {"widget": "number", "label": "Bin width (data units; overrides bins)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour (fixed, not mapped)"},
        "colour": {"widget": "color", "label": "Border colour"},
        "size": {"widget": "number", "label": "Border line width"},
        "linetype": {"widget": "enum", "label": "Border line type", "options": ["solid", "dashed", "dotted", "blank"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["stack", "dodge", "fill", "identity"]},
        "stat": {"widget": "enum", "label": "Statistical transformation", "options": ["bin", "count", "density", "identity"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Bin a continuous variable and display counts as bars; use to inspect the distribution shape of a numeric column.",
    "yaml_example": "layers:\n  - name: geom_histogram\n    params:\n      bins: 30",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_STAT_SMOOTH_OVERLAY,
        "alpha": {"widget": "number", "label": "CI ribbon opacity"},
        "colour": {"widget": "color", "label": "Line colour"},
        "fill": {"widget": "color", "label": "CI ribbon fill colour"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    },
    "description": "Fit and draw a smoothing line with a confidence ribbon; use to highlight trends in scatter plots without committing to a parametric model.",
    "yaml_example": "layers:\n  - name: geom_smooth\n    params:\n      method: loess",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_STAT_DENSITY_OVERLAY,
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour under curve"},
        "colour": {"widget": "color", "label": "Line colour"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "stack", "fill"]},
    },
    "description": "Kernel density estimate as a smooth curve; use for large n distributions where histogram bin choice is arbitrary.",
    "yaml_example": "layers:\n  - name: geom_density",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "width": {"widget": "number", "label": "Whisker width (data units)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Vertical error bars defined by ymin/ymax; requires pre-computed interval columns in the data \u2014 use after a summarize action.",
    "yaml_example": "layers:\n  - name: geom_errorbar\n    params:\n      width: 0.2",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour"},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)"},
        "size": {"widget": "number", "label": "Line width / point size"},
        "shape": {"widget": "any", "label": "Point shape (a code 0–25 or a marker name such as o)"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "fatten": {"widget": "number", "label": "Point size relative to line (multiplier)"},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Point with vertical range (ymin/ymax); combines a point estimate with its confidence interval in a single layer.",
    "yaml_example": "layers:\n  - name: geom_pointrange",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour (fixed override, not mapped)"},
        "colour": {"widget": "color", "label": "Tile border colour"},
        "size": {"widget": "number", "label": "Border line width"},
        "linetype": {"widget": "enum", "label": "Border line type", "options": ["solid", "dashed", "dotted", "blank"]},
        "width": {"widget": "number", "label": "Tile width (data units; default = resolution)"},
        "height": {"widget": "number", "label": "Tile height (data units; default = resolution)"},
        "stat": {"widget": "string", "label": "Statistical transformation"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Fill rectangular tiles defined by x/y centre coordinates; the standard layer for heatmaps.",
    "yaml_example": "layers:\n  - name: geom_tile",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour (fixed override, not mapped)"},
        "hjust": {"widget": "number", "label": "Horizontal justification (0=left, 0.5=center, 1=right)"},
        "vjust": {"widget": "number", "label": "Vertical justification (0=bottom, 0.5=center, 1=top)"},
        "interpolation": {"widget": "string", "label": "Interpolation between cell centres (for example bilinear; empty for none)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Faster alternative to geom_tile for evenly-spaced grids; use for large matrices where geom_tile performance is a bottleneck.",
    "yaml_example": "layers:\n  - name: geom_raster",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "colour": {"widget": "color", "label": "Text colour"},
        "size": {"widget": "number", "label": "Font size (pt)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "family": {"widget": "string", "label": "Font family"},
        "fontweight": {"widget": "string", "label": "Font weight (normal, bold, ...)"},
        "fontstyle": {"widget": "enum", "label": "Font style", "options": ["normal", "italic", "oblique"]},
        "ha": {"widget": "enum", "label": "Horizontal alignment", "options": ["left", "center", "right"]},
        "va": {"widget": "enum", "label": "Vertical alignment", "options": ["top", "center", "bottom", "baseline"]},
        "angle": {"widget": "number", "label": "Text angle (degrees)"},
        "lineheight": {"widget": "number", "label": "Line height multiplier"},
        "nudge_x": {"widget": "number", "label": "Horizontal nudge (data units)"},
        "nudge_y": {"widget": "number", "label": "Vertical nudge (data units)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Add text labels at x/y positions; use to annotate points or bars with a value column \u2014 prefer geom_label when readability on busy backgrounds matters.",
    "yaml_example": "layers:\n  - name: geom_text\n    params:\n      size: 8",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "colour": {"widget": "color", "label": "Text colour"},
        "fill": {"widget": "color", "label": "Label background fill"},
        "size": {"widget": "number", "label": "Font size (pt)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "family": {"widget": "string", "label": "Font family"},
        "fontweight": {"widget": "string", "label": "Font weight (normal, bold, ...)"},
        "fontstyle": {"widget": "enum", "label": "Font style", "options": ["normal", "italic", "oblique"]},
        "ha": {"widget": "enum", "label": "Horizontal alignment", "options": ["left", "center", "right"]},
        "va": {"widget": "enum", "label": "Vertical alignment", "options": ["top", "center", "bottom", "baseline"]},
        "angle": {"widget": "number", "label": "Text angle (degrees)"},
        "nudge_x": {"widget": "number", "label": "Horizontal nudge (data units)"},
        "nudge_y": {"widget": "number", "label": "Vertical nudge (data units)"},
        "label_padding": {"widget": "number", "label": "Padding around text (pt)"},
        "label_r": {"widget": "number", "label": "Corner radius (pt)"},
        "label_size": {"widget": "number", "label": "Border line width (pt)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Text labels with a filled background rectangle; more readable than geom_text on dense plots at the cost of more visual clutter.",
    "yaml_example": "layers:\n  - name: geom_label\n    params:\n      size: 8",
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
    "plotnine": "modified",
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
    "description": "Scatter points with random position noise; use to reduce overplotting in small categorical scatter plots \u2014 prefer geom_sina for publication. Differs from plotnine: the factory gives it a default seed, so the same recipe gives the same picture; `random_state: null` gives a new one each time.",
    "yaml_example": "layers:\n  - name: geom_jitter\n    params:\n      width: 0.2\n      height: 0",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_LINE_OVERLAY,
        "direction": {"widget": "enum", "label": "Step direction", "options": ["hv", "vh", "mid"]},
    },
    "description": "Connect points with a staircase line; use for survival curves, ECDF plots, or any variable that changes discretely.",
    "yaml_example": "layers:\n  - name: geom_step",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_LINE_OVERLAY,
        "arrow": {"widget": "string", "label": "Arrow spec (e.g. arrow(length=unit(0.1,'cm')))"},
        "lineend": {"widget": "enum", "label": "Line end style", "options": ["butt", "round", "square"]},
    },
    "description": "Draw line segments from (x, y) to (xend, yend); use for arrows, dumbbell charts, or connecting paired observations.",
    "yaml_example": "layers:\n  - name: geom_segment",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "slope": {"widget": "number", "label": "Slope"},
        "intercept": {"widget": "number", "label": "Y-intercept"},
        **_GEOM_REFLINE_OVERLAY,
    },
    "description": "Draw a reference line defined by slope and intercept; use to overlay the identity line (slope=1, intercept=0) on scatter plots or regression diagnostics.",
    "yaml_example": "layers:\n  - name: geom_abline\n    params:\n      slope: 1\n      intercept: 0",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["stack", "fill", "identity"]},
        "stat": {"widget": "string", "label": "Statistical transformation"},
    },
    "description": "Filled area plot from y=0 to y; use for time series where you want to emphasise cumulative volume rather than just trend.",
    "yaml_example": "layers:\n  - name: geom_area",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "bins": {"widget": "number", "label": "Number of bins in each direction"},
        "binwidth": {"widget": "string", "label": "Bin widths [x, y] (e.g. [1,1])"},
        **_GEOM_FILL_OVERLAY,
    },
    "description": "2D rectangular binning coloured by count; use to reveal structure in dense scatter plots where individual points overlap.",
    "yaml_example": "layers:\n  - name: geom_bin_2d\n    params:\n      bins: 30",
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
    "plotnine": "exact",
    "allow_extra_params": False,
    "overlay": {},
    "description": "Invisible layer that contributes only axis expansion; use to force axis limits without drawing any geometry.",
    "yaml_example": "layers:\n  - name: geom_blank",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)"},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)"},
        "shape": {"widget": "any", "label": "Shape (a code 0–25 or a marker name such as o)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Scatter plot with point size proportional to count of overlapping observations; use instead of geom_jitter when exact counts matter.",
    "yaml_example": "layers:\n  - name: geom_count",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
        "fatten": {"widget": "number", "label": "Median line thickness multiplier"},
        "width": {"widget": "number", "label": "Bar width (data units)"},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2"]},
    },
    "description": "Hollow bar from ymin to ymax with a horizontal line at y; use to display a central estimate inside a range \u2014 often combined with geom_errorbar.",
    "yaml_example": "layers:\n  - name: geom_crossbar\n    params:\n      width: 0.2",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_LINE_OVERLAY,
    },
    "description": "2D kernel density contour lines; use to show the shape of a joint distribution overlaid on a scatter plot.",
    "yaml_example": "layers:\n  - name: geom_density_2d",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "binwidth": {"widget": "number", "label": "Bin width (data units)"},
        "bins": {"widget": "number", "label": "Number of bins"},
        "method": {"widget": "enum", "label": "Binning method", "options": ["dotdensity", "histodot"]},
        "stackdir": {"widget": "enum", "label": "Stack direction", "options": ["up", "down", "center", "centerwhole"]},
        "binaxis": {"widget": "enum", "label": "Bin axis", "options": ["x", "y"]},
        "dotsize": {"widget": "number", "label": "Dot size (relative to binwidth)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "fill": {"widget": "color", "label": "Fill colour"},
        "colour": {"widget": "color", "label": "Border colour"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Stack dots along an axis with each dot representing one observation; a more data-dense alternative to histograms for small samples.",
    "yaml_example": "layers:\n  - name: geom_dotplot\n    params:\n      binwidth: 1",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "height": {"widget": "number", "label": "Whisker height (data units)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Horizontal error bars defined by xmin/xmax; use for forest plots or when the uncertainty is on the x-axis.",
    "yaml_example": "layers:\n  - name: geom_errorbarh\n    params:\n      height: 0.2",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "bins": {"widget": "number", "label": "Number of bins"},
        "binwidth": {"widget": "number", "label": "Bin width (data units; overrides bins)"},
        **_GEOM_LINE_OVERLAY,
    },
    "description": "Frequency polygon (binned counts as a line rather than bars); use to overlay multiple distributions without the visual weight of histograms.",
    "yaml_example": "layers:\n  - name: geom_freqpoly\n    params:\n      bins: 30",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "yintercept": {"widget": "number", "label": "Y-intercept (Y value of the line)"},
        **_GEOM_REFLINE_OVERLAY,
    },
    "description": "Draw a horizontal reference line at a fixed y intercept; use to mark thresholds (e.g. AMR resistance breakpoints).",
    "yaml_example": "layers:\n  - name: geom_hline\n    params:\n      yintercept: 90",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "dodge", "dodge2", "jitter", "jitterdodge"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Vertical line segment from ymin to ymax with no centre point; use for range-only displays without a point estimate marker.",
    "yaml_example": "layers:\n  - name: geom_linerange",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_LINE_OVERLAY,
        "lineend": {"widget": "enum", "label": "Line end style", "options": ["butt", "round", "square"]},
        "linejoin": {"widget": "enum", "label": "Line join style", "options": ["round", "mitre", "bevel"]},
        "arrow": {"widget": "string", "label": "Arrow spec (e.g. arrow(length=unit(0.1,'cm')))"},
    },
    "description": "Connect points in their row order rather than x-axis order; use for trajectories, connected scatter plots, or time loops.",
    "yaml_example": "layers:\n  - name: geom_path",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "size": {"widget": "number", "label": "Point size"},
        "shape": {"widget": "any", "label": "Shape (a code 0–25 or a marker name such as o)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Scatter plot where point colour encodes local density; use on dense scatter plots to reveal clustering without binning.",
    "yaml_example": "layers:\n  - name: geom_pointdensity",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
    },
    "description": "Filled polygon from x/y/group columns; use for geographic polygons or custom shapes \u2014 requires a data source with polygon vertex coordinates.",
    "yaml_example": "layers:\n  - name: geom_polygon",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm, t, exp)"},
        "dparams": {"widget": "string", "label": "Distribution parameters (dict expression)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour"},
        "size": {"widget": "number", "label": "Point size"},
        "shape": {"widget": "any", "label": "Shape (a code 0–25 or a marker name such as o)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Quantile-quantile plot comparing observed distribution to a theoretical one; use to visually assess normality assumptions.",
    "yaml_example": "layers:\n  - name: geom_qq",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm, t)"},
        "line_p": {"widget": "string", "label": "Quantile probabilities for line [lo, hi]"},
        "fullrange": {"widget": "bool", "label": "Extend line to full plot range"},
        **_GEOM_REFLINE_OVERLAY,
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Reference line for a Q-Q plot; always pair with geom_qq to make the expected distribution visible.",
    "yaml_example": "layers:\n  - name: geom_qq\n  - name: geom_qq_line",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "quantiles": {"widget": "string", "label": "Quantile(s) to fit (e.g. [0.25,0.5,0.75])"},
        **_GEOM_LINE_OVERLAY,
    },
    "description": "Fit and draw quantile regression lines; use to show how different quantiles of y change with x, especially for heteroscedastic data.",
    "yaml_example": "layers:\n  - name: geom_quantile\n    params:\n      quantiles: [0.25, 0.5, 0.75]",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
    },
    "description": "Draw rectangles defined by xmin/xmax/ymin/ymax; use for Gantt-style charts, region highlights, or custom annotation boxes.",
    "yaml_example": "layers:\n  - name: geom_rect",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        **_GEOM_FILL_OVERLAY,
        "position": {"widget": "enum", "label": "Position adjustment", "options": ["identity", "stack", "fill"]},
    },
    "description": "Shaded band between ymin and ymax lines; use for confidence intervals around time series or smooth lines.",
    "yaml_example": "layers:\n  - name: geom_ribbon\n    params:\n      alpha: 0.3",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "sides": {"widget": "enum", "label": "Sides to draw rug on", "options": ["b", "l", "t", "r", "bl", "bt", "br", "lt", "lr", "tr", "blt", "blr", "btr",
                               "ltr", "bltr"]},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Tick colour"},
        "size": {"widget": "number", "label": "Tick line width"},
        "length": {"widget": "string", "label": "Tick length (unit string, e.g. '0.03npc')"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Marginal tick marks on the axes showing raw data positions; use alongside scatter or density plots to show the actual data distribution.",
    "yaml_example": "layers:\n  - name: geom_rug\n    params:\n      alpha: 0.3",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "scale": {"widget": "enum", "label": "Scale points to", "options": ["area", "count", "width"]},
        "method": {"widget": "enum", "label": "Density method", "options": ["density", "counts"]},
        "maxwidth": {"widget": "number", "label": "Maximum width of sina (0–1)"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour (fixed, not mapped)"},
        "fill": {"widget": "color", "label": "Fill colour (for filled shapes)"},
        "size": {"widget": "number", "label": "Point size"},
        "shape": {"widget": "any", "label": "Shape (a code 0–25 or a marker name such as o)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Jittered points constrained to the density shape (like violin + jitter); the publication-preferred alternative to geom_jitter for showing individual points.",
    "yaml_example": "layers:\n  - name: geom_sina",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "radius": {"widget": "number", "label": "Spoke radius (overrides mapped radius)"},
        "arrow": {"widget": "bool", "label": "Draw arrowheads"},
        "alpha": {"widget": "number", "label": "Opacity (0–1)"},
        "colour": {"widget": "color", "label": "Colour"},
        "size": {"widget": "number", "label": "Line width"},
        "linetype": {"widget": "enum", "label": "Line type", "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Line segments from (x, y) in a direction (angle) of a given radius; use for wind roses or directional data.",
    "yaml_example": "layers:\n  - name: geom_spoke",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "xintercept": {"widget": "number", "label": "X-intercept (X value of the line)"},
        **_GEOM_REFLINE_OVERLAY,
    },
    "description": "Draw a vertical reference line at a fixed x intercept; use to mark boundaries, dates, or thresholds.",
    "yaml_example": "layers:\n  - name: geom_vline\n    params:\n      xintercept: 2020",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "width": {"widget": "number", "label": "Bar width (0–1)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Count the number of observations at each x value; the default stat used by geom_bar \u2014 only override if you need the count without the bar geometry.",
    "yaml_example": "layers:\n  - name: stat_count",
})
def handle_stat_count(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_count(**spec)


@register_plot_component("stat_bin", ui_schema={
    "label": "Stat: bin observations",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "bin", "histogram", "frequency", "numeric"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_bin"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "bins": {"widget": "number", "label": "Number of bins"},
        "binwidth": {"widget": "number", "label": "Bin width (data units; overrides bins)"},
        "boundary": {"widget": "number", "label": "Bin boundary alignment value"},
        "center": {"widget": "number", "label": "Bin center alignment value"},
        "closed": {"widget": "enum", "label": "Bin interval closure", "options": ["right", "left"]},
        "pad": {"widget": "bool", "label": "Add empty bins at each end"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Bin continuous data and count observations per bin; the default stat for geom_histogram \u2014 specify directly when building custom binned geometries.",
    "yaml_example": "layers:\n  - name: stat_bin\n    params:\n      bins: 20",
})
def handle_stat_bin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bin(**spec)


@register_plot_component("stat_identity", ui_schema={
    "label": "Stat: identity (passthrough)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "identity", "passthrough", "utility"],
    "wraps": [],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {},
    "description": "Pass data through unchanged (no statistical transformation); the default stat for most geoms \u2014 specify explicitly only when overriding another stat. Differs from plotnine: adds nothing to the plot and ignores its parameters; every geom already uses the identity stat unless another is named.",
    "yaml_example": "layers:\n  - name: stat_identity",
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
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "fun_y": {"widget": "string", "label": "Function for y (e.g. 'mean', 'median')"},
        "fun_ymin": {"widget": "string", "label": "Function for ymin"},
        "fun_ymax": {"widget": "string", "label": "Function for ymax"},
        "fun_data": {"widget": "string", "label": "Function returning data frame"},
        "geom": {"widget": "string", "label": "Geom to render (e.g. point, errorbar, bar)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute a summary function (default: mean_se) for each x group; use to overlay group summaries on geom_point or geom_jitter layers.",
    "yaml_example": "layers:\n  - name: stat_summary\n    params:\n      fun_y: mean",
})
def handle_stat_summary(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_summary(**spec)


@register_plot_component("stat_boxplot", ui_schema={
    "label": "Stat: boxplot (compute box statistics)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "boxplot", "quartiles", "IQR", "outliers"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_boxplot"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "coef": {"widget": "number", "label": "Whisker coefficient (IQR multiplier)"},
        "geom": {"widget": "string", "label": "Geom to render"},
        "width": {"widget": "number", "label": "Box width (0–1)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute box-plot statistics (five-number summary + outliers); the default stat for geom_boxplot \u2014 rarely needed directly.",
    "yaml_example": "layers:\n  - name: stat_boxplot",
})
def handle_stat_boxplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_boxplot(**spec)


@register_plot_component("stat_ydensity", ui_schema={
    "label": "Stat: y-density (violin statistics)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "ydensity", "violin", "density", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_ydensity"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "scale": {"widget": "enum", "label": "Scale violins to", "options": ["area", "count", "width"]},
        "trim": {"widget": "bool", "label": "Trim tails to data range"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute kernel density in the y direction (normalised to a common scale); the default stat for geom_violin \u2014 use to change bandwidth or density scaling.",
    "yaml_example": "layers:\n  - name: stat_ydensity\n    params:\n      scale: width",
})
def handle_stat_ydensity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ydensity(**spec)


@register_plot_component("stat_smooth", ui_schema={
    "label": "Stat: smooth (trend line)",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["stat", "smooth", "trend", "regression", "loess", "lm"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_smooth"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {**_STAT_SMOOTH_OVERLAY},
    "description": "Fit a smoothing model and compute confidence interval; the default stat for geom_smooth \u2014 specify directly to change the method without the smooth geometry.",
    "yaml_example": "layers:\n  - name: stat_smooth\n    params:\n      method: lm",
})
def handle_stat_smooth(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_smooth(**spec)


@register_plot_component("stat_density", ui_schema={
    "label": "Stat: density (kernel density estimate)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "density", "kde", "distribution", "smooth"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_density"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {**_STAT_DENSITY_OVERLAY},
    "description": "Compute 1D kernel density; the default stat for geom_density \u2014 use to tune bandwidth or trim range independently of the geometry.",
    "yaml_example": "layers:\n  - name: stat_density\n    params:\n      adjust: 1.5",
})
def handle_stat_density(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_density(**spec)


@register_plot_component("stat_qq", ui_schema={
    "label": "Stat: quantile-quantile",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "qq", "quantile", "normality", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_qq"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm)"},
        "dparams": {"widget": "string", "label": "Distribution parameters (dict expression)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute theoretical vs sample quantiles for Q-Q plots; the default stat for geom_qq \u2014 rarely needed directly unless changing the distribution.",
    "yaml_example": "layers:\n  - name: stat_qq\n    params:\n      distribution: norm",
})
def handle_stat_qq(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_qq(**spec)


@register_plot_component("stat_ecdf", ui_schema={
    "label": "Stat: empirical CDF",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "ecdf", "cdf", "cumulative", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_ecdf"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "n": {"widget": "number", "label": "Number of interpolation points"},
        "pad": {"widget": "bool", "label": "Pad to 0 and 1 at extremes"},
        "geom": {"widget": "string", "label": "Geom to render"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute empirical cumulative distribution function; use with geom_step to show what fraction of data lies below each value.",
    "yaml_example": "layers:\n  - name: stat_ecdf",
})
def handle_stat_ecdf(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ecdf(**spec)


@register_plot_component("stat_unique", ui_schema={
    "label": "Stat: unique (remove duplicates)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "unique", "deduplicate", "filter", "utility"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_unique"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Remove duplicate rows before plotting; use to avoid overplotting without jitter when duplicate coordinates should be de-duplicated.",
    "yaml_example": "layers:\n  - name: stat_unique",
})
def handle_stat_unique(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_unique(**spec)


def _function_from_string(text: str):
    """A recipe's function string (a math function name or a lambda over numbers), checked, then evaluated with numpy maths only.

    Before, any string was passed to eval and an unknown name only printed a warning and left the layer out
    (spec section 15; check ST06).
    """
    import math
    import numpy as np
    from utils.errors import VisualizationError
    from utils.formula_check import MATH_CONSTANTS, MATH_FUNCTIONS, function_string_problems

    problems = function_string_problems(text)
    if problems:
        raise VisualizationError(
            "stat_function: the function string is not allowed. " + " ".join(problems),
            tip="Fix: write a lambda of one argument over numbers, for example lambda x: x * 2")
    names = {name: getattr(np, name) for name in MATH_FUNCTIONS}
    names.update(MATH_CONSTANTS)
    names.update({"np": np, "math": math})
    return eval(compile(text.strip(), "<stat_function>", "eval"), {"__builtins__": {}, **names})  # noqa: S307


@register_plot_component("stat_function", ui_schema={
    "label": "Stat: function (plot a math function)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["stat", "function", "curve", "math", "annotation"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_function"]}],
    "plotnine": "modified",
    "allow_extra_params": True,
    "params": {
        "fun": {"widget": "string", "label": "Function as Python expression (e.g. 'lambda x: x**2')",
                "required": True},
        "n": {"widget": "number", "label": "Number of evaluation points", "required": False, "default": 101},
        "xlim": {"widget": "string", "label": "X range for evaluation [min, max]", "required": False},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows", "required": False, "default": False},
    },
    "description": "Evaluate an arbitrary function over the x range; use to overlay a theoretical curve (e.g. normal distribution, growth model) on data. Differs from plotnine: `fun` may be written as text (a math function name or a lambda over numbers); the text is checked and turned into a function with numpy maths only, where plotnine takes a function.",
    "yaml_example": "layers:\n  - name: stat_function\n    params:\n      fun: \"lambda x: 2 * x\"",
})
def handle_stat_function(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Statistical function layer. 'fun' is a callable, or a string from a recipe that is checked before it is evaluated."""
    spec = dict(spec)
    fun = spec.get("fun")
    if isinstance(fun, str):
        spec["fun"] = _function_from_string(fun)
    return p + stat_function(**spec)


@register_plot_component("stat_bin_2d", ui_schema={
    "label": "Stat: 2D binning",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "bin2d", "heatmap", "density", "2d", "count"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_bin_2d"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "bins": {"widget": "string", "label": "Bins per axis [x, y] or single number"},
        "binwidth": {"widget": "string", "label": "Bin widths [x, y]"},
        "drop": {"widget": "bool", "label": "Drop bins with zero count"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "2D rectangular binning computing count per bin; the default stat for geom_bin_2d \u2014 use to change binwidth or resolution.",
    "yaml_example": "layers:\n  - name: stat_bin_2d\n    params:\n      bins: 20",
})
def handle_stat_bin_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bin_2d(**spec)


@register_plot_component("stat_bindot", ui_schema={
    "label": "Stat: dot-plot binning",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "bindot", "dotplot", "frequency", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_bindot"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "binwidth": {"widget": "number", "label": "Bin width (data units)"},
        "binaxis": {"widget": "enum", "label": "Bin axis", "options": ["x", "y"]},
        "method": {"widget": "enum", "label": "Binning method", "options": ["dotdensity", "histodot"]},
        "origin": {"widget": "number", "label": "Bin origin"},
        "right": {"widget": "bool", "label": "Right-closed intervals"},
        "drop": {"widget": "bool", "label": "Drop empty bins"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Bin data for dot plots; the default stat for geom_dotplot \u2014 use to control bin width in dot plot stacking.",
    "yaml_example": "layers:\n  - name: stat_bindot\n    params:\n      binwidth: 1",
})
def handle_stat_bindot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bindot(**spec)


@register_plot_component("stat_density_2d", ui_schema={
    "label": "Stat: 2D density estimate",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "density2d", "contour", "bivariate", "kde"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_density_2d"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "contour": {"widget": "bool", "label": "Compute contours"},
        "n": {"widget": "number", "label": "Grid points per axis for evaluation"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute 2D kernel density estimate; the default stat for geom_density_2d \u2014 use to tune bandwidth or contour levels.",
    "yaml_example": "layers:\n  - name: stat_density_2d\n    params:\n      contour: true",
})
def handle_stat_density_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_density_2d(**spec)


@register_plot_component("stat_ellipse", ui_schema={
    "label": "Stat: confidence ellipse",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "ellipse", "confidence", "group", "cluster"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_ellipse"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "type": {"widget": "enum", "label": "Ellipse type", "options": ["t", "norm", "euclid"]},
        "level": {"widget": "number", "label": "Confidence level (0–1)"},
        "segments": {"widget": "number", "label": "Number of ellipse segments"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Fit a confidence ellipse around groups of points; use to show cluster boundaries or group confidence regions on scatter plots.",
    "yaml_example": "layers:\n  - name: stat_ellipse\n    params:\n      level: 0.95",
})
def handle_stat_ellipse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ellipse(**spec)


@register_plot_component("stat_hull", ui_schema={
    "label": "Stat: convex hull",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "hull", "convex", "polygon", "group", "cluster"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_hull"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "geom": {"widget": "string", "label": "Geom to render hull with"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute convex hull of points in each group; use to outline group extents on scatter plots where ellipses would be misleading.",
    "yaml_example": "layers:\n  - name: stat_hull",
})
def handle_stat_hull(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_hull(**spec)


@register_plot_component("stat_qq_line", ui_schema={
    "label": "Stat: QQ reference line",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "qq", "reference", "normality", "line"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_qq_line"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "distribution": {"widget": "string", "label": "Distribution name (e.g. norm)"},
        "dparams": {"widget": "string", "label": "Distribution parameters (dict expression)"},
        "line_p": {"widget": "string", "label": "Quantile probabilities for line [lo, hi]"},
        "fullrange": {"widget": "bool", "label": "Extend line to full plot range"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute the reference line for a Q-Q plot; the default stat for geom_qq_line \u2014 rarely needed directly.",
    "yaml_example": "layers:\n  - name: stat_qq_line",
})
def handle_stat_qq_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_qq_line(**spec)


@register_plot_component("stat_quantile", ui_schema={
    "label": "Stat: quantile regression",
    "category": "evolution",
    "context": ["plot"],
    "tags": ["stat", "quantile", "regression", "trend", "robust"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_quantile"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "quantiles": {"widget": "string", "label": "Quantile(s) to fit (e.g. [0.25,0.5,0.75])"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Fit quantile regression; the default stat for geom_quantile \u2014 use to change which quantiles are fitted.",
    "yaml_example": "layers:\n  - name: stat_quantile\n    params:\n      quantiles: [0.1, 0.5, 0.9]",
})
def handle_stat_quantile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_quantile(**spec)


@register_plot_component("stat_sina", ui_schema={
    "label": "Stat: sina (density-normalized jitter)",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "sina", "jitter", "violin", "density", "distribution"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_sina"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "scale": {"widget": "enum", "label": "Scale points to", "options": ["area", "count", "width"]},
        "method": {"widget": "enum", "label": "Density method", "options": ["density", "counts"]},
        "maxwidth": {"widget": "number", "label": "Maximum width (0–1)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute density-constrained jitter for sina plots; the default stat for geom_sina \u2014 use to change bandwidth scaling.",
    "yaml_example": "layers:\n  - name: stat_sina",
})
def handle_stat_sina(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_sina(**spec)


@register_plot_component("stat_sum", ui_schema={
    "label": "Stat: sum (count unique combinations)",
    "category": "correlation",
    "context": ["plot"],
    "tags": ["stat", "sum", "count", "size", "overplot"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_sum"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "geom": {"widget": "string", "label": "Geom to render"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Compute the count of overlapping observations (similar to stat_count but for 2D); the default stat for geom_count.",
    "yaml_example": "layers:\n  - name: stat_sum",
})
def handle_stat_sum(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_sum(**spec)


@register_plot_component("stat_summary_bin", ui_schema={
    "label": "Stat: binned summary",
    "category": "distribution",
    "context": ["plot"],
    "tags": ["stat", "summary", "bin", "aggregate", "group"],
    "wraps": [{"lib": "plotnine", "attr_path": ["stat_summary_bin"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "fun_y": {"widget": "string", "label": "Function for y (e.g. 'mean', 'median')"},
        "fun_ymin": {"widget": "string", "label": "Function for ymin"},
        "fun_ymax": {"widget": "string", "label": "Function for ymax"},
        "bins": {"widget": "number", "label": "Number of bins"},
        "binwidth": {"widget": "number", "label": "Bin width (data units)"},
        "na_rm": {"widget": "bool", "label": "Silently remove NA rows"},
    },
    "description": "Bin x then apply a summary function to y within each bin; use for smoothed summary curves when x is continuous and you want binned means.",
    "yaml_example": "layers:\n  - name: stat_summary_bin\n    params:\n      fun_y: mean\n      bins: 20",
})
def handle_stat_summary_bin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_summary_bin(**spec)


@register_plot_component("labs", ui_schema={
    "label": "Labels (title, axes, legend)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["labels", "title", "axis", "legend", "annotation", "subtitle", "caption"],
    "wraps": [{"lib": "plotnine", "attr_path": ["labs"]}],
    "plotnine": "exact",
    "allow_extra_params": True,
    "overlay": {
        "title": {"widget": "string", "label": "Plot title"},
        "subtitle": {"widget": "string", "label": "Subtitle (below title)"},
        "caption": {"widget": "string", "label": "Caption (bottom right)"},
        "x": {"widget": "string", "label": "X-axis label"},
        "y": {"widget": "string", "label": "Y-axis label"},
        "fill": {"widget": "string", "label": "Fill legend title"},
        "colour": {"widget": "string", "label": "Colour legend title"},
        "color": {"widget": "string", "label": "Color legend title (alias)"},
        "size": {"widget": "string", "label": "Size legend title"},
        "shape": {"widget": "string", "label": "Shape legend title"},
        "alpha": {"widget": "string", "label": "Alpha legend title"},
        "linetype": {"widget": "string", "label": "Linetype legend title"},
    },
    "description": "Set axis labels, title, subtitle, caption, and legend titles; use for every plot to replace default column names with human-readable text.",
    "yaml_example": "layers:\n  - name: labs\n    params:\n      title: My Plot Title\n      x: Year\n      y: Count\n      fill: Resistance",
})
def handle_labs(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Label component (title, x, y, custom scales)."""
    return p + labs(**spec)
