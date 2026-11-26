# Deployment standard: the structure. DEVELOPER viewpoint (2026-11-21)

Labels: RUN, READ (file:line), REASONED. I ran nothing except `grep` and `wc`. I built nothing. Her rule applies: build time is no argument; effort and risk below are facts for ordering.

## 6-line summary

1. One document, one machine-readable file, with sections: `deployment` and `app_features` as the two main parts; `sidebar`, `palettes` and `environment` as short sections of the SAME yaml (they are read by the same bootloader and the environment overrides deployment keys); the theme stylesheet outside, with a pointer (it holds no keys).
2. The source is `libs/utils/src/utils/deployment_spec.yaml` (next to `recipe_spec.yaml`, same packaging, read through `importlib.resources`). The written text for deployers is a Quarto page in `docs/deployment/`; the key tables in it, the template file and the flag matrix are generated from the yaml; the story, the use-case guide and the worked examples are hand-written.
3. Every key records 20 fields (table below). Two I recommend adding that she did not name: `status` (active / reserved, no reader / removal decided) and `check` (how it is refused, with which text).
4. Use cases: BOTH a matrix (use case against key) and one worked example file per use case, with the matrix generated from the yaml and each example file tested by starting it. An OPEN choice is a value with `status: open` and a decision-state column; the generator prints it in a box "NOT DECIDED" and the template file never contains it as live text.
5. Keeping it true: start check (D-0412), a test that every shipped file passes, a test "key in the list is read" (exact) and "key read is in the list" (exact only if reads go through one accessor; heuristic otherwise: she must choose), the old-word audit, and a format number only if she wants one (I show both ways).
6. Order: pure code first (the spec file and its loader, no behaviour change), then the check, then the renames of D-0411, then generation, then the use-case part; everything about where recipes and data are read and written (the 13 choices) waits.

## 1. One document or two, and the neighbours

| Variant | What | Effort | Risk | Tests |
|---|---|---|---|---|
| A | One document, one yaml. Parts: deployment, app features. Short sections: sidebar, palettes, environment. Theme: pointer | medium | low | one loader test, one generator test |
| B | Two documents, two yaml files (`deployment_spec.yaml`, `app_features_spec.yaml`) | medium+ | medium: the environment variables and `app_features_override` cross both; one key described in two places | two of everything, plus a test that the cross references agree |
| C | One document, one yaml with ONLY deployment and app features; sidebar, palettes and environment documented where they are today, with a pointer | small | medium: the three outside things stay unchecked (the survey found unknown panel type only a printed warning, `sidebar_validator.py:165-171`; palettes file path fixed, `bootloader.py:946`) | as A, fewer |

Recommendation: A. Reasons (REASONED, on merit): D-0413 says "one document". The `environment` section is needed to fill the column "what an environment variable overrides" (SPARMVET_DEPLOYMENT, SPARMVET_APP_FEATURES, SPARMVET_DATA_ANALYSIS_RECIPE, SPARMVET_IRIDA_TOKEN; FACTS section B). `app_features_override` sits in the deployment file but holds flag names of the app features part; with two files a deployer would read two documents for one line. The sidebar files are an enumerated vocabulary (panel ids) with a validator already; listing the allowed panel ids in the yaml lets D-0412's refusal cover them (today an unknown panel type only prints, FACTS A2).

The theme stylesheet: a pointer. It has no keys. The key `branding.theme_css` is described in the deployment part and says: "a path to a stylesheet; read from the working directory (not project_root, `bootloader.py:868`)". D-0256 says themes are code and there is no deployment setting for a theme folder.

`config/palettes.yaml`: a section with its own allowed keys. Its path is fixed in code (`bootloader.py:946`), so the section says "not a deployment choice".

## 2. The pair "text + key list", and where each lives

