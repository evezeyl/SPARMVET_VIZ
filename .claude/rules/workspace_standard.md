---
trigger: always_on
---

# Antigravity Workspace Standard (v1.20.0)

**Authority:** All Active Agents (@dasharch)
**Workspace ID:** SPARMVET_VIZ
**Persistence Level:** Mandatory Authority

## 0. Mandatory Dispatch (Read Order)

To prevent AI Drift and Quota Waste, the Agent MUST follow this sequence upon initialization:

1. **./AGENT_GUIDE.md**: Adopt the high-level Persona and Onboarding Context.
2. **./tree.txt**: Locate the physical file map.
3. **./.claude/knowledge/project_conventions.md**: Identify the "Who/Where/How" for every component.
4. **./.claude/rules/rules_runtime_environment.md**: Lock the `./.venv/bin/python` path.

## 1. The Master Index

This file is the **Sole Source of Authority** for agentic behavior in the SPARMVET_VIZ workspace. It is organized into modular rulebooks. Agents MUST read all referenced files before executing logic.

| Rulebook | Scope | File Reference |
| :--- | :--- | :--- |
| **Doc & Aesthetics** | Violet Law, Quarto/Mermaid, CSS Themes, Doc Sync | [rules_documentation_aesthetics.md](./.claude/rules/rules_documentation_aesthetics.md) |
| **Manifest Standards** | Basename Mirroring, YAML Includes | [rules_manifest_structure.md](./.claude/rules/rules_manifest_structure.md) |
| **Data Engine** | 3-Tier Tree Lifecycle (ADR-024), Decorators, Manifests | [rules_data_engine.md](./.claude/rules/rules_data_engine.md) |
| **Validation & Test** | @verify Protocol, Global Wrappers, CLI Mandate | [rules_verification_testing.md](./.claude/rules/rules_verification_testing.md) |
| **Runtime & Env** | VENV, No-Discovery, Pinned Versions, Library Autonomy | [rules_runtime_environment.md](./.claude/rules/rules_runtime_environment.md) |
| **Asset Scripts** | Bootstrappers, Synthetic Data, Governance | [rules_asset_scripts.md](./.claude/rules/rules_asset_scripts.md) |
| **UI Rules** | UI Orchestration & Aesthetics | [rules_ui_dashboard.md](./.claude/rules/rules_ui_dashboard.md) |
| **Viz Factory** | Artist Pillar, Plotnine Parity, Core Geoms | [rules_viz_factory.md](./.claude/rules/rules_viz_factory.md) |
| **UI Contract** | Theater Layout, Tier Toggle, Persona Masking, Audit Stack | [ui_implementation_contract.md](./.claude/rules/ui_implementation_contract.md) |
| **App Structure** | Server decomposition, Handler/Module boundary law | [rules_app_structure.md](./.claude/rules/rules_app_structure.md) |

## 2. Primary Technical Bible

- **Roadmap:** `implementation_plan_master.md (./.claude/plans/)`
- **Execution:** `tasks.md (./.claude/tasks/)`
- **Architecture:** `architecture_decisions.md (./.claude/knowledge/)`
- **Dependency Map:** `.claude/knowledge/dependency_index.md` — **Read before modifying any engine/library/rule file.** Lists which files consume each component (forward links) and which components each file depends on (backward links). Includes a Sync Risk Register for historically-diverging pairs.

## 3. Operational Mandate

- **@deps Session Law:** At session end, verify/add/update `@deps` blocks for every file touched, then run `build_dep_graph.py`. See §5-E for the full protocol. This is non-negotiable.
- **Mandatory Halt:** Every significant transformation or rule change requires an explicit `@verify` from the user.
- **Violet Law:** All component references in documentation must follow `ClassName (filename.py)` standard.
- **Single Source of Truth:** Local workspace files (`./.claude/`) are the authoritative source over global IDE state.
- **Relative Path Authority:** ALL file paths provided in manifests, rulebooks, and technical documentation MUST be relative to the project root. The use of absolute paths or symbolic links within the project structure is strictly FORBIDDEN.
- Background Mandate: for any script execution (unless specified otherwise) you MUST use background execution flags to ensure the UI remains responsive.
- **@sync Guardrail:** If the agent detects a discrepancy between what was discussed in chat and the actual state of files on disk (e.g., a rule says X but the code does Y, or a file referenced in chat no longer exists), the agent MUST stop and surface the discrepancy explicitly before continuing. Do not silently resolve ambiguity by choosing one side. The correct response is: "HALT: @sync required — [description of discrepancy]. Please confirm which is authoritative: the chat intent or the disk state."

## 5. Dependency Tracking System (`@deps`)

Every significant file in the project carries a `@deps` annotation block. This is the **primary tool for impact analysis** — before modifying any file, read its `@deps` block to know what else must change and why.

### 5-A. How agents use `@deps`

**Before modifying a file:**
```bash
# 1. Read the file's own @deps block — see what it provides and what mirrors it
grep -A 10 "@deps" path/to/file.py

# 2. Find everything that consumes what this file provides
grep -r "consumes:.*action:cast" . --include="*.py" --include="*.yaml" --include="*.md"

# 3. Find everything that mirrors this file (must stay behaviourally in sync)
grep -r "mirrors:.*orchestrator.py" . --include="*.py" --include="*.yaml" --include="*.md"
```

