# Instructions and work log

date:: 2026-04-07

## New chat

@Agent: Assume persona @dasharch. SYSTEM RESET.

1. Context Alignment (READ ONLY):
   - ./.claude/rules/workspace_standard.md (Authority)
   - ./.claude/knowledge/architecture_decisions.md (ADR-024: Tiered Lifecycle)
   - ./.claude/tasks/tasks.md (Current Focus: Tier 2 Branching)

2. Task Objective:
   Implement and verify the 'Tier 2 Branch' materialization logic within the Transformer.
   Goal: Create a specialized summary LazyFrame from the Tier 1 Anchor for a 'Heatmap' functional group.

3. Constraints:
   - Use Polars LazyFrames (ADR-010).
   - Use @register_action("summarize") for the branch logic.
   - Use pl.sink_parquet() to materialize the branch to 'tmp/branch_plot_density.parquet'.

4. Verification Protocol:
   - Create 'libs/transformer/tests/data/tier2_branch_test.yaml'.
   - Execute via 'libs/transformer/tests/debug_wrangler.py'.
   - HALT for @verify once 'tmp/branch_plot_density.parquet' is generated and .glimpse() is shown.

Model: Gemini 3 Flash. Mode: Fast.

## Deeper verification

@Agent: @dasharch - TASK VISIBILITY & DEFERRED LOGIC RESTORATION.

1. RULE UPDATE: THE ACTIVE VISIBILITY PROTOCOL
   - Update Section 4 of './.claude/rules/rules_verification_testing.md'.
   - Rename the rule to: "Active Visibility Protocol (Skeletal-Archive)".
   - Mandate: "Only 100% completed [x] items may be moved to archives. ANY task that is either in-progress [ ] or [DEFERRED] MUST remain in the main tasks.md under its original logical header to ensure immediate visibility."

2. SURGICAL RESTORATION (CRITICAL):
   - Review the newly created archives in './.claude/tasks/archives/'.
   - Identify any [ ] or [DEFERRED] tasks that were moved.
   - MOVE THEM BACK to their respective headers in 'tasks.md'.
   - Ensure the progress status of active phases is fully visible again.

3. FINAL TASK RECONCILIATION:
   - Provide a terminal output showing the updated count:
     - [x] Completed (In Archives)
     - [ ] In-Progress (In tasks.md)
     - [DEFERRED] (In tasks.md)

HALT for @verify. Do not proceed until 'tasks.md' correctly shows the 'Deferred' and 'In-Progress' items."
--- -
> tasks cleaning rule

@Agent: @dasharch - FINAL VERIFICATION & RULE CODIFICATION.

1. CODIFY ARCHIVING RULE:
   - Add the 'Task Archiving Protocol (Skeletal-First)' to './.claude/rules/rules_verification_testing.md' as Section 4.

2. TRACEABILITY CARD (Tier 1):
   - As per the Transparency Mandate, explicitly list:
     - Test Data Path (Source A): [Path]
     - Test Data Path (Source B): [Path]
     - Manifest Path: [Path]
     - Resulting Parquet (Anchor): [Path]
     - Exported Full View (TSV): [Path]

3. NEXT FOCUS SETTING:
   - Now that 'tasks.md' is lean, mark the following as the ONLY [ACTIVE] focus:
     - "ADR-024: Tier 2 (The Branch) - Plot-Specific Filtered Subsets."

HALT for @verify. Once you provide the paths and confirm the rule update, we are officially done with the migration."
---

@Agent: @dasharch - FINAL TASK RECONCILIATION & INTEGRITY PROOF.

1. DATA RECONCILIATION (CRITICAL):
   - Perform a cross-check between the original 'tasks.md' (prior to skeletonization) and the new archive files in './.claude/tasks/archives/'.
   - OUTPUT to terminal:
     - Total count of [x] completed tasks BEFORE migration.
     - Total count of [x] completed tasks NOW residing in archives.
     - Confirmation that the delta is ZERO.

2. SKELETON VERIFICATION:
   - Verify that all major "Logical Unit" titles (e.g., Infrastructure & Recovery, Phase 9 Integration, Viz Factory Tracker) remain in 'tasks.md' as headers.
   - Confirm each header contains a direct path link to its specific archive file.

