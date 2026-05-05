
# Work restarting

- [ ] strategy for ui implementation testing

---

- [ ] Create complete test manifest - functional
- [ ] one at the time - meaningfull test manifest

---

- [ ] Moving test manifest to config/manifests/pipelines, adapting paths for include and data reading / testing
- updating the protocol for testing that this path/manifest will be used instead of| the old one in assets

@Agent: @dasharch - FILESYSTEM ALIGNMENT & 3-LAYER VALIDATION.

Context: We are moving the authoritative 'ST22_dummy' manifest from assets/ to config/ and performing a full validation.

Tasks:

1. Move the manifest 'assets/template_manifests/1_test_data_ST22_dummy.yaml' and its associated directory 'assets/template_manifests/1_test_data_ST22_dummy/' to 'config/manifests/pipelines/'.
2. Path Correction: Update all '!include' paths within the YAML files to ensure they are relative and valid within the new /config/ structure.
3. Path Authority Check: Ensure all 'data_path' or 'source' keys in the manifest still point correctly to 'assets/test_data/1_test_data_ST22_dummy/' from the new manifest root.

Execution (Universal Evidence Loop):
Execute the 3-Layer test suite for this manifest.

- Target: config/manifests/pipelines/1_test_data_ST22_dummy.yaml
- Global Root: tmp/TEST_MANIFEST/1_test_data_ST22_dummy/

Layered Materialization:

- Layer 1 (Ingestion/Wrangling): Execute via debug_wrangler.py. Output to: tmp/TEST_MANIFEST/1_test_data_ST22_dummy/layer1/
- Layer 2 (Assembly/Persistence): Execute via debug_assembler.py. Output to: tmp/TEST_MANIFEST/1_test_data_ST22_dummy/layer2/
- Layer 3 (Viz Factory): Execute via debug_runner.py. Output to: tmp/TEST_MANIFEST/1_test_data_ST22_dummy/layer3/

Requirement:

- Use ./.venv/bin/python for all commands.
- Print df.glimpse() for each layer.
- HALT for @verify after Layer 3 is materialized.

---

- [x] Update persona for testing

@Agent: @dasharch - ARCHITECTURAL ALIGNMENT (PHASE 12-A).

Context: We are standardizing the UI Persona templates to match the Persona Traceability Matrix in .claude/knowledge/persona_traceability_matrix.md and ADR-029a.

Task:

1. Read .claude/knowledge/persona_traceability_matrix.md and .claude/rules/rules_ui_dashboard.md.
2. Review the files in config/ui/templates/.
3. Delete any legacy templates that do not map to the 5 authorized personas.
4. Rename or Create the following 5 files to ensure 1:1 parity with the Matrix:
   - pipeline-static_template.yaml
   - pipeline-exploration-simple_template.yaml
   - pipeline-exploration-advanced_template.yaml
   - project-independent_template.yaml
   - developer_template.yaml
5. Inside each file, ensure the 'persona_name' key matches the filename prefix and 'logic_access' levels (None, Basic, Advanced, Full) reflect the matrix requirements.

Follow:

- Workspace Standard: .claude/rules/workspace_standard.md
- Verification Protocol: Do not implement Python logic. This is a YAML-only configuration task.

HALT for @verify after updating the directory structure and file contents.

----

- [x] revision context script - new context for browser chat.

# Review  - UI definition - components

Please review, and modify your plan. We are not yet ready. Do not exectute any code, I want to review the adjusted plan first.

---

ok, this is a good start, but I want you to review my comment and really try to understand the intend of the project, including the bifurcating point of the blueprint.

For this you need to review in detail and very thoroughly the following files:

- .claude/rules/ui_implementation_contract.md (new : PRIMARY AUTHORITY - v1.9)
- tmp/extra/ui_reactivity_persona.md
I add an additional file to the review (which might clarify the intend of the project, this was an early attempt to define the ui implementation plan)  I grant you access to the file (without request) in: `./EVE_WORK/daily/2026-04-09/
Comparison_SideDataPolts_Tiers_Claude_implementation_plan.md`

