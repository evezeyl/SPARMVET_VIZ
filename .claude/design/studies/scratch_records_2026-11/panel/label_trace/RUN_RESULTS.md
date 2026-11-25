# Browser run results (PARTIAL: first run stopped at 13:20; second run added at 14:55, see the end)

Run on `dev`, main folder, app features `developer`, Chromium 1600x1250, port 8731. Pictures are in `shots/`.

## FIRST: the join-key check (done)

**Dropping `sample_id` through the audit is ACCEPTED, not blocked.** The code reading was right.
- Plot `qc_reads_horizontal_barplot` (join `QC_Reads_Anchor`) and plot `mlst_bar` (join `MLST_with_metadata`): My view, deselect `sample_id`, press "Audit drops (1)". The dialog "Drop 1 column(s) - choose scope" opened. No "Cannot drop join key column(s)" message, no notice at all. With a reason and Apply: "audit entry(ies) added" and "audit steps applied".
- After Apply on the QC plot, in My view: the data preview lost the column `sample_id`; the plot shows a red "Render error: ... the aesthetic 'x' is mapped to the column 'sample_id', which the data does not have" and an entry in the Alerts panel. On the MLST plot the plot did not use `sample_id`, so nothing broke: the column was gone from the table, with no warning.
- Removing the audit step (trash) and Apply restored the column and the plot (both plots).
- Server log: no line about the drop (the message would be a screen notice only; none was shown). Pictures: 11_qc_after_click, 12_qc_drop_pending_with_reason, 13_qc_after_apply, 15_qc_after_drop_applied_myview, 15_mlst_*, 16_*_after_removal.

## Other special-care checks

| Check | Code reading expected | SEEN | Picture |
|---|---|---|---|
| Data preview: names or labels? | names | NAMES. Headers `sample_id`, `total_reads`... on QC_Reads_Anchor; and also `sample_id`, `source`... on ST22_Anchor, which has a join `labels` list ("Sample ID"). The column list box also shows names. Eve's belief (labels) is not what the app does. | 05_preview_qc, 06_preview_st22 |
| Plot axis/legend titles use the column label when `labs` is empty? | no | NO. QC plot: axes `sample_id`, `total_reads`, legend `proportion_1` (labels "Total Reads", "Primary Proportion" exist). MLST plot: `sequence_type`, `count`, `country`. Where typed in `labs` the typed text shows ("Sample Id", "Count", "Selected Virulence Genes"; phenotype plot "Resistance Score (...)", "Metric Value"). Legend "ST" on the phenotype plot is the column name. | 17_p1..p4, x_virulence_full |
| Blueprint: Name typed and saved on a copy: does the banner change? | no | NOT RUN. Seen only: the Name box is EMPTY while `info.label` is "ST22 Dummy Dataset"; the form has Name, Description, Author, Version, Tags (no label field). | 20_bp_info_and_groups |
| Copy test: remove `info.label` | no banner | NOT RUN (copy A prepared, app on it did not load in time: the recipe selector was empty after start; not diagnosed) | - |
| Copy test: change one plot label | tab changes | NOT RUN (copy A prepared) | - |
| Copy test: remove one plot title | no title | NOT RUN (copy A prepared) | - |
| Join: change only a join label, recomputed? rows equal? | recomputed, same rows | NOT RUN (copy B prepared) | - |
| Join: unused ingredient, any message? | none | NOT RUN (copy B prepared) | - |
| `QA_fanout_exhibit` plot: warning about multiplied rows? | none | NONE. Plot shows its typed title and subtitle ("Inflated on purpose (issue 68)"); Alerts hold only 2 "recipe loaded" lines; no warning. | 32_fanout_plot |

## LABELS.md checks (what was reached)

