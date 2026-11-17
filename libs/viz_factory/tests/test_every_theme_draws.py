"""Every registered theme component draws a plot through the path a recipe uses (D-0245 context).

# @deps
# consumes: libs/viz_factory/src/viz_factory/registry.py (COMPONENT_SCHEMAS), libs/viz_factory/src/viz_factory/viz_factory.py (VizFactory.render)
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

The list of themes is read from the registry, never written here, so a theme added later is drawn by this test without a change.
`theme_get`, `theme_set` and `theme_update` of plotnine are not registered on purpose (D-0245): they read or change plotnine's
global default theme and draw nothing; the last test pins that reading of plotnine.
"""
import inspect

import matplotlib
import plotnine
import polars as pl
import pytest

matplotlib.use("Agg")

import viz_factory  # noqa: F401
from viz_factory.registry import COMPONENT_SCHEMAS
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": [3.0, 1.0, 2.0, 5.0], "g": ["a", "b", "c", "a"]})

REGISTERED_THEMES = sorted(n for n in COMPONENT_SCHEMAS if n.startswith("theme_"))

# Themes that cannot be drawn today, with the exact reason. An entry here is a gap that is reported, not hidden: when the
# theme draws, the strict xfail turns into a failure that asks for this entry to be removed.
EXPECTED_FAILURES: dict = {}


def draw(theme_name, params=None):
    spec = {"target_dataset": "d", "mapping": {"x": "x", "y": "y", "color": "g"},
            "layers": [{"name": "geom_point"}, {"name": theme_name, "params": params or {}}]}
    plot = VizFactory().render(DF, {"plots": {"p": spec}}, "p")
    return plot, plot.draw()


def test_the_registry_has_themes_to_draw():
    assert len(REGISTERED_THEMES) >= 10, "the list is read from the registry; a near empty list means the registry was not loaded"


@pytest.mark.parametrize("theme_name", REGISTERED_THEMES)
def test_each_registered_theme_draws_one_plot(theme_name):
    if theme_name in EXPECTED_FAILURES:
        pytest.xfail(EXPECTED_FAILURES[theme_name])
    plot, figure = draw(theme_name)
    assert figure.axes, f"{theme_name} gave a figure with no axes"
    assert theme_name in [step.name for step in plot._sparmvet.steps], f"{theme_name} was not applied by the render"


def test_the_complete_themes_differ_from_each_other_in_the_picture(tmp_path):
    """A theme that draws is not enough: a theme that is applied silently as nothing would draw too."""
    def bytes_of(name):
        plot, _ = draw(name)
        path = tmp_path / f"{name}.png"
        plot.save(path, width=3, height=2, dpi=50, verbose=False)
        return path.read_bytes()
    assert bytes_of("theme_bw") != bytes_of("theme_dark")
    assert bytes_of("theme_bw") != bytes_of("theme_void")


def test_the_plotnine_themes_that_are_not_registered_are_only_the_spelling_and_the_three_global_functions():
    plotnine_names = {n for n in dir(plotnine) if n.startswith("theme")}
    registered_as_plotnine = {n for n in REGISTERED_THEMES}
    missing = sorted(plotnine_names - registered_as_plotnine - {"themes"})
    # `theme` is wrapped by theme_custom and theme_legend_position; theme_grey is the other spelling of the registered theme_gray
    assert missing == ["theme", "theme_get", "theme_grey", "theme_set", "theme_update"]


def test_theme_get_set_and_update_read_or_change_the_global_default_and_draw_no_theme():
    source = {name: inspect.getsource(getattr(plotnine, name)) for name in ("theme_get", "theme_set", "theme_update")}
    assert 'get_option("current_theme")' in source["theme_get"]
    assert 'set_option("current_theme", new)' in source["theme_set"]
    assert "theme_set(" in source["theme_update"]
    for name, text in source.items():
        assert "ggplot" not in text.replace("ggplot2", ""), f"{name} does not build a plot"
    for name in ("theme_get", "theme_set", "theme_update"):
        assert name not in COMPONENT_SCHEMAS


def test_theme_grey_is_only_an_alias_subclass_of_the_registered_theme_gray():
    assert issubclass(plotnine.theme_grey, plotnine.theme_gray)
    assert inspect.getsource(plotnine.theme_grey).split("\n", 2)[2].strip() == "pass"
