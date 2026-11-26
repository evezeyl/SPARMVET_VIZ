# What blocks the build (coordinator, 2026-11-21, evening)

Her question: "what is remaining that blocks the build ?" Facts collected by a read-only survey of the tasks, the handoff, the ledger (D-0406 to D-0457) and the tables waiting for her. Counts are from those files; no code was run for this page.

## The short answer
- UPDATE 2026-11-21 night: the hold of the 37 statements is narrowed. Checked against the review session's transcript, 27 were on your screen in the question you answered; 10 were really added. They come to you as eight plain questions (`tmpAI/coordinator/ledger_words_check/RECHECK_AGAINST_TRANSCRIPT.md`; row 5 is answered: ledger D-0459, her words "ok strike is good - yes."). The names pass and the deployment specification now wait mainly on their own tables. Engine stage 0 is decided (D-0458) and running.
- Almost nothing is blocked by missing work. It is blocked by about 70 open questions spread over 20 tables, and by ONE hold of mine: nothing is built from today's ledger lines on the names and the deployment until you have gone through the 37 statements the relay added to them.
- Six of the eleven work streams have nothing that can be built now. Five have small pieces that can.
- Ten answers (list below) would unblock most of the building.

## Per work stream
| Stream | Can be built now (no open decision) | Blocked by (whose) | Built, waiting | Touches engine-specific code? |
|---|---|---|---|---|
| 1. The names pass (one `ui_label` everywhere) | nothing | (a) the 37 added statements: strike or keep (yours); (b) eight choices of the names table: screen words, rename of the internal `label` key, old sessions, the order of the migration (yours) | designed, not built | the recipe check in part |
| 2. The deployment specification | nothing | (a) the same 37 statements; (b) the 18 choices of the specification table; (c) what happens when nothing can be written; (d) 20 choices for a page with no user; (e) 12 choices on where uploaded data goes; (f) 8 choices on the write test; (g) the recipe name rule: refused at load, or an advice (all yours) | nothing | reading of data files, stored tables |
| 3. The lineage and the Create audit step dialog | one list of all open lineage questions (records only) | (a) tables no plot reads: ticked or not, what the line says (5 questions left after D-0457); (b) Q4, Q7, Q8, Q9, Q10, Q11; (c) eight new questions N1 to N8; (d) about 28 smaller questions of the test design, one at a time (yours) | nothing | YES: it reads Polars step names and join kinds |
| 4. "Remove from all the data" | nothing (the logic is merged) | six points before the screen: which column is "the sample key", may one table be unticked, how "may stay" and the tables that compute across samples are shown, the wording (yours) | the logic, merged | yes |
| 5. The column drop the app cannot follow | the small fixes of the review | ONE question: allowed with a warning (D-0449) or red and not tickable (your remark of the evening); then choices A to E (yours) | branch `task/drop-uncertain-allowed`, reviewed "fix first", NOT merged | yes |
| 6. The semi join; the warning for joins not YET followed | nothing | build the semi join now or keep it red; which join kinds are red; the full sentence; what "grey again" means; what the docs say to avoid (yours) | the study | yes |
| 7. The engine boundary | stage 0 if you say yes (marks and a guarding test; about 2 sessions; no behaviour change) | stage 0 before the demo: yes or no; then the target (yours) | the study and its table | it IS the engine question |
| 8. The Gallery | two record pieces (the model diagram, two ADR notes) | names and headings of 13 examples; the chart-type words; nine taxonomy choices; the corrections of 18 examples, each new picture shown to you first (yours) | the picture key, merged | plotnine and Polars in part |
| 9. Data Import | one test of a failed replace | a data file cut in the middle (five options); short rows, empty files; the words of the messages; "the old file is replaced for good" said before (yours) | nothing | the reading of files |
| 10. HOME and the export | two small defects (the audit panel blank for 1 to 3 s; a typed reason lost during a redraw); the plain text for a plot that cannot be built | the HOME browser test that fails on dev (four repairs); rows a plot does not draw (A to E); tables no plot reads exported and viewable (D-0457): which tiers, how you reach them; the help beside the screen; your manual test of the panel widths (yours) | panel widths merged, provisional | plot drawing and export: yes; HOME's frame: no |
| 11. Other | the list of old words | the old-words audit that fails on dev; the statistician agent (your "yes" typed in the coordinator session); two held branches (`task/one-python`, `task/worktree-imports`); the documents to move out of the scratch folder (8 choices); your push of `dev` | two branches | no |

