# The gaps of the guardrails of HOME and the audit: the problem, the options, a recommendation

**What this page is.** For each known gap G1 to G13 of `home_guardrails.md` section 10: the problem exactly (with one example that was run, or read at file:line), what it does to a result, the options to solve it with pros and cons, and a recommendation. Written for the owner (Eve, 2026-11-28, channel block M720). **The page recommends; the owner decides.** Nothing here is built unless a section says so.
**Evidence words:** RAN (run in a scratch script under `tmpAI/gaps/`, not in git), READ (read at file:line), REASONED (an inference), "not checked".
**Order:** the gaps that can give a silently wrong result come first.
**Words.** "Table" is one of the data tables of a recipe. "Place" is where an audit step is written (a table at its tier 1 or 2, or the result data of a plot). "Session" is the saved record of the audit steps on one recipe and one set of data files.

## Summary

| Gap | Silent? | Recommended option | Size | Needs her decision? |
|---|---|---|---|---|
| G1 Restore on other data | yes (it was) | the refusal is built; the live case below needs a decision | refusal done; live case 1 to 2 sessions | yes, for the live case |
| G2 Upload replaces the file, no copy; new session by itself | yes (the old data is gone; a session appears without asking) | E now (guard built), then the sessions options page (A: a store by hash) | small now; the real fix 3 to 5 sessions | yes (reopens D-0434) |
| G3 CR-only file reads as zero rows | yes (a console line only) | A: refuse a file that reads as zero data rows, with a plain hint | 1 session (2 files) | yes (a refusal at upload) |
| G4 No-break space inside an id | no (a warning shows, but says the same id twice) | A: the id warning names ids that differ only by an invisible character | 1 session (1 file + test) | no (it only informs) |
| G9 Join through a constant or repeated key doubles or empties rows | yes | B (a declared row-count rule) after the demo; A (ask for `validate`) is cheaper | 1 to 3 sessions | yes (changes the recipe spec) |
| G5 One id column per table (pair tables) | yes (three wrong effects) | now: no id on the pair table (recipe choice); app: A (ids are the values of both columns) | 4 to 6 files, 2 sessions | yes (3 small points) |
| G6 Ids are checked only before tier 1 | partly (a check is missing, not a wrong value) | B: check and warn at the tier where the id appears (task ID-AT-THE-TIER-IT-COMES-INTO-BEING) | 3 to 5 files, 2 sessions | no (decided D-0702, later) |
| G7 Plot ids unique over recipes: not checked at start | no (probably harmless today; not run in the app) | A: run the set check at start and reject the later recipe with the reason | 1 to 2 files, 1 session | yes (it rejects recipes that open today) |
| G8 Two processes or tabs on one user place | no (visible, or the trial is simply lost) | A: tell the deployment page that one user place belongs to one process; B: a process mark in the folder name | docs now; B 1 session | yes (a deployment rule) |
| G10 Recipe formulas run through `eval` | no (12 tries refused) | A: keep, add the 12 tries as a test; B: a study before recipes of others are shared | 1 session (test) | no for A |
| G11 Who verified is not recorded | n/a (a record is missing) | as decided: initials typed once per session, with the audit log | with the log build | no (decided) |
| G12 The audit log is not built | n/a | as decided (D-0679), build waits (D-0682) | 3 to 5 sessions (REASONED) | no (decided; the size limits are open) |
| G13 Split of the checks, no recipe at start, record of uploads, the choice at upload | partly | as decided (D-0698 to D-0701), with the correction below | 4 slices D1 to D4 | one point open (the session container) |


## G1. Steps of one dataset applied to another (Restore on other data)

**Built on 2026-11-28 for the Restore (commit `fix(session)!: a restore on other data is refused`). One half of the problem is still open: the live view.**

