# Migration Inventory: Workspace Standard Modularization
**Authority:** @dasharch
**Status:** DRAFT (Awaiting @verify)

This document maps the transition of the monolithic `workspace_standard.md` (v1.19.6) and associated system state into a modular rule system.

## 1. Mapping Overview

| Original Section / Context | Target Modular File | Description of Inclusion |
| :--- | :--- | :--- |
| **System State** (IDE, OS, Policy) | `rules_runtime.md` | Core environment configurations and pinned versions. |
| **Section 1**: Directory Authority | `rules_runtime.md` | Authorized paths and Recovery Toolkit root structure. |
| **Section 2**: Logic Source of Truth | `rules_runtime.md` | Technical authority files and engagement rules. |
| **Section 13**: Modular Library Autonomy | `rules_runtime.md` | Clear Lines Policy and independent module standards. |
| **Section 14**: Python Execution Authority | `rules_runtime.md` | Single VENV enforcement (no path hacking). |
| **Section 3**: Operational Directives | `rules_behavior.md` | Mirror Protocol and Ghost State prevention. |
| **Section 4**: Commit Readiness | `rules_behavior.md` | Formatting standards and technical record accuracy. |
| **Section 5**: Persistent Access | `rules_runtime.md` | VENV permissions and execution scope. |
| **Section 6**: Logic Conflict Guardrail | `rules_behavior.md` | Mandatory Halt and Sync-or-Stop protocols. |
| **Section 11**: Rule Modification | `rules_behavior.md` | Double Confirmation and refactoring requirements. |
| **Verification Protocol** | `rules_behavior.md` | **Evidence Loop**: CLI execution, materialization to `tmp/`, and `.glimpse()`. |
| **Section 8**: Decorator Standards | `rules_wrangling.md` | Registry pattern and atomic action signatures. |
| **Section 9**: Transformation Standard | `rules_wrangling.md` | Sequential YAML staging and logical plan order. |
| **Section 10**: Pattern Crystallization| `rules_wrangling.md` | Codifying standards after 3 implementations. |
| **Section 12**: ADR-013 Manifest | `rules_wrangling.md` | Input/Output contracts and categorical enforcement. |
| **1:1:1 Naming Law** | `rules_wrangling.md` | Action:Manifest:Data alignment standard. |
| **Data Type Selection Guide** | `rules_wrangling.md` | Guidance on string vs categorical vs numeric types. |
| **Section 7**: Dox Integrity | `rules_aesthetic.md` | Relative linking and lightweight documentation. |
| **Section 15**: Knowledge Mirroring | `rules_aesthetic.md` | Quarto Master vs Combat Log synchronization. |
| **Section 16**: Violet Law | `rules_aesthetic.md` | **Component Standard**: `ClassName (filename.py)` naming. |
| **Section 17**: Aesthetics | `rules_aesthetic.md` | CSS themes, Mermaid zoom, and library READMEs. |

## 2. Refactoring Components (Violet Standard)

The following core components will be referenced using the Violet Law throughout the new rules:
- `DataWrangler (data_wrangler.py)`
- `DataAssembler (data_assembler.py)`
- `ActionRegistry (registry.py)`
- `DataIngestor (ingestor.py)`
- `VizFactory (viz_factory.py)`
- `UniversalRunner (wrangler_debug.py)`

## 3. Migration Schedule

1. **Verification**: User reviews this inventory.
2. **Execution**: Upon `@verify`, create the 4 modular files in `./.claude/rules/`.
3. **Master Index**: Update `workspace_standard.md` to point to the new rulebooks.
4. **Cleanup**: Remove legacy sections from the master file.

---
**HALT:** Waiting for @verify to proceed with file creation.
