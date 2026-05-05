# Deployment Configuration Matrix
**Last updated:** 2026-05-05 (Session 18)
**Companion guide:** `persona_scoping_guide.md` (flag reference, dependency rules)
**Dependency map:** `functionality_dependency_map.md` (user functionality → code flags)
**Persona templates:** `config/ui/templates/`

> **Framing note:** The rows below are named example configurations ("personas"), not the primary concept.
> The primary concept is the **user functionality** each configuration enables.
> See `functionality_dependency_map.md` to understand what each flag does and which combinations are valid.

`Y` = enabled | `N` = disabled | `[P]` = proposed (not yet implemented) | `-` = N/A | `~` = partial

---

## GROUP: VIEW

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `default_tier` = T2 | T2 | T2 | T2 | T2 | T2 | T2 | T2 | T2 |
| `tier_toggle_t1t2_enabled` | N | N | N | Y | Y | Y | Y | Y |
| `tier_toggle_t3_enabled` | N | N | N | N | Y | Y | Y | Y |

> Default tier is always T2 — no exceptions. Tier toggle is configurable but required when T3 active.

---

## GROUP: FILTER — Passive (ephemeral, no audit)

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `passive_filter_enabled` | N | N | N | Y | Y | Y | Y | Y |

> Passive filter = ephemeral curiosity exploration. Does NOT change data, writes nothing to audit.

---

## GROUP: T3-AUDIT (active — changes data branch, requires justification)

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `t3_sandbox_enabled` | N | N | N | N | Y | Y | Y | Y |
| `comparison_mode_enabled` | N | N | N | N | Y | Y | Y | Y |
| `audit_report_enabled` | N | N | N | N | Y | Y | Y | Y |

> T3 cascade: all three above must be true together. See `functionality_dependency_map.md`.

---

## GROUP: SESSION

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `session_management_enabled` | N | N | N | N | Y | Y | Y | Y |
| `ghost_save.enabled` | N | N | N | N | Y | Y | Y | N |

> `ghost_save` required when T3 active. Off for passive personas (nothing to persist). Off for `qa` (automated testing).

---

## GROUP: EXPORT

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `export_enabled` | Y | N | N | Y | Y | Y | Y | Y |

> Single flag — scope (project / group / plot) determined by active context + toggle, not separate flags.
> Hashes and full audit trail always included in exports (ADR-069 — no opt-out).

---

## GROUP: INGEST

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `metadata_ingestion_enabled` | N | N | N | N | Y | Y | Y | Y |
| `import_helper_enabled` | N | N | N | N | N | Y | Y | Y |

> `import_helper_enabled: true` implies `metadata_ingestion_enabled: true`.
> Unified import UI — single browse + mapping panel; panel content driven by flag.

---

## GROUP: DEV — Developer tools

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `gallery_enabled` | N | N | N | N | N | Y | Y | Y |
| `blueprint_enabled` | N | N | N | N | N | Y | Y | Y |
| `test_lab_enabled` | N | N | N | N | N | N | Y | Y |

> Each is a single on/off flag. Sub-flags deferred until components mature.

---

## GROUP: UI-LAYOUT

| Flag | pipeline-static | demo-vetinst | web-demo | pipeline-expl-simple | pipeline-expl-advanced | project-independent | developer | qa |
|---|:---:|:---:|:---:|:---:|:---:|:---:|:---:|:---:|
| `show_persona_badge` | Y | N | N | Y | Y | Y | Y | Y |
| `manifest_selector_visible` | N | N | N | N | Y | Y | Y | Y |
| `manifest_selector.fixed_manifest` | set | set | set | set | set | null | null | null |
| `ui_title` (persona override) | - | - | set | - | - | - | - | - |
| `ui_subtitle` (persona override) | - | - | set | - | - | - | - | - |
| `show_navigation` *(derived)* | N | N | N | N | N | Y | Y | Y |
| `sidebar_profile` | default | default | default | default | default | default | default | default |

> `show_navigation` is derived — auto-shown when any of gallery / blueprint / test_lab enabled.
> `ui_title` / `ui_subtitle`: persona override > manifest `info.display_name` / `info.subtitle` > nothing.
> `sidebar_profile`: placeholder string field. Only `"default"` exists currently. Future: named layout modules.

---

## Proposed new configurations

| Flag | `[P]` web-project-showcase | `[P]` lightweight-exploration |
|---|:---:|:---:|
| `default_tier` | T2 | T2 |
| `tier_toggle_t1t2_enabled` | N | N |
| `tier_toggle_t3_enabled` | N | N |
| `passive_filter_enabled` | N | Y |
| `t3_sandbox_enabled` | N | N |
| `comparison_mode_enabled` | N | N |
| `audit_report_enabled` | N | N |
| `session_management_enabled` | N | N |
| `ghost_save.enabled` | N | N |
| `export_enabled` | N | Y |
| `metadata_ingestion_enabled` | N | N |
| `import_helper_enabled` | N | N |
| `gallery_enabled` | N | N |
| `blueprint_enabled` | N | N |
| `test_lab_enabled` | N | N |
| `show_persona_badge` | N | N |
| `manifest_selector_visible` | N | N |
| `manifest_selector.fixed_manifest` | set | set |
| `ui_title` (persona override) | set | - |
| `ui_subtitle` (persona override) | set | - |
| `show_navigation` *(derived)* | N | N |
| `sidebar_profile` | default | default |
