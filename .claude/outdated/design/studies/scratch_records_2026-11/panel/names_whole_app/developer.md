# DEVELOPER viewpoint: one scheme for names across the whole app (2026-11-21)

Labels: RUN = I ran it; READ = read at file:line; REASONED = my inference. Counts are from `grep` on `dev`, excluding `worktrees/`, `.venv/`, `tmpAI/`, `outdated/`. Nothing was changed. `FACTS.md` and the table of `name_fields` were read; I rely on their file:lines and only re-checked the ones named below.

## Summary (6 lines)
1. Seven kinds, three authored keys: `ui_label` (short name), `ui_title` (longer title), `description` (one sentence). `original_name` (column source) and the `labs` layer (figure text) stay as they are. Identity has no key (it is the mapping key or file name). Help text has no recipe key (help files, registry `description`, spec).
2. The same four keys in every file kind (recipe, app features, deployment, Gallery example, session), so `display_name`, `deployment_name`, `branding.banner.title`, the `label` of schema, join, field, session and the `info.label` / `info.name` pair all go.
3. One fallback rule for the whole app, one function that every screen and the export call: title, else short name, else the id exactly as written; a description falls back to nothing (no invented text).
4. Recommended: variant B (the `ui_` prefix for the three display kinds, everywhere an author or deployer writes a file). It reuses the exact mechanism of ADR-091 (a `renamed` table, a refusal naming the new key, a migration script, an audit script). Variant A (fix collisions only) is the smallest but does not give one rule; variant C (plain keys) is the largest and re-opens the collision with plotnine that D-0253 closed.
5. Size of B (RUN, outside worktrees): `ui_label` 213 files / 580 lines; `ui_title` 67 / 137; `info.label` 24 / 34; `info.name` 13 / 23; 115 of those files are tests. 109 recipe yaml in `config/data_analysis_recipes`, 34 Gallery recipes in `assets/gallery_data`, 12 Python files in `app/` and `libs/` read `"label"` by hand.
6. One check hazard found: `info` is free-form (`recipe_spec.yaml:28`), so an old `info.label` or `info.name` is NOT refused by the generic key check; only `info.display_name` has its own code (`recipe_check.py:315`). The refusal must be written explicitly or the "old key refused" rule does not hold for the recipe's own name.

## 1. The kinds (the scheme of variant B)

Rules shared by all: keys are lowercase snake_case; one key per kind; no key may be accepted beside its old name; every rule has a number, a severity and a single place (the spec, section 6).

| Kind | Purpose (one sentence) | Key everywhere | Who writes | Required? | Length and characters (proposal; severity) | If missing |
|---|---|---|---|---|---|---|
| 1 Identity | Names the thing for the program and for other files; never shown. | none: it is the mapping key or the file name. A file kind may need its own character rule: recipe, group, plot, schema ids are snake_case; app features names use hyphens (`app_features_validator.py:79-92`, READ via FACTS), the folder name equals the recipe `id` | author / deployer | yes | `^[a-z][a-z0-9_]*$` (recipe side), hyphens for app features; error | file refused |
| 2 Short name | What a tab, a list row, a button or a badge says. | `ui_label` | author / deployer | yes for anything that is listed or tabbed (recipe, group, plot, table, join, column, app features, session optional); no for a step | at most 32 characters, one line, no markup, not blank; blank or a newline = error; over 32 = advice (D-0405: advice at most). Evidence: plot 9-28, display_name up to 31 (FACTS 2.2, Gallery table) | the id as written (one fallback rule, below) |
| 3 Longer title | A heading, a banner, a report heading. | `ui_title` | author / deployer | no | at most 80 characters, one line; over 80 = advice | the short name, else the id |
| 4 Description | One sentence that says what the thing is for, shown as a hover or an info line. | `description` (no prefix: it is never a plotnine key) | author | no; a missing one on a recipe, table, join, Gallery example is an advice (as today, S04, J03) | one sentence, at most 200 characters; over = advice | nothing is shown (never an invented sentence) |
| 5 Help text | The meaning of a word or a setting, shown on demand. | no recipe key: help files, registry `description`, the spec (D-0399, D-0404) | maintainers | n/a | none | no mark |
| 6 Column display name | What a column is called on a screen, without renaming the column. | the field's `ui_label` (D-0360 alias; M271 asks this very place) | author | no | as kind 2 | the column name |
| 7 Text in a figure | Title, axes, legend inside the picture. | the `labs` layer only (D-0253); plotnine words stay | author | no | none | no title in the picture |

