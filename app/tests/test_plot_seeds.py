"""SEED-HOLDS-1 (ADR-104 point 3, ADR-090 point 2, ADR-097 point 2; Eve 2026-11-15): one seed in every place, per layer.

A seed written in the recipe holds. A layer that writes no seed uses the factory's seed, 0, in EVERY place: HOME
draws no seed. An audit pin is the same everywhere. A layer never takes another layer's number. Each claim compares
the jittered positions of real renders, not only the numbers.

Places (the pure parts live in app/modules/plot_seeds.py, outside the Shiny handlers, which only call them):
  HOME / reference pane   VizFactory.render(layers, aesthetic_override=the pin in home_state)  (home_theater.py)
  gallery / Blueprint     VizFactory.render(layers)                                          (nothing offered)
  bundle                  export_seed_plan + render_seed_args                                (export_handlers.py)
  record                  seeds_per_layer_record                                             (effective_run.yaml)
  re-run                  bake_plot_seeds -> the recipe the reproducibility export carries, rendered as written

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
    audit_pin_of,
    bake_plot_seeds,
    export_plot_seeds,
    export_seed_plan,
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


# (recipe layers, audit pin, the seed each jitter layer must get). `null` is the layer that asks for a random one.
CASES = {
    "recipe 123": (jitter_layers(random_state=123), None, [123]),
    "recipe 0": (jitter_layers(random_state=0), None, [0]),
    "audit pin 777 over recipe 123": (jitter_layers(random_state=123), 777, [777]),
    "audit pin 777, recipe writes none": (jitter_layers(), 777, [777]),
    "no seed": (jitter_layers(), None, [DEFAULT]),
    "two layers, two numbers": ([jl(random_state=11), jl(random_state=22)], None, [11, 22]),
    "one numbered, one not": ([jl(random_state=11), jl()], None, [11, DEFAULT]),
    "one not, one numbered": ([jl(), jl(random_state=11)], None, [DEFAULT, 11]),
    "both unnumbered": ([jl(), jl()], None, [DEFAULT, DEFAULT]),
    "audit pin over two numbers": ([jl(random_state=11), jl(random_state=22)], 777, [777, 777]),
    "audit pin over one numbered, one not": ([jl(random_state=11), jl()], 777, [777, 777]),
    "sina": ([{"name": "geom_sina"}], None, [DEFAULT]),
    "sina, recipe 5": ([{"name": "geom_sina", "params": {"random_state": 5}}], None, [5]),
}


def render_layers(layers, seeds):
    """The same layers with the given numbers written on the random layers (in order)."""
    out, it = copy.deepcopy(layers), iter(seeds)
    for layer in out:
        if (layer.get("params") or {}).get("position") == "jitter" or layer["name"] == "geom_sina":
            layer.setdefault("params", {})["random_state"] = next(it)
    return out


def all_places(df, layers, pin):
    """Run one plot through the places; return (pictures per place, the export's seeds)."""
    home_state = {"t3_plot_overrides": {"subtab_p": {"random_state": pin}}} if pin is not None else {}
    override = home_state["t3_plot_overrides"]["subtab_p"] if pin is not None else None

    home = positions(df, layers, aesthetic_override=override)          # the HOME handler's call
    reference = positions(df, layers)                                  # the comparison reference pane: no pin
    plan = export_seed_plan({"p": {"layers": layers}}, home_state, default=DEFAULT)
    bundle = positions(df, layers, **render_seed_args(plan["p"], override))
    from_record = positions(df, render_layers(layers, [r["seed"] for r in seeds_per_layer_record(plan)["p"]]))
    baked = bake_plot_seeds(recipe_with(layers), plan)
    rerun = positions(df, baked["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"])
    direct = positions(df, layers)                                     # gallery, Blueprint: nothing offered
    return {"HOME": home, "reference pane": reference, "bundle": bundle, "record": from_record, "re-run": rerun,
            "gallery / Blueprint": direct}, plan


@pytest.mark.parametrize("case", list(CASES))
def test_every_place_draws_the_picture_of_the_seeds_each_layer_must_get(df, case):
    layers, pin, expected = CASES[case]
    pics, plan = all_places(df, layers, pin)
    want = positions(df, render_layers(layers, expected))
    for place, pic in pics.items():
        if place in ("reference pane", "gallery / Blueprint") and pin is not None:
            continue  # the pin is a change the user made in HOME: these places do not apply it
        assert np.array_equal(pic, want), f"{case}: {place} is not the picture of seeds {expected}"
    assert [ls.seed for ls in plan["p"]] == expected


@pytest.mark.parametrize("case", list(CASES))
def test_the_record_holds_the_seeds_that_were_really_used(case):
    layers, pin, expected = CASES[case]
    home_state = {"t3_plot_overrides": {"subtab_p": {"random_state": pin}}} if pin is not None else {}
    plan = export_seed_plan({"p": {"layers": layers}}, home_state, default=DEFAULT)
    per_layer = seeds_per_layer_record(plan)["p"]
    assert [r["seed"] for r in per_layer] == expected
    plot_record = seeds_per_plot_record(plan)["p"]
    assert plot_record == (expected[0] if len(set(expected)) == 1 else expected)
    words = {r["source"] for r in per_layer}
    assert seed_sources_per_plot(plan)["p"] == (words.pop() if len(words) == 1 else "mixed")


def test_a_pin_changes_the_home_picture_and_the_reference_pane_does_not_apply_it(df):
    layers = jitter_layers(random_state=123)
    pic_home, pic_ref = positions(df, layers, aesthetic_override={"random_state": 777}), positions(df, layers)
    assert not np.array_equal(pic_home, pic_ref)
    assert np.array_equal(pic_ref, positions(df, render_layers(layers, [123])))


def test_the_mixed_plot_the_unnumbered_layer_never_takes_the_other_layers_number(df):
    """Layer 0 writes 11, layer 1 writes none: layer 1 has the factory's seed in every place."""
    layers = [jl(random_state=11), jl()]
    shown = positions(df, layers)
    assert not np.array_equal(shown, positions(df, render_layers(layers, [11, 11])))
    assert np.array_equal(shown, positions(df, render_layers(layers, [11, DEFAULT])))


def test_the_export_reads_the_pin_from_home_state_whatever_the_audit_trail_flag():
    """No flag is an argument of the export path: the pin in home_state is the seed (Reshuffle works without
    t3_sandbox_enabled)."""
    state = {"t3_plot_overrides": {"subtab_p": {"random_state": 777, "alpha": 0.3}, "subtab_q": {"fill_color": "red"}}}
    plan = export_seed_plan({"p": {"layers": jitter_layers(random_state=123)}, "q": {"layers": jitter_layers()}},
                            state, default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(777, "audit")]
    assert [(ls.seed, ls.source) for ls in plan["q"]] == [(DEFAULT, "default")]
    assert seed_pins_from_home_state(state, ["p", "q", "r"]) == {"p": 777}
    assert seed_pins_from_home_state({}, ["p"]) == {} and seed_pins_from_home_state(None, ["p"]) == {}
    assert audit_pin_of(state, "p") == 777 and audit_pin_of(state, "q") is None and audit_pin_of(None, "p") is None


# ---------------------------------------------------------------------------
# what the export records
# ---------------------------------------------------------------------------

def test_a_plot_without_a_seed_uses_the_default_and_records_it_as_default(df):
    layers = jitter_layers()
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    assert seeds_per_plot_record(plan) == {"p": DEFAULT}
    assert seed_sources_per_plot(plan) == {"p": "default"}
    assert np.array_equal(positions(df, layers, **render_seed_args(plan["p"], None)),
                          positions(df, jitter_layers(random_state=DEFAULT)))


def test_a_null_layer_is_exported_with_a_drawn_and_recorded_seed(df):
    layers = jitter_layers(random_state=None)
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    assert seeds_per_plot_record(plan) == {"p": EXPORT_DRAW}
    assert plan["p"][0].source == "drawn"
    assert np.array_equal(positions(df, layers, **render_seed_args(plan["p"], None)),
                          positions(df, jitter_layers(random_state=EXPORT_DRAW)))


def test_a_null_layer_next_to_a_layer_without_a_seed_keeps_the_other_layer_on_the_default(df):
    layers = [jl(random_state=None), jl()]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT, draw=lambda: EXPORT_DRAW)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(EXPORT_DRAW, "drawn"), (DEFAULT, "default")]
    assert np.array_equal(positions(df, layers, **render_seed_args(plan["p"], None)),
                          positions(df, render_layers(layers, [EXPORT_DRAW, DEFAULT])))


