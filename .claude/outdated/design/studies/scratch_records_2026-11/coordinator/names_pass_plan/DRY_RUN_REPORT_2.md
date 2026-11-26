# Names pass: dry run report, third version (2026-11-22; file DRY_RUN_REPORT_2.md)

## In plain words (written by the builder, on top of the script's own list below)

- 516 changes in 188 files (the second report: 496 in 175). By rule: `info.label` 122 (D-0410); table `label` 85, join 39, input field 219 (D-0468); plot `ui_title` removed 25 (D-0409); banner `title` 2 and `subtitle` 2 (D-0411); `deployment_name` removed 7 (D-0479); comment block written 7 (D-0479); `display_name` to `ui_label` in the 8 app features files 8 (D-0480). The key `name` (the id) is not touched.
- What changed since the second report: (1) OC06 is decided (D-0479): the 5 deployment files with no banner title now lose the key too, and every file that had the key gets a comment block (7 files, text in the section COMMENT BLOCKS, PROVISIONAL wording for her to read). (2) The 25 removed plot titles are now an open case, OC16, each printed in full with the `ui_label` beside it. (3) OC07 is decided (D-0480, her words "display_name to ui_label"). (4) The script now keeps CRLF and a byte order mark, lists all 64 files it read but did not examine (4 hold display-like keys: `FastP_reads_boxplot.yaml`, `PlasmidFinder_wrangling.yaml`, `ResFinder_Abromics_wrangling.yaml`, `stress_test_master/plots/final_plot.yaml`), and lists the CODE, test and doc places of `deployment_name` and `display_name`. (5) Safety: no write through a hard link, all targets checked before the first write, `--report` only to a new file.
- Still open (28 listed places in 3 open cases): OC16 the 25 plot titles (where does the text go?); OC09 `info.subtitle` in 2 recipes; OC10 one comment that names an old key. OC05 (Gallery `info`) is listed with 0 places and is still not decided. Conflicts: 0; places the script cannot place: 0.
- Proof on a fresh copy (tmpAI/names_copy2 of the worktree, with config, Gallery, ref_data and the fixture folders): `--apply` wrote 188 files; a second run finds 0 changes; the same files exist before and after; the 50 master recipes (config recipes and Gallery bundles) load with `utils.recipe_loader.load_recipe`, and the deployment and app features files read as YAML; every changed line is a planned key (24 lines are field entries written in a one-line mapping, where `label` became `ui_label`).
- Not decided, provisional: the form and wording of the comment block (D-0479); the block is placed at the very top, before an existing header comment of the file (the choice is open: after the header is the other option); the marker is the second line, not the first, because the first line must be the former name.

---

# Names pass: dry run report (DRY RUN: writes nothing except the report file you name. Root: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ_wt_names_dryrun)

## Summary
516 change(s) in 188 file(s); 28 listed place(s) in 3 open case(s); 0 conflict(s); 0 change(s) the script cannot place; 0 recipe(s) would get the advice (no name).

| kind of file | files read | changes |
|---|---:|---:|
| recipes | 101 | 211 |
| recipe templates | 9 | 40 |
| Gallery bundles | 34 | 68 |
| test fixtures | 113 | 171 |
| deployment files | 5 | 14 |
| deployment templates | 2 | 4 |
| app features files | 8 | 8 |

by rule: R01 label->ui_label (D-0410) x122, R02 name->ui_label (D-0410) x0, R03 ui_title->ui_label (D-0410) x0, R04 ui_title->REMOVED (D-0409) x0, R05 ui_title->REMOVED (D-0409) x25, R06 title->ui_label (D-0411) x2, R07 subtitle->description (D-0411) x2, R08 deployment_name->REMOVED (D-0479) x7, R09 ui_title->REMOVED (D-0411) x0, R10 label->ui_label (D-0468) x85, R11 label->ui_label (D-0468) x39, R12 label->ui_label (D-0468) x219, R13 display_name->ui_label (D-0480) x8, R14 ui_title.visible: false->branding.show_recipe_name: false (D-0474) x0, R15 deployment_name->a comment block at the top of the file (D-0479) x7

## Changes the dry run would make

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:13: R01 info.label -> info.ui_label  [D-0410]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:18: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:30: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:40: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:52: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year.yaml:59: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml**
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**assets/gallery_data/area_simple/data_analysis_recipe.yaml**
- assets/gallery_data/area_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/area_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_grouped/data_analysis_recipe.yaml**
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_grouped/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml**
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_horizontal/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bar_simple/data_analysis_recipe.yaml**
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bar_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml**
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/beeswarm_sina/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/boxplot_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml**
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/boxplot_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/bubble/data_analysis_recipe.yaml**
- assets/gallery_data/bubble/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/bubble/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/connected_scatter/data_analysis_recipe.yaml**
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/connected_scatter/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml**
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/density_2d_bin/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/density_simple/data_analysis_recipe.yaml**
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/density_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/dumbbell/data_analysis_recipe.yaml**
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/dumbbell/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/ecdf/data_analysis_recipe.yaml**
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/ecdf/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/error_bar/data_analysis_recipe.yaml**
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/error_bar/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/freqpoly/data_analysis_recipe.yaml**
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/freqpoly/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml**
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/heatmap_correlation/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/histogram_simple/data_analysis_recipe.yaml**
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/histogram_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/jitter_strip/data_analysis_recipe.yaml**
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/jitter_strip/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/line_grouped/data_analysis_recipe.yaml**
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/line_grouped/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/line_simple/data_analysis_recipe.yaml**
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/line_simple/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml**
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/lollipop_advanced/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/point_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/point_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/point_simple/data_analysis_recipe.yaml**
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/point_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/proportion_bar/data_analysis_recipe.yaml**
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/proportion_bar/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/qq_plot/data_analysis_recipe.yaml**
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/qq_plot/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml**
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/ridgeline_advanced/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml**
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/scatter_smooth/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/stacked_area/data_analysis_recipe.yaml**
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/stacked_area/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/stacked_bar/data_analysis_recipe.yaml**
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/stacked_bar/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/step_chart/data_analysis_recipe.yaml**
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/step_chart/data_analysis_recipe.yaml:14: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/tile_simple/data_analysis_recipe.yaml**
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/tile_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml**
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_boxplot/data_analysis_recipe.yaml:13: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_faceted/data_analysis_recipe.yaml**
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_faceted/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/gallery_data/violin_simple/data_analysis_recipe.yaml**
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- assets/gallery_data/violin_simple/data_analysis_recipe.yaml:12: R10 data_schemas.example.label -> data_schemas.example.ui_label  [D-0468]

**assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml**
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:4: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:8: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:12: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.ui_label  [D-0468]
- assets/ref_data/Virulence_genes_APEC/Virulence_genes_APEC_input_fields.yaml:16: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.ui_label  [D-0468]

**config/app_features/demo-vetinst.yaml**
- config/app_features/demo-vetinst.yaml:5: R13 display_name -> ui_label  [D-0480]

**config/app_features/developer.yaml**
- config/app_features/developer.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/pipeline-exploration-advanced.yaml**
- config/app_features/pipeline-exploration-advanced.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/pipeline-exploration-simple.yaml**
- config/app_features/pipeline-exploration-simple.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/pipeline-static.yaml**
- config/app_features/pipeline-static.yaml:3: R13 display_name -> ui_label  [D-0480]

**config/app_features/qa.yaml**
- config/app_features/qa.yaml:18: R13 display_name -> ui_label  [D-0480]

**config/app_features/standalone.yaml**
- config/app_features/standalone.yaml:5: R13 display_name -> ui_label  [D-0480]

**config/app_features/web-demo.yaml**
- config/app_features/web-demo.yaml:5: R13 display_name -> ui_label  [D-0480]

