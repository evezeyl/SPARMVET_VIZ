# Project Conventions & Quick Reference (Combat Log)

> Paths must be given according to the project root (`SPARMVET_VIZ/`), not any other folder.

## 1. File Registry (Compressed)

| Component | Purpose | I/O | Key Logic / Terms |
| :--- | :--- | :--- | :--- |
| `./.claude/` | DIRECTIVES (Rules & Workflows) | Folder | `workspace_standard`, `rules_app_structure`, `verification_protocol` |
| `./.claude/` | PROJECT STATE (Knowledge, Plans, Tasks) | Folder | `architecture_decisions`, `tasks.md`, `audit_*.md` |
| `app/src/bootloader.py` | Path Authority & Persona Bootstrapper | Config → Paths/Toggles | `Bootloader`, `persona`, ADR-031 |
| `app/src/ui.py` | 3-Zone Dashboard Shell (static HTML/CSS only) | UI Spec → Layout | `Navigation`, `Theater`, `Audit Stack` |
| `config/ui/theme.css` | Base stylesheet — injected at startup via `bootloader.get_theme_css_path()` | CSS → `ui.tags.style()` | ADR-055; personas declare `theme_css:` key to override for branding. **Full design token spec in `.claude/rules/rules_css_style_spec.md` — read before writing any CSS.** Canonical colours: primary blue `#345beb`, export teal `#10a395`, reset amber `#ffc107`. View title banners use `.view-title-banner` / `.banner-title` / `.banner-subtitle`. |
| `config/ui/sidebars/` | Shared sidebar panel-list YAML files (ADR-073) | YAML → persona template `!include` | One file per workspace×tier combination. Referenced via `!include sidebars/<name>.yaml` in persona template `workspaces:` section. |
| `app/modules/sidebar_registry.py` | Panel type registry (ADR-073) — headless-safe, Two-Category Law | `PANEL_REGISTRY` dict → type name → renderer ref + gate flag | Used by `home_theater.py` slot iteration and `SidebarValidator`. Never import Shiny here. |
| `scripts/validate_persona_config.py` | Persona + sidebar compatibility validator CLI (ADR-073) | `--persona <id>` / `--all` / `--strict` | Runs `PersonaValidator` + `SidebarValidator`. Use `--strict` in CI. Also runs at app startup (warnings logged, errors block). |
| `scripts/audit_*.py` | 13 audit scripts for automated codebase hygiene (ADR-080) | `--output .claude/logs/audits/audit_NAME_YYYY-MM-DD.md` | See `.claude/workflows/audit_routine_registry.md` for full list and `.claude/workflows/schedule_commands.md` for execution guide. |
| `scripts/run_audits.sh` | Audit wrapper — groups scripts by day slot; enforces `dev` branch (ADR-080) | `./scripts/run_audits.sh <sunday\|wednesday\|thursday\|friday\|all\|ondemand>` | Auto-switches to `dev` branch; prints unprocessed report summary at end. Session-end quick run: pass `sunday` for the four highest-value scripts. |
| `scripts/systemd/` | Systemd user timer units for persistent audit scheduling (ADR-080) | `./scripts/systemd/install.sh` (one-time setup) | `sparmvet-audit@.service` + 4 `.timer` files with `Persistent=true` — fires missed runs on next boot. See `schedule_commands.md §D`. |
| `app/src/server.py` | **Thin Orchestrator only** (ADR-045, 228 lines) | Shared state/calcs → Handler delegation | `active_cfg`, `tier1_anchor`, `tier_reference`, `tier3_leaf`, 5× `define_server()` calls |
| `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` | **Pure manifest introspection engine** (ADR-045/ADR-067/ADR-074) | Manifest path → Structural dicts | `build_sibling_map`, `build_schema_registry`, `build_lineage_chain`, `load_fields_file`, `resolve_fields_for_schema`, `build_plot_lineage`, `get_plot_ids_in_group` — importable anywhere, zero Shiny dependency |
| `libs/blueprint_arch/src/blueprint_arch/schema_registry.py` | **BLUEPRINT form catalog** (ADR-075, to be created) | `@register_action` + `@register_plot_component` `ui_schema` dicts → widget catalog | Reads `ui_schema` kwarg from registries at startup; builds action/component picker for BLUEPRINT IDE. Headless-safe — zero Shiny imports. |
| `scripts/migrate_manifests.py` | **Action name migration scanner** (ACTION-RENAME-1, to be created) | Project-wide YAML scan → rename report + apply | Scans `config/manifests/`, persona templates, `assets/gallery_data/` for deprecated action names; reports discrepancies; applies renames with `--apply` flag. |
| `app/handlers/home_theater.py` | Home Theater Shiny wiring (ADR-043/045/047) | Reactive hooks → Home UI | `dynamic_tabs`, `sidebar_nav_ui`, `sidebar_tools_ui`, `sidebar_filters`, `filter_rows_ui`, `filter_form_ui`, `home_data_preview`, `home_col_selector_ui`, `system_tools_ui`, `export_bundle_download`, `plot_group_{p_id}` |
| `app/handlers/audit_stack.py` | Pipeline Audit Shiny wiring (ADR-044/045) | Reactive hooks → Audit UI | `audit_nodes_tier2`, `audit_nodes_tier3`, `handle_apply`, `track_recipe_changes` |
| `app/handlers/blueprint_handlers.py` | Blueprint Architect Shiny wiring (ADR-039/045) | Reactive hooks → Architect UI | `_handle_manifest_import`, `_do_load_component`, `sync_blueprint_mapper`, `_handle_upload_*` |
| `app/handlers/gallery_handlers.py` | Gallery Shiny wiring (ADR-037/045) | Reactive hooks → Gallery UI | `_update_gallery_options`, `handle_gallery_clone`, `gallery_preview_img`, `gallery_md_content` |
| `app/handlers/ingestion_handlers.py` | Ingestion & persona Shiny wiring (ADR-045) | Reactive hooks → Ingest/Persona | `handle_ingest`, `update_persona_context` |
| `app/modules/orchestrator.py` | Tier 1 Ingestion & Assembly Bridge | Manifest + Data → Parquet | `DataOrchestrator (orchestrator.py)` |
| `libs/ingestion/src/ingestion/ingestor.py` | Reads sources, early validation | File → LazyFrame | `DataIngestor (ingestor.py)`, `scan_csv` |
| `libs/transformer/src/transformer/data_wrangler.py` | Layer 1 execution (Atomic) | Dataset → LazyFrame | `DataWrangler`, `@register_action` |
| `libs/transformer/src/transformer/data_assembler.py` | Layer 2 orchestration (Relational) | Multiple LFs → LazyFrame | `DataAssembler`, `sink_parquet` |
| `libs/utils/src/utils/config_loader.py` | Recursive YAML & Include Resolver | YAML → Python Dict | `ConfigManager`, `!include` |
| `libs/test_lab/src/test_lab/aqua_synthesizer.py` | [ADR-032/ADR-068] Relational Data Synthesis (SDK Core) | Schema → TSV | `clean_header`, `generate_fake_column`, `--generate_only` |
| `libs/viz_factory/src/viz_factory.py` | Artist Pillar: Plot Composition | Data + Manifest → ggplot | `VizFactory`, `Plot Layers` |
| `libs/viz_gallery/assets/refresh_gallery.py` | [ADR-037] Gallery Indexing & Integrity Refresher | CLI Tool → JSON | `refresh_gallery.py`, Pivot-Index |
| `app/modules/gallery_viewer.py` | [ADR-033/057] Split-Pane Gallery (full-width) + sidebar filter builder | Main content + sidebar UI | `GalleryViewer.render_explorer_ui()` (main), `GalleryViewer.build_sidebar_ui()` (nav_sidebar accordion — called by home_theater.py sidebar_tools_ui) |
| `protocol_tiered_data.md` | Logic Protocol for Tiers (ADR-024) | Source of Truth | Short-Circuit, Predicate Pushdown |
| `transformer_integrity_suite.py` | Automated Integrity Suite (25+ Actions) | Registry → Report | `libs/transformer/tests/` |
| `libs/ingestion/src/ingestion/excel_handler.py` | [ADR-032] Excel Workbook Normalization | XLSX → Multi-TSV | `ExcelHandler`, authoritative extraction |
| `pipeline/*.yaml` | Master configurations and nested data contracts | (Defs) → Pipeline state | `input_fields`, `output_fields` |
| `libs/*/src/*/registry.py` | Authority for valid Wrangling and Viz actions | Registry → Validation | `@register_action`, `@register_geom` |

