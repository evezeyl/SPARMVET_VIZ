# A table as a result, and the stages of a table no plot reads: one panel round (2026-11-22)

Your order (channel block M532). Four viewpoints answered once: scientist, architect, developer, user. They recommend; you decide. Facts and what is already decided: `tmpAI/panel/tables_as_results/FACTS.md`. Each option was judged on merit; what it reopens is in its own column and was not used as an argument.

## Flags first (what could change a result silently or hide a step)
1. **Why tier 2 is refused today.** Not because of a rule about tables. The three refusals (recipe check S07 and J14, and the audit copy) exist because today nothing runs the tier 2 of a table no plot reads: the steps would be written and run nowhere. If the app really builds that tier 2, the reason is gone. No ledger line of yours carries S07 or J14; J14 is named in no text of yours.
2. **The data preview shows 100 rows.** A result table shown only in the preview is not the whole table that is exported (scientist; `app/handlers/home_theater.py:1670`). A result table needs the whole table, or a visible "showing 100 of N".
3. **A tier 2 on a table that feeds a join changes nothing downstream.** A join reads tier 1 of its tables. An author who writes a mean in tier 2 of such a table and expects the join to see it would be wrong, with no message. To be said in plain words in the check and the documentation (architect).
4. **A summary table must be reproducible.** Row order, rounding, number of digits, empty values, the quantile method, and the number of rows per group (n) must be fixed and shown, or the same recipe can give a different report table (scientist).
5. **Audit.** When a sample is removed by an audit step, a result table changes. The user must see it: Original against Audited must work for a table as for a plot, and the export must hold the audited table (scientist, user).
6. **A second kind of entry touches every place that assumes "an entry is a plot"**: HOME sub-tabs, the audit steps kept per plot, the export, the report, the opening build, the lineage walk, BLUEPRINT, the Gallery. A missed place would show a table on screen that is not in the export, or the reverse (architect, developer). It must be built as ONE general entry, not as a special case.
7. **A picture of a table (option 2D)** cannot be sorted, copied or checked cell by cell, and it is not the data that is exported. All four reject it.

## Question 1: may a table that no plot reads have tier 2 steps and a tier 3?
| Option | Scientist | Architect | Developer | User | Reopens (information only) |
|---|---|---|---|---|---|
| **1A** as today: tier 1 only; tier 2 refused | pro: nothing is written that does not run. con: the summary cannot be seen, or is hidden in a plot's tier 2 where it can disagree with another | pro: simplest. con: refuses what you asked on 2026-11-21 ("T1+T2") | pro: no risk. con: leaves your words unanswered | pro: simple. con: the author is told no and the aggregation is lost | nothing |
| **1B** tier 2 allowed on every table and join, really built and stored; a tier 3 only on an entry that shows something (a plot, or a result table of question 2) | **preferred**: a summary is computed data, so it must run. con: storing every tier 2 costs time and space; no drawn check beside it | **preferred**: a tier 2 key already exists for every table; only the three refusals stop it; one rule remains. con: HOME has no way yet to open the tier 2 of such a table | **preferred**: one rule, "a tier 3 needs an entry that shows something" | **preferred**: "every table can have steps; the last stage exists only for what you see". con: a tier 2 on a hidden table still shows nothing unless the user finds it | checks S07, J14, the audit copy refusal; spec row DEC16; `home_audit_steps.md` point 19; a test of the opening build |
| **1C** tier 2 and also a tier 3 on the table itself, with no entry | con: one more unseen place for steps | con: a second kind of tier 3 key, a parallel path | con: riskiest; an invisible tier 3 | con: the same thing as a result table, twice | the same, plus D-0063, D-0237, D-0250 (tier 3 at the plot entry) |

