# What is BUILT today: recipe format, export and report, names

Branch `dev`. Read only; no tracked file was changed. Nothing was run (the agent had no shell). Claims are "read" (read at that place) or "grep" (found by search and not read in full). Each entry: what the app does | file:line (function) | reachable | status in the code | ledger numbers cited there.

Evidence labels used below: **read** = read at that line; **grep** = matched by search only.

## Header: files read (line counts where known)

- `libs/utils/src/utils/recipe_spec.yaml` (216 lines, read in full)
- `libs/utils/src/utils/recipe_check.py` (1325 lines; read: 1-260, 176-200, 309-460, 510-563, 567-590, 689-720, 814-871, 1089-1168, 1287-1325; grep for every check code)
- `libs/utils/src/utils/recipe_factory.py` (216 lines, read in full)
- `libs/utils/src/utils/recipe_loader.py` (127 lines, read in full)
- `libs/utils/src/utils/legacy_keys.py` (58 lines, read in full)
- `libs/utils/src/utils/config_loader.py` (read 100-270; the rest grep)
- `app/modules/renamed_keys.py` (246 lines, read in full)
- `app/modules/data_analysis_recipe_validator.py` (read 285-320, 402-435; rest grep)
- `app/handlers/export_handlers.py` (about 2350 lines; read 55-80, 372-400, 572-600, 1000-1150, 1480-1500 (grep), 1555-1700, 1930-2000; grep for every writer, heading and text)
- `app/assets/report_template.qmd` (106 lines, read in full)
- `app/modules/bundle_importer.py` (read 120-200; header and grep for the rest)
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py` (read 1-50; grep for the rest)
- `app/modules/data_analysis_recipe_info.py` (43 lines, read in full)
- `app/handlers/home_theater.py` (grep for the names; read 1135-1160 by grep)
- `app/src/bootloader.py` (read 396-445 partly; grep for names)
- `assets/scripts/migrate_display_names.py` (read 1-48 in full; the rules are in its docstring; the rest grep)
- `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml` (shape only, by grep on keys)
- `.claude/knowledge/decision_ledger.md` (grep for the names and format lines 400-535; the file was not run through `decision_ledger.py`)
- Rule files: `rules_data_analysis_recipe_structure.md`, `rules_data_engine.md`, `ui_implementation_contract.md`, `rules_viz_factory.md` (grep for the DECIDED / PROVISIONAL / not built / not decided tags, read in context)

Not present: `app/modules/exporter.py`. A glob for `**/exporter.py` under the repository found nothing. The word "exporter" appears only in `app/tests/test_dataset_lookup_one.py` (grep, not read). Nothing in the app imports a module of that name.

Privacy note: the demo recipe's `info.contact` line holds a personal contact. It is not copied here.

---

## 1. The recipe format as the code accepts it today

### 1.1 Two checks run on every recipe, and two loaders

1. `libs/utils/src/utils/recipe_loader.py:113-126` `check_recipe_file`: reads the file with the strict loader (`load_recipe`, 60-106), then calls `check_recipe` (1316-1324). Reading refusals: T01 (not YAML or unreadable), T02 (`!include` target missing), T10 (duplicate key), T11 (include outside the project), T07 (unquoted `on` read as a boolean key, 45-49), F01 (an included file that starts with the key it is included under, 50-52). Reachable: the data analysis recipe validator (`app/modules/data_analysis_recipe_validator.py:272-274`, 326-331).
2. `libs/utils/src/utils/config_loader.py` (class ConfigManager, read 100-270): the engine loader. Its own structural refusals: root `plots:` (179-191, message "Root-level 'plots:' key is not a valid authoring format"), missing `analysis_groups` (193-205), `data_schemas` not a mapping (207-216), a schema without `source` (231-242). It then flattens plots (248-254). It does not read `spec_version`.
3. HOME load gate, read: `app/modules/data_analysis_recipe_validator.py:402-414` `validate_data_analysis_recipe`: first `checker_problems(path, profile)` (check_recipe, profile "run"); only if that is empty, `engine_load_problems` (417-, which calls ConfigManager, 430, and checks that `id` equals the file name, 437-443).
4. BLUEPRINT: `app/modules/data_analysis_recipe_validator.py:296-311` `uploaded_recipe_report`: whole recipes go through `check_recipe` in the given profile (default "build"); fragments through `_fragment_report`. Advice lines are never blocking.
5. Legacy keys of a file, read: `libs/utils/src/utils/legacy_keys.py:9-16` (`join_manifests` -> `joins`; join key `recipe` -> `steps`; top-level `type` removed); refused in `config_loader.py:176` via `renamed_data_analysis_recipe_file_key_errors` (25-57).

Profiles of `check_recipe` (recipe_check.py:61): `run`, `build`, `gallery`, `audit`. Callers (grep): `run` in the load gate and in `assets/scripts/create_data_analysis_recipe.py:213`; `gallery` in `libs/viz_gallery/.../gallery_manager.py:250` and `assets/scripts/convert_gallery_examples.py:155`; `build` is the default of `uploaded_recipe_report`. **No production caller passes `profile="audit"`** (grep, non-test files). The audit profile is reached only by tests.

### 1.2 Top level (`recipe_spec.yaml:21-24`, checker 237-261)

- Required in the spec: `id, spec_version, data_engine, plot_engine, info, data_schemas, analysis_groups`. Optional: `entity, additional_datasets_schemas, metadata_schema, joins, plot_defaults`.
- The checker raises T04 for each missing required key (`top_level`, 242-244) but skips `spec_version` there; a missing `spec_version` gives V01 ("old format 0") instead (`version`, 248-252).
- `id` must equal the file name: T05 (246). The loader also checks this (`engine_load_problems`, data_analysis_recipe_validator.py:439-443).
- Any other top-level key: T03 via `unknown_keys` (241), with the "renamed" text when the key is in the renamed map (`recipe_spec.yaml:84-95`: `plots`, `wrangling`, `input_fields`, `output_fields`, `final_contract`, `name`, `pipeline_id`, `description`, `metadata`, `type`, `join_manifests`).
- `plots` at the root: T08 (239-240) and the loader refusal (config_loader.py:179-191). Read.
- Engine values: `data_engine` / `plot_engine` are checked against `utils/engines.py` (T06, `engine_value` 266-275). Not read in detail: engines.py.

### 1.3 `info` (checker `info()`, 309-324)

- `info` is declared `required: []`, `free_form: true` (`recipe_spec.yaml:25-28`). The checker never calls `unknown_keys` for `info` (grep: `free_form` appears only in the spec file; no code reads it). **So `info` accepts any key without a message.** Read: 309-324 has no unknown-key loop.
- The label key is required: I01 when `info.label` is missing (318). `label_keys.info: label` (`recipe_spec.yaml:13-17`). The file comment says the choice between `label` and `ui_label` is PENDING (lines 9-12).
- `info.display_name` refused with the renamed text (I03, 315-316).
- `info.description` and `info.contact` missing: advice I02 (321-323). `info.description` with an open bracket: advice D01 (326-330).
- Read by the app: `info` is shown as lines by `app/modules/data_analysis_recipe_info.py:18-36` (every key, nested keys too; no key is special).

### 1.4 Data schemas (`schemas()` 360-384, `schema()` 386-417)

- Sections accepted: `data_schemas`, `additional_datasets_schemas`, and `metadata_schema` (a reserved id, S02 if used as a schema id, 373-374 and 381-384). Duplicate schema ids across sections: S02 (376).
- A schema is a mapping. Allowed keys (spec `schema`): required `source, null_values, strip, input_fields, tier1`; optional `description, comment, tier2`; plus the label key (`label`, `label_keys.schema`, PENDING per the spec file). Any other key: S01 via `unknown_keys` (390). `wrangling` on a schema: S06 with the old-shape text (`old_shapes.schema.wrangling`, `recipe_spec.yaml:133-134`).
- **Does a source table hold a step list of its own?** No bare `steps`. It holds `tier1` (required, S06 if missing, `tiers` 523-524) and `tier2` (optional). A `steps` key on a schema is an unknown key (S01). Read: 386-417, 512-532.
- `tier2` of a schema applies only when the schema is plotted directly. If no plot reads the schema, S07 says the steps "would run nowhere" (414-417). Read.
- `label` (S03 if missing, 391-392); `description` missing: advice S04 (393-394).
- `input_fields` must be a mapping (S08, 401-405); each field is checked by `field()` (472-508): FD01 (a field is a mapping), FD02 (type missing or not a text-storable Polars dtype), FD03/FD04 (`is_primary_key`, `source_name`), FD05 (a parameter that does not belong to the type, `is_entity_key` not true/false), FD06 (a bare string).
- `source` (`source()` 419-433): `type` must be in `elements.source.types` = `local_tsv`, `local_parquet` (S05, `recipe_spec.yaml:35-38`). `path` required; `dev_path` checks the shape (PA01) and containment in the allowed roots (PA02, 435-443), with `base` the project root.
- Entity key: an `is_entity_key` field must not be numeric: E03 (`entity_key_type` 445-459). Read.
- Null values and strip: `missing_values` (461-470), S09.

### 1.5 Tiers and steps (`tiers()` 512-532, `tier()` 534-563, `steps()` 689-740)

- A tier is its own key, a mapping with `steps` (required) and `data_engine` (optional). Any other key inside a tier is refused (`tier()` 543-550). `tier1` / `tier2` / `tier3` written inside another tier is refused with a rewrite pointer (546-548).
- **Flat list refused:** a tier written as a list gets the message "written as a mapping with steps, not as a list (the form of the recipe changed)" (537-540). Code of the message: the code of the element (S06 for schemas, J07 for joins, P04 for plots).
- A tier with no `steps` key: the code of the element with "has no steps" (555-557). `steps` not a list: "steps is a list of steps" (559-561).
- Per step: `steps()` 689-740: a step is a mapping with `action` (ST01, 696-697); action must be registered (ST02, 733); tier-1-only actions outside tier 1 (ST05, 715); id and audit fields refused in the author's steps (ST08, 703-709; and an `audit_comment` in an author's step is AU01, 709-711). Parameters: ST06, ST10, ST12 (column problems in the engine's plan), ST03/ST04 region not read.
- Advice: ST13 (position action after a step with no stated order, 649-674), ST14 (top_k / bottom_k ties, 634-647), ST15 (32-bit sum, 592-632). All advice, never blocking.
- **`tier3` on a plot entry** is accepted: `plot()` 1137-1139 calls `tiers(plot, path, "P04", ... "plot")`; the spec lists `tier3` as optional in `plot` (`recipe_spec.yaml:51-57`) and `tiers.plot: [tier3]` (`recipe_spec.yaml:72-75`). Read. The comment at 1138 says the engine reads `tier3` (`DataOrchestrator.materialize_tier3`).

### 1.6 Audit steps (`audit_list` 676-687, `audit_step_keys` 567-590)

- `audit_steps` (a second list in a tier) and `audit_comment` (on each step): legal only when the profile is `audit`. Anywhere else: AU01, "only an audit recipe has audit steps ... an author never does" (680-683). Read. In a non-audit recipe the list content is not read.
- In an `audit` profile: each audit step needs an allowed action (AU02, 570-572; allowed list `AUDIT_ACTIONS` = filter, column drop, removal by key), an audit id `audit_<8 hex>_<k>` used once (AU03, 580-586), and a non-empty `audit_comment` (AU03, 587-590). A drop of a join key still used later is AU04, via `utils.key_drop` (573-579).
- The codes AU01 to AU03 are new and not in the spec's error catalogue (comment at recipe_check.py:565-566; "PROVISIONAL wording").
- `info.audit_of`: **grep finds no reader or refusal of `audit_of` in `libs/utils/src` or `app`.** Because `info` is free-form (section 1.3), a recipe with `info.audit_of` is accepted silently in every profile. The design (`recipe_format_spec.md:374`) says this key is "DECIDED, not built" and "refused in every other recipe" (D-0354).
- The audit copy in memory (`libs/utils/src/utils/audit_copy.py`, read by grep only): adds steps to `audit_steps` of a tier, with ids and `audit_comment`. Callers: `app/modules/plan_composer.py:369` (grep). Not read in full.

### 1.7 Joins (`joins()` 814-851, `ingredients()` 853-871, `join_steps` 873-, `join_columns` 1059-1088)

- A join is a mapping: `label` (J02 if missing), `ingredients` (required, list of `{dataset_id: <schema id>}`, at least one, J04), `tier1` (required, J07 via `tiers`), `tier2` (optional), `description` (advice J03), `labels` (J06: a mapping of column to text), `comment`.
- **Ingredients: only schemas of this recipe.** Read: `ingredients()` 866-867 refuses any id that is not in `schema_ids` ("is not a schema of this recipe"). So **a join cannot take another join or a derived table as an ingredient.** A join id that equals a schema id is X1 (830).
- Join keys: J05 (keys must be names or lists of names; `on` must be quoted, T07 at 892), J09 (key types differ), J10 (key not declared in input_fields), J11 (length differs), J13 (advice: float key), J12 (advice: a join of a table with itself, or a right table not yet in the chain). J08 (a column check per node, needs the graph). Read: 884-1088 partly (grep for codes).
- Tier 2 of a join: applies only when a plot reads the join. J14 otherwise (826-828). Read.
- `labels` of a join: the code writes them to the join as `labels: {column: text}` (`recipe_factory.py:108-109`, and check J06).
- The published columns of a join are its last `polars_select` (decided, D-0034 per the spec text; the checker refuses `output_fields` and `final_contract` on a join through the renamed map, `recipe_spec.yaml:109-113`, code J01 via `unknown_keys` 834). Read.

### 1.8 Groups and plot entries (`groups()` 1089-1118, `plot()` 1120-1143, `plot_content()` 1145-1168, `layers()` 1170-1218)

- Group: `ui_label` required (G01; `group` required `ui_label, plots`), optional `ui_title`, `description`, `comment` (`recipe_spec.yaml:45-47`). A group with no description: advice G02. A group `label` is refused with the text "renamed ui_label" (`recipe_spec.yaml:114-115`) via `unknown_keys` (G01, 1102). Read.
- `ui_title` on a group is **accepted** by the checker (spec optional key). See section 3.
- T09: a `run` recipe needs at least one plot (1117-1118).
- Plot id: snake_case (P03, 1122-1123). `plot` entry: `ui_label` required (P01, 1128-1129; a plot `label` is refused as renamed, 1128-1129 and `spec.renamed.plot`); `description` advice P02; `comment` CM01; `plot_engine` T06/EN02; `taxonomy` a mapping (P01, 1140-1141).
- The content: `target_dataset` must be a schema or join of this recipe (PS02, 1148-1149); `mapping` and `layers` required (PS03, 1150-1151); `layers` a list (PS03, 1155-1156); `facet_by` must be a plain column name (PS06, 1157-1161); `theme` must be a registered theme (PS05, 1162-1166); `filters` on a plot refused: "moved to the plot's tier3" (P06, 1167-1168).
- The key `spec` in a plot: refused through `unknown_keys` (P01, 1127) with the old-shape text (`recipe_spec.yaml:137-140`); plot content is not checked when `spec` is present (1142-1143).
- A plot-level `steps`: P04 (old shape, `unknown_keys` shape_codes at 1127).
- `factory_id`: no code mention (grep found none in `libs/utils/src`). A plot with `factory_id` is refused as an unknown key (P01), with a close-match suggestion, not with the DEPRECATED text of the rule file.
- Layers (`layers()` 1170-1218): a layer is `{name, params, comment}`; `name` must be a registered component (PS04, 1197); params must be arguments of the component (PS04, 1215; plotnine note 108-117); `random_state` must be a whole number (PS04 1210; PD01 1240), null or the word `random` refused (S1, 1207-1209, PROVISIONAL marked in code). A recipe with no geom or stat layer: PS03 (1218).
- Names of components: registry in `utils/...` (`checker_catalogs`), not read.

### 1.9 `plot_defaults` (`plot_defaults()` 1220-1249)

- Allowed keys (spec `plot_defaults`): `palette, theme, layers, random_state`. Unknown: PD01. The four removed keys (`default_font_family`, `facet_panel_spacing`, `legend_position`, `optimisation`) are refused with the tombstone text (PD02, `recipe_spec.yaml:145-163`). Also `height` and `show_legend` (renamed map, 125-127). Read.
- `random_state` must be a whole number (PD01, 1240). `theme` as in plots. `layers` a list (PS03, 1248).

### 1.10 Gallery profile (`gallery()` 1251-1285)

- One group with one plot (GP01), id equal to the example folder (GP04), taxonomy with the 5 axes (GP02, gallery terms in the spec 188-215), data path of the example is its own `example_data.tsv` (GP06), companion files present (GP05). Read by the spec.

### 1.11 Whole-set rule

- `check_recipe_set` (1287-1300): a plot id must be unique across all recipes (X5). Read.

### 1.12 Check codes (one line each; from grep and read)

| Code | What it refuses or advises (the message stem) | Where |
|---|---|---|
| T01 | recipe is not a mapping; (loader) not YAML | 215; loader 105 |
| T02 | include target not found (loader) | loader 82 |
| T03 | unknown top-level key (renamed text when renamed) | 241 |
| T04 | required top-level key missing | 244 |
| T05 | `id` differs from file name | 246 |
| T06 | engine value is not an engine of this app | 274 |
| T07 | unquoted `on` read as boolean | loader 47; 892 |
| T08 | root-level `plots` | 240 |
| T09 | run profile needs a group with a plot | 1118 |
| T10 | duplicate key (loader) | loader 103 |
| T11 | include outside the project (loader) | loader 76 |
| F01 | included file starts with the key it is included under (loader) | loader 51 |
| V01 | no `spec_version`: old format 0 | 251 |
| V02 / V03 | format number lower / higher than the app reads | 257, 259 |
| V04 | `spec_version` not an integer | 255 |
| EN02 | step or layer in a block of another engine | 306 |
| EN03 | registry gives no engine for a registered name (app fault) | 302 |
| I01 | `info` not a mapping, or label missing | 313, 318 |
| I02 | advice: info description or contact missing | 323 |
| I03 | `info.display_name` renamed | 316 |
| CM01 | comment is not text | many |
| D01 | advice: description seems cut (open bracket) | 329 |
| E01 / E02 / E03 | entity block: form; population not a table or no key field; numeric entity key | 337-348; 456 |
| S01 | schema or section not a mapping, or unknown schema key (incl. `steps`) | 369, 388, 390 |
| S02 | reserved id, or id used twice | 374, 376 |
| S03 | schema has no label | 392 |
| S04 | advice: schema has no description | 394 |
| S05 | source: missing, not a mapping, type not built, path missing | 421-431 |
| S06 | old `wrangling` key, or tier not a mapping with steps | 390, 538 |
| S07 | tier2 of a schema that no plot reads (steps run nowhere) | 415 |
| S08 | input_fields missing or not a mapping | 402-404 |
| S09 | null_values / strip wrong form | 468-470 |
| PA01 / PA02 | development path shape / outside allowed roots | 439, 443 |
| FD01-FD06 | field form, type missing or not storable, parameters | 477-508 |
| E03 | numeric entity key | 456 |
| ST01 | step not a mapping with `action` | 697, 719 |
| ST02 | action not registered (with a suggestion) | 733 |
| ST05 | tier-1-only action outside tier 1 | 715 |
| ST06 | step parameter problem | 765 |
| ST08 | author step has an id, or audit id in author's list | 704-707 |
| ST10 | parameter type (named in code only) | 613 (comment) |
| ST12 | a column the engine's plan does not find | 811 |
| ST13 | advice: position action after an unstated order | 668 |
| ST14 | advice: top_k / bottom_k ties | 640 |
| ST15 | advice: sum on a 32-bit column | 625 |
| AU01 | audit list or audit_comment outside an audit recipe | 681, 709 |
| AU02 | audit action not an allowed audit action | 571 |
| AU03 | audit id missing, repeated, or no reason | 582-589 |
| AU04 | drop of a key that a later join needs (by place) | 579 |
| X1 | join id equal to a schema id | 830 |
| X5 | plot id used in two recipes | recipe_check.py 1296 |
| J01 | join not a mapping, or unknown key (renamed text) | 819, 832, 834 |
| J02 | join has no label | 836 |
| J03 | advice: join has no description | 838 |
| J04 | ingredients: form, or not a schema of this recipe, or twice | 855-869 |
| J05 | join step key form (`on` / `left_on` / `right_on`, right_ingredient) | 884-896 |
| J06 | labels not a column-to-text mapping | 850 |
| J07 | join tier as a list or missing steps | via `tiers` 843 |
| J08 | column of a join step not in the graph (needs graph) | 1083 |
| J09 | join key types differ | 1041 |
| J10 | join key not declared in input_fields | 1034 |
| J11 | key lists differ in length | 998 |
| J12 | advice: join of a table with itself, or right table not yet in the chain | 920 |
| J13 | advice: float join key | 946 |
| J14 | tier2 of a join no plot reads | 826 |
| G01 | group form, missing ui_label, plots form, or a renamed key | 1094-1112 |
| G02 | advice: group has no description | 1106 |
| T09 | no group with a plot (run profile) | 1118 |
| P01 | plot not a mapping, ui_label missing, unknown key (`spec`, `label`, `taxonomy` form) | 1125-1141 |
| P02 | advice: plot has no description | 1131 |
| P03 | plot id not snake_case | 1123 |
| P04 | plot-level or tier3 step problem; plot `steps` refused | 1139, 1127 |
| P06 | `filters` on a plot | 1168 |
| PS02 | target_dataset not a schema or join | 1149 |
| PS03 | mapping or layers missing, layers not a list, no geom | 1151, 1156, 1218 |
| PS04 | layer: form, unknown component, argument not known, random_state form | 1178-1215 |
| PS05 | theme not a registered theme | 1165 |
| PS06 | facet variable not a plain column name; random params | 1160, 1189 |
| PD01 | plot_defaults: not a mapping, unknown key, random_state form | 1225-1240 |
| PD02 | removed plot_defaults key (tombstone) | 1231 |
| GP01-GP06 | gallery example rules | 1256-1284 |
| S1 / S3 (seed) | a seed is a number (PROVISIONAL marked in code) | 1207, 1236 |

Codes that the checker reads from elsewhere: J08 and X7 need the recipe graph (docstring 11-12). Not read in full: the bodies of `join_steps` (873-898), `join_key_problems` (984-1045), `join_columns` (1059-1088), `steps` parameter checks (742-812), `filter_value_problems` (767-812), `plot_content` layers (1170-1218 partly).

### 1.13 Writers (`recipe_factory.py`)

- `minimal_schema` writes `label` (line 82), `source`, `null_values`, `strip`, `input_fields`, `tier1: {steps: []}`, optional `tier2` (65-91). `minimal_join` writes `label` (102), `ingredients`, `tier1`, optional `tier2`, `labels` (94-110). `minimal_plot` writes `ui_label` (121), `target_dataset`, `mapping`, `layers` (default a bar chart), optional `tier3` (113-128). `minimal_recipe` writes `id`, `spec_version`, `data_engine`, `plot_engine` (taken from `utils/engines.py`), `info: {label}`, `data_schemas`, `joins`, `analysis_groups` with group `main` and `ui_label: Main` (131-170). `write_recipe` refuses an `id` that is not the file stem (196-202). Read in full.
- The writers therefore produce `label` for schemas, joins, fields (no `ui_label`) and `ui_label` for groups and plots. This is the state that the PENDING note in the spec describes.

### 1.14 The demo recipe, shape only (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`, grep of keys)

