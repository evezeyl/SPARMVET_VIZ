# Recipe format: the decisions, the current state, the plan and the questions (2026-11-13)

**Written for:** Eve, to confirm the scope and answer Q1-Q6 before any recipe, validator or rule file is changed.
**Status:** review only. Nothing in code, recipes, rules or docs was changed. Done today: the six audit reports of 2026-11-12 were triaged (commit `e3865b59`).
**Evidence labels:** *verified* = read at file:line or run today; *reasoned* = follows from verified facts; **DECIDED / CONFIRM / OPEN / MINE** as in the memory rule "check what is decided first" (DECIDED = you decided it and it is written; CONFIRM = written with `[confirm]` or only recommended; OPEN = not decided; MINE = my interpretation or proposal).

## 1. What I read

`home_audit_reading_guide.md` (all), `home_audit_steps.md` sections 1-5a, 8-11, 16 (points 1-21 of 5a), ADR-099 (all 16 points), `recipe_review_st22_2026-11-11.md`, `home_observations_and_future.md`, `tasks.md` (the recipe tasks), the loader, the validator, `legacy_keys.py`, the recipe tests, the gallery manager, and all shipped recipes (scan below).

## 2. The decisions that change how a recipe works

| # | Decision | Tag | Written in | What it means |
|---|---|---|---|---|
| D1 | Two **required** top-level keys, `data_engine: python-polars` and `plot_engine: python-plotnine`; an unknown value is a failure; overrides per collection / plot entry later | DECIDED | `home_audit_steps.md:163` (5a-21); ADR-099 16(j) | every recipe, template, gallery bundle and the Blueprint "new recipe" form gets two lines; recording engines and versions in the keys comes later (KEYS-NODE-1) |
| D2 | `entity:` with `noun`, `plural`, `population` (the table with one row per unit); without it the software says "entities"; never guessed from column names | DECIDED; the checks (population table exists and carries the key) MINE, from the task text | `:148` (5a-17); `tasks.md:60` | optional key; checked when present |
| D3 | `label` and `description` on **every** element: recipe `info`, group, plot, join (table), data schema. A plotted table without a description gets an *advice*, never a block | DECIDED | `:140`, `:147` (5a-9, 5a-16) | today 37 of 37 schemas and 31 of 31 joins have no `label` |
| D4 | Old names: `info` on plots / datasets / tables and `display_name` in the recipe `info:` are retired (warning first, refusal later) | DECIDED; **the new name of each is OPEN** (Q3) | `:140` | 25 plot entries, 12 schemas and 15 of 16 recipes use an old name; the code reads `display_name` in 2 places (`home_theater.py:903`, `blueprint_mapper.py:76`) and 3 writers emit it (bootstrapper, scaffolder, `create_data_analysis_recipe.py`); the Blueprint form writes `info.name` from a field called "Display name" (`blueprint_handlers.py:2670`) |
| D5 | **Fail instead of warn.** Everything written in a recipe is executed or the recipe is rejected with the reason. HOME's load gate rejects; Blueprint reports and never blocks building (empty placeholders accepted). Four failures: a step list that is never applied; an unknown action, key or parameter; a column missing at that node (dry run on column names); a step that fails on the data | DECIDED (the list of four is mine, you confirmed it) | `:161` (5a-19); `tasks.md:66` | the validator sees none of the first three today (verified, section 4) |
| D6 | One rule set `check_recipe` in `libs/utils`; the loader builds the recipe and stops on errors; the validator reports every problem; the data check stays separate | DECIDED (O1) | ADR-099 16(g) | design detail MINE: `libs/utils` cannot import `transformer`, so the actions and their parameters are handed in by the app layer (as `schema_registry` already does) |
| D7 | Every table has T1, T2, T3 with or without a join. A data schema plotted directly is a collection and **its own tier-2 list is its T2**. Tier-2 on a dataset that is only an ingredient is a failure | DECIDED; engine change in `libs/transformer` allowed, tests first (O4) | `:149` (5a-18); `tasks.md:64` | verified today: `ResFinder` tier-2 (`count_by_group`, `sort`) is silently ignored |
| D8 | Explicit optional T3 container at the plot entry, any registered action | DECIDED as principle; **the name is a placeholder** | `:146` (5a-15); `home_observations_and_future.md:20` | Q5 |
| D9 | `is_primary_key` becomes `is_entity_key` (warn first, refuse later) | **CONFIRM/OPEN**: the guide lists it as my recommendation; the task lists it as part of the format | `home_audit_reading_guide.md:110` (O9); `tasks.md:61` | Q4 |
| D10 | Recipe shapes must keep working: no join, no key, another key name, no population table, long format. The shipped recipes are the test fixtures | DECIDED | `:149-160`; `tasks.md:63` (TEST-SHAPES-1) | do **not** add keys to the keyless recipes (`2_test_data_ST22_dummy`, `figshare_integration`) |
| D11 | Formulas (`mutate` expressions, plot function strings) may use only an allowed list of Polars operations, by function name, inside the same recipe validation | DECIDED in principle; **the list is OPEN** | ADR-099 point 14; `:347` | Q8 |
| D12 | Development rules: a wrong recipe is corrected, never protected by a compatibility default; every step complete; tests adapted first and failing for the right reason on the current code | DECIDED | ADR-099 16(a)-(c) | sets the order of work (section 5) |
| D13 | ST22 test recipe R1-R4 (anchor without ResFinder, "none detected" explicit, phenotype score without unknown, MLST title with the years, virulence tiles) and descriptions with grain and missing-value treatment | DECIDED | `recipe_review_st22_2026-11-11.md:105`; `tasks.md:67` | already tracked: #67, #69, #70 |
| D14 | Rule files change only with your double confirmation; configuration files are adapted at the end | DECIDED | `rules_verification_testing.md` section 5; `CONFIG-REVIEW-1` | I draft, you confirm, then I apply |

