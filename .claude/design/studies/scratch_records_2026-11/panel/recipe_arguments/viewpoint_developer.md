# Viewpoint of the developer: how arguments and constructions enter a recipe (2026-11-17)

Role: effort, risk, test cost, build order. Not a decision; Eve decides. Labels: [read] file:line, [run] scratch run (scripts in `tmpAI/panel/recipe_arguments/developer/p1.py p2.py p3.py`), [reasoned], [estimate] (days of one builder, mine, not measured), [not checked].

## 0. What the signatures really say (the prototype question)  [run]

plotnine 0.15.4. Can the parameter annotation tell that `position` takes a position object and `axis_text_x` an `element_text`? **No, not from the signature.**
- `geom_bar`, `geom_col`, `geom_point`, `stat_summary`: signature is `(mapping, data, **kwargs)`; `position` is not a parameter at all (p1.py). It exists only as a string in the geom's DEFAULT_PARAMS (`position="stack"`) and in the docstring text. `theme(...)`: `axis_text_x=None` without annotation, rest `**kwargs` (p1.py).
- What does carry information: (a) the **value constructors** have real typed signatures (`position_dodge(width: Optional[float], preserve: Literal[...])`, `element_text(size: float|Sequence[float]|None, ha: Literal[...] ...)`, `guide_legend(title, nrow, ncol, ...)`); so the *parameters of the nested object* can be read and checked with the existing `signature_params.read_parameters` and `parameters._signature_definitions`. (b) the **themeable classes** (119 in `plotnine.themes.themeable`) carry the slot type only in prose: `axis_text_x.__doc__` has `theme_element : element_text`; 52 say element_text/line/rect, the rest say float/int/Literal, 6 say nothing (p2.py). That is parseable but it is a docstring, not an API.
- So the "slot -> object family" table (geom `position` takes `position_*`, theme key takes `element_*`, `guides(<aes>=)` and scale `guide=` take `guide_*`) cannot be derived from annotations. It must be a small table written by us (3 families for geom/guides, plus the 52 theme keys) with a test that fails when plotnine changes (the pattern of `libs/viz_factory/tests/test_exact_parameters_equal_plotnine.py`).
- plotnine itself does not check the slot: `theme(axis_text_x=element_line())` draws with no error; `axis_text_x='foo'` fails late (`Text.set() ... 'value'`), `axis_ticks_x=element_text(angle=3)` fails late with a matplotlib message, `legend_position=element_text()` draws silently (p2.py). `geom_col(position=element_text())` fails with `Unknown position of type` (p3.py). So a slot check of ours would be **stricter than plotnine**, and that is a new rule to document.

## 1. Prototype of way B against the live registry  [run, p3.py, ~25 lines]

