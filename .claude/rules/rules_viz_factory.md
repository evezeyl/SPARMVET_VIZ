---
trigger: always_on
deps:
  provides: [rule:artist_pillar, rule:plotnine_parity, rule:core_geoms_standard]
  documents: [libs/viz_factory/src/viz_factory/viz_factory.py, libs/viz_factory/src/viz_factory/geoms/core.py, libs/viz_factory/src/viz_factory/themes/core.py, libs/viz_factory/src/viz_factory/registry.py]
  consumed_by: [.claude/rules/rules_agent_role_bioscientist.md, .claude/knowledge/dependency_index.md]
---

# Viz Factory & Artist Pillar Protocols (rules_viz_factory.md)

**Authority:** Defines the Artist Pillar standards and Plotnine parity requirements.

## 1. The Artist Parity Mandate (ADR-036)

To ensure the SPARMVET visualization layer remains a competitive alternative to native Python plotting, the `viz_factory` MUST maintain **1:1 Functional Parity** with the Plotnine (ggplot2) API.

- **Parity Rule**: Every Geometry (`geom_*`), Statistic (`stat_*`), Scale (`scale_*`), Coordinate (`coord_*`), and Theme (`theme_*`) available in the stable Plotnine release MUST have a corresponding registration in the Viz Factory.
- **Maintenance**: Upon Plotnine library updates, the agent MUST perform an integrity audit to identify new visual components or parameter changes.
- **Verification**: All new components MUST pass the 1:1:1 evidence loop (Data analysis recipe -> Data -> Plot) before being marked as [DONE].

### 1a. Names of the plot components (DECIDED, not built yet)

Status: the rule is DECIDED (D-0091, D-0210, D-0218). The rename is NOT built. Today the registered names have no prefix. The examples in this file and in the recipes still show the old names until the rename task is done.

- `plotnine_<name>`: the component is exactly the plotnine object `<name>`, nothing changed (D-0091, D-0210).
- `modif_<name>`: the plotnine object `<name>` with a documented change, for example other argument defaults (D-0091, D-0210).
- The exact `plotnine_<name>` is always registered next to a `modif_<name>` (D-0091, D-0210).
- `step_<name>`: a composite of several components (D-0091, D-0210).
- Old names without a prefix are not accepted. An old name is refused with "did you mean" (D-0091).
- The registering decorator keeps a field that says exact, modified or own. A test checks that the prefix and the field agree (D-0092).
- Full parity: the 30 plotnine objects that need no extra package are registered (D-0212).
- Both spellings of the 15 name pairs (`colour` and `color`, `theme_grey` and `theme_gray`, `geom_bin2d` and `geom_bin_2d`) are registered, each exact (D-0213).
- A shortcut component that an exact plotnine component already does is deleted. A recipe writes the exact plotnine component with its arguments (D-0211). Exception, her words: "only functional modifications that are important could eventually be kept"; such a one is kept as a `modif_<name>` next to its exact original (D-0211, D-0210).
- Names written as values stay plotnine's own names (`geom: geom_area`, `stat: stat_bin`, `position: position_identity`) (D-0214).
- The same logic as the Polars actions (`polars_`, `modif_`, `step_`): `.claude/design/recipe_format_spec.md`, DEC31 (D-0091, D-0210).
- Not decided yet: how arguments and nested objects (positions, theme elements, guides, functions as parameters) are passed. This will follow (D-0218).

## 2. The Law of Aesthetics (Data analysis recipe Mapping)

- **Agnostic Mapping**: Component wrappers MUST NOT hardcode aesthetic defaults unless required for stability. Parameters must be passed through from the YAML `spec`.
- **Typo Defense**: All component handlers MUST be registered via `@register_plot_component`. Invalid components requested in a data analysis recipe MUST trigger a `VisualizationError` with closest-match suggestions.
- **Prefixed names**: the naming rule of section 1a applies to every component (D-0218). The old unprefixed names are refused with "did you mean" once the rename is built (D-0091).

## 3. The 1:1:1 Evidence Loop (Testing)

