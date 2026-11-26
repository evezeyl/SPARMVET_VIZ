REPORT: are the 22 `own` plot components real plotnine steps? (check only, nothing renamed, no repository file edited)

Setup. plotnine 0.15.4 (run). Branch dev, commit bf4b169e. Scratch scripts: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/viz_rename/cmp.py and cmp2.py.

How I compared. I reused `snapshot` and `picture` from `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py`. `snapshot` compares the structure of the plot. `picture` compares the rendered PNG. I ran the component through the registry and the direct plotnine call on the audit's 30-row table.

Words used below:
- "equal" = same snapshot and same picture.
- "verified (run)" = I ran it.
- "verified (read)" = I read it in the code.
- "reasoned" = deduced, not run.

## Answer in short
- None of the 22 is REAL in Eve's sense (one plotnine object, nothing added, fixed or changed). Each of the other 21 does something more than a bare pass-through.
- Under her rule I get 14 MODIFIED, 5 COMPOSITE, 1 BROKEN and 2 that the rule does not decide. The details are in the table and the open points.
- 10 of the 22 can be said exactly as a call of one registered plotnine component (verified, run). Each of these 10 is equal to the registered component given the same parameters:
  - facet_rows, facet_cols, coord_lims
  - guide_title, guide_nrow, guide_none (same as the registered `guide_legend` / `guides`)
  - theme_legend_position (same as `theme_custom`)
  - theme_dashboard (same as registered `theme_bw` with `base_size` 14)
  - the viridis scales (same as the registered `cmap` scale)
  - guide_ncol, guide_reverse and guide_direction behave the same way; I ran those against direct plotnine only.
- Usage: only `theme_legend_position` is named by a shipped recipe (1 file). The other 21 are used by none (verified, run: grep).

## Table (22 rows)

Columns: our name | class | real plotnine name | proposed name | what differs from the direct call | already registered? | shipped recipes | evidence

Shipped-recipe count: 0 for every row except `theme_legend_position` (1 file).

