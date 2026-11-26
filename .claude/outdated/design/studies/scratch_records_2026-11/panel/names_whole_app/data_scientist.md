# Names across the whole app: the data scientist viewpoint (2026-11-21)

Labels: RUN = I ran it (scratch: `tmpAI/panel/names_whole_app/data_scientist_scratch/`); READ = file:line read; FACTS = taken from FACTS.md, not read again by me; REASONED = inference. I judged on merit; the column "reconsiders a decision?" is information only.

## Summary (6 lines)
1. Recommended: variant V1. One key per kind in every file kind: `id`, `ui_label` (short), `ui_title` (longer), `description` (one sentence), and for a column `ui_label` plus a rule that the column name is never replaced in an export.
2. The `ui_` prefix has one scientific meaning: text written for display. Changing it never changes a row of any table. Identities and column names are the only names that can change a result. This is a test that can fail (same tables before and after a rename).
3. `description` stays plain: it is part of the record (what the plot answers), so it must travel with the recipe and be exported. It also fixes a sidecar problem: the Gallery guidance heading lives in `example_meta.md`, which does not travel with a recipe copied to HOME.
4. One fallback for the whole app: no `ui_title` gives `ui_label`; no `ui_label` gives the id as written. Never invent text (today the report title-cases the id, `export_handlers.py:373`, which hides the real id).
5. Every display name must be unique in its scope after trim and case. Today a duplicate check is exact: "Bar chart" and "Bar chart " both pass (RUN).
6. A column display name (D-0360) needs a safety rule: the slug stays the name in every export and is always one click away, or a display name hides which column was used.

## 1. The kinds

| Kind | Purpose (one sentence) | Key everywhere | Who writes | Required? | Length and characters (number; error or advice) | Missing: what is shown |
|---|---|---|---|---|---|---|
| Identity | The name the program and the files use; never shown as a title; unique. | `id` for a file (recipe, app features); the map key for entries (group, plot, schema, join, field slug) | author | yes | `[a-z][a-z0-9_]*`, at most 40 (the bundle label is cut to 40, `export_handlers.py:2253-2260`, READ via FACTS). Breach = ERROR (it can change behaviour). App features names are kebab-case today (`app_features_validator.py:79-92`, FACTS): see decision 7 | not possible |
| Short name | The name in a tab, a list, a button, a dropdown. | `ui_label` | author (user for a session) | yes for recipe (`info`), group, plot; else optional | 1 to 30 characters after trim; no newline. Empty, blank or newline = ERROR. Over 30 = ADVICE (D-0405 says advice). Unique in its scope after trim and casefold = ERROR for tabs of one recipe and for the Gallery; ADVICE elsewhere | the id as written |
| Longer title | A heading, a banner or a report heading. | `ui_title` | author | no | 1 to 80 characters; over 80 = ADVICE; blank = ERROR | the short name |
| Description | One sentence that says what the thing is for or answers. | `description` | author | no; ADVICE when missing for recipe, plot, schema, join | one sentence, at most 300 characters; over = ADVICE | nothing shown; the advice is listed for the author |
| Meaning / help | Longer text shown only on demand. | no key in a recipe. Files: `app/src/help/*.md` per user space; the spec for Gallery terms (D-0399) | app developers | no | none | nothing |
| Column display name | What a column is called in a table view. | `ui_label` on the field entry (same key as everywhere) | author | no | as short name; unique among the columns of one table = ERROR | the column name (slug) |
| Text inside a figure | Title, axes, legend of the picture. | the `labs` layer, plotnine words (`title`, `x`, `y`, `fill`) | author | no | none | the plotnine default (the column name) |

Note: `comment` stays what it is, a note from author to author, not shown.

## 2. Matrix: thing against kind (cell = key of the scheme; "-" = none)

