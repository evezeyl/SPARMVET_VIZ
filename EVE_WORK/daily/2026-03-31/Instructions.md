# Instructions for GEM

## Closing 
@Agent: @dasharch - FINAL SESSION LOG & SHUTDOWN.

1. DOCUMENTATION & RULE FINALIZATION:
- VERIFY INTEGRATION OR INTEGRATE the 'Split-Documentation Strategy' into ./.claude/rules/documentation_standards.md.
- VERIFY/UPDATE ./.claude/knowledge/project_conventions.md to reflect the new .claude/ and .claude/ split.

2. GENERATE COMBAT LOG (TEMPLATE STANDARD):
Create a new entry in ./.claude/logs/{date}_session_logs.md (or create the file if missing) using the following format:

## 📅 Session Log: 2026-03-31 [TRANSFORMER REFACTOR]
- **Status**: 🟢 SUCCESSFUL REORG & INTEGRITY AUDIT.
- **Key Accomplishments**:
    - [x] Migrated 25 actions to Tiered Schema (reshaping, cleaning, relational, performance).
    - [x] Implemented 'Integrity Suite Mandate' & 'Transformer Integrity Suite'.
    - [x] 100% Violet Law Compliance across READMEs and Quarto Docs.
    - [x] Established 'Split-Documentation' (Compact tables in main, Examples in Appendix).
- **Physical State**: 21/23 Actions verified via 1:1:1 Naming Law tests.
- **Next Focus**: Phase 3 Persistence (ADR-024) - Implementation of 'checkpoint' and 'restore' decorators.

3. TASK SYNC:
- ENSURE that all the finished tasks are updated and verified 

4. HALT:
- Confirm the log is written and the workspace is synchronized.
- TERMINATE session. See you later.

## Documentation docs 

- Implementations from today and yesterday . viz factory and transformer layer 
Ensure complete, redeable, reorganize for good flow if necessary and register files in _quarto.yml


@Agent: @dasharch - DOCS INTEGRITY & QUARTO SYNC.

1. AUDIT & HARVEST:
Read all files in ./.claude/ (rules, workflows) and ./.claude/ (knowledge, plans, tasks, logs (yesterdays log only)). 
Ensure the following specific updates from at least the last 48 hours are captured:

2. QMD CONTENT REORGANIZATION:
Create/Update/reorganize the following .qmd files in 'docs/' to reflect a professional 'Dev-to-User' flow:

- docs/standards.qmd: Centralize all 'Laws' and 'Conventions'.
- docs/transformer.qmd: Document the 4-Phase workflow and the full action registry.
- docs/persistence.qmd: Explain the Tier 1/2 materialization and the session_anchor.parquet logic.
- docs/viz_factory.qmd: Document the component-based architecture and its new integrity suite.
- docs/developer/rules.qmd: 'The Laws of SPARMVET' (Violet, 1:1:1, Integrity).
- docs/developer/testing.qmd: 'Testing Protocol' - Running the Integrity Suites and verifying the 'State of Truth'.
- docs/transformer/actions.qmd: 'Action Gallery' - Categorized list of all 25+ verified decorators.
- docs/transformer/persistence.qmd: 'Data Tiering' - Explain the Anchor vs. View lifecycle (ADR-024).


3. QUARTO CONFIGURATION:
- UPDATE '_quarto.yml': Ensure all new and reorganized .qmd files are properly registered in the sidebar/navigation.
- COMPLIANCE: Ensure all README.md files in ./libs/ link back to these master docs.
- Ensure they provide a high-level summary and then explicitly LINK to the corresponding .qmd files in docs/ for deep-dives.

4. VERIFY, REORGANIZE AND UPDATE TASKS:
- Verify and update tasks are done if they have been implemented in the last 2 days 

4. HALT & RENDER:
- Generate a 'tmp/docs_registry.txt' showing the mapping of Knowledge/Rules -> QMD files.
- HALT and provide a summary of the navigation structure in _quarto.yml for @verify.




## Integrity of rules 

ok, now before we continue, we need to make a little reorganizing of .agents and .antigravity we have in a way 2 workspace standards to ensure homogeneity, consistency and correct placement in ./agents

We need to ensure rules and workflows are placed in .agent
We need to ensure that .antigravity contains only knowledge, plans, and tasks (and logs).

