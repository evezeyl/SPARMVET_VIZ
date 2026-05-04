# Persona Scoping Guide
**Last updated:** 2026-05-04  
**Companion file:** `persona_capability_matrix.md`  
**Persona templates:** `config/ui/templates/`

This document defines the scoping groups, flags, abbreviations, and dependency rules used in the persona capability matrix. Update this file whenever a new flag is added or a group boundary changes.

---

## Abbreviations (for matrix cells)

| Symbol | Meaning |
|---|---|
| `Y` | Implemented and **enabled** for this persona |
| `N` | Implemented and **disabled** for this persona |
| `Y*` | Enabled but with known caveats (see Notes column) |
| `~` | Partially implemented |
| `[P]` | **Proposed** — flag does not exist yet; cell value is the intended state |
| `?` | To be decided — user input needed |
| `-` | Not applicable for this persona |

---

## Scoping Groups

### GROUP: VIEW — Data visibility and tier display

Controls what data tier the user sees and whether they can switch between tiers.

| Flag | Type | Description |
|---|---|---|
| `interactivity_enabled` | existing | Master gate — currently too coarse. Controls tier toggle AND implicitly gates several UI sections. **Proposed for decomposition.** |
| `[P] tier_toggle_enabled` | proposed | Explicit flag for the T1↔T2 toggle button. Decoupled from filter/sandbox access. |
| `[P] default_tier` | proposed | `T1` or `T2` — which tier renders on first load. Static/showcase personas should default to `T2` (analysis-ready). |

**Dependency:** `tier_toggle_enabled: false` should force `default_tier` to whichever tier is shown.

---

### GROUP: FILTER — View-only data exploration

**Passive filters** allow curiosity exploration **without changing data**. They are ephemeral (reset on page reload) and write nothing to the audit trail. They do not branch the data.

**Active filters** (T3) are in the T3-AUDIT group below.

| Flag | Type | Description |
|---|---|---|
| `[P] passive_filter_enabled` | proposed | Shows the filter accordion (column drop + row filter) in view-only / ephemeral mode. No audit trail. No T2 data modification. Useful for simple exploration personas. |
| `[P] column_hide_enabled` | proposed (optional) | Sub-option of passive filter: column visibility toggle only (simpler than full row filter). May not need a separate flag if `passive_filter_enabled` covers both. |

**Key distinction:**
- Passive filter = the user **explores** the data (view changes, nothing is recorded)
- Active filter (T3) = the user **justifies and records** a decision (data branch created, written to audit)

**Dependency:** `passive_filter_enabled` must NOT require `t3_sandbox_enabled`. They are independent.

---

### GROUP: T3-AUDIT — Justified edits and audit trail

Active filters that **change the data branch** (T3). Every action requires a justification reason and is written to the audit trail. T2 data is never modified — T3 creates a branch.

| Flag | Type | Description |
|---|---|---|
| `t3_sandbox_enabled` | existing | Gates the full T3 sandbox: row filters with justification, right sidebar audit panel, propagation modal. |
| `comparison_mode_enabled` | existing | Compare T2 vs T3 side-by-side. Requires `t3_sandbox_enabled` to be meaningful. |
| `audit_report_enabled` | existing | Export the consolidated audit report (HTML/PDF/DOCX). |

**Dependency:** `comparison_mode_enabled` requires `t3_sandbox_enabled: true`.

---

### GROUP: SESSION — Work-in-progress persistence

Session save/restore applies **only when T3 is active** — passive-filter-only personas have nothing to persist (view state is ephemeral by design).

| Flag | Type | Description |
|---|---|---|
| `session_management_enabled` | existing | Shows the Session Management accordion in the sidebar (save, export, import). |
| `automation.ghost_save.enabled` | existing | Autosave timer. **SESSION-PERSONA-1 (open):** must be gated on `t3_sandbox_enabled` — if T3 is not active, there is nothing to autosave. |
| `automation.ghost_save.frequency_minutes` | existing | Autosave interval. |

**Rule:** Session save (manual and autosave) is only meaningful when `t3_sandbox_enabled: true`.

---

### GROUP: EXPORT — Output packaging

