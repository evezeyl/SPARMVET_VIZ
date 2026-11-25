Exploration report. Nothing in it is decided unless a ledger number is given. Status: Report for your choice. Nothing is decided and nothing is built (as written in the report). Written: 2026-11-17. Source: .claude/design/studies/scratch_records_2026-11/panel/recipe_arguments/REPORT_for_eve.md. Copied here on 2026-11-17.

Paragraphs below are copied unchanged. Paths inside the body that point to tmpAI/ working files are local (not in git) and stay as written.

---

# How a recipe can carry the arguments and objects of plotnine and Polars, without running code

Added 2026-11-17 (night): the last chapter, "Added 2026-11-17 (night): how others keep user-written formulas safe", holds the formula-safety research. The text above is unchanged.

Written by the coordinator's agents, from one survey and four viewpoints: data scientist, software architect with security, developer, and recipe author as user. Date: 2026-11-17.
This is a report for your choice. Nothing is decided and nothing is built.

Your question (2026-11-17): how can a recipe use those arguments and constructions, without running whatever code, so that the plotnine and Polars decorators can use them? You asked for proposals before answering. These are the proposals.

Files behind this report, all in this folder: `scout_what_exists.md`, `viewpoint_scientist.md`, `viewpoint_architect_security.md`, `viewpoint_developer.md`, `viewpoint_user.md`. The earlier facts on the 15 objects are in `.claude/design/studies/scratch_records_2026-11/panel/viz_rename/q6_the_15_objects.md`.

Labels used for evidence: "run" = an agent ran it here. "read" = an agent read it in code or in the installed library. "memory" = from knowledge, not checked. "reasoned" = inferred. "estimate" = a guess of effort.

Decisions that apply and are quoted: D-0050 "No silent error that is the rule." D-0101 "Everything she reads is written in short plain sentences, one idea each". D-0165 "Where no decision exists and one is needed, that must be reported to her." Where this report finds that a decision is missing, it says so and asks you.

## The short answer

- **Names of parameters are already checked today.** The app reads every parameter name from plotnine and refuses a wrong name with "did you mean". What is not checked is the value and its type.
- **Most of what you listed can be written as plain data.** Positions with a width, element settings, guides, legend labels. No code runs. All four viewpoints agree.
- **The 15 objects are three families.** Eight positions, four elements, three guides. The proposals differ only in how a value is written and where it sits.
- **A list of forbidden things does not work.** All viewpoints reject it. The security reviewer found two holes in a list that was built from the library itself. A list of allowed things works, and it is short (about 70 registered values).
- **Functions as parameters are a different question.** They need a small list of named functions, or the summary is computed in the data first. The choices hidden inside such functions are scientific choices and are yours.
- **The demo needs nothing of this.** The developer read the demo recipe: one bar plot, no position, no element, no guide.
- **Some results change silently today, whatever you choose.** They are listed first, in the next section.
- **The viewpoints suggest one build order.** Fix today's silent problems first. Then decide the form of the 15. Then build the typed values. See "Recommendation".

## Read this first: what changes a result silently TODAY, whatever you choose

You decided that a silent error is not allowed (D-0050). These exist now.

### The scientist's findings (results)

1. **The summary layer is not reproducible by default** (run). Plotnine's `stat_summary` without `fun_data` uses a bootstrap interval with no seed. The same recipe gave an upper bar of 7.0, then 7.2. With a seed, two draws were identical. Suggestion: a seed is required for any random summary.
2. **The standard error is not the usual one** (run, read). Plotnine's `mean_se` uses the population variance (divide by n). On [1,2,3,4,10] it gives 1.414. The usual standard error (divide by n minus 1) gives 1.581. A reviewer who checks the bar in R, GraphPad or Excel gets 1.581. That R uses the sample variance is from memory. Also: a missing value is skipped by the mean but counted in n (run), and one value alone gives a bar of zero width with no message (run). Suggestion: a named summary that states the variance rule in the recipe.
3. **Legend labels given as a list are paired by sorted position, not by level** (run). Levels Resistant, Susceptible, Intermediate are sorted by plotnine as Intermediate, Resistant, Susceptible. The list ["R","S","I"] gave Intermediate as R. The picture is wrong and nothing says so. A dictionary is safer, but a key with the wrong capital letter, or a missing level, leaves the raw text with no message (run). Suggestion: the checker compares the keys with the real levels and shows the pairing to the user.
4. **Random shuffle and random sample are accepted in Polars formulas** (run). `shuffle()` and `sample(n=3)` pass the check and give a different table on each run. With a seed they are stable. Suggestion: refuse them, or require a seed.
5. **The Polars quantile default is "nearest"** (run). On [1,2,3,4,10,12] the 25th percentile is 2.0 in Polars and 2.25 in numpy and pandas (R from memory). A "median with quartiles" differs from what a reviewer reproduces. Suggestion: make the interpolation visible or required.

### The layer-form differences (seven, or six)

The brief mentioned six. The source report (`q6_the_15_objects.md`, section 6) lists seven, D1 to D7, plus a note D8 that is not a defect. The architect and the developer both use seven. I use seven. All were run.

| Label | What happens silently |
|---|---|
| D1 | `element_text` then `element_blank` on the same axis: the "hide" is lost. |
| D2 | Two `element_text` on one axis: the first one's settings are lost. |
| D3 | `element_text` is applied last, whatever its place. After a complete theme, the rotation survives; in plotnine alone it would not. The shipped heatmap recipe is written in that order. |
| D4 | Position layers are removed by name: bar, dodge, bar, dodge keeps only the last dodge. The first bar stays stacked. |
| D5 | The same removal by name for guides and for `element_blank` and `element_line`: the first is lost. |
| D6 | The plot-level `guides:` block turns an unknown guide name into a legend, silently. |
| D7 | `theme_custom` drops an unknown element name, silently. |

D1 to D5 come from the layer form (a layer is attached to the last layer, removed by name, applied last). D6 and D7 come from two hand-written readers. These two are the "two silent fallbacks".

### The security findings

1. **The formula allow-list admits two members that read a file or load serialised data** (run, by the architect). The members are `Expr.deserialize` and `Expr.from_json`. Run: a recipe formula read a file from a path written in the recipe. A second run accepted inline JSON. The Polars documentation says that loading a plan with a Python function uses pickle and can run code. A payload with a Python function was not built, so code execution is reasoned from the documentation, not shown. The list had 412 allowed members; 2 were wrong. The survey of the code (the scout) said file reading was "not reachable". The architect's run shows it is reachable. The run counts. A fix was started at once on 2026-11-17, because the issue falls under a decided rule (formulas only from an allowed list, D-0030). I did not check the state of that fix. Suggestion: allow a member by what it is (not static, takes no path, no file object, no bytes), and a test that walks all members.
2. **The path check is inactive in the app** (read, run). The spec says the app passes the allowed folders (PA02). The code passes none. Run: a path through a link that points outside the project passes. At run time the data file is also opened with no containment check. The code and the spec contradict each other. Suggestion: either the app passes the folders, or the spec is corrected by your decision. Add a test with a link.
3. **A session zip can overwrite an existing session** (reasoned from code, partly run). On this Python (3.14.10) a crafted zip did not escape the folder (run). But the session key is the first folder name in the zip, so a zip can write over an existing session with that key. There is no size limit and no test. Suggestion: check the member names, tell the user when the key exists and let the user choose, add the crafted zip as a test.
4. **Plain-data parameters that are still risky** (run unless marked):
   - A format string for text labels (`format_string` of geom_text and geom_label) follows attributes: `{0.__class__.__mro__}` printed class information into the plot. Low risk, but it is a small language.
   - `rc` and `fname` of `theme_matplotlib`. Today they fail safe (the run fails). If every library option were passed through, `fname` would read a file and echo one of its lines in a warning, and `rc` has keys such as `text.usetex` (runs LaTeX, from memory) and a savefig directory.
   - A figure size and dpi with no limit: a 50000 by 50000 pixel figure was built with no refusal (run). You decided "no time or size limit now" (D-0064). It is listed so that you decide knowing this number.