1. `facet_rows` | MODIFIED | `facet_grid` | `modif_facet_grid` | The variable is written `facets`, not `rows`, and fixed to the rows side. Only `facets` and `scales` are offered; `facet_grid` also has `space`, `margins`, `cols`, ... (verified, read: facets/core.py:122-143). | Registered `facet_grid` is `modified`, so it would also become `modif_facet_grid`: COLLISION (point 1). `facet_grid` plus `facet_rows` give an equal plot (verified, run). | 0 | Code line: `p + _built("facet_grid", lambda: facet_grid(rows=facet_variables(row_var, _columns(p)), **spec))`. Run: equal to `facet_grid(rows=["g"])`, `facet_grid(rows="g")` and `facet_grid("g ~ .")`, also with `scales=free_y`.
2. `facet_cols` | MODIFIED | `facet_grid` | `modif_facet_grid` | Same as 1, with the cols side. | Same collision. | 0 | facets/core.py:146-168. Run: equal to `facet_grid(cols=["g"])` and `facet_grid(". ~ g")`.
3. `coord_lims` | MODIFIED by the letter of the rule (restricted parameters). On behaviour it is a pure duplicate of `coord_cartesian` | `coord_cartesian` | `modif_coord_cartesian` | It offers only `xlim` and `ylim`. Registered `coord_cartesian` also offers `expand` (verified, run: params list). It passes `coord_cartesian(**spec)` unchanged. | `coord_cartesian` is registered as `exact` (so `plotnine_coord_cartesian`). A `modif_` next to its exact twin would break `test_no_exact_plotnine_object_is_registered_next_to_a_modified_one_today` as that test is written (reasoned). Open point. | 0 | coords/core.py:117-142, line `return p + coord_cartesian(**spec)`. Run: equal to the direct call and to the registered `coord_cartesian`.
4. `guide_title` | COMPOSITE | `guides` plus `guide_legend` | `step_guide_title` | Builds `guides(<mapping>=guide_legend(title=...))`. `mapping` is a required parameter, and `value` is read as an alias of `title`. | The registered `guide_legend` does the same two-object call: equal (verified, run). Same single-setting call as `guide_nrow`, so the 5 setters overlap one another. | 0 | guides/core.py:237-263. Run: equal to `guides(color=guide_legend(title="T"))`.
5. `guide_ncol` | COMPOSITE | `guides` plus `guide_legend` | `step_guide_ncol` | As 4, with `ncol`. | As 4. | 0 | guides/core.py:206. Run: equal to `guides(color=guide_legend(ncol=2))`.
6. `guide_nrow` | COMPOSITE | `guides` plus `guide_legend` | `step_guide_nrow` | As 4, with `nrow`. | As 4; equal to the registered `guide_legend` with `nrow` (verified, run). | 0 | guides/core.py:175. Run: equal to the direct call.
7. `guide_reverse` | COMPOSITE | `guides` plus `guide_legend` | `step_guide_reverse` | As 4, with `reverse`, and it sets a default: reverse is TRUE when absent. `guide_legend()` reverses nothing. | As 4. | 0 | guides/core.py:319-336. Run: with no `reverse` it is equal to `guide_legend(reverse=True)`. It is NOT equal to `guide_legend()`; the pictures differ (verified, run).
8. `guide_direction` | COMPOSITE | `guides` plus `guide_legend` | `step_guide_direction` | As 4, with `direction`, and it sets a default: horizontal when absent. | As 4. | 0 | guides/core.py:293-316. Run: with no `direction` it is equal to `guide_legend(direction="horizontal")`.
9. `guide_none` | MODIFIED | `guides` | `modif_guides` | `guides(<mapping>=False)` with `mapping` required; the registered `guides` writes the same as `color: none`. | Registered `guides` (modified) would also be `modif_guides`: COLLISION (point 1). Equal to the registered `guides` with `color: none` (verified, run). | 0 | guides/core.py:149. Run: equal to `guides(color=False)`.
10. `guide_label` | BROKEN | none | no new name (it cannot act) | Always raises. | none | 0 | See "Broken" below.
11. `theme_legend_position` | MODIFIED | `theme` | `modif_theme` | `theme(legend_position=position)`, with `position` default `right` when absent. | `theme` is not registered (listed in KNOWN_MISSING). No `plotnine_theme` exists. COLLISION with `theme_custom` (point 1). Equal to `theme_custom` with `legend_position` (verified, run). | 1 (config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml) | themes/core.py:291. Run: equal to `theme(legend_position=...)` for `bottom`, `none` and the default `right`.
12. `theme_custom` | MODIFIED (arguable COMPOSITE) | `theme` | `modif_theme` | `theme(**params)`, but a value written `{name: element_text, params:{...}}` is turned into an `element_*` object. Unknown element names are dropped silently (defect 1 below). | As 11: COLLISION. | 0 | themes/core.py:311-340. Run: equal to `theme(axis_text_x=element_text(angle=45,hjust=1))` and to `theme(legend_position="top")`. It builds `element_*` plus `theme`, which is more than one plotnine object. Whether that makes it COMPOSITE (`step_`) is open (point 2).
13. `scale_color_viridis_c` | MODIFIED | `scale_color_cmap` | `modif_scale_color_cmap` | Parameter `option` is renamed to `cmap_name` (default viridis). The form lists only `option`, `direction`, `name`, `guide`, `begin`, `end` (verified, read). `direction`, `begin` and `end` fail, and `guide: none` fails (defect 2 below). | `scale_color_cmap` is registered as `exact` (`plotnine_scale_color_cmap`), and plotnine has no viridis scale (verified, run). It is the same `modified`-beside-`exact` situation as row 3. | 0 | scales/core.py:343. Run: equal to `scale_color_cmap(cmap_name="viridis")`, to `scale_color_cmap()` with no argument, and to `option: magma` against `cmap_name="magma"`.
14. `scale_fill_viridis_c` | MODIFIED | `scale_fill_cmap` | `modif_scale_fill_cmap` | As 13. | As 13 (`plotnine_scale_fill_cmap` exists). | 0 | scales/core.py:364. Same runs.
15. `scale_color_viridis_d` | MODIFIED | `scale_color_cmap_d` | `modif_scale_color_cmap_d` | As 13, but there is no `begin` or `end`. | As 13. | 0 | scales/core.py:309. Same runs; `direction` fails.
16. `scale_fill_viridis_d` | MODIFIED | `scale_fill_cmap_d` | `modif_scale_fill_cmap_d` | As 15. | As 13. | 0 | scales/core.py:326. Same runs.
17. `theme_dashboard` | MODIFIED | `theme_bw` | `modif_theme_bw` | A default is set: `base_size` 14, where plotnine's `theme_bw` uses 11. Extra keys are added as `theme()` settings, like the registered `theme_bw`. | Registered `theme_bw` is `modified`, so it becomes `modif_theme_bw`: COLLISION (point 1). Equal to the registered `theme_bw` with `base_size: 14` (verified, run). | 0 | themes/core.py:251-268, line `spec.setdefault("base_size", 14)`. Run: equal to `theme_bw(base_size=14)` (also with `base_size` 9). It is NOT equal to `theme_bw()`: snapshot and picture differ.
18. `theme_publication` | MODIFIED | `theme_classic` | `modif_theme_classic` | Default `base_size` 11. Run: equal to `theme_classic()` too, so here the difference is invisible, because plotnine's own default is also 11. | Registered `theme_classic` is `modified`: COLLISION. | 0 | themes/core.py:271-288. Run: equal to `theme_classic(base_size=11)` and to `theme_classic()`.
19. `facet_scales` | MODIFIED (setter); the real name is UNCLEAR | `facet_wrap` or `facet_grid`, whichever is already on the plot | `modif_facet_wrap` or `modif_facet_grid`; cannot be one name (point 3) | It does not call a plotnine object. It copies the plot's facet, sets `facet.free = {...}` on the copy, and re-adds it (facets/core.py:191-213). A facet must come before it. | Registered `facet_wrap` becomes `plotnine_facet_wrap`; `facet_grid` becomes `modif_facet_grid`. | 0 | Run: equal to `facet_wrap("g", scales="free_y")` and `facet_wrap("g", scales="free")`; on `facet_grid` equal to `facet_grid(..., scales="free_y")`, and it keeps the other facet settings. Written without a facet before it, it is refused with a message (verified, read: `_facet_before`).
20. `facet_space` | MODIFIED (setter); name `facet_grid` | `facet_grid` | `modif_facet_grid` | Sets the `space` of the facet already on the plot; a `facet_wrap` there is refused. | COLLISION with `facet_grid`, `facet_rows`, `facet_cols`, `facet_margins`. | 0 | facets/core.py:216. Run: equal to `facet_grid(..., scales="free_x", space="free_x")`.
21. `facet_labeller` | MODIFIED (setter); name UNCLEAR | `facet_wrap` or `facet_grid` | as 19 | Only `label_value`, `label_both`, `label_context` are accepted. It sets `facet.labeller = as_labeller(...)` on the copy. | As 19. | 0 | facets/core.py:241. Run: equal on a wrap and on a grid.
22. `facet_margins` | MODIFIED (setter); name `facet_grid` | `facet_grid` | `modif_facet_grid` | Sets `margins` on the facet already on the plot. Default when absent is TRUE; plotnine's default is False. | COLLISION as 20. | 0 | facets/core.py:266. Run: equal to `facet_grid(..., margins=True)`, also with no `margins` given.

