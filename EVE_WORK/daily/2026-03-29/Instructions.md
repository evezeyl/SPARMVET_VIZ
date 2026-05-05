
## Starting implementation 

> Implemented that as a workflow and now its almost automatic one by one, perfect ! 
#TODO:  REMEMBER THIS FOR FUTURE

Ok, what I would like to do now, its to get the implementation of the polar library to be sure we do not have missed 
### Adding idea 

@Agent: @dasharch - FINAL VISION ANCHOR.

1. UPDATE ARCHITECTURE DECISIONS:
   - Create 'ADR-022: The Gallery & Recipe Pattern'.
   - Decision: The system will provide a 'Visual Gallery' where each plot is defined by a 3-part 'Recipe': (1) Representative Data Header, (2) YAML Manifest, (3) Resulting Image.
   - Purpose: To enable users to build personalized plots by copying and modifying existing manifests.

2. PROMOTE SCRIPTS:
   - Move 'tmp/bulk_debug_viz_factory_layers.py' to 'assets/scripts/'.
   - Refactor it to support a '--gallery' flag that generates the 'Data Header + Plot' pairs for documentation.

3. DOCUMENTATION (Violet Law):
   - Update 'docs/appendix/viz_factory_rationale.qmd' to include the 'User-as-Artist' philosophy.
   - Mention that the 'Triple-Source Integration' (Metadata/Phenotypes/Genotypes) is the premier example in this gallery.

4. LOG & CLOSEOUT:
   - Finalize './.claude/logs/audit_2026-03-29.md' with this roadmap.
   - Generate the 'Resume Prompt' for the next session to focus on 'Gallery Implementation'.

Provide the one-line 'State of Truth' and HALT.
### Cleaning scripts 

@Agent: @dasharch - RECOVERY ACTIVE. 
Mission: Evaluate 'tmp/' Scripts for Promotion to 'assets/scripts/'.

1. INVENTORY & AUDIT (Violet Law):
   - Review all Python scripts created in 'tmp/' during the Triple-Source Join session.
   - Target for Promotion: Any logic for 'SDK Normalization', '3-Way Joining', or 'Bulk Execution'.

2. MERGE & ENHANCE LOGIC:
   - Compare the 'tmp/' scripts against existing tools in 'assets/scripts/'.
   - ACTION: If a 'tmp/' script offers new functionality (e.g., automated TSV-to-YAML bootstrapping or multi-source joining), MERGE it into the appropriate tool in 'assets/scripts/'.
   - REFACTOR: Ensure all promoted code follows ADR-011 (Modular Monorepo) and does NOT use 'sys.path' hacking.

3. SCRIPT HARDENING (The Evidence Loop):
   - Every script in 'assets/scripts/' MUST use 'argparse' for path resolution.
   - Every script MUST include a '--help' description that explains its role in the SPARMVET_VIZ pipeline.

4. UPDATES:
   - Update './.claude/knowledge/project_conventions.md' to reflect the new capabilities of the scripts in 'assets/scripts/'.
   - Document the promotion in the daily audit log: './.claude/logs/audit_2026-03-29.md'.

5. TASK BLOCKER:
   - Stop activity once the 'assets/scripts/' have been updated and the 'tmp/' directory is cleaned.

HALT for @verify before deleting any script from 'tmp/' (we will KEEP the plots).

### Fixing 

@Agent: @dasharch - Persona ACTIVE. 
Mission: Viz_Factory Integrity Audit & Default Logic Implementation.

1. DEFERRED/FAILED CLASSIFICATION:
   - Audit all [ ] and [FAILED] tasks in ./.claude/tasks/tasks.md.
   - Investigate Plotnine/Mizani capabilities for each.
   - RECLASSIFY: If the feature (e.g., specific geom or scale) is missing in Plotnine, mark as: [DEFERRED - FEATURE NOT YET IMPLEMENTED IN PLOTNINE].
   - REMEDIATE: If it is a logic error in our implementation, FIX IT IMMEDIATELY and verify.

2. MANIFEST OMISSION & DEFAULT LOGIC:
   - Refactor VizFactory (viz_factory.py) to support omitted manifest keys.
   - IMPLEMENT DEFAULTS: If a layer is missing in the YAML, the factory must inject:
     - Theme: theme_bw (Default)
     - Coord: coord_cartesian
     - Position: position_identity
     - Facet: facet_null
     - Stats: stat_identity
   - NOTE: Do NOT implement a default 'geom'; the manifest must explicitly define at least one geom to render.

