# Recipe format specification (draft v0.8, 2026-11-13)

**Written for:** Eve, to read and confirm. After that it is the base of the tests, of the checker (`check_recipe`), of the rule file and of the user documentation.
**Status:** DRAFT. Nothing is built from it yet. It was written by applying the decisions of 2026-11-11/12 and your answers of 2026-11-13 to the code (read at file:line) and to every recipe file in the repository (scans in `tmpAI/recipe_format/`, scratch). The worked example is `1_test_data_ST22_dummy`: section 12 and `recipe_format_st22_draft.yaml`.
**Tags:** **[DECIDED]** you decided it; **[MINE]** my choice while writing, to confirm (section 13 lists them all); **[OPEN]** not decided, with a recommendation; **[CODE]** fixed by what existing code reads or writes (verified, file:line).

**v0.2 (same day, after your review of v0.1):** (1) comments are specified (5b): `#` comments are free and kept, and an optional `comment` key exists; (2) the example variant (gallery) is now defined from what the gallery code reads and writes (6.9). It keeps `name`, the six-axis taxonomy, `data_path`, `wrangling` with `tier3` and its own file names, and it asks for no `label` or `description`; v0.1 refused `tier3` and renamed `name`, which would have broken the gallery; (3) the taxonomy is the gallery's and does not appear in a pipeline recipe (6.8); (4) the column-name aliases are replaced by what the action schemas already declare (6.5, 11); (5) science errors of recipes are fixed, not only described (15).

**v0.3 (same day, after your gallery message):** (1) the comment key is **`comment`** (singular). Blueprint already writes it on steps, layers, groups and plots (BP-COMMENTS-1, ADR-082 Q4; `blueprint_handlers.py:376-378,402-404`, `join_designer.py:153`), and ADR-083 gives every layer a `comment`. My v0.2 had `comments` and a checker that would have refused what Blueprint saves. It is renamed and accepted on every step and every layer (5b, 6.5, 6.8). (2) Section 6.9 (gallery) is **withdrawn**: you want the gallery to follow the same spec, so the v0.2 text that kept its own words is wrong. The options, with pros and cons, are in `recipe_format_gallery_options_2026-11-13.md`; 6.9 is rewritten when you choose.

**v0.8 (same day, after the HOME analysis you pasted):** the form of a container follows **what depends on it** (4c): named and order-free is a dictionary, ordered is a list, and a third category, named **and** ordered (`final_contract`, `analysis_groups`, `plots`), is an ordered dictionary with explicit safeguards. Steps stay lists; a step that needs a name carries an optional `id` inside its list item (4d). I had drafted "steps as a dictionary" first and withdrew it; that draft was swept into another session's commit (`c8c916dc`) and is replaced here. Checked by running: reversing the keys of `final_contract` changes the column order of the stored T1 but **not** of the stored T2 (issue #86), so order in that dictionary is meaning and the cache key ignores it.

**Also in v0.8, from your message "check how each operation for the data and plot is registered":** section 6.10. The registries are the source of what a step or a layer may contain, and they have gaps that the checker would turn into false errors or silent passes (nine parameters whose declared type hides a list or a dictionary; aliases read by the code but not declared; two actions without a schema; all 191 components open to extra parameters).

**v0.7 (same day, after your message on dictionaries, identical keys and the string type):** (1) a wrong container form is refused with a message that shows the **corrected text**, in the app and in the tests; this is added to the HOME plan and the tasks so it is not missed (4c). (2) "Identical keys": a key must be unique inside one mapping, so the same slug in every table's own `input_fields` is correct; the real hazards are a repeated key inside one mapping (T10) and a column name present in both tables of a join, which the engine renames silently to `..._right` (`QC_Reads_Anchor` has `total_reads_right` today): new check J08. (3) The type vocabulary: the record gives only "deprecated alias" as the reason `string` was removed; four lists disagree and the ingestor does not cast `utf8`; to be read from one place (decided), content to decide (6.4, point 10).

**v0.6 (same day, after your note on dictionaries and reuse):** (1) you remembered correctly: **ADR-041 (ENFORCED 2026-04-20)** already decides that keyed definitions are dictionaries, ordered logic is a list and fragments are flat. v0.1 to v0.5 never stated the form of each container; section 4c does, with what the repository really contains (17 list-form containers, 33 wrapped fragments, and 3 contracts that the engine silently skips). (2) Duplicate keys are a gap: PyYAML keeps the last silently, so the loader must detect them (T10). (3) Section 0b gains the candidates that may move to `utils` (your note; nothing moved). The Dockerfile is not ready and nothing is deployed: it stays a later task.

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

**Things that may move to `utils` (your note; nothing is moved, there is no overview yet).** `utils` is where a primitive goes when two libraries need it (`rules_test_lab.md` 2c), so this is expected as the picture clears. Candidates I met while reading, with evidence:

1. **The field-type vocabulary** lives in three places: `MetadataValidator.DTYPE_MAP` (`transformer`, `metadata_validator.py:21-37`), the cast in the ingestor (`ingestor.py:162-170`) and the upload path of the app (`data_import_handlers.py:273`). **[DECIDED 2026-11-13: unify, read in one place.]** One list in the specification file, read by all.
2. **The plot-spec key sets** `_CANONICAL_SPEC_KEYS` and `_VALID_PLOT_DEFAULTS_KEYS` (`viz_factory/plot_config_resolver.py:64-74`) are facts about the recipe format. They belong in the specification file; `viz_factory` reads them from `utils`.
3. **Reading a step container** is written four times: `DataWrangler._resolve_tier` (`transformer`), `tier2_steps` (`app/modules/cache_keys.py:90`), `_step_blocks` (the validator) and inline in the orchestrator. One helper in `utils`; the recipe graph (ADR-099 16(d)) absorbs it.
4. **The shape of a `ui_schema`** (label, category, context, tags, params with widgets, description, example, wraps) is described by identical docstrings in two registries (`transformer/actions/base.py`, `viz_factory/registry.py`) and read by `blueprint_arch.schema_registry` and `help_registry`. Define the shape once in `utils` (a small type and a check); each library keeps its content.
5. **Two mechanisms for renamed keys:** `utils/legacy_keys.py` (recipe keys) and `app/modules/renamed_keys.py` (launch variables and configuration keys, ADR-091). One helper, two tables (the renamed-keys table of the specification file).
6. **`extract_primary_keys` and the lineage helpers** of `blueprint_arch` go to `utils.recipe_graph` (decided).

What stays where it is: the actions and components themselves, the `@category` selector, anything that needs Polars data or plotnine. A review of the whole of `libs/` for more candidates is task `UTILS-REUSE-REVIEW-1`, for when you want it.

**The container.** The Dockerfile is not ready and nothing is deployed (your note): the packaging condition above matters when `DOCKER-RELEASE-1` is done, not before.

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

## 4c. The form of every container (ADR-041)

**What exists.** ADR-041, ENFORCED on 2026-04-20: **keyed definitions are a dictionary, ordered logic is a list, fragments are flat.** Field definitions are a Rich Dictionary (`slug: {props}`, slugs unique); `tier1` and `tier2` are a sequential list of action mappings; an included fragment holds the value only, with no repeated anchoring key. `rules_data_engine.md` section 4 repeats it for fields. "Keyed or ordered?" is the question that decides every container below, so none is left to guess.

**The rule: the form follows what depends on it** `[DECIDED 2026-11-13, after the HOME analysis]`. ADR-041 gives the two clear cases; the third is a container that is both named and ordered.

| Category | Form | What depends on it | Containers |
|---|---|---|---|
| 1. Named; the order means nothing for the data | **dictionary** | lookup by name; names are unique | `data_schemas`, `additional_datasets_schemas`, `joins`, `input_fields`, `output_fields`, `source`, `mapping`, `params`, `plot_defaults`, `info`, `entity`, `taxonomy`, `spec` |
| 2. Ordered; the items need no name | **list** | the order of operations, drawing or joining; YAML guarantees the order of a list | step lists (`tier1`, `tier2`, `tier3`), `ingredients` (the first is the base), `layers`, a `multi` column-selector parameter |
| 3. Named, and the order is meaning | **ordered dictionary**: the order of the keys is documented as meaningful | `final_contract`: the column order of the table; `analysis_groups`: the tab order; `plots` of a group: the sub-tab order | those three |

**What is verified about category 3** (2026-11-13). The table's columns follow the keys of `final_contract` (`orchestrator.py:59-66`). PyYAML keeps the order on load and sorts on dump by default. Five dump sites in non-test code sort today: `exporter.py:56,86` (they write recipe files; test-only code) and `wrangle_studio.py:1848,1864` and `blueprint_handlers.py:861` (they display YAML and would show the wrong order). `canonical_hash` sorts keys (`cache_keys.py:53-55`; `hashing.py:18`). **A defect found by running it** (`tmpAI/recipe_format/contract_order_test.py`): reversing the keys of `final_contract` changes the column order of the stored T1 (the projection is re-applied at every read, `orchestrator.py:142,302`) but **not** of the stored T2 (returned as stored when its key matches), because the sorted hash cannot see the order. Issue #86.

**Safeguards required for category 3.** (a) The loader keeps the file order and refuses a repeated key (T10). (b) Every writer passes `sort_keys=False`, guarded by a test that scans every `yaml.dump` and `safe_dump` of non-test code. (c) A key (hash) that depends on an order is made from the ordered items, never from a sorted dictionary: `final_contract` enters the Tier 1 material as an ordered list of its keys. The tab order is downstream only and enters no data key.

