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

