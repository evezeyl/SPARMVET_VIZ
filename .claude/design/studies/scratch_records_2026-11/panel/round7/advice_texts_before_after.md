# Advice texts of the checker: old text and new text (ADVICE-TEXTS-1, PROVISIONAL)

Style: first what happens (short plain sentences), then each remedy starting with "Suggestion:". No meaning changes, with ONE exception: ST15 has an ADDED remedy (Float64, with its cost: about 15 to 16 exact digits, so very large whole numbers lose their last digits). ST14 now says at most k rows (exactly k when the table has k rows or more). The old text is what the checker wrote before; the new text is what it writes now (the quoted names, such as 'A' or 'n', come from the test recipe).

Not rewritten: J14, S07 and ST12 are errors (they stop a recipe), not advices; the text of ST12 comes from the engine's filter check and is shared with it.

## G02
- Old message: the group has no description
- Old fix: write the question its plots answer
- New message: The group has no description, so the question its plots answer is not stated.
- New fix: Suggestion: write the question its plots answer.

## I02
- Old message: info.description is missing
- Old fix: write it (spec section 13)
- New message: info.description is missing
- New fix: Suggestion: write it (spec section 13).

## J03
- Old message: the join has no description
- Old fix: write the grain and the join type (spec section 13)
- New message: The join has no description, so its grain and its join type are not stated.
- New fix: Suggestion: write the grain and the join type (spec section 13).

## J12
- Old message: Join of 'A' with itself on the same column ('id'). If each value of the column appears once, the result has the same rows and copies of the columns named `_right`. If a value repeats, rows are multiplied.
- Old fix: Remove the step if you did not mean this.
- New message: Join of 'A' with itself on the same column ('id'). The result has the same rows if each value of the column appears once, and more rows if a value repeats; the columns are copied with the suffix `_right`.
- New fix: Suggestion: remove the step if you did not mean this.

## J13
- Old message: the join key 'id' is declared Float64 in 'A': identifiers written differently (for example 001, 1 and 1.0) become the same number, leading zeros are lost, and the join merges different samples without a message
- Old fix: declare the key as a text type in input_fields of 'A' (for example String or Categorical, as for other identifiers)
- New message: The join key 'id' is declared Float64 in 'A'. Identifiers written differently (for example 001, 1 and 1.0) become the same number, leading zeros are lost, and the join merges different samples without a message.
- New fix: Suggestion: declare the key as a text type in input_fields of 'A' (for example String or Categorical, as for other identifiers).

## P02
- Old message: the plot has no description
- Old fix: write what is drawn and counted (spec section 13)
- New message: The plot has no description, so what is drawn and counted is not stated.
- New fix: Suggestion: write what is drawn and counted (spec section 13).

## S04
- Old message: the schema has no description
- Old fix: write the grain: what one row is (spec section 13)
- New message: The schema has no description, so the grain (what one row is) is not stated.
- New fix: Suggestion: write the grain: what one row is (spec section 13).

## ST13
- Old message: polars_head keeps rows by their position, but the order of the rows is not fixed by polars_sort (data_schemas.A.wrangling.tier1[1], maintain_order: false): Polars does not promise the same rows. (The checker looks only at steps with a stated order parameter; it can miss, for example, a pivot or an explode before.)
- Old fix: write maintain_order: true in that step, or write a polars_sort step with maintain_order: true before this one
- New message: polars_head keeps rows by their position, but the order of the rows is not fixed by polars_sort (data_schemas.A.wrangling.tier1[1], maintain_order: false), so Polars does not promise the same rows (the checker looks only at steps with a stated order parameter; it can miss, for example, a pivot or an explode before).
- New fix: Suggestion: write maintain_order: true in that step. Suggestion: write a polars_sort step with maintain_order: true before this one.

## ST14
- Old message: polars_top_k returns exactly k rows; when rows are tied at the limit, which of them are kept is not fixed, do not rely on it. A NaN comes first; rows with no value fill the k rows when values run out
- Old fix: to always keep the same rows, add a row number (polars_with_row_index) and give it last in `by`, or use polars_sort with maintain_order then polars_head; to keep every row tied with the k best, use polars_rank (method min) and a filter
- New message: Warning: polars_top_k keeps at most k rows: exactly k when the table has k rows or more. If several rows have the same value as the k-th row, only some of them fit, and Polars does not promise which ones. A NaN comes first (last if `reverse` is true for that column). Rows with no value fill the k rows when the real values run out.
- New fix: Suggestion: to always keep the same rows, add a row number (`polars_with_row_index`) and use it as the last `by` column. Suggestion: to keep every row that ties with the k best, use `polars_rank` (method `min`) and a filter; this can return more than k rows.

## ST15
- Old message: polars_sum of the column 'n', declared Int32: the total of a 32-bit whole-number column wraps around above about 2 thousand million (4 for UInt32) with no error and gives a wrong, possibly negative, number (the checker does not see a sum inside a formula, in a join result, or on a column made 32-bit by an earlier step)
- Old fix: write a polars_cast step to Int64 for 'n' before this step
- New message: polars_sum of the column 'n', declared Int32, can give a wrong total. A 32-bit whole-number total wraps around above about 2 thousand million (4 for UInt32) with no error and can be negative (the checker does not see a sum inside a formula, in a join result, or on a column made 32-bit by an earlier step).
- New fix: Suggestion: write a polars_cast step to Int64 (whole numbers) or Float64 (decimal numbers; it holds about 15 to 16 exact digits, so very large whole numbers lose their last digits) for 'n' before this step.

## Variants of J12 (semi and anti)
- Old: "the join of 'A' with itself uses the same key ['id'] on both sides ('how': semi): no column is copied; 'semi' keeps only the rows whose key is found in 'A' itself"
- New: "The join of 'A' with itself uses the same key ['id'] on both sides ('how': semi). No column is copied; 'semi' keeps only the rows whose key is found in 'A' itself." Fix: "Suggestion: remove the step if you did not mean this."