def test_a_plot_with_no_random_layer_has_no_seed_and_no_record():
    plan = export_plot_seeds({"p": {"layers": [{"name": "geom_bar"}]}}, {"p": 777}, default=DEFAULT, draw=lambda: 1)
    assert seeds_per_plot_record(plan) == {} and seeds_per_layer_record(plan) == {}
    assert unfixed_seed_warning(plan) is None


def test_the_record_covers_every_exported_random_plot():
    plots = {
        "a": {"layers": jitter_layers(random_state=1)},
        "b": {"layers": jitter_layers()},
        "c": {"layers": [{"name": "geom_bar"}]},
        "d": {"layers": jitter_layers(random_state=None)},
    }
    plan = export_plot_seeds(plots, {}, default=DEFAULT, draw=lambda: 7)
    assert seeds_per_plot_record(plan) == {"a": 1, "b": DEFAULT, "d": 7}
    assert set(seeds_per_layer_record(plan)) == {"a", "b", "d"}


def test_the_record_per_layer_names_each_layer_its_seed_and_its_source():
    layers = [{"name": "geom_bar"}, jl(random_state=11), jl()]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)
    assert seeds_per_layer_record(plan) == {"p": [
        {"layer_index": 1, "layer": "geom_point", "seed": 11, "source": "recipe"},
        {"layer_index": 2, "layer": "geom_point", "seed": DEFAULT, "source": "default"},
    ]}
    assert seeds_per_plot_record(plan) == {"p": [11, DEFAULT]}
    assert seed_sources_per_plot(plan) == {"p": "mixed"}


