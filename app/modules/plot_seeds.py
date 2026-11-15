"""app/modules/plot_seeds.py
The seed of a plot's jitter, outside the Shiny handlers (Two-Category Law, ADR-045).

SEED-HOLDS-1 (ADR-104 point 3): a seed written in the recipe holds; a seed pinned by an audit step is the
same in the HOME plot, the results bundle, the reproducibility export and its re-run; HOME never replaces a
recipe's seed by the one it drew. The order of precedence itself is one function in the cascade resolver
(`viz_factory.plot_config_resolver.resolve_layer_seeds`, one seed per random LAYER: a layer's number never
flows to another layer); this module only gathers its inputs for HOME and for the export, and shapes what
each hands to the render and to the record. Every seed line of the handlers is a call to a function here.

Not decided here (ADR-104, awaiting Eve): which seed a layer uses when its recipe writes none. Today HOME
draws one per session and plot and the export reuses that number (library default when HOME never showed
the plot); a layer that writes a number keeps it, in every place.
"""
from __future__ import annotations

# @deps
# provides: class:SessionSeedDraws, function:home_layer_seeds, function:home_plot_seeds, function:reference_render_args,
#           function:render_seed_args, function:remember_drawn_seed, function:export_plot_seeds,
#           function:export_seed_plan, function:seeds_per_plot_record, function:seed_sources_per_plot,
#           function:seeds_per_layer_record, function:seeds_added_to_recipe, function:seed_recipe_note,
#           function:unfixed_seed_warning, function:bake_plot_seeds, function:audit_pin_of, function:seed_pins_from_home_state
# consumes: libs/viz_factory/src/viz_factory/plot_config_resolver.py (resolve_layer_seeds, LayerSeed)
# consumed_by: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/tests/test_plot_seeds.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104, .claude/rules/rules_viz_factory.md#8
# @end_deps

import copy
import secrets
from typing import Callable

from viz_factory.plot_config_resolver import (
    LayerSeed,
    layers_need_offered_seed,
    recipe_asks_random,
    resolve_layer_seeds,
)


def _draw_seed() -> int:
    return secrets.randbits(31)


Seeds = tuple  # tuple[LayerSeed, ...]: one entry per random layer of a plot; empty when it has none


class SessionSeedDraws:
    """The seed HOME draws for a plot whose recipe writes none: one per plot, stable for the whole session.

    A plain dictionary, not reactive state: drawing here never writes a reactive value, so a Calc may call it
    (ui_implementation_contract.md section 14, R1). Stable on purpose: before, the draw was remade whenever
    `home_state` changed, so the picture could change on a tab switch.
    """

    def __init__(self, draw: Callable[[], int] = _draw_seed):
        self._draw = draw
        self._seeds: dict[str, int] = {}

    def get(self, plot_id: str) -> int:
        if plot_id not in self._seeds:
            self._seeds[plot_id] = self._draw()
        return self._seeds[plot_id]

    def has(self, plot_id: str) -> bool:
        return plot_id in self._seeds


def audit_pin_of(home_state: dict | None, plot_id: str):
    """The seed pinned for a plot in HOME's per-plot overrides (Reshuffle, or an audit override), or None.

    Read whether or not the audit trail (`t3_sandbox_enabled`) is on: the Reshuffle button is not gated by it,
    so HOME and the export both read the pin here, with no flag.
    """
    overrides = (home_state or {}).get("t3_plot_overrides", {}) or {}
    return (overrides.get(f"subtab_{plot_id}") or {}).get("random_state")


def seed_pins_from_home_state(home_state: dict | None, plot_ids) -> dict[str, object]:
    """{plot_id: seed} for the plots that have a pin (see audit_pin_of)."""
    pins = {}
    for plot_id in plot_ids:
        pin = audit_pin_of(home_state, plot_id)
        if pin is not None:
            pins[plot_id] = pin
    return pins


def home_layer_seeds(layers: list[dict], audit_pin, draws: SessionSeedDraws, plot_id: str, *, default) -> Seeds:
    """The seed of every random layer HOME shows. Draws only when a layer takes one: no audit pin and a
    random layer whose recipe writes no number."""
    offered = draws.get(plot_id) if layers_need_offered_seed(layers, audit_pin) else None
    return resolve_layer_seeds(layers, audit_pin, offered, default=default)


def home_plot_seeds(layers: list[dict], home_state: dict | None, draws: SessionSeedDraws, plot_id: str, *,
                    default) -> Seeds:
    """What the HOME plot handler uses: the pin comes from home_state, with no flag in between."""
    return home_layer_seeds(layers, audit_pin_of(home_state, plot_id), draws, plot_id, default=default)


