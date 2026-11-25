# SONNET draft: no blocking action, only warnings (her M638, ledger D-0581), 2026-11-23

Reading only, no run, no study file edited. One round, short (D-0580). Data agnostic. Her words are exact; "the review session's reading" is not hers. Tags: [HER WORDS D-0581] / [CODE READ file:line] / [TODAY] / [TO BUILD] / [REASONED].

Contents: (A) the new section for `CAUSE_AND_SOLUTIONS_ZEROS.md`; (B) the marks in the D-0573 to D-0579 section; (C) the note for `OVERLAP_AND_POPULATION.md` (fourth part).

---

## (A) The new section (paste after the D-0573 to D-0579 section, before the `---` that precedes `## THE CAUSE, AND WHAT WAS FOUND`)

## Added 2026-11-23 (ledger D-0581, D-0582): no blocking action, only warnings; automatic completion and automatic log; a red warning with a button

Not in the text above. It answers her question 1 and reopens some earlier words; the earlier lines are kept and marked "changed by D-0581" where they stand.

### Her words, exact

"I was looking at what the coordinator has posted about agents review work. I see one point the reviewers are correct : deployement without panel would be blocked so we need them to work without requesting confirmation. The deployement without panel means no user can accept anything - means that the ids missing ids (2 sided) needs to be fed automatically and the recipe needs to tell how those cases must be processed. Deployement without user agreement are expected from pipelines and data that arrives at regular updates - which means that those cases have to be thought before hand to ensure at best that cases of missing data id are limited - and they need to be treated correctly from the recipe at once. Which means that we cannot have blocking actions - only warnings - automatic fixing in the recipes and then ensuring that those cases are handled appropriately. Which means that the logs of the app including also the missing ids must also be written automatically in a specific directory.  This solution also allows the user to fix the metadata, add dummy and can upload again while letting the static deployements work. I think that answers Q1 - Both notes at once - and cannot be a hard stop - so it reopens one of my decision to allow deployements with no panel (static deployements) - But when the user has the panel important to have this warning in RED" [HER WORDS D-0581]

**Block M639 (ledger D-0582), her answer on what the user gets with a panel:** "This is correct - the user / person utilizing the results MUST read that log. b) that is good. And that allows the user to upload if he wants to." [HER WORDS D-0582] (The question she answered, put by the review session: with a panel, (a) a red warning only, or (b) a red warning and an "I have read this" button that does not block, the click recorded in the log; she chose (b).)

### What her words decide

