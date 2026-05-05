
## Viz factory startup thinking process

I want to initiate the viz_factory build (previous agent has done some work but I am usure if it follows the rules and the standards I want). The rules will be similar to the building of the transformer with its decorators.

Where we need to use actions adding plots and their different layers to the manifest. We will be able to do default plots manifests so they can be reused. Easily (aka plots template manifests)

So the process should be verify simpliar and follow the same logic (and building way) that we have used for the transformer.

We will need to have a way to have the "data agnostic mapping" of data to plots (eg what is x, what is y , what is grouping layer for fill, for symbol osv)  - and this will need to be defined in the manifest 

Note also that we will need at one point an plot update: and this part is tricky, we will need to implement a way to update the data that is passed to the plot -> send a message to the transformer -> update the data -> send a message to the plot -> update the plot (because eg we will want to be able to do data exploration -> reactualize the plot). And here I think we will need a way to mark the data as unmodified Vs filtered ... so we can go back to the unmodified data/plot if needed. 

What we have to determine is exactly what to build and how to build it. 
We will have the possibility to do several plots per manifest (so we need to think a bit how to handle this best).
We need to determine what is registred as list or dictionary in the manifest

I think that A plot should be a list of layers, and each layer is a dictionary of parameters for the layer (so we need to think a bit how to handle this best).

I think maybe the plots names itself should be a dictionary (we have a set of plots names that we can use.) Because when we will have to create the UI for the shiny app, we will want to offer the possibility to select a plot name and then the UI will have to display the selected plot (so we need to think a bit how to handle this best).

For the organisation of the viz factory code, I suggest that there is one subdirectory for each layer type (so we need to identify the types of layers that are used in plotnine - I now in R you have different layers - eg. scales, plots types, themes, coordinates, etc.)

And we will need a good way to handle the aesthetics, eg changing the color theme, the fill, the symbol, using different color palettes, etc. (I am not sure if this should be consider within a layer or as an utiliy ...) ... 

We will need plots defaults ... box plots, histograms, etc. for each type of data (e.g. continuous, categorical, etc.)



## Pro project implementation 


@Agent: @dasharch - GLOBAL AESTHETIC POLISH & LIBRARY STANDARDS (Pass 3).

1. Global CSS/SCSS Refinement:
   - Update the Quarto theme (SCSS) to fix the inline code background across the ENTIRE documentation.
   - Requirement: Switch from dark/unreadable to the same gray that is used in the code blocks.

2. Preface & Mermaid Recovery:
   - Extract the 'sequenceDiagram' from index.qmd and create ./docs/foundations/_sequence_data_flow.mmd.
   - Re-import it into index.qmd using '{{< include _sequence_data_flow.mmd >}}'.
   - Apply the high-contrast %%{init}%% header to this and all other .mmd files (fontSize: 20px, thicker lines).
   - Wrap all large diagrams in '::: {.lightbox}' for zoom functionality.

3. Module Sync & "Violet" Naming Law:
   - Audit workflows/transformation.qmd: Ensure 'wrangle_debug.py' is documented here as the Layer transformation (wrangling) runner.
   - Standardize Component Naming: Use the 'Violet Component' format [e.g., DataWrangler (data_wrangler.py)] for:
     - The Transformer components (DataWrangler, DataAssembler).
     - The Registry logic (ActionRegistry).
   - Update ./.claude/rules/workspace_standard.md to codify this as the "Component Reference Standard".

4. Library README Architecture:
   - For every library in ./libs/ (transformer, generator_utils, viz_factory, etc.):
     - Create or augment a README.md.
     - Content must include: Purpose, Key Components (Violet Standard), I/O summary, and how to run 'Editable Mode' installation.
   - Add a rule to ./.claude/rules/workspace_standard.md: "Every internal library MUST contain a README.md detailing its specific implementation and local CLI runners."

5. Cleanup & Appendix Audit:
   - Resolve footnote [^1] in the Preface.
   - Remove the empty c4_model.qmd.
   - Audit 'appendix/out_of_the_box_configuration.qmd': If empty or legacy, either write the YAML specs or delete it.



