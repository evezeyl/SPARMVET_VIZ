from typing import Dict, Any

# @deps
# provides: component:facet_wrap, component:facet_grid, component:facet_rows, component:facet_cols, component:facet_null, component:facet_scales, component:facet_space, component:facet_labeller, component:facet_margins
# consumed_by: any YAML plot spec using these component names, libs/viz_factory/src/viz_factory/viz_factory.py (via registry)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

import copy

from plotnine import facet_wrap, facet_grid, facet_null, ggplot
from utils.plot_text_check import facet_sides, facet_variables
from viz_factory.errors import CannotAct
from viz_factory.registry import register_plot_component


def _columns(p: ggplot):
    """The columns of the plot's data, or None when the plot has no table."""
    data = getattr(p, "data", None)
    return list(data.columns) if hasattr(data, "columns") else None


def _built(component: str, make):
    """Build the facet; what plotnine refuses is said in our words (it names no layer and gives no fix)."""
    try:
        return make()
    except CannotAct:
        raise
    except Exception as exc:
        first = (str(exc).strip().splitlines() or [type(exc).__name__])[0][:140]
        raise CannotAct(f"plotnine could not build the {component} ({type(exc).__name__}: {first})",
                        "Suggestion: write the exact name of a column of the data, or a list of names") from exc


def _facet_before(p: ggplot, component: str, setting: str, grid_only: bool):
    """A copy of the facet the recipe wrote before `component`, to change `setting` on; a plain error when there is none.

    plotnine fixes these settings inside facet_wrap or facet_grid, so the component can only change a facet that is
    already on the plot. The copy goes back with `p + facet`, which replaces the plot's facet.
    """
    facet = p.facet
    if facet is None or isinstance(facet, facet_null):
        raise CannotAct(
            f"{component} changes the {setting} of the facet written before it, and no facet is written before it",
            f"write {'facet_grid' if grid_only else 'facet_wrap or facet_grid'} first, then {component} after it "
            f"(or give {setting} in the facet itself)")
    if grid_only and not isinstance(facet, facet_grid):
        raise CannotAct(
            f"{component} changes the {setting} of a facet_grid, and the facet written before it is a facet_wrap, which has no {setting}",
            f"use facet_grid instead of facet_wrap")
    return copy.copy(facet)


