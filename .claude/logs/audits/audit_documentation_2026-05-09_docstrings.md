Status: PROCESSED 2026-05-09 — DOC-DRIFT-1 + DOC-DRIFT-EMOJI fixed in-session; 4 content-gap tasks created (DOC-GAP-1 through 4)
# Audit Report: Code Docstring Coverage (Tier A/B/C/D + Emoji Ban) — 2026-05-09

## Summary
- Total .py files audited: 84 (libs) + 30 (app)
- Library with worst Tier A coverage: **transformer** (0% — 0/28 files)
- Library with worst Tier B coverage: **transformer** (2% — 2/84 public functions)
- Total Tier C gaps (`@register_action` / `@register_plot_component` without domain docstring): **40 distinct decorators (195 if including all viz_factory components)**
- Tier 0 emoji violations: **7** (active enforcement — must fix)
- **Recommended pre-deployment sprint start: libs/viz_factory/** (largest user-visible gap — 195 registered components, 0% Tier C coverage)

## Coverage Matrix

| Library | Files | Tier A | Tier B | Tier C (`@register_*`) | Tier 0 (emoji) |
|---|---|---|---|---|---|
| **viz_factory** | 17 | 0/17 (0%) | 3/207 (1%) | 0/195 (0%) | 1 |
| **transformer** | 28 | 0/28 (0%) | 2/84 (2%) | 0/64 (0%) | 3 |
| **blueprint_arch** | 8 | 6/8 (75%) | 2/83 (2%) | n/a | 2 |
| **connector** | 11 | 5/11 (45%) | 0/22 (0%) | n/a | 0 |
| **ingestion** | 6 | 0/6 (0%) | 1/11 (9%) | n/a | 1 |
| **test_lab** | 5 | 0/5 (0%) | 1/16 (6%) | n/a | 0 |
| **utils** | 8 | 2/8 (25%) | 1/18 (5%) | n/a | 0 |
| **viz_gallery** | 1 | 0/1 (0%) | 1/4 (25%) | n/a | 0 |

## App Handlers & Modules — Tier D (Reactive Handler Coverage)

| File | `@render.*` | `@reactive` | With docstrings | Coverage |
|---|---|---|---|---|
| audit_stack.py | 6 | 3 | 0 | 0% |
| data_import_handlers.py | 2 | 2 | 0 | 0% |
| export_handlers.py | 2 | 0 | 0 | 0% |
| blueprint_handlers.py | 2 | 12 | 1 | 7% |
| gallery_handlers.py | 5 | 9 | 1 | 7% |
| ingestion_handlers.py | 0 | 1 | 0 | 0% |
| home_theater.py | 20 | 7 | 7 | 25% |
| filter_and_audit_handlers.py | 4 | 7 | 4 | 36% |
| session_handlers.py | 2 | 2 | 1 | 25% |
| **Totals** | 43 | 43 | 14 | **16%** |

## Top Tier C Gaps (highest user-visibility)

`libs/viz_factory/` carries the largest, most user-visible gap — 195 registered components with zero docstrings. Themes, geoms, and scales are referenced directly in user manifests, so this is the highest-impact remediation surface.

### libs/viz_factory/src/viz_factory/themes/core.py — 17 gaps
`theme_gray`, `theme_bw`, `theme_linedraw`, `theme_light`, `theme_minimal`, `theme_classic`, `theme_void`, `theme_dark`, `theme_538`, `theme_matplotlib`, `theme_seaborn`, `theme_tufte`, `theme_xkcd`, `theme_dashboard`, `theme_publication`, `theme_legend_position`, `theme_custom`

### libs/viz_factory/src/viz_factory/geoms/core.py — 21 gaps
`stat_count`, `stat_bin`, `stat_identity`, `stat_summary`, `stat_boxplot`, `stat_ydensity`, `stat_smooth`, `stat_density`, `stat_qq`, `stat_ecdf`, `stat_unique`, `stat_bin_2d`, `stat_bindot`, `stat_density_2d`, `stat_ellipse`, `stat_hull`, `stat_qq_line`, `stat_quantile`, `stat_sina`, `stat_sum`, `stat_summary_bin`

### libs/viz_factory/src/viz_factory/scales/core.py — 2 gaps
`scale_x_continuous`, `scale_y_continuous`

(Other components in `libs/viz_factory/` make up the remainder of the 195 — geoms, coords, position adjustments — see source files for the full list.)

### libs/transformer/ — 64 `@register_action` decorators with no docstrings
All registered actions documented in `rules_persona_bioscientist.md §8` need Tier C domain docstrings. Highest priority because manifests reference these by name.

## Tier 0 Emoji Violations (ACTIVE enforcement — must fix)

7 violations in source code (forbidden by `rules_code_quality.md §1`):

| File | Line | Emoji | Context |
|---|---|---|---|
| libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py | 239 | ℹ️ | f-string |
| libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py | 456 | ⚠ | f-string |
| libs/ingestion/src/ingestion/ingestor.py | 102 | ⚠️ | exception message |
| libs/transformer/src/transformer/actions/persistence/anchor.py | 33 | 💾 | f-string comment |
| libs/transformer/src/transformer/data_assembler.py | 132 | ⚠️ | warning message |
| libs/transformer/src/transformer/data_assembler.py | 165 | ⚠️ | warning message |
| libs/viz_factory/src/viz_factory/viz_factory.py | 171 | ⚠️ | warning message |

**Action:** Replace with plain text — `ℹ️` → `INFO`, `⚠️` → `WARNING`, `💾` → `Materializing` (or similar plain string). These are blocking under §1 and should be fixed before further documentation work begins.

## Recommended Pre-Deployment Sprint Order (worst → best)

1. **libs/viz_factory/** — START HERE
   - 17 files, ~99% coverage gap
   - 195 registered components with 0% Tier C coverage
   - Highest user-visibility (themes/geoms/scales appear in manifests)
   - 1 emoji violation
2. **libs/transformer/** — second priority
   - 28 files, 98% gap
   - 64 `@register_action` with 0% Tier C
   - 3 emoji violations + 0% Tier A module headers
   - Heavy scientist usage
3. **libs/blueprint_arch/** — third
   - 8 files, 25% Tier A gap remaining (best of the unfinished libs)
   - 2 emoji violations in the mapper module
4. **libs/connector/** — fourth
   - 11 files, 45% Tier A, 0% Tier B
5. **libs/ingestion / test_lab / utils / viz_gallery** — lower priority
   - Smaller surfaces, fewer registered components
6. **app/handlers/** — Tier D pass after libraries
   - 16% Tier D coverage overall
   - Lower priority than Tier C in libs (handlers are internal, registered actions are user-facing)

## Critical Insights

- **Why viz_factory is the recommended start:** 195 registered plot components with zero domain docstrings, all directly referenced in user-authored manifests. Establishing the Tier C pattern here will set the template for transformer.
- **Tier 0 emoji violations are blocking:** All 7 are in non-`print()` contexts (decorators, exception/warning messages, comments) — explicitly forbidden by §1. Fix before sprint work begins.
- **App handlers Tier D can wait:** Internal-facing; lower information value than Tier C library docs. Recommend handler pass after viz_factory + transformer.
