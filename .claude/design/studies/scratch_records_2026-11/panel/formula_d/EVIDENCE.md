# Formula option D: study with a prototype on a copy

Date: 2026-11-18. Polars 1.40.1, Python 3.14. Trial branch `trial/formula-d` (from `dev` at 6ee76184), worktree `.claude/worktrees/formula-d`. Nothing is merged. The formula code of the app is unchanged. Nothing imports the prototype. I decide nothing and recommend nothing (D-0267, D-0268, D-0274).

Labels: RAN = I ran it here (script and output file named, in `tmpAI/panel/formula_d/`). READ = I read it at file:line. REASONED = argued from the code, not run.

## The five lines for a scientist

1. The 16 formulas of the demo recipe are accepted by today's check and run without error on the real data. The tables built from them are the same as the stored golden baseline (RAN, section A2).
2. Today's check refuses 54 of the 60 hostile lines. The 6 it accepts do not run code or read a file: one needs a binary column, one is only a text, one is allowed on purpose, three are only large sizes that I never built (RAN, section A3).
3. Option D builds the same results without evaluating text. On the real data 113 of 113 formula evaluations give the same plan and the same column, and all 102 tables are identical to today's. 305 distinct formula texts from recipes and tests: 169 built identically, 136 refused with the same message. 1597 existing tests pass with D in place (RAN, section B2).
4. What stays unsafe or unproven with either way: a wrong entry in the allowed list (D calls the same members), members that are dangerous by what they do, Polars panics (one left: `pl.Array` in `str.json_decode`), memory and time (three accepted size lines; constant powers), and `hash()` results that change between Polars versions (sections A4, B4, C).
5. For a recipe author nothing changes in how a formula is written. D refuses a few odd things that today's way lets through (a Python method on a number or text, a function name left uncalled in a list) with a plain message (section B3, B5).

## Counts

- Formula lines in YAML files: 57 (shipped pipelines 22, shipped template 1, equality recipes 12, library test data 22, gallery bundles 0). Demo recipe: 16 lines in 13 files.
- Demo and other recipes run: 11 recipes, 102 table records, 113 formula evaluations of 17 distinct texts, 0 errors.
- Hostile lines: 60 read from the earlier file, plus 20 new ones. Today's check: 54 refused, 6 accepted.
- Corpus for the equality study: 305 distinct formula texts (436 places: recipes, test sources, test data). Plus 75 hand-made construct cases. Plus 1597 existing tests run with D in place.
- Trial commits: `fb0a59e7` (prototype and tests) and `bd1697cb` (54 hostile lines in the test, recursion guard).

## What was run (one process at a time; load 4.4 to 7.5 before each run, below the limit of 10)

| Script (in `tmpAI/panel/formula_d/`) | What | Output |
|---|---|---|
| `a1_list_formulas.py` | every formula text in every YAML file | `a1_formulas.jsonl`, `a1_output.txt` |
| `a2_run_real.py` | all recipes through the engine, today's evaluation and D in place of it, formula by formula and table by table | `a2_formula_records.json`, `a2_tables_today.json`, `a2_tables_d.json`, `a2_summary.json`, `a2_output.txt` |
| `a2b_order_probe.py` | the one column that differed between two collects (section A2) | `a2b_plan.txt`, `a2b_plan_optimized.txt` |
| `a3_b3_hostile.py` | 60 hostile lines + 20 new, today / D / walk alone; weakened-check probes | `a3_b3_table.json`, `a3_b3_output.txt`, `a3_accepted_run.txt` |
| `b_corpus.py` | 305 formula texts, built both ways | `b2_corpus.json`, `b2_output.txt` |
| `b2_constructs.py` | 75 constructs of the grammar | `b2_constructs.json`, `b2_constructs_output.txt` |
| `b2_tests_with_d.py` | 15 existing test files, as they are and with D in place | `b2_tests_today.txt`, `b2_tests_d.txt` |
| `a4_mutations.py` | break today's check once per rule and see which tests fail | `a4_mutations_output.txt` |
| `b6_cost.py` | build time | `b6_output.txt` |
| `c_json_decode_panics.py` | which dtype makes `str.json_decode` panic | `c_json_decode_results.json` |
| `make_tables.py` | the tables below | `tables.md`, `hostile_table.md`, `extra_table.md`, `weak_table.md` |

Libraries were imported from the worktree (printed at the start of `a2_output.txt`: `.../.claude/worktrees/formula-d/libs/utils/src/utils/formula_check.py`).

---

# PART A. Today's check on the real formulas

## A1. Every formula text (RAN: `a1_list_formulas.py`)

Method: every YAML file of the worktree (outside `.git`, `.claude`, `tmpAI`, `.venv`) was parsed; a text that parses as one Python expression and uses the name `pl` counts. The step is the nearest `action:` above it. `!include` was followed from the demo recipe: it reads 54 files, 13 of them hold formulas.

- The review session counted "16 lines in 14 files". The demo recipe has 16 lines in 13 files. The 14th file in the folder, `ResFinder_Abromics_wrangling.yaml` (3 lines), is not included by any recipe (grep of `config/data_analysis_recipes/pipelines`: no include). Its 3 formulas are checked but no recipe runs them.
- The earlier count "19 shipped formulas" does not match: I count 23 lines in shipped pipelines and templates (22 + 1), 21 distinct texts. Gallery bundles (`assets/gallery_data`) hold no formula.
- Not scanned as YAML: formulas in `.md`/`.qmd` documents and in Python test sources. The Python test sources are in the corpus of section B2.

Caveat for the column "result": a formula of `polars_group_by` is evaluated here as `with_columns` on the whole input table (a scalar spread over the rows). Its real context is covered by the table records (A2), not by this column.

### Demo recipe `1_test_data_ST22_dummy` (16 lines, 13 files)

