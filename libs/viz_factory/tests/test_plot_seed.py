"""SEED-HOLDS-1 (ADR-104, ADR-090 point 2): which seed a plot uses, in one place.

Order of precedence, per random layer: a seed pinned by an audit step (cascade level L5)  >  the number written on
that layer in the recipe  >  the library default 0 when the layer writes none. HOME draws no seed (Eve, 2026-11-15).
`random_state: null` and the word random are refused (PROVISIONAL S1, Eve's rule of 2026-11-15): a seed is a number.

The pure rule is `resolve_layer_seeds` (one seed per random LAYER: a layer's number never flows to another layer);
the cascade applies an audit pin through `render(..., aesthetic_override={"random_state": n})`.
Every test that claims a picture compares the real jittered positions, not only the number.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_plot_seed.py -q
"""
import random

import matplotlib
import numpy as np
import polars as pl
import pytest

matplotlib.use("Agg")

from viz_factory.plot_config_resolver import (
    LayerSeed,
    fixed_seed_of,
    recipe_pins_random_state,
    resolve_layer_seeds,
    resolve_plot_config,
)
from viz_factory.viz_factory import DEFAULT_RANDOM_STATE, VizFactory


@pytest.fixture(scope="module")
def df():
    rng = random.Random(11)
    return pl.DataFrame({
        "g": [rng.choice(["a", "b", "c"]) for _ in range(80)],
        "v": [rng.random() for _ in range(80)],
    })


def positions(df, layers, plot_defaults=None, **render_kwargs) -> np.ndarray:
    """The real jittered positions of the first point layer of a rendered plot."""
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": layers}
    plot = VizFactory().render(df, {"plots": {"p": spec}, "plot_defaults": plot_defaults or {}}, "p", **render_kwargs)
    return np.asarray(plot.draw().axes[0].collections[0].get_offsets()).copy()


def jitter(**params):
    return [{"name": "geom_point", "params": {"position": "jitter", **params}}]


# ---------------------------------------------------------------------------
# the pure rule, per layer
# ---------------------------------------------------------------------------

def seeds_of(layers, audit_pin=None, default=0, recipe_default=None):
    return [(ls.seed, ls.source) for ls in resolve_layer_seeds(layers, audit_pin, default=default, recipe_default=recipe_default)]


def test_no_jitter_means_no_seed():
    assert resolve_layer_seeds([{"name": "geom_bar"}], audit_pin=777, default=0) == ()


def test_audit_pin_beats_the_recipe_seed():
    assert seeds_of(jitter(random_state=123), audit_pin=777) == [(777, "audit")]


def test_recipe_seed_holds():
    assert seeds_of(jitter(random_state=123)) == [(123, "recipe")]


def test_recipe_seed_zero_is_a_seed():
    # 0 is falsy: it must not be read as "no seed" (the plotnine trap, ADR-090)
    assert seeds_of(jitter(random_state=0), default=9) == [(0, "recipe")]


def test_recipe_seed_given_as_text_is_a_seed():
    assert seeds_of(jitter(random_state="123")) == [(123, "recipe")]


def test_no_seed_written_takes_the_default():
    assert seeds_of(jitter(), default=0) == [(0, "default")]
    assert seeds_of(jitter(), default=9) == [(9, "default")], "the default is the factory's seed"


def test_each_layer_has_its_own_seed_and_a_number_never_flows_to_another_layer():
    layers = [
        {"name": "geom_jitter", "params": {"random_state": 11}},
        {"name": "geom_bar"},
        {"name": "geom_jitter", "params": {"random_state": 22}},
        {"name": "geom_jitter", "params": {}},
        {"name": "geom_point", "params": {"position": "jitter", "random_state": 33}},
        {"name": "geom_sina"},
    ]
    got = resolve_layer_seeds(layers, None, default=0)
    assert got == (
        LayerSeed(0, "geom_jitter", 11, "recipe"),
        LayerSeed(2, "geom_jitter", 22, "recipe"),
        LayerSeed(3, "geom_jitter", 0, "default"),
        LayerSeed(4, "geom_point", 33, "recipe"),
        LayerSeed(5, "geom_sina", 0, "default"),
    )


def test_an_audit_pin_is_every_random_layers_seed():
    layers = [{"name": "geom_jitter", "params": {"random_state": 11}}, {"name": "geom_sina"}]
    assert seeds_of(layers, audit_pin=777) == [(777, "audit"), (777, "audit")]


def test_recipe_pins_random_state_agrees_with_fixed_seed_of():
    for written in (None, "random", " RANDOM ", 0, 5, "7"):
        layers = jitter(random_state=written)
        assert recipe_pins_random_state(layers) is (fixed_seed_of(layers) is not None)