| `libs/transformer/tests/debug_assembler.py` | Assembly debug runner — mirrors orchestrator exactly | Manifest → `tmp/EVE_contracted_*.parquet` + `.tsv` | `DataWrangler._resolve_tier`, `MetadataValidator`, join dtype norm, `final_contract` |
| `libs/viz_factory/tests/debug_gallery.py` | Headless plot renderer for manifest audit | Contracted parquet → PNG | Reads `tmp/EVE_contracted_*.parquet`; `VizFactory.render()` |
| `.claude/knowledge/dependency_index.md` | **Forward/backward dependency map** for all tightly-coupled files | — | Check before modifying any indexed file; lists `provides` / `consumed_by` / sync risk pairs |

## 2. Verification & Logging Protocol

- **Standard**: All manual verification must follow the **Evidence Loop** defined in [rules_verification_testing.md](./.claude/rules/rules_verification_testing.md).
- **Mandatory Halt**: No task is [DONE] without a `@verify` gate and materialization to `tmp/`.
- **Phase-Gating Mandate**: UI Testing and module integration are STRICTLY PROHIBITED until the explicit Headless tests pass.
- **Headless Artifact Routing**: Automatic library test outputs map to `tmp/{lib}/`, while Manifest tests route strictly to `tmp/Manifest_test/{manifest_basename}/`.
- **Manifest Architecture**: Manifests must use the "Basename Mirroring" standard (`manifest_name/` directory containing components).
- **Session Audit**: Every significant architectural or data change MUST be logged in `./.claude/logs/audit_{{YYYY-MM-DD}}.md`. Append-only.

