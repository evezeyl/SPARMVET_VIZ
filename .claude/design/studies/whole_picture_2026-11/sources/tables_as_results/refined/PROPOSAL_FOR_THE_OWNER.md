# Where tier 3, `from:` and the results go: the refined proposal, with complete files (2026-11-22)

For you, after your order of channel block M555. Written by an Opus worker for the coordinator.
Your words that this answers: "where would go T3 for the reads summary for example ? where would be the from: located" and "I want the examples on how it would like like with all the tiers and both plot and data as result".
Every file in this document is complete: no `{...}`, no `[...]`, no "and so on". The tables, the columns and the steps are those of the demo recipe `1_test_data_ST22_dummy`. One step is not in the demo, and it is marked so.
Labels: **run** = I ran it with the real engine; **read** = I read it in the code at file:line; **reasoned** = my reasoning, not run.

---

## Part 0. Flags first, then the recommendation

### Flags: what could change a result silently or hide a step
1. **Form 4 (a result may keep steps of its own).** A plot and a table that read the same table can show different numbers when one of them adds a filter of its own. And the summary can again be written inside a result, which is the problem you raised. The screen would have to say "this result adds N steps of its own". (reasoned)
2. **Every form with a shared table.** An audit step written at a shared table changes EVERY result that reads it, also through a table made from it. Run on the demo data: one sample removed at the table of result A after its tier 2 changed result A (sequence type 428: 2 samples to 1) AND both results of the derived table (Norway 2024: 19 samples to 18). The dialog must list all of them before you confirm. (run, `try/out/audit_walk.out`)
3. **Two rules of reading.** Today a join reads the tier 1 of its ingredients (read, `app/modules/orchestrator.py:273`). `from:` would read the last stage of its table (after tier 2). If someone "unifies" this and lets joins read tier 2 too, results change silently: the source table `ResFinder` has a tier 2 (it adds `total_gene_count` and sorts) and is an ingredient of four joins of the demo. This must be your decision, with tests, never a side effect. (read, demo recipe lines 98-108, `wrangling/ResFinder_wrangling_tier2.yaml`, and the four joins that list `ResFinder`)
4. **Form 5 (named tier 3 stages inside a table).** A stage has ONE list of steps. When that list ends with a summary, a sample can no longer be removed there (`sample_id` is gone). The user must then remove it higher up, where it also changes the other result. That limit is hidden from the user unless the dialog says it. (run: the summary has the columns `country`, `year_label`, `n_samples` only)
5. **The check refuses a valid case today.** The tier 2 of a join that only a derived table reads is refused (code J14: "no plot reads this join"). Run on the form 3 file. The check must count a derived table as a reader, or a correct recipe is blocked. (run, `try/out/check_new_forms.out`; read, `libs/utils/src/utils/recipe_check.py:820-828`)
6. **One result id in two groups is not refused by a plain rule.** The second entry silently replaces the first when the app lists the plots (read, `libs/utils/src/utils/recipe_tiers.py:152-160`). The checker reports nothing; the gate refuses the recipe only through an internal fault ("the recipe check did not cover: columns ... a fault of the app"). With `from:` and results, ids must be unique across the whole recipe, with a plain refusal. (run, `try/out/check_duplicate_ids.out`)

### The recommendation in five lines (mine; yours to accept, change or refuse)
1. **Form 3.** Every data step is written in the data part, before it is used: source tables, then joins, then derived tables, then the results.
2. A **derived table** is a table made from ONE other table. It has `from:` and its own tier 1 and tier 2, like any table. It lives in a block of its own, `derived_tables`.
3. A **result** says what it is (`result: plot` or `result: table`) and which table it shows (`from:`). It has no steps of its own. A plot result adds its drawing (`mapping`, `layers`).
4. **"This result only" stays** in the audit: the audit writes its steps in the result's own tier 3, as you decided on 2026-11-20 (D-0346). Only the audit writes there; the author never does.
5. So a plot and its table that read the same table show the same numbers, by construction. If you want authors to add finishing steps to one result, form 4 is the alternative, with the warnings of flag 1.

---

## Part 1. The hierarchy, and your two questions

### Your two questions, answered plainly
**"Where would go T3 for the reads summary?"**
In form 3 the reads summary is not a tier 3 any more. It is a table of the data part, `FastP_reads_summary`, in the block `derived_tables`. It is written after the joins and before the results. Its steps are its own tier 1 (one row per sample, with a year label) and its own tier 2 (the summary). The result that shows it only names it. The complete file is in Part 2, section 2.6.
In form 4: the same, and a result may add a `tier3` of its own inside the result (for example a sort).
In form 5: it would be a named `tier3` stage inside the join `FastP_with_metadata`.

**"Where would be the `from:` located?"**
`from:` is a key of the derived table. It is written right after its `label` and `description`, and before its `tier1`. It names the ONE table the derived table is made from. That table is read at its last stage: after its tier 2, or after its tier 1 when it has no tier 2.
My suggestion: the same word `from:` in each result, in place of today's `target_dataset`, to name the table the result shows. Then one word means one thing: "the one table this reads, at its last stage".
A join does not use `from:`. It keeps `ingredients:`, and it reads the tier 1 of each ingredient, as today.

### Form 3 (recommended): the levels
```text
Level  Block (where in the file)          What is DEFINED there                                What it may USE (from above)
1      data_schemas, metadata_schema      a table read from a file; its tier 1 and tier 2      a file
2      joins                              a table made by joining several tables;              the tier 1 of each ingredient (level 1)
                                          its tier 1 and tier 2
3      derived_tables                     a table made from ONE table; its tier 1 and tier 2   from: one table of level 1, 2, or a derived
                                                                                               table written above it, at its last stage
-      plot_defaults                      defaults of the plots (the theme)                    nothing
4      analysis_groups -> results         what is shown: result: plot | table;                 from: one table of level 1, 2 or 3,
                                          for a plot, the drawing (mapping, layers)            at its last stage; plot_defaults
(4a)   the result's tier3                 written by the AUDIT only ("this result only")      the table the result reads
```
The order in which a reader meets things in the file: `id`, the engines and `info`; the source tables (each with its fields, its tier 1, its tier 2); the joins (ingredients, tier 1, tier 2); the derived tables (`from:`, tier 1, tier 2); `plot_defaults`; the groups and their results (`result:`, `from:`, then the drawing).

"A definition comes before its use", block by block:
- A source table uses only a file. Nothing has to be defined before it.
- A join uses the tables named in `ingredients`. They are defined above it.
- A derived table uses the table named in `from:`. It is defined above it: a source table, a join, or a derived table written earlier in the block.
- `plot_defaults` uses nothing. It is used by the plot results, so it is written before them. (In the demo it is at the end of the file. Moving it up changes no number; it is my suggestion.)
- A result uses the table named in `from:`, defined above it. Its drawing uses only the columns of that table.

### Form 4: the levels
The same as form 3, with one change at level 4: a result MAY hold a `tier3` with steps of its own. They are defined inside the result and used by that result only. The audit writes its "this result only" steps in the same `tier3`, after the author's.

### Form 5 (your words read literally: "T3a" is a tier of table a): the levels
```text
Level  Block                              What is DEFINED there                                What it may USE
1      data_schemas, metadata_schema      a table read from a file; tier 1, tier 2             a file
2      joins                              a joined table; tier 1, tier 2, and named tier 3     the tier 1 of each ingredient; a named tier 3
                                          stages (each one list of steps)                      stage reads the table after its tier 2
-      plot_defaults                      defaults of the plots                                nothing
3      analysis_groups -> results         result: plot | table; the drawing                    from: a table (its tier 2), or from: {table,
                                                                                               tier3: <name>} (that named stage)
```
There is no derived-table block. A stage made from a table is written inside that table, under `tier3`.