- Top: `id`, `spec_version: 1`, `data_engine`, `plot_engine`, `info` (keys `label`, `contact`, `subtitle`, `category`, `description`, `version`), `data_schemas` (about 10 schemas, each with `label`, `description`, `source`, `null_values`, `strip`, `input_fields`, `tier1` as an inline mapping or an `!include` of a file that holds `steps`; some with `tier2: {steps: []}`), `additional_datasets_schemas` (2), `metadata_schema` (a top-level key with `source`, `input_fields`, `tier1`), `joins` (about 17 joins, each with `tier1` and `tier2` fragments), `analysis_groups` (groups with `ui_label`, plots by `!include` of one file per plot). The file has no `final_contract`, no `output_fields`, no root `plots:`, no `spec:` in a plot.
- Keys used by the demo that the checker reads as free: everything under `info` (section 1.3).

### 1.15 What a recipe may not contain, read in the code

| Word | What the code does | Where |
|---|---|---|
| `final_contract` | refused: top T03 (renamed text), join J01, schema S01 | `recipe_spec.yaml:89,112`; `recipe_check.py:241`, 834, 390 |
| `output_fields` | refused like `final_contract`, on schema S01 and join J01 | `recipe_spec.yaml:88,102,111`; `config_loader.py:121` (comment: not unwrapped) |
| `spec` on a plot | refused P01 with the old-shape text ("write the content ... directly"); content not checked | `recipe_check.py:1127, 1142`; `recipe_spec.yaml:137-138` |
| flat tier list | refused (S06 / J07 / P04: "not as a list") | `recipe_check.py:537-540` |
| root `plots:` | refused T08 (checker) and config_loader:179 (engine loader) | `recipe_check.py:240`; `config_loader.py:179-191` |
| root `wrangling` / `input_fields` | refused T03 (renamed text) | `recipe_spec.yaml:86-87` |
| `from:` | refused as unknown key (T03 top, S01 schema, J01 join, P01 plot, G01 group) with a close-match suggestion | `unknown_keys` 179-196 |
| `results` (a table result) | refused as unknown key (same places). Not built: no code reads a result entry. Grep of `libs` and `app`: no `table_result`, `result_entry` or `kind: table`. | grep |
| derived table / table of a table | refused: a join takes only schemas (J04, 866-867); a schema has no steps of its own (S01) | `recipe_check.py:866-867, 390` |
| `audit_steps` | legal only in an audit recipe (AU01 elsewhere); no production caller passes profile `audit` | `recipe_check.py:680-683`; grep |
| `audit_comment` | refused in an author's step (AU01); in an audit recipe required (AU03) | `recipe_check.py:709-711, 587-590` |
| `info.audit_of` | NOT refused, NOT read (info is free-form) | `recipe_spec.yaml:25-28`; grep (no reader) |
| `factory_id` | no special refusal; refused as an unknown plot key (P01) | `recipe_check.py:1127` |
| `label` on a group | refused (G01, renamed text "renamed ui_label") | `recipe_spec.yaml:114-115`; `recipe_check.py:1102` |
| `label` on a plot | refused (P01 renamed text) | `recipe_spec.yaml:116-118`; `recipe_check.py:1128-1129` |
| `label` on a schema, join, field | ACCEPTED as the name key (`label_keys`, PENDING in the spec) | `recipe_spec.yaml:13-17`; `recipe_check.py:182, 317-318, 391-392, 835-836` |
| `ui_label` on a schema, join, field | refused: not in the known keys of those elements (unknown key, S01 / J01 / FD) | `recipe_check.py:182`; spec `schema`, `join`, `field` |
| `ui_title` on a group or plot | ACCEPTED by the checker (group optional; plot optional) | `recipe_spec.yaml:47, 53` |
| `ui_title` on a plot is read by the report | yes, first (see section 3) | `export_handlers.py:390` |
| `display_name` on info | refused I03 | `recipe_check.py:316` |
| `type` at top level | refused (legacy_keys REMOVED) | `legacy_keys.py:13-16` |
| `join_manifests` / join `recipe` | refused (legacy_keys RENAMED) | `legacy_keys.py:9-10` |
| `dataset_id` as a join key | refused: the key is `right_ingredient` (J05 unknown key: the form in `join_steps` 884-890) | recipe_check (not read in full) |
| `factory_id` in the rule file is marked DEPRECATED with a removal task | the rule file says "Engine raises PipelineError when `factory_id` is present"; the checker raises P01 instead | `rules_data_analysis_recipe_structure.md:172` vs `recipe_check.py:1127` |

