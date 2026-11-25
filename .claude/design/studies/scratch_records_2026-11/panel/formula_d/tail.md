
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

1. A `select` of one column on top of a plan with `unique(maintain_order=True)` returns the rows in a different order at each collect, because the optimizer turns `maintain_order` off (RAN: `a2b_order_probe.py`, 10 collects, 10 hashes; the optimized plan `a2b_plan_optimized.txt`). The app's whole-table path is stable. It matters for any code that selects columns on top of such a plan. The recipe step is `polars_unique`/the `unique` inside `Summary` of the demo recipe (`Summary_phenotype_length_fragmentation_assembly` receives it).
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
