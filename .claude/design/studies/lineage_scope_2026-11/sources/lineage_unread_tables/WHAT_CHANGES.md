# Tables that no plot reads become lines of the audit dialog (D-0451): what changes (scout survey, 2026-11-21; filed and shortened by the coordinator)

READ = read at file:line. REASONED = inferred. No code was run. Nothing is built.

## For the owner first
1. **A step written at such a table is seen nowhere today.** HOME's table view shows only the plot's tables (`app/handlers/home_theater.py:1173-1180`). The export writes data files only for tables a plot targets (`app/handlers/export_handlers.py:1354-1380`). No plot is below such a table (REASONED). So a ticked line there writes a step whose effect no view, no plot and no exported data file shows. It would be only in the audit recipe (D-0324, not built).
2. **"T1+T2" and "T1+T2+T3" cannot exist for these tables today.** The recipe check refuses tier 2 steps on a table or join no plot reads (`libs/utils/src/utils/recipe_check.py:413-416` S07, `:826` J14); the audit copy refuses them too (`audit_copy.py:176-178`). A tier 3 is a plot, so a table with a T3 is read by a plot. Only tier 1 of such a table can be a line.
3. **Demo recipe: six such tables.** Four joins the lineage reaches from the metadata (FastP_with_metadata, Bracken_with_metadata, ResFinder_with_metadata, AR1_MLST_Serotype_Virulence): up to four more lines for a column like the sample id. Two sources linked to nothing (Quality_metrics, Detailed_summary): the walk never reaches them, so they stay out of the normal dialog under D-0451 ("that the walk reaches"). The six other shipped recipes have no such table.
4. **Two routes to the same place.** "Remove from all the data" already writes at these tier 1 tables (`remove_from_all.py:222, 276`; test `app/tests/test_remove_from_all_demo.py:71-79`, 27 places). With D-0451 a tick of the normal dialog would write there too.
5. **The reach words.** For such a line the reach would read "0 tables you can open, 1 more table that no plot reads, 0 plots" (`lineage_walk.py:346-353`). "Tables you can open" does not fit.
6. **A test and a decision disagree (not caused by this):** `app/tests/test_opening_build.py:434-439` asserts that an unused source is not read at the opening; D-0326 says every tier 1 and tier 2 table is built and stored. Flagged only.

## What says the opposite today
Text:
- D-0346 (ledger line 380): "A join that no plot reads is not offered (question Q-A17)." Its origin (`tmpAI/coordinator/QUESTIONS_FOR_THE_STOP.md:125-126`) was a question about a TIER 2 step.
- D-0415 (ledger line 449): tables that no join links "are NOT ticked in (A); they are reached only by (B)". Not touched by D-0451 (the walk does not reach them).
- `.claude/rules/ui_implementation_contract.md:722`: changed today with D-0451.
- `libs/utils/src/utils/lineage_walk.py:31, 36` (notes P4, P8; P4 extends the rule to sources, provisional); `lineage_records.py:33, 296-298`.
- `tmpAI/panel/lineage_tests/DESIGN.md:66, 83-88, 559`; `architect/p2a.md:19, 36-40`. Line 87 gives as the reason "a line that cannot be written": true for tier 2, not for tier 1.
Code (the one exclusion): `lineage_walk.py:515-517` (`if not reach.plots:` the place goes to `Walk.unread`); with it `Unread` (`lineage_records.py:296-303`), `Walk.unread`, `nothing`, `accounted`, `within` (`:326-363`), `_classify` (`lineage_walk.py:540-544`).
Tests that assert the old rule (libs/utils/tests): `test_lineage_walk.py:72-75` (L002), `:80-90` (L005 `..._is_not_a_line_until_a_plot_reads_it`), `:609-615` (L006), `:136, 152`; `test_lineage_walk_follow.py:296-303, 340-345`; `test_lineage_walk_properties.py:89-91`; fixture `lineage_fixtures.py:8`.
Not changed: `remove_from_all.py`, `key_drop.py`, `plan_book.py`, `step_effects.py`, the tier 2 refusals (S07, J14, `audit_copy.py`), the export of data files, tests `test_remove_from_all*.py`, `test_audit_copy.py:752-757`, `test_recipe_tiers.py`, `app/tests/test_schema_tier2.py:230-239`.
The HOME dialog does not call the walk yet (no caller in `app/` outside tests), so nothing changes on screen today.

## Questions it raises (options; nothing recommended by the scout)
Q1. Tiers: (a) tier 1 only (works now); (b) also tier 2 of such a table (needs the check S07/J14 changed); (c) T3 cannot exist there.
Q2. Ticked by default? (a) ticked like every place (D-0316, D-0359); (b) not ticked, because the effect is seen nowhere.
Q3. What the line says: (a) "no plot reads this table"; (b) that, plus "this step changes only the stored table; no plot and no exported data file shows it"; (c) not a tick line but a note under the line that leads to it (the pattern of D-0446).
Q4. The reach sentence for such a line.
Q5. Two routes for one place (the tick, and "remove from all the data"): both, or only one?
Q6. Should a table no plot reads be viewable in HOME (Source / T1), so that a step there can be checked? ANSWERED 2026-11-21, ledger D-0457: yes, viewable in the data preview; and the export writes all tables.

## Not verified
The number of dialog lines before and after on the demo; what the opening build stores today; whether a stored table of such a table is visible anywhere; what an audit export holds beyond data files; the figures 20 / 4 / 13 for the metadata's reach (taken from the test design).

## Her remarks of 2026-11-21 evening (channel block M501; NOT decisions, the review session asks her again)
Her words: "1..maybe export should export all the tables if there are included in a recipe even if no plot..3. maybe because the scoping of where the removal of the second table has been done ? Of we remove in the origin of the second table it will follow all no.?. O thought a refused line was because could not trace and we do not know the effects where a red warning should be and if where red warning then we cannot thick ... Also if we have no good way to guide the user and are usure of our effects we should consider not allowing those changes or at least Warm in red ...i do not think we get that complicated cases and as we wait our use case is to remove bad samples but from the quality Insurance but who knows..."

Her lean, as the review session reads it (not her words): (1) the export could write ALL the tables of a recipe, also those no plot reads; (2) for the left join the scope explains the effect, and the dialog must say it before she confirms; (3) a line the app cannot trace is a RED warning and CANNOT be ticked; when unsure of the effects, do not allow the change, or at least warn in red. Point (3) CONFLICTS with ledger D-0449 (an uncertain drop is allowed with a warning) and with the branch task/drop-uncertain-allowed built from it: that branch is NOT merged and waits for her answer. Her use case: removing bad samples found by quality control; she does not expect complicated cases.
