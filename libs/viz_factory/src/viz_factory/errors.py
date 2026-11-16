"""One error form for the plot layer: what, which plot and layer, how to fix (VIZ-STANDARD-1, V6 and V7).

# @deps
# provides: class:CannotAct, function:plot_failure, function:layer_label
# consumes: libs/utils/src/utils/errors.py (VisualizationError), libs/utils/src/utils/pipeline_error.py (PipelineError)
# consumed_by: libs/viz_factory/src/viz_factory/viz_factory.py, libs/viz_factory/src/viz_factory/checked_plot.py, libs/viz_factory/src/viz_factory/{guides,positions,themes}/core.py
# doc: .claude/design/decisions_2026-11-14/viz_plan_for_eve.md (V6, V7), .claude/rules/rules_viz_factory.md
# @end_deps

Every error the factory raises, and every error plotnine raises while the factory builds or draws a plot, reaches the
author as one `VisualizationError` whose text is

    Plot 'p', layer 2 (geom_point): the value 'big' for 'size' is not a number. Fix: write a number, for example size: 3.

The structured record (`pipeline_error`: who fixes it, where it is shown) and the fix alone (`tip`) travel with it.
A component that cannot act raises `CannotAct`, with what and how to fix; the factory adds the plot and the layer.
"""
from typing import Optional

from utils.errors import VisualizationError
from utils.fix_text import fix_label
from utils.pipeline_error import PipelineError


class CannotAct(VisualizationError):
    """Raised by a plot component that cannot do what its name says (a missing target, mapping, geom ...).

    It carries no plot or layer: the component does not know them. The factory catches it and builds the one error form
    with `plot_failure`. Used outside the factory (a test, a script) it reads "what. Fix: how."
    """

    def __init__(self, what: str, fix: str):
        self.what = what
        self.fix = fix
        super().__init__(f"{what}. {fix_label(fix.rstrip('. '))}.", tip=fix)


_TIER_LABELS = {"L1": "built-in", "L2": "plot_defaults", "L3": "automatic", "L5": "override"}


def layer_label(tier: Optional[str], layer_no: Optional[int], name: str) -> str:
    """How an error names a layer: `layer 2 (geom_point)` for a layer the author wrote, otherwise where it came from."""
    if tier == "L4" and layer_no:
        return f"layer {layer_no} ({name})"
    if tier == "L4":
        kind = "theme" if name.startswith("theme_") else "facet_by"
        return f"the spec's {kind} ({name})"
    if tier == "L2" and layer_no:
        return f"plot_defaults layer {layer_no} ({name})"
    if tier in _TIER_LABELS:
        return f"{_TIER_LABELS[tier]} layer ({name})"
    return f"layer ({name})" if name else "layer"


def plot_failure(plot_id: str, what: str, fix: str, *, layer: Optional[str] = None,
                 evidence: Optional[dict] = None, reference: Optional[str] = None,
                 location: Optional[str] = None) -> VisualizationError:
    """The one error form. `layer` is the text of `layer_label`, or a block name such as `labels`; None for the whole plot."""
    what = what.rstrip(". ")
    fix = fix.rstrip(". ")
    where = f"Plot '{plot_id}'" + (f", {layer}" if layer else "")
    pipeline_error = PipelineError(
        component="VizFactory",
        problem=f"{where}: {what}.",
        location=location or f"VizFactory plot '{plot_id}'" + (f", {layer}" if layer else ""),
        fix=fix,
        who="data_analysis_recipe_author",
        category="visualization",
        surface="plot_overlay",
        severity="error",
        evidence=evidence or {},
        reference=reference or "",
    )
    return VisualizationError(f"{pipeline_error.problem} {fix_label(fix)}.", tip=fix, pipeline_error=pipeline_error)
