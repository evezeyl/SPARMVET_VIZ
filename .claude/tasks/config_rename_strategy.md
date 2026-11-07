# Strategy: the configuration rename (ADR-091, issue evezeyl/SPARMVET_VIZ#27)

**Goal:** rename persona, manifest and the old meanings of recipe everywhere, in a way that keeps the app working after every commit, so that when something breaks we can find the commit that did it.
**Status:** PLAN, written 2026-11-07. Starts only after Eve has approved the mapping table (CONFIG-MAPPING-1).

## Rules for the whole work

1. **Working branch `rename/config-vocabulary`** off `dev`. It is merged into `dev` (merge commit, no squash, so the chunks stay visible) only when the old-words audit is clean and both test suites pass. This keeps ADR-091's rule: no hybrid state reaches a shared branch. Other fixes go on `dev` meanwhile and are merged into the branch daily (small, so conflicts stay small).
2. **Each commit is one kind of change and leaves the headless suite green** (about 50 s, 1215 tests today). The browser suite (about 3 min, 37 tests) runs at the end of every phase.
3. **Pure moves are separate from content edits.** `git mv` alone first (100 % similarity, so `git log --follow` and rename detection work), edits in the next commit.
4. **Renames are separate from behaviour changes.** A rename commit changes names only; a behaviour commit (precedence, `~` and `${VAR}` expansion, startup errors, deleted flags) changes behaviour only. Then a failing test names its cause.
5. **The rename is done by one script with a category switch** (`--only <category>`), dry run first, the diff saved in `tmpAI/`. One category = one commit. The script and its mapping table are committed so any step can be replayed.
6. **The old-words audit (a script, committed) prints a count per word and category.** The count only goes down, never up. At the end it is zero outside the marked exclusions. It can also scan untracked and git-ignored files (`--include-untracked`, `--include-ignored`), because the working files used for testing are not in git and would otherwise keep the old words.
7. **Tag each phase** (`rename-phase-0` ... ). `git bisect run` with the headless command finds the first bad commit between two tags.
8. **Tests are renamed in the same commit as the code they test.** A test that cannot fail is not a test: for each behaviour change, break the new code once and see the test fail (project rule, `rules_verification_testing.md` section 9).
9. **Commit messages:** `refactor(<area>): ...` for renames, `feat`/`fix` for behaviour, footer `Refs: evezeyl/SPARMVET_VIZ#27`, co-author line as usual.
10. **One session per phase**, with a handoff note in `.claude/logs/handoffs/handoff_active.md` at the end. The work is too long for one context.

## Phases

| Phase | Content | Commits | Checks | Model / effort |
|---|---|---|---|---|
| **0 Safety net** | Tag `pre-config-rename`. Record the baseline (suite counts, audit counts). Write the old-words audit and the inventory script (read-only). Add the missing tests first, written against the OLD names so they pass now and are renamed with the rest: launch with each variable, a session save and restore round trip, a gallery bundle load, an export bundle with its hash keys, the retest manifests. | few, no behaviour change | all green; audit counts recorded | inventory and audit scripts `[sonnet/high]`; characterization tests `[sonnet/medium]` |
| **1 Review gate** | Inventory and mapping table written to `.claude/logs/`, reviewed by Eve. Open points of ADR-091 decided. | none (docs only) | Eve's approval | `[opus/high]` for the mapping rules that need judgement (`TransformationRecipe`, `t3_recipe`, `join_manifests`) |
| **2 Dead keys** | Delete `logic_access`, `persona_name`, `data_import_panel_visible` and their readers. | 1 | headless | `[haiku/low]` |
| **3 Python identifiers, persona** | Classes, functions, variables, module names containing persona (code only, no file format). `git mv` commit, then content commit. Tests with them. | 2 to 4 | headless | script run `[haiku/low]`; fixing what breaks `[sonnet/high]` |
| **4 App features: files and keys** | `config/ui/templates/` to `config/app_features/`, `persona_*` keys, `default_persona` to `default_app_features`, `SPARMVET_PERSONA` to `SPARMVET_APP_FEATURES` with the old-name startup error. | 3 | headless + browser | `[sonnet/high]` |
| **5 Deployment: files and keys** | `SPARMVET_PROFILE` to `SPARMVET_DEPLOYMENT`, file names, the resolution chain files (`deployment.yaml`), old-name error. | 2 | headless + browser | `[sonnet/high]` |
| **6 Recipe: identifiers** | `manifest` in Python identifiers, modules (`manifest_navigator.py`, `manifest_validator.py`), classes. Moves then edits. | 3 to 5 | headless | script `[haiku/low]`; review of the diff `[sonnet/medium]` |
| **7 Recipe: formats** | YAML keys (`join_manifests`, `manifest_selector`, `locations.manifests`, `default_manifest`), folders (`config/manifests/`, `assets/template_manifests/`), `manifest_sha256` in sessions and exports, gallery bundle files, the migration script and the old-file, old-session, old-ghost errors. Check first whether any cache key or hash input contains the old names (it may rebuild caches once; the determinism tests must still pass). | 4 to 6 | headless + browser + a real saved session migrated by hand | `[sonnet/high]`, hard cases `[opus/high]` |
| **8 Free the word "recipe"** | `recipe:` to `steps:`, T3 recipe to audit steps (`t3_recipe_by_plot`, `t3_recipe_engine.py`, ghost format), filter builder labels, `TransformationRecipe` as decided. | 3 to 5 | headless + browser | `[sonnet/high]` |
| **9 Behaviour** | Precedence per choice, `default_data_analysis_recipe` takes effect, `fixed_manifest` removed with its error, `~` and `${VAR}` expansion with the unset-variable error, the selector wording. Each with tests that were seen to fail first. | 4 to 6 | headless + browser | `[sonnet/high]` |
| **10 Documentation** | Propagate to every doc: deployment guide, `connector.qmd`, `ui_persona.qmd` (renamed), user guide, FAQ, troubleshooting, appendix, READMEs, rules, knowledge, `CLAUDE.md` tables, memory notes, test plan, retest procedure and launch commands; vocabulary note in the ADR log; DOC-RECHECK-2 items; `docs/_freeze/` re-rendered. A docs check (old words in live docs) must be clean. | several, one per folder | docs check; links render | `[sonnet/medium]` |
| **11 Retest and fix** | Full headless and browser run; the retest procedure re-written with the new names and run again (by Eve for the parts that need eyes); bugs fixed as separate `fix:` commits, each with a test. Then audit clean, merge into `dev`, tag. | as needed | everything | `[sonnet/high]`; `git bisect` puzzles `[opus/high]` |
| **12 Whole-repo screening (last, before the merge)** | Screen everything, not only tracked code: tracked files and paths; **untracked and git-ignored working files** (`tmp/`, `tmpAI/`, `issue-drafts/`, scratch scripts, local notes, test data and retest files, generated parquet and session folders, `docs/_freeze/`, rendered docs); hidden and tool folders (`.claude/` including logs and handoffs, `.vscode/`, `.github/` and CI workflows, pre-commit config, `.gitignore`, `.aiignore`, `tree.txt`, `pyproject.toml` files, shell and launch scripts, notebooks, Dockerfiles and compose files, `config/deployment/templates/`); user-level places that name the old variables (`~/.sparmvet/`, shell history aliases, IDE launch configurations, memory notes under `~/.claude/`, the My-mentoring notes that mention SPARMVET commands). Search for the old words in file names, directory names, file contents, YAML keys, environment variable names, UI labels and saved data (stored sessions, ghosts, exports, gallery index, Parquet metadata). Every hit is renamed, marked as history, or listed with a reason in a short report. The retest files and the issue drafts left over are updated or deleted. | 1 to 3 | the old-words audit run with `--include-ignored` and `--include-untracked` returns only the listed exclusions; a fresh clone launches with the new variables | `[sonnet/high]` |

