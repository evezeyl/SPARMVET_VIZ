# Handoff — Active State (2026-05-10 continued session)

**Branch:** dev  
**Working tree:** clean (all changes committed)  
**Status:** Session focus: Audit-driven quick wins. Completed 3 library/dependency tasks.

## Session Accomplishments (2026-05-10 afternoon)

### Completed Tasks

1. **LIB-TESTS-BLUEPRINT-1** ✅ `[sonnet/medium]`  
   188 pytest failures → **0 failures (194/194 tests passing)**  
   Root cause: Test file was importing `AVAILABLE_WRANGLING_ACTIONS` (function dict) instead of `ACTION_SCHEMAS` (schema dict) from transformer.actions.base  
   Fix: Changed imports and `register()` call in `libs/blueprint_arch/tests/test_schema_registry.py`  
   Result: All 58 action catalog tests + 36 component catalog tests + semantic rule tests now pass
   
2. **PKG-PLOTNINE-PATCH-1** ✅ `[haiku/low]`  
   Upgraded plotnine 0.15.3 → 0.15.4 per ADR-036 (Plotnine Parity Mandate)  
   Pinned version in pyproject.toml: `plotnine>=0.15.4,<0.16.0`  
   Re-ran parity audit: 222 plotnine symbols, 168 registered (75% coverage)  
   New components identified (geom_bin2d, stat_bin2d, stat_pointdensity) — registration deferred to BP-ACTION-PARITY-1
   
3. **PKG-IMPORTLIB-MAJOR-1** ✅ `[sonnet/low]`  
   Investigated importlib_metadata 9.0.0 upgrade (MAJOR version bump)  
   Found breaking change: opentelemetry-api 1.41.1 (pulled by shiny) requires importlib-metadata<8.8.0  
   Solution: Pinned importlib_metadata to >=6.0,<9.0.0 in pyproject.toml  
   Verified: `pip check` reports no broken requirements

**Next session:** Remaining audit-driven items in "Do Now":
  - **DOC-GAP-1** `[sonnet/medium]` — Expand `docs/workflows/ui_persona.qmd` with 4 missing items (Eight Personas, ADR-076 agent flags, ADR-077 cascade table, panel type table)
  - **DOC-GAP-4** `[haiku/low]` — Triage 8 orphaned `.qmd` files not in `_quarto.yml`

---

## What this session accomplished

This session was a dedicated audit triage session. Two agents ran:

1. **This agent (main session):** Ran Routines §10–12 (library tests, package deps, parity coverage), defined and ran Routines §17–19 (agent-based: semantic doc sync, ADR compliance, three-source persona consistency). Filed all findings as tasks. Updated registry.

2. **Parallel agent (documentation audit):** Ran a 4-part documentation audit (READMEs, docstrings, propagation, docs_tree). Fixed DOC-DRIFT-1 (6 files) and DOC-DRIFT-EMOJI (9 emoji violations) in-session. Filed DOC-GAP-1 through DOC-GAP-4 as tasks.

**All 19 audit routines now have a first-run result.** All audit log files start with `Status: PROCESSED`. The audit infrastructure is fully operational.

---

## Open tasks filed this session (priority order)

### Highest priority — ADR violation

- **ADR-078-ACTIONS-1** `[sonnet/medium]` — Retrofit `SPARMVET_DiagnosticError` into 5 transformer actions that silently `return lf` on invalid input instead of raising the required error type. Files:
  - `libs/transformer/src/transformer/actions/cleaning/expressions.py:40` — `action_regex_extract`
  - `libs/transformer/src/transformer/actions/cleaning/expressions.py:187` — `action_mutate`
  - `libs/transformer/src/transformer/actions/cleaning/analytical.py:29` — `action_window_agg`
  - `libs/transformer/src/transformer/actions/cleaning/analytical.py:64` — `action_shift`
  - `libs/transformer/src/transformer/actions/cleaning/advanced.py:27` — `action_split_and_explode`
  - After those 5, scan rest of `analytical.py` and `advanced.py` for the same pattern.

### Documentation gaps (content creation)

- **DOC-GAP-5** `[haiku/low]` — Fix ExcelHandler class claim in `libs/ingestion/README.md` (no class exists, only `main()` CLI) and "Comparison Theater" stale terminology in `libs/transformer/README.md`. Both READMEs need rewriting to match actual implementation.
- **DOC-GAP-1** `[sonnet/medium]` — Expand `docs/workflows/ui_persona.qmd`: 8 personas, ADR-076 blueprint agent flag, ADR-077 cascade table, ADR-073 panel type table.
- **DOC-GAP-2** `[haiku/low]` — Add demo-vetinst and web-demo rows to `persona_traceability_matrix.md`.
- **DOC-GAP-3** `[haiku/low]` — Add ADR-074 lineage API note to `docs/deployment/deployment_guide.qmd`.
- **DOC-GAP-4** `[haiku/low]` — Triage 8 orphaned `.qmd` files not in `_quarto.yml`.

### Library tests & infrastructure

- **LIB-TESTS-BLUEPRINT-1** `[sonnet/medium]` — 188 pytest failures in `blueprint_arch/tests/test_schema_registry.py`. Root cause: `@register_plot_component` decorators missing `allow_extra_params` / `wraps` ui_schema fields (ADR-075). Fix: add fields to viz_factory component registrations.
- **LIB-TESTS-VIZ-TIMEOUT-1** `[haiku/low]` — Increase timeout for viz_factory integrity suite in `audit_library_tests.py` (currently times out at 120s; suite renders 193+ components).
- **PKG-PLOTNINE-PATCH-1** `[haiku/low]` — Upgrade plotnine 0.15.3 → 0.15.4 (parity mandate); check changelog; re-run parity audit.
- **PKG-IMPORTLIB-MAJOR-1** `[sonnet/low]` — Investigate `importlib_metadata` MAJOR update (8.7.1 → 9.0.0); determine if safe to allow.

