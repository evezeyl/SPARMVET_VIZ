## closing -> as write log, update and put ready new chat for continuing

- See closeout_template.md (only some part to eventually update)


# TEST VIRULENCE FINDER WRANGLING 

@Agent: @dasharch - New Atomic Decorator: [split_column].

1. **The Task:** Implement the `split_column` decorator in 'libs/transformer/src/data_wrangler.py'.
2. **Logic:**
   - **Tag:** `@wrangler_action("split_column")`
   - **Implementation:** - Use `lf.with_columns(pl.col(source).str.split_exact(delimiter, n=len(new_columns)-1).struct.rename_fields(new_columns).alias("fields")).unnest("fields")`.
     - If `drop_source` is True in the params, follow the split with a `.drop(source)`.
3. **Safety:** If the number of split parts doesn't match the length of `new_columns`, Polars' `split_exact` will handle it gracefully, but ensure the decorator handles missing delimiters without crashing.
4. Procede with test data and test manifest for the new decorator (same procedure as before)
5. **Registration & Docs:** Register in the 'DataWrangler' and update 'docs/guides/transformer_usage.md'.
6. **STOP:** Confirm the implementation. I will @verify before we apply this to the VIGAS_VirulenceFinder dataset.

---

@Agent: @dasharch - Integration Test: [VIGAS_VirulenceFinder].

1. **Path Discovery:** Locate the following files and confirm their existence:
   - Master Config: 'config/manifests/pipelines/VIGAS-P/VIGAS_VirulenceFinder/VIGAS_VirulenceFinder.yaml'
   - Data File: 'assets/test_data/2_VIGAS-P_ST22_dummy/test_data_VirulenceFinder_20260307_105756.tsv' 
2. **Contract Resolution:** Load the Master Config manifest file. It refers to a 'data_schema' and 'wrangling_steps'. Follow those references to load the external YAML files.
3. **Execution:** Initialize the 'DataWrangler' using the wrangling instructions from the manifest file, and run all the steps in the wrangling list.
4. **Output:** Write the resulting LazyFrame to a TSV file 'tmp/VIGAS_VirulenceFinder_CLEANED.tsv'.
5. **STOP:** Report once the TSV is ready. I will manually inspect the output to see if we need a 'Layer 2' assembler or additional cleaning steps.

# TEST TING TRANSFORMATION DECORATOR PROTOCOL 

@Agent: @dasharch - Full Decorator Re-Test (Sequential Standard).

1. **Verify Code:** Confirm 'libs/transformer/src/data_wrangler.py' now uses the `for step in manifest_list:` loop and that all decorators accept `(lf, params)`.
2. **Test all existing decorators sequentially:** 
   - Use the existing test data (unless not appropriate)
   - use the existing manifest files (verify results agains expectations that should be documented as comments in the manifest files)


# Locating inconsitencies 

@Agent: @dasharch - MANDATORY REFACTOR: List of Dictionaries Standard.

1. **The Error:** You have drifted into using a Dictionary for the 'wrangling' manifest. We previously decided on a **List of Dictionaries** to support sequential execution and duplicate actions.
2. **The Logic Fix:** Update 'libs/transformer/src/data_wrangler.py'.
   - The `run()` method must iterate over a LIST: `for step in manifest['wrangling']:`.
   - Each `step` is a dictionary containing an 'action' key and parameter keys.
3. **Decorator Standardization:** Refactor all decorators (`fill_nulls`, `unique_rows`, `keep_columns`, `strip_whitespace`) to accept `(lf, spec)` where `spec` is the dictionary of parameters from the list item.
4. **Documentation Sync:** Update 'docs/guides/transformer_usage.md' and ensure all examples use the YAML list dash `- action: ...`.
5. **STOP:** Present the refactored `run()` loop and one example decorator for my @verify.


@Agent: @dasharch - ARCHITECTURAL LOCK: Universal Sequential Actions.