## What makes a break easy to find

- Every phase ends green and tagged; between two tags `git bisect run` with the headless command names the exact commit.
- Because renames and behaviour are never mixed, a failing test after a rename commit means a missed reference (the audit count shows where); after a behaviour commit it means the new behaviour.
- The characterization tests of phase 0 fail loudly if a rename breaks a real path (launch, session, gallery, export).

## Tests and fixtures that must be adapted (known)

`app/tests/conftest.py` and the browser tests (launch variable `SPARMVET_PERSONA`), `test_retest_manifests.py` and the retest folder `config/manifests/retest/`, `config/deployment/local/retest_profile.yaml`, all tests that read `config/manifests/...`, the persona validator tests, `session_manager` tests (ghost and session formats), gallery tests (`recipe_manifest.yaml`), export provenance tests (`manifest_sha256`), `libs/*/tests` that name manifests, and the audit scripts and reports named `audit_manifest_*`.

## Model and effort

The project table (`CLAUDE.md` section 2) puts mechanical edits and scripting at `[haiku/low]`, multi-file implementation at `[sonnet/medium]` to `[sonnet/high]`, and architecture at `[opus/high]`. Applied here: the thinking is in phase 1 and in the hard cases; running an approved script is cheap; fixing what the tests then show needs `[sonnet/high]`. Switching the model is done by Eve with `/model` between phases; a new session per phase keeps the context small.

## Risks

- **Missed references in strings** (messages, f-strings, YAML keys built from text): the audit greps text, not only identifiers.
- **Stored formats**: old sessions and ghosts. Mitigated by the migration script and a hand check on one real session.
- **Cache keys that include old names**: caches rebuild once; the determinism tests must stay green (ADR-089, ADR-090).
- **Size of the diff**: reviewed per commit, never as one block.

## Baseline (phase 0, recorded 2026-11-07 on `dev` at tag `pre-config-rename`)

| Measure | Value |
|---|---|
| Headless suite | 1213 passed (37 s) |
| Browser suite (qa) | 34 passed, 3 skipped (200 s) |
| Old-words audit, tracked files (1576 scanned) | persona 9 in paths / 1730 in content; manifest 234 / 4560; recipe 76 / 1424; profile 6 / 674 |
| Old-words audit, with untracked and ignored files (23233 scanned) | persona 15 / 2566; manifest 337 / 6978; recipe 85 / 2207; profile 26 / 1314 |

The word "profile" is counted to be reviewed by meaning: only the deployment profile is retired; other uses (for example profiling, user profile) stay and go on the exclusion list in the mapping table.
Run the audit: `./.venv/bin/python assets/scripts/audit_old_words.py [--include-untracked] [--include-ignored] [--list] [--check]`. Test: `app/tests/test_audit_old_words.py`.
