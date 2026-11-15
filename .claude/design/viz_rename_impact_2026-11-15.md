# Plot components: audit against plotnine, and the impact of the rename (2026-11-15)

Task VIZ-REGISTRY-AUDIT-1. Status: AUDIT AND PREPARATION ONLY. Nothing is renamed. The rename follows Eve's decision of 2026-11-15
(ADR-106 note V1-B, channel M106-M108) and waits for her answers in section 7.
Evidence: `libs/viz_factory/tests/test_registry_audit_vs_plotnine.py` (309 tests, runs plotnine 0.15.4) and
`assets/scripts/viz_rename_table.py` (table and dry count). Every number below comes from one of the two.

Words used: a *component* is one name a recipe can write in `layers:` (for example `geom_point`, `theme_bw`).
*exact* means the component only passes its parameters to the plotnine object of the same name. *modified* means it adds or changes something.
*own* means plotnine has no object of that name.

## 1. What changes for a recipe maker

1. Every component name in a recipe gets a prefix. `geom_point` becomes `plotnine_geom_point`; `theme_bw` becomes `modif_theme_bw`;
   `theme_dashboard` becomes `step_theme_dashboard`. The prefix tells you at a glance whether it is exactly plotnine (`plotnine_`),
   plotnine with a documented change (`modif_`), or the project's own (`step_`).
2. The `theme:` key of a plot and of `plot_defaults` also holds a component name, so it changes too.
3. An old name is refused. The message says the new name and gives the command that converts your recipes.
   There is no period in which both spellings work (Eve, 2026-11-15: "we need to detect all errors").
4. The pictures do not change. The conversion only rewrites names. A test must show this before the rename is accepted (section 6, step 0).
5. A recipe that was exported before the change (a results bundle) contains old names. It runs only after it is converted, and
   the conversion changes the recipe file, so its recorded fingerprint (`data_analysis_recipe_sha256`) changes too (section 5, risk R1).
   This is the one point that touches reproducibility; it needs your decision (question Q1).

## 2. The audit, in numbers (plotnine 0.15.4, run)

| What | Count |
|---|---|
| Public plotnine objects (`plotnine.__all__`) | 232 |
| Registered components | 191 (169 have a plotnine name, 22 have none) |
| Exact / modified / own | 123 / 46 / 22 |
| Plotnine names not registered | 63 |
| ... of which not components of a plot (aes, ggplot, ggsave, qplot, session theme setters, the mapping expressions) | 13 |
| ... of which the other spelling of a registered component (`scale_colour_*` for `scale_color_*`, `geom_bin2d`, `stat_bin2d`, `theme_grey`) | 15 |
| ... of which real gaps | 35 |
| Exact components judged by running (example and no parameter) | 123 (122 drawn and compared picture by picture; `geom_smooth` structure only, it needs `scikit-misc` to draw) |
| Differences in parameters, defaults or the object built, exact components | 0 |
| Parameters of exact components | 1863, all read from plotnine |
| Defaults plotnine has that the form cannot show | 54: 36 `nan`, 14 `after_stat(...)`, 8 `{}`, 4 `(-inf, inf)` (the 366 `None` defaults mean "absent") |
| Parameters plotnine accepts that a recipe cannot write (listed with a reason in the registry) | `data`, `mapping` (59 layers each), `rescaler`, `oob` (31 scales each), `fun_y`, `fun_ymin`, `fun_ymax` (2 each) |
| Modified components without their exact plotnine one next to them | 46 of 46 |

Plain reading: the exact components are exact. The work is naming, the gaps, and the modified ones.

### 2.1 The 35 real gaps (plotnine components no registered name covers)

- Scales, 21: the `datetime`, `ordinal`, `desaturate`, `gray` and `grey` variants for `color`, `colour` and `fill` (15); `scale_alpha_datetime`, `scale_alpha_ordinal`,
  `scale_size_datetime`, `scale_size_ordinal` (4); `scale_size_radius`, `scale_stroke` (2).