# ---------------------------------------------------------------------------
# the warning: only for a layer that asks for a random arrangement
# ---------------------------------------------------------------------------

def test_the_warning_names_only_plots_with_a_layer_that_writes_null():
    plots = {
        "plot_recipe": {"layers": jitter_layers(random_state=123)},
        "plot_audit": {"layers": jitter_layers(random_state=None)},
        "plot_null": {"layers": jitter_layers(random_state=None)},
        "plot_default": {"layers": jitter_layers()},
    }
    plan = export_plot_seeds(plots, {"plot_audit": 777}, default=DEFAULT, draw=lambda: 7)
    text = unfixed_seed_warning(plan)
    assert text is not None and "plot_null" in text
    for not_named in ("plot_recipe", "plot_audit", "plot_default"):
        assert not_named not in text
    assert "random_state" in text and "recipe" in text, "says in plain words what to write in the recipe"


def test_no_warning_when_nothing_asks_for_a_random_arrangement():
    """Nothing is unpinned any more: a layer without a seed uses 0, and the record says so."""
    plots = {"a": {"layers": jitter_layers(random_state=1)}, "b": {"layers": jitter_layers()}}
    assert unfixed_seed_warning(export_plot_seeds(plots, {"b": 2}, default=DEFAULT)) is None
    assert unfixed_seed_warning(export_plot_seeds(plots, {}, default=DEFAULT)) is None


# ---------------------------------------------------------------------------
# the recipe the reproducibility export carries
# ---------------------------------------------------------------------------

def baked_layers(layers, plan):
    return bake_plot_seeds(recipe_with(layers), plan)["analysis_groups"]["grp"]["plots"]["p"]["spec"]["layers"]


def test_baking_does_not_change_the_recipe_it_is_given():
    recipe = recipe_with(jitter_layers())
    before = copy.deepcopy(recipe)
    bake_plot_seeds(recipe, export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=DEFAULT))
    assert recipe == before


def test_baking_writes_the_default_so_that_every_seed_used_is_written():
    assert [l["params"]["random_state"] for l in baked_layers(jitter_layers(), export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=DEFAULT))] == [DEFAULT]


def test_baking_keeps_a_number_the_recipe_wrote_and_fills_the_others():
    layers = [jl(random_state=11), jl(), jl(random_state=None), {"name": "geom_bar"}]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT, draw=lambda: 7)
    assert [l.get("params", {}).get("random_state") for l in baked_layers(layers, plan)] == [11, DEFAULT, 7, None]


def test_baking_two_different_numbers_keeps_both():
    layers = [jl(random_state=11), jl(random_state=22)]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)
    assert [l["params"]["random_state"] for l in baked_layers(layers, plan)] == [11, 22]


