# Can a plot function be written the Polars way? Trial and report

Date: 2026-11-18. Trial branch: `trial/stat-function-polars` (worktree `.claude/worktrees/stat-function-polars`), from `dev` `372e390e`. Nothing is merged. Eve decides.
Asked in channel M272 (sparmvet-viz-57): Eve, "I still do not understand why we cannot do as in polars"; "we should be able to have a way to match the polars behavior".
Labels: **run** = I ran it here. **read** = I read it at file:line. **not run** = deliberately not run.
Versions: Polars 1.40.1, plotnine 0.15.4, numpy 2.4.4, Python 3.14.10.

## The answer in three sentences

Yes, we can: `fun: pl.col("x").sqrt()` works, is checked by the existing formula check (no second grammar), and draws the same picture as the lambda in every case I compared (50 of 50 pictures identical, pixel by pixel).
It costs about 140 lines of new code and, when the lambda form is deleted, removes about 230 lines of lambda grammar and about 320 lines of its tests. But it opens the plot text to the whole formula allow-list (including two heavy-memory members that D-0064 already accepted for recipe formulas), and it needs a few small decisions from you (section 13).
It also fixes a real defect of today's way: a lambda such as `lambda x: 1 / x` over a range that crosses 0, or `lambda x: np.log(x)` over negative x, stops the drawing with "plotnine could not draw it (KeyError: '__import__')".

## What the recipe author writes and sees

Today (lambda text, own grammar):
```yaml
- name: stat_function
  params:
    fun: "lambda x: x * 2"
    xlim: [1, 5]
```
Way 1 (Polars text over the column `x`, the same grammar as a recipe formula):
```yaml
- name: stat_function
  params:
    fun: 'pl.col("x") * 2'
    xlim: [1, 5]
```
What the app does with it (run): plotnine's x numbers go into a table with one column `x` (decimal numbers). The recipe text is checked by `formula_problems` (the same function that checks `polars_with_columns`). The checked expression runs once on the table. The column comes back as numbers.
Where the check lives (read): `libs/utils/src/utils/formula_check.py`. `libs/viz_factory` may import `libs/utils`, and it already does (`geoms/core.py`: `from utils.formula_check import ...`; `libs/viz_factory/pyproject.toml:14` declares `utils`). So the plot library reaches the check today, with no new import across libraries.

## What I built on the trial branch (committed, readable later)

| File | What |
|---|---|
| `libs/utils/src/utils/formula_check.py` | `function_string_problems` hands a text that is not a lambda and not a bare math name to `formula_problems` (the existing check). Adds only one rule: `pl.col("<name>")` must name `x`. New helper `is_polars_function`. |
| `libs/viz_factory/src/viz_factory/geoms/polars_function.py` (new, 106 lines) | `PolarsPlotFunction`: a `np.vectorize` subclass. plotnine calls a function one number at a time, except for a `np.ufunc` or `np.vectorize`, which it calls once with all numbers (`stats/stat_function.py`, `compute_group`). So one Polars call computes the whole curve. |
| `libs/viz_factory/src/viz_factory/geoms/core.py` | 4 lines: the Polars text goes to `PolarsPlotFunction`, the lambda stays on its old path (trial only: the two are side by side to compare). |
| `libs/viz_factory/src/viz_factory/checked_plot.py` | 7 lines: a `CannotAct` raised while plotnine draws now names the plot and the layer. |
| `libs/viz_factory/src/viz_factory/geoms/named_functions.py` (new) | Way 2 prototype: `normal`, `line`, `logistic`, `exponential` with `args`. |
| `libs/viz_factory/tests/test_stat_function_polars_trial.py` (new) | 59 tests, all pass. |
| `libs/utils/tests/test_plot_text_check.py` | One existing assertion adapted: it counted the number of problem entries for one hostile text (1 before, 2 now, because the formula check lists every problem). Three Polars assertions added. |

Commits: `abe78a8a`, `6f9b9def`. Test run (run): the files that name `stat_function`, the formula check and the plot text check, plus the yaml-example, registry, one-error-form and no-silent-error tests: 1771 passed, 9 xfailed, 1 failed (the count assertion described above); after I adapted that assertion, `test_plot_text_check.py` gives 208 passed. Not the full suite.
Break test (run): I broke the code three times and saw tests fail each time (check skipped: 20 fail; probe for values that depend on other points removed: 4 fail; naming of draw-time errors removed: 1 fails). Restored, 59 pass.

## 1. The shipped examples: both ways drawn and compared pixel by pixel

Every `fun` text in the repository (run, grep over everything outside `tmpAI`, `.git`, `.claude/logs`):

