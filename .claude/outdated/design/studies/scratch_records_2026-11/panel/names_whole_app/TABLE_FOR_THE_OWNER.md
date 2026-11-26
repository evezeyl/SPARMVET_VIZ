# One purpose and one rule for every name in the app: one table for the owner (2026-11-21; your order "again we have a purpose of each component problem")

## 0. How to read this
- Four viewpoints read a survey of the whole app and proposed one scheme each: the architect, the data scientist, the developer, and a user new to data science. A scout made the survey (`FACTS.md`). They are in `tmpAI/panel/names_whole_app/`. This file is written from them, by one writer, who decides nothing.
- READ = read at a file and line. RUN = a command was run. REASONED = an inference. Nothing in the app was run by the viewpoints. I ran three small checks myself (marked "RUN by the writer").
- Nothing is changed. No proposal here is a decision. Where the viewpoints differ, each is shown in one line and not settled.
- Your rule: an option is judged on merit. "It reconsiders a decision" is only information, in its own column. It is never a reason for or against an option.
- The companion table is `tmpAI/panel/name_fields/TABLE_FOR_THE_OWNER.md` (the name fields of a recipe; I call it "the recipe table"). Read both together. I do not repeat it; I point to its sections.
- Short forms: Arch = architect, DS = data scientist, Dev = developer, User = user new to data science.
- The viewpoints used different letters for the same three variants. I use P, Q and R in section 6 and say which is which.

---

## 1. What is wrong today, in plain words