1. **The Standard:** All data schema (data_schemas, metadata_schema, additional_data_schema) follow the SAME wrangling structure: A **Sequential List of Dictionaries**.
2. **Logic Update:** Ensure 'libs/transformer/src/data_wrangler.py' is context-agnostic. 
   - It should accept a LazyFrame and a List of Actions. 
   - It iterates through the List of 'action' in order.
3. **Decorator Refactor:** Ensure every decorator (`fill_nulls`, `unique_rows`, `keep_columns`, `strip_whitespace`) accepts exactly two arguments: `(lf: pl.LazyFrame, params: dict)`.
4. **Documentation:** Update 'workspace_standard.md' and 'docs/guides/transformer_usage.md'.
   - Explicitly state: "Wrangling is a sequential list of action-dictionaries. All data schemas use this same format.".
5. **STOP:** Confirm the code and docs are 100% homogeneous. Present the finalized `run()` loop for my @verify.


@Agent: @dasharch - Documentation Refinement: Registry vs. Pipeline.

1. **The Conflict:** Our docs currently confuse the USER about the usage of the 'Dictionary of available actions' with the 'List of manifest instructions'.
2. **Action:** Update 'docs/modules/wrangling.qmd' and 'workspace_standard.md'.
   - **Clarify:** The 'Registry' (in 'libs/transformer/src/data_wrangler.py') is a Dictionary for lookup efficiency.
   - **Clarify:** The 'Wrangling Pipeline' (YAML manifest) is a Sequential List to preserve logic order.
3. **Consistency Check:** Ensure all YAML examples show the list format:
   wrangling:
     - action: "action_name"
       columns: [...]
4. **STOP:** Confirm the documentation is no longer ambiguous. I will @verify the clarity before procede with re-testing decorators.

# PREPARING WRANGLING REAL DATA ...

## New decorator for wrangling Resfinder data - keep_columns


@Agent: @dasharch - Execute Sequential Verification for [keep_columns].

1. **Step A: The Contract (TSV + YAML):**
   - './libs/transformer/tests/data/keep_columns_test.tsv' and './libs/transformer/tests/data/keep_columns_manifest.yaml' have been generated and verified by the user
  
