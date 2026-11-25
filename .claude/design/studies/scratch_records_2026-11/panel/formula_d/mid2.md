
## A3. The 60 hostile lines through today's check on this `dev` (RAN: `a3_b3_hostile.py`, `a3_b3_table.json`)

The lines are read from `tmpAI/panel/formula_safety/hostile.py` (not retyped). Only the expression is built; nothing is collected. The numbers are the position in that file, from 1.

Result: 54 REFUSED, 6 ACCEPTED. Since the earlier report (8 accepted) the three lines about `pl.Object` (D-0230), `shuffle` and `sample` (D-0278, D-0279) are refused.

The 6 accepted, and what each does (RAN: `a3_accepted_run.txt`, on a small table):

| # | line | what it does | risk |
|---|---|---|---|
| 35 | `pl.col('a').bin.decode('hex')` | on a text column: SchemaError ("expected Binary"). On a binary column: decodes hex text to bytes (`b'6162'` gives `b'ab'`). | None found. It reads no file. |
| 39 | `pl.lit('/etc/passwd')` | a column that holds the text `/etc/passwd`. No file is read. | None. It is a text value. |
| 59 | `pl.col('a').list.eval(pl.element())` | allowed on purpose (D-0231, `formula_check.py:58-61`); returns the list column unchanged. | None. |
| 45 | `pl.col('a').repeat_by(10**12)` | builds an expression for a list of a trillion copies per row. NOT built here (size). Earlier report: accepted, "D-0064: no size limit now". | Memory. |
| 46 | `pl.lit('a') * 10**9` | text times a number. NOT built here (size). | Memory. |
| 51 | `pl.col('a').cast(pl.String).str.pad_start(4000000000)` | pads text to 4 billion characters. NOT built here (size). | Memory. |

None of the 6 runs code or reads outside the data (READ for 45, 46, 51: not run; the earlier report names them as memory). The check accepts them, so they would run in the app today.

The full table (the 20 new lines follow it):