**config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml**
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:20: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:30: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:44: R10 additional_datasets_schemas.VirulenceFinder.label -> additional_datasets_schemas.VirulenceFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:54: R10 additional_datasets_schemas.APEC_STEC_virulence_genes.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_Abromics_general_pipeline.yaml:67: R11 joins.AR1_MLST_Serotype_Virulence.label -> joins.AR1_MLST_Serotype_Virulence.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:18: R10 data_schemas.Summary.label -> data_schemas.Summary.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:29: R10 data_schemas.Summary_quality.label -> data_schemas.Summary_quality.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:43: R10 data_schemas.Quality_metrics.label -> data_schemas.Quality_metrics.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:54: R10 data_schemas.Detailed_summary.label -> data_schemas.Detailed_summary.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:66: R10 data_schemas.FastP.label -> data_schemas.FastP.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:77: R10 data_schemas.Quast.label -> data_schemas.Quast.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:88: R10 data_schemas.Bracken.label -> data_schemas.Bracken.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:99: R10 data_schemas.ResFinder.label -> data_schemas.ResFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:111: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:124: R10 additional_datasets_schemas.VirulenceFinder.label -> additional_datasets_schemas.VirulenceFinder.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:135: R10 additional_datasets_schemas.APEC_STEC_virulence_genes.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:150: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:165: R11 joins.FastP_with_metadata.label -> joins.FastP_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:173: R11 joins.Quast_with_metadata.label -> joins.Quast_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:181: R11 joins.Bracken_with_metadata.label -> joins.Bracken_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:189: R11 joins.ResFinder_with_metadata.label -> joins.ResFinder_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:197: R11 joins.MLST_with_metadata.label -> joins.MLST_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:206: R11 joins.QC_Reads_Anchor.label -> joins.QC_Reads_Anchor.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:216: R11 joins.Summary_phenotype_length_fragmentation.label -> joins.Summary_phenotype_length_fragmentation.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:224: R11 joins.ST22_Anchor.label -> joins.ST22_Anchor.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:238: R11 joins.AR1_MLST_Serotype_Virulence.label -> joins.AR1_MLST_Serotype_Virulence.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:250: R11 joins.QA_AMR_per_sample.label -> joins.QA_AMR_per_sample.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:259: R11 joins.QA_ST_with_NA.label -> joins.QA_ST_with_NA.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:266: R11 joins.QA_year_types.label -> joins.QA_year_types.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:273: R11 joins.QA_L50_integer.label -> joins.QA_L50_integer.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:280: R11 joins.QA_fanout_exhibit.label -> joins.QA_fanout_exhibit.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:290: R11 joins.QA_aggregated_no_key.label -> joins.QA_aggregated_no_key.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:298: R11 joins.QA_population_zscore.label -> joins.QA_population_zscore.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:4: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Gene_name.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:8: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Location.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:12: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.Name_plasmid.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/APEC_STEC_virulence_genes_input_fields.yaml:16: R12 additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.label -> additional_datasets_schemas.APEC_STEC_virulence_genes.input_fields.VirulenceFinder.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:4: R12 data_schemas.Bracken.input_fields.sample_id.label -> data_schemas.Bracken.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:9: R12 data_schemas.Bracken.input_fields.taxon_1.label -> data_schemas.Bracken.input_fields.taxon_1.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Bracken_input_fields.yaml:13: R12 data_schemas.Bracken.input_fields.proportion_1.label -> data_schemas.Bracken.input_fields.proportion_1.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:4: R12 data_schemas.Detailed_summary.input_fields.sample_id.label -> data_schemas.Detailed_summary.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:10: R12 data_schemas.Detailed_summary.input_fields.data.label -> data_schemas.Detailed_summary.input_fields.data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:14: R12 data_schemas.Detailed_summary.input_fields.data_type.label -> data_schemas.Detailed_summary.input_fields.data_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:18: R12 data_schemas.Detailed_summary.input_fields.predicted_phenotype.label -> data_schemas.Detailed_summary.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:22: R12 data_schemas.Detailed_summary.input_fields.cge_predicted_phenotype.label -> data_schemas.Detailed_summary.input_fields.cge_predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:26: R12 data_schemas.Detailed_summary.input_fields.identity.label -> data_schemas.Detailed_summary.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:30: R12 data_schemas.Detailed_summary.input_fields.overlap.label -> data_schemas.Detailed_summary.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:34: R12 data_schemas.Detailed_summary.input_fields.hsp_lengthtotal_length.label -> data_schemas.Detailed_summary.input_fields.hsp_lengthtotal_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:38: R12 data_schemas.Detailed_summary.input_fields.contig.label -> data_schemas.Detailed_summary.input_fields.contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:42: R12 data_schemas.Detailed_summary.input_fields.start.label -> data_schemas.Detailed_summary.input_fields.start.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:46: R12 data_schemas.Detailed_summary.input_fields.end.label -> data_schemas.Detailed_summary.input_fields.end.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Detailed_summary_input_fields.yaml:50: R12 data_schemas.Detailed_summary.input_fields.accession.label -> data_schemas.Detailed_summary.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:4: R12 data_schemas.FastP.input_fields.sample_id.label -> data_schemas.FastP.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:9: R12 data_schemas.FastP.input_fields.total_reads.label -> data_schemas.FastP.input_fields.total_reads.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:13: R12 data_schemas.FastP.input_fields.q30_rate.label -> data_schemas.FastP.input_fields.q30_rate.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/FastP_input_fields.yaml:17: R12 data_schemas.FastP.input_fields.gc_content.label -> data_schemas.FastP.input_fields.gc_content.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:4: R12 data_schemas.MLST.input_fields.sample_id.label -> data_schemas.MLST.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:10: R12 data_schemas.MLST.input_fields.scheme.label -> data_schemas.MLST.input_fields.scheme.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:15: R12 data_schemas.MLST.input_fields.sequence_type.label -> data_schemas.MLST.input_fields.sequence_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:20: R12 data_schemas.MLST.input_fields.locus_1.label -> data_schemas.MLST.input_fields.locus_1.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:25: R12 data_schemas.MLST.input_fields.locus_2.label -> data_schemas.MLST.input_fields.locus_2.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:29: R12 data_schemas.MLST.input_fields.locus_3.label -> data_schemas.MLST.input_fields.locus_3.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:34: R12 data_schemas.MLST.input_fields.locus_4.label -> data_schemas.MLST.input_fields.locus_4.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:38: R12 data_schemas.MLST.input_fields.locus_5.label -> data_schemas.MLST.input_fields.locus_5.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:43: R12 data_schemas.MLST.input_fields.locus_6.label -> data_schemas.MLST.input_fields.locus_6.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/MLST_input_fields.yaml:48: R12 data_schemas.MLST.input_fields.locus_7.label -> data_schemas.MLST.input_fields.locus_7.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:4: R12 data_schemas.Quality_metrics.input_fields.sample_id.label -> data_schemas.Quality_metrics.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:9: R12 data_schemas.Quality_metrics.input_fields.quality_module.label -> data_schemas.Quality_metrics.input_fields.quality_module.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:13: R12 data_schemas.Quality_metrics.input_fields.quality_feedback.label -> data_schemas.Quality_metrics.input_fields.quality_feedback.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:17: R12 data_schemas.Quality_metrics.input_fields.total_reads_after.label -> data_schemas.Quality_metrics.input_fields.total_reads_after.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:21: R12 data_schemas.Quality_metrics.input_fields.ratio_reads_after.label -> data_schemas.Quality_metrics.input_fields.ratio_reads_after.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:25: R12 data_schemas.Quality_metrics.input_fields.bracken_main_taxon.label -> data_schemas.Quality_metrics.input_fields.bracken_main_taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:29: R12 data_schemas.Quality_metrics.input_fields.proportion_of_main_taxon.label -> data_schemas.Quality_metrics.input_fields.proportion_of_main_taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:33: R12 data_schemas.Quality_metrics.input_fields.reads_gc_content.label -> data_schemas.Quality_metrics.input_fields.reads_gc_content.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:37: R12 data_schemas.Quality_metrics.input_fields.n50.label -> data_schemas.Quality_metrics.input_fields.n50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:41: R12 data_schemas.Quality_metrics.input_fields.total_length.label -> data_schemas.Quality_metrics.input_fields.total_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:45: R12 data_schemas.Quality_metrics.input_fields.largest_contig.label -> data_schemas.Quality_metrics.input_fields.largest_contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:49: R12 data_schemas.Quality_metrics.input_fields.num_contigs_500bp.label -> data_schemas.Quality_metrics.input_fields.num_contigs_500bp.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quality_metrics_input_fields.yaml:53: R12 data_schemas.Quality_metrics.input_fields.num_contigs_0bp.label -> data_schemas.Quality_metrics.input_fields.num_contigs_0bp.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:4: R12 data_schemas.Quast.input_fields.sample_id.label -> data_schemas.Quast.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:9: R12 data_schemas.Quast.input_fields.n50.label -> data_schemas.Quast.input_fields.n50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:13: R12 data_schemas.Quast.input_fields.total_length.label -> data_schemas.Quast.input_fields.total_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:17: R12 data_schemas.Quast.input_fields.largest_contig.label -> data_schemas.Quast.input_fields.largest_contig.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Quast_input_fields.yaml:21: R12 data_schemas.Quast.input_fields.L50.label -> data_schemas.Quast.input_fields.L50.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:4: R12 data_schemas.ResFinder.input_fields.sample_id.label -> data_schemas.ResFinder.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:9: R12 data_schemas.ResFinder.input_fields.gene.label -> data_schemas.ResFinder.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:13: R12 data_schemas.ResFinder.input_fields.predicted_phenotype.label -> data_schemas.ResFinder.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:17: R12 data_schemas.ResFinder.input_fields.identity.label -> data_schemas.ResFinder.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/ResFinder_input_fields.yaml:21: R12 data_schemas.ResFinder.input_fields.overlap.label -> data_schemas.ResFinder.input_fields.overlap.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:7: R12 data_schemas.Summary.input_fields.sample_id.label -> data_schemas.Summary.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:12: R12 data_schemas.Summary.input_fields.quality_module.label -> data_schemas.Summary.input_fields.quality_module.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:21: R12 data_schemas.Summary.input_fields.taxon.label -> data_schemas.Summary.input_fields.taxon.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:59: R12 data_schemas.Summary.input_fields.ST.label -> data_schemas.Summary.input_fields.ST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:64: R12 data_schemas.Summary.input_fields.genome_length.label -> data_schemas.Summary.input_fields.genome_length.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:70: R12 data_schemas.Summary.input_fields.N50.label -> data_schemas.Summary.input_fields.N50.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/Summary_input_fields.yaml:75: R12 data_schemas.Summary.input_fields.contigs_sup300bp.label -> data_schemas.Summary.input_fields.contigs_sup300bp.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:4: R12 additional_datasets_schemas.VirulenceFinder.input_fields.sample_id.label -> additional_datasets_schemas.VirulenceFinder.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:9: R12 additional_datasets_schemas.VirulenceFinder.input_fields.serotype.label -> additional_datasets_schemas.VirulenceFinder.input_fields.serotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/VirulenceFinder_input_fields.yaml:13: R12 additional_datasets_schemas.VirulenceFinder.input_fields.virulence_raw.label -> additional_datasets_schemas.VirulenceFinder.input_fields.virulence_raw.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:5: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:10: R12 metadata_schema.input_fields.source.label -> metadata_schema.input_fields.source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:14: R12 metadata_schema.input_fields.year.label -> metadata_schema.input_fields.year.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/input_fields/metadata_schema_input_fields.yaml:18: R12 metadata_schema.input_fields.country.label -> metadata_schema.input_fields.country.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml:2: R05 analysis_groups.Quality Control.plots.qc_reads_horizontal_barplot.ui_title REMOVED (value: Reads Quality & Taxonomy Proportion)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml:2: R05 analysis_groups.Results.plots.mlst_bar.ui_title REMOVED (value: MLST Sequence Type Distribution by Country)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml:2: R05 analysis_groups.Quality Control.plots.assembly_quality_dotplot.ui_title REMOVED (value: Assembly Quality Metrics (Quast))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:2: R05 analysis_groups.Results.plots.amr_heatmap.ui_title REMOVED (value: AMR Genes Presence by Category)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:2: R05 analysis_groups.Results.plots.virulence_bar.ui_title REMOVED (value: Selected Virulence Genes Count)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml:2: R05 analysis_groups.Results.plots.virulence_variants.ui_title REMOVED (value: Integrated Virulence & MLST Typing)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml:2: R05 analysis_groups.Cat 🐱.plots.miaou.ui_title REMOVED (value: 🐱 Miaou — Assembly Metric Distributions by Source)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml:2: R05 analysis_groups.Curiosity.plots.phenotype_genome_length_fragmentation.ui_title REMOVED (value: Phenotype Score correlation with Assembly Metrics)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_aggregated_no_key.ui_title REMOVED (value: QA: samples per country and year (aggregated, no sample_id))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_amr_genes_per_sample.ui_title REMOVED (value: QA: AMR genes per sample)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_facet_by_mapping.ui_title REMOVED (value: QA: facet_by written in mapping)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_fanout_rows_per_sample.ui_title REMOVED (value: QA EXHIBIT: rows per sample after joining two long tables)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_l50_integer.ui_title REMOVED (value: QA: samples per L50 (integer column))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_population_zscore.ui_title REMOVED (value: QA: N50 z-score per sample (depends on all samples))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_sequence_type_missing.ui_title REMOVED (value: QA: samples per sequence type)  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml:2: R05 analysis_groups.QA Canaries.plots.qa_year_label.ui_title REMOVED (value: QA: samples per year (text label))  [D-0409]