Fallback rule, one for the app: title = `ui_title` else `ui_label` else the id exactly as written. One function (proposal: `display_name(kind, entry, id)` in `libs/utils`) replaces the separate fallbacks today (`export_handlers.py:367-373` title-cases the id; `home_theater.py:105,109-115` falls to the group description or `entry.get("name")`).

## 2. Matrix: thing against kind (cell = key)

| Thing | Identity | Short `ui_label` | Title `ui_title` | `description` | Column display | Figure text |
|---|---|---|---|---|---|---|
| Recipe (`info`) | `id` = file name | `info.ui_label` (required) | `info.ui_title` (HOME banner, report) | `info.description` | - | - |
| Group | key | `ui_label` | `ui_title` (needs a reader, see to decide 4) | `description` | - | - |
| Plot | key | `ui_label` | `ui_title` | `description` | - | `labs` |
| Table (schema) | key | `ui_label` | - | `description` | - | - |
| Join | key | `ui_label` | - | `description` | - | - |
| Column (field) | slug; `original_name` | - | - | `description` (see to decide 5) | `ui_label` | - |
| Action / plot component | registered name | registry `label` (see to decide 6) | - | `description` (is the help) | - | - |
| Panel (sidebar type) | `type` | registry `label`, made the real accordion title | - | - | - | - |
| User space | HOME, BLUEPRINT, TEST_LAB, GALLERY | nav text | banner text | first line of its help file | - | - |
| App features set | `name` (hyphens) | `ui_label` (was `display_name`) | `ui_title` (HOME banner, was `ui_title.text`) | `description` | - | - |
| Deployment | file path | `ui_label` (was `deployment_name`) | `branding.banner.ui_title` (was `title`) | `branding.banner.description` (was `subtitle`) | - | - |
| Gallery example | folder = recipe `id` | the plot `ui_label` (D-0387) | `info.ui_title` | the plot `description` (see to decide 3) | - | - |
| Session | key | `ui_label` (was `label`) | - | - | - | - |
| Export bundle | file name made from `ui_label` | `ui_label` (was `export_user_name`) | - | - | - | - |

## 3. The cases

