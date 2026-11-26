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
