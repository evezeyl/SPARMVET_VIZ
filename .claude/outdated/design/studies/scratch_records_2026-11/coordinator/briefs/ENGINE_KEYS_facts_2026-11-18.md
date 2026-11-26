# ENGINE-KEYS: answers and facts of 2026-11-18 (complements ENGINE_KEYS_brief_draft.md)

Ledger: D-0250 to D-0256 recorded (`15394ef5`); M270 lines expected D-0257 (Q8) and D-0258 (default theme).

## Answers
1 = B: tier key -> optional `data_engine` -> `steps`; no `wrangling:` container, no outer `steps:`; include per tier (`tier1: !include ...`) or inline; joins, tables, plots alike.
2 = yes: the 34 gallery bundles migrate in the same pass.
3 = the plot file holds the whole entry.
4 = D-0253: figure text only in `labs`; `label` -> `ui_label`; new `ui_title`; `title:` removed from plot content; report uses `ui_title` else `ui_label`.
5 = yes, rename in the same rewrite; D-0254: `modif_` only when more than argument values (wait for the modif_ list scout).
6 = build on one branch (`task/engine-keys`, worktree `.claude/worktrees/engine-keys`), one migration, every recipe and bundle, merge only after full controls.
M270: no theme written = plotnine's own default; built-in `theme_bw` removed; the migration writes `theme_bw` where none is named and lists the files.

## Step 0 (running since 09:45, builder)
Picture comparison tool in `assets/scripts/` with write and check modes; every plot of every shipped recipe plus the equality recipes; baseline in `tmpAI/engine_keys/picture_baseline_15394ef5/`; report `tmpAI/engine_keys/step0_report.md`. Reason: the golden baseline compares data only (`golden_baseline.py:34-40,117-119`). Every later step ends with the check = identical.

## Label and title facts (scout)
- `title:` at plot root: 18 files `pipelines/1_test_data_ST22_dummy/plots/*.yaml`; 3 `figshare_integration/plots/plot_{a,b,c}_*.yaml`; inline `templates/e_coli.yaml:108,121`, `simple_template.yaml:81`, `audit.yaml:55,73`; orphan `stress_test_master/plots/final_plot.yaml` (root title AND labs title; no recipe uses it). None of the 26 live ones has a labs title; 10 of the 18 have a labs layer, 8 none.
- Path today: `plot_config_resolver.py:629-637` seeds labels.title from the spec title; `viz_factory.py:375-379` applies labs after the layers, so the root title wins over a labs title. Default None at `plot_config_resolver.py:58`.
- Migration (my reading, sent in M271): old text -> `labs` title (same picture) AND `ui_title` at the entry (same report name). The resolver's title seed is removed.
- Report names: `export_handlers.py:1779` (spec title else title-cased id), `:1782`, `:329-336`, audit prose `:436-440,486-489`, heading `:1823-1826` -> `ui_title` else `ui_label`. Only pin: `app/tests/test_export_report_texts.py:114-118`.
- `label` -> `ui_label` SURE: group label (readers `home_theater.py:1137`, `blueprint_handlers.py:2441,2539`, `agent_context.py:156`; writer `group_plot_manager.py:104`; check `recipe_check.py:884-885`); plot entry label (readers `home_theater.py:1142-1145,372-383`, `blueprint_handlers.py:2447`, navigator `:690,722,800`; writers `group_plot_manager.py:156`, `example_recipe.py:121`; check `recipe_check.py:908-910`, `recipe_spec.yaml:36`).
- WAIT for Eve (M271 q1, q2, q4): `info.label` (`home_theater.py:915-924`, `gallery_manager.py:107`, `recipe_check.py:231-232`); table and join label (`recipe_check.py:305-306,662-663`; no reader); input column label (`recipe_spec.yaml:28`; no reader); plot-tab description fallback (rule says label, description, key; code does it for groups only).
- NOT recipe keys, never rename: form and ui_schema labels, widget labels in the plot library, `sidebar_registry.py`, session labels, `taxonomy.py:108`, cytoscape nodes, export scope labels.
- `ui_title` is also an app-features key (`home_theater.py:917-924`): M271 q3.

## Gallery and other engines (scout)
Design in NOW:
- one helper `plot_engine_of(raw, plot_id)` (entry value, else top level), used by the gallery check, the taxonomy reader and `render_example`;
- `gallery_examples.py:114,119` goes through the engine dispatcher (D-0247), not a direct import of the plot library; `viz_factory.py:114-127` reads only the top-level `plot_engine` today;
- every reader of `spec` moves: `taxonomy.py:43-64`, `gallery_examples.py:92`, `example_recipe.py:121-132`, `recipe_spec.yaml:35-40`;
- checker catalogues per engine; the gallery check refuses an engine without an entry file, with the D-0239 words (`engines.py:33` wording to change);
- picture contract written in the entry text: save(path, width, height, dpi) giving PNG;
- optional engine parameter in `example_recipe`.
CAN WAIT (derived, no file migration): index `engine` field, engine filter in the gallery, geom derivation per engine, PS03 per engine, docs wording.
Stale today, not an engine point (report to Eve, rule text is hers): `rules_gallery_standards.md:16-28,98-103` and `libs/viz_gallery/README.md:22-25` name a preview generator file that does not exist; the cheat sheet says `info.geom`.
For Eve later (not blocking): show or filter the engine in the gallery; example whose engine has no library: left out with reason or listed without picture.

## Test Lab writers (found 2026-11-18, NOT in the old brief: add to step 4)
The Test Lab writes recipes: `libs/test_lab/src/test_lab/bootstrapper.py`, `scaffolder.py` (entity key by name at `scaffolder.py:156`), handlers `app/handlers/test_lab_handlers.py` (silent `sample_id` at `:422,424`, box pre-filled at `:340`). Their output is ALREADY refused by today's checker (F01, J07, S03, J02, E03; empty `analysis_groups: {}` read as missing). Step 4 must make them write the new shape AND add a test that runs the checker on what they write. The other Test Lab defects (review `.claude/design/exploration/2026-11-18_test_lab_review.md`, 15 fixes, 9 questions) are NOT part of this build.

## Theme (M270)
Remove built-in `theme_bw`: `plot_config_resolver.py:47,63`, `viz_factory.py:136`; design note `plot_config_cascade.md:62,133`. The migration writes `theme_bw` (in `plot_defaults` or per plot) where a recipe or bundle names no theme, lists the files; pictures identical (step 0 check). Report other built-in defaults that are an app choice; change none.
Recorded: D-0257 ("Q8 - A"), D-0258 ("plotnine has a default so if no theme is recorded it falls on plotnine default"); commit `cd0a11d8`.
Places (reviewer, 2026-11-18): injection = `plot_config_resolver.py:47` (`_L1_LAYERS`) and `:63` (`_BUILTIN_DEFAULTS`); `viz_factory.py:136` is a docstring. `themes/core.py:258-270` `theme_dashboard` wraps `theme_bw`, its description at `:265` says it is the default (untrue; D-0256 point 4). `blueprint_handlers.py:1816` `_THEME_CHOICES` (check whether it assumes the default). Docs: `libs/viz_factory/README.md:65,109`; `docs/appendix/viz_factory_rationale.qmd:68,93,115`; `docs/workflows/visualisation_factory.qmd:194`; design note `plot_config_cascade.md` (also 221, 315-322 still show it). Tests that pin it and must be adapted to the decided design first: `libs/viz_factory/tests/test_plot_config_resolver.py:121,219-221,250`; check `test_theme_slots.py:57-58`. How many recipes and bundles already name a theme: NOT counted yet (the rewrite tool must count and list).