And we need to read all the files that are currently in the mentioned directories in .agent (rules, workflows) and .antigravity (knowledge, plans, tasks), read and understand the content of each file and then reorganize if necessary in the appropriate file in the appropraite directory. 

I can use a thinking agent for this. 

---

@Agent: @dasharch - ARCHITECTURAL REORGANIZATION & SYNC.

1. MANDATE: CLEAR SEPARATION OF CONCERNS
Reorganize the workspace configuration directories to enforce the following hierarchy:
- ./.claude/  => DIRECTIVES (rules/, workflows/)
- ./.claude/ => PROJECT STATE (knowledge/, plans/, tasks/, logs/)

2. AUDIT & MOVE (Step-by-Step):
Read the content of all files in these directories and MOVE them to their compliant locations:
- MOVE: Any 'workflow' or 'protocol' file (e.g., ./.claude/plans/implementation_workflow_transformer.md) to ./.claude/workflows/.
- MOVE: Any 'rule' or 'standard' file to ./.claude/rules/.
- ENSURE: architecture_decisions.md, project_conventions.md, and protocol_tiered_data.md remain in ./.claude/knowledge/.
- ENSURE: implementation_plan_master.md remains in ./.claude/plans/.
- ENSURE: tasks.md remains in ./.claude/tasks/.

3. REFERENCE UPDATE (CRITICAL):
- SCAN all files in the new ./.claude/ and ./.claude/ directories.
- UPDATE any relative paths or cross-references inside the markdown files to reflect the new structure.
- UPDATE the 'File Registry' in ./.claude/knowledge/project_conventions.md to match the final physical state.

4. LOGGING & VERIFICATION:
- CREATE 'tmp/reorg_audit.txt' listing: [OLD PATH] -> [NEW PATH].

HALT and present the finalized directory tree and the 'reorg_audit.txt' for @verify.
---


##  Standard 
@Agent: @dasharch - NEW MANDATE: THE INTEGRITY SUITE PROTOCOL.

1. UPDATE STANDARDS:
- ADD the 'Integrity Suite Mandate' to ./.claude/knowledge/project_conventions.md.
"## 10. The Integrity Suite Mandate (Standardization)
**Authority:** Mandatory for all packages in `./libs/`
**Goal:** Automated discovery and validation of all registered decorators.

1. **Required Artifact**: Every library MUST contain a `tests/{lib}_integrity_suite.py` runner.
2. [cite_start]**Action Discovery**: The suite must programmatically query the library's registry (e.g., `AVAILABLE_WRANGLING_ACTIONS` or `PLOT_COMPONENT_REGISTRY`) to list all implemented actions.
3. [cite_start]**1:1:1 Validation**: For every registered action, the suite must locate and execute its corresponding test triplet (TSV data, YAML manifest, and verification output).
4. **Automated Reporting**: The suite must generate a standardized `integrity_report.txt` in `tmp/` covering:
    - **Inventory**: All implemented actions and their categories.
    - **Status**: [PASSED], [FAILED], or [NO TEST DATA] (strictly for helper exceptions).
    - [cite_start]**Compliance**: Verification of ADR-013 (Dual-Validation) and ADR-022 (Violet Law)[cite: 1].
"
- Ensure the rule requires (1) Action Discovery, (2) 1:1:1 Validation, and (3) Standardized Reporting.

Information: The user added those new tasks
"### 🛡️ Library Integrity & Quality Assurance (NEW MANDATE)
- [ ] **Standardize Transformer Integrity:** Rename `transformer_integrity_suite.py` to follow the final standard and ensure Phase 3/4 coverage.
- [ ] **Viz Factory Integrity Suite:** Refactor `bulk_debug_viz_factory_layers.py` into `viz_factory_integrity_suite.py`.
    - [ ] Implement automated component discovery from the `registry.py`.
    - [ ] Map all 35+ verified components to the 1:1:1 Evidence Loop.
    - [ ] Generate the standardized `viz_factory_integrity_report.txt`.
- [ ] **Project-Wide Compliance:** Ensure all future `./libs/` additions include an integrity suite by default."