No visual component is considered verified without:

1. **A YAML Data Analysis Recipe**: Located in `tests/test_data/` demonstrating the component usage.
2. **A TSV Dataset**: Providing the minimum required aesthetics for that component.
3. **A Rendered PNG**: Materialized during the `viz_factory_integrity_suite.py` execution.

## 4. Predicate Pushdown — UI Filter Contract

`VizFactory.render()` accepts a `filters` key in the plot config dict. This is the Tier 3 predicate pushdown interface (ADR-024). Filters are applied to the Polars LazyFrame before Pandas hand-off.

**Authoritative op list:** `eq`, `ne`, `gt`, `ge`, `lt`, `le`, `in`, `not_in`, `between`.

- `in` / `not_in`: `value` must be a Python list; values are compared typed, in the type of the column (ADR-104 point 7: `utils.filter_values.filter_condition`, shared with the HOME table and the recipe action `modif_filter`). Only a column of another type (Categorical, Datetime) compares text.
- `between`: `value` must be `[lo, hi]`; uses `pl.col(c).is_between(lo, hi, closed=...)`. Honours optional `closed` field (`'both'` default, `'left'`, `'right'`, `'none'`); needs a number or a date column.
- Adding new ops requires updating `viz_factory.py:render()` **and** documenting here.
- The `dtype` key from the filter builder is UI-layer metadata — strip it before injecting into `plot_config["filters"]`.

**Auto axis label rule:** `_auto_adjust_axis_labels()` runs at the end of every `render()` unless an `element_text` layer for that axis is already in the data analysis recipe. See `libs/viz_factory/README.md` for thresholds.

## 5. Theme Sovereignty

- **Custom Themes**: The `theme_dashboard` is the authoritative style for the SPARMVET UI.
- **3rd-Party Parity**: Seaborn, 538, and Tufte themes are actively registered components (`theme_seaborn`, `theme_538`, `theme_tufte` in `themes/core.py`). They are fully supported and available to data analysis recipe authors — not deprecated.

## 6. Palette Injection (ADR-081, BP-COLOR-3)

VizFactory supports named palette injection via the `palette:` key in data analysis recipes (BP-COLOR-3).

### 6a. Construction

`VizFactory(palette_registry: dict | None = None)`:
- `_BUILTIN_PALETTES` (class-level) always present — currently `sparmvet_brand`.
- `palette_registry` injected by `app/src/server.py` via `bootloader.get_palettes()`.
- Never reads `config/palettes.yaml` directly — library must remain file-system-independent (ADR-011).

### 6b. Data analysis recipe keys

```yaml
plot_defaults:
  palette: nvi_official      # applies to ALL plots in the data analysis recipe
  # Full plot_defaults schema → rules_data_analysis_recipe_structure.md §10

# Per-plot override (inside analysis_groups plot spec):
palette: sparmvet_brand      # overrides plot_defaults.palette for this plot
```

Resolution order: **plot-level `palette:` > `plot_defaults.palette` > none (matplotlib default)**.

