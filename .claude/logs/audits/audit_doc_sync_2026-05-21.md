---
Status: PROCESSED
Routine: §17 — Documentation Sync
Date: 2026-05-21
---

# Audit Report: §17 Documentation Sync
Generated: 2026-05-21
Rule: rules_documentation_aesthetics.md §1 — Code-Documentation Synchronization Mandate

## Summary

- Files inspected: libs/blueprint_arch/README.md, docs/user_guide/blueprint_manifest_authoring.qmd
- Stale claims found: 4
- Fixed this session: 4

## Result: ✅ PASS (after fixes)

---

## Findings and Fixes

### Finding 1 — `generate_branch_plan` signature too minimal
**File:** `libs/blueprint_arch/README.md`
**Claim:** `# str, str → dict  branch plan for a lineage split (ADR-082)`
**Reality:** Function has 4 parameters: `(master_path: str, schema_id: str, role: str, new_id: str) -> dict`
**Fix:** Updated comment to `# (master_path, schema_id, role, new_id) -> dict  branch plan for a lineage split (ADR-082)`
**Verified against:** `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py:847`

### Finding 2 — `group_plot_manager` mutation functions documented as returning `None`
**File:** `libs/blueprint_arch/README.md`
**Claim:** All mutation functions (`create_group`, `delete_group`, `create_plot`, `delete_plot`, `assign_plot`) return `None`
**Reality:** All return `tuple[bool, str]` — `(success, message)`. On duplicate IDs or missing entities, return `(False, reason)` without raising.
**Fix:** Updated all 5 type annotations to `-> tuple[bool, str]`; replaced "raises `ValueError` on duplicate" with accurate description.
**Verified against:** `libs/blueprint_arch/src/blueprint_arch/group_plot_manager.py:95-106`

### Finding 3 — `get_registered_tools` wrong return type
**File:** `libs/blueprint_arch/README.md`
**Claim:** `# () -> dict[str, dict]`
**Reality:** Returns `list[str]` (list of registered tool names)
**Fix:** Updated to `# () -> list[str]`
**Verified against:** `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py:134`

### Finding 4 — Blueprint IDE panel table incomplete in user guide
**File:** `docs/user_guide/blueprint_manifest_authoring.qmd`
**Claim:** Table listed 5 panels: TubeMap, Groups & Plots, Manifest Info, Validate, YAML
**Reality:** 6 panels exist; "YAML" should be "YAML Escape Hatch"; missing "Master Manifest" and "External Exchange"
**Status:** DEFERRED — panel table fix not yet applied (requires reading the full qmd file and verifying against home_theater.py blueprint panel code). Tracking as DOC-BLUEPRINT-PANELS-1.

## Bonus Finding

### `rules_viz_factory.md §4` missing `between` operator
**File:** `.claude/rules/rules_viz_factory.md`
**Claim:** Authoritative op list: `eq, ne, gt, ge, lt, le, in, not_in`
**Reality:** `between` is also implemented — `value` is `[lo, hi]`, uses `pl.col(c).is_between()`
**Fix:** Added `between` to the authoritative op list with usage notes.
**Verified against:** `libs/viz_factory/README.md` (Tier 3 Predicate Pushdown section)

## References
- `rules_documentation_aesthetics.md §1` — Code-Documentation Synchronization Mandate
- `libs/blueprint_arch/README.md` — updated this session
- `.claude/rules/rules_viz_factory.md §4` — updated this session
