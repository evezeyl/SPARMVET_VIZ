# Opus check of SONNET_noblock_1.md (D-0581), with her D-0582 (M639) added, 2026-11-23

Reading only. "draft N" = line N of `SONNET_noblock_1.md`.

**Checked and right:**
- Her M638 words are exact (fixed-string search); D-0581 and D-0582 are in the ledger.
- The code facts:
  - `session_manager.py:272-274` (mkdir, no handler);
  - `server.py:150`;
  - `bootloader.py:204` (`user_data/anchors`), `348-360` (five required location keys), `846-855` (`KeyError`), `857-861` (`_imports`);
  - `local.yaml:13-26`.
- The table of what D-0581 changed, the cautions, and the order are sound, except as below.

**Flags (a result changed without a message under "automatic completion, no user"):**
- (1) A never-analysed entity is completed with only the log and the export as witness. The draft's caution 1 covers it; R7 below makes the export line decided.
- (2) An id of a result file fed into the metadata changes the population of every table that starts from the metadata (R4).
- (3) A metadata line with no id, if kept, enters those tables as one more entity (R5).
- (4) The same data and recipe give the same table in every deployment only because the button of D-0582 changes nothing (R9).

## Replacements (old → new)

**R1. draft 22** (her words tie "fed automatically" to deployments with no panel).
Old: `- **The missing ids, on both sides, are fed automatically**, and "the recipe`
New: `- **The missing ids, on both sides, are fed automatically** where no user can accept ("The deployement without panel means no user can accept anything - means that the ids missing ids (2 sided) needs to be fed automatically"; with a panel: D-0582, R9), and "the recipe`

