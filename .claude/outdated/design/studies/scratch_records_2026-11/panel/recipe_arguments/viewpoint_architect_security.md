# Arguments and constructions in a recipe: software architect and security reviewer

Round 1, one viewpoint file, two sections kept apart. I recommend; Eve decides. Nothing was edited in the repository; scratch is `tmpAI/panel/recipe_arguments/architect/` (scripts and JSON listed at the end). Python 3.14.10, plotnine 0.15.4, polars 1.40.1, patsy 1.0.2.

Labels: **[run]** I ran it here; **[read file:line]** I read it here; **[memory]** from memory, not verified; **[reasoned]**. Tags: DECIDED / CONFIRM / OPEN / MINE.

---

## 0. Reported at once (a verified bug that also decides the question)

**F1. The formula allow-list admits `Expr.deserialize` and `Expr.from_json`. [run]**
- `libs/utils/src/utils/formula_check.py:95-102`: the allowed methods are "every public `Expr` method minus the ones that take a `Callable`". That is a deny-list of one property. Polars has two static methods on `Expr` that the property does not catch: `deserialize(source: str | Path | IOBase | bytes)` and `from_json`.
- Run 1: `formula_problems("pl.col('a').deserialize('<path>')")` returned `[]` (accepted).
- Run 2: through the real action `polars_with_columns`, `named_exprs: {b: "pl.col('a').deserialize('<scratch path>')"}` read a file from a path written in the recipe and returned the table `a*2`. The file was a benign expression I serialised in scratch.
- Run 3: `pl.col('a').from_json('<92 characters of JSON>')` is accepted and evaluated. The payload is inline, with no file.
- The installed Polars docstring says (run, `inspect.getdoc`): "This function uses pickle if the logical plan contains Python UDFs ... Deserializing can execute arbitrary code, so it should only be attempted on trusted data."
- I did NOT build a payload with a Python function inside. So: a file read from any path is proven; code execution is [reasoned] from the Polars documentation, not demonstrated.
- Entry points: 6 actions and the ID-reconciliation mutate (scout A5, 7 entry points; not re-counted).
- What no test catches: `libs/utils/tests/test_formula_check.py:132-137` pins that the Callable methods are denied. No test says "no allowed member takes a path, a file object or bytes, or is a static method" (grep `deserialize` in the tests: 0).
- Tag: against DECIDED D-0030 and ADR-071 layer 1 ("nobody may misuse it to run anything but data science"). D-0064 accepted the list "as built, for now"; that acceptance did not know this. CONFIRM that she wants it closed. Suggestion: the structural rule in section A.1 design C2 (a member is allowed by what it IS, not by one property it lacks). In my prototype the rule removes exactly these 2 of the 412 allowed members [run].

Other verified findings are in section 7.

---

# ARCHITECT

## A.0 Where the code is today (the distance)

