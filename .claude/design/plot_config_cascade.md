# Design: Plot Configuration Priority Cascade
# Tracks: VIZFAC-PLOT-CASCADE-1
# Status: DESIGN — accepted 2026-05-10. Implementation split into concrete tasks (see §10).
# Authority: @dasharch
# Companion ADRs: ADR-024 (3-Tier Lifecycle), ADR-049 (T3 Audit Scoping), ADR-079 (Runtime Errors)

---

## 0. TL;DR

Today, plot configuration is merged in two places (`_standardize_config()` for `plot_defaults` → spec; `_apply_palette()` ad-hoc) and one optimisation pass (`_auto_adjust_axis_labels()`) runs at the end. T3 `aesthetic_override` nodes are recorded and exported but **never applied to the rendered plot** — they are silently dropped on the way to plotnine.

This document defines a single five-tier priority cascade resolved at one merge point inside `VizFactory.render()`. The cascade is data-driven (a flat dict of resolved keys produced by `resolve_plot_config()`) so the render path becomes "merge then build" rather than "build while merging". This change unlocks T3 aesthetic overrides, makes `plot_defaults` schema explicit, and creates the seam Blueprint IDE can mount a `plot_defaults` editor onto.

---

## 1. Current State (as of 2026-05-10)

### 1a. Where merging happens today

| Location | Function | What it merges | Order |
|---|---|---|---|
| `viz_factory.py:79–80` | `_standardize_config(raw_plot_config, manifest_defaults)` | `plot_defaults` keys not present in spec | spec wins; defaults fill gaps |
| `viz_factory.py:282–287` | `_auto_adjust_axis_labels(p, ...)` | Auto-rotation + auto-size for axis text | runs unless an `element_text` layer for that axis is in the manifest |
| `viz_factory.py:289–302` | Palette injection | `plot_config["palette"]` resolved against built-in + project palette registry | only if the corresponding scale layer is absent |

There is **no separate optimisation layer**; `_auto_adjust_axis_labels` is the sole optimisation, baked into the render flow.

### 1b. T3 `aesthetic_override` state

- Node type is registered (`session_manager.py:46`, `audit_stack.py:40, 94`).
- Audit panel renders the node with the 🎨 icon.
- Export bundle's `report.qmd` includes `"Plot aesthetics were adjusted: {keys}"` in Methods.
- Export bundle's `t3_steps.yaml` records the params.
- **Never read by `VizFactory.render()`.** No code path threads `t3_plot_overrides[plot_id]` into the plot config.

This is the load-bearing gap that motivates this design — without the cascade, threading T3 overrides means duct-tape merging in three places.

### 1c. `plot_defaults` schema today

Sole use across project + gallery manifests (grep confirmed):

```yaml
plot_defaults:
  default_font_family: "Liberation Sans"
```

The `palette:` key was specified in `rules_viz_factory.md §6b` and `rules_manifest_structure.md §10` as a supported `plot_defaults` key but is not currently used in any committed manifest. The block is essentially undocumented and unenforced — manifest authors guess.

---

## 2. The Cascade — Five Layers, One Resolution

Resolution order (highest wins):

| Tier | Source | Authority over | Modifiable by |
|---|---|---|---|
| **L5** | T3 `aesthetic_override` for the active plot | All visual aesthetics (fill, colour, alpha, shape, size, palette) | Analyst (T3 sandbox) |
| **L4** | Plot `spec:` — `analysis_groups.<grp>.plots.<id>.spec` | Aesthetics, mapping, layers, scales, theme, facet | Manifest author |
| **L3** | Optimisation layer (computed from data + spec at render time) | Visual-only (axis text rotation, font sizing, density-aware layout) | None — emitted by VizFactory |
| **L2** | Manifest `plot_defaults:` block | Cross-plot defaults (palette, theme, font_family) | Manifest author |
| **L1** | VizFactory built-in defaults | Last-resort fallbacks (`theme_bw`, `coord_cartesian`, `facet_null`) | Developer |

**Conflict rule:** every key resolves to exactly one source. When two tiers compete for the same key (e.g. L5 sets `palette: foo`, L4 sets `palette: bar`), the higher tier wins silently — there is no merge-of-values, only winner-takes-all per key. The exception is the `layers:` list, which is **append-then-deduplicate** (see §4).

**Why optimisation is L3 (between spec and defaults), not L0:**
The optimisation layer is a *computed default* — it should fill in what the spec didn't say, but should never override what the spec did say. Putting it above `plot_defaults` ensures auto axis rotation only fires when neither the spec nor the manifest defaults have addressed axis text. Putting it below the spec ensures a manifest author's explicit `element_text` always wins.

