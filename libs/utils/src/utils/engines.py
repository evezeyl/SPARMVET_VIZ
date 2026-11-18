"""The engines a recipe may name, stated once (ADR-106 V8).

A recipe declares `data_engine` and `plot_engine`, and a tier or a plot entry may name its own (D-0219). The app builds one of
each today: Polars for the data steps and plotnine for the plots. `ENGINE_TABLE` is the one list: the engine value, the recipe
key it fills, the library that holds it and the prefix of the names its own entries carry. The checker's allowed list (code
T06), the recipe writers, the libraries, and the app's choice of the engine all read it, so a second engine is one more row and
one more library, and an engine this app has no library for is refused with the same words everywhere (D-0239) instead of being
drawn or run by another engine.

Names only: this module imports no library. The app (`app/modules/engine_registry.py`) is the only place that imports the entry
file of each library and joins them (D-0247).

Consumed by: `utils.recipe_check` (through `spec()["engines"]`), `utils.recipe_factory`, `utils.recipe_migration`,
`viz_factory.viz_factory` (the refusal), `viz_factory.registry` and `transformer.actions.base` (the engine of each entry),
`app/modules/engine_registry.py` (the choice), `test_lab` (the recipes it writes).
If deleted: no recipe can name an engine and the checker refuses every recipe.

# @deps
# provides: constant:DATA_ENGINE, constant:PLOT_ENGINE, constant:ENGINE_TABLE, constant:ENGINES, class:EngineRow, class:DataEngineEntry, class:PlotEngineEntry, function:engines_of, function:entry_module_name, function:effective_engine, function:engine_versions, function:tier_engine, function:engine_known, function:engine_problem, function:engine_error, function:prefix_problems, function:plot_engine_slot
# consumed_by: libs/utils/src/utils/recipe_check.py, libs/utils/src/utils/recipe_migration.py, libs/viz_factory/src/viz_factory/viz_factory.py, libs/viz_factory/src/viz_factory/registry.py,
#              libs/transformer/src/transformer/actions/base.py, app/modules/engine_registry.py,
#              libs/test_lab/src/test_lab/bootstrapper.py, libs/test_lab/src/test_lab/scaffolder.py, libs/utils/tests/test_engines.py, libs/utils/tests/test_engine_table.py
# doc: .claude/knowledge/architecture_decisions.md (ADR-106 V8, ADR-100), .claude/knowledge/decision_ledger.md (D-0219, D-0238, D-0239, D-0247)
# @end_deps
"""
from dataclasses import dataclass
from typing import Any, Callable, Dict, Iterable, Optional, Tuple

DATA_ENGINE = "python-polars"
PLOT_ENGINE = "python-plotnine"


@dataclass(frozen=True)
class EngineRow:
    """One engine the app has: the value a recipe writes, the key it fills, its library and its name prefix."""
    engine: str
    key: str       # "data_engine" or "plot_engine"
    library: str   # the package under libs/ that holds it; its module `engine_<value>` is the entry file (D-0247)
    prefix: str    # the prefix of the names its own entries carry (`polars_`, `plotnine_`); `modif_` and `step_` carry none (D-0238)
    packages: Tuple[str, ...] = ()   # the installed libraries behind the engine; their versions are read when the export record is written (D-0248)


ENGINE_TABLE: Tuple[EngineRow, ...] = (
    EngineRow(DATA_ENGINE, "data_engine", "transformer", "polars_", ("polars", "transformer")),
    EngineRow(PLOT_ENGINE, "plot_engine", "viz_factory", "plotnine_", ("plotnine", "matplotlib", "viz_factory")),
)


def engines_of(key: str) -> Tuple[str, ...]:
    """The engines this app has for a recipe key (`data_engine` or `plot_engine`), in table order."""
    return tuple(row.engine for row in ENGINE_TABLE if row.key == key)


# key of a recipe -> the engines built for it (derived: the table is the one list)
ENGINES = {key: engines_of(key) for key in ("data_engine", "plot_engine")}


def engine_versions(engine: str) -> Optional[Dict[str, str]]:
    """{library: installed version} of the libraries behind an engine, read from the installed packages at the moment it is asked
    (never typed in); a library that is not installed says "unknown". None for an engine the app has no row for (D-0248)."""
    from importlib import metadata
    for row in ENGINE_TABLE:
        if row.engine == engine:
            found = {}
            for package in row.packages:
                try:
                    found[package] = metadata.version(package)
                except metadata.PackageNotFoundError:
                    found[package] = "unknown"
            return found
    return None


