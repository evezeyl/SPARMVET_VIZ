# The default ticks of the audit dialog: your new idea, reviewed (panel of 2026-11-22)

Your order: ledger D-0501. A read-only review: nothing is built from it. First a trial with real data (`TRIAL.md`, this folder: the demo recipe, and about 16 small test recipes made for the hard cases). Then four viewpoints, one round: software architect, data scientist, statistician, a user who is not a developer. **The statistician is the scientist agent briefed a second time with a statistician's questions only: this project has no statistician agent.** The panel recommends; you decide. Your earlier line (every place ticked, D-0316) stands until you do.

- **A** = your new idea: only the earliest place of each branch starts ticked (the original data files); the later places are listed, unticked.
- **B** = your earlier line: every place the step can reach starts ticked.

## 1. Flags first
1. **On the demo recipe A and B give the same result.** All 73 tables (every table at T1 and T2, and the table of every plot) are identical, row for row, for six different sample cases. The sample is gone everywhere in both. A writes 11 steps, B writes 27.
2. **"Earliest only" is NOT always enough.** On small test recipes the sample stays although the original data files were ticked:
   - the key exists only in the SECOND table of a left join (the first table holds another column): the row stays in the first table and in the join, with an empty key. Under A and under B. The app says nothing.
   - a join RECOMPUTES the key from a table the app does not offer as a place: A leaves the sample in the join, B removes it. **This is the only case found where A and B differ.**
   - a table holds the key under ANOTHER column name and no join links it: the app does not see it at all. Under A and under B.
   - a step REWRITES the key (lower case, or an upper-case copy): the typed value does not match there. Under A and under B. The app warns for the lower case and is silent for the upper-case copy.
   - (A key of different types in different tables is refused as a whole, with the table named: safe.)
3. **"Zero rows removed means wrong place" misleads as stated.** With everything ticked (B), the step written at each of the 16 joins removes zero rows, because the earlier steps already removed them: 16 false signals. Zero is also true where the sample never was in the table. And a number above zero can stand beside a row that stays (first case of flag 2). **What was true in every run is the pair: "rows with this sample: 26 before, 0 after".** With A, each written step is the first on its path, so its number means what you expect.
4. **Today's warnings on the demo are all false alarms**, which supports your wish to remove them: 6 tables are listed "the sample may stay" and it is gone from all 6. But with A as it is built now, the 16 joins would be listed "stays by your choice", and it is gone from all 16 too. That list must go with A, or it replaces one false alarm by another.
5. **One thing no number can show** (statistician): if the user ticks only a LATER table, after a statistic was computed over all samples, the count of rows removed is the same, but the other samples' values differ (in the trial a z-score of -1.336 instead of -1.254). A makes this less likely, because the original data files are what is ticked. Neither default makes it impossible, since the user may tick and untick (your decision).
6. **For the user who is not a developer, 16 unticked lines read as "the sample stays there".** The truth is the opposite. One sentence is not enough while the 16 lines are on screen.
7. **It reopens** (information, not an argument): D-0316 (all ticked), D-0346 (the reach shown on each line), D-0347, the contract section 12g.4, and the wording "stays by your choice" built this morning from your answer on unticking.

## 2. The options
| | Merit: for | Merit: against | Evidence (TRIAL.md) |
|---|---|---|---|
| **A** earliest places ticked | The step is written where nothing comes before it, so the number shown is true and "zero" means something. 11 steps, not 27: the recipe of the audit says what you decided. The left-join case you were told about disappears, because every original file is ticked. Your "keep the bad sample in the quality results" case is findable: the quality files are in a short list. | Misses the join that recomputes its key, silently. The 16 unticked lines mislead unless they are folded away. A step started at a later place on purpose is no longer the default. | Q1, Q3, Q4, Q6, Q7 |
| **B** all places ticked | Covers the join that recomputes its key. Safe for a user who reads nothing. | 16 of 27 steps remove nothing; the "zero" signal is noise; unticking a later table does nothing and says nothing. Still misses the other three cases of flag 2. | Q4, Q5 |
| **C** = A, plus one rule, plus a recount (the panel's addition) | A's short and true record. The rule: a place where the key is created or recomputed from something the app cannot follow is ALSO ticked (it is the start of its own branch): this closes the one case where A and B differed. The recount: after the candidate recipe is built, the app counts the rows that still hold the removed value in every table it reached, and names ONLY the tables where the count is not zero. | The recount cannot see a table the app does not know (another column name, no join), and a rewritten key passes it unless a second count ignores upper and lower case and surrounding spaces. Those two stay recipe problems for the good-practice page, as you said. | Q5, Q7; architect: `lineage_walk.py:505-518` |

Cost and build time are not in this table, by your rule.

## 3. What the four viewpoints recommend
- **All four: your new default A, not B.** Three of them (architect, data scientist, user) with the addition C; the statistician with the one rule for the join that recomputes its key.
- **All four: show the pair "rows with this sample: before, after"**, not "rows removed". For a table that computes over samples the statistician asks for one plain line, not a warning: "computed over 41 samples, was 42".
- **The user viewpoint:** the later tables are not listed unless asked ("show the tables built from these"); the words are "your original data files", not "earliest place of each branch"; one sentence says: "The sample is removed from your original data files; every table built from them is recalculated without it."
- **The data scientist:** the audit log says, for each place, whether it was ticked by default, ticked by the user, unticked by the user, or left unticked by default. A reader can then tell a choice from a default.
- **The architect:** one function gives the default ticks to every dialog (a single audit step and "remove from all the data"), so the rule cannot differ between them.

## 4. My recommendation
**C: your default, with the one rule and the recount.**
- It is your idea, and it keeps your aim: no warning for a natural consequence.
- It keeps exactly one kind of warning, and only when it is true: "this table still holds the sample: N rows", measured after the build, not guessed before it. On the demo it would show nothing at all. In the cases of flag 2 that the app can see, it would name the table.
- It replaces the three lists the library has today ("may stay", "may differ", "stays by your choice"), which were all false alarms on the demo.
- What it cannot catch (a key under another name with no join; a key rewritten by a step, unless the second count is added) goes to the good-practice page as recipe rules, with your rule "one column name, one meaning; declare the ID key".

## 5. For you to decide (nothing is chosen)
1. A, B or C.
2. The number: the pair "rows with this sample: before, after" (true in every run), or "rows removed here: N" as you first said (true only at the first place of a path).
3. With A or C: are the later tables listed unticked, or shown only on request?
4. The recount after the build: yes or no; and with the second count that ignores upper and lower case and spaces, or without.
5. The one plain line for a table that computes over samples ("computed over 41 samples, was 42"): yes or no. It is information, not a warning.
6. The words: "your original data files"; the sentence of section 3.
7. The audit log marks each place as ticked by default, ticked by you, unticked by you, or left unticked by default: yes or no.
8. A step that the user starts at a later table ON PURPOSE (a filter that only makes sense there): which places start ticked then? (The architect's proposal: walk back from where the value was typed and stop at the first step that rewrites the values: that place is the earliest one.)

## 6. What nobody checked
Only the demo recipe and the small test recipes: no second real recipe. No dialog exists yet, so no wording was tested on a screen. The row counts were made at tier 1; tier 2 and the plots were compared for equality, not counted. How a later mean treats the empty values that a left join leaves.
