import difflib
from typing import Dict, Any

# @deps
# provides: component:theme_gray, component:theme_bw, component:theme_linedraw, component:theme_light, component:theme_minimal, component:theme_classic, component:theme_void, component:theme_dark, component:theme_538, component:theme_matplotlib, component:theme_seaborn, component:theme_tufte, component:theme_xkcd, component:theme_dashboard, component:theme_publication, component:theme_legend_position, component:theme_custom, component:element_text, component:element_line, component:element_rect, component:element_blank, component:xlab, component:ylab, component:ggtitle, component:annotate
# consumes: libs/viz_factory/src/viz_factory/registry.py, libs/viz_factory/src/viz_factory/errors.py (CannotAct)
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import (
    theme, theme_gray, theme_bw, theme_linedraw, theme_light,
    theme_minimal, theme_classic, theme_void, theme_dark,
    theme_538, theme_matplotlib, theme_seaborn, theme_tufte, theme_xkcd,
    ggplot, element_text, element_line, element_rect, element_blank
)
from viz_factory.errors import CannotAct
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


_THEME_BASE_PARAMS = {
    "base_size": {"widget": "number", "label": "Base font size (pt)", "required": False, "default": 11},
    "base_family": {"widget": "string", "label": "Base font family", "required": False},
}


@register_plot_component("theme_gray", ui_schema={
    "label": "Theme gray (ggplot2 default)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "gray", "grey", "ggplot2", "default"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_gray"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "ggplot2 default theme with grey panel background and white gridlines; familiar to R users but less clean than theme_bw for publications. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_gray",
})
def handle_theme_gray(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_gray, spec)


@register_plot_component("theme_bw", ui_schema={
    "label": "Theme black & white",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "bw", "black", "white", "clean"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_bw"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Black-and-white theme with white background and dark gridlines; a good default for publications and reports. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_bw",
})
def handle_theme_bw(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_bw, spec)


@register_plot_component("theme_linedraw", ui_schema={
    "label": "Theme linedraw",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "linedraw", "black", "lines"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_linedraw"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Theme with white background and black lines/ticks only; the cleanest monochrome option for print output. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_linedraw",
})
def handle_theme_linedraw(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_linedraw, spec)


@register_plot_component("theme_light", ui_schema={
    "label": "Theme light",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "light", "clean", "minimal"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_light"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Light grey axes and gridlines on white background; a clean default that is lighter than theme_bw \u2014 use for dashboard or web output. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_light",
})
def handle_theme_light(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_light, spec)


@register_plot_component("theme_minimal", ui_schema={
    "label": "Theme minimal",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "minimal", "clean", "no-background"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_minimal"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Minimal theme with no background annotations; maximises data-ink ratio \u2014 use for clean figures in manuscripts. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_minimal",
})
def handle_theme_minimal(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_minimal, spec)


@register_plot_component("theme_classic", ui_schema={
    "label": "Theme classic (axes only)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "classic", "axes", "no-grid", "publication"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_classic"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Classic axes-only theme (no gridlines, no panel border background); the standard for journal figures in many life-science journals. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_classic",
})
def handle_theme_classic(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_classic, spec)


@register_plot_component("theme_void", ui_schema={
    "label": "Theme void (no axes, no grid)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "void", "blank", "empty", "map"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_void"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Empty theme with no axes or background; use for network plots, map layers, or any visualisation that supplies its own spatial context. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_void",
})
def handle_theme_void(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_void, spec)


@register_plot_component("theme_dark", ui_schema={
    "label": "Theme dark",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "dark", "night", "dark-background"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_dark"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Dark grey panel background; use for screen display when a dark UI background makes a dark plot less jarring. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_dark",
})
def handle_theme_dark(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_dark, spec)


@register_plot_component("theme_538", ui_schema={
    "label": "Theme FiveThirtyEight (538)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "538", "fivethirtyeight", "news", "editorial"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_538"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "FiveThirtyEight-style theme with soft gridlines and custom fonts; use for editorial data journalism aesthetics. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_538",
})
def handle_theme_538(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_538, spec)


@register_plot_component("theme_matplotlib", ui_schema={
    "label": "Theme matplotlib (default)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "matplotlib", "python", "default"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_matplotlib"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Matplotlib default theme; use when visual consistency with Python matplotlib output is needed. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_matplotlib",
})
def handle_theme_matplotlib(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_matplotlib, spec)


@register_plot_component("theme_seaborn", ui_schema={
    "label": "Theme seaborn",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "seaborn", "stats", "sns"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_seaborn"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Seaborn-style theme with whitegrid aesthetic; use when visual consistency with seaborn output is needed. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_seaborn",
})
def handle_theme_seaborn(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_seaborn, spec)


@register_plot_component("theme_tufte", ui_schema={
    "label": "Theme Tufte (minimalist data-ink)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "tufte", "minimalist", "data-ink", "publication"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_tufte"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "Edward Tufte's minimalist theme with no gridlines and axis spines removed; use for highly data-dense tables-as-charts. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_tufte",
})
def handle_theme_tufte(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_tufte, spec)


@register_plot_component("theme_xkcd", ui_schema={
    "label": "Theme xkcd (hand-drawn style)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "xkcd", "comic", "hand-drawn", "fun"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_xkcd"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": _THEME_BASE_PARAMS,
    "description": "xkcd webcomic-style hand-drawn theme; use for informal or illustrative figures only \u2014 not for scientific publications. Differs from plotnine: `base_size` and `base_family` go to the theme; every other key is added on top of it as a `theme()` setting, so one layer sets the theme and its details.",
    "yaml_example": "layers:\n  - name: theme_xkcd",
})
def handle_theme_xkcd(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    return p + _apply_theme_safely(theme_xkcd, spec)


@register_plot_component("theme_dashboard", ui_schema={
    "label": "Theme dashboard (SPARMVET)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "dashboard", "sparmvet", "default", "bw"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_bw"]}],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "base_size": {"widget": "number", "label": "Base font size (pt)", "required": False, "default": 14},
        "base_family": {"widget": "string", "label": "Base font family", "required": False},
    },
    "description": "SPARMVET custom dashboard theme tuned for app display; it is not applied unless a recipe names it (without a theme the figure uses plotnine's own default, D-0258). Not in plotnine: theme_bw with `base_size` 14 unless given; other keys are added as `theme()` settings.",
    "yaml_example": "layers:\n  - name: theme_dashboard",
})
def handle_theme_dashboard(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    spec.setdefault("base_size", 14)
    return p + _apply_theme_safely(theme_bw, spec)


@register_plot_component("theme_publication", ui_schema={
    "label": "Theme publication (classic, small font)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "publication", "journal", "classic", "print"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme_classic"]}],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "base_size": {"widget": "number", "label": "Base font size (pt)", "required": False, "default": 11},
        "base_family": {"widget": "string", "label": "Base font family", "required": False},
    },
    "description": "SPARMVET custom publication theme with minimal gridlines and increased font sizes; use when preparing figures for manuscripts. Not in plotnine: theme_classic with `base_size` 11 unless given; other keys are added as `theme()` settings.",
    "yaml_example": "layers:\n  - name: theme_publication",
})
def handle_theme_publication(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    spec.setdefault("base_size", 11)
    return p + _apply_theme_safely(theme_classic, spec)


@register_plot_component("theme_legend_position", ui_schema={
    "label": "Legend position",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "legend", "position", "placement"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme"]}],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "position": {"widget": "enum", "label": "Legend position", "required": True,
                     "default": "right", "options": ["top", "bottom", "left", "right", "none"]},
    },
    "description": "Move the legend to a named position (top, bottom, left, right, none); use as a lightweight alternative to a full theme_custom call. Not in plotnine: calls theme(legend_position=position) with `position` (right when absent).",
    "yaml_example": "layers:\n  - name: theme_legend_position\n    params:\n      position: bottom",
})
def handle_theme_legend_position(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    pos = spec.get("position", "right")
    return p + theme(legend_position=pos)


# The elements a theme_custom value {name: ..., params: ...} can be (D-0050: any other name is refused, never dropped).
_ELEMENT_BUILDERS = {"element_text": element_text, "element_line": element_line,
                     "element_rect": element_rect, "element_blank": element_blank}


@register_plot_component("theme_custom", ui_schema={
    "label": "Custom theme (element dict)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "custom", "element_text", "element_rect", "element_line"],
    "wraps": [{"lib": "plotnine", "attr_path": ["theme"]}],
    "plotnine": "own",
    "allow_extra_params": True,
    "params": {},
    "description": "Arbitrary theme() override; use to adjust any individual theme element when none of the named themes or element_* layers provide enough control. Not in plotnine: calls theme(**params); a value written as {name: element_text, params: {...}} (also element_line, element_rect, element_blank) is turned into that element, any other value is passed on as it is.",
    "yaml_example": "layers:\n  - name: theme_custom\n    params:\n      axis_text_x:\n        name: element_text\n        params: {angle: 45, hjust: 1}",
})
def handle_theme_custom(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    theme_kwargs = {}
    for key, val in spec.items():
        if isinstance(val, dict) and "name" in val:
            elem_name = val["name"]
            elem_params = val.get("params", {})
            if elem_name not in _ELEMENT_BUILDERS:
                close = difflib.get_close_matches(str(elem_name), list(_ELEMENT_BUILDERS), n=1, cutoff=0.6)
                raise CannotAct(
                    f"theme_custom setting '{key}' names the element {elem_name!r}, which does not exist "
                    f"(the elements are {', '.join(_ELEMENT_BUILDERS)})",
                    f"write name: {close[0]}" if close else f"write name: one of {', '.join(_ELEMENT_BUILDERS)}")
            if elem_name == "element_blank":
                if elem_params:
                    raise CannotAct(
                        f"theme_custom setting '{key}' gives element_blank parameters ({', '.join(map(str, elem_params))}), "
                        "and element_blank takes none: they would be ignored",
                        "remove params, or use element_text, element_line or element_rect if the element must be drawn")
                theme_kwargs[key] = element_blank()
            else:
                theme_kwargs[key] = _ELEMENT_BUILDERS[elem_name](**elem_params)
        else:
            theme_kwargs[key] = val

    return p + theme(**theme_kwargs)


@register_plot_component("element_text", ui_schema={
    "label": "Element text (theme override)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "element_text", "font", "axis", "text", "rotate"],
    "wraps": [{"lib": "plotnine", "attr_path": ["element_text"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "target": {"widget": "string", "label": "Theme target (e.g. axis_text_x, strip_text)", "required": True},
        "size": {"widget": "number", "label": "Font size", "required": False},
        "colour": {"widget": "color", "label": "Text colour", "required": False},
        "face": {"widget": "enum", "label": "Font face", "required": False,
                 "options": ["plain", "italic", "bold", "bold.italic"]},
        "family": {"widget": "string", "label": "Font family", "required": False},
        "angle": {"widget": "number", "label": "Rotation angle (degrees)", "required": False, "default": 0},
        "hjust": {"widget": "number", "label": "Horizontal justification (0–1)", "required": False},
        "vjust": {"widget": "number", "label": "Vertical justification (0–1)", "required": False},
    },
    "description": "Customise a specific text element (axis labels, title, strip text); use inside theme_custom or directly to rotate axis text or change font size. Differs from plotnine: plotnine's element_text only builds the element; here `target` names the theme setting (for example axis_text_x) the element is applied to, and without `target` the plot fails with a message.",
    "yaml_example": "layers:\n  - name: element_text\n    params:\n      target: axis_text_x\n      angle: 45\n      hjust: 1",
})
def handle_element_text(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme text modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        raise CannotAct("element_text needs 'target', the theme setting it changes",
                        "write target, for example target: axis_text_x")
    return p + theme(**{target: element_text(**spec)})


@register_plot_component("element_line", ui_schema={
    "label": "Element line (theme override)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "element_line", "axis", "grid", "line"],
    "wraps": [{"lib": "plotnine", "attr_path": ["element_line"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "target": {"widget": "string", "label": "Theme target (e.g. axis_line, panel_grid)", "required": True},
        "colour": {"widget": "color", "label": "Line colour", "required": False},
        "size": {"widget": "number", "label": "Line width", "required": False},
        "linetype": {"widget": "enum", "label": "Line type", "required": False,
                     "options": ["solid", "dashed", "dotted", "dotdash", "longdash", "twodash"]},
    },
    "description": "Customise a specific line element (gridlines, axis lines); use to change gridline colour, thickness, or linetype for a particular theme element. Differs from plotnine: plotnine's element_line only builds the element; here `target` names the theme setting (for example axis_text_x) the element is applied to, and without `target` the plot fails with a message.",
    "yaml_example": "layers:\n  - name: element_line\n    params:\n      target: panel_grid_major\n      colour: '#eeeeee'",
})
def handle_element_line(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme line modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        raise CannotAct("element_line needs 'target', the theme setting it changes",
                        "write target, for example target: axis_text_x")
    return p + theme(**{target: element_line(**spec)})


@register_plot_component("element_rect", ui_schema={
    "label": "Element rect (theme override)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "element_rect", "panel", "background", "border"],
    "wraps": [{"lib": "plotnine", "attr_path": ["element_rect"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "target": {"widget": "string", "label": "Theme target (e.g. panel_background, legend_key)", "required": True},
        "fill": {"widget": "color", "label": "Fill colour", "required": False},
        "colour": {"widget": "color", "label": "Border colour", "required": False},
        "size": {"widget": "number", "label": "Border line width", "required": False},
    },
    "description": "Customise a specific rectangle element (panel background, legend background); use to change background fills or border colours. Differs from plotnine: plotnine's element_rect only builds the element; here `target` names the theme setting (for example axis_text_x) the element is applied to, and without `target` the plot fails with a message.",
    "yaml_example": "layers:\n  - name: element_rect\n    params:\n      target: panel_background\n      fill: white",
})
def handle_element_rect(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme rect modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        raise CannotAct("element_rect needs 'target', the theme setting it changes",
                        "write target, for example target: axis_text_x")
    return p + theme(**{target: element_rect(**spec)})


@register_plot_component("element_blank", ui_schema={
    "label": "Element blank (remove element)",
    "category": "theme",
    "context": ["plot"],
    "tags": ["theme", "element_blank", "remove", "hide", "axis"],
    "wraps": [{"lib": "plotnine", "attr_path": ["element_blank"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "target": {"widget": "string", "label": "Theme target to remove (e.g. axis_text_x, panel_grid)", "required": True},
    },
    "description": "Remove a theme element entirely (make it invisible); use to hide axis lines, gridlines, or strip backgrounds. Differs from plotnine: plotnine's element_blank only builds the element; here `target` names the theme setting (for example axis_text_x) the element is applied to, and without `target` the plot fails with a message.",
    "yaml_example": "layers:\n  - name: element_blank\n    params:\n      target: panel_grid_minor",
})
def handle_element_blank(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standalone theme blank modifier. Requires 'target'."""
    target = spec.pop("target", None)
    if not target:
        raise CannotAct("element_blank needs 'target', the theme setting it changes",
                        "write target, for example target: axis_text_x")
    return p + theme(**{target: element_blank()})


# labs is registered with full ui_schema in geoms/core.py — canonical location.
# The duplicate here was removed (ACTION-RENAME-1) to eliminate the startup warning.

# ── DECO-2: convenience label/annotation wrappers (added 2026-04-30) ──────────
# Data analysis recipe authors often want one-line label setters rather than the full
# labs(x=..., y=...) call. These wrap plotnine's single-axis helpers.

def _read_text(name: str, spec: Dict[str, Any], key: str, example: str, allowed: tuple) -> Any:
    """The text a label component sets. A missing key or another key is an error: it used to give an empty text, silently."""
    unknown = sorted(k for k in spec if k not in allowed)
    if unknown:
        raise CannotAct(f"{name} reads {' and '.join(repr(k) for k in allowed)} and does not know {', '.join(repr(k) for k in unknown)}",
                        f"write {key}: {example}")
    if spec.get(key) is None:
        raise CannotAct(f"{name} needs '{key}', the text it sets", f"write {key}: {example}")
    return spec[key]


@register_plot_component("xlab", ui_schema={
    "label": "X-axis label",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["label", "xlab", "axis", "x", "title"],
    "wraps": [{"lib": "plotnine", "attr_path": ["xlab"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "label": {"widget": "string", "label": "X-axis label text", "required": True},
    },
    "description": "Set the x-axis label; a shorthand alternative to using labs with an x= parameter. Differs from plotnine: the text is read from the key `label`; without it, or with any other key, the plot fails with a message.",
    "yaml_example": "layers:\n  - name: xlab\n    params:\n      label: Year of isolation",
})
def handle_xlab(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the x-axis label.

    Spec is {"label": "..."}; a missing key fails (VIZ-STANDARD-1, V6).
    """
    from plotnine import xlab
    label = _read_text("xlab", spec, "label", "Year of isolation", ("label",))
    return p + xlab(label)


@register_plot_component("ylab", ui_schema={
    "label": "Y-axis label",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["label", "ylab", "axis", "y", "title"],
    "wraps": [{"lib": "plotnine", "attr_path": ["ylab"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "label": {"widget": "string", "label": "Y-axis label text", "required": True},
    },
    "description": "Set the y-axis label; a shorthand alternative to using labs with a y= parameter. Differs from plotnine: the text is read from the key `label`; without it, or with any other key, the plot fails with a message.",
    "yaml_example": "layers:\n  - name: ylab\n    params:\n      label: Number of isolates",
})
def handle_ylab(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the y-axis label."""
    from plotnine import ylab
    label = _read_text("ylab", spec, "label", "Number of isolates", ("label",))
    return p + ylab(label)


@register_plot_component("ggtitle", ui_schema={
    "label": "Plot title (ggtitle)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["label", "ggtitle", "title", "subtitle"],
    "wraps": [{"lib": "plotnine", "attr_path": ["ggtitle"]}],
    "plotnine": "modified",
    "allow_extra_params": False,
    "params": {
        "title": {"widget": "string", "label": "Plot title text", "required": True},
        "subtitle": {"widget": "string", "label": "Subtitle (below title)", "required": False},
    },
    "description": "Set the plot title and optional subtitle; a shorthand alternative to labs(title=..., subtitle=...). Differs from plotnine: the title is read from the key `title` (plotnine's own argument name) and the optional `subtitle`; without `title`, or with any other key, the plot fails with a message.",
    "yaml_example": "layers:\n  - name: ggtitle\n    params:\n      title: AMR prevalence by year",
})
def handle_ggtitle(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the plot title (and optional subtitle)."""
    from plotnine import ggtitle
    title = _read_text("ggtitle", spec, "title", "AMR prevalence by year", ("title", "subtitle"))
    subtitle = spec.get("subtitle")
    if subtitle:
        return p + ggtitle(title, subtitle=subtitle)
    return p + ggtitle(title)


@register_plot_component("annotate", ui_schema={
    "label": "Annotate (free-form layer)",
    "category": "annotation",
    "context": ["plot"],
    "tags": ["annotate", "text", "segment", "rect", "line", "arrow"],
    "wraps": [{"lib": "plotnine", "attr_path": ["annotate"]}],
    "plotnine": "modified",
    "allow_extra_params": True,
    "params": {
        "geom": {"widget": "enum", "label": "Annotation geom type", "required": True,
                 "options": ["text", "label", "segment", "rect", "point", "line"]},
        "x": {"widget": "number", "label": "X position", "required": False},
        "y": {"widget": "number", "label": "Y position", "required": False},
        "label": {"widget": "string", "label": "Text label (for text/label geom)", "required": False},
        "xmin": {"widget": "number", "label": "X min (for rect)", "required": False},
        "xmax": {"widget": "number", "label": "X max (for rect)", "required": False},
        "ymin": {"widget": "number", "label": "Y min (for rect/segment)", "required": False},
        "ymax": {"widget": "number", "label": "Y max (for rect/segment)", "required": False},
        "colour": {"widget": "color", "label": "Colour", "required": False},
        "size": {"widget": "number", "label": "Size", "required": False},
        "alpha": {"widget": "number", "label": "Opacity (0–1)", "required": False},
    },
    "description": "Add a single annotation geometry (text, rect, segment) at specified coordinates without a data source; use for static annotations like significance brackets. Differs from plotnine: the geom is named by the key `geom` and every other key is an argument of that geom; without `geom` the plot fails with a message.",
    "yaml_example": "layers:\n  - name: annotate\n    params:\n      geom: text\n      x: 2020\n      y: 80\n      label: 'n=42'",
})
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
        raise CannotAct("annotate needs 'geom', the kind of annotation (text, label, segment, rect, point, line)",
                        "write geom: text")
    kwargs = {k: v for k, v in spec.items() if k != "geom"}
    return p + annotate(geom, **kwargs)
