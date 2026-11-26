FACTS: names, labels, titles and descriptions across the whole app (read-only survey, branch dev)

## 0. Scope and how to read this

- Read first, as ordered: `.claude/workflows/agent_principles.md`, `.claude/workflows/decision_compliance.md`, `tmpAI/panel/names_whole_app/ORDER.md`, `tmpAI/panel/name_fields/TABLE_FOR_THE_OWNER.md`. `tmp.md` was not read.
- VERIFIED = I read the line, or a search showed it, at the file:line given.
- NOT VERIFIED = not checked, or a claim I could not confirm. "Not found" means a search of `app/` (non-test files) or of the named folder found nothing. Test files are left out unless I say so.
- "Reasoned" marks an inference from what I read.
- Counts and lengths that the owner's table gives were not measured again by me.
- Each finding names the user space (HOME, BLUEPRINT, TEST_LAB, GALLERY) or the file kind (recipe, app features, deployment, sidebar YAML, session, Gallery index, export bundle, documentation).

Short forms used below: `home` = `app/handlers/home_theater.py`; `bp` = `app/handlers/blueprint_handlers.py`; `wrangle` = `app/modules/wrangle_studio.py`; `export` = `app/handlers/export_handlers.py`; `check` = `libs/utils/src/utils/recipe_check.py`; `spec` = `.claude/design/recipe_format_spec.md`; `rspec` = `libs/utils/src/utils/recipe_spec.yaml`; `taxonomy` = `libs/viz_gallery/src/viz_gallery/taxonomy.py`; `gmgr` = `libs/viz_gallery/src/viz_gallery/gallery_manager.py`; `ledger` = `.claude/knowledge/decision_ledger.md`.

---

## 1. Corrections to TABLE_FOR_THE_OWNER.md

C1. The table says HOME shows the contact message at `app/src/bootloader.py:624`. VERIFIED: the HOME message ("Contact: ...") is `app/handlers/recipe_gate_handlers.py:101`. `bootloader.py:618-626` is a startup stop message, shown to the operator when the recipe selector is hidden and the named recipe fails.

C2. The table says BLUEPRINT "new recipe" writes `info.label`. VERIFIED: `libs/blueprint_arch/src/blueprint_arch/new_recipe.py:27-28` (the docstring at line 22 says `label` was `info.name`). But the BLUEPRINT recipe Info form uses a different key, `info.name`: it shows it at `bp:2542` and `bp:2558`, and writes it at `bp:2609-2610`. The Info form's field is labelled "Name" with the placeholder "Short display name" (`bp:2571-2572`). This is missing from the table. See D1 below.

C3. The table's row for the app features title (`ui_title.text`) is right about the code: VERIFIED `home:1139-1144`. It is incomplete: no shipped app features file has a `ui_title` key (search of `config/app_features/`: none). The validator does not check it (`app/modules/app_features_validator.py`: no key list; search: no `ui_title`). `.claude/rules/rules_app_features_flags.md` does not mention it (search: none).

C4. The ledger line D-0387 (`ledger:421`) says the code reads `info.label` for the Gallery name at `gmgr:107`. VERIFIED: that is stale. The name is read from the plot's `ui_label` by `example_name` at `taxonomy:55-66` (`taxonomy:58` says `info.label` is not read there), and the index takes it at `gmgr:142`. `gmgr:107` is inside the docstring of `_repeats`. The table's section 3 item 6 already says this.

C5. The table's claim that the group `ui_title` is read by nothing: VERIFIED by search. The only reads of `ui_title` in `app/` are `export:373` (plot names in the report) and `home:1139` (app features). No group reader was found.

C6. The table's claim that the plot `ui_title` is read only by the export report: VERIFIED. `export:373` is the reader; its callers are `export:486`, `export:535`, `export:1870`, `export:1916`. Not found in HOME, Gallery or BLUEPRINT code.

C7. The table's claim that the Gallery name equals the plot `ui_label`: VERIFIED at `taxonomy:55-66`, `gmgr:142`, and `app/modules/gallery_listing.py:97` (the dropdown reads the registry `name`).

C8. Not checked by me: table rows citing `spec:367`, `spec:484-498`, `check:244-245`, `check:1102-1103`, `check:1127-1128`, `check:1256-1257`, `home:109-110`, `home:114-115`, `data_analysis_recipe_validator.py:58`, and the lengths. The `check` lines 316-317, 390-394, 834-837, 847-849, 1102-1103, 1127-1130 and `spec` lines 105, 179, 367, 484-498 were read in part; the rest are NOT VERIFIED.

C9. Ledger date conflict. VERIFIED: `spec:484` says `ui_label` was "renamed 2026-11-17, DEC52". The ledger line D-0253 (`ledger:282`) is dated 2026-11-18. Two dates for one rename: a record to reconcile (reasoned).

C10. Ledger status conflict. VERIFIED: D-0360 (`ledger:394`) is marked DECIDED, but its own text says the alias use is "a proposal, not a rule" and quotes Eve's question with "no ?". Rule H of `decision_compliance.md` asks that records that contradict be reported. Reported here.

---

## 2. The survey, item by item

### 2.1 Item 1: deployment files (`config/deployment/**`, template, `app/src/bootloader.py`)

Name-like keys, where they are written and shown:

- `deployment_name`. Example values: `config/deployment/templates/deployment_template.yaml:23` = "My Pipeline — Institution Name" (30 characters); `config/deployment/local/local.yaml:5` = "SPARMVET_VIZ (Local Dev)" (24); `config/deployment/demo/web-demo.yaml:5` = "SPARMVET demo (web-demo)" (24). Written as an attribute at `app/src/bootloader.py:122` (default "SPARMVET_VIZ (Local Dev)"). Read only by a method `get_deployment_name` at `libs/connector/src/connector/base.py:64-66`; search finds no non-test caller of that method. Search of `app/` finds no screen that shows it. The template says "shown in app footer" (template line 22); no footer code was found. VERIFIED for the write and the method; NOT VERIFIED for any screen (not found). Who writes: the person who deploys. Required: no check found.
- `branding.banner.title` and `branding.banner.subtitle`. Shown in two places: the app-wide banner, `app/src/ui.py:343-359` (logo, title, subtitle; the reader is `bootloader.get_ui_banner`, `bootloader.py:871-873`), and the HOME accordion "Deployment", `home:1968-1980` (title at `home:1975`, subtitle at `home:1976`). Example: `config/deployment/demo/web-demo.yaml:21-22` has title "" and subtitle "" (empty). Required: no. Checked: `app/tests/test_shipped_deployments.py:38-41` checks only that `theme_css` exists and the logo file exists; no check of the title. VERIFIED.
- Stale comment: `app/src/ui.py:343` says the banner comes from "ui_banner key in app features file". VERIFIED. `app/modules/renamed_keys.py:37` says `ui_banner` was renamed to `branding.banner` in the deployment file. The comment is wrong.
- `branding.contact`. Read at `bootloader.py:585`. Shown in HOME when a recipe is refused: `app/handlers/recipe_gate_handlers.py:101` ("Contact: ..." or "Contact: not configured for this deployment"). Written into the export README with its origin: `app/modules/data_analysis_recipe_validator.py:596` ("deployment (branding.contact)"). Example values: `config/deployment/templates/deployment_template.yaml:49` = "team@example.org" (16 characters); `config/deployment/local/local.yaml:11` = a repository issue-tracker address. Required: no. The template calls it "strongly recommended" (template lines 41-45). VERIFIED.
- `branding.theme_css` and `branding.banner.logo_url`: file paths, not names. Not discussed further.
- Deployment "Deployment" accordion title: `home:1973`. Registry label for the same panel: "Deployment Info" (`app/modules/sidebar_registry.py:33`). The screen text and the registry text differ. VERIFIED.
- Other keys with name-like role: `default_data_analysis_recipe` (template:32, the recipe file name without `.yaml`), `default_app_features` (template:38), `project_root`, `locations.*` (template 54-76). These are paths or ids, not names shown on a screen.

### 2.2 Item 2: app features files and sidebars

