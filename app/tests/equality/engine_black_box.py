"""Run the engine on a recipe as a black box and return the tables it builds (EQUALITY-CHECK-1, PROVISIONAL).

Same calls as `assets/scripts/golden_baseline.py`: `DataOrchestrator.materialize_tier1/2` for a table and
`VizFactory().render` for a plot. Nothing is read from inside the engine. A table or plot that fails is returned as
the exception, so a test can say what the engine did instead of crashing the collection.
"""
import contextlib
import copy
import io
import shutil
import tempfile
from dataclasses import dataclass, field
from pathlib import Path

import polars as pl

from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.orchestrator import DataOrchestrator
from utils.config_loader import ConfigManager
from viz_factory.viz_factory import VizFactory

RAW_DATA = Path("assets/test_data")


@dataclass
class EngineResult:
    t1: dict[str, "pl.DataFrame | BaseException"] = field(default_factory=dict)
    t2: dict[str, "pl.DataFrame | BaseException"] = field(default_factory=dict)
    plots: dict[str, object] = field(default_factory=dict)  # a plotnine ggplot, or the exception
    log: str = ""  # what the engine printed while it worked (for FINDINGS: did it tell the user anything?)


def run_engine(recipes_dir: Path, recipe_id: str, tables: list[str], plots: dict[str, str]) -> EngineResult:
    """Tier 1 and tier 2 of every named table, and every plot (plot id -> its target table), by the orchestrator."""
    import matplotlib
    matplotlib.use("Agg")
    result = EngineResult()
    clear_data_analysis_recipe_cache()
    work = Path(tempfile.mkdtemp(prefix="equality_"))
    sink = io.StringIO()
    try:
        with contextlib.redirect_stdout(sink), contextlib.redirect_stderr(sink):
            raw = ConfigManager(str(recipes_dir / f"{recipe_id}.yaml")).raw_config
            orchestrator = DataOrchestrator(recipes_dir, RAW_DATA)
            keys = orchestrator.compute_data_analysis_recipe_keys(recipe_id)
            lazy: dict[str, pl.LazyFrame] = {}
            for name in tables:
                anchor = work / f"{name}.parquet"
                try:
                    result.t1[name] = orchestrator.materialize_tier1(recipe_id, name, anchor, keys=keys).collect()
                    lazy[name] = orchestrator.materialize_tier2(recipe_id, name, anchor, keys=keys)
                    result.t2[name] = lazy[name].collect()
                except BaseException as exc:  # noqa: BLE001 - what the engine does is the result
                    result.t1.setdefault(name, exc)
                    result.t2.setdefault(name, exc)
            for plot_id, target in plots.items():
                if target not in lazy:
                    result.plots[plot_id] = RuntimeError(f"no table {target}")
                    continue
                try:
                    result.plots[plot_id] = VizFactory().render(lazy[target], raw, plot_id)
                except BaseException as exc:  # noqa: BLE001
                    result.plots[plot_id] = exc
    finally:
        shutil.rmtree(work, ignore_errors=True)
    result.log = sink.getvalue()
    return result


def built(plot) -> dict:
    """Build a copy of a plotnine plot and return what it computed: labels, one frame per layer, the panels."""
    clone = copy.deepcopy(plot)
    clone._build()
    return {
        "labels": {k: v for k, v in vars(clone.labels).items() if v is not None},
        "layers": [pl.from_pandas(layer.data.reset_index(drop=True)) for layer in clone.layers],
        "geoms": [type(layer.geom).__name__ for layer in clone.layers],
        "panels": pl.from_pandas(clone.layout.layout.reset_index(drop=True)),
    }
