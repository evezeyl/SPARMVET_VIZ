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
| (more rows are added as each section is written) | | | | |


## G1. Steps of one dataset applied to another (Restore on other data)

**Built on 2026-11-28 for the Restore (commit `fix(session)!: a restore on other data is refused`). One half of the problem is still open: the live view.**

**1. The problem, exactly.** Eve's example, the small and the large pair table. The user works on the small data and adds an audit step ("year > 1900", reason "made on small data"). She uploads the large files. A second session appears by itself (its key holds a hash of the data files; RAN earlier, `tmpAI/demo_upload_study/upload_sessions_run.py`: small key `...:775f2013ce39`, large key `...:6102f4cd7...`). Then she presses Restore on the small session. Before: a yellow warning "Session was saved against a different data batch", and the steps were put on the large data. After the change: an error names the session's files and the files now loaded (file name, 8-letter hash) and nothing of the session is put into the view (RAN: `app/tests/test_restore_on_other_data_refused.py`; with the guard switched off the steps are applied: the test fails, so it can fail).
**The open half (RAN, `tmpAI/gaps/g1_live.py`).** She is in the view with a step made on the small data. The data on disk changes (an upload). HOME updates its data key by itself (READ `home_theater.py` `_sync_session_provenance`, `needs_update`) but keeps the steps in the view, and tells her that "a source data file changed ... reload". If she adds one more step without reloading, ALL steps of the view are written under the new data key (READ `audit_session_save.py:44-56`). Run: one step made on key `1111...`, the key changed to `2222...`, the next save: two session folders, each holding the same step. The step made on the small data is now in the large data's session.
**2. The consequence.** Before the fix: silent (a warning that disappears after 8 seconds), the audit table and figure can be wrong for the data on screen, and the export would say the step was made on these data. After: the Restore cannot mix. The live case is still silent after the first message.
**3. Options for the live case.**

| Option | What the user sees | Pro | Con | Size | Decided lines |
|---|---|---|---|---|---|
| A. When the data on disk change while steps are in the view, the view stops accepting steps and says: "the data changed; your steps were made on the earlier data: start a new session (steps are not carried) or reload" | A clear block at the moment of change; Add is greyed with the reason | Closes the hole in one rule; consistent with the Restore | The user loses the steps in the view unless she exports first | 2 files (`home_theater.py`, `trial_handlers.py`), about 1 session | Eve 2026-11-28 (steps never mix); D-0302 untouched |
| B. At the data change a choice is asked: "Update this session (steps are kept and marked made on other data)" or "Start a new session" | A two-button choice | Fits her wish for a mechanism that takes the change into account | Needs the sessions options page decision first (where the data of a session lives, what a marked step means) | 3 to 5 files, 2 sessions | Eve 2026-11-28 point 3; reopens D-0434 in part |
| C. Leave it and keep it on the limits page | The first message only ("reload the page") | Nothing to build | The silent mixing stays | 0 | none |

**4. Recommendation.** A now (it is the same rule as the Restore, small), B later with the sessions options page. **Flag first: A changes what a user can do after an upload (she cannot add steps until she starts a new session), but it removes a silent wrong result.**
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
| A. A store by content hash: each upload kept once; the session records name, date and hash per file; at upload "Update this session / Start a new session" | Two buttons at upload; Restore finds its data | The way back is the app's job; no duplicate files | Disk grows; a rule for deleting; deployments with pipeline data (`by_dataset_id`) refuse uploads | 3 to 5 sessions | REOPENS D-0434 (no copy); touches D-0439, D-0440, contract 12d |
| B. A copy per session in the session folder | Same buttons | Simple to delete with the session | Copies of the same file per session (her real files are small, 88 MB for 2,000 isolates) | 3 sessions | REOPENS D-0434 |
| E. Today plus the guard (built): she keeps her own copies and uploads them again | An error at Restore that names the files | Nothing more to build | The replaced file is lost unless she kept it; a session still appears by itself | 0 more | D-0434 kept |
| Leave it, keep it on `current_limits.md` | As today | none | silent loss stays | 0 | none |

**4. Recommendation.** E stays as the floor (it is built). **It reopens a decision (D-0434) as soon as the app keeps data: that is hers to decide.** If she wants the way back from the app, A (a store by hash, reading from the store by hash rather than re-placing files, because re-placing changes what every other session reads). The choice at upload ("Update this session / Start a new session") is the same slice as option B of G1 and should be built with it.
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
**5. What was not checked.** Which invisible characters a real lab export writes (her files hold none that I could find: the real demo tables were not scanned for odd characters); the full app path (the warning in HOME) was not opened in a browser.
