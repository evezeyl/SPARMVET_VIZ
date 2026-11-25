# Architect viewpoint: one scheme for names across the whole app (2026-11-21)

Labels: RUN = I ran it; READ = I read it at file:line; REASONED = inferred. Tags: DECIDED / CONFIRM / OPEN / MINE. "Reconsiders" is information only.
First step done: FACTS.md did not exist; I copied the scout report to `tmpAI/panel/names_whole_app/FACTS.md` with `cp`. The copy succeeded (62046 bytes).
Scratch: `tmpAI/panel/names_whole_app/architect_scratch/` (a length count). No repository file was edited. `tmp.md` was not read.

## Summary (6 lines)
1. The real defect is not the spelling of a key. It is that the kinds are defined nowhere: today 7 readers resolve a name with 5 different fallbacks, and two separate mechanisms refuse old keys (RUN grep, READ below).
2. Fix first, in any variant: one table of kinds in one spec file; one pure resolver in `libs/utils` that every screen, the export and the Gallery call; the same strict key list for app features and deployment files that the recipe already has.
3. Kinds: `id`, short name `ui_label`, longer title `ui_title` (+ optional `ui_subtitle` for a banner), `description`, help text (a separate file or registry field, never a name key), the column display name (the field's own `ui_label`), the figure text (stays in `labs`, plotnine's words).
4. The `ui_` prefix means "the app's own text, not the engine's". That reason is mechanical only in a plot entry, which mixes app keys and plotnine content. READ `recipe_spec.yaml:70-76`: the entry's other app keys (`description`, `comment`, `taxonomy`, `plot_engine`, `tier3`) have no prefix, so the prefix is not a mechanical namespace today.
5. Recommended: variant A, extend D-0253 to every user-facing name (recipe, app features, deployment, registries), refuse old keys with the new name, one pass per file kind.
6. Two facts the user must be told: a name edit changes the recipe hash and so the session key (READ `session_manager.py:281-308`), and whether this stays "format 1" or becomes a new format is OPEN.

## 1. Evidence I checked (not redone from FACTS)
- RUN `grep ui_label` outside tests: seven readers, each with its own fallback.
  - HOME group tab: `ui_label`, else `description` (a sentence as a tab), else the id (`home_theater.py:104-105`).
  - HOME plot tab: `ui_label`, else the id in title case (`:109-110`).
  - HOME audit list: `ui_label`, else `name` (a key that is not in the format), else the id as written (`:114-115`).
  - Export report: `ui_title`, else `ui_label`, else id in title case (`export_handlers.py:368-373`).
  - BLUEPRINT list: `plot_ui_label`, the id when unreadable (`group_plot_manager.py:95-104`); group list `ui_label` else the id (`blueprint_handlers.py:2307`, `:2404`).
  - Gallery: `ui_label` only, no fallback, raises (`taxonomy.py:55-66`).
  - Navigator and agent context: the id (`data_analysis_recipe_navigator.py:765`, `agent_context.py:156`).
  A third consequence: a plot with no `ui_label` is called three different things in three places. (READ; the checker refuses it first in HOME, so it shows only in BLUEPRINT while building.)
