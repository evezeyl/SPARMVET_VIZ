# Controls on the merged head of dev `a538eca2` (the big recipe change merged), 2026-11-19, reviewer; digest by the coordinator

Outputs of every run: `tmpAI/coordinator/controls_merged_2026-11-19/`. Head and clean tree checked at start and end (RAN).

## Verdict of the reviewer: DO NOT PUSH YET: one test file fails for a reason in the test
- `app/tests/test_tier_decides_filter_form.py`: 9 setup errors. Cause (READ): the test stages a recipe with the group key `label`; the merged format refuses it (`[G01] label is not a key of this element. Tip: renamed ui_label`); no tab appears. The file was written before the merge and not adapted. Not flaky (same in three runs). Repair: test only (running, branch `task/tier-test-label`).
- Consequence until repaired: no passing browser test of "the viewed tier decides the filter form" on the merged head.

## Everything else PASSED (RAN)
| Run | Result |
|---|---|
| qa flags through the Bootloader | audit, comparison, sessions, export, Blueprint, agent switch (backend disabled), recipe edit, gallery, test lab, ingestion flags ON; testing_mode on; ghost save OFF |
| App import | OK |
| Headless, `-n 4` | 11246 passed, 5 skipped, 31 xfailed, 0 failed, 544 s (golden baseline inside) |
| 27 browser files, qa, `-n 4` | 240 passed, 3 skipped, 1 xfailed, 1 failed (flaky, below), 9 errors (the tier file) , 877 s |
| All eight setups start | 9 passed |
| Pictures | 50 identical, 1 known changed row (the empty orphan `experimental/test_logic.yaml`) |
| Tier file with `test_shiny_step_order.py`, `-n 2` | no clash; step order passes |

## One flaky test under `-n 4`
`test_shiny_smoke_blueprint.py::TestBlueprintPlotOpen::test_every_plot_of_the_demo_recipe_opens_with_its_mapping_its_layers_and_its_data`: once showed the layer list of the previous plot (`3. coord_flip` instead of `3. labs` for `qa_aggregated_no_key`); passed alone (once). Reasoned: a wait missing in the test, or Blueprint showing the previous plot's stack for a moment. To look at (task).

## Small audits, compared with the known state (not gates)
old-words: exit 1 (as known). Document links: 11 problems (dev was 19 before the merge). UML audit: fails as known (PKG-TIERS; a missing test name `test_audited_rows_and_drops_are_exported`).

## Not covered
Ghost save (off in qa); setups other than qa only started; browser files ran in parallel only; the flaky test rerun once; the Quarto render of the export.
At start-up the Bootloader removed 28 stored tables of another cache version (expected after the engine change).
