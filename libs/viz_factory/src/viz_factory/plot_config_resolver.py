# @deps
# provides: function:resolve_plot_config, function:compute_optimisation_layer,
#           function:_dedupe_layers, constant:_BUILTIN_DEFAULTS,
#           function:normalise_plot_spec, function:serialise_plot_spec, function:unknown_spec_keys, function:spec_key_names,
#           function:layers_have_random (REPRO-SEED-2), function:recipe_pins_random_state (REPRO-RESHUFFLE-1),
#           function:resolve_layer_seeds, function:apply_pin_to_layers, function:fixed_seed_of, class:LayerSeed (SEED-HOLDS-1)
# consumes: libs/utils/src/utils/errors.py (VisualizationError — hard error on legacy keys)
# consumed_by: libs/viz_factory/src/viz_factory/viz_factory.py,
#              libs/viz_factory/tests/test_plot_config_resolver.py,
#              libs/viz_factory/tests/test_plot_spec_roundtrip.py
# doc: .claude/design/plot_config_cascade.md, .claude/design/plot_authoring_model.md,
#      ADR-097 (aesthetic_override.random_state, REPRO-SEED-1)
# @end_deps
"""
Five-tier plot configuration cascade resolver (ADR-024 / cascade design 2026-05-10).

This module is intentionally free of plotnine imports — it works on plain Python
dicts and is independently testable. VizFactory.render() calls resolve_plot_config()
as the one merge point, then walks the returned dict to emit plotnine objects.

Tier order (highest wins per key):
  L5 — T3 aesthetic_override for the active plot  (analyst)
  L4 — plot spec (analysis_groups.<grp>.plots.<id>.spec)  (data analysis recipe author)
  L3 — optimisation layer (computed from data + spec)  (VizFactory)
  L2 — data analysis recipe plot_defaults block  (data analysis recipe author)
  L1 — VizFactory built-in defaults  (developer)

The `layers` list uses append-then-deduplicate rather than winner-takes-all.
geom_* and stat_* layers are never deduplicated; all others deduplicate by
(kind, target) keeping the LAST occurrence (so higher tiers win on theme,
coord, facet, scale, and element_text overrides).
"""
from __future__ import annotations

import copy
from typing import Any, NamedTuple

from utils.errors import VisualizationError
from utils.random_layers import ALWAYS_RANDOM, is_random_layer

# ---------------------------------------------------------------------------
# L1 — Built-in defaults (constants)
# ---------------------------------------------------------------------------

# Layer lists injected at L1 when no higher tier provides the same kind.
_L1_LAYERS: list[dict] = [
    {"name": "theme_bw",         "params": {}, "_tier": "L1"},
    {"name": "coord_cartesian",  "params": {}, "_tier": "L1"},
    {"name": "facet_null",       "params": {}, "_tier": "L1"},
]

# Scalar defaults used as the seed before tier merging.
_BUILTIN_DEFAULTS: dict = {
    "mapping":        {},
    "palette":        None,
    "palette_scope":  set(),
    "facet_by":       None,
    "title":          None,
    "labels":         {},
    "guides":         {},
    "filters":        [],
    "element_text":   {},   # convenience dict for L3 axis-text overrides
    "theme":          "theme_bw",  # derived from resolved layers after dedup
}

# Allowed keys in plot_defaults: (unknown keys emit a PipelineError warning)
_VALID_PLOT_DEFAULTS_KEYS: frozenset = frozenset({
    "palette", "theme", "default_font_family",
    "facet_panel_spacing", "legend_position", "optimisation", "layers", "random_state",
})

# Keys recognised as part of the spec (not taxonomy / author metadata).
# Any key NOT in this set is moved into the _meta passthrough dict by normalise_plot_spec.
_CANONICAL_SPEC_KEYS: frozenset = frozenset({
    "target_dataset", "mapping", "layers", "theme", "facet_by",
    "palette", "labels", "guides", "filters", "title", "_meta",
})