---

## Part 2. Complete files, on the real demo recipe

### The slice I chose, and why
- Two source tables: `MLST` (its real tier 1: three steps) and `metadata_schema` (tier 1 with no steps). The demo gives neither a tier 2.
- One join: `MLST_with_metadata`. Its tier 1 is the real left join on `sample_id`. Its tier 2 is real: it adds `era` and keeps the years 2023 to 2025. It is the only small join of the demo with a real tier 2, which your case needs ("T2a").
- One plot result: `mlst_bar`, the demo's plot, complete (`mapping`, `layers` with `labs`, and the theme from `plot_defaults`).
- A summary: samples per country and year. Its two steps are the real steps of the demo's `QA_aggregated_no_key` (a year label, then a count per country and year), now applied to `MLST_with_metadata` after its tier 2.
- The summary is shown twice: as a plot and as a table. So you can see that a plot and its table read the same table.
- To keep the files readable, `MLST` declares 3 of its 10 columns. Its tier 1 keeps only these 3 anyway (its first step selects them).
This slice IS your case: result A = `mlst_bar` reads `MLST_with_metadata` after its tier 2 (your "T2a"); the derived table B = `MLST_samples_per_country_year` is made from that same stage (your "T3a"); results B read it. Part 3 walks through it.

### 2.1 Today (for reference): what changes
Today a table cannot be a result. The summary can only be the tier 3 of a plot. A second result that wanted the same numbers would have to copy the steps. This file passes the check and builds (Part 6).
```yaml
id: slice_today
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: ST22 slice, written as today
  description: "MLST and metadata joined; a plot of sequence types; a summary of samples per country and year, which today can only be the tier 3 of a plot."

data_schemas:
  MLST:
    label: "MLST"
    description: "Multilocus Typing (Strain Classification)"
    source:
      type: local_tsv
      path: ./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv
    null_values: []
    strip: true
    input_fields:
      sample_id:
        original_name: "sample_id"
        type: String
        label: "Sample ID"
        is_entity_key: true
      scheme:
        original_name: "Scheme"
        type: String
        null_values: ["N/A"]
        label: "MLST Scheme"
      sequence_type:
        original_name: "Sequence Type"
        type: String
        null_values: ["-"]
        label: "Sequence Type"
    tier1:
      steps:
        - action: polars_select
          exprs: [sample_id, scheme, sequence_type]
        - action: polars_with_columns
          named_exprs:
            sequence_type: "pl.col('sequence_type').replace_strict({'unknown': 'Non Determined'}, default=pl.col('sequence_type'))"
        - action: polars_fill_null
          columns: [sequence_type]
          value: Non Determined

metadata_schema:
  label: "metadata"
  description: "Metadata (Metadata)"
  source:
    type: local_tsv
    path: ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv
  null_values: []
  strip: true
  input_fields:
    sample_id:
      original_name: "sample_id"
      type: String
      null_values: ["", "-"]
      label: "Sample ID"
      is_entity_key: true
    source:
      original_name: "Source"
      type: String
      label: "Biological Source"
    year:
      original_name: "Year"
      type: Float64
      label: "Collection Year"
    country:
      original_name: "Country"
      type: String
      label: "Origin Country"
  tier1:
    steps: []

joins:
  MLST_with_metadata:
    label: "MLST with metadata"
    description: "One row per sample: sequence type with source, year and country (left join); the second stage keeps only the years 2023 to 2025 and adds an era (Early before 2024, Recent from 2024)."
    ingredients:
      - dataset_id: MLST
      - dataset_id: metadata_schema
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: left
          maintain_order: left_right
    tier2:
      steps:
        - action: polars_with_columns
          named_exprs:
            era: "pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Recent'))"
        - action: modif_filter
          column: year
          op: between
          value: [2023, 2025]
          na: remove

analysis_groups:
  Results:
    ui_label: "AMR and Virulence"
    description: "Which sequence types, and how many samples per country and year."
    plots:
      mlst_bar:
        ui_label: "MLST Bar"
        ui_title: MLST Sequence Type Distribution by Country
        description: "Bar chart showing the frequency of MLST sequence types, filled by the origin country."
        target_dataset: MLST_with_metadata
        mapping:
          x: sequence_type
          fill: country
        layers:
          - name: geom_bar
            params: {}
          - name: scale_x_discrete
            params: {}
          - name: labs
            params:
              title: MLST Sequence Type Distribution by Country
      samples_per_country_year_bar:
        ui_label: "Samples per country and year"
        ui_title: "Samples per country and year (2023 to 2025)"
        description: "Number of samples per country and year, after the filter of the years 2023 to 2025."
        target_dataset: MLST_with_metadata
        mapping:
          x: country
          y: n_samples
          fill: year_label
        layers:
          - name: geom_col
            params: {}
          - name: labs
            params:
              title: "Samples per country and year (2023 to 2025)"
              x: Country
              y: Samples
        tier3:
          steps:
            - action: polars_with_columns
              named_exprs:
                year_label: "pl.col('year').cast(pl.Int64).cast(pl.String)"
            - action: polars_group_by
              by: [country, year_label]
              maintain_order: true
              named_aggs:
                n_samples: "pl.col('sample_id').count()"

plot_defaults:
  theme: theme_minimal
```

