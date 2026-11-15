"""Every registered plot component is built twice and compared: which are random, and are they all seeded?
(SEED-HOLDS-1, ADR-104 point 3 and ADR-090 point 2.)

Why: `geom_sina` was random and not seeded (two renders of one recipe differed, `random_state: 0` repeated); only
jitter had been looked at. So no component is assumed deterministic: each is built with the yaml_example of its
schema, with the seed 0 twice (they must give the same plot) and with the seed 1 (a random one must give another).
Then the combinations: every plotnine statistic and position with a geom, in BOTH spellings plotnine accepts for a text
(`jitter` and `position_jitter`, `sina` and `stat_sina`), and every geom with each random statistic and position.
The rule `utils.random_layers.is_random_layer` must equal what building finds.

What is compared: the data every layer holds after plotnine has computed its statistics and positions (`plot._build()`),
which is where every random number is drawn (a hash of the layer tables). No picture is made, so no figure is opened;
a theme is the one component that changes the picture only, so a theme is still drawn and its picture hashed.
All cases run once, in a pool of processes, in one module-scoped fixture (time: see the report of the task).

What cannot be built on a generic table (a facet needs its own column, a guide its own legend ...) is found by trying,
and is checked by reading the module of the plotnine object it wraps: no random number is used there. No list of such
components is kept by hand, so it cannot go stale.

Run: PYTHONPATH=. ./.venv/bin/python -m pytest libs/viz_factory/tests/test_every_component_randomness.py -q
"""
import contextlib
import hashlib
import importlib
import inspect
import io
import multiprocessing
import os
import random
import warnings
from concurrent.futures import ProcessPoolExecutor

import matplotlib
import pandas as pd
import plotnine.positions as _plotnine_positions
import plotnine.stats as _plotnine_stats
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
NUMERIC_X = ({"x": "v", "y": "w"},)
BOOT = {"fun_data": "mean_cl_boot"}
STATS = sorted(n[len("stat_"):] for n in dir(_plotnine_stats) if n.startswith("stat_") and n != "stat_")
POSITIONS = sorted(n[len("position_"):] for n in dir(_plotnine_positions) if n.startswith("position_"))
# the bootstrap randomises the interval (ymin, ymax), which geom_point does not draw: use geom_pointrange
CARRIER = {"summary": "geom_pointrange", "summary_bin": "geom_pointrange"}
# The parameters a statistic needs to be built. A binned summary is random only when the bootstrap is named (plotnine's
# default function for it is not the bootstrap), so it is built both ways.
EXTRA_PARAMS = {"summary_bin": {"bins": 20}}         # few points per bin, so that the bootstrap interval differs
# (kind, name, label, extra parameters), each in both spellings plotnine accepts for a text
SCAN_CASES = (
    [("stat", name, name, EXTRA_PARAMS.get(name, {})) for name in STATS]
    + [("stat", "summary_bin", "summary_bin with the bootstrap named", {"bins": 20, **BOOT})]
    + [("position", name, name, {}) for name in POSITIONS]
)
SPELLINGS = ("short", "prefixed")
RANDOM_PARAMETER_CASES = (
    {"stat": "sina"}, {"stat": "summary"}, {"stat": "summary_bin", "bins": 20, **BOOT},
    {"position": "jitter"}, {"position": "jitterdodge"},
)


def spelled(params: dict, spelling: str) -> dict:
    """The same parameters with `stat` / `position` written with its prefix (`stat_sina`, `position_jitter`)."""
    if spelling == "short":
        return dict(params)
    return {k: (f"{k}_{v}" if k in ("stat", "position") and not str(v).startswith(f"{k}_") else v) for k, v in params.items()}


# -- the work of one case, in a worker process ------------------------------------------------------------------------

_DF = None


def _table():
    global _DF
    if _DF is None:
        rng = random.Random(3)
        _DF = pl.DataFrame({"g": [rng.choice("abc") for _ in range(60)], "h": [rng.choice("xy") for _ in range(60)],
                            "v": [rng.random() * 10 for _ in range(60)], "w": [rng.random() * 5 for _ in range(60)]})
    return _DF