**1. The problem, exactly.** Eve's example, the small and the large pair table. The user works on the small data and adds an audit step ("year > 1900", reason "made on small data"). She uploads the large files. A second session appears by itself (its key holds a hash of the data files; RAN earlier, `tmpAI/demo_upload_study/upload_sessions_run.py`: small key `...:775f2013ce39`, large key `...:6102f4cd7...`). Then she presses Restore on the small session. Before: a yellow warning "Session was saved against a different data batch", and the steps were put on the large data. After the change: an error names the session's files and the files now loaded (file name, 8-letter hash) and nothing of the session is put into the view (RAN: `app/tests/test_restore_on_other_data_refused.py`; with the guard switched off the steps are applied: the test fails, so it can fail).
**The open half (RAN, `tmpAI/gaps/g1_live.py`).** She is in the view with a step made on the small data. The data on disk changes (an upload). HOME updates its data key by itself (READ `home_theater.py` `_sync_session_provenance`, `needs_update`) but keeps the steps in the view, and tells her that "a source data file changed ... reload". If she adds one more step without reloading, ALL steps of the view are written under the new data key (READ `audit_session_save.py:44-56`). Run: one step made on key `1111...`, the key changed to `2222...`, the next save: two session folders, each holding the same step. The step made on the small data is now in the large data's session.
**2. The consequence.** Before the fix: silent (a warning that disappears after 8 seconds), the audit table and figure can be wrong for the data on screen, and the export would say the step was made on these data. After: the Restore cannot mix. The live case is still silent after the first message.
**3. Options for the live case.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. When the data on disk change while steps are in the view, the view stops accepting steps and says: "the data changed; your steps were made on the earlier data: start a new session (steps are not carried) or reload" | A clear block at the moment of change; Add is greyed with the reason | Closes the hole in one rule; consistent with the Restore | The user loses the steps in the view unless she exports first | 2 files (`home_theater.py`, `trial_handlers.py`), about 1 session | Eve 2026-11-28 (steps never mix); D-0302 untouched |
| B. At the data change the audit of the view is closed and kept, linked to the old data, and a NEW empty audit starts on the ORIGINAL recipe (the proposal under her consideration; steps are never carried to other data, she refused that) | The panel shows the old audit as a closed item with its data, and an empty new audit | Same rule as the Restore; nothing mixes; the old audit can be chosen again with its data | Needs the sessions options page (where the data of a session lives) and whether the session container continues | 3 to 5 files, 2 sessions | Eve 2026-11-28 (an audit is linked to its dataset); reopens D-0434 in part |
| C. Leave it and keep it on the limits page | The first message only ("reload the page") | Nothing to build | The silent mixing stays | 0 | none |

**4. Recommendation.** A now (it is the same rule as the Restore, small), B later with the sessions options page (it is the target: the audit and its data go together). **Flag first: A changes what a user can do after an upload (she cannot add steps until she starts a new session), but it removes a silent wrong result.**
**5. What was not checked.** The live case was run at the level of the save function with the key changed by hand, the way the sync effect changes it (READ), not in a browser. The recipe-version warning ("saved against a different recipe version") is unchanged and still lets the steps through: it is a question for her (an edited recipe with the same name is not "another recipe" in D-0317). The Restore paths: the Restore button and the save picker are the same function (`_restore_session`; it restores the newest save only; READ `session_handlers.py`); the automatic restore at start ("Prepped Chef", `restore_t1t2`) is not called by the app (READ: `grep` finds only its definition and a comment) and restores no steps; the import of a session zip only registers the session in the panel (no steps applied); a bundle import writes its own recipe and data and never touches the view (READ `bundle_importer.py`, "Never touches live app state"). A browser test seeds sessions with invented data hashes (`test_shiny_session_restore.py` and two more): they will fail on Restore and must be reseeded (not run, no browser in this task).

## G2. An upload replaces the data file with no copy; a new session appears by itself

