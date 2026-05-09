Status: PROCESSED 2026-05-09 — DOC-DRIFT-1 + DOC-DRIFT-EMOJI fixed in-session; 4 content-gap tasks created (DOC-GAP-1 through 4)
# Audit Report: Rules → docs Propagation — 2026-05-09

## Summary
- ADRs / rules checked: 10 priority items + 17 rule files
- Propagated cleanly: 5
- Drifted (partial propagation): 3
- Missing entirely from user-facing docs: 2

## Findings

### [DRIFTED] ADR-067 — manifest_navigator.py library extraction
**Source rule/ADR:** `.claude/knowledge/changelog.md` (2026-05-05); `rules_runtime_environment.md`
**Material to users?:** Yes (developer/operator docs)
**Status in docs:** DRIFTED — inconsistent across docs
**Evidence:** `docs/workflows/dashboard_app.qmd:69` still references the old path `app/modules/manifest_navigator.py`. `docs/foundations/core_architecture.qmd` correctly shows `libs/blueprint_arch/` (with ADR-067 cite).
**Suggested fix:** Update `docs/workflows/dashboard_app.qmd:69` to reference `libs/blueprint_arch/src/blueprint_arch/manifest_navigator.py`.

### [USER-FACING-MISSING] ADR-052 — 8 personas (qa, demo-vetinst, web-demo missing from user docs)
**Source rule/ADR:** `rules_persona_feature_flags.md` §5; changelog 2026-05-09
**Material to users?:** Yes (operators deploying CI/demo systems)
**Status in docs:** INCOMPLETE
**Evidence:** `docs/workflows/ui_persona.qmd` line 25 ("The Five Personas") documents only 5 base personas. `qa`, `demo-vetinst`, and `web-demo` are absent. Templates exist in `config/ui/templates/`.
**Suggested fix:** Expand `docs/workflows/ui_persona.qmd` to document all 8 personas. Note explicitly that `qa` is the recommended `SPARMVET_PERSONA` for CI (deterministic — no ghost saves), and that `demo-vetinst` / `web-demo` are demo deployment templates.

### [USER-FACING-MISSING] ADR-076 — BLUEPRINT AI Agent Helper
**Source rule/ADR:** changelog 2026-05-09 PM; `rules_persona_feature_flags.md` Group D
**Material to users?:** Yes (operator config — backend, model, instructions)
**Status in docs:** MISSING
**Evidence:** `docs/workflows/ui_persona.qmd:213-216` mentions `manifest_edit_enabled` cascade but does not mention `blueprint_agent_enabled`, the `blueprint_agent:` config block (`backend`, `model`, `api_key_env`, `instructions_file`, `gallery_awareness`), or the system-prompt files in `config/ui/agents/*.md`.
**Suggested fix:** Add a section to `docs/workflows/ui_persona.qmd` covering: the flag, the config block schema, the available backends (`claude_cli`, `claude_api`, `disabled`), and how to point at a custom instructions file. Cross-link from `rules_persona_feature_flags.md`.

### [DRIFTED] ADR-077 — Fatal cascade enforcement (Group D)
**Source rule/ADR:** changelog 2026-05-09 PM; `rules_persona_feature_flags.md §4-5`
**Material to users?:** Yes (operator config — misconfiguration causes startup failure)
**Status in docs:** INCOMPLETE
**Evidence:** `docs/workflows/ui_persona.qmd:216` mentions cascade only for `manifest_edit_enabled`. The `blueprint_agent_enabled` fatal cascade is not in user docs. Cascade table at lines 146–162 omits it too.
**Suggested fix:** Update the cascade table to list both `manifest_edit_enabled` AND `blueprint_agent_enabled` as fatal validator errors when `blueprint_enabled: false`. Quote the exact PersonaValidator Rule 7 message so users can recognise it.

### [DRIFTED] ADR-073 — Sidebar slot registry: missing panel type
**Source rule/ADR:** `ui_implementation_contract.md §11`; changelog 2026-05-09
**Material to users?:** Yes (operators customising sidebars)
**Status in docs:** DRIFTED — built-in panel type list is incomplete
**Evidence:** `docs/workflows/ui_persona.qmd` §"Sidebar Configuration (ADR-073)" (lines 289–410) is comprehensive but the built-in panel-type table at lines 366–379 omits `blueprint_agent_chat` (added with ADR-076).
**Suggested fix:** Add `blueprint_agent_chat` row to the panel-type table (gate: `blueprint_agent_enabled`, workspace: blueprint right).

### [OPERATOR-FACING-MISSING] ADR-074 — Lineage infrastructure as shared provision
**Source rule/ADR:** changelog 2026-05-09; `rules_persona_feature_flags.md`
**Material to users?:** Yes (operators / scripted export consumers)
**Status in docs:** PARTIAL
**Evidence:** `docs/user_guide/understanding_your_export.qmd` documents lineage in export bundles. `docs/foundations/core_architecture.qmd` lists the new public API functions (`build_plot_lineage`, `get_plot_ids_in_group`). What is missing: an operator-facing note about how the export-scope toggle interacts with lineage, and how to consume these functions from external scripts.
**Suggested fix:** Add a short subsection to `docs/deployment/deployment_guide.qmd` (or a new `docs/reference/lineage_api.qmd`) showing the import path and a 5-line script example.

## Items in clean state (current)

- **ADR-075 — Form generation from ui_schema** — `docs/appendix/transformer_actions.qmd §0` and `docs/appendix/viz_factory_components.qmd §0` are comprehensive and current.
- **ADR-055 — CSS in `config/ui/theme.css`** — `docs/workflows/ui_persona.qmd:224-236` and `docs/reference/ui_style_guide.qmd` cover the mechanism and per-persona overrides.
- **ADR-048 — Deployment profile (`SPARMVET_PROFILE`)** — `docs/deployment/deployment_guide.qmd §2` documents the resolution chain.
- **Phase 25-E sidebar split** — `docs/workflows/ui_persona.qmd` documents the three accordion panels (`data_import`, `session_management`, `export`) separately.

## Recently-added rule files without docs counterpart

| Rule file | Has docs counterpart? |
|---|---|
| `workspace_standard.md` | No user-facing equivalent (acceptable — internal authority document) |
| `rules_code_quality.md` | No user-facing equivalent (acceptable — agent-internal code-style spec) |
| `dasharch.md` | No user-facing equivalent (acceptable — agent persona definition) |
| `rules_verification_testing.md` | Only partial coverage in `docs/workflows/audit_scripts.qmd` |

The first three are intentionally internal; only `rules_verification_testing.md` has a partial-coverage gap that operators of CI pipelines might want to read about.

## Severity rollup

| Item | Severity |
|---|---|
| ADR-067 path drift in dashboard_app.qmd | DRIFTED |
| ADR-052 — 3 personas missing from user docs | USER-FACING-MISSING |
| ADR-076 — agent helper not in user docs | USER-FACING-MISSING |
| ADR-077 — fatal cascade scope incomplete | DRIFTED |
| ADR-073 — `blueprint_agent_chat` panel type missing from table | DRIFTED |
| ADR-074 — operator-facing lineage doc gap | OPERATOR-FACING-MISSING |
