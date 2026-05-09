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

## [2026-05-05] — Library extraction & module decomposition

### Phase 29: Library extraction

- **New library:** `libs/blueprint_arch/` — extracted `manifest_navigator.py` (core lineage introspection) + `blueprint_mapper.py` (TubeMap DAG generation) from `app/modules/` into a standalone, headless-safe lib.
- **New library:** `libs/test_lab/` — extracted `dev_studio.py` → `test_lab_studio.py` for data utilities and developer diagnostics.
- All imports updated across `app/handlers/` and `app/src/` to reference new lib paths.
- ADR-067: Library extraction standards for headless-safe modules.

---

## [2026-05-09] — Sidebar slot registry & feature flag enforcement

### Phase 31: Sidebar slot registry (ADR-073)

- **Manifest-driven sidebars:** Sidebar panel layout now declarative via persona templates, not hardcoded in Python.
- **Registry:** `app/modules/sidebar_registry.py` — maps panel types (`project_info`, `filters`, `audit_stack`, `blueprint_agent_chat`, etc.) to gate flags.
- **Slot lists:** `config/ui/sidebars/` directory with per-workspace panel sequences (home_standard_left.yaml, blueprint_standard_right.yaml, etc.).
- **Validation:** `app/modules/sidebar_validator.py` — checks panel types against registry, includes existence, gate-flag consistency. Runs at startup alongside PersonaValidator.
- **Right sidebar exclusion fix (task 25-O):** Replaces `bootloader.is_enabled("t3_sandbox_enabled")` hardcoded checks with `bootloader.get_sidebar_config("home", "right").visible` — eliminates ADR-053 (persona name string comparison) violation.
- Verified: 8/8 persona templates pass validation.

### Phase 31 (continued): ADR-077, ADR-078 fatal cascades & DeploymentError

- **ADR-077:** Group D cascades (manifest_edit_enabled, blueprint_agent_enabled) now fatal validator errors, not silent bootloader suppression. Establishes no-silent-suppression principle for config decisions.
- **ADR-078:** DeploymentError dataclass + helpers (`format_errors_block`, `exit_if_errors`, `raise_if_errors`) in `app/modules/deployment_error.py`. PersonaValidator retrofitted to return `list[DeploymentError]`. Server startup uses `exit_if_errors` gate.
- **Verified:** 8/8 templates pass; synthetic 3-violation config produces clean formatted error block.
- Phase B (startup gate): IMPLEMENTED. Phase C (full retrofit to bootloader, connectors, manifest preflight): deferred.

### Phase 31 (continued): Feature implementation

- **BP-AGENT-PANEL-1:** `blueprint_agent_chat` panel registered in sidebar registry; added to BLUEPRINT workspace right sidebar for developer/qa personas.
- **BP-AGENT-CSS-1:** `.bp-agent-container`, `.bp-agent-message`, `.bp-agent-input-area` CSS rules in `config/ui/theme.css` (§19).
- **21-F-7:** Added `scale_x_discrete` layer to Year-based test plots in 2_test_data_ST22_dummy (ensures Year columns render as discrete categories).
- **TubeMap aesthetics:** Renamed `ref` node type → `add` in blueprint_mapper.py for semantic clarity (additional_datasets now render as "Add Data" nodes).
- **HELP-DOCS-1:** Conditional docs bundling — app checks for `docs/_site/` at startup and logs availability. DEPLOYMENT_CHECKLIST.md documents `quarto render docs/` as pre-deployment routine.

---

## [2026-05-09] — ADR 066–076 rollup

| ADR | Title | Status |
|-----|-------|--------|
| ADR-066 | Rename `assembly_manifests` → `join_manifests` — avoids bioinformatics term collision; affects all manifest YAMLs and ~21 Python files | DECIDED |
| ADR-067 | Extract `libs/blueprint_arch/` — pure-Python manifest navigation + TubeMap; headless-safe, zero Shiny imports | DECIDED |
| ADR-068 | Extract `libs/test_lab/` — absorbs `generator_utils`, renames `dev_studio.py` → `test_lab_studio.py` | DECIDED |
| ADR-069 | Complete Export Audit Trail Standard — T3 recipe IS the audit trace; auto-included in `report.qmd`; no separate FILTERS.txt for T3 | DECIDED |
| ADR-070 | Functionality-First Deployment Model — personas are named flag bundles, not the primary concept; behavior is always flag-driven | DECIDED |
| ADR-071 | Deployment Hardening Standard — no CDN links; all assets vendored locally; no secrets in source; cross-panel output prohibition | DECIDED |
| ADR-072 | [RESERVED] — numbering gap; no decision recorded | N/A |
| ADR-073 | Configurable Sidebar Slot Registry — sidebar layout declared per-workspace in persona templates; two-layer flag resolution | DECIDED / IMPLEMENTED |
| ADR-074 | Lineage Infrastructure as Shared Provision — `build_plot_lineage` + `get_plot_ids_in_group` in `libs/blueprint_arch/`; export bundle includes lineage DAG | DECIDED / PARTIAL |
| ADR-075 | BLUEPRINT IDE Build Mode — `ui_schema` form builder; action picker; YAML escape hatch; 20-step undo; contextual help | DECIDED / PENDING |
| ADR-076 | BLUEPRINT AI Agent Helper — multi-backend adapter (CLI/API/local); 7 agent tools; HTML-comment tool-call protocol | DECIDED / PENDING |

---

## [2026-05-09] — Audit session (P0/P1 hygiene)

### Phase 32: Audit & documentation (IN PROGRESS)

- **P0 completed:** AUDIT-DEPGRAPH-NOW (deps graph regenerated), AUDIT-HANDOFF-UPDATE (handoff rewritten), AUDIT-RULES-FLAGS-UPDATE (removed stale known-violation annotations; no runtime persona name checks found), AUDIT-ADR072-STUB (ADR-072 reserved stub confirmed; ADR-069 moved to correct chronological position), AUDIT-QUALITY-WRANGLING (empty unreferenced `Quality_metrics_assembly_wrangling.yaml` deleted), AUDIT-PHANTOM-TEST (phantom `test_config_loader.py` reference not present in file — no-op), AUDIT-CHANGELOG-UPDATE (this entry).
- **P0 remaining:** AUDIT-WRANGLE-FLAG (`wrangle_studio_enabled` flag addition to PersonaValidator).
- **P1 queued:** AUDIT-DEMO-PERSONAS (flag matrix demo columns), AUDIT-ABROMICS-CHECK (pipeline manifest structure assessment), AUDIT-PLAN-ORDER (implementation_plan_master.md phase reordering — escalated to sonnet/medium).

---

## Prior phases (Archives)

For phases 3–27, see git log or ADRs 1–76 in `.claude/knowledge/architecture_decisions.md`.

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

