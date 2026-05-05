## Architecture Overview (Phase 21 / ADR-043–047, 2026-04-23)

The SPARMVET App is a **Thin Shiny Shell** (ADR-003) that orchestrates four distinct layers:

1. **Navigation (Left)**: Persona-gated controls — Project selection, context-reactive Filter Recipe Builder, System Tools (Export Bundle). Dark grey (#c0c0c0).
2. **Home Theater (Center)**: Unified results mode (ADR-043). Manifest-driven groups (`navset_pill`) → plots (`navset_card_tab`) → collapsible Data Preview. Neutral grey (#d1d1d1).
3. **Pipeline Audit (Right)**: Persona-gated (hidden for `pipeline_static`/`pipeline_exploration_simple`; full T2+T3 audit stack for ≥ advanced).
4. **Specialist Modes**: Blueprint Architect (Wrangle Studio), Gallery, Dev Studio — each routed via `sidebar_nav`.

### Directory Structure

```
app/
├── app.py                      ← Bootstrap / entry point
├── src/
│   ├── bootloader.py           ← Path authority & persona bootstrap (ADR-031)
│   ├── ui.py                   ← Static HTML/CSS shell — no reactive logic
│   └── server.py               ← Thin orchestrator (~228 lines, ADR-045)
│                                  Shared state: anchor_path, tier_toggle,
│                                  applied_filters, active_home_subtab,
│                                  current_persona, recipe_pending
│                                  Shared calcs: active_cfg, tier1_anchor,
│                                  tier_reference, tier3_leaf
│
├── modules/                    ← Importable, testable, Shiny-free
│   ├── manifest_navigator.py   ← Pure manifest introspection (ADR-045)
│   ├── orchestrator.py         ← Tier 1 assembly bridge
│   ├── wrangle_studio.py       ← Blueprint Architect UI class
│   ├── gallery_viewer.py       ← Static gallery browser
│   ├── dev_studio.py           ← Developer diagnostic tools
│   └── exporter.py             ← Gallery submission
│
└── handlers/                   ← Shiny wiring only (Two-Category Law, ADR-045)
    ├── home_theater.py         ← Home mode: tabs, filters, plots, data preview,
    │                              export bundle (ADR-043/047)
    ├── audit_stack.py          ← T2/T3 audit nodes, Apply gate, Revert
    ├── blueprint_handlers.py   ← Manifest import, TubeMap, Lineage Rail
    ├── gallery_handlers.py     ← Gallery filtering, preview, clone
    └── ingestion_handlers.py   ← Data ingestion, persona switching
```

### Key Architectural Rules

- **Two-Category Law (ADR-045):** `app/modules/` = pure Python (zero Shiny). `app/handlers/` = Shiny wiring only (never imported by headless scripts).
- **Thin Orchestrator:** `server.py` ≤ 250 lines. No reactive outputs there — all in handlers.
- **Manifest-Driven:** Home tabs, filter widgets, and data previews derive exclusively from manifest `analysis_groups` at runtime (ADR-004/ADR-043). No hardcoded tab names.
- **Shiny Shell Stability (project_conventions.md §3a):** `@render.ui` shells that mount child `output_ui` slots MUST read only slowly-changing reactives (persona). Child sub-outputs are independent `@output @render.ui` functions.

### Home Theater — Phase 21 Feature Map

| Feature | Phase | Key output IDs |
|---------|-------|---------------|
| Group pill nav | 21-D | `home_groups_nav` |
| Per-group plot tabs | 21-B | `subtabs_{group_id}`, `plot_group_{p_id}` |
| Tier toggle | 21-C | `tier_toggle` (input + reactive.Value) |
| Data preview | 21-D | `home_data_preview`, `home_col_selector_ui` |
| Filter recipe builder | 21-F | `sidebar_filters`, `filter_rows_ui`, `filter_form_ui`, `filter_controls_ui` |
| Export bundle | 21-I | `system_tools_ui`, `export_bundle_download` |

### Testing

```bash
# Import sanity check
.venv/bin/python -c "from app.src.server import server; print('OK')"

# Navigator unit check
.venv/bin/python -c "from app.modules.manifest_navigator import build_sibling_map; print('OK')"

# Full test suite
.venv/bin/python -m unittest discover app/tests
```

See `.claude/rules/rules_app_structure.md` for the complete structural rulebook and ownership matrix.