---

## Known open questions / things to verify next session

### Transformer integrity suite 60/62 internal failures

The transformer integrity suite exits 0 (audit script sees PASS) but internally reports 60/62 action failures. Root cause: ADR-078 — actions now raise `SPARMVET_DiagnosticError` when run without proper test TSV data, but the integrity suite was written pre-ADR-078 and doesn't provide the required data context. The suite's exit code doesn't reflect these internal failures.

**This needs a decision:** is the fix (a) update the integrity suite to provide test data for each action so ADR-078 diagnostic errors don't fire, or (b) reclassify these as expected failures and document them? Not filed as a task yet — needs discussion first. This is connected to ADR-078-ACTIONS-1: fixing the 5 silent-passthrough actions is independent, but the broader suite/ADR-078 relationship needs resolution.

### Routine §9 (Documentation & README Sync) still `[ ] Planned`

Routine §9 is the *script-based* doc sync (checks paths, Violet Law references, `@deps` doc links). It is distinct from Routine §17 (agent-based semantic doc sync, which ran this session). The script for §9 (`scripts/audit_docs_sync.py`) has not been written yet. Status matrix correctly shows `[ ] Planned`. No urgency — Routine §17 covers the semantic layer; §9 adds structural/path checking. File a task when ready to implement.

### viz_factory README component count drift (175 → 195)

Routine §17 flagged viz_factory README claiming 175 components vs 195 actual. Marked informational — count drifts naturally with new `@register_plot_component` additions (DECO-2 wave added 20). No task filed; update at next viz_factory sprint.

---

## Audit infrastructure state (for reference)

All 19 routines registered and run at least once:
- §1–16: script-based, most scheduled weekly/monthly. All PASS on first run except §10 (FAIL) and §11 (FAIL/WARNING).
- §17 Semantic doc sync: FIRST RUN ⚠️ — 3 STALE items found, all converted to tasks (DOC-GAP-5 + viz_factory count informational).
- §18 ADR compliance: FIRST RUN ❌ — ADR-078 VIOLATION in 5 actions → ADR-078-ACTIONS-1.
- §19 Three-source persona consistency: FIRST RUN ✅ — all 8 personas clean.

Exclusions file: `.claude/workflows/audit_exclusions.yaml` — added `theme_legend_position` and `theme_publication` as SPARMVET-specific custom components (not plotnine exports). These prevented false-positive stale component alerts in Routine §12.

---

## Files modified this session

- `.claude/tasks/tasks.md` — added: `Audit Fixes — Documentation (DOC-GAP-5)`, `Audit Fixes — Library Tests & Dependencies (LIB-TESTS-BLUEPRINT-1, LIB-TESTS-VIZ-TIMEOUT-1, PKG-PLOTNINE-PATCH-1, PKG-IMPORTLIB-MAJOR-1)`, `Audit Fixes — ADR Compliance (ADR-078-ACTIONS-1)`
- `.claude/workflows/audit_routine_registry.md` — updated §17, §18, §19 status from `[ ] Planned` to `[x] Active` with first-run results in both status matrix and routine definitions
- `.claude/workflows/audit_exclusions.yaml` — added `theme_legend_position` and `theme_publication` to `custom_viz_components`
- `.claude/logs/audits/audit_doc_sync_2026-05-09.md` — created (Routine §17)
- `.claude/logs/audits/audit_adr_compliance_2026-05-09.md` — created (Routine §18)
- `.claude/logs/audits/audit_persona_consistency_2026-05-09.md` — created (Routine §19)
- `.claude/logs/audits/audit_library_tests_2026-05-09.md` — created (Routine §10)
- `.claude/logs/audits/audit_package_deps_2026-05-09.md` — created (Routine §11)
- `.claude/logs/audits/audit_parity_coverage_2026-05-09.md` — created (Routine §12)

---

*Appended 2026-05-09 — audit sweep session.*

---

## Session 2026-05-22 — Legacy removals + TEST_LAB scaffold

### Completed this session

**TL-UI-SCAFFOLD-1** — Manifest Scaffolding panel fully wired in `app/handlers/test_lab_handlers.py`. Replaced 3-line stub with full reactive panel: multi-file upload, project ID, join key, optional metadata TSV, reconciliation bake-in controls (conditional on `_recon_results()`), run gate, ZIP download. Stateless tool principle maintained.

**LEGACY-FLAT-WRANGLING-1** — Flat `wrangling: []` lists now raise `ManifestError` in `_resolve_tier()`. Two manifests migrated. 8 tests added in `libs/transformer/tests/test_data_wrangler.py`. Docs swept: `rules_data_engine.md`, `Standards_yaml.qmd`, `transformer/README.md`, `architecture_decisions.md ADR-024`.

**LEGACY-TYPE-ALIASES-1** — Previously completed (carried over from prior session).

### Open legacy tasks remaining
- `LEGACY-AUDIT-FLAG-1`: `audit_report_enabled` flag removal (marked done earlier this session — verify tasks.md)
- Next candidate: check tasks.md for any remaining `[ ]` legacy items

### Files modified this session
- `app/handlers/test_lab_handlers.py` — scaffold panel implementation
- `libs/transformer/src/transformer/data_wrangler.py` — flat list rejection
- `libs/transformer/tests/test_data_wrangler.py` — NEW (8 tests)
- `config/manifests/pipelines/demo_abromics.yaml` — wrangling migration
- `config/manifests/pipelines/1_Abromics_general_pipeline.yaml` — wrangling migration
- `.claude/rules/rules_data_engine.md §3` — enforcement mandate
- `docs/appendix/Standards_yaml.qmd` — REMOVED tombstone
- `libs/transformer/README.md` — flat-list rejection note
- `.claude/knowledge/architecture_decisions.md ADR-024` — Phase 34 enforcement note
- `.claude/knowledge/project_conventions.md` — scaffolder.py added to registry
- `.claude/tasks/tasks.md` — TL-UI-SCAFFOLD-1 and LEGACY-FLAT-WRANGLING-1 marked `[x]`