| file:line | step | column | formula | today's check | D | D = today (plan, column) | result of the column in its recipe (today) | runs |
|---|---|---|---|---|---|---|---|---|
| 1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:14 | polars_with_columns | resistance_points | `pl.when(pl.col('value') == 'Susceptible').then(pl.lit(0)).when(pl.col('valu...` | accepted | built | yes | 123 rows, Int32, 41 missing, #86d6e3c9 | 1 |
| 1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:21 | polars_group_by | phenotype_count | `pl.col('resistance_points').sum()` | accepted | built | yes | 123 rows, Int32, 0 missing, #ba87dc31 | 1 |
| 1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml:19 | polars_with_columns | length_ratio | `pl.col('hsp_len').cast(pl.Float64) / pl.col('total_len').cast(pl.Float64)` | accepted | built | yes | 280 rows, Float64, 0 missing, #8d08eac5 | 17 |
| 1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling.yaml:12 | polars_with_columns | era | `pl.when(pl.col('year') < 2024).then(pl.lit('Early')).otherwise(pl.lit('Rece...` | accepted | built | yes | 42 rows, String, 0 missing, #fe420176 | 1 |
| 1_test_data_ST22_dummy/wrangling/MLST_wrangling.yaml:9 | polars_with_columns | sequence_type | `pl.col('sequence_type').replace_strict({'unknown': 'Non Determined'}, defau...` | accepted | built | yes | 42 rows, String, 2 missing, #121596de | 17 |
| 1_test_data_ST22_dummy/wrangling/QA_AMR_per_sample.yaml:19 | polars_group_by | n_amr_genes | `pl.col('gene').count()` | accepted | built | yes | 74 rows, UInt32, 0 missing, #5b098933 | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key.yaml:8 | polars_with_columns | year_label | `pl.col('year').cast(pl.Int64).cast(pl.String)` | accepted | built | yes | 42 rows, String, 0 missing, #33adb551 | 2 |
| 1_test_data_ST22_dummy/wrangling/QA_aggregated_no_key.yaml:16 | polars_group_by | n_samples | `pl.col('sample_id').count()` | accepted | built | yes | 42 rows, UInt32, 0 missing, #5e86fc86 | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_fanout_exhibit.yaml:22 | polars_group_by | rows_per_sample | `pl.col('VF_gene').count()` | accepted | built | yes | 1731 rows, UInt32, 0 missing, #1cd46aa5 | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_population_zscore.yaml:18 | polars_with_columns | n50_zscore | `(pl.col('n50') - pl.col('n50').mean()) / pl.col('n50').std()` | accepted | built | yes | 42 rows, Float64, 0 missing, #79760dac | 1 |
| 1_test_data_ST22_dummy/wrangling/QA_year_types.yaml:6 | polars_with_columns | year_label | `pl.col('year').cast(pl.Int64).cast(pl.String)` | accepted | built | yes | 42 rows, String, 0 missing, #33adb551 | 2 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_wrangling.yaml:4 | polars_with_columns | status | `pl.lit('Detected')` | accepted | built | yes | 70 rows, String, 0 missing, #8d52e328 | 17 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_wrangling.yaml:10 | polars_with_columns | total_gene_count | `pl.len().over(['sample_id'])` | accepted | built | yes | 70 rows, UInt32, 0 missing, #72a82617 | 2 |
| 1_test_data_ST22_dummy/wrangling/ST22_Anchor_wrangling.yaml:54 | polars_with_columns | virulence_count | `pl.len().over(['sample_id'])` | accepted | built | yes | 70 rows, UInt32, 0 missing, #72a82617 | 2 |
| 1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml:19 | polars_with_columns | value | `pl.col('value').cast(pl.String).str.split(', ')` | accepted | built | yes | 168 rows, List(String), 9 missing, #68183f30 | 17 |
| 1_test_data_ST22_dummy/wrangling/VirulenceFinder_wrangling.yaml:6 | polars_with_columns | virulence_raw | `pl.col('virulence_raw').cast(pl.String).str.split(',')` | accepted | built | yes | 1315 rows, List(String), 0 missing, #b878da13 | 17 |

### Other shipped recipes and templates

| file:line | step | column | formula | today's check | D | D = today (plan, column) | result of the column in its recipe (today) | runs |
|---|---|---|---|---|---|---|---|---|
| 1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:21 | polars_with_columns | drug_name | `pl.col('cge_predicted_phenotype').str.split(',')` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:35 | polars_with_columns | AMR_Categories_Summary | `pl.when(pl.col('amr_class').is_not_null().any().over('fragment_row')).then(...` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| 1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:50 | polars_group_by | gene_count | `pl.col('AMR_Categories_Summary').count()` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| 2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:13 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 70 rows, String, 0 missing, #2a4980f3 | 1 |
| 2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:38 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 70 rows, Boolean, 0 missing, #b6aae85c | 1 |
| 2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:43 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 70 rows, String, 0 missing, #8609e5d2 | 1 |
| templates/complex_template/genomics_wrangling.yaml:4 | polars_with_columns | gene_presence | `pl.col('gene_presence').cast(pl.String).str.split(';')` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |

### Equality recipes (`app/tests/equality/recipes`)

| file:line | step | column | formula | today's check | D | D = today (plan, column) | result of the column in its recipe (today) | runs |
|---|---|---|---|---|---|---|---|---|
| eq/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 67 rows, String, 1 missing, #27b3d109 | 1 |
| eq/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 64 rows, Boolean, 0 missing, #28224714 | 1 |
| eq/2_test_data_ST22_dummy_dirty/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 64 rows, String, 0 missing, #5e1a8096 | 1 |
| eq/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 67 rows, String, 1 missing, #27b3d109 | 1 |
| eq/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 64 rows, Boolean, 0 missing, #28224714 | 1 |
| eq/2_test_data_ST22_dummy_dirty_no_null_text/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 64 rows, String, 0 missing, #5e1a8096 | 1 |
| eq/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 70 rows, String, 0 missing, #2a4980f3 | 1 |
| eq/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes | 70 rows, Boolean, 0 missing, #b6aae85c | 1 |
| eq/2_test_data_ST22_dummy_emptied/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes | 70 rows, String, 0 missing, #8609e5d2 | 1 |
| eq/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml:6 | polars_with_columns | predicted_phenotype_clean | `pl.col('predicted_phenotype').cast(pl.String).str.strip_chars().str.to_lowe...` | accepted | built | yes | 70 rows, String, 0 missing, #2a4980f3 | 1 |
| eq/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml:30 | polars_with_columns | is_multi_resistant_bool | `pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id...` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |
| eq/2_test_data_ST22_dummy_fractional_year/assembly/AMR_Profile_Joint.yaml:35 | polars_with_columns | Multiresistant | `pl.when(pl.col('is_multi_resistant_bool')).then(pl.lit('Yes')).otherwise(pl...` | accepted | built | yes (plan only) | not run on data (no recipe runs it) | 0 |

## A2. Today's check and evaluation on the real data (RAN: `a2_run_real.py`, `a2_output.txt`, `a2_summary.json`)

Method: the 11 recipes (7 shipped pipelines, 4 equality recipes) were built with the app's own path (`DataOrchestrator.materialize_tier1/2`, `VizFactory().render`, as `assets/scripts/golden_baseline.py` does). A hook on `transformer.actions.polars_calls.evaluate_formula` caught every formula the engine evaluated. For each: today's check, today's evaluation, D's build, the same plan (`Expr.meta.eq` and the text of the plan), and the column on the table the step receives (rows, type, missing values, hash of the values).

Results:
- 113 formula evaluations, 17 distinct texts. Check: accepted 113. Today's evaluation: 0 errors. D: 0 errors.
- Same plan (`meta.eq`): 113 of 113. Same column (type, missing values, values): 113 of 113.
- 102 table records (tier 1, tier 2, the table of each plot) built with today's evaluation: equal to `app/tests/golden/baseline.json` for all 7 shipped pipelines. Built with D in place of `evaluate_formula`: identical to today's for all 11 recipes.
- One recipe, `2_test_data_ST22_dummy_fractional_year`, refuses the cast on purpose (the data has a decimal Year); tier 2 and one plot are absent, the same for both ways.
- Not run on data: the 3 orphan lines and the template line. For them only the plan was compared (equal).