---

## 3. Resolution Function — `resolve_plot_config()`

The cascade is implemented as a pure function with one merge point. No partial merges anywhere else in the render path.

```python
# libs/viz_factory/src/viz_factory/plot_config_resolver.py
def resolve_plot_config(
    raw_spec: dict,
    plot_defaults: dict,
    df_collected: "pd.DataFrame",      # post-filter, post-Tier3 frame
    *,
    aesthetic_override: dict | None = None,   # T3 override for THIS plot_id
) -> dict:
    """Resolve the five-tier cascade to a single flat dict.

    Returns a dict with these keys (always present, may be empty/None):
      - mapping:        dict[str, str]   aesthetic → column
      - layers:         list[dict]       ordered layer specs (append-then-dedupe)
      - theme:          str | None       resolved theme name
      - facet_by:       str | None
      - palette:        str | None
      - palette_scope:  set[str]         {"fill", "color"} subset
      - labels:         dict             {title, x, y, fill, ...}
      - guides:         dict
      - filters:        list[dict]       UI predicate-pushdown filters
      - title:          str | None       (legacy flat key)
      - element_text:   dict             explicit per-axis overrides from spec layers
      - factory_id:     str | None
      - _provenance:    dict[str, str]   key → source tier ("L1".."L5") for debugging
    """
```

Resolution algorithm (order matters):

1. **Seed with L1 built-ins.** Constants from `_BUILTIN_DEFAULTS` dict at module top.
2. **Layer L2 over the seed.** Walk `plot_defaults`; for each key not in the seed (or in the seed as a built-in), copy in. Mark provenance `L2`.
3. **Compute L3 optimisation.** Run `compute_optimisation_layer(seed, raw_spec, df_collected)` — see §5. Layer over the seed; mark provenance `L3`.
4. **Layer L4 spec.** Walk `raw_spec`; for each key, override the seed unconditionally. Mark provenance `L4`. Special case: `layers:` is append-and-dedupe (§4).
5. **Layer L5 T3 override.** If `aesthetic_override` is non-None, walk it; for each key, override the seed unconditionally. Mark provenance `L5`. The override has a fixed schema (§6).

Output is a flat dict consumed by `VizFactory.render()` after the resolver returns. The render code then walks the dict and emits plotnine objects — no further merging.

---

## 4. The `layers:` List Is Special — Append-Then-Dedupe

Layers do not behave like scalar keys. A spec that adds a `geom_text` annotation must not displace `plot_defaults`'s `theme_dashboard` theme. The rule:

```
final_layers = (
    L2.layers (if any)             # rare — most plot_defaults blocks omit layers
    + L3.layers (optimisation)     # currently empty list; reserved for future
    + L4.layers                    # the spec's layer list
    + L5.layers (if any)           # T3 may inject a scale_*_manual when palette overridden
)
# Then: deduplicate by `(layer_kind, target)` keeping LAST occurrence
```

Where `layer_kind` is the prefix family (`theme_*`, `coord_*`, `facet_*`, `scale_fill_*`, `scale_color_*`, `element_text` with same `target` param). This ensures L5 → L4 → L3 → L2 dedup order: a higher-tier layer of the same kind suppresses lower ones.

`geom_*` and `stat_*` layers are **never deduplicated** — they accumulate. A spec adding `geom_text` on top of a `geom_bar` keeps both.

**Default injection** (currently inline at end of `render()`) is moved into L1: if no `theme_*` layer survives dedup, L1 contributes `theme_bw`; same for `coord_cartesian` and `facet_null`. The injection becomes part of resolution rather than a render-time afterthought.

---

## 5. The Optimisation Layer (L3)

Optimisation is the only layer that reads the materialised data frame. It is computed by `compute_optimisation_layer(seed, raw_spec, df_collected) -> dict` and returns a partial dict to layer over the seed.

### 5a. Scope (locked)

