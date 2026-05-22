from typing import Dict, Any

# @deps
# provides: component:facet_wrap, component:facet_grid, component:facet_rows, component:facet_cols, component:facet_null, component:facet_scales, component:facet_space, component:facet_labeller, component:facet_margins
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

from plotnine import facet_wrap, facet_grid, ggplot
from viz_factory.registry import register_plot_component


@register_plot_component("facet_wrap", ui_schema={
    "label": "Facet wrap (1D panels)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "wrap", "panel", "small-multiples", "grid"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_wrap"]}],
    "allow_extra_params": False,
    "params": {
        "facets": {"widget": "string", "label": "Column to facet by (column name)", "required": True},
        "nrow": {"widget": "number", "label": "Number of rows (auto if omitted)", "required": False},
        "ncol": {"widget": "number", "label": "Number of columns (auto if omitted)", "required": False},
        "scales": {"widget": "enum", "label": "Scale freedom", "required": False,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
        "dir": {"widget": "enum", "label": "Fill direction", "required": False,
                "default": "h", "options": ["h", "v"]},
        "strip_position": {"widget": "enum", "label": "Strip label position", "required": False,
                           "default": "top", "options": ["top", "bottom", "left", "right"]},
    },
    "description": "Wrap a 1D sequence of panels by a single variable into a 2D grid; the default faceting choice when you have one grouping variable.",
    "yaml_example": "layers:\n  - name: facet_wrap\n    params:\n      facets: Country\n      ncol: 3",
})
def handle_facet_wrap(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard individual panel wrapping."""
    # Ensure facets is a list or string
    facets = spec.pop("facets", None)
    return p + facet_wrap(facets=facets, **spec)


@register_plot_component("facet_grid", ui_schema={
    "label": "Facet grid (2D panels)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "grid", "panel", "2D", "rows", "cols"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_grid"]}],
    "allow_extra_params": False,
    "params": {
        "rows": {"widget": "string", "label": "Row facet column (or leave empty for none)", "required": False},
        "cols": {"widget": "string", "label": "Column facet column (or leave empty for none)", "required": False},
        "scales": {"widget": "enum", "label": "Scale freedom", "required": False,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
        "space": {"widget": "enum", "label": "Panel space", "required": False,
                  "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
        "margins": {"widget": "bool", "label": "Show margin (total) panels", "required": False, "default": False},
    },
    "description": "Arrange panels in a 2D grid defined by row and column variables; use when cross-tabulating two categorical variables.",
    "yaml_example": "layers:\n  - name: facet_grid\n    params:\n      rows: Year\n      cols: Country",
})
def handle_facet_grid(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Standard 2D grid of panels.
    Supports both formula-style 'facets' (rows ~ cols) or explicit 'rows'/'cols'.
    """
    facets = spec.pop("facets", None)
    if facets and "~" in facets:
        items = [i.strip() for i in facets.split("~")]
        if len(items) == 2:
            spec["rows"] = items[0] if items[0] != "." else None
            spec["cols"] = items[1] if items[1] != "." else None

    # Remove 'facets' if still present for some reason (to avoid signature error)
    spec.pop("facets", None)
    return p + facet_grid(**spec)


@register_plot_component("facet_rows", ui_schema={
    "label": "Facet rows (vertical stack)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "rows", "vertical", "stack", "panel"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_grid"]}],
    "allow_extra_params": False,
    "params": {
        "facets": {"widget": "string", "label": "Column to use as row facets", "required": True},
        "scales": {"widget": "enum", "label": "Scale freedom", "required": False,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Facet into a single column of rows by one variable; shorthand alternative to facet_grid with only a rows variable.",
    "yaml_example": "layers:\n  - name: facet_rows\n    params:\n      rows: Country",
})
def handle_facet_rows(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for vertical-only stacking in a grid."""
    row_var = spec.pop("facets", None)
    return p + facet_grid(rows=row_var, **spec)


@register_plot_component("facet_cols", ui_schema={
    "label": "Facet cols (horizontal layout)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "cols", "horizontal", "panel"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_grid"]}],
    "allow_extra_params": False,
    "params": {
        "facets": {"widget": "string", "label": "Column to use as column facets", "required": True},
        "scales": {"widget": "enum", "label": "Scale freedom", "required": False,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Facet into a single row of columns by one variable; shorthand alternative to facet_grid with only a cols variable.",
    "yaml_example": "layers:\n  - name: facet_cols\n    params:\n      cols: Year",
})
def handle_facet_cols(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for horizontal-only stacking in a grid."""
    col_var = spec.pop("facets", None)
    return p + facet_grid(cols=col_var, **spec)


@register_plot_component("facet_null", ui_schema={
    "label": "Facet null (single panel)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "null", "single", "disable"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_null"]}],
    "allow_extra_params": False,
    "params": {},
    "description": "Explicitly remove faceting; use to clear a default facet in a downstream T3 override without rebuilding the full plot spec.",
    "yaml_example": "layers:\n  - name: facet_null",
})
def handle_facet_null(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Default single-panel display.
    This is useful for explicitly disabling multi-panel layouts.
    """
    from plotnine import facet_null
    return p + facet_null(**spec)


@register_plot_component("facet_scales", ui_schema={
    "label": "Facet scales (override)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "scales", "free", "fixed"],
    "wraps": [],
    "allow_extra_params": False,
    "params": {
        "scales": {"widget": "enum", "label": "Scale freedom", "required": True,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Control whether axis scales are fixed or free across facet panels; use 'free_x' or 'free_y' when panels have very different ranges.",
    "yaml_example": "layers:\n  - name: facet_scales\n    params:\n      scales: free_y",
})
def handle_facet_scales(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to modify facet scales (free, free_x, free_y)."""
    if hasattr(p, 'facet') and p.facet:
        p.facet.params['scales'] = spec.get(
            'scales', spec.get('value', 'fixed'))
    return p


@register_plot_component("facet_space", ui_schema={
    "label": "Facet space (panel spacing)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "space", "panel", "spacing"],
    "wraps": [],
    "allow_extra_params": False,
    "params": {
        "space": {"widget": "enum", "label": "Panel space", "required": True,
                  "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Allocate panel space proportionally to data range when scales are free; combine with facet_scales to size panels by their content.",
    "yaml_example": "layers:\n  - name: facet_space\n    params:\n      space: free_y",
})
def handle_facet_space(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to modify facet space (fixed, free)."""
    if hasattr(p, 'facet') and p.facet:
        p.facet.params['space'] = spec.get('space', spec.get('value', 'fixed'))
    return p


@register_plot_component("facet_labeller", ui_schema={
    "label": "Facet labeller",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "label", "strip", "text"],
    "wraps": [],
    "allow_extra_params": False,
    "params": {
        "labeller": {"widget": "string", "label": "Labeller function name (e.g. 'label_both')", "required": True},
    },
    "description": "Set the labeller function for facet strip labels; use label_both to show 'variable: value' format in strips.",
    "yaml_example": "layers:\n  - name: facet_labeller\n    params:\n      labeller: label_both",
})
def handle_facet_labeller(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set facet labeller on the current facet object."""
    labeller = spec.get('labeller', spec.get('value'))
    if labeller and hasattr(p, 'facet') and p.facet is not None:
        # Use setattr for compatibility across plotnine versions
        try:
            p.facet.labeller = labeller
        except AttributeError:
            params = getattr(p.facet, 'params', None)
            if params is not None:
                params['labeller'] = labeller
    return p


@register_plot_component("facet_margins", ui_schema={
    "label": "Facet margins (totals)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "margins", "total", "summary"],
    "wraps": [],
    "allow_extra_params": False,
    "params": {
        "margins": {"widget": "bool", "label": "Show margin (total) panels", "required": False, "default": True},
    },
    "description": "Add marginal panels that aggregate across a facet dimension; rarely needed \u2014 use for totals/grand-total rows in grid facets.",
    "yaml_example": "layers:\n  - name: facet_margins\n    params:\n      margins: true",
})
def handle_facet_margins(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set facet margins."""
    if hasattr(p, 'facet') and p.facet:
        p.facet.params['margins'] = spec.get(
            'margins', spec.get('value', True))
    return p