5. **The global include constructor** (run). The loader of recipes registers `!include` on the global YAML loader. After two recipes were loaded, any other YAML read later honoured `!include` with the folder of the last recipe, and a refusal was silent. Suggestion: a private loader per recipe, as the other loaders do, and a test.
6. **The checks on plot text depend on parameter names** (read). The text checks look at the names `formula`, `facets`, `rows`, `cols`, `fun`. A new plotnine parameter that evaluates text under another name is not caught. A new parameter that takes a function is exposed with no test failing. Suggestion: a test that walks all registered parameters and fails when a new one takes a function, a path, a format string or a dictionary of engine settings.

The ledger has no line for the rule "no code is executed from recipe text" (2026-11-13). It is cited in the task list, but the decision line is missing (the scout tagged it CONFIRM). Question 1 below asks you to confirm it.

## What exists today

| Thing | State | Label |
|---|---|---|
| Parameter names of the 191 plot components | Read from plotnine; wrong name refused with "did you mean". 186 have a readable list; 5 are free-form. | read, run |
| Parameter types | Not checked. Of 1321 (component, parameter) pairs: 41% plain data only, 239 allow a function beside other forms, 44 need a library object, 490 not readable. The count repeats shared parameters. | run |
| Geoms and stats (63 components) | No type annotations in plotnine. Types can only come from the default value plus a hand table. | run |
| Position of a geom | Only a string (`dodge`). A value with a width (`{name: position_dodge, params: {width: 0.5}}`) fails: "Unknown position of type dict". | run |
| Elements, guides, positions as layers | Work as layers, with the seven differences above. | run |
| Nested values in code | Three hand-written places: `theme_custom`, the `guides:` block, the position layer. Two have silent fallbacks (D6, D7). | read, run |
| Value objects | Exactly 15, by base class: 8 positions, 4 elements, 3 guides. Plotnine itself cannot add them alone to a plot. | run |
| What the slot expects | Not in the signatures. `position` is not a parameter of a geom. A theme key is `None` with no annotation. For 52 of 119 theme keys the docstring says which element. | run |
| Functions as parameters | No component takes a Python function from a recipe. `stat_function` takes text checked by a grammar. `fun_data` takes one of 5 names. `labeller` takes one of 3 names. `rescaler` and `oob` are refused. | read |
| What plotnine already accepts as data | Legend labels as list or dictionary, `labeller` as a name, `fun_data` as a name, `trans` as a name, `distribution` as a scipy name. | read |
| Paths as component arguments | None, in plot components and in the 68 Polars actions. The data path `source.path` has a shape check. | read |
| Polars text | 6 actions and the ID-reconciliation step take formula text (7 entry points). Allow-list, then `eval`. | read |
| Places that run recipe text as code | 2 `eval` calls in code. Recipe text reaches an evaluator in 5 kinds (2 `eval`, 2 inside plotnine and patsy, 1 Quarto). | read |
| Shipped use | `element_text`: 3 uses in 2 files. `position_dodge`: 3 uses. `position_fill`: 1. `position_stack`: 1. The other 10 objects: 0. `theme_custom`, the `guides:` block, `stat_summary` functions, `facet_labeller`, `stat_function`: 0. | read, grep |
| Decided already | Formula allow-list "for now", no time or size limit (D-0064). Names of values stay plotnine's own names (D-0214). Every plotnine object has its exact component and a modified one sits next to it (D-0210). Shortcut components removed (D-0211). Names `plotnine_`, `modif_`, `step_` (D-0091, D-0218). | ledger, read by the scout |
| Open | How the 15 objects are added (Q6). A function given as a parameter, for example `stat_summary` (Q9, N28). | ledger |

## Your three ideas, answered

### Idea 1: "I think those were part of a theme - so I suggest we have it under modified_theme no ?"

Plain answer: right for 4 of the 15. Not enough for the other 11.

- The 4 elements (`element_text`, `element_line`, `element_rect`, `element_blank`) are values of a theme setting. This is how plotnine works (run). It covers the 52 theme keys that take an element.
- The 8 positions are not in a theme. They are the value of `position` on a geom.
- The 3 guides are not in a theme. They are the value of `guides(...)` or of a scale's `guide`.
- The scientist: "one third of the answer, not a replacement". The architect: elements under a theme, positions and guides need their own owner.
- A note on the name. The exact plotnine `theme` is not registered today. Under the naming rule it would be `plotnine_theme`, and `modif_theme` only for what we change (architect).
- If every owner (theme, position, guide) has its own copy of the code, the two copies that exist now already disagree on unknown names. The architect: three owners would make five copies. If the owners share one reader, it is the same as the typed-value proposal below.

### Idea 2: "could we provide args as a dictionary of args in the recipe, then a check of allowed args for each decorator ... but will might be a security problem"

Plain answer: this is what the project does today for parameter names. It is sound. It stops one step too early.

- Today: a recipe gives `params`, and the checker refuses a name that the component does not take (PS04, with "did you mean").
- The weakness is not the dictionary. The check stops at the names. A name that is allowed can still carry a dangerous value.
- The list of such parameters is small and known: `format_string`, `rc`, `fname`, `adjust_text`, `qhull_options`, `figure_size`, `dpi` (architect, run).
- So: only for those parameters it is a security problem, and the fix is a decision for each one: allowed, refused, or limited.
- Suggestion (architect, scientist, developer): keep the dictionary and add a kind or type per parameter (a position, an element, a guide, a number, a name from a list). This is the typed-value proposal.

### Idea 3: "would there be a way to forbid functions, expressions, import modules and files to read ... but I guess it still would be very extensive"

Plain answer: you are right that such a list is very long. The viewpoints say: do not build it. Build the opposite.

- A list of forbidden things must be complete against Python, its standard library, numpy, pandas, matplotlib, scipy and every future version. It can never be shown complete.
- The evidence is in this project. The Polars check forbids every method that takes a function. It was generated from the library. It still missed two members (`deserialize`, `from_json`), because their danger is a path and a pickle, not a function. 2 of 412 (run).
- The opposite is a list of allowed values. For plotnine it is about 70 entries (15 objects, 13 label functions, 10 breaks functions, 3 labellers, and a small table of ours). It can be generated from the library and tested against it. Everything not in the list is refused by default.
- So there is an answer to "we need to find a solution": invert the list. This is the architect's and the scientist's view (both mark the deny-list "reject" or "do not use").

## The approaches, with the same four examples

The four cases, written in YAML for each approach:

1. Rotate the labels of the x axis by 90 degrees, size 6.
2. Bars side by side, with a dodge width of 0.5.
3. A legend in two columns.
4. Error bars with the mean and the standard error.

Naming is not part of this question. The rename rule (`plotnine_`, `modif_`) is decided but not built, so I write the names as they are today. The examples are my rewriting of the examples in the viewpoint files. Where I added one, I say so.

### Approach 1. Typed value `{name, params}` in the slot where plotnine takes it

Proposed by: the scientist (approach 1), the developer (way B), the user (way B).

```yaml
# 1 rotate x labels, 90 degrees, size 6
- name: theme_custom
  params:
    axis_text_x: {name: element_text, params: {angle: 90, size: 6}}
# 2 bars side by side, width 0.5
- name: geom_bar
  params:
    position: {name: position_dodge, params: {width: 0.5}}
# 3 legend in two columns
- name: guides
  params:
    fill: {name: guide_legend, params: {ncol: 2}}
# 4 error bars, mean and standard error (a name, as today; see "Functions as parameters")
- name: stat_summary
  params: {fun_data: mean_se}
```

- This form exists today in two places only: `theme_custom` for elements and the `guides:` block for guides.
- Can say: everything plain-data at these slots.
- Cannot say: a parameter that is itself a library object (a margin object, a random-state object; an integer seed is fine).

