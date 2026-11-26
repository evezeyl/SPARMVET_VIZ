# Which plot components are, or would be, `modif_` (asked in channel M267; rule D-0254)

Digest by the coordinator of a scout's report, 2026-11-18. The scout read the code; it ran nothing.
Where a line says "earlier run", the evidence is a run recorded in the earlier reports of this folder, not a new run.
Nothing is built. Nothing is decided here.

## Counts (191 registered components)

| Class | Count | What it means |
|---|---|---|
| Exact | 122 | The code hands the recipe's arguments straight to the plotnine object of the same name. |
| Only other argument values | 3 sure, 8 doubtful | Same plotnine object, other values or a shortcut name. Under D-0254 these go out. |
| Does more | 51 | Changes something that is not an argument value. These stay. |
| Own or composite, no single plotnine object | 7 | Candidates for `step_`. One is broken (`guide_label`). |

## Goes out for sure (3). No shipped recipe and no gallery bundle uses them.

| Component | Is in fact | The recipe would write | Files that change |
|---|---|---|---|
| `coord_lims` (`coords/core.py:117-138`) | `coord_cartesian` with xlim, ylim | `coord_cartesian` with `xlim`, `ylim` | 1 test recipe |
| `theme_dashboard` (`themes/core.py:253-270`) | `theme_bw` with base size 14 | `theme_bw` with `base_size: 14` | 1 test recipe; Blueprint choice list `blueprint_handlers.py:1817` |
| `theme_publication` (`themes/core.py:273-290`) | `theme_classic`, same default size | `theme_classic` | 1 test recipe |

Note: D-0256 point 4 says "Dashboard" and "Publication" stay as code with corrected descriptions. D-0254 (later the same morning) says a component that only changes argument values goes out. These two decisions meet here: see question 1.
Two wrong descriptions found: `coord_lims` says it drops data (it does not); `theme_dashboard` says it is the default theme.

## Doubtful (8): they only RENAME an argument or fix one value

| Component | Is in fact | The recipe would write | Shipped use |
|---|---|---|---|
| `scale_color_viridis_c`, `scale_fill_viridis_c` | `scale_color_cmap` / `scale_fill_cmap`; argument `option` is plotnine's `cmap_name` | `scale_color_cmap` with `cmap_name: viridis` | none (test recipes) |
| `scale_color_viridis_d`, `scale_fill_viridis_d` | `scale_color_cmap_d` / `scale_fill_cmap_d` | same with `cmap_name` | none (test recipes) |
| `theme_legend_position` | `theme(legend_position=...)`; plotnine's `theme` is not a registered component | `theme_custom` with `legend_position` | 1 shipped plot: `1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:22-24` |
| `guide_none` | `guides(<aesthetic>=False)` | `guides` with the value none | none (test recipe) |
| `facet_rows`, `facet_cols` | `facet_grid(rows=...)` / `facet_grid(cols=...)` | `facet_grid` with `rows` or `cols` | none (test recipes) |

## Stays, with the reason (51)

- 8 positions: they attach themselves to the last layer (`positions/core.py:24`).
- `facet_grid`, `facet_wrap`: they convert a formula or names (`facets/core.py:105-116`, `registry.py:87-97`). `facet_wrap` is declared exact today but is not.
- 4 facet setters (`facet_scales`, `facet_space`, `facet_labeller`, `facet_margins`): they change the facet written before them.
- 13 named themes: extra keys are passed on to `theme()` (`themes/core.py:21-36`).
- 4 element components, `xlab`, `ylab`, `ggtitle`, `annotate`: a target key, key checks, a key moved to another place.
- 4 guides: text turned into a guide object; a `mapping` key of ours.
- `scale_x_continuous`, `scale_y_continuous`: `breaks_integer` computes breaks.
- `scale_alpha`, `scale_size`, `scale_size_area`, `scale_color_hue`, `scale_fill_hue`: a list is turned into a pair (`scales/core.py:1218-1229`). See question 5.
- `geom_jitter`, `geom_sina`, `stat_sina`: only the random seed, which the factory gives to every random layer. See question 4.
- `stat_function`: text turned into a function. `stat_identity`: does nothing at all. See question 6.

## Own or composite (7)

`theme_custom`; `guide_nrow`, `guide_ncol`, `guide_title`, `guide_direction`, `guide_reverse` (each builds a legend guide with one argument); `guide_label` (always fails; already an open question).

## Nothing answers this (for Eve), in plain words

1. Two decisions of this morning meet: "Dashboard and Publication stay as code" (D-0256) and "only other argument values goes out" (D-0254). `theme_dashboard` is `theme_bw` with size 14 and `theme_publication` is `theme_classic`. Do they (a) go out, and a recipe writes `theme_bw` with `base_size: 14`, or (b) stay as named looks of the app, as an exception she names? Default: (a), since no shipped recipe uses them.
2. Does giving an argument another NAME count as "only other argument values"? It concerns the four viridis scales, `facet_rows`, `facet_cols`, `theme_legend_position`. (a) Yes, they go out and recipes use plotnine's own names. (b) No, they stay. Default: (a); one shipped plot file changes.
3. `guide_none` (hide one legend): (a) goes out, the recipe writes `guides` with none; (b) stays. Default: (a).
4. The random seed is given by the app to every random layer. Is the seed alone a reason to call `geom_jitter`, `geom_sina`, `stat_sina` modified? (a) No: they are exact, the recipe writes the seed (the shipped recipes already do). (b) Yes. Default: (a).
5. Five scales only turn a list `[4, 20]` into the pair plotnine wants. (a) Do this for every component in one place; the five become exact. (b) Keep it in the five; they stay modified. Default: (a).
6. `stat_identity` as a layer does nothing. (a) Remove it as a layer (the value `stat: stat_identity` inside a geom stays). (b) Keep. Default: (a).
7. The five legend shortcuts (`guide_nrow`, `guide_ncol`, `guide_title`, `guide_direction`, `guide_reverse`): (a) go out, the recipe writes `guide_legend` with the argument; (b) stay as `step_` composites. Default: (a), fewer names; none is used by a shipped recipe (to verify before removal).
8. `theme_custom` has no plotnine object of that name. Its new name: (a) `step_theme_custom`, (b) `modif_theme`. Default: (b) `modif_theme`, because it is plotnine's `theme` with our way of writing elements.
9. `facet_wrap`: (a) `modif_facet_wrap` because of its own conversion, with the exact one beside it; (b) make the conversion general and keep it exact. Default: (a).
10. An earlier line (D-0211, wording of the review session) says the list of kept modifications is shown to her BEFORE anything is removed. This file is that list. Does she want to say yes to it before the removal is built? Default: yes, nothing is removed before her yes.

## For the records (not questions)

- `rules_viz_factory.md:26` still says `modif_` covers "other argument defaults". D-0254 changed that. Rule text is Eve's to release.
- The "15 objects" of question 5 are the 8 positions, 4 elements and 3 guides. A value form exists today only in `theme_custom` (elements) and in the guides block (`viz_factory.py:381-399`).
- The resolver reads name prefixes (`plot_config_resolver.py:120-162`); the rename to `plotnine_` / `modif_` changes these keys.
- Plotnine's own default values were not re-run today.
