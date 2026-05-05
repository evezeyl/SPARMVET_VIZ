# SPARMVET_VIZ: Full Project State Audit
**Date:** 2026-04-30
**Auditor:** @dasharch (Antigravity Agent)

## 1. Executive Summary
The project is advancing well technically, with Phase 21 (Unified Home Theater) and Phase 22 (Session Management & Server Decomposition) marked as completed or in final testing stages in the daily tasks. However, significant documentation drift, status tracker inconsistencies, and a parsing flaw in the automated dependency tooling have emerged. Furthermore, the `home_theater.py` module is rapidly becoming a new monolith, undermining the recent ADR-045 refactor.

## 2. Inconsistencies Between Status Trackers
There are multiple desynchronizations between the high-level roadmap (`implementation_plan_master.md`) and the live execution log (`tasks.md`).

* **Phase 21 (Unified Home Theater) Status:**
  * `implementation_plan_master.md` lists Phase 21-E (Comparison Mode) as DEFERRED, and 21-G / 21-H as PENDING.
  * `tasks.md` lists Phase 21-E as COMPLETED (2026-04-30) and 21-G / 21-H as COMPLETED (2026-04-30).
* **Phase 22 Scope Missing:**
  * `tasks.md` documents an extensive "Phase 22-J: Per-Plot Audit Scoping & Join-Key Propagation" that is completely absent from `implementation_plan_master.md`.
* **Missing Phases:**
  * `implementation_plan_master.md` jumps from Phase 11-A directly to 11-C (11-B is missing).
  * Phases 13, 14, and 15 are completely missing from the master plan sequencing.

## 3. Contradictions in Architectural Decisions (ADRs)
`architecture_decisions.md` contains lingering legacy terms and contradictory statuses.

* **ADR-040 (Bidirectional Lineage Navigation):** 
  * The top-level status claims "PARTIALLY IMPLEMENTED (... 18-D/E/F pending)".
  * However, the detailed bullet points immediately below it explicitly mark 18-D and 18-F as `✅ COMPLETED`.
* **ADR-029a (Dashboard Theater):**
  * Retains references to deprecated state variables (`ref_tier_switch`, `view_toggle`, `is_comparison`). Although ADR-043 formally supersedes this, the inline text in ADR-029a is highly contradictory to current Phase 21 implementations.
* **ADR-006 vs ADR-032 (`assets/scripts/` policy):**
  * ADR-006 is marked DEPRECATED ("Moved to ADR-032").
  * ADR-032 originally mandated the deletion of `assets/scripts/`. However, a clarification (2026-04-24) reversed this, stating `assets/scripts/` is **not deprecated** for user-facing scripts. ADR-006's deprecation note does not reflect this nuance.

## 4. Tooling / Dependency Graph Logic Error
The script `assets/scripts/build_dep_graph.py` contains a parsing flaw that corrupts the dependency graph.
* **Issue:** It blindly parses `@deps` blocks inside markdown code blocks. 
* **Evidence:** In `dependency_index.md`, `.claude/rules/workspace_standard.md` is listed as *providing* `action:cast` and *mirroring* `app/modules/orchestrator.py`. This is because the parser picked up the instructional example inside `workspace_standard.md` section 5-B. The same error occurs for `EVE_WORK/daily/2026-04-24/GEM_CONTEXT_2026-04-24_072114.md`.
* **Impact:** The auto-generated Sync Risk Register is polluted with false positives.

## 5. Architectural Law Drift (The Monolith Returns)
* **Context:** ADR-045 was executed specifically to break up `server.py` (2,362 lines) into focused handler modules due to unmanageable size.
* **Risk:** As noted in `tasks.md` (Task H-4), `app/handlers/home_theater.py` has now bloated to over 1,562 lines. By absorbing the Unified Home Theater logic (Phase 21) and the complex filter/T3 audit state, it is rapidly reproducing the exact monolith problem ADR-045 was designed to solve. 

## 6. Next Steps & Recommendations
1. **Sync Documentation:** Run an `-update-all` equivalent pass to align `implementation_plan_master.md` with `tasks.md`.
2. **Fix Dependency Parser:** Update `build_dep_graph.py` to ignore text within backticks (`` ``` ``) or implement a stricter regex matching rule for valid dependency file headers.
3. **Refactor `home_theater.py`:** Plan a Phase 24 to subdivide `home_theater.py` (e.g., extracting the sidebar filter logic or T3 Recipe management into sub-handlers) before starting Phase 23 (Multi-System Deployment).
