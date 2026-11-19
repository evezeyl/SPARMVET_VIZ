"""
@deps
provides: function:view_badge, function:has_tier2_steps, function:has_plot_steps, class:ViewBadge
consumes: app/modules/cache_keys.py
consumed_by: app/handlers/home_theater.py, app/tests/test_view_badge.py
doc: https://github.com/evezeyl/SPARMVET_VIZ/issues/17, .claude/knowledge/architecture_decisions.md#adr-086
@end_deps

What a panel is showing, in short words (issue #17). Pure logic, no Shiny.

The Home header strip has two choices (ADR-086): "Plot to show" and "Data to show". Next to each
panel a small badge says which view it shows ("Viewing: Result"), and when two views are the same
data it says so, so that "the button does nothing" is not a surprise:

  T2=T1       the plot's dataset has no tier-2 steps, so Result is identical to Raw
  T3=T2       My view without any filter or column drop is identical to Result
  T3=T2=T1    ... and Result is itself identical to Raw

A plot with tier-3 steps in the recipe reads its table plus those steps, so My view without any filter or drop is NOT the Result: the
badge then says that instead of an equality (PROVISIONAL words, the owner reads them):

  T3 = T2 plus this plot's own steps of the recipe          (the table has tier-2 steps)
  T3 = T2 = T1 plus this plot's own steps of the recipe     (it has none)

The badge is HTML next to the plot, never part of the image, so it is never exported.
"""
from dataclasses import dataclass
from typing import Optional

from app.modules.cache_keys import tier2_steps, tier3_steps

TIER_NAMES = {"T1": "Raw", "T2": "Result", "T3": "My view"}
# PROVISIONAL words (the owner reads them): My view of a plot with tier-3 steps in the recipe, no filter or drop on top
PLOT_STEPS_NOTE = "T3 = T2 plus this plot's own steps of the recipe"
PLOT_STEPS_NOTE_NO_TIER2 = "T3 = T2 = T1 plus this plot's own steps of the recipe"


@dataclass(frozen=True)
class ViewBadge:
    tier: str                 # "T1", "T2" or "T3": decides the colour
    label: str                # "Viewing: Result"
    notes: tuple              # short remarks such as ("T2=T1",)


def has_tier2_steps(raw_config: dict, target_dataset: Optional[str]) -> bool:
    """True when the plot's collection has tier-2 steps: a join's, or the own tier-2 list of a schema the plot
    reads directly (issue #77). Without them Result equals Raw.
    """
    if not target_dataset:
        return False
    return bool(tier2_steps(raw_config, target_dataset))


def has_plot_steps(raw_config: dict, plot_id: Optional[str]) -> bool:
    """True when the recipe writes tier-3 steps for this plot: its table is its target's table plus those steps."""
    if not plot_id:
        return False
    return bool(tier3_steps(raw_config, plot_id))


def view_badge(tier: str, has_tier2: bool, has_changes: bool, preview_filters: int = 0,
                table_only_filters: int = 0, plot_has_steps: bool = False) -> ViewBadge:
    """The badge for a view.

    tier         "T1" (Raw), "T2" (Result) or "T3" (My view)
    has_tier2    the plot's dataset has tier-2 steps in the data analysis recipe
    has_changes  My view has an applied filter, or a committed filter or column drop, for this plot
    plot_has_steps  the recipe writes tier-3 steps for this plot (`has_plot_steps`): My view without changes is then not equal to the Result
    """
    label = f"Viewing: {TIER_NAMES.get(tier, tier)}"
    notes: list[str] = []
    if tier == "T2":
        if not has_tier2:
            notes.append("T2=T1")
    elif tier == "T3":
        if not has_changes:
            if plot_has_steps:
                notes.append(PLOT_STEPS_NOTE if has_tier2 else PLOT_STEPS_NOTE_NO_TIER2)
            else:
                notes.append("T3=T2" if has_tier2 else "T3=T2=T1")
        elif not has_tier2:
            notes.append("T2=T1")
    if preview_filters and tier in ("T1", "T2"):
        notes.append(f"{preview_filters} preview filter(s) on, not saved")
    if table_only_filters and tier == "T2":
        notes.append(f"{table_only_filters} preview filter(s) change the table only; plots change on My view")
    return ViewBadge(tier=tier, label=label, notes=tuple(notes))