**1. The problem, exactly.** Eve's demo: a recipe built on the small data, then the large data uploaded for the same recipe. What happens (RAN by the earlier study, `tmpAI/demo_upload_study/upload_sessions_run.py`, on a scratch recipe, 12 and 40 isolates; I did not run it again; the facts below are also READ in the code):
- The file name she gives (for example `2026-11-27_Streptococcus_dysgalactiae_hamming_distance.tsv`) is ignored. The file is written at the path the recipe declares (`source.path`), over the old file (READ `orchestrator.py:182-215`, `data_import_check.py` `store_all`: copy next to it, then replace). The old file is gone: no copy, no record of the old name (D-0434, as built).
- The data key changes, so a second session appears by itself (small key `ed455052e7ba:775f2013ce39`, large key `ed455052e7ba:6102f4cd7...`). She is not asked "update this session" or "start a new one" (READ `home_theater.py` `_sync_session_provenance`).
- Her real files (read only, `tmpAI/demo_upload_study/real_case/`): small hamming table 322 bytes (4 lines), large one 136,677 bytes (2,212 lines); her two tables for the large set total about 137 KB. To go back to the small data she must upload the byte-identical small files: one added byte or Windows line endings give another key (RAN).
- Other tabs or sessions of the same recipe read the same replaced file: the replacement changes what every session of that recipe reads.
**2. The consequence.** Silent loss of the earlier data (no way back except her own copy); a session made by the app without a choice. The Restore half is now guarded (G1). A figure made on the small data cannot be remade from the app once the file is replaced.
**3. Options** (the full set is on the sessions options page, `studies/sessions_bring_their_data/OPTIONS.md`; here only the shape).

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. A store by content hash: each upload kept once; the session records name, date and hash per file; at upload a new audit starts on the original recipe and the old one is kept with its data | A new empty audit at upload; Restore of an earlier audit brings its data back | The way back is the app's job; no duplicate files | Disk grows; a rule for deleting; deployments with pipeline data (`by_dataset_id`) refuse uploads | 3 to 5 sessions | REOPENS D-0434 (no copy); touches D-0439, D-0440, contract 12d |
| B. A copy per session in the session folder | The same recording, in the session folder | Simple to delete with the session | Copies of the same file per session (her real files are small, 88 MB for 2,000 isolates) | 3 sessions | REOPENS D-0434 |
| E. Today plus the guard (built): she keeps her own copies and uploads them again | An error at Restore that names the files | Nothing more to build | The replaced file is lost unless she kept it; a session still appears by itself | 0 more | D-0434 kept |
| Leave it, keep it on `current_limits.md` | As today | none | silent loss stays | 0 | none |

**4. Recommendation.** E stays as the floor (it is built). **It reopens a decision (D-0434) as soon as the app keeps data: that is hers to decide.** If she wants the way back from the app, A (a store by hash, reading from the store by hash rather than re-placing files, because re-placing changes what every other session reads). What the choice at upload still is (the old "Update this session / Start a new session") is not decided now that an audit is always tied to its data: see the section "What an upload does to the session" on the options page. It is the same slice as option B of G1.
**5. What was not checked.** Nothing run in a browser; the real files were not uploaded (read only); the size numbers of a store are on the options page.

## G3. A file with old Mac line endings (CR only) reads as zero rows