| File | Holds | Where | Why |
|---|---|---|---|
| `deployment_spec.yaml` | the key list: per key every field of the table below; `renamed` (old key to new key or "removed: why"); `removed` (tombstones with decision and date, as `recipe_spec.yaml:145-163`); `environment`; `use_cases` (ids and names only); `format_version` if she chooses one | `libs/utils/src/utils/` | Tier 1 holds the recipe spec and is packaged (`libs/utils/pyproject.toml:17-18`); the connector (Tier 2) already imports from utils (FACTS D); the bootloader (Tier 3) reads downwards. A spec in `config/` is not packaged (FACTS D). The connector then reads its own keys from the same file without importing `app/` |
| `deployment_check.py` | load, unknown-key refusal, required keys, value rules, refusal text built from the yaml | `libs/utils/src/utils/`, next to `recipe_check.py` | pure, no Shiny, testable without the app |
| `renamed_keys.py` | today holds the old-to-new tables in code (`app/modules/renamed_keys.py:1-60`, 245 lines, 13 importers: READ by grep) | moves into the yaml; the module keeps only the function that raises | one source for the refusal text. Without this there are two tables (no half fix) |
| Quarto page `docs/deployment/deployment_standard.qmd` | hand-written: how to choose, use-case guide, worked examples, what you see when refused | `docs/` | the deployer reads here, not in `.claude/design/` (the recipe text sits in `.claude/design/recipe_format_spec.md`; a deployer is not a developer) |
| Generated key tables | one table per part, from the yaml | `docs/deployment/_keys_deployment.qmd`, `_keys_app_features.qmd` (committed) | D-0399 pattern: "a test fails if a generated file differs" |

Generated from the yaml: the template file `config/deployment/templates/deployment_template.yaml` (its comments), the key tables, `config/deployment/README.md` key list, the flag matrix (from the yaml descriptions plus the eight shipped app features files; the matrix cells come from the files, so a changed file regenerates it), the refusal texts (built at run time from `renamed`, not printed to a file), the environment variable table of `docs/reference/environment_variables.qmd`. Hand-written: the use-case guide, the worked examples, the explanations of consequences, the ADR text.

The generator is an `assets/scripts/` script (rules_asset_scripts), run by a test in compare mode. This is new tooling: there is no generator today (FACTS D: "NOT generated: no docs, cheatsheet or template"). Effort: medium. Risk: the first generated template differs from the hand-written one in wording; the owner sees a diff.

## 3. Table of contents of the written document (order; reader)

| # | Section | Holds | Reader |
|---|---|---|---|
| 1 | One page | what a deployment is, what an app features file is, how they meet, the order of start (kwarg, env, default), what happens when a file is refused | deployer |
| 2 | Find your case | the use-case matrix (case against key), with a link to the example file of each case | deployer |
| 3 | Open choices | the 13 choices as OPTIONS, each: the options, the consequence of each, "NOT DECIDED", the ledger line when it exists | deployer, owner |
| 4 | The deployment file: keys | one block per key (fields below) | deployer, developer |
| 5 | The app features file: keys | flags, selector, automation, blueprint_agent, workspaces; the flag matrix per shipped file; cascades and which are refused | deployer, recipe author |
| 6 | Sidebar files | allowed panel ids, the gate of each | developer, deployer who builds a custom app features |
| 7 | Palettes | the file, its keys, the fixed path | author of recipes |
| 8 | Environment variables | each: read where, what it overrides, secret or not, old names refused | deployer |
| 9 | Theme stylesheet | a pointer only | deployer |
| 10 | What you see when your file is refused | each refusal text with its cause | deployer |
| 11 | Old and removed keys | the `renamed` and `removed` tables | deployer migrating |
| 12 | How the standard is kept true | the checks and tests | developer |
| 13 | Worked example files | one per use case, each started by a test | deployer |

## 4. Fields recorded for EVERY key

