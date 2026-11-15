"""The named palettes viridis, plasma, magma, inferno and cividis colour a discrete and a continuous aesthetic
with the colour map of that name (they used to fail with a warning: plotnine has no scale_*_viridis_d).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_palette_viridis_family.py -q
"""
import matplotlib
import polars as pl
import pytest
from plotnine import aes, geom_point, ggplot, scale_color_cmap, scale_color_cmap_d, scale_fill_cmap, scale_fill_cmap_d

matplotlib.use("Agg")

from viz_factory.viz_factory import VizFactory

NAMES = ["viridis", "plasma", "magma", "inferno", "cividis"]


@pytest.fixture(scope="module")
def df():
    return pl.DataFrame({
        "x": [1.0, 2.0, 3.0, 4.0, 5.0, 6.0],
        "y": [2.0, 1.0, 4.0, 3.0, 6.0, 5.0],
        "g": ["a", "b", "c", "a", "b", "c"],
        "v": [0.0, 0.2, 0.4, 0.6, 0.8, 1.0],
    })


def render(df, aes_name, column, palette):
    recipe = {"plots": {"p": {"mapping": {"x": "x", "y": "y", aes_name: column},
                              "layers": [{"name": "geom_point", "params": {"shape": "o", "size": 4}}]}},
              "plot_defaults": {"palette": palette}}
    plot = VizFactory().render(df, recipe, "p")
    return plot


def point_colours(plot, key):
    fig = plot.draw()
    coll = fig.axes[0].collections[0]
    attr = coll.get_facecolor() if key == "fill" else coll.get_edgecolor()
    return [tuple(round(float(c), 4) for c in row[:3]) for row in attr]


def direct(df, aes_name, column, name, discrete):
    pdf = df.to_pandas()
    base = ggplot(pdf, aes(x="x", y="y", **{aes_name: column})) + geom_point(shape="o", size=4)
    scale = {("fill", True): scale_fill_cmap_d, ("color", True): scale_color_cmap_d,
             ("fill", False): scale_fill_cmap, ("color", False): scale_color_cmap}[(aes_name, discrete)]
    return base + scale(cmap_name=name)


@pytest.mark.parametrize("name", NAMES)
@pytest.mark.parametrize("aes_name", ["color", "fill"])
@pytest.mark.parametrize("column,discrete", [("g", True), ("v", False)])
def test_family_uses_the_colour_map(df, name, aes_name, column, discrete):
    key = "color" if aes_name == "color" else "fill"
    got = point_colours(render(df, aes_name, column, name), key)
    want = point_colours(direct(df, aes_name, column, name, discrete), key)
    assert got == want


def test_maps_differ_from_each_other(df):
    a = point_colours(render(df, "color", "g", "viridis"), "color")
    b = point_colours(render(df, "color", "g", "magma"), "color")
    assert a != b


def test_no_warning(df):
    plot = render(df, "color", "g", "plasma")
    from viz_factory.checked_plot import plot_warnings
    assert plot_warnings(plot) == []