- **No blocking action, only warnings.** "we cannot have blocking actions - only warnings".
- **The missing ids, on both sides, are fed automatically** where no user can accept ("The deployement without panel means no user can accept anything - means that the ids missing ids (2 sided) needs to be fed automatically"; with a panel: D-0582), and "the recipe needs to tell how those cases must be processed"; the cases are "treated correctly from the recipe at once".
- **The logs of the app, the missing ids included, are written automatically in a specific directory.**
- **Question 1 is answered: "Both notes at once - and cannot be a hard stop".** The two checks (ids of a result file not in the metadata; ids of the metadata not in a result file) both show their note, and nothing stops.
- **Where there is a panel, the warning is in RED.**
- **The user can still fix the metadata, add a dummy id and upload again**: "This solution also allows the user to fix the metadata, add dummy and can upload again while letting the static deployements work."
- **Deployments with no panel work without a confirmation**: "no user can accept anything".
- **With a panel: a red warning and a button "I have read this" that does not block; the click goes into the log of the ids; with no panel the log says "automatic, no user".** Her words: "This is correct - the user / person utilizing the results MUST read that log. b) that is good. And that allows the user to upload if he wants to." [HER WORDS D-0582]. (The button and what it records are the review session's question, which she answered with "b) that is good".)

### What this changes in her earlier words (each earlier line is kept)

| Earlier line | Now | Status |
|---|---|---|
| D-0573: "refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)" | a red warning and an automatic handling, not a refusal (the review session's reading; "it must not contain errors nor missing data. A rule" stays as the goal and as the warning) | CHANGED by D-0581 |
| D-0573: "A user confirm is good" and D-0574: "the user must only to accept once" | the confirmation is replaced: with a panel, a red warning and an "I have read this" button that does not block (the completion is applied anyway; the click goes into the log of the ids); with no panel the completion is automatic and the log says "automatic, no user" (the review session's reading of her "b) that is good", D-0582) | CHANGED by D-0581 and D-0582 |
| D-0579 (M635): "stopping first no ?" | answered: no stop, both notes at once | ANSWERED |
| D-0569 (b): the data check only informs | consistent | UNCHANGED |
| D-0574: the completion lives in the recipe, required on every result table; the recipe does not record the count | stays; the recipe states how the marked cases are processed | UNCHANGED |
| D-0575, D-0576: the record is in the export; a separate log | stays; the log is now written automatically, in a specific directory, also where no session exists | EXTENDED |
| "reopens one of my decision to allow deployements with no panel (static deployements)" | **her words say "reopens"; the review session reads that her decision to allow such deployments stands and the new principle is what lets them work** ("letting the static deployements work"). One line to confirm with her | TO CONFIRM |

### Where her words do NOT say something (points for her)

1. **Answered by D-0582** ("b) that is good"): with a panel, a red warning and an "I have read this" button that does not block; the user may upload a corrected metadata whenever he wants. Still hers: once per data batch or at each opening; what is recorded with no session; how the user reaches the log and what the export says (questions 9 and 10 below).
2. **"The missing ids, 2 sided, are fed automatically": what is fed for an id of a result file that is not in the metadata?** For the other side (an id of the metadata not in a result file) her earlier words say: a line with the marker "not in original data". For this side her earlier flow had NO marker and the user added the id by hand. Automatic means the app does it. Options: (i) nothing is added to the metadata; the warning is red and logged; a join from the result table keeps the rows with empty metadata values (what the lesson template shows today); (ii) a line is added to the metadata table for the id, every other column empty, with a marker (a second marker, "not in metadata": this reverses the earlier "no marker"); (iii) the recipe says how, with no app default. What she would see: on `left_join_lesson`, 2 ids (`ACC0001`, `ACC0002`) of the file `sequenced` are not in its metadata [ESTABLISHED: OVERLAP section 1]: (i) the 2 rows keep empty metadata and a red warning; (ii) the metadata gains 2 lines marked "not in metadata"; on the demo nothing (0 ids outside the metadata). Lean (Sonnet, as a lean): (ii), because her words say both sides are fed and a recipe that is told how to process "those cases" needs the cases to be marked; to confirm that a second marker is what she means. Lean (Opus, as a lean): (ii) as well, for the same reason. What (ii) changes, said plainly: the entity enters the metadata table, so it enters every table that starts from the metadata with its metadata values empty (a count per entity includes it; a plot by country shows an empty country); with no panel only the log and the export say so. Neither: say what you meant.
3. **A line of the metadata with no usable id** (empty, spaces, `-`). It cannot be matched and cannot be completed. Under "no blocking" what happens to it? (a) kept: it stays in the metadata table, a red warning names the lines, the log records them; the recipe may drop it by a visible step as `demo_abromics` does (`demo_abromics.yaml:44-47`); (b) dropped by the app before the recipe reads, warned and logged; (c) the app does nothing and does not warn. Kept lines count: a grouping by the id makes one entity of all missing ids, an anti-join lists each [POLARS SEMANTICS; ESTABLISHED: CAUSE, D-0570 fact 6]. What she would see: the demo's metadata has none (42 distinct ids); `demo_abromics` as shipped has 3 lines (file lines 5, 6, 11): (a) red warning, 3 lines, then the recipe's own step removes them; (b) the app removes them first. Lean (Sonnet): (a): nothing is changed in the data without the recipe saying so (D-0574: "it would modify the recipe" is her argument for the log). Lean (Opus): (a), and the recipe states how such lines are processed, as for the marked lines, so that no line without an id enters a result without a written rule; a line that stays enters every table that starts from the metadata as one more entity, and with no panel only the log and the export show it. Neither: say what you meant.
4. **What happens to an id repeated in the metadata** is not said either; the same options as 3.

### Two cautions (points for her, not corrections)

**1. An unattended pipeline completes a never-analysed entity with only the log as witness.** With no user and no confirmation the 4 added lines of `ResFinder` (on the demo) exist in the table with the marker "not in original data" and nothing on any screen. What must the required meaning say, and where does the reader of a published figure learn it? Her own rule: the same record is in the export (D-0575), which is also written without a user [RULE FILE `rules_app_features_flags.md`: `export_enabled` true in the static profile]. Already decided: the record is in the export ("yes that must be in the export" [HER WORDS D-0575]), and "the user / person utilizing the results MUST read that log" [HER WORDS D-0582]; so the README and the report carry a line such as "N lines were added automatically: read the log" (words PROVISIONAL). Point for her: whether the required meaning is chosen from a few words (so that "analysed, nothing found" is a deliberate statement and not a default) or free text.

**2. A deployment where nothing can be written must still not block.** Read:
- The user folder is the deployment's `user_data` (Location 4): `bootloader.get_location("user_data")` returns the resolved path and raises `KeyError` if the key is not defined [CODE READ `app/src/bootloader.py:846-855`]; the five location keys are required [CODE READ `bootloader.py:348-360`]; `local.yaml:13-26` lists `raw_data`, `data_analysis_recipes`, `cache`, `user_data`, `gallery`.
- Today `SessionManager(bootloader.get_location("user_data"))` is built at `app/src/server.py:150` and its constructor does `self.root.mkdir(parents=True, exist_ok=True)` with no handler [CODE READ `app/modules/session_manager.py:272-274`]: a folder that cannot be created raises at that line. **I found no handler for it by reading** (no try/except around `server.py:150`; I did not search the whole app). The stored tables folder `user_data/anchors` is read at `bootloader.py:204`; what it does when the folder is missing: not read.
- So today a non-writable user folder is not a warning: it ends the session start. That is the opposite of her principle; it is a point for the build, not an answer.
- **What exists for "a specific directory" for logs** (not invented): under `user_data` there are already `_sessions/<session_key>/` [CODE READ `session_manager.py:270, 314-317`], `_imports/<recipe id>/data/` [CODE READ `bootloader.py:857-861`] and `anchors/` [CODE READ `bootloader.py:204`]. Nothing exists for logs. A log directory would be a new sub-folder of `user_data` (next to those), or a place of its own in the deployment file; which, and whether a deployment may name it, is hers. Where the folder cannot be written: the log cannot be kept; to not block, the record goes into the export and the console, and the red warning says "the log could not be written". Points for her: that rule, and whether the export is then the only record.

### The updated list: what her new words do to each of the 15 questions

| # | Question (list of D-0573 to D-0579) | Now | New plain wording, with what she would see |
|---|---|---|---|
| 1 | Result-file ids not in the metadata: stop or go on? | **ANSWERED by D-0581**: both notes at once, never a hard stop | |
| 2 | Which id errors refuse the metadata? | **REWRITTEN**: refuse nothing; which id errors raise a red warning, and what happens to the line (point 3 above) | "A line of the metadata with no usable id: kept and warned, dropped and warned, or nothing?" On the demo: none; `demo_abromics`: 3 lines. Lean: kept and warned. Neither: say what you meant |
| 3 | Where does the refusal sit, order of the checks? | **DISSOLVED as a refusal; REWRITTEN**: where is the warning shown and written | "With a panel, the red warning is at the opening of the recipe, in Data Import after an upload, and in BLUEPRINT's check; with no panel, it is in the log and in the export. Is that all the places?" On the demo: a bad upload shows red and the file is taken (no refusal). Lean: those places. Neither: say what you meant |
| 4 | If the user does not confirm | **ANSWERED by D-0582**: with a panel, the red warning and the "I have read this" button that does not block; with no panel, "automatic, no user" in the log | |
| 5 | The marker and "not a zero" | **REWRITTEN** (sharper): unattended, the recipe's required meaning is the only treatment | "Must the required meaning be chosen from a few words, and does the export always say how many lines were added automatically?" (caution 1). Lean (both): few words. Neither: say what you meant |
| 6 | The block: form, tables, names | UNCHANGED | |
| 7 | The position | UNCHANGED | |
| 8 | Which metadata | UNCHANGED | |
| 9 | What asks again; where no session | **REWRITTEN** (D-0582): nothing is accepted any more; the click is recorded | "The red warning and its button "I have read this": once for each data batch (until the data or the recipe change) or at each opening? With no panel: is the log entry "automatic, no user" with the export the whole record?" On the demo with a panel: "4 ids of the metadata have no line in ResFinder: 4 lines added, marked "not in original data". [I have read this]", once per batch or at each opening; in `pipeline-static` no button, and the log says "automatic, no user". Lean: once per data batch (her word "Once per data batch" [D-0574]); with no session, the log in its directory and the export. Neither: say what you meant |
| 10 | The log | **REWRITTEN**: automatic, in a specific directory, also where no session exists; and when nothing can be written | "Where is the log directory (a sub-folder of `user_data`, or a place named in the deployment)? Since the person using the results MUST read it: does the red warning carry a link that opens the log of this data batch, and does the export hold the log, name it in the first line of the README and give it a section of the report?" Today the export has README.txt (a list of its files) and report.qmd with a section "Processing Issues During Session" that says "Review these before publishing results" [CODE READ `export_handlers.py:2012-2024, 2276-2300`]; no log of the ids exists, and the audit log (D-0478) is decided and not built. On the demo the bundle would hold the log with ResFinder's 4 ids, named first in the README. If the directory cannot be written, the export and the console carry the record. Lean: a sub-folder of `user_data`; a link from the warning; the log in the export, named first in the README and in the report. Neither: say what you meant |
| 11 | A dummy id | UNCHANGED (she says the user can still add one) | |
| 12 | The join order | UNCHANGED | |
| 13 | A recipe with no metadata block | UNCHANGED (the checks cannot run: a warning, not a block) | |
| 14 | The count per target | UNCHANGED | |
| 15 | The threshold | UNCHANGED | |
| new A | What is fed for a result-file id not in the metadata | NEW (point 2) | |
| new B | Whether her decision to allow no-panel deployments "reopens" | NEW, one line to confirm | |

### The next order, one at a time

1. **What is fed for a result-file id that is not in the metadata** (new A). Lean: a line with a marker.
2. **A metadata line with no usable id** (rewritten 2). Lean: kept and warned.
3. **The button "I have read this": once per data batch or at each opening; the record with no session** (rewritten 9; question 4 answered by D-0582). Lean: once per data batch.
4. **Unattended: what the required meaning must say; the marker** (rewritten 5). Lean: few words.
5. **The block: form and tables** (6). Lean: block the app reads; declare the id first.
6. **Position** (7) and **which metadata** (8). Lean: before; as read.
7. **The log: its directory, when nothing can be written, how the user reaches it from the warning, how the export points to it** (rewritten 10; "MUST read that log", D-0582). Lean: a sub-folder of `user_data`; a link from the warning; named first in the README and the report.
8. **Where the red warning shows** (rewritten 3).
9. **A dummy id** (11). Lean: a note in the log.
10. **The join order** (12). Lean: an advice.
11. **A recipe with no metadata block** (13); **count per target** (14); **threshold** (15).
12. **One line to confirm**: her decision to allow no-panel deployments stands (new B).

---

## (B) The marks in the D-0573 to D-0579 section (blockquotes, history kept; nothing deleted)

- Under the table "What is DECIDED in her words, and what is only the review session's reading", after it:
> **Changed by D-0581 (2026-11-23):** row 1 ("The metadata is refused ...") becomes a red warning and an automatic handling, not a refusal (the review session's reading); the rule "it must not contain errors nor missing data" stays as the goal. The confirmation in the rows of check Y and of "once per data batch" is changed for deployments with no panel (no user can accept): the completion is automatic and logged "automatic, no user"; with a panel it is not answered. The row on "stopping first" is answered: both notes at once, never a hard stop.
- Under the flag `3. A refusal at the gate closes the recipe`: `> **Changed by D-0581:** no check refuses or closes a recipe; the flag stays as history. The risk that remains is a deployment where nothing can be written (see the new section).`
- Under the heading `### The two checks, their order and the stop (her question D-0579)`: `> **Answered by D-0581 (2026-11-23):** both notes at once, never a hard stop. The case for and against is history. The reading (c) of "stopping first" is hers; (a) and (b) are void.`
- Under each of the questions 1, 2, 3, 4, 9 and 10 of the list `#### (c) The new list`: `> **Changed by D-0581:** see the table "The updated list" in the section "Added 2026-11-23 (ledger D-0581)".` (questions 1 and 4 ANSWERED, by D-0581 and D-0582; 2, 3, 9, 10 REWRITTEN.)
- Under the line `**Block M630 (ledger D-0574).**`'s "the user must only to accept once": `> **Changed by D-0581 and D-0582:** with no panel nobody can accept; automatic, logged "automatic, no user". With a panel: a red warning and an "I have read this" button that does not block (her "b) that is good"; the button is the review session's reading of the question she answered).`
- Under the line `Block M632 (ledger D-0576)`: `> **Extended by D-0581:** the log is written automatically, in a specific directory, also where no session exists.`

---

## (C) The note for `OVERLAP_AND_POPULATION.md` (fourth part, "Her answers of 2026-11-23, fourth part ...")

Directly under its table of steps (0), X, Y, add:

> **Changed by D-0581 (2026-11-23; ledger D-0581):** no step blocks or refuses. Step (0) (the metadata's own ids) "refuses" is read as a red warning and an automatic handling (what happens to a line with no usable id is her open point). Check X (ids of a result file not in the metadata) and check Y (ids of the metadata not in a result file) are shown together, both as warnings, never as a hard stop; the order and the stop of her question are answered. Check Y completes automatically, with the marker and the recipe's required meaning; with a panel the warning is red; with a panel the user gets an "I have read this" button that does not block, and the click goes into the log (D-0582). What is "fed" for X's ids is a new point for her (a line in the metadata with a marker, or nothing). The log of the missing ids is written automatically in a specific directory (not yet named). The sentence "two points that concern this file (1) ... if X stops the recipe, D-0569 (b) is reversed" is history: X does not stop, and D-0569 (b) holds.
