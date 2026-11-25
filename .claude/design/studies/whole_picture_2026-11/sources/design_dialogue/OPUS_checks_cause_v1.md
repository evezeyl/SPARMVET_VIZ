# Opus checks `CAUSE_identical_tables.md` (v1), by reading only

**What I read.**
- The file in full.
- Her words: D-0532, D-0547, D-0549, D-0563 to D-0566.
- The recipe files of `QA_fanout_exhibit`: tier 1 with its comment, tier 2, and the plot.

**Runs.** Following her D-0566 (no run on the cause), I ran two scripts that only read files. Both were registered first (`RUN_REGISTER_opus_recipes.md`):
- RR11 read my stored R5 tables and the raw files.
- RR12 scanned the recipes with my parse.
No engine and no build.

## 1. The "23"

**The Sonnet file is right, and my R5 sentence was wrong in what it counts.**

The tier 2 of `QA_fanout_exhibit` is `rows_per_sample: pl.col('VF_gene').count()`: a count of non-empty virulence genes, not of rows [RECIPE FILE `wrangling/QA_fanout_exhibit_tier2.yaml`].

My stored R5 tables, written by the engine into empty folders and read now [RR11]:
- Before the step: the entity has 23 rows in T1, with `VF_gene` non-empty in all 23 (23 distinct) and `gene` = `blaTEM-1C` in all 23. T2 = 23.
- After a step at `T1:ResFinder`: 23 rows, `VF_gene` non-empty in all 23, `gene` empty in all 23. T2 = 23.

Raw files: 29 lines of the entity in the VirulenceFinder file; the metadata has 42 entities; ResFinder has 70 rows and 38 entities.

**My sentence, corrected** (done in my own `RUN_REGISTER_opus.md` R5 and `OPUS_paths_2.md` 1.5): "The left join from the metadata kept the entity's 23 rows (only ResFinder's `gene` emptied), and its tier 2 counts the non-empty virulence genes per sample, 23 before and after."

For the records:
- The ledger's reading in D-0563, "a count of rows per entity stays 23", came from my wrong sentence. It should read "a count of the entity's non-empty virulence genes stays 23".
- H1 (a count of rows after a metadata-first join) does not apply to this table. Among joined tables, only `ST22_Anchor` counts rows (`pl.len()`) [RR12].

## 2. The cause

**AGREE**: the place chosen covers 1 of the 3 incoming paths (metadata, ResFinder, VirulenceFinder). The 23 rows come by the metadata path (kept: it is the first table of a left join) and the VirulenceFinder path, which the step does not touch [RECIPE FILE; RR11].

**On a bug.** The evidence is now stronger than "12 of 14 changed". The stored after-table holds exactly the rows the reading predicts: the ResFinder column emptied, the virulence genes intact [RR11]. No bug is needed to explain it.

**"Right for what it counts": true on the demo data, with one precision.** The plot's y label says "Rows after the join", and the column is named `rows_per_sample`. The formula counts non-empty virulence genes. The two are equal on the demo only because every row has a virulence gene. After a removal at the VirulenceFinder table, the entity would keep 1 row (from the metadata and its ResFinder row) and show 0 [REASONED].

**A deliberate exhibit: yes.**
- The tier-1 file: "QA canary, an EXHIBIT of a known defect (issue #68) ... Do not copy this pattern".
- The plot: "EXHIBIT of a known defect (issue 68) - rows are inflated on purpose".
[RECIPE FILE]

## 3. The core fact

**TRUE within her rules; to be said with that scope.** An audit step is a filter, a column drop or a removal by key (D-0322 as written in `rules_ui_dashboard.md` section 4). The author's steps are kept and the audit steps go after them (D-0541). A step at the data table removes the entity's data rows, which is exactly the state of an entity that never had data. A table that takes its rows from the metadata cannot tell the two apart. [REASONED from RECIPES G5, G6]