- Layers, settings and helpers, 14: `annotation_logticks`, `annotation_stripes`, `expand_limits`, `lims`, `xlim`, `ylim`, `theme`, `watermark`, `stat_pointdensity`,
  `geom_map` (needs `geopandas`, not installed), and the four labellers `label_both`, `label_context`, `label_value`, `labeller`
  (a recipe writes their names as the value of the facet parameter `labeller`, which works; see section 4).
- The exact list is `KNOWN_MISSING` in the test. A new plotnine object at an upgrade fails the test until it is classified.

### 2.2 The 46 modified components, run

| Group | Count | Meaning |
|---|---|---|
| Plotnine cannot add this object to a plot at all (`plot + element_text()` fails) | 15: `element_blank`, `element_line`, `element_rect`, `element_text`, `position_*` (8), `guide_legend`, `guide_colorbar`, `guide_colourbar` | The component adapts an object to a plot step (`target` names the theme setting, `mapping` names the aesthetic, the position goes to the last layer). An exact plotnine step next to it cannot exist. |
| Equal to plotnine when the change is not used | 29: `annotate`, `facet_grid`, `ggtitle`, `guides`, `xlab`, `ylab`, `geom_jitter`, `geom_sina`, `stat_sina`, 5 scales, `scale_x_continuous`, `scale_y_continuous`, 13 themes | The change is a seed set by the factory (3), a list turned into a tuple (5), `breaks_integer` (2), extra theme settings (13), a formula for `facets` (1), a clearer refusal when a key is missing (5: `annotate`, `ggtitle`, `xlab`, `ylab`, `guides`). |
| Different | 2: `stat_function` (a text function), `stat_identity` (does nothing, ignores its parameters) | |

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
a project addition and a decision of yours (N28, not decided here). One unchecked path found: `labels` given as a text.

## 5. Impact of the rename (dry run)

Counted by `assets/scripts/viz_rename_table.py count` on the tracked files of this branch. A line is counted once per component name on it.
"Decided alone" means a recipe line `name: <component>` (also the flow form `{name: <component>, ...}`) that a script can rewrite with no doubt.

| group of files | files | occurrences | decided alone (recipe `name:` line) | to read or decide |
|---|---|---|---|---|
| viz library code (registration and name logic) | 16 | 1399 | 0 | 1399 |
| viz library tests | 221 | 1332 | 408 | 924 |
| history: logs, archives (kept as they were) | 27 | 723 | 0 | 723 |
| records: design, knowledge, tasks, workflows | 29 | 430 | 24 | 406 |
| other tests | 64 | 373 | 48 | 325 |
| docs pages and READMEs | 13 | 304 | 4 | 300 |
| gallery recipes and index | 70 | 249 | 87 | 162 |
| scripts | 5 | 132 | 0 | 132 |
| plot spec files | 25 | 65 | 62 | 3 |
| other code (libs, app) | 7 | 43 | 0 | 43 |
| rule files (listed, never edited by the rename) | 5 | 38 | 0 | 38 |
| pipeline recipes (outside plots/) | 6 | 13 | 11 | 2 |
| Blueprint pickers, forms and the agent tool | 1 | 8 | 0 | 8 |
| template recipes | 4 | 8 | 6 | 2 |
| retest recipes | 4 | 5 | 5 | 0 |
| TOTAL | 497 | 5122 | 655 | 4467 |

How to read it: the recipe files that a person writes (plot specs, pipelines, templates, retest, gallery) are almost all "decided alone".
Code, tests and prose are not: each line there must be read.

Files that name a component, by group (the 5122 occurrences are in 497 files; the dry run is repeatable):

- Plot spec files (25 files, 65 occurrences, 62 decided alone). The 3 others are `theme:` keys, which are component names (decided with context).
- Pipeline recipes (6 files), template recipes (4), retest recipes (4): 26 occurrences, 22 decided alone.
- Gallery recipes and index (70 files, 249 occurrences): 87 recipe lines decided alone; 54 are the field `geom:` of `gallery_index.json`; the other 108 are text
  (descriptions, comments, the guidance note of each example). Many examples use the flow form `{name: geom_area, params: ...}`, which the script reads.
