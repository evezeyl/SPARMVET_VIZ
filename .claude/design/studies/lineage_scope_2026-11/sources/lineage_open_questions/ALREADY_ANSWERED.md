# Open lineage questions checked against the ledger (scout, 2026-11-21; saved from its report, unchanged below the notes)
Note 1 (coordinator): the scout read the ledger up to D-0445. Since then D-0446 answers O4 (a place where the column is gone is a consequence shown as a note, not a place to tick); the wording of the notes stays open.
Note 2 (coordinator): the scout's own correction: D-0445 exists and answers O3.

I could not finish the table, so I am handing back a partial result. The ledger, the question files and the handoff are all read. The code check was limited to the file headers and grep hits, not full reads.

Evidence labels: "verified" means I read or grepped the line. "Reasoned" means my inference.

**Correction to my own search.** My first pattern search said the ledger ends at D-0444. A direct read shows D-0445 at `.claude/knowledge/decision_ledger.md:479`, so the ledger does end at D-0445 (verified). The handoff's O3 entry is right.

## 1. Open questions, text, options, recommendation, blocks

**LOGIC_REVIEW.md, section 7.2 (lines 233-257). Step 1 notes are at lines 225-231.**
- **O1** (235-240). "When you remove a sample from one plot, which tables get a line, all ticked?" Options: (1) only the tables this plot's data comes from; (2) every table joined to these on the sample id; (3) as (2) plus group "same sample id, no join links these tables", ticked; (4) as (3), group shown but not ticked. Recommendation: (3) for "remove this sample", (2) for other filters. Blocks step 1's main test.
- **O2** (242-245). "May the walk read what a step writes beyond the four you listed?" Options: Yes / No. Recommendation: yes, limited to the names a step writes, never its expressions. Blocks the notes of step 3.
- **O3** (247). "A column renamed in tier 1 and renamed back in tier 2: one column named per table?" No options. Recommendation: one column. Blocks the rename-back case of step 2.
- **O4** (249). "A place where the column is gone: a note under the line, with 'N rows removed' for a filter and 'table unchanged' for a drop?" Recommendation: yes. Wording; can wait.
- **O5** (251). "The reach: '16 tables you can open and 13 plots; 4 more tables that no plot reads are also built from it'?" Recommendation: yes, and "stored" only once the opening build exists. Wording; can wait.
- **O6** (253). "Dropping a key column: refused by its name everywhere (as today), or only where a join reads it?" Options: by name / by place. Recommendation: by name for now, plus whether "the declared key of a table" is refused like a join key. Blocks the drop rule of step 4.
- **O7** (255). "Tables that no plot and no join reads (on the demo `Quality_metrics`, `Detailed_summary`): a line?" Recommendation: listed in option 3's group, not ticked. Blocks O1 option 3 on the demo.
- **O8** (257). "A self-join, and joins that are not left or inner (anti, semi, right, full)." Recommendation: grey with the reason until a recipe needs them. Can wait.

**QUESTIONS_FROM_STEP1.md (lines 6-12). Its own header (line 3) says nothing is to go to her now.** It has seven items with a "to study" note each. There are no options or recommendations.
1. Source level: what is a line at "source"; is "all raw data" the tier 1 of each source table?
2. An empty tier 3 and "only this plot": does the line create the plot's tier 3?
3. Level T2 chosen, join with no tier 2 steps: does a step at T2 create the tier 2?
4. Groups "above and below" and "linked by a join": is the second group still needed after D-0355?
5. Recomputed, cast and aggregated columns: which other actions join the readings (unpivot)?
6. Joins other than left and inner: grey until a recipe needs one?
7. `x = pl.col('y')`: should the note name the other column?