def test_baking_an_audit_pin_overrides_every_random_layer():
    layers = [jl(random_state=11), jl()]
    plan = export_plot_seeds({"p": {"layers": layers}}, {"p": 777}, default=DEFAULT)
    assert [l["params"]["random_state"] for l in baked_layers(layers, plan)] == [777, 777]


def test_baking_a_plot_the_recipe_does_not_have_is_an_error_not_a_silent_skip():
    plan = export_plot_seeds({"ghost": {"layers": jitter_layers()}}, {}, default=DEFAULT)
    with pytest.raises(KeyError, match="ghost"):
        bake_plot_seeds(recipe_with(jitter_layers()), plan)


def test_baking_a_layer_the_recipe_does_not_have_is_an_error():
    plan = export_plot_seeds({"p": {"layers": [jl(), jl()]}}, {}, default=DEFAULT)
    with pytest.raises(KeyError, match="layer 1"):
        bake_plot_seeds(recipe_with([jl()]), plan)
    with pytest.raises(KeyError, match="layer 0"):
        bake_plot_seeds(recipe_with([{"name": "geom_bar"}]), plan)


def test_baking_leaves_plots_without_random_layers_untouched():
    layers = [{"name": "geom_bar"}]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)
    recipe = recipe_with(layers)
    assert bake_plot_seeds(recipe, plan) == recipe


# ---------------------------------------------------------------------------
# what the export tells about the seeds it wrote into the recipe
# ---------------------------------------------------------------------------

def test_the_seeds_added_to_the_recipe_are_listed_with_what_the_recipe_wrote():
    layers = [jl(random_state=11), jl(), jl(random_state=None)]
    plots = {"p": {"layers": layers}, "q": {"layers": jitter_layers(random_state=3)}}
    plan = export_plot_seeds(plots, {}, default=DEFAULT, draw=lambda: 5)
    assert seeds_added_to_recipe(plan, plots) == [
        {"plot": "p", "layer_index": 1, "layer": "geom_point", "seed": DEFAULT, "source": "default", "recipe_wrote": None},
        {"plot": "p", "layer_index": 2, "layer": "geom_point", "seed": 5, "source": "drawn", "recipe_wrote": None},
    ]
    pinned = export_plot_seeds(plots, {"q": 9}, default=DEFAULT, draw=lambda: 5)
    assert seeds_added_to_recipe(pinned, plots)[-1] == {
        "plot": "q", "layer_index": 0, "layer": "geom_point", "seed": 9, "source": "audit", "recipe_wrote": 3}


def test_the_note_for_the_readme_names_every_added_seed_and_is_empty_when_none_was_added():
    plots = {"p": {"layers": [jl(random_state=11), jl()]}}
    note = "\n".join(seed_recipe_note(export_plot_seeds(plots, {}, default=DEFAULT), plots))
    assert "plot p, layer 1" in note and f"random_state {DEFAULT}" in note and "no number" in note
    assert "layer 0" not in note, "a number the recipe wrote is not an added seed"
    fixed = {"p": {"layers": jitter_layers(random_state=1)}}
    assert seed_recipe_note(export_plot_seeds(fixed, {}, default=DEFAULT), fixed) == []
    over = "\n".join(seed_recipe_note(export_plot_seeds(fixed, {"p": 9}, default=DEFAULT), fixed))
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
    home = positions(df, recipe_layers, aesthetic_override={"random_state": pin})
    plan = export_seed_plan({"p": {"layers": recipe_layers}}, state, default=DEFAULT)
    assert np.array_equal(positions(df, recipe_layers, **render_seed_args(plan["p"], None)), home)
    assert np.array_equal(home, positions(df, render_layers(recipe_layers, [pin] * len(recipe_layers))))


def test_other_overrides_are_kept_next_to_the_seed():
    drawn = export_plot_seeds({"p": {"layers": jitter_layers(random_state=None)}}, {}, default=DEFAULT, draw=lambda: 5)["p"]
    assert render_seed_args(drawn, {"alpha": 0.3}) == {"aesthetic_override": {"alpha": 0.3}, "drawn_random_state": 5}
    audit = export_plot_seeds({"p": {"layers": jitter_layers()}}, {"p": 777}, default=DEFAULT)["p"]
    assert render_seed_args(audit, {"alpha": 0.3}) == {
        "aesthetic_override": {"alpha": 0.3, "random_state": 777}, "drawn_random_state": None}
    assert render_seed_args((), None) == {"aesthetic_override": None, "drawn_random_state": None}
