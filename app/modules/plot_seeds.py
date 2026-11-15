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
#           function:seed_recipe_note, function:bake_plot_seeds,
#           function:seed_pin_steps, function:with_seed_steps
# consumes: libs/viz_factory/src/viz_factory/plot_config_resolver.py (resolve_layer_seeds, LayerSeed)
# consumed_by: app/handlers/export_handlers.py, app/tests/test_plot_seeds.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104, .claude/rules/rules_viz_factory.md#8
# @end_deps

import copy

from viz_factory.plot_config_resolver import resolve_layer_seeds


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

    An audit pin goes into the L5 override (it beats the recipe on every random layer). Nothing else is passed: a
    layer that writes a number keeps it and a layer that writes none uses the factory's seed.
    """
    override = dict(t3_overrides) if t3_overrides else None
    audit = next((ls.seed for ls in seeds if ls.source == "audit"), None)
    if audit is not None:
        override = {**(override or {}), "random_state": audit}
    return {"aesthetic_override": override}


def export_plot_seeds(plots: dict[str, dict], audit_pins: dict[str, object], *, default,
                      recipe_default=None) -> dict[str, Seeds]:
    """The seed of every random layer of every exported plot, and so what is rendered and recorded.

    Per layer: audit pin > the layer's own number > PROVISIONAL (S3) `plot_defaults.random_state` of the recipe
    (`recipe_default`) > the default (`default`: the factory's seed, 0). `plots` is {plot_id: spec}.
    """
    return {
        plot_id: resolve_layer_seeds((spec or {}).get("layers", []), audit_pins.get(plot_id), default=default,
                                     recipe_default=recipe_default)
        for plot_id, spec in plots.items()
    }


def export_seed_plan(plots: dict[str, dict], home_state: dict | None, *, default, recipe_default=None) -> dict[str, Seeds]:
    """What the export handler calls: the pins come from home_state with no flag in between."""
    return export_plot_seeds(plots, seed_pins_from_home_state(home_state, list(plots)), default=default,
                             recipe_default=recipe_default)


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
        for pid, layer_seeds in seeds.items() for ls in layer_seeds if ls.source not in ("recipe", "recipe default")
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


def bake_plot_seeds(recipe_cfg: dict, seeds: dict[str, Seeds]) -> dict:
    """A copy of the recipe in which every random layer carries the seed it was exported with.

    This is how the re-run reproduces the exported picture: the recipe is the scientific document, so the
    seed is written there, not left to a default. A number the recipe wrote on a layer holds (it is the same
    number); an audit pin replaces it; a layer without a number gets the default it was exported with. A plot or
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
            if ls.source not in ("recipe", "recipe default"):  # a recipe default is written in plot_defaults already
                layers[ls.index]["params"] = {**(layers[ls.index].get("params") or {}), "random_state": ls.seed}
    return baked


def seed_pin_steps(seeds: dict[str, Seeds]) -> dict[str, list[dict]]:
    """{plot_id: [step]}: the audit pin of each pinned plot as a step of the audit trail (Eve, 2026-11-15).

    The pin (Reshuffle, or an audit override) changes the picture, so it is a decision of the user and is listed like
    one: in `t3_steps.yaml`, in the Methods text and in the audit trail table of the report, and it is part of the
    audit-steps hash. It is not read from `t3_sandbox_enabled`: Reshuffle works without the audit trail.
    """
    steps = {}
    for plot_id, layer_seeds in seeds.items():
        pinned = [ls for ls in layer_seeds if ls.source == "audit"]
        if pinned:
            steps[plot_id] = [{
                "node_type": "random_seed",
                "id": f"random_seed_{plot_id}",
                "created_at": "",
                "params": {"seed": pinned[0].seed, "layers": [ls.index for ls in pinned]},
                "reason": "The arrangement of the random points was fixed with this seed (Reshuffle arrangement, or an "
                          "audit override); it replaces any seed written in the recipe for these layers.",
            }]
    return steps


def with_seed_steps(t3_by_plot: dict[str, list[dict]], seeds: dict[str, Seeds]) -> dict[str, list[dict]]:
    """A copy of the audited steps per plot with the seed step of each pinned plot added at the end."""
    listed = {plot_id: list(nodes) for plot_id, nodes in t3_by_plot.items()}
    for plot_id, steps in seed_pin_steps(seeds).items():
        listed[plot_id] = listed.get(plot_id, []) + steps
    return listed