### 2.2 Form 3 (recommended): derived tables; a result has no steps of its own
```yaml
id: slice_form3
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: ST22 slice, form 3
  description: "MLST and metadata joined; a plot of sequence types; a summary of samples per country and year, shown as a plot and as a table."

# ── 1. Source tables (read from files) ─────────────────────────────────────────
data_schemas:
  MLST:
    label: "MLST"
    description: "Multilocus Typing (Strain Classification)"
    source:
      type: local_tsv
      path: ./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv
    null_values: []
    strip: true
    input_fields:
      sample_id:
        original_name: "sample_id"
        type: String
        label: "Sample ID"
        is_entity_key: true
      scheme:
        original_name: "Scheme"
        type: String
        null_values: ["N/A"]
        label: "MLST Scheme"
      sequence_type:
        original_name: "Sequence Type"
        type: String
        null_values: ["-"]
        label: "Sequence Type"
    tier1:
      steps:
        - action: polars_select
          exprs: [sample_id, scheme, sequence_type]
        - action: polars_with_columns
          named_exprs:
            sequence_type: "pl.col('sequence_type').replace_strict({'unknown': 'Non Determined'}, default=pl.col('sequence_type'))"
        - action: polars_fill_null
          columns: [sequence_type]
          value: Non Determined
    tier2:
      steps: []          # empty: T2 = T1. A join reads tier 1 of its ingredients, so this tier 2 is read only by a result or a derived table that reads MLST itself.

metadata_schema:
  label: "metadata"
  description: "Metadata (Metadata)"
  source:
    type: local_tsv
    path: ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv
  null_values: []
  strip: true
  input_fields:
    sample_id:
      original_name: "sample_id"
      type: String
      null_values: ["", "-"]
      label: "Sample ID"
      is_entity_key: true
    source:
      original_name: "Source"
      type: String
      label: "Biological Source"
    year:
      original_name: "Year"
      type: Float64
      label: "Collection Year"
    country:
      original_name: "Country"
      type: String
      label: "Origin Country"
  tier1:
    steps: []
  tier2:
    steps: []            # empty: T2 = T1 (same remark as for MLST)

# ── 2. Joins (several tables joined; each ingredient is read after its tier 1) ─
joins:
  MLST_with_metadata:
    label: "MLST with metadata"
    description: "One row per sample: sequence type with source, year and country (left join); the second stage keeps only the years 2023 to 2025 and adds an era (Early before 2024, Recent from 2024)."
    ingredients:
      - dataset_id: MLST
      - dataset_id: metadata_schema
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: left
          maintain_order: left_right
    tier2:
      steps:
        - action: polars_with_columns
          named_exprs:
            era: "pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Recent'))"
        - action: modif_filter
          column: year
          op: between
          value: [2023, 2025]
          na: remove

# ── 3. Derived tables (one table made from another, read at its last stage) ───
derived_tables:
  MLST_samples_per_country_year:
    label: "MLST samples per country and year"
    description: "One row per country and year: the number of samples, counted after the filter of the years 2023 to 2025. Tier 1 keeps one row per sample (sample_id is still here); tier 2 is the aggregate (no sample_id)."
    from: MLST_with_metadata        # reads MLST_with_metadata at its last stage: after its tier 2 (33 rows)
    tier1:
      steps:
        - action: polars_with_columns
          named_exprs:
            year_label: "pl.col('year').cast(pl.Int64).cast(pl.String)"
    tier2:
      steps:
        - action: polars_group_by
          by: [country, year_label]
          maintain_order: true
          named_aggs:
            n_samples: "pl.col('sample_id').count()"

# ── Defaults read by every plot result (written before the results that use them) ─
plot_defaults:
  theme: theme_minimal

# ── 4. Results (each reads ONE table at its last stage; no data steps here) ───
analysis_groups:
  Results:
    ui_label: "AMR and Virulence"
    description: "Which sequence types, and how many samples per country and year."
    results:
      mlst_bar:
        ui_label: "MLST Bar"
        ui_title: MLST Sequence Type Distribution by Country
        description: "Bar chart showing the frequency of MLST sequence types, filled by the origin country."
        result: plot
        from: MLST_with_metadata    # no steps of its own: it shows MLST_with_metadata after tier 2
        mapping:
          x: sequence_type
          fill: country
        layers:
          - name: geom_bar
            params: {}
          - name: scale_x_discrete
            params: {}
          - name: labs
            params:
              title: MLST Sequence Type Distribution by Country
      samples_per_country_year_bar:
        ui_label: "Samples per country and year"
        ui_title: "Samples per country and year (2023 to 2025)"
        description: "Number of samples per country and year, after the filter of the years 2023 to 2025."
        result: plot
        from: MLST_samples_per_country_year
        mapping:
          x: country
          y: n_samples
          fill: year_label
        layers:
          - name: geom_col
            params: {}
          - name: labs
            params:
              title: "Samples per country and year (2023 to 2025)"
              x: Country
              y: Samples
      samples_per_country_year:
        ui_label: "Samples per country and year (table)"
        ui_title: "Samples per country and year (2023 to 2025), as a table"
        description: "The same table as the plot beside it: one row per country and year with the number of samples."
        result: table
        from: MLST_samples_per_country_year
```
What each result shows (numbers run on the demo data, Part 6):
- `mlst_bar`: `MLST_with_metadata` after its tier 2: 33 rows (one per sample of 2023 to 2025).
- `samples_per_country_year_bar` and `samples_per_country_year`: the same table, `MLST_samples_per_country_year` after its tier 2: 6 rows. The plot draws them; the table result shows them in the data preview.
- No result has steps of its own, so each result shows exactly the last stage of the table it names (T3 = T2).

### 2.3 Form 4: derived tables; a result may add steps of its own
The file of form 3, with one difference: the table result adds a sort, for itself only. That step is NOT in the demo; it is an example.
```yaml
id: slice_form4
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: ST22 slice, form 4
  description: "MLST and metadata joined; a plot of sequence types; a summary of samples per country and year, shown as a plot and as a table."

# ── 1. Source tables (read from files) ─────────────────────────────────────────
data_schemas:
  MLST:
    label: "MLST"
    description: "Multilocus Typing (Strain Classification)"
    source:
      type: local_tsv
      path: ./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv
    null_values: []
    strip: true
    input_fields:
      sample_id:
        original_name: "sample_id"
        type: String
        label: "Sample ID"
        is_entity_key: true
      scheme:
        original_name: "Scheme"
        type: String
        null_values: ["N/A"]
        label: "MLST Scheme"
      sequence_type:
        original_name: "Sequence Type"
        type: String
        null_values: ["-"]
        label: "Sequence Type"
    tier1:
      steps:
        - action: polars_select
          exprs: [sample_id, scheme, sequence_type]
        - action: polars_with_columns
          named_exprs:
            sequence_type: "pl.col('sequence_type').replace_strict({'unknown': 'Non Determined'}, default=pl.col('sequence_type'))"
        - action: polars_fill_null
          columns: [sequence_type]
          value: Non Determined
    tier2:
      steps: []          # empty: T2 = T1. A join reads tier 1 of its ingredients, so this tier 2 is read only by a result or a derived table that reads MLST itself.

metadata_schema:
  label: "metadata"
  description: "Metadata (Metadata)"
  source:
    type: local_tsv
    path: ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv
  null_values: []
  strip: true
  input_fields:
    sample_id:
      original_name: "sample_id"
      type: String
      null_values: ["", "-"]
      label: "Sample ID"
      is_entity_key: true
    source:
      original_name: "Source"
      type: String
      label: "Biological Source"
    year:
      original_name: "Year"
      type: Float64
      label: "Collection Year"
    country:
      original_name: "Country"
      type: String
      label: "Origin Country"
  tier1:
    steps: []
  tier2:
    steps: []            # empty: T2 = T1 (same remark as for MLST)

# ── 2. Joins (several tables joined; each ingredient is read after its tier 1) ─
joins:
  MLST_with_metadata:
    label: "MLST with metadata"
    description: "One row per sample: sequence type with source, year and country (left join); the second stage keeps only the years 2023 to 2025 and adds an era (Early before 2024, Recent from 2024)."
    ingredients:
      - dataset_id: MLST
      - dataset_id: metadata_schema
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: left
          maintain_order: left_right
    tier2:
      steps:
        - action: polars_with_columns
          named_exprs:
            era: "pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Recent'))"
        - action: modif_filter
          column: year
          op: between
          value: [2023, 2025]
          na: remove

# ── 3. Derived tables (one table made from another, read at its last stage) ───
derived_tables:
  MLST_samples_per_country_year:
    label: "MLST samples per country and year"
    description: "One row per country and year: the number of samples, counted after the filter of the years 2023 to 2025. Tier 1 keeps one row per sample (sample_id is still here); tier 2 is the aggregate (no sample_id)."
    from: MLST_with_metadata        # reads MLST_with_metadata at its last stage: after its tier 2 (33 rows)
    tier1:
      steps:
        - action: polars_with_columns
          named_exprs:
            year_label: "pl.col('year').cast(pl.Int64).cast(pl.String)"
    tier2:
      steps:
        - action: polars_group_by
          by: [country, year_label]
          maintain_order: true
          named_aggs:
            n_samples: "pl.col('sample_id').count()"

# ── Defaults read by every plot result (written before the results that use them) ─
plot_defaults:
  theme: theme_minimal

# ── 4. Results (each reads ONE table at its last stage; it MAY add steps of its own, for itself only) ─
analysis_groups:
  Results:
    ui_label: "AMR and Virulence"
    description: "Which sequence types, and how many samples per country and year."
    results:
      mlst_bar:
        ui_label: "MLST Bar"
        ui_title: MLST Sequence Type Distribution by Country
        description: "Bar chart showing the frequency of MLST sequence types, filled by the origin country."
        result: plot
        from: MLST_with_metadata    # no tier3 here: T3 = T2, it shows MLST_with_metadata after tier 2
        mapping:
          x: sequence_type
          fill: country
        layers:
          - name: geom_bar
            params: {}
          - name: scale_x_discrete
            params: {}
          - name: labs
            params:
              title: MLST Sequence Type Distribution by Country
      samples_per_country_year_bar:
        ui_label: "Samples per country and year"
        ui_title: "Samples per country and year (2023 to 2025)"
        description: "Number of samples per country and year, after the filter of the years 2023 to 2025."
        result: plot
        from: MLST_samples_per_country_year
        mapping:
          x: country
          y: n_samples
          fill: year_label
        layers:
          - name: geom_col
            params: {}
          - name: labs
            params:
              title: "Samples per country and year (2023 to 2025)"
              x: Country
              y: Samples
      samples_per_country_year:
        ui_label: "Samples per country and year (table)"
        ui_title: "Samples per country and year (2023 to 2025), as a table"
        description: "The table of the plot beside it, sorted by country and year for reading: one row per country and year with the number of samples."
        result: table
        from: MLST_samples_per_country_year
        tier3:                      # this result's own last steps; the plot beside it does not get them [example step, not in the demo]
          steps:
            - action: polars_sort
              by: [country, year_label]
              maintain_order: true
```
What each result shows:
- `mlst_bar`: no `tier3`, so it shows `MLST_with_metadata` after its tier 2 (T3 = T2): 33 rows.
- `samples_per_country_year_bar`: no `tier3`: the 6 rows of the derived table, in the order of the count.
- `samples_per_country_year`: its own `tier3` sorts the 6 rows by country and year (reasoned from the 6 rows: France 2023, France 2024, Germany 2023, Germany 2024, Norway 2023, Norway 2024). The numbers are the same as the plot's; only the order differs. With a filter instead of a sort, the numbers would differ (flag 1).

