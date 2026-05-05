# 2026-03-27


# General audit, knowledge base update 

@Agent: @dasharch - ARCHITECTURAL RULE: KNOWLEDGE MIRRORING.

1. Rule Update: `docs/guide/workspace_standard.md`
- ADD Section: "Knowledge Mirroring Protocol".
- Rule: `docs/*/*.qmd` is the Master Source (The "Long Memory").
- Rule: `.claude/knowledge/*.md` is the Compressed Summary (The "Combat Log").
- Requirement: The Combat Log MUST stay 100% synced with the Master Source but in a bulleted, ultra-concise format for the user and AI.

2. Task: Restore & Sync.
- ENSURE `docs/guide/verification_protocol.qmd` is the primary source for all testing rules (the user restored the file).
- RE-GENERATE `.claude/knowledge/project_conventions.md` as a compressed "Cheat Sheet" that mirrors the verification protocol and assembler logic. 

3. Task: Gap Analysis & Promotion.
- Compare EVERY file in `.claude/knowledge/*.md` against `docs/guide/*/*.qmd`.
- Rule: If a technical detail, file summary, or protocol (like the 'verification_protocol') is more up-to-date or detailed in the Combat Log, PROMOTE it to the Quarto Master.
- Requirement: Expand the "Combat Log" bullets into full, professional documentation in the .qmd files.

4. Task: Document the File Registry.
- Ensure the 3-5 line summaries for every script (Wrangler, Assembler, etc.) are mirrored in BOTH locations:
    - Compressed Table in: `.claude/knowledge/project_conventions.md`
    - Detailed Definition List in: `docs/guide/development_rules.qmd`


4. HALT:
- Confirm that the Public Record (docs/) is now a COMPLETE SUPERSET of the Combat Log.
- Delete any redundant .md fragments that are not part of the intentional Combat Log. @verify

----

@Agent: @dasharch - ARCHITECTURAL AUDIT & SURGICAL REFACTOR.

1. Prerequisite: The "Memory Bank" Sync.
- Read `.claude/rules/workspace_standard.md`. Read all the files mentioned in it
- Compare these rules against the current file tree and logic in `./libs/`.

2. Task: The Inconsistency Audit.
- Between development plan, methodology of development of the current state of the project and the documentation. 
- Augment documentation and reorganize it to make it more clear and consistent. 
- CLEANUP: Delete every redundant or obsolete documentation fragment.

3. HALT:
- Report all "Blockers" or "Inconsistencies" found during the audit.
- Provide a "Final State" confirmation that the Workspace matches the Standards. @verify

## Refixing 
@Agent: @dasharch - KNOWLEDGE CONSOLIDATION & WORKSPACE AUDIT.

1. CRITICAL: Quarto Integration (No Duplicates).
- Files in `.claude/knowledge/` development_rules.qmd, new_data_contract.qmd and wrangling.qmd are FRAGMENTS thould be incorporated into the Quarto docs and then deleted.
- Task: Read all fragments and SURGICALLY MERGE their content into:
    - `docs/guide/development_rules.qmd`
    - `docs/guide/new_data_contract.qmd`
    - `docs/modules/wrangling.qmd`
- Preservation: Keep all original user text (especially the "Large Sense" philosophy). Append technical specs as subsections.
- Purge: Once merged, DELETE the .md files from both the docs folder and .claude/knowledge/.

2. Task: The "Knowledge Bank" File Registry.
- Generate a full directory tree of: `./libs/`, `./assets/scripts/`, and `./config/manifests/`.
- For EVERY file, provide a 3-5 line summary in the `./.claude/knowledge/project_conventions.md`:
    - Purpose: (e.g., Atomic wrangling vs. Relational assembly)
    - Inputs/Outputs: (What manifests or TSVs does it touch?)
    - Key Logic: (e.g., "Uses Key-as-ID pattern for Polars joins").
    - What is the key semantic terms used in the file eg. @register_action. 
We need to keep track of the important rules and syntaxic elements that will allow us to have good coding practices (homeogeneity, organisation, clarity ...)

3. Task: Latent Rule Extraction.
- Identify implicit rules in the code (e.g., how sample_ids are synced, how decorators are registered).
- Formalize these into a the `./.claude/knowledge/project_conventions.md` file. 
- Add relevant section to `./.docs/guide/development_rules.qmd` and other documentation files if necessary.