def unknown_spec_keys(raw_spec: dict) -> list:
    """The keys of a plot spec that are not part of the format, in the order written (VIZ-STANDARD-1, V6).

    `normalise_plot_spec` moves them into `_meta`, where nothing reads them, so a mistyped key (`theem: theme_bw`) used to
    be dropped without a word. The factory refuses them. `factory_id` and the flat aesthetics are not listed here:
    `normalise_plot_spec` refuses those with its own message (ADR-083). An explicit `_meta` block is allowed.
    """
    return [k for k in raw_spec if k not in _CANONICAL_SPEC_KEYS and k != "factory_id" and k not in _LEGACY_FLAT_AES]


def spec_key_names() -> list:
    """The keys a plot spec may have, sorted, for a message."""
    return sorted(k for k in _CANONICAL_SPEC_KEYS if k != "_meta")


# Former flat aesthetic keys — checked early in normalise_plot_spec to raise a
# helpful error (ADR-083). Not exported; use mapping: block for canonical specs.
_LEGACY_FLAT_AES: frozenset = frozenset(
    ("x", "y", "color", "colour", "fill", "size", "alpha", "shape", "label")
)


# ---------------------------------------------------------------------------
# Layer dedup key
# ---------------------------------------------------------------------------

def is_partial_theme(name: str) -> bool:
    """True for a `theme_*` component that only sets some properties of the theme, read from the registry.

    A component that wraps plotnine's `theme` itself (its `wraps` is `plotnine.theme`) sets properties; one that wraps a
    named theme (`theme_bw`, `theme_minimal`, ...) is a complete theme. An unregistered name counts as complete: the
    factory refuses it when it looks the component up.
    """
    from viz_factory.registry import COMPONENT_SCHEMAS
    wraps = (COMPONENT_SCHEMAS.get(name) or {}).get("wraps") or []
    return bool(wraps) and wraps[0].get("lib") == "plotnine" and list(wraps[0].get("attr_path") or []) == ["theme"]


FACET_SETTINGS = ("facet_scales", "facet_space", "facet_margins", "facet_labeller")


def _layer_dedup_key(layer: dict) -> tuple | None:
    """Return a (kind, target) dedup key for a layer, or None for geom/stat.

    Layers with the same key deduplicate — the last occurrence wins.
    Geom and stat layers return None and are never deduplicated (they accumulate).
    """
    name = layer.get("name", "")
    if not name:
        return None
    # Geoms and stats accumulate
    if name.startswith("geom_") or name.startswith("stat_"):
        return None
    # element_text deduplicates per target axis
    if name == "element_text":
        target = layer.get("params", {}).get("target", "")
        return ("element_text", target)
    # Named layer families (single instance per plot)
    if name.startswith("theme_"):
        # A complete theme replaces a complete theme (one slot, the later wins). A partial theme setting is added to the theme
        # (no slot): `theme_legend_position` after `theme_minimal` used to replace it, and the picture lost the minimal theme.
        return None if is_partial_theme(name) else ("theme", None)
    if name.startswith("coord_"):
        return ("coord", None)
    if name in FACET_SETTINGS:
        # These change a setting of the facet written before them; they are not a facet, so they must not replace it.
        return (name, None)
    if name.startswith("facet_"):
        return ("facet", None)
    if name.startswith("scale_fill_"):
        return ("scale_fill", None)
    if name.startswith("scale_color_") or name.startswith("scale_colour_"):
        return ("scale_color", None)
    if name.startswith("scale_x_"):
        return ("scale_x", None)
    if name.startswith("scale_y_"):
        return ("scale_y", None)
    if name.startswith("scale_"):
        # Remaining scale families deduplicate by their second token
        parts = name.split("_", 2)
        family = parts[1] if len(parts) > 1 else name
        return ("scale_" + family, None)
    # Everything else deduplicates by exact name
    return (name, None)


# ---------------------------------------------------------------------------
# _dedupe_layers
# ---------------------------------------------------------------------------