A finding that is not about formulas (RAN: `a2b_order_probe.py`): in my first version I took the column with `lf.select(expr)`. For the formula `resistance_points` the values came out in a different order at each collect (10 collects: 10 different hashes, 1 hash after sorting; the full table: 1 hash in 10). The optimized plan shows `UNIQUE[maintain_order: false]` where the step wrote `maintain_order: true` (`a2b_plan_optimized.txt`). It happens only when the plan is cut to one column. The app's own path (the whole table) is stable and equal to the baseline. I changed my probe to `with_columns` and the difference went away. I did not investigate Polars further. See "Found outside the task".


## A3. The 60 hostile lines through today's check on this `dev` (RAN: `a3_b3_hostile.py`, `a3_b3_table.json`)

The lines are read from `tmpAI/panel/formula_safety/hostile.py` (not retyped). Only the expression is built; nothing is collected. The numbers are the position in that file, from 1.

Result: 54 REFUSED, 6 ACCEPTED. Since the earlier report (8 accepted) three lines are refused: `str.json_decode(pl.Object)` (D-0230), `shuffle` and `sample` (D-0278, D-0279). One line became accepted: `list.eval(pl.element())`, when `pl.element` was allowed (D-0231).

The 6 accepted, and what each does (RAN: `a3_accepted_run.txt`, on a small table):

| # | line | what it does | risk |
|---|---|---|---|
| 35 | `pl.col('a').bin.decode('hex')` | on a text column: SchemaError ("expected Binary"). On a binary column: decodes hex text to bytes (`b'6162'` gives `b'ab'`). | None found. It reads no file. |
| 39 | `pl.lit('/etc/passwd')` | a column that holds the text `/etc/passwd`. No file is read. | None. It is a text value. |
| 59 | `pl.col('a').list.eval(pl.element())` | allowed on purpose (D-0231, `formula_check.py:58-61`); returns the list column unchanged. | None. |
| 45 | `pl.col('a').repeat_by(10**12)` | builds an expression for a list of a trillion copies per row. NOT built here (size). Earlier report: accepted, "D-0064: no size limit now". | Memory. |
| 46 | `pl.lit('a') * 10**9` | text times a number. NOT built here (size). | Memory. |
| 51 | `pl.col('a').cast(pl.String).str.pad_start(4000000000)` | pads text to 4 billion characters. NOT built here (size). | Memory. |

None of the 6 runs code or reads outside the data (READ for 45, 46, 51: not run; the earlier report names them as memory). The check accepts them, so they would run in the app today.

The full table (the 20 new lines follow it):

