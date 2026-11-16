# Plot components: audit against plotnine, and the impact of the rename (2026-11-15, corrected 2026-11-16)

Task VIZ-REGISTRY-AUDIT-1. Status: AUDIT AND PREPARATION ONLY. Nothing is renamed. The rename follows Eve's decision of 2026-11-15
(ADR-106 note V1-B, channel M106-M108) and waits for her answers in section 8.

Where the numbers come from. Every number in this document is produced by one of two things, and nothing is counted by hand:

- the tests in `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py` (they run plotnine 0.15.4 and compare it with the registry);
- the script `assets/scripts/viz_rename_table.py`. **One command regenerates every table and count of sections 6 and 9:**
  `PYTHONPATH=. ./.venv/bin/python assets/scripts/viz_rename_table.py report --root .`
  (the script leaves this document and itself out of the count; the sample of section 6.2 is `... sample --root . --per-class 30 --seed 1`).

Plain words used here. A *component* is one name that a recipe can write in `layers:`, for example `geom_point` (points) or `theme_bw` (a black-and-white look).
A component is *exact* when it only hands your parameters to the plotnine object of the same name, so you get exactly what the plotnine documentation describes.
It is *modified* when it adds or changes something. It is *own* when plotnine has nothing of that name.

## 1. What changes for a recipe maker

1. Every component name in a recipe gets a prefix. `geom_point` becomes `plotnine_geom_point`; `theme_bw` becomes `modif_theme_bw`;
   `theme_dashboard` becomes `step_theme_dashboard`. The prefix tells you at a glance: `plotnine_` = exactly plotnine, `modif_` = plotnine with a change that is written down,
   `step_` = the project's own.
2. The `theme:` key of a plot and of `plot_defaults` also holds a component name, so it changes too.
3. An old name is refused. The message gives the new name and the command that converts your recipes. Both spellings never work side by side
   (Eve, 2026-11-15: "we need to detect all errors").
4. Pictures must not change. The conversion only rewrites names. A test must prove this before the rename is accepted (section 7, step 0).
5. A results bundle exported before the change contains old names. It runs only after conversion, and conversion changes the recipe file, so the recipe's recorded fingerprint
   (`data_analysis_recipe_sha256`) changes. This is the one point that touches reproducibility; it needs your decision (question Q1).

## 2. The audit, in numbers (plotnine 0.15.4, run)

| What | Count |
|---|---|
| Public plotnine objects (`plotnine.__all__`) | 232 |
| Registered components | 191 (169 carry a plotnine name, 22 carry a name plotnine does not have) |
| Exact / modified / own | 123 / 46 / 22 |
| Plotnine names not registered | 63 |
| ... not components of a plot (`aes`, `ggplot`, `ggsave`, `qplot`, the session-theme setters, the expressions inside a mapping) | 13 |
| ... the other spelling of a registered component (`scale_colour_manual` for `scale_color_manual`, `theme_grey`, `geom_bin2d`, `stat_bin2d`) | 15 |
| ... real gaps | 35 |
| Exact components compared with the direct plotnine call by running them (example and no parameter) | 123 |
| Differences found between an exact component and plotnine (parameters, defaults, the plot built, the data drawn, the picture) | 0 |
| Parameters of exact components, all read from plotnine | 1863 |
| Modified components that do not offer all the plotnine parameters (section 2.3) | 21 of the 41 that wrap a plotnine object; 165 parameters; 13 of them cannot be written at all |

How the comparison was made: for each exact component, the component of this project and the direct plotnine call are both asked to build the example from its help text, and again with no parameter.
Both must give the same plot object. For a layer (a geom or a stat) the table that it will draw must also be equal; for a scale, theme, facet, coordinate or guide the picture must also be equal
(`geom_smooth` is compared as an object only, it needs a package that is not installed to draw).

A default is the value plotnine uses when you write nothing. For 62 parameters of exact components that value is not a plain number or word, so the form cannot show it.
Example: `geom_bar` draws its `y` as "the number of rows in each bar" (plotnine writes it `after_stat('count')`): a calculation, not a value you could type. The 62 are: 36 "not a number",
14 calculations like that one, 4 "from minus infinity to infinity", 8 empty settings `{}`. In every case the component still uses plotnine's own default,
because it hands plotnine nothing when you write nothing. The test `test_the_defaults_the_form_does_not_show_are_the_audited_62` pins the list.

Plain reading: the exact components are exact. The work is the naming, the gaps, the modified components and the defects of section 5.

### 2.1 The 35 real gaps (plotnine components that no registered name covers)

- Scales, 21: the `datetime`, `ordinal`, `desaturate`, `gray` and `grey` variants for `color`, `colour` and `fill` (15); `scale_alpha_datetime`, `scale_alpha_ordinal`,
  `scale_size_datetime`, `scale_size_ordinal` (4); `scale_size_radius`, `scale_stroke` (2).
- Layers, settings and helpers, 14: `annotation_logticks`, `annotation_stripes`, `expand_limits`, `lims`, `xlim`, `ylim`, `theme`, `watermark`, `stat_pointdensity`,
  `geom_map` (needs the package `geopandas`, not installed), and the four labellers `label_both`, `label_context`, `label_value`, `labeller`
  (a recipe writes their names as the value of the facet parameter `labeller`, which works; section 4).
- The exact list is `KNOWN_MISSING` in the test. A new plotnine object at an upgrade fails the test until somebody classifies it.

### 2.2 The 46 modified components, run

| Group | Count | Meaning, with an example |
|---|---|---|
| Plotnine cannot put this object on a plot by itself | 15: `element_blank`, `element_line`, `element_rect`, `element_text`, `position_*` (8), `guide_legend`, `guide_colorbar`, `guide_colourbar` | In plotnine these are parts that you hand to something else (a text style goes inside `theme(...)`, a position inside a geom). A recipe needs a stand-alone step, so the project adds the missing information. Example: `element_text` here needs `target: axis_text_x`, which says WHICH text to style; plotnine's `element_text` has no such key. For these an exact "plotnine" twin cannot exist as a step. |
| Equal to plotnine as long as you do not use the extra | 29: `annotate`, `facet_grid`, `ggtitle`, `guides`, `xlab`, `ylab`, `geom_jitter`, `geom_sina`, `stat_sina`, 5 scales, `scale_x_continuous`, `scale_y_continuous`, 13 themes | Example: `theme_bw` here also accepts extra theme settings in the same step; with none written it gives exactly plotnine's `theme_bw`. The extras are: a seed set by the factory (3), a list turned into a tuple (5), `breaks_integer` (2), extra theme settings (13), a formula such as `rows ~ cols` for `facets` (1), a clearer refusal when a key is missing (5: `annotate`, `ggtitle`, `xlab`, `ylab`, `guides`). |
| Different | 2: `stat_function` (accepts a function written as text), `stat_identity` (does nothing, ignores its parameters) | |

None of the 46 has its exact plotnine twin registered next to it today (tested).

### 2.3 Plotnine parameters that modified components do not offer

