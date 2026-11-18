"""The plot library and the recipe checker agree on the keys of `plot_defaults` (D-0220, D-0242).

One list: `recipe_spec.yaml`, read through `utils.recipe_check.plot_defaults_keys`. A key removed from the format that
reaches the library directly (a script, Blueprint's preview) is refused with a plain message, never ignored.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_plot_defaults_keys.py -q
"""
import matplotlib
import polars as pl
import pytest

matplotlib.use("Agg")

from utils.errors import VisualizationError
from utils.recipe_check import plot_defaults_keys
from viz_factory.checked_plot import plot_warnings
from viz_factory.plot_config_resolver import _VALID_PLOT_DEFAULTS_KEYS, resolve_plot_config
from viz_factory.viz_factory import VizFactory

REMOVED = ["default_font_family", "facet_panel_spacing", "legend_position", "optimisation"]
POINT = {"name": "geom_point", "params": {}}
DF = pl.DataFrame({"x": [1.0, 2.0], "y": [3.0, 4.0]})


def render(plot_defaults):
    recipe = {"plots": {"p": {"mapping": {"x": "x", "y": "y"}, "layers": [POINT]}}, "plot_defaults": plot_defaults}
    return VizFactory().render(DF, recipe, "p")


def test_the_library_list_is_the_list_of_the_checker():
    allowed, removed = plot_defaults_keys()
    assert _VALID_PLOT_DEFAULTS_KEYS == frozenset(allowed)
    assert sorted(allowed) == ["layers", "palette", "random_state", "theme"]
    assert sorted(removed) == sorted(REMOVED)


@pytest.mark.parametrize("key", REMOVED)
def test_a_removed_key_is_refused_with_its_name_and_a_remedy(key):
    with pytest.raises(VisualizationError) as raised:
        resolve_plot_config({}, {key: "x"}, None)
    assert key in str(raised.value)
    assert "theme" in raised.value.tip


@pytest.mark.parametrize("key", REMOVED)
def test_a_removed_key_stops_a_render_too(key):
    with pytest.raises(Exception) as raised:
        render({key: "x"})
    assert key in str(raised.value) or key in str(getattr(raised.value, "tip", ""))


def test_the_warning_for_a_mistyped_key_lists_the_real_keys_only():
    plot = render({"palete": "viridis"})
    text = " ".join(w.fix for w in plot_warnings(plot))
    for key in ("palette", "theme", "layers", "random_state"):
        assert key in text
    for key in REMOVED:
        assert key not in text
