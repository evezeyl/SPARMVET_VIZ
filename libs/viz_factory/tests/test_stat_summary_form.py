"""stat_summary and stat_summary_bin offer only what a recipe can use (VIZ-FOLLOWUPS-1, item 4).

plotnine takes `fun_y`, `fun_ymin` and `fun_ymax` as Python functions, which a recipe cannot hold (`fun_y: mean` is refused:
"'mean' is not a callable object"), so the form does not offer them and says why; the summary is chosen with `fun_data`
(a name such as mean_se). The `yaml_example` of each draws summary marks, not an empty plot.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_stat_summary_form.py -q
"""
import matplotlib
import numpy as np
import polars as pl
import pytest
import yaml
from matplotlib import pyplot as plt

matplotlib.use("Agg")

import viz_factory  # noqa: F401
from viz_factory.registry import COMPONENT_SCHEMAS
from viz_factory.viz_factory import VizFactory, draw_checked

NAMES = ["stat_summary", "stat_summary_bin"]
_rng = np.random.RandomState(2)
TABLE = pl.DataFrame({"x": _rng.rand(30) * 100, "y": _rng.rand(30) * 100})


@pytest.mark.parametrize("name", NAMES)
def test_the_form_does_not_offer_a_function_parameter(name):
    schema = COMPONENT_SCHEMAS[name]
    assert not {"fun_y", "fun_ymin", "fun_ymax"} & set(schema["params"])
    assert set(schema["not_exposed"]) >= {"fun_y", "fun_ymin", "fun_ymax"}
    assert "fun_data" in schema["params"]


@pytest.mark.parametrize("name", NAMES)
def test_the_example_draws_summary_marks(name):
    layers = yaml.safe_load(COMPONENT_SCHEMAS[name]["yaml_example"])["layers"]
    plot = VizFactory().render(TABLE, {"plots": {"p": {"mapping": {"x": "x", "y": "y"}, "layers": layers}}}, "p")
    figure = draw_checked(plot)
    marks = sum(len(a.collections) + len(a.lines) for a in figure.axes)
    plt.close(figure)
    assert marks > 0
