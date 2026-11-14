# Recipe format specification (format version 1)

**Written for:** Eve, to review. Once confirmed it is the base of the checker, the tests, the rule file and the user documentation.
**Status:** DRAFT, cleaned on 2026-11-13 (task SPEC-CLEAN-1). Nothing is built from it yet except the registry fixes of issue #87 and the strict import. It holds what is decided and why. The discussion that led here is in git (the last commit before the clean-up is `a392b549`), in the issues (#73 and its children), in `.claude/design/outdated/` (the earlier drafts) and in `.claude/design/home_evidence/actions_and_polars_2026-11-13.md` (the evidence, cited here by section number).
**Tags.** **DECIDED**: Eve decided it (date), or an ADR does. **RECOMMENDED**: the two sessions agree, Eve has not answered. **OPEN**: a question, with its recommendation if there is one. **CODE**: a fact read or run in the code (file:line). A tag in brackets after a heading applies to the whole section.
**Old labels.** The labels `O1` to `O33` and `N1` to `N14` of the earlier drafts are kept in the column *Ref*, because issues, tasks and the evidence file use them; a bare number there is a row of the earlier decisions table. Decisions are `DEC01` to `DEC49`, recommendations `R1` to `R11`, open questions `Q2` to `Q5` (`Q1` was answered, DEC49); the registry gaps of section 8 are `RG1` to `RG6`; the gallery design points are `D1` to `D7`.
**Terms.** *Recipe* = a data analysis recipe, a YAML file. *Schema* = a data schema (one input table). *Collection* = a join, or a schema that is plotted directly. *Tier 1/2/3* = the steps that build, reshape and finally audit a table.
**RULE** (Eve, 2026-11-13): the recipe describes the science (data science); it must be correctly designed and correctly applied. What the recipe specifies must be done. Libraries that depend on it must be science compliant.

## 1. How it works, on one page

- **One format, one checker, one place for the rules.** Every recipe (pipelines, templates, retest scenarios, transformer test recipes, gallery examples, recipes written by the app) is a YAML file in format version 1, checked by the same function, `check_recipe`, in `libs/utils`. HOME's load gate, Blueprint's Validate, the importer, the scripts and the tests all call it through one adapter (section 14).
- **Unknown keys fail. Nothing old is tolerated.** A key that nothing executes or displays does not exist. An old name is refused at once and the message names the new one. A recipe in another format version is refused and the message names the migration tool.
- **A wrong form is refused with the correction.** The message says where, what is wrong, and shows the corrected text.
- **The form of a container follows what depends on it** (section 5): named things are dictionaries, ordered operations are lists, and the two named things whose order is meaning (`analysis_groups`, `plots`) are ordered dictionaries with safeguards.
- **Every choice is written in the recipe.** An action has no hidden default: a parameter that changes the result is required, or its default is the Polars default. The type of every column, how missing values are read, how a filter treats them, how a sort or a join orders rows: all are in the recipe (section 7.5.1).
- **The names of the actions say what they are.** `polars_<name>` is a Polars call, tested against the direct call; `modif_<name>` is a Polars idea with a documented change; `step_<name>` is several calls.
- **Operations come from the registries.** A step is a registered action with the parameters its schema declares; a layer is a registered plot component with the arguments its schema or the wrapped plotnine function declares (section 8).
- **A gallery example is a standard recipe** with a required `taxonomy`, checked in a `gallery` profile (section 9).
- **Writing a description is a rule**, not a habit (section 13). Data-science errors are fixed, not documented (section 18).

The example shows the form. The action names and parameters are illustrative; the registry fixes them (section 7.5.1).

```yaml
id: my_recipe                          # equals the file name
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: My recipe
  description: >-
    What the recipe answers, for which population, from which data.
entity: {noun: sample, plural: samples, population: Anchor}      # optional
data_schemas:
  Anchor:
    label: Anchor table
    description: >-
      One row per sample (42 rows) ...
    source: {type: local_tsv, path: assets/test_data/anchor.tsv}   # development path (7.3)
    null_values: ["", "NA"]            # required: which texts mean a missing value (7.3)
    strip: true                        # required: strip whitespace before reading
    input_fields:
      sample_id: {type: String, is_entity_key: true}
      reads: {type: Int64}
    wrangling:
      tier1:
        - {action: modif_filter, column: reads, op: ge, value: 1000, na: remove, comment: too few reads to trust}
      tier2: []
  Quality:
    label: Quality table
    description: >-
      One row per sample (42 rows) ...
    source: {type: local_tsv, path: assets/test_data/quality.tsv}
    null_values: []
    strip: true
    input_fields: {sample_id: {type: String, is_entity_key: true}}
    wrangling: {tier1: []}
joins:
  Combined:
    label: Combined table
    ingredients: [{dataset_id: Anchor}, {dataset_id: Quality}]
    steps:
      tier1:
        - {action: polars_join, right_ingredient: Quality, 'on': sample_id, how: left, maintain_order: left_right}
        - {action: polars_select, exprs: [sample_id, reads]}   # the published columns, in this order
    labels: {reads: Number of reads}   # display names of columns, shown in the audit dialog and as plot titles
analysis_groups:
  overview:
    label: Overview
    plots:
      reads_per_sample:
        label: Reads per sample
        description: Number of reads of each sample.
        spec: {target_dataset: Combined, mapping: {x: sample_id, y: reads}, layers: [{name: geom_col}]}
        steps: {tier3: []}                               # steps applied to this plot's table
```

## 2. What is decided, what is recommended, what is open

### 2.1 Decided

Each line: the decision, why in a few words, who and when. *Ref* is the label of the earlier drafts.

**Scope, principles, checker**