Please review, and modify your plan. Do not exectute any code, I want to review the adjusted plan first.

---

"@Agent: @dasharch - ARCHITECTURAL AUDIT & PLANNING MODE.

IDENTITY: You are the Lead Architect for SPARMVET_VIZ. Your priority is to reconcile the new UI Implementation Contract with existing project standards to prevent AI drift and ensure technical coherence.

1. MANDATORY SYNC:

- Read files in .claude/rules/, .claude/workflows/, .claude/knowledge/, .claude/tasks and .claude/plans

1. index the following files to establish the current 'Source of Truth':

- .agent/workspace_standard.md (outdated - defines the initial state of the workspace - important to update with the necessary information from the following files)
- .claude/rules/ui_implementation_contract.md (new : PRIMARY AUTHORITY - v1.9)
- .claude/rules/rules_ui_dashboard.md (updated : Behavioral Standards)
- tmp/extra/ui_reactivity_persona.md (new : additional file provided by the user tried to specify and associate persona with ui implementation - vision of how it should behave)
- .claude/knowledge/protocol_tier_data.md (requires review and consistency check with ui_implementation_contract.md)
- .claude/workflows/ui_manifest_integration_testing.md (outdated)
- .claude/knowledge/ui_traceability_matrix (outdated)
- .claude/knowledge/project_tasks/ui_manifest_integration_testing.md (outdated)
- .claude/knowledge/project_conventions.md (outdated - must be adjusted and completed last, when everything is understandable and decided)

1. CORE MISSION:
Perform a 'Consistency & Hygiene Check' (#hygiene) across all UI and data-wrestling files.

- Identify inconsistencies between the 'Violet Node' branching logic (Tier 3) and the older 'ui_traceability_matrix'.
- Update 'workspace_standard.md' to reflect (ENTRY POINT for agent rules)
- Resolve the 'Outdated' status of the workflows and test manifests listed in the documentation.

1. DELIVERABLES:
A. REORGANIZATION PLAN: Propose a move/merge strategy for outdated files to prevent duplication.
B. UPDATED IMPLEMENTATION PLAN: A step-by-step roadmap for Phase 12 (Theater implementation).
C. REFINED RULES: A consolidated 'rules_ui_dashboard.md' that includes the new Persona-Based Activation matrix.
D. Ask relevant question to the user to review, clarify inconsistency.

DO NOT START CODING.
Perform the Audit, list inconsistencies, and HALT for @verify before proposing the final plan."

---

We need to review the rules, knowlege and files that are necessary for development of the project: rules, workflow, knowledge base, taks and development plan
in .claude/rules/, .claude/workflows/, .claude/knowledge/, .claude/tasks,
.claude/plans

This will require particular focus on UI implementation contract and rules_ui_dashboard.md design and behavior. It is possible to reorganize those files if the content would best fit in a different file. NO DETAIL SHOULD BE REMOVED. Clarifications, in case of inconsistencies or ambiguities, should be resolved by dialog with the user (me).

- .agent/workspace_standard.md (outdated - defines the initial state of the workspace - important to update with the necessary information from the following files)
- .claude/rules/ui_implementation_contract.md (new : PRIMARY AUTHORITY - v1.9)
- .claude/rules/rules_ui_dashboard.md (updated : Behavioral Standards)
- tmp/extra/ui_reactivity_persona.md (new : additional file provided by the user tried to specify and associate persona with ui implementation - vision of how it should behave)
- .claude/knowledge/protocol_tier_data.md (requires review and consistency check with ui_implementation_contract.md)
- .claude/workflows/ui_manifest_integration_testing.md (outdated)
- .claude/knowledge/ui_traceability_matrix (outdated)
- .claude/knowledge/project_tasks/ui_manifest_integration_testing.md (outdated)
- .claude/knowledge/project_conventions.md (outdated - must be adjusted and completed last, when everything is understandable and decided)
