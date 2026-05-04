# Persona Scoping Guide
**Last updated:** 2026-05-04  
**Companion files:**
- `persona_capability_matrix.csv` — personas × flags matrix (fill `?` cells here)
- `persona_flag_legend.csv` — flag abbreviation lookup (ABBREV → full flag + group + description)
- `ui_panel_map_current.md` — CSS selectors and panel names for each UI element  

**Persona templates:** `config/ui/templates/`

This document defines the scoping groups, flag abbreviations, cell conventions, and dependency rules used in the matrix CSV. Update whenever a new flag is added or a group boundary changes.

---

## How to use the matrix CSV

Open `persona_capability_matrix.csv` with `|` as delimiter in LibreOffice / Excel.

- **Rows** = personas (existing + proposed)
- **Columns** = flag abbreviations (see `persona_flag_legend.csv` for full names)
- **Cell value** = group abbreviation when the flag is **active** for that persona; `-` when off

### Cell value conventions

| Cell value | Meaning |
|---|---|
| `VIEW` / `FILTER` / `T3` / `SESS` / `EXP` / `ING` / `DEV` / `UI` | Flag is **active** — group abbreviation shows which group it belongs to |
| `G1/G2` | Flag active and spans two groups (e.g., `VIEW/UI`) |
| `-` | Flag is **inactive** / disabled for this persona |
| `?` | **To be decided** — fill this in |
| `T1` / `T2` | For `DEF_TIER` column only — which tier loads by default |
| `set` | For `MAN_FIX` / `UI_TITLE` / `UI_SUBT` — a value is configured (see template) |
| `null` | For `MAN_FIX` — free manifest choice |
| `[P]` prefix on row name | Proposed persona — not yet implemented |

---

## Group abbreviations

| Abbrev | Full name | What it covers |
|---|---|---|
| `VIEW` | View / tier display | Tier toggle, default tier, data visibility |
| `FILTER` | Passive filter | Ephemeral curiosity exploration — no data change, no audit |
| `T3` | T3-Audit / active filter | Justified edits, T3 branch, audit trail, propagation, comparison |
| `SESS` | Session | Save/restore work-in-progress; autosave |
| `EXP` | Export | Bundle ZIP, single graph export |
| `ING` | Ingest | Metadata upload, import helper, raw data ingest |
| `DEV` | Developer tools | Gallery, Blueprint, Test Lab, Wrangle Studio |
| `UI` | UI layout | Navigation, sidebar title, manifest selector, persona badge |

---

## Flag abbreviations (summary — full details in persona_flag_legend.csv)

### GROUP: VIEW

| Abbrev | Full flag | Notes |
|---|---|---|
| `INTERACT` | `interactivity_enabled` | Master gate — too coarse; proposed for decomposition |
| `TIER_TOG` | `[P] tier_toggle_enabled` | Explicit T1↔T2 toggle; proposed |
| `DEF_TIER` | `[P] default_tier` | T1 or T2 on load; proposed |

**Dependency:** `TIER_TOG` off → `DEF_TIER` is the only tier shown (no toggle).  
**Open question:** retire `INTERACT` and replace with `TIER_TOG` + `PAS_FILT`, or keep as legacy alias?

---

### GROUP: FILTER — Passive (view-only, no data change)

| Abbrev | Full flag | Notes |
|---|---|---|
| `PAS_FILT` | `[P] passive_filter_enabled` | Column drop + row filter, ephemeral; proposed |

**Key distinction:**
- **Passive filter** (`PAS_FILT`) = user **explores** the data; view changes, nothing recorded, resets on reload
- **Active filter** (`T3_SAND`) = user **justifies and commits** a decision; T3 branch created, written to audit

**Dependency:** `PAS_FILT` is independent of `T3_SAND` — they can coexist or be used alone.  
**Open question:** should passive filter panel look visually distinct from T3 active filter panel so users can't confuse them?

---

### GROUP: T3 — Active filter and audit trail

| Abbrev | Full flag | Notes |
|---|---|---|
| `T3_SAND` | `t3_sandbox_enabled` | Full T3 sandbox; T2 never modified — T3 creates a branch |
| `CMP_MODE` | `comparison_mode_enabled` | Compare T2 vs T3; requires `T3_SAND` |
| `AUD_RPT` | `audit_report_enabled` | Export consolidated audit report |

**Dependency:** `CMP_MODE` requires `T3_SAND: true`.

---

### GROUP: SESS — Session persistence

