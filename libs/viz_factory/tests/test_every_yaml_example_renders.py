"""The yaml_example of every registered component renders and draws (VIZ-STANDARD-1, V6/V7).

# @deps
# consumes: libs/viz_factory/src/viz_factory/viz_factory.py, libs/viz_factory/src/viz_factory/registry.py
# @end_deps

The example a user copies from the help must work. Each example is put in a recipe on a table that has the columns
its geom needs (`shape_of`), then rendered and drawn. A component that cannot be given a fair table here is listed
in `NOT_JUDGED` with the reason; a component whose own example fails is listed in `KNOWN_DEFECTS` (strict xfail: the
test fails when the defect is fixed, so the entry is removed then). Neither list may hold a name that is not registered.
"""
import datetime as dt
import warnings

import matplotlib
import numpy as np
import polars as pl
import pytest
import yaml

matplotlib.use("Agg")

import viz_factory  # noqa: F401  (registers the components)
from matplotlib import pyplot as plt
from viz_factory.registry import COMPONENT_SCHEMAS
from viz_factory.viz_factory import VizFactory, draw_checked

N = 30
_rng = np.random.RandomState(1)
TABLE = pl.DataFrame({
    "x": _rng.rand(N) * 100, "y": _rng.rand(N) * 100, "v": _rng.rand(N) * 100, "s": _rng.rand(N),
    "g": ["a", "b", "c"] * 10, "Year": [2018 + i % 4 for i in range(N)], "Country": ["N", "S"] * 15,
    "d": [dt.date(2020, 1, 1) + dt.timedelta(days=10 * i) for i in range(N)],
    "dtm": [dt.datetime(2020, 1, 1) + dt.timedelta(days=10 * i) for i in range(N)],
    "td": [dt.timedelta(days=i) for i in range(N)],
    "lo": _rng.rand(N), "hi": _rng.rand(N) + 1, "xlo": _rng.rand(N), "xhi": _rng.rand(N) + 1, "xe": _rng.rand(N), "ye": _rng.rand(N),
    "lab": ["l"] * N, "colr": ["red", "blue", "green"] * 10, "shp": ["o", "s", "^"] * 10, "lt": ["solid", "dashed", "dotted"] * 10,
})

# components whose example cannot be judged on this table, with the reason
NOT_JUDGED = {
    "geom_smooth": "the example asks for loess, which needs scikit-misc (not installed)",
}
# components whose own example fails today: the defect, found by this test
KNOWN_DEFECTS = {
    "guide_label": "calls guide_legend(labels=...), which plotnine refuses",
    "facet_cols": "builds facet_grid(cols=..., **spec) and the key `cols` arrives twice",
    "facet_rows": "builds facet_grid(rows=..., **spec) and the key `rows` arrives twice",
    "facet_margins": "adds nothing to a plot that has no facet_grid: facet_null has no params (an own component that needs a facet before it)",
    "facet_scales": "same: needs a facet before it and fails on facet_null",
    "facet_space": "same: needs a facet before it and fails on facet_null",
}


def layers_of(name):
    return yaml.safe_load(COMPONENT_SCHEMAS[name]["yaml_example"])["layers"]


