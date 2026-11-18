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
    seed_pin_steps,
    with_seed_steps,
    reshuffle_offered,
    seed_caption,
    seed_in_use,
)
from viz_factory.viz_factory import DEFAULT_RANDOM_STATE, VizFactory

DEFAULT = DEFAULT_RANDOM_STATE
HOME_DRAW = 4242       # the number HOME drew for the session


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
    return {"analysis_groups": {"grp": {"plots": {"p": {"ui_label": "P", "mapping": {"x": "g", "y": "v"}, "layers": layers}}}}}


def positions(df, layers, plot_defaults=None, **render_kwargs):
    """The jittered positions of every point layer of the plot, stacked."""
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": layers}
    plot = VizFactory().render(df, {"plots": {"p": spec}, "plot_defaults": plot_defaults or {}}, "p", **render_kwargs)
    cols = plot.draw().axes[0].collections
    return np.vstack([np.asarray(c.get_offsets()) for c in cols]).copy()


def explicit(layers, seeds):
    """The same layers with the given numbers written on the jitter layers (in order)."""
    out, it = copy.deepcopy(layers), iter(seeds)
    for layer in out:
        if (layer.get("params") or {}).get("position") == "jitter":
            layer["params"]["random_state"] = next(it)
    return out


# (recipe layers, audit pin, the seed each jitter layer must get).
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
    rerun = positions(df, baked["analysis_groups"]["grp"]["plots"]["p"]["layers"])
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
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)
    assert seeds_per_plot_record(plan) == {"p": DEFAULT}
    assert seed_sources_per_plot(plan) == {"p": "default"}
    assert np.array_equal(positions(df, layers, **render_seed_args(plan["p"], None)),
                          positions(df, jitter_layers(random_state=DEFAULT)))


def test_a_plot_with_no_random_layer_has_no_seed_and_no_record():
    plan = export_plot_seeds({"p": {"layers": [{"name": "geom_bar"}]}}, {"p": 777}, default=DEFAULT)
    assert seeds_per_plot_record(plan) == {} and seeds_per_layer_record(plan) == {}


def test_the_record_covers_every_exported_random_plot():
    plots = {
        "a": {"layers": jitter_layers(random_state=1)},
        "b": {"layers": jitter_layers()},
        "c": {"layers": [{"name": "geom_bar"}]},
    }
    plan = export_plot_seeds(plots, {}, default=DEFAULT)
    assert seeds_per_plot_record(plan) == {"a": 1, "b": DEFAULT}
    assert set(seeds_per_layer_record(plan)) == {"a", "b"}


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

# ---------------------------------------------------------------------------
# the recipe the reproducibility export carries
# ---------------------------------------------------------------------------

def baked_layers(layers, plan):
    return bake_plot_seeds(recipe_with(layers), plan)["analysis_groups"]["grp"]["plots"]["p"]["layers"]


def test_baking_does_not_change_the_recipe_it_is_given():
    recipe = recipe_with(jitter_layers())
    before = copy.deepcopy(recipe)
    bake_plot_seeds(recipe, export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=DEFAULT))
    assert recipe == before


def test_baking_writes_the_default_so_that_every_seed_used_is_written():
    assert [l["params"]["random_state"] for l in baked_layers(jitter_layers(), export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=DEFAULT))] == [DEFAULT]


