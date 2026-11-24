# @deps
# provides: function:plot_view
# consumes: libs/viz_factory/src/viz_factory/plot_config_resolver.py (normalise_plot_spec)
# consumed_by: app/handlers/blueprint_handlers.py, app/tests/test_blueprint_plot_open.py
# doc: .claude/design/recipe_format_spec.md (the plot entry, D-0252)
# @end_deps
"""What Blueprint shows when a plot node is opened, as a pure function (Two-Category Law, no Shiny).

A plot entry holds the whole plot (D-0252): the keys of the app (`ui_label`, `description`, `taxonomy`,
`plot_engine`), its target table, its `mapping` and its `layers`. It is written inline in the recipe or as the whole entry in
an included file; the content is the same, so one function reads both.
"""
from __future__ import annotations

from typing import Optional

from viz_factory.plot_config_resolver import normalise_plot_spec

MAPPING_NODE = "__mapping__"


def plot_view(entry) -> tuple[Optional[str], list[dict]]:
    """The target table of a plot entry and the nodes of its stack: the mapping first, then one node per layer.

    Not a dict (an empty file, a list) gives no table and no nodes: the screen then says so, it does not guess.
    """
    if not isinstance(entry, dict):
        return None, []
    canonical = normalise_plot_spec(entry)
    nodes: list[dict] = []
    mapping = canonical.get("mapping", {})
    if mapping:
        nodes.append({"component": MAPPING_NODE, "params": mapping, "comment": ""})
    for layer in canonical.get("layers", []):
        nodes.append({"component": layer.get("name", ""), "params": layer.get("params", {}), "comment": ""})
    return entry.get("target_dataset"), nodes