2. **Step B: Execution for [keep_columns]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/keep_columns_test.tsv --manifest ./libs/transformer/tests/data/keep_columns_manifest.yaml --output tmp/keep_columns_debug_view.tsv`.
   - correct any errors of the script and implementation of the keep_columns decorator

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/keep_columns_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

---
@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [keep_columns] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **Standard Entry Template:** For each 'keep_columns' decorator, include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
4. **STOP:** Present the documentation entry for 'keep_columns' and confirm which decorator is next.



----


@Agent: @dasharch - New Atomic Decorator: [keep_columns].

1. **The Task:** Implement a new decorator `keep_columns` in 'libs/transformer/src/data_wrangler.py'.
2. **Logic:** - **Tag:** `@wrangler_action("keep_columns")`
   - **Polars Implementation:** `return lf.select(columns)` where `columns` is the list from the manifest.
   - **Safety:** Add a check to ensure that if a column in the 'keep' list doesn't exist in the data, it raises a clear error or warning (to prevent silent failures in the pipeline).
   -**Safety:** : ensure that primary key is always kept in the data 
3. **Dispatcher Update:** Register 'keep_columns' in the DataWrangler.
4. **Documentation:** Add the entry to 'docs/guides/transformer_usage.md' using the Link-Not-Repeat rule.
5. **STOP:** Confirm the implementation. I will @verify the code before we run the Universal Runner with a new test manifest.


## Strategy update 

> reupdate 
@Agent: @dasharch - Phase Audit & Architectural Alignment.

1. **State Verification:** - Confirm that the [unique_rows] decorator is fully implemented in 'libs/transformer/src/data_wrangler.py' and registered.
   

@Agent: @dasharch - Phase Audit & Architectural Alignment.

1. **Architectural Cleanup:**
   - Ensure 'architecture_decisions.md' contains 'Staged Data Assembly'.
   - Ensure 'implementation_plan_master.md' reflects 'The Assembly Factory' (Layer 2 orchestration).
   - **Constraint Check:** Verify that the 'DataWrangler' remains Atomic (Layer 1) and does NOT contain any internal join logic for additional datasets.

3. **Documentation:**
   - Update 'docs/guides/transformer_usage.md' to include the entry for 'unique_rows' using the Link-Not-Repeat rule.
   - Add a high-level note about the upcoming Assembly Layer (Layer 2) for multi-source joins.

4. **STOP:** Present a summary of what is DONE and what is PENDING in the new Staged Pipeline model. I will @verify before we start DataAssembler.


@Agent: @dasharch - Architectural Pivot: Staged Pipeline.

1. **The Vision:** We are moving away from a single nested loop. The Wrangler must remain 'Atomic' (one input -> one cleaned output).
2. **Layer 1 (Atomic):** Ensure 'DataWrangler' and 'test_wrangler.py' are optimized to run independently on any provided dataset.
3. **Layer 2 (The Assembler):** Add a new task to 'implementation_plan_master.md' for an 'Orchestrator'.
   - This script will: 
     a) Call the Wrangler for a selection of datasets.
     b) Perform joins based on the Plot requirements.
     c) Apply a second 'Final' wrangling layer if needed.
4. **Logic Check:** Ensure the 'Universal Runner' can be easily called by this Orchestrator without code duplication.
5. **STOP:** Confirm the plan now reflects this 'Staged' approach. Do NOT write code yet.


@Agent: @dasharch - Architectural Expansion: Multi-Source Support.

1. **Rule Re-Sync:** Re-read 'workspace_standard.md' and 'architecture_decisions.md'. We are adding a 3rd category of data: 'additional_datasets'.
2. **Evaluate current manifest files** config/manifests/pipelines/1_Abromics_general_pipeline/ where this option is now implemented.
3. **Update Architecture:** Add 'ADR 009: Multi-Source Ingestion' to 'architecture_decisions.md'.
   - Rule: Additional datasets must share the same 'wrangling' decorator logic as core data and metadata.
   - Rule: Joins must be explicitly defined by a 'join_on' key in the manifest, 
   Per `join_on` is column defined as primary key in the manifest with : `is_primary_key: true`.
4. **Update Master Plan:** Augment 'implementation_plan_master.md' to include the 'Joiner' phase.
5. **Logic Check:** Review 'libs/transformer/src/data_wrangler.py'. 
   - Ensure the 'DataWrangler' can loop through a list of datasets, apply rules to each. Report if the joining of LazyFrames has been implemented or if it is pending. 
6. **STOP:** Confirm the plan is updated and the logic is sound. Do NOT write code yet. I will @verify the architectural shift first.

# 10  Step by step building and user control  - unique_rows


@Agent: @dasharch - Phase 1: Core Implementation of [unique_rows].

1. **Naming Update:** We have decided to use the name 'unique_rows' instead of 'drop_row_duplicates' for better clarity. I have updated the tasks.md accordingly.
2. **Core Task:** Implement the `unique_rows` decorator in 'libs/transformer/src/data_wrangler.py'.
   - **Decorator Tag:** `@wrangler_action("unique_rows")`
   - **Logic:** `lf.unique(subset=None, maintain_order=True)`.
3. **Dispatcher Update:** Ensure 'unique_rows' is added to the DataWrangler's supported actions.

---

@Agent: @dasharch - Execute Sequential Verification for [unique_rows].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/unique_rows_test.tsv' with meaningful bacterial metadata, including duplicate rows.
   - Generate './libs/transformer/tests/data/unique_rows_manifest.yaml' defining the unique_rows logic.
   - **HALT:** "Contract for [unique_rows] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [unique_rows]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/unique_rows_test.tsv --manifest ./libs/transformer/tests/data/unique_rows_manifest.yaml --output tmp/unique_rows_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/unique_rows_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

---


# 9  Step by step building and user control  - derive_categories

@Agent: @dasharch - Execute Sequential Verification for [derive_categories].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/derive_categories_test.tsv' with meaningful bacterial metadata to test the derive_categories decorator.
   - Generate './libs/transformer/tests/data/derive_categories_manifest.yaml' defining the derive_categories logic.
   - **HALT:** "Contract for [derive_categories] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [derive_categories]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/derive_categories_test.tsv --manifest ./libs/transformer/tests/data/derive_categories_manifest.yaml --output tmp/derive_categories_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/derive_categories_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

---
@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [derive_categories] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **Standard Entry Template:** For each 'derive_categories' decorator, include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
4. **STOP:** Present the documentation entry for 'derive_categories' and confirm which decorator is next.


# 8  Step by step building and user control  - split_and_explode

@Agent: @dasharch - Execute Sequential Verification for [split_and_explode].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/split_and_explode_test.tsv' with meaningful bacterial metadata to test the split_and_explode decorator.
   - Generate './libs/transformer/tests/data/split_and_explode_manifest.yaml' defining the split_and_explode logic.
   - **HALT:** "Contract for [split_and_explode] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [split_and_explode]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/split_and_explode_test.tsv --manifest ./libs/transformer/tests/data/split_and_explode_manifest.yaml --output tmp/split_and_explode_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/split_and_explode_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

---

@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [split_and_explode] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **Standard Entry Template:** For each 'split_and_explode' decorator, include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
4. **STOP:** Present the documentation entry for 'split_and_explode' and confirm which decorator is next.

# 7. Step by step building and user control  - summarize

@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [summarize] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **Standard Entry Template:** For each 'summarize' decorator, include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
4. **STOP:** Present the documentation entry for 'summarize' and confirm which decorator is next.

> Modified by EVE
@Agent: @dasharch - Execute Sequential Verification for [summarize].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/summarize_test.tsv' with meaningful bacterial metadata. Ensure that there are repeated values in the columns to be summarized.
   - Generate './libs/transformer/tests/data/summarize_manifest.yaml' defining the summarize logic.
   - **HALT:** "Contract for [summarize] is ready. Please verify the TSV and YAML. Waiting for @verify."

@Agent: @dasharch - Manual Contract Update: [summarize] Decorator.

1. **User Override:** I have manually modified the following files:
   - './libs/transformer/tests/data/summarize_test.tsv'
   - './libs/transformer/tests/data/summarize_manifest.yaml'
2. **Re-Sync Requirement:** Do NOT regenerate these files. Read them immediately to understand the updated test case and the new 'summarize' logic I've defined.
3. **Step B: Execution for [summarize]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/summarize_test.tsv --manifest ./libs/transformer/tests/data/summarize_manifest.yaml --output tmp/summarize_debug_view.tsv`.
4. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/summarize_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

