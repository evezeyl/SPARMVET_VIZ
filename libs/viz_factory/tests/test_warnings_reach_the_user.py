"""A warning is kept on the plot for a screen to show; it used to be printed on the console only (VIZ-STANDARD-1).

# @deps
# consumes: libs/viz_factory/src/viz_factory/viz_factory.py (VizFactory.render), libs/viz_factory/src/viz_factory/checked_plot.py (plot_warnings, show_draw_errors)
# @end_deps

Three warnings: an unknown `plot_defaults` key (ignored), the `fill_color` / `fill_palette` mutex of a T3 override (the palette
wins), and a palette that cannot be applied (the plot draws without it). The plot still draws in each case.
"""
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from matplotlib.figure import Figure
from viz_factory.checked_plot import plot_warnings, show_draw_errors
from viz_factory.viz_factory import VizFactory, draw_checked

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [3.0, 1.0, 2.0], "g": ["a", "b", "c"]})


def recipe(defaults=None, **spec_more):
    spec = {"target_dataset": "d", "mapping": {"x": "x", "y": "y", "fill": "g"}, "layers": [{"name": "geom_col"}], **spec_more}
    return {"plots": {"p": spec}, "plot_defaults": defaults or {}}


def test_a_clean_plot_has_no_warning():
    assert plot_warnings(VizFactory().render(DF, recipe(), "p")) == []


def test_an_unknown_plot_defaults_key_is_a_warning_naming_the_key():
    plot = VizFactory().render(DF, recipe({"palete": "Blues"}), "p")
    found = plot_warnings(plot)
    assert len(found) == 1 and found[0].severity == "warning"
    assert "palete" in found[0].problem and "plot_defaults" in found[0].fix
    assert isinstance(draw_checked(plot), Figure), "the plot still draws"


def test_the_unknown_key_warning_is_the_same_for_every_plot_of_the_recipe():
    first = plot_warnings(VizFactory().render(DF, recipe({"palete": "Blues"}), "p"))[0]
    other = recipe({"palete": "Blues"})
    other["plots"]["q"] = other["plots"].pop("p")
    second = plot_warnings(VizFactory().render(DF, other, "q"))[0]
    assert (first.problem, first.location) == (second.problem, second.location), "the alerts panel shows it once"


def test_the_fill_colour_and_fill_palette_mutex_is_a_warning():
    plot = VizFactory().render(DF, recipe(), "p", aesthetic_override={"fill_color": "#ff0000", "fill_palette": "Blues"})
    found = plot_warnings(plot)
    assert len(found) == 1 and "fill_color" in found[0].problem and "fill_palette" in found[0].problem
    assert found[0].problem.startswith("Plot 'p': ")
    draw_checked(plot)


def test_a_palette_that_cannot_be_applied_is_a_warning_and_the_plot_draws_without_it():
    plot = VizFactory().render(DF, recipe(palette="zzz_not_a_palette"), "p")
    found = plot_warnings(plot)
    assert len(found) == 1 and "zzz_not_a_palette" in found[0].problem and found[0].problem.startswith("Plot 'p': ")
    assert "sparmvet_brand" in found[0].fix, "the fix lists the palettes that exist"
    draw_checked(plot)


def test_a_known_palette_is_no_warning():
    assert plot_warnings(VizFactory().render(DF, recipe(palette="sparmvet_brand"), "p")) == []


def test_show_draw_errors_hands_each_warning_to_the_callback_once():
    plot = VizFactory().render(DF, recipe({"palete": "x"}, palette="zzz_not_a_palette"), "p")
    seen = []
    shown = show_draw_errors(plot, on_warning=seen.append)
    assert len(seen) == 2
    shown.draw(show=False)
    assert len(seen) == 2, "drawing does not report them again"


def test_the_warnings_survive_the_copies_a_draw_makes():
    plot = VizFactory().render(DF, recipe(palette="zzz_not_a_palette"), "p")
    assert len(plot_warnings(plot + __import__("plotnine").theme_bw())) == 1