3. BULK TEST UTILITY (bulk_debug_viz_factory_layers.py):
   - Locate or recreate 'libs/viz_factory/tests/bulk_debug_viz_factory_layers.py'.
   - FEATURES:
     - Use argparse for --layer (optional) and --output (default: tmp/).
     - Results MUST materialize in tmp/<layer_name>/<component>.png.
     - Console Output: A clean table showing [PASS/FAIL] for every registered component.
   - DOCUMENTATION: Update './docs/reference/developer_how_to.qmd' with usage instructions for both the Bulk Runner and the Single Component Runner.

4. DOCUMENTATION AUDIT:
   - Update 'docs/workflows/vizualisation_factory.qmd' and 'docs/appendix/viz_factory_rationale.qmd'.
   - Ensure the rationale explains WHY specific features are [DEFERRED - FEATURE NOT YET IMPLEMENTED IN PLOTNINE].
   - Verify all Violet Law references: 'ComponentName (file_name.py)'.

5. TASK BLOCKER:
   - Do not proceed past the established [TASK BLOCKER] in tasks.md.
   - Append a summary of all reclassifications and the new Bulk Runner status to todays audit log.

HALT for @verify after implementing the Manifest Default Logic.
--- 

1. We should investigate the tasks for the viz_factory that are marked as DEFERRED OR FAILED and that are then not yet completed
- Are they trully to be DEFERRED : functionality not yet implemented in plotine (mark as [DEFERRED - FEATURE NOT YET IMPLEMENTED IN PLOTNINE] ) 
- Are they trully to be FAILED : functionality implemented but not working as expected  - if so - fix it at once
- If FAILED because not yet implemented in plotnine then mark the task as [DEFERRED - FEATURE NOT YET IMPLEMENTED IN PLOTNINE] 

2. Ability to omit layers in manifest: verification and implementation (we need to refine)
- We need to be able to omit layers in manifest, in which case default layers should be used: eg: theme_bw (better than theme_minimal, coord_cartesian, position_identity, facet_null, ...) > advise: I do not think a default geom is a good idea. We need default scale, stats is identity, position is identity, coord is cartesian, facet is null, theme is bw, ... 

3. The agent had created a bulk wrapper to test the whole viz_factory layers implementation, I cannot find the script. But such a script should be existing and caulled bulk_debug_viz_factory_layers.py - all output graphs should be provided in tmp/<layer> directory. It should be run by the user via argparse, and it should show a nice output with pass/fail for each component in the console. 
- The script should also provide the option to test a specic layer (if we do not want to test all of them)
- This should be reflected in the documentation for the user in docs in the appropriate place ./docs/reference/developer_how_to.qmd 
- The single component test script should also be documented there. 

4. ensure that the documentation in ./docs is complete for the viz_factory implementation
docs/workflows/vizualisation_factory.qmd and docs/appendix/viz_factory_rationale.qmd (ensure that the 
[DEFERRED - FEATURE NOT YET IMPLEMENTED IN PLOTNINE] tasks are mentionned there) 


--- 

@Agent: @dasharch - Persona ACTIVE. 
Mission: Iterative Completion of Viz_Factory Layers.

1. READ CORE PROTOCOLS:
   - ./.claude/workflows/viz_factory_implementation.md (Mandatory Test Loop)
   - ./.claude/rules/rules_behavior.md (The @verify Protocol)
   - ./.claude/tasks/tasks.md (Target List: Geoms, Scales, Themes, Facets, Coords, Positions, Guides, Stats)

2. OPERATIONAL PIPELINE (ITERATE PER COMPONENT):
   For every [ ] task in the Viz_Factory section:
   A. COMPONENT CHECK: Verify @register_plot_component exists in libs/viz_factory/src/.
   B. CONTRACT SYNC: If missing, create the triplet in libs/viz_factory/tests/test_data/:
      - {component_name}_test.tsv
      - {component_name}_test.yaml
   C. EXECUTION: Run the Unified Test Runner (libs/viz_factory/tests/test_runner.py).
   D. MATERIALIZATION: Save plot to tmp/<layer_name>/{component_name}.png. 
   E. GLIMPSE: Print df.glimpse() and the plot construction log to terminal.

3. ARCHITECTURAL GUARDRAILS:
   - HAND-OFF RULE: Ensure .collect() happens ONLY inside VizFactory (viz_factory.py) at ggplot init. No Pandas in the logic layers.
   - VIOLET LAW (RE-CLARIFIED): Use 'ComponentName (file_name.py)' in READMEs and .qmd documentation ONLY. Do NOT use this format for functional code/variable names.
   - BLOCKER SENSE: You MUST STOP and HALT activity if you reach the [TASK BLOCKER] defined in tasks.md.

