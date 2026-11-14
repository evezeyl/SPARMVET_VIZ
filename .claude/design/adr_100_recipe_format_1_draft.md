# ADR-100 draft: Recipe format version 1

**For Eve to read and confirm.** This file is not the ADR log. After Eve's yes, the text from the heading "ADR-100" onward
moves into `.claude/knowledge/architecture_decisions.md`; the section "Discrepancies for Eve" stays here.
**Written:** 2026-11-14, from `.claude/design/recipe_format_spec.md` (cited as "spec") and the code of branch
`feat/recipe-format-1` at commit `27f7a2e3`. It records decisions already taken (DEC45); it adds none.
**Status words:** BUILT (file:line), PARTLY (what is built and what is not), NOT BUILT (task in `.claude/tasks/tasks.md`),
NOT VERIFIED (no code found to prove it either way).

## Discrepancies for Eve (to settle before the ADR is accepted)

| # | The spec says | The code or another record says |
|---|---|---|
| D1 | `categorical` becomes `String`, refused with "this was String" (DEC27, spec:124; spec 7.4, spec:373; spec 12, spec:681; evidence `home_evidence/actions_and_polars_2026-11-13.md`:268 quotes Eve) | the migration writes `Categorical` and the checker suggests it: `libs/utils/src/utils/recipe_spec.yaml`:104-106; commit `e9ac815f` ("categorical stays Categorical": String would change the level order of plots); the shipped recipes hold 75 `type: Categorical` |
| D2 | `modif_` and `step_` actions name input columns `columns` (a list), outputs `new_column(s)` (DEC15, spec:115) | `modif_filter` takes `column` by decision (DEC39, spec:141), and `step_top_n_other` takes `column` (`libs/transformer/src/transformer/actions/composite.py`:46). The spec contradicts itself and the code follows DEC39 |
| D3 | field `label` is the default axis and legend title, "Built under #91" (DEC22, spec:114) | no code found: `viz_factory.py`:365-370 applies only an explicit `labels` block; no commit names #91. Marked NOT VERIFIED below |
| D4 | about 12 `step_` and 9 `modif_` actions remain (spec 7.5.1, spec:417) | the registry has 41 actions: 39 `polars_`, 1 `modif_` (`modif_filter`), 1 `step_` (`step_top_n_other`); `polars_group_by` and `polars_str_splitn` replace `summarize`, `split_column`, `split_column_to_parts` (commit `d07fe567`, quoting Eve: "where Polars can do it, the Polars action and nothing else"). Evidence section 25 (evidence:314) still says five `step_` stay. The spec text is out of date; the decision behind the smaller set is not in the DEC table |
| D5 | the migration is "one tool, two runs" (DEC43, spec:150) | the tool has four runs, A to D (`assets/scripts/migrate_recipe_format.py`:62): C removed `final_contract` (CONTRACT-REMOVE-1, tasks.md:199), D the strict forms (GATE-CHECKER-1, tasks.md:195) |
| D6 | "Nothing is built from it yet except the registry fixes of issue #87 and the strict import" (spec:4); Q2, Q3, Q4 are open (spec:189-191) | most of the format is built (table below); Q2 `derive_categories` is removed (not in the registry; evidence:320); Q3 answered "option A" (tasks.md:200); Q4 answered "NA = not recorded" (tasks.md:206) |

---

## ADR-100: Recipe format version 1 (DRAFT, 2026-11-14)

**Status:** DRAFT, awaiting @evezeyl. Decisions taken by Eve on 2026-11-11 to 2026-11-13 (dates per row). Authority: @dasharch.
**Source:** `.claude/design/recipe_format_spec.md` sections 2.1 (DEC01 to DEC49) and 3 to 18; issues #73 (parent), #74 to #89.
**Supersedes:** ADR-013 (Dual-Validation Manifests) and ADR-014 (Identity Logic for Wrangling), DEC23.
**Amends:** ADR-090, wording of the order rules (DEC34; text below).
**Consistent with:** ADR-041 (container forms, DEC08), ADR-099 point 16 (development rules; DEC02 cites 16(a)).

### Context