3. TRANSPARENCY MANDATE (Final Proof):
   - List the paths for the following artifacts generated in this session:
     - Archive 1: [Path]
     - Archive 2: [Path]
     - Archive 3: [Path]
     - Session Audit Log: [Path]

HALT for @verify. Provide the "Zero-Loss Confirmation" message in the terminal before I accept the changes."

----
> new tasks archives

@Agent: @dasharch - LOGICAL TASK REORGANIZATION & SKELETONIZATION.

1. SURGICAL MIGRATION (Preserve the Skeleton):
   - For every logical unit (Header) that is 100% complete:
     - Create a corresponding archive file: './.claude/tasks/archives/tasks_archive_[unit_name].md'.
     - Move the detailed '[x]' checklist items to that archive.
     - In the main 'tasks.md', KEEP the Header/Title but replace the body with:
       "> Status: COMPLETED. Detailed history moved to: [./.claude/tasks/archives/tasks_archive_[unit_name].md]"

2. REORGANIZE ACTIVE FOCUS:
   - Re-index 'Backend & Decorator-First' using the ADR-024 3-Tier terminology:

     - ## [DONE] Tier 1 (The Trunk): Relational Anchor (sink_parquet/scan_parquet)

     - ## [ACTIVE] Tier 2 (The Branch): Plot-Specific Anchors (Shared filtered subsets)

     - ## [PLANNED] Tier 3 (The Leaf): UI-driven Predicate Pushdown

3. TRANSPARENCY MANDATE (Verification Check):
   - List the EXACT file paths for:
     - The join data (Source A/B) used for the 'session_anchor_test.parquet' verification.
     - The new archive files created in this task.

4. DOCUMENTATION SYNC:
   - Update 'docs/reference/testing.qmd' to reflect this new Task Archiving protocol.

HALT for @verify. Provide a terminal count of how many logical units were archived.

---
@Agent: @dasharch - TASK ARCHIVE & RESET.

1. CREATE ARCHIVE DIRECTORY:
   - Ensure './.claude/tasks/archives/' exists.

2. MIGRATE COMPLETED TASKS:
   - Move all [x] completed items from 'Infrastructure & Recovery' to './.claude/tasks/archives/tasks_archive_infrastructure.md'.
   - Move the 'Phase 9: Triple-Source AMR Integration' block to './.claude/tasks/archives/tasks_archive_phase9.md'.
   - In 'tasks.md', keep the headers but replace the content with: "Archive: [Link to file path]".

3. RESTRUCTURE ACTIVE TASKS (tasks.md):
   - Under 'Backend & Decorator-First', create the "ADR-024: Tiered Data Lifecycle" roadmap:
     - [DONE] Tier 1 (The Trunk): Relational Anchor (sink_parquet/scan_parquet).
     - [ACTIVE] Tier 2 (The Branch): Plot-Specific Anchors (Shared filtered subsets).
     - [PLANNED] Tier 3 (The Leaf): UI-driven Predicate Pushdown.

4. TRANSPARENCY MANDATE:
   - Update './.claude/rules/rules_verification_testing.md' Section 3 to include:
     "Transparency Mandate: Every @verify result MUST list the exact file paths used for Data, Manifests, and Resulting Artifacts."

5. CLARIFY PREVIOUS RUN (Transparency Rule Test):
   - List the paths used for 'session_anchor_test.parquet' (Sources A/B and Manifest).

HALT for @verify once the folder structure is cleaned and the tasks are archived.

----

@Agent: @dasharch - TRANSPARENCY & LOGGING UPDATE.

@verify

1. UPDATE INTERACTION RULES:
   - Add the following to './.claude/rules/rules_verification_testing.md' under Section 3:
     "Transparency Mandate: Every @verify signal MUST explicitly list the file paths of all test data and manifests used."

2. DOCUMENTATION SYNC:
   - Update 'docs/foundations/data_tiering_adr.qmd' and 'docs/workflows/transformer_integrity.qmd' to reflect the successful implementation of the Tier 1 Anchor.
   - Use the Violet Law: 'Anchor (persistence/anchor.py)' and 'DataAssembler (data_assembler.py)'.

3. SESSION LOGGING:
   - Append the results of this Tier 1 implementation and the verification of the 'Short-Circuit' logic to './antigravity/logs/audit2026-04-07.md'.

----
@Agent: @dasharch - ARCHITECTURAL AUDIT & REPAIR.

