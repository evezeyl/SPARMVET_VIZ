# Persona Traceability Matrix (Component Masking)

**Objective**: Systematic verification of UI stability, functional parity, and persona masking, superseding the UI Contract traceability.
**Last updated:** 2026-05-04 (export redesign: Export panel replaces Global Project Export + Single Graph Export; scope toggle added; T3 audit trail auto-included in bundle)

## Persona Capability Matrix

| Persona | passive_exploration | t3_audit | Blueprint | Gallery | Session Mgmt | Export Bundle | Export Graph | Metadata Upload | Data Ingestion | Test Lab | testing_mode | manifest_selector.visible |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| `pipeline-static` | ❌ | ❌ | ❌ | ❌ | ❌ | ✅ | ❌ | ❌ | ❌ | ❌ | false | false |
| `pipeline-exploration-simple` | ✅ | ❌ | ✅ | ❌ | ✅ | ✅ | ❌ | ❌ | ❌ | ❌ | false | false |
| `pipeline-exploration-advanced` | ✅ | ✅ | ✅ | ❌ | ✅ | ✅ | ✅ | ✅ | ❌ | ❌ | true | true |
| `project-independent` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | true | true |
| `developer` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | true | true |
| `qa` | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | true | true |

**passive_exploration:** can apply filters and drop columns to explore the view (T1/T2 — plot updates temporarily, nothing saved, no audit trail). Already implemented; previously undocumented.
**t3_audit:** can promote filters/drops to the T3 audit pipeline (right sidebar, propagation modal, reason gatekeeper, recipe export). Controlled by `t3_sandbox_enabled` flag (Phase 25-O).
Single Graph Export accordion removed in 2026-05-04 export redesign — superseded by "Active plot" scope option in the 3-way scope toggle on the Export panel.

> **CRITICAL**: Persona IDs use **hyphens** (`pipeline-exploration-advanced`), never underscores. Underscore variants silently fail all persona gates.

> **PERSONA-2 (2026-04-30)**: `qa` is a test-harness persona — all flags ON, `ghost_save.enabled: false` for deterministic automated testing.

> **Pipeline personas are always production-mode** (ADR-052-§3): `pipeline-static` and `pipeline-exploration-simple` always have `testing_mode=false`. Data arrives via pipeline channels. Testing of pipeline integrations uses a more capable persona (developer / advanced), never a modified pipeline persona.

## Left Sidebar — Accordion Panel Visibility

| Accordion Panel | pipeline-static | pipeline-exploration-simple | pipeline-exploration-advanced | project-independent | developer | Gate Flag |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **Manifest Choice** | HIDE (fixed by config) | HIDE (fixed by config) | SHOW | SHOW | SHOW | `manifest_selector.visible` |
| **Data Import** | SHOW (read-only path display) | SHOW (read-only path display) | SHOW (active selector) | SHOW (active selector) | SHOW (active selector) | always_on; selector gated by testing_mode |
| **Filters** | HIDE (static message) | SHOW (exploration disclaimer) | SHOW | SHOW | SHOW | `interactivity_enabled` |
| **Export** (scope toggle) | SHOW | SHOW | SHOW | SHOW | SHOW | `export_bundle_enabled + export_graph_enabled` |
| **Session Management** | HIDE | SHOW | SHOW | SHOW | SHOW | `session_management_enabled` |

## Right Sidebar Visibility (ADR-044 + ADR-052)

Right sidebar is **excluded from the layout entirely** (not CSS-hidden) for `pipeline-static` and `pipeline-exploration-simple`. Center column fills full width.

**Phase 25-D fix (ADR-052-§1):** Right sidebar container previously occupied 340px even when empty. Fixed by structural exclusion of `ui.sidebar(position="right")` for personas where it is absent.

**Phase 25-O fix:** Right sidebar gate now uses `bootloader.is_enabled("t3_sandbox_enabled")` — no longer reads `SPARMVET_PERSONA` string directly. Any custom persona template with `t3_sandbox_enabled: false` will correctly suppress the right sidebar.

| Persona | Right Sidebar | Center width |
| :--- | :--- | :--- |
| `pipeline-static` | **Excluded from layout** | Full width |
| `pipeline-exploration-simple` | **Excluded from layout** | Full width |
| `pipeline-exploration-advanced` | Visible | Standard (minus 340px) |
| `project-independent` | Visible | Standard |
| `developer` | Visible | Standard |
| `qa` | Visible | Standard |

## Filter Behavior per Persona

