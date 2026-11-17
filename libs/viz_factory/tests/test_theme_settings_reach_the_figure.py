"""The common plotnine `theme()` settings, written in a recipe, reach the drawn figure (D-0242, "lots of parameters accepted").

# @deps
# consumes: libs/viz_factory/src/viz_factory/themes/core.py (theme_bw ... theme_custom), libs/viz_factory/src/viz_factory/viz_factory.py
# doc: .claude/rules/rules_viz_factory.md
# @end_deps

Two routes are tested for every setting:
  (a) a named theme with extra params: `theme_bw` with `base_family`, `base_size` and any other key added as a `theme()` setting;
  (b) `theme_custom` with element dicts: `{name: element_text, params: {...}}`.

"Reaches the figure" is proved two ways for each case: the picture of the recipe is the picture of the same plotnine theme written by
hand (pixel for pixel), and it differs from the picture without the setting (a setting with no effect would be equal to it).
Where a value can be read (font, size, angle, colour of a tick label from the figure; the properties of the theme for what plotnine keeps outside the axes, such as the axis title and the plot background), it is read as well.

A setting that cannot be written in route (a) is an expected failure with the reason: an element (text, line, rect) is an object, and
route (a) passes the value to plotnine as it is, so a dict of the recipe is refused by plotnine with a message (not silent). Those gaps
need nested objects (elements, margins); how such values are passed is a separate research.
"""
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

import viz_factory  # noqa: F401
from plotnine import (aes, element_blank, element_line, element_rect, element_text, facet_wrap, geom_point, ggplot, labs,
                      theme, theme_bw)
from viz_factory.errors import VisualizationError
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0], "y": [3.0, 1.0, 2.0, 5.0], "g": ["a", "b", "c", "a"], "f": ["u", "u", "v", "v"]})
MAPPING = {"x": "x", "y": "y", "color": "g"}
TITLE = "A title"
FAMILY = "DejaVu Serif"


def recipe_plot(*layers):
    """The plot as a recipe draws it: a point layer, a facet, a title, and the layers of the case."""
    spec = {"target_dataset": "d", "mapping": MAPPING, "facet_by": "f",
            "layers": [{"name": "geom_point"}, {"name": "labs", "params": {"title": TITLE}}] + [dict(l) for l in layers]}
    return VizFactory().render(DF, {"plots": {"p": spec}}, "p")


def hand_plot(*addables):
    plot = ggplot(DF.to_pandas(), aes(**MAPPING)) + geom_point() + facet_wrap("f") + labs(title=TITLE)
    for item in addables:
        plot = plot + item
    return plot


def pixels(plot, tmp_path, name):
    path = tmp_path / f"{name}.png"
    plot.save(path, width=4, height=3, dpi=60, verbose=False)
    return path.read_bytes()


def custom(**elements):
    """Route (b): theme_custom with element dicts, written as a recipe writes them."""
    return {"name": "theme_custom", "params": elements}


def element(name, **params):
    return {"name": name, "params": params}


def named(**params):
    """Route (a): the named theme, theme_bw, with extra params."""
    return {"name": "theme_bw", "params": params}


T = element("element_text", size=14, angle=45, color="red")