def test_baking_keeps_a_number_the_recipe_wrote_and_fills_the_others():
    layers = [jl(random_state=11), jl(), {"name": "geom_bar"}]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)
    assert [l.get("params", {}).get("random_state") for l in baked_layers(layers, plan)] == [11, DEFAULT, None]


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
    layers = [jl(random_state=11), jl()]
    plots = {"p": {"layers": layers}, "q": {"layers": jitter_layers(random_state=3)}}
    plan = export_plot_seeds(plots, {}, default=DEFAULT)
    assert seeds_added_to_recipe(plan, plots) == [
        {"plot": "p", "layer_index": 1, "layer": "geom_point", "seed": DEFAULT, "source": "default", "recipe_wrote": None},
    ]
    pinned = export_plot_seeds(plots, {"q": 9}, default=DEFAULT)
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
    plain = export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=DEFAULT)["p"]
    assert render_seed_args(plain, {"alpha": 0.3}) == {"aesthetic_override": {"alpha": 0.3}}
    audit = export_plot_seeds({"p": {"layers": jitter_layers()}}, {"p": 777}, default=DEFAULT)["p"]
    assert render_seed_args(audit, {"alpha": 0.3}) == {
        "aesthetic_override": {"alpha": 0.3, "random_state": 777}}
    assert render_seed_args((), None) == {"aesthetic_override": None}


# ---------------------------------------------------------------------------
# the audit pin is a step of the audit trail (Eve, 2026-11-15): listed in t3_steps.yaml, the Methods text and the
# audit trail table of the report, whatever the audit-trail flag
# ---------------------------------------------------------------------------

def test_a_pinned_plot_has_one_audit_step_that_says_the_seed_and_the_layers():
    plan = export_plot_seeds({"p": {"layers": [jl(random_state=11), {"name": "geom_bar"}, jl()]},
                              "q": {"layers": jitter_layers(random_state=3)}}, {"p": 777}, default=DEFAULT)
    steps = seed_pin_steps(plan)
    assert list(steps) == ["p"], "a plot that is not pinned has no step"
    (step,) = steps["p"]
    assert step["node_type"] == "random_seed"
    assert step["params"] == {"seed": 777, "layers": [0, 2]}
    assert step["reason"].strip(), "an audit step carries its reason"


def test_the_seed_step_is_added_after_the_audited_steps_and_the_input_is_not_changed():
    nodes = {"p": [{"node_type": "filter_row", "params": {}, "reason": "r"}]}
    before = copy.deepcopy(nodes)
    plan = export_plot_seeds({"p": {"layers": jitter_layers()}, "q": {"layers": jitter_layers()}}, {"p": 5, "q": 6}, default=DEFAULT)
    listed = with_seed_steps(nodes, plan)
    assert [n["node_type"] for n in listed["p"]] == ["filter_row", "random_seed"]
    assert [n["node_type"] for n in listed["q"]] == ["random_seed"]
    assert nodes == before
    assert with_seed_steps({}, export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=DEFAULT)) == {}


def test_the_methods_text_names_the_pinned_seed():
    from app.handlers.export_handlers import _build_methods_section
    plan = export_plot_seeds({"p": {"layers": jitter_layers()}}, {"p": 777}, default=DEFAULT)
    lines = _build_methods_section(all_plots=[("p", {"ui_label": "My plot"})], t3_by_plot=with_seed_steps({}, plan),
                                   ds_to_plots={}, tiers_exported=["T1"])
    text = "\n".join(lines)
    assert "777" in text and "My plot" in text and "random" in text.lower()
    assert _build_methods_section(all_plots=[("p", {})], t3_by_plot={}, ds_to_plots={}, tiers_exported=["T1"]) == []


# ---------------------------------------------------------------------------
# PROVISIONAL (S3): the recipe default, in the export, the record and the re-run
# ---------------------------------------------------------------------------

def test_the_export_uses_the_recipe_default_records_it_and_does_not_add_it_to_the_recipe(df):
    layers = [jl(random_state=11), jl()]
    plots = {"p": {"layers": layers}}
    plan = export_plot_seeds(plots, {}, default=DEFAULT, recipe_default=7)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(11, "recipe"), (7, "recipe default")]
    assert seeds_per_plot_record(plan) == {"p": [11, 7]} and seed_sources_per_plot(plan) == {"p": "mixed"}
    assert seeds_added_to_recipe(plan, plots) == [], "plot_defaults is in the recipe already"
    assert seed_recipe_note(plan, plots) == []
    shown = positions(df, layers, plot_defaults={"random_state": 7}, **render_seed_args(plan["p"], None))
    assert np.array_equal(shown, positions(df, render_layers(layers, [11, 7])))


