Status: PROCESSED
Triage: All 5 missing-file references resolved. DEPLOY-CONNECT-1 → deferred; TECH-T3-THREAD-1 → correct file ref and status updated; PYPROJECT-DEPS-1 → glob pattern fixed; ACTION-RENAME-1 → clarified (migrate_manifests.py never existed in git); CODE-DOCS-RETROSPECTIVE → split into CODE-COMMENT-STANDARD (active) + CODE-DOCS-RETROSPECTIVE (deferred). No code changes needed.
# Audit Report: Task-to-Code Drift Check
Generated: 2026-05-09T21:26:57
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Tasks file: .claude/tasks/tasks.md
Rule: Open task file references must point to existing files

- Distinct file paths referenced in open tasks: 13
- Missing files (drift): 5

## Result: ❌ FAIL

## ❌ Drift Violations (file referenced but not found)

### `config/deployment/connect/connect_profile.yaml` (task line 31)
- Task: `- [ ] Deployment profile via `SPARMVET_PROFILE` env var; add `config/deployment/connect/connect_profile.yaml` template.`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

### `.claude/tasks/design_sge_lineage_t3.md` (task line 118)
- Task: `- [ ] **TECH-T3-THREAD-1** `[sonnet/medium]`: When new T3 node types are added, thread them through `_apply_t3_to_lf`. D`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

### `libs/*/pyproject.toml` (task line 141)
- Task: `- [ ] **PYPROJECT-DEPS-1** `[haiku/low]` `[repo-hygiene]`: Verify all 8 `libs/*/pyproject.toml` files declare `libs/util`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

### `scripts/migrate_manifests.py` (task line 142)
- Task: `- [ ] **ACTION-RENAME-1** `[sonnet/medium]` `[repo-hygiene]`: Audit `@register_action` and `@register_plot_component` na`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

### `scripts/audit_code_quality.py` (task line 144)
- Task: `- [ ] **CODE-DOCS-RETROSPECTIVE** `[deferred — pre-deployment review sprint]`: Developer-level docstrings across all `li`
- **Fix options:**
  - If the file was renamed/moved: update the task to reference the new path.
  - If the file was deleted: update or close the task.
  - If the file has not been created yet: this is expected — mark task as deferred.

## References
- `.claude/tasks/tasks.md` — sole source of truth for current work
- Routine 4 (Task-to-code drift) in `.claude/workflows/audit_routine_registry.md`