# Components the factory treats by NAME, outside their own handler: it seeds the random ones and batches element_text
# into one theme() call. The registry field `plotnine` of these is therefore never `exact`
# (libs/viz_factory/tests/test_component_plotnine_field.py derives it from this set).
BATCHED_COMPONENTS = ("element_text",)
FACTORY_NAMED_COMPONENTS = frozenset(ALWAYS_RANDOM + BATCHED_COMPONENTS)


def _is_random_layer(layer: dict) -> bool:
    """True if a layer is random: a component that draws random numbers, a layer placed with `position: jitter`
    or `jitterdodge`, or a bootstrapped summary (`utils.random_layers`, the one rule the recipe checker shares).
    Used by the L5 random_state injection below and by callers that need to know whether a seed is meaningful
    for a plot before resolving the full config."""
    return is_random_layer(layer.get("name"), layer.get("params"))


def layers_have_random(layers: list[dict]) -> bool:
    """True if any layer in an unresolved L4 `layers:` list carries jitter (ADR-097
    decision 2 / REPRO-SEED-2) — used to decide whether a plot's seed is worth drawing,
    bookkeeping, or exporting at all, before paying for a full `resolve_plot_config()` call."""
    return any(_is_random_layer(layer) for layer in (layers or []))


def _is_random_word(seed) -> bool:
    """True for the spellings that mean "no fixed seed": None (null in YAML) and the word random,
    in any case and with spaces. Mirrors viz_factory._generator, which is what really reads the value."""
    return seed is None or (isinstance(seed, str) and seed.strip().lower() == "random")


def _as_seed(seed):
    """The seed as the number it stands for (the recipe may write 123 or "123"); a value that is
    not a number is returned as written, so that the render refuses it with its own message."""
    try:
        return int(seed)
    except (TypeError, ValueError):
        return seed


_NO_NUMBER = object()


def _written_seed(layer: dict):
    """The number a jitter layer's recipe writes as `random_state`, or _NO_NUMBER when it writes none
    (no key, null, or the word random)."""
    params = layer.get("params") or {}
    if "random_state" not in params or _is_random_word(params["random_state"]):
        return _NO_NUMBER
    return _as_seed(params["random_state"])


def fixed_seed_of(layers: list[dict]):
    """The number written on the first jitter layer of a plot that carries one, or None when no jitter
    layer carries a number. Only a yes/no for callers (Reshuffle is hidden when the recipe fixes a seed);
    the seed each layer really uses is `resolve_layer_seeds`."""
    for layer in (layers or []):
        if _is_random_layer(layer):
            written = _written_seed(layer)
            if written is not _NO_NUMBER:
                return written
    return None


def recipe_pins_random_state(layers: list[dict]) -> bool:
    """True if the recipe's own L4 `layers:` already pins a jitter layer's
    `random_state` to a fixed number (issue #49/REPRO-RESHUFFLE-1) — `None` or the
    string `"random"` both mean "no fixed seed, draw fresh" (viz_factory.py's own
    `_seed_random_components` rule), anything else is a deliberate author pin. Used to
    decide whether a "Reshuffle" control is meaningful: redrawing a seed the recipe
    author already fixed would silently override their choice without being obviously
    so — the control stays hidden in that case."""
    return fixed_seed_of(layers) is not None


def apply_pin_to_layers(layers: list[dict], seed) -> None:
    """Write an audit pin as `random_state` on every random layer, in place: it replaces any number the recipe
    wrote. The one place that writes a seed into layers (the cascade does it)."""
    for layer in layers:
        if _is_random_layer(layer):
            layer["params"] = {**(layer.get("params") or {}), "random_state": seed}


class LayerSeed(NamedTuple):
    """The seed one random layer of a plot uses, and where it comes from.

    index: position of the layer in the plot's `layers:` list. layer: its name.
    source: "audit" (pinned by an audit step), "recipe" (the number the recipe writes on THIS layer), "default"
    (the recipe writes none: the factory's seed, 0 unless the factory was built with another), "recipe default"
    (the recipe writes none on the layer but `plot_defaults.random_state`: PROVISIONAL S3).
    """
    index: int
    layer: str
    seed: Any
    source: str