- Shipped recipes use 39 of the 191 components in 171 places: 27 exact, 11 modified, 1 own (`theme_legend_position`). The 152 other components are used only by tests and the form.
- Blueprint pickers and forms: they read the registry (`schema_registry.py`), so the picker and the forms follow the new names by themselves.
  What is hand-written: the list `_THEME_CHOICES` in `app/handlers/blueprint_handlers.py` (5 names), `app/handlers/home_theater.py` (4 mentions),
  the agent tool `libs/blueprint_arch/src/blueprint_arch/agent_tools.py` and `agent_context.py`, and the agent instructions `config/ui/agents/blueprint_default.md` (the 8 occurrences counted).
  The agent asks the registry for the list of components; to verify, not to guess: a test must show it offers only new names.
- Docs: `docs/workflows/visualisation_factory.qmd` (97), `docs/appendix/viz_factory_components.qmd` (94), `docs/appendix/viz_factory_rationale.qmd` (22),
  `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd` (19), `docs/user_guide/reproducible_plots.qmd` (9) and 8 others: 13 files, 304 occurrences.
- Tests: viz library tests 221 files (1332 occurrences; many are the generated recipes in `libs/viz_factory/tests/test_data/`, 218 files), other tests 64 files (373).
- Library code: `libs/viz_factory/src` 16 files, 1399 occurrences (each registration, the descriptions, the name logic of section 5.2).
- Rule files: listed, never edited by the rename, a proposal after your yes: `.claude/rules/rules_viz_factory.md` (13 occurrences, sections 1, 2, 4, 6, 7),
  `rules_data_analysis_recipe_structure.md` (18), `rules_gallery_standards.md` (3), `rules_documentation_aesthetics.md` (2), `rules_agent_role_bioscientist.md` (4),
  `rules_code_quality.md`, `rules_test_lab.md`, `workspace_standard.md` (1 each, the words `labs` or `annotate`).
- History (logs, archives, old conversations): 27 files, 723 occurrences. Kept as they were; they describe the past.

### 5.1 What the script cannot decide alone (examples)

| Kind | Example | Why it needs a person |
|---|---|---|
| A component name used as a parameter VALUE | `libs/viz_factory/tests/test_data/stat_bin_test.yaml:12: stat: stat_bin`; `.../position_identity_test.yaml:11: position: position_identity` | It is plotnine's own object passed to a layer, not a component call. Proposal: it stays (question Q5). |
| The same, in the gallery index and the plot taxonomy | `assets/gallery_data/gallery_index.json:22: "geom": "geom_area"` (54 lines) | The taxonomy says "the exact plotnine function name". Proposal: it stays plotnine's name (Q5). |
| A `theme:` key | `app/tests/equality/recipes/.../multi_resistance_by_country.yaml:2: theme: theme_light` | In a plot spec or in `plot_defaults` it IS a component name and changes; in a deployment file or a document it may not. The script rewrites it only under `plots/` and `plot_defaults`. |
| A name in a written text | `libs/viz_factory/tests/test_data/annotate_test.yaml:2: description: DECO-2 smoke test for annotate` | A description, label or comment: an author decides; the script lists it. |
| A name that is also a recipe key | `libs/utils/src/utils/recipe_spec.yaml:95: labs: "a labs layer"`, `:94: facet_scales: ...`, `:96: coordinate_flip: ...` | A key of the recipe format shares the spelling of a component (`labs`, `guides`, `facet_scales`). The key stays; only the value naming the layer follows. |
| A name inside code that works by prefix | `libs/viz_factory/src/viz_factory/plot_config_resolver.py:130-160` (`name.startswith("geom_")`, `"scale_fill_"`, ...), `libs/utils/src/utils/recipe_check.py:930` | Not a name: a rule on the shape of names. See 5.2. |
| A name inside a palette | `plot_config_resolver.py:728-742` decides "the recipe already declares a `scale_fill_*`, so no palette is injected" by prefix | After the rename `plotnine_scale_fill_manual` no longer starts with `scale_fill_`, the palette would be added ON TOP of the user's own scale, silently. This is a bug the rename would create. |
| A name inside a formula or expression | none found in shipped recipes (the script looks at keys `expression`, `fun`, `formula`) | The risk exists for `stat_function` texts and `mutate` expressions; the script reports any it finds. |
| A name in a Python string or list | `app/handlers/blueprint_handlers.py:1801: _THEME_CHOICES = ["theme_light", "theme_bw", ...]`; 1475 quoted names in tests and code | Registrations, lists and assertions: read each one. The 581 calls `p9.geom_bar(...)` and imports of plotnine are plotnine's own names and stay. |
| The two spellings | `scale_colour_manual` vs `scale_color_manual` | A recipe may have used the one that is registered; the script keeps the spelling it finds and adds the prefix (Q4). |

