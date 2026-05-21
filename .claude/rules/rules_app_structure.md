---
trigger: always_on
deps:
  provides: [rule:app_structure_law, rule:two_category_law, rule:handler_module_boundary]
  documents: [app/handlers/, app/modules/, app/src/server.py]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

# App Structure Rules (ADR-045)

**Authority:** @dasharch
**Status:** FINALIZED / ARCHITECTURAL LOCK (2026-04-23)

This rulebook governs the internal structure of the `app/` package. It enforces the decomposition of `app/src/server.py` into a thin orchestrator plus focused handler modules and a pure manifest introspection module.

---

## 1. The Two-Category Law (The Hard Boundary)

All code in `app/` falls into exactly one of two categories. **Mixing them is a protocol violation.**

| Category | Where it lives | Rule |
|---|---|---|
| **Pure manifest introspection** | `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` (Phase 29 move — ADR-067) | Zero Shiny imports. Zero `input`/`output`/`session`. Pure Python functions — importable from headless scripts, test suites, CLI tools, and export handlers without side effects. Formally shared infrastructure (ADR-074). |
| **Shiny reactive wiring** | `app/handlers/<concern>.py` | Contains `@render.*`, `@reactive.Effect`, `@reactive.Calc`. Receives shared state via explicit `define_server(...)` keyword arguments. **Never imported by non-Shiny contexts.** |

**Violation examples:**
- Adding a `@render.ui` decorator inside `manifest_navigator.py` → FORBIDDEN.
- Importing from `app/handlers/blueprint_handlers.py` in a headless debug script → FORBIDDEN (handler files carry Shiny registration side-effects).
- Calling `build_sibling_map()` directly inside `server.py` without going through a handler → ALLOWED (it is a pure function), but new callers in `server.py` should be delegated to handlers.

---

## 2. Directory Map

```
app/
├── src/
│   ├── server.py          # Thin orchestrator only (~120 lines). See §3.
│   ├── ui.py              # Static Shiny UI shell. CSS. No reactive logic.
│   └── bootloader.py      # Path authority & persona bootstrap (ADR-031).
│
├── modules/               # App-layer modules: importable and testable. May import Shiny for UI-helper classes (by design — app layer only).
│   ├── orchestrator.py         # DataOrchestrator — Tier 1 assembly bridge.
│   ├── wrangle_studio.py       # WrangleStudio — Blueprint Architect UI class.
│   ├── gallery_viewer.py       # GalleryViewer — static gallery browser.
│   ├── dev_studio.py           # DevStudio — developer diagnostic tools.
│   └── exporter.py             # SubmissionExporter — gallery submission.
│
├── handlers/              # Shiny wiring only. One concern per file.
│   ├── __init__.py
│   ├── home_theater.py         # Home mode: tabs, sidebar, filters, plots, tables.
│   ├── audit_stack.py          # Pipeline Audit: T2/T3 nodes, Apply gate, Revert.
│   ├── blueprint_handlers.py   # Blueprint Architect: manifest import, lineage, TubeMap.
│   ├── gallery_handlers.py     # Gallery: filtering, preview, clone, submission.
│   └── ingestion_handlers.py   # Ingestion & persona switching.
│
└── assets/                # Static/utility scripts (no Shiny).
    └── normalize_manifest_fields.py
```

---

## 3. `server.py` Permitted Content (Thin Orchestrator Only)

`server.py` MUST contain ONLY the following. Nothing else.

1. **Imports** of modules, handlers, and libraries.
2. **Module initialisation**: `WrangleStudio(session.id)`, `DevStudio()`, `DataOrchestrator(...)`, `VizFactory(...)`.
3. **Shared reactive state** (`reactive.Value`): `anchor_path`, `recipe_pending`, `snapshot_recipe`, `gallery_refresh_trigger`, `current_persona`.
4. **Shared reactive calcs** (`@reactive.Calc`): `active_collection_id`, `active_cfg`, `tier1_anchor`, `tier_reference`, `tier3_leaf`. These are shared because multiple handlers depend on them.
5. **Shared utility functions**: `_safe_input`, `_apply_tier2_transforms`. These are pure helpers used by multiple handlers.
6. **Five `define_server(...)` delegation calls** — one per handler module, in dependency order.

**Hard limit:** `server.py` MUST NOT grow beyond ~250 lines. Any new reactive output/effect belongs in a handler.

---

## 4. `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` — Public API

**Moved to `libs/blueprint_arch/` in Phase 29 (ADR-067).** The module is formally shared infrastructure (ADR-074) — importable from any context without Shiny side-effects.

The `ManifestNavigator (manifest_navigator.py)` module exports seven public functions (no leading underscore). Internal sub-helpers within those functions remain private.

| Public Function | Signature | Returns |
|---|---|---|
| `build_sibling_map(manifest_path_str)` | `str → dict` | `rel_path → {role, schema_id, schema_type, siblings, ingredients}` |
| `build_schema_registry(manifest_path_str, includes_map)` | `str, dict → dict` | `schema_id → {schema_type, input_fields, wrangling, output_fields, …}` |
| `build_lineage_chain(selected_rel, ctx_map)` | `str, dict → list[dict]` | Ordered `[{rel, schema_id, role, label, is_active}]` |
| `load_fields_file(abs_path)` | `Path → dict` | ADR-041 Rich Dict with ADR-014 unnesting |
| `resolve_fields_for_schema(schema_id, ctx_map, inc_map)` | `str, dict, dict → dict` | ADR-041 Rich Dict, recursive with cycle guard |
| `build_plot_lineage(plot_id, manifest_path)` | `str, str → list[dict]` | Backward trace from a plot to its T1 root (ADR-074). Used by export bundle lineage graph. |
| `get_plot_ids_in_group(group_id, manifest_path)` | `str, str → list[str]` | Forward trace — all plot IDs declared in an analysis group (ADR-074). |

