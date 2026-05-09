# Handoff — Active State (2026-05-09)

**Branch:** dev  
**Last commit:** `4acfc59` feat: implement build_plot_lineage and get_plot_ids_in_group functions with tests  
**Active agent:** @dasharch  

---

## Current State

**Major work completed 2026-05-09:**
- ADRs 073–076 authored (Sidebar Slot Registry, Lineage Infrastructure, BLUEPRINT IDE Build Mode, AI Agent Helper)
- Phase 31 (Sidebar + Export Provenance): SIDEBAR-CONFIGS-1, SIDEBAR-REGISTRY-1, SIDEBAR-VALIDATE-1 **complete** ✅
  - 8 new sidebar YAML configs + slot registry + validator + CLI gate
  - All 8 persona templates updated with `workspaces:` section
  - Tests: `validate_persona_config.py --all` → 8/8 PASS
- Phase 31 export work partially done: LINEAGE-NAV-1, LINEAGE-EXPORT-1, BP-SCHEMA-1 **complete** ✅
  - `build_plot_lineage()` and `get_plot_ids_in_group()` implemented in `libs/blueprint_arch/manifest_navigator.py`
  - 19 transformer actions + 7 viz_factory components annotated with `ui_schema` kwarg
  - 2 verification tasks (SCHEMA-VERIFY-ACTIONS-1, SCHEMA-VERIFY-GEOMS-1) **complete** ✅
- 4 export export tasks still open: EXPORT-HASH-2, EXPORT-VERSION-1, EXPORT-IMG-META-1, EXPORT-AUDIT-COMPLETE-1

**In-depth audit completed (read-only, no code changes):**
- `audit_in_depth_state_2026-05-09.md`: 4 CRITICAL, 6 HIGH, 12 MEDIUM, 10 LOW findings
- All findings verified by manual grep before task creation
- 17 new audit-derived tasks written to `tasks.md` (P0/P1/P2 buckets)

**App health:** 97 unit tests pass; app imports cleanly; no data corruption risk.

---

## Known Blockers

1. **ADR-045 Two-Category Law violations** (CRITICAL)
   - 4 files in `app/modules/` have `from shiny import` — breaks headless-reuse promise
   - Affects: `wrangle_studio.py`, `gallery_viewer.py`, `test_lab_studio.py`, `help_registry.py`
   - Task: ADR045-REFACTOR [opus/high]

2. **ADR-075 manifest_edit_enabled flag absent** (CRITICAL)
   - Flag is in rules but not in any of the 8 templates or bootloader
   - Task: BP-FLAG-1 [haiku/low] — implement first; unblocks downstream form work

3. **ADR-076 AI Agent Helper — no MVP scope** (CRITICAL scope risk)
   - 10 implementation tasks are open with no MVP carve-out
   - Risk: feature could absorb 4–6 weeks without boundaries
   - Task: AUDIT-ADR076-MVP [opus/medium] — define 1-page MVP-1 spec

---

## Next Immediate Steps (Priority order)

**P0 (5–15 min each, do all today):**
- ✅ AUDIT-DEPGRAPH-NOW — done
- AUDIT-HANDOFF-UPDATE — doing now
- AUDIT-RULES-FLAGS-UPDATE — update rules table + mark 25-O done
- AUDIT-ADR072-STUB — insert ADR-072 + sort ADR-069
- AUDIT-QUALITY-WRANGLING — convert/delete empty wrangling file
- AUDIT-PHANTOM-TEST — fix phantom test reference

**P1 (30 min each, do next):**
- AUDIT-CHANGELOG-UPDATE — backfill Phases 28/29/31/32 + ADRs 066–076
- AUDIT-WRANGLE-FLAG — add wrangle_studio_enabled to validator + all templates
- AUDIT-DEMO-PERSONAS — document demo personas in flag matrix
- AUDIT-ABROMICS-CHECK — verify data source count
- AUDIT-PLAN-ORDER — sort implementation_plan_master.md chronologically

**Then — P2 (1 session each):**
- AUDIT-SGE-CLEANUP [sonnet/low] — remove orphaned SGE code
- AUDIT-NOTIF-UTIL-MOVE [haiku/low] — move notification_utils.py to modules/
- AUDIT-CSS-SWEEP [sonnet/medium] — move 101 inline styles to theme.css
- AUDIT-PLASMID-VERIFY [sonnet/low] — verify Plasmid Dynamics lineage
- AUDIT-SERVER-SLIM [sonnet/medium] — extract helpers from server.py
- AUDIT-ADR076-MVP [opus/medium] — **critical** — define MVP-1 before impl

**Phase 32 proper work (after P0/P1/P2):**
- BP-FLAG-1 [haiku/low] — highest priority; unblocks all form work
- BP-FORMS-1 [sonnet/high]
- BP-ESCAPE-1 [sonnet/medium]
- (other BP-* tasks — lower priority)

---

## Reference

- Full audit: `.claude/logs/audits/audit_in_depth_state_2026-05-09.md` (§1–7 findings + recommendations)
- Design decisions: `.claude/knowledge/architecture_decisions.md` (ADRs 073–076 source of truth)
- Task list: `.claude/tasks/tasks.md` (17 new audit-derived tasks added)

---

**Handoff author:** Audit session 2026-05-09  
**Next agent:** Start P0 tasks; refer to audit for full context
