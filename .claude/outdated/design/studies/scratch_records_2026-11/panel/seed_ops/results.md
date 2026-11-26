# Seed trace and operator table (run 2026-11-14, branch feat/recipe-format-1)
Scripts and raw output: tmpAI/panel/seed_ops/{seed_trace,ops_trace,gal_trace,form_trace}.py and *_out.txt.
RUN = executed; READ = code read, not executed. HOME's seed closure (home_theater.py:408-432, 547-551) runs only inside a
Shiny session; I RAN a replica of those exact lines against the real VizFactory (no live browser run). Pictures compared by PNG hash.

## 1. Seed: which seed is really used (same data, jitter plot)
| case | direct VizFactory().render and gallery preview | HOME plot (2 sessions) | results-bundle plot | seeds_per_plot records |
|---|---|---|---|---|
| a recipe 123 | 123 (hash = ref seed 123) RUN | NOT 123: the drawn seed (1111, 2222); hash = direct seed 1111; sessions differ RUN | 123 (hash = ref 123) RUN | the HOME drawn seed (1111), if the plot was opened in HOME; else nothing |
| b no seed | default 0 (hash = ref seed 0) RUN | a fresh draw each session; differs from 0 RUN | default 0 RUN | the HOME drawn seed (1111): not the seed the export used (0) |
| c null | no seed, differs every render RUN | fresh draw each session (not "no seed", but one number per session) | no seed, differs every render RUN | HOME drawn seed, which the export did not use |
| d T3 pin 777 | n/a (T3 only in HOME/export) | 777, both sessions RUN | 777 RUN | 777 |
| d2 T3 pin 777 over recipe 123 | 123 | 777 | 777 | 777 (resolver lets the T3 pin win, plot_config_resolver.py:577-581) |
Gallery path (`render_example` -> `VizFactory().render(table, raw, plot_id)`, gallery_examples.py:124, real example jitter_strip, RUN): a 123 holds, b = seed 0, c differs per render. No override is passed, so the recipe is respected.

## 2. Plain answers
- Case (a): does HOME overwrite the recipe's seed with the per-session seed? YES. Proof: `_effective_random_state` returns `secrets.randbits(31)` whenever no T3 pin exists (home_theater.py:430-432); it never calls recipe_pins_random_state. The value goes in `aesthetic_override["random_state"]` (547-555); the resolver replaces every jitter layer's `random_state` (plot_config_resolver.py:577-582). RUN: HOME picture hash 85249a19ed = direct render with seed 1111, not 1385b9e4f5 (seed 123).
- Two HOME sessions, same picture? (a) NO, (b) NO (RUN, draws differ). Within one session the draw is re-made whenever home_state changes (the Calc reads the whole home_state; tab and collapse changes set it, home_theater.py:814, 1286) - READ, not run: the picture may change on a tab switch.
- Does the reproducibility export give the picture the user saw? (a) NO: exported plot uses 123, HOME showed the drawn number. (b) NO: export uses 0, HOME showed the drawn number, yet effective_run.yaml says the drawn number (1111): the recorded seed does not reproduce the exported plot (RUN: export hash = seed 0, not seed 1111). (c) NO (export draws again). (d) YES.
- No code reads seeds_per_plot back to re-render (grep app/ libs/: written only, export_handlers.py:1286-1318).
- Export warning (export_handlers.py:820-832) fires for every jitter plot opened in HOME, including recipe-pinned (a); text says "(random_state: random)". A plot never opened in HOME gets no warning and no seeds_per_plot entry (READ).
- READ: export collects T3 overrides only when t3_sandbox_enabled (export_handlers.py:870), but the Reshuffle button is not gated by it (home_theater.py:684-710): with the flag off, Reshuffle changes HOME and the export ignores it.

