---
Status: PROCESSED
Routine: §18 — ADR Compliance
Date: 2026-05-21
---

# Audit Report: §18 ADR Compliance
Generated: 2026-05-21
Rule: ADR-045 (Two-Category Law), rules_verification_testing.md §1

## Summary

- Files inspected: app/handlers/home_theater.py, app/src/server.py, app/handlers/*.py
- ADR violations found: 1
- Fixed this session: 0 (fix tracked as task ADR-045-ANCHOR-SET-1)

## Result: ❌ FAIL (violation found, fix pending)

---

## Findings

### Finding 1 — ADR-045 violation: `reactive.Value.set()` inside `@render.ui`
**File:** `app/handlers/home_theater.py`
**Line:** ~655 (inside `dynamic_tabs` render function)
**Code:** `anchor_path.set(str(out_path))`
**Rule violated:** ADR-045 Reactive Write Discipline Rule R1 — renders are read-only. A `@render.*` function MUST NOT call `reactive.Value.set(...)`.
**Consequence:** Calling `.set()` during a render invalidates downstream readers mid-render, causing Shiny to emit illegal client/server state transitions:
  - "output 'X' is recalculating, but the output is in an unexpected state of: 'idle'"
  - "server has sent a progress message for 'X', but the output is in an unexpected state of: 'running'"
**Fix required:**
  1. Remove `anchor_path.set(str(out_path))` from inside `dynamic_tabs()` render
  2. Extract to a dedicated `@reactive.Effect` with idempotent guard:
     ```python
     @reactive.Effect
     def _sync_anchor_path():
         # compute out_path same way as dynamic_tabs does
         new_val = str(out_path)
         if anchor_path.get() != new_val:
             anchor_path.set(new_val)
     ```
  3. Ensure the effect triggers on the same reactive inputs that drive the path computation.
**Task:** ADR-045-ANCHOR-SET-1 (added to tasks.md)

---

## No Other Violations Found

Scanned all handler files for:
- `reactive.Value.set()` inside `@render.*` functions (Rule R1)
- Shiny imports inside `libs/` (Two-Category Law)
- `sys.path` hacks (rules_runtime_environment.md §3)

Only the one finding above detected.

## References
- `rules_viz_factory.md §4` Reactive Write Discipline (Rule R1–R4)
- `ui_implementation_contract.md §14` — same rules
- `app/handlers/home_theater.py` — violation location
- ADR-045 — Two-Category Law
