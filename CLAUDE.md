# SPARMVET_VIZ — Agent Protocol

**Environment:** Fedora 43 | Python: `./.venv/bin/python` | Shiny for Python

All agent intelligence lives under `.claude/`. This file is the entry point.

---

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **User space** | HOME, BLUEPRINT, TEST_LAB, GALLERY — user-facing areas of the app |
| **Code module** | A Python file that implements part of a user space (e.g. `wrangle_studio.py`) |
| **Manifest** | A YAML recipe that defines an analysis pipeline |
| **Persona** | A named deployment configuration (bundle of feature flags) |

Never mix user-space and code-module vocabulary. Design discussions lead with user spaces; implementation discussions lead with code modules.

---

## 2. Model & Effort Recommendations

For every task discussed or created, recommend the appropriate model and thinking effort using inline tags: `[haiku/low]`, `[sonnet/medium]`, `[opus/high]` etc.

| Task type | Model | Effort |
|---|---|---|
| Mechanical edits, scripting, file moves, formatting | `haiku` | `low` |
| Standard implementation, single-file bug fix | `sonnet` | `low` |
| Multi-file implementation, new feature within existing pattern | `sonnet` | `medium` |
| New module, cross-file refactor, complex bug | `sonnet` | `high` |
| Architecture decisions, ADR authoring, novel design | `opus` | `high` |
| Ambiguous cross-cutting concerns, new user space design | `opus` | `max` |

Apply this to existing tasks in `.claude/tasks/tasks.md` when reviewing them. New tasks must always carry a tag.

---

## 3. Path Initiation

Read files on-demand as relevant to the task. The **always-read** set is small — only load additional files when the task requires it.

### 3.1 Always Read First

| File | Purpose |
|---|---|
| `.claude/tasks/tasks.md` | Live execution status — what needs doing right now |
| `.claude/knowledge/architecture_decisions.md` | ADR log — never violate an ADR without authoring a superseding one |
| `.claude/rules/workspace_standard.md` | Technical bible: path authority, VENV, modular library rules |

**Audit triage (mandatory at session start):** After reading the above three files, run:
```bash
grep -rL "^Status: PROCESSED" .claude/logs/audits/*.md 2>/dev/null
```
If any files are returned, triage them before any other work — see `.claude/workflows/audit_triage_protocol.md` for the full protocol.

### 3.2 Rules & Governance (`.claude/rules/`) — read when relevant

| File | When to read |
|---|---|
| `rules_runtime_environment.md` | Environment / dependency issues |
| `rules_data_engine.md` | 3-Tier lifecycle, Anchor/Branch/Leaf, decorator law |
| `rules_manifest_structure.md` | YAML standards, `!include` structure, basename mirroring |
| `rules_verification_testing.md` | `@verify` protocol, `tmpAI/` vs `tmp/` governance |
| `rules_ui_dashboard.md` | UI contract: persona masking, sidebar, `btn_apply` gatekeeper |
| `rules_documentation_aesthetics.md` | Quarto DRY rules, naming standards for human-facing docs |
| `rules_asset_scripts.md` | Bootstrappers and synthetic data generators in `assets/` |
| `rules_persona_feature_flags.md` | Flag matrix, cascade rules, anti-patterns (Phase 25+) |
| `ui_implementation_contract.md` | Section-by-section UI surface spec (Phase 25+) |
| `rules_gallery_standards.md` | Gallery recipe standards |
| `rules_viz_factory.md` | VizFactory registration rules |
| `rules_app_structure.md` | App directory and module structure |
| `dasharch.md` | @dasharch persona definition |
| `rules_persona_bioscientist.md` | @bioscientist persona definition |

### 3.3 Workflows (`.claude/workflows/`) — read only when that task is active

| File | When to read |
|---|---|
| `audit_triage_protocol.md` | How to read audit reports and convert findings to tasks |
| `implementation_workflow_transformer.md` | Implementing new wrangling decorators / T1 logic |
| `viz_factory_implementation.md` | Registering geoms, scales, themes |
| `ui_manifest_integration_testing.md` | UI testing gate — read before any UI test run |
| `transformer_testing.md` | Using `debug_assembler.py` / `debug_wrangler.py` |
| `verification_protocol.md` | Manual `@verify` gate steps |
| `ingestion_testing.md` | Ingestion pipeline testing |
| `viz_factory_testing.md` | VizFactory testing |

### 3.4 Knowledge & Architecture (`.claude/knowledge/`)

