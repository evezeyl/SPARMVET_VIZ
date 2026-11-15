"""Every registered plot component is drawn twice and compared: which are random, and are they all seeded?
(SEED-HOLDS-1, ADR-104 point 3 and ADR-090 point 2.)

Why: `geom_sina` was random and not seeded (two renders of one recipe differed, `random_state: 0` repeated); only
jitter had been looked at. So no component is assumed deterministic: each is drawn with the yaml_example of its
schema, with the seed 0 twice (they must draw the same picture) and with the seed 1 (a random one must draw another).

What cannot be drawn on a generic table (a facet needs its own column, a guide its own legend ...) is found by trying,
and is checked by reading the module of the plotnine object it wraps: no random number is used there. No list of such
components is kept by hand, so it cannot go stale.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_every_component_randomness.py -q
"""
import contextlib
import hashlib
import importlib
import inspect
import io
import random
import warnings

import matplotlib
import polars as pl
import pytest
import yaml

matplotlib.use("Agg")

import viz_factory  # noqa: F401  (importing it registers the components)
from utils.random_layers import ALWAYS_RANDOM, is_random_layer
from viz_factory.registry import COMPONENT_SCHEMAS, PLOT_COMPONENTS
from viz_factory.viz_factory import VizFactory

# Explicit layers for what the example cannot draw
EXPLICIT = {
    "stat_summary / mean_se": [{"name": "stat_summary", "params": {"fun_data": "mean_se"}}],
    "stat_summary / mean_cl_boot": [{"name": "stat_summary", "params": {"fun_data": "mean_cl_boot"}}],
    "stat_summary_bin / mean_se": [{"name": "stat_summary_bin", "params": {"fun_data": "mean_se", "bins": 5}}],
    "stat_summary_bin / mean_cl_boot": [{"name": "stat_summary_bin", "params": {"fun_data": "mean_cl_boot", "bins": 5}}],
    "geom_pointrange with stat summary / mean_cl_boot": [{"name": "geom_pointrange", "params": {"stat": "summary", "fun_data": "mean_cl_boot"}}],
    "geom_point with position jitter": [{"name": "geom_point", "params": {"position": "jitter"}}],
    "geom_point with position jitterdodge": [{"name": "geom_point", "params": {"position": "jitterdodge"}}],
}
EXPLICIT_RANDOM = {name for name in EXPLICIT if "cl_boot" in name or "jitter" in name}
# components that arrange or label a plot and draw no data of their own (some wrap no single plotnine object)
LAYOUT_ONLY = ("facet_", "guide_", "theme_", "coord_", "scale_", "element_", "annotate")
MAPPINGS = (
    {"x": "g", "y": "v"}, {"x": "g", "y": "v", "fill": "h", "color": "h"}, {"x": "v", "y": "w"}, {"x": "v"},
    {"x": "v", "y": "w", "ymin": "v", "ymax": "w", "xmin": "v", "xmax": "w", "xend": "w", "yend": "w",
     "label": "g", "sample": "v", "angle": "v", "radius": "w"},
)


@pytest.fixture(scope="module")
def df():
    rng = random.Random(3)
    return pl.DataFrame({"g": [rng.choice("abc") for _ in range(60)], "h": [rng.choice("xy") for _ in range(60)],
                         "v": [rng.random() * 10 for _ in range(60)], "w": [rng.random() * 5 for _ in range(60)]})


def draw(df, layers, mapping, random_state) -> str:
    spec = {"mapping": mapping, "layers": layers}
    with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plot = VizFactory(random_state=random_state).render(df, {"plots": {"p": spec}, "plot_defaults": {}}, "p")
        buf = io.BytesIO()
        plot.draw().savefig(buf, format="png", dpi=20)
    return hashlib.sha256(buf.getvalue()).hexdigest()


def layers_of(name):
    example = COMPONENT_SCHEMAS[name].get("yaml_example")
    layers = yaml.safe_load(example)["layers"] if example else [{"name": name}]
    if not any(layer["name"].startswith(("geom_", "stat_")) for layer in layers):
        layers = [{"name": "geom_point"}] + layers
    for layer in layers:  # the example may write a seed (the recipe form): the scan is about what the factory does without one
        (layer.get("params") or {}).pop("random_state", None)
    return layers


