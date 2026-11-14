"""SEED-HOLDS-1 (ADR-104 point 3, ADR-090 point 2, ADR-097 point 2): one seed in every place.

The same plot gets the SAME seed in the HOME plot, the results-bundle plot, the reproducibility export's
record and its re-run, and the record (`seeds_per_plot`) holds the seed that was really used. Each
claim below compares the jittered positions of real renders, not only the number.

Places (the pure parts live in app/modules/plot_seeds.py, outside the Shiny handlers):
  HOME        home_plot_seed + render_seed_args  (what home_theater.py hands to the render)
  bundle      export_plot_seeds + render_seed_args  (what export_handlers.py hands to the render)
  record      seeds_per_plot_record  (effective_run.yaml)
  re-run      bake_plot_seeds -> the recipe the reproducibility export carries, rendered as written

Run: PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_plot_seeds.py -q
"""
import copy
import random

import matplotlib
import numpy as np
import polars as pl
import pytest

matplotlib.use("Agg")

from app.modules.plot_seeds import (
    SessionSeedDraws,
    bake_plot_seeds,
    export_plot_seeds,
    home_plot_seed,
    render_seed_args,
    seed_pins_from_home_state,
    seeds_per_plot_record,
    unfixed_seed_warning,
)
from viz_factory.viz_factory import DEFAULT_RANDOM_STATE, VizFactory

DEFAULT = DEFAULT_RANDOM_STATE
HOME_DRAW = 4242       # the number HOME drew for the session
EXPORT_DRAW = 999      # the number the export draws for a null plot never opened in HOME


@pytest.fixture(scope="module")
def df():
    rng = random.Random(11)
    return pl.DataFrame({
        "g": [rng.choice(["a", "b", "c"]) for _ in range(80)],
        "v": [rng.random() for _ in range(80)],
    })


def jitter_layers(**params):
    return [{"name": "geom_point", "params": {"position": "jitter", **params}}]


def recipe_with(layers):
    """A recipe with one plot, in the shape the engine carries (analysis_groups)."""
    return {"analysis_groups": {"grp": {"plots": {"p": {"spec": {"mapping": {"x": "g", "y": "v"}, "layers": layers}}}}}}


def positions(df, layers, **render_kwargs):
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": layers}
    plot = VizFactory().render(df, {"plots": {"p": spec}, "plot_defaults": {}}, "p", **render_kwargs)
    return np.asarray(plot.draw().axes[0].collections[0].get_offsets()).copy()


# The four cases of the task, as (id, recipe layers, audit pin)
CASES = {
    "recipe 123": (jitter_layers(random_state=123), None),
    "audit pin 777 over recipe 123": (jitter_layers(random_state=123), 777),
    "audit pin 777, recipe writes none": (jitter_layers(), 777),
    "no seed": (jitter_layers(), None),
    "null": (jitter_layers(random_state=None), None),
}
EXPECTED_SEED = {
    "recipe 123": 123,
    "audit pin 777 over recipe 123": 777,
    "audit pin 777, recipe writes none": 777,
    "no seed": HOME_DRAW,
    "null": HOME_DRAW,
}


def all_places(df, layers, pin):
    """Run one plot through the four places; return (positions per place, record)."""
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    overrides = {"random_state": pin} if pin is not None else None

    # HOME: the plot shown (the handler reads the pin from home_state's t3_plot_overrides)
    home_seed = home_plot_seed(layers, pin, draws, "p", default=DEFAULT)
    home = positions(df, layers, **render_seed_args(home_seed, overrides))

    # bundle plot: the export reuses HOME's drawn seed (last_drawn_seeds) and the audit pin
    last_drawn = {"p": draws.get("p")} if draws.has("p") else {}
    seeds = export_plot_seeds({"p": {"layers": layers}}, {"p": pin} if pin is not None else {}, last_drawn,
                              default=DEFAULT, draw=lambda: EXPORT_DRAW)
    bundle = positions(df, layers, **render_seed_args(seeds["p"], overrides))

    # record: effective_run.yaml's seeds_per_plot must reproduce the exported plot on its own
    record = seeds_per_plot_record(seeds)
    from_record = positions(df, layers, aesthetic_override={"random_state": record["p"]})

    # re-run: the reproducibility recipe, rendered as written, with no override at all
    baked = bake_plot_seeds(recipe_with(layers), seeds)
    rerun_layers = baked["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"]
    rerun = positions(df, rerun_layers)
    return {"HOME": home, "bundle": bundle, "record": from_record, "re-run": rerun}, record, home_seed