### 5.2 Name logic that must change first (code that reads the shape of a name)

The prefix `plotnine_` breaks every test of the form "starts with `geom_`". Places found:
`plot_config_resolver.py` (lines 130 to 160 and 313, 656, 719, 732-737: which layers stack, which one replaces which, theme, facet, scale families),
`ALWAYS_RANDOM`, `BATCHED_COMPONENTS` (`element_text`), `FACTORY_NAMED_COMPONENTS`, `FACET_SETTINGS` (4 names), `is_partial_theme`,
`libs/utils/src/utils/random_layers.py` (50, 55: a position or stat written with its plotnine prefix), `libs/utils/src/utils/recipe_check.py:930` (`has_geom`),
`plot_config_resolver.py` (palette guard, lines 728-742), and the test `derive_kind` in `test_component_plotnine_field.py`.
One function `component_family(name)` that strips the prefix and returns `geom`, `stat`, `scale_fill`, ... replaces them all; a test fails if a `startswith("geom_")` remains.

### 5.3 Risks the rename carries

- **R1 (science, reproducibility).** The conversion edits the recipe file, so `data_analysis_recipe_sha256` changes for every shipped recipe. Effects to check, not guessed:
  saved sessions are keyed by it (the restore already warns "saved against another recipe version"); exported bundles hold old names and old fingerprints, and the import
  verifies four hashes (ADR-097). The data caches should stay valid (tier keys exclude the plot specs, `rules_data_engine.md`): a test must show it.
  A bundle exported before the rename: import refuses the old names with the migration command; after migration the file hash differs from the one recorded. Needs your decision (Q1).
- **R2 (silent).** The palette guard and the layer replacement rules (5.2): a missed prefix test changes a picture without a message. The picture test (step 0) is the protection.
- **R3.** The registry grows: 31 exact neighbours of modified components, and the gaps if you register them (Q3, Q4): about 267 components (191 + 31 exact neighbours + 30 gaps + 15 spellings).
- **R4.** Descriptions, help texts, docs and the Blueprint agent instructions quote names; a doc built from the registry follows, a hand-written one does not (`check_doc_links.py` does not see names).
- **R5.** The 15 modified components that plotnine cannot add to a plot have no possible exact neighbour (section 2.2).

## 6. What an old name will show, and the plan

An old name is refused where it is written: at load (the checker), in the Blueprint form, and when the plot is built. Proposed text (like the Polars names):

> `geom_point` is the old name of `plotnine_geom_point` (renamed 2026-11-xx: every plotnine object now carries the prefix `plotnine_`).
> Convert your recipes: `./.venv/bin/python assets/scripts/migrate_plot_names.py --apply <recipe folder>`

The "did you mean" must come from an explicit table `old name -> new name` (a constant like `REMOVED_ACTIONS` in `utils/action_names.py`), not from text similarity:
the current similarity (difflib, cut-off 0.6) finds `plotnine_geom_point` for `geom_point` but not `plotnine_labs` for `labs` (0.47).
The table is generated from the registry, and a test checks that every old name of the 191 is in it.

Plan, in order, each step a commit with tests; one builder and one reviewer at a time:

0. **Picture baseline, before anything changes.** A script renders every plot of every shipped recipe and gallery example and every `yaml_example`, and stores a hash of the picture
   (fixed seed, fixed size). It does not exist today (the golden baseline hashes tables, not pictures). Mutation check: change one default, see the hash move.
