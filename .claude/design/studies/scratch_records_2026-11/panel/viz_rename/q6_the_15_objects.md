REPORT Q6: the 15 plotnine objects that cannot be added to a plot (plotnine 0.15.4). Nothing edited, renamed or committed. Scratch: tmpAI/panel/viz_rename/q6/ (h.py is the harness; b_pos, c_pos2, d_elem, e_elem2, f_guide, g_guide2, i_order, j_dedupe, k are the runs).
Labels: [run] = executed, [read] = read in code, [reasoned] = inferred.

0. Checks
- The D-0210 quotation is exact in ledger line 239 ("Q2 - note that all plotnine actions must have a default action (in case one was modified then there should be both the modif and the plotnine original)"). The D-0091, D-0050 and D-0165 quotations are also exact. [read]
- The impact doc (section 2.2) and the test list NOT_ADDABLE (test_registry_audit_vs_plotnine.py:330) name the same 15. The lists do not differ. [read]
- The 15: element_blank, element_line, element_rect, element_text; position_dodge, position_dodge2, position_fill, position_identity, position_jitter, position_jitterdodge, position_nudge, position_stack; guide_legend, guide_colorbar, guide_colourbar.
- In plotnine 0.15.4, `plotnine.guide_colourbar is plotnine.guide_colorbar` is True: one object, two names. Our `guide_colourbar` calls our `guide_colorbar` handler (guides/core.py:144-146). [run]

1. What each does today
- All 15, run alone in plotnine: `ggplot(DF, aes("x","y")) + <obj>()` fails with `AttributeError: '<name>' object has no attribute '__radd__'`. Same error for all 15. [run: a_direct.py]
- position_* (8): positions/core.py:19-25, `_apply_position` does `p.layers[-1].position = pos_obj`. It sets the position on the LAST geom already in the plot. With no layer before it, it raises CannotAct. Handlers at positions/core.py:40, 60, 80, 99, 122, 143, 165, 185. [read]
  - Recipe text: `- name: geom_bar` then `- name: position_dodge`, `params: {}` (config/.../2_test_data_ST22_dummy/plots/multi_resistance_by_country.yaml:6).
  - Run: `geom_bar` + `position_dodge{width:0.5}` gives a layer whose position is position_dodge with params {width 0.5, preserve total}. This is the same params as `geom_bar(position=position_dodge(width=0.5))` in plotnine direct. [run]
  - Shipped form `position_dodge{}`: params {None, total}, identical to direct `position="dodge"` and `position=position_dodge()`. [run]
  - Not compared as pictures: the factory adds theme_bw, coord and facet layers, so only the object parameters were compared.
- element_text, element_line, element_rect, element_blank: themes/core.py:365, 392, 418, 441. Each does `p + theme(**{target: element_*(**spec)})`. `target` is our key, not plotnine's. [read]
  - Recipe text: `- name: element_text, params: {target: axis_text_x, angle: 90, hjust: 1, vjust: 0.5, size: 8}` (config/.../1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:8-14).
  - Run: gives `theme(axis_text_x=element_text(angle=45, hjust=1))`, the same theme settings as direct plotnine (rotation 45, ha right). [run]
  - element_text is also handled by name in the factory: BATCHED_COMPONENTS (plot_config_resolver.py:172), applied last (viz_factory.py:334-361). The optimisation layer emits element_text layers itself (plot_config_resolver.py:506,511). Renaming it touches the factory too. [read]
- guide_legend, guide_colorbar, guide_colourbar: guides/core.py:84, 115, 144. Each does `p + guides(**{mapping: guide_*(**spec)})`. `mapping` is our key. [read]
  - Run: `guide_legend{mapping: color, nrow: 2, title: T}` gives `guides(color=guide_legend(nrow=2, title='T'))`. Identical in the properties compared (title, nrow, ncol, byrow). [run]

2. In plotnine directly
- See section 1: all 15 fail with the `__radd__` AttributeError when added alone. [run]
- Direct typo checks: `guides(colr=...)` gives "TypeError ... Did you mean 'color'?". `theme(axis_txt_x=...)` gives "There no themeable element called". Ours gives the same errors, wrapped in the factory's error form. [run]