5. HALT:
- Provide the Tree + Summaries in the chat for my review. @verify

## Closing 

@Agent: @dasharch - SESSION CLOSEOUT & ARCHITECTURAL HANDOVER.

1. Final State Summary:
- Task: Summarize the current state of Phase 4 (Assembly) and of todays work more generally.
- Confirm: Unified Transformer (Wrangler + Assembler) is operational.
- Confirm: Relational decorators (join_filter) are implemented and verified via 'assembler_debug.py'.

2. Log Entry (The Handover):
- Write a file `./.claude/logs/session_20260327_Phase4_Complete.md`.
- Include:
    a) The exact CLI command used for the successful Abromics Assembly.
    b) A note on the "Large Sense" of Wrangling philosophy integrated into the Quarto docs.

3. Persistence & Mirroring:
- Ensure `docs/guide/development_rules.qmd` and `docs/guide/new_data_contract.qmd` are the ONLY sources of truth.
- Verify all stray .md files have been deleted.
- Mirror the final Quarto files to ./.claude/knowledge/.

4. HALT:
- Report "Session State Frozen. Handover Log Created. Architecture Locked." @verify


## Testing 


## Starting join implementation 

1. The Strategy: Join as a Filter
You have two ways to handle a reference table that doesn't share the sample_id primary key:

Option A (The Filtering Join): If your VirulenceFinder output has a gene_id and your ReferenceTable has a list of gene_ids of interest, you join them on gene_id. Any gene in the data that isn't in the reference table "drops out" of the results.

Option B (The Mapping Join): If you want to keep the data but add a "Category" (e.g., "High Risk") based on the gene name, you join them to "decorate" the rows with new metadata.


@Agent: @dasharch - UNIFIED TRANSFORMER (Wrangler + Assembler).

1. Environment Lock (Rule 5): 
- Use ONLY ./.venv/bin/python.
- Ensure `libs/ingestion` and `libs/transformer` are available as editable modules.

2. Library Enhancement: `libs/transformer/src/`
- Task: Create `libs/transformer/src/data_assembler.py`.
- Task: The `DataAssembler` must:
    a) Inherit from or share the `@register_action` registry with `DataWrangler`.
    b) Accept a dictionary of Polars LazyFrames (the 'ingredients') and an assembly recipe.
    c) Iterate through the recipe steps

3. Relational Actions: `libs/transformer/src/actions/relational.py`
- Create this file and implement the `@register_action("join_filter")` decorator.
- Logic: `df.join(other_df, left_on=l, right_on=r, how='inner')`.

3. Debug Tool: `assets/scripts/assembler_debug.py`
- Arguments: `--manifest` (e.g., ./config/manifests/pipelines/1_Abromics_general_pipeline.yaml).
- Logic:
    a) Parse 'Assembly_manifests'. Use the Key as the ID.
    b) For each ingredient: 
       - Call `ingestion` -> `DataWrangler` -> Get Wrangled LazyFrame.
    c) Pass these wrangled frames to `DataAssembler`.
    d) Execute the Assembly Recipe (Joins + Post-Wrangling).
    e) Apply `final_contract`.
    f) Save to `./tmp/assembler_{assembly_id}.tsv`.


4. Execution Test:
- Run: ./.venv/bin/python ./assets/scripts/assembler_debug.py \
  --manifest ./config/manifests/pipelines/1_Abromics_general_pipeline.yaml

---

> Complementary tests 

@Agent: @dasharch - RELATIONAL TEST SUITE (All Join Types).

1. Environment Lock (Rule 5): 
- Use ONLY ./.venv/bin/python.

2. Create Test Package (Co-located):
- Path: `libs/transformer/tests/data/` (follow same file logic)
- For each join type (inner, left, outer):
    a) Create a `{join_type}_data_A.tsv` and `{join_type}_data_B.tsv` with overlapping and non-overlapping keys.
    b) Create a `{join_type}_manifest.yaml` that defines an assembly for that specific join.
    c) Ensure the 'assembly_manifests' key (lowercase) is used.

3. Logic Verification:
- Use `assets/scripts/assembler_debug.py` to run each test.
- Output requirements:
    - Save results to `./tmp/EVE_assembler_{join_type}.tsv`.