- `name` (the id). Example values: `config/app_features/web-demo.yaml:4` = "web-demo"; `config/app_features/pipeline-exploration-advanced.yaml:2` = "pipeline-exploration-advanced" (29 characters, the longest). Rule 2 of the validator: no underscores (`app/modules/app_features_validator.py:79-92`). Shown: the fallback display name at `app/src/bootloader.py:400`. Written by a developer. Required: yes in practice; the validator reads it. VERIFIED.
- `display_name` (the screen name). Example values and lengths: "Web Demo" (8); "VetInst Demo" (12); "Workflow Developer" (18) at `config/app_features/developer.yaml:3`; "QA / Test Harness" (17) at `qa.yaml:18`; "Standalone User (own data)" (26) at `standalone.yaml:5`; "Automated Pipeline - Static" (27) at `pipeline-static.yaml:3`; "Pipeline Exploration - Simple" (29) and "Pipeline Exploration - Advanced" (31). Read by `app/src/bootloader.py:392-402` (property `app_features_display_name`), passed to `app/src/server.py:161-162`. Shown as the badge "Active: ..." at `home:1842` (only when `show_app_features_badge` is on, `home:1841`). The badge text is the display name with underscores replaced and title case applied. Written by the developer who writes the file. Required: no check found. VERIFIED.
- `ui_title` (with `text`, `subtitle`, `visible`): read at `home:1136-1157` (the title banner of HOME; the text is `ui_title.text`, else the recipe's `info.label`, `home:1141-1144`). No shipped app features file has it (search: none). Not in the validator. Not documented in `rules_app_features_flags.md` (search: none). Written by hand in the file, if at all. VERIFIED read; NOT VERIFIED for any shipped use.
- `subtitle` of the recipe's `info`: read at `home:1147`. Listed as optional in the recipe format (`rspec` lines 25-28). VERIFIED.
- `workspaces:` block: each workspace (home, blueprint, gallery, test_lab) has `left_sidebar` and `right_sidebar`, each with `visible` and `panels:` (example `config/app_features/web-demo.yaml:36-62`). The app features files hold only `type` names through `!include` of the sidebar files (`web-demo.yaml:38`). No `label` or `title` parameter was found in any app features file (search of `config/app_features/` for `label`, `title`, `description`: none beyond `display_name` and `name`). VERIFIED.
- `deployment_info`: a panel type, written only in the sidebar files (`config/ui/sidebars/home_standard_left.yaml:5`). It has no parameters in app features. VERIFIED.
- Sidebar files (`config/ui/sidebars/*.yaml`): the panel `type` names, by file:
  - `home_standard_left.yaml:3-11`: notification_log, data_analysis_recipe_info, deployment_info, data_analysis_recipe_choice, filters, data_import, export, session_management, processing_issues.
  - `home_standard_right.yaml:3`: audit_stack.
  - `blueprint_standard_left.yaml:3-4`: notification_log, blueprint_main.
  - `blueprint_standard_right.yaml:3-7`: blueprint_surgeon, blueprint_action_help, blueprint_plot_defaults, blueprint_branch_node, blueprint_agent_chat.
  - `gallery_focus_left.yaml:3-4`: notification_log, gallery_main.
  - `gallery_focus_right.yaml:3`: gallery_right_info.
  - `testlab_standard_left.yaml:3-4`: notification_log, test_lab_info.
  - `testlab_standard_right.yaml:3`: test_lab_right_info.
  VERIFIED.
- Registry `label` (`app/modules/sidebar_registry.py`): the docstring says it is "used by SidebarValidator diagnostics" (lines 13-18). Code that reads `label`: none found. `app/modules/sidebar_validator.py:173` reads `gate_flag` only. The screens do not use the registry label as the accordion title; each accordion title is typed in the renderer code. VERIFIED.

Registry label next to the accordion title on screen (the text the user sees is in the renderer, not the registry):

| Panel type | Registry label (`sidebar_registry.py`) | Accordion title on screen (file:line) | Same? |
|---|---|---|---|
| data_analysis_recipe_info | "Info" (:25) | "Info" (`home:1949`) | yes |
| test_lab_info | "Info" (:29) | "Info" (`home:1962`) | yes |
| deployment_info | "Deployment Info" (:33) | "Deployment" (`home:1973`) | no |
| data_analysis_recipe_choice | "Data analysis recipe Choice" (:37) | "Data analysis recipe Choice" (`home:1986`) | yes |
| filters | "Filters" (:41) | "Filters" (`home:1999`) | yes |
| data_import | "Data Import" (:45) | "Data Import" (`home:2009`) | yes |
| export | "Export" (:49) | "Export / Import" (`home:2027`) | no |
| session_management | "Session Management" (:53) | "Session Management" (`home:2037`) | yes |
| audit_stack | "Pipeline Audit" (:57) | "Pipeline Audit" (`home:2211`, a heading inside the right panel) | yes |
| blueprint_agent_chat | "Blueprint Agent" (:61) | "Blueprint Agent" (`home:2200`) | yes |
| gallery_main | "Gallery Explorer" (:65) | "🔍 Gallery Taxonomy" and others (`gallery_viewer.py:33-128`) | no |
| blueprint_main | "Blueprint Recipe Editor" (:69) | "🗂️ Master data analysis recipe" etc. (`wrangle:184-241`) | no |
| blueprint_surgeon | "Blueprint Surgeon" (:73) | not found under this name on screen | not found |
| blueprint_action_help | "Action Help" (:77) | "Action Help" (`home:2168`, `wrangle:370`) | yes |
| blueprint_plot_defaults | "Plot Defaults" (:81) | "Plot Defaults" (`home:2179`) | yes |
| gallery_right_info | "Gallery Explorer" (:89) | not found | not found |
| test_lab_right_info | "Test Lab Tools (right)" (:93) | the five tool accordions (`test_lab_studio.py:103-123`) | no |
| test_lab | "Test Lab Tools" (:100) | not referenced by a shipped sidebar (`sidebar_registry.py:95-97`) | n/a |
| notification_log | "Notification Log" (:104) | "🔔 Alerts (n)" (`home:2502-2503`) | no |
| processing_issues | "Processing Issues" (:108) | not found as an accordion title | not found |

VERIFIED for each cell that has a cite. "Not found" cells: search found no such title.

### 2.3 Recipe fields not already in the owner's table

- `info.name`: the BLUEPRINT Info form reads it (`bp:2542`, shown as "Name" at `bp:2558`), writes it (`bp:2609-2610`). HOME does not read it (`home:1143` reads `info.label` only). The format's `info` block lists description, subtitle, contact, version, comment (`rspec:25-28`) and says `info` is free form (`rspec:28`), so the checker does not refuse `info.name`. VERIFIED.
- `info.author`, `info.version`, `info.tags`, `info.created`: written by BLUEPRINT (`bp:2613-2617`) and by the new-recipe factory (`libs/blueprint_arch/src/blueprint_arch/new_recipe.py:28-34`). Shown only as raw lines of the HOME Info panel (`app/modules/data_analysis_recipe_info.py:18-27`: every key is shown with its raw key name). VERIFIED.
- A field's `description` is refused by the checker: `check:478-489` builds the known keys from the format's field list plus `label` (`rspec:39-41`); `description` is not on the list, so the checker gives a finding FD01 "description is not a field property". The BLUEPRINT field card reads `description` (`wrangle:1326`) and shows it. The severity of FD01 was not read. VERIFIED (reading). The conflict between the checker and the card is VERIFIED.
- A field's `label`: accepted (`check:479`, via `label_keys_of("field")`). The BLUEPRINT field card shows it as "label:" (`wrangle:1344-1347`). The format's `label_keys` lists `field: label` as PENDING (`rspec:9-17`). VERIFIED.
- The field card header shows the slug (`wrangle:1330`) and a "🔑 PK" marker when `is_entity_key` is true (`wrangle:1332-1334`). The format's word is "entity key" (`rspec:41`, `is_entity_key`). VERIFIED.
- Join `labels`: written by `libs/utils/src/utils/recipe_factory.py:108`; checked by `check:847-849` (the mapping must be column to text). No reader for display found in `app/` or `libs/` (search of `labels` in `app/` non-test: only plot-level labels in `libs/viz_factory/src/viz_factory/plot_config_resolver.py:645-648` and `viz_factory.py:379`, which are the figure's own labels). VERIFIED for the write and the check; NOT VERIFIED for the audit dialog reader (not found).

### 2.4 Item 4: registries (actions and plot components)

Action (`@register_action`, `libs/transformer/src/transformer/actions/base.py:29-52`; the schema is stored in `ACTION_SCHEMAS`):
- Schema keys written by `_schema` in `libs/transformer/src/transformer/actions/polars_calls.py:213-227`: `label`, `category`, `context`, `tags`, `polars`, `wraps`, `params`, `description`, `yaml_example`, and optionally `rules`, `not_exposed`.
- `label` for the polars actions is made from the action name: `action.removeprefix("polars_").replace("_", " ")` (`polars_calls.py:215`). Example: `polars_sort` becomes "sort". VERIFIED.
- Hand-written labels: `modified.py:30` = "filter rows"; `composite.py:33` sets `label` through a helper. Parameter labels are typed in OVERRIDE and parameter dictionaries (`polars_calls.py:48-51`, `polars_rows.py:47-54`, `polars_time_joins.py:50-51`, `modified.py:35-39`). VERIFIED.
- Shown in BLUEPRINT: the picker reads `label` and `category` (`wrangle:863-864`, `wrangle:892`); the action header reads `label` (`wrangle:1075`, `wrangle:1150`); the help reads `description` (`wrangle:1151`, shown at `wrangle:1158` as "bp-help-description"); parameter labels are read at `bp:1338` and `wrangle:2023`. VERIFIED.
- Action names are not the recipe's ui names: an action is written in a step as `action:`/`name:` with a `polars_*` name. Not checked whether the name is shown. NOT VERIFIED.

Plot component (`@register_plot_component`, `libs/viz_factory/src/viz_factory/registry.py:49-86`):
- Schema keys: the docstring names `label, category, context, tags, plotnine, params`, and `overlay` and `not_exposed` for an `exact` component (`registry.py:55-66`). Real examples: `libs/viz_factory/src/viz_factory/coords/core.py:17` "Cartesian coordinates", `:29` a `description`; `facets/core.py:55` "Facet wrap (1D panels)". VERIFIED.
- Shown in BLUEPRINT: header label `wrangle:1010` (`comp_schema.get("label", component_name)`). The description is shown through the help registry (`app/modules/help_registry.py:59-66`, `:101`, `:120`). VERIFIED.
- The plot component's `label` is a picker text. It is not the recipe's `ui_label`, and the two are never compared. A component's name in a recipe is the `name` of a layer (`rspec:69-71`, `layer: required [name]`). VERIFIED.
- Schema registry search (`libs/blueprint_arch/src/blueprint_arch/schema_registry.py:117-143`) reads `label` for keyword search. Agent tools read `label` (`libs/blueprint_arch/src/blueprint_arch/agent_tools.py:113, 178, 345`). VERIFIED.

### 2.5 Item 5: fields of a table and column display names

- `input_fields` properties (the format's field list, `rspec:39-41`): `type`, `categories`, `precision`, `scale`, `format`, `time_unit`, `time_zone`, `original_name`, `is_entity_key`, `null_values`, `strip`, plus `label` (via label_keys). `description` is not in the list (see 2.3). VERIFIED.
- `original_name`: the exact source header. Read by the ingestor (`libs/ingestion/src/ingestion/ingestor.py:35-51`, `:89`). Read by the BLUEPRINT field card (`wrangle:1324`). VERIFIED.
- `label` of a field: read by the BLUEPRINT field card (`wrangle:1323`, `:1344-1347`) and by the BLUEPRINT agent tools (`libs/blueprint_arch/src/blueprint_arch/agent_tools.py:345`). Not found in HOME's data table or filter list. VERIFIED (absence by search).
- The owner's doc `docs/appendix/Standards_yaml.qmd:47` says the field `label` is "also the default axis title of a plot". This contradicts D-0253 (`ledger:282`: the figure text is written only in the `labs` layer). VERIFIED.
- HOME data preview: the table is `render.DataGrid(df, ...)` with `df` taken as it is from the table; the column selector lists the same names (`home:1692-1701`). No label mapping is applied. So HOME shows the column names exactly as the table holds them. VERIFIED.
- HOME filter list (the choices of a column in the filter builder): `app/handlers/filter_and_audit_handlers.py:447-450` builds the choices from `value_choices(lf, col)`; column names were not checked for a mapping. NOT VERIFIED beyond the code shown.
- Export of column names in the data files: NOT VERIFIED.

### 2.6 Item 6: export bundle and report

- Bundle file name: `export:2253-2260`: `{timestamp}_{safe_name}_results.zip`, where `safe_name` is the user's "Bundle label / name" with characters other than letters, digits, `_` and `-` replaced by `_`, cut to 40 characters; default "user". VERIFIED.
- Bundle label in the record: `export:207` ("bundle_label": safe_name). VERIFIED.
- Bundle label field: label "Bundle label / name" with the placeholder "label (no spaces, no special characters)…" and value `EXPORT_LABEL_DEFAULT` (`export:720-722`). The input id is `export_user_name` (`export:720`), so the key says "user name" while the screen says "label". VERIFIED.
- Report title: "Results Report — <recipe id>" (`export:1752`). Line `export:1776`: "Data analysis recipe: **<recipe id>**". VERIFIED.
- Plot names in the report (headings, captions, audit prose): `plot_report_name` at `export:367-373`: `ui_title`, else `ui_label`, else the plot id in title case. VERIFIED.
- Plot file names: `{plot id}.{format}` (`export:1307`), so the file name is the plot id, not any name. Error file: `{plot id}_ERROR.txt` (`export:1331`). VERIFIED.
- Dataset folder names: `_safe_ds_name` (`export:1122-1123`) replaces characters outside letters, digits, `_`, `-`. The folder is `{dataset}/plots/` (`export:1243`, README text `export:2187`). VERIFIED.
- Files at fixed names: `t3_steps.yaml` (`export:1479`), `effective_run.yaml` (`export:1626`), `data_analysis_recipes_reproducibility/{recipe id}.yaml` (`export:1507`). VERIFIED.
- Group names in the report: not found (the report uses plot names only; group names not read there). NOT VERIFIED beyond the code shown.
- Figure caption in the report: `plot_report_lines` (`export:376-383`) builds `![{caption}](_render/...)`. Where `caption` comes from was not traced. NOT VERIFIED.
- README title: "SPARMVET-VIZ Export Bundle" (`export:2124`). VERIFIED.
- "Reproducibility" words in the README and report: `export:2137-2146`, `export:2160`. VERIFIED.

### 2.7 Item 7: session files and the Gallery index

- Session `label` (session file, `assembly.json`): written at `app/modules/session_manager.py:384` (`"label": label`). Read at `session_manager.py:242` (the session name is the label, else the session key), `:807-811`, `:580`, `:619`. The label box is `session_handlers.py:224-226` with the placeholder "Describe this session…". Saved on blur (`session_handlers.py:433-445`). VERIFIED.
- Session label after an import: `session_manager.py:1034` writes "Imported {when} UTC (copy of {original key})", plus the old label if any. VERIFIED.
- Session card title: `session_handlers.py:258` shows "📁 {recipe id}", not the label. VERIFIED.
- Session export button: "💾 Export Active Session (.zip)" (`session_handlers.py:145`). Its file name: `session_handlers.py:377`. VERIFIED.
- Gallery index file: `gallery_index.json` (`libs/viz_gallery/src/viz_gallery/gallery_manager.py:42`). The index entry: `name` = `example_name(recipe)` (`gmgr:142`), `path`, `has_preview`, `has_thumb`, `taxonomy` (`gmgr:141-146`). The dropdown reads `name` (`app/modules/gallery_listing.py:97`). VERIFIED.
- The duplicate-name refusal: `gmgr:113-117`, message "Fix: give each example its own ui_label". VERIFIED.

### 2.8 Item 3: the screens (fixed text, defined in code)

User spaces. The nav item labels and their internal values (`home:1825-1839`):
- "Home" → value "Home".
- "Blueprint Architect" → value "Wrangle Studio".
- "Test Lab" → value "Test Lab".
- "Gallery" → value "Gallery".
VERIFIED.

The internal value "Wrangle Studio" is used in: `home:1049`, `home:2132`, `home:2341`, `bp:943`, `bp:972`, `home:1893` (help file map). `app/src/help/` files are mapped at `home:1892-1895` (home.md, blueprint.md, gallery.md, test_lab.md). VERIFIED.

Other names for the same BLUEPRINT space, on screen and in files:
- "Blueprint Architect" (nav `home:1833`; help `app/src/help/blueprint.md:1, 3`).
- "👣 Blueprint Architect Flight Deck" (banner `wrangle:267`).
- "Blueprint Recipe Editor" (registry `sidebar_registry.py:69`).
- "Wrangle Studio" (internal value and class name; `app/README.md:8` says "Blueprint Architect (Wrangle Studio)").
- "BLUEPRINT" (`CLAUDE.md:13`).
- "Blueprint Surgeon" (registry `:73`); the help says "Surgeon panel" (`blueprint.md:12`); on screen the panel's title is not found under either name.
VERIFIED.

Other names for the same GALLERY space:
- "Gallery" (nav `home:1839`).
- "📚 Gallery Inspiration" (banner `gallery_viewer.py:172`).
- "Gallery Explorer" (registry `sidebar_registry.py:65, 89`).
- "🔍 Gallery Taxonomy" (accordion `gallery_viewer.py:128`).
- "Gallery" help: "a curated browser of visualization examples — pre-built plot templates" (`app/src/help/gallery.md:3`). "Example" and "template" are both used.
VERIFIED.

Other names for the TEST_LAB space:
- "Test Lab" (nav `home:1836`; banner `test_lab_studio.py:94`; help `test_lab.md:1`).
- "Test Lab Tools (right)" and "Test Lab Tools" (registry `sidebar_registry.py:93, 100`).
- "TEST_LAB" (`CLAUDE.md:13`); "LAB" (review-session decision D-0396, `ledger:430`; not on screen).
- The help calls it a "toolbox of stateless data-preparation utilities" (`test_lab.md:3`); `docs/appendix/Terminology.qmd:34` calls it "developer-facing environment … (formerly 'Dev Studio')".
VERIFIED.

Header strip of HOME (`home:1169-1232`):
- "Mode:" (`home:1220`); radio labels "Exploration" and "Audit" with sub-texts "look at the data; nothing is saved" and "create audit steps" (`home:1193-1199`).
- "Table to view:" (`home:1227`); choices "Source" ("as read from the file"), "T1" ("after tier 1"), "T2" ("after tier 2"), "T3" ("the table the plot shows") (`home:1170-1190`).
- Badge: "Viewing: <view>" (`app/modules/view_badge.py:82`; `SOURCE_LABELS` at `view_badge.py:42` maps SRC to "Source"). Notes: "table '<name>'" (`view_badge.py:86`), "T2=T1" (`:90`), audited note (`:93`).
- Plot badge: "Plot: Result" (`view_badge.py:117`); "Plot: Audited" (`view_badge.py:110-111`).
- Plot image alt text: "Plot: <plot id>" (`home:638`).
- The data table title: "Data Preview (max. first 100 rows)" or "Data Preview" (`home:1664-1665`).
VERIFIED.

Panel and accordion titles: see the table in 2.2. Other accordion titles:
- BLUEPRINT left: "🗂️ Master data analysis recipe", "📝 Data analysis recipe Info", "📋 Groups & Plots", "📤 Recipe File Exchange", "🔍 Validate", "🔤 YAML Escape Hatch", "🗺️ Data analysis recipe lineage (TubeMap)" (`wrangle:184, 199, 204, 218, 237, 242, 279`). The `Recipe File Exchange` title was renamed from "External Exchange" (comment `wrangle:209-217`).
- TEST_LAB: "ID Reconciliation", "Data analysis recipe Scaffolding", "Synthetic Data", "Anonymisation", "File Reformatting" (`test_lab_studio.py:103-123`).
- GALLERY: "📊 Preview" (`gallery_viewer.py:33`), "📖 Visual Cookbook: Guidance" (`:52`), "👨‍🍳 Example" (`:117`), "🔍 Gallery Taxonomy" (`:127`). Tabs: "Plot Preview", "Data Sample", "YAML Example" (`gallery_viewer.py:36, 38, 41`). Dropdown: "Select an Example" (`gallery_viewer.py:113`).
- HOME right: "Pipeline Audit" (`home:2211`), "Action Help" (`home:2168`), "Plot Defaults" (`home:2179`), "Blueprint Agent" (`home:2200`).
- HOME left: "Info" (`home:1949`), "Deployment" (`home:1973`), "Data analysis recipe Choice" (`home:1986`), "Filters" (`home:1999`), "Data Import" (`home:2009`), "Export / Import" (`home:2027`), "Session Management" (`home:2037`), "🔔 Alerts (n)" (`home:2502-2503`).
VERIFIED.

Buttons, same action in different places:
- Apply (left filter panel, Exploration): "Apply (n)" (`filter_and_audit_handlers.py:644`). Help says "Apply" (`app/src/help/home.md:25`).
- Apply (right audit panel, Audit mode): "Apply" (`audit_stack.py:699, 715, 733, 748`); "Apply ⛔" when blocked (`audit_stack.py:708, 741`).
- Apply (BLUEPRINT form): "Apply to session" (`bp:1739`); "Apply" in the join designer (`bp:1996, 2001`).
- Apply (Data Import): "✅ Validate & Apply" (`data_import_handlers.py:237`).
- Apply (plot style): "Apply Style" (`audit_stack.py:798, 890`).
- Send to Audit: "➜ Send to Audit (n)" (`filter_and_audit_handlers.py:652`). Help: "➜ Send to Audit" (`home.md:27`).
- Reset: "Reset" (`filter_and_audit_handlers.py:667`).
- Export: "⬆ Export" (header, `export:716`); "💾 Export Bundle" (button, `export:763`); help: "Export Bundle" (`home.md:47`).
- Import: "⬇ Import a bundle" (`export:693`); upload label "Reproducibility bundle (.zip)" (`export:697`); help "Import a bundle" (`home.md:49`); result "✅ Imported as '<id>'" (`export:891`); failure "❌ Import failed" (`export:881`).
- Save (BLUEPRINT): "Save to data analysis recipe" (`bp:2581`); "✅ Saved to <file>" (`bp:1191`); "Data analysis recipe info saved." (`bp:2624`).
- Session: "💾 Export Active Session (.zip)" (`session_handlers.py:145`); "Restore" and "Delete Session" (help `home.md:52`).
VERIFIED.

Words for the same thing, on screen and in the help (in detail in section 5, table C).

### 2.9 Item 8: documentation (`docs/**/*.qmd`, `README.md`, lib READMEs)

- The format terms in docs: `docs/appendix/data_analysis_recipe_structure.yaml:52-56, 84-85` (`ui_label`, `ui_title`); `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:288-302` (`ui_label` and `ui_title`); `docs/appendix/viz_factory_components.qmd:125-128`. These agree with the format. VERIFIED.
- `docs/foundations/data_contracts_adr.qmd:19, 24`: "`info.label` is the only required key of `info`; `info` is free-form otherwise (study, version, any key you want shown in HOME)". Agrees with the checker. VERIFIED.
- `docs/appendix/Terminology.qmd:8`: the recipe's `info:` block describes it as "title, description, version, study, contact, anything the author writes". The word "title" here is not the key `label`. Differs from the format. VERIFIED.
- `docs/appendix/Standards_yaml.qmd:17, 27, 47` and `docs/foundations/data_contracts_adr.qmd:49-71, 150, 211`: a field is given `label:` and the field `label` is called "also the default axis title of a plot" (`Standards_yaml.qmd:47`). Contradicts D-0253 (`ledger:282`). VERIFIED.
- `docs/troubleshooting/index.qmd:605`: `ui_label` on a group. Agrees. VERIFIED.
- `docs/user_guide/blueprint_data_analysis_recipe_authoring.qmd:329-339`: "there is no `title:` key in the plot", followed by a code block that has a `labs` layer with `title:` as a param. The `labs` layer's `title` parameter is the figure title, which is allowed. Consistent. VERIFIED.
- `docs/appendix/Terminology.qmd:16-17`: "Anchor (Tier 1/2)" and "Leaf (Tier 3)". On screen the tiers are "T1", "T2", "T3" (`home:1170-1190`). The code uses "anchors" for the folder (`home:1114`). VERIFIED.
- `docs/appendix/Terminology.qmd:11`: "Record (formerly *Sample*)". The docs also show "Sample ID" as a field label (`Standards_yaml.qmd:27`). VERIFIED.
- `docs/appendix/Terminology.qmd:9-10`: "Schema" and "Collection". The code uses `collection_id` (`home:1112`). VERIFIED.
- `docs/UML/app.mdj:34603` says "ui_label (the name of the example, D-0387)". Matches the D-0387 wording, not the current code. VERIFIED (search).
- Violet form (`ComponentName (file_name.py)`): the rule is `.claude/rules/rules_documentation_aesthetics.md:27-33`, applying to `.qmd` files and README lists. Compliance of each doc was not checked. NOT VERIFIED.
- `README.md`: not read for names. NOT VERIFIED.
- Lib READMEs: `libs/connector/README.md:29` names `get_deployment_name()`. VERIFIED (search).

### 2.10 Item 9: vocabulary rules, ADRs, decisions

Rules that exist:
- `CLAUDE.md:11-16`: the four terms. User space = HOME, BLUEPRINT, TEST_LAB, GALLERY. Code module = a Python file. Data analysis recipe = the YAML file. App features = a named set of flags in `config/app_features/`. `CLAUDE.md:18`: "Never mix user-space and code-module vocabulary". VERIFIED.
- `docs/appendix/Terminology.qmd:4-35`: the owner's nomenclature list, with "Deployment" (line 24), "App features" (line 25), "Home" (31), "Info panel" (32), "Blueprint Architect ('Wrangle Studio')" (33), "Test Lab" (34), "Gallery" (35). VERIFIED.
- `.claude/knowledge/project_conventions.md:133`: an `input_fields` entry must include `type`; `original_name` and `label` are optional. VERIFIED.
- `.claude/rules/rules_documentation_aesthetics.md:27-33`: the Violet Law. `:33` prohibits its use in code, filenames and docstrings. VERIFIED.
- `assets/scripts/audit_old_words.py:32-40`: the retired words are persona, manifest, recipe (bare), profile, project, app features template, connector. The word `label` is not on the list. `:44-75`: exclusions. VERIFIED.
- ADR-091 (`.claude/knowledge/architecture_decisions.md:4396-4400`): the final configuration names; the words "profile" and "persona" are replaced; the entry is ACCEPTED. ADR-092 (`:4512-4523`): one flag for the BLUEPRINT and one identifier for a recipe. VERIFIED.
- `app/modules/renamed_keys.py`: app features keys (`:32-38`: persona_id → name; ui_banner → branding.banner; theme_css → branding.theme_css), deployment keys (`:17-22`), locations (`:25-29`), panel types (`:58-60`: project_info → data_analysis_recipe_info), session keys (`:63-69`). It has no entry for the recipe keys `label`, `name`, `title`, `description`. The recipe renames are held in `rspec:83-104` and in the checker. VERIFIED.

Decisions in the ledger on names and labels. Quotes are the words in the ledger line (her words, as the ledger holds them).

- D-0237 (`ledger:266`, 2026-11-17, DECIDED, Eve): the engine key first, then `label` where there is one. Her words, in the line: "B for both ... first engine then label, but you got the idea, yes, no spec ... Cleaner" (M246). Amended by D-0253 ("then label" becomes `ui_label`, stated in `ledger:282`).
- D-0252 (`ledger:281`, 2026-11-18, DECIDED): a plot in its own file holds the whole entry (label, description, taxonomy, plot content, engine line). The line says "label", which D-0253 renamed. Her words: "B - you can have the coordinator see how it can work ...". VERIFIED.
- D-0253 (`ledger:282`, 2026-11-18, DECIDED, Eve): figure text only in `labs`; `label` becomes `ui_label` (short name: HOME tab, Gallery and BLUEPRINT lists); new `ui_title` for the longer name used by the report; `title:` removed; report falls back to `ui_label`. Her words: "labs stays plotnine and the others stay ui (this is the principle we seem to agree upon) - cleaner"; "I do not think I want title from the UI leak inside the plot content". The line says NOT decided: which other `label` keys are renamed, and what happens to the old `title:` text of the 18 plot files. VERIFIED.
- D-0360 (`ledger:394`, 2026-11-20, DECIDED, status "EVE"): the field `label` is for the view of the tables; it can be an alias of the column, to avoid long column names. Her words: "label could be alias of the column to avoid long column names ... that would also allow renaming columns which makes tracking difficult no ?". The line itself calls the alias "a proposal, not a rule" (see C10). VERIFIED.
- D-0387 (`ledger:421`, 2026-11-20, DECIDED): the Gallery name is the plot's `ui_label`. Her words: "the code must read the correct label: ui_label then ?"; "info is more for the recipe maker ... ui_label is the field to use". The code reference is stale (C4). VERIFIED.
- D-0397 (`ledger:431`, 2026-11-21, DECIDED): the Gallery heading and the name are concordant, not identical; the heading becomes a real description; only one line is shown (the name). Her words: "I think the ui_label should be more like the Heading guidance text its more scientific so I think this is your case B"; "only one line show is important". VERIFIED.
- D-0398 (`ledger:432`, 2026-11-21, DECIDED): a new typed axis "Chart type" in plain words, several values allowed. The filter "Primary Geom" keeps its name. Not built. VERIFIED.
- D-0399 (`ledger:433`, 2026-11-21, DECIDED): the allowed taxonomy words and their meanings live in the recipe spec, with a generated documentation form. Her words: "would that be possible to extract the words and meanings for the gallery specific terms ... thus automatically". Not built. VERIFIED.
- D-0403 (`ledger:437`, 2026-11-21, DECIDED): a tag mismatch in the Gallery check is an advice, not an error. Her words: "Advice - and after the agentic review I want to see those advises." VERIFIED.
- D-0404 (`ledger:438`, 2026-11-21, DECIDED): the meaning of a Gallery filter term is shown on hover or click of a small mark. Her words: "Id go for C (hoover)". Not built. VERIFIED.
- D-0405 (`ledger:439`, 2026-11-21, DECIDED): in a Gallery recipe `info.label` and the plot's `ui_label` may differ; no check enforces equality; `ui_label` is short, `info.label` the header block. Her words: "the ui_label is aimed to be short - The info.label its the header block and then a title can be abit more long"; "ui_label has to be shown in the ui ? is it not more a ui tag to be able to find the correct recipe ?". VERIFIED.
- Pending question M271, the label keys (`rspec:9-17`: "PENDING (Eve, channel M271, not decided)"; `ledger:518`: "the three `label` places of the recipe ... are NOT decided"; her words there: "so data_schema I think the labels are ui_label because its what is shown in the ui"; "column_label is fine - its what is seen when data is previewed"). Status: not decided. VERIFIED.
- D-0310 and D-0016 are cited for the HOME data choice, not for names. Not used here.
- D-0034 is cited in `ledger:394` (the default of plot titles from the label does not stand for plots). Its own line was not read. NOT VERIFIED.
- Also the owner's order of today is in `tmpAI/panel/names_whole_app/ORDER.md`. VERIFIED.

---

## 3. Analysis A: kinds of name, and the fields that play each role today

Kind 1: identity (an id, a file name, a key; not shown; must be unique).
- Recipe: file name and top-level `id` must match (`check:244-245`, from the owner's table, NOT VERIFIED here). Group key and plot key (`plots.<id>`, snake_case, `spec:492`). Schema key (`data_schemas`), join key. Layer `name` (a plotnine name, `rspec:69-71`).
- Recipe spec key `id` (`rspec:23`).
- App features: `name` (`app/modules/app_features_validator.py:79-92`) and the file name.
- Deployment: no id; the file path.
- Sidebar panel `type` names (`config/ui/sidebars/*.yaml`; `sidebar_registry.py` key).
- Session: session key (folder name); `session_handlers.py:226` etc.
- Gallery: folder name = example key; must equal the recipe `id` (`check:1256-1257`, NOT VERIFIED here).
- Gallery index: the registry key (`gmgr:136-137`).
- Actions: the `polars_*` name and the registration name (`base.py:29`).
- Plot component: the registration name (`registry.py:49`).
- Palette name (`config/palettes.yaml`).
- User space nav value: "Home", "Wrangle Studio", "Test Lab", "Gallery" (`home:1825-1839`).

Kind 2: the short name (shown in a tab, a list or a button).
- Recipe group: `ui_label` (`home:103-105`).
- Recipe plot: `ui_label` (`home:108-110`, the tab; `home:113-115`, the audit list; `bp:2313`, BLUEPRINT list; `taxonomy:55-66`, Gallery).
- Recipe field: `label` (BLUEPRINT field card, `wrangle:1323, 1347`).
- Recipe table/schema/join: `label` (required by the checker, `check:390-391, 834-835`; display not verified: NOT VERIFIED).
- Session: `label` (`session_manager.py:242`, the name in the session list).
- Gallery example: `name` in the index (`gmgr:142`), shown in the dropdown (`gallery_listing.py:97`).
- Action (BLUEPRINT picker): `ui_schema` `label` (`wrangle:1075, 1150`).
- Plot component (BLUEPRINT picker): `label` (`wrangle:1010`).
- Tree node in the TubeMap/lineage: `node["label"]` (`wrangle:1466`); audit list step: `step.get("label")` (`audit_stack.py:380`); lineage export: `_s["label"]`, `_nd["label"]` (`export:1661, 1984`).
- Panel registry `label`: diagnostics only (not shown).
- Nav items: "Home", "Blueprint Architect", "Test Lab", "Gallery" (`home:1825-1839`).
- App features `display_name` (`bootloader.py:392-402`; badge at `home:1842`).
- Deployment: `deployment_name` is not shown (2.1).

Kind 3: the longer title (shown as a heading, a banner, or in a report).
- Recipe plot: `ui_title` (report only, `export:373`).
- Recipe group: `ui_title` (no reader).
- Recipe `info.label` (HOME title banner, `home:1141-1144`; HOME Info panel, raw key).
- Recipe `info.subtitle` (HOME banner subtitle, `home:1147`).
- App features `ui_title.text` and `ui_title.subtitle` (HOME banner, `home:1139-1152`).
- Deployment `branding.banner.title` and `.subtitle`: app-wide banner (`ui.py:343-359`) and HOME "Deployment" accordion (`home:1975-1976`).
- Report title "Results Report — <id>" (`export:1752`); report line "Data analysis recipe: <id>" (`export:1776`).
- Gallery: the `##` heading of `example_meta.md` (`taxonomy:97`); "📖 Visual Cookbook: Guidance" (`gallery_viewer.py:52`).
- Banners: "👣 Blueprint Architect Flight Deck" (`wrangle:267`); "Test Lab" (`test_lab_studio.py:94`); "📚 Gallery Inspiration" (`gallery_viewer.py:172`).
- Session card title "📁 <recipe id>" (`session_handlers.py:258`).

Kind 4: the description (a sentence that says what it is for).
- Recipe `info.description` (`spec:368`; read by BLUEPRINT form `bp:2543`; HOME Info panel raw line).
- Recipe group `description` (the tab text only when `ui_label` is missing, `home:105`).
- Recipe plot `description` (`spec:492`; no screen found).
- Recipe schema `description` (`check:392-394`; advice S04 when missing).
- Recipe join `description` (`check:836-838`; advice J03 when missing).
- Recipe field `description` (refused by the checker, FD01; shown by the BLUEPRINT field card, `wrangle:1326`).
- Action `description` (`polars_calls.py:221`; BLUEPRINT help `wrangle:1151, 1158`).
- Plot component `description` (`coords/core.py:29`; help registry `help_registry.py:59, 101`).
- Gallery: the `##` heading is the example's guidance heading (`taxonomy:97`); D-0397 decides it becomes a real description (`ledger:431`).
- Deployment, app features, sidebar panel, nav item, session: no description field found.

Kind 5: the meaning or help text (shown on demand).
- Help files: `app/src/help/home.md`, `blueprint.md`, `gallery.md`, `test_lab.md`, shown per user space (`home:1892-1895`).
- BLUEPRINT action help (`wrangle:1150-1158`; "Action Help" panel, `home:2168`).
- Tooltips of the HOME strip: "Source: one source table…" etc. (`home:1173-1202`).
- Badge notes (`view_badge.py:84-93`).
- Gallery filter term meanings: decided (D-0404), not built.
- BLUEPRINT form placeholders (`bp:2571-2574`).
- Info panel of HOME: every key of `info` as a raw line (`data_analysis_recipe_info.py:18-27`).

Kind 6: a display name of a column.
- Source header: `original_name` (`ingestor.py:35-51`).
- Slug: the key of the field in `input_fields` (shown as the card header in BLUEPRINT, `wrangle:1330`).
- Field `label` (BLUEPRINT field card, `wrangle:1323-1347`; agent tools `agent_tools.py:345`).
- Join `labels` mapping (written and checked, `recipe_factory.py:108`, `check:847-849`; no reader for display found).
- HOME data preview: raw column names (`home:1692-1701`).
- HOME filter list: raw names (`filter_and_audit_handlers.py:447-450`; NOT VERIFIED beyond that).
- Export data files: NOT VERIFIED.

Kind 7: the text inside a figure.
- Figure title, axis names, legend names: `labs` layer params (`spec:179`, D-0253). The docs example (`blueprint_data_analysis_recipe_authoring.qmd:335-339`) shows `title`, `x`, `fill` in `labs`.
- The `title:` key of a plot is refused (`spec:140`, `spec:508`).
- Plot alt text (not in the picture): "Plot: <plot id>" (`home:638`).
- Figure caption in the report: NOT VERIFIED.
- Deployment `branding`: no figure text.

---

## 4. Analysis B: two fields doing one job, and one key doing two jobs

Two fields doing the same job ("the short name shown in a tab or list"):
- Recipe `ui_label` (groups, plots) and recipe `info.label` (HOME banner, not a tab) both hold a name. In HOME the banner shows `info.label` (`home:1143`); the tabs show `ui_label` (`home:103-110`).
- Gallery: `info.label` (required by the checker, `check:316-317`) and `ui_label` of the plot both hold a name; only `ui_label` is read for the Gallery (`taxonomy:58`).
- App features `display_name` and recipe `info.label`: both are a screen name for a whole thing; one is the app features set, the other the recipe.
- Deployment `deployment_name` (not shown) and `branding.banner.title` (shown): two deployment names.
- Gallery example: `name` in the index (`gmgr:142`) and `ui_label` of the plot (same value, `gmgr:142` reads it).
- Session: `label` and the session card title (recipe id, `session_handlers.py:258`).

Two fields doing the same job ("the longer name"):
- Plot `ui_title` (report only) and `info.label` (HOME banner): the owner's table calls `info.label` the short name, but HOME uses it as the header. The owner (D-0405) says `info.label` is the longer header.
- Group `ui_title` (no reader) and plot `ui_title` (report).
- App features `ui_title.text` and recipe `info.label`: both replace the HOME banner; the first wins (`home:1141`).
- Deployment `branding.banner.title` (app banner and Deployment accordion).

Two fields doing the same job ("the description"):
- `info.description` (recipe), group `description` (tab fallback), plot `description`, schema `description`, join `description`, field `description` (refused), action `description`, plot component `description`.

One key name used for two jobs (or more):
- `label`: short name of a plot or group (before D-0253, `ledger:282`); field display name (`rspec:39-41`, `wrangle:1323`); schema/table/join display label (`rspec:14-16`, pending); info label (the recipe title, `rspec:14`, `check:316`); join `labels` is a different key with a mapping; session label (`session_manager.py:384`); lineage node label (`wrangle:1466`); audit step label (`audit_stack.py:380`); action picker label (`wrangle:1075`); plot component picker label (`wrangle:1010`); parameter label (`wrangle:2023`); panel registry label (`sidebar_registry.py:25-108`, diagnostics); figure label in plotnine (`labs` is the plotnine layer, not `label`). At least eight jobs.
- `ui_title`: a recipe key for the longer plot or group name (`spec:485, 498`) and an app features key for the HOME banner text (`home:1139`). The same word, two meanings (C in section 1 and D2 in section 5).
- `title`: the figure title in `labs` (`spec:140`); the report title (`export:1752`); the banner title (`branding.banner.title`); the old plot key `title:` (refused, `spec:140`); `title` in the Terminology doc (`Terminology.qmd:8`).
- `subtitle`: `info.subtitle` (recipe banner), `ui_title.subtitle` (app features banner), `branding.banner.subtitle` (app banner).
- `name`: the app features id (`app_features_validator.py:79`); a layer name (`rspec:69-71`); the Gallery index `name` (`gmgr:142`); the old recipe key (`rspec:85-94`: `name` → `info.label`); the BLUEPRINT form key `info.name` (`bp:2609`); the fallback in `home:115` (`entry.get("name")` for a plot, not in the format).
- `description`: see above; also the fallback tab text of a group (`home:105`).
- `dataset`: `target_dataset` (a plot's table key, `export:1127`), the export folder `{dataset}/plots/` (`export:1243`), "dataset" in the owner's glossary (`Terminology.qmd:10` uses "datasets" for "Collection").
- `Mode`: "Mode:" in HOME (`home:1220`); "Mode" in TEST_LAB (`test_lab_handlers.py:556`) is a different thing.
- `Preview`: "📊 Preview" (Gallery accordion, `gallery_viewer.py:33`), "Plot Preview" (Gallery tab, `:36`), "Data Preview" (HOME table, `home:1664`), "Preview" in the audit "preview" filters (help `home.md:25`). Four uses.
- `Export`: the session button "💾 Export Active Session (.zip)" (`session_handlers.py:145`), the HOME header "⬆ Export" (`export:716`), the HOME accordion "Export / Import" (`home:2027`), the registry "Export" (`sidebar_registry.py:49`), the button "💾 Export Bundle" (`export:763`).
- `Apply`: a filter Apply (`filter_and_audit_handlers.py:644`), an audit Apply (`audit_stack.py:699`), a BLUEPRINT "Apply to session" (`bp:1739`), a join Apply (`bp:1996`), "Validate & Apply" (`data_import_handlers.py:237`), and "Apply Style" (`audit_stack.py:798`).
- `T3`: the table the plot shows (`home:1188`); "T3 node"/"T3 audit" (`audit_stack.py:2`, the panel is "Pipeline Audit").
- `Audit`: a mode (`home:1199`), a panel ("Pipeline Audit", `home:2211`), a node (`audit_stack.py:533`), a step (help `home.md:27`), a plot state ("Plot: Audited", `view_badge.py:110`).

---

## 5. Analysis C: the same thing, several words (screen, code and docs)

| Thing | Words found | Where (file:line) |
|---|---|---|
| The recipe (whole file) | "data analysis recipe"; "recipe"; "Data analysis recipe Choice"; "Master data analysis recipe"; "Data analysis recipe Info"; "pipeline" (folder name `pipelines`; "Automated Pipeline - Static"; "Pipeline Audit"); "manifest" (retired, `audit_old_words.py:34`) | `home:1986, 1988`; `wrangle:184, 199`; `export:1776`; `help/home.md` (many); `config/app_features/pipeline-static.yaml:3`; `Terminology.qmd:8`; `CLAUDE.md:15` |
| The plot | "plot"; "Plot Preview" (Gallery tab); "Plot: Result"; "Plot: Audited"; "figure" (export code and report); "chart" (not on screen; proposed D-0398); "graph" (lineage) | `home:638`; `gallery_viewer.py:36`; `view_badge.py:110-117`; `export:371-383, 1632, 1720, 1734`; `ledger:432` |
| The analysis group | "analysis group" / `analysis_groups` (code key); "group" (code); "tab" (screen); "Groups & Plots" (BLUEPRINT accordion) | `home:1134`; `help/home.md:3` ("analysis_groups become tabs"); `home:103-105`; `wrangle:204` |
| The table (as the user sees it) | "Table to view"; "Data Preview"; "table" (badge); "source table" (help); "data preview table" (help) | `home:1227`; `home:1664`; `view_badge.py:86`; `help/home.md:15, 44` |
| The source data file | "Source"; "SRC" (code value); "source table" (help); "data file" (help: "file"); "original file" | `home:1171`; `home:487`; `help/home.md:15`; `help/test_lab.md:15` |
| The schema (table definition) | "schema" (help); "data schema" (help, code comment); `data_schemas` (format key); "input_fields" (format key); "Schema" (glossary) | `help/blueprint.md:12, 15`; `help/test_lab.md:12`; `rspec:33`; `Terminology.qmd:9` |
| The join | "join"; "Joint Designer" (help); "ingredients" (format) | `help/blueprint.md:14, 15`; `rspec:43` |
| The collection (joined tables) | "Collection" (glossary); `collection_id` (code); "anchor" (folder, glossary) | `Terminology.qmd:10`; `home:1112`; `home:1114`; `Terminology.qmd:16` |
| A step | "step"; "wrangling steps" (help); "transformation node" (help); "action" (picker); "step list" (glossary); "node" (audit list); "steps" (format key) | `help/blueprint.md:12`; `wrangle:1883`; `Terminology.qmd:18`; `audit_stack.py:533` |
| An audit step | "audit step" (help, glossary); "audit node" (code, screen, `audit_stack.py:533`); "audit steps" (format key `t3_audit_steps_by_plot`, `Terminology.qmd:19`); "filter and drop" (help) | `help/home.md:27`; `audit_stack.py:533`; `ledger` (many) |
| The T3 node | "T3 node": not found on screen or in help | NOT VERIFIED (not found) |
| Export / import | "Export" (several), "Export / Import" (accordion), "Export Bundle" (button), "Results bundle" (code docstring `export:2`), "Reproducibility bundle" (upload label `export:697`), "reproducibility/reimport bundle" (checkbox text `export:701, 2137`), "Export Active Session (.zip)" (session), "Import a bundle" (button) | `home:2027`; `export:763, 697, 701, 2, 2137`; `session_handlers.py:145`; `help/home.md:47-52` |
| Apply | "Apply" (filter), "Apply (n)", "Apply ⛔", "Apply to session", "Validate & Apply", "Apply Style", "Send to Audit", "Reset" | `filter_and_audit_handlers.py:644, 652, 667`; `audit_stack.py:699, 708, 798`; `bp:1739`; `data_import_handlers.py:237` |
| Save | "Save to data analysis recipe" (BLUEPRINT form); "Saved to <file>"; "Data analysis recipe info saved."; "Save" (session label on blur) | `bp:2581, 1191, 2624`; `session_handlers.py:433` |
| The panel that shows the recipe's info | "Info" (accordion); "Data analysis recipe Info" (BLUEPRINT accordion); "Info panel" (help, glossary); `data_analysis_recipe_info` (key) | `home:1949`; `wrangle:199`; `help/home.md:41`; `Terminology.qmd:32` |
| The notes panel | "Alerts" (accordion, help); "Notification Log" (registry label) | `home:2502-2503`; `help/home.md:41`; `sidebar_registry.py:104` |
| Deployment | "Deployment" (accordion); "Deployment Info" (registry label); "deployment" (glossary, format) | `home:1973`; `sidebar_registry.py:33`; `Terminology.qmd:24` |
| App features | "App features" (glossary); "Active: <display name>" (badge); "app features selector" (old) | `Terminology.qmd:25`; `home:1842` |
| The BLUEPRINT user space | "Blueprint Architect"; "Wrangle Studio"; "Blueprint Architect Flight Deck"; "Blueprint Recipe Editor" (registry); "BLUEPRINT"; "Blueprint" | `home:1833`; `home:1049`; `wrangle:267`; `sidebar_registry.py:69`; `CLAUDE.md:13`; `help/blueprint.md:1` |
| The TEST_LAB user space | "Test Lab"; "Test Lab Tools" (registry); "TEST_LAB"; "LAB" (review decision D-0396); "Dev Studio" (old) | `home:1836`; `sidebar_registry.py:93, 100`; `CLAUDE.md:13`; `ledger:430`; `Terminology.qmd:34` |
| The GALLERY user space | "Gallery"; "Gallery Explorer" (registry); "📚 Gallery Inspiration" (banner); "Gallery Taxonomy" (accordion); "example" and "template" (help) | `home:1839`; `sidebar_registry.py:65`; `gallery_viewer.py:172, 128`; `help/gallery.md:3` |
| The Gallery's filter axes | "Family" (help); "Family (Purpose)" (format example); "Data Pattern"; "Difficulty"; "Primary Geom"; "What it Shows"; "Sample Size" | `help/gallery.md:6`; `spec:209-214` |
| The Gallery's preview words | "Preview" (accordion); "Plot Preview" (tab); "Data Sample"; "YAML Example"; "Visual Cookbook: Guidance" | `gallery_viewer.py:33, 36, 38, 41, 52` |
| The HOME mode | "Exploration" and "Audit" (radio and help); "Mode:" (strip label); "Exploration mode" (export record) | `home:1193-1199, 1220`; `home:453` |
| Header tiers | "Source", "T1", "T2", "T3" (screen); "Anchor (Tier 1/2)", "Leaf (Tier 3)" (glossary) | `home:1170-1190`; `Terminology.qmd:16-17` |
| Primary key | "PK" (BLUEPRINT field card); "entity key" (format key `is_entity_key`); "primary key" (old key, `renamed`) | `wrangle:1334`; `rspec:41`; `rspec:108` |
| The name of a bundle | "Bundle label / name" (screen); `export_user_name` (key); "bundle label" (help); "label" (placeholder) | `export:720-721`; `help/home.md:47` |
| Figure text | "axis", "legend", "title" (labs params); "label" (old) | `spec:179`; `Standards_yaml.qmd:47` |

VERIFIED for each cell with a cite. "T3 node" is NOT VERIFIED (not found).

---

## 6. Analysis D: written and never read, read and never documented

Written, never read by any screen or code (VERIFIED by search unless marked):
- Deployment `deployment_name`: written at `bootloader.py:122`; read only by `connector/base.py:64-66`, a method no non-test caller uses. Not shown on any screen (not found).
- Recipe `info.submission_date`: written by the Gallery generator (owner's table; NOT VERIFIED here); read by no code; shown only as a raw line in the HOME Info panel when a recipe is opened there.
- Recipe group `ui_title`: documented as "used by the report and the headings" (`spec:485`); no reader (VERIFIED by search).
- Recipe join `labels` (display names of columns): written and checked (`recipe_factory.py:108`, `check:847-849`); no reader found for the audit dialog, the table or the export (NOT VERIFIED beyond search); `spec:69` and `spec:474` say it is shown in the audit dialog.
- Panel registry `label` (`sidebar_registry.py`): written in every entry; read by no code; only the docstring names it (`sidebar_registry.py:13-18`). VERIFIED.
- Recipe plot `description`: optional in the format (`spec:492`); no screen found reading it (NOT VERIFIED beyond search).
- Recipe `info.name` (BLUEPRINT key): written by BLUEPRINT (`bp:2609-2610`) and read by the BLUEPRINT form only (`bp:2542`). HOME, export, Gallery do not read it. Shown in HOME's Info panel as a raw line. VERIFIED.
- Recipe `info.author`, `version`, `tags`, `created`: written (`bp:2613-2617`; `new_recipe.py:28-34`); read by the BLUEPRINT form (`bp:2544-2546`); HOME shows them only as raw lines. VERIFIED.
- App features `ui_title`: read at `home:1139`; no shipped file has it; undocumented in the rules. VERIFIED.
- App features `display_name` and `name`: both read (`bootloader.py:392-402`).
- Session `label`: written and read. No write-only case found.

Read, never documented (VERIFIED by search of `docs/` and the format):
- App features `ui_title` (`home:1139`): not in `rules_app_features_flags.md` nor in `docs/` (search).
- Deployment `branding.banner` keys: documented in the template (`deployment_template.yaml:46`) and in ADR-091 (renamed_keys), not in `docs/` (search for `branding.banner` in docs was not run; NOT VERIFIED).
- BLUEPRINT form key `info.name`: not in the format (`rspec:25-28` lists the optional keys), not in the docs (NOT VERIFIED).
- `info.subtitle` (`home:1147`): in the format (`rspec:27`); documentation not checked. NOT VERIFIED.
- Gallery `example_meta.md` heading: read by the Gallery (`taxonomy:97`); not in the format (`spec` does not list it, per the owner's table). VERIFIED by search of `spec`.

Field `description` (BLUEPRINT card reads it, `wrangle:1326`; the checker refuses it, `check:478-489`): read and refused at once. VERIFIED.

---

## 7. Analysis E: questions a homogeneous scheme must answer (not answered here)

1. One key name per kind everywhere, or one per file kind? (For example: `label` for the short name in the recipe and `name` in app features and deployment, or the same key everywhere.)
2. Does every nameable thing have all seven kinds, or only some? Today a recipe group has a short name, a longer title (not read), and a description; an app features set has a display name and a banner title; a deployment has a name (not shown) and a banner.
3. Where does "short" get a number? Today nothing checks a length (owner's table, section 3 item 4; NOT VERIFIED by me beyond the format text).
4. Which of these is the one word for a recipe, a plot, a group, a table, a column, a step, a figure: short name, title, label, display name?
5. Is `info.label` the short name (the owner's wording in D-0405) or the recipe's header title? Its real values are longer than the tab names (owner's table, sec. 5).
6. Is `ui_title` a recipe key and an app features key at once? Rename one, or say it in the rule (owner's table, sec. 6 item 6).
7. Is the registry `label` (sidebar, actions, plot components) a screen name, a diagnostics name, or removed?
8. The field `label` (pending, `rspec:9-17`): does it stay `label`, become `ui_label`, or keep both as an alias (D-0360)?
9. The field `description`: does the format accept it (the BLUEPRINT card reads it; the checker refuses it)?
10. The join `labels` mapping: who reads it? Is it on the audit dialog, the table, the export, or nowhere?
11. The group `ui_title`: is it read by the report and the headings, as the format says, or removed from the format?
12. The plot `description`: does a screen show it, or is it removed from the format?
13. Should the HOME banner, the Gallery name and the tab text be checked for equality, for a length, or for nothing (D-0405 says: an advice at most)?
14. Which words are the one word for each thing on screen: "Apply", "Export", "Save", "Import", "bundle", "table", "dataset", "recipe", "plot", "figure", "chart", "group", "step", "action", "node"?
15. Which name for the BLUEPRINT space: "Blueprint Architect", "BLUEPRINT", "Wrangle Studio" (internal)? Which for the TEST_LAB space: "Test Lab", "TEST_LAB", "LAB" (D-0396)? Which for the notes panel: "Alerts" or "Notification Log"?
16. Which name for the export: "Export Bundle", "results bundle", "reproducibility bundle", "reimport bundle"?
17. Should the old docs wording ("title" in Terminology; `label` as the axis title in Standards_yaml) be corrected to the decided words (D-0253)?
18. Should `info.name` (BLUEPRINT) be renamed to `info.label`, or dropped?
19. Should the registry `label` be removed from the schema, or used for the picker?
20. Should `audit_old_words.py` also count `label`, `title` and `name` as retired words in the relevant places (its list today is persona, manifest, recipe, profile, project, app features template, connector; `audit_old_words.py:32-40`)?
21. Should the Violet Law (`ComponentName (file_name.py)`) be applied to names in the docs and README lists?

---

## 8. Not verified

- The lengths of recipe names in the 16 shipped recipes and the 34 Gallery examples (owner's table, sec. 2): not measured again.
- `check:244-245`, `check:1256-1257`, `spec:367`, `spec:484-498` (only in part), `home:109-115` (only the function bodies), `data_analysis_recipe_validator.py:58`.
- The group description tab fallback as shown on screen (owner's table says `home:105`; read, not run).
- Whether the HOME Info panel and the Gallery preview show `info` values as the owner's table says.
- The rows of the Gallery `info` (`submission_date` written by the generator).
- Where a plot or group `description` is shown on any screen (search found none; not run).
- Column display names in the export data files and the Gallery data sample.
- The audit dialog's reader of join `labels` (not found by search).
- The figure caption source in the export report (`export:376-383`).
- The severity of the checker finding FD01 for a field `description` (not read).
- The documentation's use of the Violet form, and whether `README.md` and the lib READMEs use the owner's terms.
- The `docs/UML/app.mdj` wording (only a search line read).
- Whether the code's `Mode` in TEST_LAB (`test_lab_handlers.py:556`) is a separate concept (not read beyond the line).
- The text of the Gallery filter hover (not built, D-0404).
- Decision D-0034 (cited in `ledger:394`; its line was not read).
- The T3 node word: not found on screen or in help.
- Running the app: nothing was run; all screen text is from reading the code.