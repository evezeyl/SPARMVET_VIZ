---
trigger: always_on
deps:
  provides: [rule:ui_orchestration, rule:theatre_layout, rule:sidebar_law]
  documents: [app/handlers/home_theater.py, app/handlers/session_handlers.py, app/handlers/export_handlers.py, app/handlers/filter_and_audit_handlers.py, libs/utils/src/utils/blueprint_mapper.py]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

## 1. UI Orchestration & Aesthetics (ADR-027–030)

- **Library Sovereignty:** UI MUST NOT duplicate logic; it MUST call libraries in `./libs/`.
- **Dynamic discovery:** Tabs and column filters MUST be derived from manifests and Polars schemas at runtime.
- **T3 = Publication Finisher (§12, ui_implementation_contract.md):** Tier 3 scope is **permanently locked** to row filters, row exclusions, column visibility, and aesthetic overrides. It is NOT a wrangling sandbox — no action-picker UI. Wrangling belongs in T1/T2 manifests.
- **T3 Recipe IS the Audit Trace:** There is no separate FILTERS.txt for T3. The T3 YAML recipe (list of RecipeNode dicts) is the complete audit trail. `aesthetic_override` nodes are stored separately as `t3_plot_overrides` but are included in the export report.
- **Two Ghost Save Slots:** (1) T1/T2 Ghost (`_autosave_assembly.json`) — written on assembly, refreshed on manifest/data change. (2) T3 Ghost (`_autosave_t3.json`) — written on every `btn_apply` AND on every panel switch away from Home.
- **State Feedback:** When a plot is "In-Calculation" (recalc ONLY applies to Tier 3 since Tiers 1/2 are immutable Parquet caches), the UI must use a dimming overlay with a "recalculating" message.

## 2. Left vs Right Panel Behaviors

- **Left Panel (Navigation & Context)**: Content is **panel-context-dependent** — the left sidebar renders different content depending on which top-level panel is active. Switching panels physically replaces the left sidebar DOM (not CSS-hide). See `ui_implementation_contract.md §11` for the full panel → sidebar content map.

  **Home mode left sidebar (Phase 25-E accordion structure, top-down):**
  - **Manifest Choice** — manifest selector dropdown (`project_id`). Hidden when persona has `manifest_selector.visible=false` (pipeline-static, pipeline-exploration-simple).
  - **Data Import** (Phase 25-F) — testing_mode-aware. `testing_mode=false`: read-only listing of source files resolved from the active manifest. `testing_mode=true`: same listing + metadata replacement upload (gate: `metadata_ingestion_enabled`) + multi-file/Excel uploader (gate: `data_ingestion_enabled`).
  - **Filters** — Filter Recipe Builder (Phase 21-F). Add N filter rows `{column, op, value}`. `_pending_filters` staging → `applied_filters` committed on Apply. Ops: `in`/`not_in` for discrete; `eq`/`ne`/`gt`/`ge`/`lt`/`le`/`between` for numeric. Static message + buttons hidden when `interactivity_enabled=false`; exploration disclaimer for passive personas (`metadata_ingestion_enabled=false` proxy).
  - **Export** (2026-05-04 redesign; gate: `export_bundle_enabled + export_graph_enabled`) — bundle name field, plot format radio (PNG/SVG/PDF), filter trace warning, **3-way scope toggle** `[Global project | Active group | Active plot]`, Export Bundle download. T3 Audit Trail and `t3_steps.yaml` auto-included when T3 has committed nodes. Single Graph Export accordion removed — superseded by "Active plot" scope. See `ui_implementation_contract.md §7.2` for full spec.
  - **Session Management** (gate: `session_management_enabled`) — header-level "Export Active Session (.zip)" download (Phase 25-G), import .zip control, per-session Restore + Delete (per-session Export removed in 25-G).

  **Blueprint Architect mode left sidebar:** Manifest/component navigation (dataset pipeline selector, TubeMap node selector). No filter widgets.

  **Gallery mode left sidebar:** Focus Mode (ADR-038) — operation controls hidden; gallery search/filter only.

  **Test Lab mode left sidebar (renamed "Dev Studio" → "Test Lab" in Phase 25-A):** TBD — deferred until Test Lab is finalized.
