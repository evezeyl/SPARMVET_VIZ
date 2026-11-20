"""
@deps
provides: function:view_badge, function:plot_badge, function:has_tier2_steps, function:has_plot_steps, class:ViewBadge
consumes: app/modules/cache_keys.py
consumed_by: app/handlers/home_theater.py, app/tests/test_view_badge.py
doc: https://github.com/evezeyl/SPARMVET_VIZ/issues/17, .claude/knowledge/architecture_decisions.md#adr-086
@end_deps

What a panel is showing, in short words (issue #17). Pure logic, no Shiny.

The Home header strip has the data choice (Source, T1, T2, T3; D-0310) and, with the audit switched on, the mode (Exploration or Audit).
Next to the data table a small badge says which table it shows ("Viewing: T2"), and when two views are the same data it says so, so that
"the button does nothing" is not a surprise:

  T2=T1       the plot's dataset has no tier-2 steps, so T2 is identical to T1
  T3=T2       the plot has no steps of its own in the recipe, so T3 is identical to T2
  T3=T2=T1    ... and T2 is itself identical to T1

A plot with tier-3 steps in the recipe reads its table plus those steps, so its T3 is NOT T2: the badge then says that instead of an
equality (PROVISIONAL words, the owner reads them):

  T3 = T2 plus this plot's own steps of the recipe          (the table has tier-2 steps)
  T3 = T2 = T1 plus this plot's own steps of the recipe     (it has none)

Exploration filters change the table only, never a plot (D-0311, ADR-098): the data badge and the plot badge both say so when filters are
on. In Audit mode T3 is the audited table (the plot's table plus its audited steps); T1, T2 and Source stay the original tables.

The badge is HTML next to the plot, never part of the image, so it is never exported.
"""
from dataclasses import dataclass
from typing import Optional

from app.modules.cache_keys import tier2_steps, tier3_steps

# PROVISIONAL words (the owner reads them): T3 of a plot with tier-3 steps in the recipe
PLOT_STEPS_NOTE = "T3 = T2 plus this plot's own steps of the recipe"
PLOT_STEPS_NOTE_NO_TIER2 = "T3 = T2 = T1 plus this plot's own steps of the recipe"
# PROVISIONAL words (slice B, P-B7): the Source view and the audited table
SOURCE_NOTE = "as read from its file, before any recipe step"
AUDITED_TABLE_NOTE = "the table the audited plot is drawn from: T3 plus {n} audited step(s)"

SOURCE_LABELS = {"SRC": "Source", "T1": "T1", "T2": "T2", "T3": "T3"}


@dataclass(frozen=True)
class ViewBadge:
    view: str                 # "SRC", "T1", "T2" or "T3" (a plot badge: "PLOT")
    label: str                # "Viewing: T2"
    notes: tuple              # short remarks such as ("T2=T1",)
    tone: str = "plain"       # "plain" (grey) or "audited" (amber: audited steps are on what is shown)


def has_tier2_steps(raw_config: dict, target_dataset: Optional[str]) -> bool:
    """True when the plot's collection has tier-2 steps: a join's, or the own tier-2 list of a schema the plot
    reads directly (issue #77). Without them T2 equals T1.
    """
    if not target_dataset:
        return False
    return bool(tier2_steps(raw_config, target_dataset))


def has_plot_steps(raw_config: dict, plot_id: Optional[str]) -> bool:
    """True when the recipe writes tier-3 steps for this plot: its table is its target's table plus those steps."""
    if not plot_id:
        return False
    return bool(tier3_steps(raw_config, plot_id))


def view_badge(view: str, has_tier2: bool, plot_has_steps: bool, preview_filters: int = 0, *, mode: str = "exploration",
               audited_steps: int = 0, source_table: Optional[str] = None) -> ViewBadge:
    """The badge of the data table.

    view            "SRC" (Source), "T1", "T2" or "T3"
    has_tier2       the plot's dataset has tier-2 steps in the data analysis recipe
    plot_has_steps  the recipe writes tier-3 steps for this plot (`has_plot_steps`): its T3 is then not equal to T2
    preview_filters how many exploration filters are applied (they change the table only; none exist in Audit mode)
    mode            "exploration" or "audit"; in Audit mode T3 carries the audited steps of the plot
    audited_steps   how many audited steps the plot has (read only in Audit mode, on T3)
    source_table    the id of the source table shown (view "SRC")
    """
    audited = mode == "audit" and view == "T3" and audited_steps > 0
    label = f"Viewing: {SOURCE_LABELS.get(view, view)}" + (" (audited)" if audited else "")
    notes: list[str] = []
    if view == "SRC":
        if source_table:
            notes.append(f"table '{source_table}'")
        notes.append(SOURCE_NOTE)
    elif view == "T2":
        if not has_tier2:
            notes.append("T2=T1")
    elif view == "T3":
        if audited:
            notes.append(AUDITED_TABLE_NOTE.format(n=audited_steps))
            if not has_tier2:
                notes.append("T2=T1")
        elif plot_has_steps:
            notes.append(PLOT_STEPS_NOTE if has_tier2 else PLOT_STEPS_NOTE_NO_TIER2)
        else:
            notes.append("T3=T2" if has_tier2 else "T3=T2=T1")
    if preview_filters and mode == "exploration":
        notes.append(f"{preview_filters} preview filter(s) on, not saved; they change this table only, never a plot")
    return ViewBadge(view=view, label=label, notes=tuple(notes), tone="audited" if audited else "plain")


def plot_badge(mode: str, plot_has_steps: bool, has_tier2: bool, preview_filters: int = 0, audited_steps: int = 0) -> ViewBadge:
    """The badge of a plot. In Exploration the plot is the Result (D-0019, D-0180): never changed by an exploration filter. In Audit mode it
    is the audited plot: the Result plus the audited steps of this plot (Apply-gated)."""
    if mode == "audit":
        if audited_steps:
            return ViewBadge("PLOT", "Plot: Audited", (f"{audited_steps} audited step(s) on this plot",), "audited")
        return ViewBadge("PLOT", "Plot: Audited", ("no audited step for this plot yet: identical to the Result",), "plain")
    notes: list[str] = []
    if plot_has_steps:
        notes.append("drawn from " + (PLOT_STEPS_NOTE if has_tier2 else PLOT_STEPS_NOTE_NO_TIER2))
    if preview_filters:
        notes.append(f"{preview_filters} preview filter(s) change the table only; this plot is not changed")
    return ViewBadge("PLOT", "Plot: Result", tuple(notes), "plain")
