from typing import Dict, Any

# @deps
# provides: component:theme_gray, component:theme_bw, component:theme_linedraw, component:theme_light, component:theme_minimal, component:theme_classic, component:theme_void, component:theme_dark, component:theme_538, component:theme_matplotlib, component:theme_seaborn, component:theme_tufte, component:theme_xkcd, component:theme_dashboard, component:theme_publication, component:theme_legend_position, component:theme_custom, component:element_text, component:element_line, component:element_rect, component:element_blank, component:xlab, component:ylab, component:ggtitle, component:annotate
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import (
    theme, theme_gray, theme_bw, theme_linedraw, theme_light,
    theme_minimal, theme_classic, theme_void, theme_dark,
    theme_538, theme_matplotlib, theme_seaborn, theme_tufte, theme_xkcd,
    ggplot, element_text, element_line, element_rect, element_blank
)
from viz_factory.registry import register_plot_component


def _apply_theme_safely(base_theme_func, spec: Dict[str, Any]) -> Any:
    """
    Helper to apply a base theme while allowing additional theme() parameters
    to be passed in the same spec (e.g. legend_position).
    """
    base_keys = ["base_size", "base_family"]
    base_params = {k: spec.pop(k) for k in base_keys if k in spec}

    # 1. Start with base theme
    p_theme = base_theme_func(**base_params)

    # 2. Add extra parameters via theme()
    if spec:
        p_theme += theme(**spec)

    return p_theme


@register_plot_component("theme_gray")
def handle_theme_gray(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_gray, spec)


@register_plot_component("theme_bw")
def handle_theme_bw(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_bw, spec)


@register_plot_component("theme_linedraw")
def handle_theme_linedraw(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_linedraw, spec)


@register_plot_component("theme_light")
def handle_theme_light(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_light, spec)


@register_plot_component("theme_minimal")
def handle_theme_minimal(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_minimal, spec)


@register_plot_component("theme_classic")
def handle_theme_classic(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_classic, spec)


@register_plot_component("theme_void")
def handle_theme_void(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_void, spec)


@register_plot_component("theme_dark")
def handle_theme_dark(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_dark, spec)


@register_plot_component("theme_538")
def handle_theme_538(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_538, spec)


@register_plot_component("theme_matplotlib")
def handle_theme_matplotlib(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_matplotlib, spec)


@register_plot_component("theme_seaborn")
def handle_theme_seaborn(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_seaborn, spec)


@register_plot_component("theme_tufte")
def handle_theme_tufte(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_tufte, spec)


@register_plot_component("theme_xkcd")
def handle_theme_xkcd(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_xkcd, spec)


@register_plot_component("theme_dashboard")
def handle_theme_dashboard(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    spec.setdefault("base_size", 14)
    return p + _apply_theme_safely(theme_bw, spec)


@register_plot_component("theme_publication")
def handle_theme_publication(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    spec.setdefault("base_size", 11)
    return p + _apply_theme_safely(theme_classic, spec)


@register_plot_component("theme_legend_position")
def handle_theme_legend_position(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    pos = spec.get("position", "right")
    return p + theme(legend_position=pos)


@register_plot_component("theme_custom")
def handle_theme_custom(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    theme_kwargs = {}
    for key, val in spec.items():
        if isinstance(val, dict) and "name" in val:
            elem_name = val["name"]
            elem_params = val.get("params", {})
            if elem_name == "element_text":
                theme_kwargs[key] = element_text(**elem_params)
            elif elem_name == "element_line":
                theme_kwargs[key] = element_line(**elem_params)
            elif elem_name == "element_rect":
                theme_kwargs[key] = element_rect(**elem_params)
            elif elem_name == "element_blank":
                theme_kwargs[key] = element_blank()
        else:
            theme_kwargs[key] = val

    return p + theme(**theme_kwargs)


@register_plot_component("element_text")
def handle_element_text(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme text modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        print("Warning: element_text requires a 'target' (e.g., axis_text_x).")
        return p
    return p + theme(**{target: element_text(**spec)})


@register_plot_component("element_line")
def handle_element_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme line modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        print("Warning: element_line requires a 'target'.")
        return p
    return p + theme(**{target: element_line(**spec)})


@register_plot_component("element_rect")
def handle_element_rect(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme rect modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        print("Warning: element_rect requires a 'target'.")
        return p
    return p + theme(**{target: element_rect(**spec)})


@register_plot_component("element_blank")
def handle_element_blank(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme blank modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        print("Warning: element_blank requires a 'target'.")
        return p
    return p + theme(**{target: element_blank()})


# labs is registered with full ui_schema in geoms/core.py — canonical location.
# The duplicate here was removed (ACTION-RENAME-1) to eliminate the startup warning.

# ── DECO-2: convenience label/annotation wrappers (added 2026-04-30) ──────────
# Manifest authors often want one-line label setters rather than the full
# labs(x=..., y=...) call. These wrap plotnine's single-axis helpers.

@register_plot_component("xlab")
def handle_xlab(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the x-axis label.

    Spec accepts either {"label": "..."} or just a plain string (passed via
    spec["label"] by viz_factory's flat-aesthetic standardisation).
    """
    from plotnine import xlab
    label = spec.get("label", "")
    return p + xlab(label)


@register_plot_component("ylab")
def handle_ylab(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the y-axis label."""
    from plotnine import ylab
    label = spec.get("label", "")
    return p + ylab(label)


@register_plot_component("ggtitle")
def handle_ggtitle(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the plot title (and optional subtitle)."""
    from plotnine import ggtitle
    title = spec.get("title", "")
    subtitle = spec.get("subtitle")
    if subtitle:
        return p + ggtitle(title, subtitle=subtitle)
    return p + ggtitle(title)


@register_plot_component("annotate")
def handle_annotate(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Add a free-form annotation layer (text, segment, rect, etc.).

    Spec must include `geom` (e.g. "text", "segment", "rect", "point") and the
    aesthetic kwargs that geom expects (x, y, label, xmin/xmax, etc.).
    Example:
        - name: annotate
          geom: text
          x: 5
          y: 100
          label: "p < 0.05"
    """
    from plotnine import annotate
    geom = spec.get("geom")
    if not geom:
        return p
    kwargs = {k: v for k, v in spec.items() if k != "geom"}
    return p + annotate(geom, **kwargs)
