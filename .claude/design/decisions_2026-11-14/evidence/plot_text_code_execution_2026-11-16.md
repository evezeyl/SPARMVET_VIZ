# Plot texts that run code: the sweep and how each site is closed (PLOT-TEXT-RUNS-CODE-1, 2026-11-16)

Found by a data scientist: the `formula` of a smoother is evaluated as Python by plotnine. This file answers "where else can a text of a recipe, a plot spec, a `plot_defaults` block, a palette or theme, an audit step or a session file reach something that runs it as Python", and how each reachable place is closed. The decision is the one already taken (Eve, 2026-11-13 and 2026-11-15; FORMULA-SAFETY-1; recipe format spec section 15, check ST06; ADR-099 point 14): a text of a recipe must not be able to run code; the text is read as syntax and never run before it passes. Nothing new was decided here.

**RUN** = I ran it. **READ** = read in code. Versions: plotnine 0.15.4, patsy 1.0.2, statsmodels 0.14.6, mizani 0.14.4, numpy 2.4.4, pandas 3.0.2, Polars 1.40.1, Quarto 1.8.27.

## How it was tested (RUN)

A "harmless attempt" is a text that, if something runs it, writes a small file (`marker.txt`) under `tmpAI/` of the worktree: `__import__('pathlib').Path(<marker>).write_text('x')`, wrapped as `len(...) * 0` where a number is expected. After each attempt the marker is looked for.

1. **Brute force over the registry, against the UNCHANGED code** (commit `3d69e14f`, copied with `git archive` to `tmpAI/baseline`, so my own changes cannot hide a hole): every one of the 191 registered plot components, every argument it accepts (read from plotnine and the schema), each given the text as a text, as a list of one text and as a dictionary of one text. The 11 components whose arguments cannot be listed (`annotate`, `element_line`, `element_rect`, `element_text`, `facet_labeller`, `facet_margins`, `facet_scales`, `facet_space`, `stat_identity`, `theme_custom`, `theme_legend_position`) were also tried with 44 common argument names. Scripts: `tmpAI/probe/probe_all.py`, `probe_free.py`, `run_all.sh baseline` (git-ignored scratch; they write only under `tmpAI/probe/`).
2. **By hand, against the unchanged code** (`tmpAI/probe/probe_sites.py`): the spec-level keys (`mapping` text, `facet_by`, `theme`, `palette`), `plot_defaults` (`palette`, `theme`, `default_font_family`, `legend_position`) and the T3 `aesthetic_override` (`fill_palette`, `color`, `theme`, `shape`).
3. **Reading** every `eval`, `exec`, `compile`, `.query(`, `.eval(`, `pickle`, `yaml.load`, `subprocess`, `importlib` in `libs/*/src` and `app/` (list below).

## The sites that run code (REACHED; marker written on the unchanged code)

| # | Site (text in the recipe) | Our code | Where it runs | Closed by |
|---|---|---|---|---|
| 1 | `formula` of `geom_smooth` | `geoms/core.py` `handle_smooth` | plotnine `stats/smoothers.py` `lm_formula` (`smf.ols(formula, ...)`, `dmatrices`), `rlm_formula`, `gls_formula`, `glm_formula`: patsy evaluates the call arguments as Python (`y ~ I(__import__(...))`, also `y ~ __import__(...) + x`); Python's builtins are visible | PS06 in the checker; the same check in the factory (`get_component`) |
| 2 | `formula` of `stat_smooth` | `geoms/core.py` `handle_stat_smooth` | same | same |
| 3 | `formula` of `geom_quantile` and `stat_quantile` | `geoms/core.py` | plotnine `stats/stat_quantile.py` (patsy, same way); **found by the sweep, not named in the report** | same (the check keys on the argument name `formula`, so any component that takes one is covered) |
| 4 | `facets` of `facet_wrap`, as a text or a list | `facets/core.py` `handle_facet_wrap` | plotnine `facets/facet.py` `eval_facet_vars` (`env.eval(name, inner_namespace=data)`) for every variable that is not a column | PS06 + factory; the factory demands a column of the data |
| 5 | `facets`, `rows`, `cols` of `facet_grid` (also in the form `a ~ b`) | `facets/core.py` `handle_facet_grid` | same | same |
| 6 | `facets` of `facet_rows`, `facet_cols` | `facets/core.py` | same (they build a `facet_grid`) | same |