### 2.4 Form 5: named tier 3 stages inside a table (your words read literally)
```yaml
id: slice_form5
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: ST22 slice, form 5
  description: "MLST and metadata joined; a plot of sequence types; a summary of samples per country and year, shown as a plot and as a table."

# ── 1. Source tables (read from files) ─────────────────────────────────────────
data_schemas:
  MLST:
    label: "MLST"
    description: "Multilocus Typing (Strain Classification)"
    source:
      type: local_tsv
      path: ./assets/test_data/1_test_data_ST22_dummy/test_data_MLST_results_20260307_105756.tsv
    null_values: []
    strip: true
    input_fields:
      sample_id:
        original_name: "sample_id"
        type: String
        label: "Sample ID"
        is_entity_key: true
      scheme:
        original_name: "Scheme"
        type: String
        null_values: ["N/A"]
        label: "MLST Scheme"
      sequence_type:
        original_name: "Sequence Type"
        type: String
        null_values: ["-"]
        label: "Sequence Type"
    tier1:
      steps:
        - action: polars_select
          exprs: [sample_id, scheme, sequence_type]
        - action: polars_with_columns
          named_exprs:
            sequence_type: "pl.col('sequence_type').replace_strict({'unknown': 'Non Determined'}, default=pl.col('sequence_type'))"
        - action: polars_fill_null
          columns: [sequence_type]
          value: Non Determined
    tier2:
      steps: []          # empty: T2 = T1. A join reads tier 1 of its ingredients, so this tier 2 is read only by a result or a derived table that reads MLST itself.

metadata_schema:
  label: "metadata"
  description: "Metadata (Metadata)"
  source:
    type: local_tsv
    path: ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv
  null_values: []
  strip: true
  input_fields:
    sample_id:
      original_name: "sample_id"
      type: String
      null_values: ["", "-"]
      label: "Sample ID"
      is_entity_key: true
    source:
      original_name: "Source"
      type: String
      label: "Biological Source"
    year:
      original_name: "Year"
      type: Float64
      label: "Collection Year"
    country:
      original_name: "Country"
      type: String
      label: "Origin Country"
  tier1:
    steps: []
  tier2:
    steps: []            # empty: T2 = T1 (same remark as for MLST)

# ── 2. Joins (several tables joined; each ingredient is read after its tier 1); a table may hold named tier 3 stages ─
joins:
  MLST_with_metadata:
    label: "MLST with metadata"
    description: "One row per sample: sequence type with source, year and country (left join); the second stage keeps only the years 2023 to 2025 and adds an era (Early before 2024, Recent from 2024)."
    ingredients:
      - dataset_id: MLST
      - dataset_id: metadata_schema
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: left
          maintain_order: left_right
    tier2:
      steps:
        - action: polars_with_columns
          named_exprs:
            era: "pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Recent'))"
        - action: modif_filter
          column: year
          op: between
          value: [2023, 2025]
          na: remove
    tier3:                          # named stages made from this table after its tier 2; a result reads one by its name
      samples_per_country_year:
        description: "One row per country and year: the number of samples, counted after the filter of the years 2023 to 2025 (no sample_id)."
        steps:
          - action: polars_with_columns
            named_exprs:
              year_label: "pl.col('year').cast(pl.Int64).cast(pl.String)"
          - action: polars_group_by
            by: [country, year_label]
            maintain_order: true
            named_aggs:
              n_samples: "pl.col('sample_id').count()"

# ── Defaults read by every plot result (written before the results that use them) ─
plot_defaults:
  theme: theme_minimal

# ── 3. Results (each reads ONE table, or one named tier 3 stage of a table; no data steps here) ─
analysis_groups:
  Results:
    ui_label: "AMR and Virulence"
    description: "Which sequence types, and how many samples per country and year."
    results:
      mlst_bar:
        ui_label: "MLST Bar"
        ui_title: MLST Sequence Type Distribution by Country
        description: "Bar chart showing the frequency of MLST sequence types, filled by the origin country."
        result: plot
        from: MLST_with_metadata    # no stage named: it shows MLST_with_metadata after tier 2
        mapping:
          x: sequence_type
          fill: country
        layers:
          - name: geom_bar
            params: {}
          - name: scale_x_discrete
            params: {}
          - name: labs
            params:
              title: MLST Sequence Type Distribution by Country
      samples_per_country_year_bar:
        ui_label: "Samples per country and year"
        ui_title: "Samples per country and year (2023 to 2025)"
        description: "Number of samples per country and year, after the filter of the years 2023 to 2025."
        result: plot
        from:
          table: MLST_with_metadata
          tier3: samples_per_country_year
        mapping:
          x: country
          y: n_samples
          fill: year_label
        layers:
          - name: geom_col
            params: {}
          - name: labs
            params:
              title: "Samples per country and year (2023 to 2025)"
              x: Country
              y: Samples
      samples_per_country_year:
        ui_label: "Samples per country and year (table)"
        ui_title: "Samples per country and year (2023 to 2025), as a table"
        description: "The same table as the plot beside it: one row per country and year with the number of samples."
        result: table
        from:
          table: MLST_with_metadata
          tier3: samples_per_country_year
```
What each result shows:
- `mlst_bar`: `MLST_with_metadata` after its tier 2: 33 rows.
- the two results of the summary: the named stage `samples_per_country_year` of `MLST_with_metadata`: 6 rows.
- The named stage has ONE list. The per-sample stage that form 3 keeps in the derived table's tier 1 does not exist here (flag 4).