---

## 2. The export bundle and the report

### 2.1 Entry point and the refusals before anything is written

- Entry: `app/handlers/export_handlers.py:967` `export_bundle_download` (async, `@render.download`), inside `define_export_server` (599).
- Recipe read: `safe_input(input, "data_analysis_recipe_id", ...)` (1005), keys from `orchestrator.compute_data_analysis_recipe_keys` (1010), and `export_refusal` for an unreadable recipe (1012-1017).
- Key check (EXPORT-KEYCHECK-1): `changed_since_view` (251-270) compares the recipe file set hash and the data batch hash, and the Tier 1 key of each table in scope (`_scope_tables_now`, 1025-1030). If anything changed: `blocked_export_notice` (278-312) builds the text, a notification is shown with "Reload the page (F5)", and the download is `blocked_export_zip` (314-319): a zip with ONE file, `EXPORT_NOT_CREATED.txt` (1030-1038). Read.
- Build-time change: `_on_build_change` (1040-1046) collects changes while tables are built; `refusal_for_build_changes` (322-331) gives the same refusal.
- Audit preflight (PLOT-TABLE-ORDER-1): `audit_failures` over every plot (1129); on failure a zip with `EXPORT_NOT_CREATED.txt` made of `blocked_audit_notice` (334-341) and a notification (1117-1138). Read.
- Scope: every export holds ALL plots of the recipe (1058 comment; README line 2233 "all plots of the recipe are exported"). **There is no `export_scope` value in the app code** (grep: `export_scope` appears only in three test files). The three-way scope toggle of the rule file (`ui_implementation_contract.md` 7.2) is not built.
- Export inputs read: `export_user_name` (993, used as the bundle label, 224), `export_preset` (997), `export_plot_format` (998), `export_report_format` (999), `export_include_reproducibility` (1059), plot width and height (1000-1001), and the Export panel's button text "💾 Export Bundle" (line 780). The rule file says "📦 Export Bundle" (7.2). Two names for the button text.
- The bundle folder name: `bundle_dir = f"{ts}_{safe_name}"` (1152). The zip has a top folder named `<timestamp>_<label>`. The rule file (7.2) puts the files at the top of the zip with `data/` and `plots/`.
- The file name: `_export_bundle_filename` (2339-2346): `<YYYYMMDD_HHMMSS>_<label>_results.zip`, label sanitised to 40 characters. This matches the rule file.