| Field | Source | Note |
|---|---|---|
| `key` (path, e.g. `branding.banner.ui_label`) | yaml | |
| `kind` (name, description, path, enum, number, flag, secret) | yaml | the "purpose / kind of name" she named; uses the seven kinds of D-0406 where it is a name |
| `meaning` | yaml | one sentence; the only place the sentence is written |
| `required` (yes / no / per use case) | yaml | |
| `type` and `allowed` | yaml | the checker reads them |
| `default` and `absent_behaviour` (default / fatal / silent default shown as "default, no message") | yaml | the survey found fatal (default_app_features), silent default (data_lookup, testing_mode) and a validator that says False where code says True (FACTS C(o)); the field forces one answer |
| `set_by` (deployer, author of recipes, developer, build image) | yaml | |
| `read_by` (module and function, NOT a line number) | yaml | line numbers move; a test checks the key literal appears in that module |
| `screen` (what the user sees, or "nothing") | yaml | |
| `options_per_use_case` (value, state: decided / open) | yaml | feeds the matrix |
| `check` (id, severity fatal / warning, refusal text) | yaml | added: tells the deployer what they will see |
| `path_base` (project_root, working directory, absolute) | yaml | added: `theme_css` is working-directory, locations are project_root |
| `env_override` (variable name or none) | yaml | added |
| `secret` (yes / no) | yaml | added: the token is never written in a file |
| `status` (active / reserved: no reader / removal decided D-xxxx / open) | yaml | added: `runtime.python_interpreter`, `locations.cache`, `irida.auth` are set and not read |
| `since` (format version) and `decision` (D-number) | yaml | added: the refusal can name the decision |
| `old_names` | yaml `renamed` | the refusal uses it |
| `example` (a value) | yaml | the generated template needs one |
| `doc_text` (long note, only when needed) | yaml | rare; the long story is in the hand-written page |
| `tests` (test file that proves the key) | optional | not recommended: drifts; the key-read test is the proof |

Removed from her list: nothing. Ones I would not add: line numbers (rot), the survey's per-file shipped values (derived; the matrix shows them).

## 5. Use cases and open choices

| Variant | What | Effort | Risk | Tests |
|---|---|---|---|---|
| A | Matrix only | small | medium: a deployer sees "allowed" but not a file that works | matrix generated |
| B | Worked example files only | medium | medium: a case with two options has no side-by-side view; examples drift | each example started by a test (today only 7 files are tested, `test_shipped_deployments.py:30`) |
| C | Both: the matrix is generated; each use case with a decided path has an example file under `config/deployment/` that a test starts; undecided cases have NO file | medium to large | low | start test per example; matrix test |

Recommendation: C. REASONED: the survey (FACTS E) found 19 use cases and examples for only 5 of them; IRIDA does not start (`irida.py:48-52`); a Galaxy file does not exist. An example that does not start must not be shipped: so a case with no working path appears in the matrix with state "not available" and no file.

Open choices: a key or value has `status: open` and `open_choice: <number 1 to 13>`. The generator prints it in a box "NOT DECIDED: options A, B, consequence" and omits it from the template file's live lines (it is a comment block). The start check does NOT accept an open key (refused as unknown) until a decision turns it `active`. This is how a deployer can never mistake an option for a rule. Consequence she must know: until each choice is decided, the rule "refuse the unknown key" blocks a deployer from trying it.

## 6. How the standard is kept true

| Check | Mechanism | Effort | Risk | Honest limit |
|---|---|---|---|---|
| Start check (D-0412) | `deployment_check.py` at bootloader init; refuses unknown, old, wrong type; fatal with a plain line naming key and new name | medium | medium: it will refuse files that run today (`app_features_override` with a typo, any extra top-level key; FACTS finding 2) | none |
| Shipped files pass | `test_shipped_deployments.py` extended: all files of `config/deployment/**` and `config/app_features/*` and `config/ui/sidebars/*` run through the check | small | low | today it only starts them |
| Key in the list is read | test: the module named in `read_by` contains the key literal | small | low | finds "read by nothing": python_interpreter, cache, irida.auth |
| Key read is in the list | (a) heuristic scan like `assets/scripts/inventory_config_keys.py` (it states itself it misses computed names); (b) one accessor `get(path)` that refuses an unlisted path, and a test that no module reads the deployment dict any other way | (a) small; (b) large: about 27 reads in `bootloader.py` and 13 `.get("branding"|"locations"|...)` outside it (READ by grep) | (a) false comfort; (b) medium | (a) cannot prove "every key"; (b) can |
| Old words | `assets/scripts/audit_old_words.py` (exists) fed the `renamed` and `removed` keys from the yaml | small | low | |
| Generated files equal | test runs the generator in compare mode | small | low | |
| Docs say what code does | the 18 text disagreements (FACTS C) vanish when the text is generated; a test cannot check hand-written prose | | | prose stays a risk |