**Decided but not part of this package** (not touched): removing `developer_raw_yaml`, the missing-value rule (#63), keys per node, the recipe graph, audit mode, Import gating, configuration renames.

## 3. Where the texts disagree (stop-and-confirm)

1. **Unknown keys: warning or failure?** ADR-099 16(g) (`architecture_decisions.md:5022`) and the first paragraph of UNKNOWN-KEYS-1 (`tasks.md:66`) say "warnings, never a block". 5a-19 (`home_audit_steps.md:161`) and the UPDATE in the same task say fail. The later text is yours; I follow it and would correct the ADR sentence. (Q2)
2. **"Warn first, refuse later" against "no compatibility default".** 5a-9 and O9 say warn first. ADR-099 16(a) says a wrong recipe is corrected, not protected. The repo already has the other precedent: `legacy_keys.py:9-16` refuses an old key at once, with the new name and a migration script. I propose refusing at once, since all shipped recipes are migrated in the same change. This reconsiders a decided text, so it is your call. (Q3)
3. **O9 status** (D9 above): written as a recommendation in one place, as part of the format in another.
4. **The T3 container is still a placeholder** (name and place), while the reading guide says nothing waits for you. Under D5 a key nobody executes would have to be rejected, so I propose to leave it out until audit mode is built. (Q5)
5. **The two recipe audits are blind to all of this.** `audit_data_analysis_recipe_*` and `..._coherence_*` pass 7 of 7 recipes on 2026-11-11 (already noted in that triage: they cannot see a many-to-many join or an ignored plot-spec key). They check the pipelines folder only. They will keep passing while a recipe breaks D1-D7. (Q10)
6. Cosmetic: ADR-099 lists its points in the order 10, 16, 15, 14, 13, 12, 11. Not changed.

## 4. Current state (verified 2026-11-13)

**Kinds of recipe file**

| Kind | Files | Loaded by the recipe loader? | Notes |
|---|---|---|---|
| Pipelines | 7 | yes | `1_Abromics_general_pipeline`, `1_test_data_ST22_dummy`, `2_test_data_ST22_dummy`, `3_test_no_joins`, `demo_abromics`, `figshare_integration`, `stress_test_master` |
| Templates | 5 | yes | covered by `test_every_template_is_a_valid_data_analysis_recipe` |
| Retest | 4 | yes | named as faulty scenarios (`bad_output_field`, `broken_header`, `tier2`, `top_n_other`); I have not checked what each is meant to show |
| Transformer test fixtures | 68 (`libs/transformer/tests/data`) | **no**: rejected, no `analysis_groups` (run today) | inputs of the action tests; `libs/transformer` is independent of the app |
| Legacy | 2 (`config/.../VIGAS-P/VIGAS_VirulenceFinder.yaml`, `assets/ref_data/.../Virulence_genes_APEC_...yaml`) | **no**: no `analysis_groups` | I found no code that reads them; not yet checked further |
| Gallery bundles | 34 | **no**: rejected, root `plots:` (run today) | other shape: `info` (taxonomy), `data_path`, `plots`, `wrangling`; no test validates it as a recipe |

**The 16 loadable recipes against the decided format** (`tmpAI/recipe_format/scan_compliance.py`, scratch, not committed; full result in `tmpAI/recipe_format/scan.json`)

| Measure | Result |
|---|---|
| `data_engine` / `plot_engine` / `entity` present | 0 / 0 / 0 of 16 |
| unknown top-level keys | `description` in `2_test_data_ST22_dummy`; `metadata` in `complex_template` |
| `label` missing | schemas 37 of 37, joins 31 of 31, plots 24 of 39, groups 10 |
| `description` missing | schemas 37 of 37, joins 15 of 31, plots 22 of 39, groups 11 |
| old names | `display_name` in 15 of 16 `info:`; `info` on 25 plot entries and 12 schemas |
| `is_primary_key` declared | 29 schemas; 8 without (the keyless shapes and a reference table) |
| dataset tier-2 that is silently ignored | 1: `ResFinder` in `1_test_data_ST22_dummy` (it is plotted directly by `amr_heatmap` and also an ingredient) |

**What the checkers do today** (verified by reading): the validator checks `id` equals the file name and the shape of each step list (`app/modules/data_analysis_recipe_validator.py:101-140`); the loader checks renamed keys, root `plots:`, `analysis_groups`, and that each schema has `source` (`libs/utils/src/utils/config_loader.py:141-211`). Nothing reports an unknown key, a missing engine, a bad `entity`, an old name, a tier-2 list that is never applied, or an unsafe formula. Earlier probe (`tmpAI/architect/unknown_keys.py`): an unknown top-level key and a typo key give 0 problems.

**Who writes recipes** (must emit the new format): Blueprint "new recipe" form (`app/handlers/blueprint_handlers.py:2614-2670`), `libs/test_lab/.../bootstrapper.py:154`, `.../scaffolder.py:182`, `assets/scripts/create_data_analysis_recipe.py:177`, `SF_create_data_analysis_recipe.py`, and the forked recipe of the export (copies the original, so it follows).

**Documentation that describes the format:** `.claude/rules/rules_data_analysis_recipe_structure.md`, `docs/appendix/data_analysis_recipe_structure.yaml`, `docs/appendix/Standards_yaml.qmd`, `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd`, `docs/workflows/wrangling.qmd`, `docs/workflows/blueprint_architect.qmd`, `README.md`, plus about 50 files that mention `is_primary_key` and 32 that mention `display_name`.

**Baseline before any change:** headless suite 1652 passed in 99.65 s (command of `rules_verification_testing.md` section 8).

## 5. Proposed order and work packages

Your order was: review decisions, docs, recipes, then tests and validators. Two changes, both from your own development rules (ADR-099 16(b)-(c)): write the format specification first (that is the docs step, and the tests need it), and write each package's tests before its code and before the recipe edits, so that they fail for the right reason on today's recipes. Each package is one revertible commit, `Refs: evezeyl/SPARMVET_VIZ#N`.

| Pkg | What | Model/effort | Needs from you |
|---|---|---|---|
| A. RECIPE-SPEC-1 | One page: the allowed keys at every level (top level, data schema, join, step list, plot entry, plot spec, `plot_defaults`, `info`, `entity`), required or optional, old name to new name, one example per shape. Goes into `docs/appendix/data_analysis_recipe_structure.yaml`; the rule file text is drafted for your double confirmation | `[opus/high]` | read it; confirm the rule-file diff |
| B. RECIPE-TESTS-1 | Tests from A: one small bad recipe per failure (HOME refuses, Blueprint reports), one per shape (TEST-SHAPES-1), every shipped recipe of every kind through the checker. They fail first on today's code | `[opus/high]` | - |
| C. UNKNOWN-KEYS-1 + RECIPE-FORMAT-1 (checker) | `check_recipe` in `libs/utils` (engines, entity, names, unknown keys with did-you-mean, tier-2 rule, step lists); loader stops on errors; validator reports all; app injects the action catalogue. #66 (plot-spec keys) is folded in | `[opus/high]` | Q2, Q3, Q5 |
| D. RECIPE-DATASET-TIER2-1 | Engine applies a directly plotted dataset's own tier-2 | `[opus/high]` | Q6; @verify with before/after pictures of `amr_heatmap` |
| E. Recipe sweep | Engine lines, names, entity and descriptions in the 16 recipes; the writers listed above; templates; gallery (if Q1 says yes) | `[sonnet/medium]` per kind | Q1, Q3, Q4, Q7 |
| F. RECIPE-ST22-FIX-1 | R1-R4 and the grain/missing-value descriptions (already agreed) | `[opus/high]` | pictures looked at together |
| G. Documentation sweep | the docs listed in section 4, glossary, UML check (`audit_uml_model.py`), ADR-099 sentence of 3.1 | `[sonnet/medium]` | double confirmation of rule files |
| H. Formula allowed list (P9) | rule in `check_recipe`, list derived from all shipped recipes | `[opus/high]` | Q8: you approve the list |
| I. AUDIT-REFRESH-1 | the two recipe audits call `check_recipe` over every kind, so they stop passing blind | `[sonnet/medium]` | Q10 |

Walking order: A, B, C first (they make the problems visible), then D, E, F, G; H and I after C. Estimated: several sessions, not one.

**Issues** (standing rule: file first, close with a comment that gives root cause and evidence). One tracking issue "Recipe format: implement the decisions of 2026-11-11/12" with the checklist above, and one issue per package A-I. Existing issues are linked, not duplicated: #66 (folded into C), #67, #69, #70 (F), #61.

## 6. Questions for you

**Blocking (I wait for these):**

- **Q1. Which files take the new format?** (a) the 16 loadable recipes: yes. (b) the 68 transformer test fixtures: *I recommend no*; they are inputs of action tests, they cannot load as recipes, and they would get their own light check (parses, every action is registered). (c) the 2 legacy files: *I recommend we check if anything uses them and delete or convert them, your call.* (d) the 34 gallery bundles: your task says they get the two engine lines. They have another shape and no validator; *I recommend yes, with a small gallery-kind check in the same checker.*
- **Q2. Unknown key = failure** (HOME rejects, Blueprint reports), and I correct the ADR sentence that says "warning"? Sub-question: the plot spec carries descriptive keys (`family`, `pattern`, `difficulty`, `description`, `info`) and the two stray top-level keys (`description`, `metadata`). *I recommend: allow the first four as documented optional keys, and remove the two stray ones.*
- **Q3. Old names: refuse at once or warn first?** *I recommend refuse at once* (like `join_manifests`), because every shipped recipe is migrated in the same change. And the new names: recipe `info.display_name` to `label`; plot entry `info:` (a sentence) to `description`; **what replaces a schema's `info: {category, sub_category}`?** Blueprint's map reads `sub_category` (`blueprint_mapper.py:76`). Options: keep `category` and `sub_category` as documented keys; fold into `description`; drop.
- **Q4. `is_primary_key` to `is_entity_key` now?** *I recommend now*: 29 schemas and about 50 files are touched anyway, a second sweep costs more. It also changes `libs/transformer/.../data_wrangler.py`, `wrangle_studio.py`, the bootstrapper and scaffolder.
- **Q5. T3 container: leave out of the schema until audit mode is built?** *I recommend yes* (D5: nothing executes it; the name is still open).
- **Q6. Dataset tier-2 engine fix in this change?** *I recommend yes.* It changes a figure: `amr_heatmap` would get `total_gene_count` and be sorted by it (verified from the recipe, not yet run). I would show before and after for your @verify.

**I go on with my recommendation unless you object:**

- **Q7. Descriptions and labels.** Labels from the ids (mechanical). Descriptions: I write factual ones (grain from the file headers) for the test recipes, templates and ST22; for `1_Abromics_general_pipeline` and `demo_abromics` (the ones the local deployment opens) I draft and mark them for your review, because the population is a domain statement.
- **Q8. Formula allowed list (P9):** separate package H after C; I derive the list from all shipped recipes and you approve it before it is enforced (security-relevant).
- **Q9. Rule files:** I draft the diff of `rules_data_analysis_recipe_structure.md` (and the T3 / dataset tier-2 sentences in `rules_data_engine.md` if needed) and show it before applying.
- **Q10. The old audits:** add package I, and add the new checks to the weekly Wednesday run.

## 7. Not done, and will not be done without your OK

No recipe, rule file, ADR text, UML or code was edited. No issue was opened yet (I wait for Q1-Q6 so the issues have the right scope). `libs/transformer` is not touched before Q6 and tests. No configuration file is touched (`CONFIG-REVIEW-1`).
