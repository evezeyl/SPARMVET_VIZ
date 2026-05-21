Status: PROCESSED
Triage: 3 drift findings — 1 expected (DOC-BLUEPRINT-USER-1 pending), 2 false positives (archive file now exists; build_dep_graph path is assets/scripts/ not scripts/). No new tasks added.

# Audit Report: Task-to-Code Drift Check
Generated: 2026-05-21T15:28:31
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Tasks file: .claude/tasks/tasks.md
Rule: Open task file references must point to existing files

- Distinct file paths referenced in open tasks: 8
- Missing files (drift): 3

## Result: ❌ FAIL

## ❌ Drift Violations (file referenced but not found)

### `docs/user_guide/blueprint_manifest_authoring.qmd` (task line 61)
- Task: `- [ ] **DOC-BLUEPRINT-USER-1** `[sonnet/medium]`: Write `docs/user_guide/blueprint_manifest_authoring.qmd` — user-facing`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

### `.claude/tasks/tasks_archive_phase33.md` (task line 71)
- Task: `- [ ] **TASK-ARCHIVE-1** `[haiku/low]`: Archive all completed `[x]` items from Phase 32 and Phase 33 sections in `tasks.`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

### `scripts/build_dep_graph.py` (task line 73)
- Task: `- [ ] **AUDIT-PASS-1** `[sonnet/low]`: Run the full audit suite + test suites and report findings. Steps: (1) `scripts/r`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

## References
- `.claude/tasks/tasks.md` — sole source of truth for current work
- Routine 4 (Task-to-code drift) in `.claude/workflows/audit_routine_registry.md`