**To regenerate the full dependency graph:**
```bash
.venv/bin/python assets/scripts/build_dep_graph.py
# Outputs: tmp/dep_graph.json  (machine-readable Cytoscape elements)
# Opens:   assets/dep_graph.html in browser for interactive exploration
```

**`dependency_index.md` is auto-generated** from `@deps` blocks by `build_dep_graph.py`. Do not edit it by hand.

### 5-B. Annotation format by file type

**Python files** — block at module top, after imports:
```
# @deps
# provides: action:cast, action:coalesce        ← registration names others consume by string
# mirrors: app/modules/orchestrator.py           ← must stay behaviourally in sync
# documents: —
# consumes: libs/transformer/src/transformer/actions/base.py
# consumed_by: app/modules/orchestrator.py, libs/transformer/tests/debug_assembler.py
# doc: .claude/rules/rules_persona_bioscientist.md#8
# @end_deps
```

**YAML files** — block at file top:
```
# @deps
# provides: assembly:AMR_Profile_Joint
# consumes: action:mutate, action:join, action:cast, dataset:metadata_schema
# include_parent: config/manifests/pipelines/2_test_data_ST22_dummy.yaml
# consumed_by: config/manifests/pipelines/2_test_data_ST22_dummy.yaml
# @end_deps
```

**Markdown rule/knowledge files** — in YAML frontmatter:
```yaml
---
trigger: always_on
deps:
  provides: [rule:canonical_recipe_syntax, rule:analysis_groups_structure]
  documents: [libs/transformer/src/transformer/data_assembler.py]
  consumed_by: [.claude/rules/rules_persona_bioscientist.md, docs/appendix/manifest_structure.yaml]
---
```

### 5-C. Coupling-type keywords (what action is required)

| Keyword | Meaning | Required co-update action |
|---|---|---|
| `provides:` | Names/contracts exported by this file | Update all `consumes:` references if renamed |
| `consumes:` | Names/contracts this file depends on | Must be updated if the provider renames/removes |
| `mirrors:` | Must stay behaviourally in sync with this file | Read both files together; any logic change in one must be reflected in the other |
| `documents:` | This file is the human description of that file's contract | Update when the documented file's interface changes |
| `doc:` | The rule/doc file that governs this file's interface | Read before changing; update after if the interface changed |
| `include_parent:` | This file is `!include`-d by that manifest | Moving/renaming this file breaks that manifest |
| `consumed_by:` | Files that depend on this one (the backlink) | Grep these files when changing this one's interface |

### 5-E. Mandatory Maintenance Protocol (SESSION LAW)

**This is a hard session-end obligation, not optional housekeeping.**

At the end of every session in which code, rule files, or manifests were modified:

1. **Verify** — for every file you touched, check that its `@deps` block is present and accurate.
2. **Add** — if a qualifying file has no `@deps` block, add one before closing.
3. **Update** — if you changed a file's interface (renamed a method, added an action, changed a key), update its `@deps` block and the `consumed_by:` entries in its dependencies.
4. **Regenerate** — run `build_dep_graph.py` as the final step of any session that touched annotated files:
   ```bash
   .venv/bin/python assets/scripts/build_dep_graph.py
   ```
5. **Log** — note in the session audit log (`audit_YYYY-MM-DD.md`) that deps were verified/updated.

**Trigger conditions** (either is sufficient to require the full protocol):
- Any `.py` file in `libs/` or `app/` was modified
- Any `.yaml` file in `config/manifests/` was modified
- Any `.md` file in `.claude/rules/` or `.claude/knowledge/` was modified

**An agent that ends a session without completing this protocol is in violation of workspace standards.**

### 5-D. Scope — what gets annotated

Annotate files where a change has non-obvious ripple effects:
- All Python modules that register actions or components (`@register_action`, `@register_plot_component`)
- All core library modules (`data_assembler.py`, `data_wrangler.py`, `ingestor.py`, `orchestrator.py`, `metadata_validator.py`)
- All debug scripts that mirror production logic
- All rule files (`.claude/rules/*.md`)
- All assembly recipe files (`assembly/*.yaml`)
- Plot spec files only if they have special structural dependencies

Do NOT annotate: test data files, simple TSV/CSV data, one-off utility scripts, generated files.

## 4. Temporary Workspace Execution

Two segregated temporary directories exist at the project root. Their use is **strictly non-interchangeable** (see `rules_verification_testing.md` §6 for full protocol):

- **`./tmpAI/`** — Agent-exclusive scratch space. Agents read and write here freely, without halting for user consent. Used for exploratory runs, import checks, intermediate debug artifacts, and headless CI-style validation not yet ready for user review.
- **`./tmp/`** — User-review outputs only. Reserved exclusively for `@verify` evidence that the agent declares to the user as ready for inspection. Writing agent-internal scratch here is a protocol violation.

Both directories are persistent and ignored by the embedding engine. When an agent-internal result is promoted to `@verify` status, the artifact is copied from `./tmpAI/` to `./tmp/` before the halt declaration.

---
