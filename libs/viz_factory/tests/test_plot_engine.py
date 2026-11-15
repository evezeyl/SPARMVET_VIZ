"""The factory refuses a plot engine it does not implement, and still renders with none given (ADR-106 V8).

# @deps
# consumes: libs/viz_factory/src/viz_factory/viz_factory.py (VizFactory.render), libs/utils/src/utils/engines.py
# @end_deps
"""
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from utils.engines import PLOT_ENGINE
from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1, 2, 3], "y": [3, 1, 2]})
PLOT = {"mapping": {"x": "x", "y": "y"}, "layers": [{"name": "geom_point"}]}


def recipe(**more):
    return {"plots": {"p": PLOT}, "plot_defaults": {}, **more}


def test_a_render_with_no_engine_given_works():
    assert VizFactory().render(DF, recipe(), "p") is not None


def test_a_render_with_the_implemented_engine_works():
    assert VizFactory().render(DF, recipe(plot_engine=PLOT_ENGINE), "p") is not None


@pytest.mark.parametrize("engine", ["python-ggplot2", "python-matplotlib", "", None, 3, "Python-Plotnine"])
def test_an_engine_the_factory_does_not_implement_is_refused_with_a_plain_message(engine):
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, recipe(plot_engine=engine), "p")
    text = str(error.value)
    assert repr(engine) in text, "what: the engine that was asked for"
    assert "plot_engine" in text and "'p'" in text, "where: the recipe key and the plot"
    assert PLOT_ENGINE in error.value.tip, "how to fix: the engine that is built"
    assert error.value.pipeline_error is not None
    assert error.value.pipeline_error.who == "data_analysis_recipe_author"


def test_the_refusal_comes_before_the_plot_is_looked_up():
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, {"plots": {}, "plot_engine": "python-ggplot2"}, "missing")
    assert "plot_engine" in str(error.value)