4. UPDATES:
   - Only mark a task [x] after the plot is successfully generated in tmp/.
   - Update architecture_decisions.md if any new patterns emerge.

HALT for @verify after the first 3 successful components to ensure the 'Deep Violet' aesthetic and Polars-to-Plotnine hand-off are perfect.

### Status audit 


@Agent: @dasharch - CRITICAL RULE CORRECTION & AUDIT.

1. **Update Authority**:
    - Open `/.claude/rules/rules_aesthetic.md`.
    - Explicitly clarify Section 1 (The Violet Law): "This is a DOCUMENTATION-ONLY standard. It applies to .qmd files, intended for USER/HUMAN consumption only (NOT to  READMEs, and high-level Docstrings). It MUST NOT be used for functional variable names, filenames, or class definitions within the logic."

2. **Re-Audit Functional Logic**:
    - Scan the recent implementations in `libs/viz_factory/src/`.
    - If you renamed any Python classes, variables, or files to match the "Violet" format (e.g., adding spaces or parentheses in code), REVERT THEM IMMEDIATELY to standard Pythonic naming (Snake_case/PascalCase).
    - Logic must remain clean; documentation must remain "Violet."

3. **Verify Documentation Sync**:
    - Ensure `/.claude/knowledge/project_conventions.md` accurately describes this boundary.
    - Confirm that `libs/viz_factory/README.md` uses the Violet Law for its "Key Components" list, but the actual code it points to is standard Python.

4. **Self-Correction Report**:
    - List any files where you incorrectly applied the Violet Law to functional code and confirm they have been reverted.


--- 


@Agent: @dasharch - DEEP ARCHITECTURAL CONSISTENCY & DOCUMENTATION AUDIT.

1.  **Read Sources of Truth**:
   - ./.claude/rules/workspace_standard.md (Master Authority)
   - ./.claude/knowledge/architecture_decisions.md (Technical Bible)
   - ./.claude/plans/implementation_plan_master.md (Roadmap)
   - ./.claude/workflows/viz_factory_implementation.md (testing plotocol for viz_factory implementation)
    - ./.claude/tasks/tasks.md (Current List)
    - ./libs/viz_factory/src/registry.py (Component Registry)
    - ./libs/viz_factory/tests/test_data/ (Verification Evidence)

2.  **Tasks audit**:
    - Cross-reference the "Done" [x] checkboxes in tasks.md against the actual presence of @register_plot_component decorators in the code.
    - Validate that every 'Completed' Viz component has a corresponding triplet in ./libs/viz_factory/tests/test_data/ ({name}_test.tsv, {name}_test.yaml, and evidence in tmp/).
    - If a task is marked [x] but lacks code or verification evidence, revert it to [ ].
    - If a task is implemented and verified but marked [ ], update it to [x].

3. **Context Alignment (Violet Law & ADR-013)**:
    - Audit all Python files in `libs/viz_factory/` 
    - Every component MUST be documented in its header or README using the Violet Standard: `ComponentName (file_name.py)`.
    - Cross-check all YAML manifests in `libs/viz_factory/tests/data/`. They MUST follow ADR-013: Header, `input_fields`, `wrangling`, and `output_fields`. 
   
4. **Technical Traceability (Polars-to-Plotnine)**:
    - Verify the "Hand-off Rule" (ADR-010): Polars `.collect()` MUST only occur at the final moment of `ggplot()` initialization in `VizFactory (viz_factory.py)`.
    - Search for any "leakage" of Pandas logic outside of the final visualization rendering; replace with Polars LazyFrame equivalents where found.

5. **Documentation Mirroring & Broken Links**:
    - Audit `./.claude/knowledge/project_conventions.md` against the current file tree. Update any stale file paths or I/O descriptions.
    - Check for "Ghost State": Technical decisions mentioned in chat but missing from `./.claude/knowledge/architecture_decisions.md`.
    - Ensure every library in `libs/` has a `README.md` that correctly lists its Key Components.

6. **Refactoring & Remediation**:
    - If you find a component that is implemented but undocumented, fix the documentation immediately.
    - If you find a component that violates the 'Clear Lines' Policy (cross-library imports), log it as a CRITICAL BLOCKER in `./.claude/knowledge/blockers.md`.

