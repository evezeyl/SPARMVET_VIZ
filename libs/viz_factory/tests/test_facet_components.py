"""The facet components do what their description says (VIZ-FOLLOWUPS-1, item 2).

facet_rows and facet_cols take the column in `facets` and lay the panels out like facet_grid with only rows or only cols.
facet_scales, facet_space and facet_margins set that one setting on the facet the recipe wrote BEFORE them; with no such
facet (none at all, only facet_wrap for space and margins, or the facet written after them) the plot is refused with a
message that names the fix, never "value refused" or "check the parameters".

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_facet_components.py -q
"""
import matplotlib
import numpy as np
import polars as pl
import pytest
from matplotlib import pyplot as plt
from plotnine import aes, facet_grid, facet_wrap, geom_point, ggplot

matplotlib.use("Agg")

from utils.errors import VisualizationError
from viz_factory.viz_factory import VizFactory, draw_checked

_rng = np.random.RandomState(3)
N = 40
TABLE = pl.DataFrame({
    "x": _rng.rand(N), "y": _rng.rand(N) * np.tile([1, 50], N // 2),
    "Year": [2018 + i % 4 for i in range(N)], "Country": ["N", "S"] * (N // 2),
})


def make(*facet_layers):
    layers = [{"name": "geom_point"}, *facet_layers]
    return VizFactory().render(TABLE, {"plots": {"p": {"mapping": {"x": "x", "y": "y"}, "layers": layers}}}, "p")


def axes_of(figure):
    boxes = sorted((round(a.get_position().x0, 3), round(a.get_position().y0, 3), round(a.get_position().width, 3),
                    round(a.get_position().height, 3), tuple(round(v, 3) for v in a.get_ylim())) for a in figure.axes)
    plt.close(figure)
    return boxes


def direct(facet):
    return axes_of((ggplot(TABLE.to_pandas(), aes("x", "y")) + geom_point() + facet).draw())


def drawn(*facet_layers):
    return axes_of(draw_checked(make(*facet_layers)))


def refusal(*facet_layers) -> str:
    with pytest.raises(VisualizationError) as raised:
        draw_checked(make(*facet_layers))
    return str(raised.value)


def test_facet_rows_equals_facet_grid_with_rows():
    assert drawn({"name": "facet_rows", "params": {"facets": "Country"}}) == direct(facet_grid(rows="Country"))


def test_facet_cols_equals_facet_grid_with_cols():
    assert drawn({"name": "facet_cols", "params": {"facets": "Year"}}) == direct(facet_grid(cols="Year"))


def test_facet_rows_keeps_its_scales_setting():
    got = drawn({"name": "facet_rows", "params": {"facets": "Country", "scales": "free_y"}})
    assert got == direct(facet_grid(rows="Country", scales="free_y"))


@pytest.mark.parametrize("name,wrong", [("facet_rows", "rows"), ("facet_cols", "cols")])
def test_facet_rows_and_cols_without_facets_name_the_fix(name, wrong):
    message = refusal({"name": name, "params": {wrong: "Country"}})
    assert "facets" in message and "refused by plotnine" not in message


@pytest.mark.parametrize("kind,wrap_or_grid", [("wrap", facet_wrap("Year")), ("grid", facet_grid(rows="Country", cols="Year"))])
def test_facet_scales_sets_the_scales_of_the_facet_before(kind, wrap_or_grid):
    write = {"name": "facet_wrap", "params": {"facets": "Year"}} if kind == "wrap" else \
        {"name": "facet_grid", "params": {"rows": "Country", "cols": "Year"}}
    free = facet_wrap("Year", scales="free_y") if kind == "wrap" else facet_grid(rows="Country", cols="Year", scales="free_y")
    got = drawn(write, {"name": "facet_scales", "params": {"scales": "free_y"}})
    assert got == direct(free)
    assert got != direct(wrap_or_grid)   # the setting made a difference: the test can fail


def test_facet_space_sets_the_space_of_the_facet_grid_before():
    grid = {"name": "facet_grid", "params": {"rows": "Country", "cols": "Year", "scales": "free_y"}}
    got = drawn(grid, {"name": "facet_space", "params": {"space": "free_y"}})
    assert got == direct(facet_grid(rows="Country", cols="Year", scales="free_y", space="free_y"))
    assert got != drawn(grid)


def test_facet_margins_sets_the_margins_of_the_facet_grid_before():
    grid = {"name": "facet_grid", "params": {"rows": "Country", "cols": "Year"}}
    got = drawn(grid, {"name": "facet_margins", "params": {"margins": True}})
    assert got == direct(facet_grid(rows="Country", cols="Year", margins=True))
    assert got != drawn(grid)


SETTINGS = {
    "facet_scales": {"scales": "free_y"},
    "facet_space": {"space": "free_y"},
    "facet_margins": {"margins": True},
    "facet_labeller": {"labeller": "label_both"},
}


@pytest.mark.parametrize("name", SETTINGS)
def test_a_setting_with_no_facet_before_it_is_refused_with_the_fix(name):
    message = refusal({"name": name, "params": SETTINGS[name]})
    assert name in message and "facet" in message and "refused by plotnine" not in message and "check the parameters" not in message


@pytest.mark.parametrize("name", SETTINGS)
def test_a_setting_written_before_the_facet_is_refused(name):
    message = refusal({"name": name, "params": SETTINGS[name]}, {"name": "facet_wrap", "params": {"facets": "Year"}})
    assert "before" in message


@pytest.mark.parametrize("name", ["facet_space", "facet_margins"])
def test_space_and_margins_need_a_facet_grid_not_a_facet_wrap(name):
    message = refusal({"name": "facet_wrap", "params": {"facets": "Year"}}, {"name": name, "params": SETTINGS[name]})
    assert "facet_grid" in message and "facet_wrap" in message


def test_a_facet_setting_does_not_replace_the_facet_it_changes():
    """The resolver keeps one facet per plot; a setting component is not a facet, so it must not take the facet's place."""
    got = drawn({"name": "facet_wrap", "params": {"facets": "Year"}}, {"name": "facet_labeller", "params": {"labeller": "label_both"}})
    assert len(got) == 4   # the four Year panels are still there


def test_facet_labeller_labels_the_strips_of_the_facet_before():
    figure = draw_checked(make({"name": "facet_wrap", "params": {"facets": "Year"}},
                               {"name": "facet_labeller", "params": {"labeller": "label_both"}}))
    texts = {t.get_text() for t in figure.findobj(matplotlib.text.Text)}
    plt.close(figure)
    assert "Year: 2018" in texts