def resolve_layer_seeds(layers: list[dict], audit_pin=None, *, default, recipe_default=None) -> tuple[LayerSeed, ...]:
    """The seed of every random layer of a plot, in one place (SEED-HOLDS-1, ADR-104).

    Per layer: a seed pinned by an audit step (cascade level L5, every random layer) > the number the recipe
    writes on THIS layer > PROVISIONAL (S3) `plot_defaults.random_state`, the one seed of the whole recipe
    (`recipe_default`) > the default (`default`: the factory's seed, 0) when the layer writes none. A layer that
    writes a number keeps it and never gives it to another layer. Empty when the plot has no random layer.
    (`random_state: null` and the word random are refused by the checker and the factory: a seed is a number.)
    """
    out = []
    for index, layer in enumerate(layers or []):
        if not _is_random_layer(layer):
            continue
        name = layer.get("name") or ""
        written = _written_seed(layer)
        if audit_pin is not None:
            out.append(LayerSeed(index, name, _as_seed(audit_pin), "audit"))
        elif written is _NO_NUMBER and recipe_default is not None:
            out.append(LayerSeed(index, name, _as_seed(recipe_default), "recipe default"))
        elif written is _NO_NUMBER:
            out.append(LayerSeed(index, name, default, "default"))
        else:
            out.append(LayerSeed(index, name, written, "recipe"))
    return tuple(out)


def _dedupe_layers(layers: list[dict]) -> list[dict]:
    """Deduplicate layers by (kind, target) keeping LAST occurrence.

    geom_* and stat_* return None from _layer_dedup_key and are never removed.
    All other layer kinds: if the same key appears multiple times, only the
    last instance is kept.  This ensures higher tiers (appended later) win.
    """
    # Pass 1: record the index of the LAST occurrence for each dedup key.
    key_to_last_idx: dict[tuple, int] = {}
    for i, layer in enumerate(layers):
        key = _layer_dedup_key(layer)
        if key is not None:
            key_to_last_idx[key] = i

    # Pass 2: keep layers that have no dedup key OR are the last for their key.
    kept = [
        layer for i, layer in enumerate(layers)
        if _layer_dedup_key(layer) is None
        or key_to_last_idx[_layer_dedup_key(layer)] == i
    ]
    # plotnine drops what was set before when a complete theme is added, so a partial theme setting that came first would be lost:
    # the complete theme goes before the first partial one.
    complete = next((i for i, layer in enumerate(kept) if _layer_dedup_key(layer) == ("theme", None)), None)
    first_partial = next((i for i, layer in enumerate(kept)
                          if layer.get("name", "").startswith("theme_") and is_partial_theme(layer["name"])), None)
    if complete is not None and first_partial is not None and complete > first_partial:
        kept.insert(first_partial, kept.pop(complete))
    return kept


# ---------------------------------------------------------------------------
# Spec normalisation — collect _meta, hard-fail on removed legacy keys
# ---------------------------------------------------------------------------

