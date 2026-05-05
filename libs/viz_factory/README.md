# Viz Factory (Artist Pillar)

## Purpose

The `VizFactory (viz_factory.py)` library provides a high-level, declarative interface for generating data-agnostic visualizations. It decouples the analytical pipeline from visual rendering by using a YAML-based manifest system.

## I/O

- **Input**: `pl.LazyFrame` (Polars) and a Dictionary (Manifest) following the SPARMVET visualization spec.
- **Output**: A `ggplot` object (Plotnine) ready for rendering or export.

## Tiered Data Consumption

The `VizFactory (viz_factory.py)` is agnostic to the analytical depth of the incoming data, relying on the **Tier 2 (Branch)** or **Tier 1 (Anchor)** provided by the Transformer.

- **Standard Flow**: The factory consumes **Tier 2** data, which has been pre-reshaped (e.g., pivoted to long format) and filtered for a specific functional group of plots.
- **Identity Fallback**: If no Tier 2 logic is defined (e.g., for a raw metadata table), the factory consumes **Tier 1** "As-Is", applying visual aesthetics directly to the wide tidy data.
- **Interactive Recalculation (Tier 3)**: When a user applies interactive filters in the UI, the factory re-processes the specific **Leaf** view derived from the active Branch, ensuring sub-second response times on large datasets.

## Architectural Features

- **Visual Cookbook Integration (ADR-033)**: Supports educational split-pane documentation, pairing technical manifests with structured Markdown guidance for enhanced visual literacy.

## Smart Default Hierarchy

The `VizFactory (viz_factory.py)` implements a tiered default injection policy to ensure plots render successfully even with sparse manifest definitions:

1. **Plot-Level Specs**: Explicit layers defined in the plot's `layers` block take absolute priority.
2. **Manifest-Level Defaults**: The factory automatically merges the top-level `plot_defaults` block from the active manifest into each plot's configuration. This allows you to define a global theme or color scheme once for an entire pipeline.
3. **Library-Hardcoded Fallbacks**: If no theme or coordinate system is specified at either manifest level, the factory silently injects industry-standard defaults (e.g., `theme_bw`, `coord_cartesian`).

## Tier 3 Predicate Pushdown (UI Filters)

`VizFactory.render()` accepts a `filters` list in the plot config (injected by `home_theater.py` from `applied_filters`). Filters are applied to the Polars LazyFrame **before** Pandas materialisation, preserving the Polars-first mandate.