def draw_three(df, layers, mappings=MAPPINGS):
    """(seed 0, seed 0 again, seed 1) hashes with the first mapping that draws, or None when none does.

    A random component that is seeded draws the same picture twice with one seed and another with the next seed.
    A random component that is NOT seeded breaks the first equality (the defect of geom_sina).
    """
    for mapping in mappings:
        try:
            first = draw(df, layers, mapping, 0)
        except Exception:
            continue
        return first, draw(df, layers, mapping, 0), draw(df, layers, mapping, 1)
    return None


@pytest.fixture(scope="module")
def scan(df):
    """{label: three hashes} for every component and every explicit case."""
    cases = {name: layers_of(name) for name in sorted(PLOT_COMPONENTS)}
    cases.update(EXPLICIT)
    return {label: draw_three(df, layers) for label, layers in cases.items()}


def test_most_components_are_drawn_and_every_other_one_uses_no_random_number(scan):
    """What cannot be drawn on the generic table holds no random number in its plotnine module (read, not drawn)."""
    undrawn = sorted(label for label, trio in scan.items() if trio is None)
    assert len(scan) - len(undrawn) >= 150, f"too few components could be drawn: undrawn {undrawn}"
    for name in undrawn:
        wraps = COMPONENT_SCHEMAS.get(name, {}).get("wraps") or []
        if not wraps:
            assert name.startswith(LAYOUT_ONLY), f"{name} cannot be drawn and wraps no plotnine object: check it by hand"
            continue
        wrapped = importlib.import_module(wraps[0]["lib"])
        for attr in wraps[0]["attr_path"]:
            wrapped = getattr(wrapped, attr)
        assert "random" not in inspect.getsource(importlib.import_module(wrapped.__module__)).lower(), \
            f"{name} cannot be drawn here and its plotnine module uses random numbers"


def test_the_components_found_random_are_exactly_the_ones_the_factory_seeds(scan):
    """A seeded random component draws another picture with another seed; a component that does not use the seed
    does not (and is not random, or it fails the next test)."""
    found = {label for label, trio in scan.items() if trio is not None and trio[0] != trio[2]}
    assert found == set(ALWAYS_RANDOM) | EXPLICIT_RANDOM


def test_no_component_is_random_once_the_factory_seeds_it(scan):
    random_with_a_seed = sorted(label for label, trio in scan.items() if trio is not None and trio[0] != trio[1])
    assert not random_with_a_seed, f"drawn twice with one seed they differ: {random_with_a_seed}"


def test_a_non_random_case_is_not_flagged(scan):
    for label in ("stat_summary / mean_se", "stat_summary_bin / mean_se", "geom_point", "geom_bar"):
        trio = scan[label]
        assert trio[0] == trio[1] == trio[2], f"{label} is not random"


# ---------------------------------------------------------------------------
# the combinations: a statistic or a position named as a PARAMETER of any layer (review of SEED-HOLDS-1)
# ---------------------------------------------------------------------------
# `geom_point` with `stat: sina` draws a different arrangement each time although `geom_point` is not random by name.
# plotnine's own list of statistics and positions is drawn with a geom, and every geom with every random statistic and
# position; the rule `is_random_layer` must equal what drawing finds.

import plotnine.positions as _plotnine_positions  # noqa: E402
import plotnine.stats as _plotnine_stats  # noqa: E402

STATS = sorted(n[len("stat_"):] for n in dir(_plotnine_stats) if n.startswith("stat_") and n != "stat_")
POSITIONS = sorted(n[len("position_"):] for n in dir(_plotnine_positions) if n.startswith("position_"))
NUMERIC_X = ({"x": "v", "y": "w"},)
BOOT = {"fun_data": "mean_cl_boot"}
# the bootstrap randomises the interval (ymin, ymax), which geom_point does not draw: draw it with geom_pointrange
CARRIER = {"summary": "geom_pointrange", "summary_bin": "geom_pointrange"}
# The parameters a statistic needs to be drawn. A binned summary is random only when the bootstrap is named (plotnine's
# default function for it is not the bootstrap), so it is drawn both ways.
EXTRA_PARAMS = {"summary_bin": {"bins": 20}}         # few points per bin, so that the bootstrap interval differs
SCAN_CASES = (
    [("stat", name, name, EXTRA_PARAMS.get(name, {})) for name in STATS]
    + [("stat", "summary_bin", "summary_bin with the bootstrap named", {"bins": 20, **BOOT})]
    + [("position", name, name, {}) for name in POSITIONS]
)
RANDOM_PARAMETER_CASES = (
    {"stat": "sina"}, {"stat": "summary"}, {"stat": "summary_bin", "bins": 20, **BOOT},
    {"position": "jitter"}, {"position": "jitterdodge"},
)


