# Viewpoint of the scientist and data scientist: how can a recipe carry the arguments of plotnine and Polars without running whatever code?

Scope: one round, nothing decided, nothing built, no repository file changed. Scratch scripts: `tmpAI/panel/recipe_arguments/scientist/s1` to `s11` (run with `./.venv/bin/python`, `PYTHONPATH=.`). Versions run: plotnine 0.15.4, mizani 0.14.4, Polars 1.40.1, Python 3.14.10.

Labels: **run** = I ran it here; **read** = read in an installed package or in the repository at the named place; **memory** = from my knowledge, not checked here (Altair, R, dbt, CEL, Starlark, JSON-e are not installed); **reasoned**.

Eve's goal (decision_compliance.md section 1) read first: same data and recipe give the same result; nothing changes a result silently; the software informs, the user chooses. Every judgement below is against that.

---

## 0. Flags first: things that change a result silently or hide a step

These exist today or would exist under any option that passes the arguments through. Each needs an answer whatever Eve chooses.

1. **`stat_summary` without `fun_data` is not reproducible (run).** plotnine's default is `fun_data='mean_cl_boot'`, a bootstrap with `random_state=None` (read: `stat_summary.DEFAULT_PARAMS`). Two draws of the same recipe gave an upper bar of 7.0 and then 7.2. With the stat parameter `random_state=1` the two draws were identical. Same recipe, different picture.
2. **plotnine's `mean_se` is not the usual standard error (run, read).** It computes `sqrt(np.var(series)/len(series))` and `np.var` of a Series is the population variance (ddof=0). On [1,2,3,4,10] it gives a half-width of 1.414; the sample standard error is 1.581 (ddof=1). A reviewer who checks the bar in R, GraphPad or Excel gets 1.581. (That R's `mean_se` uses the sample variance is memory.) Also in the same function: a NaN is skipped by the mean but counted in n (run: [1, NaN, 3] gave half-width 0.577, correct would be 0.707 or 1.0 depending on ddof), and n=1 gives a bar of zero width with no message (run).
3. **Legend labels as a list pair by position, not by level (run).** Levels Resistant, Susceptible, Intermediate (plotnine sorts them: Intermediate, Resistant, Susceptible). `labels=["R","S","I"]` produced Intermediate->R, Resistant->S, Susceptible->I. The picture is wrong and nothing says so. A dict is safer, but a dict key with a different case (`susceptible`) or a missing level leaves the raw level text with no message (run). The checker has the data: it can compare the keys with the real levels and show the pairing.
4. **The Polars formula allow-list accepts unseeded randomness (run).** `pl.col('x').shuffle()` and `.sample(n=3)` pass the check and give a different result on every run; with `seed=1` they are stable. Same recipe, different table.
5. **Polars `quantile` defaults to interpolation "nearest" (run).** On [1,2,3,4,10,12] the 25th percentile is 2.0 in Polars; 2.25 in numpy, pandas and (memory) R. A "median with quartiles" built by the allowed formula differs from the figure a reviewer reproduces in R. The allow-list passes both forms.
6. **Format strings are a small language (run).** mizani `label_custom("{0.__class__}")` is accepted and prints `<class 'int'>`: `str.format` follows attributes. A "label format as data" option must restrict the string to `{:spec}` fields, or it opens an information leak.
7. **A YAML tag would be dropped silently by one existing loader (read, scout A4).** `data_analysis_recipe_validator.py:167-171` registers `add_multi_constructor("!", ... None)`: any tag becomes None there. A `!position_dodge {width: 0.5}` value would reach that loader as None. This matters for the tag option below.
8. **Already known (cited, not re-run; q6_the_15_objects.md D1 to D7):** `theme_custom` drops an unknown element name silently; the plot-level `guides:` block silently turns an unknown guide into a legend; a position or guide layer replaces or is lost by name. Any option that adds typed values must remove these first, or the typed value is only as safe as the silent fallback beside it.
9. **plotnine itself evaluates text as Python with builtins (run).** `aes("x", "v*0+len(__import__('os').getcwd())")` ran and returned 66 in plain plotnine. In the factory this is closed because a mapping value must be an existing column (read: viz_factory.py:305-307), so `aes` expressions and `after_stat('prop')` cannot be written. That is a safe choice and a loss (see approach C, G).

