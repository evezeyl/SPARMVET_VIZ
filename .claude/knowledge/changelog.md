# SPARMVET-VIZ Changelog
Append a new `## [date]` section for each release / breaking-change session.
Breaking changes are marked ⚠️. Renames that affect the manifest data contract are marked 🔑.

---

## [2026-05-04] — Export redesign + manifest modularisation

### Export pipeline (EXPORT-REDESIGN-1, EXPORT-REDESIGN-2)
- **Removed** separate "Export Audit Report" button and its handler (`export_audit_report_ui`, `export_audit_report_download`, `_audit_report_filename`). The `audit_report_enabled` persona flag is now unused by the UI (kept in validator for backwards compat).
- **Removed** "Single Graph Export" accordion panel from the sidebar. Functionality superseded by the scope toggle.
- **Added** 3-way scope toggle `[Global project | Active group | Active plot]` to the Export panel, gated on persona having both `export_enabled`.
- **Added** `recipes/t3_steps.yaml` to the export bundle when T3 has committed active nodes.
- **Added** "T3 Audit Trail" section to `report.qmd` — per-plot table of committed T3 steps + user justifications; deactivated nodes excluded.
- Accordion label renamed from "Global Project Export" → "Export".
- Spec: `.claude/design/export_specification.md`

### Manifest modularisation
- `1_test_data_ST22_dummy.yaml` rewritten from 1334 → ~290 lines using `!include` fragments under `config/manifests/pipelines/1_test_data_ST22_dummy/`.
- `figshare_integration.yaml` rewritten using `!include` (224 → 69 lines).
- Templates updated to current schema conventions: `simple_project_template.yaml` (canonical inline showcase), `e_coli.yaml`, `audit.yaml`.
- Fragment conventions + threshold (inline ≤80 lines / ≤2 schemas / ≤3 plots) documented in `.claude/knowledge/manifest_data_contract_rules.md` §6.

---

## [2026-05-04] — assembly_manifests → join_manifests rename

⚠️ 🔑 **Breaking change to manifest data contract** — all manifest YAML files must be migrated simultaneously.

### What changes
| Old | New | Where |
|-----|-----|-------|
| YAML key `assembly_manifests:` | `join_manifests:` | All manifest `.yaml` files (~10 config files) |
| Python dict key `"assembly_manifests"` | `"join_manifests"` | ~21 Python files in app/ + libs/ |
| Role string `"assembly"` | `"join"` | blueprint_handlers, manifest_navigator, wrangle_studio |
| TubeMap node label `"…\nAssembly"` | `"…\nJoin"` | `libs/utils/src/utils/blueprint_mapper.py` lines ~167, ~189 |
| UI labels `"◆ Assembly"`, `"Assembly Output (Input)"` | `"◆ Join"`, `"Join Output (Input)"` | `app/modules/wrangle_studio.py` |

### Motivation
"Assembly" has a specific meaning in bioinformatics (genome/contig assembly). The concept here is purely a dataset join operation. Rename avoids confusion, especially in the Cytoscape TubeMap which the team reads.

### Exception — do NOT rename
- `session_manager.py` ~line 213: `{"assembly": ..., "contracted": ...}` — this is a Parquet file path label, unrelated to the manifest role.

### Variable name rule
Never use bare `join` as a Python variable (shadows `str.join()`, confusing next to Polars). Use `join_defs`, `join_block`, `join_step`, `is_join_step` etc.

### Execution plan
See task `ASSEMBLY-RENAME` in `.claude/tasks/tasks.md` for the 5-pass VSCode checklist.

---

## [2026-05-05] — Library extraction (Phase 29)

### New libraries promoted from app/
- `libs/blueprint_arch/` — manifest navigation, TubeMap rendering, lineage tracing. Moved from `app/modules/`.
- `libs/test_lab/` — formerly `libs/dev_studio/`; unified with test infrastructure.

### Renames
- `app/modules/dev_studio.py` → `libs/test_lab_studio.py` (class retained `TestLabStudio`)
- Imports updated across `blueprint_handlers.py`, `home_theater.py`, `server.py`

### Consequence
All 8 `libs/` packages now follow the two-tier dependency model:
- Tier 1 base: `libs/utils/` (no cross-lib imports; importable by any domain lib)
- Tier 2 domain: all other libs (zero peer-to-peer imports; each independently reusable)
- Tier 3 orchestration: `app/` only (wires multiple libs together)

---

## [2026-05-09] — Sidebar slot registry + lineage + BLUEPRINT IDE design (Phases 31–32)

### Phase 31 — Sidebar configurability (ADR-073 implementation)
- **Added** `config/ui/sidebars/` — reusable panel-list YAML files per workspace/persona combination.
- **Added** `app/modules/sidebar_registry.py` — `PANEL_REGISTRY` dict maps panel types to gate flags and renderers.
- **Added** `app/modules/sidebar_validator.py` — validates sidebar configs and `!include` targets; runs at startup.
- **Added** `scripts/validate_persona_config.py` — CLI gate for personas + sidebars (used in CI).
- **Updated** all 8 persona templates with `workspaces:` section declaring left/right sidebar slot lists per workspace.
- **Fixes** ADR-053 violation: right sidebar visibility now gated via `bootloader.get_sidebar_config("home", "right").visible` instead of persona name comparisons.