### 2.2 What the zip holds (every writer, read)

Paths are relative to the bundle folder `<timestamp>_<label>/`.

| Path | Written by | Condition | Error form |
|---|---|---|---|
| `<ds>/plots/<plot_id>.<fmt>` | 1334 | every plot; format from the panel (SVG default, D-0294 per the docstring at 974) | `<ds>/plots/<plot_id>_ERROR.txt` (1358) |
| `<ds>/T1_data.tsv` | 1409 | every table a plot reads | `<ds>/T1_data_ERROR.txt` (1413) |
| `<ds>/T2_data.tsv` | 1431 | only when `tier2_steps` of the target table is non-empty (1419) | `<ds>/T2_data_ERROR.txt` (1436) |
| `<ds>/T3_data_<plot>.tsv` | 1467 | a plot with audited steps or with `tier3` steps of the recipe (`t3_table_plots`, 1115) | `<ds>/T3_data_<plot>_ERROR.txt` (1472) |
| `<table>/T1_data.tsv` for tables no plot reads | 1501 | `tables_no_plot_reads` (61-74); PROVISIONAL (see 2.9) | `T1_data_ERROR.txt` (1506) |
| `t3_steps.yaml` | 1541 (bundle root) | when T3 has active audited nodes (`_t3_by_plot`, 1075-1083) | `t3_steps_ERROR.txt` (1546) |
| `data_analysis_recipes_reproducibility/<id>.yaml` | 1569 | ONLY when the box "Also include a reproducibility/reimport bundle" is ticked (`wants_mode2`, 1059) | `data_analysis_recipes_reproducibility/ERROR.txt` (1625) |
| `data_reproducibility/<ds><suffix>` (the actual data files) | 1580 | same condition | `data_reproducibility/<ds>_ERROR.txt` (1587) |
| `effective_run.yaml` | 1688 | ALWAYS | none |
| `lineage/lineage_graph.json` | 1791 | when the recipe's lineage can be built (1695-1800) | `lineage/lineage_graph_ERROR.txt` (1798) |
| `report.qmd` | 2112 | always | none |
| `report.<html|pdf|docx>` | 2146 | when Quarto renders (`_render/` in a temp dir, 2121-2146) | `report_RENDER_FAILED.txt` (2154) and a note in README (2165) |
| `README.txt` | 2311 | always | none |
| `EXPORT_NOT_CREATED.txt` (only zip) | 318, 1136 | key check or audit preflight failed | — |

Notes:
- The plots are drawn into the zip with `zf.writestr` (1334), and report figures link to `_render/<plot>.<ext>` (398, 400), a folder that exists only while Quarto renders (comment 349-352).
- The lineage DAG is in `lineage/`, not in `data_analysis_recipes/`.
- Plot provenance inside the image: PNG and SVG metadata with `sparmvet:data_analysis_recipe_sha256`, `sparmvet:data_batch_hash`, `sparmvet:decision_hash`, `sparmvet:tier2_key` (`_embed_png_provenance` 404-438, `_embed_svg_provenance` 440-470).

### 2.3 The audit inside the export, today

- Mode 1 (always): the audited steps are applied in memory with `audited_frame` (`app/modules/t3_audit_engine.py`, imported at export_handlers.py:40) to the plot's table, both in the plot's data (1299) and in the T3 file (1463). The steps come from `home_state` key `t3_audit_steps_by_plot` with the prefix `subtab_<plot_id>` (1102-1105, 1081, 1087). Only nodes with `active` not false are used (1081). Read.
- Mode 1 also writes `t3_steps.yaml` (1516-1542): `t3_steps` per plot, and `t3_aesthetic_overrides` when present (1539). Read.
- The "copy that writes the audit steps into a copy of a join's tier 2": it exists ONLY in Mode 2. `libs/blueprint_arch/src/blueprint_arch/t3_translator.py` (header lines 3-16, 30-41) builds, per plot, a FORK of the join the plot reads: the fork's `tier2` is the original `tier2` followed by the translated steps, with a `comment` naming the source join (`_fork_comment` 189-194; the fork is written at 277-278). The export calls `build_mode2_recipe(cfg.raw_config, _t3_by_plot)` (1564) and writes the result to `data_analysis_recipes_reproducibility/` (1569). The header says this is to be replaced "by the audit copy of the HOME design" (lines 36-38).
- The in-memory audit copy in `libs/utils/src/utils/audit_copy.py` (read by grep) is a different path: it adds `audit_steps` lists (see 1.6). Its callers in the export: none (grep: `audit_copy` does not appear in `export_handlers.py`).
- Reshuffle seeds: `with_seed_steps` adds the seed pin to the audit list (1093) and the seed plan (1069-1072) goes into `effective_run.yaml`. Read.

### 2.4 The reproducibility bundle (Mode 2) and its status texts

