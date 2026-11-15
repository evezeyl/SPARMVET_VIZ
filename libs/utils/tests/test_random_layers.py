"""Which layers of a plot are random: one rule for the factory (which seeds them) and the recipe checker (which
accepts `random_state` on them and only on them). SEED-HOLDS-1, ADR-104.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_random_layers.py -q
"""
import pytest

from utils.random_layers import ALWAYS_RANDOM, is_random_layer


@pytest.mark.parametrize("name", ALWAYS_RANDOM)
def test_a_component_that_is_random_by_itself_is_a_random_layer(name):
    assert is_random_layer(name, {}) and is_random_layer(name, None)


def test_the_always_random_components_are_the_ones_found_by_drawing_twice():
    # libs/viz_factory/tests/test_every_component_randomness.py draws every registered component twice;
    # this list must be what that scan finds
    assert set(ALWAYS_RANDOM) == {"geom_jitter", "position_jitter", "position_jitterdodge", "geom_sina", "stat_sina"}


@pytest.mark.parametrize("position", ["jitter", "jitterdodge"])
def test_any_layer_with_a_jitter_position_is_random(position):
    assert is_random_layer("geom_point", {"position": position})
    assert is_random_layer("geom_boxplot", {"position": position})


@pytest.mark.parametrize("name, params", [
    ("stat_summary", {"fun_data": "mean_cl_boot"}),
    ("stat_summary_bin", {"fun_data": "mean_cl_boot", "bins": 5}),
    ("geom_pointrange", {"stat": "summary", "fun_data": "mean_cl_boot"}),
    ("geom_crossbar", {"stat": "summary_bin", "fun_data": "mean_cl_boot"}),
])
def test_a_bootstrapped_summary_is_a_random_layer(name, params):
    assert is_random_layer(name, params)


@pytest.mark.parametrize("name, params", [
    ("geom_point", {}),
    ("geom_point", {"position": "dodge"}),
    ("geom_bar", None),
    ("stat_summary", {}),                                   # default mean_se: not random
    ("stat_summary", {"fun_data": "mean_se"}),
    ("geom_pointrange", {"fun_data": "mean_cl_boot"}),       # the identity stat never reads fun_data
    ("geom_point", {"stat": "summary", "fun_data": "mean_sdl"}),
    ("theme_bw", {}),
])
def test_everything_else_is_not_random(name, params):
    assert not is_random_layer(name, params)