def reference_render_args(layers: list[dict], draws: SessionSeedDraws, plot_id: str, *, default) -> dict:
    """The seed arguments of the comparison reference pane (T2, left): the same arrangement as My view
    (recipe numbers, this session's draw), so the two panes differ only by what the user changed. An audit
    pin is one of those changes and is not applied here."""
    return render_seed_args(home_layer_seeds(layers, None, draws, plot_id, default=default), None)


def offered_seed_of(seeds: Seeds):
    """The one seed the caller offered (HOME's draw) when some layer took it, else None."""
    return next((ls.seed for ls in seeds if ls.source == "drawn"), None)


def remember_drawn_seed(current: dict, plot_id: str, seeds: Seeds) -> dict | None:
    """The new {plot_id: seed} bookkeeping for the export, or None when nothing changes.

    Written once per plot and session: calling it again with its own result gives None, so the Effect that
    stores it settles (a value that changed on every call made an endless loop).
    """
    offered = offered_seed_of(seeds)
    if offered is None or current.get(plot_id) == offered:
        return None
    return {**current, plot_id: offered}


def render_seed_args(seeds: Seeds, t3_overrides: dict | None) -> dict:
    """The keyword arguments of `VizFactory.render` that carry the seeds (HOME and the export both use this).

    An audit pin goes into the L5 override (it beats the recipe on every random layer). The seed of the layers
    whose recipe writes no number goes in as the fallback, which fills only those layers: a layer that writes
    a number keeps its own, and never gives it to another layer.
    """
    override = dict(t3_overrides) if t3_overrides else None
    audit = next((ls.seed for ls in seeds if ls.source == "audit"), None)
    if audit is not None:
        override = {**(override or {}), "random_state": audit}
    fallback = next((ls.seed for ls in seeds if ls.source in ("drawn", "default")), None)
    return {"aesthetic_override": override, "fallback_random_state": fallback}


def export_plot_seeds(
    plots: dict[str, dict],
    audit_pins: dict[str, object],
    home_drawn: dict[str, int],
    *,
    default,
    draw: Callable[[], int] = _draw_seed,
) -> dict[str, Seeds]:
    """The seed of every random layer of every exported plot, and so what is rendered and recorded.

    Per layer: audit pin > the layer's own number > the seed HOME drew for this plot (`home_drawn`) > for a
    layer that asks `random_state: null` a seed drawn now (recorded: "random on purpose" is still
    reproducible) > the library default. `plots` is {plot_id: spec}; a plot HOME never showed has no entry
    in `home_drawn`.
    """
    seeds: dict[str, Seeds] = {}
    for plot_id, spec in plots.items():
        layers = (spec or {}).get("layers", [])
        pin = audit_pins.get(plot_id)
        offered = home_drawn.get(plot_id)
        if offered is None and pin is None and recipe_asks_random(layers):
            offered = draw()
        seeds[plot_id] = resolve_layer_seeds(layers, pin, offered, default=default)
    return seeds


def export_seed_plan(plots: dict[str, dict], home_state: dict | None, home_drawn: dict[str, int], *,
                     default, draw: Callable[[], int] = _draw_seed) -> dict[str, Seeds]:
    """What the export handler calls: the pins come from home_state with no flag in between (like HOME)."""
    return export_plot_seeds(plots, seed_pins_from_home_state(home_state, list(plots)), home_drawn,
                             default=default, draw=draw)


def _plot_seeds_flat(seeds: Seeds) -> list:
    return [ls.seed for ls in seeds]


def seeds_per_plot_record(seeds: dict[str, Seeds]) -> dict[str, object]:
    """`seeds_per_plot` of effective_run.yaml: one number per exported random plot when all its random layers
    share it (the shape the file always had), else the list of numbers in layer order; the detail is
    `seeds_per_layer`."""
    out = {}
    for pid, layer_seeds in seeds.items():
        if not layer_seeds:
            continue
        flat = _plot_seeds_flat(layer_seeds)
        out[pid] = flat[0] if len(set(flat)) == 1 else flat
    return out


def seed_sources_per_plot(seeds: dict[str, Seeds]) -> dict[str, str]:
    """`seed_source_per_plot`: the one source word of a plot, or "mixed" when its layers differ."""
    out = {}
    for pid, layer_seeds in seeds.items():
        if not layer_seeds:
            continue
        words = {ls.source for ls in layer_seeds}
        out[pid] = words.pop() if len(words) == 1 else "mixed"
    return out