7. **Final Output**:
    - Update `tasks.md` and `implementation_plan_master.md` to reflect the absolute current state of truth.
    - Generate a `/.claude/logs/audit_{{YYYY-MM-DD}}.md` documenting all fixes made during this consistency sweep.

HALT for @verify before committing major file rewrites.
### Guides implementation 

----

@Agent: @dasharch - AUDIT AND RECONCILE TASK STATE.

1.  **Read Sources of Truth**:
    - ./.claude/tasks/tasks.md (Current List)
    - ./.claude/plans/implementation_plan_master.md (Roadmap)
    - ./libs/viz_factory/src/registry.py (Component Registry)
    - ./libs/viz_factory/tests/test_data/ (Verification Evidence)

2.  **Audit Logic**:
    - Cross-reference the "Done" [x] checkboxes in tasks.md against the actual presence of @register_plot_component decorators in the code.
    - Validate that every 'Completed' Viz component has a corresponding triplet in ./libs/viz_factory/tests/test_data/ ({name}_test.tsv, {name}_test.yaml, and evidence in tmp/).
    - If a task is marked [x] but lacks code or verification evidence, revert it to [ ].
    - If a task is implemented and verified but marked [ ], update it to [x].
    - If tasks cannot be implemented because not yet implemeted in plotnine source code mark the tasks as [DEFERRED - NEED SOURCE CODE UPDATE ] 

Follow the @verify protocol before finalizing the file writes.


----
@dasharch @verify thank you excellent @verify for positions.
1. Please ensure that all the positions implementation is documented in ./docs/workflows/visualisation_factory.qmd and that the viz_factory  README.md is updated. 
2. Continue to follow ./agents/worfklows/viz_factory_implementation.md and continue the implementation of the viz_factory with the guides (guides/) layer implementation. 
- If you can use the same dataset for testing for all guides (or as many as possible with the same dataset) then this would be an asset to be able to compare their results. 
- For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done.


### Positions implementation 


@Agent: @dasharch Thank you. 
@verify for positions: position_dodge,position_dodge2 position_jitter, position_jitterdodge, position_nudge. 

I think maybe different examples and maybe geom should be used for the tests of :
poistion_fill (here it is said to standardize height of bars : proportionality  so the example should show that), position_stack (bar side by side withtout stack and then top of each other after stack - I think either its not working or the example is not appropriate), I just do not think the examples are nice. You can remove the difference in coulour if necessary but 2 colour fills are good. Also maybe try the position_dodge2 with a boxplot as it is said to work with a boxplot?  



@Agent: @dasharch @verify thank you excellent 
 continue to follow ./agents/worfklows/viz_factory_implementation.md . You are now starting the implementation of the viz_factory positions (positions/) layer. Please use at least 2 different colour eg. point colour and fill colour for the tests (it is easier for the user to see the effect of the implementation). Implement the positions one by one. Perfect if you can use the same dataset for testing for all of them, then it would be an asset to be able to compare their results. For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done. 

--- 
@Agent: @dasharch - That is likely correct. 
So I want to slightly modify the testing strategy for the positions implementation. I would like you for each position to produce 2 plots. One without applying any position (so the default one) and one with the position applied.  And I would like you to present those 2 plots side by side on the sample plot. Please agment each manifest file to account for this new testing strategy. The produce the new plots so I can verify the result. 


---


@Agent: @dasharch @verify thank you excellent 
 continue to follow ./agents/worfklows/viz_factory_implementation.md . You are now starting the implementation of the viz_factory positions (positions/) layer. Please use at least 2 different colour eg. point colour and fill colour for the tests (it is easier for the user to see the effect of the implementation). Implement the positions one by one. Perfect if you can use the same dataset for testing for all of them, then it would be an asset to be able to compare their results. For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done. 

### Coordinates implementation

@Agent: @dasharch @verify Excellent. Should we check if there is any update of plotnine build ? the documentation that I have is recent. We might not be using the last build.

@Agent: @dasharch @verify Excellent
1. Please ensure that all the facets implementation is documented in ./docs/workflows/visualisation_factory.qmd and that the viz_factory  README.md is updated. 
2. Continue to follow ./agents/worfklows/viz_factory_implementation.md and continue the implementation of the viz_factory with the coordinates (coords/) layer implementation. 
- Continue by implementing the remaining facets one by one.
- If you can use the same dataset for testing for all coordinates systems (or as many as possible with the same dataset) then this would be an asset to be able to compare their results. 
- For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done.
- Note that we will use cartesian as default coordiante system (if not specified in the manifest)