| Flag | Type | Description |
|---|---|---|
| `export_bundle_enabled` | existing | Global export ZIP: plots + data TSVs + recipes + audit trail + README with 3 hashes. |
| `export_graph_enabled` | existing | Single-graph export (PNG/SVG + per-plot README). |

---

### GROUP: INGEST — Data and metadata input

| Flag | Type | Description |
|---|---|---|
| `metadata_ingestion_enabled` | existing | Upload replacement metadata file (triggers T1 rebuild). |
| `import_helper_enabled` | existing | External import helper panel. |
| `data_ingestion_enabled` | existing | Raw data file / Excel upload. |
| `data_import_panel_visible` | existing | Shows/hides the data import sidebar accordion (parent panel). |

---

### GROUP: DEV — Developer tools

| Flag | Type | Description |
|---|---|---|
| `gallery_enabled` | existing | Gallery Browser (34 recipes, 6-axis taxonomy). |
| `developer_mode_enabled` | existing | Developer mode — enables Blueprint Architect and Test Lab. |
| `wrangle_studio_enabled` | existing | Wrangle Studio (advanced recipe editor). |

**Note:** Test Lab visibility is currently derived from `developer_mode_enabled` — no separate flag yet.

---

### GROUP: UI-LAYOUT — Navigation, sidebar, and branding

Controls what structural UI elements are visible and how the sidebar is branded/configured.

| Flag | Type | Description |
|---|---|---|
| `show_persona_badge` | existing | Shows "Active: persona-name" badge in nav header. |
| `manifest_selector.visible` | existing | Shows/hides the manifest choice dropdown in sidebar. |
| `manifest_selector.fixed_manifest` | existing | If set, locks the manifest (no user choice). `null` = free choice. |
| `ui_branding.title` | existing (web-demo) | Text shown next to logo (project/pipeline name). Currently only in web-demo template. **Proposed to standardize across all templates.** |
| `ui_branding.subtitle` | existing (web-demo) | Subtitle line. Same as above. |
| `[P] show_navigation` | proposed | Shows/hides the home button and view navigation elements. `false` = clean static display, no nav. |
| `[P] sidebar_profile` | proposed (future) | Named sidebar layout profile (`"standard"` / `"minimal"` / `"custom"`). Would load a different sidebar builder module. **Deferred — requires sidebar modularization (Phase 27+).** |

---

## Persona Template Files

| Persona ID | Template file | Primary use case |
|---|---|---|
| `pipeline-static` | `pipeline-static_template.yaml` | Automated pipeline output, view only |
| `demo-vetinst` | `demo-vetinst_template.yaml` | NVI-branded static presentation |
| `web-demo` | `web-demo_template.yaml` | Public-facing web page (has title/subtitle fields) |
| `pipeline-exploration-simple` | `pipeline-exploration-simple_template.yaml` | T1/T2 view + toggle, no T3 |
| `pipeline-exploration-advanced` | `pipeline-exploration-advanced_template.yaml` | Full T3 sandbox |
| `project-independent` | `project-independent_template.yaml` | Researcher: T3 + Gallery + Ingest |
| `developer` | `developer_template.yaml` | All features |
| `qa` | `qa_template.yaml` | Testing/CI — all features, no autosave |

---

## Proposed New Personas (to define)

| Proposed ID | Description | Key capabilities |
|---|---|---|
| `web-project-showcase` | Static project webpage, clean branding | T2 default, no toggle, `ui_branding.title`, no nav, optional export |
| `lightweight-exploration` | Explore freely, no commitments | Passive filter (view-only), T2 default, no T3, optional export |

---

## Open Design Questions

- **`interactivity_enabled` decomposition**: retire this flag and replace with `tier_toggle_enabled` + `passive_filter_enabled`? Or keep as legacy alias? Need to decide before implementing proposed flags.
- **`passive_filter_enabled` scope**: does it include column drop only, or also row filter? If row filter is ephemeral (no data change), should it look visually distinct from T3 active filter?
- **`sidebar_profile` modularization**: worth doing if >3 distinct sidebar layouts emerge from real deployments. Hold until we have concrete requests.
- **`default_tier` interaction with `tier_toggle_enabled: false`**: if toggle is hidden, the default tier is the only tier. Should the UI still show which tier is displayed (e.g., a small badge), or is that noise for static personas?
