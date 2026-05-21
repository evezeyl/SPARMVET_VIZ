# Task Archive — Documentation & Hygiene Sprint (2026-05-21)

**Archived from:** `tasks.md` — "Documentation & Hygiene Sprint" section  
**Completed:** 2026-05-21  
**Session context:** Pause-build sprint to document everything built in Phases 32–33, run full audits, and clean the task file.

---

## Sprint Context

> **2026-05-21 decision.** Pause building. Document what has been built, run audits, clean task file.  
> Moving `.claude/knowledge/` content into `docs/` is deferred to near-end-of-build.  
> All docs go under `docs/` (user-facing + developer-facing). Each lib also gets its own `README.md`.
>
> **OPUS constraint:** Must verify all claims against actual code before writing. Do NOT invent or extrapolate.  
> Check the file, then describe it. Every claim about a function signature, file path, or behaviour  
> must be confirmed with a `Read` or `grep` before it appears in any doc.

---

## Completed Tasks

- [x] **DOC-BLUEPRINT-1** `[opus/high]` — **DONE 2026-05-21.** `docs/workflows/blueprint_architect.qmd` (9 sections). History: [tasks_archive_phase32.md](tasks_archive_phase32.md).

- [x] **DOC-BLUEPRINT-USER-1** `[sonnet/medium]` — DONE 2026-05-21. `docs/user_guide/blueprint_manifest_authoring.qmd` — user-facing bioscientist guide. Covers: 3-step YAML authoring flow (data_schema → join → plot); form UI vs YAML escape hatch; branching decision guide; validation; when to call for developer help. Examples from `config/manifests/`.

- [x] **DOC-LIBREADME-BLUEPRINT-ARCH-1** `[sonnet/medium]` — DONE 2026-05-21. `libs/blueprint_arch/README.md` updated. Added: `generate_branch_plan` (4-param signature) to manifest_navigator API; `search_components` to schema_registry API; new sections for `group_plot_manager.py` (returns `tuple[bool, str]`), `agent_tools.py`, `agent_tool_parser.py`, `join_designer.py`; updated tests table (4 test files). All claims verified against source code.

- [x] **DOC-LIBREADME-TRANSFORMER-1** `[sonnet/medium]` — DONE 2026-05-21. `libs/transformer/README.md` updated. Added: full action registry table (8 categories, 62 actions verified at runtime); detection-based manifest loading explanation for `debug_assembler.py`. Existing sections verified current.

- [x] **DOC-LIBREADME-VIZFACTORY-1** `[sonnet/medium]` — DONE 2026-05-21. `libs/viz_factory/README.md` updated. Added: ADR-083 canonical plot spec section with `factory_id` removal note and `migrate_plot_specs.py`; five-tier cascade table with `normalise_plot_spec`/`serialise_plot_spec`/`resolve_plot_config` public API; palette injection table.

- [x] **DOC-LIBREADME-OTHERS-1** `[haiku/low]` — DONE 2026-05-21. Verified READMEs for `libs/ingestion/`, `libs/utils/`, `libs/connector/`, `libs/test_lab/`. All four current; no stubs needed.

- [x] **TASK-ARCHIVE-1** `[haiku/low]` — DONE 2026-05-21. Archived all completed `[x]` items from Phase 32 and Phase 33 sections. Archives: [tasks_archive_phase32.md](tasks_archive_phase32.md), [tasks_archive_phase33.md](tasks_archive_phase33.md).

- [x] **AUDIT-PASS-1** `[sonnet/low]` — DONE 2026-05-21. Full audit suite run. Results:
  - Script audits (16 reports): 11 PASS, 2 FAIL (viz_factory suite timeout, docs_sync stale paths), 2 informational, 1 warning. All PROCESSED. New tasks: VIZFAC-SUITE-TIMEOUT-1, DOC-SYNC-PLATFORM-1, DOC-SYNC-TESTING-1, PERSONA-DATAIMPORT-FLAG-DOC-1.
  - Agent §17 (doc sync): 4 stale claims fixed (group_plot_manager return types, generate_branch_plan signature, get_registered_tools return type, between operator in rules_viz_factory.md). 1 deferred: DOC-BLUEPRINT-PANELS-1.
  - Agent §18 (ADR compliance): 1 violation found — `anchor_path.set()` inside `@render.ui dynamic_tabs()`. Task: ADR-045-ANCHOR-SET-1.
  - Agent §19 (persona consistency): 7/8 PASS. 3 doc gaps logged: PERSONA-DATAIMPORT-FLAG-DOC-1, wrangle_studio_enabled (already in rules matrix — false positive), data_import_panel_visible.
  - Playwright smoke tests: 26/26 pass (3 persona-skipped expected).
  - Dep graph regenerated: 134 nodes, 259 edges.

---

## User Required — Resolved

- [x] **BP-ADR-FULL-1** (ADR-082) — **RESOLVED 2026-05-20.** All 7 BLUEPRINT decision points settled with Eve; **ADR-082 (BLUEPRINT Full Feature Set & Build-Mode Contract)** authored in `architecture_decisions.md`. Research draft marked RESOLVED. Spawned Phase 32 (cont.) task slate.