**DESIGN.md section 5.1 (lines 624-655). No recommendation is written except where stated.**
- **Q1** (624). Renamed then renamed back: same column or new? Options: same; new.
- **Q2** (625). May the walk read a few step arguments, or the plan alone? Options: hybrid with a closed list; plan only.
- **Q3** (626). A column recomputed under its own name: same column with a note, or new? Options: same with a note; new.
- **Q4** (627). Source table read directly by plots, with an empty tier 2 in the joins: hidden or kept? Options: hidden (D-0346 as written); kept. No shipped recipe has this shape.
- **Q5** (628). Does the reach count joins no plot reads, and is "a table" a distinct stored table? Options: count them; count only tables a plot reads.
- **Q6** (629). A place where the column is gone: absent, grey with reason, or a note under the line?
- **Q7** (630). Shown as a note on the first line of its path, or the source file as a line of its own?
- **Q8** (631). Drop of a join key: lines grey with the D-0297 sentence, or not offered?
- **Q9** (632). Full join on keys with different names: is the other table's key offered for "remove this sample from all tables"?
- **Q10** (633). When is a type "another type" for D-0337's note: any engine-type difference, or only the family?
- **Q11** (634). Order of the lines: data flow with the place she looks at first, or data flow alone?
- **Q12** (637). Typed value that cannot be written at one place: block the dialog, only that line, or grey that line?
- **Q13** (638). May an audit filter value be a date, and how is a column typed as date at one place and text at another?
- **Q14** (639). A step that makes a later plot impossible: is the plot listed as "cannot be drawn" before confirmation?
- **Q15** (640). A ticked place covers ticked places below it: marked covered and not written, only told, or silent?
- **Q16** (641). Row count on each line alone, or given the other ticked lines (one run), and may it change on another tick?
- **Q17** (642). Same step added a second time: refused, warned, or accepted showing 0 rows removed?
- **Q18** (643). `null_values: []`: empty field is empty text, not missing; is the user told when the no-value count is 0?
- **Q19** (644). A step that removes every row: warn, block, or show the count only?
- **Q20** (645). Same value matching different row counts at two places because of a recode (Norway to NO): is a warning needed beyond the count per line?
- **Q21** (646). For a long table, also show the number of distinct samples?
- **Q22** (647). Does "picture changed" count rows the plot drops for missing values or by its own filter?
- **Q23** (650). Must a line say that a value computed earlier in the tier still includes removed rows?
- **Q24** (651). Must the user be told that a removal after `head`, `sample` or `unique` does not bring rows back?
- **Q25** (652). Are the names behind "reaches 3 tables and 5 plots" shown on demand or always?
- **Q26** (653). Is a one-time explanation of T1, T2, T3 enough, or do the data-choice labels change to plain words?
- **Q27** (654). Can a whole group of lines be ticked or unticked in one click?
- **Q28** (655). Must the summary say which places could not be checked and that the step is not written there?

## 2. Table, one row per question

Status key: ANSWERED IN FULL, ANSWERED IN PART, OPEN. "Code" gives file:line in `libs/utils/src/utils/` unless stated.

### LOGIC_REVIEW O1 to O8