@register_plot_component("facet_wrap", ui_schema={
    "label": "Facet wrap (1D panels)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "wrap", "panel", "small-multiples", "grid"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_wrap"]}],
    "plotnine": "exact",
    "allow_extra_params": False,
    "overlay": {
        "facets": {"widget": "string", "label": "Column to facet by (column name)"},
        "nrow": {"widget": "number", "label": "Number of rows (auto if omitted)"},
        "ncol": {"widget": "number", "label": "Number of columns (auto if omitted)"},
        "scales": {"widget": "enum", "label": "Scale freedom", "options": ["fixed", "free", "free_x", "free_y"]},
        "dir": {"widget": "enum", "label": "Fill direction", "options": ["h", "v"]},
    },
    "description": "Wrap a 1D sequence of panels by a single variable into a 2D grid; the default faceting choice when you have one grouping variable. You write a column name, a list of names or `~ a + b`; the library hands plotnine a list of exact column names, because plotnine cut a name with a space (`~Collection year` became the column `Collection`).",
    "yaml_example": "layers:\n  - name: facet_wrap\n    params:\n      facets: Country\n      ncol: 3",
})
def handle_facet_wrap(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Standard individual panel wrapping."""
    return p + facet_wrap(**spec)


@register_plot_component("facet_grid", ui_schema={
    "label": "Facet grid (2D panels)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "grid", "panel", "2D", "rows", "cols"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_grid"]}],
    "plotnine": "modified",
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
    "description": "Arrange panels in a 2D grid defined by row and column variables; use when cross-tabulating two categorical variables. Differs from plotnine: `facets` may be written as a formula `rows ~ cols` (a dot means none); it is split into `rows` and `cols`.",
    "yaml_example": "layers:\n  - name: facet_grid\n    params:\n      rows: Year\n      cols: Country",
})
def handle_facet_grid(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """
    Standard 2D grid of panels.
    Supports both formula-style 'facets' (rows ~ cols) or explicit 'rows'/'cols'.
    """
    spec = dict(spec)
    columns = _columns(p)
    facets = spec.pop("facets", None)
    if facets is not None:
        if isinstance(facets, str):
            try:
                spec["rows"], spec["cols"] = facet_sides(facets, columns)
            except ValueError as exc:
                raise CannotAct(f"the facet formula {facets!r} is not rows ~ columns ({exc})", "Suggestion: write rows ~ columns, with one ~") from exc
        else:
            spec["rows"] = facets
    # exact names, as a list (a text would be cut by plotnine at the first space, dash or dot)
    for side in ("rows", "cols"):
        if spec.get(side) is not None:
            spec[side] = facet_variables(spec[side], columns)
        if spec.get(side) == []:
            spec[side] = None
    return p + _built("facet_grid", lambda: facet_grid(**spec))


@register_plot_component("facet_rows", ui_schema={
    "label": "Facet rows (vertical stack)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "rows", "vertical", "stack", "panel"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_grid"]}],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "facets": {"widget": "string", "label": "Column to use as row facets", "required": True},
        "scales": {"widget": "enum", "label": "Scale freedom", "required": False,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Facet into a single column of rows by one variable; shorthand alternative to facet_grid with only a rows variable. Not in plotnine: facet_grid with only rows; the column to split by is `facets`.",
    "yaml_example": "layers:\n  - name: facet_rows\n    params:\n      facets: Country",
})
def handle_facet_rows(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for vertical-only stacking in a grid."""
    row_var = spec.pop("facets", None)
    if row_var is None:
        raise CannotAct("facet_rows has no column to split by", "write the column in `facets` (for example facets: Country); `rows` belongs to facet_grid")
    return p + _built("facet_grid", lambda: facet_grid(rows=facet_variables(row_var, _columns(p)), **spec))


@register_plot_component("facet_cols", ui_schema={
    "label": "Facet cols (horizontal layout)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "cols", "horizontal", "panel"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_grid"]}],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "facets": {"widget": "string", "label": "Column to use as column facets", "required": True},
        "scales": {"widget": "enum", "label": "Scale freedom", "required": False,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Facet into a single row of columns by one variable; shorthand alternative to facet_grid with only a cols variable. Not in plotnine: facet_grid with only columns; the column to split by is `facets`.",
    "yaml_example": "layers:\n  - name: facet_cols\n    params:\n      facets: Year",
})
def handle_facet_cols(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Shortcut for horizontal-only stacking in a grid."""
    col_var = spec.pop("facets", None)
    if col_var is None:
        raise CannotAct("facet_cols has no column to split by", "write the column in `facets` (for example facets: Year); `cols` belongs to facet_grid")
    return p + _built("facet_grid", lambda: facet_grid(cols=facet_variables(col_var, _columns(p)), **spec))


@register_plot_component("facet_null", ui_schema={
    "label": "Facet null (single panel)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "null", "single", "disable"],
    "wraps": [{"lib": "plotnine", "attr_path": ["facet_null"]}],
    "plotnine": "exact",
    "allow_extra_params": False,
    "overlay": {},
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
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "scales": {"widget": "enum", "label": "Scale freedom", "required": True,
                   "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Control whether axis scales are fixed or free across facet panels; use 'free_x' or 'free_y' when panels have very different ranges. Not in plotnine: changes the `scales` setting of the facet already on the plot (plotnine sets it inside facet_wrap or facet_grid); with no facet before it the plot is refused, with the fix.",
    "yaml_example": "layers:\n  - name: facet_wrap\n    params:\n      facets: Country\n  - name: facet_scales\n    params:\n      scales: free_y",
})
def handle_facet_scales(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to modify facet scales (free, free_x, free_y)."""
    scales = spec.get('scales', spec.get('value', 'fixed'))
    if scales not in ("fixed", "free", "free_x", "free_y"):
        raise CannotAct(f"facet_scales does not know the value '{scales}'", "write fixed, free, free_x or free_y")
    facet = _facet_before(p, "facet_scales", "scales", grid_only=False)
    facet.free = {"x": scales in ("free", "free_x"), "y": scales in ("free", "free_y")}
    return p + facet


@register_plot_component("facet_space", ui_schema={
    "label": "Facet space (panel spacing)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "space", "panel", "spacing"],
    "wraps": [],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "space": {"widget": "enum", "label": "Panel space", "required": True,
                  "default": "fixed", "options": ["fixed", "free", "free_x", "free_y"]},
    },
    "description": "Allocate panel space proportionally to data range when scales are free; combine with facet_scales to size panels by their content. Not in plotnine: changes the `space` setting of the facet already on the plot (plotnine sets it inside facet_grid); with no facet_grid before it the plot is refused, with the fix.",
    "yaml_example": "layers:\n  - name: facet_grid\n    params:\n      rows: Country\n      cols: Year\n      scales: free_y\n  - name: facet_space\n    params:\n      space: free_y",
})
def handle_facet_space(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to modify facet space (fixed, free)."""
    space = spec.get('space', spec.get('value', 'fixed'))
    if space not in ("fixed", "free", "free_x", "free_y"):
        raise CannotAct(f"facet_space does not know the value '{space}'", "write fixed, free, free_x or free_y")
    facet = _facet_before(p, "facet_space", "space", grid_only=True)
    facet.space = space
    return p + facet


@register_plot_component("facet_labeller", ui_schema={
    "label": "Facet labeller",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "label", "strip", "text"],
    "wraps": [],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "labeller": {"widget": "string", "label": "Labeller function name (e.g. 'label_both')", "required": True},
    },
    "description": "Set the labeller function for facet strip labels; use label_both to show 'variable: value' format in strips. Not in plotnine: sets the labeller of the facet already on the plot (plotnine sets it inside facet_wrap or facet_grid); with no facet before it the plot is refused, with the fix.",
    "yaml_example": "layers:\n  - name: facet_wrap\n    params:\n      facets: Country\n  - name: facet_labeller\n    params:\n      labeller: label_both",
})
def handle_facet_labeller(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Set the strip labeller on a copy of the facet written before."""
    from plotnine.facets.labelling import as_labeller
    labeller = spec.get('labeller', spec.get('value'))
    if labeller not in ("label_value", "label_both", "label_context"):
        raise CannotAct(f"facet_labeller does not know the labeller '{labeller}'", "write label_value, label_both or label_context")
    facet = _facet_before(p, "facet_labeller", "labeller", grid_only=False)
    facet.labeller = as_labeller(labeller)
    return p + facet


@register_plot_component("facet_margins", ui_schema={
    "label": "Facet margins (totals)",
    "category": "facet",
    "context": ["plot"],
    "tags": ["facet", "margins", "total", "summary"],
    "wraps": [],
    "plotnine": "own",
    "allow_extra_params": False,
    "params": {
        "margins": {"widget": "bool", "label": "Show margin (total) panels", "required": False, "default": True},
    },
    "description": "Add marginal panels that aggregate across a facet dimension; rarely needed \u2014 use for totals/grand-total rows in grid facets. Not in plotnine: sets `margins` of the facet already on the plot (plotnine sets it inside facet_grid); with no facet_grid before it the plot is refused, with the fix.",
    "yaml_example": "layers:\n  - name: facet_grid\n    params:\n      rows: Country\n      cols: Year\n  - name: facet_margins\n    params:\n      margins: true",
})
def handle_facet_margins(p: ggplot, spec: Dict[str, Any]) -> ggplot:
    """Helper to set facet margins."""
    facet = _facet_before(p, "facet_margins", "margins", grid_only=True)
    facet.margins = spec.get('margins', spec.get('value', True))
    return p + facet