- READ: two "old key refused" mechanisms. Recipe: `recipe_spec.yaml` `renamed:` table read by the checker and the migration tool (`recipe_check.py:182-191`). App features and deployment: Python dicts in `app/modules/renamed_keys.py:15-70`, with functions at `:96-150` that test only the old names.
- READ: app features and deployment files have NO list of allowed keys. `app_features_validator.py` has none (search "unknown|allowed": nothing); `renamed_keys.py:96-150` refuses only known old names. So a mistyped `diplay_name` is accepted silently there, while ADR-100 point 2 ("unknown keys fail") holds for recipes. A scheme "one rule wherever written" is not true for these two file kinds today. (This is the architecture gap behind FACTS 2.1 and 2.2: `ui_title` in app features is read at `home_theater.py:1139` and is in no list.)
- READ: the panel registry `label` (`sidebar_registry.py`) is read by nothing; the accordion titles are typed in the renderers; 7 of 20 differ (FACTS 2.2 table). Two stores of one name that can disagree, one of them dead.
- READ `recipe_spec.yaml:9-17`: `label_keys` is built so that Eve's answer on M271 is "a one-line change per place", and `engine_keys_migration.py:693-709` renames the pending places when the table says `ui_label`. So the recipe half of variant A is already machinery, not new work. Her words in the ledger (`ledger:518`/FACTS 2.10): "the labels are ui_label because its what is shown in the ui".
- READ `session_manager.py:10, 281-287, 306-308`: the session key is `data_analysis_recipe_sha256[:12]:data_batch_hash[:12]`, and the hash is over the recipe files (docstring: "sorted relative_path:sha256 lines"). So any rename or edit of a name changes the recipe hash and the session key, although no result changes. I did not run it. (REASONED: today any edit of a `ui_label` in BLUEPRINT does the same.)
- RUN lengths (a rough count; regex on tracked YAML, includes fragments): Gallery `info.label` 34 values, min 9, median 17, max 28 (matches the owner's table); recipes under `config/data_analysis_recipes` `ui_label` 62 values, median 19, p90 27, max 109 (one value of 109 characters is worth a look); `ui_title` 25 values, 24 to 59, median 32. The `label:` count for `config/.../info.label` (140) also catches schema labels, so do not use it.
- RUN counts: 109 tracked YAML under `config/data_analysis_recipes`, 34 Gallery recipes, 8 app features files, 7 deployment YAML, 61 `.qmd`, 478 test files. Registries: 16 library files hold `register_action` or `register_plot_component`; `"label"` appears 877 times in `transformer` and `viz_factory` sources (an upper bound: parameter labels included).

## 2. The kinds (answer 1)

One file defines them. MINE: a data file `libs/utils/src/utils/names_spec.yaml`, next to `recipe_spec.yaml`, read by the recipe checker, the app features and deployment validators, the registry check, the docs generator and the audit script. It replaces the `label_keys` table (which dissolves when every place is `ui_label`). DECIDED precedent for "terms and meanings in the spec, documentation generated": D-0399 (not built).

| Kind | Purpose (one sentence) | Key, everywhere | Writes it | Required? | Rule (proposed; Eve sets the numbers) | Missing |
|---|---|---|---|---|---|---|
| Identity | Names the thing for the program and for files; never shown. | the mapping key, or `id` where a file states its own (recipe `id`; app features `name` becomes `id`) | author / developer | yes | recipe ids: lowercase snake_case; app features ids: hyphens (today's rule, `app_features_validator.py:79-92`); one pattern per file kind in the spec; a breach is an ERROR | not possible |
| Short name | What the thing is called in a tab, a list, a dropdown, a button. | `ui_label` | author / deployer / developer | yes, for every thing a user can choose or see in a list | at most 30 characters (covers Gallery max 28, recipes p90 27); no line break; a breach is an ADVICE (D-0403 and D-0405 set advice, not error, for names) | the id as written; one resolver for the whole app; never `description`, never title case |
| Longer title | A heading, a banner or a report heading. | `ui_title` (+ optional `ui_subtitle` where a banner exists) | same | no | at most 80 characters (RUN: 59 max today); advice | the short name |
| Description | One sentence that says what the thing is for, and for the recipe's science what it answers. | `description` | same | no (advice when missing, as today for schemas and joins) | one sentence; advice when over 200 characters | nothing is shown; no substitute |
| Help text | The meaning, shown on demand (hover, click, panel). | not a recipe key: help files, the registry `description`, and for Gallery terms the spec (D-0399, D-0404) | developer / owner | no | none | the control has no help mark |
| Column display name | What a column is called in a table header or a list. | the field's own `ui_label` (beside `original_name` and the slug) | author | no | at most 30 characters; advice | the slug, shown as written |
| Text in a figure | Title, axis and legend names. | `labs` layer params (plotnine words), never a name key (D-0253) | author | no | plotnine's | no title in the picture |

Fallback rule, one for the app (MINE, CONFIRM): title, else short name, else id as written. A list never falls back to `description`. The checker refuses a missing `ui_label` in HOME (P01, `recipe_check.py`), so the fallback is only seen while building in BLUEPRINT (which reports and never blocks, ADR-099 point 16/ADR-100 point 3); it should be visible there as the id, not hidden by title case.

Why a banner "title block" is split from a flag: `ui_title: {text, subtitle, visible}` in app features (`home_theater.py:1139-1144`) puts a name and a switch in one object. In the scheme `visible` becomes a flag in `flags:` (rule file `rules_app_features_flags.md`, ADR-091) and the title is a string, like the recipe's.

## 3. The matrix (thing against kind; key of the scheme, blank = not needed)

| Thing | Identity | Short name | Longer title | Description | Help | Column display |
|---|---|---|---|---|---|---|
| Recipe | `id` (= file name) | `info.ui_label` | `info.ui_title` (+ `ui_subtitle`) | `info.description` | help file | |
| Group | key | `ui_label` | `ui_title` | `description` | | |
| Plot | key | `ui_label` | `ui_title` | `description` | | |
| Table (schema) | key | `ui_label` | | `description` | | |
| Join | key | `ui_label` | | `description` | | `labels` (column to display text; see section 4) |
| Column (field) | slug | | | `description` (accepted by the checker, see section 4) | | `ui_label` |
| Action | registration name | `ui_label` | | `description` | `description` in help panel | |
| Plot component | registration name | `ui_label` | | `description` | help registry | |
| Panel | `type` | `ui_label` (one store: the registry, read by the renderer) | | | | |
| User space | nav value (internal) | `ui_label` in one table of user spaces | | | help file | |
| App features set | `id` | `ui_label` (today `display_name`) | `ui_title` (+ `ui_subtitle`) | | | |
| Deployment | file path | `ui_label` (today `deployment_name`) | `ui_title` (+ `ui_subtitle`, today `branding.banner`) | | | |
| Gallery example | folder = recipe `id` | the plot's `ui_label` (DECIDED D-0387) | `info.ui_title` | `info.description` (open: D-0397 puts it in the heading of `example_meta.md`) | the heading page | |
| Session | session key | `label` becomes `ui_label` | | | | |
| Export bundle | file name from the user's text (`export:2253-2260`) | `ui_label` (the user's text, today `export_user_name`) | the report title | | | |

## 4. The cases (answer 3)

| Case | Today | In the scheme | What it changes | Reconsiders |
|---|---|---|---|---|
| `info.label` against `info.name` (BLUEPRINT) | two keys; the form writes `info.name` (`bp:2542, 2609`), "new recipe" writes `info.label` (`new_recipe.py:27`); `info` is free form, so nothing is refused | one key `info.ui_label`; `info.name` becomes a refused key whose message names `info.ui_label`; the form reads and writes the one key | form and factory edited; `info` stays free form only for keys the spec does not own (see below) | D-0405 not touched (the two names may still differ) |
| `ui_label`, `label`, `name` as the short name | `ui_label` (plot, group), `label` (field, schema, join, info, session, registries), `name` (Gallery index, `home_theater.py:115`, bundle) | `ui_label` for all; the index `name` becomes `ui_label`; the `name` fallback at `home:115` is deleted | recipe migration (existing tool), session writer and reader, registries, index | M271 (not decided; her leaning in the ledger); D-0253 extended, not reversed |
| `ui_title` of a recipe against `ui_title` of app features | same word, two shapes (a string; an object `text/subtitle/visible`); no shipped file sets it; no key list | the same kind, the same shape (a string; `ui_subtitle`; `visible` moves to `flags`) | validator, `home:1139-1157`, template, docs | none |
| Group `ui_title` read by nothing | documented as used by the report and headings (`spec:485`), no reader (FACTS C5) | CONFIRM: either the report reads it as the section heading of its group, or the key leaves the format and the checker refuses it with a message. One of the two in the same pass | export code or format | none decided |
| `description` used as a tab text | `home_theater.py:105` | removed (the spec already says the fallback "goes", `spec:490`) | one line; one test | none |
| Gallery heading against the example name | the heading of `example_meta.md` is not read as a name (`taxonomy:97`) | the heading is guidance text: concordant, not equal (D-0397); the name is the plot `ui_label` (D-0387); no equality check (D-0405); an ADVICE when the name is more than 30 characters | none new | none |
| Nav item "Blueprint Architect" against value "Wrangle Studio" | the screen word and the internal value differ in 6 places (`home:1049, 1893, 2132, 2341`, `bp:943, 972`) | one table of user spaces (id, `ui_label`) in code; the internal value is the id and is never shown; the word on screen is the one `ui_label`. Which word is Eve's choice | rename of the internal value is a code-only change, tests can check it | ADR-092 (flag) not touched; naming is OPEN |
| Panel registry `label` against typed titles | two stores, 7 of 20 differ, the registry copy is read by nothing | one store: the registry `ui_label` is read by the renderer; a test compares every accordion title to it | `home_theater.py` renderers, `sidebar_registry.py` | none |
| Field `label` and `description` | checker refuses `description` on a field (FD01, `check:478-489`); the BLUEPRINT card shows it (`wrangle:1326`) | CONFIRM: the field has the same kinds as every thing, so `description` is accepted; the checker and the card agree | spec `field.optional`, checker | none |
| Field display name against a hidden column | the alias idea (D-0360) is marked in its own line "a proposal, not a rule"; her later words (`ledger:526`) say the question is open | the resolver returns the pair (label, slug); every screen that shows a label must also be able to show the slug (hover or a second line). A label is never the only name in a table the user acts on, in a filter or in the export (MINE; the data scientist viewpoint decides the rule) | resolver API; export | D-0360 (status conflict, FACTS C10) |
| `labels` of a join against the field's `ui_label` | two places for the display name of a column; the `labels` mapping has no reader found (FACTS 2.3) | CONFIRM: one place. Either the field's `ui_label` (a column in a table has one display name) or `labels` on the join for columns that exist only after a join (ADR-100 point 5 says display names go in `labels`, DEC23). Not both for one column | spec, checker | ADR-100 point 5 (DEC23) |
| Dataset, table, schema, collection, join | five words for table-like things (FACTS section 5) | see section 5 | docs and screen words | `Terminology.qmd` |
| Plot, figure, graph, chart | plot (recipe, screen), figure (export code and report), graph (lineage), chart (proposed D-0398) | see section 5 | words | D-0398 |
| Step, action, node | step (recipe), action (picker and registry), node (audit list, lineage) | see section 5 | words | none |
| `deployment_name` | written, read by a method no caller uses (FACTS 2.1) | `ui_label` of the deployment, shown in the Deployment panel and the banner fallback; or deleted. Never kept unread | bootloader, connector method, template | none |
| `info` is "free form" (`recipe_spec.yaml:28`) | any key accepted, so a wrong name key is silent | free form only for keys outside the kinds: a key in the spec's name list on `info` is checked; others stay free. `info.name`, `info.title`, `info.label` are refused with the new name | checker | ADR-100 point 2 (extends it) |

## 5. Words on screen and in documents (answer 4; MINE for the proposal, CONFIRM for the words)
One word per thing. A second word stays only where the engine owns it.

| Thing | Proposed word | Replaces | A second word that stays |
|---|---|---|---|
| The recipe | data analysis recipe, "recipe" in running text (CLAUDE.md section 1, Terminology) | "pipeline" for a recipe, "manifest" (retired, `audit_old_words.py:34`) | "pipeline" only for the automated deployment mode ("Automated Pipeline", `pipeline-static.yaml:3`) |
| A table | "table" | "dataset" (`target_dataset`, `export:1127`, folder `{dataset}/plots/`), "data preview table" | `target_dataset` as a format key until renamed (OPEN, a recipe format change); "schema" only for the declaration of a table (`data_schemas`) |
| Table declaration | "table definition" on screen; `data_schemas` key | "schema" and "data schema" mixed in help | "schema" in the format key |
| Joined tables | "joined table" | "collection" (`Terminology.qmd:10`, `collection_id`) | `collection_id` is a code name; the glossary maps it |
| The picture | "plot" | "figure" (export code, report text), "graph" (lineage), "chart" | "figure" inside the phrase "figure text" is plotnine's; "chart" appears only as the Gallery axis "Chart type" (D-0398) |
| Step | "step" (a line of a recipe or an audit) | "node" for a step, "transformation node", "wrangling steps" | "node" for a point of the lineage graph (a different thing) |
| Action | "action" (the registered operation a step calls) | none | `polars_*` names are Polars' |
| Export | "export" and "bundle" | "results bundle", "reproducibility bundle", "reimport bundle", "Export Bundle" | none |
| Apply | one verb "Apply" for putting a change in; "Send to Audit" stays (a different effect) | "Validate & Apply", "Apply Style", "Apply to session" renamed where the effect is the same (CONFIRM each: the effects differ, FACTS 2.8) | none |
| User spaces | HOME, BLUEPRINT, GALLERY, TEST_LAB (code); the screen word in one table | "Wrangle Studio", "Flight Deck", "Gallery Explorer", "Recipe Editor", "Test Lab Tools (right)", "LAB" | the screen label may be "Blueprint Architect" if Eve keeps it |
| Info panel | "Info" | "Data analysis recipe Info" | none |
| Notes panel | "Alerts" or "Notification Log" (Eve picks) | the other | none |
| Plot text | "figure text" for what is inside the picture | "axis title", "label" for it | `labs` and plotnine terms |
The Violet Law (`ComponentName (file_name.py)`, `rules_documentation_aesthetics.md:27-33`) is about naming code in documents; it is unrelated to these words and is not extended.

## 6. Variants (answer 5)

All three: the old key is refused with the new name, never accepted beside it (ADR-077, ADR-100 point 2, ADR-099 point 16, `rules_legacy_management.md`). Recipes go through the existing migration tool. Each file kind is changed in one pass: spec or table, checker or validator, readers, shipped files, docs, tests, in one reviewed change.

### Variant A: extend D-0253. `ui_label`, `ui_title`, `ui_subtitle` everywhere; `description` plain; `id` for identity
- Recipe: flip the four `label_keys` lines to `ui_label`; add `ui_title` and `ui_subtitle` to `info`, `description` to `field`; add `renamed:` entries for `info.label`, `schema.label`, `join.label`, `field.label`, `info.name`. Run `assets/scripts/migrate_recipe_engine_keys.py --apply` over 109 recipes plus 34 Gallery recipes (the Gallery generator `example_recipe.py:122-140` and `new_recipe.py`, `recipe_factory.py` also change). The tool is script-driven and a second run changes nothing (READ its docstring).
- Version: the spec header says changing a key changes `format_version`; format 1 was amended before its first release (D-0236). OPEN: stay in format 1 (not yet released) or make format 2.
- App features (8 files) and deployment (7 files): `display_name` to `ui_label`; `name` to `id`; `ui_title` becomes a string; `deployment_name` and `branding.banner.title` to `ui_label` and `ui_title`; add `renamed_keys.py` entries; add a key list to both validators. A one-time script is not needed for 15 files, but the refusal message names the new key.
- Code: one resolver in `libs/utils` replaces the 7 readers. Registries: `ui_label` in the action and component schemas (16 library files; up to 877 `"label"` hits to review, many are parameter labels that become `ui_label` too). Sessions: `label` to `ui_label` in `assembly.json`; add to `RENAMED_SESSION_KEYS` (`renamed_keys.py:63-69`).
- Docs: `Terminology.qmd`, `Standards_yaml.qmd:47` (the false "default axis title"), `data_contracts_adr.qmd`, the authoring guide, the UML (`docs/UML/app.mdj:34603`): from the generated table. 61 `.qmd` files in the book.
- Tests: the existing spec tests and migration tests are extended; new tests listed in section 7.
- Order that leaves a working app: (1) `names_spec.yaml` and the resolver, readers switched, behaviour unchanged except fallbacks; (2) recipe keys with migration; (3) app features and deployment with key lists; (4) panel registry as one store; (5) action and component registries; (6) sessions; (7) words and docs. Each step is complete and releasable.
- Cost on merit: the largest of the three; no shim.

### Variant B: plain `label`, `title`, `subtitle`, `description`, `id` everywhere
- Same structure as A, but the plot entry's `ui_label` and `ui_title` also become `label` and `title`. The prefix reason ("the others stay ui", D-0253) is dropped; the separation of app keys from plot content rests on `entry_keys` alone (READ `recipe_spec.yaml:70-76`), as it already does for `description`, `comment`, `taxonomy`.
- Changes more files than A: every plot file (34 Gallery + shipped), every code reader of `ui_label` (the 7 above plus `blueprint_plot_view`, `engine_keys_migration`, `recipe_factory`, `taxonomy`, `gallery_manager` messages), the docs that were just written for `ui_label`, and `renamed:` gets `ui_label` and `ui_title` as refused old keys for plots. Migration tool exists for `label` to `ui_label`; the reverse needs a new rule.
- Gain: shorter, the usual words; the user of an app features file writes `label:` without a prefix. Risk: `title` and `label` sit next to plotnine's `labs` content in one mapping (REASONED: nothing technical prevents it, a reader may confuse them). Two renames of the same key in a week.
- The one thing the prefix cannot do either: say whether a name is "shown in the UI" (her question, D-0405). `ui_title` is read only by the report (READ `export:373`). Neither prefix nor plain key answers it; the spec table does.

### Variant C: keep today's keys, fix only the collisions
- Concrete list: refuse `info.name`; give the app features title a name different from the recipe's (for example `banner_title`); settle the group `ui_title` (reader or removal), the field `description`, the `description` tab fallback; delete the unread registry `label` and `deployment_name` or give them a reader; a resolver for the recipe's own readers.
- Leaves: `label` in 8 or more jobs (FACTS section 4), `display_name`, `deployment_name`, `name`: one kind has a different key in each file kind. It answers the collisions but not "the same kind of name, one key, wherever written". M271 stays open for `info`, schema, join and field.
- Smallest change: about a dozen files; no migration of the 109 recipes except `info.name` where present.

## 7. How the scheme is kept true (answer 6)
1. One place: `names_spec.yaml` (MINE). It lists the kinds, the key, the length, the fallback and the file kinds each key is allowed in. D-0399's generator writes the table in the book from it (so the documentation cannot drift).
2. A check that can fail without a browser (REASONED; all pure Python):
   - the recipe checker reads the spec: unknown name keys fail, old keys fail with the new name, a length breach is an advice with the number;
   - app features and deployment validators read the same file; every shipped file passes;
   - the resolver is the only function that turns a thing into a name: a test lists the 7 readers' fixtures (plot with and without `ui_label`, group, plot with `ui_title`, a long label) and asserts one answer; a grep test fails if `.get("ui_label")` appears outside the resolver and the checker (this is the check that would have caught the 5 fallbacks);
   - a test that every accordion title equals its registry `ui_label`;
   - a test over all registered actions and components: every schema has `ui_label` and `description` (extend `schema_declaration_problems`, `ui_schema.py`).
3. An audit script: extend `assets/scripts/audit_old_words.py` (it counts retired words per area, `:32-40`) with the retired names: `display_name`, `deployment_name`, `info.name`, plus the words of section 5 for screen text. `--check` exits 1 when one is found.
4. A rule file: one short section in `.claude/rules/rules_data_analysis_recipe_structure.md` (the "Visible labels" part already says it, `:149-153`) pointing to `names_spec.yaml`, and a line in `rules_app_features_flags.md` for the app features and deployment keys. Do not copy the table into rules (two stores).
5. What none of this catches: whether a name is a good name (coherence of short name, title and description is the author's, D-0405); a screen word typed in a handler as a literal (the audit script sees a retired word, not a bad new one); the meaning of "short" (a number, advice only); a name in a figure (that is `labs`, checked by `plot_text_check.py`, not by this).

## 8. Where each variant touches decisions (information, not argument)
| | A | B | C |
|---|---|---|---|
| D-0253 (`ui_label`, `ui_title`, figure text in `labs`) | extends | reverses the names, keeps the principle of `labs` | keeps |
| D-0387, D-0397, D-0405 (Gallery names) | keep | keep (key spelling in text changes) | keep |
| D-0360 and the open M271 question on labels | answers M271 as `ui_label` (her words lean that way); D-0360's alias is a separate rule on use | answers M271 as `label` | leaves M271 open |
| ADR-100 point 2 (unknown keys fail; old keys named) | extends to `info` and to app features and deployment | same | partly |
| ADR-091 (configuration names), ADR-077, ADR-099 point 16 | consistent; extends strictness to app features | same | consistent |
| ADR-045 (Two-Category Law: libs headless, wiring in `app/`) | the resolver is pure in `libs/utils`; the screens call it | same | same |
| ADR-092, CLAUDE.md section 1 (words) | consistent | consistent | consistent |

## Recommendation
Variant A. On merit: it makes "one kind, one key" true for every file kind with the least new vocabulary, it reuses machinery that is already built and tested (`label_keys`, `renamed:`, the migration tool, `renamed_keys.py`), it closes the silent gap that app features and deployment accept unknown keys, and it needs no second rename of keys that are three days old. B is acceptable on merit if she prefers plain words, but it spends more files for a shorter spelling and removes the one place where the prefix does a mechanical job. C leaves the question that started the study (a purpose for each name) open and keeps `label` in many jobs; take it only as a first step: its collision fixes are all in A.
The resolver and `names_spec.yaml` (step 1 of A) are worth doing in any variant, and they leave a working app.

## To decide first (ranked)
1. Does a recipe get both a short name and a longer title in `info` (`ui_label` and `ui_title`), so `info.label` stops being "short and also the header"? (D-0405 left the header open; the owner's table calls it option C.) Everything else follows from this.
2. Key spelling: prefix everywhere (A), plain words (B), or only fix collisions (C). The user needs to be told: `ui_title` is read only by the report, so "ui" does not mean "shown in the UI".
3. Stay in recipe format 1 or make format 2 (a rename of 109 recipes and 34 Gallery examples). Tell her: any name change alters the recipe hash and the session key (not the result), so saved sessions of a migrated recipe will not match.
4. Whether a column's display name may be the only name shown (the field `ui_label`, D-0360): or must the real column name always be reachable. The user is told that a display name can hide which column was used.
5. The numbers for "short" and "long" (30 and 80 proposed from RUN data), and that a breach is an advice.
6. The group `ui_title`: a reader in the report, or leave the format.
7. The screen word for BLUEPRINT and for the notes panel, and the single verb "Apply".
8. Where the display name of a column lives: the field `ui_label` or the join `labels` (not both).

## Not verified
- No code run beyond a length count and greps. The resolver, the new spec file and the grep test are proposals, not tried.
- I did not read the session restore code: what happens to a saved session whose recipe hash changed is REASONED from `session_manager.py:10, 281-308` only.
- Not checked whether `load_data_analysis_recipe` hashes file bytes or parsed content (the docstring says per-file sha256 lines).
- The 877 count of `"label"` in `transformer` and `viz_factory` is a raw grep; how many are schema labels versus parameter labels, and how many files change, is not measured.
- The recipe selector, the Info panel rows and the HOME filter list were not checked for the name they show (FACTS section 8 still applies).
- Whether `check_gallery_at_start` notices a stale index `name` after a recipe edit (the index is a derived copy of `ui_label`, `gallery_manager.py:142`).
- Test counts were taken from file names (478 `test*.py` files), not from a test run.
- The `docs/` pages and the UML were not re-read; the doc list is taken from FACTS 2.9.
