"""A complete theme replaces a complete theme; a partial theme setting is added to it (VIZ-STANDARD-1).

# @deps
# consumes: libs/viz_factory/src/viz_factory/plot_config_resolver.py (is_partial_theme, resolve_plot_config), libs/viz_factory/src/viz_factory/registry.py
# @end_deps

`theme_minimal` followed by `theme_legend_position` used to keep only the last: every `theme_*` name was one slot,
so the minimal theme was dropped without a word and the picture came out in the default theme. Whether a theme
component is complete or partial is read from the registry: a component that wraps plotnine's `theme` itself sets
properties; one that wraps a named theme is complete.
"""
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

import viz_factory  # noqa: F401
from viz_factory.plot_config_resolver import is_partial_theme, resolve_plot_config
from viz_factory.registry import COMPONENT_SCHEMAS
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [3.0, 1.0, 2.0], "g": ["a", "b", "c"]})
MAPPING = {"x": "x", "y": "y", "color": "g"}


def themes_of(*names, **partial_params):
    layers = [{"name": "geom_point"}] + [{"name": n, "params": partial_params.get(n, {})} for n in names]
    resolved = resolve_plot_config({"mapping": MAPPING, "layers": layers}, {}, None)
    return [layer["name"] for layer in resolved["layers"] if layer["name"].startswith("theme_")], resolved


def plot_of(*layers):
    spec = {"target_dataset": "d", "mapping": MAPPING, "layers": [{"name": "geom_point"}] + [dict(l) for l in layers]}
    return VizFactory().render(DF, {"plots": {"p": spec}}, "p")


def themeables(plot):
    return set(plot.theme.themeables)


def test_the_registry_says_which_theme_components_are_partial():
    partial = sorted(n for n in COMPONENT_SCHEMAS if n.startswith("theme_") and is_partial_theme(n))
    assert partial == ["theme_custom", "theme_legend_position"]
    for complete in ("theme_bw", "theme_minimal", "theme_dashboard", "theme_publication", "theme_light"):
        assert not is_partial_theme(complete)
    assert not is_partial_theme("theme_not_registered")


def test_a_partial_theme_is_added_to_the_complete_theme_not_instead_of_it():
    names, _ = themes_of("theme_minimal", "theme_legend_position")
    assert names == ["theme_minimal", "theme_legend_position"]


def test_the_default_theme_stays_under_a_partial_theme_that_stands_alone():
    names, resolved = themes_of("theme_legend_position")
    assert names == ["theme_bw", "theme_legend_position"]
    assert resolved["theme"] == "theme_bw", "the named theme of the plot is the complete one"


def test_a_complete_theme_replaces_a_complete_theme_and_the_later_wins():
    names, resolved = themes_of("theme_minimal", "theme_light")
    assert names == ["theme_light"] and resolved["theme"] == "theme_light"


def test_a_partial_theme_written_before_the_complete_one_is_not_lost():
    names, _ = themes_of("theme_legend_position", "theme_minimal")
    assert names == ["theme_minimal", "theme_legend_position"], "the complete theme goes first, plotnine drops what came before it"


def test_two_partial_themes_are_both_kept():
    names, _ = themes_of("theme_legend_position", "theme_custom")
    assert names == ["theme_bw", "theme_legend_position", "theme_custom"]


def pixels(plot, tmp_path, name):
    path = tmp_path / f"{name}.png"
    plot.save(path, width=4, height=3, dpi=60, verbose=False)
    return path.read_bytes()


def by_hand(*addables):
    from plotnine import aes, geom_point, ggplot
    plot = ggplot(DF.to_pandas(), aes(**MAPPING)) + geom_point()
    for item in addables:
        plot = plot + item
    return plot


def test_the_picture_is_the_complete_theme_with_the_partial_setting_added(tmp_path):
    from plotnine import theme, theme_minimal
    factory = plot_of({"name": "theme_minimal"}, {"name": "theme_legend_position", "params": {"position": "bottom"}})
    assert pixels(factory, tmp_path, "factory") == pixels(by_hand(theme_minimal(), theme(legend_position="bottom")), tmp_path, "hand")
    assert pixels(factory, tmp_path, "factory") != pixels(by_hand(theme(legend_position="bottom")), tmp_path, "no_minimal"), \
        "the old result: the minimal theme was dropped and the picture was the default theme"


def test_the_order_of_the_two_does_not_change_the_picture():
    first = plot_of({"name": "theme_minimal"}, {"name": "theme_legend_position", "params": {"position": "bottom"}})
    second = plot_of({"name": "theme_legend_position", "params": {"position": "bottom"}}, {"name": "theme_minimal"})
    assert first.theme.getp("legend_position") == second.theme.getp("legend_position") == "bottom"
    assert themeables(first) == themeables(second)


def test_a_later_complete_theme_gives_the_picture_of_that_theme_only(tmp_path):
    from plotnine import theme_light
    factory = plot_of({"name": "theme_minimal"}, {"name": "theme_light"})
    assert pixels(factory, tmp_path, "factory") == pixels(by_hand(theme_light()), tmp_path, "hand")