Counter-examples looked for:
- **A marker column written by the audit step** ("removed"): not an allowed audit step (D-0322). Even then, the author's count would still count the marked rows.
- **A recipe step that reads the audit record:** no action reads it.
- **The app reading the audit record** to mark the result: possible, but outside the table (it is candidate f3).
- **A step that also covers the population path** (the join place, the metadata place, "Remove from all the data"): this is not "the data table's own place".

So I find no counter-example within her rules.

## 4. The scan

**AGREE** [RR12, my parse]:
- 14 recipes with joins, 31 joined tables.
- 7 start from the metadata: 6 in the demo and `demo_abromics::demo_join`.
- 4 of the demo's 7 have a data join.
- Only `ST22_Anchor` counts rows.
- 5 inner join steps, the same as the 5 inner joins among my RR1's 7 undeclared join steps.

## 5. The catalogue

- **(a), (b), (d), (f1), (f2), (f3):** true as described. In (b), the dialog's sentence "can remain" is hers to allow (PATHS Q6); the file says so.
- **(c):** true, except "That is the only candidate in which the 'filled' zero can be told from a counted zero by the app itself". (f3) has the same property. See R4.
- **(e), whether a right or full join can be followed in her model (D-0553), judged from the model:** YES. In the directed graph a join's parents are its ingredients, whatever `how` says. My graph script reads `ingredients` only; places, "below" and the rule of one place on a path do not change. What `how` changes is which side keeps its rows: the display must mark the kept side from `how` (right: the second table; full: both; inner: neither), not "the first ingredient". [REASONED from the model]
  - The old reading code does not follow these kinds (D-0452; `step_effects.py:68`): a description of old code only.
  - The action's form lists `right` and `full` (`polars_calls.py:85`) [CODE READ].
  - What needs a run after her choice:
    1. Requirement: D-0564 with option E.
    2. Expected: 42 rows, 4 at 0 after the fill, the key column present once, and the order kept with `maintain_order: left_right`.
    3. Independence: a scratch recipe, hand-written steps, the engine in empty folders.
- **(f4):** "written in two" is option (a) of PATHS Q5, not decided (R6).
- **Missing candidate (f5):** the recipe says that a result is per entity (a key, unknown today, J01 or S01). The app then knows to offer the join place and to warn at the data place, without a completion. It does not prevent the false zero; it lets the app say it. [REASONED] (R7)

The exact texts of R4 to R7:
- **R4.** In (c), replace "That is the only candidate in which the "filled" zero can be told from a counted zero by the app itself." with "(c) and (f3) are the candidates in which the app itself can tell a filled zero from a counted zero."
- **R5.** In (e), replace "The graph (D-0553) does not need the kind of join: the parents of the join are the same two tables. What the old walk cannot follow is the columns' origin, not the place. [REASONED; the second sentence is a reading of my graph rules and of `step_effects.py`, to be checked by Opus]" with "Her graph model (D-0553) follows a right or full join like any join: its parents are its ingredients, whatever `how` says, so the places, "below" and the rule of one place on a path are unchanged. What `how` changes is the kept side, which the display must name from `how` (right: the second table; full: both), not from the first ingredient. The old reading code does not follow these kinds (D-0452, `step_effects.py:68`): a description of old code only. [REASONED from the model; checked by Opus]"
- **R6.** In (f4), replace "Today: decided as an option, 27 places not valid in one step, written in two." with "Today: decided as an option (D-0416). As one step, its 27 places are not valid under D-0553 (35 pairs). Writing them in two steps is option (a) of PATHS Q5, hers to choose."
- **R7.** After (f4), add: "**(f5) The recipe says that a result is per entity** (a new key; today refused as unknown, J01 or S01). The app then knows that a removal for this result must cover the population path: it offers the join place and warns at the data place. It does not prevent the false zero; it lets the app say it. Today: not accepted. [REASONED]"

## 6. The question and the half page

Her words checked: D-0564 is exact in the header. In the question it is paraphrased: R8.

