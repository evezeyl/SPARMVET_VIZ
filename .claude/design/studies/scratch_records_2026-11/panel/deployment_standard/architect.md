# Architect viewpoint: the STRUCTURE of the deployment standard (2026-11-21)

Study only. Nothing was built, nothing in the repository was changed. Labels: READ (file:line, read by me in this session), FACTS (taken from the survey `FACTS.md`, not re-read), REASONED (follows from reading, not run). I ran nothing except greps and the copy of the survey (234 lines). Tags: DECIDED (ledger number) / CONFIRM / OPEN / MINE (my proposal). "Reconsiders" is information only and never a reason for or against an option.

## Decisions this rests on (quoted from the ledger lines I read)

- D-0413 (EVE, DECIDED): "And I think we will need to write a deployment standard as we are doing for recipes if its not done so we can track of the options for deployment". One document with a machine-readable key list like `recipe_spec.yaml`; for every key meaning, purpose, allowed values, default, who sets it, which code reads it, which screen shows it, options per use case; the use cases are OPTIONS, the paths and Data Import questions are not decided; "First step: a study and a draft of the STRUCTURE ... shown to her as a table; no key list is built before she has seen it."
- D-0412 (EVE, DECIDED): app features and deployment files get a list of allowed keys "as the recipe has"; an unknown or old key is refused at start with a plain line naming the key and, when known, the new name; shipped files checked in the same pass; a test that can fail.
- D-0411 / D-0407 (EVE, DECIDED): display keys carry `ui_`; the banner keys, `deployment_name` and the app features `ui_title` change; "migrated by the script, not by hand"; the two customized deployments are `demo-vetinst` and `web-demo` (D-0412).
- D-0399 (EVE, DECIDED): one source holds words and meanings; the documentation is generated from it; "a test fails if a generated file differs". Not built (FACTS D: no generator, no generated marker).
- D-0263 (EVE, DECIDED, not built): `runtime.python_interpreter` removed from the deployment files and from `rules_runtime_environment.md` section 5.

## 6-line summary

1. Recommend ONE written document with two parts (deployment; app features, with its sidebar files) plus shared sections, backed by ONE spec file `deployment_spec.yaml` in `libs/utils/src/utils/` (Tier 1, next to `recipe_spec.yaml`, same `package-data` line), and ONE pure checker `deployment_check.py` beside `recipe_check.py`. Reason: keys move between the two files (`renamed_keys.py:25-37`), several rules span both, and a deployer who is not a developer reads one place.
2. The environment variables go inside (same columns plus "overrides which key"); the palettes file goes inside as a short part of its own; the sidebar files go inside the app features part; the theme stylesheet stays outside with a pointer (only the key `branding.theme_css` is inside).
3. The spec holds every fact that is a statement about a key (meaning, allowed values and what each value means and costs, default, who sets it, read-by module, screen, check id, decision number, status, options per use case, refusal text). The template file, the key tables, the environment table, the use-case views and the refusal texts come from it; prose that explains and the worked example files stay hand-written, and the examples are real shipped files that a test checks.
4. Open choices (the 13 and fonts) live in a separate spec section `open_choices`, which the checker never reads; a key that depends on one carries the marker "NOT DECIDED, choice N"; no key of an undecided design is put in the allowed list.
5. Kept true by: the check at start (one call, before the other start checks), a test that every shipped file passes (templates included, structure group only), a test that the key lists of code and spec are the same list (no second list), a test that generated files equal the committed ones, the old-word audit reading the same `renamed` table, and a format number per file kind (OPEN for her, with a reason: only a number catches a key that keeps its name and changes its meaning).
6. Order: structure shown (now) -> spec skeleton and its own tests (no behaviour change) -> spec filled "as built" with status tags (no behaviour change) -> checker wired at start replacing the five lists and `renamed_keys.py` in one merge (D-0412) -> generators -> the D-0407/D-0411 one pass; everything about places, access words, `users`, fetch step, fonts waits for the 13 choices.

## 1. One document or two, and what is outside

