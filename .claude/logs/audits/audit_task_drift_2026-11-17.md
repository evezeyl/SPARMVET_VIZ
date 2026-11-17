Status: PROCESSED 2026-11-17 — 0 tasks created, 1 false positive skipped (the entry AUDIT-LOGS-2026-11-17 names a glob), 0 acceptable debt noted
# Audit Report: Task-to-Code Drift Check
Generated: 2026-11-17T18:48:13
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Tasks file: .claude/tasks/tasks.md
Rule: Open task file references must point to existing files

- Distinct file paths referenced in open tasks: 53
- Missing files (drift): 1

## Result: ❌ FAIL

## ❌ Drift Violations (file referenced but not found)

### `.claude/logs/audits/audit_*_2026-11-17.md` (task line 556)
- Task: `- [ ] **AUDIT-LOGS-2026-11-17** `[sonnet/low]` [records] — eleven untracked `.claude/logs/audits/audit_*_2026-11-17.md` `
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

## References
- `.claude/tasks/tasks.md` — sole source of truth for current work
- Routine 4 (Task-to-code drift) in `.claude/workflows/audit_routine_registry.md`