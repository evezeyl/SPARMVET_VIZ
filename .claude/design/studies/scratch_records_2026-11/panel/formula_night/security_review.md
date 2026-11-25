VERDICT: merge after a named fix (documentation only). The code and the tests hold. I found no way through the check, and no valid lambda that dev accepted is now refused. One true statement in the spec is now false, and D-0231 and D-0232 say what the spec must say.

FIRST, THE WORKTREE IS REALLY BEING TESTED
- `app/tests/test_imports_from_checkout.py`: 12 passed.
- I made a mistake of my own and want it on record. My first hostile run used `python -I`, which ignores PYTHONPATH, and it imported MAIN's formula_check (the printed file path showed it). I re-ran every list with the worktree PYTHONPATH from `tmpAI/env.sh` and checked that the printed path was the worktree. All results below are from the second run.
- Every pytest run was started from the worktree root, and `git status` is clean after my three break-once edits.

FINDINGS, RANKED

1. MEDIUM, a record that contradicts the code. `.claude/design/recipe_format_spec.md:803` still says "Open, not decided (2026-11-17): ... (b) `pl.element()` and `pl.field()` are not allowed, so `list.eval` and `arr.eval` cannot take an inner expression". That is false after D-0231 and the code at `formula_check.py:60`. Point (a) there ("a formula can raise a PanicException, e.g. `str.json_decode(pl.Object)`") now cites an example that is refused. It should say that Object is parked (D-0230) and that other panics remain. Rule H applies: a contradiction between records. A scribe should fix it.

2. LOW, open items for Eve, not defects of this branch. Polars panics (a `PanicException`, which is a BaseException) that the check accepts:
   - `pl.col('a').str.json_decode(pl.Unknown)` and `pl.Unknown()`. Confirmed.
   - `str.json_decode(pl.Binary)`: "not implemented: Deserialization from JSON not implemented for BinaryView".
   - `str.json_decode(pl.Array(pl.Unknown,2))`: panic for FixedSizeList.
   The builder found only the first. The last two are new.
   These three are the only panics I found in about 50 accepted dtype formulas. They are not listed in the spec (finding 1).

3. LOW, `pl.field(1)`, `pl.field(pl.col('b'))` and `pl.field('a','b')` are accepted by the check. `evaluate_formula` then raises a bare Python `TypeError` instead of a `FormulaError`. This is loud, not silent, and not a safety issue, but the message is not the project's plain one. `pl.field(['x'])` outside a struct gives a plain `InvalidOperationError`.

4. LOW, cosmetic: refusals read "Fix: Suggestion: np may use ..." (a doubled label). When the string has two problems, the sentences run together without a separator (example: `np.load('a')`).

5. NOTE, not a regression: `lambda x: 1 / x` and `np.log(x)` over a range that crosses zero stop with `KeyError: '__import__'`.
   - Cause: numpy raises a RuntimeWarning from inside the lambda. The warnings machinery then needs `__import__` from the lambda's globals, and the `__builtins__` there is `{}`.
   - It existed on dev: dev's `core.py:1308` uses the same `{"__builtins__": {}, ...}`. I reproduced it with that mechanism alone, without the branch's code (`h8.py`).
   - It is a D-0050 problem (a cryptic late failure) that nobody has decided yet. The builder correctly left it.

6. NOTE on scope, within D-0232. The uncalled function (`lambda x: sin`) and the wrong argument count (`sin(x, x)`, `math.log(x, x, x)`) were accepted on dev and failed late. Refusing them at the check is the same rule as "the check and the drawing agree". The behaviour is right: the messages name the function and the module and say what exists. Nothing is built beyond the six decisions. The builder's "open to Eve" note about the `numpy.` prefix is honest.

QUESTION 1: pl.element() and pl.field() (check function only; `h1.py`, `h2.py`)
I wrote 66 formulas. Every one of these was refused with the right member named:
- element() and field() followed by deserialize, from_json, register_plugin, inspect, map_elements, map_batches, pipe, rolling_map, meta (including `.meta` alone and `.meta.root_names()`), ext;
- the same members inside `list.eval`, `list.filter`, `list.agg`, `cumulative_eval` and `struct.with_fields`, nested two and three deep, as the keyword `expr=`, inside a list argument and inside a dict argument;
- uncalled `pl.element.__call__()`, `pl.field`, `pl.element`, `pl.field(...).__class__`, `pl._ext`, `pl.field(*['a'])`, `pl.field(**{...})`, `pl.field('x', _private=1)`, `pl.field(name=pl.element().pipe(len))`;
- `pl.col('a').element`, `.field`, `pl.Expr.field`, `pl.Expr.element`, `pl.col('a').list.element`;
- `pl.Object` inside `cast`, `json_decode(dtype=...)` and `Struct({...})` under element;
- `pl.col('a').list.eval(pl.lit(open('/etc/passwd')))` (the name `open` is refused).

