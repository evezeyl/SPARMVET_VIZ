# Audit Report: UML Model vs Code
Generated: 2026-11-19T00:55:13
Project root: .
Model file: docs/UML/app.mdj
Rule: every code/test/adr/flag/status tag in the model resolves against the repository (.claude/design/uml_model_plan.md section 5)

- Elements with tags: 235
- code tags checked: 158
- test tags checked: 21
- adr tags checked: 52
- rule tags checked: 12
- flag tags checked: 41
- status tags checked: 225
- PKG-TIERS packages scanned: 11, model edges: 19, live-import edges: 22
- Violations: 8

## Result: ❌ FAIL

### PKG_EDGE_MISSING (5)
- `PKG-TIERS`: a live import of 'transformer' exists under assets/scripts, but PKG-TIERS draws no assets/scripts -> transformer arrow
- `PKG-TIERS`: a live import of 'utils' exists under assets/scripts, but PKG-TIERS draws no assets/scripts -> utils arrow
- `PKG-TIERS`: a live import of 'viz_factory' exists under assets/scripts, but PKG-TIERS draws no assets/scripts -> viz_factory arrow
- `PKG-TIERS`: a live import of 'viz_gallery' exists under assets/scripts, but PKG-TIERS draws no assets/scripts -> viz_gallery arrow
- `PKG-TIERS`: a live import of 'utils' exists under libs/test_lab/pyproject.toml, but PKG-TIERS draws no test_lab -> utils arrow

### PKG_EDGE_STALE (2)
- `PKG-TIERS`: model draws assets/scripts -> test_lab, but no live import of 'test_lab' was found under assets/scripts
- `PKG-TIERS`: model draws transformer -> ingestion, but no live import of 'ingestion' was found under libs/transformer/pyproject.toml

### TEST_BROKEN (1)
- `test_audited_rows_and_drops_are_exported` (UMLArtifact): test='app/tests/test_export_view_consistency.py::test_audited_rows_and_drops_are_exported': 'test_audited_rows_and_drops_are_exported' not found in app/tests/test_export_view_consistency.py

**Fix:** update the model element's tag in StarUML to match the repository, or fix the repository if the model is right and the code/docs have drifted. See the findings register `.claude/tasks/uml_findings.md` for the convention.

## References
- `.claude/design/uml_model_plan.md` section 5 — the discrepancy checks this audit implements
- `.claude/tasks/uml_findings.md` — differences found between the model and the repository