- Built only when the box is ticked (1559-1633). Status: `built`, `incomplete` (a data file could not be copied), `failed` (the whole part failed). The README line (2220-2232) reads "requested ... but NOT built" when failed; "included but INCOMPLETE" when incomplete; "included" otherwise; "not included" when the box was not ticked.
- Texts shown to the user: notification with "This reproducibility bundle includes your actual raw data files, not just hashes — anyone who gets the bundle gets the data. If it contains sensitive information, anonymise it before sharing" (1604-1612, duration 12); warning when the T3 steps could not be baked in (1613-1622); failure notice (1629-1633): "do not use it to re-run the analysis". The code comment at 1574 says "Sensitive-data handling is #46, not built here."
- `effective_run.yaml` `t3_translation_skipped` holds the skipped plots (1681-1685); when the box is not ticked it says "not attempted".

### 2.5 `effective_run.yaml` (1649-1690): what it holds

Keys: `generated`, `data_analysis_recipe_sha256`, `data_batch_hash`, `t3_audit_steps_sha256`, `engine_fingerprint`, `containerized`, `image_ref`, `uv_lock_sha256`, `git_commit`, `release_version`, `contact`, `contact_source`, `software_versions`, `data_source_paths`, `engines` (engine record of each tier and plot, D-0248), `seeds_per_plot`, `seed_source_per_plot`, `seeds_per_layer`, `seeds_added_to_recipe`, `plot_warnings`, `plot_warnings_unreadable`, `t3_translation_skipped`. Its `_about` text says it is "Written identically by Publication and Reproducibility exports". Read.

### 2.6 Provenance hashes (`build_export_provenance` 77-249)

Computed fields (read 77-250 partly, names read at 231-247): `data_analysis_recipe_sha256`, `data_batch_hash`, `decision_hashes` (a name kept from an earlier design; filled from `stage_keys` tier1 keys at 171-175, or from Parquet metadata `get_parquet_metadata_hash` at 178-188), `stage_keys` (per dataset: `tier1_key`, `tier2_key`), `plot_keys` (plot tier3 keys), `t3_audit_steps_sha256` (196), `engine_fingerprint`, `containerized`, `image_ref`, `git_commit`, `uv_lock_sha256` (213-214), `release_version`, `software_versions`, `data_source_paths`, `bundle_label`, `app_features`, `preset`, `dpi`, `plot_width`, `plot_height`, `screen_view`, `tiers_exported`, `plot_count`.

### 2.7 `exported_tiers` and the README/report tier lists

`exported_tiers` (55-58): `T1` always, `T2` when a table has tier-2 keys, `T3` when `t3_table_plots` is non-empty. Read.

### 2.8 `report.qmd` (written in code at 1813-2112; no template file is used)

Front matter (1813-1822): `title: "Results Report — <data analysis recipe id>"`, `format:` with `toc-title: "Contents"`. Then, in this order, with heading levels:

1. `## Overview` (1836)
2. `## Dataset → Plot Mapping` (1843)
3. `## Provenance` (1888) with a table of keys (tier 1 and tier 2 keys per dataset, 1853-1881; "Decision hash" rows at 1875 read "sparmvet_decision_hash" from Parquet metadata)
4. `## About the data in this report` (1906) with a fixed text for T1, T2, T3 (1913-1914)
5. `## Methods` (566, built by `_build_methods_section`, inserted at 1918-1925; a level-2 heading)
6. `## Plots` (1930) with one `### <plot label>` per plot (`plot_report_lines` 393-401)
7. `## Data files` (1939) with `### <dataset>` per dataset; links to T1, T2, T3 files (1946-1971)
8. `### Tables that no plot reads` (1976), a level-3 heading inside `## Data files` (PROVISIONAL, D-0457)
9. `## T3 Audit Trail` (1989) with `### <plot label>` and a table Step / Action / Details / Justification (1994-2010)
10. `## Processing Issues During Session` (2018)
11. `## Data Lineage` (2038) with `### Lineage Step Summary` (2075) and a note about `lineage/lineage_graph.json` (2091)
12. `## Random scatter seeds` (2100) when seeds exist
13. A closing `---` (2102) and the provenance note (2105-2108)

The report's figure references use `_render/<plot>.<ext>` (398). It is rendered by Quarto (2121-2158) into `report.html` (or the chosen report format).

Not in the code's report: the rule file's sections "Study Context", "Data Summary", "Figures", "Appendix: Decisions Considered and Discarded", "Raw audit steps" (rule file `ui_implementation_contract.md` 12f). These headings are in `app/assets/report_template.qmd` (see 2.10), which no code loads.

### 2.9 Tables that no plot reads (D-0457)

- `tables_no_plot_reads` (61-74): every source table (data schema, metadata, additional dataset) and every join that no plot targets directly. PROVISIONAL (docstring 68-70). Its T1 file is written (1501) and the README and report name it (1973-1984, 2167-2175). The text "These tables are read by no plot of this recipe: their Tier 1 data is in the bundle, no figure is drawn from them." (2170) is PROVISIONAL (comment 1973, "PROVISIONAL wording (not decided)").

### 2.10 `app/assets/report_template.qmd` (106 lines, read)

A Quarto template with a YAML header titled "SPARMVET Audit Report", params `data_analysis_recipe_id`, `data_analysis_recipe_sha256`, `t3_audit_steps_sha256`, `deployment`, `export_timestamp`, and sections: `## Study Context`, `## Data Summary`, `## Methods`, `## Figures`, `## Appendix: Decisions Considered and Discarded` (text: "The following nodes were created but deactivated before export"), `## Raw audit steps (Active Nodes)`. It reads `report_data.json`.
- **No `.py` file loads this template** (grep for `report_template`: only `app/tests/test_writers_emit_format_one.py:364` lists its path, and `rules_app_structure.md:81` names it).
- **No `.py` file writes `report_data.json`** (grep). The appendix's "deactivated" nodes can not occur in the app today (see 2.11).
- The template is dead. The rule file `ui_implementation_contract.md` 12f describes this template's sections as the report spec.

### 2.11 Deactivated nodes

`_t3_by_plot` keeps nodes with `active` not false (1081). Nothing sets `active` to false (`ui_implementation_contract.md` 12c says the same: "not yet built, F-07"). The "deactivated" appendix therefore has no source in the app.

### 2.12 Import of a bundle (`app/modules/bundle_importer.py`)

- Entry from the Export panel: `_handle_import_bundle_upload` (export_handlers.py:888) and `import_bundle_report` (920). `import_bundle` (bundle_importer.py:199) reads `effective_run.yaml` (204-209) and the reproducibility recipe under `data_analysis_recipes_reproducibility/` (221-229); a bundle without it is refused with a text that says what is missing.
- It writes the recipe into `bootloader.data_analysis_recipes_dir` (252) and creates a session ghost (`SessionManager`, 296-311). It "never touches live app state" (200-201).
- Verification legs (`_verify`, 120-196): `data` (the data batch hash is recomputed and compared, 129-135); `engine` (engine fingerprint and git commit compared, 137-155); `recipe` (compared with the original recipe found locally by id, 157-184; "not_checked" when none is found, with the reason text 173-184 that the copy has baked-in steps and seeds); `t3_steps` (always "not_checked", 186-194: the text says the audited steps exist only in the exporting session).
- So the import checks the data, the engine and the recipe where it can, and never checks the T3 steps.

### 2.13 `app/modules/exporter.py`

Not present. See the header.

### 2.14 Two ways of doing one thing, export

- Two copies of the audit into a recipe: (a) Mode 1, in memory with `audited_frame` (1299, 1463); (b) Mode 2, a plot-private fork of the join (`t3_translator.py:197-278`). Both are reached from `export_bundle_download`. The rule file (7.2) says the second one is "replaces today's export copy" (DECIDED, not built).
- Reproducibility folder names: code `data_analysis_recipes_reproducibility/` and `data_reproducibility/` (1569, 1580). Rule file 7.2 table: `data_analysis_recipes/<proj>/`. Rule file 7.2 also: `data_analysis_recipes/t3_steps.yaml`; code: `t3_steps.yaml` at the bundle root (1541).
- Data folders: code `<dataset>/T1_data.tsv` etc. (1409, 1431); rule file 7.2 table: `data/<ds>_T1.tsv` and `data/<ds>_T2.tsv`. The rule file also says `<ds>/T3_data_<plot>.tsv` (matches code).
- Decision hash vs tier keys: code writes the tier keys as "Stage keys" (README 2259-2260, `stage_keys`) and keeps the older name `decision_hashes` as a fallback (README 2186-2203; `_embed_png_provenance` 421, `_embed_svg_provenance` 457, report 1875-1881). Two names for one value, both still in the bundle texts.
- Plot title in the report: `plot_report_name` reads `ui_title` first, then `ui_label` (390). The checker accepts `ui_title` on groups and plots (section 1.8). The migration plan removes it (section 3). Two readings in the code.
- Report template: the code writes the report itself (1813-2112); `report_template.qmd` is dead.
- Bundle top folder: `<timestamp>_<label>/` (1152) versus files at the top of the zip (rule file 7.2).
- Export of an audit: the rule file says the recipe is written with the audit steps as the recipe that produced the figures (DECIDED, not built). The code writes the in-memory audited tables and, in Mode 2 only, a fork of the join.
- Load of a recipe: ConfigManager (legacy structure) and `check_recipe` (strict) both run in the load gate (data_analysis_recipe_validator.py:402-414).

