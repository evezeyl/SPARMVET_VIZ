# Retest procedure

**Purpose.** Check, by hand and by script, that the stored tiers, the cache keys, the export and the load gate behave as specified, using small recipes with known numbers (deployment `retest`). It is the manual counterpart of the automated suites and the place where a person looks at the screen and at the files.
**When to run it.** After any change to the orchestrator, the cache keys, the tier stores, the export, the load gate or the recipe loader, and before a release. **Scripted counterpart:** `assets/scripts/retest_walkthrough.py` runs RT-01 to RT-07, RT-30 and RT-31 in a real browser (about 4 minutes) and puts the edited files back; the numbers of the recipes are pinned by `app/tests/test_retest_data_analysis_recipes.py`. If a number is different for you, that is a finding.
**Markers.** `[ ]` not tested, `[x]` pass, `[!]` fail, `[~]` polish, `[?]` decision. On a failure add one line starting with `>` with what you saw against what was expected.
**Screen words.** The steps below use the words of the HOME as it is built (Data to show: Raw / Result / My view; Plot to show; Pipeline Audit). The numbers and the files do not change with the redesign; the words do. When the new HOME is built (package P9 of `.claude/design/home_stage2_mechanism_spec.md`) the wording here and in the script is updated in the same commit.
Chrome: developer console, Network tab, "Disable cache" on.

---

## 0. Launch

**A. Your normal data analysis recipe** (the export and the plots of the real dummy data analysis recipe):

```
PYTHONPATH=. SPARMVET_APP_FEATURES=config/app_features/developer.yaml ./.venv/bin/shiny run app/src/main.py --reload --port 8000
```

**B. The retest set** (small data analysis recipes with known numbers; its own cache, `tmp/RETEST/`, apart from your
normal `tmp/UI_TEST/`):

```
PYTHONPATH=. SPARMVET_DEPLOYMENT=config/deployment/local/retest.yaml SPARMVET_APP_FEATURES=config/app_features/qa.yaml ./.venv/bin/shiny run app/src/main.py --port 8000
```

The qa app features has every feature on (filters, My view, T3, export). In the left panel "Data analysis recipe Choice" you
see four data analysis recipes: `retest_tier2`, `retest_top_n_other`, `retest_broken_header`, `retest_bad_output_field`.

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

## 1. Tier 2 stored as a parquet with a chained key — data analysis recipe `retest_tier2`

The data: 12 samples (`s01`..`s12`), columns `group` (A, B, C), `value`, `year`. The join **Result** has one
tier2 step: keep `value >= 10`. The join **All_samples** has no tier2 step.

- [ ] **RT-01 Load.** Select `retest_tier2`. Tab "Value by group": box plot, badge "Viewing: Result".
  "Data to show: Raw" shows **12** rows, "Result" shows **8** (`s02 s03 s05 s06 s08 s09 s11 s12`).
  Tab "Samples per year": Result shows 12 rows and the badge has the note **T2=T1**.
  The right panel "Pipeline Audit" lists `[Tier 2] filter_range`.
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
- [ ] **RT-07 Export refused when files changed after the view was opened**.
  Open `retest_tier2` and **do not reload**. Edit `samples.tsv` as in RT-06 (or change `min:` in the data analysis recipe) and save.
  Left panel Export, click "Export Bundle". Expected: a red notification "Export blocked: the data files (or the data analysis recipe)
  changed since this view was opened. Reload the page (F5)..." and the downloaded zip contains **only**
  `EXPORT_NOT_CREATED.txt`. Read it: it says what changed, what it means, what to do, and lists the keys.
  Then F5, export again: it works. Restore the file with `git checkout`.
  > Check that the text is understandable to you. This is the part that must be clear.

## 2. Export — data analysis recipe `retest_tier2`, original files

Left panel Export: bundle label `retest`, scope "Global", PNG, click "Export Bundle". Unzip it.

- [ ] **RT-10 Content.** `Result/plots/value_by_group.png`, `All_samples/plots/samples_per_year.png`,
  `Result/T1_data.tsv` (**12** rows), `Result/T2_data.tsv` (**8** rows), `All_samples/T1_data.tsv`
  (and **no** `All_samples/T2_data.tsv`), `data_analysis_recipes/`, `lineage/`, `report.qmd`, `report.html`, `README.txt`. No `*_ERROR.txt`.
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
- [ ] **RT-17 Audited steps are always exported** (only what is sent to audit is exported, and it is recorded).
  "Data to show" = My view. Filters: `value < 20`, "Add row", "Send to Audit", "Add to audit pipeline" ("This plot only"), write a
  reason in the right panel, "Apply". Then put **both** views back on **Result**, export. Expected: `Result/T3_data_value_by_group.tsv`
  (**5** rows), `data_analysis_recipes/t3_steps.yaml` with your reason, the plot `value_by_group.png` filtered (values below 20), the README
  section "Audited T3 steps (always applied...)" naming `value_by_group: 1 step(s)`, and the T3 Audit Trail with your reason in
  `report.html`. No `FILTERS.txt`.