# ---------------------------------------------------------------------------
# the cascade applies it
# ---------------------------------------------------------------------------

def test_audit_pin_in_the_override_still_beats_the_recipe():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [{"name": "geom_jitter", "params": {"random_state": 11}}]}
    resolved = resolve_plot_config(spec, {}, None, aesthetic_override={"random_state": 777})
    assert [l["params"]["random_state"] for l in resolved["layers"] if l["name"] == "geom_jitter"] == [777]


def test_a_layer_that_writes_no_seed_is_left_to_the_factory():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [{"name": "geom_jitter", "params": {}}]}
    resolved = resolve_plot_config(spec, {}, None)
    jitter_layers = [l for l in resolved["layers"] if l["name"] == "geom_jitter"]
    assert len(jitter_layers) == 1 and "random_state" not in jitter_layers[0]["params"]


# ---------------------------------------------------------------------------
# real pictures: the seed is the seed
# ---------------------------------------------------------------------------

def test_audit_pin_beats_recipe_seed_in_the_picture(df):
    pinned = positions(df, jitter(random_state=123), aesthetic_override={"random_state": 777})
    assert np.array_equal(pinned, positions(df, jitter(random_state=777)))
    assert not np.array_equal(pinned, positions(df, jitter(random_state=123)))


def test_a_layer_that_writes_no_seed_has_the_factory_seed_in_the_picture(df):
    assert np.array_equal(positions(df, jitter()), positions(df, jitter(random_state=DEFAULT_RANDOM_STATE)))


# ---------------------------------------------------------------------------
# PROVISIONAL (S3): plot_defaults.random_state, the one seed of the whole recipe
# order: audit pin > the layer's own number > plot_defaults.random_state > the factory's 0
# ---------------------------------------------------------------------------

def test_the_recipe_default_is_the_seed_of_a_layer_that_writes_none_and_says_so():
    assert seeds_of(jitter(), recipe_default=7) == [(7, "recipe default")]
    assert seeds_of(jitter(), recipe_default=0, default=9) == [(0, "recipe default")], "0 is a seed, not nothing"


def test_the_order_audit_pin_then_layer_number_then_recipe_default_then_zero():
    layers = [{"name": "geom_jitter", "params": {"random_state": 11}}, {"name": "geom_jitter", "params": {}}]
    assert seeds_of(layers, recipe_default=7) == [(11, "recipe"), (7, "recipe default")]
    assert seeds_of(layers, audit_pin=777, recipe_default=7) == [(777, "audit"), (777, "audit")]
    assert seeds_of(layers) == [(11, "recipe"), (0, "default")]


def test_the_recipe_default_gives_the_seed_in_the_picture_and_a_layer_number_still_holds(df):
    assert np.array_equal(positions(df, jitter(), plot_defaults={"random_state": 7}), positions(df, jitter(random_state=7)))
    assert not np.array_equal(positions(df, jitter(), plot_defaults={"random_state": 7}), positions(df, jitter()))
    assert np.array_equal(positions(df, jitter(random_state=123), plot_defaults={"random_state": 7}), positions(df, jitter(random_state=123)))


def test_the_recipe_default_does_not_beat_an_audit_pin_in_the_picture(df):
    pinned = positions(df, jitter(), plot_defaults={"random_state": 7}, aesthetic_override={"random_state": 777})
    assert np.array_equal(pinned, positions(df, jitter(random_state=777)))


def test_the_recipe_default_reaches_every_random_component(df):
    for layers in ([{"name": "geom_sina"}], [{"name": "geom_point"}, {"name": "position_jitter"}], [{"name": "geom_jitter"}]):
        assert np.array_equal(positions(df, layers, plot_defaults={"random_state": 7}),
                              positions(df, [dict(l, params={"random_state": 7}) if l["name"] != "geom_point" else l for l in layers]))


@pytest.mark.parametrize("written", [None, "random", "abc"])
def test_a_recipe_default_of_null_or_random_is_refused_too(df, written):
    from utils.errors import VisualizationError
    with pytest.raises(VisualizationError) as raised:
        positions(df, jitter(), plot_defaults={"random_state": written})
    assert "random_state: 0" in raised.value.tip


def test_the_cascade_knows_the_key_and_does_not_call_it_unknown():
    resolved = resolve_plot_config({"mapping": {"x": "g", "y": "v"}, "layers": jitter()}, {"random_state": 7}, None)
    assert "random_state" not in resolved["_unknown_plot_defaults_keys"]
