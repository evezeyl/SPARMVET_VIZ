Written by Opus for D-0591, D-0592
Target: `.claude/design/studies/whole_picture_2026-11/CAUSE_AND_SOLUTIONS_ZEROS.md` (dev 01e4e206). Each anchor occurs exactly once (fixed-string search). Her words are copied from the channel blocks M651 and M652.

## BLOCK 1. INSERT AFTER the line that begins `   > **ANSWERED by D-0590:** the union`
`   > **CONFIRMED by D-0591:** "the union" is now her word: "the unique ids in all datasets + metadata when exist should be the unions of all the unique ids".`

## BLOCK 2. REPLACE `## THE CAUSE, AND WHAT WAS FOUND` BY the lines up to END BLOCK 2:
### Added 2026-11-23 (ledger D-0591, D-0592): the union confirmed; the size of a mismatch; a simple log

**Her words, exact.** "yes . basically as the reviewer is writing now in his review the unique ids in all datasets + metadata when exist should be the unions of all the unique ids - if there many that do not match it means there is a problem in eg. a pipeline" [HER WORDS D-0591]. "yes it can be a log as simple as : the ids are written differently in the different output of a pipeline eg program1-ID1 program2-ID1 which means some cleaning here would need to be done ... before entering our system (eg. lab)" [HER WORDS D-0592]

**What her words say.**
- After the completion, the unique ids of every dataset, and of the metadata when it exists, are the union of all the unique ids. Many ids that do not match mean a problem upstream ("in eg. a pipeline").
- The log can be simple. Her example: ids written differently by two programs (`program1-ID1`, `program2-ID1`); the cleaning is done "before entering our system (eg. lab)".

**Readings, not her words (to confirm).**
- **No threshold for "many":** the log gives the numbers and the unmatched ids only; her "yes" answered the review session's option "no threshold, the numbers only".
- **Per table, the log lists** how many ids of how many do not match, and the ids themselves, side by side where it can, so that a pattern such as a program prefix is seen at once. The mechanism does not clean; it shows.
- **What it would show, words PROVISIONAL** [ESTABLISHED: OVERLAP section 1]: on the demo, "ResFinder: 4 of 42 ids of the metadata have no line: <ids>"; on `left_join_lesson`, "sequenced: 2 ids are not in the metadata: ACC0001, ACC0002".

**Where the documentation may point for the cleaning (by reading).**
- **What the tool does:** Test Lab's ID Reconciliation compares ONE key column of TWO files per run [RULE FILE `.claude/rules/rules_test_lab.md` section 5]. It finds exact matches, patterns (a prefix or suffix removed, a change of case, a part taken at a delimiter) and fuzzy matches, and writes the fix as a reusable YAML [CODE READ `libs/utils/src/utils/id_patterns.py:25, 103, 120`: `detect_patterns`, `apply_pattern`, `suggest_regex`].
- **What it does not do:** composite keys, three or more files at once, the join.
- **Where it exists:** it is wired in Test Lab [CODE READ `app/handlers/test_lab_handlers.py:135, 147`], which is gated by `test_lab_enabled`, set in the developer and qa profiles only [RULE FILE `rules_test_lab.md` section 7; `rules_app_features_flags.md`]. The documentation may point to it, but must not promise it in every deployment.

**For the held documentation task (D-0583):** ids written differently by the programs of a pipeline are cleaned before the data enters the system (her example `program1-ID1`, `program2-ID1`); the log of the ids shows them, and Test Lab's ID Reconciliation can find the pattern (developer and qa profiles).

---

## THE CAUSE, AND WHAT WAS FOUND
END BLOCK 2
