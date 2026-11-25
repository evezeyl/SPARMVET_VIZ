# `step_split_wide`: a design note for Eve (2026-11-18)

Status: DESIGN NOTE, nothing built. Written by a builder agent (opus) on 2026-11-18. Nothing here is decided by this note.
Eve reads it and decides. No shipped code, recipe, rule file or document was changed.

How to read the labels:
- **VERIFIED (ran)**: a script was run; the script and its output are named.
- **VERIFIED (read)**: the code was read at the file and line named.
- **EXTERNAL**: a library's own documentation, read on 2026-11-18.
- **REASONED**: my reasoning from the facts above it; not run.

The prototype scripts and their outputs are in `.claude/design/studies/scratch_records_2026-11/panel/wide_split/` (git-ignored):

| Script | What it shows | Output |
|---|---|---|
| `01_real_column.py` | The real gene-list columns of the demo recipe, read through the real ingestion | `01_real_column.out` |
| `02_polars_hard_cases.py` | What plain Polars does on every hard case | `02_polars_hard_cases.out` |
| `proto_step.py` | A scratch prototype of the step (not registered in the app) | (used by 03, 05, 06) |
| `03_equality_real_data.py` | The step against the explicit chain of `polars_` steps, on the real data | `03_equality_real_data.out` |
| `04_long_form.py` | The long form (one row per gene) and its counts | `04_long_form.out` |
| `05_cost_and_drift.py` | The cost of reading the width from the data; new data with more parts | `05_cost_and_drift.out` |
| `06_parameter_checks.py` | How the nested blocks are checked; one pitfall of a Polars parameter | `06_parameter_checks.out` |
| `07_tidyr_choices_in_polars.py` | Which tidyverse choices can be written with pure Polars | `07_tidyr_choices_in_polars.out` |
| `08_top_n_other_chain.py` | The existing `step_top_n_other` against an explicit chain | `08_top_n_other_chain.out` |

Run them from the project folder, for example `PYTHONPATH=.claude/design/studies/scratch_records_2026-11/panel/wide_split ./.venv/bin/python tmpAI/panel/wide_split/03_equality_real_data.py`. Polars 1.40.1.

## The decisions this note works from

- D-0264: "The `polars_` steps stay exactly as Polars does them." The new step has "a safeguard for too many and too few parts, the number of columns read from the data when the recipe does not say it, and counts of empty and missing cells in a visible note. NO automatic fill". "A design note comes first; nothing is built before her yes on the design."
- D-0265: "The wide split is a `step_` (a composite of several Polars steps), not a `modif_`." "When `fill` is not written there is NO fill". Three points are left to this note (section 4).
- D-0266: "How a `step_` passes parameters (Variant 1)." One nested block per composed step, "named after that Polars step, holding that step's own parameters with Polars' own names. An absent optional block means that step is not run." The step's own additions "only stop or warn; they never change a value." Two tests. Documentation "with special care". Apply the rule to the existing `step_` actions in this note, report only.
- D-0254: "A `modif_` component exists only when it does more than change argument values."
- D-0210 and D-0091: `polars_`/`plotnine_` = exact, `modif_` = a documented change, `step_` = a composite.
- D-0050: "No silent error that is the rule."
- D-0168: "Nothing should vanish silently in the audit".

## 0. In short

1. The step can be built as decided. On the real data it gives exactly the same table as the chain of Polars steps it composes (VERIFIED (ran), `03`).
2. One Polars step it needs does not exist in the app: `polars_list_to_struct`. The formula check refuses `list.to_struct`, because it can take a function (VERIFIED (ran) and (read), `libs/utils/src/utils/formula_check.py:119`). So today the explicit chain cannot be written without a workaround (section 1).
3. With the decided default (`too_few: error`), a real gene list always stops: 33 of the 42 cells of `genotype` have fewer than 8 genes (VERIFIED (ran), `03`, example 0). A gene list needs `too_few: warn` written in the recipe.
4. **No carrier exists today that takes a step's note to the screen or to the export** (VERIFIED (read): an action returns only a table, `libs/transformer/src/transformer/data_wrangler.py:133`; the join's warnings are printed only, `libs/transformer/src/transformer/data_assembler.py:37` "printed, not yet carried to the screen"). The decided visible note needs a new carrier. This is the largest part of the build.
5. Reading the number of columns from the data costs one pass over the data, and it cannot be lazy: Polars refuses `to_struct` without a number (VERIFIED (ran), `02` section O). The columns of the table then change when the data changes (VERIFIED (ran), `05` part 2).
6. Two pitfalls of plain Polars found by running: `fill_null(0)` on a text column writes the text `"0"` with no message (`02` section G); `fill_null(strategy: forward)` in a wide split copies genes from the sample above (`06` part 4).
7. Science caveat (REASONED): a gene list split by position puts different genes in the same column (`gene_3` is `sitABCD` in one sample and `dfrA17` in another). For presence or absence of a gene, the long form (one row per gene) is the usual way. The wide split fits a cell with a fixed structure, such as `"1203/1203"` (aligned length / total length).

## 1. What the author writes

### 1.1 The step

```yaml
- action: step_split_wide
  columns: [genotype]              # the step's own: one text column
  str_split: {by: ", "}            # polars_str_split, Polars' own names (always run)
  list_to_struct:                  # polars_list_to_struct (always run)
    fields: [gene_1, gene_2, gene_3, gene_4, gene_5, gene_6, gene_7, gene_8]
  unnest: {}                       # polars_unnest (always run; optional `separator`)
  str_strip_chars: {}              # polars_str_strip_chars on the new columns (OPTIONAL: absent = not run)
  fill_null: {value: "none"}       # polars_fill_null on the new columns (OPTIONAL: absent = no fill)
  too_many: error                  # the step's own: error (stop) or warn (go on, report)
  too_few: warn                    # the step's own: error or warn
```