### Facet implementation 

@verify Excellent, thank you. Please mark facet_grid as successfull. Continue to follow ./agents/worfklows/viz_factory_implementation.md and use the theme_bw for the rest of the facet layer implementation. Continue by implementing the remaining facets one by one. Perfect if you can use the same dataset for testing for all facet tests, then it would be an asset to be able to compare their results. For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done.


---

@Agent: @dasharch 
1. The development of the facets facet_wrap and facet_null are @verified and can be marked as doned and documented. 
2. However, facet_grid is still not satisfactory. The user removed all the plot to ensure that it is not due to non writing of the file, but in the plot the user openeed, then panels were not visible. Please restart facet_grid implementation. The user will verify the result.





---


@Agent: @dasharch 
1. Please document the Root Cause and Resolution (append it) to the file ./docs/appendix/viz_factory_rationale.qmd. 
2. I need to understand more about how your solution works, but indeed it seems that you found a solution for facet_wrap. Remember plot factory has to be data agnostic and the manifests are the source of truth for the implementation (wrapping columns are defined in the manifest). 
3. It seems however that your solution is not implemented in facet_grid and facet_null OR is it maybe the usage of a different theme that do not allow correct visualisation of the panels ? Please review implementation and fix it.

---


@Agent: @dasharch -

Maybe use a different theme (eg- grey theme)
 The development of the facets is not sucessfull. The grid pannels do not appear on the plots. Please restart with the facet implementation, with the first plot. The user will verify 


---

@verify it seems very good BUT can you explain why the names and grouping deviate from the list of task initially provided ? did the actual implementation differ from the provided documentation ? Is so could you provide your reasoning and integrate it (append it) into the documentation appendix file to  ./docs/appendix/viz_factory_rationale.qmd. Please also 
add the list of the taks that were to be implemented and were not - we might have to return to it at a later stage of app development. 

and the updated list of tasks ? 


### Themes implementation 
@verify very good - please continue and implement next component   

@verify 
1. excellent, thank you. Note user renamed the appendix file to viz_factory_rationale.qmd and itegrated it into the documentation 
2. continue to follow ./agents/worfklows/viz_factory_implementation.md . You are now starting themes implementation. Implement the themes one by one. Perfect if you can use the same dataset for testing for all of them, then it would be an asset to be able to compare their results. For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done.  

---
@verify very good - continue to follow ./agents/worfklows/viz_factory_implementation.md . We are now starting 
to implement the scales  - following the same logic as the geoms and implement next component   


@verify thank you excellent. Please continue to follow ./agents/worfklows/viz_factory_implementation.md. Implement the rest of the scales: one by one. For each perform the following steps implementation, testing, plot produced, task update, then move to the next task. The user will come to verify when this is done.  

----
@verify it seems very good BUT can you explain why the names and grouping deviate from the list of task initially provided ? did the actual implementation differt from the provided documentation ? 

---

@Agent: @dasharch - DOCUMENT, MARK DONE, AND PROGRESS TO NEXT GEOM.

1. **Documentation (Artist Law / Violet Law)**:
   - Update './libs/viz_factory/README.md' and the specific documentation : ./.docs/workflows/visualisation_factory.qmd. 
   - Add 'geom_point' (src/geoms/core.py).
   - Include a 'Usage' example using the exact YAML structure from 'geom_point_test.yaml' (import the yaml file in the qmd file - rule: no code duplication).

2. **Task Management**:
   - Open './.claude/tasks/tasks.md'.
   - Mark '- [x] geom_point' as completed.
   - Identify the next incomplete Geom on the list (e.g., geom_line or geom_bar).

3. **Next Implementation (Evidence Loop)**:
   - Search './EVE_WORK/reference/plotnine_api_context.md' for the signature of the NEXT geom.
   - Implement/Register it in the appropriate 'src/geoms/' file.
   - Create the Test Triplet in './libs/viz_factory/tests/test_data/':
     1. '{next_geom}_test.tsv'
     2. '{next_geom}_test.yaml' (pointing to its .tsv)
     3. Run 'test_runner.py' to produce 'tmp/USER_debug_{next_geom}.png'.

HALT for @verify: Show the updated tasks.md and the new PNG artifact.

--- 

@Agent: @dasharch - DIRECTORY RECHECK, PURGE & VIZ FACTORY INITIALIZATION.

