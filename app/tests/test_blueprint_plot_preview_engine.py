"""Blueprint plot preview: the dict handed to the plot library carries the plot engine (D-0237, ADR-106 V8).

`_plot_outcome` (`app/modules/wrangle_studio.py`) builds `{"plots": {id: entry}, "plot_defaults": ..., **plot_engine_slot(recipe)}`
for `VizFactory.render`. The dict carries the recipe's default engine; the entry's own `plot_engine` travels in the entry and the dispatcher lets it win. The closure is cut out by `ast` and run with
stand-ins for the session; the recipe is loaded by the real loader, the factory is the real one behind a recorder.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_blueprint_plot_preview_engine.py -q
"""
import ast
from pathlib import Path
from types import SimpleNamespace

import polars as pl

from app.modules import wrangle_studio
from utils.recipe_factory import minimal_plot, minimal_recipe, minimal_schema, write_recipe
from app.modules.engine_registry import PlotEngines

SOURCE = Path(wrangle_studio.__file__)


class Val:
    def __init__(self, value=None):
        self.value = value

    def get(self):
        return self.value


class Recorder:
    """The real dispatcher of the app; it keeps the recipe dictionary of each render."""

    def __init__(self):
        self.factory = PlotEngines()
        self.seen = []

    def render(self, lf, recipe, plot_id, *a, **k):
        self.seen.append((recipe, plot_id))
        return self.factory.render(lf, recipe, plot_id, *a, **k)


def preview(tmp_path, entry_engine=None, recipe_engine=None):
    entry = minimal_plot("samples", {"x": "year"})
    if entry_engine is not None:
        entry["plot_engine"] = entry_engine
    recipe = minimal_recipe("tiny", schemas={"samples": minimal_schema("data/samples.tsv", {"sample_id": "String", "year": "String"},
                                                                       entity_key="sample_id")}, plots={"p1": entry})
    if recipe_engine is not None:
        recipe["plot_engine"] = recipe_engine
    path = write_recipe(tmp_path / "tiny.yaml", recipe)
    ns = dict(vars(wrangle_studio))
    cls = next(n for n in ast.parse(SOURCE.read_text()).body if isinstance(n, ast.ClassDef) and n.name == "WrangleStudio")
    define = next(n for n in cls.body if isinstance(n, ast.FunctionDef) and n.name == "define_server")
    fn = next(n for n in ast.walk(define) if isinstance(n, ast.FunctionDef) and n.name == "_plot_outcome")
    fn.decorator_list = []
    exec(compile(ast.fix_missing_locations(ast.Module(body=[fn], type_ignores=[])), "_plot_outcome", "exec"), ns)
    recorder = Recorder()
    frame = pl.DataFrame({"sample_id": ["a", "b", "c"], "year": ["2023", "2023", "2024"]})
    ns.update(self=SimpleNamespace(active_viz_id=Val("p1"), active_data_analysis_recipe_path=Val(str(path))),
              processed_data_surgical=lambda: frame, processed_data=lambda: frame, viz_factory=recorder,
              input=SimpleNamespace(sidebar_nav=lambda: "Wrangle Studio"))  # BLUEPRINT is the open user space
    return ns["_plot_outcome"](), recorder


def test_the_dict_for_the_factory_holds_the_plot_entry_the_defaults_and_the_recipe_plot_engine(tmp_path):
    (figure, error), recorder = preview(tmp_path)
    assert error == "" and figure is not None
    (given, plot_id), = recorder.seen
    assert plot_id == "p1"
    assert set(given) == {"plots", "plot_defaults", "plot_engine"}
    assert given["plot_engine"] == "python-plotnine"                       # the recipe's engine (the writer's default)
    assert given["plots"]["p1"]["target_dataset"] == "samples" and "spec" not in given["plots"]["p1"]


def test_the_engine_written_on_the_plot_entry_wins_over_the_one_of_the_recipe(tmp_path):
    (figure, error), recorder = preview(tmp_path, entry_engine="python-plotnine", recipe_engine="some-other-engine")
    assert error == "" and figure is not None, "the dispatcher draws it with the plot's own engine, not the recipe's unknown one"
    assert recorder.seen[0][0]["plot_engine"] == "some-other-engine", "the dict carries only the recipe's default"
    assert recorder.seen[0][0]["plots"]["p1"]["plot_engine"] == "python-plotnine"


def test_an_engine_the_app_does_not_build_is_told_in_the_place_of_the_plot_not_drawn_with_another(tmp_path):
    (figure, error), recorder = preview(tmp_path, entry_engine="python-matplotlib-not-built")
    assert figure is None
    assert "plot_engine" in error and "python-matplotlib-not-built" in error
    assert recorder.seen[0][0]["plots"]["p1"]["plot_engine"] == "python-matplotlib-not-built"
