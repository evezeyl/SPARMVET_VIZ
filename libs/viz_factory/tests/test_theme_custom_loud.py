"""A theme setting that cannot act is refused with a message, never dropped (D-0050), and a legend position is the one written.

# @deps
# consumes: libs/viz_factory/src/viz_factory/themes/core.py (theme_custom, theme_legend_position), libs/viz_factory/src/viz_factory/checked_plot.py
# doc: .claude/rules/rules_viz_factory.md
# @end_deps
"""
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

import viz_factory  # noqa: F401
from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory

DF = pl.DataFrame({"x": [1.0, 2.0, 3.0], "y": [3.0, 1.0, 2.0], "g": ["a", "b", "c"]})


def plot(layer, mapping=None):
    spec = {"target_dataset": "d", "mapping": mapping or {"x": "x", "y": "y"}, "layers": [{"name": "geom_point"}, layer]}
    return VizFactory().render(DF, {"plots": {"p": spec}}, "p")


def custom(**settings):
    return {"name": "theme_custom", "params": settings}


def test_an_unknown_element_name_is_refused_naming_setting_name_choices_and_closest():
    with pytest.raises(VisualizationError) as raised:
        plot(custom(axis_text_x={"name": "element_texxt", "params": {"size": 9}})).draw()
    text = str(raised.value)
    assert "axis_text_x" in text and "'element_texxt'" in text
    for existing in ("element_text", "element_line", "element_rect", "element_blank"):
        assert existing in text
    assert "write name: element_text" in text   # the closest match


def test_an_unknown_element_name_with_no_close_match_lists_the_choices():
    with pytest.raises(VisualizationError) as raised:
        plot(custom(axis_text_x={"name": "zzz", "params": {}})).draw()
    assert "write name: one of element_text" in str(raised.value)


def test_element_blank_with_parameters_is_refused_not_ignored():
    with pytest.raises(VisualizationError) as raised:
        plot(custom(axis_text_x={"name": "element_blank", "params": {"size": 9}})).draw()
    assert "element_blank" in str(raised.value) and "size" in str(raised.value)


def test_a_valid_element_blank_still_draws():
    plot(custom(panel_grid_minor={"name": "element_blank"})).draw()
    plot(custom(panel_grid_minor={"name": "element_blank", "params": {}})).draw()


@pytest.mark.parametrize("value", [
    {"params": {"size": 9}},                                  # no name
    {"name": "element_text", "params": [1]},                  # params not a mapping
    {"name": "element_text", "params": {"sizee": 9}},         # a parameter the element does not have
])
def test_the_other_bad_element_dicts_are_refused_loudly_by_plotnine(value):
    with pytest.raises(VisualizationError) as raised:
        plot(custom(axis_text_x=value)).draw()
    assert "axis_text_x" in str(raised.value)


def test_a_named_theme_given_an_element_dict_points_to_theme_custom():
    with pytest.raises(VisualizationError) as raised:
        plot({"name": "theme_bw", "params": {"axis_text_x": {"name": "element_text", "params": {"size": 9}}}}).draw()
    text = str(raised.value)
    assert "Suggestion:" in text and "theme_custom" in text


def test_theme_custom_with_a_plotnine_refusal_gets_no_theme_custom_suggestion():
    with pytest.raises(VisualizationError) as raised:
        plot(custom(axis_textt_x={"name": "element_text", "params": {"size": 9}})).draw()
    assert "Suggestion:" not in str(raised.value)


def legend_side(position):
    """Where the drawn legend sits against the panel: top, bottom, left, right, or none when no legend is drawn."""
    figure = plot({"name": "theme_legend_position", "params": {"position": position}}, {"x": "x", "y": "y", "color": "g"}).draw()
    figure.canvas.draw()
    renderer = figure.canvas.get_renderer()
    panel = figure.axes[0].get_window_extent(renderer)
    legends = [c for c in figure.get_children() if type(c).__name__ == "FlexibleAnchoredOffsetbox"]
    if not legends:
        return "none"
    box = legends[0].get_window_extent(renderer)
    if box.y0 >= panel.y1:
        return "top"
    if box.y1 <= panel.y0:
        return "bottom"
    if box.x1 <= panel.x0:
        return "left"
    if box.x0 >= panel.x1:
        return "right"
    return "inside"


@pytest.mark.parametrize("position", ["top", "bottom", "left", "right", "none"])
def test_theme_legend_position_draws_the_legend_where_the_recipe_says(position):
    assert legend_side(position) == position