### 2.5 Is there a better form? What I looked at
- **Form 3 with the derived table nested under its source table** (the block `derived` inside `MLST_with_metadata`). It shows what is made from a table where the table is defined, and `from:` is not needed. But a chain of derived tables nests deeper and deeper, and a derived table that results read is then buried inside a join. I judge it weaker for reading (Part 4, option c).
- **One unnamed `tier3` per table** (tier 1, tier 2, tier 3 of each table, nothing named). Result A must then read T2 and result B T3 of the same table. So a result must say which stage it reads. That is a "tier key", which you replaced by "the result is the last stage" (D-0485). It also allows only one such stage per table. I did not retain it.
- I found no form better than form 3 on the merits you named. Form 5 is the closest to your words; Part 7 compares them.

### 2.6 The reads summary, complete, in form 3 (your question)
`FastP_with_metadata` has no tier 2 in the demo, so the derived table reads it after its tier 1 (the fall back T2 = T1). No plot of the demo reads `FastP_with_metadata` today.
```yaml
id: reads_form3
spec_version: 1
data_engine: python-polars
plot_engine: python-plotnine
info:
  label: ST22 reads summary, form 3
  description: "FastP read quality joined with the metadata; a reads summary per country and year, shown as a table."

# ── 1. Source tables ───────────────────────────────────────────────────────────
data_schemas:
  FastP:
    label: "FastP"
    description: "Reads Quality (Quality Control)"
    source:
      type: local_tsv
      path: ./assets/test_data/1_test_data_ST22_dummy/test_data_FastP_20260307_105756.tsv
    null_values: []
    strip: true
    input_fields:
      sample_id:
        original_name: "sample_id"
        type: String
        label: "Sample ID"
        is_entity_key: true
      total_reads:
        original_name: "total_reads"
        type: Float64
        label: "Total Reads"
      q30_rate:
        original_name: "q30_rate"
        type: Float64
        label: "Q30 Rate"
      gc_content:
        original_name: "gc_content"
        type: Float64
        label: "GC Content"
    tier1:
      steps: []

metadata_schema:
  label: "metadata"
  description: "Metadata (Metadata)"
  source:
    type: local_tsv
    path: ./assets/test_data/1_test_data_ST22_dummy/test_metadata_20260307_105756.tsv
  null_values: []
  strip: true
  input_fields:
    sample_id:
      original_name: "sample_id"
      type: String
      null_values: ["", "-"]
      label: "Sample ID"
      is_entity_key: true
    source:
      original_name: "Source"
      type: String
      label: "Biological Source"
    year:
      original_name: "Year"
      type: Float64
      label: "Collection Year"
    country:
      original_name: "Country"
      type: String
      label: "Origin Country"
  tier1:
    steps: []

# ── 2. Joins ───────────────────────────────────────────────────────────────────
joins:
  FastP_with_metadata:
    label: "FastP with metadata"
    description: "One row per sample: the FastP read-quality values with the sample's source, year and country; a left join on the sample id, so every FastP sample stays."
    ingredients:
      - dataset_id: FastP
      - dataset_id: metadata_schema
    tier1:
      steps:
        - action: polars_join
          right_ingredient: metadata_schema
          'on': [sample_id]
          how: left
          maintain_order: left_right
    # no tier2: T2 = T1, so a table made from FastP_with_metadata reads it after tier 1

# ── 3. Derived tables ──────────────────────────────────────────────────────────
derived_tables:
  FastP_reads_summary:
    label: "FastP reads summary"
    description: "One row per country and year: the number of samples and the mean of the total reads and of the Q30 rate. Tier 1 keeps one row per sample; tier 2 is the summary. A sample with no year forms its own group with an empty year."
    from: FastP_with_metadata       # its last stage is its tier 1 here (no tier 2)
    tier1:
      steps:
        - action: polars_with_columns
          named_exprs:
            year_label: "pl.col('year').cast(pl.Int64).cast(pl.String)"
    tier2:
      steps:
        - action: polars_group_by
          by: [country, year_label]
          maintain_order: true
          named_aggs:
            n_samples: "pl.col('sample_id').count()"
            mean_total_reads: "pl.col('total_reads').mean()"
            mean_q30_rate: "pl.col('q30_rate').mean()"

# ── 4. Results ─────────────────────────────────────────────────────────────────
analysis_groups:
  Quality Control:
    ui_label: "Quality Control"
    description: "How many reads, and of which quality, per country and year."
    results:
      reads_summary:
        ui_label: "Reads summary"
        ui_title: "Reads per country and year: number of samples, mean total reads, mean Q30 rate"
        description: "The summary table of FastP per country and year."
        result: table
        from: FastP_reads_summary
```
Run on the demo data by today's route (the same steps as the tier 3 of a plot), equal to plain Polars (Part 6):
```text
[route 1] reads summary as the tier 3 of a plot today: 9 rows
shape: (9, 5)
┌─────────┬────────────┬───────────┬──────────────────┬───────────────┐
│ country ┆ year_label ┆ n_samples ┆ mean_total_reads ┆ mean_q30_rate │
│ ---     ┆ ---        ┆ ---       ┆ ---              ┆ ---           │
│ str     ┆ str        ┆ u32       ┆ f64              ┆ f64           │
╞═════════╪════════════╪═══════════╪══════════════════╪═══════════════╡
│ Norway  ┆ 2024       ┆ 19        ┆ 2.1724e6         ┆ 0.845045      │
│ France  ┆ 2024       ┆ 2         ┆ 2042113.5        ┆ 0.874382      │
│ Norway  ┆ 2022       ┆ 7         ┆ 2.4099e6         ┆ 0.827052      │
│ France  ┆ 2022       ┆ 1         ┆ 2.645976e6       ┆ 0.847456      │
│ Germany ┆ 2022       ┆ 1         ┆ 1.471898e6       ┆ 0.881264      │
│ France  ┆ 2023       ┆ 1         ┆ 2.871943e6       ┆ 0.867652      │
│ Germany ┆ 2023       ┆ 5         ┆ 2380142.4        ┆ 0.795286      │
│ Norway  ┆ 2023       ┆ 2         ┆ 3.103546e6       ┆ 0.747162      │
│ Germany ┆ 2024       ┆ 4         ┆ 2.2090e6         ┆ 0.881426      │
└─────────┴────────────┴───────────┴──────────────────┴───────────────┘
[route 3] plain Polars: 9 rows; equal to route 1: True
```

### 2.7 The same forms split into files with `!include`, as the demo does
Each tier of a table, a join or a derived table goes in its own file under `wrangling/`, included per tier (D-0250): `tier1: !include '1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling_tier1.yaml'`, and for the derived table, for example, `tier1: !include '1_test_data_ST22_dummy/wrangling/MLST_samples_per_country_year_tier1.yaml'` (a name I suggest). The `from:` of a derived table stays in the main file, next to its `label` and `description`: it is the link between two tables, so a reader sees every link in one file. Each result goes in its own file, as the plots do today: `mlst_bar: !include '1_test_data_ST22_dummy/results/mlst_bar.yaml'` (the folder `plots/` renamed `results/`, a suggestion). That file holds the whole entry, `result:` and `from:` included. Under form 4 the result's `tier3` is in that file too. Under form 5 a named stage can be its own file: `samples_per_country_year: !include '.../wrangling/MLST_with_metadata_tier3_samples_per_country_year.yaml'`.

---

## Part 3. Your case, walked through

The file is the one of Part 2 (form 3 in 2.2, form 4 in 2.3). Your names and the names in the file:

| Your name | In the file | Rows (run) |
|---|---|---|
| T1a | `MLST_with_metadata` after its tier 1 (the join) | 42 |
| T2a | `MLST_with_metadata` after its tier 2 (era, years 2023 to 2025) | 33 |
| result A | `mlst_bar` (a plot), `from: MLST_with_metadata` | reads the 33 rows |
| T3a, the table made from T2a | `MLST_samples_per_country_year`: its tier 1 (one row per sample, with `year_label`), then its tier 2 (the count) | 33, then 6 |
| result B | `samples_per_country_year` (a table) and `samples_per_country_year_bar` (its plot), `from: MLST_samples_per_country_year` | read the 6 rows |