### 2.15 Decided and not built, export and report (rule files)

- `ui_implementation_contract.md` 7.2 (line 193): DECIDED, not built (D-0324, D-0333, D-0315, D-0345, D-0478): when audit steps exist, the export holds the audit recipe; the original may be added as the baseline; an audit record with the hash of the audit recipe beside it; the README says in one sentence which file is which; the audit log is always in the bundle beside the audit recipe; no tick. Also: "The old name `decision_hash` is retired with the bundle texts when the export of an audit is built." (193)
- 7.2 rule 7 (line 196): "Tables that no plot reads (D-0457; built, the reading is PROVISIONAL)" and "NOT decided and not built: how the user reaches such a table in HOME's data preview".
- 7.2 Export UI controls (lines 183-186 region): the three-way scope toggle `export_scope` (global / group / plot) and the "Active group" option. Not in the code (section 2.1).
- 7.2 "Deferred": per-plot checkbox selection; server-side write to Location 4 (deferred, not decided).
- 7.1 (line 153): DECIDED, not built: the audit log written in the session (D-0315) and exported with the audit recipe, warnings at each choice (D-0478); the audit recipe and audit record in an audit folder inside the session folder (D-0319, D-0340, D-0333).
- 12f (line 616 onwards): no DECIDED tag in the section, but the content (report sections, template) does not match the code (see 2.8, 2.10). It also names a node type `developer_raw_yaml` in the Methods rules; `renamed_keys.py:184-186` says that type was removed (AUDIT-RAWYAML-REMOVE-1).
- 12g.4 (line 725): DECIDED, not built: the Create audit step dialog (not in the export; HOME side).
- `rules_data_engine.md` section 1 (line 36): "The opening of a recipe (DECIDED, not built)" (D-0326, D-0335, D-0343) and the not-decided numbers (D-0336).

---

## 3. The names

### 3.1 Where each display name is read today

| Name | Reading place (file:line) | What is shown | Status in the code |
|---|---|---|---|
| recipe `info.label` | `app/handlers/home_theater.py:1144` (banner title, as fallback after app features `ui_title.text`) | the title of the HOME banner | read; the checker requires `info.label` (`recipe_check.py:317-318`) |
| recipe `info` (all keys) | `app/modules/data_analysis_recipe_info.py:18-36` | the Info panel: every key as a line, nested keys indented | read |
| recipe `info.subtitle` | `home_theater.py:1148` (banner subtitle) | the subtitle under the title | read; D-0482 says HOME stops reading it (not built) |
| recipe `info.name`, `info.ui_title` | nowhere (free-form `info`, `recipe_check.py:309-324`) | shown in the Info panel as plain lines | accepted silently |
| recipe `info.display_name` | refused (`recipe_check.py:315-316`) | refusal text | read |
| group `ui_label` | `home_theater.py:104-106` `group_tab_label`: `ui_label`, else `description`, else the group id | the group tab | read; the checker requires `ui_label` (`recipe_check.py:1103-1104`) |
| group `ui_title` | no reader in the app (grep: only the checker accepts it, `recipe_spec.yaml:47`) | nothing | accepted, not read |
| group `label` | refused (G01, renamed text, `recipe_check.py:1102`) | refusal | read |
| plot `ui_label` | `home_theater.py:109-111` `plot_tab_label` (else the id in title case); `home_theater.py:114-116` `plot_list_label` (audit dialogs); `export_handlers.py:390` (report, after `ui_title`) | the plot tab, the lists, the report | read |
| plot `ui_title` | `export_handlers.py:390` (first in the report) | the report name of the plot | read by the report; the checker accepts it (`recipe_spec.yaml:53`) |
| plot figure title | the `title` argument of the `labs` layer (not read in the name path; `export_handlers.py:388` comment) | the title inside the picture | by design (D-0253) |
| table `label` (schema) | `recipe_check.py:391-392` (required); `app/modules/wrangle_studio.py:873, 901` (`schema.get("label", k)`, the Blueprint picker) | the Blueprint picker; lineage node label `export_handlers.py:1723` from `navigator` | read; spec `label_keys.schema: label` (PENDING, `recipe_spec.yaml:13-17`) |
| join `label` | `recipe_check.py:835-836` (required); `recipe_factory.py:102` (writer) | (no HOME reader found in this read) | the checker requires it; spec PENDING |
| field `label` | `recipe_check.py:182` (accepted through `label_keys_of`) | (no reader found) | accepted |
| data analysis recipe selector | `home_theater.py:1935` (`available_data_analysis_recipes.keys()`); the keys are file stems (`bootloader.py:422-423`) | the selector shows the FILE NAME (recipe id), not `info.label` | read |
| deployment name | `app/src/bootloader.py:122` `deployment_name` with fallback "SPARMVET_VIZ (Local Dev)" | (where it is shown: not traced in this read) | read; D-0411 and D-0479 say it is removed (not built) |
| deployment banner title / subtitle | `app/src/ui.py:351-357` (`banner["title"]`, `["subtitle"]`); `bootloader.py:878` (`branding.banner`); `home_theater.py:1970-1977` | the banner in the sidebar and the top | read; D-0411 says `banner.title` becomes `ui_label` (not built) |
| deployment contact | `bootloader.py:591` (`branding.contact`) | contact in the rejected-recipe notice | read |
| app features display name | `bootloader.py:404-408` `display_name`, then `name`, then the file value | UI display | read; D-0480 says `display_name` becomes `ui_label`; D-0481 says `name` goes (both not built) |
| app features id | `app/modules/app_features_validator.py:79` and `sidebar_validator.py:54` (`template.get("name")`) | the id in messages | read |
| app features `ui_title` (`text`, `subtitle`, `visible`) | `home_theater.py:1138-1153` | the HOME title banner | read; D-0411 and D-0470 say it is removed (not built) |
| export bundle label | `export_handlers.py:993`, 2344 (`export_user_name`, default "user") | the bundle file name and the README line "User" | read |

### 3.2 `assets/scripts/migrate_display_names.py` (dry run, read in its docstring 1-48 and grep)

The script plans, does not write (`--apply` only on a copy; refuses the repository, exit 3). The rules it applies, with the ledger numbers it cites:

- Recipes and included files, Gallery bundles, templates, test fixtures: `info.label`, `info.name`, `info.ui_title` to `info.ui_label` (D-0410). Note: the script treats `info` keys, while the rule that the checker applies to `info` is that `label` stays the required key (section 1.3).
- `ui_title` of a group and of a plot entry: removed, its text printed (D-0409, D-0410). The text of a removed group `ui_title` is kept nowhere: an OPEN case (OC16), printed with the `ui_label` beside it. The text of a removed plot `ui_title` is compared with the `labs` title (D-0484): same (OC20, decided), differs (OC18, both printed), none (OC19).
- `label` of tables, joins and input fields to `ui_label` (D-0468).
- Deployment files: `branding.banner.title` to `ui_label`, `branding.banner.subtitle` to `description` (D-0411). `deployment_name` removed, with a comment block at the top of each file (D-0411, D-0479). The comment form is PROVISIONAL (D-0479).
- App features files: the top-level key `name` removed (D-0481; only that key). `ui_title {text, subtitle, visible}` removed, printed (D-0411, D-0470). A `visible: false` moves to the deployment key `branding.show_recipe_name: false` (D-0472, D-0474), only where exactly one deployment names that file (BANNER_SWITCH_KEY).
- Not decided, listed and never changed: the banner switch in ambiguous cases, a name with no place to go, `info.subtitle`, the Gallery generator (script docstring 26-28).
- Code places that read `deployment_name` are listed, not changed (32).

Dry-run result: not run here.

### 3.3 Old keys refused today (`app/modules/renamed_keys.py`, read in full)

