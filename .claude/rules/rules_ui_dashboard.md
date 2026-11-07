---
trigger: always_on
deps:
  provides: [rule:ui_orchestration, rule:theatre_layout, rule:sidebar_law]
  documents: [app/handlers/home_theater.py, app/handlers/session_handlers.py, app/handlers/export_handlers.py, app/handlers/filter_and_audit_handlers.py, libs/blueprint_arch/src/blueprint_arch/blueprint_mapper.py]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

## 1. UI Orchestration & Aesthetics (ADR-027–030)

- **Library Sovereignty:** UI MUST NOT duplicate logic; it MUST call libraries in `./libs/`.
- **Dynamic discovery:** Tabs and column filters MUST be derived from data analysis recipes and Polars schemas at runtime.
- **T3 = Publication Finisher (§12, ui_implementation_contract.md):** Tier 3 scope is **permanently locked** to row filters, row exclusions, column visibility, and aesthetic overrides. It is NOT a wrangling sandbox — no action-picker UI. Wrangling belongs in T1/T2 data analysis recipes.
- **audit steps IS the Audit Trace:** There is no separate FILTERS.txt for T3. The T3 YAML audit trail (list of AuditStep dicts) is the complete audit trail. `aesthetic_override` nodes are stored separately as `t3_plot_overrides` but are included in the export report.
- **Two Ghost Save Slots:** (1) T1/T2 Ghost (`_autosave_assembly.json`) — written on assembly, refreshed on data_analysis_recipe/data change. (2) T3 Ghost (`_autosave_t3.json`) — written on every `btn_apply` AND on every panel switch away from Home.
- **State Feedback:** When a plot is "In-Calculation" (recalc ONLY applies to Tier 3 since Tiers 1/2 are immutable Parquet caches), the UI must use a dimming overlay with a "recalculating" message.

## 2. Left vs Right Panel Behaviors (ADR-073)

**Sidebars are configured via the app features file, not hardcoded in Python.** Each app features file declares a `workspaces:` section with independent left/right sidebar configs per workspace (Home, Blueprint, Gallery, Test Lab). See `ui_implementation_contract.md §11` and `docs/workflows/ui_app_features.qmd` for the full slot registry spec and panel type reference.

**Two-layer resolution:** (1) The app features file **slot list** controls which panel types appear and in what order. (2) Each panel type has a **gate flag** — if the flag is disabled, the panel is silently skipped. Flags and cascade rules are completely independent of the slot list.

- **Left Sidebar**: Content is workspace-dependent. Switching workspaces physically replaces the left sidebar DOM (not CSS-hide). Panel content per workspace is declared in `workspaces.<ws>.left_sidebar.panels`. Panels are registered in `app/modules/sidebar_registry.py` (`PANEL_REGISTRY`).

  **Available Home panel types** (gate flags in parentheses): `data_analysis_recipe_info` (none), `deployment_info` (none), `data_analysis_recipe_choice` (`data_analysis_recipe_selector.visible`), `filters` (`interactivity_enabled`), `data_import` (`metadata_ingestion_enabled`), `export` (`export_enabled`), `session_management` (`session_management_enabled`). See `ui_implementation_contract.md §11d` for complete table.

  **Filter behavior unchanged:** `_pending_filters` / `applied_filters` state is preserved across workspace switches; filter widgets are only mounted when `workspaces.home.left_sidebar.panels` contains `filters` and the gate flag is on.

- **Right Sidebar**: Same slot registry pattern. Current built-in types: `audit_stack` (gate: `t3_sandbox_enabled`), `notification_log` (none), `blueprint_logic` (gate: `blueprint_enabled`). Visibility is driven by `workspaces.<ws>.right_sidebar.visible` in the app features file — **not** by app features name comparison in `ui.py` (that was an ADR-053 violation, now fixed by ADR-073/task 25-O).

- **Sidebar visibility**: `visible: false` excludes the container from the DOM. Auto-hide: if all panels skip (all gate flags off) and `visible` is unset, sidebar is excluded. `visible: true` with no active panels renders an empty container (allowed for branding/info-only configs).

- **The Focus Mode (ADR-038)**: Gallery workspace left sidebar shows only `gallery_search` panel — operation controls (Import/Session) are not in its slot list, providing automatic focus mode without extra gating logic.

