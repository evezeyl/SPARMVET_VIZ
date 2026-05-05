from typing import Dict, Any

# @deps
# provides: component:geom_boxplot, component:geom_violin, component:geom_point, component:geom_line, component:geom_bar, component:geom_col, component:geom_histogram, component:geom_smooth, component:geom_density, component:geom_errorbar, component:geom_pointrange, component:geom_tile, component:geom_raster, component:geom_text, component:geom_label, component:geom_jitter, component:geom_step, component:geom_segment, component:geom_abline, component:geom_area, component:geom_bin_2d, component:geom_blank, component:geom_count, component:geom_crossbar, component:geom_density_2d, component:geom_dotplot, component:geom_errorbarh, component:geom_freqpoly, component:geom_hline, component:geom_linerange, component:geom_path, component:geom_vline, component:stat_count, component:stat_bin, component:stat_summary, component:stat_boxplot, component:stat_smooth, component:stat_density, component:labs (geom)
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
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


@register_plot_component("geom_boxplot")
def handle_boxplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Boxplot component wrapper."""
    return p + geom_boxplot(**spec)


@register_plot_component("geom_violin")
def handle_violin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Violin (Density) component wrapper."""
    return p + geom_violin(**spec)


@register_plot_component("geom_point")
def handle_point(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Point (Scatter) component wrapper."""
    return p + geom_point(**spec)


@register_plot_component("geom_line")
def handle_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Line (Connected points) component wrapper."""
    return p + geom_line(**spec)


@register_plot_component("geom_bar")
def handle_bar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Bar (count) component wrapper."""
    return p + geom_bar(**spec)


@register_plot_component("geom_col")
def handle_col(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Column (identity) component wrapper."""
    return p + geom_col(**spec)


@register_plot_component("geom_histogram")
def handle_histogram(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Histogram component wrapper."""
    return p + geom_histogram(**spec)


@register_plot_component("geom_smooth")
def handle_smooth(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Smooth (Regression) component wrapper."""
    return p + geom_smooth(**spec)


@register_plot_component("geom_density")
def handle_density(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Density component wrapper."""
    return p + geom_density(**spec)


@register_plot_component("geom_errorbar")
def handle_errorbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Errorbar component wrapper."""
    return p + geom_errorbar(**spec)


@register_plot_component("geom_pointrange")
def handle_pointrange(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Pointrange component wrapper."""
    return p + geom_pointrange(**spec)


@register_plot_component("geom_tile")
def handle_tile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Tile (Heatmap) component wrapper."""
    return p + geom_tile(**spec)


@register_plot_component("geom_raster")
def handle_raster(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Raster (Heatmap) component wrapper."""
    return p + geom_raster(**spec)


@register_plot_component("geom_text")
def handle_text(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Text (Annotation) component wrapper."""
    return p + geom_text(**spec)


@register_plot_component("geom_label")
def handle_label(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Label (Annotation) component wrapper."""
    return p + geom_label(**spec)


@register_plot_component("geom_jitter")
def handle_jitter(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Jitter component wrapper."""
    return p + geom_jitter(**spec)


@register_plot_component("geom_step")
def handle_step(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Step plot component wrapper (useful for ECDF and staircases)."""
    return p + geom_step(**spec)


@register_plot_component("geom_segment")
def handle_segment(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard Segment component wrapper (useful for Lollipop charts)."""
    return p + geom_segment(**spec)


@register_plot_component("geom_abline")
def handle_abline(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Reference line with given slope and intercept."""
    return p + geom_abline(**spec)


@register_plot_component("geom_area")
def handle_area(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Filled area plot."""
    return p + geom_area(**spec)


@register_plot_component("geom_bin_2d")
def handle_bin_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Add a heatmap of 2d bin counts."""
    return p + geom_bin_2d(**spec)


@register_plot_component("geom_blank")
def handle_blank(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Draw nothing (useful for expanding limits)."""
    return p + geom_blank(**spec)


@register_plot_component("geom_count")
def handle_count(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Count number of point at location."""
    return p + geom_count(**spec)


@register_plot_component("geom_crossbar")
def handle_crossbar(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Hollow bar with median line."""
    return p + geom_crossbar(**spec)


@register_plot_component("geom_density_2d")
def handle_density_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Contours of a 2d density estimate."""
    return p + geom_density_2d(**spec)


@register_plot_component("geom_dotplot")
def handle_dotplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Dot plot."""
    return p + geom_dotplot(**spec)


@register_plot_component("geom_errorbarh")
def handle_errorbarh(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Horizontal error bars."""
    return p + geom_errorbarh(**spec)


@register_plot_component("geom_freqpoly")
def handle_freqpoly(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Frequency polygon."""
    return p + geom_freqpoly(**spec)


@register_plot_component("geom_hline")
def handle_hline(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Horizontal line."""
    return p + geom_hline(**spec)


@register_plot_component("geom_linerange")
def handle_linerange(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Vertical line segment."""
    return p + geom_linerange(**spec)


# @register_plot_component("geom_map")
# def handle_map(p: ggplot, spec: Dict[str, Any]) -> ggplot:
#     """Map polygons."""
#     return p + geom_map(**spec)


@register_plot_component("geom_path")
def handle_path(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Connected points in order of appearance."""
    return p + geom_path(**spec)


@register_plot_component("geom_pointdensity")
def handle_pointdensity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Cross between a scatter plot and a 2D density plot."""
    return p + geom_pointdensity(**spec)


@register_plot_component("geom_polygon")
def handle_polygon(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Filled polygons."""
    return p + geom_polygon(**spec)


@register_plot_component("geom_qq")
def handle_geom_qq(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Lower-level Quantile-Quantile plot."""
    return p + geom_qq(**spec)


@register_plot_component("geom_qq_line")
def handle_qq_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Reference line for a QQ plot."""
    return p + geom_qq_line(**spec)


@register_plot_component("geom_quantile")
def handle_quantile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Quantile regression."""
    return p + geom_quantile(**spec)


@register_plot_component("geom_rect")
def handle_rect(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """2D rectangles."""
    return p + geom_rect(**spec)


@register_plot_component("geom_ribbon")
def handle_ribbon(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Filled area between two lines."""
    return p + geom_ribbon(**spec)


@register_plot_component("geom_rug")
def handle_rug(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Marginal rug plots."""
    return p + geom_rug(**spec)


@register_plot_component("geom_sina")
def handle_sina(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Sina plot (normalized violin)."""
    return p + geom_sina(**spec)


@register_plot_component("geom_spoke")
def handle_spoke(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Line segment with given angle and radius."""
    return p + geom_spoke(**spec)


@register_plot_component("geom_vline")
def handle_vline(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Vertical line."""
    return p + geom_vline(**spec)


# --- Statistical Components ---


@register_plot_component("stat_count")
def handle_stat_count(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_count(**spec)


@register_plot_component("stat_bin")
def handle_stat_bin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bin(**spec)


@register_plot_component("stat_identity")
def handle_stat_identity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    # Most geoms default to stat_identity already
    return p


@register_plot_component("stat_summary")
def handle_stat_summary(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_summary(**spec)


@register_plot_component("stat_boxplot")
def handle_stat_boxplot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_boxplot(**spec)


@register_plot_component("stat_ydensity")
def handle_stat_ydensity(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ydensity(**spec)


@register_plot_component("stat_smooth")
def handle_stat_smooth(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_smooth(**spec)


@register_plot_component("stat_density")
def handle_stat_density(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_density(**spec)


@register_plot_component("stat_qq")
def handle_stat_qq(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_qq(**spec)


@register_plot_component("stat_ecdf")
def handle_stat_ecdf(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ecdf(**spec)


@register_plot_component("stat_unique")
def handle_stat_unique(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_unique(**spec)


@register_plot_component("stat_function")
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


@register_plot_component("stat_bin_2d")
def handle_stat_bin_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bin_2d(**spec)


@register_plot_component("stat_bindot")
def handle_stat_bindot(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_bindot(**spec)


@register_plot_component("stat_density_2d")
def handle_stat_density_2d(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_density_2d(**spec)


@register_plot_component("stat_ellipse")
def handle_stat_ellipse(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_ellipse(**spec)


@register_plot_component("stat_hull")
def handle_stat_hull(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_hull(**spec)


@register_plot_component("stat_qq_line")
def handle_stat_qq_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_qq_line(**spec)


@register_plot_component("stat_quantile")
def handle_stat_quantile(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_quantile(**spec)


@register_plot_component("stat_sina")
def handle_stat_sina(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_sina(**spec)


@register_plot_component("stat_sum")
def handle_stat_sum(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_sum(**spec)


@register_plot_component("stat_summary_bin")
def handle_stat_summary_bin(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + stat_summary_bin(**spec)


@register_plot_component("labs")
def handle_labs(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Label component (title, x, y, custom scales)."""
    return p + labs(**spec)
