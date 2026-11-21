# Handoff — Active State (2026-05-10 continued session)

**Branch:** dev  
**Working tree:** clean (all changes committed)  
**Status:** Session focus: Audit-driven quick wins. Completed 3 library/dependency tasks.

## OPEN STATE 2026-11-21, afternoon (time not read from the clock by the writer)
- Recorded 2026-11-21: D-0409 (names question 4, option B, widened: `ui_label` for every name, the export included; the open point on `info.ui_title` is answered by D-0410); new task NAMES-UI-LABEL-EVERYWHERE in `tasks.md` (not started; built with the one pass of D-0407).
- Recorded 2026-11-21: D-0410 (names question 5, option A: the recipe banner uses `info.ui_label`; `ui_title` leaves the recipe format; longer text in `info.description`; replaces the key `info.ui_title` of D-0408; the app features `ui_title` is still open). Folded into NAMES-UI-LABEL-EVERYWHERE; not started.
- Recorded 2026-11-21: D-0414 (lineage question O1 answered by Eve: the Create audit step dialog offers tick lines for all tables that get the step, no matter which lineage; two readings of the review session wait for her confirmation: places start ticked, and a removal by the key at tier 1 of each ticked table; nothing built on them; see the O1 line above); its reading is replaced by D-0415.
- Recorded 2026-11-21: D-0415 (lineage question O1, her correction of D-0414: (A) the normal dialog offers the places of the lineage of where the step was started, all ticked by default; (B) a separate explicit option "remove from all the data", independent of the lineage, only for a removal by an ID or column found in all the tables (the entity key), written at tier 1 of each table that holds it, with a warning; the tables no join links are reached only by (B). Four points of (B) wait for her confirmation; nothing built on (B). Task AUDIT-REMOVE-FROM-ALL-DATA in `tasks.md`, not started.)
- Recorded 2026-11-21: D-0412 (names question 7, option A: allowed-key lists for app features and deployment files, unknown or old keys refused at start with the new name; the customized deployments are `demo-vetinst` and `web-demo`, her answer M445). Part of NAMES-UI-LABEL-EVERYWHERE; the lists wait for the deployment standard; not built.
- Recorded 2026-11-21: D-0413 (an order: a written deployment standard as one document with a machine-readable key list, options per use case; the paths and Data Import questions stay in the deployment study). New task DEPLOYMENT-STANDARD in `tasks.md`; step 1 (scout: `tmpAI/panel/deployment_standard/FACTS.md`) running; step 2 is a table of the structure for her (`tmpAI/panel/deployment_standard/TABLE_FOR_THE_OWNER.md`); no key list before she has seen it.
- Recorded 2026-11-21: D-0411 (names question 6, option A: the deployment banner keys by kind, `title` to `ui_label`, `subtitle` to `description`; the app features `ui_title` and `deployment_name` removed; her condition: the customized deployments still work, proved by a test that can fail; documentation and spec in the same pass). Her answer closes the app features `ui_title`; her confirmation (channel M445 of 2026-11-21): the customized deployments are `demo-vetinst` and `web-demo`; no search for a third. Folded into NAMES-UI-LABEL-EVERYWHERE; not started.
- Running 2026-11-21 afternoon: a builder on the key per Gallery picture (D-0400), worktree `.claude/worktrees/gallery-picture-key`, branch `task/gallery-picture-key` (adds only the key and the notice; no recipe, picture, name or spec change; to be reviewed before any merge); back: the builder of the Gallery picture key (D-0400) is back (branch `task/gallery-picture-key`, commits e47b7d79 and baeb819d, NOT merged; a reviewer is checking it, report to come in `tmpAI/coordinator/gallery_picture_key_review/REPORT.md`); the help study's second run is back (`tmpAI/panel/help_beside/RUN_FACTS_2.md`; a corrections block was added at the top of its `TABLE_FOR_THE_OWNER.md`). Back: `tmpAI/coordinator/home_plot_width/REPORT.md` (HOME: after leaving Audit mode the plot is redrawn at full width by itself within 0.5 to 5 s; not a permanent defect), `tmpAI/coordinator/testlab_conversion/FACTS_AND_PLAN.md` (Test Lab conversion: facts and ten questions for the owner).
- Running 2026-11-21 late afternoon: three panel viewpoints (architect, developer, deployer) on the STRUCTURE of the deployment standard (D-0413), brief `tmpAI/panel/deployment_standard/BRIEF.md`, survey `FACTS.md` beside it; then one table for the owner. The reviewer of `task/gallery-picture-key` is still running.