`palette` is one of several `plot_defaults` keys. The authoritative schema (palette, theme, default_font_family, facet_panel_spacing, legend_position, optimisation toggles) is documented at `rules_data_analysis_recipe_structure.md §10`. Unknown keys emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)`.

### 6c. Scale injection rules

`_apply_palette(p, palette_name, mapping_spec, has_fill_scale, has_color_scale)`:

| Condition | Scale injected |
|---|---|
| `palette_name` in `self._palette_registry` | `scale_fill_manual` / `scale_color_manual` with hex list |
| `palette_name` in viridis family (`viridis`, `plasma`, `magma`, `inferno`, `cividis`) | `scale_fill_viridis_d` / `scale_color_viridis_d` |
| Other string | `scale_fill_brewer` / `scale_color_brewer` (plotnine wraps RColorBrewer) |
| `palette_name` unknown to all three | WARNING with list of valid deployment palette names |

**Guard rules (no injection when):**
- Aesthetic (`fill`, `color`) not present in the plot mapping.
- A `scale_fill_*` or `scale_color_*` layer already declared in the data analysis recipe layers list.

## 7. Plot Configuration Cascade (designed 2026-05-10, VIZFAC-PLOT-CASCADE-1)

Plot configuration resolves through a **five-tier priority cascade** at one merge point inside `VizFactory.render()`. The cascade replaces today's three scattered merge sites (`_standardize_config`, `_apply_palette`, `_auto_adjust_axis_labels`) with a single pure function `resolve_plot_config()`.

| Tier | Source | Modifiable by |
|---|---|---|
| **L5** | T3 `aesthetic_override` for the active plot | Analyst (T3 sandbox) |
| **L4** | Plot `spec:` (`analysis_groups.<grp>.plots.<id>.spec`) | Data analysis recipe author |
| **L3** | Optimisation layer (computed from data + spec) — **visual/aesthetic only** | None — emitted by VizFactory |
| **L2** | Data analysis recipe `plot_defaults:` block | Data analysis recipe author |
| **L1** | VizFactory built-in defaults | Developer |

- **Names in the cascade (DECIDED, not built, D-0218)**: the `theme:` key of a plot spec and of `plot_defaults` changes, because it is a component call (D-0214). Names written as values stay plotnine's own (D-0214). It must be tested thoroughly; on an error, investigate and propose solutions (D-0214).

**Resolution rule:** higher tier wins per key (winner-takes-all, no value merging). The `layers:` list is the exception — append-then-deduplicate by `(layer_kind, target)` keeping LAST occurrence (so L5 wins on theme/coord/facet/scale/element_text). `geom_*`/`stat_*` layers never deduplicated.

**Key constraints from the design:**
- L3 (optimisation) is **purely visual/aesthetic** — MUST NOT change `mapping`, `layers`, `geom_*`, `filters`, or `palette`. Allowed: axis text rotation/size, panel spacing, density-aware positions.
- L5 `aesthetic_override` has a **fixed schema** (design §6): `fill_color` ⊕ `fill_palette` (mutex with warning), `color`, `alpha`, `shape`, `size`, `theme`. `plot_scope` MUST be a single plot_id (never `__all__`).
- Unknown keys in `plot_defaults` emit `PipelineError(severity: warning, who: data_analysis_recipe_author, surface: notification)` per ADR-079. Non-fatal.
- §6 above describes today's `_apply_palette` behaviour — under the cascade it remains the renderer for the resolved `palette:` key (now produced by the cascade resolver, not read directly from the data analysis recipe dict). Behaviour rules in §6c are unchanged.

**Full design specification:** [.claude/design/plot_config_cascade.md](../design/plot_config_cascade.md). Implementation tasks: ~~VIZFAC-RESOLVER-1~~ ✓, ~~VIZFAC-DEFAULTS-DOCS-1~~ ✓, ~~VIZFAC-RENDER-WIRE-1~~ ✓, VIZFAC-T3-OVERRIDE-1, VIZFAC-T3-EXPORT-1, VIZFAC-BLUEPRINT-FORM-1.

## 8. Reproducibility and the random seed (ADR-090)

The same data and the same data analysis recipe must give the same picture. Every random component (jitter in all its forms) is seeded:

- `DEFAULT_RANDOM_STATE = 0` in `viz_factory.py` is the default seed.
- A layer sets its own with `random_state` (for example `position_jitter` with `random_state: 123`); a seed set on the layer wins over the factory's.
- `VizFactory(random_state=...)` changes the default for the whole factory. This is the way to fix or vary the seed in tests.
- The seed is handed to plotnine as a numpy generator, never as a bare number: plotnine treats `random_state=0` as "no seed" (it checks `if not random_state`).
- The seed is a default, not a rule: `random_state: null` (or `random`) on a layer, or `VizFactory(random_state=None)`, gives a different arrangement on every render.
- A new random component must be seeded in `_seed_random_components`, and `libs/viz_factory/tests/test_reproducible_render.py` must cover it.
