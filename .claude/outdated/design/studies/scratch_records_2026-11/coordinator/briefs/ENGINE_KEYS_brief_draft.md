# Brief (DRAFT, not sent): the big recipe change, "ENGINE-KEYS"

Prepared by the coordinator in the night of 2026-11-17, as the review session asked (channel M260 point 3).
NOT to be sent before Eve has answered questions 1 to 4 and 6 of `tmpAI/panel/QUESTIONS_for_eve_2026-11-18.md`
(and 5 if the rename goes in the same rewrite). Fill the places marked `<<ANSWER n>>` first.

Facts to build on: `tmpAI/panel/engine_keys_shape/scout_places.md` (every place, with file:line),
`scout_containers_title_entry.md`, the four picture files in the same folder, the plan
`.claude/design/exploration/2026-11-17_engine_fields_plan.md` (sections 1.4, 3.2, 5.3, 6).

## Order (one worktree `engine-keys`, branch `task/engine-keys`, ONE worker at a time, each continues the progress note)

One change, one rewrite of the recipes, merged once. Inside the branch the work is cut in steps so that a stop loses nothing.
Each step ends with a commit and a line in `tmpAI/progress.md`. Model per step in brackets.

1. **Tests first and the format rules** [builder, high]. `libs/utils/src/utils/recipe_spec.yaml`, `recipe_check.py`
   (plot entry, step containers, `plot_defaults` keys, new codes for the engine keys), `recipe_loader.py` (rule F01: a
   wrapper key in an included file becomes an error), `config_loader.py` (the two un-nest sites of `spec`). Tests that
   fail without the change: the old shape is refused with a message that names the rewrite tool; the new shape is
   accepted; each of the four removed keys is refused (tombstone text per `rules_legacy_management.md`).
2. **The rewrite tool** [builder, high]. In `assets/scripts/` beside `migrate_recipe_format.py` (argparse, `--check` and
   `--apply`, a path argument, no hardcoded path). Safe to run twice (the second run changes nothing and says so).
   Prints every key it removes with its old value and the file. Keeps comments and `!include` lines (round-trip
   loader; check how the earlier tools did it). Tests: twice-run; printed removals; comments kept; a file with nothing
   to change is untouched byte for byte.
3. **Run the rewrite** [builder, medium] on: `config/data_analysis_recipes/` (pipelines, templates, retest, the 54
   fragment files, the plot files), `assets/gallery_data/*/data_analysis_recipe.yaml` (only if `<<ANSWER 2>>` is yes),
   `app/tests/equality/recipes/`, the test recipes under `libs/*/tests` that are recipes (not the plot-spec test data
   of `libs/viz_factory/tests/test_data/` unless the loader reads them as recipes: check and report), templates in
   `assets/template_data_analysis_recipes/` if present, `docs/appendix/data_analysis_recipe_structure.yaml`.
   Add the commented tier-3 example to `templates/left_join_lesson.yaml` (D-0237 item 6). Report the printed removals.
4. **The readers and writers** [builder, high]: `libs/transformer/.../data_wrangler.py` `_resolve_tier`;
   `app/modules/orchestrator.py:138,296-297`; `libs/blueprint_arch` (navigator, mapper, `t3_translator.py`,
   `group_plot_manager.py:141-156`); `app/handlers/blueprint_handlers.py:489-608,522-564,903-911`;
   `app/modules/wrangle_studio.py`; `app/handlers/home_theater.py`, `audit_stack.py`, `export_handlers.py:904-960,1145`;
   `app/src/server.py:78`; `app/modules/plot_seeds.py`, `gallery_examples.py`; `libs/viz_gallery` (`example_recipe.py`,
   `taxonomy.py`); `assets/scripts/golden_baseline.py`, `convert_gallery_examples.py`, `retest_walkthrough.py:44-71`,
   the debug scripts. No shim: no reader accepts both shapes.
5. **The engine field and the engine check** [builder, high] (D-0238, D-0247): field `engine` in every registry entry
   of the transformer and of the plot library; entry files `libs/transformer/src/transformer/engine_python_polars.py`
   and `libs/viz_factory/src/viz_factory/engine_python_plotnine.py` exposing `ENTRY`; a test for every row of the
   engine table (file name = `engine_` + value with `-` turned into `_`); a test that no entry lacks the field and
   that field and name prefix agree for `polars_` (and `plotnine_` once the rename exists); the checker refuses a step
   under another engine's block (names the step, the block's engine, the step's engine) and refuses an engine name the
   app has no library for ("no library for this engine in this app", listing the engines this app has); tier 3:
   refuses an engine the audit cannot write. The libraries do not import each other; `app/` joins them.
   The plot library receives the plot's engine at draw time, and the export hands it over (defect: `export_handlers.py:1144-1147`).