- **The Gatekeeper**: `btn_apply` is locked unless all T3 audit nodes have non-empty `reason` fields. Rendered only when the right sidebar `audit_stack` panel is active.

## 3. App features Reactivity Matrix (Component Masking)

The UI dynamically alters component availability based on the templates in `config/app_features/`. Below is the authoritative component mapping (updated ADR-052, 2026-05-01):

| App features | passive_exploration | t3_audit | Filters | Right Sidebar | Gallery | Test Lab | Sessions | Export Bundle | Export Graph |
| :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- | :--- |
| **1. pipeline-static** | ❌ | ❌ | Hidden (static msg) | **Excluded from layout** | ❌ | ❌ | ❌ | ✅ | ❌ |
| **2. pipeline-exploration-simple** | ✅ | ❌ | Exploration disclaimer | **Excluded from layout** | ❌ | ❌ | ✅ | ✅ | ❌ |
| **3. pipeline-exploration-advanced** | ✅ | ✅ | Full + T3 audit | **Visible** | ❌ | ❌ | ✅ | ✅ | ✅ |
| **4. standalone** | ✅ | ✅ | Full + T3 audit | **Visible** | ✅ | ❌ | ✅ | ✅ | ✅ |
| **5. developer** | ✅ | ✅ | Full + T3 audit | **Visible** | ✅ | ✅ | ✅ | ✅ | ✅ |
| **6. qa** | ✅ | ✅ | Full + T3 audit | **Visible** | ✅ | ✅ | ✅ | ✅ | ✅ |

**passive_exploration**: T1/T2 filter + column-drop scratchpad — plot updates temporarily, nothing saved, no audit trail.
**t3_audit**: promotes filters/drops to T3 audit pipeline (right sidebar, propagation modal, reason gatekeeper, audit trail export).

**App features file flags** (in `config/app_features/<app features>_template.yaml`):
`interactivity_enabled`, `blueprint_enabled`, `test_lab_enabled`, `gallery_enabled`, `comparison_mode_enabled`, `session_management_enabled`, `import_helper_enabled`, `export_enabled`, `metadata_ingestion_enabled`, `data_ingestion_enabled`.

**`qa` app features:** Mirrors `developer` flags but sets `automation.ghost_save: false` for deterministic Playwright runs (no background ghost writes during smoke tests). It is the recommended `SPARMVET_APP_FEATURES` for CI.

**New flags (Phase 25 / ADR-052):**
`data_analysis_recipe_selector.visible` — hides Data analysis recipe Choice dropdown for pipeline app features files (when false, the deployment must name the data analysis recipe with `default_data_analysis_recipe`, or `SPARMVET_DATA_ANALYSIS_RECIPE` for one run; otherwise the app stops, ADR-091).
`testing_mode` — true = pre-fill data selector from data analysis recipe default paths; false = data injected by pipeline or chosen by user.

**Pipeline app features files are always production-mode**: `pipeline-static` and `pipeline-exploration-simple` always have `testing_mode=false` and `data_analysis_recipe_selector.visible=false`. Testing of pipeline integrations uses a more capable app features.

**Right sidebar layout (ADR-073):** Structural exclusion is now driven by `bootloader.get_sidebar_config("home", "right").visible` — set to `false` in `pipeline-static` and `pipeline-exploration-simple` app features files. This replaces the previous `SPARMVET_APP_FEATURES` env-var comparison in `ui.py` (ADR-053 violation, task 25-O, fixed in SIDEBAR-REGISTRY-1). The center column fills full width when the right sidebar is excluded.

## 4. Coding Standards & Execution

