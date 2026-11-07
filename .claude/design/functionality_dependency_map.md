# Functionality Dependency Map

> **HISTORICAL NOTE (2026-11-06):** the `audit_report_enabled` flag was removed (LEGACY-AUDIT-FLAG-1, 2026-05-22): the T3 audit trail is part of every export. Rows and text below that mention it describe the earlier design. Current flags: `.claude/rules/rules_app_features_flags.md`.

**Last updated:** 2026-05-05 (Session 18 — full mapping decided)
**Companion files:**
- `app_features_scoping_guide.md` — flag abbreviations and group definitions
- `app_features_capability_matrix.md` — app features files × flags matrix
- ADR-069 — Complete Export Audit Trail Standard

This document maps **user-facing functionalities** (what the end user can do) to **code-level flags** (what must be activated in an app features config). It defines non-negotiable cascade rules, optional/configurable flags, and derived flags that are computed automatically.

---

## Concept

**User functionality** = a coherent capability the end user perceives (e.g. "I can filter data", "I can export my results").

**Code flag** = an app features config field that gates a specific system behaviour (e.g. `t3_sandbox_enabled`, `export_enabled`).

**The key principle:** Some user functionalities have non-negotiable dependencies — activating one without the other creates a broken or misleading experience. These are encoded as cascade rules validated at startup. Other flags are independent choices left to the deployer.

---

## Dependency Map

### 1. VIEW — Basic display (always active)

| Code flag | Value | Notes |
|---|---|---|
| `default_tier` | `T2` | **Always T2.** T2 is the data analysis recipe result; T1 is raw input. No app features should default to T1. |
| `tier_toggle_t1t2_enabled` | configurable | Can be turned off (e.g. static display app features files — show T2 only) |

**Derived:** No toggle needed if app features shows only one tier.

---

### 2. PASSIVE_INTERACT — Ephemeral explore (filter/drop, no data change)

| Code flag | Required? | Notes |
|---|---|---|
| `passive_filter_enabled` | ✅ Required | Enables row filter + column drop UI |
| `tier_toggle_t1t2_enabled` | configurable | Useful but not required — can be off |
| `hashes_export` | ✅ Always on | Traceability. Never gated. See ADR-069. |
| `autosave` / `ghost_save` | ❌ Off | Nothing to persist — passive filters are ephemeral |

**Rule:** Passive filter state is NOT recorded in the audit trail. The data state is fully described by the three hashes (data_batch_hash, data_analysis_recipe_sha256, decision_hash).

---

### 3. ACTIVE_INTERACT — T3 audit branch (justified data decisions)

**Cascade rule — ALL of the following must be true when `t3_sandbox_enabled: true`.
Validation error at startup if any co-flag is missing.**

| Code flag | Required | Reason |
|---|---|---|
| `t3_sandbox_enabled` | ✅ | The T3 sandbox itself |
| `comparison_mode_enabled` | ✅ | T3 is meaningless without ability to compare T2 vs T3 |
| `audit_report_enabled` | ✅ | T3 decisions must be auditable |
| `session_management_enabled` | ✅ | audit steps must be saveable |
| `autosave` / `ghost_save` | ✅ | Disaster recovery for active work |
| `export_enabled` | ✅ | T3 decisions must be exportable (step list + audit trail) |
| `tier_toggle_t1t2_enabled` | ✅ | Required to see T1↔T2 in context |
| `tier_toggle_t3_enabled` | ✅ | Required to see T2↔T3 comparison |
| `hashes_export` | ✅ Always on | ADR-069 |

**Rule:** You cannot have T3 without export. You cannot have T3 without session management. These functionalities are two sides of the same scientific workflow — justify → record → export.

---

### 4. EXPORT — Bundle and graph export

| Code flag | Required | Notes |
|---|---|---|
| `export_enabled` | ✅ | Single flag — covers bundle, group, and plot scope |
| `hashes_export` | ✅ Always on | ADR-069 — no opt-out |

**Scope** (all plots / group / plot) is determined by the active context and the scope toggle — NOT by separate flags. `EXP_BNDL`, `EXP_GROUP`, `EXP_GRF` are collapsed into `export_enabled`.

**Cascade:** If T3 on and `export_enabled: false` → startup validation error.