| Variant | What it is | Pros | Cons | Couples or breaks | ADR or rule touched (information) |
|---|---|---|---|---|---|
| 1A one document, two parts, one spec file (RECOMMENDED, MINE) | Part A deployment, Part B app features (incl. sidebar files), shared sections (environment, palettes, cross rules, checks, renamed, use cases, open choices); one `deployment_spec.yaml` | Keys move between the kinds, so one `renamed` table can say "moved to deployment: branding.theme_css" (READ `renamed_keys.py:36-37`: `theme_css`, `ui_banner` went from app features to the deployment file; `renamed_keys.py:21`: `data_ingestion_enabled` went from the deployment file to a flag). Cross rules need both files: selector hidden requires a named recipe (READ `bootloader.py:617-639`, FACTS A1 row 4), `app_features_override` merges into flags (READ `bootloader.py:387-388`), `data_lookup` changes a screen (FACTS A1 row 6). One column set, one refusal format, one version rule. A deployer reads one place | Longer document; a deployer who never touches flags still sees Part B (mitigated: "Start here" per use case, generated, lists only the keys of MY case) | Spec file in utils contains the NAMES of HOME flags (Tier 1 holding app vocabulary): precedent `recipe_spec.yaml` holds `ui_label` and the gallery terms | ADR-091 (names and precedence): its key lists become history; ADR-048 sections 3 and 5 key text is already stale (FACTS C4) and is marked superseded for keys; ADR-011 (a library reads its spec as its own resource): respected |
| 1B two documents, two spec files | `deployment_standard` and `app_features_standard` | Each is shorter; flags can be owned by feature authors | The renamed table splits (a moved key is in neither or both); the cross rules have no home (a third document or a duplicate); two version numbers explained twice; the deployer who sets `default_app_features` or `app_features_override` must read both | Two checkers share a base or copy it | ADR-091 as above |
| 1C one document, two spec files: deployment spec in utils, app features spec in `app/` | Spec placed where the reader is | Flag names stay in Tier 3 | A moved key crosses a package boundary; `app/` has no `package-data` today (READ `app/pyproject.toml`: only dependencies) and the `config/` tree is in no package (FACTS D); the connector cannot read an `app/` spec; two checkers | Needs a packaging change in `app/` first | rules_runtime_environment.md section 4 (nothing broken), ADR-011 |

Recommendation: 1A. On merit: the thing being specified is "the files an installer writes to start the app", and those two files are chosen together, renamed together and checked together. Reconsiders a decision: none. D-0413 says "one document ... one document with two parts, or two documents (the coordinator proposes, with a reason)": this is that proposal.

Where each other file kind stands:

| File | Inside, own part, or outside | Reason |
|---|---|---|
| Sidebar files `config/ui/sidebars/*.yaml` (8 files, keys `visible`, `panels`) | Inside Part B, sub-section "Sidebar files" | They are `!include`d by app features and checked by `SidebarValidator` (FACTS A2); the panel TYPE list is owned by code (`sidebar_registry.py`) so it is an injected catalogue, and the standard shows the list generated from the registry, not typed |
| `config/palettes.yaml` | Inside, short part of its own | Read at start (`bootloader.py:927-995`, FACTS), a bad file is only a warning, its path is fixed in code (`bootloader.py:946`); whether a deployment can name another file is an OPEN point, so the standard lists it as "as built" with a marker |
| Environment variables | Inside, own section | They override file keys (precedence in ADR-091 :4417-4438, FACTS C5); the same story must be told once. Same columns plus: which key it overrides, secret or not, which script reads it. The two renamed variables (`SPARMVET_PERSONA`, `SPARMVET_PROFILE`) and the removed one (`SPARMVET_CONNECTOR`) go in the shared `renamed` table (today `renamed_keys.py:11-13`) |
| Theme stylesheet (CSS) | Outside, pointer to `rules_css_style_spec.md` | It is not a key list. Inside: only the key `branding.theme_css` (a path, must exist, base = working folder, FACTS A1 row 15). Do not confuse with the plot themes of D-0256 ("themes are code") |
| Palettes, sidebar, CSS and the Dockerfile and `bundle_connect.sh` | Scripts and image files are not specified here; the standard lists the variables they read | `bundle_connect.sh:90-102` reads `CONNECT_SERVER`, `CONNECT_API_KEY`, `SPARMVET_DEPLOYMENT_PATH` (FACTS B) |

## 2. The pair "written text + machine-readable list"

### Which file holds what