def _plot_hash(layers, mapping, random_state, draw_picture: bool) -> str:
    """A hash of what plotnine computes for the plot: the table of every layer after its statistic and position (all random
    numbers are drawn there). A theme changes the picture only, so for a theme the figure is drawn and its pixels hashed."""
    spec = {"mapping": mapping, "layers": layers}
    with contextlib.redirect_stdout(io.StringIO()), warnings.catch_warnings():
        warnings.simplefilter("ignore")
        plot = VizFactory(random_state=random_state).render(_table(), {"plots": {"p": spec}, "plot_defaults": {}}, "p")
        if draw_picture:
            import matplotlib.pyplot as plt
            fig = plot.draw()
            buf = io.BytesIO()
            fig.savefig(buf, format="png", dpi=20)
            plt.close(fig)
            return hashlib.sha256(buf.getvalue()).hexdigest()
        plot._build()
    digest = hashlib.sha256()
    for layer in plot.layers:
        digest.update(pd.util.hash_pandas_object(layer.data, index=True).values.tobytes())
        digest.update(",".join(map(str, layer.data.columns)).encode())
    return digest.hexdigest()


def _work(task):
    """(key, layers, mappings, seeds, draw_picture) -> (key, hashes for the seeds with the first mapping that works | None)."""
    key, layers, mappings, seeds, draw_picture = task
    for mapping in mappings:
        try:
            first = _plot_hash(layers, mapping, seeds[0], draw_picture)
        except Exception:
            continue
        return key, (first,) + tuple(_plot_hash(layers, mapping, seed, draw_picture) for seed in seeds[1:])
    return key, None


def layers_of(name):
    example = COMPONENT_SCHEMAS[name].get("yaml_example")
    layers = yaml.safe_load(example)["layers"] if example else [{"name": name}]
    if not any(layer["name"].startswith(("geom_", "stat_")) for layer in layers):
        layers = [{"name": "geom_point"}] + layers
    for layer in layers:  # the example may write a seed (the recipe form): the scan is about what the factory does without one
        (layer.get("params") or {}).pop("random_state", None)
    return layers


def geom_components():
    return sorted(n for n in PLOT_COMPONENTS if n.startswith("geom_") and n not in ALWAYS_RANDOM)


def _tasks():
    """Every case of this file as one task: (key, layers, mappings, seeds, draw_picture). A trio is seeds (0, 0, 1)."""
    trio = (0, 0, 1)
    tasks = []
    for name in sorted(PLOT_COMPONENTS):
        tasks.append((("component", name), layers_of(name), MAPPINGS, trio, name.startswith("theme_")))
    for label, layers in EXPLICIT.items():
        tasks.append((("explicit", label), layers, MAPPINGS, trio, False))
    for kind, name, label, extra in SCAN_CASES:
        carrier = CARRIER.get(name, "geom_point")
        for spelling in SPELLINGS:
            params = spelled({kind: name, **extra}, spelling)
            tasks.append((("parameter", kind, label, spelling, carrier, tuple(sorted(params.items()))),
                          [{"name": carrier, "params": params}], NUMERIC_X if name == "summary_bin" else MAPPINGS, trio, False))
    for geom in geom_components():
        for extra in RANDOM_PARAMETER_CASES:
            for spelling in SPELLINGS:
                params = spelled(extra, spelling)
                tasks.append((("geom", geom, tuple(sorted(params.items()))), [{"name": geom, "params": dict(params)}],
                              MAPPINGS, (0, 0), False))
    return tasks


@pytest.fixture(scope="module")
def results():
    """{key: hashes or None} for every case, built once in a pool of processes. The workers are started clean (a
    forkserver, never a fork of this process: a fork of a process that has run polars and matplotlib threads can hang
    in a long test run); each worker imports this module, which registers the components."""
    workers = max(1, min(8, (os.cpu_count() or 2) - 1))
    with ProcessPoolExecutor(max_workers=workers, mp_context=multiprocessing.get_context("forkserver")) as pool:
        return dict(pool.map(_work, _tasks(), chunksize=4))


def _components(results):
    return {key[1]: trio for key, trio in results.items() if key[0] == "component"}


def test_most_components_are_built_and_every_other_one_uses_no_random_number(results):
    """What cannot be built on the generic table holds no random number in its plotnine module (read, not built)."""
    scan = _components(results)
    undrawn = sorted(label for label, trio in scan.items() if trio is None)
    assert len(scan) - len(undrawn) >= 150, f"too few components could be built: undrawn {undrawn}"
    for name in undrawn:
        wraps = COMPONENT_SCHEMAS.get(name, {}).get("wraps") or []
        if not wraps:
            assert name.startswith(LAYOUT_ONLY), f"{name} cannot be built and wraps no plotnine object: check it by hand"
            continue
        wrapped = importlib.import_module(wraps[0]["lib"])
        for attr in wraps[0]["attr_path"]:
            wrapped = getattr(wrapped, attr)
        assert "random" not in inspect.getsource(importlib.import_module(wrapped.__module__)).lower(), \
            f"{name} cannot be built here and its plotnine module uses random numbers"