| # | class | line | today's check | message (first 70 chars) | D with check | D walk alone |
|---|---|---|---|---|---|---|
| 1 | attribute walking | `pl.col('a').__class__` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 2 | attribute walking | `pl.col('a').str.__class__.__mro__` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 3 | attribute walking | `pl.Expr.__subclasses__()` | REFUSED | pl.Expr is not allowed. Fix: use one of: all, all_horizontal, any, any | REFUSED | REFUSED |
| 4 | attribute walking | `pl.col('a').__init__.__globals__` | REFUSED | the attribute '__init__' starts with an underscore. Fix: build the col | REFUSED | REFUSED |
| 5 | attribute walking | `pl.os.system('id')` | REFUSED | pl.os is not allowed. Fix: use one of: all, all_horizontal, any, any_h | REFUSED | REFUSED |
| 6 | attribute walking | `pl.sys.modules` | REFUSED | pl.sys is not allowed. Fix: use one of: all, all_horizontal, any, any_ | REFUSED | REFUSED |
| 7 | dunder | `().__class__.__bases__[0].__subclasses__()` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 8 | dunder | `pl.__builtins__` | REFUSED | the attribute '__builtins__' starts with an underscore. Fix: build the | REFUSED | REFUSED |
| 9 | dunder | `pl.col('a').__reduce__()` | REFUSED | the attribute '__reduce__' starts with an underscore. Fix: build the c | REFUSED | REFUSED |
| 10 | dunder | `pl.__spec__.loader` | REFUSED | the attribute '__spec__' starts with an underscore. Fix: build the col | REFUSED | REFUSED |
| 11 | format strings | `'{0.__class__}'.format(pl)` | REFUSED | format is not an expression method. Fix: build the column with pl.col, | REFUSED | REFUSED |
| 12 | format strings | `pl.col('a').inspect('{0.__init__.__globals__}')` | REFUSED | inspect prints the column to the server output with a text that can re | REFUSED | REFUSED |
| 13 | format strings | `pl.format('{}', pl.col('a')).__class__` | REFUSED | the attribute '__class__' starts with an underscore. Fix: build the co | REFUSED | REFUSED |
| 14 | format strings | `f'{pl.__file__}'` | REFUSED | JoinedStr is not allowed in a formula. Fix: build the column with pl.c | REFUSED | REFUSED |
| 15 | comprehension scopes | `[c for c in ().__class__.__mro__]` | REFUSED | ListComp is not allowed in a formula. Fix: build the column with pl.co | REFUSED | REFUSED |
| 16 | comprehension scopes | `[x for x in (1,2)]` | REFUSED | ListComp is not allowed in a formula. Fix: build the column with pl.co | REFUSED | REFUSED |
| 17 | comprehension scopes | `{k: v for k, v in [(1, 2)]}` | REFUSED | DictComp is not allowed in a formula. Fix: build the column with pl.co | REFUSED | REFUSED |
| 18 | comprehension scopes | `(x for x in [1])` | REFUSED | GeneratorExp is not allowed in a formula. Fix: build the column with p | REFUSED | REFUSED |
| 19 | lambda | `(lambda: __import__('os'))()` | REFUSED | Lambda is not allowed in a formula. Fix: build the column with pl.col, | REFUSED | REFUSED |
| 20 | lambda | `pl.col('a').map_elements(lambda v: v)` | REFUSED | map_elements runs a Python function and is not allowed. Fix: build the | REFUSED | REFUSED |
| 21 | lambda | `pl.col('a').map_batches(print)` | REFUSED | map_batches runs a Python function and is not allowed. Fix: build the  | REFUSED | REFUSED |
| 22 | lambda | `pl.col('a').pipe(print)` | REFUSED | pipe runs a Python function and is not allowed. Fix: build the column  | REFUSED | REFUSED |
| 23 | builtins | `eval('1+1')` | REFUSED | the name 'eval' is not allowed; only pl is known. Fix: write pl.<funct | REFUSED | REFUSED |
| 24 | builtins | `exec('import os')` | REFUSED | the name 'exec' is not allowed; only pl is known. Fix: write pl.<funct | REFUSED | REFUSED |
| 25 | builtins | `open('/etc/passwd').read()` | REFUSED | the name 'open' is not allowed; only pl is known. Fix: write pl.<funct | REFUSED | REFUSED |
| 26 | builtins | `getattr(pl, 'read_csv')` | REFUSED | the name 'getattr' is not allowed; only pl is known. Fix: write pl.<fu | REFUSED | REFUSED |
| 27 | builtins | `print(pl)` | REFUSED | the name 'print' is not allowed; only pl is known. Fix: write pl.<func | REFUSED | REFUSED |
| 28 | imports | `__import__('os').system('id')` | REFUSED | the name '__import__' is not allowed; only pl is known. Fix: write pl. | REFUSED | REFUSED |
| 29 | imports | `import os` | REFUSED | the formula is not a valid expression (SyntaxError). Fix: write one Py | REFUSED | REFUSED |
| 30 | imports | `pl.col('a') if True else __import__('os')` | REFUSED | IfExp is not allowed in a formula. Fix: build the column with pl.col,  | REFUSED | REFUSED |
| 31 | serialised data | `pl.Expr.deserialize('/tmp/x.json')` | REFUSED | pl.Expr is not allowed. Fix: use one of: all, all_horizontal, any, any | REFUSED | REFUSED |
| 32 | serialised data | `pl.Expr.from_json('{}')` | REFUSED | pl.Expr is not allowed. Fix: use one of: all, all_horizontal, any, any | REFUSED | REFUSED |
| 33 | serialised data | `pl.col('a').meta.serialize()` | REFUSED | meta reads the structure of an expression and can write it to a file o | REFUSED | REFUSED |
| 34 | serialised data | `pl.col('a').str.json_decode(pl.Object)` | REFUSED | pl.Object holds any Python object, which a table column does not; a re | REFUSED | REFUSED |
| 35 | serialised data | `pl.col('a').bin.decode('hex')` | ACCEPTED |  | ACCEPTED | BUILT |
| 36 | file paths | `pl.read_csv('/etc/passwd')` | REFUSED | pl.read_csv is not allowed. Fix: use one of: all, all_horizontal, any, | REFUSED | REFUSED |
| 37 | file paths | `pl.scan_parquet('/etc/shadow').collect()` | REFUSED | pl.scan_parquet is not allowed. Fix: use one of: all, all_horizontal,  | REFUSED | REFUSED |
| 38 | file paths | `pl.read_json('x.json')` | REFUSED | pl.read_json is not allowed. Fix: use one of: all, all_horizontal, any | REFUSED | REFUSED |
| 39 | file paths | `pl.lit('/etc/passwd')` | ACCEPTED |  | ACCEPTED | BUILT |
| 40 | file paths | `pl.sql_expr('1')` | REFUSED | pl.sql_expr is not allowed. Fix: use one of: all, all_horizontal, any, | REFUSED | REFUSED |
| 41 | file paths | `pl.SQLContext()` | REFUSED | pl.SQLContext is not allowed. Fix: use one of: all, all_horizontal, an | REFUSED | REFUSED |
| 42 | plugins | `pl.col('a').register_plugin(lib='/tmp/x.so', symbol='f')` | REFUSED | register_plugin loads or reads something outside the expression (a fil | REFUSED | REFUSED |
| 43 | plugins | `pl.Config.set_tbl_rows(1)` | REFUSED | pl.Config is not allowed. Fix: use one of: all, all_horizontal, any, a | REFUSED | REFUSED |
| 44 | plugins | `pl.col('a').ext.to('x')` | REFUSED | ext is not an expression method. Fix: build the column with pl.col, pl | REFUSED | REFUSED |
| 45 | large allocations | `pl.col('a').repeat_by(10**12)` | ACCEPTED |  | not built (size) | not built (size) |
| 46 | large allocations | `pl.lit('a') * 10**9` | ACCEPTED |  | not built (size) | not built (size) |
| 47 | large allocations | `pl.col('a') ** 99999999` | REFUSED | an exponent must be a constant number up to 100. Fix: build the column | REFUSED | BUILT |
| 48 | large allocations | `pl.lit(10**10000)` | REFUSED | an exponent must be a constant number up to 100. Fix: build the column | REFUSED | OTHER:InvalidOperationError |
| 49 | large allocations | `pl.col('a').abs().abs().abs().abs().abs().abs().abs().abs()...` | REFUSED | the formula is longer than 2000 characters. Fix: split it into several | REFUSED | OTHER:RecursionError |
| 50 | large allocations | `pl.lit('x'*5000)` | REFUSED | a text or a list cannot be multiplied or formatted with an operator. F | REFUSED | BUILT |
| 51 | large allocations | `pl.col('a').cast(pl.String).str.pad_start(4000000000)` | ACCEPTED |  | not built (size) | not built (size) |
| 52 | nondeterminism | `pl.col('a').shuffle()` | REFUSED | shuffle draws at random, so the result would differ at each run and th | REFUSED | REFUSED |
| 53 | nondeterminism | `pl.col('a').sample(n=3)` | REFUSED | sample draws at random, so the result would differ at each run and the | REFUSED | REFUSED |
| 54 | others | `pl.col('a') << 5` | REFUSED | << is not allowed. Fix: build the column with pl.col, pl.lit, pl.when  | REFUSED | REFUSED |
| 55 | others | `*pl.col('a')` | REFUSED | the formula is not a valid expression (SyntaxError). Fix: write one Py | REFUSED | REFUSED |
| 56 | others | `pl.col(*['a'])` | REFUSED | starred arguments are not allowed. Fix: build the column with pl.col,  | REFUSED | REFUSED |
| 57 | others | `pl.col(**{'name':'a'})` | REFUSED | ** arguments are not allowed. Fix: build the column with pl.col, pl.li | REFUSED | REFUSED |
| 58 | others | `pl.col('a').__getattribute__('x')` | REFUSED | the attribute '__getattribute__' starts with an underscore. Fix: build | REFUSED | REFUSED |
| 59 | others | `pl.col('a').list.eval(pl.element())` | ACCEPTED |  | ACCEPTED | BUILT |
| 60 | others | `pl.col('a').list.eval(pl.col('a').map_elements(print))` | REFUSED | map_elements runs a Python function and is not allowed. Fix: build the | REFUSED | REFUSED |

New lines (my own, harmless to build):

| # | class | line | today's check | today builds | D builds |
|---|---|---|---|---|---|
| 101 | python method on a literal | `[3, 1, 2].sort()` | ACCEPTED | ACCEPTED  | REFUSED the attribute 'sort' is not allowed here: only a column expr |
| 102 | python method on a literal | `pl.lit('abc').str.len_chars() + 'abc'.count('a')` | ACCEPTED | ACCEPTED  | REFUSED the attribute 'count' is not allowed here: only a column exp |
| 103 | python method on a literal | `(1).abs()` | ACCEPTED | OTHER:AttributeError 'int' object has no attribute 'abs' | REFUSED the attribute 'abs' is not allowed here: only a column expre |
| 104 | function left uncalled | `[pl.col]` | ACCEPTED | ACCEPTED  | REFUSED a function or the name pl is left uncalled (character 2). Fi |
| 105 | function left uncalled | `{'f': pl.col}['f']('a')` | ACCEPTED | ACCEPTED  | REFUSED a function or the name pl is left uncalled (character 7). Fi |
| 106 | chained comparison | `pl.col('a') < pl.col('b') < 3` | ACCEPTED | REFUSED the formula "pl.col('a') < pl.col('b') < 3" could  | REFUSED the formula "pl.col('a') < pl.col('b') < 3" could not be bui |
| 107 | and/or on columns | `pl.col('a') and pl.col('b')` | ACCEPTED | REFUSED the formula "pl.col('a') and pl.col('b')" could no | REFUSED the formula "pl.col('a') and pl.col('b')" could not be built |
| 108 | repeated keyword | `pl.lit(1, dtype=pl.Int64, dtype=pl.Int64)` | ACCEPTED | OTHER:SyntaxError keyword argument repeated: dtype (<formula>, line  | REFUSED the formula 'pl.lit(1, dtype=pl.Int64, dtype=pl.Int64)' coul |
| 109 | subscript of the module | `pl['col']` | ACCEPTED | REFUSED the formula "pl['col']" could not be built: 'modul | REFUSED a function or the name pl is left uncalled (character 1). Fi |
| 110 | call of a column | `pl.col('a')()` | ACCEPTED | REFUSED the formula "pl.col('a')()" could not be built: 'E | REFUSED this cannot be called (character 1). Fix: call a pl function |
| 111 | power of a power (time) | `pl.lit((((10**100)**100)**100)**100)` | ACCEPTED | NOT BUILT (check only)  | NOT BUILT (check only)  |
| 112 | large allocation | `pl.col('a').repeat_by(10**12)` | ACCEPTED | NOT BUILT (check only)  | NOT BUILT (check only)  |
| 113 | large allocation | `pl.col('a').cast(pl.String).str.pad_start(4000000000)` | ACCEPTED | NOT BUILT (check only)  | NOT BUILT (check only)  |
| 114 | regex time | `pl.col('a').str.contains('(a+)+$')` | ACCEPTED | ACCEPTED  | ACCEPTED  |
| 115 | dtype names | `pl.col('a').cast(pl.Unknown)` | REFUSED | REFUSED pl.Unknown is not a real type for a column: a cast | REFUSED pl.Unknown is not a real type for a column: a cast to it sil |
| 116 | dtype names | `pl.col('a').str.json_decode(pl.Binary)` | REFUSED | REFUSED pl.Binary holds raw bytes, which a recipe table do | REFUSED pl.Binary holds raw bytes, which a recipe table does not hol |
| 117 | random | `pl.col('a').rank(method='random')` | REFUSED | REFUSED rank with method 'random' breaks ties at random, s | REFUSED rank with method 'random' breaks ties at random, so the resu |
| 118 | random | `pl.col('a').shuffle()` | REFUSED | REFUSED shuffle draws at random, so the result would diffe | REFUSED shuffle draws at random, so the result would differ at each  |
| 119 | random | `pl.col('a').sample(n=3)` | REFUSED | REFUSED sample draws at random, so the result would differ | REFUSED sample draws at random, so the result would differ at each r |
| 120 | random | `pl.col('a').rank(method=pl.lit('x').meta.output_name())` | REFUSED | REFUSED meta reads the structure of an expression and can  | REFUSED meta reads the structure of an expression and can write it t |

Reading of the new lines (RAN):
- Lines 101 to 105 are accepted today and run Python: `[3, 1, 2].sort()` really sorts a list in place and returns `None`; `'abc'.count('a')` runs the text method. The check allows a method on a number, text, list or dictionary when its name is also an `Expr` method. Names that coincide (RAN: `b4_literal_methods.txt`): text `count`, `replace`; list `append`, `count`, `reverse`, `sort`; tuple `count`; dictionary `get`. None of them reads a file or runs code, so the risk today is nil. It is a door that depends on Polars' own method names. `(1).abs()` ends with a raw `AttributeError`, not a plain message (line 103).
- Lines 104 and 105: a function name left uncalled inside a list or a dictionary is accepted today (`[pl.col]` returns a list with a Polars function inside).
- Line 108: a repeated keyword gives a raw `SyntaxError` today (not caught as `FormulaError`).
- Line 111: `pl.lit((((10**100)**100)**100)**100)` is accepted. Every exponent is at most 100, but the powers multiply: the result would have about 332 million bits. RAN: 2 levels take 0.3 ms, 3 levels take 0.32 s (3.3 million bits). The fourth level was NOT run (REASONED: minutes and about 40 MB). Both today's way and D would compute it, because Python does the arithmetic on constants.
- Line 114: `str.contains('(a+)+$')` is accepted and is not a time bomb: 0.2 to 3.6 ms for 30 to 30000 characters (RAN: `b4_regex_time.txt`; Polars' regex engine has no backtracking).

## A4. What today's check guarantees, what it does not, what is unproven

**The text is evaluated with `eval`.** READ: `formula_check.py:517`: `eval(compile(ast.parse(text.strip(), mode="eval"), "<formula>", "eval"), dict(EVAL_GLOBALS))`. The visible names: `EVAL_GLOBALS = {"__builtins__": {}, "pl": pl}` (`formula_check.py:508`): only `pl`, and no builtins. `pl` is the real Polars module, so `pl.os` is visible (RAN: `hasattr(pl, 'os')` is True).

**What stops a name outside the list from being reached.** READ: the check. It refuses any name other than `pl` (`:305-309`), any attribute that starts with `_` (`:315-317`), `pl.<name>` that is not in `MODULE_FUNCTIONS` or a dtype (`:319-328`), and any method that is not in `_allowed()` (`:343-358`). The second layer (empty builtins) does NOT stop a reach through `pl`. RAN (`weak_table.md`, below): with the check switched off, `eval` ran 10 of 12 harmless probes, among them `pl.os.getpid()`, `pl.__name__` and `[x for x in (1, 2)]`. Only `len(...)` and `eval(...)` failed (no builtins). So today the check is the only barrier against `pl.os.system(...)`.

**What today's check guarantees (with the test that pins it).** RAN: `a4_mutations.py` breaks the check once per rule and counts the failing tests among the 6 formula test files (527 tests):

| Rule broken | Tests that fail | Where |
|---|---|---|
| any name allowed (only `pl` known) | 10 | `test_formula_check.py` (9), `test_formula_refuses_random.py` (1) |
| any `pl.<name>` allowed (the module list) | 60 | `test_formula_check`, `test_formula_element_field`, `test_formula_refusals_2026_11_18`, `test_formula_refuses_object` |
| the refused-by-name list ignored (`inspect`, `meta`, `set_sorted`, `search_sorted`, `shuffle`, `sample`) | 40 | four files |
| functions as arguments allowed (`map_elements`, `pipe`) | 30 | four files |
| classmethods allowed (`deserialize`, `from_json`) | 20 | `test_formula_reads_no_outside_data.py` |
| outside names (`lib`, `path`) allowed | 15 | two files |
| the dtype refusals removed (`Object`, `Unknown`, `Binary`) | 53 | three files |
| the random rank check removed | 43 | `test_formula_refuses_random.py` |
| **the underscore rule removed** | **0** | no test fails |
| **the exponent limit raised to a billion** | **0** | no test fails |

Two rules have no test that fails when they are broken. The underscore rule is covered by the list (RAN: `a4_underscore_without_rule.txt`: with the rule removed, `__class__`, `__reduce__` and `pl.__name__` are still refused, as "not an expression method"), so it is a second layer. The exponent limit (`pl.col('a') ** 99999999`, `MAX_EXPONENT = 100`, `formula_check.py:52`) has no test at all: a change of the limit would go unseen.

Of the 60 hostile lines, 9 are exact texts in a test file (RAN: `b_corpus.py`); the classes are pinned by tests with other texts (table above). The trial test `libs/utils/tests/test_formula_build.py` adds the 54 refused lines.

**What today's check does not guarantee.**
- It reads signatures and parameter names; it cannot see a member that is dangerous by what it does. READ: the code says it is "a net with holes, not a proof" (`formula_check.py:206-211`). Two holes were found on 2026-11-17 (`deserialize`, `inspect`; `:15-17`, `:143-145`).
- Polars panics: a panic is a `BaseException`, not caught (`polars_calls.py:199` catches `Exception`). One is left (section C).
- Memory and time: lines 45, 46, 51, 111 (above). D-0064: "no time or size limit now".
- Python's own methods on a literal (lines 101 to 105): harmless today, a door that depends on Polars' names.
- `hash()` is allowed and its values change between Polars versions (READ: the Polars docstring of the installed 1.40.1: "does not guarantee stable results across different Polars versions").

**What remains unproven.** That the allowed lists (196 `Expr` members, 40 module functions, 150 namespace members: `str` 49, `dt` 47, `list` 41, `arr` 30, `cat` 6, `struct` 5, `name` 8, `bin` 11, RAN) hold no other member that is dangerous by effect. The walk test reads signatures and the words of the documentation; I did not read each of the members. I did not search for other panics than `json_decode`.

