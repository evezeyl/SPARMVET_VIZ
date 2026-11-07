# Deployment Configuration Guide

> **HISTORICAL NOTE (2026-11-06):** the `audit_report_enabled` flag was removed (LEGACY-AUDIT-FLAG-1, 2026-05-22): the T3 audit trail is part of every export. Rows and text below that mention it describe the earlier design. Current flags: `.claude/rules/rules_app_features_flags.md`.

**Last updated:** 2026-05-05 (Session 18 — full functionality mapping decided)
**Companion files:**
- `functionality_dependency_map.md` — **start here** — user functionality → code flag dependencies
- `app_features_capability_matrix.md` — example deployment configurations (named app features files) × flags
- `ui_panel_map_current.md` — CSS selectors and panel names for each UI element
- ADR-069 — Complete Export Audit Trail Standard

**App features files:** `config/app_features/`

---

## Core concept

SPARMVET is deployed with **app features** that define which user functionalities are available. The name "app features" is used for named example sets (e.g. `pipeline-static`, `developer`), but an app features is just a label for a specific combination of flags.

**The right way to think about deployment:**
> "What do I want my users to be able to do?" → pick the functionalities → validate dependencies → name it.

The app features files shipped with SPARMVET are reusable starting points. Deployers can create their own by composing functionalities within the cascade rules.

See `functionality_dependency_map.md` for the complete dependency rules before creating a custom configuration.

---

## Group abbreviations

| Abbrev | Full name | What it covers |
|---|---|---|
| `VIEW` | View / tier display | Default tier, tier toggle visibility |
| `FILTER` | Passive filter | Ephemeral row filter + column drop — no audit, no data change |
| `T3` | T3-Audit / active filter | Justified edits, T3 branch, audit trail, comparison |
| `SESS` | Session | Save/restore work-in-progress; ghost save |
| `EXP` | Export | Bundle ZIP + scope toggle (all plots / group / plot) |
| `ING` | Ingest | Metadata upload, full data import |
| `DEV` | Developer tools | Gallery, Blueprint Architect, Test Lab |
| `UI` | UI layout | Navigation (derived), sidebar branding, data analysis recipe selector |

---

## Flag reference

### GROUP: VIEW

| Abbrev | Full flag | Notes |
|---|---|---|
| `DEF_TIER` | `default_tier` | **Always `T2`.** T2 is the data analysis recipe result. No app features defaults to T1. |
| `TIER_T12` | `tier_toggle_t1t2_enabled` | Show T1↔T2 toggle. Configurable on/off. Required if T3 active. |
| `TIER_T3` | `tier_toggle_t3_enabled` | Show T2↔T3 comparison toggle. Required if T3 active. Off otherwise. |

**Rule:** `T3_SAND: true` → both `TIER_T12` and `TIER_T3` must be true (cascade).

---

### GROUP: FILTER — Passive (view-only, no data change)

| Abbrev | Full flag | Notes |
|---|---|---|
| `PAS_FILT` | `passive_filter_enabled` | Row filter + column drop, ephemeral — resets on reload |

**Key distinction:**
- **Passive filter** (`PAS_FILT`) = user explores; view changes, nothing recorded, resets on reload
- **Active filter** (`T3_SAND`) = user justifies and commits; T3 branch created, written to audit

Passive filter state is **not** recorded in the audit trail — the three hashes (data_batch, data analysis recipe, decision) fully describe the reproducible data state.

---

### GROUP: T3 — Active filter and audit trail

| Abbrev | Full flag | Notes |
|---|---|---|
| `T3_SAND` | `t3_sandbox_enabled` | Full T3 sandbox; T2 never modified — T3 creates a branch |
| `CMP_MODE` | `comparison_mode_enabled` | Compare T2 vs T3; required when T3 active |
| `AUD_RPT` | `audit_report_enabled` | Consolidated audit report; required when T3 active |

**Cascade:** `T3_SAND: true` requires `CMP_MODE: true` + `AUD_RPT: true` + `SESS_MGT: true` + `AUTOSAVE: true` + `export_enabled: true` + both tier toggles. `AppFeaturesConfigError` raised at startup if violated.

---

### GROUP: SESS — Session persistence

| Abbrev | Full flag | Notes |
|---|---|---|
| `SESS_MGT` | `session_management_enabled` | Session accordion UI visibility |
| `AUTOSAVE` | `ghost_save.enabled` | Ghost save timer. Only meaningful when `T3_SAND: true`. Off for passive app features files. |

**Rule:** Parquet cache (T1 materialisation) is always written for performance, independent of this flag. `AUTOSAVE` only controls the session JSON (ghost save).

---

### GROUP: EXP — Export

| Abbrev | Full flag | Notes |
|---|---|---|
| `EXP` | `export_enabled` | Single flag — enables export bundle + scope toggle (all plots / group / plot) |

**Scope** (all plots / group / plot) is determined by the active context and scope toggle — not by separate flags. The old `EXP_BNDL` / `EXP_GROUP` / `EXP_GRF` flags are collapsed into `export_enabled`.