**config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml**
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml:2: R05 analysis_groups.Results.plots.year_distribution.ui_title REMOVED (value: Sample Count by Year (T1 = all years, T2 = 2023–2025 only))  [D-0409]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:18: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:23: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:35: R10 data_schemas.amr_data.label -> data_schemas.amr_data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:45: R10 data_schemas.plasmid_data.label -> data_schemas.plasmid_data.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:57: R11 joins.AMR_Profile_Joint.label -> joins.AMR_Profile_Joint.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy.yaml:64: R11 joins.Plasmid_Profile_Joint.label -> joins.Plasmid_Profile_Joint.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:4: R12 data_schemas.amr_data.input_fields.sample_id.label -> data_schemas.amr_data.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:8: R12 data_schemas.amr_data.input_fields.gene.label -> data_schemas.amr_data.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:12: R12 data_schemas.amr_data.input_fields.predicted_phenotype.label -> data_schemas.amr_data.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:16: R12 data_schemas.amr_data.input_fields.identity.label -> data_schemas.amr_data.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:20: R12 data_schemas.amr_data.input_fields.overlap.label -> data_schemas.amr_data.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/amr_data.yaml:24: R12 data_schemas.amr_data.input_fields.accession.label -> data_schemas.amr_data.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:4: R12 metadata_schema.input_fields.sample_id.label -> metadata_schema.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:8: R12 metadata_schema.input_fields.Source.label -> metadata_schema.input_fields.Source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:12: R12 metadata_schema.input_fields.Year.label -> metadata_schema.input_fields.Year.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/metadata_schema.yaml:16: R12 metadata_schema.input_fields.Country.label -> metadata_schema.input_fields.Country.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml**
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:4: R12 data_schemas.plasmid_data.input_fields.sample_id.label -> data_schemas.plasmid_data.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:8: R12 data_schemas.plasmid_data.input_fields.plasmid_name.label -> data_schemas.plasmid_data.input_fields.plasmid_name.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:12: R12 data_schemas.plasmid_data.input_fields.identity.label -> data_schemas.plasmid_data.input_fields.identity.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:16: R12 data_schemas.plasmid_data.input_fields.overlap.label -> data_schemas.plasmid_data.input_fields.overlap.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/input_fields/plasmid_data.yaml:20: R12 data_schemas.plasmid_data.input_fields.accession.label -> data_schemas.plasmid_data.input_fields.accession.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/3_test_no_joins.yaml**
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:20: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/demo_abromics.yaml**
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:12: R10 data_schemas.MLST.label -> data_schemas.MLST.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:22: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/demo_abromics.yaml:36: R11 joins.demo_join.label -> joins.demo_join.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:23: R10 data_schemas.fg_metadata.label -> data_schemas.fg_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:34: R10 data_schemas.fg_phenotypes.label -> data_schemas.fg_phenotypes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:45: R10 data_schemas.fg_genotypes.label -> data_schemas.fg_genotypes.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration.yaml:58: R11 joins.figshare_triple_join.label -> joins.figshare_triple_join.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:4: R12 data_schemas.fg_genotypes.input_fields.host_animal_common.label -> data_schemas.fg_genotypes.input_fields.host_animal_common.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:8: R12 data_schemas.fg_genotypes.input_fields.sample_id.label -> data_schemas.fg_genotypes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:12: R12 data_schemas.fg_genotypes.input_fields.gene.label -> data_schemas.fg_genotypes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:16: R12 data_schemas.fg_genotypes.input_fields.gene_type.label -> data_schemas.fg_genotypes.input_fields.gene_type.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:21: R12 data_schemas.fg_genotypes.input_fields.gene_identifier.label -> data_schemas.fg_genotypes.input_fields.gene_identifier.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:26: R12 data_schemas.fg_genotypes.input_fields.gene_name_family.label -> data_schemas.fg_genotypes.input_fields.gene_name_family.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_genotypes_input_fields.yaml:31: R12 data_schemas.fg_genotypes.input_fields.resistance_class.label -> data_schemas.fg_genotypes.input_fields.resistance_class.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:4: R12 data_schemas.fg_metadata.input_fields.sample_id.label -> data_schemas.fg_metadata.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:8: R12 data_schemas.fg_metadata.input_fields.host_animal_species.label -> data_schemas.fg_metadata.input_fields.host_animal_species.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:12: R12 data_schemas.fg_metadata.input_fields.host_animal_common.label -> data_schemas.fg_metadata.input_fields.host_animal_common.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:16: R12 data_schemas.fg_metadata.input_fields.specimen_source_tissue.label -> data_schemas.fg_metadata.input_fields.specimen_source_tissue.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:21: R12 data_schemas.fg_metadata.input_fields.final_diagnosis.label -> data_schemas.fg_metadata.input_fields.final_diagnosis.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_metadata_input_fields.yaml:25: R12 data_schemas.fg_metadata.input_fields.animal_infection_site_uti.label -> data_schemas.fg_metadata.input_fields.animal_infection_site_uti.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:4: R12 data_schemas.fg_phenotypes.input_fields.sample_id.label -> data_schemas.fg_phenotypes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:8: R12 data_schemas.fg_phenotypes.input_fields.mic_id.label -> data_schemas.fg_phenotypes.input_fields.mic_id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:14: R12 data_schemas.fg_phenotypes.input_fields.breakpoint.label -> data_schemas.fg_phenotypes.input_fields.breakpoint.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/figshare_integration/input_fields/fg_phenotypes_input_fields.yaml:20: R12 data_schemas.fg_phenotypes.input_fields.predicted_phenotype.label -> data_schemas.fg_phenotypes.input_fields.predicted_phenotype.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_a_phenotype_bar.ui_title REMOVED (value: Phenotypic Resistance per Antibiotic)  [D-0409]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_b_genotype_bar.ui_title REMOVED (value: Resistance Gene Families by Host)  [D-0409]