Accepted, correctly: `pl.element().str.strip_chars()` and the same inside `list.eval`; `pl.col('s').struct.with_fields(pl.field('x')+1)`; `pl.col('a').struct.field('x')` (this one was already allowed on dev); `pl.field('a','b')`, `pl.field(1)`, `pl.field(pl.col('b'))` (see finding 3).

Name lookup:
- The module attribute path allows only those two names, and `Expr.field` and `Expr.element` do not exist. They go through the Expr-member table, which refuses them.
- `pl.col('other')` and `pl.col('b')` inside `list.eval` fail at run time with Polars `ComputeError: named columns are not allowed in eval`. So an element or field cannot reach columns of another frame, a file or the process.
- `pl.element()` outside a context gives a plain `InvalidOperationError`, not a panic. I ran these on a 3-row frame.

QUESTION 2: pl.Object and the other types (`h3.py`, `h4.py`)
Refused: `pl.Object`, `pl.Object()`, `List(pl.Object)`, `Array(pl.Object,2)`, `Struct({'x': pl.Object})`, `pl.Field(...)` (the name is not allowed), `pl.datatypes.Object`, `pl.Datatypes.Object`, `pl.Object.__class__`, and any of them in `cast`, `lit(dtype=)`, `json_decode(pl.Object)` or `dtype=`.

Accepted, then run on a 3-row frame. None of these can reach Object:
- Strings `'Object'` and `'object'` in `cast` and in `lit(dtype=)`: plain TypeError "cannot parse input of type 'str'".
- `Unknown`: `cast(pl.Unknown)` returns String; `json_decode(pl.Unknown)` PANICS.
- `Null`, `Decimal(38,10)`, `Decimal(0,0)`, `Decimal(100,2)`: plain InvalidOperationError.
- `Categorical` and `Categorical('lexical')`: OK. `Enum(['x'])` and `Enum([])`: error.
- `Enum([1])` and `Enum(pl.col('a'))`: TypeError. `Datetime('xx')` and `Duration('xx')`: ValueError.
- `Binary`: `cast` OK; `json_decode(pl.Binary)` PANICS.
- `List` and `Struct` bare: no panic.
- `Array(String,-1)`: OverflowError. `Array(String,10**18)`: InvalidOperationError.
- `json_decode` with List(Unknown), Struct({'x': Unknown}), Null, Categorical, Decimal(10,2), Enum, Time, Datetime('ns'): ComputeError, no panic.
- `json_decode(pl.Array(pl.Unknown,2))` PANICS.

Panics found: 3 (Unknown, Binary, Array of Unknown; finding 2).

QUESTION 3: stat_function
Check and drawing agree:
- I ran every accepted (prefix, name) pair in the real `_function_from_string`: 95 formulas, all drawn once with x=0.5 with no failure (the one failure in my script was my own test `e**x`, which is refused correctly).
- I also drew `math.sin`, `sqrt`, `asin(x/10)`, `log(x,10)`, `fabs`, `floor`, `exp` and `math.sin(x)+np.sin(x)` through plotnine's `ggplot.draw()`. All drew, so `math.f(x)` on arrays works through plotnine, and the builder's "one number at a time" is only a description.

`function_string_namespace()` (`core.py:1290`):
- Contents: the 18 numpy functions of `MATH_FUNCTIONS`, the constants `pi` and `e`, and the modules `np`, `numpy` and `math`. The lambda runs with `__builtins__` set to `{}`.
- It raises a plain VisualizationError at the first draw if a name in the tables is missing from the real module.

The check:
- It walks every node: `generic_visit` refuses every type that has no visitor.
- An attribute is accepted only for `module.const` (pi, e). A function is accepted only as a call whose func is `Name in MATH_FUNCTIONS` or `Attribute` on a Name in the three prefixes with a name in that module's table. A prefix appearing alone is refused as a name.