| # | class | line | today's check | message (first 70 chars) | D with check | D walk alone |
|---|---|---|---|---|---|---|
| 1 | attribute walking | `pl.col('a').__class__` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 2 | attribute walking | `pl.col('a').str.__class__.__mro__` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 3 | attribute walking | `pl.Expr.__subclasses__()` | REFUSED | pl.Expr is not allowed. Fix: use one of: all, all_horizontal, any, any | REFUSED | REFUSED |
| 4 | attribute walking | `pl.col('a').__init__.__globals__` | REFUSED | the attribute '__init__' starts with an underscore. Fix: build the col | REFUSED | REFUSED |
| 5 | attribute walking | `pl.os.system('id')` | REFUSED | pl.os is not allowed. Fix: use one of: all, all_horizontal, any, any_h | REFUSED | REFUSED |
| 6 | attribute walking | `pl.sys.modules` | REFUSED | pl.sys is not allowed. Fix: use one of: all, all_horizontal, any, any_ | REFUSED | REFUSED |
| 7 | dunder | `().__class__.__bases__[0].__subclasses__()` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 8 | dunder | `pl.__builtins__` | REFUSED | the attribute '__builtins__' starts with an underscore. Fix: build the | REFUSED | REFUSED |
| 9 | dunder | `pl.col('a').__reduce__()` | REFUSED | the attribute '__reduce__' starts with an underscore. Fix: build the c | REFUSED | REFUSED |
| 10 | dunder | `pl.__spec__.loader` | REFUSED | the attribute '__spec__' starts with an underscore. Fix: build the col | REFUSED | REFUSED |
| 11 | format strings | `'{0.__class__}'.format(pl)` | REFUSED | format is not an expression method. Fix: build the column with pl.col, | REFUSED | REFUSED |
| 12 | format strings | `pl.col('a').inspect('{0.__init__.__globals__}')` | REFUSED | inspect prints the column to the server output with a text that can re | REFUSED | REFUSED |
| 13 | format strings | `pl.format('{}', pl.col('a')).__class__` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 14 | format strings | `f'{pl.__file__}'` | REFUSED | JoinedStr is not allowed in a formula. Fix: build the column with pl.c | REFUSED | REFUSED |
| 15 | comprehension scopes | `[c for c in ().__class__.__mro__]` | REFUSED | ListComp is not allowed in a formula. Fix: build the column with pl.co | REFUSED | REFUSED |
| 16 | comprehension scopes | `[x for x in (1,2)]` | REFUSED | ListComp is not allowed in a formula. Fix: build the column with pl.co | REFUSED | REFUSED |
| 17 | comprehension scopes | `{k: v for k, v in [(1, 2)]}` | REFUSED | DictComp is not allowed in a formula. Fix: build the column with pl.co | REFUSED | REFUSED |
| 18 | comprehension scopes | `(x for x in [1])` | REFUSED | GeneratorExp is not allowed in a formula. Fix: build the column with p | REFUSED | REFUSED |
| 19 | lambda | `(lambda: __import__('os'))()` | REFUSED | Lambda is not allowed in a formula. Fix: build the column with pl.col, | REFUSED | REFUSED |
| 20 | lambda | `pl.col('a').map_elements(lambda v: v)` | REFUSED | map_elements runs a Python function and is not allowed. Fix: build the | REFUSED | REFUSED |
| 21 | lambda | `pl.col('a').map_batches(print)` | REFUSED | map_batches runs a Python function and is not allowed. Fix: build the  | REFUSED | REFUSED |
| 22 | lambda | `pl.col('a').pipe(print)` | REFUSED | pipe runs a Python function and is not allowed. Fix: build the column  | REFUSED | REFUSED |
| 23 | builtins | `eval('1+1')` | REFUSED | the name 'eval' is not allowed; only pl is known. Fix: write pl.<funct | REFUSED | REFUSED |
| 24 | builtins | `exec('import os')` | REFUSED | the name 'exec' is not allowed; only pl is known. Fix: write pl.<funct | REFUSED | REFUSED |
| 25 | builtins | `open('/etc/passwd').read()` | REFUSED | the name 'open' is not allowed; only pl is known. Fix: write pl.<funct | REFUSED | REFUSED |
| 26 | builtins | `getattr(pl, 'read_csv')` | REFUSED | the name 'getattr' is not allowed; only pl is known. Fix: write pl.<fu | REFUSED | REFUSED |
| 27 | builtins | `print(pl)` | REFUSED | the name 'print' is not allowed; only pl is known. Fix: write pl.<func | REFUSED | REFUSED |
| 28 | imports | `__import__('os').system('id')` | REFUSED | the name '__import__' is not allowed; only pl is known. Fix: write pl. | REFUSED | REFUSED |
| 29 | imports | `import os` | REFUSED | the formula is not a valid expression (SyntaxError). Fix: write one Py | REFUSED | REFUSED |
| 30 | imports | `pl.col('a') if True else __import__('os')` | REFUSED | IfExp is not allowed in a formula. Fix: build the column with pl.col,  | REFUSED | REFUSED |
| 31 | serialised data | `pl.Expr.deserialize('/tmp/x.json')` | REFUSED | pl.Expr is not allowed. Fix: use one of: all, all_horizontal, any, any | REFUSED | REFUSED |
| 32 | serialised data | `pl.Expr.from_json('{}')` | REFUSED | pl.Expr is not allowed. Fix: use one of: all, all_horizontal, any, any | REFUSED | REFUSED |
| 33 | serialised data | `pl.col('a').meta.serialize()` | REFUSED | meta reads the structure of an expression and can write it to a file o | REFUSED | REFUSED |
| 34 | serialised data | `pl.col('a').str.json_decode(pl.Object)` | REFUSED | pl.Object holds any Python object, which a table column does not; a re | REFUSED | REFUSED |
| 35 | serialised data | `pl.col('a').bin.decode('hex')` | ACCEPTED |  | ACCEPTED | BUILT |
| 36 | file paths | `pl.read_csv('/etc/passwd')` | REFUSED | pl.read_csv is not allowed. Fix: use one of: all, all_horizontal, any, | REFUSED | REFUSED |
| 37 | file paths | `pl.scan_parquet('/etc/shadow').collect()` | REFUSED | pl.scan_parquet is not allowed. Fix: use one of: all, all_horizontal,  | REFUSED | REFUSED |
| 38 | file paths | `pl.read_json('x.json')` | REFUSED | pl.read_json is not allowed. Fix: use one of: all, all_horizontal, any | REFUSED | REFUSED |
| 39 | file paths | `pl.lit('/etc/passwd')` | ACCEPTED |  | ACCEPTED | BUILT |
| 40 | file paths | `pl.sql_expr('1')` | REFUSED | pl.sql_expr is not allowed. Fix: use one of: all, all_horizontal, any, | REFUSED | REFUSED |
| 41 | file paths | `pl.SQLContext()` | REFUSED | pl.SQLContext is not allowed. Fix: use one of: all, all_horizontal, an | REFUSED | REFUSED |
| 42 | plugins | `pl.col('a').register_plugin(lib='/tmp/x.so', symbol='f')` | REFUSED | register_plugin loads or reads something outside the expression (a fil | REFUSED | REFUSED |
| 43 | plugins | `pl.Config.set_tbl_rows(1)` | REFUSED | pl.Config is not allowed. Fix: use one of: all, all_horizontal, any, a | REFUSED | REFUSED |
| 44 | plugins | `pl.col('a').ext.to('x')` | REFUSED | ext is not an expression method. Fix: build the column with pl.col, pl | REFUSED | REFUSED |
| 45 | large allocations | `pl.col('a').repeat_by(10**12)` | ACCEPTED |  | not built (size) | not built (size) |
| 46 | large allocations | `pl.lit('a') * 10**9` | ACCEPTED |  | not built (size) | not built (size) |
| 47 | large allocations | `pl.col('a') ** 99999999` | REFUSED | an exponent must be a constant number up to 100. Fix: build the column | REFUSED | BUILT |
| 48 | large allocations | `pl.lit(10**10000)` | REFUSED | an exponent must be a constant number up to 100. Fix: build the column | REFUSED | OTHER:InvalidOperationError |
| 49 | large allocations | `pl.col('a').abs().abs().abs().abs().abs().abs().abs().abs()...` | REFUSED | the formula is longer than 2000 characters. Fix: split it into several | REFUSED | OTHER:RecursionError |
| 50 | large allocations | `pl.lit('x'*5000)` | REFUSED | a text or a list cannot be multiplied or formatted with an operator. F | REFUSED | BUILT |
| 51 | large allocations | `pl.col('a').cast(pl.String).str.pad_start(4000000000)` | ACCEPTED |  | not built (size) | not built (size) |
| 52 | nondeterminism | `pl.col('a').shuffle()` | REFUSED | shuffle draws at random, so the result would differ at each run and th | REFUSED | REFUSED |
| 53 | nondeterminism | `pl.col('a').sample(n=3)` | REFUSED | sample draws at random, so the result would differ at each run and the | REFUSED | REFUSED |
| 54 | others | `pl.col('a') << 5` | REFUSED | << is not allowed. Fix: build the column with pl.col, pl.lit, pl.when  | REFUSED | REFUSED |
| 55 | others | `*pl.col('a')` | REFUSED | the formula is not a valid expression (SyntaxError). Fix: write one Py | REFUSED | REFUSED |
| 56 | others | `pl.col(*['a'])` | REFUSED | starred arguments are not allowed. Fix: build the column with pl.col,  | REFUSED | REFUSED |
| 57 | others | `pl.col(**{'name':'a'})` | REFUSED | ** arguments are not allowed. Fix: build the column with pl.col, pl.li | REFUSED | REFUSED |
| 58 | others | `pl.col('a').__getattribute__('x')` | REFUSED | the attribute '__getattribute__' starts with an underscore. Fix: build | REFUSED | REFUSED |
| 59 | others | `pl.col('a').list.eval(pl.element())` | ACCEPTED |  | ACCEPTED | BUILT |
| 60 | others | `pl.col('a').list.eval(pl.col('a').map_elements(print))` | REFUSED | map_elements runs a Python function and is not allowed. Fix: build the | REFUSED | REFUSED |

New lines (my own, harmless to build):

| # | class | line | today's check | today builds | D builds |
|---|---|---|---|---|---|
| 101 | python method on a literal | `[3, 1, 2].sort()` | ACCEPTED | ACCEPTED  | REFUSED the attribute 'sort' is not allowed here: only a column expr |
| 102 | python method on a literal | `pl.lit('abc').str.len_chars() + 'abc'.count('a')` | ACCEPTED | ACCEPTED  | REFUSED the attribute 'count' is not allowed here: only a column exp |
| 103 | python method on a literal | `(1).abs()` | ACCEPTED | OTHER:AttributeError 'int' object has no attribute 'abs' | REFUSED the attribute 'abs' is not allowed here: only a column expre |
| 104 | function left uncalled | `[pl.col]` | ACCEPTED | ACCEPTED  | REFUSED a function or the name pl is left uncalled (character 2). Fi |
| 105 | function left uncalled | `{'f': pl.col}['f']('a')` | ACCEPTED | ACCEPTED  | REFUSED a function or the name pl is left uncalled (character 7). Fi |
| 106 | chained comparison | `pl.col('a') < pl.col('b') < 3` | ACCEPTED | REFUSED the formula "pl.col('a') < pl.col('b') < 3" could  | REFUSED the formula "pl.col('a') < pl.col('b') < 3" could not be bui |
| 107 | and/or on columns | `pl.col('a') and pl.col('b')` | ACCEPTED | REFUSED the formula "pl.col('a') and pl.col('b')" could no | REFUSED the formula "pl.col('a') and pl.col('b')" could not be built |
| 108 | repeated keyword | `pl.lit(1, dtype=pl.Int64, dtype=pl.Int64)` | ACCEPTED | OTHER:SyntaxError keyword argument repeated: dtype (<formula>, line  | REFUSED the formula 'pl.lit(1, dtype=pl.Int64, dtype=pl.Int64)' coul |
| 109 | subscript of the module | `pl['col']` | ACCEPTED | REFUSED the formula "pl['col']" could not be built: 'modul | REFUSED a function or the name pl is left uncalled (character 1). Fi |
| 110 | call of a column | `pl.col('a')()` | ACCEPTED | REFUSED the formula "pl.col('a')()" could not be built: 'E | REFUSED this cannot be called (character 1). Fix: call a pl function |
| 111 | power of a power (time) | `pl.lit((((10**100)**100)**100)**100)` | ACCEPTED | NOT BUILT (check only)  | NOT BUILT (check only)  |
| 112 | large allocation | `pl.col('a').repeat_by(10**12)` | ACCEPTED | NOT BUILT (check only)  | NOT BUILT (check only)  |
| 113 | large allocation | `pl.col('a').cast(pl.String).str.pad_start(4000000000)` | ACCEPTED | NOT BUILT (check only)  | NOT BUILT (check only)  |
| 114 | regex time | `pl.col('a').str.contains('(a+)+$')` | ACCEPTED | ACCEPTED  | ACCEPTED  |
| 115 | dtype names | `pl.col('a').cast(pl.Unknown)` | REFUSED | REFUSED pl.Unknown is not a real type for a column: a cast | REFUSED pl.Unknown is not a real type for a column: a cast to it sil |
| 116 | dtype names | `pl.col('a').str.json_decode(pl.Binary)` | REFUSED | REFUSED pl.Binary holds raw bytes, which a recipe table do | REFUSED pl.Binary holds raw bytes, which a recipe table does not hol |
| 117 | random | `pl.col('a').rank(method='random')` | REFUSED | REFUSED rank with method 'random' breaks ties at random, s | REFUSED rank with method 'random' breaks ties at random, so the resu |
| 118 | random | `pl.col('a').shuffle()` | REFUSED | REFUSED shuffle draws at random, so the result would diffe | REFUSED shuffle draws at random, so the result would differ at each  |
| 119 | random | `pl.col('a').sample(n=3)` | REFUSED | REFUSED sample draws at random, so the result would differ | REFUSED sample draws at random, so the result would differ at each r |
| 120 | random | `pl.col('a').rank(method=pl.lit('x').meta.output_name())` | REFUSED | REFUSED meta reads the structure of an expression and can  | REFUSED meta reads the structure of an expression and can write it t |

Reading of the new lines (RAN):
- Lines 101 to 105 are accepted today and run Python: `[3, 1, 2].sort()` really sorts a list in place and returns `None`; `'abc'.count('a')` runs the text method. The check allows a method on a number, text, list or dictionary when its name is also an `Expr` method. Names that coincide (RAN: `b4_literal_methods.txt`): text `count`, `replace`; list `append`, `count`, `reverse`, `sort`; tuple `count`; dictionary `get`. None of them reads a file or runs code, so the risk today is nil. It is a door that depends on Polars' own method names. `(1).abs()` ends with a raw `AttributeError`, not a plain message (line 103).
- Lines 104 and 105: a function name left uncalled inside a list or a dictionary is accepted today (`[pl.col]` returns a list with a Polars function inside).
- Line 108: a repeated keyword gives a raw `SyntaxError` today (not caught as `FormulaError`).
- Line 111: `pl.lit((((10**100)**100)**100)**100)` is accepted. Every exponent is at most 100, but the powers multiply: the result would have about 332 million bits. RAN: 2 levels take 0.3 ms, 3 levels take 0.32 s (3.3 million bits). The fourth level was NOT run (REASONED: minutes and about 40 MB). Both today's way and D would compute it, because Python does the arithmetic on constants.
- Line 114: `str.contains('(a+)+$')` is accepted and is not a time bomb: 0.2 to 3.6 ms for 30 to 30000 characters (RAN: `b4_regex_time.txt`; Polars' regex engine has no backtracking).

## A4. What today's check guarantees, what it does not, what is unproven

**The text is evaluated with `eval`.** READ: `formula_check.py:517`: `eval(compile(ast.parse(text.strip(), mode="eval"), "<formula>", "eval"), dict(EVAL_GLOBALS))`. The visible names: `EVAL_GLOBALS = {"__builtins__": {}, "pl": pl}` (`formula_check.py:508`): only `pl`, and no builtins. `pl` is the real Polars module, so `pl.os` is visible (RAN: `hasattr(pl, 'os')` is True).

**What stops a name outside the list from being reached.** READ: the check. It refuses any name other than `pl` (`:305-309`), any attribute that starts with `_` (`:315-317`), `pl.<name>` that is not in `MODULE_FUNCTIONS` or a dtype (`:319-328`), and any method that is not in `_allowed()` (`:343-358`). The second layer (empty builtins) does NOT stop a reach through `pl`. RAN (`weak_table.md`, below): with the check switched off, `eval` ran 10 of 12 harmless probes, among them `pl.os.getpid()`, `pl.__name__` and `[x for x in (1, 2)]`. Only `len(...)` and `eval(...)` failed (no builtins). So today the check is the only barrier against `pl.os.system(...)`.

**What today's check guarantees (with the test that pins it).** RAN: `a4_mutations.py` breaks the check once per rule and counts the failing tests among the 6 formula test files (527 tests):

| Rule broken | Tests that fail | Where |
|---|---|---|
| any name allowed (only `pl` known) | 10 | `test_formula_check.py` (9), `test_formula_refuses_random.py` (1) |
| any `pl.<name>` allowed (the module list) | 60 | `test_formula_check`, `test_formula_element_field`, `test_formula_refusals_2026_11_18`, `test_formula_refuses_object` |
| the refused-by-name list ignored (`inspect`, `meta`, `set_sorted`, `search_sorted`, `shuffle`, `sample`) | 40 | four files |
| functions as arguments allowed (`map_elements`, `pipe`) | 30 | four files |
| classmethods allowed (`deserialize`, `from_json`) | 20 | `test_formula_reads_no_outside_data.py` |
| outside names (`lib`, `path`) allowed | 15 | two files |
| the dtype refusals removed (`Object`, `Unknown`, `Binary`) | 53 | three files |
| the random rank check removed | 43 | `test_formula_refuses_random.py` |
| **the underscore rule removed** | **0** | no test fails |
| **the exponent limit raised to a billion** | **0** | no test fails |

Two rules have no test that fails when they are broken. The underscore rule is covered by the list (RAN: `a4_underscore_without_rule.txt`: with the rule removed, `__class__`, `__reduce__` and `pl.__name__` are still refused, as "not an expression method"), so it is a second layer. The exponent limit (`pl.col('a') ** 99999999`, `MAX_EXPONENT = 100`, `formula_check.py:52`) has no test at all: a change of the limit would go unseen.

Of the 60 hostile lines, 9 are exact texts in a test file (RAN: `b_corpus.py`); the classes are pinned by tests with other texts (table above). The trial test `libs/utils/tests/test_formula_build.py` adds the 54 refused lines.

**What today's check does not guarantee.**
- It reads signatures and parameter names; it cannot see a member that is dangerous by what it does. READ: the code says it is "a net with holes, not a proof" (`formula_check.py:206-211`). Two holes were found on 2026-11-17 (`deserialize`, `inspect`; `:15-17`, `:143-145`).
- Polars panics: a panic is a `BaseException`, not caught (`polars_calls.py:199` catches `Exception`). One is left (section C).
- Memory and time: lines 45, 46, 51, 111 (above). D-0064: "no time or size limit now".
- Python's own methods on a literal (lines 101 to 105): harmless today, a door that depends on Polars' names.
- `hash()` is allowed and its values change between Polars versions (READ: the Polars docstring of the installed 1.40.1: "does not guarantee stable results across different Polars versions").

**What remains unproven.** That the allowed lists (196 `Expr` members, 40 module functions, 150 namespace members: `str` 49, `dt` 47, `list` 41, `arr` 30, `cat` 6, `struct` 5, `name` 8, `bin` 11, RAN) hold no other member that is dangerous by effect. The walk test reads signatures and the words of the documentation; I did not read each of the members. I did not search for other panics than `json_decode`.


---

# PART B. Option D as a prototype

## B1. What was built (READ: `libs/utils/src/utils/formula_build.py`, 269 lines, 204 of code; trial commit `fb0a59e7`)

The written form of a formula is unchanged. `build_formula(text)` has the same contract as `evaluate_formula(text)` (`formula_build.py:250`):
1. `formula_problems(text)` of today's check runs first. A refused formula gives the same message (the same function, so one set of policy rules: exponent, text multiplied, random rank, `pl.Object`, `shuffle`, argument counts of `pl.element` and `pl.field`).
2. The text is parsed with `ast.parse` (no `compile`) and walked by `_Builder` (`:91-243`). A value is built only from constants, lists, tuples, dictionaries, operators and calls of listed members.
3. There is no `eval`, `exec` or `compile` in the file. `getattr` appears only in `_tables()` (`:67-75`), with names that come from the lists of the check, never from the text. A name of the text is looked up in a dictionary; a miss is refused.

**How the list is shared (one list, not two).** `formula_build.py:21-23` imports `MODULE_FUNCTIONS`, `REFUSED_DTYPES`, `_NAMESPACES`, `_allowed`, `_dtypes`, `_namespace_classes`, `refused_members` and the message texts from `formula_check.py`. `_tables()` (`:52-88`) builds its dictionaries from them once:

| Table of D | Read from |
|---|---|
| module functions | `MODULE_FUNCTIONS` |
| dtypes | `_dtypes()` minus `REFUSED_DTYPES` |
| `Expr` methods | `_allowed()["expr"]` |
| namespace members | `_allowed()[name]` for the namespaces of `_NAMESPACES` |
| the objects after `pl.when(...)` | the four classes that `pl.when` and `.then` return |

RAN: `test_the_tables_are_read_from_the_lists_of_the_check` (in `test_formula_build.py`) asserts the tables equal the lists. A new Polars member, a new refusal or a new dtype entry changes both with no second edit. In production the private names (`_allowed` and the others) would have to become public.

**Where D is stricter on purpose.** After `.then(...)` the walk follows the types that Polars returns, not a guess from the text. A method called on a number, text, list or dictionary (not a column expression) is refused. A function name left uncalled inside a list or dictionary is refused.

## B2. Equality (RAN)

| Check | Result | Script and output |
|---|---|---|
| the 17 distinct texts the engine evaluated on the real data | 113 of 113 evaluations: same plan (`meta.eq`), same column (type, missing, values) | `a2_run_real.py`, `a2_summary.json` |
| the tables of 11 recipes (102 records) with D in place of `evaluate_formula` | identical to today's; the 7 shipped pipelines identical to `golden/baseline.json` | `a2_tables_d.json` |
| 305 distinct texts of recipes, test data and test sources (436 places) | 169 built by both: 169 same plan and same plan text. 136 refused by both: 136 same message. 0 mismatch | `b_corpus.py`, `b2_output.txt` |
| 75 constructs of the grammar | 52 built by both, same plan: 52. 23 refused by both, same message: 23. 0 mismatch | `b2_constructs.py` |
| 15 existing test files with D patched into the call sites (`polars_calls`, `id_reconciliation`, the tests) | 1597 tests pass; the same 1597 pass unpatched | `b2_tests_with_d.py` |
| the trial test file | 106 tests pass | pytest |

The 305 texts come from: the YAML files of section A1 (shipped and test), the string constants of every test source under `libs/*/tests` and `app/tests` that parse as a formula (formula check 193 texts, transformer 53, other 24), and the JSON test data (26). The 15 test files: 6 formula test files of `libs/utils/tests`, 7 of the transformer (polars equality, rows, aggregations, step conversion, recipe pairs, deterministic order), 2 of `id_reconciliation`.

**What D cannot build that today builds.** Among the 305 and the 75: nothing. Among my own new lines: the ones of section B3 (Python methods on a literal, uncalled function names in a container).

**A drift I found while building.** The first version refused `pl.when(a).then(1).when(b).then(2).alias('q')`: after a chained `.then`, an expression method such as `.alias` was not allowed. The 305 texts did not contain this shape; the construct list did (`b2_constructs.py`). I fixed it. This is the cost of two walks (the check and the builder): they can drift apart. A test that runs every refused or accepted shape through both is the guard; merging the check and the builder into one walk is an option (not built).

**Constructs listed in the brief (RAN: `b2_constructs.json`):** lambda inside `list.eval` (refused by both, the check refuses `Lambda`); `pl.element()` (equal); keyword arguments (equal); operators and their order (equal: the parser fixes the tree); chained comparison (both stop with Polars' "truth value of an Expr is ambiguous"); unary minus, invert (equal); `pl.when().then().otherwise()` chains of 1, 3 and without `otherwise` (equal); selectors `pl.col('^a.*$')`, `pl.col(pl.Int64, pl.Float64)`, `pl.all().exclude(...)` (equal); date, datetime, duration literals (equal); nested lists, tuples, dictionaries (equal); dtype objects `pl.List(pl.Struct({...}))`, `pl.Datetime('us','UTC')`, `pl.Enum([...])`, `pl.Decimal(10,2)`, `pl.Array(pl.Int64,3)`, `pl.Int64()` (equal). Hard to walk: nothing was hard. The only subtle one is the order of evaluation of `and`/`or` and chained comparisons: D does what Python does (calls `bool` on a column, which Polars refuses with a TypeError), so the error is the same as today's.

## B3. The hostile lines through D (RAN: `a3_b3_hostile.py`)

- The 60 lines: D with the check gives the same answer as today on all 60 (54 refused with the same message; 6 accepted). 0 differences.
- The 20 new lines: 8 differ from today. D refuses where today accepts (lines 101 to 105: Python methods on literals, uncalled functions in containers) or where today stops with a raw error (103: `AttributeError`; 108: `SyntaxError`). Both refuse with a different text on 109 and 110.
- The walk alone (no check), on the 54 hostile lines that the check refuses: 50 are refused by the walk (2 of them are not expressions: `import os` and `*pl.col('a')` stop at the parser). 2 are built, because they are policy of the check, not reach: `pl.col('a') ** 99999999` and `pl.lit('x'*5000)`. 2 end with another error: `pl.lit(10**10000)` (Polars refuses the huge integer) and the chain of 500 calls (RecursionError; D with the check never reaches it, the text is longer than 2000 characters). Among my new lines `rank(method='random')` is also built by the walk alone. So the walk is not a copy of the policy: D = check + walk.
- No line is refused by today's check and built by D, and none the reverse for the 60.

## B4. What D removes, what it does not

**Removes (RAN: `a3_b3_hostile.py`, `weak_table.md`).** With the check switched off, `eval` ran 10 of 12 harmless probes. D's walk refused all 12 on its own.

| class | probe (harmless) | `eval` path when the check is off | D walk when the check is off |
|---|---|---|---|
| attribute walking | `pl.col('a').__class__.__name__` | RAN: 'Expr' | REFUSED by the walk: the attribute '__class__' starts with an underscore (character 1). Fi |
| module attribute | `pl.__name__` | RAN: 'polars' | REFUSED by the walk: the attribute '__name__' starts with an underscore (character 1). Fix |
| module attribute | `pl.os.getpid() > 0` | RAN: True | REFUSED by the walk: pl.os is not allowed (character 1). Fix: use one of: all, all_horizon |
| dunder on a literal | `(1).__class__.__name__` | RAN: 'int' | REFUSED by the walk: the attribute '__class__' starts with an underscore (character 1). Fi |
| format string | `'{0.__class__.__name__}'.format(pl.col('a'))` | RAN: 'Expr' | REFUSED by the walk: the attribute 'format' is not allowed here: only a column expression  |
| comprehension | `[x for x in (1, 2)]` | RAN: [1, 2] | REFUSED by the walk: ListComp is not allowed in a formula (character 1). Fix: build the co |
| lambda | `(lambda: 1)()` | RAN: 1 | REFUSED by the walk: Lambda is not allowed in a formula (character 2). Fix: build the colu |
| conditional | `pl.col('a') if True else pl.col('b')` | RAN: <Expr ['col("a")'] at 0x7FD263F29450> | REFUSED by the walk: IfExp is not allowed in a formula (character 1). Fix: build the colum |
| uncalled outside function | `[pl.read_csv]` | RAN: [<function read_csv at 0x7fd2680fcf60>] | REFUSED by the walk: pl.read_csv is not allowed (character 2). Fix: use one of: all, all_h |
| python method on a literal | `[3, 1, 2].sort()` | RAN: None | REFUSED by the walk: the attribute 'sort' is not allowed here: only a column expression ha |
| name outside the list | `len([1, 2])` | error NameError: name 'len' is not defined | REFUSED by the walk: the name 'len' is not allowed; only pl is known (character 1). Fix: w |
| eval name | `eval('1 + 1')` | error NameError: name 'eval' is not defined | REFUSED by the walk: the name 'eval' is not allowed; only pl is known (character 1). Fix:  |

So the class "a name outside the list is reached through a trick" is closed by the walk, not only by the check. The tricks of the earlier report that rely on it (attribute walking, dunder, format strings, comprehension, lambda, builtins, conditional) are refused twice: by the check and by the walk. Also closed: Python's own methods on literals (8 names, above), and a function object passed as a value.

Mutation check of the walk (RAN: `mutation1.txt`, `mutation2.txt`): when the module lookup uses `getattr` with the text's name and the underscore guard is removed, 3 tests fail (the source test, `pl.__name__`, `[pl.read_csv]`). When `+` is built as `-`, 2 tests fail. `pl.os.getpid()` was still refused after the first break, because the next step (`.getpid` on a module) is refused by the walk's type check: two layers inside the walk.

**Does NOT remove (with evidence).**
- A wrong entry in the list. D calls what the list allows. READ: `formula_check.py:15-17`: until 2026-11-17 `Expr.deserialize` was allowed by name and could read any file. D would have called it just the same.
- Members dangerous by what they do. None known today after `inspect` (D-0229). The check and D cannot see one.
- Polars panics: D calls the same functions (section C: `pl.Array` in `json_decode`, RAN).
- Memory and time: lines 45, 46, 51 (accepted by both, REASONED: the same Polars call) and 111 (constant powers: both compute them in Python). D could refuse a constant calculation that grows too large because it does the operation itself; today's way cannot. Not built.
- `shuffle` and `sample` without a seed, and `rank(method='random')`: refused already by the check (D-0278, D-0279) and so refused by D. D adds nothing.
- `hash()` instability across Polars versions: same.

## B5. Error messages (RAN: `b2_constructs.json`, `b2_output.txt`)

- For a part the check refuses, D shows the same message, because it is the same function: 136 of 136 refused texts and 23 of 23 constructs have the same message.
- Today's messages carry no place in the formula. Example: `the attribute '__class__' starts with an underscore. Fix: build the column with pl.col, ...`. The check has the syntax tree, so it could give the character position for every refusal. That is a change to the check and does not need D.
- For what only D's walk refuses, the message has the place: `the attribute 'sort' is not allowed here: only a column expression has methods (character 1). Fix: build the column with pl.col, pl.lit, pl.when and the Polars expression methods.` and `a function or the name pl is left uncalled (character 2). Fix: call it, for example pl.col('x').`
- A Polars error while building (wrong number of arguments, `bool` of a column) gives the same text as today (`the formula '...' could not be built: ... Suggestion: check the arguments of each call against the Polars documentation`).

## B6. Cost

- Code: `formula_build.py` 269 lines (204 of code, with the docstring). The earlier estimate was about 400 lines. The test file `test_formula_build.py` 200 lines (160 of code). Today's check stays as it is: `_Checker` and the parse take about 190 lines of `formula_check.py` (`:283-475`), and 2 lines are the `eval` (`:508`, `:517`). RAN: `git diff --stat`: 469 lines added, none removed.
- Speed, build time only (RAN: `b6_cost.py`, 169 formulas, median of 15 runs): check alone 44 µs per formula; today (check + eval) 108 µs; D (check + walk) 98 µs. First call: tables of D 0.95 ms. No measurable cost.
- What would change in the app if D replaced today's way:
  - `libs/transformer/src/transformer/actions/polars_calls.py:31,195` (`_formula`): `evaluate_formula` becomes `build_formula`. One import and one call. The `except FormulaError` and `except Exception` stay.
  - `libs/id_reconciliation/src/id_reconciliation/core.py:6,254`: the same.
  - `libs/utils/src/utils/recipe_check.py:41,601`: uses `formula_problems` only; no change.
  - `formula_check.py`: `evaluate_formula`, `EVAL_GLOBALS` and the `eval` line go (or stay for the tests). The private names that D reads become public.
  - Tests: 6 test files import `evaluate_formula` (`test_formula_check`, `test_formula_element_field`, `test_formula_reads_no_outside_data`, `test_formula_refusals_2026_11_18`, `test_formula_refuses_object`, `test_formula_refuses_random`); with D patched in they pass (1597 of 1597). They would import the new name.
  - Documents: `recipe_format_spec.md` section 15 ("run with empty builtins"), the `@deps` blocks, `dependency_index.md`, the check rule ST06 text.
- Effort tag, as information only (D-0268): [sonnet/medium]. The prototype took one session. Production would add: public names, one walk or a drift test, the doc updates, and the untested exponent limit.

## B7. Options B and C of question 18

- B, a structure in YAML: a formula is written as nested mappings (the earlier scientist converted five formulas to 14 and 17 lines of YAML for one line of text). No text is evaluated.
- C, an own small language with an own parser: a formula is written in a smaller grammar (shorter than Polars text; a parser of our own, a result tied to the parser version). No text is evaluated.
- Once D exists, my evidence shows D gives the first reason for B and C (no text evaluated, the written form unchanged, results equal on the real data). I did not test B or C. What my evidence cannot judge and D does not give: B and C name their own functions, so a Polars upgrade does not change what a formula means (D follows Polars: the lists are read from the installed Polars and `hash()` changes between versions, REASONED for B and C); and B and C can put a rule on an argument (a type, a range) in a table, which D leaves to Polars. Length to write and readability: no new evidence from me; the earlier reports hold the numbers.


---

# PART C. Points that still need Eve's word (section 5 of `REPORT_formula_safety.md`)

No default from me. What each option costs is from my evidence.

**C1. Seed for `shuffle` and `sample`.** Status: both are refused now, with `rank(method='random')` and a computed rank method (D-0278, D-0279; `formula_check.py:149-176`, `_check_random_rank` at `:383-399`; RAN: lines 117 to 120 of the table). The text of the refusal says "refused for now, also with a seed, until a seed rule for formulas exists". The earlier question (require a seed or refuse) is answered for now: refuse. What is open: the day a recipe needs a random order.
- Option a: keep them refused; use the step `polars_sample` (a seed in the step) for a random sample of rows.
- Option b: allow them with a seed written in the formula (`seed=1`) and refuse them without one.
- What the evidence shows (RAN: `c_seed_run.txt`, Polars called directly): `shuffle(seed=1)` gave the same order in 3 runs; `sample(n=3, seed=7)` the same rows in 3 runs; `shuffle()` without a seed gave 5 different orders in 5 runs. Under option b the check would have to see the seed as a plain number in the text (the same rule as the random rank method). I found no other allowed member that takes a seed except `hash` (default seed 0, deterministic inside one Polars version; READ: Polars docstring) and `rank`, `rolling_rank`, `rolling_rank_by` (handled).

**C2. Polars panics from `str.json_decode`.** Status: `pl.Object`, `pl.Unknown` and `pl.Binary` are refused (D-0230, D-0259). What is left (RAN: `c_json_decode_panics.py`, 30 allowed dtype names, 10 small JSON texts each, one subprocess per dtype): `pl.Array(pl.Int64, 2)` panics on all 10 texts with "Deserialization from JSON not implemented for FixedSizeList". Every other dtype ends in a normal Polars error or a result (125 results, 131 `ComputeError`, 5 `InvalidOperationError`, 9 panics, all 9 from `pl.Array`). The names `pl.BaseExtension`, `pl.DataType` and `pl.Extension` cannot be built as a type (a plain error, not a panic). So the D-0259 reading "`pl.Array(pl.Unknown, n)` panics" is wider: any `pl.Array` panics here.
- Option a: refuse `pl.Array` when it is the argument of `json_decode` (a rule on one member).
- Option b: refuse the name `pl.Array` in formulas (`cast(pl.Array(...))` is then also refused; I did not test whether `cast` to an array works).
- Option c: catch the panic (D-0230 decided: no catching for now).
- Option d: leave it. A panic stops the calculation (`BaseException` is not caught at `polars_calls.py:199`).
- Not known: other members that panic. I scanned only `json_decode`.

**C3. New, not in the earlier report.** Short questions for Eve:
- The exponent limit (`MAX_EXPONENT = 100`) has no test (A4). Add a test? (It only needs one line.)
- A constant power grows without a limit across levels (line 111; 3 levels 0.32 s, a fourth is minutes). Leave, or limit the size of a constant calculation?
- `hash()` changes between Polars versions. Leave it allowed (the Polars version is recorded in the golden baseline, READ `golden_baseline.py` header), refuse it, or state it in the help text of the member?
- A Python method on a number, text, list or dictionary (lines 101 to 105) is accepted today and harmless today. Leave it, or refuse it (D does, today's check does not)?

# Found outside the task (reported, not fixed)

1. A `select` of one column on top of a plan with `unique(maintain_order=True)` returns the rows in a different order at each collect, because the optimizer turns `maintain_order` off (RAN: `a2b_order_probe.py`, 10 collects, 10 hashes; the optimized plan `a2b_plan_optimized.txt`). The app's whole-table path is stable. It matters for any code that selects columns on top of such a plan. The plan that shows it is in `a2b_plan.txt` (a `UNIQUE[maintain_order: true]` under the first step of `Summary_phenotype_length_fragmentation_assembly.yaml`); I did not find which recipe step writes that `UNIQUE`.
2. The 14 files / 16 lines count of the review session: 13 files / 16 lines for the demo recipe; one more file in the folder (`ResFinder_Abromics_wrangling.yaml`) is included by no recipe (A1).
3. The exponent limit and the underscore rule are not pinned by any test (A4).
4. `hash()` values change between Polars versions (A4, READ).

# What I did not run or could not

- Option D was not run through the app's UI (no browser test, as the brief says). It was run through the engine (orchestrator, wrangler, VizFactory) for 11 recipes.
- The fourth level of the constant-power line (111) and the three size lines (45, 46, 51): not built or run (memory and time).
- The 4 formula lines that no recipe runs (3 in the orphan file, 1 in the template): plan equality only.
- The full suite, the browser tests, any pickled or native-library payload: not run, by the brief.
- Formulas in `.md`/`.qmd` documents: not scanned. Formulas built by code in the tests (for example by a loop over all members): only the string constants of the sources were collected.
- Polars panics other than `json_decode`: not searched.
- `inspect` and other members dangerous by effect: not searched again; the list was not re-read member by member.

# Trial commits (branch `trial/formula-d`, worktree `.claude/worktrees/formula-d`, not pushed, not merged)

- `fb0a59e7` feat(formula): trial of option D, build a formula without eval (study only, not for merge): `libs/utils/src/utils/formula_build.py`, `libs/utils/tests/test_formula_build.py`.
- `bd1697cb` test(formula): trial of option D, add the 54 refused hostile lines and a recursion guard.