-> need to adapt the guardrails rules 

@Agent: @dasharch - Execute @sync for [summarize].

1. **Internalize Rules:** Re-read 'workspace_standard.md' (Section 6: Logic Conflict Guardrail). I have manually updated these rules to include @verify and @sync triggers.
2. **Current State:** I am issuing a **@sync** command for the current 'summarize' discrepancy.
3. **Action (The Sync):** Update './libs/transformer/tests/data/summarize_manifest.yaml' to use the SUM logic for resistance genes as per our previous discussion.
4. **Execution (Step B):** Immediately run the Universal Runner:
   `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/summarize_test.tsv --manifest ./libs/transformer/tests/data/summarize_manifest.yaml --output tmp/USER_debug_view.tsv`.
5. **Step C: Evidence:**
   - Print `df.glimpse()` to the terminal.
   - Ensure 'tmp/USER_debug_view.tsv' reflects the SUM results.
6. **STOP:** Confirm the manifest is synced and present the output.

# 6. Step by step building and user control  - drop_duplicates

@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [drop_duplicates] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **The Universal Testing Command:** Document the standard execution path:
   `.venv/bin/python libs/transformer/tests/test_wrangler.py --data [INPUT_FILE] --manifest [YAML_FILE] --output tmp/USER_debug_view.tsv`
