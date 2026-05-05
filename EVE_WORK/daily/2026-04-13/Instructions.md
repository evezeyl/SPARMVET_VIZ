# Instructions 2026-04-13

# Moderating ui testing and ui testing strategy

# testing ui
>
> tested again libraries and improving some part manifest

@Agent: @dasharch - PHASE B: UI PERSONA INTEGRATION & DEBUGGING.

1. CLEARANCE:
Phase A (Headless Audit) is @verified for the './assets/template_manifests/1_test_data_ST22_dummy.yaml'. You are authorized to launch the Shiny UI.

2. TEST GOAL:
Validate UI stability and Persona masking across different templates in 'config/ui/templates/'.

3. STEP-BY-STEP PERSONA SPRINT:

STEP 1: BASELINE STABILITY (test_full_pipeline_template.yaml)

- Action: Point 'app/src/bootloader.py' to use 'test_full_pipeline_template.yaml'.
- Launch: ./.venv/bin/python app/src/main.py
- Verify: Ensure the ST22 manifest loads, all tabs appear, and the plot area is NOT blank.

STEP 2: INTERACTIVITY (user_template.yaml)

- Action: Update bootloader to 'user_template.yaml'.
- Test: Apply a simple categorical filter (e.g., 'Source').
- Verify: The '▶ Apply' button must be the sole trigger for the plot update.

STEP 3: COMPARISON THEATER (developer_template.yaml)

