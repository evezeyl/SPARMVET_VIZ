# LBFB: the USER viewpoint (panel-user, 2026-11-20; saved by the coordinator from its report)

It read the brief, its own earlier cases, section 5 of the design page, the demo recipe (lines 155-349) and the step files of "MLST with metadata" and "Quast with metadata". It ran nothing; numbers are the brief's. Every dialog sentence is a PROPOSAL.
Facts (READ): `MLST_with_metadata`: tier 1 = left join on `sample_id` with the metadata; tier 2 adds `era` from `year`, then keeps `year` 2023 to 2025 (rows with no year removed). `mlst_bar` targets it. `Quast_with_metadata`: left join, then the measures turned into rows keeping `sample_id, source, country`, then `value` cast to a decimal: `year` is not kept there.

## A. What she expects
**Story 1: plot "MLST Bar", a bad sample, gone everywhere.** She clicks the sample, "Remove this sample from the analysis (audit step)". The dialog:
1. "You remove the sample S7 (column `sample_id`). Seen in: MLST with metadata, T2, plot mlst_bar."
2. "This step will be written in N places. All are ticked. Untick a place to keep the sample there."
3. Once: "T1 = the table after its first steps. T2 = after its second steps. T3 = the table of one plot after its own steps."
4. Group "Source files, k of k ticked": "[x] MLST (file): column `sample_id`", "[x] metadata_schema (file): `sample_id`" ...
5. Group "Tables": "[x] MLST with metadata, T1: reaches 1 other table and 0 plots"; "[x] MLST with metadata, T2 (you are here): reaches 2 plots (mlst_bar, year_distribution)".
6. Group "Plots": "[x] Only this plot: mlst_bar".
7. Before confirming: "Rows removed: MLST with metadata T1: 1. T2: 1. Other tables: 0 (the sample is not there)." and "Pictures changed: mlst_bar, year_distribution. Tables changed, picture the same: 3."
8. Only when it applies: "1 place could not be checked: the data file X was not found. The step is not written there."
After: the sample gone in both plots; a chip "Audit step 1: remove sample S7 (N places)" with "Remove step"; removing it brings everything back.

**Story 2: keep only years after 2022 in ONE plot.** "Keep rows where `year` is greater than 2022." With every place ticked she must untick all but "Only this plot: mlst_bar": the default is the opposite of her intent here (see "put in doubt"). At MLST with metadata T2: "your step removes 0 more rows here: the recipe already keeps 2023 to 2025". At T1 (if ticked): "removes N rows here. Picture changed in: era legend of mlst_bar, year_distribution" (T1 feeds T2, where `era` is made from `year`).

## B. The four questions, from her side
- **Q1 a rename across two tiers** (source P has `a`; tier 1 of join J renames `a` to `b`; tier 2 renames `b` back to `a`; a plot reads J T2). "One column": she reads "J, T2: `a`. J, T1: called `b` here. P (file): called `a`": understood at once; the step must be written with the name used there. "Two columns": she removes the value at T2 only; T1 and the file still hold it: a silent partial removal. **Recommends: one column, named as it is at each table.**
- **Q2 what the reach counts** (16 tables she can open, 20 with the joins no plot reads, 13 plots). "20 tables": she looks for 20 and finds 16 in the data choice: she doubts the count. "16 tables": understood, but 4 stored tables change unseen. Both apart: true, a little long. **Recommends: headline "16 tables, 13 plots"; "4 more tables that no plot reads also change" as a footnote or under "show which".**
- **Q3 a place where the column is gone** (`year` in "Quast with metadata"). A note under the line that reaches it: understood at once. A grey line: also understood, but grey would then mean two things (the column is gone; the place could not be checked, e.g. a missing file), and she may think something is broken. Not shown: she looks for the table and wonders if the walk failed; against "no silent failure". **Recommends: the note, plus one summary sentence "In 2 places the column `year` no longer exists: nothing is written there."** (For Quast the honest line is "nothing changes in this table": Quast is the left side of the join; numbers not verified.)
- **Q4 the drop of a key column** (`sample_id`). The dialog with key places grey: informative, but invites a half action (she confirms with the places where it is not a key and loses the ability to remove samples there later). One plain refusal before the dialog: understood at once. **Recommends: the plain refusal, with "To remove a sample, remove its rows (Remove sample), not the column."** Open for the owner: a table where `sample_id` is not a key.