---

## 1. How other tools let a declarative file use a library's options

| Tool | What it does | Lesson for us | Evidence |
|---|---|---|---|
| ggplot2 (R) | The "recipe" is R code. `position = position_dodge(width=.5)`, `theme(axis.text.x = element_text(angle=90))`, `labels = scales::label_percent()`, `fun.data = "mean_se"` (a name or a function). | Full power, no safety: the file is a program. plotnine copies the same shape (verified here that all five named cases work as code). Name strings for summaries exist (`"mean_se"`): that is the only data form of a function. | memory; plotnine side run (s2) |
| Vega-Lite / Altair | A pure JSON grammar. Positions are channels and data (`xOffset`, `stack: "normalize"`), axis formatting is a d3 format string (`format: ".0%"`), scale type is data (`type: "log"`), summaries are transforms with enumerated operations (`aggregate: [{op: "mean"}]`), the composite mark `errorbar` has `extent: "stderr" / "stdev" / "ci" / "iqr"`. Computed fields use Vega's own small expression language (a restricted JS subset, a fixed function list, no function definitions). | Proof that a figure grammar can be data end to end. Its success comes from the library being designed as data first. plotnine is code first, so we have to build the data layer ourselves. The `errorbar extent` enum is exactly the "mean with SE / median with quartiles" need, as a choice not a function. Altair is not installed: not run. | memory |
| dbt | YAML for structure and arguments; logic in SQL with Jinja; tests are generic (named, with arguments from YAML); macros are project code. | The pattern "named test or macro + data arguments in YAML" is the registry option (D). The project's own macros are code: dbt trusts the project, it does not sandbox it. | memory |
| Polars expression serialisation | `Expr.meta.serialize(format="json")` gives JSON; `pl.Expr.deserialize` reads it. | See next paragraph. | run (s1) and read (docstring) |
| plotnine `after_stat`, `stage` | Strings or calls evaluated as Python inside `aes`. | A second eval route in the library itself (flag 9). The data equivalent is a computed column or a named statistic. | run (aes text), memory (after_stat, stage) |
| YAML tags | `!position_dodge {width: 0.5}` maps to a registry constructor in a SafeLoader subclass. | Works here (run, s9): known tags build the object, an unknown tag (`!os.system`) is refused with a ConstructorError, plain `safe_load` refuses all. Weak points: flag 7, and every other tool that reads the recipe (editors, JSON converters, the Blueprint UI) must know the tags. | run |
| CEL (Google) | A small expression language, not Turing complete, built to evaluate user expressions safely; cost can be bounded. | The right model if we ever want one common expression language for both libraries. Needs a new dependency and a second language for the scientist to learn. | memory |
| Starlark | Python-like, deterministic, no file or network access, designed for configuration. | A real sandbox language, but not Python: plotnine/Polars objects would have to be exposed to it one by one: the same registry work. | memory |
| JSON-e | A JSON templating language with a limited expression language and fixed built-in functions. | Useful for parameter substitution; too weak for statistics. | memory |
| RestrictedPython and similar in-process Python sandboxes | Try to make `eval` safe by filtering. | Known to be escapable; not recommended as the security boundary. Our own check is a closed grammar (an allow-list over the syntax tree), which is the sound variant of this idea. | memory |

**Polars serialisation, answered.** An expression can be written as data: `(pl.col("len").mean() / pl.col("n").sum()).alias("r")` becomes `{"Alias":[{"BinaryExpr":{"left":{"Agg":{"Mean":{"Column":"len"}}},"op":"TrueDivide","right":{"Agg":{"Sum":{"Column":"n"}}}}},"r"]}`, and the round trip gave an equal expression (run). It is not a recipe format: (a) Polars says "Serialization is not stable across Polars versions" (read, docstring of `Expr.deserialize`), so a recipe saved today may not load after an upgrade; (b) it is a dump of an internal tree, not for people (a `when/then` becomes a `Ternary` with `{"Literal":{"Dyn":{"Int":3}}}`); (c) the docstring warns that deserialising a plan with Python UDFs uses pickle and "can execute arbitrary code" (read). Writing a UDF into it needed cloudpickle, not installed, so I did not produce one (not run). Conclusion: not usable to author or to read; useful at most as an internal check, and it must never be read from a recipe.