2. REFACTOR VIZ FACTORY TESTS:
- RENAME 'libs/viz_factory/tests/bulk_debug_viz_factory_layers.py' to 'libs/viz_factory/tests/viz_factory_integrity_suite.py'.
- UPDATE the script to programmatically discover all registered components (geoms, scales, themes, etc.) from 'libs/viz_factory/src/registry.py'.
- ENSURE it generates a 'viz_factory_integrity_report.txt' in 'tmp/' following the same format as the Transformer report.

3. EXECUTE & AUDIT:
- RUN the new 'viz_factory_integrity_suite.py'.
- HALT and present the 'Integrity Summary' table for the Viz Factory components for @verify.

Follow Verification Protocol: Materialize the updated conventions and the new report to 'tmp/' first.

## Automation library testing

@Agent: @dasharch - INTEGRITY SUITE IMPLEMENTATION.

Before we implement Phase 3 (Persistence), we require a master sanity check to ensure the new Tiered Schema is 100% functional.

1. CREATE 'libs/transformer/tests/transformer_integrity_suite.py':
- This script must act as a wrapper for both 'wrangler_debug.py' and 'assembler_debug.py'.
- TASK: Programmatically discover all actions in 'AVAILABLE_WRANGLING_ACTIONS'.
- TASK: Iterate through 'libs/transformer/tests/data/' and execute the 1:1:1 Naming Law tests for every registered action.
- TASK: Execute all existing Assembly Recipes (Layer 2) to verify relational integrity.

2. LOGGING & INVENTORY:
- The suite MUST print a clear inventory of all implemented decorators and their names.
- CATEGORIES: Reshaping, Cleaning (Core/Expressions/Advanced), Relational.
- REPORT: Clearly distinguish between [PASSED], [FAILED], and [NO TEST DATA FOUND].

3. DEFERRAL:
- Layer 3 (Exploration/Graphs) is explicitly DEFERRED for this audit.

4. HALT:
- Run the suite and materialize the full 'Integrity Report' to 'tmp/{date}transformer_integrity_report.txt'.
- HALT and present the list of implemented actions and pass/fail summary for @verify.


--- 

- [x] Reading new files 

## Extracting list of missing decorators for the transformer - polar library 
https://pola.rs/

- ./.claude/workflows/transformer_implementation.md (procedure)
- ./.claude/plans/implementation_plan_master.md (implementation plan) - updated 

--- 
> verification status 
@Agent: @dasharch - STOP & AUDIT PROTOCOL.

You have indicated progress through the task list. Before any new logic is written, you MUST perform a 'State of Truth' verification to ensure no technical debt or 'Ghost State' exists.

1. DIRECTORY & REGISTRY AUDIT:
- Verify 'libs/transformer/src/actions/' matches the Tiered Schema: (reshaping/, cleaning/, relational/, persistence/, performance/).
- Confirm every sub-package has an '__init__.py' that imports local modules to trigger the @register_action registry.
- PROVE IT: List all actions currently recognized in the 'AVAILABLE_WRANGLING_ACTIONS' dictionary.

2. COMPLIANCE AUDIT (THE LAWS):
- Verify 1:1:1 Naming Law: For every migrated/new action, confirm a corresponding .tsv and .yaml exists in 'libs/transformer/tests/data/'.
- Verify Violet Law: Check 'project_conventions.md' and library READMEs to ensure components are referenced as 'ComponentName (file_name.py)'.

3. FUNCTIONAL VERIFICATION:
- Run 'libs/transformer/tests/test_decorator_suite.py'.
- If any legacy tests fail due to the reorganization, they MUST be fixed now.
- MATERIALIZE RESULTS: Save the 'test_decorator_suite' output and a tree view of 'libs/transformer/src/actions/' to 'tmp/audit_log.txt'.

4. ADR-024 CHECKPOINT:
- Confirm 'DataAssembler (data_assembler.py)' has the scaffold for the 'Short-Circuit' rule from 'protocol_tiered_data.md'.

HALT and present the 'tmp/{date}_audit_log.txt' and registry list. DO NOT proceed to Phase 1 until this audit is @verified.

---- 
> Migration of legacy decorators 

@Agent: @dasharch - SYSTEM RESET & REFACTOR MISSION.

