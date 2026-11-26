REPORT: formula-night, 4 tasks done and committed (branch task/formula-night; worktree /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/.claude/worktrees/formula-night). Nothing pushed. Tree clean after the last commit.

COMMITS (each ends with Co-Authored-By: Claude Sonnet <noreply@anthropic.com>)
- 13309b81 docs(formula): Expr.inspect refusal recorded as decided (D-0229)
- cde88fbf fix(formula): refuse pl.Object (D-0230)
- 2a35af81 feat(formula): allow pl.element() and pl.field() (D-0231)
- 8263bec3 fix(stat_function): the check accepts a name only when the drawing has it (D-0232)
- 126fda08 merge: dev into formula-night, done on the coordinator's correction (no conflict).

PROOF OF WORKTREE IMPORTS
After the merge, from a pytest run at the worktree root, `utils.formula_check.__file__` = .../worktrees/formula-night/libs/utils/src/utils/formula_check.py and `viz_factory.__file__` = .../worktrees/formula-night/libs/viz_factory/src/viz_factory/__init__.py. `app/tests/test_imports_from_checkout.py`: 12 passed, also with PYTHONPATH unset. Outside pytest I used the worktree PYTHONPATH (tmpAI/env.sh) and the same two files resolved to the worktree.

TEST ORDER: BEFORE AND AFTER THE TRAP (the coordinator's correction)
- I found the trap myself at about 20:59, before your message: the main folder's pyproject.toml got a pytest block, so pytest started in my worktree used MAIN's code. Runs of Tasks 1, 2 and the first Task 3 suite were done before that moment, and the break-once of Task 2 proved the worktree code was in use then. Runs between 20:59 and the merge used a private config (`-c tmpAI/pytest.ini --rootdir`, which forces the worktree). Those were valid, but I repeated everything after the merge anyway.
- AFTER the merge, plain pytest from the worktree root. All numbers below are from this run:
  - libs/utils/tests + viz_factory stat_function/plot_text/registry-audit tests + all app/tests and transformer tests that name "formula" + test_plot_text_gate + test_suggestion_label + test_imports_from_checkout: 2992 passed, 8 xfailed.
  - full libs/viz_factory/tests + libs/transformer/tests: 4412 passed, 9 xfailed.
  - Browser tests not run, as asked.
- Break-once, repeated after the merge; each test failed with the code broken and the code was then restored:
  - Task 2, pl.Object check disabled: 34 failed.
  - Task 3, element/field taken off MODULE_FUNCTIONS: 9 failed.
  - Task 3, inspect no longer refused: 9 hostile-inner tests failed.
  - Task 4, math uses the numpy list: 95 failed.
  - Task 4, numpy prefix removed from the table: 4 failed.
  - Task 4, numpy not defined in the drawing namespace: 23 failed.

TASK 1 (D-0229)
The PROVISIONAL mark for `Expr.inspect` is replaced by a citation of D-0229 in three places: .claude/design/recipe_format_spec.md (formula check paragraph, about line 795), libs/utils/src/utils/formula_check.py (comment on REFUSED_BY_NAME) and libs/utils/tests/test_formula_reads_no_outside_data.py (comment above INSPECT_SPELLINGS). No behaviour change.

TASK 2 (D-0230): pl.Object refused
- formula_check.py: `REFUSED_DTYPES` and `REFUSED_DTYPE_SUGGESTION`, used in `_Checker.visit_Attribute` (the `kind == "module"` branch).
- The message reads: "pl.Object holds any Python object, which a table column does not; a recipe works on normal table columns. Fix: Suggestion: use a type a table can hold, for example pl.String, pl.Int64, ...". The "Fix: Suggestion:" form is the existing convention; readers show it as "Suggestion:" through `fix_label`.
- Every way to name the type goes through `pl.<name>`, so one refusal covers `pl.Object`, `pl.Object()`, `List(pl.Object)`, `Array(pl.Object,2)`, `Struct({'x': pl.Object})`, keyword values and list/dict containers. A dtype written as a string is not read by Polars 1.40.1: it gives a plain TypeError (tested for "Object", "object", "OBJECT", "pl.Object", "Python object"). A test fails if a Polars upgrade starts reading strings.
- Tests: libs/utils/tests/test_formula_refuses_object.py (44), including one that fails without the fix (34 fail with it broken) and one that checks no panic can start (FormulaError is raised before Polars runs). All shipped formulas are still accepted (`test_every_formula_in_the_shipped_recipes_is_allowed` stays green).
- Parked note, dated 2026-11-17, with her condition ("if a request or a necessity comes"): in the spec next to the formula rule, and in the code comment on REFUSED_DTYPES. No panic is caught.
- Not decided, found: `pl.Unknown` also panics in `str.json_decode` ("not implemented ... for Unknown"). D-0230 names only Object, so I left it. Open item for Eve: refuse `pl.Unknown` the same way?

TASK 3 (D-0231): pl.element() and pl.field()
Safety check done first (labels: verified by reading the signatures and by running).
- `pl.element()` has no parameter; `pl.field(name)` has one parameter, a text or a list of texts. Neither takes a function, a file, bytes or a library path.
- They are the same as `pl.col('')` (already allowed, and working in `list.eval`; verified) and a field name inside `struct.with_fields`.
- The returned object is an `Expr`. The argument of `list.eval`, `list.filter`, `cumulative_eval` and `struct.with_fields` is walked by the same `_Checker.visit_Call` as any other expression (verified by tests).
- Outside a list or struct, Polars gives a plain `InvalidOperationError`, not a panic (tested; the test fails if an upgrade turns it into a panic).
- No danger found, so they are allowed: "element" and "field" added to `MODULE_FUNCTIONS` (formula_check.py) and to `MODULE_REVIEWED` with review lines (test_formula_reads_no_outside_data.py).
- Tests: libs/utils/tests/test_formula_element_field.py (96). They cover:
  - formulas on data: strip inside `list.eval`, a filter, two evals in a row, `list.filter`, `struct.with_fields(pl.field('x') ** 2)`, `pl.field(['x','y'])`, and a field combined with `pl.col`;
  - hostile inner expressions: 9 refused members (deserialize, from_json, register_plugin, inspect, map_elements, map_batches, pipe, rolling_map, meta) × 4 wrappers × element/field start, all still refused, and the message names the member;
  - nested hostile members, `pl.Object` inside, uncalled `pl.element`/`pl.field`, underscore members, and hostile arguments to `pl.field`.
- Spec sentence updated (same paragraph as Task 2).

Gene-list run (no new action built). Script and output: tmpAI/night/gene_list_run.py in the worktree (git-ignored). The action names in the brief no longer exist; the registered ones are `polars_str_split`, `polars_explode`, `polars_str_strip_chars`, `polars_unique`, `polars_drop_nulls`, `modif_filter`, `polars_with_columns`. Test column: "gene1, gene2, gene3", "gene1,gene2,gene3", "" (empty), null, "gene1, gene1, gene2", " gene7 ,gene8  , ".
- What a recipe author writes today, no `pl.element`:
  ```
  - action: polars_str_split
    columns: [genes]
    by: ','
  - action: polars_explode
    columns: [genes]
  - action: polars_str_strip_chars
    columns: [genes]
  ```
  Order matters: strip AFTER explode. Splitting on ", " leaves "gene1,gene2,gene3" (no spaces) as one gene. The split on "," followed by explode and strip handles both spacings. This gives 14 rows.
- Spaces, with or without: handled by split on "," then strip after explode.
- Empty cell: becomes ONE row with gene "" (a blank gene, kept). A trailing comma or space-only element also gives a "" row (s6). Null cell: one row with null gene.
- Repeated gene: kept as two rows (s5 has gene1 twice) unless `polars_unique` on [sample, genes] is added, which collapses it.
- Dropping blanks is the author's choice and loses samples silently in the long table:
  - `polars_drop_nulls` removes the null sample (s4) from the long table;
  - `modif_filter` ne '' (needs `na: keep|remove`) removes the empty cell's sample (s3) entirely; with `na: keep`, s4 stays as a null row.
  - Neither shows the user that a sample vanished. Whether to inform (a count) is a question for Eve, related to D-0168.
- Without `pl.element`: it works, in 3 steps (4-5 with unique and filter). The whole job also runs in one `polars_with_columns` formula without element if the cell is first normalised with a regex: `pl.col('genes').str.replace_all(r'\s*,\s*', ',').str.strip_chars().str.split(',')`, then explode; the trailing comma still gives "".
- With `pl.element` the strip, blank removal and de-duplication can be done inside the list in one formula before the explode: `...split(',').list.eval(pl.element().str.strip_chars().filter(pl.element().str.strip_chars() != '')).list.unique(maintain_order=True)`. The empty and null cells then both become a null row, so no sample is lost.
- A new step: not needed to get the long format. Open item for Eve, not built: whether she wants one step "split a list column into long format" that also reports how many empty, null and repeated cells it met.

TASK 4 (D-0232): stat_function names
Verified by running before the fix:
- `math.arcsin(x)`: check accepted, drawing AttributeError.
- `numpy.arcsin(x)`: check accepted, drawing NameError.
- `math.abs`, `math.sign`: accepted, AttributeError.
- Names of `MATH_FUNCTIONS` missing in Python's `math`: abs, arccos, arcsin, arctan, sign. All 18 exist in numpy.
- I also found and fixed the same class of check/drawing disagreement: a function written but not called (`lambda x: sin`, `np.sin`) gave "Discrete value supplied to continuous scale", and a wrong argument count (`sin(x, x)`, `sin()`) gave TypeError late.

What changed:
- formula_check.py: one table, `PLOT_FUNCTION_MODULES` (np→numpy, numpy→numpy, math→math), `PLOT_FUNCTION_NAMES`, `PYTHON_MATH_FUNCTIONS` (asin, acos, atan, fabs, floor, ceil, ... no sign) and the arity rule (every function takes one number; only `math.log` takes a second, the base). `_FunctionChecker` rewritten to read them.
- viz_factory/geoms/core.py: new `function_string_namespace()`, built from the same tables. It stops with the name if a table entry is missing in the real module. `_function_from_string` uses it and `with_fix`, so there is one "Suggestion:" label.
- plot_text_check.py: no doubled "Suggestion: Suggestion:".
- Message example: "math.arcsin does not exist: math has asin, not arcsin. Suggestion: write math.asin, or np.arcsin". For `math.sign`: "math has no sign ... Suggestion: write np.sign". Also "math.abs ... math has fabs, not abs".
- HOW for `numpy.`: I chose (b), defining `numpy` in the drawing namespace. Reason: the spec already lists `numpy.name` for smoother formulas, so one vocabulary; it needs one table line; and nothing valid is refused.
- Alternative (a), only `np` and `math`, with `numpy.` refused as "write np": one way to write it, and smaller namespace. It would need a refusal in the smoother too, to stay consistent. Close call, for Eve to pick. Switching is one line in `PLOT_FUNCTION_MODULES` plus a message.
- Tests: libs/utils/tests/test_stat_function_names.py (130) and libs/viz_factory/tests/test_stat_function_names_drawn.py (about 60). They cover every refused combination, a test that fails without the fix, every table entry checked against the real modules, and every accepted name evaluated in the real drawing namespace. A few spellings (`math.asin`, `numpy.arcsin`, `math.log(x, 10)`) are drawn with plotnine.
- Shipped recipes and gallery: only libs/viz_factory/tests/test_data/stat_function_test.yaml (`lambda x: x * 2`) and assets/scripts/debug_bootstrap_viz_yamls.py (`lambda x: x**2`) use `stat_function`; neither is affected.
- Spec updated with the new rule.

OPEN / NOT RESOLVED (for Eve)
1. Late, cryptic drawing failure, found, NOT fixed: `lambda x: 1 / x` with xlim (-1, 1), or `np.log(x)` with x ≤ 0, stops the drawing with `KeyError: '__import__'`. Cause: a numpy warning inside a lambda that runs with empty builtins. With xlim (1, 3) it draws. This is a data-dependent failure, not a name. Options: (a) run the function inside `np.errstate` and give a plain message; (b) turn it into NaN, which is silent; (c) keep as is. Violates D-0050 as it stands; needs her choice because (b) hides rows.
2. In `math.sqrt(-0.9)`-type cases (domain error), Python's `math` raises ValueError at drawing: late. The message is plain Python, not the project's.
3. The smoother formula treats `math.` as numpy (`checked_plot.plot_environment`); in `stat_function` `math.` is Python's math. So `math.arcsin(x)` works in a smoother and is refused in `stat_function`. Documented in the spec, not changed.
4. `pl.Unknown` panics in `json_decode` (see Task 2).
5. dependency_index.md is auto-generated from `@deps`; I updated the `@deps` blocks (provides/consumed_by in formula_check.py and geoms/core.py) but did not run `build_dep_graph.py`. A scribe or builder must regenerate it.
6. The `PLOT_FUNCTION_*` tables live in utils without a numpy dependency (utils' pyproject has no numpy); existence in numpy/math is checked by tests and by the namespace builder, not at import in utils. Design choice made by me, reported.

NOT CHECKED
- Browser tests; the rest of app/tests (only files naming "formula", plot gate, suggestion label, imports); UML/ADR sync (`docs/UML/app.mdj`, architecture_decisions.md); whether any other place builds a `stat_function` through `stat="stat_function"` on a geom (its `fun` is not checked there; plotnine then refuses a string).
