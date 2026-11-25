# N28: stat_summary and functions as parameters (investigation, 2026-11-16)

Nothing was built or changed. **RUN** = I ran it (plotnine 0.15.4, pandas 3.0.2, numpy 2.4.4, scipy 1.17.1, Polars 1.40.1). **READ** = read in code or records. Scripts and outputs: `tmpAI/panel/round7/s2_2/` (`c_compare.py`, `c_named.py`, `d_params.py` with `.out` files). I start from `.claude/design/viz_rename_impact_2026-11-15.md` section 4 and do not repeat it.

Words used once: "summary" = one row per group with a centre and two ends of a bar. "Seed" = the number that makes random draws repeat. `fun_data` = a NAME of a summary that plotnine knows. `fun_y`, `fun_ymin`, `fun_ymax` = three Python functions (centre, lower end, upper end).

## A. One example on shipped data

Data (RUN): the ST22 recipe `1_test_data_ST22_dummy`, the shipped join `QA_population_zscore` (sample, country, `n50`: 42 samples; no missing `n50`). Groups: Norway 28, France 4, Germany 10 samples. I added, in a copy, one join written as recipe steps (`polars_group_by` on country, mean, standard deviation, count; then standard error and ends). The shipped files are unchanged.

### A.1 Three ways, numbers (RUN)

**(1) Recipe steps, drawn with `geom_point` + `geom_errorbar`.** The table that the user can read and export:

| country | n | mean | sd (n-1) | se = sd/sqrt(n) | ymin = mean - se | ymax = mean + se |
|---|---|---|---|---|---|---|
| Norway | 28 | 328189.79 | 120527.26 | 22777.51 | 305412.27 | 350967.30 |
| France | 4 | 276857.75 | 125016.90 | 62508.45 | 214349.30 | 339366.20 |
| Germany | 10 | 266014.50 | 96254.76 | 30438.43 | 235576.07 | 296452.93 |