def shape_of(name, layers):
    """(extra first layer or None, mapping) that give the example a table it can draw."""
    names = [layer["name"] for layer in layers]
    geom = next((n for n in names if n.startswith(("geom_", "stat_"))), None)
    base = None if geom else "geom_point"
    mapping = {"x": "x", "y": "y"}
    focus = geom or name
    if focus in ("geom_bar", "stat_count") or name.startswith("position_") and focus in ("geom_bar", "stat_count"):
        mapping = {"x": "g", "fill": "g"}
    elif focus in ("geom_histogram", "geom_freqpoly", "stat_bin", "geom_density", "stat_density", "geom_dotplot"):
        mapping = {"x": "x"}
    elif focus in ("geom_violin", "geom_boxplot", "geom_sina", "stat_sina", "geom_col", "geom_jitter"):
        mapping = {"x": "g", "y": "v"}
    elif focus in ("geom_crossbar", "geom_errorbar", "geom_linerange", "geom_pointrange", "geom_ribbon"):
        mapping = {"x": "x", "y": "y", "ymin": "lo", "ymax": "hi"}
        if focus == "geom_crossbar":
            mapping["x"] = "g"
    elif focus == "geom_errorbarh":
        mapping = {"y": "g", "xmin": "xlo", "xmax": "xhi"}
    elif focus == "geom_rect":
        mapping = {"xmin": "xlo", "xmax": "xhi", "ymin": "lo", "ymax": "hi"}
    elif focus == "geom_segment":
        mapping = {"x": "x", "y": "y", "xend": "xe", "yend": "ye"}
    elif focus in ("geom_qq", "stat_qq", "geom_qq_line", "stat_qq_line"):
        mapping = {"sample": "v"}
    elif focus in ("geom_text", "geom_label"):
        mapping = {"x": "x", "y": "y", "label": "lab"}
    elif focus == "geom_spoke":
        mapping = {"x": "x", "y": "y", "angle": "s", "radius": "s"}
    elif focus == "geom_raster":
        mapping = {"x": "Year", "y": "s", "fill": "v"}
    elif focus in ("geom_bin_2d", "stat_bin_2d", "geom_pointdensity", "geom_density_2d", "geom_tile"):
        mapping = {"x": "x", "y": "y"}
    if name == "position_jitterdodge":
        mapping = {"x": "g", "y": "v", "fill": "g"}
    if name == "position_nudge":
        mapping = {"x": "x", "y": "y", "label": "lab"}
    continuous = ("continuous", "gradient", "distiller", "viridis_c", "_cmap", "cmap")
    if name.startswith("scale_"):
        kind = name.split("_")[1]
        if name.endswith("_identity"):
            column = {"color": "colr", "fill": "colr", "alpha": "s", "size": "s", "shape": "shp", "linetype": "lt", "stroke": "s"}[kind]
            mapping = {**mapping, ("colour" if kind == "color" else kind): column}
        elif kind in ("color", "fill", "alpha", "size", "stroke", "shape", "linetype"):
            wants_continuous = any(word in name for word in continuous) and not name.endswith("_d") and "discrete" not in name
            wants_continuous = wants_continuous or name in ("scale_alpha", "scale_size", "scale_size_area", "scale_stroke_continuous")
            column = "v" if wants_continuous else "g"
            mapping = {**mapping, kind: column}
        elif name.startswith(("scale_x_", "scale_y_")):
            axis = name[6]
            column = {"date": "d", "datetime": "dtm", "timedelta": "td", "discrete": "g"}.get(name.split("_")[-1])
            if column:
                mapping = {**mapping, axis: column}
            elif name.split("_")[-1] in ("log10", "sqrt", "symlog", "reverse", "continuous"):
                mapping = {**mapping, axis: "v"}
    if name.startswith("guide_") or name == "guides":
        mapping = {**mapping, "fill": "g", "color": "g"}
    return base, mapping


def recipe_of(name):
    layers = layers_of(name)
    base, mapping = shape_of(name, layers)
    layers = ([{"name": base}] if base else []) + layers
    return {"plots": {"p": {"target_dataset": "d", "mapping": mapping, "layers": layers}}}


def _draw(name):
    with warnings.catch_warnings():
        warnings.simplefilter("ignore")
        figure = draw_checked(VizFactory().render(TABLE, recipe_of(name), "p"))
    plt.close(figure)


def test_the_two_lists_name_registered_components_only():
    assert set(NOT_JUDGED) | set(KNOWN_DEFECTS) <= set(COMPONENT_SCHEMAS)


@pytest.mark.parametrize("name", [
    pytest.param(n, marks=pytest.mark.xfail(strict=True, reason=KNOWN_DEFECTS[n])) if n in KNOWN_DEFECTS else n
    for n in sorted(COMPONENT_SCHEMAS) if n not in NOT_JUDGED
])
def test_the_yaml_example_renders_and_draws(name):
    _draw(name)