Counts of the proposed names (my reading of Eve's rule, mixed with open points): 14 `modif_`, 5 `step_` (the guide setters), 1 broken, 2 undecided (the two facet setters whose real name is unclear). `theme_custom` is counted in the 14 but is arguable (point 2).

## Collisions (open for Eve; I resolved none)

1. Several of our names would become the same `modif_` name:
   - `modif_facet_grid`: registered `facet_grid`, plus `facet_rows`, `facet_cols`, `facet_space`, `facet_margins`, and `facet_scales` / `facet_labeller` when they act on a grid.
   - `modif_facet_wrap`: `facet_scales` and `facet_labeller`, if they are named after the wrap. The registered `facet_wrap` is exact, so it becomes `plotnine_facet_wrap`.
   - `modif_guides`: registered `guides`, plus `guide_none`.
   - `modif_guide_legend`: only if the 5 guide setters (rows 4-8) are called MODIFIED instead of COMPOSITE. The registered `guide_legend` becomes `modif_guide_legend` too.
   - `modif_theme`: `theme_legend_position` and `theme_custom`.
   - `modif_theme_bw`: registered `theme_bw` and `theme_dashboard`.
   - `modif_theme_classic`: registered `theme_classic` and `theme_publication`.
   - The 4 viridis scales and `coord_lims` do not collide. But they would sit next to the `plotnine_` twin, which the audit test forbids today (see 3 and 13-16).
2. COMPOSITE or MODIFIED is not decided by the rule for two groups:
   - The 5 guide setters build `guides(...)` and `guide_legend(...)`: two plotnine objects, so COMPOSITE (`step_`) by the written rule. The registered `guide_legend` makes the same two-object call and is classed "modified" by the project. The two are not treated the same.
   - `theme_custom` builds `element_*` objects and `theme`. Is that COMPOSITE (`step_theme_custom`) or MODIFIED?
3. The two setters `facet_scales` and `facet_labeller` act on whichever facet is on the plot, so no single real name fits.
4. `coord_lims` and the 4 viridis scales are "modified" only by a renamed or restricted parameter. They sit next to an exact twin. The options are:
   - keep both, which breaks the audit test as written (`test_no_exact_plotnine_object_is_registered_next_to_a_modified_one_today`);
   - drop the duplicate (this is also Q8(b) of the impact document);
   - give the twin another class.

## BROKEN

- `guide_label` (verified, run). Message through the component: `CannotAct: guide_label cannot work: it passes labels to plotnine's guide_legend, which has no such argument. Fix: set the label text with labels on the scale ... guide_label waits for a decision.` The direct call fails too: `TypeError: guide_legend.__init__() got an unexpected keyword argument 'labels'`. The failure is the same on every use (matches code at guides/core.py:266-290: it only raises).

## New defects found while running (all verified, run; none is in impact document section 5 D1-D5)

1. `theme_custom` drops an unknown element name silently. `{name: element_foo}` leaves the theme equal to no change at all, and no message appears. This is against D-0050 ("No silent error that is the rule."). It only handles the four names `element_text`, `element_line`, `element_rect`, `element_blank` (themes/core.py:311-340, an `if/elif` chain with no else).
2. The 4 viridis scales offer parameters that fail:
   - `direction` (all 4): `TypeError: scale_color_cmap.__init__() got an unexpected keyword argument 'direction'`. The `_d` ones say `scale_color_cmap_d...`.
   - `begin` and `end` (the two `_c` scales): same TypeError.
   - `guide: none` (all 4): `PlotnineError: 'guide_none' Not in Registry`. `legend` and `colorbar` work.
   The form shows all of these (`_VIRIDIS_PARAMS`, scales/core.py:72-81).
3. The guide setters do not combine. `guide_nrow` followed by `guide_title` on the same aesthetic leaves a guide with the title and `nrow=None` (the first setting is lost, silently). Direct plotnine `guide_legend(nrow=2, title="T")` keeps both. The same replacement happens with any two of them.
4. `coord_lims` is described wrongly. Its label ("Coordinate limits (strict clip)"), its first description sentence ("also drop data outside the range (unlike coord_cartesian)") and its docstring ("Prevents data clipping...") say it removes data. The code calls `coord_cartesian`, which removes none. The description's own last sentence says "the same call as coord_cartesian". Run: the two are equal.

## Disagreements between the records and what I found

- Impact document section 3 and the audit test's OWN list call 21 of the 22 "convenience, preset or setter" and propose `step_` for all 22. Eve's new instruction (`plotnine_` for real, `modif_` for modified, `step_` for composite) gives different names for most of them: 14 `modif_` and 5 `step_`.
- Impact document Q2 says "`own` = `step_`". Eve's instruction of 2026-11-17 replaces that rule, so Q2 option (a) no longer matches.
- Impact document section 3 and the audit test's comment say the viridis scales call `scale_*_cmap(cmap_name=...)`. True, but they hide that `direction`, `begin`, `end` and `guide: none` fail.
- The audit test's OWN list says "one-call convenience" for `theme_custom`. Run shows it also converts elements and silently ignores unknown names (new defect 1).
- Impact document section 5 lists D1-D5; the 4 new defects are not there.
- The task listed `assets/template_data_analysis_recipes/` as a source. It does not exist in the repository (grep says "No such file or directory"). The count 0 / 1 therefore covers `config/` and `assets/gallery_data/` only.
- The impact document says only `theme_legend_position` is used by a shipped recipe. Confirmed (verified, run).

## What I did not check

- Other tables, other aesthetics or other values than the ones in my runs. Equal on the audit table is not proof for every table.
- Whether the viridis form restricts other plotnine scale parameters (`limits`, `breaks`, ...) with `allow_extra_params: False`. I read only the declared list.
- Python code outside the recipes that names these components: `app/handlers/blueprint_handlers.py`, `app/tests/test_shipped_recipes_hygiene.py`, `libs/blueprint_arch/tests/test_schema_registry.py` and docs mention some of the names. I did not open them. `docs/appendix/data_analysis_recipe_structure.yaml` lines 64 and 118 mention `scale_*_viridis_d`; I did not read what they say.
- The `value` alias of the guide setters, and the `_THEME_BASE_PARAMS` forms.
- The 1:1:1 test data files in `libs/viz_factory/tests/test_data/` (some exist for these names, e.g. `guide_title_test.yaml`). I did not run the existing example tests.
- plotnine versions other than 0.15.4.
- Whether `facet.free = {...}` (setting an internal attribute directly) is stable across plotnine versions (reasoned only).