# id, route (a) layer or None, route (b) layer, by-hand theme for (a), by-hand theme for (b), reader of the figure (or None)
# The recipe written for each case is the YAML under "yaml" in the report; here it is the same thing as a dict.
CASES = [
    ("font_family",
     named(base_family=FAMILY), custom(text=element("element_text", family=FAMILY)),
     theme_bw(base_family=FAMILY), theme_bw() + theme(text=element_text(family=FAMILY)),
     lambda plot, fig: fig.axes[0].xaxis.label.get_fontfamily()[0] == FAMILY),
    ("font_size",
     named(base_size=20), custom(text=element("element_text", size=20)),
     theme_bw(base_size=20), theme_bw() + theme(text=element_text(size=20)),
     lambda plot, fig: fig.axes[0].xaxis.label.get_fontsize() >= 20),
    ("legend_position",
     named(legend_position="bottom"), custom(legend_position="bottom"),
     theme_bw() + theme(legend_position="bottom"), theme_bw() + theme(legend_position="bottom"), None),
    ("legend_direction",
     named(legend_direction="horizontal"), custom(legend_direction="horizontal"),
     theme_bw() + theme(legend_direction="horizontal"), theme_bw() + theme(legend_direction="horizontal"), None),
    ("panel_spacing",
     named(panel_spacing=0.4), custom(panel_spacing=0.4),
     theme_bw() + theme(panel_spacing=0.4), theme_bw() + theme(panel_spacing=0.4), None),
    ("plot_margin",
     named(plot_margin=0.15), custom(plot_margin=0.15),
     theme_bw() + theme(plot_margin=0.15), theme_bw() + theme(plot_margin=0.15), None),
    ("panel_grid_major_off",
     named(panel_grid_major=element("element_blank")), custom(panel_grid_major=element("element_blank")),
     theme_bw() + theme(panel_grid_major=element_blank()), theme_bw() + theme(panel_grid_major=element_blank()), None),
    ("panel_grid_minor_off",
     named(panel_grid_minor=element("element_blank")), custom(panel_grid_minor=element("element_blank")),
     theme_bw() + theme(panel_grid_minor=element_blank()), theme_bw() + theme(panel_grid_minor=element_blank()), None),
    ("panel_grid_major_on_with_colour",
     named(panel_grid_major=element("element_line", color="red", linewidth=2)),
     custom(panel_grid_major=element("element_line", color="red", linewidth=2)),
     theme_bw() + theme(panel_grid_major=element_line(color="red", linewidth=2)),
     theme_bw() + theme(panel_grid_major=element_line(color="red", linewidth=2)), None),
    ("panel_grid_minor_on_with_colour",
     named(panel_grid_minor=element("element_line", color="blue", linewidth=2)),
     custom(panel_grid_minor=element("element_line", color="blue", linewidth=2)),
     theme_bw() + theme(panel_grid_minor=element_line(color="blue", linewidth=2)),
     theme_bw() + theme(panel_grid_minor=element_line(color="blue", linewidth=2)), None),
    ("axis_text_size",
     named(axis_text_x=element("element_text", size=16)), custom(axis_text_x=element("element_text", size=16)),
     theme_bw() + theme(axis_text_x=element_text(size=16)), theme_bw() + theme(axis_text_x=element_text(size=16)),
     lambda plot, fig: fig.axes[0].get_xticklabels()[0].get_fontsize() == 16),
    ("axis_text_angle",
     named(axis_text_x=element("element_text", angle=45)), custom(axis_text_x=element("element_text", angle=45)),
     theme_bw() + theme(axis_text_x=element_text(angle=45)), theme_bw() + theme(axis_text_x=element_text(angle=45)),
     lambda plot, fig: fig.axes[0].get_xticklabels()[0].get_rotation() == 45),
    ("axis_text_colour",
     named(axis_text_x=element("element_text", color="red")), custom(axis_text_x=element("element_text", color="red")),
     theme_bw() + theme(axis_text_x=element_text(color="red")), theme_bw() + theme(axis_text_x=element_text(color="red")),
     lambda plot, fig: fig.axes[0].get_xticklabels()[0].get_color() == "red"),
    ("axis_title_size",
     named(axis_title_x=element("element_text", size=18)), custom(axis_title_x=element("element_text", size=18)),
     theme_bw() + theme(axis_title_x=element_text(size=18)), theme_bw() + theme(axis_title_x=element_text(size=18)),
     lambda plot, fig: plot.theme.themeables["axis_title_x"].properties["size"] == 18),
    ("axis_title_angle",
     named(axis_title_x=element("element_text", angle=10)), custom(axis_title_x=element("element_text", angle=10)),
     theme_bw() + theme(axis_title_x=element_text(angle=10)), theme_bw() + theme(axis_title_x=element_text(angle=10)),
     lambda plot, fig: plot.theme.themeables["axis_title_x"].properties["rotation"] == 10),
    ("axis_title_colour",
     named(axis_title_x=element("element_text", color="green")), custom(axis_title_x=element("element_text", color="green")),
     theme_bw() + theme(axis_title_x=element_text(color="green")), theme_bw() + theme(axis_title_x=element_text(color="green")),
     lambda plot, fig: plot.theme.themeables["axis_title_x"].properties["color"] == "green"),
    ("strip_text",
     named(strip_text=element("element_text", size=18, color="blue")), custom(strip_text=element("element_text", size=18, color="blue")),
     theme_bw() + theme(strip_text=element_text(size=18, color="blue")), theme_bw() + theme(strip_text=element_text(size=18, color="blue")),
     None),
    ("plot_title",
     named(plot_title=element("element_text", size=24, color="purple")), custom(plot_title=element("element_text", size=24, color="purple")),
     theme_bw() + theme(plot_title=element_text(size=24, color="purple")), theme_bw() + theme(plot_title=element_text(size=24, color="purple")),
     None),
    ("margin_of_a_text",
     named(axis_title_x=element("element_text", margin={"t": 40})), custom(axis_title_x=element("element_text", margin={"t": 40})),
     theme_bw() + theme(axis_title_x=element_text(margin={"t": 40})), theme_bw() + theme(axis_title_x=element_text(margin={"t": 40})), None),
    ("panel_background",
     named(panel_background=element("element_rect", fill="yellow")), custom(panel_background=element("element_rect", fill="yellow")),
     theme_bw() + theme(panel_background=element_rect(fill="yellow")), theme_bw() + theme(panel_background=element_rect(fill="yellow")), None),
    ("plot_background",
     named(plot_background=element("element_rect", fill="pink")), custom(plot_background=element("element_rect", fill="pink")),
     theme_bw() + theme(plot_background=element_rect(fill="pink")), theme_bw() + theme(plot_background=element_rect(fill="pink")),
     lambda plot, fig: plot.theme.themeables["plot_background"].properties["facecolor"] == "pink"),
    ("legend_title",
     named(legend_title=element("element_text", size=22, color="red")), custom(legend_title=element("element_text", size=22, color="red")),
     theme_bw() + theme(legend_title=element_text(size=22, color="red")), theme_bw() + theme(legend_title=element_text(size=22, color="red")),
     None),
    ("legend_text",
     named(legend_text=element("element_text", size=20, color="green")), custom(legend_text=element("element_text", size=20, color="green")),
     theme_bw() + theme(legend_text=element_text(size=20, color="green")), theme_bw() + theme(legend_text=element_text(size=20, color="green")),
     None),
]