def normalise_plot_spec(raw_spec: dict) -> dict:
    """Normalise a plot spec: collect gallery/author metadata into _meta.

    Pure transformation of the L4 spec; does not merge tiers. Idempotent.

    Keys not in _CANONICAL_SPEC_KEYS (gallery taxonomy, author notes, etc.) are
    moved into a ``_meta`` passthrough dict and preserved verbatim. serialise_plot_spec
    re-expands ``_meta`` to the top level when writing back to YAML.

    Raises VisualizationError for removed legacy keys (ADR-083):
      - factory_id: replaced by explicit geom_* layers in layers:
      - flat aesthetic keys (x, y, fill, …) at top level: replaced by mapping: block
    """
    # Fast-fail on removed legacy keys — actionable errors with migration instructions.
    if "factory_id" in raw_spec:
        factory_id = raw_spec["factory_id"]
        raise VisualizationError(
            f"Plot spec uses removed key 'factory_id' (value: {factory_id!r}). "
            "factory_id was removed in ADR-083. Use explicit 'geom_*' layer in "
            "'layers:' and all aesthetics under 'mapping:'.",
            tip=(
                f"Replace 'factory_id: {factory_id}' with the appropriate geom layer "
                "in 'layers:'. Run 'assets/scripts/migrate_plot_specs.py --apply' "
                "for automatic migration of all plot specs."
            ),
        )
    flat_aes_found = sorted(_LEGACY_FLAT_AES & raw_spec.keys())
    if flat_aes_found:
        raise VisualizationError(
            f"Plot spec contains flat aesthetic key(s) {flat_aes_found!r} at top level. "
            "Flat aesthetics were removed in ADR-083. Place all aesthetics under "
            "a 'mapping:' block.",
            tip=(
                "Use 'mapping: {x: col_name, fill: col_name}' instead of top-level "
                "'x: col_name, fill: col_name'. Run "
                "'assets/scripts/migrate_plot_specs.py --apply' for automatic migration."
            ),
        )

    spec = copy.deepcopy(raw_spec)

    # Collect existing _meta and extract non-canonical keys into it.
    meta: dict = dict(spec.pop("_meta", {}))
    for k in [k for k in list(spec.keys()) if k not in _CANONICAL_SPEC_KEYS]:
        meta[k] = spec.pop(k)

    # Re-attach _meta only when non-empty.
    if meta:
        spec["_meta"] = meta

    return spec


def serialise_plot_spec(canonical: dict) -> dict:
    """Serialise a canonical (normalised) plot spec to a YAML-ready dict.

    The inverse of normalise_plot_spec for BLUEPRINT authoring and data analysis recipe emission:
    - Emits explicit ``mapping:`` (never flat x/y/fill).
    - Emits explicit ``layers:`` (geom is layers[0]).
    - Never emits ``factory_id`` — the canonical form is geom-first.
    - Re-expands ``_meta`` keys back to the top level (taxonomy, author notes).
    - Strips internal ``_tier`` / ``_meta`` markers from layer dicts.

    Round-trip render-equivalence holds: the geom layer and mapping are preserved.
    """
    out: dict = {}

    # target_dataset first for readability
    if "target_dataset" in canonical:
        out["target_dataset"] = canonical["target_dataset"]

    # mapping (never flat aes)
    mapping = canonical.get("mapping")
    if mapping:
        out["mapping"] = dict(mapping)

    # layers — strip internal keys, always include even when empty list
    raw_layers = canonical.get("layers")
    if raw_layers is not None:
        clean: list = []
        for layer in raw_layers:
            entry: dict = {"name": layer["name"], "params": dict(layer.get("params", {}))}
            clean.append(entry)
        out["layers"] = clean

    # scalar optional fields
    for key in ("theme", "facet_by", "palette", "title"):
        val = canonical.get(key)
        if val:
            out[key] = val

    # collection optional fields (only when non-empty)
    for key in ("labels", "guides", "filters"):
        val = canonical.get(key)
        if val:
            out[key] = val

    # re-expand _meta keys to top level (taxonomy, author notes, etc.)
    for k, v in (canonical.get("_meta") or {}).items():
        out[k] = v

    return out


# ---------------------------------------------------------------------------
# L3 — Optimisation layer
# ---------------------------------------------------------------------------

