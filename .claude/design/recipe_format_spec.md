# Recipe format specification (draft v0.5, 2026-11-13)

**Written for:** Eve, to read and confirm. After that it is the base of the tests, of the checker (`check_recipe`), of the rule file and of the user documentation.
**Status:** DRAFT. Nothing is built from it yet. It was written by applying the decisions of 2026-11-11/12 and your answers of 2026-11-13 to the code (read at file:line) and to every recipe file in the repository (scans in `tmpAI/recipe_format/`, scratch). The worked example is `1_test_data_ST22_dummy`: section 12 and `recipe_format_st22_draft.yaml`.
**Tags:** **[DECIDED]** you decided it; **[MINE]** my choice while writing, to confirm (section 13 lists them all); **[OPEN]** not decided, with a recommendation; **[CODE]** fixed by what existing code reads or writes (verified, file:line).

**v0.2 (same day, after your review of v0.1):** (1) comments are specified (5b): `#` comments are free and kept, and an optional `comment` key exists; (2) the example variant (gallery) is now defined from what the gallery code reads and writes (6.9). It keeps `name`, the six-axis taxonomy, `data_path`, `wrangling` with `tier3` and its own file names, and it asks for no `label` or `description`; v0.1 refused `tier3` and renamed `name`, which would have broken the gallery; (3) the taxonomy is the gallery's and does not appear in a pipeline recipe (6.8); (4) the column-name aliases are replaced by what the action schemas already declare (6.5, 11); (5) science errors of recipes are fixed, not only described (15).

**v0.3 (same day, after your gallery message):** (1) the comment key is **`comment`** (singular). Blueprint already writes it on steps, layers, groups and plots (BP-COMMENTS-1, ADR-082 Q4; `blueprint_handlers.py:376-378,402-404`, `join_designer.py:153`), and ADR-083 gives every layer a `comment`. My v0.2 had `comments` and a checker that would have refused what Blueprint saves. It is renamed and accepted on every step and every layer (5b, 6.5, 6.8). (2) Section 6.9 (gallery) is **withdrawn**: you want the gallery to follow the same spec, so the v0.2 text that kept its own words is wrong. The options, with pros and cons, are in `recipe_format_gallery_options_2026-11-13.md`; 6.9 is rewritten when you choose.

**v0.5 (same day, after your question on the rules):** section 0b records the verified answer: a checker core and a specification data file in `libs/utils` respect the layering rules, with one packaging condition (found by building wheels) and one naming point to align with the HOME stage-2 draft (`mode` or `profile`).

**v0.4 (same day, after your next message):** (1) every recipe declares a **`format_version`** (section 4b), a good idea you took from the review of the app changes with another agent: it names the version of this specification that a file is written in, the checker refuses any other version and says which migration tool to run; (2) the gallery's `taxonomy` key is **required** in the gallery profile (optional in other recipes); (3) the question "can the allowed gallery terms be in the spec, one place instead of two?" is answered in the gallery options (D3): yes, if the specification itself is also a data file; section 0 says how.

## 0. Where this file lives and how it spreads (your question)

Yes, `.claude/design/` is the right place **while it is a draft**: it is the working text for you and for me, it changes by your review, and it holds the evidence. Once you confirm it, each rule has exactly one home (W1, one source of truth):

| Part | Home after confirmation | Why there |
|---|---|---|
| The normative rules in short (what is required, what is refused) | `.claude/rules/rules_data_analysis_recipe_structure.md` (agents obey it; changed only with your double confirmation) | the agent authority |
| The reference with one example per element | `docs/appendix/data_analysis_recipe_structure.yaml` and `Standards_yaml.qmd` (the rule file already names the appendix as the user-facing source of truth) | what a recipe maker reads |
| The checks as executable rules | `libs/utils` (`check_recipe`) and its tests, one test per row of section 8 | the code is the proof |
| How to write a good description | the user guide and Blueprint's help | recipe makers |
| The text of the error messages | generated from the check table (section 8), not typed twice | no drift |

This file then becomes history (marked HISTORICAL by the rule `rules_legacy_management.md`) and points to those homes.

**Proposal, to decide with the gallery options (D3): one place for the rules themselves.** The homes above hold the same facts in prose, in code and in tests, and they can drift. If the specification is also a **data file** in `libs/utils` (the allowed keys of each element, required or advice, the types, the vocabularies including the gallery terms, the table of renamed keys, the format version), then the checker, the filter panels, the markdown tables of the appendix, the error messages and the migration tool all read or are generated from that one file. Cross-element rules and the registries of actions and plot components stay in code. This is what makes "the authorised terms are in the spec" true in a way the program can use.

## 0b. Where the checker and the specification file live (verified 2026-11-13)

**Answer.** Yes, it respects our rules, and it is better for reuse. Two conditions came out of checking: the data file must be declared as package data (otherwise it is missing in the container), and the checker must receive the action and plot catalogs from its caller instead of importing them. Both are small. The decision is also already taken: ADR-099 16(g) and the stage-2 draft (`home_stage2_mechanism_spec.md` section 1) put `check_recipe` and `recipe_graph` in `libs/utils`.

| Rule or decision | What it says | Verdict |
|---|---|---|
| `rules_runtime_environment.md` section 4, Tier 1 | `libs/utils` has no import of another repository library and no Shiny; third-party packages are allowed when declared in its `pyproject.toml` (polars and pyyaml, confirmed 2026-11-12) | respected: the core is Python and pyyaml. **Verified by running** a scratch prototype (`tmpAI/recipe_format/proto/`): after importing the core, no peer library is loaded |
| Same, Tier 2 | a domain library imports `utils` only, and declares it | respected: `transformer`, `viz_factory`, `viz_gallery`, `blueprint_arch`, `ingestion`, `connector` all declare `utils` (verified) |
| ADR-011 / `rules_viz_factory.md` 6a | a library does not read project files by path (the palette precedent) | respected: the specification file is the package's own resource, read with `importlib.resources`, no project path; it must be **packaged** (below) |
| ADR-099 16(g), `home_audit_steps.md` 5a-8, stage-2 draft | one rule set `check_recipe` in `libs/utils`; the recipe graph in `libs/utils`; the loader builds and stops on errors | decided, consistent with this proposal |
| `rules_test_lab.md` 2c | a primitive needed by two domain libraries goes to `libs/utils` | the same reason |
| ADR-094 | HOME's gate lives in the app layer "on purpose": only that layer may combine utils and transformer | stays true: the app-layer adapter combines them; only the rule set moves down. ADR-094 gets an "amended by" note |
| `rules_code_quality.md` 1 (emoji) | forbidden in Python docstrings, comments and raised messages; allowed in YAML values | the gallery icons in the data file are allowed; messages name terms, never icons |
| `workspace_standard.md` 5-E (`@deps`) | every new module and rule file carries a `@deps` block | to do with the module and the data file |