def test_the_rerun_of_a_recipe_with_a_recipe_default_draws_the_exported_picture(df):
    layers = jitter_layers()
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT, recipe_default=7)
    recipe = recipe_with(layers)
    recipe["plot_defaults"] = {"random_state": 7}
    baked = bake_plot_seeds(recipe, plan)
    assert baked["plot_defaults"] == {"random_state": 7}
    assert baked["analysis_groups"]["grp"]["plots"]["p"]["layers"] == layers, "the layers stay as written"
    assert np.array_equal(positions(df, baked["analysis_groups"]["grp"]["plots"]["p"]["layers"], plot_defaults=baked["plot_defaults"]),
                          positions(df, layers, plot_defaults={"random_state": 7}, **render_seed_args(plan["p"], None)))


def test_an_audit_pin_beats_the_recipe_default_in_the_export():
    plan = export_plot_seeds({"p": {"layers": jitter_layers()}}, {"p": 777}, default=DEFAULT, recipe_default=7)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(777, "audit")]


# ---------------------------------------------------------------------------
# what HOME shows and offers (review of SEED-HOLDS-1): the seed in use, with where it comes from, and Reshuffle
# under the SAME precedence as the resolver: audit pin > the layer's number > plot_defaults.random_state > 0
# ---------------------------------------------------------------------------

def in_use(layers, plot_defaults=None, pin=None):
    state = {"t3_plot_overrides": {"subtab_p": {"random_state": pin}}} if pin is not None else {}
    return seed_in_use(layers, plot_defaults, state, "p", default=DEFAULT)


@pytest.mark.parametrize("what, layers, plot_defaults, pin, offered", [
    ("nothing written", jitter_layers(), None, None, True),
    ("nothing written, other plot_defaults keys", jitter_layers(), {"theme": "theme_bw"}, None, True),
    ("a number on the layer", jitter_layers(random_state=5), None, None, False),
    ("a number 0 on the layer", jitter_layers(random_state=0), None, None, False),
    ("plot_defaults.random_state", jitter_layers(), {"random_state": 7}, None, False),
    ("plot_defaults.random_state 0", jitter_layers(), {"random_state": 0}, None, False),
    ("a pin", jitter_layers(), None, 9, False),
    ("a pin over a number", jitter_layers(random_state=5), None, 9, False),
    ("mixed: one layer with a number, one without", [jl(random_state=11), jl()], None, None, False),
    ("no random layer", [{"name": "geom_bar"}], None, None, False),
    ("stat sina", [{"name": "geom_point", "params": {"stat": "sina"}}], None, None, True),
])
def test_reshuffle_is_offered_only_where_no_seed_is_written_anywhere(what, layers, plot_defaults, pin, offered):
    assert reshuffle_offered(in_use(layers, plot_defaults, pin)) is offered, what


def test_a_click_would_be_a_pin_that_hides_the_control_again():
    layers = jitter_layers()
    assert reshuffle_offered(in_use(layers)) is True
    assert reshuffle_offered(in_use(layers, pin=123)) is False


@pytest.mark.parametrize("layers, plot_defaults, pin, text", [
    (jitter_layers(), None, None, "seed 0, default (nothing written in the recipe)"),
    (jitter_layers(random_state=42), None, None, "seed 42, written in the recipe"),
    (jitter_layers(random_state=0), None, None, "seed 0, written in the recipe"),
    (jitter_layers(), {"random_state": 5}, None, "seed 5, recipe default (plot_defaults)"),
    (jitter_layers(), None, 7, "seed 7, pinned in the audit"),
    (jitter_layers(random_state=42), {"random_state": 5}, 7, "seed 7, pinned in the audit"),
    ([jl(random_state=11), jl()], None, None, "seeds 11 (written in the recipe), 0 (default)"),
    ([jl(random_state=11), jl()], {"random_state": 5}, None, "seeds 11 (written in the recipe), 5 (recipe default)"),
    ([jl(random_state=3), {"name": "geom_bar"}, jl(random_state=3)], None, None, "seed 3, written in the recipe"),
])
def test_the_seed_line_says_the_seed_and_where_it_comes_from(layers, plot_defaults, pin, text):
    assert seed_caption(in_use(layers, plot_defaults, pin)) == text