| # | Decision | Why | Eve | Ref |
|---|---|---|---|---|
| DEC01 | **Scope:** every recipe, in the app and in the tests (transformer fixtures and recipes inside automatic tests included): everything that describes a read of data or a plot | one format everywhere | 2026-11-13 | 1 |
| DEC02 | **Unknown keys fail; no backward-compatible default.** The old-key table (`legacy_keys.py`) only names the replacement in the message; old names are refused at once | recipes are checked first (Blueprint), so nothing needs tolerating; a tolerated error hides a wrong result | 2026-11-13; ADR-099 16(a) | 2, 3 |
| DEC03 | **One checker `check_recipe` in `libs/utils`** for every user of recipes (HOME, Blueprint, importer, gallery, scripts, tests) | one rule set; the layer rules allow it (section 14) | ADR-099 16(g) | 12 |
| DEC04 | **`spec_version`**, an integer, is required in every recipe and in every recipe a tool writes (4.1) | the checker refuses another format and names the migration tool | 2026-11-13 | 11, 22 |
| DEC05 | **`data_engine` (`python-polars`) and `plot_engine` (`python-plotnine`) are required** | the engines are part of what a recipe means | 2026-11-13 | 7 |
| DEC06 | **`description` on every element**; where missing it is an advice with the rules of section 13; `label` is the short name | the reader who must choose where to filter did not build the recipe | 2026-11-13 | 8 |
| DEC07 | **Comments are possible and specified** (6.2): `#` comments are free and kept by every tool; a `comment` key on `info`, a schema, a join, a group, a plot, a step and a layer; the plural `comments` is refused | the why of a choice must survive; one spelling | 2026-11-13 | 9, 27 |
| DEC08 | **Containers follow ADR-041** and the form follows what depends on it (section 5); a wrong form is refused with a message that shows the corrected text | one rule, and the fix is in the message | ADR-041; 2026-11-13 | 13, 14 |
| DEC09 | **The registries are fixed** (widgets for lists and dictionaries, corrected declarations) and **plot arguments are checked** | plot instructions are part of the recipe (issue #87) | 2026-11-13 | 16 |
| DEC10 | **Errors of a recipe from a data-science point of view are fixed**, not documented (section 18) | the RULE | 2026-11-11/12 | 17 |
| DEC11 | The worked example is `1_test_data_ST22_dummy` | the most advanced, the default of Eve's tests | 2026-11-13 | 18 |
| DEC12 | **The two legacy recipes are removed**: `config/data_analysis_recipes/VIGAS-P/` and `assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_data_analysis_recipe.yaml`. `Virulence_genes_APEC_input_fields.yaml` is not legacy (the Abromics pipeline includes it) | no code reads them | 2026-11-13 | 24 |

**Elements of the recipe**

| # | Decision | Why | Eve | Ref |
|---|---|---|---|---|
| DEC13 | `is_primary_key` becomes `is_entity_key` | a generic word: the format knows no field-specific term | 2026-11-13 | 4 |
| DEC14 | **The column-name aliases are removed** (`column`, `source`, `source_column`, `target_column` for `columns`, and the other spellings of section 12) | aliases are legacy terms; choose once and apply in the libraries too | 2026-11-13 | 25 |
| DEC15 | **One name per role for the parameters of `modif_` and `step_` actions and for the audit** (H1): input columns are `columns` (a list), outputs `new_column` or `new_columns`, one `separator`. In a `polars_` action the Polars parameter names win (DEC32) | one vocabulary the audit and the forms can rely on | 2026-11-13 | 21, 14 |
| DEC16 | **A schema plotted directly applies its own tier-2 list** (engine fix, issue #77); on a schema that is only an ingredient `tier2` is an error | a list that is never applied is a silent wrong result | 2026-11-12 | 6 |
| DEC17 | **The tier-3 container is in the recipe:** `steps: {tier3: [...]}` on the plot entry, any registered action, the audit writes filters and drops. The engine must read it, because it is the data of the plot. Until it does, the checker refuses a non-empty list (P05). The order of the change is open (R1) | the plot must equal its table; HOME rule 19 "fail instead of warn" | 2026-11-13 | 5, 9 |
| DEC18 | **Profiles `run`, `build`, `gallery`, `audit`**; the audit marker `id: audit_<8 hex>_<k>` (an `id` on a step is an error in `run` and `build`); tier-3 steps are data steps (filters, dropped columns) on the plot entry's table | `run` and `build` differ only in what an empty placeholder may be | 2026-11-13 | 30, 17 |
| DEC19 | **J08 is an error with a guidance message:** a non-key column present in both tables of a join (silently renamed `name_right` by Polars) refuses the recipe; the message names both tables and the column and says how to rename or drop one | a silent rename gives a wrong column | 2026-11-13 | 23 |
| DEC20 | **The schema-level `info` block, `category` and `sub_category` are dropped**; the recipe-level `info` stays free-form (project, contact, any key) and is shown by HOME | nothing displays them | 2026-11-13 | 28 |
| DEC21 | **Plot-spec metadata:** the gallery classification is the `taxonomy` key on the plot entry (gallery), not part of a pipeline plot spec; `description` is on the plot entry; a note goes in `comment` | "do not confound" gallery and pipeline | 2026-11-13 | 26 |
| DEC22 | **Plot axis and legend titles default to the field `label`**, falling back to the column name (an explicit `labs` layer or override wins). HOME table headers keep the column name; the audit dialog shows "Label (name)". Built under #91 | readable plots without extra work | 2026-11-13 | 29 |
| DEC23 | **`final_contract` and the schema `output_fields` are removed.** The published columns of a collection are the last step of its tier 1, a plain `polars_select` (or `polars_drop`), so every column change is a visible step and the column order is the order of the list. Display names of computed columns go in a `labels: {column: text}` mapping on the collection (display only, in no data key; the dialog resolves a label as the collection's `labels`, then the input field's `label`, then nothing). ADR-013/014 are superseded | "not transparent"; one mechanism; the hashes of the tables do not change; closes #86 by removal | 2026-11-13 | 27, 7, 19 |
| DEC24 | **Strict import:** only the `input_fields` that are written are read; a declared column missing from the file fails; `original_name` matches exactly; the import reports "N file columns are not declared and were not imported". Built (commit `9bfdaf4c`) | `input_fields` becomes the typed list of what the app reads | 2026-11-13 | 22 |
| DEC25 | **`original_name`** stays on input fields (the exact header in the file); it has no meaning elsewhere | the ingestor renames to the slug, recipes use plain names | 2026-11-13 | 16 |
| DEC26 | **The id-first rule is a recommendation to the recipe maker**, done by steps in the recipe. Nothing in code enforces or verifies it; the recipe must work without assuming the id is the first column. Ingestion imposes no declared column order; a recipe that needs an order writes a step. The audit's own refusal to drop a key (UI contract 12g.3) is a rule of the audit and stays | no hidden rule inside an action | 2026-11-13 | 32 |

**Types, missing values, paths**

| # | Decision | Why | Eve | Ref |
|---|---|---|---|---|
| DEC27 | **`type` is required on every field and is any Polars dtype a text file can hold** (7.4). The declared dtype goes to the CSV reader; the reader fails strictly and names the value. `categorical` is refused with the message "this was String"; `Categorical` stays a type for those who want it; the levels of an `Enum` are the key `categories` (Polars name); the unused `@category` column selection is removed | one vocabulary (Polars); `categorical` was a tweak (String at ingestion, Categorical in the validator); a later cast from text does not work for `Boolean`, `Datetime`, `Time`, `Decimal` | 2026-11-13 | 24 |
| DEC28 | **Missing values have no default.** `null_values` (a list of texts, `[]` allowed) and `strip` (true or false) are always stated in the recipe. Ingestion reads text, applies them, then casts. The documentation warns recipe makers (null, NaN, the text `NA`; Polars has null and NaN, no NA). Placement: one setting per data schema, with an optional override per field, to limit friction (Eve, 2026-11-13). | the right answer depends on the data; today's hidden sanitiser turns `NA` (Namibia) into a missing value | 2026-11-13 | new |
| DEC29 | **A filter always states its missing-value rule:** `na` is a parameter of `modif_filter` and is required, because it follows from DEC33 (no hidden choice); Eve accepted `modif_filter` with `na` | a default silently changes which rows a figure counts | 2026-11-13 | 25 |
| DEC30 | **Paths: no engine change.** The deployment's `data_lookup` already has `data_analysis_recipe_paths` (the `source.path` of the recipe, the development fallback) and `by_dataset_id` (production: the file is found by dataset name in `raw_data`; the recipe's path is ignored). The path-shape rule (no absolute path, no `..`, no `~`, no URL) applies to a development path only. Optional later: move development paths out of the recipes | how data reaches a deployment is the deployment's business | 2026-11-13 | 31 |

**Names and actions** (7.5.1)

| # | Decision | Why | Eve | Ref |
|---|---|---|---|---|
| DEC31 | **Prefixes:** `polars_<name>` for a Polars call, `modif_<name>` for a Polars idea with a documented change, `step_<name>` for several calls; no unprefixed action name remains. A registry field `polars: exact / wrapper / modified / composite` plus `wraps` says the same in data and Blueprint shows it | "an action that is not Polars must be seen by its name" | 2026-11-13 | 7, 12 |
| DEC32 | **A `polars_` action behaves exactly as Polars:** the Polars name, all Polars parameters with the Polars names and defaults; a test compares it with the direct Polars call. A special need is a separate `modif_` action, or better, is written in the recipe | we must KNOW that it works | 2026-11-13 | 1, 9, 14 |
| DEC33 | **No hidden choice anywhere:** a parameter that changes the result is required, or its default is the Polars default; for `modif_` and `step_` a default is allowed only when the parameter is "off when absent" | transparency; the registry test makes it executable | 2026-11-13 | 13 |
| DEC34 | **Determinism is a required parameter, not an action default** (`maintain_order`, `keep`, `seed`, `n` or `fraction`, `how`): the recipe states the order rule, the action is exactly Polars. ADR-090 gets a wording change | the deliberate defaults were bad choices | 2026-11-13 | 10, 30 |
| DEC35 | **One name per action:** no alias, no second action for one Polars method (`unique` absorbs `drop_duplicates` and `unique_rows`; `rename` absorbs `rename_columns`; `join` absorbs `join_filter`); a Polars name that meant something else here is renamed | one way to say one thing | 2026-11-13 | 2, 3, 5, 6 |
| DEC36 | **Actions that do several Polars calls may stay** when simple, unambiguous, documented and every behaviour switch is an option; they are `step_`. No action returns the frame unchanged on a missing parameter or column: it fails and names the step | clear and no silent no-op | 2026-11-13 | 4 |
| DEC37 | **`polars_select` and `polars_drop` replace `keep_columns` and `drop_columns`:** plain and strict, column names only (a computed column is a `polars_with_columns` step first); no key protection, a missing column fails | the old ones added hidden rules (keys first, missing column ignored) | 2026-11-13 | 26 |
| DEC38 | **`polars_with_columns` takes a mapping `column: formula`; `mutate` and `add_constant` are removed** (`add_constant` is `pl.lit(...)`). All formulas of one step see the table as it was before the step, as in Polars | the Polars form; fewer special actions | 2026-11-13 | 11 |
| DEC39 | **`modif_filter`** (`column`, `op`, `value`, `na`) replaces the five `filter_*` actions and `is_in`, `not_in` (which filter rows, unlike Polars): one vocabulary with the audit rows and VizFactory `filters`. Its behaviour is verified first (task MODIF-FILTER-VERIFY-1). `polars_filter` (a formula predicate) can exist beside it and waits until a recipe needs it | the audit writes `modif_filter` now | 2026-11-13 | 11 |
| DEC40 | **`percentile` is removed** (it was rank divided by the row count; 0 shipped steps). `polars_rank` and `polars_quantile` come with the deferred gaps | the name was misleading | 2026-11-13 | new |
| DEC41 | **Polars methods without an action are deferred** (evidence section 19), unless they replace an existing action; `polars_fill_nan` and `polars_drop_nans` are added because NaN needs its own handling in the recipe | the app keeps working; adding one needs its equality test | 2026-11-13 | new |
| DEC42 | **`scan_parquet` and `sink_parquet` are engine functions, not recipe actions** | the engine calls them with cache paths; a recipe writing to any path is a security risk | 2026-11-13 | 11 |

**Process**

| # | Decision | Why | Eve | Ref |
|---|---|---|---|---|
| DEC43 | **Migration: one tool, two runs.** Run A: names and types, text level, result-identical (every default written into the steps, so no table changes). Run B: `final_contract`, `keep_columns`, `drop_columns` to `polars_select` and `polars_drop`, plus `labels`. A golden baseline (the content hash of every collection and plot data of every shipped recipe) is taken first; every difference is listed and shown to Eve. One `ENGINE_CACHE_VERSION` bump at the release | a mistake must be found in the run that made it; no silent change | 2026-11-13 | 28 |
| DEC44 | **Security:** a bad recipe must not be able to run code or read or write where it should not (section 15) | Eve asked for a verified security check | 2026-11-13 | 10, 29 |
| DEC45 | **ADR-100 "Recipe format version 1"** supersedes ADR-013/014, changes ADR-090's wording and records the format decisions; drafted after the names and the order of work are settled | the ADR log is in force | 2026-11-13 | 23 |
| DEC46 | **Notes, not decisions:** some library code may move to `libs/utils` when two libraries need it (`UTILS-REUSE-REVIEW-1`, nothing moved); the Dockerfile is not ready and nothing is deployed (`DOCKER-RELEASE-1`) | | 2026-11-13 | 19 |

**A cast never loses information silently** (DEC49, Eve 2026-11-13): `polars_cast` keeps its name and is exactly Polars except that a float to integer cast that would drop decimals FAILS and names the value (a silent truncation of `2022.5` to `2022` is a result changed silently); there is no `modif_cast`. Truncation is written in the recipe as its own step (`polars_round` with `decimals: 0`, then the cast). Implemented and tested by the HOME session.

**The gallery** (section 9): **DEC47** examples are standard recipes in a `gallery` profile, `taxonomy` on the plot entry (required in the gallery, five axes, `geom` derived), the specification is also a data file so the gallery terms live in one place (D1 to D3; 2026-11-13, Ref 21). **DEC48** D4 to D7 as recommended: the checker runs at index rebuild, at app start and in the tests; previews come by the app's path; the tag strip of `example_meta.md` is generated from `taxonomy`; the data contract of an example is generated and reviewed (2026-11-13, Ref O1).

### 2.2 Principles (each follows from a decision above)

- **P1 Executed, displayed, or refused.** Every key either is executed by an engine, is displayed, or is refused with the reason.
- **P2 No compatibility defaults.** A wrong recipe is corrected, never tolerated (DEC02).
- **P3 One word for one thing.** `label` is the short name shown to the user; `description` is one or two sentences; steps and tiers are written the same way everywhere.
- **P4 Generic words.** The format and the checker know no field-specific word (entity, attribute, table; not sample, gene). Field words live in recipes and help.
- **P5 An error says where, what and the fix**, and shows the corrected text: `recipe : path : what is wrong. Fix: what to write.`
- **P6 Looking for a problem is separate from running.** The checker reads the recipe and the registries and never needs the data; the data check stays separate.
- **P7 A choice is written, not assumed.** Nothing the recipe does depends on a default that the reader cannot see (DEC33).

### 2.3 Recommended, awaiting Eve

| # | Recommendation | Why | Ref |
|---|---|---|---|
| R1 | **Order of the tier-3 change.** Keep spec-level `filters` allowed until the engine reads `steps.tier3`; then a migration rewrites every filter row into a step of `steps.tier3` and the checker refuses `filters` (P06). Before the migration, measure whether VizFactory's `filters` and the filter actions treat missing values alike (task MISSING-VIZ-FILTERS-1); list every table or figure that would change. Meanwhile HOME merges the author's filters with the exploration filters instead of overwriting them (`home_theater.py:498`) only if the reader is more than one package away | a figure must equal its table; nothing changes silently | 9 |
| R2 | **`modif_over`** merges `count_by_group` and `window_agg` (both `Expr.over`) | one action per Polars method; Eve has not yet decided the merges | N11 |
| R3 | **Conditional parameters:** `ui_schema` gets a `rules` list (`when`, `require`, `one_of`, `exclusive`) read by `step_problems` and the engine, so the shape of `value` can depend on `op` and `fill_null` can take `value` or `strategy`; the Blueprint form follows it | `modif_filter` needs it | N11 |
| R4 | **One constants module for action names in `libs/utils`** (Tier 1, so `test_lab` and `id_reconciliation` can read it), the consumers read names from it; a test fails when a registered action name appears as a string elsewhere (exempt: the registry, tests, `legacy_keys.py`, the migration tool) and when a constant has no registered action. Six places spell names today (audit translator, `data_wrangler.py`, `data_assembler.py`, Blueprint, Test Lab bootstrapper, ID reconciliation) | a rename must not leave a stale string | O33 |
| R5 | **Security design** (section 15): formula check by `ast` with an allow-list of `pl.<function>` read from the installed Polars; a separate grammar for `stat_function`; path-shape and containment checks; confinement of `!include` in the loader | Eve wants it verified | O29 |
| R6 | **`na` covers null only.** A NaN is a number larger than every number and is dropped by nothing; it is handled by `polars_fill_nan` and `polars_drop_nans` and named in the documentation | null and NaN are different things in Polars | O25 |
| R7 | **Several-step actions stay minimised, each is `step_` and each is recorded** (Eve 2026-11-13): each `step_` action is examined one by one (evidence sections 3, 10, 15); where single steps give the same table the action goes (`split_and_explode` is `str_split` plus `explode`), proved by a golden test; the others are read and documented | transparency without losing tools | 7.5.1 |
| R8 | **A reference to a table by id** (`join`'s `right_ingredient`) is not a behavioural difference, so `polars_join` is still `polars_` | else `polars_join` is impossible | N12 |
| R9 | **The checker's allow-lists are read from the installed Polars** (dtypes, formula functions) and pinned by a probe test, so a Polars upgrade shows what changed | no hand-kept list | 24, O29 |
| R10 | **A column dry run** (`columns_at_each_node`, the real actions on empty frames built from the declared types) in `libs/transformer`, injected into the checker, is a possible LATER tool for "a step names a column the node does not have" (X7, J08). Measured: 34 of 35 shipped nodes have the same columns, one the same set in another order. Not needed for the id rule, not decided, not built | exact, no second copy of what an action does to columns | O32 |
| R11 | **Profiles `run` and `build` stay as they are** | they differ only in what an empty placeholder may be | O17 |

### 2.4 Open

| # | Question | Recommendation | Ref |
|---|---|---|---|
| Q2 | **`derive_categories`** reads an external file and maps rows with a Python function; it is not Polars. What it does may be a `join` with a lookup table | read it, then decide (R7) | N4 |
| Q3 | **Gallery G6:** the dead submission code (`submission_modal_ui`, `autofill_meta_from_audit`, `btn_confirm_submission`): remove or keep on purpose | decided 2026-11-14: the dead code removed, `submit_example` kept (`tasks.md:200`) | O1 |
| Q4 | **Whether `NA` is a missing value or a value in the shipped test data.** Measured (evidence section 23, an upper bound): 2856 of 176162 cells in 33 test files match one of the 14 texts (`NA` 2630, `-` 156, empty 43, `None` 21, `N/A` 6), almost all `NA` in one column, `metadata_isolation_method` of the VirulenceFinder files. Only the data owner knows | ask the data owner; the baseline shows the effect once `null_values` is explicit | 24 |
| Q5 | **Blueprint** is not touched now; what it must change afterwards is a register (evidence section 5) that becomes tasks when each recipe change lands | last in the order of work | |

## 3. Profiles, and what counts as a recipe

There is one format. A recipe is checked in a **profile**; profiles differ only in what an empty placeholder may be (R11):

| Profile | Used by | Rule |
|---|---|---|
| `run` | HOME's load gate; any program that draws plots | `analysis_groups` holds at least one group with at least one plot |
| `build` | Blueprint (building step by step); recipes that only build data (transformer tests, scripts) | `analysis_groups: {}`, `tier2: []`, `tier3: []` are accepted placeholders |
| `gallery` | gallery examples | the rules of section 9 on top of `run` |
| `audit` | the audit copy of a recipe | like `run`; steps with an `id` of the form `audit_<8 hex>_<k>` are accepted |

HOME rejects, Blueprint reports and never blocks building.

| Kind | Files | Profile | Notes |
|---|---|---|---|
| Pipeline recipes, templates, retest scenarios | 7 + 5 + 4 | `run` | the retest scenarios that are faulty on purpose keep their one fault and must be otherwise valid |
| Viz-factory test recipes | 194 in `libs/viz_factory/tests/test_data` (one per plot component, the 1:1:1 evidence loop of `rules_viz_factory.md` 3) and 1 in `libs/viz_gallery/tests/data` | `run` | today in the plot engine's compact shape (`plots:` and `data_path:` at the top; 193 of 194): each becomes a standard recipe like a gallery example; one conversion tool serves them and the gallery bundles (#89) |
| Transformer test recipes | 68 in `libs/transformer/tests/data` | `build` | the flat form (`wrangling:` and `input_fields:` at the top) is refused: each becomes one schema with its `source` path. The runners already prefer a command-line data path to the recipe's (`rules_asset_scripts.md` 4) |
| Gallery bundles | 34 | `gallery` | section 9 |
| Recipes written by the app | Blueprint's new-recipe form, test-lab bootstrapper and scaffolder, `create_data_analysis_recipe.py`, the export's forked recipe, the importer | their use | the checker runs on what they write; a test per writer; every writer emits `spec_version` |
| Recipes inside automatic tests | inline YAML strings in tests and fixtures | their purpose | one shared helper (`utils.recipe_factory`) writes a minimal valid recipe, so no test types the boilerplate |

## 4. File level

| Key | Required | Value | Executed or shown by |
|---|---|---|---|
| `id` | yes | text equal to the file name without `.yaml` | selector, caches, sessions, export |
| `spec_version` | yes | an integer, `1` (4.1) | the checker; exports record it |
| `data_engine` | yes | `python-polars` (the only value built) | checker now; fingerprint and export later |
| `plot_engine` | yes | `python-plotnine` (the only value built) | same |
| `info` | yes | mapping (7.1) | Info panel, title banner, load-gate contact |
| `entity` | no | mapping (7.2) | checker; counts, attrition and caption in audit mode |
| `data_schemas` | yes | mapping `schema id -> schema` (7.3), at least one | ingestion |
| `additional_datasets_schemas` | no | same shape, same id space | ingestion |
| `metadata_schema` | no | one schema; its id is the reserved word `metadata_schema` | ingestion, upload validation |
| `joins` | no | mapping `join id -> join` (7.6) | assembler |
| `analysis_groups` | yes | mapping `group id -> group` (7.7) | HOME tabs |
| `plot_defaults` | no | mapping (7.8) | plot engine |

Refused at the top level, with the replacement named (section 12): `plots`, `wrangling`, `input_fields`, `output_fields`, `final_contract`, `name`, `pipeline_id`, `description`, `metadata`, `type`, `join_manifests`, and any other unknown key (with a did-you-mean by spelling).

### 4.1 The format version

Every recipe declares `spec_version: 1`, the version of this specification it is written in. The first confirmed specification is format 1; the unversioned recipes of today are **format 0**. The key is not `info.version`, which stays the author's own version of the recipe's content.

The app reads **one** version. Any change of *structure* changes the number: a key added, removed or renamed, a change of required-ness or meaning, a change of a closed vocabulary (the engine names). A new term in an *open* vocabulary (the gallery terms) does not: it ships with an app release, and an app that does not know the term refuses the recipe with "unknown term". With "unknown keys fail" a new optional key also breaks an older checker, so there is no "compatible minor version", and one integer is enough.

| Check | Sev | Trigger | The message says |
|---|---|---|---|
| V01 | E | missing | this recipe is in the old format 0; run the migration tool |
| V02 | E | lower than the app reads | written for format N, the app reads M; migrate |
| V03 | E | higher | written for a newer format; update the app |
| V04 | E | not an integer (`"1"`, `1.0`, `true`) | write `spec_version: 1` |

**Migration tool:** `assets/scripts/migrate_recipe_format.py`, on the pattern of `migrate_config_vocabulary.py`: a dry run by default, `--apply` to write, safe to run twice. It edits the text, so every `#` comment is kept. **Two runs (DEC43).** *Run A* (names and types, result-identical): the replacement table of section 12, the action names, `categorical` to `String` and the other types, `spec_version` and the engine lines, unwrapped fragments, a `label` from the id; it writes into every step the default that the old action applied silently (`na: remove`, `maintain_order`, `keep`, `how`, a `seed`, the sanitiser's 14 texts as `null_values` and `strip: true`), so no table changes. *Run B* (structure): `final_contract`, `keep_columns` and `drop_columns` to `polars_select` and `polars_drop` (the keys that `keep_columns` put first are written into the list by its fixed rule, `list(dict.fromkeys(keys + columns))`, `core.py:343-352`; a key named in a `drop_columns` list is removed from the list, the action ignored it), and `labels`. It does **not** invent what is not mechanical: descriptions stay empty (an advice), `entity` is not added, science is not touched; it prints what a person must still do. The old-to-new action table is data of this tool (it also feeds `legacy_keys.py`), derived from evidence sections 15, 17 and 21.

**Where the number is recorded:** every recipe written by the app, the forked recipe of an export, `effective_run.yaml`; the importer's recipe leg says when the version differs.

**Consequences to accept.** (a) One more required key in every recipe (16 + 68 + 34 files, all writers, many tests); the tool does the mechanical part. (b) An export made under format 0 cannot be re-run until its recipe is migrated; the migrated recipe has another hash, so the importer reports a difference; the bundle still holds the original file. (c) A number can be wrong: the checker still reads the keys, so it shows as an unknown or missing key.

## 5. The form of every container (ADR-041)

**What exists.** ADR-041 (ENFORCED 2026-04-20): keyed definitions are a dictionary (field definitions are `slug: {props}`, slugs unique), ordered logic is a list (`tier1`, `tier2`), fragments are flat (the value only, no repeated anchoring key).

**The rule: the form follows what depends on it** `[DECIDED, DEC08]`:

| Category | Form | What depends on it | Containers |
|---|---|---|---|
| 1. Named; the order means nothing for the data | **dictionary** | lookup by name; names are unique | `data_schemas`, `additional_datasets_schemas`, `joins`, `input_fields`, `source`, `mapping`, `plot_defaults`, `info`, `entity`, `taxonomy`, `spec`, `labels` |
| 2. Ordered; the items need no name | **list** | the order of operations, drawing or joining; YAML guarantees the order of a list | step lists (`tier1`, `tier2`, `tier3`), `ingredients` (the first is the base), `layers`, a `multi` column-selector parameter, `null_values` |
| 3. Named, and the order is meaning | **ordered dictionary**: the order of the keys is documented as meaningful | `analysis_groups`: the tab order; `plots` of a group: the sub-tab order | those two |

Container by container:

| Container | Form | Refused |
|---|---|---|
| category 1 containers above | dictionary | a list (also a list of names, or of one-key dictionaries) |
| `analysis_groups`, `plots` of a group | ordered dictionary | the same |
| a field entry | dictionary `{type, label, ...}` | a bare string (`sample_id: categorical`, the old shorthand; none is left in the repository) |
| `wrangling` of a schema, `steps` of a join | dictionary with `tier1` (list) and optional `tier2` (list) | a flat list, `[]` |
| `tier1`, `tier2`, `tier3` | list of step mappings (7.5) | a dictionary |
| `ingredients` | list of `{dataset_id: ...}` | a dictionary, bare ids |
| `layers` | list of `{name, params, comment}` | a dictionary |
| a column-selector parameter declared `multi` | list of names | a single value |
| an included fragment | the value itself | a wrapper key that repeats the include key |

**Category 3 needs safeguards** (verified). PyYAML keeps the order on load but sorts on dump by default; five dump sites in non-test code sort today (`exporter.py:56,86`, `wrangle_studio.py:1848,1864`, `blueprint_handlers.py:861`). The safeguards: (1) the loader keeps the file order and refuses a repeated key (T10): PyYAML silently keeps the last; (2) every writer passes `sort_keys=False`, guarded by a test that scans every `yaml.dump` and `safe_dump` of non-test code. The tab order enters no data key. (With `final_contract` removed, the column order is the order of a step list and no ordered dictionary feeds a data key.)

**What does not depend on order:** `input_fields` (the ingestor renames and casts, never selects by them), `joins`, `data_schemas`, `mapping`, `params`, `info`, `labels`.

**What the repository contains today** (scan `tmpAI/recipe_format/container_forms.py`, verified): all 307 input field entries are dictionaries; **17 containers are in list form** (7 empty `[]` written where `{}` or `{tier1: []}` belongs, 10 with content: 3 `final_contract` lists, 1 `output_fields` list, 1 flat `wrangling`, 5 flat join `steps` in fixtures); the engine skips a list-form `final_contract` silently (`orchestrator.py:59-62`), so three recipes' contracts are not applied today, and removing `final_contract` (DEC23) turns each into an explicit step whose effect on the plots is checked at migration (#78); **33 fragments carry the wrapper key** that ADR-041 prohibits (the loader removes it silently); two texts contradict ADR-041 (`rules_data_analysis_recipe_structure.md` section 8 "single `spec:` root key"; `data_analysis_recipe_data_contract_rules.md` 4.3 types), both go in the documentation sweep (#79).

### 5.1 The message carries the correction `[DECIDED, DEC08]`

Each container-form check generates the corrected text from what it found. The same adapter serves HOME's load gate, Blueprint's Validate, the import screen, the scripts and the tests, so they show the same message. Each check has a test that asserts the message **contains the corrected text**, so the suggestion cannot go stale. The migration tool applies the same corrections mechanically.

| Found | The message shows (generated) |
|---|---|
| `final_contract: ...` or `output_fields: ...` | removed: end the step list with `{action: polars_select, exprs: [sample_id, value_col]}` (the columns in this order); display names go in `labels` |
| `steps: [{action: polars_join, ...}]` (a flat list) | `steps: {tier1: [{action: polars_join, ...}]}` |
| `output_fields: []` or `wrangling: []` on a schema | `wrangling: {tier1: []}` |
| a wrapper line `input_fields:` inside the included file | remove the line and its indentation; the file holds the fields themselves |
| `sample_id: categorical` | `sample_id: {type: String}` (and `categorical` itself: "this was String") |
| a repeated key | names the key and both lines; remove or rename one |

### 5.2 Identical keys `[verified]`

A key must be unique **inside one mapping** (ADR-041). The same slug in different mappings is normal: `sample_id` is in the `input_fields` of every table and in every row of a long table. The real hazards are:

1. **A repeated key inside one mapping:** PyYAML keeps the last silently (T10). This holds at any depth, including a `mapping` parameter: `{a: x, a: y}` silently drops a rename.
2. **A column name in both tables of a join that is not a join key:** the engine calls `lf.join(...)` without a suffix (`joins.py:56-58`), so Polars renames the second column to `name_right` without a message; `QC_Reads_Anchor` has `total_reads_right` today. The join keys themselves are the key family and are fine. Check **J08** (DEC19); it needs the recipe graph. `QC_Reads_Anchor` will fail the checker until it is fixed in its migration.
3. **Steps** repeat actions (a table has three `join` steps), so ordered logic cannot be keyed by the action name; it stays a list and a step that needs a name carries an `id` (7.5).

## 6. Fragments and comments

### 6.1 Fragments (`!include`)

- `key: !include 'path/to/file.yaml'` puts the content of the file exactly where the key is. The path is relative to the folder of the recipe `[CODE, config_loader.py:55; nested includes use the same folder]` and **must stay inside the project**: no absolute path, and the resolved path lies under the project root, the nearest ancestor of the recipe with a `pyproject.toml` (else the recipe's folder); a caller may name another root (`ConfigManager(..., include_root=...)`). The shipped Abromics recipe includes a fragment of `assets/ref_data/` from `config/`, so "inside the recipe's folder" would break it; section 15, check T11.
- **The fragment holds the value itself, with no wrapper key** `[DECIDED, ADR-041 point 3]`. A file whose only top-level key repeats the key it is included under is refused with "remove the wrapper line" (F01). Today the loader removes the wrapper silently (`config_loader.py:77-97`), a compatibility default ADR-041 prohibits. The ST22 recipe has 68 includes: 56 bare, 12 wrapped; over all recipes 33 are wrapped.
- A missing file is an error naming the file (T02).

### 6.2 Comments `[DECIDED, DEC07]`

| What | Form | Rule |
|---|---|---|
| A YAML comment | `# any text`, on its own line or after a value, in a recipe or fragment | **Free, anywhere, never refused.** It is not a key: the loader drops it, the checker never sees it. **Any tool that edits a recipe or a fragment keeps every comment** (a text-level edit or a round-trip library, never `yaml.dump`); a test per writer checks it. The ST22 recipe has 150 comment lines that explain defaults and why a column is kept |
| A `comment` key | `comment: text`, optional, on `info`, a schema, a join, a group, a plot entry, **every step and every layer** | The author's note of **intent: why, not what**. Read by people, never executed, never passed to an action or to the plot engine. It is not the `description`: the description says what the element is; `comment` says why. `CODE` for steps, layers, groups, plots (BP-COMMENTS-1, ADR-082 Q4, ADR-083) |

## 7. The elements

Columns: R required, o optional, a advice (never blocks).

### 7.1 `info` (the recipe's own card)

| Key | | Meaning |
|---|---|---|
| `label` | R | the short name of the recipe (was `display_name`) |
| `description` | a | what the recipe answers, for which population, from which data (section 13) |
| `subtitle` | o | shown under the title in HOME |
| `contact` | a | who to call when the recipe fails; the load gate shows it (ADR-094) |
| `version` | o | text; the author's own version |
| `comment` | o | the author's note (6.2) |
| any other key | o | free-form, displayed in the Info panel, never executed. This is the only free-form block of the format |

### 7.2 `entity` (optional)

`noun` (R, the unit in the singular), `plural` (R), `population` (R, the id of the table with one row per unit). Checks: the id exists and that table carries an entity key (7.4). Without `entity` the software says "entities" and never guesses from column names. `[DECIDED, 5a-17]`

### 7.3 Schema (`data_schemas.<id>`, `additional_datasets_schemas.<id>`, `metadata_schema`)

| Key | | Meaning |
|---|---|---|
| `label` | R | short name |
| `description` | a | the grain (what one row is), the entities, what the recipe already removed, how missing values are treated |
| `comment` | o | the author's note |
| `source` | R | `{type, path}`; `type` is `local_tsv` or `local_parquet`; `path` is the **development path** (DEC30): used when the deployment's `data_lookup` is `data_analysis_recipe_paths`, ignored in production (`by_dataset_id`). The fuzzy search of a file by dataset name in the ingestor (`ingestor.py:80-92`) goes |
| `null_values` | R | list of texts that mean "missing" (`[]` allowed): read as text, these become null, then the dtype is applied (DEC28) |
| `strip` | R | `true` or `false`: strip whitespace of text before the null words are applied |
| `input_fields` | R | mapping `column slug -> field` (7.4); `{}` means no contract; **only the declared columns are read** (DEC24) |
| `wrangling` | R | `{tier1: [...], tier2: [...]}` (7.5); `tier1` required, `tier2` optional; `[]` and a flat list are refused |

The three sections share one id space; a repeated id is an error (today the second silently replaces the first, `orchestrator.py:151-157`). `tier2` of a schema is applied **only when the schema is plotted directly** (DEC16). The keys `fields` (alias of `input_fields`), `info:` and `output_fields` are refused.

**Missing values** (DEC28). Polars has no `NA`: it has `null` (a missing value, any type) and `NaN` (a floating point value, larger than every number in comparisons, not null); R's `NA` is Polars `null`; the text `NA` in a file is a string. Polars' own reader turns only an empty field into null. Today's hidden sanitiser strips whitespace and turns 14 exact texts into null in every text column (`""`, `NA`, `N/A`, `None`, `null`, `NaN`, `-`, `na`, `n/a`, `none`, `nan`, `NULL`, `n.a.`, `N.A.`, `sanitizer.py`; evidence section 20). That list also hits identifiers and free text (`NA` is the ISO code of Namibia), and a later `!=` or `not in` filter then drops those rows: a hidden choice with a science risk. Run A writes the 14 into each schema's `null_values`, so no table changes; the maker can then shorten the list per schema or per field. Because the reader has no per-column list, the implementation reads text, applies the declared null texts, then casts. The documentation says this plainly (task DOC-MISSING-VALUES-1, with the Namibia example).

### 7.4 Fields (`input_fields.<slug>`)

| Key | | Meaning |
|---|---|---|
| `type` | R | a Polars dtype name that a text file can hold (below) |
| `categories` | o | the levels of an `Enum`, in order (required for `Enum`; it also fixes the axis order of a plot) |
| `precision`, `scale` | o | for `Decimal` |
| `format` | o | the parse format for `Date`, `Datetime`, `Time` |
| `time_unit`, `time_zone` | o | for `Datetime` |
| `original_name` | o | the column name in the file when it differs (exact match); shown in Blueprint |
| `label` | o | display name (default: the slug) |
| `is_entity_key` | o | `true` when the column identifies the entity (it repeats in long tables) |
| `null_values`, `strip` | o | override of the schema's setting for this column |

**The type** (DEC27). The type is read from Polars, not from a list of ours: the allow-list is the set of Polars dtypes that the installed Polars can read from text with the CSV reader, produced by a probe test that tries every dtype on sample text (R9), so a Polars upgrade shows what changed. The declared dtype is given to the reader (`schema_overrides`), which fails strictly and names the value: a `String` `2022.0` into `Int64` fails ("could not parse `2022.0` as dtype `i64`"). A plain `cast` from text does **not** work for `Boolean`, `Datetime`, `Time`, `Duration`, `Decimal` (run on Polars 1.40.1), which is why the type is handed to the reader. `Enum` needs its levels, `Decimal` its precision. A `Categorical` key does not join with a `String` key: the join fails loudly (`SchemaError`, verified), never silently. A TSV column whose cells are all whole numbers is read as `Int64` by Polars on its own; the declared type makes that a choice written in the recipe. Old names (`numeric`, `utf8`, `integer`, `int`, `i64`, `float`, `string`, `character`, `categorical`) are refused with the replacement named; `categorical` always meant `String`, so its message is "this was String". Run A rewrites the shipped recipes (the tables do not change; ingestion made `categorical` a String). History that matters: four type lists disagreed (rule file, user docs, `ingestor.py:162-170`, `MetadataValidator.DTYPE_MAP`); `utf8`, `boolean` and `i64` were not cast by the ingestor; 4 fixtures declare `i64`.

### 7.5 Steps, tiers and step ids

- A **step list** is `{tier1: [...], tier2: [...]}`. It appears as `wrangling` (schema), `steps` (join) and, at the plot entry, `steps: {tier3: [...]}` (7.7). All three are written the same way; an empty list means "equal to the previous node". `tier1` is required except at the plot entry; an unknown tier name is an error. `[DECIDED, 5a-15]`
- A **step** is a mapping with `action` (a registered name), exactly the parameters in that action's `ui_schema.params`, and optionally `comment`, and `id` when the app wrote it (below); neither is a parameter and neither is passed to the action. A missing required parameter, an unknown parameter and an unknown action are errors with a did-you-mean by spelling.
- **Renames and late names need no alias** (verified by running the real orchestrator, `app/tests/test_column_names_through_the_steps.py`): steps run in order and each sees the table the previous step left; a rename in a schema's tier 1 is seen by the join's steps and by tier 2; a column that exists only after a join is seen by the next step and by tier 2. The only declarative rename is `original_name` on an input field.
- **No guessing between spellings of a parameter** (DEC14). Today the wrangler looks for "which columns does this step work on" in six spellings, expands `@category`, checks the columns exist and **writes the result back into the step as `columns`** (`data_wrangler.py:132-147`); a join's steps go through `DataAssembler`, which resolves none (`filter_gt column: score` there changes nothing). What goes is the guessing and `@category`; the presence check stays, reading **the parameters that the action's own schema declares as column selectors** (71 parameters in 59 of 65 actions). Both paths then **fail** on a missing parameter and name the right one (ST03). 14 steps in 10 recipe files rely on a wrong spelling today. One rule set for the checker and the engine: `utils.ui_schema.step_problems(action, spec, schema)`; the keys every step may carry are `action`, `id` (audit profile only) and `comment`.
- `polars_join` only in tier1 (ST05). `how` is required (DEC34).
- `'on'` is quoted. An unquoted `on:` becomes the boolean key `True`; today the loader repairs it with a printed warning (`config_loader.py:18-41`). It is an error (T07).
- Formulas (`polars_with_columns` values, plot function strings) may use only an allowed list of Polars operations (section 15).

**Step ids: written by the app, not by authors** `[DECIDED, DEC18]`. Steps stay lists. A step has no name in the author's recipe: nothing in a recipe refers to a step. The key exists for one reason: the audit mode inserts steps into the audit copy of a recipe and must be able to **mark** them, to **remove or undo exactly those**, and to open the right node popup. So a step the app inserts carries `id: audit_<unique suffix>`, and the invariant "the copy minus its marked steps equals the original" compares those ids.

```yaml
tier1:
  - action: polars_join                   # the author's step: no id
    right_ingredient: Quast
    'on': sample_id
    how: left
    maintain_order: left_right
    comment: reads quality and assembly quality side by side
  - id: audit_7f3a                        # inserted by the audit mode
    action: modif_filter
    column: Country
    op: eq
    value: Norway
    na: remove
```

Rules: (1) `id` is accepted because the audit copy contains it; it is text and unique inside its list (ST08). (2) `id` and `comment` are **not part of the hash** (a mark or a note must not rebuild a table); the order is. (3) The list is the order, so nothing depends on the order of a mapping. (4) Error messages name a step by its place ("step 3 of `tier1` of `QC_Reads_Anchor`, `polars_join`"), never by an id the author did not write. Why not the action name as the key: a table repeats actions (11 of the 74 non-empty step lists repeat one; `QC_Reads_Anchor` has three joins). A dictionary of ids was rejected: silent duplicates, sorted hashes and sorting writers become real for every step, and 148+ steps would migrate.

### 7.5.1 Action names, defaults and the registry `[DECIDED, DEC31 to DEC42; evidence: home_evidence/actions_and_polars_2026-11-13.md sections 2, 3, 10, 15, 17, 19, 21]`

Why: stay aligned with Polars so that a recipe reads like the Polars code and a reader can tell at once what is Polars and what is ours.

| Class | Name | Registry `polars` | Meaning |
|---|---|---|---|
| Polars call | `polars_<name>`, the method with its namespace written in the name (`polars_str_replace_all`, `polars_dt_truncate`, `polars_list_join`; the rule is `<namespace>_<method>`, because `str_replace_all` is not an identifier in Polars) | `exact`, `wrapper` | exactly the Polars call: all Polars parameters, Polars names and defaults. `wrapper` = applied through `with_columns` with an optional target column. The equality test (below) proves it |
| Modified | `modif_<name>` | `modified` | a Polars idea with another parameter or default, or an own vocabulary (`modif_filter`); the difference is in the description, no behaviour is hidden |
| Composite | `step_<name>` | `composite` | several Polars calls; simple, unambiguous, documented, every switch an option |

**Rules.** (1) The registry field and the prefix say the same thing; a registry test fails when they disagree (one source, one reading aid); `wraps` stays: it names the call for the equality test and the help panel. (2) **Equality test:** for each `polars_` action, call it with the Polars parameters on a probe frame and compare with the direct Polars call named by `wraps`; an action that fails cannot be `polars_`. (3) **No hidden choice (DEC33):** a registry test checks that for a `polars_` action every parameter of the wrapped call is exposed and its default equals the default in `inspect.signature` of the `wraps` target (or it is required); for `modif_` and `step_` a default is allowed only when the parameter is "off when absent"; every other behaviour parameter is required. Applied: `na` on every filter; `seed` and `n` or `fraction` on `polars_sample`; `decimals` on `polars_round`; `characters` on `polars_str_strip_chars` (null means the Polars default, whitespace: `step_problems` counts null as missing, so the parameter cannot be required; the migration writes the explicit characters, `' \t\n\r"'`, where the old `strip_whitespace` also stripped quotes); the regex of a pattern selection as the maker writes it (the anchors `^...$` are written, not added); the separator of a split; the cast of a division; the many-to-one of a value replacement as a visible choice. (4) **Parameter names:** in a `polars_` action the Polars names (`subset`, `by`, `on`, `exprs`); in `modif_` and `step_` actions and in the audit vocabulary the one name per role (DEC15); the did-you-mean knows both and the message says which name the action wants. (5) **Differences that existed only for determinism** (ADR-090: `sort` stable, `unique` keep first, `sample` seed 0 and fraction 0.1, `join` how `left` and order `left_right`) are required parameters (DEC34); run A writes today's value into every step. (6) **Old names:** `legacy_keys.py` gets one entry per old name (about 44) naming the new one; old names are refused, never mapped. (7) A reference to a table by id (`right_ingredient`) does not stop `polars_join` being `polars_` (R8). (8) A display `label` per action keeps the Blueprint list short.

**What happens to the 67 actions** (an estimate from the bodies read, evidence section 15; each exact name still needs its equality test): about 21 keep their name with parameters completed or required (`drop_nulls`, `explode`, `unnest`, `unpivot`, `pivot`, `cast`, `shift`, `cum_sum`, `cum_count`, `interpolate`, `all_horizontal`, `any_horizontal`, `join`, `sort`, `sample`, `rename`, `coalesce`, `unique`, ...) and become `polars_<name>`; about 12 are renamed to a Polars name (`fill_nulls` and `fill_nulls_direction` to `polars_fill_null`, `round_numeric` to `polars_round`, `regex_replace` to `polars_str_replace_all`, `regex_extract` to `polars_str_extract`, `split_to_list` to `polars_str_split`, `date_truncate` to `polars_dt_truncate`, `describe_stats` to `polars_describe`, `horizontal_stats` to the four `polars_*_horizontal`, `keep_columns` to `polars_select`, `drop_columns` to `polars_drop`); about 16 old names become `modif_` and merge into 9 actions (`divide_columns`, `replace_values`, `select_by_pattern`, `strip_whitespace` have a hidden choice that becomes an option; `null_if`, `value_counts`; the filters merge into `modif_filter`); 12 are `step_` (`date_extract`, `derive_categories`, `recode_values`, `sanitize_column_names`, `split_and_explode`, `split_column`, `split_column_to_parts`, `summarize`, `to_struct`, `top_n_other`, `z_score`, `label_if`); 4 duplicates are removed (`unique_rows`, `rename_columns`, `join_filter`, `drop_duplicates` into `unique`); `mutate` and `add_constant` become `polars_with_columns`; `percentile` is removed; `sink_parquet` and `scan_parquet` leave the recipe vocabulary. The Polars methods that have no action (`head`, `tail`, `slice`, `top_k`, the table aggregations, `quantile`, `rank`, `join_asof`, `rolling`, ...) are deferred (DEC41, evidence section 19); `polars_filter` waits until a recipe needs a formula predicate.

**Where the old protection goes.** `keep_columns` and `drop_columns` protected the primary keys, `keep_columns` put them first and `drop_columns` ignored a missing column. None of that is in `polars_select` and `polars_drop` (DEC26, DEC37): the audit mode offers no drop of a key (UI contract 12g.3), and a recipe that drops a join key fails at the join with the engine's own error. Run B writes the explicit `polars_select` so the table stays identical and lists every `drop_columns` that named a missing column or a key: such a step never did what it said.

**Facts that justify the rules** (evidence): `is_in` and `not_in` filter rows where Polars returns a mask; `value_counts` returns a frame where Polars returns a struct column; `coalesce` overwrote its first column; `percentile` was `rank` divided by the row count; `rename` had two forms and a duplicate; `sort`, `sample`, `join`, `unique` had defaults that differ from Polars; `strip_whitespace` also stripped double quotes; `select_by_pattern` added the anchors.

### 7.6 Join (`joins.<id>`), a collection built from schemas

| Key | | Meaning |
|---|---|---|
| `label` | R | short name |
| `description` | a | what one row is, which tables are combined and how, what is removed, what a missing value means here |
| `comment` | o | the author's note |
| `ingredients` | R | list of `{dataset_id: <schema id>}`, at least one; **the first is the base**. A bare id (`- FastP`) is refused |
| `steps` | R | `{tier1: [...]}` at least (7.5); its last step is the published columns (`polars_select` or `polars_drop`, DEC23) |
| `labels` | o | mapping `column -> display text` (DEC23); also allowed on a schema that is plotted directly |

`output_fields`, `final_contract` or `info` on a join are refused (the message names `polars_select`, `labels` and `description`). Each `right_ingredient` is one of the join's `ingredients`; `on`, or `left_on` with `right_on`, names the key (not both). The orchestrator's silent fallbacks go: an unknown collection falls back to the first join (`orchestrator.py:198-206`) and a join without ingredients uses all schemas (`orchestrator.py:224`).

### 7.7 Analysis group and plot entry

`analysis_groups.<group id>`: `label` (R, the tab text), `description` (a), `comment` (o), `plots` (R, mapping; at least one in profile `run`). The fallback "label, else description, else id" (`home_theater.py:1119`) goes: 4 of the 5 ST22 groups have the tab text in `description` today. The order of the groups is the tab order `[DECIDED]`.

`plots.<plot id>` (snake_case, unique over all recipes); the order is the sub-tab order `[DECIDED]`:

| Key | | Meaning |
|---|---|---|
| `label` | R | the plot's tab text |
| `description` | a | what it shows, what is counted, which subset it leaves out |
| `comment` | o | the author's note |
| `spec` | R | the plot specification (7.8) |
| `steps` | o | `{tier3: [...]}`: the steps applied to this plot's table after its tier 2. Any registered action; the audit mode writes only filters and drops here. Omitted or empty means the plot reads its table as it is `[DECIDED, DEC17]` |
| `taxonomy` | o | classification for the Gallery (section 9); required in profile `gallery` |

**Who reads `steps.tier3`** `[DECIDED, DEC17; order R1]`. **Reader (target):** the engine, not HOME: a T3 node of the plot in `DataOrchestrator` (called "the engine reader of the plot's T3 list" here; it has no name in the code yet, the orchestrator has only `materialize_tier1` and `materialize_tier2`; the name and place are fixed by the HOME session's package P5). Its key is `hash(tier2 key, steps)`; an empty list gives the T2 key, so nothing is stored twice (`home_audit_steps.md` point 15). The plot, the plot's T3 table, the caption counts and the export all read this one node, so the plot equals its table. **Writer:** the audit adds steps to the same list (with `id` and `reason`); the author's steps carry none. **Until the reader exists** the checker refuses a non-empty list (P05), through one constant switched in the same commit as the reader. **Spec-level `filters`** stay allowed until then; the migration is R1 (checks P05, P06).

**Gallery.** An example's own steps are the plot's `steps: {tier3: [...]}` (DEC47). Found by reading: the only bundle with a non-empty `tier3` (`beeswarm_sina`) uses `filter_rows`, an action that was never registered (invented on 2026-05-03; the intended meaning is a greater-than filter on `mic_value`), and `generate_previews.py` never applies `wrangling`, so the filter is silently ignored today and the preview shows unfiltered data. That bundle migrates after the reader exists; its preview picture then changes once and Eve is shown both pictures. Task GALLERY-RIGOR-1 adds a test and the fix.

`info:` on a plot entry (a sentence, 25 times today) is refused: the message says `description`.

### 7.8 Plot specification, layers, `plot_defaults`

`spec` keys, the set the plot engine reads (`plot_config_resolver.py:71-74`): `target_dataset` (R, a join id or a schema id), `mapping` (R), `layers` (R, at least one geom or stat), `title`, `theme`, `facet_by`, `palette`, `labels`, `guides`, `filters`. Everything else is an error, with the replacement of section 12 where one exists (`facet_scales`, `labs`, `coordinate_flip` become layers, issue #66). `description` and `info` are refused inside a spec: they are the plot entry's. The gallery taxonomy keys `family`, `pattern`, `difficulty` are refused in a spec (DEC21); 16 of the 17 ST22 specs carry three of the axes only because they were copied from gallery examples on 2026-04-10, and no code reads them from a pipeline plot.

`mapping`: keys are aesthetic names of the plot engine (`x`, `y`, `fill`, `color`, `group`, `facet_by`, ...); values are column names of the target table (the "column exists at that node" check needs the recipe graph, X7).

`layers`: list of `{name, params, comment}`; `name` is a registered component (all 191 have a schema; none of the 167 layers in the repository has an unknown name); `params` are checked against **the component's schema plus the arguments of the wrapped plotnine function** `[DECIDED, DEC09]` (section 8).

Two forms exist for the same thing (`facet_by` at the top of the spec and inside `mapping`; `filters` in the spec and the tier-3 list); both are read today and both stay allowed until R1 decides the second; a top-level `facet_by` is refused later, `mapping.facet_by` stays.

`plot_defaults` keys: `palette`, `theme`, `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`, `layers` (`plot_config_resolver.py:64-67`). `height` and `show_legend` (2 templates) are errors.

## 8. Operations and the registries `[verified 2026-11-13]`

**The mechanism.** An operation exists because a Python function carries a decorator, run when its library is imported. `@register_action("name", ui_schema={...})` (`transformer/actions/base.py:22`) fills `AVAILABLE_WRANGLING_ACTIONS` and, with a schema, `ACTION_SCHEMAS`. `@register_plot_component("name", ui_schema={...})` (`viz_factory/registry.py:21`) fills `PLOT_COMPONENTS` and `COMPONENT_SCHEMAS`. A name registered twice overwrites the first. Today: **67 actions (65 with a schema), 191 components (all with a schema)**. A schema holds `label`, `category`, `context` (where the operation may appear: t1, t2, assembly, plot), `tags`, `params`, `description`, `yaml_example`, `wraps` (the Polars or plotnine function it wraps); from this specification also the registry field `polars` (7.5.1) and the conditional `rules` (R3). `server.py` already hands both schema dictionaries to `blueprint_arch.schema_registry.register` at startup (ADR-011 injection).

**What the checker reads:** the name (ST02, PS04), the parameters declared (ST03), the required ones (ST04), `multi` (ST07), the shape of each value (ST10), `context` against the tier (ST05 is one case). The core imports neither library (section 14): each caller exports its registry as plain data (name to `{params: {name: {widget, multi, required, options}}, allowed_extra_names, context}`) and passes it in.

**What the registries did not say, and the status** (scripts `registry_survey.py`, `registry_conformance.py`, `registry_examples.py` in `tmpAI/recipe_format/`). The part that does not depend on the migration or the checker is **built** (issue #87: RG1, RG5, the self-consistency tests); the dependent parts are in #76 (ST09, ST10, AR3 against the checker) and #78 (the alias reads, RG2). Asking plotnine about every schema parameter found 13 parameters in 7 components that plotnine refuses (#88).

| # | Gap | Consequence | Fix |
|---|---|---|---|
| RG1 | **No widget for a list or a dictionary.** Eight parameters are declared `string` while their example writes a list or a dictionary (`rename.mapping`, `rename_columns.mapping`, `recode_values.rules`, `replace_values.to_replace`, `is_in.values`, `not_in.values`, `split_column.new_columns`, `split_column_to_parts.new_columns`) | Blueprint shows a text box and keeps the typed text as a string; a checker cannot test the shape | **Built (#87):** widgets `list` and `mapping` in `utils.ui_schema.WIDGETS`; the eight corrected; the Blueprint form shows one line of YAML and saves a list or a mapping (`blueprint_arch.widget_text`). ST10 stays in #76 |
| RG2 | **The code reads keys the schema does not declare:** `rename.target_column`, `split_column.source`, `.target_column`, `.separator` | a recipe using an alias passes today and a schema-based checker refuses it | removed with the recipes that use them (#78); test AR2 is a ratchet that lists them |
| RG3 | **Engine-internal keys travel inside a step:** `__right_df__` (`data_assembler.py:207`), `__metadata__` (`data_wrangler.py:196`) | a recipe could carry them and reach the function | check ST09 (#76); the `__metadata__` key goes with the key protection (DEC26) |
| RG4 | `scan_parquet` and `sink_parquet` had no schema | | they leave the recipe vocabulary (DEC42); the 4 fixtures call the engine functions directly |
| RG5 | **All 191 components have `allow_extra_params: true`** and list only part of the arguments (802 parameters): deliberate, a component does `p + geom_x(**spec)` | "unknown parameter fails" cannot rest on the schema alone | **Built (#87):** `viz_factory.arguments`: for a geom or stat exactly what plotnine accepts (verified for all 63), for another plotnine class its signature with the schema, `None` for free-form components; `argument_catalog()` is plain data for the checker |
| RG6 | The wrangler's column resolution and ST03 must read the same declaration | two readings could disagree | one reading: the parameters with widget `column_selector` |

**Which form each parameter takes** (section 5 applied inside a step): a **list** where order or repetition is meaning or a set is meant (`columns`, `values`, `new_columns`, `rules`); a **dictionary** where each entry is a name with a value (`mapping`); a **scalar** otherwise. The registry must say which.

**Self-consistency tests** (built, they run on the registries; no recipe needed): AR2 the keys a function reads equal its schema; AR3 every `yaml_example` agrees with its schema in names and value shapes; AR4 every `wraps` resolves to an importable object; AR5 every component or action named by an example is registered; AR6 no name is registered twice; a layer argument that plotnine accepts passes and one it refuses fails; every enumerated geom and stat argument is accepted by plotnine; the schema parameters that plotnine refuses are a ratchet (#88). **To add (DEC31 to DEC33):** the prefix equals the `polars` field; the equality test of every `polars_` action; the no-default test; no registered action name as a string outside the registry and the constants module (R4).

## 9. Gallery examples `[DECIDED, DEC47 and DEC48]`

**Today** (verified, `gallery_manager.py`, `gallery_viewer.py`, `generate_previews.py`): a bundle in `assets/gallery_data/<id>/` holds `data_analysis_recipe.yaml` (its own compact shape: `info` with name, date and six taxonomy values; `data_path: example_data.tsv` relative to the bundle; one plot; `wrangling` with an optional `tier3`), `example_data.tsv`, `example_meta.md`, `preview_plot.png`, `preview_thumb.png`. `gallery_index.json` is rebuilt from the bundles. The viewer filters by six axes, shows Plot / Data / YAML tabs and the guidance text. Constraints that stay: a static reference (ADR-093: no run in the app, no handoff to HOME or Blueprint), offline use, mounted only if `gallery_enabled` (ADR-071), one plot per example, the folder name as the example's id, the six filter axes and icons, the index format the viewer reads.

**What is wrong, and each will be fixed** (plan in issue #82):

| # | Finding | Fixed by |
|---|---|---|
| G1 | the taxonomy terms are copied in five places and disagree (both fallback lists contain "Numeric-Numeric", which the cheat sheet does not allow, and lack 4 of 10 patterns) | the terms in the specification (one place); the UI reads them |
| G2 | previews do not come from the app's path: the script hands the bundle's own dict to the renderer, so an example the app could not load still gets a picture | previews by the app's path (DEC48) |
| G3 | the example file is never validated as a recipe; `data_path` is read by nobody | `check_recipe` in profile `gallery` at rebuild, at app start and in the tests (DEC48) |
| G4 | `dumbbell` declares `geom_segment` and draws `geom_line` and `geom_point` | `geom` derived from the first geom layer; the example is reviewed with Eve |
| G5 | 10 of 34 previews are 800x600, 24 are 960x600 | one standard size |
| G6 | dead submission code | Q3 |
| G7 | the tag strip of each `example_meta.md` repeats the taxonomy, unchecked | generated from `taxonomy` (DEC48) |
| G8 | the taxonomy travels by copy into 16 of 17 ST22 plot specs through the `_meta` passthrough of ADR-083 | removed in the ST22 migration |
| G9 | `beeswarm_sina` has an unregistered `filter_rows` that nothing applies (7.7) | GALLERY-RIGOR-1, after the tier-3 reader |

**Proof that it works** (`tmpAI/recipe_format/gallery_poc.py`, scratch): all 34 examples written as standard recipes build and render through the app's own path (ConfigManager, DataOrchestrator, VizFactory); 22 previews are pixel-identical, 10 differ only in size, 2 differ by jitter (0.9 % and 2.6 % of the pixels).

**Design** `[DECIDED, DEC47]`:

- **D1. An example is a standard recipe** (id, `spec_version`, engines, info, one schema, one group, one plot) checked in profile `gallery`. Pros: one format, one checker, one render path; an example is runnable; it shows good practice; the 34 examples become a regression suite for the plot path. Cons: the file is longer (35 to 60 lines against 25); 34 files to rewrite (scripted, reviewed); a deployment that moves the gallery folder can browse but not run the examples.
- **D2. `taxonomy` on the plot entry**, required in the gallery profile and optional in any other recipe, five declared axes: `family`, `pattern`, `difficulty`, `show`, `sample_size`; `geom` is **derived** from the first `geom_*` or `stat_*` layer and still offered as a filter. It replaces the `_meta` passthrough of ADR-083.
- **D3. The specification is also a data file** in `libs/utils` (with `check_recipe`): for each element its allowed keys and requiredness, the vocabularies (the engine names, **the gallery terms** with label, icon, order and a line of meaning), the table of renamed keys, the format version. The checker, the filter panels, the index order, the cheat sheet, the appendix tables and the migration tool read it or are generated from it. Cross-element rules and the registries stay in code. A new term in an open vocabulary does not change `spec_version`. The Polars dtypes are read from Polars, not from this file (R9). A packaging condition is in section 14.
- **D4 to D7** `[DECIDED as recommended]`: the same `check_recipe` at index rebuild, at app start (left out of the list with the reason shown, as HOME's gate) and in the tests; previews by the app's path in a Tier-3 script under `assets/scripts/`; the teaching text of `example_meta.md` is kept and the tag strip built from `taxonomy`; a data contract generated from the file and reviewed.

**The gallery profile checks:** exactly one group and one plot (GP01); `taxonomy` present with the five axes, each term in the vocabulary (GP02, GP03); `id` equals the folder name (GP04); the companion files exist (GP05); `source.path` is the bundle's own `example_data.tsv` (a plain file in the bundle: no `/` beyond the bundle folder, no `..`; GP06); `spec_version` present like everywhere.

**An example looks like this** (`bar_simple`; `geom` is not typed; the old `data_path`, `name` and `wrangling.tier3` disappear: the path is in `source`, the name is `label`, the example's own steps are the plot's `steps: {tier3: [...]}`):

```yaml
id: bar_simple
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: Bar Simple
  description: >-
    Number of records per species, coloured by antimicrobial class: the basic bar chart.
  submission_date: '2026-04-10'
data_schemas:
  example:
    label: Example data
    description: >-
      One row per record (100 rows): a species, an antimicrobial class and a numeric value.
    source: {type: local_tsv, path: ./assets/gallery_data/bar_simple/example_data.tsv}
    null_values: []
    strip: true
    input_fields:
      id: {type: String, label: Record}
      species: {type: String, label: Species}
      amr_class: {type: String, label: Antimicrobial class}
      value: {type: Float64, label: Value}
    wrangling: {tier1: []}
analysis_groups:
  example:
    label: Example
    description: The one plot of this example.
    plots:
      bar_simple:
        label: Bar Simple
        description: Bar count of records per species, filled by antimicrobial class.
        taxonomy: {family: Ranking, pattern: "1 Numeric, 1 Categorical", difficulty: Simple, show: ranking, sample_size: any}
        spec:
          target_dataset: example
          mapping: {x: species, fill: amr_class}
          layers:
            - {name: geom_bar, params: {}}
```

**Risks:** Blueprint's save path must keep the plot entry's keys (`taxonomy`, `comment`, `steps`; verify in `group_plot_manager` before converting); the first preview regeneration changes 12 pictures in git (each is looked at); a generated data contract could change a picture if a type is guessed wrong (the proof-of-concept script is the guard); the Playwright gallery tests and four UML diagrams need an update; the schema language can grow (the guard: keys, requiredness, types, vocabularies, renames and the version only).

**Order** (scheduled later): the specification part and the `gallery` profile come with the checker; then the tests; then converting the 34 bundles; then `gallery_manager.py`, previews, viewer, the load gate, rules and records (`rules_gallery_standards.md` rewritten with Eve's double confirmation; a new ADR "Gallery examples are recipes" that amends ADR-037, 061, 063 and ADR-083's `_meta`).

## 10. Rules that span elements

| # | Rule |
|---|---|
| X1 | ids are unique across `data_schemas`, `additional_datasets_schemas` and `metadata_schema`; a join id does not repeat a schema id (a plot's `target_dataset` must name one thing) |
| X2 | `target_dataset` of a plot exists; every `dataset_id` of an ingredient exists; every `right_ingredient` is an ingredient of its join |
| X3 | `entity.population` exists and carries an entity key |
| X4 | a schema's `tier2` is applied only if the schema is a plot's target; otherwise an error |
| X5 | `id` equals the file name; plot ids are unique **across the recipes of a folder** (a project-level check, `check_recipe_set`) |
| X6 | the key family: the entity-key columns of the schemas are linked by the join keys; the first version has one family (`home_audit_steps.md` 5a-13). Not a failure if absent |
| X7 | a step or a `labels` entry that names a column the node does not have is an error (a dry run on column names). Needs the recipe graph (HOME's `utils.recipe_graph`; R10) |

## 11. The check catalogue (one row = one test)

Severity: **E** error (HOME refuses; Blueprint reports and does not block building), **A** advice (shown, never blocks). IDs are permanent; messages are generated from this table with the replacement table (section 12) and, for a wrong container form, the corrected text (5.1).

| ID | Sev | Trigger | Fix named in the message |
|---|---|---|---|
| T01 | E | file missing, not YAML (the line is named), not a mapping | |
| T02 | E | `!include` target missing | create the file or correct the path |
| T03 | E | unknown top-level key | replacement or did-you-mean |
| T04 | E | `id`, `data_engine`, `plot_engine`, `info`, `data_schemas`, `analysis_groups` missing | add it |
| T05 | E | `id` differs from the file name | |
| V01-V04 | E | `spec_version` missing, older, newer, not an integer (4.1) | the migration tool, or update the app |
| T06 | E | engine value unknown, or a plot engine in the data slot | say the built values |
| T07 | E | unquoted `on` (a `True` key) anywhere | quote it |
| T08 | E | root `plots:` | move into a group |
| T09 | E | profile `run`: no group or no plot | add one |
| T10 | E | the same key twice in one mapping, at any depth (found by the loader) | remove one |
| T11 | E | an `!include` target that is an absolute path or resolves (symlinks followed) outside the project root, found by the loader | put the fragment inside the project |
| F01 | E | fragment wrapper repeats the include key | remove the wrapper line |
| F02 | E | fragment has the wrong type (a list for a mapping) | |
| I01 | E | `info` not a mapping, or `label` missing | add `label` |
| I02 | A | `info.description` or `info.contact` missing | write it (section 13) |
| I03 | E | `info.display_name` | `label` |
| E01 | E | unknown key in `entity`; `noun`/`plural`/`population` missing | |
| E02 | E | `population` unknown, or its table has no entity key | |
| S01 | E | unknown key in a schema (`info`, `fields`, `id`, `output_fields`, ...) | replacement |
| S02 | E | repeated schema id; use of the reserved id | |
| S03 | E | schema without `label` | add it |
| S04 | A | schema without `description` | write it |
| S05 | E | `source` missing, type not `local_tsv`/`local_parquet`, `path` missing | |
| S06 | E | `wrangling` is a flat list, `[]`, or has no `tier1`; unknown tier key | `{tier1: []}` |
| S07 | E | `tier2` on a schema that is only an ingredient | move it to a join, or plot the schema |
| S08 | E | `input_fields` not a mapping | |
| S09 | E | `null_values` missing or not a list of texts, or `strip` missing or not a boolean (also as a field override) | the two keys and their forms; the documentation on missing values |
| FD01 | E | unknown field property | replacement |
| FD02 | E | `type` missing, or not a Polars dtype that a text file can hold; an old name (`numeric`, `utf8`, `integer`, `string`, ...) | the allowed dtypes; `categorical`: "this was String" |
| FD03 | E | `is_primary_key` | `is_entity_key` |
| FD04 | E | `source_name` | `original_name` |
| FD05 | E | `is_entity_key` not true/false; `categories` missing for `Enum` or not a list of text; `precision`, `scale`, `format`, `time_unit`, `time_zone` on a type that does not use them | |
| FD06 | E | a field entry is a bare string | `{type: String}` |
| ST01 | E | step without `action` (shorthand), or not a mapping | |
| ST02 | E | unknown action; an old action name | did-you-mean; the new name from the old-name table |
| ST03 | E | parameter not in the action's schema (`id` and `comment` are allowed everywhere) | did-you-mean; `column`, `source`, `target_column`, `source_column` -> `columns` where that is the name |
| ST04 | E | required parameter missing (including every behaviour parameter without a Polars default: `na`, `how`, `maintain_order`, `seed`, ...) | the parameter and its allowed values |
| ST05 | E | `polars_join` in tier2 | |
| ST06 | E | a formula uses an operation outside the allowed list (section 15) | |
| ST07 | E | a parameter declared `multi` has a single value | write a list |
| ST08 | E | in profiles `run` and `build`: any `id` on a step (authors write none); in profile `audit`: an `id` that does not match `audit_<8 hex>_<k>`, or two steps with the same `id` | remove it (it is written by the app); names the place |
| ST09 | E | a reserved engine key (`__right_df__`, `__metadata__`, any `__name__`) in a step | remove it; the engine sets it |
| ST10 | E | the value of a parameter has the wrong shape for its declared widget (a list where a scalar is declared and the reverse; a repeated key in a `mapping`) | the declared form and the corrected text |
| ST11 | E | a conditional rule of the schema is broken (`when`, `require`, `one_of`, `exclusive`; R3) | the rule in words |
| J01 | E | unknown key in a join (`info`, `output_fields`, `final_contract`, ...) | replacement |
| J02 | E | join without `label` | |
| J03 | A | join without `description` | |
| J04 | E | `ingredients` missing, empty, not `{dataset_id}` items, unknown id, repeated id | |
| J05 | E | `right_ingredient` not in the join's ingredients; `on` and `left_on` both or neither | |
| J06 | E | `labels` not a mapping of text to text | |
| J07 | E | a join's `steps` is a flat list or `[]`, or has no `tier1` | `{tier1: [...]}` |
| J08 | E | a column name in both ingredients of a join, not a join key: the engine renames the second `name_right` silently (needs the recipe graph) | the message names both tables and the column; rename or drop one before the join (`polars_rename`, `polars_drop`) |
| J09 | E | the declared types of the two join keys differ (CHECKER-JOIN-KEYS-1, 2026-11-14; silent when the type of a key cannot be known from the declarations) | declare the same type for the key in both tables; a `polars_cast` before the join changes only the left table |
| J10 | E | a join key column is not declared in `input_fields` (CHECKER-JOIN-KEYS-1, 2026-11-14; silent when the type of a key cannot be known from the declarations) | write the key names as they are in each table: `on` for a name that is the same in both, `left_on` and `right_on` for names that differ |
| J11 | E | `left_on` and `right_on` have unequal length (CHECKER-JOIN-KEYS-1, 2026-11-14; silent when the type of a key cannot be known from the declarations) | write both with the same number of columns, paired by position |
| G01 | E | group without `label`; unknown key | |
| G02 | A | group without `description` | |
| P01 | E | plot entry without `label` or `spec`; unknown key (`info`) | `description` |
| P02 | A | plot without `description` | |
| P03 | E | plot id not snake_case | |
| P04 | E | `steps` at the plot entry holds anything but `tier3` | |
| P05 | E | `steps.tier3` is non-empty while the engine does not read it (one constant, switched with the reader; 7.7) | |
| P06 | E | `filters` in a plot spec, once the engine reads `steps.tier3` (R1) | `steps.tier3` |
| PS01 | E | unknown spec key | replacement |
| PS02 | E | `target_dataset` missing or unknown | |
| PS03 | E | `mapping` or `layers` missing; no geom/stat layer | |
| PS04 | E | layer without `name`; unknown component; argument unknown to the component's schema **and** to the wrapped plotnine function | did-you-mean |
| PS05 | E | `theme` not a registered theme | |
| PD01 | E | unknown `plot_defaults` key | |
| PA01 | E | a path in `source.path` or `reference_file` that is absolute, contains `..` or `~`, or is a URL (a development path, DEC30) | a path relative to the project root |
| PA02 | E | when the caller passes allowed roots: a development path that resolves outside them | |
| X1-X7 | E | the rules of section 10 | |
| CM01 | E | `comment` is not text | |
| GP01-GP06 | E | gallery profile rules (section 9) | |

The data check (a dataset that cannot be built, an `input_fields` entry with no column in the file) is **not** in this table: it needs the data and stays separate (`validate_data_analysis_recipe_data`).

## 12. Renamed and removed: the replacement table

Refused at once; the message names the new form. Mechanism: `utils/legacy_keys.py` (three dictionaries today, `legacy_keys.py:9-16`) grows to a table keyed by path and old key; the checker reads it only to write "use X". Nothing is converted silently `[DECIDED, DEC02]`. The old-to-new table of the action names is data of the migration tool and of `legacy_keys.py` (7.5.1).

| Where | Old | New |
|---|---|---|
| `info` | `display_name` | `label` |
| top level | (no `spec_version`: format 0) | `spec_version: 1` and the replacements of this table, by `migrate_recipe_format.py` |
| top level | `description` | `info.description` |
| top level | `name`, `pipeline_id` | `info.label`, `id` |
| top level | `metadata` | `metadata_schema` |
| top level | `plots`, `wrangling`, `input_fields`, `output_fields` | inside a group / inside a schema |
| top level | `type`, `join_manifests` | removed / `joins` |
| schema | `info` (with `category`, `sub_category`, `comment`) | removed: write `description` (what the table is) and `comment` (why) directly on the schema |
| schema | `fields` | `input_fields` |
| schema | `id` (inside the schema) | removed (the key is the id) |
| schema | `output_fields` | removed: the published columns are the last step of the collection's tier 1 |
| (no key) | the hidden sanitiser | `null_values` and `strip` on the schema (run A writes the 14 texts and `strip: true`) |
| field | `is_primary_key` | `is_entity_key` |
| field | `source_name` | `original_name` |
| field | `categorical` | `String` ("this was String"); `Categorical` stays a type for those who write it |
| field | `utf8`, `string`, `character` | `String` |
| field | `numeric`, `float` | `Float64` |
| field | `integer`, `int`, `i64` | `Int64` (a column whose cells are not whole numbers fails at the reader, naming the value; the migration reports it) |
| field | `date`, `bool`, `boolean` | `Date`, `Boolean` |
| field | `categories` as `@category` selection | removed (task REMOVE-CATEGORY-SELECT-1); `categories` is the level list of an `Enum` |
| step | `column`, `source`, `source_column`, `target_column` (where the schema says `columns`) | `columns` (or the Polars name in a `polars_` action) |
| step | any action name without a prefix | `polars_`, `modif_` or `step_` name (7.5.1) |
| step | `keep_columns`, `drop_columns` | `polars_select`, `polars_drop` (run B) |
| step | `mutate`, `add_constant` | `polars_with_columns` |
| step | `percentile` | removed |
| step | `how` on `join_filter` | `join_filter` is removed; `polars_join` with `how: semi` or `inner` |
| join | `info` (sentence) | `description` |
| join | `output_fields`, `final_contract` | the last step of `steps.tier1`; display names in `labels` |
| join | `recipe` | `steps` |
| join | ingredient as a bare id | `{dataset_id: id}` |
| plot entry | `info` (sentence) | `description` |
| plot spec | `description`, `info` | on the plot entry |
| plot spec | `family`, `pattern`, `difficulty` | removed from the spec; the place is `taxonomy` on the plot entry |
| plot spec | `facet_scales`, `labs`, `coordinate_flip` | `facet_wrap`/`labs`/`coord_flip` layers (issue #66) |
| `plot_defaults` | `height`, `show_legend` | removed |

## 13. How to write a description

A description is for the person who must choose where to filter or remove data and who did not build the recipe (`home_audit_steps.md` 5a-16). One or two sentences, with the facts the reader needs and no more:

| Element | Say |
|---|---|
| Recipe | the question, the population (all units or a subset, and why), the data and its date |
| Schema | **the grain** ("one row is ..."), the unit and how many (rows and units), what the recipe already removed (with the threshold), how missing values are treated (which texts, `null_values`) |
| Join | the grain of the result, the tables and the join type, whether rows multiply (one-to-many), what is removed |
| Group | the question the plots of the group answer |
| Plot | what is drawn and what is counted ("n of N"), which subset it leaves out, how a missing value is drawn |

Three kinds of "nothing" are never mixed: **not detected** (analysed, no hit: a real zero), **not analysed** (missing), **undeterminable** (a category such as "unknown"). The description says which of them the table holds. Numbers (rows, units) come from the data, not from memory.

**Write a description as a folded block** (`description: >-` then the text on the next lines): a plain text that contains a colon followed by a space is a YAML error and the recipe does not load (found twice while drafting the ST22 recipe; the checker reports it as T01 with the line). Descriptions describe the table **as it is**; a known defect or a planned change is named with `REVISE` and the issue, never hidden.

## 14. Where the checker and the rules live (verified 2026-11-13)

**The design.**

- **Core** `utils.recipe_check.check_recipe(raw, profile, *, catalogs=None, graph=None, roots=None) -> Result(problems, coverage)`. Pure. The rules are read from a packaged data file in `libs/utils` (D3). The catalogs (`actions`, `components`, `themes`, and the allowed argument names of each component) are **injected**; the recipe graph (`utils.recipe_graph`) is injected for the checks of columns per node; the allowed roots for development paths are injected (PA02).
- **`coverage`** lists which groups of checks ran (`structure`, `actions`, `components`, `columns`). A consumer that must have everything asserts it (HOME's gate does, with a test), so nothing is skipped silently.
- **One Tier-3 adapter**, today's `app/modules/data_analysis_recipe_validator.py` reduced to: build the catalogs from `transformer` and `viz_factory`, call the core, add the data check. HOME's gate, Blueprint's Validate, the import screen, the export and the audit copy, the scripts and the tests all call it.
- **Tier-2 consumers** call the core with the catalogs they own (`transformer` tests with the action catalog, `viz_factory` with the components, `viz_gallery` and `blueprint_arch` through their caller; `blueprint_arch` already holds an injected catalogue in `schema_registry`).
- **The loader** (`ConfigManager`, in `utils`) runs the checks that need no catalog (coverage `structure`) and stops on errors.
- **Callers of validation or loading today:** HOME's gate `bootloader.py:364-367`; the importer `bundle_importer.py:251`; Blueprint's Validate `blueprint_handlers.py:2803,2850` and six more loads; `retest_walkthrough.py:181`; the transformer pipeline `pipeline.py:49`; the cache keys `cache_keys.py:193`. New callers: the gallery, the audit copy, the forked recipe, the migration tool, the test-lab writers.
- **Verified by a prototype** on the ST22 recipe: with both catalogs the core finds the 3 step problems and the missing version and engine keys; with the action catalog only, the same; with no catalog the structure only, and the coverage says so.

**Does it respect the layer rules?** Yes (checked against each rule):

| Rule | Verdict |
|---|---|
| `rules_runtime_environment.md` 4, Tier 1: `libs/utils` has no import of another repository library and no Shiny; third-party packages are allowed when declared (polars, pyyaml; confirmed 2026-11-12) | respected: the core is Python and pyyaml; **verified by running** a prototype: after importing the core no peer library is loaded |
| Tier 2: a domain library imports `utils` only and declares it | respected: all six domain libraries declare `utils` |
| ADR-011 / `rules_viz_factory.md` 6a: a library does not read project files by path | respected: the specification file is the package's own resource (`importlib.resources`) |
| ADR-099 16(g): one rule set `check_recipe` and the recipe graph in `libs/utils` | decided; consistent |
| `rules_test_lab.md` 2c: a primitive needed by two domain libraries goes to `libs/utils` | the same reason (also the constants of the action names, R4) |
| ADR-094: HOME's gate lives in the app layer "on purpose" because only that layer may combine utils and transformer | stays true: the adapter combines them, only the rule set moves down; ADR-094 gets an "amended by" note |
| `rules_code_quality.md` 1: no emoji in docstrings, comments, raised messages | the gallery icons in the data file are allowed; messages name terms, never icons |
| `workspace_standard.md` 5-E: every new module and rule file carries a `@deps` block | to do with the module and the data file |

**Packaging condition** (verified by building two wheels of a copy of `utils`): the container installs the libraries **non-editable** (`assets/containers/Dockerfile:72-81`). Without `[tool.setuptools.package-data]` a YAML file inside `src/utils/` is silently **absent from the wheel**. No library ships a data file today, so `utils` is the first: declare `package-data` and add a test that builds the wheel and reads the file. (The Dockerfile also lists `libs/generator_utils`, a folder that no longer exists, and no `blueprint_arch`, `test_lab` or `id_reconciliation`; it is not ready and nothing is deployed: `DOCKER-RELEASE-1`.)

**Things that may move to `utils`** (a note; nothing is moved; `UTILS-REUSE-REVIEW-1`): (1) the plot-spec key sets `_CANONICAL_SPEC_KEYS` and `_VALID_PLOT_DEFAULTS_KEYS` (`plot_config_resolver.py:64-74`), which are facts about the format; (2) reading a step container, written four times (`DataWrangler._resolve_tier`, `tier2_steps` in `cache_keys.py:90`, `_step_blocks` of the validator, inline in the orchestrator); (3) the shape of a `ui_schema`, described by identical docstrings in two registries and read by `blueprint_arch.schema_registry` and `help_registry`; (4) two mechanisms for renamed keys (`utils/legacy_keys.py`, `app/modules/renamed_keys.py`, which also names a choice `manifest_paths` that does not exist: `DATA_LOOKUP_CHOICES` has two); (5) `extract_primary_keys` and the lineage helpers of `blueprint_arch` (to `utils.recipe_graph`, decided). What stays: the actions and components themselves and anything that needs Polars data or plotnine.

**One name to align with the HOME stage-2 draft:** it writes `check_recipe(raw, mode)` with `mode` = `run` or `build`; this file writes `profile`.

**How this file spreads once confirmed** (each rule gets one home):

| Part | Home | Why there |
|---|---|---|
| the normative rules in short | `.claude/rules/rules_data_analysis_recipe_structure.md` (changed only with Eve's double confirmation) | the agents' authority |
| the reference with one example per element | `docs/appendix/data_analysis_recipe_structure.yaml` and `Standards_yaml.qmd` | what a recipe maker reads |
| the checks as executable rules | `libs/utils` (`check_recipe`) and its tests, one test per row of section 11 | the code is the proof |
| how to write a description; missing values | the user guide and Blueprint's help | recipe makers |
| the text of the error messages | generated from the check table, not typed twice | no drift |

This file then becomes history (marked HISTORICAL, `rules_legacy_management.md`) and points to those homes.

## 15. Security: what a recipe may make the app run, read or write `[DECIDED, DEC44; design R5]`

Eve asked for a verified check that a bad recipe cannot do bad things. Inventory (evidence section 14, verified by reading, not yet attacked):

| Site | What a recipe can do today | Plan |
|---|---|---|
| formulas: `mutate`, the ID-reconciliation `mutate` (`id_reconciliation/core.py:239`), `stat_function` (`viz_factory/.../geoms/core.py:1335`, `eval(fun)` with no restriction) | run Python with `eval` (`__import__('os')` was run by a harmless probe); a recipe from outside runs code with the app's rights | formula check below, in the checker (ST06) **and** at the three sites |
| `sink_parquet` | write a Parquet file to any path | engine function, not a recipe action (DEC42) |
| `scan_parquet`, `derive_categories` `reference_file`, `source.path` | read any path the user can read; the content then appears in tables and exports | path rules below |
| `!include` | `os.path.join(dirname(recipe), included_file)`: `../..` and an absolute path read any YAML or text file (`config_loader.py:56-58`) | confined to the project root in the loader (T11); built, W3 |
| bundle import (zip) | `bundle_importer.py` extracts files; zip-slip not yet checked | HOME session: verify |
| `report.qmd` of an export | labels and reasons from a recipe are written into a Quarto file the user renders; a code cell in a label could run | HOME session: verify |
| YAML | `SafeLoader` everywhere (no object construction); aliases can still expand (memory) | low; test |
| regex | Polars uses the Rust regex engine (no catastrophic backtracking) | believed safe; test |
| agent adapter (`subprocess` of the `claude` CLI) | recipe text reaches an LLM prompt in Blueprint (developer app features only) | out of scope; noted |

**Formula check** (`libs/utils/src/utils/formula_check.py`, recipe session). Parse with `ast`. Allowed: `pl.<name>` where the name is on a SHORT explicit allow-list of module-level functions (`col`, `lit`, `when`, `all`, `any_horizontal`, ...), any `Expr` method or namespace except a deny set read from the signatures of the installed Polars (every method with a parameter annotated `Callable`: `Expr.map_batches`, `map_elements`, `pipe`, `rolling_map`, and the function form of `list.to_struct`; `str` and `dt` have none, evidence section 23), plus `meta` and anything starting with `_`, constants, arithmetic, comparison and boolean operators, lists, tuples, dicts, subscripts. Refused: any other bare name, `lambda`, comprehensions, a keyword call such as `eval` or `getattr`. The allow-list is at the module level because that is where file input and output live (`read_*`, `scan_*`, `write_*`, `sink_*`, `Config`); `Expr` methods are expressions only; the allow-list and the deny set are read from the installed Polars and pinned by a probe test (R9). `eval` also runs with `{"__builtins__": {}, "pl": pl}` (two layers). `stat_function` takes a Python lambda string (one shipped test): a separate grammar, a lambda of one argument whose body has only numbers, the argument, arithmetic (an exponent a constant up to 100) and an allow-list of math functions (`MATH_FUNCTIONS`: sin, cos, exp, log, sqrt, ...), or a bare math function name; the plot library supplies numpy for those names, with empty builtins. A refused string raises an error naming the fix; before, an unknown name (the documented example `fun: dnorm` among them) printed a warning and left the layer out silently. **Built in W3** (`libs/utils/src/utils/formula_check.py`); wired in ID reconciliation `mutate` (the old `col` name in scope is gone: only `pl`) and in `stat_function`; the transformer's `mutate` site (`polars_with_columns`) is wired in W6. **What Eve loses:** per-row Python functions. Tests: attack cases (`__import__`, `().__class__`, `lambda`, `getattr`, `pl.read_csv`, `pl.scan_parquet`) and a mutation check.

**Paths** (DEC30). Shape rule on a development path (`source.path`, `reference_file`): no absolute path, no `..`, no `~`, no URL (PA01); a gallery example's path is its own bundle file (GP06); the checker is pure, so when the caller passes allowed roots (the app: the deployment's `raw_data` and the references folder; tests: a temporary folder) the resolved path must lie inside one (PA02). Production ignores `source.path`. `reference_file` has one shipped use (`config/references/amr_phenotypes/...`, under no deployment location): it needs its own base, to be named. `scan_parquet` and `sink_parquet` are no longer recipe actions.

**Split of the work.** Recipe session: `formula_check.py`, the checker refusals, the `!include` confinement in `libs/utils/src/utils/config_loader.py` (the loader, not the checker, must refuse it: the include runs while the file is read). HOME session: attack tests, zip import, `report.qmd`.

**Known limit, written down:** a formula that is allowed can still be slow or large; nothing stops heavy computation. A recipe from outside is unverified until it passes the checker. A bundle is verified by hash against its own record; that proves it was not changed, not that it is safe.

## 16. What the code accepts today and must stop accepting

All are compatibility defaults under P2. Each is removed by the issue named (#76 checker and loader, #77 and #86 engine fixes, #78 migration and writers); a test per line.

| Where | What it tolerates | Removed with |
|---|---|---|
| `config_loader.py:18-41,136` | unquoted `on:` repaired with a printed warning | #76 (T07) |
| `config_loader.py:77-97` | fragment wrapper key removed silently | #76 (F01) |
| `config_loader.py` (PyYAML `SafeLoader`) | a repeated key keeps the last silently | #76 (T10): a loader that raises on a duplicate key |
| `config_loader.py:56-58` | an `!include` outside the project | built in W3 (T11) |
| `config_loader.py:141-211` | judges content: structure, renamed keys, source; only part of the rules | #76 (moves to `check_recipe`) |
| `data_wrangler.py:60-61` | an empty `wrangling` of any shape means "no steps" | #76 (S06) |
| `data_wrangler.py:132-147` | six spellings of the column selector, guessed and written back into the step | #76 (ST03). 14 steps in 10 recipe files rely on it today. No ADR decided the aliases (ADR-034 is the diagnostic message) |
| `data_wrangler.py:193-196`, `cleaning/core.py:320,349` | the entity keys put first and protected by `keep_columns` and `drop_columns` | #78 (DEC26, DEC37) |
| `cleaning/core.py:126`, `reshaping/core.py:202,205` | `rename` reads `target_column`; `split_column` reads `source`, `target_column`, `separator` | #76, #78 (ST03; section 8 RG2) |
| `ingestion/sanitizer.py`, `ingestor.py:169-178` | a hidden strip and 14 null texts on every text column; types `categorical`/`string` cast to String, others not cast | #78 (DEC27, DEC28) |
| `ingestor.py:80-92,107` | fuzzy file search by dataset name; `fields` alias | #76 |
| `metadata_validator.py:21-37,118` | type aliases; `source_name` | #76 |
| `orchestrator.py:59-62` | `final_contract` as a list skipped; missing columns printed | removed with `final_contract` (DEC23) |
| `orchestrator.py:151-157` | a repeated schema id replaces the first | #76 (S02) |
| `orchestrator.py:173,214-216,198-206,224` | bare ingredient; first join as fallback; all schemas as ingredients | #76 (J04) |
| `cache_keys.py:90`, `orchestrator.py` (Path A) | a schema's own tier-2 ignored | #77 |
| `home_theater.py:1119,903` | group label falls back to `description`; reads `info.display_name` | #78 |
| `blueprint_mapper.py:76-77` | node label from `display_name`, `sub_category`, or `description[:35]` | #78 |
| `plot_config_resolver.py:234-236` | non-canonical spec keys moved to `_meta` and kept | #76 (PS01); `_meta` is retired and replaced by declared keys (`comment`, `taxonomy`); ADR-083 sections 2 and 6 to amend |
| `bootstrapper.py:154`, `scaffolder.py:182`, `create_data_analysis_recipe.py:177`, `blueprint_handlers.py:2670` | write `display_name` / `name` | #78 |
| `app/modules/renamed_keys.py:20` | names a data-lookup choice `manifest_paths` that does not exist | with the next change of that file |

## 17. Tests that come out of this file (written first; they fail on today's code)

- One small invalid recipe per row of section 11: HOME refuses it, Blueprint reports it, the message holds the fix. A shared helper builds a minimal valid recipe so each test changes one thing.
- One test per row of section 12: the old form is refused and the message names the new one.
- One test per row of section 16: the tolerated form is now refused (mutation check: put the tolerance back and the test fails).
- Every shipped recipe of every kind in section 3 passes `check_recipe` with zero errors and zero advice (the retest scenarios with exactly their one planned fault). It replaces the recipe-folder test, the template test and the hygiene test, which become views of the same check.
- Shape tests (`TEST-SHAPES-1`): the shipped recipes as fixtures for no join, no key, another key name, no population table, long format.
- **Golden baseline (DEC43):** the content hash of every collection and every plot's data of every shipped recipe is recorded before any change; after each step every difference is listed. Run A must change none; run B changes only what is listed and shown to Eve.
- **Registries (section 8):** AR2 to AR6, the plotnine argument test, and the three new ones: prefix equals the `polars` field; every `polars_` action equals the direct Polars call (probe frame); no behaviour default other than the Polars default; no registered action name as a string outside the registry and the constants module (R4).
- **Container forms (5):** one test per refused form (a list where a dictionary belongs and the reverse, a bare string field, a flat `steps`, a wrapper key); a duplicate key is found by the loader; a removed `final_contract` is refused with the `polars_select` correction; after migration the plots that used a contract still render.
- **Order and ids (5, 7.5):** groups and plots keep their tab order; the hash changes when the order of steps changes and does not change when an `id` or a `comment` changes; a repeated or non-text `id` is refused; an app-inserted step has an `audit_` id; the copy minus the marked steps equals the original; a scan test requires `sort_keys=False` for every `yaml.dump` and `safe_dump` of non-test code.
- **Messages with the correction (5.1):** for each container-form check the message contains the generated corrected text; HOME's gate, Blueprint's Validate and the import screen show the same message.
- **Types and missing values (7.3, 7.4):** a table of declared dtype to resulting dtype through the ingestor for every dtype of the allow-list (the probe test pinned to the installed Polars); `2022.0` into `Int64` fails and names the value; each refused old name gives its message; `null_values` and `strip` are applied before the cast, in the defined order; a missing `null_values` or `strip` or `type` is refused; the migration writes today's 14 texts and no table changes.
- **Format version:** one test per V01 to V04; every shipped recipe, template, gallery example, written recipe and forked recipe carries `spec_version: 1`; `effective_run.yaml` records it.
- **Migration tool:** a format-0 recipe (from the git history of the ST22 recipe) becomes a recipe that passes the checker with advices only; run A changes no table hash; running it twice changes nothing; every `#` comment is kept; the list of manual steps is printed.
- **Comments:** a recipe with `#` comments passes untouched; every writer (Blueprint save, bootstrapper, scaffolder, the migration) keeps the comments of a fragment it edits.
- **Security (section 15):** attack tests for the formula check at every site, `!include` outside the folder, a path outside the allowed roots, zip-slip and `report.qmd` (HOME session).
- **Gallery protection:** the committed `gallery_index.json` equals the index rebuilt from the bundles; a bundle written by `GalleryManager.submit_example` passes the checker; every bundle renders its preview through the app path; every taxonomy term is in the vocabulary; the tag strip of each `example_meta.md` equals `taxonomy`.
- The tests that encode superseded behaviour are listed first (`TEST-ADAPT-1`): `test_empty_wrangling_is_valid` (`wrangling: []`), `test_tiered_steps_is_valid` and the other tests with inline recipes (no engines), the template and folder tests, the tests of `keep_columns`, `drop_columns`, `final_contract` and the sanitiser.

## 18. Errors from a data-science point of view (not format errors)

The format makes a recipe readable and checkable; it does not make it right. Eve's rule: those errors are fixed, not documented.

| Recipe | Known errors | Status |
|---|---|---|
| `1_test_data_ST22_dummy` | R1 `ST22_Anchor` joins two long tables (617 rows for 42 samples, `virulence_count` wrong for 18); R2 samples with only unknown phenotypes scored 0 (4 of 42); R3 the MLST plot shows 33 of 42 samples without saying so; R4 `virulence_variants` unreadable (16 panels) and coloured by a constant of the resistance table | agreed 2026-11-12; issues #67, #69, #70; task `RECIPE-ST22-FIX-1`; done **before** the ST22 descriptions are finalised, so they describe the corrected tables |
| the other pipelines (Abromics, `demo_abromics`, `figshare_integration`, `stress_test_master`, `2_` and `3_` ST22) | not reviewed one by one: Abromics was scanned (its one row-multiplying join, MLST by VirulenceFinder, is one-to-many and expected) but its plots were not looked at | a data-scientist pass per recipe (grain, joins and row counts, missing values, every picture) as part of its migration, #78 |
| templates, retest, gallery, transformer test recipes | not reviewed | gallery: every preview is looked at when regenerated; test recipes: their tests have raw-file oracles |

What the checker can catch of these (structure only): an ignored key (#66), an unknown parameter, a join that multiplies rows (#68, an advice with rows before and after). It cannot decide that a score of 0 for "unknown" is wrong; that stays the data scientist's review. A new risk of the same kind, now visible: the text `NA` read as a missing value in an identifier column (7.3).
