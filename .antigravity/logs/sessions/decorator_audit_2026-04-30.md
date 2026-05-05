# DECO-1: Decorator Audit — viz_factory & transformer vs polars 1.40 / plotnine 0.15.3

**Date:** 2026-04-30
**Versions:** polars 1.40.1 (was 1.39.3), plotnine 0.15.3 (unchanged)
**Method:** Programmatic diff of `@register_plot_component` / `@register_action` decorators against upstream library API surface.

---

## TL;DR

- **No breaking changes** in either library's API surface that affect existing project code. All polars LazyFrame methods used by transformer actions are still present with compatible signatures. No deprecated polars names (`melt`/`with_column`/`groupby`) used in production code.
- **viz_factory ≈ 88% complete coverage** of plotnine's plot-component API (176 wrapped vs 200 upstream prefixed components).
- **transformer is project-shaped, not API-shaped** — actions are domain-driven (filter_range, derive_categories, etc.), not 1:1 wrappers of polars methods. 63 registered actions cover the project's needs; gaps are not "missing wrappers" but "potentially useful new actions".

---

## viz_factory: Real Gaps Worth Filling

These are plotnine components NOT yet wrapped that have legitimate use in scientific dashboards. Listed by priority.

### High priority (commonly requested)

- **`scale_color_brewer` / `scale_fill_brewer`** — ColorBrewer palettes (Set1, Set2, RdBu, etc.). Standard for categorical fills in publications.
- **`scale_color_gradient` / `scale_color_gradient2` / `scale_color_gradientn`** — continuous color scales (single-hue, diverging two-hue, n-color). The matching `_fill_*` variants too.
- **`scale_color_distiller` / `scale_fill_distiller`** — interpolated ColorBrewer for continuous data.
- **`scale_color_cmap` / `scale_color_cmap_d`** + fill variants — matplotlib colormap bridge (the project already wraps `scale_color_viridis_c/d` as a project-only convenience; `scale_color_cmap` is the underlying generic).
- **`xlab` / `ylab` / `ggtitle`** — the `labs()` wrapper is registered but these single-axis label helpers are commonly used in manifests; manifest authors sometimes prefer one-liners.
- **`annotate`** — adds free-form text/shapes to a plot. Useful for thresholds, callouts.

### Medium priority (used in specific cases)

- **`scale_color_hue`** + fill variant — explicit hue-rotation control.
- **`scale_color_continuous`** + fill variant — alias for the default continuous scale; sometimes referenced by manifest authors.
- **`scale_color_manual`** (British: `scale_colour_manual`) — explicit color mapping. The US spelling (`scale_color_manual`) IS already wrapped; the British alias might be worth registering for consistency since plotnine accepts both.
- **`scale_alpha` / `scale_alpha_manual`** — opacity encoding.
- **`scale_size` / `scale_size_manual` / `scale_size_area`** — scaling for bubble plots.
- **`scale_shape` / `scale_shape_manual`** — categorical shape encoding.
- **`scale_linetype` / `scale_linetype_manual`** — categorical line styles.
- **`stat_pointdensity`** — companion stat for `geom_pointdensity` (geom is wrapped, stat is not).

### Low priority (rare/niche or aliases)

- **`geom_bin2d`, `stat_bin2d`** — these are aliases for `geom_bin_2d` / `stat_bin_2d` (already wrapped). Could register the alias for consistency but no functional gap.
- **`scale_color_desaturate` / `scale_color_gray` / `scale_color_grey`** — desaturation utilities; project's `theme_publication` may handle this differently.
- **`scale_color_ordinal` / `scale_alpha_ordinal` / `scale_size_ordinal` / `scale_fill_ordinal`** — ordinal-data scales; useful but uncommon.
- **`scale_*_datetime`** for color/fill/alpha/size — datetime-driven aesthetics; only relevant for time-series scientific plots.
- **`scale_size_radius` / `scale_stroke`** — niche aesthetic controls.

### Skip (not registrable)

- `theme_get`, `theme_set`, `theme_update` — getters/setters, not plot components.
- `theme_grey` — duplicate spelling of `theme_gray` (already wrapped).
- `qplot`, `ggplot`, `ggsave` — top-level API entry points.
- `after_scale`, `after_stat`, `stage` — internal evaluation helpers.

---

## viz_factory: Project-only Components (intentional)

These have no plotnine equivalent and exist as project conveniences. Keep as-is.