Context:
We are verifying Phase 10 (Tiering Layer) and ADR-024.
Documentation: ./.claude/knowledge/protocol_tiered_data.md and rules_data_engine.md.

Task:

1. Re-check 'libs/transformer/src/actions/persistence/': Does the sink_parquet implementation exist and follow the (lf, spec) contract?
2. Modify 'DataAssembler (data_assembler.py)':
   - Implement the "Short-Circuit Rule": If the target anchor parquet exists and the manifest signature is unchanged, skip assembly.
   - Ensure 'sink_parquet' is called at the end of the Layer 2 join process.
3. Verify Tier 2: Confirm 'summarize' in 'performance/aggregation.py' is optimized for reducing row counts before VizFactory handoff.

Verification:

- Run 'libs/transformer/tests/debug_assembler.py' with a multi-source manifest.
- Check 'tmp/' for 'session_anchor.parquet'.
- Use 'df.glimpse()' to verify the final assembly before persistence.

HALT for @verify once the Short-Circuit logic is proven in the terminal logs.

## Initiation

@Agent: @dasharch - SYSTEM ALIGNEMENT.

Read and Align with:

1. ./.claude/rules/workspace_standard.md (Authority)
2. ./.claude/plans/implementation_plan_master.md (Roadmap)
3. ./.claude/knowledge/architecture_decisions.md (ADRs 001-025)
4. ./.claude/tasks/tasks.md (Current Focus)

Current Environment:

- IDE: Antigravity v1.19.6 (Pinned)
- OS: Fedora 43 KDE
- VENV: ./.venv/bin/python (Mandatory)

Current Priority: Phase 10: Persistence Layer (ADR-024).
Objective: Verify and complement implementation of Tier 1 (The Anchor) persistence using pl.sink_parquet() within the DataAssembler (data_assembler.py).

Protocol:

- Use Polars LazyFrames exclusively.
- Follow the Violet Law for documentation: ComponentName (file_name.py).
- Adhere to the Evidence Loop: Create {action}_test.tsv and {action}_test.yaml, then run the Universal Wrangler Runner or Assembler Debugger.
- HALT for @verify after materializing the .parquet anchor to tmp/.

Do you acknowledge the current state and the Tiered Data Lifecycle mandate?

# Above : continuing implementation

## Stage 4 actually
>
> - fixing the stupid simplink and retest !

@Agent: Execute "Structural Repair & Task Ledger Reconciliation" (Phase 11-D).

I. OBJECTIVE
Repair the library directory structures (remove symlinks) and reconcile the Phase 3 Persistence tasks to eliminate duplicates and align with the new Data-Source-Centric tiering doctrine.

II. TASK 1: DIRECTORY REPAIR (LIBS/)
The current 'transformer -> src' and 'viz_factory -> src' structure is incorrect. We require physical, standard packaging.

1. Remove all symbolic links in ./libs/.
2. Ensure every library (transformer, viz_factory, ingestion, connector, utils) follows this exact physical layout:
   - libs/{lib}/pyproject.toml
   - libs/{lib}/README.md
   - libs/{lib}/src/ (Contains all functional package code)
   - libs/{lib}/tests/ (Contains all debug scripts and /data/ folder)
3. Use 'mv' and 'rm' commands to fix this physically. Do NOT use symlinks.

III. TASK 2: TASK LEDGER RECONCILIATION (tasks.md)

1. Read ./.claude/tasks/tasks.md.
2. Identify and DELETE all duplicated task blocks.
3. Re-index Phase 3 (Persistence Layer) to reflect the new doctrine:
   - "Implement Tier 1 (Trunk) persistence (sink_parquet) anchored on Common Data Source ID/Path."
   - "Implement Tier 2 (Branch) pre-aggregation shared by Functional Plot Groups."
   - "Verify that 'Short-Circuit' logic correctly identifies existing Parquet anchors to prevent 22-min re-renders."

IV. TASK 3: RE-VERIFICATION OF REFRESHED LIBS

1. Once directories are moved, confirm 'pip install -e ./libs/{lib}' is still valid in the root .venv.
2. Run 'libs/transformer/tests/transformer_integrity_suite.py' once to ensure the directory move didn't break import paths.

V. FINAL HALT

- Provide a clear summary of the physical directory changes (from/to).
- Confirm duplication removal in tasks.md.
- Provide a "One-line State of Truth" regarding the structural integrity.
- Await @verify.