def compute_optimisation_layer(
    seed: dict,
    raw_spec: dict,
    df_collected,  # pandas DataFrame | None
) -> list[dict]:
    """Compute visual-only L3 optimisation layers from data characteristics.

    Currently implements axis text auto-adjustment (same logic as the legacy
    _auto_adjust_axis_labels() in viz_factory.py — preserved verbatim).

    Returns a list of element_text layer dicts.  These are positioned at L3
    and will be overridden by any matching L4/L5 element_text layers via dedup.
    """
    if df_collected is None:
        return []

    # Derive mapping from seed (already has L2) + peek at raw_spec for L4 mapping
    mapping = dict(seed.get("mapping") or {})
    if not mapping:
        raw_mapping = raw_spec.get("mapping") or {}
        mapping = dict(raw_mapping)

    x_col = mapping.get("x")
    y_col = mapping.get("y")

    if x_col is None and y_col is None:
        return []

    try:
        import pandas as pd
    except ImportError:
        return []

    layers = []

    # ── X-axis ──
    x_kwargs: dict = {}
    if x_col is not None and x_col in df_collected.columns:
        col = df_collected[x_col]
        if not (pd.api.types.is_numeric_dtype(col) or
                pd.api.types.is_datetime64_any_dtype(col)):
            unique_vals = col.dropna().unique()
            n_unique = len(unique_vals)
            max_len = max((len(str(v)) for v in unique_vals), default=0)
            if max_len > 12:
                x_kwargs = {"rotation": 45, "size": 8, "ha": "right"}
            elif max_len > 6:
                x_kwargs = {"rotation": 35, "size": 9, "ha": "right"}
            elif n_unique > 12:
                x_kwargs = {"size": 8}
            elif n_unique > 6:
                x_kwargs = {"size": 9}

    # ── Y-axis ──
    y_kwargs: dict = {}
    if y_col is not None and y_col in df_collected.columns:
        col = df_collected[y_col]
        if not (pd.api.types.is_numeric_dtype(col) or
                pd.api.types.is_datetime64_any_dtype(col)):
            unique_vals = col.dropna().unique()
            n_unique = len(unique_vals)
            max_len = max((len(str(v)) for v in unique_vals), default=0)
            if n_unique > 20 or max_len > 20:
                y_kwargs = {"size": 7}
            elif n_unique > 12 or max_len > 12:
                y_kwargs = {"size": 8}
        else:
            n_unique = df_collected[y_col].dropna().nunique()
            if n_unique > 20:
                y_kwargs = {"size": 7}
            elif n_unique > 12:
                y_kwargs = {"size": 8}

    if x_kwargs:
        layers.append({
            "name": "element_text",
            "params": {"target": "axis_text_x", **x_kwargs},
        })
    if y_kwargs:
        layers.append({
            "name": "element_text",
            "params": {"target": "axis_text_y", **y_kwargs},
        })

    return layers


# ---------------------------------------------------------------------------
# Main resolver
# ---------------------------------------------------------------------------

