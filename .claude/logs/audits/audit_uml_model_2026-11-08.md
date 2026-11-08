Status: PROCESSED 2026-11-08 — 0 tasks created, 0 false positives skipped, 0 acceptable debt noted (PASS, re-verified as part of issue #32's closure; audit_task_drift.py and audit_changelog_sync.py specifically mutation-tested, not just read)
# Audit Report: UML Model vs Code
Generated: 2026-11-08T20:05:47
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Model file: docs/UML/app.mdj
Rule: every code/test/adr/flag/status tag in the model resolves against the repository (.claude/design/uml_model_plan.md section 5)

- Elements with tags: 220
- code tags checked: 143
- test tags checked: 11
- adr tags checked: 52
- rule tags checked: 12
- flag tags checked: 37
- status tags checked: 219
- PKG-TIERS packages scanned: 11, model edges: 19, live-import edges: 19
- Violations: 0

## Result: ✅ PASS

No discrepancy found between the model and the repository.

## References
- `.claude/design/uml_model_plan.md` section 5 — the discrepancy checks this audit implements
- `.claude/tasks/uml_findings.md` — differences found between the model and the repository