**Packaging (verified by building two wheels of a copy of `utils`).** The container installs the libraries **non-editable** (`assets/containers/Dockerfile:72-81`). Without `[tool.setuptools.package-data]` a YAML file inside `src/utils/` is silently **absent from the wheel**; with the declaration it is included. No library ships a data file today, so `utils` would be the first: declare `package-data` and add a test that builds the wheel and reads the file. (While reading that Dockerfile I also found `libs/generator_utils` on line 79, a folder that no longer exists, and no `blueprint_arch`, `test_lab` or `id_reconciliation`; noted in `DOCKER-RELEASE-1`.)

**The design.**

- **Core** `utils.recipe_check.check_recipe(raw, profile, *, catalogs=None, graph=None) -> Result(problems, coverage)`. Pure; the rules are read from `utils/recipe_format.yaml`; the catalogs (`actions`, `components`, `themes`) are **injected**; the recipe graph (`utils.recipe_graph`) is injected for the checks of columns per node.
- **`coverage`** lists which groups of checks ran (`structure`, `actions`, `components`, `columns`). A consumer that must have everything asserts it (HOME's gate does, and a test asserts it for the gate), so nothing is skipped silently.
- **One Tier-3 adapter**, today's `app/modules/data_analysis_recipe_validator.py` reduced to: build the catalogs from `transformer` and `viz_factory`, call the core, add the data check. HOME's gate, Blueprint's Validate, the import screen, the export and the audit copy, the scripts and the tests all call the adapter.
- **Tier-2 consumers** call the core with the catalogs they own: `transformer` tests with the action catalog, `viz_factory` tests with the components, `viz_gallery` and `blueprint_arch` through their caller (`blueprint_arch` already holds an injected catalogue in `schema_registry`).
- **The loader** (`ConfigManager`, in `utils`) runs the checks that need no catalog (coverage `structure`) and stops on errors; the data check (needs the data files) stays separate.
- **Verified on the ST22 recipe by the prototype:** with both catalogs the core finds the 3 step problems found earlier (and the missing version and engine keys); with the action catalog only, the same; with no catalog, the structure only, and the coverage says so.

**Callers of validation or loading today** (verified): HOME's gate `bootloader.py:364-367`; the importer `bundle_importer.py:251`; Blueprint's Validate `blueprint_handlers.py:2803,2850` and six more loads; `retest_walkthrough.py:181`; the transformer pipeline `pipeline.py:49`; the cache keys `cache_keys.py:193`. New callers: the gallery, the audit copy, the forked recipe, the migration tool, the test-lab writers.

**One word to align with the HOME stage-2 draft.** It writes `check_recipe(raw, mode)` with `mode` = `run` or `build`. This file writes `profile` (`run`, `build`, `gallery`). HOME already has "Exploration | Audit mode" and `view_recipe(mode)`, so a third use of "mode" would confuse. Proposal: `profile`. It needs the two sessions to agree; your call.

## 1. What you decided on 2026-11-13

1. **Scope:** every recipe, in the app and in the tests (including automatic tests); the transformer files and the recipes written for tests are recipes. Everything that uses data and describes a read of data or a plot is concerned.
2. **Unknown keys fail.** Recipes can be verified first (Blueprint), so nothing needs to be tolerated.
3. **No backward-compatible default.** The old key system (`legacy_keys.py`) is kept for one purpose only: to **suggest the replacement** in the error message.
4. Old names are **refused at once** (not warned first).
5. `is_primary_key` becomes `is_entity_key`.
6. The **T3 container** is part of the schema now (audit mode comes soon).
7. A dataset plotted directly applies its own tier-2 list (fix of the engine).
8. Two **required** keys, `data_engine: python-polars` and `plot_engine: python-plotnine`.
9. A `description` is written for every element (if missing, filled by the rules of section 10).
10. Draft with `1_test_data_ST22_dummy`, because it is the most advanced and the default for your tests.
11. Comments on recipes must be possible, and comments need a specification (5b).
12. The Gallery keeps its taxonomy and its functionality; the specification is defined by what the gallery needs; the gallery taxonomy is not mixed with the recipe (6.8, 6.9).
13. A recipe can still contain errors from a data-science point of view; they must be fixed (15).

## 2. Principles (each one is a decision or follows from one)

- **P1 Executed, displayed, or refused.** Every key of a recipe either is executed by an engine, is displayed to the user, or is refused with the reason. A key that nothing reads does not exist. `[DECIDED, 5a-19]`
- **P2 No compatibility defaults.** A wrong recipe is corrected, never tolerated. When a key was renamed, the error says the new name. `[DECIDED, ADR-099 16(a), 2026-11-13]`
- **P3 One word for one thing.** `label` is the short name shown to the user; `description` is one or two sentences; `steps` and tiers are written the same way everywhere. `[DECIDED, 5a-9]`
- **P4 Generic words.** The format and the checker know no field-specific word (entity, attribute, table, not sample, gene). Field words live in recipes and help. `[DECIDED, W7]`
- **P5 An error says where, what and the fix.** `recipe : path : what is wrong. Fix: what to write.` `[MINE, from the message style that exists]`
- **P6 Looking for a problem is separate from running.** The checker reads the recipe (and the registries of actions and plot components) and never needs the data; the data check stays separate. `[DECIDED, O1]`

## 3. One format, two profiles, and what counts as a recipe

There is **one format**. A recipe is checked in one of two **profiles** that differ only in what an *empty placeholder* may be:

| Profile | Used by | An empty `analysis_groups` / `joins` / empty step list is |
|---|---|---|
| `run` | HOME's load gate; any program that draws plots | `analysis_groups` must hold at least one group with at least one plot |
| `build` | Blueprint (building step by step), recipes that only build data (transformer tests, scripts) | accepted (`analysis_groups: {}`, `tier2: []`, `tier3: []` are explicit placeholders) |

`[DECIDED, 5a-19: HOME rejects, Blueprint reports and never blocks building; empty placeholders accepted]` Everything else is identical in both profiles.

**What is a recipe (every one gets the format):**

| Kind | Files | Profile | Notes |
|---|---|---|---|
| Pipeline recipes, templates, retest scenarios | 7 + 5 + 4 | `run` | the retest scenarios that are faulty on purpose keep their one fault and must be otherwise valid |
| Transformer test recipes | 68 in `libs/transformer/tests/data` | `build` | flat form (`wrangling:` at the top, `input_fields:` at the top) is refused: each becomes one data schema with its `source` path (section 6.3). The runners already prefer a CLI data path over the recipe's (`rules_asset_scripts.md` 4), so nothing is lost |
| Legacy files | 2 (`VIGAS-P/VIGAS_VirulenceFinder.yaml`, `assets/ref_data/.../Virulence_genes_APEC_...yaml`) | `build` | no code reads them that I found; they follow the format or are removed, your call (13.6) |
| Gallery bundles | 34 | a standard recipe in a `gallery` profile (proposal, 6.9) | **undecided**: `recipe_format_gallery_options_2026-11-13.md`. They follow the same spec; the profile adds the rules of an example |
| Recipes written by the app | Blueprint "new recipe" form, test-lab bootstrapper and scaffolder, `create_data_analysis_recipe.py`, the export's forked recipe, the importer | the profile of their use | the checker runs on what they write; a test per writer; every writer emits `format_version` |
| Recipes inside automatic tests | inline YAML strings in tests and fixtures | as their purpose | one shared helper writes a minimal valid recipe, so no test types the boilerplate (W1) |

## 4. File level

| Key | Required | Value | Executed / shown by |
|---|---|---|---|
| `id` | yes | text equal to the file name without `.yaml` | selector, caches, sessions, export |
| `format_version` | yes | an integer: the version of this specification the file is written in (`1`) | the checker (V01-V04, 4b); exports record it; the migration tool reads it |
| `data_engine` | yes | `python-polars` (only value built) | checker now; fingerprint and export record it later (KEYS-NODE-1) |
| `plot_engine` | yes | `python-plotnine` (only value built) | same |
| `info` | yes | mapping (6.1) | Info panel, title banner, load gate contact |
| `entity` | no | mapping (6.2) | checker now; counts, attrition and caption in audit mode |
| `data_schemas` | yes | mapping `schema id -> data schema` (6.3), at least one | ingestion |
| `additional_datasets_schemas` | no | mapping `schema id -> data schema` | ingestion (same shape, same id space) |
| `metadata_schema` | no | one data schema; its id is the reserved word `metadata_schema` | ingestion, upload validation |
| `joins` | no | mapping `join id -> join` (6.6) | assembler |
| `analysis_groups` | yes | mapping `group id -> group` (6.7) | HOME tabs |
| `plot_defaults` | no | mapping (6.8) | plot engine |

**Refused at the top level, with the replacement the message names** (section 9; a missing `format_version` is the first of them, 4b): `plots`, `wrangling`, `input_fields`, `output_fields`, `name`, `pipeline_id`, `description`, `metadata`, `type`, `join_manifests`, and every other unknown key (did-you-mean by spelling).

## 4b. The format version `[MINE: name and form; the idea is yours]`

**What.** Every recipe declares `format_version: 1`, the version of this specification that the file is written in. The first confirmed specification is **format 1**; the drafts v0.x are drafts of it. The unversioned recipes of today are called **format 0**. The key is not `info.version`, which stays the author's own version of the recipe's content (`1.8`).

**The app reads one version** (no compatibility, P2). A recipe with another version is refused, in both profiles, with a message that says which version the app reads and which tool migrates.

**What changes the number.** Any change of *structure*: a key added, removed or renamed, a change of required-ness or meaning, a change of a closed vocabulary (the four types, the engine names). Not a new term in an *open* vocabulary (the gallery terms): those follow the app release, and an app that does not know a term refuses the recipe with "unknown term". A new optional key is a change too: with "unknown keys fail", an older checker cannot read it, so there is no "compatible minor version". That is why one integer is enough.

| Check | Sev | Trigger | Message says |
|---|---|---|---|
| V01 | E | `format_version` missing | this recipe is in the old format 0; run the migration tool |
| V02 | E | lower than the version the app reads | written for format N, the app reads M; migrate N to M |
| V03 | E | higher than the app reads | written for a newer format; update the app |
| V04 | E | not an integer (`"1"`, `1.0`, `true`) | write `format_version: 1` |

**Migration** (one tool, for us and for any user's recipes): `assets/scripts/migrate_recipe_format.py --from 0 --to 1`, built on the pattern of `migrate_config_vocabulary.py` (a dry run by default, `--apply` to write, safe to run twice). It edits the text, so every `#` comment is kept. It applies the replacement table of section 9 mechanically, adds `format_version` and the two engine lines, unwraps fragments, and writes a `label` made from the id as real text for the author to edit. It does **not** invent what is not mechanical: descriptions stay empty (an advice), `entity` is not added, science is not touched; it prints the list of what a person must still do. The shipped recipes are migrated with the same tool, then reviewed by hand.

**Where the number is recorded and used.** In every recipe written by the app (all writers), in the forked recipe of an export (copied), in `effective_run.yaml` of an export, and by the importer (its recipe leg says when the version differs). The spec keeps a history table:

| format | specification | status |
|---|---|---|
| 0 | the unversioned recipes before 2026-11-13 | refused with the migration message |
| 1 | this specification (drafts v0.1 to v0.x until Eve confirms) | to be in force |

**Consequences to accept.** (a) One more required key in every recipe (16 + 68 + 34 files, all writers, many tests); the migration tool does the mechanical part. (b) An export made under format 0 cannot be re-run by an app that reads format 1 until its recipe is migrated; the migrated recipe has another hash, so the importer's recipe leg reports a difference. This follows from "no compatibility default"; the bundle still holds the original file, and the version recorded in `effective_run.yaml` says which app generation can read it. (c) A number can be wrong (someone changes keys without changing it): the checker still reads the keys, so the error shows up as an unknown or missing key. (d) The same idea may later apply to the app-features and deployment files; not proposed now.

**Alternatives for the value.** A date (`2026-11-13`): readable, but not ordered by meaning. `major.minor` (`1.0`): the minor part cannot mean "compatible" here (see above). The app version: couples every recipe to every release. **Alternatives for the name:** `spec_version`, `recipe_format`, `schema_version`. `format_version` matches the words of this file.

## 5. Fragments (`!include`)

- `key: !include 'path/to/file.yaml'` puts the **content of the file exactly where the key is**. The path is relative to the folder of the recipe file `[MINE: verified in config_loader.py:55, nested includes use the same folder]`.
- **The fragment holds the value itself, with no wrapper key.** A file whose only top-level key repeats the key it is included under (`input_fields:` inside the file included as `input_fields:`) is refused with "remove the wrapper line". Today the loader removes the wrapper silently (`config_loader.py:77-97`); that is a compatibility default. The ST22 recipe has 68 includes: 56 are bare and 12 are wrapped. `[MINE: bare is the majority form; the rule file's "a plot file must have a single `spec:` root key" is wrong for 19 of 23 plot files]`
- A missing file is an error naming the file.
- Comments: see 5b.

## 5b. Comments (specified)

Two things are called a comment. Both are allowed.

| What | Form | Rule |
|---|---|---|
| A YAML comment | `# any text`, on its own line or after a value, in the recipe or in any fragment | **Free, anywhere, never refused.** It is not a key: the loader drops it, the checker never sees it, nothing validates it. It belongs to the author. **Any tool that edits a recipe or a fragment keeps every comment** (a text-level edit or a round-trip library, never `yaml.dump`); a test per writer checks it. This is the "do not remove" I meant, and it is a rule for my tools, not for you: the first line of `input_fields/Summary_input_fields.yaml` is your note "USER SAYS : do not remove my comments", and the ST22 recipe holds 150 comment lines (10 in the main file, 140 in its fragments) that explain defaults ("if omitted its default to categorical") and why a column is kept or dropped. They are documentation. |
| A `comment` key | `comment: text`, optional, on `info`, a data schema, a join, a group, a plot entry, **every step and every layer** | The author's note of **intent: why, not what** (the hint of Blueprint's comment boxes). Read by people, never executed, never passed to an action or to the plot engine. This is the standard that exists: Blueprint writes it on steps (`blueprint_handlers.py:402-404`), layers (`:376-378`) and join steps (`join_designer.py:153`), and ADR-083 lists `comment` in the layer model. Shown in Blueprint's node information and in the node popup (to wire in package E, #78). It is not the `description`: the description says **what the element is** (its grain, what was removed); `comment` says why, or anything else the next person should know. Two ST22 schemas used a plural `info.comments` (for example "Filtered by % identity > 90 ..."); it becomes `comment`. `[CODE for steps, layers, groups, plots; MINE for info, schema, join]` |

## 6. The elements

Columns of every table: key, required (R), optional (o), advice (a = never blocks), meaning.

### 6.1 `info` (the recipe's own card)

| Key | R | Meaning |
|---|---|---|
| `label` | R | the short name of the recipe (was `display_name`) |
| `description` | a | what the recipe answers, for which population, from which data (section 10) |
| `subtitle` | o | shown under the title in HOME (`home_theater.py:905`) |
| `contact` | a | who to call when the recipe fails; the load gate shows it (ADR-094) |
| `version` | o | text |
| `comment` | o | the author's note (5b) |
| any other key | o | **free-form**, displayed in the Info panel, never executed (`data_analysis_recipe_info.py`). This block is the only free-form block of the format |

### 6.2 `entity` (optional)

| Key | R | Meaning |
|---|---|---|
| `noun` | R | the unit in the singular, in the recipe's own word |
| `plural` | R | the same in the plural |
| `population` | R | the id of the table (a data schema or a join) with one row per unit; the start of the attrition flow |

Checks: the id exists; that table carries an entity key (6.4). Without `entity` the software says "entities" and never guesses from column names. `[DECIDED, 5a-17]`

### 6.3 Data schema (`data_schemas.<id>`, `additional_datasets_schemas.<id>`, `metadata_schema`)

| Key | R | Meaning |
|---|---|---|
| `label` | R | short name |
| `description` | a | the grain (what one row is), the entities, what the recipe already removed, how missing values are treated (section 10) |
| `category`, `sub_category` | o | grouping text shown in Blueprint `[MINE: replaces the retired `info:` block, 13.3]` |
| `comment` | o | the author's note (5b); was `info.comments` |
| `source` | R | `{type, path}`; `type` is `local_tsv` or `local_parquet`; `path` is relative to the project root. The fuzzy search of a file by dataset name (`ingestor.py:80-92`) is removed |
| `input_fields` | R | mapping `column slug -> field` (6.4); `{}` means no contract |
| `wrangling` | R | `{tier1: [...], tier2: [...]}` (6.5); `tier1` required, `tier2` optional; **`[]` and a flat list are refused** |
| `output_fields` | o | mapping `column slug -> field`; the columns the schema publishes. Checked by the data check, **not applied by the engine** `[OPEN 13.5]` |

- The three sections share **one id space**; a repeated id is an error (today the second silently replaces the first, `orchestrator.py:151-157`). `metadata_schema` is a reserved id.
- `tier2` of a schema is applied **only when the schema is plotted directly** (a collection, `target_dataset`); on a schema that is only an ingredient it is an error ("never applied"). `[DECIDED, RECIPE-DATASET-TIER2-1]`
- The key `fields` (alias of `input_fields`, `ingestor.py:107`) and `info:` are refused.

### 6.4 Fields (`input_fields.<slug>`, `output_fields.<slug>`, `final_contract.<slug>`)

| Key | Where | Meaning |
|---|---|---|
| `type` | o | `categorical` (default), `utf8`, `numeric`, `date`. Anything else is an error. The default is yours and documented in your fragments (`type` omitted means `categorical`) `[MINE: the type vocabulary below]` |
| `original_name` | o | the column name in the file when it differs (input side); shown in Blueprint |
| `label` | o | display name (default: the slug) |
| `is_entity_key` | o | `true` when the column identifies the entity (it repeats in long tables). Replaces `is_primary_key`. `[DECIDED]` |
| `categories` | o | list of text; a step can then select `@category` (`data_wrangler.py:31-48`) |

`{}` in an output list means "keep this column as it is" (your fragments use it).
**Type vocabulary** `[MINE]`: today three lists overlap (`metadata_validator.py:21-37` accepts `int`, `integer`, `float`, `bool`, `boolean`, PascalCase), the ingestor casts only three of them (`ingestor.py:162-170`), and `i64` (4 fixtures) is accepted by the validator and ignored by the ingestor. One list of four, each handled the same way by ingestion, by the upload check and by the contract.

### 6.5 Steps and tiers

- A **step list** is `{tier1: [...], tier2: [...]}`. It appears as `wrangling` (data schema), `steps` (join) and, at the plot entry, `steps: {tier3: [...]}` (6.7). All three are written the same way; an empty list means "equal to the previous node". `tier1` is required except at the plot entry; an unknown tier name is an error. `[DECIDED, 5a-15]`
- A **step** is a mapping with `action` (a registered name), exactly the parameters in that action's `ui_schema.params`, and optionally `comment` (5b; it is not a parameter and is never passed to the action) (`libs/transformer/.../actions/base.py`). A missing required parameter, an unknown parameter and an unknown action are errors, with a did-you-mean by spelling. **The registry is the one source of the parameter contract** (W1): a test checks that the keys each action's code reads equal its schema. Today 65 of 67 actions have a schema. `scan_parquet` and `sink_parquet` have none: the rules call them engine-internal, but 4 fixture steps use them to test the actions themselves `[OPEN 13.13]`.
- **No guessing between spellings of a parameter.** Before a step runs, the wrangler looks for "which columns does this step work on" in six spellings in a fixed order (`columns`, `column`, `source`, `source_column`, `target_column`, and the boolean key that an unquoted `on:` becomes), expands `@category` names, checks that the columns exist (the friendly "did you mean" message of ADR-034), and **writes the result back into the step as `columns`** (`data_wrangler.py:132-147`). So a step that says `column:` for an action whose schema says `columns` works by accident. What goes is the guessing, not the check and not `@category`: those keep working, but they read **the parameters that the action's own schema declares as column selectors** (the schemas already do: 71 parameters in 59 of 65 actions, for example `columns`, `column`, `on`, `index`). A misspelled parameter is then reported by the checker before the run, with the right name (ST03). `[MINE: the mechanism; the principle is your "no compatibility default"]`
- `join` and `join_filter` only in tier1 (exists today, kept). `join_filter` has no `how` parameter; it is always inner (`joins.py`), so `how` on it is an error.
- `'on'` is quoted. An unquoted `on:` becomes the boolean key `True`; today the loader repairs it with a printed warning (`config_loader.py:18-41`). It is an error: the repair is a compatibility default.
- Formulas (`mutate` `expression`, plot function strings) may use only an allowed list of Polars operations by function name. The list is package H (13.8).
- Reserved for audit mode: an origin marker on audit-written steps (id, reason). Its name is set with the step compiler. `[OPEN]`

### 6.6 Join (`joins.<id>`), a collection built from schemas

| Key | R | Meaning |
|---|---|---|
| `label` | R | short name |
| `description` | a | what one row is, which tables are combined and how, what is removed, what a missing value means here |
| `comment` | o | the author's note (5b) |
| `ingredients` | R | list of `{dataset_id: <schema id>}`, at least one; **the first is the base** of the join. A bare id (`- FastP`) is refused (`orchestrator.py:173,214`) |
| `steps` | R | step list (6.5), `{tier1: [...]}` at least |
| `final_contract` | o | mapping `column -> field`, an **exclusive whitelist**: the collection keeps exactly these columns. A list is refused (today it is skipped silently, `orchestrator.py:59-62`); a column that the collection does not have is an error (today only printed) |

`output_fields` or `info` on a join are refused (the message says `final_contract` and `description`). Each `right_ingredient` of a step is one of the join's `ingredients`; `on` or `left_on` with `right_on` names the key (not both).
The orchestrator's silent fallbacks go: an unknown collection falls back to the first join (`orchestrator.py:198-206`) and a join without ingredients uses all schemas (`orchestrator.py:224`).

### 6.7 Analysis group and plot entry

`analysis_groups.<group id>`: `label` (R, the tab text), `description` (a), `comment` (o, 5b), `plots` (R, mapping; at least one in profile `run`). The fallback "label, else description, else id" (`home_theater.py:1119`) goes: today 4 of the 5 groups of the ST22 recipe have the tab text in `description`.

`plots.<plot id>` (snake_case, **unique over all recipes**):

| Key | R | Meaning |
|---|---|---|
| `label` | R | the plot's tab text |
| `description` | a | what it shows, what is counted, which subset it leaves out (section 10) |
| `comment` | o | the author's note (5b) |
| `spec` | R | the plot specification (6.8) |
| `steps` | o | `{tier3: [...]}`: the steps applied to this plot's table, after its T2. Any registered action; the audit mode writes only filters and drops here. Omitted or empty means the plot reads its table as it is. `[DECIDED, 5a-15; name and place MINE, 13.4]` |

`info:` on a plot entry (a sentence, 25 times today) is refused: the message says `description`.

### 6.8 Plot specification, layers, `plot_defaults`

`spec` keys, the set the plot engine reads (`plot_config_resolver.py:71-74`): `target_dataset` (R, a join id or a schema id), `mapping` (R), `layers` (R, at least one geom or stat), `title`, `theme`, `facet_by`, `palette`, `labels`, `guides`, `filters`. Everything else is an error, with the replacement of section 9 where one exists (`facet_scales`, `labs`, `coordinate_flip` become layers, issue #66). `description` and `info` are refused inside a spec: they are the plot entry's (6.7). The gallery taxonomy keys `family`, `pattern`, `difficulty` are refused in a pipeline spec **because the taxonomy is the gallery's, not the recipe's** (your "do not confound"): it lives today in the `info` of each gallery bundle (the gallery options propose a `taxonomy` key on the plot entry instead), it is read only by `GalleryManager.rebuild_index` from there (`gallery_manager.py:133-168`), and no code reads it from a pipeline plot. 16 of the 17 ST22 specs carry three of the axes only because they were copied from gallery examples when the plots were first written (2026-04-10). If a recipe plot is offered to the Gallery later, `GalleryManager.submit_example` takes the six values as arguments (`gallery_manager.py:28-33`) and writes them into the bundle; it does not read them from the plot. A note about a plot goes in `comment` (5b). `[MINE; 13.14]`
`mapping`: keys are aesthetic names of the plot engine (`x`, `y`, `fill`, `color`, `group`, `facet_by`, ...), values are column names of the target table (the "column exists at that node" check is package J, it needs the recipe graph).
`layers`: list of `{name, params, comment}` (`comment` optional, 5b; ADR-083); `name` is a registered component (all 191 have a schema; none of the 167 layers in the repository has an unknown name); `params` are checked against the component's schema plus the plot engine's own arguments `[MINE: mechanism to verify in package B; today 10 parameters in 8 components are outside the schemas, all valid plotnine arguments such as `color`]`.
Two forms exist for the same thing (`facet_by` at the top of the spec and inside `mapping`; `filters` in the spec and the T3 list): both are read today. They stay allowed and are listed in 13.7 for the plot-engine owner (Blueprint) to simplify.
`plot_defaults` keys: `palette`, `theme`, `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`, `layers` (`plot_config_resolver.py:64-67`). `height` and `show_legend` (2 templates) are errors.

### 6.9 The gallery: withdrawn until you choose

v0.2 kept the gallery's own file shape and words. You asked for the opposite: the examples follow the same spec (they are examples of recipes), are checked by the same code as the app, and the gallery's special needs are added to the spec as a profile. Investigated, with a proof of concept that renders all 34 examples as standard recipes through the app's own path: `recipe_format_gallery_options_2026-11-13.md` (what is wrong today, six decisions with pros and cons, what changes, in which order). The recommended design adds to this spec: a `gallery` profile (section 3), one optional key on the plot entry (`taxonomy`, 6.7), one dictionary of the gallery terms, and checks in section 8. Nothing of it is in force until you choose.

## 7. Rules that span elements

| # | Rule |
|---|---|
| X1 | ids are unique across `data_schemas`, `additional_datasets_schemas` and `metadata_schema`; join ids do not repeat a schema id (a plot's `target_dataset` must name one thing) |
| X2 | `target_dataset` of a plot exists; every `dataset_id` of an ingredient exists; every `right_ingredient` is an ingredient of its join |
| X3 | `entity.population` exists and carries an entity key |
| X4 | a schema's `tier2` is applied only if the schema is a plot's target; otherwise an error |
| X5 | `id` equals the file name; plot ids are unique **across the recipes of a folder** (a project-level check, `check_recipe_set`) |
| X6 | the key family: the entity-key columns of the schemas are linked by the join keys; first version has one family (`home_audit_steps.md` 5a-13). Not a failure if absent |
| X7 | a step or a `final_contract` that names a column the node does not have is an error (the dry run on column names). Needs the recipe graph: package J |

## 8. The check catalogue (one row = one test)

Severity: **E** error (HOME refuses; Blueprint reports and does not block building), **A** advice (shown, never blocks). IDs are permanent; messages are generated from this table with the replacement of section 9.

| ID | Sev | Trigger | Fix named in the message |
|---|---|---|---|
| T01 | E | file missing, not YAML, not a mapping | |
| T02 | E | `!include` target missing | create the file or correct the path |
| T03 | E | unknown top-level key | replacement (section 9) or did-you-mean |
| T04 | E | `id`, `data_engine`, `plot_engine`, `info`, `data_schemas`, `analysis_groups` missing | add it |
| T05 | E | `id` differs from the file name | exists today |
| V01-V04 | E | `format_version` missing, older, newer, or not an integer (4b) | the migration tool, or update the app |
| T06 | E | engine value unknown, or a plot engine in the data slot | say the built values |
| T07 | E | unquoted `on` (a `True` key) anywhere | quote it |
| T08 | E | root `plots:` | move into a group |
| T09 | E | profile `run`: no group or no plot | add one |
| F01 | E | fragment wrapper repeats the include key | remove the wrapper line |
| F02 | E | fragment has the wrong type (list for a mapping) | |
| I01 | E | `info` not a mapping, or `label` missing | add `label` |
| I02 | A | `info.description` or `info.contact` missing | write it (section 10) |
| I03 | E | `info.display_name` | `label` |
| E01 | E | unknown key in `entity`; `noun`/`plural`/`population` missing | |
| E02 | E | `population` unknown, or its table has no entity key | |
| S01 | E | unknown key in a schema (`info`, `fields`, `id`, ...) | replacement |
| S02 | E | repeated schema id; use of the reserved id | |
| S03 | E | schema without `label` | add it |
| S04 | A | schema without `description` | write it |
| S05 | E | `source` missing, type not `local_tsv`/`local_parquet`, `path` missing | |
| S06 | E | `wrangling` is a flat list, `[]`, or has no `tier1`; unknown tier key | `{tier1: []}` |
| S07 | E | `tier2` on a schema that is only an ingredient (never applied) | move it to a join, or plot the schema |
| S08 | E | `input_fields` / `output_fields` not a mapping | |
| FD01 | E | unknown field property | replacement |
| FD02 | E | `type` not one of the four | `numeric` / `categorical` / `utf8` / `date` |
| FD03 | E | `is_primary_key` | `is_entity_key` |
| FD04 | E | `source_name` | `original_name` |
| FD05 | E | `is_entity_key` not true/false; `categories` not a list of text | |
| ST01 | E | step without `action` (shorthand), or not a mapping | |
| ST02 | E | unknown action | did-you-mean |
| ST03 | E | parameter not in the action's schema (`comment` is allowed on every step) | did-you-mean; `column`, `source`, `target_column`, `source_column` -> `columns` where that is the name |
| ST04 | E | required parameter missing | |
| ST05 | E | `join` or `join_filter` in tier2 | exists today |
| ST06 | E | formula uses an operation outside the allowed list | package H |
| J01 | E | unknown key in a join (`info`, `output_fields`, ...) | replacement |
| J02 | E | join without `label` | |
| J03 | A | join without `description` | |
| J04 | E | `ingredients` missing, empty, not `{dataset_id}` items, unknown id, repeated id | |
| J05 | E | `right_ingredient` not in the join's ingredients; `on` and `left_on` both or neither | |
| J06 | E | `final_contract` not a mapping, or names a column the collection lacks | |
| G01 | E | group without `label`; unknown key | |
| G02 | A | group without `description` | |
| P01 | E | plot entry without `label` or `spec`; unknown key (`info`) | `description` |
| P02 | A | plot without `description` | |
| P03 | E | plot id not snake_case | exists in the rule |
| P04 | E | `steps` at the plot entry holds anything but `tier3` | |
| PS01 | E | unknown spec key | replacement (section 9) |
| PS02 | E | `target_dataset` missing or unknown | |
| PS03 | E | `mapping` or `layers` missing; no geom/stat layer | |
| PS04 | E | layer without `name`; unknown component; parameter unknown to the component | did-you-mean |
| PS05 | E | `theme` not a registered theme | |
| D01 | E | unknown `plot_defaults` key | |
| X5 | E | duplicate plot id across the recipes of a folder; duplicate recipe id | |
| CM01 | E | `comment` is not text | |
| GP | E | gallery profile rules (one plot, `taxonomy` in the dictionary, `id` equal to the folder, companion files) | defined with the gallery decision (gallery options, section 7, item 1) |

The data check (a dataset that cannot be built, an `output_fields` slug with no column) is **not** in this table: it needs the data and stays as it is (`validate_data_analysis_recipe_data`).

## 9. Renamed and removed: the replacement table (refused at once; the message names the new form)

Mechanism: `utils/legacy_keys.py` (today three dictionaries of renamed keys, `legacy_keys.py:9-16`) grows to a table keyed by the path and the old key; the checker reads it only to write "use X". Nothing is converted silently. `[DECIDED 2026-11-13]`

| Where | Old | New |
|---|---|---|
| `info` | `display_name` | `label` |
| top level | (no `format_version`: format 0) | `format_version: 1` and the replacements of this table, by `migrate_recipe_format.py` |
| top level | `description` | `info.description` |
| top level | `name`, `pipeline_id` | `info.label`, `id` |
| top level | `metadata` | `metadata_schema` |
| top level | `plots`, `wrangling`, `input_fields`, `output_fields` | inside a group / inside a data schema |
| top level | `type`, `join_manifests` | removed / `joins` (exist today) |
| data schema | `info` (`category`, `sub_category`, `comment`) | `category`, `sub_category`, `comment` directly on the schema (`info:` itself is refused) |
| data schema | `fields` | `input_fields` |
| data schema | `id` (inside the schema) | removed (the key is the id) |
| field | `is_primary_key` | `is_entity_key` |
| field | `source_name` | `original_name` |
| field | `type: string`, `character` | `categorical` or `utf8` (exists) |
| field | `type: int`, `integer`, `float`, `bool`, `boolean`, `i64`, `Int64`, `Float64`, `String`, `Boolean`, `Date`, `Categorical` | `numeric`, `categorical`, `date` |
| step | `column`, `source`, `source_column`, `target_column` (where the schema says `columns`) | `columns` |
| step | `how` on `join_filter` | removed (always inner) |
| join | `info` (sentence) | `description` |
| join | `output_fields` | `final_contract` |
| join | `recipe` | `steps` (exists) |
| join | ingredient as a bare id | `{dataset_id: id}` |
| plot entry | `info` (sentence) | `description` |
| plot spec | `description`, `info` | on the plot entry |
| plot spec | `family`, `pattern`, `difficulty` | removed from the spec; the proposed place is a `taxonomy` key on the plot entry (gallery options D2) |
| plot spec | `facet_scales`, `labs`, `coordinate_flip` | `facet_wrap`/`labs`/`coord_flip` layers (issue #66) |
| `plot_defaults` | `height`, `show_legend` | removed |

## 10. How to write a description (the rule for filling the missing ones)

A description is for the person who must choose where to filter or remove data and who did not build the recipe (`home_audit_steps.md` 5a-16). One or two sentences, with the facts the reader needs and no more:

| Element | Say |
|---|---|
| Recipe | the question, the population (all units or a subset, and why), the data and its date |
| Data schema | **the grain** ("one row is ..."), the unit and how many (rows and units), what the recipe already removed (with the threshold), how missing values are treated |
| Join | the grain of the result, the tables and the join type, whether rows multiply (one-to-many), what is removed |
| Group | the question the plots of the group answer |
| Plot | what is drawn and what is counted ("n of N"), which subset it leaves out, how a missing value is drawn |

Three kinds of "nothing" are never mixed: **not detected** (analysed, no hit: a real zero), **not analysed** (missing), **undeterminable** (a category such as "unknown"). The description says which of them the table holds. Numbers (rows, units) come from the data, not from memory: `tmpAI/recipe_format/st22_facts.py` computes them.

**Write a description as a folded block** (`description: >-` then the text on the next lines). A plain text that contains a colon followed by a space (`One row per sample: the main taxon ...`) is a YAML error and the recipe does not load (found twice while writing the ST22 draft; the checker reports it as T01 with the line). Descriptions describe the table **as it is**; a known defect or a planned change is named with `REVISE` and the issue, never hidden.

## 11. What the code accepts today and must stop accepting

All of these are compatibility defaults under P2. Each is removed in the package named; a test per line.

| Where | What it tolerates | Removed with |
|---|---|---|
| `config_loader.py:18-41,136` | unquoted `on:` repaired with a printed warning | C (T07) |
| `config_loader.py:77-97` | fragment wrapper key removed silently | C (F01) |
| `config_loader.py:141-211` | judges content: structure, renamed keys, source; only part of the rules | C (moves to `check_recipe`) |
| `data_wrangler.py:60-61` | an empty `wrangling` of any shape means "no steps" | C (S06) |
| `data_wrangler.py:132-147` | six spellings of the column selector, guessed in a fixed order and written back into the step | C (ST03). The presence check and `@category` stay but read the parameters the action's schema declares as column selectors. Exactly 14 steps in 10 recipe files rely on a wrong spelling today (probe). No ADR decided the aliases (ADR-034 is the diagnostic message); covered by your "no compatibility default" |
| `ingestor.py:80-92,107` | fuzzy file search by dataset name; `fields` alias | C |
| `metadata_validator.py:21-37,118` | type aliases; `source_name` | C |
| `orchestrator.py:59-62` | `final_contract` as a list skipped; missing columns printed | C (J06) |
| `orchestrator.py:151-157` | a repeated schema id replaces the first | C (S02) |
| `orchestrator.py:173,214-216,198-206,224` | bare ingredient; first join as fallback; all schemas as ingredients | C (J04) |
| `cache_keys.py:90` (`tier2_steps`), `orchestrator.py` (Path A) | a schema's own tier-2 ignored | D |
| `home_theater.py:1119,903` | group label falls back to `description`; reads `info.display_name` | E |
| `blueprint_mapper.py:76-77` | node label from `display_name`, `sub_category`, or `description[:35]` | E |
| `plot_config_resolver.py:234-236` | non-canonical spec keys moved to `_meta` and kept | C (PS01); `_meta` is retired and replaced by declared keys (`comment`; proposed `taxonomy`); ADR-083 sections 2 and 6 to amend |
| `bootstrapper.py:154`, `scaffolder.py:182`, `create_data_analysis_recipe.py:177`, `blueprint_handlers.py:2670` | write `display_name` / `name` | E |

## 12. What applying the spec to `1_test_data_ST22_dummy` showed

The draft is `recipe_format_st22_draft.yaml` (main file only; the fragment files follow in package E). Baseline of all 12 schemas and 17 collections: `tmpAI/recipe_format/st22_baseline.json` (content hashes): the migration must keep every hash except the two named changes below.

| # | Finding | Evidence | Consequence |
|---|---|---|---|
| 1 | Group tab text is in `description` (4 of 5 groups) | `1_test_data_ST22_dummy.yaml:278-324`, `home_theater.py:1119` | label and description swap; the code fallback goes |
| 2 | `info:` sentence on all 17 plot entries and `description` inside 14 of the 17 specs: the same fact twice | recipe 281-349, `plots/*.yaml` | one `description` on the entry; spec keeps only the grammar |
| 3 | `family`, `pattern`, `difficulty` in 16 specs; copied from gallery examples in the first commit of these plots (2026-04-10); no code reads them from a pipeline plot | grep of readers: only `gallery_manager.py`, from a bundle's `info` | removed from pipeline specs; the taxonomy stays in the gallery (6.9) |
| 4 | Schemas carry `info: {category, sub_category, comments}` (11 of 12), the comments hold real facts ("filtered by identity > 90 ...") | recipe 19-151 | `category`, `sub_category` and `comment` kept as keys on the schema (5b); the draft restores both `comment` |
| 5 | `Quality_metrics` has `wrangling: []` | recipe line 43 | `{tier1: []}` |
| 6 | `ResFinder` tier-2 (`count_by_group`, `sort`) is ignored; the plot `amr_heatmap` reads it directly | baseline: T2 hash equals T1 hash | **change 1:** the plot gets `total_gene_count` and the sort. Evidence: pictures before and after |
| 7 | Join `Summary_phenotype_length_fragmentation` has `info:` (a sentence) and an `output_fields` that nothing reads | recipe 195-203, `orchestrator.py:59` | `description` and `final_contract`. The whitelist lists 5 columns and the collection has 5 (126 x 5): **expected no data change; verify** |
| 8 | 3 steps outside their schema: `split_and_explode column`, `split_column source`, `join_filter how` | probe | `columns`; `columns` (+ the rest of that schema to check); `how` removed |
| 9 | 12 of 46 includes are wrapped | scan | wrappers removed, comments kept |
| 10 | The two reference-style schemas (`APEC_STEC_virulence_genes`, 11 rows, no entity key) sit in `additional_datasets_schemas` with inline wrangling and `output_fields: {}` | recipe 127-139 | fine; shows a schema without a key |
| 11 | `Summary` and `Summary_quality` read the same file as two schemas; `Quality_metrics` and `Detailed_summary` are not used by any join or plot | recipe, scan | descriptions say so; removal is your decision (issue #69 item) |
| 12 | A comment in `Summary_input_fields.yaml` says "do not remove my comments" | the file | edits are text-level |
| 13 | The ST22 recipe has R1-R4 pending (anchor without ResFinder, ...) | `recipe_review_st22_2026-11-11.md` 3b | descriptions of `ST22_Anchor`, `Summary_phenotype_length_fragmentation`, `MLST_with_metadata` are written for the table **as it is today** and marked to update with R1-R4 |
| 14 | Writing the draft: two descriptions with `: ` in plain text made the file unloadable | the IDE and `yaml.load` both refused lines 222 and 241 of the first draft | section 10 now says "folded block"; the checker's T01 names the line; the draft parses and has no element without `label`/`description` |
| 15 | Review of v0.1: my gallery variant refused `tier3` and renamed `name` to `label`; both would break the gallery (`submit_example` writes `tier3`; the index reads `name`) | `gallery_manager.py:59-63,138` | 6.9 follows the gallery code |

## 13. My choices to confirm, and the open points

1. **[MINE] Profiles** `run` and `build` as the only difference (section 3).
2. **[OPEN] The gallery follows the same spec** (your decision of 2026-11-13). How: `recipe_format_gallery_options_2026-11-13.md`, decisions D1 to D7, each with a recommendation.
3. **[MINE] Schema `category`, `sub_category` and `comment`** kept as direct keys (6.3, 5b). Blueprint's map reads `sub_category` (`blueprint_mapper.py:76`).
4. **[MINE] The T3 container is `steps: {tier3: [...]}` at the plot entry.** It mirrors `steps: {tier1, tier2}` of a join. Name and place are a placeholder; renaming later costs one line in section 6.7 and one rename in the checker.
5. **[OPEN] Schema `output_fields`** are verified by the data check (issue #18) but never applied; the rule text calls them the published contract. Keep as a checked declaration, apply them, or remove? Recommendation: keep as a checked declaration and say so in the rule file.
6. **[OPEN] The two legacy files:** keep (follow the format) or remove? I found no reader; to confirm with a search of the deployment configuration before deleting.
7. **[OPEN] Duplicate forms in the plot specification** (`facet_by` twice; `filters` against the T3 list): left to Blueprint's owner, listed in 6.8.
8. **[OPEN] Package H, the allowed list of formula operations:** derived from all recipes and shown to you before it is enforced.
9. **[MINE] Replacing the column-name aliases** (6.5, 11): the principle is yours (no compatibility default); no ADR decides the aliases either way. It changes `libs/transformer/.../data_wrangler.py`. I treat it as decided unless you object; it is part of #76 with its tests first.
10. **[MINE] The type vocabulary** of four values (6.4).
11. **[MINE] Fragment form:** bare value, wrapper refused (section 5).
12. **[MINE] `original_name` stays allowed on output lists** (it is displayed by Blueprint, `wrangle_studio.py:1310`), so the 20 ST22 contract fragments need no mass edit.
13. **[OPEN] `scan_parquet` and `sink_parquet`** have no `ui_schema`; the rules call them engine-internal, yet 4 transformer fixture steps use them to test them. Options: give them a schema and allow them (the fixtures stay recipes), or test them outside recipes. Recommendation: a schema, allowed, with a description that says they are for tests and advanced use.
14. **[MINE, follows your "do not confound"] Plot-spec metadata.** The taxonomy is not in a pipeline plot (6.8); `description` and `info` go to the plot entry; a note goes in `comment`. This reverses my review recommendation of 2026-11-13 and the text of issue #66. The gallery options (D2) propose exactly what you suggested: one optional key, `taxonomy`, on the plot entry, checked against a dictionary of the gallery terms. Decide there.
15. **[CODE] The `comment` key** exists (BP-COMMENTS-1) and is accepted on every step and layer. What is new and to confirm: `comment` also on `info`, a data schema, a join (5b).
16. **[MINE] `format_version`** (4b): the name, an integer, one version read at a time, the migration tool. Say if you prefer another name (`spec_version`, `recipe_format`) or a different value form.
17. **[OPEN] One place for the rules** (section 0 and gallery options D3): make the specification a data file, so the allowed keys, types, vocabularies (gallery terms included), renames and the version live in one file from which the checker, the filter panels and the docs read. Recommended; it shapes how #76 is built, so it should be decided before the checker starts.

## 14. Tests that come out of this file (written first, they fail on today's code)

- One small invalid recipe per row of section 8: HOME refuses it, Blueprint reports it, the message holds the fix (about 55 tests). A shared helper builds a minimal valid recipe so each test changes one thing.
- One test per row of section 9: the old form is refused and the message names the new one.
- One test per row of section 11: the tolerated form is now refused (mutation check: put the tolerance back and the test fails).
- Every shipped recipe of every kind of section 3 passes `check_recipe` with zero errors and zero advice (the retest scenarios with exactly their one planned fault). Replaces the recipe-folder test, the template test and the hygiene test, which become views of the same check.
- Shape tests (TEST-SHAPES-1): the shipped recipes as fixtures for no join, no key, another key name, no population table, long format.
- Registry oracle (AR2): for every action, the parameters its code reads equal its `ui_schema.params`.
- **Gallery protection:** the committed `gallery_index.json` equals the index rebuilt from the bundles (exists); a bundle written by `GalleryManager.submit_example` (with a `tier3` list) passes the checker; every bundle renders its preview with `generate_previews.py`; every taxonomy value is inside the cheat sheet; the tag strip of each `example_meta.md` equals `info`.
- **Format version:** one test per V01 to V04; every shipped recipe, template, gallery example, written recipe and forked recipe carries `format_version: 1`; `effective_run.yaml` records it.
- **Migration tool:** a format-0 recipe (taken from the git history of the ST22 recipe) becomes a recipe that passes the checker with advices only; running it twice changes nothing; every `#` comment is kept; the list of manual steps is printed.
- **Comments:** a recipe with `#` comments passes untouched; every writer (Blueprint save, bootstrapper, scaffolder, the migration) keeps the comments of a fragment it edits (a before/after text comparison).
- The tests that encode superseded behaviour are listed first (TEST-ADAPT-1): `test_empty_wrangling_is_valid` (`wrangling: []`), `test_tiered_steps_is_valid` and the other tests with inline recipes (no engines), the template and folder tests.

## 15. Errors from a data-science point of view (not format errors)

The format makes a recipe readable and checkable; it does not make it right. Your rule: those errors are fixed, not documented. What is known and what is planned:

| Recipe | Known errors | Status |
|---|---|---|
| `1_test_data_ST22_dummy` | R1 `ST22_Anchor` joins two long tables (617 rows for 42 samples, `virulence_count` wrong for 18); R2 samples with only unknown phenotypes scored 0 (4 of 42); R3 the MLST plot shows 33 of 42 samples without saying so; R4 `virulence_variants` unreadable (16 panels) and coloured by a constant of the resistance table | agreed by you on 2026-11-12; issues #67, #69, #70; task `RECIPE-ST22-FIX-1`; **done before the ST22 descriptions are finalised**, so that they describe the corrected tables (the `REVISE` marks in the draft disappear) |
| the other pipelines (Abromics, `demo_abromics`, `figshare_integration`, `stress_test_master`, `2_` and `3_` ST22) | not reviewed one by one: the Abromics recipe was scanned (its one row-multiplying join, MLST by VirulenceFinder, is one-to-many and expected) but its plots were not looked at | a data-scientist pass per recipe (grain, joins and row counts, missing values, every picture) as part of its migration, #78 |
| templates, retest, gallery, transformer test recipes | not reviewed | gallery: the preview of every example is looked at when `generate_previews.py` is rerun; test recipes: their tests have raw-file oracles |

What the checker can catch of these (structure only): an ignored key (#66), an unknown parameter, a join that multiplies rows (#68, a warning with rows before and after, needs your OK for `libs/transformer`). It cannot decide that a score of 0 for "unknown" is wrong; that stays the data scientist's review.