@pytest.fixture(scope="module")
def parameter_scan(df):
    """{(kind, label): (carrier, parameters, three hashes or None)}: every statistic and position drawn with a geom."""
    out = {}
    for kind, name, label, extra in SCAN_CASES:
        carrier = CARRIER.get(name, "geom_point")
        params = {kind: name, **extra}
        # a binned statistic needs a numeric x
        trio = draw_three(df, [{"name": carrier, "params": params}], NUMERIC_X if name == "summary_bin" else MAPPINGS)
        out[(kind, label)] = (carrier, params, trio)
    return out


def test_every_plotnine_statistic_and_position_is_found_random_or_not_by_drawing_and_the_rule_agrees(parameter_scan):
    drawn = {key: case for key, case in parameter_scan.items() if case[2] is not None}
    assert len(drawn) >= 25, f"too few combinations could be drawn: {sorted(set(parameter_scan) - set(drawn))}"
    for (kind, label), (carrier, params, trio) in drawn.items():
        found = trio[0] != trio[1] or trio[0] != trio[2]     # not repeatable, or sensitive to the seed
        assert is_random_layer(carrier, params) == found, f"{carrier} with {kind}: {label}: drawing says random={found}"
    assert {key for key, case in drawn.items() if case[2][0] != case[2][2]} == {
        ("stat", "sina"), ("stat", "summary"), ("stat", "summary_bin with the bootstrap named"),
        ("position", "jitter"), ("position", "jitterdodge")}


def test_a_statistic_or_position_that_cannot_be_drawn_with_a_geom_point_holds_no_random_number(parameter_scan):
    for (kind, label), (_carrier, _params, trio) in parameter_scan.items():
        if trio is None:
            name = label.split(" ")[0]
            module = getattr(_plotnine_stats if kind == "stat" else _plotnine_positions, f"{kind}_{name}")
            assert "random" not in inspect.getsource(importlib.import_module(module.__module__)).lower(), \
                f"{kind} {name} cannot be drawn here and uses random numbers"


def geom_components():
    return sorted(n for n in PLOT_COMPONENTS if n.startswith("geom_") and n not in ALWAYS_RANDOM)


@pytest.fixture(scope="module")
def geom_combinations(df):
    """{(geom, parameters): (first, second) hashes with seed 0, or None when the pair cannot be drawn}."""
    out = {}
    for geom in geom_components():
        for extra in RANDOM_PARAMETER_CASES:
            layers = [{"name": geom, "params": dict(extra)}]
            pair = None
            for mapping in MAPPINGS:
                try:
                    pair = (draw(df, layers, mapping, 0), draw(df, layers, mapping, 0))
                except Exception:
                    continue
                break
            out[(geom, tuple(sorted(extra.items())))] = pair
    return out


def test_every_geom_with_every_random_statistic_and_position_is_seeded(geom_combinations):
    drawn = {key: pair for key, pair in geom_combinations.items() if pair is not None}
    assert len(drawn) >= 100, f"too few geom combinations could be drawn ({len(drawn)} of {len(geom_combinations)})"
    not_repeatable = sorted(f"{geom} {dict(extra)}" for (geom, extra), pair in drawn.items() if pair[0] != pair[1])
    assert not not_repeatable, f"drawn twice with seed 0 they differ: {not_repeatable}"
    for (geom, extra) in drawn:
        assert is_random_layer(geom, dict(extra)), f"{geom} {dict(extra)} is random and the rule does not say so"
