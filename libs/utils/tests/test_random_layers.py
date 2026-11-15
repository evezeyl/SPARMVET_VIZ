"""Which layers of a plot are random: one rule for the factory (which seeds them) and the recipe checker (which
accepts `random_state` on them and only on them). SEED-HOLDS-1, ADR-104.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/utils/tests/test_random_layers.py -q
"""
import pytest

from utils.random_layers import ALWAYS_RANDOM, is_random_layer, is_seed_value


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
    ("stat_summary", {"fun_data": "mean_se"}),
    ("geom_pointrange", {"fun_data": "mean_cl_boot"}),       # the identity stat never reads fun_data
    ("geom_point", {"stat": "summary", "fun_data": "mean_sdl"}),
    ("theme_bw", {}),
])
def test_everything_else_is_not_random(name, params):
    assert not is_random_layer(name, params)


# -- a random statistic or position named as a parameter of ANY layer (review of SEED-HOLDS-1) ---------------------

@pytest.mark.parametrize("name", ["geom_point", "geom_boxplot", "geom_line", "geom_text", "geom_pointrange"])
def test_any_geom_with_the_sina_statistic_is_random(name):
    assert is_random_layer(name, {"stat": "sina"})


@pytest.mark.parametrize("name, params", [
    ("stat_summary", {}),                                  # plotnine's default fun_data is mean_cl_boot: random
    ("stat_summary", {"fun_data": None}),
    ("geom_point", {"stat": "summary"}),
])
def test_a_summary_without_a_named_function_is_random_because_the_default_is_the_bootstrap(name, params):
    assert is_random_layer(name, params)


@pytest.mark.parametrize("fun_data", ["mean_se", "mean_cl_normal", "mean_sdl", "median_hilow"])
def test_a_summary_with_another_named_function_is_not_random(fun_data):
    assert not is_random_layer("stat_summary", {"fun_data": fun_data})
    assert not is_random_layer("geom_point", {"stat": "summary", "fun_data": fun_data})


def test_the_other_statistics_are_not_random():
    for stat in ("identity", "count", "bin", "density", "smooth", "boxplot", "ecdf", "unique", "sum", "ydensity"):
        assert not is_random_layer("geom_point", {"stat": stat})


@pytest.mark.parametrize("value", [0, 1, 42, "7", " 12 ", "-3"])
def test_a_seed_is_a_whole_number_or_its_text(value):
    assert is_seed_value(value)


@pytest.mark.parametrize("value", [None, "random", " Random ", "abc", "1.5", 1.5, True, False, [1], {"a": 1}, ""])
def test_everything_else_is_not_a_seed(value):
    assert not is_seed_value(value)


def test_a_binned_summary_is_random_only_with_the_bootstrap_named():
    """plotnine's default fun_data of stat_summary_bin is not the bootstrap (drawn unseeded, it repeats)."""
    for name, params in (("stat_summary_bin", {"bins": 4}), ("geom_pointrange", {"stat": "summary_bin", "bins": 4}),
                         ("stat_summary_bin", {"fun_data": "mean_se"})):
        assert not is_random_layer(name, params)
    assert is_random_layer("stat_summary_bin", {"fun_data": "mean_cl_boot"})
    assert is_random_layer("geom_pointrange", {"stat": "summary_bin", "fun_data": "mean_cl_boot"})
