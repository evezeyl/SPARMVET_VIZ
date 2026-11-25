# What is left to ask (from the scout's report, ALREADY_ANSWERED.md; sentences copied, nothing added)

Only questions that are OPEN or ANSWERED IN PART. O1, O2, O3 and step item 2, Q1 to Q3 are answered in full (see the full file). Note 1: O4 is answered by D-0446; only the wording of the notes is left.

| question | already answered by (ledger) | what is still to ask |
|---|---|---|
| O4 (= Q6) | D-0446 (coordinator note); D-0347 gives the principle | The wording of the notes (see the full file). |
| O5: reach "16 tables and 13 plots; 4 more tables no plot reads" | D-0346, D-0326 | ANSWERED 2026-11-21, ledger D-0447 (the reach counts the tables no plot reads, said apart); only the exact wording is left. The same answer covers Q5 of the test design. |
| O6: dropping a key column, by name or by place | D-0358, D-0371 | ANSWERED 2026-11-21: ledger D-0448 (a declared entity key is dropped by place like any key) and D-0449 (where the walk cannot follow the column, the drop is allowed with a warning, for now, and the result must never be wrong: the intended table or a plain error). Nothing left of O6. |
| O7: tables no plot and no join reads | D-0346, D-0416, D-0415 | ANSWERED 2026-11-21: ledger D-0451 (a table that no plot reads but that the walk reaches is a line of the dialog). Nothing left of O7 as a question; what a step written there shows is listed in the survey. |
| O8: self-join; joins not left or inner | none for the walk (D-0183 covers the recipe check only) | ANSWERED 2026-11-21: ledger D-0452 (a red warning, not grey; a study of the semi join; the recipe docs say to avoid these joins). |
| Step 1: what is a line at the source level | D-0332 (per tier only) | "Is a source table's line its tier 1 (own steps) or the source file?" |
| Step 3: T2 chosen, join has no T2 steps | D-0346 | "When a join has no tier 2 steps and the user picks T2, may a step at T2 create the join's tier 2?" |
| Step 4: second group "linked by a join" | D-0415 | "Is the group 'linked by a join on the key' still offered, or do the lineage and the chosen levels replace it?" |
| Step 5: other actions joining the readings (unpivot) | D-0353, D-0356, D-0444 | "Should unpivot's names (the columns it creates from values) be read, or stay grey?" |
| Step 6: joins other than left and inner | none (same as O8) | Same as O8: answered, D-0452. |
| Step 7: `x = pl.col('y')` under its own name | D-0353, D-0356 | "Should the note name the other column (`y`) the values may come from?" |
| Q4: source read by plots, empty tier 2 in joins | D-0346 | "For a source table plots read directly and joins read with empty tier 2, is the hidden choice acceptable under D-0346?" |
| Q5: reach count, unread joins | D-0346, D-0326 | answered with O5, ledger D-0447 |
| Q6 (= O4) | D-0347 (principle only); D-0446 | See O4. |
| Q7: source file as note or line | none (same as step 1) | "Is the column's name in the source file a note on the first line, or the source file a line of its own?" |
| Q8: drop of a join key, grey or not offered | D-0297, D-0371 | "A refused drop of a key: shown grey with the reason, or not offered at all?" |
| Q9: full join with keys of different names | none | "In a full join with keys of different names, is the other table's key offered as a line for 'remove from all'?" |
| Q10: when is a type "another type" | D-0337 (type shown, no rule) | "Does a 32-bit and a 64-bit whole number count as another type?" |
| Q11: order of lines | none | "Order of lines: data flow only, or the place she looks at first?" |
| Q12: typed value that cannot be written at one place | D-0202, D-0376 | "When a typed value cannot be written at one place, does that block the whole dialog, only that line, or grey that line?" |
| Q13: audit filter value a date | D-0061, D-0202 | "May the value be a date, and how is a column that is a date at one place and text at another typed?" |
| Q14: plot made impossible | D-0316, D-0327 | "Is a plot that a step makes impossible listed as 'cannot be drawn' in the dialog before she confirms?" |
| Q15: ticked place covers places below | D-0198, D-0316 (conflict, see the full file) | "When a ticked place covers ticked places below it in its chain, are those below written, or shown as covered and not written?" |
| Q16: row count per line or total | D-0316 | "Is the row count per line alone, or the total of the ticked lines, and may it change on another tick?" |
| Q17: same step added twice | none | "Same step added a second time: refused, warned, or accepted showing 0 rows removed?" |
| Q18: `null_values: []`, count 0 | D-0035, D-0042 (neither says the user is told) | "When the no-value count is 0 with `null_values: []`, is the user told that empty text is not missing?" |
| Q19: a step that removes every row | none | "A step removes every row of a table: warn, block, or show the count only?" |
| Q20: recode, different row counts | D-0203 | "Is a warning needed for a recode between two places, beyond the count per line?" |
| Q21: distinct samples | none | "For a long table, should the dialog also give the number of distinct samples?" |
| Q22: "picture changed" and missing values | D-0318 | "Does 'picture changed' count rows the plot drops for missing values or by its own filter?" |
| Q23: earlier-computed value includes removed rows | none (context D-0146) | "Must a line say that a value computed earlier in the tier (z-score, mean, rank) still includes the removed rows?" |
| Q24: removal after head, sample, unique | none | "Must the user be told that a removal after `head`, `sample` or `unique` does not bring other rows in?" |
| Q25: names behind the reach | D-0346, D-0416 | "For the lines, are the names behind the reach shown on demand or always?" |
| Q26: T1, T2, T3 explanation in HOME | D-0306 (Blueprint wording only) | "Is a one-time explanation of T1, T2, T3 in the dialog enough, or do the labels change to plain words in both screens?" |
| Q27: tick a group in one click | none | "Can a whole group of lines be ticked or unticked in one click?" |
| Q28: summary of places not checked | D-0195 | "Must the summary say which places could not be checked and that the step is not written there?" |

## Same question under two ids (scout, section 3)
- LOGIC O3 = DESIGN Q1 (rename back); both answered by D-0357.
- LOGIC O4 = DESIGN Q6 (column gone at a place).
- LOGIC O5 = DESIGN Q5 (reach count).
- LOGIC O8 = QUESTIONS_FROM_STEP1 item 6 = DESIGN Q9 (partly).
- QUESTIONS_FROM_STEP1 item 1 = DESIGN Q7.
- Overlapping, not identical: O1 with step item 4; O2 with Q2, Q3 and step items 5 and 7; Q4 with step items 2 and 3; Q8 with O6; Q25 with O5; O7 with Q5.