**ADR-069 audit trail** — every export always includes:
`data_batch_hash` + `data_analysis_recipe_sha256` + `decision_hash` + `git_commit` + `release_version` + `created_at` + `data_analysis_recipe_name` + `app_features_id` + `active_tier` + `software_versions` + `data_source_paths` + `t3_audit_steps` (when T3 active)

Image files (PNG/SVG/PDF) additionally embed an 8-field provenance subset in file metadata (Pillow iTXt / SVG `<metadata>` / XMP). See ADR-069.

---

### 5. IMPORT — Data and metadata ingestion

| Code flag | Required | Notes |
|---|---|---|
| `metadata_ingestion_enabled` (`META_ING`) | ✅ for metadata import | Enables metadata-only mapping in import UI |
| `import_helper_enabled` (`IMP_HLP`) | ✅ for full import | Enables all data analysis recipe data sources in import UI |

**Superset rule:** `IMP_HLP: true` implies `META_ING: true`. No need to set both.

**UI:** Single browse + mapping panel. The mapping panel auto-filters to allowed data sources based on the active flag. Import behavior: **overwrite** (not merge).

---

### 6. GALLERY — Chart example browser

| Code flag | Required | Notes |
|---|---|---|
| `gallery_enabled` | ✅ | Single on/off flag |

No cascade dependencies. Standalone feature. Sub-flags deferred until component matures.

---

### 7. BLUEPRINT ARCHITECT — Lineage design tools

| Code flag | Required | Notes |
|---|---|---|
| `blueprint_enabled` | ✅ | Single on/off flag |

No cascade dependencies currently. Sub-flags (TUBE_MAP, WRNG_STU) deferred until component matures.

---

### 8. TEST LAB — Synthetic data and data analysis recipe scaffolding

| Code flag | Required | Notes |
|---|---|---|
| `test_lab_enabled` | ✅ | Single on/off flag |

No cascade dependencies currently. Sub-flags (DATA_PREP, CREATE_TEST_DATA, CREATE_DATA_ANALYSIS_RECIPE) deferred.

---

### 9. UI — Layout and branding

| Flag | Type | Rule |
|---|---|---|
| `show_navigation` | **Derived** | Auto-shown when any of `gallery_enabled` / `blueprint_enabled` / `test_lab_enabled` is true. No config needed. |
| `data_analysis_recipe_selector_visible` | configurable | `true` = user can switch data analysis recipes; `false` = data analysis recipe locked. These are opposites — never both. |
| `show_app_features_badge` | configurable | Display preference only. No functional dependency. |
| `ui_title` | configurable | Resolution: app features config override > data analysis recipe `info.display_name` > nothing shown. |
| `ui_subtitle` | configurable | Resolution: app features config override > data analysis recipe `info.subtitle` > nothing shown. Hidden if `ui_title` is off. `info.description` is free-form long text — NOT shown in UI header. |
| `sidebar_deployment` | placeholder | String field, default `"default"`. Future: named sidebar layout modules (e.g. `"website"`, `"pipeline"`). Deferred. |

---

## Cascade Rules Summary

```
T3_SAND: true
  → comparison_mode_enabled: true   (required)
  → audit_report_enabled: true      (required)
  → session_management_enabled: true (required)
  → ghost_save.enabled: true        (required)
  → export_enabled: true            (required)
  → tier_toggle_t1t2_enabled: true  (required)
  → tier_toggle_t3_enabled: true    (required)

IMP_HLP: true
  → metadata_ingestion_enabled: true (implied)

show_navigation
  → derived: true when any of gallery_enabled / blueprint_enabled / test_lab_enabled is true

ui_subtitle visible
  → requires ui_title to be shown
```

Validation: `AppFeaturesConfigError` raised at startup if any cascade rule is violated.

---

## What deployers can freely configure

- Which passive functionalities to expose (filter, tier toggle)
- Whether export is available
- Whether import is available, and at what level (metadata only vs full)
- Whether Gallery / Blueprint / Test Lab are accessible
- UI branding (title, subtitle, app features badge, data analysis recipe selector lock)
- Default tier display (always T2; toggle can be hidden)
- Ghost save on/off (only meaningful when T3 active)

## What is NOT configurable

- Hashes and audit trail in exports — always on (ADR-069)
- T3 cascade dependencies — all or nothing
- Default tier — always T2
- Navigation visibility — derived automatically