- Each block is named after the Polars step without `polars_` (M281's example uses `str_split` and `fill_null`).
- The blocks run in a fixed order: split, to struct, unnest, strip, fill. The order in which the recipe writes them does not matter (REASONED: one order, so the same recipe always gives the same table).
- The step supplies `columns` to every block. A block may not hold `columns` or `target_column` (section 5).
- `too_many` and `too_few` only stop or warn. They never change a value (D-0266).

### 1.2 Example 1: the real `genotype` column, 8 named columns

The column (VERIFIED (ran), `01`): 42 rows; 4 missing cells (the text `None`, read as missing by `null_values`); 1 to 8 genes per cell; separator `", "`; no empty text; repeated genes inside a cell (`"blaTEM-1C, sitABCD, sitABCD"`).

The step:

```yaml
- action: step_split_wide
  columns: [genotype]
  str_split: {by: ", "}
  list_to_struct: {fields: [gene_1, gene_2, gene_3, gene_4, gene_5, gene_6, gene_7, gene_8]}
  too_many: error
  too_few: warn
```

The explicit chain that gives the same table:

```yaml
- action: polars_str_split
  columns: [genotype]
  by: ", "
- action: polars_list_to_struct        # does not exist today (see below)
  columns: [genotype]
  fields: [gene_1, gene_2, gene_3, gene_4, gene_5, gene_6, gene_7, gene_8]
- action: polars_unnest
  columns: [genotype]
```

Result (VERIFIED (ran), `03`, example 1): EQUAL. 42 rows, 10 columns (`sample_id, gene_1 ... gene_8, ST`), all text, same values, same order of rows and columns. The step also equals plain Polars written by hand.

What the author sees (the prototype's text):

> WARNING step step_split_wide, column 'genotype': 33 of 42 cells have fewer than 8 parts and would lack values: row 1 (3 parts: 'blaTEM-1C, sitABCD, sitABCD'), row 2 (2 parts: 'blaTEM-1B, sitABCD'), row 3 (5 parts: ...) and 30 more.
> NOTE ... 42 rows split into 8 columns (gene_1 ... gene_8); 4 missing cells (null), 0 empty cells (''), 0 empty parts.

The chain that can be written TODAY, without `polars_list_to_struct`: `polars_str_split`, then `polars_with_columns` with eight formulas `pl.col('genotype').list.get(i, null_on_oob=True)`, then `polars_drop`. It gives the same values, but the new columns come at the end of the table, not in the place of `genotype` (VERIFIED (ran), `03`: DIFFERENT in column order, EQUAL after reordering).

### 1.3 Example 2: the number of columns read from the data, with strip and fill

```yaml
- action: step_split_wide
  columns: [genotype]
  str_split: {by: ","}
  list_to_struct: {}            # no fields, no upper_bound: the step reads the width from the data (D-0264)
  str_strip_chars: {}           # strip spaces, Polars default (whitespace)
  fill_null: {value: "none"}
  too_many: error
  too_few: warn
```

The explicit chain (the width, 8, is what the step read from the data):

```yaml
- action: polars_str_split
  columns: [genotype]
  by: ","
- action: polars_list_to_struct
  columns: [genotype]
  upper_bound: 8
- action: polars_unnest
  columns: [genotype]
- action: polars_str_strip_chars
  columns: [field_0, field_1, field_2, field_3, field_4, field_5, field_6, field_7]
- action: polars_fill_null
  columns: [field_0, field_1, field_2, field_3, field_4, field_5, field_6, field_7]
  value: none
```

Result (VERIFIED (ran), `03`, example 2): EQUAL. 42 rows, 10 columns, all text. The 4 samples with no genotype get `none` in all 8 columns. Without the two optional blocks the step equals the chain without them (example 2b), and the parts keep their leading space (`' sitABCD'`).

### 1.4 Example 3: the decided defaults stop a gene list

```yaml
- action: step_split_wide
  columns: [genotype]
  str_split: {by: ", "}
  list_to_struct: {fields: [gene_1, gene_2, gene_3, gene_4, gene_5, gene_6, gene_7, gene_8]}
  too_many: error
  too_few: error
```

VERIFIED (ran), `03`, example 0: the step stops. "33 of 42 cells have fewer than 8 parts and would lack values". With 5 names and `too_many: error` it stops on 5 cells that have 8 parts (example 0b). There is no chain to compare: a stop gives no table.

### 1.5 Example 4: the fixed-structure case that the demo recipe has today

`Detailed_summary` has a column `hsp_lengthtotal_length` (`"1203/1203"`). The recipe splits it today with `polars_str_splitn` (`n: 2`), `polars_unnest` and `polars_rename` (`config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml:3-13`).

```yaml
- action: step_split_wide
  columns: [hsp_lengthtotal_length]
  str_split: {by: "/"}
  list_to_struct: {fields: [hsp_len, total_len]}
  too_many: error
  too_few: error
```

VERIFIED (ran), `03`, example 3: EQUAL to the chain of `polars_` steps, and equal to the recipe's chain of today after moving the columns. All 280 cells have exactly 2 parts.

One difference matters: `polars_str_splitn` with `n: 2` puts every extra part into the last column, with no message (VERIFIED (ran), `02` section I: `"g1, g2, g3, g4"` with 3 gives `g3, g4` in the last column). The step with `too_many: error` would stop instead.

### 1.6 Where the shipped recipes split text today (VERIFIED (read), grep of `config/`, `assets/gallery_data/`)

| File | What it does | Form |
|---|---|---|
| `1_test_data_ST22_dummy/wrangling/Summary_wrangling.yaml:11-30` | `polars_unpivot` of genotype, phenotype, cge_phenotype and plasmid into one `value` column; then a `polars_with_columns` formula `str.split(', ')`, `polars_explode`, `polars_str_strip_chars`, `polars_unique` | long |
| `1_test_data_ST22_dummy/wrangling/VirulenceFinder_wrangling.yaml:4-26` | formula split `,`, explode, strip; then `polars_str_splitn` `': '` n 2, unnest, rename | long, then wide (2 parts; all 1315 have 2 parts, `05` part 3) |
| `1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml:3-13` | `polars_str_splitn` `/` n 2, unnest, rename | wide (2 parts) |
| `1_test_data_ST22_dummy/wrangling/ResFinder_Abromics_wrangling.yaml:19-26` | formula split `,`, explode, strip | long (the fragment is included by no recipe) |
| `templates/complex_template/genomics_wrangling.yaml:5` | `polars_explode` | long |

No gallery bundle splits text. No shipped recipe makes a wide table of `genotype` today.

## 2. What it does, step by step, on the hard cases

The steps, with what Polars does at each one:

1. **Split** (`str.split(by)`): the text becomes a list of parts. A missing cell gives a missing list. An empty text gives a list with one empty part `[""]`, not an empty list.
2. **Count** (the step's own addition): one pass over the data. Parts per cell, missing cells, empty cells, empty parts.
3. **Check** (the step's own addition): cells with more parts than columns (`too_many`), cells with fewer (`too_few`). `error` stops; `warn` goes on and adds to the note.
4. **To struct** (`list.to_struct(fields or upper_bound)`): the first parts go into the fields. **Extra parts are dropped with no message.** Missing parts become missing (null). Polars' own help says so: "NOT OK - last value missing" (EXTERNAL, Polars docstring of `list.to_struct`).
5. **Unnest** (`unnest`): the fields become columns, in the place of the source column. The source column is gone.
6. **Strip** (optional, `str.strip_chars`): on each new column.
7. **Fill** (optional, `fill_null(value)`): only missing values. An empty text stays empty.
8. **Note** (the step's own addition): the counts, shown to the user (section 5; no carrier exists today).

VERIFIED (ran), `02` (plain Polars, 3 columns, split on `","`) and `proto_step.py` (the step):

| Case | Cell | Plain Polars, 3 columns | Plain Polars, 2 columns | The step (`too_many: error`, `too_few: error`) |
|---|---|---|---|---|
| three parts | `g1, g2, g3` | `g1`, `" g2"`, `" g3"` | `g1`, `" g2"`: **g3 lost, no message** | ok with 3 |
| more parts | `g1, g2, g3, g4` | `g1, g2, g3`: **g4 lost, no message** | g3 and g4 lost | stops: "1 of N cells have more than 3 parts and would lose values" |
| fewer parts | `g1, g2` | `g1, g2, null` | `g1, g2` | stops (too few); with `warn`: `g1, g2, null` and a warning |
| empty text | `""` | `"", null, null` | `"", null` | counted as an empty cell (1 part); stops on too few |
| missing cell | null | `null, null, null` | `null, null` | counted as a missing cell, never as "too few" (REASONED: a missing cell is not a short list; it is reported on its own) |
| spaces around | `" g1 ,g2 ,  g3 "` | `" g1 "`, `"g2 "`, `"  g3 "` | | spaces kept unless `str_strip_chars: {}` |
| empty part between | `g1, , g3` | `g1`, `" "`, `" g3"` | | 3 parts; after strip the middle part is `""` (an empty part, counted) |
| separator at the end | `g1, g2,` | `g1`, `" g2"`, `""` | | 3 parts, the last empty (counted) |
| one part | `g1` | `g1, null, null` | | stops on too few |
| no space after comma, split on `", "` | `g1,g2,g3` | `"g1,g2,g3", null, null` (one part) | | stops on too few; the message shows the cell, so the author sees the separator problem |
| all cells missing | null, null | all null | | width given: all null and the note says "2 missing cells". Width from the data: **stops**, "the number of new columns cannot be read from the data, because the column has no value" |
| zero rows | (none) | 0 rows, 2 columns | | width given: 0 rows, fine. Width from the data: stops, as above (Polars gives no maximum, `02` K2) |
| column is not text | Int64 or Categorical | Polars error `SchemaError: invalid series dtype: expected String, got i64` | | stops with: "column 'x' is Int64, not text. Suggestion: write a polars_cast step to String before this step" |
| a new name already exists | `c1` exists | Polars error `DuplicateError: column with name 'c1' has more than one occurrence` | | stops, names the columns; Suggestion: other `fields`, or `unnest: {separator: "_"}` (gives `genes_split_c1`, `02` M2) |

The decided step adds the "more parts" and "fewer parts" lines. Plain Polars loses values there with no word. This is what D-0264 asks for.

## 3. The parameters

| Name | Whose | Allowed values | Default | What happens |
|---|---|---|---|---|
| `columns` | the step's own (DEC15) | a list with one text column | required | the column to split. More than one: see question 10 |
| `str_split.by` | Polars `str.split` | text | required (Polars has no default) | the separator. `", "` misses `"a,b"`; `","` plus strip handles both (section 2) |
| `str_split.inclusive`, `.literal`, `.strict` | Polars `str.split` | true or false | Polars' defaults (false, true, true) | as Polars |
| `list_to_struct.fields` | Polars `list.to_struct` | a list of names | absent | the names AND the number of the new columns. Polars also takes a function here; a recipe may not (D-0276), so only the list form |
| `list_to_struct.upper_bound` | Polars `list.to_struct` | a whole number | absent | the number of columns, named `field_0, field_1, ...` |
| neither of the two | the step's own addition (D-0264) | | | the width is read from the data (below) |
| `unnest.separator` | Polars `unnest` | text | absent | new names become `<column><separator><field>`; avoids clashes |
| `too_many` | the step's own | `error`, `warn` | required here (decided wording: default "stop"; see below) | `error`: stop and name the cells. `warn`: go on; the extra parts are dropped (that is Polars' own behaviour) and the note says how many |
| `too_few` | the step's own | `error`, `warn` | required here (as above) | `error`: stop. `warn`: go on; missing parts are missing (null) |
| `str_strip_chars` | Polars `str.strip_chars` | a block; `characters` optional | absent = no strip | strip on each new column. `{}` = whitespace (Polars default) |
| `fill_null` | Polars `fill_null` | a block: `value` (or `strategy`, see question 12) | absent = no fill (D-0265) | fills missing values only; empty text stays empty (section 4) |
| keep the source column | not decided | | Polars in place: removed | see question 9 |

**`too_many` and `too_few`: written, or a default of `error`?** The decided wording is "default: stop". The rule DEC33 allows a default for a `step_` only when the parameter is "off when absent" (`.claude/design/recipe_format_spec.md` 7.5.1 rule 3). A check that stops is not "off". So the two readings are: (a) required, the author writes `error` or `warn` (my prototype); (b) absent means `error`. Both stop by default in effect. Default proposal: (a), because the reader of the recipe sees the choice. This is question 3 of section 9.

**The number of columns read from the data** (D-0264):
- Cost: one extra pass over the data. On 2 million rows: building the lazy plan 0.0007 s; running it 0.28 s; reading the width 0.19 s (VERIFIED (ran), `05` part 1).
- Laziness: it cannot be lazy. Polars refuses `to_struct` without `fields` or `upper_bound`: "`Expr.list.to_struct` requires either `fields` to be a sequence or `upper_bound` to be set. This used to be allowed but produced unpredictable results." (VERIFIED (ran), `02` section O). So the step must read the data at that point of the recipe.
- The counts need the same pass even when the width is written (VERIFIED (ran), `05` 1d: 0.49 s with the checks).
- New data: the same recipe gave 3 columns on old data and 4 columns on new data with one more gene (VERIFIED (ran), `05` part 2). With the names written, the new data stops with "1 of 2 cells have more than 3 parts".
- Is this acceptable for a reproducible recipe? REASONED: the same data and the same recipe give the same table, so the result is reproducible. But the shape of the table is not stable: a column that a later step or a plot names may appear or disappear with new data. The stored Tier 1 table is keyed by the data hash (ADR-089, `rules_data_engine.md` section 1), so new data rebuilds it with the new columns. The recipe checker cannot know the new columns before the data is read.
- Alternatives: (1) keep it as decided and say the number in the note; (2) the checker gives an advice when a step reads its width from the data; (3) require `fields` or `upper_bound` (tidyr does not: with `names_sep` and no `names` it makes "as many as needed", EXTERNAL, tidyr reference of `separate_wider_delim`). Default proposal: (1) plus (2).

**Names of the new columns:**
- a list: `list_to_struct.fields` (Polars' own);
- a number: `list_to_struct.upper_bound` gives `field_0, field_1, ...` (Polars' own);
- a prefix with the column name: `unnest.separator` (Polars' own) gives `genotype_field_0` or `genotype_gene_1`;
- from the first row: not proposed. The first row is data, and the names would change with the data (REASONED).

**tidyverse choices** (EXTERNAL, tidyr `separate_wider_delim`: `too_many = c("error", "debug", "drop", "merge")`, `too_few = c("error", "debug", "align_start", "align_end")`; "drop" will "silently drop any extra pieces"). Can each be written with pure Polars steps? VERIFIED (ran), `07`:

| tidyr | Pure Polars | Exists today as a `polars_` step |
|---|---|---|
| `too_many: drop` | `list.slice(0, n)` then `to_struct`, or `to_struct` alone | yes, `polars_list_slice`; and it is what `too_many: warn` gives |
| `too_many: merge` | `str.splitn(by, n)` | yes, `polars_str_splitn`; it replaces split plus to-struct, so it is another chain, not a block of this step |
| `too_few: align_start` | `to_struct` as is | yes; it is what `too_few: warn` gives |
| `too_few: align_end` | `list.reverse()`, `to_struct` with reversed names | no (`polars_list_reverse` would be new). Note: with too many parts it keeps the LAST parts |
| `debug` | formulas for `x_pieces`, `x_ok`, `x_remainder` | possible with `polars_with_columns`; but it ADDS columns, and D-0266 says the additions "only stop or warn" |

All of these are OPEN for Eve (D-0264: "other choices as in the tidyverse are open for the design").

## 4. The three open questions of M280 (D-0265)

A naming point first. D-0265 speaks of a parameter `fill`. D-0266, decided after it, says each composed step gets a block named after the Polars step. So the fill is written `fill_null: {value: ...}`. REASONED: this follows D-0266; if Eve wants the word `fill`, that is a step's own parameter, and it would change values, which D-0266 does not allow for the step's own additions.

### 4.1 Does the fill apply to empty text parts and to missing parts alike?

Facts (VERIFIED (ran), `02` sections E and F):
- `fill_null` fills only missing values. An empty text `""` stays `""` (the empty cell, the empty part between two separators, the separator at the end).
- A missing CELL and a missing PART look the same after the split: both are null. `fill_null` fills them alike. The 4 real samples with no genotype get `none` in all 8 columns (`03`, example 2).

| Option | What the recipe writes | Pro | Con |
|---|---|---|---|
| A. Missing parts only (exact Polars) | `fill_null: {value: x}` | Equals Polars; nothing hidden | Empty parts stay `""`; the author must know it. The note counts them |
| B. The recipe chooses: add an optional block `replace: {old: "", new: null}` before the fill (Polars `Expr.replace`, a new `polars_replace`) | both blocks | The choice is written and is Polars | One more Polars step to build; a finding: today the engine drops a parameter whose value is null before the call (`libs/utils/src/utils/signature_params.py:75`), so `new: null` would not reach Polars without a change there |
| C. The step's own `fill` fills both | `fill: x` | One word | A step's own parameter that changes values: against D-0266 |
| D. Tell a missing cell from a missing part | | The user can see a sample with no genotype | Not possible with `fill_null` alone; needs a formula; REASONED |

Default proposal: **A**. The note says how many empty parts stayed empty, so nothing is silent. B can be added later.

### 4.2 Is the fill value always text, or typed?

Facts (VERIFIED (ran), `02` section G): the new columns are text. `fill_null(0)` on a text column gives the text `"0"`; `fill_null(1.5)` gives `"1.5"`; `fill_null(True)` gives `"true"`. No message.

| Option | Pro | Con |
|---|---|---|
| A. Text only: the step stops on a value that is not text, with "Suggestion: fill with text here, or write a polars_cast step after this step and then polars_fill_null" | No silent conversion (D-0050); a stop is allowed for a step's addition | One more step for a typed fill |
| B. Typed: an optional `cast` block before the fill (`polars_cast`) | One step | The order cast-then-fill is fixed by the step; more to explain |
| C. As Polars (silent text) | Exact Polars | A number becomes text with no word: against D-0050 |

Default proposal: **A**. A pitfall for the docs: filling with the text `NA` makes it a value, not a missing value; a later filter treats it as a value (`modif_filter` says so, `libs/transformer/src/transformer/actions/modified.py:52`).

### 4.3 Does the step strip spaces?

Facts (VERIFIED (ran), `02` A and D; `03` 2b): split on `","` keeps the spaces (`" g2"`). `str_strip_chars` on the new columns removes them. After the strip, `"g1, , g3"` has an empty middle part `""`.

| Option | Pro | Con |
|---|---|---|
| A. Optional block `str_strip_chars`, absent = no strip | Equals Polars when absent; written when wanted | The author must remember it |
| B. Always strip | Fewer mistakes | Not Polars; hides a step |
| C. Split on `", "` instead | No extra step | Misses `"g1,g2"` (`02` C) |

Default proposal: **A** (it is the decided wording "default off"). The docs show the split on `","` with the strip.

## 5. The messages

The app's form: what, where (recipe, table, step, column), then "Suggestion: ...". Proposed texts (the counts are from the real runs):

1. **Too many parts (stop):**
   "Recipe 1_test_data_ST22_dummy, table Summary, step 3 of tier1 (step_split_wide), column genotype: 5 of 42 cells have more than 5 parts; their parts after the 5th would be lost. Rows 10, 11, 13 and 2 more (row 10 has 8 parts: "aac(3)-VIa, ant(3'')-Ia, ..."). Suggestion: write more names in list_to_struct.fields (the longest cell has 8 parts), or write too_many: warn to keep the first 5 parts and drop the rest; the note will count them."
2. **Too few parts (stop):**
   "Recipe ..., column genotype: 33 of 42 cells have fewer than 8 parts; their last columns would be missing. Rows 1, 2, 3 and 30 more (row 1 has 3 parts: "blaTEM-1C, sitABCD, sitABCD"). Suggestion: write too_few: warn to leave the missing parts empty (missing), or check the separator in str_split.by."
3. **The note (visible, not a stop):**
   "Note: recipe ..., column genotype: 42 rows were split into 8 columns (gene_1 to gene_8). 4 cells were missing: all their new columns are missing. 0 cells were empty text. 33 cells had fewer than 8 parts: their last columns are missing. 0 parts were empty text. No value was filled."
   With `too_many: warn`: "... 5 cells had more than 5 parts: 15 parts were dropped." With the width read from the data: "The number of columns (8) was read from the data; new data can give another number."
4. **An unknown block or parameter name of the step:**
   "Recipe ..., step 3 (step_split_wide): fill_nul is not a parameter or a block of step_split_wide. Suggestion: write fill_null." (VERIFIED (ran), `06` part 1)
5. **A parameter that is not one of the composed Polars step's parameters:**
   "Recipe ..., step 3 (step_split_wide), block str_split: sep is not a parameter of polars_str_split (Polars str.split). Suggestion: write by." (`06` part 1 gives "write one of by, inclusive, literal, strict"; a did-you-mean on `sep` finds nothing close enough, so the list is shown.) For `values` in `fill_null` it says "Suggestion: write value."
6. **A parameter that the step supplies:** "block fill_null: columns is not a parameter of polars_fill_null here; the step applies it to the new columns. Suggestion: remove columns."
7. **The column is not text; a name already exists; the width cannot be read:** texts in section 2.

The prototype names a cell by its row number and its text. Naming the sample id would need the step to know the table's key (`is_entity_key` in `input_fields`); an action receives only the table and its own parameters today (VERIFIED (read), `libs/transformer/src/transformer/actions/base.py:23-40`). Question 15.

**The carrier of the note. FINDING: none exists today.**
- An action returns only a table (`data_wrangler.py:133`: `transformed_lf = action_func(transformed_lf, dict(rule))`). It has no way to return a note.
- The join's self-join warning is kept in `DataAssembler.cautions` and printed; the code says "no carrier takes it to the screen yet (report SELF-JOIN-WARN-1)" (`data_assembler.py:37`, `:128`). The task record says the same: "the numbers do not reach the screen (waits for Eve)" (`.claude/tasks/tasks.md:466`).
- The checker's advices reach the user, but they are found before the data is read, so they cannot hold counts (REASONED).
- So: in HOME there is no place, and in the export there is no place, where a step's note appears today.
- A second point (REASONED): the stored Tier 1 table is reused when its key matches (ADR-089). Then the step does not run again, and its note would not be made again. The note must be stored with the table, or it disappears on the second load.
- What a carrier needs (REASONED, not prototyped in the app): the wrangler and the assembler collect notes beside the table; the orchestrator stores them with the stored table; HOME shows them (the notification log is the existing place for alerts, `ui_implementation_contract.md` section 11d); the export writes them in `README.txt` and `report.qmd`. The same carrier would also serve the join counts of D-0168 and SELF-JOIN-WARN-1.

## 6. The long form (question 17, long form)

Polars facts (VERIFIED (ran), `04` part 1):
- `explode` gives one row with a blank gene for an empty text `""`, and one row with no gene (null) for a missing cell.
- No strip: a part keeps its spaces; strip after the explode.
- `explode(keep_nulls: false)` drops the missing cell's row: the sample vanishes from the long table with no word. `empty_as_null` is about empty LISTS; an empty text is a list `[""]`, so it does not apply.

On the real column (VERIFIED (ran), `04` part 2; `05` part 4): the recipe's three steps turn 42 rows into 140. 4 missing cells give 4 rows with no gene. 0 empty texts. 17 sample-gene pairs appear more than once (20 extra rows), for example `sitABCD` twice in sample 32557144.

The note the step would show (prototype): "42 rows became 140 rows; 4 missing cells (one row with no value each), 0 empty cells, 0 empty parts, 20 parts repeated inside a cell (kept as rows)."

| Option | What the recipe writes | Pro | Con |
|---|---|---|---|
| A. Its own step `step_split_long` (composes `polars_str_split`, `polars_explode`, optional `polars_str_strip_chars`, optional `polars_fill_null`) | `- action: step_split_long` with the blocks | One name, one shape of result. tidyr also has two functions (`separate_wider_delim`, `separate_longer_delim`) | One more step to build and document |
| B. The same step with `mode: long` | `- action: step_split_wide` with `mode: long` | One step to learn | The name says "wide"; `too_many`, `too_few`, `list_to_struct`, `unnest` mean nothing in long mode; a mode switch changes the shape of the table |
| C. Keep the three `polars_` steps, no note | as today | Nothing to build | The counts are not shown (D-0168) |

Both A and B were run: each gives the same table as the three `polars_` steps (VERIFIED (ran), `04` part 3, EQUAL, 140 rows). Default proposal: **A**. Its note is built on the same carrier as section 5.

## 7. How a `step_` declares what it composes

### 7.1 The declaration

Today `register_action(name, ui_schema)` takes only a name and a form schema (VERIFIED (read), `base.py:23`). A `step_` has `polars: composite` and sometimes `wraps` (`composite.py:32-41`). Proposal (REASONED):

```python
"composes": [
    {"block": "str_split",       "action": "polars_str_split",       "run": "always"},
    {"block": "list_to_struct",  "action": "polars_list_to_struct",  "run": "always"},
    {"block": "unnest",          "action": "polars_unnest",          "run": "always"},
    {"block": "str_strip_chars", "action": "polars_str_strip_chars", "run": "optional"},
    {"block": "fill_null",       "action": "polars_fill_null",       "run": "optional"},
]
```

- The list order is the run order.
- `optional`: an absent block means the step is not run (D-0266, DEC33 "off when absent").
- `always`: the step always runs. An absent block means Polars' defaults. M281's example (no `list_to_struct` block) then means "read the width from the data". The other reading: an always-run block must always be written, even as `{}`. Question 8.

### 7.2 Where the parameters of a block come from

For a `polars_` action the parameters are read from the Polars signature, plus three tables of exceptions (VERIFIED (read), `polars_calls.py:158-177` `_params_from_signature`, which calls `utils.signature_params.read_parameters`, `signature_params.py:56`; the exceptions are `REQUIRED` `:54`, `OVERRIDE` `:48`, `NOT_EXPOSED` `:69`). The result is the action's schema in `ACTION_SCHEMAS`.

Proposal: a block is judged against `ACTION_SCHEMAS[<composed action>]` without `columns` and `target_column`, with the same function the checker and the engine use, `utils.ui_schema.step_problems` (`ui_schema.py:194`). One rule set for both (DEC03). VERIFIED (ran), `06` part 2: this already gives "values is not a parameter of polars_fill_null. Fix: write value" and enforces the `one_of: [value, strategy]` rule of `polars_fill_null`.

**Finding:** today a block written as a `mapping` parameter is not looked inside. `fill_null: {values: NA}` passes the checker (VERIFIED (ran), `06` part 3). The build adds a "block" kind to `step_problems`.

**Finding:** `polars_list_to_struct` built by the generator as it is gets `fields` as a single text, and the deprecated `n_field_strategy` as a parameter (VERIFIED (ran): the first run of `03` stopped with "fields has the wrong form. Fix: write a single value"). It needs one `OVERRIDE` (a list) and one `NOT_EXPOSED` line (a reason). With them it ran (`03`).

### 7.3 The two decided tests

1. A parameter name that is not a parameter of the composed Polars step fails, with did-you-mean (VERIFIED (ran) on the prototype, `06` part 1).
2. The step equals the explicit chain of `polars_` steps, with and without the optional blocks (VERIFIED (ran) on the prototype, `03` examples 1, 2, 2b, 3).

### 7.4 The rule applied to every existing `step_` and `modif_` action (report only, no change)

The registry holds 68 actions: 65 `polars_`, 2 `modif_`, 1 `step_` (VERIFIED (ran): `polars` field counts exact 37, wrapper 28, modified 2, composite 1).

**`step_top_n_other`** (`composite.py:42-68`)
- What it does in Polars: cast the column to text; group by it and count rows (or distinct values of `count_distinct`); sort by count, then by value; keep the first `n`; join back to the table; label the rest `other_label`.
- Its parameters today: `column`, `n`, `other_label`, `new_column`, `count_distinct`. None is a parameter of a composed Polars call with its Polars name. They are the step's own vocabulary.
- An explicit chain exists: 4 `polars_with_columns` formulas (key, count over the key, a dense rank on count then value, the label) and `polars_drop`. Equal in 200 of 200 random trials, with and without `count_distinct`, with missing values, 0 to 60 rows (VERIFIED (ran), `08`). The step's own chain uses a join of the table with an aggregated copy of itself; `polars_join` joins only with another table of the recipe, so that exact chain cannot be written as `polars_` steps (VERIFIED (read), `polars_calls.py:291-298`).
- Under Variant 1 its blocks would be `with_columns: {named_exprs: {...}}`: the author would write the four formulas, and the step would add nothing. REASONED: Variant 1 does not fit this step.
- Proposal: declare `composes: [polars_with_columns, polars_drop]` for the documentation and the equality test (with the chain of `08`), and keep its own parameters. If Variant 1 were forced, what changes: 1 shipped recipe step (`config/data_analysis_recipes/retest/retest_top_n_other.yaml:27`), 1 test pair (`libs/transformer/tests/data/step_top_n_other_data_analysis_recipe.yaml`), tests `test_top_n_other.py` (14 test functions), `test_deterministic_order.py`, `test_ui_schemas.py`, `test_action_recipe_pairs.py`, `libs/blueprint_arch/tests/test_schema_registry.py`; docs `docs/appendix/transformer_actions.qmd`, `docs/workflows/wrangling.qmd`, `libs/transformer/README.md`; `libs/utils/src/utils/step_migration.py`. Gallery bundles: 0.

**`modif_filter`** (`modified.py:29-78`)
- One Polars call, `LazyFrame.filter`, which takes a formula. Its parameters (`column`, `op`, `value`, `na`, `closed`) are its own vocabulary, shared with the HOME filter panel and the audit (`modified.py:3-6`).
- It composes nothing. D-0266 is about `step_`. Proposal: no change; its `wraps` already names the call.
- If changed anyway: 10 recipe steps in `config/` (files: `1_test_data_ST22_dummy/assembly/Summary_phenotype_length_fragmentation_assembly.yaml`, `1_test_data_ST22_dummy/wrangling/Detailed_summary_wrangling.yaml`, `1_test_data_ST22_dummy/wrangling/MLST_Metadata_wrangling.yaml`, `2_test_data_ST22_dummy/wrangling/amr_data.yaml`, `2_test_data_ST22_dummy/wrangling/plasmid_data.yaml`, `retest/retest_tier2.yaml`), 8 test recipes under `app/tests/equality/recipes/`, the audit writer (`libs/blueprint_arch/src/blueprint_arch/t3_translator.py`), 29 test files under `app/tests` and `libs/*/tests`, 6 docs. Gallery bundles: 0.

**`modif_join_where`** (`polars_time_joins.py:225-313`)
- One Polars call, `LazyFrame.join_where`, with Polars' own names (`predicates`, `suffix`) and `right_ingredient`. What it adds is a fixed row order (left row, then right row) and a type check.
- It composes nothing. Proposal: no change.
- If changed anyway: 0 shipped recipe steps, 1 test pair, 11 test files.

The plot components named `step_` (D-0091, D-0210) are not built yet. The same rule would apply to them when they are (REASONED); not studied here.

## 8. The tests, the files and the documentation of the build

### 8.1 Tests (each must be able to fail)

1. `polars_list_to_struct` equals Polars, with `fields` and with `upper_bound` (a case in `test_polars_actions_equal_polars.py`).
2. The same, refused: `fields` written as something other than a list.
3. `composes` names only registered `polars_` actions; each block name is the action name without `polars_`.
4. A parameter name that is not one of the composed step's parameters fails, with did-you-mean, in the checker AND in the engine (decided).
5. A block that holds `columns` or `target_column` fails.
6. An unknown block name fails with did-you-mean.
7. Equality with the explicit chain: no optional block, each optional block alone, all of them; on the hard-case table and on the real `genotype` (decided).
8. `too_many: error` stops with the count and the rows; `too_many: warn` goes on, and the table equals the chain (this proves that the check changes no value).
9. The same for `too_few`.
10. Width from the data: equals the chain with `upper_bound` = the longest cell; all cells missing stops; zero rows stops.
11. A column that is not text stops; a Categorical column stops.
12. A new name that already exists stops; `unnest: {separator: "_"}` avoids it.
13. The note's counts are exact on the hard-case table: missing cells, empty cells, empty parts, dropped parts.
14. The note reaches HOME and the export, and is still shown when the stored Tier 1 table is reused.
15. The 1:1:1 pair files for `step_split_wide` and `polars_list_to_struct` (`test_action_recipe_pairs.py` fails without them).
16. The prefix and the `polars` field agree (`test_registry_polars_rules.py:135`); no hidden default (`:147`).
17. If question 4.2 is A: a fill value that is not text stops.
18. If the long form is built: the same tests for `step_split_long`, plus "a missing cell gives one row with no value, and is counted".
19. Break once: turn the `too_many` check off and see test 8 fail.

### 8.2 Files the build would touch (REASONED from the reads above)

- `libs/transformer/src/transformer/actions/polars_calls.py`: `polars_list_to_struct` (and, if chosen, `polars_replace`, `polars_list_reverse`).
- `libs/transformer/src/transformer/actions/composite.py`: `step_split_wide` (and `step_split_long`); `composes` on `step_top_n_other`.
- `libs/utils/src/utils/ui_schema.py`: the block kind in `step_problems`; `schema_declaration_problems` checks `composes`.
- `libs/utils/src/utils/signature_params.py:75`: only if `polars_replace` with `new: null` is chosen.
- The note carrier: `libs/transformer/src/transformer/data_wrangler.py`, `data_assembler.py`, `app/modules/orchestrator.py`, the HOME notification log (`app/handlers/home_theater.py`), `app/handlers/export_handlers.py`.
- Tests: section 8.1; pair files in `libs/transformer/tests/data/`.
- Records owned by other sessions, by message only: `.claude/design/recipe_format_spec.md` 7.5.1 (the recipe session), `rules_agent_role_bioscientist.md` section 8 (the action list).

### 8.3 Documentation (D-0266)

A user page on how to read and write a `step_` and a `modif_`: what each prefix means; the equality rule; the nested blocks; off when absent; the explicit chain beside every example; what the step adds beyond Polars; a table of every `step_` and `modif_` with the Polars steps behind it. Plus, for this step: "no automatic fill; fill in a block or a later step" (D-0264); strip after split; the separator pitfall `", "` versus `","`; the science caveat of section 0 point 7; the `NA` text pitfall. Pages to update: `docs/appendix/transformer_actions.qmd`, `docs/workflows/wrangling.qmd`, `docs/reference/wrangling_guide.qmd`, `libs/transformer/README.md`. The Blueprint help is deferred (D-0266).

### 8.4 Effort (information only, not an argument; D-0268)

| Part | Tag |
|---|---|
| `polars_list_to_struct` and its tests | [sonnet/low] |
| The block check in `step_problems` and `composes` | [sonnet/medium] |
| `step_split_wide` and its tests | [sonnet/high] |
| The note carrier (wrangler, assembler, stored table, HOME, export) | [opus/high] |
| `step_split_long` (if chosen) | [sonnet/medium] |
| `composes` on `step_top_n_other` and its equality test | [sonnet/low] |
| The documentation of `step_` and `modif_` | [sonnet/medium] |

## 9. What nothing decides (for Eve)

Most important first. Each has options and my default. The default is not a decision.

1. **The note carrier.** The decided visible note has no place to appear today. Build one carrier for step notes (HOME notification log and the export, stored with the Tier 1 table)? Options: A build it before the step; B build the step first, notes printed only; C both together. Default: A or C. B would not meet D-0264.
2. **A gene list and `too_few: error`.** With the decided default, every real gene list stops. Keep `error` and document that a list of varying length needs `too_few: warn`? Or another default for lists? Default: keep `error`, document it.
3. **`too_many` and `too_few`: always written, or absent means `error`?** Default: always written (DEC33).
4. **Fill and empty text (4.1).** A missing only; B add a `replace` block; C one `fill` for both. Default: A.
5. **Typed fill (4.2).** A text only, stop otherwise; B a `cast` block; C as Polars (silent text). Default: A.
6. **Strip (4.3).** A optional block, off when absent; B always. Default: A.
7. **Width read from the data.** Keep as decided, with the number in the note and a checker advice? Or require `fields` or `upper_bound`? Default: keep, with the note and the advice.
8. **An always-run block that is absent** (`list_to_struct`, `unnest`): A Polars' defaults (M281's example is valid as written); B it must be written, even `{}`. Default: A.
9. **The source column.** A removed (Polars in place; tidyr `cols_remove = TRUE`); B kept; C a step's own `keep_source`, off when absent. Default: A.
10. **One column per step, or several?** With several, the new names must differ (`unnest.separator`). Default: one column.
11. **The tidyverse choices** drop, merge, align_end, debug (section 3). A only `error` and `warn` now (`warn` = drop or align_start, with a note); B add `align_end` (needs `polars_list_reverse`); C add `debug` (it adds columns). Default: A.
12. **`fill_null` `strategy` inside the split** copies values from the row above, so from another sample (VERIFIED (ran), `06` part 4). A refuse `strategy` in this block, with the reason; B allow it with a warning. Default: A. (A block then holds fewer than all of Polars' parameters; the reason is written, as `NOT_EXPOSED` does for `polars_` actions.)
13. **The long form.** A its own `step_split_long`; B `mode: long`; C no step. Default: A.
14. **Variant 1 for `step_top_n_other` and the `modif_` actions.** A declare `composes` for docs and the equality test, keep their parameters; B rewrite them with blocks. Default: A.
15. **How a message names a cell.** A row number and cell text; B the sample id (the step must learn the table's key). Default: A now, B with the carrier.
16. **The science caveat.** Say in the docs that a gene list split by position puts different genes in one column, and that presence or absence is done with the long form? Default: yes.

## 10. What I did not do or could not verify

- I did not build anything in the app. `polars_list_to_struct` and `polars_replace` were registered only inside one script's process (`03`), to run the chain.
- I did not prototype the note carrier in the app; section 5 says what it needs (REASONED).
- I did not run any test suite.
- I did not read tidyr's `separate_longer_delim` page; its name is from memory.
- The 2-million-row timings are from one run on a shared machine.
- The message texts of section 5 are proposals; only the prototype's own texts were run.