The form (Blueprint) and the component's list of parameters offer only what the component declares. For 21 modified components plotnine accepts more.
Example: `scale_alpha` (transparency scale) does not list `limits`, `breaks`, `labels`, `trans`; plotnine has them.
A recipe may still write them, the checker lets them through (they are plotnine's own names); but the form never shows them, and for 4 themes they cannot be written at all (section 5).
Counted by comparing each component's parameter list with plotnine's signature (`data`, `mapping`, `rescaler`, `oob` left out: a table or a function, which a recipe cannot hold).

| Modified component | Plotnine parameters it does not offer | How many | Cannot be written at all |
|---|---|---|---|
| `facet_grid` | `as_table`, `drop`, `labeller`, `shrink` | 4 | none |
| `geom_jitter` | `geom`, `group`, `inherit_aes`, `position`, `random_state`, `raster`, `show_legend`, `stat`, `stroke`, `x`, `y` | 11 | none |
| `geom_sina` | `adjust`, `bin_limit`, `bins`, `binwidth`, `bw`, `geom`, `group`, `inherit_aes`, `position`, `raster`, `show_legend`, `stat`, `stroke`, `style`, `x`, `y` | 16 | none |
| `guide_colorbar` | `alpha`, `direction`, `display`, `draw_llim`, `draw_ulim`, `order`, `position`, `theme` | 8 | none |
| `guide_colourbar` | `alpha`, `direction`, `display`, `draw_llim`, `draw_ulim`, `nbin`, `order`, `position`, `reverse`, `theme` | 10 | none |
| `guide_legend` | `byrow`, `direction`, `order`, `override_aes`, `position`, `theme` | 6 | none |
| `guides` | `colour`, `stroke` | 2 | none |
| `position_dodge` | `preserve` | 1 | none |
| `scale_alpha` | `aesthetics`, `breaks`, `expand`, `labels`, `limits`, `minor_breaks`, `na_value`, `trans` | 8 | none |
| `scale_color_hue` | `aesthetics`, `breaks`, `color_space`, `direction`, `drop`, `expand`, `labels`, `limits`, `na_translate`, `na_value`, `s` | 11 | none |
| `scale_fill_hue` | `aesthetics`, `breaks`, `color_space`, `direction`, `drop`, `expand`, `labels`, `limits`, `na_translate`, `na_value`, `s` | 11 | none |
| `scale_size` | `aesthetics`, `breaks`, `expand`, `labels`, `limits`, `minor_breaks`, `na_value`, `trans` | 8 | none |
| `scale_size_area` | `aesthetics`, `breaks`, `expand`, `labels`, `limits`, `minor_breaks`, `na_value`, `trans` | 8 | none |
| `scale_x_continuous` | `aesthetics`, `guide`, `minor_breaks`, `na_value`, `trans` | 5 | none |
| `scale_y_continuous` | `aesthetics`, `guide`, `minor_breaks`, `na_value`, `trans` | 5 | none |
| `stat_function` | `alpha`, `args`, `arrow`, `color`, `geom`, `group`, `inherit_aes`, `lineend`, `linejoin`, `linetype`, `position`, `raster`, `show_legend`, `size`, `stat`, `x`, `y` | 17 | none |
| `stat_sina` | `adjust`, `alpha`, `bin_limit`, `bins`, `binwidth`, `bw`, `color`, `fill`, `geom`, `group`, `inherit_aes`, `position`, `raster`, `shape`, `show_legend`, `size`, `stat`, `stroke`, `style`, `x`, `y` | 21 | none |
| `theme_matplotlib` | `fname`, `rc`, `use_defaults` | 3 | `fname`, `rc`, `use_defaults` |
| `theme_seaborn` | `context`, `font`, `font_scale`, `style` | 4 | `context`, `font`, `font_scale`, `style` |
| `theme_tufte` | `ticks` | 1 | `ticks` |
| `theme_xkcd` | `length`, `randomness`, `scale`, `stroke_color`, `stroke_size` | 5 | `length`, `randomness`, `scale`, `stroke_color`, `stroke_size` |
| TOTAL: 21 components | | 165 | 13 |

Test: `test_the_modified_components_hide_165_plotnine_parameters_from_the_form` and `test_a_hidden_parameter_is_written_through_the_component_unless_it_is_one_of_the_listed_themes_settings`.


## 3. The 22 names that exist in no plotnine

Evidence: none of the 22 names (nor the `colour`, `grey` or `bin2d` spelling of them) is defined in plotnine 0.15.4, 0.12.0 or 0.5.1 (source read), and the
plotnine changelog page (v0.1 to the latest) names none of them (read once by a tool, not line by line). So none is a plotnine component under an older or newer name.
Each is a convenience, a preset, a setter, or broken. Future class by the rule `own = step_` (question Q2):

| Name | What it is, run | Calls | Future name |
|---|---|---|---|
| `facet_rows`, `facet_cols` | convenience over one call | `facet_grid` with only rows / only cols | `step_facet_rows`, `step_facet_cols` |
| `coord_lims` | the same call as `coord_cartesian` under another name | `coord_cartesian(xlim, ylim)` | `step_coord_lims` (or drop: `plotnine_coord_cartesian` does it) |
| `guide_title`, `guide_ncol`, `guide_nrow`, `guide_reverse`, `guide_direction` | convenience: one setting of `guide_legend`, for the aesthetic in `mapping` | `guides(<aes>=guide_legend(one setting))` | `step_guide_title` etc. |
| `guide_none` | convenience: hides the guide of one aesthetic | `guides(<aes>=False)` | `step_guide_none` |
| `guide_label` | BROKEN: calls `guide_legend(labels=...)`, which plotnine refuses; fails on every use | none | remove (question Q7) |
| `theme_legend_position` | convenience | `theme(legend_position=...)` | `step_theme_legend_position` |
| `theme_custom` | convenience: `theme(**settings)` plus turning `{name: element_text, params}` into elements | `theme(...)` | `step_theme_custom` |
| `scale_color_viridis_c/d`, `scale_fill_viridis_c/d` | plotnine has no viridis scale (only `cmap` ones); the name is borrowed from ggplot2 | `scale_*_cmap(_d)(cmap_name=...)` | `step_scale_color_viridis_c` etc. |
| `theme_dashboard`, `theme_publication` | the project's presets | `theme_bw(base_size=14)`, `theme_classic(base_size=11)` | `step_theme_dashboard`, `step_theme_publication` |
| `facet_labeller`, `facet_margins`, `facet_scales`, `facet_space` | setters that change the facet already on the plot (order matters; refused without a facet) | no plotnine call; plotnine sets these inside `facet_wrap` / `facet_grid` | `step_facet_labeller` etc. (or fold into the exact facet parameters, Q8) |

Only one of the 22 is used by a shipped recipe: `theme_legend_position` (1 use). The others are used by nobody yet.

## 4. Components that take a function or an expression

plotnine lets some parameters be Python functions or expressions. A recipe holds data, not code. What a recipe can write today, run on the project's test table:

| Component and parameter | A recipe CAN write | A recipe CANNOT write | What reaches plotnine unchecked |
|---|---|---|---|
| `stat_summary`, `stat_summary_bin`: `fun_data` | a name: `mean_se`, `mean_cl_boot`, `mean_cl_normal`, `mean_sdl`, `median_hilow` | any function | a wrong name: plotnine refuses it (`KeyError: mean_foo`), the message is shown with layer and parameter |
| the same: `fun_y`, `fun_ymin`, `fun_ymax` | nothing (not offered; `fun_y: mean` is refused: "'mean' is not a callable object") | a function such as the mean, a quantile | nothing reaches plotnine: the form does not offer them (N28 stays open) |
| `stat_function`: `fun` | a math function name (`sin`) or a text `lambda x: ...`, checked, numpy maths only | any other code | nothing: the text is checked first |
| `geom_smooth`, `stat_smooth`: `method` | a name: `lm`, `ols`, `wls`, `rlm`, `glm`, `gls`, `lowess`, `loess`, `mavg`, `gpr`; `formula` as text (`y ~ x + I(x**2)` runs) | a function | a wrong name (`foo`) is refused by plotnine with the list of allowed names |
| 38 continuous scales: `breaks`, `minor_breaks`, `limits` | a list of numbers | a function of the range | a string (`'foo'`) reaches numpy and fails with a technical message |
| 29 discrete scales: `breaks`, `limits` | a list of texts | a function | not run on a string; same path |
| 67 scales: `labels` | a list, a dict `{a: Alpha}` (runs), `true`, `false` | a function | **a text where a list was meant is accepted silently**: `labels: abc` draws the labels a, b, c with no message (run). A text of the wrong length is refused. |
| 38 continuous scales: `trans` | a name: `log10` (runs), `sqrt`, `reverse`, ... | a transform object | a wrong name is refused (`Could not get transform object`) |
| 31 scales: `rescaler`, `oob` | nothing (not offered; `oob: censor` is refused: "'str' object is not callable") | a function; plotnine's own names such as `censor`, `squish` | not offered |
| facets: `labeller` | `label_value`, `label_both`, `label_context` | a function | a wrong name is refused by plotnine |
| mappings: `after_stat`, `after_scale`, `stage`, an expression such as `x*2` | only a column name | any expression | refused at once: "mapped to a column which the data does not have" (clear). Twelve components (`geom_bar`, `geom_histogram`, `stat_count`, `stat_bin`, `stat_density`, `stat_qq`, ...) rely on an `after_stat` default (for example `geom_bar` counts); that default works, but cannot be rewritten in a recipe. |
| layers: `data` (a function of the table) | nothing (not offered) | a function | not offered |

Short list of components with a function or expression parameter: `stat_summary`, `stat_summary_bin`, `stat_function`, `geom_smooth`, `stat_smooth`,
all continuous and discrete scales (breaks, limits, labels, trans, rescaler, oob), the facets (`labeller`), every layer (`data`, and the mapping expressions).
For `stat_summary` a transparent and reproducible way exists today: the named summaries of `fun_data`. A wider list (a quantile with its probability, `min`, `max`) would be
a project addition and a decision of yours (N28, not decided here). One unchecked path found: `labels` given as a text (defect D4, section 5).

## 5. Defects found by the audit

Nothing is fixed here (the task is the audit). Each defect is pinned by a test in the audit file: an expected failure that turns into a red test the day somebody fixes it,
so the entry is then removed. The run that shows each one is given.

| # | Defect | The run that shows it | Pinned by |
|---|---|---|---|
| D1 | `theme_seaborn` and `theme_matplotlib` list `base_size` and `base_family` in their form, and refuse them. The message is also wrong: "'base_size' is not an argument of theme_seaborn. Fix: write base_size." | Layer `theme_seaborn` with `base_size: 12` gives `VisualizationError: layer 2 (theme_seaborn): 'base_size' is not an argument of theme_seaborn. Fix: write base_size.` Same for `base_family` and for `theme_matplotlib`. plotnine's `theme_seaborn` takes `style`, `context`, `font`, `font_scale`; `theme_matplotlib` takes `rc`, `fname`, `use_defaults`. | `test_defect_the_theme_setting_works[theme_seaborn offers base_size and refuses it]` and the matplotlib one |
| D2 | The plotnine parameters of those two themes cannot be reached. The component sends every key that it does not know to `theme(...)`, which refuses it. The same for `theme_tufte` (`ticks`) and `theme_xkcd` (`length`, `randomness`, `scale`, `stroke_color`, `stroke_size`): 13 parameters of 4 themes. | `theme_seaborn` with `style: whitegrid` gives `PlotnineError: 'There no themeable element called: style'`; the direct call `plotnine.theme_seaborn(style='whitegrid')` works. Same for `context`, and `rc` of `theme_matplotlib`. | `test_defect_the_theme_setting_works[...style / context / rc...]`, and `test_a_hidden_parameter_is_written_through_the_component_...` (the list of 13) |
| D3 | `guide_label` fails on every use. It was meant to set the legend labels through `guide_legend`, which has no `labels` argument. It says so (the message is clear) but it is offered in the form and the picker. | Layer `guide_label` with `mapping: color` and `labels: [a, b, c]` gives `guide_label cannot work: it passes labels to plotnine's guide_legend, which has no such argument.` | `test_defect_guide_label_fails_on_every_use_and_says_so` (question Q7) |
| D4 | A text where a list was meant is read by plotnine as its letters and drawn with no message: three scales, three parameters. | `scale_x_continuous` with `breaks: [10, 50, 90]` and `labels: abc` draws the labels a, b, c. `scale_color_brewer` with `limits: abc` and `scale_color_manual` with `breaks: abc` are accepted too (the data here has the groups a, b, c, so the picture looks right; with other group names the legend would silently lose them). A text of the wrong length for `labels` IS refused. | `test_defect_a_text_where_a_list_is_meant_is_refused[...]` (3) |
| D5 | The `geom_jitter` description said "`random_state: null` gives a new one each time", but the factory refuses null (a seed is a number; S1, 2026-11-15). Corrected in this round (text only). | Description before: "...; `random_state: null` gives a new one each time." Now: "...; a seed is a number: `random_state: 0` sets it; `null` and `random` are refused." | `test_no_description_says_that_a_null_or_random_seed_is_allowed` (it fails on the old text; seen) |

Smaller point found on the way: the form offers `oob` and `rescaler` of 31 scales to nobody (they take a Python function, a recipe cannot hold one), and a text such as `oob: censor` is refused with "'str' object is not callable";
plotnine's own function names (`censor`, `squish`) cannot be written. Listed in section 4.

## 6. Impact of the rename (dry run)

All counts below are generated by `viz_rename_table.py report --root .` on the committed files of this branch. A line is counted once per component name on it.
Three separate classes, because they ask different things of a person:

- **MUST CHANGE**: a recipe line `name: <component>` (also inside a document or a test string), the `theme:` key of a plot spec, a component name written as a string in code or in a test (a registration, a list, an assertion).
- **STAYS**: plotnine's own names (a direct call or an import in Python, the `wraps` line that names the plotnine object, the value of a `stat`, `position` or `geom` parameter, the `geom` field of the gallery index and the tag strip generated from it: proposal Q5), and history files (logs, archives, old conversations), which are kept as they were.
- **READ by a person**: a name inside a sentence, a comment, a docstring or a message; every rule file (listed, edited only after your yes). Often the text must change too, but only a person can tell how.

### 6.1 The counts

| group of files | files with a name | MUST CHANGE | STAYS | READ by a person | all |
|---|---|---|---|---|---|
| viz library code (registration and name logic) | 13 | 465 | 581 | 325 | 1371 |
| viz library tests | 221 | 1098 | 90 | 157 | 1345 |
| history: logs, archives (kept as they were) | 65 | 0 | 799 | 0 | 799 |
| records: design, knowledge, tasks, workflows | 29 | 33 | 1 | 396 | 430 |
| other tests | 64 | 294 | 41 | 34 | 369 |
| docs pages and READMEs | 14 | 60 | 1 | 246 | 307 |
| gallery recipes and index | 70 | 87 | 70 | 92 | 249 |
| scripts | 4 | 71 | 55 | 4 | 130 |
| plot spec files | 25 | 65 | 0 | 0 | 65 |
| rule files (listed, never edited by the rename) | 8 | 0 | 0 | 43 | 43 |
| other code (libs, app) | 7 | 18 | 0 | 25 | 43 |
| pipeline recipes (outside plots/) | 6 | 12 | 0 | 1 | 13 |
| Blueprint pickers, forms and the agent tool | 1 | 8 | 0 | 0 | 8 |
| template recipes | 4 | 8 | 0 | 0 | 8 |
| retest recipes | 4 | 5 | 0 | 0 | 5 |
| TOTAL | 535 | 2224 | 1638 | 1323 | 5185 |

By kind of occurrence:

- MUST CHANGE: 2224
    - 1238: a component name written as a whole string (a registration, a list, an assertion)
    - 730: a recipe line `name: <component>` (block or flow form)
    - 230: recipe text inside a string: a recipe line `name: <component>` (block or flow form)
    - 23: the `theme:` key of a plot spec or of plot_defaults (a component name; a `theme:` elsewhere is read first)
    - 3: recipe text inside a string: the `theme:` key of a plot spec or of plot_defaults (a component name; a `theme:` elsewhere is read first)
- STAYS: 1638
    - 799: a history file, kept as it was
    - 535: a direct plotnine call or import (plotnine's own name)
    - 184: the `wraps` entry that names the plotnine object itself
    - 35: the tag strip of a gallery example (generated from the `geom` taxonomy field; proposal Q5)
    - 35: the value of a `stat` / `position` / `geom` parameter (plotnine's own object; proposal Q5)
    - 34: the `geom` field of the gallery index (the exact plotnine function name; proposal Q5)
    - 11: the value of the parameter `stat` (plotnine's own object; proposal Q5)
    - 3: the value of the parameter `geom` (plotnine's own object; proposal Q5)
    - 1: recipe text inside a string: the value of the parameter `geom` (plotnine's own object; proposal Q5)
    - 1: the value of the parameter `position` (plotnine's own object; proposal Q5)
- READ: 1323
    - 670: prose
    - 221: a name inside a sentence or message
    - 200: a Python comment
    - 71: a docstring
    - 56: written text in a recipe (description, label, comment)
    - 43: a rule file (listed, edited only after Eve's yes)
    - 42: a recipe comment or continuation line
    - 7: the value of the key `review_trigger`
    - 2: text inside a multi-line string
    - 2: the value of the key `name`
    - 2: the value of the key `facet_scales`
    - 2: the value of the key `labs`
    - 1: the value of the key `theme`
    - 1: the value of the key `optional`
    - 1: the value of the key `coordinate_flip`
    - 1: Python text outside a string or identifier
    - 1: the value of the key `subtitle`

In words (from the table above): 535 files name a component, 5185 times. 2224 occurrences must change, 1638 stay, 1323 are for a person to read.
The recipe files a person writes are almost all in MUST CHANGE: 25 plot spec files (65), 6 pipeline recipes (12), 4 templates (8), 4 retest recipes (5), 70 gallery files (87 recipe lines; 70 stay; 92 are text to read).
Shipped recipes use 39 of the 191 components in 171 places (27 exact, 11 modified, 1 own: `theme_legend_position`); the other 152 components are used only by tests and by the form.
Blueprint pickers and forms read the registry, so they follow the new names by themselves; what is hand-written is the list `_THEME_CHOICES` in `app/handlers/blueprint_handlers.py` (the 8 occurrences
of the Blueprint group) and the instructions of the agent; to verify, not to guess: a test must show that the picker and the agent offer only new names.
Rule files, never edited by the rename: `rules_viz_factory.md`, `rules_data_analysis_recipe_structure.md`, `rules_gallery_standards.md`, `rules_documentation_aesthetics.md`,
`rules_agent_role_bioscientist.md`, `rules_code_quality.md`, `rules_test_lab.md`, `workspace_standard.md` (43 occurrences; a proposal after your yes).

### 6.2 How reliable the classification is (sampled by eye)

Sample of 30 occurrences from each class (command `sample --per-class 30 --seed N`), every line read and judged.

| Sample | MUST CHANGE wrong | STAYS wrong | READ wrong |
|---|---|---|---|
| First pass (seed 1) | 3 of 30 (10%): the `wraps` line that names the plotnine object | 0 of 30 | 6 of 30 (20%): five `yaml_example` texts with `\n  - name: ...` inside one string, one generated tag strip |
| After the repair of those three causes (seed 2, other lines) | 0 of 30 | 0 of 30 | 0 of 30 |

The line the review quoted, `app/tests/equality/reference_2_test_data_ST22_dummy.py:155`, is a docstring and is now READ (it was labelled a plotnine call).
Doubtful by nature, left to a person: a theme-element spec such as `legend_title: {name: element_blank}` is counted MUST CHANGE (it names a registered component), but whether the nested element
follows the new name depends on how the theme settings are converted; a message that tells the user "write name: geom_point" is READ (the message must follow, a person words it).
0 of 30 in a class bounds that class's error rate at about 10 percent (95 percent confidence); 0 of 90 for the three together, at about 3 percent. It is not zero, and the first pass shows what kind of error remains possible: a line whose role depends on the code around it.

### 6.3 Code that tests a name by its start (must change first)

The prefix `plotnine_` breaks every test of the form "starts with `geom_`". Found by a repeatable search (`viz_rename_table.py sites`): every `startswith(...)`, `removeprefix`, `lstrip`, `.split("_")`,
prefix string and regular expression with a family name, found by parsing the Python files under `libs/`, `app/` and `assets/scripts/`. 64 lines in 20 files; 23 lines in 6 files are production code.

What breaks at each production site if the names change and the test does not:

| file:line | What it does | What breaks |
|---|---|---|
| `plot_config_resolver.py:130` | geoms and stats are never merged, they pile up | `plotnine_geom_point` does not start with `geom_`: two geoms with the same name would count as one and the later replaces the earlier, so a layer silently disappears |
| `plot_config_resolver.py:137` | one theme replaces the other | two themes both stay |
| `plot_config_resolver.py:141`, `:146` | one coordinate system, one facet | a second one no longer replaces the first |
| `plot_config_resolver.py:148`, `:150`, `:152`, `:154`, `:156`, `:158`, `:160` | one scale per aesthetic (fill, colour, x, y, other families) | the later scale no longer replaces the earlier: plotnine receives two |
| `plot_config_resolver.py:313` | partial themes (settings only) go after a complete theme | the order is wrong: a complete theme erases the settings that came before |
| `plot_config_resolver.py:656` | the key `facet_by` adds a facet unless the recipe has a facet layer | a facet layer written with the new name is not seen, a second facet is added |
| `plot_config_resolver.py:719` | which theme is the plot's theme | the user's theme is not found, the default theme is used (the picture changes) |
| `plot_config_resolver.py:732`, `:735`, `:736` | a palette is added only if the recipe has no scale of its own | the palette is added on top of the user's own scale (the picture changes, no message) |
| `recipe_check.py:930` (`libs/utils`) | the checker looks for at least one geom or stat | every plot is reported as having no geom |
| `data_analysis_recipe_validator.py:130` (`app/modules`) | the list of themes that the checker offers | the list is empty: every `theme:` key is refused |
| `taxonomy.py:38` (`libs/viz_gallery`) | the geom of a gallery example, for the index and the search | `first_geom` returns an empty text for every example; the index loses its geom axis |
| `errors.py:45` (`libs/viz_factory`) | the words of an error message ("the spec's theme" or "facet_by") | the message names the wrong thing |
| `random_layers.py:50`, `:55` (`libs/utils`) | add `position_` or `stat_` to a plain word the user wrote in a PARAMETER (`position: jitter`) | not affected: that is plotnine's own vocabulary and stays. But the names it is compared with (`ALWAYS_RANDOM`, `stat_summary_bin`) are component names and follow the rename |

The 41 other lines are in tests, debug scripts and `assets/scripts/rename_vocabulary.py` (3 `.split("_")`, to read: probably unrelated); they must follow the code.
One function `component_family(name)` that strips the prefix and returns `geom`, `stat`, `scale_fill`, ... replaces all of them; a test must fail if a `startswith("geom_")` remains.

The complete list, generated:

| file:line | what it does with a name |
|---|---|
| `app/modules/data_analysis_recipe_validator.py:130` | .startswith() theme_ |
| `app/tests/test_render_every_plot.py:60` | .startswith() facet_grid, facet_wrap |
| `assets/scripts/rename_vocabulary.py:42` | .split("_") splits a name into its parts |
| `assets/scripts/rename_vocabulary.py:68` | .split("_") splits a name into its parts |
| `assets/scripts/rename_vocabulary.py:308` | .split("_") splits a name into its parts |
| `libs/utils/src/utils/random_layers.py:50` | prefix string position_ |
| `libs/utils/src/utils/random_layers.py:55` | prefix string stat_ |
| `libs/utils/src/utils/recipe_check.py:930` | .startswith() geom_, stat_ |
| `libs/viz_factory/src/viz_factory/errors.py:45` | .startswith() theme_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:130` | .startswith() geom_; .startswith() stat_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:137` | .startswith() theme_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:141` | .startswith() coord_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:146` | .startswith() facet_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:148` | .startswith() scale_fill_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:150` | .startswith() scale_color_; .startswith() scale_colour_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:152` | .startswith() scale_x_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:154` | .startswith() scale_y_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:156` | .startswith() scale_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:158` | .split("_") splits a name into its parts |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:160` | prefix string scale_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:313` | .startswith() theme_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:656` | .startswith() facet_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:719` | .startswith() theme_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:732` | .startswith() scale_fill_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:735` | .startswith() scale_color_ |
| `libs/viz_factory/src/viz_factory/plot_config_resolver.py:736` | .startswith() scale_colour_ |
| `libs/viz_factory/tests/debug_audit.py:81` | .startswith() coord_, element_, facet_, geom_, guide_, position_, scale_, theme_ |
| `libs/viz_factory/tests/debug_runner.py:109` | .split("_") splits a name into its parts |
| `libs/viz_factory/tests/debug_runner.py:130` | .startswith() position_ |
| `libs/viz_factory/tests/debug_runner.py:133` | .startswith() geom_ |
| `libs/viz_factory/tests/debug_runner.py:152` | .startswith() position_ |
| `libs/viz_factory/tests/debug_viz_factory_audit.py:107` | prefix string coord_; prefix string facet_; prefix string geom_; prefix string scale_; prefix string theme_ |
| `libs/viz_factory/tests/debug_viz_factory_audit.py:108` | prefix string element_; prefix string guide_; prefix string position_; prefix string stat_ |
| `libs/viz_factory/tests/test_component_schemas.py:177` | .startswith() geom_ |
| `libs/viz_factory/tests/test_every_component_randomness.py:60` | prefix string coord_; prefix string element_; prefix string facet_; prefix string guide_; prefix string scale_; prefix string theme_ |
| `libs/viz_factory/tests/test_every_component_randomness.py:68` | .startswith() stat_ |
| `libs/viz_factory/tests/test_every_component_randomness.py:69` | .startswith() position_ |
| `libs/viz_factory/tests/test_every_component_randomness.py:146` | .startswith() geom_, stat_ |
| `libs/viz_factory/tests/test_every_component_randomness.py:154` | .startswith() geom_ |
| `libs/viz_factory/tests/test_every_component_randomness.py:162` | .startswith() theme_ |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:57` | .startswith() geom_, stat_ |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:61` | .startswith() position_ |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:92` | .startswith() scale_ |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:93` | .split("_") splits a name into its parts |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:102` | .startswith() scale_x_, scale_y_ |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:104` | .split("_") splits a name into its parts |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:107` | .split("_") splits a name into its parts |
| `libs/viz_factory/tests/test_every_yaml_example_renders.py:109` | .startswith() guide_ |
| `libs/viz_factory/tests/test_no_silent_error.py:178` | .startswith() geom_ |
| `libs/viz_factory/tests/test_plot_config_resolver.py:30` | .startswith() theme_ |
| `libs/viz_factory/tests/test_plot_config_resolver.py:134` | .startswith() coord_ |
| `libs/viz_factory/tests/test_plot_config_resolver.py:143` | .startswith() facet_ |
| `libs/viz_factory/tests/test_plot_config_resolver.py:489` | .startswith() coord_ |
| `libs/viz_factory/tests/test_plot_config_resolver.py:552` | .startswith() facet_ |
| `libs/viz_factory/tests/test_plot_spec_roundtrip.py:30` | .startswith() geom_, stat_ |
| `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py:65` | prefix string scale_color_; prefix string scale_colour_ |
| `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py:86` | prefix string scale_ |
| `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py:87` | prefix string scale_ |
| `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py:88` | prefix string scale_ |
| `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py:89` | prefix string scale_ |
| `libs/viz_factory/tests/test_theme_slots.py:30` | .startswith() theme_ |
| `libs/viz_factory/tests/test_theme_slots.py:43` | .startswith() theme_ |
| `libs/viz_factory/tests/viz_factory_integrity_suite.py:67` | .split("_") splits a name into its parts |
| `libs/viz_gallery/src/viz_gallery/taxonomy.py:38` | .startswith() geom_, stat_ |

64 lines in 20 files; 23 lines in 6 production files (the rest in tests and scripts)

### 6.4 What the script cannot decide alone

| Kind | Example | Why a person decides |
|---|---|---|
| A component name as a parameter VALUE | `libs/viz_factory/tests/test_data/stat_bin_test.yaml:12: stat: stat_bin` | plotnine's own object passed to a layer, not a component call. Proposal: stays (Q5). The script counts it as STAYS |
| The `geom` field of the gallery index | `assets/gallery_data/gallery_index.json:22: "geom": "geom_area"` (34 lines; the tag strips of the examples, 35) | the taxonomy says "the exact plotnine function name". Proposal: stays (Q5) |
| A `theme:` key | `app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/plots/multi_resistance_by_country.yaml:2: theme: theme_light` | in a plot spec or in `plot_defaults` it IS a component name and changes; elsewhere it may not. The script rewrites it only under those two places |
| A name in a written text | `libs/viz_factory/tests/test_data/annotate_test.yaml:2: description: DECO-2 smoke test for annotate` | a description, a label or a comment: an author words it |
| A name that is also a recipe key | `libs/utils/src/utils/recipe_spec.yaml:95: labs: "a labs layer"`, `:94: facet_scales: ...` | a key of the recipe format shares the spelling of a component (`labs`, `guides`, `facet_scales`). The key stays |
| A name inside a formula or expression | none found in the shipped recipes (the script looks at the keys `expression`, `fun`, `formula`) | the risk exists for the text of `stat_function` and for `mutate` expressions |
| The two spellings | `scale_colour_manual` and `scale_color_manual` | the script keeps the spelling it finds and adds the prefix (Q4) |
| A name that decides whether a palette is added | `plot_config_resolver.py:732-736` | see section 6.3: this one is code, not text |

### 6.5 Risks the rename carries

- **R1 (science, reproducibility).** The conversion edits the recipe file, so `data_analysis_recipe_sha256` changes for every shipped recipe. To check, not to assume: saved sessions are keyed by it
  (the restore already warns "saved against another recipe version"); exported bundles hold old names and old fingerprints, and the import verifies four hashes (ADR-097). The data caches should stay valid
  (the tier keys leave out the plot specs, `rules_data_engine.md`): a test must show it. Needs your decision (Q1).
- **R2 (silent).** The sites of section 6.3: a missed prefix test changes a picture without a message. The picture test (step 0) is the protection.
- **R3.** The registry grows: about 267 components (191 + 31 exact twins + 30 gaps + 15 spellings).
- **R4.** Descriptions, help texts, docs and the Blueprint agent instructions quote names; a doc built from the registry follows, a hand-written one does not.
- **R5.** The 15 modified components that plotnine cannot put on a plot have no possible exact twin (section 2.2).


## 7. What an old name will show, and the plan

An old name is refused where it is written: at load (the checker), in the Blueprint form, and when the plot is built. Proposed text (like the Polars names):

> `geom_point` is the old name of `plotnine_geom_point` (renamed 2026-11-xx: every plotnine object now carries the prefix `plotnine_`).
> Convert your recipes: `<the migration command: a script to be written, not part of this audit>`

The "did you mean" must come from an explicit table `old name -> new name` (a constant like `REMOVED_ACTIONS` in `utils/action_names.py`), not from text similarity:
the current similarity (difflib, cut-off 0.6) finds `plotnine_geom_point` for `geom_point` but not `plotnine_labs` for `labs` (0.47).
The table is generated from the registry, and a test checks that every old name of the 191 is in it.

Plan, in order, each step a commit with tests; one builder and one reviewer at a time:

0. **Picture baseline, before anything changes.** A script renders every plot of every shipped recipe and gallery example and every `yaml_example`, and stores a hash of the picture
   (fixed seed, fixed size). It does not exist today (the golden baseline hashes tables, not pictures). Mutation check: change one default, see the hash move.
1. **One function for the shape of a name** (6.3), with the old names still working: tests green, pictures identical. This step carries the risk R2 on its own.
2. **Rename in the registry**: decorators, `wraps`, descriptions, the table `OLD_COMPONENT_NAMES`; prefix equals field, tested for all components (Eve's M108).
3. **Add the exact neighbours** (31) and, if decided, the gaps and spellings; each new exact component enters the audit test of this task (it proves it equals plotnine).
4. **The migration script** (to be written; dry run by default, `--apply`, idempotent, keeps comments, lists the hard cases with file and line, never guesses): runs on
   the 25 plot specs, pipelines, templates, retest, 37 gallery examples, the generated test recipes, and the documents' recipe snippets.
5. **Blueprint**: `_THEME_CHOICES`, agent instructions, help; test: the picker and the agent offer new names only.
6. **Docs**: the two component pages, the rationale, the authoring guide; the rule file proposal and the ADR-106 note (rule files only after your yes).
7. **Controls**: picture baseline identical for every shipped recipe and gallery example; prefix equals field; an old name is refused with the new name and the command, in the checker, the form
   and the build; a mutation check (rename one component back, see tests fail; let `startswith("geom_")` come back, see the guard test fail); the full headless suite; the browser tests; the golden check; `check_doc_links.py`;
   the UML check and the dependency index (the repository rules).

Tests to write for the rename itself: the old-to-new table covers all 191; prefix equals registry field; every shipped recipe converted loads with the checker and draws the same picture as before;
the converted recipes are stable when the script runs a second time; a recipe with an old name is refused with the exact text; no `startswith("geom_")`-like test is left in the code.

## 8. Questions only Eve can answer (each with a default)

- **Q1 (reproducibility).** A results bundle exported before the rename holds old names and the old recipe fingerprint. Options: (a) refuse it with the migration command, and say clearly that
  the converted recipe has a new fingerprint but the same data and picture (default); (b) the import converts it and records both fingerprints; (c) keep a read-only note in the bundle. Default (a).
- **Q2 (prefix rule).** `plotnine_` = exact, `modif_` = modified (same name as a plotnine object), `step_` = own (any name plotnine does not have: convenience, preset, setter). Options:
  (a) as stated, so prefix and registry field agree one to one (default); (b) the one-call conveniences (`facet_rows`, `guide_nrow` ...) become `modif_<their name>`, then the prefix says "changed" for a name that has no plotnine original.
- **Q3 (the 35 gaps).** Register them as `plotnine_` components (the pass-through ones are generated and tested by the audit): (a) all that need no extra package and are a layer or a scale: 30 (default); (b) only the 21 scale variants; (c) none, keep the list and the test.
  `geom_map` (geopandas), and the four labellers (a value, not a layer) stay listed under every option.
- **Q4 (two spellings).** plotnine has `scale_colour_manual` and `scale_color_manual`, `theme_grey` and `theme_gray`, `geom_bin2d` and `geom_bin_2d`. Options: (a) register both as separate components, each equal to plotnine (15 more; default, because
  "every true plotnine equivalent is `plotnine_<name>`"); (b) one spelling only, the other refused with "did you mean"; (c) a silent conversion of `colour` to `color` (not proposed: silent).
- **Q5 (names inside values).** `geom: geom_area` in the gallery taxonomy and `stat: stat_bin`, `position: position_identity` as parameter values. Default: they stay plotnine's names (they describe a plotnine object; they are not component calls). The `theme:` key of a plot spec and of `plot_defaults` changes (it is a component call).
- **Q6 (the 15 objects plotnine cannot add to a plot).** `element_*`, `position_*`, `guide_legend`, `guide_colorbar`, `guide_colourbar`. They become `modif_<name>` with no exact neighbour (it cannot exist). Option: also offer the plotnine way as a parameter of the component
  that takes it (for example `position: dodge` on a geom). Default: `modif_` only; the description says why.
- **Q7 (`guide_label`).** It fails on every use. Options: remove it now (default); rebuild; keep it renamed. Removing it first keeps a broken name out of the rename.
- **Q8 (the 4 facet setters and the one-call conveniences).** Only `theme_legend_position` is used by a shipped recipe. Options: (a) keep all 21 working own components as `step_` (default, nothing silently lost);
  (b) remove the 9 that the exact plotnine component already does (`facet_rows`, `facet_cols`, `coord_lims`, `guide_title`, `guide_ncol`, `guide_nrow`, `guide_reverse`, `guide_direction`, `guide_none`), fewer names to rename and document; (c) fold the four facet setters into parameters of `plotnine_facet_wrap` and `plotnine_facet_grid`.
- **Q9 (a function as a parameter, N28).** Not decided here. Today `fun_data` names a summary. Options for `fun_y`, `fun_ymin`, `fun_ymax`: (a) leave them out and document the `fun_data` names (default); (b) named summaries (`mean`, `median`, `min`, `max`, a quantile with its probability), each equal to the direct call, tested, recorded in the export; (c) both.
  Also: a text given to `labels` is read by plotnine as letters (found unchecked): add a check? Default yes.
- **Q10 (rule files).** The prefix rule goes into `rules_viz_factory.md` (sections 1, 2, 7). Only after your yes.

## 9. The table: old name -> new name for every component (generated)

Generated by the command of the top of this document (`report`; the table alone: `viz_rename_table.py table`). Columns: the old name; the new name; the family of the component (what kind of thing it is);
the registry field exact / modified / own, which decides the prefix; the prefix that follows. The new name is the proposal of question Q2 (default). The 22 own names are `step_` unless Q7 or Q8 removes them.

| old name | new name | family | registry field (exact / modified / own) | prefix that follows |
|---|---|---|---|---|
| `annotate` | `modif_annotate` | annotation | modified | `modif_` |
| `coord_cartesian` | `plotnine_coord_cartesian` | coord | exact | `plotnine_` |
| `coord_equal` | `plotnine_coord_equal` | coord | exact | `plotnine_` |
| `coord_fixed` | `plotnine_coord_fixed` | coord | exact | `plotnine_` |
| `coord_flip` | `plotnine_coord_flip` | coord | exact | `plotnine_` |
| `coord_lims` | `step_coord_lims` | coord | own | `step_` |
| `coord_trans` | `plotnine_coord_trans` | coord | exact | `plotnine_` |
| `element_blank` | `modif_element_blank` | element | modified | `modif_` |
| `element_line` | `modif_element_line` | element | modified | `modif_` |
| `element_rect` | `modif_element_rect` | element | modified | `modif_` |
| `element_text` | `modif_element_text` | element | modified | `modif_` |
| `facet_cols` | `step_facet_cols` | facet | own | `step_` |
| `facet_grid` | `modif_facet_grid` | facet | modified | `modif_` |
| `facet_labeller` | `step_facet_labeller` | facet | own | `step_` |
| `facet_margins` | `step_facet_margins` | facet | own | `step_` |
| `facet_null` | `plotnine_facet_null` | facet | exact | `plotnine_` |
| `facet_rows` | `step_facet_rows` | facet | own | `step_` |
| `facet_scales` | `step_facet_scales` | facet | own | `step_` |
| `facet_space` | `step_facet_space` | facet | own | `step_` |
| `facet_wrap` | `plotnine_facet_wrap` | facet | exact | `plotnine_` |
| `geom_abline` | `plotnine_geom_abline` | geom | exact | `plotnine_` |
| `geom_area` | `plotnine_geom_area` | geom | exact | `plotnine_` |
| `geom_bar` | `plotnine_geom_bar` | geom | exact | `plotnine_` |
| `geom_bin_2d` | `plotnine_geom_bin_2d` | geom | exact | `plotnine_` |
| `geom_blank` | `plotnine_geom_blank` | geom | exact | `plotnine_` |
| `geom_boxplot` | `plotnine_geom_boxplot` | geom | exact | `plotnine_` |
| `geom_col` | `plotnine_geom_col` | geom | exact | `plotnine_` |
| `geom_count` | `plotnine_geom_count` | geom | exact | `plotnine_` |
| `geom_crossbar` | `plotnine_geom_crossbar` | geom | exact | `plotnine_` |
| `geom_density` | `plotnine_geom_density` | geom | exact | `plotnine_` |
| `geom_density_2d` | `plotnine_geom_density_2d` | geom | exact | `plotnine_` |
| `geom_dotplot` | `plotnine_geom_dotplot` | geom | exact | `plotnine_` |
| `geom_errorbar` | `plotnine_geom_errorbar` | geom | exact | `plotnine_` |
| `geom_errorbarh` | `plotnine_geom_errorbarh` | geom | exact | `plotnine_` |
| `geom_freqpoly` | `plotnine_geom_freqpoly` | geom | exact | `plotnine_` |
| `geom_histogram` | `plotnine_geom_histogram` | geom | exact | `plotnine_` |
| `geom_hline` | `plotnine_geom_hline` | geom | exact | `plotnine_` |
| `geom_jitter` | `modif_geom_jitter` | geom | modified | `modif_` |
| `geom_label` | `plotnine_geom_label` | geom | exact | `plotnine_` |
| `geom_line` | `plotnine_geom_line` | geom | exact | `plotnine_` |
| `geom_linerange` | `plotnine_geom_linerange` | geom | exact | `plotnine_` |
| `geom_path` | `plotnine_geom_path` | geom | exact | `plotnine_` |
| `geom_point` | `plotnine_geom_point` | geom | exact | `plotnine_` |
| `geom_pointdensity` | `plotnine_geom_pointdensity` | geom | exact | `plotnine_` |
| `geom_pointrange` | `plotnine_geom_pointrange` | geom | exact | `plotnine_` |
| `geom_polygon` | `plotnine_geom_polygon` | geom | exact | `plotnine_` |
| `geom_qq` | `plotnine_geom_qq` | geom | exact | `plotnine_` |
| `geom_qq_line` | `plotnine_geom_qq_line` | geom | exact | `plotnine_` |
| `geom_quantile` | `plotnine_geom_quantile` | geom | exact | `plotnine_` |
| `geom_raster` | `plotnine_geom_raster` | geom | exact | `plotnine_` |
| `geom_rect` | `plotnine_geom_rect` | geom | exact | `plotnine_` |
| `geom_ribbon` | `plotnine_geom_ribbon` | geom | exact | `plotnine_` |
| `geom_rug` | `plotnine_geom_rug` | geom | exact | `plotnine_` |
| `geom_segment` | `plotnine_geom_segment` | geom | exact | `plotnine_` |
| `geom_sina` | `modif_geom_sina` | geom | modified | `modif_` |
| `geom_smooth` | `plotnine_geom_smooth` | geom | exact | `plotnine_` |
| `geom_spoke` | `plotnine_geom_spoke` | geom | exact | `plotnine_` |
| `geom_step` | `plotnine_geom_step` | geom | exact | `plotnine_` |
| `geom_text` | `plotnine_geom_text` | geom | exact | `plotnine_` |
| `geom_tile` | `plotnine_geom_tile` | geom | exact | `plotnine_` |
| `geom_violin` | `plotnine_geom_violin` | geom | exact | `plotnine_` |
| `geom_vline` | `plotnine_geom_vline` | geom | exact | `plotnine_` |
| `ggtitle` | `modif_ggtitle` | label | modified | `modif_` |
| `guide_colorbar` | `modif_guide_colorbar` | guide | modified | `modif_` |
| `guide_colourbar` | `modif_guide_colourbar` | guide | modified | `modif_` |
| `guide_direction` | `step_guide_direction` | guide | own | `step_` |
| `guide_label` | `step_guide_label` | guide | own | `step_` |
| `guide_legend` | `modif_guide_legend` | guide | modified | `modif_` |
| `guide_ncol` | `step_guide_ncol` | guide | own | `step_` |
| `guide_none` | `step_guide_none` | guide | own | `step_` |
| `guide_nrow` | `step_guide_nrow` | guide | own | `step_` |
| `guide_reverse` | `step_guide_reverse` | guide | own | `step_` |
| `guide_title` | `step_guide_title` | guide | own | `step_` |
| `guides` | `modif_guides` | guide | modified | `modif_` |
| `labs` | `plotnine_labs` | label | exact | `plotnine_` |
| `position_dodge` | `modif_position_dodge` | position | modified | `modif_` |
| `position_dodge2` | `modif_position_dodge2` | position | modified | `modif_` |
| `position_fill` | `modif_position_fill` | position | modified | `modif_` |
| `position_identity` | `modif_position_identity` | position | modified | `modif_` |
| `position_jitter` | `modif_position_jitter` | position | modified | `modif_` |
| `position_jitterdodge` | `modif_position_jitterdodge` | position | modified | `modif_` |
| `position_nudge` | `modif_position_nudge` | position | modified | `modif_` |
| `position_stack` | `modif_position_stack` | position | modified | `modif_` |
| `scale_alpha` | `modif_scale_alpha` | scale | modified | `modif_` |
| `scale_alpha_continuous` | `plotnine_scale_alpha_continuous` | scale | exact | `plotnine_` |
| `scale_alpha_discrete` | `plotnine_scale_alpha_discrete` | scale | exact | `plotnine_` |
| `scale_alpha_identity` | `plotnine_scale_alpha_identity` | scale | exact | `plotnine_` |
| `scale_alpha_manual` | `plotnine_scale_alpha_manual` | scale | exact | `plotnine_` |
| `scale_color_brewer` | `plotnine_scale_color_brewer` | scale | exact | `plotnine_` |
| `scale_color_cmap` | `plotnine_scale_color_cmap` | scale | exact | `plotnine_` |
| `scale_color_cmap_d` | `plotnine_scale_color_cmap_d` | scale | exact | `plotnine_` |
| `scale_color_continuous` | `plotnine_scale_color_continuous` | scale | exact | `plotnine_` |
| `scale_color_discrete` | `plotnine_scale_color_discrete` | scale | exact | `plotnine_` |
| `scale_color_distiller` | `plotnine_scale_color_distiller` | scale | exact | `plotnine_` |
| `scale_color_gradient` | `plotnine_scale_color_gradient` | scale | exact | `plotnine_` |
| `scale_color_gradient2` | `plotnine_scale_color_gradient2` | scale | exact | `plotnine_` |
| `scale_color_gradientn` | `plotnine_scale_color_gradientn` | scale | exact | `plotnine_` |
| `scale_color_hue` | `modif_scale_color_hue` | scale | modified | `modif_` |
| `scale_color_identity` | `plotnine_scale_color_identity` | scale | exact | `plotnine_` |
| `scale_color_manual` | `plotnine_scale_color_manual` | scale | exact | `plotnine_` |
| `scale_color_viridis_c` | `step_scale_color_viridis_c` | scale | own | `step_` |
| `scale_color_viridis_d` | `step_scale_color_viridis_d` | scale | own | `step_` |
| `scale_fill_brewer` | `plotnine_scale_fill_brewer` | scale | exact | `plotnine_` |
| `scale_fill_cmap` | `plotnine_scale_fill_cmap` | scale | exact | `plotnine_` |
| `scale_fill_cmap_d` | `plotnine_scale_fill_cmap_d` | scale | exact | `plotnine_` |
| `scale_fill_continuous` | `plotnine_scale_fill_continuous` | scale | exact | `plotnine_` |
| `scale_fill_discrete` | `plotnine_scale_fill_discrete` | scale | exact | `plotnine_` |
| `scale_fill_distiller` | `plotnine_scale_fill_distiller` | scale | exact | `plotnine_` |
| `scale_fill_gradient` | `plotnine_scale_fill_gradient` | scale | exact | `plotnine_` |
| `scale_fill_gradient2` | `plotnine_scale_fill_gradient2` | scale | exact | `plotnine_` |
| `scale_fill_gradientn` | `plotnine_scale_fill_gradientn` | scale | exact | `plotnine_` |
| `scale_fill_hue` | `modif_scale_fill_hue` | scale | modified | `modif_` |
| `scale_fill_identity` | `plotnine_scale_fill_identity` | scale | exact | `plotnine_` |
| `scale_fill_manual` | `plotnine_scale_fill_manual` | scale | exact | `plotnine_` |
| `scale_fill_viridis_c` | `step_scale_fill_viridis_c` | scale | own | `step_` |
| `scale_fill_viridis_d` | `step_scale_fill_viridis_d` | scale | own | `step_` |
| `scale_linetype` | `plotnine_scale_linetype` | scale | exact | `plotnine_` |
| `scale_linetype_discrete` | `plotnine_scale_linetype_discrete` | scale | exact | `plotnine_` |
| `scale_linetype_identity` | `plotnine_scale_linetype_identity` | scale | exact | `plotnine_` |
| `scale_linetype_manual` | `plotnine_scale_linetype_manual` | scale | exact | `plotnine_` |
| `scale_shape` | `plotnine_scale_shape` | scale | exact | `plotnine_` |
| `scale_shape_discrete` | `plotnine_scale_shape_discrete` | scale | exact | `plotnine_` |
| `scale_shape_identity` | `plotnine_scale_shape_identity` | scale | exact | `plotnine_` |
| `scale_shape_manual` | `plotnine_scale_shape_manual` | scale | exact | `plotnine_` |
| `scale_size` | `modif_scale_size` | scale | modified | `modif_` |
| `scale_size_area` | `modif_scale_size_area` | scale | modified | `modif_` |
| `scale_size_continuous` | `plotnine_scale_size_continuous` | scale | exact | `plotnine_` |
| `scale_size_discrete` | `plotnine_scale_size_discrete` | scale | exact | `plotnine_` |
| `scale_size_identity` | `plotnine_scale_size_identity` | scale | exact | `plotnine_` |
| `scale_size_manual` | `plotnine_scale_size_manual` | scale | exact | `plotnine_` |
| `scale_stroke_continuous` | `plotnine_scale_stroke_continuous` | scale | exact | `plotnine_` |
| `scale_stroke_identity` | `plotnine_scale_stroke_identity` | scale | exact | `plotnine_` |
| `scale_x_continuous` | `modif_scale_x_continuous` | scale | modified | `modif_` |
| `scale_x_date` | `plotnine_scale_x_date` | scale | exact | `plotnine_` |
| `scale_x_datetime` | `plotnine_scale_x_datetime` | scale | exact | `plotnine_` |
| `scale_x_discrete` | `plotnine_scale_x_discrete` | scale | exact | `plotnine_` |
| `scale_x_log10` | `plotnine_scale_x_log10` | scale | exact | `plotnine_` |
| `scale_x_reverse` | `plotnine_scale_x_reverse` | scale | exact | `plotnine_` |
| `scale_x_sqrt` | `plotnine_scale_x_sqrt` | scale | exact | `plotnine_` |
| `scale_x_symlog` | `plotnine_scale_x_symlog` | scale | exact | `plotnine_` |
| `scale_x_timedelta` | `plotnine_scale_x_timedelta` | scale | exact | `plotnine_` |
| `scale_y_continuous` | `modif_scale_y_continuous` | scale | modified | `modif_` |
| `scale_y_date` | `plotnine_scale_y_date` | scale | exact | `plotnine_` |
| `scale_y_datetime` | `plotnine_scale_y_datetime` | scale | exact | `plotnine_` |
| `scale_y_discrete` | `plotnine_scale_y_discrete` | scale | exact | `plotnine_` |
| `scale_y_log10` | `plotnine_scale_y_log10` | scale | exact | `plotnine_` |
| `scale_y_reverse` | `plotnine_scale_y_reverse` | scale | exact | `plotnine_` |
| `scale_y_sqrt` | `plotnine_scale_y_sqrt` | scale | exact | `plotnine_` |
| `scale_y_symlog` | `plotnine_scale_y_symlog` | scale | exact | `plotnine_` |
| `scale_y_timedelta` | `plotnine_scale_y_timedelta` | scale | exact | `plotnine_` |
| `stat_bin` | `plotnine_stat_bin` | stat | exact | `plotnine_` |
| `stat_bin_2d` | `plotnine_stat_bin_2d` | stat | exact | `plotnine_` |
| `stat_bindot` | `plotnine_stat_bindot` | stat | exact | `plotnine_` |
| `stat_boxplot` | `plotnine_stat_boxplot` | stat | exact | `plotnine_` |
| `stat_count` | `plotnine_stat_count` | stat | exact | `plotnine_` |
| `stat_density` | `plotnine_stat_density` | stat | exact | `plotnine_` |
| `stat_density_2d` | `plotnine_stat_density_2d` | stat | exact | `plotnine_` |
| `stat_ecdf` | `plotnine_stat_ecdf` | stat | exact | `plotnine_` |
| `stat_ellipse` | `plotnine_stat_ellipse` | stat | exact | `plotnine_` |
| `stat_function` | `modif_stat_function` | stat | modified | `modif_` |
| `stat_hull` | `plotnine_stat_hull` | stat | exact | `plotnine_` |
| `stat_identity` | `modif_stat_identity` | stat | modified | `modif_` |
| `stat_qq` | `plotnine_stat_qq` | stat | exact | `plotnine_` |
| `stat_qq_line` | `plotnine_stat_qq_line` | stat | exact | `plotnine_` |
| `stat_quantile` | `plotnine_stat_quantile` | stat | exact | `plotnine_` |
| `stat_sina` | `modif_stat_sina` | stat | modified | `modif_` |
| `stat_smooth` | `plotnine_stat_smooth` | stat | exact | `plotnine_` |
| `stat_sum` | `plotnine_stat_sum` | stat | exact | `plotnine_` |
| `stat_summary` | `plotnine_stat_summary` | stat | exact | `plotnine_` |
| `stat_summary_bin` | `plotnine_stat_summary_bin` | stat | exact | `plotnine_` |
| `stat_unique` | `plotnine_stat_unique` | stat | exact | `plotnine_` |
| `stat_ydensity` | `plotnine_stat_ydensity` | stat | exact | `plotnine_` |
| `theme_538` | `modif_theme_538` | theme | modified | `modif_` |
| `theme_bw` | `modif_theme_bw` | theme | modified | `modif_` |
| `theme_classic` | `modif_theme_classic` | theme | modified | `modif_` |
| `theme_custom` | `step_theme_custom` | theme | own | `step_` |
| `theme_dark` | `modif_theme_dark` | theme | modified | `modif_` |
| `theme_dashboard` | `step_theme_dashboard` | theme | own | `step_` |
| `theme_gray` | `modif_theme_gray` | theme | modified | `modif_` |
| `theme_legend_position` | `step_theme_legend_position` | theme | own | `step_` |
| `theme_light` | `modif_theme_light` | theme | modified | `modif_` |
| `theme_linedraw` | `modif_theme_linedraw` | theme | modified | `modif_` |
| `theme_matplotlib` | `modif_theme_matplotlib` | theme | modified | `modif_` |
| `theme_minimal` | `modif_theme_minimal` | theme | modified | `modif_` |
| `theme_publication` | `step_theme_publication` | theme | own | `step_` |
| `theme_seaborn` | `modif_theme_seaborn` | theme | modified | `modif_` |
| `theme_tufte` | `modif_theme_tufte` | theme | modified | `modif_` |
| `theme_void` | `modif_theme_void` | theme | modified | `modif_` |
| `theme_xkcd` | `modif_theme_xkcd` | theme | modified | `modif_` |
| `xlab` | `modif_xlab` | label | modified | `modif_` |
| `ylab` | `modif_ylab` | label | modified | `modif_` |

191 components: 123 exact -> `plotnine_`, 46 modified -> `modif_`, 22 own -> `step_`