- **Right Panel (The Active Blueprint Stack)**: In **Blueprint Architect** mode, the right panel is the authoritative workspace for the **Active Component Logic Stack**. In **Home** mode (post-ADR-043/ADR-044), visibility is persona-gated: hidden entirely for `pipeline_static` and `pipeline_exploration_simple`; full audit stack for ≥ `pipeline_exploration_advanced`. When hidden, the theater center column expands to fill the full width.
- **The Focus Mode (ADR-038)**: Global Navigation (Far-Left Sidebar) MUST programmatically hide "Operation" controls (Import/Session) when "Discovery" tabs (Gallery) are active to maximize screen utility and reduce cognitive load.
- **The Gatekeeper**: Modifications on the UI triggers no calculations until the user presses `btn_apply`. The apply action is locked unless every user-made recipe node contains a valid `comment_field` entry. The gatekeeper is only rendered when the right sidebar is visible (≥ `pipeline_exploration_advanced`).

## 3. Persona Reactivity Matrix (Component Masking)

The UI dynamically alters component availability based on the templates in `config/ui/templates/`. Below is the authoritative component mapping (updated ADR-052, 2026-05-01):

| Persona | passive_exploration | t3_audit | Filters | Right Sidebar | Gallery | Test Lab | Sessions | Export Bundle | Export Graph |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. pipeline-static** | ❌ | ❌ | Hidden (static msg) | **Excluded from layout** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **2. pipeline-exploration-simple** | ✅ | ❌ | Exploration disclaimer | **Excluded from layout** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **3. pipeline-exploration-advanced** | ✅ | ✅ | Full + T3 audit | **Visible** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **4. project-independent** | ✅ | ✅ | Full + T3 audit | **Visible** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **5. developer** | ✅ | ✅ | Full + T3 audit | **Visible** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **6. qa** | ✅ | ✅ | Full + T3 audit | **Visible** | ✅ | ✅ | ✅ | ✅ | ✅ |

**passive_exploration**: T1/T2 filter + column-drop scratchpad — plot updates temporarily, nothing saved, no audit trail.
**t3_audit**: promotes filters/drops to T3 audit pipeline (right sidebar, propagation modal, reason gatekeeper, recipe export).

**Persona template flags** (in `config/ui/templates/<persona>_template.yaml`):
`interactivity_enabled`, `developer_mode_enabled`, `gallery_enabled`, `comparison_mode_enabled`, `session_management_enabled`, `import_helper_enabled`, `export_bundle_enabled`, `export_graph_enabled`, `metadata_ingestion_enabled`, `data_ingestion_enabled`.

**`qa` persona:** Mirrors `developer` flags but sets `automation.ghost_save: false` for deterministic Playwright runs (no background ghost writes during smoke tests). It is the recommended `SPARMVET_PERSONA` for CI.

**New flags (Phase 25 / ADR-052):**
`manifest_selector.visible` — hides Manifest Choice dropdown for pipeline personas (fixed_manifest path required when false).
`testing_mode` — true = pre-fill data selector from manifest default paths; false = data injected by pipeline or chosen by user.

**Pipeline personas are always production-mode**: `pipeline-static` and `pipeline-exploration-simple` always have `testing_mode=false` and `manifest_selector.visible=false`. Testing of pipeline integrations uses a more capable persona.

**Right sidebar layout (ADR-052-§1):** For pipeline-static and pipeline-exploration-simple, the right sidebar container is **excluded at layout build time** in `app/src/ui.py` (reads `SPARMVET_PERSONA` env var at startup). The center column fills full width. Returning `ui.div()` from `right_sidebar_content_ui` is insufficient — it leaves the 340px container in the DOM.

## 4. Coding Standards & Execution

