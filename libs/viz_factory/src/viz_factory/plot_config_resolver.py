# @deps
# provides: function:resolve_plot_config, function:compute_optimisation_layer,
#           function:_dedupe_layers, constant:_BUILTIN_DEFAULTS
# consumes: -   (pure functions — no plotnine import, no cross-lib imports)
# consumed_by: libs/viz_factory/src/viz_factory/viz_factory.py,
#              libs/viz_factory/tests/test_plot_config_resolver.py
# doc: .claude/design/plot_config_cascade.md
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
    "factory_id":     None,
    "element_text":   {},   # convenience dict for L3 axis-text overrides
    "theme":          "theme_bw",  # derived from resolved layers after dedup
}

# factory_id → default base geom (may be overridden by bar_logic y-check)
_FACTORY_GEOMS: dict[str, dict] = {
    "heatmap_logic":  {"name": "geom_tile",    "params": {"color": "white", "size": 0.1}},
    "bar_logic":      {"name": "geom_bar",      "params": {}},
    "scatter_logic":  {"name": "geom_point",    "params": {}},
    "boxplot_logic":  {"name": "geom_boxplot",  "params": {}},
    "violin_logic":   {"name": "geom_violin",   "params": {}},
}

# Allowed keys in plot_defaults: (unknown keys emit a PipelineError warning)
_VALID_PLOT_DEFAULTS_KEYS: frozenset = frozenset({
    "palette", "theme", "default_font_family",
    "facet_panel_spacing", "legend_position", "optimisation", "layers",
})

# Flat aesthetic keys that may appear at the spec top level (legacy/shorthand)
_FLAT_AESTHETIC_KEYS: tuple = ("x", "y", "color", "colour", "fill",
                               "size", "alpha", "shape", "label")


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
# Spec normalisation — factory_id translation and flat aesthetic promotion
# ---------------------------------------------------------------------------

def _normalise_spec(raw_spec: dict) -> dict:
    """Promote flat aesthetics → mapping and expand factory_id → base geom layer.

    This is a pure transformation of the L4 spec; it does not merge tiers.
    """
    spec = copy.deepcopy(raw_spec)

    # 1. Promote flat aesthetics to mapping (if mapping not already explicit)
    if "mapping" not in spec:
        mapping = {k: spec[k] for k in _FLAT_AESTHETIC_KEYS if k in spec}
        if mapping:
            spec["mapping"] = mapping

    # 2. factory_id → base geom (prepend if not already present)
    factory_id = spec.get("factory_id")
    if factory_id:
        base_geom = copy.deepcopy(_FACTORY_GEOMS.get(factory_id))
        if base_geom:
            mapping = spec.get("mapping", {})
            # bar_logic: use geom_col when y aesthetic is explicitly mapped
            if factory_id == "bar_logic" and "y" in mapping:
                base_geom = {"name": "geom_col", "params": {}}
            # heatmap_logic: remap 'color' → 'fill' in mapping
            if factory_id == "heatmap_logic" and "color" in mapping:
                spec["mapping"] = dict(mapping)
                spec["mapping"]["fill"] = spec["mapping"].pop("color")

            existing_layers = spec.get("layers", [])
            existing_geoms = {l.get("name") for l in existing_layers}
            if base_geom["name"] not in existing_geoms:
                spec["layers"] = [base_geom] + existing_layers

    return spec


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

    # Derive mapping from seed (already has L2) + peek at raw_spec for L4 keys
    mapping = dict(seed.get("mapping") or {})
    if not mapping:
        mapping = {k: raw_spec[k] for k in _FLAT_AESTHETIC_KEYS if k in raw_spec}
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
      labels, guides, filters, title, factory_id, element_text,
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
                "labels", "guides", "filters", "factory_id", "theme"):
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
    spec = _normalise_spec(raw_spec)

    # Mapping
    if spec.get("mapping"):
        seed["mapping"] = spec["mapping"]
        provenance["mapping"] = "L4"

    # factory_id
    if spec.get("factory_id"):
        seed["factory_id"] = spec["factory_id"]
        provenance["factory_id"] = "L4"

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

    # spec layers (includes factory_id-injected base geom after _normalise_spec)
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
