"""The gallery taxonomy read from the specification data: axes, labels, icons, order, the derived geom, the tag strip.

Why it exists: the terms, labels and icons of the six filter axes were copied in five places that disagreed (spec
section 9, finding G1). They now live in one place, `utils/recipe_spec.yaml` (key `gallery`), and everything that shows
them asks this module: the filter panels of the viewer, the index, the tag strip of `example_meta.md`.

Five axes are typed in a recipe (`taxonomy` on the plot entry). The sixth, `geom`, is derived: it is the first
`geom_*` or `stat_*` layer of the plot (spec section 9, D2), so it cannot disagree with what is drawn.

Consumed by: gallery_manager.py, app/modules/gallery_viewer.py, app/handlers/gallery_handlers.py,
assets/scripts/convert_gallery_examples.py. No Shiny import. If deleted: the index and the filter panels cannot be built.

# @deps
# provides: function:display_axes, function:first_geom, function:the_plot, function:example_taxonomy, function:tag_strip, function:with_tag_strip, function:filter_panels
# consumes: libs/utils/src/utils/recipe_check.py (spec), libs/utils/src/utils/recipe_spec.yaml (gallery)
# consumed_by: libs/viz_gallery/src/viz_gallery/gallery_manager.py, app/modules/gallery_viewer.py, app/handlers/gallery_handlers.py, assets/scripts/convert_gallery_examples.py
# doc: .claude/design/recipe_format_spec.md (section 9; findings G1, G4, G7; design D2, D3)
# @end_deps
"""
from typing import Any, Dict, List, Optional, Tuple

from utils.recipe_check import spec

DERIVED_AXIS = "geom"
_STRIP_SEPARATOR = " · "


def display_axes() -> List[Dict[str, str]]:
    """The six axes as the gallery shows them, in order: `[{axis, label, icon}, ...]`."""
    return [dict(entry) for entry in spec()["gallery"]["display"]]


def first_geom(plot_spec: Any) -> str:
    """The name of the first `geom_*` or `stat_*` layer of a plot specification; an empty text when there is none."""
    layers = plot_spec.get("layers") if isinstance(plot_spec, dict) else None
    for layer in layers if isinstance(layers, list) else []:
        name = layer.get("name") if isinstance(layer, dict) else None
        if isinstance(name, str) and name.startswith(("geom_", "stat_")):
            return name
    return ""


def the_plot(recipe: Any) -> Optional[Tuple[str, dict]]:
    """`(plot id, plot entry)` of an example, or None when the recipe does not hold exactly one plot."""
    groups = recipe.get("analysis_groups") if isinstance(recipe, dict) else None
    found = []
    for group in groups.values() if isinstance(groups, dict) else []:
        plots = group.get("plots") if isinstance(group, dict) else None
        found += list(plots.items()) if isinstance(plots, dict) else []
    if len(found) != 1 or not isinstance(found[0][1], dict):
        return None
    return found[0]


def example_taxonomy(recipe: dict) -> Dict[str, str]:
    """The six terms of an example in display order: the five typed in `taxonomy`, and `geom` read from the layers."""
    plot = the_plot(recipe)
    if plot is None:
        raise ValueError("a gallery example holds exactly one plot")
    entry = plot[1]
    typed = entry.get("taxonomy") or {}
    terms = {}
    for axis in (item["axis"] for item in display_axes()):
        terms[axis] = first_geom(entry.get("spec")) if axis == DERIVED_AXIS else typed[axis]
    return terms


def tag_strip(taxonomy: Dict[str, str]) -> str:
    """The tag strip line of `example_meta.md` for these six terms: `> icon term · icon term ...`."""
    return "> " + _STRIP_SEPARATOR.join(f"{item['icon']} {taxonomy[item['axis']]}" for item in display_axes())


def with_tag_strip(markdown: str, strip: str) -> str:
    """The text of an `example_meta.md` with its tag strip set to `strip`; every other line is kept as it is.

    The strip is the first block-quote line that follows the first `## ` heading (blank lines between them allowed).
    When the text has the heading and no strip, the strip is added under the heading. A text without a `## ` heading
    is refused: the place of the strip is not defined.
    """
    lines = markdown.split("\n")
    heading = next((index for index, line in enumerate(lines) if line.startswith("## ")), None)
    if heading is None:
        raise ValueError("example_meta.md has no '## ' heading: write the name of the example as '## Name' on the first line")
    after = heading + 1
    while after < len(lines) and not lines[after].strip():
        after += 1
    if after < len(lines) and lines[after].startswith(">"):
        lines[after] = strip
    else:
        text_follows = heading + 1 < len(lines) and bool(lines[heading + 1].strip())
        lines[heading + 1:heading + 1] = ["", strip] + ([""] if text_follows else [])
    return "\n".join(lines)


def filter_panels(pivot: Dict[str, Dict[str, list]]) -> List[Dict[str, Any]]:
    """The filter panels of the gallery for an index pivot: `[{axis, pivot_key, label, choices}, ...]` in display order.

    The choices of a typed axis are its terms in the order of the specification, limited to the terms that at least one
    indexed example uses. The choices of `geom` are the geoms of the indexed examples, sorted by name (an open list:
    every registered geom is a possible value).
    """
    terms = spec()["gallery"]["terms"]
    panels = []
    for item in display_axes():
        axis = item["axis"]
        used = pivot.get(f"by_{axis}", {}) if isinstance(pivot, dict) else {}
        choices = sorted(used) if axis == DERIVED_AXIS else [term for term in terms[axis] if term in used]
        panels.append({"axis": axis, "pivot_key": f"by_{axis}", "label": f"{item['icon']} {item['label']}", "choices": choices})
    return panels
