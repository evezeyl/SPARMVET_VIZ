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

## 2. Left vs Right Panel Behaviors (ADR-073)

**Sidebars are configured via the persona template, not hardcoded in Python.** Each persona template declares a `workspaces:` section with independent left/right sidebar configs per workspace (Home, Blueprint, Gallery, Test Lab). See `ui_implementation_contract.md §11` and `docs/workflows/ui_persona.qmd` for the full slot registry spec and panel type reference.

**Two-layer resolution:** (1) The persona template **slot list** controls which panel types appear and in what order. (2) Each panel type has a **gate flag** — if the flag is disabled, the panel is silently skipped. Flags and cascade rules are completely independent of the slot list.

- **Left Sidebar**: Content is workspace-dependent. Switching workspaces physically replaces the left sidebar DOM (not CSS-hide). Panel content per workspace is declared in `workspaces.<ws>.left_sidebar.panels`. Panels are registered in `app/modules/sidebar_registry.py` (`PANEL_REGISTRY`).

  **Available Home panel types** (gate flags in parentheses): `project_info` (none), `deployment_info` (none), `manifest_choice` (`manifest_selector.visible`), `filters` (`interactivity_enabled`), `data_import` (`metadata_ingestion_enabled`), `export` (`export_enabled`), `session_management` (`session_management_enabled`). See `ui_implementation_contract.md §11d` for complete table.

  **Filter behavior unchanged:** `_pending_filters` / `applied_filters` state is preserved across workspace switches; filter widgets are only mounted when `workspaces.home.left_sidebar.panels` contains `filters` and the gate flag is on.

- **Right Sidebar**: Same slot registry pattern. Current built-in types: `audit_stack` (gate: `t3_sandbox_enabled`), `notification_log` (none), `blueprint_logic` (gate: `blueprint_enabled`). Visibility is driven by `workspaces.<ws>.right_sidebar.visible` in the persona template — **not** by persona name comparison in `ui.py` (that was an ADR-053 violation, now fixed by ADR-073/task 25-O).

- **Sidebar visibility**: `visible: false` excludes the container from the DOM. Auto-hide: if all panels skip (all gate flags off) and `visible` is unset, sidebar is excluded. `visible: true` with no active panels renders an empty container (allowed for branding/info-only configs).

- **The Focus Mode (ADR-038)**: Gallery workspace left sidebar shows only `gallery_search` panel — operation controls (Import/Session) are not in its slot list, providing automatic focus mode without extra gating logic.

- **The Gatekeeper**: `btn_apply` is locked unless all T3 audit nodes have non-empty `reason` fields. Rendered only when the right sidebar `audit_stack` panel is active.

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
`interactivity_enabled`, `developer_mode_enabled`, `gallery_enabled`, `comparison_mode_enabled`, `session_management_enabled`, `import_helper_enabled`, `export_enabled`, `metadata_ingestion_enabled`, `data_ingestion_enabled`.

**`qa` persona:** Mirrors `developer` flags but sets `automation.ghost_save: false` for deterministic Playwright runs (no background ghost writes during smoke tests). It is the recommended `SPARMVET_PERSONA` for CI.

**New flags (Phase 25 / ADR-052):**
`manifest_selector.visible` — hides Manifest Choice dropdown for pipeline personas (fixed_manifest path required when false).
`testing_mode` — true = pre-fill data selector from manifest default paths; false = data injected by pipeline or chosen by user.

**Pipeline personas are always production-mode**: `pipeline-static` and `pipeline-exploration-simple` always have `testing_mode=false` and `manifest_selector.visible=false`. Testing of pipeline integrations uses a more capable persona.

**Right sidebar layout (ADR-073):** Structural exclusion is now driven by `bootloader.get_sidebar_config("home", "right").visible` — set to `false` in `pipeline-static` and `pipeline-exploration-simple` persona templates. This replaces the previous `SPARMVET_PERSONA` env-var comparison in `ui.py` (ADR-053 violation, task 25-O, fixed in SIDEBAR-REGISTRY-1). The center column fills full width when the right sidebar is excluded.

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

## 7. The Blueprint Architect Invariants (ADR-039, ADR-075, ADR-082)

The Blueprint Architect provides a "Flight Deck" for manifest design.

**Feature set lock (ADR-082).** BLUEPRINT is four composable layers; the full feature set, the MVP/v2/out-of-scope inventory, and the T1/T2-vs-T3 boundary are authoritative in ADR-082.

| Layer | Capability | Owning ADR(s) |
|---|---|---|
| L1 — Navigation | TubeMap DAG + Lineage Rail + 3-column contract viewer | ADR-039/040/074 |
| L2 — Forms | Action/component picker + 8-widget `ui_schema` renderer + **Joint Designer pane** (joins) | ADR-075, ADR-082 (BP-JOINT-1) |
| L3 — Data view | Live Data Glimpse (on-Apply) | ADR-082 |
| L4 — Helpers | AI agent + YAML escape hatch + undo + branch | ADR-075/076/082 |

**Branching = lineage bifurcation at a node (ADR-082 Q3, LOCKED).** A "branch" splits one lineage in two **at a chosen node**: upstream stays **shared** (Tier 1 trunk materialized once, branches `scan_parquet` it — no recompute), child lineages diverge downstream. Physically it is the **fragment-per-component** `!include` structure (canonical: `Summary` / `Summary_quality`) — the Bifurcation Point Rule (`rules_data_engine.md`) made interactive. The TubeMap *fan-out* is the visual; the *manifest branch* is the lineage split. Whole-manifest duplication is a separate rare path (new data only). **BLUEPRINT never authors T3** — T3 is HOME-only (ADR-082 §4).

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
- **YAML escape hatch**: always visible for any persona with `blueprint_enabled: true` (read-only view). Becomes an editable textarea only when `manifest_edit_enabled: true` (developer and qa personas). An editable escape hatch emits a `developer_raw_yaml` T3 node on save. Gate: `bootloader.is_enabled("manifest_edit_enabled")` — never a persona name check. See `rules_persona_feature_flags.md §Group D`.
- Full ADR-075 spec (widget types, color widget model, help system, action naming) lives in `architecture_decisions.md`.
