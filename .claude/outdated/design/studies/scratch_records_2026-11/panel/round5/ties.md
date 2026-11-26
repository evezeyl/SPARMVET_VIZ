# Q6 - what Polars really does with tied values in top_k / bottom_k (Polars 1.40.1, RUN)

Scripts: `tmpAI/panel/round5/ties.py`, `ties_big.py`, `ties_stream.py`, `ties_actions.py` (all RUN, output copied below). "Tie" = several rows with the same value at the cut, so there is more than one way to pick k rows.

## 1. Small table, values [9, 7, 7, 7, 5] (ids a b c d e), k = 3 (RUN)
- top_k returns EXACTLY 3 rows: a(9), b(7), c(7). The third 7 (d) is dropped. It does not return all tied rows.
- Same answer on a DataFrame and on a LazyFrame, same on 3 repeats.
- Largest first (top_k) and smallest first (bottom_k). bottom_k k=3 gives e(5), b(7), c(7). `reverse=True` on top_k gives the same rows as bottom_k.
- 7 rows [5,7,7,9,7,3,7] (four 7s at b,c,e,g): k=3 gives d(9), b, c; k=2 gives d, b. All four tied (7,7,7,7) k=2 gives a, b. On these small tables the kept tied rows are the FIRST ones in table order.
- Several `by` columns: ties are broken by the next column; rows equal on every `by` column behave as above (d, e, f).
- k larger than the table: all rows (5 of 5). k = 0: no rows.

## 2. Missing values and NaN (RUN)
- null: top_k and bottom_k skip a null while there are enough real values ([9,None,7,None,7] k=3 -> 9,7,7). If fewer than k real values exist, null rows fill the rest ([None,None,5] k=2 -> 5 and a null row): so "exactly k rows" can contain a row with no value.
- NaN (not-a-number, a float that is not a number): top_k treats NaN as the LARGEST value: [9,NaN,7,7] top_k 2 -> NaN, 9. bottom_k 2 -> 7, 7. A NaN therefore silently takes first place of a "k best" list (rank also gives NaN rank 1 on descending).
- Not shown by any message today. Flag: NaN at the top of a top_k.

## 3. Large table, 3 million rows, 50 distinct values (many ties), k = 1000 (RUN)
- top_k returns exactly 1000 rows. 60,321 rows share the cut value 49; only 1000 are kept.
- Which of the tied rows: NOT the first ones in table order on this table (the small-table pattern does not hold). Same result on 5 repeats, on a table in 10 chunks (pieces in memory) and on a table in one piece, with 12 threads and with 1 thread (same fingerprint 3bea1d8b), on a LazyFrame run in memory.
- Run in the streaming engine (low-memory mode, `collect(engine="streaming")`): a DIFFERENT set/order of tied rows, and the same query on the same data gives different answers from run to run (fingerprints 43bc708d, 16e33f14, 0187b44f over 6 and 6 runs, with 12 and 4 threads). Only 1 row of the 1000 differed in membership in the run I compared, the order differed. So a result can change between two runs of the same recipe in streaming mode when ties are at the cut.
- Shuffled input: the kept tied rows are not the first ones of the shuffled table either (RUN: check False): the choice is not "first in the table" on a large table.
- bottom_k: same behaviour (exactly 1000, not the first tied rows).
- Values (as numbers) are identical in all cases; only the identity of the tied rows changes. So a plot or a mean of the value column does not change, a list of sample names does.

## 4. sort then head (RUN)
- `sort` descending then `head(3)` on the small table: a, b, c with and without `maintain_order`.
- 3 million rows: default sort and `maintain_order=True` gave the same rows (first tied rows in table order), identical on 5 repeats. Polars does not promise this without `maintain_order` (INFERRED from its documentation: the default sort is not guaranteed stable). Only `maintain_order=True` is a promise.
- Streaming engine with sort + maintain_order + head: identical on 4 runs.

## 5. rank, which method keeps "all tied values" (RUN, v = [9,7,7,7,5], rank 1 = largest, keep rank <= 3)
- `min` -> a, b, c, d (4 rows): all tied rows of the 7s are kept, so MORE than k rows. Ranks 1,2,2,2,5.
- `dense` -> a,b,c,d,e (5 rows): "the 3 best distinct values" (9, 7, 5): another meaning again.
- `max` -> a only (ranks 1,4,4,4,5): the whole tied group is dropped if it does not fit.
- `average` -> a,b,c,d (average rank 3.0 for the 7s: the same as min here by luck of this example).
- `ordinal` -> a, b, c (exactly 3 rows; ties numbered in table order).
- Second example [9,8,8,8,7,7,6], k=3: min -> a,b,c,d (4 rows); dense -> 6 rows; ordinal -> a,b,c.
- 3M rows, `min` rank <= 1000: 60,321 rows (every row that has the top value) - identical in memory and in streaming (same set).
- A null stays null in the rank and is dropped by the filter; a NaN gets rank 1.
- `min` is the method that matches "a tied value still belongs to the first k".

## 6. The two behaviours and how a recipe writes them with today's actions (RUN through the wrangler, `ties_actions.py`)
A. EXACTLY k rows, always the same ones:
 - `polars_with_row_index` (name row_no), then `polars_top_k` k, by [value, row_no], reverse [false, true]. Gives the first tied rows in table order. 3M rows: 1000 rows, equal to the first 1000 rows with value 49 in table order, identical on 3 in-memory and 4 streaming runs.
 - or `polars_sort` by value descending with maintain_order: true, then `polars_head` n: same fingerprint 76db58b9 in memory and streaming.
 - Note the table order is part of the result, so a step that changes the order earlier (a join, a group_by without maintain_order) changes which tied rows are kept.
B. EVERY row whose value is among the k best (can be more than k rows):
 - `polars_rank` columns [value], method: min, descending: true, target_column r; then `modif_filter` column r, op le, value k, na remove. Small: a,b,c,d. Big: 60,321 rows.
 - method dense instead of min if "k best DISTINCT values" is meant.
 - The count of rows is not known before the run.

## 7. What the shipped description says (READ, `libs/transformer/src/transformer/actions/polars_rows.py`, TIE_RULE)
"Polars does not promise which of several tied rows are kept at the cut, nor their order (measured with Polars 1.40.1: not the input order)." My runs: correct on a large table, NOT correct on small tables (they keep the first tied rows). Streaming gives different answers per run. The advice (end `by` with a unique column such as the row index) is confirmed by RUN.

## 8. Advice for the warning text (the advice is a recommendation; Eve decides)
- Say it when it can happen: `by` has no unique column at the end (the checker cannot know ties exist in the data, so it is an "may happen" advice, not a certainty).
- Plain words: "top_k keeps exactly k rows. If several rows have the same value at the cut, which of them are kept is not fixed: it can differ between a small and a large table, and between two runs in low-memory (streaming) mode. To keep always the same rows, add a unique column last in `by` (for example the row number from polars_with_row_index). To keep every tied row (possibly more than k rows) use polars_rank with method min and a filter."
- Do not promise "first in table order" anywhere: true on small tables, false on large ones.
- Add one line for missing values: "A missing value is skipped; if fewer than k real values exist, rows without a value fill the rest. A NaN counts as the largest value."
- Warning level: it can change which samples are listed, not the value statistics; clearly an advice, not an error (ADR-104).
