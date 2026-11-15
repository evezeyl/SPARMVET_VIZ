"""app/modules/plot_seeds.py
The seed of a plot's random layers in the export, outside the Shiny handlers (Two-Category Law, ADR-045).

SEED-HOLDS-1 (ADR-104, Eve 2026-11-15): a seed written in the recipe holds; a layer that writes none uses the
factory's seed, 0, in EVERY place (HOME, the comparison reference pane, the gallery, Blueprint, the results bundle,
the reproducibility export and its re-run); HOME draws no seed; an audit pin is the same everywhere. The order of
precedence itself is one function in the cascade resolver (`viz_factory.plot_config_resolver.resolve_layer_seeds`,
one seed per random LAYER: a layer's number never flows to another layer). HOME only passes the audit pin it holds
in `home_state` to the render; this module shapes what the export hands to the render and to the record, and writes
the used seeds into the reproducibility recipe, so that every seed used is written (recipe or audit pin).
"""
from __future__ import annotations

# @deps
# provides: function:audit_pin_of, function:seed_pins_from_home_state, function:render_seed_args,
#           function:export_plot_seeds, function:export_seed_plan, function:seeds_per_plot_record,
#           function:seed_sources_per_plot, function:seeds_per_layer_record, function:seeds_added_to_recipe,
#           function:seed_recipe_note, function:unfixed_seed_warning, function:bake_plot_seeds
# consumes: libs/viz_factory/src/viz_factory/plot_config_resolver.py (resolve_layer_seeds, LayerSeed)
# consumed_by: app/handlers/export_handlers.py, app/tests/test_plot_seeds.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104, .claude/rules/rules_viz_factory.md#8
# @end_deps

import copy
import secrets
from typing import Callable

from viz_factory.plot_config_resolver import recipe_asks_random, resolve_layer_seeds


def _draw_seed() -> int:
    return secrets.randbits(31)


Seeds = tuple  # tuple[LayerSeed, ...]: one entry per random layer of a plot; empty when it has none


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


def render_seed_args(seeds: Seeds, t3_overrides: dict | None) -> dict:
    """The keyword arguments of `VizFactory.render` that carry the seeds of an exported plot.

    An audit pin goes into the L5 override (it beats the recipe on every random layer). The seed drawn for the
    layers that write `random_state: null` goes in as `drawn_random_state`, which fills only those layers: a layer
    that writes a number keeps its own and a layer that writes none keeps the factory's seed.
    """
    override = dict(t3_overrides) if t3_overrides else None
    audit = next((ls.seed for ls in seeds if ls.source == "audit"), None)
    if audit is not None:
        override = {**(override or {}), "random_state": audit}
    drawn = next((ls.seed for ls in seeds if ls.source == "drawn"), None)
    return {"aesthetic_override": override, "drawn_random_state": drawn}


def export_plot_seeds(
    plots: dict[str, dict],
    audit_pins: dict[str, object],
    *,
    default,
    draw: Callable[[], int] = _draw_seed,
) -> dict[str, Seeds]:
    """The seed of every random layer of every exported plot, and so what is rendered and recorded.

    Per layer: audit pin > the layer's own number > the default (`default`: the factory's seed, 0) > for a layer
    that writes `random_state: null` a seed drawn now (recorded: "random on purpose" is still reproducible).
    `plots` is {plot_id: spec}.
    """
    seeds: dict[str, Seeds] = {}
    for plot_id, spec in plots.items():
        layers = (spec or {}).get("layers", [])
        pin = audit_pins.get(plot_id)
        drawn = draw() if pin is None and recipe_asks_random(layers) else None
        seeds[plot_id] = resolve_layer_seeds(layers, pin, drawn, default=default)
    return seeds


def export_seed_plan(plots: dict[str, dict], home_state: dict | None, *, default,
                     draw: Callable[[], int] = _draw_seed) -> dict[str, Seeds]:
    """What the export handler calls: the pins come from home_state with no flag in between (like HOME)."""
    return export_plot_seeds(plots, seed_pins_from_home_state(home_state, list(plots)), default=default, draw=draw)


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
    """The export's warning, only for plots with a layer that writes `random_state: null`: the export drew a seed,
    recorded it and wrote it into the reproducibility recipe, but the user's own recipe still asks for a random
    arrangement. In plain words, with what to write. None when there is nothing to say. (A layer that writes no
    seed uses 0 and is not a warning: the seed is recorded and written, `seeds_added_to_recipe`.)"""
    unfixed = [pid for pid, layer_seeds in seeds.items() if any(ls.source == "drawn" for ls in layer_seeds)]
    if not unfixed:
        return None
    shown = ", ".join(unfixed[:5]) + (f" and {len(unfixed) - 5} more" if len(unfixed) > 5 else "")
    return (
        f"The recipe asks for a random arrangement (random_state: null) in {len(unfixed)} plot(s): {shown}. "
        "The export drew one seed per plot and recorded it (seeds_per_plot in effective_run.yaml), and the "
        "reproducibility recipe carries it, but opening your own recipe again shows a different arrangement. "
        "To fix the picture, write the number on the layer in the recipe, for example `random_state: 0`."
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
