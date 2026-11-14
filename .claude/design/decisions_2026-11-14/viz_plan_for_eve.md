# Plan and questions: bringing the visualisation library to the recipe standard

Prepared 2026-11-14 by the coordinator with a state survey, an impact survey, three viewpoints and a verification run. **Nothing here is decided.** Eve decides; the review session records.

Evidence classes: RUN (proved by running code), READ (read in a file), INFERRED (reasoning, not checked).
Evidence files: `tmpAI/panel/viz/survey_state.md` (what the library has today, 15 concepts against the data side, numbers, 10 bad plot specs with the messages a user reads), `tmpAI/panel/viz/survey_impact.md` (who depends on it), `tmpAI/panel/viz/verify/results.md` (what the options would break), `tmpAI/panel/viz/brief_viz_standard.md` (the questions as asked).
Viewpoints: S = scientist and data scientist, A = architect (also effort), U = a recipe maker who is not a developer.

## 1. The goal
The plot layer (`libs/viz_factory`, plotnine 0.15.4) follows the same standard as the data side (Polars actions, recipe format 1): a recipe says exactly what is drawn, nothing is done silently, a wrong recipe is refused with a message that says how to fix it, and a colleague gets the same picture later.

## 2. Where the library stands (RUN unless marked)
- 191 components: geom 42, stat 22, scale 67, theme 17, facet 9, guide 10, position 8, coord 6, element 4, other 6. All have a description and a YAML example; 186 name the plotnine object they wrap.
- 125 pass straight through to plotnine; 66 add logic of their own. Nothing marks which; no test compares a component with the direct plotnine call.
- 22 component names exist in no plotnine (`facet_rows`, `guide_nrow`, `theme_dashboard`, ...). 29 plotnine objects have no component; the 12 `colour` spellings are refused.
- The parameter lists are written by hand: 13 to 15 declared parameters are refused by plotnine; 122 components accept any extra parameter.
- The checker judges a plot spec for: its keys, the target table, the presence of mapping, layers and a geom, the component names, and (only when given the catalogues) parameter names and the theme. It does not judge: value types, allowed values, required parameters, mapping keys, mapping columns, filters, the palette name.
- pytest for the library: 535 passed. The 194 test recipes are all in the old form (0 pass the checker); the integrity suite cannot run; no test fails when a component has no test. The README says "194 components, 98% pass" (`libs/viz_factory/README.md:154-158`): not true today.

## 3. Already decided (not asked again)
- `plot_engine: python-plotnine` is required in a recipe (DEC05); plot arguments are checked (DEC09); the tier-3 container sits on the plot entry (DEC17); `modif_filter` replaces the VizFactory filter vocabulary after its behaviour is verified (DEC39; not verified yet). Source: `recipe_format_spec.md` lines 92, 96, 109, 141.
- The same data and recipe give the same picture; random components are seeded (ADR-090). The seed is recorded per plot in the reproducibility export (ADR-097 decision 2; READ: `export_handlers.py:1286-1318` writes `seeds_per_plot` to `effective_run.yaml`, and the export warns about seeds that are not pinned).
- Parity with plotnine is a "MUST" (`rules_viz_factory.md` section 1).

## 4. Flags first
1. **Silent changes of a picture today (RUN):** a mistyped spec key (`theem: theme_bw`) renders without the theme and without a message; a filter with an unknown operator or column draws all rows; an `element_text` layer without a target is dropped. Seven such paths in total (question V6).
2. **HOME accepts what the gallery refuses (RUN):** HOME and Blueprint give the checker no parameter catalogue and no theme list, so `colr: red` and an unknown theme pass there (V5).
3. **A drawing error reaches the user raw (READ, not seen in a browser):** the app's `try` covers only `render`, which returns an undrawn plot; Shiny draws it afterwards. A `TypeError` from `size: big` is not caught by the app: the user most likely reads the raw error text in the plot area, with no plot or layer named (V7).
4. **Two records disagree on the parity decision:** `rules_viz_factory.md` section 1 cites ADR-036 for the parity "MUST"; in the ADR log, ADR-036 is "Persistent UI Integrity" (`architecture_decisions.md:452`). Option B of V9 changes that rule: your double confirmation.
5. **Option B of V10 reconsiders a recorded task** (RECIPE-MIGRATE-1, `tasks.md:130`: migrate the 194 files).
6. **The seed, two statements to reconcile (READ):** `rules_viz_factory.md` section 8 says the default seed is 0; `home_theater.py:432` draws a new random seed per session when a recipe uses jitter and does not pin one (and the export records it). Which is intended is for you to confirm.
7. **Good news, checked by running:** with the full check at HOME, 0 of 50 shipped recipes (16 recipes and 34 gallery examples) get a new error; and 0 of 72 shipped plot specs contain one of the silent cases. So V5 and V6 would change no shipped picture and refuse no shipped recipe. Not scanned: the 194 old test recipes, recipes that users upload.

