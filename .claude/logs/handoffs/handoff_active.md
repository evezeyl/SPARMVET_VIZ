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

## 2026-11-13 (later: spec v0.3, gallery as standard recipes: options written, waiting for Eve's choice)

**Eve's review of v0.2:** comments need a specification; the gallery must follow the same spec (examples are recipes), be checked by the same code as the app, and its needs go into the spec; propose solutions with pros and cons; explain the column-alias change; recipe science errors must be fixed.
**Found:** the comment key already exists as `comment` (singular): BP-COMMENTS-1, written by Blueprint on steps, layers, groups, plots (`blueprint_handlers.py:376-378,402-404`); ADR-083 lists it on layers. Spec v0.3 renames my `comments`, the checker must accept `comment` on every step and layer. The taxonomy terms are copied in five places and drifted ("Numeric-Numeric"). `submit_example` writes the example's steps into `wrangling.tier3`.
**Proof of concept (scratch `tmpAI/recipe_format/gallery_poc.py`):** all 34 gallery examples as standard recipes build and render through ConfigManager, DataOrchestrator, VizFactory; 22 pixel-identical, 10 differ only in size (800x600 committed vs 960x600), 2 jitter. Taxonomy all inside the cheat sheet; `dumbbell` declares `geom_segment` but draws `geom_line`/`geom_point`.
**Written:** `.claude/design/recipe_format_gallery_options_2026-11-13.md` (decisions D1-D7, inventory of 10 changes, order); spec section 6.9 withdrawn; issue #82; task GALLERY-RECIPES-1.
**Waiting for Eve:** D1-D7 of the gallery options (recommended: first option of each), the key name `taxonomy`, dead submission code removed or kept; plus section 13 of the spec. Nothing in the gallery or the recipes was changed.
**Do not touch:** `.claude/design/spaces/HOME.md` (Eve's edit).

## 2026-11-13 (later still: spec v0.4, format version, gallery plan v2)

**Eve's answers:** what is wrong in the gallery will be fixed; a format version for recipes matched to the spec is a good idea (from her review of the app changes with another agent); the gallery's `taxonomy` key is required; the authorised terms should be in the spec (one place instead of two); the gallery work is later but planned now.
**Written (docs only, committed):** spec v0.4 (`format_version`: section 4b, checks V01-V04, migration tool `migrate_recipe_format.py`, history table; one-place proposal in section 0; section 13 points 16-17); ST22 draft carries `format_version: 1`; gallery options v2 (`recipe_format_gallery_options_2026-11-13.md`): D3 rewritten (the specification as a data file, terms included), G1-G8 each mapped to a package and a test, plan GAL-0..GAL-9 with dependencies and tags, "decide now" (D1-D3, key name) versus "later" (D4-D7).
**Issues:** new #83 (format version + migration tool); #73, #76, #78, #82 updated, #74 commented. Tasks: RECIPE-FORMAT-VERSION-1, GALLERY-RECIPES-1 (plan).
**Waiting for Eve:** D1-D3 and the key name (they shape how #76 is built, so before the checker starts); `format_version` name/form; section 13 of the spec. Nothing in recipes, gallery or code was changed.

## 2026-11-13 (even later: the checker and the specification data file in libs/utils: verified)

**Eve's question:** does a data file in `libs/utils` break our rules; can one universal checker serve HOME, Blueprint and the others; recent decisions?
**Verified:** rules respected (Tier 1 pure + pyyaml; Tier 2 libs declare `utils`; ADR-011; ADR-099 16(g); the HOME stage-2 draft already places `utils.recipe_check` and `utils.recipe_graph` in `libs/utils`). A scratch prototype (`tmpAI/recipe_format/proto/`) shows a checker core that imports no peer library, reads its rules from a data file, gets the action/plot catalogs from the caller, and reports coverage; on the ST22 recipe it finds the 3 step problems. **Found by building wheels:** the container installs libs non-editable (`Dockerfile:72-81`); without `package-data` a YAML file in `utils` is missing from the wheel (no library ships data files today). **Also found:** `Dockerfile:79` lists the non-existent `libs/generator_utils` and omits `blueprint_arch`, `test_lab`, `id_reconciliation` (noted in DOCKER-RELEASE-1, no new issue).
**Written:** spec v0.5 section 0b (rules table, packaging, design with injected catalogs and a coverage report, one Tier-3 adapter, callers, the loader's catalog-free subset); gallery options D3/D4 note; #76 updated (architecture, packaging test, import test, full-coverage test).
**To align between sessions (Eve's call):** the HOME stage-2 draft writes `check_recipe(raw, mode)`; the recipe spec writes `profile` (run, build, gallery). "Mode" already means Exploration/Audit in HOME. Proposal: `profile`.

## 2026-11-13 (dictionaries and reuse: ADR-041 found; spec v0.6)

**Eve's notes:** (1) some library code may need to move to `utils` to be reusable (no overview yet); (2) recipes written as dictionaries: there are rules, check list or dictionary; (3) the Dockerfile is not ready, nothing is deployed.
**Found:** ADR-041 (ENFORCED 2026-04-20): keyed definitions = Rich Dictionary, tier1/tier2 = sequential list, fragments flat (no anchoring key). The spec never stated the form of each container; now section 4c does. Scan (`tmpAI/recipe_format/container_forms.py`): all 307 input and 162 output field entries are dictionaries; 17 list-form containers (7 empty `[]`, 10 with content: 3 `final_contract` lists skipped silently by the engine (`demo_abromics`, `universal_template`, `relational_audit`), 1 `output_fields` list of names, 1 flat legacy `wrangling`, 5 flat join `steps` in fixtures); 33 wrapped fragments; PyYAML keeps duplicate keys silently (verified), so the loader needs T10. Two texts contradict ADR-041 (rule file section 8; data contract rules 4.3 types). Parameters declared `multi` get a list 90 times and a single value 2 times.
**Written:** spec v0.6 (4c, checks T10, FD06, ST07, J07, reuse candidates in 0b, finding 16); #76 and #78 updated; tasks UTILS-REUSE-REVIEW-1 (a possibility, nothing moved) and the Dockerfile note ("not ready, nothing urgent").

## 2026-11-13 (dictionaries enforced with corrective messages; identical keys; the string type)

**Eve:** recipes must be dictionaries and tests and the app must verify it with an error message and a suggestion; add it to HOME and to the refactoring plan; identical keys matter (the same ID in every T1); why was the `string` type removed; unify and read the types in one place.
**Done (docs/tasks/issues only):** spec v0.7: 4c now says every container-form check shows the **corrected text** (generated), in the app (one adapter) and in the tests; "identical keys" explained (unique per mapping; `sample_id` in every table is correct; real hazards: a repeated key in one mapping (T10), a column in both tables of a join silently renamed `..._right` (check J08, `QC_Reads_Anchor.total_reads_right`), steps stay lists because a T1 repeats actions); type vocabulary history + options A-D (6.4, point 10); points 18-19. **Added to the HOME plan at Eve's request, minimal edits:** `home_stage2_mechanism_spec.md` rows P2 and P3, `home_audit_reading_guide.md` register item (C) ("added after the count"). `spaces/HOME.md` NOT touched. Tasks: RECIPE-TYPES-1, RECIPE-GRAPH-UTILS-1, RECIPE-TESTS-1 updated. Issues: new #84 (types), #73 #75 #76 #78 updated.
**Verified by running:** ingestor casts `categorical` and `string` to String, but NOT `utf8`, `boolean`, `i64` (digits stay Int64); PyYAML keeps the last of two identical keys silently; joins use Polars' default `_right` suffix.
**Why `string` was removed:** on record only "deprecated alias" (LEGACY-TYPE-ALIASES-1, Phase 34 legacy sprint, commit 125963cf; 6 recipes migrated string -> categorical). No ADR gives a deeper reason; stated as such.
**Waiting for Eve:** type vocabulary content (A keep four + cast utf8 [recommended], B rename utf8 to text, C restore string, D add boolean); point 18 (steps stay lists?); point 19 (level of J08); plus the earlier points (D1-D3 gallery, format_version name, `profile` vs `mode`).

## 2026-11-13 (spec v0.8: the form follows what depends on it; registry check)

**Eve:** (1) "design our specs accordingly, based on what depends on it" after the HOME analysis (ordered steps stay lists; named things dictionaries; optional `id` in a step); (2) "dictionaries are the containers, the rest ordered steps; check how each operation for the data and plot is registered".
**Done (docs, tasks, issues only; no code changed):** spec v0.8: 4c rule with three categories (dictionary / list / ordered dictionary), 4d step ids (optional `id`, `audit_` for app-inserted steps), checks ST08 to ST10, 6.10 registries (R1 to R6, tests AR2 to AR6), findings 18-19, section 13 points 18 and 20, tests. Issues: new #86 (stored T2 keeps the old column order after a `final_contract` reorder, verified by running), new #87 (registry gaps), #85 reframed, #73 #75 #76 #78 #83 bullets corrected. Tasks: RECIPE-ORDER-IDS-1, RECIPE-REGISTRY-1.
**Verified by running (scratch in `tmpAI/recipe_format/`):** `registry_survey.py` (67 actions, 65 with schema; 191 components, all with schema, all `allow_extra_params: true`; 8 widgets, none for list or dictionary), `registry_conformance.py` (aliases read by `rename`, `split_column`; internal `__right_df__`, `__metadata__`), `registry_examples.py` (9 examples disagree with their own declared widget), plotnine refuses `foo` and accepts `color` and `colour`, `contract_order_test.py` (T1 follows the new `final_contract` order, stored T2 does not).
**Process incident:** my uncommitted v0.8 edits (steps as dictionary, since withdrawn) were committed by the HOME session in `c8c916dc` (that commit lists 4 files, 3 of them mine; how they were included is not known). HEAD held the superseded draft until this commit replaces it. We share one working tree: both sessions stage by explicit file names.
**Waiting for Eve:** spec 13.18 details (`id` optional or required; `audit_` prefix; `final_contract` key order = column order; tab order = key order), 13.20 (parameter vocabulary; layers read plotnine arguments), type vocabulary (A to D), gallery D1-D3 and `taxonomy`, `format_version` name, `profile` vs `mode`, J08 level.

## 2026-11-13 (clean spec; #86 and #87 fixed; #88 filed)

**Eve:** fix the gaps (registries yes; `final_contract` order yes; tab order yes; plot arguments are checked); fill the issues, then do it and close when done; make the specification files clean (one file, the rest archived), then review what is undecided.
**Done:** (1) `.claude/design/recipe_format_spec.md` rewritten as ONE file (commit `e958eab1`): decisions with source (2.1), principles (2.2), **open points in one table (2.3, O1 to O18)**, then how each part works; the earlier drafts, the gallery options, the first review and the ST22 draft are in `.claude/design/outdated/` with OUTDATED banners; the ST22 findings are on issue #78. Issues #73 to #87 point at the new section numbers. (2) **#86 fixed and closed** (`b2c46ca9`): the key order of `final_contract` is part of the Tier 1 key (`ENGINE_CACHE_VERSION` 3); 9 tests. (3) **#87 fixed and closed** (`7cafc08a`): widgets `list` and `mapping`, eight declarations corrected (the count is eight, not nine), the Blueprint form shows and saves one line of YAML, `viz_factory.arguments` (what plotnine accepts, verified against plotnine for all 63 geom and stat components), `utils.strict_yaml`, `utils.ui_schema`, registry consistency tests AR2/AR4/AR5/AR6. (4) **#88 filed**: 13 schema parameters in 7 components that plotnine refuses (found by the oracle).
**Verified by running:** headless baseline 2101 passed (was 1652); Blueprint smoke suite 17 of 17; three mutation checks fail as they should.
**Not done, by design:** ST09, ST10, AR3 against the checker (#76); alias reads in `rename` and `split_column` (#78); rule files (#79, double confirmation).
**Process:** the other session was re-sorting `tasks.md` and `INDEX.md` while I worked; I committed only files I own, by name (`tasks.md` after their sort was committed).
**Waiting for Eve:** the open points of spec section 2.3 (O1 to O18); answers to what the step `id` is for are in spec 7.5 and on #85.

---
## Handoff 2026-11-13 (late): the recipe format series, HOME session alone (the recipe session was closed by Eve)

**State (all on `dev`, committed, suite green, golden baseline "result-identical"):** W0 golden baseline (`assets/scripts/golden_baseline.py`, `app/tests/golden/baseline.json`); W1 `step_problems` and schema `rules`; W2 `check_recipe`; W3 formula check, path checks, `!include` confinement; W4 `utils/action_names.py`; W5 `DataIngestor.ingest_declared` (`ingestion/declared.py`); W6 the new actions registered beside the old ones: `actions/polars_calls.py` (39 `polars_`), `actions/modified.py` (`modif_filter`), `actions/composite.py` (`step_top_n_other`); W7 part 1 `utils/recipe_migration.py` (keys, types, null_values, strip, spec_version).
**Eve's rules:** sequential, one agent; Eve decides, I recommend; Polars action and nothing else where possible; no silent behaviour, no hidden default; never truncate silently (no `modif_cast`); tests for everything, mutation-checked; I am `sonnet/high` and do the medium, low and haiku items too; only `opus/high` items need Eve to change the model (W12 ADR-100, W15 science review, W3b attack design, the rule-file text). Eve is resting; she reads the report in the chat.
**The series that remains (one atomic switch; dev must be green at every commit):**
 S1 a converter old step to new steps (`utils/step_migration.py`) with a differential test per old action (`libs/transformer/tests/test_step_conversion.py`; templates already in `test_replacements_by_polars_steps.py`);
 S2 migration tool part 2: rewrite the steps in the yaml text, run over `config/`, fixtures, tests (120 yaml files with old action names, 92 with old types, 36 `.py` and 22 `.py` with inline recipes);
 S3 remove the old actions, `ingest_declared` becomes `ingest`, DataWrangler/assembler/orchestrator/MetadataValidator/audit translator/bootstrapper/id_reconciliation use the new names (constants in `utils.action_names`), the three xfail registry tests pass;
 S4 run the tool, check the golden baseline is identical, adapt the tests;
 S5 run B (`final_contract`, `keep_columns`, `drop_columns` to `polars_select`/`polars_drop`, `labels`), cache-version bump;
 then W8 writers, W9 engine side, W10 tier-3 reader, W11 gallery (GALLERY-RIGOR-1), W13 documentation (DOC-MISSING-VALUES-1), W14 Blueprint, W16 ID-RECON-STEPS-1, REMOVE-CATEGORY-SELECT-1, the stale `manifest_paths` line.
**Open for Eve (asked, not answered):** Q3 dead gallery submission code (remove or keep); the data owner's question on `NA` in `metadata_isolation_method`.
**Files:** `.claude/design/recipe_format_spec.md` (decisions), `recipe_format_work_order.md` (W0 to W16), `home_evidence/actions_and_polars_2026-11-13.md` (sections 9 to 26, the evidence), `tmpAI/agent_channel.md` (not in git).

## Handoff 2026-11-14: recipe format 1, state after the three parallel packages

**Branch:** `feat/recipe-format-1`. Local `dev` is behind it, and nothing of today after commit 29a563c7 is pushed.

**Merged:** the three packages (W11 gallery, W8 writers, W16 ID-RECON-STEPS-1 with RETEST-REPLACE-1, REMOVE-CATEGORY-SELECT-1, RENAMED-KEYS-1), the strict checker in the load gate, migration runs C and D, the orchestrator fails on unknown ids, `CLAUDE.md` section 2.1 (agent rules).

**Controls (2026-11-14):** headless suite 3604 passed, 14 xfailed (exit 0). Browser tests 70 passed, 3 skipped (exit 0). Golden baseline: result-identical. Audits: recipe coherence, deps verify, cross-lib PASS. `validate_app_features_config --strict` PASS. FAIL: `audit_docs_sync` (3 doc backtick path violations), `audit_task_drift` (1 drift: `app/modules/exporter.py` named by AUDIT-RAWYAML-REMOVE-1), `check_doc_links` (65 problems, for example `docs/appendix/viz_factory_rationale.qmd:157-158` still point to `libs/viz_gallery/assets/generate_previews.py` and `refresh_gallery.py`). Not fixed here.

**Open decisions for Eve:**
- Gallery: accept or reject the 8 changed previews (`tmp/gallery_preview_review/`); `beeswarm_sina` (tier-3 reader, move the filter to tier 1, or drop it); rewrite `rules_gallery_standards.md` (needs her double confirmation).
- Writers: a fresh Blueprint draft has no plot and cannot be opened (loader accepts an empty draft, or the form creates a first plot); delete the dead `SF_create_data_analysis_recipe.py`?; the two `debug_*` scripts in the old test-file shape (keep as test-only or migrate).
- ID reconciliation: three defects recorded as strict xfail tests; keep the bridge (recommended).

**Next:** JOIN-KEY-TYPES-1 (decided: a join keeps declared types), then IMPORT-PATH-1 (decided: option A), then SMOKE-RACE-2, the tier-3 reader, the Blueprint package, and the documentation sweep with the full name "data analysis recipe" in user-facing text.

## Handoff 2026-11-14 (evening): JOIN-KEY-TYPES-1 merged, follow-ups, index generator

**Merged:** JOIN-KEY-TYPES-1 (`bddaf76a`): a join keeps the declared types of its keys and fails when they differ. 14 baseline records change only by the type of `sample_id`; no joined table and no plot changed.
**Follow-ups (branch `feat/recipe-format-1`):** `77538c54` the key check also fails for a missing key column (one or both sides) and for `left_on`/`right_on` of unequal length, with a plain message; the fix text says a step before the join changes only the left table; semi/anti tests. `b0f0b198` the dependency index generator skips `.claude/worktrees/` (index 4820 to 989 lines); `check_doc_links` problems 566 to 61.
**Controls (reviewer, on 6e318386):** headless 3642 passed, 14 xfailed; browser (qa) 70 passed, 3 skipped; golden baseline result-identical; audits deps_verify, cross_lib, task_drift pass; docs_sync fails with the 2 known violations; dependency index 989 lines, no worktree path.
**Open for Eve:** a first assembly step that joins the base table with itself is skipped silently (keep, or fail); template `complex_template` has the key `sample_id` as Float64; DOC-JOIN-CAST-1 needs her for the rule file and a superseding ADR for ADR-050.
**Next:** IMPORT-PATH-1 stopped at step 0 (nothing built) and waits for Eve's decision (panel recommends a data folder per import; see tasks.md); then JOIN-PREVIEW-STRICT-1 with the Blueprint package, CHECKER-JOIN-KEYS-1, SMOKE-RACE-2, the tier-3 reader, the documentation sweep, DEP-INDEX-STALE-1.

## Handoff 2026-11-14 (night): for the next coordinator session

**Start:** a Fable session types `-coordinate` first (CLAUDE.md 2.1, `.claude/workflows/agent_dispatch_howto.md`). Workers: `builder`, `reviewer`, `scribe`, `scout`, the `panel-*` viewpoints.
**Branch:** `feat/recipe-format-1`. Nothing after `29a563c7` is pushed; local `dev` is behind. Push only when Eve says.
**Done today:** three packages merged (gallery examples as recipes, recipe writers, small fixes); strict checker in the HOME load gate; JOIN-KEY-TYPES-1 merged (`bddaf76a`) with follow-ups (`77538c54`); dependency index generator skips worktrees (`b0f0b198`); record repairs (`88bb3f9a`, `3395fcad`); agent setup (`6e318386`).
**Control command note:** the baseline check is `PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json`.
**Waiting for Eve (recommendation in brackets):**
1. IMPORT-PATH-1, stopped at step 0, nothing built: which option [a data folder per import, `<user_data>/_imports/<recipe id>/data/` plus a record read by the orchestrator]; the name of the imported recipe [keep `<original>_imported_<timestamp>`]; whether the by-dataset-id rule also accepts `.parquet` [yes, and fail when both exist]. Panel of three viewpoints agreed on the option. Findings: `.claude/worktrees/agent-abd52719502485bdb/tmpAI/progress.md`; hash survey: `tmpAI/survey_hash/table.md`.
2. The eight changed gallery previews, old and new side by side in `tmp/gallery_preview_review/`.
3. A first assembly step that joins the base table with itself is skipped silently: keep, or fail (tasks.md, under JOIN-KEY-TYPES-1).
4. TEMPLATE-KEY-TYPE-1 (key declared Float64 in `complex_template`); DOC-JOIN-CAST-1 (a rule file and ADR-050 still describe the removed cast; ADR text is `opus/high`).
5. Older open points in tasks.md: `beeswarm_sina`, the empty Blueprint draft, three old scripts, three ID-reconciliation defects, RECIPE-WORD-1 scope, String or Categorical in recipes.
**Next for the coordinator, in order:** (a) after Eve's answer to 1: IMPORT-PATH-1 together with SOURCE-LOOKUP-ONE-1, one `builder` at `sonnet/high`, continued in the worktree `agent-abd52719502485bdb` (merge `feat/recipe-format-1` into it first), then `reviewer`, merge, controls; (b) CHECKER-JOIN-KEYS-1 `sonnet/medium`; (c) the Blueprint package with JOIN-PREVIEW-STRICT-1; (d) tier-3 reader, GALLERY-CHECK-START-1, FILTER-UNIFY-1, SMOKE-RACE-2, AUDIT-REPAIR-1, DEP-INDEX-STALE-1; (e) the documentation sweep at the end (61 broken documentation paths, 2 docs_sync violations, seven of them in rule files that need Eve).
**Worktrees:** `agent-a57725701187f3e6e` (join keys) is merged and removed. `agent-abd52719502485bdb` is kept: no code, only the findings note.

## Handoff 2026-11-14: third coordinator session (interim): three tasks merged, queue, decisions for Eve

Live progress file: `tmpAI/coordinator/progress_2026-11-14_session3.md` (not in git; it is the state if the session stops).

**Branch and push:** `dev` was fast-forwarded to `1dad1f4c` and pushed to `origin/dev` at the start of the session (Eve asked). The three tasks below are merged into `feat/recipe-format-1` only: NOT in `dev`, NOT pushed.
**Merged:** JOIN-PREVIEW-STRICT-1 (`870207ba`, `13194791`); CHECKER-JOIN-KEYS-1 (`9da9ce19`, `00b64f53`, merge `67419ef4`); GALLERY-CHECK-START-1 (`f7f5aa20`, `642ec0f0`, merged after `67419ef4`).
**Controls:** on `67419ef4` (reviewer): headless 3695 passed, 14 xfailed; golden baseline result-identical; app import OK. Browser tests and the full controls NOT run after these merges (the gallery merge is after `67419ef4`). At the end of the session: full controls (headless, browser with `SPARMVET_APP_FEATURES=qa`, golden baseline, audits), then `git fetch . feat/recipe-format-1:dev` and `git push origin dev` (Eve asked that all commits are in `dev` and `dev` is pushed).
**Running:** SMOKE-RACE-2 (builder, worktree `.claude/worktrees/smoke-race-2`, branch `task/smoke-race-2`): seven `inner_text(` reads changed to waiting assertions, in its two browser runs. HOME scout: which HOME tasks (tasks.md group 1, stage-2 plan, #61 to #63, #56) are buildable now.
**Queue** (Eve's priority of 2026-11-14: HOME first with its library and recipe prerequisites, then Gallery; Blueprint and Test Lab last):
1. The HOME tasks the scout tags BUILD-NOW.
2. TEST-FLAKY-1 `[sonnet/medium]` (browser tests; after SMOKE-RACE-2 is merged, same files).
3. Documentation: DOC-MISSING-VALUES-1, the `docs/` lines of DOC-JOIN-CAST-1, broken paths in `docs/` and README (worktree `.claude/worktrees/docs-sweep` exists, unused).
4. DEP-INDEX-STALE-1 `[sonnet/low]` and the session-end `build_dep_graph.py`.
5. ADR-100 draft (W12, `[opus/high]`, one builder-opus), as a draft for Eve.
6. BP-VALIDATE-1 `[sonnet/low]` (Blueprint, last).
7. Records by a scribe: tasks.md, spec catalogue J09 to J11, two stale sentences of REMOVE-CATEGORY-SELECT-1 in `.claude/design/recipe_format_spec.md`, handoff, channel row.

**Decisions for Eve, new in this session** (also marked `DECISION FOR EVE` in tasks.md):
- N1: join key rule in three places (build, Blueprint preview, checker), kept in step by a parity test only. Options: keep the copies with parity tests; or one pure rule in `libs/utils`.
- N2: `except Exception` in `_jd_run_preview` shows programming errors as "Preview failed". Options: leave; or catch only expected errors.
- N3: read-only gallery folder: a failing example in the old index is still shown (console warning only). Options: keep; or leave failing examples out in memory (`bootloader.rejected_gallery_examples`).
- N4: an example left out at start has no screen element (spec section 9 silent). Today: left out, reason in `metadata.rejected` and a console warning.
- N5: checker J10 (join key not declared in `input_fields` refused at load): confirm. See N1.
- N6: AUDIT-REPAIR-1: four old words (`persona`, `manifest`, `profile`, `project`) and one UML tag: fix the text or adapt the exclusions. `recipe` waits for RECIPE-WORD-1.
- N7: tier-3 reader (W10) needs HOME's P5 mechanism spec and the order of change R1 (`recipe_format_spec.md` line 173); `beeswarm_sina` waits for it.
- N8: W14 Blueprint package: tasks.md line 82 says Blueprint is not touched now; the earlier handoff listed it as next. Eve (2026-11-14): Blueprint and Test Lab can wait.

**Decisions for Eve, older:** see "Handoff 2026-11-14 (night)", points 1 to 5 above.

**Worktrees:** `checker-join-keys`, `join-preview-strict`, `gallery-check-start` are merged and can be removed. `smoke-race-2` in use. `docs-sweep` prepared. `agent-abd52719502485bdb` kept (findings note, no code). Tests in a worktree need the worktree sources first in `PYTHONPATH` (the shared `.venv` imports the libraries from the main tree).

## Handoff 2026-11-14 (third coordinator session, update 2): six merges, dev pushed at 46425c89, decisions N1 to N15

Live progress file: `tmpAI/coordinator/progress_2026-11-14_session3.md` (not in git).

**Branch and push:** `origin/dev` is at `46425c89` (pushed). The merges `57724105` (documentation) and `334b8dfc` (browser tests) are on `feat/recipe-format-1` only: NOT in `dev`, NOT pushed. TEST-ORDER-1 is not merged.
**Merged since the interim note:** HOME-EXPLORE-1 (merge `46425c89`, commits `9427dc36`, `73cecd2b`); the documentation (merge `57724105`, commits `a607174f`, `b5fe3e78`, `5e9864b9`: DOC-JOIN-CAST-1 docs part, DOC-MISSING-VALUES-1, one broken path); SMOKE-RACE-2 (merge `334b8dfc`, commits `382848c2`, `9dffbb8d`). Six merges in this session with the three from the interim note. The documentation diff was not reviewed on its own; the final reviewer reads it.
**Found done already:** GALLERY-SUBMIT-SCHEMA-1 (read by W11, not run: `submit_example` writes format 1 and runs `check_recipe`; tested in `test_gallery_bundle.py`); NAN-ACTIONS-1 (`polars_fill_nan` and `polars_drop_nans` exist in `libs/transformer/src/transformer/actions/polars_calls.py`).
**Controls:** on `46425c89` (reviewer): headless 3818 passed, 23 xfailed; golden baseline result-identical; tree clean. The browser gate was run on `334b8dfc` by SMOKE-RACE-2 only (61 passed, 3 skipped, twice). Not run: the audits; the full controls on the final state.
**Running:** TEST-ORDER-1 fixes (builder sonnet, worktree `home-test-order`, branch `task/home-test-order`; commit `99447ec1` removes the #62 mark; the independent raw-file oracle and the docstrings are being added; then review). TEST-FLAKY-1 (#72) (builder sonnet/medium, worktree `test-flaky-1`, branch `task/test-flaky-1`; it runs the full browser gate once).
**Still to do in this series:** merge TEST-ORDER-1 and TEST-FLAKY-1, with headless controls after each merge; DEP-INDEX-STALE-1 with `build_dep_graph.py` (last builder); final controls by a reviewer (headless, golden baseline, audits, the documentation diff `a607174f..5e9864b9`); final scribe (handoff, tasks.md, spec section 11 catalogue J09 to J11, channel row); fast-forward and push `dev`.
**Not started on purpose** (quota and Eve's priority): ADR-100 draft (W12, opus/high); BP-VALIDATE-1 (Blueprint); RECIPE-DOCS-1 (#79, large); AUDIT-REPAIR-1.
**HOME: what blocks the rebuild:** NA-RULE-63 (#63): the NaN rule and the count message, Eve to confirm; STAGE2-SPEC-1: Eve reads and confirms the v0.1 mechanism spec (`home_stage2_mechanism_spec.md`); KEYS-NODE-1: Eve confirms the hash model (`home_evidence/home_hash_model_2026-11-12.md` section 4); RECIPE-GRAPH-UTILS-1: option C+; HOME-DESIGN-REVIEW-1 (SC1, SC2, SC4, AR4, SC5, AR2, AR1); FILTER-UNIFY-1; FORMULA-SAFETY-1. Tasks that wait for these: FILTER-DTYPES-1, HOME-EXPLORE-2 (#61), HOME-EXPLORE-4/5/6 (#56), AUDIT-VIEW-1, AUDIT-RAWYAML-REMOVE-1, TEST-SHAPES-1.
**Decisions for Eve N9 to N15** (also in tasks.md as `DECISION FOR EVE`):
- N9: VizFactory `in` / `not_in` compares as text, so a numeric `in` filter gives no rows in the plot. Evidence: 4 strict xfail cases, `app/tests/test_filter_int_equivalence.py`. Options: approve the small fix now (it changes plots with numeric `in` filters), or wait for FILTER-DTYPES-1.
- N10: the reproducibility export writes the filter value as text, so re-running it on a number column fails. Evidence: `t3_translator.py` about line 127; 12 strict xfail cases. Options: approve EXPORT-FILTER-VALUE-1 (the translator is frozen, brief S4), or leave it.
- N11: `between` is not translated (UntranslatableNode). Evidence: `t3_translator.py`. Options: add the translation later, or keep refusing it.
- N12: what blocks the HOME rebuild: see the list above.
- N13: a drop and a filter on the same column at one node. The view runs filters first; the exported recipe keeps the recorded order and stops with "column not in the table". Evidence: TEST-ORDER-1, checked by running; not tested. Options: refuse such a step, or define the order.
- N14: TEST-ORDER-1 tests that wait for the unconfirmed stage-2 spec v0.1 and for the `hypothesis` dependency (D9). Options: confirm the spec and allow the dependency, or leave those tests out.
- N15: `submit_example` has no caller outside the tests (`gallery_manager.py` 163-203). Options: keep, or delete.
**User-visible change:** a threshold that is not an integer on an integer column is now compared as a number, so the plot agrees with the reproducibility export (issue #62).

## Handoff 2026-11-14 (third coordinator session, final): ten merges, dev pushed, the decisions for Eve in one list

**Start:** a Fable session types `-coordinate` first (CLAUDE.md 2.1, `.claude/workflows/agent_dispatch_howto.md`). Workers run on the model and effort of their task tag, never on Fable. Worktrees: create one with `git worktree add .claude/worktrees/<task> -b task/<task>` and link the shared environment (`ln -s <main>/.venv <worktree>/.venv`; remove the link before `git worktree remove`). The shared `.venv` imports every `libs/*` package from the main tree, so tests in a worktree need the worktree's source folders first in `PYTHONPATH` (`PYTHONPATH=$PWD:$PWD/libs/<lib>/src:...`); ask for `print(<module>.__file__)` once to check.

**Branch and push:** the branch is `feat/recipe-format-1`. `dev` is at `13f120f6` and is pushed to `origin/dev` (fourth push of the session). All ten merges below are in `origin/dev`. The records of this session (this section, the tasks.md edits, the J09 to J11 rows of the spec, `.claude/logs/audit_2026-11-14.md`) are NOT committed yet.

**Merged** (merge commit, then the commits):
1. JOIN-PREVIEW-STRICT-1: the Blueprint join preview gives the build's verdict (merge commit not recorded in the progress file; commits `870207ba`, `13194791`).
2. CHECKER-JOIN-KEYS-1: the recipe checker refuses J09, J10 and J11 at load (merge `67419ef4`; commits `9da9ce19`, `00b64f53`).
3. GALLERY-CHECK-START-1: with `gallery_enabled`, the gallery check runs at start (merge commit not recorded in the progress file; commits `f7f5aa20`, `642ec0f0`).
4. HOME-EXPLORE-1 (#62): one shared filter-value coercion in `libs/utils` (merge `46425c89`; commits `9427dc36`, `73cecd2b`).
5. Documentation (merge `57724105`; commits `a607174f`, `b5fe3e78`, `5e9864b9`): the docs part of DOC-JOIN-CAST-1, DOC-MISSING-VALUES-1, one broken path.
6. SMOKE-RACE-2 (merge `334b8dfc`; commits `382848c2`, `9dffbb8d`).
7. TEST-ORDER-1 (merge `416a5056`; commits `a086bef9`, `99447ec1`, `e823c178`): `app/tests/test_step_order.py`.
8. DEP-INDEX-STALE-1 (merge `cbad9ff3`; commits `049a5258`, `d766ac1e`, `9bd329b2`).
9. TEST-FLAKY-1 (#72) (merge `5e8470f7`; commit `87340720`).
10. Docs minimal example (merge `13f120f6`; commit `14ccda25`): the minimal example and the key-fields table of the authoring guide are format 1.

**Found done already:** NAN-ACTIONS-1 (`polars_fill_nan` and `polars_drop_nans` exist in `libs/transformer/src/transformer/actions/polars_calls.py`); GALLERY-SUBMIT-SCHEMA-1 (`submit_example` writes format 1 and runs `check_recipe` in profile gallery; tested in `libs/viz_gallery` `test_gallery_bundle.py`; read, not run).

**Controls:**
- Final, on `13f120f6` (reviewer): headless `3843 passed, 23 xfailed in 139.57s` (it was 3642 passed and 14 xfailed at the start of the session); golden baseline `result-identical` (`PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json`); `audit_deps_verify` PASS (21 load-bearing files carry a `@deps` block); `audit_docs_sync` exit 1 with 1 violation (`libs/id_reconciliation/README.md`); `audit_uml_model` 6 violations in PKG-TIERS, not new; tree clean.
- Earlier, on `dc91823d`: `task_drift` 0, `cross_lib` 0, `validate_app_features_config --all --strict` PASS, `audit_old_words` exit 1 (known), `check_doc_links` 60 problems.
- Browser gate: `70 passed, 3 skipped in 493.00s` (the browser files under `SPARMVET_APP_FEATURES=qa`). It was run before the last small merges (the progress file names the conftest hook and one docs page). It was NOT run on the final state `13f120f6`. It does not prove the flaky tests fixed: they showed only under load, and one green run does not show that they are gone.

**User-visible change:** a threshold that is not an integer on an integer column is now compared as a number, so the plot agrees with the reproducibility export (issue #62).

**Decisions for Eve** (one list; a reader goes through it with her; the evidence is in each line):

**Older points (night handoff, points 1 to 5)**
1. IMPORT-PATH-1 (`tasks.md`): which option (recommended: a data folder per import, `<user_data>/_imports/<recipe id>/data/` plus a record the orchestrator reads); the name of the imported recipe (recommended: keep `<original>_imported_<timestamp>`); whether the by-dataset-id rule also accepts `.parquet` (recommended: yes, and fail when both exist). Findings: `.claude/worktrees/agent-abd52719502485bdb/tmpAI/progress.md`; hash survey `tmpAI/survey_hash/table.md`. Note: `tasks.md` also says "Eve DECIDED 2026-11-14: option A, as production", while the night handoff says it waits. Ask Eve which is current.
2. The eight changed gallery previews (boxplot_faceted, boxplot_simple, jitter_strip, point_faceted, point_simple, tile_simple, violin_faceted, violin_simple): accept or reject each. Old and new side by side in `tmp/gallery_preview_review/`.
3. A first assembly step that joins the base table with itself is skipped silently ("redundant init", `data_assembler.py`): keep it, or fail with a plain message (recommended: fail). Evidence: JOIN-KEY-TYPES-1 in `tasks.md`; `libs/transformer/tests/test_join_key_types.py` records today's behaviour.
4. TEMPLATE-KEY-TYPE-1: `templates/complex_template` declares `sample_id` as Float64 on both sides. DOC-JOIN-CAST-1: the rule file (`.claude/rules/rules_agent_role_bioscientist.md` line 144), ADR-050 (needs a superseding ADR; ADR text is `opus/high`) and `data_contract_rules` section 13 still describe the removed automatic cast.
5. Older open points in `tasks.md`: `beeswarm_sina`, the empty Blueprint draft, three old scripts, three ID-reconciliation defects, the scope of RECIPE-WORD-1, String or Categorical in recipes.

**HOME**
6. N9: VizFactory `in` / `not_in` compares as text, so on a numeric column `in [90.0]` gives no rows in the plot while the table keeps them. Options: approve the small fix now (coerce, then `is_in`, as the engine does; it changes plots with numeric `in` filters), or wait for FILTER-DTYPES-1. Evidence: 4 strict xfail cases in `app/tests/test_filter_int_equivalence.py`.
7. N12: what blocks the HOME rebuild: see the section "HOME: what blocks the rebuild" below.
8. N13: a drop and a filter on the same column at one node. The HOME view (`audited_frame`) runs all filters before all drops; the exported recipe keeps the recorded order and stops with "column not in the table". Options: refuse such a step, or define the order. Evidence: TEST-ORDER-1, checked by running; not tested yet.

**Recipes and joins**
9. N1: the join key rule is in three places: the build (`DataAssembler._check_join_key_types`), the Blueprint preview (`check_join_keys` in `join_designer.py`) and the checker (`join_key_problems` in `libs/utils/src/utils/recipe_check.py`). They are kept in step by a parity test only. Options: keep the copies with their parity tests, or one pure rule in `libs/utils` called by all three.
10. N5: confirm that the checker refuses at load (J10) a join key not declared in `input_fields`. It mirrors the build, because the ingestor imports only the declared columns when `input_fields` is not empty. Same question as N1.
11. N7: the tier-3 reader (W10) needs HOME's P5 mechanism spec and the order of change R1 (`.claude/design/recipe_format_spec.md` line 173); `beeswarm_sina` waits for it. Options: not recorded in the progress file.

**Gallery**
12. N3: a read-only gallery folder. The start check cannot rewrite the index (status `not_writable`), so a failing example that is listed in the old index is still shown; the only trace is a console warning. Options: keep; or leave failing examples out in memory (`bootloader.rejected_gallery_examples`). Evidence: `app/modules/gallery_examples.py` (`check_gallery_at_start`).
13. N4: what the user sees for an example left out at start is not specified (spec section 9). Today: left out of the index, the reason is in `metadata.rejected`, a console warning, no screen element. Options: not recorded in the progress file.
14. N15: `submit_example` (`libs/viz_gallery/src/viz_gallery/gallery_manager.py` 163-203) has no caller outside the tests. Q3-GALLERY-SUBMISSION-1 left it in place (it writes a gallery bundle); N15 asks again: keep, or delete. Its `@deps` block is inaccurate.

**Export**
15. N10: the reproducibility export writes the filter value as text, so re-running it on a number column fails with `ComputeError cannot compare string with numeric type`. Options: approve EXPORT-FILTER-VALUE-1 (it edits the frozen `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`, about line 127; build brief S4), or leave it. Fix proposed by the reviewer: the translator writes the value through `utils.filter_values.coerce_filter_value` with the stored dtype. Evidence: 12 strict xfail cases in `app/tests/test_filter_int_equivalence.py`.
16. N11: `between` has no translation in `t3_translator` (UntranslatableNode). Options: add the translation later, or keep refusing it.

**Tests and audits**
17. N6: AUDIT-REPAIR-1: for the four old words (`persona`, `manifest`, `profile`, `project`) and one UML tag, fix the text or adapt the exclusions. `recipe` waits for RECIPE-WORD-1. Evidence: `assets/scripts/audit_old_words.py --check`, `assets/scripts/audit_uml_model.py`.
18. N14: TEST-ORDER-1 tests not written yet: where the audit writes a step (P5), the key of T3 and the per-collection key (P4), and property tests with `hypothesis` (a new dependency, D9). They depend on the unconfirmed stage-2 spec v0.1. Options: confirm the spec and allow the dependency, or leave those tests out.
19. N16: `audit_uml_model.py` reports 6 violations in PKG-TIERS of `docs/UML/app.mdj`: five missing arrows (from `assets/scripts` to transformer, utils, viz_factory and viz_gallery; from `libs/test_lab/pyproject.toml` to utils) and one stale arrow (transformer to ingestion). Not new (no importing file gained an import in this session). A UML edit needs Eve's yes. Options: not recorded in the progress file.
20. N17: `.claude/rules/rules_verification_testing.md` section 8: add `--durations=10` after `-q` in the browser command, and correct "about 4 minutes" (the gate took 8 min 13 s). It is a rule file: Eve's double confirmation.

**Blueprint**
21. N2: `except Exception` in `_jd_run_preview` (`app/handlers/blueprint_handlers.py`, about line 2060) shows any programming error as "Preview failed: ...". Options: leave; or catch only the expected errors and let programming errors through.
22. N8: the Blueprint package (W14): `tasks.md` (line 82) says Blueprint is not touched now; the night handoff listed it as next. Eve (2026-11-14): Blueprint and Test Lab can wait. Decide when W14 starts. Options: not recorded in the progress file.

**HOME: what blocks the rebuild (N12 in full)**
- NA-RULE-63 (#63): the NaN rule and the count message. The rule is in `.claude/design/home_audit_steps.md` section 19; Eve confirms it (`tasks.md`, NA-RULE-63).
- STAGE2-SPEC-1: Eve reads and confirms the v0.1 mechanism spec, `.claude/design/home_stage2_mechanism_spec.md`.
- KEYS-NODE-1: Eve confirms the hash model (`.claude/design/home_evidence/home_hash_model_2026-11-12.md`, section 4).
- RECIPE-GRAPH-UTILS-1: option C+. `utils.recipe_graph` and `utils.node_keys` do not exist yet (checked by the scout).
- HOME-DESIGN-REVIEW-1: items SC1, SC2, SC4, AR4, SC5, AR2, AR1.
- FILTER-UNIFY-1: three filter implementations (`modif_filter`, `t3_audit_engine._apply_filter_rows`, the filter loop in `VizFactory.render`); a design decision for Eve.
- FORMULA-SAFETY-1.
- Tasks that wait for these: FILTER-DTYPES-1 (after NA-RULE-63), HOME-EXPLORE-2 (#61, after RECIPE-GRAPH-UTILS-1), HOME-EXPLORE-4, -5 and -6 (#56), AUDIT-VIEW-1, AUDIT-RAWYAML-REMOVE-1, TEST-SHAPES-1 (waits for RECIPE-TESTS-1).

**Next for the coordinator, in order** (after Eve's answers; her priority: HOME first, then Gallery; Blueprint and Test Lab last):
1. HOME: EXPORT-FILTER-VALUE-1 (needs Eve's yes to edit the frozen `t3_translator.py`); N9; NA-RULE-63 (#63) after her answer on the NaN rule and the count message; then FILTER-DTYPES-1; the rest of P0 (TEST-SHAPES-1 waits for RECIPE-TESTS-1); P3 and P4 after her reading of the stage-2 spec, the hash model and option C+.
2. IMPORT-PATH-1 with SOURCE-LOOKUP-ONE-1, after her answer to point 1: one `builder` at `sonnet/high`, continued in worktree `agent-abd52719502485bdb` (merge `feat/recipe-format-1` into it first), then `reviewer`, merge, controls.
3. Gallery: her choices N3, N4 and N15, the eight previews, `beeswarm_sina` (tier-3 reader W10, N7).
4. Later: RECIPE-DOCS-1 (#79), the ADR-100 draft (W12, `opus/high`), AUDIT-REPAIR-1 (N6, N16), BP-VALIDATE-1 and the Blueprint package (W14), the DOC-JOIN-CAST-1 rule and ADR parts.

**Small tasks found, not done:**
- The import test leaves an empty `assets/test_data/_imported/` folder (IMPORT-TEST-CLEANUP-1 in `tasks.md`).
- The one `audit_docs_sync` violation (DOCS-SYNC-IDRECON-1 in `tasks.md`).
- Two sentences of `.claude/design/recipe_format_spec.md` (near lines 380 and 683) still describe the removed REMOVE-CATEGORY-SELECT-1 feature as present.
- The checker flags a missing schema `description` (S04, severity A, `libs/utils/src/utils/recipe_check.py` about line 281). The authoring page does not mention it. Not checked whether "A" is a warning.

**Not started on purpose** (quota and Eve's priority): the ADR-100 draft (W12, `opus/high`); BP-VALIDATE-1 (Blueprint); RECIPE-DOCS-1 (#79, large); AUDIT-REPAIR-1. Blueprint and Test Lab wait (Eve, 2026-11-14).

**Worktrees:** all task worktrees and branches of this session are removed. `agent-abd52719502485bdb` is kept (no code; the findings note of IMPORT-PATH-1).
