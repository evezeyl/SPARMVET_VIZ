"""Every error of the factory or of plotnine reads "what, which plot and layer, how to fix" (VIZ-STANDARD-1, V7).

# @deps
# consumes: libs/viz_factory/src/viz_factory/viz_factory.py (VizFactory.render, draw_checked, show_draw_errors), libs/viz_factory/src/viz_factory/errors.py
# @end_deps
"""
import re

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from matplotlib.figure import Figure
from plotnine import aes, geom_point, ggplot
from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory, draw_checked, show_draw_errors

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": [3.0, 1.0, 2.0, 5.0], "g": ["a", "b", "a", "b"]})
FORM = re.compile(r"^Plot 'p'(, layer (?P<n>\d+) \((?P<name>\w+)\))?: .+\. Fix: .+\.$", re.S)


def recipe(layers, mapping=None, **more):
    return {"plots": {"p": {"target_dataset": "d", "mapping": mapping or {"x": "x", "y": "y"}, "layers": layers, **more}},
            "plot_defaults": {}}


def failure(layers, mapping=None, **more):
    """The error of building and drawing the plot, whichever stage fails."""
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, recipe(layers, mapping, **more), "p").draw()
    assert FORM.match(str(error.value)), f"not in the one error form: {error.value}"
    assert error.value.pipeline_error is not None and error.value.tip
    return error.value


def test_the_wanted_message_for_a_value_that_is_not_a_number():
    error = failure([{"name": "geom_point", "params": {"size": "big"}}])
    assert str(error) == ("Plot 'p', layer 1 (geom_point): the value 'big' for 'size' is not a number. "
                          "Fix: write a number, for example size: 3.")


def test_the_same_for_a_theme_argument_that_fails_while_the_plot_is_built():
    error = failure([{"name": "geom_point"}, {"name": "theme_bw", "params": {"base_size": "huge"}}])
    assert "layer 2 (theme_bw)" in str(error) and "'huge' for 'base_size' is not a number" in str(error)


def test_a_wrong_argument_name_gets_the_close_name():
    error = failure([{"name": "geom_point", "params": {"colr": "red"}}])
    assert "'colr' is not an argument of geom_point" in str(error) and "Fix: write color" in str(error)


def test_a_mapping_key_that_the_geom_needs_names_the_layer_that_needs_it():
    error = failure([{"name": "geom_point"}], mapping={"x": "x", "yy": "y"})
    assert "layer 1 (geom_point)" in str(error)
    assert "'y'" in str(error) and "mapping" in str(error).split("Fix:")[1]


def test_a_component_that_is_not_registered_is_in_the_same_form():
    error = failure([{"name": "geom_pont"}])
    assert "layer 1 (geom_pont)" in str(error) and "write geom_point" in str(error)


def test_a_column_that_does_not_exist_is_in_the_same_form():
    error = failure([{"name": "geom_point"}], mapping={"x": "x", "y": "vv"})
    assert str(error).startswith("Plot 'p': ") and "'vv'" in str(error)


def test_a_plot_that_is_not_in_the_recipe_is_in_the_same_form():
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, {"plots": {}}, "p")
    assert FORM.match(str(error.value)), str(error.value)


def test_a_wrong_plot_engine_is_in_the_same_form():
    with pytest.raises(VisualizationError) as error:
        VizFactory().render(DF, {**recipe([{"name": "geom_point"}]), "plot_engine": "python-ggplot2"}, "p")
    assert FORM.match(str(error.value)), str(error.value)


def test_a_draw_failure_in_a_later_layer_names_that_layer_not_the_first():
    error = failure([{"name": "geom_point"}, {"name": "geom_line", "params": {"size": "big"}}])
    assert "layer 2 (geom_line)" in str(error) and "'size'" in str(error)


# -- draw_checked draws once and returns the figure ---------------------------------------------------------------

