# Findings of the equality check (EQUALITY-CHECK-1, PROVISIONAL, 2026-11-15)

What was compared: every table of the recipe `2_test_data_ST22_dummy` as the engine builds it, against the same table
written by hand in plain Polars and plotnine from the meaning of the recipe (`reference_2_test_data_ST22_dummy.py`),
on the shipped clean data and on a deliberately dirty copy (`data/dirty/EDITS.md` lists every edit). Nothing in the
engine, the shipped recipe or the shipped data was changed. A difference is kept as a failing test in
`test_findings_open.py` (not collected by default; `README.md` says how to run it).

Result in one line: on the clean data all 22 comparisons are equal; on the dirty data 16 of 22 are equal and 6 differ
(all from F1); a second dirty run with the recipe's own `null_values: []` gives 5 differences (F2).

## Differences (engine and hand-written side give different results)

### F1. A missing phenotype is counted as a resistance class (`Multiresistant`, table `AMR_Profile_Joint`)
- **Recipe says** (`assembly/AMR_Profile_Joint.yaml`, step 4 comment): "sample carries >1 distinct resistance class";
  README: "isolates resistant to >= 2 antimicrobial classes". The expression is
  `pl.col('predicted_phenotype_clean').n_unique().over('sample_id') > 1`.
- **Engine gives:** `Yes` for sample `20545497`, which has one phenotype (`tetracycline`) and one row whose phenotype is
  missing. Polars `n_unique` counts a missing value as a value, so the sample has "2 values".
- **Hand side gives:** `No` (a missing phenotype is not a class; `drop_nulls().n_unique()`).
- **Rows:** 2 of 64 rows of `AMR_Profile_Joint` (dirty data, table index 8 and 9); the plot data and the bars of both
  AMR plots (`multi_resistance_by_country`, `multi_resistance_by_source`) follow: 4 more failing cases. The
  plot-drawing itself is equal when the hand-written plot is given the engine's table (`plot_isolated` cases pass).
- **Reading:** the engine is faithful to the recipe's expression; the recipe's expression is wrong against its own
  stated meaning. Not an engine bug; a recipe error that the shipped data cannot show (no missing phenotype there).
  The fix belongs in the recipe (count the non-missing values) or in an explicit choice by Eve.

### F2. `null_values: []` does not make an empty cell a text; the engine reads it as missing
- **Recipe says** (spec 7.3, DEC28): `null_values` lists the texts that mean missing, `[]` is allowed and then no text
  is missing; ingestion "reads text, applies them, then casts" and "the reader fails strictly and names the value".
  The shipped recipe states `null_values: []`.
- **Engine gives** (shipped recipe's rule, dirty data staged as `..._dirty_no_null_text`): all five tables are built.
  An empty `Year`, `%Identity`, `%Overlap` cell becomes a missing number; an empty `Country` becomes null (while a
  `Source` of only spaces becomes the empty text `""`: the two empty cells are not treated alike).
- **Hand side gives:** the reading is refused for the three data files (`conversion from str to f64 failed ... [""]`),
  and for a text column an empty cell would stay `""`.
- **Rows:** metadata 1 empty Year and 1 empty Country; ResFinder 1 empty identity, 1 empty overlap, 1 empty phenotype,
  1 empty gene; PlasmidFinder similar (`data/dirty/EDITS.md`).
- **Reading:** either the engine does not apply `null_values` as specified (the reader's own "empty field is null"
  survives), or the spec means "an empty field is always missing" and the spec text is ambiguous. On the shipped data no
  cell is empty, so the shipped recipe never meets it. A scientist who writes `[]` believes nothing is missing.

## Not differences, but a scientist would be misled (engine and hand side agree)

- **Rows dropped silently by an inner join.** Dirty data: ResFinder 4 rows (keys `84937100`: 1, `99999991`: 2, a missing
  key: 1), PlasmidFinder 8 rows (`84937100`: 5, `99999992`: 2, a missing key: 1). The engine's printed log has no line
  about it and no table or count is returned. Clean data: 0 (4 metadata samples have no ResFinder row, 1 has no
  PlasmidFinder row; those are not rows of the plotted table).
- **A repeated key on the metadata side multiplies rows.** Sample `36428015` has two metadata rows (Parent/Norway and
  Layer/Germany): its single ResFinder hit appears twice, in two countries (+1 row in AMR, +6 rows in plasmid).
  No warning; the join is many-to-many by `how: inner` alone.
- **A NaN passes `ge` filters.** A NaN identity or overlap is a number in Polars, so `NaN >= 90` is true and the row is
  kept (the action text says so). Kept: ResFinder 2 rows (samples `12244317`, `61096143`), PlasmidFinder 1 row
  (`43436587`). Filter edges are right: exactly 90 and exactly 60 are kept, 89.9999 and 59.9999 are removed, 90.0001
  and 60.0001 kept, a missing value removed (`na: remove`).
- **The bars count rows, not samples.** The titles speak of multi-resistance and plasmid prevalence; each bar counts
  hits (genes, plasmids). Clean data: AMR plots 70 rows for 38 samples; plasmid plot 163 rows for 41 samples. Dirty:
  64 rows for 33 samples; 160 for 40.
- **Text is not cleaned beyond `strip`.** `norway` and `Norway` are two panels; the text `NA` (Namibia) stays a country
  only because the staged recipe lists `[""]` and not `NA`; a missing Country is a panel of its own (1 row); two
  missing Years (`11843673`, 2 rows) sort first. `Kanamycin` and ` kanamycin ` are one class (the recipe cleans it).
- **A Year that is not whole.** Plain Polars `cast(Int64)` turns 2023.5 into 2023 without a word. The engine refuses it
  and names the values (checked: both sides refuse, `fractional_year`). Safe; noted because the recipe comment ("float
  to Int64 to String") does not say it.
- **Order.** The recipe states no row order for the three data schemas, and no rule where missing values go in
  `polars_sort`. Both are equal to the plain-Polars defaults today (file order; missing first). Listed in `README.md`.
- **Source and Country sort by their text, not by first appearance.** Checked on the dirty data: equal.
- **The `Multiresistant` flag is computed after the filters and the join** (the recipe's step order). In the dirty data
  no sample changed (14 multi-resistant samples before and after); the effect is possible, not shown.

## Choices made on the hand-written side where the recipe is silent

A missing phenotype is not a class (F1); an empty cell is a text, not a missing value, unless `null_values` says so
(F2); a non-whole Year is refused; ascending sort, missing first, Source and Country by their text. A reading of Eve's
that differs turns a finding into an agreement or the other way round.
