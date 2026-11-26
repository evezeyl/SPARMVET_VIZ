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