| Abbrev | Full flag | Notes |
|---|---|---|
| `SESS_MGT` | `session_management_enabled` | Session accordion UI visibility |
| `AUTOSAVE` | `ghost_save.enabled` | Autosave timer — **SESSION-PERSONA-1 (open): must be gated on T3_SAND** |

**Rule:** Session save (manual + autosave) only meaningful when `T3_SAND` is active. Passive-filter-only personas have nothing to persist.

---

### GROUP: EXP — Export

| Abbrev | Full flag | Notes |
|---|---|---|
| `EXP_BNDL` | `export_bundle_enabled` | Global ZIP: plots + data + recipes + audit + README (3 hashes) |
| `EXP_GRF` | `export_graph_enabled` | Single graph export |

---

### GROUP: ING — Ingest

| Abbrev | Full flag | Notes |
|---|---|---|
| `META_ING` | `metadata_ingestion_enabled` | Upload replacement metadata (triggers T1 rebuild) |
| `IMP_HLP` | `import_helper_enabled` | External import helper panel |
| `DAT_ING` | `data_ingestion_enabled` | Raw data file / Excel upload |
| `IMP_PNL` | `data_import_panel_visible` | Parent accordion panel — container for META_ING + IMP_HLP + DAT_ING |

---

### GROUP: DEV — Developer tools

| Abbrev | Full flag | Notes |
|---|---|---|
| `GALLERY` | `gallery_enabled` | Gallery browser (34 recipes, 6-axis taxonomy) |
| `DEV_MODE` | `developer_mode_enabled` | Enables Blueprint Architect + Test Lab |
| `WRNG_STU` | `wrangle_studio_enabled` | Advanced recipe editor (Wrangle Studio) |
| `TEST_LAB` | `test_lab_enabled` | Currently derived from `DEV_MODE` — no separate flag yet |

---

### GROUP: UI — Layout and branding

| Abbrev | Full flag | Notes |
|---|---|---|
| `PRS_BADGE` | `show_persona_badge` | "Active: persona-name" in nav header |
| `MAN_SEL` | `manifest_selector.visible` | Manifest choice dropdown in sidebar |
| `MAN_FIX` | `manifest_selector.fixed_manifest` | Locks manifest; `null` = free choice |
| `UI_TITLE` | `ui_branding.title` | Project/pipeline title next to logo; already in web-demo template; proposed to standardize |
| `UI_SUBT` | `ui_branding.subtitle` | Subtitle line |
| `SHOW_NAV` | `[P] show_navigation` | Hides nav pills strip (Home / Blueprint / Test Lab / Gallery); proposed |
| `SDB_PROF` | `[P] sidebar_profile` | Named sidebar layout module; deferred Phase 27+ |

**Panel map cross-reference:** see `ui_panel_map_current.md` → Vocabulary section for CSS selectors of each UI element.

---

## Persona template files

| Persona ID | Template file | TYPE column |
|---|---|---|
| `pipeline-static` | `pipeline-static_template.yaml` | existing |
| `demo-vetinst` | `demo-vetinst_template.yaml` | existing |
| `web-demo` | `web-demo_template.yaml` | existing |
| `pipeline-exploration-simple` | `pipeline-exploration-simple_template.yaml` | existing |
| `pipeline-exploration-advanced` | `pipeline-exploration-advanced_template.yaml` | existing |
| `project-independent` | `project-independent_template.yaml` | existing |
| `developer` | `developer_template.yaml` | existing |
| `qa` | `qa_template.yaml` | existing |
| `[P] web-project-showcase` | *(not yet created)* | proposed |
| `[P] lightweight-exploration` | *(not yet created)* | proposed |

---

## Open design questions

- **`INTERACT` decomposition:** retire `interactivity_enabled` and replace with `TIER_TOG` + `PAS_FILT`? Or keep as legacy alias pointing to both? Decide before implementing proposed flags.
- **`PAS_FILT` scope:** column drop only, or also row filter? Both are non-destructive but row filter is more powerful. Should the passive filter panel be visually distinct from the T3 active filter panel?
- **`DEF_TIER` with `TIER_TOG` off:** if toggle is hidden, should the UI still show a small badge indicating which tier is displayed, or is that noise for static personas?
- **`SDB_PROF` modularization:** worth doing only if >3 distinct sidebar layouts emerge from real deployments. Hold until concrete requests come in.
- **`TEST_LAB` separate flag:** currently derived from `DEV_MODE`. Add `test_lab_enabled` as an independent flag if a use case requires Test Lab without Blueprint (or vice versa).