| Case | Today | In the scheme | What it changes | Reconsiders a decision? (information) |
|---|---|---|---|---|
| `info.label` against `info.name` | `new_recipe.py:27-28` writes `label`; BLUEPRINT form reads and writes `name` (`blueprint_handlers.py:2542, 2609`); `info` is free so nothing is refused | one key: `info.ui_label`; the form field says "Short name"; `label` and `name` of `info` refused with the new key | new explicit refusal code beside `recipe_check.py:315`; form, factory, 16 shipped recipes, 34 Gallery, tests | M271 (pending) answered; D-0405 wording ("`info.label`") moves to `info.ui_label`; spec 367/105/179/192 |
| `ui_label` / `label` / `name` as the short name | at least 8 jobs for `label` (FACTS section 4) | `ui_label` only; registries (Python dicts) are the one place that may keep `label`, see to decide 6 | `label_keys` table (4 lines), `renamed`, 12 reader files | D-0253 (extended to the other places), D-0237 |
| recipe `ui_title` against app features `ui_title` | same word, two files; the app one wins over `info.label` (`home_theater.py:1141`) | the same kind in both: the heading. One precedence line in the spec: app features / deployment title, else `info.ui_title`, else `info.ui_label` | the app features `ui_title: {text, subtitle, visible}` becomes `ui_title`, `description`, `visible`; `renamed_keys.py` gets the old names | none |
| a group's `ui_title`, read by nothing | format says report and headings | give it its reader in the report (group heading), or remove the key from the spec; never leave a documented key unread | report code (`export_handlers.py`) or spec + tests | none (spec 485 is design text) |
| `description` used as a tab text | `home_theater.py:105` | removed; the tab is `ui_label` then id | one line plus its test; the spec already says "goes" (`spec:490`) | none |
| Gallery heading against the example name | name = plot `ui_label`; heading in `example_meta.md` | name = `ui_label`, description = one source (see to decide 3) | generator and checker | D-0397 only if the source moves |
| "Blueprint Architect" against "Wrangle Studio" | nav text vs internal value in 6+ places | one visible word "Blueprint"; the internal value becomes `BLUEPRINT` (same as the id in `CLAUDE.md:13`); the class and file `wrangle_studio.py` are code modules and keep their names | `home_theater.py` (1049, 2132, 2341), `blueprint_handlers.py` (943, 972), help map, tests; sessions that store the space name need a check (not verified) | none; `app/README.md:8` and `Terminology.qmd:33` change |
| dataset / table / schema / collection / join | see section 4 | see section 4 | | |
| plot / figure / graph / chart | | see section 4 | | |
| step / action / node | | see section 4 | | |

## 4. Words on screen and in the docs (one word per thing)

| Thing | Word on screen and in the docs | Words it replaces | A second word that must stay |
|---|---|---|---|
| the YAML file | data analysis recipe (short: recipe, in running text only) | pipeline (folder, "Pipeline Audit" is a different thing: see below), manifest | `data_analysis_recipe` as code and file names |
| what the plot makes | plot | figure, graph, chart | `figure` in plotnine / matplotlib code, `chart` only as the decided Gallery axis "Chart type" (D-0398) |
| a table as the user sees it | table | dataset, data preview table, source table | Polars: `DataFrame`/`LazyFrame`; the format key `data_schemas`; "dataset" is a data-provider word (`target_dataset`), keep it in code |
| the definition of a table | schema (screen: "table definition" in help) | data schema | key `data_schemas`, `input_fields` |
| the combined table | join | ingredients (format key stays), Joint Designer (typo) | `joins` key |
| a user operation | step | action (picker), node, transformation node | `@register_action` and `polars_*` names are code; the picker header may say "step type" |
| a node of the lineage | node (lineage only) | step | cytoscape word |
| Export button | Export bundle (one name) | results bundle, reproducibility bundle, reimport bundle | none |
| Alerts panel | Alerts (screen); registry label made equal | Notification Log | module name `notification_log` |
| BLUEPRINT space | Blueprint | Blueprint Architect, Flight Deck, Recipe Editor, Surgeon, Wrangle Studio | class names |
| user space against code module | user space for HOME, BLUEPRINT, TEST_LAB, GALLERY; code module for files | mixing them (`CLAUDE.md:18`) | |
| word for the name kinds | "short name", "title", "description" in all docs; the keys are shown in code font | "label" in prose for the short name, "title" for `info` (`Terminology.qmd:8`) | `labs` params `title`, `x`, `fill` (plotnine) |

## 5. Variants