**(2) `stat_summary` with a named `fun_data`** (through the plot factory; the plot's own numbers read back):

| fun_data | Norway (ymin to ymax) | France | Germany | Exact or random |
|---|---|---|---|---|
| `mean_se` | 305822.71 to 350556.86 | 222723.84 to 330991.66 | 237138.07 to 294890.93 | exact, no random numbers |
| `mean_cl_normal` | 281454.19 to 374925.38 | 77927.96 to 475787.54 | 197157.99 to 334871.01 | exact (t distribution) |
| `mean_sdl` (mean +/- 2 sd) | 87135.26 to 569244.31 | 26823.95 to 526891.55 | 73504.98 to 458524.02 | exact |
| `median_hilow` | 138941.70 to 508652.63 (centre 333052) | 170783.00 to 427015.63 | 140495.33 to 381323.55 | exact |
| `mean_cl_boot` (plotnine's DEFAULT when no `fun_data` is written) | 285368.9 to 369561.5 | 177226.0 to 376489.5 | 206556.4 to 322358.0 | RANDOM: needs the seed |

**(3) `fun_y`, `fun_ymin`, `fun_ymax`** (mean, minimum, maximum). Direct plotnine with Python functions (RUN): Norway 328189.8 [131595 to 512760], France 276857.8 [169646 to 435932], Germany 266014.5 [136671 to 384465]. A recipe cannot write it: `fun_y: mean` gives `'mean' is not a callable object` (RUN, shown with layer and parameter).

### A.2 Do (1) and (2) agree? NO, by default (RUN)

The centre agrees exactly. The ends do not:

| | Norway | France | Germany |
|---|---|---|---|
| half-width in (1) (se with n-1) | 22777.51 | 62508.45 | 30438.43 |
| half-width in (2) `mean_se` | 22367.07 | 54133.91 | 28876.43 |
| ratio (2)/(1) | 0.98198 | 0.86603 | 0.94868 |
| sqrt((n-1)/n) | 0.98198 | 0.86603 | 0.94868 |

Cause (READ, plotnine `stats/stat_summary.py` line 136): `mean_se` is `sqrt(np.var(series)/len(series))`, and `np.var` divides by n, not n-1. So plotnine's "standard error" is smaller than the usual `sd/sqrt(n)` by `sqrt((n-1)/n)`: 13 percent for the 4 French samples, 2 percent for 28 (RUN). If the recipe steps use `std(ddof=0)`, (1) equals (2) with a largest difference of 0 (RUN). That the usual definition is n-1 is the standard textbook definition (and Polars' own `std` default); I did not check R's `mean_se` (not run).
`mean_cl_normal` equals the hand formula (sample sem times the t quantile): difference 0 (RUN). A recipe cannot write that as table steps: it needs a t quantile and I found no Polars expression for it (reasoned; a fixed 1.96 gives another number: Norway ymin 283545.9 against 281454.2, France 154341.2 against 77928.0, RUN).

### A.3 Randomness and the seed (RUN)
- Factory with its default seed, `mean_cl_boot` drawn twice: identical. With seed 1: Norway 283024.2 to 371225.2 (changed).
- Direct plotnine, no seed: different each time. Direct plotnine with `random_state=0`: ALSO different each time (plotnine reads 0 as "no seed", READ line 292); `random_state=7` repeats. The library passes a numpy generator, so seed 0 works (READ `viz_factory.py` line 66; RUN identical twice).
- Science point: for the 4 French samples the bootstrap interval is 177226 to 376490 (width 199 thousand), the t interval is 77928 to 475788 (width 398 thousand): the bootstrap is half as wide with n=4. It is plotnine's default when no `fun_data` is written, and the seed hides nothing here: over seeds 0 to 19 the French lower end only moves between 173 and 181 thousand.

### A.4 What the export contains and where the numbers can be seen
- (1): the summary IS a table (`n`, `mean`, `sd`, `se`, `ymin`, `ymax`). The user reads it in HOME and exports it. A reviewer re-computes it from the steps. The step list is in the recipe.
- (2): the numbers are computed inside the picture. READ: no code in `app/` or `libs/` reads the computed layer data (`grep layers.data`: nothing). The export holds the 42-row sample table, the recipe text (`fun_data: mean_se`) and the seed. The drawn ends exist only on the picture and can be read off by eye. A reviewer who wants them has to rerun plotnine. (Assumed, not run: the exported bundle has no file of the stat output.)
- Missing values: with one missing `n50` in Norway, plotnine drops the row before the summary (n becomes 27, RUN) and issues a Python warning "stat_summary : Removed 1 rows containing non-finite values". Whether the app shows that warning I did not check. In (1) the same row is handled by the Polars step and `n` counts it explicitly.

## B. Which is more transparent, five sentences
1. Table steps (1) are more transparent: every number is a visible column, in the table the user exports, and the formula is the one the maker wrote (with n-1 or n written down).
2. A `stat_summary` with a name (2) is shorter but hides the formula in plotnine, where the "standard error" divides by n and the default interval is a random bootstrap.
3. Both are reproducible: (1) always; (2) only if the seed is fixed (the library does that) and the plotnine, pandas and numpy versions stay the same.
4. A recipe maker loses with (1) the t-based interval (no t quantile in table steps) and the bootstrap, and writes 4 steps; with (2) the exported numbers and the free choice of formula.
5. For a figure for a paper I would write (1); `stat_summary` with a named function is fine for a quick look, with the formula named in the description.

## C. Named summaries as a parameter (`mean`, `median`, `min`, `max`, a quantile)

The test (RUN, `c_named.py`): each name is mapped to the obvious function and the plotnine call with that function is compared with the same summary written as a Polars step, per country, with and without a missing value:

| Name | Direct plotnine call (`fun_y=...`) equals the Polars step? (largest difference) | With one missing value | Trap |
|---|---|---|---|
| `mean` (`np.mean`) | yes, 0 | yes, 0 | none |
| `median` (`np.median`) | yes, 0 | yes, 0 (plotnine drops the missing row first; called on the raw column `np.median` returns NaN) | depends on that drop |
| `min`, `max` | yes, 0 | yes, 0 | none |
| `quantile` p (`np.percentile`, linear) | yes, 0 | yes, 0 | Polars' own `quantile` default is `nearest`: q25 gives 241527, 184806, 185096 against 231189, 181016, 186675 (linear). The name must say which |
| `sd` (`np.std(ddof=1)`) | yes, 1.5e-11 (rounding) | yes | `np.std` default is n, not n-1: the name must fix it |

What is recorded in the export: only the name written in the recipe (`fun_y: median`); the function behind the name is code of the library, so the version of the library and of numpy decide it (assumed: not recorded today; a test that pins the table of names protects it). What a test should pin: each name against the direct plotnine call on a fixed table (as above); the missing-value row count; quantile written as a number between 0 and 1 and linear; a name not in the list refused with the list; no random numbers, so no seed; and that the exact plotnine component `plotnine_stat_summary` stays registered next to a `modif_stat_summary` (record V1-B: a documented change is `modif_`).
A name needs no expression (answer to the question of the paragraph N28): five names and a quantile number are data, not code. An expression (a text `lambda`) would need the checked-text rule of `stat_function` (RUN: `lambda x: x**2` runs, a call to `__import__('os').getcwd()` is refused with a clear message).

## D. The other function parameters: a name, a recipe step, or neither? (RUN, `d_params.py`)

| Parameter | Can be a NAME | Can be a recipe STEP | Cannot |
|---|---|---|---|
| scale `trans` | yes, already: `log10` works; a made-up name is refused (message: "Could not get transform object. None", weak) | | |
| facet `labeller` | yes, already: `label_value`, `label_both`, `label_context` work, `foo` refused | the labels a maker wants: write a new label column with `polars_with_columns` and facet by it, no function needed | |
| scale `labels` | a list or a dict, already | for a free text per level: a label column; | a function of the break. Names of label functions such as `percent` are NOT accepted (RUN: refused with the misleading "Breaks and labels are different lengths"); they could be added as names |
| scale `breaks`, `minor_breaks`, `limits` | numbers in a list, already | | a function of the range; the name `pretty` fails with a raw numpy error (RUN) |
| scale `rescaler`, `oob` | plotnine's names (`censor`, `squish`) could be names: not offered today | | a free function |
| `stat_function` `fun` | a numpy name (`sin`) and a text `lambda`, checked by an allow-list (RUN: works, harmful call refused) | | any other code |
| `geom_smooth` `method` | yes: `lm`, `loess`, ... | | a function |
| `geom_smooth` `formula` | text in the patsy form | | **see the FLAG below** |
| `stat_summary` `fun_data` | yes: 5 names | the summary as table steps (section A) | any function |
| `stat_summary` `fun_y`, `fun_ymin`, `fun_ymax` | yes if the names of section C are added | the summary as table steps | a free function |

### FLAG (verified bug, first): the text of a `geom_smooth` formula runs Python code (RUN)
A recipe layer `geom_smooth` with `method: lm` and a `formula` that contains `I(len(__import__('pathlib').Path('<scratch file>').write_text('x')) * 0 + x)` WROTE the file `tmpAI/panel/round7/s2_2/marker.txt` through the plot factory (the call then failed with a plain "refused by plotnine" error, but the code had already run). The cause is plotnine's formula reader (patsy evaluates what is inside `I(...)`). The text allow-list that protects Polars formulas and `stat_function` does not cover `formula`. The impact document says `formula` "as text (`y ~ x + I(x**2)` runs)" without this point. Records: ADR-099 point 14 (a recipe value must never run as code); FORMULA-SAFETY-1 (closed) covers Polars formulas only (READ `tasks.md`). A recipe from another person could therefore run code on the machine that renders it. A verified bug: it should get an issue now (I changed no file and opened no issue).

## E. Points for Eve (only where no record answers)

Records checked: `tasks.md` N28 (open), channel M97 (kept out of the night queue; default "keep these three parameters not offered"), the impact document section 4 (names of `fun_data` already work), V1-B naming (a documented change is `modif_`).

1. **N28: how should a maker get a mean with an error bar?** (a) Keep `fun_y`, `fun_ymin`, `fun_ymax` not offered, and teach the table-step route (a recipe example in the gallery and help). (b) Add named summaries as a `modif_stat_summary` (names of section C), exact `plotnine_stat_summary` stays. (c) Both. Default: (a), which is the standing default of M97. My view as data scientist: (a) is the most transparent for a published figure; (b) is a convenience and not needed for transparency.
2. **`mean_se` divides by n, not n-1.** Options: (a) say it in the component description and help, and give an advice in the checker for `fun_data: mean_se` ("plotnine's standard error uses n; it is 13 percent smaller than sd/sqrt(n) with 4 samples"); (b) a `modif_` version with the usual formula. Default: (a). The exact plotnine one must stay as it is (record V1-B).
3. **Advice for a `stat_summary` that names no `fun_data`.** Plotnine's default is the random bootstrap, narrow with few samples (RUN, n=4). Options: (a) a checker advice "write `fun_data` and say why"; (b) nothing. Default: (a), advice only.
4. **FLAG: the `geom_smooth` formula text runs Python.** Options: (a) check the text of `formula` with an allow-list like `stat_function` (column names, numbers, `+ - * / ** ~ ( )`, `I(...)` with numpy maths); (b) refuse a written `formula` and offer only `method`; (c) leave it. Default: (a). Needs her yes because it changes what a recipe can write; the bug itself should be filed regardless.
5. **Names for label and rescale functions** (`percent`, `comma`, `censor`, `squish`). Options: (a) add them as names; (b) do not, a maker writes a list or a label column. Default: (b): a recipe cannot hold a function, and a list is the transparent form (I did not check whether a shipped recipe wants one of these names).