## 3a. Shiny Reactive Shell Stability Law (2026-04-23)

Critical pattern discovered during Phase 21-F implementation. Violating this causes entire UI sections to disappear.

**Law:** A `@render.ui` output that reads a frequently-changing `reactive.Value` (e.g., `_pending_filters`) will re-render its entire DOM subtree on every change, destroying any child `output_ui` nodes. Shiny cannot re-bind destroyed output IDs — child outputs become invisible permanently until page refresh.

**Correct pattern — split into independent outputs:**
1. **Shell** (`sidebar_filters`): reads only slowly-changing reactives (persona only). Mounts stable `output_ui()` slot IDs. Never re-renders unless persona changes.
2. **Sub-outputs** (`filter_rows_ui`, `filter_form_ui`, `filter_controls_ui`, etc.): each is an independent `@output @render.ui` function reading only the reactive values it needs. Re-renders in isolation without touching sibling outputs.

**`selected=` must be explicit:** When a `@render.ui` re-renders a `ui.input_select(...)`, Shiny resets the selection to the first option unless `selected=current_value` is passed explicitly at render time. Use `safe_input(input, "fb_col", default)` to read the current selection before rendering.

**JS callbacks in selectize options:** The `render` option in selectize.js requires actual JS function objects. Passing Python strings causes `l.apply is not a function` client error. Use CSS for visual customization instead.

## 3. UI Shell Architecture (ADR-043/ADR-044/ADR-073)

