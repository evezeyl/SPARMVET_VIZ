"""The recipe names plot engine X at the top, one plot entry names engine Y: the plot is drawn by Y, from the callers (D-0237).

The dispatcher `PlotEngines.render` alone chooses between the entry's own engine and the recipe's default. The small recipe
dictionary a caller builds carries the recipe's default (`plot_engine_slot`) and the entry in `plots`. These tests run the
dictionary of HOME (built by `opening_build.plot_render_recipe`, which HOME calls in both places, checked with `ast`) and the real generator of the export through the real
dispatcher with a stand-in engine, so a dispatcher that ignores the entry's own engine fails here (before, the caller's slot
repeated the own engine and hid that break).

# @deps
# consumes: app/modules/opening_build.py (plot_render_recipe), app/handlers/home_theater.py, app/handlers/export_handlers.py, app/modules/engine_registry.py, app/tests/test_export_download_path.py, app/tests/test_cache_chain.py
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


def home_calls_the_one_builder(relative):
    """The number of calls of `plot_render_recipe` in a handler file: HOME draws a plot in two places (plot and comparison pane)."""
    tree = ast.parse((ROOT / relative).read_text(encoding="utf-8"))
    return [n for n in ast.walk(tree) if isinstance(n, ast.Call) and getattr(n.func, "id", None) == "plot_render_recipe"]


def test_the_builder_of_home_hands_over_the_recipe_default_and_the_dispatcher_lets_the_entry_win(stand_in):
    import polars as pl
    from app.modules.opening_build import plot_render_recipe
    assert len(home_calls_the_one_builder("app/handlers/home_theater.py")) == 2, \
        "HOME builds the plot dictionary in two places (plot and comparison) through plot_render_recipe; update this test"
    spec = {"plot_engine": "python-stand-in", "target_dataset": "A", "mapping": {"x": "x"}, "layers": [{"name": "geom_bar"}], "ui_label": "P"}
    frame = pl.DataFrame({"x": ["a", "b", "a"]})
    Stand_in.calls = []
    recipe = plot_render_recipe({"plot_engine": "python-plotnine", "plot_defaults": {}}, "p", copy.deepcopy(spec))
    assert recipe["plot_engine"] == "python-plotnine", "the dictionary carries the recipe's default"
    assert recipe["plots"]["p"]["plot_engine"] == "python-stand-in", "the entry keeps its own engine"
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
