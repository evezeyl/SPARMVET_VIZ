# Recipe format specification (format version 1)

**Written for:** Eve, to review. Once confirmed it is the base of the checker, the tests, the rule file and the user documentation.
**Status:** DRAFT. Nothing is built from it yet. It states how recipes will work and how each point was decided. How it was reached is in the issues (#73 and its children), in `.claude/design/outdated/` (the earlier drafts, with the findings of applying the format to the ST22 recipe) and in git.
**Tags.** **DECIDED**: Eve decided it (date) or an ADR does. **PROPOSED**: my choice while writing, to confirm. **OPEN**: not decided, with a recommendation; all open points are listed in section 2.3. **CODE**: fixed by code that exists (verified, file:line).
**Terms.** *Recipe* = a data analysis recipe, a YAML file. *Schema* = a data schema (one input table). *Collection* = a join, or a schema that is plotted directly. *Tier 1/2/3* = the steps that build, reshape and finally audit a table.

## 1. How it works, on one page

- **One format, one checker, one place for the rules.** Every recipe (pipelines, templates, retest scenarios, transformer test recipes, gallery examples, recipes written by the app) is a YAML file in format version 1, checked by the same function, `check_recipe`, in `libs/utils`. HOME's load gate, Blueprint's Validate, the importer, the scripts and the tests all call it through one adapter (section 14).
- **Unknown keys fail. Nothing old is tolerated.** A key that nothing executes or displays does not exist. An old name is refused at once and the message names the new one. No compatibility defaults. A recipe in another format version is refused and the message names the migration tool.
- **A wrong form is refused with the correction.** The message says where, what is wrong, and shows the corrected text, in the app and in the tests.
- **The form of a container follows what depends on it** (section 5): named things are dictionaries, ordered operations are lists, and a few named things whose order is meaning (`final_contract`, `analysis_groups`, `plots`) are ordered dictionaries with safeguards.
- **Operations come from the registries.** A step is a registered action with the parameters its schema declares; a layer is a registered plot component with the arguments its schema or the wrapped plotnine function declares (section 8).
- **A gallery example is a standard recipe** with a required `taxonomy`, checked in a `gallery` profile (section 9).
- **Writing a description is a rule**, not a habit (section 13). Data-science errors are fixed, not documented (section 17).

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
    source: {type: local_tsv, path: assets/test_data/anchor.tsv}
    input_fields:
      sample_id: {type: categorical, is_entity_key: true}
      reads: {type: numeric}
    wrangling:
      tier1:
        - {action: filter_range, columns: reads, min: 1000, comment: too few reads to trust}
      tier2: []
  Quality:
    label: Quality table
    description: >-
      One row per sample (42 rows) ...
    source: {type: local_tsv, path: assets/test_data/quality.tsv}
    input_fields: {sample_id: {type: categorical, is_entity_key: true}}
    wrangling: {tier1: []}
joins:
  Combined:
    label: Combined table
    ingredients: [{dataset_id: Anchor}, {dataset_id: Quality}]
    steps:
      tier1:
        - {action: join, right_ingredient: Quality, 'on': sample_id, how: left}
    final_contract: {sample_id: {}, reads: {}}          # exclusive whitelist; its order is the column order
analysis_groups:
  overview:
    label: Overview
    plots:
      reads_per_sample:
        label: Reads per sample
        description: Number of reads of each sample.
        spec: {target_dataset: Combined, mapping: {x: sample_id, y: reads}, layers: [{name: geom_col}]}
        steps: {tier3: []}                               # audit steps of this plot
```

## 2. What is decided, what is still open

### 2.1 Decided

| # | Decision | Source |
|---|---|---|
| 1 | **Scope:** every recipe, in the app and in the tests (transformer fixtures and recipes inside automatic tests included): everything that describes a read of data or a plot | Eve 2026-11-13 |
| 2 | **Unknown keys fail.** Recipes are checked first (Blueprint), so nothing needs tolerating | Eve 2026-11-13 |
| 3 | **No backward-compatible default.** The old-key table (`legacy_keys.py`) only suggests the replacement in the message. Old names are **refused at once**, not warned first | Eve 2026-11-13; ADR-099 16(a) |
| 4 | `is_primary_key` becomes `is_entity_key` | Eve 2026-11-13 |
| 5 | The **tier-3 container** is in the schema now (audit mode comes soon); its name and place are proposed (O12) | Eve 2026-11-13 |
| 6 | A dataset plotted directly applies its **own tier-2 list** (engine fix, issue #77) | Eve 2026-11-12 |
| 7 | `data_engine` (`python-polars`) and `plot_engine` (`python-plotnine`) are **required** | Eve 2026-11-13 |
| 8 | A **`description`** on every element; where missing it is filled by the rules of section 13 | Eve 2026-11-13 |
| 9 | Comments on recipes must be possible and are specified (section 6.2) | Eve 2026-11-13 |
| 10 | The **gallery** follows the same specification (its examples are recipes), is checked by the same code, keeps its taxonomy and its functions, and has a **required `taxonomy` key**; its allowed terms live in the specification, one place instead of two; the work is planned now and done later (section 9) | Eve 2026-11-13 |
| 11 | Every recipe has a **`spec_version`** that the checker matches against the specification; the gallery has it too | Eve 2026-11-13 (idea from her review with another agent); name decided in row 22 |
| 12 | One **checker in `libs/utils`** for every user of recipes (HOME, Blueprint, importer, gallery, scripts, tests) | ADR-099 16(g); verified against the layer rules (section 14) |
| 13 | **Containers follow ADR-041** (keyed things are dictionaries, ordered logic is a list, fragments are flat). A wrong form is refused with a message that shows the corrected text, in the app and in the tests; this is also in the HOME plan | ADR-041; Eve 2026-11-13 |
| 14 | **The form follows what depends on it** (section 5): steps stay lists, authors write no step name, and the app marks the steps it inserts with an `id` (O5); `final_contract` key order **is** the column order; the tab order **is** the key order of `analysis_groups` and `plots` | Eve 2026-11-13 |
| 15 | The **field-type vocabulary is read in one place**; its content is row 20 | Eve 2026-11-13 |
| 16 | **The registries are fixed** (widgets for lists and dictionaries, corrected declarations), and **plot arguments are checked**: plot instructions are part of the recipe (section 8; issue #87) | Eve 2026-11-13 |
| 17 | Errors of a recipe from a data-science point of view are **fixed**, not documented (section 17) | Eve 2026-11-11/12 |
| 18 | The worked example is `1_test_data_ST22_dummy` (the most advanced, the default of Eve's tests) | Eve 2026-11-13 |
| 20 | **Field types:** `categorical` (default), `utf8`, `numeric`, `date` and `boolean` (Option A plus `boolean`, section 7.4). The ingestor is fixed so that `utf8` is cast to text and `boolean` is cast with a real cast; the message for the removed `string` quotes the two meanings | Eve 2026-11-13 |
| 21 | **Gallery design D1 + D2 + D3** (section 9): an example is a standard recipe in a `gallery` profile; the key is `taxonomy` on the plot entry, required in the gallery, five axes, `geom` derived; the specification is also a data file so the gallery terms live in one place. D4 to D7 are decided when the gallery work starts | Eve 2026-11-13 |
| 22 | **The version key is `spec_version`**, an integer (section 4.1) | Eve 2026-11-13 |
| 23 | **J08 is an error with a guidance message:** a non-key column present in both tables of a join (silently renamed `name_right` by Polars) refuses the recipe; the message names both tables and the column and says how to rename or drop one (section 5.2) | Eve 2026-11-13 |
| 24 | **The two legacy recipes are removed**: `config/data_analysis_recipes/VIGAS-P/` (a recipe and its fragments) and `assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_data_analysis_recipe.yaml`; no code reads them. `Virulence_genes_APEC_input_fields.yaml` in the same folder is **not** legacy: the Abromics pipeline includes it | Eve 2026-11-13 |
| 25 | **The column-name aliases are removed** (`column`, `source`, `source_column`, `target_column` for `columns`, and the other spellings of section 12); display names for plots are a separate matter (#91) | Eve 2026-11-13 |
| 26 | **Plot-spec metadata:** the gallery classification is the `taxonomy` key (gallery), not part of a pipeline plot spec; `description` is on the plot entry; a note goes in `comment` | Eve 2026-11-13 ("we had decided to put that in the gallery taxonomy") |
| 27 | **`comment` is allowed on `info`, a schema and a join** (it already is on steps, layers, groups and plots). The plural `comments` is a typo and is **refused**; the message says `comment` | Eve 2026-11-13 |
| 19 | Notes, not decisions: some library code may move to `libs/utils` when two libraries need it (nothing moved; `UTILS-REUSE-REVIEW-1`); the Dockerfile is not ready and nothing is deployed (`DOCKER-RELEASE-1`) | Eve 2026-11-13 |

### 2.2 Principles (each follows from a decision above)

- **P1 Executed, displayed, or refused.** Every key either is executed by an engine, is displayed, or is refused with the reason. `[DECIDED, 5a-19]`
- **P2 No compatibility defaults.** A wrong recipe is corrected, never tolerated. `[DECIDED, ADR-099 16(a)]`
- **P3 One word for one thing.** `label` is the short name shown to the user; `description` is one or two sentences; steps and tiers are written the same way everywhere. `[DECIDED, 5a-9]`
- **P4 Generic words.** The format and the checker know no field-specific word (entity, attribute, table; not sample, gene). Field words live in recipes and help. `[DECIDED, W7]`
- **P5 An error says where, what and the fix**, and shows the corrected text. `recipe : path : what is wrong. Fix: what to write.` `[PROPOSED, from the message style that exists]`
- **P6 Looking for a problem is separate from running.** The checker reads the recipe and the registries and never needs the data; the data check stays separate. `[DECIDED, O1 of the HOME plan]`

### 2.3 Open: what is still undecided or unclear

The numbers O1 to O18 are kept as references; a decided point leaves the table (O2, O3, O6, O8, O13, O15 and O18 were decided on 2026-11-13: rows 20, 22, 23, 24, 25, 26 and 27 of section 2.1).

| # | Question | Recommendation | Touches |
|---|---|---|---|
| O1 | **Gallery, the later decisions D4 to D7** (section 9): where an example is checked (D4), how previews are made (D5), the tag strip of `example_meta.md` (D6), the data contract of an example (D7); and whether the dead submission code is removed (G6) | D4 `check_recipe` at rebuild, at app start and in the tests; D5 previews by the app's path; D6 tag strip generated from `taxonomy`; D7 generated contract, reviewed | #82 |
| O4 | **`profile`** (not `mode`) for run/build/gallery: the HOME session changed its stage-2 spec to `profile` and keeps "mode" for Exploration/Audit. It also proposes a fourth profile **`audit`** for the audit copy of a recipe (steps with `audit_` ids are accepted only there). **Eve to confirm** | confirm `profile` and the profile `audit` | #76, HOME |
| O5 | **The marker on a step the audit inserts.** HOME's proposal (message M6): `id: audit_<action>_<k>` where `<action>` is 8 hex characters, one per user action (all steps of one action share it, so an undo removes the whole action) and `<k>` is 1, 2, ...; no other key on a step; the origin header (hash of the original's file set, spec version, time) stays outside the recipe, in the audit record, so the copy is a valid recipe. In profile `run` or `build` an `id` on a step is an **error** (authors write none); in profile `audit` an id must match the pattern. Authors never write it (Eve: an `id` that authors do not use would confuse). **Eve to confirm** | accept HOME's proposal | #85, HOME |
| O7 | **Schema `output_fields`.** ADR-013 calls them the *published contract* of a schema (input_fields, wrangling, output_fields) and ADR-014 "a strict `.select()`"; the engine never applies them, the data check only compares them with the columns. Eve: "the intent was control of the recipe". **Measured by an experiment** (scratch, nothing changed in the code): applying them to ST22 leaves 12 of 17 collections identical, 5 lose columns (`QC_Reads_Anchor` 54 to 12, `FastP_with_metadata` 17 to 7, `Bracken_with_metadata` 19 to 6, `ResFinder_with_metadata` 17 to 7, the plot collection `ResFinder` 14 to 4), and **2 collections fail** (`QA_ST_with_NA`, `QA_L50_integer`: a later `keep_columns` needs a column the schema did not declare). So declarations and recipe disagree today and nothing says so. **Options.** **A** keep as a checked declaration (today; the ADR text then says "strict select" while the code does not: ADR-013/014 amended). **B** apply them (what ADR-013/014 say: control; the 5 schemas lose their unlisted columns, 2 declarations are corrected; best done when the checker's column dry run X7 exists). **C** remove them: Blueprint's third column and 23 recipe files change, ADR-013/014 superseded, the published columns then come only from a join's `final_contract` (a schema plotted directly has no whitelist) | **B** if control is the aim (after X7); A is the minimum | section 7.3 |
| O9 | **Duplicate forms in a plot spec** (`facet_by` at the top and inside `mapping`; `filters` in the spec and the tier-3 list) | allowed for now; the plot-engine owner (Blueprint) simplifies | section 7.8 |
| O10 | **Package H, the list of operations a formula may use** (`mutate` expressions, plot function strings) | derived from all recipes and shown to Eve before it is enforced | #80 |
| O11 | **`scan_parquet` and `sink_parquet`** have no schema; 4 transformer fixtures use them | give them a schema, allowed, described as for tests and advanced use | #87 |
| O12 | **The tier-3 container**: `steps: {tier3: [...]}` on the plot entry | keep (it mirrors `steps: {tier1, tier2}` of a join); renaming later is one line | section 7.7 |
| O14 | **Schema `category` and `sub_category`, and the schema-level `info:` block.** Evidence: they were introduced with the ST22 test pipeline on 2026-04-10 (commit `29ec53cf`) and no ADR or document explains them; the documentation puts `category` in the *recipe-level* `info` (`docs/foundations/data_contracts_adr.qmd`: `display_name`, `category`, `tags`, `version`), which HOME displays (free-form, `info_lines`). Readers of a *schema's* `info`: only a fallback node label in Blueprint's map (`blueprint_mapper.py:76`) and a copy into the navigator's registry; HOME does not read them (HOME session, M6). **Options.** **A** drop both. **B** direct keys of the schema. **C** a free-form `info` block on a schema like the recipe's (project, contact, any key), displayed in Blueprint's node details (needs a small display change). The intent must come from Eve | C if schema notes are wanted, else A | section 7.3 |
| O16 | **`original_name`.** Purpose (documented in `Standards_yaml.qmd` and `data_contracts_adr.qmd`): the exact column header in the data file, which drives the ingestor's rename to the slug, so recipes can use plain names while the files stay as the pipeline tools write them (headers such as "Sequence Type" or "%Identity"). HOME does not need it (columns are slugs after ingestion). On an output list it has no ingest role (Blueprint shows it); its fate follows O7 | keep on input fields; on output lists it follows O7 | section 7.4 |
| O17 | **Profiles**: `run` and `build` differ only in what an empty placeholder may be | keep | section 3 |

## 3. Profiles, and what counts as a recipe

There is one format. A recipe is checked in a **profile**; profiles differ only in what an empty placeholder may be (O17):

| Profile | Used by | Rule |
|---|---|---|
| `run` | HOME's load gate; any program that draws plots | `analysis_groups` holds at least one group with at least one plot |
| `build` | Blueprint (building step by step); recipes that only build data (transformer tests, scripts) | `analysis_groups: {}`, `tier2: []`, `tier3: []` are accepted placeholders |
| `gallery` | gallery examples | the rules of section 9 on top of `run` |
| `audit` (proposed with the HOME session, O4) | the audit copy of a recipe | like `run`; steps with an `id` of the form `audit_<8 hex>_<k>` are accepted (O5) |

HOME rejects, Blueprint reports and never blocks building `[DECIDED, 5a-19]`.

| Kind | Files | Profile | Notes |
|---|---|---|---|
| Pipeline recipes, templates, retest scenarios | 7 + 5 + 4 | `run` | the retest scenarios that are faulty on purpose keep their one fault and must be otherwise valid |
| Viz-factory test recipes | 194 in `libs/viz_factory/tests/test_data` (one per plot component, the 1:1:1 evidence loop of `rules_viz_factory.md` 3) and 1 in `libs/viz_gallery/tests/data` | `run` | today in the plot engine's compact shape (`plots:` and `data_path:` at the top; 193 of 194): each becomes a standard recipe like a gallery example; one conversion tool serves them and the gallery bundles; found by Eve's question "do the library tests have recipes too?" (#89) |
| Transformer test recipes | 68 in `libs/transformer/tests/data` | `build` | the flat form (`wrangling:` and `input_fields:` at the top) is refused: each becomes one schema with its `source` path. The runners already prefer a command-line data path to the recipe's (`rules_asset_scripts.md` 4) |
| Gallery bundles | 34 | `gallery` | section 9 |
| Recipes written by the app | Blueprint's new-recipe form, test-lab bootstrapper and scaffolder, `create_data_analysis_recipe.py`, the export's forked recipe, the importer | their use | the checker runs on what they write; a test per writer; every writer emits `spec_version` |
| Recipes inside automatic tests | inline YAML strings in tests and fixtures | their purpose | one shared helper writes a minimal valid recipe, so no test types the boilerplate |

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

Refused at the top level, with the replacement named (section 12): `plots`, `wrangling`, `input_fields`, `output_fields`, `name`, `pipeline_id`, `description`, `metadata`, `type`, `join_manifests`, and any other unknown key (with a did-you-mean by spelling).

### 4.1 The format version

Every recipe declares `spec_version: 1`, the version of this specification it is written in (the key is called `spec_version`, Eve 2026-11-13). The first confirmed specification is format 1; the unversioned recipes of today are **format 0**. The key is not `info.version`, which stays the author's own version of the recipe's content.

The app reads **one** version. Any change of *structure* changes the number: a key added, removed or renamed, a change of required-ness or meaning, a change of a closed vocabulary (the types, the engine names). A new term in an *open* vocabulary (the gallery terms) does not: it ships with an app release, and an app that does not know the term refuses the recipe with "unknown term". With "unknown keys fail" a new optional key also breaks an older checker, so there is no "compatible minor version", and one integer is enough.

| Check | Sev | Trigger | The message says |
|---|---|---|---|
| V01 | E | missing | this recipe is in the old format 0; run the migration tool |
| V02 | E | lower than the app reads | written for format N, the app reads M; migrate |
| V03 | E | higher | written for a newer format; update the app |
| V04 | E | not an integer (`"1"`, `1.0`, `true`) | write `spec_version: 1` |

**Migration tool:** `assets/scripts/migrate_recipe_format.py --from 0 --to 1`, on the pattern of `migrate_config_vocabulary.py`: a dry run by default, `--apply` to write, safe to run twice. It edits the text, so every `#` comment is kept. It applies the replacement table (section 12), adds `spec_version` and the engine lines, unwraps fragments and writes a `label` from the id for the author to edit. It does **not** invent what is not mechanical: descriptions stay empty (an advice), `entity` is not added, science is not touched; it prints what a person must still do.

**Where the number is recorded:** every recipe written by the app, the forked recipe of an export, `effective_run.yaml`; the importer's recipe leg says when the version differs. History table: format 0, the unversioned recipes before 2026-11-13, refused with the migration message; format 1, this specification.

**Consequences to accept.** (a) One more required key in every recipe (16 + 68 + 34 files, all writers, many tests); the tool does the mechanical part. (b) An export made under format 0 cannot be re-run until its recipe is migrated; the migrated recipe has another hash, so the importer reports a difference. This follows from "no compatibility default"; the bundle still holds the original file. (c) A number can be wrong: the checker still reads the keys, so it shows as an unknown or missing key. (d) The same idea may later apply to the app-features and deployment files; not proposed now.

## 5. The form of every container (ADR-041)

**What exists.** ADR-041 (ENFORCED 2026-04-20): keyed definitions are a dictionary (field definitions are `slug: {props}`, slugs unique), ordered logic is a list (`tier1`, `tier2`), fragments are flat (the value only, no repeated anchoring key).

**The rule: the form follows what depends on it** `[DECIDED 2026-11-13]`:

| Category | Form | What depends on it | Containers |
|---|---|---|---|
| 1. Named; the order means nothing for the data | **dictionary** | lookup by name; names are unique | `data_schemas`, `additional_datasets_schemas`, `joins`, `input_fields`, `output_fields`, `source`, `mapping`, `plot_defaults`, `info`, `entity`, `taxonomy`, `spec` |
| 2. Ordered; the items need no name | **list** | the order of operations, drawing or joining; YAML guarantees the order of a list | step lists (`tier1`, `tier2`, `tier3`), `ingredients` (the first is the base), `layers`, a `multi` column-selector parameter |
| 3. Named, and the order is meaning | **ordered dictionary**: the order of the keys is documented as meaningful | `final_contract`: the column order of the table; `analysis_groups`: the tab order; `plots` of a group: the sub-tab order | those three |

Container by container:

| Container | Form | Refused |
|---|---|---|
| category 1 containers above | dictionary | a list (also a list of names, or of one-key dictionaries) |
| `final_contract`, `analysis_groups`, `plots` of a group | ordered dictionary | the same |
| a field entry | dictionary `{type, label, ...}`, or `{}` meaning "as in the input" | a bare string (`sample_id: categorical`, the old shorthand; none is left in the repository) |
| `wrangling` of a schema, `steps` of a join | dictionary with `tier1` (list) and optional `tier2` (list) | a flat list, `[]` |
| `tier1`, `tier2`, `tier3` | list of step mappings (7.5) | a dictionary |
| `ingredients` | list of `{dataset_id: ...}` | a dictionary, bare ids |
| `layers` | list of `{name, params, comment}` | a dictionary |
| a column-selector parameter declared `multi` | list of names | a single value |
| an included fragment | the value itself | a wrapper key that repeats the include key |

**Category 3 is verified, and needs safeguards.** The columns of a table follow the keys of `final_contract` (`orchestrator.py:59-66`). PyYAML keeps the order on load but sorts on dump by default; five dump sites in non-test code sort today (`exporter.py:56,86`, `wrangle_studio.py:1848,1864`, `blueprint_handlers.py:861`); `canonical_hash` sorts keys (`cache_keys.py:53-55`, `hashing.py:18`). **A defect found by running it:** reversing the keys of `final_contract` changes the column order of the stored Tier 1 but **not** of the stored Tier 2, because the sorted hash cannot see the order (issue #86; `tmpAI/recipe_format/contract_order_test.py`). The safeguards:

1. The loader keeps the file order and refuses a repeated key (T10): PyYAML silently keeps the last.
2. Every writer passes `sort_keys=False`, guarded by a test that scans every `yaml.dump` and `safe_dump` of non-test code.
3. A key (hash) that depends on an order is made from the ordered items, never from a sorted dictionary: `final_contract` enters the Tier 1 key material as an ordered list of its keys. The tab order is downstream only and enters no data key.

**What does not depend on order (checked):** `input_fields` and `output_fields` of a schema (the ingestor renames and casts, never selects by them; if schema `output_fields` are ever applied they become category 3, O7), `joins`, `data_schemas` (the one reader of the order of `joins` is the first-join fallback, which goes, section 15), `mapping`, `params`, `info`.

**What the repository contains today** (scan `tmpAI/recipe_format/container_forms.py`, all kinds of recipe, verified): all 307 input and 162 output field entries are dictionaries; **17 containers are in list form**: 7 empty `[]` written where `{}` or `{tier1: []}` belongs, and 10 with content (3 `final_contract` lists, 1 `output_fields` list of names, 1 flat `wrangling`, 5 flat join `steps` in fixtures); **the engine skips a list-form `final_contract` silently** (`orchestrator.py:59-62`), so the contracts of `demo_abromics`, `universal_template` and `relational_audit` are **not applied today**, and converting `demo_abromics` makes it an exclusive whitelist of 5 columns (its plots are checked at migration, #78); **33 fragments carry the wrapper key** that ADR-041 prohibits (the loader removes it silently); two texts contradict ADR-041 (`rules_data_analysis_recipe_structure.md` section 8 "single `spec:` root key"; `data_analysis_recipe_data_contract_rules.md` 4.3 types), both go in the documentation sweep (#79).

### 5.1 The message carries the correction `[DECIDED 2026-11-13]`

Each container-form check generates the corrected text from what it found. The same adapter serves HOME's load gate, Blueprint's Validate, the import screen, the scripts and the tests, so they show the same message. Each check has a test that asserts the message **contains the corrected text**, so the suggestion cannot go stale. The migration tool applies the same corrections mechanically.

| Found | The message shows (generated) |
|---|---|
| `final_contract: [sample_id, value_col]` | `final_contract` is a dictionary of columns. Write: `final_contract: {sample_id: {}, value_col: {}}` |
| `final_contract: [{sample_id: {type: categorical}}, ...]` (a list of one-key dictionaries) | the same dictionaries merged: `final_contract: {sample_id: {type: categorical}, ...}` |
| `output_fields: []` | `output_fields: {}` |
| `steps: [{action: join, ...}]` (a flat list) | `steps: {tier1: [{action: join, ...}]}` |
| a wrapper line `input_fields:` inside the included file | remove the line and its indentation; the file holds the fields themselves |
| `sample_id: categorical` | `sample_id: {type: categorical}` |
| a repeated key | names the key and both lines; remove or rename one |

The file keeps the dictionary; the code makes the list it needs (`list(final_contract)`). No recipe writes a list of names.

### 5.2 Identical keys `[verified]`

A key must be unique **inside one mapping** (ADR-041). The same slug in different mappings is normal: `sample_id` is in the `input_fields` of every table (66 field dictionaries in the repository, each its own mapping) and in every row of a long table. The real hazards are:

1. **A repeated key inside one mapping:** PyYAML keeps the last silently (T10). This holds at any depth, including a `mapping` parameter: `{a: x, a: y}` silently drops a rename.
2. **A column name in both tables of a join that is not a join key:** the engine calls `lf.join(...)` without a suffix (`joins.py:56-58`), so Polars renames the second column to `name_right` without a message; `QC_Reads_Anchor` has `total_reads_right` today. The join keys themselves (`sample_id`) are the key family and are fine. Check **J08** (an error with a guidance message, decision 23); it needs the recipe graph. The message names both tables and the column and says how to rename or drop one before the join. `QC_Reads_Anchor` will therefore fail the checker until it is fixed in its migration.
3. **Steps** repeat actions (a table has three `join` steps), so ordered logic cannot be keyed by the action name; it stays a list and a step that needs a name carries an `id` (7.5).

## 6. Fragments and comments

### 6.1 Fragments (`!include`)

- `key: !include 'path/to/file.yaml'` puts the content of the file exactly where the key is. The path is relative to the folder of the recipe `[CODE, config_loader.py:55; nested includes use the same folder]`.
- **The fragment holds the value itself, with no wrapper key** `[DECIDED, ADR-041 point 3]`. A file whose only top-level key repeats the key it is included under is refused with "remove the wrapper line" (F01). Today the loader removes the wrapper silently (`config_loader.py:77-97`), a compatibility default that ADR-041 prohibits. The ST22 recipe has 68 includes: 56 bare, 12 wrapped; over all recipes 33 are wrapped.
- A missing file is an error naming the file (T02).

### 6.2 Comments

Two things are called a comment. Both are allowed.

| What | Form | Rule |
|---|---|---|
| A YAML comment | `# any text`, on its own line or after a value, in a recipe or fragment | **Free, anywhere, never refused.** It is not a key: the loader drops it, the checker never sees it. **Any tool that edits a recipe or a fragment keeps every comment** (a text-level edit or a round-trip library, never `yaml.dump`); a test per writer checks it. The ST22 recipe has 150 comment lines (10 in the main file, 140 in its fragments) that explain defaults and why a column is kept; the first line of `Summary_input_fields.yaml` is Eve's note "do not remove my comments" |
| A `comment` key | `comment: text`, optional, on `info`, a schema, a join, a group, a plot entry, **every step and every layer** | The author's note of **intent: why, not what**. Read by people, never executed, never passed to an action or to the plot engine. `[CODE for steps, layers, groups, plots: BP-COMMENTS-1, ADR-082 Q4, ADR-083; PROPOSED for info, schema, join, O13]`. It is not the `description`: the description says what the element is; `comment` says why. Two ST22 schemas used a plural `info.comments`; it becomes `comment` |

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
| `category`, `sub_category` | o | grouping text shown in Blueprint `[PROPOSED, O14]` |
| `comment` | o | the author's note (was the typo `info.comments`, now refused) |
| `source` | R | `{type, path}`; `type` is `local_tsv` or `local_parquet`; `path` is relative to the project root. The fuzzy search of a file by dataset name (`ingestor.py:80-92`) goes |
| `input_fields` | R | mapping `column slug -> field` (7.4); `{}` means no contract |
| `wrangling` | R | `{tier1: [...], tier2: [...]}` (7.5); `tier1` required, `tier2` optional; `[]` and a flat list are refused |
| `output_fields` | o | mapping `column slug -> field`; checked by the data check, **not applied by the engine** (O7) |

The three sections share one id space; a repeated id is an error (today the second silently replaces the first, `orchestrator.py:151-157`). `tier2` of a schema is applied **only when the schema is plotted directly**; on a schema that is only an ingredient it is an error `[DECIDED]`. The keys `fields` (alias of `input_fields`) and `info:` are refused.

### 7.4 Fields (`input_fields.<slug>`, `output_fields.<slug>`, `final_contract.<slug>`)

| Key | Meaning |
|---|---|
| `type` | `categorical` (default), `utf8`, `numeric`, `date`, `boolean`; anything else is an error (decision 20) |
| `original_name` | the column name in the file when it differs; shown in Blueprint. Allowed on output lists (O16) |
| `label` | display name (default: the slug) |
| `is_entity_key` | `true` when the column identifies the entity (it repeats in long tables). Replaces `is_primary_key` `[DECIDED]` |
| `categories` | list of text; a step can then select `@category` (`data_wrangler.py:31-48`) |

`{}` in an output list means "keep this column as it is".

**The type vocabulary** `[DECIDED 2026-11-13: one place; five types]`. Four lists disagree today: the rule file (`categorical`, `utf8`), the user docs (`categorical`, `numeric`, `date`, `boolean`), the ingestor (casts `numeric` to Float64, `categorical` and `string` to String, `date` to Date, **nothing else**, `ingestor.py:162-170`) and `MetadataValidator.DTYPE_MAP` (14 names, `metadata_validator.py:21-37`). Verified by running the ingestor on a column of digits: `categorical` and `string` give String; `utf8`, `boolean` and `i64` are **not cast** (the digits stay Int64), so `utf8` does not force text; `string` is accepted by the ingestor but refused by `enforce_schema`; 4 fixtures declare `i64`, which nothing handles. `string` was removed on 2026-05-22 as a "deprecated alias" (`LEGACY-TYPE-ALIASES-1`, commit `125963cf`); no ADR gives a deeper reason. What the files show: all 6 recipes that used it were migrated to `categorical`, and the rule wants the author to say whether a text column is a **group** (`categorical`: identifiers, labels, repeating values; `sample_id` must be one so that digits become text and joins match) or **free text** (`utf8`).

**Decided (Eve, 2026-11-13): option A plus `boolean`.** Five types: `categorical` (the default: identifiers, labels, repeating values; a group), `utf8` (free text), `numeric`, `date`, `boolean`. What changes: the ingestor casts `utf8` to text (today it does not) and `boolean` with a real cast (the accepted spellings are fixed in the vocabulary file and tested); `string` stays refused and its message quotes the two meanings (`categorical` or `utf8`); the 4 fixtures that declare `i64` are corrected. Alternatives that were not chosen: rename `utf8` to `text`; restore `string` and drop `utf8`.

The vocabulary is one list in the specification file, each entry with a one-line meaning that the error message quotes (section 14).

### 7.5 Steps, tiers and step ids

- A **step list** is `{tier1: [...], tier2: [...]}`. It appears as `wrangling` (schema), `steps` (join) and, at the plot entry, `steps: {tier3: [...]}` (7.7). All three are written the same way; an empty list means "equal to the previous node". `tier1` is required except at the plot entry; an unknown tier name is an error. `[DECIDED, 5a-15]`
- A **step** is a mapping with `action` (a registered name), exactly the parameters in that action's `ui_schema.params`, and optionally `comment`, and `id` when the app wrote it (below); neither is a parameter and neither is passed to the action. A missing required parameter, an unknown parameter and an unknown action are errors with a did-you-mean by spelling.
- **No guessing between spellings of a parameter.** Before a step runs, the wrangler looks for "which columns does this step work on" in six spellings in a fixed order (`columns`, `column`, `source`, `source_column`, `target_column`, and the boolean key that an unquoted `on:` becomes), expands `@category` names, checks the columns exist (ADR-034's friendly message) and **writes the result back into the step as `columns`** (`data_wrangler.py:132-147`). So a step that says `column:` for an action whose schema says `columns` works by accident. What goes is the guessing, not the presence check and not `@category`: those read **the parameters that the action's own schema declares as column selectors** (71 parameters in 59 of 65 actions). A misspelled parameter is then reported before the run with the right name (ST03). Exactly 14 steps in 10 recipe files rely on a wrong spelling today. `[PROPOSED mechanism, O15]`
- `join` and `join_filter` only in tier1 (ST05). `join_filter` has no `how`; it is always inner (`joins.py`), so `how` on it is an error.
- `'on'` is quoted. An unquoted `on:` becomes the boolean key `True`; today the loader repairs it with a printed warning (`config_loader.py:18-41`). It is an error (T07).
- Formulas (`mutate` `expression`, plot function strings) may use only an allowed list of Polars operations by function name (O10).

**Step ids: written by the app, not by authors** `[DECIDED direction; the name is O5]`. Steps stay lists. A step has no name in the author's recipe: nothing in a recipe refers to a step, so an author writes no `id`. The key exists for one reason: the audit mode inserts steps into the audit copy of a recipe and must be able to **mark** them (the origin marker), to **remove or undo exactly those**, and to open the right node popup. So a step the app inserts carries `id: audit_<unique suffix>`, and the invariant "the copy minus its marked steps equals the original" compares those ids.

```yaml
tier1:
  - action: join                          # the author's step: no id
    right_ingredient: Quast
    'on': sample_id
    comment: reads quality and assembly quality side by side
  - id: audit_7f3a                        # inserted by the audit mode
    action: filter_eq
    column: Country
    value: Norway
```

Rules: (1) `id` is accepted because the audit copy contains it; it is text and unique inside its list (ST08). The checker is not obliged to accept an `id` in a recipe that is not an audit copy; whether it warns is decided with the audit mode. (2) `id` and `comment` are **not part of the hash** (a mark or a note must not rebuild a table); the order is. (3) The list is the order, so nothing depends on the order of a mapping. (4) Error messages name a step by its place ("step 3 of `tier1` of `QC_Reads_Anchor`, `join`"), never by an id the author did not write. Why not the action name as the key: a table repeats actions (11 of the 74 non-empty step lists repeat one; `QC_Reads_Anchor` has three `join` steps; 148 steps in those lists at least). No action has a parameter named `id` (checked), so there is no clash.

| Option | Pros | Cons |
|---|---|---|
| A. Steps as an ordered dictionary of ids | an id by construction | all three dangers (silent duplicates, sorted hashes, sorting writers) become real for every step; every step needs a name; 6 writers and Blueprint's form change; 148+ steps migrate; ADR-041 point 2 superseded |
| **B. A list; the app marks the steps it inserts with an `id`; authors write none** (direction) | YAML guarantees the order; a duplicate cannot drop a step silently; no migration of steps; nothing new for authors | the id is a key inside the item, not the key of the container (ST08 enforces uniqueness) |
| C. A list without any id | nothing changes | the audit mode must mark its steps another way (a separate key, or by position, which breaks when a step is inserted) |

### 7.6 Join (`joins.<id>`), a collection built from schemas

| Key | | Meaning |
|---|---|---|
| `label` | R | short name |
| `description` | a | what one row is, which tables are combined and how, what is removed, what a missing value means here |
| `comment` | o | the author's note |
| `ingredients` | R | list of `{dataset_id: <schema id>}`, at least one; **the first is the base**. A bare id (`- FastP`) is refused |
| `steps` | R | `{tier1: [...]}` at least (7.5) |
| `final_contract` | o | mapping `column -> field`, an **exclusive whitelist** in column order: the collection keeps exactly these columns, in this order. A list is refused (today it is skipped silently); a column the collection lacks is an error (today only printed) |

`output_fields` or `info` on a join are refused (the message says `final_contract` and `description`). Each `right_ingredient` is one of the join's `ingredients`; `on`, or `left_on` with `right_on`, names the key (not both). The orchestrator's silent fallbacks go: an unknown collection falls back to the first join (`orchestrator.py:198-206`) and a join without ingredients uses all schemas (`orchestrator.py:224`).

### 7.7 Analysis group and plot entry

`analysis_groups.<group id>`: `label` (R, the tab text), `description` (a), `comment` (o), `plots` (R, mapping; at least one in profile `run`). The fallback "label, else description, else id" (`home_theater.py:1119`) goes: 4 of the 5 ST22 groups have the tab text in `description` today. The order of the groups is the tab order `[DECIDED]`.

`plots.<plot id>` (snake_case, unique over all recipes); the order is the sub-tab order `[DECIDED]`:

| Key | | Meaning |
|---|---|---|
| `label` | R | the plot's tab text |
| `description` | a | what it shows, what is counted, which subset it leaves out |
| `comment` | o | the author's note |
| `spec` | R | the plot specification (7.8) |
| `steps` | o | `{tier3: [...]}`: the steps applied to this plot's table after its tier 2. Any registered action; the audit mode writes only filters and drops here. Omitted or empty means the plot reads its table as it is `[DECIDED, 5a-15; name and place O12]` |
| `taxonomy` | o | classification for the Gallery (section 9); required in profile `gallery` |

`info:` on a plot entry (a sentence, 25 times today) is refused: the message says `description`.

### 7.8 Plot specification, layers, `plot_defaults`

`spec` keys, the set the plot engine reads (`plot_config_resolver.py:71-74`): `target_dataset` (R, a join id or a schema id), `mapping` (R), `layers` (R, at least one geom or stat), `title`, `theme`, `facet_by`, `palette`, `labels`, `guides`, `filters`. Everything else is an error, with the replacement of section 12 where one exists (`facet_scales`, `labs`, `coordinate_flip` become layers, issue #66). `description` and `info` are refused inside a spec: they are the plot entry's. The gallery taxonomy keys `family`, `pattern`, `difficulty` are refused in a spec: the taxonomy is the gallery's, not the recipe's (Eve: "do not confound"); 16 of the 17 ST22 specs carry three of the axes only because they were copied from gallery examples on 2026-04-10, and no code reads them from a pipeline plot (O18).

`mapping`: keys are aesthetic names of the plot engine (`x`, `y`, `fill`, `color`, `group`, `facet_by`, ...); values are column names of the target table (the "column exists at that node" check needs the recipe graph, X7).

`layers`: list of `{name, params, comment}`; `name` is a registered component (all 191 have a schema; none of the 167 layers in the repository has an unknown name); `params` are checked against **the component's schema plus the arguments of the wrapped plotnine function** `[DECIDED 2026-11-13]` (section 8).

Two forms exist for the same thing (`facet_by` at the top of the spec and inside `mapping`; `filters` in the spec and the tier-3 list); both are read today, both stay allowed (O9).

`plot_defaults` keys: `palette`, `theme`, `default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`, `layers` (`plot_config_resolver.py:64-67`). `height` and `show_legend` (2 templates) are errors.

## 8. Operations and the registries `[verified 2026-11-13]`

**The mechanism.** An operation exists because a Python function carries a decorator, run when its library is imported. `@register_action("name", ui_schema={...})` (`transformer/actions/base.py:22`) fills `AVAILABLE_WRANGLING_ACTIONS` and, with a schema, `ACTION_SCHEMAS`. `@register_plot_component("name", ui_schema={...})` (`viz_factory/registry.py:21`) fills `PLOT_COMPONENTS` and `COMPONENT_SCHEMAS`. A name registered twice overwrites the first. Today: **67 actions (65 with a schema), 191 components (all with a schema)**. A schema holds `label`, `category`, `context` (where the operation may appear: t1, t2, assembly, plot), `tags`, `params`, `description`, `yaml_example`, `wraps` (the Polars or plotnine function it wraps). `server.py` already hands both schema dictionaries to `blueprint_arch.schema_registry.register` at startup (ADR-011 injection).

**What the checker reads:** the name (ST02, PS04), the parameters declared (ST03), the required ones (ST04), `multi` (ST07), the shape of each value (ST10), `context` against the tier (ST05 is one case). The core imports neither library (section 14): each caller exports its registry as plain data (name to `{params: {name: {widget, multi, required, options}}, allowed_extra_names, context}`) and passes it in.

**What the registries do not say today** (scripts `registry_survey.py`, `registry_conformance.py`, `registry_examples.py` in `tmpAI/recipe_format/`), with why and consequence. **Status 2026-11-13:** the part that does not depend on the recipe migration or the checker is **built** (issue #87: R1, R5, the self-consistency tests; permission given by Eve); the dependent parts are in #76 (ST09, ST10, AR3 against the checker) and #78 (the alias reads, R2). One more defect was found by asking plotnine about every schema parameter: 13 parameters in 7 components that plotnine refuses (#88).

| # | Gap | Why it is so | Consequence | Fix |
|---|---|---|---|---|
| R1 | **No widget for a list or a dictionary.** Eight parameters are declared `string` while their own example writes a list or a dictionary (their labels already say "YAML list" or "YAML dict"; the two `is_in`/`not_in` labels say "comma-separated", which the code does not read): `rename.mapping`, `rename_columns.mapping` (dictionary); `recode_values.rules` (list of mappings); `replace_values.to_replace`, `is_in.values`, `not_in.values`, `split_column.new_columns`, `split_column_to_parts.new_columns` (lists) | the schemas were written for the Blueprint form renderer (ADR-075), which knows 9 widgets (`column_selector`, `string`, `enum`, `column_or_literal`, `number`, `dtype_picker`, `expression`, `bool`, `color`) | Blueprint shows a text box and its save handler keeps the typed text as a string (`blueprint_handlers.py:1213-1216`, read, not run); a checker cannot test the shape and would call the actions' own examples wrong | **Built (#87):** widgets `list` and `mapping` (a list of mappings is a `list` with `items: mapping`), one vocabulary in `utils.ui_schema.WIDGETS`; the eight corrected; the Blueprint form shows one line of YAML and saves a list or a mapping (`blueprint_arch.widget_text`), and an error says the form to write. Check ST10 stays in #76 |
| R2 | **The code reads keys the schema does not declare:** `rename.target_column` (`cleaning/core.py:126`), `split_column.source`, `.target_column`, `.separator` (`reshaping/core.py:202,205`) | aliases kept for older scripts (comments in the code) | a recipe using an alias passes today and a schema-based checker refuses it. Used today: `split_column` `source` x3, `separator` x1, `column` x1, `new_names` x1; `keep_columns` `target_column` x1; `split_and_explode` `target_column` x3, `column` x2 | removed with the recipes that use them (#78); test AR2 is a ratchet that lists them (`test_action_registry_consistency.py`) |
| R3 | **Engine-internal keys travel inside a step:** `__right_df__` (`data_assembler.py:207`, read at `joins.py:39`) and `__metadata__` (`data_wrangler.py:196`, read at `cleaning/core.py:320,349`) | the engine passes the right table and the primary keys through the step dictionary | a recipe could carry them and reach the function | check ST09 (#76) |
| R4 | `scan_parquet` and `sink_parquet` have no schema | engine-internal actions; 4 fixture steps use them to test them | an unknown-parameter check cannot run on them | O11 |
| R5 | **All 191 components have `allow_extra_params: true`** and their schemas list only part of the arguments (802 parameters) | **deliberate**: a component does `p + geom_x(**spec)`, any plotnine argument passes (`libs/viz_factory/README.md:266`, test `test_allow_extra_params_is_true`) | "unknown parameter fails" cannot rest on the schema alone: it would refuse valid arguments (`color` x8, `outlier_alpha`, `size` in the shipped recipes). plotnine itself refuses an unknown argument (`PlotnineError`, verified) and accepts both `color` and `colour` | **Built (#87):** `viz_factory.arguments`: for a geom or stat exactly what plotnine accepts (verified against plotnine for all 63), for another plotnine class or function its signature with the schema, `None` for free-form components; `argument_catalog()` is plain data for the checker. Asking plotnine about the schemas found 13 parameters it refuses (#88). Completing the 191 schemas is a later option |
| R6 | The wrangler's column resolution and ST03 must read the same declaration | `data_wrangler.py:132-147` | two readings could disagree | one reading: the parameters with widget `column_selector` |

**Which form each parameter takes** (the rule of section 5 applied inside a step): a **list** where order or repetition is meaning or a set is meant (`columns`, `values`, `new_columns`, `rules`); a **dictionary** where each entry is a name with a value (`mapping`: old name to new name); a **scalar** otherwise. The registry must say which.

**Self-consistency tests** (built, they run on the registries; no recipe needed): AR2 the keys a function reads equal its schema (a ratchet that lists the aliases of R2); AR3 every `yaml_example` agrees with its schema in names and value shapes (`test_action_schema_examples.py`; it failed on the eight of R1 before the fix, and passing it **through the checker** comes with #76); AR4 every `wraps` resolves to an importable object; AR5 every component or action named by an example is registered; AR6 no name is registered twice in the source; a layer argument that plotnine accepts (`color`, `colour`) passes and one it refuses (`foo`) fails; every enumerated geom and stat argument is accepted by plotnine and an invented one is refused; the schema parameters that plotnine refuses are a ratchet (#88).

## 9. Gallery examples `[DECIDED 2026-11-13: D1, D2, D3; D4 to D7 later, O1]`

**Today** (verified, `gallery_manager.py`, `gallery_viewer.py`, `generate_previews.py`): a bundle in `assets/gallery_data/<id>/` holds `data_analysis_recipe.yaml` (its own compact shape: `info` with name, date and six taxonomy values; `data_path`; one plot; `wrangling` with an optional `tier3`), `example_data.tsv`, `example_meta.md`, `preview_plot.png`, `preview_thumb.png`. `gallery_index.json` is rebuilt from the bundles (a registry and a pivot of taxonomy value to examples). The viewer filters by six axes, shows Plot / Data / YAML tabs and the guidance text. Constraints that stay: a static reference (ADR-093: no run in the app, no handoff to HOME or Blueprint), offline use, mounted only if `gallery_enabled` (ADR-071), one plot per example, the folder name as the example's id, the six filter axes and icons, the index format the viewer reads.

**What is wrong, and each will be fixed** (details and the plan are in issue #82):

| # | Finding | Fixed by |
|---|---|---|
| G1 | the taxonomy terms are copied in five places and disagree (both fallback lists contain "Numeric-Numeric", which the cheat sheet does not allow, and lack 4 of 10 patterns) | the terms in the specification (one place); the UI reads them |
| G2 | previews do not come from the app's path: the script hands the bundle's own dict to the renderer, so an example the app could not load still gets a picture | previews by the app's path |
| G3 | the example file is never validated as a recipe; `data_path` is read by nobody | `check_recipe` in profile `gallery` at rebuild, at app start and in the tests |
| G4 | `dumbbell` declares `geom_segment` and draws `geom_line` and `geom_point` | `geom` derived from the first geom layer; the example is reviewed with Eve |
| G5 | 10 of 34 previews are 800x600, 24 are 960x600 | one standard size |
| G6 | dead submission code (`submission_modal_ui`, `autofill_meta_from_audit`, `btn_confirm_submission`) | removed, or kept on purpose (Eve's call) |
| G7 | the tag strip of each `example_meta.md` repeats the taxonomy, unchecked | generated from `taxonomy`, or checked |
| G8 | the taxonomy travels by copy into 16 of 17 ST22 plot specs through the `_meta` passthrough of ADR-083 | removed in the ST22 migration (O18) |

**Proof that it works** (`tmpAI/recipe_format/gallery_poc.py`, scratch): all 34 examples written as standard recipes build and render through the app's own path (ConfigManager, DataOrchestrator, VizFactory); 22 previews are pixel-identical, 10 differ only in size, 2 differ by jitter (0.9 % and 2.6 % of the pixels).

**Design (decided 2026-11-13):**

- **D1. An example is a standard recipe** (id, `spec_version`, engines, info, one schema, one group, one plot) checked in profile `gallery`. Pros: one format, one checker, one render path; an example is runnable; it shows good practice; the 34 examples become a regression suite for the plot path. Cons: the file is longer (35 to 60 lines against 25); 34 files to rewrite (scripted, reviewed); a deployment that moves the gallery folder can browse but not run the examples. Alternatives (keep the compact shape and add checks; generate a recipe from the compact shape) keep two formats or two sources.
- **D2. `taxonomy` on the plot entry**, required in the gallery profile and optional in any other recipe (so a plot can be offered to the Gallery without retyping), five declared axes: `family`, `pattern`, `difficulty`, `show`, `sample_size`; `geom` is **derived** from the first `geom_*` or `stat_*` layer and still offered as a filter. It replaces the `_meta` passthrough of ADR-083. Alternatives: `info.taxonomy` (info is free-form, so the check is a special case), a sidecar file (a second format), inside the spec as ADR-083 does (the spec stops being pure grammar).
- **D3. The specification is also a data file** in `libs/utils` (with `check_recipe`): for each element its allowed keys and their requiredness, the types, the **vocabularies** (types, engines, **the gallery terms** with label, icon, order and a line of meaning), the table of renamed keys, the format version. The checker, the filter panels, the index order, the cheat sheet, the appendix tables and the migration tool read it or are generated from it. Cross-element rules and the registries stay in code. Terms change more often than structure: a new term in an open vocabulary does not change `spec_version`. A packaging condition is in section 14.
- **D4 to D7 (can wait until the gallery work starts):** D4 the same `check_recipe` at index rebuild, at app start (left out of the list with the reason shown, as HOME's gate) and in the tests (recommended); D5 previews by the app's path in a Tier-3 script under `assets/scripts/`; D6 keep the teaching text of `example_meta.md` and build the tag strip from `taxonomy`; D7 a data contract generated from the file and reviewed.

**The gallery profile checks** `[PROPOSED, with the decision]`: exactly one group and one plot (GP01); `taxonomy` present with the five axes, each term in the vocabulary (GP02, GP03); `id` equals the folder name (GP04); the companion files exist (GP05); `spec_version` present like everywhere.

**An example looks like this** (`bar_simple`; `geom` is not typed, the old `data_path`, `name` and `wrangling.tier3` disappear: the path is in `source`, the name is `label`, the example's own steps are the plot's `steps: {tier3: [...]}`):

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
    input_fields:
      id: {type: categorical, label: Record}
      species: {type: categorical, label: Species}
      amr_class: {type: categorical, label: Antimicrobial class}
      value: {type: numeric, label: Value}
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

**Risks:** Blueprint's save path must keep the plot entry's keys (`taxonomy`, `comment`, `steps`; verify in `group_plot_manager` before converting); the first preview regeneration changes 12 pictures in git (each is looked at); a generated data contract could change a picture if a type is guessed wrong (the proof-of-concept script is the guard); the Playwright gallery tests and four UML diagrams need an update; if D3 is chosen the schema language can grow (the guard: keys, requiredness, types, vocabularies, renames and the version only).

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
| X7 | a step or a `final_contract` that names a column the node does not have is an error (a dry run on column names). Needs the recipe graph |

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
| F01 | E | fragment wrapper repeats the include key | remove the wrapper line |
| F02 | E | fragment has the wrong type (a list for a mapping) | |
| I01 | E | `info` not a mapping, or `label` missing | add `label` |
| I02 | A | `info.description` or `info.contact` missing | write it (section 13) |
| I03 | E | `info.display_name` | `label` |
| E01 | E | unknown key in `entity`; `noun`/`plural`/`population` missing | |
| E02 | E | `population` unknown, or its table has no entity key | |
| S01 | E | unknown key in a schema (`info`, `fields`, `id`, ...) | replacement |
| S02 | E | repeated schema id; use of the reserved id | |
| S03 | E | schema without `label` | add it |
| S04 | A | schema without `description` | write it |
| S05 | E | `source` missing, type not `local_tsv`/`local_parquet`, `path` missing | |
| S06 | E | `wrangling` is a flat list, `[]`, or has no `tier1`; unknown tier key | `{tier1: []}` |
| S07 | E | `tier2` on a schema that is only an ingredient | move it to a join, or plot the schema |
| S08 | E | `input_fields` / `output_fields` not a mapping | |
| FD01 | E | unknown field property | replacement |
| FD02 | E | `type` not in the vocabulary | the vocabulary with its meanings |
| FD03 | E | `is_primary_key` | `is_entity_key` |
| FD04 | E | `source_name` | `original_name` |
| FD05 | E | `is_entity_key` not true/false; `categories` not a list of text | |
| FD06 | E | a field entry is a bare string | `{type: categorical}` |
| ST01 | E | step without `action` (shorthand), or not a mapping | |
| ST02 | E | unknown action | did-you-mean |
| ST03 | E | parameter not in the action's schema (`id` and `comment` are allowed everywhere) | did-you-mean; `column`, `source`, `target_column`, `source_column` -> `columns` where that is the name |
| ST04 | E | required parameter missing | |
| ST05 | E | `join` or `join_filter` in tier2 | |
| ST06 | E | a formula uses an operation outside the allowed list | O10 |
| ST07 | E | a parameter declared `multi` has a single value | write a list |
| ST08 | E | in profiles `run` and `build`: any `id` on a step (authors write none); in profile `audit`: an `id` that does not match `audit_<8 hex>_<k>`, or two steps with the same `id` | remove it (it is written by the app); names the place |
| ST09 | E | a reserved engine key (`__right_df__`, `__metadata__`, any `__name__`) in a step | remove it; the engine sets it |
| ST10 | E | the value of a parameter has the wrong shape for its declared widget (a list where a scalar is declared and the reverse; a repeated key in a `mapping`) | the declared form and the corrected text |
| J01 | E | unknown key in a join (`info`, `output_fields`, ...) | replacement |
| J02 | E | join without `label` | |
| J03 | A | join without `description` | |
| J04 | E | `ingredients` missing, empty, not `{dataset_id}` items, unknown id, repeated id | |
| J05 | E | `right_ingredient` not in the join's ingredients; `on` and `left_on` both or neither | |
| J06 | E | `final_contract` not a mapping, or names a column the collection lacks | |
| J07 | E | a join's `steps` is a flat list or `[]`, or has no `tier1` | `{tier1: [...]}` |
| J08 | E | a column name in both ingredients of a join, not a join key: the engine renames the second `name_right` silently (needs the recipe graph) | the message names both tables and the column; rename or drop one before the join (`rename`, `drop_columns`) |
| G01 | E | group without `label`; unknown key | |
| G02 | A | group without `description` | |
| P01 | E | plot entry without `label` or `spec`; unknown key (`info`) | `description` |
| P02 | A | plot without `description` | |
| P03 | E | plot id not snake_case | |
| P04 | E | `steps` at the plot entry holds anything but `tier3` | |
| PS01 | E | unknown spec key | replacement |
| PS02 | E | `target_dataset` missing or unknown | |
| PS03 | E | `mapping` or `layers` missing; no geom/stat layer | |
| PS04 | E | layer without `name`; unknown component; argument unknown to the component's schema **and** to the wrapped plotnine function | did-you-mean |
| PS05 | E | `theme` not a registered theme | |
| D01 | E | unknown `plot_defaults` key | |
| X1-X7 | E | the rules of section 10 | |
| CM01 | E | `comment` is not text | |
| GP01-GP05 | E | gallery profile rules (section 9) | defined with the gallery decision |

The data check (a dataset that cannot be built, an `output_fields` slug with no column) is **not** in this table: it needs the data and stays separate (`validate_data_analysis_recipe_data`).

## 12. Renamed and removed: the replacement table

Refused at once; the message names the new form. Mechanism: `utils/legacy_keys.py` (three dictionaries today, `legacy_keys.py:9-16`) grows to a table keyed by path and old key; the checker reads it only to write "use X". Nothing is converted silently `[DECIDED]`.

| Where | Old | New |
|---|---|---|
| `info` | `display_name` | `label` |
| top level | (no `spec_version`: format 0) | `spec_version: 1` and the replacements of this table, by `migrate_recipe_format.py` |
| top level | `description` | `info.description` |
| top level | `name`, `pipeline_id` | `info.label`, `id` |
| top level | `metadata` | `metadata_schema` |
| top level | `plots`, `wrangling`, `input_fields`, `output_fields` | inside a group / inside a schema |
| top level | `type`, `join_manifests` | removed / `joins` |
| schema | `info` (`category`, `sub_category`, `comment`) | `category`, `sub_category`, `comment` directly on the schema |
| schema | `fields` | `input_fields` |
| schema | `id` (inside the schema) | removed (the key is the id) |
| field | `is_primary_key` | `is_entity_key` |
| field | `source_name` | `original_name` |
| field | `type: string`, `character` | `categorical` or `utf8` |
| field | `type: int`, `integer`, `float`, `i64`, `Int64`, `Float64`, `String`, `Date`, `Categorical` | `numeric`, `categorical`, `date` |
| field | `type: bool`, `Boolean` | `boolean` |
| step | `column`, `source`, `source_column`, `target_column` (where the schema says `columns`) | `columns` |
| step | `how` on `join_filter` | removed (always inner) |
| join | `info` (sentence) | `description` |
| join | `output_fields` | `final_contract` |
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
| Schema | **the grain** ("one row is ..."), the unit and how many (rows and units), what the recipe already removed (with the threshold), how missing values are treated |
| Join | the grain of the result, the tables and the join type, whether rows multiply (one-to-many), what is removed |
| Group | the question the plots of the group answer |
| Plot | what is drawn and what is counted ("n of N"), which subset it leaves out, how a missing value is drawn |

Three kinds of "nothing" are never mixed: **not detected** (analysed, no hit: a real zero), **not analysed** (missing), **undeterminable** (a category such as "unknown"). The description says which of them the table holds. Numbers (rows, units) come from the data, not from memory.

**Write a description as a folded block** (`description: >-` then the text on the next lines): a plain text that contains a colon followed by a space is a YAML error and the recipe does not load (found twice while drafting the ST22 recipe; the checker reports it as T01 with the line). Descriptions describe the table **as it is**; a known defect or a planned change is named with `REVISE` and the issue, never hidden.

## 14. Where the checker and the rules live (verified 2026-11-13)

**The design.**

- **Core** `utils.recipe_check.check_recipe(raw, profile, *, catalogs=None, graph=None) -> Result(problems, coverage)`. Pure. The rules are read from a packaged data file in `libs/utils` (D3, O1). The catalogs (`actions`, `components`, `themes`, and the allowed argument names of each component) are **injected**; the recipe graph (`utils.recipe_graph`) is injected for the checks of columns per node.
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
| `rules_test_lab.md` 2c: a primitive needed by two domain libraries goes to `libs/utils` | the same reason |
| ADR-094: HOME's gate lives in the app layer "on purpose" because only that layer may combine utils and transformer | stays true: the adapter combines them, only the rule set moves down; ADR-094 gets an "amended by" note |
| `rules_code_quality.md` 1: no emoji in docstrings, comments, raised messages | the gallery icons in the data file are allowed; messages name terms, never icons |
| `workspace_standard.md` 5-E: every new module and rule file carries a `@deps` block | to do with the module and the data file |

**Packaging condition** (verified by building two wheels of a copy of `utils`): the container installs the libraries **non-editable** (`assets/containers/Dockerfile:72-81`). Without `[tool.setuptools.package-data]` a YAML file inside `src/utils/` is silently **absent from the wheel**. No library ships a data file today, so `utils` is the first: declare `package-data` and add a test that builds the wheel and reads the file. (The Dockerfile also lists `libs/generator_utils` on line 79, a folder that no longer exists, and no `blueprint_arch`, `test_lab` or `id_reconciliation`; it is not ready and nothing is deployed: `DOCKER-RELEASE-1`.)

**Things that may move to `utils`** (a note; nothing is moved, there is no overview yet; `UTILS-REUSE-REVIEW-1`): (1) the type vocabulary (`MetadataValidator.DTYPE_MAP`, the ingestor cast, the upload path: decided to be read in one place); (2) the plot-spec key sets `_CANONICAL_SPEC_KEYS` and `_VALID_PLOT_DEFAULTS_KEYS` (`plot_config_resolver.py:64-74`), which are facts about the format; (3) reading a step container, written four times (`DataWrangler._resolve_tier`, `tier2_steps` in `cache_keys.py:90`, `_step_blocks` of the validator, inline in the orchestrator); (4) the shape of a `ui_schema`, described by identical docstrings in two registries and read by `blueprint_arch.schema_registry` and `help_registry`; (5) two mechanisms for renamed keys (`utils/legacy_keys.py`, `app/modules/renamed_keys.py`); (6) `extract_primary_keys` and the lineage helpers of `blueprint_arch` (to `utils.recipe_graph`, decided). What stays: the actions and components themselves, the `@category` selector, anything that needs Polars data or plotnine.

**One name to align with the HOME stage-2 draft** (O4): it writes `check_recipe(raw, mode)` with `mode` = `run` or `build`; this file writes `profile`.

**How this file spreads once confirmed** (each rule gets one home):

| Part | Home | Why there |
|---|---|---|
| the normative rules in short | `.claude/rules/rules_data_analysis_recipe_structure.md` (changed only with Eve's double confirmation) | the agents' authority |
| the reference with one example per element | `docs/appendix/data_analysis_recipe_structure.yaml` and `Standards_yaml.qmd` | what a recipe maker reads |
| the checks as executable rules | `libs/utils` (`check_recipe`) and its tests, one test per row of section 11 | the code is the proof |
| how to write a description | the user guide and Blueprint's help | recipe makers |
| the text of the error messages | generated from the check table, not typed twice | no drift |

This file then becomes history (marked HISTORICAL, `rules_legacy_management.md`) and points to those homes.

## 15. What the code accepts today and must stop accepting

All are compatibility defaults under P2. Each is removed by the issue named (#76 checker and loader, #77 and #86 engine fixes, #78 migration and writers); a test per line.

| Where | What it tolerates | Removed with |
|---|---|---|
| `config_loader.py:18-41,136` | unquoted `on:` repaired with a printed warning | #76 (T07) |
| `config_loader.py:77-97` | fragment wrapper key removed silently | #76 (F01) |
| `config_loader.py` (PyYAML `SafeLoader`) | a repeated key keeps the last silently | #76 (T10): a loader that raises on a duplicate key |
| `config_loader.py:141-211` | judges content: structure, renamed keys, source; only part of the rules | #76 (moves to `check_recipe`) |
| `data_wrangler.py:60-61` | an empty `wrangling` of any shape means "no steps" | #76 (S06) |
| `data_wrangler.py:132-147` | six spellings of the column selector, guessed and written back into the step | #76 (ST03). 14 steps in 10 recipe files rely on it today. No ADR decided the aliases (ADR-034 is the diagnostic message) |
| `cleaning/core.py:126`, `reshaping/core.py:202,205` | `rename` reads `target_column`; `split_column` reads `source`, `target_column`, `separator` | #76, #78 (ST03; section 8 R2) |
| `ingestor.py:80-92,107` | fuzzy file search by dataset name; `fields` alias | #76 |
| `metadata_validator.py:21-37,118` | type aliases; `source_name` | #76 |
| `orchestrator.py:59-62` | `final_contract` as a list skipped; missing columns printed | #76 (J06) |
| `orchestrator.py:151-157` | a repeated schema id replaces the first | #76 (S02) |
| `orchestrator.py:173,214-216,198-206,224` | bare ingredient; first join as fallback; all schemas as ingredients | #76 (J04) |
| `cache_keys.py:90`, `orchestrator.py` (Path A) | a schema's own tier-2 ignored; the key ignores the order of `final_contract` | #77, #86 |
| `home_theater.py:1119,903` | group label falls back to `description`; reads `info.display_name` | #78 |
| `blueprint_mapper.py:76-77` | node label from `display_name`, `sub_category`, or `description[:35]` | #78 |
| `plot_config_resolver.py:234-236` | non-canonical spec keys moved to `_meta` and kept | #76 (PS01); `_meta` is retired and replaced by declared keys (`comment`, `taxonomy`); ADR-083 sections 2 and 6 to amend |
| `bootstrapper.py:154`, `scaffolder.py:182`, `create_data_analysis_recipe.py:177`, `blueprint_handlers.py:2670` | write `display_name` / `name` | #78 |


## 16. Tests that come out of this file (written first; they fail on today's code)

- One small invalid recipe per row of section 11: HOME refuses it, Blueprint reports it, the message holds the fix. A shared helper builds a minimal valid recipe so each test changes one thing.
- One test per row of section 12: the old form is refused and the message names the new one.
- One test per row of section 15: the tolerated form is now refused (mutation check: put the tolerance back and the test fails).
- Every shipped recipe of every kind in section 3 passes `check_recipe` with zero errors and zero advice (the retest scenarios with exactly their one planned fault). It replaces the recipe-folder test, the template test and the hygiene test, which become views of the same check.
- Shape tests (`TEST-SHAPES-1`): the shipped recipes as fixtures for no join, no key, another key name, no population table, long format.
- **Registries (section 8):** AR2 to AR6 and the plotnine argument test.
- **Container forms (5):** one test per refused form (a list where a dictionary belongs and the reverse, a bare string field, a flat `steps`, a wrapper key); a duplicate key is found by the loader; a `final_contract` list is refused instead of skipped; after migration the `demo_abromics` plots still render with their 5-column contract.
- **Order and ids (5, 7.5):** the key order of `final_contract` is the column order after load, run and write, in T1 **and** T2 (fails today, #86); groups and plots keep their tab order; the hash changes when the order of steps changes and does not change when an `id` or a `comment` changes; a repeated or non-text `id` is refused; an app-inserted step has an `audit_` id; the copy minus the marked steps equals the original; a scan test requires `sort_keys=False` for every `yaml.dump` and `safe_dump` of non-test code.
- **Messages with the correction (5.1):** for each container-form check the message contains the generated corrected text; HOME's gate, Blueprint's Validate and the import screen show the same message.
- **Types (7.4):** a table of declared type to resulting dtype, run through the ingestor for every type of the vocabulary (including digits declared as text); each refused name gives a message that quotes the meanings; no list of types exists in code (a grep test).
- **Format version:** one test per V01 to V04; every shipped recipe, template, gallery example, written recipe and forked recipe carries `spec_version: 1`; `effective_run.yaml` records it.
- **Migration tool:** a format-0 recipe (from the git history of the ST22 recipe) becomes a recipe that passes the checker with advices only; running it twice changes nothing; every `#` comment is kept; the list of manual steps is printed.
- **Comments:** a recipe with `#` comments passes untouched; every writer (Blueprint save, bootstrapper, scaffolder, the migration) keeps the comments of a fragment it edits (a before/after text comparison).
- **Gallery protection:** the committed `gallery_index.json` equals the index rebuilt from the bundles; a bundle written by `GalleryManager.submit_example` (with a `tier3` list) passes the checker; every bundle renders its preview through the app path; every taxonomy term is in the vocabulary; the tag strip of each `example_meta.md` equals `taxonomy`.
- The tests that encode superseded behaviour are listed first (`TEST-ADAPT-1`): `test_empty_wrangling_is_valid` (`wrangling: []`), `test_tiered_steps_is_valid` and the other tests with inline recipes (no engines), the template and folder tests.

## 17. Errors from a data-science point of view (not format errors)

The format makes a recipe readable and checkable; it does not make it right. Eve's rule: those errors are fixed, not documented.

| Recipe | Known errors | Status |
|---|---|---|
| `1_test_data_ST22_dummy` | R1 `ST22_Anchor` joins two long tables (617 rows for 42 samples, `virulence_count` wrong for 18); R2 samples with only unknown phenotypes scored 0 (4 of 42); R3 the MLST plot shows 33 of 42 samples without saying so; R4 `virulence_variants` unreadable (16 panels) and coloured by a constant of the resistance table | agreed 2026-11-12; issues #67, #69, #70; task `RECIPE-ST22-FIX-1`; done **before** the ST22 descriptions are finalised, so they describe the corrected tables |
| the other pipelines (Abromics, `demo_abromics`, `figshare_integration`, `stress_test_master`, `2_` and `3_` ST22) | not reviewed one by one: Abromics was scanned (its one row-multiplying join, MLST by VirulenceFinder, is one-to-many and expected) but its plots were not looked at | a data-scientist pass per recipe (grain, joins and row counts, missing values, every picture) as part of its migration, #78 |
| templates, retest, gallery, transformer test recipes | not reviewed | gallery: every preview is looked at when regenerated; test recipes: their tests have raw-file oracles |

What the checker can catch of these (structure only): an ignored key (#66), an unknown parameter, a join that multiplies rows (#68, an advice with rows before and after). It cannot decide that a score of 0 for "unknown" is wrong; that stays the data scientist's review.