The optimisation layer is **purely visual / aesthetic**. It MUST NOT:
- Change the `mapping:` (aesthetic → column).
- Change `factory_id:` or any `geom_*` layer.
- Change `filters:` (those are L4 explicit).
- Change `palette:` (that's an aesthetic-data choice the analyst owns).

It MAY:
- Emit `element_text` layers targeting axis text (size, rotation, ha).
- Emit `theme(panel_spacing=...)` adjustments for facet density.
- Emit `position_jitter(width=...)` or analogous spacing-only positions when overplotting is detected.

Anything outside that envelope requires extending the locked scope here first — agents do not invent new optimisation behaviours ad hoc.

### 5b. Current behaviour preserved

The existing `_auto_adjust_axis_labels()` heuristic (rotation + size based on `n_unique` and `max_len` of the column) is the entire L3 implementation today. It moves into `compute_optimisation_layer` with no behavioural change. The per-axis guard logic ("skip if manifest already addressed it") becomes implicit: L4 wins by virtue of being a higher tier, so the L3 emission for that axis is overridden during dedup.

### 5c. Future extensions (deferred — non-blocking)

Reserved hooks for future optimisation work, **not implemented in the initial cascade** but designed so they can plug into L3 without further architecture changes:

| Heuristic | Trigger | L3 emission |
|---|---|---|
| Density-aware jitter | scatter with `n_rows / unique(x*y) > 5` | `position_jitter(width=0.2, height=0.0)` |
| Facet panel spacing | `facet_wrap` with `n_facets > 6` | `theme(panel_spacing=0.4)` |
| Legend ncol auto | discrete fill/color with `n_levels > 8` | `guides(fill=guide_legend(ncol=2))` |

Each is opt-in via a future `optimisation:` block in `plot_defaults` (e.g. `optimisation: {density_jitter: true}`) — disabled-by-default to keep current visual behaviour stable. The cascade design accommodates this; the heuristics themselves are out of scope for VIZFAC-PLOT-CASCADE-1.

### 5d. Path B (two-pass render) — accepted long-term direction

The decision recorded in the original task ("Path B (two-pass render) correct long-term; current `_auto_adjust_axis_labels()` stays as-is until designed") is honoured: the cascade implementation is single-pass (build the resolved config dict, then build plotnine once). A genuine two-pass render — render once at low quality, measure tick label widths from the rendered figure, then re-render with informed sizes — is a future evolution of L3 that this design does not preclude. The key compatibility constraint is that L3 must remain a pure function of `(seed, raw_spec, df_collected)` and may not depend on a partial render result. Two-pass would relax that to `(seed, raw_spec, df_collected, low_quality_figure)` — additive, not breaking.

---

## 6. T3 `aesthetic_override` — Fixed Schema for L5

T3 nodes have free-shape `params` today. For L5 to be reliable, `aesthetic_override` nodes get a fixed sub-schema that the resolver knows how to merge.

```yaml
- node_type: aesthetic_override
  id: "t3_node_xxx"
  plot_scope: "amr_heatmap"      # exact plot_id (NOT __all__ — overrides are per-plot)
  params:
    # All keys optional; only supplied keys are applied
    fill_color:    "#ff5733"     # solid fill (single colour)
    fill_palette:  "viridis"     # OR a palette name from registry — mutex with fill_color
    color:         "#222222"     # outline / point colour
    alpha:         0.7           # 0.0–1.0
    shape:         "circle"      # plotnine shape name
    size:          3             # numeric — geom default size
    theme:         "theme_void"  # named theme — overrides plot_defaults.theme
  reason: "Switched to viridis to align with publication colour scheme."
```

Resolution rules:

- `fill_color` and `fill_palette` are **mutually exclusive**. If both are present, `fill_palette` wins (palette is the higher-information signal) and a notification is emitted (`PipelineError` with `severity: warning`, `who: analyst`, `surface: notification`).
- `theme:` from L5 fully replaces L4 / L2 theme.
- `fill_palette` translates to `palette:` in the resolved dict and triggers the existing `_apply_palette()` path.
- `fill_color` (solid) translates to a `scale_fill_manual(values=[colour])` layer injected by L5.
- `color`, `alpha`, `size`, `shape` from L5 translate to layer params on the **first geom layer** in the resolved layer list (the geom is what consumes these aesthetics statically — non-mapped values).
- `aesthetic_override` nodes target exactly one plot (`plot_scope` is a plot_id, never `__all__`). Cross-plot propagation, if needed, is achieved by creating multiple nodes (one per plot) — the propagation modal in audit_stack handles this transparently.

**Why a fixed schema for L5 only:** other T3 node types (`filter_row`, `drop_column`, etc.) operate on the data frame, not on visual config; they have their own application path and don't go through the cascade. Only `aesthetic_override` flows through the visual config layer.

---

## 7. `plot_defaults:` Schema — Explicit Documented Keys

Today's situation ("guess what's allowed") becomes a documented set. Manifest authors get autocomplete; Blueprint IDE gets a form to mount.

### 7a. Allowed keys (initial set — extend by ADR amendment)

```yaml
plot_defaults:
  # Visual style
  palette:             string        # name from palette registry; default for fill+color
  theme:               string        # registered theme component name (e.g. theme_bw)
  default_font_family: string        # plotnine default font (e.g. "Liberation Sans")

  # Layout
  facet_panel_spacing: number        # 0–1, plotnine default 0.05; bumps for dense facets
  legend_position:     string        # "right" | "top" | "bottom" | "left" | "none"

  # Optimisation toggles (reserved — see §5c; default off)
  optimisation:
    auto_axis_text:    bool          # default true (current behaviour)
    density_jitter:    bool          # default false
    panel_spacing:     bool          # default false
    legend_ncol:       bool          # default false
```

Unknown keys in `plot_defaults` emit a `PipelineError` (`severity: warning`, `who: manifest_author`, `surface: notification`). They do not crash — manifest authors can layer experimental keys without breakage — but the warning prevents typos from going silent.

### 7b. Per-plot override

The `spec:` block accepts the same keys as `plot_defaults`. A plot that wants a different palette, theme, or optimisation toggle declares it locally; resolution rules from §2 apply.

---

## 8. Render Path After Cascade

```python
def render(self, df, manifest, plot_id, *, aesthetic_override=None):
    # 1. Pull raw config
    raw_spec = manifest.get("plots", {}).get(plot_id) or _raise_missing_plot(plot_id)
    plot_defaults = manifest.get("plot_defaults", {}) or {}

    # 2. Apply UI filters (Tier 3 predicate pushdown — unchanged)
    df = self._apply_ui_filters(df, raw_spec.get("filters", []))

    # 3. Materialise — needed by the optimisation layer
    df_collected = df.collect().to_pandas()

    # 4. ─── ONE MERGE POINT ───
    config = resolve_plot_config(
        raw_spec=raw_spec,
        plot_defaults=plot_defaults,
        df_collected=df_collected,
        aesthetic_override=aesthetic_override,
    )

    # 5. Build plotnine from the resolved dict
    p = ggplot(df_collected, aes(**config["mapping"]))
    for layer in config["layers"]:
        p = get_component(layer["name"])(p, layer.get("params", {}))
    if config.get("labels"):
        p = p + labs(**config["labels"])
    if config.get("guides"):
        p = p + _build_guides(config["guides"])
    if config.get("palette"):
        p = self._apply_palette(p, config["palette"], config["mapping"], config["palette_scope"])

    return p
```

The render path becomes ~30 lines of "walk the resolved dict and emit". All merge logic is in `resolve_plot_config()`.

---

## 9. Backward Compatibility

- **No manifest changes required for existing plots.** A spec with no `plot_defaults` and no `aesthetic_override` resolves to the same plotnine output as today (modulo dedup tie-breaks, which are tested in §11).
- **The `factory_id` translation** (`bar_logic` → `geom_bar` injection) moves into the resolver as a normalisation step on `raw_spec` before tier merging. Behaviour preserved.
- **The flat aesthetic promotion** (`x:`, `y:`, `fill:` at spec top level → `mapping:`) also moves into the resolver. Behaviour preserved.
- **The auto axis label heuristic** moves to L3. Behaviour preserved (per-axis guard becomes implicit via tier dedup).
- **`single_graph_export_handlers.py` and `export_handlers.py`** continue to call `VizFactory.render()` — the new optional `aesthetic_override=` kwarg defaults to None, so existing callers are unaffected. Threading T3 overrides into export is a follow-up task (see §10).

---

## 10. Implementation Tasks (concrete, derived from this design)

| Task | Effort | Delivers |
|---|---|---|
| **VIZFAC-RESOLVER-1** `[sonnet/high]` | Create `libs/viz_factory/src/viz_factory/plot_config_resolver.py` with `resolve_plot_config()`, `compute_optimisation_layer()`, `_dedupe_layers()`, `_BUILTIN_DEFAULTS`. Pure functions, no plotnine import. Unit tests assert provenance per key for all five tiers and dedup order on `theme_*`/`coord_*`/`facet_*`/`scale_*_*`/`element_text`. |
| **VIZFAC-RENDER-WIRE-1** `[sonnet/medium]` | Refactor `VizFactory.render()` to use `resolve_plot_config()`. Move `factory_id` normalisation, flat-aesthetic promotion, and auto-axis-label heuristic into the resolver. Existing `viz_factory_integrity_suite` MUST pass unchanged. |
| **VIZFAC-T3-OVERRIDE-1** `[sonnet/medium]` | Wire `aesthetic_override` into the call site: `home_theater.py` plot renders extract `home_state["t3_plot_overrides"].get(plot_id)`, pass as `aesthetic_override=` kwarg to `VizFactory.render()`. Schema validation per §6 (mutex check, key whitelist) emits `PipelineError` (depends on DIAG-RUNTIME-BASE-1). |
| **VIZFAC-T3-EXPORT-1** `[sonnet/medium]` | Same wiring in `export_handlers.py` so exported plots reflect T3 overrides. Updates `TECH-T3-THREAD-1` scope. |
| **VIZFAC-DEFAULTS-DOCS-1** `[sonnet/low]` | Document `plot_defaults:` allowed keys (§7a) in `rules_manifest_structure.md §10`, `rules_viz_factory.md §6`, and `docs/appendix/manifest_structure.yaml`. Unknown-key warning machinery: emit `PipelineError` with `who: manifest_author` per §7a. |
| **VIZFAC-BLUEPRINT-FORM-1** `[sonnet/medium]` `[blocked: VIZFAC-DEFAULTS-DOCS-1]` | Blueprint IDE: mount a `plot_defaults` editor form in the BLUEPRINT logic sidebar when the active node is the manifest root. Form fields driven by §7a allowed keys + their `ui_schema` (mirror the action picker pattern). |

Tasks are independently testable. VIZFAC-RESOLVER-1 is the foundation; VIZFAC-RENDER-WIRE-1 makes the system use it without behavioural change; the remaining four are independent feature deliveries that build on the new seam.

---

## 11. Testing — Cascade Truth Table

Each tier-conflict combination is asserted in `libs/viz_factory/tests/test_plot_config_resolver.py`. Truth-table excerpt:

| Test | L5 | L4 | L3 | L2 | L1 | Expected |
|---|---|---|---|---|---|---|
| `theme_only_l1` | — | — | — | — | `theme_bw` | `theme_bw`, provenance L1 |
| `theme_l2_overrides_l1` | — | — | — | `theme_dashboard` | `theme_bw` | `theme_dashboard`, L2 |
| `theme_l4_overrides_l2` | — | `theme_void` | — | `theme_dashboard` | `theme_bw` | `theme_void`, L4 |
| `theme_l5_overrides_l4` | `theme_minimal` | `theme_void` | — | `theme_dashboard` | `theme_bw` | `theme_minimal`, L5 |
| `axis_text_l3_when_no_l4` | — | mapping only | rotation 45 | — | — | rotation 45, L3 |
| `axis_text_l4_suppresses_l3` | — | `element_text(rotation=0)` | rotation 45 | — | — | rotation 0, L4 |
| `palette_l5_mutex_warns` | `fill_color="#ff0", fill_palette="viridis"` | — | — | — | — | palette `viridis`, warning emitted |
| `layers_dedup_keeps_last` | — | `theme_void` then `theme_bw` | — | — | — | `theme_bw` (last in dedup order) |
| `layers_dedup_geoms_accumulate` | — | `geom_bar` + `geom_text` | — | — | — | both layers present |

The truth table prevents regressions; it is the contract document of the cascade.

---

## 12. Out of Scope (Explicit)

- **Two-pass render** — designed for compatibility (§5d) but not implemented.
- **New optimisation heuristics** — designed-for hooks (§5c) but not implemented.
- **Per-persona plot defaults** — a `persona_plot_defaults` template field could layer between L2 and L1 in the future. Not in this design.
- **Manifest-level theme inheritance from a parent manifest** — `!include` resolution is structural, not config-cascading. Out of scope.
- **Aesthetic propagation across plots** — handled by §12g of `ui_implementation_contract.md` via per-plot node duplication. The cascade resolver sees only the per-plot override slice; cross-plot propagation is upstream of the resolver.

---

## 13. References

- ADR-024 — 3-Tier Lifecycle (T1/T2/T3 data flow)
- ADR-049 — Per-Plot T3 Audit Scoping (where `aesthetic_override` lives)
- ADR-079 — Runtime Error Discipline (where unknown-key warnings flow)
- `rules_viz_factory.md §6` — palette resolution (existing rule, refined here)
- `rules_manifest_structure.md §10` — `plot_defaults` block (existing rule, expanded here)
- `ui_implementation_contract.md §12g` — aesthetic_override propagation
- `.claude/design/design_t3_export_threading.md` — companion gap analysis (T3 → export bundle)
