# Start here (2026-11-12): builders and the design review side by side

> **OUTDATED (2026-11-13, moved to `outdated/` in the cleanup of `.claude`):** the start file for the builders written before the design was agreed; the build plan is `.claude/design/home_stage2_mechanism_spec.md` section 5. Kept for history only; do not build on it.


> **ON HOLD (2026-11-12, Eve):** the prompts below were written before the design is agreed. The order of work is now design, agree, plan, build (`.claude/design/home_audit_reading_guide.md` section 0). **Do not use these prompts and do not start a work package until Eve releases it.** Independent of the design, and the first candidates to release: WP1 (#62), WP2 (#61), WP3a, WP8 (#66), WP10 (#68, needs her OK). WP4-WP6 (Exploration behaviour) wait for the behaviour design.

**Written for:** Eve, and the Claude sessions she starts tomorrow. **Prepared:** 2026-11-11 evening, while Eve rested.
Three tracks run at the same time. They must not step on each other: each has its own files (section 2).

| Track | Who | Does | Never touches |
|---|---|---|---|
| **D** design review | Eve + one Claude session | decides the audit design (`home_audit_review_agenda_2026-11-12.md`), edits design files, ADR-098/099, the UML | code, tests, recipes |
| **A** engine | one builder agent | WP1 (#62), WP2 (#61), then WP8 (#66); WP3a engine helper | HOME handlers, the export, frozen files |
| **B** exploration | one builder agent | WP4 (#56), WP5 (filter test suite), WP3a display, WP6 (help) | engine files of track A, frozen files, design files |

Waiting for Eve (nobody builds these): the ST22 anchor (#67), the score of samples without phenotype (#70), the rest of #69, the NA rule (WP3b),
the many-to-many check (WP10, edits `libs/transformer`), everything of audit mode.

## 1. First fifteen minutes (every builder)

1. `git status`, `git log --oneline -15`; read `CLAUDE.md` section 9 (no guessing) and `.claude/tasks/home_exploration_build_brief.md` (sections 0, 0b, 3).
2. Baseline: headless **1649 passed** (2026-11-12, after the seventh canary); browser gate **70 passed, 3 skipped** (not rerun since the canary was added; the browser tests do not read the QA group); canaries `app/tests/test_qa_canaries.py` 9 passed. Red baseline: stop and report.
3. Read your issues with all their comments, then **claim** them (issue protocol, brief section 0b) and fill your row of the status table.
4. Say in one message what you will do first and which files you will edit; then work.

## 2. Who owns which file (one owner per file)

| Files | Owner |
|---|---|
| `app/modules/t3_audit_engine.py`, a new `libs/utils/src/utils/filter_values.py`, the filter block of `libs/viz_factory/src/viz_factory/viz_factory.py`, `libs/viz_factory/src/viz_factory/plot_config_resolver.py`, the body of `extract_primary_keys` in `session_manager.py`, a new `app/modules/recipe_keys.py`, their tests | **A** |
| `app/handlers/home_theater.py`, `app/handlers/filter_and_audit_handlers.py` (only the places listed in WP4), a new `app/modules/preview_filters.py`, `app/modules/view_badge.py`, `app/src/help/home.md`, `docs/user_guide/system_transparency.qmd`, `docs/appendix/FAQ.qmd`, `app/tests/test_filters_behaviour.py` | **B** |
| `.claude/design/home_*`, ADR-098/099 in `architecture_decisions.md`, `docs/UML/**`, the reading guide | **D** |
| `1_test_data_ST22_dummy` recipe files | nobody until Eve answers #67/#70; canaries may be **added** (brief section 0b) |
| `CLAUDE.md` | Eve (do not edit; committed 2026-11-11 with her section 9) |

**Where two packages meet:**
- `t3_audit_engine.py`: only A edits it. B needs a counting helper for WP3a: A adds it right after WP1 (a pure function, signature agreed in an issue comment on #63); B calls it.
- `viz_factory.py`: A does WP1 (filter block) and then WP8 (the warning near line 250), in that order, never both at once.
- `filter_and_audit_handlers.py`: only B. If A needs a text change there, A comments on #56 and B does it.
- A diagram or ADR that a builder finds wrong: comment on the issue and tell D; do not edit.

## 3. Traps (verified or learned the hard way)

1. **No git worktrees for builders.** The libraries are installed editable with absolute paths (`.venv/.../__editable__.transformer*.pth` points to `.../SPARMVET_VIZ/libs/transformer/src`), so a worktree would test the original tree's code. Work in the same tree, on disjoint files.
2. **Git in a shared tree:** stage by file name, commit with a pathspec (`git commit -m ... -- <your files>`), never `git stash`, `git reset`, `git checkout -- <file>`, `git add -A` or `git add .` (they would take or destroy the other tracks' work). To mutation-check, edit and restore your own file by hand, never with stash.
3. **The browser gate (7.5 min) one at a time.** Before you start it comment `GATE RUNNING <session>` on your issue; after, `GATE DONE <numbers>`. Two gates at once are timing-flaky. Do not edit code while your gate runs.
4. **Eve's dev server** (`--reload`, port 8123) reloads on every edit: keep each edit atomic, a half-written file breaks her page.
5. **Scratch:** own folder `tmpAI/<your-name>/`; `tmp/` is for `@verify` evidence only.
6. **A recipe change needs its picture looked at**, not only a green test (the review found that the tests pass with wrong figures).
7. **The browser tests are timing-sensitive on this machine; this is established, not a guess** (controlled experiment of 2026-11-11, `.claude/design/home_evidence/home_audit_forensics_2026-11-12.md` section 5, issue #72). The old code (before the day's changes) failed as often
   as the new code, and only under CPU load (1 of 3 runs each; 0 of 3 without load); the failures are always in different tests; no random seed or random order is involved. Known races: the label test reads the disk right after `_wait_shiny`;
   a recipe selection right after `goto` can be lost (the page then shows the default recipe). Rule: a red gate is a **question**: rerun the failing test alone, then the file once; if it fails again in the same place it is real (revert your package, S2).
   Never close an issue on a gate you have seen fail without saying so in the DONE comment. `TestRecipeSwitchPlotRender` is the other known timing-flaky test.

## 4. Paste-ready prompts

**Track A (engine):**
> Read `.claude/tasks/next_session_start.md` and `.claude/tasks/home_exploration_build_brief.md`, then work as track A: WP1 (#62), WP2 (#61), then WP8 (#66). Follow the issue protocol (section 0b): read each issue with its comments, claim it, comment at every commit, tick boxes only for what you verified, close with a DONE comment. Frozen files and the compatibility contract (S3, S5) bind you; ask Eve when anything is unclear.

**Track B (exploration):**
> Read `.claude/tasks/next_session_start.md` and `.claude/tasks/home_exploration_build_brief.md`, then work as track B: WP4 (#56), WP5 with the QA canaries, WP3a display after track A's helper exists, WP6 last. Same protocol and constraints; do not edit engine files, design files or the UML.

**Track D (design review, with Eve):**
> Read `.claude/design/home_audit_review_agenda_2026-11-12.md`, then `.claude/design/home_evidence/home_gating_and_test_configs_2026-11-12.md` (the decision paper, section 8 = the questions), `home_audit_reading_guide.md`, `.claude/design/home_evidence/home_audit_forensics_2026-11-12.md` (section 0 and 4 first) and `.claude/design/home_evidence/home_audit_architect_review_2026-11-12.md` (section 0 first). Run the review with Eve in the order of the agenda, write her decisions into the design files at once, and change nothing in code.

**Open question that may change WP4's scope (do not guess; Eve answers it in the review):** the interim of the header strip for the two features without the sandbox flag (forensics 3.7, F8; brief section 5, question 3). Until she answers, track B builds WP4 as briefed: the strip stays as built, nothing about My view, Compare or "Plot to show" is touched. (An earlier idea of adding a view-policy module to WP4 is withdrawn.)

## 5. What every builder hands back

For each package: the issue closed or updated with a DONE comment (what changed, evidence with counts, mutation check, pictures looked at, what was not done), the status-table row, the `tasks.md` entry, a handoff line, `@deps` blocks of touched files and `python assets/scripts/build_dep_graph.py`, and one line in `.claude/logs/audit_YYYY-MM-DD.md`.
