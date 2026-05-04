# Persona Capability Matrix
**Last updated:** 2026-05-04  
**Companion guide:** `persona_scoping_guide.md` (abbreviations, group definitions, dependencies)  
**Persona templates:** `config/ui/templates/`

`Y` = enabled | `N` = disabled | `[P]` = proposed (not yet implemented) | `?` = to decide | `-` = N/A | `~` = partial

---

## GROUP: VIEW

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `interactivity_enabled` | N | N | Y | Y | Y | Y | Y | Y |
| `[P] tier_toggle_enabled` | ? | N | ? | Y | Y | Y | Y | Y |
| `[P] default_tier` | ? | T2 | T2 | ? | ? | ? | ? | ? |

---

## GROUP: FILTER (passive — view only, no data change)

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `[P] passive_filter_enabled` | N | N | ? | ? | ? | ? | Y | Y |

> Passive filter = ephemeral, curiosity exploration. Does NOT change data, writes nothing to audit.

---

## GROUP: T3-AUDIT (active — changes data branch, requires justification)

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `t3_sandbox_enabled` | N | N | N | N | Y | Y | Y | Y |
| `comparison_mode_enabled` | N | N | N | N | Y | Y | Y | Y |
| `audit_report_enabled` | N | N | N | N | Y | Y | Y | Y |

> Active filter = creates T3 branch, justification required, written to audit trail. T2 is never modified.

---

## GROUP: SESSION

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `session_management_enabled` | N | N | N | N | Y | Y | Y | Y |
| `ghost_save.enabled` | N | N | N | N | Y | Y | Y | N |

> Session save only meaningful when `t3_sandbox_enabled: true` — see SESSION-PERSONA-1.

---

## GROUP: EXPORT

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `export_bundle_enabled` | Y | N | N | Y | Y | Y | Y | Y |
| `export_graph_enabled` | N | N | N | N | Y | Y | Y | Y |

---

## GROUP: INGEST

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `metadata_ingestion_enabled` | N | N | N | N | Y | Y | Y | Y |
| `import_helper_enabled` | N | N | N | N | N | Y | Y | Y |
| `data_ingestion_enabled` | N | N | N | N | N | Y | Y | Y |
| `data_import_panel_visible` | Y | N | N | Y | Y | Y | Y | Y |

---

## GROUP: DEV

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `gallery_enabled` | N | N | N | N | N | Y | Y | Y |
| `developer_mode_enabled` | N | N | N | N | N | N | Y | Y |
| `wrangle_studio_enabled` | N | N | N | N | N | N | Y | Y |
| test_lab *(derived from dev_mode)* | N | N | N | N | N | N | Y | Y |

---

## GROUP: UI-LAYOUT

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `show_persona_badge` | Y | N | N | Y | Y | Y | Y | Y |
| `manifest_selector.visible` | N | N | N | N | Y | Y | Y | Y |
| `manifest_selector.fixed_manifest` | set | set | set | set | set | null | null | null |
| `ui_branding.title` | - | - | `""` | - | - | - | - | - |
| `ui_branding.subtitle` | - | - | `""` | - | - | - | - | - |
| `[P] show_navigation` | ? | N | N | ? | ? | ? | Y | Y |
| `[P] sidebar_profile` | ? | ? | ? | ? | ? | ? | ? | ? |

---

## Proposed new personas (rows to fill in)

| Flag | web-project-showcase | lightweight-exploration |
|---|:---:|:---:|
| `interactivity_enabled` | N | N |
| `[P] tier_toggle_enabled` | N | N |
| `[P] default_tier` | T2 | T2 |
| `[P] passive_filter_enabled` | N | Y |
| `t3_sandbox_enabled` | N | N |
| `comparison_mode_enabled` | N | N |
| `audit_report_enabled` | N | N |
| `session_management_enabled` | N | N |
| `ghost_save.enabled` | N | N |
| `export_bundle_enabled` | ? | ? |
| `export_graph_enabled` | N | N |
| `metadata_ingestion_enabled` | N | N |
| `import_helper_enabled` | N | N |
| `data_ingestion_enabled` | N | N |
| `data_import_panel_visible` | N | N |
| `gallery_enabled` | N | N |
| `developer_mode_enabled` | N | N |
| `wrangle_studio_enabled` | N | N |
| `show_persona_badge` | N | N |
| `manifest_selector.visible` | N | ? |
| `ui_branding.title` | set | - |
| `ui_branding.subtitle` | set | - |
| `[P] show_navigation` | N | ? |