## Stage 3

@Agent: Execute "Surgical Architectural Finalization" (Phase 11-C).

I. OBJECTIVE
Finalize the homogenization of project rules, persona protocols, and testing logic. You must ensure strict boundary enforcement and optimize data processing for large, multi-source manifests.

II. MANDATORY UPDATES

1. Boundary Lock (.aiignore at Root):
   - Update `rules_runtime_environment.md` and `dasharch.md`.
   - Command: "The agent MUST strictly respect the .aiignore file located at the project root. Do not scan directories like EVE_WORK, archives, or .claude/embeddings/ unless the user explicitly grants a 'Border-Crossing Permit' for a specific file."

2. Tiered Data (Data-Source Centric Sharing):
   - Update `rules_data_engine.md`.
   - Redefine the 'Bifurcation Point' for large manifests (e.g., ResFinder, Virulence Finder):
     - Tier 1 (The Trunk): Relational Anchor. Logic applied to a common data source (identified by ID or Path) that is shared by ALL plots dependent on that source.
     - Tier 2 (The Branch): Plot-Specific Anchor. Logic or pre-aggregation shared by a Functional Group of plots (e.g., all Heatmaps using the same filtered subset).
     - Instruction: "To minimize recalculation, always suggest a wrangling sequence that prioritizes shared transformations as early as possible (Tier 1) based on the common data source ID/Path."

3. Persona Entry Protocol (Token & Logic Efficiency):
   - Update `dasharch.md`.
   - Command: "SESSION START: Your absolute first action is to read ./.claude/rules/workspace_standard.md. Based on the task at hand, selectively ingest only the relevant rules and workflows to conserve tokens and prevent knowledge drift. Do not scan the entire workspace by default."

4. Testing Hierarchy (Engines vs. Orchestrators):
   - Replace the 'Testing Protocols' section in `rules_verification_testing.md` with this logic:
     - Component Debuggers (The Engines): `libs/{lib}/tests/debug_{component}.py`. Specialized runners for isolated logic (e.g., `debug_wrangler.py` for Layer 1 decorators).
     - Global Library Wrapper (The Orchestrator): `libs/{lib}/tests/{lib}_integrity_suite.py`. A high-level runner that programmatically discovers actions and dispatches them to the appropriate 'Engine' for verification.
   - Command: "The Orchestrator MUST use the Engines to perform the actual execution; it does not contain the testing logic itself."

III. DOCUMENTATION & SITE SYNC

- Update `docs/reference/testing.qmd` to reflect the 'Engines vs. Orchestrators' hierarchy exactly.
- Update `docs/foundations/data_tiering_adr.qmd` with the new data-source-centric sharing rules.
- Ensure all library READMEs point to the correct `{lib}_integrity_suite.py`.

IV. FINAL HALT

- Provide a summary of updated files.
- Provide a "One-line State of Truth" regarding the new boundary and data sharing rules.
- Await @verify before updating .claude/tasks/tasks.md.

-----
Improvement / clarification - modulation

Hi, we need to have a control of some of the updates and agent behaviour that was made-

1. The agent does not respect the boundaries of AI ignore - and scans through the whole project, including directories that are not relevant to the task and that are defined, directories that are marked as to be ignored in the .aiignore file (it can however asks specific permission when relevant or when explicitly asked to do so in the rules files). This is not good from my token usage nor for privacy purposes, and it risks to confuse the agent as I keep archives in the EVE_WORK directory. We need to ensure respect of AI ignore boundaries.

2. We need to inspect if the changes that were made are correct and complete. I attached the new context and rules files (attached the new context files as a single concatenated file, I ommited the python scripts as they are not relevant for now). You need to review if the changes that have been implemented are correct and complete (when asked you can make a review prompt for antigravity so that the agent can implement the minor required updates). I ask you to focus even more thouroughly on those specific points:  

- A) rules_data_engine.md : move from tier 2 to tier 1 : when its shared by more than 3 plots, maybe it needs to be when shared by all the plots depending on the data source  (need to ensure the data can be used by all branches otherwise the app will fail, but it could suggest eg a logic that allow to maximize sharing eg, steps order feks)
- B) dasharch.md -> @dasharch must read the workspace_standard.md file entry rule and must be redirected to all other rules, workflow and knowlege file. Also I think the agent should be able to access and read relevant context depending on the task at hand, is this something we need to codify ?
- C) please review that this paragraph in rules_verification_testing.md is correct and consistent with the testing_hiearchy_logic.md file.