**What result A shows:** the bar plot of sequence types, filled by country, from 33 samples. Sequence type 428 has 2 samples.
**What result B shows:** 6 rows: Norway 2024: 19, France 2024: 2, France 2023: 1, Germany 2023: 5, Norway 2023: 2, Germany 2024: 4 (total 33). The plot and the table show the same numbers (form 3: same table, no steps of their own).

### One audit step at three places
The step: "remove sample 97991777" (a Norway sample of 2024, sequence type 428). It is a removal by key, one of the three audit steps allowed (D-0322). I ran it with the real engine at the three places (`try/audit_walk.py`; the step is written as an author step, because the audit recipe is not read from a file yet; the effect on the data is the same).

**What the dialog lists before you confirm.** The step is created while viewing result A. The walk of the lineage (D-0347) finds every table that has the column `sample_id`. Only distinct tables are lines, each with its reach (D-0346); every line is ticked when the dialog opens and you untick (D-0316):

| Line in the dialog | Reach | Note |
|---|---|---|
| `MLST`, tier 1 | 3 results | removes the row before the join |
| `metadata_schema`, as read (no steps) | 3 results | the MLST row stays, with an empty year and country, until tier 2 removes it (empty year, `na: remove`) (reasoned) |
| `MLST_with_metadata`, tier 1 (T1a) | 3 results | |
| `MLST_with_metadata`, tier 2 (T2a) | 3 results | place (ii) |
| `MLST_samples_per_country_year`, tier 1 (T3a) | 2 results: the table B and its plot | place (iii) |
| `MLST_samples_per_country_year`, tier 2 | no line | `sample_id` does not exist there: the table is one row per country and year |
| This result only: `mlst_bar` | 1 result | place (i) |

**(i) "This result only", at result A.**
- Changes: result A only. Run: 32 rows; sequence type 428 now has 1 sample.
- Stays: both results B (Norway 2024 still 19).
- Written in the audit recipe at: `analysis_groups.Results.results.mlst_bar.tier3.audit_steps`.

**(ii) At the shared table, after its tier 2 (T2a).**
- Changes: result A (32 rows, ST 428: 1) AND both results B (Norway 2024: 18; total 32), because B is made from T2a.
- Stays: nothing in this slice.
- Written at: `joins.MLST_with_metadata.tier2.audit_steps`.

**(iii) At the derived table B (T3a), its tier 1.**
- Changes: both results B (Norway 2024: 18; total 32).
- Stays: result A (33 rows, ST 428: 2).
- Written at: `derived_tables.MLST_samples_per_country_year.tier1.audit_steps`.
- It cannot be written at B's tier 2: `sample_id` is gone there.

### Where form 3 and form 4 differ in this case
- The three places, the lines, the reach and the numbers are the same in both forms.
- In form 4 the table result `samples_per_country_year` has a step of its own (the sort). Its tier 3 holds that step, and the audit's "this result only" steps for it come after the sort, in the same tier 3. In form 3 its tier 3 holds audit steps only.
- In form 4 the screen of that table result must say "this result adds 1 step of its own". If that step were a filter, the table and its plot would show different numbers (flag 1).
- Under form 5, place (iii) does not exist: the named stage ends with the count, so the sample can only be removed at T2a (place ii), which also changes result A (flag 4).

---

## Part 4. Where the derived table lives

| | (a) Among the joins (a `joins` entry with `from:` and no ingredients) | (b) A block of its own, `derived_tables` (my choice) | (c) Nested under the table it is made from |
|---|---|---|---|
| What a recipe maker reads | "joins" holds a table that joins nothing: surprising | the name says what it is | sees, under each table, what is made from it |
| Rule of reading | two rules in one block: `ingredients` read at tier 1, `from:` at the last stage | one rule per block | `from:` is implied by the place |
| Order of the file | the derived table may sit before the join it reads | files, joins, derived tables, results: top to bottom | follows its source; a chain nests deeper |
| Finding the readers of a table | search `from:` and `dataset_id:` | search `from:` | look inside the table, then search the results |
| Ids | one id space with tables and joins (today the check X1 already refuses a join id that is also a table id, `recipe_check.py:829-830`) | the same id space must include the derived tables: one id = one table in the whole recipe | the nested ids must still be unique in the whole recipe |
| What a reader finds first | the joins block, mixed | the block `derived_tables`, after the joins | the source table |

Ids must be unique across source tables, joins, derived tables and results, so that `from:` names one thing. Today a result id written in two groups is not refused by a plain rule (flag 6).

---

## Part 5. "Table to view" (Source | T1 | T2 | T3) in HOME

What each choice shows, in Exploration, for the results of the slice. Rows are the numbers run in Part 6. The badge words "Result" and "an earlier stage" are those you accepted (D-0487). "Source" today is a source file as read, with a list "Source table" of the sources that feed the open result (read by a scout, `FACTS_2.md`, `app/handlers/home_theater.py:290-313`).

| Form | Result | Source | T1 | T2 | T3 |
|---|---|---|---|---|---|
| Today | `mlst_bar` | MLST or metadata, as read | join after tier 1: 42 | after tier 2: 33 | "T3 = T2", Result |
| Today | the summary plot | MLST or metadata | 42 | 33 | its own tier 3: 6 rows, Result |
| Today | a table result | does not exist | | | |
| 3 | `mlst_bar` | MLST or metadata | `MLST_with_metadata` T1: 42 | T2: 33 | "T3 = T2", Result |
| 3 | `samples_per_country_year` (table) and its plot | see below | `MLST_samples_per_country_year` T1: 33, one per sample with `year_label` | T2: 6 | "T3 = T2", Result |
| 4 | `mlst_bar` | as form 3 | 42 | 33 | "T3 = T2", Result |
| 4 | `samples_per_country_year` (table, with its sort) | see below | 33 | 6 | 6 rows sorted, Result, "1 step of its own" |
| 5 | `mlst_bar` | MLST or metadata | 42 | 33 | "T3 = T2", Result |
| 5 | the two results of the summary | MLST or metadata | `MLST_with_metadata` T1: 42 | T2: 33 | the named stage: 6, Result |

In Audit mode, T3 adds the audit steps applied with a reason, as today; T1 and T2 show the originals.

**Is "Source" meaningful for a derived table?** It has no file: its source is another table, read at its last stage. Three readings, yours to choose:
- (s1) Source keeps one meaning, "the files as read": for result B the list holds `MLST` and `metadata_schema`. Then T2a (33 rows) is not among the four choices of result B; you see it from result A.
- (s2) For a derived table, Source shows the table it is made from: `MLST_with_metadata` after its tier 2 (33 rows), with the badge "made from MLST_with_metadata (after tier 2)". Source then means two things.
- (s3) The list "Source table" holds both: the files, and the table it is made from, each named. My suggestion: one meaning, "what this table is made from, as read", and nothing hidden.
Under form 5 this question does not arise: the four choices are exactly the chain of one table (files, T1a, T2a, T3a). That is a real merit of form 5 in HOME.

---

## Part 6. Tried against the recipe check, honestly

Scripts and outputs: `tmpAI/panel/tables_as_results/refined/try/` (`build_today.py`, `audit_walk.py`, `check_new_forms.py`, `check_second_pass.py`, `check_duplicate_ids.py`; outputs in `try/out/`). All run from the repository root with `PYTHONPATH=. ./.venv/bin/python`.

