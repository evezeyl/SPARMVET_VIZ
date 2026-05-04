# 🛸 SPARMVET_VIZ: Unified Agent Protocol (v1.0)

## 1. Core Authority & Context

- **Root Authority**: `/.agents/rules/workspace_standard.md`
- **Default Persona**: All agents MUST adopt the **@dasharch** persona by default unless explicitly instructed otherwise - defined in `.agents/rules/dasharch.md`.
If specified otherwise, the agent MUST adopt the **@bioscientist** persona - defined in `.agents/rules/rules_persona_bioscientist.md`.

- **Read Order**: You MUST read files in the order defined in the Master Index before generating code.
- **Environment**: OS: Fedora 43 | Python: `./.venv/bin/python` | Pinned: v1.19.6.
- **Mode of action** You are equipped with a modular rule system. Do not guess logic. You MUST identify and read the relevant files defined in next section "## 2. PATH INITIATION:" , from the following directories BEFORE executing a task.

## 2. PATH INITIATION

### 2.1. Rules & Governance (`./.agents/rules/`)

These files define the "how" and "where" of project execution. They are critical for ensuring the agent uses the correct Python environment and follows established coding standards.

|**File Path**|**Short Description**|
|---|---|
|`workspace_standard.md`|**The Technical Bible.** Defines mandatory read order, path authority (VENV), and modular library rules.|
|`rules_runtime_environment.md`|**Environment Lock.** Pinned system versions (IDE v1.19.6), VENV enforcement, and "Clear Lines" library policy.|
|`rules_data_engine.md`|**Data Protocols.** Defines the 3-Tier Lifecycle (Anchor/Branch/Leaf) and the "Law of Decorators".|
|`rules_manifest_structure.md`|**YAML Standards.** Mandates "Basename Mirroring" and `!include` structure for manifest components.|
|`rules_verification_testing.md`|**The Audit Gate.** Establishes the `@verify` protocol and the mandatory segregation between `tmpAI/` (Agent scratch) and `tmp/` (User review).|
|`rules_ui_dashboard.md`|**UI Contract.** Persona masking rules, Sidebar behaviors, and the `btn_apply` gatekeeper logic.|
|`rules_documentation_aesthetics.md`|**The Violet Law.** Enforces Quarto DRY rules and standard naming for human-facing docs.|
|`rules_asset_scripts.md`|**Utility Governance.** Manages the use of bootstrappers and synthetic data generators in `assets/`.|
|`rules_persona_feature_flags.md`|**Persona Flag Authority.** Authoritative flag matrix, dependency cascade rules, and the anti-pattern prohibition on persona name string comparisons. Added Phase 25.|
|`ui_implementation_contract.md`|**UI Implementation Contract.** Section-by-section spec for every UI surface: session management, export panels, filter builder, T3 sandbox, reactive write discipline. Added Phase 25.|


---

### 2.2. Workflows (`./.agents/workflows/`)

These provide step-by-step instructions for specific technical tasks. Give these to the agent _only_ when that specific phase is active.

|**File Path**|**Short Description**|
|---|---|
|`implementation_workflow_transformer.md`|Protocol for implementing new wrangling decorators and Tier 1 logic.|
|`viz_factory_implementation.md`|Protocol for the "Artist Pillar"—registering geoms, scales, and themes.|
|`ui_manifest_integration_testing.md`|**The Master Gate.** Strictly prohibits UI testing until all headless audits pass.|
|`transformer_testing.md`|Specific steps for using `debug_assembler.py` and `debug_wrangler.py`.|
|`verification_protocol.md`|Centralized instructions for triggering manual user verification gates.|

---

### 2.3. Knowledge & Architecture (`./.antigravity/knowledge/`)

These track the "why" and the long-term state of project intelligence.