- Environment variables: `SPARMVET_PERSONA` -> `SPARMVET_APP_FEATURES`; `SPARMVET_PROFILE` -> `SPARMVET_DEPLOYMENT`; `SPARMVET_CONNECTOR` removed (10-14, 76-93).
- Deployment keys: `default_persona`, `default_manifest`, `prefer_discovery`, `data_ingestion_enabled` (17-22, 96-119). Locations: `curated_data`, `user_sessions`, `manifests` (25-29).
- App features top keys: `persona_id` -> `name`, `features` -> `flags`, `manifest_selector` -> `data_analysis_recipe_selector`, `theme_css`, `ui_banner` -> `branding` (32-38, 122-166). Selector keys `fixed_data_analysis_recipe`, `fixed_manifest` (134-144).
- Flags: `show_persona_badge`, `manifest_edit_enabled` (41-44); retired `wrangle_studio_enabled`, `developer_mode_enabled` (47-50).
- App features names: `project-independent` -> `standalone` (53-55). Panel types: `project_info` -> `data_analysis_recipe_info` (58-60).
- Session keys: `manifest_id`, `manifest_sha256`, `t3_recipe`, `t3_recipe_by_plot`, `t3_recipe_sha256` (63-69, 169-176).
- Audit step types: `developer_raw_yaml` refused as removed (185-187, 204-205); a step with an unknown type or missing parts refused (195-234).
- Recipe keys: section 1.15 (`legacy_keys.py`).
- Not refused by `renamed_keys.py`: the names `display_name` (app features), `name` (app features, read), `deployment_name`, banner `title`/`subtitle`, `ui_title` of app features (read), `info.name`, `info.ui_title`.

### 3.4 Names: where the decisions and the code disagree (for the design agent; no proposal here)

1. D-0253 (2026-11-18): the report name is `ui_title` when given, else `ui_label` (rule file `rules_data_analysis_recipe_structure.md` section 8 and spec `recipe_spec.yaml:53`). Code: `export_handlers.py:390` reads `ui_title` first. Ledger D-0409 (line 443 of the ledger) and D-0484: `ui_title` removed from the report; the ledger line 443 says "(ui_title no longer used by the report); D-0253 is not edited". So the rule file and the code disagree with the decision of 2026-11-21/22.
2. The label key of schemas, joins and fields: `recipe_spec.yaml:9-17` says PENDING (`label` or `ui_label`); D-0468 (2026-11-22) says `label` becomes `ui_label`. The checker requires `label` (`recipe_check.py:317, 391, 835`). The recipe factory writes `label` (`recipe_factory.py:82, 102`).
3. `deployment_name`: D-0411/D-0479 say removed; code reads it at `bootloader.py:122`.
4. App features `display_name` and `name`: D-0480 and D-0481 say `ui_label` and removal; code reads `display_name` then `name` (`bootloader.py:404-408`); `sidebar_validator.py:54` and `app_features_validator.py:79` read `name`.
5. Recipe banner subtitle: D-0482 says HOME stops reading `info.subtitle`; code reads it (`home_theater.py:1148`).
6. App features `ui_title` (text, subtitle, visible): D-0411/D-0470 say removed; code reads it (`home_theater.py:1140-1147`).
7. Deployment banner `title`/`subtitle`: D-0411 says `title` becomes `ui_label`; code reads `title` (`ui.py:351`, `home_theater.py:1976`).
8. The selector shows file stems (`bootloader.py:423`, `home_theater.py:1935`), not `info.label`. No decision read in this pass says which name the selector should show (not checked in the ledger).
9. Group label fallback: the code reads `ui_label`, then `description`, then the group id (`home_theater.py:104-106`); the spec requires `ui_label` (`recipe_check.py:1103-1104`). Two readings: the fallback is not in the checker.

### 3.5 Texts on screen about names that state a limit

- `EXPORT_READY_TEXTS` (export_handlers.py:580-583): "Getting ready ..." and "Your last change may not have been received..."; the comment says PROVISIONAL until Eve has read them (579).
- Migration texts are not on screen (dry run).

---

## 4. Rule files: DECIDED, not built, and PROVISIONAL (every statement with its section)

### `.claude/rules/rules_data_analysis_recipe_structure.md`
- Section 8, line 172: DEPRECATED (ADR-083) `factory_id`, removal task BP-PLOT-LEGACY-REMOVE-1. Code: refused as unknown key only (1.15).
- Section 11b, line 327: "Where a recipe fails (DECIDED, not built; D-0338, D-0342)": one function that names the place of a problem in the file and line. Not decided: D-0342 (the form of the sentence, the path of keys, the guard, how a problem met only when data is read names its place). "The line shown when the check itself fails is kept as built, provisional (D-0338)."
- Section 10 (plot_defaults): no tag; the four removed keys are refused (D-0220, D-0242). Code agrees (section 1.9).
- Section 1 to 7, 9, 12: no DECIDED or PROVISIONAL tag found by grep. Section 7 says "`final_contract` is removed" (D-0034) and the code agrees.

### `.claude/rules/rules_data_engine.md`
- Section 1, "The opening of a recipe (DECIDED, not built)" (line 36): build and store every tier 1 and tier 2 table and the tier 3 table of plots with their own steps at opening; draw each plot once as proof; progress line; warn on large plots; refuse a plot that cannot be drawn at opening (D-0326, D-0335, D-0343, D-0334, D-0336, D-0327). "Not decided": the number of rows that triggers the warning (D-0336). Code: "Today the tables are built when a plot first needs them" (the document says so).
- Section 1, Tier 3 "Handoff" and "Execution (built)": no tag.
- Sections 3 and 4: no DECIDED or PROVISIONAL tag found by grep. Section 3 says tiers are keys of their own (D-0250, built) and section 4 says the published columns are the last `polars_select` (D-0034, built).