def entry_module_name(engine: str) -> str:
    """The module that names an engine and exposes ENTRY: `engine_` plus the value with `-` turned into `_` (D-0247)."""
    return "engine_" + engine.replace("-", "_")


@dataclass(frozen=True)
class DataEngineEntry:
    """What the app needs to run the tiers of a table or a join with one data engine: the class that runs a list of
    steps (and reads the steps of a tier) and the class that assembles a join."""
    engine: str
    wrangler: Any
    assembler: Any


@dataclass(frozen=True)
class PlotEngineEntry:
    """What the app needs to draw a plot with one plot engine: its factory class (built once per app with the app's settings) and
    how it says which theme a plot it drew was drawn with (`applied_theme(plot)`, for the export record, D-0248). An engine with no
    `applied_theme` records no theme, and the record says so."""
    engine: str
    factory: Callable[..., Any]
    applied_theme: Optional[Callable[[Any], Optional[dict]]] = None


def effective_engine(key: str, *levels: Any) -> Any:
    """The engine of a block: the first level that writes `key`, else None (D-0219: the block's own, then the recipe's).

    A level that writes the key with no value counts as written: its empty value is returned so the caller can refuse it;
    falling back to the next level would hide the empty line (D-0050). None when no level writes the key: the app has no
    default engine, a recipe names one (the checker requires it, T04).
    """
    for level in levels:
        if isinstance(level, dict) and key in level:
            return level[key]
    return None


def tier_engine(recipe: Any, body: Any, tier: str) -> Any:
    """The data engine of one tier of `body` (a table, a join, or a plot entry for tier 3): the tier's own value, else the recipe's."""
    held = body.get(tier) if isinstance(body, dict) else None
    return effective_engine("data_engine", held, recipe)


def engine_known(key: str, value: Any) -> bool:
    """True when `value` is an engine this app has for `key`."""
    return isinstance(value, str) and value in ENGINES[key]


def engine_problem(key: str, value: Any) -> Optional[Tuple[str, str]]:
    """None when `value` is an engine built for `key`; else (what is wrong, how to fix it), in plain words.

    The words for a name the app has no library for are decided (D-0239): "no library for this engine in this app", with the
    engines of this app. A key with no value is told as missing, not as an unknown name.
    """
    allowed = ENGINES[key]
    if engine_known(key, value):
        return None
    fix = f"write {key}: {allowed[0]}" + (f" (one of {', '.join(allowed)})" if len(allowed) > 1 else "")
    if value is None:
        return (f"the recipe names no {key} (its value is None)", fix)
    return (f"the recipe key {key} is {value!r}: no library for this engine in this app (the engines of this app: {', '.join(allowed)})", fix)


def engine_error(key: str, value: Any, *, where: str, error: Any = None) -> Exception:
    """The refusal for a run: the recipe error (what, where, how to fix) for an engine the app cannot use.

    `where` names the block, for example "the tier1 of the table 'A'". `error` is the class of the error (the plot layer
    gives its own); the default is the recipe error, imported here so that this module stays light.
    """
    from utils.errors import DataAnalysisRecipeError
    what, fix = engine_problem(key, value) or ("the engine cannot be used", f"write {key}: {ENGINES[key][0]}")
    return (error or DataAnalysisRecipeError)(f"{where}: {what}.", tip=fix)


def prefix_problems(engine_of_name: Dict[str, str]) -> list:
    """The names whose prefix says one engine and whose field says another: [(name, engine in the field, engine of the prefix)].

    Names with no engine prefix (`modif_`, `step_`, plain plot components) are not judged by their name: they carry the engine
    in the field only (D-0238).
    """
    problems = []
    for name, engine in engine_of_name.items():
        for row in ENGINE_TABLE:
            if name.startswith(row.prefix) and engine != row.engine:
                problems.append((name, engine, row.engine))
    return problems


def plot_engine_slot(entry: Any, recipe: Any) -> dict:
    """The `plot_engine` slot to hand to the plot library for one plot: the entry's own value, else the recipe's (D-0237).

    Returns {"plot_engine": value} or {} when neither names one (library use outside a recipe means the built engine).
    The library reads the slot of the recipe dict it is given, so the caller puts this into that dict.
    """
    for level in (entry, recipe):
        if isinstance(level, dict) and "plot_engine" in level:
            return {"plot_engine": level["plot_engine"]}
    return {}
