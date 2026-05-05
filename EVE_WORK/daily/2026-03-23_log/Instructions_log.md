# 2026-03-23 - Restarting development 

> Agent : "Recovery Toolkit Initialization and Consistency check" 

> Inventory confirmed. Start with fill_nulls verification
BUT produced csv - need to motify 
@Agent: REJECTED. You are bypassing the Project Architecture.

1. **New Requirement: TSV Default.** re-ingest and re-index './agents/rules/verification_protocol.md' it has been updated by the user to reflect the TSV default requirement.
2. **Use the Testing Framework:** Do NOT write long Python strings in the terminal. 
   - All logic must live in `./libs/transformer/src/`.
   - All tests must be executed via python scripts that are specifically designed for this purpose in each library eg. for transformers use `pytest libs/transformer/tests/test_wrangler.py`, update if necessary but do not remove any other test functionality.
3. **Restart Phase B (Execution):**
   - Update `test_wrangler.py` to handle the TSV loading and YAML manifest.
   - Run the test using the command: `.venv/bin/pytest libs/transformer/tests/test_wrangler.py`.
   - Materialize the results to `tmp/USER_debug_view.csv` (keeping the output viewable in Excel Viewer).
4. **HALT:** Provide the `df.glimpse()` output and wait for my @verify signal. 


--- ENSURING OK STATUS ---
@Agent: @dasharch - Optimization: Update .aiignore.

1. **Update .aiignore:** Add `*.egg-info/`, `__pycache__/`, `.venv/`, and `tmp/` to the .aiignore file in the root.
2. **Verify Focus:** Confirm that you will no longer scan these directories during your background indexing.
3. **Clean Workspace Check:** Confirm that all 'requires.txt' files have been deleted and dependencies are strictly inside the `pyproject.toml` files.
4. **STOP:** Once the ignore rules are active and the workspace is clean, provide a final confirmation of the environment status.

--- VERIFYING ROOT PROJECT FOR WORKSPACE BEFORE GIVING ACCESS AUTHORIZATION ---
@Agent: @dasharch - Security & Scope Check.
1. **Identify Root:** Run `pwd` or a Python `os.getcwd()` and report exactly what you consider the 'Project Root'.
2. **List Top-Level:** List all directories in the current root. 
3. **Confirm Boundaries:** Explicitly confirm that you do NOT have access to paths outside of this specific workspace folder (e.g., your User home directory or System folders).

--- ENSURING CLEAN REPO - cleaning build artifacts ---
@Agent: @dasharch - Emergency Dependency Consolidation.

1. **Purge Legacy Artifacts:**
   - Locate and delete any `requires.txt` or `requirements.txt` files generated in `app/` or `libs/*/`.
   - Ensure the `.egg-info` directories are left alone (these are normal for editable installs).
2. **Standardize pyproject.toml:**
   - For `app/` and each library in `libs/`, ensure all dependencies (e.g., polars, plotnine, shiny) are explicitly listed under the `[project.dependencies]` key in the `pyproject.toml` file.
   - DO NOT create external requirements files.
3. **Environment Re-Sync:**
   - From the root `.venv`, run `pip install -e ./libs/transformer`, `pip install -e ./libs/viz_factory`, and `pip install -e ./app` to ensure the registry is based on the TOML files.
4. **Memory Bank Correction:**
   - Update ./.claude/knowledge/architecture_decisions.md to state: "Legacy requirements files are forbidden; pyproject.toml is the sole source of truth for module dependencies".
5. **STOP:** Confirm once the TOML files are updated and the 'requires.txt' files are deleted. Do not proceed to wrangling until the file structure is clean.


--- ADDING MISSING DECISIONS TO DOCUMENTATION SO WILL REMEBMER NEXT TIME 
 ---
@Agent: @dasharch - Permanent Memory Update: Modular Monorepo Strategy.

1. **Document Architecture Decision:**
   - Update ./.claude/knowledge/architecture_decisions.md.
   - **Title:** ADR-005: Modular Monorepo & Independent Package Management.
   - **Context:** The project is a monorepo where each subdirectory in `libs/` is an independent Python package.
   - **Decision:** Each library MUST maintain its own `pyproject.toml`. The global `.venv` at the root will install these libraries in 'editable mode' (`pip install -e ./libs/transformer`).
2. **Map the Paths:**
   - Explicitly list the paths in the ADR: `./libs/transformer`, `./libs/viz_factory`, and `./app`.
   - Note that `./libs/utils` also follows this pattern.
3. **Requirement Scan:**
   - Scan each existing `pyproject.toml` in those paths. 
   - If `polars` is missing from `libs/transformer/pyproject.toml`, add it.
   - If `plotnine` is missing from `libs/viz_factory/pyproject.toml`, add it.
4. **Implementation Plan Update:**
   - Update ./.claude/plans/implementation_plan_v2.md to include 'Module Dependency Management' as a core development rule.
5. **STOP:** Confirm these files are mirrored and the paths are correctly recorded. Do not build the .venv until I verify this ADR.

## 1. restarting - new chat - avoiding long context
@Agent: Assume persona @dasharch.
1. Read the Recovery Toolkit in ./.claude/ (specifically tasks.md and implementation_plan_v2.md).
2. Perform a Consistency Check between the YAML manifests in ./config/manifests/pipelines/ and the code in ./transformer/ and ./libs/viz_factory/.
3. Verify that the Decorator Registry is ready for the first implementation: drop_duplicates and summarize.
4. Initialize libs/transformer/src/actions/core/duplicates.py and summarize.py.
5. Begin the refactor of libs/viz_factory/src/base.py to use a @register_plot decorator, mirroring the success of the Transformer registry.




 