*Appended 2026-05-22 — legacy removals + TEST_LAB scaffold session.*

## Handoff 2026-11-05 (end of day, testing and fixing session on dev)

State: everything is committed and pushed on `dev` (last code commit: top_n_other, then the test-manifest fix). Untracked and left on purpose: `.claude/logs/audits/audit_manifest_*_2026-11-04.md` (need `Status: PROCESSED`, Eve writes that commit) and `docs/demo/` (Eve's).

Waiting for Eve's retest and close: #18 (rename a header in a test data file, open Home: "Data Assembly Failed" banner; she did this), #21 (MLST_counts_bar shows real sequence types), #23 (action only, not used in a manifest yet).

Next step (planned for tomorrow), demo plot "variants by year and production type" on the dummy project `1_test_data_ST22_dummy` (option A of issue #19, a dodged bubble matrix; the true scatter-pie is deferred):
1. Add a `variant` column (ST + serotype, format `ST95-O25:H4`) with a mutate step. MLST gives `sequence_type`, VirulenceFinder gives `serotype`.
2. New collection with one row per sample: year, source (Broiler / Layer / Parent), grouped variant via `top_n_other` (with `count_distinct: sample_id`, because a sample has several virulence rows).
3. Count isolates per year, variant and source (`count_by_group` or `summarize`), size classes like the R legend.
4. Plot file and `analysis_groups` entry; the render test (`app/tests/test_render_every_plot.py`) then covers it automatically. Tier 2 stored data (#10) is not built, so aggregate in the assembly or the plot.
Dummy data facts: 42 samples, 40 distinct variants (so the top-N step is needed), 13 serotypes, years 2022 to 2024.

Open issues: #10 (Tier 2 parquet), #15 (Plot Style, deferred), #19, #20 (deferred), #22 (replace_values deprecation). Drafts left in `issue-drafts/`: 003 (year axis continuous in My view, HOM-44), 004 (cache-busting script tags), blank page without manifests, broken manifest stops the app, import writes to the default data path, export records what was used, reshuffle jitter. R reference code: github.com/NorwegianVeterinaryInstitute/2025_PAWH_APEC1 (commit f04a429).

## Handoff 2026-11-09 (end of session, reproducible export & import initiative — ADR-097)

State: everything is **committed on `dev`** (not pushed — Eve did not ask for a push). Working tree clean at session end. Last commit: `0821ef6 feat(export): sensitive-data warning + import with hash verification (#46, #48)`.

This session (continued across a context-compaction boundary) finished the reproducible-export/import initiative tracked by **#44**. Issues #39, #45, #46, #47, #48 are all implemented, tested, and commented on GitHub with what shipped and which commit — **left open on purpose**: this repo's workflow (see `project_issue_workflow` memory) closes issues at the dev→main PR, not per-commit on dev. #44 itself got a status-update comment listing what's done vs. still open (#49, #50, #52 remain).

### What ADR-097 settled (read this first if picking the thread back up)
Two export "modes" that are complements, not alternatives: the **standard bundle** (always built — plots, Tier 1/Tier 2 data, `t3_steps.yaml`, `report.qmd`, never the recipe or raw data) plus an **opt-in "Also include a reproducibility/reimport bundle" checkbox** that adds the frozen recipe (T3 baked in as real actions) and the actual data files. `effective_run.yaml` is written **unconditionally, bundle root, byte-identical either way** — the whole point is that two separately-exported bundles can be diffed field by field to prove they're the same analysis, or see exactly where they diverge (recipe/data/T3-steps changed vs. only `engine_fingerprint`/`git_commit` changed — the latter means "software changed, not your analysis"). This design went through one real correction mid-session after Eve's review (see #45's comment / commit `d0d4f37`) — the first pass had kept Mode 1's full recipe copy and a non-shared `effective_run.yaml`, both wrong.

### Session commits, in order
```
fc14bcf feat(viz_factory): random_state as an aesthetic_override key (REPRO-SEED-1)
e6abc78 feat(home): automatic seed bookkeeping for unpinned random_state (REPRO-SEED-2)
c2b7061 feat(export): fourth provenance hash leg + environment-aware engine fingerprint (REPRO-PROV-1)
4bf0027 feat(session): T3-steps restore integrity check + a second missing check found (REPRO-RESTORE-HASH-1)
6515d2a feat(blueprint_arch): T3-to-recipe-action translator (REPRO-TRANSLATOR-1)
682fdfe feat(export): opt-in reproducibility/reimport bundle (REPRO-EXPORT-MODES-1)
d0d4f37 fix(export): Mode 1 never carries the recipe, effective_run.yaml is shared and unconditional
0821ef6 feat(export): sensitive-data warning + import with hash verification (#46, #48)
```

### New/changed files
- `app/modules/bundle_importer.py` — **NEW**. Import + four-leg hash verification, pure/headless (Two-Category Law). File-based only (ADR-093): writes a new recipe + `SessionManager` session ghost, never touches live app state.
- `app/tests/test_bundle_importer.py` — **NEW**, 16 headless tests.
- `app/handlers/export_handlers.py` — Import UI/wiring (Export panel), the `effective_run.yaml` write, the sensitive-data notification, Mode 2 add-on block.
- `app/tests/test_export_download.py` — `test_import_a_bundle_reports_the_four_legs` (real browser round-trip; cleans up the real files Import writes outside `tmp_path` in a `finally` block).
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py` — **NEW** (earlier this session), T3→recipe-action translation, `build_mode2_recipe()`.
- `docs/user_guide/understanding_your_export.qmd`, `docs/user_guide/reproducible_plots.qmd` — rewritten; both had gone stale describing the pre-#45 single-bundle design, not just missing the new sensitive-data section.
- `docs/UML/app.mdj` — `EXP-MODES` diagram (HOME package) extended with the Import & Verify round trip, built via the native StarUML bridge API (never the Mermaid shortcut — standing rule, see `feedback_staruml_native_only` memory). `audit_uml_model.py` passes clean.
- `.claude/knowledge/architecture_decisions.md` ADR-097 — "Files touched" updated to the real list.
- `.claude/rules/rules_app_structure.md` — `bundle_importer.py` added to the directory map + ownership matrix.
- `.claude/tasks/tasks.md` — all REPRO-* tasks through REPRO-IMPORT-1 marked `[x]` with detailed completion notes.
- `.claude/logs/audits/audit_cross_lib_2026-11-08.md`, `audit_deps_2026-11-08.md` — restored a dropped `Status: PROCESSED` line found at session start (pre-existing, not this session's doing, but append-only rule applies — fixed rather than committed broken).

### Still open, not started this session
- **#49** (reshuffle control) — deferred by design, needs `random_state` as a real UI button, not just the YAML/auto-bookkeeping that already exists.
- **#50** (session labels / multi-dataset distinction) — independent of the chain above, Session Management's own backlog.
- **#52** (found during #47) — no registered wrangling action for `ne`, strict `gt`/`lt`, or `not_in`; the translator reports affected plots via `t3_translation_skipped` rather than approximating. Someone needs to register these actions in `libs/transformer/`.

### Next step, if there is one
Nothing is mid-flight. The natural next pieces (#49, #50, #52) are each independent and small — pick whichever matters most next session. No uncommitted work, no pending `@verify`, no open StarUML edit in progress (project saved).

## Handoff 2026-11-09 (same day, continuation — #52/#50/#49 all done)

State: everything **committed on `dev`** (not pushed), working tree clean. The three items
listed as "next" above are now all done, closing out #44 entirely (7/7 sub-issues).

```
0db0b49 feat(transformer): register filter_ne/filter_gt/filter_lt/not_in actions (#52)
c8c62dc feat(session): editable per-session labels, fixes label-before-first-Apply bug (#50)
dc49a7e feat(home): reshuffle-and-pin control for an unpinned plot seed (#49)
```

Each closed with a GitHub issue comment (not closed — this repo's workflow closes issues at
the dev→main PR). #44 (tracking) got a final summary comment too.

**#52** — `filter_ne`/`filter_gt`/`filter_lt` (`libs/transformer/.../cleaning/core.py`) and
`not_in` (`cleaning/analytical.py`), following the existing action pattern exactly.
`t3_translator.py`'s `_TRANSLATABLE_OPS` now covers all 8 T3 filter ops.

**#50** — found a real bug while building the UI: `set_session_label`/`get_session_label`
only ever touched the most-recent T3 ghost, so a brand-new session (before any Apply) could
not be labelled at all. Canonical storage moved to `assembly.json` (exists from first
assembly; `write_assembly_ghost(label=None)` preserves an existing label across a
recipe/data-change rewrite). UI: `ui.input_text(..., update_on="blur")` in the session card,
no separate Save button, guarded by comparing against the stored value (R3) so an unrelated
session action elsewhere can't spuriously re-fire the save.

**#49** — "🔀 Reshuffle arrangement" button next to a plot with an unpinned jitter layer;
clicking draws and pins a new seed into that plot's T3 `aesthetic_override.random_state`
(the shape #39/REPRO-SEED-1 already built — no new render-side plumbing needed). New
`recipe_pins_random_state()` in `plot_config_resolver.py` decides visibility. Found and fixed
three real bugs via the tests: an id collision between the `output_ui` wrapper and the button
inside it (both named `plot_reshuffle_{p_id}`); a copy-pasted `reactive.isolate()` that
silently stopped the button from ever reacting to its own pin; and a shared-module-scoped-page
state leak (the new tests left the browser on the "Curiosity" group tab, breaking
`TestViewBadges` later in the same file) — fixed by following this file's own documented
convention of restoring navigation state in a `finally` block.

### Files changed this continuation
- `libs/transformer/src/transformer/actions/cleaning/{core,analytical}.py` — 4 new actions
- `libs/transformer/tests/test_filter_actions.py` — NEW
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py` + its tests — extended op coverage
- `app/modules/session_manager.py`, `app/handlers/session_handlers.py` — label storage + UI
- `app/tests/test_session_manager.py`, `app/tests/test_shiny_smoke.py` — new tests throughout
- `app/handlers/home_theater.py` — reshuffle control
- `libs/viz_factory/src/viz_factory/plot_config_resolver.py` + its tests — `recipe_pins_random_state`
- `docs/user_guide/reproducible_plots.qmd`, `docs/foundations/reproducibility_same_input_same_output.qmd`,
  `docs/user_guide/understanding_your_export.qmd` — corrected/updated throughout both sessions
- `.claude/tasks/tasks.md`, `.claude/knowledge/architecture_decisions.md` — all REPRO-* and
  ACTIONS-FILTER-GAPS-1 entries marked done with implementation notes
- `.claude/rules/rules_agent_role_bioscientist.md §8` — action list updated

### Next step
Nothing is mid-flight and #44's whole initiative is now complete. Whatever Eve picks next is
unrelated to this thread — there is no natural continuation queued.

## Handoff 2026-11-09 (same day, final pass — thorough re-verification, issues closed, pushed)

Eve asked explicitly for a thorough re-verification (UML, docs, audits, tests) before closing
the issues and pushing — this correction supersedes the "not closing — closes at the dev→main
PR" assumption written earlier in this file; that was my own inferred default, not her
instruction, and she overrode it directly here.

**UML** (native StarUML bridge, never Mermaid): found and fixed two stale `SEQ-EXPORT`
messages that described pre-ADR-097-correction behaviour (an unconditional recipe-copy step
that no longer exists, and a provenance message not mentioning `effective_run.yaml`). Updated
three `UI-HOME` wireframe panel labels to mention this session's additions (Import, session
labels, Reshuffle) at the granularity the wireframe already uses elsewhere.
`audit_uml_model.py`: 0 violations throughout.

**Docs:** found two more stale canonical action lists beyond what #52's own commit touched —
`libs/transformer/README.md` and `docs/appendix/transformer_actions.qmd` (the latter is the
full per-action gallery; added proper §2.15–2.17/§6.3 entries, not just a list mention).
`audit_docs_sync.py` and `check_doc_links.py` both run fresh: 0 new violations (87
pre-existing broken doc links found, none touching anything this session changed — left
alone, out of scope).

**Audits:** `./scripts/run_audits.sh all` — all 10 routines PASS. Found a real, silently-broken
routine: `audit_template_flags.py` was renamed to `audit_app_features_flags.py` during the
ADR-091 vocabulary rename, but `run_audits.sh`'s thursday/all step and the script's own
docstring usage examples still named the old file — `|| true` was swallowing the resulting
error on every scheduled run since. Fixed both references.

**Tests, full gate:** headless `libs app/tests` 1589 passed. Full Playwright gate —
`test_shiny_smoke.py` + `test_shiny_smoke_blueprint.py` + `test_export_download.py` +
`test_every_app_features_starts.py` together — 64 passed, 3 expected skips.

**Issues:** #39, #44, #45, #46, #47, #48, #49, #50, #52 all explicitly **closed** (not just
commented) at Eve's direct request, each with a closing comment naming what was re-verified.

**Commits this pass:**
```
dd5e2ab docs(uml): thorough re-verification pass — UML, docs, and audit drift for #44
```
(plus the three feature commits from the prior handoff entry: 0db0b49, c8c62dc, dc49a7e)

**Pushed to `origin/dev`** (`git@github.com:evezeyl/SPARMVET_VIZ.git`) — confirm with
`git log origin/dev -1` if picking this up fresh.

### Next step
None queued. #44 is fully closed, verified, and pushed.

---

## Handoff 2026-11-10 (end of day — live-testing findings, 3 fixes, evening review pass)

Eve did live manual testing of Home/Blueprint/Test Lab and found 4 real problems in one pass.
All fixed, tested, documented, UML-synced, and pushed. Tomorrow's plan: she tests HOME
properly, starting that session fresh (no memory) — this entry is what that fresh session
needs to know.

### What was wrong, and what was fixed

1. **Issue #53 — Blueprint's left-sidebar panel was named "External Exchange."** It only
   imports/exports a bare recipe YAML, not a reproducibility bundle, but the name didn't say
   that — Eve read it as the place to import a reproducibility bundle. Renamed to
   **"Recipe File Exchange"** with an explicit one-line pointer to the real location
   (`app/modules/wrangle_studio.py`, `build_sidebar_ui()`).

2. **Issue #54 — the reproducibility bundle Import control existed in HOME's Export panel
   but Eve could not find it.** First fix (visible label + hint text) was not enough — she
   said so directly ("BUT I cant see the External Exchange HOME - where do we import it?").
   Real fix: restructured `system_tools_ui()` in `app/handlers/export_handlers.py` so Import
   is a bold-headed block, physically **first**, above Export, inside an accordion panel
   renamed **"Export / Import."** Confirmed by pixel position in a new mutation-tested test
   (`test_import_a_bundle_block_is_findable_above_export_form`), not just by existence.

3. **Issue #55 — Test Lab's right sidebar showed nothing.** Root cause:
   `config/ui/sidebars/testlab_standard_right.yaml` was `visible: false, panels: []`, stale
   since the panel content (`_render_test_lab_right_info()`, 5 tool descriptions) was written
   — the content always worked, the slot config was just never flipped on. Fixed the YAML;
   added a regression test that checks the actual tool names render
   (`test_test_lab_right_sidebar_shows_the_tool_descriptions`) — there was no test for this
   panel at all before, which is why a dead config sat unnoticed.

4. **Blueprint's "Validate" button never actually validated against the real engine load
   path.** It only ran a static-shape subprocess check — a recipe could pass Validate and
   still fail to load in HOME. Fixed `_handle_validate()` in `app/handlers/blueprint_handlers.py`
   to merge three checks: `validate_data_analysis_recipe()` (the real ADR-092/094 engine-load
   path) + the existing static coherence subprocess + `validate_data_analysis_recipe_data()`
   (data vs. contract). New test asserts the `"recipe rules"` row specifically, not just a
   PASS/FAIL badge (`test_validate_runs_the_real_engine_load_check`).

### The pattern behind all of this (why it slipped through)

Every one of these was a case of "the test checked existence, not the actual user-visible
behavior." Added three new mutation-tested Playwright regression tests closing exactly that
gap — each one verified tonight to fail against the original bug and pass against the fix,
with zero leftover mutation code (`git diff` confirmed clean each time). See the "GUARDED"
code comments at the 4 touched files for which test guards which behavior.

### Also fixed, unrelated to today's bug reports

A real, pre-existing Playwright test race in
`TestRecipeSwitchRendering::test_first_plot_renders_without_a_click_after_recipe_switch`
(predates this session, commit `47b274c`, 2026-11-08) — the restore-to-ST22-dummy step waited
on a tab label shared by two different recipes, so a later test's shared-session shortcut
could occasionally load the wrong one. Fixed by waiting on a plot sub-tab name unique to
ST22-dummy plus an explicit selector-value check. Verified clean twice in a row after the fix.

### Still open / known caveats (not blocking)

- `mcp__staruml-bridge__staruml_export_diagrams` silently does not write files — confirmed by
  unchanged mtimes across two calls that both reported success. Worked around tonight by
  copying the already-rendered `staruml_diagram_image` result directly. Needs a real fix or
  replacement before it's next needed for a larger diagram batch.
- Issue #54's "comparison to what was before" — whether Eve meant something beyond the 4-leg
  hash verification table (e.g. an actual diff view against the currently-open recipe) is
  still open, documented in the issue #54 comment thread and as `HOM-59` in
  `.claude/tasks/test_plan_home_2026-11.md`. Needs her clarification, not a guess.

### Verification done tonight, all clean

- Live Playwright screenshot walkthrough (dev server, `developer` app features, port 8123) of
  Home Export/Import, Blueprint Recipe File Exchange + Validate, Test Lab right sidebar — all
  6 screenshots visually confirmed correct, saved to `tmpAI/home_review_2026-11-10/`
  (gitignored, agent scratch — not meant to persist, regenerate if needed).
- Test recipe for tomorrow, `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`:
  0 structure problems, 0 data-contract problems (`validate_data_analysis_recipe[_data]`).
- UML: added the missing UI-TESTLAB right-sidebar panel (frame widened 940→1250), saved,
  `audit_uml_model.py` 0 violations.
- Headless suite: 1589 passed. Full Playwright gate: 67 passed (64 + 3 new)/3 skipped, no
  flakes, 428.85s.
- `audit_docs_sync.py` 0 violations, `audit_deps_verify.py` PASS.

### Commits this session

```
143ae2d fix(blueprint,home): close #53/#54/#55 and make Validate check the real recipe rules
58d6490 test(home,blueprint): mutation-tested regression guards + UML + intent comments
```

Pushed to `origin/dev`. Working tree clean (`git status --porcelain` empty at session end).

### Next step for tomorrow's fresh session

Eve is testing HOME tomorrow, deliberately starting a **new chat session with no memory** so
testing starts clean. For that fresh session:

1. Read this handoff entry first, then `.claude/tasks/test_plan_home_2026-11.md` for the
   live test plan (has `HOM-59` open, see above).
2. The 3 issues fixed tonight (#53/#54/#55) are closed — re-verify only if something looks off
   again, don't assume they're still broken.
3. Test recipe is `1_test_data_ST22_dummy` — already confirmed clean, no need to re-check
   unless the data or recipe files change.
4. Dev server for manual testing: `PYTHONPATH=. SPARMVET_APP_FEATURES=developer
   ./.venv/bin/shiny run app/src/main.py --port 8123` (or whichever app features Eve wants —
   `developer` has every flag on).
5. The new "VOCAB NOTE" / "GUARDED" code-comment convention (added tonight at
   `wrangle_studio.py`, `export_handlers.py`, `home_theater.py` ×2) is there to help a fresh
   session quickly find which test/UML element governs a given panel's intent — grep for
   `VOCAB NOTE` or `GUARDED` if something in HOME looks wrong and the reason isn't obvious.

## Handoff 2026-11-11 (HOME filters and audit: design day; a fresh session may start the build of Exploration and the engine fixes)

**Branch:** dev. Code last changed by `fa552bf` / `28ec1a6`; everything after is design (UML, ADR-098/099, design files, issues).
**Uncommitted and not ours:** `CLAUDE.md` (Eve added section 9 "No Guessing"). Never stage it.

### What happened
Eve's manual test of HOM-09 led to a day of design. Result: Exploration (preview, table only, per dataset, cleared on view change) is
agreed; audit mode (the only way to change a plot) is designed but **not decided** (13 questions in
`.claude/design/home_audit_reading_guide.md`). Four reviews (scientist, data scientist, developer, consistency checker) found
verified bugs and design holes; the method is saved in `.claude/workflows/design_review_personas.md`.

### Built today (on dev, tested)
Preview filters change the table on every view and plots only on My view (ADR-098); trash unapplies at once; one operator vocabulary
and text size (#57, closed); tests for all of it (headless 1599 passed; `test_shiny_smoke.py` 38 passed, 3 skipped).

### Verified problems, open (issues)
#61 `extract_primary_keys` returns `[]` on tiered join steps (the ADR-049 key safeguards never fire; its only test is a dead debug script);
#62 integer thresholds truncated (`>= 90.5` keeps 90); #63 missing values dropped silently by `!=`, none-of and comparisons; #59 helper and
message for a plot broken by a dropped column; #64 guard rails; #60 the audit redesign; #56 Exploration.

### Next step for a new session
Open `.claude/tasks/home_exploration_build_brief.md` and follow it: WP1, WP2, WP3a, WP4 (with WP5), WP6; WP3b (the NA rule) is BLOCKED. It has a safety protocol (baseline, one revertible
commit per package, frozen files, compatibility with the audit) and four questions for Eve to ask first. Task entries: `HOME-EXPLORE-1..6` in `tasks.md`.
Re-verified the same day: #61 (empty key list on 3 recipes), #59, #62, #63; and a new finding, the audit engine and the translated recipe actions
give different rows for an integer threshold, so the figure and the reproducibility bundle disagree today (#62).
Audit mode waits for Eve (`AUDIT-DECIDE-1`). Archive tag before the redesign: `archive/home-filters-uml-2026-11-11`.

### Where everything is
Reading guide `.claude/design/home_audit_reading_guide.md`; design `home_preview_filters.md`, `home_audit_steps.md` (sections 18-20 are the
reviews); ADR-098 (built) and ADR-099 (target); diagrams `docs/UML/diagrams/HOME-*` and `UI-HOME-*`; issues #56, #59-#64.

## Handoff addendum 2026-11-11 (recipe review of 1_test_data_ST22_dummy)

**Done:** data-scientist review of the ST22 recipe (`.claude/design/recipe_review_st22_2026-11-11.md`). Verified by running: `facet_by` inside `mapping:` is ignored (#65);
three other plot-spec keys dropped silently (#66); `ST22_Anchor` joins two long tables (rows 74 -> 1731, `virulence_count` wrong for 18 of 42 samples, #67; engine check #68);
recipe hygiene (#69); samples with only unknown phenotypes scored as 0 (#70); the recipe data check passes while a schema cannot be built (#71). #61 has a second defect (the `on:` of
`unpivot` steps would be taken as join keys). Recipe fixed where unambiguous; all six plot-target collections byte-identical before/after; 21 new tests
(`test_shipped_recipes_hygiene.py`), headless 1620 passed.
**Waiting for Eve:** `RECIPE-ST22-2` (three questions in section 3 of the review file). **Brief updated:** WP7-WP10 added, WP2 gains the unpivot test.

## Handoff 2026-11-11 night (prepared while Eve rested; start from `.claude/tasks/next_session_start.md`)

**Done and committed:** recipe fixes of `1_test_data_ST22_dummy` (`7775a8d`); QA canary group with raw-file oracles (`c2cb302`); `mapping.facet_by` honoured (`4f85ec2`, #65, closed);
the recipe data check runs the wrangling (`af36dc9`, #71, closed). Issues #61-#71 re-verified against the code the same day (#59, #61, #62, #63 demonstrated again by running).
**Verification:** headless 1646 passed; QA canaries 8 passed; browser gate: 1 pass (recipe fixes only), then 3 runs of the changed tree with 1 or 2 timing failures each time in DIFFERENT tests (info panel, preview filter row removal, session label) that pass alone and in other runs; fresh-session load time unchanged; not proven either way: issue #72 (read it before you trust or distrust a red gate). I committed with that stated.
**Prepared for tomorrow:** `.claude/tasks/next_session_start.md` (three tracks, file ownership, traps, paste-ready prompts), the build brief with an issue protocol for parallel sessions, a status table and the canary map,
`.claude/design/home_audit_review_agenda_2026-11-12.md` and `home_audit_first_cut.md` (a proposal for a smaller first audit version, not decided), `recipe_review_st22_2026-11-11.md`.
**Waiting for Eve:** #67 (ST22 anchor), #70 (unknown phenotypes), #69 (rest), the NA rule (WP3b), the many-to-many check (#68, edits `libs/transformer`), the 13 audit decisions.
**Do not forget:** `CLAUDE.md` (Eve's section 9) was committed on 2026-11-11 at her request; do not edit it. Libraries are installed editable with absolute paths, so no git worktrees for builders.


## 2026-11-12 (morning, before the audit review)

**Done:** QA canary `QA_aggregated_no_key` (the fixture for the audit reach, #60; headless 1649 passed); the cheaper engine (E) explained with measurements (`home_audit_forensics_2026-11-12.md` 3.2b); F8 and 3.7 corrected: a feature without audit never changes a plot, that is Eve's rule and not a loss; a software architect's forensic review of the app and of the undecided items (`.claude/design/home_audit_architect_review_2026-11-12.md`).
**Most consequential finding:** recipe text runs as Python (`eval` in `mutate`); verified by running a `developer_raw_yaml` step. Bundle import writes a zip's recipe into the shared recipes folder. Severe only on a shared server. Not exploited. Options in architect review 3.1; nothing changed.
**Waiting for Eve:** N2-N6 and the proposal "view policy first in WP4 (#56)" (task `AUDIT-ARCH-DECIDE-1`); the earlier list (R1-R4, 13 audit decisions, NA rule, WP10). No issue was filed for the architect findings (candidates are listed in section 6 of the review).
**Not changed:** app code, design files other than the three above, the UML. The builders' file ownership and prompts in `next_session_start.md` are unchanged apart from the baseline numbers (headless 1649, canaries 9).

## 2026-11-12 (correction, same morning)

Eve asked me to check every consequence against what is decided. **Corrections to the entry above:** (1) the strip: the decided target has "Data: Raw | Result" in every feature and no "Plot to show", no My view, no Compare in Exploration; the rule "no sandbox flag, no changed plot" was already decided in ADR-099 (it was never a new decision N1). (2) "view policy first in WP4" is **withdrawn** (WP4 is interim; the policy module belongs to the audit build, written against the target). (3) The cheaper engine reconsiders a decided mechanism and was measured in the plot-level mode only. (4) Keys (inference as fallback) and the NA rule in principle were already decided.
**The real open question** is the interim for the two features without the sandbox flag (they keep a plot that changes unrecorded until audit mode exists; brief section 5, question 3, never answered), and the meaning of "Raw has no plot (NA)". Both in forensics 3.7, F8, F14. New verified fact: no code creates a `developer_raw_yaml` step (the rules say the Blueprint escape hatch does).
**Files rebuilt:** `.claude/design/home_audit_forensics_2026-11-12.md` (status map, reconsideration list R1-R6), `.claude/design/home_audit_architect_review_2026-11-12.md` (status on every item). Builders' instructions are unchanged.

## 2026-11-12 (Eve's answers on gating and test configurations)

Eve answered: filters not active are **hidden**; gating follows the configuration and must be clever; preview filters and filters that change/send to audit stay different; correct configuration files for automatic tests are needed; the demo is not a design concern. Everything else goes into documents for review (she cannot split attention).
**New paper:** `.claude/design/home_gating_and_test_configs_2026-11-12.md` (problem P1-P6, capability model, options G1-G4, companion rule R-a/b/c, test configurations C1-C4, 8 questions). Verified by running (scratch configs in `tmpAI/architect/test_configs/`, not committed): configs validate by path (`scripts/validate_app_features_config.py --strict`) and launch; a no-audit config offers My view and Plot to show; the "Exploration only" notice depends on a proxy flag; the Export panel says "steps sent to audit" without an audit; Rule 6 makes audit without Compare fatal (11 of 32 combinations clean).
**Waiting for Eve:** Q1-Q8 of the paper (task `HOME-GATING-DECIDE-1`) and the earlier list. Nothing built; builder instructions unchanged.

## 2026-11-12 (Eve's correction: design first)

Eve: the gating paper described how the code works today and started in the wrong order. **New order:** (1) agree the behaviour design, (2) mechanism, (3) build plan, (4) code, (5) gating and test configurations derived from the agreed behaviour table, (6) tests. **New file:** `.claude/design/home_design_first_roadmap_2026-11-12.md` (stages, behaviour table by kind of configuration from decided texts with open cells, questions Q1-Q5). The gating paper is PAUSED (banner). Builders: unchanged (engine fixes and WP4 stay; nothing touches the strip). Waiting for Eve: Q1-Q5 (task `HOME-DESIGN-FIRST-1`). Found: the contract 7.1 says sessions save applied filters, the exploration design says never, no code saves them (to correct in stage 3).

## 2026-11-12 (sorting the clutter, Eve's order of work)

Eve: move outdated plans/tests to a flagged `outdated` folder; work as design (science- and software-sound) -> review and agree -> plan -> build, one problem at a time. **Done:** ten files moved to `.claude/outdated/` (README index, OUTDATED banners; rename plan/mapping, Phase 26 UI checklist, August testing log, 3 design sketches); the three analysis papers moved to `.claude/design/home_evidence/`; builder brief and start file flagged ON HOLD, first cut PARKED, HOME test plan flagged "valid for as built"; reading guide section 0 now holds the order of work, the criteria (S1-S6, W1-W6) and the problem queue P1-P9 (**P1 is NOW**). Not moved (tied to something live): retest procedure, test plans, `design_t3_export_threading.md` (CLAUDE.md), the brief (issues link to it). Builders must not start before Eve releases a package.

## 2026-11-12 (P1 decided)
Eve decided P1: audit mode requires export, Compare and sessions; Compare requires audit. Rule 6 of the validator is right; my F16 / gating P4 / R-b, R-c / `test-audit` were wrong (withdrawn in the papers). Reading guide idea 8 explains "rows are not samples"; idea 9 and ADR-099 point 10 reworded (audit may remove poor-quality samples or data that makes no sense in a plot; not for exploration; not for homogenising messy fields). ADR-099 point 11 added. P2 is now.

## 2026-11-12 (P2, plot decided)
Eve: Exploration has ONE plot (Result, immutable, always shown); Audit mode has the immutable Result (comparison) and the audited plot (T3/My view). Replaces "Raw has no plot (NA)" in `home_preview_filters.md` (text fixed). UML to update after her OK: UI-HOME-EXPLORATION box and HOME-VIEW-MATRIX PLOT row (Raw cell "NA"). Open in P2: the notice text.

## 2026-11-13 (recipe format: specification drafted, issues filed; no recipe, validator or code changed yet)

**Eve's answers (2026-11-13):** the format applies to EVERY recipe (app and tests, transformer test recipes, gallery, writers); unknown keys FAIL; no backward-compatible default, old names refused at once with `legacy_keys.py` only suggesting the replacement; `is_primary_key` -> `is_entity_key`; T3 container in the schema now; dataset tier-2 fixed; required `data_engine: python-polars` and `plot_engine: python-plotnine`; descriptions filled by data-scientist rules; draft with `1_test_data_ST22_dummy`; spec lives in `.claude/design/` then spreads to rule file, appendix and user docs.
**Done and committed:** audit triage of the six reports of 2026-11-12 (`e3865b59`, all PASS, the checks are May-era and blind to the new rules); review `recipe_format_review_2026-11-13.md` (`f77425b0`); specification `recipe_format_spec.md` v0.1 and the ST22 main-file draft `recipe_format_st22_draft.yaml` (`6e83f773`; later edits and this entry in the next commit).
**Issues (fork, `-R evezeyl/SPARMVET_VIZ`):** tracking #73; #74 spec, #75 tests, #76 checker (folds #66), #77 tier-2 bug, #78 migrate, #79 docs, #80 formulas, #81 audits. Tasks in `tasks.md` carry the numbers (RECIPE-SPEC-1, RECIPE-TESTS-1, RECIPE-MIGRATE-1, RECIPE-DOCS-1, RECIPE-FORMULAS-1, RECIPE-AUDIT-REFRESH-1; UNKNOWN-KEYS-1 = checker).
**Baseline before any change:** headless 1652 passed in 99.65 s. ST22 content-hash baseline: `tmpAI/recipe_format/st22_baseline.json` (scratch, not committed; regenerate with `tmpAI/recipe_format/st22_facts.py`). Other scratch: `scan_compliance.py`, `key_inventory.py`, `step_params_probe.py`, `layer_probe.py`.
**Waiting for Eve:** section 13 of the spec (14 points: example variant for the gallery, schema `category`/`sub_category`, T3 container name, schema `output_fields` applied or not, legacy files, plot-spec taxonomy keys refused (reverses #66's text), alias removal in `libs/transformer`, type vocabulary, `scan_parquet`/`sink_parquet`), and the Abromics descriptions later.
**Next step (after her review):** #75 tests first (they must fail for the right reason on today's code), then #76 checker, #77 tier-2 fix with before/after pictures of `amr_heatmap` for @verify, #78 migration (ST22 first, text-level edits, fragment comments are Eve's: "do not remove").
**Do not touch:** `.claude/design/spaces/HOME.md` shows as modified in the working tree: it is Eve's own edit, never stage it.