**ADR-069 rule — hashes always on:** Every export always includes the full provenance set (data_batch_hash, data_analysis_recipe_sha256, decision_hash, git_commit, release_version, created_at, data_analysis_recipe_name, app_features_id, active_tier, software_versions, data_source_paths). No flag, no opt-out. Image files embed an 8-field subset in file metadata (PNG iTXt / SVG `<metadata>` / PDF XMP).

---

### GROUP: ING — Ingest

| Abbrev | Full flag | Notes |
|---|---|---|
| `META_ING` | `metadata_ingestion_enabled` | Import UI shows metadata schema only |
| `IMP_HLP` | `import_helper_enabled` | Import UI shows all data analysis recipe data sources (implies `META_ING`) |

**UI:** Single browse + mapping panel. Panel auto-filters to allowed sources based on active flag. Import behavior: **overwrite** (not merge).

**Superset rule:** `IMP_HLP: true` implies `META_ING: true`.

---

### GROUP: DEV — Developer tools

| Abbrev | Full flag | Notes |
|---|---|---|
| `GALLERY` | `gallery_enabled` | Gallery browser (34 examples, 6-axis taxonomy). Standalone — no cascade. |
| `BLUEPRINT` | `blueprint_enabled` | Blueprint Architect (TubeMap, data analysis recipe navigator). Standalone. Sub-flags deferred. |
| `TEST_LAB` | `test_lab_enabled` | Test Lab (synthetic data, data analysis recipe scaffolding). Standalone. Sub-flags deferred. |

Each is a single on/off flag. Sub-flags (e.g. TUBE_MAP, WRNG_STU for Blueprint; DATA_PREP, CREATE_TEST_DATA for Test Lab) are deferred until components mature. When introduced, sub-flags will be additive and non-breaking.

---

### GROUP: UI — Layout and branding

| Abbrev | Full flag | Type | Notes |
|---|---|---|---|
| `PRS_BADGE` | `show_app_features_badge` | configurable | "Active: app features name" in nav header. Display preference, no functional dependency. |
| `MAN_SEL` | `data_analysis_recipe_selector_visible: true` | configurable | User can switch data analysis recipes in sidebar. |
| `MAN_FIX` | `data_analysis_recipe_selector_visible: false` | configurable | Data analysis recipe locked — selector hidden. Opposite of MAN_SEL; never both. |
| `UI_TITLE` | `ui_title` (app features) / `info.display_name` (data analysis recipe) | configurable | Resolution: app features config override > data analysis recipe field > nothing. |
| `UI_SUBT` | `ui_subtitle` (app features) / `info.subtitle` (data analysis recipe) | configurable | Same resolution as UI_TITLE. Hidden if UI_TITLE is off. `info.description` is long free-form text — NOT shown in header. |
| `SHOW_NAV` | *(derived)* | **derived** | Auto-shown when any of `gallery_enabled` / `blueprint_enabled` / `test_lab_enabled` is true. No config field needed. |
| `SDB_PROF` | `sidebar_deployment` | placeholder | String field, default `"default"`. Future: named sidebar layout modules (e.g. `"website"`, `"pipeline"`). Deferred. |

---

## Cascade rules (summary)

```
T3_SAND: true  →  comparison_mode_enabled: true
               →  audit_report_enabled: true
               →  session_management_enabled: true
               →  ghost_save.enabled: true
               →  export_enabled: true
               →  tier_toggle_t1t2_enabled: true
               →  tier_toggle_t3_enabled: true

IMP_HLP: true  →  metadata_ingestion_enabled: true

show_navigation  →  derived: any(gallery_enabled, blueprint_enabled, test_lab_enabled)

ui_subtitle      →  only shown when ui_title is shown
```

Startup validation raises `AppFeaturesConfigError` if any cascade rule is violated.

---

## Example deployment configurations (app features files)

| App features ID | Intended use case | Template file |
|---|---|---|
| `pipeline-static` | Read-only display of pre-processed results | `pipeline-static.yaml` |
| `demo-vetinst` | Branded demo / presentation | `demo-vetinst.yaml` |
| `web-demo` | Public web display | `web-demo.yaml` |
| `pipeline-exploration-simple` | Pipeline users who filter but do not modify | `pipeline-exploration-simple.yaml` |
| `pipeline-exploration-advanced` | Pipeline users with full T3 audit capability | `pipeline-exploration-advanced.yaml` |
| `standalone` | Researcher with their own data — full data import + T3 | `standalone.yaml` |
| `developer` | Full access including Blueprint + Test Lab | `developer.yaml` |
| `qa` | Automated testing — all flags on | `qa.yaml` |
| `[P] web-showcase` | Public website with branded static display | *(not yet created)* |
| `[P] lightweight-exploration` | Passive filter only, minimal UI | *(not yet created)* |

---

## Open design questions (remaining)

- **`INTERACT` decomposition:** `interactivity_enabled` is a legacy coarse-grained flag. Decision pending: retire and replace with `PAS_FILT` + `TIER_T12`, or keep as alias?
- **`TEST_LAB` separate flag:** currently derived from `developer_mode_enabled`. Separate flag needed if a use case requires Test Lab without Blueprint (or vice versa).
- **`SDB_PROF` modularization:** implement only when >2 distinct sidebar layouts emerge from real deployments.
