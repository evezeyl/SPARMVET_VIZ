# Audit Report: Three-Source Persona Consistency (Routine 19)
Generated: 2026-05-21
Status: WARNING — 7/8 personas PASS (all warnings are documentation gaps; no runtime failures)

All ADR-077 fatal cascade rules satisfied. App starts cleanly for all 8 personas.

## Per-Persona Results

- **pipeline-static** [PASS] — fully consistent across all 3 sources
- **pipeline-exploration-simple** [PASS with NOTE] — `interactivity_enabled: true` consistent in template and rules matrix; `persona_capability_matrix.md` has no explicit row for it (reconstructable from other flags — doc gap only)
- **pipeline-exploration-advanced** [PASS] — fully consistent; `audit_report_enabled: true` in all 3 sources
- **project-independent** [PASS] — fully consistent; `blueprint_agent_enabled: false` with `blueprint_enabled: true` correct
- **developer** [PASS] — fully consistent; Phase 33 ADR-076 `blueprint_agent:` block verified (`backend: claude_cli`, all required keys present)
- **qa** [PASS] — `blueprint_agent_enabled: true` with `backend: disabled` correct (exercises panel without live backend); `ghost_save.enabled: false` matches design
- **demo-vetinst** [PASS] — consistent on feature flags; undocumented `ui_banner:` block (branding only)
- **web-demo** [PASS] — consistent; `ui_banner:` block undocumented

## Cross-Source Findings (non-blocking)

| # | Severity | Finding |
|---|---|---|
| 1 | WARNING | `wrangle_studio_enabled` in all 8 templates but absent from rules matrix and design doc |
| 2 | WARNING | `persona_capability_matrix.md` has no explicit `interactivity_enabled` row |
| 3 | WARNING | `ui_banner:` block in demo-vetinst and web-demo templates is undocumented in rules |
| 4 | WARNING | `data_import_panel_visible` in templates but absent from rules matrix — unclear if superseded by ADR-073 sidebar slot registry |
| 5 | INFO | `show_persona_badge`, `manifest_selector.visible`, `ghost_save.enabled` in templates but absent from rules matrix |
| 6 | PASS | All ADR-077 fatal cascades clean — no `blueprint_agent_enabled: true` with `blueprint_enabled: false` |
| 7 | PASS | `blueprint_agent:` config block present only in developer and qa templates — correct per spec |

## Action Items

- [ ] Add `wrangle_studio_enabled` row to `rules_persona_feature_flags.md` flag matrix
- [ ] Add `interactivity_enabled` row to `persona_capability_matrix.md`
- [ ] Clarify `data_import_panel_visible` status (superseded by ADR-073?)

## References
- `.claude/rules/rules_persona_feature_flags.md` — authoritative flag matrix
- `.claude/design/persona_capability_matrix.md` — design intent
- `config/ui/templates/*_template.yaml` — declared values per persona
- Routine 19 in `.claude/workflows/audit_routine_registry.md`