4. Results Audit:
- Inner: Confirm only matching keys exist (The Filter).
- Left: Confirm all keys from Table A exist, with nulls for missing Table B data (The Decorator).
- Outer: Confirm all keys from both tables exist (The Union).

5. Final Full Pipeline Run:
- Once the unit tests pass, execute the main Abromics pipeline to verify the dummy gene integration:
  ./.venv/bin/python ./assets/scripts/assembler_debug.py \
  --manifest ./config/manifests/pipelines/1_Abromics_general_pipeline.yaml

6. HALT:
- Print a summary table of the row counts for the 3 unit tests vs. the final Abromics run. @verify
--- 

@Agent: @dasharch - ARCHITECTURAL DOCUMENTATION UPDATE (Phase 4).

1. Environment Lock (Rule 5): 
- Use ONLY ./.venv/bin/python.

2. Quarto Update: Review the theme of the different quarto files in docs/ directory and subdirectories. Update documentation to reflect the current state of the project.
- PRESERVE all existing user text and scientific context.
- ADD Section: "Phase 4: Data Assembly & Relational Joins".
    - Explain the `DataAssembler` class in `libs/transformer/src/data_assembler.py`.
    - Document the shared `@wrangler_action` registry.
- ADD Section: "Relational Decorators".
    - Document `join_filter`: parameters (right_ingredient, left_on, right_on, how).
    - Explain that `inner` joins are used for whitelisting/filtering.
- ADD Section: "Assembly Recipes & Contracts".
    - Use the AR1_MLST_Serotype_Virulence example to show how `ingredients` are fetched and `recipes` are executed.
    - Define the role of `final_contract` as the ultimate column guard.

3. Knowledge Mirroring:
- Update `docs/guide/new_data_contract.qmd` to include the `assembly_manifests` schema (lowercase).
- MIRROR both updated .qmd files to ./.claude/knowledge/.

4. Final Cleanup:
- Confirm that NO redundant .md files remain.
- Ensure all "EVE_" test results in `tmp/` are correctly documented as the "Traceability Standard."

5. HALT:
- Report "Documentation Unified. Assembler Logic Codified." @verify

---

@Agent: @dasharch - SURGICAL QUARTO INTEGRATION (Do NOT Overwrite).

1. Environment Lock (Rule 5): 
- Use ONLY ./.venv/bin/python.