| Thing | Identity | Short name | Title | Description | Help | Column display | Figure text |
|---|---|---|---|---|---|---|---|
| Recipe | `id`, file name | `info.ui_label` | `info.ui_title` (banner) | `info.description` | - | - | - |
| Group | map key | `ui_label` | `ui_title` (needs a reader, case 5) | `description` | - | - | - |
| Plot | map key (the file name in exports) | `ui_label` | `ui_title` (report heading) | `description` | - | - | `labs` layer |
| Table (schema) | map key | `ui_label` | - | `description` | - | - | - |
| Join | map key | `ui_label` | - | `description` | - | `ui_labels` map (see case 9) | - |
| Column | slug (map key) | - | - | `description` | - | `ui_label` on the field | - |
| Action | registration name | `ui_label` (registry) | - | `description` | `yaml_example` | - | - |
| Plot component | registration name | `ui_label` | - | `description` | - | - | - |
| Panel | `type` | `ui_label` in the registry, the only place | - | - | in the user space help file | - | - |
| User space | internal value (`blueprint`) | `ui_label` ("Blueprint Architect") | banner text | - | help file | - | - |
| App features set | `name` | `ui_label` (was `display_name`) | `ui_title` (flat string) | `description` | - | - | - |
| Deployment | file path | `ui_label` (was `deployment_name`) | `ui_title` (was `branding.banner.title`) | `description` (was `banner.subtitle`) | - | - | - |
| Gallery example | folder = recipe `id` | the plot's `ui_label` (D-0387) | `info.ui_title` | the plot's `description` (one place) | filter term hover (D-0404) | - | `labs` |
| Session | session key | `ui_label` (typed by the user) | - | `description` (optional) | - | - | - |
| Export bundle | the file name from the user's label, cut to 40 | the bundle label | report title | - | README | - | - |

## 3. The cases

| Case | Today | In the scheme | What it changes | Reconsiders a decision? (info only) |
|---|---|---|---|---|
| `info.label` against `info.name` | New recipe writes `info.label` (`new_recipe.py:27-28`); the BLUEPRINT Info form writes `info.name` (`blueprint_handlers.py:2542, 2609-2610`). Both pass because `info` is free (FACTS, rspec:28). One thing, two keys, no error. | `info.ui_label` (short) and `info.ui_title` (header). `info.name` is refused with the new name. `info` stays free for other keys but the three name keys are checked. | BLUEPRINT form, new_recipe, checker, 16 shipped recipes, 34 Gallery recipes, docs | D-0405 (header block is now `info.ui_title`, meaning kept); the `label_keys` PENDING (M271) |
| `ui_label`, `label`, `name` for the short name | `ui_label` (group, plot); `label` (info, schema, join, field, session, action, component, node); `name` (Gallery index, app features id) | `ui_label` for every short name; `name` only as the id in app features; the index key `name` becomes `ui_label` | recipe format, registries, session file, index, loaders | D-0253 (extended to all places, as M271 words lean: "labels are ui_label because its what is shown in the ui") |
| `ui_title` recipe against app features | The recipe key is the longer plot or group name (report). The app features key is the HOME banner (`home_theater.py:1139`), no shipped file has it (FACTS) | Same meaning in both: the longer title. App features `ui_title` is a flat string; `ui_title.subtitle` becomes `description`. Add it to the validator and to `rules_app_features_flags.md` | app features validator and rule file | none found |
| Group `ui_title` read by nothing | no reader (FACTS C5) | Either the report uses it (group heading above its plots) or it is removed. My advice: give it the reader: a methods reader needs the group heading in the report | export report | none; format text `spec:485` says it is used |
| `description` as a tab text | group fallback `home_theater.py:105` | removed: one fallback rule (id, never description) | HOME code, one test | the format already says it goes (`spec:490`) |
| Gallery heading against the example name | name = plot `ui_label`; heading = `##` of `example_meta.md` | name = plot `ui_label`; the long text = the plot's `description` in the recipe; `example_meta.md` keeps only the cookbook guidance, no heading as a name source | 34 Gallery recipes, taxonomy reader, check | D-0397 (where the description lives, not that it is longer than the name); consistent with D-0252 |
| "Blueprint Architect" against "Wrangle Studio" | nav "Blueprint Architect", value "Wrangle Studio" in 2 handlers, the app README, 2 config YAML files (an app features file and a sidebar file) and 5 tests (grep, RUN) | internal value `blueprint` = the id; screen word = `ui_label`. Not stored in session or export (grep of `session_manager.py`, `export_handlers.py`: none, RUN), so no result changes | rename in code, YAML, tests | none |
| dataset, table, schema, collection, join | see section 4 | see section 4 | docs, screen | none |
| plot, figure, graph, chart | see section 4 | see section 4 | | D-0398 keeps "Chart type" |
| step, action, node | see section 4 | see section 4 | | |
| Join `labels` against plot `labels` (found by me) | join `labels` = column to display text (`recipe_check.py:847-849`, READ); a plot also allows `labels` (`recipe_spec.yaml:54`, READ) that feeds the figure labels (`plot_config_resolver.py:645-648`, READ). Same key, two jobs. No reader of the join one found (FACTS) | join: `ui_labels`; plot: the key is a figure text, which belongs to the `labs` layer (D-0253), so decide whether plot-level `labels` stays | format, checker, factory | D-0253 (figure text only in `labs`) |
| Field `label`/`description` (found) | the checker refuses `description` on a field (FD01), the BLUEPRINT card shows it (`wrangle_studio.py:1326`, FACTS) | `description` accepted on a field: a column definition (unit, meaning) is the most useful text a data reader can have | format, checker | D-0360 (refines) |

