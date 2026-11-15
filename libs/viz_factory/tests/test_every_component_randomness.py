"""Every registered plot component is drawn twice and compared: which are random, and are they all seeded?
(SEED-HOLDS-1, ADR-104 point 3 and ADR-090 point 2.)

Why: `geom_sina` was random and not seeded (two renders of one recipe differed, `random_state: 0` repeated); only
jitter had been looked at. So no component is assumed deterministic: each is drawn with the yaml_example of its
schema, with the seed 0 twice (they must draw the same picture) and with the seed 1 (a random one must draw another).

What cannot be drawn on a generic table is listed in `NOT_DRAWN` with the reason, and is checked by reading the module
of the plotnine object it wraps: no random number is used there.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_every_component_randomness.py -q
"""
import contextlib
import hashlib
import importlib
import inspect
import io
import random
import warnings

import matplotlib
import polars as pl
import pytest
import yaml

matplotlib.use("Agg")

import viz_factory  # noqa: F401  (importing it registers the components)
from utils.random_layers import ALWAYS_RANDOM
from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS
from viz_factory.viz_factory import VizFactory

# Components that a generic table cannot draw from their yaml_example, and why. Each is checked below: it must still
# fail to draw (so this list cannot go stale) and its plotnine module must hold no random number.
NOT_DRAWN = {
    **{name: "a facet only splits the table by a column; it needs a facetting column of its own"
       for name in ("facet_cols", "facet_grid", "facet_margins", "facet_rows", "facet_scales", "facet_space", "facet_wrap")},
    "coord_lims": "needs the limits of an axis; it only sets them",
    **{name: "a palette or a transform of an axis; the palette of the installed mizani cannot be built here"
       for name in ("scale_color_brewer", "scale_fill_brewer", "scale_fill_distiller", "scale_color_gradientn",
                    "scale_fill_gradientn", "scale_color_viridis_c", "scale_color_viridis_d", "scale_fill_viridis_c",
                    "scale_fill_viridis_d", "scale_x_timedelta", "scale_y_timedelta")},
    "theme_custom": "free-form theme settings",
    "stat_summary": "its yaml_example names no summary function a table can use; drawn below with explicit parameters",
    "stat_summary_bin": "same as stat_summary",
}
# Explicit layers for what the example cannot draw
EXPLICIT = {
    "stat_summary / mean_se": [{"name": "stat_summary", "params": {"fun_data": "mean_se"}}],
    "stat_summary / mean_cl_boot": [{"name": "stat_summary", "params": {"fun_data": "mean_cl_boot"}}],
    "stat_summary_bin / mean_se": [{"name": "stat_summary_bin", "params": {"fun_data": "mean_se", "bins": 5}}],
    "stat_summary_bin / mean_cl_boot": [{"name": "stat_summary_bin", "params": {"fun_data": "mean_cl_boot", "bins": 5}}],
    "geom_pointrange with stat summary / mean_cl_boot": [{"name": "geom_pointrange", "params": {"stat": "summary", "fun_data": "mean_cl_boot"}}],
    "geom_point with position jitter": [{"name": "geom_point", "params": {"position": "jitter"}}],
    "geom_point with position jitterdodge": [{"name": "geom_point", "params": {"position": "jitterdodge"}}],
}
EXPLICIT_RANDOM = {name for name in EXPLICIT if "cl_boot" in name or "jitter" in name}
MAPPINGS = (
    {"x": "g", "y": "v"}, {"x": "g", "y": "v", "fill": "h", "color": "h"}, {"x": "v", "y": "w"}, {"x": "v"},
    {"x": "v", "y": "w", "ymin": "v", "ymax": "w", "xmin": "v", "xmax": "w", "xend": "w", "yend": "w",
     "label": "g", "sample": "v", "angle": "v", "radius": "w"},
)


@pytest.fixture(scope="module")
def df():
    rng = random.Random(3)
    return pl.DataFrame({"g": [rng.choice("abc") for _ in range(60)], "h": [rng.choice("xy") for _ in range(60)],
                         "v": [rng.random() * 10 for _ in range(60)], "w": [rng.random() * 5 for _ in range(60)]})