**What does not depend on order (checked).** `input_fields` and `output_fields` of a schema: the ingestor renames and casts but never selects by them, and the schema `output_fields` are not applied (point 5 of section 13); if they are ever applied they move to category 3. `joins` and `data_schemas`: the one place that read the order of `joins` is the first-join fallback, which is removed (section 11). `mapping`, `params`, `info`. The lines of `info` and the fields shown in Blueprint follow the file (presentation only; the writers' `sort_keys=False` is enough).

The same, container by container:


| Container | Form | Why | Refused |
|---|---|---|---|
| `data_schemas`, `additional_datasets_schemas`, `joins`, `input_fields`, `output_fields`, `source`, `mapping`, `plot_defaults`, `info`, `entity`, `taxonomy` | **dictionary** (category 1) | each item has a name, unique, found by key; the order means nothing for the data | a list (also a list of names, or of one-key dictionaries) |
| `final_contract`, `analysis_groups`, `plots` of a group | **ordered dictionary** (category 3) | named, and the order of the keys is meaning: the column order of the table, the tab order, the sub-tab order | a list (also a list of names, or of one-key dictionaries) |
| a field entry | dictionary `{type, label, ...}` or `{}` | `{}` means "as in the input" | a bare string (`sample_id: categorical`, the deprecated shorthand; none is left in the repository) |
| `wrangling` of a schema, `steps` of a join | dictionary with `tier1` (list) and optional `tier2` (list) | the two tiers are named | a flat list, `[]` |
| `tier1`, `tier2`, `tier3` | **list** of step mappings, each with an optional `id` and `comment` (4d) | the order of operations is the logic (category 2) | a dictionary |
| `ingredients` | **list** of `{dataset_id: ...}` | the first one is the base of the join | a dictionary, bare ids |
| `layers` | **list** of `{name, params, comment}` | layers are drawn in order | a dictionary |
| a column-selector parameter that the action's schema declares `multi` | **list** of names | the schema says it takes several | a single value `[MINE]` (2 steps in 1 file today) |
| an included fragment | the value itself | ADR-041 point 3 | a wrapper key that repeats the include key |

**What the repository contains** (scan `tmpAI/recipe_format/container_forms.py`, all kinds of recipe file, verified):

- all **307 input and 162 output field entries are dictionaries**: the deprecated string shorthand is gone;
- **17 containers are in list form.** 7 are empty `[]` written where `{}` or `{tier1: []}` belongs. 10 have content: **3 `final_contract` lists** (`demo_abromics` a list of 5 one-key dictionaries; `universal_template` and the fixture `relational_audit` lists of names), **1 `output_fields` list of names** (`complex_template`), 1 flat `wrangling` (the legacy VIGAS file), and **5 flat `steps` in join fixtures** (the main engine refuses a non-empty flat list);
- **the engine skips a list-form `final_contract` silently** (`orchestrator.py:59-62`), so the contracts of `demo_abromics`, `universal_template` and `relational_audit` are **not applied today**. Converting `demo_abromics` to a dictionary makes it an exclusive whitelist of 5 columns: its plots must be checked at migration (#78);
- **33 fragments carry the wrapper key** that ADR-041 point 3 prohibits (18 `input_fields`, 4 `final_contract`, 4 `spec`, 3 `steps`, 2 `output_fields`, 2 `wrangling`); the loader removes it silently, which is the compatibility default of P2;
- **two texts contradict ADR-041**: `rules_data_analysis_recipe_structure.md` section 8 ("the included plot file must contain a single `spec:` root key") and `data_analysis_recipe_data_contract_rules.md` 4.3 (types `categorical | numeric | string | boolean | date`, where `string` was removed on 2026-05-22). Both go in the documentation sweep (#79, rule file with your double confirmation);
- **slugs must be unique (ADR-041), but nothing checks it:** PyYAML keeps the last of two identical keys without a message (verified). The loader therefore needs a duplicate-key detection (T10).

**The message carries the correction** `[DECIDED 2026-11-13]`. A recipe must be a dictionary where ADR-041 says so, and the program says what to write instead, in the app and in the tests. Each container-form check generates the corrected text from what it found:

| Found | The message shows (generated) |
|---|---|
| `final_contract: [sample_id, value_col]` | `final_contract` is a dictionary of columns. Write: `final_contract: {sample_id: {}, value_col: {}}` |
| `final_contract: [{sample_id: {type: categorical}}, {...}]` (a list of one-key dictionaries) | the same dictionaries merged: `final_contract: {sample_id: {type: categorical}, ...}` |
| `output_fields: []` | `output_fields: {}` |
| `steps: [{action: join, ...}]` (a flat list) | `steps: {tier1: [{action: join, ...}]}` |
| a wrapper line `input_fields:` inside the included file | remove the line `input_fields:` and its indentation; the file holds the fields themselves |
| `sample_id: categorical` | `sample_id: {type: categorical}` |
| a repeated key | names the key and both lines; remove or rename one |

It shows in HOME's load gate (the reason of the rejection), in Blueprint's Validate, in the import screen and in the scripts, because they all call the same adapter (0b). Each check has a test that asserts the message **contains the corrected text** (section 14), so the suggestion cannot go stale. The migration tool applies the same corrections mechanically (4b).

**Dictionaries in the file, lists made by the code.** The file keeps the dictionary; the code makes the list it needs (`list(final_contract)`, the keys of `input_fields`). No recipe writes a list of names.

**Identical keys** `[verified]`. A key must be unique **inside one mapping** (ADR-041: slugs unique in their context). The same slug in different mappings is normal and correct: `sample_id` is in the `input_fields` of every table (66 field dictionaries in the repository, each its own mapping) and is a value in every row of a long table. Three things are different, and they are the real hazards:

1. **A repeated key inside one mapping.** PyYAML keeps the last silently (T10).
2. **A column name present in both tables of a join that is not a join key.** The engine calls `lf.join(...)` without a suffix (`joins.py:56-58`), so Polars renames the second column to `name_right` without a message. `QC_Reads_Anchor` has `total_reads_right` today (ST22 baseline). The join keys themselves (`sample_id` in every table) are the key family and are fine. New check **J08** (advice, suggestion: rename or drop one of the two before the join). It needs the recipe graph (columns per node), so it comes with `RECIPE-GRAPH-UTILS-1`.
3. **Steps.** A T1 repeats the same action (three `join` steps in `QC_Reads_Anchor`), so ordered logic cannot be keyed by the action name. It stays a list (ADR-041 point 2), and a step that needs a name carries an `id` inside its list item (4d).

## 4d. Step ids: an optional `id` inside the list item `[DECIDED direction: Eve 2026-11-13 after the HOME analysis; details to confirm]`

**What.** Steps stay a list. A step is a mapping with `action`, its parameters, and two optional keys: `id` (text) and `comment` (5b).

```yaml
tier1:
  - id: join_quast               # optional; unique in this list when present
    action: join
    right_ingredient: Quast
    'on': [sample_id]
    comment: reads quality and assembly quality side by side
  - {action: join, right_ingredient: Bracken, 'on': [sample_id]}     # no id: fine
```

**Why an id, and why not the action name.** A table repeats actions: in 11 of the 74 non-empty step lists of the repository the same action occurs more than once (`QC_Reads_Anchor` has three `join` steps); there are 148 steps in those lists, at least. The id is needed for the origin marker of audit steps, for removing an audit step, for the node popup and for error messages. The audit only adds steps and removes its own (decided), so the author's steps need no id; an author may give one to refer to a step. No action has a parameter named `id` (checked), so there is no clash.

**Rules.**
1. `id` is text and unique inside its list: check ST08 (E; the message names both positions).
2. A step that **the app inserts always has an id**: `audit_` followed by a unique suffix. That is the **origin marker** that the HOME draft waits for (6.5, open). The invariant "the copy minus its marked steps equals the original" compares ids.
3. `id` and `comment` are **not part of the hash** (`canonical_steps` removes them): renaming or commenting a step must not rebuild a table. The order is part of it.
4. The list is the order, so nothing depends on the order of a mapping (YAML guarantees the order of a list).

**What it avoids.** The three dangers recorded in the HOME draft (point 7), all verified: a repeated key is silent in YAML; both hashes sort keys; five dump sites sort keys. They remain real for category 3 (4c), where they are guarded.

| Option | Pros | Cons |
|---|---|---|
| A. Steps as an ordered dictionary of ids | an id by construction | the order depends on the file (the hash on a list, every writer, the loader: all needed and verified); every step needs a name; 6 writers change and Blueprint's form needs a name field; all 148+ steps migrate; ADR-041 point 2 superseded |
| **B. A list, `id` optional inside the item** **[direction]** | ids where wanted; the order is guaranteed by YAML; a duplicate cannot drop a step silently; the hash keeps the order; no migration of steps | the id is a key inside the item, not the key of the container (a check enforces uniqueness) |
| C. A list without ids | nothing changes | no address but position |

ADR-041 point 2 is unchanged and gains the `id` key. Only code that inserts steps writes ids (the audit compiler). **To confirm:** `id` optional (recommended) or required on every step; the `audit_` prefix.

## 5. Fragments (`!include`)

- `key: !include 'path/to/file.yaml'` puts the **content of the file exactly where the key is**. The path is relative to the folder of the recipe file `[MINE: verified in config_loader.py:55, nested includes use the same folder]`.
- **The fragment holds the value itself, with no wrapper key** `[DECIDED, ADR-041 point 3, ENFORCED 2026-04-20]`. A file whose only top-level key repeats the key it is included under (`input_fields:` inside the file included as `input_fields:`) is refused with "remove the wrapper line". Today the loader removes the wrapper silently (`config_loader.py:77-97`): a compatibility default that ADR-041 itself prohibits. The ST22 recipe has 68 includes: 56 are bare and 12 are wrapped; over all recipes 33 are wrapped (4c).
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
**Type vocabulary: to be read from one place `[DECIDED to unify; content OPEN, point 10]`.** Four lists disagree today. (1) `rules_data_analysis_recipe_structure.md` section 9 lists `categorical` and `utf8` only. (2) The user docs (`Standards_yaml.qmd`) list `categorical`, `numeric`, `date`, `boolean`. (3) The ingestor casts `numeric` to Float64, `categorical` or `string` to String, `date` to Date, and **nothing else** (`ingestor.py:162-170`). (4) `MetadataValidator.DTYPE_MAP` accepts 14 names (`metadata_validator.py:21-37`). **Verified by running the ingestor** on a column of digits: `categorical` and `string` give String; `utf8`, `boolean` and `i64` are **not cast** (the digits stay Int64), so `utf8` does not force text; and `string` is accepted by the ingestor but refused by `enforce_schema`. 4 fixtures declare `i64`, which nothing handles.

**Why `string` was removed.** The record says only "deprecated aliases" (`LEGACY-TYPE-ALIASES-1`, the Phase 34 legacy-removal sprint, 2026-05-22: `tasks_archive_2026-05-22.md:113`, commit `125963cf`; the policy is "one authoritative way to do each thing", `rules_legacy_management.md`). No ADR gives a deeper reason. What the files show: all 6 recipes that used `string` were migrated to `categorical`, so in practice it meant "a category"; and the rule wants the author to say whether a text column is a **group** (`categorical`: identifiers, labels, repeating values, drawn as discrete groups, joined as text; `sample_id` must be one, so that digits become text and joins match) or **free text** (`utf8`). The reason is therefore my inference, not a recorded decision.

**Options for the content** (the vocabulary is one list in the specification file, each entry with a one-line meaning that the error message quotes):

| Option | Pros | Cons |
|---|---|---|
| **A. Keep four** (`categorical`, `utf8`, `numeric`, `date`); fix the ingestor so `utf8` is cast to text; the message for `string` quotes the two meanings **[recommended]** | the author states the intent; no new names; smallest change | `utf8` is the name of an encoding, not a word a scientist chooses |
| B. Rename `utf8` to `text` | a plain word; the format changes once anyway (4b) | one more rename; `utf8` is used in 1 recipe |
| C. Restore `string` for free text and drop `utf8` | a familiar word | the old doubt returns: is a `string` column a category? |
| D. Add `boolean` | the docs list it | no recipe uses it, the ingestor ignores it; add it only with a real cast and a real use |


### 6.5 Steps and tiers

- A **step list** is `{tier1: [...], tier2: [...]}`. It appears as `wrangling` (data schema), `steps` (join) and, at the plot entry, `steps: {tier3: [...]}` (6.7). All three are written the same way; an empty list means "equal to the previous node". `tier1` is required except at the plot entry; an unknown tier name is an error. `[DECIDED, 5a-15]`
- A **step** is a mapping with `action` (a registered name), exactly the parameters in that action's `ui_schema.params`, and optionally `id` (4d) and `comment` (5b); neither is a parameter and neither is passed to the action (`libs/transformer/.../actions/base.py`). A missing required parameter, an unknown parameter and an unknown action are errors, with a did-you-mean by spelling. **The registry is the one source of the parameter contract** (W1): a test checks that the keys each action's code reads equal its schema. Today 65 of 67 actions have a schema. `scan_parquet` and `sink_parquet` have none: the rules call them engine-internal, but 4 fixture steps use them to test the actions themselves `[OPEN 13.13]`.
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

### 6.10 How operations are registered, and what the checker can read from it (verified 2026-11-13)

**The mechanism.** An operation exists because a Python function carries a decorator, run when the library is imported. `@register_action("name", ui_schema={...})` (`transformer/actions/base.py:22`) fills `AVAILABLE_WRANGLING_ACTIONS` (name to function) and, when a schema is given, `ACTION_SCHEMAS`. `@register_plot_component("name", ui_schema={...})` (`viz_factory/registry.py:21`) fills `PLOT_COMPONENTS` and `COMPONENT_SCHEMAS`. A name registered twice overwrites the first with a log line. Today: **67 actions (65 with a schema), 191 components (all with a schema)**. The schema holds `label`, `category`, `context` (where the operation may appear: t1, t2, assembly, plot), `tags`, `params`, `description`, `yaml_example`, `wraps` (the Polars or plotnine function it wraps; 39 of 65 actions, all components).

**What the checker reads.** Name known or not (ST02, PS04), parameters declared or not (ST03), required present (ST04), `multi` (ST07), `context` against the tier (a `join` in tier 2: ST05 is one case of it). The core never imports `transformer` or `viz_factory` (0b): each caller exports its registry as plain data (name to `{params: {name: {widget, multi, required, options}}, extra_params_allowed, context}`) and passes it in. One function in each library produces that data from the two dictionaries above.

**What the registries do not say (checked by running `registry_survey.py`, `registry_conformance.py`, `registry_examples.py` in `tmpAI/recipe_format/`):**

| # | Gap | Evidence | Consequence for the checker | Resolution |
|---|---|---|---|---|
| R1 | No widget for a dictionary or a list of values. Nine parameters are declared `string` or `multi` enum while their own `yaml_example` writes a dictionary or a list: `rename.mapping`, `rename_columns.mapping` (dictionary old to new); `recode_values.rules` (list of mappings); `replace_values.to_replace`, `is_in.values`, `not_in.values`, `split_column.new_columns`, `split_column_to_parts.new_columns` (lists); `date_extract.parts` (a `multi` enum) | the 8 widgets in use: `column_selector`, `string`, `enum`, `column_or_literal`, `number`, `dtype_picker`, `expression`, `bool` | a shape check would call the actions' own examples wrong; Blueprint shows a text box and the user types YAML into it | add widgets `list` and `mapping` (and `rules` for `recode_values`) to the vocabulary of the two registries; correct the nine declarations; the checker tests the shape. A repeated key inside a `mapping` is T10 at any depth: `{a: x, a: y}` silently drops a rename |
| R2 | The code reads keys the schema does not declare: `rename.target_column`, `split_column.source`, `.separator`, `.target_column` (`cleaning/core.py:126`; `reshaping/core.py:202,205`). | `registry_conformance.py`; section 11 | these are the aliases of 6.5, hidden in the function body, outside the one place (`data_wrangler.py:132-147`) that section 11 already lists | remove the reads with the aliases (package C); a test (AR2) compares the keys a function reads with its schema |
| R3 | Engine-internal keys travel inside the step: `__right_df__` (`data_assembler.py:207`, read at `joins.py:39`) and `__metadata__` (`data_wrangler.py:196`, read at `cleaning/core.py:320,349`) | grep | a recipe can carry them: they would reach the function | check ST09: a key that starts and ends with a double underscore is reserved and refused in a recipe |
| R4 | `scan_parquet` and `sink_parquet` have no schema (engine-internal; 4 fixture steps use them) | `registry_survey.py` | an unknown-parameter check cannot run on them | section 13, point 13 |
| R5 | All 191 components carry `allow_extra_params: true` and their schemas list only a part of the arguments (802 parameters for 191 components); plotnine itself refuses an unknown argument (`PlotnineError`, verified) and accepts both `color` and `colour` | `registry_survey.py`; 8 layer parameters of the shipped recipes are outside the schemas (`color` x8, `outlier_alpha`, `size`) | "unknown parameter fails" cannot rest on the schema alone: it would reject valid plotnine arguments | PS04 reads the schema **plus** the arguments of the wrapped class (signature and aesthetics, resolved from `wraps` by `viz_factory`, as the help panel does) and passes the result to the core as the component's allowed names; an unknown name is an error with a did-you-mean. Open: complete the schemas instead (191 components), later |
| R6 | A step with a `column_selector` parameter is resolved by the wrangler (the six spellings, `@category` names); the schema says which parameters are selectors | `data_wrangler.py:132-147` | ST03 and the selector resolution must read the same declaration | one reading of the schema: the parameters with widget `column_selector` |

**Which form each registered parameter takes** (the rule of 4c, applied to the values inside a step): a **list** where order or repetition is meaning or a set is meant (`columns`, `values`, `new_columns`, `rules`, `on` with several keys); a **dictionary** where each entry is a name with a value (`mapping`: old name to new name; `plot_defaults`; `mapping` of a plot); a **scalar** otherwise. The registry must say which; today it says "string" for all three, which is R1.

**Self-consistency tests** (they run on the registries, no recipe needed): AR2 (the keys a function reads equal its schema), AR3 (every `yaml_example` passes the checker: shape, names, required; fails today on the nine of R1), AR4 (every `wraps` resolves to an importable function), AR5 (every component name used by `yaml_example` or by a shipped recipe is registered), AR6 (no registered name is overwritten at import).

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

Severity: **E** error (HOME refuses; Blueprint reports and does not block building), **A** advice (shown, never blocks). IDs are permanent; messages are generated from this table with the replacement of section 9 and, for a wrong container form, the corrected text (4c).

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
| T10 | E | the same key twice in one mapping (PyYAML keeps the last silently); found by the loader, ADR-041 "slugs unique" | remove one |
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
| FD06 | E | a field entry is a bare string (`sample_id: categorical`) | `{type: categorical}` |
| ST01 | E | step without `action` (shorthand), or not a mapping | |
| ST02 | E | unknown action | did-you-mean |
| ST03 | E | parameter not in the action's schema (`id` and `comment` are allowed on every step) | did-you-mean; `column`, `source`, `target_column`, `source_column` -> `columns` where that is the name |
| ST04 | E | required parameter missing | |
| ST05 | E | `join` or `join_filter` in tier2 | exists today |
| ST06 | E | formula uses an operation outside the allowed list | package H |
| ST07 | E | a parameter declared `multi` has a single value | write a list |
| ST08 | E | two steps of one list have the same `id`, or an `id` is not text | rename one; the message names both positions (4d) |
| ST09 | E | a reserved engine key (`__right_df__`, `__metadata__`, any `__name__`) in a step | remove it; the engine sets it (6.10, R3) |
| ST10 | E | the value of a parameter has the wrong shape for its declared widget (a list where a scalar is declared, a dictionary where a list is, a repeated key in a `mapping`) | the message shows the declared form and the corrected text (6.10, R1) |
| J01 | E | unknown key in a join (`info`, `output_fields`, ...) | replacement |
| J02 | E | join without `label` | |
| J03 | A | join without `description` | |
| J04 | E | `ingredients` missing, empty, not `{dataset_id}` items, unknown id, repeated id | |
| J05 | E | `right_ingredient` not in the join's ingredients; `on` and `left_on` both or neither | |
| J06 | E | `final_contract` not a mapping, or names a column the collection lacks | |
| J07 | E | a join's `steps` is a flat list or `[]`, or has no `tier1` | `{tier1: [...]}` |
| J08 | A | a column name in both ingredients of a join, not a join key: the engine renames the second `name_right` silently (needs the recipe graph) | rename or drop one before the join |
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
| `config_loader.py:77-97` | fragment wrapper key removed silently (ADR-041 point 3 prohibits it) | C (F01) |
| `config_loader.py` (PyYAML `SafeLoader`) | a repeated key in a mapping keeps the last silently | C (T10): a loader that raises on a duplicate key |
| `config_loader.py:141-211` | judges content: structure, renamed keys, source; only part of the rules | C (moves to `check_recipe`) |
| `data_wrangler.py:60-61` | an empty `wrangling` of any shape means "no steps" | C (S06) |
| `data_wrangler.py:132-147` | six spellings of the column selector, guessed in a fixed order and written back into the step | C (ST03). The presence check and `@category` stay but read the parameters the action's schema declares as column selectors. Exactly 14 steps in 10 recipe files rely on a wrong spelling today (probe). No ADR decided the aliases (ADR-034 is the diagnostic message); covered by your "no compatibility default" |
| `cleaning/core.py:126`, `reshaping/core.py:202,205` | `rename` reads `target_column`; `split_column` reads `source`, `target_column`, `separator` although its schema declares `columns` and `delimiter` | C (ST03; 6.10 R2). Used today: `split_column` `source` x3, `separator` x1, `column` x1, `new_names` x1; `keep_columns` `target_column` x1; `split_and_explode` `target_column` x3, `column` x2 (probe) |
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
| 16 | Your note on dictionaries: ADR-041 decides the form of fields (dictionary), tiers (list) and fragments (flat); the repository has 17 list-form containers, 33 wrapped fragments and 3 contracts the engine skips silently (`demo_abromics`, `universal_template`, `relational_audit`) | 4c; scan `container_forms.py`; `orchestrator.py:59-62` | 4c states the form of every container; checks S08, J06, J07, FD06, F01, T10; the `demo_abromics` contract is checked at migration |
| 17 | A column name in both tables of a join, not a join key, is renamed `..._right` silently | `joins.py:56-58`; ST22 baseline: `QC_Reads_Anchor.total_reads_right` | check J08 (with the recipe graph); `QC_Reads_Anchor` looked at by the data-scientist pass at migration |
| 18 | Where dictionary order is meaning: the column order of a table (`final_contract`) and the tab order (`analysis_groups`, `plots`). Reversing the keys of `final_contract` changes the stored T1 but not the stored T2; the HOME session's three dangers (silent duplicates, sorted hashes, sorting writers) are verified | `tmpAI/recipe_format/contract_order_test.py`; `orchestrator.py:59-66,142,302`; `cache_keys.py:53-55`; `hashing.py:18`; 5 dump sites | 4c category 3 with safeguards; 4d step ids; issues #85, #86 |
| 19 | The registries cannot describe a list or a dictionary parameter (9 declared `string` or `multi` enum while their example is a list or a dictionary), hide aliases in function bodies (`rename`, `split_column`), have 2 actions without a schema, and leave all 191 components open to extra parameters | `registry_survey.py`, `registry_conformance.py`, `registry_examples.py`, `step_params_probe.py`, `layer_probe.py`; `base.py:22`; `registry.py:21` | 6.10: widgets `list` and `mapping`, checks ST09 and ST10, tests AR2 to AR6; section 11 rows; issue #87 |

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
10. **[DECIDED to unify, OPEN content] The type vocabulary** (6.4): one list in the specification file, read by the ingestor, the validators and the upload path. The content is yours: options A to D in 6.4 (recommended A).
11. **[DECIDED, ADR-041] Fragment form:** bare value, wrapper refused (section 5); nothing to decide, only to apply.
12. **[MINE] `original_name` stays allowed on output lists** (it is displayed by Blueprint, `wrangle_studio.py:1310`), so the 20 ST22 contract fragments need no mass edit.
13. **[OPEN] `scan_parquet` and `sink_parquet`** have no `ui_schema`; the rules call them engine-internal, yet 4 transformer fixture steps use them to test them. Options: give them a schema and allow them (the fixtures stay recipes), or test them outside recipes. Recommendation: a schema, allowed, with a description that says they are for tests and advanced use.
14. **[MINE, follows your "do not confound"] Plot-spec metadata.** The taxonomy is not in a pipeline plot (6.8); `description` and `info` go to the plot entry; a note goes in `comment`. This reverses my review recommendation of 2026-11-13 and the text of issue #66. The gallery options (D2) propose exactly what you suggested: one optional key, `taxonomy`, on the plot entry, checked against a dictionary of the gallery terms. Decide there.
15. **[CODE] The `comment` key** exists (BP-COMMENTS-1) and is accepted on every step and layer. What is new and to confirm: `comment` also on `info`, a data schema, a join (5b).
16. **[MINE] `format_version`** (4b): the name, an integer, one version read at a time, the migration tool. Say if you prefer another name (`spec_version`, `recipe_format`) or a different value form.
17. **[OPEN] One place for the rules** (section 0 and gallery options D3): make the specification a data file, so the allowed keys, types, vocabularies (gallery terms included), renames and the version live in one file from which the checker, the filter panels and the docs read. Recommended; it shapes how #76 is built, so it should be decided before the checker starts.
18. **[DECIDED direction, details OPEN] The form follows what depends on it** (4c, 4d; you decided it after the HOME analysis): steps stay lists with an optional `id`; named things are dictionaries; `final_contract`, `analysis_groups` and `plots` are ordered dictionaries with safeguards. To confirm: `id` optional (recommended) or required; the `audit_` prefix; `final_contract` key order = the table's column order (recommended: yes, documented and tested; fixes #86); tab order = key order of `analysis_groups` and `plots` (recommended: yes).
19. **[OPEN] The level of J08** (the silent `_right` suffix): advice (recommended: it changes a name, not a number, unless a plot uses the suffixed column) or error.
20. **[OPEN, follows your message on registration] The parameter vocabulary of the registries** (6.10 R1): add the widgets `list` and `mapping` (and `rules`) and correct the nine declarations; and for plot layers either (a) keep the schemas as they are and let the checker read the wrapped plotnine arguments (recommended now: it needs no edit of 191 schemas), or (b) complete the 191 schemas so they list every argument (later, with the documentation sprint). The change touches both registries (`libs/transformer`, `libs/viz_factory`): I will not edit them before you confirm.

## 14. Tests that come out of this file (written first, they fail on today's code)

- One small invalid recipe per row of section 8: HOME refuses it, Blueprint reports it, the message holds the fix (about 55 tests). A shared helper builds a minimal valid recipe so each test changes one thing.
- One test per row of section 9: the old form is refused and the message names the new one.
- One test per row of section 11: the tolerated form is now refused (mutation check: put the tolerance back and the test fails).
- Every shipped recipe of every kind of section 3 passes `check_recipe` with zero errors and zero advice (the retest scenarios with exactly their one planned fault). Replaces the recipe-folder test, the template test and the hygiene test, which become views of the same check.
- Shape tests (TEST-SHAPES-1): the shipped recipes as fixtures for no join, no key, another key name, no population table, long format.
- Registry self-consistency (6.10): AR2 for every action the parameters its code reads equal its `ui_schema.params`; AR3 every `yaml_example` passes the checker (fails on the nine parameters of R1); AR4 every `wraps` resolves; AR5 every component named by an example or a shipped recipe is registered; AR6 no registered name is overwritten at import; a layer parameter that plotnine accepts (`color`, `colour`) passes and one it refuses (`foo`) fails.
- **Gallery protection:** the committed `gallery_index.json` equals the index rebuilt from the bundles (exists); a bundle written by `GalleryManager.submit_example` (with a `tier3` list) passes the checker; every bundle renders its preview with `generate_previews.py`; every taxonomy value is inside the cheat sheet; the tag strip of each `example_meta.md` equals `info`.
- **Container forms (4c):** one test per refused form (a list where a dictionary belongs and the reverse, a bare string field, a flat `steps`, a wrapper key); a duplicate key is found by the loader; a `final_contract` list is refused instead of skipped; after migration the `demo_abromics` plots still render with their 5-column contract.
- **Order and ids (4c, 4d):** the key order of `final_contract` is the column order after load, run and write, in T1 **and** T2 (a round trip; fails today, #86); groups and plots keep their tab order; the hash changes when the order of steps changes and does not change when an `id` or a `comment` changes; a repeated or non-text `id` is refused; an app-inserted step has an `audit_` id; the copy minus the marked steps equals the original; a scan test requires `sort_keys=False` for every `yaml.dump` and `safe_dump` of non-test code.
- **Messages with the correction (4c):** for each container-form check the message contains the generated corrected text, compared with an expected string; HOME's gate, Blueprint's Validate and the import screen show the same message (one adapter).
- **Types (6.4):** a table of declared type to resulting dtype, run through the ingestor for every type of the vocabulary (including digits declared as text); each refused name gives a message that quotes the meanings; no list of types exists in code (a grep test).
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