- `scale_color_viridis_c` / `_d` + fill variants — wrappers around `scale_color_cmap(cmap="viridis", ...)`.
- `theme_custom`, `theme_dashboard`, `theme_legend_position`, `theme_publication` — bespoke themes.
- `coord_lims` — likely a wrapper that sets x/y limits in one call.
- `facet_cols`, `facet_rows`, `facet_labeller`, `facet_margins`, `facet_scales`, `facet_space` — manifest-level helpers that translate to `facet_wrap()`/`facet_grid()` parameters.
- `guide_direction`, `guide_label`, `guide_ncol`, `guide_nrow`, `guide_reverse`, `guide_title`, `guide_none` — manifest-level helpers for legend customization.

---

## transformer: Polars Coverage

63 actions registered. The project's action set is **domain-driven** (filter_range, derive_categories, label_if, percentile, z_score, horizontal_stats) rather than a 1:1 wrap of polars. That's the right shape for a data engine — manifest authors should compose high-level intents, not raw polars expressions.

### Polars-method coverage check (informative)

Of the ~50 most-used polars LazyFrame ops, 19 have direct action equivalents. The remaining 31 are either:
- Aggregation primitives (`mean`, `median`, `std`, `var`, `n_unique`, `quantile`) — covered by `summarize` / `horizontal_stats` / `percentile` (composed actions).
- Cumulative ops (`cumsum`, `cummax`, `cummin`) — partial coverage via `cum_sum` and `cum_count`.
- I/O (`read_csv`, `read_excel`, `read_parquet`, `write_*`) — handled by `DataIngestor` outside the action registry (correct separation).
- Generic composition (`with_columns`, `select`) — too general; the project intentionally exposes specific wrappers like `mutate`, `derive_categories`.

### Potentially useful new actions (project-driven, not API-driven)

- **`concat` / `vstack`** — combine multiple datasets vertically. Currently only `join` (horizontal) is supported as a recipe action. Useful for multi-batch ingestion.
- **`fill_nan` (vs `fill_null`)** — explicit NaN handling for Float columns where users distinguish missing-by-design (None) from numerical NaN.
- **`describe_stats` is registered** but sparsely; could be expanded.
- **`rolling_*` / `window_*`** — window operations beyond the existing `window_agg`. Useful for time-series.
- **`upsample` / `downsample`** — datetime resampling. Niche but valuable for time-series projects.

### No urgent gaps

The transformer's coverage is sufficient for the current data engine. New actions should be added when a manifest author reaches for one — not preemptively.

---

## Polars 1.39 → 1.40 — Compatibility Check

| Concern | Status |
|---|---|
| `melt` → `unpivot` rename (polars 1.0) | ✅ project uses `unpivot` exclusively |
| `with_column` → `with_columns` rename | ✅ no `with_column` in project |
| `groupby` → `group_by` rename | ✅ only pandas-side `groupby` in `assets/scripts/figshare_plot_integration.py` (pandas DataFrame, not polars) |
| `pl.Expr.is_between(closed=...)` | ✅ uses string `'both'/'none'/'left'/'right'`, project filter code uses correct values |
| `LazyFrame.collect_schema().names()` vs `.columns` | ✅ migrated in commit `3e8f328` (silenced PerformanceWarnings) |
| `fastexcel` for `pl.read_excel` | ✅ added as ingestion dependency |
| `pyarrow` for parquet custom metadata | ✅ added as transformer dependency (BUG-CACHE-1 era) |

**No code changes required for the polars version bump.**

---

## Plotnine 0.15.3 — Compatibility Check

The project's plotnine version is unchanged (was already 0.15.3). The deferred items in `tasks.md`:

- `scale_x_timedelta`, `scale_y_timedelta` (deferred for dtype-mismatch) — still applicable, retest separately.
- `geom_map` (deferred for spatial-data dependency) — still applicable, no library change needed.

---

## Recommendation

Add a single follow-up task **DECO-2** (enhancement, not blocking) to wrap the high-priority scale_* gaps:

- `scale_color_brewer` / `scale_fill_brewer`
- `scale_color_gradient` / `scale_color_gradient2` / `scale_color_gradientn` (+ fill)
- `scale_color_distiller` / `scale_fill_distiller`
- `scale_color_cmap` / `scale_color_cmap_d` (+ fill)
- `xlab` / `ylab` / `ggtitle`
- `annotate`

These cover the typical scientific publication palette + axis labeling. The medium/low priority items can be added on demand.

**No urgent action required.** The project is fully compatible with polars 1.40.1 and plotnine 0.15.3 as currently installed.