| Item | Expected | SEEN |
|---|---|---|
| Banner title/subtitle | `info.label`, `info.subtitle` | seen: "ST22 Dummy Dataset" and subtitle (01_banner) |
| Recipe selector | file name | seen: file names only (list in INDEX) |
| 5 group tabs | group `label` | seen, with emoji. The QA group's long label wraps onto a second line of the tab strip. |
| 17 plot tabs | plot `label` | seen (2, 1, 5, 1, 8 per group), 03_group_1..5 |
| Data to show / Plot to show / badge | - | seen; badge "Viewing: Result" plus "T2=T1" on joins without tier 2; "Viewing: My view" |
| Info panel | all info keys | seen: label, contact, subtitle, category, description, version (04_info_panel; contact hidden) |
| Pipeline Audit, join with tier 2 / without | "[Tier 2]" lines / "No Tier 2 steps defined" | seen. Collection shows the join id. Tier 2 lines read like "polars_with_columns: polars_with_columns" (name twice). 10_audit_panel_pending, x_home0 |
| Filter dialog "Apply to" | plot labels | seen: labels ("Assembly Quality Dotplot", "Miaou"...). 09_*. |
| Audit panel heading | plot id (other things 3) | seen: "My Adjustments (Tier 3) - mlst_bar", "No T3 adjustments for qc_reads_horizontal_barplot yet": the plot ID, not the label |
| Audit stack's own "Apply to" (Plot Style dialog) | id in title case | NOT REACHABLE: the Plot Style panel is not mounted in HOME |
| Filter column box | names | names with the type, e.g. "year [Float64]" |
| Blueprint groups/plots list | labels | seen: labels |
| Blueprint join list (`dataset_pipeline_selector`) | "<id> - join" | seen as "<id> - join" (text "FastP_with_metadata - join") |
| Tube map nodes | ids; plots? | tables and joins: ids ("Metadata" for `metadata_schema`, "X Wrangle"). PLOTS: the plot id in title case ("Mlst Bar", "Amr Heatmap", "Qa Amr Genes Per Sample"), NOT the plot label. Six arrows into `ST22_Anchor`: confirmed (FastP, ResFinder, MLST, VirulenceFinder, APEC_STEC_virulence_genes, metadata_schema) | 21a..c |
| Lineage rail | ids | seen: ids ("MLST wrangling", "MLST_with_metadata join", "mlst_bar plot_spec") | 24_bp_interface_tab_plot |
| Field cards | label line | seen: "label: Sample ID", "source col: ...". `Summary`: 7 of 11 fields have a label; `genotype`, `phenotype`, `cge_phenotype`, `plasmid` show only the source column. A join card shows ids and ingredients only (no label, no `labels`). | 25_bp_fields_* |
| Gallery | own names | seen: 34 examples, names from the gallery files (30_gallery_list) |
| Export report | plot headings | headings and captions are the plot FILE title ("Reads Quality & Taxonomy Proportion"), NOT the plot label; the caption adds "dataset: `<join id>`". Report title: "Results Report - 1_test_data_ST22_dummy" (file name). |
| Export README | - | "Data analysis recipe name: 1_test_data_ST22_dummy" (file name); Contact: <contact>; "Tiers : T1" although T2 files exist |
| Export run record keys | - | _about, generated, data_batch_hash, engine_fingerprint, containerized, image_ref, git_commit, release_version, contact, contact_source (recipe (info.contact)), software_versions, data_source_paths, seeds_per_plot, seed_source_per_plot, seeds_per_layer, seeds_added_to_recipe |
| Export table files | `<join id>_T1.tsv` (JOINS 10) | DIFFERENT: `<join id>/T1_data.tsv` and `<join id>/T2_data.tsv` (T2 only where the join has tier 2) |
| Export lineage file | plot labels | plot nodes use the plot LABEL ("MLST Bar", "Miaou"); joins use the join id; no join label |

## JOINS.md checks 1-12

1 plot tabs show plot labels, no join named: seen. 2 "T2=T1" badge: seen. 3 preview header on a join plot: column names only, no join name or label: seen. 4 "Collection: <join id>", only violet tier-2 lines, join step not listed: seen. 5 key drop: ACCEPTED (see top). 6 fanout warning: none. 7 Blueprint join list "<id> - join": seen. 8 tube map ids, six arrows: seen. 9 lineage ids: seen. 10 export files: different (above). 11, 12: not run.

## Not checked
Copy tests (3 + 2), the Blueprint Name save test, the report headings after a title removal, long recipe selector list as a picture (options are in INDEX), field card picture of a join with a label.