def resolve_plot_config(
    raw_spec: dict,
    plot_defaults: dict,
    df_collected,  # pandas DataFrame | None
    *,
    aesthetic_override: dict | None = None,
) -> dict:
    """Resolve the five-tier cascade to a single flat config dict.

    Parameters
    ----------
    raw_spec : dict
        The plot spec from analysis_groups.<grp>.plots.<id>.spec (L4).
    plot_defaults : dict
        Data analysis recipe-level plot_defaults block (L2).
    df_collected : pd.DataFrame | None
        Materialised DataFrame used by the L3 optimisation layer.
        Pass None to skip optimisation (testing / headless contexts).
    aesthetic_override : dict | None
        T3 aesthetic_override params for this specific plot_id (L5).

    Returns
    -------
    dict with keys:
      mapping, layers, theme, facet_by, palette, palette_scope,
      labels, guides, filters, title, element_text,
      _provenance, _unknown_plot_defaults_keys, _l5_mutex_warn

    The `_provenance` dict maps config keys → "L1".."L5".
    The `_unknown_plot_defaults_keys` list names unrecognised plot_defaults keys
      — the caller (VizFactory) should emit PipelineError warnings for each.
    The `_l5_mutex_warn` bool is True when both fill_color and fill_palette were
      supplied in the aesthetic_override (fill_palette wins per §6).
    """
    provenance: dict[str, str] = {}
    unknown_pd_keys: list[str] = []
    l5_mutex_warn: bool = False

    # ── Accumulate layers in tier order (L1 → L5); dedup at the end ─────────
    all_layers: list[dict] = []

    # ── L1: Built-in defaults ────────────────────────────────────────────────
    seed: dict = copy.deepcopy(_BUILTIN_DEFAULTS)
    for layer in _L1_LAYERS:
        all_layers.append(copy.deepcopy(layer))
    for key in ("mapping", "palette", "facet_by", "title",
                "labels", "guides", "filters", "theme"):
        provenance[key] = "L1"

    # ── L2: plot_defaults ────────────────────────────────────────────────────
    for key, val in (plot_defaults or {}).items():
        if key == "layers":
            for number, layer in enumerate(val or [], start=1):
                all_layers.append({**layer, "_tier": "L2", "_layer_no": number})
        elif key == "palette":
            seed["palette"] = val
            provenance["palette"] = "L2"
        elif key == "theme":
            # theme name from plot_defaults becomes a layer at L2 tier
            all_layers.append({"name": val, "params": {}, "_tier": "L2"})
            provenance["theme"] = "L2"
        elif key in _VALID_PLOT_DEFAULTS_KEYS:
            seed[key] = val
            provenance[key] = "L2"
        else:
            unknown_pd_keys.append(key)

    # ── L3: Optimisation (computed from data + spec) ─────────────────────────
    opt_layers = compute_optimisation_layer(seed, raw_spec, df_collected)
    for layer in opt_layers:
        all_layers.append({**layer, "_tier": "L3"})

    # ── L4: Plot spec ────────────────────────────────────────────────────────
    spec = normalise_plot_spec(raw_spec)

    # WHY: `facet_by` inside `mapping:` is the documented spelling (rules_data_analysis_recipe_structure.md
    # section 8; the Blueprint mapping form writes it there). Plotnine has no such aesthetic and ignores it
    # silently, so without this the plot got no panels (issue #65). A spec-level `facet_by` wins over it.
    if isinstance(spec.get("mapping"), dict) and "facet_by" in spec["mapping"]:
        mapping = dict(spec["mapping"])
        facet_from_mapping = mapping.pop("facet_by")
        spec = {**spec, "mapping": mapping}
        if facet_from_mapping and not spec.get("facet_by"):
            spec["facet_by"] = facet_from_mapping

    # Mapping
    if spec.get("mapping"):
        seed["mapping"] = spec["mapping"]
        provenance["mapping"] = "L4"

    # facet_by
    if spec.get("facet_by"):
        seed["facet_by"] = spec["facet_by"]
        provenance["facet_by"] = "L4"

    # palette (per-plot override beats plot_defaults)
    if spec.get("palette"):
        seed["palette"] = spec["palette"]
        provenance["palette"] = "L4"

    # filters (T3 predicate pushdown — only from spec)
    if spec.get("filters"):
        seed["filters"] = list(spec["filters"])
        provenance["filters"] = "L4"

    # labels (merge: spec labels win; flat title fills in if missing)
    labels = dict(spec.get("labels", {}))
    title = spec.get("title")
    if title:
        seed["title"] = title
        provenance["title"] = "L4"
        if "title" not in labels:
            labels["title"] = title
    if labels:
        seed["labels"] = labels
        provenance["labels"] = "L4"

    # guides
    if spec.get("guides"):
        seed["guides"] = dict(spec["guides"])
        provenance["guides"] = "L4"

    # theme at spec level → inject as a layer at L4
    if spec.get("theme"):
        all_layers.append({"name": spec["theme"], "params": {}, "_tier": "L4"})
        provenance["theme"] = "L4"

    # spec layers
    for number, layer in enumerate(spec.get("layers", []), start=1):
        # `_layer_no` is the position in the author's list, so an error names the layer the author wrote
        all_layers.append({**layer, "_tier": "L4", "_layer_no": number})

    # facet_by flat key → inject facet_wrap if no explicit facet_ layer in spec
    if spec.get("facet_by") and not any(
        l.get("name", "").startswith("facet_") for l in spec.get("layers", [])
    ):
        all_layers.append({
            "name": "facet_wrap",
            "params": {"facets": f"~{spec['facet_by']}"},
            "_tier": "L4",
        })

    # ── L5: T3 aesthetic_override ────────────────────────────────────────────
    if aesthetic_override:
        override = dict(aesthetic_override)

        # fill_color / fill_palette mutex — fill_palette wins, flag the conflict
        has_fill_color = "fill_color" in override
        has_fill_palette = "fill_palette" in override
        if has_fill_color and has_fill_palette:
            l5_mutex_warn = True
            del override["fill_color"]   # fill_palette takes precedence

        if "fill_palette" in override:
            seed["palette"] = override["fill_palette"]
            provenance["palette"] = "L5"

        if "fill_color" in override:
            all_layers.append({
                "name": "scale_fill_manual",
                "params": {"values": [override["fill_color"]]},
                "_tier": "L5",
            })

        if "theme" in override:
            all_layers.append({
                "name": override["theme"],
                "params": {},
                "_tier": "L5",
            })
            provenance["theme"] = "L5"

        # color, alpha, shape, size → stored for render path to apply on first geom
        geom_overrides = {
            k: override[k]
            for k in ("color", "alpha", "shape", "size")
            if k in override
        }
        if geom_overrides:
            seed["_l5_geom_overrides"] = geom_overrides
            provenance["_l5_geom_overrides"] = "L5"

        # random_state (issue #39/ADR-097 decision 2): pin or reshuffle the seed for every
        # jitter-capable layer this plot has, overriding whatever the recipe itself set.
        # Mutates the already-appended L1-L4 layers in place, before dedup — a plot with no
        # jitter at all simply has no layer to match, so this is a no-op for it.
        if "random_state" in override:
            apply_pin_to_layers(all_layers, override["random_state"])
            provenance["random_state"] = "L5"

    # ── Deduplicate layers ───────────────────────────────────────────────────
    seed["layers"] = _dedupe_layers(all_layers)

    # ── Derive convenience fields from resolved layers ───────────────────────
    # theme: name of the surviving theme_* layer (or L1 fallback)
    resolved_theme = _BUILTIN_DEFAULTS["theme"]
    for layer in reversed(seed["layers"]):
        if layer.get("name", "").startswith("theme_") and not is_partial_theme(layer["name"]):
            resolved_theme = layer["name"]
            break
    seed["theme"] = resolved_theme

    # palette_scope: which aesthetics the palette applies to
    scope: set[str] = set()
    if "fill" in seed["mapping"]:
        scope.add("fill")
    if "color" in seed["mapping"] or "colour" in seed["mapping"]:
        scope.add("color")
    # Check if any surviving scale_fill_* blocks palette injection for fill
    has_scale_fill = any(
        l.get("name", "").startswith("scale_fill_") for l in seed["layers"]
    )
    has_scale_color = any(
        l.get("name", "").startswith("scale_color_") or
        l.get("name", "").startswith("scale_colour_")
        for l in seed["layers"]
    )
    # Scope excludes axes already covered by an explicit scale layer
    if has_scale_fill:
        scope.discard("fill")
    if has_scale_color:
        scope.discard("color")
    seed["palette_scope"] = scope

    # element_text: compact view of optimisation axis overrides (for callers that
    # need the values directly without walking the layers list)
    element_text_map: dict = {}
    for layer in seed["layers"]:
        if layer.get("name") == "element_text":
            target = layer.get("params", {}).get("target")
            if target:
                element_text_map[target] = {
                    k: v for k, v in layer["params"].items() if k != "target"
                }
    seed["element_text"] = element_text_map

    # ── Metadata ─────────────────────────────────────────────────────────────
    seed["_provenance"] = provenance
    seed["_unknown_plot_defaults_keys"] = unknown_pd_keys
    seed["_l5_mutex_warn"] = l5_mutex_warn

    return seed
