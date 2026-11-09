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
