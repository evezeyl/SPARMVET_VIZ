
---

# PART B. Option D as a prototype

## B1. What was built (READ: `libs/utils/src/utils/formula_build.py`, 269 lines, 204 of code; trial commit `fb0a59e7`)

The written form of a formula is unchanged. `build_formula(text)` has the same contract as `evaluate_formula(text)` (`formula_build.py:250`):
1. `formula_problems(text)` of today's check runs first. A refused formula gives the same message (the same function, so one set of policy rules: exponent, text multiplied, random rank, `pl.Object`, `shuffle`, argument counts of `pl.element` and `pl.field`).
2. The text is parsed with `ast.parse` (no `compile`) and walked by `_Builder` (`:91-243`). A value is built only from constants, lists, tuples, dictionaries, operators and calls of listed members.
3. There is no `eval`, `exec` or `compile` in the file. `getattr` appears only in `_tables()` (`:67-75`), with names that come from the lists of the check, never from the text. A name of the text is looked up in a dictionary; a miss is refused.

**How the list is shared (one list, not two).** `formula_build.py:21-23` imports `MODULE_FUNCTIONS`, `REFUSED_DTYPES`, `_NAMESPACES`, `_allowed`, `_dtypes`, `_namespace_classes`, `refused_members` and the message texts from `formula_check.py`. `_tables()` (`:52-88`) builds its dictionaries from them once:

| Table of D | Read from |
|---|---|
| module functions | `MODULE_FUNCTIONS` |
| dtypes | `_dtypes()` minus `REFUSED_DTYPES` |
| `Expr` methods | `_allowed()["expr"]` |
| namespace members | `_allowed()[name]` for the namespaces of `_NAMESPACES` |
| the objects after `pl.when(...)` | the four classes that `pl.when` and `.then` return |

RAN: `test_the_tables_are_read_from_the_lists_of_the_check` (in `test_formula_build.py`) asserts the tables equal the lists. A new Polars member, a new refusal or a new dtype entry changes both with no second edit. In production the private names (`_allowed` and the others) would have to become public.

**Where D is stricter on purpose.** After `.then(...)` the walk follows the types that Polars returns, not a guess from the text. A method called on a number, text, list or dictionary (not a column expression) is refused. A function name left uncalled inside a list or dictionary is refused.

## B2. Equality (RAN)

| Check | Result | Script and output |
|---|---|---|
| the 17 distinct texts the engine evaluated on the real data | 113 of 113 evaluations: same plan (`meta.eq`), same column (type, missing, values) | `a2_run_real.py`, `a2_summary.json` |
| the tables of 11 recipes (102 records) with D in place of `evaluate_formula` | identical to today's; the 7 shipped pipelines identical to `golden/baseline.json` | `a2_tables_d.json` |
| 305 distinct texts of recipes, test data and test sources (436 places) | 169 built by both: 169 same plan and same plan text. 136 refused by both: 136 same message. 0 mismatch | `b_corpus.py`, `b2_output.txt` |
| 75 constructs of the grammar | 52 built by both, same plan: 52. 23 refused by both, same message: 23. 0 mismatch | `b2_constructs.py` |
| 15 existing test files with D patched into the call sites (`polars_calls`, `id_reconciliation`, the tests) | 1597 tests pass; the same 1597 pass unpatched | `b2_tests_with_d.py` |
| the trial test file | 106 tests pass | pytest |

The 305 texts come from: the YAML files of section A1 (shipped and test), the string constants of every test source under `libs/*/tests` and `app/tests` that parse as a formula (formula check 193 texts, transformer 53, other 24), and the JSON test data (26). The 15 test files: 6 formula test files of `libs/utils/tests`, 7 of the transformer (polars equality, rows, aggregations, step conversion, recipe pairs, deterministic order), 2 of `id_reconciliation`.

**What D cannot build that today builds.** Among the 305 and the 75: nothing. Among my own new lines: the ones of section B3 (Python methods on a literal, uncalled function names in a container).

**A drift I found while building.** The first version refused `pl.when(a).then(1).when(b).then(2).alias('q')`: after a chained `.then`, an expression method such as `.alias` was not allowed. The 305 texts did not contain this shape; the construct list did (`b2_constructs.py`). I fixed it. This is the cost of two walks (the check and the builder): they can drift apart. A test that runs every refused or accepted shape through both is the guard; merging the check and the builder into one walk is an option (not built).

