"""The recipe names plot engine X at the top, one plot entry names engine Y: the plot is drawn by Y, from the callers (D-0237).

The dispatcher `PlotEngines.render` alone chooses between the entry's own engine and the recipe's default. The small recipe
dictionary a caller builds carries the recipe's default (`plot_engine_slot`) and the entry in `plots`. These tests run the
dictionary of HOME (both builders, cut from the source with `ast`) and the real generator of the export through the real
dispatcher with a stand-in engine, so a dispatcher that ignores the entry's own engine fails here (before, the caller's slot
repeated the own engine and hid that break).

# @deps
# consumes: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/engine_registry.py, app/tests/test_export_download_path.py, app/tests/test_cache_chain.py
# doc: .claude/knowledge/decision_ledger.md (D-0237, D-0219)
# @end_deps
"""
import ast
import copy
import io
import zipfile
from pathlib import Path

import pytest

from app.modules import engine_registry
from app.modules.cache_keys import clear_data_analysis_recipe_cache
from app.modules.engine_registry import PlotEngines, REGISTRY
from app.tests.test_cache_chain import World
from app.tests.test_export_download_path import _download_function, _fresh_cache, _run  # noqa: F401  (the autouse fixture too)
from utils import engines
from utils.engines import PlotEngineEntry
from viz_factory import VizFactory
from viz_factory.engine_python_plotnine import ENTRY

ROOT = Path(__file__).resolve().parents[2]


class Stand_in(VizFactory):
    """Draws as plotnine does, and records that it was the one asked."""
    calls = []

    def render(self, df, recipe, plot_id, **kwargs):
        Stand_in.calls.append((plot_id, recipe.get("plot_engine")))
        return super().render(df, recipe, plot_id, **kwargs)


@pytest.fixture
def stand_in(monkeypatch):
    Stand_in.calls = []
    monkeypatch.setitem(REGISTRY, "python-stand-in", PlotEngineEntry(engine="python-stand-in", factory=Stand_in,
                                                                     applied_theme=ENTRY.applied_theme))
    monkeypatch.setattr(engines, "ENGINES", {**engines.ENGINES, "plot_engine": ("python-plotnine", "python-stand-in")})


def dicts_built_by(relative):
    """Every `synthetic_data_analysis_recipe = {...}` expression of a handler file, as code to evaluate."""
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    found = [n.value for n in ast.walk(tree) if isinstance(n, ast.Assign) and isinstance(n.value, ast.Dict)
             and any(isinstance(t, ast.Name) and t.id == "synthetic_data_analysis_recipe" for t in n.targets)]
    return [compile(ast.Expression(ast.fix_missing_locations(node)), relative, "eval") for node in found]


def test_the_builders_of_home_hand_over_the_recipe_default_and_the_dispatcher_lets_the_entry_win(stand_in):
    import polars as pl
    codes = dicts_built_by("app/handlers/home_theater.py")
    assert len(codes) == 2, "HOME builds the plot dictionary in two places (plot and comparison); update this test"
    from app.handlers.home_theater import plot_engine_slot
    spec = {"plot_engine": "python-stand-in", "target_dataset": "A", "mapping": {"x": "x"}, "layers": [{"name": "geom_bar"}], "ui_label": "P"}
    frame = pl.DataFrame({"x": ["a", "b", "a"]})
    for code in codes:
        Stand_in.calls = []
        cfg = type("Cfg", (), {"raw_config": {"plot_engine": "python-plotnine", "plot_defaults": {}}})()
        recipe = eval(code, {"p_id": "p", "plot_spec": copy.deepcopy(spec), "spec": spec, "cfg": cfg, "plot_engine_slot": plot_engine_slot})
        assert recipe["plot_engine"] == "python-plotnine", "the dictionary carries the recipe's default"
        PlotEngines().render(frame, recipe, "p")
        assert Stand_in.calls == [("p", "python-stand-in")], "the plot's own engine drew it"


def test_the_export_draws_a_plot_with_the_engine_its_entry_names_not_the_recipes(tmp_path, monkeypatch, stand_in):
    world = World(tmp_path)
    recipe_file = world.data_analysis_recipes_dir / "tiny.yaml"
    text = recipe_file.read_text()
    changed = text.replace("        target_dataset: C\n", "        plot_engine: python-stand-in\n        target_dataset: C\n")
    assert changed != text, "the edit changed nothing: the test would prove nothing"
    recipe_file.write_text(changed)
    clear_data_analysis_recipe_cache()
    view = world.orch.compute_data_analysis_recipe_keys("tiny")
    yielded = _run(_download_function(world, view, [], monkeypatch))
    names = zipfile.ZipFile(io.BytesIO(yielded[0])).namelist()
    assert any(n.endswith("p.png") for n in names), names
    assert Stand_in.calls and Stand_in.calls[0][0] == "p", "the stand-in engine of the plot entry drew it"