1. INITIALIZE & MIGRATE (PRIORITY 1):
- Initialize the new directory structure in 'libs/transformer/src/actions/'.
- MOVE existing decorators from 'core/' and 'advanced/' to their new homes as per the Tiered Schema:
    - Cleaning (Core): fill_nulls, rename, drop_duplicates, keep_columns.
    - Cleaning (Expressions): strip_whitespace.
    - Cleaning (Advanced): derive_categories (Move to 'cleaning/advanced.py').
    - Reshaping: split_column, split_and_explode.
    - Relational: join, join_filter.


2. INTEGRITY CHECK (HALT):
- Update all '__init__.py' files in 'libs/transformer/src/actions/' to ensure auto-loading of all migrated functions.
- Run 'libs/transformer/tests/test_decorator_suite.py' to confirm migration success.
- HALT and provide a "Migration Success Report" showing all legacy actions are registered and passing.


3. PHASE 1: NEW RESHAPING DECORATORS:
- Post-migration, Verify and implement these NEW actions if not already implemented in 'reshaping/core.py':
    - 'unpivot', 'explode' (batch-ready), 'unnest', and 'pivot'.
- Follow the 1:1:1 Naming Law for Evidence Loop triplets in 'libs/transformer/tests/data/'.
----
@Agent: @dasharch - SYSTEM RESET & PHASE 10 DEPLOYMENT.

1. FILE INTEGRATION & SYNC:
- USER moved the provided 'implementation_workflow_transformer.md' to ./.claude/plans/.
- User has overwritten ./.claude/knowledge/project_conventions.md with the 'project_conventions_updated.md' content
- READ ./.claude/knowledge/protocol_tiered_data.md to internalize the Anchor vs. View logic.

2. DOCUMENTATION COMPLIANCE:
- Verify that the 'File Registry' in project_conventions.md correctly lists all Tiered Data components.
- Ensure all references follow the 'Violet Law' (ComponentName (file_name.py)) as per ADR-022.