| # | What a user or an author meets | Where | Evidence |
|---|---|---|---|
| 1 | In BLUEPRINT, the form of the recipe's Info has a field "Name" ("Short display name"). It writes `info.name`. HOME's title banner reads `info.label` (the recipe's own name key). So you type a name and nothing shows it. The checker accepts both, because `info` takes any key. | BLUEPRINT, HOME, recipe | READ `app/handlers/blueprint_handlers.py:2542, 2609-2610`; `libs/blueprint_arch/src/blueprint_arch/new_recipe.py:27-28` writes `info.label`; READ by the writer `home_theater.py:1141-1144`. RUN by the writer: `info.name` is in 0 of 8 recipe files with a top-level `info` in `config/data_analysis_recipes`, and in 0 of the 34 Gallery recipes. So it is a hazard, not yet a case in shipped files. |
| 2 | One user space has seven names: Blueprint Architect, Wrangle Studio, Flight Deck, Recipe Editor, Surgeon, Blueprint, BLUEPRINT. A newcomer may think they are seven tools. Wrangle Studio is the internal value of the nav item, in six places. | BLUEPRINT | READ FACTS 2.8 (`home_theater.py:1049, 1893, 2132, 2341`; `blueprint_handlers.py:943, 972`; `sidebar_registry.py:69, 73`; `wrangle_studio.py:267`). The other two spaces also have several names (Gallery: Inspiration, Explorer, Taxonomy; Test Lab: Dev Studio, Tools, LAB). |
| 3 | Six buttons say "Apply" and have six different effects: filter, audit, BLUEPRINT form, join, data import, plot style. | HOME, BLUEPRINT | READ FACTS 2.8 (`filter_and_audit_handlers.py:644`; `audit_stack.py:699, 798`; `blueprint_handlers.py:1739, 1996`; `data_import_handlers.py:237`). |
| 4 | The same thing has several words: table / dataset / source table / collection; plot / figure / graph / chart; step / action / node; export / results bundle / reproducibility bundle / reimport bundle. | screens, help, documentation | READ FACTS section 5 (the full list with file and line). |
| 5 | One key has several jobs. `label` has at least eight (recipe name, table, join, column, session, action picker, component picker, lineage node). `ui_title` is a longer plot name in a recipe and a banner object in app features. `description` is also used as a tab text. `labels` is a column-to-text map in a join and a figure text in a plot. | recipe, app features, registries | READ FACTS section 4; `recipe_check.py:847-849` (join `labels`); `recipe_spec.yaml:54` and `plot_config_resolver.py:645-648` (plot `labels`), found by DS. |
| 6 | Fields are written and read by nothing: a group's `ui_title`; the panel registry's `label`; the deployment's `deployment_name` (the template says "shown in app footer"; no footer was found); `info.submission_date`; a join's `labels`; a plot's `description`. | recipe, deployment, sidebar registry | READ FACTS section 6; recipe table section 3. |
| 7 | Five different fallbacks when a name is missing. A group falls back to its description (a sentence as a tab). A plot in the audit list falls back to a key (`name`) that the format does not have. The report writes the id in title case ("p_one" becomes "P One"), a name the program invents. The Gallery has no fallback and raises. | HOME, report, Gallery, BLUEPRINT | RUN by Arch (grep, seven readers); READ `home_theater.py:104-105, 114-115`; `export_handlers.py:368-373`; `taxonomy.py:55-66`. |
| 8 | A mistyped key in an app features file or a deployment file is accepted silently. The recipe refuses unknown keys; these two file kinds have no list of allowed keys. | app features, deployment | READ Arch (`app_features_validator.py` has no key list; `renamed_keys.py:96-150` tests only known old names). |
| 9 | The check for two examples with one name compares the text exactly. "Bar chart" and "Bar chart " (trailing space) both pass and look the same in the dropdown. | Gallery | RUN by DS (copy of the logic); READ `taxonomy.py:55-66`, `gallery_manager.py:113-117`. |
| 10 | A `ui_title` that is a blank space wins over `ui_label` in the report, and the heading is empty. | report | RUN by DS (copy of the logic); READ `export_handlers.py:373`. |
| 11 | A column's `description` is refused by the checker (finding FD01) and shown by BLUEPRINT's field card. | recipe, BLUEPRINT | READ FACTS 2.3 (`recipe_check.py:478-489`; `wrangle_studio.py:1326`). Severity of FD01 not read. |
| 12 | Seven panel titles on screen differ from the name in the registry (FACTS table: 6 marked "no", 3 "not found"); the registry copy is read by nothing. | HOME and the other spaces | READ FACTS 2.2 table; Arch counts "7 of 20" (the two counts differ; see section 11). |
| 13 | The session box says "Describe this session..." but its text is used as the session's name; the session card shows the recipe id, not the name. | HOME | READ FACTS 2.7 (`session_handlers.py:224-226, 258`). |
| 14 | Two docs say things the decided rules say the opposite of: `Standards_yaml.qmd:47` calls a column's `label` "also the default axis title of a plot" (D-0253: figure text only in `labs`); `Terminology.qmd:8` calls `info` "title, description, ...". | documentation | READ FACTS 2.9. |

---

## 2. The idea in one page

Seven KINDS of name. Every viewpoint arrived at the same seven.

| Kind | Purpose, in one plain sentence | Shown where | Who writes it |
|---|---|---|---|
| Identity | The name the program and files use; never shown as a title; unique. | nowhere (or in a file name) | author or developer |
| Short name | What a tab, a list row, a button or a dropdown says. | tabs, lists, dropdowns | author, deployer, developer |
| Longer title | A heading, a banner or a report heading. | HOME banner, report | author, deployer |
| Description | One sentence: what the thing is for, or what it answers. | an info line or hover (today mostly nowhere) | author |
| Help or meaning | Shown only when the user asks (hover, click, panel). | help files, hover | developer, owner |
| Display name of a column | How a column is called in a table view, without renaming the column. | table views, lists | author |
| Text inside a figure | Title, axes and legend inside the picture. | the picture | author (in the `labs` layer; plotnine's own words) |

**Where all four viewpoints agree:**
- One fallback rule for the whole app, by one function that every screen, the report and the Gallery call: title, else short name, else the id exactly as written. A description has no fallback: nothing is shown and, for a recipe, a table or a join, an advice is given. Never invent text; never use the description as a tab.
- The text inside a figure stays only in the `labs` layer (D-0253). Help has no key in a recipe.
- A name too long is an advice, not an error (D-0405 says "an advice at most"). A blank name or one with a line break is an error (DS, Dev).
- The old key is refused with the new name, not accepted beside it. One pass per file kind.
- One place writes the kinds, keys and numbers; the documentation is generated from it (the way D-0399 does for Gallery terms). Architect: a new file `libs/utils/src/utils/names_spec.yaml`. DS and Dev: a block `name_kinds` in `recipe_spec.yaml` (and Dev: a second file for app features and deployment).
- All four recommend the same variant, P (section 6). Their reasons differ.

**Where they differ** (each shown, none settled): the numbers for "short", "long" and "one sentence" (30 / 80 / 200 Arch; 30 / 80 / 300 DS; 32 / 80 / 200 Dev; 30 / 80 / 160 User); whether `description` has a `ui_` prefix (User only: `ui_description`); the word for a picture (DS: figure; the others: plot); the word for the BLUEPRINT space; the registries' `label` (section 4, row 14). More in section 10.

---

## 3. The matrix: thing against kind

Key shown is the key of variant P (prefix `ui_`). A blank cell = not needed. Where viewpoints differ, the cell names them.

| Thing | Identity | Short name | Longer title | Description | Help | Column display | Figure text |
|---|---|---|---|---|---|---|---|
| Recipe | `id` (= file name) | `info.ui_label` (all) | `info.ui_title` (all; Arch adds `ui_subtitle`) | `info.description` (User: `info.ui_description`) | help file (Arch, User) | | |
| Group | map key | `ui_label` | `ui_title` (needs a reader: all) | `description` (User: `ui_description`) | | | |
| Plot | map key (the file name in exports) | `ui_label` | `ui_title` | `description` (User: `ui_description`) | | | `labs` layer |
| Table (schema) | map key | `ui_label` | | `description` | | | |
| Join | map key | `ui_label` | | `description` | | Arch: join `labels`, one place with the field (open); DS: `ui_labels` | |
| Column (field) | slug (map key); `original_name` is the source header (Dev) | | | `description` (Arch, DS, Dev accept it; User: not listed) | | `ui_label` (all) | |
| Action | registered name | `ui_label` (Arch, DS, User); Dev: registry keeps `label` (open) | | `description` | Arch: the description in the help panel; DS: `yaml_example` | | |
| Plot component | registered name | same as action | | `description` | help registry (Arch) | | |
| Panel (sidebar) | `type` | `ui_label`, one store, read by the renderer (Arch, DS); Dev: registry `label` becomes the real title; User: today read by nothing | | | | | |
| User space | internal value (Arch, Dev: the id, never shown) | `ui_label` (Arch, DS); Dev, User: the nav text | banner text (DS, Dev, User) | Dev: first line of its help file | help file | | |
| App features set | `name` (Arch: renamed `id`; the others keep `name`) | `ui_label` (today `display_name`) | `ui_title`, a flat string (Arch: plus `ui_subtitle`, and `visible` moves to the flags; DS: subtitle becomes `description`) | DS, Dev: `description` | | | |
| Deployment | file path | `ui_label` (today `deployment_name`); Arch: or delete it | `ui_title` (today `branding.banner.title`) | DS: `description` (today `banner.subtitle`); Dev: `branding.banner.description`; Arch: `ui_subtitle` | | | |
| Gallery example | folder = recipe `id` | the plot's `ui_label` (D-0387) | `info.ui_title` (Arch, DS, Dev) | Arch: `info.description` (open); DS, Dev: the plot's `description` (Dev: open); User: plot `ui_description` | filter-term hover (D-0404); the guidance page | | `labs` |
| Session | session key | `ui_label` (all; today `label`) | | DS: optional `description`; User: optional note | | | |
| Export bundle | file name from the user's text, cut to 40 | the user's text (Arch: `ui_label`; Dev: replaces `export_user_name`) | report title | | README | | |

---

## 4. The cases

"Today" gives the evidence. The last column is information only.

| # | Case | Today | What each viewpoint proposes | What it changes for a user or an author | Reconsiders a decision? (information) |
|---|---|---|---|---|---|
| 1 | `info.name` against `info.label` (section 1, row 1) | Two keys; the form writes one, HOME reads the other; nothing refused. | All: one key for the recipe name, the old ones refused with the new name. Arch, DS, Dev: `info.ui_label`. User: "one key", spelling follows its variant. Dev finds a hazard: `info` takes any key, so the refusal must be written (`recipe_check.py:315` has code only for `info.display_name`). | Author: stops typing a name nothing shows. The form and the new-recipe factory change. | None for the refusal. The key spelling touches M271 (open) and the sentence of D-0405 (it says `info.label`). |
| 2 | What `info.label` is (recipe table, section 5; options A to D) | The format says "short name" (`spec:367`); HOME uses it as the banner; real values are up to 40 characters, longer than tab names. | Arch, DS, Dev: split it. `info.ui_label` short and required; `info.ui_title` longer and optional (the banner). This is the recipe table's option C. User: one key for the name; "the title a second key or the same". | HOME banner = `ui_title`, else `ui_label`. Dev: the 16 shipped recipes need their long text moved to `ui_title`. | Option B of the recipe table changes format sentences (`spec:105, 179, 192, 367`); the split keeps D-0405's meaning. |
| 3 | The short name has four keys: `ui_label`, `label`, `name`, `display_name` | `ui_label` for group and plot; `label` for info, table, join, column, session, registries; `name` for the Gallery index and the app features id; `display_name` for app features; `deployment_name`. | All four: `ui_label` for every short name (variant P). Dev: registries may keep `label` by a stated exception. Arch: the Gallery index `name` becomes `ui_label`, and the `name` fallback at `home_theater.py:115` is deleted. | One key per kind. About 12 reader files, the registries, the session file, the index. | M271 (the three `label` places, open; your words lean to `ui_label`); D-0253 extended, not reversed. |
| 4 | `ui_title` in a recipe against `ui_title` in app features | Recipe: a string, read only by the report. App features: an object `{text, subtitle, visible}` read by HOME's banner. No shipped app features file sets it. The validator has no key list. | Arch, DS, Dev: same meaning in both (the longer title), same shape (a string). Arch: `visible` moves to the flags. Dev: one precedence line in the spec: app features or deployment title, else `info.ui_title`, else `info.ui_label`. User: remove or rename the app features key. | HOME banner always names something clear. Validator, `home_theater.py:1139-1157`, template, docs change. | None. |
| 5 | A group's `ui_title` read by nothing | The format says report and headings use it (`spec:485`); no reader (READ by the scout and checked again by Arch). | All: give it a reader (a group heading in the report), or remove it from the format. DS advises the reader. Dev: "never leave a documented key unread". | Author: either sees the title in the report, or the key is refused. | None. |
| 6 | `description` used as a tab text | `home_theater.py:105`. The format says this fallback "goes" (`spec:490`). | All: remove it. Tab = `ui_label`, else the id. | One line and a test. A sentence as a tab name stops looking like a bug. | None (the format already says it goes). |
| 7 | Gallery heading against the example's name; and where the Gallery description lives (recipe table, Q8 option c) | Name = the plot's `ui_label` (D-0387). The `##` heading of `example_meta.md` is guidance text; not read as a name, not compared. | Arch: concordant, not equal (D-0397); an advice if the name is over 30. DS: the one-sentence description in the plot's `description` (travels with the recipe; the heading page does not travel when a recipe is copied to HOME). Dev: one source, open. User: at the choice the list needs the name and one sentence. | The 34 examples and the check change only if the description moves. | D-0397 puts the description in the heading; moving it to the recipe reconsiders where, not that it is longer than the name. |
| 8 | The other keys of `info` (`subtitle`, `description`, `contact`, `submission_date`) and what `info` is for in a Gallery recipe | `submission_date` is written by the Gallery generator and read by nothing. | Recipe table Q8 (a to d) lists the options. No viewpoint chose between them. DS: add the deployment and app features set to the export record (it also gives `deployment_name` its first reader). | See the recipe table. | Option c reconsiders D-0397. |
| 9 | "Blueprint Architect" against "Wrangle Studio" | The nav shows the first; the internal value is the second, in six places. | Arch: one table of user spaces; the internal value is the id and never shown; the screen word is your choice. DS: internal value `blueprint`, screen "Blueprint Architect". Dev: the visible word "Blueprint", internal value `BLUEPRINT`; the class and file `wrangle_studio.py` keep their names. User: "Blueprint" everywhere. | One place, one word. Code, YAML and tests change (DS counts 2 handlers, the app README, 2 config files, 5 tests). DS: not stored in a session or the export (grep, RUN). | None; the glossary page `Terminology.qmd:33` changes. |
| 10 | dataset / table / schema / collection / join | Five words (FACTS section 5). | Section 5 below. | Screen and documentation words. | None. |
| 11 | plot / figure / graph / chart | "figure" in the export and report; "graph" in the lineage; "chart" proposed for the new filter. | Section 5. DS differs (figure). | Words. | D-0398 ("Chart type"). |
| 12 | step / action / node | "node" in the audit list; "transformation node" in the help. | Section 5. Dev differs (the picker says "step type"). | Words. | None. |
| 13 | Six "Apply" buttons (section 1, row 3) | Six effects under one word. | Arch: one verb "Apply" for putting a change in; "Send to Audit" stays; each rename needs a check because the effects differ. User: the button carries its object ("Apply filter", "Apply audit step"). DS and Dev: not addressed. | User sees what each button does. | None. |
| 14 | Registries (action, plot component, panel) keep a `label` key written by maintainers | Panel: registry `label` read by nothing; the titles are typed in the renderer. Actions and components: `label` is the picker text. About 900 lines in `viz_factory` hold the word (Dev counts the word, not its role). | Arch, DS: `ui_label` everywhere, one store for panels, a test that every accordion title equals it. Dev: open: keep `label` in registries by a stated exception, or rename. | If kept, the spec says so and a second key name stays by decision. If renamed, up to 877 hits to review (Arch, transformer and viz_factory). | None. |
| 15 | Field `label` and `description` | Checker refuses `description`, the card shows it. | Arch, DS, Dev: accept `description` on a field (a column definition is the most useful text a data reader has: DS). | The checker and the card agree. | D-0360 refines (DS). |
| 16 | A column's display name hides which column was used (D-0360 alias) | The ledger lines D-0360 and the open item of 2026-11-20 contradict each other (section 11). HOME shows raw column names today (`home_theater.py:1692-1701`). | Arch: the resolver returns the pair (label, slug); every screen that shows a display name can show the slug. DS: show the display name and the slug on hover; never in a data file or an audit step; two columns with one display name = error. User: "Display name: <x> (column: <real name>)". | Science rule; see section 7. | D-0360 (status conflict). |
| 17 | Join `labels` against the field's `ui_label` | Two places for one column's display name; the join one has no reader found. | Arch: one place, not both (the field's `ui_label`, or `labels` for columns that exist only after a join). DS: join `ui_labels`, and decide whether the plot-level `labels` stays. | Spec and checker. | ADR-100 point 5 (DEC23, per Arch). D-0253 for the plot-level `labels` (DS). |
| 18 | `deployment_name` | Written; read only by a method no caller uses. | Arch: `ui_label` of the deployment, shown; or deleted; never kept unread. DS: `ui_label`. Dev: `ui_label`. User: shown nowhere today, and the template tells a deployer it is "shown in app footer". | Bootloader, connector method, template. | None. |
| 19 | Mistyped key in app features or deployment (section 1, row 8) | Accepted silently. | Arch, Dev: the same key-list check for both file kinds as the recipe has. | A typo is refused with a plain line. | ADR-100 point 2 extended (Arch). |
| 20 | Duplicate names by trailing space or case (row 9) | Exact comparison. | DS: unique after trim and case-fold; error for the tabs of one recipe and for the Gallery; advice elsewhere. | Two names that look the same are refused. | None. |
| 21 | Blank `ui_title` (row 10); invented title-cased id (row 7) | Empty heading; "P One". | DS, Dev: the one fallback, id exactly as written; a blank is an error. | No empty heading, no invented name. | None. |
| 22 | "Info" panel twice on one screen; "Alerts" or "Notification Log"; "Deployment" or "Deployment Info" | Several titles for one panel (FACTS 2.2). | User: "Recipe info" and "Deployment". Alerts: DS, Dev say "Alerts"; Arch and User leave it to you ("Alerts" sounds like a problem: User). | Words. | None. |

---

## 5. One word per thing on screen and in the documentation

"A second word stays" means: where an outside tool owns the word.

| Thing | The word proposed | The words it replaces (where found) | Where a second word must stay | Who proposes; who differs |
|---|---|---|---|---|
| The YAML file | data analysis recipe (short: recipe) | pipeline as a name for the recipe; manifest (retired, `audit_old_words.py:34`) | "pipeline" only for the automated deployment mode (Arch, `pipeline-static.yaml:3`), the folder name (Dev), or outside the app (User) | all agree |
| The BLUEPRINT user space | Arch: your choice; DS: Blueprint Architect; Dev, User: Blueprint | Wrangle Studio, Flight Deck, Recipe Editor, Surgeon (FACTS 2.8) | the class and file `wrangle_studio.py` (Dev); BLUEPRINT in `CLAUDE.md` for the internal id | differ on the word (open) |
| The Test Lab user space | Test Lab | Dev Studio, Test Lab Tools, LAB (D-0396, not on screen) | TEST_LAB as the internal id | User, DS |
| The Gallery user space | Gallery; its panels "Examples" and "Filters" | Inspiration, Explorer, "Taxonomy", "template" (FACTS 2.8) | none | User only |
| The notes panel | Alerts (DS, Dev); Arch and User: you pick | Notification Log | the id `notification_log` | differ |
| The picture | plot (Arch, Dev, User); figure (DS) | figure, graph, chart (FACTS section 5) | "figure" in plotnine's documentation and in "figure text"; "chart" only in the filter "Chart type" (D-0398; User: it would read "Plot type") | DS differs |
| A group | group, shown as a tab | analysis group on screen | the key `analysis_groups` | DS, User |
| A table the user sees | table | dataset, data preview table, collection (all four); Dev also "source table" | `target_dataset` (format key) and `collection_id` (code), until renamed; the Polars words in code | Dev replaces "source table"; DS keeps "source table" for a table as read from the file |
| The definition of a table | schema; "table definition" in help (Arch, Dev, User once) | data schema | the keys `data_schemas`, `input_fields` | agree |
| The joined table | joined table (Arch); join for the operation, joined table for the result (DS); join (Dev, User) | collection | `collection_id` in code | small |
| A line of a step list | step | wrangling step, transformation node, node | "node" only for a point of the lineage graph | agree |
| The kind of operation chosen | action | none (Arch, DS, User) | `polars_*` names are Polars' | Dev: the picker may say "step type" |
| What the user sends to audit | audit step; Audit mode (DS) | audit node, "filter and drop" | the key `t3_audit_steps_by_plot` | DS |
| The zip for others | export bundle; import bundle | results bundle, reproducibility bundle, reimport bundle, "Export Bundle" | the file name `..._results.zip` | Arch, DS, Dev, User agree on one name |
| The session zip | session file (User) | "Export Active Session" | none | User only |
| The info panels | Info (Arch); "Recipe info" and "Deployment" (User) | "Data analysis recipe Info" (Arch); "Info" twice (User) | none | differ |
| Primary key | entity key with a hover (User) | PK, slug, primary key | the key `is_entity_key` | User |
| A column's identity | column name (slug) (DS) | field name | "field" = the entry in `input_fields`, never the column's name | DS |
| A display name | display name (`ui_label`) (DS, User) | alias, label | none | DS, User |
| Apply | Arch: Apply; User: "Apply filter", "Apply audit step" | Validate & Apply, Apply Style, Apply to session (each to be checked) | "Send to Audit" stays | differ |
| "name" against "label" as the word shown to a user | User: "name" on screen ("label" makes the user think of an axis label or a tag); a message quotes both: "give each example its own short name (ui_label)". DS and Dev: "short name", "title", "description" in all documents, keys in code font | "label" in prose for the short name; "title" for `info` (`Terminology.qmd:8`) | `labs` parameters (`title`, `x`, `fill`) are plotnine's | Arch does not address the screen word |

The Violet Law (`ComponentName (file_name.py)`) is about naming code in documents. Arch: it is unrelated and not extended. Compliance of each document was not checked.

---

## 6. The variants for the key names

Same three variants, different letters in the reports. In this file:
- **P**: the prefix `ui_` for every display key in every file kind (`ui_label`, `ui_title`, and where a banner exists a subtitle). Arch A, DS V1, Dev B, User A.
- **Q**: plain `label`, `title`, `description` everywhere. Arch B, DS V2, Dev C, User B.
- **R**: keep today's keys, fix only the collisions. Arch C, DS V3, Dev A, User C.

`description` stays plain in all three, except in User's reading of P (`ui_description`).

| | P: prefix `ui_` | Q: plain words | R: collisions only |
|---|---|---|---|
| What it gives | One key per kind, in every file kind. Closes the M271 question (`label` becomes `ui_label`). | One key per kind, the usual words. | The smallest change. Settles `info.name`, the app features title, the unread keys. |
| What it leaves | Nothing of the "one key per kind" rule. | `label` and `title` next to plotnine's `labs` content in a plot entry (Arch, DS, Dev: confusion risk; DS says plotnine also uses the plain words). | The same kind has several keys: `label` in at least eight jobs, `display_name`, `deployment_name`, `name`. M271 stays open (Arch, DS). Dev: five short-name keys remain. |
| Recipe format and version | Flip the four lines of `label_keys` (`recipe_spec.yaml:12-17`) to `ui_label`; `info.ui_title` added; `description` on a field. Version: see below. | The same structure, and group and plot `ui_label` and `ui_title` go back to `label` and `title`. | None in the keys. `format_version` stays 1. |
| Checker | New `renamed:` entries for `info.label`, `schema.label`, `join.label`, `field.label`, `info.name`; an explicit refusal in `info` (Dev); length and blank rules from the spec. | The same, plus the current refusal text for plot `label` must change (it says "renamed `ui_label`"). | Two codes (`info.name`; the group `ui_title`). |
| Code | One function replaces the seven readers. 12 Python files read `"label"` by hand (Dev). Registries: 16 library files hold registrations (Arch); `"label"` appears 877 times in `transformer` and `viz_factory` (Arch, a raw count, parameter labels included). | Every reader of `ui_label` and `ui_title` goes back: `ui_label` is in 213 files / 580 lines and `ui_title` in 67 files / 137 lines (Dev, RUN; 115 of the files are tests). | A few lines in `blueprint_handlers.py`, `home_theater.py`. |
| Recipe files | 109 YAML under `config/data_analysis_recipes` and 34 Gallery recipes, by the existing migration tool `assets/scripts/migrate_recipe_engine_keys.py --apply` (script-driven, a second run changes nothing: Arch, READ its docstring). Also the generators `example_recipe.py:122-140`, `new_recipe.py`, `recipe_factory.py`. Info keys in use: `info.label` 24 files / 34 lines; `info.name` 13 files / 23 lines (Dev, RUN; mostly tests, see section 1 row 1). | The same files, undone for group and plot. Arch: more files than P; the reverse of `label` to `ui_label` needs a new migration rule. | Only files that hold `info.name`. Dev says 0 Gallery; DS says 34; RUN by the writer: 0 Gallery. |
| App features and deployment | `display_name` to `ui_label`; `ui_title` to a string; `deployment_name`, `branding.banner.title` and `subtitle` renamed; entries in `renamed_keys.py`; a key list added to both validators. 8 app features files (RUN, Arch; writer confirmed); deployment: 7 YAML (RUN by the writer, includes the template and 2 demo files; Dev writes "8+3 files", not explained). | The same, with `title` and `label`. | One key renamed. |
| Sessions | `label` to `ui_label` in `assembly.json`; Arch: add to `RENAMED_SESSION_KEYS` (`renamed_keys.py:63-69`). Dev: refuse old sessions or migrate them. DS: recipes in old bundles are refused on re-import until migrated. | The same. | None. |
| Documentation | `Terminology.qmd`, `Standards_yaml.qmd:47` (the false "default axis title"), `data_contracts_adr.qmd`, the authoring guide, the UML note `docs/UML/app.mdj:34603`; 61 `.qmd` in the book (Arch). Generated from the spec where possible. | The same, plus the plotnine confusion in each. | 4 passages (Dev). |
| Tests | Spec and migration tests extended; one test per kind; 115 files hold the names, most are fixture edits a script does (Dev). | Larger. | Few. |
| How it is done in one pass with the old key refused | A `renamed` table, a migration script, an audit rule; one merge in which no state has both keys. Dev: the pass over recipes, Gallery, fixtures, readers and checker must be one piece; each step before and after leaves a working app. | The same. | Not needed. |
| Recommended by | Arch, DS, Dev, User, each on merit. | none | none (Arch: take it only as a first step; its collision fixes are all inside P) |

**Facts to know about P and Q:**
- Arch found: the `ui_` prefix does not mean "shown on screen" today. `ui_title` is read only by the report (`export_handlers.py:373`). In a plot entry the prefix does one mechanical job (it separates the app's keys from plotnine's content); the entry's other app keys (`description`, `comment`, `taxonomy`, `plot_engine`, `tier3`) have no prefix (`recipe_spec.yaml:70-76`). Neither prefix nor plain key answers your question "has `ui_label` to be shown in the UI?"; the spec table does. User's condition for P: no `ui_` key unless a screen really shows it.
- Dev found: `info` is free-form (`recipe_spec.yaml:28`). An old `info.label` or `info.name` is not refused by the generic key check. The refusal must be written, or "old key refused" does not hold for the recipe's own name.
- Format version, all four: stay in format 1 or make format 2. The spec header (`recipe_spec.yaml:3-8`, READ by the writer) says format 1 "was amended before its first release" (D-0236) and "No format 2". Whether a release has happened is a fact only you have (section 9).

---

## 7. The rules that protect the science (data scientist)

1. A text written for display never changes a row of any table. Only identities and column names can change a result. Test that can fail (DS): change every `ui_*` and `description` in a recipe, run it, compare the T3 tables and the plot data: identical.
2. Where a display name is shown, the real column name is reachable (a hover, or a second line). A display name can hide which column was used.
3. A display name never goes into a data file or an audit step. An audit step that filters a column names the real column. Two columns with one display name in one table is an error (DS). Arch: a label is never the only name in a table the user acts on, in a filter, or in the export (the resolver returns both).
4. A reader of a methods section can cite recipe `id`, `info.version` and plot `id` (the plot file name in the export). The title and the short name are not stable citations; the README should say so (DS). The report shows the plot name while the picture's file is named by the id; DS asks to print the id beside the heading.
5. A name change alters the recipe hash and the session key, not the result (Arch, READ `session_manager.py:10, 281-308`, not run). The key is the first 12 characters of the recipe hash and of the data hash. What happens to a saved session of a migrated recipe was not read in the restore code. The rules text (`ui_implementation_contract.md` section 12d) says: same recipe id with a different hash gives a warning, not a block; a session of another recipe is refused; a session file saved by an older format is refused and not converted (D-0312). Whether a folder named by the old key is still found after a rename was not verified. In plain words: sessions saved before the rename may not match the migrated recipe; I could not check how the app reacts.

---

## 8. How the scheme is kept true later

| What | Proposal | Who |
|---|---|---|
| One place for the kinds, keys, numbers and fallback | `names_spec.yaml` (Arch); a `name_kinds` block in `recipe_spec.yaml` (DS, Dev) plus a second spec for app features and deployment (Dev). The documentation table is generated from it. | all |
| One function for the fallback | A pure function in `libs/utils` that every screen, the report and the Gallery call. Dev: `display_name(kind, entry, id)` and `check_names`. A test fails if `.get("ui_label")` or `["ui_title"]` appears outside it and the checker (this would have caught the five fallbacks). | Arch, Dev |
| Allowed keys for app features and deployment | The same strict key list the recipe has; unknown or old keys refused with the new name. | Arch, Dev |
| Audit of retired words | `assets/scripts/audit_old_words.py` (list today: persona, manifest, recipe bare, profile, project, app features template, connector; `label`, `title`, `name` are not on it, READ `:32-40`) gets the retired keys (`display_name`, `deployment_name`, `info.name`, `ui_banner`) and the retired screen words of section 5. | all |
| Tests | Old key refused with the new name; blank or newline `ui_label` is an error; 33 and 81 characters give an advice (Dev); every accordion title equals its registry name; every registered action and component has a name and a description; one parametrised test that HOME, BLUEPRINT, the Gallery and the report give the same fallback. | Arch, Dev |
| A rule file | One short section in `rules_data_analysis_recipe_structure.md` pointing to the spec (Arch); or `.claude/rules/rules_names.md` plus a line in `CLAUDE.md` section 1 (Dev). A line in `rules_app_features_flags.md` for the app features and deployment keys (Arch). The table is not copied into the rules (two stores). | Arch, Dev |
| Where advices are shown | Today most advices have no screen (recipe table section 4; HOME shows five kinds only). User: one list in BLUEPRINT's "Validate". Your D-0403 asks to see the Gallery advices; not built. | User; open |
| What none of this catches | Whether a name is a good name (D-0405: the author's control); a screen word typed in a handler as plain text (the audit sees a retired word, not a bad new one); what "short" means; text in a figure (checked elsewhere by `plot_text_check.py`). | Arch |

---

## 9. To decide, ranked (larger first)

For each: "reconsiders?" is information only.

1. **Does every kind have one key in every file kind?** Options: P (prefix), Q (plain), R (collisions only). All four viewpoints recommend P on merit. P gains one rule everywhere; costs the largest change (section 6). Q gains the usual words and costs a reversal in about 213 files. R is the smallest and leaves the rule untrue. Reconsiders: P extends D-0253; Q reverses its key names but keeps `labs`; R keeps D-0253; all touch M271.
2. **What does a recipe get in `info`: one name or a short name and a title?** Options: A keep `info.label` short (recipe table); B `info.label` is the title; C `info.ui_label` plus `info.ui_title` (Arch, DS, Dev). Everything else follows. Reconsiders: B changes format sentences; C keeps D-0405's meaning.
3. **Is a group's `ui_title` read by the report or removed?** DS advises a reader. Gain: a documented key does something. Cost: export code, or a format change. Reconsiders: none.
4. **Where does the Gallery description live?** The plot's `description` in the recipe (DS, Dev, User) or the heading of `example_meta.md` (D-0397, Arch open). One source or the defect stays. Reconsiders: D-0397.
5. **Column display names: shown alone or with the real name?** DS and Arch rule: the real name always reachable, never in a file or audit step. A FACT is needed from you here: D-0360 and your later words disagree (section 11). Reconsiders: D-0360.
6. **Where does a column's display name live: the field's `ui_label` or a join's `labels`?** One, not both (Arch). Reconsiders: ADR-100 point 5.
7. **The words on screen.** The BLUEPRINT word; the notes panel word; "plot" or "figure"; the single verb "Apply" or the verb with its object; "Wrangle Studio" out of every text a user reads. User ranks the BLUEPRINT word first. Reconsiders: none; D-0398's "Chart type" if the word is "plot".
8. **The numbers for "short", "long", "one sentence", and error or advice.** Proposals in section 2, from measured lengths (Gallery 9 to 28; recipes: median 19, p90 27, one value of 109 characters, RUN by Arch). Reconsiders: none (D-0405 says advice for names).
9. **Registries: rename `label` to `ui_label`, or keep it by a stated exception?** Dev asks; Arch and DS rename. Cost: up to 877 hits to review.
10. **Does a column (field) accept a `description`?** The checker refuses it, the BLUEPRINT card shows it. Arch, DS, Dev accept it. Reconsiders: D-0360 refines (DS).
11. **Facts that only you have:** (a) Was recipe format 1 ever released? The spec says no ("before its first release", "No format 2"). It decides "stay in 1 or make 2". (b) Old session files: refuse or convert? The rules text says refuse and convert nothing (D-0312, a session-format rule). Does that apply to a `label` rename in the session file? Dev asks; Arch says add to the renamed-keys list.
12. **Other:** the `target_dataset` key to `target_table` (DS asks; Arch calls it a format change); app features id `name` to `id` (Arch only); one id style (snake_case for recipes, hyphens for app features: keep or unify, DS); the deployment and app features set written into the export record (DS); whether the Gallery list shows one sentence beside the name (User; D-0397 says one line).

---

## 10. If you agree: the order of work (Dev's proposal; Arch gives a similar seven-step order)

Not started; waits for your word. Each step leaves a working app.

| Step | What | Model and effort (Dev, CLAUDE.md tags) |
|---|---|---|
| 1 | Your answers to section 9. A decision; nothing built. | opus/high |
| 2 | Tests rewritten to the decided design; the spec block and one fallback function in `libs/utils`; the screens switched to it with no change in keys. No recipe and no screen touched; low risk. Arch: the same step first; worth doing in any variant. | sonnet/high |
| 3 | Migration script; dry run on a copy; a reviewer reads the list. | sonnet/medium |
| 4 | One merge: script applied to recipes, Gallery, fixtures; readers in about 12 files; checker refusal including `info`; `label_keys` flipped. The risky step; one piece because the old key is refused. Reviewer opus/high. | sonnet/high |
| 5 | App features and deployment keys; key lists added to both validators. Own worktree; touches `home_theater.py`, so merge after step 4. | sonnet/medium |
| 6 | Screen words and help files. Parallel with 5 except in `home_theater.py` and `blueprint_handlers.py`. | haiku/low for the list, sonnet/medium for code |
| 7 | Documentation, UML note, Terminology, spec sentences, rule file, audit script entries. Can start at step 3. | sonnet/low |
| 8 | Sessions: refuse or migrate old `label`. Last, because it touches user files. | sonnet/high |

Regression risks (Dev, reasoned): a reader missed by search; the Gallery duplicate refusal message; old sessions; the HOME banner order changing silently (a test fixes it).

---

## 11. Not verified, and records that contradict each other

**Not verified** (merged, with who says so):
- Nothing was run by the four viewpoints. The recipe selector text; the Info panel rows; whether tabs cut long names; the content of "Alerts"; the recipe `id` on a screen; the audit dialog's reader of join `labels`; the figure caption source in the report; the severity of FD01; column names in the Gallery data sample and the export data files; the Gallery filter hover (not built). (FACTS, DS, User)
- The session restore code and the effect of a changed recipe hash (Arch, DS). Whether the nav value "Wrangle Studio" is stored in an older session (DS, Dev).
- Whether `load_data_analysis_recipe` hashes file bytes or parsed content (Arch). Whether the Gallery check notices a stale index name after an edit (Arch).
- Whether format 1 was released (Dev). Whether the 900 `label` lines in `viz_factory` are registry keys or plotnine arguments (Dev counted the word). The count of 12 reader files and of 115 test files (Dev, word counts; tests not opened).
- Lengths in the 16 shipped recipes and 34 Gallery examples: partly measured (Arch RUN: Gallery 34 values, 9 to 28, median 17; recipes `ui_label` 62 values, median 19, p90 27, max 109; `ui_title` 25 values, 24 to 59, median 32; rough regex including fragments). The recipe table counts by hand. The numbers 30, 32, 80, 160, 200, 300 are proposals, not measures of a survey.
- Compliance of the documentation with the Violet form; the README and lib READMEs were not read for names.
- The ledger line D-0034, cited inside D-0360, was not read by the scout.

**Records that contradict each other** (reported, not resolved; rule H):
1. D-0387 says the code reads `info.label` for the Gallery name at `gallery_manager.py:107`. The code reads the plot's `ui_label` (`taxonomy.py:55-66`; `gallery_manager.py:142`). The ledger line is stale (FACTS C4; recipe table section 3).
2. `spec:484` says `ui_label` was renamed on 2026-11-17 (DEC52); D-0253 is dated 2026-11-18 (FACTS C9).
3. D-0360 is DECIDED, but its text calls the alias "a proposal, not a rule". Your later words of 2026-11-20 ("it is still my question - what is the label used for ...") say the question is open. The ledger itself records this as a contradiction, "stays open until she answers" (`decision_ledger.md:526`; READ by the writer). FACTS C10.
4. D-0253 and `Standards_yaml.qmd:47` (a field `label` as "also the default axis title of a plot"). The documentation is out of date.
5. `app/src/ui.py:343` says the banner comes from the `ui_banner` key in an app features file; `renamed_keys.py:37` says it was renamed `branding.banner` in the deployment file. The comment is wrong (FACTS 2.1).
6. The deployment template (line 22) says `deployment_name` is "shown in app footer"; no footer code was found.
7. `rules_app_features_flags.md` does not mention the app features `ui_title` that `home_theater.py:1139` reads; no shipped app features file sets it (FACTS C3).
8. Counts that differ:
   - Panel titles that differ from the registry: Arch "7 of 20"; the FACTS table has 6 marked "no", 3 "not found", 1 not used.
   - Gallery recipes touched by variant R: Dev 0, DS 34; RUN by the writer: 0 (no Gallery recipe has `info.name`).
   - Deployment files: RUN by the writer 7 YAML (including the template and 2 demo files); Dev writes "8+3 files" without saying what the 3 are.
   - Shipped recipes: the recipe table says 16; the writer's scan found 8 files with a top-level `info` in `config/data_analysis_recipes` (fragments and included files have none). The gap was not explained; I did not look for the other 8.
   - `"label"` hits in registries: Arch 877 (`transformer` and `viz_factory`); Dev "about 900" (`viz_factory` only). Different scopes.
   - Format: the spec header says "No format 2" and "amended before its first release"; the architect and the developer say "stay in 1 or make 2: open".
