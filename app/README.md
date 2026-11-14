## Architecture Overview (Phase 21 / ADR-043–047, 2026-04-23)

The SPARMVET App is a **Thin Shiny Shell** (ADR-003) that orchestrates four distinct layers:

1. **Navigation (Left)**: App features gated controls — Data analysis recipe selection, context-reactive Filter builder, System Tools (Export Bundle). Dark grey (#c0c0c0).
2. **Home Theater (Center)**: Unified results mode (ADR-043). Data analysis recipe-driven groups (`navset_pill`) → plots (`navset_card_tab`) → collapsible Data Preview. Neutral grey (#d1d1d1).
3. **Pipeline Audit (Right)**: App features gated (hidden for `pipeline-static`/`pipeline-exploration-simple`; full T2+T3 audit stack for ≥ advanced).
4. **Specialist Modes**: Blueprint Architect (Wrangle Studio), Gallery, Test Lab — each routed via `sidebar_nav`.

### Directory Structure

```
app/
├── src/
│   ├── main.py                 ← Bootstrap / entry point (`app = App(app_ui, server, ...)`)
│   ├── bootloader.py           ← Path authority & app features bootstrap (ADR-031)
│   ├── ui.py                   ← Static HTML/CSS shell — no reactive logic
│   └── server.py               ← Thin orchestrator (~240 lines, ADR-045)
│                                  Shared state: anchor_path, audit_pending,
│                                  snapshot_steps, gallery_refresh_trigger,
│                                  data_refresh_trigger, notification_log,
│                                  session_processing_issues, home_state,
│                                  active_home_subtab, tier_toggle,
│                                  current_app_features
│                                  Shared calcs: active_collection_id,
│                                  active_cfg, tier1_anchor
│
├── modules/                    ← Importable, testable, Shiny-free
│   ├── orchestrator.py         ← Tier 1/2 assembly bridge, cache keys
│   ├── wrangle_studio.py       ← Blueprint Architect UI class
│   ├── gallery_viewer.py       ← Static gallery browser
│   ├── test_lab_studio.py      ← Test Lab coordinator (renamed from dev_studio.py)
│   ├── session_manager.py      ← Session ghost files
│
│   (Pure data analysis recipe introspection — `DataAnalysisRecipeNavigator` — moved to
│    `libs/blueprint_arch/src/blueprint_arch/data_analysis_recipe_navigator.py`, ADR-067)
│
└── handlers/                   ← Shiny wiring only (Two-Category Law, ADR-045)
    ├── home_theater.py              ← Home mode: tabs, plots, data preview, sidebar dispatch
    ├── audit_stack.py               ← T2/T3 audit nodes, Apply gate, Revert
    ├── filter_and_audit_handlers.py ← Filter builder, Send to Audit, propagation modal
    ├── export_handlers.py           ← Export bundle (ADR-043/047)
    ├── session_handlers.py          ← Session save/restore/import/delete
    ├── data_import_handlers.py      ← Data Import panel (upload, assign, metadata replace)
    ├── blueprint_handlers.py        ← Data analysis recipe import, TubeMap, Lineage Rail
    ├── gallery_handlers.py          ← Gallery filtering, preview, clone
    ├── ingestion_handlers.py        ← Data analysis recipe file ingestion, app features switching
    └── test_lab_handlers.py         ← Test Lab tools (scaffolding, reconciliation, synthetic data)
```

### Key Architectural Rules

- **Two-Category Law (ADR-045):** `app/modules/` = pure Python (zero Shiny). `app/handlers/` = Shiny wiring only (never imported by headless scripts).
- **Thin Orchestrator:** `server.py` ≤ 250 lines. No reactive outputs there — all in handlers.
- **Data analysis recipe-Driven:** Home tabs, filter widgets, and data previews derive exclusively from data analysis recipe `analysis_groups` at runtime (ADR-004/ADR-043). No hardcoded tab names.
- **Shiny Shell Stability (project_conventions.md §3a):** `@render.ui` shells that mount child `output_ui` slots MUST read only slowly-changing reactives (app features). Child sub-outputs are independent `@output @render.ui` functions.

### Home Theater — Phase 21 Feature Map

| Feature | Phase | Key output IDs |
|---------|-------|---------------|
| Group pill nav | 21-D | `home_groups_nav` |
| Per-group plot tabs | 21-B | `subtabs_{group_id}`, `plot_group_{p_id}` |
| Tier toggle | 21-C | `tier_toggle` (input + reactive.Value) |
| Data preview | 21-D | `home_data_preview`, `home_col_selector_ui` |
| Filter builder | 21-F | `sidebar_filters`, `filter_rows_ui`, `filter_form_ui`, `filter_controls_ui` |
| Export bundle | 21-I | `system_tools_ui`, `export_bundle_download` |

### Testing

```bash
# Import sanity check
.venv/bin/python -c "from app.src.server import server; print('OK')"

# Navigator unit check (lib moved to blueprint_arch, ADR-067)
.venv/bin/python -c "from blueprint_arch.data_analysis_recipe_navigator import build_sibling_map; print('OK')"

# Full headless test suite (most app/tests files are pytest-style, not unittest.TestCase —
# use pytest, not `python -m unittest discover`, to run them all)
PYTHONPATH=. ./.venv/bin/python -m pytest app/tests \
  --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py \
  --ignore=app/tests/test_export_download.py --ignore=app/tests/test_every_app_features_starts.py -q
```

See `.claude/rules/rules_verification_testing.md §8` for the Playwright browser-test commands.

See `.claude/rules/rules_app_structure.md` for the complete structural rulebook and ownership matrix.
