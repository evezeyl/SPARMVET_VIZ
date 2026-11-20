"""
@deps
provides: function:build_plan, function:collections_of, function:run_opening, function:plot_render_recipe, function:draw_plot_proof, function:progress_text, function:opening_signature, function:large_plot_warning, class:BuildItem, class:OpeningResult, constant:LARGE_PLOT_ROWS
consumes: app/modules/orchestrator.py (materialize_tier1, materialize_tier2, materialize_tier3), app/modules/cache_keys.py (DataAnalysisRecipeKeys), app/modules/build_failure.py (short_engine_text), libs/utils/src/utils/recipe_tiers.py (plot_entries, tier2_steps, tier3_steps), libs/viz_factory/src/viz_factory/checked_plot.py (draw_checked), libs/utils/src/utils/engines.py (plot_engine_slot)
consumed_by: app/handlers/opening_handlers.py, app/handlers/home_theater.py (plot_render_recipe: the recipe HOME draws a plot from), app/tests/test_opening_build.py
doc: .claude/knowledge/decision_ledger.md (D-0326, D-0343, D-0335, D-0334, D-0336, D-0327), .claude/rules/rules_data_engine.md, .claude/rules/rules_data_analysis_recipe_structure.md#11
@end_deps

The opening of a recipe in HOME: everything is built and stored by key before the user works (D-0326), no Shiny.

What opening does, in order (`build_plan`, ONE function: a later piece that needs "the plan of every place" reads the same list):
1. the Tier 1 table of every collection (every join, and every table a plot reads directly);
2. the Tier 2 table of every collection that has tier-2 steps (a collection without them has T2 = T1: nothing extra is stored);
3. the Tier 3 table of every plot that has tier-3 steps of its own (D-0343; a plot without them reads its Tier 2: T3 = T2, nothing extra);
4. every plot drawn once, from its table, with the code HOME draws it with (D-0335): the proof that it draws. The picture is not stored.

A step that cannot be built, or a plot that cannot be drawn, refuses the recipe with a plain reason that names the table, tier and step or the plot
(D-0326, D-0327): `OpeningResult.problems`. The caller decides what a refusal does (HOME shows the recipe like one that failed the load gate).
A later opening with equal keys builds nothing: each table is read from its stored file while its key matches (the orchestrator's own rule).

This module builds. It does not know Shiny, the gate or the screen: the progress is a callback, the drawing is a callable.
"""
from __future__ import annotations

import gc
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Callable, Iterable, Optional

import polars as pl

from app.modules.build_failure import short_engine_text
from utils.recipe_tiers import plot_entries, tier2_steps, tier3_steps

# The number of rows a plot receives above which the app warns in plain words; nothing is refused (D-0336). The value is decided: 1,000,000 rows per plot
# (D-0363, "provisional value is large enough"); the warning fires ABOVE it (more than 1,000,000), not at it. The TEXT of the warning (`large_plot_warning`)
# is PROVISIONAL. The one place of the number.
LARGE_PLOT_ROWS = 1_000_000

TIER1, TIER2, TIER3, PLOT = "tier1", "tier2", "tier3", "plot"
TABLE_KINDS = (TIER1, TIER2, TIER3)


@dataclass(frozen=True)
class BuildItem:
    """One thing the opening builds. `ident` is the table (tier 1, tier 2) or the plot (tier 3, plot); `key` is the key the stored table carries (for a
    plot: the key of the table it reads); `target` is the table a plot reads."""
    kind: str
    ident: str
    key: str
    target: Optional[str] = None

    @property
    def is_table(self) -> bool:
        return self.kind in TABLE_KINDS


def collections_of(raw: dict) -> list[str]:
    """Every collection the recipe stores: its joins in the order written, then every table a plot reads directly, in plot order."""
    found = list(dict.fromkeys(list((raw.get("joins") or {}).keys())))
    for entry in plot_entries(raw).values():
        target = entry.get("target_dataset")
        if target and target not in found:
            found.append(target)
    return found


