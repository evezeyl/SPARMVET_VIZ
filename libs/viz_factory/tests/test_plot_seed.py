"""SEED-HOLDS-1 (ADR-104, ADR-090 point 2): which seed a plot uses, in one place.

Order of precedence: a seed pinned by an audit step (cascade level L5)  >  the seed written in the recipe
>  the seed a caller offers when the recipe writes none (HOME draws one per session)  >  the library default.

The pure rule is `resolve_layer_seeds` (one seed per random LAYER: a layer's number never flows to another layer); the cascade applies it through `render(..., fallback_random_state=...)`.
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
    layers_need_offered_seed,
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

def seeds_of(layers, audit_pin=None, offered=None, default=0):
    return [(ls.seed, ls.source) for ls in resolve_layer_seeds(layers, audit_pin, offered, default=default)]


def test_no_jitter_means_no_seed():
    assert resolve_layer_seeds([{"name": "geom_bar"}], audit_pin=777, offered=5, default=0) == ()


def test_audit_pin_beats_the_recipe_seed_and_the_offered_one():
    assert seeds_of(jitter(random_state=123), audit_pin=777, offered=5) == [(777, "audit")]


def test_recipe_seed_beats_the_offered_one():
    assert seeds_of(jitter(random_state=123), offered=5) == [(123, "recipe")]


def test_recipe_seed_zero_is_a_seed():
    # 0 is falsy: it must not be read as "no seed" (the plotnine trap, ADR-090)
    assert seeds_of(jitter(random_state=0), offered=5, default=9) == [(0, "recipe")]


def test_recipe_seed_given_as_text_is_a_seed():
    assert seeds_of(jitter(random_state="123"), offered=5) == [(123, "recipe")]


@pytest.mark.parametrize("written", [None, "random", " Random "])
def test_null_or_random_in_the_recipe_takes_the_offered_seed(written):
    layers = jitter(random_state=written)
    assert seeds_of(layers, offered=5) == [(5, "drawn")]
    assert recipe_asks_random(layers) is True
    assert fixed_seed_of(layers) is None


def test_no_seed_written_takes_the_offered_seed_else_the_default():
    layers = jitter()
    assert seeds_of(layers, offered=5) == [(5, "drawn")]
    assert seeds_of(layers, offered=None, default=0) == [(0, "default")]
    assert recipe_asks_random(layers) is False


def test_each_layer_has_its_own_seed_and_a_number_never_flows_to_another_layer():
    layers = [
        {"name": "geom_jitter", "params": {"random_state": 11}},
        {"name": "geom_bar"},
        {"name": "geom_jitter", "params": {"random_state": 22}},
        {"name": "geom_jitter", "params": {}},
        {"name": "geom_point", "params": {"position": "jitter", "random_state": None}},
    ]
    got = resolve_layer_seeds(layers, None, 5, default=0)
    assert got == (
        LayerSeed(0, "geom_jitter", 11, "recipe"),
        LayerSeed(2, "geom_jitter", 22, "recipe"),
        LayerSeed(3, "geom_jitter", 5, "drawn"),
        LayerSeed(4, "geom_point", 5, "drawn"),
    )
    # without an offered seed the unnumbered layers get the library default, never 11
    assert [ls.seed for ls in resolve_layer_seeds(layers, None, None, default=0)] == [11, 22, 0, 0]


def test_an_audit_pin_is_every_random_layers_seed():
    layers = [{"name": "geom_jitter", "params": {"random_state": 11}}, {"name": "geom_jitter", "params": {}}]
    assert seeds_of(layers, audit_pin=777, offered=5) == [(777, "audit"), (777, "audit")]


def test_an_offered_seed_is_needed_only_when_a_layer_writes_no_number_and_nothing_is_pinned():
    assert layers_need_offered_seed(jitter()) is True
    assert layers_need_offered_seed(jitter(random_state=None)) is True
    assert layers_need_offered_seed(jitter(random_state=0)) is False
    assert layers_need_offered_seed(jitter(), audit_pin=3) is False
    assert layers_need_offered_seed([{"name": "geom_bar"}]) is False
    mixed = [{"name": "geom_jitter", "params": {"random_state": 11}}, {"name": "geom_jitter", "params": {}}]
    assert layers_need_offered_seed(mixed) is True, "the unnumbered layer needs one although another has a number"


def test_recipe_pins_random_state_agrees_with_fixed_seed_of():
    for written in (None, "random", " RANDOM ", 0, 5, "7"):
        layers = jitter(random_state=written)
        assert recipe_pins_random_state(layers) is (fixed_seed_of(layers) is not None)


# ---------------------------------------------------------------------------
# the cascade applies it
# ---------------------------------------------------------------------------

def test_fallback_seed_fills_only_layers_without_a_number():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [
        {"name": "geom_jitter", "params": {"random_state": 11}},
        {"name": "geom_jitter", "params": {}},
        {"name": "geom_jitter", "params": {"random_state": None}},
    ]}
    resolved = resolve_plot_config(spec, {}, None, fallback_random_state=99)
    seeds = [l["params"].get("random_state") for l in resolved["layers"] if l["name"] == "geom_jitter"]
    assert seeds == [11, 99, 99]


def test_audit_pin_in_the_override_still_beats_the_recipe_and_the_fallback():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [{"name": "geom_jitter", "params": {"random_state": 11}}]}
    resolved = resolve_plot_config(spec, {}, None, aesthetic_override={"random_state": 777}, fallback_random_state=99)
    assert [l["params"]["random_state"] for l in resolved["layers"] if l["name"] == "geom_jitter"] == [777]


def test_fallback_none_changes_nothing():
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": [{"name": "geom_jitter", "params": {}}]}
    resolved = resolve_plot_config(spec, {}, None)
    jitter_layers = [l for l in resolved["layers"] if l["name"] == "geom_jitter"]
    assert len(jitter_layers) == 1 and "random_state" not in jitter_layers[0]["params"]


# ---------------------------------------------------------------------------
# real pictures: the seed is the seed
# ---------------------------------------------------------------------------

def test_recipe_seed_holds_over_a_fallback_seed_in_the_picture(df):
    held = positions(df, jitter(random_state=123), fallback_random_state=1111)
    assert np.array_equal(held, positions(df, jitter(random_state=123)))
    assert not np.array_equal(held, positions(df, jitter(random_state=1111)))


def test_fallback_seed_is_the_seed_of_the_picture_when_the_recipe_writes_none(df):
    assert np.array_equal(positions(df, jitter(), fallback_random_state=1111), positions(df, jitter(random_state=1111)))


def test_fallback_seed_replaces_null_in_the_picture(df):
    got = positions(df, jitter(random_state=None), fallback_random_state=1111)
    assert np.array_equal(got, positions(df, jitter(random_state=1111)))


def test_audit_pin_beats_recipe_seed_in_the_picture(df):
    pinned = positions(df, jitter(random_state=123), aesthetic_override={"random_state": 777}, fallback_random_state=123)
    assert np.array_equal(pinned, positions(df, jitter(random_state=777)))


def test_the_library_default_is_unchanged_when_nothing_is_offered(df):
    assert np.array_equal(positions(df, jitter()), positions(df, jitter(random_state=DEFAULT_RANDOM_STATE)))
