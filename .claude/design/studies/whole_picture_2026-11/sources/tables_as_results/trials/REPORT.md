# How does a table result show that the audit worked and what it affected? (trials, 2026-11-22)

Labels: RAN = executed here; READ = read at file:line; REASONED = from the outputs. Nothing in the repository was edited; everything is under `tmpAI/panel/tables_as_results/trials/`.

## For the owner

### The baseline (Part A)
- The original result of an entry (its last stage, with the recipe's own tier 3 steps, no audit step) can be read today: `DataOrchestrator.materialize_tier3(recipe, entry, anchors_dir)` (READ `app/modules/orchestrator.py:690-750`). It is the stored tier 2 table (or tier 1 when there are no tier 2 steps) plus the entry's own tier 3 steps. It is stored on disk when the entry has its own tier 3 steps (`QA_population_zscore__T3_qa_population_zscore.parquet` in the run), otherwise it is the stored tier 2/tier 1 table read lazily. HOME's "Original" pane of Compare draws from exactly this table, with no audit node (READ `home_theater.py:755-799`, `tier="T3"`).
- The audited result is NOT stored today. In HOME it is the original result plus `audited_frame(lf, nodes)` computed in memory (READ `app/modules/t3_audit_engine.py:771`, used `home_theater.py:1299`, `export_handlers.py:1463`); that mechanism only knows filter and column-drop steps at the entry's own table. The other mechanism, the audit copy (`utils/audit_copy.py` + `app/modules/audit_run.py`), is built and tested, and is the one that can place a step upstream; its audited entry table is computed on demand and stored nowhere (READ `orchestrator.py:731-736`, "PROVISIONAL ... stored nowhere"). `audit_run` builds `table_original` and `table_audit` and compares them only with `.equals` to set `PlotRun.affected` (READ `audit_run.py:266-271`); the two tables are not returned and no difference is computed. Nothing on the screen calls `audit_run` yet (READ its docstring: "Nothing a user sees is wired to it yet"; grep: only `app/tests/test_audit_run.py` consumes it).
- Is it true that an audit recipe "has its own recipe and its own data hashes"? RAN, partly. The recipe hash of the audit copy differs from the original (`a6e4b01f38f8` against `919ff8cdd063`) and every table key that a step touches differs. The DATA hash is the SAME (`a1ae45bde9f0` both): a removal is a step, the data files are the same bytes. And no audit record or file is written: the record with the hash is DECIDED (D-0324, D-0333), not built (READ `audit_copy.py` module text: "the audit record's job (D-0333; not built here)"; the copy lives in an object in memory).
- Is "original result against audited result, both at the LAST stage" the right pair, not "T2 against T3"? Yes, by the run. Example (RAN, scratch copy of the demo where the plot `qa_population_zscore` has its own tier 3 step "remove Germany"; the audit removes sample 32557144 upstream):
  - original T3 against audited T3 (right pair): 1 row removed (sample 32557144), 31 z-scores changed.
  - original T2 against audited T3 (wrong pair): 11 rows "removed" (10 Germany rows that the audit did NOT remove, plus the sample), 31 changed.
  - original T2 against audited T2: 1 row removed, 41 changed; true, but it says nothing about what the entry shows.

### The solutions, each with one real output (Part B)
All outputs below: RAN on the demo recipe (42 samples), tables built through `run_audit` (the real engine). Case C1 = the sample 32557144 removed from all tables with `remove_from_all` (an audit step upstream, at tier 1 of every table that has the key).

**S1, your idea: whole-row diff, no key.** Rows only in the original, rows only in the audited table (duplicates counted).
- `QA_aggregated_no_key` after the removal: only in original `Norway | 2024 | 19`; only in audited `Norway | 2024 | 18`. A mean or a count that moved is two lines one under the other: recognisable by eye.
- `QA_population_zscore` after the same removal: 42 rows only in the original, 41 only in the audited (every row, because every z-score moved); the removed sample is one of 42 lines. Unreadable as a list.
- It never needs a key and it never refuses. It hides WHICH column moved and, when a column was dropped, the rows look equal (see below).

**S2, paired by a key.** Full outer join on the key: removed, added, changed cells with old and new.
- `QA_population_zscore`, key `sample_id`: `paired 41, removed 1 (32557144 | Norway | 366418 | 0.4976), added 0, changed cells 41`; first changes `97991777 n50_zscore 0.207335 -> 0.217453`.
- `QA_aggregated_no_key`, key `country, year_label`: `Norway | 2024 | n_samples 19 -> 18`, nothing else.
- `Quast_with_metadata` (one row per sample and metric): refused, "no key can be read from the recipe" (it has an unpivot the lineage walk does not read).
- Where does the key come from? The recipe knows two things (RAN with `utils.step_effects.effect_of` and `recipe_graph.declared_entity_keys`): the entity key declared on the source tables (`is_entity_key`: `sample_id`) and the `by` columns of a `polars_group_by` (READ `step_effects.py:152-156`, names only). In the 4 tables this gave `sample_id` (z-score), `country, year_label` (aggregate), `sample_id, country` (AMR). In every case the key was then CHECKED on the data: unique and without missing values in both tables, otherwise refuse. Where the lineage has a step the walk does not read (unpivot), no key. Cases where the entity key is not unique: `ResFinder_with_metadata` (50 rows share a sample id): the check refused. So the app can find a candidate safely only if the key is verified on both tables; it cannot know every key (long tables).

**S3, the counts line.** `QA_population_zscore` after C1: rows 42 -> 41, columns 4 -> 4, rows not in both 42/41; `n50` mean 308497 -> 307085; `n50_zscore` min -1.52 -> -1.49. Cheap (0.3-0.6 ms). Never wrong, but "rows 42 -> 41" does not say which row, and a mean that moved says nothing about why.

**S4, per-column summary.** Needs the pairing (S2). `n50_zscore: changed 41 of 41 paired, delta from -0.004 to +0.026`; `n50: changed 0`; `country: values gone [], new []`. For the aggregate: `n_samples: changed 1 of 9, delta -1`.

**S5, S1 made readable (pair rows where exactly ONE column differs).** `QA_population_zscore`: 41 pairs, each `(97991777, Norway, 332629, 0.2073) -> (... 0.2175) column n50_zscore`, 1 original row unpaired (the removed sample). `QA_aggregated_no_key`: the `19 -> 18` pair, column `n_samples`. In the 16 real runs (4 tables x 4 cases) no row had two candidates (ambiguous 0). It does pair wrongly on constructed data: orig `France | 2022 | 7` (group removed) and aud `France | 2023 | 7` (new group) are paired as "year changed" (RAN, synthetic). The risk is real, rare, and it is a guess.

**S6, another honest solution: per audit decision, the result rows that changed when that decision alone is applied.** On the z-score result (42 rows), RAN with `run_audit` once per decision:

| Decision alone | rows | removed | cells changed | whole rows differing (S1) | run_audit time |
|---|---|---|---|---|---|
| D1 remove sample 32557144 from all tables | 42 -> 41 | 1 | 41 | 42 / 41 | 2.3 s |
| D2 drop Germany rows at the result | 42 -> 32 | 10 | 0 | 10 / 0 | 0.4 s |
| D3 drop column n50 at the result | 42 -> 42 | 0 | 0 | 0 / 0 (column n50 gone) | 0.5 s |
| all three | 42 -> 31 | 11 | 31 | 42 / 31 | 2.3 s |

This says which decision did what (D1 moved all the z-scores, D2 removed ten rows). Cost: one extra run per decision.

### Part C: which solution answers which question (case C1, one sample removed upstream; and the others where it differs)
Cells: answers / partly / no / misleads. Q1 = "did my step do what I meant?" (the sample is gone). Q2 = "what else moved?".

| Solution | z-score table | aggregate (no sample id) | AMR per sample | long table, no key (Quast) |
|---|---|---|---|---|
| S1 Q1 | partly (the sample is one of 42 listed rows) | partly (a count fell 19 -> 18; the sample is not a row) | answers (1 row only in original, with its id) | answers (3 rows, with the id) |
| S1 Q2 | misleads (42/41 rows look "all replaced"; no word on what moved) | answers (the changed row, old and new) | answers (nothing else: 0 rows only in audited) | answers (nothing else) |
| S2 Q1 | answers (removed 1, with its values) | partly (same as above) | answers | no (refused, no key) |
| S2 Q2 | answers (41 cells, column `n50_zscore`, old and new) | answers (`n_samples 19 -> 18`) | answers (0 cells) | no (refused) |
| S3 Q1 | partly (42 -> 41, which row not said) | partly (9 -> 9, the sum of counts moved) | partly (42 -> 41) | partly (126 -> 123) |
| S3 Q2 | partly (the mean and min/max of z moved) | partly (max 19 -> 18, mean changed) | partly | partly |
| S4 Q1 | no | no | no | no (needs a key) |
| S4 Q2 | answers (`n50_zscore` 41 of 41, delta range) | answers | answers | no (refused) |
| S5 Q1 | answers (1 unpaired original row) | partly | answers | answers (3 unpaired) |
| S5 Q2 | answers (41 pairs, column named) | answers (1 pair) | answers | answers (nothing paired) |
| S6 (per decision) | answers per decision | answers per decision | answers per decision | answers per decision (counts only) |

Column drop (case C4), where S1 misleads: `QA_AMR_per_sample` after dropping `country`: S1 on the common columns says "0 rows differ" (RAN: only in original 0, only in audited 0). It is only right if the dropped column is shown on its own line (the script prints `columns dropped ['country']`). S2 refused when the dropped column was part of the key (3 of 4 tables). S3 shows `cols (3, 2)`.

### What can mislead (from the outputs)
- A table where one value feeds all the others (z-score): S1 lists every row as changed; the user cannot see the one removed sample. S2/S4/S5 are readable.
- An aggregate that moved because a group lost a sample (`19 -> 18`): every solution shows the number that moved; NONE says why (the group lost a sample). The removed sample is not a row of that table. A group that lost all its samples (case C2, France): the 3 France groups appear as "removed" rows, with no word on the cause.
- A column dropped by the audit: S1 on common columns shows no difference unless the column list is shown too.
- Compare against the wrong stage (T2 against T3): 10 rows look removed by the audit that the audit did not remove (Part A).
- Exact float comparison: one unit in the last place on every z-score made all 42 rows differ (S1) and 42 cells (S2) (RAN). Noise itself was NOT found: the same table built twice, built with one thread, round-tripped through parquet and through a tab-separated file gave 0 differing rows on all 4 tables (RAN). A tolerance would be a choice; none is made here.
- Duplicates: an anti-join on all columns misses a duplicated row removed once (original has `(a,1)` twice, audited once: naive anti-join sees 0 rows, the counted multiset diff sees the row; RAN). The counted way is needed.
- Missing values: two rows with a null (or NaN) in the same place are matched as equal by the join with `nulls_equal=True` (RAN). Columns of type list and struct: the multiset diff and S2 work in polars 1.40 (RAN); they were not tried inside the app.

### Size, time, memory
- Output lines (one removed sample, S1 only-orig + only-aud): demo tables 1 to 8 lines. Synthetic 1000 rows x 30 columns, one removal and one column that changes for every row (the z-score case): S1 gives 1000 + 999 lines; S2 gives 1 removed + 999 changed cells (S2 also has a line per cell: 999). So S1, S2 and S5 are unreadable on this case without a cap or a summary; S3, S4 stay 30 lines.
- Time on the demo: S1 3-30 ms, S2 1-8 ms, S3 under 1 ms, S5 under 2 ms per table. Synthetic: 1000 rows 22 ms (S1) / 71 ms (S2); 10 000 rows 85 / 88 ms; 100 000 rows 793 / 306 ms.
- Memory: both tables are collected; 0.2 MB (1000 x 30), 2.4 MB (10 000 x 30), 24 MB (100 000 x 30) per table (polars `estimated_size`), the diff adds a similar amount. `run_audit` itself (building the audited tables): 0.4 to 2.3 s on the demo.
- Can refuse instead of guessing: S2 (no key, key not unique, key missing in a table: all refuse with a reason, RAN); S4 (needs S2); S1, S3 never refuse; S5 never refuses but guesses.

### Also verified: the total number of rows in HOME's data preview
You remember right about "All rows", and the count is not the table's. READ `home_theater.py:1692-1702`: with "All rows" off the grid receives `lf.head(100)`, and `render.DataGrid(df, filters=False, height="300px")` does not switch the grid's own summary off (default `summary=True`). RAN in a scratch Shiny app with the same call (1000-row table): All rows off: `Viewing rows 1 through 9 of 100`; All rows on: `Viewing rows 1 through 9 of 1000`. So the grid says 100, not the real total, when capped. I did not run HOME itself in a browser. By grep, no other place in `home_theater.py` shows a row total (the title only says "max. first 100 rows").

### What I could not try
- A real result table: none exists in the app (the demo tables here are those a plot reads).
- The audit steps written at the entry's own tier 3 (a `tier3: audit_steps` form is not merged, `ui_implementation_contract.md` 12a); only the audit copy's tier 1 and tier 2 steps and the T3 node form of HOME (`audited_frame`; not run here: the row filters at the result were done as audit-copy steps at tier 2/tier 1 of the table).
- Browser view of any solution; the app's own handling of 1000+ rows in the grid.
- A tolerance for floats, a key for long tables (needs the recipe author to declare it), the "why" of an aggregate change.
- Case D (source-level removal with a scratch copy of the data): replaced by `remove_from_all`, which writes the step at tier 1 of every table that holds the key (the truthful audit way, RAN); the removal is applied by the engine before every later step, so the z-score and the counts are recomputed as the app will.

## Details
Scripts: `trials/scripts/` (`common.py`, `build_pairs.py`, `solutions.py`, `keyfind.py`, `run_all.py`, `exp_noise.py`, `exp_a2.py`, `exp_size_steps.py`, `build_orig.py`). Outputs: `trials/out/<case>__<table>.txt` (all S1-S5 prints for 4 cases x 4 tables), `trials/out/summary.json`, `trials/data/pairs/*/*.parquet` (original and audited result tables), `trials/build_pairs.out`, `trials/dgcheck/` (the DataGrid probe).
Cases: C1 one sample from all tables; C2 the 4 France samples from all tables; C3 a row filter at the result table (sample id; country France for the aggregate); C4 a column drop at the result (`n50`, `year_label`, `country`, `source`).
Tables: `QA_population_zscore` (T2), `QA_aggregated_no_key` (T2), `QA_AMR_per_sample` (T2), `Quast_with_metadata` (no tier 2: T1). Plots affected by C1: 17 of 17 (a removal at tier 1 of all tables reaches everything); by C3/C4: 5.
Key from the recipe per table: z-score `sample_id`; aggregate `country, year_label`; AMR `sample_id, country`; Quast none (unpivot not read). S2 checked uniqueness on both tables for each.
No pytest suite was run; one script at a time; the load average was about 11-12 throughout.