| | A. Keep keys, fix collisions | B. `ui_` prefix for the three display kinds, everywhere (recommended) | C. Plain `label` / `title` / `description` everywhere |
|---|---|---|---|
| Idea | `info.name`->`info.label`; no reader-less keys; add advices | `ui_label`, `ui_title`, `description` in recipe, app features, deployment, session, export | the three plain words in every file kind |
| Keys left for the short name | `ui_label`, `label` (schema, join, field, info, session), `display_name`, `deployment_name`: five | one | one |
| Recipe format and version | none in the keys; `format_version` stays 1 | the rename of `info`, schema, join, field changes the format: `format_version` 2 or an amendment before release (the file says it was amended before the first release, `recipe_spec.yaml:3-8`; whether a release has happened: not verified) | same plus the reversal of D-0253 on group and plot |
| Checker | 2 codes (info.name, group `ui_title` reader) | `label_keys` four lines (`recipe_spec.yaml:12-17`), `renamed` entries, explicit info refusal, `name_kinds` limits | same, plus a tombstone for the already refused plot `label` that now becomes valid again: the refusal text must change ("renamed ui_label" is the current message) |
| Code | `blueprint_handlers.py` and `home_theater.py` lines | 12 reader files (`session_manager`, `gallery_viewer`, `export_handlers`, `audit_stack`, `schema_registry`, `agent_tools`, `data_analysis_recipe_navigator`, ...) plus the shared function | the same, and every `ui_label` and `ui_title` reader (213 and 67 files) goes back |
| Recipes | 16 shipped (`info.name` check), 0 Gallery | 109 yaml in `config/data_analysis_recipes`, 34 Gallery recipes, 34 `example_meta.md` untouched | the same set, doubled by the reversal |
| App features and deployment | none | `renamed_keys.py` entries; the shipped app features files, the deployment files, the template (counts not taken); session JSON: old sessions need a refusal or a migration (sessions are user files on disk, `session_manager.py:384`) | the same |
| Docs | 4 passages | `Terminology.qmd`, `Standards_yaml.qmd:47`, `data_contracts_adr.qmd`, authoring guide, UML note `app.mdj:34603` | the same, plus the plotnine confusion in all of them |
| Tests | few | 115 files hold the names (RUN count); most are fixture edits that a script does | larger |
| Old key refused in one pass | n/a | yes: `renamed` table + migration script + audit rule (below) | yes |
| Honest limit | one rule only in the docs, five keys remain | registries keep `label` unless to decide 6 says otherwise | collides with `labs.title` and `labs.x` in author's minds; `label` had at least 8 jobs |

