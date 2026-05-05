# UI Test Log — 2026-05-02

**Tester:** @evezeyl
**Branch:** dev (Phase 25 baseline)
**Protocol ref:** [tasks_test_ui_current.md](../../../.claude/tasks/tasks_test_ui_current.md)

---

## Test results

| Section | Item | Status | Notes |
|---|---|---|---|
| 0 | App starts cleanly | | |
| 0 | No red banners on load | | |
| 0 | Correct persona confirmed in terminal | | |
| 1a | pipeline-static: no manifest selector | | |
| 1a | pipeline-static: no T3 tier | | |
| 1a | pipeline-static: no right sidebar panel | | |
| 1a | pipeline-static: no Gallery / Blueprint nav | | |
| 1a | pipeline-static: filter panel shows static message | | |
| 1b | pipeline-exploration-simple: interactive filters | | |
| 1b | pipeline-exploration-simple: no T3 tier | | |
| 1b | pipeline-exploration-simple: no Gallery | | |
| 1c | project-independent: manifest selector visible | | |
| 1c | project-independent: Gallery nav visible | | |
| 1c | project-independent: Blueprint Architect nav visible | | |
| 1c | project-independent: T3 tier in toggle | | |
| 1c | project-independent: right sidebar audit panel visible | | |
| 1c | project-independent: Session Management visible | | |
| 1c | project-independent: Single Graph Export visible | | |
| 1c | project-independent: Test Lab NOT visible | | |
| 1d | developer: Test Lab visible | | |
| 2 | Manifest Choice accordion: opens/collapses | | |
| 2 | Manifest Choice: project change reloads plots | | |
| 2 | Data Import accordion: opens/shows import UI | | |
| 2 | Filters accordion: opens with filter builder | | |
| 2 | Global Project Export accordion visible | | |
| 2 | Single Graph Export accordion visible | | |
| 2 | Session Management accordion visible | | |
| 2 | Accordion panels independent (opening one doesn't close others) | | |
| 2 | Persona name shown below nav pills | | |
| 3 | Tabs match analysis groups in manifest | | |
| 3 | Each tab loads plots without traceback | | |
| 3 | Sub-tabs navigate between plots | | |
| 3 | Plot renders as static image | | |
| 3 | Data Preview shows ~100 rows | | |
| 3 | Data Preview updates on sub-tab switch | | |
| 3 | Thin header strip shows dataset label + tier toggle | | |
| 4a | T1→T2: plot/preview update or remain identical | | |
| 4a | T1→T2: no flickering in terminal | | |
| 4b | T1→T3: Apply button label changes to ➜ Audit | | |
| 4b | T1→T3: right sidebar shows Pipeline Audit | | |
| 4c | Tier toggle stability: plot sub-tab unchanged (STATE-1) | | |
| 4c | Panel switch doesn't reset tier toggle (STATE-1/2) | | |
| 5a | Filter string column: correct operators shown | | |
| 5a | Filter string: between NOT shown for string | | |
| 5a | Filter string: Add → staged row appears | | |
| 5a | Filter string: Apply → data preview filtered | | |
| 5a | Filter string: plot updates | | |
| 5a | Filter string: Reset clears filter | | |
| 5b | Filter numeric: between operator present | | |
| 5b | Filter numeric between: two inputs (lo/hi) shown | | |
| 5b | Filter numeric between: range applied correctly | | |
| 5b | Filter numeric: operator persists on same column (UX-FILTER-1) | | |
| 5b | Filter numeric: operator resets on column change | | |
| 5c | Two staged rows: Apply applies AND logic | | |
| 5c | Remove one row: count updates, Apply applies remaining | | |
| 6 | T3 filter non-key: propagation modal opens | | |
| 6 | T3 filter non-key: no PK warning banner | | |
| 6 | T3 filter non-key: "This plot only" scoping works | | |
| 6 | T3 filter non-key: pending node + yellow reason input | | |
| 6 | T3 filter non-key: reason required for Apply | | |
| 6 | T3 filter non-key: Apply confirms with notification | | |
| 6 | T3 filter non-key: other plot unaffected | | |
| 7 | T3 PK filter: PK warning banner in modal | | |
| 7 | T3 PK filter: "All plots" → node icon is 🚫 Exclusion | | |
| 7 | T3 PK filter: node appears in all plots | | |
| 7 | T3 PK filter: Apply removes sample from all plots | | |
| 8 | T3 "All plots except": QC plot excluded from node | | |
| 8 | T3 "All plots except": QC plot still shows sample after Apply | | |
| 9a | Drop non-key column: Audit drops button activates | | |
| 9a | Drop non-key column: modal no PK warning | | |
| 9a | Drop non-key column: Apply removes column from this plot only | | |
| 9b | Drop PK column: blocked with red notification | | |
| 9b | Drop PK column: no node added | | |
| 10 | Node deletion: 🗑 removes node from all plots | | |
| 10 | Node deletion: data reverts | | |
| 11 | Blueprint Architect nav: TubeMap renders | | |
| 11 | Blueprint Architect: right sidebar → "Blueprint Surgeon" | | |
| 11 | Blueprint Architect: node click updates right sidebar | | |
| 11 | Return to Home: right sidebar → "Pipeline Audit" | | |
| 12 | Gallery nav: recipe browser loads | | |
| 12 | Gallery: left sidebar shows Discovery Mode message | | |
| 12 | Gallery: filter sidebar works | | |
| 12 | Gallery: card click loads preview | | |
| 12 | Return to Home: plots and left sidebar restore | | |
| 13 | Comparison mode toggle visible in T3 | | |
| 13 | Comparison mode: layout changes to two-panel | | |
| 13 | Comparison mode: toggle off restores single panel | | |
| 13 | AUDIT-4: compare toggle loses state on plot switch? | | |
| 14 | Session Management: ghost auto-save (2 min) | | |
| 14 | Session Management: restore button reloads nodes | | |
| 15 | Global Export: bundle downloads / path reported | | |
| 16 | Single Graph Export: PNG/SVG downloads | | |
| 17 | STATE-1: plot flickers on tier toggle? | | |
| 17 | STATE-2/AUDIT-4: compare toggle switches plot? | | |
| 17 | UX-1: plot rendering speed (note seconds) | | |
| 17 | UX-2: column multiselect narrower than panel? | | |
| 17 | BUG-PERF-1: repeated materialize_tier1 in terminal? | | |
| 18 | Cancel modal: no node added | | |
| 18 | ➜ Audit (0): disabled or notification shown | | |
| 18 | Two filters same column: independent nodes | | |
| 18 | Schema-skip propagation: skipped plots mentioned in notification | | |

---

## Problems and change requests

| # | Section | Severity | Description | Expected | Actual |
|---|---|---|---|---|---|
| | | | | | |

**Severity:** `bug-critical` | `bug-minor` | `ux` | `change-request` | `question`

---

## Summary

- Date tested:
- App start time (from terminal):
- Persona used:
- Test data (manifest/project):
- Passed: / Total:
- Blockers:
- Notes:
