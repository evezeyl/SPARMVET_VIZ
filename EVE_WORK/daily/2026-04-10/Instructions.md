For UI see 2026-04-09

## Testing the template manifest

"@Agent: @dasharch - TASK: MODULAR ST22 PIPELINE BURN-IN (PHASE 12-B).

Context:

- Main Manifest: ./assets/template_manifests/1_test_data_ST22_dummy.yaml.
- Rule: Follow ADR-012 (Staged Assembly) and ADR-034 (Diagnostic Layer).
- Output Path: tmp/TEST_MANIFEST/<subdir>.

Objective:

1. Stage 1 (Tier 1 Atomic): Iterate through every !include in the master manifest. Use 'debug_wrangler.py' to process each dataset.
   - Output: Save glimpsed TSVs to tmp/TEST_MANIFEST/tier1_atomic/.
2. Stage 2 (Tier 1 Anchor): Use 'debug_assembler.py' to join all Tier 1 outputs with 'metadata_schema.yaml' and the 'VIGAS-P' external data.
   - Check: Ensure join keys are primary and non-null.
   - Output: Save the joined Anchor to tmp/TEST_MANIFEST/tier1_anchor/.
3. Stage 3 (Tier 2 Branching): Execute the 'summarize' and 'group' logic for 'Quality Control' vs 'Results'.
   - Output: Save branched views to tmp/TEST_MANIFEST/tier2_branches/.
4. Error Audit: If any stage fails, use the 'Ingredient Checker' to suggest the fix for the manifest.

Verification:

- For each stage, output a 'df.glimpse()' and a confirmation of the file path.
- Confirm the 'VIGAS-P' data is successfully integrated into the 'Results' branch.

HALT for @verify after each Stage to allow for manual inspection."

## Old

---
ok, now I want the agent to help me make complete the manifest for the test data: ./assets/template_manifests/1_test_data_ST22_dummy.yaml (and all include files that are in the subfolder
./assets/template_manifests/1_test_data_ST22_dummy). It must be as meaningful data cleaning, wrangling and create as useful visualisations as possible for the user (meaningfull for the user). The agent should at least for one dataset create a branching of the tier 1 data to create different plots.
Each dataset should be merged with the existing metadata file (both primary dataschema and additional data schema). There should be the possibility to add the categories to the plots eg. quality control vs results and this needs then to be visible in the ui.

The data that are corresponding to this manifest are in the folder: ./assets/template_manifests/
within the subfolder 1_test_data_ST22_dummy and 2_VIGAS-P_ST22_dummy (which should be considered as additional data that is added into the manifest, as it has not been produced by the same pipeline)

I created a copy (.tar.gz of the current state, so If I need to implement some changes for the real dataset then I can always go back to the current state)

Note that I have also created a new template persona: "pipeline-static_template.yaml", a very basic ui, so we can start testing step by step. (only the export function is toogle) - all the rest will be static (when we are ready to test the ui manually we will start with this persona)

---

Good - now that we have the gallery implemented, we need to verify that the option "gallery " and "developper" can be turned off depending on the persona.

----

For the gallery view and submission - I would like to have some precision and adding some features.
I would like to make it possible for us to have a little description associated to the gallery viewer:

- we have the gallery plot view in a tab, where we can view the associated tier 1 and tier 2 data frame, and the
yaml recipe to do that. I would like to have that in the left side of the panel. On the right side of the panel I would like to have the possibility of having a description of plot/and data. This could for example read from a markdown file in the same folder as the recipe. The structure of the markdown file could be something like this:
- when you can use / do not use this plot (most suited for)
- data schema : your data tier 1 must be eg. categorical, numeric ....
- data tier 2 applies those transformations to be able to create this plot
- what the plot is showing / assumptions - problems and other commentts

So basically we would need a mandatory template to be filled whith the descriptions of the data tier 1, data tier 2 and the plot itself. But the rest need to be flexible

And this could be rendered (nicely formated) in the right side of the panel when we view the plot in the gallery.
Can we add that to the decisions development plan / architecture and tasks list ? (ask questions if you do not understand what I mean)

"@Agent: @dasharch - SYSTEM UPDATE: ADR-033 & GALLERY REFINEMENT.

Context:

- User has requested a structured 'Visual Cookbook' extension to ADR-025/028.
- Document this in ./.claude/knowledge/architecture_decisions.md as ADR-033.

Objective:

1. Update Implementation Plan: Add 'Phase 14-B: Educational Gallery Engine' to ./.claude/plans/implementation_plan_master.md.
2. Update Tasks: Add the following under Phase 14 in ./.claude/tasks/tasks.md:
   - [ ] Build 'recipe_meta.md' parser in app/modules/gallery_viewer.py.
   - [ ] Implement 50/50 Split-Pane Gallery UI (Technical Left / Educational Right).
   - [ ] Enforce mandatory Markdown template for Gallery submissions.
3. Code Scaffolding: Create a 'recipe_template.md' in assets/gallery_data/ with the four mandatory headers requested (Suitability, Schema, Tier 2, Interpretations).

Logic: The description pane must be rendered nicely (using shiny::markdown) and stay visually distinct from the 'Theater' (ADR-029a).

HALT for @verify once the plan and task files are updated."