### `.claude/rules/ui_implementation_contract.md`
Section 1 (header line 1): "what is decided but not built is marked 'DECIDED, not built'".
- Section 2 (line 57): DECIDED, not built: the audit step at T1 or T2, chosen by tick lines (D-0022, D-0316, D-0318, D-0337, D-0346, D-0347). Today audit steps are at T3 only (the strip says "for now").
- Section 2 (line 53): PROVISIONAL: the default of the data choice (T3; P-B1, `server.py:138-139`); the mode default is "not decided: PROVISIONAL".
- Section 2 (line 54): DECIDED D-0311 (exploration filters removed when the viewed table changes); PROVISIONAL: clearing on plot-tab change, mode switch, recipe change (`filter_and_audit_handlers.py:168-174`).
- Section 7.1 (line 153): DECIDED, not built: audit log in the session (D-0315; D-0478), audit recipe and record in an audit folder (D-0319, D-0340, D-0333).
- Section 7.2 (line 193): DECIDED, not built (D-0324, D-0333, D-0315, D-0345, D-0478): the audit recipe is the export of an audit; the baseline may be added; audit record with its hash; README sentence; the audit log always; no tick.
- Section 7.2 rule 7 (line 196): "built, the reading is PROVISIONAL" (D-0457); "NOT decided and not built": how the user reaches such a table in HOME's data preview, and the viewing of its tiers.
- Section 7.2 (lines 183-186 area, export controls): the 3-way scope toggle is described as built; not in the code (2.1). Deferred: per-plot checkbox, server-side write.
- Section 8 (lines 266-268): "Comparisons on text, date and true/false columns are not decided and not offered"; value box kind PROVISIONAL (the builder's choice; the typed value at a change of kind); "For the owner, not decided: ..." (line 268).
- Section 8 (line 286): "Wording of the new messages: PROVISIONAL." (the data import check).
- Section 9 (line 289): PROVISIONAL (the coordinator's choice) on a deployment with `data_lookup: by_dataset_id`; PROVISIONAL (an agent's choice) on recipes imported from a bundle. Line 294: "Provenance obligation (NOT built; waits for the owner, DATA-IMPORT-OVERWRITE)". Line 298: status, not built items. Line 287: converting a comma-separated or Excel file "NOT decided and is not built".
- Section 12 (line 440): DECIDED, not built (D-0322, D-0329, D-0332): the audit recipe check, the `audit_steps` and `audit_comment` keys (also 1.6 above; the keys are not read from a file yet, D-0354).
- Section 12 (line 452): the Plot Style panel not mounted (not a DECIDED tag; "not mounted ... for now").
- Section 12g.2 (line 694): DECIDED, not built as described (D-0313, D-0082): entity key and "columns used to join" are two lists; as built one list.
- Section 12g.3 (line 701): D-0448 decided 2026-11-21; "the mark PROVISIONAL in the code is to be removed when that code is next touched".
- Section 12g.4 (line 725): DECIDED, not built: the Create audit step dialog (D-0316, D-0318, D-0325, D-0337, D-0346, D-0347, D-0451); not decided: whether a table no plot reads is ticked when the dialog opens (D-0451); the rename across two tiers (no number).
- Section 12f (lines 616 onwards): no tag, content differs from the code (2.8, 2.10, 2.11).
- Section 13 (line 860): PROVISIONAL: the clearing of filters on a plot-tab change, mode switch or recipe change (`filter_and_audit_handlers.py:168-174`).

### `.claude/rules/rules_viz_factory.md`
- Section 1a (line 21): "Names of the plot components (DECIDED, not built yet)": the `plotnine_<name>` rename (D-0091, D-0210, D-0218). Line 23: "The rename is NOT built."
- Section 1a (line 36): not decided yet: how arguments and nested objects are passed (D-0218).
- Section 1a (line 123, in section 7 cascade): "Names in the cascade (DECIDED, not built, D-0218)": the `theme:` key of a plot entry changes to a component call (D-0214).
- Section 8 (line 145): "The Reshuffle button ... offered only in Audit mode (D-0341; built). ... how a reshuffle is written down as an audit step ... is not decided (D-0341)."
- Section 1a: the list also says "Full parity: the 30 plotnine objects..." (D-0212) and "Both spellings of the 15 name pairs ..." (D-0213): DECIDED, no build tag.

---

## Two ways of doing one thing found

1. **Plot name in the report**: `ui_title` first (`export_handlers.py:390`), `ui_label` second; the checker accepts `ui_title` (`recipe_spec.yaml:47, 53`); the migration plan removes it (ledger D-0409, D-0484).
2. **Audit into the export, two copies**: in memory with `audited_frame` for every export (`export_handlers.py:1299, 1463`), and a plot-private fork of the join for the reproducibility bundle only (`t3_translator.py:197-278`; `export_handlers.py:1564`). Both are "the audit" in the bundle.
3. **Recipe label key**: `label` (required and written by the factory and read by the checker: `recipe_check.py:317, 391, 835`; `recipe_factory.py:82, 102`), and the group and plot key `ui_label` (`recipe_check.py:1103`, `recipe_factory.py:121`). Spec says PENDING; ledger D-0468 says `label` becomes `ui_label`.
4. **Two loaders for one recipe**: ConfigManager (`config_loader.py`, structural checks at 176-244 and the engine's flatten at 248-254) and `check_recipe` (strict; `data_analysis_recipe_validator.py:402-414` runs both, in order). A rule of one can be silent in the other: for example `spec_version` is required by the checker only through V01, not by ConfigManager.
5. **Data folder names**: `<dataset>/T1_data.tsv` (code, `export_handlers.py:1409`) versus `data/<ds>_T1.tsv` (rule file 7.2 table).
6. **Reproducibility folder names**: `data_analysis_recipes_reproducibility/` and `data_reproducibility/` (code, 1569, 1580) versus `data_analysis_recipes/` (rule file 7.2 table).
7. **`t3_steps.yaml` location**: bundle root (code, 1541) versus `data_analysis_recipes/t3_steps.yaml` (rule file 7.2 table).
8. **Stage key names**: `tier1_key` and `tier2_key` (code, README 2193-2194; export_handlers.py:1167-1174) versus `decision_hashes`, `sparmvet_decision_hash` (code, `export_handlers.py:171-188, 421, 457, 1875-1881, 2108, 2203`).
9. **Report template**: the code writes the report in code (1813-2112); `report_template.qmd` (106 lines) with other headings is not loaded by any code.
10. **Report title**: "Results Report — <id>" (code, 1814) versus "SPARMVET Audit Report" (template, and rule file 12f).
11. **Bundle top folder**: `<timestamp>_<label>/` (code, 1152) versus files at the top of the zip (rule file 7.2).
12. **Button text**: "💾 Export Bundle" (code, 780) versus "📦 Export Bundle" (rule file 7.2).
13. **Name of the app title**: app features `ui_title.text` (home_theater.py:1140-1147), then recipe `info.label` (1144), then nothing; the deployment banner `title` (ui.py:351). Three sources for one banner.
14. **Two kinds of plot list name**: `plot_tab_label` (ui_label, else title case, 109-111) and `plot_list_label` (ui_label, else `name`, else id, 114-116). The `name` key of a plot entry is not in the spec.
15. **Group label**: `ui_label`, else `description`, else id (`home_theater.py:104-106`) versus `ui_label` required (`recipe_check.py:1103-1104`).

## Texts on screen that state a limit

- `export_handlers.py:2170` "These tables are read by no plot of this recipe: their Tier 1 data is in the bundle, no figure is drawn from them." (PROVISIONAL, 1973)
- `export_handlers.py:2233` "Plots: N (all plots of the recipe are exported)": the scope is always all plots.
- `export_handlers.py:2223` "Reproducibility: requested ... but NOT built; the reason is in data_analysis_recipes_reproducibility/ERROR.txt".
- `export_handlers.py:2268` "Audited T3 steps (always applied to the plot and its data):".
- `export_handlers.py:1914` (T3 row of the report's "About the data" table): "Only audited steps are exported: filters tried while exploring are never included."
- `export_handlers.py:1604-1612`: "This reproducibility bundle includes your actual raw data files ... If it contains sensitive information, anonymise it before sharing".
- `export_handlers.py:1629-1633`: "do not use it to re-run the analysis" (the reproducibility part failed).
- `export_handlers.py:278-312`: EXPORT_NOT_CREATED.txt text: what changed, "reload with F5", the keys of both views.
- `export_handlers.py:580-583`: EXPORT_READY_TEXTS (PROVISIONAL, 579).
- `bundle_importer.py:176-194`: the "not_checked" texts (recipe leg and T3 leg).
- `recipe_check.py` advice texts starting with "Suggestion:" and "Warning:" (ST14 at 641, ST15 at 629, J12, J13) are advice, not blocking.
- `recipe_check.py:565-566` comment: "PROVISIONAL wording" for AU01 to AU03 and ST08.
- `renamed_keys.py:192` FIX text: "start a new session from the recipe ..." (for a refused audit step).
- `export_handlers.py:2305-2309` README: "Only audited steps are exported; exploration filters never are."

## Not read / could not tell

- `libs/utils/src/utils/recipe_check.py`: bodies of `join_steps` (873-898), `join_key_problems` (984-1045), `join_columns` (1059-1088), `steps` parameter checks (742-812), `filter_value_problems` (767-812), `formulas` (742-766), the layer checks in detail (1170-1218) and `checker_catalogs`. The list of codes in 1.12 is from grep plus the reads named there.
- `libs/utils/src/utils/recipe_spec.yaml` lines 1-216 read in full; `engines.py` not read.
- `app/handlers/export_handlers.py`: lines 77-250 (provenance, read partly by grep), 471-575 (Methods text, not read), 600-970 (the Export panel UI, read only by grep for the controls), 1150-1300 (plots, read partly), 1300-1420 (not read), 1500-1510 (grep), 1700-1800 (lineage build, not read), 2038-2110 (lineage and seeds report sections, grep), 2312-end (not read).
- `app/modules/bundle_importer.py`: 199-400 (the session writing and the verification of the session) not read in full.
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`: functions `translate_t3_node` (92-158), `build_mode2_recipe` body (197-278) read by grep only.
- `libs/utils/src/utils/audit_copy.py`: read by grep only.
- `app/src/bootloader.py`: `data_lookup`, `get_location` not read; the places where the deployment name is shown (the migration lists them; this read did not trace them).
- `app/handlers/home_theater.py`: the banner code at 1135-1160 read by grep only, and the plot and group labels at 96-117 read by grep only.
- `assets/scripts/migrate_display_names.py`: the code below line 48 not read (rules read in its docstring); no dry run was run.
- `.claude/knowledge/decision_ledger.md`: read by grep only (line numbers 265-535 and the names rows); `decision_ledger.py` not run (no shell). The wording of D-0253 at line 282 and of the names rows at 440-518 was read by grep output, cut at 150-320 characters.
- Whether `info.label` is shown in the Blueprint picker beyond the schema label: not traced.
- The engine registry and plot component names (`utils/engines.py`, `checker_catalogs`): not read.
- The four rule files: grep for the tags with context; sections not tagged were not read line by line.

## Five most important findings (one line each)

1. **`info` is free-form**: any key under `info` (for example `audit_of`, `name`, `ui_title`) is accepted without a message, and `info.audit_of` has no reader (`recipe_spec.yaml:25-28`, `recipe_check.py:309-324`).
2. **Two ways for the report name**: `export_handlers.py:390` reads `ui_title` first, the checker accepts `ui_title` on groups and plots, but ledger D-0409 and D-0484 say it is removed.
3. **Scope and export layout differ from the rule file**: the export always holds all plots (no `export_scope` in the app code), and the folder names differ from the rule file 7.2 table (`<dataset>/T1_data.tsv`, `data_analysis_recipes_reproducibility/`, root `t3_steps.yaml`).
4. **The audit in the export has two copies**: in-memory `audited_frame` always, and a plot-private join fork only in the reproducibility bundle (`t3_translator.py:197-278`, `export_handlers.py:1564`), with the "for now" note that the fork will be replaced.
5. **Label key for schemas, joins and fields is PENDING in the spec but DECIDED in D-0468**: the checker and factory still use `label` (`recipe_spec.yaml:9-17`, `recipe_check.py:317, 391, 835`), and the name readers (deployment, app features, banner, `info.subtitle`) still read the keys that D-0411, D-0480, D-0481 and D-0482 say to remove.

Also noted, not in the five: the report template `app/assets/report_template.qmd` is not loaded by any code; `app/modules/exporter.py` does not exist.
