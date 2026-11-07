# Retest procedure, 2026-11-06

**For:** Eve (tester). **Covers:** issues #10, #18, #21, #23 and the export checks (EXPORT-CHECK-1), plus
what changed in BLUEPRINT/HOME on 2026-11-06.
**Markers:** same as `test_plan_2026-06.md` section 0.1: `[ ]` not tested, `[x]` pass, `[!]` fail, `[~]` polish,
`[?]` decision. On a failure add one line starting with `>`.
**How the numbers below were checked:** every number was produced by a real run on 2026-11-06 (browser,
real download) and the data analysis recipes are kept working by `app/tests/test_retest_data_analysis_recipes.py`. If a number is
different for you, that is a finding.

Chrome: developer console, Network tab, "Disable cache" on (as in the test plan).

---

## 0. Launch

**A. Your normal project data** (issues #21 and the export on the real dummy project):

```
PYTHONPATH=. SPARMVET_APP_FEATURES=config/ui/templates/developer_template.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
```

**B. The retest set** (small data analysis recipes with known numbers; its own cache, `tmp/RETEST/`, apart from your
normal `tmp/UI_TEST/`):

```
PYTHONPATH=. SPARMVET_DEPLOYMENT=config/deployment/local/retest.yaml SPARMVET_APP_FEATURES=config/ui/templates/qa_template.yaml ./.venv/bin/shiny run app/src/main.py --port 8000
```

The qa app features has every feature on (filters, My view, T3, export). In the left panel "Data analysis recipe Choice" you
see four projects: `retest_tier2`, `retest_top_n_other`, `retest_broken_header`, `retest_bad_output_field`.

**After you edit a config or data file you do NOT restart the server: save the file and reload the page (F5).**
(The app compares the files with what it loaded, ADR-089.) Restart only if you changed Python code.

Start clean when you want: `rm -rf tmp/RETEST` (deletes only the retest cache).

### Files you will edit

| File | Used in |
|---|---|
| `config/data_analysis_recipes/retest/retest_tier2.yaml` (places marked `EDIT HERE`) | RT-04, RT-05, RT-07 |
| `assets/test_data/retest/samples.tsv` | RT-06, RT-07 |
| `config/data_analysis_recipes/retest/retest_top_n_other.yaml` | RT-21 |
| `config/data_analysis_recipes/retest/retest_broken_header.yaml` | RT-30 |
| `config/data_analysis_recipes/retest/retest_bad_output_field.yaml` | RT-31 |

Undo any edit with `git checkout -- <file>`.

### Look at the stored files

```
ls -l --time-style=full-iso tmp/RETEST/user/anchors/
```

Tier 1 is `<join>.parquet`, Tier 2 is `<join>__T2.parquet`. A changed modification time means the file was rewritten.

---

## 1. Tier 2 stored as a parquet with a chained key (issue #10) — project `retest_tier2`

The data: 12 samples (`s01`..`s12`), columns `group` (A, B, C), `value`, `year`. The join **Result** has one
tier2 step: keep `value >= 10`. The join **All_samples** has no tier2 step.

- [ ] **RT-01 Load.** Select `retest_tier2`. Tab "Value by group": box plot, badge "Viewing: Result".
  "Data to show: Raw" shows **12** rows, "Result" shows **8** (`s02 s03 s05 s06 s08 s09 s11 s12`).
  Tab "Samples per year": Result shows 12 rows and the badge has the note **T2=T1**.
  The right panel "Pipeline Audit" lists `[Tier 2] filter_range` (new today: before, it never listed Tier 2 steps).
- [ ] **RT-02 Files.** `ls tmp/RETEST/user/anchors/` shows `Result.parquet`, `Result__T2.parquet`, `All_samples.parquet`
  and **no** `All_samples__T2.parquet` (no tier2 step, nothing stored).
- [ ] **RT-03 Reuse.** Note the time of `Result__T2.parquet`. Switch "Data to show" Raw, Result, My view, Result, and press F5.
  The time of `Result__T2.parquet` and `Result.parquet` does **not** change.
- [ ] **RT-04 Change a Tier 2 step only.** In `retest_tier2.yaml` change `min: 10` to `min: 20`, save, F5.
  Result now shows **3** rows (`s05 s06 s09`). `Result__T2.parquet` has a new time; `Result.parquet` (Tier 1) has the **old** time.
- [ ] **RT-05 Move a step from Tier 2 to Tier 1.** Restore `min: 10`. Then cut the step and put it in tier1:
  ```yaml
  steps:
    tier1:
      - action: filter_range
        columns: [value]
        min: 10
    tier2: []
  ```
  Save, F5. Raw now shows **8** rows (the step is in Tier 1), the badge says **T2=T1**, and `Result__T2.parquet`
  is **gone** (no false T2 data). `Result.parquet` has a new time.
- [ ] **RT-06 Change the data.** Restore the data analysis recipe (`git checkout -- config/data_analysis_recipes/retest/retest_tier2.yaml`).
  Add a line at the end of `samples.tsv` (tabs between the fields): `s13	A	40	2024`. Save, F5.
  Raw shows **13** rows, Result **9**. Both parquet files have new times.
  Then `git checkout -- assets/test_data/retest/samples.tsv`.
- [ ] **RT-07 Export refused when files changed after the view was opened** (EXPORT-KEYCHECK-1).
  Open `retest_tier2` and **do not reload**. Edit `samples.tsv` as in RT-06 (or change `min:` in the data analysis recipe) and save.
  Left panel Export, click "Export Bundle". Expected: a red notification "Export blocked: the data files (or the data analysis recipe)
  changed since this view was opened. Reload the page (F5)..." and the downloaded zip contains **only**
  `EXPORT_NOT_CREATED.txt`. Read it: it says what changed, what it means, what to do, and lists the keys.
  Then F5, export again: it works. Restore the file with `git checkout`.
  > Check that the text is understandable to you. This is the part that must be clear.

## 2. Export (EXPORT-CHECK-1) — project `retest_tier2`, original files

Left panel Export: bundle label `retest`, scope "Global project", PNG, click "Export Bundle". Unzip it.

- [ ] **RT-10 Content.** `Result/plots/value_by_group.png`, `All_samples/plots/samples_per_year.png`,
  `Result/T1_data.tsv` (**12** rows), `Result/T2_data.tsv` (**8** rows), `All_samples/T1_data.tsv`
  (and **no** `All_samples/T2_data.tsv`), `steps/`, `lineage/`, `report.qmd`, `report.html`, `README.txt`. No `*_ERROR.txt`.
- [ ] **RT-11 Plot = screen.** The exported `value_by_group.png` is the same picture as the Result plot on screen
  (8 values, nothing below 10, groups A B C).
- [ ] **RT-12 Keys.** In `README.txt` (section Reproducibility): Data Analysis Recipe SHA256, Data batch hash, and per dataset
  `tier1_key=...` and `tier2_key=...`. For `All_samples` the tier2 key reads `none (T2 equals T1)`. The same lines are in the
  provenance table of `report.html`. The PNG carries them too (`exiftool` or `identify -verbose file.png | grep sparmvet`).
- [ ] **RT-13 Keys = stored files.** The keys in the README equal the ones inside the parquet files:
  ```
  PYTHONPATH=. ./.venv/bin/python -c "
  import pyarrow.parquet as pq
  for f in ['Result','Result__T2']:
      m = pq.read_metadata(f'tmp/RETEST/user/anchors/{f}.parquet').metadata
      print(f, {k.decode(): v.decode()[:16] for k, v in m.items() if k.startswith(b'sparmvet')})"
  ```
- [ ] **RT-14 Change one thing, export again.** (a) change `min:` (Tier 2 step): only the `tier2_key` of `Result` changes
  and the plot changes; (b) add a row to `samples.tsv`: Data batch hash, `tier1_key` and `tier2_key` change; (c) change an
  included file or a Tier 1 part: Data analysis recipe SHA256 and the keys change. Nothing exported may show the state from before the change.
- [ ] **RT-15 Exploration is never exported.** Left panel Filters: column `value`, operator `<`, value `20`, "Add row", "Apply"
  (this is exploration: nothing is sent to audit). Under the buttons a reminder reads "Sandbox: only steps sent to audit are
  exported." (when "My view" is selected), and the Export panel says the same. Export with "Plot to show" = Result, then with
  My view: both bundles are **identical to an export made without the filter**: same plots, no `FILTERS.txt`, no `T3_data_*` file.
  There is no "Include T3 filtered data" checkbox any more. (Automated: `test_export_download.py::test_exploration_filters_are_never_exported`.)
- [ ] **RT-16 Audited step: plot and data.** Do RT-17 below, then open `Result/T3_data_value_by_group.tsv`: **5** rows
  (`s02 s03 s08 s11 s12`: values below 20 inside the Result of 8). The plot `All_samples` has no audited step: its data stays
  the Result and it has no T3 file. The T3 data is always built on T2 when the join has tier2 steps, on T1 otherwise.
- [ ] **RT-17 Audited steps are always exported** (issue #25; your rule: only what is sent to audit is exported, and it is recorded).
  "Data to show" = My view. Filters: `value < 20`, "Add row", "Send to Audit", "Add to audit pipeline" ("This plot only"), write a
  reason in the right panel, "Apply". Then put **both** views back on **Result**, export. Expected: `Result/T3_data_value_by_group.tsv`
  (**5** rows), `steps/t3_steps.yaml` with your reason, the plot `value_by_group.png` filtered (values below 20), the README
  section "Audited T3 steps (always applied...)" naming `value_by_group: 1 step(s)`, and the T3 Audit Trail with your reason in
  `report.html`. No `FILTERS.txt`. (Checked in a real browser run on 2026-11-06, except the picture.)
- [ ] **RT-18 Pure Result app features.** Launch with `pipeline-static.yaml` instead (deployment B) and `SPARMVET_DATA_ANALYSIS_RECIPE=retest_tier2` (a static page must name its recipe): export still works
  and holds the Result.

## 3. Issue #23: `top_n_other` — project `retest_top_n_other`

Data: 21 rows, 18 samples, 8 variants `V1..V8` and 1 missing value. Sample `s07` has 4 rows of `V2`. The data analysis recipe keeps the
top **3** variants, counting the number of different samples (`count_distinct: sample_id`).

- [ ] **RT-20 Result.** Home shows the plot "Rows per grouped variant" (if the area is empty, click the tab: known bug, see
  section 5). Bars: **Other 9, V1 6, V3 3, V4 2, nan 1**. The data preview has the new column `variant_top3`; the missing value
  stays empty (it is not "Other"); the bar `nan` is that one row. V4 is kept, V5 is not: tie of 2 samples, V4 wins alphabetically.
- [ ] **RT-21 Without `count_distinct`.** In `retest_top_n_other.yaml` delete the line `count_distinct: sample_id`, save, F5.
  Now the kept variants count **rows**: bars **V1 6, V2 4, V3 3, Other 7, nan 1**. (V2 is kept because it has 4 rows, although
  only one sample.) Restore the file.
- [ ] **RT-22 Action help.** In BLUEPRINT open the action picker and find `top_n_other`: description and YAML example are shown.

## 4. Issue #18: a failed dataset and a wrong declared field

- [ ] **RT-30 Renamed header.** Select `retest_broken_header`. Home shows a red banner:
  **"Data Assembly Failed: Dataset 'Genes' could not be loaded for 'Genes_joined': Dataset [Genes] Validation Failed.
  Missing columns: ['predicted_phenotype']"**. In `retest_broken_header.yaml` change the path to `genes.tsv`
  (`EDIT HERE`), save, F5: the plot "Genes" appears.
- [ ] **RT-31 Declared field with no column.** Select `retest_bad_output_field`: it loads normally (a data schema's
  `output_fields` is not applied yet). The check is a function, not yet a screen (task VALIDATE-UI-1):
  ```
  PYTHONPATH=. ./.venv/bin/python -c "
  from app.modules.data_analysis_recipe_validator import validate_data_analysis_recipe_data
  for p in validate_data_analysis_recipe_data('config/data_analysis_recipes/retest/retest_bad_output_field.yaml', 'assets/test_data'): print(p)"
  ```
  Expected: `... declared column 'phenotype' matches no column of the dataset  Tip: Did you mean 'predicted_phenotype'?`
  Change `phenotype:` to `predicted_phenotype:` in the file: the command prints nothing.
  > Decided 2026-11-06: a BLUEPRINT button is needed before the demo (issue #26). The command is only for now.

## 5. Issue #21 and other changes of today — deployment A (normal project)

- [ ] **RT-40 #21 MLST.** Project `1_test_data_ST22_dummy`, plot `MLST_counts_bar`: many bars with real sequence types (19 kinds)
  and one bar **"Non Determined"** with 2 samples. No bar called "keep". Same in the facets of `integration_plot`.
- [ ] **RT-41 BLUEPRINT plot error banner** (ADR-045 fix: the render no longer writes state). In BLUEPRINT select a node of a
  plot that has no data yet: a yellow banner above the plot explains it ("No data loaded for ..."). Select a node with data:
  the plot shows and the banner is gone. (Not covered by an automated test.)
- [ ] **RT-42 App features switching.** There is no runtime app features switch (removed earlier, ADR-053). Confirm you do not expect one.
- [ ] **RT-43 Gallery submission debug script.** `PYTHONPATH=. ./.venv/bin/python libs/viz_gallery/tests/debug_gallery_submission.py --data-analysis-recipe config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml --data-dir assets/test_data/1_test_data_ST22_dummy`
  prints "Gallery Bundle materialized" and three PASSED lines (it was broken: a syntax error and an old API).

- [ ] **RT-50 Switching project: lag or blank plot?** Switch between `retest_tier2` and `retest_top_n_other` several times. Note
  (1) how long until the first plot is drawn, (2) whether it is drawn **without** clicking its tab, (3) whether the right panel
  "Pipeline Audit" names the plot you are looking at. In my automated browser the plot stayed empty for 10 seconds until the tab was
  clicked and the audit panel kept the old plot name (same on this morning's code, so not caused by today's changes). You see only a
  short lag, so this may depend on the browser or on a click. Mark `[~]` if only a lag, `[!]` if the plot needs a click.
  (Draft kept in `issue-drafts/switching-project-leaves-first-plot-blank.md`, not created.)

### Known problems found while preparing this

- A data analysis recipe with no `joins` fails with "Untitled_Collection": issue #24.
- Issue #22 (`replace_values` deprecation warning) is **not fixed yet**: running tests still prints the warning.

---

## 6. What the automated tests already cover (do not repeat by hand)

Headless (about 50 s): `PYTHONPATH=. ./.venv/bin/python -m pytest libs app/tests --ignore=app/tests/test_shiny_smoke.py --ignore=app/tests/test_shiny_smoke_blueprint.py --ignore=app/tests/test_export_download.py -q` → 1209 passed on 2026-11-06.
Browser (about 3 min): `PYTHONPATH=. SPARMVET_APP_FEATURES=qa ./.venv/bin/python -m pytest app/tests/test_shiny_smoke.py app/tests/test_shiny_smoke_blueprint.py app/tests/test_export_download.py -q` → 33 passed, 3 skipped.

| Covered | Test |
|---|---|
| Tier 2 stored, reused, recomputed, removed; corrupt file; categorical columns read back | `app/tests/test_tier2_store.py` |
| Chained keys and cache rebuild rules | `test_cache_chain.py`, `test_cache_keys.py` |
| Every shipped plot renders from the stored Tier 2 | `test_render_every_plot.py` |
| Export keys recorded; export refused after a change; My view build T3 > T2 > T1 | `test_export_provenance.py`, `test_export_view_consistency.py` |
| A real export download (keys in the README, no error files, refused after a data change) | `test_export_download.py` |
| The retest data analysis recipes give the numbers of this procedure | `test_retest_data_analysis_recipes.py` |
| No render writes a reactive value (ADR-045) | `test_render_purity.py` |

## 7. After the retest

Close the issues that pass (#18, #21, #23, #10) with the comment "retested, passes" and the date; for each `[!]` write the
one-line note and I fix it. Decisions already taken 2026-11-06: the export is the Result plus the audited steps and exploration is never exported (#25); a BLUEPRINT validate button is needed (#26).