| Where | Text | Polars way | Result |
|---|---|---|---|
| `libs/viz_factory/tests/test_data/stat_function_test.yaml` (the ONLY recipe file with a `fun`; no gallery bundle, no `config/` recipe has one) | `lambda x: x * 2` | `pl.col("x") * 2` | 0 pixels differ (through `VizFactory.render`, `xlim [1,5]`, the real test data) |
| registry `yaml_example` of `stat_function` (`geoms/core.py`) | `lambda x: 2 * x` | `2 * pl.col("x")` | 0 pixels differ |
| `assets/scripts/debug_bootstrap_viz_yamls.py:123` | `lambda x: x**2` | `pl.col("x") ** 2` | 0 pixels differ. But see "found beside" below: that script's recipe cannot draw today. |
| tests and docs texts | `sin`, `2 * x ** 2 + 1`, `np.sqrt(x) + math.pi`, `np.log10(x)`, normal density, logistic, `np.floor(x)` | each rewritten | 0 pixels differ |

Each pair was drawn in five ways: plain with `xlim`; no `xlim` (range from the data); `n=11`; `facet_wrap` by a column (3 panels); coloured by a column (3 groups). 10 pairs x 5 ways = **50 of 50 pictures identical to the byte** (PNG, 100 dpi, `tmpAI/trial/e5_pixels.py`).
Control (run): `x * 2` against `x * 2.01` differs in 16458 pixels (5.4 percent); a plot with and without the curve differs in 38277 pixels. So the comparison can fail.
Found beside: `debug_bootstrap_viz_yamls.py` writes `geom_line` with `stat: stat_function` and a `fun` text; drawing it gives "stat_function requires parameter 'fun' to be a function" (run). It is a defect of that script, with or without this trial.

## 2. Every old name: does a Polars way exist, and does the formula check accept it?

