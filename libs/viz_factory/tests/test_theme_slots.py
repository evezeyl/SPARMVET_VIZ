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


def test_a_partial_theme_that_stands_alone_is_added_to_plotnines_own_default_not_to_an_app_theme():
    names, resolved = themes_of("theme_legend_position")
    assert names == ["theme_legend_position"], "no complete theme is injected under it (D-0258)"
    assert resolved["theme"] == "theme_gray", "the base of the plot is plotnine's own default"


def test_a_complete_theme_replaces_a_complete_theme_and_the_later_wins():
    names, resolved = themes_of("theme_minimal", "theme_light")
    assert names == ["theme_light"] and resolved["theme"] == "theme_light"


def test_a_partial_theme_written_before_the_complete_one_is_not_lost():
    names, _ = themes_of("theme_legend_position", "theme_minimal")
    assert names == ["theme_minimal", "theme_legend_position"], "the complete theme goes first, plotnine drops what came before it"


def test_two_partial_themes_are_both_kept():
    names, _ = themes_of("theme_legend_position", "theme_custom")
    assert names == ["theme_legend_position", "theme_custom"]


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


# D-0258 (Eve, 2026-11-18): without a theme in the recipe the figure is drawn with plotnine's own default (theme_gray); the app
# adds no theme of its own. A recipe that wants another look writes it (plot_defaults.theme or a theme layer).

def test_a_plot_with_no_theme_written_is_drawn_with_plotnines_own_default(tmp_path):
    from plotnine import theme_bw
    factory = plot_of()
    assert pixels(factory, tmp_path, "factory") == pixels(by_hand(), tmp_path, "plotnine_default")
    assert pixels(factory, tmp_path, "factory") != pixels(by_hand(theme_bw()), tmp_path, "bw"), "theme_bw is no longer the app's default"


def test_the_resolved_config_of_a_plot_with_no_theme_names_plotnines_default_and_holds_no_theme_layer():
    resolved = resolve_plot_config({"mapping": MAPPING, "layers": [{"name": "geom_point"}]}, {}, None)
    assert resolved["theme"] == "theme_gray"
    assert resolved["_provenance"]["theme"] == "plotnine"
    assert [layer["name"] for layer in resolved["layers"] if layer["name"].startswith("theme_")] == []


def test_a_theme_in_plot_defaults_is_the_theme_of_a_plot_that_writes_none(tmp_path):
    from plotnine import theme_light
    plot = VizFactory().render(DF, {"plots": {"p": {"target_dataset": "d", "mapping": MAPPING, "layers": [{"name": "geom_point"}]}},
                                    "plot_defaults": {"theme": "theme_light"}}, "p")
    assert pixels(plot, tmp_path, "factory") == pixels(by_hand(theme_light()), tmp_path, "hand")


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


# D-0244 (Eve, 2026-11-17): a complete theme replaces a complete theme, a partial one is added; a plot that writes its own
# complete theme loses the default's font and legend. This matches plotnine. The default comes from the recipe (plot_defaults).
RECIPE_DEFAULT_THEME = {"layers": [{"name": "theme_bw", "params": {"base_family": "DejaVu Serif", "legend_position": "bottom"}}]}


def default_plot(*plot_layers):
    spec = {"target_dataset": "d", "mapping": MAPPING, "layers": [{"name": "geom_point"}] + [dict(l) for l in plot_layers]}
    return VizFactory().render(DF, {"plots": {"p": spec}, "plot_defaults": RECIPE_DEFAULT_THEME}, "p")


def font_and_legend(plot):
    return plot.theme.themeables["text"].properties["family"], plot.theme.getp("legend_position")


def test_the_default_theme_of_the_recipe_gives_its_font_and_legend():
    assert font_and_legend(default_plot()) == ("DejaVu Serif", "bottom")


def test_a_plot_with_its_own_complete_theme_loses_the_font_and_legend_of_the_default():
    family, legend = font_and_legend(default_plot({"name": "theme_minimal"}))
    assert family != "DejaVu Serif", "the font of the default theme is gone: the complete theme of the plot replaced it"
    assert legend == "right", "the legend of the default theme is gone too (plotnine's own default position)"


def test_a_plot_with_a_partial_theme_keeps_the_default_and_the_partial_setting_is_added():
    family, legend = font_and_legend(default_plot({"name": "theme_legend_position", "params": {"position": "top"}}))
    assert family == "DejaVu Serif", "the font of the default theme stays"
    assert legend == "top", "the partial setting of the plot wins over the legend of the default"


def test_the_same_in_plotnine_a_complete_theme_added_after_another_replaces_it():
    from plotnine import theme, theme_bw, theme_minimal
    plot = by_hand(theme_bw(base_family="DejaVu Serif") + theme(legend_position="bottom"), theme_minimal())
    assert plot.theme.themeables["text"].properties["family"] != "DejaVu Serif"
    assert plot.theme.getp("legend_position") == "right"
