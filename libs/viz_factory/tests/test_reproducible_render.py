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
    "geom_sina": ([{"name": "geom_sina"}], None),
    "stat_sina": ([{"name": "stat_sina"}], None),
    "bootstrapped summary": ([{"name": "stat_summary", "params": {"fun_data": "mean_cl_boot"}}], None),
    "geom_point with stat sina": ([{"name": "geom_point", "params": {"stat": "sina"}}], None),
    "position written position_jitter": ([{"name": "geom_point", "params": {"position": "position_jitter"}}], None),
    "position written position_jitterdodge": ([{"name": "geom_point", "params": {"position": "position_jitterdodge"}}], {"x": "g", "y": "v", "fill": "h"}),
    "stat written stat_sina": ([{"name": "geom_point", "params": {"stat": "stat_sina"}}], None),
    "stat written stat_summary": ([{"name": "geom_pointrange", "params": {"stat": "stat_summary"}}], None),
    "summary with no function named (plotnine's default is the bootstrap)": ([{"name": "stat_summary"}], None),
    "bootstrapped summary on a geom": ([{"name": "geom_pointrange", "params": {"stat": "summary", "fun_data": "mean_cl_boot"}}], None),
}


@pytest.mark.parametrize("route", list(JITTER_ROUTES))
def test_jitter_renders_identically_every_time(df, route):
    layers, mapping = JITTER_ROUTES[route]
    hashes = {render_bytes(VizFactory(), df, layers, mapping) for _ in range(RENDERS)}
    assert len(hashes) == 1, f"{route}: {RENDERS} renders gave {len(hashes)} different pictures"


@pytest.mark.parametrize("route", [r for r in JITTER_ROUTES if r != "jitterdodge on a geom"])
def test_a_different_factory_seed_gives_a_different_arrangement(df, route):
    layers, mapping = JITTER_ROUTES[route]
    default = render_bytes(VizFactory(), df, layers, mapping)
    other = render_bytes(VizFactory(random_state=DEFAULT_RANDOM_STATE + 7), df, layers, mapping)
    assert default != other
    assert other == render_bytes(VizFactory(random_state=DEFAULT_RANDOM_STATE + 7), df, layers, mapping)


@pytest.mark.parametrize("layers", [
    [{"name": "geom_sina", "params": {"random_state": 5}}],
    [{"name": "stat_summary", "params": {"fun_data": "mean_cl_boot", "random_state": 5}}],
])
def test_a_seed_written_on_sina_or_a_bootstrapped_summary_wins_over_the_factory_seed(df, layers):
    assert render_bytes(VizFactory(random_state=1), df, layers) == render_bytes(VizFactory(random_state=2), df, layers)


def test_random_state_zero_repeats_on_sina(df):
    layers = [{"name": "geom_sina", "params": {"random_state": 0}}]
    assert len({render_bytes(VizFactory(random_state=None), df, layers) for _ in range(RENDERS)}) == 1


def test_a_layer_can_set_its_own_seed(df):
    mine = [{"name": "geom_point"}, {"name": "position_jitter", "params": {"random_state": 123}}]
    a = render_bytes(VizFactory(random_state=1), df, mine)
    b = render_bytes(VizFactory(random_state=2), df, mine)
    assert a == b, "a seed set on the layer wins over the factory seed"


def test_plots_without_randomness_are_unchanged_by_the_seed(df):
    layers = [{"name": "geom_boxplot"}]
    assert render_bytes(VizFactory(), df, layers) == render_bytes(VizFactory(random_state=99), df, layers)


# --- PROVISIONAL (S1, Eve's rule of 2026-11-15): a seed is a number; null and "random" are refused ---------------


@pytest.mark.parametrize("written", [None, "random", " Random ", "abc", 1.5])
@pytest.mark.parametrize("layers", [
    [{"name": "geom_point"}, {"name": "position_jitter", "params": {"random_state": "?"}}],
    [{"name": "geom_point", "params": {"position": "jitter", "random_state": "?"}}],
    [{"name": "geom_jitter", "params": {"random_state": "?"}}],
    [{"name": "geom_sina", "params": {"random_state": "?"}}],
    [{"name": "stat_summary", "params": {"fun_data": "mean_cl_boot", "random_state": "?"}}],
])
def test_a_recipe_that_writes_null_or_random_is_refused_with_the_fix(df, layers, written):
    import copy
    from utils.errors import VisualizationError
    layers = copy.deepcopy(layers)
    for layer in layers:
        if (layer.get("params") or {}).get("random_state") == "?":
            layer["params"]["random_state"] = written
    with pytest.raises(VisualizationError) as raised:
        render_bytes(VizFactory(), df, layers)
    assert "random_state: 0" in raised.value.tip and "number" in str(raised.value).lower()


def test_the_factory_handle_for_tests_stays_a_factory_can_be_unseeded_for_all_its_jitter(df):
    """VizFactory(random_state=None) is the library handle for a test that needs a different arrangement each time;
    it is not a recipe key. Kept on purpose (S1)."""
    layers = [{"name": "geom_point", "params": {"position": "jitter"}}]
    hashes = {render_bytes(VizFactory(random_state=None), df, layers) for _ in range(RENDERS)}
    assert len(hashes) > 1


def test_seed_zero_really_seeds_the_arrangement(df):
    """plotnine treats random_state=0 as no seed; a generator object makes 0 work (ADR-090)."""
    layers = [{"name": "geom_point"}, {"name": "position_jitter", "params": {"random_state": 0}}]
    assert len({render_bytes(VizFactory(random_state=None), df, layers) for _ in range(RENDERS)}) == 1


def test_the_default_seed_is_the_number_zero(df):
    """Written as the literal: a test that compares with DEFAULT_RANDOM_STATE cannot see the constant change."""
    assert DEFAULT_RANDOM_STATE == 0 and VizFactory().default_random_state == 0
    for layers in ([{"name": "geom_point", "params": {"position": "jitter"}}], [{"name": "geom_sina"}],
                   [{"name": "geom_point", "params": {"stat": "sina"}}]):
        written = [dict(layer, params={**layer.get("params", {}), "random_state": 0}) for layer in layers]
        assert render_bytes(VizFactory(), df, layers) == render_bytes(VizFactory(random_state=None), df, written)