The old list `MATH_FUNCTIONS` has 18 names (`formula_check.py:68-72`): sin cos tan arcsin arccos arctan sinh cosh tanh exp log log10 log2 sqrt abs floor ceil sign. The old modules: `np`, `numpy` (the same 18 names) and `math` (Python's own names: `asin`, `fabs`, ...), plus constants `pi` and `e`.
**All 18 old names exist as Polars methods and are accepted by the existing formula check.** The `math.` names too. The table adds the things you asked for. "In the old lambda list" = whether the old text I wrote for the same thing was accepted by the OLD check. Differences are against the real old path (the lambda evaluated number by number), over a grid of 2001 points (the domain suits each function).

| What | Polars way | In Polars 1.40.1 | Accepted by the formula check | In the old lambda list | Max difference to the old way (absolute / relative) |
|---|---|---|---|---|---|
| sin | `pl.col("x").sin()` | yes | yes | yes | identical to the last bit |
| cos | `pl.col("x").cos()` | yes | yes | yes | identical to the last bit |
| tan | `pl.col("x").tan()` | yes | yes | yes | identical to the last bit |
| arcsin | `pl.col("x").arcsin()` | yes | yes | yes | identical to the last bit |
| arccos | `pl.col("x").arccos()` | yes | yes | yes | identical to the last bit |
| arctan | `pl.col("x").arctan()` | yes | yes | yes | identical to the last bit |
| sinh | `pl.col("x").sinh()` | yes | yes | yes | identical to the last bit |
| cosh | `pl.col("x").cosh()` | yes | yes | yes | identical to the last bit |
| tanh | `pl.col("x").tanh()` | yes | yes | yes | 1.1e-16 / 2.8e-16 |
| exp | `pl.col("x").exp()` | yes | yes | yes | identical to the last bit |
| log (natural) | `pl.col("x").log()` | yes | yes | yes | identical to the last bit |
| log10 | `pl.col("x").log10()` | yes | yes | yes | 4.4e-16 / 4.1e-16 |
| log2 | `pl.col("x").log(2)` | yes | yes | yes | 8.9e-16 / 2.2e-16 |
| log with a base (math.log(x, 10)) | `pl.col("x").log(10)` | yes | yes | yes | identical to the last bit |
| sqrt | `pl.col("x").sqrt()` | yes | yes | yes | identical to the last bit |
| abs | `pl.col("x").abs()` | yes | yes | yes | identical to the last bit |
| floor | `pl.col("x").floor()` | yes | yes | yes | identical to the last bit |
| ceil | `pl.col("x").ceil()` | yes | yes | yes | identical to the last bit |
| sign | `pl.col("x").sign()` | yes | yes | yes | identical to the last bit |
| math names: asin | `pl.col("x").arcsin()` | yes | yes | yes | identical to the last bit |
| math names: fabs | `pl.col("x").abs()` | yes | yes | yes | identical to the last bit |
| round (0 decimals), np.round | `pl.col("x").round(0)` | yes | yes | no | identical to the last bit |
| round half cases (-2.5..2.5 by 0.5) | `pl.col("x").round(0)` | yes | yes | no | identical to the last bit |
| arctan2(x, 2) | `pl.arctan2(pl.col("x"), 2)` | no | no | no | not compared |
| arctan2 method on Expr | `pl.col("x").arctan2(2)` | no | no | no | not compared |
| log1p | `pl.col("x").log1p()` | yes | yes | no | identical to the last bit |
| power, non-integer exponent 1.5 | `pl.col("x") ** 1.5` | yes | yes | yes | identical to the last bit |
| power 1.5 of negative x | `pl.col("x") ** 1.5` | yes | yes | yes | identical to the last bit |
| power, integer exponent 3 | `pl.col("x") ** 3` | yes | yes | yes | 1.4e-14 / 2.2e-16 |
| power, negative exponent -2 | `pl.col("x") ** -2` | yes | no | no | not compared |
| power by method .pow(1.5) | `pl.col("x").pow(1.5)` | yes | yes | yes | identical to the last bit |
| power with x as exponent: 2 ** x | `pl.lit(2.0) ** pl.col("x")` | yes | no | no | not compared |
| power with x as exponent: pl.lit(2).pow(x) | `pl.lit(2.0).pow(pl.col("x"))` | yes | yes | no | identical to the last bit |
| clip (min and max against constants) | `pl.col("x").clip(-1, 1)` | yes | yes | no | identical to the last bit |
| min against a constant (min(x, 1)) | `pl.min_horizontal(pl.col("x"), 1)` | yes | yes | no | identical to the last bit |
| max against a constant (max(x, 0)) | `pl.max_horizontal(pl.col("x"), 0)` | yes | yes | no | identical to the last bit |
| max(x,0) by clip lower bound | `pl.col("x").clip(lower_bound=0)` | yes | yes | no | identical to the last bit |
| constant pi | `3.141592653589793 * pl.col("x")` | yes | yes | yes | identical to the last bit |
| constant e | `2.718281828459045 ** pl.col("x")` | yes | no | no | not compared |
| pi by pl.lit | `pl.lit(3.141592653589793) * pl.col("x")` | yes | yes | yes | identical to the last bit |
| condition (when/then/otherwise) | `pl.when(pl.col("x") < 0).then(0).otherwise(pl.col("x"))` | yes | yes | no | identical to the last bit |
| normal density, mean 0, sd 1 | `(-0.5 * pl.col("x") ** 2).exp() / 2.5066282746310002` | yes | yes | yes | 5.6e-17 / 2.2e-16 |
| normal density, mean 1, sd 2 | `(-0.5 * ((pl.col("x") - 1) / 2) ** 2).exp() / (2 * 2.5066282746310002)` | yes | yes | yes | 2.8e-17 / 3.7e-16 |
| logistic 1/(1+exp(-x)) | `1 / (1 + (-pl.col("x")).exp())` | yes | yes | yes | identical to the last bit |
| cbrt (new in Polars) | `pl.col("x").cbrt()` | yes | yes | no | 4.4e-16 / 4.3e-16 |
| degrees | `pl.col("x").degrees()` | yes | yes | no | identical to the last bit |
| radians | `pl.col("x").radians()` | yes | yes | no | identical to the last bit |
| arcsinh | `pl.col("x").arcsinh()` | yes | yes | no | 4.4e-16 / 2.3e-16 |
| arctan2 with pl.lit second argument | `pl.arctan2(pl.col("x"), pl.lit(2))` | yes | no | no | not compared |
| power, negative exponent by .pow(-2) | `pl.col("x").pow(-2)` | yes | yes | no | identical to the last bit |
| power, negative exponent by 1 / x ** 2 | `1 / pl.col("x") ** 2` | yes | yes | no | 1.8e-12 / 2.2e-16 |
| e ** x by .exp() | `pl.col("x").exp()` | yes | yes | no | 5.7e-14 / 4.4e-16 |
| modulo x % 2 | `pl.col("x") % 2` | yes | yes | yes | identical to the last bit |
| floor division x // 2 | `pl.col("x") // 2` | yes | yes | yes | identical to the last bit |

Summary of the table (run, `tmpAI/trial/e2_table.py`, data in `evidence/e2_table.json`):
- 54 texts tried. 52 exist in Polars 1.40.1. 48 are accepted by the existing formula check. 6 are not accepted (gaps below).
- 48 compared with the old way: 38 identical to the last bit; the other 10 differ by at most 4.4e-16 relative (1.8e-12 absolute, for values near 1e4). Where the numbers are not finite, the pattern of NaN and infinity is the same in all 48.
- `round`: Polars `round(0)` and `np.round` agree on the half cases (-2.5 to 2.5 by 0.5): both round half to even.
- Gaps of the allow-list (the check refuses a harmless thing; I did NOT widen it):
  1. `pl.arctan2(y, x)` exists in Polars but is not on `MODULE_FUNCTIONS`. There is no `Expr.arctan2`. So arctan2 is not possible. The old way had no arctan2 either.
  2. `** -2` (a negative exponent) is refused: the exponent rule wants a plain constant, and `-2` is a unary minus on 2 (`formula_check.py`, `visit_BinOp`). The same refusal exists for recipe formulas today. Workarounds that pass: `.pow(-2)` or `1 / pl.col("x") ** 2`.
  3. `** pl.col("x")` (the variable as exponent) is refused by the same rule. `pl.lit(2.0).pow(pl.col("x"))` passes. So `.pow` skips a rule that `**` has. That is an inconsistency of the check, found here, not caused by the trial.
  4. No `pi` and `e` names. The author writes the numbers: `3.141592653589793 * pl.col("x")`. `e ** x` is `pl.col("x").exp()`. `pl.lit(math.pi)` is not possible (no `math` in a formula). The old way had `pi`, `e`, `np.pi`.

## 3. Numbers at the edges, against the old way (run, `e3_edges.py`)

The old way runs the lambda with empty builtins. A numpy warning (log of a negative number, division by zero, overflow) needs `__import__`, so it raises `KeyError: '__import__'`. This is a defect of today's way (it is also the "stops with an error that does not say what is wrong" of question 12).

| Case | Old way | Way 1 |
|---|---|---|
| log of -1, 0, 1 (`np.log`) | error `KeyError: '__import__'` at -1 and 0; 0 at 1 | NaN, -inf, 0 (the same values as Polars gives); the trial leaves non-finite points out (gap), as decided in question 12 |
| `math.log` of -1, 0 | `ValueError: expected a positive input` (and the message blames `xlim`: "the value [-1, 1] for 'xlim' is refused") | NaN, -inf (gap) |
| `1 / x` at 0 | `KeyError: '__import__'` | inf, left out (gap) |
| `x / 0` | `KeyError: '__import__'` for all x | -inf, NaN, inf, left out |
| sqrt of -1 | `KeyError: '__import__'` | NaN (gap) |
| `exp(1000)`, `x ** 100` at 1e4 | `KeyError: '__import__'` | inf (gap) |
| NaN in x | NaN | NaN |
| inf in x, `sin` | `KeyError: '__import__'` | NaN |
| bare name `log` (numpy ufunc) over -1..1 | draws; plotnine says "Removed 50 rows containing missing values" (a Python warning the user does not see) | draws; "Removed 51 rows" (the same kind, also not visible) |
| null (from `pl.when(...).otherwise(None)`) | not possible in a lambda | null becomes NaN, a gap |
| constant function (`pl.lit(2)` or `2`) | `lambda x: 2` gives 2.0 each | 2.0 each; a horizontal line (a result of one value is repeated for every point, as `with_columns` does) |
| integer input `[3,5,7]`, `x // 2` | 1, 2, 3 | 1, 2, 3 |
| integer input `x ** 100` at 10 and 20 | 0.0, 0.0 (numpy int overflow, silent) | 1e100, 1.27e130 |

Integer or decimal x: plotnine always hands decimal numbers (`np.linspace`), so an integer column does not occur in a real plot. The trial still casts x to Float64, because Polars on an `Int64` column does integer work: `x ** 100` wraps around to negative numbers, `x // 2` stays an integer (run, `Int64` column `[3,5,7,10]`). With the cast there is nothing to know about integer overflow.
A date axis: a `stat_function` on a date x axis fails in both ways with a plotnine message that does not say why (run, `e10_date.py`). Same today, not caused by the trial.

What the trial does NOT do: the visible warning of question 12 ("2 of 101 points were left out at x = 0"). The function counts the non-finite points (`PolarsPlotFunction.non_finite`); the place that shows them to the user is the Q12 task.

### Results that are not a column of numbers (run, `e4_messages.py`)

| Result of the expression | What happens |
|---|---|
| one value (`pl.lit(2)`, `2`) | repeated for every point (a constant curve) |
| a different length (`head(3)`, `filter(...)`) | refused: "gives 3 values for 6 points" |
| true/false (`pl.col("x") > 1`) | refused: "gives Boolean, a curve needs numbers" |
| text | refused: "gives String, a curve needs numbers" |
| several columns | cannot be produced: the table has one column; `pl.col("x", "x")` gives one column (Polars drops the duplicate). The check "gives N columns" is in the code and not reachable. |
| no column (`pl.col(pl.Int64)`, the table is decimal) | refused: "selects no column" |
| a value that depends on the other points (`pl.col("x") - pl.col("x").mean()`, `cum_sum`, `shift`, `pl.len()`, `shuffle()`) | refused at build time (see 4, point 5) |

## 4. What the user reads (exact texts, run, through `VizFactory.render`, plot named `my_plot`)

Plot and layer are named (D-0050). Each text ends with "Fix:" or "Suggestion:".

- Refused name: `Plot 'my_plot', layer 2 (stat_function): the function string is refused: pl.read_csv is not allowed. Suggestion: use one of: all, all_horizontal, any, ... when.`
- Refused method that takes a function: `... map_elements runs a Python function and is not allowed; the function string is refused: Lambda is not allowed in a formula. Suggestion: build the column with pl.col, pl.lit, pl.when and the Polars expression methods.`
- Unknown method: `... sqroot is not an expression method. Suggestion: build the column with ...`
- Syntax error: `... the formula is not a valid expression (SyntaxError). Suggestion: write one Python expression.`
- Wrong column name `pl.col("y")`: `... a plot function has one column, 'x', not 'y'. Suggestion: write pl.col('x').` (found at the recipe check too, code PS06: `layer_text_problems` gives `('fun', "the function string is refused: a plot function has one column, 'x', not 'y'", "Suggestion: write pl.col('x')")`)
- Non-numeric result: `Plot 'my_plot', layer 2 (stat_function): the function 'pl.col("x") > 1' gives Boolean, a curve needs numbers. Fix: write an expression that gives numbers; a condition can be turned into numbers with pl.when(...).then(1).otherwise(0).`
- Other length: `... gives 3 values for 6 points. Fix: write an expression that gives one value for each x, for example pl.col('x') * 2.`
- Depends on the other points: `... gives a value that depends on the other points (for example a sum, a mean, a shift, a running total or a count), so the curve would change with the number of points. Fix: write an expression where each value depends on its own x only, for example pl.col('x') ** 2.`
- Polars' own error: `... could not be computed (SchemaError: invalid series dtype: expected `String`, got `f64` for series with name `x`). Fix: check the expression with the Polars documentation; it works on the column x.`
- An error that appears only for big x, at the drawing (`pl.col("x").cast(pl.Int8)`, xlim 0..1000): `Plot 'my_plot', layer 2 (stat_function): the function '...' could not be computed (InvalidOperationError: conversion from `f64` to `i8` failed in column 'x' for 88 out of 101 values: [130.0, 140.0, ... 220.0]). Fix: ...` Without my 7-line change in `checked_plot.py` this text came without the plot and layer (run: it did).
- `args` given: `... was given arguments (args). Fix: write the numbers inside the expression, for example pl.col('x') * 2 + 1.`

Today's texts for comparison (run): `1 / x` crossing 0 gives `Plot 'my_plot': plotnine could not draw it (KeyError: '__import__'). Fix: check the mapping and the layers of this plot against the plotnine documentation.` (no layer, no cause). A refused lambda text can give two problems for one name, for example `np.load('a')` also complains about the constant 'a'.
One wording point: the check's own messages list up to 38 names ("use one of: all, all_horizontal, ...") and refer to "a formula" ("Lambda is not allowed in a formula"). For a plot function that reads long. It is the same text as for recipe formulas. A short plot-specific wording is possible; not done.

## 5. Speed (run, `e6_speed.py`, a machine that was busy: whole-plot times swing by 200 ms)

plotnine's default number of points is `n = 101` (`stats/stat_function.py`, `DEFAULT_PARAMS`). It evaluates once per panel (and group): a plot with 12 panels called the Polars function 12 times (run).

| n points | Old way: one call per number, as plotnine does | Way 1: one Polars call | |
|---|---|---|---|
| 101 | 0.20 ms | 0.98 ms | the Polars call has a fixed cost of about 1 ms |
| 1001 | 1.96 ms | 1.02 ms | |
| 10001 | 18.6 ms | 1.5 ms | |

A naive version that calls Polars once per number (what plotnine would do with a plain function) costs 94 ms for 101 points: that is why the trial uses the `np.vectorize` subclass. This relies on a plotnine detail (`isinstance(fun, (np.ufunc, np.vectorize))` at `stat_function.py`). If plotnine drops it, the function still works but 100 times slower (about 94 ms per panel); a test of `draw_calls == 3` for 3 panels would catch it.
The build-time check and the probe (see 6) cost 3.9 ms per layer, once per render. A whole plot (render and draw) takes 200 to 450 ms here; the difference between the two ways is inside that noise. Speed is not a reason for or against.

## 6. `args`, the parameters of a function

plotnine's `args` passes extra arguments to the function (`old_fun(x, *args)` or `**args`). Today a recipe cannot use it with a text function: a lambda must take exactly one argument (`lambda x, k: x * k` is refused: "the lambda must take exactly one plain argument"), and `fun: sin` with `args: [2]` fails inside numpy ("return arrays must be of ArrayType"), with `args: {k: 2}` "sin() got an unexpected keyword argument 'k'" (run, `e8_args.py`). So today `args` does not work for a recipe at all, and nothing is lost.
Way 1: the parameters are numbers in the expression: `(-0.5 * ((pl.col("x") - 1) / 2) ** 2).exp() / (2 * 2.5066282746310002)` is a normal curve with mean 1, sd 2. The trial refuses `args` with the sentence above. What is lost: one place to change a parameter (it sits inside the text), and the names `mean` and `sd`. Way 2 keeps names (below).

## 7. Safety: the Polars rule covers the new path fully (run, `e7_safety.py` and the test file)

- I ran the 60 harmless probes of the formula safety report (attribute access, dunder names, imports, calls outside the list, `map_elements`, `map_batches`, `pipe`, file reads, `scan_*`, SQL, `deserialize`, `meta.serialize`, `inspect`, `register_plugin`, comprehensions and the rest) through `function_string_problems` and through `PolarsPlotFunction(...)`. **52 refused, 8 accepted, 0 differences from `formula_problems`** (same decisions as the recipe formula check). I patched `builtins.eval` with a recorder: **0 of the refused texts reached `eval`**. Also in the test file, for 19 of them.
- The 8 accepted are the ones the report already lists as accepted: `bin.decode('hex')`, `pl.lit('/etc/passwd')` (just a text value), `repeat_by(10**12)`, `pl.lit('a') * 10**9`, `str.pad_start(4000000000)`, `shuffle()`, `sample(n=3)`, `list.eval(pl.element())`. I constructed only the harmless ones. I did **not run** the three allocation probes (`repeat_by`, `pad_start`, `pl.lit('a') * 10**9`): on the plot path they would run at build time on 6 rows and at the drawing on 101 rows. `shuffle` and `sample` are stopped in practice by the "depends on other points" probe (a permutation of six numbers differs from six single numbers), but that is a net, not a proof.
- `evaluate_formula` checks again before it runs (read: `formula_check.py`, `evaluate_formula` calls `formula_problems` and raises `FormulaError`), so skipping the plot check does not open the door. (Break test 1 skipped the plot check: the tests that assert the check failed, 20 of them.)
- No `lambda` and no free `eval` on the new path. The one `eval` is the one in `evaluate_formula`: the checked text, empty builtins, only the name `pl`. It is the one that recipe formulas use. In the trial the old `eval` of the lambda form is still in `_function_from_string` (for the comparison); adopting way 1 deletes it, so the plot text has one `eval` site shared with the recipe formulas instead of two.
- **What gets worse**: the plot text now reaches 38 module functions and about 200 `Expr` members instead of 18 maths names, and with them the known holes D-0064 accepted for recipe formulas (large allocations; the `str.json_decode` panics are refused for `pl.Object` by D-0230, and for `pl.Unknown`, `pl.Binary` and arrays of unknown as you decided in M273). In the old grammar `np.ones(10 ** 12)` was refused. This is the main cost of way 1. D-0064 says "no time or size limit now" and "re-evaluated at the end".

## 8. The other ways

### Way 2: a small set of named curves with parameters (prototype, run)
`fun: normal` with `args: {mean: 2, sd: 0.8}`. `libs/viz_factory/src/viz_factory/geoms/named_functions.py`: 4 curves (`normal`, `line`, `logistic`, `exponential`), about 55 lines. No text is evaluated. plotnine's own `args` carries the parameters.
Run: the `normal` curve with mean 2 and sd 0.8 draws the same picture as its lambda (0 pixels differ), the values are equal (max difference 0.0). Refusals in plain words: `sd` of 0 ("must be above 0"), an unknown parameter name ("has no parameter sdd"), a text instead of a number, an unknown curve name ("there is no curve named 'normall'. Fix: choose one of: ...").
Pros: nothing to evaluate, so nothing to attack; parameters have names; plain messages; very short recipes. Cons: a closed set: a curve that is not in the table cannot be drawn, so each request is a code change with a test and a help text; it does not "match Polars behaviour" (it is a different idea); it still needs a rule for the smoother. It is a good addition to way 1 for the most used curves, not a replacement.

### Way 3: keep the lambda, one prefix rule (your fallback B)
Run (`w3.py`): removing `numpy` from `PLOT_FUNCTION_MODULES` and from `_MATH_MODULES` makes `numpy.sqrt` refused in both places: for the plot function with the message "the module 'numpy' is not allowed. Suggestion: use math, np, for example np.sqrt(x)"; for the smoother with "the function 'numpy.sqrt' is not allowed in a smoother formula ... alone or as np.<name>". So B is two table entries, one custom sentence "write np", the removal of `numpy` from `checked_plot.plot_environment`, and the tests that use `numpy.` (about 10 lines).
Fact that B does not solve: `math` does not mean the same in the two places. In a plot function `math` is Python's `math` (names `asin`, `fabs`; one number at a time; `math.log(-1)` raises). In a smoother `math` is numpy (`checked_plot.py`, `plot_environment`: `"math": np`), so `math.sqrt(x)` works on a column. One prefix list with two meanings is one rule on paper only. To make it one rule, `math.` must be refused in one place or defined the same in both.
Pros: cheapest (a few lines). Cons: keeps the second grammar and its tables (about 230 lines plus tests), the crash on `1 / x`, and the `math` confusion. It does not give the Polars way.

### Way 4: anything else I found
- **4a. A computed column, no new component (works today).** A recipe step (`polars_with_columns`, same formula check) adds `fx = pl.col("x").sqrt()`, and the plot maps `y: fx` with `geom_line`. Run: draws. Limit: the curve exists only at the x values in the data (no smooth curve between points, nothing outside the data range). It is the right way for "values predicted for my samples", not for a theoretical curve over a range.
- **4b. A second table for the layer**: not possible today. A layer cannot take another table: `data: other_table` is refused by plotnine ("expected a dataframe or a mapping"), run. It would be a bigger design change (one table per layer).
- **4c. Pre-evaluating in an `xlim` grid table**: same as 4b.

## 9. The smoother formula (`geom_smooth`, `stat_smooth`, the quantile layers)

Fact: its `formula` is a patsy model formula, for example `y ~ x + I(x**2)` or `y ~ bs(x, df=4)`. The text has a `~`, with y on the left and the model on the right. A term can make several columns (a spline `bs(x, df=4)` makes 4; `C(g)` makes one per level; `x:z` is an interaction). patsy turns it into a design matrix for the fitting routine. Our checker has its own parser for it (`_FormulaParser`, `formula_check.py`), so there are now three grammars for text: the Polars formula, the lambda, and the smoother.
Why it cannot be Polars: a Polars expression gives one column from columns. It has no `~`, no spline bases, no factor coding and no interaction terms; the fitting routine needs the design matrix, not one column. A hybrid (patsy text with Polars inside `I(...)`) would be two languages in one text.
One rule for it under each way:
- Way 1: the plot function is Polars; the smoother stays patsy. Two languages remain, each with one rule. The prefix question disappears for `stat_function` (there is no prefix: methods like `.sqrt()`) and remains only for the smoother. Suggested rule for the smoother alone: bare names and `np.` only; `numpy.` and `math.` refused with "write np" (this is B, applied where the prefix still exists).
- Way 2: as way 1 for the smoother.
- Way 3 (B in both places): one prefix list `np`, `math` for both, but with the two meanings of `math` described above.

## 10. What changes for each way if it is adopted

| | Way 1 (Polars text) | Way 2 (named curves) | Way 3 (B) |
|---|---|---|---|
| Code | `formula_check.py`: remove `_FunctionChecker` and its constants (`PLOT_FUNCTION_MODULES`, `PLOT_FUNCTION_NAMES`, `PYTHON_MATH_FUNCTIONS`, `_PYTHON_MATH_NAME`, `_PLOT_FUNCTION_ARGUMENTS`), about 180 lines; keep `MATH_FUNCTIONS` and `MATH_CONSTANTS` only for the smoother. `geoms/core.py`: remove `function_string_namespace` and the lambda `eval` (about 47 lines), add the module of about 106 lines (already written). `checked_plot.py`: the 7 lines. | new module about 55 lines per 4 curves, a table, one entry in the check | 2 table entries, one message, `plot_environment`, about 10 test lines |
| Registry entry | `stat_function` `ui_schema`: label "Function as Python expression (e.g. 'lambda x: x**2')" becomes "Function as a Polars expression over the column x"; `description` ("a math function name or a lambda ... numpy maths only") and `yaml_example` (`fun: "lambda x: 2 * x"`) change. Blueprint form: the `fun` widget stays a string. `plotnine: modified` stays (the text form is a difference to plotnine). | label, `description`, `yaml_example`, a `args` help text per curve | none or the help text of the prefix |
| Checker (`recipe_check.py`) | does not know `fun` itself. `plot_text_check.py:161` (`layer_text_problems`, code PS06) calls `function_string_problems`. Nothing to change there; the docstring text changes. | the check must know the names of the curves and the parameters | no change |
| Shipped recipes to rewrite | exactly 1: `libs/viz_factory/tests/test_data/stat_function_test.yaml` (`fun`). Plus `assets/scripts/debug_bootstrap_viz_yamls.py:123` (already broken). No gallery bundle, no `config/` recipe, no template. | the same 1 | 0 |
| Tests | rewrite `libs/utils/tests/test_stat_function_names.py` (162 lines), `libs/viz_factory/tests/test_stat_function_names_drawn.py` (107), `test_stat_function_formula.py` (51); change the `lambda` cases of `test_formula_check.py` (16 lines), `test_formula_reads_no_outside_data.py` (18; the `np.load` probes become Polars probes), `test_recipe_check.py`, `test_plot_text_check.py`, `test_registry_audit_vs_plotnine.py`, `test_plot_text_runs_no_code.py` (1 each). The trial test file (59 tests) is the start. | new tests per curve | about 10 lines |
| Docs | `docs/workflows/visualisation_factory.qmd:91` (one line); spec section 15 (the owner's file); `rules_viz_factory.md` (hers to release); `dependency_index.md` regenerated | same | same |
| Pictures | identical (50 of 50) | identical for the normal curve (0 pixels) | identical |
| Decisions it touches | D-0030 (formulas from the allow-list: satisfied better), D-0064 (accepted holes: now also on the plot path), D-0232 (check and drawing agree: nothing left to disagree, one check) | D-0232 in a different way | D-0232 as it is |
| Effort tag | `[sonnet/medium]` | `[sonnet/medium]` | `[haiku/low]` to `[sonnet/low]` |

## 11. Options with pros and cons (one table)

| Option | For | Against |
|---|---|---|
| Way 1: Polars text (replaces the lambda) | One grammar for every formula in a recipe. What the author knows from the recipe steps works here. About 230 lines of code and 320 lines of tests less. Pictures identical. Fixes the crash on `1 / x` and the unreadable messages. More functions (`clip`, `round`, `when/then`, `log1p`, `cbrt`). Same edge behaviour as Polars (what you asked for). | The plot text reaches the whole allow-list and its known heavy-memory members (D-0064). `pi` and `e` must be numbers. Three small gaps in the allow-list (`arctan2`, negative and variable exponent) already exist for recipe formulas. A probe is needed so a curve does not depend on the number of points (a net, not a proof). One recipe and a few texts to rewrite. |
| Way 2: named curves | Safest. Short. Named parameters. | Closed set. Not Polars. More code to keep per curve. |
| Way 3: B (`np.` and `math.` only) | Cheapest. | Keeps the lambda grammar, its crash on `1 / x`, and `math` with two meanings. Does not match Polars. |
| Way 4a: a computed column | Works today, no code. | Only at the data's own x values. |
| Do nothing (question 10 default A) | Nothing to do. | The crash on `1 / x` and `log(x)`; two languages for formulas; `numpy.` and `np.` both. |

## 12. Recommendation (one, marked)

**RECOMMENDATION: way 1 (Polars text replaces the lambda form), in one step, with the lambda form deleted at the same time (principle 4: one way, no shim), and way 2 only later for curves that scientists ask for often (the normal curve).** Apply the "write np" rule to the smoother formula alone.
Reason: it is the only option that gives what you asked for, the same behaviour as Polars, and the evidence says it costs little: identical pictures, the same check as recipe formulas, fewer lines. The price is the wider text surface (item 5 below), which is a risk you already accepted for recipe formulas in D-0064.

## 13. What nothing decides (for Eve): plain questions, with defaults

1. **Replace the lambda form by the Polars form?** Both together would be two ways to write one thing. Default: replace, in one step, rewrite the one recipe file, delete the lambda grammar. If you say no, the trial stays unmerged.
2. **A curve that depends on the other points** (`pl.col("x") - pl.col("x").mean()`, `shift`, `cum_sum`, `pl.len()`): the curve would change with the number of points or the range. Refuse it (what the trial does) or allow it with a warning? Default: refuse, with the sentence in section 4. The probe is a net: an expression that depends on the others only for large values would pass it.
3. **`pi` and `e`**: write the numbers (3.141592653589793, 2.718281828459045) and `.exp()`, or add a name? Default: write the numbers, say so in the help text; no new name.
4. **Gaps of the allow-list** (`pl.arctan2`, `** -2`, `** pl.col("x")`; they exist today for recipe formulas too): widen the allow-list or leave? I changed nothing. Default: leave, list them in the help text with the workarounds (`.pow(-2)`). Adding `arctan2` is one entry, with its reason.
5. **The plot text now reaches the heavy-memory members** (`repeat_by(10**12)`, `pad_start(4000000000)`, `pl.lit('a') * 10**9`), the same as recipe formulas under D-0064. Accept as decided there, or give the plot text a stricter rule (for example a time or size limit)? Default: accept as D-0064, re-evaluate at the end.
6. **Visible warning for left-out points** (question 12, A2): the function counts them. The place that shows the warning is that task. Same warning for the lambda and the Polars form while both exist. Default: as decided.
7. **The smoother formula rule**: bare names and `np.` only; `numpy.` and `math.` refused with "write np". Default: yes, for the smoother alone. This closes question 10 for `stat_function` (no prefix any more) and keeps it only for the smoother.
8. **Date axis**: `stat_function` on a date x axis fails today and with way 1, with a message that does not say why. Fix later? Default: later.

## 14. What I ran and what I only read

Ran: all scripts in `evidence/` (copies of `tmpAI/trial/` of the worktree), the 59 trial tests, the existing tests listed above, three break tests.
Read only: `stat_function.py` of plotnine, `formula_check.py`, `plot_text_check.py`, `checked_plot.py`, `errors.py`, `viz_factory.py`, the channel block M272 and M274, question 10, the ledger lines D-0030, D-0064, D-0230, D-0232, D-0257, the formula safety report.
Not run: the memory probes (`repeat_by(10**12)`, `pad_start(4000000000)`, `pl.lit('a') * 10**9`); any payload (no pickle, no native library); the full test suite; the browser tests; the app.
Not touched: `pyproject.toml`, pytest configuration, CI, settings, `CLAUDE.md`, rule files, ADR text, the spec.
Open points the trial found that are not part of the choice: (a) the lambda path crashes with `KeyError: '__import__'` on any numpy warning (real, today, run); (b) `math.log` of a negative number blames `xlim` in its message (run); (c) `debug_bootstrap_viz_yamls.py` writes a `stat_function` recipe that cannot draw (run); (d) `.pow` skips the exponent rule that `**` has (run).

## 15. Trial commits

- `abe78a8a` feat(viz_factory): trial of a stat_function written as a Polars expression (not decided)
- `6f9b9def` feat(viz_factory): trial leaves non-finite curve points out as a gap (question 12)
Branch `trial/stat-function-polars`. Evidence and scripts: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/stat_function_polars/evidence/`.