4. **Standard Entry Template:** For each tested decorator (starting with 'drop_duplicates'), include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
5. **Logic Guardrail (I/O):**
   - **Input:** Flexible (CSV or TSV supported).
   - **Output:** MUST be TSV. Ensure 'test_wrangler.py' uses `include_header=True, separator="\t"` for the final write.
6. **STOP:** Present the documentation entry for 'drop_duplicates' and confirm which decorator is next.

@Agent: @dasharch - Execute Sequential Verification for [drop_duplicates].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/drop_duplicates_test.tsv' with meaningful bacterial metadata (include nulls in numeric and categorical columns).
   - Generate './libs/transformer/tests/data/drop_duplicates_manifest.yaml' defining the drop_duplicates logic.
   - **HALT:** "Contract for [drop_duplicates] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [drop_duplicates]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/drop_duplicates_test.tsv --manifest ./libs/transformer/tests/data/drop_duplicates_manifest.yaml --output tmp/drop_duplicates_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/drop_duplicates_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

# 5. Step by step building and user control  - rename

@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [rename] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **The Universal Testing Command:** Document the standard execution path:
   `.venv/bin/python libs/transformer/tests/test_wrangler.py --data [INPUT_FILE] --manifest [YAML_FILE] --output tmp/USER_debug_view.tsv`
4. **Standard Entry Template:** For each tested decorator (starting with 'rename'), include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
5. **Logic Guardrail (I/O):**
   - **Input:** Flexible (CSV or TSV supported).
   - **Output:** MUST be TSV. Ensure 'test_wrangler.py' uses `include_header=True, separator="\t"` for the final write.
6. **STOP:** Present the documentation entry for 'rename' and confirm which decorator is next.

@Agent: @dasharch - Execute Sequential Verification for [rename].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/rename_test.tsv' with meaningful bacterial metadata (include nulls in numeric and categorical columns).
   - Generate './libs/transformer/tests/data/rename_manifest.yaml' defining the rename logic.
   - **HALT:** "Contract for [rename] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [rename]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/rename_test.tsv --manifest ./libs/transformer/tests/data/rename_manifest.yaml --output tmp/rename_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/rename_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."


# 4. Step by step building and user control  - replace_values


@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [replace_values] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **The Universal Testing Command:** Document the standard execution path:
   `.venv/bin/python libs/transformer/tests/test_wrangler.py --data [INPUT_FILE] --manifest [YAML_FILE] --output tmp/USER_debug_view.tsv`
4. **Standard Entry Template:** For each tested decorator (starting with 'replace_values'), include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
5. **Logic Guardrail (I/O):**
   - **Input:** Flexible (CSV or TSV supported).
   - **Output:** MUST be TSV. Ensure 'test_wrangler.py' uses `include_header=True, separator="\t"` for the final write.
6. **STOP:** Present the documentation entry for 'replace_values' and confirm which decorator is next.

---

@Agent: @dasharch - Execute Sequential Verification for [replace_values].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/replace_values_test.tsv' with meaningful bacterial metadata (include nulls in numeric and categorical columns).
   - Generate './libs/transformer/tests/data/replace_values_manifest.yaml' defining the replace logic.
   - **HALT:** "Contract for [replace_values] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [replace_values]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/replace_values_test.tsv --manifest ./libs/transformer/tests/data/replace_values_manifest.yaml --output tmp/replace_values_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/replace_values_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

# 3. Step by step building and user control  - drop_nulls

@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [drop_nulls] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **The Universal Testing Command:** Document the standard execution path:
   `.venv/bin/python libs/transformer/tests/test_wrangler.py --data [INPUT_FILE] --manifest [YAML_FILE] --output tmp/USER_debug_view.tsv`
4. **Standard Entry Template:** For each tested decorator (starting with 'drop_nulls'), include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
5. **Logic Guardrail (I/O):**
   - **Input:** Flexible (CSV or TSV supported).
   - **Output:** MUST be TSV. Ensure 'test_wrangler.py' uses `include_header=True, separator="\t"` for the final write.
6. **STOP:** Present the documentation entry for 'drop_nulls' and confirm which decorator is next.



--- 

@Agent: @dasharch - Execute Sequential Verification for [drop_nulls].

1. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/drop_nulls_test.tsv' with meaningful bacterial metadata (include nulls in numeric and categorical columns).
   - Generate './libs/transformer/tests/data/drop_nulls_manifest.yaml' defining the drop logic.
   - **HALT:** "Contract for [drop_nulls] is ready. Please verify the TSV and YAML. Waiting for @verify."

2. **Step B: Execution for [drop_nulls]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/drop_nulls_test.tsv --manifest ./libs/transformer/tests/data/drop_nulls_manifest.yaml --output tmp/drop_nulls_debug_view.tsv`.

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/drop_nulls_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."






# 2. Step by step building and user control  - FILL NULLS



---


@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify ok. Mark [fill_nulls] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **The Universal Testing Command:** Document the standard execution path:
   `.venv/bin/python libs/transformer/tests/test_wrangler.py --data [INPUT_FILE] --manifest [YAML_FILE] --output tmp/USER_debug_view.tsv`
4. **Standard Entry Template:** For each tested decorator (starting with 'fill_nulls'), include:
   - **Description:** A clear functional summary.
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
5. **Logic Guardrail (I/O):**
   - **Input:** Flexible (CSV or TSV supported).
   - **Output:** MUST be TSV. Ensure 'test_wrangler.py' uses `include_header=True, separator="\t"` for the final write.
6. **STOP:** Present the documentation entry for 'fill_nulls' and confirm which decorator is next.



--- 

@Agent: @dasharch - Execute Phase 1: Sequential Verification for [fill_nulls].

1. **Context & Rules Sync:**
   - Read './agents/rules/workspace_standard.md' and './agents/workflows/verification_protocol.md'.
   - Confirm active root .venv and TSV/CLI-Argparse standards.

2. **Step A: The Contract (TSV + YAML):**
   - Generate './libs/transformer/tests/data/fill_nulls_test.tsv' with meaningful bacterial metadata (include nulls in numeric and categorical columns).
   - Generate './libs/transformer/tests/data/fill_nulls_manifest.yaml' defining the fill logic.
   - **HALT:** "Contract for [fill_nulls] is ready. Please verify the TSV and YAML. Waiting for @verify."

--- 

@Agent: @dasharch - Universal Runner Implementation and execution for [fill_nulls]

1. **Step A: The Universal Runner (test_wrangler.py):**
   - Refactor './libs/transformer/tests/test_wrangler.py' to be entirely generic.
   - **Logic:** It must load any `--data` (.tsv) and any `--manifest` (.yaml), then use the `DataWrangler.apply_wrangling_rules()` to process the data.
   - **CLI:** Strictly maintain `argparse` for --data, --manifest, and --output.

2. **Step B: Execution for [fill_nulls]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/fill_nulls_test.tsv --manifest ./libs/transformer/tests/data/fill_nulls_manifest.yaml --output tmp/fill_nulls_debug_view.tsv`.
3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/fill_nulls_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."


# Step by step building and user control 
- implemented workflow rule for one step at the time
- instructions that dasharch must respect the user testing protocol 

# 1. Recheck completness and consistency with a thinking model
--- 


- [x] Recheck completness and consistency with a thinking model
> for this used planning and high model 

@Agent: @dasharch - Full Project & Documentation Congruence Audit (The "Zero-Debt" Scan).
1. Read : `./.claude/rules/workspace_standard.md` and `./.claude/workflows/verification_protocol.md`
2. **The Vision-Reality Audit:** Use a deep-thinking model to cross-reference our 'Planned Logic' against our 'Current Implementation'.
   - **Plans:** `./.claude/plans/implementation_plan_master.md`, `./.claude/knowledge/architecture_decisions.md`, and `./.claude/tasks/tasks.md`.
   - **Implementation:** All files in `./libs/`, `./app/`, `./assets/`, and `./config/`.
   - **Documentation:** All files in `./docs/`.