## Global audit 


> 4th round 
@Agent: @dasharch - RECOVERY: FINAL DOCS RESTRUCTURE & MERMAID SYNC.

1. Mermaid Local-Path Sync (Logic Layer):
   - For every .qmd file that imports a mermaid file:
     - Update the '{{< include ... >}}' or '{{< mermaid ... >}}' tags.
     - Use STRICT local relative paths (e.g., if both are in ./docs/workflows/, use '{{< include _mermaid.mmd >}}').
     - Remove all legacy paths pointing to /guide/ or /modules/.

2. Theme Injection (Distrobox Readiness):
   - Open every _mermaid.mmd file.
   - Prepend if not already present the Mermaid initialization header: %%{init: {'theme': 'base', 'themeVariables': { 'primaryColor': '#007bff' }}}%% (or match the project theme).
   - Ensure the .mmd files are self-contained and render correctly in a standalone Mermaid viewer.

3. Quarto Master Sync (_quarto.yml):
   - Ensure 'appendix/Shiny_flavors.qmd' is added to the Appendix section.
   - Perform an 'Orphan Check': Ensure every .qmd in the subdirectories is listed in the sidebar.

4. HALT for @verify:
   - Provide the updated _quarto.yml content.
   - Confirm the location of '_mermaid.mmd' for the main 'Transformer' workflow.

> 3d round 


@Agent: @dasharch - PHYSICAL DOCS RESTRUCTURE & PATH SYNC.

1. Directory Creation:
   - Create the following directories if they do not exist:
     - ./docs/foundations/ [files under part: "[Foundations] in _quarto.yml"] 
     - ./docs/workflows/ [files under part: "[Workflows] in _quarto.yml"] 
     - ./docs/reference/ [files under part: "[Reference] in _quarto.yml"] 
     - ./docs/appendix/ [files under part: "[Technical Appendix] in _quarto.yml"] 

2. Physical Migration (Git-Aware):
   - Use 'git mv' to move every .qmd file from its current location (using _quarto.yml as a reference) to the folder corresponding to its Part in the _quarto.yml structure.
   - Ensure the root ./docs/index.qmd stays in the root for Quarto entry.

3. Path Reconciliation (_quarto.yml):
   - Update the _quarto.yml file to reflect the NEW relative paths (e.g.,     - guide/user_preferences.qmd should become  workflow/user_preferences.qmd, follwoing current _quarto.yml structure).
   - Double-check: Ensure every file mentioned in the 'Master Journey' now has a correct, existing path.

5. HALT for @verify:
   - Provide a 'Migration Log' showing the Old Path -> New Path.
   - Confirm that 'quarto render' (or a dry run) shows no missing file errors.


> second round 
@Agent: @dasharch - DEEP SEMANTIC AUDIT & STRUCTURAL RECONCILIATION (Pass 2).

1. Comprehensive Source Scan (Strict Scope):
   - Perform a thorough content analysis of EVERY .qmd file within:
     - ./docs/appendix/
     - ./docs/architecture/
     - ./docs/cheatsheets/
     - ./docs/guide/
     - ./docs/modules/
     - Root-level files (index.qmd, etc.) and _quarto.yml.
   - EXCLUSION: Skip ./docs/_book/ and ./docs/.quarto/ to preserve tokens.

2. Identification of 'Logic Debt' & 'Shadow Processes':
   - Trace the 'Clean-then-Cast' (String-to-Categorical) and 'SDK Stage A-D' logic through every folder.
   - Flag 'Shadow Processes': Mentions of old script names (like 'test_') or manual steps that the SDK now automates.
   - Verify that the 'Ambiguity Rule' and 'Boundary Protection' are documented in both the Technical and User guides.