## 4. Words: one word per thing

| Thing | The one word on screen and in docs | Words it replaces | Where a second word stays |
|---|---|---|---|
| Whole recipe file | data analysis recipe ("recipe" short, after first use) | pipeline (as a name for the recipe), manifest | "pipeline" only in a deployment's folder name; "Pipeline Audit" is a different thing: see audit |
| The picture | figure (the rendered image, in the report) | chart, graph | "chart" only in the Gallery filter "Chart type" for the user (D-0398) |
| The recipe entry | plot (the specification, a tab) | | plotnine words (`geom`, `layer`) in YAML |
| Group | group (screen: group tab) | analysis group on screen | `analysis_groups` as the key |
| Anything with rows | table | dataset, data preview table, collection | `target_dataset` (format key), until renamed (decision 6); Polars words (LazyFrame) in code only |
| Source file as read | source table | original file, data file | `original_name` (the file header, exact) |
| Definition of a source table | schema | data schema | `data_schemas` key |
| Joined table | join (the operation), joined table (the result) | collection | `collection_id` in code |
| One entry of a step list | step | wrangling step, transformation node, node | `steps` key |
| The kind of operation chosen | action | | `polars_*` names |
| Audit | audit step (what the user sends); Audit mode | audit node, filter and drop | `t3_audit_steps_by_plot` key |
| Export | export bundle; import bundle | results bundle, reproducibility bundle, reimport bundle | the file name `..._results.zip` |
| Notes panel | Alerts | Notification Log | registry id `notification_log` |
| Spaces | Blueprint Architect, Test Lab, Gallery, Home | Wrangle Studio, Dev Studio, Flight Deck | uppercase BLUEPRINT/TEST_LAB only in internal docs (CLAUDE.md) |
| A column's identity | column name (slug) | field name | "field" = the entry in `input_fields`, never the name of the column |
| Display name | display name (`ui_label`) | alias, label (when it means display name) | none |

Not on the retired-words list today: `label`, `title`, `name` (`assets/scripts/audit_old_words.py:32-40`, FACTS).

## 5. Variants

| | V1 (recommended) | V2 | V3 |
|---|---|---|---|
| Rule | `ui_` for text written for display, plain `description`, same key in every file kind | plain `label`/`title`/`description` everywhere | keep today's keys, fix only the collisions |
| Recipe format and version | rename `info.label`, schema, join, field `label` to `ui_label`; add `info.ui_title`; join `ui_labels`. `format_version` changes (rspec header says a key change does) | the opposite: group and plot `ui_label` back to `label`, `ui_title` to `title` | `info.name` refused; app features `ui_title` renamed; unread keys removed; no format change |
| Checker | new rules: unique, trim, length advice, blank error; `label_keys` table removed | same rules, other keys | collision checks only |
| Code | registries (action, component, parameter) `label` to `ui_label`; session and Gallery index keys; HOME/export fallbacks | same count | small |
| Shipped recipes and 34 Gallery | all rewritten in one pass by a script | all rewritten, undoing D-0253 | 16 + 34 touched only for `info.name` |
| App features and deployment | `display_name`, `deployment_name`, `ui_title.text`, `banner.title/subtitle` renamed; refused with the new name through `renamed_keys.py:17-69` (the existing mechanism) | `title`, `label` | one key |
| Docs and tests | Terminology, Standards_yaml (axis title claim removed), authoring guide, UML; tests for each rule | same | few |
| One pass, old key refused? | yes: migration script + checker error that names the new key; no alias | yes | not needed |
| Scientific effect | none on tables; recipes in old bundles are refused on re-import until migrated (tell the user) | same | none |
| Left unsolved | nothing | `label` keeps at least eight jobs (FACTS section 4); plotnine collision | the same kind has two keys (`label` and `ui_label`) in one recipe |