@pytest.mark.parametrize("case", list(CASES))
def test_every_place_draws_the_same_picture(df, case):
    layers, pin = CASES[case]
    pics, record, _ = all_places(df, layers, pin)
    for place, pic in pics.items():
        assert np.array_equal(pic, pics["HOME"]), f"{case}: {place} differs from the HOME plot"


@pytest.mark.parametrize("case", list(CASES))
def test_the_record_holds_the_seed_that_was_really_used(df, case):
    layers, pin = CASES[case]
    pics, record, home_seed = all_places(df, layers, pin)
    assert record == {"p": EXPECTED_SEED[case]}
    assert home_seed.seed == EXPECTED_SEED[case]
    # and it is the seed of the pictures, not just a number
    assert np.array_equal(pics["HOME"], positions(df, copy.deepcopy(layers), aesthetic_override={"random_state": EXPECTED_SEED[case]}))


def test_the_recipe_seed_is_not_replaced_by_the_drawn_one(df):
    layers = jitter_layers(random_state=123)
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    ps = home_plot_seed(layers, None, draws, "p", default=DEFAULT)
    assert (ps.seed, ps.source) == (123, "recipe")
    assert not draws.has("p"), "a recipe seed needs no draw"
    shown = positions(df, layers, **render_seed_args(ps, None))
    assert np.array_equal(shown, positions(df, jitter_layers(random_state=123)))
    assert not np.array_equal(shown, positions(df, jitter_layers(random_state=HOME_DRAW)))


def test_recipe_seed_zero_holds(df):
    layers = jitter_layers(random_state=0)
    pics, record, _ = all_places(df, layers, None)
    assert record == {"p": 0}
    assert np.array_equal(pics["HOME"], pics["re-run"])


# ---------------------------------------------------------------------------
# the drawn seed is stable for the session and the plot
# ---------------------------------------------------------------------------

def test_the_drawn_seed_is_stable_for_the_session_and_the_plot():
    draws = SessionSeedDraws()
    first = draws.get("p")
    assert all(draws.get("p") == first for _ in range(20)), "a tab switch must not redraw the seed"
    layers = jitter_layers()
    assert home_plot_seed(layers, None, draws, "p", default=DEFAULT).seed == first


def test_two_sessions_draw_independently():
    seeds = {SessionSeedDraws().get("p") for _ in range(5)}
    assert len(seeds) > 1


def test_each_plot_has_its_own_draw():
    draws = SessionSeedDraws()
    assert len({draws.get(f"p{i}") for i in range(5)}) > 1


# ---------------------------------------------------------------------------
# plots HOME never showed, and what the export records
# ---------------------------------------------------------------------------