3. Structural Reorganization & Orphans Check:
   - Suggest a high-level grouping for _quarto.yml that eliminates 'file scatter.'
   - RECONCILIATION: Compare the proposed tree against the file system. Identify any .qmd files currently NOT referenced in _quarto.yml (Orphans).
   - Propose a 'User Journey' hierarchy:
     - [Foundations]: ADRs, Tidy Data, Manifest Philosophy.
     - [Workflows]: SDK Scaffolding, Fuzzy Reconciler, Transformer Logic.
     - [Reference]: Cheat Sheets, Naming Rules, Technical Appendix.

4. Mermaid & Aesthetic Strategy:
   - Identify every diagram that is outdated, low-contrast, or structurally messy.
   - Propose a CSS/Theme variable strategy for Mermaid to ensure professional rendering in the final build.

5. Deliverable - The 'Audit Matrix':
   - Provide a table: [File Path] | [Current Status] | [Logic Conflict/Orphan Status] | [Proposed Action].
   - Provide the new suggested _quarto.yml structure.

HALT: Do not edit files. I will review this 'Deep Audit Matrix' before we commit to the refactor.

--- 

@Agent: @dasharch - GLOBAL SOURCE AUDIT & REORGANIZATION PLAN.

1. Source-Only Scan:
   - Perform a full audit of all SOURCE files in ./.claude/, ./.claude/, and the .qmd files in ./docs/.
   - STRICT EXCLUSION: Do not scan ./docs/_book/, ./docs/.quarto/, or any other build/cache directories.

2. Consistency Check:
   - Compare the current code implementation (Ingestion, Transformers with its Decorators, SDK) against the written documentation.
   - Identify 'Semantic Drift': Where names, rules, or logic in the docs no longer match the code (e.g., deprecated script names, old naming conventions).
   - Ensure semantic homogeneity across the codebase and documentation. Add rules and conventions if necessary.

3. Proposed Reorganization (The 'User Journey'):
   - Based on the content you find, suggest an improved structure for _quarto.yml. 
   - Consider grouping by: 
     - Foundations (Tidy Data, ADRs)
     - Core Engine (Ingestion, Transformer with its Decorators, Casting Logic)
     - Project Scaffolding (SDK, Reconciler)
     - Appendices (Technical deep-dives).
   - Propose where to merge overlapping files to eliminate code/logic duplication.

4. Mermaid & Visuals Assessment:
   - Identify which diagrams are outdated (update those) or illegible (update those).
   - Suggest a styling strategy for Mermaid to ensure clarity and high-contrast rendering and proper rendering in the final quarto build.

5. Deliverable:
   - Do NOT edit the files yet. 
   - Provide a 'Structural Audit & Reorganization Plan'. This plan should list the proposed table of contents and a summary of 'Truth Discrepancies' that need fixing.

HALT: I will review your plan before you begin the rewriting/refactoring process.







## SDK Documentation
---

@Agent: @dasharch - DOCUMENTATION CONSOLIDATION: SDK & RECONCILER.

1. Update User Documentation (./docs/modules/generator_utils.qmd): for the new SDK layer. Do not include the viz_factory update because you started development on your own to test the generator_utils layer. viz_factory is not part of the SDK and and is not yet approved for use.
   - Add Section: "Relational Reconciliation (Stage D)".
   - Explain the 'Short-to-Long' key matching strategy (Metadata Anchors vs. Noisy Filenames).
   - Document the 'Match_Type' labels: EXACT, FUZZY, AMBIGUOUS, and ORPHAN.
   - Explain the 'Boundary Protection' rule (e.g., why 'x100w2' must not match 'x100w20').

2. Update Debugging Guide (./docs/guide/debugging_pipelines.qmd):
   - Add instructions for using 'debug_reconciler.py' and 'debug_ambiguity.py'.
   - List the mandatory TSV outputs in /tmp/reconciler/ and what they represent (conflicts.tsv, orphans_target.tsv).

3. Update Internal Rules (./.claude/rules/workspace_standard.md):
   - Section 8 (Naming): Formally codify the 'debug_' prefix for interactive CLI tools that materialize TSV evidence.
   - Section 12 (Data Integrity): Add the 'Ambiguity Check' requirement: "Any fuzzy join must be audited for AMBIGUOUS matches where one reference ID maps to multiple target IDs."