## The order I propose for your answers (most unblocking first)
| # | Question | It unblocks | Where |
|---|---|---|---|
| 1 | The 37 statements the relay added to today's lines on names and deployment: strike or keep | the names pass, the deployment specification (the two largest builds) | `tmpAI/coordinator/ledger_words_check/TABLE_FOR_THE_OWNER.md` |
| 2 | Engine stage 0 before the demo: yes or no | every later build is written inside the guard; costs about 2 sessions | `tmpAI/panel/engine_boundary/TABLE_FOR_THE_OWNER.md` choice 3 |
| 3 | A line the app cannot trace: tickable with a warning, or red and not tickable | the drop branch, the join warning, question N1; it is one principle for three places | `tmpAI/coordinator/drop_uncertain/REPORT_FOR_THE_OWNER.md` and `REVIEW.md` |
| 4 | The HOME browser test that fails on dev: which repair | a green test suite on `dev` for everything that follows | `tmpAI/coordinator/smoke_preview_filter/REPORT.md` |
| 5 | The names table: the eight remaining choices | the names pass, after 1 | `tmpAI/panel/names_whole_app/TABLE_FOR_THE_OWNER.md` section 9 |
| 6 | The deployment specification: its 18 choices, and "nothing can be written" | the specification, then the bundle import, the audit folder, the write test | `tmpAI/panel/deployment_standard/TABLE_FOR_THE_OWNER.md` section 8 |
| 7 | "Remove from all the data": the six points | its screen: your stated use case (removing bad samples) | `.claude/tasks/tasks.md`, task AUDIT-REMOVE-FROM-ALL-DATA |
| 8 | Tables no plot reads: ticked or not; which tiers are shown and exported | the dialog lines and the export of D-0457 | `tmpAI/coordinator/lineage_unread_tables/WHAT_CHANGES.md` |
| 9 | The semi join: build now or keep red; a note for the left join | the join warning and the docs | `tmpAI/coordinator/lineage_semi_join/REPORT.md`, `tmpAI/panel/left_join_note/FOR_THE_OWNER.md` |
| 10 | The Gallery: names, chart-type words, taxonomy, corrections | the Gallery rebuild for the demo | `tmpAI/panel/gallery_taxonomy/`, `gallery_verify/`, `gallery_study/` |
Then: a cut data file and rows a plot does not draw (results; no shipped recipe affected today); Q4 to Q11; the rest.

For the demo (HOME and the Gallery first): 4, 10, 7 and 3 matter most; 1, 5 and 6 are the largest builds but the demo runs without them.

## What waits on the engine study, and what does not
- Nothing HAS to wait: the study is done and stage 0 is the same under every design option.
- If stage 0 is built first, everything after it is written inside the guard. Streams 3 to 6 (the lineage, the audit, the joins) are the ones that touch Polars names; from today their new code reads those names from the existing lists and adds no Polars elsewhere.
- Engine-neutral and free to go at any time: the names pass (records and keys), the deployment specification, HOME's frame defects, the records.

## Records found wrong while collecting (being corrected by a scribe; not questions for you)
- The task "Data Import overwrite" still says it waits for your yes; you decided it (D-0434, D-0438).
- A Gallery task is still open although its work is merged (D-0400).
- A Gallery task names two questions you already answered (D-0401, D-0402).
- Two lineage lists disagree on how many questions are left (one counts 5 design questions, the other about 28 smaller ones): both are right; they count different things; one list is to be made (task LINEAGE-QUESTIONS-ONE-LIST).

## Not verified
The counts of choices come from the "to decide" sections of the tables, not from a re-reading of every table; whether the two small HOME defects were started; the data-file-cut and recipe-name reports were not re-read in full.