**config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml**
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml:2: R05 analysis_groups.AMR Integration.plots.plot_c_resistance_class.ui_title REMOVED (value: Resistance Class by Host Animal)  [D-0409]

**config/data_analysis_recipes/pipelines/stress_test_master.yaml**
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:12: R10 data_schemas.Stress_Source.label -> data_schemas.Stress_Source.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master.yaml:23: R11 joins.Master_Collection.label -> joins.Master_Collection.ui_label  [D-0468]

**config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml**
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:5: R12 data_schemas.Stress_Source.input_fields.id.label -> data_schemas.Stress_Source.input_fields.id.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:9: R12 data_schemas.Stress_Source.input_fields.species.label -> data_schemas.Stress_Source.input_fields.species.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:13: R12 data_schemas.Stress_Source.input_fields.amr_class.label -> data_schemas.Stress_Source.input_fields.amr_class.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:17: R12 data_schemas.Stress_Source.input_fields.collection_date.label -> data_schemas.Stress_Source.input_fields.collection_date.ui_label  [D-0468]
- config/data_analysis_recipes/pipelines/stress_test_master/input_fields/Stress_Source_input_fields.yaml:21: R12 data_schemas.Stress_Source.input_fields.value.label -> data_schemas.Stress_Source.input_fields.value.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_bad_select_column.yaml**
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:16: R10 data_schemas.Genes.label -> data_schemas.Genes.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:23: R12 data_schemas.Genes.input_fields.sample_id.label -> data_schemas.Genes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:24: R12 data_schemas.Genes.input_fields.gene.label -> data_schemas.Genes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:25: R12 data_schemas.Genes.input_fields.predicted_phenotype.label -> data_schemas.Genes.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_bad_select_column.yaml:35: R11 joins.Genes_joined.label -> joins.Genes_joined.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_broken_header.yaml**
- config/data_analysis_recipes/retest/retest_broken_header.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:16: R10 data_schemas.Genes.label -> data_schemas.Genes.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:23: R12 data_schemas.Genes.input_fields.sample_id.label -> data_schemas.Genes.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:24: R12 data_schemas.Genes.input_fields.gene.label -> data_schemas.Genes.input_fields.gene.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:25: R12 data_schemas.Genes.input_fields.predicted_phenotype.label -> data_schemas.Genes.input_fields.predicted_phenotype.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_broken_header.yaml:33: R11 joins.Genes_joined.label -> joins.Genes_joined.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_tier2.yaml**
- config/data_analysis_recipes/retest/retest_tier2.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_tier2.yaml:16: R10 data_schemas.Samples.label -> data_schemas.Samples.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:23: R12 data_schemas.Samples.input_fields.sample_id.label -> data_schemas.Samples.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:24: R12 data_schemas.Samples.input_fields.group.label -> data_schemas.Samples.input_fields.group.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:25: R12 data_schemas.Samples.input_fields.value.label -> data_schemas.Samples.input_fields.value.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:26: R12 data_schemas.Samples.input_fields.year.label -> data_schemas.Samples.input_fields.year.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:34: R11 joins.Result.label -> joins.Result.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_tier2.yaml:47: R11 joins.All_samples.label -> joins.All_samples.ui_label  [D-0468]

**config/data_analysis_recipes/retest/retest_top_n_other.yaml**
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:16: R10 data_schemas.Variants.label -> data_schemas.Variants.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:23: R12 data_schemas.Variants.input_fields.sample_id.label -> data_schemas.Variants.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:24: R12 data_schemas.Variants.input_fields.variant.label -> data_schemas.Variants.input_fields.variant.ui_label  [D-0468]
- config/data_analysis_recipes/retest/retest_top_n_other.yaml:38: R11 joins.Variants_joined.label -> joins.Variants_joined.ui_label  [D-0468]

**config/data_analysis_recipes/templates/audit.yaml**
- config/data_analysis_recipes/templates/audit.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/audit.yaml:13: R10 data_schemas.submission_logs.label -> data_schemas.submission_logs.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:26: R12 data_schemas.submission_logs.input_fields.lab_id.label -> data_schemas.submission_logs.input_fields.lab_id.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:30: R12 data_schemas.submission_logs.input_fields.submission_date.label -> data_schemas.submission_logs.input_fields.submission_date.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:34: R12 data_schemas.submission_logs.input_fields.status.label -> data_schemas.submission_logs.input_fields.status.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:38: R12 data_schemas.submission_logs.input_fields.turnaround_time.label -> data_schemas.submission_logs.input_fields.turnaround_time.ui_label  [D-0468]
- config/data_analysis_recipes/templates/audit.yaml:51: R05 analysis_groups.Performance.plots.tat_distribution.ui_title REMOVED (value: Turnaround Time by Laboratory)  [D-0409]
- config/data_analysis_recipes/templates/audit.yaml:71: R05 analysis_groups.Volumes.plots.submission_status.ui_title REMOVED (value: Submissions by Current Status)  [D-0409]

**config/data_analysis_recipes/templates/complex_template.yaml**
- config/data_analysis_recipes/templates/complex_template.yaml:9: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/complex_template.yaml:15: R10 data_schemas.genomics.label -> data_schemas.genomics.ui_label  [D-0468]
- config/data_analysis_recipes/templates/complex_template.yaml:27: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/complex_template.yaml:40: R11 joins.master_assembly.label -> joins.master_assembly.ui_label  [D-0468]