**(a) Today's file passes and builds (run).**
```text
[check] validate_data_analysis_recipe(slice_today.yaml): 0 problem(s)
[check] validate_data_analysis_recipe_data(slice_today.yaml): 0 problem(s)
```
The join and the summary, first rows:
```text
[build] MLST_with_metadata T1: 42 rows, columns ['sample_id', 'scheme', 'sequence_type', 'source', 'year', 'country']
[build] MLST_with_metadata T2 (after era and the filter 2023-2025): 33 rows, columns ['sample_id', 'scheme', 'sequence_type', 'source', 'year', 'country', 'era']
shape: (5, 7)
┌───────────┬─────────────────┬───────────────┬─────────┬────────┬─────────┬────────┐
│ sample_id ┆ scheme          ┆ sequence_type ┆ source  ┆ year   ┆ country ┆ era    │
│ ---       ┆ ---             ┆ ---           ┆ ---     ┆ ---    ┆ ---     ┆ ---    │
│ str       ┆ str             ┆ str           ┆ str     ┆ f64    ┆ str     ┆ str    │
╞═══════════╪═════════════════╪═══════════════╪═════════╪════════╪═════════╪════════╡
│ 32557144  ┆ ecoli_achtman_4 ┆ 57            ┆ Broiler ┆ 2024.0 ┆ Norway  ┆ Recent │
│ 97991777  ┆ ecoli_achtman_4 ┆ 428           ┆ Parent  ┆ 2024.0 ┆ Norway  ┆ Recent │
│ 80700308  ┆ ecoli_achtman_4 ┆ 371           ┆ Layer   ┆ 2024.0 ┆ Norway  ┆ Recent │
│ 51573804  ┆ ecoli_achtman_4 ┆ 154           ┆ Parent  ┆ 2024.0 ┆ Norway  ┆ Recent │
│ 35115511  ┆ ecoli_achtman_4 ┆ 429           ┆ Layer   ┆ 2024.0 ┆ Norway  ┆ Recent │
└───────────┴─────────────────┴───────────────┴─────────┴────────┴─────────┴────────┘

[route 1] T3 of the plot samples_per_country_year_bar (tier 3 = year_label, group_by): 6 rows
shape: (6, 3)
┌─────────┬────────────┬───────────┐
│ country ┆ year_label ┆ n_samples │
│ ---     ┆ ---        ┆ ---       │
│ str     ┆ str        ┆ u32       │
╞═════════╪════════════╪═══════════╡
│ Norway  ┆ 2024       ┆ 19        │
│ France  ┆ 2024       ┆ 2         │
│ France  ┆ 2023       ┆ 1         │
│ Germany ┆ 2023       ┆ 5         │
│ Norway  ┆ 2023       ┆ 2         │
│ Germany ┆ 2024       ┆ 4         │
└─────────┴────────────┴───────────┘
```
Both plots of the file were drawn (`mlst_bar` from 33 rows, the summary plot from 6 rows).

**(b) The data of forms 3, 4 and 5, proved by today's format (run).** The new forms do not exist, so they cannot be built. Their data can: the derived table B is "the steps year label and count, on `MLST_with_metadata` after its tier 2". Today a recipe can write it in only two ways (routes 1 and 2); route 3 uses no recipe:
- route 1: as the tier 3 of a plot that reads `MLST_with_metadata` (the file of 2.1);
- route 2: as a second join that repeats the join AND the tier 2 steps of `MLST_with_metadata`, because a join reads the tier 1 of its ingredients and an ingredient must be a source table (read, `recipe_check.py:867`, code J04). This is exactly what today's format cannot express without copying: a table made from the stage after another table's tier 2.
- route 3: plain Polars on the two files, no recipe.
```text
[route 1] T3 of the plot samples_per_country_year_bar (tier 3 = year_label, group_by): 6 rows
[route 2] T2 of the join MLST_samples_repeated (steps repeated): 6 rows
[route 3] plain Polars: 6 rows
[compare] route 1 equals route 2: True
[compare] route 1 equals route 3: True
[sum] samples counted in the summary: 33 (T2 rows: 33)
```
The reads summary of 2.6: by today's route (the tier 3 of a plot) and by plain Polars: equal, 9 rows (`try/out/check_new_forms.out`).

**(c) The check run on the files of the new forms: what does not exist yet (run).**
First pass, the files as written:
```text
== form3/slice_form3.yaml: 5 error(s)
   slice_form3.yaml : derived_tables : [T03] derived_tables is not a key of this element. Fix: remove it, or write one of additional_datasets_schemas, analysis_groups, data_engine, data_schemas, entity, id, info, joins, metadata_schema, plot_defaults, plot_engine, spec_version
   slice_form3.yaml : joins.MLST_with_metadata.tier2 : [J14] tier2 of a join applies only when a plot reads the join: no plot reads this join, so these steps would run nowhere. Fix: plot this join, or remove the steps
   slice_form3.yaml : analysis_groups.Results.results : [G01] results is not a key of this element. Fix: remove it, or write one of comment, description, plots, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots : [G01] plots is a mapping of id to plot. Fix: write plot id: {ui_label, target_dataset, mapping, layers}
   slice_form3.yaml : analysis_groups : [T09] profile run needs at least one group with one plot. Fix: add a group with a plot

== form5/slice_form5.yaml, the one line that differs from form 3 (it has no derived_tables, so no T03):
   slice_form5.yaml : joins.MLST_with_metadata.tier3 : [J01] tier3 is not a key of this element. Fix: write tier2
```
The checker stops at the group when it meets `results`. Second pass, with only the word `results` renamed `plots` in a scratch copy, to see what it says about the entries (form 3; form 4 gives the same list; form 5 the same, with J01, a `tier3` in a join, in place of T03):
```text
== form3/slice_form3.yaml with `results` renamed `plots`: 12 error(s)
   slice_form3.yaml : derived_tables : [T03] derived_tables is not a key of this element. Fix: remove it, or write one of additional_datasets_schemas, analysis_groups, data_engine, data_schemas, entity, id, info, joins, metadata_schema, plot_defaults, plot_engine, spec_version
   slice_form3.yaml : joins.MLST_with_metadata.tier2 : [J14] tier2 of a join applies only when a plot reads the join: no plot reads this join, so these steps would run nowhere. Fix: plot this join, or remove the steps
   slice_form3.yaml : analysis_groups.Results.plots.mlst_bar.result : [P01] result is not a key of this element. Fix: remove it, or write one of comment, description, facet_by, filters, guides, labels, layers, mapping, palette, plot_engine, target_dataset, taxonomy, theme, tier3, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots.mlst_bar.from : [P01] from is not a key of this element. Fix: remove it, or write one of comment, description, facet_by, filters, guides, labels, layers, mapping, palette, plot_engine, target_dataset, taxonomy, theme, tier3, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots.mlst_bar.target_dataset : [PS02] target_dataset None is not a schema or a join of this recipe. Fix: name one
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year_bar.result : [P01] result is not a key of this element. Fix: remove it, or write one of comment, description, facet_by, filters, guides, labels, layers, mapping, palette, plot_engine, target_dataset, taxonomy, theme, tier3, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year_bar.from : [P01] from is not a key of this element. Fix: remove it, or write one of comment, description, facet_by, filters, guides, labels, layers, mapping, palette, plot_engine, target_dataset, taxonomy, theme, tier3, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year_bar.target_dataset : [PS02] target_dataset None is not a schema or a join of this recipe. Fix: name one
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year.result : [P01] result is not a key of this element. Fix: remove it, or write one of comment, description, facet_by, filters, guides, labels, layers, mapping, palette, plot_engine, target_dataset, taxonomy, theme, tier3, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year.from : [P01] from is not a key of this element. Fix: remove it, or write one of comment, description, facet_by, filters, guides, labels, layers, mapping, palette, plot_engine, target_dataset, taxonomy, theme, tier3, ui_label, ui_title
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year.target_dataset : [PS02] target_dataset None is not a schema or a join of this recipe. Fix: name one
   slice_form3.yaml : analysis_groups.Results.plots.samples_per_country_year : [PS03] mapping and layers are required. Fix: add mapping and layers
```
What does not exist yet, in plain words:
1. The block `derived_tables` (T03). Its steps are not checked at all today; they are proved only by the routes of (b).
2. The list `results` in a group (G01); the keys `result` and `from` in an entry (P01); an entry without `target_dataset` (PS02; the message even says "target_dataset None").
3. A table result: the check asks for `mapping` and `layers` (PS03).
4. A derived table as a reader: the tier 2 of `MLST_with_metadata` is refused because "no plot reads this join" (J14).
5. Form 5: a `tier3` in a join (J01).
6. The private `tier3` of form 4 raised no error: the key exists today on a plot entry.