1. **One function for the shape of a name** (5.2), with the old names still working: tests green, pictures identical. This step carries the risk R2 on its own.
2. **Rename in the registry**: decorators, `wraps`, descriptions, the table `OLD_COMPONENT_NAMES`; prefix equals field, tested for all components (Eve's M108).
3. **Add the exact neighbours** (31) and, if decided, the gaps and spellings; each new exact component enters the audit test of this task (it proves it equals plotnine).
4. **The migration script** `assets/scripts/migrate_plot_names.py` (dry run by default, `--apply`, idempotent, keeps comments, lists the hard cases with file and line, never guesses): runs on
   the 25 plot specs, pipelines, templates, retest, 37 gallery examples, the generated test recipes, and the documents' recipe snippets.
5. **Blueprint**: `_THEME_CHOICES`, agent instructions, help; test: the picker and the agent offer new names only.
6. **Docs**: the two component pages, the rationale, the authoring guide; the rule file proposal and the ADR-106 note (rule files only after your yes).
7. **Controls**: picture baseline identical for every shipped recipe and gallery example; prefix equals field; an old name is refused with the new name and the command, in the checker, the form
   and the build; a mutation check (rename one component back, see tests fail; let `startswith("geom_")` come back, see the guard test fail); the full headless suite; the browser tests; the golden check; `check_doc_links.py`;
   the UML check and the dependency index (the repository rules).

Tests to write for the rename itself: the old-to-new table covers all 191; prefix equals registry field; every shipped recipe converted loads with the checker and draws the same picture as before;
the converted recipes are stable when the script runs a second time; a recipe with an old name is refused with the exact text; no `startswith("geom_")`-like test is left in the code.

## 7. Questions only Eve can answer (each with a default)

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

## 8. The table: old name -> new name for every component (generated)

Generated by `./.venv/bin/python assets/scripts/viz_rename_table.py table`. The new name is the proposal of question Q2 (default). The 22 own names are `step_` unless Q7 or Q8 removes them.

| old name | new name | class | registry field |
|---|---|---|---|
| `annotate` | `modif_annotate` | annotation | modified |
| `coord_cartesian` | `plotnine_coord_cartesian` | coord | exact |
| `coord_equal` | `plotnine_coord_equal` | coord | exact |
| `coord_fixed` | `plotnine_coord_fixed` | coord | exact |
| `coord_flip` | `plotnine_coord_flip` | coord | exact |
| `coord_lims` | `step_coord_lims` | coord | own |
| `coord_trans` | `plotnine_coord_trans` | coord | exact |
| `element_blank` | `modif_element_blank` | element | modified |
| `element_line` | `modif_element_line` | element | modified |
| `element_rect` | `modif_element_rect` | element | modified |
| `element_text` | `modif_element_text` | element | modified |
| `facet_cols` | `step_facet_cols` | facet | own |
| `facet_grid` | `modif_facet_grid` | facet | modified |
| `facet_labeller` | `step_facet_labeller` | facet | own |
| `facet_margins` | `step_facet_margins` | facet | own |
| `facet_null` | `plotnine_facet_null` | facet | exact |
| `facet_rows` | `step_facet_rows` | facet | own |
| `facet_scales` | `step_facet_scales` | facet | own |
| `facet_space` | `step_facet_space` | facet | own |
| `facet_wrap` | `plotnine_facet_wrap` | facet | exact |
| `geom_abline` | `plotnine_geom_abline` | geom | exact |
| `geom_area` | `plotnine_geom_area` | geom | exact |
| `geom_bar` | `plotnine_geom_bar` | geom | exact |
| `geom_bin_2d` | `plotnine_geom_bin_2d` | geom | exact |
| `geom_blank` | `plotnine_geom_blank` | geom | exact |
| `geom_boxplot` | `plotnine_geom_boxplot` | geom | exact |
| `geom_col` | `plotnine_geom_col` | geom | exact |
| `geom_count` | `plotnine_geom_count` | geom | exact |
| `geom_crossbar` | `plotnine_geom_crossbar` | geom | exact |
| `geom_density` | `plotnine_geom_density` | geom | exact |
| `geom_density_2d` | `plotnine_geom_density_2d` | geom | exact |
| `geom_dotplot` | `plotnine_geom_dotplot` | geom | exact |
| `geom_errorbar` | `plotnine_geom_errorbar` | geom | exact |
| `geom_errorbarh` | `plotnine_geom_errorbarh` | geom | exact |
| `geom_freqpoly` | `plotnine_geom_freqpoly` | geom | exact |
| `geom_histogram` | `plotnine_geom_histogram` | geom | exact |
| `geom_hline` | `plotnine_geom_hline` | geom | exact |
| `geom_jitter` | `modif_geom_jitter` | geom | modified |
| `geom_label` | `plotnine_geom_label` | geom | exact |
| `geom_line` | `plotnine_geom_line` | geom | exact |
| `geom_linerange` | `plotnine_geom_linerange` | geom | exact |
| `geom_path` | `plotnine_geom_path` | geom | exact |
| `geom_point` | `plotnine_geom_point` | geom | exact |
| `geom_pointdensity` | `plotnine_geom_pointdensity` | geom | exact |
| `geom_pointrange` | `plotnine_geom_pointrange` | geom | exact |
| `geom_polygon` | `plotnine_geom_polygon` | geom | exact |
| `geom_qq` | `plotnine_geom_qq` | geom | exact |
| `geom_qq_line` | `plotnine_geom_qq_line` | geom | exact |
| `geom_quantile` | `plotnine_geom_quantile` | geom | exact |
| `geom_raster` | `plotnine_geom_raster` | geom | exact |
| `geom_rect` | `plotnine_geom_rect` | geom | exact |
| `geom_ribbon` | `plotnine_geom_ribbon` | geom | exact |
| `geom_rug` | `plotnine_geom_rug` | geom | exact |
| `geom_segment` | `plotnine_geom_segment` | geom | exact |
| `geom_sina` | `modif_geom_sina` | geom | modified |
| `geom_smooth` | `plotnine_geom_smooth` | geom | exact |
| `geom_spoke` | `plotnine_geom_spoke` | geom | exact |
| `geom_step` | `plotnine_geom_step` | geom | exact |
| `geom_text` | `plotnine_geom_text` | geom | exact |
| `geom_tile` | `plotnine_geom_tile` | geom | exact |
| `geom_violin` | `plotnine_geom_violin` | geom | exact |
| `geom_vline` | `plotnine_geom_vline` | geom | exact |
| `ggtitle` | `modif_ggtitle` | label | modified |
| `guide_colorbar` | `modif_guide_colorbar` | guide | modified |
| `guide_colourbar` | `modif_guide_colourbar` | guide | modified |
| `guide_direction` | `step_guide_direction` | guide | own |
| `guide_label` | `step_guide_label` | guide | own |
| `guide_legend` | `modif_guide_legend` | guide | modified |
| `guide_ncol` | `step_guide_ncol` | guide | own |
| `guide_none` | `step_guide_none` | guide | own |
| `guide_nrow` | `step_guide_nrow` | guide | own |
| `guide_reverse` | `step_guide_reverse` | guide | own |
| `guide_title` | `step_guide_title` | guide | own |
| `guides` | `modif_guides` | guide | modified |
| `labs` | `plotnine_labs` | label | exact |
| `position_dodge` | `modif_position_dodge` | position | modified |
| `position_dodge2` | `modif_position_dodge2` | position | modified |
| `position_fill` | `modif_position_fill` | position | modified |
| `position_identity` | `modif_position_identity` | position | modified |
| `position_jitter` | `modif_position_jitter` | position | modified |
| `position_jitterdodge` | `modif_position_jitterdodge` | position | modified |
| `position_nudge` | `modif_position_nudge` | position | modified |
| `position_stack` | `modif_position_stack` | position | modified |
| `scale_alpha` | `modif_scale_alpha` | scale | modified |
| `scale_alpha_continuous` | `plotnine_scale_alpha_continuous` | scale | exact |
| `scale_alpha_discrete` | `plotnine_scale_alpha_discrete` | scale | exact |
| `scale_alpha_identity` | `plotnine_scale_alpha_identity` | scale | exact |
| `scale_alpha_manual` | `plotnine_scale_alpha_manual` | scale | exact |
| `scale_color_brewer` | `plotnine_scale_color_brewer` | scale | exact |
| `scale_color_cmap` | `plotnine_scale_color_cmap` | scale | exact |
| `scale_color_cmap_d` | `plotnine_scale_color_cmap_d` | scale | exact |
| `scale_color_continuous` | `plotnine_scale_color_continuous` | scale | exact |
| `scale_color_discrete` | `plotnine_scale_color_discrete` | scale | exact |
| `scale_color_distiller` | `plotnine_scale_color_distiller` | scale | exact |
| `scale_color_gradient` | `plotnine_scale_color_gradient` | scale | exact |
| `scale_color_gradient2` | `plotnine_scale_color_gradient2` | scale | exact |
| `scale_color_gradientn` | `plotnine_scale_color_gradientn` | scale | exact |
| `scale_color_hue` | `modif_scale_color_hue` | scale | modified |
| `scale_color_identity` | `plotnine_scale_color_identity` | scale | exact |
| `scale_color_manual` | `plotnine_scale_color_manual` | scale | exact |
| `scale_color_viridis_c` | `step_scale_color_viridis_c` | scale | own |
| `scale_color_viridis_d` | `step_scale_color_viridis_d` | scale | own |
| `scale_fill_brewer` | `plotnine_scale_fill_brewer` | scale | exact |
| `scale_fill_cmap` | `plotnine_scale_fill_cmap` | scale | exact |
| `scale_fill_cmap_d` | `plotnine_scale_fill_cmap_d` | scale | exact |
| `scale_fill_continuous` | `plotnine_scale_fill_continuous` | scale | exact |
| `scale_fill_discrete` | `plotnine_scale_fill_discrete` | scale | exact |
| `scale_fill_distiller` | `plotnine_scale_fill_distiller` | scale | exact |
| `scale_fill_gradient` | `plotnine_scale_fill_gradient` | scale | exact |
| `scale_fill_gradient2` | `plotnine_scale_fill_gradient2` | scale | exact |
| `scale_fill_gradientn` | `plotnine_scale_fill_gradientn` | scale | exact |
| `scale_fill_hue` | `modif_scale_fill_hue` | scale | modified |
| `scale_fill_identity` | `plotnine_scale_fill_identity` | scale | exact |
| `scale_fill_manual` | `plotnine_scale_fill_manual` | scale | exact |
| `scale_fill_viridis_c` | `step_scale_fill_viridis_c` | scale | own |
| `scale_fill_viridis_d` | `step_scale_fill_viridis_d` | scale | own |
| `scale_linetype` | `plotnine_scale_linetype` | scale | exact |
| `scale_linetype_discrete` | `plotnine_scale_linetype_discrete` | scale | exact |
| `scale_linetype_identity` | `plotnine_scale_linetype_identity` | scale | exact |
| `scale_linetype_manual` | `plotnine_scale_linetype_manual` | scale | exact |
| `scale_shape` | `plotnine_scale_shape` | scale | exact |
| `scale_shape_discrete` | `plotnine_scale_shape_discrete` | scale | exact |
| `scale_shape_identity` | `plotnine_scale_shape_identity` | scale | exact |
| `scale_shape_manual` | `plotnine_scale_shape_manual` | scale | exact |
| `scale_size` | `modif_scale_size` | scale | modified |
| `scale_size_area` | `modif_scale_size_area` | scale | modified |
| `scale_size_continuous` | `plotnine_scale_size_continuous` | scale | exact |
| `scale_size_discrete` | `plotnine_scale_size_discrete` | scale | exact |
| `scale_size_identity` | `plotnine_scale_size_identity` | scale | exact |
| `scale_size_manual` | `plotnine_scale_size_manual` | scale | exact |
| `scale_stroke_continuous` | `plotnine_scale_stroke_continuous` | scale | exact |
| `scale_stroke_identity` | `plotnine_scale_stroke_identity` | scale | exact |
| `scale_x_continuous` | `modif_scale_x_continuous` | scale | modified |
| `scale_x_date` | `plotnine_scale_x_date` | scale | exact |
| `scale_x_datetime` | `plotnine_scale_x_datetime` | scale | exact |
| `scale_x_discrete` | `plotnine_scale_x_discrete` | scale | exact |
| `scale_x_log10` | `plotnine_scale_x_log10` | scale | exact |
| `scale_x_reverse` | `plotnine_scale_x_reverse` | scale | exact |
| `scale_x_sqrt` | `plotnine_scale_x_sqrt` | scale | exact |
| `scale_x_symlog` | `plotnine_scale_x_symlog` | scale | exact |
| `scale_x_timedelta` | `plotnine_scale_x_timedelta` | scale | exact |
| `scale_y_continuous` | `modif_scale_y_continuous` | scale | modified |
| `scale_y_date` | `plotnine_scale_y_date` | scale | exact |
| `scale_y_datetime` | `plotnine_scale_y_datetime` | scale | exact |
| `scale_y_discrete` | `plotnine_scale_y_discrete` | scale | exact |
| `scale_y_log10` | `plotnine_scale_y_log10` | scale | exact |
| `scale_y_reverse` | `plotnine_scale_y_reverse` | scale | exact |
| `scale_y_sqrt` | `plotnine_scale_y_sqrt` | scale | exact |
| `scale_y_symlog` | `plotnine_scale_y_symlog` | scale | exact |
| `scale_y_timedelta` | `plotnine_scale_y_timedelta` | scale | exact |
| `stat_bin` | `plotnine_stat_bin` | stat | exact |
| `stat_bin_2d` | `plotnine_stat_bin_2d` | stat | exact |
| `stat_bindot` | `plotnine_stat_bindot` | stat | exact |
| `stat_boxplot` | `plotnine_stat_boxplot` | stat | exact |
| `stat_count` | `plotnine_stat_count` | stat | exact |
| `stat_density` | `plotnine_stat_density` | stat | exact |
| `stat_density_2d` | `plotnine_stat_density_2d` | stat | exact |
| `stat_ecdf` | `plotnine_stat_ecdf` | stat | exact |
| `stat_ellipse` | `plotnine_stat_ellipse` | stat | exact |
| `stat_function` | `modif_stat_function` | stat | modified |
| `stat_hull` | `plotnine_stat_hull` | stat | exact |
| `stat_identity` | `modif_stat_identity` | stat | modified |
| `stat_qq` | `plotnine_stat_qq` | stat | exact |
| `stat_qq_line` | `plotnine_stat_qq_line` | stat | exact |
| `stat_quantile` | `plotnine_stat_quantile` | stat | exact |
| `stat_sina` | `modif_stat_sina` | stat | modified |
| `stat_smooth` | `plotnine_stat_smooth` | stat | exact |
| `stat_sum` | `plotnine_stat_sum` | stat | exact |
| `stat_summary` | `plotnine_stat_summary` | stat | exact |
| `stat_summary_bin` | `plotnine_stat_summary_bin` | stat | exact |
| `stat_unique` | `plotnine_stat_unique` | stat | exact |
| `stat_ydensity` | `plotnine_stat_ydensity` | stat | exact |
| `theme_538` | `modif_theme_538` | theme | modified |
| `theme_bw` | `modif_theme_bw` | theme | modified |
| `theme_classic` | `modif_theme_classic` | theme | modified |
| `theme_custom` | `step_theme_custom` | theme | own |
| `theme_dark` | `modif_theme_dark` | theme | modified |
| `theme_dashboard` | `step_theme_dashboard` | theme | own |
| `theme_gray` | `modif_theme_gray` | theme | modified |
| `theme_legend_position` | `step_theme_legend_position` | theme | own |
| `theme_light` | `modif_theme_light` | theme | modified |
| `theme_linedraw` | `modif_theme_linedraw` | theme | modified |
| `theme_matplotlib` | `modif_theme_matplotlib` | theme | modified |
| `theme_minimal` | `modif_theme_minimal` | theme | modified |
| `theme_publication` | `step_theme_publication` | theme | own |
| `theme_seaborn` | `modif_theme_seaborn` | theme | modified |
| `theme_tufte` | `modif_theme_tufte` | theme | modified |
| `theme_void` | `modif_theme_void` | theme | modified |
| `theme_xkcd` | `modif_theme_xkcd` | theme | modified |
| `xlab` | `modif_xlab` | label | modified |
| `ylab` | `modif_ylab` | label | modified |

191 components: 123 exact -> `plotnine_`, 46 modified -> `modif_`, 22 own -> `step_`
