---
trigger: always_on
deps:
  provides: [rule:venv_path_mandate, rule:no_discovery, rule:pinned_versions, rule:library_autonomy]
  documents: [.venv/]
  consumed_by: [.claude/knowledge/dependency_index.md]
---

# Runtime & Environment Authority (rules_runtime_environment.md)

**Authority:** Defines constraints on python environments, dependency locators, and module isolation.

## 1. System & IDE Truths (Pinned Lifecycle)

- **IDE Version:** Antigravity v1.19.6 (STABLE/PINNED).
- **OS:** Fedora 43 KDE X1 (Velocifero Compute).
- **Update Policy:** `update.mode: none` (DNF pinned). Do not attempt to upgrade generic apt/dnf OS layers outside of explicit commands.
- **VENV Enforcement:** All execution MUST occur exclusively within the `./.venv/bin/python` environment at the project root.
- **Verification Rule:** Do NOT repeatedly re-run virtual environment checks if the status is already known to be successfully locked.
- **Execution Authority**: ALL commands must prefix with `./.venv/bin/python`. Using the system `python3` is strictly PROHIBITED.
- **Path Map**: Use `tree.txt` in the root as the primary filesystem reference. Do not run `ls -R` or `find` commands to discover the project structure.

## 2. Directory Governance (The Master Root)

The following paths in the project root are the **ONLY Authorized** core operational centers. The creation of arbitrary top-level folders within `./.claude/` without explicit authorization is strictly FORBIDDEN.

**Boundary Lock (`.aiignore`):** The agent MUST strictly respect the `.aiignore` file located at the project root. Do not scan directories like `EVE_WORK`, `archives`, or `.claude/embeddings/` unless the user explicitly grants a "Border-Crossing Permit" for a specific file.

- **`./.claude/plans/`**: `implementation_plan_master.md` (Sole authoritative roadmap).
- **`./.claude/tasks/`**: `tasks.md` (Sole execution status authority).
- **`./.claude/knowledge/`**: Persistent codebase intelligence logs and KIs.
- **`./.claude/logs/`**: **Log Authority**. ALL session audits and daily logs MUST be stored in `./.claude/logs/audit_{YYYY-MM-DD}.md`. Content in these logs is **APPEND-ONLY**; deleting or replacing previous session entries is strictly FORBIDDEN. The creation of log files in the project root or `EVE_WORK/` is strictly FORBIDDEN.
- **`./docs/`**: The absolute single source of truth for all human-facing project knowledge, diagrams, and API boundaries.
- **Zero-Discovery Rule**: The agent must NOT perform "exploratory" reads. If a file is not in `tree.txt` or the `Master Index`, halt and ask the user.
- **Context Loading**: Upon initialization, the agent MUST read the `Master Index` (workspace_standard.md) before any other action.

## 3. Modular Monorepo & Editable Packages (ADR-011 / ADR-016)

The `/libs/` directory contains highly autonomous logic modules. Each directory within must be treated as a wholly independent python package.

- **Editable Mode Mandate**: All core libraries (`ingestion`, `transformer`, `utils`, `viz_factory`) MUST be installed in 'Editable Mode' (`pip install -e`).
- **Dependencies (`pyproject.toml`)**: Libraries must declare their dependencies strictly inside their respective `pyproject.toml` files, bypassing archaic `requirements.txt`.
- **No Path Hacking (Testing Violation Ban)**: The use of `sys.path.append` or `sys.path.insert` is completely PROHIBITED across the entire project structure. This explicit ban **EXTENDS STRICTLY** to all testing scripts (`tests/` directories). All components, including test suites, MUST rely on standard cross-references and standard module resolution after `pip install -e`. If a test suite imports fail, fix the environment hook; do NOT hack the path.

## 4. The "Clear Lines" Library Policy — Two-Tier Dependency Model

Each library in `./libs/` is designed to be **independently installable and reusable without the UI layer**. If you want to build a different frontend (CLI tool, FastAPI service, Galaxy wrapper, Jupyter workflow), you import only the layer(s) you need. `app/` is the ONLY place that wires multiple libraries together.

### Tier 1 — Base layer: `libs/utils/`

- Zero cross-lib imports of its own — only stdlib and polars allowed.
- May be imported by any domain library.
- **Explicit dependency rule:** Any domain library that imports from `libs/utils/` MUST declare it in its own `pyproject.toml` `[project.dependencies]`. Silent/implicit use is forbidden.

### Tier 2 — Domain layers: all other `libs/`

- **No peer-to-peer cross-lib imports.** A domain library MUST NEVER import from another domain library. `transformer` importing from `ingestion` is the canonical FORBIDDEN example.
- May import from `libs/utils/` (Tier 1) only, with explicit `pyproject.toml` declaration.
- Each library must be independently installable via `pip install -e ./libs/<name>/` with no hidden dependencies.

### Tier 3 — Orchestration layer: `app/` and `assets/scripts/`

- May import from any library in `./libs/`.
- This is the ONLY layer that orchestrates multiple libraries together.

**`pyproject.toml` dependency naming standard (resolved 2026-05-11):** When declaring a local lib as a dependency, use the **package name** (e.g., `"utils"`, `"ingestion"`), NOT the path form `"libs/utils"`. The path form is not a valid PEP 508 specifier — pip cannot resolve it. All four affected `pyproject.toml` files (`blueprint_arch`, `connector`, `transformer`, `viz_factory`) have been corrected. The canonical example is `ingestion/pyproject.toml` which already used `"utils"` correctly.

**`TYPE_CHECKING` guard — cross-lib type annotations:** If a domain lib needs to reference a type from another domain lib **solely for static analysis** (e.g., a function signature annotation), the import MUST be guarded by `if TYPE_CHECKING:` and never used at runtime. The injected object is passed by the caller (Tier 3 orchestration layer). Use `consumes_typeonly:` in the `@deps` block to document this pattern. Example: `libs/transformer/pipeline.py` annotates `DataIngestor` for type-checking only — the actual instance is injected at runtime by the caller (orchestrator or test runner). This is **not** a violation of the Clear Lines policy.

**Existing tech debt (do not expand):** All previously listed violations have been resolved. The `transformer→ingestion` item was a TYPE_CHECKING-only annotation (not a runtime violation). The `"libs/utils"` pyproject entries have been corrected. Track any new violations in `tasks.md`.

`libs/utils/` imports are the only acceptable cross-lib exception going forward, and must always be declared in `pyproject.toml` using the package name `"utils"`.

## 5. Python Interpreter Authority

- The path to the active Python interpreter MUST be defined in config/connectors/ (e.g., python_path: "./.venv/bin/python").
- UI components and scripts MUST fetch this path via the Bootloader rather than hardcoding environment-specific strings.