**Import pattern** (from any context):
```python
from blueprint_arch.manifest_navigator import (
    build_sibling_map, build_schema_registry, build_lineage_chain,
    load_fields_file, resolve_fields_for_schema,
    build_plot_lineage, get_plot_ids_in_group
)
```

---

## 5. Handler `define_server(...)` Contract

Every handler module MUST expose exactly one entry point:

```python
def define_server(input, output, session, *, <explicit_dependencies>):
    """Registers all @render.* and @reactive.* for <concern>."""
    ...
```

**Rules:**
- `input, output, session` are always the first three positional arguments.
- All shared state and calcs MUST be passed as **keyword-only arguments** (after `*`) to prevent positional errors.
- The function MUST NOT `return` anything. Side effects (registrations) only.
- Dependencies MUST be minimal — only pass what the handler actually uses.

**Example signature:**
```python
# app/handlers/home_theater.py
def define_server(input, output, session, *,
                  active_cfg, tier1_anchor, tier_reference, tier3_leaf,
                  current_persona, anchor_path, recipe_pending, snapshot_recipe,
                  wrangle_studio, orchestrator, viz_factory, bootloader):
```

---

## 6. Ownership Matrix — Where to Make Changes

| I need to change... | Edit this file |
|---|---|
| How the Home tabs are built / left sidebar shows | `app/handlers/home_theater.py` |
| Filter recipe builder (add row / apply / reset) | `app/handlers/home_theater.py` |
| Data preview column selector | `app/handlers/home_theater.py` |
| Export results bundle (zip / plots / data / Quarto) | `app/handlers/home_theater.py` |
| The Pipeline Audit stack (Violet/Yellow nodes, Apply gate) | `app/handlers/audit_stack.py` |
| Blueprint Architect manifest import / TubeMap / Lineage Rail | `app/handlers/blueprint_handlers.py` |
| Gallery filtering, preview, clone, submission | `app/handlers/gallery_handlers.py` |
| Data ingestion / persona switching | `app/handlers/ingestion_handlers.py` |
| How manifests are parsed structurally (sibling map, registry, lineage) | `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py` |
| BLUEPRINT form catalog + `ui_schema` registry at startup | `libs/blueprint_arch/src/blueprint_arch/schema_registry.py` (ADR-075) |
| The static Shiny HTML shell / CSS | `app/src/ui.py` |
| Path authority / persona bootstrap | `app/src/bootloader.py` |
| Shared reactive state or tier calcs | `app/src/server.py` (§3 only) |
| Tier 1 assembly / Parquet materialization | `app/modules/orchestrator.py` |
| Visual plot composition / predicate pushdown ops | `libs/viz_factory/` |
| Data wrangling actions | `libs/transformer/` |

---

## 8. Home Theater Handler — Key Reactive Components (Phase 21, 2026-04-23)

`app/handlers/home_theater.py` implements the unified Home Theater (ADR-043/ADR-044/ADR-047).

### Filter Recipe Builder (Phase 21-F)

| Reactive | Type | Purpose |
|---|---|---|
| `_pending_filters` | `reactive.Value[list]` | Staging area — rows added but not yet applied |
| `applied_filters` | `reactive.Value[list]` | Committed filters — consumed by plots and data preview |

Each filter row: `{column: str, op: str, value: str|list, dtype: str}`.

**Shell stability pattern** (mandatory — see `project_conventions.md §3a`):
- `sidebar_filters` (shell): reads only `current_persona.get()`. Mounts `output_ui` slots for sub-outputs.
- `filter_rows_ui`, `filter_form_ui`, `filter_controls_ui`, `filter_t3_btn_ui`: independent `@output @render.ui` functions reading only what they need.
- Reason: re-rendering the shell destroys child `output_ui` DOM nodes — Shiny cannot rebind destroyed IDs.

**Type coercion** (`_apply_filter_rows`): auto-promotes `eq`→`in` / `ne`→`not_in` when value is a list; casts column to Utf8 for set ops; coerces scalar value to column dtype for numeric comparisons.

### Data Preview (Phase 21-D/F)

| Output | Purpose |
|---|---|
| `home_data_preview` | 100-row DataGrid — active plot dataset, with `applied_filters` + column selector applied |
| `home_col_selector_ui` | Selectize multi-select for column visibility (preview-only, does not affect plots) |

### Export Bundle (Phase 21-I / ADR-047)

| Symbol | Type | Purpose |
|---|---|---|
| `system_tools_ui` | `@output @render.ui` | Export controls: user-name input, preset radio, download button |
| `export_bundle_download` | `@render.download` (async) | Generates and yields zip bundle bytes |
| `_export_bundle_filename()` | helper | Reactive-safe filename: `YYYYMMDD_HHMMSS_<name>_results.zip` |

**Bundle contents**: `plots/` (SVG or PNG), `data/` (T1+T2 always; T3 for advanced+T3 active), `recipes/` (project YAMLs), `FILTERS.txt` (No Trace No Export trace), `report.qmd` (Quarto source), `README.txt`.

---

## 7. Verification Protocol

The decomposition refactor (Phase 22) is **behaviour-neutral** — no logic changes, only structural relocation. Verification complete (2026-04-23):

1. **Import check**: `python -c "from app.src.server import server"` — ✅ passed.
2. **Navigator unit check**: `python -c "from blueprint_arch.manifest_navigator import build_sibling_map; print('OK')"` — ✅ passed (import path updated Phase 29, ADR-067).
3. **Live UI check**: UI smoke test by user — no major regressions detected. ✅