# Settings that route (a) cannot write: the value is an element object. plotnine refuses the dict of the recipe, with a message.
ROUTE_A_SCALAR = {"font_family", "font_size", "legend_position", "legend_direction", "panel_spacing", "plot_margin"}
ROUTE_A_GAP = ("route (a) passes the value as it is to plotnine's theme(); an element is an object and the recipe's dict "
               "{name: element_*, params: ...} is refused by plotnine (VisualizationError naming the setting), so it cannot be written; use theme_custom")

IDS = [c[0] for c in CASES]


def layer_of(case, route):
    return case[1] if route == "a" else case[2]


def hand_of(case, route):
    return case[3] if route == "a" else case[4]


def _params():
    for case in CASES:
        for route in ("a", "b"):
            marks = []
            if route == "a" and case[0] not in ROUTE_A_SCALAR:
                marks.append(pytest.mark.xfail(strict=True, raises=VisualizationError, reason=ROUTE_A_GAP))
            yield pytest.param(case, route, id=f"{case[0]}-route_{route}", marks=marks)


@pytest.mark.parametrize("case,route", list(_params()))
def test_the_setting_reaches_the_drawn_figure(case, route, tmp_path):
    layer = layer_of(case, route)
    from_recipe = recipe_plot(layer)
    baseline = recipe_plot()
    wanted = hand_plot(hand_of(case, route))
    drawn = pixels(from_recipe, tmp_path, "recipe")
    assert drawn == pixels(wanted, tmp_path, "hand"), "the recipe does not draw what the same plotnine theme draws by hand"
    assert drawn != pixels(baseline, tmp_path, "baseline"), "the setting has no effect: the picture is the one without it"
    reader = case[5]
    if reader is not None:
        figure = from_recipe.draw()
        assert reader(from_recipe, figure), "the value read from the drawn figure is not the one written in the recipe"