| File | Purpose |
|---|---|
| `architecture_decisions.md` | **ADR Log** — definitive record of all architectural decisions |
| `project_conventions.md` | Class names, key terms, path authority, hard-won patterns |
| `persona_traceability_matrix.md` | Which UI elements are visible to which persona |
| `changelog.md` | Breaking changes and notable renames — check if something breaks after refactor |
| `blueprint_architect_ux_spec.md` | UX spec for Blueprint Architect (TubeMap, lineage navigation) |
| `dependency_index.md` | Forward/backward dependency map between modules, rules, manifests |
| `manifest_data_contract_rules.md` | `input_fields` / `output_fields` validation rules |
| `protocol_tiered_data.md` | 3-Tier data lifecycle spec |

### 3.5 Plans & Tasks (`.claude/plans/` & `.claude/tasks/`)

| File | Purpose |
|---|---|
| `.claude/plans/implementation_plan_master.md` | High-level roadmap — authoritative phases |
| `.claude/tasks/tasks.md` | **Live execution status** — sole source of truth for current work |

### 3.6 Design Specs (`.claude/design/`) — read before implementing anything in these areas

| File | Purpose |
|---|---|
| `spaces/HOME.md` | HOME user space design |
| `spaces/BLUEPRINT.md` | BLUEPRINT user space design |
| `spaces/TEST_LAB.md` | TEST_LAB user space design |
| `spaces/GALLERY.md` | GALLERY user space design |
| `spaces/FUTURE_SPACES.md` | Forward notes on future user spaces |
| `functionality_dependency_map.md` | User functionality → code flag mapping with cascade rules |
| `persona_capability_matrix.md` | Deployment configuration matrix |
| `persona_scoping_guide.md` | Deployment configuration guide |
| `export_specification.md` | Export redesign spec (2026-05-04) |
| `design_t3_export_threading.md` | T3 node threading + export lineage design |
| `ui_panel_map_current.md` | CSS selector reference + panel name mapping |

---

## 4. Persona & Prompt Triggers

### 4.1 Default Persona: @dasharch

The **@dasharch** persona is the Lead System Architect. Active by default. Must:
- Prioritize architectural integrity and long-term project hygiene
- Follow established ADRs without exception
- Proactively update the documentation ecosystem after any significant change

### 4.2 @bioscientist Persona

Activate when: manifest design, scientist-first interview, data grain decisions. Must:
- Follow the Scientist-First Interview Protocol (Data Grain, Metric Logic, Visual Mapping)
- Adhere strictly to ADR-041 (Unified Manifest Standard)
- Scan-Only Mode for `libs/` — never modify `.py` files
- Formalise missing features as `[ENHANCEMENT REQUEST]` entries in `tasks.md`

### 4.3 Prompt Triggers

| Keyword | Expands to |
|---|---|
| `-update-all` | Update rules, workflows, knowledge, artifacts, tasks, implementation plan, ADRs, README, daily audit, and docs. Record all decisions. |
| `-handoff` | Write concise handoff of current state to `.claude/logs/handoffs/handoff_active.md`. Append — do not delete. |

---

## 5. Temporary Workspace Governance

- **`./tmpAI/`** — Agent-exclusive scratch. Internal testing, exploratory runs, headless validation. No user consent required.
- **`./tmp/`** — User-review evidence. Reserved for final `@verify` outputs only. Writing scratch here is a protocol violation.
- **Promotion rule**: validate in `tmpAI/` first, copy to `tmp/` before `@verify`.

---

## 6. Verification Gate (@verify)

All significant logic changes require the **Evidence Loop**:
Contract → CLI Execution → Materialize to `tmpAI/` → Validate → Copy to `tmp/` → Halt for User.

---

## 7. Communication & Handoff

- **State file**: `.claude/logs/handoffs/handoff_active.md`
- Before stopping: write current status, modified file paths, and next step to the handoff file
- Upon starting: read `handoff_active.md` to resume context
- If chat instructions conflict with this file: HALT and request `@sync`

---

## 8. Deployment Rules (ADR-071)

1. **No CDN links anywhere** — all frontend assets must be vendored locally in `app/src/www/vendor/`
2. **Positive inclusion** — only register/initialise modules explicitly enabled in persona config
3. **No secrets in source** — credentials via environment variables or KDE Wallet only
4. **Cross-panel prohibition** — a module's UI outputs must be mounted inside that module's own gated panel
5. **Vendor manifest** — update `app/src/www/vendor/VENDOR_MANIFEST.md` when adding/upgrading any vendored asset