**Constructs listed in the brief (RAN: `b2_constructs.json`):** lambda inside `list.eval` (refused by both, the check refuses `Lambda`); `pl.element()` (equal); keyword arguments (equal); operators and their order (equal: the parser fixes the tree); chained comparison (both stop with Polars' "truth value of an Expr is ambiguous"); unary minus, invert (equal); `pl.when().then().otherwise()` chains of 1, 3 and without `otherwise` (equal); selectors `pl.col('^a.*$')`, `pl.col(pl.Int64, pl.Float64)`, `pl.all().exclude(...)` (equal); date, datetime, duration literals (equal); nested lists, tuples, dictionaries (equal); dtype objects `pl.List(pl.Struct({...}))`, `pl.Datetime('us','UTC')`, `pl.Enum([...])`, `pl.Decimal(10,2)`, `pl.Array(pl.Int64,3)`, `pl.Int64()` (equal). Hard to walk: nothing was hard. The only subtle one is the order of evaluation of `and`/`or` and chained comparisons: D does what Python does (calls `bool` on a column, which Polars refuses with a TypeError), so the error is the same as today's.

## B3. The hostile lines through D (RAN: `a3_b3_hostile.py`)

- The 60 lines: D with the check gives the same answer as today on all 60 (54 refused with the same message; 6 accepted). 0 differences.
- The 20 new lines: 8 differ from today. D refuses where today accepts (lines 101 to 105: Python methods on literals, uncalled functions in containers) or where today stops with a raw error (103: `AttributeError`; 108: `SyntaxError`). Both refuse with a different text on 109 and 110.
- The walk alone (no check), on the 54 hostile lines that the check refuses: 50 are refused by the walk (2 of them are not expressions: `import os` and `*pl.col('a')` stop at the parser). 2 are built, because they are policy of the check, not reach: `pl.col('a') ** 99999999` and `pl.lit('x'*5000)`. 2 end with another error: `pl.lit(10**10000)` (Polars refuses the huge integer) and the chain of 500 calls (RecursionError; D with the check never reaches it, the text is longer than 2000 characters). Among my new lines `rank(method='random')` is also built by the walk alone. So the walk is not a copy of the policy: D = check + walk.
- No line is refused by today's check and built by D, and none the reverse for the 60.

## B4. What D removes, what it does not

**Removes (RAN: `a3_b3_hostile.py`, `weak_table.md`).** With the check switched off, `eval` ran 10 of 12 harmless probes. D's walk refused all 12 on its own.

| class | probe (harmless) | `eval` path when the check is off | D walk when the check is off |
|---|---|---|---|
| attribute walking | `pl.col('a').__class__.__name__` | RAN: 'Expr' | REFUSED by the walk: the attribute '__class__' starts with an underscore (character 1). Fi |
| module attribute | `pl.__name__` | RAN: 'polars' | REFUSED by the walk: the attribute '__name__' starts with an underscore (character 1). Fix |
| module attribute | `pl.os.getpid() > 0` | RAN: True | REFUSED by the walk: pl.os is not allowed (character 1). Fix: use one of: all, all_horizon |
| dunder on a literal | `(1).__class__.__name__` | RAN: 'int' | REFUSED by the walk: the attribute '__class__' starts with an underscore (character 1). Fi |
| format string | `'{0.__class__.__name__}'.format(pl.col('a'))` | RAN: 'Expr' | REFUSED by the walk: the attribute 'format' is not allowed here: only a column expression  |
| comprehension | `[x for x in (1, 2)]` | RAN: [1, 2] | REFUSED by the walk: ListComp is not allowed in a formula (character 1). Fix: build the co |
| lambda | `(lambda: 1)()` | RAN: 1 | REFUSED by the walk: Lambda is not allowed in a formula (character 2). Fix: build the colu |
| conditional | `pl.col('a') if True else pl.col('b')` | RAN: <Expr ['col("a")'] at 0x7FD263F29450> | REFUSED by the walk: IfExp is not allowed in a formula (character 1). Fix: build the colum |
| uncalled outside function | `[pl.read_csv]` | RAN: [<function read_csv at 0x7fd2680fcf60>] | REFUSED by the walk: pl.read_csv is not allowed (character 2). Fix: use one of: all, all_h |
| python method on a literal | `[3, 1, 2].sort()` | RAN: None | REFUSED by the walk: the attribute 'sort' is not allowed here: only a column expression ha |
| name outside the list | `len([1, 2])` | error NameError: name 'len' is not defined | REFUSED by the walk: the name 'len' is not allowed; only pl is known (character 1). Fix: w |
| eval name | `eval('1 + 1')` | error NameError: name 'eval' is not defined | REFUSED by the walk: the name 'eval' is not allowed; only pl is known (character 1). Fix:  |

So the class "a name outside the list is reached through a trick" is closed by the walk, not only by the check. The tricks of the earlier report that rely on it (attribute walking, dunder, format strings, comprehension, lambda, builtins, conditional) are refused twice: by the check and by the walk. Also closed: Python's own methods on literals (8 names, above), and a function object passed as a value.

Mutation check of the walk (RAN: `mutation1.txt`, `mutation2.txt`): when the module lookup uses `getattr` with the text's name and the underscore guard is removed, 3 tests fail (the source test, `pl.__name__`, `[pl.read_csv]`). When `+` is built as `-`, 2 tests fail. `pl.os.getpid()` was still refused after the first break, because the next step (`.getpid` on a module) is refused by the walk's type check: two layers inside the walk.

**Does NOT remove (with evidence).**
- A wrong entry in the list. D calls what the list allows. READ: `formula_check.py:15-17`: until 2026-11-17 `Expr.deserialize` was allowed by name and could read any file. D would have called it just the same.
- Members dangerous by what they do. None known today after `inspect` (D-0229). The check and D cannot see one.
- Polars panics: D calls the same functions (section C: `pl.Array` in `json_decode`, RAN).
- Memory and time: lines 45, 46, 51 (accepted by both, REASONED: the same Polars call) and 111 (constant powers: both compute them in Python). D could refuse a constant calculation that grows too large because it does the operation itself; today's way cannot. Not built.
- `shuffle` and `sample` without a seed, and `rank(method='random')`: refused already by the check (D-0278, D-0279) and so refused by D. D adds nothing.
- `hash()` instability across Polars versions: same.

## B5. Error messages (RAN: `b2_constructs.json`, `b2_output.txt`)

- For a part the check refuses, D shows the same message, because it is the same function: 136 of 136 refused texts and 23 of 23 constructs have the same message.
- Today's messages carry no place in the formula. Example: `the attribute '__class__' starts with an underscore. Fix: build the column with pl.col, ...`. The check has the syntax tree, so it could give the character position for every refusal. That is a change to the check and does not need D.
- For what only D's walk refuses, the message has the place: `the attribute 'sort' is not allowed here: only a column expression has methods (character 1). Fix: build the column with pl.col, pl.lit, pl.when and the Polars expression methods.` and `a function or the name pl is left uncalled (character 2). Fix: call it, for example pl.col('x').`
- A Polars error while building (wrong number of arguments, `bool` of a column) gives the same text as today (`the formula '...' could not be built: ... Suggestion: check the arguments of each call against the Polars documentation`).

## B6. Cost

- Code: `formula_build.py` 269 lines (204 of code, with the docstring). The earlier estimate was about 400 lines. The test file `test_formula_build.py` 200 lines (160 of code). Today's check stays as it is: `_Checker` and the parse take about 190 lines of `formula_check.py` (`:283-475`), and 2 lines are the `eval` (`:508`, `:517`). RAN: `git diff --stat`: 469 lines added, none removed.
- Speed, build time only (RAN: `b6_cost.py`, 169 formulas, median of 15 runs): check alone 44 µs per formula; today (check + eval) 108 µs; D (check + walk) 98 µs. First call: tables of D 0.95 ms. No measurable cost.
- What would change in the app if D replaced today's way:
  - `libs/transformer/src/transformer/actions/polars_calls.py:31,195` (`_formula`): `evaluate_formula` becomes `build_formula`. One import and one call. The `except FormulaError` and `except Exception` stay.
  - `libs/id_reconciliation/src/id_reconciliation/core.py:6,254`: the same.
  - `libs/utils/src/utils/recipe_check.py:41,601`: uses `formula_problems` only; no change.
  - `formula_check.py`: `evaluate_formula`, `EVAL_GLOBALS` and the `eval` line go (or stay for the tests). The private names that D reads become public.
  - Tests: 6 test files import `evaluate_formula` (`test_formula_check`, `test_formula_element_field`, `test_formula_reads_no_outside_data`, `test_formula_refusals_2026_11_18`, `test_formula_refuses_object`, `test_formula_refuses_random`); with D patched in they pass (1597 of 1597). They would import the new name.
  - Documents: `recipe_format_spec.md` section 15 ("run with empty builtins"), the `@deps` blocks, `dependency_index.md`, the check rule ST06 text.
- Effort tag, as information only (D-0268): [sonnet/medium]. The prototype took one session. Production would add: public names, one walk or a drift test, the doc updates, and the untested exponent limit.

## B7. Options B and C of question 18

- B, a structure in YAML: a formula is written as nested mappings (the earlier scientist converted five formulas to 14 and 17 lines of YAML for one line of text). No text is evaluated.
- C, an own small language with an own parser: a formula is written in a smaller grammar (shorter than Polars text; a parser of our own, a result tied to the parser version). No text is evaluated.
- Once D exists, my evidence shows D gives the first reason for B and C (no text evaluated, the written form unchanged, results equal on the real data). I did not test B or C. What my evidence cannot judge and D does not give: B and C name their own functions, so a Polars upgrade does not change what a formula means (D follows Polars: the lists are read from the installed Polars and `hash()` changes between versions, REASONED for B and C); and B and C can put a rule on an argument (a type, a range) in a table, which D leaves to Polars. Length to write and readability: no new evidence from me; the earlier reports hold the numbers.

