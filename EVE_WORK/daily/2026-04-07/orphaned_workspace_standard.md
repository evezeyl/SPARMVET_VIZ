wwwwwwwwwwwwwwwwwwwwwwww---
trigger: always_on
---

# Antigravity Workspace Standard (v1.19.6)
**Authority:** All Active Agents (Universal Ownership)
**Workspace ID:** SPARMVET_VIZ
**Persistence Level:** Mandatory 

## 1. Directory Authority (The Recovery Toolkit)
The following paths in the project root are the **ONLY Authorized** source of truth for workspace state and versioning. The creation of new top-level folders within `./.claude/` is strictly FORBIDDEN without architectural review.

- **`./.claude/plans/`**: `implementation_plan_master.md` (**SOLE AUTHORITATIVE ROADMAP**).
- **`./.claude/tasks/`**: `tasks.md` (**SOLE SOURCE OF TRUTH FOR EXECUTION**).
- **`./.claude/conversations/`**: Archived chat exports and session summaries.
- **`./.claude/logs/`**: Daily audit logs and change records.
- **`./.claude/knowledge/`**: Persistent codebase knowledge items (KIs).
- **`./.claude/embeddings/`**: Local vector storage for tool-layer retrieval.

## 2. Logic Source of Truth (Technical Authority)
The following files are the **Command Rules of Engagement**. Failure to consult these before implementation is a violation of the `@dasharch` authority.

| Path | Role | Rule of Usage |
| :--- | :--- | :--- |
| `./.claude/rules/workspace_standard.md` | **Agentic Rules in Workspace** | Code of conduct |
| `./.claude/plans/implementation_plan_master.md` | **Sole Roadmap** | Check this to determine the current Phase and Task ID. |
| `./.claude/knowledge/architecture_decisions.md` | **Technical Bible** | Consult before writing NEW logic to ensure ADR compliance. |
| `./.claude/knowledge/blockers.md` | **Hurdle Tracker** | Review when entering a new Phase to check for unresolved logic blockers. |
| `./.claude/knowledge/milestones.md` | **Project Memory** | Refines the historical context of what has been verified. |
| `./.claude/tasks/tasks.md` | **Execution Tracker** | MUST be updated after every `@verify` gate. |
| `./.claude/knowledge/project_conventions.md` | **Essential files Tree - component | MUST be read and be updated when necessary | 

## 3. Operational Directives: The Mirror Protocol
- **State Mirroring:** Every time a task is updated or a plan is modified, the Agent MUST write a copy to the respective `./.claude/` folder.
- **Chat Archiving:** Before ending a session, the Agent MUST export a summary or full log of the current conversation to `./.claude/conversations/`.
- **Conflict Resolution:** If the global IDE state differs from the local workspace files, the **local workspace files** are the authoritative source.
- **No Ghost State:** Technical decisions made in chat are not "real" until they are mirrored into `architecture_decisions.md` or `tasks.md`.

## 3. Environment Authority (VENV)
- **Single VENV:** All execution MUST occur within a `.venv/` directory located at the project root.
- **Agent Restriction:** Agents are FORBIDDEN from creating sub-environments or local `__pypackages__`.
- **Dependency Sync:** Any new library (e.g., `polars`, `plotnine`, `ruamel.yaml`) must be added to `pyproject.toml` before implementation. This for Each library (subdirectory in libs) AND for the general App in app/pyproject.toml.  
- **Package-First Authority:** All core libraries (`ingestion`, `transformer`, `utils`, `viz_factory`) MUST be installed in 'Editable Mode' (`pip install -e`). 
- **No Path Hacking:** Future scripts and tests are FORBIDDEN from using `sys.path.append` or `sys.path.insert` to locate internal modules. All internal communication must occur via standard Python package imports (e.g., `import ingestion`).
- **Cleanup:** All `__pycache__` and `.ipynb_checkpoints` must be ignored by Git and the Agent's scan.

## 4. Commit Readiness
- All mirrored artifacts must use clean Markdown formatting for Git diffing.
- Priority is placed on **First-Time Accuracy** to ensure the mirrored history is a reliable technical record.

## 5. Persistent Access & Permissions
- **Root .venv Access:** The Agent is granted permanent, non-expiring access to `./.venv/` for the duration of the project.
- **No-Prompt Execution:** All calls to `python`, `pytest`, or `pip` within the root `.venv` are pre-authorized to avoid workflow interruptions.
- **Scope:** This access is limited to reading metadata and executing binaries; manual modification of `.venv` internals is reserved for environment-sync tasks only.