| File | Holds | Lives in | Why there |
|---|---|---|---|
| `deployment_spec.yaml` | Everything that is a statement about one key or one value (see section 4), the `renamed`, `removed` (tombstones with decision, date, why, expiry) tables, `use_cases`, `open_choices`, the check catalogue texts, `format_version` | `libs/utils/src/utils/` | Tier 1 has no peer import and already ships one data file as package data (READ `libs/utils/pyproject.toml`, `[tool.setuptools.package-data] utils = ["recipe_spec.yaml"]`); `libs/connector` already imports `utils` and declares it (READ `libs/connector/pyproject.toml:13`, `filesystem.py:17`); `rules_runtime_environment.md` section 4 says a different frontend (CLI, Galaxy wrapper) imports only the layer it needs, so the check of a deployment file must work without `app/`; the container installs libraries non-editable, so only a file inside a package reaches it (`recipe_format_spec.md:839`, FACTS D) |
| `deployment_check.py` (pure) | `check(raw, kind, catalogs) -> Result(problems, coverage)`, same shape as `recipe_check.py` (`Problem` with code, severity, path, message, fix; `coverage` says which groups ran) | `libs/utils/src/utils/` | Same reason; `coverage` makes a consumer assert that everything ran (template check runs the structure group only, start runs all) |
| Catalogues injected by `app/` | Panel types (`sidebar_registry.py`), names of shipped app features files, recipe names found in the recipes folder, connector class names | `app/` | Code-owned lists stay with their owner and are injected, as `check_recipe` takes the action and component catalogues (`recipe_format_spec.md:818`) |
| The written document | Prose: how to choose, why, what the user sees, the use-case stories, the open choices explained; plus generated key tables | draft in `.claude/design/` while she reviews (as the recipe spec was); then spreads: short normative rules to `.claude/rules/` (changed only with her confirmation), reference to `docs/reference/` (the reader is a deployer, so the final home is the user documentation, not a design folder) | Mirrors `recipe_format_spec.md` section 14 "how this file spreads" |
| Examples | The shipped files themselves (`config/deployment/**`, `config/app_features/*.yaml`); the document includes them (`{{< include >}}` has precedent: `docs/appendix/FAQ.qmd:94`, READ by grep) | `config/` | A pasted example in prose is a second store; a tested file cannot drift |

Rule for which list lives where (MINE): a closed list that is a property of the FORMAT (flag names, `data_lookup` values, `deployment_type` values, `session_import` keys) lives in the spec and the code reads it from there, as the plot library reads `plot_defaults_keys()` from the recipe spec (READ `recipe_check.py:84-92`); a list owned by code (panel types, recipe names) is injected. Today that rule is broken in six places (READ): `_REQUIRED_FLAGS` (`app_features_validator.py:15-29`), `DATA_LOOKUP_CHOICES` (`orchestrator.py:45`), the connector's literal `"irida"`/`"galaxy"` (`connector/__init__.py:40-45`), `_SESSION_IMPORT_KEYS` (`session_manager.py:853`, used at `889-894`), the names written into a message (`bootloader.py:747-749`, which omits `web-demo` and `demo-vetinst`), plus the renamed tables (below). Each is a second store that can disagree with the new allowed-key list. They must be replaced in the same merge that wires the check (no shim, "one authoritative way"), and a test like `libs/utils/tests/test_engines.py:21-31` ("no second list of engines") must assert it.

Renames today live in at least five stores (READ): `app/modules/renamed_keys.py`, `libs/utils/src/utils/legacy_keys.py`, the `renamed` table of `recipe_spec.yaml:83`, `assets/scripts/migrate_config_vocabulary.py` (`SESSION_KEYS`, `_RENAME`), and the word list of `assets/scripts/audit_old_words.py`. The deployment spec's `renamed`/`removed` tables replace `renamed_keys.py` (deployment and app features parts) and become the list that the migration script and the old-word audit read. The recipe-side stores are a different standard and are not touched here (MINE, information: the same refactor is open there).

### What is generated, what stays hand-written

| Output | From | How it is kept true |
|---|---|---|
| Key tables of the document (all fields except prose) | spec | generated file with a header "generated from `deployment_spec.yaml` by `<script>`; do not edit"; test fails if the committed file differs (D-0399 wording) |
| `config/deployment/templates/deployment_template.yaml` (and an app features template, which does not exist today) | spec: key order, `meaning` as comment, `template_value`, `template: include|comment|omit` | same test; also the template passes the structure check. Removes today's wrong template sentences: FACTS C disagreements (a), (b), (e), (j) |
| Environment variable table (replaces `environment_variables.qmd:22-26`) | spec `environment` | same test. Removes (d) wrong error types and (f) Galaxy variables |
| `config/deployment/README.md` key table | spec | the README keeps the hand-written folder layout and resolution text, and points to the generated table |
| Use-case view "keys for my case" (one per case) and the full use-case matrix (appendix) | spec `use_cases` and each key's `by_use_case` | same test |
| Flag matrix (flag against app features file) | the shipped `config/app_features/*.yaml` themselves, NOT the spec | derived from files, so it cannot disagree with them (FACTS A2 matrix was built by hand) |
| Check catalogue table and `renamed`/`removed` table | spec | same test |
| Refusal texts | NOT generated into a file: the checker reads the sentence from the spec at run time (the recipe does this: `renamed`, `old_shapes`, `removed` sentences "are the refusal text", FACTS D) | a test per `renamed`/`removed` entry puts the old key in a minimal file and compares the exact line |
| Hand-written | the explanation of how to choose, the stories, the open-choice questions, cross-rule prose, and the one sentence of `meaning` per key (written once, in the spec) | rule of the document: no default, allowed value or behaviour is stated in prose; prose points to the generated table |

