# 2026-03-26


**Action Audit: 'split_column'** 
## 
- [ ] test split_column decorator

- [ ] test one by one the new decorators
- [ ] update documentation (new decorators, architectural decisions)

## Testing 

## List of genes to extract from virulence finder 

- [ ] restart here : checking the abscence of wrangling and correct work of the process 
```bash
./.venv/bin/python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --manifest ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_manifest.yaml \
  --output tmp/EVE_TEST.tsv
```

Now we will need to run the command : 
./.venv/bin/python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --manifest ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_manifest.yaml \
  --output tmp/EVE_TEST.tsv

 But this data set has a particularity, it should just be imported as is. So only the input_fields should be populated. The script  test_wrangler.py should be adapted such as the ability to take into for empty wrangling and output_fields or (wrangling: [ ], output_fields: [ ]) or ommited wranlging and output fields, in which case the output should be the same as input data. 


@Agent: @dasharch - SCRIPT ADAPTATION (Identity Transformations).

We need to support datasets that require "Import-As-Is" logic (No wrangling, No output filtering).

1. Environment Lock (Rule 5): 
- Use ONLY ./.venv/bin/python.

2. Code Modification:
- Modify `libs/transformer/tests/test_wrangler.py` and the core `DataWrangler` logic:
    a) If `wrangling` is missing or an empty list `[]`, bypass the action execution loop.
    b) If `output_fields` is missing or an empty list `[]`, the final LazyFrame should retain all columns from `input_fields`.
- Ensure no Polars exceptions are raised when these keys are null or ommitted. But You are welcome to introduce a message that can be printed to the console that says "Identity transformation".

3. Execution Test (Identity Check):
- Run: ./.venv/bin/python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --manifest ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_manifest.yaml \
  --output tmp/EVE_TEST.tsv

4. Evidence & HALT:
- Print `df.glimpse()` of the result.
- Verify that the column count in `tmp/EVE_TEST.tsv` matches the raw input exactly.
- DO NOT proceed further. @verify




---


@Agent: @dasharch - SCRIPT UPGRADE (Asset Generator v2).

The command for `create_manifest.py` failed to produce an output. 

1. Environment Lock (Rule 5):
- Execute using ONLY ./.venv/bin/python.

2. Debug & Refactor Task:
- Read `assets/scripts/create_manifest.py`.
- Create a NEW improved version: `assets/scripts/SF_create_manifest.py`.
- Improvements Required:
    a) Directory Guard: Use `os.makedirs(exist_ok=True)` for the output path.
    b) ADR-013 Compliance: The generated YAML MUST contain:
       - `input_fields`: (Inferred from Polars `df.schema`).
       - `wrangling`: (A placeholder list `[]`). 
       - `output_fields`: (A placeholder list `[]`).
    c) Polars Integration: Use `pl.scan_csv(separator='\t')` to read the first 10 rows and map Polars types to YAML types.

3. Execution Test:
- Run: ./.venv/bin/python ./assets/scripts/SF_create_manifest.py \
  --data ./assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC.tsv \
  --output tmp/EVE_manifest.yaml

4. HALT & Evidence:
- Confirm `tmp/EVE_manifest.yaml` exists.
- Print the first 10 lines of the generated YAML to verify the ADR-013 structure.
- DO NOT proceed to further tasks. @verify


## Virulence finder  - VIGAS-P

./.venv/bin/python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/test_data/2_VIGAS-P/VIGAS_VirulenceFinder/VIGAS_VirulenceFinder_test.tsv \
  --manifest ./config/manifests/VIGAS-P/VIGAS_VirulenceFinder.yaml \
  --output tmp/EVE_TEST.tsv



@Agent: @dasharch - MANUAL VERIFICATION (VIGAS-P Virulence).

1. Environment Lock (Rule 5):
- Execute using: ./.venv/bin/python
- Verify path before running.

2. Test Execution:
- Run the Universal Runner with the following specific paths:
  python ./libs/transformer/tests/test_wrangler.py \
  --data ./assets/test_data/2_VIGAS-P/VIGAS_VirulenceFinder/VIGAS_VirulenceFinder_test.tsv \
  --manifest ./config/manifests/VIGAS-P/VIGAS_VirulenceFinder/VIGAS_VirulenceFinder_wrangling.yaml --output tmp/EVE_TEST.tsv

3. Verification Steps:
- Check if the 'input_fields' correctly validated the raw TSV.
- Verify the 'wrangling' steps were staged in the Polars plan.
- Confirm the final LazyFrame was collected and filtered to only include 'output_fields'.