- [ ] **RT-18 Pure Result app features.** Launch with `pipeline-static.yaml` instead (deployment B) and `SPARMVET_DATA_ANALYSIS_RECIPE=retest_tier2` (a static page must name its data analysis recipe): export still works
  and holds the Result.

## 3. `top_n_other` — data analysis recipe `retest_top_n_other`

Data: 21 rows, 18 samples, 8 variants `V1..V8` and 1 missing value. Sample `s07` has 4 rows of `V2`. The data analysis recipe keeps the
top **3** variants, counting the number of different samples (`count_distinct: sample_id`).

- [ ] **RT-20 Result.** Home shows the plot "Rows per grouped variant" (if the area is empty, report it: the plot must draw without a click). Bars: **Other 9, V1 6, V3 3, V4 2, nan 1**. The data preview has the new column `variant_top3`; the missing value
  stays empty (it is not "Other"); the bar `nan` is that one row. V4 is kept, V5 is not: tie of 2 samples, V4 wins alphabetically.
- [ ] **RT-21 Without `count_distinct`.** In `retest_top_n_other.yaml` delete the line `count_distinct: sample_id`, save, F5.
  Now the kept variants count **rows**: bars **V1 6, V2 4, V3 3, Other 7, nan 1**. (V2 is kept because it has 4 rows, although
  only one sample.) Restore the file.
- [ ] **RT-22 Action help.** In BLUEPRINT open the action picker and find `top_n_other`: description and YAML example are shown.

## 4. The load gate: a recipe that fails its checks is refused and listed

The gate runs once per process, at startup (ADR-094): a recipe that fails the structure check or the data check is not offered in the selector and appears beneath it, with its problems and a contact. After you fix a file, **restart the server** (F5 is not enough for this check).

- [ ] **RT-30 Renamed header.** Launch deployment B (section 0) and open any retest recipe. Beneath the selector "Data analysis recipe" the panel says it lists unavailable recipes and shows `retest_broken_header` in red with
  *"data_schemas.Genes: dataset cannot be loaded: Column(s) ['predicted_phenotype'] declared in input_fields for 'Genes' not found in the source file (expected file headers: ['predicted_phenotype'])"*. It cannot be selected. In `retest_broken_header.yaml` change the path to `genes.tsv` (`EDIT HERE`), restart: the recipe is selectable and its plot "Genes" appears.
- [ ] **RT-31 Declared field with no column.** The same list shows `retest_bad_output_field` with
  *"data_schemas.Genes.output_fields.phenotype: declared column 'phenotype' matches no column of the dataset  Tip: Did you mean 'predicted_phenotype'?"*.
  Change `phenotype:` to `predicted_phenotype:` in the file, restart: it is selectable. The same check runs on demand in BLUEPRINT with "Validate data analysis recipe" (advisory there: nothing is hidden).

## 5. Other checks with the normal recipe (deployment A)

- [ ] **RT-40 MLST.** Recipe `1_test_data_ST22_dummy`, plot `MLST_counts_bar`: many bars with real sequence types (19 kinds) and one bar **"Non Determined"** with 2 samples. No bar called "keep". Same in the facets of `integration_plot`.
- [ ] **RT-41 BLUEPRINT plot error banner.** In BLUEPRINT select a node of a plot that has no data yet: a yellow banner above the plot explains it ("No data loaded for ..."). Select a node with data: the plot shows and the banner is gone. (Not covered by an automated test.)

---

## 6. What the automated tests already cover (do not repeat by hand)

Commands: `rules_verification_testing.md` section 8 (headless baseline and browser gate).

| Covered | Test |
|---|---|
| Tier 2 stored, reused, recomputed, removed; corrupt file; categorical columns read back | `app/tests/test_tier2_store.py` |
| Chained keys and cache rebuild rules | `test_cache_chain.py`, `test_cache_keys.py` |
| Every shipped plot renders from the stored Tier 2 | `test_render_every_plot.py` |
| Export keys recorded; export refused after a change; My view build T3 > T2 > T1 | `test_export_provenance.py`, `test_export_view_consistency.py` |
| A real export download (keys in the README, no error files, refused after a data change, exploration never exported) | `test_export_download.py` |
| The retest recipes give the numbers of this procedure | `test_retest_data_analysis_recipes.py` |
| The load gate refuses a failing recipe and lists it | `test_data_analysis_recipe_load_gate.py` |
| No render writes a reactive value (ADR-045) | `test_render_purity.py` |

## 7. When a check fails

Write the id, what you saw and what was expected; open one issue per problem (`gh issue create -R evezeyl/SPARMVET_VIZ`, a draft first in `issue-drafts/`); when it is fixed, re-run the check and tick it. A change of the procedure goes in the same commit as the change of behaviour it follows.