**config/data_analysis_recipes/templates/e_coli.yaml**
- config/data_analysis_recipes/templates/e_coli.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/e_coli.yaml:12: R10 data_schemas.amr_results.label -> data_schemas.amr_results.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:25: R12 data_schemas.amr_results.input_fields.sample_id.label -> data_schemas.amr_results.input_fields.sample_id.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:29: R12 data_schemas.amr_results.input_fields.serotype.label -> data_schemas.amr_results.input_fields.serotype.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:33: R12 data_schemas.amr_results.input_fields.sequence_type.label -> data_schemas.amr_results.input_fields.sequence_type.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:37: R12 data_schemas.amr_results.input_fields.ctx_m_gene.label -> data_schemas.amr_results.input_fields.ctx_m_gene.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:41: R12 data_schemas.amr_results.input_fields.growth_rate.label -> data_schemas.amr_results.input_fields.growth_rate.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:46: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:62: R12 metadata_schema.input_fields.collection_date.label -> metadata_schema.input_fields.collection_date.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:66: R12 metadata_schema.input_fields.country_of_origin.label -> metadata_schema.input_fields.country_of_origin.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:70: R12 metadata_schema.input_fields.hospital_site.label -> metadata_schema.input_fields.hospital_site.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:74: R12 metadata_schema.input_fields.patient_age.label -> metadata_schema.input_fields.patient_age.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:78: R12 metadata_schema.input_fields.patient_outcome.label -> metadata_schema.input_fields.patient_outcome.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:83: R11 joins.amr_with_metadata.label -> joins.amr_with_metadata.ui_label  [D-0468]
- config/data_analysis_recipes/templates/e_coli.yaml:104: R05 analysis_groups.AMR.plots.serotype_dist.ui_title REMOVED (value: Serotype Distribution by Country)  [D-0409]
- config/data_analysis_recipes/templates/e_coli.yaml:119: R05 analysis_groups.AMR.plots.growth_rate_by_st.ui_title REMOVED (value: Growth Rate by Sequence Type)  [D-0409]

**config/data_analysis_recipes/templates/left_join_lesson.yaml**
- config/data_analysis_recipes/templates/left_join_lesson.yaml:10: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:22: R10 data_schemas.sequenced.label -> data_schemas.sequenced.ui_label  [D-0468]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:41: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/left_join_lesson.yaml:61: R11 joins.lesson_assembly.label -> joins.lesson_assembly.ui_label  [D-0468]

**config/data_analysis_recipes/templates/simple_template.yaml**
- config/data_analysis_recipes/templates/simple_template.yaml:6: R01 info.label -> info.ui_label  [D-0410]
- config/data_analysis_recipes/templates/simple_template.yaml:12: R10 data_schemas.primary_data.label -> data_schemas.primary_data.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:28: R12 data_schemas.primary_data.input_fields.value.label -> data_schemas.primary_data.input_fields.value.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:32: R12 data_schemas.primary_data.input_fields.group.label -> data_schemas.primary_data.input_fields.group.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:37: R10 metadata_schema.label -> metadata_schema.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:53: R12 metadata_schema.input_fields.category.label -> metadata_schema.input_fields.category.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:58: R11 joins.main_collection.label -> joins.main_collection.ui_label  [D-0468]
- config/data_analysis_recipes/templates/simple_template.yaml:80: R05 analysis_groups.Overview.plots.value_by_group.ui_title REMOVED (value: Measurement Values by Group)  [D-0409]

**config/deployment/connect/connect_template.yaml**
- config/deployment/connect/connect_template.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/connect/connect_template.yaml:21: R08 deployment_name REMOVED (value: SPARMVET — Production (Posit Connect))  [D-0479]

**config/deployment/demo/demo-vetinst.yaml**
- config/deployment/demo/demo-vetinst.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/demo/demo-vetinst.yaml:5: R08 deployment_name REMOVED (value: SPARMVET demo (demo-vetinst))  [D-0479]
- config/deployment/demo/demo-vetinst.yaml:21: R06 branding.banner.title -> branding.banner.ui_label  [D-0411]
- config/deployment/demo/demo-vetinst.yaml:22: R07 branding.banner.subtitle -> branding.banner.description  [D-0411]

**config/deployment/demo/web-demo.yaml**
- config/deployment/demo/web-demo.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/demo/web-demo.yaml:5: R08 deployment_name REMOVED (value: SPARMVET demo (web-demo))  [D-0479]
- config/deployment/demo/web-demo.yaml:21: R06 branding.banner.title -> branding.banner.ui_label  [D-0411]
- config/deployment/demo/web-demo.yaml:22: R07 branding.banner.subtitle -> branding.banner.description  [D-0411]

**config/deployment/local/local.yaml**
- config/deployment/local/local.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/local/local.yaml:5: R08 deployment_name REMOVED (value: SPARMVET_VIZ (Local Dev))  [D-0479]

**config/deployment/local/retest.yaml**
- config/deployment/local/retest.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/local/retest.yaml:5: R08 deployment_name REMOVED (value: SPARMVET RETEST)  [D-0479]

**config/deployment/pipeline_test/pipeline_test.yaml**
- config/deployment/pipeline_test/pipeline_test.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/pipeline_test/pipeline_test.yaml:15: R08 deployment_name REMOVED (value: SPARMVET_VIZ (Pipeline Test))  [D-0479]

**config/deployment/templates/deployment_template.yaml**
- config/deployment/templates/deployment_template.yaml:1: R15 deployment_name -> a comment block at the top of the file  [D-0479]
- config/deployment/templates/deployment_template.yaml:23: R08 deployment_name REMOVED (value: My Pipeline — Institution Name)  [D-0479]

**libs/transformer/tests/data/modif_filter_data_analysis_recipe.yaml**
- libs/transformer/tests/data/modif_filter_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml**
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:21: R12 data_schemas.modif_join_where.input_fields.id.label -> data_schemas.modif_join_where.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:24: R12 data_schemas.modif_join_where.input_fields.lo.label -> data_schemas.modif_join_where.input_fields.lo.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:27: R12 data_schemas.modif_join_where.input_fields.hi.label -> data_schemas.modif_join_where.input_fields.hi.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:41: R12 data_schemas.modif_join_where_right.input_fields.rid.label -> data_schemas.modif_join_where_right.input_fields.rid.ui_label  [D-0468]
- libs/transformer/tests/data/modif_join_where_data_analysis_recipe.yaml:44: R12 data_schemas.modif_join_where_right.input_fields.v.label -> data_schemas.modif_join_where_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_all_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_all_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_any_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_any_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_bottom_k_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_bottom_k_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cast_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_coalesce_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_coalesce_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cum_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cum_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_cum_sum_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_cum_sum_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_describe_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_describe_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_nans_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_nans_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_drop_nulls_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_drop_nulls_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_dt_truncate_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_dt_truncate_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_explode_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_explode_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_fill_nan_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_fill_nan_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_fill_null_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_fill_null_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_first_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_first_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_gather_every_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_gather_every_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_group_by_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_group_by_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_group_by_dynamic_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_group_by_dynamic_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_head_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_head_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_interpolate_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_interpolate_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:21: R12 data_schemas.polars_join_asof.input_fields.id.label -> data_schemas.polars_join_asof.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:24: R12 data_schemas.polars_join_asof.input_fields.site.label -> data_schemas.polars_join_asof.input_fields.site.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:27: R12 data_schemas.polars_join_asof.input_fields.t.label -> data_schemas.polars_join_asof.input_fields.t.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:30: R12 data_schemas.polars_join_asof.input_fields.x.label -> data_schemas.polars_join_asof.input_fields.x.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:44: R12 data_schemas.polars_join_asof_right.input_fields.site.label -> data_schemas.polars_join_asof_right.input_fields.site.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:47: R12 data_schemas.polars_join_asof_right.input_fields.t.label -> data_schemas.polars_join_asof_right.input_fields.t.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_asof_data_analysis_recipe.yaml:50: R12 data_schemas.polars_join_asof_right.input_fields.v.label -> data_schemas.polars_join_asof_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:21: R12 data_schemas.polars_join.input_fields.id.label -> data_schemas.polars_join.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:24: R12 data_schemas.polars_join.input_fields.g.label -> data_schemas.polars_join.input_fields.g.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:27: R12 data_schemas.polars_join.input_fields.n.label -> data_schemas.polars_join.input_fields.n.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:30: R12 data_schemas.polars_join.input_fields.f.label -> data_schemas.polars_join.input_fields.f.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:33: R12 data_schemas.polars_join.input_fields.s.label -> data_schemas.polars_join.input_fields.s.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:47: R12 data_schemas.polars_join_right.input_fields.id.label -> data_schemas.polars_join_right.input_fields.id.ui_label  [D-0468]
- libs/transformer/tests/data/polars_join_data_analysis_recipe.yaml:50: R12 data_schemas.polars_join_right.input_fields.v.label -> data_schemas.polars_join_right.input_fields.v.ui_label  [D-0468]