## Question 2: may a recipe mark a table as a RESULT, shown in the plot area as a table?
| Option | Scientist | Architect | Developer | User | Reopens (information only) |
|---|---|---|---|---|---|
| **2A** nothing new: such a table is seen in the data preview and the export | con: the preview is 100 rows, so what is shown is not what is exported | pro: cheapest, one store. con: the author cannot name or curate a result | pro: safe. con: gives no result table | con: the preview follows the selected plot, so a table that belongs to no plot is not found | nothing (D-0457 as decided) |
| **2B** a new kind of entry in a group, beside the plots: a table with its own short name, the table it reads, optional last steps of its own (tier 3), optional choice of columns; HOME shows it in the plot area, in its own sub-tab, as a table; exported as a data file and in the report; audit steps as for a plot | **preferred**: it reads the table, so it is a real reader; the table shown and the file exported are the same object. con: it must fix rounding, digits and row order | **preferred, only as ONE general entry**: one reader, one key, ids unique across plots and tables; a sibling key `tables` in the group (not a `kind` word on a plot entry, which would let the 19 places that read plot entries treat a table as a plot); drawn by the grid HOME already has, never by the plot library | **preferred**: its tier 3 key is of the same kind as a plot's | **preferred**: a summary is a result, and one looks for it next to the plots; it has a name, so the audit line reads "Table <name>" | D-0109 ("a table on itself ... need to have plots"); D-0063, D-0237 (tier 3 at the plot entry: it would be "at the entry"); the BLUEPRINT node kinds; contract sections 2, 5 and 7.2 |
| **2C** a mark on a table (`result: true`), no entry | con: no place for a tier 3 or audit steps; cannot say which columns | con: cannot say which tier, no name, a special case | con: cannot hold a tier 3, a name or a column choice | con: a mark that silently does nothing if misplaced | D-0109 |
| **2D** a plot whose drawing is a table (a picture) | con: loses the values and the precision | con: a picture, not data; the plot library has no table drawing | con: a plot would no longer equal its table | rejected: cannot be sorted, copied or searched | none |

Suggested words, not final (user viewpoint): sub-tab "Table: <name>"; badge "Result table"; dialog line "Table <name> (shown as a result)".

## The link between the two questions
With 2B, a result table READS its table. That table is then no longer "read by nothing": its tier 2 runs, and its last steps live on the entry, exactly as for a plot. So 2B answers most of question 1 by itself, and the checks S07 and J14 would become "no plot and no result table reads this table" under 1A+2B, or go entirely under 1B+2B.

## My recommendation (the coordinator's; yours to accept, change or refuse)
**1B and 2B together, built as one general "entry" (a plot or a table).** All four viewpoints chose the same pair, each for its own reason. It matches your words: T3 is data, tier 2 is still data wrangling, each tier of a table can hold useful information. It removes a refusal that existed only because nothing ran the steps. Its real cost is not time: it is that every place that assumes "an entry is a plot" must change in the same pass, with a test that the screen, the export and the report hold the same table.

If you choose it, these stay yours to decide afterwards (nothing chosen):
- (a) Does D-0109 stand in a changed form? Your words then: "A table on itself can produce results that are interesting for the user but need to have plots". With 2B a recipe could hold a group with result tables and no plot.
- (b) With 1B alone, a table that no plot and no result table reads still has a tier 2 that is built, exported and viewable in the preview (D-0457). Is that wanted, or must a tier 2 always have a reader (then S07 and J14 stay in the form "no plot and no result table reads this")?
- (c) How many rows a result table shows on screen, and whether n per group is required or advised for a summary.
- (d) The Gallery: only plots as examples (as today), or result tables too.
- (e) The words: "table", "result table", the sub-tab and the badge.

## What it means for the two pieces of work in progress
- The lineage library part (a table no plot reads is a line, at tier 1): kept under every option. Under 1B it is extended so that tier 2 of such a table is a line too. Developer's advice: merge it first, then extend.
- The export of every table (tier 1): kept under every option. Under 1B+2B the export loop is reshaped to walk every table and every entry.
- The four questions the review session holds (ticked or not, the words of the line, the reach sentence, the two routes) depend on your answer here.

## A build order if you choose 1B + 2B (developer; each slice complete, no shim)
1. Tests first: the three refusals accept a tier 2 that is really built; one test that screen, export and report give the same table; a test of the stored table's key.
2. The recipe format and check, the reading of tiers, and the key of a table entry, together.
3. The engine: tier 2 of every table and the last steps of every table entry are built.
4. The audit copy and the lineage walk; the export and the report (these can run side by side).
5. HOME: the table sub-tab, the preview, Original against Audited.
6. Gallery and BLUEPRINT.

## Not verified, and one disagreement between the viewpoints and the records
- The architect reads that the opening already builds tier 2 of every table with steps (`opening_build.py:83`); the rule file says the opening build is "DECIDED, not built". One of the two is out of date. Not checked by me; a scout can settle it.
- No viewpoint ran code for this round. The plot library was not searched for a table drawing beyond the registered components.
- The rule texts disagree on where tier 2 is stored (`rules_data_engine.md:27` against `docs/foundations/data_tiering_adr.qmd:32`); to settle in slice 1.

## The four answers, as given
Saved beside this file: `VIEWPOINTS.md`.