### Approach 2. One-key short form, and the slot-implied short form

Proposed by: the architect (design A, marker choice ii), the scientist (approach 2).

```yaml
# architect's one-key form: the key is the plotnine name
- name: theme_custom
  params: {axis_text_x: {element_text: {angle: 90, size: 6}}}
- name: geom_bar
  params: {position: {position_dodge: {width: 0.5}}}
- name: guides
  params: {fill: {guide_legend: {ncol: 2}}}

# scientist's slot-implied form: the slot knows the class
- name: theme_custom
  params: {axis_text_x: {angle: 90, size: 6}}
- name: geom_bar
  params: {position: {dodge: {width: 0.5}}}
- name: guides
  params: {fill: {legend: {ncol: 2}}}
```

- Case 4 is the same as in approach 1, or a named function (approach 5).
- The architect's reason against `{name, params}`: it collides with a legal label mapping whose categories are called `name` and `params` (reasoned). The one-key form has no collision unless a category is spelled like a function name.
- The slot-implied form is shorter, but the table "slot to class" must be generated and tested. The element type of a theme key is only in the docstring (read).

### Approach 3. A section per owner, plain keys (your idea 1 made general)

Proposed by: you (idea 1); written out in the developer (way C) and the user (way C).

```yaml
# 1
theme:
  axis_text_x: {angle: 90, size: 6}
# 2
position on the layer: {dodge: {width: 0.5}}
# 3 (my reading of the same idea; the viewpoints did not write it)
guides:
  fill: {ncol: 2}
# 4 not covered by this idea
```

- It is the shortest to write.
- The user viewpoint: it cannot be copied from the plotnine documentation. A novice would pass `angle` to `axis_ticks_x`, which needs a line and not a text, and fail.
- The developer: the whole table "key to object" is hand-written (52 theme keys, positions, guides). It drifts silently when plotnine adds a key. Highest risk of the typed forms.

### Approach 4. A short call text, parsed and never run

Proposed by: the scientist (approach 3), the architect (design C; C2 is the safe variant), the developer (way D), the user (way D).

```yaml
- name: theme_custom
  params: {axis_text_x: "element_text(angle=90, size=6)"}
- name: geom_bar
  params: {position: "position_dodge(width=0.5)"}
- name: guides
  params: {fill: "guide_legend(ncol=2)"}
- name: stat_summary
  params: {fun_data: "mean_se"}
```

- The text is read with `ast`, and objects are built by calling registered names only. There is no `eval` (C2). The scientist ran it: `__import__('os').getcwd()`, `open('/etc/passwd')`, a lambda and `9**9**9` were refused. A typo `element_text(angel=90)` is accepted by the parser and must still go through the parameter check.
- For: easiest to copy from the plotnine and ggplot2 documentation. One line.
- Against: a second language to document and test. Quoting in YAML. A form cannot show fields for a parameter inside a string. The user viewpoint: it feels like code, and one would wonder whether it runs. The developer: the repository already had defects from text checks (five kinds of recipe text reach an evaluator).

### Approach 5. Named functions and named choices, with data parameters

Proposed by: the scientist (approach 4), the architect (design D), the developer (way E), the user (way E).

```yaml
# 4 error bars: a name from a shipped, tested list, with data parameters
- name: stat_summary
  params:
    fun_data: {name: mean_sem, params: {ddof: 1}}
# 1 as a named choice (user viewpoint): hides the numbers
x_labels: rotated
```

- The scientist ran a list of three summaries and compared with independent numbers: `mean_sem` 4 plus or minus 1.5811 (reference 1.5811), `mean_ci_t` half-width 4.3899 (scipy 4.3899), `median_iqr` 3.0 with 2.0 to 4.0. Missing values dropped, n recorded, n below 2 gives a missing value, not a zero-width bar.
- The user viewpoint: `rotated` does not say 45 or 90 degrees or which size, so it cannot reproduce a published figure. Allowed only if each name expands visibly into approach 1.
- The names `mean_sem`, `summary_mean` and so on are placeholders in the sources. They are not registered names.

### Approach 6. Compute in the data, then plot the columns

Proposed by: the scientist (approach 5).

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