def test_a_plot_never_opened_in_home_without_a_seed_uses_the_default_and_records_it(df):
    layers = jitter_layers()
    seeds = export_plot_seeds({"p": {"layers": layers}}, {}, {}, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    assert seeds_per_plot_record(seeds) == {"p": DEFAULT}
    assert np.array_equal(positions(df, layers, **render_seed_args(seeds["p"], None)),
                          positions(df, jitter_layers(random_state=DEFAULT)))


def test_a_null_plot_never_opened_in_home_is_exported_with_a_drawn_and_recorded_seed(df):
    layers = jitter_layers(random_state=None)
    seeds = export_plot_seeds({"p": {"layers": layers}}, {}, {}, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    assert seeds_per_plot_record(seeds) == {"p": EXPORT_DRAW}
    assert seeds["p"].source == "drawn"


def test_a_plot_with_no_jitter_has_no_seed_and_no_record(df):
    bars = [{"name": "geom_bar"}]
    seeds = export_plot_seeds({"p": {"layers": bars}}, {"p": 777}, {"p": 5}, default=DEFAULT, draw=lambda: 1)
    assert seeds_per_plot_record(seeds) == {}
    assert unfixed_seed_warning(seeds) is None


def test_the_record_covers_every_exported_jitter_plot():
    plots = {
        "a": {"layers": jitter_layers(random_state=1)},
        "b": {"layers": jitter_layers()},
        "c": {"layers": [{"name": "geom_bar"}]},
        "d": {"layers": jitter_layers(random_state=None)},
    }
    seeds = export_plot_seeds(plots, {}, {"b": 55}, default=DEFAULT, draw=lambda: 7)
    assert seeds_per_plot_record(seeds) == {"a": 1, "b": 55, "d": 7}


def test_the_audit_pin_is_read_even_when_the_audit_trail_is_off():
    """Reshuffle works without t3_sandbox_enabled; the export must still hold what the user saw."""
    home_state = {"t3_plot_overrides": {"subtab_p": {"random_state": 777}, "subtab_q": {"fill_color": "red"}}}
    assert seed_pins_from_home_state(home_state, ["p", "q", "r"]) == {"p": 777}
    assert seed_pins_from_home_state({}, ["p"]) == {}
    assert seed_pins_from_home_state(None, ["p"]) == {}


# ---------------------------------------------------------------------------
# the warning
# ---------------------------------------------------------------------------

def test_the_warning_names_only_plots_whose_seed_is_not_in_the_recipe_nor_pinned():
    plots = {
        "plot_recipe": {"layers": jitter_layers(random_state=123)},
        "plot_audit": {"layers": jitter_layers()},
        "plot_home": {"layers": jitter_layers()},
        "plot_null": {"layers": jitter_layers(random_state=None)},
    }
    seeds = export_plot_seeds(plots, {"plot_audit": 777}, {"plot_home": 5}, default=DEFAULT, draw=lambda: 7)
    text = unfixed_seed_warning(seeds)
    assert text is not None
    assert "plot_home" in text and "plot_null" in text
    assert "plot_recipe" not in text and "plot_audit" not in text
    assert "random_state" in text and "recipe" in text, "says in plain words what to write in the recipe"


def test_no_warning_when_every_seed_is_fixed_or_pinned():
    plots = {"a": {"layers": jitter_layers(random_state=1)}, "b": {"layers": jitter_layers()}}
    seeds = export_plot_seeds(plots, {"b": 2}, {"b": 99}, default=DEFAULT, draw=lambda: 7)
    assert unfixed_seed_warning(seeds) is None


# ---------------------------------------------------------------------------
# the recipe the reproducibility export carries
# ---------------------------------------------------------------------------

def test_baking_does_not_change_the_recipe_it_is_given():
    recipe = recipe_with(jitter_layers())
    before = copy.deepcopy(recipe)
    seeds = export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, {"p": 5}, default=DEFAULT, draw=lambda: 7)
    bake_plot_seeds(recipe, seeds)
    assert recipe == before


def test_baking_keeps_a_number_the_recipe_wrote_and_fills_the_others():
    layers = [
        {"name": "geom_jitter", "params": {"random_state": 11}},
        {"name": "geom_jitter", "params": {}},
        {"name": "geom_jitter", "params": {"random_state": None}},
        {"name": "geom_bar"},
    ]
    seeds = export_plot_seeds({"p": {"layers": layers}}, {}, {"p": 5}, default=DEFAULT, draw=lambda: 7)
    baked = bake_plot_seeds(recipe_with(layers), seeds)["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"]
    assert [l.get("params", {}).get("random_state") for l in baked] == [11, 11, 11, None]


def test_baking_an_audit_pin_overrides_every_jitter_layer():
    layers = [{"name": "geom_jitter", "params": {"random_state": 11}}, {"name": "geom_jitter", "params": {}}]
    seeds = export_plot_seeds({"p": {"layers": layers}}, {"p": 777}, {}, default=DEFAULT, draw=lambda: 7)
    baked = bake_plot_seeds(recipe_with(layers), seeds)["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"]
    assert [l["params"]["random_state"] for l in baked] == [777, 777]


def test_baking_a_plot_the_recipe_does_not_have_is_an_error_not_a_silent_skip():
    seeds = export_plot_seeds({"ghost": {"layers": jitter_layers()}}, {}, {}, default=DEFAULT, draw=lambda: 7)
    with pytest.raises(KeyError, match="ghost"):
        bake_plot_seeds(recipe_with(jitter_layers()), seeds)


def test_baking_leaves_plots_without_jitter_untouched():
    layers = [{"name": "geom_bar"}]
    seeds = export_plot_seeds({"p": {"layers": layers}}, {}, {}, default=DEFAULT, draw=lambda: 7)
    recipe = recipe_with(layers)
    assert bake_plot_seeds(recipe, seeds) == recipe
