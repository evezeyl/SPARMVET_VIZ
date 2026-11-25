# Audit Report: Documentation and README Sync
Generated: 2026-11-21T17:32:44
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/worktrees/gallery-picture-key
Rule: docs_documentation_aesthetics.md §1 — Code-Documentation Synchronization Mandate

- README coverage violations: 0
- @deps documents: broken links: 2
- Doc backtick path violations: 1
- Violet Law stale references: 0
- Duplicate ADR numbers: 0
- **Total violations: 3**

## Result: ❌ FAIL

## ✅ README Coverage — No violations

## ❌ @deps documents: Links

- **`.claude/rules/rules_agent_channel.md`**
  @deps `documents:` references missing file: `tmpAI/agent_channel.md`
  *Fix: Update the `documents:` entry in the @deps block to point to the correct (current) file path.*
- **`.claude/rules/rules_runtime_environment.md`**
  @deps `documents:` references missing file: `.venv/`
  *Fix: Update the `documents:` entry in the @deps block to point to the correct (current) file path.*

## ❌ Doc Backtick File Paths

- **`libs/viz_factory/README.md`**
  Backtick path not found on disk: `tests/test_theme_slots.py`
  *Fix: Update the file reference in the doc. If the file was renamed, use the new path. If the file was deleted, remove or rewrite the paragraph.*

## ✅ Violet Law Stale References — No violations

## ✅ ADR Numbers — No violations

## References
- `rules_documentation_aesthetics.md §1` — Code-Documentation Synchronization Mandate
- `rules_documentation_aesthetics.md §3` — The Violet Law
- `workspace_standard.md §5` — @deps annotation format
- Routine 9 (Documentation sync) in `.claude/workflows/audit_routine_registry.md`