4. Evidence & HALT:
- Print `df.glimpse()` of the result.
- Save a debug view to `tmp/EVE_TEST.tsv`.
- DO NOT proceed to the next task. HALT and report results. @verify

---

@Agent: @dasharch - Execute Sequential Verification for [split_column].

1. **Step A: The Contract (TSV + YAML):**
   - './libs/transformer/tests/data/split_column_test.tsv' and './libs/transformer/tests/data/split_column_manifest.yaml' have been generated and verified by the user
  
2. **Step B: Execution for [split_column]:**
   - Run the universal script: `.venv/bin/python libs/transformer/tests/test_wrangler.py --data ./libs/transformer/tests/data/split_column_test.tsv --manifest ./libs/transformer/tests/data/split_column_manifest.yaml --output tmp/split_column_debug_view.tsv`.
   - correct any errors of the script and implementation of the split_column decorator

3. **Step C: Evidence & Inspection:**
   - Materialize results to 'tmp/USER_debug_view.tsv' and 'tmp/split_column_debug_view.tsv'.
   - Print `df.glimpse()` to the terminal.
   - **HALT:** "Execution complete. Check USER_debug_view.tsv in Excel Viewer. Waiting for @verify to mark as [DONE]."

---

@Agent: @dasharch - Documentation Update: Decorator Registry & CLI Usage.

1. **Task Completion:** @verify. Mark [split_column] as [DONE] in './.claude/tasks/tasks.md'.
2. **Update Documentation:** Augment the 'Decorator Registry' in './docs/modules/wrangling.qmd' appropriate existing guide.
3. **Standard Entry Template:** For each 'split_column' decorator, include:
   - **Description:** A clear functional summary. Explain processing of edge case (truncation, abscence of delimiter, etc.)
   - **Manifest Link:** Provide a relative link to the tested YAML in './libs/transformer/tests/data/'.
   - **Test Data Link:** Provide a relative link to the input TSV/CSV used for the test.
4. **STOP:** Present the documentation entry for 'split_column' wait for further instructions.


## Agent alignment (OK) 

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
## Blocker removal : decision data schema

@Agent: @dasharch - ARCHITECTURAL REFACTOR (ADR-013: Dual-State Schema).

1. Update Source of Truth:
- Read ./.claude/knowledge/architecture_decisions.md and ./.claude/knowledge/blockers.md.
- Create ADR-013: "Dual-Validation Manifests".
    - Rule: Manifests must use `input_fields` (Raw/Ingestion), `wrangling` (Logic), and `output_fields` (Final Contract).
- Remove the Blocker regarding "DataSchema representation" from blockers.md as it is now resolved by this Hybrid approach.

2. Manifest Restructuring:
- Locate all YAML manifests in ./config/manifests/pipelines/.
- Perform the following structural update:
    - Rename the existing 'fields:' key to 'input_fields:'.
    - Ensure 'wrangling:' remains the second block.
    - Append an 'output_fields:' block after 'wrangling:'. 
    - For now, populate 'output_fields:' with the same list as 'input_fields:' unless a 'drop_columns' or 'rename' action is clearly present in the wrangling block.

3. Code Alignment Check:
- Scan `libs/ingestion/` and `libs/transformer/` to identify where the 'fields' key is accessed.
- Update the logic to point to 'input_fields' for raw validation and 'output_fields' for final selection.

4. Verification:
- Run a syntax check on one modified YAML to ensure it remains valid.
- HALT and report: "ADR-013 Implemented. Manifests migrated. Waiting for @verify."

## Initiation

Assume persona @dasharch.

Welcome back. Before generating any code or executing steps, you MUST fulfill the following contextual handoff requirements:
1. **Read `./.claude/rules/workspace_standard.md`
2. **Read `./.claude/knowledge/architecture_decisions.md`**. Align your understanding with the Sequential Staging logic for YAML manifests.
3. Review `./.claude/knowledge/blockers.md` carefully: there is an active blocker regarding Manifest Consistency (`VIGAS_VirulenceFinder` pipeline paths and schema field discrepancies).
4. **Read `./.claude/workflows/verification_protocol.md`**
5. Report any architectural divergence immediately upon starting your work. If user prompts contradict established rules, invoke the Halt & Verify protocol.

---


## Setup prep 
- [x] Rewrote my helper gem and improved to be able to better help with tasks (setup sync context, insurance consistency instructions, etc.)