Convention (MINE): every generated file carries one marker line and one shared test helper compares; the Gallery cheatsheet of D-0399 should use the same marker and helper so there is one way (OPEN whether she wants one helper or two generators; information only).

## 3. Section list of the written document (order; reader: D deployer, R author of recipes, V developer)

| # | Section | Holds | Reader |
|---|---|---|---|
| 0 | How to read this document | The tags (DECIDED / NOT DECIDED / AS BUILT), what generated means, the vocabulary (deployment, app features, recipe, user space) | D R V |
| 1 | Start here: find your case | One entry per use case: one line, the example file, the keys you must write, the keys that do not apply, the open choices that touch it (generated). A deployer stops reading after this and the key table of the keys named | D |
| 2 | The files and the start | The file kinds, who writes each, how a deployment is found (kwarg, env variable, file, development fallback), what happens at start, what a refusal looks like | D V |
| 3 | Part A: the deployment file | Key tables by group: which app features and recipe, locations, branding, data lookup, session import, connector blocks, app features override | D V |
| 4 | Part B: the app features file | Name keys, the flags in groups with cascades, `testing_mode`, `automation`, `blueprint_agent`, the workspaces and sidebar slots | D (little), V |
| 5 | Sidebar files | `visible`, `panels`; the panel list generated from the registry | V |
| 6 | The palettes file | Keys, the three shipped palettes, what is checked | D R |
| 7 | Environment variables | Table with override, secret, reader | D V |
| 8 | Theme stylesheet and other files | Pointer only | D |
| 9 | Rules that span files | Selector hidden needs a recipe; override against cascades; `data_lookup` and the Data Import screen; each with its check id | D V |
| 10 | The check catalogue | One row per check: id, group (structure or start), severity (refused / warning / advice), text, who runs it, test name | V |
| 11 | Renamed and removed keys | Replacement table with the decision number; tombstones with expiry | D V |
| 12 | Use cases: the matrix | Generated matrix key against case; every cell is a value, "-" or "NOT DECIDED, choice N" | D V |
| 13 | Open choices (NOT rules) | The 13 choices and fonts as options with consequences, status NOT DECIDED, no preferred option | D |
| 14 | Format version and how this standard is kept true | The number rule, the tests of section 6, how to change a key | V |

Left out on purpose: a section "what the code accepts today and must stop accepting" (the recipe spec has one, section 16). It is a task list and goes stale the day the work is done; the 18 disagreements of FACTS C go to the task, and the generated tables remove most of them (REASONED).

## 4. Fields recorded for every key (columns of the key table)

Owner named = in D-0413. Stored: S = hand-written once in the spec, D = derived or generated, T = verified by a test.