3. **Global Search for "Legacy Contaminants":** Scan every file in the repository for:
   - **Format Drift:** References to `.csv` or `sep=","` (must be updated to `.tsv` and `sep="\t"`, `.json`  instead of `.yaml`).
   - **CLI Compliance:** Any Python script in `src/` or `tests/` lacking `argparse` support (must support manual execution).
   - **Pathing Errors:** Hardcoded absolute paths (e.g., `/Users/...`) or incorrect relative links in `pyproject.toml` files.

4. **Detection Points for Inconsistency:**
   - **Protocol Mismatch:** Does the Master Plan or docs omit the 'v1.6 Verification Protocol' (TSV + CLI + @verify)?
   - **Dead Tasks:** Are there [TODO] tasks in `tasks.md` that contradict current `blockers.md` or `milestones.md`?
   - **Metadata Sync:** Does the test data in `assets/` match the schemas defined in the `knowledge/` ADRs?

5. **Actionable Report (The Debt List):**
   - List every 'Incongruent File' found.
   - For each item, provide a one-line 'Proposed Reconciliation' (e.g., "Update docs/README.md to reflect TSV standard").
   - **DO NOT APPLY FIXES YET.**

6. **STOP:** Present this Audit Report and wait for my @verify to begin the cleanup or switch to the fast execution model.

---
- [x] Need to merge the paths and force it to use one source of truth


@Agent: @dasharch - Execute Knowledge Audit & Rule Formalization.

1. **Audit Knowledge Directory:** Scan all Markdown files in `./.claude/knowledge/`.
2. **Define Usage Rules:** For each file found, determine its unique role in our workflow (e.g., ADRs, long-term memory, technical constraints).
3. **Update Workspace Standard:** 
   - Edit './agents/rules/workspace_standard.md' to include the 'Logic Source of Truth' section.
   - List each path with a short description of its content AND a specific 'Rule of Usage' (e.g., 'Check this file before every new implementation').
4. **Clean & Consolidate:** 
   - If any information is duplicated between files, consolidate it into the most logical human-readable file.
   - Delete any empty or redundant sub-directories in `./.claude/knowledge/`.
5. **STOP:** Present the new 'Logic Source of Truth' table from the workspace standard and confirm your commitment to using these files consistently.



@Agent: @dasharch - Permanent Path Authority Lock.

1. **Acknowledge Current Tree:** Note the existing structure in ./.claude/. This is now the ONLY authorized pathing schema.
2. **Consolidation Finalization:**
   - Use `./.claude/tasks/tasks.md` as the sole source of truth for execution.
   - Use `./.claude/plans/implementation_plan_master.md` as the sole roadmap.
   - Delete `./.claude/tasks/initialization_task.md` once its contents are merged into the main `tasks.md`.
   - homogenize usage of each required artifact, log and knowledge files
3. **Update Workspace Standard:** Ensure ./.claude/rules/workspace_standard.md reflects these exact paths and forbids the creation of any new top-level folders in ./.claude/.




--- 

- [x] Need to merge implementation plans 

@Agent: @dasharch - ARCHITECTURAL CONSOLIDATION REQUIRED.

1. **The Goal:** Merge `implementation_plan_current.md`, `implementation_plan_restoration.md`, and `implementation_plan_v2.md` into ONE file: `./.claude/plans/implementation_plan_master.md`.
2. **Priority Logic:**
   - Favor **v2** for high-level architecture.
   - Favor the **restoration** plan for the root .venv and modular lib setup.
   - **MANDATORY:** Include the v1.6 Verification Protocol (TSV-default, CLI-argparse for all tests, and @verify gates).
3. **Conflict Resolution:** If you find contradictory instructions between the three plans, you MUST stop and ask me for clarification. Do not guess.
4. **Cleanup:** Once the 'master' plan is verified by me, delete the 3 old versions to prevent future logic drift.
5. **Instruction Update:** Update 'workspace_standard.md' to reflect that `implementation_plan_master.md` is now the ONLY authoritative roadmap.
6. **STOP:** Present the table of contents and the 'Verification Rules' section of the new Master Plan for my review.
---

- [x] Need to ensure it keep the argparse and allow me to run the tests on the python  -> rule added