Supported ops: `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `not_in`, `between`.

- `in` / `not_in`: value must be a list; `pl.col(col).cast(Utf8).is_in(str_vals)` (string-cast both sides for safe comparison).
- Scalar ops: value is auto-coerced to the column dtype read from `df.collect_schema()` (string operands on numeric columns get converted to int/float). String operand on a numeric column triggers a `[viz_factory] ⚠️` log line — that signals a widget bypass.
- `between`: value is `[lo, hi]`; uses `pl.col(c).is_between(lo, hi, closed=...)`. Honours an optional `closed` field on the filter row (`'both'` default = inclusive, `'none'` = exclusive).
- Auto-promotion: `eq` with a list value is silently upgraded to `in`; same for `ne` → `not_in`.
- **Note:** `dtype` key from the filter recipe builder is stripped before injection — VizFactory filter dicts do not use it (the dtype is re-read from the LF schema each call).

Both filter paths (this one + `_apply_filter_rows` in `home_theater.py`) implement identical logic. Locked down by `app/tests/test_filter_operators.py` (21 cases).

## Auto Axis Label Adjustment (IU-7, 2026-04-23)

`VizFactory._auto_adjust_axis_labels(p, df_collected, x_col, y_col)` is applied automatically at the end of every `render()` call unless the manifest already has an explicit `element_text` layer targeting that axis.

**X-axis rules (categorical only — numeric/datetime left untouched):**

| Condition | Result |
|-----------|--------|
| `max_len > 12` | 45° rotation, size 8, ha right |
| `max_len > 6` | 35° rotation, size 9, ha right |
| `n_unique > 12` (short labels) | size 8, no rotation |
| `n_unique > 6` (short labels) | size 9, no rotation |

**Y-axis rules (categorical only):**

| Condition | Result |
|-----------|--------|
| `n_unique > 20` or `max_len > 20` | size 7 |
| `n_unique > 12` or `max_len > 12` | size 8 |

To suppress auto-adjustment for a specific axis, add an `element_text` layer targeting `axis_text_x` or `axis_text_y` in the manifest — the auto-adjuster skips axes already addressed by the manifest.

## Aesthetic Validation Gate (ADR-034)

To prevent silent failures, the factory performs a "Pre-Flight" check before rendering:

- **Typo Detection**: If a manifest aesthetic (x, y, fill) references a missing column, the system uses string-similarity heuristics to suggest the closest matches in the dataset.
- **Fail-Fast**: Invalid aesthetics trigger a `VisualizationError` with a helpful `tip` for the user, rather than producing an empty frame or crashing the UI.

## Documentation
>
> [!IMPORTANT]
> This README is a high-level summary. For exhaustive component deep-dives, usage tutorials, and the testing rationale, you MUST refer to the official [Viz Factory Dev-to-User Guide](../../docs/workflows/visualisation_factory.qmd).

## Library Integrity Status

- **Status**: 🟢 **VERIFIED** (100% Registry Alignment)
- **Component Audit**: 175 Components Registered
- **Pass Rate**: 98% (172/175 Passed, 2 Timedelta failures pending dtypes, 1 Spatial data constraint)
- **Last Audit**: 2026-04-17 (Automated Suite v3)

## Key Components (Violet Standard)

- **VizFactory (viz_factory.py)**: Central orchestration class that handles manifest parsing and ggplot composition. Supports explicit `title`, `subtitle`, and `caption` mapping from the manifest via the `labs` layer.
- **GeomFactory (geoms/core.py)**: Registry for 40+ geometric and statistical layers (Point, Line, Bar, Density, Sina, etc.) including the boxplot/violin family.
- **ScaleFactory (scales/core.py)**: Handles visual scaling, axis naming, and math/date transformations (log10, sqrt, datetime). DECO-2 (2026-04-30) added the aesthetic-generic family: `scale_alpha[_manual]`, `scale_size[_manual|_area]`, `scale_shape[_manual]`, `scale_linetype[_manual]`, `scale_color_hue` / `scale_fill_hue`, `scale_color_continuous` / `scale_fill_continuous`.
- **ThemeFactory (themes/core.py)**: Manages stylistic presets including 3rd-party themes (538, Seaborn, XKCD), the multi-label `labs` component, and DECO-2 single-axis label helpers `xlab` / `ylab` / `ggtitle` / `annotate` (free-form text/segment/rect/point overlays).
- **FacetFactory (facets/core.py)**: Orchestrates layout partitioning (Wrap, Grid).
- **GalleryMaterializer (assets/scripts/materialize_manifest_plots.py)**: [Audit Utility] Cross-pillar tool for materializing all plots in a manifest into Layer 3 PNGs for bulk verification.
- **IntegritySuite (viz_factory_integrity_suite.py)**: [Orchestrator] Programmatically audits all 193+ registered components for 1:1:1 evidence (was 176 before DECO-2).

- **VisualisationRunner (debug_runner.py)** - [Dev Tool]: High-performance CLI for rendering isolated components and verifying manifest mappings.
- **Audit (debug_audit.py)** - [Validator]: Scans for Ghost Tasks (Tasks marked [x] but missing logic).
- **Distiller (debug_distiller.py)** - [Component Debugger]: Isolated test for Color Distiller palettes and scaling.
- **Sync (debug_bulk_sync.py)** - [Developer Utility]: Logic tool to auto-reflect library test results into the central task tracker.
- **ActionRegistry (registry.py)**: Decorator-based system for the dynamic extension of plot components.

## Tests

Three tiers of automated tests:

### 1. Pytest — fast component contract check (sub-second)

Verifies every registered component imports correctly, accepts realistic specs, and returns a valid `ggplot` object. Run from the project root:

```bash
./.venv/bin/python -m pytest libs/viz_factory/tests/ -v
```

Test modules:
- `tests/test_deco2_components.py` — DECO-2 wrappers (38 cases)

### 2. Integrity suite — end-to-end PNG materialisation

Walks every `*_test.yaml` in `tests/test_data/` through `debug_runner.py` and writes PNG artefacts. Heavier (matplotlib renders) but the most thorough check that a component works end-to-end through manifest → ggplot → image:

```bash
./.venv/bin/python libs/viz_factory/tests/viz_factory_integrity_suite.py --output_dir tmp/viz_factory/
```

### 3. Single-component CLI render (dev workflow)

```bash
./.venv/bin/python libs/viz_factory/tests/debug_runner.py libs/viz_factory/tests/test_data/{component}_test.yaml --output_dir tmp/viz_factory/
```

For each new `@register_plot_component`, follow the implementation workflow in `.claude/workflows/viz_factory_implementation.md`:
1. Create `tests/test_data/{name}_test.yaml`
2. Add a pytest case in the appropriate `tests/test_*.py` module (or create a new one)
3. Render via debug_runner; verify the PNG; update README; mark task done.

Refer to the [Visualisation Factory Workflow](../../docs/workflows/visualisation_factory.qmd) for detailed implementation and usage examples.