| # | Field | Owner named | Stored | Reason and notes |
|---|---|---|---|---|
| 1 | key (dotted path), file kind | implied | S | `branding.banner.ui_label` |
| 2 | meaning (one plain sentence) | yes | S | the only prose per key |
| 3 | purpose, split in two: `purpose` (why would I set it) and `kind_of_name` (one of the seven kinds of D-0406, only for name keys) | yes | S | a name key says identity, short name, title, description, help, column name or figure text |
| 4 | type | no, added | S | string, path, number, switch, list, block |
| 5 | allowed values: for a closed list each value gets `means` and `consequence` (and `status`) | yes, extended | S | the software informs: each option shown with what it does and costs, no preference |
| 6 | required, optional, or required-when (with the check id) | no, added | S | today `project_root` is "REQUIRED" in ADR-048:1106 and optional in code (FACTS C c) |
| 7 | default when absent, or "none: start refused, check id"; plus `silent` yes/no | yes, extended | S, T | a default that code and validator state differently is a silent choice: badge default True (`bootloader.py:859-864`), `testing_mode` True (`bootloader.py:899`), the validator says "defaulting to False" (`app_features_validator.py:101-103`; FACTS C o). One value per key in the spec; code reads it from the spec |
| 8 | who sets it: deployer, app features author, pipeline, launch (env variable or kwarg), script | yes | S | |
| 9 | read by: module names (not file:line) | yes | S, T | lines go stale; the test checks that the module contains the key as a quoted string |
| 10 | shown on: screen names in user-space words, or "no screen" | yes | S | not testable without a browser; hand-written, checked by a reviewer only |
| 11 | options per use case: list of {case, value or advice, status as built / NOT DECIDED choice N / not applicable} | yes | S | only where a case differs; the matrix is generated |
| 12 | checked how: `refused` / `warned` / `not checked`, with check id | no, added | S, T | FACTS A1 lists keys not checked (`deployment_type`, `project_root`, `app_features_override` names) |
| 13 | result effect: `none` / `which data or recipe is read` / `what the export holds` | no, added (MINE) | S | the deployer must see which keys can change a result: `data_lookup`, `locations.raw_data`, `locations.data_analysis_recipes`, `default_data_analysis_recipe`, `testing_mode`, interactivity and audit flags. Fits ADR-090 "nothing changes a result silently" |
| 14 | path base (for path keys): project root, working folder, the file's own folder | no, added | S | the bases differ today: locations from `project_root` or working folder (`filesystem.py:41-49`), `theme_css` from the working folder (`bootloader.py:868`); F14 of the deployment study |
| 15 | overridden by (env variable, kwarg) | partly | S | precedence in one place |
| 16 | status: `as built` / `removal decided` (decision) / `NOT DECIDED (choice N)`; `decided_by` (D-number, ADR) | no, added | S, T | `deployment_name` (D-0411), `python_interpreter` (D-0263) are in the files and read by nothing; the status says so without hiding them. A `removal decided` entry must have a task (rule 4 of agent_principles: "A deprecation has a removal task") |
| 17 | `template_value`, `template` (include / comment / omit) | no, added | S | feeds the template generator |
| 18 | secret yes/no | no | S | environment variables only; file keys never hold a token (the IRIDA token is an environment variable, FACTS B) |
| 19 | since which version | asked "add or remove" | REMOVED as a field | the app has no version attached to a key; the format number (section 6) answers "since when" |
| 20 | `open_choices: [n]` marker | no, added | S, T | the visible "may change" mark of section 5 |

Per allowed value (field 5): `means`, `consequence`, `status`. This is where the standard tells the deployer what they need at the moment of choosing between two options (for `session_import` limits: what a larger value costs; for `data_lookup`: what the Data Import screen shows; see the closing list "What the user must be told").

## 5. How the use cases and the open choices appear

| Variant | What | Pros | Cons |
|---|---|---|---|
| 5A matrix only | one big key-by-case table | complete overview | 19 cases by 35 keys, mostly "same"; a deployer cannot see what to write |
| 5B worked example file per case only | one file per case | concrete for a deployer | an example for an undecided case would be a decision; 13 of the 19 cases have no shipped file today (FACTS E: closest file exists for cases 2, 3, 4, 5, 11, 15, 17 only); an example is a second store unless it is a tested real file |
| 5C both, generated from one list, examples are real tested files (RECOMMENDED, MINE) | `use_cases` list in the spec (stable ids of my own, e.g. `local-checkout`, `static-page`, `static-pipeline`, `container`, `github-install`, `posit-connect`; each entry says whether it was listed by her in block M430 or added by an agent) plus `by_use_case` on keys | The deployer's view "keys for my case" is generated; the matrix is an appendix; a case with no decided design shows its example as "no example: NOT DECIDED, choice N" | The use-case list needs her confirmation (CONFIRM) |

An OPEN choice in the standard (MINE):
1. A separate Part (section 13) generated from `open_choices` in the spec: id, question, options with what each gives and costs, link to the study table. No "recommended" column: the standard informs, the study recommends.
2. The checker never reads `open_choices`, so a key that belongs only to an undecided design (named places, access words, `users`, fetch step, font list) is NOT in the allowed list. A file that uses it is refused today with "this key is not decided yet", which is true. A test asserts that no key named in `open_choices` appears in `elements`.
3. A key that exists today and depends on a choice (locations, `cache`, `user_data`, `data_lookup`, `project_root`, `irida`, `deployment_type`, `testing_mode`, palettes path) keeps its row, status `as built`, with the marker "NOT DECIDED: may change by choice N" in the key table and in the use-case cells.
4. When she decides a choice: promotion is a small written step (add keys to `elements` with `decided_by`, add `renamed` entries for the keys replaced, bump the format number if a meaning or a name changed, migrate files by script, remove the choice from `open_choices` and leave a ledger reference). Nothing in the standard changes before that.