## 3. Where the code does not do what Eve decided (recipe seed holds; app warns)
1. home_theater.py:430-432 + 547-551: recipe-pinned seed replaced by a session draw (case a).
2. home_theater.py:430-432: case b/c also drawn, while rules_viz_factory.md s8 says default 0 and docs/user_guide/reproducible_plots.qmd:53-59 say "recorded 123" (a) and "program default 0" (b): the code records the HOME draw (export_handlers.py:1292-1294).
3. export_handlers.py:1039-1041: export passes only T3 overrides, so it cannot use the HOME draw: view and export differ for a, b, c.
4. export_handlers.py:820-832: warning wrongly includes recipe-pinned plots; says nothing when a pinned seed was overridden.
5. plot_config_resolver.py:577-582: no rule "recipe pin outranks an automatic draw"; only a T3 pin should win.
Intended text: rules_viz_factory.md s8 lines 117-124 ("a seed set on the layer wins over the factory's"; "default, not a rule"); ADR-090 decision 2 (architecture_decisions.md:4294, "same data and manifest give the same picture"; default 0; null/random = new arrangement every render); ADR-097 decision 2 (architecture_decisions.md:4823-4832: "For the default case (`random_state: random`, no pinned override), the seed actually drawn is remembered" - written for the unpinned case only, so a recipe pin was never meant to be drawn over).
Tests that pin today's behaviour: libs/viz_factory/tests/test_plot_config_resolver.py:341 (`test_overrides_a_recipe_set_seed`: L5 beats the recipe, legitimate for a T3 pin); test_reproducible_render.py (factory level only, all pass); app/tests/test_export_download.py:163 (only the key exists); test_export_provenance.py:108 (hash changes); test_shiny_smoke.py:790-840 (Reshuffle shown/hidden). NO test covers HOME's draw over a recipe pin, nor that the recorded seed equals the seed the export used.

## 4. Operators (value forms as the HOME dialog stores them; RUN on a 6-row table with one null)
| op | engine modif_filter | HOME dialog offers | HOME table path | plot path | export translator | Blueprint form |
|---|---|---|---|---|---|---|
| eq, ne | yes (all dtypes) | text/date/bool/discrete: yes (stored as in/not_in list); number: yes | yes | yes | yes for text, number; date and bool: translated, then the engine REFUSES (list of text vs Date/Boolean, RUN) | yes |
| gt ge lt le | yes (text, number, date) | number only; text, date, bool: no | yes | yes | yes (number) | yes |
| in, not_in | yes | text/date/bool/discrete: yes; number: no (unless scale_x_discrete) | yes | yes (text cast) | text ok; date/bool: engine refuses | yes |
| between | yes, `closed` both/left/right/none | number only; closed both or none only | yes | yes | NO: UntranslatableNode (t3_translator.py:75) | yes |
Null rows: table, plot and translator (`na: remove`) agree (RUN). The dialog has no `na` choice (engine has keep/remove).
## 5. Gaps
- Engine has, screen lacks: gt/ge/lt/le/between on text and date columns; closed left/right; na keep.
- Screen offers, later path refuses/ignores: (1) between in Send-to-Audit: translator raises, plot is skipped in the reproducibility recipe. (2) `closed: none` is lost when a between row goes to audit (filter_and_audit_handlers.py:481 builds params without closed; home_theater.py:375-380 rebuilds rows without closed): RUN, exploration gives [3.0], the audited row gives [2.0, 3.0, 4.0], silently inclusive. (3) Date and boolean filters: translated step fails at the engine (RUN). (4) Boolean filter in HOME returns the wrong rows: values are "True" but a Polars cast gives "true": `in ["True"]` keeps 0 rows, `not_in` keeps all (RUN, table and plot). (5) Latent: plot path casts a float column to text for in/not_in, the table path coerces to the dtype: in ["2","3"] gives [2.0,3.0] in the table, [] in the plot (RUN); not reachable from the dialog today. (6) Engine `between` with text bounds treats the text as column names (ColumnNotFoundError, RUN).
- `_op_label` (t3_audit_engine.py:30) has no `between`; OP_WORDS does (cosmetic).
Blueprint form: all 9 operators and all 4 `closed` values and na keep/remove are in the dropdowns (RUN); the schema `rules` (shape per op) are not enforced by the form, only by the engine at run.
