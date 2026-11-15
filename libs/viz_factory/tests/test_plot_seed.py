"""SEED-HOLDS-1 (ADR-104, ADR-090 point 2): which seed a plot uses, in one place.

Order of precedence, per random layer: a seed pinned by an audit step (cascade level L5)  >  the number written on
that layer in the recipe  >  the library default 0 when the layer writes none. HOME draws no seed (Eve, 2026-11-15).
A layer that writes `random_state: null` asks for a random arrangement and takes the seed an export draws for it.

The pure rule is `resolve_layer_seeds` (one seed per random LAYER: a layer's number never flows to another layer);
the cascade applies a drawn seed through `render(..., drawn_random_state=...)`.
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
    recipe_asks_random,
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


def positions(df, layers, **render_kwargs) -> np.ndarray:
    """The real jittered positions of the first point layer of a rendered plot."""
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": layers}
    plot = VizFactory().render(df, {"plots": {"p": spec}, "plot_defaults": {}}, "p", **render_kwargs)
    return np.asarray(plot.draw().axes[0].collections[0].get_offsets()).copy()


def jitter(**params):
    return [{"name": "geom_point", "params": {"position": "jitter", **params}}]


# ---------------------------------------------------------------------------
# the pure rule, per layer
# ---------------------------------------------------------------------------

def seeds_of(layers, audit_pin=None, drawn=None, default=0):
    return [(ls.seed, ls.source) for ls in resolve_layer_seeds(layers, audit_pin, drawn, default=default)]


def test_no_jitter_means_no_seed():
    assert resolve_layer_seeds([{"name": "geom_bar"}], audit_pin=777, drawn=5, default=0) == ()


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
    layers = jitter()
    assert seeds_of(layers, default=0) == [(0, "default")]
    assert seeds_of(layers, drawn=5, default=0) == [(0, "default")], "a drawn seed is for null only: HOME draws nothing"
    assert recipe_asks_random(layers) is False


@pytest.mark.parametrize("written", [None, "random", " Random "])
def test_null_or_random_in_the_recipe_takes_the_seed_drawn_for_it(written):
    layers = jitter(random_state=written)
    assert seeds_of(layers, drawn=5) == [(5, "drawn")]
    assert recipe_asks_random(layers) is True
    assert fixed_seed_of(layers) is None
    with pytest.raises(ValueError, match="random_state: null"):
        resolve_layer_seeds(layers, default=0)


def test_each_layer_has_its_own_seed_and_a_number_never_flows_to_another_layer():
    layers = [
        {"name": "geom_jitter", "params": {"random_state": 11}},
        {"name": "geom_bar"},
        {"name": "geom_jitter", "params": {"random_state": 22}},
        {"name": "geom_jitter", "params": {}},
        {"name": "geom_point", "params": {"position": "jitter", "random_state": None}},
        {"name": "geom_sina"},
    ]
    got = resolve_layer_seeds(layers, None, 5, default=0)
    assert got == (
        LayerSeed(0, "geom_jitter", 11, "recipe"),
        LayerSeed(2, "geom_jitter", 22, "recipe"),
        LayerSeed(3, "geom_jitter", 0, "default"),
        LayerSeed(4, "geom_point", 5, "drawn"),
        LayerSeed(5, "geom_sina", 0, "default"),
    )


def test_an_audit_pin_is_every_random_layers_seed():
    layers = [{"name": "geom_jitter", "params": {"random_state": 11}}, {"name": "geom_sina"}]
    assert seeds_of(layers, audit_pin=777, drawn=5) == [(777, "audit"), (777, "audit")]


def test_recipe_pins_random_state_agrees_with_fixed_seed_of():
    for written in (None, "random", " RANDOM ", 0, 5, "7"):
        layers = jitter(random_state=written)
        assert recipe_pins_random_state(layers) is (fixed_seed_of(layers) is not None)


# ---------------------------------------------------------------------------
# the cascade applies it
# ---------------------------------------------------------------------------

def test_a_drawn_seed_fills_only_the_layers_that_write_null():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [
        {"name": "geom_jitter", "params": {"random_state": 11}},
        {"name": "geom_jitter", "params": {}},
        {"name": "geom_jitter", "params": {"random_state": None}},
    ]}
    resolved = resolve_plot_config(spec, {}, None, drawn_random_state=99)
    seeds = [l["params"].get("random_state", "unwritten") for l in resolved["layers"] if l["name"] == "geom_jitter"]
    assert seeds == [11, "unwritten", 99], "a layer that writes nothing keeps the factory's seed"


def test_audit_pin_in_the_override_still_beats_the_recipe_and_the_drawn_seed():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [{"name": "geom_jitter", "params": {"random_state": 11}}]}
    resolved = resolve_plot_config(spec, {}, None, aesthetic_override={"random_state": 777}, drawn_random_state=99)
    assert [l["params"]["random_state"] for l in resolved["layers"] if l["name"] == "geom_jitter"] == [777]


def test_no_drawn_seed_changes_nothing():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [{"name": "geom_jitter", "params": {}}]}
    resolved = resolve_plot_config(spec, {}, None)
    jitter_layers = [l for l in resolved["layers"] if l["name"] == "geom_jitter"]
    assert len(jitter_layers) == 1 and "random_state" not in jitter_layers[0]["params"]


# ---------------------------------------------------------------------------
# real pictures: the seed is the seed
# ---------------------------------------------------------------------------

def test_recipe_seed_holds_over_a_drawn_seed_in_the_picture(df):
    held = positions(df, jitter(random_state=123), drawn_random_state=1111)
    assert np.array_equal(held, positions(df, jitter(random_state=123)))
    assert not np.array_equal(held, positions(df, jitter(random_state=1111)))


def test_a_layer_that_writes_no_seed_keeps_the_factory_seed_in_the_picture(df):
    assert np.array_equal(positions(df, jitter(), drawn_random_state=1111), positions(df, jitter(random_state=DEFAULT_RANDOM_STATE)))


def test_a_drawn_seed_replaces_null_in_the_picture(df):
    got = positions(df, jitter(random_state=None), drawn_random_state=1111)
    assert np.array_equal(got, positions(df, jitter(random_state=1111)))


def test_audit_pin_beats_recipe_seed_in_the_picture(df):
    pinned = positions(df, jitter(random_state=123), aesthetic_override={"random_state": 777}, drawn_random_state=123)
    assert np.array_equal(pinned, positions(df, jitter(random_state=777)))


def test_the_library_default_is_unchanged_when_nothing_is_drawn(df):
    assert np.array_equal(positions(df, jitter()), positions(df, jitter(random_state=DEFAULT_RANDOM_STATE)))