## C. Built in steps
With only the first step (a filter on a column never renamed or recomputed) the dialog must already: (1) list every place that holds the column by the same name, in the order of the data flow, with "you are here"; (2) show per table "rows removed" and per plot "picture changed / the same", computed; (3) say at the top what this version does not find ("places where the column has another name or another meaning are not listed"); (4) show a grey line with the reason for every place the walk cannot decide ("the column may be called differently in this table; this step is not written there", "the column is computed here from other columns", "this table was reshaped; the column is not found by name", "the data file was not found"): a MISSING line is not acceptable; (5) the confirm button counts the places not checked: "Confirm (2 places not checked)"; (6) "Remove step" restores everything.
Order that matters to a user: 1 the plain filter on an unchanged column with rows removed and pictures changed; 2 the reach and "only this plot"; 3 grey lines with reasons; 4 the type difference; 5 the rename; 6 the recompute with its note; 7 the drop and the key refusal; 8 the fixtures (a table shared by six plots, plots with their own steps). For her, 2 and 3 come before 5: without grey reasons she cannot trust 1.

## D. What will be missed
Surprises although every line was true: the reach is not the rows removed; a filter before a join and after it are different things; a filter at T1 changes T2 (`era` is built from `year`); a step the recipe already does removes 0 rows; many ticked places doing the same; a missing file makes the list shorter; the same condition on a decimal and a whole-number column keeps different rows; rows are not samples in a long table ("how many samples?"); a sample "removed everywhere" still shown as a missing label through a join; a value computed earlier in the tier (a z-score) still contains the removed rows.
To tell her ONCE: "Reaches means the tables and plots built from this place; it is not the number of rows removed. Rows removed are shown for each table." and "A step at a source file changes the source; a table built from it by a left join keeps its rows."
What she will want next that is not offered: a preview of the rows before confirming; ticking a whole group in one click; changing a step instead of removing it; seeing why a place is grey with the recipe step shown.

## E. Five checks a person can do in the app, five minutes each
1 Remove sample S7 with everything ticked; open each table of the list: S7 in none; the row counts before and after equal the "rows removed" announced. 2 The same with only "Only this plot: mlst_bar": year_distribution unchanged, mlst_bar without S7. 3 "Remove step": every table and plot as at the start. 4 `year > 2022` at MLST with metadata T2 only: "removes 0 more rows", the table unchanged; then at T1 only: the era legend changes. 5 Rename a copy of the Quast data file and reopen: the Quast places grey with the reason, the others tickable, the summary counts the places not checked; put the file back: the dialog as before.

## The three sentences the dialog cannot do without (proposals)
1 "This step will be written in N places; M places could not be checked and the step is not written there." 2 "Reaches means the tables and plots built from this place; it is not the number of rows removed. Rows removed are shown for each table." 3 "A step at a source file changes the source; a table built from it by a left join keeps its rows."

## What this puts in doubt, from the user's side (not reopened by the viewpoint)
- "Every place starts ticked" (D-0194, D-0316): the wrong default when the request begins in ONE plot (story 2): she must untick all but one, and a tired user clicks through. Proposal to show her: when the request starts from a plot's own filter, only "Only this plot" starts ticked.
- D-0352 ("within the same tier then it will be the same column") speaks of one tier; a rename across two tiers is another case.
- "A join no plot reads is not offered" with question 2: stored tables change in places she never sees; consistent only if the dialog says so once.
- "Each line says what is true there": for question 3 "no line" may be read as "no change": the note is needed.