Reconsiders: none. It keeps D-0413 ("WITHOUT deciding the paths and Data Import questions").

## 6. How the standard is kept true

| Check | What it proves | Where | What it does not catch |
|---|---|---|---|
| T1 the spec describes itself: every key has all required fields; every closed list value has `means`; every `decided_by` exists in the ledger (`decision_ledger.py check`) | the spec is complete | `libs/utils/tests` | whether a sentence is true |
| T2 every shipped file passes the structure check: 7 deployment files, 8 app features files, 8 sidebar files, palettes, and the templates (structure group only; they have placeholders, so they cannot start, READ `test_shipped_deployments.py`: templates are excluded from the start test and only get four key assertions) | no shipped file uses an unlisted or old key; the two customized deployments are included (D-0411 condition) | app tests; the structure part in utils | values that only a start can test |
| T3 the key list of code equals the key list of spec: every quoted key read in the listed `read_by` module is in the spec and every spec key with status `as built` is read in its module (promotes `assets/scripts/inventory_config_keys.py`, a read-only heuristic script, to a test that uses the spec instead of scanning the files; READ its docstring "heuristic") | catches the survey's finds: keys set by nothing (`runtime.python_interpreter`, `deployment_name`) and keys read by nothing (`blueprint_agent.model`...) only when status says `removal decided` | app tests | a key read through a computed name (READ: flags go through one accessor `self.flags.get(feature, default)`, `bootloader.py:864`, and `features.get(child)` loops at `bootloader.py:815`, `app_features_validator.py:124-175`; these read lists of names held in code, so T4 covers them); a module that still contains the string but no longer acts on it |
| T4 no second list: the lists of section 2 are read from the spec (as `test_engines.py:21-31`) | the five duplicate lists cannot return | app and utils tests | a list in a language other than Python (`bundle_connect.sh`) |
| T5 generated files equal committed files (template, tables, environment table, use-case views) | docs and template cannot drift (D-0399) | one shared helper | hand-written prose that states a behaviour: the rule "no default or behaviour in prose" is a review rule, a script could grep prose for known key names only |
| T6 per `renamed`/`removed` entry: the old key in a minimal file gives the exact line naming the new key (D-0412); per tombstone: `tombstone_expires` not passed | the refusals work | utils tests | a rename of the VALUE of a key (e.g. a renamed app features file name): add `renamed_values` or leave it to the file-exists check, OPEN for the key stage |
| T7 every check id in the catalogue has a test that fails when the check is removed (break it once, as `rules_verification_testing.md` section 9 asks) | no dead check | tests | a check whose test passes for the wrong reason |
| T8 packaging: the wheel contains `deployment_spec.yaml` (extend `libs/utils/tests/test_packaging.py:17-29`) | the container finds the spec | utils tests | |
| T9 old-word audit reads the `renamed`/`removed` words from the spec | no old word in docs, templates, comments (the stale comment `ui.py:343`, `local.yaml.example` in `bootloader.py:310,688`, FACTS C 20) | `assets/scripts/audit_old_words.py --check` | text that paraphrases an old word |
| T10 no open-choice key in `elements`; every `open_choices` entry has status NOT DECIDED | an undecided option cannot become a rule by accident | utils tests | |
| T11 the output of every writer of deployment files passes the check: `assets/scripts/create_test_deployment.py` writes `deployment_name` and `python_interpreter` (FACTS C 24), the test fixture `SPARMVET_TEST_GENERATED_DEPLOYMENT` (`app/tests/conftest.py:25-37`, FACTS B) | no third writer of the format | app tests | |

The check at start (D-0412): ONE call, `deployment_check.check(..., kind="deployment")` and `kind="app_features"` (sidebar files inside the second), at the head of `Bootloader.__init__`, where `exit_if_errors(renamed_deployment_key_errors(...))` stands today (READ `bootloader.py:114`), and it replaces that line. All existing start checks (`bootloader.py:321-359`, `164-178`, `587-639`, `AppFeaturesValidator`, `SidebarValidator`, `filesystem.py:53-66`, `session_manager.py:879-907`) stay as the "start" group but are listed in the check catalogue with ids and the same severity words, so that the user sees one kind of refusal. Point of no return: the start; before it nothing is written. Today the user folder is created late and fails with a raw error at the first click (F11 of the deployment study, run by the architect there); the standard lists that check as a gap and its fix belongs to the deployment study (S3 there), not to this document.

