# Project Architecture & Rulebook Homogenization (Phase 11)

This plan details the restructuring of the rulebooks, workflows, and test naming conventions, aligning with the 3-Tier Tree Data Lifecycle and Homogeneous CLI Standards.

## Proposed Changes

### 1. Rulebook Restructuring
The following files in `.claude/rules/` will be consolidated. **Deletion will strictly happen only at the very end**, after global integrity is checked and verified:
- `rules_aesthetic.md`
- `rules_behavior.md`
- `rules_documentation_standards.md`
- `rules_runtime.md`
- `rules_tiered_data.md`
- `rules_wrangling.md`

We will draft the following 5 authoritative rulebooks (each strictly `<12,000` characters; if exceeded, they will be logically chunked):
#### [NEW] rules_documentation_aesthetics.md
- Merge aesthetics and documentation standards.
- Enforce "Violet Law" exclusively for HUMAN-FACING docs. Prohibit Violet Law in functional code.
- Define Quarto/Mermaid zoomability and CSS themes.
- **Added Mandate**: Code and Documentation must be kept in sync. All refactoring/naming/function changes must actively reflect in `docs/*.qmd` and `README.md`.

#### [NEW] rules_data_engine.md
- Merge wrangling and tiered data logic.
- Implement 3-Tier Tree Lifecycle (Trunk: Relational Anchor, Branch: Plot-Specific Anchor, Leaf: Interactive UI View).
- Define the Bifurcation Point.

#### [NEW] rules_verification_testing.md
- Standardize Naming: `libs/{lib}/tests/{lib}_integrity_suite.py` and `libs/{lib}/tests/debug_{component_name}.py`.
- CLI Mandate: `argparse` with `--help` for all scripts.
- Enforce @verify protocol.
- **Added Mandate**: Clarify that global library wrapper test scripts are required and must be run to ensure complete automation testing works.

#### [NEW] rules_runtime_environment.md
- Enforce Modular Monorepo (ADR-011) and Editable Mode (ADR-016).
- Strict VENV lock and DNF pinning for Antigravity v1.19.6.

#### [NEW] rules_asset_scripts.md
- Governance for `./assets/scripts/`.
- Data Priority Hierarchy (Override -> Manifest -> Default).
- Differentiate Suggestive Tools from Functional Assistants.

---

### 2. Core Configuration and Workflows

#### [MODIFY] .claude/rules/workspace_standard.md
- Retain this file; update the Master Index to point to the new rulebooks.

#### [MODIFY] .claude/rules/dasharch.md
- Retain this file; add "Integrity Guardian" instructions.

#### [MODIFY] .claude/workflows/implementation_workflow_transformer.md and viz_factory_implementation.md
- Update to use the 3-Tier Tree logic and standardized test naming.

---

### 3. Tests Renaming & Doc Sync 
- Rename all existing integrity suites in `libs/transformer/tests/` and `libs/viz_factory/tests/` to follow the `{lib}_integrity_suite.py` pattern.
- Ensure component debug scripts follow the `debug_{component_name}.py` pattern.
- **Documentation Sync**: Traverse `docs/*.qmd` and `libs/*/README.md` to ensure any renamed scripts or new logic are mirrored appropriately.

## Verification Plan

### Automated Tests
- Run library test wrapper scripts to prove that automated testing functionality remains intact and respects `--help`.
- Script programmatic checks on the character length of the 5 new rulebooks (must be <12,000 characters).

### Manual Verification
- Review deletion of legacy files only after confirming full functionality and correct doc syncing.