4. Update Combat Log (./.claude/knowledge/project_conventions.md):
   - Summarize the 'Reconciler Workflow': 
     Scan -> Intersection Analysis -> Regex Generation -> Boundary Check -> TSV Materialization.

5. HALT for @verify:
   - Confirm all cross-references are active. 
   - Provide a final 'State of the SDK' summary including all 4 modules (Extractor, Bootstrapper, Synthesizer, Reconciler).

---
Fuzzy matching for columns

@Agent: @dasharch - IMPLEMENT RELATIONAL KEY RECONCILER (SDK Phase 7).

1. New Module: ./libs/generator_utils/src/reconciler.py
   - Goal: Identify cleaning patterns (regex) to align mismatched Primary/Secondary keys.
   - Logic (Sub-string Intersection): 
     - Detect cases where 'Short Keys' (e.g., Metadata IDs) are contained within 'Long/Noisy Keys' (e.g., Fastq filenames).
     - Calculate the 'Intersection Score' (Percentage of matches found via substring vs. exact).
   - Regex Generation: 
     - Automatically suggest a 'regex_extract' pattern that isolates the anchor key from the noisy string.
     - Example: If 'Sample_01' is found in 'Sample_01_L001_R1.tsv', suggest r'(Sample_\d+)'.

2. Support for Multi-Key Joins:
   - Allow the reconciler to handle Primary, Secondary, and Tertiary keys simultaneously [ADR-009].
   - Ensure it can propose different cleaning patterns for different keys within the same dataset.

3. Iterative CLI Runner (argparse):
   - Create ./libs/generator_utils/tests/test_reconciler.py.
   - Arguments: 
     - --ref [path to reference tsv] --target [path to noisy tsv]
     - --keys [comma-separated key names]
     - --mode [exact|fuzzy]
   - Output: A 'Reconciliation Report' showing:
     - Original Match % vs. Predicted Match % after suggested regex.
     - A preview table: [Original Long Key] -> [Extracted Key] -> [Reference Match].

4. Manifest Integration:
   - The script must be able to update the 'wrangling' block of the target manifest with the suggested regex [ADR-013].

5. HALT for @verify:
   - Demonstrate the Reconciler - create test following testing protocol. 
   - Print the suggested regex and the resulting match percentage.




---


@Agent: @dasharch - SDK LOGIC MIGRATION (Phase 7).

1. Script Inspection:
   - Read all .py scripts in ./assets/scripts/.
   - Analyze the logic for:
     - Excel sheet extraction (XLSX -> TSV).
     - Automated manifest template generation (note deprecated template - use latest conventions).
     - Synthetic data creation (identifying PKs and categorical levels, generating test data with ommission of some values/missing value generations, wrong keys, etc).

2. Implementation - Stage A: extractor.py:
   - Port the Excel-to-TSV logic into ./libs/generator_utils/src/extractor.py.
   - Requirement: Support a 'Project Basename' approach where a folder is created matching the Excel filename [ADR-013].

3. Implementation - Stage B: bootstrapper.py:
   - Port the manifest inference logic into ./libs/generator_utils/src/bootstrapper.py.
   - Requirement: Automatically generate the 3-block YAML structure (input_fields, wrangling, output_fields, assembly logic, plotting logic - that will soon be implemented) for each TSV [ADR-013].
   - you can use the existing .config/manifest/pipeline folder, to determine the structure and implementation of a complex manifest (note plotting logit will be implemented following the same process as for wrangling and assembly logic)

   - Logic: Detect 'String' vs 'Float' and suggest 'Categorical' for low-cardinality text columns [Section 12].

4. Implementation - Stage C: aqua_synthesizer.py:
   - Port the fake data logic into ./libs/generator_utils/src/aqua_synthesizer.py.
   - FIX: Implement 'Relational Anchoring'. It MUST create a shared pool of Primary Keys to ensure metadata and analytical tables (like ResFinder) can be joined successfully.