"One code path" claim: D-0412 "an unknown key is refused at start" is one path only if the five duplicate lists are removed in the same merge; otherwise the allowed-key list and, e.g., `_SESSION_IMPORT_KEYS` can disagree (the survey found `session_manager` already refuses unknown keys on its own, FACTS A1 row 12, so a new list beside it is the second store). REASONED.

### Versions: does a deployment file carry a format number

| Variant | What | Pros | Cons | Reconsiders |
|---|---|---|---|---|
| 6A none; the old key is refused by name (D-0412 alone) | no number | nothing to add to files | a key that keeps its name and changes meaning is accepted silently (examples pending now: the path base of relative paths, F14; `data_lookup` under confinement, choice 4; the meaning of `locations.cache`, no reader today; defaults of `testing_mode`) | no |
| 6B a number in the spec only (version of the standard, shown in the document and in the generated template), not in the files | | the document states which version it describes | does not protect a file | no |
| 6C one required key per file kind (`deployment_format`, `app_features_format`), counters separate; sidebar and palettes files follow the number of the kind that includes or reads them; rule as in `recipe_spec.yaml:2-3`: a removed or renamed key, or a changed meaning, default or base changes the number; a new optional key with an unchanged default does not | the refusal for an old file is ONE line naming the file and the migration script (as recipe checks V01 to V03, READ `recipe_check.py:248-258`), plus the per-key lines | every file, including a user's own, gets one more required key and one migration; a number can be bumped without need (churn) | no (D-0412 stands; the recipe does the same) |

Recommendation: 6C, on merit, because only a number makes "nothing changes a result silently" true for a key that keeps its name. OPEN for her; the cost is one key in every file. Whether the recipe spec's rule "changing a key changes the version" is enforced by a test, I did not verify (NOT VERIFIED).

## 7. Order of work after she has seen the structure

Each step leaves a working app. "W" = what waits.

| Step | Work | Behaviour change | Why in this place |
|---|---|---|---|
| S0 | She answers "To decide first" below | none | the structure is the order |
| S1 | Spec skeleton: the field schema (section 4), `use_cases`, `open_choices` (copied from the study table, status NOT DECIDED), `format_version`; test T1, T8, T10; `package-data` line | none, nothing reads it | cheapest place to find that the fields are wrong, before 60 keys are typed |
| S2 | Key entries "as built" for deployment, app features, sidebar, palettes, environment, with status tags (`removal decided` for `deployment_name`, `ui_title`, `python_interpreter`); test T2 (pure, structure only) and T3 | none | the spec describes today; every wrong sentence of FACTS C is settled once, in one place |
| S3 | `deployment_check.py` wired at start, replacing `renamed_keys.py`, `_REQUIRED_FLAGS`, `DATA_LOOKUP_CHOICES`, the connector's literal names and `_SESSION_IMPORT_KEYS`; tests T4, T6, T7, T11; the format number if 6C is chosen, with a script that adds it to the shipped files | an unknown key in a file now stops the start (D-0412); typos in `app_features_override` are refused | one merge, no half state, no alias |
| S4 | Generators and their test (T5): key tables, template, environment table, README table; hand-written copies of the same tables removed in the same merge | none | no second store |
| S5 | The D-0407 / D-0411 one pass through the spec: `renamed`/`removed` entries, migration script, the two customized deployments proved by the test D-0411 asks for | yes (renames) | the spec is the source for the script, so the pass is safe to repeat |
| S6 | Use-case views and matrix generated; sections 1, 12 | none | |
| S7 | Promotion of each decided choice (section 5, item 4) | per choice | |

W (waits for the 13 choices and fonts): any key of named places, access words, `users`, fetch step, font list; the fate of `locations.cache` (no reader, ADR-091 CONFIG-CACHE-LOCATION-1) and of `user_data`; the meaning of `data_lookup` and of relative paths under confinement (choice 4); `project_root`; the `irida` block and the `deployment_type` classes (choices on IRIDA and API); the key for a palettes path; the default of `testing_mode` with Data Import overwrite (choice 8); the use-case examples for cases with no design; the format number bump that the choices will cause. Not waiting: `python_interpreter` and `deployment_name` removal (decided), the renamed banner keys (decided).

## Where the structure reconsiders or amends a decision or rule (information)

