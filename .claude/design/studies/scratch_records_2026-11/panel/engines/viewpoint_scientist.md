SCIENTIST AND DATA SCIENTIST REPORT: mixed Polars and R engines in one recipe

Scratch: /home/evezeyl/Documents/Insync/gdrive/OBSWORK/20_GITS/SPARMVET_VIZ/tmpAI/panel/engines/scientist/ (p.py, r.R, t.parquet, t.csv). Nothing in the repo was edited.

## What I could and could not run
- R 4.5.3 is installed. No R packages beyond base are installed: arrow, dplyr, ggplot2 and nanoparquet are all absent (verified, run).
- So the Parquet round trip in R was not run. Claims about dplyr, arrow and ggplot2 are marked "reasoned (documentation, not run)".
- I did run Polars 1.40.1 against base R, and CSV as the bridge. Base R shares R's NA, NaN, sort, round and factor rules.
- Polars schema written to Parquet: Enum, Categorical, Date, Datetime with zone Europe/Oslo, Int64 with null, Boolean with null, String with "", null and " a", Int64 above 2^53, Float64 with NaN and null.

## 1. Handing data from Polars to R and back
| Item | Result | Label |
|---|---|---|
| Null vs NaN in a float column | Polars keeps both (null_count 1, nan_count 1). R keeps both (NA and NaN) from CSV. R's `is.na()` is TRUE for both. | verified (run) |
| Empty string vs null | CSV merges them: R reads both as "". Parquet and Arrow keep the difference; arrow maps null to NA_character_ and "" stays "". | CSV verified (run); Parquet reasoned |
| Int64 above 2^53 | Via CSV, R reads a double. `2^53+1 == 2^53` is TRUE in R, so distinct IDs collide. arrow downcasts int64 to int32 when it fits, otherwise gives double, unless `integer64` is requested. | verified (run) for double; arrow reasoned |
| Boolean with null | CSV gives character "true", "false" and "". Parquet gives logical with NA. | CSV verified (run); Parquet reasoned |
| Datetime with zone | CSV writes an offset string. Parquet stores UTC plus the zone name. R POSIXct carries one zone attribute, and a missing attribute means the R session zone (here Europe/Oslo). | CSV verified (run); Parquet reasoned |
| Date | R reads Date from Parquet. Plain CSV gives character. | CSV verified (run); Parquet reasoned |
| Categorical and Enum | CSV gives character. In R, `factor()` sorts levels alphabetically in the session locale (hi, lo, mid), not in the Enum order lo, mid, hi. | verified (run) |
| Row and column order | Parquet keeps both. | reasoned |

Polars sorts an Enum by its declared order (lo, mid, hi) and a Categorical by a different rule (hi, hi, lo, mid). That is already a trap before R is involved (verified, run).

What changes a result or a picture:
- An ID collision merges two samples in a join or a count.
- A factor order gives a different axis or legend order.
- A time zone gives a different day or a different hour.
- Losing the null vs "" difference changes a "how many missing" count.
- A silent int to double conversion changes IDs and counts.

## 2. The same step in two engines (base R vs Polars)
| Step | Polars | R | Label |
|---|---|---|---|
| `x > 2` on `[1, NaN, null, 3]` | `[F, T, null, T]`: NaN counts as greater than 2 | `[F, NA, NA, T]` | verified (run) |
| Filter keeps NaN rows? | Yes, for `> 2` | No: base `[` gives `NA NA 3`. dplyr `filter` drops NA and NaN rows. | `[` verified (run); dplyr reasoned |
| Round of 0.5, 1.5, 2.5 | 0, 2, 2 (checked here on those inputs) | 0, 2, 2 | verified (run) |
| Round to 2 decimals of 2.675 and 1.005 | 2.68 and 1.0 | 2.67 and 1.00 | verified (run) |
| Sort of "a", "A", "b", "B", "_x", "9", "10", null, "" | Bytewise: "", "10", "9", "A", "B", "_x", "a", "b"; null first | Locale en_US: "", "_x", "10", "9", "a", "A", "b", "B". Under the C locale it matches Polars. NA is dropped. | verified (run) |
| Join on a null key | Not matched by default (`nulls_equal=False`). With `nulls_equal=True` the null rows match. | `merge` matches NA with NA. dplyr `na_matches="na"` does the same. | Polars and base R verified (run); dplyr reasoned |
| Join keys " a" vs "a", or "A" vs "a" | No match (0 rows) | No match | Polars verified (run); R reasoned |
| `group_by` | Order not guaranteed unless `maintain_order` is set (matches DEC34) | dplyr sorts groups by key | R reasoned |
| `unique` first | Needs `keep` and `maintain_order` | `distinct` keeps the first row | reasoned |
| Seeded sampling | Different generators | `set.seed(1); runif` and `sample` give R's own stream | `set.seed` verified (run) |

The Polars numbers, sort and NaN rows are covered by DEC29 (`na` required), DEC33 and DEC34 (determinism), and DEC41 (NaN handled in the recipe).