def build_plan(raw: dict, keys) -> list[BuildItem]:
    """The list of everything the opening builds, in the order it is built, with the key of each (D-0326, D-0343, D-0335).

    Tier 1 of every collection, then Tier 2 of those with tier-2 steps, then Tier 3 of the plots with tier-3 steps of their own, then every plot. A
    collection or plot without steps of a tier has no item of that tier: its table IS the table before it (T2 = T1, T3 = T2), so nothing extra is built or
    stored. `keys` is the `DataAnalysisRecipeKeys` of the recipe, computed once by the caller."""
    collections = collections_of(raw)
    plots = plot_entries(raw)
    plan = [BuildItem(TIER1, c, keys.tier1_key_of(c)) for c in collections]
    plan += [BuildItem(TIER2, c, keys.tier2_key_of(c)) for c in collections if tier2_steps(raw, c)]
    plan += [BuildItem(TIER3, p, _plot_key(keys, p), e.get("target_dataset")) for p, e in plots.items() if tier3_steps(raw, p)]
    plan += [BuildItem(PLOT, p, _plot_key(keys, p), e.get("target_dataset")) for p, e in plots.items()]
    return plan


def _plot_key(keys, plot_id: str) -> str:
    try:
        return keys.plot_key_of(plot_id)
    except KeyError:   # a plot whose target the recipe does not name: it has no key; its build says why
        return ""


def opening_signature(recipe_id: str, keys) -> tuple:
    """What an opening was done for: the recipe, its files and the data. A later opening with the same signature has nothing to build."""
    return (recipe_id, keys.data_analysis_recipe_sha256, keys.data_batch_hash)


def progress_text(recipe_id: str, tables_done: int, tables_total: int, plots_done: int, plots_total: int) -> str:
    """The progress line in plain words, PROVISIONAL wording (D-0334): "Opening 'x': tables 12 of 24, plots 5 of 17"."""
    return f"Opening '{recipe_id}': tables {tables_done} of {tables_total}, plots {plots_done} of {plots_total}"


def large_plot_warning(plot_id: str, rows: int, limit: int) -> str:
    """The warning text, PROVISIONAL wording (D-0336): the plot receives very many rows; nothing is refused."""
    return (f"The plot '{plot_id}' receives {rows:,} rows (more than {limit:,}). Drawing it may take long and use much memory; nothing is refused. "
            f"Suggestion: count or aggregate in the recipe first (a tier-2 step of its table or a tier-3 step of the plot), so the plot receives fewer rows.")


@dataclass
class OpeningResult:
    """What the opening found. `problems` are plain sentences: a recipe with one is refused. `warnings` do not refuse. `inputs_changed` are the
    orchestrator's notices (a table built while its inputs changed was returned and not stored)."""
    problems: list = field(default_factory=list)
    warnings: list = field(default_factory=list)
    inputs_changed: list = field(default_factory=list)
    tables_done: int = 0   # tables of the plan that were gone through (built, or read because their stored file carries their key): the count follows the plan

    @property
    def ok(self) -> bool:
        return not self.problems


def plot_render_recipe(raw: dict, plot_id: str, spec: dict) -> dict:
    """The recipe HOME hands the plot engine to draw `plot_id`: the plot entry, the recipe's `plot_defaults` and its plot engine. The one place that makes
    it: HOME's plot, the comparison pane and the opening's proof of drawing all call this."""
    import copy
    from utils.engines import plot_engine_slot
    return {"plots": {plot_id: copy.deepcopy(spec)}, "plot_defaults": raw.get("plot_defaults", {}), **plot_engine_slot(raw)}


def draw_plot_proof(viz_factory, raw: dict, plot_id: str, lf: pl.LazyFrame) -> None:
    """Draw the plot once from its table and discard the picture (D-0335): raises the plot engine's own error when it cannot be drawn.

    The same build as HOME's plot (`plot_render_recipe`, `viz_factory.render`) and the one checked draw (`draw_checked`: every failure is the one error form that
    names the plot and the layer). The figure is closed at once: nothing is stored and memory is given back before the next plot."""
    from viz_factory.checked_plot import draw_checked
    figure = draw_checked(viz_factory.render(lf, plot_render_recipe(raw, plot_id, plot_entries(raw)[plot_id]), plot_id), plot_id)
    try:
        import matplotlib.pyplot as plt
        plt.close(figure)
    finally:
        del figure
        gc.collect()