DIRECTORY RECHECK & SURGICAL CLEANUP
1. **Audit**: Scan './libs/viz_factory/tests/' and './libs/viz_factory/src/'.
2. **Keep**: Any existing directory structures that align with: geoms/, scales/, themes/, facets/, coords/, positions/, guides/.
3. **Purge**: Delete any files that do not fit the new 'Data-Manifest Coupling' standard (e.g., old standalone python test scripts like 'debug_viz.py' or 'test_plotnine.py' that aren't part of the new 'test_runner.py' logic).
4. **Result**: The 'tests/' folder should only contain 'test_data/' and the new 'test_runner.py' once completed. 



---


cd tmp/
../.venv/bin/python ../libs/viz_factory/tests/test_runner.py ../libs/viz_factory/tests/test_data/geom_point_test.yaml


@Agent: @dasharch - SYSTEM UPDATE & VIZ FACTORY ARCHITECTURE (Data-Manifest Coupling).

PART 1: SYSTEM UPDATE (Hard Requirement)
1. Open './.claude/docs/rules_behavior.md'.
2. Append the following 'Artist Law' section exactly:

### 📜 Artist Law: The Evidence-Driven Visual Contract
- **No Implementation without Evidence**: A component is not 'implemented' until it passes a standalone test.
- **Data-Manifest Coupling**: Every component test MUST consist of a triplet in './libs/viz_factory/tests/test_data/':
    1. `{component_name}_test.tsv`: The raw data (Tab-Separated).
    2. `{component_name}_test.yaml`: The manifest (must include a 'data_path' key pointing to its sibling .tsv).
    3. `USER_debug_{component_name}.png`: The resulting artifact in 'tmp/'.
- **Unified Test Runner**: Implementation must include a general test script in './libs/viz_factory/tests/test_runner.py' that can execute any component test by taking ONLY a manifest path as input. (Reference the Transformer library logic for file-based automation).
- **Component Reference**: Use 'Violet Law': 'ClassName (filename.py)' for all documentation.

3. Commit this change before proceeding.

PART2: Verify the implementation of geom_point and ensure the implementation logic and rules are followed

# Refining instructions 

Please improve this prompt so I we can start the implementation of the viz factory.

We will start to implement each geom one by one (follwoing the order in the 
./.claude/tasks/tasks.md file). 
Process : implementation 
Invidual tests for each geom (data, manifest everything must be created in the same go) must go in ./.libs/viz_factory/tests/test_data/

We follow the same logic as the transformer lib wrangler implementation. We allow recognizing the geom by {geom_name}_test.py and {geom_name}_test.yaml ... 

Expectations of results if possible. If require eg a minimum eg theme mapping osv for the geoms, it would be nice to be able to use the same for all the tests .

output should be verifyied byt the user -> tmp/user_debug_plot.png for example 

If there is need of debug, the documentation for all layers is in ./EVE_WORK/reference/plotnine_api_context.md 
which can be searched to find the code for the different layers components.



SPARMVET_VIZ Antigravity Specialist
Custom Gem
SPARMVET_VIZ Antigravity Specialist said
This strategy establishes the foundation for the Artist Pillar by aligning the Viz Factory (viz_factory.py) architecture with the complete "Grammar of Graphics" layers found in the Plotnine source code.


3. Implementation Protocol (The Prompting Loop)
For every geom in the list, I will generate a specialized prompt for @dasharch that follows this contract:

Contract: Define the mapping and params dictionary schema for the manifest.

Implementation: Register the component in libs/viz_factory/src/geoms/.

Validation Data: Generate a minimal synthetic Polars LazyFrame suited for that geom.

Verification: Materialize a plot to tmp/ for human review.


---

@Agent: @dasharch - SYSTEM UPDATE & VIZ FACTORY INITIALIZATION.

PART 1: SYSTEM UPDATE (Hard Requirement)
1. Open './.claude/docs/rules_behavior.md'.
2. Append the following section exactly:

### 📜 Artist Law: The Evidence-Driven Visual Contract
- **No Implementation without Evidence**: A component (geom, scale, theme, etc.) is not 'implemented' until it passes a standalone test using a local '.py' data generator and a '.yaml' manifest.
- **Verification Artifacts**: For the visualistation factory: Every test must output a high-resolution PNG to './tmp/' named 'USER_debug_{component_name}.png'.
- **Component Reference**: Documentation must strictly follow the 'Violet Law': 'ClassName (filename.py)' when describing layers.
- **Standardization**: All individual tests must use a shared 'test_base_theme.yaml' to ensure aesthetic consistency, allowing focus on functional logic.

3. Commit this change to the ruleset before proceeding.



--- 
@Agent: @dasharch - INITIALIZE VIZ FACTORY & IMPLEMENT FIRST GEOM (Following Artist Law).

**MANDATORY RULE (Artist Law)**: No component is complete without an Evidence Loop. Each implementation MUST include a test data script (.py), a test manifest (.yaml), and a materialized PNG in 'tmp/'.

1. **Verify Library Base Setup**:
   - Ensure './libs/viz_factory/src/' has subdirectories: geoms/, scales/, themes/, facets/, coords/, positions/, guides/.
   - Verify implementation of 'registry.py' with the '@register_plot_component' decorator.
   - Verify implementation of 'VizFactory (viz_factory.py)' core logic:
     * Accept (dataframe, manifest_dict, plot_id).
     * Materialize Polars LazyFrame to Pandas [ADR-010].
     * Initialize 'ggplot' with 'mapping' and pipe 'layers' from the registry.

2. **Standard Test Environment**:
   - Create './libs/viz_factory/tests/test_data/'.
   - Create a 'Standard Theme Mapping' (e.g., theme_minimal) to be reused across all geom tests to ensure consistency.

3. **Geom Implementation (Target: geom_point)**:
   - Search './EVE_WORK/reference/plotnine_api_context.md' for 'geom_point' signatures and parameters.
   - Implement and register 'geom_point' in './libs/viz_factory/src/geoms/core.py'.
   - Ensure naming is strictly functional (e.g., 'geom_point').

4. **The Evidence Loop (Validation)**:
   - Create './libs/viz_factory/tests/test_data/geom_point_test.py' (Polars generator).
   - Create './libs/viz_factory/tests/test_data/geom_point_test.yaml' (Manifest using geom_point + base_theme).
   - Generate the plot and save to 'tmp/USER_debug_geom_point.png'.

5. **Verification**:
   - Save the resulting plot to 'tmp/USER_{{geom_name}}_test_plot.png'.
   - LOG: Display the applied manifest and the successful registration of the component.

HALT for @verify: 
   - Show the 'tmp/USER_{{geom_name}}_test_plot.png' and wait for validation before proceeding to the next geom in tasks.md.


## Sanitize with factory, prepare implementation plan


@Agent: @dasharch - INITIALIZE VIZ FACTORY (Artist Pillar).

1. Library Setup:
   - Verify/Initialize ./libs/viz_factory/src/ and ./libs/viz_factory/tests/.
   - Ensure pyproject.toml exists and is installed in 'Editable Mode' (-e) [ADR-011].
   - verify existing files in the viz_factory directory and make sure they are aligned with the new modular rule files (and inspect their functions).

2. Core Implementation - VizFactory (viz_factory.py):
   - Implement the '@register_plot_component' decorator in 'registry.py'.
   - Logic: The factory MUST accept (dataframe, manifest_dict, plot_id).
   - Manifest Standard: Use 'Dictionary-for-Names' (plot_id) and 'List-for-Layers'.
   - Mapping: Implement the 'data-agnostic mapping' block (aes) as defined in the vision.

3. Module Organization (Subdirectories):
   - Create and initialize: ./geoms/, ./scales/, ./themes/, and ./facets/.
   - Violet Law: Ensure each directory has a __init__.py that auto-registers components.
   - Initial Components: Register 'geom_boxplot' (geoms/core.py) and 'theme_violet' (themes/violet.py).

4. Data Hand-off (ADR-010):
   - Ensure the factory performs the '.collect().to_pandas()' conversion ONLY at the final moment of Plotnine initialization [rules_runtime.md].

5. Verification Script - debug_viz.py:
   - Create './libs/viz_factory/tests/debug_viz.py' following the 'debug_' convention.
   - Evidence Loop: Materialize a test plot to 'tmp/USER_debug_plot.png' and HALT.

6. README & Standards:
   - Update './libs/viz_factory/README.md' using the 'Violet Component' standard.
   - Document the 'Filtered vs. Anchor' logic for state management.

HALT for @verify:
   - Provide the Inventory of registered plot components and the first materialized 'tmp/' plot.

## Workspace standard rules refactor 

so now we need it to make a pass at : 


./.claude/knowledge/architecture_decisions.md
./.claude/knowledge/project_conventions.md
./.claude/workflows/verification_protocol.md"
To ensure that they do not contain rules that should be integrated into the new modular rule files.

Moreover, the agent yesterday started to create new directories. I moved that into ./.claude/backups 
We need to make sure that the all information is either captured in the new modular rule files or in the corresponding files that the normal aligned agent should be using in the following directories: ./.claude/knowledge, ./.claude/plans and ./.claude/tasks 


@Agent: @dasharch - POST-REORGANIZATION AUDIT & CLEANUP.

The modular rule files are created, but we must now verify 'Logic Density' and remove redundancy.

1.  **Re-Check Modular Rules**: Compare 'rules_runtime.md', 'rules_wrangling.md', 'rules_behavior.md', and 'rules_aesthetic.md' against:
    - ./.claude/knowledge/architecture_decisions.md (Check ADR-013/014 integration)
    - ./.claude/knowledge/project_conventions.md (Check Type Selection Guide)
    - ./.claude/workflows/verification_protocol.md (Check @verify Evidence Loop)

2.  **Audit Backups**: Read everything in './.claude/backups'. 
    - Is there any logic or task state there NOT present in the active ./.claude/ or ./.claude/ directories? 
    - If YES: Move it to the correct authorized file now.
    - If NO: Prepare the directory for deletion.

3.  **Redundancy Purge**: Once logic is verified in the Rules, suggest which sections of the original Knowledge/Workflow files should be deleted or simplified to prevent 'Double-Rule Drift'.

4.  **Violet Law Enforcement**: Confirm all newly written rules use 'Component (filename.py)'.

HALT and provide a 'Gap Report'—list what was missing and where you moved it.

--- 

> the workspace standard is too large - so we need to refactor it to be more modular.

@Agent: @dasharch - PRE-MIGRATION INVENTORY - CONTEXT INJECTION & REFACTOR.


1. Read the user backup of the latest workspace_standard in './EVE_WORK/daily/2026-03-28/workspace_standard_backup.md'. 
We need to refactor the workspace rules and standards to be more modular.

2. To prevent architectural drift during the modularization of our rules, you must create a temporary file: './.claude/rules/migration_inventory.md'.

3. **Map Every Component**: Document the transition of Sections 1-17 of 'workspace_standard.md' and the 'ANTIGRAVITY_GEM_context.md' system state into the following 4 sub-files in the .claude/rules/ directory:
    - rules_runtime.md
    - rules_wrangling.md
    - rules_behavior.md
    - rules_aesthetic.md

2.  **Incorporate External Context**: Ensure the 'Data Type Selection Guide' (from project_conventions.md) and the 'Evidence Loop' (from verification_protocol.md) are mapped as mandatory inclusions.

3.  **Halt for Approval**: Once this file is written, present it as a table and HALT. Do not begin the actual refactoring or file creation until I provide the @verify command.

4.  **Violet Standard**: All file/class references in the inventory MUST follow 'ClassName (filename.py)'.

















---- 

2. Create './.claude/rules/rules_runtime.md' and include these SYSTEM TRUTHS:
   - IDE Version: Antigravity v1.19.6 (STABLE/PINNED).
   - OS: Fedora 43 KDE (Velocifero Compute).
   - Update Policy: 'update.mode: none' (DNF pinned).
   - VENV: All execution MUST use './.venv/bin/python'. No path hacking (sys.path).

3. Create './.claude/rules/rules_wrangling.md':
   - Include Section 8 (Decorators), Section 9 (Transformation), and Section 12 (ADR-013 Manifest Contract).
   - Pull the 'Data Type Selection' and '1:1:1 Naming Law' from `./.claude/knowledge/project_conventions.md` into `rules_wrangling.md`.

4. Create './.claude/rules/rules_behavior.md':
   - Include the @verify Protocol: Generate Test Data/Manifest -> Execute CLI -> Materialize to tmp/ -> df.glimpse() -> HALT.
   - Include the 'Halt & Verify' Protocol for rule changes.
   - Pull the 'Evidence Loop' from `./.claude/workflows/verification_protocol.md` into `rules_behavior.md`.


5. Create './.claude/rules/rules_aesthetic.md` (Violet Law, Documentation, Quarto/Mermaid). 



6. **Clean Up**: 
    - Once the new ./.claude/rules/ directory is verified, update the main workspace_standard.md to be a 'Master Index' that mandates reading these sub-files.
    - Reference all components using the Violet Law: ComponentName (file_name.py).
    - Strip the old monolithic sections.
    - Ensure no component are missing - only reorganized.
    - Transform it into a 'Master Authority Index' that explicitly points to these sub-rulebooks.
    - Apply the Violet Law: ClassName (filename.py) to all descriptions.

HALT and confirm when the local rule directory is the new 'Source of Truth'.