def test_a_value_of_route_a_that_plotnine_refuses_is_a_loud_error_not_a_silent_one():
    with pytest.raises(VisualizationError) as raised:
        recipe_plot(named(panel_grid_minor=element("element_blank"))).draw()
    assert "panel_grid_minor" in str(raised.value)


# ---- the automatic axis-text adjustment and how an author overrides it (to be documented, D-0242) ----
LONG = pl.DataFrame({"x": ["a long category name", "another long name", "third long label"], "y": ["category number one", "category number two", "category number three"],
                     "g": ["a", "b", "c"]})


def axis_plot(df, *layers, mapping=None):
    spec = {"target_dataset": "d", "mapping": mapping or {"x": "x", "y": "y"}, "layers": [{"name": "geom_point"}] + [dict(l) for l in layers]}
    return VizFactory().render(df, {"plots": {"p": spec}}, "p")


def tick_rotations(plot):
    ax = plot.draw().axes[0]
    return ax.get_xticklabels()[0].get_rotation(), ax.get_yticklabels()[0].get_rotation()


def test_the_axis_text_is_adjusted_automatically_for_long_text_axes_in_every_plot():
    x_rotation, y_rotation = tick_rotations(axis_plot(LONG))
    assert x_rotation == 45, "long labels on the x axis are rotated by the automatic adjustment"


def test_a_numeric_axis_is_left_alone_by_the_automatic_adjustment():
    numeric = pl.DataFrame({"x": [1.0, 2.0], "y": [1.0, 2.0]})
    assert tick_rotations(axis_plot(numeric)) == (0, 0)


def test_an_element_text_layer_of_the_author_overrides_the_adjustment_for_that_axis_only():
    own = {"name": "element_text", "params": {"target": "axis_text_x", "angle": 0}}
    x_rotation, y_rotation = tick_rotations(axis_plot(LONG, own))
    assert x_rotation == 0, "the author's element_text on axis_text_x wins over the automatic rotation"
    own_y = {"name": "element_text", "params": {"target": "axis_text_y", "angle": 30}}
    x_rotation, y_rotation = tick_rotations(axis_plot(LONG, own_y))
    assert (x_rotation, y_rotation) == (45, 30), "overriding y leaves the automatic adjustment of x in place"


@pytest.mark.xfail(strict=True, reason=(
    "GAP, not decided: the adjustment is an element_text layer applied last, so a theme_custom written for the same axis is applied "
    "before it and loses, with no message. D-0242 names only the element_text layer as the way to override; whether theme_custom "
    "should also override, or say that it does not, is open"))
def test_a_theme_custom_axis_text_overrides_the_adjustment():
    custom_x = custom(axis_text_x=element("element_text", angle=0))
    x_rotation, _ = tick_rotations(axis_plot(LONG, custom_x))
    assert x_rotation == 0


def test_the_colour_of_an_element_can_be_written_with_either_spelling(tmp_path):
    first = pixels(recipe_plot(custom(axis_text_x=element("element_text", color="red"))), tmp_path, "color")
    second = pixels(recipe_plot(custom(axis_text_x=element("element_text", colour="red"))), tmp_path, "colour")
    assert first == second