def _plain(error: BaseException) -> str:
    """A build error as one plain sentence: its text and its tip (the engine's plan is left out)."""
    text = short_engine_text(error, limit=900)
    tip = getattr(error, "tip", None)
    return f"{text} {tip}".strip() if tip and str(tip) not in text else text


def _plot_problem(plot_id: str, error: BaseException) -> str:
    text = _plain(error)
    return text if f"'{plot_id}'" in text else f"The plot '{plot_id}' cannot be drawn: {text}"


def run_opening(orchestrator, recipe_id: str, raw: dict, keys, anchors_dir: Path, *, draw: Callable[[str, pl.LazyFrame], None],
                progress: Optional[Callable[[int, int, int, int], None]] = None, large_rows: Optional[int] = None,
                plan: Optional[Iterable[BuildItem]] = None) -> OpeningResult:
    """Build every item of the plan, in order, and say what was found.

    Each table is built by the orchestrator through its own `materialize_*` with the keys handed in (computed once by the caller), so a table whose stored
    file carries its key is read, not built. A table that fails is not retried by anything that depends on it: its dependants are skipped (their reason is
    the one already told). A plot is drawn with `draw(plot_id, table)`, which raises when it cannot. `progress(tables_done, tables_total, plots_done,
    plots_total)` is called after every item; the counts are from the plan.

    A failure of an item is a problem of the recipe (`result.problems`), whatever its kind: the engine's own error is turned into one plain sentence.
    Only `Exception` is caught: an interrupt stops the opening."""
    large_rows = LARGE_PLOT_ROWS if large_rows is None else large_rows   # read when called, so that one change of the constant is the change everywhere
    result = OpeningResult()
    items = list(plan) if plan is not None else build_plan(raw, keys)
    tables_total = sum(1 for i in items if i.is_table)
    plots_total = sum(1 for i in items if i.kind == PLOT)
    done_tables = done_plots = 0
    failed_tables: set = set()
    failed_plots: set = set()
    anchors_dir = Path(anchors_dir)
    told = lambda change: result.inputs_changed.append(change.text)   # noqa: E731

    if progress:
        progress(0, tables_total, 0, plots_total)
    for item in items:
        try:
            if item.kind == TIER1:
                orchestrator.materialize_tier1(recipe_id, item.ident, anchors_dir / f"{item.ident}.parquet", keys=keys, on_inputs_changed=told)
            elif item.kind == TIER2:
                if item.ident not in failed_tables:
                    orchestrator.materialize_tier2(recipe_id, item.ident, anchors_dir / f"{item.ident}.parquet", keys=keys, on_inputs_changed=told)
            elif item.kind == TIER3:
                if item.target not in failed_tables:
                    orchestrator.materialize_tier3(recipe_id, item.ident, anchors_dir, keys=keys, on_inputs_changed=told)
            else:
                if item.target not in failed_tables and item.ident not in failed_plots:
                    table = orchestrator.materialize_tier3(recipe_id, item.ident, anchors_dir, keys=keys, on_inputs_changed=told)
                    rows = _row_count(table)
                    if rows is not None and rows > large_rows:
                        result.warnings.append(large_plot_warning(item.ident, rows, large_rows))
                    draw(item.ident, table)
        except Exception as error:
            if item.kind == PLOT:
                result.problems.append(_plot_problem(item.ident, error))
            else:
                result.problems.append(_plain(error))
            if item.kind == TIER1 or item.kind == TIER2:
                failed_tables.add(item.ident)
            elif item.kind == TIER3:
                failed_plots.add(item.ident)
        if item.is_table:
            done_tables += 1
            result.tables_done = done_tables
        else:
            done_plots += 1
        if progress:
            progress(done_tables, tables_total, done_plots, plots_total)
    return result


def _row_count(table: pl.LazyFrame) -> Optional[int]:
    """The rows of a plot's table, read from the stored file without reading its columns; None when it cannot be counted (the draw then says why)."""
    try:
        return int(table.select(pl.len()).collect().item())
    except Exception:
        return None