Two details of the facet routes. `facet_wrap` with the `~` form (`~ a`) and the spec's `facet_by` are not reachable: plotnine reads that form with the pattern `\w+`, which stops at the first character that is not a word character, so only a plain name is taken (RUN: not reached). An older defect found on the way (RUN, unchanged code): `facet_by: Collection year` (a column name with a space) facets by the column `Collection`, the first word, with no message, because of that pattern; reported, not touched. A facet text that is a list or a plain text is evaluated.

## The sites that were tried and do NOT run the text

| Site | Result (RUN on the unchanged code) | Why |
|---|---|---|
| spec `mapping` values (`x: "<code>"`, `fill`, `facet_by`) | refused | the factory demands that every mapped value is a column of the data (`viz_factory.py` "the aesthetic ... is mapped to the column ... which the data does not have"). plotnine would evaluate it (`mapping/evaluation.py` `env.eval`) if it got there; it does not |
| `mapping` and `data` given inside a layer's `params` | refused by plotnine (a dictionary is not an aesthetic) | no evaluation |
| `stat_function` `fun` | refused: the allow-list `function_string_problems` | already closed (FORMULA-SAFETY-1, `geoms/core.py` `_function_from_string`); now also in the checker (PS06) |
| `stat_function` `args`, `stat_summary` `fun_data`, `fun_y`, `fun_args`, `fun` | not run | a name is looked up in a table; `fun_args` is passed to the function as data; `fun_y: mean` is refused ("not a callable") |
| scale `trans`, `labels`, `breaks`, `minor_breaks`, `limits`, `oob`, `rescaler`, `expand`, `guide`, `name`; `scale_x_log10`, `coord_trans` | not run (errors or accepted) | looked up by name or used as data |
| `labeller` (facet_wrap, `facet_labeller`) | not run | `facet_labeller` has its own list of three names; plotnine's `as_labeller` looks the name up |
| `geom` / `stat` / `position` given as text, `annotate` `geom` | not run | plotnine looks the name up in a registry |
| `geom_text` `format_string`, `parse` | not run | `str.format` on the label; `parse` goes to matplotlib mathtext (not Python) |
| `method`, `method_args`, `span` of a smoother | not run | `method` is a name; `method_args` values go to the model as data (a statsmodels object cannot be written in a recipe) |
| `labs`, `xlab`, `ggtitle`, titles | not run | text drawn on the figure |
| `plot_defaults`: `palette`, `theme`, `default_font_family`, `legend_position` | not run (a warning or an error) | a palette name is looked up in a registry or a module (`getattr` of a name on the brewer module can only read an attribute, not call one) |
| spec `palette`, `theme` | not run | same |
| T3 `aesthetic_override`: `fill_palette`, `color`, `theme`, `shape` | not run | same |
| the free-form components (`annotate`, `element_*`, `theme_custom`, `facet_scales`, ...) with 44 common argument names | not run | |
| `filter` values of the audit steps and of `modif_filter` | typed values, never evaluated | `utils.filter_values.filter_condition` |
| session files | JSON, loaded with `json`; their texts reach the audit steps (below) | no evaluation by the loader |
| YAML | every loader in `libs/` and `app/` is a `SafeLoader` or a subclass of it (READ: `strict_yaml.py`, `recipe_loader.py`, `config_loader.py`, `data_analysis_recipe_navigator.py`, `group_plot_manager.py`, `bootloader.py` and the validators) | no object construction |