- **Home Module State Object** (`home_state`): A single `reactive.Value` dict holding navigation state, filter state, audit steps, pending T3 nodes, and plot overrides. Full schema in `ui_implementation_contract.md §13`. Survives all panel switches. `t3_audit_steps` (wrangling audit nodes) and `t3_plot_overrides` (aesthetic changes per plot sub-tab) are **separate fields** within it. Changes only apply upon `btn_apply`.
- **The Pipeline Builder Scope**: `build_polars_pipeline(df, steps)` must dynamically translate nodes. In simpler app features files, this relies on basic filter mappings. In **Developer/Advanced** app features files, this must proxy directly out to the unified `@register_action` registry defined in the Transformer layer to support any arbitrary Python execution payload.
- **Unified Home Theater (ADR-043)**: The "Analysis Theater / Viz" nav mode is **eliminated**. Home is the sole results mode. Data analysis recipe-defined `analysis_groups` are the primary tab structure of Home. Plot sub-tabs (`navset_underline`) are wrapped in a **collapsible accordion panel**; data preview panes are in a **separate collapsible accordion panel below**. Both default to expanded. Collapse state is user-driven and must not reset on sub-tab navigation.
- **Plot vs data view (ADR-086)**: the Home header strip has two independent choices. "Data to show" (Raw / Result / My view) drives the data preview only; "Plot to show" (Result / My view / Compare Result vs My view) drives the plots only. Plots never show T1. Comparison Mode is always T2 (left) vs My view (right). Implemented 2026-11-05; see `ui_implementation_contract.md §2/§5`.
- **Hierarchical Visualization**: Home MUST organize data analysis recipe-defined plots into **Sub-Tabs** (navset_underline) within their respective category tabs to prevent vertical scrolling clutter. These sub-tabs are wrapped in a collapsible accordion as per ADR-043.
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
  - The Gallery MUST serve pre-rendered `.png` assets, YAML data analysis recipes, and JSON metadata exclusively from `assets/gallery_data/`.
  - The ONLY permitted interactive functionality is the transplantation (cloning) of a pure YAML string into the Tier 3 active sandbox.
- **Hierarchical Asset Caching (TBD-02)**: The Bootloader MUST implement a single source of truth static dict for all materialized/parsed assets natively at runtime to prevent repetitive file-IO overhead.
  - Cache Hierarchy Contract: `_asset_cache[data_analysis_recipe_id][dataset_id][plot_id][asset_type]`
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
| `app/modules/t3_audit_engine.py` | Pure helpers (Two-Category Law): `_apply_filter_rows`, `_op_label`. No Shiny imports. | (functions) |
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

- **T1 Startup**: app loads, no startup errors, data analysis recipe load renders group nav tabs
- **T2 App features masking**: sidebar visibility for launch app features (2 tests skip unless non-developer app features)
- **T3 Filter pipeline**: filter form renders, add row, apply no-crash, reset clears rows — highest-risk refactor surface
- **T4 Data preview**: `#home_data_preview` visible after data analysis recipe load

### Commands

```bash
# Core unit tests (fast, ~2 s) — run first
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q

# Playwright smoke tests (qa app features — deterministic, ~35 s)
PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py -v

# App import must stay clean
python -c "from app.src.main import app; print('OK')"
```

### App features for automated testing

Use `SPARMVET_APP_FEATURES=qa` for all automated runs. The `qa` app features has all flags ON and
`ghost_save.enabled: false` — deterministic behaviour without auto-saves interfering with
DOM state. See `config/app_features/qa.yaml`.

### Critical patterns

- **`_wait_shiny(page)`**: always call after any interaction that triggers a Shiny reactive.
  Uses `document.documentElement.classList.contains('shiny-busy')` — do not skip this.
- **Group tab selectors**: use `.nav-link:has-text('Quality Control')` (partial text, emoji-safe).
  Role-based selectors (`get_by_role("tab")`) fail on emoji-containing labels.
- **`fb_op` select**: `filter_form_ui` re-renders when `fb_col` changes, detaching `fb_op` from DOM.
  Always call `_wait_shiny()` after column selection before touching operator or value fields.
- **No runtime app features selector**: `#app_features_selector` does not exist; app features is launch-time
  config (`SPARMVET_APP_FEATURES`). The old `test_reactive_shell.py` (app features switch, Apply gate label)
  was removed 2026-11-06; its Apply-gate logic is covered by `test_session_manager.py` and a UI-level
  test is open as AUDIT-GATE-UI-1.
- **Libs**: all of `libs/` collects and passes under `pytest libs` (2026-11-06); no lib needs to be
  excluded any more (`generator_utils` was renamed to `test_lab`, ADR-084).

### Decision table

| Test scope | Command |
|---|---|
| Fast regression only | `pytest app/tests/test_filter_operators.py libs/connector/tests/ libs/viz_factory/tests/test_deco2_components.py -q` |
| Full gate (required before merge) | Add `SPARMVET_APP_FEATURES=qa pytest app/tests/test_shiny_smoke.py -v` |
| Home Theater change (Phase 24+) | Both above + `python -c "from app.src.main import app; print('OK')"` |

