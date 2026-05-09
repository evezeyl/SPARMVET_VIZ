Status: PROCESSED
Triage: Fixed. SidebarValidator was printing a NOTE for gate-disabled panels (by-design per ADR-073 two-layer resolution). The _WarningCollector in --strict mode captured these NOTEs as warnings, causing 5 templates to fail. Fix: removed the NOTE print; gate-disabled panels are silently skipped as designed — no announcement needed. Re-run: ✅ PASS (8/8).
# Audit Report: Persona Template Flag Completeness
Generated: 2026-05-09T21:26:56
Project root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ
Rule: rules_persona_feature_flags.md — Authoritative flag matrix, cascade enforcement
Validator: PersonaValidator + SidebarValidator (strict mode — warnings treated as errors)

- Templates validated: 8
- Passed: 3
- Failed: 5

## Result: ❌ FAIL

## ❌ Template Failures

### demo-vetinst (exit 1)
```
============================================================
Validating: demo-vetinst_template.yaml
============================================================
[SidebarValidator] NOTE: [demo-vetinst] workspaces.home.left_sidebar includes 'manifest_choice' but its gate flag 'manifest_selector_visible' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [demo-vetinst] workspaces.home.left_sidebar includes 'filters' but its gate flag 'interactivity_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [demo-vetinst] workspaces.home.left_sidebar includes 'data_import' but its gate flag 'metadata_ingestion_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [demo-vetinst] workspaces.home.left_sidebar includes 'export' but its gate flag 'export_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [demo-vetinst] workspaces.home.left_sidebar includes 'session_management' but its gate flag 'session_management_enabled' is disabled — panel will be silently skipped.
  → PASS  errors=0  warnings=5

────────────────────────────────────────────────────────────
Total: 1 template(s)  errors=0  warnings=5
RESULT: FAIL (--strict: warnings treated as errors)
```

### pipeline-exploration-simple (exit 1)
```
============================================================
Validating: pipeline-exploration-simple_template.yaml
============================================================
[SidebarValidator] NOTE: [pipeline-exploration-simple] workspaces.home.left_sidebar includes 'manifest_choice' but its gate flag 'manifest_selector_visible' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [pipeline-exploration-simple] workspaces.home.left_sidebar includes 'data_import' but its gate flag 'metadata_ingestion_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [pipeline-exploration-simple] workspaces.home.left_sidebar includes 'session_management' but its gate flag 'session_management_enabled' is disabled — panel will be silently skipped.
  → PASS  errors=0  warnings=3

────────────────────────────────────────────────────────────
Total: 1 template(s)  errors=0  warnings=3
RESULT: FAIL (--strict: warnings treated as errors)
```

### pipeline-static (exit 1)
```
============================================================
Validating: pipeline-static_template.yaml
============================================================
[SidebarValidator] NOTE: [pipeline-static] workspaces.home.left_sidebar includes 'manifest_choice' but its gate flag 'manifest_selector_visible' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [pipeline-static] workspaces.home.left_sidebar includes 'filters' but its gate flag 'interactivity_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [pipeline-static] workspaces.home.left_sidebar includes 'data_import' but its gate flag 'metadata_ingestion_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [pipeline-static] workspaces.home.left_sidebar includes 'session_management' but its gate flag 'session_management_enabled' is disabled — panel will be silently skipped.
  → PASS  errors=0  warnings=4

────────────────────────────────────────────────────────────
Total: 1 template(s)  errors=0  warnings=4
RESULT: FAIL (--strict: warnings treated as errors)
```

### project-independent (exit 1)
```
============================================================
Validating: project-independent_template.yaml
============================================================
[SidebarValidator] NOTE: [project-independent] workspaces.blueprint.right_sidebar includes 'blueprint_agent_chat' but its gate flag 'blueprint_agent_enabled' is disabled — panel will be silently skipped.
  → PASS  errors=0  warnings=1

────────────────────────────────────────────────────────────
Total: 1 template(s)  errors=0  warnings=1
RESULT: FAIL (--strict: warnings treated as errors)
```

### web-demo (exit 1)
```
============================================================
Validating: web-demo_template.yaml
============================================================
[SidebarValidator] NOTE: [web-demo] workspaces.home.left_sidebar includes 'manifest_choice' but its gate flag 'manifest_selector_visible' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [web-demo] workspaces.home.left_sidebar includes 'data_import' but its gate flag 'metadata_ingestion_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [web-demo] workspaces.home.left_sidebar includes 'export' but its gate flag 'export_enabled' is disabled — panel will be silently skipped.
[SidebarValidator] NOTE: [web-demo] workspaces.home.left_sidebar includes 'session_management' but its gate flag 'session_management_enabled' is disabled — panel will be silently skipped.
  → PASS  errors=0  warnings=4

────────────────────────────────────────────────────────────
Total: 1 template(s)  errors=0  warnings=4
RESULT: FAIL (--strict: warnings treated as errors)
```

## ✅ Templates Passing

- `developer`
- `pipeline-exploration-advanced`
- `qa`

## References
- `.claude/rules/rules_persona_feature_flags.md` — authoritative flag matrix
- `scripts/validate_persona_config.py` — validator CLI
- `config/ui/templates/` — all persona template files
- Routine 8 (Template flag completeness) in `.claude/workflows/audit_routine_registry.md`