Before format 1 a recipe could be wrong without anyone knowing. The loader tolerated old keys and old forms, repaired an
unquoted `on`, and removed fragment wrappers silently (spec 16). Unknown keys were ignored (UNKNOWN-KEYS-1). Actions had
hidden defaults that changed which rows a figure counts: a sanitiser turned the text `NA` (Namibia) into a missing
value; `keep_columns` put keys first; filters dropped missing values without a word (spec 7.3, 7.5.1). Four lists of field
types disagreed (spec 7.4). `final_contract` was a second, hidden place where columns were selected, and a list-form
contract was skipped silently (spec 5). Eve's rule (spec:8): the recipe describes the science; what it specifies must be
done; nothing may be hidden. Format 1 makes every recipe explicit, versioned and checked by one function.

### Decisions

**A. Scope, version, engines**

| # | Decision | Source | Status |
|---|---|---|---|
| 1 | Every recipe is in format 1: pipelines, templates, retest, gallery, transformer and viz-factory test recipes, recipes written by the app, recipes inside tests | DEC01, spec 3 | PARTLY: shipped recipes pass (`app/tests/test_shipped_recipes_pass_the_checker.py`); gallery 33 of 34 (GALLERY-RIGOR-1); one pair per action (ACTION-RECIPES-1). NOT BUILT: the 194 viz-factory test recipes (RECIPE-MIGRATE-1, #89; WRITERS-W8-1 decision 3) |
| 2 | `spec_version: 1` (an integer) is required; unversioned recipes are format 0; another version is refused and the message names the migration tool (V01-V04) | DEC04, spec 4.1 | PARTLY: checks `recipe_check.py`:178-189; all 16 shipped recipe files carry it; writers emit it (`recipe_factory.py`:162). NOT BUILT: recorded in `effective_run.yaml` and by the importer (RECIPE-FORMAT-VERSION-1) |
| 3 | `data_engine: python-polars` and `plot_engine: python-plotnine` are required | DEC05, spec 4 | BUILT: `recipe_spec.yaml`:6-8, `recipe_check.py`:191-194 |
| 4 | Every element has a `label`; a missing `description` is an advice, never a block | DEC06, spec 13 | BUILT as checks: `recipe_check.py`:208-210, 280-281, 471-472, 638-639, 662-663. The descriptions themselves: RECIPE-MIGRATE-1 |

**B. File shape and keys**

| # | Decision | Source | Status |
|---|---|---|---|
| 5 | Unknown keys fail; old names are refused at once and the message names the new one; no compatibility default | DEC02, spec 12 | PARTLY: `recipe_check.py`:124-136 with the table `recipe_spec.yaml`:59-101. An old action name gets a spelling suggestion only: the checker can name the new action (`recipe_check.py`:424) but the app passes no old-name table (`app/modules/data_analysis_recipe_validator.py`:106-112) |
| 6 | Containers follow ADR-041: named things are dictionaries, ordered operations are lists, `analysis_groups` and `plots` are ordered dictionaries; a wrong form is refused with the corrected text | DEC08, spec 5 | PARTLY: step containers and fields `recipe_check.py`:340-342, 378-396; duplicate keys refused by the new loader (`recipe_loader.py`, T10). NOT VERIFIED: one test per check that the message holds the corrected text; `sort_keys=False` at every writer |
| 7 | `#` comments are free and kept by every tool; a `comment` key on info, schema, join, group, plot, step and layer; `comments` is refused | DEC07, spec 6.2 | PARTLY: `comment` and CM01 `recipe_check.py`:206, 282, 416, 473, 640, 664, 711; `comments` refused `recipe_spec.yaml`:80. NOT VERIFIED: writers keep `#` comments |
| 8 | The schema-level `info`, `category`, `sub_category` are dropped; the recipe-level `info` stays free-form | DEC20, spec 7.1 | BUILT: `recipe_spec.yaml`:74-79 |
| 9 | The two legacy recipes are removed (`config/data_analysis_recipes/VIGAS-P/`, `assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_data_analysis_recipe.yaml`) | DEC12 | BUILT: both paths are gone |

**C. Fields, types, missing values, paths**

| # | Decision | Source | Status |
|---|---|---|---|
| 10 | `is_primary_key` becomes `is_entity_key` | DEC13 | BUILT: `recipe_spec.yaml`:82, `recipe_check.py`:353. One fragment that no recipe includes still has the old key (`1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml`) |
| 11 | Strict import: only declared `input_fields` are read; a declared column missing from the file fails; `original_name` matches exactly; the import reports the columns it left out | DEC24, DEC25 | BUILT: `libs/ingestion/src/ingestion/ingestor.py`:91-129 |
| 12 | `type` is required and is any Polars dtype a text file can hold; the dtype is given to the reader, which fails and names the value; `Enum` levels are `categories`; old type names are refused | DEC27, spec 7.4 | PARTLY: `polars_types.py`:43, `recipe_check.py`:359-372, `ingestion/declared.py`:46-117. What `categorical` becomes: see D1 |
| 13 | Missing values have no default: `null_values` (a list, `[]` allowed) and `strip` (true or false) on every schema, with an optional per-field override; read as text, apply them, then cast | DEC28, spec 7.3 | BUILT: `recipe_check.py`:329-338 (S09), `declared.py`:35-43, 93-95; the hidden sanitiser is gone (no `sanitizer.py` in `libs/ingestion`) |
| 14 | The id-first rule is a recommendation done by steps; no code enforces it; ingestion imposes no column order | DEC26 | BUILT: `polars_select` and `polars_drop` carry no key rule (`polars_calls.py`:69) |
| 15 | Paths: no engine change; the deployment's `data_lookup` decides; a development `source.path` is not absolute, has no `..`, `~` or URL | DEC30, spec 15 | BUILT: `recipe_check.py`:319-327 (PA01, PA02), `recipe_paths.py`:22, 41 |

**D. Steps and action names**

| # | Decision | Source | Status |
|---|---|---|---|
| 16 | Column-name aliases are removed; nothing is guessed between spellings | DEC14, spec 7.5 | BUILT: `data_wrangler.py`:22; `test_actions_must_act.py`:68 |
| 17 | One parameter name per role in `modif_` and `step_` actions; Polars names in `polars_` actions | DEC15 | NOT VERIFIED: see D2 |
| 18 | Prefixes `polars_`, `modif_`, `step_`; the registry field `polars` (exact, wrapper, modified, composite) says the same | DEC31 | BUILT: all 41 names prefixed (registry read at run); `libs/transformer/tests/test_registry_polars_rules.py`:131-138 |
| 19 | A `polars_` action is exactly Polars, proved by a test against the direct call | DEC32 | BUILT: `libs/transformer/tests/test_polars_actions_equal_polars.py` |
| 20 | No hidden choice: a behaviour parameter is required or has the Polars default | DEC33 | BUILT: `test_registry_polars_rules.py`:140-151 |
| 21 | Determinism is a required parameter, not an action default | DEC34 | BUILT: required in the registry: `polars_sort` (`by`, `maintain_order`), `polars_unique` (`keep`, `maintain_order`), `polars_join` (`how`, `maintain_order`), `polars_sample` (`seed`; `n` or `fraction` by a rule), `polars_group_by` (`maintain_order`) |
| 22 | One name per action, no alias, no second action for one Polars method | DEC35 | BUILT: 41 distinct names |
| 23 | Several-call actions may stay as `step_` when simple and documented; no action returns the table unchanged on a missing parameter or column | DEC36 | BUILT: `test_actions_must_act.py`:54-68 (no `xfail` left). The set that stays: see D4 |
| 24 | `polars_select` and `polars_drop` replace `keep_columns` and `drop_columns`: plain, strict, names only | DEC37 | BUILT: `polars_calls.py` |
| 25 | `polars_with_columns` takes a mapping column to formula; `mutate` and `add_constant` are removed | DEC38 | BUILT: `named_exprs`, `polars_calls.py`:70; neither old name is registered |
| 26 | `modif_filter` (`column`, `op`, `value`, `na`) replaces the five `filter_*`, `is_in`, `not_in`; `na` is required | DEC39, DEC29 | BUILT: `actions/modified.py`:74; all four required (registry read at run); `test_modif_filter.py`. `polars_filter` waits by decision |
| 27 | `percentile` is removed | DEC40 | BUILT: not registered |
| 28 | Polars methods without an action are deferred; `polars_fill_nan` and `polars_drop_nans` are added | DEC41 | BUILT: both registered |
| 29 | `scan_parquet` and `sink_parquet` are engine functions, not recipe actions | DEC42 | BUILT: `libs/transformer/src/transformer/anchor.py`:19, 36 |
| 30 | A cast never loses information: a float-to-integer cast that would drop decimals fails and names the value | DEC49 | BUILT: `polars_calls.py`:358-374 |

**E. Joins and published columns**

| # | Decision | Source | Status |
|---|---|---|---|
| 31 | `final_contract` and the schema `output_fields` are removed; the published columns are the last tier-1 step (`polars_select` or `polars_drop`); display names go in `labels` on the collection | DEC23, spec 7.6 | BUILT: CONTRACT-REMOVE-1 (tasks.md:199); refused `recipe_spec.yaml`:62-64, 86-87; `labels` J06 `recipe_check.py`:481-483; cache version "4" `app/modules/cache_keys.py`:42 |
| 32 | J08: a non-key column in both tables of a join is an error with guidance (Polars renames it `name_right` silently) | DEC19, spec 5.2 | PARTLY: the check `recipe_check.py`:599-619 runs only with a recipe graph; the graph is NOT BUILT (RECIPE-GRAPH-UTILS-1) and the app passes none (`data_analysis_recipe_validator.py`:120) |

**F. Plots**

| # | Decision | Source | Status |
|---|---|---|---|
| 33 | A schema plotted directly applies its own tier 2; on a schema that is only an ingredient `tier2` is an error | DEC16, spec 7.3 | PARTLY: the error S07 `recipe_check.py`:299-301. NOT BUILT in the engine: `tier2_steps` reads joins only (`cache_keys.py`:90-95; RECIPE-DATASET-TIER2-1, #77) |
| 34 | The plot entry holds `steps: {tier3: [...]}`; the engine must read it; until then a non-empty list is refused (P05) | DEC17, spec 7.7 | PARTLY: container and P05 `recipe_check.py`:41, 666-674. NOT BUILT: the engine reader (stage-2 package P5, STAGE2-SPEC-1) |
| 35 | The gallery taxonomy is `taxonomy` on the plot entry, not part of a plot spec; `description` is on the plot entry | DEC21 | BUILT: `recipe_spec.yaml`:40, 94-96 |
| 36 | Plot axis and legend titles default to the field `label` | DEC22 | NOT VERIFIED: see D3 |
| 37 | The registries are fixed and plot arguments are checked against the component schema and the plotnine function | DEC09, spec 8 | BUILT: PS04 `recipe_check.py`:701-727, catalogue `data_analysis_recipe_validator.py`:111-112. Open: 13 refused plotnine arguments (#88) |
| 38 | Gallery examples are standard recipes in profile `gallery`, `taxonomy` required, terms in the specification data file | DEC47, spec 9 | PARTLY: 33 of 34 (tasks.md:166); `beeswarm_sina` waits for the tier-3 reader (tasks.md:167) |
| 39 | The checker runs at index rebuild, at app start and in the tests; previews come by the app's path; the tag strip is generated | DEC48 | BUILT: GALLERY-RIGOR-1, GALLERY-CHECK-START-1 (tasks.md:166-168) |

**G. The checker and its profiles**

| # | Decision | Source | Status |
|---|---|---|---|
| 40 | One checker `check_recipe` in `libs/utils` for HOME, Blueprint, importer, gallery, scripts and tests | DEC03, spec 14 | PARTLY: `recipe_check.py`:799; used by HOME's gate and Blueprint's Validate (`data_analysis_recipe_validator.py`:115-140, GATE-CHECKER-1). `ConfigManager` still repairs an unquoted `on` and unwraps fragments silently (`config_loader.py`:18-41, 108-116) |
| 41 | Profiles `run`, `build`, `gallery`, `audit`; the app writes step ids `audit_<8 hex>_<k>`; an author writes none | DEC18, spec 3, 7.5 | BUILT: `recipe_check.py`:46-47, 407-415 |
| 42 | A bad recipe must not run code or read or write where it should not | DEC44, spec 15 | PARTLY: formula check `libs/utils/src/utils/formula_check.py`, used at `polars_calls.py`:203, `geoms/core.py`:1320, `id_reconciliation/core.py`:253 and as ST06 `recipe_check.py`:436-450; `!include` confined (`config_loader.py`:58-80, T11). NOT VERIFIED: zip import, `report.qmd` (SECURITY-RECIPE-1) |

**H. Process**

| # | Decision | Source | Status |
|---|---|---|---|
| 43 | Migration by one tool, text level (comments kept), a golden baseline first, every table difference shown to Eve, one cache bump at release | DEC43, spec 4.1 | BUILT: `assets/scripts/migrate_recipe_format.py`, `app/tests/test_golden_baseline.py`, `cache_keys.py`:42. Number of runs: see D5 |
| 44 | Errors of a recipe from a data-science point of view are fixed, not documented | DEC10, spec 18 | NOT BUILT: RECIPE-ST22-FIX-1 (#67, #69, #70) |
| 45 | The worked example is `1_test_data_ST22_dummy` | DEC11 | a documentation choice; nothing to build |

DEC45 is this ADR. DEC46 is a note, not a decision (`UTILS-REUSE-REVIEW-1`, `DOCKER-RELEASE-1`).

**What is refused, with which message** (spec 11, 12; message form `recipe : path : [code] what. Fix: what to write`,
`recipe_check.py`:76-80): an unknown key (the replacement or a did-you-mean); a missing version (V01, "run the migration
tool"); an old type name (the Polars name); `final_contract` or `output_fields` ("end the step list with a polars_select
step"); a flat or empty step list (`{tier1: []}`); an unknown action (did-you-mean); a missing required parameter (the
parameter and its values); a step id written by an author ("remove id"); a non-empty `tier3` (P05); an unquoted `on`
(T07, in join steps `recipe_check.py`:517-518); an `!include` outside the project (T11); a formula outside the allowed list (ST06).

### What it supersedes

- **ADR-013** (`input_fields` and `output_fields`): `input_fields` is now the typed list of the columns that are read
  (DEC24); there is no `output_fields`; the published columns are the last tier-1 step, `polars_select` or `polars_drop` (DEC23).
- **ADR-014** (identity logic): an empty step list means "equal to the previous node" (spec 7.5); `wrangling: []`, a
  missing `wrangling` and a flat list are refused (S06); `input_fields: {}` means no contract, every column of the file is
  read (spec 7.3; `recipe_check.py`:529); `output_fields` is gone, so its identity rule is gone.

**ADR-090, proposed new wording** (DEC34; the plots part, points 2, 4 and 6, is unchanged). Replace decision point 1 by:

> 1. **Order rules are written in the recipe** (ADR-100). A step that can reorder rows states its order rule as a
>    required parameter, with the Polars name; the action is exactly Polars and adds no default of its own. Each rule has
>    a test on data large enough to expose a random order.
>    | Action | Required parameter | Value that gives the order of ADR-090 |
>    |---|---|---|
>    | `polars_group_by` | `maintain_order` | `true`: groups in the order they first appear |
>    | `polars_sort` | `maintain_order` | `true`: equal keys keep their input order |
>    | `polars_join` | `how`, `maintain_order` | `left_right` (`right_left` for a right join) |
>    | `polars_unique` | `keep`, `maintain_order` | `first`, `true` |
>    | `polars_sample` | `seed`, and `n` or `fraction` | a fixed seed, for example `0` |
>
>    The migration wrote these values into every shipped step, so no table changed. `summarize`, `drop_duplicates`,
>    `join_filter`, `value_counts` and `sample` with a default seed no longer exist.

Replace point 3 by: "A new action that can reorder rows exposes its order rule as a required parameter (or keeps the
Polars default, DEC33), states the rule in its description and has a test of that rule. A new random component must be
seeded." In point 5 add: "(raised to 4 by ADR-100)". In the consequences, replace "`maintain_order: false` remains
available for `drop_duplicates`" by "Any order parameter can be set otherwise in a step; the choice is visible in the recipe."

### Consequences

- **For recipe makers.** More to write: version and engine lines, a type on every field, `null_values` and `strip` on
  every schema, the order and missing-value parameters on every step, a select step at the end of tier 1. In return a
  recipe says everything it does, and an error names the place and the fix. Old recipes must be migrated by the tool.
- **For reproducibility.** No hidden default changes a result: the order of rows, the reading of missing values, the
  type of every column, the rows a filter keeps are in the file and in its hash. A Polars upgrade shows up in the
  equality and probe tests. The golden baseline proved the migration result-identical, except the changes listed and
  shown to Eve (DEMO-RECIPE-1, tasks.md:196).
- **For the app.** HOME refuses a recipe that fails the checker; Blueprint reports it. The engine no longer guesses
  (aliases, sanitiser, key protection, contract). An export made under format 0 cannot be re-run until its recipe is
  migrated (spec 4.1 consequence b).

### Documents that must follow (not edited by this draft)

Rule files (Eve's double confirmation; each still names a removed form):
- `.claude/rules/rules_data_analysis_recipe_structure.md`: sections 5 (`final_contract`), 7 (action names, `mutate`), 8, 9 (types `categorical`, `utf8`), 11.
- `.claude/rules/rules_data_engine.md`: section 2 (determinism wording, ADR-090), section 4 (ADR-013/014, `output_fields`), section 5.
- `.claude/rules/rules_agent_role_bioscientist.md`: sections 3, 6 and the action list of section 8; line 144 (join cast, DOC-JOIN-CAST-1).
- `.claude/rules/rules_test_lab.md`: section 4 (bootstrapper output: `output_fields`, `final_contract`, old action names in 4c).
- `.claude/rules/rules_gallery_standards.md` (tasks.md:167); `.claude/rules/rules_app_structure.md` and `rules_code_quality.md` (`output_fields` mentions).

Knowledge and documentation:
- `.claude/knowledge/architecture_decisions.md`: SUPERSEDED markers on ADR-013 and ADR-014; the ADR-090 wording; an "amended by" note on ADR-094 (spec 14); ADR-083 sections 2 and 6, `_meta` retired (spec 16).
- `.claude/knowledge/data_analysis_recipe_data_contract_rules.md`, `project_conventions.md`, `blueprint_architect_ux_spec.md`.
- `docs/appendix/data_analysis_recipe_structure.yaml`, `docs/appendix/Standards_yaml.qmd`, the authoring page (tasks.md:137-139) (RECIPE-DOCS-1, #79).
- The spec becomes HISTORICAL and points to these homes (spec 14).

### Not decided yet (not part of this ADR)

- R1 Order of the tier-3 change and the fate of spec-level `filters` (spec:173).
- R2 `modif_over` (spec:174); evidence section 25 says it falls (evidence:303).
- R3 Conditional parameters `rules` (spec:175); code has them (`utils/ui_schema.py`:142, `polars_sample`) but the spec row is a recommendation.
- R4 One constants module for action names (spec:176); `libs/utils/src/utils/action_names.py` exists.
- R5 Security design details (spec:177).
- R6 `na` covers null only (spec:178).
- R7 Several-step actions minimised, each recorded (spec:179); see D4.
- R8 A table reference does not stop `polars_join` being `polars_` (spec:180).
- R9 Allow-lists read from the installed Polars, pinned by a probe test (spec:181).
- R10 A column dry run in `libs/transformer` (spec:182).
- R11 Profiles `run` and `build` stay as they are (spec:183).
- Q2 `derive_categories` (spec:189); removed in code, see D6.
- Q3 Gallery dead submission code (spec:190); answered in tasks.md:200, not in the spec.
- Q4 Is `NA` a missing value in the test data (spec:191); answered in tasks.md:206, not in the spec.
- Q5 What Blueprint must change afterwards (spec:192).
- J09, J10, J11 join-key checks (spec:636-638): built (`recipe_check.py`:539-597); N5, J10 at load, awaits Eve (tasks.md:188).
- N1 one join-key rule in three places (tasks.md:185).
- Whether ADR-100 also supersedes ADR-050 (hidden join-key cast removed, Eve 2026-11-14, tasks.md:181): DOC-JOIN-CAST-1 (tasks.md:189) asks for a superseding ADR; not in the DEC table.
- ADR-099 16(g) sentence "unknown keys are warnings", superseded by DEC02 in tasks.md:123; the correction of ADR-099 is RECIPE-DOCS-1 (tasks.md:136).