| Question | Status | What is still to ask her | Code check |
|---|---|---|---|
| O1: which tables get a line when a sample is removed from one plot | **ANSWERED IN FULL.** D-0415 (line 449): lineage places all ticked by default, plus a separate "remove from all the data" for the entity key only. D-0416 (line 450): "yes B. 1. yes (though unlikely no plot) 2. yes off . 3. yes. 4. We need to be data agnostic..." | Only the other filters remain: "the tables joined on the key" (D-0415: "Not decided: the other filters"). | `remove_from_all.py:4-7, 10-13` (offered only for the entity key); `:152` (default off, D-0416 point 2); `:73` (warning text, her D-0416 words, provisional). `lineage_walk.py:19-21` (groups LINEAGE and JOIN_LINKED; unlinked tables only as information, `Walk.outside`), consistent with (A) and (B). |
| O2: may the walk read what a step writes beyond the four readings | **ANSWERED IN FULL.** D-0356 (line 390): "2. yes". D-0444 (line 478): "A", the same content recorded again. | Nothing for O2. Unpivot is not covered (see step item 5). | `step_effects.py:7-13` (seven readings, names only, "never the formula"). No unpivot in the list. |
| O3: rename in tier 1, renamed back in tier 2, one column? | **ANSWERED IN FULL.** D-0357 (line 391): "3. yes one colomn". D-0445 (line 479): "A - but remember the user can still decide to scope his answer to remove eg..in T2". | Nothing. D-0445 adds that unticking the tier 1 place leaves it untouched (a test the review session asked for; not her words). | `lineage_walk.py:25-26, 32` (renamed back followed as one column, P4b). |
| O4: note for a place where the column is gone, with the "N rows removed" / "table unchanged" wording | **ANSWERED IN PART.** Principle: D-0347 (line 381): "so that each line says plainly what is true there" (the review's reading, confirmed "Yes"). D-0318 (line 352) defines "table changed" / "picture changed". Not decided: the note's form and wording. | "For a place where the column is gone, should the line carry a note naming the step that removed it, with the wording 'N rows removed' (filter) and 'table unchanged' (drop)?" | `lineage_walk.py:33` (P5: a `Gone` note, "not confirmed"); `:587` (note or grey). |
| O5: reach "16 tables and 13 plots; 4 more tables no plot reads also built from it" | **ANSWERED IN PART.** D-0346 (line 380): "Each line shows its reach: how many tables and plots depend on it"; "A join that no plot reads is not offered". D-0326 (line 360): opening builds and stores every tier 1 and tier 2 table. Not decided: whether the count includes unread tables. | "Does the reach count (N tables) include the tables no plot reads, shown as a separate number?" | `lineage_walk.py:31` (P4: unread places counted apart in `Walk.unread`, not a line). |
| O6: dropping a key column, by name or by place | **ANSWERED IN PART.** D-0358 (line 392): "4. B I think it should be refused by place"; D-0371 (line 405): the refusal applies only to an audit step. Still open: whether a declared key (`is_entity_key`) with no later join is refused like a join key. | "A declared entity key that no later join uses: may it be dropped in the audit, as the place rule implies, or refused like a join key?" | `key_drop.py:1-9` (by place, one rule); `:23` (declared key not refused, PROVISIONAL); `lineage_walk.py:49` (P15, PROVISIONAL). `join_keys.py` has no `key_drop_problem` (only a comment at `:300`). D-0358's "Not built" note is stale. |
| O7: tables no plot and no join reads: a line? | **ANSWERED IN PART.** D-0346: "A join that no plot reads is not offered" (joins only). D-0416 (line 450): remove-all reaches a table no plot reads. D-0415 (line 449): unlinked tables "NOT ticked in (A)". Shown-unticked or not shown: not said. | "Should a table that no plot and no join reads appear as an unticked line in the normal dialog, or only under 'remove from all the data'?" | `lineage_walk.py:31` (P4: not a line, counted apart). This differs from the report's option 3. |
| O8: self-join; joins not left or inner | **OPEN** for the walk. No line on lineage display. D-0183 (line 212) covers self-join warnings in the recipe check, not the audit. | "Are joins that are not left or inner, and a column present twice, shown grey with the reason in the audit dialog until a recipe needs them?" | `lineage_walk.py:35` (P7: a column twice is grey; other joins unread); `step_effects.py:30, 64` (PROVISIONAL, O8). |

### QUESTIONS_FROM_STEP1 items 1 to 7

| Question | Status | What is still to ask her | Code check |
|---|---|---|---|
| 1. What is a line at the source level? | **OPEN.** D-0332 (line 366) gives audit lists per tier only; no source list. | "Is a source table's line its tier 1 (own steps) or the source file?" | `lineage_walk.py:22`; `lineage_records.py:58` (grey `no_step_list`, PROVISIONAL). |
| 2. Empty tier 3, "only this plot" creates the plot's tier 3? | **ANSWERED IN FULL.** D-0346 (line 380): "the audit copy gives the plot its own audit steps at tier 3 even when the recipe has no tier 3 steps for it; its reach is one plot"; her answer "Tick". | Nothing. | `lineage_walk.py:36` (tier 3 always a line). |
| 3. T2 chosen, join has no T2 steps: does a step at T2 create T2? | **ANSWERED IN PART.** D-0346: the line is the lowest level that has steps (so tier 1 is shown). It says the T3 line creates tier 3 but says nothing about T2. | "When a join has no tier 2 steps and the user picks T2, may a step at T2 create the join's tier 2?" | `lineage_walk.py:34, 36` (P6, P8). The `(O3)` label in P8 is the code's own numbering, not LOGIC_REVIEW O3. |
| 4. Second group "linked by a join" still needed? | **ANSWERED IN PART.** D-0415 (line 449): lineage places (A) and a separate key option (B). Her words do not name the join-linked group. | "Is the group 'linked by a join on the key' still offered, or do the lineage and the chosen levels replace it?" | `lineage_records.py:34-37` (LINEAGE, JOIN_LINKED); `lineage_walk.py:19-20, 530-533, 552` (both groups kept). |
| 5. Other actions joining the readings (unpivot, 267 grey lines) | **ANSWERED IN PART.** D-0353 (line 387): "Same column, with a note (Recommended)"; D-0356 (line 390) names of compute, group-by, cast; D-0444 (line 478) fill and strip names. Unpivot is named nowhere. | "Should unpivot's names (the columns it creates from values) be read, or stay grey?" | `step_effects.py:7-13` (no unpivot); `:24` (an action outside the list is `unread`, grey). |
| 6. Joins other than left and inner | **OPEN.** Same as O8. | Same as O8. | `step_effects.py:30, 64`. |
| 7. `x = pl.col('y')` under its own name: note naming the other column? | **ANSWERED IN PART.** D-0353: same column with a note. D-0356 (line 390): names only, never formulas. Whether the note names the other column is not decided. | "Should the note name the other column (`y`) the values may come from?" | `lineage_walk.py:28-29` (PROVISIONAL; `knows_source_of_values` False). |

### DESIGN.md Q1 to Q11

| Question | Status | What is still to ask her | Code check |
|---|---|---|---|
| Q1: renamed then renamed back, same column? | **ANSWERED IN FULL.** D-0357 (line 391); D-0445 (line 479). | Nothing. | `lineage_walk.py:25-26, 32`. |
| Q2: walk reads step arguments (hybrid) or plan only? | **ANSWERED IN FULL.** D-0351 (line 385): "Yes, checked (Recommended)"; D-0356 (line 390). | Nothing. | `step_effects.py:1-13` (closed list, "EXACTLY"); `lineage_walk.py:15-16`. |
| Q3: recomputed under own name, same column with note? | **ANSWERED IN FULL.** D-0353 (line 387): "Same column, with a note (Recommended)". | Nothing. | `lineage_records.py:68` (`NOTE_RECOMPUTED`); `lineage_walk.py:26-27`. |
| Q4: source read by plots, empty tier 2 in joins: hidden or kept? | **ANSWERED IN PART.** D-0346 (line 380): "only distinct tables are lines", her "Tick". The shape of this case was not named by her. | "For a source table plots read directly and joins read with empty tier 2, is the hidden choice acceptable under D-0346?" | `lineage_walk.py:34` (P6, "as written"). |
| Q5: reach counts unread joins; is "a table" a distinct stored table? | **ANSWERED IN PART.** D-0346 (joins no plot reads not offered); D-0326 (line 360) stores tier 1 and 2 of every table at opening. The count is not decided. | "Does the 'N tables' count include the unread tables that are stored?" | `lineage_walk.py:31` (counted apart); `remove_from_all.py:14-17` (reaches unread tables). |
| Q6: column gone at a place: absent, grey, or a note? | **OPEN.** D-0347 gives the principle only. | "For a place where the column is gone: absent from the list, grey with a reason, or a note under the line?" | `lineage_walk.py:33` (a `Gone` note, not confirmed). |
| Q7: source file as a note or a line of its own? | **OPEN.** Same as step item 1. | "Is the column's name in the source file a note on the first line, or the source file a line of its own?" | `lineage_records.py:58`. |
| Q8: drop of a join key: grey with the D-0297 sentence, or not offered? | **ANSWERED IN PART.** D-0297 (line 331): join-key drop refused in the audit with a plain sentence; D-0371 (line 405): refused only where a later join uses it. Grey or not offered is not decided. | "A refused drop of a key: shown grey with the reason, or not offered at all?" | `lineage_walk.py:44-46` (a refused line is grey); `lineage_records.py:346`. |
| Q9: full join with keys of different names: other key offered? | **OPEN.** No line. | "In a full join with keys of different names, is the other table's key offered as a line for 'remove from all'?" | `remove_from_all.py:10-11` (key family = declared keys plus join key pairs); `step_effects.py:64` (full join unread). |
| Q10: when is a type "another type"? | **OPEN.** D-0337 (line 371) says the type is shown, no rule for what counts. | "Does a 32-bit and a 64-bit whole number count as another type?" | `lineage_records.py:67` (`NOTE_ANOTHER_TYPE`, compares the type strings, reasoned). |
| Q11: order of lines | **OPEN.** No line. | "Order of lines: data flow only, or the place she looks at first?" | Not checked. |

### DESIGN.md Q12 to Q28

| Question | Status | What is still to ask her | Code check |
|---|---|---|---|
| Q12: typed value that cannot be written at one place | **ANSWERED IN PART.** D-0202 (line 231): "I would go for a." (typed per node; lossless only). D-0376 (line 410): "well decimal should not arrives for an integer column because decimal is not integer" (filter form, one line refused). Scope of the audit refusal open. | "When a typed value cannot be written at one place, does that block the whole dialog, only that line, or grey that line?" | Not checked. |
| Q13: may an audit filter value be a date? | **ANSWERED IN PART.** D-0061 (line 90): "a date picker" (HOME filters). D-0202 types the value per node. | "May the value be a date, and how is a column that is a date at one place and text at another typed?" | Not checked. |
| Q14: plot made impossible: listed as "cannot be drawn" before confirmation? | **ANSWERED IN PART.** D-0316 (line 350): the dialog shows the plots affected before confirmation. D-0327 (line 361): a recipe with an unrenderable plot is refused at opening. | "Is a plot that a step makes impossible listed as 'cannot be drawn' in the dialog before she confirms?" | `lineage_records.py:78` (`PLOT_USES_COLUMN`, a consequence). Code assumes the listing. |
| Q15: a ticked place covers ticked places below: covered and not written, told, or silent? | **ANSWERED IN PART, with a conflict.** D-0198 (line 227): her words "The later ones show as 'covered by T1' and are not written" (agreed in her turn). D-0198 also says "only the earliest ticked node ... is still her idea ... not decided". D-0316 (line 350) ticks every place when the dialog opens. | "When a ticked place covers ticked places below it in its chain, are those below written, or shown as covered and not written?" | No "covered" rule found in `libs/utils/src/utils` (grep: no file). |
| Q16: row count per line alone, or with the other ticked lines? | **ANSWERED IN PART.** D-0316: rows and plots affected are shown before she confirms. Per line or whole run: not decided. | "Is the row count per line alone, or the total of the ticked lines, and may it change on another tick?" | Not checked. |
| Q17: same step added a second time | **OPEN.** No line. | "Same step added a second time: refused, warned, or accepted showing 0 rows removed?" | Not checked. |
| Q18: `null_values: []`, is the user told when the no-value count is 0? | **OPEN.** D-0035 (line 64): `null_values` stated, no default; D-0042 (line 71): `na` stated, no default. Neither says the user is told. | "When the no-value count is 0 with `null_values: []`, is the user told that empty text is not missing?" | Not checked. |
| Q19: a step that removes every row | **OPEN.** No line. | "A step removes every row of a table: warn, block, or show the count only?" | Not checked. |
| Q20: same value matches different row counts at two places (recode) | **ANSWERED IN PART.** D-0203 (line 232): "yes warn that is good" (values not one-to-one between nodes). The recode case without a cast is not named. | "Is a warning needed for a recode between two places, beyond the count per line?" | Not checked. |
| Q21: distinct samples besides rows | **OPEN.** No line. | "For a long table, should the dialog also give the number of distinct samples?" | Not checked. |
| Q22: does "picture changed" count rows dropped for missing values? | **ANSWERED IN PART.** D-0318 (line 352): "picture changed" = "the columns or rows the plot itself uses changed". Treatment of missing values: not said. | "Does 'picture changed' count rows the plot drops for missing values or by its own filter?" | Not checked. |
| Q23: earlier-computed value still includes removed rows | **OPEN.** Context: D-0146 (line 175) places audit steps at the end of each list. | "Must a line say that a value computed earlier in the tier (z-score, mean, rank) still includes the removed rows?" | Not checked. |
| Q24: removal after `head`, `sample` or `unique` | **OPEN.** No line. | "Must the user be told that a removal after `head`, `sample` or `unique` does not bring other rows in?" | Not checked. |
| Q25: names behind "reaches 3 tables and 5 plots", on demand or always? | **ANSWERED IN PART.** D-0346 (line 380): each line shows its reach (counts). D-0416 (line 450): the list of tables is shown before confirmation (remove-all only). | "For the lines, are the names behind the reach shown on demand or always?" | Not checked. |
| Q26: explanation of T1, T2, T3 in HOME | **OPEN** for HOME. D-0306 (line 340) is Blueprint wording only. | "Is a one-time explanation of T1, T2, T3 in the dialog enough, or do the labels change to plain words in both screens?" | Not checked. |
| Q27: whole group ticked or unticked in one click | **OPEN.** No line. | "Can a whole group of lines be ticked or unticked in one click?" | Not checked. |
| Q28: summary says which places could not be checked | **ANSWERED IN PART.** D-0195 (line 224): "Than also ensure that the whole lineage is really searched and found (no silent failure I think)". Content of the summary: not decided. | "Must the summary say which places could not be checked and that the step is not written there?" | `remove_from_all.py:26-29` (`may_stay` list, F1 review). Not checked against the dialog. |

## 3. Questions asked twice under different ids

- **LOGIC O3 = DESIGN Q1.** Same question (rename back). Both answered by D-0357.
- **LOGIC O4 = DESIGN Q6.** Same question (column gone at a place).
- **LOGIC O5 = DESIGN Q5 (reach count).** Same question, different wording.
- **LOGIC O8 = QUESTIONS_FROM_STEP1 item 6 = DESIGN Q9 (partly).** Joins that are not left or inner.
- **QUESTIONS_FROM_STEP1 item 1 = DESIGN Q7.** Source level as a line.
- **Overlapping, not identical:** LOGIC O1 with step item 4 (which groups or tables get a line); LOGIC O2 with DESIGN Q2 and Q3 and step items 5 and 7 (names read, recompute notes); DESIGN Q4 with step items 2 and 3 (empty tiers); DESIGN Q8 with LOGIC O6 (dropping a key); DESIGN Q25 with LOGIC O5 (reach wording); LOGIC O7 with DESIGN Q5 (tables no plot reads).

## 4. The handoff (`.claude/logs/handoffs/handoff_active.md`)

- Line 138 "LBFB questions O1 to O8": O2 answered by D-0444 (correct, but D-0356 at line 390 already answered it on 2026-11-20, which the handoff does not say). O3 answered by D-0445 (correct).
- Line 138, O1 paragraph: "two points wait for her confirmation" is stale. D-0416 (line 450) answered those four points.
- Line 138, "O4 to O8 open": stale for O6, which D-0358 answers by place (partly; the declared-key part is open). O4, O5 and O7 are partly answered. O8 is open.
- Line 139, "Q1 to Q3 are answered by D-0351 to D-0354; one point of Q1 still to confirm: two renames in different tiers": stale. Q1's point is answered by D-0357 (line 391) and D-0445. D-0354 is the audit file format, not a Q answer.

## Not verified

- Ledger lines 1 to 174 and 233 to 279 were searched by keyword only, because the search tool omits long lines. Lines 340 to 479 were read in full.
- The "all_raw data" quote in the LOGIC_REVIEW intro is attributed to D-0355. D-0355 (line 389) does not contain it, and the ledger has no "all_raw" line (verified by grep).
- Code: I read the module headers and grep hits only. I did not read whole functions, run the tests, or check the default ticks in the HOME dialog.
- DESIGN.md section 6 (U1 to U13) is not in the owner question list, so it is not tabled.
- I did not read `tmp.md`.