def draw(df, layers, mapping, random_state) -> str:
    spec = {"mapping": mapping, "layers": layers}
    with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plot = VizFactory(random_state=random_state).render(df, {"plots": {"p": spec}, "plot_defaults": {}}, "p")
        buf = io.BytesIO()
        plot.draw().savefig(buf, format="png", dpi=20)
    return hashlib.sha256(buf.getvalue()).hexdigest()


def layers_of(name):
    example = COMPONENT_SCHEMAS[name].get("yaml_example")
    layers = yaml.safe_load(example)["layers"] if example else [{"name": name}]
    if not any(layer["name"].startswith(("geom_", "stat_")) for layer in layers):
        layers = [{"name": "geom_point"}] + layers
    for layer in layers:  # the example may write a seed (the recipe form): the scan is about what the factory does without one
        (layer.get("params") or {}).pop("random_state", None)
    return layers


def draw_three(df, layers):
    """(seed 0, seed 0 again, seed 1) hashes with the first mapping that draws, or None when none does.

    A random component that is seeded draws the same picture twice with one seed and another with the next seed.
    A random component that is NOT seeded breaks the first equality (the defect of geom_sina).
    """
    for mapping in MAPPINGS:
        try:
            first = draw(df, layers, mapping, 0)
        except Exception:
            continue
        return first, draw(df, layers, mapping, 0), draw(df, layers, mapping, 1)
    return None


@pytest.fixture(scope="module")
def scan(df):
    """{label: three hashes} for every component and every explicit case."""
    cases = {name: layers_of(name) for name in sorted(PLOT_COMPONENTS) if name not in NOT_DRAWN}
    cases.update(EXPLICIT)
    return {label: draw_three(df, layers) for label, layers in cases.items()}


def test_every_component_is_drawn_or_listed_with_its_reason(scan):
    undrawn = {label for label, trio in scan.items() if trio is None}
    assert not undrawn, f"cannot be drawn on the generic table and are not in NOT_DRAWN: {sorted(undrawn)}"
    assert set(NOT_DRAWN) <= set(PLOT_COMPONENTS), "NOT_DRAWN names a component that is not registered"


def test_the_components_that_cannot_be_drawn_still_cannot_and_use_no_random_number(df):
    for name, reason in NOT_DRAWN.items():
        if name in ("stat_summary", "stat_summary_bin"):
            continue  # covered by the explicit cases
        assert draw_three(df, layers_of(name)) is None, f"{name} can now be drawn: take it out of NOT_DRAWN"
        wraps = COMPONENT_SCHEMAS[name].get("wraps") or []
        if not wraps:
            continue
        wrapped = importlib.import_module(wraps[0]["lib"])
        for attr in wraps[0]["attr_path"]:
            wrapped = getattr(wrapped, attr)
        source = inspect.getsource(importlib.import_module(wrapped.__module__))
        assert "random" not in source.lower(), f"{name}: its plotnine module uses random numbers ({reason})"


def test_the_components_found_random_are_exactly_the_ones_the_factory_seeds(scan):
    """A seeded random component draws another picture with another seed; a component that does not use the seed
    does not (and is not random, or it fails the next test)."""
    found = {label for label, trio in scan.items() if trio[0] != trio[2]}
    assert found == set(ALWAYS_RANDOM) | EXPLICIT_RANDOM


def test_no_component_is_random_once_the_factory_seeds_it(scan):
    random_with_a_seed = sorted(label for label, trio in scan.items() if trio[0] != trio[1])
    assert not random_with_a_seed, f"drawn twice with one seed they differ: {random_with_a_seed}"


def test_a_non_random_case_is_not_flagged(scan):
    for label in ("stat_summary / mean_se", "stat_summary_bin / mean_se", "geom_point", "geom_bar"):
        trio = scan[label]
        assert trio[0] == trio[1] == trio[2], f"{label} is not random"