def seeds_per_layer_record(seeds: dict[str, Seeds]) -> dict[str, list[dict]]:
    """`seeds_per_layer`: for every random layer, its position, name, seed and where the seed comes from."""
    return {
        pid: [{"layer_index": ls.index, "layer": ls.layer, "seed": ls.seed, "source": ls.source} for ls in layer_seeds]
        for pid, layer_seeds in seeds.items() if layer_seeds
    }


def _written_in_recipe(plots: dict[str, dict], plot_id: str, index: int):
    layers = ((plots.get(plot_id) or {}).get("layers")) or []
    return (layers[index].get("params") or {}).get("random_state") if index < len(layers) else None


def seeds_added_to_recipe(seeds: dict[str, Seeds], plots: dict[str, dict]) -> list[dict]:
    """The seeds the export wrote into the reproducibility recipe: every layer whose seed does not come from
    a number the recipe already writes, with what the recipe wrote there (null when nothing)."""
    return [
        {"plot": pid, "layer_index": ls.index, "layer": ls.layer, "seed": ls.seed, "source": ls.source,
         "recipe_wrote": _written_in_recipe(plots, pid, ls.index)}
        for pid, layer_seeds in seeds.items() for ls in layer_seeds if ls.source != "recipe"
    ]


def seed_recipe_note(seeds: dict[str, Seeds], plots: dict[str, dict]) -> list[str]:
    """Plain lines, for the README and the report, naming the seeds the export added to the reproducibility
    recipe (a YAML comment would be lost by the dump). Empty when it added none."""
    added = seeds_added_to_recipe(seeds, plots)
    if not added:
        return []
    lines = [
        "Random scatter (jitter) seeds the export wrote into the reproducibility recipe, so that the re-run",
        "draws the exported picture. The recipe you started from did not hold these numbers",
        "(also in effective_run.yaml: seeds_added_to_recipe, seeds_per_layer):",
    ]
    for a in added:
        was = "no number" if a["recipe_wrote"] in (None, "random") else f"recipe wrote {a['recipe_wrote']}"
        lines.append(f"  plot {a['plot']}, layer {a['layer_index']} ({a['layer']}): random_state {a['seed']} "
                     f"[{a['source']}; {was}]")
    return lines


def unfixed_seed_warning(seeds: dict[str, Seeds]) -> str | None:
    """The export's warning, only for plots with a random layer whose seed is neither written in the recipe
    nor pinned by an audit step (drawn or default); in plain words, with what to write in the recipe."""
    unfixed = [pid for pid, layer_seeds in seeds.items() if any(ls.source in ("drawn", "default") for ls in layer_seeds)]
    if not unfixed:
        return None
    shown = ", ".join(unfixed[:5]) + (f" and {len(unfixed) - 5} more" if len(unfixed) > 5 else "")
    return (
        f"The seed of the random scatter is not fixed in the recipe for {len(unfixed)} plot(s): {shown}. "
        "The export used one seed per plot and recorded it (seeds_per_plot in effective_run.yaml), and the "
        "reproducibility recipe carries it, but opening your own recipe again can show a different arrangement. "
        "To fix the picture, write the number on the jitter layer of each plot in the recipe, "
        "for example `random_state: 123`."
    )


def bake_plot_seeds(recipe_cfg: dict, seeds: dict[str, Seeds]) -> dict:
    """A copy of the recipe in which every random layer carries the seed it was exported with.

    This is how the re-run reproduces the exported picture: the recipe is the scientific document, so the
    seed is written there, not left to a draw. A number the recipe wrote on a layer holds (it is the same
    number); an audit pin replaces it; a layer without a number gets the seed it was drawn with. A plot or
    layer that is not in the recipe, or is not a random layer there, is an error: nothing is skipped
    silently (ADR-104).
    """
    baked = copy.deepcopy(recipe_cfg)
    specs = {
        pid: entry.get("spec")
        for group in (baked.get("analysis_groups") or {}).values()
        for pid, entry in (group.get("plots") or {}).items()
    }
    for plot_id, layer_seeds in seeds.items():
        if not layer_seeds:
            continue
        spec = specs.get(plot_id)
        if spec is None:
            raise KeyError(
                f"Plot '{plot_id}' is not in the recipe, so its seed cannot be written into the "
                "reproducibility recipe."
            )
        layers = spec.get("layers", [])
        for ls in layer_seeds:
            if ls.index >= len(layers) or layers[ls.index].get("name") != ls.layer:
                raise KeyError(
                    f"Plot '{plot_id}': layer {ls.index} ({ls.layer}) is not in the recipe, so its seed "
                    f"{ls.seed} cannot be written into the reproducibility recipe."
                )
            if ls.source != "recipe":
                layers[ls.index]["params"] = {**(layers[ls.index].get("params") or {}), "random_state": ls.seed}
    return baked