6. **Cache keys** [builder, medium] (D-0240): `app/modules/cache_keys.py:47` version 4 to 5; each tier's engine is an
   argument of that tier's key; the plot engine enters no table key. Tests: a changed tier engine changes only that
   tier's key and the keys after it; a changed plot engine changes no table key; no stale table is served after the
   bump; the one-sentence notice is shown once: "The tables of your recipes are rebuilt once because the app changed
   how it names what it stored. Your results do not change."
7. **The export record** [builder, medium] (D-0248): `effective_run.yaml` records per plot and per tier the engine,
   the library versions of the engines used, and the theme as applied per plot (`export_handlers.py:1453-1474`).
8. **Spec, rules, docs** [builder-opus only if a rule text needs judgement; else builder, medium] (D-0249 allows the
   sentences of plan 3.2 and 5.3): `recipe_format_spec.md` (the example at 55-75, DEC05, DEC08, DEC17, 4.1 with the
   sentence "format 1 was amended before its first release, on <date>, by decision of Eve", the open list of engine
   names, the plot entry table, `plot_defaults`), `rules_data_analysis_recipe_structure.md` (sections 2, 7, 8, 10),
   `rules_viz_factory.md` (6b, 7), `rules_data_engine.md` (section 3), `rules_agent_role_bioscientist.md`,
   `rules_test_lab.md` (stubs), the `.qmd` docs and READMEs listed by the scout, the changelog, `@deps`, then the
   dependency index. `docs/UML/app.mdj`: list what must change, do not edit (the bridge needs StarUML running).
9. **Final checks by the builder**: a grep that finds none of the four keys and no `spec:` under a plot entry outside
   the tombstone; the golden baseline (`--check`): if it differs, STOP and report (the change must not alter a result);
   the gallery previews identical.

Then: reviewer (diff, decision compliance, break-once on five points, the rewrite run twice on a copy), full controls,
merge, scribe (tasks.md, handoff, ledger "built" notes).

## Decisions block to paste at the top of each step's brief (quotes are from the ledger lines)

- D-0236: "B we are still in development so no problem - ensure all changes are propagated."
- D-0237: "B for both ... first engine then label, but you got the idea, yes, no spec ... Cleaner"
- D-0238: "A" (verify the quoted words of the ledger line at send time; the hook needs at least 12 characters of the line)
- D-0240, D-0241 ("Ok A"), D-0242: "A - we need lots of parameters accepted. And set B eventually as deferred - if needed."
- D-0247, D-0248, D-0249: "13 and 14 are trivial (because of 12 and our principles) - as they are related - so put now"
- D-0220: "A recipe key that does nothing is dead code and is removed from the recipe structure."
- D-0219: "the top of the recipe gives the default engines for the whole recipe, a tier or a plot may override them"
- D-0050: "No silent error that is the rule."
- plus the NEW ledger lines for her answers to questions 1 to 4 (to be recorded by a scribe BEFORE the first step is sent).

## To fill from her answers

- `<<ANSWER 1>>` tier container: A (containers kept, `steps:` twice) / B (tier keys directly in the table, the join and
  the plot entry; `wrangling:` and the outer `steps:` go; the 54 fragment files keep their root `tier1:` and are
  included one level higher: check how an include of several keys into a mapping is written, `<<: !include` is not
  YAML-safe here; this may mean the fragment is included per tier: REPORT the options before choosing) / C (inner word).
- `<<ANSWER 2>>` gallery bundles follow: yes / no.
- `<<ANSWER 3>>` what moves into an included plot file: plot content and label only / the whole entry.
- `<<ANSWER 4>>` the `title:` key: kept / moved to a labels layer.
- `<<ANSWER 5>>` rename in the same rewrite: yes (then V1-B-RENAME's steps are added between steps 4 and 5, with the
  picture-equality test first) / no.

## Risks to name in the brief

- Variant B and the 54 fragment files: today a fragment is the VALUE of `wrangling:` (it starts with `tier1:`). Without
  the container there is no single key to hang the include on. Options to report, not to choose silently: include per
  tier (`tier1: !include ...`, the fragment then holds the tier's content `data_engine`/`steps`), which fits her words
  "an include file that holds a tier ... would itself say which engine it is for"; or keep one container for tables only.
- Session files and bundles written before the change hold tier 3 and plot content in the old shape: check
  `session_manager.py` and `bundle_importer.py`; an old session must be refused or read with a plain message, not
  half-read (D-0050). The cache version bump already invalidates stored tables.
- Blueprint writes recipes: every writer must write the new shape, or Blueprint produces recipes the checker refuses.
- The plot-spec test data of the plot library (about 165 YAML files) are plot contents, not recipes: they may need no
  change at all; verify before touching.