I ran 108 hostile or odd lambdas through the check (`h6.py`). All refused and none accepted, among them:
- np.load, fromfile, ctypeslib.load_library, memmap, np.lib, np.lib.npyio.load, vectorize, frompyfunc, core.sin;
- math.__loader__, __dict__, np.__builtins__, `x.__class__.__mro__`;
- `y=np` default, nested lambda, comprehension, walrus, f-string, subscript, starred, keywords including `out=`;
- `np.sin.__call__`, `np.sin.at`, np.sin applied to np / math / np.sin, `np.numpy.sin`, `np.np.sin`;
- IfExp, BoolOp, Compare, not, ~, @, <<, `x**x`, `x**10000`, `'a'*10**9`, `__import__`, eval, open, getattr, `np.sin(x)(x)`, `.T`, `.real`;
- np.pi.__class__, `np.e(x)`, `np.pi()`, `math.pi.real`;
- uncalled `math.sin`, `np.sin`, `sin`; `sin(x, x)`; `sin()`; `math.log(x,x,x)`; `math.pow`; `math.abs`; `math.sign`; `math.arcsin`; `numpy.load`; np.clip, where, maximum, power, hypot, exp2.

Accepted correctly: `np.sign`, `np.arcsin`, `numpy.arcsin`, `math.fabs`, `math.asin`, `np.sqrt(x)+math.sqrt(x)`, `abs(x)`, `-x`, `x % 2`, `x // 2`, bare `sin`.

Is (b) at least as safe as (a)? Yes. The `numpy` name is the same module object as `np`, which was already in the dev namespace. The check refuses every attribute not in the table, for both. So (b) adds no reach.

Compared with dev, lambdas accepted on dev and refused now: uncalled function names, wrong argument counts, `math.abs`, `math.sign`, `math.arcsin`, `np.sin(np.sin)`. All of them failed at the draw on dev. Accepted now and refused on dev: `math.fabs`, `math.asin`. No shipped use is affected. The only `stat_function` strings in recipes, tests and gallery are `lambda x: x * 2` (`libs/viz_factory/tests/test_data/stat_function_test.yaml:17`) and `lambda x: x**2` (`assets/scripts/debug_bootstrap_viz_yamls.py`). I did not open `docs/workflows/visualisation_factory.qmd` beyond one grep line.

QUESTION 4: decision compliance
- D-0229: the PROVISIONAL mark for inspect is gone from code, spec and test comments (grep is empty). The words "decided by Eve on 2026-11-17 (D-0229...)" are now in the spec.
- D-0230: the parked note with date and her condition is in the spec (about line 795) and in the comment on REFUSED_DTYPES (`formula_check.py:156`). No panic is caught, as she said. The message is plain and carries a Suggestion.
- D-0231: the safety check is written down, and I confirmed it by running. pl.element and pl.field are allowed with no danger found. The check walks the inner expression, as shown above.
- D-0232: complied; HOW was open to the builder. Behaviour checked by running, as above.
- D-0050: the one late failure the builder left (finding 5) is reported, not hidden.
- Nothing else is built beyond the six decisions. The spec's stat_function sentences are true. I checked the quoted messages by running `math.arcsin`.
- ADR and UML sync (`docs/UML/app.mdj`, `architecture_decisions.md`) and the `dependency_index.md` regeneration were not checked; the builder says it did not run `build_dep_graph.py`.

QUESTION 5: break-once (test files `test_stat_function_names.py`, `test_stat_function_names_drawn.py`, `test_formula_check.py`)
Baseline 358 passed. Each edit was restored with `git checkout`, and `git status` was clean afterwards:
- Arity check turned off (`if not low <= len(node.args) <= high` replaced by `if False`): 1 failed in the first test run, with `-x`.
- Uncalled-name refusal turned off: 1 failed in the first run, with `-x`.
- Added "arcsin" to `PYTHON_MATH_FUNCTIONS` (a false accept): 1 failed.
All three were caught. The tests can fail. I did not run the builder's other break-once cases. Shipped-recipe formulas pass (`test_every_formula_in_the_shipped_recipes_is_allowed` is inside the green runs).

QUESTION 6: full runs, worktree root
- `libs/utils/tests`: 1902 passed.
- `libs/viz_factory/tests`: 2165 passed, 9 xfailed, 2 warnings.
- `libs/transformer/tests`: 2247 passed.
- `app/tests` headless (without the four browser files): 3291 passed, 4 skipped, 3 xfailed, 0 failed (26 min 11 s on a busy machine). One earlier attempt of this suite was cut by my own 590 s timeout and is not a failure; I re-ran it with no timeout.

NOT CHECKED
- Browser tests, UML and ADR sync, `dependency_index.md` regeneration.
- Other panics in Polars outside the dtype and json_decode family.
- `stat="stat_function"` set on a geom as a `stat=` argument (the builder flagged it too).
- Whether a Polars upgrade breaks the walk tests.
- My probes ran only on small in-memory frames. I read no file outside the repository.