```
- **Global Library Wrapper:** `libs/{lib}/tests/{lib}_integrity_suite.py`
  - *Purpose:* Programmatically query the registry, ingest all registered manifest-data combinations, execute them, and yield an automated `{lib}_integrity_report.txt`.
  - *Rule:* The global library wrapper script MUST be launched to ensure the entire system functions organically during broad refactorings.
- **Component Debuggers:** `libs/{lib}/tests/debug_{component_name}.py` 
  - *Purpose:* Isolated testing for individual features, decorators, or core modules during active development.
```

 I need to ensure that it is clear eg:  transformer library has 2 componets: the wrangler and the assembler, so we need 2 tests files BUT eg the wrangler need to be able to test all decorators, but one by one. While the  Global Library Wrapper is a wrapper that use the wrangler and assembler tester to test each decorator that is implemented on the whole library so I need to ensure that this logic is clear. Can you rewrite this paragraph instructions in a markdown text box so I can add it in the correct place in the documentation ?
 It seems that the reformating has been done according to what I want, but I am unsure if the instructions are clear enough (I might understadn those diferently than the AI)

 -D) Ebsyre that the documentation correctly reflect your paragraph on ### 🧪 Testing Hierarchy & Logic

## Stage 2

@Agent: Execute "Project Architecture & Rulebook Homogenization" (Refactor Phase 11).

I. OBJECTIVE
Restructure all project rules, workflows, and test naming conventions to align with the "3-Tier Tree Data Lifecycle" and "Homogeneous CLI Standards." You must eliminate architectural drift and redundancy.

II. MANDATORY READS (CURRENT STATE)

- ./.claude/rules/ (all files)
- ./.claude/knowledge/architecture_decisions.md
- ./.claude/knowledge/project_conventions.md
- ./libs/transformer/tests/
- ./libs/viz_factory/tests/

III. TASK 1: THE 5-FILE RULEBOOK SPLIT
Delete all existing files in ./.claude/rules/ and replace them with these 5 authoritative files (Max 12k chars each):

1. rules_documentation_aesthetics.md:
   - Merge rules_aesthetic.md and rules_documentation_standards.md.
   - Enforce "Violet Law": ComponentName (file_name.py) is strictly for HUMAN-FACING .qmd and READMEs.
   - Prohibit Violet Law in functional code, logic, or docstrings.
   - Include Quarto/Mermaid zoomability and CSS theme standards.

2. rules_data_engine.md:
   - Merge rules_wrangling.md, rules_tiered_data.md, and ADR-024.
   - Implement the "3-Tier Tree Lifecycle":
     - Tier 1 (Trunk): Relational Anchor (All joins/heavy cleaning). Parquet on disk.
     - Tier 2 (Branch): Plot-Specific Anchor (Pre-aggregation/shrunk data for heavy plots). Parquet on disk.
     - Tier 3 (Leaf): Interactive UI View (Transient filters/LazyFrames). In-memory or tmp/.
   - Define "Bifurcation Point": Transformations shared by >3 plots move to Tier 1; plot-specific logic stays in Tier 2.

3. rules_verification_testing.md:
   - Standardize Naming:
     - Full Library: libs/{lib}/tests/{lib}_integrity_suite.py
     - Component Debuggers: libs/{lib}/tests/debug_{component_name}.py
   - CLI Mandate: Every Python script (libs and assets/scripts) MUST use argparse with a --help docstring. No hardcoded paths.
   - Enforce the @verify protocol (1:1:1 Evidence Loop).

4. rules_runtime_environment.md:
   - Enforce ADR-011 (Modular Monorepo) and ADR-016 (Editable Mode).
   - Strict VENV lock and DNF pinning for Antigravity v1.19.6 integrity.

5. rules_asset_scripts.md:
   - Governance for ./assets/scripts/.
   - Data Priority Hierarchy: 1. CLI Override (--data), 2. Manifest 'source' key, 3. Default Skeleton.
   - Differentiate "Suggestive Tools" (Synthetic data) from "Functional Assistants" (Manifest bootstrappers).

IV. TASK 2: WORKFLOW REFACTORING
Update ./.claude/workflows/ (implementation_workflow_transformer.md and visualisation_factory.md) to:

- Use the 3-Tier Tree logic (Trunk -> Branch -> Leaf).
- Reference the new standardized test naming (lib_integrity_suite.py).

V. TASK 3: CODEBASE & INDEX CLEANUP

- Rename all existing integrity suites to follow the {lib}_integrity_suite.py pattern.
- Update ./.claude/rules/workspace_standard.md (The Master Index) to point to the 5 new rulebooks.
- Update ./.claude/rules/dasharch.md: Add "Integrity Guardian" instructions: check integrity_report.txt before writing code; enforce naming laws.

VI. FINAL HALT
Provide a summary of deleted/renamed files and a "One-line State of Truth." Await @verify before committing changes to .claude/tasks/tasks.md.

## Stage 1

- [ ] Review all rules for AI context (first pass). In .claude/rules/
  - [x] rules_documentation_standards.md
  - [x] rules_aesthetic.md -
  - [x] rules_behavior.md
  - [x] rules_runtime.md
  - [x] rules_tiered_data.md
  - [x] rules_wrangling.md
  - [x] workspace_standard.md
- [ ] in .claude/workflows/
  - [ ] implementation_workflow_transformer.md
  - [ ] verification_protocol.md
  - [ ] viz_factory_implementation.md
- [ ] in .claude/knowledge/
  - [ ] architecture_decisions.md
  - [ ] blockers.md
  - [ ] milestones.md  
  - [ ] project_conventions.md
  - [ ] protocol_tiered_data.md
- [ ] in .claude/plans/
  - [ ] implementation_plan_master.md
- [ ] in .claude/tasks/
  - [ ] tasks.md

AI TO DO :
Hi, I attached your !sync file for the context (one large file that concatenates the main context and some other files we will need to review). Please read this context thoroughly.

We need to inspect the context and rules files and propose a new version of the rules files.

1 Do not remove rules unless agreed with me.
2 When we agree at the end of our conversation, and solely then, you will need to prepare a prompt for the antigravity integrated AI with the detail instructions so it can do the necessary changes we agreed upon, using the gemini 3 Flash model. This means you will need to detail all the steps and provide clear instruction of what needs to be changed. I will indicate that all has been reviewed and agreed via @generate_prompt.
3 **Important: All rules and workflow files are limited to 12,000 characters each, Therefore it is important to adopt a correct structure and split the files in logical parts**.

Here are some points I noted for review, but they are not exhaustive (so you will need to review all the and suggest better organization):

A. rules_aesthetic.md and rules_documentation_standards.md : redundancy shoult it be merged  in one single document ? Eventual inconsistencies must be found and resolved.
B. we need to ensure homogeneity in development rules : for the tests scripts eg. naming -> extract rule from the code structure (eg `tests/{lib}_integrity_suite.py`  might need to be renamed to current debug (see tree), we need also to ensure that it is writen in the rules that we an individual test script eg. per decorator / function and then a global wrapper to test the whole library (there are some parts already in the files). But we need to ensure consistency when continuing development.
C. It is important that a rule is given to ensure that all python scripts use argparse, because it needs to be possible for the user to use via command line. Wrappers scripts must adapt to this, running all individual tests via argparse.
D. rules_behavior.md : violet law ? shoult it only appear in the docs ? or should it refered to when necessary (avoid redundancy when not necessary)
E. tiered data protocol : note that a plot might reuse the same basic wrangling, so tier data might need to be stopped at a certain level, which will allow bifurcating the data transformation for different plots. We will need a solution after for update of the tier data2 from user (but need to be at a later stage)
F. should the rules_tiered_data.md merged or at least be mentionned in rules_wrangling.md ? should the context .claude/knowledge/protocol_tiered_data.md be mentionned or partially merged with rules_tiered_data.md ... and rules_wrangling.md ... ?
G. we need to create rules for the development of helper scripts for the user, in order consistency and their usage and purpose must also be documented. Scripts to assist uers are in .assets/scripts and I added those scripts to the context file.
H. At the end,  you will need to review the antigravity agent definition (.claude/rules/dasharch.md), and propose improvements of its definition so it can better assist the user in its tasks.
I. When this is settled , .claude/rules/workspace_standard.md will need to be updated, to ensure that the agent has to review the appropriate context files and rules ... as this is the main entry point for the agent (the file that explain what the agent must read and ingest before starting to work)