---

## Part 7. The forms compared

| | Today | Form 3: derived tables, no steps in a result | Form 4: derived tables, a result may add steps | Form 5: named tier 3 stages inside a table |
|---|---|---|---|---|
| What is a result, what is a stage | a plot only; its tier 3 holds data steps | a result shows one table; every stage is a tier of a table | as form 3, plus a result's own last steps | a result shows a table or one named stage of a table |
| Same numbers for a plot and its table | no table result; a second result copies the steps | yes, by construction | yes, unless a result adds a filter of its own (flag 1) | yes, both read the same stage |
| Audit: "this result only" | yes (the plot's tier 3) | yes: the result's tier 3, written by the audit only (D-0346) | yes: after the result's own steps | yes, but after the stage's last step; a sample cannot be removed after a count (flag 4) |
| Audit: "all results that read this" | at a tier of the target | at any tier of any table; reach followed through `from:` | as form 3 | at tier 1 or 2 of the table, or at a named stage (then all readers of that stage) |
| One definition of "the table a result shows" | target's tier 2 plus the plot's tier 3 | the table named in `from:`, at its last stage | that, plus the result's own steps | the table, or the named stage, in `from:` |
| A definition comes before its use | no: the summary is inside the result | yes, everywhere | yes, except a result's own steps | yes, everywhere |
| Described like tier 1 and tier 2 | no | yes: a derived table has a tier 1 and a tier 2 | yes for tables; a result's `tier3` has the same shape | in place yes (beside tier 1 and 2), in shape no: `tier3` holds NAMED lists |
| "Which data does this result show, after which steps?" (result `samples_per_country_year`) | no table result; the plot: 4 places (plot entry, join, MLST, metadata) | 5 places: result, derived table, join, MLST, metadata | 5 places, plus the result's own steps | 4 places: result, join with its stage, MLST, metadata |
| "If I change this step, which results change?" (the year label step) | the plot holding it; any copy elsewhere is not found | search `from: MLST_samples_per_country_year`: 2 results | same: 2 results | search `tier3: samples_per_country_year`: 2 results |
| Same question, for the tier 2 of the join (the years 2023 to 2025) | search `target_dataset`: 2 plots | 2 searches: 1 result and 1 derived table, then its 2 readers: 3 results | as form 3 | 1 search: 3 results |
| The words "tier 3" and "T3" | the plot's own steps | not written by the author; on screen "T3 = T2", or T3 with audit steps | the result's own steps; "T3 = T2" when none | a named stage of a table |
| "Table to view" for a result made from another table | not applicable | the chain is longer than four choices (Part 5) | as form 3 | the four choices are the chain |
| A third kind of result later | not applicable | one more value of `result:` | the same | the same |
| Strongest argument against | no table result; steps copied | a result that needs a filter or sort for itself needs a named table | two places for last steps; a summary can again be hidden in a result | one list per stage; no chain; no per-sample stage before a count; a different shape of tier |
| Reopens (information only) | | D-0063 and D-0306 (the author writes a plot's tier 3); D-0024 and D-0237 point 3 (the tier 3 container stays, for the audit only) | none of these; adds the derived tables | D-0250 (a tier is one list), D-0237 point 3, D-0063, D-0306; a result reads a chosen stage, close to your first idea in D-0485 |
| Cost (information only) | | a new block and node kind (the T1 and T2 of a derived table, read from the T2 of its source), its keys, the check codes, J14 and S07 counting derived tables, the Source list of HOME | as form 3, plus the line "N steps of its own" and an advice in the check | a named stage node kind, `from:` with two parts, keys, lineage levels, audit places |

All three new forms also need the names of the result system (`results`, `result:`, `from:`), which are open (D-0485, D-0487).

---

## Part 8. My recommendation, and what stays yours

### Recommendation: form 3
- It meets both of your wishes fully: every stage is defined like tier 1 and tier 2 (a derived table has both), and every definition comes before its use.
- It is good data science: one table, one definition; a plot and its table that read it show the same numbers; to know which results a step changes, you search one name.
- The main argument for form 4 was the audit ("this result only"). That is already decided: the audit gives a result its own audit steps even when the recipe has none for it (D-0346). The panel of round 5 wrote that under form 3 "this result only" exists only when a table has one reader; that does not follow D-0346.
- Form 5 is the closest to your words "T3a", and it is the best in "Table to view". But its stage has one list: no per-sample stage before a count, so a sample cannot be removed from B alone (run in Part 3), and no table can be made from a stage.
- What form 3 costs a recipe maker: a figure-only filter or sort becomes a named table. I judge that a gain: it is visible, reusable and audited like any table.

### Yours to decide (nothing chosen)
1. **The form:** 3, 4 or 5.
2. **The list of results:** `results` (suggestion, K1 of the earlier proposal).
3. **The key that says what a result is:** `result: plot | table`, required in every entry (suggestion).
4. **The key that names the table a result shows:** `from:` (suggestion; the same word as in a derived table). Alternatives: `table:` (reads oddly next to `result: table`), `reads:`, or keep `target_dataset`.
5. **The block of derived tables:** `derived_tables` (suggestion), as a block of its own (Part 4, option b).
6. **What `from:` reads:** the last stage of its table (suggestion: the same rule as a result). Alternative: name the stage, for example `from: {table: MLST_with_metadata, tier: tier2}`.
7. **Form 4 only:** the name of a result's own steps: keep `tier3`, or another word.
8. **Form 3 only:** confirm that the author may never write steps in a result's `tier3`, and that the audit still writes there ("this result only").
9. **Joins:** keep "a join reads the tier 1 of its ingredients" (today), or read their last stage like `from:`. The second changes results silently in the demo (flag 3).
10. **May a join take a derived table as an ingredient?** Today an ingredient must be a source table (J04). Not needed for your case; needed to join a summary with a reference table.
11. **"Source" for a derived table** in "Table to view": s1, s2 or s3 (Part 5).

### What I found that the panel missed
- D-0346 already gives "this result only" without author steps in a result (above).
- The check refuses the tier 2 of a table read only by a derived table (J14; flag 5). The same holds for a source table (S07).
- A result id repeated in two groups is not refused by a plain rule (flag 6).
- `plot_defaults` is written after the results in the demo; under your rule it belongs before them.
- Today's format cannot write a table made from the stage after another table's tier 2 without copying the steps (Part 6, route 2).

### Not verified
- No new form was built: the format, the check and the engine do not know them. Their data was proved by today's routes only.
- The dialog lines of Part 3 are reasoned from D-0346 and D-0347 and from the columns of each table; the dialog was not run.
- "Table to view" for the new forms is reasoned, not tried on a screen.