## 6. The Logic Conflict Guardrail
- **Rule of Precedence**: Project Rules (workspace_standard.md) and ADRs (architecture_decisions.md) always take precedence over chat prompts.
- **Mandatory Halt (Rule Violation)**: If a user prompt asks for an implementation that contradicts a Project Rule (e.g., asking for CSV when the rule is TSV), the Agent MUST NOT execute. It must state: "I have detected a conflict between your request and [Rule Name]. Should I follow the Rule or the Prompt for this specific task?"
- **Sync-or-Stop (Content Discrepancy)**: If the Agent detects a discrepancy between the user's prompt (intent) and the file currently on disk (implementation), the Agent **MUST NOT** execute.
    - It must present the two versions to the user.
    - It must ask: "Should I update the file on disk to match your new instructions @sync, or should I follow the existing file @verify ? 
   - it must wait for one of two specific keywords: 
       - @verify: The Agent accepts the file on disk as the "Source of Truth" and executes the test immediately. 
       - @sync: The Agent first updates the file on disk to match the latest chat instructions, then executes the test.

## 7. Documentation Integrity
- Never repeat source code or data content within documentation files. Instead, provide a relative link to the file (e.g., [wrangler_debug.py](../../../../tests/wrangler_debug.py)). This prevents documentation drift and keeps files lightweight.

## 8. Decorator Standards (The Law of Decorators)
- **Homogeneity:** All wrangling actions MUST follow the exact same architectural pattern. Adding a new action (e.g., `split_column`) should never require changes to the internal `DataWrangler` dispatcher or the Registry logic.
- **Registration Pattern:** Actions are registered using the `@register_action("name")` decorator. This decorator is a "Basic Dictionary-Mapping Standard" (O(1) lookup).
- **Function Signature:** Every action MUST accept exactly two arguments: `(lf: pl.LazyFrame, spec: Dict[str, Any])`.
- **Parameter Extraction:** All parameters (columns, delimiters, flags) MUST be extracted from the `spec` dictionary.
- **Independence:** Actions MUST be atomic and independent. They receive a `LazyFrame` and return a modified `LazyFrame` without side effects outside the Polars execution plan.
- **Mandatory Testing:** Every new registered action MUST include a dedicated test manifest and dataset in `./libs/transformer/tests/data/` and MUST pass the automated `./libs/transformer/tests/test_decorator_suite.py` before integration.
- **Naming Convention for Atomic Testing:** Every registered action MUST have a corresponding test pair using the exact action name:
    - Logic: `@register_action("my_action")`
    - Manifest: `./libs/transformer/tests/data/my_action_manifest.yaml`
    - Data: `./libs/transformer/tests/data/my_action_test.tsv`
- **Verification Tool Naming:** All interactive CLI scripts for logic verification must use the prefix 'debug_' (e.g., `debug_reconciler.py`) to distinguish them from automated pytest suites.
- **Evidence Materialization**: Debug tools MUST materialize their findings as TSVs into a `tmp/` subdirectory (e.g., `tmp/reconciler/`) for manual audit before any manifest is committed as [DONE].

## 9. Wrangling & Transformation Standard
- **Universal Format:** All wrangling configurations in YAML manifests (`data_schemas`, `metadata_schema`, etc.) MUST use a **Sequential List of Dictionaries**.
- **Staging Order:** Wrangling steps are **staged (appended to the query plan)** exactly in the order they appear in the list.
- **Logic vs. Physical:** The iteration order in the manifest defines the **Logical Plan**, but Polars handles the **Physical Execution** optimization.
- **Atomicity:** Every decorator implementation MUST accept exactly two arguments: `(lf: pl.LazyFrame, spec: Dict[str, Any])`. Parameters must be extracted from the `spec` dictionary.
- **Registry:** The internal Registry (`registry.py`) is a dictionary for O(1) lookup, but it is populated dynamically from modular action files using the `@register_action` decorator.

## 10. Pattern Crystallization.
- **Threshold**: When a new component type (e.g., a decorator) reaches a count of 3, the established pattern must be codified as a "Standard" in this document.
- **Evidence-Based Writing**: The Agent must use the first 2 implementations as the "source of truth" to write the rule for the 3rd.
- **Maintenance**: Once a rule is written, the Agent no longer needs to read multiple files for that type—it simply follows the Rule or Halts on divergence.

## 11. Rule Modification & Double Confirmation (The "Halt & Verify" Protocol)
- To ensure project-wide stability and prevent accidental "architectural drift," any change to a codified rule (e.g., Section 8: Decorator Standards) must follow this strict safety protocol:
- Double Confirmation Required: If a user request contradicts an established rule in workspace_standard.md, the Agent must HALT and explicitly state: "This request modifies Rule [X]. Is this really your intent?" The Agent cannot proceed until the user provides a second, explicit confirmation.
- Mandatory Refactoring: Upon double confirmation, the Agent is responsible for identifying all existing functions, classes, or files that follow the old pattern. These must be refactored to the new standard immediately.
- Forced Re-testing: Every refactored component must be re-tested in the same session to ensure that the rule change has not introduced regressions and that project-wide homogeneity is maintained.

