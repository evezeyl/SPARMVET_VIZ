"""app/modules/plot_seeds.py
The seed of a plot's jitter, outside the Shiny handlers (Two-Category Law, ADR-045).

SEED-HOLDS-1 (ADR-104 point 3): a seed written in the recipe holds; a seed pinned by an audit step is the
same in the HOME plot, the results bundle, the reproducibility export and its re-run; HOME never replaces a
recipe's seed by the one it drew. The order of precedence itself is one function in the cascade resolver
(`viz_factory.plot_config_resolver.resolve_plot_seed`); this module only gathers its inputs for HOME and for
the export, and shapes what each hands to the render and to the record.

Not decided here (ADR-104, awaiting Eve): which seed a plot uses when the recipe writes none. Today HOME
draws one per session and the export reuses that number (library default when HOME never showed the plot).
"""
from __future__ import annotations

# @deps
# provides: class:SessionSeedDraws, function:home_plot_seed, function:render_seed_args, function:export_plot_seeds,
#           function:seeds_per_plot_record, function:seed_sources_per_plot, function:unfixed_seed_warning,
#           function:bake_plot_seeds, function:seed_pins_from_home_state
# consumes: libs/viz_factory/src/viz_factory/plot_config_resolver.py (resolve_plot_seed, PlotSeed)
# consumed_by: app/handlers/home_theater.py, app/handlers/export_handlers.py, app/tests/test_plot_seeds.py
# doc: .claude/knowledge/architecture_decisions.md#ADR-104, .claude/rules/rules_viz_factory.md#8
# @end_deps

import copy
import secrets
from typing import Callable

from viz_factory.plot_config_resolver import (
    PlotSeed,
    apply_seed_to_layers,
    fixed_seed_of,
    layers_have_jitter,
    recipe_asks_random,
    resolve_plot_seed,
)


def _draw_seed() -> int:
    return secrets.randbits(31)


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


def home_plot_seed(layers: list[dict], audit_pin, draws: SessionSeedDraws, plot_id: str, *, default) -> PlotSeed:
    """The seed HOME shows for a plot. Draws only when nothing else decides: no audit pin, no number in the recipe."""
    needs_draw = layers_have_jitter(layers) and audit_pin is None and fixed_seed_of(layers) is None
    return resolve_plot_seed(layers, audit_pin, draws.get(plot_id) if needs_draw else None, default=default)


def render_seed_args(plot_seed: PlotSeed, t3_overrides: dict | None) -> dict:
    """The keyword arguments of `VizFactory.render` that carry the seed (HOME and the export both use this).

    An audit pin goes into the L5 override (it beats the recipe); every other seed goes in as the fallback,
    which fills only the jitter layers the recipe gives no number.
    """
    override = dict(t3_overrides) if t3_overrides else None
    if plot_seed.source == "audit":
        override = {**(override or {}), "random_state": plot_seed.seed}
    fallback = plot_seed.seed if plot_seed.source in ("recipe", "drawn", "default") else None
    return {"aesthetic_override": override, "fallback_random_state": fallback}


def seed_pins_from_home_state(home_state: dict | None, plot_ids) -> dict[str, object]:
    """{plot_id: seed} pinned in HOME's per-plot overrides (Reshuffle, or an audit override).

    Read whether or not the audit trail (`t3_sandbox_enabled`) is on: the Reshuffle button is not gated by it,
    so a flag-gated read made the export ignore a seed the user had been looking at.
    """
    overrides = (home_state or {}).get("t3_plot_overrides", {}) or {}
    pins = {}
    for plot_id in plot_ids:
        pin = (overrides.get(f"subtab_{plot_id}") or {}).get("random_state")
        if pin is not None:
            pins[plot_id] = pin
    return pins


def export_plot_seeds(
    plots: dict[str, dict],
    audit_pins: dict[str, object],
    home_drawn: dict[str, int],
    *,
    default,
    draw: Callable[[], int] = _draw_seed,
) -> dict[str, PlotSeed]:
    """The seed every exported plot uses, and records.

    audit pin > recipe seed > the seed HOME drew for this plot (`home_drawn`) > for `random_state: null` a
    seed drawn now (recorded: "random on purpose" is still reproducible) > the library default.
    `plots` is {plot_id: spec}; a plot HOME never showed has no entry in `home_drawn`.
    """
    seeds: dict[str, PlotSeed] = {}
    for plot_id, spec in plots.items():
        layers = (spec or {}).get("layers", [])
        drawn = home_drawn.get(plot_id)
        if drawn is None and recipe_asks_random(layers):
            drawn = draw()
        seeds[plot_id] = resolve_plot_seed(layers, audit_pins.get(plot_id), drawn, default=default)
    return seeds


def seeds_per_plot_record(seeds: dict[str, PlotSeed]) -> dict[str, object]:
    """`seeds_per_plot` of effective_run.yaml: the seed each exported jitter plot really used."""
    return {pid: ps.seed for pid, ps in seeds.items() if ps.source != "none"}


def seed_sources_per_plot(seeds: dict[str, PlotSeed]) -> dict[str, str]:
    """Where each recorded seed comes from: audit, recipe, drawn or default (for the reader of the record)."""
    return {pid: ps.source for pid, ps in seeds.items() if ps.source != "none"}


def unfixed_seed_warning(seeds: dict[str, PlotSeed]) -> str | None:
    """The export's warning, only for plots whose seed is neither written in the recipe nor pinned by an
    audit step; in plain words, with what to write in the recipe. None when there is nothing to say."""
    unfixed = [pid for pid, ps in seeds.items() if ps.source in ("drawn", "default")]
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


def bake_plot_seeds(recipe_cfg: dict, seeds: dict[str, PlotSeed]) -> dict:
    """A copy of the recipe in which every exported jitter plot carries the seed it was exported with.

    This is how the re-run reproduces the exported picture: the recipe is the scientific document, so the
    seed is written there, not left to a draw. An audit pin is written on every jitter layer (it beat the
    recipe); any other seed fills only the layers that carry no number (a number the recipe wrote holds).
    A plot that is not in the recipe is an error: nothing is skipped silently (ADR-104).
    """
    baked = copy.deepcopy(recipe_cfg)
    specs = {
        pid: entry.get("spec")
        for group in (baked.get("analysis_groups") or {}).values()
        for pid, entry in (group.get("plots") or {}).items()
    }
    for plot_id, ps in seeds.items():
        if ps.source == "none":
            continue
        spec = specs.get(plot_id)
        if spec is None:
            raise KeyError(
                f"Plot '{plot_id}' is not in the recipe, so its seed {ps.seed} cannot be written into the "
                "reproducibility recipe."
            )
        apply_seed_to_layers(spec.get("layers", []), ps.seed, override_all=ps.source == "audit")
    return baked
