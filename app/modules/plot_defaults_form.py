# engine: python-plotnine (the plotnine theme names that the plot defaults form offers, and the plotnine default when none is chosen)
# @deps
# provides: function:form_values, function:theme_choices, function:merged_plot_defaults, constant:FORM_KEYS, constant:NO_THEME
# consumes: libs/utils/src/utils/recipe_check.py (plot_defaults_keys: the keys the checker accepts)
# consumed_by: app/handlers/blueprint_handlers.py, app/tests/test_blueprint_plot_defaults_form.py
# doc: .claude/rules/rules_data_analysis_recipe_structure.md#10
# @end_deps
"""What Blueprint's plot-defaults form shows and writes, as pure functions (Two-Category Law, no Shiny).

The form shows two keys of the `plot_defaults` block of the open recipe: `palette` and `theme`. A save changes only the
keys the user changed and keeps every other part of the block as it was (the seed `random_state`, the `layers`, any
accepted key the form does not show). With no theme chosen it writes none: plotnine's own default applies (D-0258).
The four keys removed from the format (D-0220, D-0242) are neither shown nor written.
"""
from __future__ import annotations

from typing import Optional

from utils.recipe_check import plot_defaults_keys

FORM_KEYS = ("palette", "theme")
NO_THEME = ""  # the choice that writes no theme: the figure uses plotnine's own default
_KNOWN_THEMES = ("theme_light", "theme_bw", "theme_minimal", "theme_classic", "theme_dashboard")

# the form may only offer what the checker accepts
assert set(FORM_KEYS) <= set(plot_defaults_keys()[0])


def form_values(defaults: Optional[dict]) -> dict:
    """The value of each field of the form for a `plot_defaults` block (a missing key is an empty field)."""
    block = defaults or {}
    return {"palette": str(block.get("palette") or ""), "theme": str(block.get("theme") or NO_THEME)}


def theme_choices(defaults: Optional[dict]) -> dict:
    """The theme choices: no theme first, the shipped themes, and the theme the block already holds when it is another one."""
    current = form_values(defaults)["theme"]
    names = list(_KNOWN_THEMES)
    if current and current not in names:
        names.append(current)
    return {NO_THEME: "(none: plotnine's default)", **{name: name for name in names}}


def merged_plot_defaults(existing: Optional[dict], palette: str, theme: str) -> dict:
    """The block to write after a save: `existing` with only `palette` and `theme` set from the form.

    An empty palette removes the key, no theme removes the key; every other key is kept as it was, with its value.
    """
    block = dict(existing or {})
    palette = (palette or "").strip()
    theme = (theme or NO_THEME).strip()
    if palette:
        block["palette"] = palette
    else:
        block.pop("palette", None)
    if theme:
        block["theme"] = theme
    else:
        block.pop("theme", None)
    return block