5. Verification Protocol:
   - Create a minimal CLI runner ./libs/generator_utils/tests/test_sdk.py that executes A -> B -> C in one flow.
   - HALT: Generate a 'Sample Project' and provide a df.glimpse() of the joined synthetic data to prove the PK mismatch bug is fixed.



--- 


Ok, now we come back to the scripts development. Do not produce any prompt, we need to discuss and plan. 
I did not want to clean all the scripts in assests, some scripts are helpers to build manifests. 

They cover: 
- parsing tables from xlsx files containing multiple sheets into tsv files (into a common directory) 
- creating template manifest files from those (from the directory or from a single separated file - different scripts) 
- creating test data from true data (getting list of values from categorical columns, and ranges for numeric columns) and using those to create test data (including eg ommission of some values/missing value generations, wrong keys, etc)


So I think we should improve this process to really have a suite that would help the user to create manifests and test data. Right now its a bit combersom to use. 


Maybe we could eventually (maybe not now but later) plan a gui to help do this, including planning the wrangling, joining and plotting steps, and the user also eg select the decorators and preview the results, step by step (so we need to consider how to structure this in order to let this possibility open for the future)

Any good ideas on how to do this?  We need at least to improve the current process, also I think it was some bug in the script because the primary keys were not matching between the different datasets (we need to have option to match completly, including when some values are repeated - eg long format) but also the option to create some mistmatch (aqua generating a nice test suite for our app)


---

@Agent: @dasharch - INITIALIZE GENERATOR SDK (Phase 7).

1. Library Creation (ADR-011):
   - Create the directory ./libs/generator_utils/src/ and ./libs/generator_utils/tests/.
   - Initialize a pyproject.toml in ./libs/generator_utils/ following the monorepo standard [ADR 011].
   - Ensure it is installed in 'Editable Mode' in the root .venv.

2. Module Scaffolding (Headless Engine):
   Create the following empty modules in ./libs/generator_utils/src/:
   - extractor.py: Logic for xlsx -> tsv normalization.
   - bootstrapper.py: Logic for manifest YAML inference (input/output_fields).
   - aqua_synthesizer.py: Logic for Relational Test Data generation (PK Anchoring).

3. Strategic Rule Update:
   - Update ./.claude/rules/workspace_standard.md (Section 13).
   - Add: "The Generator SDK (libs/generator_utils) is the sole authorized engine for scaffolding new projects and generating synthetic test data. It must remain UI-agnostic to support future Shiny/GUI integration."

4. Feature Roadmap Entry:
   - Update ./.claude/plans/implementation_plan_master.md.
   - Add 'Phase 7: Visual Pipeline Builder (SDK)' to the roadmap.
   - Note the 'Aqua Suite' as the solution for the PK Mismatch blocker.

5. HALT:
   - Confirm the library is recognized by 'pip list' and the directory structure is ready for logic migration.

- 

## Improving helper scripts and doc

@Agent: @dasharch - USER-FRIENDLY MANIFEST CHEATSHEET.

1. Update Documentation (./docs/guide/new_data_contract.qmd):
   - Replace or insert the "Data Type Selection Guide".
   - Create a clean Markdown table with these specific columns: [Type | What it is (with example) | When to use it].

2. Table Content Requirements (Non-Technical Language):
   - string: "Plain text. (Example: 'Sample_01', 'Escherichia coli')." | "Use this for names or IDs that need cleaning (removing spaces or fixing typos) before the final output."
   - categorical: "Grouped categories. (Example: 'ST22', 'High Resistance')." | "Use for all labels, species, or gene names. It makes joining datasets faster and ensures plots look correct."
   - integer: "Whole numbers. (Example: 42, 100)." | "Use for counts or IDs that don't have decimals."
   - float: "Numbers with decimals. (Example: 98.5, 0.001)." | "Use for percentages, identity scores, or measurements."
   - boolean: "Yes/No toggle. (Example: True, False)." | "Use for presence/absence of a gene or a simple 'Pass/Fail' status."

3. Operational Note:
   - Add a mandatory note below the table: "Important Order: If you need to clean a name (String), do it in the 'wrangling' block first. Then, set it to 'categorical' in the 'output_fields' to lock it in for the dashboard." [Section 12].