For the result not to depend on the engine, a recipe step would have to state:
- the missing-value rule, and the NaN rule separately from the null rule;
- whether null join keys match;
- the sort order, the collation (C or a named locale), nulls first or last, and tie handling;
- a `maintain_order` value;
- the rounding rule and the number of decimals;
- the seed and the random generator.

Even then, the sampling streams differ, so a seeded random step cannot be engine independent.

## 3. ggplot2 vs plotnine
- Defaults differ between the two, so parity of the pictures cannot be promised (reasoned; ggplot2 and plotnine not run).
- Binning: `geom_histogram` bins and the order of categories (factor levels vs pandas category) differ. The default theme (this project uses `theme_bw`), the fonts available, the size units, the jitter RNG and the legend layout also differ.
- The repo already has plotnine-only code: the plot receives pandas through `df.collect().to_pandas()` (viz_factory.py:262), and `random_state` is a plotnine seed.
- Parity is a risky promise. A ggplot2 plot should be its own plot kind with ggplot2's own names (verified, read of the spec naming rule, D-0091).
- Faithful rendering of the existing plotnine specs by ggplot2 is not defensible.

## 4. Reproducibility record
The export must record at least:
- R version and every package version actually loaded;
- the arrow or Parquet reader versions;
- the platform and locale (collation) and the time zone;
- the seed and the RNG kind;
- the full script text and its hash;
- the exact input file hash and the output hash;
- the engine name per unit.

The export currently has no engine field (scout, export_handlers.py has no data_engine or plot_engine field). Only the plotnine version is recorded (scout, export_handlers.py:104).

Safe units, from the science side:
| Unit | Verdict |
|---|---|
| Per recipe | Safe: one engine and no mixing. |
| Per plot, with the table handed over as Parquet | Safest mix. The tables have already been produced and audited by Polars, and R only draws. The risk is limited to type conversion and picture defaults. |
| Per table or per tier | Possible but needs a stated boundary. Each hand-off is a place for silent change. |
| Per step | Unsafe. NaN, null, sort and join differences apply at every step, and the checker cannot know the other engine's rules. |

## 5. The traps
- Two engines give different rows for the same step. Examples above: NaN in a filter, null join keys, sort collation, and rounding at 2 decimals. This is the largest risk.
- A silent fall-back to the default engine. The recipe would still run and give a picture, and nobody would know the R part had not run.
- The checker (recipe_check.py) cannot know steps of the second engine. The engine key is read only at top level (scout, recipe_check.py:218-221), and DEC32's equality test applies only to `polars_` actions.
- The cache keys have no engine version (scout, cache_keys.py:70-72), so a change of R or ggplot2 would not invalidate a cached result.
- A sample that disappears in R. `filter` drops NA rows, so a sample with a missing value can vanish without a message. The audit would not show it.
- A factor order set by locale: the axis order of a plot changes on another machine.
- Statistics computed in R before a removal can differ from those computed in Polars after it.
- The R script is code. It would run with the user's rights (DEC42 already refuses arbitrary file writes for the same reason).

## 6. Recommendation (reasoned, mine)
Allow now, in the format only, with nothing built:
- one `engine` field per plot entry, default taken from the top-level `plot_engine`;
- the plot engine switched only per plot, and only after the table has been written as Parquet by the data engine;
- an R plot entry that names the script, the input table, the types it expects and the seed;
- a checker error if a plot's engine is not installed, with no fall-back;
- the engine and its package versions written in the export for every unit.

Refuse for now:
- mixing data engines per step or per table;
- any promise of parity between plotnine and ggplot2;
- a default engine that is applied silently;
- an R plot that reads anything other than the declared Parquet input.

Per-table or per-tier data engines should wait until there is an equality-test method for dplyr like the `polars_` one (DEC32), and the recipe states the rules listed in section 2.

## Options table
| Option | For | Against | Evidence |
|---|---|---|---|
| A. One engine per recipe | Simplest to defend; matches DEC05 and the current checker | Cannot use ggtree or sf (the strongest use case, r_backend.md) | read |
| B. Engine per plot, data engine unchanged | R draws only; the data stays Polars and audited; the smallest boundary | Pictures differ from plotnine; needs new export fields and type rules | reasoned; type rules partly run |
| C. Data engine per table or tier | Allows dplyr work | Null, NaN, sort and join rules differ; the checker is blind to the second engine's steps | verified (run) for the differences |
| D. Engine per step | Maximum flexibility | Every step is a silent-change point; not defensible | reasoned |

## Told to Eve before she chooses
- What each type becomes at the Parquet boundary (section 1), once arrow is installed and checked.
- That ggplot2 pictures will not match plotnine pictures.
- That a mixed result needs more fields in the export.
- That engine-independent results need the recipe to state the rules in section 2.

## Not checked
- arrow, dplyr, ggplot2 and plotnine-vs-ggplot2 pictures (none run; R packages are not installed).
- The Parquet round trip into R and back.
- What the app currently does when it converts Polars to pandas (scout says reasoned only).
- Behaviour on Windows, Mac or other locales.
- Rscript start-up time and the sandbox security of running R.
