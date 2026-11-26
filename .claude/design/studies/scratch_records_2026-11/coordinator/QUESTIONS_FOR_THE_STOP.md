# Questions for the stop (one list; the review session brings them to the owner one at a time)

Kept by the coordinator. Rule (M336 point 3, M338, M340): only vision, correctness or what she sees. Each: the step it blocks, the options, my view. Facts: a scout's survey of dev `a538eca2`, 2026-11-19 (READ, nothing run).

## ANSWERED by the owner
- 2026-11-20 (channel M343): slice 0 point 1 and Q-A9: "B". The data choice in Exploration offers Source | T1 | T2 | T3 (her HOME design edit of 2026-11-13 stands; ADR-099's "Raw | Result" is superseded on this point). A plot with its own tier 3 steps is drawn from the table shown under T3; the "T3 = T2" badge problem disappears. Filters follow the tier being viewed.
- 2026-11-20 (channel, 07:30): slice 0 point 5: "A". Exploration filters are cleared when the viewed tier changes (D-0178 stands). Not kept, not checked, not carried silently.
- 2026-11-20 (channel, 07:33): slice 0 point 7: "A - best to clean all old sessions". A pre-redesign session file is refused with a plain line (saved by an older version); no conversion. All old session files are deleted (session files only, never recipes or data); list first, report what was removed.
- 2026-11-20 (channel M347): Q-A8: "C". Both lists, named differently: "the entity key" (declared, D-0082; drives the key warning and "remove from all tables") and "columns used to join" (information). Ledger D-0313.
- 2026-11-20 (channel M349): slice 0 point 2: "B". One undo control, "Remove step". Ledger D-0314.
- 2026-11-20 (channel M350): slice 0 point 3: "A". The audit log is always written in the session, optional in the export; date and initials live in the log (settles Q-A14 (a)). Ledger D-0315.
- 2026-11-20 (channel M348): Q-A4 is NOT decided. She asks for a verified study of tracking the columns along the lineages (the same tracking gives the filter dialog its scope) and a panel table of solutions with pros and cons (Blueprint architect, data scientist, user). Goes to `tmpAI/panel/column_tracking/`. Blocks slice C.
- 2026-11-20 (channel M351): slice 0 point 4: "A". Every place ticked when the dialog opens (D-0194 stands); rows and plots affected shown before she confirms. Ledger D-0316.
- 2026-11-20 (channel M352): slice 0 point 8: "A". A session saved against a different recipe is refused on restore with a plain line; the warning stays only for the same recipe with another data batch. Ledger D-0317. Built in piece B-1b. NEW open case from it: the same recipe id with an edited content (not covered by her word; today's warning kept until she says).
- 2026-11-20 (channel M353): Q-A16: "C". Affected plots listed with two statements, "table changed" and "picture changed". Ledger D-0318.
- 2026-11-20 (channel M354): Q-A13: point 1 "I think audit/ good" (D-0319; exact path to confirm against the design pages); point 3 "Comments kept" (D-0320); point 5 "ok" (D-0321). Points 2 (what the audit recipe says about its original) and 4 (the form of the reason, a marked comment) are OPEN: panel table to `tmpAI/panel/audit_recipe_file/`.
- 2026-11-20 (channel M355 of sparmvet-viz-50): Q-A15: "A : for now yes only filter and drops". The check of an audit recipe refuses any audit step that is not a filter, a column drop or a removal by key; the allowed list in one place. LEDGER LINE STILL TO WRITE (next number D-0322; batch with the next answers).
- 2026-11-20 (channel M356): her yes ("A") for the one cell of the flag table. Ledger D-0323. Done in the flag and session piece as its own commit.
- 2026-11-20 (channel M357): Q-A2 and slice 0 point 6: "A". When audit steps were added, the export holds the audit recipe as the recipe that produced the figures (it replaces today's export copy); the original may be added as the baseline, clearly named, out of the way. Ledger D-0324. Slice D. ALL slice 0 points are now answered.
- Q-A13 points 2 and 4: the table is ready, `tmpAI/panel/audit_recipe_file/TABLE_FOR_THE_OWNER.md`; waits for her (six points are hers).
- 2026-11-20 (channel M358, M359 of sparmvet-viz-50): Q-A4: she EXCLUDES A, D and E2, and takes Blueprint out of the choice (HOME and GALLERY first; Blueprint's needs go to its later design pass). Live options: B and C. She asks for a MEASURED cost of B and C on `figshare_integration` and the demo recipe (running), the answer on a stored table at the end of tier 3, and a corrected table. PARKED for the Blueprint pass: column pickers that follow a rename (rules per action); today Blueprint offers only the declared fields.
- 2026-11-20 (channel M362 of sparmvet-viz-50): **Q-A4 DECIDED: B.** Her words: "3 - but when a recipe is open should not everything be build? then errors should be detected because it actually runs B at choosing the recipe (=opening) -> then B anyway its applied for the audit - because no change can happen to the recipe if we are not in audit mode - and the audit steps need to be rebuild when we add with a reason (applied) so B I think is the correct choice". LEDGER LINE STILL TO WRITE (D-0325). Her points 2 (pivot) and 3 (type on the line) of the table are not answered yet. NEW, not decided: should opening a recipe build or check everything, so that an error of the original shows at opening? Facts and options to `tmpAI/panel/column_tracking/OPENING_CHECK_options.md` (a scout collects what HOME builds at opening today).
- 2026-11-20 (channel M364 of sparmvet-viz-50): **DECIDED: opening a recipe builds EVERYTHING**, stored by key: every tier 1 and tier 2 table, the tier 3 table of every plot, and every plot, so a plot is ready when selected; equal keys rebuild nothing. Her words: "Q-A4 - well at opening the recipe it should build everything - also note that because once its build if there is no audit change we will have the session cache to use so it wont be rebuild if there is not change to the recipe and data no? We need to solve this one before we take the question you did put on screen" and "On the first open, every table of tier 1 and tier 2 is built and stored. Build T3 and plot -> why are those steps always forgotten? the plot need to be ready when the user selects it no? No a T3 and plot must be done from the recipe if do not exist T3 reuse previous steps anyway". LEDGER LINE STILL TO WRITE (D-0326). It supersedes my options page `tmpAI/panel/column_tracking/OPENING_CHECK_options.md` (written a few minutes before; its facts stand, its recommendation does not). BEFORE BUILDING she wants four figures (running, the measurement builder): what is stored today (is a drawn plot stored); time and memory of a one-table-at-a-time build on the 30x and 100x data; the time to draw every plot; what the load gate does on a build error and whether a progress line is needed. It also settles Q-A10 in the direction "stored" (the tier 3 table is stored).
- 2026-11-20 (channel M365 of sparmvet-viz-50), for the piece that builds D-0326: a TEST that a recipe with a plot that cannot be drawn is refused at opening with a plain reason, and that a recipe whose plots can all be drawn opens (able to fail). Her words: "if the plot is not prebuild we need a test because then we are sure that the plot recipe do not fail - we could have recipe failure only when the user click the recipe --- no then we sure ensure the whole recipe works at least - even if the plot is rebuild. We had said that exploration filters are only data exploration and they are never applied so it changes nothing - its only audit applied steps that change things". Read as: one plot that cannot be drawn refuses the whole recipe (asked the review session to confirm). Exploration filters change the table only, never a plot, nothing stored, nothing exported: confirmed from the records (D-0019, D-0180, ADR-099 point 1) and already what slice B builds.
- Q-A4: table version 2, `tmpAI/panel/column_tracking/TABLE_FOR_THE_OWNER.md`; waits for her.
- Waiting for her yes: one cell of the flag table in the rule file `rules_app_features_flags.md:128` (simple, comparison: true becomes false); blocks the merge of the flag and session piece.
- NEW open points from the flag and session piece (after the build): the same recipe edited since the session was saved (today a warning; kept); the session list shows the cards of other recipes with Restore (a click gives the refusal line); an old file with the same key as a new session (built: not written over; the user is told to delete it); `migrate_config_vocabulary.py --sessions` is pointless now (remove?).
- NEW open points from the Source reader: what Source shows for a recipe whose map cannot be drawn; an empty source file gives an error (as tier 1), a header-only file shows zero rows.
- Still open of slice 0: point 6 (the recipe in the export of an audit; slice D).
- Ledger numbers of the first three: D-0310 (point 1, Q-A9), D-0311 (point 5), D-0312 (point 7).

## FOR SLICE D, her wording requests on the export report (channel M360 of sparmvet-viz-50, 2026-11-20; Q-A6 and Q-A11; the final sentences are NOT decided, she reads them in the app)
Her words: "New wording: can it be possible to specify what the key (column) is in the report? would not 'Key of the Tier <Number> parquet: Tier <number> key <column name that is the key> tier engine, version, resolved manifest, data (or previous data tier), steps'? Do not forget to add T3 steps and plot steps in the report if necessary (can be worth to plan adding - maybe one day we will be able to make some changes in the plot aesthetics in audit - we need to plan ahead). Also a bit uncertain about the adding in the report we had the recipe - the report can make the changes from the audit clear - is it what is meant here? because otherwise the original recipe is added anyway no?"
For the builder of slice D's bundle texts: (1) each key row says what the key is made of: tier number, engine and version, the table's definition and what it reads, the data or the previous tier, the steps of that tier; (2) a SEPARATE line names the entity key column(s) of the table (the key of the report rows is a fingerprint, not a column; the two must not be mixed); (3) the rows cover the plot's tier 3 steps (written in the recipe, and audited) and leave room for plot aesthetics changed in an audit later, so nothing needs rewording then; (4) the report's audit section makes the changes of the audit clear: what was added, where, why, which plots changed ("table changed" / "picture changed", D-0318); the audit recipe is the truth and the original the baseline (D-0324); the README line "plus that plot's tier3 steps of the recipe" must say these are steps the recipe's author wrote, not audit steps.
To verify before slice D: the review session says the bundle "already holds the original recipe (data_analysis_recipes/)"; the scout of today found ONE resolved file `data_analysis_recipes_reproducibility/<id>.yaml` without comments and no copy of the recipe's own files (`export_handlers.py:1493-1500`). Check which is true on dev before the brief.

## NEW from slice B (the coordinator's provisional choices; full text in `SLICE_B_plan.md`)
P-B1 the data choice starts on T3; P-B2 changing the plot or the Source table also resets the exploration filters; P-B3 in Audit mode until slice C, "Send to Audit" and the column drop only while T3 is viewed; P-B4 no preview "Apply" in Audit mode; P-B5 the session file holds no view value, and a restored session with audit steps opens Audit mode; P-B6 the export line "Active tier" becomes the mode and the data choice; P-B7 names in the code; the texts of the refusals (old session; flag pair).

- Slice B's blocking points (1, 5, 7, Q-A9) are all answered. Point 8 only if B touches it. The questions that block nothing (Q-A3, Q-A5, Q-A7, Q-A10, Q-A17) come after the blocking ones.

## From slice 0 of the slice plan (`tmpAI/panel/audit_redesign/SLICES_v3_2026-11-18.md` lines 17-27)
Points 1 to 8 as written there. Blocks: 1, 5, 7 block slice B (as M340 says); 2, 3, 4 block slice C; 6 blocks slice D; 8 blocks slice B or C.

## Q-A1. Labels in the keys of the stored tables (slice 0 point 9). Blocks: nothing now; decides one line in piece A3.
- Fact: today everything written under a table or a join enters the key, a join's `labels` included; plot labels do not. So changing a join label rebuilds the tables.
- Options: (a) take the labels out of the keys (a label change rebuilds nothing); (b) keep them in.
- My view: (a). A label is text for the reader, not data. Built so that the change is one place.

## Q-A2. The export of an audit today writes the audit steps into a copy of the join's tier 2, not into the plot's tier 3. Blocks: slice D (and the end of piece A5).
- Fact: `t3_translator.py:263-277`. Her decisions say: the audit adds steps at the end of the T1, T2 or T3 list of a copy (D-0146, D-0102).
- Options: (a) the new audit recipe replaces this export copy in slice D; (b) both stay.
- My view: (a); two ways to write the same steps would disagree one day. Same as slice 0 point 6.

## Q-A3. D-0135 is marked DECIDED in the ledger, but its own text says it is a relayed plan that "becomes decided only when she confirms it". Blocks: nothing in slice A (I do not quote it); slice D builds on it.
- For the review session to settle in the ledger, or to ask her once.

## Q-A4. Where a field exists is UNKNOWN for many tables when read from the recipe alone. Blocks: slice C (the dialog that shows where a field exists), and the precise part of the keys.
- Fact (piece A1, RAN by the builder): the map knows the columns of a table only while the steps are filters, sorts, a select or a drop of plain names. After a join, a rename, a new column, a reshape, the columns are "unknown" (never guessed). On the demo recipe: 50 of 85 places unknown.
- Options: (a) a dry run of the recipe on the real data gives the true columns of every table (to build in the transformer; exact; needs the data); (b) a written rule per action for what it does to the columns (no data needed; every action must declare it; a wrong declaration shows a wrong place); (c) both: dry run in HOME, declared rule only where no data is at hand.
- My view: (a) first. HOME always has the data, and the truth is what the engine produced. Not a guess, and nothing to keep in step with the actions.

## Q-A5. May a join take another join as an ingredient ("a join of joins")? Blocks: nothing now.
- Fact: the engine and the checker accept only source tables as ingredients today. The map draws a join of joins without complaint; the slice plan lists it among the shapes to test.
- Options: (a) not allowed (as the engine does today): the map refuses it too; (b) allowed: the engine and the checker learn it (a build).
- My view: (a) until a recipe needs it; then it is a build of its own. The map keeps drawing it meanwhile (marked provisional).

## Q-A6. Two sentences of the export report were reworded by a builder (piece A3). Blocks: nothing; a text she reads.
- Fact: the report rows that describe the key of the Tier 1 and Tier 2 tables said "chained key of the whole recipe"; with a key per table that is no longer true. The builder wrote new sentences (pinned by a test). The reviewer quotes old and new: see `tmpAI/coordinator/SLICE_A3_table_keys_report.md` and the review.
- Options: (a) keep the builder's wording; (b) her own wording.
- My view: (a) unless she reads it and wants other words; marked provisional.

## Q-A7. The old name `decision_hash` is still written into every stored table and into the export texts. Blocks: nothing now.
- Fact: ADR-101 point 7 retires it "after checking that nothing else calls it". It is still read by the start-up sweep and written into the bundle README and report. Removing it changes the text of the bundle and what an old bundle reader finds.
- Options: (a) retire it in slice D (the export of an audit), with the bundle texts; (b) retire it now in its own small piece.
- My view: (a): one change of the bundle's texts, not two.

## Q-A8. What is "the key" of a recipe for the audit: every column used to join, or only the declared entity key? Blocks: slice C (the warning on a filter that touches a key; "remove from all tables").
- Fact (piece A2, RAN): today HOME takes every column that any join step uses as a key (so `Gene_name` and `VF_gene` count in the demo recipe). The new map takes only the columns declared as entity key, linked through the joins. They differ on 15 of 54 recipes: recipes with no declared entity key get no key at all from the map; recipes with a declared key and no join get one only from the map.
- Options: (a) the declared entity key only (her decision "keys are declared in the recipe", D-0082); then a recipe without a declared key has none and the checker must say so; (b) every join column as today; (c) both, named differently on screen (the entity key, and "columns used to join").
- My view: (a) with the checker asking for the declaration, and (c)'s second list only as information in the dialog. To settle before slice C.

## Q-A9. A plot whose recipe has its own tier 3 steps: what does the Result view show? Blocks: slice B (the views). No shipped recipe has such steps yet.
- Fact (piece A4, built): the plot is drawn from the plot's own table (its tier 3), as the format decides ("the plot equals its table"). The data view "Result" still shows the table at tier 2. So for such a plot the Result plot and the Result table differ, and the small badge would say "T3 = T2", which is untrue then.
- Options: (a) the Result data view shows the plot's own table (tier 3) for such a plot; (b) a fourth data view "T3" beside Raw and Result (this is her "Source | T1 | T2 | T3" of slice 0 point 1); (c) leave as built and only correct the badge.
- My view: (b), settled together with slice 0 point 1; it is the same question. Until then (c) is the smallest honest step: the badge must not say something untrue.

## Q-A10. The table of a plot with tier 3 steps: kept as a file, or computed when needed? Blocks: nothing; speed only.
- Fact: built as "computed when needed" (nothing new on disk). The design files leave it open.
- Options: (a) computed when needed; (b) stored like tier 2, with its key.
- My view: (a) until a real recipe is slow; then (b). Nothing she sees changes either way.

## Q-A11. Texts of the export bundle changed by a builder (piece A4). A text she reads.
- README line: "... plus that plot's filters and column drops" became "... plus that plot's tier3 steps of the recipe and its audited filters and column drops".
- New link label in the report for a plot with recipe tier 3 steps only: "Data of the plot (T3)".
- The bundle now holds the data file of a plot that has recipe tier 3 steps even when nothing was audited (so the plot's data is in the bundle).
- My view: keep; her wording if she wants other words.

## Q-A12. The line a user reads when the check itself fails on a recipe (piece A2 repair). A text she reads.
- "[CHECK] the recipe r.yaml could not be checked: the check itself failed on the shape of this recipe (<error>); the recipe is not accepted". Tip: "Look for a value of the wrong kind (a list where text is expected, a mapping where a list is expected). If the recipe looks right, this is a fault of the app: report it."
- My view: keep; her wording if she wants other words.

## Q-A13. The audit recipe as a FILE. Blocks: slice C (writing a step) and slice D (the export). Piece A5 builds it in memory only.
The records disagree or are silent on five small points; all are about the file a user finds in a session or a bundle:
- Its name and folder: "under `user_data` next to `anchors/`, in `audit/<session_key>/`" (audit design page) or "`_sessions/<session key>/audit/<recipe id>.yaml`" (mechanism page, an agent's proposal). My view: in the session folder, named after the recipe; one place for everything of a session.
- Its header: names the original, or the original's hash, or both. My view: both (name to read, hash to check).
- The author's `#` comments: the copy is one resolved file (all includes merged). Either the comments are lost in the copy (the original keeps them), or the copy must be written by a text-level tool. My view: the copy may lose them, said plainly in its header, because the original is the reference; her rule "every writer keeps comments" then needs this one named exception, which is hers to give.
- The reason of a step: in the step's `comment` (checker accepts it) and, per her decision, as a `#` comment. My view: the `comment` key only; one place.
- What the number at the end of the step id counts (`audit_<8 hex>_<k>`): undefined. My view: the order in which the steps were created in that audit.

## Q-A14. Date and initials of an audit step, and the log of added and removed steps. Blocks: slice C/D.
- Fact: the step in the recipe may hold only `action`, `id`, `comment`. Her decision: the full log "can be added, optional, for archive" (D-0189); the key design names a record "with reasons, initials, dates and the event log".
- Options: (a) date and initials live only in the log file beside the copy; the log is always written in the session and optional in the export; (b) also as `#` comments in the copy.
- My view: (a).

## Q-A15. Should the check of an audit recipe REFUSE any audit step that is not a filter or a drop? Blocks: nothing now.
- Fact: the design says "the audit writes only filters, drops and removals by key"; the checker's audit profile does not enforce it.
- My view: yes, enforce it in the check (a copy edited by hand could otherwise carry any step under an audit id). It changes what the check accepts, so it is hers.

## Q-A16. When is a plot "affected" by an audit step? Blocks: slice C (the numbers and the list of affected plots shown before she confirms).
- Fact (piece A5, built): a plot is affected when the CONTENT of the plot's table differs between the original and the audit run (her decided rule in the key design). So a filter that removes nothing does not affect the plot. But a dropped column that the plot does not draw DOES count as affected, because the table differs although the picture is the same.
- Options: (a) as built: the table decides; (b) only the columns the plot uses decide; (c) show both: "table changed" and "picture changed".
- My view: (a) for the rule, and say in the dialog what changed (rows, columns), so that a dropped unused column reads as "table changed, picture the same". Simple and never hides a change.

## Q-A17. An audit step at tier 2 of a table that no plot reads is refused by the copy (it would be applied nowhere). Blocks: slice C (which places the dialog offers).
- My view: keep the refusal; the dialog should not offer such a place. Listed so she can object.

## For Blueprint's later pass (parked, not asked now)
- What Blueprint shows for a recipe the map cannot draw. Built provisionally in piece A2: the broken element is left out and listed (nothing shows the list yet); before, a dangling link was drawn. Options: as built and show the list / refuse the map with the plain error / a partial mode in the map. Waits for: the Blueprint design pass.
- Blueprint builds a recipe step by step; the map refuses a broken recipe with the list of problems. Either Blueprint checks first, or the map gets a lenient mode. Waits for: the Blueprint design pass.
- The file each element comes from is not known to the map (the loader drops it). Waits for: piece A2 (navigator on the map); a builder reports the options.

## Records that disagree, settled by a later decision (no question; listed so the owner can object)
- Is the plot engine part of a table key? ADR-101 text says yes; her later D-0240 says "The plot engine enters no table key". Built as D-0240.
- The form of the tier 3 key: the format spec says a hash of the tier-2 key and the steps; D-0025 and ADR-101 say a series of labelled parts. Built as D-0025. The spec sentence is out of date (goes with the rule and spec sentences later).
- Order inside slice A: the stage-2 mechanism page puts the tier 3 reader after the keys; the slice plan lists both in slice A. Built: graph, then keys, then the reader.
