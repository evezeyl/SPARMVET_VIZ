Status: PROCESSED
# Audit Report: Parity Mandate Coverage
Generated: 2026-05-21T16:09:57
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: ADR-035 (Polars Parity Mandate), ADR-036 (Artist Parity Mandate)

- Plotnine 0.15.4: 222 symbols, 168 registered (75% coverage), 54 gap
- Stale registrations: 0 unresolved, 20 accepted (in audit_exclusions.yaml), 5 custom (SPARMVET-specific)
- Polars 1.40.1: 63 registered actions, 416 total Expr methods across 9 namespaces

## Plotnine Parity (ADR-036)

### ℹ️ Accepted Stale Registrations (in audit_exclusions.yaml — no action needed)

- `annotate` — review when: Check plotnine changelog — confirm it is gone or find the new name.
- `coord_lims` — review when: Upgrade plotnine and confirm status.
- `facet_cols` — review when: Upgrade plotnine and re-check what's exported.
- `facet_labeller` — review when: Same as facet_cols.
- `facet_margins` — review when: Same as facet_cols.
- `facet_rows` — review when: Same as facet_cols.
- `facet_scales` — review when: Same as facet_cols.
- `facet_space` — review when: Same as facet_cols.
- `guide_direction` — review when: Upgrade plotnine and check guide API.
- `guide_label` — review when: Upgrade plotnine and check guide API.
- `guide_ncol` — review when: Upgrade plotnine and check guide API.
- `guide_none` — review when: Upgrade plotnine and re-check.
- `guide_nrow` — review when: Upgrade plotnine and check guide API.
- `guide_reverse` — review when: Upgrade plotnine and check guide API.
- `guide_title` — review when: Upgrade plotnine and check guide API.
- `guides` — review when: Re-run with a newer plotnine; update PLOTNINE_SINGLES in the script if needed.
- `scale_color_viridis_c` — review when: Remove after confirming no manifests use the old name.
- `scale_color_viridis_d` — review when: Remove after confirming no manifests use the old name.
- `scale_fill_viridis_c` — review when: Remove after confirming no manifests use the old name.
- `scale_fill_viridis_d` — review when: Remove after confirming no manifests use the old name.

### 🔴 Coverage Gap — 54 unregistered plotnine symbols

These exist in the installed plotnine but have no `@register_plot_component` entry.
Each missing symbol is a potential feature the VizFactory cannot express in a manifest.

**geom** (1 missing):
  `geom_bin2d`

**stat** (2 missing):
  `stat_bin2d`, `stat_pointdensity`

**scale** (33 missing):
  `scale_alpha_datetime`, `scale_alpha_ordinal`, `scale_color_datetime`, `scale_color_desaturate`, `scale_color_gray`, `scale_color_grey`, `scale_color_ordinal`, `scale_colour_brewer`, `scale_colour_cmap`, `scale_colour_cmap_d`, `scale_colour_continuous`, `scale_colour_datetime`, `scale_colour_desaturate`, `scale_colour_discrete`, `scale_colour_distiller`, `scale_colour_gradient`, `scale_colour_gradient2`, `scale_colour_gradientn`, `scale_colour_gray`, `scale_colour_grey`, `scale_colour_hue`, `scale_colour_identity`, `scale_colour_manual`, `scale_colour_ordinal`, `scale_fill_datetime`, `scale_fill_desaturate`, `scale_fill_gray`, `scale_fill_grey`, `scale_fill_ordinal`, `scale_size_datetime`, `scale_size_ordinal`, `scale_size_radius`, `scale_stroke`

**theme** (4 missing):
  `theme_get`, `theme_grey`, `theme_set`, `theme_update`

**annotation** (2 missing):
  `annotation_logticks`, `annotation_stripes`

**other** (13 missing):
  `aes`, `after_scale`, `after_stat`, `arrow`, `ggplot`, `lims`, `qplot`, `stage`, `theme`, `watermark`, `xlim`, `ylim`, `ylim`

**Action:** For each gap, decide whether to register the component or explicitly
mark it as out-of-scope in this file's `SCOPE_EXCLUSIONS` set.
See `rules_viz_factory.md §1` and `viz_factory_implementation.md`.

## Polars Expression Coverage (ADR-035)

