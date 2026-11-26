| What | Polars way | In Polars 1.40.1 | Accepted by the formula check | In the old lambda list | Max difference to the old way (absolute / relative) |
|---|---|---|---|---|---|
| sin | `pl.col("x").sin()` | yes | yes | yes | identical to the last bit |
| cos | `pl.col("x").cos()` | yes | yes | yes | identical to the last bit |
| tan | `pl.col("x").tan()` | yes | yes | yes | identical to the last bit |
| arcsin | `pl.col("x").arcsin()` | yes | yes | yes | identical to the last bit |
| arccos | `pl.col("x").arccos()` | yes | yes | yes | identical to the last bit |
| arctan | `pl.col("x").arctan()` | yes | yes | yes | identical to the last bit |
| sinh | `pl.col("x").sinh()` | yes | yes | yes | identical to the last bit |
| cosh | `pl.col("x").cosh()` | yes | yes | yes | identical to the last bit |
| tanh | `pl.col("x").tanh()` | yes | yes | yes | 1.1e-16 / 2.8e-16 |
| exp | `pl.col("x").exp()` | yes | yes | yes | identical to the last bit |
| log (natural) | `pl.col("x").log()` | yes | yes | yes | identical to the last bit |
| log10 | `pl.col("x").log10()` | yes | yes | yes | 4.4e-16 / 4.1e-16 |
| log2 | `pl.col("x").log(2)` | yes | yes | yes | 8.9e-16 / 2.2e-16 |
| log with a base (math.log(x, 10)) | `pl.col("x").log(10)` | yes | yes | yes | identical to the last bit |
| sqrt | `pl.col("x").sqrt()` | yes | yes | yes | identical to the last bit |
| abs | `pl.col("x").abs()` | yes | yes | yes | identical to the last bit |
| floor | `pl.col("x").floor()` | yes | yes | yes | identical to the last bit |
| ceil | `pl.col("x").ceil()` | yes | yes | yes | identical to the last bit |
| sign | `pl.col("x").sign()` | yes | yes | yes | identical to the last bit |
| math names: asin | `pl.col("x").arcsin()` | yes | yes | yes | identical to the last bit |
| math names: fabs | `pl.col("x").abs()` | yes | yes | yes | identical to the last bit |
| round (0 decimals), np.round | `pl.col("x").round(0)` | yes | yes | no | identical to the last bit |
| round half cases (-2.5..2.5 by 0.5) | `pl.col("x").round(0)` | yes | yes | no | identical to the last bit |
| arctan2(x, 2) | `pl.arctan2(pl.col("x"), 2)` | no | no | no | not compared |
| arctan2 method on Expr | `pl.col("x").arctan2(2)` | no | no | no | not compared |
| log1p | `pl.col("x").log1p()` | yes | yes | no | identical to the last bit |
| power, non-integer exponent 1.5 | `pl.col("x") ** 1.5` | yes | yes | yes | identical to the last bit |
| power 1.5 of negative x | `pl.col("x") ** 1.5` | yes | yes | yes | identical to the last bit |
| power, integer exponent 3 | `pl.col("x") ** 3` | yes | yes | yes | 1.4e-14 / 2.2e-16 |
| power, negative exponent -2 | `pl.col("x") ** -2` | yes | no | no | not compared |
| power by method .pow(1.5) | `pl.col("x").pow(1.5)` | yes | yes | yes | identical to the last bit |
| power with x as exponent: 2 ** x | `pl.lit(2.0) ** pl.col("x")` | yes | no | no | not compared |
| power with x as exponent: pl.lit(2).pow(x) | `pl.lit(2.0).pow(pl.col("x"))` | yes | yes | no | identical to the last bit |
| clip (min and max against constants) | `pl.col("x").clip(-1, 1)` | yes | yes | no | identical to the last bit |
| min against a constant (min(x, 1)) | `pl.min_horizontal(pl.col("x"), 1)` | yes | yes | no | identical to the last bit |
| max against a constant (max(x, 0)) | `pl.max_horizontal(pl.col("x"), 0)` | yes | yes | no | identical to the last bit |
| max(x,0) by clip lower bound | `pl.col("x").clip(lower_bound=0)` | yes | yes | no | identical to the last bit |
| constant pi | `3.141592653589793 * pl.col("x")` | yes | yes | yes | identical to the last bit |
| constant e | `2.718281828459045 ** pl.col("x")` | yes | no | no | not compared |
| pi by pl.lit | `pl.lit(3.141592653589793) * pl.col("x")` | yes | yes | yes | identical to the last bit |
| condition (when/then/otherwise) | `pl.when(pl.col("x") < 0).then(0).otherwise(pl.col("x"))` | yes | yes | no | identical to the last bit |
| normal density, mean 0, sd 1 | `(-0.5 * pl.col("x") ** 2).exp() / 2.5066282746310002` | yes | yes | yes | 5.6e-17 / 2.2e-16 |
| normal density, mean 1, sd 2 | `(-0.5 * ((pl.col("x") - 1) / 2) ** 2).exp() / (2 * 2.5066282746310002)` | yes | yes | yes | 2.8e-17 / 3.7e-16 |
| logistic 1/(1+exp(-x)) | `1 / (1 + (-pl.col("x")).exp())` | yes | yes | yes | identical to the last bit |
| cbrt (new in Polars) | `pl.col("x").cbrt()` | yes | yes | no | 4.4e-16 / 4.3e-16 |
| degrees | `pl.col("x").degrees()` | yes | yes | no | identical to the last bit |
| radians | `pl.col("x").radians()` | yes | yes | no | identical to the last bit |
| arcsinh | `pl.col("x").arcsinh()` | yes | yes | no | 4.4e-16 / 2.3e-16 |
| arctan2 with pl.lit second argument | `pl.arctan2(pl.col("x"), pl.lit(2))` | yes | no | no | not compared |
| power, negative exponent by .pow(-2) | `pl.col("x").pow(-2)` | yes | yes | no | identical to the last bit |
| power, negative exponent by 1 / x ** 2 | `1 / pl.col("x") ** 2` | yes | yes | no | 1.8e-12 / 2.2e-16 |
| e ** x by .exp() | `pl.col("x").exp()` | yes | yes | no | 5.7e-14 / 4.4e-16 |
| modulo x % 2 | `pl.col("x") % 2` | yes | yes | yes | identical to the last bit |
| floor division x // 2 | `pl.col("x") // 2` | yes | yes | yes | identical to the last bit |