---

## 2. What is really in the surface (numbers from the installed libraries)

- plotnine objects with a signature scanned: 212 names. Parameters that take a function-like value: `labels` 96, `breaks` 96, `limits` 98, `rescaler` 52, `oob` 52, `trans` 52 (all the scales), `labeller` 2 (read, s5). `labeller` is only the three names `label_value`, `label_both`, `label_context` in plotnine 0.15.4 (read, signature Literal). `guide` on the scales is `'legend'` or none.
- Geoms and stats take `**kwargs`: `geom_bar(self, mapping, data, **kwargs)` (read). The real parameter list comes from `DEFAULT_PARAMS` (`geom_bar`: stat, position, na_rm, just, width; `stat_summary`: geom, position, na_rm, fun_data, fun_y, fun_ymin, fun_ymax, fun_args, random_state; read, s5). So "generate the grammar from signatures" is true for scales, themes, guides and positions, and false for geoms: the repository's own `parameters.py` overlay is already the answer there.
- Themeables: 119 classes (read); 52 of them are documented to take an element (21 `element_line`, 20 `element_text`, 11 `element_rect`). The element type is only in the docstring ("theme_element : element_text"), not in a machine field (read). A slot-to-class table is therefore derivable but must be generated and tested, not trusted.
- The 14 value objects, parameter types: 4 have a parameter that is not plain data in the signature (`Margin`, `Theme`, `np.random.RandomState`; run, s6). A signature-generated grammar also missed a real parameter: `element_text(angle=90)` works in plotnine (alias through `**kwargs`) but `angle` is not in the signature, which lists `rotation` (run). So generation gives the skeleton; a curated overlay is needed, and a test must compare the overlay with plotnine.
- What plotnine itself can execute from a text (read, grep of the installed package): `aes` (mapping/evaluation.py `env.eval`), facets (facet.py:618), `qplot`, and patsy for smoother formulas. mizani `gettrans` takes a name from a registry (no eval). I found no `open(` for user files outside the data. The repository already closes the first three by rule (scout A1, A2).

---

## 3. The approaches

Eve's own ideas are included as stated. "Proposed by": Eve, review session (the options A to D of q6, the call it "typed value", the registry and script ideas in the brief), me.

For each: what the author writes, what can and cannot be said, reproducibility and what the export records, what is checked and how the error reads, silent changes.

### Approach 1. Typed value objects (Eve's idea 2, shaped like q6 options B/C)

A closed registry of value objects; a value is `{name: <plotnine name>, params: {...}}` (the form `theme_custom` and the `guides:` block already use). Names and parameters checked against the signature plus a curated overlay; unknown name, unknown parameter, wrong type all refused with a "did you mean".

```yaml
- name: geom_bar
  params:
    position: {name: position_dodge, params: {width: 0.5}}
- name: theme_custom                       # Eve's idea 1: elements live in the theme
  params:
    axis_text_x: {name: element_text, params: {angle: 90}}
    panel_grid_minor: {name: element_blank}
- name: guides
  params:
    fill: {name: guide_legend, params: {ncol: 2}}
- name: scale_fill_discrete
  params:
    labels: {Resistant: Res., Susceptible: Sus., Intermediate: Int.}   # plain data, no object
```