4. Mirroring:
   - Sync this simplified table to ./.claude/knowledge/project_conventions.md for quick AI reference [Section 15].

5. HALT: 
   - Print the table and confirm that all legacy technical jargon (like 'Int64' or 'character') has been moved to the technical appendix, leaving this guide simple for the user.


---


@Agent: @dasharch - SESSION MILESTONE AUDIT & LOGGING.

1. Final Verification:
   - Run the ./libs/transformer/tests/test_decorator_suite.py one last time.
   - Confirm all 'Clean-then-Cast' logic passes for Categorical types [ADR-013].

2. Update Audit Log (./.claude/logs/audit_{{YYYY-MM-DD}}.md):
   - Document the migration of test runners (test_wrangler.py -> wrangler_debug.py) [ADR-005, 016].
   - Document the new 1:1:1 Naming Law for decorators [Section 8].
   - Document the Categorical vs. String "Order of Operations" standard [Section 12].

3. Documentation Finalization:
   - Confirm cross-references exist between:
     - ./docs/guide/new_data_contract.qmd
     - ./docs/modules/wrangling.qmd
     - ./docs/appendix/data_types_philosophy.qmd

4. HALT: 
   - Confirm all .claude/ files are mirrored and provide the summary of the 'Current State of Truth'.

--- 

@Agent: @dasharch - EMERGENCY PATH REPAIR & PATTERN CRYSTALLIZATION.

You have incorrectly genericized test paths. You must restore the 1:1:1 mapping between decorators, data, and manifests.

1. Path Restoration (Strict Mapping):
   - Iterate through all manifests in ./libs/transformer/tests/data/.
   - For each manifest '{{ACTION_NAME}}_manifest.yaml', ensure the 'source' path points EXACTLY to './libs/transformer/tests/data/{{ACTION_NAME}}_test.tsv'. 
   - Example: 'strip_whitespace_manifest.yaml' MUST point to 'strip_whitespace_test.tsv'.

2. Codify the Naming Law:
   - Update ./.claude/rules/workspace_standard.md (Section 8: Decorator Standards).
   - Add the following rule: 
     "Naming Convention for Atomic Testing: Every registered action MUST have a corresponding test pair using the exact action name:
      - Logic: @register_action('my_action')
      - Manifest: ./libs/transformer/tests/data/my_action_manifest.yaml
      - Data: ./libs/transformer/tests/data/my_action_test.tsv"

3. Automated Suite Alignment:
   - Ensure the 'test_decorator_suite.py' uses this naming convention to dynamically find and execute tests for all registered actions.

4. Documentation Update:
   - Reflect this strict naming convention in ./.claude/knowledge/project_conventions.md and the user docs.

5. HALT for @verify:
   - Print a table showing: [Action Name | Manifest Path | Data Path] for all currently implemented decorators to confirm the 1:1:1 mapping is restored.


   ----

- Need to create a wrapper script to automate decorator testing in ./libs/transformer/tests/ using the existing manifests and datasets that are in ./libs/transformer/data. Might need to adjust the manifests to the new standards (path of the data, input_fields and output_fields. Uncertain if the manifest follow the latest adopted standards. but this needs to be verified)

- Then it needs to document this addition (in the appropriate memory bank place and in docs for the user) and mark a rule that everytime a new decorator is added to the testing list of this it needs to be added to the test wrapper script for testing decorators.


@Agent: @dasharch - DECORATOR TEST AUTOMATION & STANDARDIZATION.

1. Manifest Audit (ADR-013/Section 12):
   - Review all YAML manifests in ./libs/transformer/tests/data/.
   - Update them to the mandatory 3-block structure: Header -> input_fields -> wrangling -> output_fields.
   - Ensure 'source' blocks use the correct relative paths for the test TSVs [ADR-015].
   - Verify that output_fields acts as a strict Polars .select() contract [Section 12].