Replacements:
- **R8.** Replace "You said: the join should not start with the metadata, or we need a solution we do not have yet [D-0564]." with "You said: "well there we have it the join should not start with the medata or we need a solution we do not have yet ." [D-0564]".
- **R9.** Replace "the data first and the metadata second works today and removes the entity completely wherever you write the step" with "the data first and the metadata second works today: a step at the data table or at the join place removes the entity completely; a step at the metadata place only empties its metadata columns [RECIPES G5]".
- **R10** (D-0532, said plainly, not softened). Add after "So the question is about the zero.":

  "Your direction and the zeros cannot both hold. To show an entity that has no data row, the table must keep the metadata's rows. So in every form with zeros (A, B, C, E) the metadata is the kept side: first with a left join, or second with a right or full join. Only D follows your direction fully, and D has no zeros. Why: a row for an entity with no data can only come from the metadata. How you would see it: in A, B, C and E the plot keeps 42 bars, with 0 for an entity removed at the data table; in D it has 38 bars and no zeros."
- **R11.** Option E becomes: "**E.** A right or full join, so that the metadata is written second (e). It still keeps the metadata's rows, so you would see the same as A: 42 bars, and 0 for an entity removed at the data table. Your graph model follows such a join like any other (its parents are the same tables). The old reading code does not follow these kinds (D-0452); the new one is not built. Whether the engine builds it as expected is a run after your choice."
- **R12** (no effort argument). In "My lean", replace "Reason: it needs nothing new in the check or the engine, it removes the entity completely at the default place, and it tells the user the one thing that can surprise." with "Reason: at the default place it removes the entity completely; it tells the user the one thing that can surprise (the false zero at the data table); and it keeps the zeros the plot is written to show. `QA_fanout_exhibit` is a deliberate exhibit of a defect: changing it changes its purpose."
- **R13.** Replace "D reopens the plot's own purpose (a sample without a gene must appear at 0)." with "D changes the purpose written in the plot itself (a sample without a gene must appear at 0); it reopens no decision of yours."
- **R14.** In "On the demo you would SEE":
  - replace "With (b) it is the same, but the dialog says before you apply that the step covers 1 of 2 paths and the entity can remain." with "With (b) it is the same; if you allow the sentence of PATHS Q6, the dialog says before you apply that the step covers 1 of 2 paths and the entity can remain.";
  - after "Today (and with (a), (c), (e))", add "[today: run; with (a), (c), (e): reasoned]".

The numbers are right [RR11, raw files]:
- 42 entities in the metadata;
- 38 with a ResFinder row, so 4 with 0 genes;
- 41 after a removal at the join place.

Half page:
- **R2.** Replace "The app: not shown to be at fault. ..." with "The app: not at fault in the evidence. My stored tables of the earlier run, read now, hold exactly the rows the reading predicts: the ResFinder column emptied, the 23 virulence genes intact [Opus RR11]. Twelve of the 14 tables below changed in that run [PATHS G8]."
- **R3.** In "The core fact", replace "So no solution can give" with "So, within your rules (an audit step is a filter, a column drop or a removal by key, written after your steps), no solution can give". The same scope in (f) item 1.
- **R1.** In section (c), replace "It counts virulence-gene rows after a join with a long ResFinder table." with "It counts the non-empty virulence genes of each sample after the join. On the demo this equals the rows, because every row has a virulence gene; after a removal at the VirulenceFinder table, an entity would keep 1 row and show 0."

## 7. Closing line

**I agree with `CAUSE_identical_tables.md` with these 14 replacements, R1 to R14:**
- R1: (c), what the plot counts.
- R2: half page, the app.
- R3: the scope "within your rules".
- R4: (c), "the only candidate".
- R5: (e), judged from the model.
- R6: (f4), "written in two".
- R7: add (f5).
- R8: her words exact.
- R9: "wherever you write the step".
- R10: her direction against the zeros, said plainly.
- R11: option E and what she sees.
- R12: the lean without an effort argument.
- R13: D "reopens".
- R14: what she would see with (b), and the tags.

Open between us: nothing, if the Sonnet agent accepts them.
