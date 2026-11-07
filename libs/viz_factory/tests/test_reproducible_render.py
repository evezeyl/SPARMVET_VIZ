"""The same data and data analysis recipe must give the same picture, also for random scatter (jitter).

Every way jitter reaches a plot is seeded by default, a layer can set its own `random_state`, and
VizFactory(random_state=...) sets the default for a whole factory (the handle for tests that need
a known arrangement).

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_reproducible_render.py -q
"""
import hashlib
import io
import random

import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from viz_factory.viz_factory import DEFAULT_RANDOM_STATE, VizFactory

RENDERS = 3  # unseeded jitter differs on every render


@pytest.fixture(scope="module")
def df():
    rng = random.Random(11)
    return pl.DataFrame({
        "g": [rng.choice(["a", "b", "c"]) for _ in range(120)],
        "h": [rng.choice(["x", "y"]) for _ in range(120)],
        "v": [rng.random() for _ in range(120)],
    })


def render_bytes(factory, df, layers, mapping=None) -> str:
    spec = {"mapping": mapping or {"x": "g", "y": "v"}, "layers": layers}
    plot = factory.render(df, {"plots": {"p": spec}, "plot_defaults": {}}, "p")
    buf = io.BytesIO()
    plot.draw().savefig(buf, format="png", dpi=60)
    return hashlib.sha256(buf.getvalue()).hexdigest()


JITTER_ROUTES = {
    "position string on a geom": ([{"name": "geom_point", "params": {"position": "jitter"}}], None),
    "geom_jitter": ([{"name": "geom_jitter", "params": {}}], None),
    "position_jitter layer": ([{"name": "geom_point"}, {"name": "position_jitter"}], None),
    "jitterdodge on a geom": ([{"name": "geom_point", "params": {"position": "jitterdodge"}}], {"x": "g", "y": "v", "fill": "h"}),
}


@pytest.mark.parametrize("route", list(JITTER_ROUTES))
def test_jitter_renders_identically_every_time(df, route):
    layers, mapping = JITTER_ROUTES[route]
    hashes = {render_bytes(VizFactory(), df, layers, mapping) for _ in range(RENDERS)}
    assert len(hashes) == 1, f"{route}: {RENDERS} renders gave {len(hashes)} different pictures"


@pytest.mark.parametrize("route", ["position string on a geom", "geom_jitter", "position_jitter layer"])
def test_a_different_factory_seed_gives_a_different_arrangement(df, route):
    layers, mapping = JITTER_ROUTES[route]
    default = render_bytes(VizFactory(), df, layers, mapping)
    other = render_bytes(VizFactory(random_state=DEFAULT_RANDOM_STATE + 7), df, layers, mapping)
    assert default != other
    assert other == render_bytes(VizFactory(random_state=DEFAULT_RANDOM_STATE + 7), df, layers, mapping)


def test_a_layer_can_set_its_own_seed(df):
    mine = [{"name": "geom_point"}, {"name": "position_jitter", "params": {"random_state": 123}}]
    a = render_bytes(VizFactory(random_state=1), df, mine)
    b = render_bytes(VizFactory(random_state=2), df, mine)
    assert a == b, "a seed set on the layer wins over the factory seed"


def test_plots_without_randomness_are_unchanged_by_the_seed(df):
    layers = [{"name": "geom_boxplot"}]
    assert render_bytes(VizFactory(), df, layers) == render_bytes(VizFactory(random_state=99), df, layers)


# --- the seed is a default, not a rule: an explicit "random" gives a new arrangement each time ----


@pytest.mark.parametrize("unseeded", [None, "random"])
def test_a_layer_can_ask_for_a_different_arrangement_every_time(df, unseeded):
    layers = [{"name": "geom_point"}, {"name": "position_jitter", "params": {"random_state": unseeded}}]
    hashes = {render_bytes(VizFactory(), df, layers) for _ in range(RENDERS)}
    assert len(hashes) > 1, "random_state: null / random must not be seeded"


@pytest.mark.parametrize("unseeded", [None, "random"])
def test_a_factory_can_be_unseeded_for_all_its_jitter(df, unseeded):
    layers = [{"name": "geom_point", "params": {"position": "jitter"}}]
    hashes = {render_bytes(VizFactory(random_state=unseeded), df, layers) for _ in range(RENDERS)}
    assert len(hashes) > 1


def test_seed_zero_really_seeds_the_arrangement(df):
    """plotnine treats random_state=0 as no seed; a generator object makes 0 work (ADR-090)."""
    layers = [{"name": "geom_point"}, {"name": "position_jitter", "params": {"random_state": 0}}]
    assert len({render_bytes(VizFactory(random_state=None), df, layers) for _ in range(RENDERS)}) == 1