A resolver `resolve(value)`: a dict with `name` (and optional `params`) -> look the name up in a table of plotnine constructors, resolve params recursively (depth limit 6), refuse unknown parameter names from the constructor signature, build the object. Results:
- `position: {name: position_dodge, params: {width: 0.5}}` + `theme(axis_text_x={name: element_text, params:{angle: 90}})` drew; object params identical to plotnine direct (`width 0.5, preserve total`).
- Refused with a plain message: `position_dodg` (lists the allowed names), `widht` (parameter not of position_dodge), `angel`.
- **What breaks / must be written new:**
  1. The resolver cannot use `PLOT_COMPONENTS`: the registered `position_dodge`, `element_text`, `guide_legend` are *layer handlers* `(p, spec) -> p` (positions/core.py:19-25, themes/core.py:365, guides/core.py:84), not constructors. The value table is a **second registry** (name -> plotnine class, `plotnine` own name, as D-0214 wants for values). The live registry holds 22 names with these prefixes (p3.py), 15 of them the not-addable ones.
  2. `get_component` (registry.py:105-120) is the one choke point where every component's params can be walked and resolved before the handler runs (it already runs `refuse_unsafe_texts` and `_exact_facets` there). Exact geoms pass `**spec` straight to plotnine (geoms/core.py, e.g. `p + stat_unique(**spec)`), so doing the resolve here covers all 42 geoms and 22 stats with no per-geom edit.
  3. **Seed hole (important).** `utils/random_layers.py:48-50` `position_of` returns the position name only when `position` is a string (`_plotnine_name` returns None for a dict, line 41-43, with the comment "a recipe cannot hold ... a mapping"). With B a recipe `position: {name: position_jitter}` would be *not seen as random*: no seed injected, unseeded jitter, a different picture every render, silently. `_seed_random_components` (viz_factory.py:60-81) and `is_random_layer` (random_layers.py:58-68, shared with the checker) must read the nested form, and the seed must go into the nested `random_state`. This is a reproducibility rule (Eve's S1); the test `test_every_component_randomness.py` and `test_plot_seed.py` must cover the nested form.
  4. The recipe checker only checks top-level `params` keys of a layer (recipe_check.py:955-981: `for key in params`, PS04). Nested values are not looked at, and `layer_text_problems` (plot_text_check.py:132-) takes only top-level keys. A nested `{name, params}` needs a recursive pass (PS04 for the nested name and parameter, PS06 for any text inside).
  5. Dedupe/ordering stays for layer forms (plot_config_resolver.py `_dedupe_layers` by name; `BATCHED_COMPONENTS = ("element_text",)` at :172 applied last, viz_factory.py:334-361). A value form has no such behaviour: that is a gain (D1-D5 of q6 vanish for values) but also a **difference between the two forms** while both exist.
  6. `theme_custom` today silently drops an unknown element name (themes/core.py:325-337, no else) and `guides:` block falls back to `guide_legend` (viz_factory.py:391). The resolver replaces both and makes them refusals: this is a behaviour change of existing recipes, but no shipped recipe uses either (0 uses of `theme_custom`, 0 `guides:` in config/ and gallery_data/ [run grep]).
  7. Where the theme value lives: `theme:` of a plot is a *name* of a complete theme (plot_config_resolver.py:646), element settings are a `theme_custom` layer or `element_text` layers. A "theme block with keys" is a new spec key (resolver L4 key list + `unknown_spec_keys`, the rule that today refuses unknown keys). B for elements can reuse `theme_custom` (no new key) or add a block (C-like); that is a design choice, not mine.

## 2. Way by way

### A. Separate layers as today
- Reuse: everything. New: nothing for the demo.
- Effort: 0 for code. The rename of the 15 layer components to `modif_<name>` is a pure rename (rename doc `.claude/design/viz_rename_impact_2026-11-15.md`). But D-0210 ("both the modif and the plotnine original") cannot be met: no original exists for these 15 (q6 section 4(i), all 15 fail `__radd__` alone [read q6]). Quantity left unfixed: D1-D7 silent differences (q6 section 6).
- Risk: the 7 silent defects stay (second `element_text` on one axis drops the first, dedupe drops the first of two `element_blank`, position goes to the last layer, `element_text` last whatever its place). Error from the user: invisible.
- Tests: the existing set; only renames.

### B. Typed value {name, params} where it belongs
- Reuse: `signature_params.read_parameters` and `parameters._signature_definitions` (nested param names and types from the plotnine constructor signature, so the form comes for free for the nested object); `arguments.accepted_names` pattern; `get_component` choke point; the existing `theme_custom` element branch and the `guides:` block as the two partial precedents; `ui_schema` widgets for the form.
- New: (1) value registry (constructors by plotnine name + slot-family table + test against plotnine) ~1.5 d [estimate]; (2) resolve in `get_component` + refusal with did-you-mean + nested depth limit ~1 d; (3) rewrite `theme_custom` and the `guides` block on the resolver, remove silent fallbacks ~0.5 d; (4) seed and randomness reading nested position (random_layers, `_seed_random_components`, checker) ~1 d; (5) checker recursion PS04/PS06 ~1 d; (6) scale `guide=` and `guides` component accepting objects (guides/core.py:50-60 passes only strings today) ~0.5 d; (7) Blueprint form "object" widget (pick name, then fields of that constructor) ~2-3 d [estimate; the form code was **not read**]; (8) migration of shipped uses + docs + tests ~1.5 d. Total ~9-11 days [estimate].
- Files touched (non-test): registry.py, a new values module, themes/core.py, guides/core.py, viz_factory.py (guides block, seeding), random_layers.py, recipe_check.py, plot_text_check.py, schema widget code, README + `rules_viz_factory.md` 1a; ~10 files.
- Risk: medium. Main silent risks: the seed hole (3 above), slot check stricter than plotnine (a recipe plotnine draws now refuses), plotnine upgrade changing a constructor signature or the themeable docstrings (the test must fail, then the table is updated by hand: a test, not a silent fallback).
- Tests: new: resolver unit (allowed, unknown name, unknown param, wrong slot, depth limit, nested), seed with nested jitter (same pixels twice), checker nested, picture equality value form vs layer form, plotnine-drift test of the slot table. Changed: the tests that pin layer behaviour only if the layer form is removed (see rows below).

### C. A section per owner with plain keys
- Reuse: resolver L4 key list, `theme_legend_position`-style named components. New: for every key the app must know the object class and the parameters; since the signatures do not say (section 0), the **whole table key -> object** is hand-written (theme: 52 keys; geom position; guides) with a drift test; the parameters of the key are not a named object so the form shows fields from the key's own table, not from a constructor signature.
- Effort ~8-10 days [estimate]; the table is the cost, and it is the part that silently drifts at a plotnine update (new themeable, renamed). Risk: highest of the typed forms: a new unlisted key is either refused (plotnine feature unreachable) or guessed (not allowed). Two renderings of one object (the app decides which class), the user cannot reuse the plotnine docs (viewpoint_user.md C).
- Tests: as B plus a per-key table test.

### D. Short call-like text, allow-list grammar, never evaluated, parsed to B's structure
- Reuse: `formula_check.py` (ast.parse + allow-list visitor, `_parse` :289, `formula_problems` :297-310) as a pattern; the B resolver after parsing. New: the grammar `name(kw=literal, ...)` with nested calls, literals only; an error pointing at the column in the text; the reverse (structure -> text) for the Blueprint form and the export record (one canonical text).
- Effort: B (all of it, because D parses to B) + parser ~1.5 d + canonical printer ~0.5 d + form parse-back ~1 d = ~12-14 days [estimate]. Risk: two surface syntaxes for one thing (user view: "two ways side by side confuses most"); `random_state=0` etc. literal rules; comments, quotes; a text in a YAML string can be misread for a Polars-style formula. Safe in principle (no eval), but precedent in this repo is that text checks produced several defects (PLOT-TEXT-RUNS-CODE-1: 5 kinds of text reach an evaluator [read scout A5]).
- Tests: B + grammar fuzz (refuse `__import__`, lambda, attributes, calls to unknown names, deep nesting), round trip text <-> structure.

### E. Registry of named ready-made functions/choices with data parameters
- Reuse: the existing pattern is already there: `stat_summary` `fun_data` as a name (geoms/core.py:1146), `facet_labeller` allow-list (facets/core.py:259), `_function_from_string` for `stat_function` (core.py:1289-1308). New: registry of named summary functions, label formatters, breaks functions, labellers, with data params; each must be proved to equal what plotnine does with the same function (same pictures).
- Effort: ~0.5-1 d per function family [estimate]; unbounded set, and needs a decision on which functions are in. 0 shipped uses [read scout B3], so the demo gains nothing. Risk low-medium: a named function whose behaviour is ours (e.g. "mean_se") is a *modified* thing and needs the plotnine-original rule (D-0210). Tests per function (picture or number equality).
- Independent of B: can come later, no common file except registry.py.

### F. Polars
- Keep the allow-listed formula text (decided: D-0064, "The formula allow-list as built is accepted for now") : effort 0, risk already understood (CPU/memory limit, "no time or size limit now"), tests exist (`test_formula_check.py`, `test_mutate_formula.py`, named in scout A5).
- Expressions as data: effort **large**: 6 Polars/modif actions + id-reconciliation mutate (7 entry points [read scout A5]) and all shipped formulas (`named_exprs`, `named_aggs`, `predicates`) rewritten as trees; Blueprint nested boxes (user view says slower for a division); a new test set proving equality with the text path. Not needed by the demo. Not part of the same build as B (different library, different files); it can be a later own decision.

## 3. Counts (grep, [run])

| Place | position_* | element_* | guide_* | theme_custom | `guides:` |
|---|---|---|---|---|---|
| config/ (recipes) | 3 files (position_dodge after geom_bar) | 2 files, 3 uses | 0 | 0 | 0 |
| assets/gallery_data/ (37 bundles) | 2 files (position_fill, position_stack) | 0 | 0 | 0 | 0 |
| assets/template_data_analysis_recipes | 0 | 0 | 0 | 0 | 0 |
| app/tests | 13 files, 16 lines | 0 | 0 | 0 | 0 |
| libs/viz_factory/tests | 16 files, 52 lines | 9 files, 52 lines | 8 files, 35 lines | 5 files, 11 lines | 0 |
| libs/utils/tests | 2 files, 9 lines | 0 | 0 | 0 | 0 |

(`position:` as a string value: 3 recipes in config, 2 gallery bundles, 2 app/tests files, 6 viz_factory test files. These stay valid in B, D, E, F: the string form is not removed unless Eve decides so.)
- Shipped layer-form uses that a B migration would move: 5 layer uses of position_* (3 + fill + stack), 3 of element_text = 8, in 7 files (5 in config, 2 in gallery). Mechanical migration is possible for position_*: the rule today is "last layer", so `geom_X` then `position_Y{p}` becomes `geom_X{position: {name: position_Y, params: p}}` when the previous layer is the geom (all 5 are). For `element_text{target: T, ...}` -> `theme_custom{T: {name: element_text, params}}`, **but not order-neutral**: ResFinder_genes_heatmap.yaml:8-17 writes element_text then `theme_minimal`, and element_text is applied last today (q6 D3); a `theme_custom` layer written in the same place would be overwritten by the complete theme and the rotation would vanish. The migration must put the value after the theme (or the design must say where theme values apply). Therefore: not blindly mechanical; verify by picture.
- Golden baseline: `app/tests/test_golden_baseline.py` records the **tables** of every plot, not pictures (docstring lines 1-8); it does not detect a changed theme, position or element. It will stay identical for any of the ways. The picture checks that exist are: `libs/viz_factory/tests/test_reproducible_render.py` (sha256 of a PNG, dpi 60, lines 36-39, same input twice) and the gallery bundles' `preview_plot.png` / `preview_thumb.png` (checked by `libs/viz_gallery/tests/test_gallery_bundle.py`, `app/tests/test_gallery_app_path.py`: what exactly they compare was **not read**). No test compares old layer form picture with new value form picture: it must be written (one test, 8 shipped uses, hash equal).

## 4. Combination with the rename (D-0091, D-0210, D-0213, D-0214; `viz_rename_impact_2026-11-15.md`)

- D-0214 says names written as VALUES stay plotnine's own names. So under B the value is `{name: position_dodge}`, while after the rename the layer form is `modif_position_dodge`: **no name collision**, and the value registry is separate from `PLOT_COMPONENTS`. This is why the two builds are independent in files: the rename touches names in the registries, `theme:` key, `plot_config_resolver.py` family rules (`BATCHED_COMPONENTS` name :172, `FACTORY_NAMED_COMPONENTS`), tests that pin names, 25 recipes dirs and gallery; B touches new values module, `get_component`, random_layers, checker recursion.
- The shared file is `registry.py` and `recipe_check.py`/`viz_factory.py` (rename edits name lists; B edits the choke point and the seed function). Merge conflicts are small and mechanical if the rename lands first or the two worktrees keep to separate functions.
- One build or two: **two**. The rename is a rename (pure, testable by the audit test vs plotnine, high file count, low logic); B is new logic (small file count, high logic). Doing both in one branch mixes a mechanical diff with a logic diff and makes a review of the seed rule hard.
- Order: the rename first is possible *only if* the 15 layer forms are named `modif_` with no `plotnine_` neighbour for now. That is a state D-0210 forbids ("both the modif and the plotnine original"), and the existing test `test_no_exact_plotnine_object_is_registered_next_to_a_modified_one_today` pins the opposite. It is a **temporary half state**: acceptable only if written as a numbered open point, with a removal task, not as a result. Alternative: B first (small, the original arrives as a value), then rename with all three slots done: ~1 week later, no half state.
- Smallest first step that unblocks the rename: **a decision, not code**: "for position_*, element_*, guide_* the plotnine original is the typed value `{name, params}` in the slot where plotnine takes it (3 slots), the layer form is `modif_`; functions as parameters (E) and Polars (F) are decided separately." Then the rename can register `modif_` names for the 15 and a task for B is queued with D-0210's wording. Cost of this step: 0 code; 1 decision.
- Parallel worktrees: (W1) rename of the layer names [mechanical, sonnet/medium for the bulk, reviewer opus]; (W2) B value registry + resolver + seed + checker [opus/high, because of the seed and the checker rules]; (W3) shipped migration + docs + picture-equality test, after W1 and W2; (W4) Blueprint object widget, after W2's schema is fixed; E and F: later, own decisions.

## 5. What the demo needs

Read from config and gallery greps:
- `demo_abromics.yaml:71-81`: one plot, `geom_bar` only: **no position layer, no element, no guide**. The shipped pipelines that use more: ST22 dummy 1 (`element_text` rotated axis text in 2 plots), ST22 dummy 2 (3 plots with `position_dodge` `params: {}` after `geom_bar`), `stress_test_master` (`position: "dodge"` as a string value), gallery `stacked_bar`, `proportion_bar` (position_stack/position_fill layers), `bar_grouped` and `stacked_area` (string `position`). 
- No shipped recipe uses `stat_summary` `fun_*` / `fun_data`, `facet_labeller`, `guide_label`, scale `guide:` or `labels:`, `stat_function`, a nested `guides:` block, `theme_custom` (0 uses [read scout B2/B3, grep above]). The demo uses nothing of E or F beyond what exists, and nothing beyond **dodge positions and rotated axis text**.
- So for the demo: **nothing new is needed.** Every shipped use works today in the layer form and in the string form for position; picture state is whatever the previews show now. The demo would be affected only if the rename is built first (names change) or the layer form is removed (8 uses rewritten).
- What can wait: B entirely (including form widget), C, D, E, F. What must not be forgotten: the layer-form defects are real but invisible to the demo; list them as known defects (q6 D1-D7), not fixes.
- Caveat [reasoned]: if the demo shows the Blueprint form for these three objects, a user who wants a width on a dodge cannot write it as a value today (only as a layer), and cannot write a rotated axis text except through `element_text` + `target`. It works; it is just the odd form.

## 6. Table

| Way | Reuse | Effort [estimate] | Risk | Recipes / tests touched |
|---|---|---|---|---|
| A layers as today | all | 0 (rename only) | 7 silent defects stay (D1-D7); D-0210 not met for 15 | 0 recipes; rename tests only |
| B typed value | signature_params, parameters.py, get_component choke point, theme_custom/guides precedents | ~9-11 d incl. form | medium: seed hole (nested jitter), slot table drift, stricter than plotnine | 8 layer uses in 7 files if layer form is migrated (0 if both kept); new tests ~6 sets; changed: tests that pin layer form only if removed (position 16 viz tests files, element 9, guide 8) |
| C sections plain keys | resolver key list | ~8-10 d | high: hand table of keys drifts silently at plotnine update | same recipes as B + per-key table test |
| D call-like text | formula_check pattern, plus all of B | ~12-14 d | two syntaxes; grammar bugs; round trip | B + grammar fuzz + round-trip |
| E named functions registry | fun_data / labeller precedents | 0.5-1 d per family | each named function must equal plotnine or be `modif` | 0 recipes (0 uses); a test per function |
| F Polars | formula_check, evaluate_formula | keep: 0; as data: large (7 entry points) | keep: known limit CPU/memory (D-0064) | keep: 0; data: all formula recipes |

## 7. Recommendation (mine, for Eve to accept or change)

1. Decide the **form for the 15 only**, now: B (typed value in its slot) as the plotnine original, layer form kept as `modif_`. Write the decision with D-0210 and D-0214 numbers.
2. Build order (tags per CLAUDE.md section 2): (a) value registry + slot table + drift test `[opus/high]`; (b) resolve at `get_component`, rewrite `theme_custom` and `guides:` without fallbacks `[sonnet/high]`; (c) seed and checker for the nested form `[opus/high]` (a reproducibility rule: needs tests that can fail, same picture twice, jitter without seed refused); (d) rename of the layer names in parallel worktree W1 `[sonnet/medium]`, reviewed `[opus/high]`; (e) migration of 8 shipped uses with picture equality `[sonnet/medium]`; (f) Blueprint object widget and docs `[sonnet/high]`. (a)-(c) sequential in one worktree; (d) parallel with (a)-(c); (e), (f) after both.
3. Leave E and F out of this build. For the demo, build nothing of this: freeze, list D1-D7 as known defects.

## 8. What Eve must be told to choose well (not what to choose)

- The signatures do not say which object a slot takes; the table is ours and a plotnine update can break it (a test will say so).
- B and D forms make the app **stricter than plotnine** (plotnine draws `axis_text_x=element_line()`; we would refuse).
- Both forms (layer and value) alive at once = two ways to do one thing and a difference of behaviour (order, dedupe, last-applied) between them: ADR-099 "one authoritative way" speaks for removing the layer form after migration, with a tombstone; a decision on that is needed.
- Nested jitter without the seed work = silent non-reproducible pictures (hard rule); the seed work is part of B, not optional.
- The rename first leaves a temporary state where the 15 have no plotnine original (D-0210); it must be written as an open point with a removal task.
- The demo needs none of this.

## Not checked

- The Blueprint form code (widgets for an object value): effort of (7) is a guess.
- What gallery `preview_plot.png` tests compare (pixels, hash, or existence); whether any preview uses `element_text` (grep: 0 in gallery).
- Whether scale `guide=` and `guides` component paths take an object after plotnine's own handling (only q6 runs).
- Test counts inside app/tests (16 lines) by file meaning; whether any app test reads the layer names for a UI list (rename side).
- plotnine 0.15 -> next: only the present signatures were run.
- Polars version drift: not run.
- That `demo_abromics` is the demo the owner means (read: one `geom_bar` plot at lines 71-81; the other pipelines were only grepped).
- The stat_function, patsy builtins question (scout not checked list).
