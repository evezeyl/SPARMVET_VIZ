# @deps
# provides: function:resolve_plot_config, function:compute_optimisation_layer,
#           function:_dedupe_layers, constant:_BUILTIN_DEFAULTS,
#           function:normalise_plot_spec, function:serialise_plot_spec
# consumes: libs/utils/src/utils/errors.py (VisualizationError — hard error on legacy keys)
# consumed_by: libs/viz_factory/src/viz_factory/viz_factory.py,
#              libs/viz_factory/tests/test_plot_config_resolver.py,
#              libs/viz_factory/tests/test_plot_spec_roundtrip.py
# doc: .claude/design/plot_config_cascade.md, .claude/design/plot_authoring_model.md
# @end_deps
"""
Five-tier plot configuration cascade resolver (ADR-024 / cascade design 2026-05-10).

This module is intentionally free of plotnine imports — it works on plain Python
dicts and is independently testable. VizFactory.render() calls resolve_plot_config()
as the one merge point, then walks the returned dict to emit plotnine objects.

Tier order (highest wins per key):
  L5 — T3 aesthetic_override for the active plot  (analyst)
  L4 — plot spec (analysis_groups.<grp>.plots.<id>.spec)  (manifest author)
  L3 — optimisation layer (computed from data + spec)  (VizFactory)
  L2 — manifest plot_defaults block  (manifest author)
  L1 — VizFactory built-in defaults  (developer)

The `layers` list uses append-then-deduplicate rather than winner-takes-all.
geom_* and stat_* layers are never deduplicated; all others deduplicate by
(kind, target) keeping the LAST occurrence (so higher tiers win on theme,
coord, facet, scale, and element_text overrides).
"""
from __future__ import annotations

import copy

from utils.errors import VisualizationError

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
    "facet_panel_spacing", "legend_position", "optimisation", "layers",
})

# Keys recognised as part of the spec (not taxonomy / author metadata).
# Any key NOT in this set is moved into the _meta passthrough dict by normalise_plot_spec.
_CANONICAL_SPEC_KEYS: frozenset = frozenset({
    "target_dataset", "mapping", "layers", "theme", "facet_by",
    "palette", "labels", "guides", "filters", "title", "_meta",
})

# Former flat aesthetic keys — checked early in normalise_plot_spec to raise a
# helpful error (ADR-083). Not exported; use mapping: block for canonical specs.
_LEGACY_FLAT_AES: frozenset = frozenset(
    ("x", "y", "color", "colour", "fill", "size", "alpha", "shape", "label")
)


# ---------------------------------------------------------------------------
# Layer dedup key
# ---------------------------------------------------------------------------

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
        return ("theme", None)
    if name.startswith("coord_"):
        return ("coord", None)
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
    return [
        layer for i, layer in enumerate(layers)
        if _layer_dedup_key(layer) is None
        or key_to_last_idx[_layer_dedup_key(layer)] == i
    ]


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

    The inverse of normalise_plot_spec for BLUEPRINT authoring and manifest emission:
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
        Manifest-level plot_defaults block (L2).
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
            for layer in (val or []):
                all_layers.append({**layer, "_tier": "L2"})
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
    for layer in spec.get("layers", []):
        all_layers.append({**layer, "_tier": "L4"})

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

    # ── Deduplicate layers ───────────────────────────────────────────────────
    seed["layers"] = _dedupe_layers(all_layers)

    # ── Derive convenience fields from resolved layers ───────────────────────
    # theme: name of the surviving theme_* layer (or L1 fallback)
    resolved_theme = _BUILTIN_DEFAULTS["theme"]
    for layer in reversed(seed["layers"]):
        if layer.get("name", "").startswith("theme_"):
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
