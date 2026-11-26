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