**libs/transformer/tests/data/polars_last_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_last_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_limit_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_limit_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_list_join_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_list_join_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_list_slice_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_list_slice_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_max_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_max_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_max_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_max_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_mean_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_mean_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_mean_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_mean_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_median_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_median_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_min_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_min_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_min_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_min_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_null_count_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_null_count_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_pivot_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_pivot_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_quantile_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_quantile_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rank_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rank_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_remove_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_remove_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rename_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rename_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_reverse_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_reverse_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_rolling_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_rolling_data_analysis_recipe.yaml:7: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_round_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_round_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sample_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sample_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_select_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_select_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_shift_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_shift_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_slice_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_slice_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sort_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sort_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_std_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_std_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_extract_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_extract_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_replace_all_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_replace_all_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_split_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_split_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_splitn_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_splitn_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_str_strip_chars_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_str_strip_chars_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sum_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sum_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_sum_horizontal_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_sum_horizontal_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_tail_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_tail_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_top_k_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_top_k_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unique_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unique_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unnest_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unnest_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_unpivot_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_unpivot_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_var_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_var_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_with_columns_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_with_columns_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/polars_with_row_index_data_analysis_recipe.yaml**
- libs/transformer/tests/data/polars_with_row_index_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

**libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml**
- libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml:8: R01 info.label -> info.ui_label  [D-0410]

## CANNOT BE DECIDED BY THE SCRIPT
(listed, never changed; each line is a place a person or the owner decides)

### OC16: The longer title of a group or a plot is removed and kept nowhere: where does the text go? -- 25 place(s)
> D-0409 (1), (2): a group's and a plot's `ui_title` is removed from the format and the report uses the `ui_label`. The removal is applied as decided; the TEXT of each title is kept nowhere. Each text is printed in full below, with the `ui_label` that replaces it, so that the owner can say where a longer text belongs (for example `description`).
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_horizontal_barplot.yaml:2: analysis_groups.Quality Control.plots.qc_reads_horizontal_barplot.ui_title "Reads Quality & Taxonomy Proportion" is removed and kept nowhere; ui_label is "QC Reads Horizontal Barplot"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/MLST_counts_bar.yaml:2: analysis_groups.Results.plots.mlst_bar.ui_title "MLST Sequence Type Distribution by Country" is removed and kept nowhere; ui_label is "MLST Bar"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/Quast_assembly_quality_barplot.yaml:2: analysis_groups.Quality Control.plots.assembly_quality_dotplot.ui_title "Assembly Quality Metrics (Quast)" is removed and kept nowhere; ui_label is "Assembly Quality Dotplot"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/ResFinder_genes_heatmap.yaml:2: analysis_groups.Results.plots.amr_heatmap.ui_title "AMR Genes Presence by Category" is removed and kept nowhere; ui_label is "AMR Heatmap"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/VirulenceFinder_counts_bar.yaml:2: analysis_groups.Results.plots.virulence_bar.ui_title "Selected Virulence Genes Count" is removed and kept nowhere; ui_label is "Virulence Bar"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/integration_plot.yaml:2: analysis_groups.Results.plots.virulence_variants.ui_title "Integrated Virulence & MLST Typing" is removed and kept nowhere; ui_label is "Virulence Variants"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/miaou.yaml:2: analysis_groups.Cat 🐱.plots.miaou.ui_title "🐱 Miaou — Assembly Metric Distributions by Source" is removed and kept nowhere; ui_label is "Miaou 🐈"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/phenotype_genome_length_dotplot.yaml:2: analysis_groups.Curiosity.plots.phenotype_genome_length_fragmentation.ui_title "Phenotype Score correlation with Assembly Metrics" is removed and kept nowhere; ui_label is "Phenotype Genome Length Fragmentation"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_aggregated_no_key.yaml:2: analysis_groups.QA Canaries.plots.qa_aggregated_no_key.ui_title "QA: samples per country and year (aggregated, no sample_id)" is removed and kept nowhere; ui_label is "QA Aggregated No Key"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_amr_genes_per_sample.yaml:2: analysis_groups.QA Canaries.plots.qa_amr_genes_per_sample.ui_title "QA: AMR genes per sample" is removed and kept nowhere; ui_label is "QA AMR Genes Per Sample"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_facet_by_mapping.yaml:2: analysis_groups.QA Canaries.plots.qa_facet_by_mapping.ui_title "QA: facet_by written in mapping" is removed and kept nowhere; ui_label is "QA Facet By Mapping"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_fanout_rows_per_sample.yaml:2: analysis_groups.QA Canaries.plots.qa_fanout_rows_per_sample.ui_title "QA EXHIBIT: rows per sample after joining two long tables" is removed and kept nowhere; ui_label is "QA Fanout Rows Per Sample"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_l50_integer.yaml:2: analysis_groups.QA Canaries.plots.qa_l50_integer.ui_title "QA: samples per L50 (integer column)" is removed and kept nowhere; ui_label is "QA L50 Integer"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_population_zscore.yaml:2: analysis_groups.QA Canaries.plots.qa_population_zscore.ui_title "QA: N50 z-score per sample (depends on all samples)" is removed and kept nowhere; ui_label is "QA Population Zscore"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_sequence_type_missing.yaml:2: analysis_groups.QA Canaries.plots.qa_sequence_type_missing.ui_title "QA: samples per sequence type" is removed and kept nowhere; ui_label is "QA Sequence Type Missing"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/qa_year_label.yaml:2: analysis_groups.QA Canaries.plots.qa_year_label.ui_title "QA: samples per year (text label)" is removed and kept nowhere; ui_label is "QA Year Label"
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/year_distribution.yaml:2: analysis_groups.Results.plots.year_distribution.ui_title "Sample Count by Year (T1 = all years, T2 = 2023–2025 only)" is removed and kept nowhere; ui_label is "Year Distribution"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_a_phenotype_bar.yaml:2: analysis_groups.AMR Integration.plots.plot_a_phenotype_bar.ui_title "Phenotypic Resistance per Antibiotic" is removed and kept nowhere; ui_label is "Plot A Phenotype Bar"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_b_genotype_bar.yaml:2: analysis_groups.AMR Integration.plots.plot_b_genotype_bar.ui_title "Resistance Gene Families by Host" is removed and kept nowhere; ui_label is "Plot B Genotype Bar"
- config/data_analysis_recipes/pipelines/figshare_integration/plots/plot_c_resistance_class.yaml:2: analysis_groups.AMR Integration.plots.plot_c_resistance_class.ui_title "Resistance Class by Host Animal" is removed and kept nowhere; ui_label is "Plot C Resistance Class"
- config/data_analysis_recipes/templates/audit.yaml:51: analysis_groups.Performance.plots.tat_distribution.ui_title "Turnaround Time by Laboratory" is removed and kept nowhere; ui_label is "Tat Distribution"
- config/data_analysis_recipes/templates/audit.yaml:71: analysis_groups.Volumes.plots.submission_status.ui_title "Submissions by Current Status" is removed and kept nowhere; ui_label is "Submission Status"
- config/data_analysis_recipes/templates/e_coli.yaml:104: analysis_groups.AMR.plots.serotype_dist.ui_title "Serotype Distribution by Country" is removed and kept nowhere; ui_label is "Serotype Dist"
- config/data_analysis_recipes/templates/e_coli.yaml:119: analysis_groups.AMR.plots.growth_rate_by_st.ui_title "Growth Rate by Sequence Type" is removed and kept nowhere; ui_label is "Growth Rate By ST"
- config/data_analysis_recipes/templates/simple_template.yaml:80: analysis_groups.Overview.plots.value_by_group.ui_title "Measurement Values by Group" is removed and kept nowhere; ui_label is "Value By Group"

### OC09: Display-like keys that no decision names (for example `info.subtitle`) -- 2 place(s)
> D-0408: `info` is the free information block: every key written is shown. No line renames or removes these keys.
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml:8: info.subtitle: E. coli ST22 — AMR & Virulence Research (demo)
- config/data_analysis_recipes/pipelines/3_test_no_joins.yaml:8: info.subtitle: A single data schema with no joins at all — issue

### OC05: What the Gallery writes in `info`, and where a Gallery description lives -- 0 place(s)
> D-0408: NOT decided: what the Gallery generator writes in `info` (Gallery question Q8). The KEY of a Gallery bundle is renamed like any recipe's (D-0407: `ui_` in every file kind; D-0468: the `label` of recipe files); what `info` is for in an example is open.
- 34 Gallery bundle(s); keys written in their `info`: description x34, label x34, submission_date x34; 34 bundle(s) with an example_meta.md (the guidance text)

### OC10: Comments that name an old key (a person must reword them) -- 1 place(s)
> D-0411: the one pass also covers the documentation and the recipe specification. The script never edits a comment.
- config/deployment/templates/deployment_template.yaml:46: branding.banner: optional {logo_url, title, subtitle} shown in the Deployment info panel.