## OPEN STATE 2026-11-21, late morning (the owner is on a break; the time is not written here because it was not read from the clock by the writer)
- Decided by the owner today and recorded: D-0397 to D-0405 (Gallery questions Q1 to Q7 and Q9; a tag mismatch is an advice). Gallery Q8 comes to her with the table of name fields.
- Tables ready for her, all under `tmpAI/panel/`: `deployment_io/` (reading and writing recipes and data per deployment; fonts added as choice 14), `gallery_verify/` (the 34 examples verified; tag advices), `gallery_taxonomy/` (review of the taxonomy), `gallery_study/Q1_NAMES_AND_HEADINGS_DRAFT.md` and `Q2_CHART_TYPE_DRAFT.md`, `name_fields/` (the purpose of each name field), `help_beside/` (help that stays open beside the screen), `data_import_words/`. Each folder holds `TABLE_FOR_THE_OWNER.md` unless named otherwise.
- Names across the app: the table is written (`tmpAI/panel/names_whole_app/TABLE_FOR_THE_OWNER.md`, 2026-11-21). Recorded: D-0406 (question 1, option A: the principle of the seven kinds of name and the agreed rules); D-0407 (question 2, variant P: the prefix `ui_` on every display key in every file kind, `description` unchanged, old keys refused, one migration pass per file kind). Open, one at a time: what `info` holds, the screen words, the registries, the format version, old sessions, the migration order. Nothing is built.
- Recorded 2026-11-21: D-0408 (names question 3, option A: one name key for a recipe, `info.ui_title`, file name as fallback; `info.label` and `info.name` refused; I01 goes; D-0405 not edited).
- Checked 2026-11-21: `tmpAI/panel/gallery_verify/SOURCES_CHECK.md` (the two unverified Gallery points against EUCAST; not merged into the owner's table).
- Owner's standing order of 2026-11-21 (her words, relayed in the channel): "ps have the coordinator do something unless everything it can do independently is done ?" The coordinator keeps working on everything that does not depend on an open decision.
- Waits for her: her 'yes' for the statistician agent (task PANEL-STATISTICIAN-AGENT); the repair of the out-of-date HOME browser test; every table above. No recipe, name, heading, tag, spec or screen is changed before she has read them.
- Her standing rule of today: an option is judged on merit; 'it reconsiders a decision' is information in its own column, never an argument.

## OPEN STATE 2026-11-21, 09:50 by the clock (note: the time '09:30' of the block below was written about 45 minutes ahead of the clock)
- Nothing is running. `dev` is clean and not pushed; last commits: the ledger lines D-0397, D-0398, D-0399 (Gallery questions Q1, Q2, Q3 decided by the owner) and the UML commit.
- Ready for the owner to read: the deployment study table (`tmpAI/panel/deployment_io/TABLE_FOR_THE_OWNER.md`); the Gallery drafts for Q1 and Q2 (`tmpAI/panel/gallery_study/Q1_NAMES_AND_HEADINGS_DRAFT.md`, `Q2_CHART_TYPE_DRAFT.md`); the Data Import message texts (`tmpAI/panel/data_import_words/TABLE_FOR_THE_OWNER.md`) and facts (`tmpAI/coordinator/data_import_questions/ANSWERS_A_AND_B.md`); the cause of the failing HOME browser test (`tmpAI/coordinator/smoke_preview_filter/REPORT.md`: the test is out of date; she chooses the repair).
- She answers the Gallery questions one at a time (Q4 to Q9 are open). No recipe, name, heading or spec is changed before she has read the drafts.
- Her standing rule of 2026-11-21: an option is judged on merit; 'it reopens a decision' is information in its own column, never an argument. Every panel brief carries it.

## OPEN STATE 2026-11-21, 09:30 (resumed after the session refresh)
- Nothing is running. `dev` holds the UML commit and one records commit after it; clean; not pushed.
- Done since the park: the cause of the failing HOME browser test (the test is out of date; no fix yet); the facts for the owner's Data Import questions a and b; the table of message texts (question c); the UML of the library tiers, the app frame and the Gallery.
- Waits for the owner: the repair of the HOME test; the Data Import points S1 to S14 and the message texts; the two provisional refusals of Data Import (bundle-imported recipe: refused by choice, not by failure; deployment that finds data by table name: only the pipeline test deployment uses it); the Connect template; the new small tasks above in `tasks.md`.

## PARKED 2026-11-21, 08:15 (owner's order, to refresh the session for StarUML)

- Nothing is running. No worker was stopped. `dev` = 7022ac9f plus one records commit for this park; clean; not pushed (the owner pushes).
- No worktree holds uncommitted work of a running task. The older worktrees are unchanged (see the coordinator note).
- First task after the restart: HOME-SMOKE-PREVIEW-FILTER-FAILS (find the cause with evidence; report to the owner before any fix).
- New low-priority task: TESTLAB-REFORMAT-CONVERSION (plan only).
- Restart: read `tmpAI/coordinator/progress_2026-11-14_session3.md` (top block), then `tmpAI/agent_channel.md` (grep `### M42`, the file is large), then the block below.

## OPEN STATE 2026-11-21, 07:30

- HOME Data Import format check merged into `dev` (two reviews). Controls on head `076dae89`: 13,406 headless passed; 453 browser passed with 1 known failure (also fails on `dev`) and 1 load flake (passed alone twice); 9/9 app features start.
- `dependency_index.md` to regenerate (not yet done).
- Provisional points of the merge (not the owner's decisions): the refusal for a recipe imported from a bundle; the refusal in a deployment that finds data files by table name (`by_dataset_id`); the refusal by file name; the wording of the messages.
- Waits for the owner: DATA-IMPORT-OVERWRITE (an upload replaces the data file with no copy of the old one); the three provisional refusals above; the message wording (HOME-DATA-IMPORT-MESSAGES-WORDS).
- New open entries in `tasks.md`: HOME-DATA-IMPORT-MESSAGES-WORDS, HOME-DATA-IMPORT-HANDLER-TEST, HOME-SMOKE-PREVIEW-FILTER-FAILS (the browser test `test_a_preview_filter_never_changes_the_plot` fails alone on `dev` `a9ec41dd` and on the branch; cause not investigated).

## OPEN STATE 2026-11-21, 04:35

- dev head `ff8205e8` (Test Lab review merged as documents), plus the records commit that follows this block. Both fallback reviews are complete as documents: BLUEPRINT `.claude/design/blueprint_revision/GUIDE.md` (merged `52c4bcfa`), Test Lab `.claude/design/lab_revision/GUIDE.md` (merged `ff8205e8`). Remains for both: the owner's reading and the verifications of section 3 of each guide.
- RUNNING at 04:35: the Data Import fix (HOME, points 1 to 4 of task HOME-DATA-IMPORT-FORMAT-CHECK), builder in worktree `.claude/worktrees/data-import-format`, branch `task/data-import-format`. When it reports: a reviewer reviews the diff and runs the full controls on the branch, then merge. Point 5 (the overwrite) is not built: it waits for the owner (DATA-IMPORT-OVERWRITE).
- Earlier state, 03:25, follows. Former text, kept: dev head `52c4bcfa` (BLUEPRINT review merged as documents: `2c70694e` and `52c4bcfa`), plus the records commit that follows this block. Not pushed: the owner pushes. Ledger ends at D-0396.
- Merged today after 16:50 (one line each):
  - `e6ae8d0f` HOME fixes of the browser walk: the screen cleared while a recipe opens; the header strip in a narrow window; the filter form cleared with the filters; the README tiers line; the help page; a test that no view rebuilds a stored table.
  - `cdbef5ff` lineage walk, step 0b: the plan of every place composed from the build's own code; the audit's key-drop gate given the plan; an app error no longer shown as "cannot tell". PROVISIONAL: a drop the walk cannot follow is not written (owner's choice open: allow with a warning, or refuse).
  - `7a8369e2` ledger history test redone (D-0380).
  - `84163a1b`, `a7dfc724` step 1 of the BLUEPRINT review (D-0395); the earlier studies kept in git.
  - `211270e2` the Export test under the opening cover.
  - `b429c632` three HOME fixes: whole numbers only for an integer column at entry (D-0376); Pending badge and Apply shown in Audit mode only (D-0377); confirmation before Delete Session (D-0378).
  - `3c66e790` Gallery: four dead links replaced, three without a page left as they are (ecdf, freqpoly, qq_plot; D-0379); "Clear all ticks" button.
  - `0c17fff8` Gallery: the name read from `ui_label` (D-0387); the index rebuilt at start and never holding a machine-dependent path; a repeated name left out with its reason (PROVISIONAL: the first in folder-name order is kept); the data sample read by the picture's path (no decision number given in the brief).
- Running at 03:25: nothing. Worktree `.claude/worktrees/panel-widths` and branch `task/panel-widths` removed.
  - Panel widths (FRAME-PANEL-WIDTHS; D-0375, D-0381 to D-0386) merged as `8cd699f7`: all user spaces; side panels follow the window (left 17 %, 190..340 px; right 15 %, 170..340 px), the main panel keeps at least half, the grip drag, double click resets; HOME right panel closed and empty in Exploration, opens with Audit mode. Values provisional in `app/modules/frame_widths.py` until her test (D-0386). Reviews: `tmpAI/coordinator/panel_widths_review/`, `panel_widths_review2/`, `panel_widths_review3/`. Controls: 13,565 headless passed; 432 browser passed (4 load flakes passed alone); 9 of 9 app features start.
  - Open for her test, none blocking: HOME right panel blank 1 to 3 s when Audit mode opens; HOME: text typed in a reason box while the list is redrawn is lost; HOME: Apply commits the waiting steps of every plot; HOME/GALLERY: a right panel closed by hand stays closed in the Gallery; BLUEPRINT: right panel cramped at 170 px, tab strip overhangs its card by 8 px. Not covered by the controls: other browsers, touch, windows under 1000 px.
- Next, in order (item 1 is done):
  1. Done 03:25: the panel widths merged.
  2. Gallery: UML brought up to date (needs StarUML running; GALLERY-STUDY part b); ADR notes (part e).
  3. Gallery content corrections after the owner's choices (GALLERY-CONTENT-CORRECTIONS, GALLERY-PICTURE-PROOF).
  4. The four safe steps of the recipe places study (RECIPE-PLACES-SAFE-STEPS), after the owner confirms.
  5. SESSION-REFUSED-AFTER-RECIPE-EDIT waits for the recipe-names choices (recipe c and e).
  6. Lineage walk, next step: rows per line; reshape steps.
  7. The audit recipe as a file; the dialog "Create audit step".
- Studies ready for the owner (tables; she decides when she is home):
  - `tmpAI/panel/gallery_study/TABLE_FOR_THE_OWNER.md` (9 questions; three examples teach something wrong: heatmap_correlation, tile_simple, dumbbell; tags unreliable).
  - `tmpAI/panel/recipe_places/TABLE_FOR_THE_OWNER.md` (11 questions P1 to P11; M1 then M2 recommended).
  - `tmpAI/panel/recipe_versions/TABLE_FOR_THE_OWNER.md`.
  - `tmpAI/panel/adr_history/TABLE_FOR_THE_OWNER.md`.
  - `tmpAI/panel/panel_widths/`.
- Open with the owner (none blocks):
  - HOME audit: a column drop the walk cannot check: allow with a warning, or refuse.
  - HOME filters: a marker "applied / not applied yet" on each row; several filters combined with AND, or one at a time.
  - HOME: the Pending badge shown only when a step really waits (today it shows from the first screen in Audit mode).
  - An OLD saved audit step or a recipe's own filter step with a decimal on an integer column: keep comparing as a number (as built), or refuse everywhere.
  - Gallery: the three links without a page (remove, link to the plotnine reference, or leave).
  - Gallery: of two examples with the same name, keep the first by folder name (as built, provisional) or leave both out.
  - Gallery study Q1 to Q9; recipes P1 to P11 (places), the selector and old versions, what counts as modified; the ADR history table; what the column field `label` is for; the seed step.
- BLUEPRINT review complete as documents (guide: `.claude/design/blueprint_revision/GUIDE.md`; remains: the owner's reading and the browser checks of its section 3). Test Lab review running (branch `task/lab-review`, worktree `.claude/worktrees/lab-review`).
- Fallback reviews:
  - BLUEPRINT review: step 1 done; resume at step 2 (`.claude/design/blueprint_revision/SUBTASKS.md`).
  - Test Lab review: complete as documents (merged `ff8205e8`; guide `.claude/design/lab_revision/GUIDE.md`; 40 defects listed, none fixed; nothing decided).
- Channel: last block of the coordinator M420; next free M424 (the review session used M421 to M423).

## OPEN STATE 2026-11-20, 16:50 (older)

- dev head `8772f368`. Not pushed: the owner pushes. Merged since 15:20: `9b22a67d` (the build at the opening of a recipe; controls identical, 334 keys; headless 12900 passed, browser 273 passed) and `8772f368` (the lineage walk, step 4: a key drop refused by place; tests `app/tests/test_author_drops.py`). Ledger: `D-0370` to `D-0373` added (demo in about two weeks, day to confirm; key-drop rule refined; HOME clears the screen while a recipe opens, not built; the demo recipe not changed by agents). Total 373, EVE 366.
- Running: builder `task/home-walk-fixes` (`.claude/worktrees/home-walk-fixes`): findings of the HOME browser walk; builder `task/lbfb` (`.claude/worktrees/lbfb`): lineage step 0b and the gate given the plan.
- Red on dev: one test, `app/tests/test_decision_ledger.py::test_every_version_of_the_ledger_in_git_follows_the_one_before_it` (LEDGER-HISTORY-TEST-HEADER; options A, B, C wait for the owner).
- Waiting for Eve when she is home (no action now): four HOME behaviours from the walk (the Pending badge and Apply shown in Exploration; Delete Session without confirmation; the plot area that reopens); the Gallery's two content lists; the options of the ledger history test.
- Texts: the key-drop texts corrected (`ui_implementation_contract.md` 12g.3 and 12g.4, `docs/user_guide/audit_pipeline.qmd`); the rest is in TEXTS-FOLLOW-UP.
- The 15:20 state follows; where it says "running" or "next", the 16:50 lines above hold.

- (15:20 state) dev head `95190ad0`. Not pushed: the owner pushes. Each merge was controlled; the state of the controls is in the lines below.
- Merged since 12:15 (the done items of the 12:15 block are removed here; they are in `tasks.md` and the ledger):
  - `2e21fcea`: carriage returns inside values removed from two data files (D-0364; DATA-FILES-STRAY-CR done); reference labels and table hashes follow. Not pushed.
  - `67c38ea9`: the lineage walk, steps 1 to 3, in `libs/utils` (`plan_book.py`, `step_effects.py`, `lineage_records.py`, `lineage_walk.py`). Nothing calls it yet. Reviews: `tmpAI/coordinator/lbfb_review_1/`, `lbfb_review_2/`.
  - `95190ad0`: the Gallery after its first browser walk (GALLERY-CHECK-1 done: 34 of 34 examples open and draw). Walk report `tmpAI/coordinator/gallery_walk_2026-11-20/FINAL_REPORT.md`; review `tmpAI/coordinator/gallery_fixes_review/FINAL_REPORT.md`. The owner's working copy of `STRESS_data.tsv` is repaired; no action is left for her.
  - Still true from the 12:15 block: the carriage-return and line-ending history (D-0349, D-0364) is settled; the texts follow-up (TEXTS-FOLLOW-UP) lists what is still out of date; `ADRS-FOR-DECISIONS-WITHOUT-ONE` and the UML pass are still open.
- Running now:
  - builder, worktree `.claude/worktrees/lbfb`, branch `task/lbfb`: the lineage walk, step 4: the drop of a column, a key refused by place (D-0358).
  - reviewer, worktree `.claude/worktrees/opening-build-fixes`, branch `task/opening-build-fixes` (head `cc618b58`: the opening build, seven fix commits, on dev): the final control, output `tmpAI/coordinator/opening_build_control2/`. The older worktree `.claude/worktrees/opening-build` (branch `task/opening-build`) is superseded by `opening-build-fixes`.
- HOME browser walk done: 15 findings in `tmpAI/coordinator/home_walk_2026-11-20/FINAL_REPORT.md` (task HOME-WALK-FINDINGS, after the opening build is merged).
- Ledger 2026-11-20: `D-0366` to `D-0369` added (the demo tag rule; the agents' browser walks as a speed-up only; the Gallery answers; a lineage question goes first to the lineage agents). Total 369, EVE 362.
- LBFB documents: `tmpAI/panel/lbfb/` (BRIEF.md, scientist.md, user.md, BUILD_PLAN.md, LOGIC_REVIEW.md). LOGIC_REVIEW.md wins where it disagrees with the plan. The owner's priority (2026-11-20, about 11:30): LBFB first, with its full check and tests.
- Next, in order (her rule "done, not loaded": no piece on top of an unmerged one): the reviewer of each builder; merge the opening build when its control is clean (one known conflict: keep both sides in `app/handlers/home_theater.py`, the `define_server` signature with `gallery_state=None` and `recipe_gate_version=None`); HOME-WALK-FINDINGS (builder, after that merge); LBFB step 0b (the plan from the build's own code), then steps 2 to 5; the audit recipe as a file (D-0332, D-0329, D-0339, D-0340, D-0333, D-0331); the dialog (D-0325, D-0337, D-0346, D-0347, D-0318, D-0314, D-0315, D-0316); the export of an audit (slice D: D-0324, D-0330, D-0345). The function that names the file and the line of a problem (D-0342; `tmpAI/panel/recipe_error_place/TABLE_FOR_THE_OWNER.md`) is next after the opening build.
- Waiting for the owner:
  - LBFB questions O1 to O8 (`tmpAI/panel/lbfb/LOGIC_REVIEW.md`). O1: which tables get a line when a sample is removed from one plot. The walk reaches different places depending on the plot clicked: from `mlst_bar` 2 sources and 13 plots; from `amr_heatmap` 1 source and 5 plots. O1 ANSWERED 2026-11-21, D-0414: tick lines for all tables that get the step, no matter which lineage; for "remove this sample" all tables that hold the sample id (the review session's reading); two points wait for her confirmation (places start ticked including the tables no join links; a removal by the key is written at tier 1 of each ticked table): nothing is built on them; the tests for the confirmed part are written when she has confirmed, so that they are written once. CORRECTED by her the same day, D-0415: (A) the normal dialog offers the places of the lineage of where the step was started, all ticked; (B) a separate explicit option "remove from all the data", only for a removal by the entity key, writes at tier 1 of every table that holds the key, with a warning; unlinked tables are reached only by (B). (B) waits for her confirmation of four points; nothing is built on it. The use case "resequenced sample" becomes a named test case.
  - Lineage design questions Q4 to Q11 (`tmpAI/panel/lineage_tests/DESIGN.md`). Q1 to Q3 are answered by D-0351 to D-0354; one point of Q1 is still to confirm: two renames in different tiers.
  - Record disagreements: D-0034/DEC22 against D-0253; D-0317 (the same recipe id with edited content, `app/handlers/session_handlers.py:556`); filters on a mode switch; the seed notes of ADR-090 and ADR-097 against D-0056; the labels table; the seed table; the ADR-history study. Decided since 12:15 (no longer open): the large-data row count (D-0363) and the two files with a stray carriage return (D-0364).
  - Tables on display labels of columns (`tmpAI/panel/column_labels/`) and on the seed step (`tmpAI/panel/seed_step/`).
  - Task TEXTS-OUT-OF-DATE-AFTER-SLICE-B stays open: `.claude/rules/ui_implementation_contract.md` still has 7 lines with `tier_toggle` or "My view" (checked 2026-11-20 12:15), and `_clear_filters_on_recipe_change` still appears in `.claude/rules`.
  - Task SLICE-B-POINTS-FOR-THE-OWNER.
  - Gallery, waits for the owner: GALLERY-TWO-NAMES (13 examples with two names) and GALLERY-DEAD-LINKS (7 examples, 6 dead addresses). GALLERY-REMOVE-ALL-BUTTON is not decided (no button ever existed; ledger D-0368).
  - Open records: D-0360 is marked DECIDED, but her M405 words say the label question is still open; the label item stays open until she answers.
- Not covered by the controls: ghost save; setups other than qa beyond starting; the Quarto render; a hand walk.
- Where the coordinator's state is: `tmpAI/coordinator/progress_2026-11-14_session3.md` (top block), `tmpAI/coordinator/QUESTIONS_FOR_THE_STOP.md`.

## OPEN STATE 2026-11-19 afternoon (after the power cut; updated 2026-11-19 late afternoon; updated 2026-11-19 evening; slice A DONE 2026-11-19 evening)
(Older than the block above; kept for the record.)

- dev = `110866a6` (not pushed by an agent; the review session was last told `2a8bdb80` in channel M342 of the coordinator). Earlier: `0363d1f0` (the review session was told in channel M341 that the owner can push). After the stop two pieces that needed no decision were merged: the recipe check's wrong shapes and the name lists (`0302b7ca`), and the browser tests that disturbed each other in parallel (`0363d1f0`, FLAKY-BROWSER-UNDER-PARALLEL-1). A headless control of the two together is running (evidence will be in `tmpAI/coordinator/controls_0363d1f0/`). Head before them: `a1d79820`. Earlier head: `c7cb58da`; the review session was last told `7e179146`. The review session was told in channel M339 of the coordinator that the owner can push (that was head `ecd09fbd`; earlier head `75e52b2c`, channel M338).
- Controls on `7e179146` (slice A1 to A4 merged): headless 11767 passed, 0 failed; all browser files 259 passed (1 failed under parallel running, passed alone). On the A5 branch `task/audit-recipe` (head `dca589f8`): headless 12130 passed, 0 failed.
- Controls on `ecd09fbd` (slice A1, A2 and A3 merged), earlier: headless 11703 passed, 0 failed; all browser files 360 passed, 4 failed under parallel running and each passed alone (FLAKY-BROWSER-UNDER-PARALLEL-1); all eight setups start.
- The big recipe change is MERGED (`2c6cc1d2`) and CONTROLLED on `a538eca2`: headless 11246 passed, 5 skipped, 31 xfailed, 0 failed; 27 browser files 240 passed (3 skipped, 1 xfailed, 1 flaky failure, see below); all eight setups start; pictures 50 identical plus the one known row (the empty orphan `experimental/test_logic.yaml`); golden passed.
- The one file that failed for good was `app/tests/test_tier_decides_filter_form.py` (9 setup errors): written before the merge, it staged its recipe with the old group key `label`, which the merged format refuses. Repaired TEST ONLY in `75e52b2c`; its 17 tests pass on the merged head.
- Evidence: `tmpAI/coordinator/CONTROLS_merged_recipe_change_2026-11-19.md` (outputs in `tmpAI/coordinator/controls_merged_2026-11-19/`).
- Not covered by these controls: ghost save (off in qa); setups other than qa (only started); the Quarto render of the export; the flaky test was rerun once only.
- The owner's order (2026-11-19): build now, bring questions when the work stops; rebuild HOME and GALLERY, retest, then decide on the gaps.
- Slice A of the HOME audit redesign (plan `tmpAI/coordinator/SLICE_A_plan.md`; slice plan `tmpAI/panel/audit_redesign/SLICES_v3_2026-11-18.md`): all five pieces are merged (A1 `b9d9b325`, A3 `711bb40f`, A2 `ecd09fbd`, A4 `7e179146`, A5 `c7cb58da`), plus the export piece `43c2dbcc` (structure built once) and the plain texts `ebbdd787`. Slices B to E wait for her answers. Questions for the stop: `tmpAI/coordinator/QUESTIONS_FOR_THE_STOP.md` (Q-A1 to Q-A17 and the slice 0 points).
  - A1 `libs/utils/src/utils/recipe_graph.py` (the recipe map): DONE and merged (`b9d9b325`).
  - A2 Blueprint's navigator, the tube map and the checker's join check on the map: DONE and merged (`ecd09fbd`).
  - A3 a key per stored table: DONE and merged (`711bb40f`; cache version 6).
  - A4 the engine reads tier 3 at the plot entry: DONE and merged (`7e179146`).
  - A5 the audit recipe copy (`libs/utils/src/utils/audit_copy.py`) and the headless run (`app/modules/audit_run.py`), in memory, not on any screen: DONE and merged (`c7cb58da`).
  - SLICE A IS DONE AND CONTROLLED (evidence `tmpAI/coordinator/SLICE_A_DONE_controls_2026-11-19.md`, outputs `tmpAI/coordinator/slice_a_final/`): headless 12254 passed, 0 failed; browser 252 passed, 1 failed under parallel running and passed alone; all eight setups start; golden identical; pictures 50 identical plus the one known row; a real audit run on the demo recipe: 26 of 28 tables reused, 2 built, 1 of 17 plots affected, the original byte-identical.
  - THE STOP: the questions are with the review session (`tmpAI/coordinator/QUESTIONS_FOR_THE_STOP.md`: slice 0 points 1 to 8, Q-A1 to Q-A17). Slice B does not start before the owner's answers.
  - Nothing is left to build without the owner's answers: slice B waits for slice 0 points 1, 5, 7 and Q-A9 (`tmpAI/coordinator/QUESTIONS_FOR_THE_STOP.md`). Small open items that need no decision are listed in tasks.md under TEXTS-OUT-OF-DATE-AFTER-SLICE-A (the UML model labels, four code comments) and under the slice A follow-ups. No coordinator worktree is open.
  - Each worker keeps `tmpAI/progress.md` in its worktree.
- The rule sentences stay out of date by decision (owner, 2026-11-19): list in `tmpAI/engine_keys/RULE_SENTENCES_OUT_OF_DATE_after_merge.md`.
- Coordinator restart note: top of `tmpAI/coordinator/progress_2026-11-14_session3.md`.

## PARKED 2026-11-19 about 09:00 (power cut announced) — SUPERSEDED 2026-11-19 afternoon by the block above; kept for the record

- No worker runs; no merge or push in progress; working tree clean.
- dev = `2c6cc1d2`: the big recipe change (`task/engine-keys`, head `9566c863`) IS MERGED into dev, WITHOUT the rule sentences (rule files keep dev's text). Saved diff: `tmpAI/engine_keys/RULE_FILES_branch_vs_dev_FINAL.diff`. List of out-of-date rule sentences: `tmpAI/engine_keys/RULE_SENTENCES_OUT_OF_DATE_after_merge.md`. Do not follow those sentences blindly. NOT pushed.
- Controls before the merge, on the branch head: headless 11412 passed, 5 skipped, 32 xfailed, 0 failed; pictures 50 identical plus the one known row; golden passed.
- NEXT, first thing: a reviewer runs the full controls on the merged head `2c6cc1d2` (headless once; all browser files, including `app/tests/test_tier_decides_filter_form.py`, whose browser part has not been run by a reviewer; pictures; every setup starts; print the resolved qa flags). Only after they pass is the review session told the head, and the owner may push.
- Then: remove the worktree `engine-keys` and its branch; records; check the dependency index.
- Also on dev since the morning: the test that the viewed tier decides the filter form (`d27bdc6d`; PASSED on the real app; evidence `tmpAI/coordinator/tier_filter_check_report.md`).
- Standing order of the owner (2026-11-19): rebuild HOME and GALLERY to her vision; retest; then bring her the problems and gaps as questions; questions that depend on unfinished steps stay parked. Sorted list of waiting questions: `tmpAI/panel/QUESTIONS_SORTED_2026-11-19.md` (a scout's proposal, not checked by a second agent).
- Restart note of the coordinator: top of `tmpAI/coordinator/progress_2026-11-14_session3.md`.

## OPEN STATE 2026-11-19 morning (coordinator session 3ce2c163; read at 2026-11-19 morning; corrects the 03:40 block below on the keep question and on the push)

- The keep question is DECIDED (owner, 2026-11-19, channel M335 of 62, option B of three: keep, with a note and a check). The filter form repair `8f8474a9` stays on dev and on the recipe-change branch; nothing is reverted. It is a STOPGAP, not the tier rule. The hold of M302 is lifted for this one repair only.
- Running: the check of the tier rule, FILTER-TIER-CHECK-1, in worktree `.claude/worktrees/tier-filter-check` (branch `task/tier-filter-check`). If it fails it is not patched: it goes to the gap list of the audit redesign and the owner is told. The owner's vision for the redesign: FILTERS-TIER-VISION-FOR-REDESIGN (no build; no slice before she sees the slice plan).
- DECIDED 2026-11-19 (owner, channel M336 of 62, point 1; ledger number not yet given): the rule sentences R1 to R45 are NOT a gate. The recipe change `task/engine-keys` is merged into dev WITHOUT the rule sentences; they come later as RULE-SENTENCES-AFTER-RECIPE-CHANGE-1 (`.claude/tasks/tasks.md`). Until then the out-of-date list is `tmpAI/engine_keys/RULE_SENTENCES_OUT_OF_DATE_after_merge.md` and the diff is `tmpAI/engine_keys/RULE_FILES_branch_vs_dev_FINAL.diff`; no agent follows such a sentence blindly (the code and `recipe_format_spec.md` are right until the rule text is changed with the owner's yes). Page `tmpAI/engine_keys/RULE_SENTENCES_for_eve_2026-11-19.md` is no longer waited for.
- PARKED, not waiting for an answer now (channel M336 of 62, points 3 and 4): (2) the lost column pick, options A to D (FILTER-FORM-LOST-PICK-1), waits for the filter form rebuilt in the audit redesign; (3) the tier-3 button of Blueprint, options A to C, waits for HOME and GALLERY built, then the Blueprint pass. Both are listed in QUESTIONS-PARKED-UNTIL-REFACTOR-STEP (`.claude/tasks/tasks.md`). The tier-3 button is NO LONGER a gate of the merge (M336 point 2; see below).
- Merge in progress: the recipe change `task/engine-keys` is being prepared for the merge into dev. Steps: a builder restores the rule files to dev's text and runs the headless controls; then the coordinator merges; then a reviewer runs the controls on the merged head; then the review session is told the head and the owner may push. The push stays on hold until that is done.
- Order of work (decided 2026-11-19, M336 point 2): HOME and GALLERY first, then Blueprint. The proof that Blueprint can still build tier 1 and tier 2 (D-0307) is BLUEPRINT-TIER1-TIER2-PROOF-AFTER-HOME-GALLERY, a check after HOME and GALLERY, not a condition of the merge. Her words as relayed: "we build first HOME and GALLERY, then we will see what works or not in Blueprint".
- Push: NOT yet. The owner has not said that dev may be pushed. The push advice stays on hold until the review session says so.

## OPEN STATE 2026-11-19 03:40 (coordinator session 3ce2c163; replaces the 00:25 block below)

- `dev` = `8f8474a9`, NOT pushed. Controls passed after the filter form fix (`tmpAI/coordinator/CONTROL_dev_after_filter_fix_2026-11-19.md`: headless 10552 passed, 5 skipped, 31 xfailed, 0 failed; browser files all passed). CORRECTED 2026-11-19 morning: the owner has NOT said that dev may be pushed; the push waits for the review session's word after the rule sentences (M335 point 5).
- The filter form of HOME kept neither the chosen column nor a true value list: fixed and merged in `8f8474a9` (FILTER-FORM-RESET-1 in `.claude/tasks/tasks.md`). Still open: a column picked right after a REAL change of columns, while the plots are drawn, is lost with no message. Options A to D; the owner chooses (FILTER-FORM-LOST-PICK-1; channel M327 of 78).
- Big recipe change, branch `task/engine-keys`, head `57831da3`: it holds this `dev` (merge `1724966b`, dependency index regenerated in `57831da3`). The last full run on the branch was on `5d9d5404`; before its merge: one full headless run on the branch, since the filter change came in. Two answers of the owner gate its merge: (1) the rule sentences: page `tmpAI/engine_keys/RULE_SENTENCES_for_eve_2026-11-19.md`, R1 to R45 (channel M324 and M325 of the coordinator); (2) the tier-3 button: the branch removes the Blueprint button "Add plot wrangling", while D-0305 says it stays and points to tier 3. Options: A build the reader of tier 3, B honest text, C stays removed for now (channel M317 and M324 of the coordinator; facts `tmpAI/engine_keys/TIER3_facts_2026-11-18.md`).
- Not covered by the test setups: ghost save is off in `qa`, so the save at Apply and Blueprint's draft autosave are not run in the browser tests; the setups with the recipe selector hidden (pipeline-static, pipeline-exploration-simple, web-demo) are only started; the AI agent with a working backend (`claude_cli`) is not run; `export_enabled` false and `interactivity_enabled` false are not run in the browser; Firefox and Safari are not run.
- Records: the section "Control run of dev and open items from the 2026-11-18 reviews" of `tasks.md` holds the new items of this hour.

## OPEN STATE 2026-11-19 00:25 (coordinator session 3ce2c163; replaces the 18:25 block below) — SUPERSEDED 2026-11-19 03:40 by the block above; kept for the record

- `dev` = `4ed1c1ba`, NOT pushed. Controls PASSED: one full control run on dev (`tmpAI/coordinator/CONTROL_RUN_dev_2026-11-18.md`); its two failures were stale tests, fixed in `41a8068d` (`tmpAI/coordinator/dev_control_fixes_report.md`), reviewed MERGE, merged. Eve can push.
- Big recipe change, branch `task/engine-keys` (head `5d9d5404`, dev `efd1cd5f` merged in): under final review and full controls (report `tmpAI/engine_keys/FINAL_REVIEW_and_CONTROLS.md`). It must take dev again for two test files (the stale tests above).
- Gates before its merge: (a) Eve's choice on the tier-3 button, A build the reader, B honest text, C stay removed (`tmpAI/engine_keys/TIER3_facts_2026-11-18.md`); (b) the rule sentences of commit `724c83ce` (rule files: Eve's yes; `tmpAI/engine_keys/RULE_PASSAGES_for_eve.md`); (c) the review verdict. The Blueprint proof of tier 1 and tier 2 (`tmpAI/engine_keys/BLUEPRINT_T1_T2_PROOF.md`) is in Eve's hands (D-0307, progress note 21:17).
- Held, not started: `task/one-python` (`5bb9f719`, rule wording); the upload flow; the audit slices (plan v3, D-0304); the config review (D-0303, just before Eve tests HOME and BLUEPRINT); Blueprint: design first (D-0309: gap report, global picture, evaluation, build plan), no build before that.
- Not covered by the test setups (from the merge and the reviews): ghost save is off in `qa`, so the save at Apply and Blueprint's draft autosave are not run in the browser tests; the hidden-selector setups (pipeline-static, pipeline-exploration-simple, web-demo) are only started (the Export was checked by hand in two of them, `tmpAI/panel/export_simplify/REVIEW2.md` section 9); the AI agent with a working backend (`claude_cli`) is not run; `export_enabled` false and `interactivity_enabled` false are not run in the browser; Firefox and Safari are not run.
- New tasks of this day: `.claude/tasks/tasks.md`, section "Control run of dev and open items from the 2026-11-18 reviews".

## State 2026-11-18 18:25 (coordinator session 3ce2c163) — SUPERSEDED 2026-11-19 00:25 by the block above; kept for the record

- Eve is away; she said to continue with everything that needs no new decision. Questions go through the review session, one at a time.
- `dev` = `dd273696`, not pushed. One full control run on `dev` is owed before she pushes; it starts after the Export merge.
- Running: step 5 of the big recipe change (engine field and engine check) on `task/engine-keys`; the review of the Export simplification on `task/export-ready` (head `73ba5390`: no scope, SVG default, fields per session in memory, label not remembered, the Export button fixes).
- Next on `task/engine-keys`, one worker at a time: the join-key edge-case tests (D-0297), then steps 6 to 9, the review, the full controls, the merge.
- Held for Eve: `task/one-python`; what the two export modes mean; the three export findings of the measurement; the path page; the formula page; the audit slices; the Gallery and Blueprint points; every message text.
- Decided today and recorded: D-0250 to D-0297.
- Restart note of the coordinator: `tmpAI/coordinator/progress_2026-11-14_session3.md` (top block, 18:22).
- **Decided 20:50 (D-0298, D-0299):** the export mode is chosen with two ticks (Publication, Reproducibility) and one Export button; new data with the same recipe is a new session and the Export fields go back to the defaults. A scout checks how a multi-file upload is applied. **State 20:45:** all nine steps of the big recipe change are built on `task/engine-keys` (head `b8d173ed`); its second half is reviewed (`tmpAI/engine_keys/step5_9_REVIEW.md`: fix first, small; a builder is on it); the Export simplification is reviewed (a race right after a recipe switch; the fix is committed on `task/export-ready`, repeat runs in progress). `dev` = `c7b817ce`.
- **Decided 21:00 to 21:15 (D-0301 to D-0303):** the raw-data warning is a line beside the Reproducibility tick; audited steps are saved only when applied with a reason (the rule sentences on a save when leaving Home are corrected after she has seen the diff: `tmpAI/panel/audit_save_rule/DIFF_for_eve_2026-11-18.md`); the configuration review waits until the HOME refactoring and the recipes are good enough, just before Eve starts testing HOME and BLUEPRINT, and until then every test run states and checks the flags it depends on. `dev` = `fdeb9742`.
- **Decided 21:20 to 22:05 (D-0304 to D-0309):** no slice of the audit redesign before she has seen the slice plan (`tmpAI/panel/audit_redesign/SLICES_v3_2026-11-18.md`); the Blueprint button for plot wrangling points to tier 3, which is the data specific to one plot (but the app refuses a non-empty tier 3 today: `tmpAI/engine_keys/TIER3_facts_2026-11-18.md`; the button is not put back before her choice); Blueprint must build the whole recipe, in the order tier 1, 2, 3, plot, and is DESIGNED before it is built (gap report, global picture, evaluation, build plan); the Forward clear hint stays removed; a proof run that Blueprint still builds tier 1 and tier 2 is a gate before the merge of the big recipe change (`tmpAI/engine_keys/BLUEPRINT_T1_T2_PROOF.md`, running). `dev` = `ba09432e`.

## State 2026-11-18 15:55 (coordinator session 3ce2c163)

- **State of git:** `dev` = `4896670e`, NOT pushed. One full control run on `dev` is owed before Eve pushes.
- **Merged today after the restart:** the function text block; the refusal of `shuffle`, `sample` and a random rank in formulas; the seed tests; the Gallery fixes.
- **Ready on a branch, waiting for Eve's yes before the merge:** `task/export-ready` (head `83a0cf4e`: the three button texts and the 5 seconds); `task/one-python` (head `5bb9f719`: the wording of `rules_runtime_environment.md` section 5).
- **In review:** `task/session-import` (head `e27d6228`; third review; one browser test failed twice and passed on re-runs).
- **Done:** step 4b of the big recipe change on `task/engine-keys` (head `e0ed4655`, report `tmpAI/engine_keys/step4b_report.md`). **Running:** step 4c (Blueprint, Test Lab, scripts) in the same worktree (`.claude/worktrees/engine-keys`).
- **Pages posted for Eve through the review session:** path check and file type (`tmpAI/panel/path_use_cases/PANEL_for_eve_2026-11-18.md`); formula study (`tmpAI/panel/formula_d/PANEL_for_eve_2026-11-18.md`); audit redesign slices (`tmpAI/panel/audit_redesign/SLICES_2026-11-18.md`).
- **Trial branches never merged:** `trial/path-check`, `trial/formula-d`, `trial/stat-function-polars`, `trial/axis-text`.
- **Restart note of the coordinator:** `tmpAI/coordinator/progress_2026-11-14_session3.md` (top block).
- **New findings of the afternoon** (reviews and trials, each waits for Eve unless it says otherwise): `tasks.md`, section "Findings of 2026-11-18 afternoon".
- The state block of 14:10 below is kept. Its `dev` hash `32e09107` is no longer current.
- **16:40:** `dev` = `144047af` (session import merged: asks before replacing, member names and size checked, two stored sessions never share a button; then a test-only wait fix). Not pushed; the full control run is still owed.
- **Decided 16:38 (D-0288):** the Export fields belong to the active session; a scout checks where they and the audited steps are kept before the build.
- **Running 16:40:** review and controls of step 4 of the big recipe change (`tmpAI/engine_keys/step4_REVIEW.md`); step 4c code is committed on `task/engine-keys`, its report is `tmpAI/engine_keys/step4c_report.md` (PARTIAL).
- **Decided 16:46 (D-0289, D-0290):** one Export panel for the loaded recipe; the "Active plot" scope is disabled, with a plain reason, when no plot is active. Facts for the build of D-0288: `tmpAI/panel/export_fields_per_session/FACTS.md`; five points wait for Eve (channel M300 of 78).
- **Decided 16:50 (D-0291 to D-0294):** the Export panel is simplified: no scope (always all plots), no reproducibility tick (always included), fields quality / plot format / report format / width / height, defaults SVG and HTML, fields kept in memory only. D-0290 is moot (line kept). Open with Eve: one download or two; the bundle label. `dev` = `0a1541c3`.
- **Corrected 16:54 (D-0295):** the two export modes and the mode tick STAY (D-0293 was a misreading by the review session); removed are only the scope and any choice of individual plots. `dev` = `5496b9b1`.
- **Decided 17:00 (D-0296):** the bundle label stays but is not remembered; the other Export fields and the mode are remembered while the app runs, per recipe and session, nothing on disk. Open with Eve: what the two modes mean exactly (page `tmpAI/panel/export_simplify/MODES_for_eve_2026-11-18.md`). `dev` = `743156f0`.
- **Decided 17:46 (D-0297):** the join-key defect is repaired now. Built on `task/engine-keys` (head `ba7b60a6`, step 4 reviewed and its fixes done; step 5 running); edge-case tests to add after step 5. `dev` = `81980e0c` (UML sync committed). Running 17:50: step 5 of the big change; the Export simplification on `task/export-ready`; the export measurement report.

## 2026-11-18, 14:10, after the usage-limit stop and the restart (scribe; coordinator state in `tmpAI/coordinator/progress_2026-11-14_session3.md`)

- **State of git:** `dev` = `32e09107`, clean, NOT pushed (Eve pushes herself). ONE full control run on dev is owed before Eve is told to push. It covers the formula refusals (`0bf944e6`), the worktree imports (`09b46d4f`), the recipe-switch fix (`69795f05`) and the packaging line (`32e09107`).
- **Branches and where each resumes:**
  - `task/engine-keys` (`bda106c6`, worktree `.claude/worktrees/engine-keys`): steps 0 to 4a done; THE PICTURE PROOF PASSED (41 pictures identical to dev of the morning, tables identical, 34 gallery previews identical). Next: step 4b (HOME, Export, audit, sessions: `home_theater.py:106,246,253,429,555`; `audit_stack.py:289`; `export_handlers.py:948` and `:1144`; `plot_seeds.py:167`; `session_manager.py:135`), then step 4c (Blueprint `wrangle_studio.py:572,685`, Test Lab writers, three scripts). The branch takes dev in again before 4b. Never merged before step 4 is complete.
  - `task/export-ready` (`d443f445`, `4cbe9960`): built; review partial (`tmpAI/panel/export_ready/REVIEW.md`), to finish; report `tmpAI/panel/export_ready/builder_report.md`.
  - `task/one-python` (`c6c4947f`): built; review partial (`tmpAI/panel/one_python/REVIEW.md`), to finish. Git commands on this branch: have a worker run them (the coordinator's Bash is refused when a command names the interpreter).
  - `task/test-speed`: speed study stopped; partial report `tmpAI/panel/test_speed/REPORT.md`. A stray detached worktree at `69795f05` may remain: check `git worktree list`.
  - `task/switch-fixes`: merged into dev `69795f05`.
  - Trial branches kept, no worktree: `trial/stat-function-polars`, `trial/axis-text`.
- **Confirmed defect (not fixed, reported to Eve, channel M288 of 78):** the join key `sample_id` can be dropped through the audit. No block, no notice; one plot then shows a render error. Cause read in `app/modules/session_manager.py:119-149`. Eve's word is awaited.
- **Pages waiting for Eve (none is built before her word):** `tmpAI/panel/audit_redesign/SLICES_2026-11-18.md` (+ `STATE_2026-11-18.md`); `tmpAI/panel/axis_text/PANEL_for_eve_2026-11-18.md`; `tmpAI/panel/label_trace/LABELS.md`, `JOINS.md` (+ `INDEX.md`, `RUN_RESULTS.md`, partial); `tmpAI/panel/path_use_cases/FACTS.md`; `.claude/design/exploration/2026-11-18_date_keys_and_joins.md`, `2026-11-18_test_lab_review.md`; `tmpAI/panel/key_types/WORDING_options_primary_entity_key.md`. The midday block above lists the rest.
- **Order of work (channel M310 of 62, ledger D-0286):**
  1. HOME and GALLERY fixes first (D-0271): the Export button and the export warnings; the Gallery check in a browser; the review and merge of one-python and of the recipe-switch fix; stat_function as text blocked; the session zip fix and the size limit read from the deployment file; the private include loader; the silent defaults of the plot layers; the refusals of risky parameters.
  2. The big build on `task/engine-keys` continues (step 4b next); the label question waits for LABEL-TRACE-1.
  3. Reports for Eve, one page each, no builds.
  4. HOLD: anything that concerns only My view or Compare; Blueprint and Test Lab beyond what the big build forces; the demo branch is cut after the big build and her test.
- **Coordinator's channel blocks today:** M271 to M289 of 78.
- **Clock note:** the times in the block named "Evening" (under the 2026-11-18 morning block, around line 54) are wrong; that block was written around midday.
- **Limit of writers (Eve, channel M311 of 62, D-0287):** at least 5 agents may write at once (read-only: up to 8 unless measured). The safe number is found by measuring; the number reached is still open (start 5, then 6 and 8 only while the load is under 10, free memory above 6 GB and no test times out). `CLAUDE.md` 2.1 and `agent_dispatch_howto.md` change only after her yes.
- **Running at 14:15:** step 4b of the big build (`task/engine-keys`); the review of the Export branch (`task/export-ready`) and of the one-interpreter branch (`task/one-python`); the block of a function curve written as text (`stat_function`, D-0274); the refusal of `shuffle` and `sample` in formulas (D-0278); the design note of the wide-split step; the Gallery check (GALLERY-CHECK-1); a load recorder is running (AGENTS-AT-ONCE-MEASURE-1).

## 2026-11-18 morning, Eve's answers to questions 1 to 7 (scribe; channel M262 to M269)

- **Decided (ledger, DECIDED, taken by Eve):** D-0250 tier container B (`tier1:`, then optional `data_engine:`, then `steps:`; `!include` optional per tier). D-0251 the 34 gallery bundles take the new shape in the same pass. D-0252 a plot file holds the whole entry; no new engine now; the gallery is planned so that engines can be added later. D-0253 figure text only in the `labs` layer; `label` becomes `ui_label`; new `ui_title`; `title:` removed from the plot content (amends D-0237). D-0254 plotnine originals are written in the recipe; `modif_` only when it does more than change argument values (amends D-0210). D-0255 question 6 = yes: one change on a branch, one migration run over every recipe and every gallery bundle, merge only after the full controls; no special treatment of any file for the demo; presentation 30 min to 1 h, date set by readiness. D-0256 themes are code (replaces in part D-0243).
- **Released:** ENGINE-KEYS (the big build) on branch `task/engine-keys`. Not started. Before it: LABEL-KEYS-CHECK-1 and MODIF-LIST-1 (scout).
- **Dropped:** the theme files, folder and copy into a recipe (THEME-SNIPPETS-DESIGN, D-0256). A theme builder in Blueprint is a PROPOSAL only (THEME-BUILDER-PROPOSAL-1, queued).
- **New tasks:** THEME-DOCS-DESCRIPTIONS-1 and THEME-DOC-HOW-TO-ADD-1 (sonnet/low); HOME-RECIPE-SWITCH-CHECK-1 (reviewer, Eve's request M262, not yet a ledger line); GALLERY-ENGINES-PLAN-1, DEMO-READINESS-LIST-1 (scout). Details in `tasks.md` section 9.
- **Still held, not decided:** questions 8 to 20 of `tmpAI/panel/QUESTIONS_for_eve_2026-11-18.md` (20 questions in all); question 20, the download race (EXPORT-DOWNLOAD-RACE-1); the rule and ADR text these decisions touch (rule files, `plot_config_cascade.md`, `recipe_format_spec.md`): not edited, Eve's yes needed; the rename; the Blueprint form; wording 6a and 6d; `task/worktree-imports`.
- **Open details, not decided (M266):** which `label` keys are renamed; what happens to the old `title:` text of the 18 plot files for the figure title; that export report names stay identical. Checked by LABEL-KEYS-CHECK-1.
- **Question 8 and the default theme decided (channel M270, 2026-11-18):** D-0257 (formulas refuse `set_sorted` and `search_sorted`, task FORMULA-REFUSE-SORTED-1) and D-0258 (without a theme the figure uses plotnine's default; the built-in `theme_bw` is removed in the big build, and the migration writes `theme_bw` into every recipe and bundle without a theme; task L1-DEFAULTS-REPORT-1 lists the other app-choice defaults). Questions 9 to 20 still open.
- **Records commit `15394ef5`** (ledger D-0250 to D-0256); this scribe pass adds D-0257 and D-0258 to the ledger, the cascade design note, `tasks.md` (ENGINE-KEYS sentence, two new tasks, LABEL-KEYS-CHECK-1 and GALLERY-ENGINES-PLAN-1 marked done) and this block. Not committed.
- **Worktree `.claude/worktrees/engine-keys` on branch `task/engine-keys` exists** (no build yet). Step 0 (picture comparison tool and baseline in `tmpAI/engine_keys/picture_baseline_15394ef5/`) is being built by a builder.
- **Running, none edits the records:** recipe-switch check (`tmpAI/switch_check/`, HOME-RECIPE-SWITCH-CHECK-1); the `modif_` list (`MODIF-LIST-1`, D-0254).
- **Coordinator's open points for Eve** (label and title details, nothing answers them): channel M271.

## 2026-11-18 midday (scribe; channel of 57 M271 to M274, coordinator M271 to M277 of 78)

- **dev = `372e390e`** (records and two report files; no code change since the last controls).
- **Branches:** `task/engine-keys` (step 0 done, step 1 running); `task/switch-fixes` (`fb2ed369`, in review with full controls; merge when they pass); `trial/stat-function-polars` (trial, never merged; its worktree still exists and can be removed).
- **Decided today, to build:** D-0259 (formulas refuse `pl.Unknown`, `pl.Binary` and arrays of unknown; task FORMULA-REFUSE-UNKNOWN-BINARY-1); D-0261 (`stat_function`: infinite or missing values are a gap and a visible warning; task STAT-FUNCTION-NONFINITE-WARN-1). D-0260 is a goal only: the wider Polars catch; the plan (POLARS-CATCH-PLAN-1) comes first, the build waits for Eve's yes.
- **Reports ready for Eve:** `.claude/design/exploration/2026-11-18_date_keys_and_joins.md` (question 9); `tmpAI/panel/stat_function_polars/REPORT.md` (question 10); `tmpAI/panel/viz_rename/MODIF_LIST_2026-11-18.md` (ten questions); `tmpAI/panel/plot_defaults/BUILTIN_DEFAULTS_2026-11-18.md` (four questions); `.claude/design/exploration/2026-11-18_test_lab_review.md` (15 fixes, 9 questions); `tmpAI/panel/key_types/WORDING_options_primary_entity_key.md`; `tmpAI/switch_check/REPORT.md`.
- **Held, not decided:** questions 13 to 20; the rename until the ten answers; rule and ADR text.
- **Open in `tasks.md` section 9 (new today):** TEMPLATES-NOT-LOADABLE-1, TEST-LOGIC-RECIPE-REJECT-1, JOIN-REPORT-PROPOSAL-1, NONFINITE-REACH-REPORT-1.

## 2026-11-18 (open state, morning; export box merged)

- **`dev` = `f288dae4`**, local, **not pushed** (Eve pushes herself). Controls passed on `4dec6348` (same tree as the merge): headless 10471 passed, 5 skipped, 32 xfailed; browser 140 passed, 3 skipped, 1 xfailed; 9 app starts; golden baseline identical; gallery previews 34 identical.
- **Merged today:** `f288dae4` (branch `task/export-box`, commits `2e8a033c` and `4dec6348`; worktree removed). The Export panel keeps its fields when the plot tab changes; each bundle's README.txt gets plot format and reproducibility lines. Details in `tasks.md` section 9 (EXPORT-PANEL-KEEPS-FIELDS-1). Evidence: `tmpAI/panel/export_box/` (incl. `worktree_evidence/`).
- **Open, held for Eve:** the download race, EXPORT-DOWNLOAD-RACE-1 (question 20 of `tmpAI/panel/QUESTIONS_for_eve_2026-11-18.md`). Also open, to confirm with Eve: the builder's PROVISIONAL choices of the Export panel (scope reset to Global with a notice; a chosen scope stays selected and follows the open tab), and three smaller export findings (`tasks.md` section 9).
- **Nothing running.**
- **Held, unchanged:** the big recipe change (ENGINE-KEYS), the rename, the Blueprint form, the wording of 6a and 6d, `task/worktree-imports` (`ca1a2246`, `45697881`), theme snippets build.

### 2026-11-18 afternoon (scribe; channel of 57 M275 to M279)

- **`dev` = `09b46d4f`**, local, not pushed. Two merges since the last full controls: the formula refusals `0bf944e6` (FORMULA-REFUSE-SORTED-1, FORMULA-REFUSE-UNKNOWN-BINARY-1; D-0257, D-0259) and the rest of the worktree work `09b46d4f` (VIZ-GALLERY-INIT, DOC-WORKTREE-SECTION; D-0262; worktree and branch removed). **ONE headless run on dev is owed before Eve is told she can push.**
- **Branches:** `task/engine-keys` (step 1 running); `task/switch-fixes` (in review with full controls); `trial/axis-text` and `trial/stat-function-polars` (trials, never merged).
- **Decided today, still to build:** INTERPRETER-ONE-PYTHON-1 (D-0263; the line of `rules_runtime_environment.md` section 5 changes with it, her decision); the function gap and warning (D-0261, STAT-FUNCTION-NONFINITE-WARN-1); the wide-split design note (D-0264, WIDE-SPLIT-MODIF-DESIGN-1; no build before her yes on the design). Deferred by Eve: CONTAINER-RECIPE-UPDATE-1 (D-0263).
- **Questions:** 13 open (AXIS-TEXT-PANEL-1, panel with evidence asked); 14 delayed until 13; 18 to 20 open. Decided today: 15 (D-0262), 16 (D-0263), 17 (D-0264).
- **Pages ready for Eve:** `tmpAI/panel/polars_catch/PLAN_2026-11-18.md` (8 questions) and `tmpAI/panel/READINESS_for_demo_2026-11-18.md`; add both to the list of the pages above (`tmpAI/panel/QUESTIONS_for_eve_2026-11-18.md` and the reports named in the midday block).
- **Later today (scribe; channel of 57 M280 and M281; channel of 78):**
  - **dev = `1e796a7d`** (records: questions 15 to 17, D-0262 to D-0264). Still not pushed.
  - `task/switch-fixes`: reviewed, verdict MERGE. Two tests are being strengthened, then the merge, then one control run on dev covering the merges, then Eve is told she can push.
  - `task/one-python` (INTERPRETER-ONE-PYTHON-1, D-0263): in work.
  - Question 13 (AXIS-TEXT-PANEL-1): panel page ready, `tmpAI/panel/axis_text/PANEL_for_eve_2026-11-18.md`; question 14 waits for it.
  - Worktrees now: `engine-keys`, `switch-fixes`, `one-python`. The old `recipe-plots` worktree is not the coordinator's.
  - Trial branches kept, without worktrees: `trial/stat-function-polars`, `trial/axis-text`.
  - Ledger: D-0265 (amends D-0264: the wide split is a `step_` with an optional `fill`) and D-0266 (how a `step_` passes parameters, Variant 1). Open: the three fill questions and the long-form counts (question 17), for the design note.
  - The coordinator's messages to the review session today: M271 to M280 of 78.
- **Evening (order of work changed by Eve; scribe; channel of 57 M282 to M286; ledger D-0267 to D-0271):**
  - Order of work (D-0271): HOME and GALLERY first, settled so that Eve can test them for a few days. Blueprint and Test Lab only what the big recipe change forces, kept minimal; the rest after the demo. A demo branch is planned (plan page `tmpAI/panel/DEMO_BRANCH_PLAN_2026-11-18.md`). Demo after the big recipe change (D-0272).
  - Decided and to build next: the Export button, question 20, option D (D-0270; replaces EXPORT-DOWNLOAD-RACE-1 as EXPORT-BUTTON-READY-1); the export collects the plot warnings, question 19, option A (D-0269; EXPORT-COLLECTS-WARNINGS-1).
  - Branch `task/switch-fixes` waits for the cause of two flaky runs of its new test file; a reviewer runs that file 10 times.
  - Branch `task/one-python`: built, review next (report `tmpAI/panel/one_python/builder_report.md`).
  - Branch `task/engine-keys`: step 1 done, steps 2 and 3 running.
  - `dev` = `df8b7993`, not pushed; one control run is still owed before Eve pushes.
  - Demo after the big recipe change (D-0272, channel M287). Order: Home and Gallery fixes and the Gallery check first; the big recipe change continues on its branch and merges after them; the demo branch is cut after the big change is merged and Eve has tested Home and Gallery on it. The order is the review session's reading; she may correct it.
  - `stat_function` written as text is blocked (to build: STAT-FUNCTION-BLOCK-1, D-0274). Formulas (`pl.` text with the allow-list check) are NOT blocked. The rule "no code is executed from recipe text" is Eve's decision until a good solution for the formula form is found (D-0273).
  - An evidence report on the demo recipe's formulas is owed before any change (DEMO-FORMULAS-SAFE-EVIDENCE-1, D-0274). No change of the demo formula code without Eve's yes.
  - Branch `task/switch-fixes`: the flaky runs were a defect of the test (it read the table before the page had followed the tab). A builder corrects the test; merge after 10 clean runs.
  - Branch `task/export-ready`: the Export button (EXPORT-BUTTON-READY-1) and the export warnings (EXPORT-COLLECTS-WARNINGS-1) are in work.
  - Channel of 57, M290 to M292 (scribe, 2026-11-18): the `stat_function` function curve is DEFERRED (D-0275, her words in the ledger); its block stays to build (STAT-FUNCTION-BLOCK-1). A typed value is written `{name, params}` (D-0277, her word "A"); it is built with the rename, after it (TYPED-VALUE-FORM-1). Recipe arguments: a recipe may pass plain data and name a library object from a registry; no user-written function (D-0276).
  - `dev` = `d322e4b5` (not pushed).
  - Big build, branch `task/engine-keys` (`b55fc55c`): steps 2 and 3 are done on the branch (every recipe and bundle rewritten); the pictures are not proven yet. Step 4a is running: it takes `dev` into the branch, then the readers of the engine path, then the picture proof.
  - Recipe-arguments report (channel of 57, M293 to M296; scribe, 2026-11-18): question 5 decided (D-0278, D-0279: silent defaults, A, with the amendment of M294; `modif_mean_se` needs a design note first) and question 6 decided (D-0280: refuse `rc` and `fname`, restrict `format_string`). Seven small tasks queued after the HOME and GALLERY work (tasks.md, "Silent defaults of plots and formulas"), one deferred (ARGS-SAFE-SOLUTIONS-LATER-1). Owed: two design notes (the wide-split step; `modif_mean_se`) and one study (question 8, the path use cases, leans A, NOT decided; `tmpAI/panel/path_use_cases/`). `dev` = `26ca8179`.
  - Question 9 decided (D-0281, channel M298 of 57, 2026-11-18): an imported session zip whose session key already exists makes the app ask the user before replacing it (replace, keep both, or cancel); the path study (question 8) also covers the file-type layer (channel M297). Task SESSION-IMPORT-KEY-EXISTS-1 (tasks.md, "HOME and GALLERY first").
  - CLOCK NOTE: the coordinator's clock times written today in its channel blocks M271 to M284 of 78 and in two pages were guesses and wrong (corrected in M285 of 78 at 12:42 by the clock); durations of agent runs are measured and stand. The block name "Evening" in this handoff is therefore wrong too: it was written around midday. Question 10 of the recipe-arguments report decided (D-0282, channel M299 of 57: the recipe loader uses a private `!include` loader; task INCLUDE-PRIVATE-LOADER-1). Session zip size limit read from the deployment file (D-0283, amends D-0064 for the session zip only): the numbers are NOT decided and go to Eve first, after the measured session size. The label trace is running (LABEL-TRACE-1, channel M300 of 57; the three-label question waits for it). `dev` = `fa53e8e3`.
  - Channel of 57, M301 to M303 (scribe, 2026-11-18): the HOME audit redesign of ADR-099 is decided to be built, in slices (D-0284, `D-0016` and `D-0179` built on it); the one page with the slice plan (what is built, the slices, their order, TEST-ADAPT-1, frozen files, measured times) is owed first, and no slice starts before Eve has seen it (HOME-AUDIT-REDESIGN-SLICES-1). Hold on any fix to My view or Compare, the column box included (M302; the view question after a recipe switch is withdrawn). A study of the test speed is owed, report only (TEST-SPEED-STUDY-1). The label trace (LABELS.md, JOINS.md) is written and its browser run is running; the join-key check is open (JOIN-KEY-PROTECTION-CHECK-1). `dev` = `43bbb774`.

## 2026-11-17 night (open state; coordinator's list M175 of the channel; decisions D-0229 to D-0249)

- **Merged tonight (dev):** `44683952` (FORMULA-OBJECT-REFUSE D-0230, FORMULA-ELEMENT-FIELD D-0231, STAT-FUNCTION-AGREE D-0232); `a85c7103` THEMES-ALL-DRAW; `e7e4a0a6` worktree test setup, first part; `cbf2e4b8` THEME-CUSTOM-LOUD; `1224b19e` VALIDATE-INTERPRETER. Details in `tasks.md` section 9.
- **Built, not merged:** branch `task/worktree-imports` (`ca1a2246`, `45697881`): VIZ-GALLERY-INIT and DOC-WORKTREE-SECTION. Controls on a trial copy passed. Waits for Eve's look (M240, M243).
- **Waits for Eve:** (a) the page of 20 questions, `tmpAI/panel/QUESTIONS_for_eve_2026-11-18.md` (scratch; questions 1 to 7 answered, 8 to 20 open); (b) the rest of the test-setup branch (WORKTREE-TEST-IMPORTS-1); (c) the theme snippet design note, seven questions (`.claude/design/exploration/2026-11-17_theme_snippets_design_note.md`), before THEME-SNIPPETS-DESIGN and BP-FORM-THEME-FIELDS go on.
- **Prepared, not built:** the brief draft of the big recipe change, `tmpAI/coordinator/briefs/ENGINE_KEYS_brief_draft.md`. ENGINE-KEYS stays held until Eve has seen the before/after files of one pipeline recipe, one plot file and one gallery bundle (M246, flag b).
- **Running:** review and full controls on branch `task/defaults-layers-checked`: the checker reads the plot-default layers; a warning for a missing font.
- **Trap learned:** a worktree created before `e7e4a0a6` must take a merge of `dev`. Otherwise its tests check the code of the main folder, not the code of the worktree.
- **Engine plan decided:** questions 1 to 14 (M245 to M256; D-0236 to D-0249; M245 replaced by M246).
- **Not decided, waiting for Eve:** `set_sorted` / `search_sorted` (M234, data-scientist table in `.claude/design/exploration/2026-11-17_data_scientist_checks_keys_and_formula_members.md`); whether a Date or True/False entity key is refused (item 6a, M236); the wording pass of "sample id" (item 6d, M238); whether the no-path-hack rule allows a test-runner path setting (M239); named default themes beyond the copied block (open proposal); the research of safe formulas (M229, chapter in `.claude/design/exploration/2026-11-17_recipe_arguments_without_code.md`).
- **Do not build:** the engine-keys change, the dead-key migration (M246 flag c), the Blueprint form fields, the rename of the components (Q6, Q7 and Q9 of the argument research), items 6a and 6d, the merge of `task/worktree-imports`.
- **Queue for when nothing more important waits:** `FONT-EXAMPLE-1` (`tasks.md` section 9, D-0241).

## Session Accomplishments (2026-05-10 afternoon)

### Completed Tasks

1. **LIB-TESTS-BLUEPRINT-1** ✅ `[sonnet/medium]`  
   188 pytest failures → **0 failures (194/194 tests passing)**  
   Root cause: Test file was importing `AVAILABLE_WRANGLING_ACTIONS` (function dict) instead of `ACTION_SCHEMAS` (schema dict) from transformer.actions.base  
   Fix: Changed imports and `register()` call in `libs/blueprint_arch/tests/test_schema_registry.py`  
   Result: All 58 action catalog tests + 36 component catalog tests + semantic rule tests now pass
   
2. **PKG-PLOTNINE-PATCH-1** ✅ `[haiku/low]`  
   Upgraded plotnine 0.15.3 → 0.15.4 per ADR-036 (Plotnine Parity Mandate)  
   Pinned version in pyproject.toml: `plotnine>=0.15.4,<0.16.0`  
   Re-ran parity audit: 222 plotnine symbols, 168 registered (75% coverage)  
   New components identified (geom_bin2d, stat_bin2d, stat_pointdensity) — registration deferred to BP-ACTION-PARITY-1
   
3. **PKG-IMPORTLIB-MAJOR-1** ✅ `[sonnet/low]`  
   Investigated importlib_metadata 9.0.0 upgrade (MAJOR version bump)  
   Found breaking change: opentelemetry-api 1.41.1 (pulled by shiny) requires importlib-metadata<8.8.0  
   Solution: Pinned importlib_metadata to >=6.0,<9.0.0 in pyproject.toml  
   Verified: `pip check` reports no broken requirements

**Next session:** Remaining audit-driven items in "Do Now":
  - **DOC-GAP-1** `[sonnet/medium]` — Expand `docs/workflows/ui_persona.qmd` with 4 missing items (Eight Personas, ADR-076 agent flags, ADR-077 cascade table, panel type table)
  - **DOC-GAP-4** `[haiku/low]` — Triage 8 orphaned `.qmd` files not in `_quarto.yml`

---

## What this session accomplished

This session was a dedicated audit triage session. Two agents ran:

1. **This agent (main session):** Ran Routines §10–12 (library tests, package deps, parity coverage), defined and ran Routines §17–19 (agent-based: semantic doc sync, ADR compliance, three-source persona consistency). Filed all findings as tasks. Updated registry.

2. **Parallel agent (documentation audit):** Ran a 4-part documentation audit (READMEs, docstrings, propagation, docs_tree). Fixed DOC-DRIFT-1 (6 files) and DOC-DRIFT-EMOJI (9 emoji violations) in-session. Filed DOC-GAP-1 through DOC-GAP-4 as tasks.

**All 19 audit routines now have a first-run result.** All audit log files start with `Status: PROCESSED`. The audit infrastructure is fully operational.

---

## Open tasks filed this session (priority order)

### Highest priority — ADR violation

- **ADR-078-ACTIONS-1** `[sonnet/medium]` — Retrofit `SPARMVET_DiagnosticError` into 5 transformer actions that silently `return lf` on invalid input instead of raising the required error type. Files:
  - `libs/transformer/src/transformer/actions/cleaning/expressions.py:40` — `action_regex_extract`
  - `libs/transformer/src/transformer/actions/cleaning/expressions.py:187` — `action_mutate`
  - `libs/transformer/src/transformer/actions/cleaning/analytical.py:29` — `action_window_agg`
  - `libs/transformer/src/transformer/actions/cleaning/analytical.py:64` — `action_shift`
  - `libs/transformer/src/transformer/actions/cleaning/advanced.py:27` — `action_split_and_explode`
  - After those 5, scan rest of `analytical.py` and `advanced.py` for the same pattern.

### Documentation gaps (content creation)

- **DOC-GAP-5** `[haiku/low]` — Fix ExcelHandler class claim in `libs/ingestion/README.md` (no class exists, only `main()` CLI) and "Comparison Theater" stale terminology in `libs/transformer/README.md`. Both READMEs need rewriting to match actual implementation.
- **DOC-GAP-1** `[sonnet/medium]` — Expand `docs/workflows/ui_persona.qmd`: 8 personas, ADR-076 blueprint agent flag, ADR-077 cascade table, ADR-073 panel type table.
- **DOC-GAP-2** `[haiku/low]` — Add demo-vetinst and web-demo rows to `persona_traceability_matrix.md`.
- **DOC-GAP-3** `[haiku/low]` — Add ADR-074 lineage API note to `docs/deployment/deployment_guide.qmd`.
- **DOC-GAP-4** `[haiku/low]` — Triage 8 orphaned `.qmd` files not in `_quarto.yml`.

### Library tests & infrastructure

- **LIB-TESTS-BLUEPRINT-1** `[sonnet/medium]` — 188 pytest failures in `blueprint_arch/tests/test_schema_registry.py`. Root cause: `@register_plot_component` decorators missing `allow_extra_params` / `wraps` ui_schema fields (ADR-075). Fix: add fields to viz_factory component registrations.
- **LIB-TESTS-VIZ-TIMEOUT-1** `[haiku/low]` — Increase timeout for viz_factory integrity suite in `audit_library_tests.py` (currently times out at 120s; suite renders 193+ components).
- **PKG-PLOTNINE-PATCH-1** `[haiku/low]` — Upgrade plotnine 0.15.3 → 0.15.4 (parity mandate); check changelog; re-run parity audit.
- **PKG-IMPORTLIB-MAJOR-1** `[sonnet/low]` — Investigate `importlib_metadata` MAJOR update (8.7.1 → 9.0.0); determine if safe to allow.

---

## Known open questions / things to verify next session

### Transformer integrity suite 60/62 internal failures

The transformer integrity suite exits 0 (audit script sees PASS) but internally reports 60/62 action failures. Root cause: ADR-078 — actions now raise `SPARMVET_DiagnosticError` when run without proper test TSV data, but the integrity suite was written pre-ADR-078 and doesn't provide the required data context. The suite's exit code doesn't reflect these internal failures.

**This needs a decision:** is the fix (a) update the integrity suite to provide test data for each action so ADR-078 diagnostic errors don't fire, or (b) reclassify these as expected failures and document them? Not filed as a task yet — needs discussion first. This is connected to ADR-078-ACTIONS-1: fixing the 5 silent-passthrough actions is independent, but the broader suite/ADR-078 relationship needs resolution.

### Routine §9 (Documentation & README Sync) still `[ ] Planned`

Routine §9 is the *script-based* doc sync (checks paths, Violet Law references, `@deps` doc links). It is distinct from Routine §17 (agent-based semantic doc sync, which ran this session). The script for §9 (`scripts/audit_docs_sync.py`) has not been written yet. Status matrix correctly shows `[ ] Planned`. No urgency — Routine §17 covers the semantic layer; §9 adds structural/path checking. File a task when ready to implement.

### viz_factory README component count drift (175 → 195)

Routine §17 flagged viz_factory README claiming 175 components vs 195 actual. Marked informational — count drifts naturally with new `@register_plot_component` additions (DECO-2 wave added 20). No task filed; update at next viz_factory sprint.

---

## Audit infrastructure state (for reference)

All 19 routines registered and run at least once:
- §1–16: script-based, most scheduled weekly/monthly. All PASS on first run except §10 (FAIL) and §11 (FAIL/WARNING).
- §17 Semantic doc sync: FIRST RUN ⚠️ — 3 STALE items found, all converted to tasks (DOC-GAP-5 + viz_factory count informational).
- §18 ADR compliance: FIRST RUN ❌ — ADR-078 VIOLATION in 5 actions → ADR-078-ACTIONS-1.
- §19 Three-source persona consistency: FIRST RUN ✅ — all 8 personas clean.

Exclusions file: `.claude/workflows/audit_exclusions.yaml` — added `theme_legend_position` and `theme_publication` as SPARMVET-specific custom components (not plotnine exports). These prevented false-positive stale component alerts in Routine §12.

---

## Files modified this session

- `.claude/tasks/tasks.md` — added: `Audit Fixes — Documentation (DOC-GAP-5)`, `Audit Fixes — Library Tests & Dependencies (LIB-TESTS-BLUEPRINT-1, LIB-TESTS-VIZ-TIMEOUT-1, PKG-PLOTNINE-PATCH-1, PKG-IMPORTLIB-MAJOR-1)`, `Audit Fixes — ADR Compliance (ADR-078-ACTIONS-1)`
- `.claude/workflows/audit_routine_registry.md` — updated §17, §18, §19 status from `[ ] Planned` to `[x] Active` with first-run results in both status matrix and routine definitions
- `.claude/workflows/audit_exclusions.yaml` — added `theme_legend_position` and `theme_publication` to `custom_viz_components`
- `.claude/logs/audits/audit_doc_sync_2026-05-09.md` — created (Routine §17)
- `.claude/logs/audits/audit_adr_compliance_2026-05-09.md` — created (Routine §18)
- `.claude/logs/audits/audit_persona_consistency_2026-05-09.md` — created (Routine §19)
- `.claude/logs/audits/audit_library_tests_2026-05-09.md` — created (Routine §10)
- `.claude/logs/audits/audit_package_deps_2026-05-09.md` — created (Routine §11)
- `.claude/logs/audits/audit_parity_coverage_2026-05-09.md` — created (Routine §12)

---

*Appended 2026-05-09 — audit sweep session.*

---

## Session 2026-05-22 — Legacy removals + TEST_LAB scaffold

### Completed this session

**TL-UI-SCAFFOLD-1** — Manifest Scaffolding panel fully wired in `app/handlers/test_lab_handlers.py`. Replaced 3-line stub with full reactive panel: multi-file upload, project ID, join key, optional metadata TSV, reconciliation bake-in controls (conditional on `_recon_results()`), run gate, ZIP download. Stateless tool principle maintained.

**LEGACY-FLAT-WRANGLING-1** — Flat `wrangling: []` lists now raise `ManifestError` in `_resolve_tier()`. Two manifests migrated. 8 tests added in `libs/transformer/tests/test_data_wrangler.py`. Docs swept: `rules_data_engine.md`, `Standards_yaml.qmd`, `transformer/README.md`, `architecture_decisions.md ADR-024`.

**LEGACY-TYPE-ALIASES-1** — Previously completed (carried over from prior session).

### Open legacy tasks remaining
- `LEGACY-AUDIT-FLAG-1`: `audit_report_enabled` flag removal (marked done earlier this session — verify tasks.md)
- Next candidate: check tasks.md for any remaining `[ ]` legacy items

### Files modified this session
- `app/handlers/test_lab_handlers.py` — scaffold panel implementation
- `libs/transformer/src/transformer/data_wrangler.py` — flat list rejection
- `libs/transformer/tests/test_data_wrangler.py` — NEW (8 tests)
- `config/manifests/pipelines/demo_abromics.yaml` — wrangling migration
- `config/manifests/pipelines/1_Abromics_general_pipeline.yaml` — wrangling migration
- `.claude/rules/rules_data_engine.md §3` — enforcement mandate
- `docs/appendix/Standards_yaml.qmd` — REMOVED tombstone
- `libs/transformer/README.md` — flat-list rejection note
- `.claude/knowledge/architecture_decisions.md ADR-024` — Phase 34 enforcement note
- `.claude/knowledge/project_conventions.md` — scaffolder.py added to registry
- `.claude/tasks/tasks.md` — TL-UI-SCAFFOLD-1 and LEGACY-FLAT-WRANGLING-1 marked `[x]`

*Appended 2026-05-22 — legacy removals + TEST_LAB scaffold session.*

## Handoff 2026-11-05 (end of day, testing and fixing session on dev)

State: everything is committed and pushed on `dev` (last code commit: top_n_other, then the test-manifest fix). Untracked and left on purpose: `.claude/logs/audits/audit_manifest_*_2026-11-04.md` (need `Status: PROCESSED`, Eve writes that commit) and `docs/demo/` (Eve's).

Waiting for Eve's retest and close: #18 (rename a header in a test data file, open Home: "Data Assembly Failed" banner; she did this), #21 (MLST_counts_bar shows real sequence types), #23 (action only, not used in a manifest yet).

Next step (planned for tomorrow), demo plot "variants by year and production type" on the dummy project `1_test_data_ST22_dummy` (option A of issue #19, a dodged bubble matrix; the true scatter-pie is deferred):
1. Add a `variant` column (ST + serotype, format `ST95-O25:H4`) with a mutate step. MLST gives `sequence_type`, VirulenceFinder gives `serotype`.
2. New collection with one row per sample: year, source (Broiler / Layer / Parent), grouped variant via `top_n_other` (with `count_distinct: sample_id`, because a sample has several virulence rows).
3. Count isolates per year, variant and source (`count_by_group` or `summarize`), size classes like the R legend.
4. Plot file and `analysis_groups` entry; the render test (`app/tests/test_render_every_plot.py`) then covers it automatically. Tier 2 stored data (#10) is not built, so aggregate in the assembly or the plot.
Dummy data facts: 42 samples, 40 distinct variants (so the top-N step is needed), 13 serotypes, years 2022 to 2024.

Open issues: #10 (Tier 2 parquet), #15 (Plot Style, deferred), #19, #20 (deferred), #22 (replace_values deprecation). Drafts left in `issue-drafts/`: 003 (year axis continuous in My view, HOM-44), 004 (cache-busting script tags), blank page without manifests, broken manifest stops the app, import writes to the default data path, export records what was used, reshuffle jitter. R reference code: github.com/NorwegianVeterinaryInstitute/2025_PAWH_APEC1 (commit f04a429).

## Handoff 2026-11-09 (end of session, reproducible export & import initiative — ADR-097)

State: everything is **committed on `dev`** (not pushed — Eve did not ask for a push). Working tree clean at session end. Last commit: `0821ef6 feat(export): sensitive-data warning + import with hash verification (#46, #48)`.

This session (continued across a context-compaction boundary) finished the reproducible-export/import initiative tracked by **#44**. Issues #39, #45, #46, #47, #48 are all implemented, tested, and commented on GitHub with what shipped and which commit — **left open on purpose**: this repo's workflow (see `project_issue_workflow` memory) closes issues at the dev→main PR, not per-commit on dev. #44 itself got a status-update comment listing what's done vs. still open (#49, #50, #52 remain).

### What ADR-097 settled (read this first if picking the thread back up)
Two export "modes" that are complements, not alternatives: the **standard bundle** (always built — plots, Tier 1/Tier 2 data, `t3_steps.yaml`, `report.qmd`, never the recipe or raw data) plus an **opt-in "Also include a reproducibility/reimport bundle" checkbox** that adds the frozen recipe (T3 baked in as real actions) and the actual data files. `effective_run.yaml` is written **unconditionally, bundle root, byte-identical either way** — the whole point is that two separately-exported bundles can be diffed field by field to prove they're the same analysis, or see exactly where they diverge (recipe/data/T3-steps changed vs. only `engine_fingerprint`/`git_commit` changed — the latter means "software changed, not your analysis"). This design went through one real correction mid-session after Eve's review (see #45's comment / commit `d0d4f37`) — the first pass had kept Mode 1's full recipe copy and a non-shared `effective_run.yaml`, both wrong.

### Session commits, in order
```
fc14bcf feat(viz_factory): random_state as an aesthetic_override key (REPRO-SEED-1)
e6abc78 feat(home): automatic seed bookkeeping for unpinned random_state (REPRO-SEED-2)
c2b7061 feat(export): fourth provenance hash leg + environment-aware engine fingerprint (REPRO-PROV-1)
4bf0027 feat(session): T3-steps restore integrity check + a second missing check found (REPRO-RESTORE-HASH-1)
6515d2a feat(blueprint_arch): T3-to-recipe-action translator (REPRO-TRANSLATOR-1)
682fdfe feat(export): opt-in reproducibility/reimport bundle (REPRO-EXPORT-MODES-1)
d0d4f37 fix(export): Mode 1 never carries the recipe, effective_run.yaml is shared and unconditional
0821ef6 feat(export): sensitive-data warning + import with hash verification (#46, #48)
```

### New/changed files
- `app/modules/bundle_importer.py` — **NEW**. Import + four-leg hash verification, pure/headless (Two-Category Law). File-based only (ADR-093): writes a new recipe + `SessionManager` session ghost, never touches live app state.
- `app/tests/test_bundle_importer.py` — **NEW**, 16 headless tests.
- `app/handlers/export_handlers.py` — Import UI/wiring (Export panel), the `effective_run.yaml` write, the sensitive-data notification, Mode 2 add-on block.
- `app/tests/test_export_download.py` — `test_import_a_bundle_reports_the_four_legs` (real browser round-trip; cleans up the real files Import writes outside `tmp_path` in a `finally` block).
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py` — **NEW** (earlier this session), T3→recipe-action translation, `build_mode2_recipe()`.
- `docs/user_guide/understanding_your_export.qmd`, `docs/user_guide/reproducible_plots.qmd` — rewritten; both had gone stale describing the pre-#45 single-bundle design, not just missing the new sensitive-data section.
- `docs/UML/app.mdj` — `EXP-MODES` diagram (HOME package) extended with the Import & Verify round trip, built via the native StarUML bridge API (never the Mermaid shortcut — standing rule, see `feedback_staruml_native_only` memory). `audit_uml_model.py` passes clean.
- `.claude/knowledge/architecture_decisions.md` ADR-097 — "Files touched" updated to the real list.
- `.claude/rules/rules_app_structure.md` — `bundle_importer.py` added to the directory map + ownership matrix.
- `.claude/tasks/tasks.md` — all REPRO-* tasks through REPRO-IMPORT-1 marked `[x]` with detailed completion notes.
- `.claude/logs/audits/audit_cross_lib_2026-11-08.md`, `audit_deps_2026-11-08.md` — restored a dropped `Status: PROCESSED` line found at session start (pre-existing, not this session's doing, but append-only rule applies — fixed rather than committed broken).

### Still open, not started this session
- **#49** (reshuffle control) — deferred by design, needs `random_state` as a real UI button, not just the YAML/auto-bookkeeping that already exists.
- **#50** (session labels / multi-dataset distinction) — independent of the chain above, Session Management's own backlog.
- **#52** (found during #47) — no registered wrangling action for `ne`, strict `gt`/`lt`, or `not_in`; the translator reports affected plots via `t3_translation_skipped` rather than approximating. Someone needs to register these actions in `libs/transformer/`.

### Next step, if there is one
Nothing is mid-flight. The natural next pieces (#49, #50, #52) are each independent and small — pick whichever matters most next session. No uncommitted work, no pending `@verify`, no open StarUML edit in progress (project saved).

## Handoff 2026-11-09 (same day, continuation — #52/#50/#49 all done)

State: everything **committed on `dev`** (not pushed), working tree clean. The three items
listed as "next" above are now all done, closing out #44 entirely (7/7 sub-issues).

```
0db0b49 feat(transformer): register filter_ne/filter_gt/filter_lt/not_in actions (#52)
c8c62dc feat(session): editable per-session labels, fixes label-before-first-Apply bug (#50)
dc49a7e feat(home): reshuffle-and-pin control for an unpinned plot seed (#49)
```

Each closed with a GitHub issue comment (not closed — this repo's workflow closes issues at
the dev→main PR). #44 (tracking) got a final summary comment too.

**#52** — `filter_ne`/`filter_gt`/`filter_lt` (`libs/transformer/.../cleaning/core.py`) and
`not_in` (`cleaning/analytical.py`), following the existing action pattern exactly.
`t3_translator.py`'s `_TRANSLATABLE_OPS` now covers all 8 T3 filter ops.

**#50** — found a real bug while building the UI: `set_session_label`/`get_session_label`
only ever touched the most-recent T3 ghost, so a brand-new session (before any Apply) could
not be labelled at all. Canonical storage moved to `assembly.json` (exists from first
assembly; `write_assembly_ghost(label=None)` preserves an existing label across a
recipe/data-change rewrite). UI: `ui.input_text(..., update_on="blur")` in the session card,
no separate Save button, guarded by comparing against the stored value (R3) so an unrelated
session action elsewhere can't spuriously re-fire the save.

**#49** — "🔀 Reshuffle arrangement" button next to a plot with an unpinned jitter layer;
clicking draws and pins a new seed into that plot's T3 `aesthetic_override.random_state`
(the shape #39/REPRO-SEED-1 already built — no new render-side plumbing needed). New
`recipe_pins_random_state()` in `plot_config_resolver.py` decides visibility. Found and fixed
three real bugs via the tests: an id collision between the `output_ui` wrapper and the button
inside it (both named `plot_reshuffle_{p_id}`); a copy-pasted `reactive.isolate()` that
silently stopped the button from ever reacting to its own pin; and a shared-module-scoped-page
state leak (the new tests left the browser on the "Curiosity" group tab, breaking
`TestViewBadges` later in the same file) — fixed by following this file's own documented
convention of restoring navigation state in a `finally` block.

### Files changed this continuation
- `libs/transformer/src/transformer/actions/cleaning/{core,analytical}.py` — 4 new actions
- `libs/transformer/tests/test_filter_actions.py` — NEW
- `libs/blueprint_arch/src/blueprint_arch/t3_translator.py` + its tests — extended op coverage
- `app/modules/session_manager.py`, `app/handlers/session_handlers.py` — label storage + UI
- `app/tests/test_session_manager.py`, `app/tests/test_shiny_smoke.py` — new tests throughout
- `app/handlers/home_theater.py` — reshuffle control
- `libs/viz_factory/src/viz_factory/plot_config_resolver.py` + its tests — `recipe_pins_random_state`
- `docs/user_guide/reproducible_plots.qmd`, `docs/foundations/reproducibility_same_input_same_output.qmd`,
  `docs/user_guide/understanding_your_export.qmd` — corrected/updated throughout both sessions
- `.claude/tasks/tasks.md`, `.claude/knowledge/architecture_decisions.md` — all REPRO-* and
  ACTIONS-FILTER-GAPS-1 entries marked done with implementation notes
- `.claude/rules/rules_agent_role_bioscientist.md §8` — action list updated

### Next step
Nothing is mid-flight and #44's whole initiative is now complete. Whatever Eve picks next is
unrelated to this thread — there is no natural continuation queued.

## Handoff 2026-11-09 (same day, final pass — thorough re-verification, issues closed, pushed)

Eve asked explicitly for a thorough re-verification (UML, docs, audits, tests) before closing
the issues and pushing — this correction supersedes the "not closing — closes at the dev→main
PR" assumption written earlier in this file; that was my own inferred default, not her
instruction, and she overrode it directly here.

**UML** (native StarUML bridge, never Mermaid): found and fixed two stale `SEQ-EXPORT`
messages that described pre-ADR-097-correction behaviour (an unconditional recipe-copy step
that no longer exists, and a provenance message not mentioning `effective_run.yaml`). Updated
three `UI-HOME` wireframe panel labels to mention this session's additions (Import, session
labels, Reshuffle) at the granularity the wireframe already uses elsewhere.
`audit_uml_model.py`: 0 violations throughout.

**Docs:** found two more stale canonical action lists beyond what #52's own commit touched —
`libs/transformer/README.md` and `docs/appendix/transformer_actions.qmd` (the latter is the
full per-action gallery; added proper §2.15–2.17/§6.3 entries, not just a list mention).
`audit_docs_sync.py` and `check_doc_links.py` both run fresh: 0 new violations (87
pre-existing broken doc links found, none touching anything this session changed — left
alone, out of scope).

**Audits:** `./scripts/run_audits.sh all` — all 10 routines PASS. Found a real, silently-broken
routine: `audit_template_flags.py` was renamed to `audit_app_features_flags.py` during the
ADR-091 vocabulary rename, but `run_audits.sh`'s thursday/all step and the script's own
docstring usage examples still named the old file — `|| true` was swallowing the resulting
error on every scheduled run since. Fixed both references.

**Tests, full gate:** headless `libs app/tests` 1589 passed. Full Playwright gate —
`test_shiny_smoke.py` + `test_shiny_smoke_blueprint.py` + `test_export_download.py` +
`test_every_app_features_starts.py` together — 64 passed, 3 expected skips.

**Issues:** #39, #44, #45, #46, #47, #48, #49, #50, #52 all explicitly **closed** (not just
commented) at Eve's direct request, each with a closing comment naming what was re-verified.

**Commits this pass:**
```
dd5e2ab docs(uml): thorough re-verification pass — UML, docs, and audit drift for #44
```
(plus the three feature commits from the prior handoff entry: 0db0b49, c8c62dc, dc49a7e)

**Pushed to `origin/dev`** (`git@github.com:evezeyl/SPARMVET_VIZ.git`) — confirm with
`git log origin/dev -1` if picking this up fresh.

### Next step
None queued. #44 is fully closed, verified, and pushed.

---

## Handoff 2026-11-10 (end of day — live-testing findings, 3 fixes, evening review pass)

Eve did live manual testing of Home/Blueprint/Test Lab and found 4 real problems in one pass.
All fixed, tested, documented, UML-synced, and pushed. Tomorrow's plan: she tests HOME
properly, starting that session fresh (no memory) — this entry is what that fresh session
needs to know.

### What was wrong, and what was fixed

1. **Issue #53 — Blueprint's left-sidebar panel was named "External Exchange."** It only
   imports/exports a bare recipe YAML, not a reproducibility bundle, but the name didn't say
   that — Eve read it as the place to import a reproducibility bundle. Renamed to
   **"Recipe File Exchange"** with an explicit one-line pointer to the real location
   (`app/modules/wrangle_studio.py`, `build_sidebar_ui()`).

2. **Issue #54 — the reproducibility bundle Import control existed in HOME's Export panel
   but Eve could not find it.** First fix (visible label + hint text) was not enough — she
   said so directly ("BUT I cant see the External Exchange HOME - where do we import it?").
   Real fix: restructured `system_tools_ui()` in `app/handlers/export_handlers.py` so Import
   is a bold-headed block, physically **first**, above Export, inside an accordion panel
   renamed **"Export / Import."** Confirmed by pixel position in a new mutation-tested test
   (`test_import_a_bundle_block_is_findable_above_export_form`), not just by existence.

3. **Issue #55 — Test Lab's right sidebar showed nothing.** Root cause:
   `config/ui/sidebars/testlab_standard_right.yaml` was `visible: false, panels: []`, stale
   since the panel content (`_render_test_lab_right_info()`, 5 tool descriptions) was written
   — the content always worked, the slot config was just never flipped on. Fixed the YAML;
   added a regression test that checks the actual tool names render
   (`test_test_lab_right_sidebar_shows_the_tool_descriptions`) — there was no test for this
   panel at all before, which is why a dead config sat unnoticed.

4. **Blueprint's "Validate" button never actually validated against the real engine load
   path.** It only ran a static-shape subprocess check — a recipe could pass Validate and
   still fail to load in HOME. Fixed `_handle_validate()` in `app/handlers/blueprint_handlers.py`
   to merge three checks: `validate_data_analysis_recipe()` (the real ADR-092/094 engine-load
   path) + the existing static coherence subprocess + `validate_data_analysis_recipe_data()`
   (data vs. contract). New test asserts the `"recipe rules"` row specifically, not just a
   PASS/FAIL badge (`test_validate_runs_the_real_engine_load_check`).

### The pattern behind all of this (why it slipped through)

Every one of these was a case of "the test checked existence, not the actual user-visible
behavior." Added three new mutation-tested Playwright regression tests closing exactly that
gap — each one verified tonight to fail against the original bug and pass against the fix,
with zero leftover mutation code (`git diff` confirmed clean each time). See the "GUARDED"
code comments at the 4 touched files for which test guards which behavior.

### Also fixed, unrelated to today's bug reports

A real, pre-existing Playwright test race in
`TestRecipeSwitchRendering::test_first_plot_renders_without_a_click_after_recipe_switch`
(predates this session, commit `47b274c`, 2026-11-08) — the restore-to-ST22-dummy step waited
on a tab label shared by two different recipes, so a later test's shared-session shortcut
could occasionally load the wrong one. Fixed by waiting on a plot sub-tab name unique to
ST22-dummy plus an explicit selector-value check. Verified clean twice in a row after the fix.

### Still open / known caveats (not blocking)

- `mcp__staruml-bridge__staruml_export_diagrams` silently does not write files — confirmed by
  unchanged mtimes across two calls that both reported success. Worked around tonight by
  copying the already-rendered `staruml_diagram_image` result directly. Needs a real fix or
  replacement before it's next needed for a larger diagram batch.
- Issue #54's "comparison to what was before" — whether Eve meant something beyond the 4-leg
  hash verification table (e.g. an actual diff view against the currently-open recipe) is
  still open, documented in the issue #54 comment thread and as `HOM-59` in
  `.claude/tasks/test_plan_home_2026-11.md`. Needs her clarification, not a guess.

### Verification done tonight, all clean

- Live Playwright screenshot walkthrough (dev server, `developer` app features, port 8123) of
  Home Export/Import, Blueprint Recipe File Exchange + Validate, Test Lab right sidebar — all
  6 screenshots visually confirmed correct, saved to `tmpAI/home_review_2026-11-10/`
  (gitignored, agent scratch — not meant to persist, regenerate if needed).
- Test recipe for tomorrow, `config/data_analysis_recipes/pipelines/1_test_data_ST22_dummy.yaml`:
  0 structure problems, 0 data-contract problems (`validate_data_analysis_recipe[_data]`).
- UML: added the missing UI-TESTLAB right-sidebar panel (frame widened 940→1250), saved,
  `audit_uml_model.py` 0 violations.
- Headless suite: 1589 passed. Full Playwright gate: 67 passed (64 + 3 new)/3 skipped, no
  flakes, 428.85s.
- `audit_docs_sync.py` 0 violations, `audit_deps_verify.py` PASS.

### Commits this session

```
143ae2d fix(blueprint,home): close #53/#54/#55 and make Validate check the real recipe rules
58d6490 test(home,blueprint): mutation-tested regression guards + UML + intent comments
```

Pushed to `origin/dev`. Working tree clean (`git status --porcelain` empty at session end).

### Next step for tomorrow's fresh session

Eve is testing HOME tomorrow, deliberately starting a **new chat session with no memory** so
testing starts clean. For that fresh session:

1. Read this handoff entry first, then `.claude/tasks/test_plan_home_2026-11.md` for the
   live test plan (has `HOM-59` open, see above).
2. The 3 issues fixed tonight (#53/#54/#55) are closed — re-verify only if something looks off
   again, don't assume they're still broken.
3. Test recipe is `1_test_data_ST22_dummy` — already confirmed clean, no need to re-check
   unless the data or recipe files change.
4. Dev server for manual testing: `PYTHONPATH=. SPARMVET_APP_FEATURES=developer
   ./.venv/bin/shiny run app/src/main.py --port 8123` (or whichever app features Eve wants —
   `developer` has every flag on).
5. The new "VOCAB NOTE" / "GUARDED" code-comment convention (added tonight at
   `wrangle_studio.py`, `export_handlers.py`, `home_theater.py` ×2) is there to help a fresh
   session quickly find which test/UML element governs a given panel's intent — grep for
   `VOCAB NOTE` or `GUARDED` if something in HOME looks wrong and the reason isn't obvious.

## Handoff 2026-11-11 (HOME filters and audit: design day; a fresh session may start the build of Exploration and the engine fixes)

**Branch:** dev. Code last changed by `fa552bf` / `28ec1a6`; everything after is design (UML, ADR-098/099, design files, issues).
**Uncommitted and not ours:** `CLAUDE.md` (Eve added section 9 "No Guessing"). Never stage it.

### What happened
Eve's manual test of HOM-09 led to a day of design. Result: Exploration (preview, table only, per dataset, cleared on view change) is
agreed; audit mode (the only way to change a plot) is designed but **not decided** (13 questions in
`.claude/design/home_audit_reading_guide.md`). Four reviews (scientist, data scientist, developer, consistency checker) found
verified bugs and design holes; the method is saved in `.claude/workflows/design_review_personas.md`.

### Built today (on dev, tested)
Preview filters change the table on every view and plots only on My view (ADR-098); trash unapplies at once; one operator vocabulary
and text size (#57, closed); tests for all of it (headless 1599 passed; `test_shiny_smoke.py` 38 passed, 3 skipped).

### Verified problems, open (issues)
#61 `extract_primary_keys` returns `[]` on tiered join steps (the ADR-049 key safeguards never fire; its only test is a dead debug script);
#62 integer thresholds truncated (`>= 90.5` keeps 90); #63 missing values dropped silently by `!=`, none-of and comparisons; #59 helper and
message for a plot broken by a dropped column; #64 guard rails; #60 the audit redesign; #56 Exploration.

### Next step for a new session
Open `.claude/tasks/home_exploration_build_brief.md` and follow it: WP1, WP2, WP3a, WP4 (with WP5), WP6; WP3b (the NA rule) is BLOCKED. It has a safety protocol (baseline, one revertible
commit per package, frozen files, compatibility with the audit) and four questions for Eve to ask first. Task entries: `HOME-EXPLORE-1..6` in `tasks.md`.
Re-verified the same day: #61 (empty key list on 3 recipes), #59, #62, #63; and a new finding, the audit engine and the translated recipe actions
give different rows for an integer threshold, so the figure and the reproducibility bundle disagree today (#62).
Audit mode waits for Eve (`AUDIT-DECIDE-1`). Archive tag before the redesign: `archive/home-filters-uml-2026-11-11`.

### Where everything is
Reading guide `.claude/design/home_audit_reading_guide.md`; design `home_preview_filters.md`, `home_audit_steps.md` (sections 18-20 are the
reviews); ADR-098 (built) and ADR-099 (target); diagrams `docs/UML/diagrams/HOME-*` and `UI-HOME-*`; issues #56, #59-#64.

## Handoff addendum 2026-11-11 (recipe review of 1_test_data_ST22_dummy)

**Done:** data-scientist review of the ST22 recipe (`.claude/design/recipe_review_st22_2026-11-11.md`). Verified by running: `facet_by` inside `mapping:` is ignored (#65);
three other plot-spec keys dropped silently (#66); `ST22_Anchor` joins two long tables (rows 74 -> 1731, `virulence_count` wrong for 18 of 42 samples, #67; engine check #68);
recipe hygiene (#69); samples with only unknown phenotypes scored as 0 (#70); the recipe data check passes while a schema cannot be built (#71). #61 has a second defect (the `on:` of
`unpivot` steps would be taken as join keys). Recipe fixed where unambiguous; all six plot-target collections byte-identical before/after; 21 new tests
(`test_shipped_recipes_hygiene.py`), headless 1620 passed.
**Waiting for Eve:** `RECIPE-ST22-2` (three questions in section 3 of the review file). **Brief updated:** WP7-WP10 added, WP2 gains the unpivot test.

## Handoff 2026-11-11 night (prepared while Eve rested; start from `.claude/tasks/next_session_start.md`)

**Done and committed:** recipe fixes of `1_test_data_ST22_dummy` (`7775a8d`); QA canary group with raw-file oracles (`c2cb302`); `mapping.facet_by` honoured (`4f85ec2`, #65, closed);
the recipe data check runs the wrangling (`af36dc9`, #71, closed). Issues #61-#71 re-verified against the code the same day (#59, #61, #62, #63 demonstrated again by running).
**Verification:** headless 1646 passed; QA canaries 8 passed; browser gate: 1 pass (recipe fixes only), then 3 runs of the changed tree with 1 or 2 timing failures each time in DIFFERENT tests (info panel, preview filter row removal, session label) that pass alone and in other runs; fresh-session load time unchanged; not proven either way: issue #72 (read it before you trust or distrust a red gate). I committed with that stated.
**Prepared for tomorrow:** `.claude/tasks/next_session_start.md` (three tracks, file ownership, traps, paste-ready prompts), the build brief with an issue protocol for parallel sessions, a status table and the canary map,
`.claude/design/home_audit_review_agenda_2026-11-12.md` and `home_audit_first_cut.md` (a proposal for a smaller first audit version, not decided), `recipe_review_st22_2026-11-11.md`.
**Waiting for Eve:** #67 (ST22 anchor), #70 (unknown phenotypes), #69 (rest), the NA rule (WP3b), the many-to-many check (#68, edits `libs/transformer`), the 13 audit decisions.
**Do not forget:** `CLAUDE.md` (Eve's section 9) was committed on 2026-11-11 at her request; do not edit it. Libraries are installed editable with absolute paths, so no git worktrees for builders.


## 2026-11-12 (morning, before the audit review)

**Done:** QA canary `QA_aggregated_no_key` (the fixture for the audit reach, #60; headless 1649 passed); the cheaper engine (E) explained with measurements (`home_audit_forensics_2026-11-12.md` 3.2b); F8 and 3.7 corrected: a feature without audit never changes a plot, that is Eve's rule and not a loss; a software architect's forensic review of the app and of the undecided items (`.claude/design/home_audit_architect_review_2026-11-12.md`).
**Most consequential finding:** recipe text runs as Python (`eval` in `mutate`); verified by running a `developer_raw_yaml` step. Bundle import writes a zip's recipe into the shared recipes folder. Severe only on a shared server. Not exploited. Options in architect review 3.1; nothing changed.
**Waiting for Eve:** N2-N6 and the proposal "view policy first in WP4 (#56)" (task `AUDIT-ARCH-DECIDE-1`); the earlier list (R1-R4, 13 audit decisions, NA rule, WP10). No issue was filed for the architect findings (candidates are listed in section 6 of the review).
**Not changed:** app code, design files other than the three above, the UML. The builders' file ownership and prompts in `next_session_start.md` are unchanged apart from the baseline numbers (headless 1649, canaries 9).

## 2026-11-12 (correction, same morning)

Eve asked me to check every consequence against what is decided. **Corrections to the entry above:** (1) the strip: the decided target has "Data: Raw | Result" in every feature and no "Plot to show", no My view, no Compare in Exploration; the rule "no sandbox flag, no changed plot" was already decided in ADR-099 (it was never a new decision N1). (2) "view policy first in WP4" is **withdrawn** (WP4 is interim; the policy module belongs to the audit build, written against the target). (3) The cheaper engine reconsiders a decided mechanism and was measured in the plot-level mode only. (4) Keys (inference as fallback) and the NA rule in principle were already decided.
**The real open question** is the interim for the two features without the sandbox flag (they keep a plot that changes unrecorded until audit mode exists; brief section 5, question 3, never answered), and the meaning of "Raw has no plot (NA)". Both in forensics 3.7, F8, F14. New verified fact: no code creates a `developer_raw_yaml` step (the rules say the Blueprint escape hatch does).
**Files rebuilt:** `.claude/design/home_audit_forensics_2026-11-12.md` (status map, reconsideration list R1-R6), `.claude/design/home_audit_architect_review_2026-11-12.md` (status on every item). Builders' instructions are unchanged.

## 2026-11-12 (Eve's answers on gating and test configurations)

Eve answered: filters not active are **hidden**; gating follows the configuration and must be clever; preview filters and filters that change/send to audit stay different; correct configuration files for automatic tests are needed; the demo is not a design concern. Everything else goes into documents for review (she cannot split attention).
**New paper:** `.claude/design/home_gating_and_test_configs_2026-11-12.md` (problem P1-P6, capability model, options G1-G4, companion rule R-a/b/c, test configurations C1-C4, 8 questions). Verified by running (scratch configs in `tmpAI/architect/test_configs/`, not committed): configs validate by path (`scripts/validate_app_features_config.py --strict`) and launch; a no-audit config offers My view and Plot to show; the "Exploration only" notice depends on a proxy flag; the Export panel says "steps sent to audit" without an audit; Rule 6 makes audit without Compare fatal (11 of 32 combinations clean).
**Waiting for Eve:** Q1-Q8 of the paper (task `HOME-GATING-DECIDE-1`) and the earlier list. Nothing built; builder instructions unchanged.

## 2026-11-12 (Eve's correction: design first)

Eve: the gating paper described how the code works today and started in the wrong order. **New order:** (1) agree the behaviour design, (2) mechanism, (3) build plan, (4) code, (5) gating and test configurations derived from the agreed behaviour table, (6) tests. **New file:** `.claude/design/home_design_first_roadmap_2026-11-12.md` (stages, behaviour table by kind of configuration from decided texts with open cells, questions Q1-Q5). The gating paper is PAUSED (banner). Builders: unchanged (engine fixes and WP4 stay; nothing touches the strip). Waiting for Eve: Q1-Q5 (task `HOME-DESIGN-FIRST-1`). Found: the contract 7.1 says sessions save applied filters, the exploration design says never, no code saves them (to correct in stage 3).

## 2026-11-12 (sorting the clutter, Eve's order of work)

Eve: move outdated plans/tests to a flagged `outdated` folder; work as design (science- and software-sound) -> review and agree -> plan -> build, one problem at a time. **Done:** ten files moved to `.claude/outdated/` (README index, OUTDATED banners; rename plan/mapping, Phase 26 UI checklist, August testing log, 3 design sketches); the three analysis papers moved to `.claude/design/home_evidence/`; builder brief and start file flagged ON HOLD, first cut PARKED, HOME test plan flagged "valid for as built"; reading guide section 0 now holds the order of work, the criteria (S1-S6, W1-W6) and the problem queue P1-P9 (**P1 is NOW**). Not moved (tied to something live): retest procedure, test plans, `design_t3_export_threading.md` (CLAUDE.md), the brief (issues link to it). Builders must not start before Eve releases a package.

## 2026-11-12 (P1 decided)
Eve decided P1: audit mode requires export, Compare and sessions; Compare requires audit. Rule 6 of the validator is right; my F16 / gating P4 / R-b, R-c / `test-audit` were wrong (withdrawn in the papers). Reading guide idea 8 explains "rows are not samples"; idea 9 and ADR-099 point 10 reworded (audit may remove poor-quality samples or data that makes no sense in a plot; not for exploration; not for homogenising messy fields). ADR-099 point 11 added. P2 is now.

## 2026-11-12 (P2, plot decided)
Eve: Exploration has ONE plot (Result, immutable, always shown); Audit mode has the immutable Result (comparison) and the audited plot (T3/My view). Replaces "Raw has no plot (NA)" in `home_preview_filters.md` (text fixed). UML to update after her OK: UI-HOME-EXPLORATION box and HOME-VIEW-MATRIX PLOT row (Raw cell "NA"). Open in P2: the notice text.

## 2026-11-13 (recipe format: specification drafted, issues filed; no recipe, validator or code changed yet)

**Eve's answers (2026-11-13):** the format applies to EVERY recipe (app and tests, transformer test recipes, gallery, writers); unknown keys FAIL; no backward-compatible default, old names refused at once with `legacy_keys.py` only suggesting the replacement; `is_primary_key` -> `is_entity_key`; T3 container in the schema now; dataset tier-2 fixed; required `data_engine: python-polars` and `plot_engine: python-plotnine`; descriptions filled by data-scientist rules; draft with `1_test_data_ST22_dummy`; spec lives in `.claude/design/` then spreads to rule file, appendix and user docs.
**Done and committed:** audit triage of the six reports of 2026-11-12 (`e3865b59`, all PASS, the checks are May-era and blind to the new rules); review `recipe_format_review_2026-11-13.md` (`f77425b0`); specification `recipe_format_spec.md` v0.1 and the ST22 main-file draft `recipe_format_st22_draft.yaml` (`6e83f773`; later edits and this entry in the next commit).
**Issues (fork, `-R evezeyl/SPARMVET_VIZ`):** tracking #73; #74 spec, #75 tests, #76 checker (folds #66), #77 tier-2 bug, #78 migrate, #79 docs, #80 formulas, #81 audits. Tasks in `tasks.md` carry the numbers (RECIPE-SPEC-1, RECIPE-TESTS-1, RECIPE-MIGRATE-1, RECIPE-DOCS-1, RECIPE-FORMULAS-1, RECIPE-AUDIT-REFRESH-1; UNKNOWN-KEYS-1 = checker).
**Baseline before any change:** headless 1652 passed in 99.65 s. ST22 content-hash baseline: `tmpAI/recipe_format/st22_baseline.json` (scratch, not committed; regenerate with `tmpAI/recipe_format/st22_facts.py`). Other scratch: `scan_compliance.py`, `key_inventory.py`, `step_params_probe.py`, `layer_probe.py`.
**Waiting for Eve:** section 13 of the spec (14 points: example variant for the gallery, schema `category`/`sub_category`, T3 container name, schema `output_fields` applied or not, legacy files, plot-spec taxonomy keys refused (reverses #66's text), alias removal in `libs/transformer`, type vocabulary, `scan_parquet`/`sink_parquet`), and the Abromics descriptions later.
**Next step (after her review):** #75 tests first (they must fail for the right reason on today's code), then #76 checker, #77 tier-2 fix with before/after pictures of `amr_heatmap` for @verify, #78 migration (ST22 first, text-level edits, fragment comments are Eve's: "do not remove").
**Do not touch:** `.claude/design/spaces/HOME.md` shows as modified in the working tree: it is Eve's own edit, never stage it.

## 2026-11-13 (later: spec v0.3, gallery as standard recipes: options written, waiting for Eve's choice)

**Eve's review of v0.2:** comments need a specification; the gallery must follow the same spec (examples are recipes), be checked by the same code as the app, and its needs go into the spec; propose solutions with pros and cons; explain the column-alias change; recipe science errors must be fixed.
**Found:** the comment key already exists as `comment` (singular): BP-COMMENTS-1, written by Blueprint on steps, layers, groups, plots (`blueprint_handlers.py:376-378,402-404`); ADR-083 lists it on layers. Spec v0.3 renames my `comments`, the checker must accept `comment` on every step and layer. The taxonomy terms are copied in five places and drifted ("Numeric-Numeric"). `submit_example` writes the example's steps into `wrangling.tier3`.
**Proof of concept (scratch `tmpAI/recipe_format/gallery_poc.py`):** all 34 gallery examples as standard recipes build and render through ConfigManager, DataOrchestrator, VizFactory; 22 pixel-identical, 10 differ only in size (800x600 committed vs 960x600), 2 jitter. Taxonomy all inside the cheat sheet; `dumbbell` declares `geom_segment` but draws `geom_line`/`geom_point`.
**Written:** `.claude/design/recipe_format_gallery_options_2026-11-13.md` (decisions D1-D7, inventory of 10 changes, order); spec section 6.9 withdrawn; issue #82; task GALLERY-RECIPES-1.
**Waiting for Eve:** D1-D7 of the gallery options (recommended: first option of each), the key name `taxonomy`, dead submission code removed or kept; plus section 13 of the spec. Nothing in the gallery or the recipes was changed.
**Do not touch:** `.claude/design/spaces/HOME.md` (Eve's edit).

## 2026-11-13 (later still: spec v0.4, format version, gallery plan v2)

**Eve's answers:** what is wrong in the gallery will be fixed; a format version for recipes matched to the spec is a good idea (from her review of the app changes with another agent); the gallery's `taxonomy` key is required; the authorised terms should be in the spec (one place instead of two); the gallery work is later but planned now.
**Written (docs only, committed):** spec v0.4 (`format_version`: section 4b, checks V01-V04, migration tool `migrate_recipe_format.py`, history table; one-place proposal in section 0; section 13 points 16-17); ST22 draft carries `format_version: 1`; gallery options v2 (`recipe_format_gallery_options_2026-11-13.md`): D3 rewritten (the specification as a data file, terms included), G1-G8 each mapped to a package and a test, plan GAL-0..GAL-9 with dependencies and tags, "decide now" (D1-D3, key name) versus "later" (D4-D7).
**Issues:** new #83 (format version + migration tool); #73, #76, #78, #82 updated, #74 commented. Tasks: RECIPE-FORMAT-VERSION-1, GALLERY-RECIPES-1 (plan).
**Waiting for Eve:** D1-D3 and the key name (they shape how #76 is built, so before the checker starts); `format_version` name/form; section 13 of the spec. Nothing in recipes, gallery or code was changed.

## 2026-11-13 (even later: the checker and the specification data file in libs/utils: verified)

**Eve's question:** does a data file in `libs/utils` break our rules; can one universal checker serve HOME, Blueprint and the others; recent decisions?
**Verified:** rules respected (Tier 1 pure + pyyaml; Tier 2 libs declare `utils`; ADR-011; ADR-099 16(g); the HOME stage-2 draft already places `utils.recipe_check` and `utils.recipe_graph` in `libs/utils`). A scratch prototype (`tmpAI/recipe_format/proto/`) shows a checker core that imports no peer library, reads its rules from a data file, gets the action/plot catalogs from the caller, and reports coverage; on the ST22 recipe it finds the 3 step problems. **Found by building wheels:** the container installs libs non-editable (`Dockerfile:72-81`); without `package-data` a YAML file in `utils` is missing from the wheel (no library ships data files today). **Also found:** `Dockerfile:79` lists the non-existent `libs/generator_utils` and omits `blueprint_arch`, `test_lab`, `id_reconciliation` (noted in DOCKER-RELEASE-1, no new issue).
**Written:** spec v0.5 section 0b (rules table, packaging, design with injected catalogs and a coverage report, one Tier-3 adapter, callers, the loader's catalog-free subset); gallery options D3/D4 note; #76 updated (architecture, packaging test, import test, full-coverage test).
**To align between sessions (Eve's call):** the HOME stage-2 draft writes `check_recipe(raw, mode)`; the recipe spec writes `profile` (run, build, gallery). "Mode" already means Exploration/Audit in HOME. Proposal: `profile`.

## 2026-11-13 (dictionaries and reuse: ADR-041 found; spec v0.6)

**Eve's notes:** (1) some library code may need to move to `utils` to be reusable (no overview yet); (2) recipes written as dictionaries: there are rules, check list or dictionary; (3) the Dockerfile is not ready, nothing is deployed.
**Found:** ADR-041 (ENFORCED 2026-04-20): keyed definitions = Rich Dictionary, tier1/tier2 = sequential list, fragments flat (no anchoring key). The spec never stated the form of each container; now section 4c does. Scan (`tmpAI/recipe_format/container_forms.py`): all 307 input and 162 output field entries are dictionaries; 17 list-form containers (7 empty `[]`, 10 with content: 3 `final_contract` lists skipped silently by the engine (`demo_abromics`, `universal_template`, `relational_audit`), 1 `output_fields` list of names, 1 flat legacy `wrangling`, 5 flat join `steps` in fixtures); 33 wrapped fragments; PyYAML keeps duplicate keys silently (verified), so the loader needs T10. Two texts contradict ADR-041 (rule file section 8; data contract rules 4.3 types). Parameters declared `multi` get a list 90 times and a single value 2 times.
**Written:** spec v0.6 (4c, checks T10, FD06, ST07, J07, reuse candidates in 0b, finding 16); #76 and #78 updated; tasks UTILS-REUSE-REVIEW-1 (a possibility, nothing moved) and the Dockerfile note ("not ready, nothing urgent").

## 2026-11-13 (dictionaries enforced with corrective messages; identical keys; the string type)

**Eve:** recipes must be dictionaries and tests and the app must verify it with an error message and a suggestion; add it to HOME and to the refactoring plan; identical keys matter (the same ID in every T1); why was the `string` type removed; unify and read the types in one place.
**Done (docs/tasks/issues only):** spec v0.7: 4c now says every container-form check shows the **corrected text** (generated), in the app (one adapter) and in the tests; "identical keys" explained (unique per mapping; `sample_id` in every table is correct; real hazards: a repeated key in one mapping (T10), a column in both tables of a join silently renamed `..._right` (check J08, `QC_Reads_Anchor.total_reads_right`), steps stay lists because a T1 repeats actions); type vocabulary history + options A-D (6.4, point 10); points 18-19. **Added to the HOME plan at Eve's request, minimal edits:** `home_stage2_mechanism_spec.md` rows P2 and P3, `home_audit_reading_guide.md` register item (C) ("added after the count"). `spaces/HOME.md` NOT touched. Tasks: RECIPE-TYPES-1, RECIPE-GRAPH-UTILS-1, RECIPE-TESTS-1 updated. Issues: new #84 (types), #73 #75 #76 #78 updated.
**Verified by running:** ingestor casts `categorical` and `string` to String, but NOT `utf8`, `boolean`, `i64` (digits stay Int64); PyYAML keeps the last of two identical keys silently; joins use Polars' default `_right` suffix.
**Why `string` was removed:** on record only "deprecated alias" (LEGACY-TYPE-ALIASES-1, Phase 34 legacy sprint, commit 125963cf; 6 recipes migrated string -> categorical). No ADR gives a deeper reason; stated as such.
**Waiting for Eve:** type vocabulary content (A keep four + cast utf8 [recommended], B rename utf8 to text, C restore string, D add boolean); point 18 (steps stay lists?); point 19 (level of J08); plus the earlier points (D1-D3 gallery, format_version name, `profile` vs `mode`).

## 2026-11-13 (spec v0.8: the form follows what depends on it; registry check)

**Eve:** (1) "design our specs accordingly, based on what depends on it" after the HOME analysis (ordered steps stay lists; named things dictionaries; optional `id` in a step); (2) "dictionaries are the containers, the rest ordered steps; check how each operation for the data and plot is registered".
**Done (docs, tasks, issues only; no code changed):** spec v0.8: 4c rule with three categories (dictionary / list / ordered dictionary), 4d step ids (optional `id`, `audit_` for app-inserted steps), checks ST08 to ST10, 6.10 registries (R1 to R6, tests AR2 to AR6), findings 18-19, section 13 points 18 and 20, tests. Issues: new #86 (stored T2 keeps the old column order after a `final_contract` reorder, verified by running), new #87 (registry gaps), #85 reframed, #73 #75 #76 #78 #83 bullets corrected. Tasks: RECIPE-ORDER-IDS-1, RECIPE-REGISTRY-1.
**Verified by running (scratch in `tmpAI/recipe_format/`):** `registry_survey.py` (67 actions, 65 with schema; 191 components, all with schema, all `allow_extra_params: true`; 8 widgets, none for list or dictionary), `registry_conformance.py` (aliases read by `rename`, `split_column`; internal `__right_df__`, `__metadata__`), `registry_examples.py` (9 examples disagree with their own declared widget), plotnine refuses `foo` and accepts `color` and `colour`, `contract_order_test.py` (T1 follows the new `final_contract` order, stored T2 does not).
**Process incident:** my uncommitted v0.8 edits (steps as dictionary, since withdrawn) were committed by the HOME session in `c8c916dc` (that commit lists 4 files, 3 of them mine; how they were included is not known). HEAD held the superseded draft until this commit replaces it. We share one working tree: both sessions stage by explicit file names.
**Waiting for Eve:** spec 13.18 details (`id` optional or required; `audit_` prefix; `final_contract` key order = column order; tab order = key order), 13.20 (parameter vocabulary; layers read plotnine arguments), type vocabulary (A to D), gallery D1-D3 and `taxonomy`, `format_version` name, `profile` vs `mode`, J08 level.

## 2026-11-13 (clean spec; #86 and #87 fixed; #88 filed)

**Eve:** fix the gaps (registries yes; `final_contract` order yes; tab order yes; plot arguments are checked); fill the issues, then do it and close when done; make the specification files clean (one file, the rest archived), then review what is undecided.
**Done:** (1) `.claude/design/recipe_format_spec.md` rewritten as ONE file (commit `e958eab1`): decisions with source (2.1), principles (2.2), **open points in one table (2.3, O1 to O18)**, then how each part works; the earlier drafts, the gallery options, the first review and the ST22 draft are in `.claude/design/outdated/` with OUTDATED banners; the ST22 findings are on issue #78. Issues #73 to #87 point at the new section numbers. (2) **#86 fixed and closed** (`b2c46ca9`): the key order of `final_contract` is part of the Tier 1 key (`ENGINE_CACHE_VERSION` 3); 9 tests. (3) **#87 fixed and closed** (`7cafc08a`): widgets `list` and `mapping`, eight declarations corrected (the count is eight, not nine), the Blueprint form shows and saves one line of YAML, `viz_factory.arguments` (what plotnine accepts, verified against plotnine for all 63 geom and stat components), `utils.strict_yaml`, `utils.ui_schema`, registry consistency tests AR2/AR4/AR5/AR6. (4) **#88 filed**: 13 schema parameters in 7 components that plotnine refuses (found by the oracle).
**Verified by running:** headless baseline 2101 passed (was 1652); Blueprint smoke suite 17 of 17; three mutation checks fail as they should.
**Not done, by design:** ST09, ST10, AR3 against the checker (#76); alias reads in `rename` and `split_column` (#78); rule files (#79, double confirmation).
**Process:** the other session was re-sorting `tasks.md` and `INDEX.md` while I worked; I committed only files I own, by name (`tasks.md` after their sort was committed).
**Waiting for Eve:** the open points of spec section 2.3 (O1 to O18); answers to what the step `id` is for are in spec 7.5 and on #85.

---
## Handoff 2026-11-13 (late): the recipe format series, HOME session alone (the recipe session was closed by Eve)

**State (all on `dev`, committed, suite green, golden baseline "result-identical"):** W0 golden baseline (`assets/scripts/golden_baseline.py`, `app/tests/golden/baseline.json`); W1 `step_problems` and schema `rules`; W2 `check_recipe`; W3 formula check, path checks, `!include` confinement; W4 `utils/action_names.py`; W5 `DataIngestor.ingest_declared` (`ingestion/declared.py`); W6 the new actions registered beside the old ones: `actions/polars_calls.py` (39 `polars_`), `actions/modified.py` (`modif_filter`), `actions/composite.py` (`step_top_n_other`); W7 part 1 `utils/recipe_migration.py` (keys, types, null_values, strip, spec_version).
**Eve's rules:** sequential, one agent; Eve decides, I recommend; Polars action and nothing else where possible; no silent behaviour, no hidden default; never truncate silently (no `modif_cast`); tests for everything, mutation-checked; I am `sonnet/high` and do the medium, low and haiku items too; only `opus/high` items need Eve to change the model (W12 ADR-100, W15 science review, W3b attack design, the rule-file text). Eve is resting; she reads the report in the chat.
**The series that remains (one atomic switch; dev must be green at every commit):**
 S1 a converter old step to new steps (`utils/step_migration.py`) with a differential test per old action (`libs/transformer/tests/test_step_conversion.py`; templates already in `test_replacements_by_polars_steps.py`);
 S2 migration tool part 2: rewrite the steps in the yaml text, run over `config/`, fixtures, tests (120 yaml files with old action names, 92 with old types, 36 `.py` and 22 `.py` with inline recipes);
 S3 remove the old actions, `ingest_declared` becomes `ingest`, DataWrangler/assembler/orchestrator/MetadataValidator/audit translator/bootstrapper/id_reconciliation use the new names (constants in `utils.action_names`), the three xfail registry tests pass;
 S4 run the tool, check the golden baseline is identical, adapt the tests;
 S5 run B (`final_contract`, `keep_columns`, `drop_columns` to `polars_select`/`polars_drop`, `labels`), cache-version bump;
 then W8 writers, W9 engine side, W10 tier-3 reader, W11 gallery (GALLERY-RIGOR-1), W13 documentation (DOC-MISSING-VALUES-1), W14 Blueprint, W16 ID-RECON-STEPS-1, REMOVE-CATEGORY-SELECT-1, the stale `manifest_paths` line.
**Open for Eve (asked, not answered):** Q3 dead gallery submission code (remove or keep); the data owner's question on `NA` in `metadata_isolation_method`.
**Files:** `.claude/design/recipe_format_spec.md` (decisions), `recipe_format_work_order.md` (W0 to W16), `home_evidence/actions_and_polars_2026-11-13.md` (sections 9 to 26, the evidence), `tmpAI/agent_channel.md` (not in git).

## Handoff 2026-11-14: recipe format 1, state after the three parallel packages

**Branch:** `feat/recipe-format-1`. Local `dev` is behind it, and nothing of today after commit 29a563c7 is pushed.

**Merged:** the three packages (W11 gallery, W8 writers, W16 ID-RECON-STEPS-1 with RETEST-REPLACE-1, REMOVE-CATEGORY-SELECT-1, RENAMED-KEYS-1), the strict checker in the load gate, migration runs C and D, the orchestrator fails on unknown ids, `CLAUDE.md` section 2.1 (agent rules).

**Controls (2026-11-14):** headless suite 3604 passed, 14 xfailed (exit 0). Browser tests 70 passed, 3 skipped (exit 0). Golden baseline: result-identical. Audits: recipe coherence, deps verify, cross-lib PASS. `validate_app_features_config --strict` PASS. FAIL: `audit_docs_sync` (3 doc backtick path violations), `audit_task_drift` (1 drift: `app/modules/exporter.py` named by AUDIT-RAWYAML-REMOVE-1), `check_doc_links` (65 problems, for example `docs/appendix/viz_factory_rationale.qmd:157-158` still point to `libs/viz_gallery/assets/generate_previews.py` and `refresh_gallery.py`). Not fixed here.

**Open decisions for Eve:**
- Gallery: accept or reject the 8 changed previews (`tmp/gallery_preview_review/`); `beeswarm_sina` (tier-3 reader, move the filter to tier 1, or drop it); rewrite `rules_gallery_standards.md` (needs her double confirmation).
- Writers: a fresh Blueprint draft has no plot and cannot be opened (loader accepts an empty draft, or the form creates a first plot); delete the dead `SF_create_data_analysis_recipe.py`?; the two `debug_*` scripts in the old test-file shape (keep as test-only or migrate).
- ID reconciliation: three defects recorded as strict xfail tests; keep the bridge (recommended).

**Next:** JOIN-KEY-TYPES-1 (decided: a join keeps declared types), then IMPORT-PATH-1 (decided: option A), then SMOKE-RACE-2, the tier-3 reader, the Blueprint package, and the documentation sweep with the full name "data analysis recipe" in user-facing text.

## Handoff 2026-11-14 (evening): JOIN-KEY-TYPES-1 merged, follow-ups, index generator

**Merged:** JOIN-KEY-TYPES-1 (`bddaf76a`): a join keeps the declared types of its keys and fails when they differ. 14 baseline records change only by the type of `sample_id`; no joined table and no plot changed.
**Follow-ups (branch `feat/recipe-format-1`):** `77538c54` the key check also fails for a missing key column (one or both sides) and for `left_on`/`right_on` of unequal length, with a plain message; the fix text says a step before the join changes only the left table; semi/anti tests. `b0f0b198` the dependency index generator skips `.claude/worktrees/` (index 4820 to 989 lines); `check_doc_links` problems 566 to 61.
**Controls (reviewer, on 6e318386):** headless 3642 passed, 14 xfailed; browser (qa) 70 passed, 3 skipped; golden baseline result-identical; audits deps_verify, cross_lib, task_drift pass; docs_sync fails with the 2 known violations; dependency index 989 lines, no worktree path.
**Open for Eve:** a first assembly step that joins the base table with itself is skipped silently (keep, or fail); template `complex_template` has the key `sample_id` as Float64; DOC-JOIN-CAST-1 needs her for the rule file and a superseding ADR for ADR-050.
**Next:** IMPORT-PATH-1 stopped at step 0 (nothing built) and waits for Eve's decision (panel recommends a data folder per import; see tasks.md); then JOIN-PREVIEW-STRICT-1 with the Blueprint package, CHECKER-JOIN-KEYS-1, SMOKE-RACE-2, the tier-3 reader, the documentation sweep, DEP-INDEX-STALE-1.

## Handoff 2026-11-14 (night): for the next coordinator session

**Start:** a Fable session types `-coordinate` first (CLAUDE.md 2.1, `.claude/workflows/agent_dispatch_howto.md`). Workers: `builder`, `reviewer`, `scribe`, `scout`, the `panel-*` viewpoints.
**Branch:** `feat/recipe-format-1`. Nothing after `29a563c7` is pushed; local `dev` is behind. Push only when Eve says.
**Done today:** three packages merged (gallery examples as recipes, recipe writers, small fixes); strict checker in the HOME load gate; JOIN-KEY-TYPES-1 merged (`bddaf76a`) with follow-ups (`77538c54`); dependency index generator skips worktrees (`b0f0b198`); record repairs (`88bb3f9a`, `3395fcad`); agent setup (`6e318386`).
**Control command note:** the baseline check is `PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json`.
**Waiting for Eve (recommendation in brackets):**
1. IMPORT-PATH-1, stopped at step 0, nothing built: which option [a data folder per import, `<user_data>/_imports/<recipe id>/data/` plus a record read by the orchestrator]; the name of the imported recipe [keep `<original>_imported_<timestamp>`]; whether the by-dataset-id rule also accepts `.parquet` [yes, and fail when both exist]. Panel of three viewpoints agreed on the option. Findings: `.claude/worktrees/agent-abd52719502485bdb/tmpAI/progress.md`; hash survey: `tmpAI/survey_hash/table.md`.
2. The eight changed gallery previews, old and new side by side in `tmp/gallery_preview_review/`.
3. A first assembly step that joins the base table with itself is skipped silently: keep, or fail (tasks.md, under JOIN-KEY-TYPES-1).
4. TEMPLATE-KEY-TYPE-1 (key declared Float64 in `complex_template`); DOC-JOIN-CAST-1 (a rule file and ADR-050 still describe the removed cast; ADR text is `opus/high`).
5. Older open points in tasks.md: `beeswarm_sina`, the empty Blueprint draft, three old scripts, three ID-reconciliation defects, RECIPE-WORD-1 scope, String or Categorical in recipes.
**Next for the coordinator, in order:** (a) after Eve's answer to 1: IMPORT-PATH-1 together with SOURCE-LOOKUP-ONE-1, one `builder` at `sonnet/high`, continued in the worktree `agent-abd52719502485bdb` (merge `feat/recipe-format-1` into it first), then `reviewer`, merge, controls; (b) CHECKER-JOIN-KEYS-1 `sonnet/medium`; (c) the Blueprint package with JOIN-PREVIEW-STRICT-1; (d) tier-3 reader, GALLERY-CHECK-START-1, FILTER-UNIFY-1, SMOKE-RACE-2, AUDIT-REPAIR-1, DEP-INDEX-STALE-1; (e) the documentation sweep at the end (61 broken documentation paths, 2 docs_sync violations, seven of them in rule files that need Eve).
**Worktrees:** `agent-a57725701187f3e6e` (join keys) is merged and removed. `agent-abd52719502485bdb` is kept: no code, only the findings note.

## Handoff 2026-11-14: third coordinator session (interim): three tasks merged, queue, decisions for Eve

Live progress file: `tmpAI/coordinator/progress_2026-11-14_session3.md` (not in git; it is the state if the session stops).

**Branch and push:** `dev` was fast-forwarded to `1dad1f4c` and pushed to `origin/dev` at the start of the session (Eve asked). The three tasks below are merged into `feat/recipe-format-1` only: NOT in `dev`, NOT pushed.
**Merged:** JOIN-PREVIEW-STRICT-1 (`870207ba`, `13194791`); CHECKER-JOIN-KEYS-1 (`9da9ce19`, `00b64f53`, merge `67419ef4`); GALLERY-CHECK-START-1 (`f7f5aa20`, `642ec0f0`, merged after `67419ef4`).
**Controls:** on `67419ef4` (reviewer): headless 3695 passed, 14 xfailed; golden baseline result-identical; app import OK. Browser tests and the full controls NOT run after these merges (the gallery merge is after `67419ef4`). At the end of the session: full controls (headless, browser with `SPARMVET_APP_FEATURES=qa`, golden baseline, audits), then `git fetch . feat/recipe-format-1:dev` and `git push origin dev` (Eve asked that all commits are in `dev` and `dev` is pushed).
**Running:** SMOKE-RACE-2 (builder, worktree `.claude/worktrees/smoke-race-2`, branch `task/smoke-race-2`): seven `inner_text(` reads changed to waiting assertions, in its two browser runs. HOME scout: which HOME tasks (tasks.md group 1, stage-2 plan, #61 to #63, #56) are buildable now.
**Queue** (Eve's priority of 2026-11-14: HOME first with its library and recipe prerequisites, then Gallery; Blueprint and Test Lab last):
1. The HOME tasks the scout tags BUILD-NOW.
2. TEST-FLAKY-1 `[sonnet/medium]` (browser tests; after SMOKE-RACE-2 is merged, same files).
3. Documentation: DOC-MISSING-VALUES-1, the `docs/` lines of DOC-JOIN-CAST-1, broken paths in `docs/` and README (worktree `.claude/worktrees/docs-sweep` exists, unused).
4. DEP-INDEX-STALE-1 `[sonnet/low]` and the session-end `build_dep_graph.py`.
5. ADR-100 draft (W12, `[opus/high]`, one builder-opus), as a draft for Eve.
6. BP-VALIDATE-1 `[sonnet/low]` (Blueprint, last).
7. Records by a scribe: tasks.md, spec catalogue J09 to J11, two stale sentences of REMOVE-CATEGORY-SELECT-1 in `.claude/design/recipe_format_spec.md`, handoff, channel row.

**Decisions for Eve, new in this session** (also marked `DECISION FOR EVE` in tasks.md):
- N1: join key rule in three places (build, Blueprint preview, checker), kept in step by a parity test only. Options: keep the copies with parity tests; or one pure rule in `libs/utils`.
- N2: `except Exception` in `_jd_run_preview` shows programming errors as "Preview failed". Options: leave; or catch only expected errors.
- N3: read-only gallery folder: a failing example in the old index is still shown (console warning only). Options: keep; or leave failing examples out in memory (`bootloader.rejected_gallery_examples`).
- N4: an example left out at start has no screen element (spec section 9 silent). Today: left out, reason in `metadata.rejected` and a console warning.
- N5: checker J10 (join key not declared in `input_fields` refused at load): confirm. See N1.
- N6: AUDIT-REPAIR-1: four old words (`persona`, `manifest`, `profile`, `project`) and one UML tag: fix the text or adapt the exclusions. `recipe` waits for RECIPE-WORD-1.
- N7: tier-3 reader (W10) needs HOME's P5 mechanism spec and the order of change R1 (`recipe_format_spec.md` line 173); `beeswarm_sina` waits for it.
- N8: W14 Blueprint package: tasks.md line 82 says Blueprint is not touched now; the earlier handoff listed it as next. Eve (2026-11-14): Blueprint and Test Lab can wait.

**Decisions for Eve, older:** see "Handoff 2026-11-14 (night)", points 1 to 5 above.

**Worktrees:** `checker-join-keys`, `join-preview-strict`, `gallery-check-start` are merged and can be removed. `smoke-race-2` in use. `docs-sweep` prepared. `agent-abd52719502485bdb` kept (findings note, no code). Tests in a worktree need the worktree sources first in `PYTHONPATH` (the shared `.venv` imports the libraries from the main tree).

## Handoff 2026-11-14 (third coordinator session, update 2): six merges, dev pushed at 46425c89, decisions N1 to N15

Live progress file: `tmpAI/coordinator/progress_2026-11-14_session3.md` (not in git).

**Branch and push:** `origin/dev` is at `46425c89` (pushed). The merges `57724105` (documentation) and `334b8dfc` (browser tests) are on `feat/recipe-format-1` only: NOT in `dev`, NOT pushed. TEST-ORDER-1 is not merged.
**Merged since the interim note:** HOME-EXPLORE-1 (merge `46425c89`, commits `9427dc36`, `73cecd2b`); the documentation (merge `57724105`, commits `a607174f`, `b5fe3e78`, `5e9864b9`: DOC-JOIN-CAST-1 docs part, DOC-MISSING-VALUES-1, one broken path); SMOKE-RACE-2 (merge `334b8dfc`, commits `382848c2`, `9dffbb8d`). Six merges in this session with the three from the interim note. The documentation diff was not reviewed on its own; the final reviewer reads it.
**Found done already:** GALLERY-SUBMIT-SCHEMA-1 (read by W11, not run: `submit_example` writes format 1 and runs `check_recipe`; tested in `test_gallery_bundle.py`); NAN-ACTIONS-1 (`polars_fill_nan` and `polars_drop_nans` exist in `libs/transformer/src/transformer/actions/polars_calls.py`).
**Controls:** on `46425c89` (reviewer): headless 3818 passed, 23 xfailed; golden baseline result-identical; tree clean. The browser gate was run on `334b8dfc` by SMOKE-RACE-2 only (61 passed, 3 skipped, twice). Not run: the audits; the full controls on the final state.
**Running:** TEST-ORDER-1 fixes (builder sonnet, worktree `home-test-order`, branch `task/home-test-order`; commit `99447ec1` removes the #62 mark; the independent raw-file oracle and the docstrings are being added; then review). TEST-FLAKY-1 (#72) (builder sonnet/medium, worktree `test-flaky-1`, branch `task/test-flaky-1`; it runs the full browser gate once).
**Still to do in this series:** merge TEST-ORDER-1 and TEST-FLAKY-1, with headless controls after each merge; DEP-INDEX-STALE-1 with `build_dep_graph.py` (last builder); final controls by a reviewer (headless, golden baseline, audits, the documentation diff `a607174f..5e9864b9`); final scribe (handoff, tasks.md, spec section 11 catalogue J09 to J11, channel row); fast-forward and push `dev`.
**Not started on purpose** (quota and Eve's priority): ADR-100 draft (W12, opus/high); BP-VALIDATE-1 (Blueprint); RECIPE-DOCS-1 (#79, large); AUDIT-REPAIR-1.
**HOME: what blocks the rebuild:** NA-RULE-63 (#63): the NaN rule and the count message, Eve to confirm; STAGE2-SPEC-1: Eve reads and confirms the v0.1 mechanism spec (`home_stage2_mechanism_spec.md`); KEYS-NODE-1: Eve confirms the hash model (`home_evidence/home_hash_model_2026-11-12.md` section 4); RECIPE-GRAPH-UTILS-1: option C+; HOME-DESIGN-REVIEW-1 (SC1, SC2, SC4, AR4, SC5, AR2, AR1); FILTER-UNIFY-1; FORMULA-SAFETY-1. Tasks that wait for these: FILTER-DTYPES-1, HOME-EXPLORE-2 (#61), HOME-EXPLORE-4/5/6 (#56), AUDIT-VIEW-1, AUDIT-RAWYAML-REMOVE-1, TEST-SHAPES-1.
**Decisions for Eve N9 to N15** (also in tasks.md as `DECISION FOR EVE`):
- N9: VizFactory `in` / `not_in` compares as text, so a numeric `in` filter gives no rows in the plot. Evidence: 4 strict xfail cases, `app/tests/test_filter_int_equivalence.py`. Options: approve the small fix now (it changes plots with numeric `in` filters), or wait for FILTER-DTYPES-1.
- N10: the reproducibility export writes the filter value as text, so re-running it on a number column fails. Evidence: `t3_translator.py` about line 127; 12 strict xfail cases. Options: approve EXPORT-FILTER-VALUE-1 (the translator is frozen, brief S4), or leave it.
- N11: `between` is not translated (UntranslatableNode). Evidence: `t3_translator.py`. Options: add the translation later, or keep refusing it.
- N12: what blocks the HOME rebuild: see the list above.
- N13: a drop and a filter on the same column at one node. The view runs filters first; the exported recipe keeps the recorded order and stops with "column not in the table". Evidence: TEST-ORDER-1, checked by running; not tested. Options: refuse such a step, or define the order.
- N14: TEST-ORDER-1 tests that wait for the unconfirmed stage-2 spec v0.1 and for the `hypothesis` dependency (D9). Options: confirm the spec and allow the dependency, or leave those tests out.
- N15: `submit_example` has no caller outside the tests (`gallery_manager.py` 163-203). Options: keep, or delete.
**User-visible change:** a threshold that is not an integer on an integer column is now compared as a number, so the plot agrees with the reproducibility export (issue #62).

## Handoff 2026-11-14 (third coordinator session, final): ten merges, dev pushed, the decisions for Eve in one list

**Start:** a Fable session types `-coordinate` first (CLAUDE.md 2.1, `.claude/workflows/agent_dispatch_howto.md`). Workers run on the model and effort of their task tag, never on Fable. Worktrees: create one with `git worktree add .claude/worktrees/<task> -b task/<task>` and link the shared environment (`ln -s <main>/.venv <worktree>/.venv`; remove the link before `git worktree remove`). The shared `.venv` imports every `libs/*` package from the main tree, so tests in a worktree need the worktree's source folders first in `PYTHONPATH` (`PYTHONPATH=$PWD:$PWD/libs/<lib>/src:...`); ask for `print(<module>.__file__)` once to check.

**Branch and push:** the branch is `feat/recipe-format-1`. `dev` is at `13f120f6` and is pushed to `origin/dev` (fourth push of the session). All ten merges below are in `origin/dev`. The records of this session (this section, the tasks.md edits, the J09 to J11 rows of the spec, `.claude/logs/audit_2026-11-14.md`) are NOT committed yet.

**Merged** (merge commit, then the commits):
1. JOIN-PREVIEW-STRICT-1: the Blueprint join preview gives the build's verdict (merge commit not recorded in the progress file; commits `870207ba`, `13194791`).
2. CHECKER-JOIN-KEYS-1: the recipe checker refuses J09, J10 and J11 at load (merge `67419ef4`; commits `9da9ce19`, `00b64f53`).
3. GALLERY-CHECK-START-1: with `gallery_enabled`, the gallery check runs at start (merge commit not recorded in the progress file; commits `f7f5aa20`, `642ec0f0`).
4. HOME-EXPLORE-1 (#62): one shared filter-value coercion in `libs/utils` (merge `46425c89`; commits `9427dc36`, `73cecd2b`).
5. Documentation (merge `57724105`; commits `a607174f`, `b5fe3e78`, `5e9864b9`): the docs part of DOC-JOIN-CAST-1, DOC-MISSING-VALUES-1, one broken path.
6. SMOKE-RACE-2 (merge `334b8dfc`; commits `382848c2`, `9dffbb8d`).
7. TEST-ORDER-1 (merge `416a5056`; commits `a086bef9`, `99447ec1`, `e823c178`): `app/tests/test_step_order.py`.
8. DEP-INDEX-STALE-1 (merge `cbad9ff3`; commits `049a5258`, `d766ac1e`, `9bd329b2`).
9. TEST-FLAKY-1 (#72) (merge `5e8470f7`; commit `87340720`).
10. Docs minimal example (merge `13f120f6`; commit `14ccda25`): the minimal example and the key-fields table of the authoring guide are format 1.

**Found done already:** NAN-ACTIONS-1 (`polars_fill_nan` and `polars_drop_nans` exist in `libs/transformer/src/transformer/actions/polars_calls.py`); GALLERY-SUBMIT-SCHEMA-1 (`submit_example` writes format 1 and runs `check_recipe` in profile gallery; tested in `libs/viz_gallery` `test_gallery_bundle.py`; read, not run).

**Controls:**
- Final, on `13f120f6` (reviewer): headless `3843 passed, 23 xfailed in 139.57s` (it was 3642 passed and 14 xfailed at the start of the session); golden baseline `result-identical` (`PYTHONPATH=. ./.venv/bin/python assets/scripts/golden_baseline.py --check app/tests/golden/baseline.json`); `audit_deps_verify` PASS (21 load-bearing files carry a `@deps` block); `audit_docs_sync` exit 1 with 1 violation (`libs/id_reconciliation/README.md`); `audit_uml_model` 6 violations in PKG-TIERS, not new; tree clean.
- Earlier, on `dc91823d`: `task_drift` 0, `cross_lib` 0, `validate_app_features_config --all --strict` PASS, `audit_old_words` exit 1 (known), `check_doc_links` 60 problems.
- Browser gate: `70 passed, 3 skipped in 493.00s` (the browser files under `SPARMVET_APP_FEATURES=qa`). It was run before the last small merges (the progress file names the conftest hook and one docs page). It was NOT run on the final state `13f120f6`. It does not prove the flaky tests fixed: they showed only under load, and one green run does not show that they are gone.

**User-visible change:** a threshold that is not an integer on an integer column is now compared as a number, so the plot agrees with the reproducibility export (issue #62).

**Decisions for Eve** (one list; a reader goes through it with her; the evidence is in each line):

**Older points (night handoff, points 1 to 5)**
1. IMPORT-PATH-1 (`tasks.md`): which option (recommended: a data folder per import, `<user_data>/_imports/<recipe id>/data/` plus a record the orchestrator reads); the name of the imported recipe (recommended: keep `<original>_imported_<timestamp>`); whether the by-dataset-id rule also accepts `.parquet` (recommended: yes, and fail when both exist). Findings: `.claude/worktrees/agent-abd52719502485bdb/tmpAI/progress.md`; hash survey `tmpAI/survey_hash/table.md`. Note: `tasks.md` also says "Eve DECIDED 2026-11-14: option A, as production", while the night handoff says it waits. Ask Eve which is current.
2. The eight changed gallery previews (boxplot_faceted, boxplot_simple, jitter_strip, point_faceted, point_simple, tile_simple, violin_faceted, violin_simple): accept or reject each. Old and new side by side in `tmp/gallery_preview_review/`.
3. A first assembly step that joins the base table with itself is skipped silently ("redundant init", `data_assembler.py`): keep it, or fail with a plain message (recommended: fail). Evidence: JOIN-KEY-TYPES-1 in `tasks.md`; `libs/transformer/tests/test_join_key_types.py` records today's behaviour.
4. TEMPLATE-KEY-TYPE-1: `templates/complex_template` declares `sample_id` as Float64 on both sides. DOC-JOIN-CAST-1: the rule file (`.claude/rules/rules_agent_role_bioscientist.md` line 144), ADR-050 (needs a superseding ADR; ADR text is `opus/high`) and `data_contract_rules` section 13 still describe the removed automatic cast.
5. Older open points in `tasks.md`: `beeswarm_sina`, the empty Blueprint draft, three old scripts, three ID-reconciliation defects, the scope of RECIPE-WORD-1, String or Categorical in recipes.

**HOME**
6. N9: VizFactory `in` / `not_in` compares as text, so on a numeric column `in [90.0]` gives no rows in the plot while the table keeps them. Options: approve the small fix now (coerce, then `is_in`, as the engine does; it changes plots with numeric `in` filters), or wait for FILTER-DTYPES-1. Evidence: 4 strict xfail cases in `app/tests/test_filter_int_equivalence.py`.
7. N12: what blocks the HOME rebuild: see the section "HOME: what blocks the rebuild" below.
8. N13: a drop and a filter on the same column at one node. The HOME view (`audited_frame`) runs all filters before all drops; the exported recipe keeps the recorded order and stops with "column not in the table". Options: refuse such a step, or define the order. Evidence: TEST-ORDER-1, checked by running; not tested yet.

**Recipes and joins**
9. N1: the join key rule is in three places: the build (`DataAssembler._check_join_key_types`), the Blueprint preview (`check_join_keys` in `join_designer.py`) and the checker (`join_key_problems` in `libs/utils/src/utils/recipe_check.py`). They are kept in step by a parity test only. Options: keep the copies with their parity tests, or one pure rule in `libs/utils` called by all three.
10. N5: confirm that the checker refuses at load (J10) a join key not declared in `input_fields`. It mirrors the build, because the ingestor imports only the declared columns when `input_fields` is not empty. Same question as N1.
11. N7: the tier-3 reader (W10) needs HOME's P5 mechanism spec and the order of change R1 (`.claude/design/recipe_format_spec.md` line 173); `beeswarm_sina` waits for it. Options: not recorded in the progress file.

**Gallery**
12. N3: a read-only gallery folder. The start check cannot rewrite the index (status `not_writable`), so a failing example that is listed in the old index is still shown; the only trace is a console warning. Options: keep; or leave failing examples out in memory (`bootloader.rejected_gallery_examples`). Evidence: `app/modules/gallery_examples.py` (`check_gallery_at_start`).
13. N4: what the user sees for an example left out at start is not specified (spec section 9). Today: left out of the index, the reason is in `metadata.rejected`, a console warning, no screen element. Options: not recorded in the progress file.
14. N15: `submit_example` (`libs/viz_gallery/src/viz_gallery/gallery_manager.py` 163-203) has no caller outside the tests. Q3-GALLERY-SUBMISSION-1 left it in place (it writes a gallery bundle); N15 asks again: keep, or delete. Its `@deps` block is inaccurate.

**Export**
15. N10: the reproducibility export writes the filter value as text, so re-running it on a number column fails with `ComputeError cannot compare string with numeric type`. Options: approve EXPORT-FILTER-VALUE-1 (it edits the frozen `libs/blueprint_arch/src/blueprint_arch/t3_translator.py`, about line 127; build brief S4), or leave it. Fix proposed by the reviewer: the translator writes the value through `utils.filter_values.coerce_filter_value` with the stored dtype. Evidence: 12 strict xfail cases in `app/tests/test_filter_int_equivalence.py`.
16. N11: `between` has no translation in `t3_translator` (UntranslatableNode). Options: add the translation later, or keep refusing it.

**Tests and audits**
17. N6: AUDIT-REPAIR-1: for the four old words (`persona`, `manifest`, `profile`, `project`) and one UML tag, fix the text or adapt the exclusions. `recipe` waits for RECIPE-WORD-1. Evidence: `assets/scripts/audit_old_words.py --check`, `assets/scripts/audit_uml_model.py`.
18. N14: TEST-ORDER-1 tests not written yet: where the audit writes a step (P5), the key of T3 and the per-collection key (P4), and property tests with `hypothesis` (a new dependency, D9). They depend on the unconfirmed stage-2 spec v0.1. Options: confirm the spec and allow the dependency, or leave those tests out.
19. N16: `audit_uml_model.py` reports 6 violations in PKG-TIERS of `docs/UML/app.mdj`: five missing arrows (from `assets/scripts` to transformer, utils, viz_factory and viz_gallery; from `libs/test_lab/pyproject.toml` to utils) and one stale arrow (transformer to ingestion). Not new (no importing file gained an import in this session). A UML edit needs Eve's yes. Options: not recorded in the progress file.

## Handoff 2026-11-15 08:45 (coordinator): Eve's decisions of this morning, what is built and in review

**Decisions (Eve, 2026-11-15, channel M80 to M82):**
- Seed: fixed at 0 by default; HOME draws no seed per session; the export uses the recipe's seed.
- Categorical: the standard follows Polars; `Categorical` and `String` are both usable (DEC27 is a refactoring choice only). Shipped recipes change only after the scientist list is shown to Eve.
- `polars_join_where` is renamed `modif_join_where` (DEC31, DEC32).
- Ties in `top_k` / `bottom_k`: inform the user; warnings clearly distinct from errors; test what Polars does first.
- The 64-bit sum: scientist's feedback only, low priority.
- Empty `polars_select` `exprs`, `polars_unpivot` `on`, `polars_top_k` / `polars_bottom_k` `by`: refused with the reason.

**New question for the panel (no build):** a restricted, structured Python file and back to a recipe (PY-RECIPE-1).

**State (2026-11-15 08:45):**
- HEAD `293d9c39`, not pushed (origin/dev `f769c8dd`).
- Builders running: `task/seed-holds` (fixes), `task/typed-values` (additions after a review that said merge), `task/row-order`.
- In review: `task/viz-params` (V3), `task/viz-errors` (V6, V7).
- Panel round 5 running (brief `tmpAI/panel/brief_round5.md`).
- Next: merge seed-holds, then typed-values; the full controls; push dev; then PLOT-TABLE-ORDER-1 and V4.
20. N17: `.claude/rules/rules_verification_testing.md` section 8: add `--durations=10` after `-q` in the browser command, and correct "about 4 minutes" (the gate took 8 min 13 s). It is a rule file: Eve's double confirmation.

**Blueprint**
21. N2: `except Exception` in `_jd_run_preview` (`app/handlers/blueprint_handlers.py`, about line 2060) shows any programming error as "Preview failed: ...". Options: leave; or catch only the expected errors and let programming errors through.
22. N8: the Blueprint package (W14): `tasks.md` (line 82) says Blueprint is not touched now; the night handoff listed it as next. Eve (2026-11-14): Blueprint and Test Lab can wait. Decide when W14 starts. Options: not recorded in the progress file.

**HOME: what blocks the rebuild (N12 in full)**
- NA-RULE-63 (#63): the NaN rule and the count message. The rule is in `.claude/design/home_audit_steps.md` section 19; Eve confirms it (`tasks.md`, NA-RULE-63).
- STAGE2-SPEC-1: Eve reads and confirms the v0.1 mechanism spec, `.claude/design/home_stage2_mechanism_spec.md`.
- KEYS-NODE-1: Eve confirms the hash model (`.claude/design/home_evidence/home_hash_model_2026-11-12.md`, section 4).
- RECIPE-GRAPH-UTILS-1: option C+. `utils.recipe_graph` and `utils.node_keys` do not exist yet (checked by the scout).
- HOME-DESIGN-REVIEW-1: items SC1, SC2, SC4, AR4, SC5, AR2, AR1.
- FILTER-UNIFY-1: three filter implementations (`modif_filter`, `t3_audit_engine._apply_filter_rows`, the filter loop in `VizFactory.render`); a design decision for Eve.
- FORMULA-SAFETY-1.
- Tasks that wait for these: FILTER-DTYPES-1 (after NA-RULE-63), HOME-EXPLORE-2 (#61, after RECIPE-GRAPH-UTILS-1), HOME-EXPLORE-4, -5 and -6 (#56), AUDIT-VIEW-1, AUDIT-RAWYAML-REMOVE-1, TEST-SHAPES-1 (waits for RECIPE-TESTS-1).

**Next for the coordinator, in order** (after Eve's answers; her priority: HOME first, then Gallery; Blueprint and Test Lab last):
1. HOME: EXPORT-FILTER-VALUE-1 (needs Eve's yes to edit the frozen `t3_translator.py`); N9; NA-RULE-63 (#63) after her answer on the NaN rule and the count message; then FILTER-DTYPES-1; the rest of P0 (TEST-SHAPES-1 waits for RECIPE-TESTS-1); P3 and P4 after her reading of the stage-2 spec, the hash model and option C+.
2. IMPORT-PATH-1 with SOURCE-LOOKUP-ONE-1, after her answer to point 1: one `builder` at `sonnet/high`, continued in worktree `agent-abd52719502485bdb` (merge `feat/recipe-format-1` into it first), then `reviewer`, merge, controls.
3. Gallery: her choices N3, N4 and N15, the eight previews, `beeswarm_sina` (tier-3 reader W10, N7).
4. Later: RECIPE-DOCS-1 (#79), the ADR-100 draft (W12, `opus/high`), AUDIT-REPAIR-1 (N6, N16), BP-VALIDATE-1 and the Blueprint package (W14), the DOC-JOIN-CAST-1 rule and ADR parts.

**Small tasks found, not done:**
- The import test leaves an empty `assets/test_data/_imported/` folder (IMPORT-TEST-CLEANUP-1 in `tasks.md`).
- The one `audit_docs_sync` violation (DOCS-SYNC-IDRECON-1 in `tasks.md`).
- Two sentences of `.claude/design/recipe_format_spec.md` (near lines 380 and 683) still describe the removed REMOVE-CATEGORY-SELECT-1 feature as present.
- The checker flags a missing schema `description` (S04, severity A, `libs/utils/src/utils/recipe_check.py` about line 281). The authoring page does not mention it. Not checked whether "A" is a warning.

**Not started on purpose** (quota and Eve's priority): the ADR-100 draft (W12, `opus/high`); BP-VALIDATE-1 (Blueprint); RECIPE-DOCS-1 (#79, large); AUDIT-REPAIR-1. Blueprint and Test Lab wait (Eve, 2026-11-14).

**Worktrees:** all task worktrees and branches of this session are removed. `agent-abd52719502485bdb` is kept (no code; the findings note of IMPORT-PATH-1).

## Corrections 2026-11-14 (records check)

Earlier lines above are not edited; where they disagree with the following, the following (dated later) holds.
1. Lines 665 and 745: NA-RULE-63 is DECIDED 2026-11-14 (channel M65, `tasks.md:38`), not waiting. The hash model (KEYS-NODE-1) was decided 2026-11-12 (`home_hash_model_2026-11-12.md` section 5). "Option C+" is superseded by DEC23 (`tasks.md:48`). HOME-DESIGN-REVIEW-1 (also line 746) has one open point: SC4, which samples the selector finds (`tasks.md:74`).
2. Lines 668 and 728 (N10): the reproducibility export writes the filter value as the panel stored it and drops `dtype`. A number box stores a number and that export works; the failing values come from the multi-select box (a number column shown as discrete, a Date, a Boolean) and from hand-written values (`tasks.md:43`).
3. Line 706 (IMPORT-PATH-1): Eve's principle is decided (option A, as production); the mechanism waits (`tasks.md:178`).
4. Lines 673 and 725 (N15): decided, `submit_example` stays (`tasks.md:200`).
5. Lines 620 and 739 (N8): Eve 2026-11-14, order HOME, then Gallery, Blueprint and Test Lab last (line 751 of this file). The "Next (c) the Blueprint package" of the night handoff is superseded. The pointer "`tasks.md` (line 82)" is now line 87.

## Handoff 2026-11-14 23:50 (coordinator, after the usage-limit stop): what runs, in which worktree, what is next

**(a) How to restart**
- A Fable session types `-coordinate` (CLAUDE.md section 4.3), then reads this section, `tmpAI/coordinator/progress_2026-11-14_session3.md` (the "STATE OF THE DAY" block at its top) and `tmpAI/agent_channel.md`.
- A stopped worker is continued by a new agent of the right model in the SAME worktree. Each worktree keeps `tmpAI/progress.md` (done, next, findings). Never resume a Fable agent.

**(b) Git**
- Branch `feat/recipe-format-1`, HEAD `55e578f5` (CLAUDE.md section 2.1, standing rules of the coordinator, and the guard hook).
- `origin/dev` = `edd96ee7`; controls passed there.
- Merged into `feat/recipe-format-1`, NOT pushed, NOT yet through a control run: `51ce0e9e` (decision documents in `.claude/design/decisions_2026-11-14/`), `70b01370` (HOME plot check, V5), `af5560a9` (join flags J12, J13), `55e578f5` (CLAUDE.md and hook).

**(c) Running** (the hash in brackets in the state block is the agent id, not the last commit; the last commit is not recorded there)
- `.claude/worktrees/na-rule-b`, branch `task/na-rule-b` [agent 22a0dc14]: NA rule part 2 BUILT; reviewer resumed (four-way equality, mutation checks, the rule-file edit must leave the branch).
- `.claude/worktrees/agent-abd52719502485bdb`, branch `worktree-agent-abd52719502485bdb` [agent aa26ce6b]: import "as production" BUILT and reviewed; FIX FIRST: Blueprint Validate must pass `imports_dir`; fix builder resumed.
- `.claude/worktrees/gallery-flags`, branch `task/gallery-flags` [agent 26c40302]: gallery flags BUILT and reviewed; FIX FIRST: browser test staging a broken example, a line for status `failed`; fix builder resumed.
- `.claude/worktrees/adr-sync`, branch `task/adr-sync` [agent aa16979a]: ADR update BUILT and reviewed; FIX FIRST: ten corrections in `tmpAI/panel/adr/review_corrections.md`; builder-opus correcting.
- `.claude/worktrees/polars-rows`, branch `task/polars-rows`: deferred Polars actions, group rows; builder sonnet/high, building.

**(d) Next, in order**
1. Merge each of the four after its fix and review; the reviewer runs headless, golden baseline and the browser gate on the merged tree; push `dev`; scribe updates handoff and tasks.md.
2. After `na-rule-b` is merged (same files): one builder for Q9 Option 1 and the operators; one builder for the seed (the recipe's seed holds, one seed everywhere, export uses and records the seed shown, a test per place); then PLOT-TABLE-ORDER-1 (recording guard, plot follows table, check at export).
3. Polars batch: `polars-aggs` (sum, min, max, mean, median, std, var, quantile, count, null_count, first, last) and `polars-time` (rank, join_asof, join_where, group_by_dynamic, rolling), each in its own worktree, one new module per group.
4. Viz plan step 2 (registry field, plot_engine read, shared parameter module to utils) AFTER the Polars batch (same file `polars_calls.py`).
5. Scribe: memory addition (`tmpAI/coordinator/memory_addition.md`) into the memory file; spec catalogue rows J12 and J13; changelog note "old imports must be imported again".

**(e) Decided by Eve on 2026-11-14 (evening)**
- No silent error. The recipe is the scientific document: a seed fixed in it holds; an audit-pinned seed is the same everywhere and is tested.
- V1 to V10 of the visualisation plan accepted as recommended.
- Every engine operator is offered in HOME; `between` is kept with its four `closed` values.
- The filter value is typed at the source: the panel stores the real value from a map of shown text to value; the engine stays strict; the checker checks the value type; old audit nodes are typed at export; the UI shows the column type.
- Audit removal goes back and forward in the lineage and the user chooses; exploration acts on the data viewed.
- The frozen files `t3_translator.py` and `export_handlers.py` may be edited through a builder for the NA rule, the seed and the operators.
- The deferred Polars actions start now.
- The ADRs follow the latest decisions.
- The coordinator never edits a file.

**(f) Open for Eve** (one at a time, through the review session)
1. Self-join: refuse, or run as written (built: runs with the advice).
2. `categorical`.
3. Seed when the recipe writes none.
4. Blueprint authoring tier 3.
5. Show all advices, or only J12 and J13.
6. The rule-file diff of NA part 2.

**(g) Where the documents are**
- `.claude/design/decisions_2026-11-14/` (proposals, visualisation plan, evidence).
- Working copies in `tmpAI/panel/`; progress in `tmpAI/coordinator/progress_2026-11-14_session3.md`.

## Handoff 2026-11-15 00:15 (coordinator): merged and pushed, what runs, what is next

**(a) Pushed**
- `origin/dev` = `62e0cc0c`, after the full controls: headless 4017 passed, 22 xfailed; `test_empty_data_analysis_recipe_startup` passes on the real tree; golden result-identical; browser gate 73 passed, 3 skipped; audit_docs_sync 0; cross-lib pass; check_doc_links 50 problems (3 more than before: to find and fix).

**(b) Merged since the handoff of 23:50** (into `feat/recipe-format-1`)
- records `a625fc63`
- gallery flags `ffe10199`
- ADR log `df1a31fa` (ADR-100 to ADR-106; change list `.claude/design/decisions_2026-11-14/adr_sync_changes.md`)
- import as production `62e0cc0c`
- Polars row actions `da74b373` (NOT pushed yet)

**(c) Running** (worktree and branch)
- Second review of `na-rule-b`, branch `task/na-rule-b`, worktree `.claude/worktrees/na-rule-b`.
- Review of `polars-aggs`, branch `task/polars-aggs`.
- Builders: `polars-time`, branch `task/polars-time`; `seed-holds`, branch `task/seed-holds` (SEED-HOLDS-1).

**(d) Next, in order**
1. After `na-rule-b` is reviewed: a builder merges `feat/recipe-format-1` into the worktree (conflicts expected in `home_theater.py` and `data_analysis_recipe_validator.py`) and runs the suites; then the coordinator merges.
2. Q9 Option 1 and the remaining operators (one builder); PLOT-TABLE-ORDER-1.
3. Viz plan step 2, after the Polars batch (same file `polars_calls.py`).
4. Clean-up: the "41 actions" counts (now 51 and more), the 3 new doc-link problems, changelog note on old imports ("must be imported again").

**(e) Open for Eve**
1. A same-key self-join: runs with an advice today, or refuse.
2. `categorical`: DEC27 refuses it; the code and the shipped fields keep `Categorical`.
3. The seed when the recipe writes none.
4. Whether Blueprint may author the plot entry's tier 3.
5. Show all checker advices, or only those that can change a result.
6. Ties in `polars_top_k` and `polars_bottom_k`, and `polars_head` after a step with no promised order: advice only today, no decided rule.
7. The one-line rule-file edit of `ui_implementation_contract.md` section 8, in branch `task/na-rule-b`.
8. Aggregating a table that holds a text column gives a missing value and no message (Polars' behaviour).

## Handoff 2026-11-15 01:06 (coordinator): the Polars actions and the NA rule are merged and pushed; what runs; what is next

**(a) Pushed**
- `origin/dev` = `f769c8dd`, after the full controls: headless suite 4935 passed, 22 xfailed; golden baseline result-identical; full browser gate 74 passed, 3 skipped; audit_docs_sync 0 violations; cross-library audit PASS; check_doc_links 50 problems (none in the ADR log, this handoff, the action page or the library READMEs).

**(b) Merged since the handoff of 00:15** (into `feat/recipe-format-1`)
- Polars table aggregations `4644a9ea`
- NA rule part 2 `4674b604`
- Polars rank, as-of join, join on conditions and time windows `f769c8dd`
- The registry holds 68 actions.

**(c) Running** (each in worktree `.claude/worktrees/<name>`, branch `task/<name>`)
- `seed-holds`: SEED-HOLDS-1.
- `viz-field-engine`: VIZ-STANDARD-1 step 2 (the field exact / modified / own on every plot component; the factory refuses an engine it does not implement).
- `typed-values`: EXPORT-FILTER-VALUE-1 and OPERATORS-SCREENS-1 (the filter value typed at the source; every operator in HOME).
- `cleanup-counts`: CLEANUP-COUNTS-1 (stated action counts, a test that gave false alarms in worktrees, the checker and empty lists, stale paths).

**(d) Next**
1. PLOT-TABLE-ORDER-1, after `typed-values` is merged (same files).
2. VIZ-STANDARD-1 steps 3 to 5: parameters read from plotnine; one strict rule set for layer parameters; tests driven by the registry, silent paths, one error form.

**(e) Open for Eve** (one line each)
1. A same-key self-join runs with an advice (built) or is refused.
2. `categorical`: DEC27 against the code.
3. The seed when the recipe writes none.
4. Whether Blueprint may author the plot entry's tier 3.
5. Show all checker advices, or only those that can change a result.
6. Ties in `polars_top_k` / `polars_bottom_k` and `polars_head` after a step with no promised order (advice only today).
7. `polars_join_where` fixes the order of its result because Polars gives none: `polars_` or `modif_` prefix.
8. The sum of a 64-bit integer column wraps around without an error (stated in the description, not checked).
9. A Polars panic while a plan runs is reported but cannot name the step.
10. Aggregating a table that holds a text column gives a missing value and no message (Polars' behaviour).
11. Comparisons on Date and Boolean columns in the HOME filter (options are being prepared).

## Handoff 2026-11-15 08:15 (coordinator): restart after the second usage-limit stop; what runs; what is next

**(a) Git**
- Branch `feat/recipe-format-1`, HEAD `b91a9fd5` (CLEANUP-COUNTS-1): a parameter may require at least one item; 40 actions refuse an empty list or mapping that would do nothing; the stated action counts follow the registry (68), with a test; tests that start the app in a subprocess use the sources of their own checkout.
- `origin/dev` = `f769c8dd`. `b91a9fd5` is NOT pushed and has had NO control run.

**(b) Running** (resumed at 08:07 after the stop at about 01:45; same agents, same worktrees; each worktree `.claude/worktrees/<name>`, branch `task/<name>`)
- `seed-holds`: SEED-HOLDS-1. Last commit c098f116, plus uncommitted edits in `plot_config_resolver.py` and `test_plot_seed.py` (fixes after review). Left: merge of feat into the worktree, then the suites.
- `typed-values`: EXPORT-FILTER-VALUE-1 and OPERATORS-SCREENS-1. Last commit 89043503 (review by a reviewer that breaks the code; that reviewer uses a temporary worktree `/tmp/claude-1000/old4674`). Left: the review result, the fixes, the merge.
- `viz-field-engine`: VIZ-STANDARD-1 step 2. Fix 6894208c; merge of feat 9c27174c committed in the worktree. Left: the suites after the merge.
- `rule-proposals`: the proposed changes of the stale rule files, for Eve's double confirmation. Last commit 21909669, plus one uncommitted proposal file. Left: the remaining rule files and the README. No rule file is edited.

**(c) Merge order and controls**
- When ready: `seed-holds`, then `typed-values`, then `viz-field-engine` (each has merged feat into its worktree). One branch at a time.
- A reviewer runs the FULL controls on the merged tree (headless suite, golden baseline, browser gate, audits, doc links). Push `dev` only after they pass.

**(d) Next, in order**
1. PLOT-TABLE-ORDER-1, after `typed-values` is merged (same files).
2. VIZ-STANDARD-1 steps 3 to 5: parameters read from plotnine; one strict rule set for layer parameters; tests driven by the registry; silent paths; one error form.
3. The export lines for `plot_engine` (two lines given by the viz builder).
4. A Polars panic names the step (pass a label from the orchestrator).
5. The migration tool refuses `replace_values` without columns, earlier.
6. Scribe: tasks, handoff, dependency index.
7. Panel round on the open questions (seed default, `categorical`, ties, empty values Polars accepts): no viewpoints started yet.

**(e) Open questions for Eve** (one at a time through the review session; full text: channel message M79 in `tmpAI/agent_channel.md`, and `tmpAI/panel/proposals_for_eve.md`)
1. The seed when the recipe writes none.
2. `categorical`: DEC27 against the code and the shipped fields.
3. The prefix of `polars_join_where` (it fixes an order).
4. Ties in `polars_top_k` and `polars_bottom_k`.
5. The 64-bit sum wrap-around.
6. Empty values that Polars accepts (`polars_select`, `polars_unpivot`, `polars_top_k`).
7. A same-key self-join: run with an advice, or refuse.
8. Which checker advices are shown (all, or only those that can change a result).
9. Comparisons on Date, Boolean and text columns in the HOME filter.
10. Small ones: `beeswarm_sina`, the complex template's data files, the orphan fragment, Blueprint's stale view, tier 3 in Blueprint.
11. The rule-file proposals (double confirmation).

## Handoff 2026-11-15 08:20 (coordinator): two merges, four builds running, panel round 4

**(a) Merged, not pushed.** No control run yet on the merged tree.
- `05a6fa30`: rule-file proposals. 16 proposals and a README under `.claude/design/decisions_2026-11-14/rule_file_proposals/`. No rule file was edited. A reviewer's verdict: "correct first", seven small corrections, being made now. Then they wait for Eve's double confirmation.
- `4525fcb1`: VIZ-STANDARD-1, parts V1 and V8. Every plot component carries `plotnine: exact | modified | own`. The factory refuses a `plot_engine` it does not build. Code in `libs/utils/src/utils/engines.py`. Second review: MERGE.
- `origin/dev` is still `f769c8dd`.

**(b) Running**
- `task/seed-holds`: SEED-HOLDS-1, fixes after review.
- `task/typed-values`: EXPORT-FILTER-VALUE-1 and OPERATORS-SCREENS-1, in review by a reviewer who breaks the code.
- `task/viz-params` (new): VIZ-STANDARD-1 step 3, V3. The shared parameter-reading module moves to `libs/utils`; a compare test; parameter lists read from plotnine with a hand overlay.
- `task/viz-errors` (new): VIZ-STANDARD-1, V6 and V7. Five silent paths become errors; one error form, `draw_checked`.

**(c) Panel round 4** (brief `tmpAI/panel/brief_round4.md`). The scientist, architect and user viewpoints reported on four open choices: the seed when the recipe writes none; the old type word `categorical`; row order with ties and position, and the prefix of `polars_join_where`; empty values Polars accepts and the 64-bit sum. The proposals go to Eve through session sparmvet-viz-57. Nothing is decided.

**(d) Next, in order**
1. Merge `seed-holds`, then `typed-values`.
2. A small builder for the export lines (`plot_engine`, `draw_checked`).
3. A reviewer runs the full controls (headless, golden, browser gate, audits, doc links); push `dev`.
4. PLOT-TABLE-ORDER-1, then V4, then V2 + V10 + V9.

## Handoff 2026-11-15 09:10 (coordinator)

**Merged, not pushed.** `d2c97bc6` (V3: the plot parameters of the exact components are read from plotnine). HEAD is not pushed; `origin/dev` is `f769c8dd`.

**Eve's decisions of 2026-11-15, one line each** (channel `tmpAI/agent_channel.md`, M83 and M84):
- 9: text greater/less not offered in the HOME filter (reversible); Date by date picker, Boolean by two-choice control.
- 10a: `beeswarm_sina` converted to the new form.
- 10b: small synthetic data made for `complex_template`.
- 10c: the three removed actions found out; the orphan fragment `ResFinder_Abromics_wrangling.yaml` converted, not deleted.
- 10e: Blueprint MAY author the plot entry's tier 3 (the note is in `recipe_format_spec.md` and at ADR-100).
- 10d (investigation, no build): Blueprint must open a failing recipe and show its fix list (BP-STALE-VIEW-1).
- 11 (explanation owed): list of every shipped-recipe result change, old vs new engine, in the changelog (RESULT-CHANGES-1).

**Strategy (Eve, M83 point 2):** builds on a recommendation are PROVISIONAL (recorded with the commit, reversible) when no result changes silently and nothing is hidden; open points go to her in ONE ordered list with a default each.

**Queue (build work that needs no decision):**
1. Seed branch: default 0, `geom_sina` seeded, seeds written, `beeswarm_sina` converted there.
2. Row order: ST13, then the tie and sum warnings.
3. viz-errors (after review).
4. typed-values (third review).
5. Export lines.
6. Full controls and push.
7. PLOT-TABLE-ORDER-1.
8. The warnings look.
9. FILTER-PICKERS-1, with the value list on demand.
10. RECIPES-SMALL-1.
11. V4.

**Records changed 2026-11-15 (not committed):** `recipe_format_spec.md` (tier 3 note); `architecture_decisions.md` (superseded markers at ADR-082, 093, 099; tier 3 note and RECIPES-SMALL note at ADR-100; filter-control note at ADR-104); `tasks.md` (FILTER-PICKERS-1, RECIPES-SMALL-1, RESULT-CHANGES-1, PY-RECIPE-1, BP-STALE-VIEW-1, SC4 and gallery-reason-list markers, process rule).

## Handoff 2026-11-15 09:20 (coordinator)

Records of this morning, by the review session (channel M85 to M88). Not committed; the records are in the main tree. Eve's decisions, one line each:
- **D22 (dated 2026-11-15):** yes, the formula allow-list as built (`fe856c26`) is accepted for now; FORMULA-SAFETY-1 and ADR-099 point 14 are closed as one decision.
- **D23 (dated 2026-11-15):** no time or size limit for formulas now; the known limit is stated in the docs.
- **Security rule (dated 2026-11-15):** two layers. In the app, nobody may misuse it to run anything but data science. At the deployment, who may deposit recipes and which options the user has is gated by the system; the app's checks do not replace that. Recorded in ADR-071; tasks DOCS-SECURITY-1 and SECURITY-REVIEW-END-1.
- **Gate gap (found by running, architect):** HOME's load gate runs once at startup; a recipe saved from Blueprint is not checked again. Task GATE-GAP-1 (queued; evidence `tmpAI/panel/round5/blueprint_failed_load/details.md`).
- **Blueprint with a failing recipe:** three places show the previous recipe with no message, one can freeze the session (the freeze was fixed with BP-UPLOAD-EXIT-1). Eve's choice open, L31: options A, B (recommended), C in BP-STALE-VIEW-1.
- **Equality check plan:** EQUALITY-CHECK-1, step 1 a dirty copy of the ST22 data and one hand-written recipe (PROVISIONAL, tests only), step 2 every action, step 3 all shipped recipes; evidence `tmpAI/panel/round5/equality_check/`. RESULT-CHANGES-1 dropped (Eve: "we want the results to be correct").
- **Scientist's two findings on the ST22 recipe (RECIPE-SCIENCE-1, Eve's choice L33 open):** the bars count gene rows (70) where the title speaks of samples (38); the inner join drops 4 of 42 metadata samples from the AMR table and 1 from the plasmid table with no message (JOIN-COUNTS-1 makes it visible).

**What runs:** the seed branch `task/seed-holds` (default 0, no per-session seed in HOME; the per-step seed field is with the panel); row order `task/row-order` with the warnings (`modif_join_where`, the four empty values refused, the position advice); `recipes-small` (RECIPES-SMALL-1). Reviews running: the viz-errors and typed-values branches, third round.

**Queue, in this order:**
1. GATE-GAP-1
2. EQUALITY-CHECK-1, step 1
3. export lines
4. full controls and push
5. PLOT-TABLE-ORDER-1
6. the warnings look (D36, D37; L8, L9)
7. FILTER-PICKERS-1, with the value list on demand (L10) and Time and Duration controls
8. V4
9. DOCS-SECURITY-1

Open for Eve (one number each in the channel list M86): L1 to L33; RECIPE-SCIENCE-1 and L31 (BP-STALE-VIEW-1) need her choice before their build.

## Handoff 2026-11-15 09:42 (coordinator): RESTART HERE (usage limit; next session 13:00)

**Git:** branch `feat/recipe-format-1`, HEAD `d6a2822a`. NOT pushed since `f769c8dd` (= origin/dev, the last tree with FULL controls passed). Merged on top, no control run on the merged tree yet: `b91a9fd5` clean-up, `05a6fa30` + `293d9c39` rule-file proposals, `4525fcb1` viz V1 + V8, `d2c97bc6` viz V3, `efcce204` typed filter values + all operators, `d6a2822a` template data + orphan fragment, and record commits. **No merge into main. Push dev only after a reviewer's FULL controls pass (headless, golden, browser gate, audits, doc links).**

**Worktrees, each with `tmpAI/progress.md`; continue each with a NEW agent of the same kind in the SAME worktree (first `git status`, `git log -5`, read its progress note):**
1. `.claude/worktrees/seed-holds` (`task/seed-holds`, builder sonnet/high). Fix round after review is DONE and merged with feat. RUNNING when the session stopped: Eve's DECIDED 1: HOME draws no seed, default 0 everywhere; `geom_sina` seeded (it was not); `random_state: 0` written in gallery `jitter_strip` and ST22 `phenotype_genome_length_dotplot`; `beeswarm_sina` converted (10a); the audit pin listed in the audit trail text; PROVISIONAL S1 (`random_state: null` refused) and S3 (`plot_defaults: random_state`), each its own commit. Then: review (reviewer breaks the code), merge.
2. `.claude/worktrees/viz-errors` (`task/viz-errors`, builder sonnet/high). V6 + V7 built; review = FIX FIRST; fix list sent (blocker: `home_theater.py:550` reads a reactive value in `session.on_flushed`: alert lost, other plots blank, Export panel empty; export `_ERROR.txt` and `report.qmd`; `ggtitle`/`xlab`/`ylab` missing text; `guide_label` options; printed-only warnings to the Alerts; the theme drop on `virulence_bar`: complete theme replaces, partial setting adds; list every shipped picture that changes). Then: second review, merge.
3. `.claude/worktrees/dataset-tier2` (`task/dataset-tier2`, builder-OPUS high, one opus at a time). RECIPE-DATASET-TIER2-1 (issue 77, decided 2026-11-12): a table plotted directly runs its own tier 2; shipped tables/pictures change by decision (`ResFinder` / `amr_heatmap`); baseline regenerated only for those; changelog. Then review, merge.
4. `.claude/worktrees/row-order` (`task/row-order`, builder sonnet/medium). Review: MERGE everything EXCEPT 6b189414. TO SEND to a builder there (NOT yet sent): (a) the `validate` pre-check gives FALSE REFUSALS (45 of 20000 random cases: `how: inner` with an empty table; Polars accepts) and misses right/full/semi/anti: redesign as "diagnose on failure": Polars decides whether the join fails; only when Polars raises is the plain message built (step, tables, key, what `validate` asked, an example, the fix); test against Polars on random cases incl. empty tables; (b) wrong statements to correct in the description and in ST14: "Polars keeps the first tied rows on a small table" is NOT true (114 of 200 cases differ on 20-row tables); "in streaming the kept rows differ from run to run" was NOT reproduced: say only "which tied rows are kept is not fixed"; "a NaN comes first" is wrong for `bottom_k` (last); (c) ST15's text names its blind spots (a sum in a formula, a join result). Then a short second review, merge. NOTE: my channel M85 passed the scientist's "first tied rows on small tables" and "streaming differs" to Eve: CORRECT IT on the channel (not yet done).

**Eve's decisions NOT YET RECORDED in tasks.md / ADRs (channel blocks M87 to M90 from sparmvet-viz-57; a scribe was dispatched at 09:42: check `git status` for its uncommitted edits and commit by file name):** D7 one join-key rule in `libs/utils` (JOIN-KEY-ONE-1, after row-order merges; her principle: one source of truth everywhere); D8 never skip a join silently, a self-join runs with a clear WARNING, a data-scientist viewpoint says whether any self-join case should be an error (no build of an error before her answer); D13 Blueprint join preview catches only expected errors (early); D10 template key to String + the float-key advice (exists: J13); D14 ALL old words corrected in every active file and the docs (scout lists hits per word first; propose exclusions for current vocabulary); D15 wait for the stage-2 spec; D16 correct the six arrows of the UML package diagram PKG-TIERS (StarUML open, native API only, then `audit_uml_model.py`); D17 YES to the two-line edit of `rules_verification_testing.md` section 8 (`--durations=10`, the true duration): her confirmation is given, a builder may edit that rule file for exactly this; D24 rule files updated to the current format: verify each statement against the code, ask only what no file answers, prepare the diffs; D26 scout first, then remove the two helper scripts and their docs if nothing calls them; D27 FIX NOW `agent_tools.py:202` (`get_field_contract` returns the removed `output_fields`), with a test; D28 a reviewer verifies the two doc statements, a builder corrects. D12 NOT decided: she read "filters" as interaction: tell her in one plain sentence that G-b is a read-only message under the taxonomy explorer listing the examples left out with the reason, no interaction, and say whether the taxonomy explorer itself was touched (have an agent check). Not answered: D11, C10, C11, Q7/Q8 (= D35 partly answered by D8, D36, D37), L1 to L4 (Categorical), S1 to S3 (seed; S1 and S3 are being built as PROVISIONAL).

**Builder queue after the four worktrees (max 3 builders; opus one at a time):** GATE-GAP-1 (defect) -> EQUALITY-CHECK-1 step 1 (PROVISIONAL, tests only) -> D27 + D13 (small, Blueprint) -> JOIN-KEY-ONE-1 -> export lines for `plot_engine` -> FULL controls + push dev (as soon as seed, viz-errors, row-order, dataset-tier2 are merged) -> PLOT-TABLE-ORDER-1 -> FILTER-PICKERS-1 (date picker, Boolean two-choice, Time, Duration; value list on demand) -> warnings look (D36, D37, PROVISIONAL) + JOIN-COUNTS-1 -> FILTER-UNIFY-1 -> V4, V2 + V10, V9 -> D14 old words -> D26 -> DOCS-SECURITY-1 -> formula follow-ups -> D16 UML -> D17 rule-file edit -> RECIPE-SCIENCE-1 after Eve's answer (L33).

**Read-only work ready to start:** data-scientist viewpoint on self-join use cases (D8); a scout for D14 (hits per old word) and D26 (callers of the two scripts); a reviewer for D28; a check of the gallery G-b sentence (D12).

**Channel:** my last messages M83 to M88 and M90 hold the findings and THE ONE LIST (M86, L1 to L33). Owed to sparmvet-viz-57: acknowledgement of its M87 to M90; the correction on ties; typed-values and recipes-small merged; three small choices from the fragment conversion (five more fragments included by nothing: delete, convert or wire; `gene` gives 13 rows, `[sample_id, gene]` gives 63 rows for the duplicate removal; wire the converted fragment into a recipe or not).
13:08: the session resumed; the stopped workers continue in their worktrees (seed-holds, viz-errors, dataset-tier2); row-order gets its fix when a builder is free.

## Handoff 2026-11-15 14:02 (coordinator)

**Facts (clock read 2026-11-15 14:02):**
- Merged since the restart, NOT pushed (origin/dev is `f769c8dd`); no control run on the merged tree yet.
- `eafc570c` RECIPE-DATASET-TIER2-1 (issue 77): a table that a plot reads directly runs its own tier 2; one function `utils.recipe_tiers.tier2_steps`. The ONLY shipped result that changes (Eve, 2026-11-12): the Result (T2) of `ResFinder` in `1_test_data_ST22_dummy` gains `total_gene_count` and a sort; the picture of `amr_heatmap` follows. A hand-written Polars reading equals the engine; golden baseline regenerated for those 2 records; changelog entry.
- `c442af4c` VIZ-STANDARD-1 parts V6 and V7: five silent paths of the plot factory are errors; one error form; a failed plot shows its message in its place and once in the Alerts, and no longer blanks HOME; the export says a failed plot was not drawn; a complete theme replaces a complete theme, a partial setting is added (`virulence_bar` follows its recipe, the only shipped picture that changes); a test renders the `yaml_example` of all 191 components. V1, V3, V5, V8 merged earlier; next V4, V2, V10, V9.
- Built, in review: `task/small-fixes` (D27 agent tool, D13 Blueprint join preview, D26 two helper scripts removed, D17 two-line rule-file edit, D10 test that no template declares a decimal join key, D28 two doc sentences, D14 old uses in two files).
- Being built: `task/seed-holds` (Eve's default 0: HOME draws no seed; `geom_sina` seeded; seeds written in recipes; `beeswarm_sina` converted; PROVISIONAL S1 and S3), `task/gate-gap` (GATE-GAP-1), `task/row-order` (third fix round: the `validate` message names the right join; numbering; tests).
- Known follow-ups, not built: TIER2-FOLLOWUPS-1 (tier-2 merge: false sentence in the exported report `export_handlers.py` about line 1507; `docs/foundations/data_tiering_adr.qmd` lines 29-32; test of the exported T2 of a schema; a JOIN's tier-2 list that no plot reads runs nowhere with no message; Blueprint's Live Data Glimpse shows T1 for every table) and VIZ-FOLLOWUPS-1 (viz merge: named palette `viridis` never applies, `scale_fill_viridis_d` does not exist in plotnine 0.15.4, `scale_fill_cmap_d` does; five facet components `facet_cols`, `facet_rows`, `facet_margins`, `facet_scales`, `facet_space` fail on their own example with a misleading message; `guide_label` cannot work, Eve's choice rebuild or remove; no test pins that the alert is written after the flush; the rule "a partial theme setting written BEFORE a complete theme is kept" is not in the docs, Eve to confirm; warnings are not written into the export bundle).

**Queue:**
1. Merge `task/small-fixes`, `task/row-order`, `task/gate-gap`, `task/seed-holds` as their reviews pass (each branch merges the main branch into itself first).
2. Then the export lines for `plot_engine`.
3. Then a reviewer runs the FULL controls (headless, golden, browser gate, audits, doc links); then dev is pushed.
4. Then TIER2-FOLLOWUPS-1, JOIN-KEY-ONE-1, EQUALITY-CHECK-1 step 1, the stage-2 spec brought to v0.2, PLOT-TABLE-ORDER-1, FILTER-PICKERS-1, the warnings look, VIZ-FOLLOWUPS-1 with V4.

Records: `tasks.md` marked RECIPE-DATASET-TIER2-1 done; VIZ-STANDARD-1 V6/V7 merged; TIER2-FOLLOWUPS-1 and VIZ-FOLLOWUPS-1 added; section 5 items D27, D13, D26, D17, D10, D28, D14 marked "built on task/small-fixes, in review". Nothing committed.

## Handoff 2026-11-15 18:45 (coordinator)

**Facts (clock read 2026-11-15, about 18:45; from `tmpAI/coordinator/progress_2026-11-14_session3.md`):**
- HEAD `fcae8d0c`, branch `feat/recipe-format-1`. NOT pushed. origin/dev is `f769c8dd` (the last tree with the FULL controls). No merge into main. The records below are uncommitted edits.
- Merged this evening, no FULL control run on the merged tree yet: `5598a7fd` JOIN-KEY-ONE-1 (one join-key rule in `libs/utils`); `839ffac3` the seven small fixes (D27, D13, D26, D17, D10, D28, D14); `c46cd11b` GATE-GAP-1 (HOME checks a recipe again when its files change); `fcae8d0c` VIZ-FOLLOWUPS-1 (viridis palettes, facets).
- Merged this afternoon: `eafc570c` and `ca0cdc75` (tier 2 of a table a plot reads directly, and J14); `c442af4c` the plot factory's error form; `be08b169` ROW-ORDER-1; `3eb954fc` EQUALITY-CHECK-1 step 1; `5e610429` the stage-2 plan v0.2.
- KNOWN DEFECT on the merged tree: `app/tests/test_join_preview_errors.py::test_a_broken_yaml_is_shown_as_the_recipe_problem_not_an_exit` fails. Two merged branches met: `small-fixes` catches the loader's `SystemExit` in the join preview; `gate-gap` made `cache_keys.load_data_analysis_recipe` raise a plain `ValueError`, which the preview's narrow list does not catch. Being fixed on `task/small-fixes-2`.
- Open worktrees: `seed-holds` (fix round after review: a layer with `stat: sina` unseeded; the seed in use shown beside the plot); `small-fixes-2` (BP-SAVE-TUPLE-1, STEP-NUMBERING-1; the fix above; then the full headless suite); `filter-pickers` (stopped early; to resume).
- Lesson: every merge was automatic, and this defect came from two clean merges. The FULL controls on the merged tree must run before more merges pile up.
- Records: `tasks.md` marked done JOIN-KEY-ONE-1, BP-PREVIEW-ERRORS-1, OLD-WORDS-1 (partly), HELPER-SCRIPTS-1, AGENT-TOOL-FIELDS-1, D10, D17, D28, ROW-ORDER-1, EQUALITY-CHECK-1 (step 1), VIZ-FOLLOWUPS-1; section 6 added with Eve's afternoon decisions (channel M94, M95, M97, M100). ADR-102, ADR-099 dated notes added.

**VIZ NIGHT QUEUE (no decision needed; one builder and one reviewer at a time; each: tests first, a mutation check by the builder and by the reviewer, the list of every shipped picture that changes):** done and merged: V1, V3, V5, V6 (five paths), V7, V8; in review: VIZ-FOLLOWUPS-1 (palettes, facets). Then: (1) V4: ONE rule set judges a layer's parameters (unknown, required, shape, allowed values) in the checker and in the factory; `allow_extra_params` removed; the hand widgets that are narrower than plotnine accepts corrected [sonnet/high, worktree `viz-v4`, after viz-followups merges]; (2) V2 + V10-B: a registry-driven test for every component (it renders; an `exact` one equals the direct plotnine call on the built layer data; the same input gives the same picture; a `modified` one states its change), then the 194 old test recipes, the dead integrity suite and the debug runners that no longer run are removed [sonnet/high, worktree `viz-tests`, after V4]; (3) V9-B: the list of plotnine objects registered and missing, generated; a test that reports new plotnine objects at an upgrade; `color` and `colour` both accepted in a recipe; the rule-file text as a PROPOSAL only [sonnet/medium]; (4) the export records and passes `plot_engine` (two lines; after seed and gate-gap are merged) [haiku/low]; (5) the plot's two remaining silent filter paths (an unknown column skipped, an unknown operator ignored: `viz_factory.py` about 194 to 260) become errors through the one filter rule [sonnet/medium]. KEPT OUT, they need her yes: the rule-file edit of V9; the ADR-036 reference (flag 4 of the plan); V1-C (prefix the 22 names that are not plotnine's); `guide_label` (N17); the theme order (N18); `stat_summary` `fun_y` (N28); the Blueprint form questions.

**HOME and recipe queue (decided; after the merges and the push):** PLOT-TABLE-ORDER-1; the warnings look + the self-join error and row counts (N3, N5, L32); the recipe overview in the right panel with the switch (N7(3)); RECIPE-FIXES by a data-scientist viewpoint then a builder (shipped pipelines: descriptions, N21 multi-resistance formula; gallery: every example in format 1 and rendered; the four fragments wired; the ResFinder piece per sample and gene, N9); OLD-WORDS agent (N12); the audit history log wording (N7(2)).

**QUEUE as slots free:** (1) scribe: record the merges and Eve's decisions (done in this section's records); (2) reviewer: S2-1 evidence (both orders); (3) builder `filter-pickers` (resume `a1e6cda8…`); (4) reviewer: HOME-STATE-PER-RECIPE-1 (filters and audit steps carried over between recipes: establish by running).

## Handoff 2026-11-15 19:10 (coordinator)

**Merged `de917267` SMALL-FIXES-2** (the record in `tasks.md`, section 6):
- Blueprint saves a multi-select value as a plain list (BP-SAVE-TUPLE-1; its xfail dropped).
- The wrangler and the upload report count steps from 1, like the checker (STEP-NUMBERING-1).
- Every YAML writer under `app/` and `libs/` uses the safe dumper and keeps key order (scan test `app/tests/test_writers_emit_format_one.py`).
- A recipe that cannot be loaded raises `RecipeLoadError(DataAnalysisRecipeError, ValueError)` (`libs/utils/src/utils/errors.py`, `app/modules/cache_keys.py`). This repairs `app/tests/test_join_preview_errors.py::test_a_broken_yaml_is_shown_as_the_recipe_problem_not_an_exit`, which failed on `c46cd11b`.
- Review: five mutations caught; headless 7024 passed, 13 xfailed; golden identical.

**Running:**
- The FULL controls on `de917267` (a reviewer, main tree). `dev` is pushed only on PASS (origin/dev is `f769c8dd`).
- Builders: `task/seed-holds` (fix round after review); `task/plot-table-order` (PLOT-TABLE-ORDER-1, PROVISIONAL S2-1).
- Stopped, to resume: `task/filter-pickers` (nothing committed).

**Open findings from the review:**
- (a) `app/tests/test_shiny_gate_gap.py::test_a_step_saved_in_blueprint_that_fails_the_gate_is_not_used_by_home` failed 1 run in 3 at line 77. Cause not established; being investigated with the FULL controls. Task GATE-GAP-FLAKY-1.
- (b) Three scripts in `assets/scripts/` write YAML with an unsafe or unsorted dumper, outside the scan: `migrate_plot_specs.py` (`yaml.Dumper`), `SF_create_data_analysis_recipe.py` and `debug_bootstrap_viz_yamls.py` (plain `yaml.dump`; the last sorts keys). Task SCRIPT-DUMPERS-1.
- (c) `assets/scripts/golden_baseline.py` on a broken recipe writes "SystemExit: 1" for it and exits 0. Task GOLDEN-BROKEN-RECIPE-1.

Records: `tasks.md` section 6 (three done lines, three open lines). No commit made here; the coordinator commits.

## Handoff 2026-11-15 21:11 (coordinator)

**State of `origin/dev`:** `060cee41` is PUSHED. It was pushed after the full controls passed on that exact tree:
- Headless suite: 7079 passed, 7 xfailed.
- Golden tables: result-identical.
- Browser gate: 72 passed, 3 skipped, 12 min 46 s.
- `test_shiny_gate_gap.py`: 5 runs of 5 passed.
- Docs sync: 0 in the main tree. Audit of imports between libraries: PASS.
- Doc links: 7 problems, all under `.claude/rules/` (known; the proposal is in `.claude/design/decisions_2026-11-14/rule_file_proposals/doc_links.proposal.md`).
- Not part of the set, and failing as on `f769c8dd`: `audit_old_words`; `audit_uml_model` (6 lines).

**Merged since the last handoff section:**
- `6d37e398` DOC-LINKS-FIX-1: doc links went from 50 (on `f769c8dd`) to 48, and now to 7.
- `060cee41` CONTROLS-FIX-1: the Blueprint agent adapter is built once at app start, in `app/src/main.py`. Cause: its synchronous probe ran inside a render, blocked the event loop, and the gate poll was cancelled. HOME keeps the notice of a replaced recipe until the user picks one or the recipe passes again (`follow_step`, `notice_after_pick` in `app/handlers/recipe_gate_handlers.py`).

**In work:**
- `task/plot-table-order`: fix round after review (two surviving mutations of the bundle; removal of `developer_raw_yaml` measured 42 rows against 22; the plot named in errors; S2-1 wording; the dialog).
- `task/seed-holds`: third fix round (`position: position_jitter` written as text was not found by the random-layer rule; the `plot_failure` form; seed 0 tests; a cheaper check).
- Stopped, to resume: `task/filter-pickers`.

**Measured durations (for the D17 lines of `rules_verification_testing.md`; a proposal, not an edit):** headless about 8 to 9.5 minutes (the rule says about 25 s); browser gate about 12 to 13 minutes.

**Records (records agent, 2026-11-15, for the coordinator to commit by file name):**
- `.claude/tasks/tasks.md`: new section 7 (Eve's decisions of 2026-11-15, evening, channel M101 to M129), the open tasks AGENT-PROBE-1, GATE-NOTICE-TESTS-1, DEP-INDEX-REGEN-1, RULE-LINKS-R1; GATE-GAP-FLAKY-1 marked done; AUDIT-RAWYAML-REMOVE-1 marked in work.
- `.claude/knowledge/architecture_decisions.md`: dated notes in ADR-104 (S2-1) and ADR-106 (V1-B).
- `.claude/design/decisions_2026-11-14/adr_proposals/audit_history_log.proposal.md`: the ADR wording for N7-2 (proposal, not in the ADR log).

## Handoff 2026-11-16 00:15 (coordinator)

**What you see first:** `origin/dev` is at `4f299025`, and it is pushed. The full checks passed on that exact tree.

**Checks on `4f299025`:**
- Headless tests: 7619 passed, 0 failed.
- Golden tables: identical to the reference.
- Gallery pictures: 34, identical.
- Browser gate: 72 passed, 3 skipped. Nine other browser files passed.
- Docs sync and the check of imports between libraries: pass.
- Doc links: 7, all in rule files (known).

**Merged since the handoff of 21:11:**
- `af4c44aa`: the list of every rule-file change (`.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md`, 128 rows).
- `653e70b1`: the seed build. Every seed that is used is written. HOME draws no seed per session. The seed in use is shown beside the plot. A refused seed names the plot, the layer and the fix. The whole-recipe seed and the audit pin stay PROVISIONAL.
- `806dc852`: the advice texts. Each advice says what happens, then "Suggestion:". Also the `top_k` text and the note on whole-number sums.
- `4f299025`: the recorded order. One function, `audited_frame` in `app/modules/t3_audit_engine.py`, serves the table, the plot, the bundle and the export check. A step that cannot be applied is refused. The step type `developer_raw_yaml` is removed. The filter dialog no longer offers a dropped column.

**In work:**
- `task/categorical`: the shipped `Categorical` fields (100 to `String`, 1 to `Enum`, 1 to `Float64`). In review.
- `task/viz-audit`: the audit of the plot components against plotnine, and the impact document of the rename. Corrections after review. Nothing is renamed.

**Stopped, to resume:** `task/filter-pickers`. Nothing committed.

**Files for Eve, not in git:**
- `tmpAI/panel/round7/questions_checked.md`: 33 questions checked against the records (6 decided, 15 to confirm by yes or no, 15 open). Section C is her list.
- `tmpAI/panel/adr/ledger.md` (column "taken by") and `tmpAI/panel/adr/taken_by_report.md` (6 points).
- `tmpAI/panel/round7/original_vs_audit_recipe.md`.
- `tmpAI/panel/round7/categorical_migration_list.md`.
- `tmpAI/panel/round7/advice_texts_before_after.md`.

**Records changed, not committed (records agent, 2026-11-16 00:15; the coordinator commits by file name):**
- `.claude/tasks/tasks.md`: section 7 (done lines), AGENT-PROBE-1 now a defect, eight new open tasks.
- `.claude/design/home_stage2_mechanism_spec.md`: the paragraph "Original recipe and audit recipe" added at the top.
- `docs/user_guide/audit_pipeline.qmd`: the same paragraph added.
- `tmpAI/agent_channel.md`: partly trimmed (2 coordinator blocks deleted; 7 candidates kept, the rest of the trim was refused by the permission check). List: `tmpAI/coordinator/channel_trim_2026-11-16.md`.

## Handoff 2026-11-16 02:55 (coordinator)

**What you see first:** `origin/dev` is at `78c620bf`, pushed. It holds the migration of the `Categorical` fields and the audit of the plot components. The full checks passed on that exact tree.

**Checks on `78c620bf`:**
- Headless tests: 7976 passed, 0 failed. Golden tables: identical.
- Gallery pictures: 34, identical.
- Browser gate: 72 passed. Eight other browser files passed.

**Pushed:** `78c620bf` (the `Categorical` migration, the plot components audit).

**Merged, NOT pushed:** `a386422a`, the filter controls by type of column (FILTER-PICKERS-1). The next push needs one full control run on the merged tree. Eight provisional choices wait for Eve.

**Branches in review,** each in its worktree under `.claude/worktrees/`:
- `task/smooth-formula` (HEAD `3527855d`): the security fix, five places closed (PLOT-TEXT-RUNS-CODE-1). The reviewer attacks it and establishes the facts on the export report (REPORT-TEXT-RUNS-CODE-1).
- `task/recipe-fixes` (HEAD `3805df49`): 37 step descriptions, false descriptions corrected, the first line of the multi-resistance formula with 16 of 38 samples before and after, one old file deleted, messages of declared types.

Order after the reviews: merge both; one full control run on the merged tree (filter controls, security fix, recipe fixes); push `dev`. No merge into `main`.

**For Eve, one file (not in git):** `tmpAI/panel/round7/FOR_EVE_one_list.md`. 34 points answered by yes or no; 41 points to choose, each with options and a default; 25 points that a record already answers are in its Appendix A with what is to build. Sources: `tmpAI/panel/round7/questions_checked.md`, `tmpAI/panel/adr/ledger.md` (column "taken by") and `taken_by_report.md`, `tmpAI/panel/round7/n7_4/result.md` and `points_checked.md`, `tmpAI/panel/round7/recipe_fixes/fix_list.md`, `tmpAI/panel/round7/old_words/replacements.md`, `tmpAI/panel/round7/s2_2/typing_at_reading.md` and `stat_summary.md`, `tmpAI/panel/round7/filter_pickers_points_for_eve.md`, `tmpAI/panel/round7/categorical_migration_list.md`, `tmpAI/panel/round7/original_vs_audit_recipe.md`. In git: `.claude/design/viz_rename_impact_2026-11-15.md`, `.claude/design/decisions_2026-11-14/rule_file_proposals/RULE_FILE_CHANGES.md`.

**Not started, in this order:**
1. The fix of the export report, if the facts confirm it.
2. The reading errors (the decided parts; READING-ERRORS-1).
3. The removal of all saved caches and sessions (CLEAN-SAVED-1; Eve's decision of 2026-11-15). It runs alone, when no test run uses the main tree.
4. "A recipe changed while in use" (S2-3-Q, an investigation).
5. The pictures of the recipe overview (three viewpoints; RECIPE-OVERVIEW-2).
6. Last: the audit of the state of the repository Eve asked for.

**How to resume after a usage-limit stop:** read the top block "LOG SINCE 18:03" of `tmpAI/coordinator/progress_2026-11-14_session3.md`. Continue each stopped agent by a message in its own worktree. Never two workers on one worktree. At most three workers at once.

**Records changed, not committed (records agent, 2026-11-16 02:55; the coordinator commits by file name):** `.claude/tasks/tasks.md` (EXPORT-RECIPE-REFUSE-1 rewritten as TO CONFIRM WITH EVE; FILTER-PICKERS-1 line; section 7 done lines; five new open lines at the end of the list).

## Handoff 2026-11-16 20:15 (coordinator)

**What you see first:** the branch `feat/recipe-format-1` is at `be47a357`, NOT pushed. `dev` on the server is at `78c620bf`. Nothing is merged into `main`. The push waits for two things: the self-join warning (the main line still holds the error that Eve decided against, D-0183), and one full control run on the merged tree.

**Merged on 2026-11-16 after `78c620bf`** (one line each, merge hash, what the user gets):
- `a386422a`: filter controls by column type (FILTER-PICKERS-1). Merged before 02:55, still not pushed.
- `dd6a9d2f`: see git log (the subject is not in the coordinator note).
- `472c0ff2`: recipe fixes. 11 false step descriptions corrected, 3 cut sentences completed, a test that every description is whole, checker advice D01.
- `f5f3618a`: see git log (the feature tip before the stale-keys fix was merged).
- `77b663f1`: see git log (base of the ledger tests and of the verification).
- `edfff765`: the intent document with Eve's correction of its first page; ledger lines D-0143 to D-0152.
- `7632f963`: `smooth-formula`. Export report text is made safe (no code runs from a title, label or reason); facets are drawn on the exact column name; a tip that starts with "Suggestion:" is shown as it is.
- `bb90db5c`: decision rules. The hook checks each brief for quoted decision lines; ledger lines D-0153 to D-0162.
- `42d66368`: ledger lines D-0177 to D-0181 (exploration filter reset, stage and version model, gallery preview command).
- `9a8e8917`: tests only. The nine hook tests follow the quote rule.
- `7ef46987`: `verif-fix-1`. The validator reports the Polars errors of a one-row run; an old action name is refused with "Suggestion: use <new>". It also adds the self-join ERROR (J15) that SELF-JOIN-WARN-1 undoes.
- `90971058`: ledger lines D-0182 to D-0186 (warning not error for self-joins; check when selected; check start at first load; changing data is not a failure, changing a recipe is).
- `42118164`: `recipe-small`. Eve's reason beside the multi-resistance formula; labels checked; 12 capital labels in the plot titles (PROVISIONAL until she confirms).
- `41071530`: `stale-keys`. A stored table is never served under an old key; a build tells the user, or refuses, when its inputs change during the build.
- `36fc906c`: `flake`. One strict-xfail test file for the Export panel reset. Diagnosis only, no fix.
- `be47a357`: `ledger-5`. Ledger lines D-0187 to D-0193 (the export logic of 2026-11-16).

**Running now:**
- SELF-JOIN-WARN-1: builder, worktree `.claude/worktrees/self-join-warn`, branch `task/self-join-warn`.
- Impact report for "a recipe is checked when it is selected": read-only reviewer, `tmpAI/panel/check_on_select/impact_report.md`.
- Parked: `.claude/worktrees/recipe-plots` (branch `task/recipe-plots`). Nothing written there.

**Files for Eve written today** (paths only):
- `tmpAI/panel/verification/SUMMARY_for_eve.md`: the verification batches 1 to 3 and their 17 questions.
- `tmpAI/panel/verification/SUMMARY_two_periods.md`: the 65 verification findings, sorted by period (before and after the coordinator start).
- `tmpAI/panel/verification/h1_filter_view_change.md`: the filter view check, with Eve's reset proposal against D-0019.
- `tmpAI/panel/verification/rule_edits_and_action_names.md`: the 67 old action names and the 15 rule-file edits.
- `tmpAI/panel/round7/FOR_EVE_still_open_2026-11-16.md`: every open point (191), blocks B1 to B13. B1 (the export) is now DECIDED in part.
- `tmpAI/panel/export_modes/export_modes_compare.md`: the export as built, against Eve's statement of 2026-11-16.

**The new rule for briefs** (since `bb90db5c`): every agent except scout, scribe and the panel agents needs a "Decisions" block. Each decision number must be followed by quoted words from its ledger line (D-0156, D-0159, D-0166). Only numbers taken by Eve and DECIDED count. A missing ledger refuses the call. Eve asked whether the hook must be so strict (M171 point D). No change to the hook until she answers.

**Next, in Eve's order:**
1. Merge the self-join warning (SELF-JOIN-WARN-1).
2. One full control run on the merged tree, then the push of `dev` (no merge into `main`).
3. The impact report, then the design for the check on selection (CHECK-ON-SELECT).
4. The proposals for one recipe on many datasets and sessions (SESSIONS-MANY-DATASETS).
5. The three viewpoint questions: audit steps between steps, the help button, the readable audit points file (VIEWPOINTS-O13-O14).
6. The UML tasks (UML-TASKS).
7. The demo recipe (DEMO-JOIN-1, D-0167).
8. Blueprint keeps comments (BP-COMMENTS-1, D-0174; the library question first).
9. The plain message for a missing column (MISSING-COLUMN-MESSAGE-1, D-0176).
10. The Export panel that resets on a plot tab change (EXPORT-PANEL-RESET-1; waits for her answer).
11. The swallowed errors in session, import and export (VERIF-FIX-2).

**Open choices that wait for Eve:** see `tmpAI/panel/round7/FOR_EVE_still_open_2026-11-16.md` and the five points of channel message M153 in `tmpAI/agent_channel.md`. The points are not copied here.

## Handoff 2026-11-16 23:45 (coordinator)

**What you see first:** `dev` on the server is at `93f39d24`. It was pushed at 23:36. That push was my error: I pushed before I read the review session's instruction "git local only tonight" (channel M193). I reported it in channel M161 (sent by the coordinator, sparmvet-viz-46). There will be no further push until Eve says so. Branch `feat/recipe-format-1` is at `93f39d24` plus local commits. Nothing is merged into `main`.

**Merged since the handoff of 20:15** (one line each: merge hash, what the user gets):
- `46fa84da`: ledger lines D-0194 to D-0197 for the audit dialog. Records only, no code.
- `11c7ca5e`: ledger lines D-0198 to D-0203 for the audit dialog (the three cautions, the second use case, the sentence for the docs, the typed value, the one-to-one warning). Records only, no code.
- `f3e5be86`: the branch `task/self-join-warn` brought up to date with `feat`. A branch merge; nothing new reaches the user until `93f39d24`.
- `93f39d24`: `task/self-join-warn` (`698fcdb4`) merged into `feat` and pushed to `dev`. The user gets: every self-join gives a warning with the rows before and after and the rows with a missing key, never an error. One function now writes every advice sentence ("what happens. Suggestion: ...").

**Running now (local only, no push):**
- Swallowed errors in session, import and export (VERIF-FIX-2): worktree `.claude/worktrees/verif-fix-2`, branch `task/verif-fix-2`, from `93f39d24`.
- Demo recipe that keeps every sample (DEMO-JOIN-1, D-0167): worktree `.claude/worktrees/demo-join`, branch `task/demo-join`.
- Parked: `.claude/worktrees/recipe-plots`. Nothing is written there.
- This section and section 8 of `tasks.md` were written by the records scribe RECORDS-1116-B. They are not committed yet; the coordinator commits them by file name.

**Files for Eve written since 20:15** (path, one line each):
- `tmpAI/panel/check_on_select/impact_report.md`: what checking a recipe when it is selected costs and changes; eight questions.
- `tmpAI/panel/sessions/PROPOSALS_for_eve.md`: one recipe on many datasets, and sessions with a comment; four questions.
- `tmpAI/panel/audit_model/scenarios_report.md`: round 1 of her audit scenarios, run on recipe 1 with the real engine.
- `tmpAI/panel/audit_model/scenarios_report_round2.md`: round 2: the lineage of a column, names and types per place, the 2002.5 case.
- `tmpAI/panel/audit_rules/PROPOSALS_for_eve.md`: three viewpoints on the audit rules, with options; six questions.
- `tmpAI/panel/dialog_preview/PROPOSAL_for_eve.md`: what the audit dialog can show while it is open; one question.
- `tmpAI/panel/audit_docs/intent_text_draft.md`: draft of the help text and the docs section for "the node you tick expresses the intent". Not in the docs yet.
- `tmpAI/panel/steps_position_help/PROPOSAL_for_eve.md`: whether an audit step may sit between the recipe's steps, and the help button; three questions.
- `tmpAI/panel/export_modes/export_modes_compare.md`: the export as built, against Eve's statement of 2026-11-16. This file is already named in the handoff of 20:15; it is not new since then.

**The one list of questions that wait for Eve:** channel `tmpAI/agent_channel.md`. Three coordinator messages (sender: sparmvet-viz-46) hold it. The review session also has messages named M157 to M161 in the same file; the ones below are the coordinator's.
- M157, points 1 to 15: 1 removal by condition or by sample ids; 2 "only the earliest ticked step writes it"; 3 the two intents at the top of the dialog; 4 the lineage of a column after a rename; 5 a decimal typed for a whole-number column; 6 rows with no value, one choice per place; 7 a removed sample shown as 0 in another table; 8 the numbers of the self-join warning do not reach the screen; 9 a recipe checked when it is selected (eight points); 10 one recipe, many datasets, sessions (four points); 11 the export (five points left); 12 the Export panel reset on a plot tab change; 13 the exploration filter on another table at the same stage; 14 the hook that checks the briefs; 15 small confirmations (the capital labels, the recipe in the export, nine rule-file edits).
- M158, point 16: the other plots and tables while the dialog is open (the order of four items; the table of rows that would be removed; other plots on a click; "no draft").
- M159, point 17: the help text (its length; "place" or "node"; "T1, T2, T3" or plain words).
- M160, point 18: an audit step stays at the end of its stage; the checker refuses an audit step not at the end; the help with one sentence and a "?".
- M161, point 19 (sent at 23:45): the self-join numbers; a cross join is refused for any table; two texts still describe the old self-join rule; the old-words check fails on every tree.

**Tonight's allowances from the review session (channel M193, M194; for tonight only):** up to 5 agents at once, one worktree and one branch per writer. Git is local only: no push until Eve says so. CLAUDE.md is not changed. On an automatic resume: read the progress note, the channel from M192, `git status` and `git worktree list`; continue the interrupted worktrees with new agents in the same worktrees; do not wait for Eve.

**Next, in order:**
1. Review and local merge of the two running branches (`task/verif-fix-2`, `task/demo-join`), with the full controls.
2. The new text for the export diagram and the UML tasks (UML-TASKS; EXPORT-MODES text).
3. The channel clean-up (CHANNEL-CLEAN): remove the messages that are fully recorded.
4. Then whatever her answers open.

## Handoff 2026-11-17 07:15 (coordinator)

**What you see first:** the branch `feat/recipe-format-1` is at `79cdeab5`. It is LOCAL: 25 commits ahead of `dev` on the server (`93f39d24`). Nothing has been pushed since 23:36 on 2026-11-16 (channel M193: git is local only until Eve says so). Nothing is merged into `main`. The full controls of the merged tree are running; their logs are in `tmpAI/controls_79cdeab5/`.

**Merged locally since the handoff of 23:45** (merge hash, what the user gets):
- `5c212b02`: the demo recipe keeps every sample. A sample with no MLST result shows "Non Determined" (D-0167).
- `79cdeab5`: errors that were swallowed in the session screen, the session files, the bundle import and the export are now told to the user (D-0050). A click on Restore restores once: before, it repeated without end, and the version on the server has the same defect. Apply pressed while a step has no reason no longer crashes and closes the connection.

**Open worktrees:** only `.claude/worktrees/recipe-plots` (parked, nothing written).

**Older defects found tonight, NOT fixed** (one line each):
- The Export panel is redrawn on every change of plot tab and resets what the user set.
- The report of an export links its figures to a folder that is not in the zip.
- A plot with no target table: its data and its plots are in two differently named folders, and the README names one.
- About 70 places where a failed read of a value the user set is silently replaced by the default (`safe_input`).
- The reason box read at Apply falls back to the old reason (`audit_stack.py:167`).
- Provenance fields of the export are dropped silently (`export_handlers.py:92-154`).
- The delete icon of an audit step and the Revert button are run by no test.
- After a failed "Delete all sessions", a locked session folder is half deleted.
- `recipe_gate_handlers.py:186` writes a notice inside an effect (no loop found).

**What waits for Eve:** the one list of 22 points. Channel blocks: M157 (points 1 to 15), M158 (16), M159 (17), M160 (18), M161 (19), M162 (20), M164 (21), M165 (22). The status block for her is M166.
1. removal by a condition or by sample ids
2. which ticked step writes a value (only the earliest one)
3. the two intents at the top of the audit dialog
4. the lineage of a column after a rename
5. a decimal typed for a whole-number column
6. rows with no value: one choice per place
7. a removed sample shown as 0 in another table
8. the self-join warning numbers do not reach the screen
9. a recipe checked when it is selected
10. one recipe on many datasets, and sessions
11. the export (five points)
12. the Export panel reset on a plot tab change
13. an exploration filter on another table at the same stage
14. the hook that checks the briefs
15. small confirmations (capital labels, recipe in the export, nine rule-file edits)
16. other plots and tables while the dialog is open
17. the help text (length, words)
18. an audit step at the end of its stage; the help with a "?"
19. self-join numbers, cross join refused, two old texts, the old-words check
20. the text of the export diagram
21. the demo recipe: two MLST-only samples, the label "Non Determined", the warning
22. when to push (default: wait)

**Files for Eve written since 23:45:**
- `tmpAI/panel/export_modes/EXP-MODES_new_text.md`: proposed text for the export diagram, with the points she must decide. No StarUML edit before her yes.
- `tmpAI/panel/verification/review_verif_fix_2_and_restore_loop.md`: the review of the swallowed-error fix and of the Restore loop (confirmed in a real browser).

**Next, in order:**
1. The result of the full controls on the merged tree.
2. Then nothing more can be built without her answers.
3. When she allows a push: read the channel first, then push `dev` only (the tree that passed the controls).

## 2026-11-17 13:30 (coordinator: state for the resume)

Written by a records agent from the progress block "RESTART HERE: UPDATE 12:10" (`tmpAI/coordinator/progress_2026-11-14_session3.md`), the reports named in it, and the channel blocks M200 to M207. Text marked **[coordinator's wording]** is not Eve's own words. Everything else is her words or a file read.

**State**
- Local `dev` = `8f951761`. It is 12 commits ahead of `origin/dev` (`36d1bd23`).
- The main folder is checked out on `dev`. Eve switched it herself.
- Eve pushes herself. The coordinator session cannot push (its permission check refused the push; channel M200). The review session pushed `36d1bd23` at Eve's instruction (channel M200).

**Merged today**
- LEDGER-8 (`5d3acf1d`): ledger lines D-0204 (pushes allowed), D-0205 (one common set of ids across the datasets of a recipe), D-0206 (remove the caches, re-run the odd results).
- `bf4b169e`: the tasks commit with four tasks. **[coordinator's wording: the four task names are not in this section; read the commit.]**
- DATA-IDS-FIX-1 (`8f951761`), decisions D-0205, D-0206, D-0167. What a user sees:
  - The demo join table (`demo_abromics`) has 27 rows for 27 samples. Before the fix it had 40 rows.
  - 12 samples have no MLST result. They stay in the table as "Non Determined" (D-0167).
  - The 3 metadata lines with no sample id are removed by the recipe with a warning, as before.
  - The MLST file has one row per sample and scheme (30 rows to 15). The ResFinder file (read by no recipe) holds only ids of the set.
  - A new recipe `left_join_lesson` is in the templates folder. It teaches what a left join does when the ids do not match. Its 2 foreign ids are its one named exception in the id test (channel M201).
  - `complex_template` holds one common set of ids (commit `5b7624e7`). Its left-join example moved to `left_join_lesson`.
- The generator: `assets/scripts/generate_demo_data.py`, seed 20261117 written in the code. The same seed gives identical files; another seed gives other bytes. It writes to `tmp/demo_data_generated` by default and does not replace files without `--overwrite`.
- The id test: `app/tests/test_recipe_data_one_set_of_ids.py` (14 tests). It fails, and names the file and the ids, when a table holds an id outside the set of the metadata, when the metadata repeats an id, or when a table with one row per sample repeats a (sample, scheme) pair.

**Controls on `8f951761`** (report `tmpAI/controls_8f951761/REPORT.md`; logs in the same folder; no tracked file changed, `git status` clean after the runs)

| Control | Result | Counts |
|---|---|---|
| 1 App import | OK | rc 0 |
| 2 Headless suite | pass | 9834 passed, 5 skipped, 15 xfailed (28 min 38 s) |
| 3 Golden baseline | pass | `result-identical` |
| 4 Gallery previews (compare mode, no `--apply`) | pass | 34 identical, 0 size only, 0 differs, 0 new, 0 error |
| 5 Browser gate (qa) | 1 failed in the full run | 71 passed, 3 skipped, 1 failed (10 min) |
| 6a audit_cross_lib | PASS | no violations |
| 6b check_doc_links | rc 1 | 7 problems, the same 7 as known, no new one |
| 6c audit_docs_sync | PASS | 0 violations |
| 6d audit_old_words --check | rc 1 | the same retired words and folders as the earlier log `79cdeab5`; "recipe" paths 92 to 93 (the new recipe) |

- The one failure is a known timing race, not a new defect: `app/tests/test_export_download.py:327`, `StopIteration`, in `test_the_export_records_the_seed_the_recipe_writes_and_writes_it_into_the_reproducibility_recipe`. Run alone: pass, pass. The three runs gave fail, pass, pass. It is not fixed.
- The 3 skips come from the skip conditions of the test files (for example "Blueprint requires developer or qa"). The report did not name them.

**Caches** (D-0206)
- 156 paths removed, 110,156,232 bytes (about 105 MB). All were untracked (under `tmp/` and `tmpAI/`). Details: `tmpAI/controls_8f951761/caches_removed.md`.
- Kept as "not sure" (not removed): `tmp/UI_TEST/user/_blueprint_drafts/76964f0f81b1_1_test_data_ST22_dummy.json` (a user draft, not a cache); other `tmp/` evidence folders; `tmpAI/panel/**`; other `tmpAI/audit_*` folders; the golden copies `tmpAI/golden_*.json`.
- Three left-over `shiny run` processes from old worktrees, still running, not stopped: pid 104136 (`recipe-small`, port 59197), pid 248767 (`self-join-warn`, port 59399), pid 1171940 (`verif-fix-2`, port 9819).

**Odd results, re-run on the new data** (report parts 3 and 7; verdicts against the id fix only)
- a. Demo join: 27 rows, 27 samples. Solved by the id fix. "Non Determined": 15 rows (12 without MLST, 3 with an unknown result). Consistent with the recipe text.
- b. Join cautions: none for any shipped recipe. A caution exists only for self-joins.
- c. Joins that lose samples: none. Samples before equal samples after, in every join.
- c. Joins where rows grow (rows before, then after each join; samples stay the same):
  - `1_Abromics_general_pipeline`, `AR1_MLST_Serotype_Virulence`: 42 to 984 (VirulenceFinder, left join), then 342 (APEC/STEC list, inner join).
  - `1_test_data_ST22_dummy`, `ST22_Anchor`: 42 to 74 (ResFinder), 74 to 1731 (VirulenceFinder), 1731 to 617 (APEC/STEC list).
  - `figshare_integration`, `figshare_triple_join`: 980 to 18,437 to 203,146.
  - Flagged, not decided. No recipe warns about it.
- d. Multiresistant count: the plot counts rows (46 of 70 rows; 16 of 38 samples). The recipe says it counts rows. Not a bug by the report's reading.
- e. Duplicate rows: the ST22 VirulenceFinder file has 583 rows in exact-duplicate groups. The recipe removes them before the join, so they do not reach the joined tables. But `ST22_Anchor` holds 14 identical rows (ResFinder gene hits listed twice), `QA_fanout_exhibit` 256, `QA_AMR_per_sample` 2, `Plasmid_Profile_Joint` 4. Plot `virulence_bar` counts the 14.

**Eve's answers today on the plot component rename**
Sources: the progress block (entry "EVE'S ANSWERS TODAY", 12:10; not yet in the ledger, LEDGER-9 owed), and channel M201 to M204 (not in the ledger either). Her words are quoted where the channel has them.
- Q1 (progress): (a) refuse an old bundle; no conversion. The message gives the commit, the choices and the contact. A helper that injects audit steps into a new recipe is deferred. The commit is the version for now.
- Q2 (progress): classify each of the 22 own components. Real: `plotnine_<real name>`. Modified: `modif_<real name>`. Composite: `step_`. Every `modif_` has its `plotnine_` original next to it.
- Q3 (progress and channel M201): "a) full parity": register the 30 plotnine objects.
- Q2 and Q8 (channel M202, her words): "a) yes; only functional modifications that are important could eventually be kept; so yes the recipes need to be adapted and then the components matched to plotnine defaults. Good catch." Recorded in the channel as: remove the shortcut components that an exact plotnine component already does; a component stays only if it is a functional modification that matters; list each one kept, with its reason, to her before removing it.
- Q4 (channel M203, her word "A"): register both spellings of the 15 pairs (for example `colour` and `color`), each exact and equal to plotnine; the picker shows one entry per pair; no silent conversion.
- Q5 (channel M204, her words): "A). But it needs to be tested thoroughly to ensure that this does work; if errors: investigate and propose solutions." Names written as values stay plotnine's names (`geom: geom_area`, `stat: stat_bin`, `position: position_identity`). The `theme:` key changes, because it is a component call. Test conditions are in M204 (picture baseline first; a test per place that holds a name as a value).
- Progress block: "Demo: which MLST row removed does not matter."
- Progress block: `left_join_lesson` = new recipe for the lesson.
- Channel M201: the id test's one named exception is `left_join_lesson` (`sequenced`); `complex_template` gets one common id set.

**Open with Eve** (one numbered list; questions go to her through the review session only, channel M201)
1. Collisions (Q2 in the progress block): remove the shortcut components or keep them under longer names. **[coordinator's wording: channel M202 records her answer "a)" to this; the coordinator must confirm before the build. See Contradictions 1.]**
2. Two spellings (Q4 in the progress block). **[Channel M203 records "A". Same check as point 1.]**
3. Q5 to Q10 of the rename: Q5 (channel M204, answered), Q6 (the 15 objects that cannot be added to a plot: an original must exist; what is technically possible, by running), Q7, Q9 (`stat_summary`), Q10. Q6, Q7, Q9 and Q10 stay open. Full list: `.claude/design/viz_rename_impact_2026-11-15.md` section 8.
4. Entity declaration: refuse or warn when the `entity:` key is missing; and the rule-file sentence on the type of `sample_id`. **[Contradiction 4: D-0029 already says "fail instead of warn".]**
5. Contact text of `left_join_lesson`: invented by the builder. Eve must check it.
6. Reference tables in the id test (`ID-TEST-REFERENCE-TABLES-1`).
7. A caution when rows grow after a join (JOIN-GROWTH-CAUTION-1). Options and the question are in tasks.md section 8.
8. The 14 exact duplicate rows in `ST22_Anchor` (ST22-DUPLICATE-ROWS-1).
9. No message at a join when the ids find no match (seen in `left_join_lesson`).
10. Channel M205 to M207 (not a decision, not built): Eve asks for research on engines. A recipe-level default engine, overridable per data schema, per tier and per plot (R/ggplot2 as a second plot engine; `dplyr` as a second data engine). She wants a panel round before the recipe specification is completed. She said it is for planning. The review session asked for the panel round.

**Next, in order** [coordinator's wording]
1. The ledger lines for today's answers (LEDGER-9): the progress-block answers and channel M201 to M204, each with her words and the date.
2. `EXPORT-CONTACT-1` (goes before the rename; Eve's answer recorded in tasks.md section 8).
3. The rename (V1-B-RENAME and VIZ-OWN-22-1), once the open points 1 to 3 above are answered by Eve.
4. VIZ-PARITY-30-1 after the rename (order decided by the coordinator, not by Eve).

**Contradictions found in the records (reported, not fixed; rule H)**
1. Rename Q2, Q4 and Q5: the progress block (12:10) and the brief list them as open. Channel M202, M203 and M204 record Eve's answers to them as decided. The ledger has no line for any of them yet.
2. Label "Q1": the progress block (12:10) gives Q1 as the old-bundle question. The older progress entry (10:10) gives Q1 as the fingerprint question (`viz_rename_impact_2026-11-15.md` section 8). `tasks.md` section 8 (EXPORT-CONTACT-1 line) cites "Q1 of the plot component rename" for her contact answer. Three readings of one label.
3. The migration command: `tasks.md` section 8 (IMPORT-OLD-BUNDLE-MESSAGE-1) says "No migration command in the message". Channel M201 says old bundles are refused "with the migration command". The two cannot both hold.
4. Entity declaration: the brief asks Eve "refuse or warn" as an open point. Ledger D-0029 (EVE, DECIDED, 2026-11-12) says "fail instead of warn" for the `entity:` declaration. One of the two must be dissolved or narrowed.
5. Demo MLST row: the builder report (choice 1) and the review (C1) list "which MLST row stays" as open. The progress block says Eve answered it ("does not matter"). No ledger line.
6. `complex_template` exception: the builder report (choice 5) says the exception stays on `complex_template`. The merged test (`app/tests/test_recipe_data_one_set_of_ids.py` line 271) and commit `5b7624e7` put the exception on `left_join_lesson`. The merged state follows channel M201. The builder report is out of date.

## 2026-11-17 16:30 (coordinator: state for the resume)

Written by a records agent from the coordinator's brief of 16:30, the reports it names, and the channel blocks M170 to M172 of the coordinator. Text marked **[coordinator's wording]** is not Eve's own words. Everything else is her words or a file read.

**State**
- Local `dev` = `445c84f6`. It is 18 commits ahead of `origin/dev` (`36d1bd23`).
- Eve pushes herself. The main folder is on `dev`.
- No worktree of today is left. Nothing is running.

**Merged since 13:30**
- LEDGER-9 (`16fe7512`): ledger lines D-0207 to D-0217. Review: PASS.
- EXPORT-CONTACT-1 (`445c84f6`, D-0208). What a user sees:
  - The bundle README has one contact line. `effective_run.yaml` has two keys for it: the contact and where it came from.
  - Three cases: the contact of the recipe; else the contact of the deployment; else neither (nothing is written).
  - A blank contact counts as absent.
  - A line break in a contact is written on one line.

**Controls on `445c84f6`** (all pass; logs in `tmpAI/controls_445c84f6/`)
- App import: OK.
- Headless suite: 9844 passed, 5 skipped, 15 xfailed.
- Golden baseline: identical.
- Browser gate (qa): 72 passed, 3 skipped, 0 failed.
- audit_cross_lib and audit_docs_sync: pass.
- check_doc_links: the same 7 known problems, no new one.

**Research done, nothing decided**
- Engine report `tmpAI/panel/engines/REPORT_for_eve.md`. Short answer:
  - A default theme for all plots exists and works (`theme_bw`; a recipe sets its own with `plot_defaults: theme:`; one plot overrides it).
  - An engine per plot (R and ggplot2 draw from the stored table): sound to plan. All four viewpoints support it.
  - An engine per tier or per table (dplyr): possible, large, risky for correctness. Three viewpoints say not now; one says only when a concrete use appears.
  - An engine per step: all four say no.
  - One sentence now in the recipe specification (engine names are an open list) avoids a format change later.
  - Six questions for Eve (report section "What you are asked"):
    1. The recipe format now: option 2 (write the principle, build nothing)?
    2. Engine names as an open list?
    3. Per plot only, no engine per step? The data side (dplyr) waits for a concrete use?
    4. An R snippet in a recipe: confirmed no?
    5. The four `plot_defaults` keys that do nothing: make them work, or refuse them?
    6. Real numbers: install ggplot2, arrow and svglite in R on her machine (she installs, or says an agent may)?
- Q6 facts `tmpAI/panel/viz_rename/q6_the_15_objects.md` (sections 6 and 7):
  - The fact: none of the 15 objects can be added to a plot alone. Plotnine fails for each with an AttributeError. So D-0210 ("an exact component next to its original") cannot hold in that strict sense.
  - Six silent differences from plotnine, D1 to D6 (section 6).
  - Four options, A to D (section 7).
  - **[coordinator's wording]** The coordinator's recommendation is C (only the value form). The file itself gives no recommendation: its section 7 says "no recommendation where D-0210 does not decide". C is not a decision.

**Open with Eve** (through the review session only; channel M170, M171, M172 of the coordinator)
1. Q6, the 15 objects: options A to D.
2. Q7, Q9 (`stat_summary`) and Q10 of the rename.
3. The six engine questions above.
4. The 11 points of channel M170 (coordinator block, 12:55).
5. New: the rule-file sentence for the contact in `.claude/rules/ui_implementation_contract.md` section 7.2.
6. New: a blank contact in HOME. `resolve_contact` shows a blank instead of the deployment's contact (CONTACT-BLANK-HOME-1). Export treats a blank contact as absent; HOME does not.
- The points 1 to 10 of the 13:30 list stay open as they were.
- **[records note]** The ledger does not hold "questions go through the review session only". No words of Eve say it. A ledger test refuses a relayed line of today, so it is not written there.

**Next**
- Nothing of the rename before her answers (Q6, Q7, Q9, Q10).
- Buildable without her: none known.

**Contradictions found in the records (reported, not fixed)**
1. Channel numbers: `tmpAI/agent_channel.md` has two blocks numbered M170 (line 1215 from the review session, line 1722 from the coordinator), and the same for M171 (1268 and 1739) and M172 (1274 and 1744). The rule says a number is not reused while the file exists.
2. The brief calls option C "the coordinator's recommendation". `q6_the_15_objects.md` section 7 gives no recommendation (see above).
3. Contact: EXPORT-CONTACT-1 treats a blank contact as absent. `resolve_contact` (`app/modules/data_analysis_recipe_validator.py:428-435`) does not, so HOME and export differ (CONTACT-BLANK-HOME-1).
4. VIZ-PARITY-30-1 and VIZ-OWN-22-1 (`tasks.md` section 8) say "no ledger line yet" and "LEDGER-9 owed". LEDGER-9 is now merged. The records did not check whether D-0207 to D-0217 hold the Q2, Q3, Q4 and Q5 answers.
5. The brief lists `test_shiny_gate_gap` among the browser files with a hard-coded `.venv/bin/shiny`. Grep finds no such path in `app/tests/test_shiny_gate_gap.py`. The other 11 files match.

## 2026-11-17 18:40 (coordinator: state for the resume)

Written by a records agent from the coordinator's brief of 18:40 and the channel block M173 (coordinator, 18:10). Text marked **[coordinator's wording]** is not Eve's own words. Everything else is her words or a file read.

**What you see first:** local `dev` = `80cd4e94`. It is 25 commits ahead of `origin/dev`. Check with `git log origin/dev..dev`. Eve pushes herself. Nothing is pushed by an agent.

**Merged on local `dev` since 16:30**
- `2ccfc34f` BROWSER-TESTS-FIXED-PATH-1 (DONE): eleven browser test files start the app with `app_command(port)` from `app/tests/subprocess_env.py`; a guard test and a proof test. Reviewed MERGE. Full controls PASSED (`tmpAI/controls_2ccfc34f/REPORT.md`): headless 9775 passed, 0 failed; browser 136 passed, 3 skipped, 1 xfailed; 9 app-features starts; golden identical; audits as before (7 known doc links; old-words check rc 1, known). One unexplained flake: an extra rerun of the two smoke files failed one test once (not recorded which one); the next run passed.
- `5e04e70c` LEDGER-10: ledger lines D-0218 to D-0228.
- `86c63fe2` EXPLORATION-REPORTS-1 (D-0221): five final reports and an index in `.claude/design/exploration/`.
- `1d09f9e8` VIZ-PREFIX-RULE-TEXT-1 (D-0218): section 1a of `rules_viz_factory.md`. The rename itself is not built.
- `80cd4e94` SAMPLE-ID-TYPE-1 (D-0225) and the demo contact of `left_join_lesson` (D-0226): checker error E03 refuses a numeric declared entity key; advice J13 stays; rule sentence corrected at `rules_data_analysis_recipe_structure.md:214`. Reviewed MERGE; headless in the worktree 9865 passed, 0 failed; golden identical. **Full controls on `80cd4e94` in the main folder are OWED.**
- EXPORT-CONTACT-1 (`445c84f6`) and LEDGER-9 (`16fe7512`) were merged before 16:30; `tasks.md` line 505 still said "open" and is now marked done.

**Running**
- Builder on `task/formula-deserialize` (worktree `.claude/worktrees/formula-deserialize`): FORMULA-ALLOWLIST-DESERIALIZE-1 `[sonnet/high]`. The formula check lets `Expr.deserialize` and `Expr.from_json` through; a recipe formula can read a file. Fix: a structural rule plus a test that walks all allowed members. Under D-0030.

**Owed next**
- Full controls on the next merge, and on `80cd4e94` (not yet run in the main folder).
- The reports for Eve, all in `tmpAI/panel/` (they move to `.claude/design/exploration/` once she has them):
  - `recipe_arguments/REPORT_for_eve.md`: 10 questions; question 4 (the plotnine original of the 15 objects is the typed value in its slot; the layer form is `modif_`) unblocks the rename and answers Q6. Q7 (`guide_label`) and Q9 (functions) can wait.
  - `engines/PLAN_engine_fields_for_eve.md`: 14 questions; first: recipe format 2, or amend format 1 (122 recipe files are stamped format 1). The removal of dead keys waits for this answer.
  - `author_manifest/REPORT_for_eve.md`: 9 questions; the same format question.
  - `lookup_table/viewpoint_scientist.md`: no opposition; needs her yes on the field names.
- Newer final reports to copy into `.claude/design/exploration/` when she has them: `tmpAI/panel/author_manifest/REPORT_for_eve.md`, `tmpAI/panel/engines/PLAN_engine_fields_for_eve.md`, `tmpAI/panel/recipe_arguments/REPORT_for_eve.md`. Also: add the folder to `CLAUDE.md` section 3.6 and `.claude/INDEX.md` (a worker; CLAUDE.md needs Eve's yes).
- The rename waits for her answers on Q6, Q7 and Q9. They are now carried by question 4 of the arguments report (see above). Nothing of the rename before that.

**Eve's goal (D-0228)**
- A good FUNCTIONAL demo as soon as possible; the date is set by how ready the app is (M268, D-0255; corrected 2026-11-18, Eve does not present at the end of the week). Eve is away for the evening.
- Order (coordinator's wording): what is decided and not built first (the demo must not break), then research. The demo recipe is not yet named by her; the developer assumed `demo_abromics`. Ask her.

**Pitfall for every worktree (WORKTREE-TEST-IMPORTS-1)**
- In a worktree, `PYTHONPATH=.` alone imports the libs of the MAIN folder, because the shared `.venv` has editable installs. Tests can silently test the wrong code. Until the fix, check the import path in a worktree run before trusting a result.

**Open questions for Eve (one list, through the review session; none is a decision)**
1. The three engine-plan defects: may they be fixed now (D-0050)? (ENGINE-PLOT-HANDOFF-1, PLOT-ENTRY-KEYS-LOST-1, BLUEPRINT-PLOT-DEFAULTS-FORM-1)
2. Recipe format 2, or amend format 1 (ENGINE-FIELDS-PLAN-1, CONTACT-AUTHOR-MANIFEST-1, PLOT-DEFAULTS-DEAD-KEYS-1).
3. Question 5 of the arguments report: fix the five silent defaults first (SILENT-DEFAULTS-2026-11-17).
4. The security findings: one line each in `tasks.md` section 9, all wait for her.
5. The field names of the lookup key and the five additions (LOOKUP-TABLE-1).
6. Whether a Date or Boolean entity key is also refused; the old-vocabulary lines; fold J13 into E03 or keep both (SAMPLE-ID-FOLLOWUPS-ASK-EVE).
7. The words for the ENTITY-DECL-SHIPPED-1 "yes" (M224 is the review session's reading; exempting lookup tables may conflict with D-0029).
8. Which recipe is the demo recipe.
9. The rename waits for Q6, Q7, Q9 (see above).

**Records contradictions found and fixed here**
- `tasks.md` line 505: EXPORT-CONTACT-1 was still "open" though merged `445c84f6`; marked done.
- `tasks.md` line 510: ID-TEST-REFERENCE-TABLES-1 said "Eve chooses"; D-0222 decides option a. Note added.
- `tasks.md` line 519: PLOT-DEFAULTS-DEAD-KEYS-1 said "waits for Eve's choice"; D-0220 decides the removal. Note added.
- `tasks.md` line 511: ENTITY-DECL-SHIPPED-1 note added (M224 "yes" is not her words).
- Task ids not given by the brief and chosen by the records agent: ENGINE-PLOT-HANDOFF-1, PLOT-ENTRY-KEYS-LOST-1, BLUEPRINT-PLOT-DEFAULTS-FORM-1, SAMPLE-ID-FOLLOWUPS-ASK-EVE. Tags marked [records] were not given by the brief (VIZ-SEED-DICT-POSITION-1, VIZ-PICTURE-EQUALITY-TEST-1, SECURITY-FINDINGS-2026-11-17, SILENT-DEFAULTS-2026-11-17, ENGINE-FIELDS-PLAN-1, CONTACT-AUTHOR-MANIFEST-1, LOOKUP-TABLE-1, AUDIT-LOGS-2026-11-17, and the defect lines). The coordinator should check them.

**Still open from 16:30 (not changed)**
- The 16:30 contradictions 1 to 4 (channel numbers M170 to M172 used twice; the brief's "option C recommendation" wording; HOME and export contact differ, CONTACT-BLANK-HOME-1; VIZ-PARITY-30-1 says "LEDGER-9 owed", now merged) stay as they were. Item 4 is not fixed: VIZ-PARITY-30-1 and VIZ-OWN-22-1 in `tasks.md` section 8 still say "LEDGER-9 owed"; the coordinator should say whether to edit them.
- Item 5 above (`test_shiny_gate_gap`) stays open.