How the pass is made without a shim (REASONED from ADR-091's practice, READ `renamed_keys.py`, `migrate_recipe_format.py`): the migration script edits text so comments stay, prints a list without `--apply`, and is safe to run twice. Sequence: (1) write the new keys in the spec and the old ones in `renamed`; (2) run the script on a copy and read the list; (3) in one merge: the script applied to every recipe, fixture and Gallery file, the readers, the checker, the tests. No release or merge exists in which both keys work. The checker then refuses any file that still has an old key and names the new one.

## 6. How the scheme stays true (REASONED)
- One place: a `name_kinds:` block in `libs/utils/src/utils/recipe_spec.yaml` (kind, key, purpose, required, length, severity, fallback). The checker, the migration script, the generated documentation (D-0399 asks the same for Gallery terms) and the screens read it. A parallel block for app features and deployment files in their own spec file, because those loaders do not read the recipe spec.
- One function `display_name` and one `check_names` in `libs/utils`; the screens call it; a test greps the readers (`app/`, `libs/`) so that a screen reading `"label"` or `["ui_title"]` directly fails.
- `assets/scripts/audit_old_words.py` gets the retired keys (a second table: `display_name`, `deployment_name`, `info.name`, plain `label` outside registries) and the words of section 4 for screen text; it already runs from `app/tests/test_audit_old_words.py`.
- A rule file `.claude/rules/rules_names.md` (the kinds in one table, linking to the spec) and a line in `CLAUDE.md` section 1.
- A test per kind: the key exists only in the spec; a file with an old key is refused with the new name; a blank or newline `ui_label` is an error; 33 and 81 characters are advices; the fallback is the same for HOME, BLUEPRINT, the Gallery and the report (one parametrised test).

## Recommendation: variant B
On merit: it is the only one that gives each kind one key in every file kind, it answers M271 and the `info.label` / `info.name` split, it removes the two-meaning `ui_title`, and its rename path already exists in the repository. Cost, as information: B changes the sentences of the format (`spec:105,179,192,367`), D-0253 (extended), D-0405 (key moves to `info.ui_label`), D-0237, and M271 gets its answer. A would leave five short-name keys; C would reverse D-0253.

## Build order (each step leaves a working app; model/effort from CLAUDE.md section 2)
1. Owner's answers to "To decide first" `[opus/high]` (a decision, nothing built).
2. Tests rewritten to the new design, and the `name_kinds` block in the spec with `display_name` and `check_names` in `libs/utils` `[sonnet/high]`: pure code, no recipe touched, no screen touched. Risk: low; app unchanged.
3. Migration script, dry run on a copy, list read by a reviewer `[sonnet/medium]` (a script, mechanical; the check of its output is the real work).
4. One atomic merge: script applied to recipes, Gallery, fixtures; readers in the 12 files; checker refusal incl. info; `label_keys` flipped `[sonnet/high]`, reviewer `[opus/high]`. This is the risky step; it must be one piece because the old key is refused.
5. App features and deployment keys (`renamed_keys.py`, 8+3 files, template, validators) `[sonnet/medium]`. Own files, own worktree; touches `home_theater.py` banner lines, so merge after 4.
6. Screen words and help files (section 4) `[haiku/low]` for the list, `[sonnet/medium]` for the code lines. Parallel with 5 except in `home_theater.py` and `blueprint_handlers.py`.
7. Docs, UML note, Terminology, spec sentences, rule file, audit script entries `[sonnet/low]`; docs can start at step 3 in parallel.
8. Sessions: refusal or migration of old `label` `[sonnet/high]`, last, because it touches user files.

Regression risks (REASONED): a reader missed by grep (the 12 files read `"label"` through `.get`; the test in section 6 catches the rest); the Gallery duplicate-name refusal (`gallery_manager.py:113-117`) message names `ui_label`, already right; old sessions; HOME banner precedence changing silently (a test fixes it).

## To decide first (ranked)
1. Do the three display kinds take the `ui_` prefix in every file kind (B), only in recipes (today), or none (C)? Consequence: A leaves five short-name keys; C reverses D-0253.
2. `info`: one pair `info.ui_label` (short, required) and `info.ui_title` (banner, optional)? Consequence: HOME banner = `ui_title`, else `ui_label`; the 16 shipped recipes need their long `info.label` text moved to `ui_title`.
3. Gallery example description: one source, the plot `description`, or the `example_meta.md` heading (D-0397)? Consequence: two sources is the same defect as today.
4. A group's `ui_title`: a reader in the report, or removed from the spec?
5. A field's `description`: the BLUEPRINT card reads it, the checker refuses it (`recipe_check.py:478-489`, FD01). Accept it or remove it from the card.
6. Registries (actions, plot components, panels): keep their Python key `label` (written by maintainers, not authors, about 900 lines under `viz_factory`) or rename it? Consequence: keeping it leaves a second key name by decision, and says so in the spec.
7. The numbers 32, 80, 200 and whether over-length is an advice (my proposal) or an error.
8. Format version: bump to 2 or amend format 1 (needs the fact whether format 1 has been released).
9. Sessions: refuse old sessions with `label`, or migrate them.

## Not verified
Whether format 1 was released (decides item 8); how sessions store the user-space value "Wrangle Studio"; whether the 900 `label` lines in `viz_factory` are registry keys or plotnine arguments (I counted the word, not the role); the reader of the collection `labels:` and the figure caption source (FACTS "not verified"); severity of FD01; the numbers 32, 80, 200 are proposals set from the measured lengths in the Gallery table and FACTS 2.2, not from a statistical survey; the 115 test files were counted by the word, not opened. I did not run the checker or the app.
