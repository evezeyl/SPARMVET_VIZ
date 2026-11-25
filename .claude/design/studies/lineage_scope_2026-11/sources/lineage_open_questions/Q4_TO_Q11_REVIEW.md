# Lineage design questions Q4 to Q11, checked against the decisions up to D-0454 (scout, 2026-11-21; filed by the coordinator)

Ordered by D-0456. Source of the questions: `tmpAI/panel/lineage_tests/DESIGN.md` section 5.1 (lines 623-634). "TO CONFIRM" = the answer rests on the review session's reading in a bracket, not on her words. No test was run.

## Summary
- Answered: 1 (Q6). Changed: 2 (Q5, Q8). Still open: 5 (Q4, Q7, Q9, Q10, Q11).
- Q1 to Q3 were answered earlier (D-0357, D-0445; D-0351, D-0356, D-0444; D-0353).
- Eleven test cases change. Eight new questions (N1 to N8) are in no list yet.

## The table for the owner
| Q | The question, in plain words | Status | Options (what each means for the user) |
|---|---|---|---|
| Q4 | A source table is read directly by plots AND by joins that add no step of their own. "Only distinct tables are lines" gives one line. Can a step be written only for the plots that read the table directly, not for the joins? | STILL OPEN for this shape (D-0346 gives the general rule) | (a) one line: the step reaches the joins and the plots; (b) a second line: the direct plots only |
| Q5 | Does the reach count the tables no plot reads? | CHANGED: D-0447 (counted, said apart) and D-0451 (they are lines too). The meaning of her "A" in D-0447 is TO CONFIRM | nothing left, except the six questions of `tmpAI/coordinator/lineage_unread_tables/WHAT_CHANGES.md` |
| Q6 | A place where the column no longer exists: a tick line or not? | ANSWERED: D-0446: not a tick; a consequence note. The wording of the note is hers to read | - |
| Q7 | A column at the very start (the source file): is the file's own column name a note on the first line, or a line of its own? | STILL OPEN | (a) a note on the first line; (b) a line for the source file, which the user cannot write into |
| Q8 | A drop of a join key that a later join needs: shown grey with the reason, or not offered at all? | CHANGED: refused by place (D-0358, D-0371, D-0448); an uncertain drop is allowed with a warning (D-0449). Grey or hidden is still open | (a) grey with the reason; (b) not offered |
| Q9 | A full join whose two keys have different names: does "remove from all the data" also remove by the other key? | STILL OPEN (D-0416 says "every table that holds the key column"). A full join is not followed YET (D-0452) | (a) yes, removed there too; (b) no: the sample stays there (a partial removal the user must be told about) |
| Q10 | "The column has another type here": which difference earns the note? | STILL OPEN (D-0337: "I do not think its so important for us") | (a) any difference of the engine's type; (b) only a change of kind (number, text, date) |
| Q11 | The order of the lines in the dialog | STILL OPEN | (a) the place looked at first, then the flow of the data; (b) the flow of the data alone |

## New questions raised by today's decisions (in no list yet)
- N1. A red line for a join not YET followed (D-0452): can it be ticked (with the warning), or not?
- N2. D-0453 "it might becomes grey again": a normal line, or the grey line that cannot be ticked? (TO CONFIRM)
- N3. A key drop through a join the app cannot follow: allowed with the warning (as D-0449), or refused as today?
- N4. D-0450: are the consequences shown before confirming for every audit step, or only for drops? (the review session's reading)
- N5. Where does a consequence note go when no line leads to that place?
- N6. "Remove from all the data" reaches the two demo tables that nothing links (Quality_metrics, Detailed_summary): keep?
- N7. Is a source that no join links part of a lineage (it is not a line of the normal dialog under D-0451)?
- N8. A join that reads a join (D-0344, not built): refused, or a red warning?
Also open elsewhere: the six questions of `lineage_unread_tables/WHAT_CHANGES.md`; the six choices of `lineage_semi_join/REPORT.md`; choices A to E of `drop_uncertain/REPORT_FOR_THE_OWNER.md`.

## Test cases that change
| Case | Where | Changed by | Must assert instead |
|---|---|---|---|
| L005 | DESIGN.md:83-88; `libs/utils/tests/test_lineage_walk.py:80-90` | D-0451 | the join no plot reads IS a line |
| L002 | DESIGN.md:63-68; `test_lineage_walk.py:68-77` | D-0451 | 14 lines, nothing "unread" |
| L006 | `test_lineage_walk.py:609-615` | D-0451 | same |
| L034 (drop rule) | DESIGN.md:243-247; `test_lineage_walk.py:420-428` | D-0449 | an uncertain drop is allowed with the warning |
| joins not followed | `test_lineage_walk_follow.py:102-114`; `test_lineage_walk.py:352-359` | D-0452, D-0454 | a warning sentence that holds "YET"; red TO CONFIRM |
| consequence note | DESIGN.md:192-211; `test_lineage_walk.py:379-395` | D-0446 | a note, no tick |
| reach wording | `test_lineage_walk.py:76, 87, 90` | D-0447 | the two-part count |
| remove from all | DESIGN.md:332-338; `test_lineage_walk.py:252-273` | D-0415, D-0416 | the separate option, by key at T1 |
| L082 to L084 | DESIGN.md | their basis is a bracket in D-0195, not her words | TO CONFIRM |
| declared entity key | DESIGN.md:217-221; `test_lineage_drop.py:193-204` | D-0448 | dropped by place like any key |
| recomputed column | DESIGN.md:228-232 | D-0353 | same column, with a note |

Earlier U-questions of the design: U1, U6, U8, U10 changed; U3, U12 answered; U2, U5 open; U4, U9, U11, U13 partly answered; U7 not verified.

## Not verified
No test run; several test bodies not read in full; D-0031, D-0313, D-0102 not read; the shape claimed in Q4 (DESIGN.md:627) not checked on a recipe.

## Her remarks of 2026-11-21 evening (channel block M501; NOT decisions, the review session asks her again)
Her words: "1..maybe export should export all the tables if there are included in a recipe even if no plot..3. maybe because the scoping of where the removal of the second table has been done ? Of we remove in the origin of the second table it will follow all no.?. O thought a refused line was because could not trace and we do not know the effects where a red warning should be and if where red warning then we cannot thick ... Also if we have no good way to guide the user and are usure of our effects we should consider not allowing those changes or at least Warm in red ...i do not think we get that complicated cases and as we wait our use case is to remove bad samples but from the quality Insurance but who knows..."

Her lean, as the review session reads it (not her words): (1) the export could write ALL the tables of a recipe, also those no plot reads; (2) for the left join the scope explains the effect, and the dialog must say it before she confirms; (3) a line the app cannot trace is a RED warning and CANNOT be ticked; when unsure of the effects, do not allow the change, or at least warn in red. Point (3) CONFLICTS with ledger D-0449 (an uncertain drop is allowed with a warning) and with the branch task/drop-uncertain-allowed built from it: that branch is NOT merged and waits for her answer. Her use case: removing bad samples found by quality control; she does not expect complicated cases.