Coverage is measured by loose heuristic match (action name ↔ method name substring).
Low-coverage namespaces indicate where new transformer actions may be valuable.

| Namespace | Covered | Total | Coverage |
|-----------|---------|-------|----------|
| `__expr__` | 44 | 208 | 🔴 21% |
| `arr` | 14 | 31 | ⚠️ 45% |
| `cat` | 1 | 6 | 🔴 16% |
| `dt` | 5 | 47 | 🔴 10% |
| `list` | 16 | 43 | ⚠️ 37% |
| `meta` | 2 | 17 | 🔴 11% |
| `name` | 2 | 10 | 🔴 20% |
| `str` | 6 | 49 | 🔴 12% |
| `struct` | 2 | 5 | ⚠️ 40% |

### 🔴 Low-Coverage Namespaces (< 30%)

**`pl.Expr.__expr__.*`** — 44/208 covered. Sample uncovered: `abs`, `agg_groups`, `alias`, `append`, `arccos`, `arccosh`, `arcsin`, `arcsinh`, `arctan`, `arctanh`
**`pl.Expr.cat.*`** — 1/6 covered. Sample uncovered: `ends_with`, `get_categories`, `len_bytes`, `len_chars`, `starts_with`
**`pl.Expr.dt.*`** — 5/47 covered. Sample uncovered: `add_business_days`, `base_utc_offset`, `century`, `combine`, `convert_time_zone`, `datetime`, `day`, `days_in_month`, `dst_offset`, `epoch`
**`pl.Expr.meta.*`** — 2/17 covered. Sample uncovered: `as_expression`, `as_selector`, `has_multiple_outputs`, `is_column`, `is_column_selection`, `is_literal`, `is_regex_projection`, `output_name`, `pop`, `root_names`
**`pl.Expr.name.*`** — 2/10 covered. Sample uncovered: `map`, `map_fields`, `prefix`, `prefix_fields`, `suffix`, `suffix_fields`, `to_lowercase`, `to_uppercase`
**`pl.Expr.str.*`** — 6/49 covered. Sample uncovered: `concat`, `contains`, `contains_any`, `count_matches`, `decode`, `encode`, `ends_with`, `escape_regex`, `extract_all`, `extract_groups`

**Action:** Low-coverage namespaces indicate where new `@register_action` decorators
would provide the most value. Consult `rules_data_engine.md §5` (Polars Parity Mandate).

## Registered Inventory

### Transformer Actions (63 registered)

`action_name`, `add_constant`, `all_horizontal`, `any_horizontal`, `cast`, `coalesce`, `count_by_group`, `cum_count`, `cum_sum`, `date_extract`, `date_truncate`, `derive_categories`, `describe_stats`, `divide_columns`, `drop_columns`, `drop_duplicates`, `drop_nulls`, `explode`, `fill_nulls`, `fill_nulls_direction`, `filter_eq`, `filter_range`, `horizontal_stats`, `interpolate`, `is_in`, `join`, `join_filter`, `keep_columns`, `label_if`, `list_join`, `list_slice`, `mutate`, `null_if`, `percentile`, `pivot`, `recode_values`, `regex_extract`, `regex_replace`, `rename`, `rename_columns`, `replace_values`, `round_numeric`, `sample`, `sanitize_column_names`, `scan_parquet`, `select_by_pattern`, `shift`, `sink_parquet`, `sort`, `split_and_explode`, `split_column`, `split_column_to_parts`, `split_to_list`, `strip_whitespace`, `summarize`, `to_struct`, `unique`, `unique_rows`, `unnest`, `unpivot`, `value_counts`, `window_agg`, `z_score`

### VizFactory Components (193 registered)