- Case 4 only. Cases 1 to 3 are not touched by this approach.
- Run: SE 1.581139 with n of 5, and `geom_pointrange` drew it.
- Gain: the numbers behind the bars are a table the user can see, the export holds them, a reviewer recomputes them, and n is visible (plotnine's `stat_summary` never shows n).
- Loss: a bootstrap interval per group is not expressible with an allowed formula. More steps to write.

### Approach 7. A script file, or an extension module, named by a hash

Proposed by: the scientist (approach 6, script file), the architect (design F, a module installed by the deployment).

```yaml
functions: {file: my_summaries.py, sha256: 9f2c...}      # scientist's form
- name: stat_summary
  params: {fun_data: {function: my_summaries.mean_trimmed, params: {trim: 0.1}}}
# architect's form: a module installed by the operator, named in the recipe
fill: {ext_lab_theme.nudged_dodge: {width: 0.5}}
```

- Can say everything Python can. It is the only way to "use all Python options" literally.
- It runs code with the rights of the app. A hash proves the file is the same one, not that it is safe. A recipe or bundle from another institute could carry or name the code.
- It contradicts the rule "no code from recipe text" (see the missing ledger line) and ADR-071 layer 1, unless you change that rule. Scientist: only as a separate trusted mode, a different product decision. Architect: defer; decide after the data forms show what stays out of reach.
- The scientist did not build or run it (reasoned).

### Approach 8. Pass everything through and forbid the dangerous (your idea 3)

Proposed by: you. Examined by the scientist (approach 7) and the architect (design H). Rejected by both, with the evidence under idea 3.

### Approach 9. Layers as today (the baseline)

Proposed by: nobody; it is the present state. Developer (way A), user (way A), architect (design G).

```yaml
- name: geom_bar
- name: position_dodge
  params: {width: 0.5}
- name: element_text
  params: {target: axis_text_x, angle: 90, size: 6}
- name: guide_legend
  params: {mapping: fill, ncol: 2}
- name: stat_summary
  params: {fun_data: mean_se}
```

- Works for the demo. The seven differences stay.
- The developer: the rule "both the modif and the plotnine original" (D-0210) cannot be met, because no original exists for these 15. The user viewpoint: dodge before the bar, or two text styles on one axis, gives silent mistakes, and the HOME user sees none of it.

### Also looked at, and not recommended

| Option | Why not | Who |
|---|---|---|
| YAML tags, for example `!position_dodge {width: 0.5}` | One existing loader turns any tag into nothing (read, scout). Tags are lost in JSON stores, editors and the Blueprint. | scientist, architect |
| Polars JSON serialisation of an expression | Not stable across Polars versions (docstring). Not human-readable. Loading a plan with a Python function uses pickle. Same attack surface as security finding 1. | scientist (run), architect |
| A second shared expression language (CEL, Vega style) | A new dependency. 16 shipped recipes use `pl.` text and would change. From memory for CEL, Starlark, JSON-e. | scientist |

### The table

Cost figures are estimates of the viewpoints.

| Approach | Proposed by | Cases covered | What is lost | Security | Cost (estimate) | For and against |
|---|---|---|---|---|---|---|
| 1 Typed value `{name, params}` | scientist, developer, user | 1, 2, 3 | Parameters that are library objects | Safe if the slot refuses an unknown name and D6, D7 are removed first | Developer 9 to 11 days incl. the Blueprint form (form code not read). Architect ~1000 lines, 3 to 4 builder sessions, Blueprint not estimated. | For: scientist, developer, user. Against: the architect prefers the one-key form. |
| 2 One-key or slot-implied short form | architect, scientist | 1, 2, 3 | A second spelling if the long form stays; a table to generate and test | As approach 1 | As approach 1 (architect's design A) | For: architect. Scientist: best for reading, more to generate. |
| 3 A section per owner | you (idea 1) | 1, 2, 3 as separate owners | Case 4; functions | Weak if each owner copies the check | Developer 8 to 10 days; architect ~80 lines per owner | Against: developer (highest drift risk), user (cannot copy from the plotnine docs). Architect: only if owners share one reader. |
| 4 Call text, parsed | scientist, architect, developer, user | 1, 2, 3, 4, and Polars | A second grammar to document | Without `eval`, strong; with check then `eval`, the gap of security finding 1 | Architect ~400 lines for the no-`eval` version; developer 12 to 14 days | For: user (copy from the docs). Against: developer (two syntaxes), user (feels like code, no form fields). |
| 5 Named functions | scientist, architect, developer, user | 4 | A function nobody registered | Safe if each entry is data-only and tested | Developer 0.5 to 1 day per family; architect ~200 lines plus a decision | For: scientist, architect. Developer: later, separate build. User: only if names expand visibly. |
| 6 Compute in the data | scientist | 4 | Bootstrap CI; `after_stat`; more steps | Lowest at the plot | no separate figure | For: scientist. Not a full answer. |
| 7 Script file or extension | scientist, architect | all | nothing | Code by design; trust moves to the operator | Architect ~400 lines | Against now: scientist, architect. |
| 8 Pass through and deny-list | you | all in theory | nothing in theory | Does not hold | endless | Against: all. |
| 9 Layers as today | status quo | what is written | Seven silent differences remain | As today | 0 | The demo works. |

## Functions as parameters

Open in the ledger (Q9, N28). Today no recipe value can be a Python function. A recipe cannot say `fun_y: mean` as a function.

The scientist's list of what a scientist in this field needs:

| Need | Today in plotnine as data? | What the scientist proposes |
|---|---|---|
| Mean with standard error | `mean_se` is population variance (flag above) | A named summary with the variance rule shown, or compute in the data |
| Mean with SD, mean with 95% interval (t) | Named ones exist (`mean_sdl`, `mean_cl_normal`) | Check against scipy before trusting |
| Mean with bootstrap interval | `mean_cl_boot`, unseeded | A named one with a required seed |
| Median with quartiles, median with range | `median_hilow` is a 95% interval by default (reasoned, not run), not quartiles | A named one, or compute in the data and name the interpolation |
| Proportion with a Wilson or exact interval | Not in plotnine | A named one (arithmetic in data is long) |
| Percent, thousands, scientific labels | `label_custom("{:.0%}")` works (run), but a format string is a small language | A named list, or a restricted format |
| Log breaks, date labels | A list of breaks and the strings `date_labels="%Y"` are plain data (run) | Plain data is enough |
| Legend text | Dictionary (run), with the key check | Plain data with the check |
| Facet label style | One of three names | The name |

The scientist's count: about ten registered entries are enough for these needs. Two thirds are already plain data in plotnine or can be computed in the data.

The architect splits the same thing in two sources:

1. Library functions that return a function from data (13 label functions, 10 breaks functions, 3 labellers). They can be generated from the library.
2. A table of ours, for functions the library takes only as Python objects (`fun_y`, `fun_ymin`, `fun_ymax` of `stat_summary`, and `stat_function`). Each entry is a scientific choice, not a technical one.

What is lost with a small list: a function nobody registered (a trimmed mean, a custom score). The scientist: it can still be computed in a Polars step if the allowed formula can say it. A label that joins two columns is a column, so it is not lost.

The choices hidden in such a function. Each must be written in the recipe or shown to the user:

- Sample or population variance (divide by n minus 1, or by n).
- What happens to a missing value: skipped by the mean, counted in n or not.
- A seed, for anything random.
- The interpolation of a quantile.
- What a group of one value gives (a missing value, not a zero-width bar).

These are yours to decide (architect: "She decides, the app shows the policy"). No decision exists (Q9, N28). Nobody in the sources proposes to decide it for you.

## The Polars side

The question: keep the checked formula text, or something else?

- **Keep the text for writing** (scientist, developer, user). The scientist converted five formulas to nested dictionaries (run): 14 and 17 lines of YAML for what is one line of text. A reviewer reads the one line. A string-method chain did not convert in the prototype. You accepted the allow-list "for now" (D-0064).
- **A data form only as a view.** The scientist: show the parsed tree (which function, which columns), not as the recipe language. The user viewpoint: write the text, and show the allowed functions and the parsed result beside it. Three nested boxes for a division are slower than one line.
- **Interpret the text without `eval`** (architect, design C2). The text is read by `ast`, and objects are built by calling registered members only. A node type with no code in the interpreter cannot run, whatever the check missed. A prototype gave the same expression as the present code on 15 of 15 shipped-style formulas (run), and refused the attacks (run). About 400 lines, replaces the two `eval` calls (estimate). The scientist and the developer do not propose this. The developer: Polars as data is large (7 entry points) and not needed for the demo; a later, separate decision.
- **Serialised expressions as input:** rejected, see the table.
- **What the scientist asks to add to the text form** (run unless marked):
  1. Seeds: require a seed for `shuffle` and `sample`.
  2. Quantile: make the interpolation visible or required.
  3. The check says which columns a formula reads and which it creates. This worked in a test (`meta.root_names()`, `meta.output_name()`).
  4. Record the Polars version with the result.
  5. `repeat_by` with a very large number is accepted. A memory bomb passes. You accepted "no size limit now" (D-0064), so it is recorded, not a new question.
- **Also:** the structural rule for the allowed members (security finding 1).

## What the demo needs, and the link to the rename

**The demo** (developer): nothing. The demo recipe has one `geom_bar` plot, with no position, no element, no guide. Everything shipped works today. The demo would be touched only if the rename is built first (names change) or the layer form is removed (8 uses rewritten). The developer: freeze, and list D1 to D7 as known defects, not fixes. One caveat (reasoned): if the demo shows the Blueprint form for these objects, a user who wants a width on a dodge cannot write it as a value today. It works, but only as a layer.

**How this links to the rename of the plot components.** Names that values carry stay plotnine's own (D-0214). So a value `position_dodge` and a layer `modif_position_dodge` have no name collision. The value registry is separate from the registry of steps. The architect adds one test: no value name equals a step name.

**The smallest decision that unblocks the rename** (developer): one decision, not code. His sentence: for positions, elements and guides, the plotnine original is the typed value in the slot where plotnine takes it (three slots), and the layer form is `modif_`. Functions (approach 5) and Polars are decided separately. The rename can then register the `modif_` names for the 15, and the value build is queued with the wording of D-0210.

**Build separately.** The developer: two builds. The rename is a pure rename (many files, little logic). The value build is new logic (few files, much logic, the seed rule). In one branch, a mechanical diff would hide a logic diff.

**The half state, if the rename comes first.** The 15 would have `modif_` and no plotnine original. D-0210 forbids that state, and an existing test pins the opposite. It is acceptable only as a written open point with a removal task. The other order (values first, then the rename) removes the half state, about one week later (estimate).

**The picture test that must exist first** (developer). The existing golden test records tables, not pictures. It will not see a changed theme, position or element. The existing picture checks are the reproducible-render hash test (same input twice) and the gallery previews; what the previews compare was not read. A new test is needed before any migration: the old layer form and the new value form give the same picture (same hash), for the 8 shipped uses. A trap found by the developer: the heatmap recipe writes `element_text` before `theme_minimal`. Today `element_text` is applied last. A value written at the same place would be overwritten by the complete theme and the rotation would vanish. So the migration is not blindly mechanical. It must be checked by picture.

**A reproducibility trap in the value build** (developer, read and reasoned). The seed code looks for random layers only when `position` is a string. A value `position: {name: position_jitter}` would not be seen as random. No seed would be added. The jitter would differ on every render, silently. So the seed work and the checker work on the nested form are part of the build. The checker today looks only at top-level parameters. A nested value needs a recursive check.

**The value form is stricter than plotnine** (developer, run). Plotnine draws `theme(axis_text_x=element_line())` with no error. A value form with a slot check would refuse it. This is a new rule to document. A plotnine update can also break the slot table. A test must then fail loudly, and the table is updated by hand.

## Recommendation of the viewpoints (the viewpoints' recommendation, not a decision)

### What they agree on

1. Fix today's silent problems and the security findings first, whatever the choice.
2. Do not forbid; allow. A registry of allowed values and names, generated from the library and tested against it.
3. Plain data in the recipe. No code from recipe text. A script file (approach 7) is not part of this build.
4. For the 15 objects: the typed value in the slot is the plotnine original. Scientist, architect (design A), developer and user agree on the principle.
5. Remove the silent fallbacks D6 and D7 as part of it. A typed value is only as safe as the fallback beside it.
6. One way to write each thing. The user: two ways side by side confuse most. The developer: ADR-099 "one authoritative way" speaks for removing the layer form after the migration, with a removal note. That needs your decision.
7. Functions (approaches 5 and 6) and Polars as data are separate decisions and a later build.

### Where they differ

| Point | Who says what |
|---|---|
| How a typed value is written | Scientist, developer, user: `{name, params}` (already used by `theme_custom` and the `guides:` block, no loader change). Architect: the one-key form, because `{name, params}` collides with a label mapping whose categories are called `name` and `params`. The architect says the checker can refuse that case. |
| The Polars text | Architect: interpret without `eval` (C2) with the structural rule. Scientist and developer: keep the text and the allow-list as accepted for now, add the seed and quantile checks. User: keep the text, show the allowed functions. |
| Layer form after the build | Developer: keep as `modif_` for now, decide later whether to remove. Architect: D1 to D5 are removed only if the layer form is dropped (Q6 option C). User: one way only. |
| Functions | Scientist: a registry of about ten, plus compute in the data. Architect: library functions generated, plus a table of ours that needs your decision. Developer: leave out of this build. |
| Cost | Developer: 9 to 11 days with the Blueprint form (estimate, form not read). Architect: about 1000 lines, 3 to 4 builder sessions, Blueprint not estimated. Different units and scope. Neither is measured. |

### Order of build

0. Fix the silent defaults and security findings. Independent of your choice.
1. One decision: how a value is written, and the slot for the 15 (questions 3 and 4 below).
2. Build the value registry, the slot table and the drift test against plotnine (developer: opus, high).
3. Resolve values at the one place where every component is called. Rewrite `theme_custom` and the `guides:` block with no silent fallback (developer: sonnet, high).
4. The seed rule and the checker for the nested form, with tests that can fail: same picture twice, jitter without a seed refused (developer: opus, high).
5. In parallel, in its own worktree: the rename of the layer names (developer: sonnet for the bulk, reviewed by opus).
6. Before any migration: the picture-equality test for the 8 shipped uses.
7. Migration of the 8 shipped uses, the Blueprint object widget, the documentation. The documentation must show a table of where each object goes, the three examples (rotation, dodge, error bars) next to the plotnine call they equal, and what the app refuses with the message (user viewpoint).
8. Later, each its own decision: the functions registry, the Polars interpreter, an extension module.

What HOME shows for a refused object (user viewpoint): the plot is not drawn, no blank figure, and the page says in plain words what was not known, where in the recipe, and that the plot was not drawn, with the allowed choices.

## What you are asked

One numbered list. The fewest questions that let the work continue, most important first. Each can be answered by a letter or yes or no. The default is what the viewpoints suggest. A default is never a decision.

1. **Confirm the rule "no code is executed from recipe text"** (2026-11-13). The ledger has no line for it. Yes or no. Default: yes, so it is written in the ledger.
2. **What does "all Python and Polars options" mean for a recipe?**
   - A. Every library parameter that is plain data, and every library object by its name from a registry. No function written by the user.
   - B. A, plus a script file or an extension module for user-written functions (approach 7).
   - Default: A. B is a different security decision.
3. **How is a typed value written?**
   - A. `{name: position_dodge, params: {width: 0.5}}` (scientist, developer, user).
   - B. `{position_dodge: {width: 0.5}}` (architect).
   - C. Call text `"position_dodge(width=0.5)"`.
   - Default: A. The choice affects the checker, the form and the documentation, not security.
4. **For the 15 objects: is the plotnine original the typed value in its slot, with the layer form kept as `modif_`?** Yes or no. Default: yes. This is the smallest decision that unblocks the rename. If yes, the rename and the value build are two builds, and the picture-equality test comes first.
5. **Fix today's silent defaults before anything else?** Seed required for the bootstrap, shuffle and sample. The standard error with a stated variance rule. The quantile interpolation shown. Legend labels shown as a pairing, with a key check. Yes or no. Default: yes (D-0050). The details of each are yours to approve.
6. **Risky plain parameters: `rc` and `fname` (theme_matplotlib), `format_string`, `adjust_text`, `qhull_options`.**
   - A. Refuse `rc` and `fname`. Restrict `format_string` to a number format.
   - B. Allow all, as pass-through.
   - Default: A (architect, scientist).
7. **The Polars text: keep the allow-list and `eval` with the structural fix and the checks, or move to an interpreter with no `eval`?**
   - A. Keep, add the fix and the seed and quantile checks.
   - B. Interpreter with no `eval` (architect).
   - Default: A for now. The architect recommends B. The scientist and the developer do not. This can also wait.
8. **Is the path check made real?** The spec says the app passes the allowed folders (PA02). The code passes none. A. The app passes them, and the file is checked when opened. B. The spec is corrected. Default: A.
9. **A session zip whose key already exists: ask the user, refuse, or overwrite?** Default: ask the user (inform, do not choose).
10. **The global `!include` loader:** change it to a private loader per recipe? Yes or no. Default: yes, a defect with a clear fix.

### Can wait

- Which named functions exist and how they treat missing values, the variance rule and the seed (Q9, N28). Default: leave out of this build and bring the list to you before any is built. The scientist's list of about ten is a start, not a decision.
- Whether the layer form is removed after the migration, with a removal note (ADR-099 one authoritative way). Default: decide after the values work.
- A limit on figure size, dpi, `n`, `bins`, sample size. D-0064 says no limit now. The architect asks that you reaffirm it knowing the 50000 by 50000 pixel figure. Default: reaffirm, and record the number.
- A deployment extension module (approach 7, architect design F). Default: not now.
- The demo: nothing to do for this question.

## Not checked

- The Blueprint form code. The effort of the form widget (2 to 3 days in the developer's total) is a guess.
- What the gallery previews compare (pixels, hash, or existence), and whether any preview uses an element.
- Any payload with a Python function inside a serialised Polars expression. Not built, by choice. Code execution through `deserialize` is reasoned from the Polars documentation.
- The state of the security fix started on 2026-11-17. I did not check it.
- Other tools (Altair and Vega-Lite, R and ggplot2, dbt, CEL, Starlark, JSON-e): from memory, not installed, not run.
- Pictures. The viewpoints compared objects, numbers and labels, not pixels. The architect's seven cases were byte-identical PNGs against the direct plotnine call (run). The comparison of the old layer form and the new value form is not done.
- Versions: only plotnine 0.15.4, mizani 0.14.4, Polars 1.40.1, Python 3.14.10.
- Whether patsy or plotnine expose Python builtins to a smoother formula. The architect ran it with the evaluator alone (builtins visible) and through the factory (refused). The text check is then the only barrier.
- Whether the other loaders also ignore tags (read from the scout only).
- The scout did not read all ledger lines. The scientist did not search the ledger for the missing "no code" line.
- Counts repeat shared parameters. The 41% plain-data share is per component and counts a shared parameter such as `labels` 67 times. The "490 not readable" includes 244 theme keywords.
- Every effort figure is an estimate. The developer's and architect's costs are in different units and cover different scope.
- Where the sources conflict: six against seven differences (source lists seven); the scout said file reading is not reachable in the formula check, the architect's run showed it is; cost estimates differ; the marker for a value differs (architect against the others); the Polars interpreter is proposed by the architect only.

## Added 2026-11-17 (night): how others keep user-written formulas safe

Added chapter for `.claude/design/studies/scratch_records_2026-11/panel/recipe_arguments/REPORT_for_eve.md`. Date: 2026-11-17. Nothing was edited, built or decided.

Labels: **run** means I ran it here. **read** means I read it in a file. **web** means a search result read on 2026-11-17. **memory** means not checked.

#### 0. Anything that would change a decided behaviour

- **D-0030** says "formulas only from an allowed list of Polars functions (P9)". D-0064 says the allow-list "as built is accepted for now" and "no time or size limit now".
  - Option (a) below, text plus check, keeps both decisions as they are.
  - Options (b) and (c) keep the allow-list idea. They change how a formula is written in the recipe. I found no ledger line that decides the written form of a formula. Read: `.claude/knowledge/decision_ledger.md:59`, `:93`. The grep showed no other formula-form decision, but I did not read the whole ledger.
  - So (b) or (c) needs a new decision from you (D-0165).
- **Open item, not decided.** The spec marks `Expr.inspect` as refused by name: "PROVISIONAL, an agent's choice under D-0030 on 2026-11-17, to be confirmed by the owner" (`recipe_format_spec.md` section 15; `formula_check.py:104-106`). It waits for you.
- **Two points where the check accepts something that is not safe or not reproducible** (run, details in section 4):
  1. `shuffle()` and `sample(n=3)` pass the check and give a different table on each run. Your own rule is "the same data and recipe give the same result". The earlier report lists this as finding 4 of the scientist. No decision exists on seeds.
  2. A very large allocation is accepted, for example `repeat_by(10**12)` and `str.pad_start(4000000000)`. D-0064 says no size limit now. This is recorded, not new.
- **The check is a net with holes, not a proof.** The code says so itself (`formula_check.py:123-137`). Two holes were already found by people on 2026-11-17: `deserialize` and `inspect`. Section 1 shows that similar tools had similar holes, and they were fixed in later versions.

#### 1. How comparable projects keep user expressions safe, and how they failed

Short rule from the sources: a list of what is allowed works better than a list of what is forbidden. A list still has holes. The holes appear where the tool lets text run through Python's own text-formatting or attribute lookup.

**OWASP and CWE-95 (eval injection).**
- The advice is to remove dynamic code execution if you can. Replace it with parsers, mappings or an allow-listed interpreter. If you must use eval, check the input strictly and sandbox it. [web: https://wiki.owasp.org/index.php/Direct_Dynamic_Code_Evaluation_('Eval_Injection') and https://dipsylala.github.io/FlawFixingGuidance/CWE-95, read 2026-11-17]. The search showed mirrors of this text. I did not open the current owasp.org page.
- Your app already follows the "allow-list" part and the "second layer" part (empty builtins, `formula_check.py:386-395`, read).

**Restricted AST evaluators (they parse the text, then walk it).**

| Tool | Real advisories (web, 2026-11-17) |
|---|---|
| asteval | CVE-2025-24359, GHSA-3wwr-3g9f-9gc7. A crafted format string leaves the sandbox. Fixed in 1.0.6. Score 8.4. https://advisories.gitlab.com/pypi/asteval/CVE-2025-24359/ |
| simpleeval | CVE-2026-32640, GHSA-44vg-5wv2-h2hg. Chained attribute lookups on allowed objects reached `os` and `sys`. Fixed in 1.0.5. Scores differ by source (8.7 to 9.8). https://advisories.gitlab.com/pypi/simpleeval/CVE-2026-32640/ |
| RestrictedPython | CVE-2023-41039 (sandbox escape through `format`). CVE-2023-37271 (stack frame escape). CVE-2026-76825 (escape when the policy exposes `string.Formatter`; fix in 8.4). https://cvepremium.circl.lu/vuln/cve-2023-41039 and https://advisories.gitlab.com/pypi/restrictedpython/CVE-2026-76825/ |

**Template sandboxes.**
- Jinja2 sandbox: CVE-2024-56326, GHSA-q2x7-8rv6-6q7h. An indirect reference to `str.format` ran Python code. Fixed in 3.1.5. https://advisories.gitlab.com/pypi/jinja2/CVE-2024-56326/ [web]. Sources disagree on severity (5.4 to 7.8).
- dbt uses Jinja. Its own sandbox status I did not check (memory).

**Dataframe tools that take user text.**
- pandas `query` and `eval`: the pandas documentation now warns that `query()` can run arbitrary code like `eval()`. The CVE for it (CVE-2024-9880) is disputed. https://nvd.nist.gov/vuln/detail/CVE-2024-9880 and https://security.snyk.io/vuln/SNYK-PYTHON-PANDAS-8549481 [web].
- Downstream, applications that pass user or model text to it were hit: CVE-2023-39662 (LlamaIndex) and CVE-2026-25481 (Langroid). In Langroid, an allow-list of DataFrame methods was bypassed by chaining allowed methods to reach the `eval` builtin. Fixed in 0.59.32. https://advisories.gitlab.com/pypi/langroid/CVE-2026-25481/ [web].
- This last case matters for you. It is the same shape as your design: a list of allowed methods on a dataframe object. The lesson is that "allowed method" must also mean "reaches nothing outside the data".
- numexpr: the search did not describe numexpr itself. One report said both engines worked in its test [web, weak]. Treat as not checked.

**Structure-based and small-language tools (not searched, memory).**
- Vega expression language: its own parser, an allow-list of functions, no access to the page's objects. Safe by design, but it is a language someone has to maintain.
- JSON-logic: operators are plain data, no text runs. Lines are long.
- Ibis and Polars SQL context: build expressions from structure or SQL text. The SQL context can read files if the table names allow it. Polars `pl.SQLContext` and `pl.sql_expr` exist at module level (run, section 2); your check refuses both because they are not on `MODULE_FUNCTIONS`.

**What this means in short:** every tool that runs real Python on a text got a real advisory. The tools that never run text as Python (structure forms, own parsers) have no such record in my sources. I did not search for advisories on them.

#### 2. What Polars can reach beyond the data (installed Polars 1.40.1, run)

Method: I listed the module names and the `Expr` members and namespaces, then called your own functions `refused_members()` and `_allowed()`. Script: `tmpAI/panel/formula_safety/introspect.py` (scratch).

**At module level (`pl.<name>`).** The app allows 38 names (`MODULE_FUNCTIONS`, `formula_check.py:55-62`). The other 161 callables of `pl` are refused by the check, including all of these:
- Reading files: `read_csv`, `read_parquet`, `read_json`, `read_ndjson`, `read_excel`, `read_ods`, `read_avro`, `read_ipc`, `read_delta`, `read_database`, `read_database_uri`, `read_lines`, `read_clipboard`.
- Scanning files: `scan_csv`, `scan_parquet`, `scan_ndjson`, `scan_ipc`, `scan_delta`, `scan_iceberg`, `scan_lines`, `scan_pyarrow_dataset`.
- SQL: `SQLContext`, `sql`, `sql_expr`.
- Global state: `Config`, `StringCache`, `enable_string_cache`, `thread_pool_size`, `set_random_seed`, `register_extension_type`.
- Writing is not at module level. It is on frames (`write_*`, `sink_*`), and a formula does not reach frames.

**On `Expr` (218 public names).** The check allows 200 in `expr`. It refuses these (read from the output):

| Member | What it does | Reason given by the check |
|---|---|---|
| `deserialize`, `from_json` | build an expression from a file or serialised data | reads outside data |
| `register_plugin` | loads a native library | loads outside |
| `map_batches`, `map_elements`, `pipe`, `rolling_map`, `list.to_struct`, `arr.to_struct`, `name.map`, `name.map_fields` | call a Python function | takes a function |
| `meta` (whole namespace; it also has `serialize`, `write_json`, `show_graph`) | read or write expression structure | refused by name |
| `inspect` | prints the column with a text run through `str.format` | refused by name |
| `ext` | extension namespace | not an expression method |

- Polars says about `register_plugin`: "highly unsafe as this will call the C function loaded" (run, docstring of the installed version).
- Polars documents `deserialize` as reading "a path to a file or a file-like object". The pickle warning for serialised Python functions is from the earlier report, which read the Polars documentation. I did not build a payload.

**Allowed today and worth knowing** (run, names confirmed in `_allowed()`):
- `sample`, `shuffle` (random, not reproducible without a seed).
- `repeat_by`, `reshape` (can allocate a lot).
- `str.json_decode` (can raise `PanicException`, not caught by `except Exception`; this is open item (a) in the spec, `recipe_format_spec.md` around line 806, read).
- `bin.decode`, `hash`.
- `list.eval` and `arr.eval` (allowed; they need `pl.element()`, which is not allowed, so they are mostly unusable).
- `str.json_path_match`, `struct.json_encode`.

**Words found in the documentation of allowed members** (run): `path` in `set_sorted`, `http` in many regex examples, `url` in `str.extract`, `json` in the JSON members. These are examples and descriptions, not file access. I did not read each member's behaviour.

**Which the allow-list names today, in one line:** it names 38 module functions and 200 `Expr` members plus the namespaces `str`, `dt`, `list`, `arr`, `cat`, `struct`, `name`, `bin`. It does not name anything that reads files, loads libraries, runs a Python function, or runs SQL (run on 60 hostile lines, section 4). It does not stop random, large or panicking members.

#### 3. The comparison table

Three real formulas from the shipped recipes (read, `config/data_analysis_recipes/pipelines/`):
- **F1** (`1_test_data_ST22_dummy/wrangling/QA_population_zscore.yaml:18`): a z-score.
- **F2** (`2_test_data_ST22_dummy/assembly/AMR_Profile_Joint.yaml:38`): multi-resistant flag.
- **F3** (`1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml:14`): resistance points with `when`, `then`.

The grep for `expression:` in `config/` finds nothing. The recipes write formulas under `named_exprs:` with `pl.col`. There are 19 such lines in the shipped pipelines (grep, run).

##### How each formula looks

**(a) Text plus check (today).**
```
n50_zscore: (pl.col('n50') - pl.col('n50').mean()) / pl.col('n50').std()
is_multi_resistant_bool: pl.col('predicted_phenotype_clean').drop_nulls().n_unique().over('sample_id') > 1
resistance_points: pl.when(pl.col('value') == 'Susceptible').then(pl.lit(0)).when(pl.col('value').cast(pl.String).str.starts_with('unknown')).then(pl.lit(None)).otherwise(pl.lit(1))
```
3 lines. One line per formula.

**(b) Nested YAML structure.** The names and shapes below are my illustration. They are not a design, only the size.
```
n50_zscore:
  div:
    - sub: [{col: n50}, {mean: {col: n50}}]
    - std: {col: n50}
is_multi_resistant_bool:
  gt:
    - over:
        expr:
          n_unique:
            drop_nulls: {col: predicted_phenotype_clean}
        by: sample_id
    - 1
resistance_points:
  when:
    - if: {eq: [{col: value}, Susceptible]}
      then: 0
    - if: {starts_with: [{cast: [{col: value}, String]}, unknown]}
      then: null
    - else: 1
```
About 22 lines for the three. The earlier report says the scientist found 14 and 17 lines for what is one line of text (`REPORT_for_eve.md` section "The Polars side"), the same order of size.

**(c) Own small language.**
```
n50_zscore: (n50 - mean(n50)) / std(n50)
is_multi_resistant_bool: n_unique(drop_nulls(predicted_phenotype_clean)) over sample_id > 1
resistance_points: if value == 'Susceptible' then 0 elif starts_with(str(value), 'unknown') then null else 1
```
3 lines, a bit shorter than (a). Illustration only. I did not design the grammar.

##### Table

| | (a) Text plus check | (b) Structure in YAML | (c) Own parser for a small language |
|---|---|---|---|
| **Safety** | Good if the check holds. Today's check refuses all 60 hostile lines of section 4 except the ones about size and randomness. It is a net with holes (`formula_check.py:123-137`); two holes found on 2026-11-17. Text is run by Python `eval` with empty builtins as a second layer (`:386-395`). The tools in section 1 that run Python on text all got advisories. | Strongest. A name not on the fixed list cannot run, because there is no code that handles it. No text is run. | Strong. Same idea as (b), and it is a smaller surface than Python. The parser itself must be written and tested. A parser bug is possible. |
| **Length to write** | 1 line per formula. | About 5 to 8 lines per formula. Long `when` chains are worst. | 1 line. Slightly shorter than (a). |
| **How it reads in a recipe** | Looks like the Polars and R-style code a data scientist knows. A reviewer can copy it into Polars. | Hard to read at a glance. Nesting hides the order of operations. | Reads like a formula. Differs from Polars; a reviewer must learn it. |
| **Work to build (estimate, not measured)** | Done. Keep testing it on each Polars upgrade (the walk tests do this). | Large. A table of every allowed method with its arguments, a reader, tests, a migration of 19 shipped formulas, and a new help in Blueprint. Many days (guess). | Large. A grammar, a parser, an evaluator, error messages, tests, migration, help. Similar to (b), maybe more. Many days (guess). |
| **Effect on decided points** | Keeps D-0030 and D-0064 as they are. | Keeps the allow-list idea of D-0030. Changes the written form, which needs a new decision (D-0165). Breaks every recipe and bundle that holds text formulas. | Same as (b). A new language also changes the "same data and recipe give the same result" story: a result now depends on the app's own parser version. |
| **What the architect of the earlier report proposed** | | | A fourth way is in that report: keep the text, but read it with `ast` and build the expression by calling registered members only, with no `eval` (about 400 lines, run on 15 formulas, `REPORT_for_eve.md` section "The Polars side"). This keeps the written form of (a) and removes the `eval` call. I did not re-check it. |

I did not test (b) or (c) on the formulas. The formulas are illustrations I wrote by hand.

#### 4. Test idea: hostile formulas

Method: `tmpAI/panel/formula_safety/hostile.py` (scratch). I called only `formula_problems()` from `libs/utils/src/utils/formula_check.py`. I did not evaluate any of these. Result for each line: REFUSED or ACCEPTED by today's check.

The test should assert that every line marked "must be refused" is refused. Lines marked ACCEPTED are the gap list.

**Attribute walking**
1. `pl.col('a').__class__`: reach the class. REFUSED (underscore).
2. `pl.col('a').str.__class__.__mro__`: walk the class tree. REFUSED.
3. `pl.Expr.__subclasses__()`: list all classes. REFUSED (`pl.Expr` not allowed).
4. `pl.col('a').__init__.__globals__`: read module globals. REFUSED.
5. `pl.os.system('id')`: reach `os` through `pl`. REFUSED.
6. `pl.sys.modules`: reach loaded modules. REFUSED.

**Dunder access**
7. `().__class__.__bases__[0].__subclasses__()`: classic escape. REFUSED.
8. `pl.__builtins__`: reach builtins. REFUSED.
9. `pl.col('a').__reduce__()`: pickle hook. REFUSED.
10. `pl.__spec__.loader`: reach the module loader. REFUSED.
11. `pl.col('a').__getattribute__('x')`: lookup by name. REFUSED.

**Format strings**
12. `'{0.__class__}'.format(pl)`: format string walks attributes (the shape of the asteval and Jinja advisories). REFUSED (`format` is not an expression method on a string).
13. `pl.col('a').inspect('{0.__init__.__globals__}')`: same trick, on Polars `inspect`. REFUSED (by name).
14. `pl.format('{}', pl.col('a')).__class__`: format then attribute. REFUSED.
15. `f'{pl.__file__}'`: f-string reads a name. REFUSED (JoinedStr).

**Comprehension scopes**
16. `[c for c in ().__class__.__mro__]`: comprehension with attribute walking. REFUSED.
17. `[x for x in (1,2)]`: plain list comprehension. REFUSED.
18. `{k: v for k, v in [(1, 2)]}`: dict comprehension. REFUSED.
19. `(x for x in [1])`: generator. REFUSED.

**Lambda and Python functions**
20. `(lambda: __import__('os'))()`: lambda that imports. REFUSED.
21. `pl.col('a').map_elements(lambda v: v)`: per-row Python function. REFUSED.
22. `pl.col('a').map_batches(print)`: batch Python function. REFUSED.
23. `pl.col('a').pipe(print)`: pipe a function. REFUSED.

**Builtins**
24. `eval('1+1')`: eval. REFUSED.
25. `exec('import os')`: exec. REFUSED.
26. `open('/etc/passwd').read()`: file read. REFUSED.
27. `getattr(pl, 'read_csv')`: reach a function by name. REFUSED.
28. `print(pl)`: print. REFUSED.

**Imports**
29. `__import__('os').system('id')`: import a module. REFUSED.
30. `import os`: statement, not an expression. REFUSED (syntax error).
31. `pl.col('a') if True else __import__('os')`: hide it in a conditional. REFUSED.

**Serialised data**
32. `pl.Expr.deserialize('/tmp/x.json')`: build an expression from a file. REFUSED at the module level.
33. `pl.Expr.from_json('{}')`: build from JSON. REFUSED.
34. `pl.col('a').meta.serialize()`: write the structure. REFUSED.
35. `pl.col('a').str.json_decode(pl.Object)`: Polars raises `PanicException`; code that catches only `Exception` does not catch it. **ACCEPTED** (known open item (a) in the spec).
36. `pl.col('a').bin.decode('hex')`: decode bytes. **ACCEPTED**; harmless by itself (my reading, not tested at run time).

**File paths and SQL**
37. `pl.read_csv('/etc/passwd')`: read a file. REFUSED.
38. `pl.scan_parquet('/etc/shadow').collect()`: scan a file. REFUSED.
39. `pl.read_json('x.json')`: read JSON. REFUSED.
40. `pl.lit('/etc/passwd')`: a path as plain text. **ACCEPTED**; correct, since it is only a text value.
41. `pl.sql_expr('1')`: SQL text. REFUSED.
42. `pl.SQLContext()`: SQL context. REFUSED.

**Plugins and global state**
43. `pl.col('a').register_plugin(lib='/tmp/x.so', symbol='f')`: load a native library. REFUSED.
44. `pl.Config.set_tbl_rows(1)`: change the global setting. REFUSED.
45. `pl.col('a').ext.to('x')`: extension namespace. REFUSED.

**Very large allocations**
46. `pl.col('a').repeat_by(10**12)`: very large list. **ACCEPTED** (D-0064: no size limit now).
47. `pl.lit('a') * 10**9`: very large text. **ACCEPTED**. The check refuses a text constant multiplied (`formula_check.py` `visit_BinOp`), but not a call result.
48. `pl.col('a') ** 99999999`: huge exponent. REFUSED (exponent limit 100).
49. `pl.lit(10**10000)`: huge number built by power. REFUSED.
50. `pl.col('a')` plus `.abs()` 500 times: very deep chain. REFUSED (over 2000 characters).
51. `pl.lit('x'*5000)`: text multiplied. REFUSED.
52. `pl.col('a').cast(pl.String).str.pad_start(4000000000)`: 4 GB of padding. **ACCEPTED**.

**Randomness (not a security problem, a reproducibility one)**
53. `pl.col('a').shuffle()`: random order. **ACCEPTED**.
54. `pl.col('a').sample(n=3)`: random rows. **ACCEPTED**.

**Syntax tricks**
55. `pl.col('a') << 5`: shift operator. REFUSED.
56. `*pl.col('a')`: star expression. REFUSED.
57. `pl.col(*['a'])`: starred argument. REFUSED.
58. `pl.col(**{'name':'a'})`: keyword unpacking. REFUSED.
59. `pl.col('a').list.eval(pl.element())`: inner expression. REFUSED (`pl.element` not allowed, a limit not a danger).
60. `pl.col('a').list.eval(pl.col('a').map_elements(print))`: function hidden inside `eval`. REFUSED.

**Count:** 60 lines. 49 refused. 11 accepted: lines 35, 36, 40, 46, 47, 52, 53, 54. That is 8 lines, not 11. The correct count is: 52 refused, 8 accepted (run; I counted from the output list). Of the 8, only 40 and 36 are fine; 35, 46, 47, 52, 53, 54 are the gap list.

For the test, the "must refuse" group (everything refused above, in groups of attribute walking, dunder, format strings, comprehensions, lambda, builtins, imports, plugins, SQL, file readers) is 52 lines. A "known gaps, must stay visible" group holds 35, 46, 47, 52, 53, 54. That group needs your decision on seeds and size (no decision exists).

The existing test file already tests some of this (`test_formula_reads_no_outside_data.py`, read: file read, `inspect`, math function strings, the walk of every allowed member). I did not check which of my 60 lines it already covers.

#### 5. A suggestion for the reader (not a decision)

Facts first. I did not see a hole in the check that I could use. The check is also not a proof; the code says so (`formula_check.py:123-137`).
- **Option (a)** is the cheapest and is decided for now (D-0064). Its weak points are the two classes of danger that signature reading cannot see: members dangerous by effect (`inspect`), and members that panic or allocate.
- The earlier report's fourth way (parse the text, call registered members only, no `eval`) keeps your formulas as they are and removes one risk class: a name the check missed would then have no code to run. That is a middle way between (a) and (c). It is an estimate of about 400 lines from the earlier report. I did not test it.
- (b) and (c) cost most and change what recipe authors write.

What needs your word, because no decision exists: (1) require a seed for `shuffle` and `sample`, or refuse them; (2) confirm or remove `inspect` as refused by name; (3) whether `PanicException` from `json_decode` is a problem for you.

#### 6. What I did not check

- Primary advisory texts. I read search results only for the CVEs, never the GitHub advisory pages themselves. Scores and fixed versions differ by source and are quoted as the search showed.
- Vega expression language, JSON-logic, Ibis, Polars SQL context and dbt sandbox: from memory, no search.
- The numexpr claim about `query`: weak, from one search result.
- Whether the walk tests in `libs/utils/tests/test_formula_reads_no_outside_data.py` already cover my 60 lines. I read only the test names.
- Whether any of the 8 accepted lines is run by the app and what it costs at run time (not run; I did not call `evaluate_formula`).
- The reading of the `str.format` danger in `inspect` comes from the spec and code comments; I only confirmed it is refused.
- The size of work for (b) and (c) is a guess.
- The three formulas in forms (b) and (c) are written by me, not tested.
- Whether `scout`, panel or reviewer reports contradict the 2026-11-17 `inspect` fix. I did not read them.
- Polars version: 1.40.1 only. Python 3.14 per the earlier report; I did not check.

Files used (all read-only except my scratch in `.claude/design/studies/scratch_records_2026-11/panel/formula_safety/`):
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/utils/src/utils/formula_check.py`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/libs/utils/tests/test_formula_reads_no_outside_data.py`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/design/recipe_format_spec.md`
- `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/design/studies/scratch_records_2026-11/panel/recipe_arguments/REPORT_for_eve.md`
- Scratch scripts: `/home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/formula_safety/introspect.py` and `.../hostile.py`

Since this chapter was written: `pl.Object` is refused in formulas (D-0230) and `pl.element()` / `pl.field()` are allowed after a security review (D-0231); three more types that crash the JSON-decoding member are asked of Eve.