- **Sidebars are declarative (ADR-073):** Left and right sidebar layouts are declared per persona template under `workspaces.<ws>.left_sidebar` / `workspaces.<ws>.right_sidebar`. Panel types are registered in `app/modules/sidebar_registry.py` (`PANEL_REGISTRY`). Persona template `!include` targets in `config/ui/sidebars/` enable shared configs across personas. `bootloader.get_sidebar_config(workspace, side)` is the runtime API. **Never hardcode sidebar panel sequences in Python** — add to the registry and declare in template.
- **Two-layer resolution:** Slot list (persona template) controls presence/order; feature flags control capability. Fully independent. A panel in the slot list with a disabled flag is silently skipped.
- **Navigation (Left, #c0c0c0)**: Workspace-dependent. Filter widgets are **context-reactive to the active plot sub-tab** — regenerated on sub-tab change, scoped to that plot's `plot_spec` aesthetics. Switching workspaces physically replaces the left sidebar DOM.
- **Theater (Center, #d1d1d1)**:
  - **Home Mode (Unified)**: Tabs driven exclusively by manifest `analysis_groups`. Each group tab contains `navset_underline` plot sub-tabs wrapped in a **collapsible accordion**. Data preview in a **separate collapsible accordion below**. No hardcoded tabs. Controlled by the **Tier Toggle** (T1/T2 always; T3-Wrangle/T3-Plot persona-gated). **Comparison Mode** (persona-gated separate toggle) splits the theater into T2-reference (left) and T3-active (right).
  - **Architect Mode (Flight Deck)**: Tri-pane vertical stack (Collapsible TubeMap → Live Plot → Live Table). Unchanged.
- **Audit/Logic Stack (Right, #c0c0c0)**:
  - **Home Mode**: Controlled by `workspaces.home.right_sidebar.visible` in persona template (ADR-073). `false` = layout element excluded (theater expands full width). `true` with `audit_stack` panel = shows T2 Violet blueprint nodes + T3 Yellow sandbox nodes (requires `t3_sandbox_enabled=true`).
  - **Architect Mode**: Active Blueprint Component Logic Stack. Controlled by `workspaces.blueprint.right_sidebar`.
- **Focus Mode (ADR-038)**: Gallery workspace left sidebar slot list contains only `gallery_search` — operation panels absent by design, not by flag suppression.
- **Thin UI (ADR-003)**: UI modules MUST NOT implement wrangling or plotting logic. Authoritative GUI specifications rely on `ui_implementation_contract.md`.
- **CSS convention (ADR-055):** All dashboard styling lives in `config/ui/theme.css` — not inline in Python code. New UI styling goes in that file (or a persona-specific override file declared via `theme_css:` in the persona template). Inline `style=` attributes are allowed only for truly one-off values that cannot be expressed as a CSS rule. `bootloader.get_theme_css_path()` resolves the active CSS path at startup.
- **Removed**: The "Analysis Theater / Viz" nav item is eliminated (ADR-043). The `theater_grid` toggle, `btn_max_plot`, `btn_max_table`, `btn_reset_theater` controls are superseded by the Tier Toggle + Comparison Mode model. The hardcoded "Inspector" tab is removed.

## 4. Path Authority Strategy (ADR-031 / ADR-048)

System storage and hardware endpoints are strictly decoupled from UI code via a deployment profile YAML. The active profile is resolved by `app/src/bootloader.py` via a **4-level priority chain** (ADR-048 §4):

| Level | Source | Used by |
|---|---|---|
| 1 | `SPARMVET_PROFILE` env var → explicit path | Galaxy XML wrapper, IRIDA container, Docker Compose, systemd |
| 2 | `~/.sparmvet/profile.yaml` | Local PC (scientist or admin places this once at setup) |
| 3 | `/etc/sparmvet/profile.yaml` | Institutional server (sysadmin places at deploy time) |
| 4 | `config/deployment/local/local_profile.yaml` | Developer running from repo root (current dev fallback) |

The first level that exists wins. If `SPARMVET_PROFILE` is set but the path doesn't exist, the Bootloader raises `FileNotFoundError` immediately (hard misconfiguration). Startup log line: `[Bootloader] Profile resolved at level N (...)`.

**Connector lifecycle (ADR-048 §11, 2026-05-02):** After profile resolution, the bootloader immediately calls `get_connector(profile)` → `connector.fetch_data()` → `connector.resolve_paths()`. The resolved paths from `resolve_paths()` are stored in `self._resolved_locations` and become the **authoritative source for all location paths**. `bootloader.get_location(key)` reads from `_resolved_locations` — never from the raw profile dict. The connector result is cached per profile path (`_resolved_locations_cache`); `fetch_data()` runs at most once per process.

Profile schema and full documentation: `config/deployment/templates/connector_template.yaml` and ADR-048.

**Persona resolution order (Phase 25-M fix):** `persona=` kwarg > `SPARMVET_PERSONA` env var > `default_persona` in deployment profile > `ValueError`. No hardcoded fallback in code — the local dev profile (`config/deployment/local/local_profile.yaml`) sets `default_persona: "developer"`.

**Flag-only gating rule (ADR-053):** Runtime code MUST use `bootloader.is_enabled(flag)` for all persona-gated decisions. Comparing `bootloader.persona` against name strings is prohibited — personas are abstract presets. Key flags: `t3_sandbox_enabled` (T3 tier + right sidebar), `interactivity_enabled` (T3 Tier Toggle + comparison mode), `session_management_enabled`, `export_enabled`, `audit_report_enabled`. See `rules_persona_feature_flags.md` §Anti-Pattern.

- **Location 1 (Raw/Ingestion)**: Path to raw external data assets.
- **Location 2 (Manifests)**: Path to pipeline definitions and wrangling recipes.
- **Location 3 (Tiers 1 & 2)**: Curated Parquet Anchors & Views (`session_anchor.parquet`).
- **Location 4 (User & Tiers 3)**: User session states, active UI leaf interactions, and autosaves.
- **Location 5 (Gallery)**: Assets gallery for cloned/submitted recipes (`assets/gallery_data/`). Governed by `gallery_index.json` (Pivot-Index).

## 5. Tiered Data Lifecycle (ADR-024)

- **Tier 1 (Anchor)**: Fully assembled Tidy Table. Materialized via `sink_parquet` in `DataAssembler`.
- **Tier 2 (Branch)**: Shared summarizes/views derived from Tier 1 for rapid analysis discovery.
- **Tier 3 (Leaf)**: User-specific reactive transient view. Predicate Pushdown enabled via `scan_parquet` of the Tier 1 file.

## 9. Manifest Construction (ADR-041)

To ensure interoperability between the Blueprint Architect UI and the Polars Backend Engines, all manifest components must adhere to the following unified standard:

### 1. The Schema (Keyed)

- **Target**: `input_fields`, `output_fields`.
- **Format**: **Dictionary** (Key = Slug).
- **Rule**: Every entry must include `original_name`, `type`, and `label`.
- **Why**: Enables high-performance $O(1)$ lookup for ingestion and contract validation.

```yaml
# input_fields.yaml
sample_id:
  original_name: "Raw_Sample_ID"
  type: categorical
  label: "Sample ID"
```

### 2. The Logic (Ordered)

- **Target**: `wrangling.tier1`, `wrangling.tier2`.
- **Format**: **Sequential List** of Action Dicts.
- **Rule**: Tiered nesting is mandatory (ADR-024).
- **Why**: Order of execution is critical for data pipelining.

```yaml
# wrangling.yaml
tier1:
  - action: "rename"
    mapping: { "old": "new" }
  - action: "filter"
    query: "new > 0"
```

### 3. Fragments (Flat)

- **Target**: All `!include` files.
- **Format**: Flat dict or list (no redundant top-level anchoring key like `input_fields:`).
- **Why**: Allows direct unnesting and recursive loading by `ConfigManager`.

---

## 6. Logic Authority & Wrangling

- **Standard**: Wrangling follows definitions in [rules_data_engine.md](./.claude/rules/rules_data_engine.md).
- **Registry Recognition**: Actions registered via `@register_action` are automatically available to `DataWrangler` and `DataAssembler`.
- **Contract Boundary**: `output_fields` is the terminal `.select()` query guarding against column drift.

## 7. Viz Factory Workflow (Artist Pillar)

- **Path**: `libs/viz_factory` (Headless).
- **A. Data-Agnostic Mapping**: Aesthetics independent of plot type.
- **B. Layer Composition**: Sequence of geoms -> scales -> themes.
- **C. Violet Component Standard**: `ComponentName (file_name.py)` ONLY for docs and README lists.
- **D. Hand-off Rule**: Conversion to Pandas ONLY at the moment of `ggplot()` initialization.

## 8. Blueprint Architect — Lineage Index (ADR-040 / ADR-045)

Five pure functions in `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` provide the manifest structural index powering the Blueprint Architect (moved to `libs/blueprint_arch/` in Phase 29, ADR-067):

| Function | Keyed by | Value summary |
| :--- | :--- | :--- |
| `build_sibling_map(manifest_path_str)` | `rel_path` (str) | `{role, schema_id, schema_type, siblings, ingredients}`. Role values: `input_fields`, `output_fields`, `wrangling`, `join`, `plot_spec`. |
| `build_schema_registry(manifest_path_str, includes_map)` | `schema_id` (str) | Full slot map: each slot is `str` (rel_path), `{"inline": val}`, or `None`. |
| `build_lineage_chain(selected_rel, ctx_map)` | — | Ordered `list[node_dict]` for the Rail; `is_active` marks the selected node. |
| `load_fields_file(abs_path)` | — | Reads standalone fields YAML with ADR-014 unnesting. |
| `resolve_fields_for_schema(schema_id, ctx_map, inc_map)` | — | Recursive field resolution with cycle guard; returns ADR-041 Rich Dict. |
| `build_plot_lineage(plot_id, manifest_path)` | — | **ADR-074.** Backward trace from a named plot ID to its T1 root. Returns ordered `list[node_dict]`. Used by the export bundle lineage graph generator. |
| `get_plot_ids_in_group(group_id, manifest_path)` | — | **ADR-074.** Forward trace — returns all `plot_id` strings declared under the given `analysis_group`. |

**Key constraint**: Only `str` rel-paths are used as ctx dict keys. Inline YAML content (`{"inline": val}`) is stored in the `siblings` dict only — never as a dict key (unhashable).

**Join ingredient resolution**: Join wrangling files have `role="join"` and `ingredients=[schema_ids]`. To load ingredient fields in the upstream accordion, resolve `schema_id → output_fields rel_path` by scanning `ctx_map` for matching `schema_id` + `role="output_fields"`. (Renamed from "assembly" — ADR-066, 2026-05-04)

**Plot spec `target_dataset` resolution**: `target_dataset` names a data schema (e.g. `"FastP"`), not necessarily a join. Upstream lookup tries three passes: (1) join output_fields, (2) any output_fields for matching schema_id, (3) input_fields fallback.

**Sidebar display labels**: `_update_dataset_pipelines` shows `"{schema_id} — {role}"` labels. Option value stays as `rel_path` for `inc_map` lookup.

**Rail / TubeMap click → full load**: Both `handle_lineage_node_click` and `_sync_selector_from_node_click` call `ui.update_select(...)` then `ui.js_eval("document.getElementById('btn_import_manifest').click();")`.

**Live View plot preview**: `architect_active_plot` uses `ConfigManager(active_manifest_path.get()).raw_config` (full manifest). `active_viz_id` is set only when `role=="plot_spec"`. `active_raw_yaml` holds only the component fragment — do not use it for rendering.

**Temporary workspace**: `./tmpAI/` is agent-exclusive scratch space (headless tests, debug artifacts). `./tmp/` is for user-review outputs only (`@verify` evidence). Both are git-ignored. See `rules_verification_testing.md` §6

---

## 11. @bioscientist Protocol (Manifest Design)

- **Mandatory Knowledge**: `config/manifests/README.md`, `rules_persona_bioscientist.md`.
- **Registry Check**: Before generating YAML, the agent MUST verify action existence in `libs/transformer/src/transformer/registry.py` and `libs/viz_factory/src/viz_factory/registry.py`.
- **Logic Breakdown**: Every manifest proposal must include the scientific rationale for joins and transformation steps.
- **Gap Detection**: If an action is missing, it becomes a `[ENHANCEMENT REQUEST]` for the **@dasharch** persona, recorded in `tasks.md`.
---

## 10. Pipeline Stability & YAML Resilience (ADR-042)

To ensure the SPARMVET data engine survives diverse YAML formatting and large-scale relational joins:

- **Reserved Word Resilience**: Wrangling rule iteration and metadata purging MUST use `isinstance(k, str)` guards. Unquoted YAML `on:` is parsed as boolean `True`; the engine handles this via explicit `.get(True)` lookups in `DataWrangler` and `DataAssembler`.
- **Type-Safety in Recoding**: All comparison predicates in `recode_values` (e.g., `starts_with`, `contains`) MUST defensively cast targets to `pl.String`. This prevents `'bool' object has no attribute 'starts_with'` errors on heterogeneous datasets.
- **Contract Mapping Logic**: The `DataAssembler` final select query uses a contract-first approach. If columns are renamed or aliased during wrangling, the `output_fields` contract (or `final_contract`) must define the mapping. The system prioritizes `original_name` for projection to ensure contract compliance even when internal keys vary.

---

## 12. Data Mutation → Plot Invalidation Pattern (`data_refresh_trigger`)

When any server-side action changes the source data (file import, data correction, cache bust), the standard mechanism to invalidate all plot renders is:

```python
# server.py — declare once in shared state
data_refresh_trigger = reactive.Value(0)

# the mutating handler — increment after writing
data_refresh_trigger.set(data_refresh_trigger.get() + 1)

# _resolve_t1_lf in home_theater.py — subscribe so all downstream renders invalidate
if data_refresh_trigger is not None:
    data_refresh_trigger.get()
```

Do NOT call `reactive.invalidate()` directly or attempt to re-trigger individual render outputs. `data_refresh_trigger` is the single broadcast signal for "source data changed, rebuild everything."

**Cache bust sequence (on import):**
1. Delete `{anchors_dir}/{ds_id}.parquet` if it exists.
2. `bootloader.set_cached_asset(project_id, ds_id, "anchor", "lf", None)` — clears the LF cache entry.
3. `data_refresh_trigger.set(data_refresh_trigger.get() + 1)` — triggers reactive invalidation of all plot renders.

---

## 13. MetadataValidator — Canonical dtype_map

`libs/transformer/src/transformer/metadata_validator.py` maps YAML `type:` string values to polars dtypes. The canonical map (as of 2026-05-02):

```python
dtype_map = {
    "string": pl.Utf8, "numeric": pl.Float64, "categorical": pl.Categorical,
    "date": pl.Date, "utf8": pl.Utf8, "character": pl.Utf8,
    "float": pl.Float64, "int": pl.Int64, "integer": pl.Int64,
    "bool": pl.Boolean, "boolean": pl.Boolean,
    # PascalCase (polars canonical names, used in some manifests)
    "Int64": pl.Int64, "Float64": pl.Float64, "String": pl.Utf8,
    "Boolean": pl.Boolean, "Date": pl.Date, "Categorical": pl.Categorical,
}
```

An unrecognised type string triggers `warnings.warn` — it does NOT silently default to string.

**Do not add `.lower()` before lookup.** The map includes both lowercase aliases and PascalCase names explicitly. Lowercasing would break `"Int64"` → `"int64"` (not in map) and similar.

---

## 14. VizFactory Continuous Scale — Custom Break Logic

To add a manifest-level break parameter to `scale_x_continuous` / `scale_y_continuous`, use `_resolve_continuous_spec(spec)` in `libs/viz_factory/src/viz_factory/scales/core.py`.

Current supported param: `breaks_integer: true` → integer-only axis ticks via `MaxNLocator`.

**Key constraint:** plotnine calls `breaks(limits)` where `limits` is a `(min, max)` tuple. A raw `MaxNLocator` instance is not directly callable with that signature. Always wrap:

```python
def _integer_breaks(lims):
    return MaxNLocator(integer=True).tick_values(lims[0], lims[1])
```

Manifest usage (must be under `params:`, not at the layer's top level):
```yaml
layers:
  - name: scale_x_continuous
    params:
      breaks_integer: true
```

---

## 15. Notification Log Pattern — `make_notifier` (UX-NOTIF-1, ADR-060)

All user-facing notifications (audit operations, import, export, session) must use `_notify` rather than calling `ui.notification_show` directly. Developer-internal handlers (Blueprint, Wrangle, Gallery clone) may use `ui.notification_show` directly.

**Usage in a new handler:**
```python
from app.handlers.notification_utils import make_notifier

def define_my_server(input, output, session, *, ..., notification_log=None):
    _notify = make_notifier(notification_log)
    ...
    # instead of ui.notification_show("✅ Done", type="success", duration=4):
    _notify("✅ Done", type="success", duration=4)
```

**Threading `notification_log` to a new inner handler:**
- Add `notification_log=None` to the inner `define_*` signature.
- Pass `notification_log=notification_log` from the outer `define_server` call.
- In `server.py`, `notification_log` is already in shared state and passed to `home_theater.define_server`.

**Rules:**
- `notification_log` is a `reactive.Value([])` — items are `{"ts": "HH:MM:SS", "msg": str, "type": str}`.
- `_notify` is constructed ONCE at define-time, not inside reactive closures.
- `notification_log=None` → graceful fallback to plain toasts (safe for tests or contexts that don't need logging).
- Keep last 20 entries — `make_notifier` enforces this automatically.
- **Ghost persistence (UX-NOTIF-2, 2026-05-09):** `notification_log` is serialized to the T3 ghost. `session_manager.write_t3_ghost()` accepts `notification_log: list | None`; `session_handlers.py` restores it after loading a ghost. Old ghosts without the key fall back to `[]` silently.

---

## 16. Gallery recipe_meta.md Standard Format (ADR-061)

Every `assets/gallery_data/<recipe>/recipe_meta.md` must follow this structure:

```markdown
## [Recipe Name]

> 📊 [Family] · 🔢 [Data Pattern] · 📈 [Difficulty]

### Suitability (When to Use)
…

### Data Schema (Tier 1)
…

### Transformation Logic (Tier 2)
…

### Interpretations & Assumptions
…

### Inspiration & Resources
…
```

**Rules:**
- `##` is the recipe name — the ONLY h2 in the file. No "Recipe Metadata:" prefix.
- The `> ` blockquote immediately after the h2 is the taxonomy tag strip. It must contain all three classification values separated by ` · `. No other blockquotes at the top level.
- Content sections use `###` (h3). Never use `##` for sections.
- `h4`/`h5`/`h6` are available for rare sub-sections within a `###` block.

**Rationale:** the previous format used `##` for both taxonomy lines and section headings — visually indistinguishable. The blockquote tag strip is compact, left-bordered, and semantically distinct.

**Reference:** `assets/gallery_data/recipe_template.md` is the canonical template.

---

## 17. Fail-Fast Configuration Discipline (ADR-077, 2026-05-09)

**Principle:** *Silent suppression hides bugs. Silent rewriting hides intent. The default response to a contradictory configuration is to halt with a clear error, not to guess what the operator probably meant.*

**Rule for new flag dependencies:** when adding a flag with a parent gate, default to **fatal** (validator-enforced) cascade. Soft (silent-suppression) cascades are an explicit backwards-compatibility exception, not a pattern to copy.

| Cascade type | Where enforced | When to use |
|---|---|---|
| **Fatal** | `PersonaValidator._FATAL_CASCADE_GATES` + Rule 7 — startup error blocks app | Default for any new flag-dependency. Examples: ADR-075 `manifest_edit_enabled`, ADR-076 `blueprint_agent_enabled`. |
| **Soft** | `bootloader._load_persona_config()` — silently sets child to false + warning | Legacy compatibility only (Group B `interactivity_enabled`, Group C `import_helper_enabled`). Do NOT use for new flags without explicit ADR justification. |

**ADR authoring rule:** every ADR introducing a new flag MUST declare cascade type explicitly with rationale. The cascade type is documented in `rules_persona_feature_flags.md` Cascade Enforcement § when the rule is added.

---

## 18. Diagnostic Error Discipline — `DeploymentError` (ADR-078, 2026-05-09)

**Use this whenever a startup-time failure is surfaced to the operator.**

```python
from app.modules.deployment_error import DeploymentError, exit_if_errors

errors: list[DeploymentError] = []
if some_check_fails():
    errors.append(DeploymentError(
        component="MyValidator",                # who emitted it
        problem="One sentence — what is wrong",
        location="path/to/file.yaml or features.foo in path/...",
        fix="Concrete remediation. Name the file. Name the key. Name the value.",
        who="operator",                         # operator | developer | both
        reference=".claude/rules/<rule_file>.md §<section> + ADR-<N>",
        related=("other_flag", "other_file"),  # optional
    ))
exit_if_errors(errors, header="My component failed validation")
```

**Five mandatory fields:** `component`, `problem`, `location`, `fix`, `who`. Optional: `reference`, `related`. Format is fixed across every component so operators and log-scrapers can rely on it.

**Where to use:**

| Context | Pattern |
|---|---|
| Validator returns errors to caller | `def validate(...) -> list[DeploymentError]` |
| Startup integration point | `exit_if_errors(errors)` — prints formatted block to stderr + `sys.exit(1)` |
| Embedded server / test harness | `raise_if_errors(errors)` — raises `DeploymentFailure` with structured payload |
| CLI script | `print(format_errors_block(errors), file=sys.stderr)` + non-zero exit |

**`who` field semantics:**
- `operator` — config edit fixes it; no code change needed (most common). Galaxy admins, NVI lab techs, Posit Connect operators.
- `developer` — code change required. Module bug, broken contract, missing implementation.
- `both` — config issue that also reveals an underlying design problem worth raising.

**`fix` field discipline:** "Invalid configuration" is a diagnostic failure. "Set `blueprint_agent_enabled: false` in `developer_template.yaml`" is a diagnostic success. Always name the file, the key, and the new value.

**Roadmap:** Phase B (DIAG-CORE-1, ✅) covers PersonaValidator. Phase C (committed work, see `tasks.md` "Diagnostic Error Discipline" block) retrofits SidebarValidator, Bootloader, Connectors, manifest preflight, plus a `docs/troubleshooting/` reference catalog. Runtime errors (ingestion / assembler / wrangler / viz_factory / T3 apply / Blueprint) are deferred to ADR-079 because their audience and render path differ.

**Forbidden patterns:**
- `raise ValueError(f"validation failed: {'; '.join(strs)}")` at startup boundaries
- bare `print` warnings for errors that should block startup
- swallowing exceptions silently (e.g. bare `except:` returning empty results)

---

## 17. BLUEPRINT AI Agent Adapter Pattern (ADR-076)

**Entry point:** `bootloader.get_agent_adapter()` — returns a cached adapter instance.

```python
adapter = bootloader.get_agent_adapter()          # ClaudeCliAdapter or DisabledAdapter
if adapter.is_disabled:
    # show banner; do not render chat panel
    ...
else:
    from blueprint_arch.agent_context import build_system_prompt, build_turn_context
    system_prompt = build_system_prompt(
        manifest_path=active_manifest_path,
        instructions_file=bootloader.get_agent_config().get("instructions_file"),
        project_root=bootloader.project_root,
    )
    context = build_turn_context(active_workspace="blueprint")
    session_id = adapter.start_session(system_prompt, context)
    response = adapter.send_message(session_id, user_message)
    # response.content contains the text (fenced tool calls embedded for claude_cli)
    # use agent_tool_parser.py to extract tool calls from content
```

**Module locations** (all headless-safe, zero Shiny imports):
- `libs/blueprint_arch/src/blueprint_arch/agent_adapter.py` — `AgentAdapter` protocol, `ClaudeCliAdapter`, `DisabledAdapter`, `make_adapter()`
- `libs/blueprint_arch/src/blueprint_arch/agent_context.py` — `build_system_prompt()`, `build_turn_context()`
- `libs/blueprint_arch/src/blueprint_arch/agent_tool_parser.py` — (BP-AGENT-PARSER-1, pending) fenced-block extractor
- `libs/blueprint_arch/src/blueprint_arch/agent_tools.py` — (BP-AGENT-TOOLS-1, pending) 7 MVP tools

**Session directory isolation (ADR-076 §11):** Each session runs in `{project_root}/agent_sessions/{uuid}/` with a `.cwd-marker` so Claude Code scopes its conversation history to that dir — isolated from the user's main terminal session. Lock file (`lock`) enforces single-flight within a session.

**Fenced-block tool-call protocol (ADR-076 §10.1):** `ClaudeCliAdapter` instructs the model (via system prompt) to emit tool calls as:
```
<!-- AGENT_TOOL_CALL -->
```json
{"tool": "propose_manifest_diff", "arguments": {...}}
```
<!-- /AGENT_TOOL_CALL -->
```
Parser extracts these; any text outside the markers is conversation.

**`--output-format text` note:** The implementation uses `--output-format text` (not `json`) for simplicity — `result.stdout.strip()` is the full response content. ADR-076 uses `json` format in the spec; implementation deviation is harmless and simplifies content extraction.

**Bootloader config accessor:**
```python
cfg = bootloader.get_agent_config()
# {'backend': 'claude_cli', 'instructions_file': '...', 'gallery_awareness': False, ...}
```

**Fallback discipline:** `make_adapter()` catches all `RuntimeError` from `ClaudeCliAdapter.__init__` (missing binary, not logged in) and returns `DisabledAdapter(reason)`. App startup is never blocked by an agent misconfiguration.


## 15. Palette Registry & VizFactory Palette Injection (ADR-081)

### File: `config/palettes.yaml`

Deployment-level palette registry. Optional — system always falls back to the built-in `sparmvet_brand` palette.

```yaml
palettes:
  my_palette:
    - "#1D5B8B"
    - "#E8A020"
```

Loaded by `bootloader.get_palettes()` at startup. Returns `{name: [hex, ...]}` dict — never empty (`sparmvet_brand` always present). Emits INFO when file absent; WARNING with file path + parse error when file malformed.

### Bootloader API

```python
bootloader.get_palettes()          # → {name: [hex, ...]} — never empty
```

### VizFactory construction

```python
# app/src/server.py — the only call site
VizFactory(palette_registry=bootloader.get_palettes())
```

VizFactory is **library-autonomous**: works with only `_BUILTIN_PALETTES` when `palette_registry=None`. Never reads `config/palettes.yaml` directly — ADR-011 boundary.

### Manifest usage

```yaml
# Manifest-level default (applies to all plots):
plot_defaults:
  palette: nvi_official

# Per-plot override:
plots:
  my_plot:
    palette: sparmvet_brand
```

### Scale injection (VizFactory._apply_palette)

| Palette source | Scale injected |
|---|---|
| Project registry hit | `scale_fill_manual` / `scale_color_manual` (hex list) |
| Viridis family name | `scale_fill_viridis_d` / `scale_color_viridis_d` |
| Other matplotlib name | `scale_fill_brewer` / `scale_color_brewer` |
| Unknown name | WARNING listing valid project palette names |

Guards: only injects for aesthetics in mapping; never overwrites existing `scale_fill_*`/`scale_color_*` layers.