def test_no_seed_line_for_a_plot_without_a_random_layer():
    assert seed_caption(in_use([{"name": "geom_bar"}])) is None


def test_a_pin_applies_to_every_random_layer_and_the_text_says_so():
    """Kept as built (reviewer measured it): a pin replaces the seed of ALL the plot's random layers, also one the
    recipe wrote a number on. The Reshuffle button is therefore only offered where no layer has a written seed."""
    seeds = in_use([jl(random_state=11), jl()], pin=9)
    assert [(ls.seed, ls.source) for ls in seeds] == [(9, "audit"), (9, "audit")]
    from app.modules.plot_seeds import RESHUFFLE_TITLE
    assert "every random layer" in RESHUFFLE_TITLE and "Remove the pinned seed" in RESHUFFLE_TITLE


# ---------------------------------------------------------------------------
# the default seed is the literal 0 (a mutation to 1 once survived every headless test)
# ---------------------------------------------------------------------------

def test_the_default_seed_is_the_number_zero_in_the_factory_and_in_the_export(df):
    assert DEFAULT_RANDOM_STATE == 0 and VizFactory().default_random_state == 0
    plan = export_plot_seeds({"p": {"layers": jitter_layers()}}, {}, default=VizFactory().default_random_state)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(0, "default")]
    assert np.array_equal(positions(df, jitter_layers()), positions(df, jitter_layers(random_state=0)))
    assert not np.array_equal(positions(df, jitter_layers()), positions(df, jitter_layers(random_state=1)))


# ---------------------------------------------------------------------------
# the seed 0 is a seed on every path: a pin of 0, a number 0 on a layer, plot_defaults.random_state 0
# (0 is falsy: `if pin:` instead of `if pin is not None:` once passed every test)
# ---------------------------------------------------------------------------

def test_a_pin_of_zero_beats_a_written_seed_in_every_place(df):
    layers = jitter_layers(random_state=5)
    state = {"t3_plot_overrides": {"subtab_p": {"random_state": 0}}}
    assert audit_pin_of(state, "p") == 0 and seed_pins_from_home_state(state, ["p"]) == {"p": 0}
    seeds = in_use(layers, pin=0)
    assert [(ls.seed, ls.source) for ls in seeds] == [(0, "audit")]
    assert seed_caption(seeds) == "seed 0, pinned in the audit" and reshuffle_offered(seeds) is False
    plan = export_seed_plan({"p": {"layers": layers}}, state, default=DEFAULT)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(0, "audit")]
    assert seeds_per_plot_record(plan) == {"p": 0} and seed_sources_per_plot(plan) == {"p": "audit"}
    (step,) = seed_pin_steps(plan)["p"]
    assert step["params"]["seed"] == 0
    assert render_seed_args(plan["p"], None) == {"aesthetic_override": {"random_state": 0}}
    pinned = positions(df, layers, aesthetic_override={"random_state": 0})                      # HOME
    assert np.array_equal(pinned, positions(df, render_layers(layers, [0])))
    assert not np.array_equal(pinned, positions(df, layers))                                    # the recipe's 5 does not win
    assert np.array_equal(positions(df, layers, **render_seed_args(plan["p"], None)), pinned)   # bundle
    baked = baked_layers(layers, plan)                                                          # re-run
    assert [l["params"]["random_state"] for l in baked] == [0]
    assert np.array_equal(positions(df, baked), pinned)