- **Names: done.** `libs/viz_factory/src/viz_factory/parameters.py` (`exact_parameters`, `accepted_names`) reads every parameter name from plotnine; `arguments.py` hands the allowed names to the checker as plain data (PS04, `recipe_check.py:978-981`). 191 components, 186 have a readable list; 5 are free-form (`facet_labeller`, `facet_margins`, `facet_scales`, `facet_space`, `stat_identity`) [run].
- **Types: not done.** The reader keeps the annotation only to choose a widget (`SIMPLE_ANNOTATIONS`, `parameters.py:52`); the checker tests names only, plus the PS06 texts (`recipe_check.py:939-983`), values are judged when plotnine draws. I wrote a 40-line reader in scratch (resolves plotnine's aliases such as `ScaleLabelsUser`, which live in `plotnine/scales/_runtime_typing.py`). Result [run, `coverage.py`]: of 123 function-like components, 1321 (component, parameter) pairs; 548 are plain data only (41%), 239 admit a callable beside other forms, 44 need a library object, 490 could not be read to a set of forms (244 of those are the `theme(**themeables)` keyword names, counted for two components). Counts are per component, so a shared parameter such as `labels` counts 67 times.
- **63 of the 191 components are geoms and stats. They have no annotations at all**; plotnine gives only `DEFAULT_PARAMS`, 101 distinct names, 544 pairs [run]. Their types can only come from the default value (str 261, bool 97, None 96, int 41, float 29, tuple 12, dict 8) plus a hand overlay. The 96 whose default is `None` have no type.
- **Nested objects: 3 hand-written places, with defects.** `theme_custom` (`themes/core.py:323-340`, an if/elif chain, unknown element dropped silently), the plot-level `guides:` block (`viz_factory.py:380-398`, unknown name falls back to `guide_legend`, line 391), and `position_*` as a layer on the last layer (`positions/core.py:19-25`). The `position` of a geom takes only strings; `position: {name: position_dodge, params: {width: 0.5}}` fails with "Unknown position of type dict" (Q6 report, run there).
- **The 15 objects are exactly three base classes.** By `issubclass` on plotnine's `position`, `element_base` and `guide` I get 8 + 4 + 3 = 15, the same 15 as Q6 [run]. So a registry of values can be generated, not written.
- **What plotnine already accepts as plain data.** `labels` as list or dict, `labeller` as one of 3 names or a dict, `fun_data` as one of 5 names, `trans` as a name, `distribution` as a scipy name [read plotnine `facets/labelling.py:235-259`, `stats/stat_summary.py:~153`, `mizani/transforms.py:921-947`, `stats/distributions.py:32-40`]. Many "function as a parameter" cases already have a data form in the library itself.
- **Library version.** The root `pyproject.toml:14` pins `plotnine>=0.15.4,<0.16.0`; `libs/viz_factory/pyproject.toml:10` says `plotnine>=0.14.0` [read]. The export records python, polars, shiny and plotnine versions (`export_handlers.py:105-110`, read). The recipe itself carries no library version.

## A.1 The designs

Six named cases are written for each design. "Case 6" is a Polars expression as an argument. Names follow the decided rule: step names are prefixed (`plotnine_`, `modif_`, `step_`, D-0091, D-0218, DECIDED, not built); names written as VALUES stay plotnine's own (D-0214, DECIDED). The home of element values is the exact plotnine `theme`, which is not registered today (KNOWN_MISSING, the_22 report); Eve's idea 1 ("under modified_theme") would then be `plotnine_theme` for the exact call and `modif_theme` only for what we change.

### Design A. Typed value, one resolver, kind declared by the parameter (MINE, built on the hints; extends the existing `exact` mechanism)

A recipe value is plain data (text, number, boolean, null, list, mapping). A mapping with ONE key that is a registered value name is a typed value: the key is the plotnine name, the value is its parameters, nested to any depth. The registry of values is generated: the 15 objects by base class, the 13 `mizani` label factories and 10 break factories, the 3 labellers, plus a small table of named summary functions that is ours (see D). Each entry carries its parameters read from the signature (the reader that exists today), and a **kind** (`position`, `element`, `guide`, `labels_function`, `breaks_function`, `labeller`, `summary_function`). A parameter declares which kinds it takes; a position parameter takes a position, a theme key takes an element.

```yaml
# 1 position with arguments
- name: plotnine_geom_col
  params: {position: {position_dodge: {width: 0.5}}}
# 2 element as the value of a theme key (margin is a plain mapping, plotnine takes a dict)
- name: plotnine_theme
  params: {axis_text_x: {element_text: {angle: 45, hjust: 1, margin: {t: 10}}}}
# 3 guides(fill=guide_legend(ncol=2))
- name: plotnine_guides
  params: {fill: {guide_legend: {ncol: 2}}}
# 4 legend entry labels: list, dict (plain data, plotnine's own forms) or function
- name: plotnine_scale_fill_manual
  params: {values: ["#dd0000", "#00aa00"], labels: {x: Treated, y: Control}}
- name: plotnine_scale_y_continuous
  params: {labels: {label_percent: {scale: 0.01}}}
# 5 a function as a parameter (summary_mean is a name in OUR table, placeholder)
- name: plotnine_stat_summary
  params: {fun_y: {summary_mean: {}}, fun_ymin: {summary_min: {}}, fun_ymax: {summary_max: {}}}
- name: plotnine_facet_wrap
  params: {facets: g, labeller: {label_both: {}}}
# 6 Polars: text, see design C2
```

- **Proof it can be exact [run, `typed_prototype.py`, ~25-line resolver].** Seven cases (position, element with nested margin, guides, labels dict, labels function, `stat_summary` with three functions, labeller) each produced a PNG byte-identical to the direct plotnine call. Refusals: a misspelt name ("did you mean `position_dodge`"), a misspelt parameter (lists what is accepted), a non-data Python object. A value such as `width: {__import__: os}` is accepted by the resolver (it is data, never called) and plotnine would refuse it later: this shows "safe" and "valid" are two checks; types give the second.
- **One mechanism for both libraries, respecting Clear Lines** (`rules_runtime_environment.md` section 4). `libs/utils` is Tier 1: it may use polars and pyyaml (declared), it does not declare plotnine. So the walker, the error form, did-you-mean, the kind check and the dry run live in `utils` and take the registry as plain data, as `argument_catalog` does today (spec section 14). `viz_factory` builds the plotnine registry; `transformer` builds the Polars one. The checker in `utils` validates names, parameters and kinds without importing plotnine. The surface for Polars expressions is a chain (`pl.col('x').str.to_lowercase()`), which is awkward as nested mappings; so for Polars A shares the registry, checker and tests but the surface stays text (C2). Honest answer: one core, two surfaces.
- **Fit with `plotnine_` / `modif_` / `step_` and D-0210.** The exact value is plotnine's own name. A modified value is `modif_<name>` next to it (for example a label function with a documented default). No wrapper per case: the registry is generated and a test compares it to plotnine. For the 15, the unprefixed name leaves the step namespace (they cannot be added alone, Q6 section 1) and exists only as a value name; a test must check that no value name equals a step name. This is Q6 option B or C; CONFIRM with Eve that "exact component" for these 15 means exact value (D-0210 text: "every plotnine object has its exact component").
- **When plotnine or Polars adds or renames a parameter.** Names are read at import, so a renamed parameter makes an old recipe fail with did-you-mean (loud, good). A NEW parameter is accepted by name, and its type is read; if its type admits a callable or a path, the registry-walk test of section 8 must fail the build until someone decides. A changed default or changed meaning of the same name is not detectable; only the pinned upper version (`<0.16.0`) and the recorded version in the export cover it.
- **Checker, `ui_schema`, export.** Checker: new codes after PS04 (unknown value name, parameter not accepted, kind mismatch), same resolver in dry-run mode. `ui_schema`: one new widget `object` with `kinds: [...]` added to `WIDGETS` in `libs/utils/src/utils/ui_schema.py:20-32`, the vocabulary all registries, the form and the checker already share. Blueprint's widget code I did not read; its cost is not estimated. Export: add, for audit only and never read back, the resolved call as text (`position_dodge(width=0.5)`) next to the typed value; this is the "recipe, then what it became" record (MINE).
- **Recipe format change: YES** (a new value form in 5 parameter families). Spec section on DEC31 and `ui_schema` change; recipes written today stay valid, because they hold only strings there.
- **Cost (estimate, not measured).** About 1000 lines with tests: resolver and dry run in utils ~250, plotnine registry ~200, annotation reader ~100 (the prototype is 40), checker ~100, replace the three hand-written places (about -150), tests ~400. 3 to 4 builder sessions, plus Blueprint (unknown).
- **Marker choice, a consequence Eve should see.** Three ways to mark a typed value: (i) the existing `{name: ..., params: ...}` (used by `theme_custom` and the `guides:` block): it collides with a legal label mapping whose categories are called `name` and `params` [reasoned]; (ii) a one-key mapping whose key is a registered name (above): no collision unless a category is spelled like a function, and the checker can refuse that case when the parameter also takes a mapping; (iii) a YAML tag `!position_dodge {width: 0.5}`: unambiguous, but tags are lost in JSON stores (sessions, exports) and in `_TolerantLoader`, which ignores unknown tags (`data_analysis_recipe_validator.py:167-171`, scout) [reasoned for the loss].

### Design B. A section per owner, hand-coded (Eve's idea 1, generalised) (EVE, MINE as a variant)

Each owner takes typed values of its own kind, written separately: `theme` (elements), the geom's `position` (positions), `guides` and scale `guide` (guides).
- YAML: the same as A for cases 1 to 3. Cases 4 and 5 (functions) need a fourth and fifth owner.
- **What it covers:** elements 4 of 15 under a theme owner; positions 8 and guides 3 need their own owners. Idea 1 is right for plotnine's `theme(...)`, which is where elements live; it does not reach positions, guides or functions.
- **Cost of separate code per owner:** each owner repeats name check, unknown-name error, nesting, did-you-mean. Today's two copies already disagree on unknown names: `theme_custom` drops silently (D7), the `guides:` block falls back silently (D6). Three owners would make five copies. If the owners share A's resolver and each declares its kind, B is A.
- **Checker and form:** one rule per owner; a new owner is a new code path in the checker and the form.
- **Format change:** yes. **Cost:** about 80 lines per owner plus tests, cheap at first, grows per case [estimate].

### Design C. A small allow-listed text for construction (the formula checker generalised) (hint)

The value is written as text close to plotnine's code: `position: "position_dodge(width=0.5)"`, `axis_text_x: "element_text(angle=45, hjust=1)"`. A grammar check admits only registered names and data arguments.

**C1: check, then `eval`** (what `formula_check.py` does today, `evaluate_formula`, line 317-322). **C2: check, then interpret, no `eval`** (MINE, prototype in `interp_prototype.py`). C2 reads the text with `ast`, then BUILDS the object by calling registered members only; a node type with no code in the interpreter cannot run, whatever the check missed. Same 15 shipped-style formulas give the same Polars expression as `evaluate_formula` (15 of 15 [run]); the attacks (`deserialize`, `from_json`, lambda, comprehension, f-string, `__class__`, `len(...)`, `pl.read_csv`, `.meta`, `pipe`) are all refused [run].

```yaml
# plotnine side, case 1 to 3, 5
- name: plotnine_geom_col
  params: {position: "position_dodge(width=0.5)"}
- name: plotnine_theme
  params: {axis_text_x: "element_text(angle=45, hjust=1)"}
- name: plotnine_guides
  params: {fill: "guide_legend(ncol=2)"}
- name: plotnine_stat_summary
  params: {fun_y: "summary_mean", fun_ymin: "summary_min", fun_ymax: "summary_max"}
# case 6, Polars (already how it is)
- action: polars_with_columns
  named_exprs: {ratio: "pl.col('a').cast(pl.Float64) / pl.col('b').cast(pl.Float64)"}
```

- **One mechanism for both libraries:** yes, the cleanest answer: one text grammar engine with two namespaces (`pl.` and plotnine names). The Polars side exists; plotnine is a second namespace. It sits in `utils` for the same reason `formula_check` does.
- **For:** reads like plotnine/Polars code (D-0214, "same as Polars"); one surface; Eve's "use all python options" feels literal.
- **Against:** text in YAML is quoted text, with nested quoting for nested calls; the text must be parsed in the checker, the engine and the form; every new text place is a new place to defend; ADR-099 point 15 (DECIDED 2026-11-12) says "steps are built from named parameterised actions, never from formula text with user values" (for audit steps; the intent leans to data, CONFIRM whether it extends to plot values); Blueprint needs an expression editor per parameter that takes an object. C1 keeps the check-then-eval gap: the checker's idea of "allowed" and Python's evaluation are two readers (F1 is that gap).
- **Version change:** the grammar names are read from the registry; same as A.
- **Format change:** yes (text where today only strings). **Cost (estimate):** C1 about 300 lines; C2 about 400 (interpreter ~120 incl. Polars when/then states, replaces the two `eval` calls).

### Design D. Named functions with data parameters, for every place a library wants a callable (hint; partly MINE)

Two sources, not one:
1. **Library factories** that already return callables from data: `mizani` `label_*` (13) and `breaks_*` (10), plotnine labellers (3). `{label_percent: {scale: 0.01}}`. These are generated from the library, same registry as A.
2. **A table that is OURS** for functions the library only takes as Python objects: `fun_y`, `fun_ymin`, `fun_ymax` of `stat_summary` and `stat_summary_bin` (plotnine: `make_summary_fun`, a callable only, `stats/stat_summary.py:~160-180`), and `stat_function`. Each entry is a scientific choice, not a technical one: `np.mean(series)` on a pandas Series is `Series.mean`, which skips NA; a named function must state its NA behaviour (D-0050, "nothing changes a result silently"). This is the open question Q9 / N28 (OPEN, ledger :275, :310).
- It is a subset of A for the value surface; kept separate because source 2 needs Eve's decision on which functions and how NA is treated. `libs/utils` holds nothing; the table lives in `viz_factory` because it is plotnine-specific.
- **Format change:** yes. **Cost:** about 200 lines plus tests; the work is the decision, not the code.

### Design E. Data serialisation of expressions (Polars `Expr.meta.serialize`) (hint)

The recipe holds a serialised expression (JSON or binary) that the app deserialises.
- **Reject, with evidence.** F1 is exactly this: deserialisation is the attack surface (docstring: can unpickle Python functions). The JSON is not hand-written or readable, is "not stable across Polars versions" (docstring, run), and a Blueprint form cannot edit it. Plotnine has no equivalent.
- Useful only as an INTERNAL cache key or as a machine-written export record, never as recipe input. **Cost:** low code, high risk. No fit with ADR-099 or the readability rule.

### Design F. Premise change: a deployment-shipped extension module, by name and hash (hint; premise)

The recipe language stays closed (A/D). For "all Python" an operator installs a module in the deployment, registered by name, whose hash is recorded; a recipe says `{ext_lab_theme.nudged_dodge: {width: 0.5}}`. The recipe never contains code.
- **For:** satisfies "all Python options" without making the recipe a language; fits ADR-071 layer 2 (the deployment decides who deposits what, DECIDED 2026-11-15) and D-0030 (import is a separate function for an authorised person).
- **Against:** an extension IS arbitrary code, run with the app's rights; the trust moves entirely to the operator. Reproducibility needs the module to travel with the export or be pinned by hash, and a bundle from another institute that names an extension this deployment lacks must stop with a named missing module. A second engine is impossible through it. Hash proves it was not changed, not that it is safe (spec section 15, last paragraph).
- **Reconsiders:** the premise "the recipe is the whole program". Not decided anywhere.
- **Format change:** a new key and a deployment setting; **cost (estimate):** ~400 lines, loader, hash record in the export, bundle behaviour, tests, docs. Worth deciding only after A/D, when Eve sees what remains out of reach.

### Design G. One component per case (the status quo, continued) (baseline)

`theme_legend_position`, `guide_nrow`, `guide_ncol`, `guide_title` are this approach: each case is a hand-written component. The 22 own components (the_22 report) show the outcome: 14 `modif_`, 5 `step_`, 1 broken, 2 undecided, 10 exact duplicates, and defects (guide setters replace one another, D3 of that report). Cost grows with every case; D-0211 already asks to delete shortcuts. Kept in the table as the baseline that A to D replace.

### Design H. Pass everything through, forbid the dangerous (Eve's idea 3) (EVE)

Pass any parameter to the library and keep a list of forbidden functions, modules, files and arguments.
- **Evidence it does not hold [run]:** the project's own deny set for formulas is "every method with a Callable parameter" (F1). It missed `deserialize` and `from_json` because their danger is a path and a pickle, not a Callable. The deny set was a good-faith, generated list; it still left two members open out of 412.
- The list Eve fears ("a very extensive list") is real: Python, the standard library, numpy, pandas, matplotlib, scipy and every future release. Design A inverts it: the list is the finite set of registered values (about 70 entries here), and everything else is refused by default.

### Eve's idea 2 (args as a dictionary, checked against the allowed args per decorator)

This is what the project does today (`params` plus PS04). The weakness is not the dictionary; it is that the check stops at NAMES. A name that is allowed can still carry a dangerous value (section 5: `format_string`, `rc`, `fname`, `adjust_text`). A, B, C, D all add the second half: a type or kind per parameter, with a decision for each parameter that takes text the library interprets.

## A.2 Which silent differences each design removes

The Q6 report lists seven defects D1 to D7 (D8 is a note), not six; I map all seven. D1 to D5 are properties of the LAYER form (attach to the last layer, dedupe by name, element_text applied last). D6 and D7 are properties of two hand-written readers.

| Q6 defect | A alone | A + layer form removed (Q6 option C) | B hand-coded | C | D | E, F, G, H |
|---|---|---|---|---|---|---|
| D1 element_text then element_blank: blank lost | stays for the modif layer | removed (no layer) | stays | as A | n/a | none |
| D2 two element_text on one target: first lost | stays | removed | stays | as A | n/a | none |
| D3 element_text applied last whatever the order | stays | removed | stays | as A | n/a | none |
| D4 position layers deduped by name | stays | removed | stays | as A | n/a | none |
| D5 same dedupe for guides and elements | stays | removed | stays | as A | n/a | none |
| D6 `guides:` block turns an unknown name into `guide_legend` | removed (one reader, unknown name refused) | removed | stays unless owners share the resolver | removed | n/a | G keeps, H keeps |
| D7 `theme_custom` drops an unknown element | removed | removed | stays unless shared | removed | n/a | G keeps, H keeps |

So the mechanism removes D6 and D7 by itself, and D1 to D5 only if the layer form is dropped (Q6 option C, OPEN) or each is fixed on its own. [read from Q6 section 6 and 7; the mapping is reasoned, not run]

## A.3 A second engine later (ggplot2, dplyr)

- **A (data):** the typed tree is engine-neutral. A second engine adds a registry (names prefixed `ggplot2_`, `dplyr_`, as `polars_` and `plotnine_` are, D-0091) and a PRINTER from the tree to R source, never a parser of text. The allow-list is per engine; the walker, kind check, errors and the registry-walk test are shared.
- **C (text):** each engine needs its own grammar and parser; the text is in another language; the check-then-eval gap would have to be rebuilt.
- **F:** impossible (an extension is Python).
- **D:** `label_*` factories have R counterparts by name (`scales::label_percent`); the table of summary functions is per engine.
- Not examined: how R would be run at all (not in scope). [reasoned]

---

# SECURITY REVIEWER

## 4. Threat model in plain words

- **Who writes a recipe.** (a) The system manager of a deployment, who puts recipes in a directory the app reads (ADR-099 point 14: "recipes normally come from a system manager's directory"): trusted. (b) A recipe author at another institute whose recipe arrives by e-mail or as a bundle: semi-trusted, may be careless or hostile. (c) A HOME user who imports a bundle (zip with recipe, data, manifest): import is its own function, on only by configuration, for an authorised person (D-0030). (d) A Blueprint author who edits text, sometimes with an LLM (the `claude` CLI adapter, developer app features only; scout A3.12).
- **What the app runs with.** One Python process under one OS user: it can read every file that user can read, in particular the deployment's data and the project, and write sessions and exports. It starts `git`, `quarto` and the `claude` CLI as subprocesses (scout A3.12). It does not need the network (ADR-071 rule 1) but nothing prevents it. This machine has `/usr/bin/latex`, `pdflatex`, `xelatex` [run, `which`].
- **What "arbitrary code" means here.** Anything a recipe can make Python run other than the library call the author intended: (1) `eval` or `exec` of recipe text; (2) unpickling (Polars `deserialize` of a plan with a Python function [reasoned from the docstring]); (3) a library that runs a program for a setting (matplotlib with `text.usetex` runs LaTeX [memory]; the rc key exists [run]; whether shell escape is off by default is not checked); (4) reading a file the recipe names and showing its content in a log, a table or a plot; (5) writing a file; (6) exhausting memory or time (availability, not code).
- **Two layers (ADR-071, DECIDED 2026-11-15):** the app's checks, and the deployment's control of who may deposit recipes. The app's checks do not replace the second layer. D-0064 accepted the formula allow-list "for now" and "no time or size limit now".

## 5. Where each design stops being safe

**Allow-by-type against a deny-list.**
- *Allow-by-type* says: a recipe value is only text, number, boolean, null, list or mapping; a name is an object only if a code-owned registry has it. What can be written is bounded by construction: a recipe cannot name `os`, `open`, `pickle` or a lambda, because nothing resolves them. A new Python library version cannot add a way to name something that is not in the registry. Its limit: what the library DOES with plain data (next list).
- *Deny-list* says: anything may be written except these names. The set of dangerous names is open (every module, builtin, method, and every future release). It holds only as long as the authors thought of every danger. F1 is the proof [run]: a deny set generated from the signatures still missed 2 of 412 members.
- So: allow-by-type for what can be written, plus a decision per parameter for what plain data means to the library. Neither alone.

**Parameters reachable today that do something dangerous even as plain data** (walked from the registries by `scan_plotnine2.py`, `scan_polars.py`, `scan_expr.py`; counts per component).

Plotnine, 191 components:

| Class | Parameters (components) | What the present code does |
|---|---|---|
| Text evaluated as Python | `formula` (4: geom_smooth, stat_smooth, geom_quantile, stat_quantile); `facets` (1: facet_wrap); `rows`, `cols` (3: facet_grid, facet_rows, facet_cols); `fun` (1: stat_function) | Refused by PS06 (`plot_text_check.py:132-165`), keyed on these NAMES [read]. A new plotnine parameter that evaluates text is not caught. |
| Text the library interprets, not evaluated as code | `format_string` (2: geom_text, geom_label); `date_labels`, `date_breaks`, `date_minor_breaks` (4 date scales); `qhull_options` (1: stat_hull) | NOT refused. Run: `format_string: "{0.__class__.__mro__}"` printed `(<class 'float'>, <class 'object'>)` into the plot [run]: attribute reads, no calls, from plain data values only; low. `qhull_options: "TO <file>"` is refused by scipy itself ("qh.fout was not set", [run]). |
| Name resolved by a library table | `distribution` (4; scipy list, `getattr` only after membership), `fun_data` (2; 5-entry dict), `labeller` (4; `LABELLERS` dict), `trans` (38; mizani `REGISTRY` dict), `geom`/`stat`/`position` strings (64/63/72; plotnine registry), `method` (6), `package` (3), `kernel` (4) | Safe while the library resolves through a dict or an enumerated set [read the library lines above]. Each should be a registry entry with a decision. |
| Dictionary forwarded as keyword arguments | `method_args` (4), `kde_params` (3), `dparams` (4), `adjust_text` (2), `fun_args` (2), `args` (1), `rc` (1: theme_matplotlib) | Not judged; the names inside are the library's. `rc` is the dangerous one (below). |
| A path or a file | `fname` (1: theme_matplotlib); `path_effects` (2, objects) | `fname` and `rc` are in the checker's catalogue as accepted names (`allowed_arguments("theme_matplotlib")` returned `fname, rc, use_defaults, base_size, base_family`, [run]) but the handler sends them to `theme(...)` and the run fails "no themeable element called: fname" [run]. Today it fails safe; passing every library option through would make it reach `rc_params_from_file`, which echoes a line of any file in a warning (run: "Missing colon in file '<path>', line 1 ('<the line>')"), and `rc`, whose keys include `text.usetex`, `text.latex.preamble`, `animation.ffmpeg_path`, `savefig.directory`, `backend` [run, key list]. A dictionary of plain values would then configure the engine. |
| A function by type | `breaks` (75, with stats), `labels` (67), `limits` (67), `minor_breaks` (38), `rescaler` (38), `oob` (38), `fun_y`/`fun_ymin`/`fun_ymax` (2 each) | A recipe cannot write a callable, so these fail safe. `rescaler` and `oob` are refused by name (`parameters.py:47-48`), `fun_y*` by `not_exposed` (`geoms/core.py:1143` and `:1533`). Any other new callable parameter is exposed silently: no test fails (grep `Callable` in viz tests: 0). |
| Size and count | `figure_size`, `dpi` (2 via `theme`), `n` (10), `bins` (10), `gridsize` (2), `levels` (2) | No limit (D-0064 "no time or size limit now"). Run: `figure_size: [500, 500], dpi: 100` built a 50000 x 50000 pixel figure with no refusal [run]; rasterising it would need about 10 GB [reasoned]. |

Polars, 68 actions, 205 (action, parameter) pairs, all read from the Polars signatures:

| Class | Parameters | What the present code does |
|---|---|---|
| Expression text | 6 parameters: `named_exprs` (polars_with_columns), `named_aggs` (polars_group_by, polars_group_by_dynamic, polars_rolling), `predicates` (polars_remove, modif_join_where); plus the ID-reconciliation mutate | AST allow-list then `eval`. F1 hole. Module functions are a short list of 38 (`formula_check.py:44-50`); `pl.read_csv`, `pl.scan_parquet`, `pl.int_range` refused [run]. |
| Path or file | none among the 68 actions' exposed parameters (name and annotation scan) [run]; the Expr members `deserialize` (`source`) and `json_path_match` (an expression, not a path) were the only 2 hits among 412 allowed members | `deserialize` is the F1 hole. |
| Regular expression | `pattern` in `polars_str_extract` and `polars_str_replace_all` (the two my scan flagged) | Rust regex: `(a*)*b` on 20 strings of 50000 characters took 0.006 s; `((a{100}){100}){100}` is refused by a compile size limit of 10 MB [run]. No catastrophic backtracking. |
| Size or count | `polars_sample n`, `polars_shift n`, `polars_join how: cross`, `repeat_by`, `sample` in an expression | No limit [reasoned, not run]. |
| Callable by type | `polars_rename.mapping` takes a function in Polars; the widget is `mapping` (a dictionary), so ST10 refuses other forms (`ui_schema.py` `step_problems`, read) | Fails safe by the form check. |
| Name lookup | `dtype` (`getattr(pl, name)`, guarded by the dtype name list, `polars_calls.py:185-189`, scout) | Safe. |

**Where each design stops being safe.**

| Design | Stops being safe when |
|---|---|
| A (typed value) | a registered constructor has a parameter that is a path, a format, a program or a callable (`label_custom(template)` is a format string and `label_date(fmt)` a strftime format [memory, not run]); a registry entry is added without the walk test; the kind check is missing and an object reaches a place that calls it. It never runs recipe text. |
| B (owners) | as A, plus each owner repeats the name check: one owner without it re-opens the silent fallbacks (D6, D7). |
| C1 (text, `eval`) | the check admits any member that leaves "expression only" (F1 is that); two readers of one text (our `ast` walk and Python's compile) can disagree. |
| C2 (text, interpreter) | the same member list is wrong (a registry decision), but a node type with no code cannot run; no builtins, no globals. Stronger than C1; the member list still needs the structural rule. |
| D (named functions) | an entry is added whose argument is a format string or a callable. NA handling is correctness, not security. |
| E (serialised) | at once: deserialisation is the hole. |
| F (extension) | at once, by design: it is code; trust is the operator's. |
| G | at each new component. |
| H (deny-list) | at the first dangerous member nobody listed (F1). |

## 6. Mappings: is `x: "factor(year)"` or `y: "after_stat(count)"` evaluated from a recipe?

- **Plot-level `mapping:` is NOT evaluated; it is refused.** `viz_factory.py:303-318` requires every mapped value to be an exact column of the data. Run: `y: after_stat(count)` and `x: factor(x)` stop with "the aesthetic is mapped to the column ..., which the data does not have" [run, `probes1.py`]. A column that is literally named `len(g)` works as a column, because plotnine looks `col in data` before it evaluates (`plotnine/mapping/evaluation.py:162-165`, read) [run].
- **The layer's own `mapping` parameter cannot carry text either.** `geom_point` with `mapping: {y: "len(g)*0+y"}` fails in plotnine ("expected a dataframe or a mapping", it needs an `aes` object); the checker's catalogue still accepts the NAME `mapping` (it is in `LAYER_NOT_EXPOSED`, `parameters.py:42`, and `accepted_names` includes it) [run, read].
- **Consequence for the question.** `factor(...)`, `after_stat(...)`, `stage(...)` are not available to authors today, and they are not a security gap; they are missing features. If Eve wants them, the safe path is MINE and applies to A and C2: plotnine only evaluates strings we generate. A typed node `{after_stat: count}` or `{factor: year}` is validated (function from a registry, column an exact column) and then PRINTED into the string that plotnine evaluates. An author's text never reaches plotnine's `env.eval`. The three evaluated places today (smoother formula, facet variable, `stat_function`) could be reduced the same way, and the PS06 check by name would become unnecessary.

## 7. Gaps found by the scout, checked

1. **PA02 containment inactive in the app.** [read + run] `app/modules/data_analysis_recipe_validator.py:247, 258, 277` call `check_recipe(_file)` with no roots; `containment_problems` returns `[]` when roots is None (`recipe_paths.py:41-51`). The spec says the app passes roots (`recipe_format_spec.md:798`): a contradiction (rule H). Run: a path `data/link/other.tsv` where `link` is a symlink to a folder outside the project passes PA01 (shape), passes PA02 with no roots, fails PA02 with the project as root, and the file opens [run]. *Judgement:* low in practice (PA01 refuses `..`, absolute, `~`, URL, so it needs a symlink inside the tree); high as a record contradiction. *Suggestion:* the app passes roots (deployment raw_data and references) or the spec line is corrected by a decision; either way a test with a symlink.
2. **`source.path` opened at run time with no containment**, relative to the process folder, not to the recipe. [read `ingestor.py:71-86`: `Path(source_path)` into `pl.scan_csv`/`scan_parquet`] *Judgement:* medium, a second line of defence is missing and the result depends on the working directory (a reproducibility point). *Suggestion:* resolve against the recipe or deployment root and call `containment_problems` at the open, as well as in the checker.
3. **`zf.extractall` on a session zip.** [run] On Python 3.14.10 a crafted zip with `../escaped_dotdot.txt`, `/tmp_abs_probe_scratch/abs.txt`, `ok/sub/../../escaped2.txt` and a member typed as a symlink extracted entirely inside the destination: `..` removed, absolute names re-rooted, the symlink member written as a plain file (listing in `files/zip`). So no zip-slip on this version. Remaining, [reasoned from `session_manager.py:566-585`]: the check relies on the standard library of the running version and has no test; the session key is `Path(anchor).parts[0]` of the first member name, so a zip can write over an existing session folder with that key; there is no size limit. *Judgement:* low for escape, medium for overwrite. *Suggestion:* validate member names (no `..`, no absolute, one top-level key matching a key pattern), tell the user when the key exists and let them choose (inform, do not choose), cap the total size, add the crafted zip as a test.
4. **`yaml.SafeLoader.add_constructor('!include', ...)` on the global class.** [run, `config_loader.py:129`] After two `ConfigManager` objects (folders A then B), an unrelated `yaml.safe_load("y: !include a.yaml")` returned B's fragment; `!include ../outside_secret.yaml` returned `{}` and the refusal went into a list nobody reads; `'!include' in yaml.SafeLoader.yaml_constructors` is True. So any YAML parsed by SafeLoader later (a manifest, a session file, an uploaded file) honours `!include` with the last recipe's folder and root, and a refusal is silent. *Judgement:* medium: integrity and reproducibility (wrong folder, cross-session bleed, silent `{}`), low for confidentiality (confined to the project root). *Suggestion:* a private Loader subclass per ConfigManager, as the other loaders do; never touch `yaml.SafeLoader`; a test that `yaml.safe_load('a: !include x')` raises after a recipe was loaded.
5. **Three deployment loaders without containment** (`bootloader.py:672-688`, `app_features_validator.py:190-204`, `sidebar_validator.py:209-223`; scout read, not re-read by me). *Judgement:* low (operator files, not recipe content). *Suggestion:* one shared include helper in `utils`, so the rule exists once.
6. **Builtins reachable from a patsy formula or facet expression?** [run, `probes3.py`] The evaluator ALONE sees builtins: `geom_smooth(formula="y ~ I(len(x)*0 + x)")` and `facet_wrap("len(g)")` with only `plot_environment()` ran `len`. Through the factory both are refused ("the function 'len' is not allowed", "not a column of the data"). `y ~ x + abs(x)` is allowed and `abs` is the numpy one in that environment. So the text check is the only barrier, as the docstring says (`checked_plot.py:45`). *Judgement:* acceptable while the check is by registry; fragile because PS06 is keyed on the parameter NAMES `formula`, `facets`, `rows`, `cols`, `fun` (`plot_text_check.py:132-165`). *Suggestion:* design A/C2's generated-text principle (section 6).
7. Beyond the scout (MINE): `theme_matplotlib` `fname`/`rc` accepted by the checker and failed at run (section 5); `geom_text` `format_string` not covered (section 5); `figure_size`/`dpi` unbounded (section 5); F1.

## 8. Invariants that must be true for ANY chosen design

1. No recipe text is evaluated outside the checked grammars; a grammar is a registry, never a deny set. The number of places that read recipe text as code is a number a test pins (today 2 `eval` calls, [scout A5]).
2. Every callable comes from a registry in code. A recipe holds text, number, boolean, null, list or mapping.
3. Every path is contained, checked at the open, not only in the checker. No exposed parameter takes a path unless it has its own base and a decision.
4. Every component parameter is allowed by name AND by kind or type. An unknown name or kind is refused with a did-you-mean and the one error form; never dropped, never defaulted (D6, D7 are the counter-example).
5. A new parameter of a registered component that accepts a callable, a path, a file object, bytes, a format string or a dictionary of engine settings makes a test fail until someone records a decision. The test walks the registries (what my scans do: `scan_plotnine2.py`, `scan_polars.py`, `scan_expr.py`). Today no test does (0 greps).
6. Every member of an expression allow-list is allowed by what it IS: not static, not class, takes no path, file or bytes. A test walks the 412 members.
7. Registry names for values do not collide with step names; a test pins it.
8. Resource limits are a decision: either "none, stated" (D-0064) or a number; each size-driven parameter is listed.
9. A test that cannot be fooled by the check being the only barrier: the evaluator alone is unsafe (run), so the tests assert on the whole path (factory), as `test_plot_text_runs_no_code.py` does with a marker file.
10. The export records the recipe as written, the library versions (already), and for typed values the resolved call (MINE) so the audit shows what ran.

What an audit or test would NOT catch today: F1 (the pinned deny set names only Callable); `format_string`; `rc`/`fname` becoming reachable when options are passed through; a new evaluated plot text under another parameter name; a new callable parameter on a plot component; the global YAML loader; zip behaviour on another Python version.

---

## Summary table

| Design | Proposed by | Covers which named cases | Security judgement | Cost (estimate) | Recommendation |
|---|---|---|---|---|---|
| A. Typed value, one resolver, kind per parameter | MINE (hints from the brief) | 1, 2, 3, 4 (list, dict, function), 5, labeller; not 6 (chains) | Holds by construction if the walk test exists; stops at a registered parameter that is a path, a format or a callable | ~1000 lines, 3-4 sessions + Blueprint | Recommend, as the core for plotnine |
| B. Section per owner | Eve (idea 1), generalised | 1-3 only; not 4 (functions), 5 | As A if shared; weak if copied | ~80 lines per owner | Only as A with owners declaring kinds |
| C1. Text, check then eval | brief hint | 1-6 | Gap check/eval; F1 is the example | ~300 lines | Not recommended |
| C2. Text, interpreter, no eval | MINE | 1-6; the only design that serves case 6 with the same grammar | Stronger than C1; needs the structural member rule | ~400 lines | Recommend for Polars expressions; optional for plotnine |
| D. Named functions (library factories + our table) | brief hint, partly MINE | 4 (function), 5, labeller | Safe if entries are data-only; NA policy is Eve's | ~200 lines + decision | Recommend with A; the table needs a decision |
| E. Serialised expressions | brief hint | 6 only | Unsafe (is F1) | low code | Reject |
| F. Extension module by name and hash | brief hint (premise) | "everything" | Code by design; trust = operator | ~400 lines | Defer; decide after A/D show what is out of reach |
| G. One component per case | status quo | whatever is written | Per component | grows | Replaced by A |
| H. Pass through + deny-list | Eve (idea 3) | all | Does not hold (F1) | endless | Reject |
| Eve's idea 2 (dict + allowed names) | Eve | names only | Names yes, values no | exists | Keep, add kinds (A) |

My combined recommendation: A (with D's library factories) for plotnine objects and functions; C2 (interpreter, structural member rule) for Polars expression text; fix F1 first; keep F open. This reconsiders no decided rule except (CONFIRM) the meaning of "exact component" for the 15 (D-0210, Q6 option B or C) and the surface for plot values against ADR-099 point 15.

## What Eve is asked

1. What does "all python and polars options" mean: every library PARAMETER, plain data (yes in A/D); every library OBJECT with a constructor (yes in A, by registry); a function written by the user (no in the recipe; F is the only way). Which?
2. How is a typed value written: one-key mapping `{position_dodge: {width: 0.5}}`, `{name, params}`, or a YAML tag? (consequences in A.1)
3. For Polars expressions: keep text, and interpret it without `eval`? And fix F1 now (structural rule)?
4. Which named summary functions exist and how do they treat NA (Q9)? She decides, the app shows the policy.
5. For the 15 objects: value only (Q6 option C) or value plus a `modif_` layer (option B)? (D1 to D5 depend on it.)
6. For each parameter class that is plain but dangerous (`rc`, `fname`, `format_string`, `adjust_text`, `qhull_options`, `figure_size`, `dpi`): allowed, refused, or limited by a number.
7. Reaffirm "no time or size limit now" (D-0064) knowing the 50000 x 50000 pixel figure.
8. PA02: should the app pass roots (spec) or should the spec change?
9. Session zip with an existing key: overwrite, refuse, or ask the user?
10. Is a deployment extension module (F) wanted at all, later?

## Not checked

- Blueprint's form code and widget handling of a new `object` widget; HOME and export code beyond `export_handlers.py:95-125`.
- A payload with a Python function inside a serialised Polars expression (by choice); `text.usetex` with LaTeX (not run); matplotlib `rc` keys beyond the list; `theme_xkcd`, `theme_seaborn` (only signatures listed).
- Memory use of `sample(n=...)`, joins, 50000-pixel save (not run).
- Bundle import code (`bundle_importer.py:265`, scout only); the three deployment loaders (scout only); the ID-reconciliation ST06; `recipe_check.formulas()` caller.
- The existing test suite was not run; I did not run `test_formula_check.py`.
- The plain-data share (41%) is per component and counts shared parameters repeatedly; "490 unreadable" includes 244 theme keywords; geom/stat types are from defaults only.
- The count of seven D defects against "six" in the brief: I used the Q6 report, section 6.
- Whether `modif_` named themes forward every extra key to `theme(**spec)` in all 13 themes (read for `theme_gray`, `theme_bw`, `theme_matplotlib` only).
- plotnine versions other than 0.15.4; R engines; the unread parts of `plot_config_resolver` (a mapping could be added by the T3 override; I only read that the resolved mapping is validated at `viz_factory.py:303-318`).

## Scratch files (all under `tmpAI/panel/recipe_arguments/architect/`)

`scan_plotnine2.py` (+`plotnine_scan2.json`), `coverage.py`, `scan_polars.py` (+`polars_scan.json`), `scan_expr.py`, `typed_prototype.py`, `interp_prototype.py`, `probes1.py` to `probes4.py`, `probe_memory.py`, `files/` (benign serialised expression, canary files, crafted zip, include folders, symlink folder; nothing outside scratch).
