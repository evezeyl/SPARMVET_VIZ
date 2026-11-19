"""@deps
provides: function:engine_record, function:failed_plot_record, constant:NOT_RUN
consumes: libs/utils/src/utils/engines.py (tier_engine, effective_engine, engine_versions: the functions the run chooses with), libs/utils/src/utils/recipe_tiers.py (collection_body, step_list)
consumed_by: app/handlers/export_handlers.py, app/tests/test_engine_record.py
doc: .claude/knowledge/decision_ledger.md (D-0248, D-0258, D-0219), .claude/rules/ui_implementation_contract.md#7.2
@end_deps

The `engines` part of `effective_run.yaml` (D-0248), headless, no Shiny.

The Publication export carries no recipe, so this record is the only place the engine of an export is written. It holds:
- `recipe_default`: the `data_engine` and `plot_engine` the recipe writes at its top (None when it writes none: no default is invented);
- `tables`: every table and join the plots of the export read, with the engine of each tier that ran (the tier 1 of the
  ingredients of a join too: a join reads the tier 1 of its ingredients, their tier 2 did not run);
- `plots`: per plot the engine it was drawn with, whether it was drawn, the theme as it was applied (or why none is recorded); and, only
  for a plot that writes `tier3` steps, `tier3`: the data engine that ran them (a plot with none reads its table as it is: nothing ran);
- `library_versions`: per engine that appears, the installed versions of the libraries behind it, read when the record is made.

One source: the engine of a tier is `utils.engines.tier_engine`, the function `DataOrchestrator` chooses the entry with; the engine
of a plot and its theme come from `PlotEngines.record_of`, taken from the plot that was drawn; this module reads the recipe text
for nothing else than which tables the plots read and which tier-2 lists have steps.
"""
from typing import Any, Dict, Iterable, Tuple

from utils import engines
from utils.recipe_tiers import collection_body, step_list

# What the tier 2 of a collection with no steps is recorded as: nothing ran, T2 equals T1 (the words of the README of the export).
NOT_RUN = "none (T2 equals T1)"


def failed_plot_record(raw: dict, entry: Any, exc: BaseException) -> dict:
    """The record of a plot that was not drawn: its engine as the dispatcher reads it (the entry's own, else the recipe's, as
    written, also when the app has no library for it), no theme, and the first line of the reason."""
    first = (str(exc).strip().splitlines() or [type(exc).__name__])[0]
    return {"plot_engine": engines.effective_engine("plot_engine", entry, raw), "drawn": False, "theme": None, "not_drawn_because": first}


def _table_record(raw: dict, collection_id: str, body: Any) -> dict:
    """The engines of the tiers of one collection that was plotted: tier 1, and tier 2 when it has steps."""
    kind = "join" if isinstance(raw.get("joins"), dict) and collection_id in raw["joins"] else "table"
    return {"kind": kind, "tier1": engines.tier_engine(raw, body, "tier1"),
            "tier2": engines.tier_engine(raw, body, "tier2") if step_list(body, "tier2") else NOT_RUN}


def _ingredients(join: Any) -> Iterable[str]:
    for item in (join.get("ingredients") or []) if isinstance(join, dict) else []:
        ingredient = item.get("dataset_id") if isinstance(item, dict) else item
        if ingredient:
            yield ingredient


def engine_record(raw: dict, plots: Iterable[Tuple[str, Any]], drawn: Dict[str, dict]) -> dict:
    """The `engines` record of one export.

    `raw` is the resolved recipe, `plots` the (plot id, plot entry) of the export in scope, `drawn` the record of each plot that was
    attempted (`PlotEngines.record_of` for a plot that was drawn, `failed_plot_record` for one that was not). A plot of the scope
    that is in no record is shown as not drawn: nothing is left out silently (D-0050).
    """
    plots = list(plots)
    tables: Dict[str, dict] = {}
    for _plot_id, entry in plots:
        target = entry.get("target_dataset") if isinstance(entry, dict) else None
        body = collection_body(raw, target) if target else None
        if body is not None and target not in tables:
            tables[target] = _table_record(raw, target, body)
    for collection_id, record in list(tables.items()):
        if record["kind"] != "join":
            continue
        for ingredient in _ingredients(raw["joins"][collection_id]):
            if ingredient not in tables:
                tables[ingredient] = {"kind": "table", "tier1": engines.tier_engine(raw, collection_body(raw, ingredient), "tier1")}

    plot_records: Dict[str, dict] = {}
    for plot_id, entry in plots:
        plot_records[plot_id] = dict(drawn.get(plot_id) or {
            "plot_engine": engines.effective_engine("plot_engine", entry, raw), "drawn": False, "theme": None,
            "not_drawn_because": "it was not attempted in this export"})
        if step_list(entry, "tier3"):
            plot_records[plot_id]["tier3"] = engines.tier_engine(raw, entry, "tier3")

    used = []
    for record in tables.values():
        used += [record["tier1"]] + ([record["tier2"]] if record.get("tier2") not in (None, NOT_RUN) else [])
    used += [record["plot_engine"] for record in plot_records.values()]
    used += [record["tier3"] for record in plot_records.values() if "tier3" in record]
    versions: Dict[str, Any] = {}
    for engine in used:
        found = engines.engine_versions(engine) if isinstance(engine, str) else None
        if found is not None:
            versions[engine] = found

    return {
        "recipe_default": {"data_engine": raw.get("data_engine"), "plot_engine": raw.get("plot_engine")},
        "tables": tables,
        "plots": plot_records,
        "library_versions": versions,
    }