| Item | Amended or touched | Note |
|---|---|---|
| Spec file in `libs/utils` holding app features flags | `rules_runtime_environment.md` section 4 (Tier 1 base): respected, no peer import; ADR-099 16(g) (one rule set in utils) analogous | CONFIRM for her: Tier 1 gets app vocabulary, as `recipe_spec.yaml` already has `ui_label` and gallery terms |
| Renamed tables of deployment and app features move from `app/modules/renamed_keys.py` to the spec | ADR-091 point 2 (old key refused with new name): same behaviour, one store; ADR-077 (fail fast, Group B soft / Group D fatal): the check catalogue must use the same classes | the soft cascades (`bootloader.py:811-829`) are silent except a printed line; the catalogue must say what the user sees: OPEN, see list below |
| Key lists of ADR-048 sections 3 and 5 and ADR-091 | become history ("see the standard"); `rules_runtime_environment.md` section 5 ("python path MUST be in the deployment") contradicts D-0263 and must not be copied | scribe step after S2 |
| Template and README become generated | `rules_documentation_aesthetics.md` section 4 (DRY: use includes, no repeated content): supports it | |
| Format number | none (D-0412 stands) | |

## To decide first (ranked)

1. One document with two parts and one spec file (1A), or two documents (1B)? Everything else follows. Consequence for her: with 1A a deployer reads one place and a key that moves between the files has one entry; the document is longer and Tier 1 holds the names of HOME flags.
2. Does the spec live in `libs/utils` (so the connector and any other frontend can check a deployment file without `app/`) or in `app/`? Consequence: `utils` grows; the other choice needs `package-data` in `app/` and the connector cannot read it.
3. Does each deployment and app features file carry a format number (6C)? Consequence: one key in every file, including users' own, and one migration; without it a key that keeps its name and changes meaning is accepted silently.
4. Are the open choices shown in the standard as a separate Part with no recommended option, and are keys of undecided designs refused today with "not decided yet"? (Section 5.)
5. The use-case list: is her list of block M430 plus the cases agents added the list of the standard, and who may add one? (CONFIRM.)
6. Which severity does each silent behaviour get (refused, warning on screen, advice): the soft cascades, a missing flag (the validator only warns, `app_features_validator.py:99-103`), `testing_mode` and badge defaults, an unknown panel type (printed warning only, `sidebar_validator.py:165-171`)? The standard cannot be written without one answer per item; it is hers (rule: the software informs, the user decides).
7. Per flag: required (a missing one is refused) or optional with one written default? (Today the three defaults disagree, FACTS C o.)
8. Is the generated-file convention one helper for the Gallery cheatsheet and the deployment standard?

For the key stage, not now: the app features `display_name` is a display key shown as a badge (FACTS A2) and D-0407 says every display key carries `ui_`; D-0411 names `ui_title` and `deployment_name` but not `display_name`. CONFIRM whether it becomes `ui_label`.

## What the user must be told in the standard to choose well (not what to choose)

- For each key: what it does, what it costs to set it, what happens when it is absent (the default and whether it is silent), whether it can change which data or recipe a result is made from, and where it is read from (base folder).
- For each allowed value of a closed list: what it means and what it changes on screen (e.g. `by_dataset_id` shows "Data location (provided by deployment)").
- For a key that depends on an open choice: "NOT DECIDED, may change", with what the file will have to change when it is decided.
- At a refusal: the file, the key, what is allowed, the new name when known, the migration script when the whole file is old; never a stack trace.
- That the shipped examples are tested and that an example for a case with no design does not exist.

## Not verified

- I did not run the app, the checker, or any test; no prototype of `deployment_check`. All statements are READ or REASONED.
- That `deployment_spec.yaml` in `libs/utils` installs in the container wheel: REASONED from `libs/utils/pyproject.toml` and `recipe_format_spec.md:839`; the existing packaging test covers `recipe_spec.yaml` only (FACTS D).
- The counts of flags and keys come from FACTS, not recounted. FACTS section A and C (every other `file:line`) were not re-read except where cited as READ above.
- Whether a test enforces "a changed key changes `format_version`" for the recipe spec.
- Whether Quarto includes a generated fragment under `docs/` builds and freezes cleanly (`docs/_freeze` exists); `{{< include >}}` of a YAML file has precedent, a generated `.qmd` fragment has none.
- Whether the connector or a Galaxy wrapper would really call a deployment check without `app/` (a design argument, no user yet).
- What an audit would not catch: T3 sees quoted names only; "shown on" and `meaning` sentences are hand-written truth; a test that generated files are current cannot tell that the spec sentence is wrong; the old-word audit does not see paraphrases; the `bundle_connect.sh` and Dockerfile readers of variables are outside Python tests.