## Left on disk
- `copies/` : recipes_A, recipes_B (edited copies), deploy_A.yaml, deploy_B.yaml, empty cache/user folders. Copy A app: stopped.
- `export/20261118_131640_labeltrace/` the unpacked bundle (its run record and README hold the contact address; do not publish).
- `run/` scripts and logs; `facts_*.json` (contact removed).
- `tmp/UI_TEST/user/`: the app wrote `assembly.json` for several session folders, a draft `_blueprint_drafts/76964f0f81b1_1_test_data_ST22_dummy.json`, and `anchors/` parquet files; the six `t3_20261118T12*.json` files I created were deleted. Anything else there pre-existed or is rewritten by any app start.
- A process with PID 583839 is not mine.


## Second run (2026-11-18, 14:55 by the clock)

Run on `dev` (main folder), app features `developer`, Chromium 1600x1250, port 8751. Recipes only on copies; the deployment files `copies/deploy_A.yaml` ... `deploy_F.yaml` point the recipe folder at the copies. Shipped files unchanged (`git status` clean). The app wrote its files only under `copies/user_*`.

### Why copy A showed an empty selector
Copy A had `info.label` removed. The checker refuses it: `1_test_data_ST22_dummy.yaml: info: [I01] info.label is required. Tip: add label` (verified with `validate_data_analysis_recipe` and in the app). HOME shows "No data analysis recipes yet", the sentence "The data analysis recipe '1_test_data_ST22_dummy' failed its checks ... HOME does not use it", and the contact of the deployment. The selector has no option; the "Data analysis recipe Choice" panel lists the recipe as unavailable. Pictures 50A, 51A. Facts: `run2/facts_a.json`.
Side note: in the full-folder copies, `1_Abromics_general_pipeline` is refused because its include paths are relative (`../../assets/ref_data/...`) and the copy is one folder deeper. An artefact of copying, not an app fault.

### a. Remove `info.label`
Refused by the checker (I01). HOME: no banner, no recipe, no tabs; only the reason. Picture 50A, 51A.

### b. Plot label "XX" (copy C, plot `mlst_bar`)
HOME plot tab list of the Virulence group: AMR Heatmap, Virulence Bar, **XX**, Year Distribution, Virulence Variants (picture 53). Export report (`run2/export_C_report.qmd`, run on all plots): heading `### MLST Sequence Type Distribution by Country` (the plot file title), figure caption the same title plus "dataset: MLST_with_metadata". "XX" appears in two places only: the lineage diagram node `mlst_bar__plot_spec["XX / plot"]` and the lineage table row `| plot_spec | mlst_bar | XX |`. The heading does NOT change, as expected.

### c. Remove one plot file's `title:` (copy C, plot `year_distribution`)
The picture has no title (54). Report heading: `### Year Distribution`, caption "Year Distribution - dataset: MLST_with_metadata". Code: `export_handlers.py:437,487,1779` use `spec.get("title") or plot_id.replace("_"," ").title()`. The plot label is also "Year Distribution", so the output alone does not separate the two; the code does.

### d. Change ONLY a join label (copy D, join `MLST_with_metadata`: "MLST with metadata" to "MLST with metadata CHANGED-ONLY-LABEL")
The app was stopped, the file edited, the app started again, the MLST Bar plot opened. Stored tables in `copies/user_D/anchors/` (file modification time / key recorded in the file; the key is the first 12 characters):