- Action: Update bootloader to 'developer_template.yaml'.
- Verify: Ensure the dual-column 'Comparison Theater' is visible.
- Audit Stack: Confirm inherited Tier 2 steps are Light Violet (#f3e5f5) and user Tier 3 steps are Light Yellow (#fffde7).

1. FAILURE PROTOCOL:
If a persona fails to render correctly, do NOT modify 'libs/'. Check the persona YAML first to ensure 'comparison_mode_enabled' or 'audit_panel_visible' flags are correctly set.

PRESENT EVIDENCE:
Report the success/failure of each Step. List any UI elements that appeared when they should have been masked.

# Nr 3  flash work

@Agent: @dasharch - CRITICAL TASK: MANIFEST RESTRUCTURE & AUDIT.

1. CONTEXT SYNC (NEW STANDARDS):
Read and strictly enforce:

- ./.claude/rules/rules_manifest_structure.md (Basename Mirroring Mandate)
- ./.claude/rules/rules_verification_testing.md (Phase-Gating Protocol)
- ./.claude/workflows/ui_manifest_integration_testing.md (The Master Gate)

1. GOAL: REWRITE & VERIFY MANIFESTS
The 'STRESS_FINAL.yaml' was unsuccessful. You must refactor it and the primary 'ST22_dummy_manifest' to match the official structural authority (assets/template_manifests/1_test_data_ST22_dummy.yaml).

2. PHASE A: STRUCTURAL REWRITE (Basename Mirroring):

- Refactor 'config/manifests/pipelines/STRESS_FINAL.yaml' and its includes.
- Requirement: All !include files MUST move to 'config/manifests/pipelines/STRESS_FINAL/' (mirrored directory).
- Categorize components into subdirectories: input_fields/, wrangling/, output_fields/, and plots/.

1. PHASE B: HEADLESS AUDIT (MANDATORY EVIDENCE LOOP):
Before ANY UI activity, execute the following for the restructured manifest:

- Step 1 (Ingestion): Run 'libs/ingestion/tests/debug_ingestor.py'.
- Step 2 (Assembly): Run 'libs/transformer/tests/debug_assembler.py'.
- Step 3 (Viz Factory): Run 'libs/viz_factory/tests/debug_runner.py'.

1. ARTIFACT ROUTING & PROOF OF LIFE:

- Strictly route all test outputs to: tmp/Manifest_test/STRESS_FINAL/.
- PRESENT EVIDENCE: Output a .glimpse() of the data and the path to 'USER_debug_{plot}.png'.

1. MANDATORY HALT:
Halt and wait for @verify. DO NOT proceed to app/src/main.py. UI testing is strictly prohibited until Phase B passes.

@Agent: Focus on structural compliance first. If the ConfigManager cannot find an include, verify the directory basename matches the YAML filename exactly.

# Nr 2 - verification

- manual and via browser agent

# New Nr 1

@Agent: @dasharch - ARCHITECTURAL REFACTOR: TEST GOVERNANCE & MANIFEST STANDARDS.

1. CONTEXT SYNC:

- Read: ./.claude/rules/workspace_standard.md
- Read: ./.claude/plans/implementation_plan_master.md
- Read: ./.claude/knowledge/architecture_decisions.md (Focus on ADR-011, ADR-024, ADR-031)

1. GOAL: RESTRUCTURE TESTING & MANIFEST RULES
You must refactor the rulebooks to eliminate duplication and enforce strict phase-gating.

A. BASE AUTHORITY REFACTOR:

- Consolidate universal "Evidence Loop" logic (Contract -> CLI -> Materialize -> Glimpse -> Halt) into ./.claude/rules/rules_verification_testing.md.
- Ensure all other workflows reference this base protocol.

B. SPECIFIC WORKFLOW EXTENSIONS:
Create or refine the following modular workflows. Each must define the specific 'Engine' (debug_*.py) to use:

- ./.claude/workflows/ingestion_testing.md (Engine: debug_ingestor.py)
- ./.claude/workflows/transformer_testing.md (Engine: debug_assembler.py)
- ./.claude/workflows/viz_factory_testing.md (Engine: debug_runner.py)
- ./.claude/workflows/ui_manifest_integration_testing.md (The "Master Gate")

C. MANIFEST STRUCTURAL STANDARD:

- Create ./.claude/rules/rules_manifest_structure.md.
- MANDATE: "Basename Mirroring". A manifest (main.yaml) MUST have its !include components in a directory named 'main/' at the same level.
- Reference assets/template_manifests/1_test_data_ST22_dummy.yaml as the structure authority.

1. EXECUTION GUARDRAIL:

- Enforce Phase-Gating: UI testing (app/src/main.py) is STRICTLY PROHIBITED until Phase A (Headless Audit) is successful.
- Audit Directory: All headless results MUST be stored in tmp/Manifest_test/{manifest_basename}/.
- Proof of Life: You must present a .glimpse() of data and the USER_debug_{plot}.png artifact for every manifest test before requesting @verify.

1. TASKS UPDATE:

- Audit tasks.md. Re-open any [DONE] items related to Gallery or Persona UI that do not meet these new standards.

PLAN BEFORE EXECUTION. Provide the proposed structure of the new/refactored files for @verify before writing.

# Nr1

Hi, here is your context for sync.

We will need an agent prompt for a new chat (the agent can have access to all the files in the project - some directories need request but has the same context files as you do):

1. Initialization

2. We need a ui testing workflow : .agent/workflows/ui_manifest_integration_testing.md

3. A. It needs to include the testing of the whole manifest (that the manifest is defined correctly and is complete - and that all libraries that use the manifest - and that the ui depend upon - are producing the expected output)

- structure of the manifest (maybe we need to write a document for the structure of yaml manifests. Example to use for this is `assets/template_manifests/*`) there is a main yaml and several files that are included in the main yaml (those included files are deposited a directory with the same basename as the main yaml and at the same level as the main yaml)
- The manifest must be completely tested and used for:
- transformer library (wrangling, assembly, production of data tiers) using the manifest
- viz factory (production of plot objects) using the manifest. Verififcation of the plot object is required (halt for verify if necessary)
- same procedure for other layers, if they are dependent on the correct specification of manifest (#REVIEW : should we add more libraries to the automatic testing?)

- audit in `tmp/Manifest_test/{manifest_basename}/*` - Then it must verify session_anchor.parquet exists and matches output_fields; that the `USER_debug_{plot_id}.png` is high-resolution and matches the mapping, and present the `.glimpse()` of the data and the rendered PNG to the user. This can include a halt for verify if the agent is not sure about the output or cannot automatically test the success of the test.

2.B When the tests in A are successfull, and ONLY then the ui testing can procede.

- The previous agent in antigravity started autonomous development and ui testing (not horrible because actually advanced a lot on debugging ui - but it needs to respect the rules, development plan and testing procedures). Some task were marked as done but are not completely finished (gallery not completed, different persona modes testing in ui not completed). We must ensure that the agent respects the rules, development plan and testing procedures.