## COMMENT BLOCKS the script would write at the top of each deployment file (D-0479; form and wording PROVISIONAL: not decided)
(the first line is the former `deployment_name`; the second is the fixed marker line that tells a second run that the block exists; then only what the file itself states. Read the wording: it can be changed in one place, the BLOCK_* constants at the top of the script, before anything is applied.)

**config/deployment/connect/connect_template.yaml**: at the top of the file, before the existing leading comment (18 line(s)), which is kept below it
```
# SPARMVET — Production (Posit Connect)
# Description of this deployment, written by the names pass; the app does not read it.
# Default app features: pipeline-static
# Default recipe: my_pipeline
```

**config/deployment/demo/demo-vetinst.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
# SPARMVET demo (demo-vetinst)
# Description of this deployment, written by the names pass; the app does not read it.
# Default app features: demo-vetinst
# Default recipe: 1_test_data_ST22_dummy
# Contact: amr-surveillance@vetinst.no
```

**config/deployment/demo/web-demo.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
# SPARMVET demo (web-demo)
# Description of this deployment, written by the names pass; the app does not read it.
# Default app features: web-demo
# Default recipe: 1_test_data_ST22_dummy
```

**config/deployment/local/local.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
# SPARMVET_VIZ (Local Dev)
# Description of this deployment, written by the names pass; the app does not read it.
# Default app features: developer
# Contact: https://github.com/evezeyl/SPARMVET_VIZ/issues
```

**config/deployment/local/retest.yaml**: at the top of the file, before the existing leading comment (3 line(s)), which is kept below it
```
# SPARMVET RETEST
# Description of this deployment, written by the names pass; the app does not read it.
# Default app features: developer
```

**config/deployment/pipeline_test/pipeline_test.yaml**: at the top of the file, before the existing leading comment (12 line(s)), which is kept below it
```
# SPARMVET_VIZ (Pipeline Test)
# Description of this deployment, written by the names pass; the app does not read it.
# Default recipe: 1_test_data_ST22_dummy
```

**config/deployment/templates/deployment_template.yaml**: at the top of the file, before the existing leading comment (13 line(s)), which is kept below it
```
# My Pipeline — Institution Name
# Description of this deployment, written by the names pass; the app does not read it.
# Default app features: pipeline-static
# Default recipe: pipeline_name
# Contact: team@example.org
```

## CODE places that read or write a removed key (the pass must change them; not changed here; text match, a person reads each line)
deployment_name (D-0479: the key goes; the bootloader and the connector hold no deployment name):
  code: 4 place(s) in 3 file(s)
  - app/src/bootloader.py:122: self.deployment_name: str = self.deployment_config.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
  - libs/connector/src/connector/base.py:64: def get_deployment_name(self) -> str:
  - libs/connector/src/connector/base.py:66: return self._deployment.get("deployment_name", "SPARMVET_VIZ")
  - assets/scripts/create_test_deployment.py:68: "deployment_name": args.description,
  tests: 29 place(s) in 20 file(s)
  - app/tests/gate_stage.py:71: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "gate stage", "locat
  - app/tests/test_bootloader_launch.py:37: body = {"deployment_type": "filesystem", "deployment_name": name, "locations": locations}
  - app/tests/test_bootloader_launch.py:58: assert b.deployment_name == "dep.yaml"
  - app/tests/test_bootloader_store_cleanup.py:38: path.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "dep", "default_app_featur
  - app/tests/test_cache_version_6.py:212: path.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "dep", "default_app_featur
  - app/tests/test_data_analysis_recipe_load_gate.py:35: body = {"deployment_type": "filesystem", "deployment_name": name,
  - app/tests/test_deployment_branding.py:58: assert b.deployment_name == file_data.get("deployment_name", "SPARMVET_VIZ (Local Dev)")
  - app/tests/test_deployment_branding.py:81: assert b.deployment_name == "SPARMVET demo (demo-vetinst)"
  - app/tests/test_deployment_branding.py:91: assert b.deployment_name == "SPARMVET demo (web-demo)"
  - app/tests/test_empty_data_analysis_recipe_startup.py:39: "deployment_name": "empty-recipes-test",
  - app/tests/test_gate_gap.py:35: body = {"deployment_type": "filesystem", "deployment_name": "dep",
  - app/tests/test_opening_handler.py:236: (tmp_path / "dep.yaml").write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "dep", 
  - app/tests/test_shiny_filter_pickers.py:79: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "typed pickers", "lo
  - app/tests/test_shiny_filter_types.py:69: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "typed values", "loc
  - app/tests/test_shiny_filter_value_list.py:62: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "long list", "locati
  - app/tests/test_shiny_filter_whole_numbers.py:59: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "whole numbers", "lo
  - app/tests/test_shiny_plot_errors.py:95: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot errors", "loca
  - app/tests/test_shiny_plot_tier3.py:97: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot tier3", "locat
  - app/tests/test_shiny_plot_warnings.py:72: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "plot warnings", "lo
  - app/tests/test_shiny_step_order.py:85: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "step order", "locat
  - app/tests/test_tier_decides_filter_form.py:197: deployment.write_text(yaml.safe_dump({"deployment_type": "filesystem", "deployment_name": "tier filter", "loca
  - libs/connector/tests/test_connectors.py:44: "deployment_name": "AMR Pipeline",
  - libs/connector/tests/test_connectors.py:111: "deployment_name": "AMR Pipeline",
  - libs/connector/tests/test_connectors.py:151: def test_get_deployment_name(self):
  - libs/connector/tests/test_connectors.py:153: assert c.get_deployment_name() == "AMR Pipeline"
  - libs/connector/tests/test_connectors.py:155: def test_get_deployment_name_default(self):
  - libs/connector/tests/test_connectors.py:157: assert c.get_deployment_name() == "SPARMVET_VIZ"
  - libs/utils/tests/test_path_expansion.py:25: "deployment_name": "~keep~"}
  - libs/utils/tests/test_path_expansion.py:28: assert cfg["deployment_name"] == "~keep~"  # not a path key
  docs: 5 place(s) in 2 file(s)
  - docs/deployment/deployment_guide.qmd:39: deployment_name: "AMR Surveillance — Institute Server"
  - docs/deployment/deployment_guide.qmd:63: deployment_name: "AMR Pipeline — IRIDA"
  - docs/deployment/deployment_guide.qmd:92: | `deployment_name` | — | Not shown; purely informational |
  - docs/workflows/connector.qmd:84: deployment_name: "AMR Pipeline — Galaxy EU"
  - docs/workflows/connector.qmd:255: deployment_name: "SPARMVET_VIZ (Local Dev)"
display_name (D-0480: the key becomes ui_label in app features files (the reader `app_features_display_name`, the allowed keys of the validator, the old-key refusal)):
  code: 23 place(s) in 9 file(s)
  - app/handlers/blueprint_handlers.py:2647: ui.input_text("bp_new_display_name", "Display name",
  - app/handlers/blueprint_handlers.py:2696: display_name = (safe_input(input, "bp_new_display_name", "") or slug).strip()
  - app/handlers/blueprint_handlers.py:2704: slug, display_name, description=desc, author=author, created=today))
  - app/modules/wrangle_studio.py:1871: display_name = "mapping (aes)"
  - app/modules/wrangle_studio.py:1877: display_name = component_name
  - app/modules/wrangle_studio.py:1884: display_name = node.get("action", "unknown")
  - app/modules/wrangle_studio.py:1909: ui.span(f"{i + 1}. {display_name}", class_="fw-bold small"),
  - app/src/bootloader.py:398: def app_features_display_name(self) -> str:
  - app/src/bootloader.py:399: """Human-readable app features name from the template's display_name field.
  - app/src/bootloader.py:405: self.config.get("display_name")
  - app/src/server.py:162: print(f"DEBUG: Initializing Server with App features: {bootloader.app_features_display_name}")
  - app/src/server.py:163: current_app_features = reactive.Value(bootloader.app_features_display_name)
  - libs/utils/build/lib/utils/recipe_check.py:315: if "display_name" in info:
  - libs/utils/build/lib/utils/recipe_check.py:316: self.add("I03", "info.display_name", "display_name was renamed", self.spec["renamed"]["info"]["display_name"])
  - libs/utils/build/lib/utils/recipe_migration.py:5: - renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name
  - libs/utils/build/lib/utils/recipe_migration.py:151: name = _find(info[1], "display_name")
  - libs/utils/build/lib/utils/recipe_migration.py:155: report.append("info: display_name -> label")
  - libs/utils/src/utils/recipe_check.py:315: if "display_name" in info:
  - libs/utils/src/utils/recipe_check.py:316: self.add("I03", "info.display_name", "display_name was renamed", self.spec["renamed"]["info"]["display_name"])
  - libs/utils/src/utils/recipe_migration.py:5: - renames `info.display_name` to `label`, `is_primary_key` to `is_entity_key`, `source_name` to `original_name
  - libs/utils/src/utils/recipe_migration.py:151: name = _find(info[1], "display_name")
  - libs/utils/src/utils/recipe_migration.py:155: report.append("info: display_name -> label")
  - assets/scripts/migrate_recipe_format.py:4: What run A does: adds spec_version and the engine lines; renames display_name, is_primary_key and source_name;
  tests: 12 place(s) in 11 file(s)
  - app/tests/debug_pipeline_connector.py:181: record("App features loaded", PASS, bl2.app_features_display_name)
  - app/tests/test_bundle_importer.py:35: info: {{display_name: Tiny}}
  - app/tests/test_cache_keys.py:65: info: {{display_name: Tiny}}
  - app/tests/test_data_analysis_recipe_info.py:8: assert info_lines({"display_name": "AMR", "version": "1.0"}) == [(0, "display_name", "AMR"), (0, "version", "1
  - app/tests/test_data_import_check.py:28: info: {{display_name: Tiny}}
  - app/tests/test_writers_emit_format_one.py:35: OLD_WORDS = ("output_fields", "final_contract", "display_name", "is_primary_key", "source_name", "_t3_origin",
  - libs/blueprint_arch/tests/test_new_recipe.py:43: assert "name" not in info and "display_name" not in info
  - libs/test_lab/tests/test_bootstrapper.py:152: assert "output_fields" not in schema and "display_name" not in recipe["info"]
  - libs/utils/tests/test_recipe_check.py:130: ("I03", "E", lambda r: r["info"].update(display_name="x"), "run"),
  - libs/utils/tests/test_recipe_factory.py:51: for old in ("output_fields", "final_contract", "display_name", "is_primary_key", "source_name"):
  - libs/utils/tests/test_recipe_migration.py:15: display_name: Old recipe   # the name
  - libs/utils/tests/test_recipe_migration.py:68: def test_display_name_becomes_label():
  docs: 4 place(s) in 3 file(s)
  - docs/reference/environment_variables.qmd:79: The app features config file can be placed **anywhere** — there is no filename convention requirement. The fil
  - docs/reference/environment_variables.qmd:87: # 2. Edit display_name, name, and feature flags in the new file
  - docs/workflows/ui_app_features.qmd:252: display_name: "Workflow Developer"
  - .claude/rules/rules_toolchain.md:24: | `assets/scripts/migrate_display_names.py` | DRY RUN of the names pass (ledger D-0407 to D-0412, D-0468 to D-

## Facts to name the recipe banner switch (D-0472)
(per deployment file: its default app features file and the keys of its `branding` block; per app features file: what its `ui_title` sets today. The list of allowed deployment keys does not exist yet: D-0412 asks for it, it comes with the deployment standard; today the only refusal tables are app/modules/renamed_keys.py and the readers app/src/bootloader.py:591, 874, 877-879)
- config/deployment/connect/connect_template.yaml: default_app_features = pipeline-static; branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/demo/demo-vetinst.yaml: default_app_features = demo-vetinst; branding keys: theme_css, banner, contact; banner keys: logo_url, title, subtitle; the banner shows: title 'AMR Surveillance — Overview'; line 'Norwegian Veterinary Institute'; logo 'assets/demo/logo-no.svg'
- config/deployment/demo/web-demo.yaml: default_app_features = web-demo; branding keys: theme_css, banner; banner keys: logo_url, title, subtitle; the banner shows: logo 'assets/demo/logo-no.svg'
- config/deployment/local/local.yaml: default_app_features = developer; branding keys: contact; banner keys: (no banner); the banner shows: no banner
- config/deployment/local/retest.yaml: default_app_features = developer; branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/pipeline_test/pipeline_test.yaml: default_app_features = (none); branding keys: (no branding block); banner keys: (no banner); the banner shows: no banner
- config/deployment/templates/deployment_template.yaml: default_app_features = pipeline-static; branding keys: contact; banner keys: (no banner); the banner shows: no banner
- config/app_features/demo-vetinst.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/developer.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-exploration-advanced.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-exploration-simple.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/pipeline-static.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/qa.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/standalone.yaml: does not set ui_title (the recipe banner is shown)
- config/app_features/web-demo.yaml: does not set ui_title (the recipe banner is shown)

## WOULD GET THE ADVICE (no recipe name)
(not an error, D-0470: the file name is shown where a name is needed)

## DECIDED, nothing for the script to change (counts only)
(D-0468, D-0469, D-0471, D-0475)

### OC02: DECIDED, not renamed: the `"label"` strings of the Python code (action forms, registries) -- 0 place(s)
> D-0468: the review session's reading (not her words): the `"label"` strings of the Python code are not recipe keys and are not renamed by this pass. Counted by text match, not a parse.
- 890 place(s) in 22 file(s) write a `"label"` key in libs/*/src (text match; blueprint_arch: 11, test_lab: 6, transformer: 53, utils: 3, viz_factory: 814, viz_gallery: 3)

### OC03: DECIDED: the recipe format number stays 1 -- 0 place(s)
> D-0469 (her words: we are still in development so the same format can stay): the recipe format number stays 1. The count shows the spec_version of every master recipe.
- spec_version found in 1 x122 master recipe(s)

### OC04: DECIDED: old session files are refused, not converted -- 0 place(s)
> D-0475 (her words: 3, 4, 6, 7. accepted.; point 4 as the review session reports it: a saved session with an old name key is refused with a plain line, no conversion, resting on D-0312, D-0471): old session files are refused, not converted. The script lists where a session holds a name key and never touches a session.
- 34 session file(s) found under a `_sessions` folder, 0 with an old name key. The session writer's own `label` is the user's label of the session, not a recipe name (app/modules/session_manager.py).

## 64 file(s) read but not examined (no spec_version, included by no recipe)
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/AR1_MLST_Serotype_Virulence.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Bracken_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Bracken_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/FastP_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/FastP_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_L50_integer.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_ST_with_NA.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_population_zscore_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_population_zscore_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QA_year_types.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/QC_Reads_Anchor_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Quast_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Quast_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_wrangling_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_wrangling_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier1.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling_tier2.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/VirulenceFinder_wrangling.yaml
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/metadata_schema_wrangling.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/assembly/Plasmid_Profile_Joint.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/wrangling/amr_data.yaml
- config/data_analysis_recipes/pipelines/2_test_data_ST22_dummy/wrangling/plasmid_data.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/fg_genotypes_wrangling.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/fg_metadata_wrangling.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/fg_phenotypes_wrangling.yaml
- config/data_analysis_recipes/pipelines/figshare_integration/wrangling/figshare_triple_join_steps.yaml
- config/data_analysis_recipes/pipelines/stress_test_master/plots/final_plot.yaml
- config/data_analysis_recipes/pipelines/stress_test_master/wrangling/Master_Collection_steps.yaml
- config/data_analysis_recipes/pipelines/stress_test_master/wrangling/Stress_Source_wrangling.yaml
- config/data_analysis_recipes/templates/complex_template/genomics_wrangling.yaml
- config/data_analysis_recipes/templates/complex_template/master_steps.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty/wrangling/plasmid_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_dirty_no_null_text/wrangling/plasmid_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_emptied/wrangling/plasmid_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/assembly/Plasmid_Profile_Joint.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/wrangling/amr_data.yaml
- app/tests/equality/recipes/2_test_data_ST22_dummy_fractional_year/wrangling/plasmid_data.yaml

4 of them hold display-like keys (label, name, title, subtitle, display_name, ui_title, ui_label) that the script did not look at:
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/plots/FastP_reads_boxplot.yaml: title (line 2), name (line 10)
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/PlasmidFinder_wrangling.yaml: label (line 4)
- config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml: name (line 18)
- config/data_analysis_recipes/pipelines/stress_test_master/plots/final_plot.yaml: title (line 1), name (line 6)
