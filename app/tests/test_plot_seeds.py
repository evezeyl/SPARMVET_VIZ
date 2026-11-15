"""SEED-HOLDS-1 (ADR-104 point 3, ADR-090 point 2, ADR-097 point 2): one seed in every place, per layer.

A seed written in the recipe holds, an audit pin is the same everywhere, and a layer that writes no number
never takes another layer's number. The same plot gets the SAME seeds in the HOME plot, the results-bundle
plot, the reproducibility export's record and its re-run, and the record holds the seeds that were really
used. Each claim compares the jittered positions of real renders, not only the numbers.

Places (the pure parts live in app/modules/plot_seeds.py, outside the Shiny handlers, which only call them):
  HOME        home_plot_seeds + render_seed_args  (what home_theater.py hands to the render)
  reference   reference_render_args               (the comparison pane, left)
  bundle      export_seed_plan + render_seed_args  (what export_handlers.py hands to the render)
  record      seeds_per_layer_record               (effective_run.yaml)
  re-run      bake_plot_seeds -> the recipe the reproducibility export carries, rendered as written
  direct      VizFactory.render with nothing offered (gallery, Blueprint): unchanged

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
    audit_pin_of,
    bake_plot_seeds,
    export_plot_seeds,
    export_seed_plan,
    home_layer_seeds,
    home_plot_seeds,
    reference_render_args,
    remember_drawn_seed,
    render_seed_args,
    seed_pins_from_home_state,
    seed_recipe_note,
    seed_sources_per_plot,
    seeds_added_to_recipe,
    seeds_per_layer_record,
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


def jl(**params):
    """One jittered point layer."""
    return {"name": "geom_point", "params": {"position": "jitter", **params}}


def jitter_layers(**params):
    return [jl(**params)]


def recipe_with(layers):
    """A recipe with one plot, in the shape the engine carries (analysis_groups)."""
    return {"analysis_groups": {"grp": {"plots": {"p": {"spec": {"mapping": {"x": "g", "y": "v"}, "layers": layers}}}}}}


def positions(df, layers, **render_kwargs):
    """The jittered positions of every point layer of the plot, stacked."""
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": layers}
    plot = VizFactory().render(df, {"plots": {"p": spec}, "plot_defaults": {}}, "p", **render_kwargs)
    cols = plot.draw().axes[0].collections
    return np.vstack([np.asarray(c.get_offsets()) for c in cols]).copy()


def explicit(layers, seeds):
    """The same layers with the given numbers written on the jitter layers (in order)."""
    out, it = copy.deepcopy(layers), iter(seeds)
    for layer in out:
        if (layer.get("params") or {}).get("position") == "jitter":
            layer["params"]["random_state"] = next(it)
    return out


# (recipe layers, audit pin, the seed each jitter layer must get)
CASES = {
    "recipe 123": (jitter_layers(random_state=123), None, [123]),
    "audit pin 777 over recipe 123": (jitter_layers(random_state=123), 777, [777]),
    "audit pin 777, recipe writes none": (jitter_layers(), 777, [777]),
    "no seed": (jitter_layers(), None, [HOME_DRAW]),
    "null": (jitter_layers(random_state=None), None, [HOME_DRAW]),
    "two layers, two numbers": ([jl(random_state=11), jl(random_state=22)], None, [11, 22]),
    "one numbered, one not": ([jl(random_state=11), jl()], None, [11, HOME_DRAW]),
    "one not, one numbered": ([jl(), jl(random_state=11)], None, [HOME_DRAW, 11]),
    "one numbered, one null": ([jl(random_state=11), jl(random_state=None)], None, [11, HOME_DRAW]),
    "both unnumbered": ([jl(), jl()], None, [HOME_DRAW, HOME_DRAW]),
    "audit pin over two numbers": ([jl(random_state=11), jl(random_state=22)], 777, [777, 777]),
    "audit pin over one numbered, one not": ([jl(random_state=11), jl()], 777, [777, 777]),
}


def all_places(df, layers, pin):
    """Run one plot through the places; return (pictures per place, seeds of the bundle, seeds of HOME)."""
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    home_state = {"t3_plot_overrides": {"subtab_p": {"random_state": pin}}} if pin is not None else {}
    overrides = {"random_state": pin} if pin is not None else None

    home_seeds = home_plot_seeds(layers, home_state, draws, "p", default=DEFAULT)
    home = positions(df, layers, **render_seed_args(home_seeds, overrides))

    # bundle plot: the export reuses HOME's drawn seed (last_drawn_seeds) and the pin from home_state
    last_drawn = {"p": draws.get("p")} if draws.has("p") else {}
    plan = export_seed_plan({"p": {"layers": layers}}, home_state, last_drawn, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    bundle = positions(df, layers, **render_seed_args(plan["p"], overrides))

    # record: effective_run.yaml's seeds_per_layer must reproduce the exported plot on its own
    from_record = positions(df, explicit(layers, [r["seed"] for r in seeds_per_layer_record(plan)["p"]]))

    # re-run: the reproducibility recipe, rendered as written, with no override at all
    baked = bake_plot_seeds(recipe_with(layers), plan)
    rerun = positions(df, baked["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"])
    return {"HOME": home, "bundle": bundle, "record": from_record, "re-run": rerun}, plan, home_seeds


@pytest.mark.parametrize("case", list(CASES))
def test_every_place_draws_the_picture_of_the_seeds_each_layer_must_get(df, case):
    layers, pin, expected = CASES[case]
    pics, plan, home_seeds = all_places(df, layers, pin)
    want = positions(df, explicit(layers, expected))
    for place, pic in pics.items():
        assert np.array_equal(pic, want), f"{case}: {place} is not the picture of seeds {expected}"
    assert [ls.seed for ls in home_seeds] == expected
    assert [ls.seed for ls in plan["p"]] == expected


@pytest.mark.parametrize("case", list(CASES))
def test_the_record_holds_the_seeds_that_were_really_used(case):
    layers, pin, expected = CASES[case]
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    home_state = {"t3_plot_overrides": {"subtab_p": {"random_state": pin}}} if pin is not None else {}
    home_plot_seeds(layers, home_state, draws, "p", default=DEFAULT)
    plan = export_seed_plan({"p": {"layers": layers}}, home_state, {"p": draws.get("p")} if draws.has("p") else {},
                            default=DEFAULT, draw=lambda: EXPORT_DRAW)
    per_layer = seeds_per_layer_record(plan)["p"]
    assert [r["seed"] for r in per_layer] == expected
    assert [r["layer_index"] for r in per_layer] == list(range(len(layers)))
    plot_record = seeds_per_plot_record(plan)["p"]
    assert plot_record == (expected[0] if len(set(expected)) == 1 else expected)
    words = {r["source"] for r in per_layer}
    assert seed_sources_per_plot(plan)["p"] == (words.pop() if len(words) == 1 else "mixed")


def test_the_mixed_plot_the_unnumbered_layer_never_takes_the_other_layers_number(df):
    """The changed picture of the review: layer 0 writes 11, layer 1 writes none."""
    layers = [jl(random_state=11), jl()]
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    home = home_plot_seeds(layers, {}, draws, "p", default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in home] == [(11, "recipe"), (HOME_DRAW, "drawn")]
    shown = positions(df, layers, **render_seed_args(home, None))
    assert not np.array_equal(shown, positions(df, explicit(layers, [11, 11])))
    assert np.array_equal(shown, positions(df, explicit(layers, [11, HOME_DRAW])))
    # a direct render (gallery, Blueprint): the unnumbered layer gets the library default, as before
    assert np.array_equal(positions(df, layers), positions(df, explicit(layers, [11, DEFAULT])))


def test_the_recipe_seed_is_not_replaced_by_the_drawn_one(df):
    layers = jitter_layers(random_state=123)
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    seeds = home_layer_seeds(layers, None, draws, "p", default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in seeds] == [(123, "recipe")]
    assert not draws.has("p"), "a recipe seed needs no draw"
    shown = positions(df, layers, **render_seed_args(seeds, None))
    assert np.array_equal(shown, positions(df, jitter_layers(random_state=123)))
    assert not np.array_equal(shown, positions(df, jitter_layers(random_state=HOME_DRAW)))


def test_recipe_seed_zero_holds(df):
    layers = jitter_layers(random_state=0)
    pics, plan, _ = all_places(df, layers, None)
    assert seeds_per_plot_record(plan) == {"p": 0}
    assert np.array_equal(pics["HOME"], pics["re-run"])


# ---------------------------------------------------------------------------
# HOME handler lines, as pure functions (what the handler passes in and gets back)
# ---------------------------------------------------------------------------

def test_home_does_not_draw_over_a_recipe_seed_in_the_handler_path():
    """The HOME handler calls home_plot_seeds with home_state: a recipe seed must come back as it is."""
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    seeds = home_plot_seeds(jitter_layers(random_state=123), {"t3_plot_overrides": {}}, draws, "p", default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in seeds] == [(123, "recipe")]
    assert render_seed_args(seeds, None)["fallback_random_state"] is None


def test_home_reads_the_audit_pin_whatever_the_audit_trail_flag():
    """No flag is an argument of the HOME path: the pin in home_state is the seed (Reshuffle works without
    t3_sandbox_enabled)."""
    state = {"t3_plot_overrides": {"subtab_p": {"random_state": 777, "alpha": 0.3}}}
    seeds = home_plot_seeds(jitter_layers(random_state=123), state, SessionSeedDraws(), "p", default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in seeds] == [(777, "audit")]
    assert render_seed_args(seeds, state["t3_plot_overrides"]["subtab_p"]) == {
        "aesthetic_override": {"random_state": 777, "alpha": 0.3}, "fallback_random_state": None}
    assert audit_pin_of(state, "p") == 777 and audit_pin_of(state, "q") is None and audit_pin_of(None, "p") is None


def test_the_reference_pane_has_the_seeds_of_my_view_without_the_audit_pin(df):
    layers = [jl(random_state=11), jl()]
    draws = SessionSeedDraws(draw=lambda: HOME_DRAW)
    shown_seeds = home_plot_seeds(layers, {}, draws, "p", default=DEFAULT)
    args = reference_render_args(layers, draws, "p", default=DEFAULT)
    assert args == render_seed_args(shown_seeds, None)
    assert args["fallback_random_state"] == HOME_DRAW, "the reference pane was rendered without the seed"
    assert np.array_equal(positions(df, layers, **args), positions(df, explicit(layers, [11, HOME_DRAW])))
    # the pin is a change the user made: the reference pane does not apply it
    pinned = {"t3_plot_overrides": {"subtab_p": {"random_state": 777}}}
    assert reference_render_args(layers, draws, "p", default=DEFAULT) == args
    assert home_plot_seeds(layers, pinned, draws, "p", default=DEFAULT)[0].seed == 777


def test_the_stored_drawn_seed_is_written_once_per_plot_and_session():
    draws = SessionSeedDraws()
    layers = jitter_layers()
    seeds = home_layer_seeds(layers, None, draws, "p", default=DEFAULT)
    stored = remember_drawn_seed({}, "p", seeds)
    assert stored == {"p": draws.get("p")}, "the number HOME showed is the number stored"
    for _ in range(5):                      # the Effect runs again and again: nothing changes
        again = home_layer_seeds(layers, None, draws, "p", default=DEFAULT)
        assert remember_drawn_seed(stored, "p", again) is None
    assert remember_drawn_seed(stored, "q", home_layer_seeds(layers, None, draws, "q", default=DEFAULT)) is not None
    assert remember_drawn_seed({}, "p", home_layer_seeds(jitter_layers(random_state=1), None, draws, "p", default=DEFAULT)) is None
    assert remember_drawn_seed({}, "p", ()) is None


def test_the_export_reads_the_pin_from_home_state_whatever_the_audit_trail_flag():
    state = {"t3_plot_overrides": {"subtab_p": {"random_state": 777}, "subtab_q": {"fill_color": "red"}}}
    plan = export_seed_plan({"p": {"layers": jitter_layers(random_state=123)}, "q": {"layers": jitter_layers()}},
                            state, {"q": 5}, default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(777, "audit")]
    assert [(ls.seed, ls.source) for ls in plan["q"]] == [(5, "drawn")]
    assert seed_pins_from_home_state(state, ["p", "q", "r"]) == {"p": 777}
    assert seed_pins_from_home_state({}, ["p"]) == {} and seed_pins_from_home_state(None, ["p"]) == {}


# ---------------------------------------------------------------------------
# the drawn seed is stable for the session and the plot
# ---------------------------------------------------------------------------

def test_the_drawn_seed_is_stable_for_the_session_and_the_plot():
    draws = SessionSeedDraws()
    first = draws.get("p")
    assert all(draws.get("p") == first for _ in range(20)), "a tab switch must not redraw the seed"
    assert home_layer_seeds(jitter_layers(), None, draws, "p", default=DEFAULT)[0].seed == first


def test_two_sessions_draw_independently():
    assert len({SessionSeedDraws().get("p") for _ in range(5)}) > 1


def test_each_plot_has_its_own_draw():
    draws = SessionSeedDraws()
    assert len({draws.get(f"p{i}") for i in range(5)}) > 1


# ---------------------------------------------------------------------------
# plots HOME never showed, and what the export records
# ---------------------------------------------------------------------------

def test_a_plot_never_opened_in_home_without_a_seed_uses_the_default_and_records_it(df):
    layers = jitter_layers()
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, {}, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    assert seeds_per_plot_record(plan) == {"p": DEFAULT}
    assert seed_sources_per_plot(plan) == {"p": "default"}
    assert np.array_equal(positions(df, layers, **render_seed_args(plan["p"], None)),
                          positions(df, jitter_layers(random_state=DEFAULT)))


def test_a_null_plot_never_opened_in_home_is_exported_with_a_drawn_and_recorded_seed():
    plan = export_plot_seeds({"p": {"layers": jitter_layers(random_state=None)}}, {}, {}, default=DEFAULT,
                             draw=lambda: EXPORT_DRAW)
    assert seeds_per_plot_record(plan) == {"p": EXPORT_DRAW}
    assert plan["p"][0].source == "drawn"


def test_a_plot_with_no_jitter_has_no_seed_and_no_record():
    plan = export_plot_seeds({"p": {"layers": [{"name": "geom_bar"}]}}, {"p": 777}, {"p": 5}, default=DEFAULT,
                             draw=lambda: 1)
    assert seeds_per_plot_record(plan) == {} and seeds_per_layer_record(plan) == {}
    assert unfixed_seed_warning(plan) is None


def test_the_record_covers_every_exported_jitter_plot():
    plots = {
        "a": {"layers": jitter_layers(random_state=1)},
        "b": {"layers": jitter_layers()},
        "c": {"layers": [{"name": "geom_bar"}]},
        "d": {"layers": jitter_layers(random_state=None)},
    }
    plan = export_plot_seeds(plots, {}, {"b": 55}, default=DEFAULT, draw=lambda: 7)
    assert seeds_per_plot_record(plan) == {"a": 1, "b": 55, "d": 7}
    assert set(seeds_per_layer_record(plan)) == {"a", "b", "d"}


def test_the_record_per_layer_names_each_layer_its_seed_and_its_source():
    layers = [{"name": "geom_bar"}, jl(random_state=11), jl()]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, {"p": 5}, default=DEFAULT)
    assert seeds_per_layer_record(plan) == {"p": [
        {"layer_index": 1, "layer": "geom_point", "seed": 11, "source": "recipe"},
        {"layer_index": 2, "layer": "geom_point", "seed": 5, "source": "drawn"},
    ]}
    assert seeds_per_plot_record(plan) == {"p": [11, 5]}
    assert seed_sources_per_plot(plan) == {"p": "mixed"}


# ---------------------------------------------------------------------------
# the warning
# ---------------------------------------------------------------------------

def test_the_warning_names_only_plots_whose_seed_is_not_in_the_recipe_nor_pinned():
    plots = {
        "plot_recipe": {"layers": jitter_layers(random_state=123)},
        "plot_audit": {"layers": jitter_layers()},
        "plot_home": {"layers": jitter_layers()},
        "plot_null": {"layers": jitter_layers(random_state=None)},
        "plot_default": {"layers": jitter_layers()},
        "plot_mixed": {"layers": [jl(random_state=1), jl()]},
    }
    plan = export_plot_seeds(plots, {"plot_audit": 777}, {"plot_home": 5, "plot_mixed": 6}, default=DEFAULT,
                             draw=lambda: 7)
    text = unfixed_seed_warning(plan)
    assert text is not None
    for named in ("plot_home", "plot_null", "plot_default", "plot_mixed"):
        assert named in text, f"{named}: its seed is not fixed in the recipe"
    assert "plot_recipe" not in text and "plot_audit" not in text
    assert "random_state" in text and "recipe" in text, "says in plain words what to write in the recipe"


def test_a_plot_whose_seed_source_is_default_is_warned_about():
    plan = export_plot_seeds({"only_default": {"layers": jitter_layers()}}, {}, {}, default=DEFAULT)
    assert plan["only_default"][0].source == "default"
    assert "only_default" in unfixed_seed_warning(plan)


def test_no_warning_when_every_seed_is_fixed_or_pinned():
    plots = {"a": {"layers": jitter_layers(random_state=1)}, "b": {"layers": jitter_layers()}}
    plan = export_plot_seeds(plots, {"b": 2}, {"b": 99}, default=DEFAULT, draw=lambda: 7)
    assert unfixed_seed_warning(plan) is None


# ---------------------------------------------------------------------------
# the recipe the reproducibility export carries
# ---------------------------------------------------------------------------

def baked_layers(layers, plan):
    return bake_plot_seeds(recipe_with(layers), plan)["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"]


def test_baking_does_not_change_the_recipe_it_is_given():
    recipe = recipe_with(jitter_layers())
    before = copy.deepcopy(recipe)
    bake_plot_seeds(recipe, export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, {"p": 5}, default=DEFAULT))
    assert recipe == before


def test_baking_keeps_a_number_the_recipe_wrote_and_fills_only_the_layers_without_one():
    layers = [jl(random_state=11), jl(), jl(random_state=None), {"name": "geom_bar"}]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, {"p": 5}, default=DEFAULT, draw=lambda: 7)
    baked = baked_layers(layers, plan)
    assert [l.get("params", {}).get("random_state") for l in baked] == [11, 5, 5, None]


def test_baking_two_different_numbers_keeps_both():
    layers = [jl(random_state=11), jl(random_state=22)]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, {}, default=DEFAULT)
    assert [l["params"]["random_state"] for l in baked_layers(layers, plan)] == [11, 22]


def test_baking_an_audit_pin_overrides_every_jitter_layer():
    layers = [jl(random_state=11), jl()]
    plan = export_plot_seeds({"p": {"layers": layers}}, {"p": 777}, {}, default=DEFAULT)
    assert [l["params"]["random_state"] for l in baked_layers(layers, plan)] == [777, 777]


def test_baking_a_plot_the_recipe_does_not_have_is_an_error_not_a_silent_skip():
    plan = export_plot_seeds({"ghost": {"layers": jitter_layers()}}, {}, {}, default=DEFAULT)
    with pytest.raises(KeyError, match="ghost"):
        bake_plot_seeds(recipe_with(jitter_layers()), plan)


def test_baking_a_layer_the_recipe_does_not_have_is_an_error():
    plan = export_plot_seeds({"p": {"layers": [jl(), jl()]}}, {}, {}, default=DEFAULT)
    with pytest.raises(KeyError, match="layer 1"):
        bake_plot_seeds(recipe_with([jl()]), plan)
    with pytest.raises(KeyError, match="layer 0"):
        bake_plot_seeds(recipe_with([{"name": "geom_bar"}]), plan)


def test_baking_leaves_plots_without_jitter_untouched():
    layers = [{"name": "geom_bar"}]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, {}, default=DEFAULT)
    recipe = recipe_with(layers)
    assert bake_plot_seeds(recipe, plan) == recipe


# ---------------------------------------------------------------------------
# what the export tells about the seeds it wrote into the recipe
# ---------------------------------------------------------------------------

def test_the_seeds_added_to_the_recipe_are_listed_with_what_the_recipe_wrote():
    layers = [jl(random_state=11), jl(), jl(random_state=None)]
    plots = {"p": {"layers": layers}, "q": {"layers": jitter_layers(random_state=3)}}
    plan = export_plot_seeds(plots, {}, {"p": 5}, default=DEFAULT)
    assert seeds_added_to_recipe(plan, plots) == [
        {"plot": "p", "layer_index": 1, "layer": "geom_point", "seed": 5, "source": "drawn", "recipe_wrote": None},
        {"plot": "p", "layer_index": 2, "layer": "geom_point", "seed": 5, "source": "drawn", "recipe_wrote": None},
    ]
    pinned = export_plot_seeds(plots, {"q": 9}, {}, default=DEFAULT)
    assert seeds_added_to_recipe(pinned, plots)[-1] == {
        "plot": "q", "layer_index": 0, "layer": "geom_point", "seed": 9, "source": "audit", "recipe_wrote": 3}


def test_the_note_for_the_readme_names_every_added_seed_and_is_empty_when_none_was_added():
    plots = {"p": {"layers": [jl(random_state=11), jl()]}}
    note = "\n".join(seed_recipe_note(export_plot_seeds(plots, {}, {"p": 5}, default=DEFAULT), plots))
    assert "plot p, layer 1" in note and "random_state 5" in note and "no number" in note
    assert "layer 0" not in note, "a number the recipe wrote is not an added seed"
    fixed = {"p": {"layers": jitter_layers(random_state=1)}}
    assert seed_recipe_note(export_plot_seeds(fixed, {}, {}, default=DEFAULT), fixed) == []
    over = "\n".join(seed_recipe_note(export_plot_seeds(fixed, {"p": 9}, {}, default=DEFAULT), fixed))
    assert "recipe wrote 1" in over


# ---------------------------------------------------------------------------
# an audit pin reaches the render even when the other overrides are absent
# ---------------------------------------------------------------------------

@pytest.mark.parametrize("recipe_layers", [jitter_layers(random_state=123), jitter_layers(), [jl(random_state=11), jl()]])
def test_the_bundle_plot_follows_an_audit_pin_when_the_audit_trail_is_off(df, recipe_layers):
    """With t3_sandbox_enabled off the export has no aesthetic overrides at all, but Reshuffle still
    pinned a seed in HOME: the exported plot must be the one the user saw."""
    pin = 777
    state = {"t3_plot_overrides": {"subtab_p": {"random_state": pin}}}
    home = positions(df, recipe_layers, **render_seed_args(
        home_plot_seeds(recipe_layers, state, SessionSeedDraws(draw=lambda: HOME_DRAW), "p", default=DEFAULT),
        {"random_state": pin}))
    plan = export_seed_plan({"p": {"layers": recipe_layers}}, state, {}, default=DEFAULT)
    assert np.array_equal(positions(df, recipe_layers, **render_seed_args(plan["p"], None)), home)
    assert np.array_equal(home, positions(df, explicit(recipe_layers, [pin] * len(recipe_layers))))


def test_other_overrides_are_kept_next_to_the_seed():
    draws = SessionSeedDraws(draw=lambda: 5)
    drawn = home_layer_seeds(jitter_layers(), None, draws, "p", default=DEFAULT)
    assert render_seed_args(drawn, {"alpha": 0.3}) == {"aesthetic_override": {"alpha": 0.3}, "fallback_random_state": 5}
    audit = home_layer_seeds(jitter_layers(), 777, draws, "p", default=DEFAULT)
    assert render_seed_args(audit, {"alpha": 0.3}) == {
        "aesthetic_override": {"alpha": 0.3, "random_state": 777}, "fallback_random_state": None}
    assert render_seed_args((), None) == {"aesthetic_override": None, "fallback_random_state": None}