- Can express: all 15 objects at the slots that take them, with every parameter that is plain data (verified here that the three named plotnine forms work, s2). Cannot: parameters that are objects (`theme=` of a guide, `margin` as an object; `random_state` as RandomState, but an integer seed is fine); functions.
- Reproducibility: the typed value is data, so the recipe is the record. The export should write the resolved value with its defaults (for example `position_dodge(width=None, preserve='total')`, run: today's defaults) and the plotnine version.
- Checked: at the checker, before drawing. Error reads like the existing ones: `axis_text_x: unknown element 'element_txt'. Known: ...`. In plotnine alone a typo `angel` fails only at draw time with a matplotlib message (run: `Text.set() got an unexpected keyword argument 'angel'`); the checker should catch it earlier.
- Silent changes: none if the silent fallbacks of flag 8 are removed first and the slot refuses a name it does not know. With layer-form positions kept beside it, the "replaces the earlier position" defects stay.
- Eve's idea 1 (elements under a theme): correct and complete for the 52 element-valued theme keys, and it is how plotnine works (run). It does not cover positions (a layer slot) nor guides (a scale or `guides` slot). So it is one third of the answer, not a replacement.

### Approach 2. Slot-implied short form (mine)

The slot knows the class (a theme key knows it takes an element; `position` knows it takes a position; `guides` entries take a guide), so the author writes only the arguments and, where the class is a choice, its short name.

```yaml
position: {dodge: {width: 0.5}}                # or position: dodge when no argument
theme_custom:
  axis_text_x: {angle: 90}                     # class from the themeable's element type
  panel_grid_minor: blank
guides:
  fill: {legend: {ncol: 2}}
```

- Same reach as approach 1; shorter, no `element_`/`position_` words, so the rename question (`plotnine_`/`modif_`) never touches it. Easier to read for a biologist.
- Cost: the slot-to-class table must be generated (the 52 element types are only in docstrings, read) and a test must compare it with plotnine; "one thing, two spellings" if the long form stays; error text is one step further from the plotnine docs the author is copying from. Keys named like their class (`{dodge: ...}`) are a second grammar to learn.
- Reproducibility and checks as approach 1. Silent changes: none by itself.

### Approach 3. Call text, parsed not evaluated (mine, the Polars habit applied to plotnine)

The author writes the call as in the plotnine documentation; the app parses it into a syntax tree, accepts only calls to the 15 names with named literal arguments, builds the objects itself. No `eval`.

```yaml
position: "position_dodge(width=0.5)"
theme_custom:
  axis_text_x: "element_text(angle=90)"
guides:
  fill: "guide_legend(ncol=2)"
```

- Run (s11): the three named cases built; `__import__('os').getcwd()`, `open('/etc/passwd')`, a lambda and `9**9**9` were refused; a typo `element_text(angel=90)` is accepted by the parser and must still go through the signature check (same gap as approach 1).
- Gain: copy and paste from plotnine documentation and from tutorials; the same form scientists already use in the formula text. Loss: it is a text with its own grammar to document and test; quoting inside YAML; the checker must parse it (one more text site, though not an evaluator); two different forms across the recipe (text here, dict there) unless Polars goes the same way.
- Silent changes: none by itself. Error reads as a syntax message, so the "did you mean" must be built.

### Approach 4. A shipped registry of named functions with data parameters (brief's premise, my content)

The deployment ships a small library of named, tested functions. The recipe names one and gives data parameters. The library is code, but code the project wrote and tested, not code in a recipe.

```yaml
- name: stat_summary
  params:
    fun_data: {name: mean_sem, params: {ddof: 1}}
- name: scale_y_continuous
  params:
    labels: {name: percent, params: {accuracy: 1}}
    breaks: {name: log_breaks, params: {base: 2}}
- name: scale_x_datetime
  params: {date_labels: "%Y", date_breaks: "1 year"}     # already data in plotnine
```

- I ran a registry of three summaries inside `stat_summary` (s9) and compared with independent numbers: `mean_sem` gave 4 ± 1.5811 (reference 1.5811), `mean_ci_t` half-width 4.3899 (scipy reference 4.3899), `median_iqr` 3.0 with 2.0 to 4.0. NaN is dropped and n is recorded; n<2 returns NaN, not a zero-width bar.
- Can express: anything the registry holds. Cannot: a function nobody registered. Whoever adds a name decides the statistics for everyone, so each entry needs a test against a reference and a written definition (ddof, interpolation, seed). That is the point of the option, and also its work.
- Reproducibility: the export records name, parameters, registry version and a hash of the function source; seeded functions (bootstrap) must take a required `seed`.
- Checked: names and parameter types at the checker; error reads `fun_data: unknown summary 'mean_se2'. Known: mean_sem, median_iqr, ...`.
- Silent changes: none if no entry hides a default (flags 1, 2, 5): the registry can remove them (required seed, ddof shown in the recipe).

### Approach 5. Compute in the data, plot the columns (mine, reconsiders the premise)

Do not pass functions to the plot at all. The summary, the labels and the breaks that need a function become a Polars step that produces a table, and the plot draws the table with ordinary geoms.

```yaml
steps:
  - action: polars_group_by
    params:
      by: [group]
      named_aggs:
        y:  "pl.col('value').mean()"
        n:  "pl.col('value').count()"
        se: "pl.col('value').std() / pl.col('value').count().sqrt()"
  - action: polars_with_columns
    params:
      named_exprs:
        ymin: "pl.col('y') - pl.col('se')"
        ymax: "pl.col('y') + pl.col('se')"
plot:
  - name: geom_pointrange        # y, ymin, ymax are columns
```

- Run (s10): the group table gave a = 4.0 with SE 1.581139 (ddof=1, as polars `std` defaults) and n=5, and `geom_pointrange` drew it. The quartile version needed `quantile(0.25)` with the interpolation named (flag 5). Log scale with a list of breaks (`trans: log10`, `breaks: [1,10,100,1000]`) and `date_labels="%Y"`, `date_breaks="1 year"` are plain data in plotnine already (run). `label_percent(accuracy=1)` needs a named constructor (run) or a restricted format string (flag 6). Legend text can be made a column, or the dict form with a key check (flag 3).
- Gain: the numbers behind the bars are a table the user can see, the export can hold, and a reviewer can recompute; the sample size `n` is visible (plotnine's `stat_summary` never shows it). No function reaches a plot.
- Loss (run/reasoned): a percentile bootstrap interval is not expressible per group in an allowed expression (so it is lost unless a registry entry is added), `after_stat` proportions need a column, and every summary figure needs a step before the plot (more steps to write). Proportion data with a Wilson interval (resistant isolates per group; typical in this field) is arithmetic with `sqrt`, which the allow-list allows, but it is long to write: a registry action would serve better.
- Silent changes: none from the plot; the step carries the Polars risks (flags 4, 5).

### Approach 6. A script file the recipe points to, recorded by hash (brief's premise)

```yaml
functions: {file: my_summaries.py, sha256: 9f2c...}
...
fun_data: {function: my_summaries.mean_trimmed, params: {trim: 0.1}}
```

- Can express: anything Python or Polars can. This is the only option that fulfils "use all Python and Polars options" literally.
- Reproducibility: strong if the hash, the Python version and the versions of the libraries are recorded and checked at load. A hash proves that the file is the same one; it does not prove that the file is safe.
- Security: it runs arbitrary code. That contradicts the rule cited in tasks.md:454 ("a recipe text must never run code", date 2026-11-13; the scout says the ledger line is missing: CONFIRM) and ADR-071's two layers. The app imports recipes and bundles from other people (scout, bundle_importer), so a recipe from a colleague could carry the file. It could be acceptable only as an explicit deployment mode for a trusted local installation, with the code shown to the user before the first run. That is a different product decision, not an argument handling choice.
- I did not build or run it (not run); the judgement is reasoned.

### Approach 7. Deny-list over arbitrary Python (Eve's idea 3)

Allow the user to write anything and forbid dangerous names, imports, file reads and parameters.

- A deny-list must be complete against everything Python and its libraries can reach; it is the weakest of the options and is known to fail (memory: in-process sandbox escapes through attribute walks such as `().__class__.__mro__...`). The repository already chose the opposite for Polars: an **allow**-list on the syntax tree, with the Polars list generated from the library signatures (38 module functions allowed; every method with a Callable parameter denied; read formula_check.py:44-91, and my probes s8: `map_elements`, `pipe`, `read_csv`, `Expr.deserialize`, `meta.serialize`, `int_range` were refused). It was extensive to build once and is now tested. It still left holes (flags 4, 5; `repeat_by(10**9)` is accepted, so a memory bomb passes, run s8; Eve accepted "no size limit now", D-0064).
- So idea 3 is right in its worry (the list is large) and the answer is: invert it (allow), and generate the allowed list from the library with tests, as already done. Eve's own words "I guess it still would be very extensive" are correct for a deny-list and not for an allow-list that is generated.

### Approach 8. A second expression language shared by both libraries (mine, longer term)

One restricted expression language (CEL or the Vega expression idea) for every computed thing: formulas, summaries, label functions. The recipe holds expressions; a translator turns them into Polars expressions and into plotnine function objects.

- Can express: custom summaries and labels with one grammar and one checker; the scientist learns one language.
- Cost: a new dependency or a language to write and maintain; translation to plotnine callables is code we write and test per function; the Polars text the repository has today (`pl.col(...)`) already is that language for Polars, and changing it would break 16 shipped recipes (grep: 16 YAML files contain `pl.` calls). Not recommended now; listed because it reconsiders the premise.

---

## 4. Functions as parameters: what a scientist really needs

For this field (bacterial genomics, AMR phenotypes, assemblies, MIC, counts by year or source) the figures I would expect to defend:

| Need | Typical use | Data-only in plotnine today (run)? | Registry entry needed? |
|---|---|---|---|
| Mean with SE (sample, ddof=1) | assembly length, n50 by group | No: `mean_se` is ddof=0 (flag 2) | Yes, or compute in data (approach 5) |
| Mean with SD | spread | `mean_sdl` named exists (read) | Optional |
| Mean with 95% CI (t) | method comparison | `mean_cl_normal` named exists (read) | Check against scipy t before trusting |
| Mean with bootstrap CI | skewed data | `mean_cl_boot` but unseeded by default (flag 1) | Yes with a required seed |
| Median with quartiles (IQR) | skewed counts | Not named: `median_hilow` is a 95% interval by default (reasoned: signature `confidence_interval=0.95`; I did not run it), not quartiles | Yes, or data (approach 5, name the interpolation) |
| Median with min and max | small groups | No | Yes, or data |
| Proportion with Wilson or exact interval | percent resistant per group | No | Yes (not in plotnine at all), or arithmetic in data |
| Count n and show it | every group | `stat_summary` hides n | Data (approach 5) |
| Percent labels | proportions | `label_custom("{:.0%}")` works (run) | A named enum or a restricted format string (flag 6) |
| Thousands separator, scientific | counts, lengths | `label_custom("{:,.0f}")` (run), `label_scientific()` | Same |
| Log10 or log2 breaks and labels | MIC, counts | `trans: log10` is a string; breaks can be a list `[0.25,0.5,1,2,4,8]` (run); `label_log` exists | List data is enough |
| Date formats and breaks | isolates per year | `date_labels="%Y"`, `date_breaks="1 year"` strings (run) | No |
| Relabel legend entries | resistance classes | dict (run) | Data with the key check (flag 3) |
| Facet label style | `label_both` | One of three names (read) | No |
| `stat_function` curve | fitted line | Text grammar exists in the repository (scout A1.2) | Already handled |

Answers:
- Is a fixed registry of named functions with data parameters enough? For these needs, yes: about ten entries (mean_sem, mean_sd, mean_ci_t, mean_cl_boot with seed, median_iqr, median_range, proportion_wilson, percent, comma, scientific, log breaks). Two thirds are already plain data in plotnine or can be computed in the data.
- What is lost: a user-defined reducer or label function that nobody registered (a trimmed mean, a custom score, a label that joins two columns). The label that joins columns is a column, so not lost. A custom statistic inside a plot is lost, but nothing stops it being computed in a Polars step if the allow-list can express it.
- The registry is also where the statistical definition is fixed once and shown (ddof, interpolation, seed). A scientist cannot defend `mean_se` today without knowing flag 2.

---

## 5. The Polars side: text, data or registry?

Is the allow-listed formula text the right form? **Yes for authoring.** I converted five shipped-style formulas to nested dictionaries (run, s4): `pl.col('hsp_len').cast(pl.Float64) / pl.col('total_len').cast(pl.Float64)` became 14 lines of YAML, a `when/then/otherwise` 17 lines, and the string-method chain would not convert without extra rules in my prototype. The two forms built an equal expression on every case that converted, so a data form is a faithful second view, but it is far harder to read and to write. A reviewer reads the one-line text. The shipped formulas (grep, 16 files) are mostly `when/then`, `over`, `cast`, `str.*`, arithmetic, `replace_strict` with a dict.

A data form is worth having only as a derived view (show the parsed tree: which function, which columns), not as the recipe language. A registry already exists for the common cases: the 68 `polars_` actions are one. More presets (z-score by group, percent of total) belong there rather than as more text.

What the text form needs, honest list (run unless marked):
1. Seeds: refuse or require `seed` for `shuffle`, `sample` (flag 4).
2. Quantile: make the interpolation visible or required (flag 5).
3. The recipe check should say which columns a formula reads and which it creates (it can: `meta.root_names()` and `meta.output_name()` worked in s1); that is what a reviewer asks.
4. Record the Polars version with the result (Polars JSON is not a stable record; the text plus the version is).
5. `repeat_by`/large ranges: decided "no size limit now" (D-0064); I record that it is accepted.

---

## 6. The named cases, in one place (run: s2, s6, s10, s11)

| Case | In plotnine (run) | Plain data that describes it | Which approaches cover it |
|---|---|---|---|
| `position_dodge(width=0.5)` as a geom's `position` | works | `{name/params}` or `{dodge: {width: 0.5}}` or text | 1, 2, 3 |
| `theme(axis_text_x=element_text(angle=90))` | works | element at a theme key | 1, 2, 3 (Eve's idea 1 is this case) |
| `guides(fill=guide_legend(ncol=2))` | works | guide at a `guides` key or a scale's `guide` | 1, 2, 3 (idea 1 does not cover it) |
| `scale_fill_discrete(labels={...})` | works; list also works; function also works | a dict of level to text | all, with the key check (flag 3) |
| `stat_summary(fun_data="mean_se")` | works as a name; `fun_y="mean"` as a string fails: "'mean' is not a callable object" | a name from a registry | 4, 5 |
| `stat_summary(fun_y=..., fun_ymin=..., fun_ymax=...)` | needs callables | three names from a registry, or three columns | 4, 5 (the factory refuses these today) |
| scale `labels` or `breaks` as a function | works with a function or `label_*()` | named constructor with data args, or a list, or `date_labels` strings | 4 (named), data forms |
| labellers | one of three names | the name | any |
| Polars `with_columns`, `agg`, `filter` | text, allow-listed, evaluated | text stays | existing |

---

## 7. Summary table

| Approach | Proposed by | Covers which named cases | What is lost | Risk to results | My judgement |
|---|---|---|---|---|---|
| 1 Typed value objects, closed registry, checked parameters | Eve (idea 2) and review session (q6 B/C) | position, element, guide (not function) | object-valued parameters; names must be curated | Low once fallbacks D6/D7 are removed; today's silent fallbacks remain a risk | Sound and plain data. Needs the overlay and tests. |
| Eve's idea 1: elements under the theme | Eve | element only | positions and guides | None added | Right for 52 theme keys, one third of the question |
| 2 Slot-implied short form | me | position, element, guide | a second spelling, generated table to maintain | Low | Best for readability; more to generate and test |
| 3 Call text parsed with `ast`, not evaluated | me | position, element, guide | a second grammar to document | Low; run: hostile text refused | Good for people who copy from plotnine docs; needs "did you mean" |
| 4 Named function registry with data parameters | review session (brief) and me (content) | functions, labels, breaks, summaries | functions nobody registered | Lowest if each entry is tested and has no hidden default | Best answer for functions; needs ownership and tests |
| 5 Compute in the data, plot columns | me | summaries, labels as columns; position/element/guide untouched | bootstrap CI, `after_stat`, more steps | Lowest at the plot; the step carries Polars risks | Best for reproducibility and review; not a complete answer |
| 6 Script file by hash | review session (brief) | everything | nothing | Highest: arbitrary code; hash is identity, not safety | Only as a separate trusted-deployment mode if Eve changes the "no code" rule |
| 7 Deny-list over Python | Eve (idea 3) | everything in theory | nothing in theory | High: a deny-list is never complete | Do not use; the allow-list in the repository is its safer form |
| 8 Second shared expression language | me | functions and formulas | 16 shipped recipes would change; new dependency | Medium (migration) | Not now; listed because it reconsiders the premise |
| YAML tags (variant of 1) | me | position, element, guide | the tolerant loader turns tags into None (flag 7); other tools lose them | Medium unless every loader is fixed | Avoid; the `{name, params}` form needs no loader change |
| Polars JSON serialisation | review session (brief) | Polars only | readability, version stability | High: not stable across versions, pickle with UDFs | Not usable as recipe format |

---

## 8. Recommendation (mine, for Eve to decide)

I would take a combination because the question has three separate parts and they do not need the same answer:

1. **Objects (position, element, guide): approach 1 or 2 or 3, one of them, with the checks.** They are all plain data and the choice between them is about readability and how the rename rule (`plotnine_`, `modif_`) is applied, not about security. In every case the checker must compare parameter names with the library (a typo reaches plotnine only at draw time with a matplotlib message, run), and the silent fallbacks (flag 8) must be removed first. My preference is the `{name, params}` form of approach 1 because the repository already uses it, it is unambiguous for tools, and it asks no loader change.
2. **Functions: approach 4 (a small registry) for what is needed in a plot, and approach 5 (compute in the data) as the default for summaries.** Both avoid code in the recipe. Whichever is chosen must first fix flags 1 to 3: seed required, ddof visible, label dict or list shown as an explicit level-to-text pairing.
3. **Polars: keep the allow-listed text.** Add the seed and interpolation checks, and show the columns read and written.
4. **Script file (6): not now; the rule cited at tasks.md:454 stands unless Eve changes it.**

The answer to "should work: we should be able to use all python and polars options" is: all the options that are data (names and values) can be made available by generated lists with a test against the library; options that are functions need either a registry or a computed column. That keeps "nothing changes a result silently". The price is that the first release will not offer an arbitrary user-written function, which is a choice for Eve to take knowingly.

## 9. What Eve must be told to choose well (not what to choose)

- Which of the three families she wants to open now: objects (cheap, data), functions (a registry or compute-in-data, needs owners for the statistics), arbitrary code (a different security decision).
- That plotnine's own defaults are not neutral: `stat_summary` is unseeded and `mean_se` uses ddof=0 (flags 1, 2). Passing them through unchanged is a choice about results.
- That a list of legend labels pairs by sorted position, a dict by exact key, and neither says when it is wrong (flag 3).
- That a tag-based YAML form fails silently in one existing loader (flag 7).
- That the Polars side has two silent defaults (unseeded sampling, nearest-rank quantile) that are independent of this question and exist today (flags 4, 5).

## 10. Not checked

- Altair, Vega-Lite, R/ggplot2, dbt, CEL, Starlark, JSON-e: from memory only; none installed or run. The R `mean_se` definition is memory.
- Whether deserialising a hand-written Polars JSON containing pickled bytes runs code: only the documentation was read; I did not produce or load a UDF (cloudpickle is not installed and I installed nothing).
- Fuzzing the allow-list for escapes (only 17 probes, s8); the stated residual risk is time and memory (D-0064).
- The recipe checker's behaviour on any new value form (no form exists); the Blueprint UI, the export code (what versions it records today), the HOME audit.
- Pictures: I compared objects, numbers and labels, not pixels.
- plotnine versions other than 0.15.4; mizani 0.14.4 only.
- Whether other loaders besides the one named in flag 7 also ignore tags (flag 7 is read from the scout report only, not re-read).
- Whether `label_custom` with a restricted format string is enough for all label needs; whether bootstrap with a required seed gives the same numbers on a different numpy version.
- The ledger line for "no code from recipe text, 2026-11-13": the scout could not find it; I did not search the ledger.