## 12. ADR-013: The Manifest Data Contract
- **Universal Structure:** All yaml manifests (pipeline or dataset) MUST follow the mandatory block structure: Header (ID/Description) -> `input_fields` -> `wrangling` -> `output_fields`.
- **The Contract Guard:** The `output_fields` block is a strict Polars `.select()` contract. Any column not explicitly defined in the output contract MUST be dropped by the pipeline before data is exposed to the orchestration layer. This is the primary defense against "Column Drift."
- **Categorical Enforcement:** All discrete metadata defined in `output_fields` MUST use `type: categorical` to ensure **Plotnine** discrete scale compatibility and relational join integrity.
- **Ambiguity Check**: Any fuzzy join or regex-based key extraction MUST be audited for **AMBIGUOUS** matches where a single reference ID maps to multiple target records. High-priority warnings generated by `debug_reconciler.py` or `debug_ambiguity.py` MUST be addressed by refining the wrangling regex or filters.
- **Order of Operations:** String-based cleaning (wrangling) MUST precede Categorical casting (output_fields contract). The pipeline executes wrangling on raw strings and performs the Categorical cast as the final, terminal contract enforcement step [Section 9, 12].
- **ADR-014 (Identity Mode):** If no wrangling is required, `wrangling: []` and `output_fields: []` are used to indicate an Identity Transformation (Select All).

## 13. Modular Library Autonomy (The Clear Lines Policy)
- **Independent Modules:** Libraries located in `./libs/` (e.g., `ingestion`, `transformer`, `utils`) are standalone, reusable tools. They must be developed and tested as if they could exist in separate repositories.
- **Data-Agnostic Logic:** Internal lib logic must be **data-agnostic**. Libraries MUST NOT contain code that fetches or locates raw data files (e.g., `transformer` must not call `DataIngestor`). They receive data (LazyFrames) from the caller and return processed results, ensuring they can be tested in isolation with mock data.
- **Directory Standard:** Each library MUST use the structure `./libs/[lib_name]/src/` for logic and `./libs/[lib_name]/tests/` for verification.
- **NO Cross-Library Imports:** It is strictly FORBIDDEN for one library in `./libs/` to import from another (e.g., `transformer` MUST NOT import `ingestion`). 
- **Orchestration Layer:** Coordination between libraries (joining data, sequential execution) is restricted to the **App Layer** (`app/`) or top-level **Execution Scripts** (`assets/scripts/`).
- **Standard Import Interface:** Libraries must provide a clean package interface via `__init__.py` and a valid `pyproject.toml`.
- **Library Documentation Standard:** Every internal library MUST contain a `README.md` detailing its specific purpose, Key Components (using Violet Standard), I/O summary, and local CLI runners.
- **Generator SDK:** The Generator SDK (`libs/generator_utils`) is the sole authorized engine for scaffolding new projects and generating synthetic test data. It must remain UI-agnostic to support future Shiny/GUI integration.

## 14. Python Execution Authority
- **Single Source of Truth:** All execution MUST occur via the root virtual environment: `./.venv/bin/python`.
- **Editable Mode:** All internal libraries MUST be installed in 'Editable Mode' (`pip install -e ./libs/name`) to ensure standard package imports work without path hacking (ADR-016).
- **No Path Hacking:** Use of `sys.path.append` or `sys.path.insert` for internal modules is prohibited.

## 15. Knowledge Mirroring Protocol
- **Master Source (The "Long Memory"):** All files within `docs/*/*.qmd` are the permanent, detailed public record. They contain full prose, philosophy, and complete contextual documentation.
- **Compressed Summary (The "Combat Log"):** All files within `.claude/knowledge/*.md` serve as ultra-concise cheat sheets.
- **Sync Requirement:** The Combat Log MUST stay 100% technically synced with the Master Source, but aggressively compressed (bullet points, tables) for rapid AI/User parsing. Any new technical discovery must be written formally to `docs/` and briefly to `.claude/`.

## 16. Component Reference Standard (The Violet Law)
- **Violet Component Format:** When referring to architectural components in documentation (Markdown, Quarto, etc.), agents MUST use the explicit 'Violet' standard format: `ClassName (filename.py)`.
- **Examples:** `DataWrangler (data_wrangler.py)`, `DataAssembler (data_assembler.py)`, `ActionRegistry (registry.py)`.
- **Purpose:** This unambiguous naming convention prevents confusion between conceptual layers and the actual Python implementation files.

## 17. Documentation Aesthetics & Naming
1. **Violet Component Standard**: When referring to code modules, always use the format: **Component (file_name.py)** where the component and brackets are colored violet/purple.
2. **Library READMEs**: Each library in `./libs/` must contain a `README.md` that serves as the entry point for developers.
3. **Inline Code Styling**: Use the 'Deep Violet' CSS theme for all inline code blocks (`background: #3a2a4d`, `color: #e0cffc`) to ensure legibility and brand consistency.
4. **Mermaid Zoom**: All large architectural diagrams must be wrapped in a `::: {.lightbox}` div to enable click-to-zoom functionality in the Quarto render.