|**File Path**|**Short Description**|
|---|---|
|`architecture_decisions.md`|**ADR Log.** The definitive record of all architectural decisions (ADR-001 through ADR-052+).|
|`project_conventions.md`|**Combat Log.** A compressed registry of class names, key terms, path authority, and hard-won patterns.|
|`persona_traceability_matrix.md`|**UI Logic.** Authoritative mapping of which UI elements are visible to which persona profile.|
|`milestones.md`|Historical record of project phases (Legacy → Skeleton → Prototyping).|
|`blockers.md`|Tracking of technical debt and unresolved data orchestration challenges.|
|`blueprint_architect_ux_spec.md`|UX spec for the Blueprint Architect panel (TubeMap, lineage navigation). Added Phase 22+.|
|`dependency_index.md`|Forward/backward dependency map between engine modules, rule files, manifests, debug scripts.|
|`manifest_data_contract_rules.md`|Data contract rules for manifest `input_fields` / `output_fields` validation.|
|`protocol_tiered_data.md`|Protocol spec for the 3-Tier (Anchor/Branch/Leaf) data lifecycle.|
|`refactor_protocol_phase24.md`|Reusable refactor protocol (used for Phase 24 decomposition and Phase 25). Handler decomposition rules.|

---

### 2.4. Plans & Tasks (`./.antigravity/plans/` & `tasks/`)

These represent the active roadmap and granular execution status.

|**File Path**|**Short Description**|
|---|---|
|`implementation_plan_master.md`|**Authoritative Roadmap.** Tracks high-level phases (currently Phase 12-A) and technical goals.|
|`tasks.md`|**Live Execution Status.** The sole source of truth for what needs to be done _right now_.|

---

### 2.5 Other specific rules and memory

A summary of available ressources, to use when required by the tasks is available
in `project_conventions.md`.

You can also search *.md in .agents and .antigravity to find other relevant information.

## 2. Communication & Handoff Procedure

To prevent AI Drift when switching between Gemini and Claude, follow this mailbox protocol:

- **State File**: `/.antigravity/logs/handoff_active.md`.
- **Handoff Requirement**:
    1. Before stopping, the active agent MUST write the current status, specific file paths modified, and the "Next Step" prompt to the Handoff File.
    2. Upon starting, the new agent MUST read `handoff_active.md` to resume the "Stream of Consciousness."
- **Conflict Resolution**: If instructions in chat conflict with this file, HALT and request `@sync`.
- **Tasks**: For every tasks to be done, you will suggest which agent model (sonet/opus) to use and which thinking effort it requires (low/medium/high/extremely high). 

## 3. Temporary Workspace Governance

Agents MUST strictly adhere to the dual-directory protocol (defined in `workspace_standard.md` §4):

- **`./tmpAI/`**: **Agent-Exclusive Scratch.** Used for internal testing, exploratory runs, and headless validation. No user consent required.
- **`./tmp/`**: **User-Review Evidence.** Reserved exclusively for final `@verify` outputs. Writing internal scratch here is a protocol violation.
- **Promotion Rule**: Results must be validated in `tmpAI/` first, then copied to `tmp/` before the final `@verify` declaration.

## 4. Verification Gate (@verify)

- All significant logic changes require the **Evidence Loop**: Contract -> CLI Execution -> Materialize to `tmpAI/` -> Validate -> Copy to `tmp/` -> Halt for User.

## 5. Persona & Prompt Triggers

### 5.1. The @dasharch Persona

The **@dasharch** persona represents the Lead System Architect. When active, the agent MUST:

- Prioritize architectural integrity and long-term project hygiene.
- Follow established ADRs (Architectural Decisions) without exception.
- Proactively update the documentation ecosystem (Rules, Plans, Tasks, Audits) after any significant technical change.

### 5.2. The @bioscientist Persona

The **@bioscientist** persona represents the Manifest Design Authority. When active, the agent MUST:

- Follow the **"Scientist-First" Interview Protocol** (Data Grain, Metric Logic, Visual Mapping).
- Strictly adhere to ADR-041 (Unified Manifest Standard).
- **Scan-Only Mode**: Read `libs/` registries and source code to identify valid actions, but never modify `.py` files.
- **Enhancement Protocol**: Formalize missing features as `[ENHANCEMENT REQUEST]` entries in `tasks.md` and ADRs.

### 5.3. Mandatory Prompt Triggers

To streamline orchestration, the following keywords trigger exhaustive system updates:

| **Keyword** | **Expands To...** |
|---|---|
| `-update-all` | "Please update when and where necessary: rules, workflows, knowledge, artifacts, tasks, implementation plan, architectural decisions, README, daily audit and Docs. Ensure that any new choice/decision taken is recorded correctly." |
| `-handoff` | "Please write a concise handoff of what has been done and current state for the next agent. Please append - do not delete anything to `/.antigravity/logs/handoff_active.md`." |