---

## 7. The Blueprint Architect Invariants (ADR-039, ADR-075, ADR-082)

The Blueprint Architect provides a "Flight Deck" for data analysis recipe design.

**Feature set lock (ADR-082).** BLUEPRINT is four composable layers; the full feature set, the MVP/v2/out-of-scope inventory, and the T1/T2-vs-T3 boundary are authoritative in ADR-082.

| Layer | Capability | Owning ADR(s) |
|---|---|---|
| L1 — Navigation | TubeMap DAG + Lineage Rail + 3-column contract viewer | ADR-039/040/074 |
| L2 — Forms | Action/component picker + 8-widget `ui_schema` renderer + **Joint Designer pane** (joins) | ADR-075, ADR-082 (BP-JOINT-1) |
| L3 — Data view | Live Data Glimpse (on-Apply) | ADR-082 |
| L4 — Helpers | AI agent + YAML escape hatch + undo + branch | ADR-075/076/082 |

**Branching = lineage bifurcation at a node (ADR-082 Q3, LOCKED).** A "branch" splits one lineage in two **at a chosen node**: upstream stays **shared** (Tier 1 trunk materialized once, branches `scan_parquet` it — no recompute), child lineages diverge downstream. Physically it is the **fragment-per-component** `!include` structure (canonical: `Summary` / `Summary_quality`) — the Bifurcation Point Rule (`rules_data_engine.md`) made interactive. The TubeMap *fan-out* is the visual; the *data analysis recipe branch* is the lineage split. Whole-data analysis recipe duplication is a separate rare path (new data only). **BLUEPRINT never authors T3** — T3 is HOME-only (ADR-082 §4).

- **The Central Vertical Stack (The Theater)**:
  1. **Top Header**: The **Interactive TubeMap** (DAG). Must be collapsible to maximize workspace.
  2. **Central Body**: The **Live Visualization** (Plot).
  3. **Bottom Footer**: The **Live Data Glimpse** (Table).
- **The Joint Designer pane (BP-JOINT-1, ADR-082 Q5)**: A dedicated center-theater tab for authoring `join` steps — left + right ingredient schemas side-by-side, composite-key pickers, and a **real-data** live key-match preview (materialises each ingredient via the orchestrator; overlap computed on String-cast keys, mirroring the assembler). Apply is audit-gated on a justification and emits a canonical `join` step (`on` symmetric / `left_on`+`right_on` asymmetric). Pure logic: `libs/blueprint_arch/src/blueprint_arch/join_designer.py`. Replaces the former fabricated join modal.
- **The Right Sidebar (The Logic)**: Focuses exclusively on the internal transformation steps of the component selected in the Map.
- **Logic Sync**: Any modification in the Right Sidebar MUST trigger a reactive update of the Central Stack (Plot & Table) for immediate verification.

**IDE Build Mode additions (ADR-075):**
- **Form generation from `ui_schema`**: Action and component forms in BLUEPRINT are generated from `ui_schema` dicts embedded in `@register_action` and `@register_plot_component` decorators. The `schema_registry.py` module in `libs/blueprint_arch/` reads these dicts at startup and builds the action/component picker catalog. All form rendering is driven by this catalog — no hardcoded form layouts.
- **Action picker**: searchable by `tags`, filtered by `context` (`t1` / `t2` / `assembly` / `plot`) and `category`. Position rules are enforced by the `context` tag — the picker only shows actions valid for the current node position.
- **Apply gate**: upstream schema propagates on Apply only (not continuously). The form reflects the last-applied schema state between Apply presses.
- **Edit/remove after Apply**: three layers — (1) edit in place + re-Apply, (2) 20-step session undo deque (`BP-UNDO-1`), (3) YAML escape hatch.
- **YAML escape hatch**: always visible for any app features with `blueprint_enabled: true` (read-only view). Becomes an editable textarea only when `data_analysis_recipe_edit_enabled: true` (developer and qa app features files). An editable escape hatch emits a `developer_raw_yaml` T3 node on save. Gate: `bootloader.is_enabled("data_analysis_recipe_edit_enabled")` — never an app features name check. See `rules_app_features_flags.md §Group D`.
- Full ADR-075 spec (widget types, color widget model, help system, action naming) lives in `architecture_decisions.md`.
