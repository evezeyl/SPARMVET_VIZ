"""
@deps
provides: function:view_badge, function:has_tier2_steps, class:ViewBadge
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

The badge is HTML next to the plot, never part of the image, so it is never exported.
"""
from dataclasses import dataclass
from typing import Optional

from app.modules.cache_keys import tier2_steps

TIER_NAMES = {"T1": "Raw", "T2": "Result", "T3": "My view"}


@dataclass(frozen=True)
class ViewBadge:
    tier: str                 # "T1", "T2" or "T3": decides the colour
    label: str                # "Viewing: Result"
    notes: tuple              # short remarks such as ("T2=T1",)


def has_tier2_steps(raw_config: dict, target_dataset: Optional[str]) -> bool:
    """True when the join that builds the plot's dataset has tier-2 steps.

    A plot that targets a bare data schema (no join) has none, so Result equals Raw.
    """
    if not target_dataset:
        return False
    return bool(tier2_steps(raw_config, target_dataset))


def view_badge(tier: str, has_tier2: bool, has_changes: bool) -> ViewBadge:
    """The badge for a view.

    tier         "T1" (Raw), "T2" (Result) or "T3" (My view)
    has_tier2    the plot's dataset has tier-2 steps in the data analysis recipe
    has_changes  My view has an applied filter, or a committed filter or column drop, for this plot
    """
    label = f"Viewing: {TIER_NAMES.get(tier, tier)}"
    notes: list[str] = []
    if tier == "T2":
        if not has_tier2:
            notes.append("T2=T1")
    elif tier == "T3":
        if not has_changes:
            notes.append("T3=T2" if has_tier2 else "T3=T2=T1")
        elif not has_tier2:
            notes.append("T2=T1")
    return ViewBadge(tier=tier, label=label, notes=tuple(notes))