**R2. draft 26** ("the recipe works meanwhile" is the review session's reading, not her words).
Old: `- **The user can still fix the metadata, add a dummy id and upload again**, while the recipe works meanwhile.`
New: `- **The user can still fix the metadata, add a dummy id and upload again**: "This solution also allows the user to fix the metadata, add dummy and can upload again while letting the static deployements work."`

**R3. draft 33** (ellipses inserted into her quote).
Old: `| D-0573: "refuse the metadata ... that contains errors or missing data (at the id level only ...)" |`
New: `| D-0573: "refuse the metadata (it is the responsability of the user) that contains errors or missing data (at the id level only - there can be true metadata that is missing but not in the id)" |`

**R4. draft 44** (flag 2, and my lean).
Old: `to confirm that a second marker is what she means. Neither: say what you meant.`
New: `to confirm that a second marker is what she means. Lean (Opus, as a lean): (ii) as well, for the same reason. What (ii) changes, said plainly: the entity enters the metadata table, so it enters every table that starts from the metadata with its metadata values empty (a count per entity includes it; a plot by country shows an empty country); with no panel only the log and the export say so. Neither: say what you meant.`

**R5. draft 45** (flag 3, and my lean).
Old: `(D-0574: "it would modify the recipe" is her argument for the log). Neither: say what you meant.`
New: `(D-0574: "it would modify the recipe" is her argument for the log). Lean (Opus): (a), and the recipe states how such lines are processed, as for the marked lines, so that no line without an id enters a result without a written rule; a line that stays enters every table that starts from the metadata as one more entity, and with no panel only the log and the export show it. Neither: say what you meant.`

**R6. draft 46** (wording wrong).
Old: `4. **Which deployments take the repeated id of the metadata** is not said either;`
New: `4. **What happens to an id repeated in the metadata** is not said either;`

**R7. draft 50** (the export record is decided, D-0575).
Old: `Points for her: whether the required meaning is chosen from a few words (so that "analysed, nothing found" is a deliberate statement and not a default) or free text; whether the export's README and report always carry a line "N lines were added automatically, see the log".`
New: `Already decided: the record is in the export ("yes that must be in the export" [HER WORDS D-0575]), and "the user / person utilizing the results MUST read that log" [HER WORDS D-0582]; so the README and the report carry a line such as "N lines were added automatically: read the log" (words PROVISIONAL). Point for her: whether the required meaning is chosen from a few words (so that "analysed, nothing found" is a deliberate statement and not a default) or free text.`

**R8. draft 56** (line number).
Old: ``[CODE READ `session_manager.py:271, 314-317`]``
New: ``[CODE READ `session_manager.py:270, 314-317`]``

**R9. After draft 27, insert** (her D-0582):
`- **With a panel: a red warning and a button "I have read this" that does not block; the click goes into the log of the ids; with no panel the log says "automatic, no user".** Her words: "This is correct - the user / person utilizing the results MUST read that log. b) that is good. And that allows the user to upload if he wants to." [HER WORDS D-0582]. (The button and what it records are the review session's question, which she answered with "b) that is good".)`

**R10. draft 34** (the confirmation is replaced by the button).
Old: `| with no panel nobody can accept: the completion is automatic, logged as "automatic, no user" | CHANGED by D-0581 for no panel; **NOT answered by her words where there is a panel** (below) |`
New: `| the confirmation is replaced: with a panel, a red warning and an "I have read this" button that does not block (the completion is applied anyway; the click goes into the log of the ids); with no panel the completion is automatic and the log says "automatic, no user" (the review session's reading of her "b) that is good", D-0582) | CHANGED by D-0581 and D-0582 |`

**R11. draft 43** (point 1 is answered).
Old: `1. **With a panel: is a confirmation still asked, once per data batch?** She says no-panel deployments must work without one. For a user at a screen her words do not say. Two behaviours: (a) the same everywhere: red warning, automatic completion, log "automatic"; (b) with a panel, a confirmation once per batch, without one the automatic path.`
New: `1. **Answered by D-0582** ("b) that is good"): with a panel, a red warning and an "I have read this" button that does not block; the user may upload a corrected metadata whenever he wants. Still hers: once per data batch or at each opening; what is recorded with no session; how the user reaches the log and what the export says (questions 9 and 10 below).`

**R12. draft 65** (question 4 answered).
Old: `| **DISSOLVED** for no panel (no confirmation exists). **REWRITTEN** for a panel | "With a panel: a confirmation once per batch, or only the red warning and the automatic completion?" On the demo: a dialog "4 lines will be added to ResFinder. Confirm?" or only a red line and the log. Lean: the same everywhere. Neither: say what you meant |`
New: `| **ANSWERED by D-0582**: with a panel, the red warning and the "I have read this" button that does not block; with no panel, "automatic, no user" in the log | |`

**R13. draft 70** (question 9 rewritten, with what she would see).
Old: `| **DISSOLVED** if the completion is automatic everywhere (nothing is accepted); **kept** only if question 4 keeps a confirmation with a panel | decided by the answer to the new question 3 below |`
New: `| **REWRITTEN** (D-0582): nothing is accepted any more; the click is recorded | "The red warning and its button "I have read this": once for each data batch (until the data or the recipe change) or at each opening? With no panel: is the log entry "automatic, no user" with the export the whole record?" On the demo with a panel: "4 ids of the metadata have no line in ResFinder: 4 lines added, marked "not in original data". [I have read this]", once per batch or at each opening; in `pipeline-static` no button, and the log says "automatic, no user". Lean: once per data batch (her word "Once per data batch" [D-0574]); with no session, the log in its directory and the export. Neither: say what you meant |`

**R14. draft 71** (question 10: "MUST read that log").
Old: `"Where is the log directory? A sub-folder of `user_data`, or a place named in the deployment? If it cannot be written, the export and the console carry the record." Lean: a sub-folder of `user_data`. Neither: say what you meant |`
New: `"Where is the log directory (a sub-folder of `user_data`, or a place named in the deployment)? Since the person using the results MUST read it: does the red warning carry a link that opens the log of this data batch, and does the export hold the log, name it in the first line of the README and give it a section of the report?" Today the export has README.txt (a list of its files) and report.qmd with a section "Processing Issues During Session" that says "Review these before publishing results" [CODE READ `export_handlers.py:2012-2024, 2276-2300`]; no log of the ids exists, and the audit log (D-0478) is decided and not built. On the demo the bundle would hold the log with ResFinder's 4 ids, named first in the README. If the directory cannot be written, the export and the console carry the record. Lean: a sub-folder of `user_data`; a link from the warning; the log in the export, named first in the README and in the report. Neither: say what you meant |`

**R15. draft 84.**
Old: `3. **With a panel: a confirmation, or only the red warning** (rewritten 4; settles 9). Lean: the same everywhere.`
New: `3. **The button "I have read this": once per data batch or at each opening; the record with no session** (rewritten 9; question 4 answered by D-0582). Lean: once per data batch.`

**R16. draft 88.**
Old: `7. **The log directory, and when nothing can be written** (rewritten 10). Lean: sub-folder of `user_data`.`
New: `7. **The log: its directory, when nothing can be written, how the user reaches it from the warning, how the export points to it** (rewritten 10; "MUST read that log", D-0582). Lean: a sub-folder of `user_data`; a link from the warning; named first in the README and the report.`

**R17. draft 103.**
Old: `(question 1 ANSWERED; 2, 3, 4, 10 REWRITTEN; 9 DISSOLVED or kept with question 4.)`
New: `(questions 1 and 4 ANSWERED, by D-0581 and D-0582; 2, 3, 9, 10 REWRITTEN.)`

**R18. draft 104.**
Old: `` `> **Changed by D-0581:** with no panel nobody can accept; automatic. With a panel: not answered.` ``
New: `` `> **Changed by D-0581 and D-0582:** with no panel nobody can accept; automatic, logged "automatic, no user". With a panel: a red warning and an "I have read this" button that does not block (her "b) that is good"; the button is the review session's reading of the question she answered).` ``

**R19. draft 113.**
Old: `whether a confirmation is still asked where there is a panel is not in her words.`
New: `with a panel the user gets an "I have read this" button that does not block, and the click goes into the log (D-0582).`

**R20. draft 100** (a reading presented as decided).
Old: `becomes a red warning and an automatic handling, not a refusal;`
New: `becomes a red warning and an automatic handling, not a refusal (the review session's reading);`

## Closing

I sign the draft with these replacements applied.