2. Create 'test_decorator_suite.py':
   - Location: ./libs/transformer/tests/
   - Logic: A wrapper script that iterates through all implemented decorators in the registry.
   - Execution: It must call wrangler_debug.py for each decorator using its corresponding test manifest and dataset.
   - Validation: It must catch and report any decorator that fails to return a LazyFrame or violates the output contract.

3. Codify the "Testing Rule":
   - Update ./.claude/rules/workspace_standard.md (Section 8: Decorator Standards).
   - Add: "Mandatory Testing: Every new registered action MUST be added to the test_decorator_suite.py registry to ensure continuous integration of atomic logic."

4. Knowledge Mirroring:
   - Document the suite in ./.claude/knowledge/project_conventions.md.
   - Add a technical guide in ./docs/ describing how to add new decorators to the automated test loop.

5. HALT for @verify:
   - Run the suite and print the 'Pass/Fail' summary for all current decorators.

## Some cleaning

---
@Agent: @dasharch - GLOBAL PATH SYNCHRONIZATION.

Due to the consolidation of test runners, we have renamed and moved core debugging scripts. You must now synchronize all internal and external references.

1. Root Search (Excluding EVE_WORK/): 
   - Perform a recursive grep/search across the project root for the following strings:
     - "test_wrangler.py" (To be replaced by "wrangler_debug.py")
     - "assets/scripts/assembler_debug.py" (To be updated to "libs/transformer/tests/assembler_debug.py")
     - "assets/scripts/wrangle_debug.py" (To be updated to "libs/transformer/tests/wrangler_debug.py")

2. Update Targets (Absolute Source of Truth):
   - Mirror these changes in:
     - ./.claude/rules/workspace_standard.md
     - ./.claude/knowledge/project_conventions.md
     - ./.claude/tasks/tasks.md
     - All relevant files in ./docs/ (Maintaining Documentation Integrity [Section 7]).

3. Knowledge Update: 
   - Update your internal 'databank' and context to reflect that wrangler_debug.py is now the official 'Universal Wrangler Runner' [ADR 005].

4. HALT for @verify: 
   - Provide a list of all files modified and confirm that no legacy paths remain in the .claude/ hierarchy.
   
---

@Agent: @dasharch - FINAL TEST CONSOLIDATION (Layer 2).

1. Refactor assembler_debug.py (same logic than for wrangler_debug.py):
   - Implement argparse to support optional overrides for:
     --data (Path to input TSVs/Sources)
     --manifest (Path to the Assembly/Recipe YAML) (REQUIRED)
     --output (Path to the materialized result)
   - Ensure it defaults to the existing mock data if no arguments are provided.

2. Integration Check:
   - Confirm that this script utilizes the DataAssembler and the central registry [ADR 018].
   - Verify it follows the 'Evidence Generation' step of the Verification Protocol (materializing to tmp/ for manual @verify).

3. Logic Audit:
   - Final check: Ensure NO .collect() calls exist in the libs logic; keep them restricted to these test runners or the future data_executor.py.

4. HALT for @verify:
   - Provide the exact CLI command to run a test assembly with custom data.

---

@Agent: @dasharch - PRE-PLOT REFACTORING (Phase 3).

1. Functionality Audit & Comparison:
   - Compare .libs/transformer/tests/test_wrangler.py against .assets/scripts/wrangle_debug.py.
   - Determine if test_wrangler.py is deprecated or if wrangle_debug.py contains superior logic for Layer 1 terminal evaluation.
   - Ensure the survivor maintains the 'Universal Runner' standards (argparse, CLI-First) [ADR 005].

2. Migration & Consolidation:
   - Move .assets/scripts/assembler_debug.py to .libs/transformer/tests/.
   - Consolidate the superior Layer 1 test logic into .libs/transformer/tests/wrangler_debug.py.
   - Delete the redundant scripts from .assets/scripts/ once verified.

3. Lazy Audit:
   - Confirm all @register_action decorators return pl.LazyFrame and NO premature .collect() exists in the transformer core.

4. HALT for @verify:
   - Print the new directory structure of .libs/transformer/tests/ and confirm the CLI arguments for the consolidated twrangler_debug.py.