## 5. The questions

| # | Question | Options | S | A (effort) | U | Coordinator's recommendation |
|---|---|---|---|---|---|---|
| V1 | Do names say what a component is? | A keep all names; a registry field `exact` / `modified` / `own`, shown in the help and the checker. B prefix every name (`plotnine_geom_point`). C prefix only the 22 names that are not plotnine's. | C, plus the field | A (small); B is large and breaks every recipe; C gives two naming rules | C: "no prefix = plotnine", and a snippet copied from plotnine documentation still works | **A now** (no recipe changes). C is your choice: it makes the name itself tell, but renames components in recipes. Not checked: how many shipped recipes use one of the 22 names (for example `theme_dashboard`). Not B. |
| V2 | What may a wrapper do? | A an `exact` component must equal the direct plotnine call, proved by a test for each; a `modified` one states its change. B leave. | A | A (medium; test generated from the registry) | not asked | **A.** It is what makes "exactly plotnine" a fact and not a hope. The 66 components with logic each get a stated change. |
| V3 | Where does the parameter list come from? | A read from plotnine at registration, with a list of what is not exposed and why. B hand-written, with a test that compares with plotnine. C names from plotnine, descriptions by hand. | C now, A later | A with a small hand overlay (large); first step is B's compare test, which exists as a ratchet | not asked | **A as the target, in two steps:** the compare test first, then the reading from plotnine with a hand overlay for descriptions and choices. |
| V4 | Is a layer's parameter judged? | A one rule set (unknown, required, shape, allowed values), as for data steps, used by the checker and the engine; every component strict. B checker only. C leave. | A, strict | A (medium), **after V3**: a hand-written type that is too narrow would refuse a valid value (example: `shape` declared as a number) | A: "size must be a number" before the run | **A, after V3.** The data side's rule set (`step_problems`) already accepts any name, values and schema (READ, A): shared code, no second checker. |
| V5 | The same check at HOME as in the gallery? | A give the full catalogues everywhere. B keep. | A | A (small) | A | **A, and it can be built now:** it follows the decided rule "one checker, one answer", and the run check shows no shipped recipe is affected. A user's own recipe with a wrong parameter would be refused at load with the fix, where today it fails at render. |
| V6 | The seven silent paths | A each becomes an error ("a component that cannot act fails"). B a warning. C case by case. | A; the filter cases wait for the filter decision | A for five paths (small each); the two filter paths wait for FILTER-UNIFY-1 | A: a warning in a log is not read | **A for the five; the two filter paths with FILTER-UNIFY-1** (proposals file D1 to D4). One existing test asserts the silent behaviour of `annotate` and is reversed. |
| V7 | Errors in one form | A the factory draws inside a checked call and turns every error into "what, which plot and layer, how to fix". B leave. | A | A (medium; a `draw_checked` helper so nothing is drawn twice; touches the app server, the export, the gallery) | A | **A.** Proposed message (U): "Plot 'p', layer 2 (geom_point): the value 'big' for 'size' is not a number. Fix: write a number, for example size: 3." |
| V8 | `plot_engine` is declared and read by nothing | A the factory refuses an engine it does not implement; the export records the plotnine version. B checker only. | A | A, reduced (small): the app picks the engine, which is the seam for a second engine later | not asked | **A.** Not checked: whether the plotnine version is already in the export's provenance. |
| V9 | Parity with plotnine, and spelling | A keep "MUST" and reach it. B what is registered is exact, what is missing is listed, a test reports new plotnine objects at an upgrade. Spelling: accept `color` and `colour`, or one spelling with "did you mean". | B, both spellings | B (small to medium); both spellings are plotnine's own names, generated in one list | both spellings: copied code must run | **B with both spellings.** It changes a rule file: your double confirmation. With V3 (pass-through components generated from plotnine) most of the 29 missing objects come at low cost anyway. |
| V10 | The 194 old test recipes and the dead suite | A migrate the files to format 1 and replace the suite by pytest driven by the registry. B drop the files and the suite; each schema's YAML example becomes its test, through a small generated recipe. C leave. | A, with the example as the test | B (medium): no second store of recipes, no migration that the tier-3 change would redo | B: the example a user copies is the one that is tested | **B.** It reconsiders RECIPE-MIGRATE-1 for these files: yours to decide. A component test proves three things: it renders and draws, it equals plotnine when `exact`, the same input gives the same picture. Stored pictures only for a few cases. |
| V11 | The seed | A the export records it; the checker advises to pin `random_state`. B as now. | A | already decided and built (ADR-090, ADR-097); add only the checker advice (small) | not asked | **Only the checker advice is new.** Confirm flag 6 (seed 0, or a new seed per session that is recorded). Not checked: whether `report.qmd` shows the seed. |
| V12 | Order of work | see section 7 | silent paths and the checks first | eight steps | not asked | section 7 |