3. SCHEMA APPROVED (Directory restructuring for the Transformer's action registry accepted). 
- INITIALIZE DIRECTORY STRUCTURE:
Create the proposed sub-packages in 'libs/transformer/src/actions/' and ensure each has an '__init__.py' that preserves the auto-loading registry logic defined in ADR-001.
- EXECUTE PHASE 1 (RESHAPING):
Implement the decorators for 'unpivot', 'explode', 'unnest', and 'pivot' in 'reshaping/core.py'.
- EVIDENCE LOOP:
Follow the 1:1:1 Naming Law for each new action. Generate test triplets in 'libs/transformer/tests/data/' and materialize verification results to 'tmp/' using 'wrangler_debug.py'.

4. HALT:
Once Phase 1 is verified with @glimpse() results in the terminal, HALT for @verify before proceeding to Phase 2.


---- 

```text

@Agent: @dasharch - SYSTEM RESET & CONTEXT SYNC (PHASE 10 INITIATION)

1. RE-ESTABLISH SOURCE OF TRUTH (READ ONLY):
Execute a full read of the following updated files to align with ADR-024 (Tiered Data Lifecycle):
- ./.claude/knowledge/architecture_decisions.md (Review ADR-024)
- ./.claude/knowledge/protocol_tiered_data.md (NEW Logic Protocol)
- ./.claude/plans/implementation_plan_master.md (Phase 10 Roadmap)
- ./.claude/tasks/tasks.md (Updated 'Transformer Reorganization & Tiering' header)

2. MANDATORY DOCUMENTATION TASKS:
Before any logic execution, update the workspace documentation to reflect the new architecture:
- UPDATE ./.claude/knowledge/project_conventions.md: Add 'protocol_tiered_data.md' to the File Registry and update the 'Wrangling' section to acknowledge the Tier 1 (Anchor) vs. Tier 2 (View) logic.
- CREATE ./.claude/plans/implementation_workflow_transformer.md: Use the structure from viz_factory_implementation.md. Define 4 Phases: 
    - Phase 1: Structural (unpivot, explode, unnest)
    - Phase 2: Atomic Expressions (coalesce, cast, regex_extract)
    - Phase 3: Persistence (sink_parquet, scan_parquet)
    - Phase 4: Performance (group_by, agg)
- COMPLIANCE: Use ADR-022 'Violet Law' (ComponentName (file_name.py)) for all new component references in documentation.

3. STRATEGIC SCHEMA DRAFT:
Propose a directory schema for libs/transformer that groups decorators into logical sub-packages (e.g., reshaping/, cleaning/, relational/, persistence/). DO NOT implement yet.

4. OPERATIONAL GATE (HALT):
Current Status: Initiating 'Step 1: Inventory Audit'. 
- DO NOT generate code for decorators or persistence logic yet.
- HALT and confirm you have updated the documentation and internalized the 'Short-Circuit' logic from protocol_tiered_data.md.
- Await the final user-provided inventory list.

Follow Verification Protocol: Materialize doc changes to tmp/ for @verify before committing to knowledge/.
```

## Reminder 
⚖️ The Logic Behind the Move
The "Technical Bible" Rule: According to the Workspace Standard, the ./.claude/knowledge/ directory is the designated home for the Primary Technical Bible, including architecture decisions. Since this file serves as the specific technical implementation logic for ADR-024, it belongs right next to the architecture decisions.

Naming Consistency: Your existing files follow a noun_description.md pattern (e.g., architecture_decisions.md, project_conventions.md). protocol_tiered_data.md fits this rhythm perfectly while mirroring the "Protocol" terminology used in the agent's workflow.

Discovery for @dasharch: By placing it in knowledge/, you keep the foundational "Why" (ADR-024) and the "How" (the Protocol) in the same logical bucket. This makes it easier to reference in the "Alignment Prompt" without adding new directories to the agent's scan path.

## Context

We will for now delay that - please make a note of it - I will ask "resume block and next steps resolution". 

We will start find out what decorators can be missing for the transformer and then implement them. Do not write any prompt until requested. We will do one step at the time. 

Here is the plan of what we are going to do (step by step), And we will need to think together. 

1. Find a way to list all the polar tidy and wrangling functions that are implemented and that could be useful for the transformer library 
This will require accessing the polar library documentation and source code. 
We need to find a solution to either extract the doc from the website, get the source code, so you can scan it.
2. We need to revise the transformer library to see what decorators are missing to implement all the polar tidy and wrangling functions. It might mean to reorganize the transformer library. 
We have here several points to consider:
- we need to wrangle and tidy any type of data in a tidy format (this is the main goal of the transformer library)
- we need to assemble different tidy dataframes in a tidy format (this is the secondary goal of the transformer library)
- we want to consider implementing a way to temporary store the assembled data on disk (in a tmp folder - that can later on be specified - depending in which system eg IRIDA, Galaxy, local, via a docker container the app will be used...) to avoid memory issues. This might need to be particularly important, for when we will add a secondary function to the transformer library that will allow further filtering of the tidydata via buttons and selects in the UI. That would allow not to have to recompute all the transformation steps every time the user wants to filter the data eg. via the UI, eg. to explore the data in the UI eg. selecting specific values in columns that are used for a specific plot. This would allow to return to the original tidydata step associated to the plot much faster. So we should think about how to implement that, and we need to think efficiency for heavy datasets. 
- When this is decided, we need to add those changes to the correct implementation and architecture decision docs and update the tasks.md file in antigravity accordingly.

Then we can : 
3. See if we need to reorganize the directory structure of the transformer (aka eg. a similar thinking process as we had done for the viz_factory)
4. make a list of all decorators that are not yet implemented but require to be implemented in the transformer factory, this will be a list of tasks (markdown text box) that I will copy those in the tasks.md file in antigravity. 
5. make an implementation workflow similar to the implementation workflow we had done for the viz_factory_implementation.md
6. run the reorganisation and ensure that all the decorators already implemented are tested to ensure that the already implemented decorators are running and passing tests.
7. Then we can start implementing the missing decorators in the transformer factory. 


Lets start by step 1. Here is the url for the documentation for the python polar library: https://docs.pola.rs/api/python/stable/reference/index.html


- [x] Given
- [ ] Asked to wait for "resume block and next steps resolution" - for the guidance so we can focus on the exhaustive implementation of the transformer - polar library 
- [ ] 


# Decorators 

5. Strategy for missing decorators
As we begin Step 1 of your plan, I have identified the following "Must-Have" decorators missing from the current tasks.md:

unpivot (formerly melt): Critical for converting wide antibiotic panels to tidy long format.

coalesce: For multi-source metadata where one column might have nulls that need filling from another.

aggregate / summarize: For the Pre-Aggregation strategy to reduce row counts.

pivot: For specialized summary exports (e.g., Species vs. Resistance Matrix).

RequirementPolars FunctionDecorator Name (Proposed)Persistencesink_parquet() / write_parquet()@register_action("checkpoint")Fast Recoveryscan_parquet()@register_action("restore_anchor")Explorationfilter(), select()Already in core/UI-Ready Reductiongroup_by().agg()@register_action("summarize")

SPARMVET_VIZ Antigravity Specialist
Custom Gem
SPARMVET_VIZ Antigravity Specialist said
This is a strategic turning point for the SPARMVET_VIZ architecture. Based on your "Step 2" goals and the technical constraints of Plotnine (which struggles with Matplotlib's overhead for 200k+ rows), here is the technical breakdown.

1. Where does Pre-Aggregation belong?
The Verdict: The Transformer Library (as a Layer 3 or "Summary" pass).

While the note suggested updating the VizFactory, architectural best practices dictate that Data Transformation (backend) should be decoupled from Information Presentation (frontend).

Why Transformer?: Polars is 5–20x faster than Pandas/Matplotlib for aggregations. By implementing a summarize or aggregate decorator in the Transformer, we reduce the data volume before it touches the VizFactory.

The Bottleneck: Plotnine (the artist) is the bottleneck, not Polars (the engine). Passing 200k rows to ggplot() causes the 22-minute lag; passing a pre-aggregated 50-row summary table takes milliseconds.

Action: We should add a Layer 3: Summary Factory to the Transformer, which can be triggered by the UI or a manifest flag.

2. The Parquet Checkpoint Workflow
You don't need a separate "parquet library"; Polars handles Parquet natively and with extreme efficiency.

What is Parquet?
Parquet is a columnar storage format that mirrors how Polars stores data in memory. It is significantly faster and smaller (~80% smaller) than CSV because it only reads the columns and rows you actually ask for (Predicate Pushdown).

The "Checkpoint" Workflow (Aligned with your Step 2)
To achieve the "Efficiency for heavy datasets" you requested, the app workflow should follow this loop:

Stage	Component	Action	Result
1. Primary Build	Transformer	Executes Layer 1 (Tidy) & Layer 2 (Assemble).	LazyFrame
2. Checkpoint	Transformer	Calls .sink_parquet("tmp/anchor_table.parquet").	On-Disk Anchor
3. UI Exploration	App/Server	Uses pl.scan_parquet("tmp/anchor_table.parquet").	Instant "Virtual" Table
4. UI Filter	App/Server	Applies .filter(pl.col("Species") == input.selection).	Fast Subsetting
5. Hand-off	VizFactory	Collects the filtered/aggregated data for Plotnine.	Fast Render
FunctionAction TypePurpose in Transformerunpivot() (or melt())StructuralConverts wide data (e.g., columns for each gene) into long format (Gene Name | Result).pivot()StructuralUsed for final summary reports where specific wide-matrix views are needed.explode()Atomic/Adv.Expands list-like entries (e.g., multiple genes in one cell) into multiple rows.unnest()StructuralFlattens struct columns (common in complex bio-informatics JSON/Parquet).2. Atomic Cleaning & Wrangling (Layer 1)These are candidates for @register_action decorators to ensure data integrity before assembly.Null/Nan Logic: fill_null(), drop_nulls(), coalesce() (takes the first non-null value across columns—great for backfilling).String Precision: str.strip_chars(), str.replace(), str.extract() (Regex-based extraction for metadata parsing).Schema Enforcement: cast() (standardizing types like Categorical or Int), rename(), drop().Math & Logic: round(), clip() (capping values), when().then().otherwise() (declarative conditional labeling).3. Relational & Assembly (Layer 2)Functions that power the DataAssembler for joining metadata, phenotypes, and genotypes.Joins: join() (supporting left, inner, outer, semi, and anti for filtering intersections).Concatenation: concat() (vertical/horizontal stacking of standardized datasets).Deduplication: unique() (ensuring primary key integrity during multi-source joins).4. Persistence & Optimization (The Efficiency Pillar)To address your goal of temporary storage and avoiding re-computation:sink_parquet() / write_parquet(): Best for "Checkpointing" assembled data on disk. Parquet is highly efficient for heavy datasets and preserves types.group_by().agg(): Essential for the pre-aggregation strategy to speed up UI rendering.