3. How plotnine uses them, and what a recipe can write today
- Positions: plotnine takes them as the VALUE of `position=` on a geom or stat. A string name (`"dodge"`) or an object `position_dodge(width=0.5)` both work in plotnine. [run]
  - In a recipe, as a string on the geom: `position: dodge`, `dodge2`, `identity`, `stack`, `fill`, `jitter`, `jitterdodge`, `nudge` all work through the registry and render. They set the geom's position (run 4, 4b, 4c). Shipped examples: `position: "dodge"` (config/.../stress_test_master/plots/final_plot.yaml:9), `{name: geom_col, params: {position: dodge}}` (assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:39).
  - A value with parameters does NOT exist. `position: {name: position_dodge, params: {width: 0.5}}` and `position: {position_dodge: {width: 0.5}}` fail with "Unknown position of type <class 'dict'>", in the factory's error form. The string form cannot carry `width` or `height`. [run]
  - `position: position_dodge` (the call name as the value) also works, because plotnine accepts it. `position: bogus` fails with "'position_bogus' Not in Registry". [run]
- Elements: plotnine takes them as the VALUE of a `theme(...)` parameter.
  - `theme_custom` takes `{name: element_text, params: {...}}` as a value. It works for element_text, element_line, element_rect, element_blank (themes/core.py:323-340; runs G, H). It is hard-coded with if/elif. [run + read]
  - theme_bw and the other named themes refuse the same value: "unexpected keyword argument 'value'" (run L). Plain text `element_blank` is refused (run M). [run]
- Guides: plotnine takes them as the VALUE of `guides(color=...)` or of a scale's `guide=`.
  - Our `guides` component accepts only the strings `legend`, `colorbar`, `none`, `false` as typed values (guides/core.py:50-60). `{name: guide_legend, params: {nrow: 2}}` and `{nrow: 2}` fail with "Unknown guide: {...}"; the text `guide_legend` fails with "'guide_guide_legend' Not in Registry". The same on `scale_color_hue guide:`. [run]
  - The spec-level `guides:` block of a plot (viz_factory.py:~375-395) DOES take `{name: guide_legend, nrow: 2}`. That is a typed value with parameters. It has silent defects (section 6). [run + read]

4. What is technically possible, per group (evidence, no recommendation)
(i) Exact component in the strict sense (component called alone gives the same plot as plotnine called the same way)
- NO for all 15. Plotnine itself cannot add them alone (section 1: the `__radd__` AttributeError for all 15). So there is no plotnine plot to equal. The test `test_plotnine_cannot_add_this_object_to_a_plot_so_an_exact_step_cannot_exist` pins this. [run]
- Reasoned: an "exact component" could only be a function that RETURNS the plotnine object (a value constructor), not a layer step. That is item (ii).
(ii) Exact VALUE form (the plotnine object as the value of the parameter that takes it, built from its plotnine name plus parameters, nothing of ours added)
- Needed: a typed value `{name: <plotnine name>, params: {...}}` resolved by the registry at every parameter that takes an object: `position` of every geom and stat, every theme setting, `guides(...)` and a scale's `guide`.
- It exists today only in these places:
  - `theme_custom`, for the 4 element names (hard-coded; run G, H).
  - The spec-level `guides:` block, for guide_legend and guide_colorbar.
- It does not exist for `position` (string only, no parameters). `guides`, scale `guide` and the named themes refuse it.
- Not tested: whether the recipe checker (before render) would accept a new value form. No such form exists to test.
(iii) Keep the layer form as `modif_<name>`: what it adds or changes against plotnine
- Position:
  - It attaches to the LAST layer in the plot, only. Two geoms then dodge: only the second changes (run 3). With `bar, point, dodge`, dodge goes on the point and plotnine refuses with 'Width not defined'. So the order of layers in the recipe changes the result. No error says "this went to the point layer".
  - It silently REPLACES a position that the geom already had: `geom_bar{position: fill}` + `position_dodge{width: 0.5}` ends as dodge. [run]
  - A second position layer replaces the first on the same geom (dodge then stack gives stack). [run]
  - No geom before it gives a clear error (run 2). Dodge before the geom also gives that error.
  - Jitter seeding by the factory is a further addition of ours.
  - Parameters not in our form (e.g. `preserve`) still pass through (run c_pos2). [run]