def test_the_components_found_random_are_exactly_the_ones_the_factory_seeds(results):
    """A seeded random component gives another plot with another seed; one that does not use the seed does not (and is
    not random, or it fails the next test)."""
    found = {name for name, trio in _components(results).items() if trio is not None and trio[0] != trio[2]}
    found |= {key[1] for key, trio in results.items() if key[0] == "explicit" and trio is not None and trio[0] != trio[2]}
    assert found == set(ALWAYS_RANDOM) | EXPLICIT_RANDOM


def test_no_component_is_random_once_the_factory_seeds_it(results):
    random_with_a_seed = sorted(str(key) for key, trio in results.items()
                                if key[0] in ("component", "explicit") and trio is not None and trio[0] != trio[1])
    assert not random_with_a_seed, f"built twice with one seed they differ: {random_with_a_seed}"


def test_a_non_random_case_is_not_flagged(results):
    explicit = {key[1]: trio for key, trio in results.items() if key[0] == "explicit"}
    for label in ("stat_summary / mean_se", "stat_summary_bin / mean_se"):
        assert explicit[label][0] == explicit[label][1] == explicit[label][2], f"{label} is not random"
    for name in ("geom_point", "geom_bar"):
        trio = _components(results)[name]
        assert trio[0] == trio[1] == trio[2], f"{name} is not random"


# ---------------------------------------------------------------------------
# the combinations: a statistic or a position named as a PARAMETER of any layer, in both spellings of plotnine
# ---------------------------------------------------------------------------
# `geom_point` with `stat: sina` is random although `geom_point` is not random by name; `position: position_jitter` is
# `position: jitter` for plotnine. plotnine's own list of statistics and positions is built with a geom, each in both
# spellings, and every geom with every random statistic and position; the rule must equal what building finds.

def _parameters(results):
    return {key: trio for key, trio in results.items() if key[0] == "parameter"}


def test_every_plotnine_statistic_and_position_is_found_random_or_not_and_the_rule_agrees_in_both_spellings(results):
    cases = _parameters(results)
    drawn = {key: trio for key, trio in cases.items() if trio is not None}
    assert len(drawn) >= 50, f"too few combinations could be built: {sorted(set(cases) - set(drawn))}"
    found = set()
    for (_, kind, label, spelling, carrier, params), trio in drawn.items():
        is_random = trio[0] != trio[1] or trio[0] != trio[2]     # not repeatable, or sensitive to the seed
        assert is_random_layer(carrier, dict(params)) == is_random, \
            f"{carrier} with {dict(params)}: building says random={is_random}"
        if trio[0] != trio[2]:
            found.add((kind, label, spelling))
    expected = {("stat", "sina"), ("stat", "summary"), ("stat", "summary_bin with the bootstrap named"),
                ("position", "jitter"), ("position", "jitterdodge")}
    assert {(k, label) for k, label, _ in found} == expected
    assert {s for _, _, s in found} == set(SPELLINGS) and len(found) == 2 * len(expected), \
        "every random statistic and position must be found random in both spellings"


def test_a_statistic_or_position_that_cannot_be_built_with_a_geom_holds_no_random_number(results):
    for (_, kind, label, _spelling, _carrier, _params), trio in _parameters(results).items():
        if trio is None:
            name = label.split(" ")[0]
            module = getattr(_plotnine_stats if kind == "stat" else _plotnine_positions, f"{kind}_{name}")
            assert "random" not in inspect.getsource(importlib.import_module(module.__module__)).lower(), \
                f"{kind} {name} cannot be built here and uses random numbers"


def test_every_geom_with_every_random_statistic_and_position_is_seeded_in_both_spellings(results):
    cases = {key: pair for key, pair in results.items() if key[0] == "geom"}
    drawn = {key: pair for key, pair in cases.items() if pair is not None}
    assert len(drawn) >= 200, f"too few geom combinations could be built ({len(drawn)} of {len(cases)})"
    not_repeatable = sorted(f"{geom} {dict(params)}" for (_, geom, params), pair in drawn.items() if pair[0] != pair[1])
    assert not not_repeatable, f"built twice with seed 0 they differ: {not_repeatable}"
    for (_, geom, params) in drawn:
        assert is_random_layer(geom, dict(params)), f"{geom} {dict(params)} is random and the rule does not say so"