| stored file | before | after d | after e (see e) | rows before / d / e | content hash |
|---|---|---|---|---|---|
| FastP_with_metadata.parquet | 14:42:07.956 / c4c8dfe88541 | 14:43:06.946 / d7358681f40d | 14:43:57.835 / b531f75fd211 | 42 / 42 / 42 | same (d6b1e0cd) |
| MLST.parquet | 14:42:04.479 / b310b15bbc3b | 14:42:04.479 / b310b15bbc3b | 14:42:04.479 / b310b15bbc3b | 42 / 42 / 42 | same (7bc2989e) |
| MLST_with_metadata.parquet | 14:42:13.654 / c4c8dfe88541 | 14:43:12.432 / d7358681f40d | 14:44:03.175 / b531f75fd211 | 42 / 42 / 42 | same (bc765d50) |
| MLST_with_metadata__T2.parquet | 14:42:13.676 / 3065920123d1 | 14:43:12.455 / ba5383ecfe25 | 14:44:03.202 / dedf9e0cb143 | 33 / 33 / 33 | same (478daf6f) |
| QC_Reads_Anchor.parquet | 14:42:08.095 / c4c8dfe88541 | 14:43:07.127 / d7358681f40d | 14:43:57.988 / b531f75fd211 | 42 / 42 / 42 | same (233348ea) |
| ResFinder.parquet | 14:42:11.727 / c4c8dfe88541 | 14:43:10.841 / d7358681f40d | 14:44:01.431 / b531f75fd211 | 70 / 70 / 70 | same (17d7acce) |
| ResFinder__T2.parquet | 14:42:11.749 / 0aa93d517c01 | 14:43:10.869 / f83414db980c | 14:44:01.462 / 8dbfb9915014 | 70 / 70 / 70 | same (3e76b235) |

Answer: YES, recomputed. Every stored joined table was rewritten (new time) and the recorded key changed, for the join I touched and for the others too (FastP_with_metadata, QC_Reads_Anchor, ResFinder). The raw table `MLST.parquet` was not rewritten (its key is unchanged). Rows are identical (row count and hash of the content equal before and after). A new session folder was also created (the recipe's file-set hash changed). Cost: a rebuild with identical rows; the change is silent (no message).

### e. Add an ingredient no step uses (copy D, `MLST_with_metadata` gets `- dataset_id: Bracken`)
No message in the checker (`validate_data_analysis_recipe` and `checker_advices`: empty lists), none in HOME (the alert counter stayed "Alerts (2)", no error text on the plot tab), none in the server log. The only WARN in the log is "13 file columns of 'Bracken' are not declared in input_fields", which is the normal ingest message for that table (reasoned: another join, Bracken_with_metadata, loads it anyway; I did not run the pristine recipe to compare). The tables were rebuilt again (keys changed), rows identical (see table, column "e"). Plot opens without error (63).

### f. Blueprint info form "Name"
First finding: Blueprint's recipe list comes from the fixed relative folder `config/data_analysis_recipes/pipelines` (`blueprint_handlers.py:1073`), not from the deployment's recipe folder. The list in a copy deployment pointed to the shipped files. So I ran the app from a scratch project root (symlinks to the repository, own copy of the recipes folder; deleted afterwards) and typed on the copy.
Typed "TYPED IN BLUEPRINT" in Name and pressed "Save to data analysis recipe": message "Data analysis recipe info saved." The key written into the copy is `info.name`. The HOME banner stayed "ST22 Dummy Dataset" (same session and after a page reload) (72, 73). The form's Name box was empty before (the recipe has `info.label`, not `info.name`) (70, 71).
Also: the save rewrote the whole file (`run2/F_before.yaml` and `run2/F_after.yaml`): comments lost (14 lines with `#`, then 2), quotes and wrapping changed, `tags: []` added, 54 `!include` lines kept. Contact address is inside those two files: do not publish.

### g. Recipe selector list
Picture 52: the opened list shows file names (1_test_data_ST22_dummy, 2_test_data_ST22_dummy, 3_test_no_joins, demo_abromics, figshare_integration, stress_test_master). A native list is not drawn by a headless browser, so the list was shown by giving the select a list size; same entries as the select holds.

### Left on disk (second run)
- `copies/recipes_A, _C, _D, _E` (edited copies), `copies/deploy_C.yaml ... deploy_F.yaml`, `copies/cache_*` (empty), `copies/user_C, user_D, user_E, user_F` (files the app wrote: `anchors/`, `_sessions/`, drafts).
- `run2/` scripts, logs, `anchors_*.json`, `facts_*.json`, `export_C_report.qmd` (contact removed), `F_before.yaml`, `F_after.yaml` (hold the contact address).
- `shots/50A` to `73`.
- Not left: the scratch project root (deleted), the app (stopped, PID 981888/952992 gone). `tmp/UI_TEST/user/` untouched by this run (my deployments use `copies/user_*`).