### Phase 31 — Export provenance (partial, ADR-069)
- **Implemented** `LINEAGE-NAV-1`: `build_plot_lineage(plot_id, manifest_path)` and `get_plot_ids_in_group(group_id, manifest_path)` — backward and forward lineage tracing.
- **Implemented** `LINEAGE-EXPORT-1`: `lineage/lineage_graph.json` generation (shared-node DAG) + Mermaid flowchart in `report.qmd`.
- **Implemented** `BP-SCHEMA-1`: `ui_schema` kwarg in `@register_action` and `@register_plot_component`; 19 transformer actions + 7 viz_factory components annotated; `schema_registry.py` reads schemas at startup.
- **Pending** export tasks: EXPORT-HASH-2, EXPORT-VERSION-1, EXPORT-IMG-META-1, EXPORT-AUDIT-COMPLETE-1.

### Phase 32 — BLUEPRINT IDE Build Mode design (ADR-075 + ADR-076)
- **ADR-075** — BLUEPRINT form builder, action picker, Apply gate, YAML escape hatch (read-only / editable), session undo deque (20 steps), contextual help via `__doc__`.
- **ADR-076** — BLUEPRINT AI Agent Helper: adapter protocol (CLI, API, local model backends), tool-call protocol (HTML-comment fenced JSON), 7 agent tools, chat panel, session bundle artifacts.
- **Pending** all form/escape/undo/help/color/agent implementation tasks.

### ADRs authored 2026-05-09
- **ADR-073** — Sidebar Slot Registry (implemented today)
- **ADR-074** — Lineage Infrastructure as Shared Provision (2 tasks implemented)
- **ADR-075** — BLUEPRINT IDE Build Mode (7 tasks pending)
- **ADR-076** — BLUEPRINT AI Agent Helper (10 tasks pending)

---
## [2026-05-09 — afternoon] — Configuration discipline + diagnostic errors (Phase 32)

### ADRs authored
- **ADR-076 (revised)** — BLUEPRINT AI Agent Helper: §10 tool-call protocol (HTML-comment fenced JSON for `claude_cli`) + §11 subprocess isolation (per-session `cwd`, flock single-flight, auth probe). Streaming dropped from Phase 1.
- **ADR-077** — No-Silent-Suppression principle. Group D cascades are fatal validator errors, not silent bootloader rewrites. General principle: *"Silent suppression hides bugs. Silent rewriting hides intent."*
- **ADR-078** — Diagnostic Error Discipline. `DeploymentError` dataclass with five mandatory fields (component, problem, location, fix, who). Phase B delivered (PersonaValidator + server.py + CLI). Phase C committed: SidebarValidator, Bootloader, Connectors, manifest preflight, troubleshooting catalog, CLI scripts.
- **ADR-079** — Runtime Error Discipline (placeholder). Distinct treatment from ADR-078 because audience (analyst, not operator), fix surface (data/manifest, not config), and render path (Shiny, not stderr) differ. Targets ingestion / assembler / wrangler / viz_factory / T3 apply / Blueprint manifest validation.

### Tasks closed
- **BP-AGENT-FLAG-1** ✅ — `blueprint_agent_enabled` flag + config block landed in 8 templates; cascade is fatal (Rule 7).
- **DIAG-CORE-1** ✅ — `app/modules/deployment_error.py` + PersonaValidator retrofit + server.py + CLI script updated.

### Files added
- `app/modules/deployment_error.py` — `DeploymentError` dataclass + `format_errors_block` / `exit_if_errors` / `raise_if_errors` / `DeploymentFailure`.

### Files modified
- All 8 `config/ui/templates/*.yaml` — `blueprint_agent_enabled` flag + (developer/qa) `blueprint_agent:` config block.
- `app/modules/persona_validator.py` — `_FATAL_CASCADE_GATES` + Rule 7; returns `list[DeploymentError]`.
- `app/src/server.py` — `exit_if_errors()` startup gate replaces `raise ValueError(...)`.
- `app/src/bootloader.py` — Group D cascade explicitly NOT applied (per ADR-077). Docstring points at PersonaValidator.
- `scripts/validate_persona_config.py` — `format_errors_block()` for output.
- `.claude/rules/rules_persona_feature_flags.md` — Group D, Full Flag Matrix, Cascade Enforcement §4–5 (now FATAL), Misconfiguration table, Files Governed.
- `.claude/knowledge/project_conventions.md` — new sections 17 (Fail-Fast Configuration Discipline) and 18 (DeploymentError pattern).

### Convention shifts
- New cascades default to **fatal** (validator-enforced). Soft cascades require ADR justification.
- Startup-time errors MUST emit `DeploymentError` records, not bare strings or `raise ValueError`.
- Streaming SSE explicitly out of scope for the BLUEPRINT agent in Phase 1; all backends buffered.