| Persona | Filter form visible | Behavior | Label |
| :--- | :--- | :--- | :--- |
| `pipeline-static` | ❌ | Static message: 'Filters are set by the pipeline configuration' | — |
| `pipeline-exploration-simple` | ✅ | T1/T2 only — plot updates temporarily, nothing saved | 'Exploration only — filters are not saved and do not modify data permanently' |
| `pipeline-exploration-advanced` | ✅ | T1/T2 passive exploration + T3 audit | No disclaimer |
| `project-independent` | ✅ | T1/T2 passive exploration + T3 audit | No disclaimer |
| `developer` | ✅ | T1/T2 passive exploration + T3 audit | No disclaimer |

**Apply/Audit button (single button — label changes per tier, already correct in code):**
- T1/T2 → `Apply (N)` — commits to transient `applied_filters` (passive exploration, no audit trail)
- T3 → `➜ Audit (N)` — opens propagation modal to promote to T3 audit pipeline

## Element Behaviors (updated)

| UI Category | Element ID | Functionality / Rule |
| :--- | :--- | :--- |
| **Navigation** | `project_id` (→ Manifest Choice) | Manifest discovery and loading. Hidden for pipeline personas — manifest fixed by config. |
| **Tier Toggle** | `tier_toggle` | T1 / T2 / T3. T3 hidden for `pipeline-static` (no interactivity) and `pipeline-exploration-simple` (passive exploration only — no T3 audit). |
| **Comparison Mode** | `comparison_mode` | Toggle visible for t3_audit personas only, AND only when tier == T3. Gate on `comparison_mode_enabled` flag. |
| **Filters** | `sidebar_filters` | Recipe-builder row filter UI. In T3: `➜ Audit (N)` promotes rows to per-plot T3 audit stack. In T1/T2: `Apply (N)` commits transient `applied_filters` (passive exploration — plot updates, nothing saved). |
| **Filters** | `home_col_selector_ui` | Column visibility for Data Preview. In T3: `➜ Audit drops (N)` promotes drops to `drop_column` audit nodes. |
| **Theater** | `dynamic_tabs` | Manifest-driven: groups → `navset_pill`, plots → `navset_card_tab`. |
| **Theater** | `home_data_preview` | DataGrid scoped to active plot's `target_dataset`. Applies committed T3 filter/drop nodes. |
| **Audit Stack** | `audit_nodes_tier2` | Violet read-only nodes (T2 blueprint steps). t3_audit personas only. |
| **Audit Stack** | `audit_nodes_tier3` | Per-plot Yellow nodes. Filtered to `home_state.active_plot_subtab`. Shows "Applied to N plots" badge and ⚠️ PK warning banner. |
| **Audit Stack** | `audit_stack_tools_ui` | Apply button (gated — all pending nodes must have non-empty reason). |
| **Audit Stack** | `propagation_modal` | 3-option scope dialog: "This plot only / All plots / All plots except…". |
| **Audit Stack** | `🗑 delete` | Removes a node and ALL linked copies sharing the same `id` across every plot stack. |
| **Session Mgmt** | `session_list_ui` | Lists all assembly/T3 ghosts. Restore + Export (.zip, Phase 25) + Delete per session. Visible for ≥ `pipeline-exploration-simple` (gate: `session_management_enabled`). |
| **Export** | `export_bundle_download` | ZIP: plots (format selector: PNG/SVG/PDF) + T1/T2 TSVs + YAML recipes + Quarto `.qmd` + README. All personas. |
| **Export** | `export_audit_report` | HTML/PDF/DOCX audit report via Quarto (server-side, Phase 25). t3_audit personas only. |
| **Export** | `export_graph_download` | Single plot + data slice + manifest section + T3 modifications. t3_audit personas. (Phase 25 BUILD_NEW.) |

## Comparison Mode Detail (Phase 21-E)

- Toggle label: "⚖ Compare T2 vs T3"
- Gate: `comparison_mode_enabled` flag AND `tier_toggle == "T3"`
- Left column: T2 baseline (no T3 nodes applied)
- Right column: T3 adjusted (committed T3 filter/drop nodes applied)

## Known Bugs tracked in tasks.md

| Bug ID | Description | Status |
|---|---|---|
| PERSONA-1 | Session Management hardcoded persona-name set | ✅ Fixed Phase 25-C |
| AUDIT-4 | Comparison toggle resets on plot switch (reactive scoping bug) | Open — Phase 25-C |
| GALLERY-BUG | Gallery always visible regardless of persona | ✅ Fixed Phase 25-A |
| LAYOUT-BUG | Right sidebar 340px always in DOM | ✅ Fixed Phase 25-D |
| PERSONA-NAME-CHECKS | 7 persona name string comparisons in runtime code | ✅ Fixed Phase 25-O — replaced with `t3_sandbox_enabled` flag |