## 6. What is impacted, and where (READ; details in `survey_impact.md`)

| Area | What | Touched by |
|---|---|---|
| The library | `registry.py`, the component files, `viz_factory.py` (render, filters, the silent paths), `arguments.py`, `plot_config_resolver.py` | V1 to V9 |
| Shared code in `libs/utils` | `step_problems` (reused as it is); a new shared module that reads a parameter list from a wrapped object, today inside `transformer/actions/polars_calls.py`; the recipe checker's plot checks (`recipe_check.py:683-727`) | V3, V4 |
| The app | `server.py` (creates the factory), `home_theater.py` (plot render, the uncaught draw error), `data_analysis_recipe_validator.py:111-112` (the catalogues given to the checker), `gallery_examples.py`, the export | V5, V7, V8 |
| Blueprint | the component picker and forms (`blueprint_arch/schema_registry.py`), the agent tool that lists components | V1, V3 |
| Recipes | 25 plot spec files under the pipelines, plot blocks in 45 template, retest and pipeline files, 34 gallery recipes: no change needed unless you choose V1-B or V1-C | V1 |
| Tests | 6 app test files that import the library; the 194 test recipes, 7 debug runners and the integrity suite of the library | V2, V10 |
| Audit scripts | `audit_data_analysis_recipe_coherence.py`, `audit_parity_coverage.py`, `audit_palette_registry.py` | V1, V9 |
| Records | `rules_viz_factory.md` (sections 1, 3 and 8), `rules_gallery_standards.md`, `rules_verification_testing.md` (the integrity suite), ADR-019, ADR-083, ADR-090; the library README; 5 documentation pages | all |

## 7. Proposed order of work (after your decisions; from the architect, adjusted)

| Step | Work | Depends on | Tag |
|---|---|---|---|
| 0 | Correct the README's "98% pass" to what is true today | nothing; no decision | `haiku/low` |
| 1 | V5: full catalogues at HOME and Blueprint, with a test that runs the shipped recipes through HOME's gate | your yes | `sonnet/low` |
| 2 | In parallel: V1-A registry field (`exact` / `modified` / `own`); V8 the factory reads `plot_engine`, the export records the plotnine version; the shared parameter-reading module moves to `libs/utils` | your yes | `sonnet/medium` each |
| 3 | V3: compare test, then parameter lists read from plotnine with a hand overlay | step 2 (shared module) | `sonnet/high` |
| 4 | V4: one rule set judges layer parameters, in the checker and the engine; `allow_extra_params` removed | step 3 | `sonnet/high` |
| 5 | In parallel: V2 and V10 (registry-driven tests: renders, equals plotnine, same picture; old files and suite removed); V9 (generated list, both spellings, upgrade test); V6 (five silent paths); V7 (one error form, `draw_checked`) | steps 3 and 4 for V2 and V10; V6 and V7 are independent | `sonnet/medium` to `sonnet/high` |
| 6 | The plot uses `modif_filter`; the two filter paths of V6 close | FILTER-UNIFY-1 and DEC39 (proposals file D1 to D4) | `sonnet/high` |
| 7 | The tier-3 reader (R1) | step 5 (so no recipe is migrated twice) | as planned |
| 8 | An ADR that records these decisions, and the rule files that follow | your decisions | `opus/high` |

The HOME rebuild can run in parallel; it only needs step 1 before its acceptance tests (A, INFERRED).

## 8. Not checked
How the app shows a drawing error in a real browser; the gallery render path and `app/tests/test_render_every_plot.py`; whether `report.qmd` shows the seed; whether the plotnine version is already in the export; how many shipped recipes use one of the 22 own names; `rules_viz_factory.md` sections 4 and 6 against the code line by line; the behaviour at a plotnine upgrade (no probe test exists); recipes that users upload.

## 9. What you decide
V1 names (field only, or also a prefix for own names). V2 exact means proved equal. V3 parameter lists read from plotnine. V4 one strict rule set. V5 the full check at HOME (can start now). V6 silent paths become errors. V7 one error form. V8 the engine is read. V9 the parity rule and the two spellings (rule file). V10 drop or migrate the 194 files (recorded task). V11 the seed: 0 or per session. The order of section 7.