Why V1, on merit: one key per kind lets a recipe author, a checker and a methods reader treat the same kind the same way. The prefix tells a reader that this text is cosmetic, which is exactly what a reviewer asks. V3 leaves M271 open and the two-key inconsistency. V2 puts a plain word that plotnine also uses back into the recipe.

## 6. Keeping it true

1. One place: the recipe spec `libs/utils/src/utils/recipe_spec.yaml` (it already holds `label_keys`): a `name_kinds` table (kind, key, required, max length, severity). The documentation form is generated from it (as D-0399 does for Gallery terms).
2. The checker reads the table; each severity above is a finding code.
3. A test that can fail: change every `ui_*` and `description` in a recipe, run the pipeline, compare the T3 tables and the plot data: identical.
4. `audit_old_words.py`: add retired keys (`info.name`, `display_name`, `deployment_name`, `ui_banner`) as refused names; add the retired words of section 4.
5. One rule file for the kinds (not a copy of the table, a pointer to the spec).

## 7. What a reader and an author need

- A reader of a methods section can cite: recipe `id` + `info.version` + plot `id` (the plot file name in the export, `export_handlers.py:1307`). The title and the label are not stable citations; say so in the README. The export records the contact origin but not the deployment or app features set that produced it (grep of `export_handlers.py` for `display_name`/`deployment_name`: none, RUN): add them to the export record, which also gives `deployment_name` its first reader.
- The report heading shows the plot name, the figure file is named by the id: add the id beside the heading so the two can be matched.
- Column display names (D-0360): in a table view show the display name and the slug on hover; never in a data file or an audit step. An audit step that filters on a column must name the slug (the step is a result of the recipe, `Result plus the steps`). Two columns with one display name is an error.
- Author guidance: short name = what I click (a noun phrase, at most 30 characters); title = a heading for a reader who sees only this; description = one sentence: what it answers, for which population, from which table.

## RUN findings (silent risks)
- Duplicate names pass if they differ by trailing space or case: `example_name` returns the text as written (`taxonomy.py:55-66`, READ) and `_repeats` compares exactly (`gallery_manager.py:113-117`, READ). RUN: "Bar chart" and "Bar chart " both accepted; "bar chart" differs from "Bar chart". Two examples can look the same in the dropdown.
- A blank `ui_title` (" ") wins over `ui_label` in the report: `plot_report_name` uses `or`, a space is truthy, so the heading is empty (RUN on a copy of the logic; `export_handlers.py:373`).
- A whitespace-only `ui_label` raises in the Gallery (RUN: ValueError), but the HOME tab would show it empty (REASONED).
- The report title-cases the id when both names are missing, so "p_one" becomes "P One" (READ): a name invented by the program.

## To decide first (ranked)
1. Is `ui_label` the key of the short name for every thing, including `info`, tables, joins, columns, registries (the M271 question)? Or only where it is shown today?
2. Is the recipe's header title `info.ui_title` (V1) or does `info.label` stay (D-0405 words)?
3. Where does the Gallery description live: the plot `description` in the recipe (travels with it), or the `example_meta.md` heading (D-0397)?
4. Column display names: when shown, must the slug be visible, and may an audit step or an export carry a display name? (my rule: never in data files or steps)
5. Does a group `ui_title` get a reader in the report, or is it removed?
6. Does `target_dataset` become `target_table` (one word "table")?
7. One id style: snake_case for recipes, kebab for app features: keep or unify?
8. Do the deployment and the app features set get written into the export record?

## Not verified
- Where BLUEPRINT and HOME show a plot or group `description` (none found, FACTS).
- Who reads the join `labels` (none found by search).
- What the recipe chooser shows (id or `info.label`).
- Column names in the Gallery data sample and the export data files.
- The severity of FD01; the lengths of the shipped recipes (not re-measured).
- Whether the nav value "Wrangle Studio" is stored in any session written by an older version.
- The files and keys count of each variant beyond FACTS.md; a script to migrate was not written.