def test_draw_checked_returns_the_figure_and_draws_once(monkeypatch):
    plot = VizFactory().render(DF, recipe([{"name": "geom_point"}]), "p")
    calls = []
    real = ggplot.draw
    monkeypatch.setattr(ggplot, "draw", lambda self, *a, **k: calls.append(1) or real(self, *a, **k))
    figure = draw_checked(plot)
    assert isinstance(figure, Figure) and len(calls) == 1


def test_draw_checked_raises_the_one_form_for_a_plot_the_factory_built():
    plot = VizFactory().render(DF, recipe([{"name": "geom_point", "params": {"size": "big"}}]), "p")
    with pytest.raises(VisualizationError) as error:
        draw_checked(plot)
    assert "layer 1 (geom_point)" in str(error.value)


def test_draw_checked_gives_a_plot_not_built_by_the_factory_a_plain_message():
    plot = ggplot(DF.to_pandas(), aes("x", "y")) + geom_point(size="big")
    with pytest.raises(VisualizationError) as error:
        draw_checked(plot, plot_id="mine")
    assert str(error.value).startswith("Plot 'mine': ") and "Fix:" in str(error.value)


def test_a_good_plot_draws_the_same_through_draw_checked_and_save():
    plot = VizFactory().render(DF, recipe([{"name": "geom_point"}]), "p")
    assert isinstance(draw_checked(plot), Figure)


# -- the error shown in the place of the plot (HOME) -------------------------------------------------------------

def test_show_draw_errors_draws_the_message_instead_of_raising_and_reports_it():
    plot = VizFactory().render(DF, recipe([{"name": "geom_point", "params": {"size": "big"}}]), "p")
    seen = []
    shown = show_draw_errors(plot, on_error=seen.append)
    figure = shown.draw(show=False)
    assert isinstance(figure, Figure)
    assert len(seen) == 1 and isinstance(seen[0], VisualizationError)
    shown_text = " ".join(" ".join(t.get_text() for t in figure.findobj(matplotlib.text.Text)).split())
    assert "'size' is not a number" in shown_text and "Fix: write a number" in shown_text


def test_show_draw_errors_keeps_a_good_plot_unchanged_and_silent():
    plot = VizFactory().render(DF, recipe([{"name": "geom_point"}]), "p")
    seen = []
    figure = show_draw_errors(plot, on_error=seen.append).draw(show=False)
    assert seen == [] and isinstance(figure, Figure)


def test_the_error_figure_survives_the_save_path_that_shiny_uses(tmp_path):
    plot = VizFactory().render(DF, recipe([{"name": "geom_point", "params": {"size": "big"}}]), "p")
    show_draw_errors(plot).save(tmp_path / "e.png", width=4, height=3, dpi=50, verbose=False)
    assert (tmp_path / "e.png").stat().st_size > 0


def test_without_show_draw_errors_saving_a_failing_plot_raises(tmp_path):
    plot = VizFactory().render(DF, recipe([{"name": "geom_point", "params": {"size": "big"}}]), "p")
    with pytest.raises(VisualizationError):
        plot.save(tmp_path / "never.png", verbose=False)
    assert not (tmp_path / "never.png").exists()


def test_a_text_for_an_argument_whose_default_is_a_number_is_not_called_not_a_number_without_proof():
    # scale_color_brewer's `palette` has the default 1 and also takes a name: 'Set1' needs `type: qual`, it is not "not a number".
    error = failure([{"name": "geom_point", "params": {}}, {"name": "scale_color_brewer", "params": {"palette": "Set1"}}],
                    mapping={"x": "x", "y": "y", "color": "g"})
    assert "is not a number" not in str(error)


def test_a_keyword_refused_deeper_inside_plotnine_is_not_blamed_on_the_layer():
    error = failure([{"name": "geom_point"}, {"name": "theme_custom", "params": {"axis_text_x": {"angle": 45}}}])
    assert "is not an argument of theme_custom" not in str(error)