**1. The problem, exactly.** A pair table with three pairs, saved with CR-only line endings (the old Mac form; some lab scripts and spreadsheet exports still write it). RAN (`tmpAI/gaps/g3_g4.py`, the ingestion's own read `ingest_file`, the one Data Import and the load use): the same file with LF endings gives 3 rows; with CR endings it gives **0 rows and no error**. The reader sees one long header line. When every column the recipe declares is among the first columns of the file (here `isolate1`, `isolate2`, `hamming`), the declared columns are found and the table is empty; the only trace is a console line listing garbled "not imported" names such as `note\rA1`. When a declared column lies beyond the first CR (my first test, `dist`), the read is refused, with a misleading message ("column not found").
**2. The consequence.** Silent: an empty table opens, every plot is empty, the id check may add every id from the metadata as "missing in original table". Whoever opens it sees empty figures, not the cause. No result is wrong, but a figure can be empty without a word of why.
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. Refuse a file that reads as zero data rows (at upload and in the data check), saying "no data rows were read; the file may use CR line endings: save it with LF" | A plain refusal at upload; a rejected recipe with the reason at start | Fixes the silent case for every cause of an empty read; informs, does not change the data | An empty table that is wanted is refused (the recipe maker can declare none; to decide) | 2 files (`data_import_check.py`, the data check) and a test; 1 session | D-0050 (no silent error); D-0593 to D-0596 kept (no cleaning) |
| B. Only warn (a yellow notice) | A notice | Nothing refused | A warning is easy to miss and the empty figures follow | same | same |
| C. Read CR as a line end | Works | Convenient | The app starts to repair files: against D-0593 to D-0596; reopens them | 1 session | REOPENS D-0593 to D-0596 |
| D. Leave it and keep it on the limits page | silent empty table | none | silent | 0 | none |

**4. Recommendation.** A. **It refuses files that open today (silently empty), so tell her first.** Open point for her: is a recipe whose table is empty on purpose ever valid (a table that has no rows yet)? If yes, refuse at upload only and warn in the data check.
**5. What was not checked.** The app path (HOME opening an empty table) was not run; the rule "empty table at the id check" is READ in `rules_data_analysis_recipe_structure.md` section 13, not run. Her lab script that writes the files (task D6) is not found yet.

## G4. An id with an invisible character inside (a no-break space)

**1. The problem, exactly.** The metadata lists the isolate `Sample 1` (a normal space). The results table, written by another tool, has `Sample\u00a01` (a no-break space, invisible, copied from a web page or a spreadsheet). The reader removes spaces at the two ends of a text (`strip`), never inside it. RAN (`tmpAI/gaps/g3_g4.py`, with the app's own id check `build_report`): the two ids are different texts. The warning says, in two lines for the same table: "1 id(s) are not in the metadata: Sample 1" and "2 id(s) of the metadata are not in this table: Sample 1, Sample 3". The same words "Sample 1" appear on both sides, and a line is added to each table for it ("missing in original table"). Nothing says why. (The earlier case of an id with a no-break space at the END was removed by the reader: RAN, `A2\u00a0` read as `A2`.)
**2. The consequence.** Visible, not silent: the id warning shows. But it cannot be understood: the user sees one id twice and cannot find the difference. A join on the id would not match the sample, so its measurements are not on its metadata row (it appears as two rows, one with empty measurements); a figure by group would drop the sample from its group without a word beyond the warning.
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. The id warning says when two ids differ only by invisible or look-alike characters ("'Sample 1' and 'Sample\u00a01' differ by a no-break space") | A line that names the cause | Informs; changes no data; the recipe maker fixes it with a visible step | Needs a list of characters to look for | 1 file (`id_completion.py`) + a test; 1 session | D-0593 to D-0596 (no cleaning) kept; D-0050 |
| B. The app removes them at read | Ids just work | Convenient | The app cleans data in HOME: reopens D-0593 to D-0596; changes ids silently | 1 session | REOPENS D-0593 to D-0596 |
| C. Document the recipe-maker answer (a visible `polars_str_replace_all` step) in the help of the id warning | A help sentence | No code | The user must read it | docs only | none |
| D. Leave it, keep it on the limits page | The confusing warning | none | confusion stays | 0 | none |

**4. Recommendation.** A, with C in the same message (the way out is the step). It informs and changes no result, so it needs no decision of hers beyond "yes, add the hint".
**5. What was not checked.** Which invisible characters a real lab export writes (RAN: her four real demo files hold no byte outside plain ASCII and no CR, so they are not affected); the full app path (the warning in HOME) was not opened in a browser.

## G9. A join through a key that does not identify one row doubles or empties the table

**Correction first.** The first words of this gap said "a cross join". RAN (`tmpAI/gaps/g9.py`, through the registered action `polars_join`, the one a recipe step runs): a cross join written as such is **refused** ("exactly one of on, left_on is wanted"; with a key: "cross join should not pass join keys"). So the problem is not the cross join but the same effect through an ordinary join. I corrected the rows of the guardrails and limits pages.
**1. The problem, exactly.** Her "information" table has exactly one row (a table of constants). The recipe maker joins it to the main table (3 rows) through a key that is the same on every line (a constant `k = 1` added to both tables), or, more commonly, the other table has the same id twice. RAN: inner join with an other table of 0, 1, 2 rows gives 0, 3, 6 rows; left join gives 3, 3, 6. With `validate: m:1` written on the join, the 2-row case is refused ("join keys did not fulfill m:1 validation") (RAN). The app does not ask for `validate` and does not check the row count after a join (READ: `recipe_check.py` has no rule on `validate`; the plain-words diagnosis `join_diagnosis.py` runs only for joins that write it).
**2. The consequence.** Silent and wrong: every table below the join is doubled or empty; figures count twice. Only a person who knows the expected row count notices.
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. The recipe check advises (not refuses) a join with no `validate` ("write validate: m:1 or 1:1 so that a repeated key is refused") | An advice line at recipe check | Uses what exists; no new key | An advice can be ignored | 1 file (`recipe_check.py`), 1 session | D-0033 (no new keys) not touched |
| B. A declared rule on a table or join: "exactly N rows" / "no more rows than the left table", checked at load with a plain refusal (task RECIPE-ROW-COUNT-ASSERT) | A refusal that names the table, the expected and the real count | Catches every cause (repeated key, constant key, empty file) | A new recipe key: changes the spec (D-0033: unknown keys are refused) | 3 files + docs, 2 to 3 sessions | REOPENS the recipe spec; D-0033 |
| C. After each join the app shows the row count change in the data preview ("this join took 3 rows to 6") | A note next to the table | Shows the effect to every user, no spec change | Informs only; may not be seen | 2 files, 1 to 2 sessions | none |
| D. Leave it; the preparation script checks the one-row table; keep on the limits page | Nothing | Nothing to build | Silent wrong size stays | 0 | none |

**4. Recommendation.** A and C together are small, change no spec and tell the user; B is the real guard and is hers to decide (it adds a key). **B changes the recipe format: flag first.** Before the demo: the preparation script check and the sentence `validate: m:1` in the recipe help.
**5. What was not checked.** The app path (a recipe with the join opened in HOME): not run. Whether the recipe check refuses `how: cross` at check time (it did not name it; the engine refuses at run time with the quoted words). The `modif_join_where` join with an always-true predicate was not run.

## G5. The id rules read ONE id column per table; a pair table has two

**1. The problem, exactly.** Her cgMLST table has one line per pair of isolates, with two isolate columns. Her real small file (read only, `real_case/small`): 3 lines, `isolate1` holds test1, test2 and `isolate2` holds test1, test3. The isolate `test3` appears only in `isolate2`. RAN (`tmpAI/gaps/g5.py`, the app's own id reading and report): her real files alone give nothing to complete against (her information table is one row of constants with no isolate id column, so it takes no part in the ids), so nothing happens. With a metadata table that lists test1, test2 and test3 (synthetic), the id rules read only `isolate1` (the first id column declared; READ `id_completion.py:211`, marked PROVISIONAL at `:41`): they say "1 id of the metadata is not in this table: test3" and **add a line for test3 to the pair table**, empty distances, marked "missing in original table". The pair table goes from 3 to 4 lines, although test3 is there. The earlier study (RAN, 6 to 15 isolates) found two more effects: an isolate present only in `isolate2` and missing from the metadata (a typo, `ISO99`) is never reported; and "remove isolate X from all the data" removes only the lines where X is `isolate1`, X stays in the lines where it is `isolate2` (a half removal).
**2. The consequence.** Three silent effects: a false added line (distance counts change by one empty line), an invisible typo, a half removal that looks complete. Her recipe today avoids all three by declaring no id on the pair table.
**3. Options** (from the study `PAIR_TABLE_IDS_OPTIONS.md`, main checkout, not in git).

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| C. No id on the pair table (a recipe choice, works today) | Nothing added; no id check for the pair table; "remove from all" does not offer it | No code; the table stays exactly the file | The typo is not checked; the removal is written by hand on both columns | 0 | D-0589 not met for this table (an exception for her to confirm) |
| A. Ids are the values of BOTH columns; a line is added only for an isolate in neither | The warnings work; no false line; the typo is found | Meets every decided line; no rows doubled | "Remove from all" must write two steps for a table with two id columns (not decided) | 4 to 6 files + tests, 2 sessions | none reopened; the "first column" choice was PROVISIONAL |
| B / E. A "relation table" mark: checked, never completed | As A, no added lines | The table is exactly the file | A new recipe key; reopens D-0574, D-0586 and a sentence of D-0590 | 3 sessions | REOPENS D-0574, D-0586, D-0590 |
| D. Each pair written twice | Works with today's code | No change in the app | Plots count each pair twice; 176 MB at 2,000 isolates (RAN) | 0 | none |
| Leave it | The three effects | none | silent | 0 | none |

**4. Recommendation.** For the demo recipe: C. For the app: A. **It needs her decision on three small points** (the column an added line is written in; what "remove from all" does for two columns; the wording of the log). **B and D are not recommended: B reopens decisions, D changes counts silently.**
**5. What was not checked.** Her real information table has no id, so the false line was run with a synthetic metadata table, not her files together. A and B were simulated in the earlier study, not built. Nothing in a browser.

## G6. The ids are checked and completed only before tier 1

**1. The problem, exactly.** The app makes the ids equal and checks them when it reads a file, before any recipe step (READ `orchestrator.py` `_read_source`; `id_completion.py:8`; D-0613: there is no earlier or later place). A table whose isolate column comes into being at a later tier gets no check. RAN (`tmpAI/gaps/g6.py`, her real small pair table): at tier 2 the recipe unpivots the two isolate columns into one `isolate` column. The table after tier 2 holds test1, test2 and test3; the app, before tier 1, looked at `isolate1` only: test1 and test2. With a metadata that also lists `test4` (an isolate with no pair): a check at tier 2 would say "test4 is missing"; the check before tier 1 says "test3 and test4 are missing" (test3 wrongly).
**2. The consequence.** Not a wrong value but a missing or wrong warning: an id that is lost or wrong after a reshape is never reported; the ids after the reshape are never compared with the metadata. Nothing is added to the table at tier 2 (the completion is before tier 1 only), so a left join at tier 2 can leave an isolate out without a word.
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. Declare the id at the tier where it comes into being; check and warn there (the decided task, D-0702) | The same id warning for that table | Matches D-0702; no change to the data | A new recipe key (where the id is declared); the check must run on tier tables | 3 to 5 files, 2 sessions | D-0613 ("everything before tier 1") partly extended; D-0702 |
| B. Also add the lines at that tier (complete the reshaped table) | Lines added after the reshape | The "left joins always work" aim holds | More changes to data; reopens D-0613 | 4 sessions | REOPENS D-0613 |
| C. Leave it; the recipe maker checks the reshaped table (a visible step) | Nothing | Nothing to build | The check is missing for reshaped tables | 0 | none |

**4. Recommendation.** A (check and warn only), later, as decided in D-0702. It changes no data and tells the user more. B is not recommended: it adds data at a second place.
**5. What was not checked.** The orchestrator was read, not run on a recipe with a tier-2 reshape; the way the id would be declared is not designed (the task says check and warn only).

## G7. The plot id must be unique over all recipes, but the app does not check it at start

**1. The problem, exactly.** The rule (rules file, section 8; check X5, `check_recipe_set`): a plot id is unique over all the recipes of a folder. The check is run by the tests on the shipped folders (`test_every_recipe_follows_the_spec.py:211,217`) and by the Gallery manager (`gallery_manager.py:114`); the app does not run it over the recipes it discovers (READ: `grep check_recipe_set` finds no call in `app/` or in the bootloader). RAN (`tmpAI/gaps/g7.py`): two recipes that both have a plot `hist` give "[X5] the plot id 'hist' is also used in recipe_a". A user recipe copied into the recipe folder with a plot id of another recipe is not reported.
**What would happen** (READ, not run in the app): HOME makes ONE output slot per plot id (`home_theater.py:155-163`, a `seen` set) and each slot reads the plot of the recipe now open when it draws (`:898-912`), so a shared id probably draws the right plot. What is not known: whether anything else is keyed by plot id across recipes (the folder names of the export, the audit places `T3:<plot>`; steps are set aside when the recipe changes, so they do not cross).
**2. The consequence.** Probably none visible today; the rule exists because the two names collide in the page, and a later change could break it silently. The harm is a rule that the tests keep for shipped recipes and nobody keeps for the user's.
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. Run `check_recipe_set` at start over the discovered recipes; the later recipe goes to the rejected list with the X5 line | A recipe refused with the reason ("the plot id 'hist' is also used in recipe_a") | Keeps the decided rule; the reason is plain | Refuses recipes that open today; whose copy is "later" depends on order | 1 to 2 files (`bootloader.py`) + test, 1 session | X5, D-0534 (stands) |
| B. Relax the rule to "unique within a recipe" and check that nothing else is keyed by plot id | Nothing refused | Fewer refusals | Reopens the rule and D-0534; needs the checks that are not run | 2 sessions | REOPENS X5 / D-0534 |
| C. Leave it; the tests keep the shipped folders | Nothing | Nothing to build | User recipes unchecked | 0 | none |

**4. Recommendation.** A as a warning first (a line in the alerts, the recipe stays selectable), to see how often it happens; make it a refusal only if she wants it. **A refusal changes what opens today: flag.**
**5. What was not checked.** The behaviour of the app with two recipes sharing a plot id was read, not run; the export folders and the audit places were not run with a shared id.

## G8. Two app processes (or tabs) on one user place

**1. The problem, exactly.** Every try of an audit step is computed into a folder of its own under the user place (`audit_trial/<token>`, one token per browser session). At the start of an app process every folder under `audit_trial` is removed, because a killed process leaves its files (READ `bootloader.py:221-222`, `audit_trial.py:147-160`). RAN (`tmpAI/gaps/g8.py`): process A has a trial folder with a stored table; process B starts on the same user place; B's start removes A's folder (`removed: ['tokenA12345678']`). The code says so itself ("a decision for the owner: separate user places, or a process mark in the folder name").
What A then sees (READ, `audit_trial.py:220-232`): a trial whose files are gone is "no trial", never a failing table; the user tries the step again. Two TABS of one process each have their own token, so they do not clean each other. Two tabs on the same recipe and data share the audit folder (`audit_anchors`); a table another tab rewrote is refused with "was changed by another session on the same recipe and data and could not be built again here. Reload ..." (READ `audit_run.py:154`).
**2. The consequence.** Visible or harmless: a lost try, a message with a way out. No wrong result was found. The risk is bounded by the deployment: a server with several workers on one user place would hit it often.
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. State it as a deployment rule: one user place per process (docs, `deployment` page, a check at start that writes a lock file and warns when another process holds it) | A warning at start of the second process | Honest, small | A lock file can go stale after a crash | 1 session | D-0439, D-0440 (deployment decides) |
| B. A process mark in the folder name; the start removes only folders of a dead process | Nothing | The cleanup is safe | A way to know a process is dead (a pid file) | 1 session | none |
| C. Leave it and keep it on the limits page | Lost tries when a second process starts | Nothing to build | A multi-worker server loses tries | 0 | none |

**4. Recommendation.** B if a multi-worker deployment is planned (it makes the cleanup safe without any rule for the administrator); otherwise A as one sentence in the deployment page. Neither changes a result.
**5. What was not checked.** Two real processes were not started; the cleanup was run as a function on a scratch folder. The audit folder across two processes was not run.

## G10. A recipe step runs a formula through `eval`

**1. The problem, exactly.** A recipe step such as `polars_with_columns` holds a formula as text (`pl.col('a').cast(pl.Int8)`). The app checks the text against a list of allowed names and methods, then runs it with Python's `eval` with no builtins and only `pl` in scope (READ `formula_check.py:508-520`, `EVAL_GLOBALS`). A recipe written by someone else is therefore code that the check must hold back. RAN (`tmpAI/gaps/g10.py`, `evaluate_formula`): 12 attempts to leave the list were all refused with a plain line: `__import__` (a write to a canary file: **not written**), `getattr`, `__class__.__mro__...__subclasses__()`, `__init__.__globals__`, `__reduce__`, a lambda, a list comprehension, `map_elements` and `map_batches` with a Python function, `pipe(print)`, `pl.read_csv('/etc/passwd')`, `.eval(...)`. A plain `pl.col('a').cast(pl.Int8)` is allowed (the control).
**2. The consequence.** None found. A refused formula stops the recipe with a plain reason. The risk that remains is of other kinds that the check does not look at: a formula that is allowed but costs a lot of time or memory, and a mistake in the allow-list when Polars adds a method (the list is built from Polars itself: `_allowed`, `denied_methods`, so a new Polars method is allowed or denied by a rule, not by hand; not re-read).
**3. Options.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. Keep, and keep the 12 tries as a test that fails when one is allowed (mutation: allow `__import__`) | Nothing | Pins what was RAN today | Does not cover a new Polars method | 1 session | none |
| B. The sharing study (PROTOTYPE-SAFE-SHARING-STUDY): what a recipe from another person may do, a size/time limit, a review step | A plan | Needed before recipes are shared between users | Study, no code | 1 study | open |
| C. Leave it | Nothing | none | an unpinned guard | 0 | none |

**4. Recommendation.** A now (small, pins the result), B before any deployment in which users load recipes written by others.
**5. What was not checked.** Only the formulas of `evaluate_formula`; the function string of a plot (`function_string_problems`) and the smoother formula were not tried; cost or memory of an allowed formula; a Polars method added after the list was built. The test of A is written (`libs/utils/tests/test_formula_escape_tries.py`, 13 tests; with the check skipped 12 of them fail).

## G11. Who marked "User verified" is not recorded

**Decided, not built.** D-0670: the mark is called "User verified" and is written in the log (who, when). D-0677: "who" is the initials of the person, typed once per session, accepted for now; she notes it may be limited when several people work on one project (unusual; a solution comes later). Where: the mark is made in `app/modules/audit_add.py` (READ the guardrails row); the log does not exist yet (G12), so nothing is stored. **Missing:** the field for the initials, the place it is stored, and the log itself. Task AUDIT-WHO-IN-USER-VERIFIED waits for the log build. **Until then:** the export cannot say who verified a place; the user must not take the mark as a signature. Nothing was run; nothing needs her decision.

## G12. The audit log is not built

**Decided, not built.** D-0478: the audit log, with the warnings shown at each choice, is always exported with the audit recipe (no tick). D-0679: the design is accepted: one history file per session, a human-readable view made at each export, both at the top level of every export, with a closed list of events (design page `tmpAI/panel/audit_log/DESIGN_FOR_THE_OWNER.md`, main checkout, not in git). D-0689: the ids of removed rows are stored inside the step's record, one list per place, with a warning system for size. D-0682: the BUILD waits until she is sure the quotas allow it. **Missing:** everything: the file, the events, the export part, the size limits (not decided: D-0689 names none). **Until then:** the export holds the audit recipe and the steps with their reasons, not the history of what was added, removed or tried. The data changes of G2 would be events of this log. Size: not estimated here (REASONED: 3 to 5 sessions).

## G13. The demo-case slices D1 to D4 (decided direction, not built)

**Decided, not built.** D-0698: the structure check at app start and the data check at upload; a recipe without data is selectable with an empty state; a rejected recipe is taken back when its data appears, with no restart (D1; the study RAN that today such a recipe is refused at start and does not come back without a restart). D2: no recipe selected at start (HOME-NO-RECIPE-AT-START). D-0699: the file name, date and hash of each upload recorded with the session (D3). D-0700: the choice at an upload is the user's, not automatic (D4). **Corrected by her on 2026-11-28 (relayed):** an audit is linked to its dataset, an upload of other data starts a NEW audit on the original recipe, and steps are never carried to other data; what remains of the old "Update this session / Start a new session" is open (the session container; see the options page). The tasks line of D4 was corrected. D-0701: going back means choosing the previous session of the same recipe, and the session brings its data (how: the options page). **Missing:** all four slices. The guard of G1 (built) is the interim floor. **Until then:** a recipe with no data is refused at start; an upload makes a new session by itself (G2).