Recommendation for "key read is in the list": (b) is the complete way and the only exact one. (a) is a half fix if sold as "every key". She decides; show both.

Format number: option 1, a required `format_version: 1` in every deployment and app features file (as `spec_version` in the recipe), refusal "this file is format 1, the app needs 2"; cost: one more key for every deployer, 15 shipped files change. Option 2, none: the allowed-key list plus the `renamed` table already refuses an old key with its new name; cost: a changed MEANING of the same key is not seen. The recipe says "No format 2" before first release (`recipe_spec.yaml:6-7`). Information, not my pick.

## 7. Order of work after she has seen the structure

Each step leaves a working app.

| Step | What | Tag | Parallel? |
|---|---|---|---|
| 0 | She answers "To decide first"; a scribe records | scribe | |
| 1 | Write `deployment_spec.yaml` (deployment + app features + environment) from the survey; no code reads it yet. Cleans the survey's 18 disagreements into explicit `status` and `check` fields | `sonnet/high` (judgement per key) | alone |
| 2 | Tests written first for the loader and the checker (fail on today's code); edge cases: empty file, unknown key, old key, wrong type, missing required, key with `status: open` | `sonnet/medium` | after 1 |
| 3 | `deployment_check.py` and the bootloader call; move the `renamed_keys` tables into the yaml and keep one raising function; shipped files fixed in the same pass | `sonnet/high` (cross-file refactor, 13 importers) | after 2 |
| 4 | D-0411 renames (banner `title` to `ui_label`, `subtitle` to `description`; remove `deployment_name` and app features `ui_title`), migration script, proof for `demo-vetinst` and `web-demo` | `sonnet/medium` | after 3; D-0407 pass |
| 5 | Remove keys decided dead: `runtime.python_interpreter` (D-0263) | `haiku/low` | with 4 |
| 6 | Sidebar and palettes sections; allowed panel ids from the registry | `sonnet/medium` | parallel with 4 (own files) |
| 7 | The generator (template, key tables, matrix, README table); compare test | `sonnet/high` | after 1; parallel with 3 and 4 (own script, own worktree) |
| 8 | The Quarto page, hand-written parts; delete the 18 stale statements | `sonnet/medium` | after 7 |
| 9 | Test "read_by" and the reader accessor (if she chooses b) | `sonnet/high` | after 3 |
| 10 | Use-case section, matrix, example files | `sonnet/medium` | only the decided cases; WAITS for the 13 choices for the rest |

Waits for the 13 choices: every `locations` key redesign (`recipes`, `data`, `user` lists with `access`), the keys of rows 12 to 14 (`users: several`, nothing writable), fonts (D-0400), `session_import` numbers (D-0283), the format of `app_features_override`. Steps 1 to 9 do not need them: the yaml holds them as `status: open`.

## To decide first (ranked; information for each, not my choice)

1. One yaml and one document (variant A), or two, or a core-only version (C)? A gives one place for env overrides; B means two documents for one deployer.
2. "Every key the code reads is in the list": one accessor (exact, large: about 40 read sites) or a heuristic scan (small, cannot prove it)?
3. A required format number in deployment and app features files: yes (15 files change) or no (a changed meaning of an old key is not seen)?
4. Where the written page lives: `docs/deployment/` for the deployer (my reading) or `.claude/design/` as the recipe text? A deployer is not a developer.
5. An open choice in the key list: refused as unknown until decided (safe, blocks trying) or accepted with a printed warning (lets a deployer try, but is a silent-ish choice)?
6. Does a worked example file exist only for a case that starts today? (IRIDA does not start.)

## Not verified

I did not run the tests, the app, or the generator ideas. The counts "about 27 / 13 read sites" come from two greps with different patterns and may miss reads through helper functions. `renamed_keys.py` 13 importers is a grep of file names containing the word, including tests and scripts. I did not read CLAUDE.md's rule files for the exact name of the library boundary check; the Tier statement comes from FACTS D. I did not check whether Quarto can include a generated file with `{{< include >}}` as this repo uses it (it appears in `docs/appendix/FAQ.qmd` by grep only). Model tags are my proposal from the table at `CLAUDE.md:26-33`.