- **Home Module State Object** (`home_state`): A single `reactive.Value` dict holding navigation state, filter state, T3 recipe, pending T3 nodes, and plot overrides. Full schema in `ui_implementation_contract.md §13`. Survives all panel switches. `t3_recipe` (wrangling audit nodes) and `t3_plot_overrides` (aesthetic changes per plot sub-tab) are **separate fields** within it. Changes only apply upon `btn_apply`.
- **The Pipeline Builder Scope**: `build_polars_pipeline(df, recipe)` must dynamically translate nodes. In simpler personas, this relies on basic filter mappings. In **Developer/Advanced** personas, this must proxy directly out to the unified `@register_action` registry defined in the Transformer layer to support any arbitrary Python execution payload.
- **Unified Home Theater (ADR-043)**: The "Analysis Theater / Viz" nav mode is **eliminated**. Home is the sole results mode. Manifest-defined `analysis_groups` are the primary tab structure of Home. Plot sub-tabs (`navset_underline`) are wrapped in a **collapsible accordion panel**; data preview panes are in a **separate collapsible accordion panel below**. Both default to expanded. Collapse state is user-driven and must not reset on sub-tab navigation.
- **Hierarchical Visualization**: Home MUST organize manifest-defined plots into **Sub-Tabs** (navset_underline) within their respective category tabs to prevent vertical scrolling clutter. These sub-tabs are wrapped in a collapsible accordion as per ADR-043.
- **CSS Layer (The High-Density Shell)**:
  - **Background**: Body and Theater background MUST use **Neutral Grey (#d1d1d1)** for premium white-card contrast.
  - **Sidebars**: MUST use **Dark Grey (#c0c0c0)** sidebar backgrounds for visual symmetry.
  - **Gaps**: All structural gaps (between sidebars, theater, and cards) MUST be standardized at **10px** to balance breathing room with screen utility.
  - **Density Optimization**: Navigation sidebars MUST use collapsible accordions and ultra-high-density inputs (uppercase labels, <4px margins) to minimize vertical scrolling.
  - **Alignment**: Primary module headers (e.g., "Pipeline Audit") and theater titles (e.g., "SPARMVET Home") MUST be perfectly centered via flex-alignment.
  - **Buttons**: Action buttons (e.g., "Reset Sync", "Apply") MUST use the standard **SPARMVET Blue (`#345beb`)** `btn-primary` class unless specifically designated as destructive. Note: `#0d6efd` is Bootstrap's default and must NOT be used — it conflicts with the locked accent colour. Destructive = amber `#ffc107`. Teal `#10a395` = export/ingest actions only.
  - **Nodes**: The `violet` (#f3e5f5) inherited rows and `yellow` (#fffde7) sandbox rows must strictly maintain the visual standard.
  - **ID Sanitation**: ALL major theater components MUST use dynamic IDs based on the active sidebar module (ADR-036) to ensure complete DOM clearing during module context switches.

## 5. Architectural Invariants (Gallery & Caching)

- **Gallery Isolation Boundary (TBD-03)**: The Gallery (`gallery_viewer.py`) MUST strictly operate as a static reference browser. It is explicitly forbidden from generating dynamic Polars materializations or calculating Plotnine objects at runtime.
  - The Gallery MUST serve pre-rendered `.png` assets, YAML manifests, and JSON metadata exclusively from `assets/gallery_data/`.
  - The ONLY permitted interactive functionality is the transplantation (cloning) of a pure YAML string into the Tier 3 active sandbox.
- **Hierarchical Asset Caching (TBD-02)**: The Bootloader MUST implement a single source of truth static dict for all materialized/parsed assets natively at runtime to prevent repetitive file-IO overhead.
  - Cache Hierarchy Contract: `_asset_cache[project_id][dataset_id][plot_id][asset_type]`
- **Gallery Taxonomy & Indexing (ADR-037)**: The Gallery UI MUST NOT perform direct filesystem scans or YAML parsing for filtering.
  - Filtering logic MUST rely exclusively on the pre-computed `gallery_index.json` (Pivot-Index).
  - The UI is responsible for performing set-intersections against the pivot IDs to provide zero-latency responses.
  - The index MUST be maintained via the `refresh_gallery.py` utility located in the library assets.

## 6. Headless Playwright Smoke Testing (Mandatory Verification Gate)

Any change to `app/handlers/home_theater.py` or its sub-handlers MUST pass the headless
Playwright smoke suite before the commit is accepted. This is the UI verification gate for
Phase 24 and all future Home Theater refactors.

### Home Theater handler map (post-Phase-24, ADR-051 IMPLEMENTED 2026-05-01)

| File | Owns | Entry point |
|---|---|---|
| `app/handlers/home_theater.py` | Coordinator: `_safe_id`, `_collect_all_group_plot_ids`, reactive helpers + closures, `dynamic_tabs`, tier-toggle/session-provenance trackers, `home_data_preview`/`home_col_selector_ui`/`col_drop_audit_btn_ui`, `sidebar_nav_ui`, `sidebar_tools_ui`, `right_sidebar_content_ui`, plot/table renders + brush + comparison toggle, calls to all three sub-handlers. | `define_server(...)` |
| `app/modules/t3_recipe_engine.py` | Pure helpers (Two-Category Law): `_apply_filter_rows`, `_op_label`. No Shiny imports. | (functions) |
| `app/handlers/session_handlers.py` | Session management panel: `session_management_ui`, `_handle_session_import`, `_handle_session_actions`, `_restore_session`. | `define_session_server(...)` |
| `app/handlers/export_handlers.py` | Export pipeline: `system_tools_ui`, `export_bundle_download`, `export_audit_report_*`, filename helpers. | `define_export_server(...)` |
| `app/handlers/filter_and_audit_handlers.py` | Filter UI + T3 audit: `sidebar_filters` shell, `filter_rows_ui`, `filter_form_ui`, `filter_controls_ui`, all filter effects, propagation modal, `_make_remove_handler` factory. | `define_filter_audit_server(...)` |

Shared `reactive.Value` instances (`applied_filters`, `_pending_filters`,
`_propagation_scratch`, `home_state`) are created in `home_theater.define_server()` and
passed as kwargs to the sub-handlers. They are NEVER module-level globals.

### Infrastructure

| File | Role |
|---|---|
| `app/tests/conftest.py` | `shiny_app` fixture — module-scoped `ShinyAppProc` via `shiny.pytest.create_app_fixture` |
| `app/tests/test_shiny_smoke.py` | 12 smoke tests across 4 tiers (T1–T4) |
| `app/tests/test_filter_operators.py` | 21-case filter contract regression (pure logic, fast) |

### Test tiers

- **T1 Startup**: app loads, no startup errors, project load renders group nav tabs
- **T2 Persona masking**: sidebar visibility for launch persona (2 tests skip unless non-developer persona)
- **T3 Filter pipeline**: filter form renders, add row, apply no-crash, reset clears rows — highest-risk refactor surface
- **T4 Data preview**: `#home_data_preview` visible after project load

### Commands

```bash
# Core unit tests (fast, ~2 s) — run first
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q

# Playwright smoke tests (qa persona — deterministic, ~35 s)
PYTHONPATH=. SPARMVET_PERSONA=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v

# App import must stay clean
python -c "from app.src.main import app; print('OK')"
```

### Persona for automated testing

Use `SPARMVET_PERSONA=qa` for all automated runs. The `qa` persona has all flags ON and
`ghost_save.enabled: false` — deterministic behaviour without auto-saves interfering with
DOM state. See `config/ui/templates/qa_template.yaml`.

### Critical patterns

- **`_wait_shiny(page)`**: always call after any interaction that triggers a Shiny reactive.
  Uses `document.documentElement.classList.contains('shiny-busy')` — do not skip this.
- **Group tab selectors**: use `.nav-link:has-text('Quality Control')` (partial text, emoji-safe).
  Role-based selectors (`get_by_role("tab")`) fail on emoji-containing labels.
- **`fb_op` select**: `filter_form_ui` re-renders when `fb_col` changes, detaching `fb_op` from DOM.
  Always call `_wait_shiny()` after column selection before touching operator or value fields.
- **Pre-existing failures**: `test_reactive_shell.py::test_persona_switch_reactivity` and
  `test_reactive_shell.py::test_reactive_audit_gate` fail due to `#persona_selector` not
  rendered in UI — persona is env-var-only. Do not regress further; these are not Phase 24 concerns.
- **Excluded libs**: always exclude `libs/generator_utils/` and `libs/utils/` — pre-existing
  ImportErrors unrelated to any refactor work.

### Decision table

| Test scope | Command |
|---|---|
| Fast regression only | `pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q` |
| Full gate (required before merge) | Add `SPARMVET_PERSONA=qa pytest app/tests/test_shiny_smoke.py -v` |
| Home Theater change (Phase 24+) | Both above + `python -c "from app.src.main import app; print('OK')"` |

---

## 7. The Blueprint Architect Invariants (ADR-039)

The Blueprint Architect provides a "Flight Deck" for manifest design.

- **The Central Vertical Stack (The Theater)**:
  1. **Top Header**: The **Interactive TubeMap** (DAG). Must be collapsible to maximize workspace.
  2. **Central Body**: The **Live Visualization** (Plot).
  3. **Bottom Footer**: The **Live Data Glimpse** (Table).
- **The Right Sidebar (The Logic)**: Focuses exclusively on the internal transformation steps of the component selected in the Map.
- **Logic Sync**: Any modification in the Right Sidebar MUST trigger a reactive update of the Central Stack (Plot & Table) for immediate verification.