Every `eval` / `exec` / `compile` in `libs/*/src` and `app/` (READ, grep): `formula_check.py` (`evaluate_formula`, after the check), `geoms/core.py` `_function_from_string` (after the check). Nothing else. `subprocess` is used for `git`, `quarto` and the `claude` helper; their arguments are not recipe text (the helper's prompt is recipe text, out of scope: Blueprint helper, developer app features only).

## One more site found, NOT closed here: `report.qmd` of an export (REACHED, needs a decision)

The export writes `report.qmd` from text of the session and the recipe (`app/handlers/export_handlers.py`: the plot `title`, the plot and dataset ids, the audit step `reason` and `params`, the processing issues) with no escaping, and then runs `quarto render` on it on the machine that runs the app (`export_handlers.py` about line 1770). A text with a new line followed by a fenced Python cell is a code cell for Quarto.

RUN: I built `report.qmd` with the same line construction as the handler (the T3 Audit Trail row, `export_handlers.py` about line 1640-1647, with a `reason` that holds a fenced `{python}` cell), and ran `quarto render report.qmd --to html` in `tmpAI/quarto_probe/` as the handler does (`QUARTO_PYTHON=/usr/bin/python3`, the interpreter on this machine that has Jupyter): the cell ran and wrote its marker. I did not run the real export handler (it needs a Shiny session), so what I proved is the Quarto part and the unescaped line, not the whole path. With the default interpreter of this machine (Homebrew Python, no `yaml`) Quarto stops before running a cell, so the exposure depends on how the host is set up; a server with Quarto and Jupyter set up for rendering has it.

Who can supply that text: the audit `reason` is typed by the user, but it also arrives in a session file the user restores or imports and in an imported bundle; the plot `title`, ids and labels come from the recipe. This is the item "HOME session: verify" of spec section 15. It is **not closed in this task**: the file belongs to the HOME and export area, and how to close it is a choice (below).

Options (the HOME session and Eve decide):

| Option | What it does | Consequence |
|---|---|---|
| A. Escape every inserted text | one function that turns a text into a safe single Markdown line (new lines to spaces, backticks and braces escaped) and is used for every `f"...{text}..."` that goes into the report | small; the report keeps its python cells; every new insertion must remember to use it (a test can list the insertions) |
| B. Render without executing | `quarto render --no-execute`, the cells that matter written as plain Markdown by the app | no code of the report runs at all; the app writes the tables itself; a bigger change of the template |
| C. Both | A for correctness of the text, B as the second layer | most robust |

Recommendation: A now with a test that puts a fenced cell into every inserted field and asserts that the rendered source holds no cell that the author did not write; B later.

## The checks (what is built)

| Part | File | What it does |
|---|---|---|
| grammar of a smoother formula | `libs/utils/src/utils/formula_check.py` `smoother_formula_problems` | reads the text as tokens, never runs it. Allowed: the names `x` and `y`, numbers, `+ - * / : **` and the comparisons, brackets, `~` exactly once, the patsy functions `I C bs cr cc te center standardize scale`, the math names of `MATH_FUNCTIONS` bare or as `np.name`, `numpy.name`, `math.name`, `pi`, `e`; a call may have options whose value is a number or `True` or `False`; an exponent is a number up to 100 and not repeated; at most 400 parts and 2000 characters. Refused: any other name or function (`getattr`, `eval`, `open`, `__import__`, `np.load`), a text in quotes, a list, a subscript (`x[0]`), an attribute (`x.__class__`), a keyword or `*` argument, `lambda`, a conditional, a second `~` |
| the layer check | `libs/utils/src/utils/plot_text_check.py` `layer_text_problems` | applies the grammar to the argument `formula` of any component; checks the facet variables of the `facet_*` components (`facets`, `rows`, `cols`; the text is split at `~` and `+` as plotnine does): without the data a plain column name (letters, digits, underscore, space, dot, dash); with the data an exact column; checks the `fun` of `stat_function` |
| the checker | `libs/utils/src/utils/recipe_check.py` | check **PS06** on every layer, and on `mapping.facet_by`; needs no catalogue, so HOME's load gate, Blueprint's Validate, the importer and the gallery check all show it |
| the factory | `libs/viz_factory/src/viz_factory/registry.py` `get_component` / `refuse_unsafe_texts` | every component is handed out inside the same check, with the columns of the data; a refusal is a `CannotAct`, which the factory turns into the one error form that names the plot and the layer |
| the environment | `libs/viz_factory/src/viz_factory/checked_plot.py` `plot_environment` | plotnine evaluated texts in the frame of `VizFactory.render`, so the table, the recipe and `self` were visible by name. It now sees numpy maths only. Python's builtins stay visible to any `eval`: the check is what keeps them out of reach. A side effect that a recipe maker will like: `y ~ np.log(x)` and `y ~ log(x)` now work (before, they stopped with "name 'np' is not defined") |

The message reads: `Plot 'p', layer 2 (geom_smooth): the formula 'y ~ I(eval(x))' is refused: the function 'eval' is not allowed in a smoother formula. Fix: Suggestion: write one of the allowed functions: ...` (the checker prints `[PS06]` and the path `analysis_groups.g.plots.p.spec.layers[2].params.formula`). The label `Fix:` is the factory's one error form; the sentence after it is the suggestion.

## The smoother formulas (RUN through the factory and plotnine, `y ~ ...`, method `lm`)

Worked before the change and work now (the same result): `y ~ x`, `y ~ x + I(x**2)`, `y ~ x + I(x**2) + I(x**3)`, `y ~ x - 1`, `y ~ 0 + x`, `y ~ 1 + x`, `y ~ x ** 2`, `y ~ I(x ** 2)`, `y ~ I(x**0.5)`, `y ~ I(1/x)`, `y ~ I(x > 5)`, `y ~ I(x*2)`, `y ~ (x + 1)`, `y ~ I(x**2) + x`, `y ~ bs(x, df=4)`, `y ~ cr(x, df=4)`, `y ~ center(x)`, `y ~ standardize(x)`, `y ~ scale(x)`.

Did not work before (a name error, because the formula was evaluated in the frame of `render`, which has no `np`), work now: `y ~ np.log(x)`, `y ~ log(x)`, `y ~ I(np.log(x))`, `np.log(y) ~ np.log(x)`, `y ~ np.log10(x)`, `y ~ np.exp(x/10)`, `y ~ np.sqrt(x)`, `y ~ I(np.sqrt(x))`, `y ~ math.log(x)`, `y ~ I(np.abs(x))`, `y ~ np.abs(x)`, `y ~ np.log(x + 1)`, `y ~ np.sin(x)`, `y ~ np.sinh(x)`.

Do not work before and after (plotnine or patsy refuses them, or the name is outside the list): `y ~ C(g)`, `y ~ x*g`, `y ~ x:g`, `y ~ x + g` (a smoother sees only `x` and `y`), `y ~ poly(x, 2)` (patsy has no `poly`), `y ~ 1/x`, `y ~ x + I(x^2)`, `~ x`, `x`, and, refused by the allow-list, `np.power`, `np.log1p`, `np.arcsinh`.

**No shipped recipe, template, retest recipe or gallery example uses a `formula`** (grep of every `*.yaml`: no `formula:` key), so the allow-list refuses nothing that ships. Facets that ship use the forms `col`, `row ~ col`, `~ col` and `facet_by`; all pass.

## Pictures

(filled in at the end of the task, see the report)

## What was not checked

- The real export handler (`export_handlers.py`) was not run end to end (see the `report.qmd` section).
- Combinations of two texts in one layer (each argument was tried alone).
- A plotnine, patsy or mizani release other than the installed ones: a test (`libs/viz_factory/tests/test_plot_text_runs_no_code.py`) would have to be extended by the brute-force script; the script is scratch and not in the repository. A new plotnine release that evaluates another argument is not caught by the tests.
- `facet_by` in `plot_defaults` or in a T3 override: neither takes it.
