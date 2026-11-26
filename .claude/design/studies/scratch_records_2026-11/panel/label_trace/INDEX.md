# What you write in the recipe, where it shows (PARTIAL: first run stopped at 13:20; second run 14:55 added the copy tests, see the end; what is still open is listed there)

Plain summary for Eve. Seen in the running app (HOME, Blueprint, Gallery, Export); pictures in `shots/`. Not done in the first run: the three tests on a copy of the recipe and the Blueprint Name test (see `RUN_RESULTS.md`); done in the second run (end of this page). The branch of the big recipe change was not used: its screens cannot run yet.

First: dropping the column `sample_id` through the audit is NOT blocked (on two join plots). The plot can then show a red error. See `RUN_RESULTS.md`.

| What you write (key) | Where it shows | Picture |
|---|---|---|
| `info.label` | HOME banner title; line "label:" in the Info panel | 01, 04 |
| `info.subtitle` | line under the banner; Info panel | 01, 04 |
| group `label` | HOME group tab; Blueprint group list | 03_group_1..5, 20 |
| plot `label` | HOME plot tab; filter dialog list; Blueprint plot list; export lineage file | 03, 09, 20 |
| plot file `title` | title on the picture; report heading and caption | 17, report |
| plot file `labs` x, y, fill | axis and legend titles on the picture (as typed) | 17 |
| input column `label` | Blueprint field cards only | 24, 25 |
| table / join `label` | nowhere (ids are shown) | 21, 24 |
| `info.label` removed | the recipe is REFUSED: HOME shows no recipe and no banner, only the reason | 50A, 51A |
| `info.name` (what Blueprint's "Name" box writes) | NOT the HOME banner; the banner reads `info.label` | 70, 71, 72, 73 |
| plot `label` changed to "XX" | HOME plot tab shows "XX"; the picture title and the report heading do not change; the report's lineage list shows "XX" | 53 |
| plot file `title` removed | no title on the picture; the report heading becomes the plot id in title case | 54 |
| join `label` changed (nothing else) | nowhere on screen; but the stored table is rebuilt (same rows) | no picture, see the second run |

Written in the recipe, shown nowhere (confirmed again in the second run for the join `label`, and an unused join `ingredients` entry is not reported anywhere): table `label`, `description`, `comment`; join `label`, `description`, `labels`; plot `description`, `taxonomy`; group `description` (when the label exists); the column labels in the data preview, the column list, the filter box, the plot axes, the export tables.

## 1. HOME
1. Banner (01_banner): 1 title "ST22 Dummy Dataset" = `info.label` (line 6); 2 subtitle = `info.subtitle` (line 8).
2. Whole screen (01_home_full): 1 title, 2 subtitle, 3 group tabs, 4 "Plot to show", 5 "Data to show".
3. Recipe selector (02): lists FILE names (1_Abromics_general_pipeline, 1_test_data_ST22_dummy, 2_test_data_ST22_dummy, 3_test_no_joins, demo_abromics, figshare_integration, stress_test_master): not `info.label`.
4. Group tabs (03_group_1..5): "Quality Control" (2 plots), "Curiosity plots" (1), "AMR and Virulence" (5), "Cat" (1), "QA canaries (not for publication): ..." (8); each from the group `label` (main file lines 302-366). Plot tabs from plot `label`: e.g. "QC Reads Horizontal Barplot", "Miaou" (lines 306-405).
5. Badge "Viewing: Result" + "T2=T1" (05, 06): typed by the app.
6. Data preview (05_preview_qc, 06_preview_st22): title "Data Preview (max. first 100 rows)" typed by the app; column headers are the column NAMES (`sample_id`, `total_reads`...), also for `ST22_Anchor` whose `labels` list is not used. Column list box (4): names.
7. Filter form (07): the column box lists names with type, e.g. "year [Float64]".
8. Info panel (04_info_panel): label, contact (hidden here), subtitle, category, description, version: all from `info`.
9. Pipeline Audit (x_home0, 10, 32): "Collection: <join id>" (id, not label); "Inherited (Tier 2)": "No Tier 2 steps defined." for QC_Reads_Anchor, or lines like "[Tier 2] modif_filter: modif_filter" for MLST_with_metadata. "My Adjustments (Tier 3) - mlst_bar" uses the plot id.
10. Audit dialog (08, 09, 09b): "Apply to: This plot only / All plots / All plots except..."; the list of plots uses the plot labels.

## 2. Pictures (17_p1..p4, x_virulence_full, 32)
- QC reads: title typed in the plot file; axes `sample_id`, `total_reads`; legend `proportion_1` (column names).
- Virulence bar: title typed in file; "Sample Id", "Count", "Selected Virulence Genes" typed in `labs`.
- Phenotype: title and axis titles typed (`labs`); legend "ST" is a column name; panel names (N50, genome_length...) are values of a column.
- MLST bar: title typed; axes `sequence_type`, `count`, legend `country`: names.

## 3. Blueprint (20, 21a-c, 22, 23, 24, 25)
Info form (20): Name EMPTY (the form reads `info.name`, not `info.label`), Description, Author, Version 1.8. Group and plot lists use labels. Tube map: tables and joins show ids; plot nodes show the plot id in title case ("Mlst Bar"), not the label. Lineage rail (24): ids. Field cards (25): "label: Sample ID" lines; four `Summary` columns have no label.

## 4. Gallery (30)
34 examples; names and column descriptions come from the gallery example files, not from this recipe.

## 5. Export (text excerpts)
- Report title: "Results Report - 1_test_data_ST22_dummy" (file name). Plot headings and captions: the plot file `title` + "dataset: `<join id>`".
- README: "Data analysis recipe name : 1_test_data_ST22_dummy"; "Contact : <contact>".
- Run record keys: _about, generated, data_batch_hash, engine_fingerprint, containerized, image_ref, git_commit, release_version, contact, contact_source, software_versions, data_source_paths, seeds_per_plot, seed_source_per_plot, seeds_per_layer, seeds_added_to_recipe.
- Table files: `<join id>/T1_data.tsv`, `<join id>/T2_data.tsv`. Header of MLST_with_metadata: sample_id, scheme, sequence_type, source, year, country (names).
- Lineage file: plot nodes use plot labels ("MLST Bar", "Miaou"), joins and tables use ids.


## Second run (2026-11-18, 14:55 by the clock)

Same app, same `developer` features, on copies in `copies/` (recipes_A, _C, _D, _E and a scratch project root for Blueprint). The shipped recipe files were not changed (`git status` clean). Pictures 50A to 73 in `shots/`; scripts and raw facts in `run2/`.

Why the earlier run showed an EMPTY recipe selector on copy A: copy A had `info.label` removed. The checker refuses a recipe without it (code I01: "info.label is required"), so HOME does not offer the recipe. The scratch deployment file was fine. See 50A and 51A.

1. Remove `info.label`: the checker refuses the recipe. HOME says "No data analysis recipes yet" and gives the reason and the contact. No banner, no selector entry (50A, 51A).
2. Change one plot label to "XX": the HOME plot tab shows "XX" (53). The export report heading of that plot stays the plot file's title ("MLST Sequence Type Distribution by Country"). The "XX" appears only in the report's lineage table and diagram.
3. Remove one plot file's title: the picture has no title (54). The report heading is the plot id in title case ("Year Distribution"). Careful: that plot's label is also "Year Distribution", so the text alone cannot tell which one the heading uses. The code does: `export_handlers.py:1779` takes the plot file title, else the plot id in title case.
4. Change only a join's label: the stored joined tables are rebuilt. Rows and content are the same. See `RUN_RESULTS.md` for the numbers.
5. Add an ingredient that no step uses: no message anywhere.
6. Blueprint "Name" box: it writes `info.name`. The HOME banner does not change.
7. The recipe selector opened as a list (52): file names, not `info.label`.

Another thing found: Blueprint's recipe list is read from the fixed folder `config/data_analysis_recipes/pipelines` (`blueprint_handlers.py:1073`), not from the deployment's recipe folder. So a deployment with its own recipe folder shows different recipes in HOME and in Blueprint. I tested Blueprint on a scratch project root for this reason.

Another thing found: Blueprint's "Save to data analysis recipe" rewrites the WHOLE recipe file. Comments in the file are lost (14 lines with `#` became 2), quotes and line breaks change, and a `tags: []` line appears. The `!include` lines stayed (54 and 54).

Still not covered (honest list): the audit stack's own "Apply to" (its panel is not mounted in HOME); a picture of a join's field card with a label; the real banner when `info.label` is present but empty (refused earlier than HOME can show it, not tried); Blueprint on `qa` and `standalone` features.