def test_a_written_seed_of_zero_holds_over_the_default_and_the_recipe_default_in_every_place(df):
    layers = jitter_layers(random_state=0)
    seeds = in_use(layers, plot_defaults={"random_state": 7})
    assert [(ls.seed, ls.source) for ls in seeds] == [(0, "recipe")]
    assert seed_caption(seeds) == "seed 0, written in the recipe" and reshuffle_offered(seeds) is False
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT, recipe_default=7)
    assert seeds_per_plot_record(plan) == {"p": 0} and seed_sources_per_plot(plan) == {"p": "recipe"}
    assert seeds_added_to_recipe(plan, {"p": {"layers": layers}}) == []
    assert np.array_equal(positions(df, layers, plot_defaults={"random_state": 7}), positions(df, render_layers(layers, [0])))
    assert not np.array_equal(positions(df, layers, plot_defaults={"random_state": 7}), positions(df, render_layers(layers, [7])))
    assert [l["params"]["random_state"] for l in baked_layers(layers, plan)] == [0]


def test_a_recipe_default_of_zero_is_a_seed_in_every_place(df):
    """plot_defaults.random_state: 0 differs from "nothing written" only in the source and in a factory built with another
    default (so the test uses a factory seed that is not 0)."""
    layers = jitter_layers()
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=9, recipe_default=0)
    assert [(ls.seed, ls.source) for ls in plan["p"]] == [(0, "recipe default")]
    assert seeds_per_plot_record(plan) == {"p": 0} and seed_sources_per_plot(plan) == {"p": "recipe default"}
    assert seed_caption(seed_in_use(layers, {"random_state": 0}, None, "p", default=9)) == "seed 0, recipe default (plot_defaults)"
    assert reshuffle_offered(seed_in_use(layers, {"random_state": 0}, None, "p", default=9)) is False
    assert seeds_added_to_recipe(plan, {"p": {"layers": layers}}) == []
    recipe = recipe_with(layers)
    recipe["plot_defaults"] = {"random_state": 0}
    assert bake_plot_seeds(recipe, plan)["plot_defaults"] == {"random_state": 0}
    # a factory whose own seed is 9: only the recipe default 0 gives the 0 picture
    spec = {"mapping": {"x": "g", "y": "v"}, "layers": layers}

    def shown(plot_defaults):
        plot = VizFactory(random_state=9).render(df, {"plots": {"p": spec}, "plot_defaults": plot_defaults}, "p")
        return np.vstack([np.asarray(c.get_offsets()) for c in plot.draw().axes[0].collections])

    assert np.array_equal(shown({"random_state": 0}), positions(df, render_layers(layers, [0])))
    assert not np.array_equal(shown({}), positions(df, render_layers(layers, [0])))


# --- the bootstrapped summary layer is seeded and recorded like jitter (D-0278 point 1, D-0279 point 1) ---------------

@pytest.mark.parametrize("layer", [
    {"name": "stat_summary"},                                          # plotnine's default function is the bootstrap
    {"name": "stat_summary", "params": {"fun_data": "mean_cl_boot"}},
    {"name": "geom_pointrange", "params": {"stat": "summary"}},
])
def test_a_bootstrapped_summary_layer_is_recorded_with_its_seed_and_baked_into_the_rerun_recipe(layer):
    layers = [copy.deepcopy(layer)]
    plan = export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)
    record = seeds_per_layer_record(plan)
    assert record["p"][0]["seed"] == DEFAULT and record["p"][0]["source"] == "default"
    baked = bake_plot_seeds(recipe_with(layers), plan)
    spec = next(iter(next(iter(baked["analysis_groups"].values()))["plots"].values()))["spec"]
    assert spec["layers"][0]["params"]["random_state"] == DEFAULT


def test_a_non_random_summary_layer_has_no_seed_in_the_record():
    layers = [{"name": "stat_summary", "params": {"fun_data": "mean_se"}}]
    assert seeds_per_layer_record(export_plot_seeds({"p": {"layers": layers}}, {}, default=DEFAULT)) == {}
