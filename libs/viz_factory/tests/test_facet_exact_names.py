"""A facet variable is handed to plotnine as an exact column name (PLOT-TEXT-RUNS-CODE-1, fix round 2026-11-16).

plotnine reads a facet text such as `~Collection year` with a pattern that stops at the first character that is not a
letter, digit or underscore: with a column `Collection` and a column `Collection year` it drew the panels of `Collection`
(2 panels instead of 3) and said nothing. The facet components now give plotnine a list of exact names, read from the
recipe's text by our own reader (`utils.plot_text_check.facet_variables`).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_facet_exact_names.py -q
"""
import matplotlib
import polars as pl
import pytest
from matplotlib.text import Text

matplotlib.use("Agg")

from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory


def two_columns():
    """`Collection` has 2 values and `Collection year` has 3: the right facet draws 3 panels."""
    return pl.DataFrame({
        "x": [float(i) for i in range(12)], "y": [float(i % 5) for i in range(12)],
        "Collection": [["u", "v"][i % 2] for i in range(12)],
        "Collection year": [["2001", "2002", "2003"][i % 3] for i in range(12)],
    })


def draw(data, layers=(), mapping=None):
    layers = [{"name": "geom_point"}, *layers]
    recipe = {"plots": {"p": {"mapping": mapping or {"x": "x", "y": "y"}, "layers": layers}}, "plot_defaults": {}}
    plot = VizFactory().render(data, recipe, "p")
    figure = plot.draw(show=False)
    texts = {t.get_text() for t in figure.findobj(Text)}
    panels = [a for a in figure.axes if a.has_data()]
    return plot, texts, len(panels)


def layer(name, **params):
    return {"name": name, "params": params}


def test_the_two_column_case_draws_three_panels_with_the_right_titles_through_facet_by():
    recipe = {"plots": {"p": {"mapping": {"x": "x", "y": "y"}, "facet_by": "Collection year", "layers": [{"name": "geom_point"}]}},
              "plot_defaults": {}}
    figure = VizFactory().render(two_columns(), recipe, "p").draw(show=False)
    texts = {t.get_text() for t in figure.findobj(Text)}
    assert {"2001", "2002", "2003"} <= texts and "u" not in texts
    assert len([a for a in figure.axes if a.has_data()]) == 3


def test_facet_by_in_the_mapping_is_exact_too():
    recipe = {"plots": {"p": {"mapping": {"x": "x", "y": "y", "facet_by": "Collection year"}, "layers": [{"name": "geom_point"}]}},
              "plot_defaults": {}}
    figure = VizFactory().render(two_columns(), recipe, "p").draw(show=False)
    assert len([a for a in figure.axes if a.has_data()]) == 3


@pytest.mark.parametrize("facets", ["~Collection year", "~ Collection year", "Collection year", ["Collection year"]])
def test_facet_wrap_draws_the_column_that_is_named(facets):
    _, texts, panels = draw(two_columns(), [layer("facet_wrap", facets=facets)])
    assert panels == 3 and {"2001", "2002", "2003"} <= texts


@pytest.mark.parametrize("params", [
    {"rows": "Collection year"},
    {"cols": "Collection year"},
    {"facets": "Collection year ~ ."},
    {"facets": ". ~ Collection year"},
    {"rows": ["Collection year"], "cols": None},
])
def test_facet_grid_draws_the_column_that_is_named(params):
    _, texts, panels = draw(two_columns(), [layer("facet_grid", **params)])
    assert panels == 3 and {"2001", "2002", "2003"} <= texts


@pytest.mark.parametrize("component", ["facet_rows", "facet_cols"])
def test_facet_rows_and_cols_draw_the_column_that_is_named(component):
    _, texts, panels = draw(two_columns(), [layer(component, facets="Collection year")])
    assert panels == 3 and {"2001", "2002", "2003"} <= texts


def test_a_grid_formula_with_two_columns_gives_the_product():
    _, texts, panels = draw(two_columns(), [layer("facet_grid", facets="Collection ~ Collection year")])
    assert panels == 6 and {"u", "v", "2001", "2002", "2003"} <= texts


@pytest.mark.parametrize("name", ["with space", "with-dash", "with.dot", "accentué été", "2nd value", "a b-c.d", "x1"])
@pytest.mark.parametrize("how", ["facet_by", "wrap_text", "wrap_formula", "wrap_list", "grid_rows", "grid_formula", "facet_rows", "facet_cols"])
def test_a_column_name_with_a_space_a_dash_a_dot_an_accent_or_a_number_first_is_drawn_right(name, how):
    data = pl.DataFrame({"x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0], "y": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
                         name: ["p", "q", "r", "p", "q", "r"]})
    layers = {
        "facet_by": [],
        "wrap_text": [layer("facet_wrap", facets=name)],
        "wrap_formula": [layer("facet_wrap", facets="~" + name)],
        "wrap_list": [layer("facet_wrap", facets=[name])],
        "grid_rows": [layer("facet_grid", rows=name)],
        "grid_formula": [layer("facet_grid", facets=f". ~ {name}")],
        "facet_rows": [layer("facet_rows", facets=name)],
        "facet_cols": [layer("facet_cols", facets=name)],
    }[how]
    spec = {"mapping": {"x": "x", "y": "y"}, "layers": [{"name": "geom_point"}, *layers]}
    if how == "facet_by":
        spec["facet_by"] = name
    recipe = {"plots": {"p": spec}, "plot_defaults": {}}
    figure = VizFactory().render(data, recipe, "p").draw(show=False)
    assert len([a for a in figure.axes if a.has_data()]) == 3
    assert {"p", "q", "r"} <= {t.get_text() for t in figure.findobj(Text)}


def test_a_name_that_is_not_a_column_is_refused_in_our_words_with_the_columns_listed():
    with pytest.raises(VisualizationError) as error:
        draw(two_columns(), [layer("facet_wrap", facets="~Collection yr")])
    text = str(error.value)
    assert "'Collection yr'" in text and "not a column" in text and "Collection year" in text
    assert "refused by plotnine" not in text and ". Suggestion: " in text and "Fix: Suggestion" not in text


def test_a_wrap_formula_with_a_variable_on_the_left_is_refused_in_our_words():
    with pytest.raises(VisualizationError) as error:
        draw(two_columns(), [layer("facet_wrap", facets="Collection ~ Collection year")])
    assert "nothing on the left of the ~" in str(error.value) and "Suggestion:" in str(error.value)


def test_a_grid_formula_with_two_tildes_is_refused_in_our_words():
    with pytest.raises(VisualizationError) as error:
        draw(two_columns(), [layer("facet_grid", facets="Collection ~ Collection year ~ x")])
    assert "one ~" in str(error.value) and "Suggestion:" in str(error.value)