2. Task: Document Synthesis (Context Preservation).
- Read `docs/guide/development_rules.qmd` and the recent `wrangling.md`.
- INTEGRATE the "Wrangling in a Large Sense" section from to the docs/modules/wrangling.qmd or the docs/ relevant .qmd files. 
- INTEGRATE the two files you created into .claude/knowledge/ as .qmd files into the equivalent docs/*/*.qmd files, then remove those files from .claude/knowledge. 
- USE this philosophy to frame the new "Phase 4: Data Assembly" documentation.
- Do NOT delete the user's existing text. If a section exists, APPEND the new technical specs (join_filter, assembler_debug.py) as subsections.

3. Specific Updates:
- Update `development_rules.qmd`: Include the "Unified Transformer" model where Wrangler and Assembler share the `@wrangler_action` registry.
- Update `new_data_contract.qmd`: Document the `assembly_manifests` YAML structure, emphasizing the "Key-as-ID" pattern.

4. Validation & Cleanup:
- Confirm that the Quarto callouts (::: {.callout-note}) are used for new ADRs.
- DELETE the redundant `.md` files once the `.qmd` is verified as a complete superset.
- MIRROR the final merged Quarto files to ./.claude/knowledge/.

5. HALT:
- Report "Surgical Merge Complete. Philosophical Context Preserved. Quarto is the Master Source." @verify
--- 

## New guardrail 


@Agent: @dasharch - QUARTO MASTER CONSOLIDATION & TEST EXECUTION.

1. Environment Lock (Rule 5):
- Use ONLY ./.venv/bin/python.

2. Documentation Merge (Quarto Authority):
- MERGE `development_rules.md` into `docs/guide/development_rules.qmd`.
- MERGE `new_data_contract.md` into `docs/guide/new_data_contract.qmd`.
- DELETE both `.md` versions.
- Ensure the `.qmd` files use Quarto callouts (::: {.callout-note}) for ADR-013, ADR-015, and ADR-018.
- Add a section: "Standardized Testing" with the exact CLI command for `wrangle_debug.py`.

3. Task - Live Verification (ST22 Dummy):
- Execute the debugger to prove the "Clean Lines" work:
  ./.venv/bin/python ./assets/scripts/wrangle_debug.py \
  --manifest ./config/manifests/pipelines/1_Abromics_general_pipeline.yaml

4. Evidence & Mirroring:
- Provide the exact command-line output from the successful run.
- Confirm `tmp/MLST_results_debug.tsv` (or the deduced ID) was created.
- Mirror the updated `.qmd` files to ./.claude/knowledge/.

5. HALT:
- Report "Quarto Consolidation Complete. Redundant MD Files Deleted. Testing Standardized." @verify

---

@Agent: @dasharch - MODULAR INTEGRITY AUDIT (Rule 5 & Clear Lines).

1. Environment Lock (Rule 5):
- Use ONLY ./.venv/bin/python.

2. Audit Task:
- Scan all Python files modified in the last 24 hours, specifically in:
    - ./libs/ingestion/src/
    - ./libs/transformer/src/
    - ./libs/viz_factory/src/
    - ./assets/scripts/
- Check for 'Shortened Imports' (e.g., `import ingestion`) inside the `./libs/` directory.

3. Correction Logic:
- IF a file inside `./libs/transformer/` is importing `ingestion`: 
    - REMOVE the import. 
    - REFACTOR the function to accept a Polars LazyFrame as an argument instead.
- IF a file inside `./assets/scripts/` (like wrangle_debug.py) is using `import ingestion`:
    - This is ALLOWED (it is an Orchestrator). 

4. Workspace Rule Enforcement:
- Ensure `workspace_standard.md` clearly states: "Internal lib logic must be data-agnostic; it receives data from the caller, it does not fetch it itself."

5. HALT:
- Report all violations found and fixed.
- Print the import block of `libs/transformer/src/data_wrangler.py` to prove independence. @verify

---
@Agent: @dasharch - PERMANENT WORKSPACE RULE UPDATE.

1. Environment Lock (Rule 5):
- Use ONLY ./.venv/bin/python.

2. Task: Update `./.claude/rules/workspace_standard.md`.
- Section: "ADR-013: The Manifest Data Contract"
    - Rule: All manifests MUST follow the structure: Header (ID/Desc) -> input_fields -> wrangling -> output_fields.
    - Rule: 'output_fields' is a strict Polars .select() contract. It is the final guard against Column Drift.
- Section: "Modular Library Autonomy (The Clear Lines Policy)"
    - Rule: Libraries in ./libs/ are independent, reusable modules. 
    - Rule: Structure MUST be: ./libs/[lib_name]/src/ for logic and ./libs/[lib_name]/tests/ for internal verification.
    - Rule: NO cross-imports between libs (e.g., 'transformer' cannot import 'ingestion').
    - Rule: Orchestration (joining libs) is restricted to the 'app/' layer or top-level 'assets/scripts/'.
- Section: "Python Execution Authority"
    - Rule: Use Editable Mode (pip install -e) for libs. 
    - Rule: Always execute via root ./.venv/bin/python.

3. Cross-Reference Update:
- Update `architecture_decisions.md` to point to these new sections in the workspace rules.

4. Verification:
- Read back the newly added sections to confirm they match the "Clear Lines" philosophy.
- Mirror changes to ./.claude/knowledge/.

HALT: Report "Workspace Rules Codified. Boundaries Enforced." @verify

5. Ensure code consistency to the new rules 
- Review the `pyproject.toml` created for `ingestion` and `transformer`. 
- Ensure they do not create "Circular Dependencies." 
- Rule: `libs/transformer` must NOT import from `libs/ingestion`. All cross-library coordination happens in the `app/` layer or via a shared `utils` lib.
- Update `assets/scripts/wrangle_debug.py` to ensure it acts as a "mini-app" that imports both libs correctly without violating their independent structures. 
- Verify that the other scripts use those rules and that __init__.py files are correctly set up to allow imports.

6. Refine Documentation (docs/guide/development_rules.md):
- Add a section: "Modular Boundaries and Reusability."
- Explain that each lib in `./libs/` is a standalone tool.
- Detail the "Clear Lines" policy: Data flows from Ingestor -> App -> Transformer.
- Explain the import strategy: Using `import ingestion` is allowed due to editable installs, but the internal `src/` structure must be respected to maintain local testability.

HALT: Report "Workspace Rules Codified. Boundaries Enforced. Documentation updated." @verify


## Manifest creations for Abromics (Minimum dataset for figures)

@Agent: @dasharch - REFINED WRANGLE DEBUGGER (v2).

1. Environment Lock (Rule 5):
- Use ONLY ./.venv/bin/python.




./.venv/bin/python ./assets/scripts/wrangle_debug.py \
--manifest ./config/manifests/pipelines/1_Abromics_general_pipeline.yaml




---
@Agent: @dasharch - DOCUMENTATION REFINEMENT (The Data Contract).

1. Environment Lock (Rule 5):
- Use ONLY ./.venv/bin/python.
    
2. Task: Create `.assets/scripts/wrangle_debug.py`.
- The script must take 1 argument: `--manifest`.  Deduce the dataset from the 'id' or 'name' field inside the YAML.
- Logic:
    a) Read the general pipeline manifest (./config/manifests/pipelines/1_Abromics_general_pipeline.yaml).
    b) Extract the specific `dataset_id` block.
    c) Use the `ingestion` package to load the LazyFrame via the 'source' block.
    d) Pass the LazyFrame and the wrangling steps to the `DataWrangler`.
    e) Validate vs. `output_fields` (The Contract).
    f) Sink the result to `./tmp/{dataset_id}_debug.tsv` using `df.collect().write_csv(separator='\t')`.


3. Documentation Task: Create/Update `docs/guide/new_data_contract.md`.
- Section 1: The Anatomy of a Manifest.
    - Explain the Header (ID, Description, header Metadata).
    - Explain the data contracts for the different types of datasets (data_schemas, metadata_schema, additional_datasets_schemas). Eg. datasets comming from same pipeline (data_schemas) vs metadata_schema (metadata for the pipeline dataset) vs datasets comming from different pipelines, references datasets, etc (additional_datasets_schemas).
    - Explain the three-block structure that is valid for all dataset types: `input_fields`, `wrangling`, `output_fields`.
    - Use `./config/manifests/pipelines/1_Abromics_general_pipeline.yaml` (active datasets only - uncommented) as the primary code example.
- Section 2: Actions vs. Contracts.
    - Explicitly explain why we separate 'wrangling' (the actions) from 'output_fields' (the final state).
    - Explain that 'output_fields' is the final Polars `.select()` guard.
- Section 3: Preventing Column Drift.
    - Describe how this setup ensures the DataAssembler receives a stable, predictable schema even if raw ingestion changes.
- Section 4: Scaling the Pipeline.
    - Instructions on how to add a new dataset to the general manifest using the same principles.

4. Consistency Check:
- Ensure the documentation matches the actual logic in `libs/ingestion/` and `assets/scripts/wrangle_debug.py`.

5. HALT:
- Mirror the file to ./.claude/knowledge/ for session persistence.
- Provide a 3-sentence summary of the new guide. @verify

----

- The user has created a general manifest, it contains manifest for several datasets 
- we need a solution to add the path of the dataset in the manifest so it can easily be used by the system for testing (note later on this path might be a variable as the data will be fetched from api or for adatabase - so we need a flexible solution that will allow determine how the data is loaded)
- the general manifest is in ./config/manifests/pipelines/1_Abromics_general_pipeline.yaml - comments mask datasets that are not yet implemented (keep those as is). We need to test if all the different datasets can be loaded and processed correctly. 
- The datasets are currently in ./assets/test_data/1_test_data_ST22_dummy/ directory, ./assets/test_data/2_VIGAS-P_ST22_dummy and ./assets/ref_data/Virulence_genes_APEC


@Agent: @dasharch - MULTI-SOURCE ALIGNMENT (Phase 4 Preparation).

1. Environment Lock (Rule 5): 
- Use ONLY ./.venv/bin/python.

2. General Manifest Update:
- Open `./config/manifests/pipelines/1_Abromics_general_pipeline.yaml`.
- For each active (uncommented) dataset, implement a `source` block:
    ```yaml
    source:
      type: "local_tsv" # Flexible for future 'api' or 'db' types
      path: "./assets/test_data/1_test_data_ST22_dummy/filename.tsv"
    ```
- Use the following directory mappings for the active datasets:
    - Group 1: ./assets/test_data/1_test_data_ST22_dummy/
    - Group 2: ./assets/test_data/2_VIGAS-P_ST22_dummy/
    - Group 3 (Ref): ./assets/ref_data/Virulence_genes_APEC/

3. Ingestion Logic Adaptation:
- Modify `libs/ingestion/src/ingestor.py` (or relevant loader) to:
    a) Read the `source` block from the manifest.
    b) If `type == "local_tsv"`, resolve the path relative to the project root.
    c) Ensure it remains compatible with Polars `scan_csv`.

4. Batch Validation Test:
- Use the Universal Runner or a new loop script to verify that all active datasets in the general manifest can be reached and read into a LazyFrame.
- Report a "Connectivity Table" (Dataset ID | Path | Status).

5. HALT:
- Do NOT uncomment hidden datasets.
- Save changes to the local workspace mirror. @verify


--- Tesing creation of input_fields manifest ---


----

For dataset `./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv` 
- Need creation input_fields manifest (not the global one, so maybe we should have the way to have a script that only create the input fields manifest - could be an option from /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/assets/scripts/SF_create_manifest.py script)
-  Need creation output_fields : keep columns : sample_id, Sequence Type
- Need maybe a solution to store a value from Scheme column (unique value - so it can eg be used as information for a plot later on or a method information later on . Here it would be eg . used Scheme: ecoli_achtman_4) - Usure if it could be easy (if not we can keep that for later on - We can write that as a defer solution to find)


- create input_fields manifest for ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv

We will have to create the input_fields manifest in ./config/manifests/pipelines/1_Abromics_general_pipeline directory

The user will create the wrangling and output_fields manifests


@Agent: @dasharch - MANIFEST GENERATION (MLST & Metadata).

1. Environment Lock (Rule 5):
- Execute using ONLY ./.venv/bin/python.

2. Script Enhancement:
- Read `assets/scripts/SF_create_manifest.py`.
- Add a `--mode` argument with options: `full` (default) or `input_only`.
- In `input_only` mode, the script should ONLY generate the `input_fields` block based on Polars schema inference and leave `wrangling` and `output_fields` as empty lists `[]`.

3. Task - MLST Manifest:
- Generate input-only manifest for: `./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv`
- Save to: `./config/manifests/pipelines/1_Abromics_general_pipeline/MLST_results_manifest.yaml`

4. Task - Metadata Manifest:
- Generate input-only manifest for: `./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv`
- Save to: `./config/manifests/pipelines/1_Abromics_general_pipeline/test_metadata_manifest.yaml`

5. Metadata Extraction (Conceptual):
- Identify the unique value in the 'Scheme' column of the MLST data.
- Do NOT implement a solution yet. Log this requirement in ./.claude/knowledge/blockers.md as: "ST22-001: Implement Metadata Constant Extraction for global plot labels."

6. HALT:
- Confirm both YAML files exist in the target directory.
- Print the first 5 lines of each to verify ADR-013 structure. @verify



## Initiation

@Agent: @dasharch - SYSTEM INITIALIZATION 
1. Mandatory Context Injection (Read First):
- ./.claude/rules/workspace_standard.md (The Law)
- ./.claude/knowledge/architecture_decisions.md (The History)
-  ./.claude/workflows/verification_protocol.md (procedure)

2. Environment Lock ( NON-NEGOTIABLE):
- You MUST use the root `./.venv/bin/python`. 
- Verify now: Run `which python` and `python -c "import sys; print(sys.prefix)"`. 
- If it is NOT the project .venv, STOP and report the error.

3. Execution Protocol (Rule 11 & ADR-013):
- Manifests now use: input_fields -> wrangling -> output_fields.
- Do NOT execute tasks autonomously. The user will prompt for specific tasks
- Every task must end with a HALT and a request for @verify.

Confirm your environment is locked to ./.venv and you are ready for Phase 3 manual verification support. @verify

--- 
@Agent: Assume persona @dasharch.
Welcome back. Before generating any code or executing steps, you MUST fulfill the following contextual handoff requirements:
**Read `./EVE_WORK/notes/daily/2026-03-27/Instructions_log.md`** This is the log from yesterday. W we will continue where we left off.

---



