# HOME — Main Analysis Space

**Type:** User space  
**Status:** Mature (core built; several tasks pending)  
**Last updated:** 2026-05-05

---

## Purpose

HOME is where the user runs **predefined, repeatable analyses** and gets **publication-ready results**. The analysis pipeline is defined in a manifest (built in BLUEPRINT); HOME runs it. The user's interaction space is intentionally narrow: load data, apply the manifest, make justified minor adjustments, inspect, and export.

The core values of HOME — audit trail, transparency, reproducibility, shareability — are not optional features. They are the reason HOME exists. Every action taken in HOME must be documentable and defensible: the user should be able to hand their exported report to a colleague or reviewer and have it tell the full story of how the data was processed.

The other user spaces exist to serve HOME: BLUEPRINT builds the manifests HOME runs, TEST_LAB prepares the data HOME receives, GALLERY provides the inspiration BLUEPRINT uses.

---

## User Functionalities

| Functionality | What the user can do |
|---|---|
| **Load data** | Import one or more data files (CSV/TSV/XLSX) into the session |
| **Select manifest** | Choose which predefined manifest (analysis recipe) to apply, optionally filtered by selector |
| **Run analysis** | Execute the manifest pipeline: T1 filter/select, T2 group/aggregate, joint merge, tidy pivot/reshape, wrangle, plot — as defined; no ad-hoc steps |
| **Filter / drop data** | Apply justified exclusions (e.g. remove low-quality samples) with a mandatory reason — logged to audit trail |
| **Palette override** | Apply a per-session colour palette that overrides the manifest defaults for this run; does not modify the manifest; label display is auto-adjusted for legibility based on plot size and label count (prefer automatic over manual control) |
| **Inspect** | Preview data at any pipeline stage; see row counts, column types, sample rows |
| **Audit** | Review the full decision/action log; see what changed, why, and by whom |
| **Export** | Export plots (PNG/SVG/PDF), data (CSV/TSV/Parquet), or a full audit report (HTML/PDF) with complete provenance — ready to share with colleagues or submit as supplementary material |
| **Session** | Autosave progress; restore a prior session; view session history |
| **Navigate** | Switch between active manifests/tiers from the sidebar |

---

## Non-Goals

- HOME does not build or edit manifests — that is BLUEPRINT.
- HOME does not generate or transform test data — that is TEST_LAB.
- HOME does not browse or contribute recipes — that is GALLERY.
- HOME does not expose raw Python/R code to the user.

---

## Key Design Constraints

- **Manifest-driven**: HOME never applies ad-hoc transformations. Every action comes from a manifest node. Structural changes (new steps, new columns, new plot types) go to BLUEPRINT.
- **Narrow user interaction surface by design**: the user adjusts within the manifest's bounds, not around it. This is intentional — it ensures reproducibility and protects the audit trail.
- **Audit always on**: Every applied action is logged with hash, timestamp, and provenance (ADR-069). No opt-out.
- **Filter/drop requires justification**: any data exclusion must carry a reason field. Empty reason = blocked. This is a UX constraint, not just a data constraint.
- **Palette override is session-scoped**: the user can override the manifest's colour palette for their session only. It does not write back to the manifest. Structural colour changes (new palettes, per-group colours) belong in BLUEPRINT.
- **Auto-legible labels**: label rendering adapts automatically to plot size and label count. Manual label override is a last resort, not a primary control.
- **Positive inclusion** (ADR-071): Only modules enabled in the persona config are registered and mounted. Disabled modules produce no DOM output.
- **T3 cascade rule**: T3 sandbox requires CMP_MODE + AUD_RPT + SESS_MGT + AUTOSAVE + export_enabled + both TIER_TOGs.
- **Export single flag**: `export_enabled` gates all export surfaces; format-level control is within that flag.

---

## Code Modules

| Code module | Role |
|---|---|
| `wrangle_studio.py` | Pipeline rendering, plot output, sub-tab management |
| `t3_recipe_engine.py` | T3 sandbox: live recipe editing within a session |
| `filter_and_audit_handlers.py` | TIER_TOG filters, audit trail panel |
| `ingestion_handlers.py` | Data loading, file parsing |
| `data_import_handlers.py` | Import UI and metadata mapping |
| `export_handlers.py` + `exporter.py` | All export surfaces |
| `session_handlers.py` + `session_manager.py` | Autosave, session restore, ghost_save |
| `audit_stack.py` | Right-panel audit stack rendering |

---

## Current State

- Core pipeline (wrangle + plot) built and working.
- T3 sandbox built; pending DEPLOY-MODULES-1 gating.
- Filter/audit panel built.
- Export: basic CSV/plot export works; audit-complete metadata (EXPORT-AUDIT-COMPLETE-1), image metadata embedding (EXPORT-IMG-META-1), and version stamping (EXPORT-VERSION-1) pending.
- Session autosave: ghost_save pending SESSION-PERSONA-1 gating.
- Import unified panel: IMPORT-UI-1 pending.

---

## Open Questions

- **Auto-label algorithm**: what determines when labels are rotated, truncated, or hidden? Font size, plot width, label count threshold? Needs a spec before implementation.
- **Auto-label algorithm**: what determines when labels are rotated, truncated, or hidden? Font size, plot width, label count threshold? Needs a spec before implementation.
- Preview rows: default 100, "show all" toggle — UX-PREVIEW-ROWS-1.
- Plot panel collapse/minimize — THEATER-1.
- How does the user navigate between multiple active manifests when `manifest_selector_visible` is off?
