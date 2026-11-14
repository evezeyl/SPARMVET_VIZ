# SPARMVET_VIZ — Agent Protocol

**Environment:** Fedora 43 | Python: `./.venv/bin/python` | Shiny for Python

All agent intelligence lives under `.claude/`. This file is the entry point.

---

## 1. Vocabulary

| Term | Meaning |
|---|---|
| **User space** | HOME, BLUEPRINT, TEST_LAB, GALLERY — user-facing areas of the app |
| **Code module** | A Python file that implements part of a user space (e.g. `wrangle_studio.py`) |
| **Data analysis recipe** | A YAML file that defines how data becomes plots: the inputs, the tier steps, the joins and the plots |
| **App features** | A named set of feature flags that decides what the user may do (a file in `config/app_features/`) |

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

### 2.1 Dispatching agents (Eve, 2026-11-14)

When one session coordinates other agents (subagents started with the Agent tool). How to start and use it: `.claude/workflows/agent_dispatch_howto.md`. The agents are defined in `.claude/agents/` (model, effort and tools are fixed there).

- **A Fable session IS the coordinator** (Eve, 2026-11-14). If your model is Fable, your first action is the trigger `-coordinate` (below), and you work as the `coordinator` agent (`.claude/agents/coordinator.md`): you plan, order, dispatch, review reports, merge, report. You do not write code or tests, do not run test suites or audits, do not read large files, do not edit records. You do it yourself only: answer Eve, plan, write a brief, read up to 100 lines to write it, a one-line fix, a merge, a `git` command. Everything else goes to a worker, and when unsure you delegate. Bash is for git only (`git status`, `log`, `diff --stat`, `worktree add`, `merge`, `branch`); a test suite, an audit, a script, `shiny run` or `quarto` is always run by the `reviewer` or a builder, and the hook refuses it otherwise. A Sonnet or Opus session is not a coordinator and works as usual.
- **Start independent tasks together, in one message**, and give each worker its model (the `builder`, `builder-opus`, `scout`, `scribe`, `reviewer` agents carry it) and the effort of its tag. Wait for the reports; never repeat a running worker's job.
- **Only the coordinator may be a Fable model, and only one Fable agent runs at a time.** A dispatched agent is never Fable. Reason: three Fable workers used the whole session quota in one batch, the work stopped until the quota came back, and the coordinator was blocked too.
- **A dispatched agent runs on the model and effort of its task tag** (the table above; `haiku` or `sonnet` for almost everything). An `opus` worker only when the tag says `opus`, and then one at a time.
- **At most 3 agents at once** (5 only for read-only work), each in its own git worktree and branch, on files no other agent edits. The `reviewer` reviews every diff; the coordinator merges one branch at a time and has the `reviewer` run the full test suite after each merge.
- **An agent only implements what is decided.** A choice that is open goes back to Eve with the options; the agents never decide.
- A stopped agent is continued by a new agent of the right model **in the same worktree**, so that no work is lost.
- **The coordinator only coordinates** (Eve, 2026-11-14): it writes the briefs, reads the reports, decides the order, merges, and reports to Eve. Everything another agent can do is handed to a lighter agent that reports back: writing code and tests, running the test suites and the audits (the controls), surveys, reviews of a diff, the records (`tasks.md`, the handoff, the dependency index), preparing files for Eve. The coordinator does a thing itself only when briefing it would cost more than doing it (a one-line fix, a merge). Reason: the coordinator is the most expensive model; its tokens are for judgement, not for work.
- Every worker keeps a short progress note in its worktree (`tmpAI/progress.md`: done, next, findings), so that a stop loses nothing.
- **Changing model or effort during a task** (Eve, 2026-11-14): the coordinator stops the worker, reads its progress note, and starts a new worker of the other agent or effort in the same worktree with a new brief (done, next, instructions). Never two workers on one worktree.
- **Open choices go to a decision panel** (Eve, 2026-11-14): when a choice has two or more valid approaches, the coordinator starts, at once and for one round, two or three viewpoints (they only recommend; scratch checks only under `tmpAI/panel/`): `panel-scientist` (scientist and data scientist: correctness, transparency, reproducibility), `panel-architect` (software architect: ADRs, boundaries), `panel-developer` (developer: effort, risk, order; merged into the architect when the question is small) and `panel-user` (a user who is not a developer: is the information needed to choose shown in plain words). Before the panel, a `scout` collects what is already DECIDED and the brief tags it DECIDED / CONFIRM / OPEN. Each viewpoint answers in at most 250 words. The coordinator shows Eve one table (option, viewpoint, pro, con, evidence) plus its recommendation, flags first anything that changes a result silently, hides a step from the user or reconsiders a decision, and **stops**. The panel recommends, Eve decides.
- **Principles for every agent** (`.claude/workflows/agent_principles.md`, collected from Eve's standing rules): verify and never guess; science transparent and reproducible; deliver robust tools and inform the user of pitfalls, never choose for the user; no half fixes and no shims; tests that can fail; check what is decided first; keep it simple.
- **Briefs: aim for 10 lines, never more than 20** (the extra lines only for a complex problem; Eve, 2026-11-14). **Workers report in 15 lines or fewer**; the coordinator reads reports, not diffs or logs (a `reviewer` reads the diff).
- **Enforcement** (how it works and where it does not: `agent_dispatch_howto.md` section 7): the agent files fix each worker's model and tools; `.claude/settings.json` sets the default worker model to sonnet and refuses `Agent(model:fable)`; the hook `.claude/hooks/coordinator_guard.py` refuses, for a session in coordinator mode only (workers are not affected): Edit and Write outside `tmpAI/`, Bash commands that run suites, audits, scripts or renders, and any agent that would run on Fable (allowed: the named workers, and any other agent whose call names `model: haiku` or `sonnet`). **Use the cheapest agent that can do the task** (Eve, 2026-11-14: "you do not use a CEO of a big firm to clean your floors"): ladder in `agent_dispatch_howto.md` section 3.

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
| `rules_toolchain.md` | Tools needed to build, test and document the app, and how to call them |
| `rules_data_engine.md` | 3-Tier lifecycle, Anchor/Branch/Leaf, decorator law |
| `rules_data_analysis_recipe_structure.md` | YAML standards, `!include` structure, basename mirroring |
| `rules_verification_testing.md` | `@verify` protocol, `tmpAI/` vs `tmp/` governance |
| `rules_ui_dashboard.md` | UI contract: app features masking, sidebar, `btn_apply` gatekeeper |
| `rules_documentation_aesthetics.md` | Quarto DRY rules, naming standards for human-facing docs |
| `rules_asset_scripts.md` | Bootstrappers and synthetic data generators in `assets/` |
| `rules_app_features_flags.md` | Flag matrix, cascade rules, anti-patterns (Phase 25+) |
| `ui_implementation_contract.md` | Section-by-section UI surface spec (Phase 25+) |
| `rules_code_quality.md` | Emoji ban (active), comment philosophy, pre-deployment documentation tiers |
| `rules_gallery_standards.md` | Gallery example standards |
| `rules_viz_factory.md` | VizFactory registration rules |
| `rules_app_structure.md` | App directory and module structure |
| `dasharch.md` | @dasharch agent role definition |
| `rules_agent_role_bioscientist.md` | @bioscientist agent role definition |

### 3.3 Workflows (`.claude/workflows/`) — read only when that task is active

| File | When to read |
|---|---|
| `agent_dispatch_howto.md` | Starting a coordinator session, the workers, model and effort per task tag, the decision panel |
| `agent_principles.md` | Eve's standing principles for every agent (verify, reproducible science, inform not choose, no half fixes) |
| `design_review_personas.md` | The review method with personas (checker, scientist, data scientist, developer; others proposed) |
| `audit_triage_protocol.md` | How to read audit reports and convert findings to tasks |
| `implementation_workflow_transformer.md` | Implementing new wrangling decorators / T1 logic |
| `viz_factory_implementation.md` | Registering geoms, scales, themes |
| `ui_data_analysis_recipe_integration_testing.md` | UI testing gate — read before any UI test run |
| `transformer_testing.md` | Using `debug_assembler.py` / `debug_wrangler.py` |
| `verification_protocol.md` | Manual `@verify` gate steps |
| `ingestion_testing.md` | Ingestion pipeline testing |
| `viz_factory_testing.md` | VizFactory testing |

### 3.4 Knowledge & Architecture (`.claude/knowledge/`)

| File | Purpose |
|---|---|
| `architecture_decisions.md` | **ADR Log** — definitive record of all architectural decisions |
| `project_conventions.md` | Class names, key terms, path authority, hard-won patterns |
| `app_features_traceability_matrix.md` | Which UI elements are visible with which app features |
| `changelog.md` | Breaking changes and notable renames — check if something breaks after refactor |
| `blueprint_architect_ux_spec.md` | UX spec for Blueprint Architect (TubeMap, lineage navigation) |
| `dependency_index.md` | Forward/backward dependency map between modules, rules, data analysis recipes |
| `data_analysis_recipe_data_contract_rules.md` | `input_fields` / `output_fields` validation rules |
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
| `developer_workflow.md` | End-to-end producer journey across TEST_LAB → BLUEPRINT → GALLERY → HOME; module independence, "Send to" handoff, cross-space seams |
| `functionality_dependency_map.md` | User functionality → code flag mapping with cascade rules |
| `app_features_capability_matrix.md` | Deployment configuration matrix |
| `app_features_scoping_guide.md` | Deployment configuration guide |
| `export_specification.md` | Export redesign spec (2026-05-04) |
| `design_t3_export_threading.md` | T3 node threading + export lineage design |
| `ui_panel_map_current.md` | CSS selector reference + panel name mapping |
| `uml_model_plan.md` | UML model of the app: diagram catalogue, conventions, discrepancy checks |

---

## 4. Agent Roles & Prompt Triggers

### 4.1 Default Agent Role: @dasharch

The **@dasharch** agent role is the Lead System Architect. Active by default. Must:
- Prioritize architectural integrity and long-term project hygiene
- Follow established ADRs without exception
- Proactively update the documentation ecosystem after any significant change

### 4.2 @bioscientist Agent Role

Activate when: data analysis recipe design, scientist-first interview, data grain decisions. Must:
- Follow the Scientist-First Interview Protocol (Data Grain, Metric Logic, Visual Mapping)
- Adhere strictly to ADR-041 (unified data analysis recipe standard)
- Scan-Only Mode for `libs/` — never modify `.py` files
- Formalise missing features as `[ENHANCEMENT REQUEST]` entries in `tasks.md`

### 4.3 Prompt Triggers

| Keyword | Expands to |
|---|---|
| `-update-all` | Update rules, workflows, knowledge, artifacts, tasks, implementation plan, ADRs, README, daily audit, and docs. Record all decisions. |
| `-handoff` | Write concise handoff of current state to `.claude/logs/handoffs/handoff_active.md`. Append — do not delete. |
| `-coordinate` | Coordinator mode (section 2.1): run `mkdir -p tmpAI/coordinator && touch tmpAI/coordinator/<this session's id>` (the id is the UUID folder name in the scratchpad path), then work only as the coordinator. The hook now refuses this session's Edit and Write outside `tmpAI/`. |
| `-solo` | Leave coordinator mode: remove `tmpAI/coordinator/<this session's id>` and work as a normal session. |

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
- **Agent channel** (several sessions work in this repo at the same time): read `tmpAI/agent_channel.md` at the start, keep your row of "Working on now" current, post and delete messages, stage and commit by file name. Rule: `.claude/rules/rules_agent_channel.md` (this repository only; Eve 2026-11-13)
- If chat instructions conflict with this file: HALT and request `@sync`

---

## 8. Deployment Rules (ADR-071)

1. **No CDN links anywhere** — all frontend assets must be vendored locally in `app/src/www/vendor/`
2. **Positive inclusion** — only register/initialise modules explicitly enabled in the app features file
3. **No secrets in source** — credentials via environment variables or KDE Wallet only
4. **Cross-panel prohibition** — a module's UI outputs must be mounted inside that module's own gated panel
5. **Vendor manifest** — update `app/src/www/vendor/VENDOR_MANIFEST.md` when adding/upgrading any vendored asset

---

## 9. Working Rules: No Guessing

- **Never guess intent:** If a request has any ambiguity, missing requirements, or multiple valid architectural approaches, DO NOT write code or edit files yet.
- **Ask first:** List your specific clarifying questions (bulleted, concise) and state any assumptions you are making. Wait for Eve's confirmation before executing changes.
- **Never speculate:** Detect discrepancies, ask questions, and proceed only when everything is clear.