`annotate`, `coord_cartesian`, `coord_equal`, `coord_fixed`, `coord_flip`, `coord_lims`, `coord_trans`, `element_blank`, `element_line`, `element_rect`, `element_text`, `facet_cols`, `facet_grid`, `facet_labeller`, `facet_margins`, `facet_null`, `facet_rows`, `facet_scales`, `facet_space`, `facet_wrap`, `geom_abline`, `geom_area`, `geom_bar`, `geom_bin_2d`, `geom_blank`, `geom_boxplot`, `geom_col`, `geom_count`, `geom_crossbar`, `geom_density`, `geom_density_2d`, `geom_dotplot`, `geom_errorbar`, `geom_errorbarh`, `geom_freqpoly`, `geom_histogram`, `geom_hline`, `geom_jitter`, `geom_label`, `geom_line`, `geom_linerange`, `geom_map`, `geom_path`, `geom_point`, `geom_pointdensity`, `geom_pointrange`, `geom_polygon`, `geom_qq`, `geom_qq_line`, `geom_quantile`, `geom_raster`, `geom_rect`, `geom_ribbon`, `geom_rug`, `geom_segment`, `geom_sina`, `geom_smooth`, `geom_spoke`, `geom_step`, `geom_text`, `geom_tile`, `geom_violin`, `geom_vline`, `ggtitle`, `guide_colorbar`, `guide_colourbar`, `guide_direction`, `guide_label`, `guide_legend`, `guide_ncol`, `guide_none`, `guide_nrow`, `guide_reverse`, `guide_title`, `guides`, `labs`, `name`, `position_dodge`, `position_dodge2`, `position_fill`, `position_identity`, `position_jitter`, `position_jitterdodge`, `position_nudge`, `position_stack`, `scale_alpha`, `scale_alpha_continuous`, `scale_alpha_discrete`, `scale_alpha_identity`, `scale_alpha_manual`, `scale_color_brewer`, `scale_color_cmap`, `scale_color_cmap_d`, `scale_color_continuous`, `scale_color_discrete`, `scale_color_distiller`, `scale_color_gradient`, `scale_color_gradient2`, `scale_color_gradientn`, `scale_color_hue`, `scale_color_identity`, `scale_color_manual`, `scale_color_viridis_c`, `scale_color_viridis_d`, `scale_fill_brewer`, `scale_fill_cmap`, `scale_fill_cmap_d`, `scale_fill_continuous`, `scale_fill_discrete`, `scale_fill_distiller`, `scale_fill_gradient`, `scale_fill_gradient2`, `scale_fill_gradientn`, `scale_fill_hue`, `scale_fill_identity`, `scale_fill_manual`, `scale_fill_viridis_c`, `scale_fill_viridis_d`, `scale_linetype`, `scale_linetype_discrete`, `scale_linetype_identity`, `scale_linetype_manual`, `scale_shape`, `scale_shape_discrete`, `scale_shape_identity`, `scale_shape_manual`, `scale_size`, `scale_size_area`, `scale_size_continuous`, `scale_size_discrete`, `scale_size_identity`, `scale_size_manual`, `scale_stroke_continuous`, `scale_stroke_identity`, `scale_x_continuous`, `scale_x_date`, `scale_x_datetime`, `scale_x_discrete`, `scale_x_log10`, `scale_x_reverse`, `scale_x_sqrt`, `scale_x_symlog`, `scale_x_timedelta`, `scale_y_continuous`, `scale_y_date`, `scale_y_datetime`, `scale_y_discrete`, `scale_y_log10`, `scale_y_reverse`, `scale_y_sqrt`, `scale_y_symlog`, `scale_y_timedelta`, `stat_bin`, `stat_bin_2d`, `stat_bindot`, `stat_boxplot`, `stat_count`, `stat_density`, `stat_density_2d`, `stat_ecdf`, `stat_ellipse`, `stat_function`, `stat_hull`, `stat_identity`, `stat_qq`, `stat_qq_line`, `stat_quantile`, `stat_sina`, `stat_smooth`, `stat_sum`, `stat_summary`, `stat_summary_bin`, `stat_unique`, `stat_ydensity`, `theme_538`, `theme_bw`, `theme_classic`, `theme_custom`, `theme_dark`, `theme_dashboard`, `theme_gray`, `theme_legend_position`, `theme_light`, `theme_linedraw`, `theme_matplotlib`, `theme_minimal`, `theme_publication`, `theme_seaborn`, `theme_tufte`, `theme_void`, `theme_xkcd`, `xlab`, `ylab`

## References
- `rules_data_engine.md §5` — Polars Parity Mandate (ADR-035)
- `rules_viz_factory.md §1` — Artist Parity Mandate (ADR-036)
- `libs/transformer/src/transformer/actions/` — action registry source
- `libs/viz_factory/src/viz_factory/` — component registry source
- Routine 12 (Parity mandate coverage) in `.claude/workflows/audit_routine_registry.md`