- Elements: `target` is ours, so the plotnine theme key is a separate parameter.
  - element_text is applied LAST whatever its place in the recipe (defect D3).
  - A missing `target` and a typo target are clear errors. [run]
- Guides: `mapping` is ours. Missing `mapping` gives a clear error; a bad parameter gives a clear error. [run]
  - Plotnine-only parameters hidden in the form (byrow etc.) still pass through. [run]

5. Shipped use (config/, assets/gallery_data/) [read via grep]
- element_text: 3 uses in 2 files (ResFinder_genes_heatmap.yaml:8 and :15; VirulenceFinder_counts_bar.yaml:15), both in 1_test_data_ST22_dummy.
- position_dodge: 3 uses in 3 files (2_test_data_ST22_dummy: multi_resistance_by_country, plasmid_counts_by_year, multi_resistance_by_source), all `params: {}` after `geom_bar`.
- position_fill: 1 (assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:41, `{name: position_fill, params: {}}`).
- position_stack: 1 (assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:40).
- The other 10 (element_blank, element_line, element_rect, position_dodge2, position_identity, position_jitter, position_jitterdodge, position_nudge, guide_legend, guide_colorbar, guide_colourbar): 0 uses. guide_colourbar: 0.
- Value forms in shipped recipes: `position: "jitter"` (phenotype_genome_length_dotplot.yaml:11), `position: "dodge"` (final_plot.yaml:9), `position: dodge` (gallery bar_grouped), `position: stack` (gallery stacked_area:39). No shipped use of `theme_custom` or of a spec-level `guides:`.
- Not searched: test data under libs/*/tests and app/tests, and assets/template_data_analysis_recipes.

6. Defects found on the way (each run)
D1. element_text then element_blank on the same target: ours keeps the text; plotnine hides it. Ours: axis_text_x = {visible: True, rotation: 45}. Plotnine direct (text, then blank): {visible: False}. The user's blank is lost silently (cause: element_text is applied last). [run: e_elem2.py]
D2. element_text angle then element_text hjust, same target: ours drops the first. Ours: {size 8.8, ha right}, rotation lost. Plotnine merges: {rotation 45, ha right}. Two layers of the same element_text silently lose the first one's settings. [run]
D3. element_text is applied last whatever the order, so it survives a later complete theme. Ours, element_text then theme_minimal: rotation 90 kept. Plotnine direct, same order: {size 8.8}, rotation gone. The shipped heatmap recipe writes it in that order (ResFinder_genes_heatmap.yaml:8-17). It is by design (viz_factory.py:334 comment) but the element_text description does not say it. The result differs from plotnine for the same recipe text. [run: i_order.py]
D4. Position layers are deduplicated by name, so bar, dodge, bar, dodge keeps only the last dodge. Result: [('geom_bar', 'position_stack'), ('geom_bar', 'position_dodge')]. The first bar stays stacked; no error. [run: j_dedupe.py]
D5. The same name-dedupe for the other families:
  - Two `guide_legend` layers for color and fill: only fill remains; the color guide is lost silently. [run]
  - Two `element_blank` layers for two targets: the first is lost (panel_grid_minor stays visible True). [run: k.py]
  - Two `element_line` layers for two targets: the first is lost (axis_line colour None). [run]
  - Plotnine direct keeps both. Shipped recipes are not hit by D5 (element_text is deduped per target and the only element in shipped recipes; no shipped guide or element_blank/line/rect use).
D6. The spec-level `guides:` block (viz_factory.py:~375-395): `{name: guide_colourbar}` silently becomes a guide_legend (run result: guide_legend, title g); a typo `guide_legnd` silently becomes a guide_legend; the text `legend` is silently ignored (result `{}`). The lookup falls back with `_guide_ctors.get(ctor_name, guide_legend)`. [run: g_guide2.py]
D7. `theme_custom` with an unknown element name (`element_txt`) is silently dropped: the key vanishes and the render is OK (themes/core.py:329-337 if/elif without else). Already known in D-0211's note; confirmed by run I. [run + read]
D8. Not a defect but relevant to D-0214: a value of `position: position_dodge` (the call name) works in plotnine and through us. The text `guide_legend` as a `guides` value does not (fails, clear). [run]
- Clear refusals (not defects): no geom before a position; missing `target`; missing `mapping`; bad parameter names; target typo (all in the factory's error form). [run]

7. Options for Eve (no recommendation where D-0210 does not decide)
D-0210 says every plotnine object has its exact component and a modified one sits next to its original. Section 4(i) shows that cannot hold in the strict "alone" sense for these 15. The options below say what each does. Per D-0165, this is a choice that needs a decision; none exists.

| Option | `position_dodge` | `element_text` | `guide_legend` | Exact against plotnine | Ours | Breaks in shipped recipes | Silent |
|---|---|---|---|---|---|---|---|
| A. Only `modif_<name>` layers, no exact neighbour (the doc's default) | `- name: modif_position_dodge, params: {width: 0.5}` after the geom | `- name: modif_element_text, params: {target: axis_text_x, angle: 45}` | `- name: modif_guide_legend, params: {mapping: color, nrow: 2}` | Nothing: no `plotnine_` neighbour. The `plotnine` field would say "modified" with no original, which D-0210 forbids ("both the modif and the plotnine original"). | `target`, `mapping`, "last layer" attachment, element_text last, dedupe by name | 3 element_text, 3 position_dodge, 2 gallery (fill, stack): 8 renames | D1 to D7 unchanged |
| B. A value constructor registered as the exact `plotnine_<name>` (returns the object; usable only as a value) plus `modif_<name>` layer next to it | `position: {name: plotnine_position_dodge, params: {width: 0.5}}` on the geom, plus the layer form as modif | `theme_custom: {axis_text_x: {name: plotnine_element_text, params: {angle: 45}}}` plus the modif layer | `guides: {color: {name: plotnine_guide_legend, params: {nrow: 2}}}` plus the modif layer | The value is exact if built from plotnine's own parameters, nothing of ours. | The layer form (modif) | Same 8 shipped renames, as modif | Needs a value form for the 3 parameters; today it exists only for elements in `theme_custom` and for guide_legend/colorbar in the spec-level block. Each existing silent fallback (D6, D7) must be fixed for B to be a typed value without silence. |
| C. Remove the layer form; only the value form (`position: {name: plotnine_position_dodge, params: {...}}` on the geom) | Same as B's value | `theme_custom` value | `guides` value | Exact; our additions removed | Nothing of the layer form | The shipped 8 would need rewriting into values; no place for `target` or `mapping` as layer keys; D1 to D5 disappear because the layer and its dedupe disappear | Fewer silent paths, since no layer attachment, no dedupe, no batching |
| D. Keep layer, add value with parameters only where missing (positions) | `position: {name: position_dodge, params: {width: 0.5}}` | unchanged | unchanged | Partial | Layer form stays | None | Does not close D1 to D7 |

- Option C also removes the order-of-layers dependency. Option A, B and D keep D1 to D5 unless fixed separately.
- What each option needs, per [run] above: the value-with-parameters form is missing for `position` (strings only), missing for `guides`/scale `guide` (strings only), partial for elements (`theme_custom` only), partial for guides (the spec-level block only).
- Not decided here: the shape of the value key (`name`/`params` is what `theme_custom` and the guides block use today; the registry would resolve it).

What I did not check
- The recipe checker (the static check before render, `validate_data_analysis_recipe`): which of these values or layers it accepts. I ran the factory's render and `draw_checked` only.
- Pictures: layer form against direct plotnine were compared by object parameters, not by pixels (the factory adds its own theme/coord/facet layers).
- Test data under libs/*/tests, app/tests and assets/template_data_analysis_recipes for shipped counts; whether the Blueprint form and HOME (not run) use these 15 names in code outside the factory.
- Two `position_dodge` on two geoms with a dict value; stat_* layers as the target of a position layer; the interaction with the T3 overrides and plot_defaults for element_text.
- The Q6 section 8 text of the impact document beyond lines 415-430 was not re-read in full.
